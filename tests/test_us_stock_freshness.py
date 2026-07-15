from __future__ import annotations

import unittest
from datetime import datetime
from unittest.mock import Mock
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


class UsStockRefreshIngestionTests(unittest.TestCase):
    def test_market_scopes_run_without_cik_and_statement_scope_remains(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_us_stock_refresh_inputs

        profile_runner = Mock(
            return_value={
                "status": "success",
                "rows_written": 1,
                "failed_symbols": [],
                "message": "profile ok",
            }
        )
        price_runner = Mock(
            return_value={
                "status": "success",
                "rows_written": 5,
                "failed_symbols": [],
                "message": "price ok",
            }
        )
        statement_runner = Mock()

        result = run_collect_us_stock_refresh_inputs(
            "NET",
            cik="",
            identity_cik="",
            price_start="2026-07-07",
            price_end="2026-07-15",
            collect_profile=True,
            collect_prices=True,
            collect_statements=True,
            profile_runner=profile_runner,
            price_runner=price_runner,
            statement_runner=statement_runner,
        )

        profile_runner.assert_called_once_with(
            kinds=("stock",),
            symbols=["NET"],
            progress_callback=None,
        )
        price_runner.assert_called_once_with(
            ["NET"],
            start="2026-07-07",
            end="2026-07-15",
            interval="1d",
            execution_profile="managed_safe",
        )
        statement_runner.assert_not_called()
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 6)
        self.assertEqual(result["details"]["remaining_scopes"], ["sec_statements"])

    def test_invalid_symbol_runs_no_refresh_scope(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_us_stock_refresh_inputs

        profile_runner = Mock()
        price_runner = Mock()
        statement_runner = Mock()

        result = run_collect_us_stock_refresh_inputs(
            "BAD SYMBOL",
            cik="",
            identity_cik="",
            price_start="2026-07-07",
            price_end="2026-07-15",
            collect_profile=True,
            collect_prices=True,
            collect_statements=True,
            profile_runner=profile_runner,
            price_runner=price_runner,
            statement_runner=statement_runner,
        )

        self.assertEqual(result["status"], "failed")
        profile_runner.assert_not_called()
        price_runner.assert_not_called()
        statement_runner.assert_not_called()


class UsStockRefreshFacadeTests(unittest.TestCase):
    @staticmethod
    def _model(
        *,
        cik: str | None,
        status: str,
        scopes: list[str] | None = None,
    ) -> dict[str, object]:
        freshness: dict[str, object] = {
            "status": status,
            "expected_price_date": "2026-07-15",
            "price_basis_date": "2026-07-07",
            "profile_basis_date": "2026-02-04",
            "gaps": [],
        }
        if scopes:
            freshness["action"] = {
                "id": "refresh_us_stock_data",
                "symbol": "NET",
                "scopes": scopes,
                "enabled": True,
            }
        return {
            "instruments": {
                "us_stock": {
                    "selection": {"symbol": "NET", "cik": cik},
                    "data_freshness": freshness,
                }
            }
        }

    def test_facade_collects_market_before_identity_then_statements(self) -> None:
        from app.jobs.overview_actions import run_overview_us_stock_data_refresh

        calls: list[str] = []
        models = iter(
            [
                self._model(
                    cik=None,
                    status="REFRESH_AVAILABLE",
                    scopes=["asset_profile", "prices", "sec_identity", "sec_statements"],
                ),
                self._model(
                    cik="1892534",
                    status="REFRESH_AVAILABLE",
                    scopes=["sec_statements"],
                ),
                self._model(cik="1892534", status="READY"),
            ]
        )

        def model_builder(*, selected_symbol: str):
            calls.append("model")
            self.assertEqual(selected_symbol, "NET")
            return next(models)

        def collection_runner(symbol: str, **kwargs):
            self.assertEqual(symbol, "NET")
            if kwargs["collect_statements"]:
                calls.append("collect:sec")
                self.assertEqual(kwargs["cik"], "1892534")
                return {"status": "success", "rows_written": 20, "failed_symbols": []}
            calls.append("collect:market")
            self.assertTrue(kwargs["collect_profile"])
            self.assertTrue(kwargs["collect_prices"])
            self.assertEqual(kwargs["cik"], "")
            return {"status": "success", "rows_written": 6, "failed_symbols": []}

        def identity_runner(symbols, *, progress_callback=None):
            calls.append("identity")
            self.assertEqual(symbols, ["NET"])
            self.assertIsNone(progress_callback)
            return {"status": "success", "rows_written": 1, "failed_symbols": []}

        result = run_overview_us_stock_data_refresh(
            "NET",
            model_builder=model_builder,
            identity_runner=identity_runner,
            collection_runner=collection_runner,
        )

        self.assertEqual(
            calls,
            ["model", "collect:market", "identity", "model", "collect:sec", "model"],
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 27)
        self.assertEqual(result["details"]["before"]["action"]["symbol"], "NET")
        self.assertEqual(result["details"]["after"]["status"], "READY")

    def test_facade_preserves_market_success_when_identity_remains_missing(self) -> None:
        from app.jobs.overview_actions import run_overview_us_stock_data_refresh

        calls: list[str] = []
        before = self._model(
            cik=None,
            status="REFRESH_AVAILABLE",
            scopes=["asset_profile", "prices", "sec_identity", "sec_statements"],
        )
        remaining = self._model(
            cik=None,
            status="REFRESH_AVAILABLE",
            scopes=["sec_identity", "sec_statements"],
        )
        models = iter([before, remaining, remaining])

        def model_builder(*, selected_symbol: str):
            calls.append("model")
            return next(models)

        def collection_runner(symbol: str, **kwargs):
            calls.append("collect:market")
            self.assertFalse(kwargs["collect_statements"])
            return {"status": "success", "rows_written": 6, "failed_symbols": []}

        def identity_runner(symbols, *, progress_callback=None):
            calls.append("identity")
            return {"status": "failed", "rows_written": 0, "failed_symbols": ["NET"]}

        result = run_overview_us_stock_data_refresh(
            "NET",
            model_builder=model_builder,
            identity_runner=identity_runner,
            collection_runner=collection_runner,
        )

        self.assertEqual(
            calls,
            ["model", "collect:market", "identity", "model", "model"],
        )
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 6)
        self.assertEqual(
            result["details"]["after"]["action"]["scopes"],
            ["sec_identity", "sec_statements"],
        )

    def test_ready_facade_is_noop_without_provider_calls(self) -> None:
        from app.jobs.overview_actions import run_overview_us_stock_data_refresh

        model_builder = Mock(return_value=self._model(cik="1892534", status="READY"))
        identity_runner = Mock()
        collection_runner = Mock()

        result = run_overview_us_stock_data_refresh(
            "NET",
            model_builder=model_builder,
            identity_runner=identity_runner,
            collection_runner=collection_runner,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 0)
        identity_runner.assert_not_called()
        collection_runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
