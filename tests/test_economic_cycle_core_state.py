from __future__ import annotations

from dataclasses import replace

import pandas as pd

from finance.economic_cycle_observed_state import ObservedStateResult
from finance.economic_cycle_transition_feasibility import (
    TransitionFeasibilityReport,
)


def _observed(date_text: str, phase: str | None) -> ObservedStateResult:
    return ObservedStateResult(
        observed_state={
            "as_of_date": date_text,
            "phase": phase,
            "data_status": "READY" if phase else "UNAVAILABLE",
        },
        recent_changes=(),
        transition_monitor={},
    )


def _sample_report(status: str = "GO_EXPERIMENT") -> TransitionFeasibilityReport:
    reasons = () if status == "GO_EXPERIMENT" else ("INSUFFICIENT_TRANSITION_EVENTS",)
    return TransitionFeasibilityReport(
        status=status,
        reason_codes=reasons,
        total_origins=200,
        usable_origins=200,
        first_usable_at="2000-01-31",
        last_usable_at="2016-08-31",
        phase_origin_counts={
            "recovery": 50,
            "expansion": 50,
            "slowdown": 50,
            "contraction": 50,
        },
        event_count=80,
        origin_event_counts={
            "recovery": 20,
            "expansion": 20,
            "slowdown": 20,
            "contraction": 20,
        },
        destination_event_counts={
            "recovery": 20,
            "expansion": 20,
            "slowdown": 20,
            "contraction": 20,
        },
        route_event_counts={},
        holdout_event_count=20,
        holdout_destination_event_counts={
            "recovery": 5,
            "expansion": 5,
            "slowdown": 5,
            "contraction": 5,
        },
        events=(),
    )


def _core_panel() -> pd.DataFrame:
    values = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 2.0, 1.0, 0.0]
    return pd.DataFrame(
        {
            "forecast_origin": pd.date_range("2000-01-31", periods=10, freq="ME"),
            "IPT_z": values,
            "H_z": values,
            "EMPLOY_z": values,
            "RUC_z": values,
            "activity_score": values,
            "labor_income_score": values,
            "data_status": ["READY"] * 10,
        }
    )


def test_core_feature_panel_derives_level_momentum_changes_and_duration() -> None:
    from finance.economic_cycle_core_state import build_core_feature_panel

    panel = build_core_feature_panel(_core_panel())

    assert {
        "raw_level",
        "level",
        "momentum",
        "level_change_1m",
        "level_change_3m",
        "level_change_6m",
        "momentum_change_1m",
        "momentum_change_3m",
        "momentum_change_6m",
        "activity_labor_dispersion",
        "positive_breadth",
        "phase",
        "phase_duration",
    } <= set(panel)
    assert panel.loc[5, "level"] == 1.0
    assert panel.loc[5, "momentum"] == 3.0
    assert panel.loc[5, "phase"] == "expansion"
    assert panel.loc[5, "positive_breadth"] == 1.0
    assert panel.loc[5, "activity_labor_dispersion"] == 0.0


def _gate():
    from finance.economic_cycle_core_state import CoreStateGate

    return CoreStateGate(
        minimum_phase_occupancy=0.0,
        maximum_phase_occupancy=1.0,
        maximum_one_month_episode_fraction=1.0,
        minimum_revision_overlap=1,
        minimum_revision_phase_agreement=0.0,
        minimum_revision_level_side_agreement=0.0,
        minimum_nber_recession_months=1,
        minimum_nber_below_side_fraction=0.0,
        minimum_nber_peaks=1,
        minimum_nber_peak_capture_rate=0.0,
        minimum_nber_troughs=1,
        minimum_nber_trough_capture_rate=0.0,
    )


def test_core_state_gate_passes_hand_checkable_semantic_fixture() -> None:
    from finance.economic_cycle_core_state import evaluate_core_state_gate

    dates = pd.date_range("2000-01-31", periods=8, freq="ME")
    phases = (
        "contraction",
        "contraction",
        "recovery",
        "recovery",
        "expansion",
        "expansion",
        "slowdown",
        "slowdown",
    )
    history = tuple(
        _observed(date.date().isoformat(), phase)
        for date, phase in zip(dates, phases, strict=True)
    )
    nber = {
        date.date().isoformat(): value
        for date, value in zip(
            dates,
            (False, True, True, True, False, False, False, False),
            strict=True,
        )
    }

    report = evaluate_core_state_gate(
        _core_panel().iloc[:8],
        history,
        history,
        nber_months=nber,
        sample_report=_sample_report(),
        gate=_gate(),
    )

    assert report.status == "READY"
    assert report.reason_codes == ()
    assert report.phase_origin_counts == {
        "recovery": 2,
        "expansion": 2,
        "slowdown": 2,
        "contraction": 2,
    }
    assert report.revision_phase_agreement == 1.0
    assert report.revision_level_side_agreement == 1.0
    assert report.nber_peak_count == 1
    assert report.nber_trough_count == 1


def test_core_state_gate_reports_independent_failure_reasons() -> None:
    from finance.economic_cycle_core_state import evaluate_core_state_gate

    dates = pd.date_range("2000-01-31", periods=16, freq="ME")
    expansion = tuple(_observed(date.date().isoformat(), "expansion") for date in dates)
    contraction = tuple(
        _observed(date.date().isoformat(), "contraction") for date in dates
    )
    nber = {
        date.date().isoformat(): value
        for date, value in zip(
            dates,
            (
                False,
                False,
                True,
                True,
                True,
                True,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ),
            strict=True,
        )
    }
    strict = replace(
        _gate(),
        minimum_phase_occupancy=0.08,
        maximum_phase_occupancy=0.50,
        minimum_revision_phase_agreement=0.60,
        minimum_revision_level_side_agreement=0.80,
        minimum_nber_below_side_fraction=0.65,
        minimum_nber_peak_capture_rate=0.70,
        minimum_nber_trough_capture_rate=0.70,
    )

    report = evaluate_core_state_gate(
        _core_panel(),
        expansion,
        contraction,
        nber_months=nber,
        sample_report=_sample_report("NO_GO_DATA"),
        gate=strict,
    )

    assert report.status == "NO_GO_CORE_STATE"
    assert {
        "PHASE_OCCUPANCY",
        "REVISION_PHASE_INSTABILITY",
        "REVISION_SIDE_INSTABILITY",
        "NBER_RECESSION_SEMANTICS",
        "NBER_PEAK_CAPTURE",
        "NBER_TROUGH_CAPTURE",
        "SAMPLE_GATE_FAILED",
    } <= set(report.reason_codes)


def test_core_state_gate_rejects_excess_one_month_episodes() -> None:
    from finance.economic_cycle_core_state import evaluate_core_state_gate

    dates = pd.date_range("2000-01-31", periods=8, freq="ME")
    phases = ("recovery", "expansion") * 4
    history = tuple(
        _observed(date.date().isoformat(), phase)
        for date, phase in zip(dates, phases, strict=True)
    )
    nber = {
        date.date().isoformat(): value
        for date, value in zip(
            dates,
            (False, True, True, False, False, False, False, False),
            strict=True,
        )
    }
    gate = replace(_gate(), maximum_one_month_episode_fraction=0.25)

    report = evaluate_core_state_gate(
        _core_panel().iloc[:8],
        history,
        history,
        nber_months=nber,
        sample_report=_sample_report(),
        gate=gate,
    )

    assert "ONE_MONTH_EPISODES" in report.reason_codes


def test_core_state_gate_rejects_unavailable_latest_confirmed_origin() -> None:
    from finance.economic_cycle_core_state import evaluate_core_state_gate

    dates = pd.date_range("2000-01-31", periods=8, freq="ME")
    phases = (
        "contraction",
        "contraction",
        "recovery",
        "recovery",
        "expansion",
        "expansion",
        "slowdown",
        None,
    )
    history = tuple(
        _observed(date.date().isoformat(), phase)
        for date, phase in zip(dates, phases, strict=True)
    )
    nber = {
        date.date().isoformat(): value
        for date, value in zip(
            dates,
            (False, True, True, True, False, False, False, False),
            strict=True,
        )
    }

    report = evaluate_core_state_gate(
        _core_panel().iloc[:8],
        history,
        history,
        nber_months=nber,
        sample_report=_sample_report(),
        gate=_gate(),
    )

    assert report.status == "NO_GO_CORE_STATE"
    assert "INCOMPLETE_SOURCE_COVERAGE" in report.reason_codes
