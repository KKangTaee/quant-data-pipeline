from __future__ import annotations

import pandas as pd

from finance.data.macro import DEFAULT_MACRO_SERIES, FRED_SERIES_CONFIG
from finance.loaders import economic_cycle_assets


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
