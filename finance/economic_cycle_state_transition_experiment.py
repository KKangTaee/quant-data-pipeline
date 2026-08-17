"""Read-only feasibility orchestration for economic-cycle state transitions."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass, replace
from datetime import date
from typing import Any

import pandas as pd

from finance.economic_cycle_confirmed_state import (
    build_confirmed_observed_history,
    build_confirmed_state_frame,
)
from finance.economic_cycle_core_state import (
    CoreStateAuditReport,
    build_core_feature_panel,
    evaluate_core_state_gate,
)
from finance.economic_cycle_observed_state import ObservedStateResult
from finance.economic_cycle_realtime_history import (
    build_rtdsm_monthly_panel,
    build_rtdsm_observed_history,
)
from finance.economic_cycle_transition_comparison import (
    PairedSkillReport,
    TransitionTaskDecision,
    compare_common_origin_skill,
    evaluate_task_gates,
)
from finance.economic_cycle_transition_dataset import (
    TransitionDataset,
    build_transition_dataset,
)
from finance.economic_cycle_transition_drivers import (
    MARKET_DRIVER_FEATURES,
    REQUIRED_DRIVER_FEATURES,
    REQUIRED_DRIVER_SERIES,
    DriverCoverageReport,
    audit_transition_driver_coverage,
    build_transition_driver_panel,
    extend_transition_dataset,
)
from finance.economic_cycle_transition_feasibility import (
    TransitionFeasibilityReport,
    evaluate_confirmed_transition_sample_feasibility,
)
from finance.economic_cycle_transition_validation import (
    TransitionValidationReport,
    run_transition_validation,
)
from finance.loaders.economic_cycle import load_economic_cycle_vintages
from finance.loaders.economic_cycle_assets import (
    load_economic_cycle_asset_prices,
    load_economic_cycle_market_series,
)
from finance.loaders.economic_cycle_realtime import load_rtdsm_signal_history
from finance.loaders.inflation_policy import load_inflation_policy_training_vintages


RTDSM_SERIES = ("IPT", "H", "EMPLOY", "RUC")
RTDSM_HISTORY_START = pd.Timestamp("1971-09-30")


@dataclass(frozen=True)
class StateStageResult:
    """Audited canonical state and the exact inputs for downstream labels."""

    source_counts: dict[str, object]
    core_panel: pd.DataFrame
    raw_history: tuple[ObservedStateResult, ...]
    confirmed_state_frame: pd.DataFrame
    sample_report: TransitionFeasibilityReport
    state_report: CoreStateAuditReport


@dataclass(frozen=True)
class DriverStageResult:
    """Core, required-extended and optional-market model datasets."""

    core_dataset: TransitionDataset
    extended_dataset: TransitionDataset
    shadow_dataset: TransitionDataset | None
    driver_report: DriverCoverageReport
    shadow_report: DriverCoverageReport | None
    source_counts: dict[str, object]


@dataclass(frozen=True)
class StateTransitionFeasibilityReport:
    """Side-effect-free evidence and the final 1~3 phase decision."""

    status: str
    reason_codes: tuple[str, ...]
    as_of_date: str
    source_counts: dict[str, object]
    sample_report: TransitionFeasibilityReport
    state_report: CoreStateAuditReport
    driver_report: DriverCoverageReport | None
    shadow_driver_report: DriverCoverageReport | None
    fiscal_status: str
    core_validation: TransitionValidationReport | None
    extended_validation: TransitionValidationReport | None
    shadow_validation: TransitionValidationReport | None
    core_decision: TransitionTaskDecision | None
    extended_decision: TransitionTaskDecision | None
    paired_skill: PairedSkillReport | None

    def to_dict(self) -> dict[str, object]:
        """Return finite JSON-safe evidence without altering the audit decision."""

        return _json_safe(asdict(self))


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _normalized_cutoff(as_of_date: str | date) -> pd.Timestamp:
    cutoff = pd.Timestamp(as_of_date)
    if cutoff.tzinfo is not None:
        cutoff = cutoff.tz_convert(None)
    cutoff = cutoff.normalize()
    if cutoff < RTDSM_HISTORY_START:
        raise ValueError("as_of_date must be on or after the RTDSM history start")
    return cutoff


def _load_nber_months(cutoff: pd.Timestamp) -> dict[str, bool]:
    rows = load_economic_cycle_vintages(
        ("USREC",),
        start_date=RTDSM_HISTORY_START.date().isoformat(),
        end_date=cutoff.date().isoformat(),
        as_of_date=cutoff.date().isoformat(),
    )
    result: dict[str, bool] = {}
    for row in rows:
        observation = pd.to_datetime(row.get("observation_date"), errors="coerce")
        value = pd.to_numeric(row.get("value"), errors="coerce")
        if pd.isna(observation) or pd.isna(value):
            continue
        month = pd.Timestamp(observation).to_period("M").to_timestamp("M")
        result[month.date().isoformat()] = float(value) >= 0.5
    return result


def _build_state_stage(cutoff: pd.Timestamp) -> StateStageResult:
    origins = list(pd.date_range(RTDSM_HISTORY_START, cutoff, freq="ME"))
    start_text = RTDSM_HISTORY_START.date().isoformat()
    cutoff_text = cutoff.date().isoformat()
    vintage_rows = list(
        load_rtdsm_signal_history(
            RTDSM_SERIES,
            start_date=start_text,
            end_date=cutoff_text,
            as_of_date=cutoff_text,
        )
    )
    nber_months = _load_nber_months(cutoff)
    counts = Counter(str(row.get("series_id") or "").upper() for row in vintage_rows)
    source_counts: dict[str, object] = {
        **{series_id: int(counts.get(series_id, 0)) for series_id in RTDSM_SERIES},
        "rtdsm_rows": len(vintage_rows),
        "USREC": len(nber_months),
        "forecast_origins": len(origins),
    }

    realtime_panel = build_rtdsm_monthly_panel(
        vintage_rows,
        forecast_origins=origins,
        vintage_lag_months=0,
    )
    revised_panel = build_rtdsm_monthly_panel(
        vintage_rows,
        forecast_origins=origins,
        vintage_lag_months=3,
    )
    raw_history = tuple(build_rtdsm_observed_history(realtime_panel))
    revised_raw_history = tuple(build_rtdsm_observed_history(revised_panel))
    state_frame = build_confirmed_state_frame(raw_history)
    revised_state_frame = build_confirmed_state_frame(revised_raw_history)
    confirmed_history = build_confirmed_observed_history(state_frame)
    revised_history = build_confirmed_observed_history(revised_state_frame)
    sample_report = evaluate_confirmed_transition_sample_feasibility(state_frame)
    core_panel = build_core_feature_panel(realtime_panel)
    state_report = evaluate_core_state_gate(
        core_panel,
        confirmed_history,
        revised_history,
        nber_months=nber_months,
        sample_report=sample_report,
    )
    missing_sources = [
        series_id for series_id in RTDSM_SERIES if not source_counts[series_id]
    ]
    if missing_sources:
        state_report = replace(
            state_report,
            status="NO_GO_CORE_STATE",
            reason_codes=tuple(
                dict.fromkeys(("INCOMPLETE_RTDSM_SOURCE", *state_report.reason_codes))
            ),
        )
    return StateStageResult(
        source_counts=source_counts,
        core_panel=core_panel,
        raw_history=raw_history,
        confirmed_state_frame=state_frame,
        sample_report=sample_report,
        state_report=state_report,
    )


def _build_driver_stage(
    cutoff: pd.Timestamp,
    state: StateStageResult,
) -> DriverStageResult:
    core_dataset = build_transition_dataset(
        state.core_panel,
        state.raw_history,
        confirmed_state_frame=state.confirmed_state_frame,
    )
    cutoff_text = cutoff.date().isoformat()
    as_of_at = f"{cutoff_text}T23:59:59.999999+00:00"
    vintage_rows = list(
        load_inflation_policy_training_vintages(
            as_of_at=as_of_at,
            history_start=RTDSM_HISTORY_START.date().isoformat(),
            series_ids=REQUIRED_DRIVER_SERIES,
        )
    )

    market_rows: list[dict[str, object]] = []
    market_error: str | None = None
    try:
        market_rows.extend(
            load_economic_cycle_market_series(
                series_ids=("VIXCLS",),
                start_date=RTDSM_HISTORY_START.date().isoformat(),
                end_date=cutoff_text,
            )
        )
        market_rows.extend(
            load_economic_cycle_asset_prices(
                symbols=("GC=F", "DX-Y.NYB"),
                equity_symbols=("^GSPC", "SPY"),
                lookback_rows=2000,
                end_date=cutoff_text,
            )
        )
    except Exception as exc:  # Optional shadow data must not block required audit.
        market_error = type(exc).__name__
        market_rows = []

    origins = state.core_panel.get("forecast_origin", pd.Series(dtype=object)).tolist()
    feature_panel = build_transition_driver_panel(
        vintage_rows,
        origins,
        market_rows=market_rows,
    )
    extended_dataset = extend_transition_dataset(
        core_dataset,
        feature_panel,
        REQUIRED_DRIVER_FEATURES,
    )
    driver_report = audit_transition_driver_coverage(
        extended_dataset,
        state.confirmed_state_frame,
        REQUIRED_DRIVER_FEATURES,
    )

    shadow_dataset: TransitionDataset | None = None
    shadow_report: DriverCoverageReport | None = None
    if market_rows:
        shadow_dataset = extend_transition_dataset(
            extended_dataset,
            feature_panel,
            MARKET_DRIVER_FEATURES,
        )
        shadow_report = audit_transition_driver_coverage(
            shadow_dataset,
            state.confirmed_state_frame,
            MARKET_DRIVER_FEATURES,
        )

    driver_counts = Counter(
        str(row.get("series_id") or "").upper() for row in vintage_rows
    )
    market_counts = Counter(
        str(row.get("provider_symbol") or row.get("series_id") or "").upper()
        for row in market_rows
    )
    source_counts: dict[str, object] = {
        **{
            f"driver_{series_id}": int(driver_counts.get(series_id, 0))
            for series_id in REQUIRED_DRIVER_SERIES
        },
        "driver_rows": len(vintage_rows),
        "market_rows": len(market_rows),
        **{
            f"market_{symbol}": int(market_counts.get(symbol, 0))
            for symbol in ("^GSPC", "SPY", "VIXCLS", "GC=F", "DX-Y.NYB")
        },
    }
    if market_error:
        source_counts["market_loader_error"] = market_error
    return DriverStageResult(
        core_dataset=core_dataset,
        extended_dataset=extended_dataset,
        shadow_dataset=shadow_dataset,
        driver_report=driver_report,
        shadow_report=shadow_report,
        source_counts=source_counts,
    )


def _reason_union(*groups: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def run_state_transition_feasibility(
    as_of_date: str | date,
    *,
    state_builder: Callable[[pd.Timestamp], StateStageResult] = _build_state_stage,
    driver_builder: Callable[[pd.Timestamp, StateStageResult], DriverStageResult] = _build_driver_stage,
    validation_runner: Callable[[TransitionDataset], TransitionValidationReport] = run_transition_validation,
    task_evaluator: Callable[[TransitionValidationReport], TransitionTaskDecision] = evaluate_task_gates,
    skill_comparator: Callable[[TransitionValidationReport, TransitionValidationReport], PairedSkillReport] = compare_common_origin_skill,
) -> StateTransitionFeasibilityReport:
    """Evaluate state, driver coverage and forecast skill without any writer."""

    cutoff = _normalized_cutoff(as_of_date)
    cutoff_text = cutoff.date().isoformat()
    state = state_builder(cutoff)
    base = {
        "as_of_date": cutoff_text,
        "sample_report": state.sample_report,
        "state_report": state.state_report,
        "fiscal_status": "NOT_TESTABLE",
    }
    if state.state_report.status != "READY":
        return StateTransitionFeasibilityReport(
            status="NO_GO",
            reason_codes=state.state_report.reason_codes,
            source_counts=dict(state.source_counts),
            driver_report=None,
            shadow_driver_report=None,
            core_validation=None,
            extended_validation=None,
            shadow_validation=None,
            core_decision=None,
            extended_decision=None,
            paired_skill=None,
            **base,
        )

    driver = driver_builder(cutoff, state)
    source_counts = {**state.source_counts, **driver.source_counts}
    if driver.driver_report.status != "DRIVER_READY":
        return StateTransitionFeasibilityReport(
            status="NO_GO",
            reason_codes=driver.driver_report.reason_codes,
            source_counts=source_counts,
            driver_report=driver.driver_report,
            shadow_driver_report=driver.shadow_report,
            core_validation=None,
            extended_validation=None,
            shadow_validation=None,
            core_decision=None,
            extended_decision=None,
            paired_skill=None,
            **base,
        )

    core_validation = validation_runner(driver.core_dataset)
    extended_validation = validation_runner(driver.extended_dataset)
    core_decision = task_evaluator(core_validation)
    extended_decision = task_evaluator(extended_validation)
    paired_skill = skill_comparator(core_validation, extended_validation)

    shadow_validation: TransitionValidationReport | None = None
    if (
        driver.shadow_dataset is not None
        and driver.shadow_report is not None
        and driver.shadow_report.status == "DRIVER_READY"
    ):
        shadow_validation = validation_runner(driver.shadow_dataset)

    pressure_qualified = (
        extended_decision.pressure_status == "READY"
        and paired_skill.pressure_common_origins > 0
        and paired_skill.pressure_mean_relative_skill > 0.0
    )
    destination_qualified = (
        extended_decision.destination_status == "READY"
        and paired_skill.destination_common_origins > 0
        and paired_skill.destination_mean_relative_skill > 0.0
    )
    if pressure_qualified and destination_qualified:
        status = "GO"
        reasons: tuple[str, ...] = ()
    elif pressure_qualified ^ destination_qualified:
        status = "LIMITED_GO"
        reasons = _reason_union(
            extended_decision.pressure_reason_codes,
            extended_decision.destination_reason_codes,
            paired_skill.reason_codes,
        )
    else:
        status = "NO_GO"
        reasons = _reason_union(
            extended_decision.pressure_reason_codes,
            extended_decision.destination_reason_codes,
            paired_skill.reason_codes,
        )

    return StateTransitionFeasibilityReport(
        status=status,
        reason_codes=reasons,
        source_counts=source_counts,
        driver_report=driver.driver_report,
        shadow_driver_report=driver.shadow_report,
        core_validation=core_validation,
        extended_validation=extended_validation,
        shadow_validation=shadow_validation,
        core_decision=core_decision,
        extended_decision=extended_decision,
        paired_skill=paired_skill,
        **base,
    )
