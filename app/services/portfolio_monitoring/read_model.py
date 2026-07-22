from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable, Mapping, Sequence

import pandas as pd

from .persistence import MonitoringItemRecord, MonitoringRepository, PortfolioGroupRecord
from .valuation import ItemValueLane, modified_dietz_return
from .diagnosis import DIAGNOSIS_POLICY_VERSION, DiagnosisFact, project_diagnoses
from .macro_context import MACRO_CONTEXT_VERSION, MacroContext, MacroObservation
from .market_chart import MarketChartLoader, build_selected_item_market_chart
from .schemas import build_request_fingerprint


WORKSPACE_SCHEMA_VERSION = "portfolio_monitoring_workspace_v2"
ACTIVE_ITEM_STATUSES = {"active", "data_review"}
MONITORING_VALUE_METHOD = {
    "basis": "oldest_latest_usable_date_among_active_lanes",
    "alignment": "as_of_step_without_interpolation",
    "pre_start": "planned_capital_as_cash",
    "post_end": "exit_value_as_cash",
    "cashflow_return": "daily_modified_dietz_weight_0_5",
}


def build_monitoring_config_fingerprint() -> str:
    """Identify the exact policy/macro/value contract used by the workspace."""

    return build_request_fingerprint({
        "workspace_schema": WORKSPACE_SCHEMA_VERSION,
        "diagnosis_policy": DIAGNOSIS_POLICY_VERSION,
        "macro_context": MACRO_CONTEXT_VERSION,
        "method": MONITORING_VALUE_METHOD,
    })


@dataclass(frozen=True)
class GroupMetrics:
    invested_capital: Decimal
    gross_contributions: Decimal
    gross_withdrawals: Decimal
    net_contributions: Decimal
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
        gross_contributions=invested_capital,
        gross_withdrawals=Decimal("0"),
        net_contributions=invested_capital,
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
    *,
    contribution_by_item: Mapping[str, Decimal] | None = None,
) -> GroupMetrics:
    """Calculate common-basis metrics from the daily group value curve."""

    capital = _money(invested_capital)
    if group_curve.empty or "date" not in group_curve or "total_value" not in group_curve:
        return _empty_metrics(capital)
    frame = group_curve.copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
    frame["total_value"] = pd.to_numeric(frame["total_value"], errors="coerce")
    for column in (
        "gross_contributions",
        "gross_withdrawals",
        "unit_value",
    ):
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["date", "total_value"])
    frame = frame.loc[frame["date"] <= pd.Timestamp(basis_date)].sort_values("date")
    frame = frame.drop_duplicates(subset=["date"], keep="last").reset_index(drop=True)
    if frame.empty:
        return _empty_metrics(capital)

    current_value = _money(frame.iloc[-1]["total_value"])
    gross_contributions = (
        _money(frame.iloc[-1]["gross_contributions"])
        if "gross_contributions" in frame
        and pd.notna(frame.iloc[-1]["gross_contributions"])
        else capital
    )
    gross_withdrawals = (
        _money(frame.iloc[-1]["gross_withdrawals"])
        if "gross_withdrawals" in frame
        and pd.notna(frame.iloc[-1]["gross_withdrawals"])
        else Decimal("0")
    )
    net_contributions = gross_contributions - gross_withdrawals
    pnl = current_value + gross_withdrawals - gross_contributions
    if "unit_value" in frame and frame["unit_value"].notna().all():
        performance_values = [_money(value) for value in frame["unit_value"]]
        total_return = performance_values[-1] - Decimal("1")
    else:
        performance_values = [_money(value) for value in frame["total_value"]]
        total_return = pnl / gross_contributions if gross_contributions > 0 else None
    running_peak = performance_values[0]
    drawdowns: list[Decimal] = []
    for value in performance_values:
        running_peak = max(running_peak, value)
        drawdowns.append(value / running_peak - Decimal("1"))
    mdd = min(drawdowns)
    start_date = frame.iloc[0]["date"].date()
    observation_days = max((basis_date - start_date).days, 0)
    start_value = performance_values[0]
    end_value = performance_values[-1]
    if observation_days > 0 and start_value > 0 and end_value > 0:
        cagr = (end_value / start_value) ** (
            Decimal("365") / Decimal(observation_days)
        ) - Decimal("1")
    else:
        cagr = None

    contributions = dict(contribution_by_item or {})
    if not contributions:
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
        invested_capital=gross_contributions,
        gross_contributions=gross_contributions,
        gross_withdrawals=gross_withdrawals,
        net_contributions=net_contributions,
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
    for column in (
        "external_flow",
        "cumulative_contributions",
        "cumulative_withdrawals",
        "flow_adjusted_index",
    ):
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["date", "total_value"])
    return frame.sort_values("date").drop_duplicates(subset=["date"], keep="last")


def _lane_total_return(
    lane: ItemValueLane | None,
    as_of_date: date,
) -> Decimal | None:
    """Return the cash-flow-adjusted item return observed on one exact date."""

    if lane is None:
        return None
    frame = _normalized_lane_curve(lane)
    if frame.empty or "flow_adjusted_index" not in frame:
        return None
    exact = frame.loc[frame["date"] == pd.Timestamp(as_of_date)]
    if exact.empty:
        return None
    value = exact.iloc[-1]["flow_adjusted_index"]
    if pd.isna(value):
        return None
    return _money(value) - Decimal("1")


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
    planned_capital = lane.initial_capital if lane is not None else item.initial_capital
    if lane is None or on_date < lane.effective_start_date:
        return planned_capital
    frame = _normalized_lane_curve(lane)
    eligible = frame.loc[frame["date"] <= pd.Timestamp(on_date)]
    if eligible.empty:
        return planned_capital
    return _money(eligible.iloc[-1]["total_value"])


def _cashflow_at(
    item: MonitoringItemRecord,
    lane: ItemValueLane | None,
    on_date: date,
) -> tuple[Decimal, Decimal, Decimal]:
    initial = lane.initial_capital if lane is not None else item.initial_capital
    if lane is None or on_date < lane.effective_start_date:
        return initial, Decimal("0"), Decimal("0")
    frame = _normalized_lane_curve(lane)
    eligible = frame.loc[frame["date"] <= pd.Timestamp(on_date)]
    if eligible.empty:
        return initial, Decimal("0"), Decimal("0")
    latest = eligible.iloc[-1]
    contributions = (
        _money(latest["cumulative_contributions"])
        if "cumulative_contributions" in eligible
        and pd.notna(latest["cumulative_contributions"])
        else initial
    )
    withdrawals = (
        _money(latest["cumulative_withdrawals"])
        if "cumulative_withdrawals" in eligible
        and pd.notna(latest["cumulative_withdrawals"])
        else Decimal("0")
    )
    exact = frame.loc[frame["date"] == pd.Timestamp(on_date)]
    external_flow = (
        _money(exact.iloc[-1]["external_flow"])
        if not exact.empty
        and "external_flow" in exact
        and pd.notna(exact.iloc[-1]["external_flow"])
        else Decimal("0")
    )
    return contributions, withdrawals, external_flow


def _requested_start(
    item: MonitoringItemRecord,
    lane: ItemValueLane | None,
) -> date:
    if (
        lane is not None
        and lane.position is not None
        and lane.position.requested_start_date is not None
    ):
        return lane.position.requested_start_date
    return item.requested_start_date


def _effective_start(
    item: MonitoringItemRecord,
    lane: ItemValueLane | None,
) -> date:
    return lane.effective_start_date if lane is not None else item.effective_start_date


def align_group_value_lanes(
    items: Sequence[MonitoringItemRecord],
    lanes: Mapping[str, ItemValueLane | BaseException],
) -> GroupValueResult:
    """Align item lanes on one conservative common basis without interpolation."""

    ordered_items = list(items)
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
    invested_capital = sum(
        (
            valid_lanes[item.monitoring_item_id].initial_capital
            if item.monitoring_item_id in valid_lanes
            else item.initial_capital
            for item in ordered_items
        ),
        Decimal("0"),
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
            max(
                (
                    _requested_start(
                        item,
                        valid_lanes.get(item.monitoring_item_id),
                    )
                    for item in ordered_items
                ),
                default=None,
            )
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

    start_date = min(
        _requested_start(item, valid_lanes.get(item.monitoring_item_id))
        for item in ordered_items
    )
    timeline = {start_date, basis_date}
    for item in ordered_items:
        lane = valid_lanes.get(item.monitoring_item_id)
        requested_start = _requested_start(item, lane)
        effective_start = _effective_start(item, lane)
        timeline.add(requested_start)
        if effective_start <= basis_date:
            timeline.add(effective_start)
        if item.tracking_end_effective_date and item.tracking_end_effective_date <= basis_date:
            timeline.add(item.tracking_end_effective_date)
        if lane is not None:
            frame = _normalized_lane_curve(lane)
            timeline.update(
                value.date()
                for value in frame["date"]
                if start_date <= value.date() <= basis_date
            )

    rows: list[dict[str, Any]] = []
    group_unit_value: Decimal | None = Decimal("1")
    previous_total = invested_capital
    for on_date in sorted(value for value in timeline if start_date <= value <= basis_date):
        row: dict[str, Any] = {"date": pd.Timestamp(on_date)}
        total = Decimal("0")
        gross_contributions = Decimal("0")
        gross_withdrawals = Decimal("0")
        external_flow = Decimal("0")
        for item in ordered_items:
            lane = valid_lanes.get(item.monitoring_item_id)
            value = _value_at(item, lane, on_date)
            contributions, withdrawals, item_flow = _cashflow_at(
                item,
                lane,
                on_date,
            )
            row[f"item:{item.monitoring_item_id}"] = float(value)
            total += value
            gross_contributions += contributions
            gross_withdrawals += withdrawals
            external_flow += item_flow
        row["total_value"] = float(total)
        row["external_flow"] = float(external_flow)
        row["gross_contributions"] = float(gross_contributions)
        row["gross_withdrawals"] = float(gross_withdrawals)
        daily_return = modified_dietz_return(
            previous_total,
            total,
            external_flow,
        )
        if daily_return is None or group_unit_value is None:
            group_unit_value = None
        else:
            group_unit_value *= Decimal("1") + daily_return
        row["daily_flow_adjusted_return"] = (
            float(daily_return) if daily_return is not None else None
        )
        row["unit_value"] = (
            float(group_unit_value) if group_unit_value is not None else None
        )
        rows.append(row)
        previous_total = total
    curve = pd.DataFrame(rows)
    contribution_by_item: dict[str, Decimal] = {}
    for item in ordered_items:
        lane = valid_lanes.get(item.monitoring_item_id)
        current = _value_at(item, lane, basis_date)
        contributions, withdrawals, _ = _cashflow_at(item, lane, basis_date)
        contribution_by_item[item.monitoring_item_id] = (
            current + withdrawals - contributions
        )
    metrics = calculate_group_metrics(
        curve,
        invested_capital,
        basis_date,
        contribution_by_item=contribution_by_item,
    )
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
            "initial_capital": (
                valid_lanes[item.monitoring_item_id].initial_capital
                if item.monitoring_item_id in valid_lanes
                else item.initial_capital
            ),
            "current_value": _value_at(
                item,
                valid_lanes.get(item.monitoring_item_id),
                basis_date,
            ),
            "total_return": _lane_total_return(
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
AnalysisBuilder = Callable[[Sequence[MonitoringItemRecord], Mapping[str, ItemValueLane | BaseException], GroupValueResult], Mapping[str, Any]]


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


def project_risk_calibration(
    artifact: Mapping[str, Any] | Any | None,
    *,
    current_policy_version: str,
    current_config_fingerprint: str,
) -> dict[str, Any]:
    """Expose probability only for a current, explicitly READY artifact."""

    raw = asdict(artifact) if is_dataclass(artifact) and not isinstance(artifact, type) else dict(artifact or {})
    status = str(raw.get("publication_status") or raw.get("status") or "SUPPRESSED").upper()
    reasons = [str(value) for value in raw.get("reasons") or [] if str(value)]
    if not raw:
        reasons.append("qualified calibration artifact is not available")
    fingerprint_mismatch = bool(raw) and (
        str(raw.get("policy_version") or "") != current_policy_version
        or str(raw.get("config_fingerprint") or "") != current_config_fingerprint
    )
    if fingerprint_mismatch:
        status = "SUPPRESSED"
        reasons.append("policy/config fingerprint does not match the current workspace")
    result: dict[str, Any] = {
        "publication_status": status if status in {"SUPPRESSED", "LIMITED", "READY"} else "SUPPRESSED",
        "reasons": list(dict.fromkeys(reasons)),
    }
    if result["publication_status"] != "READY" or raw.get("probability") is None:
        return result
    for key in (
        "probability", "horizon_sessions", "event_definition", "sample_size",
        "brier_score", "baseline_brier", "limitations",
    ):
        result[key] = raw.get(key)
    return result


def _compact_history_rows(rows: Sequence[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    fields = ("as_of_date", "observation_state", "severity", "confidence", "resolved_at", "outcome")
    return [
        {key: row.get(key) for key in fields}
        for row in rows or []
        if isinstance(row, Mapping)
    ]


def _project_selected_position(
    items: Sequence[MonitoringItemRecord],
    lanes: Mapping[str, ItemValueLane | BaseException],
    selected_item_id: str | None,
) -> dict[str, Any]:
    selected = next(
        (item for item in items if item.monitoring_item_id == selected_item_id),
        None,
    )
    empty = {
        "monitoring_item_id": selected_item_id,
        "eligible": False,
        "reason": "개별주식 종목을 선택해 주세요.",
        "as_of_date": None,
        "current_value": None,
        "requested_start_date": None,
        "effective_start_date": None,
        "entry_close": None,
        "initial_capital": None,
        "effective_initial_shares": None,
        "current_shares": None,
        "gross_contributions": Decimal("0"),
        "gross_withdrawals": Decimal("0"),
        "pnl": None,
        "total_return": None,
        "event_rows": [],
    }
    if selected is None:
        return empty
    if not (
        selected.source_type == "direct_security"
        and selected.instrument_kind == "stock"
        and selected.funding_mode == "fixed_shares"
    ):
        return {
            **empty,
            "monitoring_item_id": selected.monitoring_item_id,
            "reason": "개별주식의 보유 수량 방식에서만 거래를 기록할 수 있습니다.",
        }
    lane = lanes.get(selected.monitoring_item_id)
    if not isinstance(lane, ItemValueLane) or lane.position is None:
        return {
            **empty,
            "monitoring_item_id": selected.monitoring_item_id,
            "reason": "보유내역 가치곡선을 계산할 수 없습니다.",
        }
    command_eligible = selected.status in ACTIVE_ITEM_STATUSES
    frame = _normalized_lane_curve(lane)
    total_return = _lane_total_return(lane, lane.latest_usable_date)
    latest_value = None
    if "total_value" in frame and not frame.empty:
        value = frame.iloc[-1]["total_value"]
        if pd.notna(value):
            latest_value = _money(value)
    return {
        "monitoring_item_id": selected.monitoring_item_id,
        "eligible": command_eligible,
        "reason": (
            None
            if command_eligible
            else "추적 종료를 취소한 뒤 거래를 기록할 수 있습니다."
        ),
        "as_of_date": lane.latest_usable_date.isoformat(),
        "current_value": latest_value,
        "requested_start_date": (
            lane.position.requested_start_date or selected.requested_start_date
        ).isoformat(),
        "effective_start_date": (
            lane.position.effective_start_date or lane.effective_start_date
        ).isoformat(),
        "entry_close": lane.position.entry_close or selected.entry_close,
        "initial_capital": (
            lane.position.initial_capital or lane.initial_capital
        ),
        "effective_initial_shares": lane.position.effective_initial_shares,
        "current_shares": lane.position.current_shares,
        "gross_contributions": lane.position.cumulative_contributions,
        "gross_withdrawals": lane.position.cumulative_withdrawals,
        "pnl": lane.position.pnl,
        "total_return": total_return,
        "event_rows": list(lane.position.event_rows),
    }


def _project_item_details(
    items: Sequence[MonitoringItemRecord],
    lanes: Mapping[str, ItemValueLane | BaseException],
    *,
    basis_date: date | None,
    market_chart_loader: MarketChartLoader | None,
) -> dict[str, dict[str, Any]]:
    """Preload per-item detail so read-only selection stays in React."""

    return {
        item.monitoring_item_id: {
            "position": _project_selected_position(
                items,
                lanes,
                item.monitoring_item_id,
            ),
            "market_chart": (
                build_selected_item_market_chart(
                    items,
                    selected_item_id=item.monitoring_item_id,
                    basis_date=basis_date,
                    loader=market_chart_loader,
                )
                if market_chart_loader is not None
                else None
            ),
        }
        for item in items
    }


def _resolved_market_chart_item_id(
    items: Sequence[MonitoringItemRecord],
    selected_item_id: str | None,
) -> str | None:
    selected = next(
        (item for item in items if item.monitoring_item_id == selected_item_id),
        None,
    )
    if selected is None:
        selected = next(
            (item for item in items if item.status != "ended"),
            items[0] if items else None,
        )
    return selected.monitoring_item_id if selected is not None else None


def build_portfolio_monitoring_workspace(
    repository: MonitoringRepository,
    *,
    active_group_id: str | None = None,
    selected_item_id: str | None = None,
    catalog_query: str = "",
    generated_at: datetime | None = None,
    lane_loader: LaneLoader | None = None,
    market_chart_loader: MarketChartLoader | None = None,
    diagnosis_facts: Sequence[DiagnosisFact] | None = None,
    exposure_coverage: float = 0.0,
    macro_context: MacroContext | None = None,
    macro_observations: Sequence[MacroObservation] | None = None,
    analysis_builder: AnalysisBuilder | None = None,
    risk_calibration_artifact: Mapping[str, Any] | Any | None = None,
    diagnosis_history: Sequence[Mapping[str, Any]] | None = None,
    default_only: bool = False,
) -> dict[str, object]:
    """Build the versioned, read-only projection consumed by the React workbench."""

    groups = repository.list_groups(include_deleted=False)
    items_by_group = {
        group.portfolio_group_id: repository.list_items(group.portfolio_group_id)
        for group in groups
    }
    if default_only:
        selected_group = next((group for group in groups if group.is_default), None)
    else:
        selected_group = next(
            (group for group in groups if group.portfolio_group_id == active_group_id),
            None,
        )
        if selected_group is None:
            selected_group = next((group for group in groups if group.is_default), groups[0] if groups else None)
    active_result: GroupValueResult | None = None
    selected_items: list[MonitoringItemRecord] = []
    lane_values: dict[str, ItemValueLane | BaseException] = {}
    if selected_group is not None:
        selected_items = items_by_group[selected_group.portfolio_group_id]
        loader = lane_loader or getattr(repository, "load_value_lane", None)
        for item in selected_items:
            if callable(loader):
                try:
                    lane_values[item.monitoring_item_id] = loader(item)
                except Exception as exc:  # read projection must preserve partial state
                    lane_values[item.monitoring_item_id] = exc
            else:
                lane_values[item.monitoring_item_id] = RuntimeError("Value lane loader is not configured.")
        active_result = align_group_value_lanes(selected_items, lane_values)

        if analysis_builder is not None:
            try:
                analysis = dict(analysis_builder(selected_items, lane_values, active_result) or {})
                diagnosis_facts = list(analysis.get("diagnosis_facts") or diagnosis_facts or [])
                exposure_coverage = float(analysis.get("exposure_coverage", exposure_coverage))
                macro_context = analysis.get("macro_context") or macro_context
                macro_observations = list(analysis.get("macro_observations") or macro_observations or [])
            except Exception as exc:
                macro_context = macro_context or MacroContext(
                    status="LIMITED", as_of_dates={}, publication="LIMITED", cycle={}, family_scores={},
                    outlooks={}, pathways={}, coverage=0.0, warnings=(f"analysis projection failed: {exc}",),
                )

    timestamp = generated_at or datetime.now()
    diagnosis = project_diagnoses(list(diagnosis_facts or []), exposure_coverage)
    observation_rows = list(macro_observations or [])
    observation_rank = {"high": 3, "medium": 2, "low": 1}
    severity_rank = {"HIGH": 3, "MEDIUM": 2, "WATCH": 2, "LOW": 1, "INFO": 0}
    top_macro = sorted(
        (row for row in observation_rows if row.confidence != "LOW"),
        key=lambda row: (-severity_rank.get(row.severity, 0), -row.affected_weight, row.rule_id),
    )
    combined: dict[str, dict[str, Any]] = {}
    for row in diagnosis.top_three:
        combined[row.root_id] = asdict(row)
    for row in top_macro:
        projected = {
            **asdict(row),
            "classification": "macro_observation",
            "meaning": row.current_observation,
            "measured_fact": row.current_observation,
            "threshold": " + ".join(row.matched_conditions),
            "persistence": 1,
            "contribution": None,
            "policy_version": MACRO_CONTEXT_VERSION,
        }
        current = combined.get(row.root_id)
        if current is None or (
            severity_rank.get(row.severity, 0), row.affected_weight
        ) > (
            severity_rank.get(str(current.get("severity") or ""), 0),
            float(current.get("affected_weight") or 0),
        ):
            combined[row.root_id] = projected
    now_to_review = sorted(
        combined.values(),
        key=lambda row: (
            -severity_rank.get(str(row.get("severity") or ""), 0),
            -float(row.get("affected_weight") or 0),
            str(row.get("rule_id") or ""),
        ),
    )[:3]
    macro_state = max(
        (row.state for row in observation_rows),
        key=lambda value: observation_rank.get(value, 0),
        default="low",
    )
    source_health = (
        {
            "status": macro_context.status,
            "publication": macro_context.publication,
            "coverage": macro_context.coverage,
            "as_of_dates": dict(macro_context.as_of_dates),
            "warnings": list(macro_context.warnings),
        }
        if macro_context is not None
        else {
            "status": "LIMITED",
            "publication": "LIMITED",
            "coverage": 0.0,
            "as_of_dates": {},
            "warnings": ["macro context is not configured"],
        }
    )
    method = dict(MONITORING_VALUE_METHOD)
    config_fingerprint = build_monitoring_config_fingerprint()
    risk_calibration = project_risk_calibration(
        risk_calibration_artifact,
        current_policy_version=DIAGNOSIS_POLICY_VERSION,
        current_config_fingerprint=config_fingerprint,
    )
    item_details = _project_item_details(
        selected_items,
        lane_values,
        basis_date=active_result.basis_date if active_result is not None else None,
        market_chart_loader=market_chart_loader,
    )
    workspace: dict[str, object] = {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "generated_at": timestamp.isoformat(timespec="seconds"),
        "config_fingerprint": config_fingerprint,
        "groups": [
            _group_summary(
                group,
                items_by_group[group.portfolio_group_id],
                selected=(selected_group is not None and group.portfolio_group_id == selected_group.portfolio_group_id),
            )
            for group in groups
        ],
        "active_group": active_result,
        "selected_position": _project_selected_position(
            selected_items,
            lane_values,
            selected_item_id,
        ),
        "item_details": item_details,
        "catalog": {"query": catalog_query, "items": []},
        "commands": [],
        "diagnosis": {
            "policy_version": DIAGNOSIS_POLICY_VERSION,
            "top_three": [asdict(row) for row in diagnosis.top_three],
            "strengths": [asdict(row) for row in diagnosis.strengths],
            "weaknesses": [asdict(row) for row in diagnosis.weaknesses],
            "data_gaps": [asdict(row) for row in diagnosis.data_gaps],
            "all_rows": [asdict(row) for row in diagnosis.all_rows],
            "display_groups": [asdict(group) for group in diagnosis.display_groups],
            "coverage": exposure_coverage,
        },
        "macro_observation": {
            "version": MACRO_CONTEXT_VERSION,
            "state": macro_state,
            "rows": [asdict(row) for row in observation_rows],
            "top_rows": [asdict(row) for row in top_macro[:3]],
        },
        "now_to_review": now_to_review,
        "source_health": source_health,
        "risk_calibration": risk_calibration,
        "diagnosis_history": _compact_history_rows(diagnosis_history),
        "method": method,
        "boundaries": {
            "db_only": True,
            "provider_fetch": False,
            "live_orders": False,
            "auto_rebalance": False,
        },
    }
    if market_chart_loader is not None:
        resolved_item_id = _resolved_market_chart_item_id(
            selected_items,
            selected_item_id,
        )
        workspace["selected_item_market_chart"] = (
            item_details[resolved_item_id]["market_chart"]
            if resolved_item_id is not None
            else build_selected_item_market_chart(
                selected_items,
                selected_item_id=selected_item_id,
                basis_date=active_result.basis_date if active_result is not None else None,
                loader=market_chart_loader,
            )
        )
    return workspace
