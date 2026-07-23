from __future__ import annotations

import unittest
from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo


class Sp500PriceFreshnessTests(unittest.TestCase):
    def test_ready_when_spx_reaches_latest_completed_session(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        model = {
            "basis": {
                "spx": {"date": "2026-07-23"},
                "spy": {"date": "2026-07-23"},
            }
        }
        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness(model)

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["gap_sessions"], 0)
        self.assertNotIn("action", result)

    def test_stale_spx_exposes_one_manual_action_and_session_gap(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        model = {
            "basis": {
                "spx": {"date": "2026-07-16"},
                "spy": {"date": "2026-07-22"},
            }
        }
        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness(model)

        self.assertEqual(result["status"], "REFRESH_AVAILABLE")
        self.assertEqual(result["gap_sessions"], 5)
        self.assertEqual(result["price_basis_date"], "2026-07-16")
        self.assertEqual(result["spy_price_basis_date"], "2026-07-22")
        self.assertEqual(
            result["action"],
            {
                "id": "refresh_sp500_price_data",
                "label": "최신 데이터로 다시 계산",
                "enabled": True,
            },
        )

    def test_missing_spx_is_actionable(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness({"basis": {}})

        self.assertEqual(result["status"], "MISSING")
        self.assertIsNone(result["price_basis_date"])
        self.assertEqual(result["action"]["id"], "refresh_sp500_price_data")

    def test_future_dated_spx_keeps_warning_evidence(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        model = {"basis": {"spx": {"date": "2026-07-24"}}}
        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            return_value=date(2026, 7, 23),
        ):
            result = build_sp500_price_freshness(model)

        self.assertEqual(result["status"], "READY")
        self.assertIn("SPX_PRICE_DATE_AFTER_COMPLETED_SESSION", result["warnings"])

    def test_calendar_error_preserves_retry_action(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        with patch(
            "app.services.overview.sp500_valuation_freshness.latest_completed_nyse_session",
            side_effect=RuntimeError("calendar unavailable"),
        ):
            result = build_sp500_price_freshness(
                {"basis": {"spx": {"date": "2026-07-16"}}}
            )

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["action"]["id"], "refresh_sp500_price_data")
        self.assertIn("최신 완료 장", result["message"])

    def test_market_open_uses_previous_completed_session(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        result = build_sp500_price_freshness(
            {"basis": {"spx": {"date": "2026-07-23"}}},
            now=datetime(
                2026,
                7,
                24,
                10,
                0,
                tzinfo=ZoneInfo("America/New_York"),
            ),
        )

        self.assertEqual(result["expected_price_date"], "2026-07-23")
        self.assertEqual(result["status"], "READY")

    def test_weekend_uses_friday_completed_session(self) -> None:
        from app.services.overview.sp500_valuation_freshness import (
            build_sp500_price_freshness,
        )

        result = build_sp500_price_freshness(
            {"basis": {"spx": {"date": "2026-07-24"}}},
            now=datetime(
                2026,
                7,
                25,
                12,
                0,
                tzinfo=ZoneInfo("America/New_York"),
            ),
        )

        self.assertEqual(result["expected_price_date"], "2026-07-24")
        self.assertEqual(result["status"], "READY")
