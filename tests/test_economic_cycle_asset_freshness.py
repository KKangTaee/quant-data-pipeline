from __future__ import annotations


def test_asset_freshness_separates_daily_business_age_and_weekly_calendar_age() -> None:
    from app.services.overview.economic_cycle_asset_freshness import (
        build_asset_pathway_freshness,
    )

    market_rows = [
        {"series_id": series_id, "observation_date": "2026-08-07", "value": 1.0}
        for series_id in (
            "DGS2",
            "DGS10",
            "DFII10",
            "T10YIE",
            "VIXCLS",
            "BAA10Y",
        )
    ] + [
        {"series_id": series_id, "observation_date": "2026-07-31", "value": 1.0}
        for series_id in ("WCESTUS1", "WCRFPUS2", "WRPUPUS2")
    ]
    price_rows = [
        {
            "provider_symbol": symbol,
            "candle_time_utc": "2026-08-07",
            "close": 100.0,
        }
        for symbol in ("GC=F", "DX-Y.NYB", "CL=F", "HG=F", "^GSPC", "SPY")
    ]

    result = build_asset_pathway_freshness(
        market_rows,
        price_rows,
        reference_date="2026-08-10",
    )

    assert result["status"] == "READY"
    assert result["refresh_required"] is False
    assert result["stale_series"] == []


def test_asset_freshness_reports_exact_stale_and_missing_series() -> None:
    from app.services.overview.economic_cycle_asset_freshness import (
        build_asset_pathway_freshness,
    )

    market_rows = [
        {"series_id": series_id, "observation_date": "2026-08-07", "value": 1.0}
        for series_id in ("DGS10", "T10YIE", "VIXCLS", "BAA10Y")
    ] + [
        {"series_id": "DGS2", "observation_date": "2026-07-27", "value": 1.0},
        {
            "series_id": "WCESTUS1",
            "observation_date": "2026-07-24",
            "value": 1.0,
        },
        {
            "series_id": "WCRFPUS2",
            "observation_date": "2026-07-31",
            "value": 1.0,
        },
        {
            "series_id": "WRPUPUS2",
            "observation_date": "2026-07-31",
            "value": 1.0,
        },
    ]
    price_rows = [
        {
            "provider_symbol": symbol,
            "candle_time_utc": "2026-08-07",
            "close": 100.0,
        }
        for symbol in ("GC=F", "DX-Y.NYB", "CL=F", "HG=F", "^GSPC", "SPY")
    ]

    result = build_asset_pathway_freshness(
        market_rows,
        price_rows,
        reference_date="2026-08-10",
    )

    assert result["status"] == "REFRESH_AVAILABLE"
    assert result["refresh_required"] is True
    assert result["stale_series"] == ["DGS2", "WCESTUS1"]
    assert result["missing_series"] == ["DFII10"]
