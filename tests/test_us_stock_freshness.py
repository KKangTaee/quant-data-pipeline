from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo


US_EASTERN = ZoneInfo("America/New_York")


def _turnaround_model(
    *,
    profile_basis_date: str | None,
    price_basis_date: str | None,
    statement_core_missing: bool = False,
    scopes: list[str] | None = None,
) -> dict[str, object]:
    return {
        "coverage": {
            "profile_basis_date": profile_basis_date,
            "price_basis_date": price_basis_date,
            "statement_period_end": "2026-03-31",
            "statement_available_at": "2026-05-08",
            "statement_core_missing": statement_core_missing,
        },
        "collection_plan": {"scopes": list(scopes or [])},
    }


class UsStockFreshnessTests(unittest.TestCase):
    def test_missing_selected_identity_blocks_freshness_action(self) -> None:
        from app.services.overview.us_stock_freshness import (
            build_us_stock_data_freshness,
        )

        result = build_us_stock_data_freshness(
            "NET",
            per_model={"status": "ERROR", "selection": None},
            turnaround_model={"status": "ERROR", "coverage": {}},
            now=datetime(2026, 7, 15, 18, 0, tzinfo=US_EASTERN),
        )

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["reason_code"], "IDENTITY_UNAVAILABLE")
        self.assertNotIn("action", result)

    def test_net_like_stale_market_data_remains_refreshable_without_cik(self) -> None:
        from app.services.overview.us_stock_freshness import (
            build_us_stock_data_freshness,
        )

        result = build_us_stock_data_freshness(
            "NET",
            per_model={
                "selection": {
                    "symbol": "NET",
                    "cik": None,
                    "latest_price_date": "2026-07-07",
                }
            },
            turnaround_model=_turnaround_model(
                profile_basis_date="2026-02-04",
                price_basis_date="2026-07-07",
                scopes=["asset_profile", "prices"],
            ),
            now=datetime(2026, 7, 15, 18, 0, tzinfo=US_EASTERN),
        )

        self.assertEqual(result["status"], "REFRESH_AVAILABLE")
        self.assertEqual(result["expected_price_date"], "2026-07-15")
        self.assertEqual(result["action"]["symbol"], "NET")
        self.assertEqual(result["action"]["scopes"], ["asset_profile", "prices"])
        self.assertNotIn("sec_identity", result["action"]["scopes"])

    def test_statement_period_end_age_alone_does_not_create_refresh_action(self) -> None:
        from app.services.overview.us_stock_freshness import (
            build_us_stock_data_freshness,
        )

        result = build_us_stock_data_freshness(
            "AAPL",
            per_model={
                "selection": {
                    "symbol": "AAPL",
                    "cik": "320193",
                    "latest_price_date": "2026-07-15",
                }
            },
            turnaround_model=_turnaround_model(
                profile_basis_date="2026-07-15",
                price_basis_date="2026-07-15",
            ),
            now=datetime(2026, 7, 15, 18, 0, tzinfo=US_EASTERN),
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["statement_period_end"], "2026-03-31")
        self.assertEqual(result["statement_available_at"], "2026-05-08")
        self.assertNotIn("action", result)

    def test_statement_gap_adds_identity_but_keeps_market_scopes_collectable(self) -> None:
        from app.services.overview.us_stock_freshness import (
            build_us_stock_data_freshness,
        )

        result = build_us_stock_data_freshness(
            "NET",
            per_model={
                "selection": {
                    "symbol": "NET",
                    "cik": None,
                    "latest_price_date": "2026-07-07",
                },
                "collection_action": {"scopes": ["sec_statements"]},
            },
            turnaround_model=_turnaround_model(
                profile_basis_date="2026-02-04",
                price_basis_date="2026-07-07",
                statement_core_missing=True,
                scopes=["asset_profile", "prices", "sec_statements"],
            ),
            now=datetime(2026, 7, 15, 18, 0, tzinfo=US_EASTERN),
        )

        self.assertEqual(
            result["action"]["scopes"],
            ["asset_profile", "prices", "sec_identity", "sec_statements"],
        )
        self.assertEqual(
            [gap["reason_code"] for gap in result["gaps"]],
            [
                "PROFILE_PRICE_BASIS_MISALIGNED",
                "PRICE_BEHIND_COMPLETED_SESSION",
                "SEC_IDENTITY_MISSING",
                "STATEMENT_RAW_GAP",
            ],
        )

    def test_structural_per_state_does_not_become_a_refresh_scope(self) -> None:
        from app.services.overview.us_stock_freshness import (
            build_us_stock_data_freshness,
        )

        result = build_us_stock_data_freshness(
            "RIVN",
            per_model={
                "selection": {
                    "symbol": "RIVN",
                    "cik": "1874178",
                    "latest_price_date": "2026-07-15",
                },
                "readiness": {"reason_code": "NON_POSITIVE_EPS"},
            },
            turnaround_model=_turnaround_model(
                profile_basis_date="2026-07-15",
                price_basis_date="2026-07-15",
            ),
            now=datetime(2026, 7, 15, 18, 0, tzinfo=US_EASTERN),
        )

        self.assertEqual(result["status"], "READY")
        self.assertNotIn("action", result)


if __name__ == "__main__":
    unittest.main()
