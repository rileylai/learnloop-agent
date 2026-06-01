from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.app.dependencies import get_tool_registry
from src.app.schemas import TelegramWebhookRequest, TelegramWebhookResponse
from src.db.session import get_db_session
from src.orchestrators import TelegramGatewayError, TelegramGatewayOrchestrator
from src.repositories import WorkflowRunRepository
from src.services import WorkflowRunService
from src.tools import ToolRegistry

router = APIRouter()


def _build_telegram_gateway_orchestrator(
    *,
    db_session: Session,
    tool_registry: ToolRegistry,
) -> TelegramGatewayOrchestrator:
    return TelegramGatewayOrchestrator(
        tool_registry=tool_registry,
        workflow_run_service=WorkflowRunService(WorkflowRunRepository(db_session)),
    )


@router.post("/api/telegram/webhook", response_model=TelegramWebhookResponse)
async def handle_telegram_webhook(
    payload: TelegramWebhookRequest,
    request: Request,
    db_session: Session = Depends(get_db_session),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> TelegramWebhookResponse:
    orchestrator = _build_telegram_gateway_orchestrator(
        db_session=db_session,
        tool_registry=tool_registry,
    )
    request_workflow_id = str(getattr(request.state, "workflow_id", ""))
    message = payload.message
    chat_id = str(message.chat.id) if message is not None else None
    text = message.text if message is not None else None

    try:
        result = await orchestrator.handle_webhook(
            update_id=payload.update_id,
            chat_id=chat_id,
            text=text,
            request_workflow_id=request_workflow_id,
        )
    except TelegramGatewayError as exc:
        raise HTTPException(
            status_code=exc.http_status_code,
            detail={
                "error_code": exc.error_code,
                "message": exc.message,
                "failure_reason": exc.failure_reason,
                "workflow_run_id": exc.workflow_run_id,
            },
        ) from exc

    return TelegramWebhookResponse(
        workflow_run_id=result.workflow_run_id,
        status=result.status,
        handled=result.handled,
        command=result.command,
        reply_text=result.reply_text,
        telegram_message_id=result.telegram_message_id,
        skipped_reason=result.skipped_reason,
    )
