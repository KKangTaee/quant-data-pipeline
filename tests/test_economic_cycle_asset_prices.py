from __future__ import annotations

import importlib
import importlib.util


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


def test_asset_price_loader_reads_only_bounded_stored_daily_rows() -> None:
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
        lookback_rows=80,
        query_fn=fake_query,
    )

    assert {row["provider_symbol"] for row in rows} == {"GC=F", "DX-Y.NYB"}
    assert captured["database"] == "finance_price"
    assert "FROM futures_ohlcv" in str(captured["sql"])
    assert "interval_code = '1d'" in str(captured["sql"])
    assert captured["params"][-1] == 80
