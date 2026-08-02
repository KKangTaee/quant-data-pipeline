from __future__ import annotations

import math

import pytest


def _empty_net_moves() -> dict[str, float]:
    return {
        "cut_3_plus": 0.0,
        "cut_2": 0.0,
        "cut_1": 0.0,
        "hold": 0.0,
        "hike_1": 0.0,
        "hike_2": 0.0,
        "hike_3_plus": 0.0,
    }


def test_sep_rate_dots_remain_an_anonymous_marginal_net_move_prior() -> None:
    from finance.policy_path import derive_sep_net_move_prior

    rows = [
        {
            "released_at": "2026-06-17 18:00:00",
            "target_period": "2026",
            "variable_name": "federal_funds_rate",
            "distribution_kind": "DOT",
            "bin_value_pct": value,
            "participant_count": count,
        }
        for value, count in (
            (3.375, 1),
            (3.625, 8),
            (3.875, 3),
            (4.125, 5),
            (4.375, 1),
        )
    ]

    prior = derive_sep_net_move_prior(
        rows,
        target_period="2026",
        current_midpoint_pct=3.625,
    )

    assert prior == {
        "cut_3_plus": 0.0,
        "cut_2": 0.0,
        "cut_1": 1 / 18,
        "hold": 8 / 18,
        "hike_1": 3 / 18,
        "hike_2": 5 / 18,
        "hike_3_plus": 1 / 18,
    }


def test_latest_vote_direction_is_a_next_meeting_prior_not_a_hawkish_score() -> None:
    from finance.policy_path import derive_decision_action_prior

    prior = derive_decision_action_prior(
        {
            "target_lower_before_pct": 3.5,
            "target_upper_before_pct": 3.75,
            "target_lower_after_pct": 3.5,
            "target_upper_after_pct": 3.75,
            "vote_for_count": 9,
            "vote_against_count": 3,
            "dissents_json": """[
              {"member_name":"A","preferred_action":"HIKE_25"},
              {"member_name":"B","preferred_action":"HIKE_25"},
              {"member_name":"C","preferred_action":"HIKE_25"}
            ]""",
        }
    )

    assert prior == {"cut": 0.0, "hold": 0.75, "hike": 0.25}


def test_inflation_reaction_matrix_does_not_turn_one_hot_shock_into_certain_hike() -> None:
    from finance.inflation_path import INFLATION_STATES
    from finance.policy_path import project_inflation_states_to_policy

    state_probabilities = {state: 0.0 for state in INFLATION_STATES}
    state_probabilities["shock_reacceleration"] = 1.0
    reaction_matrix = {
        state: {
            **_empty_net_moves(),
            "hold": 1.0,
        }
        for state in INFLATION_STATES
    }
    reaction_matrix["shock_reacceleration"] = {
        **_empty_net_moves(),
        "hold": 0.30,
        "hike_1": 0.45,
        "hike_2": 0.20,
        "hike_3_plus": 0.05,
    }

    projected = project_inflation_states_to_policy(
        state_probabilities,
        reaction_matrix=reaction_matrix,
    )

    assert projected["hold"] == 0.30
    assert math.isclose(
        projected["hike_1"] + projected["hike_2"] + projected["hike_3_plus"],
        0.70,
    )


def test_component_blend_excludes_missing_optional_prior_and_enforces_weight_cap() -> None:
    from finance.policy_path import blend_probability_components

    blended = blend_probability_components(
        {
            "economic": {"cut": 0.1, "hold": 0.7, "hike": 0.2},
            "committee": {"cut": 0.0, "hold": 0.75, "hike": 0.25},
            "market": None,
        },
        weights={"economic": 0.6, "committee": 0.3, "market": 0.1},
        labels=("cut", "hold", "hike"),
        max_component_weight=0.70,
    )
    assert blended == {
        "cut": pytest.approx(1 / 15),
        "hold": pytest.approx(43 / 60),
        "hike": pytest.approx(13 / 60),
    }

    with pytest.raises(ValueError, match="weight cap"):
        blend_probability_components(
            {
                "economic": {"cut": 0.1, "hold": 0.7, "hike": 0.2},
                "committee": {"cut": 0.0, "hold": 0.75, "hike": 0.25},
            },
            weights={"economic": 0.8, "committee": 0.2},
            labels=("cut", "hold", "hike"),
            max_component_weight=0.70,
        )


def test_policy_forecast_keeps_net_moves_and_target_bins_consistent() -> None:
    from finance.policy_path import build_policy_path_forecast

    sep = {**_empty_net_moves(), "hold": 0.5, "hike_1": 0.5}
    economic = {**_empty_net_moves(), "hold": 0.25, "hike_1": 0.75}
    forecast = build_policy_path_forecast(
        current_midpoint_pct=3.625,
        net_move_components={"sep": sep, "economic": economic},
        net_move_weights={"sep": 0.5, "economic": 0.5},
        next_action_components={
            "economic": {"cut": 0.0, "hold": 0.4, "hike": 0.6},
            "committee": {"cut": 0.0, "hold": 0.75, "hike": 0.25},
        },
        next_action_weights={"economic": 0.5, "committee": 0.5},
        max_component_weight=0.70,
    )

    assert forecast.net_move_probabilities["hold"] == 0.375
    assert forecast.net_move_probabilities["hike_1"] == 0.625
    assert forecast.year_end_target_probabilities == {
        "3.6250": 0.375,
        "3.8750": 0.625,
    }
    assert forecast.next_meeting_probabilities == {
        "cut": 0.0,
        "hold": 0.575,
        "hike": 0.425,
    }
    assert math.isclose(sum(forecast.year_end_target_probabilities.values()), 1.0)
