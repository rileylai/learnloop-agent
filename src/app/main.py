from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request

from src.app.api import notion_index_router, qa_router
from src.app.config import get_settings
from src.observability.logger import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.log_level)
request_logger = get_logger("learnloop.request")

app = FastAPI(title="LearnLoop Agent")
app.include_router(notion_index_router)
app.include_router(qa_router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    workflow_id = request.headers.get("X-Workflow-ID") or str(uuid4())
    request.state.workflow_id = workflow_id
    start_time = perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        request_logger.exception(
            "request_failed",
            extra={
                "workflow_id": workflow_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
        raise

    duration_ms = round((perf_counter() - start_time) * 1000, 2)
    request_logger.info(
        "request_completed",
        extra={
            "workflow_id": workflow_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["X-Workflow-ID"] = workflow_id
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
