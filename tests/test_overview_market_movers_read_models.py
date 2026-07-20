from __future__ import annotations

from app.services.overview.market_movers_read_model import (
    CANONICAL_SECTORS,
    canonical_sector,
    canonical_sector_options,
    filter_rows_by_canonical_sector,
)


def test_canonical_sector_collapses_provider_aliases() -> None:
    assert canonical_sector("Financial Services") == "Financials"
    assert canonical_sector("Information Technology") == "Technology"
    assert canonical_sector("Consumer Cyclical") == "Consumer Discretionary"
    assert canonical_sector("Consumer Defensive") == "Consumer Staples"
    assert canonical_sector("Healthcare") == "Health Care"
    assert canonical_sector("Basic Materials") == "Materials"


def test_sector_options_expose_only_canonical_values() -> None:
    rows = [
        {"sector": "Financial Services"},
        {"sector": "Financials"},
        {"sector": "Technology"},
        {"sector": None},
    ]

    assert canonical_sector_options(rows) == ["All", "Financials", "Technology", "Unknown"]
    assert len(CANONICAL_SECTORS) == 11


def test_filter_uses_same_canonical_value_as_options() -> None:
    rows = [
        {"symbol": "A", "sector": "Financial Services"},
        {"symbol": "B", "sector": "Financials"},
        {"symbol": "C", "sector": "Technology"},
    ]

    filtered = filter_rows_by_canonical_sector(rows, "Financials")

    assert [row["symbol"] for row in filtered] == ["A", "B"]
    assert {row["sector"] for row in filtered} == {"Financials"}


def test_public_sector_options_use_canonical_taxonomy() -> None:
    from app.services.overview.market_movers import load_market_mover_sector_options

    def query_fn(db_name: str, sql: str, params=None):
        del db_name, sql, params
        return [
            {"symbol": "A", "sector": "Financial Services"},
            {"symbol": "B", "sector": "Financials"},
            {"symbol": "C", "sector": "Information Technology"},
        ]

    assert load_market_mover_sector_options(query_fn=query_fn) == [
        "All",
        "Financials",
        "Technology",
    ]
