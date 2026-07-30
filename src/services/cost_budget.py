from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable, Optional, Tuple

from src.db.models import WorkflowRun


COST_FIELDS = ("estimated_cost", "embedding_estimated_cost")


@dataclass(frozen=True)
class CostBudgetDecision:
    status: str
    allowed: bool
    estimated_cost_usd: Optional[float]
    budget_usd: Optional[float]


@dataclass(frozen=True)
class CostBudgetSnapshot:
    daily_cost_usd: float
    daily_budget_usd: Optional[float]
    daily_status: str
    unknown_cost_workflow_count: int
    workflow_budget_exceeded_count: int
    workflow_budget_usd: Optional[float]


class CostBudgetService:
    """Aggregate recorded workflow costs and evaluate operator thresholds."""

    def __init__(
        self,
        *,
        daily_budget_usd: Optional[float] = None,
        workflow_budget_usd: Optional[float] = None,
    ) -> None:
        self._daily_budget = _normalize_budget(daily_budget_usd)
        self._workflow_budget = _normalize_budget(workflow_budget_usd)

    @property
    def daily_budget_usd(self) -> Optional[float]:
        return _as_float(self._daily_budget)

    @property
    def workflow_budget_usd(self) -> Optional[float]:
        return _as_float(self._workflow_budget)

    def evaluate_workflow_cost(
        self,
        estimated_cost_usd: Optional[float],
    ) -> CostBudgetDecision:
        normalized_cost = _normalize_cost(estimated_cost_usd)
        if normalized_cost is None:
            return CostBudgetDecision(
                status="unknown",
                allowed=True,
                estimated_cost_usd=None,
                budget_usd=self.workflow_budget_usd,
            )
        if self._workflow_budget is None:
            return CostBudgetDecision(
                status="unconfigured",
                allowed=True,
                estimated_cost_usd=_as_float(normalized_cost),
                budget_usd=None,
            )
        if normalized_cost > self._workflow_budget:
            return CostBudgetDecision(
                status="exceeded",
                allowed=False,
                estimated_cost_usd=_as_float(normalized_cost),
                budget_usd=_as_float(self._workflow_budget),
            )
        return CostBudgetDecision(
            status="ok",
            allowed=True,
            estimated_cost_usd=_as_float(normalized_cost),
            budget_usd=_as_float(self._workflow_budget),
        )

    def summarize(
        self,
        workflow_runs: Iterable[WorkflowRun],
        *,
        now: Optional[datetime] = None,
    ) -> CostBudgetSnapshot:
        current_time = _as_utc(now or datetime.now(timezone.utc))
        day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_total = Decimal("0")
        unknown_cost_workflow_count = 0
        workflow_budget_exceeded_count = 0

        for workflow_run in workflow_runs:
            cost, unknown = extract_workflow_cost(workflow_run)
            if cost is None and unknown and _as_utc(workflow_run.started_at) >= day_start:
                unknown_cost_workflow_count += 1
            if cost is not None:
                if _as_utc(workflow_run.started_at) >= day_start:
                    daily_total += cost
                if self._workflow_budget is not None and cost > self._workflow_budget:
                    workflow_budget_exceeded_count += 1

        if self._daily_budget is None:
            daily_status = "unconfigured"
        elif daily_total > self._daily_budget:
            daily_status = "exceeded"
        elif unknown_cost_workflow_count > 0:
            daily_status = "unknown"
        else:
            daily_status = "ok"

        return CostBudgetSnapshot(
            daily_cost_usd=_as_float(daily_total) or 0.0,
            daily_budget_usd=self.daily_budget_usd,
            daily_status=daily_status,
            unknown_cost_workflow_count=unknown_cost_workflow_count,
            workflow_budget_exceeded_count=workflow_budget_exceeded_count,
            workflow_budget_usd=self.workflow_budget_usd,
        )


def extract_workflow_cost(workflow_run: WorkflowRun) -> Tuple[Optional[Decimal], bool]:
    """Return recorded cost and whether a cost-bearing workflow is unknown."""
    if not workflow_run.metadata_json:
        return None, False
    try:
        metadata = json.loads(workflow_run.metadata_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None, False
    if not isinstance(metadata, dict):
        return None, False

    costs = []
    unknown = False
    for field_name in COST_FIELDS:
        if field_name not in metadata:
            continue
        value = metadata[field_name]
        if value is None:
            unknown = True
            continue
        normalized = _normalize_cost(value)
        if normalized is None:
            unknown = True
        else:
            costs.append(normalized)

    if costs:
        return sum(costs, Decimal("0")), False
    return None, unknown


def _normalize_budget(value: Optional[float]) -> Optional[Decimal]:
    if value is None:
        return None
    normalized = _normalize_cost(value)
    if normalized is None or normalized <= 0:
        raise ValueError("cost budget must be a positive finite number")
    return normalized


def _normalize_cost(value: object) -> Optional[Decimal]:
    if isinstance(value, bool) or value is None:
        return None
    try:
        candidate = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not candidate.is_finite() or candidate < 0:
        return None
    return candidate


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _as_float(value: Optional[Decimal]) -> Optional[float]:
    if value is None:
        return None
    result = float(value)
    return result if math.isfinite(result) else None
