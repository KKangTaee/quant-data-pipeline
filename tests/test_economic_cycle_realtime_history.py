from __future__ import annotations

import math
from datetime import date

import pandas as pd
import pytest

from finance.economic_cycle_observed_state import ObservedStateResult
from finance.economic_cycle_transition_feasibility import TransitionSampleGate


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


def test_rtdsm_loader_filters_source_and_signal_window() -> None:
    from finance.loaders.economic_cycle_realtime import (
        load_rtdsm_signal_history,
    )

    rows = [
        {
            "series_id": "IPT",
            "observation_date": "2020-01-01",
            "realtime_start": "2020-02-29",
            "realtime_end": "2020-03-30",
            "source": "philadelphia_fed_rtdsm",
            "value": 100.0,
            "updated_at": "2020-02-29 23:59:59",
        },
        {
            "series_id": "IPT",
            "observation_date": "2018-01-01",
            "realtime_start": "2020-02-29",
            "realtime_end": "2020-03-30",
            "source": "philadelphia_fed_rtdsm",
            "value": 50.0,
            "updated_at": "2020-02-29 23:59:59",
        },
        {
            "series_id": "IPT",
            "observation_date": "2020-01-01",
            "realtime_start": "2020-02-29",
            "realtime_end": "2020-03-30",
            "source": "fred",
            "value": 999.0,
            "updated_at": "2020-02-29 23:59:59",
        },
        {
            "series_id": "EMPLOY",
            "observation_date": "2020-01-01",
            "realtime_start": "2020-02-29",
            "realtime_end": "2020-03-30",
            "source": "philadelphia_fed_rtdsm",
            "value": 200.0,
            "updated_at": "2020-02-29 23:59:59",
        },
    ]
    captured: list[tuple[str, tuple[object, ...]]] = []

    def query_fn(_database: str, sql: str, params: tuple[object, ...]):
        captured.append((sql, params))
        return rows

    result = load_rtdsm_signal_history(
        ["IPT"],
        start_date="2020-02-01",
        end_date="2020-03-31",
        as_of_date="2020-03-31",
        query_fn=query_fn,
    )

    assert [row["value"] for row in result] == [100.0]
    assert "source = %s" in captured[0][0]
    assert captured[0][1][0] == "philadelphia_fed_rtdsm"


def _vintage_rows() -> list[dict[str, object]]:
    intervals = (
        ("2020-01-31", "2020-02-28", 1.0),
        ("2020-02-29", "9999-12-31", 2.0),
    )
    configs = {
        "IPT": (("2019-07-01", 100.0), ("2020-01-01", 110.0)),
        "H": (("2019-10-01", 100.0), ("2020-01-01", 110.0)),
        "EMPLOY": (("2019-10-01", 100.0), ("2020-01-01", 110.0)),
        "RUC": (("2019-10-01", 5.0), ("2020-01-01", 4.0)),
    }
    rows: list[dict[str, object]] = []
    for series_id, values in configs.items():
        for realtime_start, realtime_end, revision in intervals:
            for observation_date, value in values:
                revised = value
                if observation_date == "2020-01-01":
                    if series_id == "RUC":
                        revised = value - (revision - 1.0)
                    else:
                        revised = value + 10.0 * (revision - 1.0)
                rows.append(
                    {
                        "series_id": series_id,
                        "observation_date": observation_date,
                        "realtime_start": realtime_start,
                        "realtime_end": realtime_end,
                        "source": "philadelphia_fed_rtdsm",
                        "value": revised,
                    }
                )
    return rows


def test_rtdsm_panel_uses_revision_eligible_at_each_origin() -> None:
    from finance.economic_cycle_realtime_history import (
        build_rtdsm_monthly_panel,
    )

    panel = build_rtdsm_monthly_panel(
        _vintage_rows(),
        forecast_origins=["2020-01-31", "2020-02-29"],
        minimum_history_months=2,
    )

    assert panel.loc[0, "EMPLOY_signal"] == pytest.approx(
        (math.pow(1.10, 4.0) - 1.0) * 100.0
    )
    assert panel.loc[1, "EMPLOY_signal"] == pytest.approx(
        (math.pow(1.20, 4.0) - 1.0) * 100.0
    )
    assert panel.loc[0, "IPT_signal"] == pytest.approx(
        (math.pow(1.10, 2.0) - 1.0) * 100.0
    )
    assert panel.loc[0, "RUC_signal"] == 1.0
    assert panel.loc[1, "RUC_signal"] == 2.0
    assert pd.isna(panel.loc[0, "EMPLOY_z"])
    assert math.isfinite(float(panel.loc[1, "EMPLOY_z"]))


def test_rtdsm_panel_vintage_lag_uses_later_revision_without_future_observations() -> None:
    from finance.economic_cycle_realtime_history import (
        build_rtdsm_monthly_panel,
    )

    realtime = build_rtdsm_monthly_panel(
        _vintage_rows(),
        forecast_origins=["2020-01-31", "2020-02-29"],
        minimum_history_months=2,
    )
    revised = build_rtdsm_monthly_panel(
        _vintage_rows(),
        forecast_origins=["2020-01-31", "2020-02-29"],
        minimum_history_months=2,
        vintage_lag_months=1,
    )

    assert revised.loc[0, "EMPLOY_signal"] > realtime.loc[0, "EMPLOY_signal"]
    assert revised.loc[0, "EMPLOY_latest_observation_date"] == "2020-01-01"
    assert revised.loc[0, "EMPLOY_vintage_date"] == "2020-02-29"


def test_rtdsm_panel_uses_one_month_backward_lag_without_interpolation() -> None:
    from finance.economic_cycle_realtime_history import (
        build_rtdsm_monthly_panel,
    )

    observations = pd.date_range("2019-07-01", "2020-05-01", freq="MS")
    rows: list[dict[str, object]] = []
    for series_id in ("IPT", "H", "EMPLOY", "RUC"):
        for index, observation in enumerate(observations):
            if series_id == "RUC" and observation == pd.Timestamp("2020-01-01"):
                continue
            value = (
                5.0 - index * 0.05 - index * index * 0.01
                if series_id == "RUC"
                else 100.0 + index
            )
            if observation == pd.Timestamp("2020-05-01"):
                value = 999.0
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": observation.date().isoformat(),
                    "realtime_start": "2019-07-31",
                    "realtime_end": "9999-12-31",
                    "source": "philadelphia_fed_rtdsm",
                    "value": value,
                }
            )

    panel = build_rtdsm_monthly_panel(
        rows,
        forecast_origins=pd.date_range("2020-01-31", "2020-04-30", freq="ME"),
        minimum_history_months=2,
    )
    april = panel.iloc[-1]

    # 2020-01 is absent, so use the actual 4M change from 2019-12 and
    # normalize it to the locked 3M RUC signal. The future May value is ignored.
    assert april["RUC_signal"] == pytest.approx(0.76 * 3.0 / 4.0)
    assert bool(april["RUC_lag_fallback"]) is True
    assert april["RUC_latest_observation_date"] == "2020-04-01"
    assert april["data_status"] == "LIMITED"


def test_rtdsm_panel_single_origin_preserves_unscaled_missing_scores() -> None:
    from finance.economic_cycle_realtime_history import (
        build_rtdsm_monthly_panel,
    )

    panel = build_rtdsm_monthly_panel(
        _vintage_rows(),
        forecast_origins=["2020-01-31"],
        minimum_history_months=60,
    )

    assert len(panel) == 1
    assert pd.isna(panel.loc[0, "activity_score"])
    assert pd.isna(panel.loc[0, "labor_income_score"])


def test_rtdsm_observed_history_waits_for_level_and_momentum() -> None:
    from finance.economic_cycle_realtime_history import (
        build_rtdsm_observed_history,
    )

    origins = pd.date_range("2000-01-31", periods=9, freq="ME")
    values = [-3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0]
    panel = pd.DataFrame(
        {
            "forecast_origin": origins,
            "activity_score": values,
            "labor_income_score": values,
            "data_status": ["READY"] * 9,
            "IPT_z": values,
            "H_z": values,
            "EMPLOY_z": values,
            "RUC_z": values,
        }
    )

    history = build_rtdsm_observed_history(panel)

    assert len(history) == 9
    assert all(
        item.observed_state["phase"] is None for item in history[:5]
    )
    assert history[5].observed_state["phase"] == "recovery"
    assert history[-1].observed_state["phase"] == "expansion"


def test_rtdsm_parity_metrics_are_hand_checkable() -> None:
    from finance.economic_cycle_realtime_history import (
        RtdsmParityGate,
        evaluate_rtdsm_parity,
    )

    dates = ["2020-01-31", "2020-02-29", "2020-03-31", "2020-04-30"]
    current = [
        _observed(item, phase)
        for item, phase in zip(
            dates,
            ("recovery", "expansion", "slowdown", "contraction"),
            strict=True,
        )
    ]
    rtdsm = [
        _observed(item, phase)
        for item, phase in zip(
            dates,
            ("recovery", "expansion", "contraction", "contraction"),
            strict=True,
        )
    ]

    report = evaluate_rtdsm_parity(
        rtdsm,
        current,
        gate=RtdsmParityGate(
            minimum_overlap_months=4,
            minimum_phase_agreement=0.70,
            minimum_kappa=0.60,
            minimum_level_side_agreement=0.70,
        ),
    )

    assert report.status == "PASS"
    assert report.overlap_months == 4
    assert report.phase_agreement == pytest.approx(0.75)
    assert report.level_side_agreement == pytest.approx(0.75)
    assert report.cohens_kappa == pytest.approx(2.0 / 3.0)
    assert report.confusion_counts["slowdown->contraction"] == 1


def test_rtdsm_parity_fails_each_locked_threshold_explicitly() -> None:
    from finance.economic_cycle_realtime_history import (
        RtdsmParityGate,
        evaluate_rtdsm_parity,
    )

    dates = ["2020-01-31", "2020-02-29"]
    current = [_observed(dates[0], "recovery"), _observed(dates[1], "expansion")]
    rtdsm = [_observed(dates[0], "expansion"), _observed(dates[1], "recovery")]

    report = evaluate_rtdsm_parity(
        rtdsm,
        current,
        gate=RtdsmParityGate(
            minimum_overlap_months=3,
            minimum_phase_agreement=0.5,
            minimum_kappa=0.1,
            minimum_level_side_agreement=0.5,
        ),
    )

    assert report.status == "NO_GO_PARITY"
    assert report.reason_codes == (
        "INSUFFICIENT_COMMON_PERIOD",
        "LOW_PHASE_AGREEMENT",
        "LOW_COHEN_KAPPA",
        "LOW_LEVEL_SIDE_AGREEMENT",
    )


def test_rtdsm_parity_defines_perfect_zero_variance_kappa() -> None:
    from finance.economic_cycle_realtime_history import (
        RtdsmParityGate,
        evaluate_rtdsm_parity,
    )

    current = [_observed("2020-01-31", "recovery")]
    report = evaluate_rtdsm_parity(
        current,
        current,
        gate=RtdsmParityGate(1, 1.0, 1.0, 1.0),
    )

    assert report.cohens_kappa == 1.0
    assert report.status == "PASS"


def _transition_history() -> list[ObservedStateResult]:
    return [
        _observed("2020-01-31", "recovery"),
        _observed("2020-02-29", "recovery"),
        _observed("2020-03-31", "expansion"),
        _observed("2020-04-30", "expansion"),
    ]


def test_rtdsm_readiness_requires_sample_parity_and_complete_sources() -> None:
    from finance.economic_cycle_realtime_history import (
        RtdsmParityGate,
        evaluate_rtdsm_model_readiness,
    )

    history = _transition_history()
    sample_gate = TransitionSampleGate(
        minimum_usable_origins=4,
        minimum_events=1,
        minimum_events_per_destination=0,
        minimum_events_per_origin=0,
        holdout_fraction=0.5,
        minimum_holdout_events=1,
        minimum_holdout_events_per_destination=0,
    )
    parity_gate = RtdsmParityGate(4, 1.0, 1.0, 1.0)

    ready = evaluate_rtdsm_model_readiness(
        history,
        history,
        source_complete=True,
        sample_gate=sample_gate,
        parity_gate=parity_gate,
    )
    incomplete = evaluate_rtdsm_model_readiness(
        history,
        history,
        source_complete=False,
        sample_gate=sample_gate,
        parity_gate=parity_gate,
    )
    contradictory = [
        _observed("2020-01-31", "expansion"),
        _observed("2020-02-29", "expansion"),
        _observed("2020-03-31", "recovery"),
        _observed("2020-04-30", "recovery"),
    ]
    parity_failed = evaluate_rtdsm_model_readiness(
        history,
        contradictory,
        source_complete=True,
        sample_gate=sample_gate,
        parity_gate=parity_gate,
    )

    assert ready.status == "GO_MODEL_EXPERIMENT"
    assert incomplete.status == "NO_GO_DATA"
    assert "INCOMPLETE_RTDSM_SOURCE" in incomplete.reason_codes
    assert parity_failed.status == "NO_GO_PARITY"
