from __future__ import annotations

import importlib
import importlib.util
import math
from datetime import date

import pandas as pd

from finance.economic_cycle_catalog import IndicatorSpec, get_economic_cycle_catalog


def _load_module():
    spec = importlib.util.find_spec("finance.economic_cycle_features")
    assert spec is not None, "economic cycle feature module must exist"
    return importlib.import_module("finance.economic_cycle_features")


def _spec(transform: str, *, direction: int = 1, aggregation: str = "month_end"):
    return IndicatorSpec(
        series_id="TEST",
        factor="activity",
        role="phase_forecast",
        frequency="monthly",
        aggregation=aggregation,
        transform=transform,
        direction=direction,
        minimum_history_months=1,
    )


def test_exact_monthly_aggregations_and_catalog_transforms() -> None:
    module = _load_module()
    observations = pd.DataFrame(
        {
            "observation_date": pd.to_datetime(
                ["2020-01-05", "2020-01-25", "2020-02-10"]
            ),
            "value": [1.0, 3.0, 5.0],
        }
    )

    monthly_mean = module.aggregate_observations_monthly(
        observations, aggregation="monthly_mean"
    )
    month_end = module.aggregate_observations_monthly(
        observations, aggregation="month_end"
    )
    assert monthly_mean.tolist() == [2.0, 5.0]
    assert month_end.tolist() == [3.0, 5.0]

    six_months = pd.Series(
        [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 110.0],
        index=pd.period_range("2020-01", periods=7, freq="M"),
    )
    four_months = pd.Series(
        [100.0, 101.0, 102.0, 108.0],
        index=pd.period_range("2020-01", periods=4, freq="M"),
    )

    assert math.isclose(
        module.transform_monthly_signal(
            _spec("annualized_log_change_6m"), six_months
        ),
        21.0,
        rel_tol=1e-9,
    )
    assert math.isclose(
        module.transform_monthly_signal(
            _spec("annualized_log_change_3m"), four_months
        ),
        ((1.08**4) - 1.0) * 100.0,
        rel_tol=1e-9,
    )
    assert module.transform_monthly_signal(
        _spec("mean_level_3m"), four_months
    ) == (101.0 + 102.0 + 108.0) / 3.0
    assert module.transform_monthly_signal(
        _spec("level_change_3m", direction=-1), four_months
    ) == -8.0
    assert math.isclose(
        module.transform_monthly_signal(
            _spec("log_change_3m", direction=-1), four_months
        ),
        -math.log(1.08) * 100.0,
        rel_tol=1e-9,
    )
    cli = pd.Series(
        [99.0, 99.2, 99.4, 100.0],
        index=pd.period_range("2020-01", periods=4, freq="M"),
    )
    assert module.transform_monthly_signal(_spec("cli_gap_and_change_3m"), cli) == 1.0
    assert module.transform_monthly_signal(
        _spec("level", direction=-1), four_months
    ) == -108.0
    assert module.transform_monthly_signal(
        _spec("level_minus_2"), pd.Series([2.5], index=[pd.Period("2020-01")])
    ) == 0.5
    assert math.isclose(
        module.transform_monthly_signal(
            _spec("annualized_log_change_3m_minus_2"), four_months
        ),
        ((1.08**4) - 1.0) * 100.0 - 2.0,
        rel_tol=1e-9,
    )


def test_expanding_scale_is_unchanged_when_future_extreme_is_appended() -> None:
    module = _load_module()
    values = [float(index + (index % 5)) for index in range(70)]

    before = module.fit_expanding_robust_scale(values, minimum_history=10)
    after = module.fit_expanding_robust_scale(
        [*values, 1_000_000.0], minimum_history=10
    )

    assert before == after[:-1]


def test_expanding_scale_requires_warmup_and_clamps_extremes() -> None:
    module = _load_module()
    values = [float(index) for index in range(60)] + [1_000_000.0]

    scaled = module.fit_expanding_robust_scale(values, minimum_history=60)

    assert all(value is None for value in scaled[:59])
    assert scaled[59] is not None
    assert scaled[-1] == 4.0


def test_factor_scores_require_two_indicators_and_75_percent_coverage() -> None:
    module = _load_module()
    modeled = [
        item for item in get_economic_cycle_catalog() if item.role != "label_anchor"
    ]
    complete = {f"{item.series_id}_z": 1.0 for item in modeled}
    complete.update({f"{item.series_id}_stale": False for item in modeled})

    ready = module.calculate_factor_scores(pd.DataFrame([complete]))
    assert ready.loc[0, "data_quality_status"] == "READY"
    assert ready.loc[0, "overall_coverage"] == 1.0

    thin_activity = dict(complete)
    for item in modeled:
        if item.factor == "activity" and item.series_id != "INDPRO":
            thin_activity[f"{item.series_id}_z"] = None
    limited = module.calculate_factor_scores(pd.DataFrame([thin_activity]))
    assert pd.isna(limited.loc[0, "activity_score"])
    assert limited.loc[0, "data_quality_status"] == "LIMITED"

    below_threshold = dict(complete)
    for item in modeled[-5:]:
        below_threshold[f"{item.series_id}_z"] = None
    coverage_limited = module.calculate_factor_scores(pd.DataFrame([below_threshold]))
    assert coverage_limited.loc[0, "overall_coverage"] == 11 / 16
    assert coverage_limited.loc[0, "data_quality_status"] == "LIMITED"


def test_staleness_thresholds_are_frequency_aware() -> None:
    module = _load_module()
    origin = date(2026, 7, 31)
    catalog = {item.series_id: item for item in get_economic_cycle_catalog()}

    assert not module.is_series_stale(catalog["T10Y3M"], date(2026, 6, 16), origin)
    assert module.is_series_stale(catalog["T10Y3M"], date(2026, 6, 15), origin)
    assert not module.is_series_stale(catalog["ICSA"], date(2026, 6, 16), origin)
    assert not module.is_series_stale(catalog["PAYEMS"], date(2026, 5, 17), origin)
    assert module.is_series_stale(catalog["PAYEMS"], date(2026, 5, 16), origin)
    assert not module.is_series_stale(catalog["CFNAI"], date(2026, 4, 22), origin)
    assert module.is_series_stale(catalog["CFNAI"], date(2026, 4, 21), origin)
