from __future__ import annotations

import inspect

import pandas as pd

from finance.economic_cycle_core_state import CoreStateAuditReport
from finance.economic_cycle_observed_state import ObservedStateResult, PHASE_SEQUENCE
from finance.economic_cycle_transition_feasibility import TransitionFeasibilityReport
from finance.economic_cycle_transition_validation import (
    ProbabilityMetrics,
    TransitionValidationReport,
)


def _sample_report(status: str = "GO_EXPERIMENT") -> TransitionFeasibilityReport:
    return TransitionFeasibilityReport(
        status=status,
        reason_codes=() if status == "GO_EXPERIMENT" else ("INSUFFICIENT_TRANSITION_EVENTS",),
        total_origins=200,
        usable_origins=200,
        first_usable_at="2000-01-31",
        last_usable_at="2016-08-31",
        phase_origin_counts={phase: 50 for phase in PHASE_SEQUENCE},
        event_count=80,
        origin_event_counts={phase: 20 for phase in PHASE_SEQUENCE},
        destination_event_counts={phase: 20 for phase in PHASE_SEQUENCE},
        route_event_counts={},
        holdout_event_count=20,
        holdout_destination_event_counts={phase: 5 for phase in PHASE_SEQUENCE},
        events=(),
    )


def _core_report(status: str = "READY") -> CoreStateAuditReport:
    return CoreStateAuditReport(
        status=status,
        reason_codes=() if status == "READY" else ("REVISION_PHASE_INSTABILITY",),
        usable_origins=200,
        phase_origin_counts={phase: 50 for phase in PHASE_SEQUENCE},
        phase_occupancy={phase: 0.25 for phase in PHASE_SEQUENCE},
        episode_count=80,
        one_month_episode_fraction=0.0,
        revision_overlap=180,
        revision_phase_agreement=0.90,
        revision_level_side_agreement=0.95,
        nber_recession_months=24,
        nber_below_side_fraction=0.80,
        nber_peak_count=4,
        nber_peak_capture_rate=0.75,
        nber_trough_count=4,
        nber_trough_capture_rate=0.75,
        sample_status="GO_EXPERIMENT",
    )


def _validation_report(*, ready: bool) -> TransitionValidationReport:
    model = ProbabilityMetrics(
        brier=0.10 if ready else 0.13,
        log_loss=0.20 if ready else 0.25,
        ece=0.05,
    )
    baseline = ProbabilityMetrics(brier=0.12, log_loss=0.24, ece=0.08)
    return TransitionValidationReport(
        pressure_predictions=(),
        destination_predictions=(),
        pressure_metrics=model,
        pressure_baseline_metrics={"global_rate": baseline, "duration_hazard": baseline},
        destination_metrics=model,
        destination_baseline_metrics={"phase_frequency": baseline, "fixed_cycle": baseline},
        pressure_event_count=50,
        pressure_holdout_has_both=True,
        destination_event_count=50,
        destination_event_counts={phase: 12 for phase in PHASE_SEQUENCE},
        destination_final_25_counts={phase: 3 for phase in PHASE_SEQUENCE},
        invalid_probability_count=0,
    )


def _panel() -> pd.DataFrame:
    dates = pd.date_range("2000-01-31", periods=12, freq="ME")
    values = [float(index) for index in range(12)]
    return pd.DataFrame(
        {
            "forecast_origin": dates,
            "IPT_z": values,
            "H_z": values,
            "EMPLOY_z": values,
            "RUC_z": values,
            "activity_score": values,
            "labor_income_score": values,
            "data_status": ["READY"] * 12,
        }
    )


def _history() -> tuple[ObservedStateResult, ...]:
    dates = pd.date_range("2000-01-31", periods=12, freq="ME")
    phases = tuple(PHASE_SEQUENCE[index % 4] for index in range(12))
    return tuple(
        ObservedStateResult(
            observed_state={
                "as_of_date": date.date().isoformat(),
                "phase": phase,
                "data_status": "READY",
            },
            recent_changes=(),
            transition_monitor={},
        )
        for date, phase in zip(dates, phases, strict=True)
    )


def _dependencies(core_status: str, validation_ready: bool, calls: list[str]):
    vintage_rows = [{"series_id": phase} for phase in ("IPT", "H", "EMPLOY", "RUC")]

    def validation_runner(_dataset):
        calls.append("validation")
        return _validation_report(ready=validation_ready)

    return {
        "rtdsm_loader": lambda **_kwargs: vintage_rows,
        "nber_loader": lambda **_kwargs: {"2000-01-31": False},
        "panel_builder": lambda *_args, **_kwargs: _panel(),
        "history_builder": lambda _panel_value: _history(),
        "sample_evaluator": lambda _history_value: _sample_report(),
        "core_evaluator": lambda *_args, **_kwargs: _core_report(core_status),
        "validation_runner": validation_runner,
    }


def test_core_state_failure_stops_before_validation() -> None:
    from finance.economic_cycle_transition_experiment import (
        run_transition_experiment,
    )

    calls: list[str] = []
    report = run_transition_experiment(
        "2026-07-31",
        **_dependencies("LIMITED", True, calls),
    )

    assert report.status == "NO_GO_CORE_STATE"
    assert calls == []
    assert report.validation_report is None


def test_core_state_pass_runs_validation_exactly_once() -> None:
    from finance.economic_cycle_transition_experiment import (
        run_transition_experiment,
    )

    calls: list[str] = []
    report = run_transition_experiment(
        "2026-07-31",
        **_dependencies("READY", True, calls),
    )

    assert report.status == "READY"
    assert calls == ["validation"]
    assert report.publication_decision is not None
    assert report.publication_decision.status == "READY"


def test_limited_model_gate_returns_no_go_model_without_writer_boundary() -> None:
    from finance.economic_cycle_transition_experiment import (
        run_transition_experiment,
    )

    calls: list[str] = []
    report = run_transition_experiment(
        "2026-07-31",
        **_dependencies("READY", False, calls),
    )

    assert report.status == "NO_GO_MODEL"
    assert "PRESSURE_BASELINE_UNDERPERFORMANCE" in report.reason_codes
    assert "writer" not in inspect.signature(run_transition_experiment).parameters
