from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd


class PracticalValidationServiceContractTests(unittest.TestCase):
    def test_source_handoff_without_persistence_is_ui_neutral(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {
            "selection_source_id": "source-1",
            "source_title": "Quality portfolio",
            "source_type": "saved_mix",
        }

        with patch.object(service, "append_portfolio_selection_source") as append_source:
            handoff = service.prepare_practical_validation_source_handoff(source, persist=False)

        append_source.assert_not_called()
        self.assertEqual(handoff.source_payload, source)
        self.assertIsNot(handoff.source_payload, source)
        self.assertEqual(handoff.mode, "Selected Source")
        self.assertEqual(handoff.requested_panel, "Practical Validation")
        self.assertFalse(handoff.persisted)
        self.assertIn("Quality portfolio", handoff.notice)
        self.assertIn("live approval", handoff.notice)

    def test_source_handoff_with_persistence_reports_persisted(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {"selection_source_id": "source-2"}

        with patch.object(service, "append_portfolio_selection_source") as append_source:
            handoff = service.prepare_practical_validation_source_handoff(source, persist=True)

        append_source.assert_called_once_with(source)
        self.assertTrue(handoff.persisted)
        self.assertEqual(handoff.source_payload, source)
        self.assertIn("source-2", handoff.notice)

    def test_final_review_handoff_without_persistence_preserves_payloads(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {"selection_source_id": "source-3", "source_type": "single_strategy"}
        validation_result = {
            "selection_source_id": "source-3",
            "source_title": "Dual momentum candidate",
            "overall_status": "REVIEW",
        }

        with patch.object(service, "save_practical_validation_result") as save_result:
            handoff = service.prepare_final_review_handoff_from_validation(
                source=source,
                validation_result=validation_result,
                persist_validation=False,
            )

        save_result.assert_not_called()
        self.assertEqual(handoff.requested_panel, "Final Review")
        self.assertFalse(handoff.persisted)
        self.assertEqual(handoff.session_payload["source"], source)
        self.assertIsNot(handoff.session_payload["source"], source)
        self.assertEqual(handoff.session_payload["validation_result"], validation_result)
        self.assertIsNot(handoff.session_payload["validation_result"], validation_result)
        self.assertIn("Dual momentum candidate", handoff.notice)

    def test_final_review_handoff_with_persistence_saves_validation_result(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {"selection_source_id": "source-4"}
        validation_result = {"selection_source_id": "source-4"}

        with patch.object(service, "save_practical_validation_result") as save_result:
            handoff = service.prepare_final_review_handoff_from_validation(
                source=source,
                validation_result=validation_result,
                persist_validation=True,
            )

        save_result.assert_called_once_with(validation_result)
        self.assertTrue(handoff.persisted)
        self.assertEqual(handoff.requested_panel, "Final Review")

    def test_service_imports_do_not_load_streamlit(self) -> None:
        script = """
import sys
import app.runtime
import app.runtime.backtest
import app.runtime.candidate_library
import app.runtime.backtest_result_bundle
import app.services.backtest_evidence_read_model
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_diagnostics
import app.services.backtest_practical_validation
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_replay
import app.services.backtest_practical_validation_source
import app.services.overview_market_intelligence
print("streamlit" in sys.modules)
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "False")

    def test_runtime_package_import_does_not_load_streamlit(self) -> None:
        script = """
import sys
import importlib.util
import app.runtime
import app.runtime.candidate_library
print("streamlit" in sys.modules)
print(importlib.util.find_spec("app.web.runtime") is None)
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.splitlines(), ["False", "True"])

    def test_practical_validation_helpers_are_not_web_modules(self) -> None:
        script = """
import importlib.util
import sys
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_curve_context
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_stress_sensitivity
import app.services.backtest_practical_validation_source
print("streamlit" in sys.modules)
print(importlib.util.find_spec("app.web.backtest_practical_validation_curve") is None)
print(importlib.util.find_spec("app.web.backtest_practical_validation_connectors") is None)
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.splitlines(), ["False", "True", "True"])


class PracticalValidationDiagnosticsServiceContractTests(unittest.TestCase):
    def test_diagnostics_public_compatibility_contract_is_explicit(self) -> None:
        from app.services import backtest_practical_validation_curve_context as curve_context
        from app.services import backtest_practical_validation_diagnostics as diagnostics
        from app.services import backtest_practical_validation_source as source_builders

        self.assertEqual(
            diagnostics.__all__,
            [
                "VALIDATION_PROFILE_OPTIONS",
                "VALIDATION_PROFILE_QUESTIONS",
                "build_practical_validation_result",
                "build_selection_source_from_candidate_draft",
                "build_selection_source_from_saved_mix_prefill",
                "build_selection_source_from_weighted_mix_prefill",
                "build_validation_profile",
                "compact_benchmark_curve_snapshot_from_bundle",
                "compact_curve_snapshot_from_bundle",
                "source_components_dataframe",
            ],
        )
        self.assertIs(diagnostics.build_validation_profile, source_builders.build_validation_profile)
        self.assertIs(diagnostics.source_components_dataframe, source_builders.source_components_dataframe)
        self.assertIs(diagnostics.compact_curve_snapshot_from_bundle, curve_context.compact_curve_snapshot_from_bundle)

    def test_profile_builder_and_curve_snapshot_are_ui_neutral(self) -> None:
        from app.services import backtest_practical_validation_curve_context as curve_context
        from app.services import backtest_practical_validation_source as source_builders

        profile = source_builders.build_validation_profile(
            "custom",
            {
                "primary_goal": "defensive",
                "drawdown_tolerance": "dd_10",
                "holding_period": "6_to_12m",
                "complexity_allowance": "broad_etf_only",
                "alternative_success_metric": "lower_mdd",
            },
        )
        curve = curve_context.compact_curve_snapshot_from_bundle(
            {
                "result_df": pd.DataFrame(
                    [
                        {"Date": "2020-01-31", "Total Balance": 100.0},
                        {"Date": "2020-02-28", "Total Balance": 98.0},
                    ]
                )
            }
        )

        self.assertEqual(profile["profile_id"], "custom")
        self.assertEqual(profile["profile_label"], "사용자 지정")
        self.assertEqual(profile["answers"]["primary_goal"], "defensive")
        self.assertEqual(profile["answer_labels"]["drawdown_tolerance"], "-10% 내외")
        self.assertEqual(profile["thresholds"]["mdd_review_line"], -10.0)
        self.assertGreaterEqual(profile["domain_weights"]["stress_scenario_diagnostics"], 1.35)
        self.assertEqual([row["Date"] for row in curve], ["2020-01-31", "2020-02-28"])
        self.assertEqual([row["Total Balance"] for row in curve], [100.0, 98.0])
        self.assertAlmostEqual(curve[0]["Total Return"], 0.0)
        self.assertAlmostEqual(curve[1]["Total Return"], -0.02)


class BoundaryContractHardeningTests(unittest.TestCase):
    def _load_boundary_checker(self):
        script_path = (
            Path(__file__).resolve().parents[1]
            / ".aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py"
        )
        spec = importlib.util.spec_from_file_location("check_ui_engine_boundary", script_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_app_web_import_is_hard_boundary_violation(self) -> None:
        checker = self._load_boundary_checker()

        with tempfile.TemporaryDirectory() as tmp_dir:
            candidate = Path(tmp_dir) / "bad_runtime.py"
            candidate.write_text(
                "from app.web.backtest_common import format_percent\n",
                encoding="utf-8",
            )

            with (
                patch.object(checker, "_boundary_files", return_value=[candidate]),
                patch.object(checker, "_relative", return_value="app/runtime/bad_runtime.py"),
            ):
                violations, advisories = checker._scan_boundary_files()

        self.assertEqual(advisories, [])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["kind"], "app_web_import")
        self.assertEqual(violations[0]["path"], "app/runtime/bad_runtime.py")


class FinanceWorkspacePathContractTests(unittest.TestCase):
    def test_runtime_and_job_paths_use_canonical_aiworkspace_note_root(self) -> None:
        from app.jobs.result_artifacts import RUN_ARTIFACT_DIR
        from app.jobs.run_history import HISTORY_FILE
        from app.runtime import (
            BACKTEST_HISTORY_FILE,
            CURRENT_CANDIDATE_REGISTRY_FILE,
            FINAL_SELECTION_DECISION_REGISTRY_FILE,
            PORTFOLIO_PROPOSAL_REGISTRY_FILE,
            SAVED_PORTFOLIO_FILE,
        )
        from app.workspace_paths import FINANCE_NOTE_DIR, PROJECT_ROOT, REGISTRIES_DIR, SAVED_DIR

        expected_note_dir = PROJECT_ROOT / ".aiworkspace" / "note" / "finance"
        self.assertEqual(FINANCE_NOTE_DIR, expected_note_dir)
        self.assertEqual(REGISTRIES_DIR, expected_note_dir / "registries")
        self.assertEqual(SAVED_DIR, expected_note_dir / "saved")

        runtime_paths = [
            CURRENT_CANDIDATE_REGISTRY_FILE,
            FINAL_SELECTION_DECISION_REGISTRY_FILE,
            PORTFOLIO_PROPOSAL_REGISTRY_FILE,
            SAVED_PORTFOLIO_FILE,
            BACKTEST_HISTORY_FILE,
            HISTORY_FILE,
            RUN_ARTIFACT_DIR,
        ]
        for path in runtime_paths:
            path_text = str(path)
            self.assertIn("/.aiworkspace/note/finance/", path_text)
            self.assertNotIn("/.note/finance/", path_text)


class BacktestRuntimeContractTests(unittest.TestCase):
    def test_result_bundle_public_compatibility_contract_is_preserved(self) -> None:
        import app.runtime
        from app.runtime import backtest as runtime_backtest
        from app.runtime import backtest_result_bundle

        self.assertIs(
            runtime_backtest.build_backtest_result_bundle,
            backtest_result_bundle.build_backtest_result_bundle,
        )
        self.assertIs(
            app.runtime.build_backtest_result_bundle,
            backtest_result_bundle.build_backtest_result_bundle,
        )

    def test_result_bundle_contract_sorts_dates_and_keeps_metadata(self) -> None:
        from app.runtime.backtest_result_bundle import build_backtest_result_bundle

        bundle = build_backtest_result_bundle(
            pd.DataFrame(
                [
                    {"Date": "2020-02-29", "Total Balance": 102.0, "Total Return": 0.02},
                    {"Date": "2020-01-31", "Total Balance": 100.0, "Total Return": 0.0},
                ]
            ),
            strategy_name="Global Relative Strength",
            strategy_key="global_relative_strength",
            input_params={
                "tickers": ["SPY", "TLT"],
                "start": "2020-01-01",
                "end": "2020-02-29",
                "timeframe": "1d",
                "option": "month_end",
                "rebalance_interval": 1,
                "score_lookback_months": [3, 6, 12],
            },
            warnings=["price freshness warning"],
        )

        self.assertEqual(bundle["strategy_name"], "Global Relative Strength")
        self.assertEqual(
            [date.strftime("%Y-%m-%d") for date in bundle["result_df"]["Date"]],
            ["2020-01-31", "2020-02-29"],
        )
        self.assertEqual(
            [date.strftime("%Y-%m-%d") for date in bundle["chart_df"]["Date"]],
            ["2020-01-31", "2020-02-29"],
        )
        self.assertEqual(bundle["meta"]["strategy_family"], "Global Relative Strength")
        self.assertEqual(bundle["meta"]["result_rows"], 2)
        self.assertEqual(bundle["meta"]["actual_result_start"], "2020-01-31")
        self.assertEqual(bundle["meta"]["actual_result_end"], "2020-02-29")
        self.assertEqual(bundle["meta"]["tickers"], ["SPY", "TLT"])
        self.assertEqual(bundle["meta"]["warnings"], ["price freshness warning"])
        self.assertEqual(bundle["meta"]["score_lookback_months"], [3, 6, 12])
        self.assertFalse(bundle["summary_df"].empty)

    def test_result_bundle_rejects_missing_required_columns(self) -> None:
        from app.runtime.backtest_result_bundle import build_backtest_result_bundle

        with self.assertRaisesRegex(ValueError, "missing required columns"):
            build_backtest_result_bundle(
                pd.DataFrame([{"Date": "2020-01-31", "Total Balance": 100.0}]),
                strategy_name="Equal Weight",
                strategy_key="equal_weight",
                input_params={},
            )


class OverviewMarketIntelligenceServiceContractTests(unittest.TestCase):
    def _query_fn(self, db_name: str, sql: str, params=None) -> list[dict[str, object]]:
        del db_name
        if "FROM market_event_calendar" in sql:
            rows = [
                {
                    "event_date": "2026-06-17",
                    "event_type": "FOMC_MEETING",
                    "symbol": None,
                    "title": "FOMC Meeting: June 16-17*, 2026",
                    "source": "federal_reserve_fomc_calendar",
                    "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                    "confidence": 1.0,
                    "collected_at": "2026-05-28 02:00:00",
                },
                {
                    "event_date": "2026-07-29",
                    "event_type": "FOMC_MEETING",
                    "symbol": None,
                    "title": "FOMC Meeting: July 28-29, 2026",
                    "source": "federal_reserve_fomc_calendar",
                    "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                    "confidence": 1.0,
                    "collected_at": "2026-05-28 02:00:00",
                },
                {
                    "event_date": "2026-07-30",
                    "event_type": "EARNINGS",
                    "symbol": "MSFT",
                    "title": "MSFT Earnings Release",
                    "source": "yfinance_calendar",
                    "source_url": "https://finance.yahoo.com/quote/MSFT/analysis",
                    "confidence": 0.65,
                    "collected_at": "2026-05-28 03:00:00",
                },
            ]
            event_filter = None
            for value in params or []:
                if value in {"FOMC_MEETING", "EARNINGS"}:
                    event_filter = value
                    break
            if event_filter:
                return [row for row in rows if row["event_type"] == event_filter]
            return rows
        if "FROM market_universe_member" in sql:
            return [
                {
                    "symbol": "AAA",
                    "long_name": "AAA Corp",
                    "sector": "Technology",
                    "industry": "Software",
                    "market_cap": 100,
                    "status": "active",
                    "error_msg": None,
                    "last_collected_at": "2026-05-18 10:00:00",
                    "universe_as_of_date": "2026-05-28",
                    "universe_collected_at": "2026-05-28 11:00:00",
                    "universe_source": "wikipedia_sp500_constituents",
                    "universe_source_url": "https://example.test/sp500",
                },
                {
                    "symbol": "BBB",
                    "long_name": "BBB Corp",
                    "sector": "Healthcare",
                    "industry": "Medical Devices",
                    "market_cap": 200,
                    "status": "active",
                    "error_msg": None,
                    "last_collected_at": "2026-05-18 10:00:00",
                    "universe_as_of_date": "2026-05-28",
                    "universe_collected_at": "2026-05-28 11:00:00",
                    "universe_source": "wikipedia_sp500_constituents",
                    "universe_source_url": "https://example.test/sp500",
                },
            ]
        if "MAX(snapshot_time_utc) AS snapshot_time_utc" in sql:
            return [{"snapshot_time_utc": "2026-05-18 15:35:00"}]
        if "FROM market_intraday_snapshot s" in sql:
            return [
                {
                    "symbol": "AAA",
                    "interval_code": "5m",
                    "snapshot_time_utc": "2026-05-18 15:35:00",
                    "quote_time_utc": "2026-05-18 15:30:00",
                    "previous_close": 100.0,
                    "latest_price": 112.0,
                    "return_pct": 12.0,
                    "volume": 1000,
                    "provider_status": "ok",
                    "error_msg": None,
                    "source": "yfinance",
                    "source_ref": "test",
                },
                {
                    "symbol": "BBB",
                    "interval_code": "5m",
                    "snapshot_time_utc": "2026-05-18 15:35:00",
                    "quote_time_utc": None,
                    "previous_close": None,
                    "latest_price": None,
                    "return_pct": None,
                    "volume": None,
                    "provider_status": "missing",
                    "error_msg": "missing latest price",
                    "source": "yfinance",
                    "source_ref": "test",
                },
            ]
        if "MAX(`date`) AS latest_raw_date" in sql:
            return [{"latest_raw_date": "2026-05-19"}]
        if "MAX(`date`) AS latest_price_date" in sql:
            return [
                {"symbol": "AAA", "latest_price_date": "2026-05-18"},
                {"symbol": "BBB", "latest_price_date": "2026-05-18"},
                {"symbol": "CCC", "latest_price_date": "2026-05-18"},
                {"symbol": "DDD", "latest_price_date": "2026-05-18"},
            ]
        if "GROUP BY `date`" in sql:
            dates = [
                "2026-05-18",
                "2026-05-15",
                "2026-05-14",
                "2026-05-13",
                "2026-05-12",
                "2026-05-11",
                "2026-05-08",
                "2026-05-07",
                "2026-05-06",
                "2026-05-05",
                "2026-05-04",
                "2026-05-01",
                "2026-04-30",
                "2026-04-29",
                "2026-04-28",
                "2026-04-27",
                "2026-04-24",
                "2026-04-23",
                "2026-04-22",
                "2026-04-21",
                "2026-04-20",
                "2026-04-17",
            ]
            return [{"date": item, "usable_rows": 1200} for item in dates]
        if "FROM nyse_asset_profile" in sql:
            return [
                {
                    "symbol": "AAA",
                    "long_name": "AAA Corp",
                    "sector": "Technology",
                    "industry": "Software",
                    "market_cap": 100,
                },
                {
                    "symbol": "BBB",
                    "long_name": "BBB Corp",
                    "sector": "Technology",
                    "industry": "Software",
                    "market_cap": 300,
                },
                {
                    "symbol": "CCC",
                    "long_name": "CCC Corp",
                    "sector": "Healthcare",
                    "industry": "Medical Devices",
                    "market_cap": 200,
                },
                {
                    "symbol": "DDD",
                    "long_name": "DDD Corp",
                    "sector": "Energy",
                    "industry": "Oil & Gas",
                    "market_cap": 100,
                },
            ]
        if "COALESCE(adj_close, close) AS price" in sql:
            return [
                {"symbol": "AAA", "date": "2026-05-15", "price": 100.0},
                {"symbol": "AAA", "date": "2026-05-18", "price": 110.0},
                {"symbol": "AAA", "date": "2026-04-17", "price": 100.0},
                {"symbol": "BBB", "date": "2026-05-15", "price": 100.0},
                {"symbol": "BBB", "date": "2026-05-18", "price": 130.0},
                {"symbol": "BBB", "date": "2026-04-17", "price": 100.0},
                {"symbol": "CCC", "date": "2026-05-15", "price": 100.0},
                {"symbol": "CCC", "date": "2026-05-18", "price": 120.0},
                {"symbol": "CCC", "date": "2026-04-17", "price": 100.0},
                {"symbol": "DDD", "date": "2026-05-18", "price": 140.0},
            ]
        return []

    def test_effective_market_date_skips_sparse_latest_raw_date(self) -> None:
        from app.services.overview_market_intelligence import resolve_effective_market_dates

        window = resolve_effective_market_dates(
            period="daily",
            min_price_rows=1000,
            today=date(2026, 5, 28),
            query_fn=self._query_fn,
        )

        self.assertEqual(window["status"], "OK")
        self.assertEqual(window["latest_raw_date"], "2026-05-19")
        self.assertEqual(window["effective_end_date"], "2026-05-18")
        self.assertEqual(window["start_date"], "2026-05-15")
        self.assertEqual(window["stale_days"], 10)

    def test_market_movers_snapshot_ranks_returnable_symbols_and_reports_gaps(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_limit=100,
            period="daily",
            top_n=5,
            today=date(2026, 5, 28),
            prefer_intraday=False,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["universe_count"], 4)
        self.assertEqual(snapshot["coverage"]["returnable_count"], 3)
        self.assertEqual(snapshot["coverage"]["missing_count"], 1)
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 30.0)
        self.assertIn("Latest raw price date is sparse", snapshot["warnings"][0])
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Symbol"], "DDD")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Reason"], "missing start price")
        self.assertEqual(
            snapshot["missing_rows"].iloc[0]["Recommended Action"],
            "Refresh daily OHLCV history or inspect previous-close coverage.",
        )

    def test_market_movers_snapshot_uses_sp500_intraday_previous_close_returns(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_code="SP500",
            period="daily",
            top_n=5,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["universe_code"], "SP500")
        self.assertEqual(snapshot["coverage"]["price_mode"], "Intraday Snapshot")
        self.assertEqual(snapshot["coverage"]["coverage_basis"], "Current S&P 500 constituents")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 1)
        self.assertEqual(snapshot["coverage"]["failed_count"], 1)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["status"], "stale")
        self.assertTrue(snapshot["coverage"]["refresh_state"]["refresh_due"])
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 12.0)
        self.assertEqual(snapshot["rows"].iloc[0]["Start Date"], "Previous Close")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Reason"], "missing latest price")
        self.assertEqual(
            snapshot["missing_rows"].iloc[0]["Recommended Action"],
            "Refresh the daily snapshot; if it persists, inspect provider quote coverage.",
        )

    def test_market_movers_snapshot_uses_top1000_intraday_returns(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_code="TOP1000",
            period="daily",
            top_n=5,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["universe_code"], "TOP1000")
        self.assertEqual(snapshot["coverage"]["price_mode"], "Intraday Snapshot")
        self.assertEqual(snapshot["coverage"]["coverage_basis"], "Latest asset_profile.market_cap snapshot")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 1)
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 12.0)
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Reason"], "missing latest price")

    def test_group_leadership_snapshot_uses_monthly_weighted_and_equal_returns(self) -> None:
        from app.services.overview_market_intelligence import build_group_leadership_snapshot

        snapshot = build_group_leadership_snapshot(
            universe_limit=100,
            group_by="sector",
            top_n=5,
            min_group_size=1,
            today=date(2026, 5, 28),
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["date_window"]["period"], "monthly")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 3)
        first_row = snapshot["rows"].iloc[0]
        self.assertEqual(first_row["Group"], "Technology")
        self.assertEqual(first_row["Symbols"], 2)
        self.assertEqual(first_row["Equal Weight Return %"], 20.0)
        self.assertEqual(first_row["Market Cap Weighted Return %"], 25.0)
        self.assertEqual(first_row["Top Symbol"], "BBB")

    def test_market_events_snapshot_reads_fomc_rows_from_db(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        snapshot = build_market_events_snapshot(
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["event_count"], 2)
        self.assertEqual(snapshot["coverage"]["next_event_date"], "2026-06-17")
        self.assertEqual(snapshot["coverage"]["latest_collected_at"], "2026-05-28 02:00")
        self.assertEqual(snapshot["coverage"]["official_count"], 2)
        self.assertEqual(snapshot["coverage"]["estimate_count"], 0)
        self.assertEqual(snapshot["rows"].iloc[0]["Type"], "FOMC_MEETING")
        self.assertEqual(snapshot["rows"].iloc[0]["Date"], "2026-06-17")
        self.assertEqual(snapshot["rows"].iloc[0]["Source Type"], "Official")
        self.assertEqual(snapshot["rows"].iloc[0]["Freshness"], "Official")

    def test_market_events_snapshot_can_read_all_event_types(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        snapshot = build_market_events_snapshot(
            event_type=None,
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["event_type"], "All")
        self.assertEqual(snapshot["coverage"]["event_count"], 3)
        self.assertEqual(snapshot["coverage"]["official_count"], 2)
        self.assertEqual(snapshot["coverage"]["estimate_count"], 1)
        self.assertEqual(snapshot["coverage"]["stale_estimate_count"], 0)
        self.assertEqual(set(snapshot["rows"]["Type"]), {"FOMC_MEETING", "EARNINGS"})
        earnings_row = snapshot["rows"][snapshot["rows"]["Type"] == "EARNINGS"].iloc[0]
        self.assertEqual(earnings_row["Source Type"], "Provider Estimate")
        self.assertEqual(earnings_row["Freshness"], "Current estimate")

    def test_market_events_snapshot_warns_on_stale_earnings_estimates(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, sql, params
            return [
                {
                    "event_date": "2026-07-30",
                    "event_type": "EARNINGS",
                    "symbol": "MSFT",
                    "title": "MSFT Earnings Release",
                    "source": "yfinance_calendar",
                    "source_url": "https://finance.yahoo.com/quote/MSFT/analysis",
                    "confidence": 0.65,
                    "collected_at": "2026-05-01 03:00:00",
                }
            ]

        snapshot = build_market_events_snapshot(
            event_type="EARNINGS",
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["estimate_count"], 1)
        self.assertEqual(snapshot["coverage"]["stale_estimate_count"], 1)
        self.assertEqual(snapshot["rows"].iloc[0]["Freshness"], "Stale estimate")
        self.assertEqual(snapshot["rows"].iloc[0]["Age Days"], 27)
        self.assertIn("Refresh Earnings Calendar", snapshot["warnings"][0])


class MarketIntelligenceIngestionContractTests(unittest.TestCase):
    def test_sp500_snapshot_uses_fast_quote_rows_without_yfinance_download(self) -> None:
        from finance.data import market_intelligence as mi

        members = [
            {"symbol": "AAA"},
            {"symbol": "BBB"},
        ]

        def quote_fetcher(symbols):
            self.assertEqual(symbols, ["AAA", "BBB"])
            return [
                {
                    "symbol": "AAA",
                    "regularMarketPrice": 112.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912000,
                    "regularMarketVolume": 1000,
                    "marketState": "REGULAR",
                },
                {
                    "symbol": "BBB",
                    "regularMarketPrice": 96.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912001,
                    "regularMarketVolume": 2000,
                    "marketState": "REGULAR",
                },
            ]

        written_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        with (
            patch.object(mi, "sync_market_intelligence_tables", return_value=None),
            patch.object(mi, "_load_db_previous_close_map", return_value={}),
            patch.object(mi, "upsert_intraday_snapshot_rows", side_effect=capture_rows),
        ):
            result = mi.collect_and_store_sp500_intraday_snapshot(
                universe_loader=lambda: members,
                quote_fetcher=quote_fetcher,
                quote_batch_size=200,
                method="quote_fast",
                fallback_to_yfinance=False,
            )

        self.assertEqual(result["source"], "yahoo_quote")
        self.assertEqual(result["method"], "quote_fast")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(result["symbols_processed"], 2)
        self.assertEqual(written_rows[0]["source"], "yahoo_quote")
        self.assertAlmostEqual(float(written_rows[0]["return_pct"]), 12.0)
        self.assertAlmostEqual(float(written_rows[1]["return_pct"]), -4.0)

    def test_top_universe_snapshot_writes_top1000_rows(self) -> None:
        from finance.data import market_intelligence as mi

        members = [{"symbol": "AAA"}, {"symbol": "BBB"}]

        def quote_fetcher(symbols):
            self.assertEqual(symbols, ["AAA", "BBB"])
            return [
                {
                    "symbol": "AAA",
                    "regularMarketPrice": 112.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912000,
                    "regularMarketVolume": 1000,
                },
                {
                    "symbol": "BBB",
                    "regularMarketPrice": 96.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912001,
                    "regularMarketVolume": 2000,
                },
            ]

        written_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        with (
            patch.object(mi, "sync_market_intelligence_tables", return_value=None),
            patch.object(mi, "_load_db_previous_close_map", return_value={}),
            patch.object(mi, "upsert_intraday_snapshot_rows", side_effect=capture_rows),
        ):
            result = mi.collect_and_store_market_intraday_snapshot(
                universe_code="TOP1000",
                universe_limit=1000,
                universe_loader=lambda: members,
                quote_fetcher=quote_fetcher,
                quote_batch_size=200,
                method="quote_fast",
                fallback_to_yfinance=False,
            )

        self.assertEqual(result["universe_code"], "TOP1000")
        self.assertEqual(result["universe_limit"], 1000)
        self.assertEqual(result["source"], "yahoo_quote")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(written_rows[0]["universe_code"], "TOP1000")
        self.assertAlmostEqual(float(written_rows[0]["return_pct"]), 12.0)


class MarketIntelligenceEventCalendarContractTests(unittest.TestCase):
    def test_market_event_schema_contains_required_columns(self) -> None:
        from finance.data.db.schema import MARKET_INTELLIGENCE_SCHEMAS

        schema_sql = MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"]

        for column in [
            "event_date",
            "event_type",
            "symbol",
            "title",
            "source",
            "source_url",
            "confidence",
            "collected_at",
            "raw_payload_json",
        ]:
            self.assertIn(column, schema_sql)
        self.assertIn("UNIQUE KEY uk_market_event_key", schema_sql)

    def test_fomc_calendar_parser_uses_final_meeting_day_and_official_links(self) -> None:
        from finance.data import market_intelligence as mi

        html = """
        <div class="panel panel-default">
          <div class="panel-heading"><h4><a id="42828">2026 FOMC Meetings</a></h4></div>
          <div class="row fomc-meeting">
            <div class="fomc-meeting__month"><strong>June</strong></div>
            <div class="fomc-meeting__date">16-17*</div>
            <a href="/newsevents/pressreleases/monetary20260617a.htm">HTML</a>
          </div>
          <div class="row fomc-meeting">
            <div class="fomc-meeting__month"><strong>Apr/May</strong></div>
            <div class="fomc-meeting__date">30-1</div>
          </div>
        </div>
        """

        rows = mi._parse_fomc_calendar_events_from_html(  # noqa: SLF001
            html,
            source_url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            years=[2026],
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["event_date"], "2026-06-17")
        self.assertEqual(rows[0]["event_type"], "FOMC_MEETING")
        self.assertTrue(rows[0]["raw_payload"]["has_summary_of_economic_projections"])
        self.assertEqual(
            rows[0]["raw_payload"]["links"][0]["url"],
            "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260617a.htm",
        )
        self.assertEqual(rows[1]["event_date"], "2026-05-01")

    def test_collect_fomc_calendar_writes_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        with (
            patch.object(
                mi,
                "fetch_fomc_calendar_events",
                return_value=[
                    {
                        "event_date": "2026-06-17",
                        "event_type": "FOMC_MEETING",
                        "symbol": None,
                        "title": "FOMC Meeting: June 16-17*, 2026",
                        "source": mi.FOMC_CALENDAR_SOURCE,
                        "source_url": mi.FOMC_CALENDAR_SOURCE_URL,
                        "confidence": 1.0,
                        "raw_payload": {"meeting_range": "June 16-17*"},
                    }
                ],
            ),
            patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows),
        ):
            result = mi.collect_and_store_fomc_calendar(years=[2026])

        self.assertEqual(result["source"], mi.FOMC_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "FOMC_MEETING")
        self.assertEqual(result["events_found"], 1)
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(result["event_dates"], ["2026-06-17"])
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_yfinance_earnings_calendar_builds_event_rows_for_window(self) -> None:
        from finance.data import market_intelligence as mi

        calendars = {
            "AAA": {
                "Earnings Date": [date(2026, 7, 30)],
                "Earnings Average": 1.23,
                "Revenue Average": 1000000,
            },
            "BBB": {},
        }

        class FakeTicker:
            def __init__(self, symbol: str) -> None:
                self.calendar = calendars[symbol]

        result = mi.fetch_yfinance_earnings_calendar_events(
            ["AAA", "BBB"],
            start_date="2026-05-28",
            lookahead_days=120,
            ticker_factory=FakeTicker,
        )

        self.assertEqual(result["source"], mi.EARNINGS_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "EARNINGS")
        self.assertEqual(result["events_found"], 1)
        self.assertEqual(result["missing_symbols"], ["BBB"])
        row = result["events"][0]
        self.assertEqual(row["event_date"], "2026-07-30")
        self.assertEqual(row["symbol"], "AAA")
        self.assertEqual(row["event_type"], "EARNINGS")
        self.assertEqual(row["confidence"], 0.65)
        self.assertEqual(row["raw_payload"]["provider_calendar"]["Earnings Average"], 1.23)

    def test_collect_earnings_calendar_writes_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        def fake_fetcher(symbols, **kwargs):
            self.assertEqual(symbols, ["AAA", "BBB"])
            self.assertEqual(kwargs["lookahead_days"], 90)
            return {
                "source": mi.EARNINGS_CALENDAR_SOURCE,
                "source_url": mi.EARNINGS_CALENDAR_SOURCE_URL,
                "event_type": "EARNINGS",
                "method": "yfinance_ticker_calendar",
                "start_date": "2026-05-28",
                "end_date": "2026-08-26",
                "symbols_requested": 2,
                "symbols_processed": 2,
                "events": [
                    {
                        "event_date": "2026-07-30",
                        "event_type": "EARNINGS",
                        "symbol": "AAA",
                        "title": "AAA Earnings Release",
                        "source": mi.EARNINGS_CALENDAR_SOURCE,
                        "source_url": "https://finance.yahoo.com/quote/AAA/analysis",
                        "confidence": 0.65,
                        "raw_payload": {"provider": mi.EARNINGS_CALENDAR_SOURCE},
                    }
                ],
                "events_found": 1,
                "missing_symbols": ["BBB"],
                "failed_symbols": [],
            }

        with patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows):
            result = mi.collect_and_store_earnings_calendar(
                symbols=["AAA", "BBB"],
                lookahead_days=90,
                earnings_fetcher=fake_fetcher,
            )

        self.assertEqual(result["source"], mi.EARNINGS_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "EARNINGS")
        self.assertEqual(result["symbol_source"], "manual")
        self.assertEqual(result["events_found"], 1)
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(result["event_dates"], ["2026-07-30"])
        self.assertEqual(result["missing_symbols"], ["BBB"])
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_market_event_upsert_normalizes_payload_and_business_key(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeDb:
            def __init__(self) -> None:
                self.used_dbs: list[str] = []
                self.executemany_calls: list[tuple[str, list[dict[str, object]]]] = []
                self.closed = False

            def use_db(self, db_name: str) -> None:
                self.used_dbs.append(db_name)

            def executemany(self, sql: str, rows: list[dict[str, object]]) -> None:
                self.executemany_calls.append((sql, rows))

            def close(self) -> None:
                self.closed = True

        fake_db = FakeDb()
        with (
            patch.object(mi, "_db", return_value=fake_db),
            patch.object(mi, "sync_table_schema") as sync_schema,
        ):
            rows_written = mi.upsert_market_event_rows(
                [
                    {
                        "event_date": "2026-06-17",
                        "event_type": "fomc meeting",
                        "symbol": "",
                        "title": "FOMC Meeting",
                        "source": "federal_reserve",
                        "source_url": "https://example.test/fomc",
                        "confidence": "0.95",
                        "raw_payload": {"meeting": "June"},
                    }
                ]
            )

        self.assertEqual(rows_written, 1)
        self.assertEqual(fake_db.used_dbs, ["finance_meta"])
        sync_schema.assert_called_once()
        _, captured_rows = fake_db.executemany_calls[0]
        captured = captured_rows[0]
        self.assertEqual(captured["event_date"], "2026-06-17")
        self.assertEqual(captured["event_type"], "FOMC_MEETING")
        self.assertIsNone(captured["symbol"])
        self.assertEqual(captured["confidence"], 0.95)
        self.assertEqual(captured["raw_payload_json"], '{"meeting":"June"}')
        self.assertEqual(len(str(captured["event_key"])), 64)
        self.assertTrue(fake_db.closed)

    def test_market_intelligence_sync_includes_event_calendar_table(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeDb:
            def __init__(self) -> None:
                self.used_dbs: list[str] = []

            def use_db(self, db_name: str) -> None:
                self.used_dbs.append(db_name)

            def close(self) -> None:
                pass

        dbs = [FakeDb(), FakeDb()]

        def fake_db(*args, **kwargs):
            del args, kwargs
            return dbs.pop(0)

        with (
            patch.object(mi, "_db", side_effect=fake_db),
            patch.object(mi, "sync_table_schema") as sync_schema,
        ):
            mi.sync_market_intelligence_tables()

        synced_tables = [call.args[1] for call in sync_schema.call_args_list]
        self.assertIn("market_universe_member", synced_tables)
        self.assertIn("market_event_calendar", synced_tables)
        self.assertIn("market_intraday_snapshot", synced_tables)


class PracticalValidationReplayServiceContractTests(unittest.TestCase):
    def test_recheck_plan_extends_to_latest_market_date(self) -> None:
        from app.services import backtest_practical_validation_replay as replay_service

        source = {
            "selection_source_id": "source-replay",
            "period": {"actual_start": "2020-01-31", "actual_end": "2020-12-31"},
        }

        with patch.object(replay_service, "load_latest_market_date", return_value="2021-01-08"):
            plan = replay_service.build_practical_validation_recheck_plan(source)

        self.assertEqual(plan["mode"], replay_service.RECHECK_MODE_EXTEND_TO_LATEST)
        self.assertEqual(plan["status"], "EXTENDED")
        self.assertEqual(plan["stored_period"], {"start": "2020-01-31", "end": "2020-12-31"})
        self.assertEqual(plan["requested_period"], {"start": "2020-01-31", "end": "2021-01-08"})
        self.assertEqual(plan["latest_market_date"], "2021-01-08")
        self.assertEqual(plan["extension_days"], 8)
        self.assertEqual(plan["curve_source"], "actual_runtime_latest_recheck")

    def test_recheck_plan_stored_period_does_not_query_latest_market_date(self) -> None:
        from app.services import backtest_practical_validation_replay as replay_service

        source = {
            "selection_source_id": "source-replay",
            "period": {"start": "2020-01-31", "end": "2020-12-31"},
        }

        with patch.object(replay_service, "load_latest_market_date") as load_latest:
            plan = replay_service.build_practical_validation_recheck_plan(
                source,
                mode=replay_service.RECHECK_MODE_STORED_PERIOD,
            )

        load_latest.assert_not_called()
        self.assertEqual(plan["mode"], replay_service.RECHECK_MODE_STORED_PERIOD)
        self.assertEqual(plan["status"], "STORED_PERIOD")
        self.assertEqual(plan["requested_period"], {"start": "2020-01-31", "end": "2020-12-31"})
        self.assertFalse(plan["uses_latest_db_date"])
        self.assertEqual(plan["curve_source"], "actual_runtime_replay")

    def test_actual_replay_returns_blocked_contract_when_source_period_is_missing(self) -> None:
        from app.services import backtest_practical_validation_replay as replay_service

        result = replay_service.run_practical_validation_actual_replay(
            {"selection_source_id": "source-missing-period", "components": []}
        )

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["source_id"], "source-missing-period")
        self.assertEqual(result["recheck_plan"]["status"], "BLOCKED")
        self.assertEqual(result["period_coverage"]["status"], "BLOCKED")
        self.assertEqual(result["portfolio_curve"], [])
        self.assertEqual(result["benchmark_curve"], [])


class ProviderGapCollectionServiceContractTests(unittest.TestCase):
    def _validation_result(self) -> dict[str, object]:
        return {
            "selection_source_id": "source-provider-gap",
            "provider_coverage": {
                "symbols": ["SPY", "TLT", "XYZ"],
                "symbol_weights": {"SPY": 0.6, "TLT": 0.3, "XYZ": 0.1},
                "coverage": {
                    "operability": {"missing_symbols": ["SPY", "XYZ"]},
                    "holdings": {"missing_symbols": ["SPY", "XYZ"]},
                    "exposure": {"missing_symbols": ["SPY", "XYZ"]},
                    "macro": {
                        "diagnostic_status": "REVIEW",
                        "series_count": 2,
                        "stale_count": 1,
                    },
                },
            },
        }

    def test_provider_gap_rows_and_plan_are_built_without_ui_runtime(self) -> None:
        from app.services import backtest_practical_validation as service

        verified_rows = [
            {"symbol": "SPY", "data_kind": "operability", "provider": "ishares", "parser": "factsheet"},
            {"symbol": "SPY", "data_kind": "holdings", "provider": "ishares", "parser": "holdings_csv"},
            {"symbol": "SPY", "data_kind": "exposure", "provider": "ishares", "parser": "provider_aggregate"},
        ]

        with patch.object(service, "load_etf_provider_source_map", return_value=verified_rows):
            rows = service.build_provider_gap_rows(self._validation_result())
            plan = service.build_provider_gap_collection_plan(self._validation_result())

        rows_by_symbol = {row["ETF"]: row for row in rows}
        self.assertEqual(rows_by_symbol["SPY"]["Action"], "운용성 보강, holdings/exposure 수집")
        self.assertEqual(rows_by_symbol["TLT"]["Action"], "조치 없음")
        self.assertEqual(rows_by_symbol["XYZ"]["Action"], "운용성 보강, source map 자동 탐색")
        self.assertEqual(plan["source_map_discovery"], ["XYZ"])
        self.assertEqual(plan["operability_official"], ["SPY"])
        self.assertEqual(plan["operability_bridge"], ["SPY", "XYZ"])
        self.assertEqual(plan["holdings_exposure"], ["SPY"])
        self.assertTrue(plan["macro"])
        self.assertEqual(
            service.provider_gap_state_key(self._validation_result()),
            "practical_validation_provider_gap_results_source-provider-gap",
        )

    def test_provider_gap_collection_runs_planned_jobs_and_records_history(self) -> None:
        from app.services import backtest_practical_validation as service

        first_plan = {
            "source_map_discovery": ["XYZ"],
            "source_symbols": ["SPY", "XYZ"],
            "operability_official": [],
            "operability_bridge": [],
            "holdings_exposure": [],
            "mapping_needed": [],
            "macro": False,
        }
        second_plan = {
            "source_map_discovery": [],
            "source_symbols": ["SPY", "XYZ"],
            "operability_official": ["SPY"],
            "operability_bridge": ["SPY", "XYZ"],
            "holdings_exposure": ["SPY"],
            "mapping_needed": [],
            "macro": True,
        }

        def result(job_name: str, symbols_requested: int | None = 1) -> dict[str, object]:
            return {
                "job_name": job_name,
                "status": "success",
                "rows_written": 1,
                "symbols_requested": symbols_requested,
                "failed_symbols": [],
                "message": "ok",
            }

        with (
            patch.object(
                service,
                "build_provider_gap_collection_plan",
                side_effect=[first_plan, second_plan],
            ) as build_plan,
            patch.object(
                service,
                "run_discover_etf_provider_source_map",
                return_value=result("discover"),
            ) as discover,
            patch.object(
                service,
                "run_collect_etf_operability_provider",
                side_effect=[result("operability_official"), result("operability_bridge", 2)],
            ) as operability,
            patch.object(
                service,
                "run_collect_etf_holdings_exposure",
                return_value=result("holdings_exposure"),
            ) as holdings,
            patch.object(
                service,
                "run_collect_macro_market_context",
                return_value=result("macro", None),
            ) as macro,
            patch.object(service, "append_run_history") as append_history,
        ):
            results = service.run_provider_gap_collection(self._validation_result())

        self.assertEqual(build_plan.call_count, 2)
        discover.assert_called_once_with(["SPY", "XYZ"], verify=True)
        operability.assert_any_call(
            ["SPY"],
            provider="official",
            as_of_date=None,
            lookback_days=60,
            timeframe="1d",
        )
        operability.assert_any_call(
            ["SPY", "XYZ"],
            provider="db_bridge",
            as_of_date=None,
            lookback_days=60,
            timeframe="1d",
        )
        holdings.assert_called_once_with(
            ["SPY"],
            provider="official",
            as_of_date=None,
            include_provider_aggregates=True,
            refresh_mode="canonical_refresh",
        )
        macro.assert_called_once_with()
        self.assertEqual(len(results), 5)
        self.assertEqual(append_history.call_count, 5)
        provider_areas = [
            result["run_metadata"]["input_params"]["provider_area"]
            for result in results
        ]
        self.assertEqual(
            provider_areas,
            [
                "etf_provider_source_map",
                "etf_operability_official",
                "etf_operability_db_bridge",
                "etf_holdings_exposure",
                "macro_context",
            ],
        )
        self.assertTrue(
            all(
                result["run_metadata"]["pipeline_type"]
                == "practical_validation_provider_gap_collection"
                for result in results
            )
        )


class FinalReviewEvidenceReadModelContractTests(unittest.TestCase):
    def test_status_display_uses_current_decision_routes(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_status_display

        selected = build_final_review_status_display(
            {"decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO"}
        )
        rejected = build_final_review_status_display({"decision_route": "REJECT_FOR_PRACTICAL_USE"})

        self.assertEqual(selected["route"], "FINAL_REVIEW_DECISION_COMPLETE")
        self.assertIn("next_action", selected)
        self.assertEqual(rejected["route"], "FINAL_REVIEW_REJECTED")

    def test_status_display_keeps_legacy_handoff_route_as_fallback(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_status_display

        status = build_final_review_status_display(
            {"phase35_handoff": {"handoff_route": "LEGACY_COMPLETE"}}
        )

        self.assertEqual(status["route"], "LEGACY_COMPLETE")
        self.assertIn("next_action", status)

    def test_decision_display_rows_keep_table_contract(self) -> None:
        from app.services.backtest_evidence_read_model import (
            build_final_review_decision_display_rows,
        )

        rows = build_final_review_decision_display_rows(
            [
                {
                    "updated_at": "2026-05-20T10:00:00",
                    "decision_id": "decision-1",
                    "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "source_type": "proposal",
                    "source_id": "proposal-1",
                    "selected_components": [{"ticker": "SPY"}, {"ticker": "TLT"}],
                    "decision_evidence_snapshot": {"route": "READY", "score": 92},
                }
            ]
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["Updated At"], "2026-05-20T10:00:00")
        self.assertEqual(row["Decision ID"], "decision-1")
        self.assertEqual(row["Source"], "proposal / proposal-1")
        self.assertEqual(row["Components"], 2)
        self.assertEqual(row["Evidence Route"], "READY")
        self.assertEqual(row["Evidence Score"], 92)
        self.assertEqual(row["Final Status"], "FINAL_REVIEW_DECISION_COMPLETE")
        self.assertEqual(row["Live Approval"], "Disabled")

    def test_evidence_rows_expand_current_and_wrapped_decision_shapes(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_decision_evidence_rows

        decision = {
            "decision_evidence_snapshot": {
                "checks": [
                    {
                        "criteria": "Evidence route",
                        "ready": True,
                        "current": "READY",
                        "meaning": "Reusable final review evidence",
                        "score": 1,
                    }
                ]
            },
            "risk_and_validation_snapshot": {
                "validation_checks": [
                    {
                        "Criteria": "Validation status",
                        "Ready": False,
                        "Current": "REVIEW",
                    }
                ],
                "robustness_validation": {
                    "checks": [{"criteria": "Robustness status", "current_value": "WATCH"}]
                },
            },
            "paper_tracking_snapshot": {
                "checks": [{"criteria": "Paper status", "current": "OPTIONAL"}]
            },
        }

        rows = build_final_decision_evidence_rows({"raw_decision": decision})

        self.assertEqual(
            [row["Area"] for row in rows],
            [
                "Final Review Evidence",
                "Validation",
                "Robustness",
                "Paper Observation",
            ],
        )
        self.assertEqual(rows[0]["Criteria"], "Evidence route")
        self.assertTrue(rows[0]["Ready"])
        self.assertEqual(rows[1]["Current"], "REVIEW")
        self.assertEqual(rows[2]["Current"], "WATCH")
        self.assertEqual(rows[3]["Current"], "OPTIONAL")


if __name__ == "__main__":
    unittest.main()
