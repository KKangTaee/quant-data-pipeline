from __future__ import annotations

import importlib

import pandas as pd
import pytest

from finance.data.macro import DEFAULT_MACRO_SERIES, FRED_SERIES_CONFIG
from finance.loaders import economic_cycle_assets


def _daily_points(
    *, start: str, count: int, start_value: float, step: float
) -> list[dict[str, object]]:
    dates = pd.bdate_range(start=start, periods=count)
    return [
        {"date": timestamp.date(), "value": start_value + step * index}
        for index, timestamp in enumerate(dates)
    ]


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
        "series_ids": ("DGS2", "DGS10", "DFII10", "VIXCLS", "BAA10Y"),
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
