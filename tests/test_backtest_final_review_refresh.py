from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import MagicMock
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


def replay_result(*, end: str = "2026-07-15", status: str = "PASS") -> dict[str, object]:
    return {
        "status": status,
        "portfolio_curve": [
            {"Date": "2016-01-29", "Total Balance": 10000.0},
            {"Date": end, "Total Balance": 54000.0},
        ],
        "period_coverage": {
            "status": "PASS",
            "actual_period": {"start": "2016-01-29", "end": end},
        },
        "market_date_contract": {
            "requested_market_date": "2026-07-15",
            "latest_common_price_date": end,
            "limiting_symbols": ["BIL"] if end < "2026-07-15" else [],
        },
    }


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


class FinalReviewRefreshOrchestrationTests(unittest.TestCase):
    def test_replay_available_skips_ingestion_and_appends_new_validation(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        price_runner = MagicMock()
        replay_runner = MagicMock(return_value=replay_result())
        validation_builder = MagicMock(
            return_value={
                "validation_id": "validation-grs-refreshed",
                "selection_source_id": "selection-grs-current",
                "final_review_gate": {"can_save_and_move": True},
            }
        )
        saver = MagicMock()

        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-15", "2026-07-15"),
            price_refresh_runner=price_runner,
            replay_runner=replay_runner,
            validation_builder=validation_builder,
            validation_saver=saver,
        )

        price_runner.assert_not_called()
        replay_runner.assert_called_once()
        saver.assert_called_once()
        self.assertEqual(result["status"], "refreshed")
        self.assertEqual(result["new_validation_id"], "validation-grs-refreshed")
        self.assertTrue(result["validation_saved"])

    def test_price_refresh_runs_before_replay_when_common_date_is_stale(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        frames = iter(
            [
                freshness_frame("2026-06-26", "2026-07-10"),
                freshness_frame("2026-07-15", "2026-07-15"),
            ]
        )
        price_runner = MagicMock(
            return_value={
                "status": "success",
                "rows_written": 18,
                "details": {
                    "post_refresh_unresolved_symbols": [],
                    "post_refresh_price_freshness": {"details": {"classification_rows": []}},
                },
            }
        )
        replay_runner = MagicMock(return_value=replay_result())
        validation_builder = MagicMock(
            return_value={
                "validation_id": "validation-grs-latest",
                "selection_source_id": "selection-grs-current",
                "final_review_gate": {"can_save_and_move": True},
            }
        )
        saver = MagicMock()

        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: next(frames),
            price_refresh_runner=price_runner,
            replay_runner=replay_runner,
            validation_builder=validation_builder,
            validation_saver=saver,
        )

        refresh_meta = price_runner.call_args.args[0]
        self.assertEqual(refresh_meta["end"], "2026-07-15")
        self.assertIn("BIL", refresh_meta["price_freshness"]["details"]["stale_symbols_all"])
        replay_runner.assert_called_once()
        saver.assert_called_once()
        self.assertEqual(result["status"], "refreshed")
        self.assertEqual(result["refreshed_curve_end"], "2026-07-15")

    def test_replay_failure_after_price_refresh_never_saves_validation(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        frames = iter(
            [
                freshness_frame("2026-06-26", "2026-07-10"),
                freshness_frame("2026-07-15", "2026-07-15"),
            ]
        )
        saver = MagicMock()
        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: next(frames),
            price_refresh_runner=MagicMock(
                return_value={"status": "success", "rows_written": 12, "details": {}}
            ),
            replay_runner=MagicMock(return_value=replay_result(status="BLOCKED")),
            validation_builder=MagicMock(),
            validation_saver=saver,
        )

        self.assertEqual(result["status"], "failed_after_price_refresh")
        self.assertFalse(result["validation_saved"])
        saver.assert_not_called()

    def test_blocked_new_validation_is_not_appended(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        saver = MagicMock()
        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: freshness_frame("2026-07-15", "2026-07-15"),
            price_refresh_runner=MagicMock(),
            replay_runner=MagicMock(return_value=replay_result()),
            validation_builder=MagicMock(
                return_value={
                    "validation_id": "validation-blocked",
                    "selection_source_id": "selection-grs-current",
                    "final_review_gate": {"can_save_and_move": False},
                }
            ),
            validation_saver=saver,
        )

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["validation_saved"])
        saver.assert_not_called()

    def test_no_curve_progress_returns_partial_without_append(self) -> None:
        from app.services.backtest_final_review_refresh import (
            run_final_review_observation_refresh,
        )

        frames = iter(
            [
                freshness_frame("2026-06-26", "2026-07-10"),
                freshness_frame("2026-06-26", "2026-07-10"),
            ]
        )
        saver = MagicMock()
        result = run_final_review_observation_refresh(
            source=source_fixture(),
            validation=validation_fixture(),
            now=datetime(2026, 7, 16, 5, 0, tzinfo=ET),
            freshness_loader=lambda **_: next(frames),
            price_refresh_runner=MagicMock(
                return_value={
                    "status": "partial_success",
                    "rows_written": 5,
                    "details": {
                        "post_refresh_unresolved_symbols": ["BIL"],
                        "post_refresh_price_freshness": {
                            "details": {
                                "classification_rows": [
                                    {
                                        "symbol": "BIL",
                                        "reason": "persistent_source_gap_or_symbol_issue",
                                    }
                                ]
                            }
                        },
                    },
                }
            ),
            replay_runner=MagicMock(),
            validation_builder=MagicMock(),
            validation_saver=saver,
        )

        self.assertEqual(result["status"], "partial_refresh")
        self.assertEqual(result["provider_gap_symbols"], ["BIL"])
        self.assertFalse(result["replay_executed"])
        saver.assert_not_called()


if __name__ == "__main__":
    unittest.main()
