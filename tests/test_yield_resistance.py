from __future__ import annotations

import math


def test_pivot_is_unknown_until_right_hand_confirmation_date() -> None:
    from finance.yield_resistance import detect_confirmed_pivots

    observations = [
        {"observation_date": f"2026-01-0{index + 1}", "value": value}
        for index, value in enumerate((4.0, 4.2, 4.7, 4.3, 4.1))
    ]

    before = detect_confirmed_pivots(
        observations,
        left_days=2,
        right_days=2,
        as_of_date="2026-01-04",
    )
    after = detect_confirmed_pivots(
        observations,
        left_days=2,
        right_days=2,
        as_of_date="2026-01-05",
    )

    assert before == ()
    assert len(after) == 1
    assert after[0].pivot_date == "2026-01-03"
    assert after[0].known_at_date == "2026-01-05"
    assert after[0].value_pct == 4.7


def test_close_pivots_cluster_into_a_dynamic_zone_with_timeframe_confluence() -> None:
    from finance.yield_resistance import ConfirmedPivot, cluster_resistance_zones

    pivots = (
        ConfirmedPivot("2026-01-03", "2026-01-05", 4.68, 63),
        ConfirmedPivot("2025-10-10", "2025-10-14", 4.71, 252),
        ConfirmedPivot("2025-04-02", "2025-04-04", 4.69, 504),
        ConfirmedPivot("2026-02-01", "2026-02-03", 4.30, 63),
    )

    zones = cluster_resistance_zones(
        pivots,
        tolerance_pct=0.05,
        as_of_date="2026-02-10",
    )

    assert len(zones) == 2
    strong = max(zones, key=lambda zone: zone.zone_strength)
    assert strong.zone_lower_pct == 4.68
    assert strong.zone_upper_pct == 4.71
    assert strong.timeframes == (63, 252, 504)
    assert strong.touch_count == 3
    assert strong.known_at_date == "2026-01-05"


def test_same_pivot_seen_in_multiple_lookbacks_is_one_touch() -> None:
    from finance.yield_resistance import ConfirmedPivot, cluster_resistance_zones

    repeated = (
        ConfirmedPivot("2026-01-03", "2026-01-05", 4.70, 63),
        ConfirmedPivot("2026-01-03", "2026-01-05", 4.70, 252),
        ConfirmedPivot("2026-01-03", "2026-01-05", 4.70, 504),
    )

    zone = cluster_resistance_zones(
        repeated,
        tolerance_pct=0.05,
        as_of_date="2026-01-10",
    )[0]

    assert zone.touch_count == 1
    assert zone.timeframes == (63, 252, 504)


def test_incomplete_history_does_not_claim_long_lookback_confluence() -> None:
    from finance.yield_resistance import build_dynamic_resistance_zones

    observations = [
        {"observation_date": f"2026-07-{index + 1:02d}", "value": value}
        for index, value in enumerate(
            (4.10, 4.20, 4.35, 4.55, 4.30, 4.18, 4.25, 4.40, 4.60, 4.42, 4.30)
        )
    ]

    assert build_dynamic_resistance_zones(
        observations,
        as_of_date="2026-07-11",
    ) == ()


def test_resistance_state_requires_confirmation_and_preserves_failure() -> None:
    from finance.yield_resistance import classify_resistance_state

    assert (
        classify_resistance_state(
            (4.64, 4.68),
            zone_lower_pct=4.70,
            zone_upper_pct=4.72,
            buffer_pct=0.03,
        )
        == "APPROACH"
    )
    assert (
        classify_resistance_state(
            (4.70, 4.73, 4.74, 4.71, 4.73),
            zone_lower_pct=4.70,
            zone_upper_pct=4.72,
            buffer_pct=0.0,
        )
        == "CONFIRMED"
    )
    assert (
        classify_resistance_state(
            (4.75, 4.74, 4.73, 4.74, 4.76),
            zone_lower_pct=4.70,
            zone_upper_pct=4.72,
            buffer_pct=0.0,
            prior_state="CONFIRMED",
            hold_days=3,
        )
        == "HOLD"
    )
    assert (
        classify_resistance_state(
            (4.74, 4.71, 4.65),
            zone_lower_pct=4.70,
            zone_upper_pct=4.72,
            buffer_pct=0.03,
            prior_state="ATTEMPT",
        )
        == "FAILED"
    )


def test_resistance_state_replay_reconstructs_hold_and_failure() -> None:
    from finance.yield_resistance import replay_resistance_state

    observations = [
        {"observation_date": f"2026-07-{index + 1:02d}", "value": value}
        for index, value in enumerate((4.70, 4.73, 4.74, 4.75, 4.76, 4.65))
    ]

    assert replay_resistance_state(
        observations[:-1],
        zone_lower_pct=4.70,
        zone_upper_pct=4.72,
        buffer_pct=0.0,
        known_at_date="2026-07-01",
        hold_days=3,
    ) == "HOLD"
    assert replay_resistance_state(
        observations,
        zone_lower_pct=4.70,
        zone_upper_pct=4.72,
        buffer_pct=0.0,
        known_at_date="2026-07-01",
        hold_days=3,
    ) == "FAILED"


def test_driver_decomposition_keeps_two_lenses_separate() -> None:
    from finance.yield_resistance import decompose_yield_driver

    result = decompose_yield_driver(
        nominal_10y_change_bp=20.0,
        two_year_change_bp=8.0,
        real_10y_change_bp=4.0,
        breakeven_10y_change_bp=15.0,
        term_premium_change_bp=3.0,
    )

    assert result.dominant_driver == "inflation_driven"
    assert result.real_inflation_lens == {
        "real_10y_change_bp": 4.0,
        "breakeven_10y_change_bp": 15.0,
        "identity_gap_bp": 1.0,
    }
    assert result.policy_term_lens == {
        "two_year_policy_proxy_change_bp": 8.0,
        "term_premium_change_bp": 3.0,
    }
    assert math.isclose(
        result.real_inflation_lens["real_10y_change_bp"]
        + result.real_inflation_lens["breakeven_10y_change_bp"]
        + result.real_inflation_lens["identity_gap_bp"],
        20.0,
    )


def test_ten_year_breakout_alone_never_confirms_inflation() -> None:
    from finance.yield_resistance import evaluate_inflation_confirmation

    unconfirmed = evaluate_inflation_confirmation(
        resistance_state="CONFIRMED",
        dominant_driver="real_growth_driven",
        breakeven_confirmed=False,
        reacceleration_probability_before=0.20,
        reacceleration_probability_after=0.20,
        term_premium_only=False,
    )
    confirmed = evaluate_inflation_confirmation(
        resistance_state="HOLD",
        dominant_driver="inflation_driven",
        breakeven_confirmed=True,
        reacceleration_probability_before=0.20,
        reacceleration_probability_after=0.45,
        term_premium_only=False,
    )

    assert unconfirmed == "UNCONFIRMED"
    assert confirmed == "INFLATION_CONFIRMED"
