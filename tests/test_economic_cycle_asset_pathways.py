from __future__ import annotations

import importlib

import pandas as pd
import pytest

from finance.data.macro import DEFAULT_MACRO_SERIES, FRED_SERIES_CONFIG
from finance.data.eia_petroleum import EIA_WEEKLY_PETROLEUM_SERIES
from finance.loaders import economic_cycle_assets


def _daily_points(
    *, start: str, count: int, start_value: float, step: float
) -> list[dict[str, object]]:
    dates = pd.bdate_range(start=start, periods=count)
    return [
        {"date": timestamp.date(), "value": start_value + step * index}
        for index, timestamp in enumerate(dates)
    ]


def _economic_evidence() -> list[dict[str, object]]:
    return [
        {
            "factor": "activity_score",
            "value": -0.8,
            "source_date": "2026-06-30",
        },
        {
            "factor": "labor_income_score",
            "value": -0.5,
            "source_date": "2026-06-30",
        },
        {
            "factor": "financial_leading_score",
            "value": 0.2,
            "source_date": "2026-06-30",
        },
        {
            "factor": "inflation_policy_score",
            "value": 0.7,
            "source_date": "2026-06-30",
        },
    ]


def _macro_history(directions: dict[str, str]) -> list[dict[str, object]]:
    dates = pd.bdate_range(start="2021-03-01", periods=1400)
    rows: list[dict[str, object]] = []
    for series_id, direction in directions.items():
        for index, timestamp in enumerate(dates):
            if series_id == "VIXCLS":
                daily_multiplier = 1.001 if direction == "UP" else 0.999
                value = 20.0 * (daily_multiplier**index)
            else:
                daily_step = 0.001 if direction == "UP" else -0.001
                value = 5.0 + daily_step * index
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": timestamp.date(),
                    "value": value,
                }
            )
    return rows


def _price_history(directions: dict[str, str]) -> list[dict[str, object]]:
    dates = pd.bdate_range(start="2021-03-01", periods=1400)
    rows: list[dict[str, object]] = []
    for symbol, direction in directions.items():
        daily_multiplier = 1.001 if direction == "UP" else 0.999
        rows.extend(
            {
                "provider_symbol": symbol,
                "candle_time_utc": timestamp.date(),
                "close": 100.0 * (daily_multiplier**index),
                "provider_status": "ok",
            }
            for index, timestamp in enumerate(dates)
        )
    return rows


def test_asset_pathway_fred_series_are_registered_for_default_collection() -> None:
    expected = {"DGS2", "DGS10", "DFII10"}

    assert expected.issubset(set(DEFAULT_MACRO_SERIES))
    assert FRED_SERIES_CONFIG["DGS2"] == {
        "series_name": (
            "Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity"
        ),
        "category": "treasury_yield",
        "frequency": "daily",
        "units": "percent",
    }
    assert FRED_SERIES_CONFIG["DGS10"]["category"] == "treasury_yield"
    assert FRED_SERIES_CONFIG["DFII10"]["category"] == "real_yield"


def test_rates_and_eia_series_catalogs_are_exact() -> None:
    assert "T10YIE" in DEFAULT_MACRO_SERIES
    assert FRED_SERIES_CONFIG["T10YIE"]["category"] == "inflation_expectation"
    assert set(EIA_WEEKLY_PETROLEUM_SERIES) == {
        "WCESTUS1",
        "WCRFPUS2",
        "WRPUPUS2",
    }


def test_market_series_loader_requests_only_the_pathway_window() -> None:
    captured: dict[str, object] = {}

    def fake_macro_loader(series_ids, *, start, end):
        captured.update(series_ids=tuple(series_ids), start=start, end=end)
        return pd.DataFrame(
            [
                {
                    "series_id": "DGS2",
                    "observation_date": "2026-07-16",
                    "value": 4.2,
                }
            ]
        )

    rows = economic_cycle_assets.load_economic_cycle_market_series(
        start_date="2021-03-01",
        end_date="2026-07-17",
        macro_loader=fake_macro_loader,
    )

    assert captured == {
        "series_ids": (
            "DGS2",
            "DGS10",
            "DFII10",
            "T10YIE",
            "VIXCLS",
            "BAA10Y",
            "WCESTUS1",
            "WCRFPUS2",
            "WRPUPUS2",
        ),
        "start": "2021-03-01",
        "end": "2026-07-17",
    }
    assert rows[0]["series_id"] == "DGS2"


def test_evaluate_series_uses_percent_and_basis_point_units() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    price = _daily_points(
        start="2021-03-01", count=1400, start_value=100.0, step=0.05
    )
    price = [
        {"date": row["date"], "value": 100.0 * (1.001**index)}
        for index, row in enumerate(price)
    ]
    rates = _daily_points(
        start="2021-03-01", count=1400, start_value=3.0, step=0.001
    )
    reference = price[-1]["date"]

    price_result = pathways.evaluate_series(
        price,
        series_id="DX-Y.NYB",
        reference_date=reference,
        change_mode="PERCENT_RETURN",
    )
    rate_result = pathways.evaluate_series(
        rates,
        series_id="DFII10",
        reference_date=reference,
        change_mode="BASIS_POINT",
    )

    assert price_result["unit"] == "percent"
    assert rate_result["unit"] == "bp"
    assert rate_result["changes"]["21d"] == pytest.approx(2.1)
    assert price_result["directions"]["21d"] == "UP"
    assert price_result["directions"]["63d"] == "UP"


def test_evaluate_series_reports_neutral_and_missing_reason() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")

    assert pathways._direction(0.4, threshold=0.5) == "NEUTRAL"
    assert pathways._direction(0.6, threshold=0.5) == "UP"
    result = pathways.evaluate_series(
        [],
        series_id="DGS2",
        reference_date="2026-07-17",
        change_mode="BASIS_POINT",
    )
    assert result["reason_code"] == "MISSING_SERIES"


@pytest.mark.parametrize(
    ("points", "reference_date", "expected_reason"),
    [
        (
            _daily_points(
                start="2025-01-01", count=314, start_value=3.0, step=0.001
            ),
            pd.bdate_range(start="2025-01-01", periods=314)[-1].date(),
            "INSUFFICIENT_HISTORY",
        ),
        (
            _daily_points(
                start="2024-12-18", count=400, start_value=3.0, step=0.001
            ),
            "2026-07-17",
            "STALE_SERIES",
        ),
    ],
)
def test_evaluate_series_rejects_short_or_stale_history(
    points: list[dict[str, object]],
    reference_date: object,
    expected_reason: str,
) -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")

    result = pathways.evaluate_series(
        points,
        series_id="DGS2",
        reference_date=reference_date,
        change_mode="BASIS_POINT",
    )

    assert result["reason_code"] == expected_reason
    assert result["directions"] == {
        "21d": "UNAVAILABLE",
        "63d": "UNAVAILABLE",
    }


def test_evaluate_series_keeps_small_flat_changes_neutral() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    points = _daily_points(
        start="2021-03-01", count=1400, start_value=3.0, step=0.0
    )

    result = pathways.evaluate_series(
        points,
        series_id="DFII10",
        reference_date=points[-1]["date"],
        change_mode="BASIS_POINT",
    )

    assert result["directions"] == {"21d": "NEUTRAL", "63d": "NEUTRAL"}


def test_evaluate_series_excludes_points_after_reference_date() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    points = _daily_points(
        start="2021-03-01", count=1401, start_value=3.0, step=0.001
    )
    points[-1]["value"] = 99.0
    reference = points[-2]["date"]

    result = pathways.evaluate_series(
        points,
        series_id="DGS10",
        reference_date=reference,
        change_mode="BASIS_POINT",
    )

    assert result["as_of_date"] == str(reference)
    assert result["changes"]["5d"] == pytest.approx(0.5)


def test_spread_uses_same_horizon_long_minus_short_changes() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    dgs10_points = _daily_points(
        start="2021-03-01", count=1400, start_value=3.0, step=0.002
    )
    dgs2_points = _daily_points(
        start="2021-03-01", count=1400, start_value=2.0, step=0.001
    )
    reference = dgs10_points[-1]["date"]

    spread = pathways.evaluate_spread(
        dgs10_points,
        dgs2_points,
        reference_date=reference,
    )

    assert spread["changes"]["21d"] > 0
    assert spread["structure_status"] == "STEEPENING"
    assert spread["current_level_bp"] > 0


def test_weekly_evaluator_separates_four_week_and_year_over_year() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    weekly_points = [
        {"date": timestamp.date(), "value": 400_000.0 + index * 100.0}
        for index, timestamp in enumerate(
            pd.date_range(end="2026-07-10", periods=260, freq="W-FRI")
        )
    ]

    result = pathways.evaluate_weekly_series(
        weekly_points,
        series_id="WCESTUS1",
        reference_date="2026-07-17",
    )

    assert set(result["changes"]) == {"4w", "52w"}
    assert result["freshness"] == "CURRENT"
    assert result["unit"] == "percent"


def test_observed_pathway_preserves_measurement_and_interpretation() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")
    evaluation = {
        "series_id": "DFII10",
        "as_of_date": "2026-07-16",
        "unit": "bp",
        "freshness": "CURRENT",
        "reason_code": None,
        "changes": {"5d": 2.0, "21d": 5.0, "63d": 8.0},
        "directions": {"21d": "UP", "63d": "UP"},
    }

    pathway = pathways.build_observed_pathway(
        "real_yield",
        "10년 실질금리",
        evaluation,
        interpretation="최근 1개월과 3개월 모두 상승했습니다.",
    )

    assert pathway["pathway_id"] == "real_yield"
    assert pathway["series"] == evaluation
    assert pathway["interpretation"].startswith("최근 1개월")


def test_gold_pathways_separate_real_yield_dollar_and_risk_directions() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")

    contexts = pathways.build_asset_pathway_contexts(
        evidence=_economic_evidence(),
        market_rows=_macro_history(
            {
                "DFII10": "UP",
                "DGS2": "UP",
                "VIXCLS": "DOWN",
                "BAA10Y": "DOWN",
            }
        ),
        price_rows=_price_history({"GC=F": "DOWN", "DX-Y.NYB": "UP"}),
        reference_date="2026-07-17",
    )

    gold = contexts["gold"]
    statuses = {row["pathway_id"]: row["status"] for row in gold["pathways"]}
    assert statuses == {
        "real_yield": "SUPPORTS_FALL",
        "dollar": "SUPPORTS_FALL",
        "short_rate": "SUPPORTS_FALL",
        "risk_aversion": "SUPPORTS_FALL",
    }
    assert gold["coverage"] == "SUFFICIENT"
    assert gold["price_context"]["status"] == "FALLING"
    assert "가격 원인을 확정" in gold["narrative"]
    assert {row["pathway_id"] for row in gold["unmeasured_pathways"]} == {
        "official_flows",
        "external_events",
    }


def test_dollar_is_partial_until_relative_rates_are_collected() -> None:
    pathways = importlib.import_module("finance.economic_cycle_asset_pathways")

    contexts = pathways.build_asset_pathway_contexts(
        evidence=_economic_evidence(),
        market_rows=_macro_history(
            {
                "DGS2": "UP",
                "DGS10": "UP",
                "DFII10": "UP",
                "VIXCLS": "UP",
                "BAA10Y": "UP",
            }
        ),
        price_rows=_price_history({"GC=F": "DOWN", "DX-Y.NYB": "UP"}),
        reference_date="2026-07-17",
    )

    dollar = contexts["dollar"]
    statuses = {
        row["pathway_id"]: row["status"] for row in dollar["pathways"]
    }
    assert statuses == {
        "us_nominal_yield": "SUPPORTS_RISE",
        "us_real_yield": "SUPPORTS_RISE",
        "risk_aversion": "SUPPORTS_RISE",
    }
    assert dollar["coverage"] == "PARTIAL"
    relative_rates = next(
        row
        for row in dollar["unmeasured_pathways"]
        if row["pathway_id"] == "relative_rates"
    )
    assert relative_rates["reason_code"] == "RELATIVE_RATE_NOT_COLLECTED"
    assert "해외 상대금리" in dollar["narrative"]
