from __future__ import annotations

import math

import pytest


def _paths():
    from finance.inflation_policy_simulation import SimulationPath

    return (
        SimulationPath(
            path_id="slow-hold",
            weight=0.25,
            q4_core_pce_pct=3.1,
            remaining_monthly_mom_pct=(0.2, 0.2, 0.2),
            policy_net_steps=0,
            year_end_policy_midpoint_pct=3.625,
            rate_paths_pct={"DGS10": (4.45, 4.55, 4.60, 4.62, 4.61)},
        ),
        SimulationPath(
            path_id="sticky-one",
            weight=0.25,
            q4_core_pce_pct=3.5,
            remaining_monthly_mom_pct=(0.3, 0.3, 0.3),
            policy_net_steps=1,
            year_end_policy_midpoint_pct=3.875,
            rate_paths_pct={"DGS10": (4.55, 4.68, 4.73, 4.74, 4.75)},
        ),
        SimulationPath(
            path_id="hot-two",
            weight=0.35,
            q4_core_pce_pct=3.8,
            remaining_monthly_mom_pct=(0.5, 0.4, 0.4),
            policy_net_steps=2,
            year_end_policy_midpoint_pct=4.125,
            rate_paths_pct={"DGS10": (4.60, 4.72, 4.74, 4.76, 4.78)},
        ),
        SimulationPath(
            path_id="term-premium",
            weight=0.15,
            q4_core_pce_pct=3.2,
            remaining_monthly_mom_pct=(0.2, 0.2, 0.2),
            policy_net_steps=0,
            year_end_policy_midpoint_pct=3.625,
            rate_paths_pct={"DGS10": (4.65, 4.71, 4.73, 4.70, 4.69)},
        ),
    )


def test_rate_path_combines_two_lenses_without_25bp_mechanical_mapping() -> None:
    from finance.inflation_policy_simulation import compose_rate_path

    projection = compose_rate_path(
        expected_two_year_path_pct=(3.70, 3.90),
        expected_short_rate_path_pct=(3.60, 3.80),
        term_premium_path_pct=(0.50, 0.55),
        real_10y_path_pct=(1.80, 1.85),
        breakeven_10y_path_pct=(2.20, 2.30),
        policy_term_weight=0.4,
        real_inflation_weight=0.6,
    )

    assert projection.two_year_path_pct == (3.70, 3.90)
    assert projection.ten_year_policy_term_lens_pct == (4.10, 4.35)
    assert projection.ten_year_real_inflation_lens_pct == (4.0, 4.15)
    assert projection.ten_year_path_pct == (4.04, 4.23)
    assert not math.isclose(
        projection.ten_year_path_pct[-1] - projection.ten_year_path_pct[0],
        0.25,
    )


def test_forward_target_probability_uses_path_weights() -> None:
    from finance.inflation_policy_simulation import (
        RateTargetCondition,
        calculate_target_probability,
    )

    condition = RateTargetCondition(
        instrument="DGS10",
        zone_lower_pct=4.70,
        zone_upper_pct=4.72,
        condition="BREAK",
        buffer_pct=0.0,
        hold_days=3,
    )

    assert math.isclose(calculate_target_probability(_paths(), condition), 0.60)


def test_reverse_conditioning_reports_distributions_not_one_required_path() -> None:
    from finance.inflation_policy_simulation import (
        RateTargetCondition,
        condition_paths_on_target,
    )

    result = condition_paths_on_target(
        _paths(),
        RateTargetCondition(
            instrument="DGS10",
            zone_lower_pct=4.70,
            zone_upper_pct=4.72,
            condition="REACH",
            buffer_pct=0.0,
            hold_days=3,
        ),
        minimum_supporting_paths=2,
        minimum_effective_paths=1.5,
    )

    assert result.status == "AVAILABLE"
    assert result.supporting_path_count == 3
    assert result.policy_net_step_probabilities == pytest.approx(
        {
            "hold": 0.2,
            "hike_1": 1 / 3,
            "hike_2": 7 / 15,
        }
    )
    assert result.q4_core_pce_quantiles_pct is not None
    assert result.required_remaining_mom_quantiles_pct is not None
    assert result.q4_core_pce_quantiles_pct["p20"] < result.q4_core_pce_quantiles_pct["p80"]


def test_reverse_conditioning_refuses_sparse_target_support() -> None:
    from finance.inflation_policy_simulation import (
        RateTargetCondition,
        condition_paths_on_target,
    )

    result = condition_paths_on_target(
        _paths(),
        RateTargetCondition(
            instrument="DGS10",
            zone_lower_pct=4.90,
            zone_upper_pct=4.95,
            condition="REACH",
            buffer_pct=0.0,
            hold_days=3,
        ),
        minimum_supporting_paths=2,
        minimum_effective_paths=1.5,
    )

    assert result.status == "NOT_AVAILABLE"
    assert result.target_probability == 0.0
    assert result.policy_net_step_probabilities is None


def test_next_pce_scenario_reweights_target_posterior_instead_of_triggering_boolean() -> None:
    from finance.inflation_policy_simulation import (
        RateTargetCondition,
        posterior_target_probability_for_next_pce,
    )

    condition = RateTargetCondition(
        instrument="DGS10",
        zone_lower_pct=4.70,
        zone_upper_pct=4.72,
        condition="REACH",
        buffer_pct=0.0,
        hold_days=3,
    )
    cool = posterior_target_probability_for_next_pce(
        _paths(), condition, observed_mom_pct=0.2, observation_noise_pct=0.08
    )
    hot = posterior_target_probability_for_next_pce(
        _paths(), condition, observed_mom_pct=0.5, observation_noise_pct=0.08
    )

    assert 0.0 < cool < hot < 1.0


def test_next_pce_scenario_reweights_policy_hike_probability_from_joint_paths() -> None:
    from finance.inflation_policy_simulation import (
        posterior_policy_hike_probability_for_next_pce,
    )

    cool = posterior_policy_hike_probability_for_next_pce(
        _paths(), observed_mom_pct=0.2, observation_noise_pct=0.08
    )
    hot = posterior_policy_hike_probability_for_next_pce(
        _paths(), observed_mom_pct=0.5, observation_noise_pct=0.08
    )

    assert 0.0 < cool < hot < 1.0
