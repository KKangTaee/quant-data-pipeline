from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


def _macro_regime_rows(
    dates: pd.DatetimeIndex,
    *,
    source_type: str = "official",
    coverage_status: str = "actual",
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for idx, date in enumerate(dates):
        if idx < 24:
            vix, curve, credit = 15.0, 1.2, 2.0
        elif idx < 42:
            vix, curve, credit = 22.0, 0.4, 2.6
        else:
            vix, curve, credit = 35.0, -0.2, 3.2
        for series_id, value in (("VIXCLS", vix), ("T10Y3M", curve), ("BAA10Y", credit)):
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": date,
                    "source": "fred",
                    "source_type": source_type,
                    "source_mode": "csv_download",
                    "category": "market_context",
                    "coverage_status": coverage_status,
                    "value": value,
                }
            )
    return pd.DataFrame(rows)


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

    def test_selection_source_preserves_cost_and_turnover_snapshots_without_new_registry(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_candidate_draft

        source = build_selection_source_from_candidate_draft(
            {
                "source_kind": "latest_backtest_run",
                "strategy_key": "equal_weight",
                "strategy_name": "Equal Weight",
                "result_snapshot": {
                    "start_date": "2020-01-31",
                    "end_date": "2024-12-31",
                    "cagr": 0.1,
                    "maximum_drawdown": -0.2,
                    "sharpe_ratio": 1.0,
                    "end_balance": 1500.0,
                },
                "settings_snapshot": {
                    "tickers": ["SPY", "TLT"],
                    "rebalance_interval": 1,
                    "transaction_cost_bps": 10.0,
                },
                "cost_model_snapshot": {
                    "cost_model_contract_version": "cost_model_source_contract_v1",
                    "cost_application_status": "applied_to_result_curve",
                    "transaction_cost_bps": 10.0,
                    "estimated_cost_total": 42.0,
                },
                "turnover_evidence_snapshot": {
                    "turnover_model_contract_version": "turnover_evidence_contract_v1",
                    "turnover_estimation_status": "estimated_from_holdings",
                    "turnover_source": "end_next_holdings_weight_delta",
                    "turnover_observation_count": 12,
                    "turnover_rebalance_rows": 12,
                    "avg_turnover": 0.2,
                },
                "net_cost_curve_snapshot": {
                    "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                    "net_cost_curve_status": "applied_with_measurable_cost",
                    "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                    "total_balance_is_net_of_cost": True,
                    "net_cost_curve_rows": 12,
                    "estimated_cost_total": 42.0,
                    "estimated_cost_positive_rows": 12,
                    "gross_end_balance": 1542.0,
                    "net_end_balance": 1500.0,
                    "gross_net_end_balance_delta": 42.0,
                },
            }
        )

        self.assertEqual(
            source["cost_model_snapshot"]["cost_application_status"],
            "applied_to_result_curve",
        )
        self.assertEqual(
            source["components"][0]["replay_contract"]["cost_model_snapshot"]["estimated_cost_total"],
            42.0,
        )
        self.assertEqual(
            source["turnover_evidence_snapshot"]["turnover_estimation_status"],
            "estimated_from_holdings",
        )
        self.assertEqual(
            source["components"][0]["replay_contract"]["turnover_evidence_snapshot"]["avg_turnover"],
            0.2,
        )
        self.assertEqual(
            source["net_cost_curve_snapshot"]["net_cost_curve_status"],
            "applied_with_measurable_cost",
        )
        self.assertEqual(
            source["components"][0]["replay_contract"]["net_cost_curve_snapshot"][
                "gross_net_end_balance_delta"
            ],
            42.0,
        )
        self.assertEqual(source["construction"]["rebalance_cadence"], 1)

    def test_service_imports_do_not_load_streamlit(self) -> None:
        script = """
import sys
import app.runtime
import app.runtime.backtest
import app.runtime.candidate_library
import app.runtime.backtest_result_bundle
import app.services.backtest_construction_risk_audit
import app.services.backtest_data_coverage_audit
import app.services.backtest_realism_audit
import app.services.backtest_evidence_read_model
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_diagnostics
import app.services.backtest_practical_validation
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_replay
import app.services.backtest_practical_validation_source
import app.services.backtest_validation_efficacy
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
import app.services.backtest_data_coverage_audit
import app.services.backtest_realism_audit
import app.services.backtest_construction_risk_audit
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_curve_context
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_stress_sensitivity
import app.services.backtest_practical_validation_source
import app.services.backtest_temporal_validation
import app.services.backtest_validation_efficacy
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


class ConstructionRiskAuditContractTests(unittest.TestCase):
    def _validation_with_board(self, board: dict) -> dict:
        return {
            "validation_profile": {
                "profile_id": "balanced_core",
                "thresholds": {"max_weight_review": 75.0},
            },
            "metrics": {
                "active_components": 2,
                "weight_total": 100.0,
                "max_weight": 60.0,
            },
            "diagnostic_results": [
                {
                    "domain": "concentration_overlap_exposure",
                    "status": "PASS",
                    "summary": "component concentration and provider look-through available",
                }
            ],
            "provider_coverage": {
                "look_through_board": board,
            },
        }

    def test_ready_audit_uses_provider_look_through_without_writes(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            CONSTRUCTION_RISK_READY,
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            self._validation_with_board(
                {
                    "schema_version": "look_through_board_v1",
                    "status": "PASS",
                    "summary": "Provider look-through board status PASS.",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "top_holding_weight": 3.5,
                    "top_overlap_weight": 2.0,
                    "dominant_asset_bucket": "equity",
                    "dominant_asset_weight": 60.0,
                    "unknown_exposure_weight": 0.0,
                }
            )
        )

        self.assertEqual(audit["route"], CONSTRUCTION_RISK_READY)
        self.assertEqual(audit["source_strength"], "provider_backed")
        self.assertEqual(audit["metrics"]["pass"], 6)
        self.assertEqual(audit["metrics"]["holdings_coverage_weight"], 100.0)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def test_missing_provider_coverage_is_not_ready_even_with_proxy_diagnostic(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            CONSTRUCTION_RISK_NEEDS_INPUT,
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            {
                "metrics": {
                    "active_components": 2,
                    "weight_total": 100.0,
                    "max_weight": 50.0,
                },
                "diagnostic_results": [
                    {
                        "domain": "concentration_overlap_exposure",
                        "status": "PASS",
                        "summary": "proxy concentration did not exceed threshold",
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], CONSTRUCTION_RISK_NEEDS_INPUT)
        self.assertEqual(audit["source_strength"], "proxy_only")
        self.assertEqual(rows_by_criteria["Provider look-through coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Top holding concentration"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Asset bucket exposure"]["Status"], "NEEDS_INPUT")

    def test_top_holding_overlap_and_unknown_exposure_trigger_review(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            CONSTRUCTION_RISK_REVIEW,
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            self._validation_with_board(
                {
                    "schema_version": "look_through_board_v1",
                    "status": "PASS",
                    "summary": "Provider look-through board status PASS.",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "top_holding_weight": 30.0,
                    "top_overlap_weight": 22.0,
                    "dominant_asset_bucket": "equity",
                    "dominant_asset_weight": 70.0,
                    "unknown_exposure_weight": 4.0,
                }
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], CONSTRUCTION_RISK_REVIEW)
        self.assertEqual(rows_by_criteria["Top holding concentration"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Holdings overlap"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Asset bucket exposure"]["Status"], "REVIEW")


class ValidationEfficacyAuditContractTests(unittest.TestCase):
    def test_ready_audit_uses_compact_evidence_without_writes(self) -> None:
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_READY,
            build_validation_efficacy_audit,
        )

        audit = build_validation_efficacy_audit(
            {
                "selection_source_id": "source-ready",
                "checks": [
                    {"Criteria": "Selection source", "Ready": True, "Current": "source-ready"},
                    {"Criteria": "Active components", "Ready": True, "Current": "3"},
                    {"Criteria": "Target weight total", "Ready": True, "Current": "100.00%"},
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "portfolio_curve_rows": 120,
                    "curve_provenance": {
                        "portfolio_curve_source": "actual_runtime_replay",
                        "portfolio_curve_rows": 120,
                        "runtime_recheck_status": "PASS",
                        "runtime_recheck_id": "replay-1",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                        "actual_period": {"start": "2020-01-31", "end": "2026-05-20"},
                        "requested_period": {"start": "2020-01-31", "end": "2026-05-20"},
                    },
                    "period_coverage": {
                        "status": "PASS",
                        "actual_period": {"start": "2020-01-31", "end": "2026-05-20"},
                        "requested_period": {"start": "2020-01-31", "end": "2026-05-20"},
                    },
                    "benchmark_parity": {
                        "status": "PASS",
                        "metrics": {"coverage_ratio": 1.0, "same_period": True, "same_frequency": True},
                    },
                },
                "temporal_validation": {
                    "status": "PASS",
                    "summary": "36M walk-forward 12 windows: worst excess 2.00%.",
                    "metrics": {
                        "window_count": 12,
                        "worst_rolling_excess_return": 0.02,
                        "negative_excess_window_share": 0.0,
                        "worst_drawdown_gap": 0.0,
                        "portfolio_curve_source": "actual_runtime_replay",
                    },
                },
                "oos_holdout_validation": {
                    "status": "PASS",
                    "summary": "OOS holdout: out excess 3.00%, drawdown gap 0.00%.",
                    "metrics": {
                        "in_sample_months": 30,
                        "out_sample_months": 30,
                        "out_sample_excess_return": 0.03,
                        "excess_change": 0.0,
                        "out_sample_drawdown_gap": 0.0,
                    },
                },
                "regime_split_validation": {
                    "status": "PASS",
                    "summary": "Regime split 3 buckets / 59 months: worst excess 1.00%.",
                    "metrics": {
                        "regime_bucket_count": 3,
                        "common_months": 59,
                        "stress_regime_months": 36,
                        "worst_regime_excess_return": 0.01,
                        "worst_regime_drawdown_gap": 0.0,
                        "macro_source": "finance.loaders.macro.load_macro_series_observations",
                    },
                },
                "provider_coverage_display_rows": [
                    {"Area": "ETF Operability", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "ETF Holdings", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "ETF Exposure", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "Macro Context", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "robustness_validation": {
                    "robustness_route": "READY_FOR_STRESS_SWEEP",
                    "robustness_lab_board": {"status": "PASS", "summary": "stress / rolling / sensitivity attached"},
                },
                "survivorship_control": {"status": "controlled"},
                "diagnostic_summary": {"status_counts": {"NOT_RUN": 0}},
            }
        )

        self.assertEqual(audit["route"], VALIDATION_EFFICACY_READY)
        self.assertEqual(audit["metrics"]["pass"], 13)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def test_walkforward_temporal_validation_uses_benchmark_aligned_windows(self) -> None:
        from app.services.backtest_temporal_validation import build_walkforward_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        portfolio["Total Return"] = portfolio["Total Balance"].pct_change().fillna(0.0)
        benchmark["Total Return"] = benchmark["Total Balance"].pct_change().fillna(0.0)

        evidence = build_walkforward_validation(
            portfolio,
            benchmark,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
            window_months=12,
        )

        self.assertEqual(evidence["schema_version"], "walkforward_validation_contract_v1")
        self.assertEqual(evidence["status"], "PASS")
        self.assertGreater(evidence["metrics"]["window_count"], 3)
        self.assertGreaterEqual(evidence["metrics"]["worst_rolling_excess_return"], 0.0)
        self.assertFalse(evidence["registry_write"])
        self.assertFalse(evidence["memo_persistence"])

    def test_walkforward_temporal_validation_does_not_pass_short_or_proxy_only_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_walkforward_validation

        short_dates = pd.date_range("2023-01-31", periods=10, freq="ME")
        short_curve = pd.DataFrame(
            {
                "Date": short_dates,
                "Total Balance": [100.0 + idx for idx in range(len(short_dates))],
                "Total Return": [0.0] + [0.01] * (len(short_dates) - 1),
            }
        )
        short_evidence = build_walkforward_validation(
            short_curve,
            short_curve,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
            window_months=12,
        )

        self.assertEqual(short_evidence["status"], "NEEDS_INPUT")

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        proxy_portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_evidence = build_walkforward_validation(
            proxy_portfolio,
            proxy_benchmark,
            portfolio_curve_source="component_curve_weighted_proxy",
            benchmark_curve_source="db_price_proxy",
            benchmark_parity={"status": "PASS"},
            window_months=12,
        )

        self.assertEqual(proxy_evidence["status"], "REVIEW")
        self.assertTrue(proxy_evidence["metrics"]["proxy_evidence"])

    def test_oos_holdout_validation_uses_out_sample_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_oos_holdout_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )

        evidence = build_oos_holdout_validation(
            portfolio,
            benchmark,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(evidence["schema_version"], "oos_holdout_validation_contract_v1")
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["metrics"]["in_sample_months"], 30)
        self.assertEqual(evidence["metrics"]["out_sample_months"], 30)
        self.assertGreaterEqual(evidence["metrics"]["out_sample_excess_return"], 0.0)
        self.assertFalse(evidence["registry_write"])
        self.assertFalse(evidence["memo_persistence"])

    def test_oos_holdout_validation_does_not_pass_short_or_proxy_only_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_oos_holdout_validation

        short_dates = pd.date_range("2023-01-31", periods=10, freq="ME")
        short_curve = pd.DataFrame(
            {
                "Date": short_dates,
                "Total Balance": [100.0 + idx for idx in range(len(short_dates))],
            }
        )
        short_evidence = build_oos_holdout_validation(
            short_curve,
            short_curve,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(short_evidence["status"], "NEEDS_INPUT")

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        proxy_portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_evidence = build_oos_holdout_validation(
            proxy_portfolio,
            proxy_benchmark,
            portfolio_curve_source="component_curve_weighted_proxy",
            benchmark_curve_source="db_price_proxy",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(proxy_evidence["status"], "REVIEW")
        self.assertTrue(proxy_evidence["metrics"]["proxy_evidence"])

    def test_regime_split_validation_uses_macro_bucket_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_regime_split_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        macro = _macro_regime_rows(dates)

        evidence = build_regime_split_validation(
            portfolio,
            benchmark,
            macro,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            macro_source="finance.loaders.macro.load_macro_series_observations",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(evidence["schema_version"], "regime_split_validation_contract_v1")
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["metrics"]["regime_bucket_count"], 3)
        self.assertGreaterEqual(evidence["metrics"]["stress_regime_months"], 3)
        self.assertGreaterEqual(evidence["metrics"]["worst_regime_excess_return"], 0.0)
        self.assertFalse(evidence["registry_write"])
        self.assertFalse(evidence["memo_persistence"])

    def test_regime_split_validation_does_not_pass_missing_or_proxy_macro(self) -> None:
        from app.services.backtest_temporal_validation import build_regime_split_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        missing_evidence = build_regime_split_validation(
            portfolio,
            benchmark,
            pd.DataFrame(),
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            macro_source="missing",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(missing_evidence["status"], "NEEDS_INPUT")

        proxy_macro = _macro_regime_rows(dates, source_type="computed_proxy", coverage_status="proxy")
        proxy_evidence = build_regime_split_validation(
            portfolio,
            benchmark,
            proxy_macro,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            macro_source="computed_proxy_macro",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(proxy_evidence["status"], "REVIEW")
        self.assertTrue(proxy_evidence["metrics"]["proxy_evidence"])

    def test_missing_runtime_and_provider_evidence_are_not_passed(self) -> None:
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_NEEDS_INPUT,
            build_validation_efficacy_audit,
        )

        audit = build_validation_efficacy_audit(
            {
                "selection_source_id": "source-gap",
                "checks": [
                    {"Criteria": "Selection source", "Ready": True, "Current": "source-gap"},
                    {"Criteria": "Active components", "Ready": True, "Current": "2"},
                    {"Criteria": "Target weight total", "Ready": True, "Current": "100.00%"},
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": False, "Current": "NOT_RUN"},
                    {"Criteria": "Runtime period coverage", "Ready": False, "Current": "NOT_RUN"},
                    {"Criteria": "Provider coverage", "Ready": False, "Current": "NOT_RUN"},
                    {"Criteria": "Benchmark parity", "Ready": False, "Current": "NOT_RUN"},
                ],
                "provider_coverage_display_rows": [
                    {"Area": "ETF Operability", "Diagnostic Status": "NOT_RUN", "Freshness": "not_run"},
                    {"Area": "ETF Holdings", "Diagnostic Status": "NOT_RUN", "Freshness": "not_run"},
                ],
                "diagnostic_summary": {"status_counts": {"NOT_RUN": 4}},
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], VALIDATION_EFFICACY_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Runtime replay evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Provider / freshness evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Survivorship / universe guard"]["Status"], "REVIEW")

    def test_survivorship_guard_uses_data_coverage_lifecycle_evidence(self) -> None:
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_READY,
            build_validation_efficacy_audit,
        )

        audit = build_validation_efficacy_audit(
            {
                "selection_source_id": "source-lifecycle",
                "checks": [
                    {"Criteria": "Selection source", "Ready": True, "Current": "source-lifecycle"},
                    {"Criteria": "Active components", "Ready": True, "Current": "2"},
                    {"Criteria": "Target weight total", "Ready": True, "Current": "100.00%"},
                    {"Criteria": "Data Trust", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "portfolio_curve_rows": 120,
                    "curve_provenance": {
                        "portfolio_curve_source": "actual_runtime_replay",
                        "portfolio_curve_rows": 120,
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                    "benchmark_parity": {
                        "status": "PASS",
                        "metrics": {"coverage_ratio": 1.0, "same_period": True, "same_frequency": True},
                    },
                },
                "provider_coverage_display_rows": [
                    {"Area": "ETF Operability", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "ETF Holdings", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "robustness_validation": {
                    "robustness_route": "READY_FOR_STRESS_SWEEP",
                    "robustness_lab_board": {"status": "PASS", "summary": "stress / rolling / sensitivity attached"},
                },
                "data_coverage_audit": {
                    "rows": [
                        {
                            "Criteria": "Survivorship / delisting control",
                            "Status": "PASS",
                            "Evidence": "historical lifecycle rows cover requested period",
                        }
                    ]
                },
                "diagnostic_summary": {"status_counts": {"NOT_RUN": 0}},
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], VALIDATION_EFFICACY_READY)
        self.assertEqual(rows_by_criteria["Survivorship / universe guard"]["Status"], "PASS")


class BacktestRealismAuditContractTests(unittest.TestCase):
    def test_turnover_postprocess_marks_missing_holding_columns(self) -> None:
        from app.runtime.backtest import _apply_transaction_cost_postprocess

        result_df = pd.DataFrame(
            [
                {"Date": "2020-01-31", "Total Balance": 1000.0, "Total Return": None},
                {"Date": "2020-02-29", "Total Balance": 1010.0, "Total Return": 0.01},
            ]
        )

        hardened, diagnostics = _apply_transaction_cost_postprocess(
            result_df,
            transaction_cost_bps=10.0,
        )

        self.assertEqual(diagnostics["turnover_estimation_status"], "not_estimated_missing_holdings")
        self.assertIn("End Ticker", diagnostics["turnover_input_missing_columns"])
        self.assertTrue(hardened["Turnover"].isna().all())
        self.assertEqual(diagnostics["estimated_cost_total"], 0.0)
        self.assertEqual(diagnostics["net_cost_curve_status"], "applied_without_turnover_estimate")
        self.assertTrue(diagnostics["total_balance_is_net_of_cost"])
        self.assertEqual(diagnostics["estimated_cost_positive_rows"], 0)

    def test_turnover_postprocess_estimates_from_holdings(self) -> None:
        from app.runtime.backtest import _apply_transaction_cost_postprocess

        result_df = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Total Balance": 1000.0,
                    "Total Return": None,
                    "End Ticker": [],
                    "End Balance": [],
                    "Next Ticker": ["SPY"],
                    "Next Balance": [1000.0],
                    "Cash": 0.0,
                    "Rebalancing": True,
                },
                {
                    "Date": "2020-02-29",
                    "Total Balance": 1010.0,
                    "Total Return": 0.01,
                    "End Ticker": ["SPY"],
                    "End Balance": [1010.0],
                    "Next Ticker": ["TLT"],
                    "Next Balance": [1010.0],
                    "Cash": 0.0,
                    "Rebalancing": True,
                },
            ]
        )

        hardened, diagnostics = _apply_transaction_cost_postprocess(
            result_df,
            transaction_cost_bps=10.0,
        )

        self.assertEqual(diagnostics["turnover_estimation_status"], "estimated_from_holdings")
        self.assertEqual(diagnostics["turnover_observation_count"], 2)
        self.assertEqual(diagnostics["turnover_rebalance_rows"], 2)
        self.assertEqual(diagnostics["max_turnover"], 1.0)
        self.assertGreater(diagnostics["estimated_cost_total"], 0.0)
        self.assertEqual(diagnostics["net_cost_curve_status"], "applied_with_measurable_cost")
        self.assertGreater(diagnostics["estimated_cost_positive_rows"], 0)
        self.assertGreater(diagnostics["gross_net_end_balance_delta"], 0.0)
        self.assertIn("Turnover", hardened.columns)

    def test_ready_audit_uses_cost_turnover_and_liquidity_metadata_without_writes(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_READY,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "cost_model_snapshot": {
                        "cost_model_contract_version": "cost_model_source_contract_v1",
                        "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                        "cost_application_status": "applied_to_result_curve",
                        "cost_application_target": "result_df.Total Balance/Total Return",
                        "cost_turnover_source": "end_next_holdings_weight_delta",
                        "transaction_cost_bps": 10.0,
                        "avg_turnover": 0.15,
                        "estimated_cost_total": 125.0,
                    },
                    "turnover_evidence_snapshot": {
                        "turnover_model_contract_version": "turnover_evidence_contract_v1",
                        "turnover_estimation_status": "estimated_from_holdings",
                        "turnover_source": "end_next_holdings_weight_delta",
                        "turnover_observation_count": 24,
                        "turnover_rebalance_rows": 24,
                        "turnover_nonzero_count": 12,
                        "avg_turnover": 0.15,
                        "max_turnover": 0.4,
                        "avg_rebalance_turnover": 0.15,
                    },
                    "net_cost_curve_snapshot": {
                        "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                        "net_cost_curve_status": "applied_with_measurable_cost",
                        "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                        "total_balance_is_net_of_cost": True,
                        "net_cost_curve_rows": 24,
                        "estimated_cost_total": 125.0,
                        "estimated_cost_positive_rows": 12,
                        "gross_end_balance": 1200.0,
                        "net_end_balance": 1075.0,
                        "gross_net_end_balance_delta": 125.0,
                        "turnover_estimation_status": "estimated_from_holdings",
                    },
                    "cost_slippage_sensitivity": {
                        "schema_version": "cost_slippage_sensitivity_contract_v1",
                        "status": "PASS",
                        "computed_count": 3,
                        "review_count": 0,
                        "not_run_count": 0,
                        "runtime_followup_count": 0,
                        "summary": "Cost bps 5/10/25 and slippage spread shock passed.",
                        "rows": [
                            {
                                "Scenario": "Transaction cost bps sweep",
                                "Scope": "cost / slippage",
                                "Result Status": "PASS",
                            }
                        ],
                    },
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "real_money_hardening": True,
                            "avg_turnover": 0.15,
                            "max_turnover": 0.4,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "official operability coverage",
                            "provenance": {
                                "freshness_status": "fresh",
                                "source_mix": "official 100.0%",
                                "source_type_weights": {"official": 100.0},
                                "coverage_status_weights": {"actual": 100.0},
                                "as_of_range": "2026-05-20",
                                "stale_weight": 0.0,
                                "unknown_freshness_weight": 0.0,
                            },
                            "metrics": {
                                "review_count": 0,
                                "review_symbols": [],
                                "min_net_assets": 50_000_000_000,
                                "min_avg_daily_dollar_volume": 500_000_000,
                                "max_bid_ask_spread_pct": 0.0002,
                            },
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        self.assertEqual(audit["route"], BACKTEST_REALISM_READY)
        self.assertEqual(audit["cost_model_contract"]["application_status"], "applied_to_result_curve")
        self.assertEqual(audit["net_cost_curve_contract"]["proof_status"], "applied_with_measurable_cost")
        self.assertEqual(audit["turnover_evidence_contract"]["evidence_strength"], "actual_estimate")
        self.assertEqual(
            audit["cost_slippage_sensitivity_contract"]["evidence_strength"],
            "explicit_cost_slippage_sensitivity",
        )
        self.assertEqual(audit["liquidity_capacity_contract"]["proof_status"], "official_fresh_capacity_evidence")
        self.assertEqual(audit["metrics"]["pass"], 9)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def _ready_realism_validation_without_sensitivity(self):
        return {
            "selection_source_snapshot": {
                "construction": {"rebalance_cadence": "monthly"},
                "cost_model_snapshot": {
                    "cost_model_contract_version": "cost_model_source_contract_v1",
                    "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                    "cost_application_status": "applied_to_result_curve",
                    "cost_application_target": "result_df.Total Balance/Total Return",
                    "cost_turnover_source": "end_next_holdings_weight_delta",
                    "transaction_cost_bps": 10.0,
                    "avg_turnover": 0.15,
                    "estimated_cost_total": 125.0,
                },
                "turnover_evidence_snapshot": {
                    "turnover_model_contract_version": "turnover_evidence_contract_v1",
                    "turnover_estimation_status": "estimated_from_holdings",
                    "turnover_source": "end_next_holdings_weight_delta",
                    "turnover_observation_count": 24,
                    "turnover_rebalance_rows": 24,
                    "turnover_nonzero_count": 12,
                    "avg_turnover": 0.15,
                    "max_turnover": 0.4,
                    "avg_rebalance_turnover": 0.15,
                },
                "net_cost_curve_snapshot": {
                    "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                    "net_cost_curve_status": "applied_with_measurable_cost",
                    "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                    "total_balance_is_net_of_cost": True,
                    "net_cost_curve_rows": 24,
                    "estimated_cost_total": 125.0,
                    "estimated_cost_positive_rows": 12,
                    "gross_end_balance": 1200.0,
                    "net_end_balance": 1075.0,
                    "gross_net_end_balance_delta": 125.0,
                    "turnover_estimation_status": "estimated_from_holdings",
                },
                "source_snapshot": {
                    "settings_snapshot": {
                        "transaction_cost_bps": 10.0,
                        "rebalance_interval": 1,
                        "operator_tax_scope_acknowledged": True,
                    },
                    "meta": {
                        "real_money_hardening": True,
                        "avg_turnover": 0.15,
                        "max_turnover": 0.4,
                        "net_cagr_spread": 0.03,
                        "promotion_min_net_cagr_spread": -0.02,
                    },
                },
            },
            "provider_coverage": {
                "coverage": {
                    "operability": {
                        "diagnostic_status": "PASS",
                        "coverage_weight": 100.0,
                        "summary": "official operability coverage",
                        "provenance": {
                            "freshness_status": "fresh",
                            "source_mix": "official 100.0%",
                            "source_type_weights": {"official": 100.0},
                            "coverage_status_weights": {"actual": 100.0},
                            "as_of_range": "2026-05-20",
                            "stale_weight": 0.0,
                            "unknown_freshness_weight": 0.0,
                        },
                        "metrics": {
                            "review_count": 0,
                            "review_symbols": [],
                            "min_net_assets": 50_000_000_000,
                            "min_avg_daily_dollar_volume": 500_000_000,
                            "max_bid_ask_spread_pct": 0.0002,
                        },
                    }
                }
            },
            "diagnostic_results": [
                {
                    "domain": "operability_cost_liquidity",
                    "status": "PASS",
                    "metrics": {"one_way_cost_bps": 10.0},
                    "evidence_rows": [
                        {
                            "Check": "One-way cost bps assumption",
                            "Status": "PASS",
                            "Evidence": "cost bps exists but this is not sensitivity evidence",
                        }
                    ],
                }
            ],
        }

    def test_missing_cost_slippage_sensitivity_requires_review_despite_ready_costs(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(self._ready_realism_validation_without_sensitivity())

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Cost / slippage sensitivity evidence"]["Status"], "REVIEW")
        self.assertEqual(
            audit["cost_slippage_sensitivity_contract"]["evidence_strength"],
            "missing_sensitivity_evidence",
        )

    def test_generic_robustness_sensitivity_without_cost_axis_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        validation = self._ready_realism_validation_without_sensitivity()
        validation["sensitivity_interpretation"] = {
            "status": "PASS",
            "summary": "2 curve sensitivity checks computed.",
            "computed_count": 2,
            "review_count": 0,
            "runtime_followup_count": 0,
            "rows": [
                {
                    "Check": "Weight tilt sensitivity",
                    "Status": "PASS",
                    "Finding": "component weights stable",
                }
            ],
        }
        validation["robustness_validation"] = {
            "robustness_lab_board": {
                "status": "PASS",
                "metrics": {
                    "computed_sensitivity_checks": 2,
                    "sensitivity_review_count": 0,
                    "runtime_followup_count": 0,
                },
                "summary_rows": [
                    {
                        "Check": "Sensitivity coverage",
                        "Status": "PASS",
                        "Current": "computed 2",
                        "Evidence": "weight and drop-one checks",
                    }
                ],
            }
        }

        audit = build_backtest_realism_audit(validation)

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Cost / slippage sensitivity evidence"]["Status"], "REVIEW")
        self.assertEqual(
            audit["cost_slippage_sensitivity_contract"]["evidence_strength"],
            "generic_sensitivity_only",
        )

    def test_legacy_provider_pass_without_capacity_contract_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "cost_model_snapshot": {
                        "cost_model_contract_version": "cost_model_source_contract_v1",
                        "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                        "cost_application_status": "applied_to_result_curve",
                        "transaction_cost_bps": 10.0,
                        "estimated_cost_total": 125.0,
                    },
                    "turnover_evidence_snapshot": {
                        "turnover_model_contract_version": "turnover_evidence_contract_v1",
                        "turnover_estimation_status": "estimated_from_holdings",
                        "turnover_source": "end_next_holdings_weight_delta",
                        "turnover_observation_count": 24,
                        "turnover_rebalance_rows": 24,
                        "avg_turnover": 0.15,
                    },
                    "net_cost_curve_snapshot": {
                        "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                        "net_cost_curve_status": "applied_with_measurable_cost",
                        "total_balance_is_net_of_cost": True,
                        "net_cost_curve_rows": 24,
                        "estimated_cost_total": 125.0,
                        "estimated_cost_positive_rows": 12,
                        "gross_end_balance": 1200.0,
                        "net_end_balance": 1075.0,
                        "gross_net_end_balance_delta": 125.0,
                    },
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "real_money_hardening": True,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "legacy pass without provenance",
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Liquidity / operability evidence"]["Status"], "REVIEW")
        self.assertEqual(
            audit["liquidity_capacity_contract"]["proof_status"],
            "legacy_provider_pass_without_capacity_contract",
        )

    def test_cost_assumption_without_application_proof_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_NEEDS_INPUT,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "avg_turnover": 0.15,
                            "max_turnover": 0.4,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "official operability coverage",
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Transaction cost model"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Net cost curve proof"]["Status"], "NEEDS_INPUT")
        self.assertEqual(audit["cost_model_contract"]["application_status"], "assumption_only")

    def test_rebalance_cadence_without_turnover_estimate_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "cost_model_snapshot": {
                        "cost_model_contract_version": "cost_model_source_contract_v1",
                        "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                        "cost_application_status": "applied_to_result_curve",
                        "transaction_cost_bps": 10.0,
                        "estimated_cost_total": 0.0,
                    },
                    "turnover_evidence_snapshot": {
                        "turnover_model_contract_version": "turnover_evidence_contract_v1",
                        "turnover_estimation_status": "not_estimated_missing_holdings",
                        "turnover_source": "missing_result_holding_columns",
                        "turnover_input_missing_columns": ["End Ticker", "Next Ticker"],
                    },
                    "net_cost_curve_snapshot": {
                        "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                        "net_cost_curve_status": "applied_without_turnover_estimate",
                        "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                        "total_balance_is_net_of_cost": True,
                        "net_cost_curve_rows": 24,
                        "estimated_cost_total": 0.0,
                        "estimated_cost_positive_rows": 0,
                        "gross_net_end_balance_delta": 0.0,
                        "turnover_estimation_status": "not_estimated_missing_holdings",
                    },
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "real_money_hardening": True,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "official operability coverage",
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Net cost curve proof"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Turnover evidence"]["Status"], "REVIEW")
        self.assertEqual(audit["net_cost_curve_contract"]["proof_status"], "applied_without_turnover_estimate")
        self.assertEqual(audit["turnover_evidence_contract"]["evidence_strength"], "missing_estimate")

    def test_missing_cost_and_liquidity_evidence_are_not_passed(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_NEEDS_INPUT,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {"construction": {}},
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "NOT_RUN",
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Transaction cost model"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Liquidity / operability evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Tax / account scope"]["Status"], "REVIEW")


class DataCoverageAuditContractTests(unittest.TestCase):
    def test_ready_audit_uses_db_price_provider_and_survivorship_evidence_without_writes(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_READY,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY", "TLT"],
                    "symbol_weights": {"SPY": 60.0, "TLT": 40.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "TLT",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                    ],
                    "asset_profile_rows": [
                        {"symbol": "SPY", "status": "active"},
                        {"symbol": "TLT", "status": "active"},
                    ],
                },
                "provider_coverage_display_rows": [
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
                "survivorship_control": {"status": "controlled"},
            }
        )

        self.assertEqual(audit["route"], DATA_COVERAGE_READY)
        self.assertEqual(audit["metrics"]["pass"], 6)
        self.assertEqual(audit["metrics"]["price_covered_weight"], 100.0)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def test_lifecycle_rows_control_survivorship_without_explicit_flag(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_READY,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY", "TLT"],
                    "symbol_weights": {"SPY": 60.0, "TLT": 40.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "TLT",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                    ],
                    "asset_profile_rows": [
                        {"symbol": "SPY", "status": "active"},
                        {"symbol": "TLT", "status": "active"},
                    ],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "historical_feed",
                            "source_type": "historical_listing",
                            "coverage_status": "actual",
                            "first_seen_date": "1993-01-29",
                            "last_seen_date": None,
                        },
                        {
                            "symbol": "TLT",
                            "listing_status": "active",
                            "source": "historical_feed",
                            "source_type": "historical_listing",
                            "coverage_status": "actual",
                            "first_seen_date": "2002-07-26",
                            "last_seen_date": None,
                        },
                    ],
                },
                "provider_coverage_display_rows": [
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_READY)
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "PASS")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "PASS")
        self.assertEqual(audit["metrics"]["lifecycle_covered_symbols"], ["SPY", "TLT"])

    def test_current_listing_snapshot_does_not_control_historical_survivorship(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_REVIEW,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY"],
                    "symbol_weights": {"SPY": 100.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        }
                    ],
                    "asset_profile_rows": [{"symbol": "SPY", "status": "active"}],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "nyse_listings_directory",
                            "source_type": "current_listing_snapshot",
                            "coverage_status": "partial",
                            "first_seen_date": "2026-05-28",
                            "last_seen_date": "2026-05-28",
                        }
                    ],
                },
                "provider_coverage_display_rows": [{"Diagnostic Status": "PASS", "Freshness": "fresh"}],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_REVIEW)
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "REVIEW")
        self.assertIn("SPY", audit["metrics"]["lifecycle_partial_symbols"])
        self.assertEqual(audit["metrics"]["lifecycle_current_snapshot_symbols"], ["SPY"])

    def test_missing_db_price_and_universe_evidence_are_not_passed(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_NEEDS_INPUT,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY"],
                    "symbol_weights": {"SPY": 100.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [],
                    "asset_profile_rows": [],
                },
                "provider_coverage_display_rows": [],
                "curve_evidence": {},
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Price DB window coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "NEEDS_INPUT")

    def test_lifecycle_audit_scoring_separates_partial_identity_computed_and_actual_evidence(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_REVIEW,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY", "AAPL", "ABC"],
                    "symbol_weights": {"SPY": 40.0, "AAPL": 40.0, "ABC": 20.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "AAPL",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "ABC",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                    ],
                    "asset_profile_rows": [
                        {"symbol": "SPY", "status": "active"},
                        {"symbol": "AAPL", "status": "active"},
                        {"symbol": "ABC", "status": "active"},
                    ],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "historical_feed",
                            "source_type": "historical_listing",
                            "coverage_status": "actual",
                            "first_seen_date": "1993-01-29",
                            "last_seen_date": None,
                        },
                        {
                            "symbol": "AAPL",
                            "listing_status": "active",
                            "source": "nasdaq_symdir_nasdaqlisted",
                            "source_type": "current_listing_snapshot",
                            "coverage_status": "partial",
                            "first_seen_date": "2026-05-28",
                            "last_seen_date": "2026-05-28",
                            "event_type": "listing_observed",
                        },
                        {
                            "symbol": "AAPL",
                            "listing_status": "active",
                            "source": "sec_company_tickers_exchange",
                            "source_type": "current_listing_snapshot",
                            "coverage_status": "partial",
                            "first_seen_date": "2026-05-28",
                            "last_seen_date": "2026-05-28",
                            "event_type": "listing_observed",
                            "related_cik": 320193,
                        },
                        {
                            "symbol": "AAPL",
                            "listing_status": "active",
                            "source": "computed_snapshot_lifecycle",
                            "source_type": "computed_from_snapshots",
                            "coverage_status": "partial",
                            "first_seen_date": "2019-01-01",
                            "last_seen_date": "2021-12-31",
                            "event_type": "historical_membership",
                        },
                        {
                            "symbol": "ABC",
                            "listing_status": "delisted",
                            "source": "sec_form25_abc",
                            "source_type": "delisting_feed",
                            "coverage_status": "actual",
                            "first_seen_date": None,
                            "last_seen_date": "2020-06-01",
                            "event_type": "delisting",
                            "event_date": "2020-06-01",
                        },
                    ],
                },
                "provider_coverage_display_rows": [{"Diagnostic Status": "PASS", "Freshness": "fresh"}],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_REVIEW)
        self.assertEqual(audit["metrics"]["lifecycle_covered_symbols"], ["SPY"])
        self.assertEqual(audit["metrics"]["lifecycle_partial_symbols"], ["AAPL", "ABC"])
        self.assertEqual(audit["metrics"]["lifecycle_actual_symbols"], ["ABC", "SPY"])
        self.assertEqual(audit["metrics"]["lifecycle_actual_noncovering_symbols"], ["ABC"])
        self.assertEqual(audit["metrics"]["lifecycle_current_snapshot_symbols"], ["AAPL"])
        self.assertEqual(audit["metrics"]["lifecycle_identity_crosscheck_symbols"], ["AAPL"])
        self.assertEqual(audit["metrics"]["lifecycle_computed_partial_symbols"], ["AAPL"])
        self.assertEqual(audit["metrics"]["lifecycle_delisting_actual_symbols"], ["ABC"])
        self.assertEqual(
            audit["metrics"]["lifecycle_row_counts_by_category"],
            {
                "computed_partial": 1,
                "current_snapshot": 1,
                "delisting_actual": 1,
                "historical_actual": 1,
                "identity_crosscheck": 1,
            },
        )
        self.assertIn("current_snapshot=AAPL", rows_by_criteria["Universe / listing evidence"]["Evidence"])
        self.assertIn("sec_identity=AAPL", rows_by_criteria["Universe / listing evidence"]["Evidence"])
        self.assertIn("computed_partial=AAPL", rows_by_criteria["Survivorship / delisting control"]["Evidence"])
        self.assertIn("delisting_actual=ABC", rows_by_criteria["Survivorship / delisting control"]["Evidence"])


class SecForm25DelistingCollectorContractTests(unittest.TestCase):
    def test_form25_payload_maps_to_lifecycle_row_without_claiming_full_membership(self) -> None:
        from finance.data.sec_delisting import (
            build_sec_form25_lifecycle_rows,
            extract_sec_form25_filings,
            normalize_sec_ticker_map,
        )

        ticker_map = normalize_sec_ticker_map(
            {
                "0": {"cik_str": 123456, "ticker": "ABC", "title": "ABC Corp"},
            }
        )
        filings = extract_sec_form25_filings(
            {
                "filings": {
                    "recent": {
                        "form": ["10-K", "25-NSE"],
                        "accessionNumber": ["0000123456-26-000001", "0000123456-26-000002"],
                        "filingDate": ["2026-02-01", "2026-03-15"],
                        "reportDate": ["2026-01-01", ""],
                        "primaryDocument": ["abc-10k.htm", "primary_doc.xml"],
                    }
                }
            }
        )
        rows = build_sec_form25_lifecycle_rows(
            "abc",
            "stock",
            ticker_map["ABC"],
            filings,
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["symbol"], "ABC")
        self.assertEqual(row["listing_status"], "delisted")
        self.assertEqual(row["source_type"], "delisting_feed")
        self.assertEqual(row["coverage_status"], "actual")
        self.assertIsNone(row["first_seen_date"])
        self.assertEqual(row["last_seen_date"], "2026-03-15")
        self.assertEqual(row["event_type"], "delisting")
        self.assertEqual(row["event_date"], "2026-03-15")
        self.assertEqual(row["related_cik"], 123456)
        self.assertIn("sec_form25_000012345626000002", row["source"])
        self.assertIn("primary_doc.xml", row["source_ref"])
        self.assertIn('"event_type": "delisting"', row["evidence_json"])
        self.assertIn("absence of Form 25 is not active-listing proof", row["evidence_json"])

    def test_current_listing_snapshot_maps_to_partial_listing_observed_event(self) -> None:
        from finance.data import nyse_db

        class FakeDB:
            def __init__(self) -> None:
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

        fake_db = FakeDB()
        frame = pd.DataFrame(
            [
                {
                    "symbol": "spy",
                    "name": "SPDR S&P 500 ETF Trust",
                    "url": "https://www.nyse.com/quote/ARCX:SPY",
                }
            ]
        )
        with patch.object(nyse_db, "sync_table_schema"):
            count = nyse_db._upsert_symbol_lifecycle_rows(  # noqa: SLF001 - contract locks DB row semantics.
                fake_db,
                kind="etf",
                frame=frame,
                snapshot_date="2026-05-28",
            )

        self.assertEqual(count, 1)
        written_row = fake_db.executemany_calls[0][1][0]
        self.assertEqual(written_row["symbol"], "SPY")
        self.assertEqual(written_row["source_type"], "current_listing_snapshot")
        self.assertEqual(written_row["coverage_status"], "partial")
        self.assertEqual(written_row["event_type"], "listing_observed")
        self.assertEqual(written_row["event_date"], "2026-05-28")
        self.assertIsNone(written_row["related_symbol"])
        self.assertIsNone(written_row["related_cik"])
        self.assertIn("not sufficient alone for historical survivorship PASS", written_row["evidence_json"])

    def test_collector_writes_db_lifecycle_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import sec_delisting

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                if "nyse_etf" in sql:
                    return []
                if "nyse_stock" in sql:
                    return [{"symbol": "ABC"}]
                return []

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        def fake_fetch(url: str, user_agent: str, timeout: float):
            if url == sec_delisting.SEC_COMPANY_TICKERS_URL:
                return {"0": {"cik_str": 123456, "ticker": "ABC", "title": "ABC Corp"}}
            return {
                "filings": {
                    "recent": {
                        "form": ["25-NSE"],
                        "accessionNumber": ["0000123456-26-000002"],
                        "filingDate": ["2026-03-15"],
                        "reportDate": [""],
                        "primaryDocument": ["primary_doc.xml"],
                    },
                    "files": [],
                }
            }

        fake_db = FakeDB()
        with patch.object(sec_delisting, "MySQLClient", return_value=fake_db), patch.object(
            sec_delisting,
            "sync_table_schema",
        ):
            summary = sec_delisting.collect_and_store_sec_form25_delistings(
                ["ABC"],
                user_agent="Unit Test unit@example.com",
                fetch_json=fake_fetch,
                request_sleep=0,
            )

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 1)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        self.assertEqual(len(fake_db.executemany_calls), 1)
        written_row = fake_db.executemany_calls[0][1][0]
        self.assertEqual(written_row["kind"], "stock")
        self.assertEqual(written_row["source_type"], "delisting_feed")
        self.assertEqual(written_row["event_type"], "delisting")
        self.assertEqual(written_row["event_date"], "2026-03-15")

    def test_ingestion_job_surfaces_form25_coverage_gaps(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_sec_form25_delistings",
            return_value={
                "rows_written": 1,
                "unmapped_symbols": ["MISS"],
                "symbols_without_form25": [],
                "errors": [],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_sec_form25_delistings("ABC,MISS", user_agent="Unit Test unit@example.com")

        self.assertEqual(result["job_name"], "collect_sec_form25_delistings")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 1)
        self.assertIn("MISS", result["failed_symbols"])


class SymbolDirectorySnapshotCollectorContractTests(unittest.TestCase):
    def test_nasdaq_listed_snapshot_maps_to_partial_listing_observed_rows(self) -> None:
        from finance.data.symbol_directory import build_symbol_directory_lifecycle_rows

        text = "\n".join(
            [
                "Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares",
                "AAPL|Apple Inc. Common Stock|Q|N|N|100|N|N",
                "QQQ|Invesco QQQ Trust, Series 1|G|N|N|100|Y|N",
                "TEST|Test Issue|Q|Y|N|100|N|N",
                "File Creation Time: 0528202613:04|||||",
            ]
        )

        rows, metadata = build_symbol_directory_lifecycle_rows(
            "nasdaqlisted",
            text,
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(metadata["event_date"], "2026-05-28")
        self.assertEqual(metadata["rows_built"], 2)
        self.assertEqual(metadata["skipped_test_issues"], 1)
        rows_by_symbol = {row["symbol"]: row for row in rows}
        self.assertEqual(rows_by_symbol["AAPL"]["kind"], "stock")
        self.assertEqual(rows_by_symbol["QQQ"]["kind"], "etf")
        self.assertEqual(rows_by_symbol["AAPL"]["source"], "nasdaq_symdir_nasdaqlisted")
        self.assertEqual(rows_by_symbol["AAPL"]["source_type"], "current_listing_snapshot")
        self.assertEqual(rows_by_symbol["AAPL"]["coverage_status"], "partial")
        self.assertEqual(rows_by_symbol["AAPL"]["event_type"], "listing_observed")
        self.assertEqual(rows_by_symbol["AAPL"]["event_date"], "2026-05-28")
        self.assertIn("not historical membership or delisting proof", rows_by_symbol["AAPL"]["evidence_json"])

    def test_otherlisted_snapshot_maps_exchange_context_without_claiming_history(self) -> None:
        from finance.data.symbol_directory import build_symbol_directory_lifecycle_rows

        text = "\n".join(
            [
                "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol",
                "SPY|SPDR S&P 500 ETF Trust|P|SPY|Y|100|N|SPY",
                "GE|GE Aerospace Common Stock|N|GE|N|100|N|GE",
                "File Creation Time: 0528202613:04|||||||",
            ]
        )

        rows, metadata = build_symbol_directory_lifecycle_rows(
            "otherlisted",
            text,
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(metadata["rows_built"], 2)
        rows_by_symbol = {row["symbol"]: row for row in rows}
        self.assertEqual(rows_by_symbol["SPY"]["kind"], "etf")
        self.assertEqual(rows_by_symbol["SPY"]["source"], "nasdaq_symdir_otherlisted")
        self.assertIn('"exchange": "P"', rows_by_symbol["SPY"]["evidence_json"])
        self.assertIn('"nasdaq_symbol": "SPY"', rows_by_symbol["SPY"]["evidence_json"])
        self.assertEqual(rows_by_symbol["GE"]["event_type"], "listing_observed")

    def test_collector_writes_symbol_directory_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import symbol_directory

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                return []

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        def fake_fetch(url: str, user_agent: str, timeout: float) -> str:
            if url == symbol_directory.NASDAQ_LISTED_URL:
                return "\n".join(
                    [
                        "Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares",
                        "AAPL|Apple Inc. Common Stock|Q|N|N|100|N|N",
                        "File Creation Time: 0528202613:04|||||",
                    ]
                )
            return "\n".join(
                [
                    "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol",
                    "SPY|SPDR S&P 500 ETF Trust|P|SPY|Y|100|N|SPY",
                    "File Creation Time: 0528202613:04|||||||",
                ]
            )

        fake_db = FakeDB()
        with patch.object(symbol_directory, "MySQLClient", return_value=fake_db), patch.object(
            symbol_directory,
            "sync_table_schema",
        ):
            summary = symbol_directory.collect_and_store_symbol_directory_snapshots(
                user_agent="Unit Test unit@example.com",
                fetch_text=fake_fetch,
            )

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 2)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        written_rows = fake_db.executemany_calls[0][1]
        self.assertEqual({row["source"] for row in written_rows}, {"nasdaq_symdir_nasdaqlisted", "nasdaq_symdir_otherlisted"})
        self.assertEqual({row["event_type"] for row in written_rows}, {"listing_observed"})
        self.assertEqual({row["coverage_status"] for row in written_rows}, {"partial"})

    def test_ingestion_job_wraps_symbol_directory_snapshot_summary(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_symbol_directory_snapshots",
            return_value={
                "rows_written": 2,
                "rows_found": 2,
                "errors": [],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_symbol_directory_snapshots(user_agent="Unit Test unit@example.com")

        self.assertEqual(result["job_name"], "collect_symbol_directory_snapshots")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(result["symbols_processed"], 2)


class SecCompanyTickerCrosscheckContractTests(unittest.TestCase):
    def test_sec_exchange_payload_maps_to_partial_listing_observed_rows(self) -> None:
        from finance.data.sec_company_tickers import (
            build_sec_company_ticker_lifecycle_rows,
            normalize_sec_company_tickers_exchange,
        )

        records = normalize_sec_company_tickers_exchange(
            {
                "fields": ["cik", "name", "ticker", "exchange"],
                "data": [
                    [320193, "Apple Inc.", "AAPL", "Nasdaq"],
                    [1067983, "BERKSHIRE HATHAWAY INC", "BRK-B", "NYSE"],
                    ["bad", "Bad CIK", "BAD", "NYSE"],
                ],
            }
        )
        rows, metadata = build_sec_company_ticker_lifecycle_rows(
            records,
            kind_by_symbol={"AAPL": "stock", "BRK-B": "stock"},
            symbols=["AAPL"],
            collected_at="2026-05-28 00:00:00",
            snapshot_date="2026-05-28",
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(metadata["skipped_not_requested"], 1)
        row = rows[0]
        self.assertEqual(row["symbol"], "AAPL")
        self.assertEqual(row["kind"], "stock")
        self.assertEqual(row["source"], "sec_company_tickers_exchange")
        self.assertEqual(row["source_type"], "current_listing_snapshot")
        self.assertEqual(row["coverage_status"], "partial")
        self.assertEqual(row["event_type"], "listing_observed")
        self.assertEqual(row["event_date"], "2026-05-28")
        self.assertEqual(row["related_cik"], 320193)
        self.assertIn('"exchange": "Nasdaq"', row["evidence_json"])
        self.assertIn("not historical membership proof", row["evidence_json"])

    def test_collector_writes_sec_crosscheck_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import sec_company_tickers

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                if "nyse_etf" in sql:
                    return [{"symbol": "QQQ"}]
                if "nyse_stock" in sql:
                    return [{"symbol": "AAPL"}]
                return []

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        def fake_fetch(url: str, user_agent: str, timeout: float):
            self.assertEqual(url, sec_company_tickers.SEC_COMPANY_TICKERS_EXCHANGE_URL)
            return {
                "fields": ["cik", "name", "ticker", "exchange"],
                "data": [
                    [320193, "Apple Inc.", "AAPL", "Nasdaq"],
                    [111111, "Invesco QQQ Trust", "QQQ", "Nasdaq"],
                ],
            }

        fake_db = FakeDB()
        with patch.object(sec_company_tickers, "MySQLClient", return_value=fake_db), patch.object(
            sec_company_tickers,
            "sync_table_schema",
        ):
            summary = sec_company_tickers.collect_and_store_sec_company_ticker_crosscheck(
                symbols=["AAPL", "QQQ"],
                user_agent="Unit Test unit@example.com",
                fetch_json=fake_fetch,
                snapshot_date="2026-05-28",
            )

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 2)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        rows_by_symbol = {row["symbol"]: row for row in fake_db.executemany_calls[0][1]}
        self.assertEqual(rows_by_symbol["AAPL"]["kind"], "stock")
        self.assertEqual(rows_by_symbol["QQQ"]["kind"], "etf")
        self.assertEqual({row["coverage_status"] for row in rows_by_symbol.values()}, {"partial"})
        self.assertEqual({row["event_type"] for row in rows_by_symbol.values()}, {"listing_observed"})

    def test_ingestion_job_wraps_sec_crosscheck_summary(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_sec_company_ticker_crosscheck",
            return_value={
                "requested": 2,
                "rows_written": 1,
                "requested_missing_symbols": ["MISS"],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_sec_company_ticker_crosscheck("AAPL,MISS", user_agent="Unit Test unit@example.com")

        self.assertEqual(result["job_name"], "collect_sec_company_ticker_crosscheck")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 1)
        self.assertIn("MISS", result["failed_symbols"])


class ComputedSnapshotLifecycleContractTests(unittest.TestCase):
    def test_repeated_current_snapshots_build_partial_computed_row(self) -> None:
        from finance.data.computed_lifecycle import build_computed_snapshot_lifecycle_rows

        rows, metadata = build_computed_snapshot_lifecycle_rows(
            [
                {
                    "symbol": "spy",
                    "kind": "etf",
                    "listing_status": "active",
                    "source": "nasdaq_symdir_otherlisted",
                    "source_type": "current_listing_snapshot",
                    "coverage_status": "partial",
                    "first_seen_date": "2026-05-01",
                    "last_seen_date": "2026-05-28",
                    "event_type": "listing_observed",
                    "event_date": "2026-05-28",
                    "name": "SPDR S&P 500 ETF Trust",
                },
                {
                    "symbol": "ONE",
                    "kind": "stock",
                    "listing_status": "active",
                    "source": "sec_company_tickers_exchange",
                    "source_type": "current_listing_snapshot",
                    "coverage_status": "partial",
                    "first_seen_date": "2026-05-28",
                    "last_seen_date": "2026-05-28",
                    "event_type": "listing_observed",
                    "event_date": "2026-05-28",
                },
            ],
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(metadata["rows_built"], 1)
        self.assertEqual(metadata["skipped_insufficient_observation_dates"], 1)
        row = rows[0]
        self.assertEqual(row["symbol"], "SPY")
        self.assertEqual(row["kind"], "etf")
        self.assertEqual(row["listing_status"], "active")
        self.assertEqual(row["source"], "computed_snapshot_lifecycle")
        self.assertEqual(row["source_type"], "computed_from_snapshots")
        self.assertEqual(row["coverage_status"], "partial")
        self.assertEqual(row["first_seen_date"], "2026-05-01")
        self.assertEqual(row["last_seen_date"], "2026-05-28")
        self.assertEqual(row["event_type"], "historical_membership")
        self.assertEqual(row["event_date"], "2026-05-28")
        self.assertIn('"pass_eligible": false', row["evidence_json"])
        self.assertIn("absence from current snapshots is not delisting proof", row["evidence_json"])

    def test_collector_writes_computed_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import computed_lifecycle

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                return [
                    {
                        "symbol": "SPY",
                        "kind": "etf",
                        "listing_status": "active",
                        "source": "nasdaq_symdir_otherlisted",
                        "source_type": "current_listing_snapshot",
                        "coverage_status": "partial",
                        "first_seen_date": "2026-05-01",
                        "last_seen_date": "2026-05-28",
                        "event_type": "listing_observed",
                        "event_date": "2026-05-28",
                        "name": "SPDR S&P 500 ETF Trust",
                    }
                ]

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        fake_db = FakeDB()
        with patch.object(computed_lifecycle, "MySQLClient", return_value=fake_db), patch.object(
            computed_lifecycle,
            "sync_table_schema",
        ):
            summary = computed_lifecycle.collect_and_store_computed_snapshot_lifecycle(symbols=["SPY"])

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 1)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        written_row = fake_db.executemany_calls[0][1][0]
        self.assertEqual(written_row["source_type"], "computed_from_snapshots")
        self.assertEqual(written_row["coverage_status"], "partial")
        self.assertIsNone(written_row["inactive_detected_at"])

    def test_ingestion_job_wraps_computed_snapshot_summary(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_computed_snapshot_lifecycle",
            return_value={
                "requested": 2,
                "rows_written": 1,
                "requested_missing_symbols": ["MISS"],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_computed_snapshot_lifecycle("SPY,MISS")

        self.assertEqual(result["job_name"], "collect_computed_snapshot_lifecycle")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 1)
        self.assertIn("MISS", result["failed_symbols"])

    def test_partial_computed_snapshot_row_does_not_pass_survivorship(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_REVIEW,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY"],
                    "symbol_weights": {"SPY": 100.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        }
                    ],
                    "asset_profile_rows": [{"symbol": "SPY", "status": "active"}],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "computed_snapshot_lifecycle",
                            "source_type": "computed_from_snapshots",
                            "coverage_status": "partial",
                            "first_seen_date": "2019-01-01",
                            "last_seen_date": "2021-12-31",
                            "event_type": "historical_membership",
                            "event_date": "2021-12-31",
                        }
                    ],
                },
                "provider_coverage_display_rows": [{"Diagnostic Status": "PASS", "Freshness": "fresh"}],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_REVIEW)
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "REVIEW")
        self.assertIn("SPY", audit["metrics"]["lifecycle_partial_symbols"])
        self.assertEqual(audit["metrics"]["lifecycle_computed_partial_symbols"], ["SPY"])


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

    def test_robustness_lab_board_keeps_compact_evidence_contract(self) -> None:
        from app.services.backtest_practical_validation_stress_sensitivity import build_robustness_lab_board

        board = build_robustness_lab_board(
            stress_interpretation={
                "status": "REVIEW",
                "summary": "1/2개 covered stress window만 계산됐습니다.",
                "covered_count": 2,
                "computed_count": 1,
                "uncomputed_count": 1,
                "worst_mdd": -0.25,
                "worst_mdd_scenario": "COVID crash",
                "worst_benchmark_spread": -0.04,
                "rows": [
                    {
                        "Check": "Stress coverage",
                        "Status": "REVIEW",
                        "Finding": "1/2 covered windows computed",
                        "Why It Matters": "stress coverage compact summary",
                        "Next Check": "daily replay",
                    }
                ],
            },
            sensitivity_interpretation={
                "status": "PASS",
                "summary": "2개 sensitivity 계산됨",
                "computed_count": 2,
                "review_count": 0,
                "runtime_followup_count": 1,
                "worst_scenario": "Mix weight +5%p: Core",
                "worst_cagr_delta": -0.01,
                "worst_mdd_delta": -0.02,
            },
            stress_rows=[
                {
                    "Scenario": "COVID crash",
                    "Result Status": "REVIEW",
                    "Window": "2020-02-19 -> 2020-03-23",
                    "Portfolio Return": -0.18,
                    "Portfolio MDD": -0.25,
                    "Benchmark Spread": -0.04,
                    "Expected Check": "return / MDD / benchmark spread",
                }
            ],
            sensitivity_rows=[
                {
                    "Scenario": "GTAA parameter perturbation",
                    "Scope": "interval / MA window",
                    "Result Status": "NOT_RUN",
                    "Expected Check": "cadence 민감도",
                }
            ],
            overfit_audit={"status": "PASS", "trial_count": 4, "interpretation": "trial count ok"},
            rolling_evidence={
                "status": "PASS",
                "summary": "12개월 rolling 계산됨",
                "metrics": {"window_count": 8, "worst_rolling_cagr": 0.01, "worst_rolling_mdd": -0.08},
            },
        )

        self.assertEqual(board["schema_version"], "robustness_lab_board_v1")
        self.assertEqual(board["status"], "REVIEW")
        self.assertEqual(board["metrics"]["computed_stress_windows"], 1)
        self.assertEqual(board["metrics"]["runtime_followup_count"], 1)
        self.assertEqual(len(board["summary_rows"]), 6)
        self.assertTrue(any(row["Check"] == "Local overfit audit" for row in board["summary_rows"]))
        self.assertTrue(any(row["Status"] == "NOT_RUN" for row in board["follow_up_rows"]))


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
        self.assertEqual(operability_context["metrics"]["review_count"], 0)
        self.assertEqual(operability_context["metrics"]["min_net_assets"], 50_000_000_000)
        self.assertEqual(operability_context["metrics"]["min_avg_daily_dollar_volume"], 500_000_000)
        self.assertEqual(operability_context["metrics"]["max_bid_ask_spread_pct"], 0.0002)
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

    def test_provider_context_keeps_bridge_liquidity_evidence_in_review(self) -> None:
        from app.services import backtest_practical_validation_provider_context as provider_context

        operability = pd.DataFrame(
            [
                {
                    "symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "local_db_bridge",
                    "source_type": "database_bridge",
                    "coverage_status": "bridge",
                    "collected_at": "2026-05-21",
                    "expense_ratio": 0.0009,
                    "net_assets": 500_000_000_000,
                    "avg_daily_dollar_volume": 3_000_000_000,
                    "bid_ask_spread_pct": 0.0001,
                    "premium_discount_pct": 0.0002,
                }
            ]
        )

        with (
            patch.object(provider_context, "load_etf_operability_snapshot", return_value=operability),
            patch.object(provider_context, "load_etf_holdings_snapshot", return_value=pd.DataFrame()),
            patch.object(provider_context, "load_etf_exposure_snapshot", return_value=pd.DataFrame()),
            patch.object(provider_context, "load_macro_snapshot", return_value=pd.DataFrame()),
        ):
            context = provider_context.build_provider_context(
                {"SPY": 100.0},
                as_of_date="2026-05-28",
                max_provider_staleness_days=45,
                max_macro_staleness_days=10,
            )

        operability_context = context["coverage"]["operability"]
        self.assertEqual(operability_context["status"], "bridge")
        self.assertEqual(operability_context["diagnostic_status"], "REVIEW")
        self.assertEqual(operability_context["provenance"]["source_type_weights"], {"database_bridge": 100.0})
        self.assertEqual(operability_context["metrics"]["review_count"], 0)


class FinalReviewEvidenceReadModelContractTests(unittest.TestCase):
    def _integrated_gate_ready_validation(self) -> dict:
        return {
            "selection_source_id": "source-integrated-ready",
            "validation_id": "validation-integrated-ready",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
            "diagnostic_summary": {
                "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
            },
            "checks": [
                {"Criteria": "Data Trust", "Ready": True, "Current": "PASS"},
                {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
            ],
            "provider_coverage": {
                "coverage": {
                    "holdings": {"diagnostic_status": "PASS"},
                    "operability": {"diagnostic_status": "PASS"},
                    "exposure": {"diagnostic_status": "PASS"},
                }
            },
            "diagnostic_results": [],
            "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
            "validation_efficacy_audit": self._gate_audit(
                route="VALIDATION_EFFICACY_READY",
                label="Ready",
                criteria="Runtime replay evidence",
                status="PASS",
                ready=True,
                current="PASS",
                meaning="runtime replay attached",
            ),
            "data_coverage_audit": self._gate_audit(
                route="DATA_COVERAGE_READY",
                label="Ready",
                criteria="Price DB window coverage",
                status="PASS",
                ready=True,
                current="100.0% / symbols=2",
                meaning="data coverage attached",
            ),
            "backtest_realism_audit": self._gate_audit(
                route="BACKTEST_REALISM_READY",
                label="Ready",
                criteria="Transaction cost model",
                status="PASS",
                ready=True,
                current="10 bps / net curve applied",
                meaning="realism evidence attached",
            ),
        }

    def _gate_audit(
        self,
        *,
        route: str,
        label: str,
        criteria: str,
        status: str,
        ready: bool,
        current: str,
        meaning: str,
    ) -> dict:
        return {
            "route": route,
            "route_label": label,
            "rows": [
                {
                    "Criteria": criteria,
                    "Status": status,
                    "Ready": ready,
                    "Current": current,
                    "Meaning": meaning,
                }
            ],
        }

    def _gate_policy_severities(self, packet: dict) -> dict:
        gate_policy = dict(packet.get("gate_policy_snapshot") or {})
        return {
            row.get("Group"): row.get("Severity")
            for row in list(gate_policy.get("policy_rows") or [])
        }

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
                "validation_efficacy_audit": {
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "NOT_RUN",
                            "Meaning": "runtime replay gap",
                        }
                    ]
                },
                "data_coverage_audit": {
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "80.0% / symbols=2",
                            "Meaning": "price coverage gap",
                        }
                    ]
                },
                "backtest_realism_audit": {
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "10 bps / assumption only",
                            "Meaning": "cost model gap",
                        }
                    ]
                },
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
                    "robustness_lab_board": {
                        "summary_rows": [
                            {
                                "Check": "Sensitivity coverage",
                                "Status": "REVIEW",
                                "Current": "computed 3 / review 1 / runtime follow-up 1",
                                "Evidence": "compact robustness lab summary",
                                "Meaning": "sensitivity coverage compact summary",
                            }
                        ]
                    },
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
                "Validation Efficacy",
                "Data Coverage",
                "Backtest Realism",
                "Look-through Exposure",
                "Robustness Lab",
                "Robustness",
                "Paper Observation",
            ],
        )
        self.assertEqual(rows[0]["Criteria"], "Evidence route")
        self.assertTrue(rows[0]["Ready"])
        self.assertEqual(rows[1]["Current"], "REVIEW")
        self.assertEqual(rows[2]["Criteria"], "Runtime replay evidence")
        self.assertFalse(rows[2]["Ready"])
        self.assertEqual(rows[3]["Criteria"], "Price DB window coverage")
        self.assertFalse(rows[3]["Ready"])
        self.assertEqual(rows[4]["Criteria"], "Transaction cost model")
        self.assertFalse(rows[4]["Ready"])
        self.assertEqual(rows[5]["Criteria"], "Holdings Coverage")
        self.assertTrue(rows[5]["Ready"])
        self.assertEqual(rows[6]["Criteria"], "Sensitivity coverage")
        self.assertFalse(rows[6]["Ready"])
        self.assertEqual(rows[7]["Current"], "WATCH")
        self.assertEqual(rows[8]["Current"], "OPTIONAL")

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
            "validation_efficacy_audit": {
                "route": "VALIDATION_EFFICACY_READY",
                "route_label": "Ready",
                "rows": [
                    {
                        "Criteria": "Runtime replay evidence",
                        "Status": "PASS",
                        "Ready": True,
                        "Current": "PASS",
                        "Meaning": "runtime replay attached",
                    }
                ],
            },
            "data_coverage_audit": {
                "route": "DATA_COVERAGE_READY",
                "route_label": "Ready",
                "rows": [
                    {
                        "Criteria": "Price DB window coverage",
                        "Status": "PASS",
                        "Ready": True,
                        "Current": "100.0% / symbols=2",
                        "Meaning": "price coverage attached",
                    }
                ],
            },
            "backtest_realism_audit": {
                "route": "BACKTEST_REALISM_READY",
                "route_label": "Ready",
                "rows": [
                    {
                        "Criteria": "Transaction cost model",
                        "Status": "PASS",
                        "Ready": True,
                        "Current": "10 bps / net curve applied",
                        "Meaning": "cost model attached",
                    }
                ],
            },
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
        sections = [row["Section"] for row in packet["checks"]]
        self.assertIn("Validation Efficacy Audit", sections)
        self.assertIn("Data Coverage Audit", sections)
        self.assertIn("Backtest Realism Audit", sections)
        self.assertEqual(packet["summary"]["validation_efficacy_route"], "VALIDATION_EFFICACY_READY")
        self.assertEqual(packet["summary"]["data_coverage_route"], "DATA_COVERAGE_READY")
        self.assertEqual(packet["summary"]["backtest_realism_route"], "BACKTEST_REALISM_READY")
        assumptions = [row["Assumption"] for row in packet["assumptions_and_limits"]]
        self.assertIn("Hypothetical backtest", assumptions)
        self.assertIn("No live approval / order", assumptions)

    def test_integrated_investability_gate_all_ready_allows_selected_route(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-integrated-ready"},
            validation=self._integrated_gate_ready_validation(),
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(packet["gate_policy_snapshot"]["select_allowed"])
        self.assertFalse(packet["gate_policy_snapshot"]["waiver_supported"])
        severities = self._gate_policy_severities(packet)
        self.assertEqual(severities["validation_efficacy"], "PASS")
        self.assertEqual(severities["data_coverage"], "PASS")
        self.assertEqual(severities["backtest_realism"], "PASS")
        execution_boundary = next(row for row in packet["checks"] if row["Section"] == "Execution Boundary")
        self.assertEqual(execution_boundary["Current"], "live approval disabled / order disabled")

    def test_integrated_investability_gate_multiple_review_gaps_hold_selected_route(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["checks"][3] = {"Criteria": "Provider coverage", "Ready": True, "Current": "REVIEW"}
        validation["diagnostic_summary"] = {
            "status_counts": {"PASS": 8, "REVIEW": 4, "BLOCKED": 0, "NOT_RUN": 0}
        }
        validation["diagnostic_results"] = [
            {
                "domain": "operability_cost_liquidity",
                "title": "10. Operability / Cost / Liquidity",
                "status": "REVIEW",
                "next_action": "provider actual evidence 보강",
            }
        ]
        validation["validation_efficacy_audit"] = self._gate_audit(
            route="VALIDATION_EFFICACY_REVIEW",
            label="Review Required",
            criteria="PIT / look-ahead boundary",
            status="REVIEW",
            ready=False,
            current="needs review",
            meaning="PIT boundary needs review",
        )
        validation["data_coverage_audit"] = self._gate_audit(
            route="DATA_COVERAGE_REVIEW",
            label="Review Required",
            criteria="Survivorship / delisting control",
            status="REVIEW",
            ready=False,
            current="not proven",
            meaning="current listing is not survivorship control",
        )
        validation["backtest_realism_audit"] = self._gate_audit(
            route="BACKTEST_REALISM_REVIEW",
            label="Review Required",
            criteria="Tax / account scope",
            status="REVIEW",
            ready=False,
            current="not modeled",
            meaning="tax/account scope review",
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-integrated-review"},
            validation=validation,
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

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_NEEDS_REVIEW")
        self.assertFalse(packet["select_ready"])
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "hold_or_re_review")
        self.assertEqual(packet["gate_policy_snapshot"]["blockers"], [])
        self.assertTrue(packet["gate_policy_snapshot"]["waiver_required_for_select"])
        severities = self._gate_policy_severities(packet)
        self.assertEqual(severities["provider_coverage"], "REVIEW_REQUIRED")
        self.assertEqual(severities["validation_efficacy"], "REVIEW_REQUIRED")
        self.assertEqual(severities["data_coverage"], "REVIEW_REQUIRED")
        self.assertEqual(severities["backtest_realism"], "REVIEW_REQUIRED")

    def test_integrated_investability_gate_multiple_blockers_block_selected_route(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_efficacy_audit"] = self._gate_audit(
            route="VALIDATION_EFFICACY_NEEDS_INPUT",
            label="Evidence Input Needed",
            criteria="Runtime replay evidence",
            status="NEEDS_INPUT",
            ready=False,
            current="NOT_RUN",
            meaning="runtime replay missing",
        )
        validation["data_coverage_audit"] = self._gate_audit(
            route="DATA_COVERAGE_NEEDS_INPUT",
            label="Coverage Input Needed",
            criteria="Price DB window coverage",
            status="NEEDS_INPUT",
            ready=False,
            current="0.0% / symbols=2",
            meaning="price coverage missing",
        )
        validation["backtest_realism_audit"] = self._gate_audit(
            route="BACKTEST_REALISM_BLOCKED",
            label="Blocked",
            criteria="Execution boundary",
            status="BLOCKED",
            ready=False,
            current="execution model invalid",
            meaning="execution assumption blocks selection",
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-integrated-blocked"},
            validation=validation,
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
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertTrue(packet["gate_policy_snapshot"]["waiver_required_for_select"])
        severities = self._gate_policy_severities(packet)
        self.assertEqual(severities["validation_efficacy"], "BLOCK")
        self.assertEqual(severities["data_coverage"], "BLOCK")
        self.assertEqual(severities["backtest_realism"], "BLOCK")
        self.assertGreaterEqual(len(packet["gate_policy_snapshot"]["blockers"]), 3)

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

    def test_gate_policy_blocks_selected_route_on_validation_efficacy_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-efficacy-gap"},
            validation={
                "selection_source_id": "source-efficacy-gap",
                "validation_id": "validation-efficacy-gap",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
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
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_NEEDS_INPUT",
                    "route_label": "Evidence Input Needed",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "NOT_RUN",
                            "Meaning": "runtime replay missing",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
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
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertTrue(
            any(
                row["Group"] == "validation_efficacy" and row["Severity"] == "BLOCK"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_surfaces_temporal_oos_and_regime_review_rows(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_efficacy_audit"] = {
            "route": "VALIDATION_EFFICACY_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Walk-forward temporal validation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "windows=6 / negative share=0.33",
                    "Meaning": "rolling excess return is unstable",
                },
                {
                    "Criteria": "OOS holdout validation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "out=12 / excess change=-0.08",
                    "Meaning": "holdout performance deteriorated",
                },
                {
                    "Criteria": "Regime split validation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "risk_off bucket short history",
                    "Meaning": "regime evidence needs review",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-temporal-review"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "validation_efficacy"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_NEEDS_REVIEW")
        self.assertFalse(selected_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "REVIEW_REQUIRED")
        self.assertIn("Walk-forward temporal validation", policy_row["Evidence"])
        self.assertIn("OOS holdout validation", policy_row["Evidence"])
        self.assertIn("Regime split validation", policy_row["Evidence"])
        self.assertIn("REVIEW", policy_row["Current"])

    def test_gate_policy_blocks_selected_route_on_temporal_oos_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_efficacy_audit"] = {
            "route": "VALIDATION_EFFICACY_NEEDS_INPUT",
            "route_label": "Evidence Input Needed",
            "rows": [
                {
                    "Criteria": "OOS holdout validation",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "out_sample_months=0",
                    "Meaning": "holdout period is missing",
                },
                {
                    "Criteria": "Regime split validation",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "macro history missing",
                    "Meaning": "regime macro evidence is missing",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-temporal-gap"},
            validation=validation,
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
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "validation_efficacy"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "BLOCK")
        self.assertIn("OOS holdout validation", policy_row["Evidence"])
        self.assertIn("Regime split validation", policy_row["Evidence"])
        self.assertIn("NEEDS_INPUT", policy_row["Current"])

    def test_gate_policy_blocks_selected_route_on_backtest_realism_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-gap"},
            validation={
                "selection_source_id": "source-realism-gap",
                "validation_id": "validation-realism-gap",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
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
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_NEEDS_INPUT",
                    "route_label": "Realism Input Needed",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "missing",
                            "Meaning": "cost model missing",
                        }
                    ],
                },
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
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertTrue(
            any(
                row["Group"] == "backtest_realism" and row["Severity"] == "BLOCK"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_blocks_selected_route_on_data_coverage_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "data-coverage-gap"},
            validation={
                "selection_source_id": "source-data-gap",
                "validation_id": "validation-data-gap",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
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
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_NEEDS_INPUT",
                    "route_label": "Coverage Input Needed",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "0.0% / symbols=2",
                            "Meaning": "price coverage missing",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
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
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertTrue(
            any(
                row["Group"] == "data_coverage" and row["Severity"] == "BLOCK"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_requires_review_on_data_coverage_review(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "data-coverage-review"},
            validation={
                "selection_source_id": "source-data-review",
                "validation_id": "validation-data-review",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
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
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_REVIEW",
                    "route_label": "Review Required",
                    "rows": [
                        {
                            "Criteria": "Survivorship / delisting control",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "not proven",
                            "Meaning": "current listing is not survivorship control",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
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
                row["Group"] == "data_coverage" and row["Severity"] == "REVIEW_REQUIRED"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_requires_review_on_backtest_realism_review(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-review"},
            validation={
                "selection_source_id": "source-realism-review",
                "validation_id": "validation-realism-review",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
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
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_REVIEW",
                    "route_label": "Review Required",
                    "rows": [
                        {
                            "Criteria": "Tax / account scope",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "not modeled",
                            "Meaning": "tax/account scope review",
                        }
                    ],
                },
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
                row["Group"] == "backtest_realism" and row["Severity"] == "REVIEW_REQUIRED"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_surfaces_cost_slippage_and_liquidity_review_rows(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Cost / slippage sensitivity evidence",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "generic robustness only",
                    "Meaning": "cost / slippage axis is missing",
                    "Next Action": "비용 bps / spread / slippage 축의 sensitivity evidence를 확인합니다.",
                },
                {
                    "Criteria": "Liquidity / operability evidence",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "weak_source_or_proxy_liquidity_evidence",
                    "Meaning": "fresh official capacity evidence missing",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-sensitivity-review"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "backtest_realism"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_NEEDS_REVIEW")
        self.assertFalse(selected_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "REVIEW_REQUIRED")
        self.assertIn("Cost / slippage sensitivity evidence", policy_row["Evidence"])
        self.assertIn("Liquidity / operability evidence", policy_row["Evidence"])

    def test_gate_policy_blocks_selected_route_on_cost_slippage_sensitivity_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_NEEDS_INPUT",
            "route_label": "Realism Input Needed",
            "rows": [
                {
                    "Criteria": "Cost / slippage sensitivity evidence",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "cost=- / net=missing_net_cost_curve_proof",
                    "Meaning": "cost input or net cost curve proof missing",
                    "Next Action": "거래비용 입력과 net cost curve proof를 먼저 보강합니다.",
                }
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-sensitivity-gap"},
            validation=validation,
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
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "backtest_realism"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "BLOCK")
        self.assertIn("Cost / slippage sensitivity evidence", policy_row["Evidence"])
        self.assertIn("NEEDS_INPUT", policy_row["Current"])

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
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Provider / freshness evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
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


class SelectedPortfolioMonitoringTimelineContractTests(unittest.TestCase):
    def _selected_row(self) -> dict:
        return {
            "decision_id": "decision-selected",
            "updated_at": "2026-05-28T10:00:00",
            "operation_status": "normal",
            "operation_status_label": "정상 관찰",
            "status_reason": "selected row is operational",
            "evidence_route": "READY_FOR_FINAL_DECISION",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "robustness_route": "READY_FOR_STRESS_SWEEP",
            "paper_observation_route": "PAPER_OBSERVATION_READY",
            "review_cadence": "monthly_or_rebalance_review",
            "review_triggers": ["CAGR deterioration review"],
            "blockers": [],
            "raw_decision": {
                "decision_id": "decision-selected",
                "updated_at": "2026-05-28T10:00:00",
                "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                "selected_practical_portfolio": True,
                "selected_components": [
                    {
                        "title": "Selected Component",
                        "registry_id": "candidate-selected",
                        "target_weight": 100.0,
                        "benchmark": "SPY",
                        "period_start": "2020-01-01",
                        "period_end": "2024-12-31",
                    }
                ],
                "decision_evidence_snapshot": {"route": "READY_FOR_FINAL_DECISION", "checks": [], "blockers": []},
                "investability_evidence_packet": {
                    "route": "INVESTABILITY_PACKET_READY",
                    "gate_policy_snapshot": {
                        "outcome": "select_ready",
                        "select_allowed": True,
                    },
                },
                "paper_tracking_snapshot": {
                    "route": "PAPER_OBSERVATION_READY",
                    "review_cadence": "monthly_or_rebalance_review",
                    "review_triggers": ["CAGR deterioration review"],
                },
            },
        }

    def _candidate_rows_by_id(self) -> dict:
        return {
            "candidate-selected": {
                "registry_id": "candidate-selected",
                "title": "Selected Component",
                "strategy_family": "equal_weight",
                "contract": {
                    "tickers": ["SPY", "QQQ"],
                    "benchmark_ticker": "SPY",
                    "start": "2020-01-01",
                    "end": "2024-12-31",
                    "rebalance_interval": 12,
                },
                "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
            }
        }

    def test_monitoring_timeline_is_read_only_and_requires_recheck_input(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_monitoring_timeline

        timeline = build_selected_portfolio_monitoring_timeline(self._selected_row())

        self.assertEqual(timeline["schema_version"], "selected_monitoring_timeline_v1")
        self.assertEqual(timeline["timeline_status"], "NEEDS_INPUT")
        self.assertEqual([row["event"] for row in timeline["rows"]], [
            "Final Review selection",
            "Evidence gate snapshot",
            "Performance Recheck",
            "Actual Allocation drift",
            "Review trigger preview",
        ])
        self.assertFalse(timeline["execution_boundary"]["monitoring_log_auto_write"])
        self.assertEqual(timeline["execution_boundary"]["write_policy"], "read_only_timeline")

    def test_monitoring_timeline_surfaces_recheck_breach_and_drift_watch(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_monitoring_timeline

        timeline = build_selected_portfolio_monitoring_timeline(
            self._selected_row(),
            recheck_result={
                "status": "ok",
                "verdict_route": "PERFORMANCE_WEAKENED",
                "verdict": "원래 검증 대비 CAGR이 의미 있게 낮아졌습니다.",
                "period": {"start": "2024-01-01", "end": "2026-05-28"},
                "change_summary": {
                    "cagr_delta_vs_baseline": -0.05,
                    "mdd_delta_vs_baseline": -0.02,
                },
            },
            drift_check={
                "route": "DRIFT_WATCH",
                "route_label": "비중 관찰 필요",
                "verdict": "일부 drift가 watch 기준을 넘었습니다.",
                "next_action": "다음 점검일에 drift 확대 여부를 확인합니다.",
                "metrics": {"max_abs_drift": 2.5, "current_weight_total": 100.0},
            },
            alert_preview={
                "alert_route": "WATCH_ALERT",
                "alert_route_label": "관찰 경고",
                "verdict": "watch component를 다음 관찰 주기에 확인합니다.",
                "next_action": "watch component의 drift 확대 여부를 봅니다.",
                "metrics": {"alert_row_count": 2, "review_trigger_count": 1},
            },
        )

        self.assertEqual(timeline["timeline_status"], "BREACHED")
        by_event = {row["event"]: row for row in timeline["rows"]}
        self.assertEqual(by_event["Performance Recheck"]["status"], "BREACHED")
        self.assertEqual(by_event["Actual Allocation drift"]["status"], "WATCH")
        self.assertEqual(by_event["Review trigger preview"]["status"], "WATCH")
        self.assertFalse(timeline["execution_boundary"]["auto_rebalance"])

    def test_selected_continuity_check_requires_recheck_input_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_continuity_check

        continuity = build_selected_portfolio_continuity_check(self._selected_row())

        self.assertEqual(continuity["schema_version"], "selected_continuity_check_v1")
        self.assertEqual(continuity["route"], "CONTINUITY_NEEDS_INPUT")
        checks = {row["Check"]: row for row in continuity["checks"]}
        self.assertEqual(checks["Selected Final Review row"]["Status"], "PASS")
        self.assertEqual(checks["Component target contract"]["Status"], "PASS")
        self.assertEqual(checks["Performance Recheck input"]["Status"], "NEEDS_INPUT")
        self.assertFalse(continuity["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(continuity["execution_boundary"]["live_approval"])

    def test_selected_continuity_check_blocks_non_selected_or_invalid_component_contract(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_continuity_check

        row = self._selected_row()
        row["raw_decision"]["decision_route"] = "HOLD_FOR_MORE_PAPER_TRACKING"
        row["raw_decision"]["selected_practical_portfolio"] = False
        row["raw_decision"]["selected_components"][0]["target_weight"] = 80.0

        continuity = build_selected_portfolio_continuity_check(row)

        self.assertEqual(continuity["route"], "CONTINUITY_BLOCKED")
        checks = {item["Check"]: item for item in continuity["checks"]}
        self.assertEqual(checks["Selected Final Review row"]["Status"], "BLOCKED")
        self.assertEqual(checks["Component target contract"]["Status"], "BLOCKED")
        self.assertFalse(continuity["execution_boundary"]["order_instruction"])

    def test_recheck_comparison_requires_recheck_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_comparison

        comparison = build_selected_portfolio_recheck_comparison(self._selected_row())

        self.assertEqual(comparison["schema_version"], "selected_recheck_comparison_v1")
        self.assertEqual(comparison["route"], "RECHECK_COMPARISON_NOT_RUN")
        self.assertEqual(comparison["overall_status"], "NEEDS_INPUT")
        rows = {row["Check"]: row for row in comparison["rows"]}
        self.assertEqual(rows["Performance Recheck input"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "NEEDS_INPUT")
        self.assertFalse(comparison["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(comparison["execution_boundary"]["live_approval"])
        self.assertFalse(comparison["execution_boundary"]["auto_rebalance"])

    def test_recheck_comparison_surfaces_breach_from_recheck_delta(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_comparison

        comparison = build_selected_portfolio_recheck_comparison(
            self._selected_row(),
            recheck_result={
                "status": "ok",
                "verdict_route": "PERFORMANCE_WEAKENED",
                "verdict": "원래 검증 대비 CAGR이 의미 있게 낮아졌습니다.",
                "period": {
                    "start": "2024-01-01",
                    "end": "2026-05-28",
                    "baseline_start": "2020-01-01",
                    "baseline_end": "2024-12-31",
                    "added_days_vs_baseline": 513,
                },
                "portfolio_summary": {"cagr": 0.04, "mdd": -0.22},
                "baseline_summary": {"cagr": 0.10, "mdd": -0.14, "start": "2020-01-01", "end": "2024-12-31"},
                "benchmark_summary": {"cagr": 0.06},
                "change_summary": {
                    "cagr_delta_vs_baseline": -0.06,
                    "mdd_delta_vs_baseline": -0.08,
                    "benchmark_cagr": 0.06,
                    "net_cagr_spread": -0.02,
                },
                "component_rows": [{"Component": "Selected Component", "Registry ID": "candidate-selected"}],
                "blockers": [],
            },
        )

        self.assertEqual(comparison["route"], "RECHECK_COMPARISON_BREACHED")
        self.assertEqual(comparison["overall_status"], "BREACHED")
        rows = {row["Check"]: row for row in comparison["rows"]}
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "BREACHED")
        self.assertEqual(rows["MDD vs selected baseline"]["Status"], "BREACHED")
        self.assertEqual(rows["Benchmark spread"]["Status"], "BREACHED")
        self.assertFalse(comparison["execution_boundary"]["order_instruction"])
        self.assertFalse(comparison["execution_boundary"]["auto_rebalance"])

    def test_recheck_comparison_ready_when_thesis_holds(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_comparison

        comparison = build_selected_portfolio_recheck_comparison(
            self._selected_row(),
            recheck_result={
                "status": "ok",
                "verdict_route": "SELECTION_THESIS_HOLDS",
                "verdict": "선택한 재검증 기간에서 기존 선정 근거가 유지됩니다.",
                "period": {
                    "start": "2024-01-01",
                    "end": "2026-05-28",
                    "baseline_start": "2020-01-01",
                    "baseline_end": "2024-12-31",
                    "added_days_vs_baseline": 513,
                },
                "portfolio_summary": {"cagr": 0.12, "mdd": -0.12},
                "baseline_summary": {"cagr": 0.10, "mdd": -0.14, "start": "2020-01-01", "end": "2024-12-31"},
                "benchmark_summary": {"cagr": 0.08},
                "change_summary": {
                    "cagr_delta_vs_baseline": 0.02,
                    "mdd_delta_vs_baseline": 0.02,
                    "benchmark_cagr": 0.08,
                    "net_cagr_spread": 0.04,
                },
                "component_rows": [{"Component": "Selected Component", "Registry ID": "candidate-selected"}],
                "blockers": [],
            },
        )

        self.assertEqual(comparison["route"], "RECHECK_COMPARISON_READY")
        self.assertEqual(comparison["overall_status"], "CLEAR")
        self.assertEqual(comparison["metrics"]["breached_count"], 0)
        self.assertEqual(comparison["metrics"]["watch_count"], 0)
        self.assertEqual(comparison["metrics"]["needs_input_count"], 0)

    def test_recheck_readiness_blocks_missing_replay_contract_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_readiness

        readiness = build_selected_portfolio_recheck_readiness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={},
        )

        self.assertEqual(readiness["schema_version"], "selected_recheck_readiness_v1")
        self.assertEqual(readiness["route"], "RECHECK_READINESS_BLOCKED")
        rows = {row["Check"]: row for row in readiness["rows"]}
        self.assertEqual(rows["Selected component contract"]["Status"], "PASS")
        self.assertEqual(rows["Candidate replay contract"]["Status"], "BLOCKED")
        self.assertFalse(readiness["execution_boundary"]["db_write"])
        self.assertFalse(readiness["execution_boundary"]["registry_write"])
        self.assertFalse(readiness["execution_boundary"]["monitoring_log_auto_write"])

    def test_recheck_readiness_ready_when_db_latest_and_replay_contract_exist(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_readiness

        readiness = build_selected_portfolio_recheck_readiness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={
                "candidate-selected": {
                    "registry_id": "candidate-selected",
                    "title": "Selected Component",
                    "strategy_family": "equal_weight",
                    "contract": {
                        "tickers": ["SPY", "QQQ"],
                        "benchmark_ticker": "SPY",
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "rebalance_interval": 12,
                    },
                    "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
                }
            },
        )

        self.assertEqual(readiness["route"], "RECHECK_READINESS_READY")
        self.assertEqual(readiness["metrics"]["blocked_count"], 0)
        self.assertEqual(readiness["metrics"]["needs_input_count"], 0)
        self.assertEqual(readiness["metrics"]["replay_contract_count"], 1)
        self.assertEqual(readiness["metrics"]["symbol_count"], 2)
        rows = {row["Check"]: row for row in readiness["rows"]}
        self.assertEqual(rows["DB latest market date"]["Status"], "PASS")
        self.assertEqual(rows["Default recheck period"]["Status"], "PASS")

    def test_recheck_symbol_freshness_detects_missing_and_stale_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_symbol_freshness

        freshness = build_selected_portfolio_recheck_symbol_freshness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={
                "candidate-selected": {
                    "registry_id": "candidate-selected",
                    "title": "Selected Component",
                    "strategy_family": "equal_weight",
                    "contract": {
                        "tickers": ["SPY", "QQQ"],
                        "benchmark_ticker": "DIA",
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "rebalance_interval": 12,
                    },
                    "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
                }
            },
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                    {"symbol": "QQQ", "latest_date": "2026-05-10", "row_count": 980},
                ]
            ),
        )

        self.assertEqual(freshness["schema_version"], "selected_recheck_symbol_freshness_v1")
        self.assertEqual(freshness["route"], "SYMBOL_FRESHNESS_MISSING")
        self.assertEqual(freshness["metrics"]["symbol_count"], 3)
        self.assertEqual(freshness["metrics"]["stale_count"], 1)
        self.assertEqual(freshness["metrics"]["missing_count"], 1)
        rows = {row["Symbol"]: row for row in freshness["rows"]}
        self.assertEqual(rows["QQQ"]["Status"], "STALE")
        self.assertEqual(rows["DIA"]["Status"], "MISSING")
        self.assertFalse(freshness["execution_boundary"]["db_write"])
        self.assertFalse(freshness["execution_boundary"]["registry_write"])
        self.assertFalse(freshness["execution_boundary"]["monitoring_log_auto_write"])

    def test_recheck_symbol_freshness_ready_when_all_symbols_recent(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_symbol_freshness

        freshness = build_selected_portfolio_recheck_symbol_freshness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={
                "candidate-selected": {
                    "registry_id": "candidate-selected",
                    "title": "Selected Component",
                    "strategy_family": "equal_weight",
                    "contract": {
                        "tickers": ["SPY", "QQQ"],
                        "benchmark_ticker": "SPY",
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "rebalance_interval": 12,
                    },
                    "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
                }
            },
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                    {"symbol": "QQQ", "latest_date": "2026-05-27", "row_count": 999},
                ]
            ),
        )

        self.assertEqual(freshness["route"], "SYMBOL_FRESHNESS_READY")
        self.assertEqual(freshness["metrics"]["pass_count"], 2)
        self.assertEqual(freshness["metrics"]["missing_count"], 0)
        self.assertEqual(freshness["metrics"]["stale_count"], 0)
        rows = {row["Symbol"]: row for row in freshness["rows"]}
        self.assertIn("benchmark", rows["SPY"]["Role"])
        self.assertFalse(freshness["execution_boundary"]["order_instruction"])

    def test_selected_provider_evidence_ready_from_injected_provider_context(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        evidence = build_selected_portfolio_provider_evidence(
            self._selected_row(),
            candidate_rows_by_id=self._candidate_rows_by_id(),
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Holdings",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF holdings snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Exposure",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF exposure snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "Macro Context",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": None,
                        "Source Mix": "fred: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "Macro context is available.",
                    },
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                    "summary_rows": [{"Check": "Holdings coverage", "Status": "PASS"}],
                },
            },
        )

        self.assertEqual(evidence["schema_version"], "selected_provider_evidence_v1")
        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_READY")
        self.assertEqual(evidence["metrics"]["provider_symbol_count"], 2)
        self.assertEqual(evidence["metrics"]["needs_input_count"], 0)
        self.assertEqual(evidence["symbol_weights"], {"QQQ": 50.0, "SPY": 50.0})
        self.assertFalse(evidence["execution_boundary"]["db_write"])
        self.assertFalse(evidence["execution_boundary"]["provider_collection"])
        self.assertFalse(evidence["execution_boundary"]["monitoring_log_auto_write"])

    def test_selected_provider_evidence_surfaces_not_run_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        evidence = build_selected_portfolio_provider_evidence(
            self._selected_row(),
            candidate_rows_by_id=self._candidate_rows_by_id(),
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Holdings",
                        "Coverage": "not_run",
                        "Diagnostic Status": "NOT_RUN",
                        "Coverage Weight": 0.0,
                        "Source Mix": "-",
                        "Freshness": "missing",
                        "As Of Range": "-",
                        "Summary": "ETF holdings snapshot coverage is unavailable.",
                    },
                    {
                        "Area": "ETF Exposure",
                        "Coverage": "partial",
                        "Diagnostic Status": "REVIEW",
                        "Coverage Weight": 50.0,
                        "Source Mix": "official: 50.0%",
                        "Freshness": "stale",
                        "As Of Range": "2026-04-01 -> 2026-04-01",
                        "Summary": "ETF exposure snapshot covers 50.0% of target weight.",
                    },
                ],
                "look_through_board": {
                    "status": "REVIEW",
                    "holdings_coverage_weight": 0.0,
                    "exposure_coverage_weight": 50.0,
                    "unknown_exposure_weight": 50.0,
                    "top_holding_weight": 0.0,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_NEEDS_DATA")
        self.assertEqual(evidence["metrics"]["needs_input_count"], 1)
        self.assertEqual(evidence["metrics"]["review_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["ETF Exposure"]["Status"], "REVIEW")
        self.assertFalse(evidence["execution_boundary"]["registry_write"])
        self.assertFalse(evidence["execution_boundary"]["order_instruction"])

    def test_selected_provider_evidence_marks_component_fallback_as_review(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        row = self._selected_row()
        row["raw_decision"]["selected_components"][0]["universe"] = "SPY QQQ"

        evidence = build_selected_portfolio_provider_evidence(
            row,
            candidate_rows_by_id={},
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    }
                ],
                "look_through_board": {"status": "PASS"},
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_REVIEW")
        self.assertEqual(evidence["symbol_weights"], {"QQQ": 50.0, "SPY": 50.0})
        self.assertEqual(evidence["metrics"]["fallback_contract_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["Selected Symbol Contract"]["Status"], "REVIEW")
        self.assertFalse(evidence["execution_boundary"]["monitoring_log_auto_write"])


class DecisionDossierContractTests(unittest.TestCase):
    def _final_decision_row(self) -> dict:
        return {
            "decision_id": "decision-dossier",
            "created_at": "2026-05-28T09:00:00",
            "updated_at": "2026-05-28T10:00:00",
            "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
            "selected_practical_portfolio": True,
            "source_type": "practical_validation_result",
            "source_id": "source-dossier",
            "source_title": "GTAA selected portfolio",
            "selection_source_id": "source-dossier",
            "validation_id": "validation-dossier",
            "selected_components": [
                {
                    "title": "GTAA component",
                    "registry_id": "candidate-gtaa",
                    "target_weight": 100.0,
                    "benchmark": "SPY",
                }
            ],
            "decision_evidence_snapshot": {
                "route": "READY_FOR_FINAL_DECISION",
                "score": 8.2,
                "checks": [
                    {
                        "Criteria": "Portfolio validation",
                        "Ready": True,
                        "Current": "READY_FOR_FINAL_REVIEW",
                        "Meaning": "validation evidence attached",
                        "Score": 2.4,
                    }
                ],
                "blockers": [],
            },
            "investability_evidence_packet": {
                "route": "INVESTABILITY_PACKET_READY",
                "checks": [
                    {
                        "Section": "Execution Boundary",
                        "Ready": True,
                        "Current": "live approval disabled / order disabled",
                        "Meaning": "not an order",
                    }
                ],
                "gate_policy_snapshot": {
                    "schema_version": "investability_gate_policy_v1",
                    "outcome": "select_ready",
                    "select_allowed": True,
                    "blockers": [],
                    "review_required": [],
                    "policy_rows": [
                        {
                            "Group": "benchmark",
                            "Status": "PASS",
                            "Severity": "PASS",
                            "Current": "PASS",
                            "Evidence": "benchmark parity attached",
                            "Required Action": "none",
                        }
                    ],
                },
            },
            "risk_and_validation_snapshot": {
                "validation_route": "READY_FOR_FINAL_REVIEW",
                "validation_score": 8.5,
                "diagnostic_summary": {"status_counts": {"PASS": 10, "REVIEW": 1, "NOT_RUN": 1}},
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP", "robustness_score": 7.8},
            },
            "paper_tracking_snapshot": {
                "route": "PAPER_OBSERVATION_READY",
                "review_cadence": "monthly_or_rebalance_review",
                "review_triggers": ["CAGR deterioration review"],
                "checks": [
                    {
                        "Criteria": "Review triggers",
                        "Ready": True,
                        "Current": "1",
                        "Meaning": "trigger attached",
                    }
                ],
            },
            "operator_decision": {
                "reason": "검증 근거가 충분합니다.",
                "constraints": "실제 투자 전 금액과 중단 기준 확인",
                "next_action": "Selected Dashboard에서 사후 점검",
            },
        }

    def test_decision_dossier_is_read_only_markdown_export(self) -> None:
        from app.services.backtest_evidence_read_model import build_decision_dossier

        dossier = build_decision_dossier(self._final_decision_row())

        self.assertEqual(dossier["schema_version"], "decision_dossier_v1")
        self.assertEqual(dossier["decision"]["decision_id"], "decision-dossier")
        self.assertEqual(dossier["metrics"]["component_count"], 1)
        self.assertGreaterEqual(dossier["metrics"]["evidence_check_count"], 1)
        self.assertEqual(dossier["execution_boundary"]["write_policy"], "read_only_dossier")
        self.assertFalse(dossier["execution_boundary"]["report_auto_write"])
        self.assertFalse(dossier["execution_boundary"]["live_approval"])
        self.assertIn("# Final Decision Dossier", dossier["markdown"])
        self.assertIn("decision-dossier", dossier["filename"])
        self.assertIn("not live approval", dossier["markdown"])

    def test_decision_dossier_can_include_selected_monitoring_timeline(self) -> None:
        from app.services.backtest_evidence_read_model import build_decision_dossier

        dossier = build_decision_dossier(
            {"raw_decision": self._final_decision_row()},
            monitoring_timeline={
                "schema_version": "selected_monitoring_timeline_v1",
                "timeline_status": "WATCH",
                "timeline_label": "관찰",
                "conclusion": "watch event가 있습니다.",
                "rows": [
                    {
                        "order": 3,
                        "event": "Performance Recheck",
                        "timestamp": "2026-05-28",
                        "status": "WATCH",
                        "status_label": "관찰",
                        "signal": "PARTIAL_RECHECK",
                        "next_action": "다음 점검에서 확인",
                        "source": "session_state.performance_recheck",
                    }
                ],
                "metrics": {"row_count": 1},
            },
        )

        self.assertTrue(dossier["monitoring_timeline"]["present"])
        self.assertTrue(dossier["metrics"]["monitoring_timeline_present"])
        self.assertIn("Performance Recheck", dossier["markdown"])
        self.assertFalse(dossier["execution_boundary"]["monitoring_log_auto_write"])


if __name__ == "__main__":
    unittest.main()
