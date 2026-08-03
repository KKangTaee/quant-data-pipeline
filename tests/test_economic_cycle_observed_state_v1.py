from __future__ import annotations

import importlib

import pandas as pd
import pytest


REAL_SERIES = (
    "INDPRO",
    "W875RX1",
    "RRSFS",
    "CFNAI",
    "PAYEMS",
    "UNRATE",
    "ICSA",
    "AWHMAN",
)


def _module():
    return importlib.import_module("finance.economic_cycle_observed_state")


def _panel(
    raw_levels: list[float],
    *,
    missing: tuple[str, ...] = (),
    stale: tuple[str, ...] = (),
) -> pd.DataFrame:
    origins = pd.date_range("2025-01-31", periods=len(raw_levels), freq="ME")
    rows: list[dict[str, object]] = []
    for origin, value in zip(origins, raw_levels, strict=True):
        row: dict[str, object] = {
            "forecast_origin": origin,
            "activity_score": value,
            "labor_income_score": value,
            "financial_leading_score": 0.25,
            "inflation_policy_score": 0.10,
        }
        for series_id in REAL_SERIES:
            row[f"{series_id}_z"] = None if series_id in missing else value
            row[f"{series_id}_stale"] = series_id in stale
        rows.append(row)
    return pd.DataFrame(rows)


@pytest.mark.parametrize(
    ("raw_levels", "expected_level", "expected_momentum", "expected_phase"),
    [
        ([-1.0, -1.0, -1.0, -0.5, -0.5, -0.5], -0.5, 0.5, "recovery"),
        ([0.5, 0.5, 0.5, 1.0, 1.0, 1.0], 1.0, 0.5, "expansion"),
        ([1.0, 1.0, 1.0, 0.5, 0.5, 0.5], 0.5, -0.5, "slowdown"),
        ([-0.5, -0.5, -0.5, -1.0, -1.0, -1.0], -1.0, -0.5, "contraction"),
        ([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 0.0, 0.0, "expansion"),
    ],
)
def test_observed_state_uses_literal_three_month_level_and_prior_window_momentum(
    raw_levels: list[float],
    expected_level: float,
    expected_momentum: float,
    expected_phase: str,
) -> None:
    result = _module().build_observed_state_snapshot(_panel(raw_levels))

    assert result.observed_state["level"] == pytest.approx(expected_level)
    assert result.observed_state["momentum"] == pytest.approx(expected_momentum)
    assert result.observed_state["phase"] == expected_phase
    assert result.observed_state["data_status"] == "READY"


def test_observed_state_eligibility_uses_only_eight_real_economy_series() -> None:
    module = _module()
    levels = [-1.0, -1.0, -1.0, -0.5, -0.5, -0.5]

    ready = module.build_observed_state_snapshot(_panel(levels))
    limited = module.build_observed_state_snapshot(
        _panel(levels, missing=("INDPRO", "PAYEMS"), stale=("CFNAI",))
    )
    unavailable = module.build_observed_state_snapshot(
        _panel(levels, missing=("INDPRO", "W875RX1", "PAYEMS"))
    )
    missing_factor_panel = _panel(levels).drop(columns=["activity_score"])
    missing_factor = module.build_observed_state_snapshot(missing_factor_panel)

    assert ready.observed_state["available_series"] == 8
    assert ready.observed_state["data_status"] == "READY"
    assert limited.observed_state["available_series"] == 6
    assert limited.observed_state["data_status"] == "LIMITED"
    assert unavailable.observed_state["available_series"] == 5
    assert unavailable.observed_state["data_status"] == "UNAVAILABLE"
    assert unavailable.observed_state["phase"] is None
    assert missing_factor.observed_state["data_status"] == "UNAVAILABLE"
    assert missing_factor.observed_state["phase"] is None


def test_breadth_and_recent_changes_use_literal_available_pairs() -> None:
    module = _module()
    panel = _panel([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    current = panel.index[-1]
    for series_id in REAL_SERIES[:3]:
        panel.loc[current, f"{series_id}_z"] = -1.0

    result = module.build_observed_state_snapshot(panel)
    changes = {row["horizon_months"]: row for row in result.recent_changes}

    assert result.observed_state["level_breadth"] == pytest.approx(5 / 8)
    assert result.observed_state["momentum_breadth"] == pytest.approx(5 / 8)
    assert changes[1]["composite_delta"] == pytest.approx(1.0)
    assert changes[3]["composite_delta"] == pytest.approx(3.0)
    assert changes[6]["composite_delta"] == pytest.approx(6.0)
    assert changes[1]["status"] == "STRENGTHENING"


def test_revision_reference_limits_or_promotes_confidence_without_overriding_phase() -> None:
    module = _module()
    pit = _panel([0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0])
    same_revision = pit.copy(deep=True)
    sensitive_revision = _panel([1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0])

    stable = module.build_observed_state_snapshot(pit, revised_panel=same_revision)
    sensitive = module.build_observed_state_snapshot(
        pit, revised_panel=sensitive_revision
    )

    assert stable.observed_state["phase"] == "expansion"
    assert stable.observed_state["revision_sensitivity"] == "STABLE"
    assert stable.observed_state["confidence"] == "HIGH"
    assert sensitive.observed_state["phase"] == "expansion"
    assert sensitive.observed_state["revision_sensitivity"] == "SENSITIVE"
    assert sensitive.observed_state["confidence"] == "MEDIUM"


def test_first_boundary_crossing_changes_observation_but_keeps_transition_anchor() -> None:
    module = _module()
    history = module.build_observed_state_history(
        _panel([-1.0, -1.0, -1.0, -2.0, -2.0, -2.0, 2.0])
    )

    crossing = history[-1]
    conditions = {
        row["condition_id"]: row["status"]
        for row in crossing.transition_monitor["conditions"]
    }
    assert crossing.observed_state["phase"] == "recovery"
    assert crossing.transition_monitor["anchor_phase"] == "contraction"
    assert crossing.transition_monitor["target_phase"] == "recovery"
    assert crossing.transition_monitor["status"] == "WATCH"
    assert crossing.transition_monitor["conditions_met"] == 2
    assert conditions == {
        "persistence": "UNMET",
        "diffusion": "MET",
        "corroboration": "MET",
    }
    assert len(crossing.transition_monitor["context"]) == 2


def test_initial_transition_anchor_records_first_valid_origin_without_claiming_confirmation() -> None:
    module = _module()
    history = module.build_observed_state_history(
        _panel([-1.0, -1.0, -1.0, -2.0, -2.0, -2.0])
    )

    initial = history[-1].transition_monitor

    assert initial["anchor_phase"] == "contraction"
    assert initial["anchor_started_at"] == "2025-06-30"
    assert initial["anchor_source"] == "INITIALIZED"
    assert initial["anchor_confirmed_at"] is None


def test_transition_confirms_on_three_conditions_and_promotes_anchor_next_release() -> None:
    module = _module()
    history = module.build_observed_state_history(
        _panel([-1.0, -1.0, -1.0, -2.0, -2.0, -2.0, 2.0, -1.0, 0.0])
    )

    confirmed = history[-2]
    promoted = history[-1]
    assert confirmed.transition_monitor["anchor_phase"] == "contraction"
    assert confirmed.transition_monitor["target_phase"] == "recovery"
    assert confirmed.transition_monitor["status"] == "CONFIRMED"
    assert confirmed.transition_monitor["conditions_met"] == 3
    assert confirmed.transition_monitor["confirmed_at"] == "2025-08-31"
    assert promoted.transition_monitor["anchor_phase"] == "recovery"
    assert promoted.transition_monitor["target_phase"] == "expansion"
    assert promoted.transition_monitor["anchor_started_at"] == "2025-08-31"
    assert promoted.transition_monitor["anchor_source"] == "CONFIRMED"
    assert promoted.transition_monitor["anchor_confirmed_at"] == "2025-08-31"


def test_candidate_reversal_returns_to_maintain_without_changing_anchor() -> None:
    module = _module()
    history = module.build_observed_state_history(
        _panel([-1.0, -1.0, -1.0, -2.0, -2.0, -2.0, 2.0, -6.0])
    )

    reversed_state = history[-1]
    assert reversed_state.observed_state["phase"] == "contraction"
    assert reversed_state.transition_monitor["anchor_phase"] == "contraction"
    assert reversed_state.transition_monitor["status"] == "MAINTAIN"
    assert reversed_state.transition_monitor["conditions_met"] == 0
    assert reversed_state.transition_monitor["candidate_started_at"] is None


def test_unavailable_month_breaks_persistence_but_keeps_confirmed_anchor() -> None:
    module = _module()
    panel = _panel(
        [-1.0, -1.0, -1.0, -2.0, -2.0, -2.0, 2.0, -1.0, -1.0]
    )
    unavailable_index = panel.index[-2]
    for series_id in REAL_SERIES[:3]:
        panel.loc[unavailable_index, f"{series_id}_z"] = None

    history = module.build_observed_state_history(panel)
    unavailable = history[-2]
    after_gap = history[-1]
    conditions = {
        row["condition_id"]: row["status"]
        for row in after_gap.transition_monitor["conditions"]
    }

    assert unavailable.observed_state["data_status"] == "UNAVAILABLE"
    assert unavailable.transition_monitor["anchor_phase"] == "contraction"
    assert conditions["persistence"] == "UNMET"
    assert after_gap.transition_monitor["status"] == "WATCH"


def test_non_adjacent_observation_does_not_skip_confirmed_anchor() -> None:
    module = _module()
    result = module.build_observed_state_snapshot(
        _panel([-1.0, -1.0, -1.0, -2.0, -2.0, -2.0, 5.0])
    )

    assert result.observed_state["phase"] == "expansion"
    assert result.transition_monitor["anchor_phase"] == "contraction"
    assert result.transition_monitor["target_phase"] == "recovery"
    assert result.transition_monitor["non_adjacent_observation"] is True
    assert result.transition_monitor["status"] == "WATCH"
