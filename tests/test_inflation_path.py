from __future__ import annotations

import math


def test_q4_over_q4_uses_quarterly_index_means() -> None:
    from finance.inflation_path import calculate_q4_over_q4

    levels = {
        "2025-10-01": 100.0,
        "2025-11-01": 101.0,
        "2025-12-01": 102.0,
        "2026-10-01": 103.0,
        "2026-11-01": 104.0,
        "2026-12-01": 105.0,
    }

    assert math.isclose(
        calculate_q4_over_q4(levels, year=2026),
        (104.0 / 101.0 - 1.0) * 100.0,
        abs_tol=1e-12,
    )


def test_required_remaining_mom_solves_the_index_path_not_a_sum() -> None:
    from finance.inflation_path import required_constant_mom_for_q4_target

    levels = {
        "2025-10-01": 100.0,
        "2025-11-01": 100.0,
        "2025-12-01": 100.0,
        "2026-06-01": 102.0,
    }
    target = (
        (
            102.0 * 1.0025**4
            + 102.0 * 1.0025**5
            + 102.0 * 1.0025**6
        )
        / 3.0
        / 100.0
        - 1.0
    ) * 100.0

    solved = required_constant_mom_for_q4_target(
        levels,
        forecast_months=(
            "2026-07-01",
            "2026-08-01",
            "2026-09-01",
            "2026-10-01",
            "2026-11-01",
            "2026-12-01",
        ),
        target_q4_over_q4=target,
    )

    assert math.isclose(solved, 0.25, abs_tol=1e-8)


def test_state_definition_is_versioned_from_sep_distribution_and_error() -> None:
    from finance.inflation_path import derive_state_definition

    rows = [
        {
            "released_at": "2026-06-17 18:00:00",
            "target_period": "2026",
            "variable_name": "core_pce",
            "distribution_kind": "HISTOGRAM",
            "bin_lower_pct": 2.5,
            "bin_upper_pct": 2.6,
            "participant_count": 1,
        },
        {
            "released_at": "2026-06-17 18:00:00",
            "target_period": "2026",
            "variable_name": "core_pce",
            "distribution_kind": "HISTOGRAM",
            "bin_lower_pct": 3.1,
            "bin_upper_pct": 3.2,
            "participant_count": 3,
        },
        {
            "released_at": "2026-06-17 18:00:00",
            "target_period": "2026",
            "variable_name": "core_pce",
            "distribution_kind": "HISTOGRAM",
            "bin_lower_pct": 3.3,
            "bin_upper_pct": 3.4,
            "participant_count": 10,
        },
        {
            "released_at": "2026-06-17 18:00:00",
            "target_period": "2026",
            "variable_name": "core_pce",
            "distribution_kind": "HISTOGRAM",
            "bin_lower_pct": 3.5,
            "bin_upper_pct": 3.6,
            "participant_count": 4,
        },
    ]

    definition = derive_state_definition(
        rows,
        target_period="2026",
        forecast_error_pct=0.20,
        price_stability_target_pct=2.0,
    )

    assert definition.sep_center_pct == 3.35
    assert definition.boundaries_pct == (2.95, 3.15, 3.55, 3.95)
    assert definition.definition_version.startswith("sep-20260617-")


def test_state_definition_remains_ordered_when_sep_is_near_or_below_target() -> None:
    from finance.inflation_path import derive_state_definition

    def definition_for(center: float):
        return derive_state_definition(
            (
                {
                    "released_at": "2026-06-17 18:00:00",
                    "target_period": "2026",
                    "variable_name": "core_pce",
                    "distribution_kind": "HISTOGRAM",
                    "bin_lower_pct": center - 0.05,
                    "bin_upper_pct": center + 0.05,
                    "participant_count": 18,
                },
            ),
            target_period="2026",
            forecast_error_pct=0.20,
            price_stability_target_pct=2.0,
        )

    near_target = definition_for(2.20)
    below_target = definition_for(1.80)

    assert near_target.boundaries_pct == (1.8, 2.0, 2.4, 2.8)
    assert below_target.boundaries_pct == (1.8, 2.0, 2.2, 2.6)
    assert all(
        left < right
        for definition in (near_target, below_target)
        for left, right in zip(
            definition.boundaries_pct,
            definition.boundaries_pct[1:],
        )
    )


def test_state_and_threshold_probabilities_are_complete_simplexes() -> None:
    from finance.inflation_path import (
        InflationStateDefinition,
        calculate_state_probabilities,
        calculate_threshold_probabilities,
    )

    definition = InflationStateDefinition(
        definition_version="fixture-v1",
        target_period="2026",
        sep_released_at="2026-06-17T18:00:00+00:00",
        sep_center_pct=3.35,
        forecast_error_pct=0.20,
        price_stability_target_pct=2.0,
        boundaries_pct=(2.95, 3.15, 3.55, 3.95),
    )
    samples = (2.8, 3.0, 3.4, 3.7, 4.1)

    states = calculate_state_probabilities(samples, definition)
    thresholds = calculate_threshold_probabilities(samples, (3.4, 3.5, 3.6))

    assert states == {
        "rapid_disinflation": 0.2,
        "gradual_disinflation": 0.2,
        "sticky": 0.2,
        "reacceleration": 0.2,
        "shock_reacceleration": 0.2,
    }
    assert math.isclose(sum(states.values()), 1.0, abs_tol=1e-12)
    assert thresholds == {"3.4000": 0.6, "3.5000": 0.4, "3.6000": 0.4}


def test_core_path_simulation_preserves_index_compounding_and_uncertainty_contract() -> None:
    from finance.inflation_path import (
        InflationStateDefinition,
        simulate_core_pce_paths,
    )

    definition = InflationStateDefinition(
        definition_version="fixture-v1",
        target_period="2026",
        sep_released_at="2026-06-17T18:00:00+00:00",
        sep_center_pct=3.35,
        forecast_error_pct=0.20,
        price_stability_target_pct=2.0,
        boundaries_pct=(2.95, 3.15, 3.55, 3.95),
    )
    levels = {
        "2025-10-01": 100.0,
        "2025-11-01": 100.0,
        "2025-12-01": 100.0,
        "2026-06-01": 102.0,
    }
    months = tuple(f"2026-{month:02d}-01" for month in range(7, 13))

    forecast = simulate_core_pce_paths(
        levels,
        forecast_months=months,
        component_monthly_mom_pct={
            "bridge": {month: 0.25 for month in months},
        },
        component_weights={"bridge": 1.0},
        residual_history_pct=(0.0,),
        sample_count=20,
        seed=7,
        state_definition=definition,
        thresholds_pct=(3.4, 3.5),
    )
    expected_q4 = (
        (
            102.0 * 1.0025**4
            + 102.0 * 1.0025**5
            + 102.0 * 1.0025**6
        )
        / 3.0
        / 100.0
        - 1.0
    ) * 100.0

    assert math.isclose(forecast.q4_quantiles_pct["p50"], expected_q4, abs_tol=1e-10)
    assert math.isclose(
        forecast.monthly_index_quantiles["2026-12-01"]["p50"],
        102.0 * 1.0025**6,
        abs_tol=1e-10,
    )
    assert math.isclose(sum(forecast.state_probabilities.values()), 1.0)
    assert forecast.component_weights == {"bridge": 1.0}


def test_next_release_scenario_fixes_the_assumed_print_before_future_residuals() -> None:
    from finance.inflation_path import (
        InflationStateDefinition,
        simulate_core_pce_paths,
    )

    definition = InflationStateDefinition(
        definition_version="fixture-v1",
        target_period="2026",
        sep_released_at="2026-06-17T18:00:00+00:00",
        sep_center_pct=3.35,
        forecast_error_pct=0.20,
        price_stability_target_pct=2.0,
        boundaries_pct=(2.95, 3.15, 3.55, 3.95),
    )
    months = tuple(f"2026-{month:02d}-01" for month in range(7, 13))

    forecast = simulate_core_pce_paths(
        {
            "2025-10-01": 100.0,
            "2025-11-01": 100.0,
            "2025-12-01": 100.0,
            "2026-06-01": 102.0,
        },
        forecast_months=months,
        component_monthly_mom_pct={
            "bridge": {month: 0.2 for month in months},
        },
        component_weights={"bridge": 1.0},
        residual_history_pct=(-0.1, 0.1),
        fixed_monthly_mom_pct={"2026-07-01": 0.4},
        sample_count=100,
        seed=7,
        state_definition=definition,
        thresholds_pct=(3.4,),
    )

    assert forecast.monthly_mom_quantiles_pct["2026-07-01"] == {
        "p05": 0.4,
        "p20": 0.4,
        "p50": 0.4,
        "p80": 0.4,
        "p95": 0.4,
    }
    assert forecast.monthly_mom_quantiles_pct["2026-08-01"]["p05"] < 0.2
    assert forecast.monthly_mom_quantiles_pct["2026-08-01"]["p95"] > 0.2


def test_core_path_simulation_requires_empirical_residual_evidence() -> None:
    import pytest
    from finance.inflation_path import (
        InflationStateDefinition,
        simulate_core_pce_paths,
    )

    definition = InflationStateDefinition(
        definition_version="fixture-v1",
        target_period="2026",
        sep_released_at="2026-06-17T18:00:00+00:00",
        sep_center_pct=3.35,
        forecast_error_pct=0.20,
        price_stability_target_pct=2.0,
        boundaries_pct=(2.95, 3.15, 3.55, 3.95),
    )

    with pytest.raises(ValueError, match="residual_history_pct"):
        simulate_core_pce_paths(
            {
                "2025-10-01": 100.0,
                "2025-11-01": 100.0,
                "2025-12-01": 100.0,
                "2026-11-01": 103.0,
            },
            forecast_months=("2026-12-01",),
            component_monthly_mom_pct={"bridge": {"2026-12-01": 0.2}},
            component_weights={"bridge": 1.0},
            residual_history_pct=(),
            sample_count=10,
            seed=1,
            state_definition=definition,
            thresholds_pct=(3.5,),
        )
