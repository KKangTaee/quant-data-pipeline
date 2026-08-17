from __future__ import annotations

import math

import pandas as pd

from finance.economic_cycle_observed_state import ObservedStateResult


def _observed(date: pd.Timestamp, phase: str | None) -> ObservedStateResult:
    return ObservedStateResult(
        observed_state={
            "as_of_date": date.date().isoformat(),
            "phase": phase,
            "data_status": "READY" if phase else "UNAVAILABLE",
        },
        recent_changes=(),
        transition_monitor={},
    )


def _fixture(phases: tuple[str, ...]) -> tuple[pd.DataFrame, tuple[ObservedStateResult, ...]]:
    dates = pd.date_range("2000-01-31", periods=len(phases), freq="ME")
    values = [float(index + 1) / 10.0 for index in range(len(phases))]
    panel = pd.DataFrame(
        {
            "forecast_origin": dates,
            "IPT_z": values,
            "H_z": values,
            "EMPLOY_z": values,
            "RUC_z": values,
            "activity_score": values,
            "labor_income_score": values,
            "level": values,
            "momentum": values,
            "level_change_1m": values,
            "level_change_3m": values,
            "level_change_6m": values,
            "momentum_change_1m": values,
            "momentum_change_3m": values,
            "momentum_change_6m": values,
            "activity_labor_dispersion": [0.0] * len(phases),
            "positive_breadth": [0.75] * len(phases),
            "phase_duration": list(range(1, len(phases) + 1)),
        }
    )
    return panel, tuple(
        _observed(date, phase)
        for date, phase in zip(dates, phases, strict=True)
    )


def test_two_release_confirmation_allows_non_adjacent_destination() -> None:
    from finance.economic_cycle_transition_dataset import build_transition_dataset

    panel, history = _fixture(
        (
            "contraction",
            "contraction",
            "slowdown",
            "slowdown",
            "expansion",
            "expansion",
            "recovery",
            "recovery",
            "recovery",
        )
    )

    dataset = build_transition_dataset(panel, history)
    rows = dataset.rows.set_index("forecast_origin")

    # The first differing release is only a candidate. The second confirms it.
    assert rows.loc[pd.Timestamp("2000-03-31"), "confirmed_phase"] == "contraction"
    assert rows.loc[pd.Timestamp("2000-04-30"), "confirmed_phase"] == "slowdown"
    assert rows.loc[pd.Timestamp("2000-04-30"), "episode_id"] == 1
    assert rows.loc[pd.Timestamp("2000-04-30"), "confirmed_transition_from"] == "contraction"
    assert rows.loc[pd.Timestamp("2000-04-30"), "confirmed_transition_to"] == "slowdown"

    # contraction -> slowdown is deliberately valid; no fixed cycle route is imposed.
    assert rows.loc[pd.Timestamp("2000-01-31"), "destination_target"] == "slowdown"
    assert rows.loc[pd.Timestamp("2000-01-31"), "destination_known_at"] == pd.Timestamp(
        "2000-04-30"
    )


def test_pressure_target_means_transition_confirmed_within_three_releases() -> None:
    from finance.economic_cycle_transition_dataset import build_transition_dataset

    panel, history = _fixture(
        (
            "recovery",
            "recovery",
            "recovery",
            "recovery",
            "recovery",
            "expansion",
            "expansion",
            "expansion",
            "expansion",
            "expansion",
        )
    )

    rows = build_transition_dataset(
        panel,
        history,
        pressure_horizon_releases=3,
    ).rows.set_index("forecast_origin")

    # Confirmation is 2000-07-31: four releases away from March, three from April.
    assert rows.loc[pd.Timestamp("2000-03-31"), "pressure_target"] == 0
    assert rows.loc[pd.Timestamp("2000-04-30"), "pressure_target"] == 1
    assert rows.loc[pd.Timestamp("2000-05-31"), "pressure_target"] == 1
    assert rows.loc[pd.Timestamp("2000-06-30"), "pressure_target"] == 1
    assert rows.loc[pd.Timestamp("2000-04-30"), "target_known_at"] == pd.Timestamp(
        "2000-07-31"
    )
    assert math.isnan(rows.loc[pd.Timestamp("2000-09-30"), "pressure_target"])


def test_episode_weights_sum_to_one_per_confirmed_episode() -> None:
    from finance.economic_cycle_transition_dataset import build_transition_dataset

    panel, history = _fixture(
        (
            "recovery",
            "recovery",
            "recovery",
            "expansion",
            "expansion",
            "expansion",
            "expansion",
            "slowdown",
            "slowdown",
            "slowdown",
            "slowdown",
            "slowdown",
        )
    )

    rows = build_transition_dataset(panel, history).rows
    eligible = rows.loc[rows["eligible"]]

    weight_sums = eligible.groupby("episode_id")["episode_weight"].sum()
    assert not weight_sums.empty
    assert all(abs(value - 1.0) < 1e-12 for value in weight_sums)
    assert set(rows["phase_recovery"].unique()) <= {0.0, 1.0}
    assert set(rows["phase_expansion"].unique()) <= {0.0, 1.0}


def test_missing_feature_keeps_audit_row_but_excludes_it_from_model() -> None:
    from finance.economic_cycle_transition_dataset import (
        CORE_FORECAST_FEATURES,
        build_transition_dataset,
    )

    panel, history = _fixture(("recovery",) * 8)
    panel.loc[3, "IPT_z"] = float("nan")

    dataset = build_transition_dataset(panel, history)
    row = dataset.rows.iloc[3]

    assert "IPT_z" in CORE_FORECAST_FEATURES
    assert not bool(row["eligible"])
    assert row["ineligible_reason"] == "MISSING_MODEL_FEATURE"
    assert row["episode_weight"] == 0.0
    assert len(dataset.rows) == len(panel)


def test_dataset_consumes_supplied_confirmed_frame_without_second_confirmation() -> None:
    from finance.economic_cycle_confirmed_state import build_confirmed_state_frame
    from finance.economic_cycle_transition_dataset import build_transition_dataset

    panel, history = _fixture(
        ("recovery", "recovery", "expansion", "expansion", "expansion")
    )
    confirmed = build_confirmed_state_frame(history)

    rows = build_transition_dataset(
        panel,
        history,
        confirmed_state_frame=confirmed,
    ).rows
    transition = rows.loc[rows["confirmed_transition_to"] == "expansion"].iloc[0]

    assert transition["forecast_origin"] == pd.Timestamp("2000-04-30")


def test_restrict_features_recalculates_eligibility_and_episode_weights() -> None:
    from finance.economic_cycle_transition_dataset import (
        COMPACT_CORE_FORECAST_FEATURES,
        build_transition_dataset,
        restrict_transition_dataset_features,
    )

    panel, history = _fixture(("recovery",) * 8)
    panel.loc[3, "IPT_z"] = float("nan")
    original = build_transition_dataset(panel, history)

    restricted = restrict_transition_dataset_features(
        original,
        COMPACT_CORE_FORECAST_FEATURES,
    )

    assert restricted.feature_names == COMPACT_CORE_FORECAST_FEATURES
    assert bool(restricted.rows.loc[3, "eligible"]) is True
    eligible = restricted.rows.loc[restricted.rows["eligible"]]
    assert all(
        abs(value - 1.0) < 1e-12
        for value in eligible.groupby("episode_id")["episode_weight"].sum()
    )
