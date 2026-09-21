from datetime import datetime, timezone

import unittest

from app.services.backtest_price_refresh import build_backtest_price_refresh_plan


def assert_long_stale_prices_remain_collectable(stale_symbols):
    """A DB age heuristic must not prevent the first recovery collection."""
    plan = build_backtest_price_refresh_plan(
        {
            "tickers": ["QQQ", *stale_symbols],
            "start": "2016-01-01",
            "end": "2026-09-18",
            "price_freshness": {
                "status": "warning",
                "details": {
                    "common_latest_date": "2026-08-05",
                    "refresh_symbols_all": ["QQQ", *stale_symbols],
                    "classification_scope": "heuristic",
                    "classification_rows": [
                        {"symbol": "QQQ", "reason": "source_gap_or_symbol_issue"},
                        *[
                            {
                                "symbol": symbol,
                                "latest_date": "2026-08-05",
                                "lag_days": 44,
                                "profile_status": "active",
                                "reason": "persistent_source_gap_or_symbol_issue",
                            }
                            for symbol in stale_symbols
                        ],
                    ],
                },
            },
        },
        now=datetime(2026, 9, 21, tzinfo=timezone.utc),
        active_symbol_resolutions={},
    )

    assert plan["eligible"] is True
    assert plan["tickers"] == ["QQQ", *stale_symbols]
    assert plan["provider_gap_symbols"] == []
    assert plan["collection_start"] == "2026-08-06"
    assert plan["collection_end"] == "2026-09-18"


def assert_only_long_stale_prices_offer_recovery():
    plan = build_backtest_price_refresh_plan(
        {
            "tickers": ["IAU"],
            "end": "2026-09-18",
            "price_freshness": {
                "details": {
                    "common_latest_date": "2026-08-05",
                    "refresh_symbols_all": ["IAU"],
                    "classification_rows": [
                        {
                            "symbol": "IAU",
                            "reason": "persistent_source_gap_or_symbol_issue",
                        }
                    ],
                }
            },
        },
        now=datetime(2026, 9, 21, tzinfo=timezone.utc),
        active_symbol_resolutions={},
    )

    assert plan["status"] == "refresh_available"
    assert plan["eligible"] is True
    assert plan["tickers"] == ["IAU"]


class BacktestPriceRefreshRegressionTests(unittest.TestCase):
    def test_long_stale_prices_remain_collectable(self):
        for symbols in (["IAU", "IEF", "MTUM", "QUAL", "TLT", "USMV"], ["UNRELATED"]):
            with self.subTest(symbols=symbols):
                assert_long_stale_prices_remain_collectable(symbols)

    def test_only_long_stale_prices_offer_recovery(self):
        assert_only_long_stale_prices_offer_recovery()
