from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
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


class ProviderContextProvenanceContractTests(unittest.TestCase):
    def test_provider_context_exposes_compact_provenance_and_downgrades_stale_pass(self) -> None:
        from app.services import backtest_practical_validation_provider_context as provider_context

        operability = pd.DataFrame(
            [
                {
                    "symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "expense_ratio": 0.0009,
                    "net_assets": 500_000_000_000,
                    "avg_daily_dollar_volume": 3_000_000_000,
                    "bid_ask_spread_pct": 0.0001,
                    "premium_discount_pct": 0.0002,
                },
                {
                    "symbol": "TLT",
                    "as_of_date": "2026-03-01",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-03-02",
                    "expense_ratio": 0.0015,
                    "net_assets": 50_000_000_000,
                    "avg_daily_dollar_volume": 500_000_000,
                    "bid_ask_spread_pct": 0.0002,
                    "premium_discount_pct": 0.0001,
                },
            ]
        )
        holdings = pd.DataFrame(
            [
                {
                    "fund_symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "holding_id": "AAPL",
                    "holding_symbol": "AAPL",
                    "holding_name": "Apple Inc",
                    "weight_pct": 5.0,
                },
                {
                    "fund_symbol": "TLT",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "holding_id": "UST",
                    "holding_symbol": "UST",
                    "holding_name": "US Treasury",
                    "weight_pct": 5.0,
                },
            ]
        )
        exposure = pd.DataFrame(
            [
                {
                    "fund_symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "exposure_type": "asset_class",
                    "exposure_name": "Equity",
                    "weight_pct": 100.0,
                },
                {
                    "fund_symbol": "TLT",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "exposure_type": "asset_class",
                    "exposure_name": "Treasury Bond",
                    "weight_pct": 100.0,
                },
            ]
        )
        macro = pd.DataFrame(
            [
                {
                    "series_id": "VIXCLS",
                    "observation_date": "2026-05-27",
                    "source": "fred",
                    "source_type": "official",
                    "source_mode": "csv",
                    "coverage_status": "actual",
                    "value": 18.0,
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                    "collected_at": "2026-05-28",
                },
                {
                    "series_id": "T10Y3M",
                    "observation_date": "2026-05-27",
                    "source": "fred",
                    "source_type": "official",
                    "source_mode": "csv",
                    "coverage_status": "actual",
                    "value": 0.7,
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                    "collected_at": "2026-05-28",
                },
                {
                    "series_id": "BAA10Y",
                    "observation_date": "2026-05-27",
                    "source": "fred",
                    "source_type": "official",
                    "source_mode": "csv",
                    "coverage_status": "actual",
                    "value": 2.0,
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                    "collected_at": "2026-05-28",
                },
            ]
        )

        with (
            patch.object(provider_context, "load_etf_operability_snapshot", return_value=operability),
            patch.object(provider_context, "load_etf_holdings_snapshot", return_value=holdings),
            patch.object(provider_context, "load_etf_exposure_snapshot", return_value=exposure),
            patch.object(provider_context, "load_macro_snapshot", return_value=macro),
        ):
            context = provider_context.build_provider_context(
                {"SPY": 70.0, "TLT": 30.0},
                as_of_date="2026-05-28",
                max_provider_staleness_days=45,
                max_macro_staleness_days=10,
            )

        self.assertEqual(context["schema_version"], 2)
        operability_context = context["coverage"]["operability"]
        provenance = operability_context["provenance"]
        self.assertEqual(operability_context["status"], "actual")
        self.assertEqual(operability_context["diagnostic_status"], "REVIEW")
        self.assertEqual(provenance["freshness_status"], "stale")
        self.assertEqual(provenance["stale_symbols"], ["TLT"])
        self.assertEqual(provenance["stale_weight"], 30.0)
        self.assertEqual(provenance["source_type_weights"], {"official": 100.0})
        self.assertEqual(provenance["coverage_status_weights"], {"actual": 100.0})
        self.assertEqual(provenance["as_of_range"], "2026-03-01..2026-05-20")

        board = context["look_through_board"]
        self.assertEqual(board["schema_version"], "look_through_board_v1")
        self.assertEqual(board["status"], "PASS")
        self.assertEqual(board["holdings_coverage_weight"], 100.0)
        self.assertEqual(board["exposure_coverage_weight"], 100.0)
        self.assertEqual(board["top_holding_weight"], 3.5)
        self.assertEqual(board["dominant_asset_bucket"], "equity")
        self.assertEqual(board["dominant_asset_weight"], 70.0)
        asset_rows_by_bucket = {row["Asset Bucket"]: row for row in board["asset_bucket_rows"]}
        self.assertEqual(asset_rows_by_bucket["equity"]["Portfolio Weight"], 70.0)
        self.assertEqual(asset_rows_by_bucket["bond"]["Portfolio Weight"], 30.0)
        fund_rows_by_symbol = {row["Symbol"]: row for row in board["fund_coverage_rows"]}
        self.assertEqual(fund_rows_by_symbol["SPY"]["Holdings Freshness"], "fresh")
        self.assertEqual(fund_rows_by_symbol["TLT"]["Exposure Coverage"], "actual")

        rows_by_area = {row["Area"]: row for row in context["display_rows"]}
        self.assertEqual(rows_by_area["ETF Operability"]["Freshness"], "stale")
        self.assertEqual(rows_by_area["ETF Operability"]["Source Mix"], "official 100.0%")
        self.assertEqual(rows_by_area["Macro Context"]["Freshness"], "fresh")
        self.assertIn("fred/csv", rows_by_area["Macro Context"]["Source Mix"])


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
                "provider_look_through_board": {
                    "summary_rows": [
                        {
                            "Check": "Holdings Coverage",
                            "Status": "PASS",
                            "Current": "100.0%",
                            "Evidence": "fresh / official 100.0% / 2026-05-20",
                            "Meaning": "holdings coverage compact summary",
                        }
                    ]
                },
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
                "Look-through Exposure",
                "Robustness",
                "Paper Observation",
            ],
        )
        self.assertEqual(rows[0]["Criteria"], "Evidence route")
        self.assertTrue(rows[0]["Ready"])
        self.assertEqual(rows[1]["Current"], "REVIEW")
        self.assertEqual(rows[2]["Criteria"], "Holdings Coverage")
        self.assertTrue(rows[2]["Ready"])
        self.assertEqual(rows[3]["Current"], "WATCH")
        self.assertEqual(rows[4]["Current"], "OPTIONAL")

    def test_investability_packet_ready_contract_is_ui_neutral(self) -> None:
        from app.services.backtest_evidence_read_model import build_investability_evidence_packet

        validation = {
            "selection_source_id": "source-ready",
            "validation_id": "validation-ready",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "diagnostic_summary": {"status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}},
            "checks": [
                {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
            ],
            "provider_coverage": {
                "coverage": {
                    "holdings": {"diagnostic_status": "PASS"},
                    "operability": {"diagnostic_status": "PASS"},
                }
            },
            "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-ready"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["source_chain"]["selection_source_id"], "source-ready")
        self.assertEqual(packet["summary"]["not_run"], 0)
        self.assertEqual(packet["critical_gaps"], [])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(packet["gate_policy_snapshot"]["select_allowed"])
        assumptions = [row["Assumption"] for row in packet["assumptions_and_limits"]]
        self.assertIn("Hypothetical backtest", assumptions)
        self.assertIn("No live approval / order", assumptions)

    def test_investability_packet_blocks_selected_route_on_critical_not_run(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-gap"},
            validation={
                "selection_source_id": "source-gap",
                "validation_id": "validation-gap",
                "diagnostic_summary": {"status_counts": {"PASS": 10, "REVIEW": 1, "BLOCKED": 0, "NOT_RUN": 1}},
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "REVIEW"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "not_run_critical_domains": [
                    {
                        "domain": "stress_scenario_diagnostics",
                        "title": "7. Stress / Scenario Diagnostics",
                        "next_action": "daily replay evidence 필요",
                    }
                ],
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )

        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertFalse(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertTrue(packet["gate_policy_snapshot"]["waiver_required_for_select"])
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])

    def test_gate_policy_blocks_selected_route_on_provider_review_for_balanced_profile(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-provider-review"},
            validation={
                "selection_source_id": "source-provider-review",
                "validation_id": "validation-provider-review",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 11, "REVIEW": 1, "BLOCKED": 0, "NOT_RUN": 0}
                },
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "REVIEW"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "title": "10. Operability / Cost / Liquidity",
                        "status": "REVIEW",
                        "next_action": "provider actual evidence 보강",
                    }
                ],
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_NEEDS_REVIEW")
        self.assertFalse(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "hold_or_re_review")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(
            any(
                row["Group"] == "provider_coverage" and row["Severity"] == "REVIEW_REQUIRED"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_final_review_save_evaluation_uses_investability_packet_gate(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_save_evaluation

        blocked_packet = {
            "route": "INVESTABILITY_PACKET_BLOCKED",
            "select_ready": False,
        }
        selected = _build_final_review_save_evaluation(
            evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=blocked_packet,
            decision_id="decision-packet-blocked",
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            operator_reason="reason attached",
            existing_decision_ids=set(),
        )
        hold = _build_final_review_save_evaluation(
            evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=blocked_packet,
            decision_id="decision-packet-hold",
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            operator_reason="reason attached",
            existing_decision_ids=set(),
        )

        self.assertFalse(selected["can_save"])
        self.assertIn("Investability evidence packet", selected["blockers"])
        self.assertTrue(hold["can_save"])

    def test_final_review_decision_row_stores_compact_gate_policy_snapshot(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_decision_row

        packet = {
            "route": "INVESTABILITY_PACKET_READY",
            "select_ready": True,
            "gate_policy_snapshot": {
                "schema_version": "investability_gate_policy_v1",
                "outcome": "select_ready",
                "select_allowed": True,
                "policy_rows": [
                    {
                        "Criteria": "Benchmark Parity",
                        "Group": "benchmark",
                        "Ready": True,
                        "Severity": "PASS",
                    }
                ],
            },
        }

        row = _build_final_review_decision_row(
            source={"source_id": "source-row", "source_type": "practical_validation_result"},
            validation={"selection_source_id": "source-row", "validation_id": "validation-row"},
            paper_observation={"active_components": [], "checks": []},
            evidence={"route": "READY_FOR_FINAL_DECISION", "checks": [], "blockers": []},
            investability_packet=packet,
            decision_id="decision-row",
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            operator_reason="reason",
            operator_constraints="constraints",
            operator_next_action="next",
        )

        self.assertEqual(row["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(row["gate_policy_snapshot"]["policy_rows"][0]["Group"], "benchmark")


if __name__ == "__main__":
    unittest.main()
