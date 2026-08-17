from __future__ import annotations

import pandas as pd

from finance.economic_cycle_observed_state import ObservedStateResult


def _history(phases: tuple[str | None, ...]) -> tuple[ObservedStateResult, ...]:
    dates = pd.date_range("2000-01-31", periods=len(phases), freq="ME")
    return tuple(
        ObservedStateResult(
            observed_state={
                "as_of_date": date.date().isoformat(),
                "phase": phase,
                "data_status": "READY" if phase else "UNAVAILABLE",
            },
            recent_changes=(),
            transition_monitor={},
        )
        for date, phase in zip(dates, phases, strict=True)
    )


def test_bootstrap_requires_two_matching_usable_releases() -> None:
    from finance.economic_cycle_confirmed_state import build_confirmed_state_frame

    rows = build_confirmed_state_frame(
        _history(("recovery", "expansion", "expansion"))
    ).set_index("forecast_origin")

    assert pd.isna(rows.loc[pd.Timestamp("2000-01-31"), "confirmed_phase"])
    assert pd.isna(rows.loc[pd.Timestamp("2000-02-29"), "confirmed_phase"])
    assert rows.loc[pd.Timestamp("2000-03-31"), "confirmed_phase"] == "expansion"
    assert rows.loc[pd.Timestamp("2000-03-31"), "episode_id"] == 0
    assert pd.isna(
        rows.loc[pd.Timestamp("2000-03-31"), "confirmed_transition_to"]
    )


def test_gap_resets_candidate_and_non_adjacent_transition_is_not_backdated() -> None:
    from finance.economic_cycle_confirmed_state import build_confirmed_state_frame

    rows = build_confirmed_state_frame(
        _history(
            (
                "contraction",
                "contraction",
                "slowdown",
                None,
                "slowdown",
                "slowdown",
            )
        )
    ).set_index("forecast_origin")

    assert rows.loc[pd.Timestamp("2000-03-31"), "candidate_streak"] == 1
    assert rows.loc[pd.Timestamp("2000-04-30"), "candidate_streak"] == 0
    assert rows.loc[pd.Timestamp("2000-05-31"), "confirmed_phase"] == "contraction"
    assert rows.loc[pd.Timestamp("2000-06-30"), "confirmed_phase"] == "slowdown"
    assert (
        rows.loc[pd.Timestamp("2000-06-30"), "confirmed_transition_from"]
        == "contraction"
    )
    assert (
        rows.loc[pd.Timestamp("2000-06-30"), "confirmed_transition_to"]
        == "slowdown"
    )


def test_confirmed_history_marks_prebootstrap_rows_unavailable() -> None:
    from finance.economic_cycle_confirmed_state import (
        build_confirmed_observed_history,
        build_confirmed_state_frame,
    )

    confirmed = build_confirmed_observed_history(
        build_confirmed_state_frame(_history(("recovery", "recovery", "recovery")))
    )

    assert confirmed[0].observed_state["data_status"] == "UNAVAILABLE"
    assert confirmed[0].observed_state["phase"] is None
    assert confirmed[1].observed_state["data_status"] == "READY"
    assert confirmed[1].observed_state["phase"] == "recovery"
    assert confirmed[1].transition_monitor["candidate_streak"] == 0


def test_confirmation_releases_must_be_at_least_two() -> None:
    from finance.economic_cycle_confirmed_state import build_confirmed_state_frame

    try:
        build_confirmed_state_frame(_history(("recovery",)), confirmation_releases=1)
    except ValueError as exc:
        assert str(exc) == "confirmation_releases must be at least 2"
    else:
        raise AssertionError("confirmation_releases=1 must be rejected")
