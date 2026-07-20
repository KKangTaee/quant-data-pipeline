from __future__ import annotations

from app.services.overview.market_movers_read_model import (
    CANONICAL_SECTORS,
    canonical_sector,
    canonical_sector_options,
    filter_rows_by_canonical_sector,
)
from app.services.overview.market_movers_readiness import build_collection_readiness
from app.services.overview.market_movers_group_flow import (
    build_group_flow_state,
    build_market_cap_bellwethers,
    normalize_industry,
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


def test_market_cap_bellwethers_are_not_return_leaders() -> None:
    rows = [
        {
            "symbol": "BIG",
            "sector": "Technology",
            "return_pct": 1.0,
            "market_cap": 900,
            "asset_kind": "stock",
        },
        {
            "symbol": "MID",
            "sector": "Technology",
            "return_pct": 2.0,
            "market_cap": 500,
            "asset_kind": "stock",
        },
        {
            "symbol": "SMALL",
            "sector": "Technology",
            "return_pct": 12.0,
            "market_cap": 100,
            "asset_kind": "stock",
        },
        {
            "symbol": "ETF",
            "sector": "Technology",
            "return_pct": 3.0,
            "market_cap": 2_000,
            "asset_kind": "etf",
        },
    ]

    result = build_market_cap_bellwethers(rows, group_by="sector", top_n=3)

    assert [row["symbol"] for row in result["Technology"]["rows"]] == [
        "BIG",
        "MID",
        "SMALL",
    ]
    assert result["Technology"]["rows"][0]["rank"] == 1


def test_group_flow_labels_narrow_cap_led_rally() -> None:
    current = [
        {
            "group": "Technology",
            "symbols": 20,
            "positive_symbol_share": 35.0,
            "equal_weight_return": -0.2,
            "market_cap_weighted_return": 1.1,
        }
    ]
    previous = [
        {
            "Group": "Technology",
            "Positive Symbol Share %": 45.0,
            "Equal Weight Return %": 0.1,
            "Market Cap Weighted Return %": 0.4,
        }
    ]

    flow = build_group_flow_state(
        current_rows=current,
        previous_rows=previous,
        market_return_pct=0.5,
        group_by="sector",
    )

    assert flow[0]["state"] == "NARROW_CAP_LED"
    assert flow[0]["relative_strength_pp"] == 0.6
    assert flow[0]["breadth_change_pp"] == -10.0


def test_industry_normalization_uses_stable_display_keys() -> None:
    assert normalize_industry("  software   - infrastructure ") == "Software—Infrastructure"
    assert normalize_industry("SEMICONDUCTORS") == "Semiconductors"
    assert normalize_industry(None) == "Unknown"
