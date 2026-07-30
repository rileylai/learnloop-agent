from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from src.app.telegram_runtime import build_telegram_gateway_orchestrator
from src.app.dependencies import (
    get_cost_tracker,
    get_embedding_client,
    get_prompt_template_loader,
    get_provider_router,
    get_tool_registry,
    get_trust_boundary,
)
from src.db.session import (
    get_db_session_factory,
    get_unit_of_work_factory,
)
from src.orchestrators import (
    TelegramDocumentAttachment,
    TelegramGatewayError,
    TelegramPhotoAttachment,
)

TELEGRAM_WEBHOOK_JOB_PATH = f"{__name__}.process_telegram_webhook_job"


def process_telegram_webhook_job(
    update_id: Optional[int],
    chat_id: Optional[str],
    text: Optional[str],
    caption: Optional[str],
    document: Optional[Dict[str, Any]],
    photos: List[Dict[str, Any]],
    request_workflow_id: str,
) -> Dict[str, Any]:
    """Run one claimed Telegram update inside an RQ worker process.

    Expected Telegram/domain failures are persisted by the gateway and returned
    as a completed job so RQ does not retry a user-visible failed update. RQ
    retries unexpected worker failures, such as a process crash before the
    ledger reaches a terminal state.
    """

    db_session_factory = get_db_session_factory()
    db_session = db_session_factory()
    try:
        gateway = build_telegram_gateway_orchestrator(
            db_session=db_session,
            db_session_factory=db_session_factory,
            unit_of_work_factory=get_unit_of_work_factory(),
            tool_registry=get_tool_registry(),
            provider_router=get_provider_router(),
            embedding_client=get_embedding_client(),
            cost_tracker=get_cost_tracker(),
            prompt_template_loader=get_prompt_template_loader(),
            trust_boundary=get_trust_boundary(),
        )
        result = asyncio.run(
            gateway.handle_claimed_webhook(
                update_id=update_id,
                chat_id=chat_id,
                text=text,
                caption=caption,
                document=(
                    TelegramDocumentAttachment(**document)
                    if document is not None
                    else None
                ),
                photos=[TelegramPhotoAttachment(**photo) for photo in photos],
                request_workflow_id=request_workflow_id,
            )
        )
        return asdict(result)
    except TelegramGatewayError as exc:
        return {
            "status": "failed",
            "error_code": exc.error_code,
            "failure_reason": exc.failure_reason,
            "workflow_run_id": exc.workflow_run_id,
        }
    finally:
        db_session.close()
