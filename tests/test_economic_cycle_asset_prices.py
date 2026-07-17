from __future__ import annotations

import importlib
import importlib.util
from datetime import date

import pandas as pd
import pytest


def test_dollar_index_is_a_core_daily_futures_instrument() -> None:
    futures_market = importlib.import_module("finance.data.futures_market")

    assert "DX-Y.NYB" in futures_market.DEFAULT_CORE_FUTURES_SYMBOLS
    instrument = next(
        row
        for row in futures_market.DEFAULT_FUTURES_INSTRUMENTS
        if row["provider_symbol"] == "DX-Y.NYB"
    )
    assert instrument["exchange"] == "ICE"
    assert instrument["futures_group"] == "FX Futures"


def test_asset_price_loader_applies_reference_date_before_row_rank() -> None:
    spec = importlib.util.find_spec("finance.loaders.economic_cycle_assets")
    assert spec is not None
    loader = importlib.import_module("finance.loaders.economic_cycle_assets")
    captured: dict[str, object] = {}

    def fake_query(database: str, sql: str, params: tuple[object, ...]):
        captured.update(database=database, sql=sql, params=params)
        return [
            {
                "provider_symbol": "GC=F",
                "candle_time_utc": "2026-07-16 00:00:00",
                "close": 4004.4,
                "source": "yfinance",
            },
            {
                "provider_symbol": "DX-Y.NYB",
                "candle_time_utc": "2026-07-16 00:00:00",
                "close": 100.57,
                "source": "yfinance",
            },
        ]

    rows = loader.load_economic_cycle_asset_prices(
        symbols=("GC=F", "DX-Y.NYB"),
        lookback_rows=1500,
        end_date="2026-07-17",
        query_fn=fake_query,
    )

    assert {row["provider_symbol"] for row in rows} == {"GC=F", "DX-Y.NYB"}
    assert captured["database"] == "finance_price"
    assert "FROM futures_ohlcv" in str(captured["sql"])
    assert "interval_code = '1d'" in str(captured["sql"])
    assert "candle_time_utc < DATE_ADD(%s, INTERVAL 1 DAY)" in str(
        captured["sql"]
    )
    assert captured["params"][-2:] == ("2026-07-17", 1500)


def _price_rows(
    symbol: str,
    *,
    direction: str,
    end_date: date,
    count: int = 1400,
) -> list[dict[str, object]]:
    dates = pd.bdate_range(end=end_date, periods=count)
    multiplier = 1.001 if direction == "UP" else 0.999
    return [
        {
            "provider_symbol": symbol,
            "candle_time_utc": timestamp.date(),
            "close": 100.0 * (multiplier**index),
            "source": "yfinance",
            "provider_status": "ok",
        }
        for index, timestamp in enumerate(dates)
    ]


def _market_rows(end_date: date) -> list[dict[str, object]]:
    dates = pd.bdate_range(end=end_date, periods=1400)
    directions = {
        "DGS2": "UP",
        "DGS10": "UP",
        "DFII10": "UP",
        "VIXCLS": "DOWN",
        "BAA10Y": "DOWN",
    }
    rows: list[dict[str, object]] = []
    for series_id, direction in directions.items():
        for index, timestamp in enumerate(dates):
            if series_id == "VIXCLS":
                multiplier = 1.001 if direction == "UP" else 0.999
                value = 20.0 * (multiplier**index)
            else:
                step = 0.001 if direction == "UP" else -0.001
                value = 5.0 + step * index
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": timestamp.date(),
                    "value": value,
                }
            )
    return rows


def _recovery_horizons() -> list[dict[str, object]]:
    return [
        {"horizon_months": 0, "dominant_phase": "recovery"},
        {"horizon_months": 1, "dominant_phase": "recovery"},
        {"horizon_months": 2, "dominant_phase": "recovery"},
    ]


def _actual_evidence() -> list[dict[str, object]]:
    return [
        {"factor": "activity_score", "value": -0.82},
        {"factor": "labor_income_score", "value": -0.44},
        {"factor": "financial_leading_score", "value": 0.22},
        {"factor": "inflation_policy_score", "value": 0.79},
    ]


def test_gold_and_dollar_expose_measured_pathways_without_alignment_claims() -> None:
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    end = date(2026, 7, 16)
    price_rows = [
        *_price_rows("GC=F", direction="DOWN", end_date=end),
        *_price_rows("DX-Y.NYB", direction="UP", end_date=end),
    ]

    implications = interpretation.build_market_implications(
        _recovery_horizons(),
        _actual_evidence(),
        price_rows,
        market_rows=_market_rows(end),
        price_reference_date=date(2026, 7, 17),
    )

    assert [row["asset_group"] for row in implications] == [
        "rates",
        "equities",
        "gold",
        "dollar",
        "commodities",
    ]
    gold = implications[2]
    dollar = implications[3]
    assert gold["price_context"]["status"] == "FALLING"
    assert dollar["price_context"]["status"] == "RISING"
    assert dollar["price_context"]["as_of_date"] == "2026-07-16"
    assert gold["coverage"] == "SUFFICIENT"
    assert dollar["coverage"] == "PARTIAL"
    for item in (gold, dollar):
        assert "assessment" not in item
        assert "alignment" not in item
        assert "macro_signal_label" not in item
        assert item["is_directional_forecast"] is False


@pytest.mark.parametrize(
    ("row_count", "latest_date", "expected_reason"),
    [
        (314, date(2026, 7, 16), "INSUFFICIENT_HISTORY"),
        (400, date(2026, 7, 9), "STALE_SERIES"),
    ],
)
def test_asset_price_confirmation_stays_unavailable_for_short_or_stale_history(
    row_count: int,
    latest_date: date,
    expected_reason: str,
) -> None:
    interpretation = importlib.import_module("finance.economic_cycle_interpretation")
    rows = _price_rows(
        "GC=F",
        direction="DOWN",
        end_date=latest_date,
        count=row_count,
    )

    gold = interpretation.build_market_implications(
        _recovery_horizons(),
        _actual_evidence(),
        rows,
        price_reference_date=date(2026, 7, 17),
    )[2]

    assert gold["price_context"]["status"] == "UNAVAILABLE"
    assert gold["price_context"]["reason_code"] == expected_reason
    assert "alignment" not in gold
