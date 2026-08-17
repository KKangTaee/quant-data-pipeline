from __future__ import annotations

import inspect
import json

import pandas as pd

from finance.economic_cycle_core_state import CoreStateAuditReport
from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_transition_comparison import (
    PairedSkillReport,
    TransitionTaskDecision,
)
from finance.economic_cycle_transition_drivers import DriverCoverageReport
from finance.economic_cycle_transition_feasibility import TransitionFeasibilityReport
from finance.economic_cycle_transition_validation import (
    ProbabilityMetrics,
    TransitionValidationReport,
)


def _sample_report() -> TransitionFeasibilityReport:
    return TransitionFeasibilityReport(
        status="GO_EXPERIMENT",
        reason_codes=(),
        total_origins=240,
        usable_origins=220,
        first_usable_at="2000-01-31",
        last_usable_at="2019-12-31",
        phase_origin_counts={phase: 55 for phase in PHASE_SEQUENCE},
        event_count=60,
        origin_event_counts={phase: 15 for phase in PHASE_SEQUENCE},
        destination_event_counts={phase: 15 for phase in PHASE_SEQUENCE},
        route_event_counts={},
        holdout_event_count=15,
        holdout_destination_event_counts={phase: 3 for phase in PHASE_SEQUENCE},
        events=(),
    )


def _state_report(status: str) -> CoreStateAuditReport:
    return CoreStateAuditReport(
        status=status,
        reason_codes=() if status == "READY" else ("PHASE_OCCUPANCY",),
        usable_origins=220,
        phase_origin_counts={phase: 55 for phase in PHASE_SEQUENCE},
        phase_occupancy={phase: 0.25 for phase in PHASE_SEQUENCE},
        episode_count=60,
        one_month_episode_fraction=0.0,
        revision_overlap=200,
        revision_phase_agreement=0.8,
        revision_level_side_agreement=0.9,
        nber_recession_months=24,
        nber_below_side_fraction=0.75,
        nber_peak_count=4,
        nber_peak_capture_rate=0.75,
        nber_trough_count=4,
        nber_trough_capture_rate=0.75,
        sample_status="GO_EXPERIMENT",
    )


def _driver_report(status: str) -> DriverCoverageReport:
    return DriverCoverageReport(
        status=status,
        reason_codes=() if status == "DRIVER_READY" else ("INSUFFICIENT_DRIVER_TRANSITIONS",),
        usable_origins=200,
        independent_transitions=55,
        total_confirmed_transitions=60,
        destination_counts={phase: 12 for phase in PHASE_SEQUENCE},
        holdout_destination_counts={phase: 3 for phase in PHASE_SEQUENCE},
        series_coverage={},
    )


def _validation_report() -> TransitionValidationReport:
    metrics = ProbabilityMetrics(brier=0.1, log_loss=0.2, ece=0.05)
    return TransitionValidationReport(
        pressure_predictions=(),
        destination_predictions=(),
        pressure_metrics=metrics,
        pressure_baseline_metrics={},
        destination_metrics=metrics,
        destination_baseline_metrics={},
        pressure_event_count=50,
        pressure_holdout_has_both=True,
        destination_event_count=50,
        destination_event_counts={phase: 12 for phase in PHASE_SEQUENCE},
        destination_final_25_counts={phase: 3 for phase in PHASE_SEQUENCE},
        invalid_probability_count=0,
    )


def _decision(pressure: str, destination: str) -> TransitionTaskDecision:
    return TransitionTaskDecision(
        pressure_status=pressure,
        pressure_reason_codes=() if pressure == "READY" else ("PRESSURE_LIMITED",),
        destination_status=destination,
        destination_reason_codes=() if destination == "READY" else ("DESTINATION_LIMITED",),
        combined_status=(
            "READY" if pressure == destination == "READY" else "LIMITED"
        ),
    )


def _skill(pressure: float, destination: float) -> PairedSkillReport:
    reasons = []
    if pressure <= 0:
        reasons.append("PRESSURE_NO_PAIRED_IMPROVEMENT")
    if destination <= 0:
        reasons.append("DESTINATION_NO_PAIRED_IMPROVEMENT")
    return PairedSkillReport(
        status="READY" if not reasons else "LIMITED",
        reason_codes=tuple(reasons),
        pressure_common_origins=40,
        destination_common_origins=40,
        pressure_mean_relative_skill=pressure,
        destination_mean_relative_skill=destination,
        pressure_metrics={},
        destination_metrics={},
    )


def _dependencies(
    calls: list[str],
    *,
    state_status: str = "READY",
    driver_status: str = "DRIVER_READY",
    core_decision: TransitionTaskDecision | None = None,
    extended_decision: TransitionTaskDecision | None = None,
    paired_skill: PairedSkillReport | None = None,
):
    from finance.economic_cycle_state_transition_experiment import (
        DriverStageResult,
        StateStageResult,
    )

    validation = _validation_report()

    def state_builder(_cutoff):
        calls.append("state")
        return StateStageResult(
            source_counts={"IPT": 100, "H": 100, "EMPLOY": 100, "RUC": 100},
            core_panel=pd.DataFrame(),
            raw_history=(),
            confirmed_state_frame=pd.DataFrame(),
            sample_report=_sample_report(),
            state_report=_state_report(state_status),
        )

    def driver_builder(_cutoff, _state):
        calls.append("driver")
        return DriverStageResult(
            core_dataset="core",
            extended_dataset="extended",
            shadow_dataset=None,
            driver_report=_driver_report(driver_status),
            shadow_report=None,
            source_counts={"driver_rows": 1000, "market_rows": 0},
        )

    def validation_runner(dataset):
        calls.append(f"validate:{dataset}")
        return validation

    decisions = {
        id(validation): extended_decision or _decision("READY", "READY")
    }
    decision_calls = 0

    def task_evaluator(report):
        nonlocal decision_calls
        decision_calls += 1
        if decision_calls == 1:
            return core_decision or _decision("READY", "READY")
        return decisions[id(report)]

    return {
        "state_builder": state_builder,
        "driver_builder": driver_builder,
        "validation_runner": validation_runner,
        "task_evaluator": task_evaluator,
        "skill_comparator": lambda _core, _extended: paired_skill
        or _skill(0.05, 0.04),
    }


def test_state_failure_stops_before_driver_and_model_work() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        run_state_transition_feasibility,
    )

    calls: list[str] = []
    report = run_state_transition_feasibility(
        "2026-07-31",
        **_dependencies(calls, state_status="NO_GO_CORE_STATE"),
    )

    assert report.status == "NO_GO"
    assert report.driver_report is None
    assert report.core_validation is None
    assert report.extended_validation is None
    assert calls == ["state"]


def test_driver_failure_runs_state_but_stops_before_model_fit() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        run_state_transition_feasibility,
    )

    calls: list[str] = []
    report = run_state_transition_feasibility(
        "2026-07-31",
        **_dependencies(calls, driver_status="SHADOW_ONLY"),
    )

    assert report.status == "NO_GO"
    assert report.driver_report is not None
    assert report.extended_validation is None
    assert calls == ["state", "driver"]


def test_extended_ready_and_paired_ready_returns_go() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        run_state_transition_feasibility,
    )

    calls: list[str] = []
    report = run_state_transition_feasibility(
        "2026-07-31",
        **_dependencies(calls),
    )

    assert report.status == "GO"
    assert calls == ["state", "driver", "validate:core", "validate:extended"]
    assert report.fiscal_status == "NOT_TESTABLE"
    json.dumps(report.to_dict(), allow_nan=False, default=str)


def test_pressure_and_core_destination_ready_ignore_extended_destination_failure() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        run_state_transition_feasibility,
    )

    calls: list[str] = []
    report = run_state_transition_feasibility(
        "2026-07-31",
        **_dependencies(
            calls,
            extended_decision=_decision("READY", "LIMITED"),
            paired_skill=_skill(0.03, -0.01),
        ),
    )

    assert report.status == "GO"
    assert "DESTINATION_LIMITED" not in report.reason_codes


def test_core_destination_failure_blocks_extended_pressure_go() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        run_state_transition_feasibility,
    )

    calls: list[str] = []
    report = run_state_transition_feasibility(
        "2026-07-31",
        **_dependencies(
            calls,
            core_decision=_decision("LIMITED", "LIMITED"),
            extended_decision=_decision("READY", "READY"),
            paired_skill=_skill(0.03, 0.04),
        ),
    )

    assert report.status == "LIMITED_GO"
    assert "DESTINATION_LIMITED" in report.reason_codes


def test_experiment_has_no_writer_boundary() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        run_state_transition_feasibility,
    )

    assert "writer" not in inspect.signature(run_state_transition_feasibility).parameters


def test_driver_vintage_loader_falls_back_to_realtime_history() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        _load_driver_vintages,
    )

    requested_fallback: list[str] = []

    def released_loader(**_kwargs):
        return (
            {
                "series_id": "DGS2",
                "observation_date": "2000-01-31",
                "released_at": "2000-02-01T00:00:00Z",
                "value": 5.0,
            },
        )

    def history_loader(series_ids, **_kwargs):
        requested_fallback.extend(series_ids)
        return [
            {
                "series_id": "PERMIT",
                "observation_date": "2000-01-31",
                "realtime_start": "2000-02-01",
                "value": 1000.0,
            }
        ]

    rows = _load_driver_vintages(
        pd.Timestamp("2026-07-31"),
        released_loader=released_loader,
        history_loader=history_loader,
    )

    assert "DGS2" not in requested_fallback
    assert {str(row["series_id"]) for row in rows} == {"DGS2", "PERMIT"}


def test_driver_market_loader_requests_baa10y_from_db_only_path() -> None:
    from finance.economic_cycle_state_transition_experiment import (
        _load_driver_market_rows,
    )

    requested: list[tuple[str, ...]] = []

    def market_loader(*, series_ids, **_kwargs):
        requested.append(tuple(series_ids))
        return [
            {
                "series_id": "BAA10Y",
                "observation_date": "2000-01-31",
                "value": 2.0,
            }
        ]

    rows = _load_driver_market_rows(
        pd.Timestamp("2026-07-31"),
        market_loader=market_loader,
        asset_loader=lambda **_kwargs: [],
    )

    assert requested == [("BAA10Y", "VIXCLS")]
    assert rows[0]["series_id"] == "BAA10Y"
