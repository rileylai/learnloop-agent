from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.app.dependencies import get_readiness_service
from src.app.schemas.ops import ReadinessCheck, ReadinessResponse
from src.services import ReadinessReport, ReadinessService


router = APIRouter()


def _build_response(report: ReadinessReport) -> ReadinessResponse:
    return ReadinessResponse(
        status="ready" if report.is_ready else "not_ready",
        mode=report.mode,
        checks={
            name: ReadinessCheck(
                status=check.status,
                detail=check.detail,
                failure_reason=check.failure_reason,
            )
            for name, check in report.checks.items()
        },
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness(
    readiness_service: ReadinessService = Depends(get_readiness_service),
) -> ReadinessResponse:
    response = _build_response(readiness_service.check())
    if response.status != "ready":
        payload = (
            response.model_dump()
            if hasattr(response, "model_dump")
            else response.dict()
        )
        return JSONResponse(status_code=503, content=payload)
    return response
