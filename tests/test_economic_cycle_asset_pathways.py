from __future__ import annotations

from finance.data.macro import DEFAULT_MACRO_SERIES, FRED_SERIES_CONFIG


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
