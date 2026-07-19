from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable, Mapping, Sequence

import pandas as pd

from .persistence import MonitoringItemRecord, MonitoringRepository, PortfolioGroupRecord
from .valuation import ItemValueLane
from .diagnosis import DIAGNOSIS_POLICY_VERSION, DiagnosisFact, project_diagnoses


WORKSPACE_SCHEMA_VERSION = "portfolio_monitoring_workspace_v1"
ACTIVE_ITEM_STATUSES = {"active", "data_review"}


@dataclass(frozen=True)
class GroupMetrics:
    invested_capital: Decimal
    current_value: Decimal
    pnl: Decimal
    total_return: Decimal | None
    mdd: Decimal | None
    cagr: Decimal | None
    observation_days: int
    short_window: bool
    total_contribution: Decimal
    downside_contribution: Decimal
    contribution_by_item: dict[str, Decimal]


@dataclass(frozen=True)
class GroupValueResult:
    status: str
    basis_date: date | None
    curve: pd.DataFrame
    metrics: GroupMetrics
    failures: dict[str, str]
    item_rows: tuple[dict[str, Any], ...]
    active_item_count: int
    history_item_count: int


def _money(value: Any) -> Decimal:
    return Decimal(str(value))


def _empty_metrics(invested_capital: Decimal = Decimal("0")) -> GroupMetrics:
    return GroupMetrics(
        invested_capital=invested_capital,
        current_value=invested_capital,
        pnl=Decimal("0"),
        total_return=Decimal("0") if invested_capital > 0 else None,
        mdd=Decimal("0") if invested_capital > 0 else None,
        cagr=None,
        observation_days=0,
        short_window=True,
        total_contribution=Decimal("0"),
        downside_contribution=Decimal("0"),
        contribution_by_item={},
    )


def calculate_group_metrics(
    group_curve: pd.DataFrame,
    invested_capital: Decimal,
    basis_date: date,
) -> GroupMetrics:
    """Calculate common-basis metrics from the daily group value curve."""

    capital = _money(invested_capital)
    if group_curve.empty or "date" not in group_curve or "total_value" not in group_curve:
        return _empty_metrics(capital)
    frame = group_curve.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
    frame["total_value"] = pd.to_numeric(frame["total_value"], errors="coerce")
    frame = frame.dropna(subset=["date", "total_value"])
    frame = frame.loc[frame["date"] <= pd.Timestamp(basis_date)].sort_values("date")
    frame = frame.drop_duplicates(subset=["date"], keep="last").reset_index(drop=True)
    if frame.empty:
        return _empty_metrics(capital)

    current_value = _money(frame.iloc[-1]["total_value"])
    pnl = current_value - capital
    total_return = pnl / capital if capital > 0 else None
    value_decimals = [_money(value) for value in frame["total_value"]]
    running_peak = value_decimals[0]
    drawdowns: list[Decimal] = []
    for value in value_decimals:
        running_peak = max(running_peak, value)
        drawdowns.append(value / running_peak - Decimal("1"))
    mdd = min(drawdowns)
    start_date = frame.iloc[0]["date"].date()
    observation_days = max((basis_date - start_date).days, 0)
    start_value = _money(frame.iloc[0]["total_value"])
    if observation_days > 0 and start_value > 0 and current_value > 0:
        cagr = (current_value / start_value) ** (Decimal("365") / Decimal(observation_days)) - Decimal("1")
    else:
        cagr = None

    contributions: dict[str, Decimal] = {}
    for column in frame.columns:
        if not str(column).startswith("item:"):
            continue
        item_id = str(column).split(":", 1)[1]
        start = _money(frame.iloc[0][column])
        current = _money(frame.iloc[-1][column])
        contributions[item_id] = current - start
    total_contribution = sum(contributions.values(), Decimal("0"))
    downside_contribution = sum(
        (value for value in contributions.values() if value < 0),
        Decimal("0"),
    )
    return GroupMetrics(
        invested_capital=capital,
        current_value=current_value,
        pnl=pnl,
        total_return=total_return,
        mdd=mdd,
        cagr=cagr,
        observation_days=observation_days,
        short_window=observation_days < 365,
        total_contribution=total_contribution,
        downside_contribution=downside_contribution,
        contribution_by_item=contributions,
    )


def _normalized_lane_curve(lane: ItemValueLane) -> pd.DataFrame:
    frame = lane.curve.copy()
    if "date" not in frame or "total_value" not in frame:
        return pd.DataFrame(columns=["date", "total_value"])
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
    frame["total_value"] = pd.to_numeric(frame["total_value"], errors="coerce")
    frame = frame.dropna(subset=["date", "total_value"])
    return frame.sort_values("date").drop_duplicates(subset=["date"], keep="last")


def _value_at(
    item: MonitoringItemRecord,
    lane: ItemValueLane | None,
    on_date: date,
) -> Decimal:
    if (
        item.status == "ended"
        and item.tracking_end_effective_date is not None
        and on_date >= item.tracking_end_effective_date
        and item.exit_value is not None
    ):
        return item.exit_value
    if lane is None or on_date < lane.effective_start_date:
        return item.initial_capital
    frame = _normalized_lane_curve(lane)
    eligible = frame.loc[frame["date"] <= pd.Timestamp(on_date)]
    if eligible.empty:
        return item.initial_capital
    return _money(eligible.iloc[-1]["total_value"])


def align_group_value_lanes(
    items: Sequence[MonitoringItemRecord],
    lanes: Mapping[str, ItemValueLane | BaseException],
) -> GroupValueResult:
    """Align item lanes on one conservative common basis without interpolation."""

    ordered_items = list(items)
    invested_capital = sum((item.initial_capital for item in ordered_items), Decimal("0"))
    failures: dict[str, str] = {}
    valid_lanes: dict[str, ItemValueLane] = {}
    for item in ordered_items:
        value = lanes.get(item.monitoring_item_id)
        if isinstance(value, ItemValueLane):
            valid_lanes[item.monitoring_item_id] = value
        else:
            failures[item.monitoring_item_id] = (
                str(value) if isinstance(value, BaseException) else "Value lane is unavailable."
            )

    active_items = [item for item in ordered_items if item.status in ACTIVE_ITEM_STATUSES]
    active_lane_dates = [
        valid_lanes[item.monitoring_item_id].latest_usable_date
        for item in active_items
        if item.monitoring_item_id in valid_lanes
    ]
    if active_lane_dates:
        basis_date = min(active_lane_dates)
    else:
        fallback_dates = [lane.latest_usable_date for lane in valid_lanes.values()]
        fallback_dates.extend(
            item.tracking_end_effective_date
            for item in ordered_items
            if item.tracking_end_effective_date is not None
        )
        basis_date = max(fallback_dates) if fallback_dates else (
            max((item.requested_start_date for item in ordered_items), default=None)
        )

    if basis_date is None or not ordered_items:
        return GroupValueResult(
            status="PARTIAL" if failures else "EMPTY",
            basis_date=basis_date,
            curve=pd.DataFrame(columns=["date", "total_value"]),
            metrics=_empty_metrics(invested_capital),
            failures=failures,
            item_rows=tuple(),
            active_item_count=len(active_items),
            history_item_count=len(ordered_items),
        )

    start_date = min(item.requested_start_date for item in ordered_items)
    timeline = {start_date, basis_date}
    for item in ordered_items:
        timeline.add(item.requested_start_date)
        if item.effective_start_date <= basis_date:
            timeline.add(item.effective_start_date)
        if item.tracking_end_effective_date and item.tracking_end_effective_date <= basis_date:
            timeline.add(item.tracking_end_effective_date)
        lane = valid_lanes.get(item.monitoring_item_id)
        if lane is not None:
            frame = _normalized_lane_curve(lane)
            timeline.update(
                value.date()
                for value in frame["date"]
                if start_date <= value.date() <= basis_date
            )

    rows: list[dict[str, Any]] = []
    for on_date in sorted(value for value in timeline if start_date <= value <= basis_date):
        row: dict[str, Any] = {"date": pd.Timestamp(on_date)}
        total = Decimal("0")
        for item in ordered_items:
            value = _value_at(item, valid_lanes.get(item.monitoring_item_id), on_date)
            row[f"item:{item.monitoring_item_id}"] = float(value)
            total += value
        row["total_value"] = float(total)
        rows.append(row)
    curve = pd.DataFrame(rows)
    metrics = calculate_group_metrics(curve, invested_capital, basis_date)
    item_rows = tuple(
        {
            "monitoring_item_id": item.monitoring_item_id,
            "source_ref": item.source_ref,
            "status": item.status,
            "lane_status": (
                valid_lanes[item.monitoring_item_id].status
                if item.monitoring_item_id in valid_lanes
                else "failed"
            ),
            "initial_capital": item.initial_capital,
            "current_value": _value_at(
                item,
                valid_lanes.get(item.monitoring_item_id),
                basis_date,
            ),
            "failure": failures.get(item.monitoring_item_id),
        }
        for item in ordered_items
    )
    return GroupValueResult(
        status="PARTIAL" if failures else "READY",
        basis_date=basis_date,
        curve=curve,
        metrics=metrics,
        failures=failures,
        item_rows=item_rows,
        active_item_count=len(active_items),
        history_item_count=len(ordered_items),
    )


LaneLoader = Callable[[MonitoringItemRecord], ItemValueLane | BaseException]


def _group_summary(
    group: PortfolioGroupRecord,
    items: Sequence[MonitoringItemRecord],
    *,
    selected: bool,
) -> dict[str, Any]:
    return {
        "portfolio_group_id": group.portfolio_group_id,
        "name": group.name,
        "is_default": group.is_default,
        "selected": selected,
        "status": group.status,
        "version": group.version,
        "active_item_count": sum(item.status in ACTIVE_ITEM_STATUSES for item in items),
        "history_item_count": len(items),
    }


def build_portfolio_monitoring_workspace(
    repository: MonitoringRepository,
    *,
    active_group_id: str | None = None,
    catalog_query: str = "",
    generated_at: datetime | None = None,
    lane_loader: LaneLoader | None = None,
    diagnosis_facts: Sequence[DiagnosisFact] | None = None,
    exposure_coverage: float = 0.0,
) -> dict[str, object]:
    """Build the versioned, read-only projection consumed by the React workbench."""

    groups = repository.list_groups(include_deleted=False)
    items_by_group = {
        group.portfolio_group_id: repository.list_items(group.portfolio_group_id)
        for group in groups
    }
    selected_group = next(
        (group for group in groups if group.portfolio_group_id == active_group_id),
        None,
    )
    if selected_group is None:
        selected_group = next((group for group in groups if group.is_default), groups[0] if groups else None)
    active_result: GroupValueResult | None = None
    if selected_group is not None:
        selected_items = items_by_group[selected_group.portfolio_group_id]
        loader = lane_loader or getattr(repository, "load_value_lane", None)
        lane_values: dict[str, ItemValueLane | BaseException] = {}
        for item in selected_items:
            if callable(loader):
                try:
                    lane_values[item.monitoring_item_id] = loader(item)
                except Exception as exc:  # read projection must preserve partial state
                    lane_values[item.monitoring_item_id] = exc
            else:
                lane_values[item.monitoring_item_id] = RuntimeError("Value lane loader is not configured.")
        active_result = align_group_value_lanes(selected_items, lane_values)

    timestamp = generated_at or datetime.now()
    diagnosis = project_diagnoses(list(diagnosis_facts or []), exposure_coverage)
    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "generated_at": timestamp.isoformat(timespec="seconds"),
        "groups": [
            _group_summary(
                group,
                items_by_group[group.portfolio_group_id],
                selected=(selected_group is not None and group.portfolio_group_id == selected_group.portfolio_group_id),
            )
            for group in groups
        ],
        "active_group": active_result,
        "catalog": {"query": catalog_query, "items": []},
        "commands": [],
        "diagnosis": {
            "policy_version": DIAGNOSIS_POLICY_VERSION,
            "top_three": [asdict(row) for row in diagnosis.top_three],
            "strengths": [asdict(row) for row in diagnosis.strengths],
            "weaknesses": [asdict(row) for row in diagnosis.weaknesses],
            "data_gaps": [asdict(row) for row in diagnosis.data_gaps],
            "all_rows": [asdict(row) for row in diagnosis.all_rows],
            "coverage": exposure_coverage,
        },
        "method": {
            "basis": "oldest_latest_usable_date_among_active_lanes",
            "alignment": "as_of_step_without_interpolation",
            "pre_start": "planned_capital_as_cash",
            "post_end": "exit_value_as_cash",
        },
        "boundaries": {
            "db_only": True,
            "provider_fetch": False,
            "live_orders": False,
            "auto_rebalance": False,
        },
    }
