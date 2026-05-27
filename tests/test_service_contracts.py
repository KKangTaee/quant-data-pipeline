from __future__ import annotations

import subprocess
import sys
import unittest
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
