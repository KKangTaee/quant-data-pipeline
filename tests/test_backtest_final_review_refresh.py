from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd


ET = ZoneInfo("America/New_York")


def source_fixture() -> dict[str, object]:
    return {
        "selection_source_id": "selection-grs-current",
        "source_kind": "single_candidate",
        "period": {"actual_start": "2016-01-29", "actual_end": "2026-06-26"},
        "components": [
            {
                "component_id": "grs",
                "title": "Global Relative Strength",
                "target_weight": 100.0,
                "strategy_key": "global_relative_strength",
                "contract": {
                    "tickers": ["SPY", "QQQ", "GLD", "IEF", "TLT"],
                    "cash_ticker": "BIL",
                },
            }
        ],
    }


def validation_fixture(*, curve_end: str = "2026-06-26") -> dict[str, object]:
    return {
        "validation_id": "validation-grs-current",
        "selection_source_id": "selection-grs-current",
        "selection_source_snapshot": source_fixture(),
        "validation_profile": {
            "profile_id": "balanced_core",
            "answers": {"capital_priority": "balanced"},
        },
        "curve_evidence": {
            "replay_attempt": {
                "portfolio_curve": [
                    {"Date": "2016-01-29", "Total Balance": 10000.0},
                    {"Date": curve_end, "Total Balance": 53000.0},
                ]
            }
        },
    }


def freshness_frame(bil: str, others: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"symbol": "SPY", "latest_date": others, "row_count": 2500},
            {"symbol": "QQQ", "latest_date": others, "row_count": 2500},
            {"symbol": "GLD", "latest_date": others, "row_count": 2500},
            {"symbol": "IEF", "latest_date": others, "row_count": 2500},
            {"symbol": "TLT", "latest_date": others, "row_count": 2500},
            {"symbol": "BIL", "latest_date": bil, "row_count": 2500},
        ]
    )


class FinalReviewRefreshStatusTests(unittest.TestCase):
    def test_current_grs_requires_price_refresh_and_names_bil_limiter(self) -> None:
        from app.services.backtest_final_review_refresh import (
            build_final_review_refresh_status,
        )

        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-06-26", "2026-07-10"),
        )

        self.assertEqual(status["status"], "price_refresh_available")
        self.assertEqual(status["stored_curve_end"], "2026-06-26")
        self.assertEqual(status["latest_completed_market_date"], "2026-07-15")
        self.assertEqual(status["db_common_price_date"], "2026-06-26")
        self.assertEqual(status["limiting_symbols"], ["BIL"])
        self.assertIn("BIL", status["refreshable_symbols"])
        self.assertTrue(status["selection_blocked"])

    def test_db_common_date_newer_than_curve_requires_replay_only(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-15", "2026-07-15"),
        )

        self.assertEqual(status["status"], "replay_available")
        self.assertEqual(status["db_common_price_date"], "2026-07-15")
        self.assertTrue(status["can_refresh"])

    def test_curve_at_target_is_up_to_date(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation_fixture(curve_end="2026-07-15"),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-15", "2026-07-15"),
        )

        self.assertEqual(status["status"], "up_to_date")
        self.assertFalse(status["can_refresh"])
        self.assertFalse(status["selection_blocked"])

    def test_known_provider_gap_is_partial_not_endless_refresh(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        validation = validation_fixture()
        validation["observation_refresh_snapshot"] = {
            "target_market_date": "2026-07-15",
            "provider_gap_symbols": ["BIL"],
        }
        status = build_final_review_refresh_status(
            source=source_fixture(),
            validation=validation,
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-06-26", "2026-07-15"),
        )

        self.assertEqual(status["status"], "partial_refresh")
        self.assertEqual(status["provider_gap_symbols"], ["BIL"])
        self.assertFalse(status["can_refresh"])
        self.assertFalse(status["selection_blocked"])

    def test_missing_selection_source_contract_is_blocked(self) -> None:
        from app.services.backtest_final_review_refresh import build_final_review_refresh_status

        status = build_final_review_refresh_status(
            source={},
            validation={"validation_id": "validation-missing"},
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: pd.DataFrame(),
        )

        self.assertEqual(status["status"], "blocked")
        self.assertFalse(status["can_refresh"])
        self.assertTrue(status["selection_blocked"])


if __name__ == "__main__":
    unittest.main()
