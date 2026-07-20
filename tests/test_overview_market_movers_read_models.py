from __future__ import annotations

from app.services.overview.market_movers_read_model import (
    CANONICAL_SECTORS,
    canonical_sector,
    canonical_sector_options,
    filter_rows_by_canonical_sector,
)
from app.services.overview.market_movers_readiness import build_collection_readiness


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


def test_partial_readiness_keeps_metric_denominators_explicit() -> None:
    readiness = build_collection_readiness(
        universe_count=4,
        returnable_count=3,
        volume_count=2,
        market_cap_count=2,
        missing_rows=[
            {"symbol": "D", "reason": "missing end price", "gap_code": "MISSING_QUOTE"}
        ],
        basis="EOD",
        effective_end_date="2026-07-17",
        stale_days=0,
    )

    assert readiness["state"] == "PARTIAL"
    assert readiness["metrics"]["return"]["valid"] == 3
    assert readiness["metrics"]["volume"]["valid"] == 2
    assert readiness["metrics"]["market_cap"]["excluded"] == 2
    assert readiness["gap_summary"] == [{"code": "MISSING_QUOTE", "count": 1}]


def test_blocked_readiness_does_not_publish_a_false_empty_ranking() -> None:
    readiness = build_collection_readiness(
        universe_count=0,
        returnable_count=0,
        volume_count=0,
        market_cap_count=0,
        missing_rows=[],
        basis=None,
        effective_end_date=None,
        stale_days=None,
    )

    assert readiness["state"] == "BLOCKED"
    assert readiness["primary_action"] == "UNIVERSE_SETUP"
    assert readiness["publish_results"] is False
