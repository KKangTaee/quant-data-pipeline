from __future__ import annotations

import pandas as pd

from finance.economic_cycle_observed_state import (
    REAL_ECONOMY_SERIES,
    build_observed_state_history,
    phase_from_coordinates,
)


LITERAL_LEVELS = (-1.0, -1.0, -1.0, -2.0, -2.0, -2.0, 2.0, -1.0, 0.0, 1.0, 1.0)


def _literal_panel(
    levels: tuple[float, ...] = LITERAL_LEVELS,
    *,
    nber_recession: float = 0.0,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for origin, value in zip(
        pd.date_range("2025-01-31", periods=len(levels), freq="ME"),
        levels,
        strict=True,
    ):
        row: dict[str, object] = {
            "forecast_origin": origin,
            "activity_score": value,
            "labor_income_score": value,
            "financial_leading_score": 0.25,
            "inflation_policy_score": 0.10,
            "USREC_signal": nber_recession,
        }
        for series_id in REAL_ECONOMY_SERIES:
            row[f"{series_id}_z"] = value
            row[f"{series_id}_stale"] = False
        rows.append(row)
    return pd.DataFrame(rows)


def test_literal_history_meets_observed_state_and_transition_acceptance_contract() -> None:
    history = build_observed_state_history(_literal_panel())

    plotted_phase_mismatches = 0
    confirmed_one_month_flipbacks = 0
    for index, result in enumerate(history):
        state = result.observed_state
        phase = state["phase"]
        if phase is not None:
            plotted = phase_from_coordinates(float(state["level"]), float(state["momentum"]))
            plotted_phase_mismatches += int(plotted != phase)
        if result.transition_monitor["status"] == "CONFIRMED" and index + 1 < len(history):
            next_phase = history[index + 1].observed_state["phase"]
            confirmed_one_month_flipbacks += int(
                next_phase == result.transition_monitor["anchor_phase"]
            )

    assert plotted_phase_mismatches == 0
    assert confirmed_one_month_flipbacks == 0
    assert sum(
        result.transition_monitor["status"] == "CONFIRMED" for result in history
    ) >= 1


def test_nber_reference_never_overrides_observed_phase() -> None:
    non_recession = build_observed_state_history(_literal_panel(nber_recession=0.0))
    recession = build_observed_state_history(_literal_panel(nber_recession=1.0))

    assert [result.observed_state["phase"] for result in recession] == [
        result.observed_state["phase"] for result in non_recession
    ]
    assert [result.transition_monitor["status"] for result in recession] == [
        result.transition_monitor["status"] for result in non_recession
    ]


def test_revision_sensitive_results_are_reported_without_replacing_pit_phase() -> None:
    pit_panel = _literal_panel()
    revised_panel = _literal_panel(tuple(-value for value in LITERAL_LEVELS))
    pit_history = build_observed_state_history(pit_panel)
    compared = build_observed_state_history(pit_panel, revised_panel=revised_panel)

    sensitive = [
        result
        for result in compared
        if result.observed_state["revision_sensitivity"] == "SENSITIVE"
    ]

    assert sensitive
    assert [result.observed_state["phase"] for result in compared] == [
        result.observed_state["phase"] for result in pit_history
    ]
    assert all(
        result.observed_state["revised_phase"] != result.observed_state["phase"]
        for result in sensitive
    )
