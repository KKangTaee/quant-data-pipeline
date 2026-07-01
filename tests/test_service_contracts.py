from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
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


def _risk_on_momentum_fixture() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    symbols = ["AAA", "BBB", "CCC", "DDD"]
    dates = pd.bdate_range("2024-01-01", periods=90)
    price_rows: list[dict[str, object]] = []
    for symbol_idx, symbol in enumerate(symbols):
        base = 20.0 + symbol_idx * 5.0
        for day_idx, day in enumerate(dates):
            close = base * (1.0 + 0.004 * day_idx)
            if day_idx > 55 and symbol in {"AAA", "BBB"}:
                close *= 1.0 + 0.003 * (day_idx - 55)
            volume = 800_000 + (20_000 * day_idx if day_idx > 55 else 2_000 * day_idx) + symbol_idx * 100_000
            price_rows.append(
                {
                    "symbol": symbol,
                    "date": day,
                    "open": close * 0.995,
                    "high": close * 1.01,
                    "low": close * 0.99,
                    "close": close,
                    "volume": volume,
                }
            )

    statement_rows = [
        {
            "symbol": symbol,
            "period_end": pd.Timestamp(f"{year}-12-31"),
            "latest_available_at": pd.Timestamp(f"{year + 1}-03-01"),
            "operating_income": 100.0,
            "total_debt": 50.0,
            "shareholders_equity": 200.0,
            "total_assets": 500.0,
        }
        for symbol in symbols
        for year in [2020, 2021, 2022, 2023]
    ]
    macro_scores = pd.DataFrame(
        {
            "date": dates,
            "risk_on_mean_z": 0.5,
            "rate_pressure_mean_z": 0.0,
            "dollar_pressure_mean_z": 0.0,
            "safe_haven_mean_z": 0.0,
            "standardized_symbol_count": 8,
        }
    )
    return pd.DataFrame(price_rows), pd.DataFrame(statement_rows), macro_scores


class BacktestPresetCatalogContractTests(unittest.TestCase):
    def test_gtaa_spy_low_mdd_top3_preset_is_available(self) -> None:
        from app.web.backtest_common import GTAA_PRESETS, GTAA_PRESET_PARAMETER_DEFAULTS

        preset_name = "GTAA SPY Low-MDD Style Top-3"

        self.assertIn(preset_name, GTAA_PRESETS)
        self.assertEqual(
            GTAA_PRESETS[preset_name],
            ["QQQ", "SOXX", "MTUM", "QUAL", "USMV", "IAU", "IEF", "TLT"],
        )

        strongest_preset = "GTAA SPY Low-MDD Style Top-2 ADV20"
        self.assertIn(strongest_preset, GTAA_PRESETS)
        self.assertEqual(
            GTAA_PRESETS[strongest_preset],
            ["QQQ", "SOXX", "MTUM", "QUAL", "USMV", "IAU", "IEF", "TLT"],
        )
        self.assertEqual(
            GTAA_PRESET_PARAMETER_DEFAULTS[strongest_preset],
            {
                "top": 2,
                "interval": 4,
                "score_lookback_months": [1, 6],
                "trend_filter_window": 200,
                "risk_off_mode": "cash_only",
                "defensive_tickers": ["IEF", "TLT"],
                "benchmark_ticker": "SPY",
                "min_price_filter": 5.0,
                "min_avg_dollar_volume_20d_m_filter": 20.0,
                "transaction_cost_bps": 10.0,
            },
        )


class RiskOnMomentumSwingContractTests(unittest.TestCase):
    def test_risk_on_momentum_atr_indicator_uses_simple_true_range_mean(self) -> None:
        from finance.indicators import add_atr

        rows = pd.DataFrame(
            [
                {"symbol": "AAA", "date": "2024-01-01", "high": 12.0, "low": 10.0, "close": 11.0},
                {"symbol": "AAA", "date": "2024-01-02", "high": 14.0, "low": 11.0, "close": 13.0},
                {"symbol": "AAA", "date": "2024-01-03", "high": 15.0, "low": 12.0, "close": 12.5},
            ]
        )

        result = add_atr(rows, period=2)

        self.assertAlmostEqual(float(result.loc[0, "true_range"]), 2.0)
        self.assertAlmostEqual(float(result.loc[1, "true_range"]), 3.0)
        self.assertAlmostEqual(float(result.loc[2, "true_range"]), 3.0)
        self.assertTrue(pd.isna(result.loc[0, "atr2"]))
        self.assertAlmostEqual(float(result.loc[1, "atr2"]), 2.5)
        self.assertAlmostEqual(float(result.loc[2, "atr2"]), 3.0)

    def test_risk_on_momentum_executes_d_plus_one_and_logs_signal_holding_days(self) -> None:
        from finance.swing import RiskOnMomentumConfig, run_risk_on_momentum_backtest

        prices, statements, macro_scores = _risk_on_momentum_fixture()
        result = run_risk_on_momentum_backtest(
            prices,
            config=RiskOnMomentumConfig(
                start="2024-03-15",
                end="2024-05-03",
                start_balance=10_000.0,
                macro_filter_enabled=True,
                scanner_top_n_per_day=10,
                random_seed=1,
            ),
            macro_scores=macro_scores,
            statement_history=statements,
        )

        self.assertFalse(result.trade_log_df.empty)
        closed = result.trade_log_df[result.trade_log_df["exit_reason"] != "END_OF_BACKTEST"]
        self.assertFalse(closed.empty)
        self.assertTrue((pd.to_datetime(closed["entry_date"]) > pd.to_datetime(closed["entry_signal_date"])).all())
        self.assertLessEqual(int(closed["holding_days"].max()), 5)
        self.assertFalse(result.scanner_df.empty)
        self.assertIn("QUEUED_BUY", set(result.scanner_df["status"]))

    def test_risk_on_momentum_macro_hard_filter_blocks_new_entries(self) -> None:
        from finance.swing import RiskOnMomentumConfig, run_risk_on_momentum_backtest

        prices, statements, macro_scores = _risk_on_momentum_fixture()
        blocked_macro = macro_scores.copy()
        blocked_macro["risk_on_mean_z"] = -1.0

        result = run_risk_on_momentum_backtest(
            prices,
            config=RiskOnMomentumConfig(
                start="2024-03-15",
                end="2024-05-03",
                start_balance=10_000.0,
                macro_filter_enabled=True,
                scanner_top_n_per_day=10,
            ),
            macro_scores=blocked_macro,
            statement_history=statements,
        )

        self.assertTrue(result.trade_log_df.empty)
        self.assertFalse(result.result_df["Macro Filter Pass"].any())

    def test_risk_on_momentum_atr_based_uses_signal_date_atr(self) -> None:
        from finance.swing import RiskOnMomentumConfig, prepare_swing_feature_frame, run_risk_on_momentum_backtest

        prices, statements, macro_scores = _risk_on_momentum_fixture()
        features = prepare_swing_feature_frame(prices, statement_history=statements)
        result = run_risk_on_momentum_backtest(
            prices,
            config=RiskOnMomentumConfig(
                start="2024-03-15",
                end="2024-05-03",
                start_balance=10_000.0,
                exit_mode="atr_based",
                atr_period=14,
                stop_atr_multiple=0.8,
                take_profit_atr_multiple=1.2,
                macro_filter_enabled=True,
                scanner_top_n_per_day=10,
                random_seed=1,
            ),
            macro_scores=macro_scores,
            statement_history=statements,
            prepared_features=features,
        )

        closed = result.trade_log_df[result.trade_log_df["exit_reason"] != "END_OF_BACKTEST"].copy()
        self.assertFalse(closed.empty)
        first = closed.iloc[0]
        feature_row = features[
            (features["symbol"] == first["symbol"])
            & (pd.to_datetime(features["date"]).dt.strftime("%Y-%m-%d") == first["entry_signal_date"])
        ].iloc[0]
        self.assertEqual(first["exit_mode"], "atr_based")
        self.assertAlmostEqual(float(first["entry_atr"]), float(feature_row["atr14"]))
        self.assertEqual(int(first["atr_period"]), 14)

    def test_risk_on_momentum_ranking_penalty_allows_pressure_without_hard_filtering(self) -> None:
        from finance.swing import RiskOnMomentumConfig, run_risk_on_momentum_backtest

        prices, statements, macro_scores = _risk_on_momentum_fixture()
        pressure_macro = macro_scores.copy()
        pressure_macro["risk_on_mean_z"] = 0.5
        pressure_macro["rate_pressure_mean_z"] = 2.0

        hard_filter_result = run_risk_on_momentum_backtest(
            prices,
            config=RiskOnMomentumConfig(
                start="2024-03-15",
                end="2024-05-03",
                macro_filter_enabled=True,
                macro_filter_mode="hard_filter",
                scanner_top_n_per_day=10,
            ),
            macro_scores=pressure_macro,
            statement_history=statements,
        )
        penalty_result = run_risk_on_momentum_backtest(
            prices,
            config=RiskOnMomentumConfig(
                start="2024-03-15",
                end="2024-05-03",
                macro_filter_enabled=True,
                macro_filter_mode="ranking_penalty",
                rate_pressure_penalty_weight=10.0,
                scanner_top_n_per_day=10,
            ),
            macro_scores=pressure_macro,
            statement_history=statements,
        )

        self.assertTrue(hard_filter_result.trade_log_df.empty)
        self.assertFalse(penalty_result.trade_log_df.empty)
        self.assertTrue((penalty_result.scanner_df["macro_penalty_total"] > 0).any())
        self.assertEqual(set(penalty_result.trade_log_df["macro_filter_mode"]), {"ranking_penalty"})

    def test_history_payload_restores_risk_on_momentum_settings(self) -> None:
        from app.web.backtest_history_helpers import _build_history_payload

        payload = _build_history_payload(
            {
                "strategy_key": "risk_on_momentum_5d",
                "tickers": [],
                "input_start": "2024-01-01",
                "input_end": "2024-05-31",
                "timeframe": "1d",
                "option": "close_based",
                "universe_mode": "top1000",
                "preset_name": "Top1000",
                "universe_limit": 1000,
                "start_balance": 25_000.0,
                "strategy_execution_mode": "close_based",
                "exit_mode": "atr_based",
                "max_holding_days": 5,
                "stop_loss_pct": -2.5,
                "take_profit_pct": 5.0,
                "atr_period": 14,
                "stop_atr_multiple": 1.0,
                "take_profit_atr_multiple": 2.0,
                "max_new_positions_per_day": 3,
                "max_total_positions": 3,
                "macro_filter_enabled": True,
                "macro_filter_mode": "ranking_penalty",
                "risk_on_min": 0.0,
                "rate_pressure_max": 1.0,
                "dollar_pressure_max": 1.0,
                "safe_haven_max": 1.0,
                "rate_pressure_penalty_weight": 9.0,
                "dollar_pressure_penalty_weight": 8.0,
                "safe_haven_penalty_weight": 7.0,
                "min_price_filter": 5.0,
                "min_avg_dollar_volume_20d": 20_000_000.0,
                "min_avg_volume_20d": 500_000.0,
                "random_iterations": 50,
                "scanner_top_n_per_day": 50,
                "run_comparison_suite": True,
                "run_sensitivity_suite": True,
            }
        )

        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload["strategy_key"], "risk_on_momentum_5d")
        self.assertEqual(payload["universe_mode"], "top1000")
        self.assertEqual(payload["max_holding_days"], 5)
        self.assertEqual(payload["stop_loss_pct"], -2.5)
        self.assertEqual(payload["exit_mode"], "atr_based")
        self.assertEqual(payload["macro_filter_mode"], "ranking_penalty")
        self.assertEqual(payload["stop_atr_multiple"], 1.0)
        self.assertEqual(payload["rate_pressure_penalty_weight"], 9.0)
        self.assertTrue(payload["macro_filter_enabled"])
        self.assertEqual(payload["min_avg_dollar_volume_20d"], 20_000_000.0)

    def test_risk_on_momentum_sp500_universe_resolves_market_universe(self) -> None:
        from app.runtime.backtest.runners import risk_on_momentum as runtime

        with (
            patch.object(
                runtime,
                "load_market_cap_universe_members",
                return_value=[{"symbol": "AAPL"}, {"symbol": "MSFT"}],
            ) as load_universe,
            patch.object(runtime, "load_top_symbols_from_asset_profile") as fallback_universe,
        ):
            symbols, mode, preset, limit, source = runtime._resolve_risk_on_momentum_universe(
                tickers=[],
                universe_mode="snp500",
                preset_name=None,
                universe_limit=None,
            )

        load_universe.assert_called_once_with("SP500", universe_limit=500)
        fallback_universe.assert_not_called()
        self.assertEqual(symbols, ["AAPL", "MSFT"])
        self.assertEqual(mode, "sp500")
        self.assertEqual(preset, "S&P 500")
        self.assertEqual(limit, 500)
        self.assertEqual(source, "market_cap_universe_members:SP500")

    def test_risk_on_momentum_sp500_universe_requires_membership_rows(self) -> None:
        from app.runtime import backtest as facade_runtime
        from app.runtime.backtest.runners import risk_on_momentum as runtime

        with (
            patch.object(runtime, "load_market_cap_universe_members", return_value=[]),
            patch.object(runtime, "load_top_symbols_from_asset_profile") as fallback_universe,
        ):
            with self.assertRaises(facade_runtime.BacktestDataError):
                runtime._resolve_risk_on_momentum_universe(
                    tickers=[],
                    universe_mode="sp500",
                    preset_name=None,
                    universe_limit=None,
                )

        fallback_universe.assert_not_called()

    def test_risk_on_momentum_v2_analysis_frames_are_generated(self) -> None:
        from finance.swing import RiskOnMomentumConfig, run_risk_on_momentum_backtest
        from finance.swing_analysis import (
            build_quality_warnings,
            build_swing_comparison_suite,
            build_swing_sensitivity_suite,
            build_swing_stability_tables,
            build_trade_cause_summary,
        )

        prices, statements, macro_scores = _risk_on_momentum_fixture()
        config = RiskOnMomentumConfig(
            start="2024-03-15",
            end="2024-05-03",
            start_balance=10_000.0,
            macro_filter_enabled=True,
            scanner_top_n_per_day=10,
        )
        result = run_risk_on_momentum_backtest(
            prices,
            config=config,
            macro_scores=macro_scores,
            statement_history=statements,
        )

        comparison = build_swing_comparison_suite(
            prices,
            config=config,
            primary_result=result,
            macro_scores=macro_scores,
            statement_history=statements,
            prepared_features=None,
        )
        sensitivity = build_swing_sensitivity_suite(
            prices,
            config=config,
            macro_scores=macro_scores,
            statement_history=statements,
            prepared_features=None,
        )
        stability = build_swing_stability_tables(result)
        trade_causes = build_trade_cause_summary(result.trade_log_df)
        warnings = build_quality_warnings(
            result=result,
            random_summary_df=pd.DataFrame(),
            benchmark_comparison_df=pd.DataFrame(),
            sensitivity_df=sensitivity,
            price_freshness={"status": "ok"},
            macro_scores=macro_scores,
            macro_filter_enabled=True,
        )

        self.assertIn("comparison_df", comparison)
        self.assertFalse(comparison["comparison_df"].empty)
        self.assertFalse(sensitivity.empty)
        self.assertIn("yearly_stability_df", stability)
        self.assertFalse(trade_causes.empty)
        self.assertFalse(warnings.empty)


class PracticalValidationServiceContractTests(unittest.TestCase):
    def test_market_sentiment_overlay_is_context_only_for_practical_validation(self) -> None:
        from app.services import backtest_practical_validation as service

        snapshot_rows = pd.DataFrame(
            [
                {
                    "series_id": "CNN_FEAR_GREED",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "CNN Fear & Greed Index",
                    "category": "sentiment_index",
                    "units": "score_0_100",
                    "value": 62.4,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "greed"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "AAII_BEARISH",
                    "observation_date": pd.Timestamp("2026-06-03"),
                    "source": "aaii_sentiment_survey",
                    "source_type": "official",
                    "source_mode": "html",
                    "series_name": "AAII Bearish Sentiment",
                    "category": "sentiment_survey",
                    "units": "percent",
                    "value": 28.0,
                    "coverage_status": "actual",
                    "missing_fields_json": "{}",
                    "collected_at": pd.Timestamp("2026-06-04 14:50:00"),
                    "staleness_days": 2,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "AAII_BULL_BEAR_SPREAD",
                    "observation_date": pd.Timestamp("2026-06-03"),
                    "source": "aaii_sentiment_survey",
                    "source_type": "official",
                    "source_mode": "html",
                    "series_name": "AAII Bull-Bear Spread",
                    "category": "sentiment_survey",
                    "units": "percentage_point",
                    "value": 12.5,
                    "coverage_status": "actual",
                    "missing_fields_json": "{}",
                    "collected_at": pd.Timestamp("2026-06-04 14:50:00"),
                    "staleness_days": 2,
                    "snapshot_status": "actual",
                },
            ]
        )

        overlay = service.build_market_sentiment_context_overlay(
            snapshot_rows=snapshot_rows,
            history_rows=pd.DataFrame(),
            today=date(2026, 6, 5),
        )

        self.assertEqual(overlay["status"], "OK")
        self.assertEqual(overlay["risk_context"]["state"], "risk-on")
        self.assertEqual(overlay["risk_context"]["source_phase"], "GREED_LEANING")
        self.assertEqual(overlay["metrics"]["cnn_fear_greed"], 62.4)
        self.assertEqual(overlay["metrics"]["aaii_bull_bear_spread"], 12.5)
        self.assertIn("탐욕", overlay["headline"])
        self.assertTrue(overlay["boundary"]["context_only"])
        self.assertEqual(overlay["boundary"]["gate_effect"], "none")
        self.assertFalse(overlay["boundary"]["affects_pass_blocker"])
        self.assertFalse(overlay["boundary"]["trade_signal"])
        self.assertFalse(overlay["boundary"]["live_approval"])
        self.assertFalse(overlay["boundary"]["broker_order"])
        self.assertFalse(overlay["boundary"]["auto_rebalance"])
        self.assertFalse(overlay["boundary"]["registry_write"])
        self.assertEqual(
            {row["Metric"] for row in overlay["evidence_rows"]},
            {"CNN Fear & Greed", "AAII Bearish", "AAII Bull-Bear Spread"},
        )

    def test_market_sentiment_overlay_remains_context_only_on_downstream_surfaces(self) -> None:
        from app.services import backtest_practical_validation as service

        snapshot_rows = pd.DataFrame(
            [
                {
                    "series_id": "CNN_FEAR_GREED",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "CNN Fear & Greed Index",
                    "category": "sentiment_index",
                    "units": "score_0_100",
                    "value": 26.0,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "fear"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "AAII_BEARISH",
                    "observation_date": pd.Timestamp("2026-06-03"),
                    "source": "aaii_sentiment_survey",
                    "source_type": "official",
                    "source_mode": "html",
                    "series_name": "AAII Bearish Sentiment",
                    "category": "sentiment_survey",
                    "units": "percent",
                    "value": 48.5,
                    "coverage_status": "actual",
                    "missing_fields_json": "{}",
                    "collected_at": pd.Timestamp("2026-06-04 14:50:00"),
                    "staleness_days": 2,
                    "snapshot_status": "actual",
                },
            ]
        )

        overlays = [
            service.build_market_sentiment_context_overlay(
                snapshot_rows=snapshot_rows,
                history_rows=pd.DataFrame(),
                today=date(2026, 6, 5),
                surface=surface,
            )
            for surface in ("Final Review", "Operations > Portfolio Monitoring")
        ]

        self.assertEqual([overlay["surface"] for overlay in overlays], ["Final Review", "Operations > Portfolio Monitoring"])
        self.assertEqual({overlay["risk_context"]["state"] for overlay in overlays}, {"risk-off"})
        for overlay in overlays:
            boundary = overlay["boundary"]
            self.assertTrue(boundary["context_only"])
            self.assertEqual(boundary["gate_effect"], "none")
            self.assertFalse(boundary["affects_pass_blocker"])
            self.assertFalse(boundary["trade_signal"])
            self.assertFalse(boundary["live_approval"])
            self.assertFalse(boundary["broker_order"])
            self.assertFalse(boundary["auto_rebalance"])
            self.assertFalse(boundary["registry_write"])
            self.assertFalse(boundary["saved_setup_write"])
            self.assertFalse(boundary["monitoring_signal"])
            self.assertIn(overlay["surface"], boundary["message"])

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

    def test_final_review_source_options_hide_blocked_practical_validation_results(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_source_options

        blocked = {
            "validation_id": "validation-blocked",
            "selection_source_id": "source-blocked",
            "source_title": "Blocked source",
            "final_review_gate": {"can_save_and_move": False},
        }
        ready = {
            "validation_id": "validation-ready",
            "selection_source_id": "source-ready",
            "source_title": "Ready source",
            "final_review_gate": {"can_save_and_move": True},
            "selected_route_preflight": {"select_allowed": True},
        }

        options = _build_final_review_source_options(
            [{"registry_id": "legacy-candidate", "title": "Legacy candidate"}],
            [{"proposal_id": "legacy-proposal"}],
            practical_validation_rows=[blocked, ready],
            session_practical_source={"validation_result": blocked},
            include_legacy_sources=False,
        )

        self.assertEqual(len(options), 1)
        self.assertEqual(options[0]["source_type"], "practical_validation_result")
        self.assertEqual(options[0]["source_id"], "validation-ready")

    def test_practical_validation_registry_serializes_db_scalar_payloads(self) -> None:
        from app.runtime.backtest.stores import portfolio_selection

        with tempfile.TemporaryDirectory() as tmp_dir:
            result_file = Path(tmp_dir) / "PRACTICAL_VALIDATION_RESULTS.jsonl"
            with patch.object(portfolio_selection, "PRACTICAL_VALIDATION_RESULT_FILE", result_file):
                portfolio_selection.append_practical_validation_result(
                    {
                        "selection_source_id": "source-json-safe",
                        "input_evidence": {
                            "data_coverage_context": {
                                "price_window_rows": [
                                    {
                                        "symbol": "SPY",
                                        "window_row_count": Decimal("2558"),
                                        "first_date": date(2020, 1, 31),
                                        "latest_seen": pd.Timestamp("2026-05-29"),
                                    }
                                ]
                            }
                        },
                    }
                )
            loaded = json.loads(result_file.read_text(encoding="utf-8").strip())

        row = loaded["input_evidence"]["data_coverage_context"]["price_window_rows"][0]
        self.assertEqual(row["window_row_count"], 2558)
        self.assertEqual(row["first_date"], "2020-01-31")
        self.assertEqual(row["latest_seen"], "2026-05-29T00:00:00")

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

    def test_compact_selection_history_extracts_monthly_holdings(self) -> None:
        from app.services.backtest_practical_validation_source import compact_selection_history_from_result_df

        result_df = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Rebalancing": True,
                    "Next Ticker": ["SPY", "TLT"],
                    "Next Balance": [600.0, 400.0],
                    "Raw Selected Ticker": ["SPY", "TLT", "GLD"],
                    "Overlay Rejected Ticker": ["GLD"],
                    "Cash": 0.0,
                    "Total Balance": 1000.0,
                    "Total Return": 0.0,
                },
                {
                    "Date": "2020-02-29",
                    "Rebalancing": False,
                    "Next Ticker": ["SPY", "TLT"],
                    "Next Balance": [610.0, 410.0],
                    "Cash": 0.0,
                    "Total Balance": 1020.0,
                    "Total Return": 0.02,
                },
            ]
        )

        rows = compact_selection_history_from_result_df(result_df, component_title="GTAA", component_weight=100.0)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2020-01-31")
        self.assertEqual(rows[0]["component"], "GTAA")
        self.assertEqual(rows[0]["selected_tickers"], ["SPY", "TLT"])
        self.assertEqual(rows[0]["target_weights"], [0.6, 0.4])
        self.assertEqual(rows[0]["raw_selected_tickers"], ["SPY", "TLT", "GLD"])
        self.assertEqual(rows[0]["overlay_rejected_tickers"], ["GLD"])
        self.assertIn("Selected SPY 60.0%, TLT 40.0%", rows[0]["interpretation"])

    def test_selection_source_preserves_selection_history_snapshot(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_candidate_draft

        selection_history = [
            {
                "date": "2020-01-31",
                "component": "Quality Snapshot",
                "selected_tickers": ["AAPL", "MSFT"],
                "target_weights": [0.5, 0.5],
            }
        ]

        source = build_selection_source_from_candidate_draft(
            {
                "source_kind": "latest_backtest_run",
                "strategy_key": "quality_snapshot_strict_annual",
                "strategy_name": "Quality Snapshot (Strict Annual)",
                "result_snapshot": {"start_date": "2020-01-31", "end_date": "2020-12-31"},
                "settings_snapshot": {"tickers": ["AAPL", "MSFT"], "rebalance_interval": 1},
                "selection_history_snapshot": selection_history,
            }
        )

        self.assertEqual(source["selection_history"], selection_history)
        self.assertEqual(source["components"][0]["selection_history"], selection_history)

    def test_saved_mix_source_preserves_component_selection_history(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_saved_mix_prefill

        source = build_selection_source_from_saved_mix_prefill(
            {
                "source_kind": "weighted_portfolio_mix",
                "weighted_portfolio_id": "mix-1",
                "weighted_portfolio_name": "Two Sleeve Mix",
                "weighted_summary": {"cagr": 0.1, "mdd": -0.2},
                "weighted_period": {"start": "2020-01-31", "end": "2020-12-31"},
                "components": [
                    {
                        "registry_id": "component-1",
                        "strategy_name": "Quality Snapshot (Strict Annual)",
                        "target_weight": 60.0,
                        "selection_history": [{"date": "2020-01-31", "selected_tickers": ["AAPL"]}],
                    }
                ],
            }
        )

        self.assertEqual(source["construction"]["target_weight_total"], 60.0)
        self.assertEqual(source["components"][0]["selection_history"][0]["selected_tickers"], ["AAPL"])

    def test_saved_mix_source_preserves_weight_rationale_and_cost_snapshots(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_saved_mix_prefill

        source = build_selection_source_from_saved_mix_prefill(
            {
                "source_kind": "weighted_portfolio_mix",
                "weighted_portfolio_id": "mix-2",
                "weighted_portfolio_name": "Role Aware Mix",
                "weighted_summary": {"cagr": 0.1, "mdd": -0.2},
                "weighted_period": {"start": "2020-01-31", "end": "2020-12-31"},
                "weighted_curve_snapshot": [{"date": "2020-01-31", "value": 1000.0}],
                "components": [
                    {
                        "registry_id": "component-core",
                        "strategy_name": "Equal Weight",
                        "candidate_role": "weighted_mix_component",
                        "proposal_role": "core_anchor",
                        "target_weight": 60.0,
                        "weight_reason": "Core exposure",
                        "selection_history": [{"date": "2020-01-31", "selected_tickers": ["SPY"]}],
                        "contract": {"transaction_cost_bps": 10.0},
                    },
                    {
                        "registry_id": "component-defense",
                        "strategy_name": "Risk Parity",
                        "candidate_role": "weighted_mix_component",
                        "proposal_role": "defensive_sleeve",
                        "target_weight": 40.0,
                        "weight_reason": "Drawdown dampener",
                        "selection_history": [{"date": "2020-01-31", "selected_tickers": ["TLT"]}],
                        "contract": {"transaction_cost_bps": 10.0},
                    },
                ],
            }
        )

        self.assertEqual(source["components"][0]["weight_reason"], "Core exposure")
        self.assertEqual(source["components"][1]["role_source"], "weighted_mix_component")
        self.assertEqual(source["cost_model_snapshot"]["transaction_cost_bps"], 10.0)
        self.assertEqual(source["turnover_evidence_snapshot"]["turnover_source"], "component_selection_history")
        self.assertEqual(source["net_cost_curve_snapshot"]["net_cost_curve_rows"], 1)
        self.assertEqual(
            source["components"][0]["replay_contract"]["cost_model_snapshot"]["cost_model_source"],
            "component_contracts",
        )

    def test_validation_source_traits_classify_single_etf_tactical_candidate(self) -> None:
        from app.services.backtest_practical_validation_modules import infer_validation_source_traits

        traits = infer_validation_source_traits(
            {
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [
                    {
                        "strategy_key": "gtaa",
                        "target_weight": 100.0,
                        "universe": ["SPY", "QQQ", "GLD", "IEF"],
                        "replay_contract": {
                            "settings_snapshot": {
                                "tickers": ["SPY", "QQQ", "GLD", "IEF"],
                                "interval": 2,
                            }
                        },
                    }
                ],
            }
        )

        self.assertTrue(traits["is_single_component"])
        self.assertFalse(traits["is_weighted_mix"])
        self.assertTrue(traits["is_etf_like"])
        self.assertTrue(traits["is_tactical"])
        self.assertTrue(traits["is_high_turnover"])
        self.assertEqual(traits["symbol_count"], 4)

    def test_validation_module_gate_blocks_missing_required_runtime_replay(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": False, "Current": "NOT_RUN"},
            {"Criteria": "Runtime period coverage", "Ready": False, "Current": "NOT_RUN"},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
            {"domain": "regime_macro_suitability", "status": "REVIEW"},
            {"domain": "sentiment_risk_on_off_overlay", "status": "REVIEW"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [{"strategy_key": "gtaa", "target_weight": 100.0, "universe": ["SPY", "TLT"]}],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=pass_row,
            risk_contribution_rows=[{"Criteria": "Pairwise correlation", "Status": "NEEDS_INPUT"}],
            component_role_weight_rows=[{"Criteria": "Component role source coverage", "Status": "REVIEW"}],
            backtest_realism_rows=pass_row,
        )

        gate = plan["final_review_gate"]
        self.assertFalse(gate["can_save_and_move"])
        self.assertEqual(gate["route"], "BLOCKED_FOR_FINAL_REVIEW")
        self.assertEqual([row["module_id"] for row in gate["blocking_modules"]], ["latest_replay"])
        self.assertEqual(gate["blocking_modules"][0]["gate_effect"], "Blocks Final Review")
        self.assertIn("전략 재검증", gate["blocking_modules"][0]["gate_reason"])
        self.assertEqual(
            gate["blocking_modules"][0]["resolution_surface"],
            "3. 최신 데이터 기준 전략 재검증",
        )
        self.assertIn("전략 재검증 실행", gate["blocking_modules"][0]["resolution_action"])
        modules = {row["module_id"]: row for row in plan["modules"]}
        self.assertFalse(modules["risk_contribution"]["applies"])
        self.assertEqual(modules["risk_contribution"]["status"], "NOT_APPLICABLE")
        self.assertEqual(modules["risk_contribution"]["gate_effect"], "Not applicable")
        display_rows = {row["Module"]: row for row in plan["module_display_rows"]}
        self.assertEqual(
            display_rows["Latest Runtime Replay"]["Fix Location"],
            "3. 최신 데이터 기준 전략 재검증",
        )

    def test_validation_board_map_marks_single_gtaa_conditional_boards(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": True},
            {"Criteria": "Runtime period coverage", "Ready": True},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
            {"domain": "regime_macro_suitability", "status": "REVIEW"},
            {"domain": "sentiment_risk_on_off_overlay", "status": "REVIEW"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [
                    {
                        "strategy_key": "gtaa",
                        "target_weight": 100.0,
                        "universe": ["SPY", "QQQ", "GLD", "IEF"],
                        "replay_contract": {
                            "settings_snapshot": {
                                "tickers": ["SPY", "QQQ", "GLD", "IEF"],
                                "interval": 2,
                            }
                        },
                    }
                ],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=pass_row,
            risk_contribution_rows=[{"Criteria": "Pairwise correlation", "Status": "NEEDS_INPUT"}],
            component_role_weight_rows=[{"Criteria": "Component role source coverage", "Status": "REVIEW"}],
            backtest_realism_rows=pass_row,
        )

        modules = {row["module_id"]: row for row in plan["modules"]}
        self.assertTrue(modules["provider_investability"]["applies"])
        self.assertFalse(modules["leverage_inverse"]["applies"])
        self.assertTrue(modules["macro_regime"]["applies"])
        self.assertFalse(modules["risk_contribution"]["applies"])
        self.assertFalse(modules["component_role_weight"]["applies"])

        display_rows = {row["Module"]: row for row in plan["module_display_rows"]}
        self.assertEqual(display_rows["Risk Contribution"]["Module Type"], "Conditional")
        self.assertEqual(display_rows["Risk Contribution"]["Applies"], "No")
        self.assertIn("Risk Contribution Audit", display_rows["Risk Contribution"]["Evidence Boards"])
        self.assertEqual(display_rows["Risk Contribution"]["Fix Location"], "Risk Contribution Audit")

        board_rows = {row["Board"]: row for row in plan["board_display_rows"]}
        self.assertEqual(board_rows["Provider Coverage"]["Applies"], "Yes")
        self.assertEqual(board_rows["Look-through Exposure Board"]["Applies"], "Yes")
        self.assertEqual(board_rows["Risk Contribution Audit"]["Applies"], "No")
        self.assertEqual(board_rows["Component Role / Weight Audit"]["Applies"], "No")
        self.assertIn("single component", board_rows["Risk Contribution Audit"]["Applicability"])

    def test_validation_module_gate_allows_ready_with_review_modules(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": True},
            {"Criteria": "Runtime period coverage", "Ready": True},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [{"strategy_key": "equal_weight", "target_weight": 100.0, "universe": ["SPY", "TLT"]}],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=[{"Criteria": "Component weight concentration", "Status": "REVIEW"}],
            risk_contribution_rows=[],
            component_role_weight_rows=[],
            backtest_realism_rows=[{"Criteria": "Cost / slippage sensitivity evidence", "Status": "REVIEW"}],
        )

        gate = plan["final_review_gate"]
        self.assertTrue(gate["can_save_and_move"])
        self.assertEqual(gate["route"], "READY_WITH_REVIEW")
        self.assertEqual(gate["blocking_modules"], [])
        self.assertTrue(
            {row["module_id"] for row in gate["review_modules"]}
            >= {"construction_risk", "backtest_realism"}
        )
        self.assertTrue(
            all(row["gate_effect"] == "Final Review review" for row in gate["review_modules"])
        )
        display_rows = {row["Module"]: row for row in plan["module_display_rows"]}
        self.assertIn("Benchmark / Comparator Parity", display_rows)
        self.assertEqual(display_rows["Benchmark / Comparator Parity"]["Gate Effect"], "Ready")

    def test_validation_module_gate_blocks_selected_route_preflight_gaps(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": True},
            {"Criteria": "Runtime period coverage", "Ready": True},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [{"strategy_key": "equal_weight", "target_weight": 100.0, "universe": ["SPY", "TLT"]}],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=pass_row,
            risk_contribution_rows=[],
            component_role_weight_rows=[],
            backtest_realism_rows=[{"Criteria": "Net performance policy", "Status": "REVIEW"}],
            selected_route_preflight={
                "select_allowed": False,
                "policy_outcome": "hold_or_re_review",
                "review_required": ["Backtest Realism: Net performance policy: gross-only evidence"],
                "next_action": "net performance evidence를 보강합니다.",
            },
        )

        gate = plan["final_review_gate"]
        self.assertFalse(gate["can_save_and_move"])
        self.assertEqual(gate["route"], "BLOCKED_FOR_FINAL_REVIEW")
        self.assertIn("selected-route", gate["verdict"])
        self.assertEqual(gate["blocking_modules"][0]["module_id"], "selected_route_preflight")
        modules = {row["module_id"]: row for row in plan["modules"]}
        self.assertEqual(modules["selected_route_preflight"]["status"], "NEEDS_INPUT")
        self.assertEqual(modules["selected_route_preflight"]["gate_effect"], "Blocks Final Review")
        self.assertIn("gross-only", modules["selected_route_preflight"]["resolution_action"])

    def test_service_imports_do_not_load_streamlit(self) -> None:
        script = """
import sys
import app.runtime
import app.runtime.backtest
import app.runtime.backtest.read_models.candidate_library
import app.runtime.backtest.result_bundle
import app.services.backtest_component_role_weight_audit
import app.services.backtest_construction_risk_audit
import app.services.backtest_data_coverage_audit
import app.services.backtest_realism_audit
import app.services.backtest_evidence_read_model
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_diagnostics
import app.services.backtest_practical_validation_board_registry
import app.services.backtest_practical_validation_modules
import app.services.backtest_practical_validation
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_replay
import app.services.backtest_practical_validation_source
import app.services.backtest_risk_contribution_audit
import app.services.backtest_selected_route_preflight
import app.services.backtest_validation_efficacy
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
import app.runtime.backtest.read_models.candidate_library
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
import app.services.backtest_component_role_weight_audit
import app.services.backtest_data_coverage_audit
import app.services.backtest_realism_audit
import app.services.backtest_construction_risk_audit
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_curve_context
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_stress_sensitivity
import app.services.backtest_practical_validation_source
import app.services.backtest_risk_contribution_audit
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


class RiskContributionAuditContractTests(unittest.TestCase):
    def _validation(
        self,
        *,
        diagnostic_status: str = "PASS",
        average_correlation: float | None = 0.25,
        max_correlation: float | None = 0.45,
        max_risk_contribution: float | None = 0.55,
        monthly_return_rows: int = 48,
        curve_source: str = "actual_runtime_replay",
        curve_rows: int = 120,
        dependency_status: str = "PASS",
    ) -> dict:
        diagnostic_metrics: dict[str, object] = {"monthly_return_rows": monthly_return_rows}
        if average_correlation is not None:
            diagnostic_metrics["average_correlation"] = average_correlation
        if max_correlation is not None:
            diagnostic_metrics["max_correlation"] = max_correlation
        if max_risk_contribution is not None:
            diagnostic_metrics["max_risk_contribution"] = max_risk_contribution
        return {
            "metrics": {"active_components": 2},
            "curve_evidence": {
                "component_curve_rows": [
                    {
                        "Component": "Core",
                        "Weight": 60.0,
                        "Curve Source": curve_source,
                        "Rows": curve_rows,
                    },
                    {
                        "Component": "Defense",
                        "Weight": 40.0,
                        "Curve Source": curve_source,
                        "Rows": curve_rows,
                    },
                ]
            },
            "diagnostic_results": [
                {
                    "domain": "correlation_diversification_risk_contribution",
                    "status": diagnostic_status,
                    "summary": "Correlation and risk contribution evidence available.",
                    "metrics": diagnostic_metrics,
                    "evidence_rows": [
                        {
                            "Component": "Core",
                            "Weight": 60.0,
                            "Risk Contribution Proxy": 0.55,
                        },
                        {
                            "Component": "Defense",
                            "Weight": 40.0,
                            "Risk Contribution Proxy": 0.45,
                        },
                    ],
                }
            ],
            "sensitivity_interpretation": {
                "rows": [
                    {
                        "Check": "Component dependency",
                        "Status": dependency_status,
                        "Finding": "Drop-one dependency is contained.",
                        "Why It Matters": "No single component explains the portfolio.",
                    }
                ]
            },
        }

    def test_ready_audit_uses_runtime_component_curves_without_writes(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_READY,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(self._validation())

        self.assertEqual(audit["route"], RISK_CONTRIBUTION_READY)
        self.assertEqual(audit["source_strength"], "runtime_component_curves")
        self.assertEqual(audit["metrics"]["pass"], 5)
        self.assertEqual(audit["metrics"]["monthly_return_rows"], 48)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["raw_matrix_persistence"])

    def test_missing_component_matrix_needs_input(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_NEEDS_INPUT,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(
            {
                "metrics": {"active_components": 2},
                "diagnostic_results": [
                    {
                        "domain": "correlation_diversification_risk_contribution",
                        "status": "NOT_RUN",
                        "summary": "component return matrix missing",
                        "metrics": {"monthly_return_rows": 0},
                    }
                ],
                "sensitivity_interpretation": {
                    "rows": [{"Check": "Component dependency", "Status": "NOT_RUN"}]
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], RISK_CONTRIBUTION_NEEDS_INPUT)
        self.assertEqual(audit["source_strength"], "missing_component_matrix")
        self.assertEqual(rows_by_criteria["Component return matrix coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Pairwise correlation"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Risk contribution concentration"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Drop-one component dependency"]["Status"], "NEEDS_INPUT")

    def test_high_correlation_and_risk_contribution_trigger_review(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_REVIEW,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(
            self._validation(
                average_correlation=0.76,
                max_correlation=0.92,
                max_risk_contribution=0.85,
                curve_source="embedded_result_curve",
                dependency_status="REVIEW",
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], RISK_CONTRIBUTION_REVIEW)
        self.assertEqual(audit["source_strength"], "embedded_component_curves")
        self.assertEqual(rows_by_criteria["Pairwise correlation"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Risk contribution concentration"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Drop-one component dependency"]["Status"], "REVIEW")

    def test_db_price_proxy_source_triggers_review(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_REVIEW,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(self._validation(curve_source="db_price_proxy"))

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], RISK_CONTRIBUTION_REVIEW)
        self.assertEqual(audit["source_strength"], "db_price_proxy")
        self.assertEqual(rows_by_criteria["Component return matrix coverage"]["Status"], "REVIEW")


class ComponentRoleWeightAuditContractTests(unittest.TestCase):
    def _validation(
        self,
        *,
        profile_id: str = "balanced_core",
        primary_goal: str = "balanced",
        max_weight_review: float = 75.0,
        components: list[dict] | None = None,
    ) -> dict:
        components = list(
            components
            or [
                {
                    "title": "Core Trend",
                    "strategy_name": "GTAA",
                    "proposal_role": "core_anchor",
                    "target_weight": 50.0,
                    "weight_reason": "Core allocation",
                },
                {
                    "title": "Defense",
                    "strategy_name": "Risk Parity",
                    "proposal_role": "defensive_sleeve",
                    "target_weight": 30.0,
                    "weight_reason": "Drawdown dampener",
                },
                {
                    "title": "Diversifier",
                    "strategy_name": "Equal Weight",
                    "proposal_role": "diversifier",
                    "target_weight": 20.0,
                    "weight_reason": "Diversification sleeve",
                },
            ]
        )
        return {
            "validation_profile": {
                "profile_id": profile_id,
                "profile_label": "균형형",
                "answers": {"primary_goal": primary_goal},
                "thresholds": {"max_weight_review": max_weight_review},
            },
            "metrics": {
                "active_components": len(components),
                "weight_total": sum(float(component.get("target_weight") or 0.0) for component in components),
                "max_weight": max([float(component.get("target_weight") or 0.0) for component in components], default=0.0),
            },
            "selection_source_snapshot": {
                "source_kind": "weighted_portfolio_mix",
                "components": components,
            },
        }

    def test_ready_audit_uses_explicit_roles_without_writes(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_READY,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(self._validation())

        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_READY)
        self.assertEqual(audit["source_strength"], "explicit_role_metadata")
        self.assertEqual(audit["metrics"]["pass"], 6)
        self.assertEqual(audit["metrics"]["explicit_role_weight"], 100.0)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])
        self.assertFalse(audit["execution_boundary"]["role_preset_persistence"])

    def test_missing_multi_component_roles_need_input(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_NEEDS_INPUT,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(
            self._validation(
                components=[
                    {"title": "A", "strategy_name": "GTAA", "target_weight": 60.0},
                    {"title": "B", "strategy_name": "Equal Weight", "target_weight": 40.0},
                ]
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_NEEDS_INPUT)
        self.assertEqual(audit["source_strength"], "missing_role_metadata")
        self.assertEqual(rows_by_criteria["Component role source coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Role concentration discipline"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Weight rationale coverage"]["Status"], "NEEDS_INPUT")

    def test_profile_weight_and_role_concentration_trigger_review(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_REVIEW,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(
            self._validation(
                components=[
                    {
                        "title": "Core",
                        "strategy_name": "GTAA",
                        "proposal_role": "core_anchor",
                        "target_weight": 90.0,
                        "weight_reason": "High conviction core",
                    },
                    {
                        "title": "Diversifier",
                        "strategy_name": "Equal Weight",
                        "proposal_role": "diversifier",
                        "target_weight": 10.0,
                        "weight_reason": "Small diversifier",
                    },
                ]
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_REVIEW)
        self.assertEqual(rows_by_criteria["Profile-aware weight discipline"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Role concentration discipline"]["Status"], "REVIEW")

    def test_hedged_profile_without_matching_role_triggers_review(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_REVIEW,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(
            self._validation(
                profile_id="hedged_tactical",
                primary_goal="hedged_tactical",
                max_weight_review=70.0,
                components=[
                    {
                        "title": "Core",
                        "strategy_name": "Equal Weight",
                        "proposal_role": "core_anchor",
                        "target_weight": 60.0,
                        "weight_reason": "Core exposure",
                    },
                    {
                        "title": "Growth",
                        "strategy_name": "Quality Growth",
                        "proposal_role": "growth_sleeve",
                        "target_weight": 40.0,
                        "weight_reason": "Growth exposure",
                    },
                ],
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_REVIEW)
        self.assertEqual(rows_by_criteria["Profile intent role fit"]["Status"], "REVIEW")


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

    def test_streamlit_shell_delegates_ingestion_console_to_dedicated_module(self) -> None:
        import ast

        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertIn("app.web.ingestion_console", imported_modules)
        self.assertNotIn("_render_ingestion_console", function_names)

    def test_streamlit_shell_does_not_expose_legacy_pages_sidebar(self) -> None:
        import ast

        pages_dir = Path("app/web/pages")
        self.assertFalse(pages_dir.exists())

        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }

        self.assertIn("app.web.backtest_page", imported_modules)
        self.assertNotIn("app.web.pages.backtest", imported_modules)

    def test_backtest_page_uses_compact_korean_english_workflow_tabs(self) -> None:
        source = Path("app/web/backtest_page.py").read_text(encoding="utf-8")
        selector_body = source[source.index("def _render_backtest_panel_selector"):]
        selector_body = selector_body[: selector_body.index("def render_backtest_tab")]

        self.assertIn("st.pills(", selector_body)
        self.assertIn("format_func=_backtest_workflow_stage_label", selector_body)
        self.assertIn("후보 분석 · Backtest Analysis", source)
        self.assertIn("실전 검증 · Practical Validation", source)
        self.assertIn("최종 검토 · Final Review", source)
        self.assertIn("stBaseButton-pillsActive", source)
        self.assertIn("#ff4b4b", source)
        self.assertNotIn("segmented_control", selector_body)
        self.assertNotIn("st.radio(", selector_body)

    def test_backtest_page_removes_unused_guide_snapshot_and_reference_panels(self) -> None:
        page_source = Path("app/web/backtest_page.py").read_text(encoding="utf-8")
        analysis_source = Path("app/web/backtest_analysis.py").read_text(encoding="utf-8")
        common_source = Path("app/web/backtest_common.py").read_text(encoding="utf-8")

        self.assertNotIn("Backtest 사용 안내", page_source)
        self.assertNotIn("Strategy Capability Snapshot", common_source)
        self.assertNotIn("_render_strategy_capability_snapshot", common_source)
        self.assertNotIn("전략 개발 참고", analysis_source)
        self.assertNotIn("backtest_analysis_show_research_reference_panels", analysis_source)

    def test_ingestion_console_module_owns_render_entrypoint(self) -> None:
        from app.web.ingestion_console import render_ingestion_page

        self.assertTrue(callable(render_ingestion_page))

    def test_ingestion_console_delegates_read_only_diagnostics_to_service_facade(self) -> None:
        import ast

        source = Path("app/web/ingestion_console.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertIn("app.services.ingestion_diagnostics", imported_modules)
        self.assertNotIn("app.jobs.diagnostics", imported_modules)
        self.assertNotIn("finance.data.financial_statements", imported_modules)
        self.assertNotIn("finance.loaders", imported_modules)
        self.assertNotIn("finance.loaders.price", imported_modules)
        self.assertNotIn("_load_price_window_summary_cached", function_names)

    def test_ingestion_diagnostics_service_owns_public_entrypoints(self) -> None:
        from app.services.ingestion_diagnostics import (
            load_price_window_preflight_summary,
            run_price_stale_diagnosis,
            run_statement_coverage_diagnosis,
            run_statement_pit_inspection,
        )

        self.assertTrue(callable(load_price_window_preflight_summary))
        self.assertTrue(callable(run_price_stale_diagnosis))
        self.assertTrue(callable(run_statement_coverage_diagnosis))
        self.assertTrue(callable(run_statement_pit_inspection))

    def test_backtest_compare_delegates_visual_shell_to_component_module(self) -> None:
        import ast

        source = Path("app/web/backtest_compare/page.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertIn("app.web.backtest_compare.components", imported_modules)
        self.assertNotIn("_render_portfolio_mix_builder_css", function_names)
        self.assertNotIn("_render_portfolio_mix_flow_strip", function_names)
        self.assertNotIn("_render_portfolio_mix_section_head", function_names)
        self.assertNotIn("_html_text", function_names)
        self.assertNotIn("_status_chip_tone", function_names)

    def test_backtest_compare_components_module_owns_visual_entrypoints(self) -> None:
        from app.web.backtest_compare.components import (
            html_text,
            render_component_result_overview_cards,
            render_portfolio_mix_builder_css,
            render_portfolio_mix_flow_strip,
            render_portfolio_mix_section_head,
            status_chip_tone,
        )

        self.assertTrue(callable(render_portfolio_mix_builder_css))
        self.assertTrue(callable(render_portfolio_mix_flow_strip))
        self.assertTrue(callable(render_portfolio_mix_section_head))
        self.assertTrue(callable(render_component_result_overview_cards))
        self.assertEqual(html_text("<unsafe>"), "&lt;unsafe&gt;")
        self.assertEqual(status_chip_tone("Ready For Next Review"), "pass")

    def test_backtest_runtime_facade_delegates_risk_on_momentum_to_dedicated_module(self) -> None:
        import ast

        source = Path("app/runtime/backtest/facade.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imported_modules.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertIn("app.runtime.backtest.runners.risk_on_momentum", imported_modules)
        self.assertNotIn("run_risk_on_momentum_5d_backtest_from_db", function_names)
        self.assertNotIn("_resolve_risk_on_momentum_universe", function_names)

    def test_risk_on_momentum_runtime_module_owns_public_entrypoint(self) -> None:
        from app.runtime import backtest
        from app.runtime.backtest.runners.risk_on_momentum import run_risk_on_momentum_5d_backtest_from_db

        self.assertIs(backtest.run_risk_on_momentum_5d_backtest_from_db, run_risk_on_momentum_5d_backtest_from_db)

    def test_backtest_runtime_facade_delegates_real_money_helpers_to_dedicated_module(self) -> None:
        import ast

        source = Path("app/runtime/backtest/facade.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imported_modules.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertIn("app.runtime.backtest.real_money", imported_modules)
        self.assertNotIn("_apply_real_money_hardening", function_names)
        self.assertNotIn("_build_deployment_readiness_contract", function_names)
        self.assertNotIn("_apply_transaction_cost_postprocess", function_names)
        self.assertNotIn("_build_benchmark_result_df", function_names)

    def test_real_money_runtime_module_owns_facade_helper_contracts(self) -> None:
        from app.runtime import backtest
        from app.runtime.backtest.real_money import (
            ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            _apply_real_money_hardening,
            _apply_transaction_cost_postprocess,
            _build_deployment_readiness_contract,
        )

        self.assertIs(backtest._apply_real_money_hardening, _apply_real_money_hardening)
        self.assertIs(backtest._apply_transaction_cost_postprocess, _apply_transaction_cost_postprocess)
        self.assertIs(backtest._build_deployment_readiness_contract, _build_deployment_readiness_contract)
        self.assertEqual(backtest.ETF_REAL_MONEY_DEFAULT_BENCHMARK, ETF_REAL_MONEY_DEFAULT_BENCHMARK)

    def test_backtest_runtime_facade_delegates_strict_family_to_dedicated_module(self) -> None:
        import ast

        source = Path("app/runtime/backtest/facade.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imported_modules.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        function_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertIn("app.runtime.backtest.runners.strict_factor", imported_modules)
        self.assertNotIn("inspect_strict_annual_price_freshness", function_names)
        self.assertNotIn("run_quality_snapshot_strict_annual_backtest_from_db", function_names)
        self.assertNotIn("run_value_snapshot_strict_annual_backtest_from_db", function_names)
        self.assertNotIn("run_quality_value_snapshot_strict_annual_backtest_from_db", function_names)
        self.assertNotIn("_run_statement_quality_bundle", function_names)

    def test_strict_runtime_module_owns_facade_runner_contracts(self) -> None:
        from app.runtime import backtest
        from app.runtime.backtest.runners.strict_factor import (
            inspect_strict_annual_price_freshness,
            run_quality_snapshot_strict_annual_backtest_from_db,
            run_quality_value_snapshot_strict_annual_backtest_from_db,
            run_value_snapshot_strict_annual_backtest_from_db,
        )

        self.assertIs(backtest.inspect_strict_annual_price_freshness, inspect_strict_annual_price_freshness)
        self.assertIs(
            backtest.run_quality_snapshot_strict_annual_backtest_from_db,
            run_quality_snapshot_strict_annual_backtest_from_db,
        )
        self.assertIs(
            backtest.run_value_snapshot_strict_annual_backtest_from_db,
            run_value_snapshot_strict_annual_backtest_from_db,
        )
        self.assertIs(
            backtest.run_quality_value_snapshot_strict_annual_backtest_from_db,
            run_quality_value_snapshot_strict_annual_backtest_from_db,
        )


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


class JobResultArtifactContractTests(unittest.TestCase):
    def test_earnings_symbol_diagnostics_become_failure_rows(self) -> None:
        from app.jobs.result_artifacts import _extract_failure_rows

        rows = _extract_failure_rows(
            {
                "job_name": "collect_earnings_calendar",
                "status": "partial_success",
                "started_at": "2026-05-28 10:00:00",
                "finished_at": "2026-05-28 10:00:01",
                "failed_symbols": ["AAA", "BBB"],
                "message": "Earnings calendar completed with issues.",
                "details": {
                    "missing_symbols": ["AAA"],
                    "symbol_diagnostics": [
                        {
                            "symbol": "AAA",
                            "status": "missing",
                            "reason": "outside_window",
                            "detail": "Provider date was outside the selected window.",
                        },
                        {
                            "symbol": "BBB",
                            "status": "failed",
                            "reason": "provider_error",
                            "detail": "provider unavailable",
                        },
                    ]
                },
            }
        )

        self.assertEqual(
            [(row["symbol"], row["kind"], row["detail"]) for row in rows],
            [
                ("AAA", "earnings_missing", "outside_window"),
                ("BBB", "earnings_failed", "provider_error"),
            ],
        )


class OverviewAutomationContractTests(unittest.TestCase):
    def test_market_session_banner_reports_open_day_times(self) -> None:
        from app.web.overview.session_helpers import US_EASTERN_TZ, _market_session_banner_model

        model = _market_session_banner_model(now=datetime(2026, 5, 29, 10, 0, tzinfo=US_EASTERN_TZ))

        self.assertEqual(model["status"], "장중")
        self.assertIn("2026-05-29 ET", model["title"])
        self.assertEqual(model["items"][0]["value"], "05-29 22:30 KST")
        self.assertEqual(model["items"][0]["detail"], "09:30 ET")
        self.assertEqual(model["items"][1]["value"], "05-30 05:00 KST")
        self.assertEqual(model["items"][1]["detail"], "16:00 ET")

    def test_market_session_banner_reports_weekend_closure(self) -> None:
        from app.web.overview.session_helpers import US_EASTERN_TZ, _market_session_banner_model

        model = _market_session_banner_model(now=datetime(2026, 5, 30, 10, 0, tzinfo=US_EASTERN_TZ))

        self.assertEqual(model["status"], "휴장")
        self.assertIn("주말", model["detail"])
        self.assertEqual(model["items"][1]["value"], "06-01 22:30 KST")
        self.assertEqual(model["items"][1]["detail"], "09:30 ET")

    def test_market_session_banner_reports_observed_holiday_closure(self) -> None:
        from app.web.overview.session_helpers import US_EASTERN_TZ, _market_session_banner_model

        model = _market_session_banner_model(now=datetime(2026, 7, 3, 10, 0, tzinfo=US_EASTERN_TZ))

        self.assertEqual(model["status"], "휴장")
        self.assertIn("Independence Day", model["detail"])

    def test_market_context_session_payload_uses_previous_trading_day_when_closed(self) -> None:
        from app.web.overview.session_helpers import US_EASTERN_TZ, _market_context_session_payload

        model = _market_context_session_payload(now=datetime(2026, 6, 20, 10, 0, tzinfo=US_EASTERN_TZ))

        self.assertEqual(model["phase"], "휴장")
        self.assertFalse(model["is_market_open_now"])
        self.assertEqual(model["session_date"], "2026-06-20")
        self.assertEqual(model["basis_date"], "2026-06-18")

    def test_snapshot_status_labels_intraday_quote_time(self) -> None:
        from app.web.overview.session_helpers import _snapshot_status_items

        items = _snapshot_status_items(
            {
                "status": "OK",
                "coverage": {
                    "price_mode": "Intraday Snapshot",
                    "snapshot_time_utc": "2026-05-29 21:32",
                    "returnable_count": 503,
                    "universe_count": 503,
                },
            }
        )

        self.assertEqual(items[0]["title"], "Effective Quote Time")
        self.assertEqual(items[0]["value"], "2026-05-29 21:32")
        self.assertIn("previous close", items[0]["detail"])

    def test_snapshot_status_labels_sparse_eod_date(self) -> None:
        from app.web.overview.session_helpers import _snapshot_status_items

        items = _snapshot_status_items(
            {
                "status": "OK",
                "coverage": {
                    "price_mode": "EOD DB",
                    "latest_raw_date": "2026-05-28",
                    "effective_end_date": "2026-05-27",
                    "returnable_count": 500,
                    "universe_count": 503,
                },
            }
        )

        self.assertEqual(items[0]["title"], "Effective EOD Date")
        self.assertEqual(items[0]["value"], "2026-05-27")
        self.assertIn("latest raw 2026-05-28 is sparse", items[0]["detail"])

    def test_browser_auto_refresh_timing_shows_remaining_cadence(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_timing

        timing = _browser_auto_refresh_timing(
            {
                "status": "skipped",
                "plan": [
                    {
                        "label": "S&P 500 Daily Snapshot",
                        "reason": "cadence not due",
                        "cadence_minutes": 5,
                        "last_finished_at": "2026-05-29 10:00:00",
                        "next_due_at": "2026-05-29 10:05:00",
                    }
                ],
            },
            now=datetime(2026, 5, 29, 10, 2, 30),
        )

        self.assertEqual(timing["title"], "다음 갱신까지 2분 30초")
        self.assertEqual(timing["progress_pct"], 50)
        self.assertEqual(timing["next_due_at"], "2026-05-29 10:05:00")

    def test_browser_auto_refresh_timing_waits_outside_market_hours(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_timing

        timing = _browser_auto_refresh_timing(
            {
                "status": "skipped",
                "plan": [
                    {
                        "label": "S&P 500 Daily Snapshot",
                        "reason": "outside US market hours",
                        "cadence_minutes": 5,
                        "last_finished_at": "2026-05-29 10:00:00",
                        "next_due_at": "2026-05-29 10:05:00",
                    }
                ],
            },
            now=datetime(2026, 5, 29, 10, 2, 30),
        )

        self.assertEqual(timing["title"], "미국 정규장 대기")
        self.assertEqual(timing["progress_pct"], 0)

    def test_browser_auto_refresh_timing_rebases_success_to_next_cadence(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_timing

        timing = _browser_auto_refresh_timing(
            {
                "status": "success",
                "finished_at": "2026-05-29 10:03:00",
                "plan": [
                    {
                        "label": "S&P 500 Daily Snapshot",
                        "reason": "due",
                        "should_run": True,
                        "cadence_minutes": 5,
                        "last_finished_at": "2026-05-29 09:58:00",
                        "next_due_at": "2026-05-29 10:03:00",
                    }
                ],
            },
            now=datetime(2026, 5, 29, 10, 4, 0),
        )

        self.assertEqual(timing["title"], "방금 갱신됨. 다음 갱신까지 4분")
        self.assertEqual(timing["next_due_at"], "2026-05-29 10:08:00")
        self.assertEqual(timing["progress_pct"], 20)

    def test_browser_auto_refresh_check_due_uses_next_due(self) -> None:
        from app.web.overview_dashboard import _should_run_browser_auto_refresh_check

        summary = {
            "status": "skipped",
            "plan": [
                {
                    "label": "S&P 500 Daily Snapshot",
                    "reason": "cadence not due",
                    "cadence_minutes": 5,
                    "last_finished_at": "2026-05-29 10:00:00",
                    "next_due_at": "2026-05-29 10:05:00",
                }
            ],
        }

        self.assertFalse(
            _should_run_browser_auto_refresh_check(summary, now=datetime(2026, 5, 29, 10, 4, 59))
        )
        self.assertTrue(
            _should_run_browser_auto_refresh_check(summary, now=datetime(2026, 5, 29, 10, 5, 0))
        )

    def test_browser_auto_refresh_completion_label_uses_actionable_status(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_completion_label

        self.assertEqual(
            _browser_auto_refresh_completion_label({"status": "success"}),
            "S&P 500 스냅샷 갱신이 완료되었습니다.",
        )
        self.assertEqual(
            _browser_auto_refresh_completion_label(
                {
                    "status": "skipped",
                    "plan": [{"label": "S&P 500 Daily Snapshot", "reason": "outside US market hours"}],
                }
            ),
            "S&P 500 일중 스냅샷: 미국 정규장 시간이 아니라 수집하지 않았습니다.",
        )
        self.assertEqual(
            _browser_auto_refresh_completion_label({"status": "locked"}),
            "다른 Overview 갱신 작업이 이미 실행 중입니다.",
        )

    def test_browser_auto_refresh_job_config_tracks_selected_coverage(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_job_config

        self.assertEqual(
            _browser_auto_refresh_job_config("SP500"),
            {"profile": "browser_safe", "job_id": "sp500_intraday"},
        )
        self.assertEqual(
            _browser_auto_refresh_job_config("TOP1000"),
            {"profile": "intraday", "job_id": "top1000_intraday"},
        )
        self.assertEqual(
            _browser_auto_refresh_job_config("TOP2000"),
            {"profile": "intraday", "job_id": "top2000_intraday"},
        )

    def test_overview_dashboard_routes_collection_through_action_facade(self) -> None:
        import ast

        helper_sources = "\n".join(
            Path(path).read_text(encoding="utf-8")
            for path in (
                "app/web/overview/market_context_helpers.py",
                "app/web/overview/market_movers_helpers.py",
                "app/web/overview/futures_macro_helpers.py",
                "app/web/overview/sentiment_helpers.py",
                "app/web/overview/events_helpers.py",
            )
        )
        tree = ast.parse(helper_sources)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }

        self.assertIn("app.jobs.overview_actions", imported_modules)
        self.assertNotIn("app.jobs.ingestion_jobs", imported_modules)
        self.assertNotIn("app.jobs.overview_automation", imported_modules)
        self.assertNotIn("app.jobs.run_history", imported_modules)

    def test_overview_dashboard_delegates_page_shell_to_overview_package(self) -> None:
        import ast

        source = Path("app/web/overview_dashboard.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }

        self.assertIn("app.web.overview.page", imported_modules)
        self.assertIn("render_overview_dashboard", source)

    def test_overview_primary_tab_entry_modules_exist(self) -> None:
        import importlib.util

        expected_modules = {
            "app.web.overview.market_context": "render_market_context_tab",
            "app.web.overview.market_movers": "render_market_movers_tab",
            "app.web.overview.futures_macro": "render_futures_macro_tab",
            "app.web.overview.sentiment": "render_sentiment_tab",
            "app.web.overview.events": "render_events_tab",
        }

        for module_name, entrypoint in expected_modules.items():
            try:
                spec = importlib.util.find_spec(module_name)
            except ModuleNotFoundError:
                spec = None
            self.assertIsNotNone(spec, f"{module_name} should exist")
            module = importlib.import_module(module_name)
            self.assertTrue(callable(getattr(module, entrypoint, None)))

    def test_overview_page_dispatches_primary_tabs_to_tab_modules(self) -> None:
        import ast

        page_path = Path("app/web/overview/page.py")
        self.assertTrue(page_path.exists(), "Overview page shell should live under app/web/overview/page.py")
        source = page_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }

        self.assertIn("app.web.overview.market_context", imported_modules)
        self.assertIn("app.web.overview.market_movers", imported_modules)
        self.assertIn("app.web.overview.futures_macro", imported_modules)
        self.assertIn("app.web.overview.sentiment", imported_modules)
        self.assertIn("app.web.overview.events", imported_modules)
        render_body = source[source.index("def render_overview_dashboard"):]
        self.assertIn('"Market Context": render_market_context_tab', render_body)
        self.assertIn('"Market Movers": render_market_movers_tab', render_body)
        self.assertIn('"Futures Macro": render_futures_macro_tab', render_body)
        self.assertIn('"Sentiment": render_sentiment_tab', render_body)
        self.assertIn('"Events": render_events_tab', render_body)

    def test_overview_primary_tab_modules_own_tab_orchestration(self) -> None:
        module_contracts = {
            "app/web/overview/market_context.py": {
                "entrypoint": "def render_market_context_tab",
                "forbidden": "_legacy._render_overview_market_context_tab",
                "required": [
                    "render_market_context_header()",
                    "load_market_context_cockpit_model()",
                    "render_macro_context_cockpit(",
                    "render_market_context_refresh_bar(",
                ],
            },
            "app/web/overview/market_movers.py": {
                "entrypoint": "def render_market_movers_tab",
                "forbidden": "_legacy._render_market_movers_tab",
                "required": [
                    "render_market_movers_header()",
                    "render_market_movers_controls()",
                    "is_market_movers_auto_refresh_enabled(",
                    "render_market_movers_snapshot(",
                ],
            },
            "app/web/overview/futures_macro.py": {
                "entrypoint": "def render_futures_macro_tab",
                "forbidden": "_legacy._render_futures_macro_tab",
                "required": [
                    "render_futures_macro_header()",
                    "render_futures_macro_fragment(detail_expanded=True)",
                ],
            },
            "app/web/overview/sentiment.py": {
                "entrypoint": "def render_sentiment_tab",
                "forbidden": "_legacy._render_market_sentiment_tab",
                "required": [
                    "render_sentiment_header()",
                    "render_sentiment_controls()",
                    "load_sentiment_snapshot()",
                    "render_sentiment_snapshot_overview(",
                ],
            },
            "app/web/overview/events.py": {
                "entrypoint": "def render_events_tab",
                "forbidden": "_legacy._render_events_tab",
                "required": [
                    "render_events_header()",
                    "render_event_refresh_toolbar()",
                    "load_event_snapshot_context(",
                    "render_events_overview_lanes(",
                ],
            },
        }

        for path, contract in module_contracts.items():
            source = Path(path).read_text(encoding="utf-8")
            self.assertIn(contract["entrypoint"], source)
            self.assertNotIn(contract["forbidden"], source)
            for required in contract["required"]:
                self.assertIn(required, source)

    def test_overview_component_surfaces_are_split_by_domain(self) -> None:
        import importlib.util

        expected_modules = {
            "app.web.overview.components.layout": ["render_market_session_banner"],
            "app.web.overview.components.market_context": ["render_macro_context_cockpit"],
            "app.web.overview.components.events": [
                "render_event_agenda_sections",
                "render_event_source_lane",
                "render_event_warning_strip",
                "render_events_summary_strip",
                "render_macro_week_lane",
            ],
        }

        for module_name, entrypoints in expected_modules.items():
            try:
                spec = importlib.util.find_spec(module_name)
            except ModuleNotFoundError:
                spec = None
            self.assertIsNotNone(spec, f"{module_name} should exist")
            module = importlib.import_module(module_name)
            for entrypoint in entrypoints:
                self.assertTrue(callable(getattr(module, entrypoint, None)))

    def test_overview_active_tabs_use_domain_component_surfaces(self) -> None:
        page_source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        market_context_source = Path("app/web/overview/market_context.py").read_text(encoding="utf-8")
        events_source = Path("app/web/overview/events.py").read_text(encoding="utf-8")
        events_helper_source = Path("app/web/overview/events_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.components.layout import render_market_session_banner", page_source)
        self.assertIn("render_market_session_banner(", page_source)
        self.assertNotIn("_legacy.render_market_session_banner(", page_source)

        self.assertIn(
            "from app.web.overview.components.market_context import render_macro_context_cockpit",
            market_context_source,
        )
        self.assertIn("render_macro_context_cockpit(cockpit_model, include_reading_flow=False)", market_context_source)
        self.assertNotIn("_legacy.render_macro_context_cockpit(", market_context_source)

        self.assertIn("from app.web.overview.components.events import (", events_helper_source)
        self.assertIn("render_events_summary_strip(", events_helper_source)
        self.assertIn("render_event_source_lane(", events_helper_source)
        self.assertIn("render_event_warning_strip(", events_helper_source)
        self.assertIn("render_macro_week_lane(", events_helper_source)
        self.assertNotIn("_legacy.render_events_summary_strip(", events_source)
        self.assertNotIn("_legacy.render_event_source_lane(", events_source)
        self.assertNotIn("_legacy.render_event_warning_strip(", events_source)
        self.assertNotIn("_legacy.render_macro_week_lane(", events_source)

    def test_overview_service_surfaces_are_split_by_domain(self) -> None:
        import importlib.util

        expected_modules = {
            "app.services.overview.market_context": [
                "build_overview_macro_context_cockpit",
                "build_overview_source_confidence_catalog",
            ],
            "app.services.overview.market_movers": [
                "build_group_leadership_snapshot",
                "build_market_movers_snapshot",
                "build_overview_breadth_heatmap_summary",
                "load_market_mover_sector_options",
            ],
            "app.services.overview.events": [
                "build_market_events_snapshot",
                "build_overview_macro_week_lane",
            ],
            "app.services.overview.sentiment": ["build_market_sentiment_snapshot"],
            "app.services.overview.data_health": [
                "build_collection_ops_snapshot",
                "build_overview_data_health_ingestion_handoff",
            ],
            "app.services.overview.ia": ["load_overview_ia_closeout_model"],
        }

        for module_name, entrypoints in expected_modules.items():
            try:
                spec = importlib.util.find_spec(module_name)
            except ModuleNotFoundError:
                spec = None
            self.assertIsNotNone(spec, f"{module_name} should exist")
            module = importlib.import_module(module_name)
            for entrypoint in entrypoints:
                self.assertTrue(callable(getattr(module, entrypoint, None)))

    def test_overview_dashboard_helpers_use_domain_service_surfaces(self) -> None:
        source = Path("app/web/overview_dashboard_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.services.overview.data_health import (", source)
        self.assertIn("from app.services.overview.events import (", source)
        self.assertIn("from app.services.overview.ia import load_overview_ia_closeout_model", source)
        self.assertIn("from app.services.overview.market_context import (", source)
        self.assertIn("from app.services.overview.market_movers import (", source)
        self.assertIn("from app.services.overview.sentiment import build_market_sentiment_snapshot", source)
        self.assertNotIn("from app.services.overview_market_intelligence import (", source)

    def test_overview_ia_closeout_body_lives_in_service_surface(self) -> None:
        service_source = Path("app/services/overview/ia.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview_dashboard_helpers.py").read_text(encoding="utf-8")

        self.assertIn("def load_overview_ia_closeout_model", service_source)
        self.assertIn('"schema_version": "overview_ia_closeout_v1"', service_source)
        self.assertNotIn("def load_overview_ia_closeout_model", helper_source)

    def test_overview_legacy_cleanup_audit_tracks_active_retained_and_removable_buckets(self) -> None:
        audit_path = Path(
            ".aiworkspace/note/finance/tasks/active/overview-legacy-cleanup-v6-v10-20260625/LEGACY_USAGE_AUDIT.md"
        )
        self.assertTrue(audit_path.exists())
        audit = audit_path.read_text(encoding="utf-8")

        for heading in (
            "## Active Legacy Calls",
            "## Retained Compatibility",
            "## Removable Candidates",
            "## Next Extraction Order",
        ):
            self.assertIn(heading, audit)

        self.assertIn("`_render_overview_tab_selector`", audit)
        self.assertIn("`_render_futures_monitor_tab`", audit)
        self.assertIn("`load_overview_dashboard_snapshot`", audit)
        self.assertIn("Candidate Ops", audit)

    def test_overview_helper_extraction_audit_tracks_target_helper_modules(self) -> None:
        audit_path = Path(
            ".aiworkspace/note/finance/tasks/active/overview-tab-helper-extraction-v11-v16-20260625/"
            "HELPER_EXTRACTION_AUDIT.md"
        )
        self.assertTrue(audit_path.exists())
        audit = audit_path.read_text(encoding="utf-8")

        for heading in (
            "## Active Legacy Helper Calls",
            "## Target Helper Modules",
            "## Extraction Order",
            "## Guard Rules",
        ):
            self.assertIn(heading, audit)

        for module_name in (
            "market_context_helpers.py",
            "events_helpers.py",
            "futures_macro_helpers.py",
            "market_movers_helpers.py",
            "sentiment_helpers.py",
        ):
            self.assertIn(module_name, audit)

        self.assertIn("legacy_dashboard.py", audit)

    def test_overview_legacy_dashboard_removal_audit_tracks_phase_targets(self) -> None:
        audit_path = Path(
            ".aiworkspace/note/finance/tasks/active/overview-legacy-dashboard-removal-v17-v24-20260625/"
            "LEGACY_DASHBOARD_REMOVAL_AUDIT.md"
        )
        self.assertTrue(audit_path.exists())
        audit = audit_path.read_text(encoding="utf-8")

        for heading in (
            "## Remaining Direct Dependencies",
            "## Removal Phases",
            "## Migration Targets",
            "## Deletion Guard",
        ):
            self.assertIn(heading, audit)

        for target in (
            "session_helpers.py",
            "market_context_helpers.py",
            "events_helpers.py",
            "sentiment_helpers.py",
            "market_movers_helpers.py",
            "futures_macro_helpers.py",
            "overview_dashboard.py",
            "legacy_dashboard.py",
        ):
            self.assertIn(target, audit)

        self.assertFalse(Path("app/web/overview/legacy_dashboard.py").exists())

    def test_overview_page_uses_session_helper_instead_of_legacy_dashboard(self) -> None:
        page_source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/session_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.session_helpers import _market_session_banner_model", page_source)
        self.assertNotIn("legacy_dashboard", page_source)
        self.assertNotIn("_legacy.", page_source)
        self.assertIn("def _market_session_banner_model", helper_source)
        self.assertIn("def _market_context_session_payload", helper_source)
        self.assertIn("def _snapshot_status_items", helper_source)

    def test_overview_market_context_entrypoint_uses_tab_helper_module(self) -> None:
        source = Path("app/web/overview/market_context.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/market_context_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.market_context_helpers import (", source)
        self.assertNotIn("legacy_dashboard", source)
        self.assertNotIn("_legacy.", source)

        for function_name in (
            "render_market_context_header",
            "render_market_context_refresh_reflection",
            "load_market_context_cockpit_model",
            "render_market_context_refresh_bar",
        ):
            self.assertIn(f"def {function_name}", helper_source)

        self.assertNotIn("legacy_dashboard", helper_source)
        self.assertNotIn("_legacy.", helper_source)
        self.assertIn("load_overview_macro_context_cockpit(", helper_source)
        self.assertIn("run_overview_market_context_refresh_smart(", helper_source)
        self.assertIn("run_overview_market_context_refresh_all(", helper_source)

    def test_overview_events_entrypoint_uses_tab_helper_module(self) -> None:
        source = Path("app/web/overview/events.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/events_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.events_helpers import (", source)
        self.assertNotIn("legacy_dashboard", source)
        self.assertNotIn("_legacy.", source)

        for function_name in (
            "render_events_header",
            "render_event_refresh_toolbar",
            "load_event_snapshot_context",
            "render_event_refresh_results",
            "render_events_overview_lanes",
            "has_event_rows",
            "filter_event_calendar_rows",
            "render_event_detail_tabs",
        ):
            self.assertIn(f"def {function_name}", helper_source)

        self.assertNotIn("legacy_dashboard", helper_source)
        self.assertNotIn("_legacy.", helper_source)
        self.assertIn("load_overview_market_events_snapshot(", helper_source)
        self.assertIn("_render_event_month_grid(filtered_rows)", helper_source)

    def test_overview_futures_macro_entrypoint_uses_tab_helper_module(self) -> None:
        source = Path("app/web/overview/futures_macro.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/futures_macro_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.futures_macro_helpers import (", source)
        self.assertNotIn("legacy_dashboard", source)
        self.assertNotIn("_legacy.", source)

        for function_name in (
            "render_futures_macro_header",
            "render_futures_macro_fragment",
            "_render_futures_macro_refresh_controls",
            "_render_futures_macro_panel",
            "_futures_market_brief_model",
            "_futures_weekly_flow_model",
        ):
            self.assertIn(f"def {function_name}", helper_source)

        self.assertNotIn("legacy_dashboard", helper_source)
        self.assertNotIn("_legacy.", helper_source)
        self.assertIn("load_overview_futures_macro_snapshot(", helper_source)

    def test_overview_market_movers_entrypoint_uses_tab_helper_module(self) -> None:
        source = Path("app/web/overview/market_movers.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/market_movers_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.market_movers_helpers import (", source)
        self.assertNotIn("legacy_dashboard", source)
        self.assertNotIn("_legacy.", source)

        for function_name in (
            "render_market_movers_header",
            "render_market_movers_controls",
            "render_market_movers_context_captions",
            "normalize_market_movers_refresh_mode",
            "is_market_movers_auto_refresh_enabled",
            "render_market_movers_auto_refresh_panel",
            "render_market_movers_snapshot",
        ):
            self.assertIn(f"def {function_name}", helper_source)

        self.assertNotIn("legacy_dashboard", helper_source)
        self.assertNotIn("_legacy.", helper_source)
        self.assertIn("_render_market_movers_controls()", helper_source)
        self.assertIn("_render_market_movers_refresh_bar(", helper_source)
        self.assertIn("_render_market_movers_snapshot_panel(", helper_source)

    def test_overview_sentiment_entrypoint_uses_tab_helper_module(self) -> None:
        source = Path("app/web/overview/sentiment.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/sentiment_helpers.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.sentiment_helpers import (", source)
        self.assertNotIn("legacy_dashboard", source)
        self.assertNotIn("_legacy.", source)

        for function_name in (
            "render_sentiment_header",
            "render_sentiment_controls",
            "render_sentiment_job_result",
            "load_sentiment_snapshot",
            "render_sentiment_snapshot_overview",
            "has_sentiment_rows",
            "render_sentiment_empty_state",
            "render_sentiment_detail_sections",
        ):
            self.assertIn(f"def {function_name}", helper_source)

        self.assertNotIn("legacy_dashboard", helper_source)
        self.assertNotIn("_legacy.", helper_source)
        self.assertIn("run_overview_market_sentiment()", helper_source)
        self.assertIn("load_overview_market_sentiment_snapshot()", helper_source)
        self.assertIn("_render_sentiment_analysis_panel(analysis)", helper_source)
        self.assertIn("_sentiment_trend_chart(", helper_source)

    def test_overview_legacy_cleanup_removes_confirmed_unused_surfaces(self) -> None:
        legacy_path = Path("app/web/overview/legacy_dashboard.py")
        wrapper_source = Path("app/web/overview_dashboard.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview_dashboard_helpers.py").read_text(encoding="utf-8")

        self.assertFalse(legacy_path.exists())
        for function_name in (
            "render_overview_dashboard",
            "_render_overview_market_context_tab",
            "_render_market_movers_tab",
            "_render_futures_macro_tab",
            "_render_futures_monitor_tab",
            "_render_sector_industry_tab",
            "_render_market_sentiment_tab",
            "_render_events_tab",
        ):
            self.assertNotIn(f"def {function_name}", wrapper_source)

        for function_name in (
            "load_overview_dashboard_snapshot",
            "build_overview_top_candidates",
            "build_overview_funnel_rows",
            "build_overview_next_actions",
            "build_overview_activity_rows",
        ):
            self.assertNotIn(f"def {function_name}", helper_source)

    def test_overview_removed_legacy_surfaces_do_not_leak_through_compat_wrapper(self) -> None:
        from app.web import overview_dashboard

        for name in (
            "load_overview_dashboard_snapshot",
            "build_overview_top_candidates",
            "build_overview_funnel_rows",
            "build_overview_next_actions",
            "build_overview_activity_rows",
            "_render_overview_market_context_tab",
            "_render_market_movers_tab",
            "_render_futures_macro_tab",
            "_render_futures_monitor_tab",
            "_render_sector_industry_tab",
            "_render_market_sentiment_tab",
            "_render_events_tab",
        ):
            self.assertFalse(hasattr(overview_dashboard, name), f"{name} should stay removed from wrapper exports")

    def test_overview_helpers_do_not_reintroduce_candidate_ops_runtime_imports(self) -> None:
        import ast

        source = Path("app/web/overview_dashboard_helpers.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imported_names = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }

        self.assertNotIn("app.runtime", imported_modules)
        self.assertFalse(
            {
                "load_current_candidate_registry_latest",
                "load_pre_live_candidate_registry_latest",
                "load_portfolio_proposals",
                "load_backtest_run_history",
                "load_saved_portfolios",
                "load_candidate_review_notes",
            }
            & imported_names
        )

    def test_overview_navigation_surface_owns_selector_entrypoints(self) -> None:
        from app.web.overview import navigation

        self.assertEqual(
            navigation.OVERVIEW_DEEP_TAB_OPTIONS,
            (
                "Market Context",
                "Market Movers",
                "Futures Macro",
                "Sentiment",
                "Events",
            ),
        )
        self.assertTrue(callable(navigation._render_overview_tab_selector))
        self.assertTrue(callable(navigation._render_selected_overview_tab))
        source = Path("app/web/overview/navigation.py").read_text(encoding="utf-8")
        self.assertIn("def _render_overview_tab_selector", source)
        self.assertIn("def _render_selected_overview_tab", source)

    def test_overview_page_uses_navigation_surface_instead_of_legacy_selector_body(self) -> None:
        page_source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        wrapper_source = Path("app/web/overview_dashboard.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.overview.navigation import (", page_source)
        self.assertIn("_render_overview_tab_selector()", page_source)
        self.assertIn("_render_selected_overview_tab(", page_source)
        self.assertNotIn("_legacy._render_overview_tab_selector()", page_source)
        self.assertNotIn("_legacy._render_selected_overview_tab(", page_source)
        self.assertNotIn("legacy_dashboard", wrapper_source)
        self.assertNotIn("_legacy_dashboard", wrapper_source)

    def test_overview_service_surfaces_stay_streamlit_free(self) -> None:
        import ast

        for path in sorted(Path("app/services/overview").glob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported_modules = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imported_modules.update(
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            )

            self.assertNotIn("streamlit", imported_modules, f"{path} should stay Streamlit-free")
            self.assertFalse(
                any(module == "app.web" or module.startswith("app.web.") for module in imported_modules),
                f"{path} should not import web UI modules",
            )

    def test_overview_component_surfaces_do_not_pull_services_or_data(self) -> None:
        import ast

        forbidden_prefixes = ("app.services", "app.jobs", "finance.data", "finance.loaders")
        for path in sorted(Path("app/web/overview/components").glob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported_modules = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imported_modules.update(
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            )

            self.assertFalse(
                any(module == prefix or module.startswith(f"{prefix}.") for module in imported_modules for prefix in forbidden_prefixes),
                f"{path} should remain a visual component surface, not a service/data entrypoint",
            )

    def test_overview_active_page_and_tabs_do_not_import_data_or_jobs_directly(self) -> None:
        import ast

        guarded_paths = [
            Path("app/web/overview/page.py"),
            Path("app/web/overview/market_context.py"),
            Path("app/web/overview/market_movers.py"),
            Path("app/web/overview/futures_macro.py"),
            Path("app/web/overview/sentiment.py"),
            Path("app/web/overview/events.py"),
        ]
        forbidden_modules = {
            "app.jobs.ingestion_jobs",
            "app.jobs.overview_automation",
            "app.jobs.run_history",
            "finance.data",
            "finance.loaders",
        }
        for path in guarded_paths:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported_modules = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imported_modules.update(
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            )

            self.assertFalse(
                any(
                    module == forbidden or module.startswith(f"{forbidden}.")
                    for module in imported_modules
                    for forbidden in forbidden_modules
                ),
                f"{path} should route data/job work through helpers or action facades",
            )

    def test_overview_dashboard_wrapper_remains_thin_compatibility_facade(self) -> None:
        source = Path("app/web/overview_dashboard.py").read_text(encoding="utf-8")

        self.assertLessEqual(len(source.splitlines()), 80)
        self.assertIn("from app.web.overview.page import render_overview_dashboard", source)
        self.assertIn("from app.web.overview.navigation import (", source)
        self.assertIn("from app.web.overview.market_movers_helpers import (", source)
        self.assertIn("from app.web.overview.futures_macro_helpers import (", source)
        self.assertNotIn("import streamlit", source)
        self.assertNotIn("legacy_dashboard", source)
        self.assertNotIn("for _name in dir", source)

    def test_overview_dashboard_uses_lazy_selected_deep_tab_rendering(self) -> None:
        source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        render_body = source[source.index("def render_overview_dashboard"):]
        context_label_index = render_body.index('"Market Context"')
        market_label_index = render_body.index('"Market Movers"')
        futures_macro_label_index = render_body.index('"Futures Macro"')
        sentiment_label_index = render_body.index('"Sentiment"')
        events_label_index = render_body.index('"Events"')

        self.assertIn("_render_overview_tab_selector(", render_body)
        self.assertIn("_render_selected_overview_tab(", render_body)
        self.assertNotIn("st.tabs(", render_body)
        self.assertNotIn("snapshot = load_overview_dashboard_snapshot()", render_body)
        self.assertNotIn('"Futures Monitor"', render_body)
        self.assertNotIn('"Sector / Industry"', render_body)
        self.assertNotIn('"Data Health": _render_collection_ops_tab', render_body)
        self.assertNotIn('"Candidate Ops"', render_body)
        self.assertNotIn("load_overview_dashboard_snapshot", render_body)
        self.assertLess(context_label_index, market_label_index)
        self.assertLess(market_label_index, futures_macro_label_index)
        self.assertLess(futures_macro_label_index, sentiment_label_index)
        self.assertLess(sentiment_label_index, events_label_index)

    def test_overview_dashboard_primary_selector_excludes_inactive_tabs(self) -> None:
        from app.web.overview_dashboard import OVERVIEW_DEEP_TAB_OPTIONS

        self.assertEqual(
            OVERVIEW_DEEP_TAB_OPTIONS,
            (
                "Market Context",
                "Market Movers",
                "Futures Macro",
                "Sentiment",
                "Events",
            ),
        )
        self.assertNotIn("Futures Monitor", OVERVIEW_DEEP_TAB_OPTIONS)
        self.assertNotIn("Sector / Industry", OVERVIEW_DEEP_TAB_OPTIONS)
        self.assertNotIn("Data Health", OVERVIEW_DEEP_TAB_OPTIONS)
        self.assertNotIn("Candidate Ops", OVERVIEW_DEEP_TAB_OPTIONS)

    def test_overview_dashboard_primary_selector_uses_internal_pill_widget(self) -> None:
        source = Path("app/web/overview/navigation.py").read_text(encoding="utf-8")
        helper_body = source[source.index("def _render_overview_tab_selector"):]
        helper_body = helper_body[: helper_body.index("def _render_selected_overview_tab")]

        self.assertIn("st.pills(", helper_body)
        self.assertIn('selection_mode="single"', helper_body)
        self.assertIn("required=True", helper_body)
        self.assertIn("format_func=_overview_tab_display_label", helper_body)
        self.assertIn("st.markdown(", helper_body)
        self.assertIn("_overview_tab_nav_css()", helper_body)
        self.assertNotIn("segmented_control", helper_body)
        self.assertNotIn("st.radio(", helper_body)
        self.assertNotIn("href=", helper_body)
        self.assertNotIn("<a ", helper_body)
        self.assertIn("ov-primary-nav", source)
        self.assertIn('stBaseButton-pillsActive', source)
        self.assertIn("border-bottom: 1px solid", source)
        self.assertIn("border-radius: 0", source)
        self.assertIn("box-shadow: none", source)
        self.assertIn("var(--text-color)", source)
        self.assertIn("#ff4b4b", source)
        self.assertNotIn("background: #f2faf7", source)

    def test_overview_dashboard_dispatches_only_selected_deep_tab(self) -> None:
        from app.web.overview_dashboard import _render_selected_overview_tab

        calls: list[str] = []
        renderers = {
            "Market Context": lambda: calls.append("Market Context"),
            "Market Movers": lambda: calls.append("Market Movers"),
            "Futures Macro": lambda: calls.append("Futures Macro"),
        }

        _render_selected_overview_tab("Futures Macro", renderers=renderers)

        self.assertEqual(calls, ["Futures Macro"])

    def test_overview_dashboard_defaults_unknown_deep_tab_to_market_context(self) -> None:
        from app.web.overview_dashboard import _overview_active_tab_label

        self.assertEqual(_overview_active_tab_label("does-not-exist"), "Market Context")
        self.assertEqual(_overview_active_tab_label("Futures Macro"), "Futures Macro")
        self.assertEqual(_overview_active_tab_label("Futures Monitor"), "Market Context")
        self.assertEqual(_overview_active_tab_label("Sector / Industry"), "Market Context")
        self.assertEqual(_overview_active_tab_label(None), "Market Context")

    def test_overview_dashboard_pill_nav_slug_contract(self) -> None:
        from app.web.overview_dashboard import (
            OVERVIEW_DEEP_TAB_OPTIONS,
            _overview_tab_seed_label,
            _overview_tab_display_label,
            _overview_tab_label_from_slug,
        )

        for label in OVERVIEW_DEEP_TAB_OPTIONS:
            display = _overview_tab_display_label(label)
            self.assertIn(label, display)

        self.assertEqual(_overview_tab_label_from_slug("market-context"), "Market Context")
        self.assertEqual(_overview_tab_label_from_slug("market-movers"), "Market Movers")
        self.assertEqual(_overview_tab_label_from_slug("futures-macro"), "Futures Macro")
        self.assertIn("시장 맥락", _overview_tab_display_label("Market Context"))
        self.assertIn("변동 종목", _overview_tab_display_label("Market Movers"))
        self.assertIn("선물 매크로", _overview_tab_display_label("Futures Macro"))
        self.assertIn("심리", _overview_tab_display_label("Sentiment"))
        self.assertIn("일정", _overview_tab_display_label("Events"))
        self.assertEqual(
            _overview_tab_seed_label(
                query_label="Market Movers",
                widget_value="Sentiment",
                session_value="Market Context",
            ),
            "Sentiment",
        )
        self.assertEqual(
            _overview_tab_seed_label(
                query_label="Market Movers",
                widget_value=None,
                session_value="Market Context",
            ),
            "Market Movers",
        )

    def test_overview_dashboard_routes_futures_macro_as_primary_tab(self) -> None:
        source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        futures_source = Path("app/web/overview/futures_macro.py").read_text(encoding="utf-8")
        futures_helper_source = Path("app/web/overview/futures_macro_helpers.py").read_text(encoding="utf-8")
        render_body = source[source.index("def render_overview_dashboard"):]

        self.assertIn('"Futures Macro": render_futures_macro_tab', render_body)
        self.assertIn("def render_futures_macro_tab", futures_source)
        self.assertIn("render_futures_macro_fragment(detail_expanded=True)", futures_source)
        self.assertNotIn("legacy_dashboard", futures_helper_source)
        self.assertNotIn("_legacy.", futures_helper_source)
        self.assertIn("_render_futures_macro_panel(detail_expanded=detail_expanded)", futures_helper_source)
        self.assertNotIn('"Futures Monitor"', render_body)

    def test_futures_macro_tab_exposes_daily_refresh_and_cache_reload(self) -> None:
        futures_source = Path("app/web/overview/futures_macro.py").read_text(encoding="utf-8")
        futures_helper_source = Path("app/web/overview/futures_macro_helpers.py").read_text(encoding="utf-8")
        style_source = Path("app/web/overview_ui_components.py").read_text(encoding="utf-8")
        controls_body = futures_helper_source[futures_helper_source.index("def _render_futures_macro_refresh_controls") :]
        controls_body = controls_body[: controls_body.index("def _render_futures_macro_panel")]
        panel_body = futures_helper_source[futures_helper_source.index("def _render_futures_macro_panel") :]
        panel_body = panel_body[: panel_body.index("def render_futures_macro_fragment")]
        tab_body = futures_source[futures_source.index("def render_futures_macro_tab") :]

        self.assertIn("render_futures_macro_fragment(detail_expanded=True)", tab_body)
        self.assertNotIn("_legacy._render_futures_macro_refresh_controls()", tab_body)
        self.assertNotIn("legacy_dashboard", futures_helper_source)
        self.assertNotIn("_legacy.", futures_helper_source)
        self.assertIn("_render_futures_macro_refresh_controls(", panel_body)
        self.assertIn("section_detail=", panel_body)
        self.assertNotIn('_render_futures_section_header(\n        "매크로 컨텍스트"', panel_body)
        self.assertIn("_run_futures_daily_ohlcv_action()", controls_body)
        self.assertIn("clear_overview_futures_macro_snapshot_cache()", controls_body)
        self.assertIn("overview_futures_macro_tab_daily_refresh", controls_body)
        self.assertIn("overview_futures_macro_tab_reload", controls_body)
        self.assertIn("ov-futures-macro-action-copy", controls_body)
        self.assertIn("ov-futures-macro-action-title", controls_body)
        self.assertIn("ov-futures-macro-action-rule", controls_body)
        self.assertIn("section_detail", controls_body)
        self.assertNotIn("데이터 작업", controls_body)
        self.assertIn("st.columns([1, 0.16, 0.16]", controls_body)
        self.assertNotIn("2.05, 0.62, 0.62, 1.25", controls_body)
        self.assertIn('"일봉 갱신"', controls_body)
        self.assertIn('"다시 읽기"', controls_body)
        self.assertIn(".ov-futures-macro-action-title", style_source)
        self.assertIn(".ov-futures-macro-action-rule", style_source)
        self.assertIn(".st-key-overview_futures_macro_tab_daily_refresh button", style_source)
        self.assertIn(".st-key-overview_futures_macro_tab_reload button", style_source)

    def test_overview_dashboard_renders_default_market_context_without_load_gate(self) -> None:
        source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        render_body = source[source.index("def render_overview_dashboard"):]

        self.assertNotIn("_render_overview_tab_load_gate", source)
        self.assertNotIn("시장 맥락 불러오기", source)
        self.assertNotIn("OVERVIEW_LOADED_TABS_KEY", source)
        self.assertLess(
            render_body.index("active_tab = _render_overview_tab_selector()"),
            render_body.index("_render_selected_overview_tab("),
        )

    def test_overview_dashboard_renders_macro_context_cockpit_inside_market_context_tab(self) -> None:
        source = Path("app/web/overview/market_context.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/market_context_helpers.py").read_text(encoding="utf-8")
        helper_body = source[source.index("def render_market_context_tab"):]

        self.assertIn("cockpit_model = load_market_context_cockpit_model()", helper_body)
        self.assertIn("render_macro_context_cockpit(cockpit_model, include_reading_flow=False)", helper_body)
        self.assertIn("render_market_context_refresh_bar(cockpit_model)", helper_body)
        cockpit_index = helper_body.index("render_macro_context_cockpit(cockpit_model, include_reading_flow=False)")
        refresh_index = helper_body.index("render_market_context_refresh_bar(cockpit_model)")
        self.assertLess(cockpit_index, refresh_index)
        self.assertIn("load_market_context_cockpit_model", helper_body)
        self.assertIn("render_macro_context_cockpit", helper_body)
        self.assertNotIn("_render_overview_historical_analog_controls()", helper_body)
        self.assertNotIn("render_macro_context_reading_flow(", helper_body)
        self.assertNotIn("_render_overview_historical_analog_repair_action(", helper_body)
        self.assertNotIn("render_overview_ia_closeout_guide(load_overview_ia_closeout_model())", helper_body)
        self.assertNotIn("legacy_dashboard", helper_source)
        self.assertNotIn("_legacy.", helper_source)
        self.assertIn("load_overview_macro_context_cockpit(", helper_source)
        self.assertIn("run_overview_market_context_refresh_smart(", helper_source)

    def test_overview_dashboard_keeps_deep_tab_guide_out_of_market_context_brief(self) -> None:
        source = Path("app/web/overview/market_context.py").read_text(encoding="utf-8")
        helper_body = source[source.index("def render_market_context_tab"):]

        self.assertIn("cockpit_model = load_market_context_cockpit_model()", helper_body)
        self.assertIn("render_macro_context_cockpit(cockpit_model, include_reading_flow=False)", helper_body)
        self.assertNotIn("render_macro_context_reading_flow(", helper_body)
        self.assertNotIn("_render_overview_historical_analog_controls()", helper_body)
        self.assertNotIn("load_overview_ia_closeout_model", helper_body)
        self.assertNotIn("render_overview_ia_closeout_guide", helper_body)
        self.assertNotIn("Deep Tab", helper_body)

    def test_overview_market_context_loader_excludes_futures_macro_by_default(self) -> None:
        source = Path("app/web/overview_dashboard_helpers.py").read_text(encoding="utf-8")
        helper_body = source[source.index("def load_overview_macro_context_cockpit"):]

        self.assertIn("include_futures_macro: bool = False", helper_body)
        self.assertIn("include_historical_analog: bool = False", helper_body)
        guard_index = helper_body.index("if include_futures_macro:")
        call_index = helper_body.index("futures_macro_snapshot = load_overview_futures_macro_snapshot()")
        self.assertLess(guard_index, call_index)
        analog_guard_index = helper_body.index("if include_historical_analog:")
        analog_call_index = helper_body.index("historical_analog_snapshot = load_overview_market_context_historical_analog(")
        self.assertLess(analog_guard_index, analog_call_index)
        self.assertIn("include_futures_macro=include_futures_macro", helper_body)

    def test_overview_market_context_refresh_reflection_copy_distinguishes_outcomes(self) -> None:
        from app.web import overview_dashboard

        reflection_state = getattr(overview_dashboard, "_overview_market_context_refresh_reflection_state", None)
        self.assertTrue(callable(reflection_state), "Market Context refresh should expose reflection state copy.")

        reflected_at = datetime(2026, 6, 12, 14, 32)

        success = reflection_state(
            {"status": "success", "finished_at": "2026-06-12 14:31:59"},
            reflected_at=reflected_at,
        )
        partial = reflection_state(
            {"status": "partial_success", "finished_at": "2026-06-12 14:31:59"},
            reflected_at=reflected_at,
        )
        failed = reflection_state(
            {"status": "failed", "finished_at": "2026-06-12 14:31:59"},
            reflected_at=reflected_at,
        )

        self.assertTrue(success["reflected"])
        self.assertIn("방금 갱신을 반영했습니다", success["label"])
        self.assertIn("2026-06-12 14:32", success["detail"])
        self.assertTrue(partial["reflected"])
        self.assertIn("일부 자료만 반영했습니다", partial["label"])
        self.assertIn("오래된 항목", partial["detail"])
        self.assertFalse(failed["reflected"])
        self.assertIn("갱신 실패", failed["label"])
        self.assertIn("기존 자료", failed["detail"])

    def test_overview_market_context_refresh_clears_cache_before_rerun(self) -> None:
        source = Path("app/web/overview/market_context_helpers.py").read_text(encoding="utf-8")
        if "def render_market_context_refresh_bar" not in source:
            self.fail("Overview should keep the Market Context refresh bar helper.")
        helper_body = source[source.index("def render_market_context_refresh_bar"):]

        self.assertIn("_overview_market_context_refresh_reflection_state", helper_body)
        self.assertIn("overview_market_context_refresh_reflection", helper_body)
        self.assertIn("st.rerun()", helper_body)

        store_index = helper_body.index("_store_overview_job_result(result_key, result)")
        clear_index = helper_body.index("_clear_overview_market_context_caches()")
        rerun_index = helper_body.index("st.rerun()")

        self.assertLess(store_index, clear_index)
        self.assertLess(clear_index, rerun_index)

    def test_overview_market_context_refresh_assist_shows_smart_plan_before_job_result(self) -> None:
        source = Path("app/web/overview/market_context_helpers.py").read_text(encoding="utf-8")
        if "def render_market_context_refresh_bar" not in source:
            self.fail("Overview should keep the Market Context refresh bar helper.")
        helper_body = source[source.index("def render_market_context_refresh_bar"):]

        self.assertIn("_overview_market_context_refresh_expander_label(cockpit_model)", helper_body)
        self.assertIn("_render_overview_market_context_smart_refresh_plan(cockpit_model)", helper_body)
        action_hint_index = helper_body.index("_render_overview_market_context_smart_refresh_plan(cockpit_model)")
        button_index = helper_body.index("cols[1].button(")
        result_index = helper_body.index("_render_overview_market_context_refresh_result(result_key)")

        self.assertLess(action_hint_index, button_index)
        self.assertLess(button_index, result_index)
        self.assertIn('with st.expander("갱신 상세", expanded=False):', source)

    def test_overview_data_health_is_not_a_primary_overview_tab(self) -> None:
        source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        wrapper_source = Path("app/web/overview_dashboard.py").read_text(encoding="utf-8")
        render_body = source[source.index("def render_overview_dashboard"):]

        self.assertNotIn("def _render_collection_ops_tab", wrapper_source)
        self.assertNotIn("load_overview_data_health_ingestion_handoff", render_body)
        self.assertNotIn("render_data_health_ingestion_handoff", render_body)
        self.assertNotIn('"Data Health"', render_body)

    def test_overview_sector_industry_standalone_tab_is_removed_from_primary_overview(self) -> None:
        page_source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
        wrapper_source = Path("app/web/overview_dashboard.py").read_text(encoding="utf-8")
        render_body = page_source[page_source.index("def render_overview_dashboard"):]

        self.assertNotIn("def _render_sector_industry_tab", wrapper_source)
        self.assertNotIn('"Sector / Industry"', render_body)
        self.assertIn("build_overview_breadth_heatmap_summary", Path("app/services/overview/market_movers.py").read_text(encoding="utf-8"))

    def test_overview_events_tab_renders_macro_week_lane_before_calendar_filters(self) -> None:
        source = Path("app/web/overview/events.py").read_text(encoding="utf-8")
        helper_source = Path("app/web/overview/events_helpers.py").read_text(encoding="utf-8")
        tab_body = source[source.index("def render_events_tab"):]
        lane_index = tab_body.index("render_events_overview_lanes(")
        filter_index = tab_body.index("filter_event_calendar_rows(")

        self.assertLess(lane_index, filter_index)
        self.assertIn("load_overview_macro_week_lane(context.snapshot)", helper_source)
        self.assertNotIn("_legacy.load_overview_macro_week_lane", helper_source)

    def test_futures_chart_symbols_supports_compact_and_all_data_scopes(self) -> None:
        from app.web.overview_dashboard import _futures_chart_symbols

        symbols = [f"S{index}=F" for index in range(1, 10)]
        chartable_symbols = [symbol for symbol in symbols if symbol != "S4=F"]
        snapshot = {
            "symbols": symbols,
            "all_candles": pd.DataFrame(
                {"Symbol": symbol, "Datetime": "2026-06-09 09:30:00", "Close": 100.0}
                for symbol in chartable_symbols
            ),
        }

        self.assertEqual(_futures_chart_symbols(snapshot), chartable_symbols[:6])
        self.assertEqual(_futures_chart_symbols(snapshot, chart_scope="all_with_data"), chartable_symbols)

    def test_futures_monitor_command_summary_owns_page_state_without_provider_rows(self) -> None:
        from app.web.overview_dashboard import _futures_command_summary_items

        selected_symbols = ["NQ=F", "ZN=F", "CL=F", "6E=F", "GC=F", "6J=F"]
        snapshot = {
            "status": "REVIEW",
            "coverage": {
                "returnable_count": 6,
                "symbol_count": 6,
                "latest_age_minutes": 26,
                "oldest_age_minutes": 26,
            },
            "top_move": {"Symbol": "NQ=F", "15m %": -0.6, "60m %": -0.3, "State": "Stale"},
            "latest_run": {
                "status": "success",
                "rows_written": 9874,
                "latest_candle_time_utc": "2026-06-22 14:34:00",
            },
        }

        items = _futures_command_summary_items(
            snapshot=snapshot,
            group="Pre-open Core",
            selected_symbols=selected_symbols,
            lookback_label="6H",
            chart_interval="5m",
            refresh_mode="manual",
        )

        self.assertEqual([item["label"] for item in items], ["관찰 범위", "데이터 상태", "단기 움직임"])
        flattened = " ".join(str(value) for item in items for value in item.values())
        self.assertIn("개장 전 핵심", flattened)
        self.assertIn("갱신 필요", flattened)
        self.assertIn("NQ=F", flattened)
        self.assertNotIn("9874", flattened)
        self.assertNotIn("2026-06-22 14:34:00", flattened)

    def test_futures_monitor_live_summary_line_avoids_repeating_top_move_or_run(self) -> None:
        from app.web.overview_dashboard import _futures_live_summary_line

        selected_symbols = ["NQ=F", "ZN=F", "CL=F", "6E=F", "GC=F", "6J=F"]
        snapshot = {
            "symbols": selected_symbols,
            "top_move": {"Symbol": "NQ=F", "15m %": -0.6, "60m %": -0.3, "State": "Stale"},
            "latest_run": {"status": "success", "rows_written": 9874},
            "all_candles": pd.DataFrame(
                {"Symbol": symbol, "Datetime": "2026-06-22 14:30:00", "Close": 100.0}
                for symbol in selected_symbols
            ),
        }

        summary = _futures_live_summary_line(
            snapshot,
            chart_interval="5m",
            lookback_label="6H",
            chart_scope="compact_6",
        )

        self.assertIn("선택 6개", summary)
        self.assertIn("5분 봉", summary)
        self.assertIn("차트 가능 6개 중 6개 표시", summary)
        self.assertNotIn("NQ=F", summary)
        self.assertNotIn("9874", summary)
        self.assertNotIn("성공", summary)

    def test_futures_monitor_macro_support_items_do_not_repeat_scenario(self) -> None:
        from app.web.overview_dashboard import _macro_support_items

        macro = {
            "summary": {"scenario": "혼재된 매크로 흐름"},
            "confidence": {
                "label": "Medium Confidence",
                "reasons": ["Most core symbols have 60D standardized moves."],
                "sample_size": 0,
                "occurrence_count": 950,
                "hit_applicable": False,
            },
            "validation": {
                "status": "OK",
                "coverage": {"validation_dates": 1212, "history_span_years": 5.05},
                "current_scenario_metrics": {
                    "Occurrence Count": 950,
                    "Directional Hit Applicable": False,
                },
            },
        }

        items = _macro_support_items(macro)

        self.assertEqual([item["label"] for item in items], ["근거 강도", "과거 점검", "유사 구간"])
        self.assertEqual(items[0]["value"], "보통")
        self.assertNotIn("근거 강도", str(items[0]["value"]))
        flattened = " ".join(str(value) for item in items for value in item.values())
        self.assertNotIn("혼재된 매크로 흐름", flattened)

    def test_futures_workbench_context_bar_items_compactly_summarize_controls(self) -> None:
        from app.web.overview_dashboard import _futures_workbench_context_items

        selected_symbols = ["NQ=F", "ZN=F", "CL=F", "6E=F", "GC=F", "6J=F"]
        snapshot = {
            "status": "REVIEW",
            "coverage": {
                "latest_age_minutes": 591,
                "oldest_age_minutes": 591,
            },
            "latest_run": {
                "status": "success",
                "rows_written": 9874,
                "latest_candle_time_utc": "2026-06-22 14:34:00",
            },
        }

        items = _futures_workbench_context_items(
            snapshot=snapshot,
            group="Pre-open Core",
            selected_symbols=selected_symbols,
            lookback_label="6H",
            chart_interval="5m",
            chart_scope="compact_6",
            refresh_mode="manual",
        )

        self.assertEqual([item["label"] for item in items], ["관찰", "차트", "자료", "다음 행동"])
        flattened = " ".join(str(value) for item in items for value in item.values())
        self.assertIn("개장 전 핵심 · 6개", flattened)
        self.assertIn("6H · 5분 봉 · 핵심 6개", flattened)
        self.assertIn("오래됨", flattened)
        self.assertIn("갱신 필요", flattened)
        self.assertNotIn("선택 선물 1분봉 갱신", flattened)
        self.assertNotIn("9874", flattened)
        self.assertNotIn("2026-06-22 14:34:00", flattened)

    def test_futures_refresh_module_groups_live_and_macro_actions(self) -> None:
        from app.web.overview_dashboard import _futures_refresh_module_model

        snapshot = {
            "status": "REVIEW",
            "coverage": {
                "latest_age_minutes": 18,
                "oldest_age_minutes": 24,
            },
        }
        macro = {
            "coverage": {
                "latest_daily_date": "2026-06-19",
                "standardized_count": 16,
                "symbol_count": 16,
            }
        }

        model = _futures_refresh_module_model(
            snapshot=snapshot,
            macro=macro,
            selected_symbols=["NQ=F", "ZN=F", "CL=F"],
            refresh_mode="auto_60s",
        )

        self.assertEqual(model["title"], "자료 갱신")
        self.assertEqual([item["label"] for item in model["sources"]], ["실시간 차트 자료", "매크로 일봉 자료"])
        self.assertIn("1분봉", model["sources"][0]["basis"])
        self.assertIn("선택 선물 3개", model["sources"][0]["detail"])
        self.assertIn("최신 candle 18분", model["sources"][0]["detail"])
        self.assertIn("1D OHLCV", model["sources"][1]["basis"])
        self.assertIn("기준일 2026-06-19", model["sources"][1]["detail"])
        self.assertIn("16/16", model["sources"][1]["detail"])
        self.assertEqual([item["label"] for item in model["actions"]], ["1분봉 갱신", "일봉 매크로 갱신", "화면 다시 읽기"])
        self.assertEqual([mode["label"] for mode in model["modes"]], ["수동", "60초 자동 확인"])

    def test_futures_watch_strip_items_show_symbol_state_without_provider_run(self) -> None:
        from app.web.overview_dashboard import _futures_watch_strip_items

        rows = pd.DataFrame(
            [
                {"Symbol": "NQ=F", "State": "Stale", "15m %": -0.6, "60m %": -0.3, "Age Min": 26},
                {"Symbol": "ZN=F", "State": "Calm", "15m %": 0.1, "60m %": 0.2, "Age Min": 2},
            ]
        )
        snapshot = {
            "rows": rows,
            "latest_run": {"status": "success", "rows_written": 9874},
        }

        items = _futures_watch_strip_items(snapshot, ["NQ=F", "ZN=F"])

        self.assertEqual([item["symbol"] for item in items], ["NQ=F", "ZN=F"])
        self.assertEqual(items[0]["state"], "오래됨")
        self.assertIn("15분 -0.60%", items[0]["move"])
        flattened = " ".join(str(value) for item in items for value in item.values())
        self.assertNotIn("9874", flattened)
        self.assertNotIn("success", flattened)

    def test_futures_market_brief_model_places_scenario_and_support_together(self) -> None:
        from app.web.overview_dashboard import _futures_market_brief_model

        macro = {
            "coverage": {"standardized_count": 16, "symbol_count": 16, "latest_daily_date": "2026-06-19"},
            "summary": {
                "scenario": "혼재된 매크로 흐름",
                "sub_scenario": "성장 약세 + 방어 확인 부족",
                "regime_hint": "Risk-off 후보",
                "mixed_reason": "위험자산과 성장 proxy는 약하지만 안전자산 선호가 아직 충분하지 않습니다.",
            },
            "summary_sentences": ["현재 선물 일봉 기준 흐름이 한 방향으로 강하게 모이지 않습니다."],
            "evidence": ["Risk-On +14, Growth +1, Rate Pressure +46", "Dollar Pressure -13"],
            "confidence": {
                "label": "Low Confidence",
                "reasons": ["Most core symbols have 60D standardized moves."],
                "occurrence_count": 950,
                "hit_applicable": False,
            },
            "validation": {
                "status": "OK",
                "coverage": {"validation_dates": 1212, "history_span_years": 5.05},
                "current_scenario_metrics": {"Occurrence Count": 950},
            },
        }

        model = _futures_market_brief_model(macro)

        self.assertEqual(model["eyebrow"], "오늘 기준 시장 브리프")
        self.assertEqual(model["scenario"], "혼재된 매크로 흐름")
        self.assertEqual(model["sub_scenario"], "성장 약세 + 방어 확인 부족")
        self.assertEqual(model["regime_hint"], "Risk-off 후보")
        self.assertIn("안전자산 선호", model["mixed_reason"])
        self.assertIn("한 방향으로 강하게 모이지", model["sentence"])
        self.assertEqual([item["label"] for item in model["support_items"]], ["근거 강도", "과거 점검", "유사 구간", "자료 기준"])
        self.assertIn("위험선호 +14", " ".join(model["evidence_chips"]))
        self.assertNotIn("Risk-On", " ".join(model["evidence_chips"]))

    def test_futures_weekly_flow_model_ranks_driver_and_supports(self) -> None:
        from app.web.overview_dashboard import _futures_weekly_flow_model

        weekly_context = {
            "basis": "저장된 1D 선물 OHLCV의 최근 5거래일 변화율",
            "summary": "최근 1주 기준으로 원자재/물가 변화가 가장 두드러집니다(-2.93%).",
            "cards": [
                {"label": "위험선호", "value": "+2.20%", "detail": "지수 선물이 위험자산 선호를 지지합니다.", "tone": "positive"},
                {"label": "금리 부담", "value": "+0.24%", "detail": "중립권입니다.", "tone": "neutral"},
                {"label": "달러 압력", "value": "+0.75%", "detail": "달러 강세 압력처럼 읽힙니다.", "tone": "danger"},
                {"label": "원자재/물가", "value": "-2.93%", "detail": "물가 압력을 낮춥니다.", "tone": "positive"},
            ],
        }

        model = _futures_weekly_flow_model(weekly_context)

        self.assertEqual(model["title"], "최근 1주 흐름")
        self.assertEqual(model["driver"]["label"], "원자재/물가")
        self.assertEqual(model["driver"]["value"], "-2.93%")
        self.assertEqual([item["label"] for item in model["supporting"]], ["위험선호", "원자재/물가"])
        self.assertEqual([item["label"] for item in model["tempering"]], ["달러 압력"])
        self.assertIn("가장 두드러집니다", model["summary"])

    def test_overview_ui_css_defines_text_subtle_token_for_cockpit_readability(self) -> None:
        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()

        self.assertIn("--ov-mi-color-text-subtle:", css)
        self.assertIn(".ov-macro-brief-detail", css)

    def test_overview_ui_css_defines_source_confidence_lane(self) -> None:
        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()

        self.assertIn(".ov-source-confidence", css)
        self.assertIn(".ov-source-confidence-list", css)
        self.assertIn(".ov-source-confidence-row", css)

    def test_overview_ui_renders_supporting_sections_as_collapsible_disclosures(self) -> None:
        import inspect

        from app.web import overview_ui_components

        css = overview_ui_components.overview_ui_css()
        source = inspect.getsource(overview_ui_components)

        self.assertIn(".ov-context-disclosure", css)
        self.assertIn(".ov-context-disclosure > summary", css)
        self.assertIn(
            '<details class="ov-macro-reading-section ov-source-confidence ov-source-ledger ov-context-disclosure is-evidence-footer"',
            source,
        )
        self.assertIn('<summary class="ov-source-confidence-summary"', source)
        self.assertIn('<details class="ov-ia-closeout ov-context-disclosure"', source)
        self.assertIn('<summary class="ov-ia-closeout-summary"', source)
        self.assertNotIn('<section class="ov-ia-closeout">', source)

    def test_overview_ui_css_defines_market_context_summary_rail(self) -> None:
        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()

        self.assertIn(".ov-macro-cockpit-rail", css)
        self.assertIn(".ov-macro-status-item", css)
        self.assertIn(".ov-macro-section-title", css)
        self.assertIn(".ov-macro-cockpit-refresh-assist", css)
        self.assertIn(".ov-macro-brief-row", css)
        self.assertIn(".ov-macro-cue-row", css)
        self.assertIn(".ov-macro-cue-action", css)

    def test_overview_market_context_findings_use_rail_without_card_left_rule(self) -> None:
        import re

        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()
        scoped_match = re.search(r"\.ov-context-finding-row \{(?P<body>.*?)\n\}", css, re.S)
        self.assertIsNotNone(scoped_match, "Market Context findings should render as rail rows.")
        scoped_body = scoped_match.group("body") if scoped_match else ""

        self.assertIn("grid-template-columns: minmax(5rem, 0.22fr)", scoped_body)
        self.assertIn("padding: 0.72rem 0;", scoped_body)
        self.assertNotIn("border-left", scoped_body)
        self.assertNotIn("min-height", scoped_body)

    def test_overview_market_context_keeps_historical_analog_out_of_default_entry(self) -> None:
        helper_body = Path("app/web/overview/market_context.py").read_text(encoding="utf-8")
        helper_body = helper_body[helper_body.index("def render_market_context_tab"):]

        self.assertIn("render_macro_context_cockpit(cockpit_model, include_reading_flow=False)", helper_body)
        self.assertNotIn("_legacy._render_overview_historical_analog_repair_action(cockpit_model)", helper_body)
        self.assertNotIn("_render_overview_historical_analog_controls()", helper_body)
        self.assertNotIn("render_macro_context_reading_flow(", helper_body)
        cockpit_index = helper_body.index("render_macro_context_cockpit(cockpit_model, include_reading_flow=False)")
        refresh_bar_index = helper_body.index("render_market_context_refresh_bar(cockpit_model)")
        self.assertLess(cockpit_index, refresh_bar_index)

    def test_overview_market_context_keeps_historical_analog_controls_available_but_not_rendered(self) -> None:
        source = Path("app/web/overview_ui_components.py").read_text(encoding="utf-8")
        market_context_source = Path("app/web/overview/market_context.py").read_text(encoding="utf-8")
        self.assertIn("_macro_cockpit_historical_analog_html", source)
        self.assertIn("Macro 조건 결과 비교", source)
        self.assertIn("macro_dimension_audit", source)
        helper_body = market_context_source[market_context_source.index("def render_market_context_tab"):]

        self.assertNotIn("initial_analog_controls = _legacy._overview_historical_analog_control_state()", helper_body)
        self.assertNotIn("analog_controls = _legacy._render_overview_historical_analog_controls()", helper_body)
        self.assertNotIn("if analog_controls != initial_analog_controls:", helper_body)
        self.assertNotIn("as_of_date=initial_analog_controls", helper_body)
        self.assertNotIn("pattern_window=str(initial_analog_controls", helper_body)
        self.assertNotIn("as_of_date=analog_controls", helper_body)
        self.assertNotIn("pattern_window=str(analog_controls", helper_body)
        self.assertIn("render_macro_context_cockpit(cockpit_model, include_reading_flow=False)", helper_body)
        self.assertNotIn("render_macro_context_reading_flow(", helper_body)

    def test_overview_market_context_historical_analog_can_reuse_visible_sector_snapshot(self) -> None:
        from app.web import overview_dashboard_helpers

        visible_snapshot = {
            "status": "OK",
            "rows": pd.DataFrame(
                [
                    {"Rank": 1, "Group": "Consumer Cyclical", "Market Cap Weighted Return %": 3.4},
                    {"Rank": 2, "Group": "Basic Materials", "Market Cap Weighted Return %": 1.1},
                ]
            ),
        }
        captured: dict[str, object] = {}

        def fake_loader(**kwargs):
            raise AssertionError(f"historical analog should not reload sector leadership: {kwargs}")

        def fake_builder(**kwargs):
            captured.update(kwargs)
            return {"status": "OK", "leadership_sector": "Consumer Cyclical", "proxy_etf": "XLY"}

        with patch.object(overview_dashboard_helpers, "load_overview_group_leadership_snapshot", side_effect=fake_loader):
            with patch.object(overview_dashboard_helpers, "build_historical_analog_snapshot", side_effect=fake_builder):
                result = overview_dashboard_helpers.load_overview_market_context_historical_analog(
                    as_of_date=None,
                    pattern_window="20D",
                    events_snapshot={"status": "OK"},
                    group_leadership_snapshot=visible_snapshot,
                )

        self.assertEqual(result["proxy_etf"], "XLY")
        self.assertIs(captured["group_leadership_snapshot"], visible_snapshot)
        self.assertEqual(captured["pattern_window"], "20D")

    def test_overview_market_context_uses_cardless_brief_layout_contract(self) -> None:
        from app.web import overview_ui_components

        css = overview_ui_components.overview_ui_css()
        cue_html = overview_ui_components._macro_cockpit_interpretation_cues_html(
            [
                {
                    "label": "가까운 주요 이벤트",
                    "value": "다음 FOMC 2일 후",
                    "detail": "FOMC Meeting",
                    "status": "REVIEW",
                    "target_tab": "Events",
                    "freshness": "2026-06-15",
                }
            ]
        )
        analog_html = overview_ui_components._macro_cockpit_historical_analog_html(
            {
                "status": "INSUFFICIENT_DATA",
                "headline": "과거 유사 맥락 자료 부족",
                "detail": "Industrials(XLI) coverage 부족",
                "leadership_sector": "Industrials",
                "proxy_etf": "XLI",
                "sample_count": 0,
                "data_window": "",
                "rows": [],
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )
        source_html = overview_ui_components._macro_cockpit_source_confidence_html(
            {
                "status": "REVIEW",
                "summary": {"detail": "저장 자료 기준"},
                "items": [
                    {
                        "surface": "Prices",
                        "status": "REVIEW",
                        "title": "가격 자료",
                        "detail": "stale",
                        "freshness": "2026-06-15",
                        "owner": "Ingestion",
                        "caveat": "context only",
                    }
                ],
                "boundary_note": "context only",
            }
        )

        self.assertIn(".ov-macro-cues-list", css)
        self.assertIn(".ov-context-finding-rail", css)
        self.assertIn(".ov-analog-basis-bar", css)
        self.assertIn(".ov-source-ledger", css)
        self.assertIn("ov-context-finding-rail", cue_html)
        self.assertIn("ov-context-finding-row", cue_html)
        self.assertIn("ov-historical-analog-row", analog_html)
        self.assertIn("ov-historical-analog-scope", analog_html)
        self.assertIn("기준 변경은 아래 과거 참고 통계에만 적용", analog_html)
        self.assertIn("ov-analog-basis-bar", analog_html)
        self.assertIn("ov-source-confidence-list", source_html)
        self.assertIn("ov-source-ledger", source_html)
        self.assertNotIn("ov-macro-cues-grid", cue_html)
        self.assertNotIn("ov-source-confidence-card", source_html)
        self.assertNotIn("ov-historical-analog-empty", analog_html)

    def test_overview_market_context_keeps_market_brief_to_actionable_context(self) -> None:
        from app.web import overview_ui_components

        model = {
            "status": "REVIEW",
            "summary": {
                "headline": "오늘 가장 큰 움직임은 SNDK +14.5%입니다.",
                "detail": "Technology 리더십이 확인되고, 선물/매크로 배경은 금리 압력입니다.",
                "tone": "warning",
                "rail": [
                    {"label": "자료 상태", "value": "확인 필요", "detail": "3 checks", "tone": "warning"},
                    {"label": "Top Mover", "value": "SNDK +14.5%", "detail": "stale", "tone": "warning"},
                ],
            },
            "sector_pressure": {},
            "event_timeline": {},
            "brief_rows": [
                {
                    "label": "무엇이 움직였나",
                    "value": "SNDK +14.5%",
                    "detail": "Technology 안에서 단일 종목 영향이 컸는지 breadth와 함께 확인합니다.",
                    "tone": "warning",
                },
                {
                    "label": "확산",
                    "value": "Technology 우위",
                    "detail": "리더십 sector와 market mover가 같은 방향인지 봅니다.",
                    "tone": "positive",
                },
                {
                    "label": "Futures/Macro 배경",
                    "value": "장중 macro 해석 보류",
                    "detail": "Futures Monitor 1m OHLCV가 오래되어 risk-on / 금리 압력 설명은 낮게 봅니다.",
                    "tone": "warning",
                },
            ],
            "context_findings": [
                {
                    "label": "Events",
                    "conclusion": "추정 일정 71개는 검증/신선도 제한이 있어 확정 일정처럼 읽으면 안 됩니다.",
                    "interpretation": "오늘 브리프의 이벤트 배경은 caveat로만 둡니다.",
                    "evidence": "96개 추정 일정 · 71개 제한",
                    "source_area": "Events · Earnings estimates",
                    "freshness": "2026-06-15",
                    "priority": "P1",
                    "tone": "warning",
                },
                {
                    "label": "Futures / 금리 압력",
                    "conclusion": "선물 맥락은 risk-on 흐름과 금리 압력이 같이 보입니다.",
                    "interpretation": "주식 강세를 단순 위험선호로만 읽기 어렵습니다.",
                    "evidence": "Risk-on with rate pressure",
                    "source_area": "Futures Macro Thermometer",
                    "freshness": "2026-06-15",
                    "priority": "P2",
                    "tone": "warning",
                },
            ],
            "historical_analog": {},
            "source_confidence": {},
            "boundary_note": "context only",
        }

        cockpit_html = overview_ui_components._macro_context_cockpit_html(model, include_reading_flow=False)
        full_html = overview_ui_components._macro_context_cockpit_html(model)
        reading_html = overview_ui_components._macro_context_reading_flow_html(
            model,
            include_brief=False,
            include_historical_analog=False,
            include_source_confidence=False,
        )

        self.assertIn("ov-market-brief-lane", cockpit_html)
        self.assertIn("오늘의 시장 브리프", cockpit_html)
        self.assertIn("무엇이 움직였나", cockpit_html)
        self.assertIn("장중 macro 해석 보류", cockpit_html)
        self.assertIn("risk-on / 금리 압력 설명은 낮게 봅니다.", cockpit_html)
        self.assertNotIn("이벤트 배경", cockpit_html)
        self.assertNotIn("직접 원인 근거 약함", cockpit_html)
        self.assertNotIn("오늘 움직임의 원인을 이벤트로 단정하지 않습니다.", cockpit_html)
        self.assertNotIn("브리프 신뢰도", cockpit_html)
        self.assertNotIn("이벤트 일정", cockpit_html)
        self.assertNotIn("선물 기반 장중 해석 제한", cockpit_html)
        self.assertNotIn("이벤트 caveat", cockpit_html)
        self.assertNotIn("자료 신뢰도 caveat", cockpit_html)
        self.assertNotIn("ov-macro-reading-section ov-macro-brief", cockpit_html)
        self.assertNotIn("맥락 검토 결과", full_html)
        self.assertNotIn("ov-context-finding-rail", full_html)
        self.assertNotIn("맥락 검토 결과", reading_html)
        self.assertNotIn("ov-context-finding-rail", reading_html)
        self.assertNotIn("관찰 지점", full_html)
        self.assertNotIn("확인 위치", full_html)
        self.assertNotIn("확인하세요", full_html)
        self.assertNotIn("ov-macro-cues-list", full_html)
        self.assertNotIn("ov-macro-cue-row", full_html)

    def test_overview_market_context_v2_css_removes_repeated_card_grid_language(self) -> None:
        import re

        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()
        reading_section = re.search(r"\.ov-macro-reading-section \{(?P<body>.*?)\n\}", css, re.S)
        macro_comparison = re.search(r"\.ov-macro-compare-section \{(?P<body>.*?)\n\}", css, re.S)
        next_check_rail = re.search(r"\.ov-context-finding-rail \{(?P<body>.*?)\n\}", css, re.S)
        next_check_row = re.search(r"\.ov-context-finding-row \{(?P<body>.*?)\n\}", css, re.S)

        self.assertIsNotNone(reading_section)
        self.assertIsNotNone(macro_comparison)
        self.assertIsNotNone(next_check_rail)
        self.assertIsNotNone(next_check_row)

        reading_body = reading_section.group("body") if reading_section else ""
        macro_body = macro_comparison.group("body") if macro_comparison else ""
        rail_body = next_check_rail.group("body") if next_check_rail else ""
        row_body = next_check_row.group("body") if next_check_row else ""

        self.assertIn("background: transparent", reading_body)
        self.assertNotIn("border-left", reading_body)
        self.assertIn("display: grid", rail_body)
        self.assertIn("grid-template-columns: minmax(5rem, 0.22fr) minmax(0, 1.1fr) minmax(0, 1.15fr) minmax(12rem, 0.8fr)", row_body)
        self.assertNotIn("min-height", row_body)
        self.assertNotIn("repeat(3", rail_body)
        self.assertIn("background: transparent", macro_body)
        self.assertNotIn("border-bottom", macro_body)

    def test_overview_source_confidence_summary_exposes_scan_metrics_before_opening(self) -> None:
        from app.web import overview_ui_components

        source_html = overview_ui_components._macro_cockpit_source_confidence_html(
            {
                "status": "REVIEW",
                "status_label": "자료 확인 필요",
                "summary": {
                    "detail": "일부 저장 자료 확인 필요",
                    "ok_count": 3,
                    "review_count": 2,
                    "missing_count": 1,
                },
                "items": [
                    {
                        "surface": "Prices",
                        "status": "REVIEW",
                        "title": "가격 자료",
                        "detail": "기준일 오래됨",
                        "freshness": "Update due",
                        "owner": "Data Health",
                        "caveat": "context only",
                        "next_check": "Market Movers 기준일과 누락 상태가 가격 맥락의 신뢰도 주의점입니다.",
                    },
                    {
                        "surface": "Events",
                        "status": "OK",
                        "title": "이벤트 자료",
                        "detail": "공식/추정 혼합",
                        "freshness": "Fresh",
                        "owner": "Events",
                        "caveat": "estimate caveat",
                        "next_check": "Events source type이 이벤트 자료 주의점입니다.",
                    },
                ],
                "boundary_note": "context only",
            }
        )

        self.assertIn("ov-source-confidence-strip", source_html)
        self.assertIn("정상 3", source_html)
        self.assertIn("보강 2", source_html)
        self.assertIn("부족 1", source_html)
        self.assertIn("Prices", source_html)
        self.assertIn("가격 맥락의 신뢰도 주의점", source_html)

    def test_overview_source_confidence_groups_reference_and_meta_without_unresolved_copy(self) -> None:
        from app.web import overview_ui_components

        source_html = overview_ui_components._macro_cockpit_source_confidence_html(
            {
                "status": "OK",
                "status_label": "자료 정상 · 참고 제한",
                "summary": {
                    "detail": "브리프 자료와 참고/관리 메타를 분리합니다.",
                    "ok_count": 3,
                    "review_count": 0,
                    "reference_count": 2,
                    "missing_count": 0,
                },
                "items": [
                    {
                        "surface": "Market Movers",
                        "status": "OK",
                        "status_label": "자료 정상",
                        "title": "Prices / Movers",
                        "detail": "가격 움직임 자료",
                        "freshness": "2026-06-20 12:35",
                        "owner": "Overview",
                        "caveat": "context only",
                        "next_check": "-",
                        "source_role": "brief_source",
                        "counts_for_status": True,
                    },
                    {
                        "surface": "Events",
                        "status": "REFERENCE_LIMIT",
                        "status_label": "참고 제한",
                        "title": "Events",
                        "detail": "추정 일정은 확정 일정처럼 읽지 않습니다.",
                        "freshness": "2026-06-20 12:36",
                        "owner": "Events",
                        "caveat": "원인 분석 엔진이 아닙니다.",
                        "next_check": "-",
                        "source_role": "reference_context",
                        "counts_for_status": False,
                    },
                    {
                        "surface": "Data Health",
                        "status": "META",
                        "status_label": "관리 메타",
                        "title": "Data Health",
                        "detail": "보강 가능한 항목은 필요 자료 보강에 반영됩니다.",
                        "freshness": "2026-06-20 12:36",
                        "owner": "Data Health",
                        "caveat": "자료 관리 메타입니다.",
                        "next_check": "-",
                        "source_role": "management_meta",
                        "counts_for_status": False,
                    },
                ],
                "boundary_note": "context only",
            }
        )

        self.assertIn("시장 브리프 직접 자료", source_html)
        self.assertIn("참고 / 관리 자료", source_html)
        self.assertIn("참고 2", source_html)
        self.assertIn("Events", source_html)
        self.assertIn("참고 제한", source_html)
        self.assertIn("Data Health", source_html)
        self.assertIn("관리 메타", source_html)
        self.assertNotIn("Events · 자료 확인 필요", source_html)
        self.assertNotIn("Data Health · 자료 확인 필요", source_html)

    def test_overview_source_confidence_uses_ledger_language_without_review_gate_copy(self) -> None:
        from app.web import overview_ui_components

        source_html = overview_ui_components._macro_cockpit_source_confidence_html(
            {
                "status": "REVIEW",
                "status_label": "자료 확인 필요",
                "summary": {
                    "detail": "필요 자료를 확인하고 보강할 위치를 정리합니다.",
                    "ok_count": 1,
                    "review_count": 1,
                    "missing_count": 0,
                },
                "items": [
                    {
                        "surface": "Futures Monitor",
                        "status": "REVIEW",
                        "title": "Futures Monitor 1m OHLCV",
                        "detail": "선물 가격 이력 freshness를 확인합니다.",
                        "freshness": "3950m old",
                        "owner": "Data Health",
                        "caveat": "시장 맥락 참고용",
                        "next_check": "필요 자료 보강에서 기존 Overview 갱신을 실행합니다.",
                    }
                ],
                "boundary_note": (
                    "Market Context는 저장 자료의 출처와 한계를 설명하는 참고 화면이며, "
                    "승인/차단 판단이나 운영 알림을 만들지 않습니다."
                ),
            }
        )

        self.assertIn("ov-source-ledger", source_html)
        self.assertIn("자료 기준", source_html)
        self.assertIn("사용 위치", source_html)
        self.assertIn("보강 판단", source_html)
        self.assertIn("필요 자료 보강", source_html)
        for forbidden in ["PASS", "BLOCKER", "Final Review decision", "Operations monitoring", "monitoring action"]:
            self.assertNotIn(forbidden, source_html)

    def test_overview_source_confidence_renders_status_board_not_diagnostic_table(self) -> None:
        from app.web import overview_ui_components

        source_html = overview_ui_components._macro_cockpit_source_confidence_html(
            {
                "status": "OK",
                "status_label": "자료 정상 · 참고 제한",
                "summary": {
                    "detail": "브리프 자료는 정상이고 참고 제한은 분리합니다.",
                    "ok_count": 4,
                    "review_count": 0,
                    "reference_count": 2,
                    "missing_count": 0,
                },
                "items": [
                    {
                        "surface": "Market Movers",
                        "status": "OK",
                        "status_label": "자료 정상",
                        "title": "Prices / Movers",
                        "detail": "503/503 symbols returnable",
                        "freshness": "2026-06-20 13:57",
                        "owner": "Workspace > Ingestion plus Overview refresh",
                        "caveat": "가격 맥락 참고용",
                        "next_check": "-",
                        "source_role": "brief_source",
                        "counts_for_status": True,
                    },
                    {
                        "surface": "Events",
                        "status": "REFERENCE_LIMIT",
                        "status_label": "참고 제한",
                        "title": "Events",
                        "detail": "추정 일정은 확정 일정처럼 읽지 않습니다.",
                        "freshness": "2026-06-20 12:36",
                        "owner": "Events",
                        "caveat": "원인 분석 엔진이 아닙니다.",
                        "next_check": "-",
                        "source_role": "reference_context",
                        "counts_for_status": False,
                    },
                    {
                        "surface": "Data Health",
                        "status": "META",
                        "status_label": "관리 메타",
                        "title": "Data Health",
                        "detail": "보강 가능한 항목은 별도 보강 판단에 반영됩니다.",
                        "freshness": "2026-06-22 09:09",
                        "owner": "Data Health",
                        "caveat": "자료 관리 메타입니다.",
                        "next_check": "-",
                        "source_role": "management_meta",
                        "counts_for_status": False,
                    },
                ],
                "boundary_note": "context only",
            }
        )

        self.assertIn("ov-source-status-board", source_html)
        self.assertIn("자료 상태 요약", source_html)
        self.assertIn("시장 브리프 직접 자료", source_html)
        self.assertIn("참고 / 관리 자료", source_html)
        self.assertIn("보강 판단", source_html)
        self.assertIn("브리프 자료 정상 4개", source_html)
        self.assertIn("현재 보강 대상 0개", source_html)
        self.assertIn("참고 제한 2개", source_html)
        self.assertNotIn("자료 영역", source_html)
        self.assertNotIn("관리 위치:", source_html)

    def test_overview_market_context_refresh_bar_has_compact_no_action_state(self) -> None:
        source = Path("app/web/overview/market_context_helpers.py").read_text(encoding="utf-8")
        self.assertIn("_render_overview_market_context_refresh_status_panel(", source)
        self.assertIn("ov-refresh-status-panel", source)
        self.assertIn("if not action_ids:", source)
        self.assertIn("전체 Market Context 자료 보강", source)

        no_action_branch = source[source.index("if not action_ids:") : source.index("else:", source.index("if not action_ids:"))]
        self.assertNotIn('summary.get("primary_button_label")', no_action_branch)
        self.assertNotIn('key="overview_market_context_refresh_smart"', no_action_branch)

    def test_overview_macro_context_model_includes_hybrid_visual_fields(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        model = build_overview_macro_context_cockpit(
            market_movers_snapshot={
                "status": "OK",
                "coverage": {"returnable_count": 2, "universe_count": 2, "effective_end_date": "2026-06-15"},
                "rows": [
                    {
                        "Symbol": "SNDK",
                        "Name": "Sandisk",
                        "Sector": "Technology",
                        "Return %": 14.5,
                        "Volume Ratio": 2.0,
                    }
                ],
            },
            group_leadership_snapshot={
                "status": "OK",
                "coverage": {"returnable_count": 20, "universe_count": 20, "effective_end_date": "2026-06-15"},
                "rows": [
                    {
                        "Rank": 1,
                        "Group": "Industrials",
                        "Symbols": 10,
                        "Positive Symbols": 9,
                        "Positive Symbol Share %": 90.0,
                        "Market Cap Weighted Return %": 3.3,
                        "Equal Weight Return %": 2.1,
                        "Top 3 Positive Share %": 35.0,
                        "Top Symbol": "CAT",
                        "Top Symbol Return %": 4.2,
                    },
                    {
                        "Rank": 2,
                        "Group": "Technology",
                        "Symbols": 10,
                        "Positive Symbols": 6,
                        "Positive Symbol Share %": 60.0,
                        "Market Cap Weighted Return %": 1.2,
                        "Equal Weight Return %": 1.0,
                        "Top 3 Positive Share %": 45.0,
                        "Top Symbol": "SNDK",
                        "Top Symbol Return %": 14.5,
                    },
                ],
            },
            futures_macro_snapshot={
                "status": "OK",
                "coverage": {"latest_date": "2026-06-15"},
                "summary": {"scenario": "좋은 risk-on", "summary": "금리 부담 제한"},
                "scores": [{"Metric": "Risk Appetite", "Score": 54}],
            },
            sentiment_snapshot={
                "status": "OK",
                "coverage": {"cnn_score": 29.7, "cnn_rating": "fear", "aaii_bull_bear_spread": -17.3},
                "analysis": {"phase_label": "공포 우위", "headline": "공포 심리가 우위", "data_confidence": {"status": "OK", "detail": "fresh"}},
            },
            events_snapshot={
                "status": "OK",
                "coverage": {"event_count": 2, "needs_review_count": 1, "latest_collected_at": "2026-06-15"},
                "rows": [
                    {
                        "Date": "2026-06-17",
                        "Type": "FOMC_MEETING",
                        "Type Label": "FOMC",
                        "Title": "FOMC Meeting",
                        "Days Until": 2,
                        "Source Type": "Official",
                        "Validation": "Official",
                        "Freshness": "Official",
                        "Quality Action": "No action",
                        "Importance": "High",
                    },
                    {
                        "Date": "2026-06-22",
                        "Type": "MACRO_CPI",
                        "Type Label": "CPI",
                        "Title": "CPI",
                        "Days Until": 7,
                        "Source Type": "Unknown",
                        "Validation": "Unknown",
                        "Freshness": "Stale source",
                        "Quality Action": "Inspect source freshness",
                        "Importance": "High",
                    },
                ],
            },
            collection_ops_snapshot={
                "status": "OK",
                "coverage": {"ok_count": 2, "due_count": 1, "stale_count": 0, "partial_count": 0, "missing_count": 0, "failed_count": 0},
                "rows": [],
            },
        )

        self.assertIn("sector_pressure", model)
        self.assertIn("event_timeline", model)
        self.assertGreaterEqual(len(model["sector_pressure"]["heatmap_rows"]), 2)
        self.assertGreaterEqual(len(model["event_timeline"]["items"]), 2)

    def test_overview_market_context_renders_tape_heatmap_and_timeline_contract(self) -> None:
        from app.web import overview_ui_components

        css = overview_ui_components.overview_ui_css()
        model = {
            "status": "REVIEW",
            "summary": {
                "headline": "오늘 가장 큰 움직임은 SNDK +14.5%입니다.",
                "detail": "Industrials 리더십이 확인되고, 선물/매크로 배경은 risk-on입니다. 확인할 자료 7개를 먼저 본 뒤 Market Movers, Sector, Futures 흐름을 함께 읽으세요.",
                "tone": "warning",
                "rail": [
                    {"label": "자료 상태", "value": "확인 필요", "detail": "7 checks", "tone": "warning"},
                    {"label": "Top Mover", "value": "SNDK +14.5%", "detail": "stale", "tone": "warning"},
                    {"label": "Breadth", "value": "Industrials", "detail": "91%", "tone": "positive"},
                    {"label": "Macro", "value": "Risk-on", "detail": "rates muted", "tone": "positive"},
                    {"label": "Next Event", "value": "FOMC D-2", "detail": "review", "tone": "warning"},
                ],
            },
            "sector_pressure": {
                "summary": {"headline": "Broad participation"},
                "heatmap_rows": [
                    {"group": "Industrials", "market_cap_weighted_return_pct": 3.3, "positive_symbol_share_pct": 91, "symbols": 70, "tone": "positive"},
                    {"group": "Technology", "market_cap_weighted_return_pct": 1.2, "positive_symbol_share_pct": 61, "symbols": 80, "tone": "primary"},
                ],
                "coverage": {"freshness": "2026-06-15"},
            },
            "event_timeline": {
                "items": [
                    {"cluster": "FOMC", "title": "FOMC Meeting", "days_until": 2, "freshness": "Official", "tone": "warning"},
                    {"cluster": "CPI", "title": "CPI", "days_until": 7, "freshness": "Stale source", "tone": "warning"},
                ],
                "coverage": {"review_count": 1, "latest_collected_at": "2026-06-15"},
            },
            "brief_rows": [],
            "interpretation_cues": [],
            "boundary_note": "context only",
        }

        html = overview_ui_components._macro_cockpit_body_html(model)

        self.assertIn(".ov-macro-hybrid-tape", css)
        self.assertIn(".ov-sector-pressure-map", css)
        self.assertIn(".ov-event-timeline", css)
        self.assertIn("ov-macro-hybrid-tape", html)
        self.assertIn("ov-sector-pressure-map", html)
        self.assertIn("ov-event-timeline", html)
        self.assertIn("ov-sector-pressure-tile", html)
        self.assertIn("ov-event-timeline-row", html)

    def test_overview_market_context_splits_dashboard_from_reading_flow_contract(self) -> None:
        from app.web import overview_ui_components

        model = {
            "status": "REVIEW",
            "summary": {
                "headline": "오늘 가장 큰 움직임은 SNDK +14.5%입니다.",
                "detail": "Industrials 리더십이 확인되고, 선물/매크로 배경은 risk-on입니다. 확인할 자료 7개를 먼저 본 뒤 Market Movers, Sector, Futures 흐름을 함께 읽으세요.",
                "tone": "warning",
                "rail": [
                    {"label": "자료 상태", "value": "확인 필요", "detail": "7 checks", "tone": "warning"},
                    {"label": "Top Mover", "value": "SNDK +14.5%", "detail": "stale", "tone": "warning"},
                    {"label": "Breadth", "value": "Industrials", "detail": "91%", "tone": "positive"},
                    {"label": "Macro", "value": "Risk-on", "detail": "rates muted", "tone": "positive"},
                    {"label": "Next Event", "value": "FOMC D-2", "detail": "review", "tone": "warning"},
                ],
            },
            "sector_pressure": {
                "summary": {"headline": "Broad participation"},
                "heatmap_rows": [
                    {"group": "Industrials", "market_cap_weighted_return_pct": 3.3, "positive_symbol_share_pct": 91, "symbols": 70, "tone": "positive"},
                ],
                "coverage": {"freshness": "2026-06-15"},
            },
            "event_timeline": {
                "items": [{"cluster": "FOMC", "title": "FOMC Meeting", "days_until": 2, "freshness": "Official", "tone": "warning"}],
                "coverage": {"review_count": 1, "latest_collected_at": "2026-06-15"},
            },
            "brief_rows": [
                {"label": "무엇이 움직였나", "value": "SNDK +14.5%", "detail": "Technology leader", "tone": "warning"},
                {
                    "label": "이벤트 배경",
                    "value": "직접 원인 근거 약함",
                    "detail": "가까운 FOMC 일정은 배경 변수지만 오늘 움직임의 원인으로 단정하지 않습니다.",
                    "tone": "warning",
                },
            ],
            "interpretation_cues": [
                {"label": "구형 해석 cue", "value": "렌더링 대상 아님", "detail": "legacy", "tone": "warning"},
            ],
            "context_findings": [
                {
                    "label": "Events",
                    "conclusion": "FOMC 일정이 시장 해석을 바꿀 수 있는 가까운 event입니다.",
                    "interpretation": "이벤트는 오늘 브리프의 배경 변수로만 둡니다.",
                    "evidence": "Official macro · 2026-06-15",
                    "source_area": "Events · Official macro",
                    "freshness": "2026-06-15",
                    "priority": "P1",
                    "tone": "warning",
                },
            ],
            "historical_analog": {
                "status": "INSUFFICIENT_DATA",
                "headline": "과거 유사 맥락 자료 부족",
                "detail": "XLI coverage 부족",
                "leadership_sector": "Industrials",
                "proxy_etf": "XLI",
                "sample_count": 0,
                "data_window": "",
                "rows": [],
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            },
            "source_confidence": {"status": "OK", "summary": {"detail": "저장 자료 기준"}, "items": []},
            "boundary_note": "context only",
        }

        html = overview_ui_components._macro_context_cockpit_html(model)
        cockpit_html = html.split('<section class="ov-macro-reading-flow"', 1)[0]
        reading_html = html.split('<section class="ov-macro-reading-flow"', 1)[1]

        self.assertIn('<section class="ov-macro-cockpit"', cockpit_html)
        self.assertIn("ov-macro-cockpit-narrative", cockpit_html)
        self.assertIn("오늘 가장 큰 움직임은 SNDK +14.5%입니다.", cockpit_html)
        self.assertNotIn("현재 맥락:", cockpit_html)
        self.assertIn("ov-macro-hybrid-tape", cockpit_html)
        self.assertIn("ov-macro-visual-board", cockpit_html)
        self.assertIn("오늘의 시장 브리프", cockpit_html)
        self.assertIn("ov-market-brief-lane", cockpit_html)
        self.assertIn("이벤트 배경", cockpit_html)
        self.assertIn("직접 원인 근거 약함", cockpit_html)
        self.assertIn("오늘 움직임의 원인으로 단정하지 않습니다.", cockpit_html)
        self.assertNotIn("브리프 신뢰도", cockpit_html)
        self.assertNotIn("이벤트 caveat", cockpit_html)
        self.assertNotIn("해석할 때 같이 볼 변수", cockpit_html)
        self.assertNotIn("과거 유사 맥락 참고", cockpit_html)
        self.assertNotIn("구형 해석 cue", reading_html)
        self.assertNotIn("ov-macro-reading-section ov-macro-brief", reading_html)
        self.assertNotIn("ov-macro-reading-section ov-macro-cues", reading_html)
        self.assertNotIn("ov-context-finding-rail", reading_html)
        self.assertNotIn("맥락 검토 결과", reading_html)
        self.assertNotIn("Events에서 official source를 확인하세요.", reading_html)
        self.assertNotIn("확인 위치", reading_html)
        self.assertIn("ov-macro-reading-section ov-historical-analog-row", reading_html)
        self.assertIn("ov-macro-reading-section ov-source-confidence", reading_html)

    def test_overview_market_context_relabels_supporting_flow_as_next_context_reference_and_evidence(self) -> None:
        from app.web import overview_ui_components

        model = {
            "status": "REVIEW",
            "summary": {
                "headline": "오늘 가장 큰 움직임은 SNDK +14.5%입니다.",
                "detail": "Technology 리더십이 확인되고, 선물/매크로 배경은 금리 압력입니다. 확인할 자료 3개를 먼저 본 뒤 Market Movers, Sector, Futures 흐름을 함께 읽으세요.",
                "tone": "warning",
                "rail": [
                    {"label": "자료 상태", "value": "확인 필요", "detail": "3 checks", "tone": "warning"},
                    {"label": "Top Mover", "value": "SNDK +14.5%", "detail": "stale", "tone": "warning"},
                    {"label": "Breadth", "value": "Technology", "detail": "91%", "tone": "positive"},
                    {"label": "Macro", "value": "금리 압력", "detail": "rates firm", "tone": "warning"},
                    {"label": "Next Event", "value": "FOMC D-2", "detail": "review", "tone": "warning"},
                ],
            },
            "sector_pressure": {},
            "event_timeline": {},
            "brief_rows": [
                {"label": "무엇이 움직였나", "value": "SNDK +14.5%", "detail": "Technology leader", "tone": "warning"},
                {
                    "label": "이벤트 배경",
                    "value": "직접 원인 근거 약함",
                    "detail": "추정 일정이 많아 오늘 움직임의 원인을 이벤트로 단정하지 않습니다.",
                    "tone": "warning",
                },
            ],
            "interpretation_cues": [
                {"label": "구형 해석 cue", "value": "렌더링 대상 아님", "detail": "legacy", "tone": "warning"},
            ],
            "context_findings": [
                {
                    "label": "Events",
                    "conclusion": "추정 일정 중 검증/신선도 제한이 있어 확정 일정처럼 읽으면 안 됩니다.",
                    "interpretation": "오늘 브리프의 이벤트 배경은 caveat로만 둡니다.",
                    "evidence": "Events · Earnings estimates",
                    "source_area": "Events · Earnings estimates",
                    "freshness": "2026-06-15",
                    "priority": "P1",
                    "tone": "warning",
                },
                {
                    "label": "Futures / 금리 압력",
                    "conclusion": "선물 맥락은 risk-on 흐름과 금리 압력이 같이 보입니다.",
                    "interpretation": "주식 강세를 단순 위험선호로만 읽기 어렵습니다.",
                    "evidence": "Futures Macro Thermometer",
                    "source_area": "Futures Macro Thermometer",
                    "freshness": "2026-06-15",
                    "priority": "P2",
                    "tone": "warning",
                },
            ],
            "historical_analog": {
                "status": "INSUFFICIENT_DATA",
                "headline": "과거 유사 맥락 자료 부족",
                "detail": "XLK coverage 부족",
                "leadership_sector": "Technology",
                "proxy_etf": "XLK",
                "sample_count": 0,
                "data_window": "",
                "rows": [],
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            },
            "source_confidence": {"status": "REVIEW", "summary": {"detail": "저장 자료 기준"}, "items": []},
            "boundary_note": "context only",
        }

        html = overview_ui_components._macro_context_cockpit_html(model)

        self.assertNotIn("맥락 검토 결과", html)
        self.assertNotIn("Market Context가 이미 읽은 보조 맥락", html)
        self.assertNotIn("ov-context-finding-rail", html)
        self.assertIn("이벤트 배경", html)
        self.assertIn("직접 원인 근거 약함", html)
        self.assertIn("오늘 움직임의 원인을 이벤트로 단정하지 않습니다.", html)
        self.assertNotIn("브리프 신뢰도", html)
        self.assertNotIn("이벤트 일정", html)
        self.assertNotIn("선물 기반 장중 해석 제한", html)
        self.assertNotIn("이벤트 caveat", html)
        self.assertNotIn("자료 신뢰도 caveat", html)
        self.assertNotIn("다음 맥락 체크", html)
        self.assertNotIn("확인 위치", html)
        self.assertNotIn("확인하세요", html)
        self.assertNotIn("구형 해석 cue", html)
        self.assertIn("참고: 과거 유사 맥락", html)
        self.assertIn("근거: 자료 기준 / 출처 상태", html)
        self.assertNotIn("해석할 때 같이 볼 변수", html)
        self.assertNotIn("자료 상태 주의점", html)

    def test_overview_ui_css_defines_market_context_reading_sections(self) -> None:
        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()

        self.assertIn(".ov-macro-reading-flow", css)
        self.assertIn(".ov-macro-reading-section", css)
        self.assertIn(".ov-macro-reading-section .ov-macro-section-title", css)
        self.assertIn(".ov-macro-reading-section .ov-macro-brief-value", css)
        self.assertIn(".ov-macro-reading-section .ov-macro-brief-detail", css)
        self.assertIn(".ov-macro-cockpit-narrative", css)
        self.assertIn(".ov-macro-reading-section .ov-macro-cue-value", css)
        self.assertIn(".ov-macro-reading-section .ov-source-confidence-title", css)
        self.assertIn(".ov-historical-analog-row.is-muted-reference", css)
        self.assertIn(".ov-analog-explain", css)
        self.assertIn(".ov-analog-summary-strip", css)
        self.assertIn(".ov-analog-interpretation", css)
        self.assertIn(".ov-historical-analog-table-block", css)
        self.assertIn(".ov-source-confidence.is-evidence-footer", css)
        self.assertNotIn(".ov-brief-confidence", css)
        self.assertNotIn(".ov-brief-confidence-row", css)

        analog_section_block = css[css.index(".ov-historical-analog-row {") : css.index(".ov-historical-analog-head {")]
        self.assertNotIn("background: transparent", analog_section_block)

    def test_overview_market_session_banner_uses_surface_text_color(self) -> None:
        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()
        title_block = css[css.index(".ov-market-session-title {"):css.index(".ov-market-session-detail {")]
        value_block = css[css.index(".ov-market-session-value {"):css.index(".ov-market-session-item-detail {")]

        self.assertIn("color: var(--ov-mi-color-text);", title_block)
        self.assertIn("color: var(--ov-mi-color-text);", value_block)
        self.assertNotIn("color: inherit;", title_block)
        self.assertNotIn("color: inherit;", value_block)

    def test_overview_market_context_copy_uses_korean_summary_first_language(self) -> None:
        import inspect

        from app.web.overview import market_context, market_context_helpers
        from app.web import overview_ui_components

        dashboard_source = "\n".join(
            [
                inspect.getsource(market_context),
                inspect.getsource(market_context_helpers),
            ]
        )
        component_source = "\n".join(
            [
                inspect.getsource(overview_ui_components.render_macro_context_cockpit),
                inspect.getsource(overview_ui_components._macro_context_cockpit_html),
                inspect.getsource(overview_ui_components._macro_cockpit_brief_rows_html),
                inspect.getsource(overview_ui_components._macro_cockpit_next_checks_html),
                inspect.getsource(overview_ui_components._macro_cockpit_interpretation_cues_html),
                inspect.getsource(overview_ui_components._macro_cockpit_row_meta_html),
                inspect.getsource(overview_ui_components._macro_cockpit_source_confidence_html),
            ]
        )

        self.assertIn("시장 맥락", dashboard_source)
        self.assertIn("저장된 시장 자료로 현재 세션의 움직임, 확산, 이벤트 배경을 빠르게 확인합니다.", dashboard_source)
        self.assertIn("필요 자료 보강", dashboard_source)
        self.assertNotIn("보조 갱신", dashboard_source)
        self.assertIn("오늘의 시장 맥락", component_source)
        self.assertIn("시장 브리프", component_source)
        self.assertNotIn("브리프 신뢰도", component_source)
        self.assertNotIn("맥락 검토 결과", component_source)
        self.assertIn("자료 영역", component_source)
        self.assertNotIn("핵심 요약", component_source)
        self.assertNotIn("해석 전 확인", component_source)
        self.assertNotIn("해석할 때 같이 볼 변수", component_source)
        self.assertNotIn("다음 확인 순서", component_source)
        self.assertNotIn("확인 위치", component_source)
        self.assertNotIn("Overview Macro Context", component_source)
        self.assertNotIn("다음에 볼 Deep Tab", component_source)
        self.assertNotIn("Source Confidence / 출처 신뢰도", component_source)
        self.assertNotIn("Freshness: ", component_source)

    def test_overview_ui_css_defines_ia_closeout_guide(self) -> None:
        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()

        self.assertIn(".ov-ia-closeout", css)
        self.assertIn(".ov-ia-closeout-card", css)

    def test_overview_ia_closeout_model_demotes_ops_surfaces_from_primary_tabs(self) -> None:
        from app.web.overview_dashboard_helpers import load_overview_ia_closeout_model

        model = load_overview_ia_closeout_model()

        self.assertEqual(model["schema_version"], "overview_ia_closeout_v1")
        self.assertEqual(model["title"], "Deep Tab 읽는 순서")
        self.assertIn("cockpit", model["detail"])
        self.assertIn("먼저", model["detail"])
        self.assertEqual([section["id"] for section in model["sections"]], ["market_context", "data_repair"])
        market_section = model["sections"][0]
        data_section = model["sections"][1]
        self.assertEqual(market_section["tabs"], ["Market Movers", "Sentiment", "Events"])
        self.assertNotIn("Futures Monitor", market_section["tabs"])
        self.assertNotIn("Sector / Industry", market_section["tabs"])
        self.assertNotIn("Data Health", market_section["tabs"])
        self.assertEqual(data_section["status"], "EXTERNAL")
        self.assertIn("Operations > System / Data Health", data_section["owner"])
        self.assertEqual(data_section["tabs"], [])
        self.assertIn("Overview 최상위 탭", data_section["detail"])
        self.assertNotIn("Candidate Ops", str(model))
        self.assertIn("context-only", model["boundary_note"])
        self.assertIn("생성하지 않습니다", model["boundary_note"])

    def test_overview_cockpit_shell_uses_surface_background_for_dark_theme_readability(self) -> None:
        from app.web.overview_ui_components import overview_ui_css

        css = overview_ui_css()
        cockpit_block = css[css.index(".ov-macro-cockpit {"):css.index(".ov-macro-cockpit-head {")]

        self.assertIn("var(--ov-mi-color-surface)", cockpit_block)
        self.assertNotIn("transparent), rgba(255,255,255,0.97)", cockpit_block)

    def test_overview_action_facade_wraps_intraday_refresh_defaults(self) -> None:
        from app.jobs import overview_actions

        with patch.object(
            overview_actions,
            "run_collect_market_intraday_snapshot",
            return_value={"job_name": "collect_top1000_intraday_snapshot", "status": "success"},
        ) as collect:
            result = overview_actions.run_overview_market_intraday_snapshot(
                universe_code="TOP1000",
                universe_limit=1000,
            )

        self.assertEqual(result["job_name"], "collect_top1000_intraday_snapshot")
        collect.assert_called_once_with(
            universe_code="TOP1000",
            universe_limit=1000,
            interval="5m",
            chunk_size=100,
            quote_batch_size=200,
            method="quote_fast",
            fallback_to_yfinance=False,
        )

    def test_overview_market_movers_refresh_action_collects_eod_history_through_ohlcv_job(self) -> None:
        from app.jobs import overview_actions

        action = getattr(overview_actions, "run_overview_market_movers_eod_history", None)
        if not callable(action):
            self.fail("Overview action facade should expose run_overview_market_movers_eod_history.")

        with (
            patch.object(
                overview_actions,
                "load_market_universe_members",
                return_value=[{"symbol": "AAA"}, {"symbol": "BBB"}, {"symbol": "AAA"}],
            ) as load_universe,
            patch.object(
                overview_actions,
                "run_collect_ohlcv",
                return_value={
                    "job_name": "collect_ohlcv",
                    "status": "success",
                    "rows_written": 1512,
                    "message": "OHLCV collection completed.",
                },
            ) as collect,
        ):
            result = action(
                universe_code="SP500",
                universe_limit=500,
                period="yearly",
            )

        self.assertEqual(result["job_name"], "overview_market_movers_eod_history")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["details"]["target_tables"], ["finance_price.nyse_price_history"])
        self.assertEqual(result["details"]["market_mover_period"], "yearly")
        self.assertEqual(result["details"]["collection_period"], "3y")
        self.assertEqual(result["details"]["symbols_requested"], 2)
        load_universe.assert_called_once_with("SP500")
        collect.assert_called_once_with(
            ["AAA", "BBB"],
            period="3y",
            interval="1d",
            execution_profile="managed_safe",
        )

    def test_overview_market_movers_refresh_action_uses_large_universe_loader_for_top1000(self) -> None:
        from app.jobs import overview_actions

        action = getattr(overview_actions, "run_overview_market_movers_eod_history", None)
        if not callable(action):
            self.fail("Overview action facade should expose run_overview_market_movers_eod_history.")

        with (
            patch.object(
                overview_actions,
                "load_market_cap_universe_members",
                return_value=[{"symbol": "AAA"}, {"symbol": "CCC"}],
            ) as load_universe,
            patch.object(
                overview_actions,
                "run_collect_ohlcv",
                return_value={"job_name": "collect_ohlcv", "status": "success", "rows_written": 504},
            ) as collect,
        ):
            result = action(
                universe_code="TOP1000",
                universe_limit=1000,
                period="monthly",
            )

        self.assertEqual(result["details"]["collection_period"], "1y")
        self.assertEqual(result["details"]["coverage_basis"], "Latest asset_profile.market_cap snapshot")
        load_universe.assert_called_once_with("TOP1000", universe_limit=1000)
        collect.assert_called_once_with(
            ["AAA", "CCC"],
            period="1y",
            interval="1d",
            execution_profile="managed_safe",
        )

    def test_overview_market_movers_refresh_action_uses_nasdaq_directory_loader(self) -> None:
        from app.jobs import overview_actions

        with (
            patch.object(
                overview_actions,
                "load_nasdaq_symbol_directory_universe_members",
                return_value=[{"symbol": "AAPL"}, {"symbol": "MSFT"}, {"symbol": "AAPL"}],
            ) as load_universe,
            patch.object(
                overview_actions,
                "run_collect_ohlcv",
                return_value={"job_name": "collect_ohlcv", "status": "success", "rows_written": 756},
            ) as collect,
        ):
            result = overview_actions.run_overview_market_movers_eod_history(
                universe_code="NASDAQ",
                universe_limit=5000,
                period="weekly",
            )

        self.assertEqual(result["details"]["coverage_basis"], "Nasdaq-listed current snapshot")
        self.assertEqual(result["details"]["source"], "yfinance OHLCV")
        load_universe.assert_called_once_with()
        collect.assert_called_once_with(
            ["AAPL", "MSFT"],
            period="3mo",
            interval="1d",
            execution_profile="managed_safe",
        )

    def test_overview_automation_standard_plan_includes_symbol_directory_refresh(self) -> None:
        from app.jobs.overview_automation import build_overview_automation_plan

        plan = build_overview_automation_plan(
            profile="standard",
            history_rows=[],
            now=datetime(2026, 6, 17, 15, 0, tzinfo=timezone.utc),
            allow_outside_market_hours=True,
        )
        job_ids = [row["job_id"] for row in plan]

        self.assertIn("nasdaq_symbol_directory", job_ids)
        self.assertIn("nasdaq_intraday", job_ids)
        directory_row = next(row for row in plan if row["job_id"] == "nasdaq_symbol_directory")
        intraday_row = next(row for row in plan if row["job_id"] == "nasdaq_intraday")
        self.assertFalse(directory_row["market_hours_only"])
        self.assertEqual(directory_row["cadence_minutes"], 24 * 60)
        self.assertEqual(intraday_row["cadence_minutes"], 30)
        self.assertTrue(intraday_row["market_hours_only"])

    def test_overview_market_movers_refresh_bar_renders_eod_action_for_non_daily_without_auto_mode(self) -> None:
        source = Path("app/web/overview/market_movers_helpers.py").read_text(encoding="utf-8")

        self.assertIn("run_overview_market_movers_eod_history", source)
        self.assertIn("def _render_market_movers_daily_refresh_bar", source)
        self.assertIn("def _render_market_movers_eod_refresh_bar", source)
        self.assertIn("run_overview_market_movers_eod_history,", source)

        dispatch_body = source[source.index("def _render_market_movers_refresh_bar") :]
        dispatch_body = dispatch_body[: dispatch_body.index("def _rank_token")]
        self.assertIn("_render_market_movers_daily_refresh_bar", dispatch_body)
        self.assertIn("_render_market_movers_eod_refresh_bar", dispatch_body)

        eod_body = source[source.index("def _render_market_movers_eod_refresh_bar") :]
        eod_body = eod_body[: eod_body.index("def _render_market_movers_refresh_bar")]
        self.assertIn("가격 이력 갱신", eod_body)
        self.assertIn("run_overview_market_movers_eod_history(", eod_body)
        self.assertNotIn("_select_market_refresh_mode", eod_body)
        self.assertNotIn("_render_market_auto_refresh_summary", eod_body)

    def test_market_movers_empty_snapshot_replaces_stale_why_it_moved_panel(self) -> None:
        source = Path("app/web/overview/market_movers_helpers.py").read_text(encoding="utf-8")

        self.assertIn("Market mover rows are needed before Why It Moved can be shown.", source)
        self.assertIn("선택한 coverage에 ranking row가 생기면 조사 패널을 사용할 수 있습니다.", source)

    def test_overview_action_facade_runs_market_context_refresh_bundle(self) -> None:
        from app.jobs import overview_actions

        calls: list[str] = []

        def _result(job_name: str, status: str = "success") -> dict[str, Any]:
            calls.append(job_name)
            return {"job_name": job_name, "status": status, "message": f"{job_name} done"}

        with (
            patch.object(
                overview_actions,
                "run_overview_market_intraday_snapshot",
                side_effect=lambda **_: _result("market_intraday"),
            ) as market_snapshot,
            patch.object(
                overview_actions,
                "run_overview_futures_ohlcv",
                side_effect=lambda **_: _result("futures_1m"),
            ) as futures_1m,
            patch.object(
                overview_actions,
                "run_overview_futures_daily_ohlcv",
                side_effect=lambda: _result("futures_daily"),
            ) as futures_daily,
            patch.object(
                overview_actions,
                "run_overview_market_sentiment",
                side_effect=lambda: _result("market_sentiment"),
            ) as sentiment,
            patch.object(
                overview_actions,
                "run_overview_fomc_calendar",
                side_effect=lambda **_: _result("fomc_calendar"),
            ) as fomc,
            patch.object(
                overview_actions,
                "run_overview_earnings_calendar",
                side_effect=lambda: _result("earnings_calendar", status="partial_success"),
            ) as earnings,
            patch.object(
                overview_actions,
                "run_overview_macro_calendar",
                side_effect=lambda **_: _result("macro_calendar"),
            ) as macro,
        ):
            summary = overview_actions.run_overview_market_context_refresh_all(
                years=(2026, 2027),
                futures_symbols=("ES=F", "NQ=F"),
            )

        self.assertEqual(summary["job_name"], "overview_market_context_refresh_all")
        self.assertEqual(summary["status"], "partial_success")
        self.assertEqual(summary["jobs_run"], 5)
        self.assertEqual(summary["jobs_failed"], 0)
        self.assertEqual(
            calls,
            [
                "market_intraday",
                "market_sentiment",
                "fomc_calendar",
                "earnings_calendar",
                "macro_calendar",
            ],
        )
        market_snapshot.assert_called_once_with(universe_code="SP500", universe_limit=500)
        futures_1m.assert_not_called()
        futures_daily.assert_not_called()
        sentiment.assert_called_once_with()
        fomc.assert_called_once_with(years=(2026, 2027))
        earnings.assert_called_once_with()
        macro.assert_called_once_with(years=(2026, 2027))

    def test_overview_action_facade_runs_smart_market_context_refresh_actions_only(self) -> None:
        from app.jobs import overview_actions

        calls: list[str] = []

        def _result(job_name: str, status: str = "success") -> dict[str, Any]:
            calls.append(job_name)
            return {"job_name": job_name, "status": status, "message": f"{job_name} done"}

        with (
            patch.object(
                overview_actions,
                "run_overview_market_intraday_snapshot",
                side_effect=lambda **_: _result("market_intraday"),
            ) as market_snapshot,
            patch.object(
                overview_actions,
                "run_overview_futures_ohlcv",
                side_effect=lambda **_: _result("futures_1m"),
            ) as futures_1m,
            patch.object(
                overview_actions,
                "run_overview_futures_daily_ohlcv",
                side_effect=lambda: _result("futures_daily"),
            ) as futures_daily,
            patch.object(
                overview_actions,
                "run_overview_market_sentiment",
                side_effect=lambda: _result("market_sentiment"),
            ) as sentiment,
            patch.object(
                overview_actions,
                "run_overview_fomc_calendar",
                side_effect=lambda **_: _result("fomc_calendar"),
            ) as fomc,
            patch.object(
                overview_actions,
                "run_overview_earnings_calendar",
                side_effect=lambda: _result("earnings_calendar", status="partial_success"),
            ) as earnings,
            patch.object(
                overview_actions,
                "run_overview_macro_calendar",
                side_effect=lambda **_: _result("macro_calendar"),
            ) as macro,
        ):
            summary = overview_actions.run_overview_market_context_refresh_smart(
                action_ids=(
                    "top1000_intraday_snapshot",
                    "top2000_intraday_snapshot",
                    "futures_1m",
                    "futures_daily",
                    "earnings_calendar",
                ),
                years=(2026, 2027),
                futures_symbols=("ES=F", "NQ=F"),
            )

        self.assertEqual(summary["job_name"], "overview_market_context_refresh_smart")
        self.assertEqual(summary["status"], "partial_success")
        self.assertEqual(summary["jobs_run"], 1)
        self.assertEqual(summary["jobs_failed"], 0)
        self.assertEqual(calls, ["earnings_calendar"])
        market_snapshot.assert_not_called()
        futures_1m.assert_not_called()
        futures_daily.assert_not_called()
        sentiment.assert_not_called()
        fomc.assert_not_called()
        earnings.assert_called_once_with()
        macro.assert_not_called()

    def test_overview_market_context_refresh_bar_prefers_smart_refresh_and_keeps_full_fallback(self) -> None:
        source = Path("app/web/overview/market_context_helpers.py").read_text(encoding="utf-8")

        self.assertIn("run_overview_market_context_refresh_smart", source)
        self.assertIn("_render_overview_market_context_smart_refresh_plan", source)
        self.assertIn('summary = dict(refresh_plan.get("summary") or {})', source)
        self.assertIn("현재 이슈만 보강", source)
        self.assertIn("전체 Market Context 자료 보강", source)
        self.assertIn("overview_market_context_refresh_smart", source)
        self.assertIn("overview_market_context_refresh_all", source)

    def test_overview_action_facade_collects_historical_analog_price_gaps_with_existing_ohlcv_job(self) -> None:
        from app.jobs import overview_actions

        with patch.object(
            overview_actions,
            "run_collect_ohlcv",
            return_value={
                "job_name": "collect_ohlcv",
                "status": "success",
                "rows_written": 2520,
                "message": "OHLCV collection completed.",
            },
        ) as collect:
            result = overview_actions.run_overview_historical_analog_ohlcv(
                symbols=["XLK", "SPY", "XLK"],
            )

        self.assertEqual(result["job_name"], "overview_historical_analog_ohlcv")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["details"]["target_tables"], ["finance_price.nyse_price_history"])
        self.assertEqual(result["details"]["symbols"], ["XLK", "SPY"])
        collect.assert_called_once_with(
            ["XLK", "SPY"],
            period="10y",
            interval="1d",
            execution_profile="managed_safe",
        )

    def test_group_trend_heatmap_expands_for_many_selected_groups(self) -> None:
        from app.web.overview_dashboard import (
            GROUP_TREND_HEATMAP_ROW_HEIGHT,
            _build_group_leadership_trend_heatmap,
        )

        rows = pd.DataFrame(
            [
                {
                    "Date": "2026-05-27",
                    "Group": f"Sector {index}",
                    "Market Cap Weighted Return %": float(index),
                    "Symbols": 10,
                    "Top Symbol": "AAA",
                }
                for index in range(11)
            ]
        )

        chart_spec = _build_group_leadership_trend_heatmap(rows).to_dict()

        self.assertGreaterEqual(chart_spec["height"], GROUP_TREND_HEATMAP_ROW_HEIGHT * 11)

    def test_run_history_append_serializes_provider_date_payload(self) -> None:
        from app.jobs import run_history

        with tempfile.TemporaryDirectory() as tmp_dir:
            history_file = Path(tmp_dir) / "WEB_APP_RUN_HISTORY.jsonl"
            with patch.object(run_history, "HISTORY_FILE", history_file):
                run_history.append_run_history(
                    {
                        "job_name": "collect_earnings_calendar",
                        "status": "success",
                        "started_at": "2026-05-29 10:00:00",
                        "finished_at": "2026-05-29 10:00:02",
                        "duration_sec": 2.0,
                        "rows_written": 1,
                        "symbols_requested": 1,
                        "symbols_processed": 1,
                        "failed_symbols": [],
                        "message": "earnings calendar completed",
                        "details": {
                            "symbol_diagnostics": [
                                {
                                    "symbol": "AAA",
                                    "provider_dates": [date(2026, 7, 30)],
                                }
                            ]
                        },
                    }
                )
                loaded = run_history.load_run_history(limit=1)

        self.assertEqual(
            loaded[0]["details"]["symbol_diagnostics"][0]["provider_dates"],
            ["2026-07-30"],
        )

    def test_browser_safe_profile_only_selects_sp500_intraday_snapshot(self) -> None:
        from app.jobs.overview_automation import VALID_PROFILES, build_overview_automation_plan

        self.assertIn("browser_safe", VALID_PROFILES)

        plan = build_overview_automation_plan(
            profile="browser_safe",
            history_rows=[],
            now=datetime(2026, 5, 29, 15, 0, tzinfo=timezone.utc),
        )

        self.assertEqual([row["job_id"] for row in plan], ["sp500_intraday"])
        self.assertTrue(plan[0]["should_run"])
        self.assertEqual(plan[0]["cadence_minutes"], 5)
        self.assertTrue(plan[0]["market_hours_only"])

    def test_intraday_plan_skips_outside_market_hours_unless_allowed(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, build_overview_automation_plan

        spec = ScheduledJobSpec(
            job_id="fake_intraday",
            job_name="fake_intraday_job",
            label="Fake Intraday",
            cadence_minutes=5,
            profiles=("test",),
            market_hours_only=True,
            runner=lambda _: {},
            description="fake provider run",
        )
        outside_market_hours = datetime(2026, 5, 29, 23, 0, tzinfo=timezone.utc)

        plan = build_overview_automation_plan(
            profile="test",
            history_rows=[],
            now=outside_market_hours,
            specs=(spec,),
        )
        self.assertFalse(plan[0]["should_run"])
        self.assertEqual(plan[0]["reason"], "outside US market hours")

        allowed_plan = build_overview_automation_plan(
            profile="test",
            history_rows=[],
            now=outside_market_hours,
            allow_outside_market_hours=True,
            specs=(spec,),
        )
        self.assertTrue(allowed_plan[0]["should_run"])
        self.assertEqual(allowed_plan[0]["reason"], "due")

    def test_plan_uses_cadence_from_latest_accepted_history(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, build_overview_automation_plan

        spec = ScheduledJobSpec(
            job_id="fake_calendar",
            job_name="fake_calendar_job",
            label="Fake Calendar",
            cadence_minutes=60,
            profiles=("test",),
            market_hours_only=False,
            runner=lambda _: {},
            description="fake calendar run",
        )
        history_rows = [
            {
                "job_name": "fake_calendar_job",
                "status": "success",
                "finished_at": "2026-05-29 10:00:00",
            }
        ]

        early_plan = build_overview_automation_plan(
            profile="test",
            history_rows=history_rows,
            now=datetime(2026, 5, 29, 10, 30),
            specs=(spec,),
        )
        self.assertFalse(early_plan[0]["should_run"])
        self.assertEqual(early_plan[0]["reason"], "cadence not due")

        due_plan = build_overview_automation_plan(
            profile="test",
            history_rows=history_rows,
            now=datetime(2026, 5, 29, 11, 1),
            specs=(spec,),
        )
        self.assertTrue(due_plan[0]["should_run"])
        self.assertEqual(due_plan[0]["reason"], "due")

    def test_run_appends_scheduled_metadata_and_releases_lock(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, run_overview_automation

        calls: list[datetime] = []

        def fake_runner(value: datetime) -> dict:
            calls.append(value)
            return {
                "job_name": "fake_calendar_job",
                "status": "success",
                "started_at": "2026-05-29 10:00:00",
                "finished_at": "2026-05-29 10:00:01",
                "duration_sec": 1.0,
                "rows_written": 3,
                "symbols_requested": None,
                "symbols_processed": None,
                "failed_symbols": [],
                "message": "fake completed",
                "details": {"source": "fake"},
            }

        spec = ScheduledJobSpec(
            job_id="fake_calendar",
            job_name="fake_calendar_job",
            label="Fake Calendar",
            cadence_minutes=60,
            profiles=("test",),
            market_hours_only=False,
            runner=fake_runner,
            description="fake calendar run",
        )
        appended: list[dict] = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            lock_path = Path(tmp_dir) / "overview.lock"
            summary = run_overview_automation(
                profile="test",
                history_rows=[],
                history_appender=appended.append,
                lock_path=lock_path,
                now=datetime(2026, 5, 29, 10, 0),
                specs=(spec,),
            )
            self.assertFalse(lock_path.exists())

        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["jobs_run"], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(appended), 1)
        metadata = appended[0]["run_metadata"]
        self.assertEqual(metadata["execution_mode"], "scheduled")
        self.assertEqual(metadata["automation_profile"], "test")
        self.assertEqual(metadata["automation_job_id"], "fake_calendar")
        self.assertEqual(appended[0]["details"]["automation"]["profile"], "test")
        self.assertEqual(appended[0]["details"]["automation"]["execution_mode"], "scheduled")

    def test_run_can_append_browser_auto_metadata(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, run_overview_automation

        def fake_runner(_: datetime) -> dict:
            return {
                "job_name": "fake_intraday_job",
                "status": "success",
                "started_at": "2026-05-29 10:00:00",
                "finished_at": "2026-05-29 10:00:02",
                "duration_sec": 2.0,
                "rows_written": 503,
                "symbols_requested": 503,
                "symbols_processed": 503,
                "failed_symbols": [],
                "message": "fake intraday completed",
                "details": {},
            }

        spec = ScheduledJobSpec(
            job_id="fake_intraday",
            job_name="fake_intraday_job",
            label="Fake Intraday",
            cadence_minutes=5,
            profiles=("browser_safe",),
            market_hours_only=False,
            runner=fake_runner,
            description="fake browser auto run",
        )
        appended: list[dict] = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            summary = run_overview_automation(
                profile="browser_safe",
                execution_mode="browser_auto",
                history_rows=[],
                history_appender=appended.append,
                lock_path=Path(tmp_dir) / "overview.lock",
                now=datetime(2026, 5, 29, 10, 0),
                specs=(spec,),
            )

        self.assertEqual(summary["execution_mode"], "browser_auto")
        self.assertEqual(appended[0]["run_metadata"]["execution_mode"], "browser_auto")
        self.assertIn("Browser-session Overview automation", appended[0]["run_metadata"]["execution_context"])
        self.assertEqual(appended[0]["details"]["automation"]["execution_mode"], "browser_auto")

    def test_dry_run_does_not_call_runner_or_append_history(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, run_overview_automation

        def fake_runner(_: datetime) -> dict:
            raise AssertionError("dry-run should not execute the runner")

        spec = ScheduledJobSpec(
            job_id="fake_calendar",
            job_name="fake_calendar_job",
            label="Fake Calendar",
            cadence_minutes=60,
            profiles=("test",),
            market_hours_only=False,
            runner=fake_runner,
            description="fake calendar run",
        )
        appended: list[dict] = []

        summary = run_overview_automation(
            profile="test",
            dry_run=True,
            history_rows=[],
            history_appender=appended.append,
            now=datetime(2026, 5, 29, 10, 0),
            specs=(spec,),
        )

        self.assertEqual(summary["status"], "dry_run")
        self.assertEqual(summary["jobs_due"], 1)
        self.assertEqual(summary["jobs_run"], 0)
        self.assertEqual(appended, [])


class BacktestRuntimeContractTests(unittest.TestCase):
    def test_gtaa_strategy_records_liquidity_exclusions_when_adv_filter_is_enabled(self) -> None:
        from finance.strategy import gtaa3

        dates = pd.to_datetime(["2024-01-31", "2024-02-29"])
        dfs = {
            "AAA": pd.DataFrame(
                {
                    "Date": dates,
                    "Close": [100.0, 101.0],
                    "MA200": [90.0, 90.0],
                    "Avg Score": [5.0, 5.0],
                }
            ),
            "BBB": pd.DataFrame(
                {
                    "Date": dates,
                    "Close": [100.0, 102.0],
                    "MA200": [90.0, 90.0],
                    "Avg Score": [1.0, 1.0],
                }
            ),
        }

        result = gtaa3(
            dfs,
            start_balance=10_000,
            top=1,
            filter_ma="MA200",
            min_avg_dollar_volume_20d_m=5.0,
            avg_dollar_volume_20d_by_date={
                "AAA": {pd.Timestamp("2024-01-31"): 1_000_000.0, pd.Timestamp("2024-02-29"): 1_000_000.0},
                "BBB": {pd.Timestamp("2024-01-31"): 10_000_000.0, pd.Timestamp("2024-02-29"): 10_000_000.0},
            },
        )

        self.assertIn("Liquidity Excluded Count", result.columns)
        self.assertEqual(result.loc[0, "Liquidity Excluded Ticker"], ["AAA"])
        self.assertEqual(int(result.loc[0, "Liquidity Excluded Count"]), 1)
        self.assertEqual(result.loc[0, "Raw Selected Ticker"], ["BBB"])

    def test_gtaa_execution_dispatch_passes_min_adv_filter_to_runtime(self) -> None:
        from app.services.backtest_execution import execute_single_backtest

        payload = {
            "strategy_key": "gtaa",
            "tickers": ["QQQ", "SOXX", "MTUM", "QUAL", "USMV", "IAU", "IEF", "TLT"],
            "start": "2016-01-01",
            "end": "2026-05-01",
            "timeframe": "1d",
            "option": "month_end",
            "top": 3,
            "interval": 3,
            "score_lookback_months": [1, 6],
            "trend_filter_window": 250,
            "risk_off_mode": "cash_only",
            "defensive_tickers": ["IEF", "TLT"],
            "min_price_filter": 5.0,
            "min_avg_dollar_volume_20d_m_filter": 20.0,
            "transaction_cost_bps": 10.0,
            "benchmark_ticker": "SPY",
            "universe_mode": "preset",
            "preset_name": "GTAA SPY Low-MDD Style Top-3",
        }

        with patch(
            "app.services.backtest_execution.run_gtaa_backtest_from_db",
            return_value={"strategy_name": "GTAA", "meta": {}},
        ) as runner:
            result = execute_single_backtest(payload, strategy_name="GTAA")

        self.assertTrue(result.ok, result.error_message)
        self.assertEqual(runner.call_args.kwargs["min_avg_dollar_volume_20d_m_filter"], 20.0)

    def test_execution_preview_ignores_later_stage_probation_monitoring_fields(self) -> None:
        from app.runtime.backtest import _build_deployment_readiness_contract

        preview = _build_deployment_readiness_contract(
            {
                "benchmark_available": True,
                "benchmark_contract": "spy",
                "benchmark_label": "SPY Benchmark",
                "universe_contract": "historical_dynamic_pit",
                "price_freshness": {"status": "ok"},
                "benchmark_policy_status": "normal",
                "liquidity_policy_status": "normal",
                "validation_policy_status": "normal",
                "guardrail_policy_status": "normal",
                "etf_operability_status": "normal",
                "rolling_review_status": "normal",
                "out_of_sample_review_status": "normal",
                # Legacy later-stage fields can remain in metadata, but Execution Preview must not score them.
                "shortlist_status": "hold",
                "probation_status": "not_ready",
                "monitoring_status": "blocked",
            }
        )

        check_names = {row["Check"] for row in preview["deployment_checklist_rows"]}
        self.assertNotIn("Shortlist", check_names)
        self.assertNotIn("Probation", check_names)
        self.assertNotIn("Monitoring", check_names)
        self.assertEqual(preview["deployment_readiness_status"], "small_capital_ready")
        self.assertEqual(preview["deployment_check_fail_count"], 0)

    def test_candidate_readiness_scores_source_checks_not_legacy_deployment_status(self) -> None:
        from app.web.backtest_result_display import _build_next_step_readiness_evaluation

        evaluation = _build_next_step_readiness_evaluation(
            {
                "promotion_decision": "real_money_candidate",
                "deployment_readiness_status": "blocked",
                "benchmark_available": True,
                "validation_status": "normal",
                "benchmark_policy_status": "normal",
                "liquidity_policy_status": "normal",
                "validation_policy_status": "normal",
                "guardrail_policy_status": "normal",
                "etf_operability_status": "normal",
                "price_freshness": {"status": "ok"},
                "rolling_review_status": "caution",
                "out_of_sample_review_status": "caution",
                "transaction_cost_bps": 10.0,
                "turnover_estimation_status": "not_estimated_missing_holdings",
                "net_cost_curve_status": "applied_without_turnover_estimate",
            }
        )

        self.assertTrue(evaluation["can_move_to_compare"])
        self.assertEqual(evaluation["blocking_reasons"], [])
        self.assertEqual(evaluation["score"], 8.0)
        self.assertIn("Rolling Review: caution", evaluation["review_reasons"])
        self.assertIn("Split-Period Check: caution", evaluation["review_reasons"])
        self.assertIn("Turnover Estimate: not_estimated_missing_holdings", evaluation["review_reasons"])
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Execution Source Checks"]["현재 값"], "block 0 / review 2")
        self.assertEqual(criteria["Validation Source Checks"]["현재 값"], "block 0 / review 2")

    def test_practical_validation_handoff_gate_blocks_hold_candidates(self) -> None:
        from app.web.backtest_result_display import _build_practical_validation_handoff_state

        state = _build_practical_validation_handoff_state(
            {
                "meta": {
                    "promotion_decision": "hold",
                    "benchmark_available": True,
                    "validation_status": "normal",
                    "benchmark_policy_status": "normal",
                    "liquidity_policy_status": "normal",
                    "validation_policy_status": "normal",
                    "guardrail_policy_status": "normal",
                    "etf_operability_status": "normal",
                    "price_freshness": {"status": "ok"},
                }
            }
        )

        self.assertFalse(state["can_submit"])
        self.assertEqual(state["status_label"], "진입 보류")
        self.assertIn("Promotion Decision이 hold이거나 비어 있음", state["display_reasons"])
        criteria = {row["label"]: row for row in state["criteria"]}
        self.assertEqual(criteria["Promotion"]["value"], "보류")

    def test_practical_validation_handoff_gate_allows_ready_candidates(self) -> None:
        from app.web.backtest_result_display import _build_practical_validation_handoff_state

        state = _build_practical_validation_handoff_state(
            {
                "meta": {
                    "promotion_decision": "real_money_candidate",
                    "benchmark_available": True,
                    "validation_status": "normal",
                    "benchmark_policy_status": "normal",
                    "liquidity_policy_status": "normal",
                    "validation_policy_status": "normal",
                    "guardrail_policy_status": "normal",
                    "etf_operability_status": "normal",
                    "price_freshness": {"status": "ok"},
                }
            }
        )

        self.assertTrue(state["can_submit"])
        self.assertEqual(state["status_label"], "진입 가능")
        self.assertEqual(state["display_reasons"], ["막는 항목 없음"])
        criteria = {row["label"]: row for row in state["criteria"]}
        self.assertEqual(criteria["실행 원천"]["value"], "통과")
        self.assertEqual(criteria["검증 원천"]["value"], "통과")

    def test_portfolio_mix_candidate_gate_allows_ready_mix(self) -> None:
        from app.web.backtest_compare import _build_weighted_mix_candidate_readiness_evaluation

        def _bundle(strategy_name: str) -> dict:
            return {
                "strategy_name": strategy_name,
                "summary_df": pd.DataFrame([{"End Balance": 110.0}]),
                "result_df": pd.DataFrame(
                    [
                        {"Date": "2024-12-31", "Total Balance": 100.0},
                        {"Date": "2025-12-31", "Total Balance": 110.0},
                    ]
                ),
                "meta": {
                    "strategy_name": strategy_name,
                    "end": "2025-12-31",
                    "promotion_decision": "real_money_candidate",
                    "benchmark_available": True,
                    "validation_status": "normal",
                    "benchmark_policy_status": "normal",
                    "liquidity_policy_status": "normal",
                    "validation_policy_status": "normal",
                    "guardrail_policy_status": "normal",
                    "etf_operability_status": "normal",
                    "price_freshness": {"status": "ok"},
                },
            }

        weighted_bundle = {
            "summary_df": pd.DataFrame([{"End Balance": 112.0}]),
            "result_df": pd.DataFrame(
                [
                    {"Date": "2024-12-31", "Total Balance": 100.0},
                    {"Date": "2025-12-31", "Total Balance": 112.0},
                ]
            ),
            "component_strategy_names": ["GTAA", "Equal Weight"],
            "component_input_weights": [70.0, 30.0],
            "component_data_trust_rows": [
                {"Strategy": "GTAA", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
                {"Strategy": "Equal Weight", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
            ],
            "date_policy": "intersection",
        }

        evaluation = _build_weighted_mix_candidate_readiness_evaluation(
            weighted_bundle,
            [_bundle("GTAA"), _bundle("Equal Weight")],
        )

        self.assertTrue(evaluation["can_send_to_practical_validation"])
        self.assertEqual(evaluation["stage_status"], "PASS")
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Weight Discipline"]["상태"], "PASS")
        self.assertEqual(criteria["Component 1차 후보 판단"]["상태"], "PASS")

    def test_portfolio_mix_candidate_gate_blocks_hold_component(self) -> None:
        from app.web.backtest_compare import _build_weighted_mix_candidate_readiness_evaluation

        ready_meta = {
            "end": "2025-12-31",
            "promotion_decision": "real_money_candidate",
            "benchmark_available": True,
            "validation_status": "normal",
            "benchmark_policy_status": "normal",
            "liquidity_policy_status": "normal",
            "validation_policy_status": "normal",
            "guardrail_policy_status": "normal",
            "etf_operability_status": "normal",
            "price_freshness": {"status": "ok"},
        }
        result_df = pd.DataFrame(
            [
                {"Date": "2024-12-31", "Total Balance": 100.0},
                {"Date": "2025-12-31", "Total Balance": 110.0},
            ]
        )
        bundles = [
            {"strategy_name": "GTAA", "summary_df": pd.DataFrame([{"End Balance": 110.0}]), "result_df": result_df, "meta": dict(ready_meta)},
            {
                "strategy_name": "Equal Weight",
                "summary_df": pd.DataFrame([{"End Balance": 108.0}]),
                "result_df": result_df,
                "meta": {**ready_meta, "promotion_decision": "hold"},
            },
        ]
        weighted_bundle = {
            "summary_df": pd.DataFrame([{"End Balance": 112.0}]),
            "result_df": result_df,
            "component_strategy_names": ["GTAA", "Equal Weight"],
            "component_input_weights": [50.0, 50.0],
            "component_data_trust_rows": [
                {"Strategy": "GTAA", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
                {"Strategy": "Equal Weight", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
            ],
            "date_policy": "intersection",
        }

        evaluation = _build_weighted_mix_candidate_readiness_evaluation(weighted_bundle, bundles)

        self.assertFalse(evaluation["can_send_to_practical_validation"])
        self.assertEqual(evaluation["stage_status"], "HOLD")
        self.assertTrue(any("Promotion Decision" in reason for reason in evaluation["blocking_reasons"]))
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Component 1차 후보 판단"]["상태"], "FAIL")

    def test_portfolio_mix_candidate_gate_blocks_non_100_weight_total(self) -> None:
        from app.web.backtest_compare import _build_weighted_mix_candidate_readiness_evaluation

        meta = {
            "end": "2025-12-31",
            "promotion_decision": "real_money_candidate",
            "benchmark_available": True,
            "validation_status": "normal",
            "benchmark_policy_status": "normal",
            "liquidity_policy_status": "normal",
            "validation_policy_status": "normal",
            "guardrail_policy_status": "normal",
            "etf_operability_status": "normal",
            "price_freshness": {"status": "ok"},
        }
        result_df = pd.DataFrame(
            [
                {"Date": "2024-12-31", "Total Balance": 100.0},
                {"Date": "2025-12-31", "Total Balance": 110.0},
            ]
        )
        bundles = [
            {"strategy_name": "GTAA", "summary_df": pd.DataFrame([{"End Balance": 110.0}]), "result_df": result_df, "meta": meta},
            {"strategy_name": "Equal Weight", "summary_df": pd.DataFrame([{"End Balance": 108.0}]), "result_df": result_df, "meta": meta},
        ]
        weighted_bundle = {
            "summary_df": pd.DataFrame([{"End Balance": 112.0}]),
            "result_df": result_df,
            "component_strategy_names": ["GTAA", "Equal Weight"],
            "component_input_weights": [70.0, 20.0],
            "component_data_trust_rows": [
                {"Strategy": "GTAA", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
                {"Strategy": "Equal Weight", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
            ],
            "date_policy": "intersection",
        }

        evaluation = _build_weighted_mix_candidate_readiness_evaluation(weighted_bundle, bundles)

        self.assertFalse(evaluation["can_send_to_practical_validation"])
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Weight Discipline"]["상태"], "FAIL")
        self.assertIn("target weight 합계가 100%가 아님", criteria["Weight Discipline"]["판단"])

    def test_result_bundle_public_compatibility_contract_is_preserved(self) -> None:
        import app.runtime
        from app.runtime import backtest as runtime_backtest
        from app.runtime.backtest import result_bundle

        self.assertIs(
            runtime_backtest.build_backtest_result_bundle,
            result_bundle.build_backtest_result_bundle,
        )
        self.assertIs(
            app.runtime.build_backtest_result_bundle,
            result_bundle.build_backtest_result_bundle,
        )

    def test_result_bundle_contract_sorts_dates_and_keeps_metadata(self) -> None:
        from app.runtime.backtest.result_bundle import build_backtest_result_bundle

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

    def test_dynamic_etf_execution_dispatch_adds_promotion_policy_defaults(self) -> None:
        from app.runtime.backtest import (
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )
        from app.services.backtest_execution import execute_single_backtest

        payload = {
            "strategy_key": "global_relative_strength",
            "tickers": ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"],
            "cash_ticker": "BIL",
            "start": "2016-01-29",
            "end": "2026-05-29",
            "timeframe": "1d",
            "option": "month_end",
            "top": 2,
            "interval": 1,
            "universe_mode": "manual_tickers",
            "preset_name": "GRS Liquid Macro Top2",
        }

        with patch(
            "app.services.backtest_execution.run_global_relative_strength_backtest_from_db",
            return_value={"strategy_name": "Global Relative Strength", "meta": {}},
        ) as runner:
            result = execute_single_backtest(payload, strategy_name="Global Relative Strength")

        self.assertTrue(result.ok, result.error_message)
        kwargs = runner.call_args.kwargs
        self.assertEqual(kwargs["promotion_min_benchmark_coverage"], STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE)
        self.assertEqual(kwargs["promotion_min_net_cagr_spread"], STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD)
        self.assertEqual(
            kwargs["promotion_min_liquidity_clean_coverage"],
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        )
        self.assertEqual(
            kwargs["promotion_max_underperformance_share"],
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        )
        self.assertEqual(
            kwargs["promotion_min_worst_rolling_excess_return"],
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )
        self.assertEqual(kwargs["promotion_max_strategy_drawdown"], STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN)
        self.assertEqual(
            kwargs["promotion_max_drawdown_gap_vs_benchmark"],
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        )

    def test_global_relative_strength_source_contract_includes_promotion_policy_defaults(self) -> None:
        from app.runtime import backtest as runtime_backtest
        from app.runtime.backtest.runners import global_relative_strength as grs_runtime
        from app.runtime.backtest import (
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )

        result_df = pd.DataFrame(
            [
                {"Date": "2020-01-31", "Total Balance": 100.0, "Total Return": 0.0},
                {"Date": "2020-02-29", "Total Balance": 103.0, "Total Return": 0.03},
                {"Date": "2020-03-31", "Total Balance": 107.0, "Total Return": 0.07},
            ]
        )
        result_df.attrs["effective_tickers"] = ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"]
        result_df.attrs["requested_tickers"] = ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"]
        captured_hardening_kwargs: dict[str, object] = {}

        def _capture_hardening(bundle: dict[str, object], **kwargs: object) -> dict[str, object]:
            captured_hardening_kwargs.update(kwargs)
            return bundle

        with (
            patch.object(
                grs_runtime,
                "inspect_strict_annual_price_freshness",
                return_value={"status": "ok", "message": "", "details": {}},
            ),
            patch.object(grs_runtime, "_preflight_price_strategy_data"),
            patch.object(grs_runtime, "get_global_relative_strength_from_db", return_value=result_df),
            patch.object(grs_runtime, "_apply_real_money_hardening", side_effect=_capture_hardening),
        ):
            bundle = runtime_backtest.run_global_relative_strength_backtest_from_db(
                tickers=["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"],
                cash_ticker="BIL",
                start="2020-01-31",
                end="2020-03-31",
                timeframe="1d",
                option="month_end",
                top=2,
                interval=1,
                benchmark_ticker="AOR",
                universe_mode="manual_tickers",
                preset_name="GRS Liquid Macro Top2",
            )

        meta = bundle["meta"]
        self.assertEqual(meta["promotion_min_benchmark_coverage"], STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE)
        self.assertEqual(meta["promotion_min_net_cagr_spread"], STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD)
        self.assertEqual(
            meta["promotion_min_liquidity_clean_coverage"],
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        )
        self.assertEqual(
            meta["promotion_max_underperformance_share"],
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        )
        self.assertEqual(
            meta["promotion_min_worst_rolling_excess_return"],
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )
        self.assertEqual(meta["promotion_max_strategy_drawdown"], STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN)
        self.assertEqual(
            meta["promotion_max_drawdown_gap_vs_benchmark"],
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        )
        self.assertEqual(
            captured_hardening_kwargs["promotion_min_net_cagr_spread"],
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        )

    def test_dynamic_etf_compare_override_preserves_promotion_policy_defaults(self) -> None:
        from app.runtime.backtest import STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD
        from app.web.backtest_compare import _bundle_to_saved_strategy_override

        override = _bundle_to_saved_strategy_override(
            {
                "strategy_name": "Global Relative Strength",
                "meta": {
                    "tickers": ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"],
                    "cash_ticker": "BIL",
                    "top": 2,
                    "rebalance_interval": 1,
                    "benchmark_ticker": "AOR",
                },
            }
        )

        self.assertEqual(
            override["promotion_min_net_cagr_spread"],
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        )
        self.assertIn("promotion_min_benchmark_coverage", override)
        self.assertIn("promotion_min_liquidity_clean_coverage", override)
        self.assertIn("promotion_max_drawdown_gap_vs_benchmark", override)

    def test_result_bundle_rejects_missing_required_columns(self) -> None:
        from app.runtime.backtest.result_bundle import build_backtest_result_bundle

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
        if "AS latest_raw_date" in sql and "ORDER BY `date` DESC" in sql:
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
        if "SUM(CASE WHEN volume IS NOT NULL THEN volume ELSE 0 END) AS total_volume" in sql:
            return [
                {
                    "symbol": "AAA",
                    "total_volume": 5_000,
                    "avg_daily_volume": 1_000,
                    "total_dollar_volume": 650_000.0,
                    "avg_daily_dollar_volume": 130_000.0,
                    "volume_days": 5,
                },
                {
                    "symbol": "BBB",
                    "total_volume": 7_500,
                    "avg_daily_volume": 1_500,
                    "total_dollar_volume": 900_000.0,
                    "avg_daily_dollar_volume": 180_000.0,
                    "volume_days": 5,
                },
                {
                    "symbol": "CCC",
                    "total_volume": 12_500,
                    "avg_daily_volume": 2_500,
                    "total_dollar_volume": 2_500_000.0,
                    "avg_daily_dollar_volume": 500_000.0,
                    "volume_days": 5,
                },
            ]
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
                {"symbol": "AAA", "date": "2026-05-11", "price": 100.0, "volume": 700},
                {"symbol": "AAA", "date": "2026-05-14", "price": 95.0, "volume": 900},
                {"symbol": "AAA", "date": "2026-05-15", "price": 100.0, "volume": 1000},
                {"symbol": "AAA", "date": "2026-05-18", "price": 110.0, "volume": 1500},
                {"symbol": "AAA", "date": "2026-04-17", "price": 100.0, "volume": 800},
                {"symbol": "BBB", "date": "2026-05-11", "price": 100.0, "volume": 1800},
                {"symbol": "BBB", "date": "2026-05-14", "price": 90.0, "volume": 1800},
                {"symbol": "BBB", "date": "2026-05-15", "price": 100.0, "volume": 2000},
                {"symbol": "BBB", "date": "2026-05-18", "price": 130.0, "volume": 2500},
                {"symbol": "BBB", "date": "2026-04-17", "price": 100.0, "volume": 1900},
                {"symbol": "CCC", "date": "2026-05-11", "price": 100.0, "volume": 1200},
                {"symbol": "CCC", "date": "2026-05-14", "price": 100.0, "volume": 1200},
                {"symbol": "CCC", "date": "2026-05-15", "price": 100.0, "volume": 1000},
                {"symbol": "CCC", "date": "2026-05-18", "price": 120.0, "volume": 1700},
                {"symbol": "CCC", "date": "2026-04-17", "price": 100.0, "volume": 1100},
                {"symbol": "DDD", "date": "2026-05-18", "price": 140.0, "volume": 900},
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

    def test_latest_raw_date_query_uses_ordered_latest_row(self) -> None:
        import inspect
        import app.services.overview_market_intelligence as service

        source = inspect.getsource(service._query_latest_raw_date)

        self.assertIn("ORDER BY `date` DESC", source)
        self.assertIn("LIMIT 1", source)
        self.assertNotIn("MAX(`date`)", source)

    def test_group_trend_window_contract_uses_compact_horizons(self) -> None:
        from app.services.overview_market_intelligence import resolve_group_trend_market_dates

        market_dates = [
            item.strftime("%Y-%m-%d")
            for item in reversed(pd.bdate_range(end="2026-05-29", periods=320).tolist())
        ]

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "AS latest_raw_date" in sql and "ORDER BY `date` DESC" in sql:
                return [{"latest_raw_date": market_dates[0]}]
            if "GROUP BY `date`" in sql:
                return [{"date": item, "usable_rows": 1200} for item in market_dates]
            return []

        daily = resolve_group_trend_market_dates(period="daily", query_fn=query_fn)
        weekly = resolve_group_trend_market_dates(period="weekly", query_fn=query_fn)
        monthly = resolve_group_trend_market_dates(period="monthly", query_fn=query_fn)

        self.assertEqual(daily["trend_window_label"], "Last 1M")
        self.assertEqual(len(daily["windows"]), 21)
        self.assertEqual(weekly["trend_window_label"], "Last 3M")
        self.assertEqual(len(weekly["windows"]), 13)
        self.assertEqual(monthly["trend_window_label"], "Last 12M")
        self.assertEqual(len(monthly["windows"]), 12)

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
        self.assertEqual(snapshot["rows"].iloc[0]["Volume"], 2500)
        self.assertEqual(snapshot["rows"].iloc[0]["Dollar Volume"], 325000.0)
        self.assertEqual(snapshot["rows"].iloc[0]["Previous Return %"], 11.11)
        self.assertEqual(snapshot["rows"].iloc[0]["Momentum Delta pp"], 18.89)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Basis"], "Daily dollar volume")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume"], 2500)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Dollar Volume"], 325000.0)
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
        self.assertEqual(snapshot["coverage"]["returnable_pct"], 50.0)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["status"], "stale")
        self.assertTrue(snapshot["coverage"]["refresh_state"]["refresh_due"])
        self.assertEqual(snapshot["coverage"]["refresh_state"]["check_interval_minutes"], 5)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["stale_after_minutes"], 15)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["next_due_in_minutes"], 0)
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 12.0)
        self.assertEqual(snapshot["rows"].iloc[0]["Volume"], 1000)
        self.assertEqual(snapshot["rows"].iloc[0]["Dollar Volume"], 112000.0)
        self.assertEqual(snapshot["rows"].iloc[0]["Previous Return %"], 5.26)
        self.assertEqual(snapshot["rows"].iloc[0]["Momentum Delta pp"], 6.74)
        self.assertEqual(snapshot["rows"].iloc[0]["Start Date"], "Previous Close")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Basis"], "Daily dollar volume")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Metric"], 112000.0)
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
        self.assertEqual(snapshot["coverage"]["returnable_pct"], 25.0)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["universe_count"], 4)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["returnable_count"], 1)
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 12.0)
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Reason"], "missing latest price")

    def test_market_movers_snapshot_uses_nasdaq_symbol_directory_current_snapshot(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM nyse_symbol_lifecycle" in sql:
                return [
                    {
                        "symbol": "AAPL",
                        "long_name": "Apple Inc.",
                        "sector": "Technology",
                        "industry": "Consumer Electronics",
                        "market_cap": 3_000_000_000_000,
                        "status": "active",
                        "error_msg": None,
                        "last_collected_at": "2026-06-16 10:00:00",
                        "profile_exchange": "NMS",
                        "listing_status": "active",
                        "source_type": "current_listing_snapshot",
                        "coverage_status": "partial",
                        "event_type": "listing_observed",
                        "event_date": "2026-06-17",
                        "universe_collected_at": "2026-06-17 08:00:00",
                        "universe_source": "nasdaq_symdir_nasdaqlisted",
                        "universe_source_url": "https://www.nasdaqtrader.com/",
                    },
                    {
                        "symbol": "MSFT",
                        "long_name": "Microsoft Corp.",
                        "sector": "Technology",
                        "industry": "Software",
                        "market_cap": 2_800_000_000_000,
                        "status": "active",
                        "error_msg": None,
                        "last_collected_at": "2026-06-16 10:00:00",
                        "profile_exchange": "NMS",
                        "listing_status": "active",
                        "source_type": "current_listing_snapshot",
                        "coverage_status": "partial",
                        "event_type": "listing_observed",
                        "event_date": "2026-06-17",
                        "universe_collected_at": "2026-06-17 08:00:00",
                        "universe_source": "nasdaq_symdir_nasdaqlisted",
                        "universe_source_url": "https://www.nasdaqtrader.com/",
                    },
                ]
            if "AS latest_raw_date" in sql and "ORDER BY `date` DESC" in sql:
                return [{"latest_raw_date": "2026-06-16"}]
            if "GROUP BY `date`" in sql:
                return [
                    {"date": "2026-06-16", "usable_rows": 5000},
                    {"date": "2026-06-15", "usable_rows": 5000},
                    {"date": "2026-06-12", "usable_rows": 5000},
                ]
            if "COALESCE(adj_close, close) AS price" in sql:
                return [
                    {"symbol": "AAPL", "date": "2026-06-15", "price": 100.0, "volume": 1000},
                    {"symbol": "AAPL", "date": "2026-06-16", "price": 106.0, "volume": 1500},
                    {"symbol": "MSFT", "date": "2026-06-15", "price": 200.0, "volume": 900},
                    {"symbol": "MSFT", "date": "2026-06-16", "price": 202.0, "volume": 1100},
                ]
            return []

        snapshot = build_market_movers_snapshot(
            universe_code="NASDAQ",
            universe_limit=5000,
            period="daily",
            top_n=5,
            today=date(2026, 6, 17),
            prefer_intraday=False,
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["universe_code"], "NASDAQ")
        self.assertEqual(snapshot["universe_label"], "Nasdaq-listed current snapshot")
        self.assertEqual(snapshot["coverage"]["coverage_basis"], "Nasdaq-listed current snapshot")
        self.assertEqual(snapshot["coverage"]["universe_source"], "nasdaq_symdir_nasdaqlisted")
        self.assertEqual(snapshot["coverage"]["universe_source_type"], "current_listing_snapshot")
        self.assertEqual(snapshot["coverage"]["universe_coverage_status"], "partial")
        self.assertEqual(snapshot["coverage"]["universe_event_date"], "2026-06-17")
        self.assertIn("current listing observation only", snapshot["coverage"]["universe_caveat"])
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "AAPL")

    def test_market_movers_snapshot_explains_missing_nasdaq_directory_refresh(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, sql, params
            return []

        snapshot = build_market_movers_snapshot(
            universe_code="NASDAQ",
            universe_limit=5000,
            period="daily",
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "NO_UNIVERSE")
        self.assertEqual(snapshot["universe_code"], "NASDAQ")
        self.assertIn("Nasdaq Symbol Directory refresh", snapshot["message"])

    def test_market_movers_missing_rows_include_profile_lifecycle_and_issue_evidence(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM nyse_asset_profile" in sql:
                return [
                    {
                        "symbol": "AAA",
                        "long_name": "AAA Corp",
                        "sector": "Technology",
                        "industry": "Software",
                        "market_cap": 100,
                        "status": "active",
                        "error_msg": None,
                        "last_collected_at": "2026-06-16 10:00:00",
                        "profile_exchange": "NYS",
                    },
                    {
                        "symbol": "STALE",
                        "long_name": "Stale Corp",
                        "sector": "Technology",
                        "industry": "Software",
                        "market_cap": 90,
                        "status": "error",
                        "error_msg": "provider profile unavailable",
                        "last_collected_at": "2026-03-23 10:00:00",
                        "profile_exchange": "NMS",
                    },
                ]
            if "AS latest_raw_date" in sql and "ORDER BY `date` DESC" in sql:
                return [{"latest_raw_date": "2026-06-16"}]
            if "GROUP BY `date`" in sql:
                return [
                    {"date": "2026-06-16", "usable_rows": 5000},
                    {"date": "2026-06-15", "usable_rows": 5000},
                    {"date": "2026-06-12", "usable_rows": 5000},
                ]
            if "COALESCE(adj_close, close) AS price" in sql:
                return [
                    {"symbol": "AAA", "date": "2026-06-15", "price": 100.0, "volume": 1000},
                    {"symbol": "AAA", "date": "2026-06-16", "price": 105.0, "volume": 1000},
                    {"symbol": "STALE", "date": "2026-06-16", "price": 10.0, "volume": 100},
                ]
            if "MAX(`date`) AS latest_price_date" in sql:
                return [{"symbol": "STALE", "latest_price_date": "2026-03-23"}]
            if "FROM nyse_symbol_lifecycle" in sql:
                return [
                    {
                        "symbol": "STALE",
                        "listing_status": "active",
                        "source": "nasdaq_symdir_nasdaqlisted",
                        "source_type": "current_listing_snapshot",
                        "coverage_status": "partial",
                        "event_type": "listing_observed",
                        "event_date": "2026-06-17",
                        "collected_at": "2026-06-17 08:00:00",
                    }
                ]
            if "FROM market_data_issue" in sql:
                return [
                    {
                        "symbol": "STALE",
                        "issue_type": "quote_gap",
                        "diagnosis": "provider_quote_gap",
                        "occurrence_count": 3,
                        "last_seen_at": "2026-06-16 14:00:00",
                        "latest_evidence": "quote endpoint missing while DB price exists",
                    }
                ]
            return []

        snapshot = build_market_movers_snapshot(
            universe_code="TOP1000",
            universe_limit=1000,
            period="daily",
            today=date(2026, 6, 17),
            prefer_intraday=False,
            query_fn=query_fn,
        )
        missing = snapshot["missing_rows"]

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(missing.iloc[0]["Symbol"], "STALE")
        for column in ["Likely Cause", "Evidence Summary", "Next Check", "Listing Evidence", "Profile Freshness", "Market Data Issue"]:
            self.assertIn(column, missing.columns)
        self.assertIn("Profile status error", missing.iloc[0]["Evidence Summary"])
        self.assertIn("current_listing_snapshot", missing.iloc[0]["Listing Evidence"])
        self.assertIn("current listing observation only", missing.iloc[0]["Listing Evidence"])
        self.assertIn("provider_quote_gap", missing.iloc[0]["Market Data Issue"])
        self.assertIn("profile", missing.iloc[0]["Next Check"].lower())

    def test_market_movers_weekly_volume_rows_use_average_and_total_volume(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_code="TOP1000",
            period="weekly",
            top_n=5,
            today=date(2026, 5, 28),
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 30.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Symbol"], "CCC")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Basis"], "Avg daily dollar volume")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Metric"], 500000.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Avg Daily Volume"], 2500)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Total Volume"], 12500)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Avg Daily Dollar Volume"], 500000.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Total Dollar Volume"], 2500000.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Days"], 5)

    def test_market_mover_catalyst_links_include_context_without_fetching_articles(self) -> None:
        from app.services.overview_market_intelligence import build_market_mover_catalyst_links

        rows = build_market_mover_catalyst_links(
            symbol="AAA",
            name="AAA Corp",
            period="weekly",
            coverage="TOP1000",
            rank=2,
            rank_source="Volume Rank",
        )

        self.assertEqual(len(rows), 6)
        self.assertEqual(rows.iloc[0]["Source"], "Yahoo Finance")
        self.assertEqual(rows.iloc[0]["URL"], "https://finance.yahoo.com/quote/AAA")
        self.assertIn("AAA", rows.iloc[1]["Search Query"])
        self.assertIn("AAA Corp", rows.iloc[1]["Search Query"])
        self.assertIn("Weekly", rows.iloc[1]["Search Query"])
        self.assertIn("Top 1000 by market cap", rows.iloc[1]["Search Query"])
        self.assertIn("Volume Rank 2", rows.iloc[1]["Search Query"])
        self.assertIn("news.google.com/search", rows.iloc[1]["URL"])
        self.assertIn("SEC", rows.iloc[2]["Source"])
        self.assertIn("sec.gov/edgar/search", rows.iloc[2]["URL"])
        self.assertIn("Investor Relations", rows.iloc[3]["Source"])
        self.assertIn("www.google.com/search", rows.iloc[3]["URL"])
        self.assertEqual(rows.iloc[4]["Source"], "Google News KR")
        self.assertIn("뉴스", rows.iloc[4]["Search Query"])
        self.assertIn("hl=ko", rows.iloc[4]["URL"])
        self.assertIn("ceid=KR%3Ako", rows.iloc[4]["URL"])
        self.assertEqual(rows.iloc[5]["Source"], "Naver News")
        self.assertIn("주가", rows.iloc[5]["Search Query"])
        self.assertIn("search.naver.com/search.naver", rows.iloc[5]["URL"])

    def test_market_mover_why_it_moved_read_model_includes_context_links_and_pending_metadata(self) -> None:
        from app.services.overview_market_intelligence import build_market_mover_why_it_moved_read_model

        model = build_market_mover_why_it_moved_read_model(
            mover={
                "Rank": 2,
                "Symbol": "AAA",
                "Name": "AAA Corp",
                "Sector": "Technology",
                "Industry": "Software",
                "Market Cap": 1234567890,
                "Return %": 12.34,
                "Volume": 987654,
                "Dollar Volume": 54321000.25,
                "Previous Return %": 3.21,
                "Momentum Delta pp": 9.13,
            },
            period="weekly",
            coverage="TOP1000",
            rank_source="Volume Rank",
        )

        self.assertEqual(model["status"], "READY")
        self.assertEqual(model["mode"], "manual_investigation")
        self.assertEqual(model["identity"]["Symbol"], "AAA")
        self.assertEqual(model["identity"]["Sector"], "Technology")
        self.assertEqual(model["context"]["Period"], "Weekly")
        self.assertEqual(model["context"]["Coverage"], "Top 1000 by market cap")
        self.assertEqual(model["context"]["Rank Type"], "Volume Rank")
        self.assertEqual(model["context"]["Rank"], "2")
        self.assertEqual(model["movement"]["Return %"], 12.34)
        self.assertEqual(model["movement"]["Momentum Delta pp"], 9.13)
        self.assertEqual(model["metadata"]["status"], "NOT_REQUESTED")
        self.assertEqual(len(model["links"]), 6)
        self.assertEqual(model["links"].iloc[0]["Source"], "Yahoo Finance")
        self.assertIn("Google News KR", set(model["links"]["Source"]))
        self.assertIn("Naver News", set(model["links"]["Source"]))

    def test_market_mover_compact_metadata_fetcher_keeps_news_and_sec_metadata_bounded(self) -> None:
        from app.services.overview_market_intelligence import fetch_market_mover_compact_metadata

        def news_fetcher(symbol: str, max_items: int) -> list[dict[str, object]]:
            self.assertEqual(symbol, "AAA")
            self.assertEqual(max_items, 2)
            return [
                {
                    "title": "AAA shares rise after guidance update",
                    "publisher": "Market Desk",
                    "published_at": "2026-06-03T13:00:00Z",
                    "url": "https://example.com/news/aaa",
                    "body": "article body should not enter compact metadata",
                }
            ]

        def sec_fetcher(symbol: str, max_items: int, user_agent: str | None, request_timeout: float) -> list[dict[str, object]]:
            self.assertEqual(symbol, "AAA")
            self.assertEqual(max_items, 2)
            self.assertGreater(request_timeout, 0)
            return [
                {
                    "form": "8-K",
                    "filing_date": "2026-06-02",
                    "title": "Current report",
                    "url": "https://www.sec.gov/Archives/edgar/data/1/0001/a8k.htm",
                    "document": "filing body should not enter compact metadata",
                }
            ]

        metadata = fetch_market_mover_compact_metadata(
            "aaa",
            max_news=2,
            max_filings=2,
            news_fetcher=news_fetcher,
            sec_fetcher=sec_fetcher,
            korean_news_fetcher=lambda symbol, name, max_items, request_timeout: [],
        )

        self.assertEqual(metadata["status"], "OK")
        self.assertEqual(metadata["symbol"], "AAA")
        self.assertEqual(list(metadata["news"].columns), ["Title", "Source", "Published At", "URL"])
        self.assertEqual(metadata["news"].iloc[0]["Title"], "AAA shares rise after guidance update")
        self.assertNotIn("Body", metadata["news"].columns)
        self.assertEqual(list(metadata["korean_news"].columns), ["Title", "Source", "Published At", "Snippet", "URL"])
        self.assertNotIn("Body", metadata["korean_news"].columns)
        self.assertEqual(list(metadata["sec_filings"].columns), ["Form", "Filing Date", "Title", "URL"])
        self.assertEqual(metadata["sec_filings"].iloc[0]["Form"], "8-K")
        self.assertNotIn("Document", metadata["sec_filings"].columns)

    def test_market_mover_compact_metadata_fetcher_adds_korean_news_metadata_lane(self) -> None:
        from app.services.overview_market_intelligence import fetch_market_mover_compact_metadata

        def korean_news_fetcher(
            symbol: str,
            name: str | None,
            max_items: int,
            request_timeout: float,
        ) -> list[dict[str, object]]:
            self.assertEqual(symbol, "AAA")
            self.assertEqual(name, "AAA Corp")
            self.assertEqual(max_items, 2)
            self.assertGreater(request_timeout, 0)
            return [
                {
                    "title": "<b>AAA</b> 주가 급등",
                    "originallink": "https://news.example.kr/aaa-original",
                    "link": "https://n.news.naver.com/article/001/0001",
                    "description": "<b>AAA</b>가 실적 발표 이후 상승했다는 기사 패시지입니다.",
                    "pubDate": "Sat, 06 Jun 2026 09:15:00 +0900",
                    "body": "Korean article body must not enter compact metadata",
                }
            ]

        metadata = fetch_market_mover_compact_metadata(
            "aaa",
            name="AAA Corp",
            max_news=0,
            max_korean_news=2,
            max_filings=0,
            news_fetcher=lambda symbol, max_items: [],
            korean_news_fetcher=korean_news_fetcher,
            sec_fetcher=lambda symbol, max_items, user_agent, request_timeout: [],
        )

        self.assertEqual(metadata["status"], "OK")
        korean_news = metadata["korean_news"]
        self.assertEqual(list(korean_news.columns), ["Title", "Source", "Published At", "Snippet", "URL"])
        self.assertEqual(korean_news.iloc[0]["Title"], "AAA 주가 급등")
        self.assertEqual(korean_news.iloc[0]["URL"], "https://news.example.kr/aaa-original")
        self.assertEqual(korean_news.iloc[0]["Source"], "news.example.kr")
        self.assertIn("실적 발표 이후 상승", korean_news.iloc[0]["Snippet"])
        self.assertNotIn("<b>", korean_news.iloc[0]["Title"])
        self.assertNotIn("Body", korean_news.columns)

    def test_market_mover_google_news_kr_rss_fetcher_builds_keyless_metadata_rows(self) -> None:
        from urllib.parse import parse_qs, urlparse

        import app.services.overview_market_intelligence as service

        self.assertTrue(
            hasattr(service, "_fetch_google_news_kr_rss_metadata"),
            "Google News KR RSS metadata fetcher should exist as the default keyless Korean news provider.",
        )

        observed_request: dict[str, object] = {}
        payload = b"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <item>
              <title><![CDATA[AAA \xec\xa3\xbc\xea\xb0\x80 \xea\xb8\x89\xeb\x93\xb1 - Investing.com \xed\x95\x9c\xea\xb5\xad\xec\x96\xb4]]></title>
              <link>https://news.google.com/rss/articles/aaa</link>
              <pubDate>Sat, 06 Jun 2026 09:15:00 GMT</pubDate>
              <source url="https://kr.investing.com">Investing.com \xed\x95\x9c\xea\xb5\xad\xec\x96\xb4</source>
              <description><![CDATA[<a href="https://example.kr/aaa">AAA</a> \xec\x8b\xa4\xec\xa0\x81 \xeb\xb0\x9c\xed\x91\x9c \xec\x9d\xb4\xed\x9b\x84 \xec\x83\x81\xec\x8a\xb9...]]></description>
            </item>
          </channel>
        </rss>"""

        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self) -> bytes:
                return payload

        def fake_urlopen(request: object, timeout: float) -> FakeResponse:
            observed_request["url"] = getattr(request, "full_url", "")
            observed_request["headers"] = dict(request.header_items())
            observed_request["timeout"] = timeout
            return FakeResponse()

        with patch("urllib.request.urlopen", fake_urlopen):
            rows = service._fetch_google_news_kr_rss_metadata("aaa", "AAA Corp", 3, 4.5)

        request_url = str(observed_request["url"])
        query = parse_qs(urlparse(request_url).query)
        self.assertEqual(urlparse(request_url).netloc, "news.google.com")
        self.assertEqual(urlparse(request_url).path, "/rss/search")
        self.assertIn("AAA", query["q"][0])
        self.assertIn("AAA Corp", query["q"][0])
        self.assertIn("주가", query["q"][0])
        self.assertEqual(query["hl"], ["ko"])
        self.assertEqual(query["gl"], ["KR"])
        self.assertEqual(query["ceid"], ["KR:ko"])
        self.assertGreater(len(str(observed_request["headers"].get("User-agent") or "")), 0)
        self.assertEqual(observed_request["timeout"], 4.5)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "AAA 주가 급등 - Investing.com 한국어")
        self.assertEqual(rows[0]["link"], "https://news.google.com/rss/articles/aaa")
        self.assertEqual(rows[0]["source"], "Investing.com 한국어")
        self.assertIn("실적 발표 이후 상승", rows[0]["description"])
        self.assertEqual(rows[0]["pubDate"], "Sat, 06 Jun 2026 09:15:00 GMT")
        self.assertNotIn("body", rows[0])

    def test_market_mover_compact_metadata_fetcher_uses_google_news_kr_without_naver_credentials(self) -> None:
        import app.services.overview_market_intelligence as service

        calls: list[tuple[str, str | None, int, float]] = []

        def google_news_fetcher(
            symbol: str,
            name: str | None,
            max_items: int,
            request_timeout: float,
        ) -> list[dict[str, object]]:
            calls.append((symbol, name, max_items, request_timeout))
            return [
                {
                    "title": "AAA 주가 급등 - 한국경제",
                    "link": "https://news.google.com/rss/articles/aaa",
                    "source": "한국경제",
                    "description": "AAA 실적 발표 이후 상승했다는 검색 결과 단서입니다.",
                    "pubDate": "Sat, 06 Jun 2026 09:15:00 GMT",
                    "body": "article body should not enter compact metadata",
                }
            ]

        from app.services.overview_market_intelligence import fetch_market_mover_compact_metadata

        with patch.dict(
            "os.environ",
            {"NAVER_SEARCH_CLIENT_ID": "", "NAVER_SEARCH_CLIENT_SECRET": ""},
            clear=False,
        ), patch.object(service, "_fetch_google_news_kr_rss_metadata", google_news_fetcher, create=True):
            metadata = fetch_market_mover_compact_metadata(
                "AAA",
                name="AAA Corp",
                max_korean_news=3,
                news_fetcher=lambda symbol, max_items: [
                    {
                        "title": "AAA shares rise",
                        "publisher": "Market Desk",
                        "published_at": "2026-06-03T13:00:00Z",
                        "url": "https://example.com/news/aaa",
                    }
                ],
                sec_fetcher=lambda symbol, max_items, user_agent, request_timeout: [],
            )

        self.assertEqual(metadata["status"], "OK")
        self.assertEqual(calls, [("AAA", "AAA Corp", 3, 8.0)])
        self.assertFalse(metadata["korean_news"].empty)
        self.assertEqual(metadata["korean_news"].iloc[0]["Source"], "한국경제")
        self.assertEqual(metadata["korean_news"].iloc[0]["URL"], "https://news.google.com/rss/articles/aaa")
        self.assertNotIn("Body", metadata["korean_news"].columns)
        self.assertFalse(any("NAVER_SEARCH" in message for message in metadata["messages"]))

    def test_market_mover_compact_metadata_fetcher_distinguishes_empty_and_failed(self) -> None:
        from app.services.overview_market_intelligence import fetch_market_mover_compact_metadata

        empty = fetch_market_mover_compact_metadata(
            "AAA",
            news_fetcher=lambda symbol, max_items: [],
            korean_news_fetcher=lambda symbol, name, max_items, request_timeout: [],
            sec_fetcher=lambda symbol, max_items, user_agent, request_timeout: [],
        )

        self.assertEqual(empty["status"], "NO_METADATA")
        self.assertEqual(empty["messages"], ["AAA에 대해 간단 뉴스, 한국어 뉴스 또는 SEC 공시 메타데이터가 반환되지 않았습니다."])

        def failing_news(symbol: str, max_items: int) -> list[dict[str, object]]:
            raise RuntimeError("news timeout")

        def failing_sec(symbol: str, max_items: int, user_agent: str | None, request_timeout: float) -> list[dict[str, object]]:
            raise RuntimeError("sec timeout")

        failed = fetch_market_mover_compact_metadata(
            "AAA",
            news_fetcher=failing_news,
            korean_news_fetcher=lambda symbol, name, max_items, request_timeout: [],
            sec_fetcher=failing_sec,
        )

        self.assertEqual(failed["status"], "FAILED")
        self.assertEqual(failed["news"].empty, True)
        self.assertEqual(failed["sec_filings"].empty, True)
        self.assertIn("뉴스 메타데이터 조회 실패: news timeout", failed["messages"])
        self.assertIn("SEC 메타데이터 조회 실패: sec timeout", failed["messages"])

    def test_market_mover_compact_metadata_fetcher_marks_partial_provider_failure(self) -> None:
        from app.services.overview_market_intelligence import fetch_market_mover_compact_metadata

        def sec_timeout(symbol: str, max_items: int, user_agent: str | None, request_timeout: float) -> list[dict[str, object]]:
            raise RuntimeError("sec timeout")

        metadata = fetch_market_mover_compact_metadata(
            "AAA",
            news_fetcher=lambda symbol, max_items: [
                {
                    "title": "AAA shares rise",
                    "publisher": "Market Desk",
                    "published_at": "2026-06-03T13:00:00Z",
                    "url": "https://example.com/news/aaa",
                }
            ],
            korean_news_fetcher=lambda symbol, name, max_items, request_timeout: [],
            sec_fetcher=sec_timeout,
        )

        self.assertEqual(metadata["status"], "PARTIAL")
        self.assertEqual(metadata["news"].empty, False)
        self.assertEqual(metadata["sec_filings"].empty, True)
        self.assertIn("SEC 메타데이터 조회 실패: sec timeout", metadata["messages"])

    def test_market_mover_metadata_status_strip_distinguishes_lookup_states(self) -> None:
        from app.services.overview_market_intelligence import (
            WHY_IT_MOVED_NEWS_COLUMNS,
            WHY_IT_MOVED_KOREAN_NEWS_COLUMNS,
            WHY_IT_MOVED_SEC_COLUMNS,
            build_market_mover_metadata_not_requested_state,
            build_market_mover_metadata_status_strip,
        )

        not_requested = build_market_mover_metadata_status_strip(
            build_market_mover_metadata_not_requested_state("AAA")
        )
        self.assertEqual(not_requested["lookup"]["label"], "조회 상태")
        self.assertEqual(not_requested["lookup"]["value"], "조회 전")
        self.assertEqual(not_requested["lookup"]["tone"], "neutral")
        self.assertEqual(not_requested["news"]["value"], "조회 전")
        self.assertEqual(not_requested["korean_news"]["value"], "조회 전")
        self.assertEqual(not_requested["sec"]["value"], "조회 전")
        self.assertEqual(not_requested["storage"]["label"], "저장 경계")
        self.assertEqual(not_requested["storage"]["value"], "세션 전용")

        partial = build_market_mover_metadata_status_strip(
            {
                "status": "PARTIAL",
                "fetched_at_utc": "2026-06-04T01:02:03Z",
                "news": pd.DataFrame(
                    [{"Title": "AAA moves", "Source": "Desk", "Published At": "2026-06-04", "URL": "https://example.com"}],
                    columns=WHY_IT_MOVED_NEWS_COLUMNS,
                ),
                "korean_news": pd.DataFrame([], columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS),
                "sec_filings": pd.DataFrame([], columns=WHY_IT_MOVED_SEC_COLUMNS),
                "messages": ["SEC 메타데이터 조회 실패: timeout"],
            }
        )
        self.assertEqual(partial["lookup"]["value"], "부분 완료")
        self.assertEqual(partial["lookup"]["tone"], "warning")
        self.assertEqual(partial["news"]["value"], "1건")
        self.assertEqual(partial["korean_news"]["value"], "0건")
        self.assertEqual(partial["sec"]["value"], "실패")
        self.assertEqual(partial["fetched_at"]["value"], "2026-06-04T01:02:03Z")

        korean_failed = build_market_mover_metadata_status_strip(
            {
                "status": "PARTIAL",
                "fetched_at_utc": "2026-06-04T01:02:03Z",
                "news": pd.DataFrame(
                    [{"Title": "AAA moves", "Source": "Desk", "Published At": "2026-06-04", "URL": "https://example.com"}],
                    columns=WHY_IT_MOVED_NEWS_COLUMNS,
                ),
                "korean_news": pd.DataFrame([], columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS),
                "sec_filings": pd.DataFrame([], columns=WHY_IT_MOVED_SEC_COLUMNS),
                "messages": ["한국어 뉴스 메타데이터 조회 실패: timeout"],
            }
        )
        self.assertEqual(korean_failed["korean_news"]["value"], "실패")
        self.assertEqual(korean_failed["korean_news"]["tone"], "error")

        failed = build_market_mover_metadata_status_strip(
            {
                "status": "FAILED",
                "fetched_at_utc": "2026-06-04T01:02:03Z",
                "news": pd.DataFrame([], columns=WHY_IT_MOVED_NEWS_COLUMNS),
                "korean_news": pd.DataFrame([], columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS),
                "sec_filings": pd.DataFrame([], columns=WHY_IT_MOVED_SEC_COLUMNS),
                "messages": [
                    "뉴스 메타데이터 조회 실패: timeout",
                    "한국어 뉴스 메타데이터 조회 실패: timeout",
                    "SEC 메타데이터 조회 실패: timeout",
                ],
            }
        )
        self.assertEqual(failed["lookup"]["value"], "실패")
        self.assertEqual(failed["lookup"]["tone"], "error")
        self.assertEqual(failed["news"]["value"], "실패")
        self.assertEqual(failed["korean_news"]["value"], "실패")
        self.assertEqual(failed["sec"]["value"], "실패")

        no_metadata = build_market_mover_metadata_status_strip(
            {
                "status": "NO_METADATA",
                "fetched_at_utc": "2026-06-04T01:02:03Z",
                "news": pd.DataFrame([], columns=WHY_IT_MOVED_NEWS_COLUMNS),
                "korean_news": pd.DataFrame([], columns=WHY_IT_MOVED_KOREAN_NEWS_COLUMNS),
                "sec_filings": pd.DataFrame([], columns=WHY_IT_MOVED_SEC_COLUMNS),
                "messages": ["AAA에 대해 간단 뉴스, 한국어 뉴스 또는 SEC 공시 메타데이터가 반환되지 않았습니다."],
            }
        )
        self.assertEqual(no_metadata["lookup"]["value"], "메타데이터 없음")
        self.assertEqual(no_metadata["lookup"]["tone"], "warning")
        self.assertEqual(no_metadata["news"]["value"], "0건")
        self.assertEqual(no_metadata["korean_news"]["value"], "0건")
        self.assertEqual(no_metadata["sec"]["value"], "0건")

    def test_market_mover_sec_filings_sort_by_form_priority_deterministically(self) -> None:
        from app.services.overview_market_intelligence import sort_market_mover_sec_filings_by_form_priority

        filings = pd.DataFrame(
            [
                {"Form": "4", "Filing Date": "2026-06-04", "Title": "Insider", "URL": "https://example.com/4"},
                {"Form": "10-Q", "Filing Date": "2026-06-04", "Title": "Quarterly", "URL": "https://example.com/10q"},
                {"Form": "SC 13G", "Filing Date": "2026-06-04", "Title": "Other", "URL": "https://example.com/13g"},
                {"Form": "8-K", "Filing Date": "2026-06-04", "Title": "Current", "URL": "https://example.com/8k"},
                {"Form": "10-K", "Filing Date": "2026-06-03", "Title": "Annual", "URL": "https://example.com/10k"},
            ]
        )

        sorted_filings = sort_market_mover_sec_filings_by_form_priority(filings)

        self.assertEqual(list(sorted_filings["Form"]), ["8-K", "10-Q", "4", "SC 13G", "10-K"])
        self.assertEqual(list(sorted_filings.columns), ["Form", "Filing Date", "Title", "URL"])

    def test_market_mover_sec_lane_keeps_metadata_table_only_without_preview_helpers(self) -> None:
        import app.services.overview_market_intelligence as market_intelligence
        import app.web.overview_dashboard as overview_dashboard

        sec_filings = pd.DataFrame(
            [
                {
                    "Form": "8-K",
                    "Filing Date": "2026-06-04",
                    "Title": "Current report",
                    "URL": "https://www.sec.gov/Archives/edgar/data/1/0001/a8k.htm",
                }
            ]
        )

        display = overview_dashboard._market_mover_open_link_frame(sec_filings, ["Form", "Filing Date", "Title", "Open"])
        config = overview_dashboard._market_mover_metadata_column_config()

        self.assertEqual(list(display.columns), ["양식", "공시일", "제목", "열기"])
        self.assertEqual(display.iloc[0]["열기"], "https://www.sec.gov/Archives/edgar/data/1/0001/a8k.htm")
        self.assertIn("열기", config)
        self.assertEqual(config["열기"]["type_config"]["type"], "link")
        self.assertFalse(hasattr(overview_dashboard, "_render_market_mover_sec_preview_controls"))
        self.assertFalse(hasattr(overview_dashboard, "_market_mover_sec_digest_display_model"))
        self.assertFalse(hasattr(market_intelligence, "fetch_market_mover_sec_filing_preview"))
        self.assertFalse(hasattr(market_intelligence, "parse_market_mover_sec_filing_preview"))

    def test_market_mover_catalyst_candidates_keep_return_and_volume_rank_context(self) -> None:
        from app.web.overview_dashboard import _market_mover_catalyst_candidates

        return_rows = pd.DataFrame(
            [
                {
                    "Rank": 1,
                    "Symbol": "AAA",
                    "Name": "AAA Corp",
                    "Sector": "Technology",
                    "Industry": "Software",
                    "Market Cap": 1234567890,
                    "Return %": 12.34,
                    "Volume": 987654,
                    "Dollar Volume": 54321000.25,
                    "Previous Return %": 3.21,
                    "Momentum Delta pp": 9.13,
                },
                {"Rank": 2, "Symbol": "BBB", "Name": "BBB Corp"},
            ]
        )
        volume_rows = pd.DataFrame(
            [
                {"Rank": 1, "Symbol": "BBB", "Name": "BBB Corp"},
                {"Rank": 2, "Symbol": "AAA", "Name": "AAA Corp"},
            ]
        )

        candidates = _market_mover_catalyst_candidates(return_rows, volume_rows)

        self.assertEqual([item["id"] for item in candidates], ["return:1:AAA", "return:2:BBB", "volume:1:BBB", "volume:2:AAA"])
        self.assertEqual(candidates[0]["rank_source"], "Return Rank")
        self.assertEqual(candidates[2]["rank_source"], "Volume Rank")
        self.assertIn("수익률 #1", candidates[0]["label"])
        self.assertIn("거래량 #1", candidates[2]["label"])
        self.assertEqual(candidates[0]["mover"]["Sector"], "Technology")
        self.assertEqual(candidates[0]["mover"]["Return %"], 12.34)
        self.assertEqual(candidates[0]["mover"]["Momentum Delta pp"], 9.13)

    def test_market_mover_metadata_tables_configure_url_as_clickable_link(self) -> None:
        from app.web.overview_dashboard import _market_mover_metadata_column_config

        config = _market_mover_metadata_column_config()

        self.assertIn("열기", config)
        self.assertEqual(config["열기"]["type_config"]["type"], "link")
        self.assertEqual(config["열기"]["type_config"]["display_text"], "열기")

    def test_market_mover_korean_news_display_model_keeps_snippet_and_clickable_open_link(self) -> None:
        from app.web.overview_dashboard import _market_mover_metadata_column_config, _market_mover_open_link_frame

        frame = pd.DataFrame(
            [
                {
                    "Title": "AAA 주가 급등",
                    "Source": "news.example.kr",
                    "Published At": "Sat, 06 Jun 2026 09:15:00 +0900",
                    "Snippet": "실적 발표 이후 상승했다는 기사 패시지입니다.",
                    "URL": "https://news.example.kr/aaa-original",
                }
            ]
        )

        display = _market_mover_open_link_frame(frame, ["Title", "Source", "Published At", "Snippet", "Open"])
        config = _market_mover_metadata_column_config()

        self.assertEqual(list(display.columns), ["제목", "출처", "게시 시각", "단서", "열기"])
        self.assertEqual(display.iloc[0]["단서"], "실적 발표 이후 상승했다는 기사 패시지입니다.")
        self.assertEqual(display.iloc[0]["열기"], "https://news.example.kr/aaa-original")
        self.assertEqual(config["열기"]["type_config"]["type"], "link")

    def test_market_mover_research_link_tables_share_clickable_url_config(self) -> None:
        from app.web.overview_dashboard import _market_mover_external_search_table_model

        table_model = _market_mover_external_search_table_model(
            pd.DataFrame(
                [
                    {
                        "Source": "Google News KR",
                        "URL": "https://news.google.com/search?q=AAA",
                        "Search Query": "AAA 뉴스",
                        "Purpose": "Korean-language search.",
                    },
                    {
                        "Source": "Naver News",
                        "URL": "https://search.naver.com/search.naver?where=news&query=AAA",
                        "Search Query": "AAA 뉴스",
                        "Purpose": "Naver search.",
                    },
                ]
            )
        )
        config = table_model["column_config"]

        self.assertEqual(table_model["label"], "외부 검색")
        self.assertFalse(table_model["expanded"])
        self.assertEqual(list(table_model["rows"].columns), ["출처", "열기", "검색어", "용도"])
        self.assertIn("Google News KR", set(table_model["rows"]["출처"]))
        self.assertIn("Naver News", set(table_model["rows"]["출처"]))
        self.assertIn("열기", config)
        self.assertEqual(config["열기"]["type_config"]["type"], "link")
        self.assertEqual(config["열기"]["type_config"]["display_text"], "열기")

    def test_market_movers_snapshot_falls_back_to_listing_names(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        observed_sql: dict[str, str] = {}

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            if "FROM nyse_asset_profile p" in sql:
                observed_sql["universe"] = sql
                return [
                    {
                        "symbol": "AAA",
                        "long_name": "AAA LISTING INC",
                        "sector": "Technology",
                        "industry": "Software",
                        "market_cap": 100,
                    },
                    {
                        "symbol": "BBB",
                        "long_name": "BBB LISTING INC",
                        "sector": "Technology",
                        "industry": "Software",
                        "market_cap": 300,
                    },
                ]
            return self._query_fn(db_name, sql, params)

        snapshot = build_market_movers_snapshot(
            universe_code="TOP1000",
            period="daily",
            top_n=5,
            today=date(2026, 5, 28),
            prefer_intraday=False,
            query_fn=query_fn,
        )

        self.assertIn("LEFT JOIN nyse_stock", observed_sql["universe"])
        self.assertIn("COALESCE(NULLIF(p.long_name, ''), s.name)", observed_sql["universe"])
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["rows"].iloc[0]["Name"], "BBB LISTING INC")

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
        self.assertEqual(snapshot["period"], "monthly")
        self.assertEqual(snapshot["trend_window_label"], "Last 12M")
        self.assertFalse(snapshot["trend_rows"].empty)
        self.assertFalse(snapshot["ticker_leader_rows"].empty)
        self.assertEqual(snapshot["coverage"]["returnable_count"], 3)
        first_row = snapshot["rows"].iloc[0]
        self.assertEqual(first_row["Group"], "Technology")
        self.assertEqual(first_row["Symbols"], 2)
        self.assertEqual(first_row["Positive Symbols"], 2)
        self.assertEqual(first_row["Positive Symbol Share %"], 100.0)
        self.assertEqual(first_row["Equal Weight Return %"], 20.0)
        self.assertEqual(first_row["Market Cap Weighted Return %"], 25.0)
        self.assertEqual(first_row["Cap vs Equal Gap pp"], 5.0)
        self.assertEqual(first_row["Top 3 Positive Share %"], 100.0)
        self.assertEqual(first_row["Top Symbol"], "BBB")
        technology_leaders = snapshot["ticker_leader_rows"][
            snapshot["ticker_leader_rows"]["Group"] == "Technology"
        ].sort_values("Rank")
        self.assertEqual(technology_leaders["Symbol"].tolist(), ["BBB", "AAA"])
        self.assertEqual(technology_leaders.iloc[0]["Positive Return Share %"], 75.0)
        self.assertIn("Previous Return %", technology_leaders.columns)
        self.assertIn("Momentum Delta pp", technology_leaders.columns)

    def test_group_leadership_snapshot_supports_sp500_daily_trend(self) -> None:
        from app.services.overview_market_intelligence import build_group_leadership_snapshot

        snapshot = build_group_leadership_snapshot(
            universe_code="SP500",
            universe_limit=500,
            group_by="sector",
            period="daily",
            top_n=5,
            min_group_size=1,
            today=date(2026, 5, 28),
            trend_groups=("Healthcare",),
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["universe_code"], "SP500")
        self.assertEqual(snapshot["period"], "daily")
        self.assertEqual(snapshot["trend_window_label"], "Last 1M")
        self.assertEqual(snapshot["coverage"]["price_mode"], "Intraday Snapshot")
        self.assertEqual(snapshot["coverage"]["snapshot_time_utc"], "2026-05-18 15:35")
        self.assertEqual(snapshot["date_window"]["start_date"], "Previous Close")
        self.assertEqual(snapshot["rows"].iloc[0]["Top Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Top Symbol Return %"], 12.0)
        self.assertEqual(snapshot["ticker_leader_rows"].iloc[0]["End Date"], "2026-05-18 15:30")
        self.assertEqual(snapshot["ticker_leader_rows"].iloc[0]["Previous Return %"], 5.26)
        self.assertEqual(snapshot["ticker_leader_rows"].iloc[0]["Momentum Delta pp"], 6.74)
        self.assertEqual(snapshot["coverage"]["coverage_basis"], "Current S&P 500 constituents")
        self.assertFalse(snapshot["rows"].empty)
        self.assertFalse(snapshot["trend_rows"].empty)
        self.assertIn("Healthcare", set(snapshot["trend_rows"]["Group"]))

    def test_overview_breadth_heatmap_summary_scores_participation_and_concentration(self) -> None:
        from app.services.overview_market_intelligence import build_overview_breadth_heatmap_summary

        snapshot = {
            "status": "OK",
            "period": "daily",
            "universe_code": "SP500",
            "coverage": {
                "returnable_count": 503,
                "price_mode": "Intraday Snapshot",
                "snapshot_time_utc": "2026-06-08 14:00",
            },
            "date_window": {"start_date": "Previous Close", "effective_end_date": "2026-06-08"},
            "rows": pd.DataFrame(
                [
                    {
                        "Group": "Technology",
                        "Symbols": 80,
                        "Positive Symbols": 56,
                        "Positive Symbol Share %": 70.0,
                        "Market Cap Weighted Return %": 1.8,
                        "Equal Weight Return %": 0.8,
                        "Top 3 Positive Share %": 72.0,
                        "Top Symbol": "NVDA",
                        "Top Symbol Return %": 5.3,
                    },
                    {
                        "Group": "Utilities",
                        "Symbols": 30,
                        "Positive Symbols": 15,
                        "Positive Symbol Share %": 50.0,
                        "Market Cap Weighted Return %": -0.4,
                        "Equal Weight Return %": -0.2,
                        "Top 3 Positive Share %": 40.0,
                        "Top Symbol": "NEE",
                        "Top Symbol Return %": 1.1,
                    },
                ]
            ),
        }

        model = build_overview_breadth_heatmap_summary(snapshot)

        self.assertEqual(model["schema_version"], "overview_breadth_heatmap_summary_v1")
        self.assertEqual(model["status"], "OK")
        self.assertEqual(model["coverage"]["group_count"], 2)
        self.assertEqual(model["summary"]["participation_label"], "mixed")
        self.assertEqual(model["summary"]["concentration_label"], "concentrated")
        self.assertEqual(model["summary"]["leader"], "Technology")
        self.assertEqual(model["cards"][0]["title"], "Participation")
        self.assertEqual(model["heatmap_rows"][0]["group"], "Technology")
        self.assertEqual(model["heatmap_rows"][0]["tone"], "positive")
        self.assertIn("not a trading action", model["boundary_note"])

    def test_overview_breadth_heatmap_summary_keeps_full_canonical_sector_map(self) -> None:
        from app.services.overview_market_intelligence import build_overview_breadth_heatmap_summary
        from app.web.overview_ui_components import _sector_pressure_map_html

        sector_names = [
            "Communication Services",
            "Consumer Cyclical",
            "Consumer Defensive",
            "Energy",
            "Financials",
            "Financial Services",
            "Healthcare",
            "Industrials",
            "Basic Materials",
            "Real Estate",
            "Technology",
            "Utilities",
        ]
        rows = pd.DataFrame(
            [
                {
                    "Rank": index,
                    "Group": sector,
                    "Symbols": 20,
                    "Positive Symbols": 12,
                    "Positive Symbol Share %": 60.0,
                    "Market Cap Weighted Return %": 3.0 - (index * 0.1),
                    "Equal Weight Return %": 2.0 - (index * 0.05),
                    "Top 3 Positive Share %": 25.0,
                    "Top Symbol": f"S{index}",
                    "Top Symbol Return %": 4.0,
                }
                for index, sector in enumerate(sector_names, start=1)
            ]
        )

        model = build_overview_breadth_heatmap_summary({"status": "OK", "coverage": {}, "rows": rows}, limit=None)
        groups = [row["group"] for row in model["heatmap_rows"]]
        html = _sector_pressure_map_html(model)

        self.assertEqual(len(groups), 11)
        self.assertEqual(len(set(groups)), 11)
        self.assertIn("Consumer Cyclical", groups)
        self.assertIn("Financial Services", groups)
        self.assertNotIn("Financials", groups)
        self.assertEqual(html.count("ov-sector-pressure-tile"), 11)

    def test_overview_macro_week_lane_clusters_near_events_without_signal_language(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_week_lane

        snapshot = {
            "status": "OK",
            "coverage": {
                "event_count": 4,
                "official_count": 2,
                "estimate_count": 1,
                "latest_collected_at": "2026-06-08 01:30",
            },
            "rows": pd.DataFrame(
                [
                    {
                        "Date": "2026-06-10",
                        "Days Until": 2,
                        "Type": "MACRO_CPI",
                        "Title": "CPI: Consumer Price Index",
                        "Source Type": "Official",
                        "Validation": "Official",
                        "Freshness": "Official",
                        "Quality Action": "No action",
                        "Importance": "High",
                    },
                    {
                        "Date": "2026-06-12",
                        "Days Until": 4,
                        "Type": "EARNINGS",
                        "Symbol": "AAPL",
                        "Title": "AAPL Earnings Release",
                        "Source Type": "Estimate",
                        "Validation": "Estimate",
                        "Freshness": "Stale estimate",
                        "Quality Action": "Refresh Earnings Calendar",
                        "Importance": "Medium",
                    },
                    {
                        "Date": "2026-06-24",
                        "Days Until": 16,
                        "Type": "MACRO_GDP",
                        "Title": "GDP release",
                        "Source Type": "Official",
                        "Validation": "Official",
                        "Freshness": "Official",
                        "Quality Action": "No action",
                        "Importance": "High",
                    },
                ]
            ),
        }

        model = build_overview_macro_week_lane(snapshot, horizon_days=14)

        self.assertEqual(model["schema_version"], "overview_macro_week_lane_v2")
        self.assertEqual(model["status"], "REVIEW")
        self.assertEqual(model["summary"]["near_event_count"], 2)
        self.assertEqual(model["summary"]["next_event_label"], "MACRO_CPI in 2d")
        self.assertEqual(model["clusters"]["CPI"]["count"], 1)
        self.assertEqual(model["clusters"]["Earnings"]["count"], 1)
        self.assertEqual(model["items"][0]["type"], "MACRO_CPI")
        self.assertNotIn("PASS", model["boundary_note"])
        self.assertIn("context 전용", model["boundary_note"])
        self.assertIn("거래 실행", model["boundary_note"])

    def test_overview_macro_week_lane_splits_recent_and_upcoming_major_macro_events(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_week_lane

        snapshot = {
            "status": "OK",
            "coverage": {
                "event_count": 5,
                "official_count": 3,
                "estimate_count": 2,
                "latest_collected_at": "2026-06-12 01:30",
            },
            "rows": pd.DataFrame(
                [
                    {
                        "Date": "2026-06-10",
                        "Days Until": -2,
                        "Type": "MACRO_CPI",
                        "Title": "CPI: Consumer Price Index for May 2026",
                        "Source Type": "Official",
                        "Validation": "Official",
                        "Freshness": "Official",
                        "Quality Action": "No action",
                        "Importance": "High",
                    },
                    {
                        "Date": "2026-06-11",
                        "Days Until": -1,
                        "Type": "EARNINGS",
                        "Symbol": "ORCL",
                        "Title": "ORCL Earnings Release",
                        "Source Type": "Provider Estimate",
                        "Validation": "Not confirmed",
                        "Freshness": "Current estimate",
                        "Quality Action": "Treat as unconfirmed; retry later or inspect source",
                        "Importance": "Medium",
                    },
                    {
                        "Date": "2026-06-17",
                        "Days Until": 5,
                        "Type": "FOMC_MEETING",
                        "Title": "FOMC Meeting: June 16-17*, 2026",
                        "Source Type": "Official",
                        "Validation": "Official",
                        "Freshness": "Official",
                        "Quality Action": "No action",
                        "Importance": "High",
                    },
                    {
                        "Date": "2026-06-23",
                        "Days Until": 11,
                        "Type": "EARNINGS",
                        "Symbol": "CCL",
                        "Title": "CCL Earnings Release",
                        "Source Type": "Provider Estimate",
                        "Validation": "Cross-checked",
                        "Freshness": "Current estimate",
                        "Quality Action": "No action",
                        "Importance": "Medium",
                    },
                    {
                        "Date": "2026-06-25",
                        "Days Until": 13,
                        "Type": "MACRO_GDP",
                        "Title": "GDP: Third Estimate",
                        "Source Type": "Official",
                        "Validation": "Official",
                        "Freshness": "Official",
                        "Quality Action": "No action",
                        "Importance": "High",
                    },
                ]
            ),
        }

        model = build_overview_macro_week_lane(snapshot, horizon_days=14)

        self.assertEqual(model["schema_version"], "overview_macro_week_lane_v2")
        self.assertEqual(model["summary"]["recent_event_count"], 1)
        self.assertEqual(model["summary"]["upcoming_event_count"], 3)
        self.assertIn("recent major event", model["summary"]["headline"])
        self.assertEqual(model["recent_items"][0]["type"], "MACRO_CPI")
        self.assertEqual(model["recent_items"][0]["window"], "recent")
        self.assertEqual(model["upcoming_items"][0]["type"], "FOMC_MEETING")
        self.assertEqual(model["upcoming_items"][0]["window"], "upcoming")
        self.assertEqual(model["items"][0]["type"], "MACRO_CPI")
        self.assertEqual(model["items"][1]["type"], "FOMC_MEETING")

    def test_market_events_snapshot_defaults_to_recent_plus_upcoming_and_prioritizes_major_macro(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        captured: dict[str, object] = {}

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, sql
            captured["params"] = list(params or [])
            return [
                {
                    "event_date": "2026-06-10",
                    "event_type": "MACRO_CPI",
                    "symbol": None,
                    "title": "CPI: Consumer Price Index for May 2026",
                    "source": "bureau_labor_statistics_release_schedule",
                    "source_type": "official",
                    "validation_status": "official",
                    "event_status": "active",
                    "source_url": "https://www.bls.gov/schedule/2026/",
                    "confidence": 0.95,
                    "collected_at": "2026-06-11 23:45:00",
                },
                {
                    "event_date": "2026-06-11",
                    "event_type": "EARNINGS",
                    "symbol": "ORCL",
                    "title": "ORCL Earnings Release",
                    "source": "yfinance_calendar",
                    "source_type": "provider_estimate",
                    "validation_status": "not_confirmed",
                    "event_status": "active",
                    "source_url": "https://finance.yahoo.com/quote/ORCL/analysis",
                    "confidence": 0.6,
                    "collected_at": "2026-06-11 23:44:00",
                },
                {
                    "event_date": "2026-06-17",
                    "event_type": "FOMC_MEETING",
                    "symbol": None,
                    "title": "FOMC Meeting: June 16-17*, 2026",
                    "source": "federal_reserve_fomc_calendar",
                    "source_type": "official",
                    "validation_status": "official",
                    "event_status": "active",
                    "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                    "confidence": 1.0,
                    "collected_at": "2026-06-11 23:44:00",
                },
                {
                    "event_date": "2026-06-23",
                    "event_type": "EARNINGS",
                    "symbol": "CCL",
                    "title": "CCL Earnings Release",
                    "source": "yfinance_calendar",
                    "source_type": "provider_estimate",
                    "validation_status": "cross_checked",
                    "event_status": "active",
                    "source_url": "https://finance.yahoo.com/quote/CCL/analysis",
                    "confidence": 0.75,
                    "collected_at": "2026-06-11 23:44:00",
                },
            ]

        snapshot = build_market_events_snapshot(
            event_type=None,
            today=date(2026, 6, 12),
            horizon_days=14,
            limit=100,
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["date_window"]["start_date"], "2026-06-05")
        self.assertEqual(snapshot["date_window"]["end_date"], "2026-06-26")
        self.assertIn("2026-06-05", captured["params"])
        self.assertEqual(snapshot["coverage"]["recent_event_count"], 2)
        self.assertEqual(snapshot["coverage"]["upcoming_event_count"], 2)
        self.assertEqual(snapshot["coverage"]["recent_high_importance_count"], 1)
        self.assertEqual(snapshot["coverage"]["upcoming_high_importance_count"], 1)
        self.assertEqual(snapshot["coverage"]["next_event_date"], "2026-06-17")
        self.assertEqual(snapshot["coverage"]["latest_recent_event_date"], "2026-06-10")
        self.assertEqual(list(snapshot["rows"]["Type"][:2]), ["MACRO_CPI", "FOMC_MEETING"])
        self.assertEqual(snapshot["rows"].iloc[0]["Window"], "Recent")
        self.assertEqual(snapshot["rows"].iloc[1]["Window"], "Upcoming")

    def test_overview_source_confidence_catalog_surfaces_provider_caveats_and_review_items(self) -> None:
        from app.services.overview_market_intelligence import build_overview_source_confidence_catalog

        model = build_overview_source_confidence_catalog(
            market_movers_snapshot={
                "status": "OK",
                "coverage": {
                    "returnable_count": 503,
                    "universe_count": 503,
                    "snapshot_time_utc": "2026-06-08 14:00",
                    "refresh_state": {"label": "Stale", "detail": "2962m old", "recommended_action": "Run Update Daily Snapshot."},
                },
                "rows": pd.DataFrame([{"Symbol": "NVDA"}]),
            },
            group_leadership_snapshot={
                "status": "OK",
                "coverage": {"returnable_count": 503, "universe_count": 503, "effective_end_date": "2026-06-08"},
                "rows": pd.DataFrame([{"Group": "Technology"}]),
            },
            futures_macro_snapshot={
                "status": "OK",
                "coverage": {"standardized_count": 14, "symbol_count": 16, "latest_date": "2026-06-07"},
            },
            sentiment_snapshot={
                "status": "OK",
                "analysis": {"data_confidence": {"status": "Review", "detail": "1 stale sentiment source"}},
                "coverage": {"cnn_score": 54.7, "aaii_bull_bear_spread": -0.7},
            },
            events_snapshot={
                "status": "OK",
                "coverage": {
                    "event_count": 12,
                    "official_count": 5,
                    "estimate_count": 7,
                    "needs_review_count": 2,
                    "stale_estimate_count": 1,
                    "latest_collected_at": "2026-06-08 01:30",
                },
                "rows": pd.DataFrame([{"Type": "EARNINGS", "Freshness": "Stale estimate"}]),
            },
            collection_ops_snapshot={
                "status": "REVIEW",
                "coverage": {"ok_count": 3, "due_count": 1, "stale_count": 1, "partial_count": 0, "missing_count": 0, "failed_count": 0},
                "rows": pd.DataFrame(
                    [
                        {"Area": "S&P 500 Daily Snapshot", "Status": "Due", "Data Freshness": "8m old", "Next Action": "Refresh S&P 500 daily snapshot."},
                        {"Area": "Market Sentiment", "Status": "OK", "Data Freshness": "1d old", "Next Action": "No action needed."},
                    ]
                ),
            },
        )

        self.assertEqual(model["schema_version"], "overview_source_confidence_catalog_v1")
        self.assertEqual(model["status"], "REVIEW")
        self.assertEqual(model["summary"]["review_count"], 2)
        self.assertEqual(model["summary"]["reference_count"], 2)
        self.assertEqual(model["items"][0]["id"], "prices")
        self.assertEqual(model["items"][0]["status"], "REVIEW")
        self.assertTrue(model["items"][0]["counts_for_status"])
        self.assertEqual(model["items"][0]["source_role"], "brief_source")
        self.assertIn("가격 맥락의 신뢰도 주의점", model["items"][0]["next_check"])
        self.assertEqual(model["items"][2]["id"], "futures")
        self.assertIn("무료 선물 provider", model["items"][2]["caveat"])
        self.assertEqual(model["items"][3]["id"], "sentiment")
        self.assertEqual(model["items"][3]["status"], "REVIEW")
        self.assertEqual(model["items"][4]["id"], "events")
        self.assertEqual(model["items"][4]["status"], "REFERENCE_LIMIT")
        self.assertEqual(model["items"][4]["status_label"], "참고 제한")
        self.assertFalse(model["items"][4]["counts_for_status"])
        self.assertEqual(model["items"][4]["source_role"], "reference_context")
        self.assertEqual(model["items"][4]["actionability"], "not_actionable")
        self.assertIn("추정 일정 확인", model["items"][4]["detail"])
        self.assertIn("stale estimate", model["items"][4]["detail"])
        self.assertEqual(model["items"][5]["id"], "data_health")
        self.assertEqual(model["items"][5]["status"], "META")
        self.assertEqual(model["items"][5]["status_label"], "관리 메타")
        self.assertFalse(model["items"][5]["counts_for_status"])
        self.assertEqual(model["items"][5]["source_role"], "management_meta")
        next_targets = [item["target_tab"] for item in model["next_checks"]]
        self.assertNotIn("Data Health", next_targets)
        self.assertNotIn("Events", next_targets)
        self.assertIn("context 전용", model["boundary_note"])

    def test_overview_source_confidence_does_not_mark_events_and_data_health_meta_as_unresolved(self) -> None:
        from app.services.overview_market_intelligence import build_overview_source_confidence_catalog

        model = build_overview_source_confidence_catalog(
            market_movers_snapshot={
                "status": "OK",
                "coverage": {"returnable_count": 503, "universe_count": 503, "snapshot_time_utc": "2026-06-20 12:35"},
                "rows": pd.DataFrame([{"Symbol": "SNDK"}]),
            },
            group_leadership_snapshot={
                "status": "OK",
                "coverage": {"returnable_count": 503, "universe_count": 503, "effective_end_date": "2026-06-20"},
                "rows": pd.DataFrame([{"Group": "Technology"}]),
            },
            futures_macro_snapshot={
                "status": "OK",
                "coverage": {"standardized_count": 16, "symbol_count": 16, "latest_date": "2026-06-20"},
            },
            sentiment_snapshot={
                "status": "OK",
                "analysis": {"data_confidence": {"status": "High", "detail": "fresh"}},
                "coverage": {"cnn_score": 55, "aaii_bull_bear_spread": 1.2},
            },
            events_snapshot={
                "status": "OK",
                "coverage": {
                    "event_count": 71,
                    "official_count": 4,
                    "estimate_count": 67,
                    "needs_review_count": 67,
                    "stale_estimate_count": 3,
                    "latest_collected_at": "2026-06-20 12:36",
                },
                "rows": pd.DataFrame([{"Type": "EARNINGS", "Source Type": "Estimate", "Freshness": "Stale estimate"}]),
            },
            collection_ops_snapshot={
                "status": "REVIEW",
                "coverage": {"ok_count": 3, "due_count": 0, "stale_count": 2, "partial_count": 0, "missing_count": 0, "failed_count": 0},
                "rows": pd.DataFrame(
                    [
                        {"Area": "Futures Monitor 1m OHLCV", "Status": "Stale", "Data Freshness": "2006m old"},
                    ]
                ),
            },
        )

        self.assertEqual(model["status"], "OK")
        self.assertEqual(model["status_label"], "자료 정상 · 참고 제한")
        self.assertEqual(model["summary"]["review_count"], 0)
        self.assertEqual(model["summary"]["reference_count"], 2)
        self.assertEqual(model["next_checks"], [])
        event_item = next(item for item in model["items"] if item["id"] == "events")
        data_item = next(item for item in model["items"] if item["id"] == "data_health")
        self.assertEqual(event_item["status_label"], "참고 제한")
        self.assertEqual(data_item["status_label"], "관리 메타")
        self.assertFalse(event_item["counts_for_status"])
        self.assertFalse(data_item["counts_for_status"])

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
        self.assertEqual(snapshot["rows"].iloc[0]["Days Until"], 20)
        self.assertEqual(snapshot["rows"].iloc[0]["Importance"], "High")
        self.assertEqual(snapshot["rows"].iloc[0]["Focus"], "Next 30D")
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
        self.assertEqual(snapshot["coverage"]["estimate_only_count"], 1)
        self.assertEqual(snapshot["coverage"]["action_required_count"], 1)
        self.assertEqual(snapshot["coverage"]["high_importance_count"], 2)
        self.assertEqual(snapshot["coverage"]["needs_review_count"], 1)
        self.assertEqual(snapshot["coverage"]["this_week_count"], 0)
        self.assertEqual(snapshot["coverage"]["next_30d_count"], 1)
        self.assertEqual(snapshot["coverage"]["stale_estimate_count"], 0)
        self.assertEqual(set(snapshot["rows"]["Type"]), {"FOMC_MEETING", "EARNINGS"})
        earnings_row = snapshot["rows"][snapshot["rows"]["Type"] == "EARNINGS"].iloc[0]
        self.assertEqual(earnings_row["Importance"], "Medium")
        self.assertEqual(earnings_row["Focus"], "Needs Review")
        self.assertEqual(earnings_row["Source Type"], "Provider Estimate")
        self.assertEqual(earnings_row["Freshness"], "Current estimate")
        self.assertEqual(earnings_row["Quality Action"], "Enable cross-check or refresh closer to date")

    def test_market_events_snapshot_macro_filter_reads_macro_prefix_rows(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name
            self.assertIn("event_type LIKE %s", sql)
            self.assertIn("MACRO_%", params or [])
            return [
                {
                    "event_date": "2026-06-10",
                    "event_type": "MACRO_CPI",
                    "symbol": None,
                    "title": "CPI: Consumer Price Index for May 2026",
                    "source": "bureau_labor_statistics_release_schedule",
                    "source_type": "official",
                    "validation_status": "official",
                    "event_status": "active",
                    "source_url": "https://www.bls.gov/schedule/2026/",
                    "confidence": 0.95,
                    "collected_at": "2026-05-28 04:00:00",
                },
                {
                    "event_date": "2026-06-25",
                    "event_type": "MACRO_GDP",
                    "symbol": None,
                    "title": "GDP: Gross Domestic Product, 1st Quarter 2026",
                    "source": "bureau_economic_analysis_release_schedule",
                    "source_type": "official",
                    "validation_status": "official",
                    "event_status": "active",
                    "source_url": "https://www.bea.gov/index.php/news/schedule/full",
                    "confidence": 0.95,
                    "collected_at": "2026-05-28 04:00:00",
                },
            ]

        snapshot = build_market_events_snapshot(
            event_type="MACRO",
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["event_type"], "MACRO")
        self.assertEqual(snapshot["coverage"]["event_count"], 2)
        self.assertEqual(snapshot["coverage"]["official_count"], 2)
        self.assertEqual(set(snapshot["rows"]["Type"]), {"MACRO_CPI", "MACRO_GDP"})

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

    def test_collection_ops_snapshot_combines_db_freshness_and_run_history(self) -> None:
        from app.services.overview_market_intelligence import build_collection_ops_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM market_intraday_snapshot" in sql:
                return [
                    {"universe_code": "SP500", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                    {"universe_code": "TOP1000", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                ]
            if "FROM futures_ohlcv" in sql:
                return [
                    {
                        "latest_candle_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        "active_symbols": 4,
                        "candle_rows": 240,
                    }
                ]
            if "FROM market_universe_member" in sql:
                return [
                    {
                        "universe_code": "SP500",
                        "active_symbols": 503,
                        "latest_collected_at": "2026-05-28 01:00:00",
                        "latest_as_of_date": "2026-05-28",
                    }
                ]
            if "FROM market_event_calendar" in sql:
                return [
                    {
                        "event_type": "FOMC_MEETING",
                        "active_events": 12,
                        "future_events": 12,
                        "next_event_date": "2026-06-17",
                        "latest_collected_at": "2026-05-28 02:00:00",
                    },
                    {
                        "event_type": "EARNINGS",
                        "active_events": 3,
                        "future_events": 3,
                        "next_event_date": "2026-07-30",
                        "latest_collected_at": "2026-05-28 03:00:00",
                    },
                ]
            return []

        snapshot = build_collection_ops_snapshot(
            today=date(2026, 5, 28),
            query_fn=query_fn,
            history_rows=[
                {
                    "job_name": "collect_sp500_universe",
                    "status": "success",
                    "finished_at": "2026-05-28 01:01:00",
                    "rows_written": 503,
                    "symbols_processed": 503,
                    "failed_symbols": [],
                    "duration_sec": 1.2,
                    "message": "S&P 500 universe collection completed.",
                },
                {
                    "job_name": "collect_sp500_universe",
                    "status": "success",
                    "finished_at": "2026-05-28 01:05:00",
                    "rows_written": 503,
                    "symbols_processed": 503,
                    "failed_symbols": [],
                    "duration_sec": 1.1,
                    "message": "S&P 500 universe scheduled collection completed.",
                    "run_metadata": {"execution_mode": "scheduled"},
                },
                {
                    "job_name": "collect_sp500_intraday_snapshot",
                    "status": "success",
                    "finished_at": "2026-05-28 04:05:00",
                    "rows_written": 503,
                    "symbols_processed": 503,
                    "failed_symbols": [],
                    "duration_sec": 5.1,
                    "message": "S&P 500 browser auto snapshot completed.",
                    "run_metadata": {
                        "execution_mode": "browser_auto",
                        "automation_profile": "browser_safe",
                    },
                },
                {
                    "job_name": "collect_earnings_calendar",
                    "status": "partial_success",
                    "finished_at": "2026-05-28 03:01:00",
                    "rows_written": 2,
                    "symbols_processed": 2,
                    "failed_symbols": ["AAA"],
                    "duration_sec": 2.5,
                    "message": "Earnings calendar completed with missing symbols.",
                },
            ],
        )

        rows = snapshot["rows"]
        self.assertEqual(snapshot["status"], "REVIEW")
        self.assertEqual(snapshot["coverage"]["partial_count"], 1)
        universe_row = rows[rows["Area"] == "S&P 500 Universe"].iloc[0]
        self.assertEqual(universe_row["Status"], "OK")
        self.assertEqual(universe_row["Rows"], 503)
        self.assertEqual(universe_row["Last Auto Run"], "2026-05-28 01:05")
        self.assertEqual(universe_row["Auto Source"], "Scheduled")
        self.assertEqual(universe_row["Last Manual Run"], "2026-05-28 01:01")
        self.assertEqual(universe_row["Next Auto Due"], "2026-05-29 01:05")
        sp500_intraday_row = rows[rows["Area"] == "S&P 500 Daily Snapshot"].iloc[0]
        self.assertEqual(sp500_intraday_row["Last Auto Run"], "2026-05-28 04:05")
        self.assertEqual(sp500_intraday_row["Auto Source"], "Browser Auto")
        self.assertEqual(sp500_intraday_row["Next Auto Due"], "2026-05-28 04:10")
        futures_row = rows[rows["Area"] == "Futures Monitor 1m OHLCV"].iloc[0]
        self.assertEqual(futures_row["Status"], "OK")
        self.assertIn("4 symbols", futures_row["Data Freshness"])
        self.assertEqual(snapshot["coverage"]["latest_auto_at"], "2026-05-28 04:05")
        earnings_row = rows[rows["Area"] == "Earnings Calendar"].iloc[0]
        self.assertEqual(earnings_row["Status"], "Partial")
        self.assertEqual(earnings_row["Failed"], 1)
        self.assertEqual(earnings_row["Failure Streak"], 1)
        self.assertIn("Inspect failed symbols", earnings_row["Next Action"])

    def test_collection_ops_snapshot_supports_legacy_event_calendar_schema(self) -> None:
        from app.services.overview_market_intelligence import build_collection_ops_snapshot

        event_query_count = 0

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            nonlocal event_query_count
            del db_name, params
            if "FROM market_intraday_snapshot" in sql:
                return [
                    {"universe_code": "SP500", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                    {"universe_code": "TOP1000", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                    {"universe_code": "TOP2000", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                ]
            if "FROM futures_ohlcv" in sql:
                return [
                    {
                        "latest_candle_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        "active_symbols": 4,
                        "candle_rows": 240,
                    }
                ]
            if "FROM market_universe_member" in sql:
                return [
                    {
                        "universe_code": "SP500",
                        "active_symbols": 503,
                        "latest_collected_at": "2026-05-28 01:00:00",
                        "latest_as_of_date": "2026-05-28",
                    }
                ]
            if "FROM market_event_calendar" in sql:
                event_query_count += 1
                if "event_status" in sql:
                    raise RuntimeError("Unknown column 'event_status'")
                return [
                    {
                        "event_type": "FOMC_MEETING",
                        "active_events": 12,
                        "future_events": 12,
                        "next_event_date": "2026-06-17",
                        "latest_collected_at": "2026-05-28 02:00:00",
                    }
                ]
            return []

        snapshot = build_collection_ops_snapshot(today=date(2026, 5, 28), query_fn=query_fn)

        self.assertEqual(event_query_count, 2)
        fomc_row = snapshot["rows"][snapshot["rows"]["Area"] == "FOMC Calendar"].iloc[0]
        self.assertEqual(fomc_row["Status"], "OK")
        self.assertIn("next 2026-06-17", fomc_row["Data Freshness"])

    def test_collection_ops_snapshot_marks_macro_calendar_due_when_some_macro_types_missing(self) -> None:
        from app.services.overview_market_intelligence import build_collection_ops_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM market_intraday_snapshot" in sql:
                return []
            if "FROM futures_ohlcv" in sql:
                return []
            if "FROM market_universe_member" in sql:
                return []
            if "FROM market_event_calendar" in sql:
                return [
                    {
                        "event_type": "MACRO_GDP",
                        "active_events": 2,
                        "future_events": 2,
                        "next_event_date": "2026-06-25",
                        "latest_collected_at": "2026-05-28 04:00:00",
                    }
                ]
            return []

        snapshot = build_collection_ops_snapshot(today=date(2026, 5, 28), query_fn=query_fn)

        macro_row = snapshot["rows"][snapshot["rows"]["Area"] == "Macro Calendar"].iloc[0]
        self.assertEqual(macro_row["Status"], "Due")
        self.assertIn("covered 1/4", macro_row["Data Freshness"])

    def test_market_sentiment_snapshot_summarizes_cnn_and_aaii_context(self) -> None:
        from app.services.overview_market_intelligence import build_market_sentiment_snapshot

        snapshot_rows = pd.DataFrame(
            [
                {
                    "series_id": "CNN_FEAR_GREED",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "CNN Fear & Greed Index",
                    "category": "sentiment_index",
                    "units": "score_0_100",
                    "value": 54.7,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "neutral", "previous_close": 54.0}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "AAII_BEARISH",
                    "observation_date": pd.Timestamp("2026-06-03"),
                    "source": "aaii_sentiment_survey",
                    "source_type": "official",
                    "source_mode": "html",
                    "series_name": "AAII Bearish Sentiment",
                    "category": "sentiment_survey",
                    "units": "percent",
                    "value": 37.0,
                    "coverage_status": "actual",
                    "missing_fields_json": "{}",
                    "collected_at": pd.Timestamp("2026-06-04 14:50:00"),
                    "staleness_days": 2,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "AAII_BULL_BEAR_SPREAD",
                    "observation_date": pd.Timestamp("2026-06-03"),
                    "source": "aaii_sentiment_survey",
                    "source_type": "official",
                    "source_mode": "html",
                    "series_name": "AAII Bull-Bear Spread",
                    "category": "sentiment_survey",
                    "units": "percentage_point",
                    "value": -0.7,
                    "coverage_status": "actual",
                    "missing_fields_json": "{}",
                    "collected_at": pd.Timestamp("2026-06-04 14:50:00"),
                    "staleness_days": 2,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "CNN_FNG_MARKET_MOMENTUM_SP500",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "Market Momentum",
                    "category": "sentiment_component",
                    "units": "score_0_100",
                    "value": 93.8,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "extreme greed"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "CNN_FNG_STOCK_PRICE_BREADTH",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "Stock Price Breadth",
                    "category": "sentiment_component",
                    "units": "score_0_100",
                    "value": 31.4,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "fear"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "CNN_FNG_STOCK_PRICE_STRENGTH",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "Stock Price Strength",
                    "category": "sentiment_component",
                    "units": "score_0_100",
                    "value": 33.0,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "fear"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "CNN_FNG_PUT_CALL_OPTIONS",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "Put / Call Options",
                    "category": "sentiment_component",
                    "units": "score_0_100",
                    "value": 96.6,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "extreme greed"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "CNN_FNG_MARKET_VOLATILITY_VIX",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "Market Volatility",
                    "category": "sentiment_component",
                    "units": "score_0_100",
                    "value": 50.0,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "neutral"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "CNN_FNG_JUNK_BOND_DEMAND",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "Junk Bond Demand",
                    "category": "sentiment_component",
                    "units": "score_0_100",
                    "value": 6.6,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "extreme fear"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
                {
                    "series_id": "CNN_FNG_SAFE_HAVEN_DEMAND",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "source_type": "official",
                    "source_mode": "json",
                    "series_name": "Safe Haven Demand",
                    "category": "sentiment_component",
                    "units": "score_0_100",
                    "value": 71.8,
                    "coverage_status": "actual",
                    "missing_fields_json": json.dumps({"rating": "greed"}),
                    "collected_at": pd.Timestamp("2026-06-04 23:10:00"),
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                },
            ]
        )
        history_rows = pd.DataFrame(
            [
                {
                    "series_id": "CNN_FEAR_GREED",
                    "observation_date": pd.Timestamp("2026-06-03"),
                    "source": "cnn_fear_greed",
                    "value": 54.0,
                    "category": "sentiment_index",
                },
                {
                    "series_id": "CNN_FEAR_GREED",
                    "observation_date": pd.Timestamp("2026-06-04"),
                    "source": "cnn_fear_greed",
                    "value": 54.7,
                    "category": "sentiment_index",
                },
                {
                    "series_id": "AAII_BEARISH",
                    "observation_date": pd.Timestamp("2026-06-03"),
                    "source": "aaii_sentiment_survey",
                    "value": 37.0,
                    "category": "sentiment_survey",
                },
            ]
        )

        snapshot = build_market_sentiment_snapshot(
            snapshot_rows=snapshot_rows,
            history_rows=history_rows,
            today=date(2026, 6, 5),
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["cnn_score"], 54.7)
        self.assertEqual(snapshot["coverage"]["cnn_rating"], "neutral")
        self.assertEqual(snapshot["coverage"]["aaii_bearish"], 37.0)
        self.assertEqual(snapshot["coverage"]["aaii_bull_bear_spread"], -0.7)
        self.assertEqual(snapshot["rows"].iloc[0]["Series"], "CNN Fear & Greed")
        self.assertIn("Stock Price Breadth", set(snapshot["component_rows"]["Series"]))
        self.assertFalse(snapshot["history_rows"].empty)
        analysis = snapshot["analysis"]
        self.assertEqual(analysis["phase"], "MIXED_NEUTRAL")
        self.assertEqual(analysis["phase_label"], "혼합 중립")
        self.assertIn("내부는 엇갈린", analysis["headline"])
        self.assertEqual(analysis["data_confidence"]["status"], "High")
        self.assertEqual(analysis["driver_summary"]["greed_count"], 3)
        self.assertEqual(analysis["driver_summary"]["fear_count"], 3)
        self.assertEqual(analysis["driver_summary"]["neutral_count"], 1)
        self.assertEqual(
            [step["title"] for step in analysis["analysis_steps"]],
            ["지금 결론", "왜 이렇게 보나", "강한 신호", "약한 신호", "그래서 어떻게 보나", "다음 확인"],
        )
        self.assertIn("중립", analysis["analysis_steps"][0]["status"])
        self.assertIn("지수는 버티지만", analysis["analysis_steps"][4]["detail"])
        explanations = analysis["component_explanations"]
        self.assertEqual(len(explanations), 7)
        momentum = next(item for item in explanations if item["series"] == "Market Momentum")
        self.assertIn("S&P 500", momentum["what_it_checks"])
        self.assertIn("지수 추세", momentum["current_reading"])
        breadth = next(item for item in explanations if item["series"] == "Stock Price Breadth")
        self.assertIn("시장 폭", breadth["current_reading"])
        self.assertIn("Market Movers", analysis["next_checks"][0]["target"])

    def test_collection_ops_snapshot_tracks_market_sentiment_freshness(self) -> None:
        from app.services.overview_market_intelligence import build_collection_ops_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM market_intraday_snapshot" in sql:
                return []
            if "FROM futures_ohlcv" in sql:
                return []
            if "FROM market_universe_member" in sql:
                return []
            if "FROM market_event_calendar" in sql:
                return []
            if "FROM macro_series_observation" in sql:
                return [
                    {
                        "latest_observation_date": "2026-06-04",
                        "latest_collected_at": "2026-06-04 23:10:00",
                        "series_count": 2,
                    }
                ]
            return []

        snapshot = build_collection_ops_snapshot(
            today=date(2026, 6, 5),
            query_fn=query_fn,
            history_rows=[
                {
                    "job_name": "collect_market_sentiment",
                    "status": "success",
                    "finished_at": "2026-06-04 23:11:00",
                    "rows_written": 260,
                    "symbols_processed": 2,
                    "failed_symbols": [],
                    "duration_sec": 1.5,
                    "message": "Market sentiment collection completed.",
                }
            ],
        )

        sentiment_row = snapshot["rows"][snapshot["rows"]["Area"] == "Market Sentiment"].iloc[0]
        self.assertEqual(sentiment_row["Status"], "OK")
        self.assertEqual(sentiment_row["Rows"], 260)
        self.assertIn("latest 2026-06-04", sentiment_row["Data Freshness"])

    def test_overview_data_health_handoff_ranks_problem_rows_and_points_to_collection_surfaces(self) -> None:
        from app.services.overview_market_intelligence import build_overview_data_health_ingestion_handoff

        handoff = build_overview_data_health_ingestion_handoff(
            {
                "status": "REVIEW",
                "coverage": {
                    "ok_count": 1,
                    "due_count": 1,
                    "stale_count": 1,
                    "partial_count": 1,
                    "missing_count": 1,
                    "failed_count": 1,
                },
                "rows": pd.DataFrame(
                    [
                        {
                            "Area": "S&P 500 Daily Snapshot",
                            "Status": "Due",
                            "Data Freshness": "8m old",
                            "Failure Streak": 0,
                            "Next Action": "Refresh S&P 500 daily snapshot before using daily movers.",
                        },
                        {
                            "Area": "FOMC Calendar",
                            "Status": "Failed",
                            "Data Freshness": "45d old; next 2026-06-17",
                            "Failure Streak": 2,
                            "Last Issue": "2026-06-08 09:30",
                            "Next Action": "Open run history details and rerun after checking the failure message.",
                        },
                        {
                            "Area": "Macro Calendar",
                            "Status": "Missing",
                            "Data Freshness": "No future MACRO rows",
                            "Failure Streak": 0,
                            "Next Action": "Run Refresh Macro Calendar or import the BLS .ics file.",
                        },
                        {
                            "Area": "Futures Monitor 1m OHLCV",
                            "Status": "Stale",
                            "Data Freshness": "64m old; 16 symbols",
                            "Failure Streak": 0,
                            "Next Action": "Refresh before using futures context.",
                        },
                        {
                            "Area": "Earnings Calendar",
                            "Status": "Partial",
                            "Data Freshness": "0d old; covered 1/2",
                            "Failed": 7,
                            "Failure Streak": 1,
                            "Next Action": "Inspect failed symbols, then rerun a bounded collection.",
                        },
                        {
                            "Area": "Market Sentiment",
                            "Status": "OK",
                            "Data Freshness": "1d old; latest 2026-06-04; 2/5 series",
                            "Next Action": "No action needed.",
                        },
                    ]
                ),
            },
            limit=4,
        )

        self.assertEqual(handoff["schema_version"], "overview_data_health_ingestion_handoff_v1")
        self.assertEqual(handoff["status"], "REVIEW")
        self.assertEqual(handoff["summary"]["review_count"], 5)
        self.assertEqual(handoff["summary"]["top_priority"], "FOMC Calendar")
        self.assertEqual(handoff["summary"]["next_target_surface"], "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > FOMC 일정")
        self.assertEqual([item["area"] for item in handoff["priority_items"]], ["FOMC Calendar", "Macro Calendar", "Futures Monitor 1m OHLCV", "Earnings Calendar"])
        self.assertEqual(handoff["priority_items"][0]["status"], "Failed")
        self.assertEqual(handoff["priority_items"][0]["severity"], "critical")
        self.assertIn("Failure streak 2", handoff["priority_items"][0]["reason"])
        self.assertEqual(handoff["priority_items"][1]["target_surface"], "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 시장 이벤트 캘린더 수집 > 매크로 발표")
        self.assertEqual(handoff["priority_items"][2]["owner_surface"], "Workspace > Ingestion")
        self.assertEqual(handoff["priority_items"][2]["target_surface"], "Workspace > Ingestion > 일상 운영 / 검증 데이터 > 선물 OHLCV 수집")
        self.assertEqual(handoff["priority_items"][2]["alternate_surface"], "Workspace > Overview > Futures Monitor")
        self.assertEqual(handoff["counts"]["OK"], 1)
        self.assertEqual(handoff["counts"]["Failed"], 1)
        self.assertIn("read-only", handoff["boundary_note"].lower())
        self.assertIn("does not execute", handoff["boundary_note"].lower())

    def test_overview_macro_context_cockpit_can_omit_futures_macro_for_fast_entry(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        cockpit = build_overview_macro_context_cockpit(
            include_futures_macro=False,
            market_movers_snapshot={
                "status": "OK",
                "period_label": "Daily",
                "universe_label": "S&P 500",
                "coverage": {"returnable_count": 470, "universe_count": 503, "effective_end_date": "2026-06-05"},
                "rows": pd.DataFrame(
                    [{"Rank": 1, "Symbol": "NVDA", "Name": "NVIDIA Corp", "Return %": 4.2, "Sector": "Technology"}]
                ),
            },
            group_leadership_snapshot={
                "status": "OK",
                "period_label": "Daily",
                "coverage": {"returnable_count": 470, "universe_count": 503},
                "rows": pd.DataFrame(
                    [{"Rank": 1, "Group": "Technology", "Positive Symbol Share %": 82.0, "Market Cap Weighted Return %": 1.8}]
                ),
            },
            sentiment_snapshot={
                "status": "OK",
                "analysis": {
                    "phase_label": "혼합 중립",
                    "headline": "Fear & Greed is neutral while internals are mixed.",
                    "data_confidence": {"status": "High", "detail": "latest CNN / AAII rows"},
                },
                "coverage": {"cnn_score": 54.7, "cnn_rating": "neutral", "aaii_bull_bear_spread": -0.7},
            },
            events_snapshot={
                "status": "OK",
                "coverage": {"event_count": 1, "next_event_date": "2026-06-10", "needs_review_count": 0},
                "rows": pd.DataFrame(
                    [{"Date": "2026-06-10", "Type Label": "CPI", "Title": "CPI Release", "Days Until": 2, "Importance": "High"}]
                ),
            },
            collection_ops_snapshot={
                "status": "REVIEW",
                "coverage": {"ok_count": 2, "due_count": 1, "stale_count": 3, "partial_count": 1, "missing_count": 0, "failed_count": 0},
                "rows": pd.DataFrame(
                    [
                        {"Area": "Top1000 Daily Snapshot", "Status": "Partial", "Data Freshness": "11m old", "Next Action": "Refresh Top1000."},
                        {"Area": "Top2000 Daily Snapshot", "Status": "Stale", "Data Freshness": "37m old", "Next Action": "Refresh Top2000."},
                        {"Area": "Futures Monitor 1m OHLCV", "Status": "Stale", "Data Freshness": "47m old", "Next Action": "Refresh futures."},
                        {"Area": "Earnings Calendar", "Status": "Partial", "Data Freshness": "covered 1/2", "Next Action": "Inspect failed symbols."},
                    ]
                ),
            },
            direct_market_context_refresh_only=True,
        )

        self.assertEqual([card["id"] for card in cockpit["cards"]], ["movement", "breadth", "sentiment", "events", "data"])
        self.assertEqual(
            [item["label"] for item in cockpit["summary"]["rail"]],
            ["자료 상태", "Top Mover", "Breadth", "Next Event"],
        )
        self.assertEqual(
            [row["label"] for row in cockpit["brief_rows"]],
            ["무엇이 움직였나", "확산/집중인가", "이벤트 배경"],
        )
        self.assertEqual([cue["label"] for cue in cockpit["interpretation_cues"]], ["이벤트 압력", "심리 확인"])
        self.assertNotIn("Macro", [item["label"] for item in cockpit["summary"]["rail"]])
        self.assertNotIn("futures", [card["id"] for card in cockpit["cards"]])
        self.assertNotIn("futures", [item["id"] for item in cockpit["source_confidence"]["items"]])
        self.assertEqual(cockpit["refresh_plan"]["action_ids"], ["earnings_calendar"])
        refresh_sources = [item["source_area"] for item in cockpit["refresh_plan"]["items"]]
        self.assertNotIn("Top1000 Daily Snapshot", refresh_sources)
        self.assertNotIn("Top2000 Daily Snapshot", refresh_sources)
        self.assertNotIn("Futures Monitor 1m OHLCV", refresh_sources)
        summary_copy = f"{cockpit['summary']['headline']} {cockpit['summary']['detail']}"
        self.assertNotIn("macro", summary_copy.lower())
        self.assertNotIn("선물/매크로", summary_copy)

    def test_overview_macro_context_cockpit_summarizes_existing_context_snapshots(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        cockpit = build_overview_macro_context_cockpit(
            market_movers_snapshot={
                "status": "OK",
                "period_label": "Daily",
                "universe_label": "S&P 500",
                "coverage": {
                    "returnable_count": 470,
                    "universe_count": 503,
                    "effective_end_date": "2026-06-05",
                    "refresh_state": "Due",
                },
                "rows": pd.DataFrame(
                    [
                        {
                            "Rank": 1,
                            "Symbol": "NVDA",
                            "Name": "NVIDIA Corp",
                            "Return %": 4.2,
                            "Sector": "Technology",
                        }
                    ]
                ),
            },
            group_leadership_snapshot={
                "status": "OK",
                "period_label": "Daily",
                "coverage": {"returnable_count": 470, "universe_count": 503},
                "rows": pd.DataFrame(
                    [
                        {
                            "Rank": 1,
                            "Group": "Technology",
                            "Positive Symbol Share %": 82.0,
                            "Market Cap Weighted Return %": 1.8,
                        },
                        {
                            "Rank": 2,
                            "Group": "Energy",
                            "Positive Symbol Share %": 41.0,
                            "Market Cap Weighted Return %": -0.4,
                        },
                    ]
                ),
            },
            futures_macro_snapshot={
                "status": "OK",
                "summary": {"scenario": "Risk-on with rate pressure", "summary": "Equity futures are firm while rates are pressuring duration."},
                "scores": pd.DataFrame(
                    [
                        {"Score": "Risk-On Score", "Value": 33, "Direction": "risk-on", "Tone": "positive"},
                        {"Score": "Rate Pressure Score", "Value": 27, "Direction": "rate pressure", "Tone": "warning"},
                    ]
                ),
                "coverage": {"standardized_count": 14, "symbol_count": 16, "latest_date": "2026-06-05"},
            },
            sentiment_snapshot={
                "status": "OK",
                "analysis": {
                    "phase_label": "혼합 중립",
                    "headline": "Fear & Greed is neutral while internals are mixed.",
                    "data_confidence": {"status": "High", "detail": "latest CNN / AAII rows"},
                },
                "coverage": {"cnn_score": 54.7, "cnn_rating": "neutral", "aaii_bull_bear_spread": -0.7},
            },
            events_snapshot={
                "status": "OK",
                "coverage": {"event_count": 3, "next_event_date": "2026-06-10", "needs_review_count": 1},
                "rows": pd.DataFrame(
                    [
                        {
                            "Date": "2026-06-10",
                            "Type Label": "CPI",
                            "Title": "CPI Release",
                            "Days Until": 2,
                            "Importance": "High",
                            "Validation": "Official",
                        }
                    ]
                ),
            },
            collection_ops_snapshot={
                "status": "REVIEW",
                "coverage": {"ok_count": 4, "due_count": 2, "stale_count": 1, "partial_count": 1, "missing_count": 0, "failed_count": 0},
                "rows": pd.DataFrame(
                    [
                        {"Area": "Futures Monitor 1m OHLCV", "Status": "Due", "Data Freshness": "8m old", "Next Action": "Refresh before using futures context."},
                        {"Area": "Earnings Calendar", "Status": "Partial", "Data Freshness": "covered 1/2", "Next Action": "Inspect failed symbols."},
                    ]
                ),
            },
        )

        self.assertEqual(cockpit["schema_version"], "overview_macro_context_cockpit_v1")
        self.assertEqual(cockpit["status"], "REVIEW")
        summary_copy = f"{cockpit['summary']['headline']} {cockpit['summary']['detail']}"
        summary_sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<!\d)[.!?。]+", summary_copy)
            if sentence.strip()
        ]
        self.assertEqual(cockpit["summary"]["headline"], "오늘은 NVDA +4.2% 같은 상위 움직임을 섹터 확산과 함께 읽는 구간입니다.")
        self.assertNotIn("현재 맥락:", summary_copy)
        self.assertGreaterEqual(len(summary_sentences), 2)
        self.assertLessEqual(len(summary_sentences), 3)
        self.assertIn("Technology", cockpit["summary"]["detail"])
        self.assertIn("Risk-on with rate pressure", cockpit["summary"]["detail"])
        self.assertIn("보강 가능한 자료 3개", cockpit["summary"]["detail"])
        self.assertEqual(cockpit["summary"]["status_label"], "자료 보강 필요")
        self.assertEqual(cockpit["summary"]["review_count"], 3)
        self.assertEqual(cockpit["summary"]["data_review_count"], 4)
        self.assertEqual(cockpit["summary"]["next_path"], "S&P 500 Daily Snapshot → Futures Monitor 1m OHLCV → Earnings Calendar")
        self.assertEqual(cockpit["summary"]["rail"][0]["label"], "자료 상태")
        self.assertEqual(cockpit["summary"]["rail"][0]["value"], "보강 가능 자료 3개")
        self.assertEqual(
            [item["label"] for item in cockpit["summary"]["rail"]],
            ["자료 상태", "Top Mover", "Breadth", "Macro", "Next Event"],
        )
        self.assertEqual(
            [row["label"] for row in cockpit["brief_rows"]],
            ["무엇이 움직였나", "확산/집중인가", "Futures/Macro 배경"],
        )
        self.assertEqual([cue["label"] for cue in cockpit["interpretation_cues"]], ["이벤트 압력", "심리 확인", "매크로 확인"])
        self.assertNotIn("자료 상태 주의점", [cue["label"] for cue in cockpit["interpretation_cues"]])
        self.assertEqual(cockpit["brief_rows"][0]["target_tab"], "Market Movers")
        self.assertEqual(cockpit["brief_rows"][2]["target_tab"], "Futures Monitor")
        self.assertEqual(cockpit["brief_rows"][2]["source_area"], "Futures Monitor 1m OHLCV")
        self.assertEqual(cockpit["brief_rows"][2]["freshness_label"], "8m old")
        self.assertEqual(cockpit["brief_rows"][2]["value"], "장중 macro 해석 보류")
        self.assertIn("risk-on / 금리 압력 설명은 낮게 봅니다", cockpit["brief_rows"][2]["detail"])
        self.assertNotIn("이벤트 배경", [row["label"] for row in cockpit["brief_rows"]])
        self.assertNotIn("brief_caveats", cockpit)
        self.assertEqual(cockpit["refresh_plan"]["schema_version"], "overview_market_context_refresh_plan_v1")
        self.assertEqual(cockpit["refresh_plan"]["summary"]["primary_button_label"], "현재 이슈만 보강")
        self.assertEqual(cockpit["refresh_plan"]["summary"]["full_refresh_label"], "전체 Market Context 자료 보강")
        self.assertEqual(
            [item["action_id"] for item in cockpit["refresh_plan"]["items"]],
            ["sp500_intraday_snapshot", "futures_1m", "earnings_calendar"],
        )
        self.assertEqual(
            [item["resolution"] for item in cockpit["refresh_plan"]["items"]],
            ["resolvable", "resolvable", "partial"],
        )
        self.assertEqual(cockpit["refresh_plan"]["items"][1]["source_area"], "Futures Monitor 1m OHLCV")
        self.assertIn("시장 휴장", cockpit["refresh_plan"]["items"][1]["limitation"])
        self.assertIn("추정", cockpit["refresh_plan"]["items"][2]["limitation"])
        self.assertEqual(cockpit["refresh_plan"]["excluded_items"][0]["source_area"], "Events")
        self.assertEqual(cockpit["refresh_plan"]["excluded_items"][0]["resolution"], "not_actionable")
        self.assertEqual(cockpit["interpretation_cues"][0]["target_tab"], "Events")
        self.assertEqual(cockpit["interpretation_cues"][2]["target_tab"], "Futures Macro")
        self.assertEqual([card["id"] for card in cockpit["cards"]], ["movement", "breadth", "futures", "sentiment", "events", "data"])
        self.assertEqual([card["group"] for card in cockpit["cards"][:3]], ["core", "core", "core"])
        self.assertEqual([card["group"] for card in cockpit["cards"][3:]], ["supporting", "supporting", "supporting"])
        self.assertEqual(cockpit["cards"][0]["value"], "NVDA +4.2%")
        self.assertIn("Technology 리더십", cockpit["cards"][1]["detail"])
        self.assertIn("금리 압력", cockpit["cards"][2]["badges"][1]["label"])
        self.assertEqual(cockpit["cards"][3]["value"], "혼합 중립")
        self.assertEqual(cockpit["cards"][4]["value"], "2026-06-10")
        self.assertEqual(cockpit["cards"][5]["value"], "관리 메타")
        self.assertEqual([item["id"] for item in cockpit["context_findings"]], ["market_movers", "futures", "events", "data_health"])
        self.assertIn("source_area", cockpit["context_findings"][0])
        self.assertIn("conclusion", cockpit["context_findings"][0])
        self.assertIn("interpretation", cockpit["context_findings"][0])
        self.assertIn("evidence", cockpit["context_findings"][0])
        self.assertIn("freshness", cockpit["context_findings"][0])
        self.assertIn("priority", cockpit["context_findings"][0])
        self.assertEqual(cockpit["context_findings"][2]["label"], "Events")
        self.assertNotIn("확인하세요", " ".join(str(item) for item in cockpit["context_findings"]))
        self.assertEqual(cockpit["data_health_handoff"]["schema_version"], "overview_data_health_ingestion_handoff_v1")
        self.assertEqual(cockpit["source_confidence"]["schema_version"], "overview_source_confidence_catalog_v1")
        self.assertEqual(cockpit["source_confidence"]["status"], "REVIEW")
        self.assertGreaterEqual(cockpit["source_confidence"]["summary"]["reference_count"], 2)
        self.assertIn("prices", [item["id"] for item in cockpit["source_confidence"]["items"]])
        self.assertIn("context 전용", cockpit["boundary_note"])

    def test_overview_macro_context_cockpit_uses_last_market_basis_when_market_is_closed(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        cockpit = build_overview_macro_context_cockpit(
            market_session_context={
                "phase": "휴장",
                "is_trading_day": False,
                "is_market_open_now": False,
                "session_date": "2026-06-20",
                "reason": "주말",
            },
            market_movers_snapshot={
                "status": "OK",
                "period_label": "Daily",
                "universe_label": "S&P 500",
                "coverage": {
                    "returnable_count": 503,
                    "universe_count": 503,
                    "snapshot_time_utc": "2026-06-18 20:58",
                    "effective_end_date": "2026-06-18",
                    "refresh_state": {"status": "stale", "label": "Stale", "detail": "3020m old", "tone": "danger"},
                },
                "rows": pd.DataFrame(
                    [
                        {
                            "Rank": 1,
                            "Symbol": "NVDA",
                            "Name": "NVIDIA Corp",
                            "Return %": 4.2,
                            "Sector": "Technology",
                        }
                    ]
                ),
            },
            group_leadership_snapshot={
                "status": "OK",
                "period_label": "Daily",
                "coverage": {"returnable_count": 503, "universe_count": 503, "effective_end_date": "2026-06-18"},
                "rows": pd.DataFrame(
                    [
                        {
                            "Rank": 1,
                            "Group": "Technology",
                            "Positive Symbol Share %": 82.0,
                            "Market Cap Weighted Return %": 1.8,
                        }
                    ]
                ),
            },
            futures_macro_snapshot={
                "status": "OK",
                "summary": {"scenario": "Risk-on with rate pressure", "summary": "Equity futures are firm."},
                "scores": pd.DataFrame(),
                "coverage": {"standardized_count": 16, "symbol_count": 16, "latest_date": "2026-06-18"},
            },
            sentiment_snapshot={
                "status": "OK",
                "analysis": {"phase_label": "혼합 중립", "data_confidence": {"status": "High", "detail": "latest rows"}},
                "coverage": {},
            },
            events_snapshot={
                "status": "OK",
                "coverage": {"event_count": 0},
                "rows": pd.DataFrame(),
            },
            collection_ops_snapshot={
                "status": "OK",
                "coverage": {"ok_count": 6, "due_count": 0, "stale_count": 0, "partial_count": 0, "missing_count": 0, "failed_count": 0},
                "rows": pd.DataFrame(),
            },
        )

        self.assertEqual(cockpit["market_session"]["brief_title"], "마지막 거래일 시장 브리프")
        self.assertIn("기준: 2026-06-18", cockpit["market_session"]["brief_subtitle"])
        self.assertIn("미국장 휴장", cockpit["market_session"]["brief_subtitle"])
        self.assertIn("마지막 거래일", cockpit["summary"]["headline"])
        self.assertNotIn("오늘은", cockpit["summary"]["headline"])
        self.assertEqual(cockpit["summary"]["rail"][0]["value"], "자료 정상 · 휴장 기준")
        self.assertEqual(cockpit["summary"]["review_count"], 0)
        self.assertEqual(cockpit["refresh_plan"]["items"], [])
        self.assertEqual(cockpit["refresh_plan"]["summary"]["primary_button_label"], "현재 보강 없음")
        self.assertEqual(cockpit["brief_rows"][0]["status_label"], "휴장 기준")
        self.assertEqual(cockpit["brief_rows"][0]["freshness_label"], "2026-06-18")
        self.assertEqual(cockpit["brief_rows"][1]["freshness_label"], "2026-06-18")
        prices = next(item for item in cockpit["source_confidence"]["items"] if item["id"] == "prices")
        self.assertEqual(prices["status"], "OK")
        self.assertEqual(prices["status_label"], "자료 정상")

    def test_overview_macro_context_cockpit_keeps_intraday_refresh_action_when_market_is_open(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        cockpit = build_overview_macro_context_cockpit(
            market_session_context={
                "phase": "장중",
                "is_trading_day": True,
                "is_market_open_now": True,
                "session_date": "2026-06-18",
                "reason": "정규장",
            },
            market_movers_snapshot={
                "status": "OK",
                "period_label": "Daily",
                "universe_label": "S&P 500",
                "coverage": {
                    "returnable_count": 503,
                    "universe_count": 503,
                    "snapshot_time_utc": "2026-06-18 15:00",
                    "effective_end_date": "2026-06-18",
                    "refresh_state": {"status": "stale", "label": "Stale", "detail": "30m old", "tone": "danger"},
                },
                "rows": pd.DataFrame(
                    [
                        {"Rank": 1, "Symbol": "NVDA", "Name": "NVIDIA Corp", "Return %": 4.2, "Sector": "Technology"}
                    ]
                ),
            },
            group_leadership_snapshot={"status": "OK", "period_label": "Daily", "coverage": {}, "rows": pd.DataFrame()},
            futures_macro_snapshot={"status": "OK", "summary": {}, "scores": pd.DataFrame(), "coverage": {}},
            sentiment_snapshot={"status": "OK", "analysis": {"data_confidence": {"status": "High"}}, "coverage": {}},
            events_snapshot={"status": "OK", "coverage": {"event_count": 0}, "rows": pd.DataFrame()},
            collection_ops_snapshot={"status": "OK", "coverage": {}, "rows": pd.DataFrame()},
        )

        self.assertEqual(cockpit["market_session"]["brief_title"], "오늘의 시장 브리프")
        self.assertIn("sp500_intraday_snapshot", cockpit["refresh_plan"]["action_ids"])
        self.assertEqual(cockpit["refresh_plan"]["summary"]["primary_button_label"], "현재 이슈만 보강")

    def test_market_context_brief_html_renders_session_title_and_basis(self) -> None:
        from app.web.overview_ui_components import _macro_context_cockpit_html

        html = _macro_context_cockpit_html(
            {
                "status": "OK",
                "summary": {
                    "headline": "마지막 거래일에는 NVDA +4.2% 같은 상위 움직임을 섹터 확산과 함께 읽는 구간입니다.",
                    "detail": "Technology 리더십.",
                    "status_label": "자료 정상 · 휴장 기준",
                    "rail": [],
                },
                "market_session": {
                    "brief_title": "마지막 거래일 시장 브리프",
                    "brief_subtitle": "기준: 2026-06-18 · 현재 미국장 휴장",
                },
                "brief_rows": [
                    {"label": "무엇이 움직였나", "value": "NVDA +4.2%", "detail": "Technology lead", "tone": "positive"}
                ],
                "sector_pressure": {},
                "event_timeline": {},
            },
            include_reading_flow=False,
        )

        self.assertIn("마지막 거래일 시장 브리프", html)
        self.assertIn("기준: 2026-06-18", html)
        self.assertNotIn("오늘의 시장 브리프", html)

    def test_overview_macro_context_cockpit_uses_recent_cpi_as_compact_event_cue(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        cockpit = build_overview_macro_context_cockpit(
            market_movers_snapshot={
                "status": "OK",
                "coverage": {"returnable_count": 503, "universe_count": 503, "effective_end_date": "2026-06-12"},
                "rows": pd.DataFrame([{"Symbol": "SNDK", "Return %": 14.5, "Name": "Sandisk", "Sector": "Technology"}]),
            },
            group_leadership_snapshot={
                "status": "OK",
                "coverage": {"returnable_count": 503, "universe_count": 503, "effective_end_date": "2026-06-12"},
                "rows": pd.DataFrame(
                    [
                        {
                            "Group": "Technology",
                            "Market Cap Weighted Return %": 0.9,
                            "Positive Symbol Share %": 52.0,
                        }
                    ]
                ),
            },
            futures_macro_snapshot={
                "status": "OK",
                "summary": {"scenario": "금리 압력", "summary": "Rates and USD are firm."},
                "scores": pd.DataFrame([{"Score": "Rate Pressure Score", "Value": 64, "Tone": "warning"}]),
                "coverage": {"standardized_count": 14, "symbol_count": 16, "latest_date": "2026-06-12"},
            },
            sentiment_snapshot={
                "status": "OK",
                "analysis": {
                    "phase_label": "중립",
                    "headline": "Sentiment is neutral.",
                    "data_confidence": {"status": "High", "detail": "latest sentiment rows"},
                },
                "coverage": {"cnn_score": 55, "cnn_rating": "neutral", "aaii_bull_bear_spread": -1.0},
            },
            events_snapshot={
                "status": "OK",
                "coverage": {
                    "event_count": 4,
                    "next_event_date": "2026-06-17",
                    "latest_recent_event_date": "2026-06-10",
                    "needs_review_count": 0,
                    "official_count": 2,
                    "estimate_count": 1,
                    "latest_collected_at": "2026-06-12 01:30",
                },
                "rows": pd.DataFrame(
                    [
                        {
                            "Date": "2026-06-10",
                            "Days Until": -2,
                            "Window": "Recent",
                            "Type": "MACRO_CPI",
                            "Type Label": "CPI",
                            "Title": "CPI: Consumer Price Index for May 2026",
                            "Source Type": "Official",
                            "Validation": "Official",
                            "Freshness": "Official",
                            "Quality Action": "No action",
                            "Importance": "High",
                        },
                        {
                            "Date": "2026-06-17",
                            "Days Until": 5,
                            "Window": "Upcoming",
                            "Type": "FOMC_MEETING",
                            "Type Label": "FOMC",
                            "Title": "FOMC Meeting: June 16-17*, 2026",
                            "Source Type": "Official",
                            "Validation": "Official",
                            "Freshness": "Official",
                            "Quality Action": "No action",
                            "Importance": "High",
                        },
                    ]
                ),
            },
            collection_ops_snapshot={
                "status": "REVIEW",
                "coverage": {"ok_count": 4, "due_count": 0, "stale_count": 1, "partial_count": 0, "missing_count": 0, "failed_count": 0},
                "rows": pd.DataFrame(
                    [
                        {
                            "Area": "Macro Calendar",
                            "Status": "Stale",
                            "Data Freshness": "covered 2/4",
                            "Next Action": "Refresh Macro Calendar or import the BLS .ics file.",
                        }
                    ]
                ),
            },
        )

        event_card = cockpit["cards"][4]
        self.assertEqual(event_card["value"], "최근 CPI 발표 확인 필요")
        self.assertIn("2일 전", event_card["detail"])
        self.assertIn("다음 FOMC 5일 후", event_card["detail"])
        self.assertEqual(cockpit["interpretation_cues"][0]["value"], "최근 CPI 발표 확인 필요")
        self.assertEqual(cockpit["interpretation_cues"][0]["label"], "이벤트 압력")
        self.assertEqual(cockpit["interpretation_cues"][2]["label"], "매크로 확인")
        self.assertNotIn("자료 상태 주의점", [cue["label"] for cue in cockpit["interpretation_cues"]])
        event_findings = [item for item in cockpit["context_findings"] if item["id"] == "events"]
        self.assertEqual(len(event_findings), 1)
        self.assertEqual(event_findings[0]["label"], "Events")
        self.assertIn("가까운 event", event_findings[0]["conclusion"])
        self.assertIn("Events", event_findings[0]["source_area"])
        self.assertNotIn("확인하세요", event_findings[0]["conclusion"])

    def test_overview_macro_context_cockpit_normalizes_intraday_refresh_state_dict(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        cockpit = build_overview_macro_context_cockpit(
            market_movers_snapshot={
                "status": "OK",
                "coverage": {
                    "returnable_count": 503,
                    "universe_count": 503,
                    "effective_end_date": "2026-06-05",
                    "refresh_state": {
                        "status": "stale",
                        "label": "Stale",
                        "detail": "2962m old",
                        "tone": "warning",
                        "recommended_action": "Run Update Daily Snapshot.",
                    },
                },
                "rows": pd.DataFrame(
                    [
                        {
                            "Symbol": "AAPL",
                            "Name": "Apple Inc",
                            "Return %": -1.2,
                            "Sector": "Technology",
                        }
                    ]
                ),
            },
            group_leadership_snapshot={"status": "OK", "coverage": {}, "rows": pd.DataFrame()},
            futures_macro_snapshot={"status": "OK", "coverage": {}, "summary": {}, "scores": pd.DataFrame()},
            sentiment_snapshot={"status": "OK", "coverage": {}, "analysis": {}},
            events_snapshot={"status": "OK", "coverage": {}, "rows": pd.DataFrame()},
            collection_ops_snapshot={"status": "OK", "coverage": {"ok_count": 6}, "rows": pd.DataFrame()},
        )

        movement = cockpit["cards"][0]
        self.assertEqual(movement["status"], "Stale")
        self.assertEqual(movement["badges"][1]["value"], "자료 오래됨")
        self.assertNotIn("{", movement["badges"][1]["value"])


class OverviewMarketContextAnalogServiceContractTests(unittest.TestCase):
    def _analog_price_rows(self, symbols: list[str], dates: pd.DatetimeIndex) -> pd.DataFrame:
        rows: list[dict[str, object]] = []
        anchors = [20, 35]
        current_index = len(dates) - 1
        for symbol in symbols:
            prices = [100.0 for _ in dates]
            if symbol == "XLV":
                for anchor in anchors + [current_index]:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 104.0
            if symbol == "QQQ":
                for anchor in anchors:
                    prices[anchor] = 100.0
                    prices[anchor + 5] = 105.0
                    prices[anchor + 20] = 120.0
                    prices[anchor + 60] = 160.0
            for idx, day in enumerate(dates):
                rows.append(
                    {
                        "symbol": symbol,
                        "date": day,
                        "close": prices[idx],
                        "adj_close": prices[idx],
                    }
                )
        return pd.DataFrame(rows)

    def test_sector_etf_proxy_map_resolves_gics_and_provider_aliases(self) -> None:
        from app.services.overview_market_context_analog import (
            sector_etf_proxy_map,
            resolve_sector_etf_proxy,
        )

        proxies = sector_etf_proxy_map()

        self.assertEqual(proxies["Technology"]["symbol"], "XLK")
        self.assertEqual(resolve_sector_etf_proxy("Consumer Defensive")["symbol"], "XLP")
        self.assertEqual(resolve_sector_etf_proxy("Consumer Cyclical")["symbol"], "XLY")
        self.assertEqual(resolve_sector_etf_proxy("Basic Materials")["symbol"], "XLB")
        self.assertEqual(resolve_sector_etf_proxy("Health Care")["symbol"], "XLV")

    def test_price_coverage_helper_marks_short_sector_etf_history_insufficient(self) -> None:
        from app.services.overview_market_context_analog import summarize_price_coverage

        short_dates = pd.bdate_range("2026-03-02", periods=63)
        long_dates = pd.bdate_range("2024-01-02", periods=260)
        price_rows = pd.concat(
            [
                pd.DataFrame(
                    {
                        "symbol": "XLI",
                        "date": short_dates,
                        "adj_close": [100.0] * len(short_dates),
                        "close": [100.0] * len(short_dates),
                    }
                ),
                pd.DataFrame(
                    {
                        "symbol": "SPY",
                        "date": long_dates,
                        "adj_close": [100.0] * len(long_dates),
                        "close": [100.0] * len(long_dates),
                    }
                ),
            ],
            ignore_index=True,
        )

        coverage = summarize_price_coverage(price_rows, symbols=["XLI", "SPY"], min_rows=252)
        by_symbol = {row["symbol"]: row for row in coverage}

        self.assertEqual(by_symbol["XLI"]["status"], "INSUFFICIENT_DATA")
        self.assertEqual(by_symbol["XLI"]["row_count"], 63)
        self.assertEqual(by_symbol["XLI"]["start_date"], "2026-03-02")
        self.assertEqual(by_symbol["SPY"]["status"], "OK")

    def test_historical_analog_reports_current_leadership_proxy_but_does_not_force_short_history(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2026-03-02", periods=63)
        price_rows = pd.concat(
            [
                pd.DataFrame({"symbol": "XLI", "date": dates, "adj_close": 100.0, "close": 100.0}),
                pd.DataFrame({"symbol": "SPY", "date": pd.bdate_range("2024-01-02", periods=260), "adj_close": 100.0, "close": 100.0}),
            ],
            ignore_index=True,
        )

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Industrials", "Market Cap Weighted Return %": 3.34}]),
            },
            price_history=price_rows,
            comparison_symbols=("SPY",),
            min_history_rows=252,
        )

        self.assertEqual(model["status"], "INSUFFICIENT_DATA")
        self.assertEqual(model["leadership_sector"], "Industrials")
        self.assertEqual(model["proxy_etf"], "XLI")
        self.assertIn("자료 부족", model["headline"])
        self.assertEqual(model["sample_count"], 0)
        self.assertFalse(model["rows"])
        self.assertEqual(model["current_as_of"], "2026-05-27")
        self.assertIn("5D 상대강도", model["calculation_note"])

    def test_historical_analog_exposes_generalized_repair_action_for_insufficient_proxy_or_comparison_symbols(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        short_dates = pd.bdate_range("2026-03-02", periods=63)
        medium_dates = pd.bdate_range("2025-01-02", periods=140)
        long_dates = pd.bdate_range("2022-01-03", periods=820)
        price_rows = pd.concat(
            [
                pd.DataFrame({"symbol": "XLF", "date": short_dates, "adj_close": 100.0, "close": 100.0}),
                pd.DataFrame({"symbol": "SPY", "date": long_dates, "adj_close": 100.0, "close": 100.0}),
                pd.DataFrame({"symbol": "TLT", "date": medium_dates, "adj_close": 100.0, "close": 100.0}),
            ],
            ignore_index=True,
        )

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Financial Services", "Market Cap Weighted Return %": 2.4}]),
            },
            price_history=price_rows,
            comparison_symbols=("SPY", "TLT"),
            min_history_rows=252,
        )

        self.assertEqual(model["proxy_etf"], "XLF")
        self.assertEqual([item["symbol"] for item in model["coverage_gaps"]], ["XLF", "TLT"])
        self.assertEqual(model["repair_action"]["symbols"], ["XLF", "TLT"])
        self.assertEqual(model["repair_action"]["period"], "10y")
        self.assertEqual(model["repair_action"]["interval"], "1d")
        self.assertIn("finance_price.nyse_price_history", model["repair_action"]["target_table"])

    def test_historical_analog_uses_anchor_after_returns_without_current_row_lookahead(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-01-02", periods=100)
        price_rows = self._analog_price_rows(["XLV", "SPY", "QQQ", "TLT", "GLD"], dates)

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Healthcare", "Market Cap Weighted Return %": 2.1}]),
            },
            price_history=price_rows,
            comparison_symbols=("SPY", "QQQ", "TLT", "GLD"),
            min_history_rows=80,
            min_sample_count=2,
            min_anchor_gap=10,
        )

        self.assertEqual(model["status"], "OK")
        self.assertEqual(model["leadership_sector"], "Healthcare")
        self.assertEqual(model["proxy_etf"], "XLV")
        self.assertEqual(model["sample_count"], 2)
        self.assertNotIn(str(dates[-1].date()), model["anchor_dates"])
        self.assertIn("5D", model["condition_summary"])
        self.assertEqual(model["current_as_of"], str(dates[-1].date()))
        self.assertIn("5D 상대강도", model["calculation_note"])
        qqq_5d = next(row for row in model["rows"] if row["asset"] == "QQQ" and row["horizon"] == "5D")
        qqq_60d = next(row for row in model["rows"] if row["asset"] == "QQQ" and row["horizon"] == "60D")
        self.assertAlmostEqual(qqq_5d["median_return_pct"], 5.0, places=2)
        self.assertAlmostEqual(qqq_60d["median_return_pct"], 60.0, places=2)
        self.assertTrue(any("미래 움직임 보장이 아님" in item for item in model["limitations"]))

    def test_historical_analog_replays_selected_as_of_and_pattern_window_without_future_rows(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-01-02", periods=140)
        as_of_index = 100
        anchors = [40, 70]
        rows: list[dict[str, object]] = []
        for symbol in ["XLV", "SPY", "QQQ"]:
            prices = [100.0 for _ in dates]
            if symbol == "XLV":
                for anchor in [*anchors, as_of_index]:
                    prices[anchor - 20] = 100.0
                    prices[anchor] = 105.0
                prices[-1] = 175.0
            if symbol == "QQQ":
                for anchor in anchors:
                    prices[anchor] = 100.0
                    prices[anchor + 5] = 106.0
                    prices[anchor + 20] = 125.0
                prices[-1] = 250.0
            for idx, day in enumerate(dates):
                rows.append(
                    {
                        "symbol": symbol,
                        "date": day,
                        "close": prices[idx],
                        "adj_close": prices[idx],
                    }
                )
        price_rows = pd.DataFrame(rows)
        as_of_date = str(dates[as_of_index].date())

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Healthcare", "Market Cap Weighted Return %": 2.1}]),
            },
            price_history=price_rows,
            comparison_symbols=("SPY", "QQQ"),
            horizons=(5, 20),
            as_of_date=as_of_date,
            pattern_window="20D",
            min_history_rows=80,
            min_sample_count=2,
            min_anchor_gap=20,
        )

        self.assertEqual(model["status"], "OK")
        self.assertEqual(model["schema_version"], "overview_market_context_historical_analog_v2")
        self.assertEqual(model["requested_as_of"], as_of_date)
        self.assertEqual(model["current_as_of"], as_of_date)
        self.assertTrue(str(model["data_window"]).endswith(as_of_date))
        self.assertEqual(model["pattern_window"], "20D")
        self.assertEqual(model["pattern_window_label"], "20D")
        self.assertIn("20D-SPY 20D", model["condition_summary"])
        self.assertNotIn(str(dates[-1].date()), model["data_window"])
        self.assertNotIn(str(dates[-1].date()), model["anchor_dates"])
        qqq_20d = next(row for row in model["rows"] if row["asset"] == "QQQ" and row["horizon"] == "20D")
        self.assertAlmostEqual(qqq_20d["median_return_pct"], 25.0, places=2)
        self.assertTrue(any("선택 기준일 이후 가격" in item for item in model["limitations"]))

    def test_historical_analog_explains_when_selected_as_of_is_bounded_by_common_price_history(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-01-02", periods=130)
        effective_index = 100
        requested_index = 120
        effective_date = str(dates[effective_index].date())
        requested_date = str(dates[requested_index].date())
        anchors = [35, 60, 85]
        rows: list[dict[str, object]] = []
        for symbol in ["XLV", "SPY", "QQQ", "GLD"]:
            prices = [100.0 for _ in dates]
            if symbol == "XLV":
                for anchor in [*anchors, effective_index, requested_index]:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 104.0
            if symbol == "QQQ":
                for anchor in anchors:
                    prices[anchor] = 100.0
                    prices[anchor + 20] = 118.0
            last_index = requested_index if symbol == "XLV" else effective_index
            for idx, day in enumerate(dates[: last_index + 1]):
                rows.append(
                    {
                        "symbol": symbol,
                        "date": day,
                        "close": prices[idx],
                        "adj_close": prices[idx],
                    }
                )

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Healthcare", "Market Cap Weighted Return %": 2.1}]),
            },
            price_history=pd.DataFrame(rows),
            comparison_symbols=("SPY", "QQQ", "GLD"),
            horizons=(5, 20),
            as_of_date=requested_date,
            pattern_window="5D",
            min_history_rows=80,
            min_sample_count=2,
            min_anchor_gap=10,
        )

        self.assertEqual(model["requested_as_of"], requested_date)
        self.assertEqual(model["current_as_of"], effective_date)
        alignment = model["as_of_alignment"]
        self.assertFalse(alignment["is_aligned"])
        self.assertEqual(alignment["requested_as_of"], requested_date)
        self.assertEqual(alignment["effective_as_of"], effective_date)
        self.assertIn("SPY", alignment["limiting_symbols"])
        self.assertIn("공통 가격", alignment["reason"])
        self.assertTrue(any(effective_date in warning for warning in model["basis_warnings"]))
        self.assertEqual(model["repair_action"]["label"], "과거 유사 맥락 가격 기준 최신화")
        self.assertEqual(model["repair_action"]["symbols"], ["SPY", "QQQ", "GLD"])
        self.assertTrue(model["repair_action"]["stale_basis"])
        self.assertIn(requested_date, model["repair_action"]["reason"])
        self.assertIn(effective_date, model["repair_action"]["reason"])

    def test_historical_analog_builds_separate_gld_conditioned_pilot_without_changing_broad_rows(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-01-02", periods=120)
        current_index = len(dates) - 1
        anchors = [30, 50, 70]
        gld_matching_anchors = {30, 70}
        rows: list[dict[str, object]] = []
        for symbol in ["XLV", "SPY", "QQQ", "GLD"]:
            prices = [100.0 for _ in dates]
            if symbol == "XLV":
                for anchor in [*anchors, current_index]:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 104.0
            if symbol == "QQQ":
                for anchor in anchors:
                    prices[anchor] = 100.0
                    prices[anchor + 20] = 120.0
            if symbol == "GLD":
                for anchor in anchors:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 102.0 if anchor in gld_matching_anchors else 98.0
                    prices[anchor + 20] = 110.0
                prices[current_index - 5] = 100.0
                prices[current_index] = 102.0
            for idx, day in enumerate(dates):
                rows.append(
                    {
                        "symbol": symbol,
                        "date": day,
                        "close": prices[idx],
                        "adj_close": prices[idx],
                    }
                )

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Healthcare", "Market Cap Weighted Return %": 2.1}]),
            },
            price_history=pd.DataFrame(rows),
            comparison_symbols=("SPY", "QQQ", "GLD"),
            futures_history=pd.DataFrame(),
            horizons=(20,),
            min_history_rows=90,
            min_sample_count=3,
            min_anchor_gap=10,
        )

        self.assertEqual(model["sample_count"], 3)
        self.assertTrue(model["rows"])
        pilot = model["macro_conditioned_analog"]
        self.assertEqual(pilot["schema_version"], "overview_market_context_macro_conditioned_analog_pilot_v1")
        self.assertEqual(pilot["additional_condition_count"], 1)
        self.assertEqual(pilot["broad_sample_count"], 3)
        self.assertEqual(pilot["sample_count"], 2)
        self.assertEqual(pilot["sample_quality"]["status"], "REVIEW")
        self.assertIn("GLD", pilot["condition_summary"])
        self.assertIn("Broad 3회 중 Macro 조건 포함 2회", pilot["sample_reduction_reason"])
        self.assertEqual([item["id"] for item in pilot["used_conditions"]], ["sector_relative_strength", "gld_safe_haven_context"])
        self.assertEqual([item["id"] for item in pilot["insufficient_conditions"]], ["futures_rate_pressure_context"])
        self.assertNotIn("futures_macro_thermometer", [item["id"] for item in pilot["excluded_conditions"]])
        self.assertEqual(
            [row["sample_count"] for row in pilot["rows"] if row["asset"] == "QQQ" and row["horizon"] == "20D"],
            [2],
        )

    def test_historical_analog_adds_stored_futures_rate_pressure_condition_without_future_rows(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-01-02", periods=120)
        as_of_index = 90
        as_of_date = str(dates[as_of_index].date())
        anchors = [30, 50, 70]
        rows: list[dict[str, object]] = []
        for symbol in ["XLV", "SPY", "QQQ", "GLD"]:
            prices = [100.0 for _ in dates]
            if symbol == "XLV":
                for anchor in [*anchors, as_of_index]:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 104.0
            if symbol == "QQQ":
                for anchor in anchors:
                    prices[anchor] = 100.0
                    prices[anchor + 20] = 120.0
            if symbol == "GLD":
                for anchor in anchors:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 102.0 if anchor in {30, 70} else 98.0
                prices[as_of_index - 5] = 100.0
                prices[as_of_index] = 102.0
                prices[-5] = 100.0
                prices[-1] = 98.0
            for idx, day in enumerate(dates):
                rows.append({"symbol": symbol, "date": day, "close": prices[idx], "adj_close": prices[idx]})

        futures_rows: list[dict[str, object]] = []
        for futures_symbol in ["ZN=F", "ZB=F"]:
            prices = [100.0 for _ in dates]
            for anchor in [30, as_of_index]:
                prices[anchor - 5] = 100.0
                prices[anchor] = 97.0
            prices[70 - 5] = 100.0
            prices[70] = 103.0
            prices[-5] = 100.0
            prices[-1] = 104.0
            for idx, day in enumerate(dates):
                futures_rows.append(
                    {
                        "provider_symbol": futures_symbol,
                        "interval_code": "1d",
                        "candle_time_utc": day,
                        "open": prices[idx],
                        "high": prices[idx],
                        "low": prices[idx],
                        "close": prices[idx],
                        "volume": 1000,
                    }
                )

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Healthcare", "Market Cap Weighted Return %": 2.1}]),
            },
            price_history=pd.DataFrame(rows),
            futures_history=pd.DataFrame(futures_rows),
            comparison_symbols=("SPY", "QQQ", "GLD"),
            horizons=(20,),
            as_of_date=as_of_date,
            min_history_rows=80,
            min_sample_count=3,
            min_anchor_gap=10,
        )

        pilot = model["macro_conditioned_analog"]
        self.assertEqual(model["current_as_of"], as_of_date)
        self.assertEqual(pilot["broad_sample_count"], 3)
        self.assertEqual(pilot["sample_count"], 1)
        self.assertEqual(pilot["additional_condition_count"], 2)
        self.assertEqual(
            pilot["macro_condition_counts"],
            {
                "broad": 3,
                "gld": 2,
                "futures": 1,
                "futures_available": 3,
                "intersection": 1,
            },
        )
        self.assertEqual(
            [item["id"] for item in pilot["used_conditions"]],
            ["sector_relative_strength", "gld_safe_haven_context", "futures_rate_pressure_context"],
        )
        self.assertEqual(pilot["insufficient_conditions"], [])
        self.assertIn("Rate Pressure futures proxy", pilot["condition_summary"])
        self.assertIn("ZN=F/ZB=F", pilot["condition_summary"])
        self.assertIn(as_of_date, pilot["used_conditions"][-1]["detail"])
        self.assertNotIn(str(dates[-1].date()), pilot["used_conditions"][-1]["detail"])
        self.assertEqual(pilot["anchor_dates"], [str(dates[30].date())])
        self.assertIn("futures proxy", pilot["sample_reduction_reason"])

    def test_historical_analog_adds_macro_dimension_audit_without_hard_filtering_macro_series(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-01-02", periods=120)
        as_of_index = 90
        as_of_date = str(dates[as_of_index].date())
        anchors = [30, 50, 70]
        rows: list[dict[str, object]] = []
        for symbol in ["XLV", "SPY", "QQQ", "GLD"]:
            prices = [100.0 for _ in dates]
            if symbol == "XLV":
                for anchor in [*anchors, as_of_index]:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 104.0
            if symbol == "QQQ":
                for anchor in anchors:
                    prices[anchor] = 100.0
                    prices[anchor + 20] = 120.0
            if symbol == "GLD":
                for anchor in anchors:
                    prices[anchor - 5] = 100.0
                    prices[anchor] = 102.0 if anchor in {30, 70} else 98.0
                prices[as_of_index - 5] = 100.0
                prices[as_of_index] = 102.0
                prices[-5] = 100.0
                prices[-1] = 98.0
            for idx, day in enumerate(dates):
                rows.append({"symbol": symbol, "date": day, "close": prices[idx], "adj_close": prices[idx]})

        futures_rows: list[dict[str, object]] = []
        for futures_symbol in ["ZN=F", "ZB=F"]:
            prices = [100.0 for _ in dates]
            for anchor in [30, as_of_index]:
                prices[anchor - 5] = 100.0
                prices[anchor] = 97.0
            prices[70 - 5] = 100.0
            prices[70] = 103.0
            prices[-5] = 100.0
            prices[-1] = 104.0
            for idx, day in enumerate(dates):
                futures_rows.append(
                    {
                        "provider_symbol": futures_symbol,
                        "interval_code": "1d",
                        "candle_time_utc": day,
                        "open": prices[idx],
                        "high": prices[idx],
                        "low": prices[idx],
                        "close": prices[idx],
                        "volume": 1000,
                    }
                )

        macro_values = {
            "T10Y3M": {30: -0.25, 50: 0.75, 70: -0.15, as_of_index: -0.35, len(dates) - 1: 1.2},
            "VIXCLS": {30: 16.0, 50: 28.0, 70: 17.0, as_of_index: 17.5, len(dates) - 1: 31.0},
            "BAA10Y": {30: 1.65, 50: 2.65, 70: 1.75, as_of_index: 1.8, len(dates) - 1: 3.1},
        }
        macro_rows: list[dict[str, object]] = []
        for series_id, indexed_values in macro_values.items():
            for idx, value in indexed_values.items():
                macro_rows.append(
                    {
                        "series_id": series_id,
                        "observation_date": dates[idx],
                        "source": "fred",
                        "source_type": "official",
                        "source_mode": "stored",
                        "series_name": series_id,
                        "category": "macro",
                        "frequency": "daily",
                        "units": "Percent",
                        "value": value,
                        "coverage_status": "actual",
                    }
                )
        sentiment_rows = pd.DataFrame(
            [
                {
                    "series_id": "CNN_FEAR_GREED",
                    "observation_date": dates[idx],
                    "source": "cnn",
                    "series_name": "CNN Fear & Greed",
                    "category": "sentiment",
                    "value": 45 + idx % 10,
                    "coverage_status": "actual",
                }
                for idx in [84, 87, as_of_index]
            ]
        )
        events_snapshot = {
            "status": "OK",
            "rows": pd.DataFrame(
                [
                    {
                        "Date": as_of_date,
                        "Type": "FOMC_MEETING",
                        "Type Label": "FOMC",
                        "Title": "FOMC meeting",
                        "Days Until": 0,
                        "Source": "federal_reserve",
                    }
                ]
            ),
            "coverage": {"event_count": 1, "official_count": 1, "latest_collected_at": as_of_date},
        }

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Healthcare", "Market Cap Weighted Return %": 2.1}]),
            },
            price_history=pd.DataFrame(rows),
            futures_history=pd.DataFrame(futures_rows),
            macro_series_history=pd.DataFrame(macro_rows),
            sentiment_history=sentiment_rows,
            events_snapshot=events_snapshot,
            comparison_symbols=("SPY", "QQQ", "GLD"),
            horizons=(20,),
            as_of_date=as_of_date,
            min_history_rows=80,
            min_sample_count=3,
            min_anchor_gap=10,
        )

        pilot = model["macro_conditioned_analog"]
        audit = pilot["macro_dimension_audit"]
        self.assertEqual(audit["schema_version"], "overview_market_context_macro_dimension_audit_v1")
        self.assertEqual(pilot["sample_count"], 1)
        self.assertEqual(audit["broad_anchor_count"], 3)
        self.assertEqual(audit["conditioned_anchor_count"], 1)
        dimensions = {item["id"]: item for item in audit["dimensions"]}
        self.assertEqual(dimensions["sector_relative_strength"]["status"], "USED")
        self.assertEqual(dimensions["gld_safe_haven_context"]["status"], "USED")
        self.assertEqual(dimensions["futures_rate_pressure_context"]["status"], "USED")
        self.assertEqual(dimensions["macro_t10y3m"]["status"], "AVAILABLE_REFERENCE")
        self.assertEqual(dimensions["macro_t10y3m"]["latest_date"], as_of_date)
        self.assertNotIn(str(dates[-1].date()), dimensions["macro_t10y3m"]["detail"])
        self.assertEqual(dimensions["macro_t10y3m"]["anchor_preview_count"], 2)
        self.assertEqual(dimensions["macro_vixcls"]["anchor_preview_count"], 2)
        self.assertEqual(dimensions["macro_baa10y"]["anchor_preview_count"], 2)
        self.assertEqual(dimensions["events_calendar"]["status"], "DEFERRED")
        self.assertEqual(dimensions["market_sentiment"]["status"], "INSUFFICIENT_HISTORY")
        for item in dimensions.values():
            self.assertIn(item["status"], {"USED", "AVAILABLE_REFERENCE", "INSUFFICIENT_HISTORY", "UNAVAILABLE", "DEFERRED"})
            self.assertIn("usage", item)
            self.assertIn("source", item)

    def test_historical_analog_keeps_macro_dimension_audit_when_broad_proxy_coverage_is_short(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-03-01", periods=70)
        price_rows: list[dict[str, object]] = []
        for symbol in ["XLB", "SPY", "GLD"]:
            for idx, day in enumerate(dates):
                price_rows.append(
                    {
                        "symbol": symbol,
                        "date": day,
                        "close": 100.0 + idx,
                        "adj_close": 100.0 + idx,
                    }
                )
        macro_rows: list[dict[str, object]] = []
        for series_id, value in [("T10Y3M", -0.3), ("VIXCLS", 17.0), ("BAA10Y", 1.8)]:
            macro_rows.append(
                {
                    "series_id": series_id,
                    "observation_date": dates[-1],
                    "source": "fred",
                    "series_name": series_id,
                    "category": "macro",
                    "value": value,
                    "coverage_status": "actual",
                }
            )

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Basic Materials", "Market Cap Weighted Return %": 1.2}]),
            },
            price_history=pd.DataFrame(price_rows),
            macro_series_history=pd.DataFrame(macro_rows),
            futures_history=pd.DataFrame(),
            comparison_symbols=("SPY", "GLD"),
            min_history_rows=120,
        )

        self.assertEqual(model["status"], "INSUFFICIENT_DATA")
        audit = model["macro_conditioned_analog"]["macro_dimension_audit"]
        dimensions = {item["id"]: item for item in audit["dimensions"]}
        self.assertEqual(dimensions["sector_relative_strength"]["status"], "INSUFFICIENT_HISTORY")
        self.assertEqual(dimensions["macro_t10y3m"]["status"], "AVAILABLE_REFERENCE")
        self.assertEqual(dimensions["macro_vixcls"]["status"], "AVAILABLE_REFERENCE")
        self.assertEqual(dimensions["macro_baa10y"]["status"], "AVAILABLE_REFERENCE")
        self.assertEqual(dimensions["macro_t10y3m"]["anchor_preview_count"], 0)

    def test_historical_analog_marks_macro_pilot_insufficient_when_gld_context_is_missing(self) -> None:
        from app.services.overview_market_context_analog import build_historical_analog_snapshot

        dates = pd.bdate_range("2024-01-02", periods=120)
        price_rows = self._analog_price_rows(["XLV", "SPY", "QQQ"], dates)

        model = build_historical_analog_snapshot(
            group_leadership_snapshot={
                "status": "OK",
                "rows": pd.DataFrame([{"Rank": 1, "Group": "Healthcare", "Market Cap Weighted Return %": 2.1}]),
            },
            price_history=price_rows,
            comparison_symbols=("SPY", "QQQ", "GLD"),
            futures_history=pd.DataFrame(),
            min_history_rows=90,
            min_sample_count=2,
            min_anchor_gap=10,
        )

        self.assertEqual(model["status"], "OK")
        self.assertTrue(model["rows"])
        pilot = model["macro_conditioned_analog"]
        self.assertEqual(pilot["status"], "INSUFFICIENT_CONTEXT")
        self.assertFalse(pilot["rows"])
        self.assertEqual([item["id"] for item in pilot["used_conditions"]], ["sector_relative_strength"])
        self.assertEqual([item["id"] for item in pilot["insufficient_conditions"]], ["gld_safe_haven_context"])

    def test_group_leadership_date_resolver_respects_selected_as_of_date(self) -> None:
        from app.services.overview_market_intelligence import resolve_group_trend_market_dates

        captured: list[tuple[str, list[object]]] = []
        eligible_dates = list(pd.bdate_range(end="2024-03-15", periods=6).strftime("%Y-%m-%d"))[::-1]

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name
            captured.append((sql, list(params or [])))
            if "AS latest_raw_date" in sql and "ORDER BY `date` DESC" in sql:
                return [{"latest_raw_date": "2024-03-15"}]
            return [{"date": day, "usable_rows": 500} for day in eligible_dates]

        window = resolve_group_trend_market_dates(
            period="weekly",
            min_price_rows=100,
            as_of_date="2024-03-15",
            query_fn=query_fn,
        )

        self.assertEqual(window["status"], "OK")
        self.assertEqual(window["requested_as_of"], "2024-03-15")
        self.assertEqual(window["end_date"], "2024-03-15")
        self.assertLessEqual(window["start_date"], "2024-03-15")
        self.assertTrue(any("`date` <= %s" in sql for sql, _ in captured))
        self.assertTrue(any("2024-03-15" in params for _, params in captured))

    def test_macro_context_cockpit_embeds_analog_read_model_when_supplied(self) -> None:
        from app.services.overview_market_intelligence import build_overview_macro_context_cockpit

        cockpit = build_overview_macro_context_cockpit(
            market_movers_snapshot={"status": "OK", "coverage": {}, "rows": pd.DataFrame([{"Symbol": "MRNA", "Return %": 7.2, "Name": "Moderna", "Sector": "Healthcare"}])},
            group_leadership_snapshot={"status": "OK", "coverage": {}, "rows": pd.DataFrame([{"Group": "Healthcare", "Market Cap Weighted Return %": 2.1, "Positive Symbol Share %": 64.0}])},
            futures_macro_snapshot={"status": "OK", "coverage": {}, "summary": {}, "scores": pd.DataFrame()},
            sentiment_snapshot={"status": "OK", "coverage": {}, "analysis": {}},
            events_snapshot={"status": "OK", "coverage": {}, "rows": pd.DataFrame()},
            collection_ops_snapshot={"status": "OK", "coverage": {"ok_count": 6}, "rows": pd.DataFrame()},
            historical_analog_snapshot={
                "schema_version": "overview_market_context_historical_analog_v2",
                "status": "OK",
                "headline": "과거 유사 맥락 2회 발견",
                "detail": "Healthcare(XLV)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Healthcare",
                "proxy_etf": "XLV",
                "sample_count": 2,
                "condition_summary": "5D relative strength 기준",
                "data_window": "2024-01-02 - 2024-05-20",
                "coverage": [],
                "rows": [],
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            },
        )

        self.assertEqual(cockpit["historical_analog"]["proxy_etf"], "XLV")
        self.assertIn("과거 유사 맥락", cockpit["historical_analog"]["headline"])
        self.assertIn("context 전용", cockpit["boundary_note"])

    def test_historical_analog_html_keeps_context_only_language(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "OK",
                "headline": "과거 유사 맥락 2회 발견",
                "detail": "Healthcare(XLV)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Healthcare",
                "proxy_etf": "XLV",
                "sample_count": 2,
                "condition_summary": "5D relative strength 기준",
                "data_window": "2024-01-02 - 2024-05-20",
                "rows": [
                    {
                        "asset": "QQQ",
                        "horizon": "5D",
                        "median_return_pct": 5.0,
                        "positive_rate_pct": 100.0,
                        "best_return_pct": 5.0,
                        "worst_return_pct": 5.0,
                        "sample_count": 2,
                    }
                ],
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("참고: 과거 유사 맥락", html)
        self.assertIn("QQQ", html)
        for forbidden in ["추천", "매수", "매도", "신호", "PASS", "BLOCKER"]:
            self.assertNotIn(forbidden, html)

    def test_historical_analog_html_explains_similarity_before_statistics(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        rows = []
        for asset, median, positive, best, worst in [
            ("XLK", 3.3, 65.5, 14.8, -11.8),
            ("SPY", 2.5, 75.9, 9.2, -8.1),
            ("QQQ", 4.0, 65.5, 13.0, -10.9),
            ("TLT", -0.1, 48.3, 8.5, -8.4),
        ]:
            rows.append(
                {
                    "asset": asset,
                    "horizon": "20D",
                    "median_return_pct": median,
                    "positive_rate_pct": positive,
                    "best_return_pct": best,
                    "worst_return_pct": worst,
                    "sample_count": 29,
                }
            )

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "OK",
                "headline": "과거 유사 맥락 29회 발견",
                "detail": "Technology(XLK)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Technology",
                "proxy_etf": "XLK",
                "sample_count": 29,
                "condition_summary": "XLK 5D-SPY 5D 상대강도 >= +2.6% 기준",
                "data_window": "2016-06-16 - 2026-05-29",
                "current_as_of": "2026-05-29",
                "calculation_note": "선택한 기준 시점의 sector ETF SPY 대비 5D 상대강도 기준",
                "rows": rows,
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("선택한 기준 시점의 리더십 섹터", html)
        self.assertIn("XLK가 SPY 대비 5D 기준 강했던 과거 구간", html)
        self.assertIn("유사 맥락 계산", html)
        self.assertIn("ov-analog-summary-strip", html)
        self.assertIn("ov-analog-basis-bar", html)
        self.assertIn("ov-analog-basis-summary", html)
        self.assertIn("ov-analog-method-line", html)
        self.assertIn("ov-analog-technical-details", html)
        self.assertNotIn("ov-analog-method-grid", html)
        self.assertNotIn("현재 기준", html)
        self.assertNotIn("표본 품질", html)
        self.assertNotIn("먼저 볼 점", html)
        self.assertNotIn("주의할 점", html)
        self.assertNotIn("먼저 읽을 결론", html)
        self.assertIn("기준 변경은 아래 과거 참고 통계에만 적용", html)
        self.assertNotIn("ov-analog-basis-ledger", html)
        self.assertIn("상단 시장 브리프는 현재 세션에 맞춘 장중 snapshot 또는 마지막 거래일 기준", html)
        self.assertIn("계산 기준", html)
        self.assertIn("latest", html)
        self.assertIn("계산 기준일", html)
        self.assertIn("2026-05-29", html)
        self.assertIn("기준 자산", html)
        self.assertIn("유사 조건", html)
        self.assertIn("5D", html)
        self.assertIn("표본", html)
        self.assertIn("2016-06-16 - 2026-05-29", html)
        self.assertIn("계산식", html)
        self.assertIn("선택한 기준 시점의 sector ETF SPY 대비 5D 상대강도 기준", html)
        self.assertIn("XLK 20D 중간값", html)
        self.assertIn("+3.3%", html)
        self.assertIn("상승 비율", html)
        self.assertIn("최악", html)
        self.assertIn("미래 움직임 보장이 아님", html)
        self.assertIn("핵심 자산 비교", html)
        self.assertNotIn("시장 배경 요약", html)
        self.assertIn("상세 통계", html)
        self.assertLessEqual(html.count("29회"), 1)

        explanation_index = html.index("선택한 기준 시점의 리더십 섹터를 ETF proxy로 보고")
        summary_index = html.index("ov-analog-summary-strip")
        matrix_index = html.index("ov-analog-outcome-matrix")
        table_index = html.index("ov-historical-analog-table-block")
        self.assertLess(explanation_index, summary_index)
        self.assertLess(summary_index, matrix_index)
        self.assertLess(matrix_index, table_index)

        primary_block = html[html.index("핵심 자산 비교") : html.index("상세 통계")]
        self.assertIn("XLK · 20D", primary_block)
        self.assertIn("SPY · 20D", primary_block)
        self.assertIn("QQQ · 20D", primary_block)
        self.assertIn("TLT · 20D", primary_block)

    def test_historical_analog_html_prioritizes_matrix_and_collapses_stat_tables(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        rows = []
        for asset in ["XLB", "SPY", "QQQ", "TLT", "GLD"]:
            for horizon, median, positive, worst in [
                ("5D", 0.5, 63.6, -13.1),
                ("20D", 1.5, 63.6, -19.9),
                ("60D", 3.6, 64.8, -16.5),
            ]:
                rows.append(
                    {
                        "asset": asset,
                        "horizon": horizon,
                        "median_return_pct": median,
                        "positive_rate_pct": positive,
                        "best_return_pct": median + 8.0,
                        "worst_return_pct": worst,
                        "sample_count": 88,
                    }
                )

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "OK",
                "headline": "과거 유사 맥락 88회 발견",
                "detail": "Basic Materials(XLB)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Basic Materials",
                "proxy_etf": "XLB",
                "sample_count": 88,
                "condition_summary": "XLB 5D-SPY 5D 상대강도 >= +1.0%",
                "data_window": "2016-06-20 - 2026-05-29",
                "current_as_of": "2026-05-29",
                "rows": rows,
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("ov-analog-outcome-matrix", html)
        self.assertIn("핵심 자산 비교", html)
        self.assertIn("XLB", html)
        self.assertIn("SPY", html)
        self.assertIn("QQQ", html)
        self.assertIn("5D", html)
        self.assertIn("20D", html)
        self.assertIn("60D", html)
        self.assertNotIn("시장 배경 요약", html)
        self.assertIn("TLT", html)
        self.assertIn("GLD", html)
        self.assertIn("ov-analog-detail-tables", html)
        self.assertIn("<summary>상세 통계</summary>", html)
        self.assertLess(html.index("ov-analog-outcome-matrix"), html.index("ov-analog-detail-tables"))
        for forbidden in ["예측", "추천", "매수", "매도", "신호", "가능성이 높다"]:
            self.assertNotIn(forbidden, html)

    def test_historical_analog_html_turns_insufficient_data_into_actionable_gap_panel(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "INSUFFICIENT_DATA",
                "headline": "과거 유사 맥락 자료 부족",
                "detail": "Financials(XLF) 기준 가격 coverage가 부족합니다.",
                "leadership_sector": "Financial Services",
                "proxy_etf": "XLF",
                "sample_count": 0,
                "data_window": "",
                "rows": [],
                "coverage_gaps": [
                    {"symbol": "XLF", "row_count": 63, "min_rows": 756, "detail": "63 rows from 2026-03-02"},
                    {"symbol": "TLT", "row_count": 140, "min_rows": 756, "detail": "140 rows from 2025-01-02"},
                ],
                "repair_action": {
                    "label": "부족 ETF 가격 이력 보강",
                    "symbols": ["XLF", "TLT"],
                    "period": "10y",
                    "interval": "1d",
                    "target_table": "finance_price.nyse_price_history",
                },
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("ov-analog-gap-panel", html)
        self.assertIn("부족 ETF 가격 이력 보강", html)
        self.assertIn("XLF", html)
        self.assertIn("63 / 756", html)
        self.assertIn("TLT", html)
        self.assertIn("140 / 756", html)
        self.assertIn("아래 자료 수집 버튼", html)
        self.assertNotIn("Macro 조건 비교", html)
        self.assertNotIn("자료가 충분한 sector ETF history가 쌓이면", html)

    def test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "OK",
                "headline": "과거 유사 맥락 3회 발견",
                "detail": "Healthcare(XLV)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Healthcare",
                "proxy_etf": "XLV",
                "sample_count": 3,
                "condition_summary": "XLV 5D-SPY 5D 상대강도 >= +2.0%",
                "data_window": "2024-01-02 - 2024-06-17",
                "rows": [
                    {
                        "asset": "XLV",
                        "horizon": "20D",
                        "median_return_pct": 4.0,
                        "positive_rate_pct": 66.7,
                        "best_return_pct": 8.0,
                        "worst_return_pct": -3.0,
                        "sample_count": 3,
                    }
                ],
                "macro_conditioned_analog": {
                    "schema_version": "overview_market_context_macro_conditioned_analog_pilot_v1",
                    "status": "REVIEW",
                    "status_label": "pilot 표본 좁음",
                    "headline": "Macro 조건 포함 pilot 표본 2회",
                    "detail": "Broad analog 3회 중 GLD context까지 맞는 2회만 표시합니다.",
                    "condition_summary": "XLV relative strength + GLD 5D context",
                    "broad_sample_count": 3,
                    "sample_count": 2,
                    "macro_condition_counts": {
                        "broad": 3,
                        "gld": 2,
                        "futures": 2,
                        "futures_available": 3,
                        "intersection": 2,
                    },
                    "additional_condition_count": 1,
                    "sample_reduction_reason": "Broad 3회 중 Macro 조건 포함 2회만 남았습니다.",
                    "sample_quality": {
                        "status": "REVIEW",
                        "label": "pilot-limited",
                        "detail": "표본이 좁아 broad 결과와 함께 읽어야 합니다.",
                    },
                    "used_conditions": [
                        {"id": "sector_relative_strength", "label": "Sector ETF vs SPY relative strength", "status_label": "사용", "detail": "XLV 5D gap"},
                        {"id": "gld_safe_haven_context", "label": "GLD price proxy", "status_label": "사용", "detail": "GLD 5D 상승 context"},
                        {"id": "futures_rate_pressure_context", "label": "Rate Pressure futures proxy", "status_label": "사용", "detail": "ZN=F/ZB=F 5D through 2024-06-17"},
                    ],
                    "macro_dimension_audit": {
                        "schema_version": "overview_market_context_macro_dimension_audit_v1",
                        "status": "OK",
                        "broad_anchor_count": 3,
                        "conditioned_anchor_count": 2,
                        "dimensions": [
                            {
                                "id": "sector_relative_strength",
                                "label": "Sector ETF vs SPY relative strength",
                                "status": "USED",
                                "anchor_preview_count": 3,
                            },
                            {
                                "id": "gld_safe_haven_context",
                                "label": "GLD price proxy",
                                "status": "USED",
                                "detail": "GLD 5D 상승 context",
                                "anchor_preview_count": 2,
                            },
                            {
                                "id": "futures_rate_pressure_context",
                                "label": "Rate Pressure futures proxy",
                                "status": "USED",
                                "detail": "ZN=F/ZB=F 5D through 2024-06-17",
                                "anchor_preview_count": 2,
                            },
                        ],
                    },
                    "insufficient_conditions": [
                        {"id": "fred_rates", "label": "2Y / 10Y FRED rates", "status_label": "사용 안 함", "detail": "이번 차수 제외"},
                    ],
                    "excluded_conditions": [
                        {"id": "events_sentiment", "label": "Events / sentiment", "status_label": "이번 차수 제외", "detail": "3차-A 범위 밖"},
                    ],
                    "rows": [
                        {
                            "asset": "XLV",
                            "horizon": "20D",
                            "median_return_pct": 5.0,
                            "positive_rate_pct": 100.0,
                            "best_return_pct": 6.0,
                            "worst_return_pct": 4.0,
                            "sample_count": 2,
                        }
                    ],
                },
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("참고: 과거 유사 맥락", html)
        self.assertIn("Macro 조건 후 결과 변화", html)
        self.assertIn("ov-macro-compare-section", html)
        self.assertIn("ov-macro-basis-bar", html)
        self.assertIn("ov-macro-delta-matrix", html)
        self.assertIn("Macro 조건 결과 비교", html)
        self.assertIn("기본 유사 맥락", html)
        self.assertIn("GLD 같은 상태", html)
        self.assertIn("금리선물 같은 상태", html)
        self.assertIn("XLV가 SPY 대비 5D 기준 비슷하게 강했던 구간", html)
        self.assertIn("GLD가 현재처럼 상승 흐름이었던 과거 구간", html)
        self.assertIn("ZN=F/ZB=F가 현재와 비슷한 금리선물 배경이었던 구간", html)
        self.assertIn("기본 유사 맥락 3회 중 Macro 추가 배경까지 현재와 같았던 표본은 2회입니다", html)
        self.assertIn("기본 3회 중 GLD 상태 2회", html)
        self.assertIn("기본 3회 중 금리선물 상태 2회", html)
        self.assertIn("GLD와 금리선물이 모두 같았던 2회", html)
        self.assertIn("두 조건 모두", html)
        self.assertNotIn("GLD 조건 통과 2회 중 금리선물 상태 2회", html)
        self.assertIn("결과 변화", html)
        self.assertNotIn("ov-macro-sample-flow", html)
        self.assertNotIn("ov-macro-delta-table", html)
        self.assertNotIn("ov-macro-funnel-track", html)
        self.assertNotIn("Broad vs Macro 조건 포함", html)
        self.assertNotIn("표본 흐름", html)
        self.assertNotIn("Broad sample", html)
        self.assertNotIn("Macro 조건 sample", html)
        self.assertNotIn("실제로 반영한 조건", html)
        self.assertNotIn("자료 부족으로 적용 못 한 조건", html)
        self.assertNotIn("이번 차수 제외", html)
        self.assertNotIn("사용 조건", html)
        self.assertNotIn("Macro 조건 포함 핵심 자산", html)
        self.assertNotIn("Macro 조건 포함 보조 자산", html)
        self.assertIn("GLD price proxy", html)
        self.assertIn("Rate Pressure futures proxy", html)
        self.assertIn("ZN=F/ZB=F 5D", html)
        self.assertIn("조건 후", html)
        self.assertIn("기본", html)
        self.assertIn("+4.0%", html)
        self.assertIn("+5.0%", html)
        self.assertIn("+1.0%p", html)
        macro_delta_html = html[html.index("Macro 조건 결과 비교") :]
        self.assertIn("has-return-gradient is-positive", macro_delta_html)
        self.assertIn("표본 2회라 broad 결과와 함께 낮춰 읽습니다", html)
        self.assertLess(html.index("참고: 과거 유사 맥락"), html.index("Macro 조건 후 결과 변화"))
        self.assertLess(html.index("ov-historical-analog-limitations"), html.index("ov-macro-compare-section"))
        self.assertNotIn('class="ov-macro-conditioned-pilot"', html)
        self.assertNotIn('class="ov-macro-comparison"', html)
        for forbidden in ["예측", "추천", "매수", "매도", "신호", "가능성이 높다"]:
            self.assertNotIn(forbidden, html)

    def test_historical_analog_html_names_requested_effective_dates_and_macro_condition_roles(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "OK",
                "headline": "과거 유사 맥락 3회 발견",
                "detail": "Healthcare(XLV)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Healthcare",
                "proxy_etf": "XLV",
                "sample_count": 3,
                "condition_summary": "XLV 5D-SPY 5D 상대강도 >= +2.0%",
                "data_window": "2024-01-02 - 2024-05-21",
                "requested_as_of": "2024-06-18",
                "current_as_of": "2024-05-21",
                "as_of_alignment": {
                    "requested_as_of": "2024-06-18",
                    "effective_as_of": "2024-05-21",
                    "is_aligned": False,
                    "reason": "요청 기준일보다 이른 DB 공통 가격 기준으로 계산했습니다.",
                    "limiting_symbols": ["SPY", "QQQ", "GLD"],
                    "latest_by_symbol": {"XLV": "2024-06-18", "SPY": "2024-05-21"},
                },
                "basis_warnings": [
                    "선택 기준일 2024-06-18은 SPY, QQQ, GLD 공통 가격 기준 2024-05-21로 계산했습니다."
                ],
                "rows": [
                    {
                        "asset": "XLV",
                        "horizon": "20D",
                        "median_return_pct": 4.0,
                        "positive_rate_pct": 66.7,
                        "best_return_pct": 8.0,
                        "worst_return_pct": -3.0,
                        "sample_count": 3,
                    }
                ],
                "macro_conditioned_analog": {
                    "schema_version": "overview_market_context_macro_conditioned_analog_pilot_v1",
                    "status": "REVIEW",
                    "status_label": "pilot 표본 좁음",
                    "headline": "Macro 조건 포함 pilot 표본 1회",
                    "detail": "기존 broad analog 3회 중 추가 macro context까지 맞는 1회만 별도로 봅니다.",
                    "condition_summary": "XLV relative strength + GLD 5D context + Rate Pressure futures proxy",
                    "broad_sample_count": 3,
                    "sample_count": 1,
                    "additional_condition_count": 2,
                    "sample_reduction_reason": "Broad 3회 중 Macro 조건 포함 1회만 남았습니다.",
                    "sample_quality": {
                        "status": "REVIEW",
                        "label": "pilot-limited",
                        "detail": "broad 결과와 함께 읽어야 합니다.",
                    },
                    "used_conditions": [
                        {"id": "sector_relative_strength", "label": "Sector ETF vs SPY relative strength", "status_label": "사용", "detail": "XLV 5D gap"},
                        {"id": "gld_safe_haven_context", "label": "GLD price proxy", "status_label": "사용", "detail": "GLD 5D 중립권"},
                        {"id": "futures_rate_pressure_context", "label": "Rate Pressure futures proxy", "status_label": "사용", "detail": "ZN=F/ZB=F 5D"},
                    ],
                    "insufficient_conditions": [
                        {"id": "fred_rates", "label": "2Y / 10Y FRED rates", "status_label": "사용 안 함", "detail": "이번 화면에서는 참고만 표시"},
                    ],
                    "excluded_conditions": [
                        {"id": "events_sentiment", "label": "Events / sentiment", "status_label": "이번 차수 제외", "detail": "annotation only"},
                    ],
                    "rows": [],
                },
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("선택 기준일과 실제 계산일이 다릅니다", html)
        self.assertIn("요청 기준일", html)
        self.assertIn("실제 계산 기준일", html)
        self.assertIn("2024-06-18", html)
        self.assertIn("2024-05-21", html)
        self.assertIn("기본 유사 맥락 기준", html)
        self.assertIn("GLD 조건 적용", html)
        self.assertIn("금리선물 조건 적용", html)
        self.assertIn("XLV가 SPY 대비 5D 기준 비슷하게 강했던 구간", html)
        self.assertIn("GLD가 현재처럼 중립권이었던 과거 구간", html)
        self.assertIn("ZN=F/ZB=F가 현재와 비슷한 금리선물 배경이었던 구간", html)
        self.assertIn("Sector ETF vs SPY relative strength", html)
        self.assertIn("GLD price proxy", html)
        self.assertIn("Rate Pressure futures proxy", html)
        self.assertLess(html.index("기본 유사 맥락 기준"), html.index("GLD 조건 적용"))
        macro_conditions = html[html.index("GLD 조건 적용") :]
        self.assertNotIn("Sector ETF vs SPY relative strength</strong>", macro_conditions)
        self.assertNotIn("실제로 반영한 조건", html)
        self.assertNotIn("자료 부족으로 적용 못 한 조건", html)
        self.assertNotIn("참고만 하는 정보", html)
        for forbidden in ["예측", "추천", "매수", "매도", "신호", "가능성이 높다", "PASS", "BLOCKER"]:
            self.assertNotIn(forbidden, html)

    def test_historical_analog_html_renders_macro_dimension_audit_inside_pilot(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "OK",
                "headline": "과거 유사 맥락 3회 발견",
                "detail": "Healthcare(XLV)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Healthcare",
                "proxy_etf": "XLV",
                "sample_count": 3,
                "condition_summary": "XLV 5D-SPY 5D 상대강도 >= +2.0%",
                "rows": [
                    {
                        "asset": "XLV",
                        "horizon": "20D",
                        "median_return_pct": 4.0,
                        "positive_rate_pct": 66.7,
                        "best_return_pct": 8.0,
                        "worst_return_pct": -3.0,
                        "sample_count": 3,
                    }
                ],
                "macro_conditioned_analog": {
                    "schema_version": "overview_market_context_macro_conditioned_analog_pilot_v1",
                    "status": "REVIEW",
                    "status_label": "pilot 표본 좁음",
                    "headline": "Macro 조건 포함 pilot 표본 1회",
                    "detail": "기존 broad analog 3회 중 추가 macro context까지 맞는 1회만 별도로 봅니다.",
                    "condition_summary": "XLV relative strength + GLD 5D context",
                    "broad_sample_count": 3,
                    "sample_count": 1,
                    "additional_condition_count": 2,
                    "sample_reduction_reason": "Broad 3회 중 Macro 조건 포함 1회만 남았습니다.",
                    "sample_quality": {
                        "status": "REVIEW",
                        "label": "pilot-limited",
                        "detail": "broad 결과와 함께 읽어야 합니다.",
                    },
                    "used_conditions": [
                        {"id": "sector_relative_strength", "label": "Sector ETF vs SPY relative strength", "status_label": "사용", "detail": "XLV 5D gap"},
                        {"id": "gld_safe_haven_context", "label": "GLD price proxy", "status_label": "사용", "detail": "GLD 5D 상승 context"},
                    ],
                    "insufficient_conditions": [],
                    "excluded_conditions": [],
                    "macro_dimension_audit": {
                        "schema_version": "overview_market_context_macro_dimension_audit_v1",
                        "status": "OK",
                        "summary": "3개 차원은 실제 조건, 3개 macro series는 참고 preview, event/sentiment는 보류입니다.",
                        "broad_anchor_count": 3,
                        "conditioned_anchor_count": 1,
                        "dimensions": [
                            {
                                "id": "sector_relative_strength",
                                "label": "Sector ETF vs SPY",
                                "status": "USED",
                                "status_label": "사용",
                                "usage": "hard condition",
                                "source": "DB price history",
                                "detail": "Broad anchor condition",
                                "latest_date": "2024-05-06",
                                "coverage_start": "2024-01-02",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 3,
                            },
                            {
                                "id": "macro_t10y3m",
                                "label": "T10Y3M yield curve proxy",
                                "status": "AVAILABLE_REFERENCE",
                                "status_label": "참고",
                                "usage": "bucket preview only",
                                "source": "finance.loaders.macro.load_macro_series_observations",
                                "detail": "Current bucket inverted; broad anchors with same bucket: 2.",
                                "latest_date": "2024-05-06",
                                "current_value": -0.25,
                                "current_bucket": "yield curve inverted",
                                "coverage_start": "2024-01-02",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 2,
                            },
                            {
                                "id": "macro_vixcls",
                                "label": "VIXCLS volatility backdrop",
                                "status": "AVAILABLE_REFERENCE",
                                "status_label": "참고",
                                "usage": "bucket preview only",
                                "source": "finance.loaders.macro.load_macro_series_observations",
                                "detail": "Current bucket calm; broad anchors with same bucket: 2.",
                                "latest_date": "2024-05-06",
                                "current_value": 16.2,
                                "current_bucket": "volatility calm",
                                "coverage_start": "2024-01-02",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 2,
                            },
                            {
                                "id": "macro_baa10y",
                                "label": "BAA10Y credit spread backdrop",
                                "status": "AVAILABLE_REFERENCE",
                                "status_label": "참고",
                                "usage": "bucket preview only",
                                "source": "finance.loaders.macro.load_macro_series_observations",
                                "detail": "Current bucket contained; broad anchors with same bucket: 2.",
                                "latest_date": "2024-05-06",
                                "current_value": 1.7,
                                "current_bucket": "credit spread contained",
                                "coverage_start": "2024-01-02",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 2,
                            },
                            {
                                "id": "events_calendar",
                                "label": "Events calendar",
                                "status": "DEFERRED",
                                "status_label": "보류",
                                "usage": "annotation only",
                                "source": "build_market_events_snapshot / build_overview_macro_week_lane",
                                "detail": "Near-term event context remains annotation; not applied to anchors.",
                                "latest_date": "2024-05-06",
                                "coverage_start": "2024-05-06",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 0,
                            },
                            {
                                "id": "macro_t10y2y",
                                "label": "T10Y2Y yield spread",
                                "status": "AVAILABLE_REFERENCE",
                                "status_label": "참고",
                                "usage": "bucket preview only",
                                "source": "finance.loaders.macro.load_macro_series_observations",
                                "detail": "Reference preview only.",
                                "latest_date": "2024-05-06",
                                "coverage_start": "2024-01-02",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 1,
                            },
                            {
                                "id": "macro_dff",
                                "label": "DFF policy rate",
                                "status": "AVAILABLE_REFERENCE",
                                "status_label": "참고",
                                "usage": "bucket preview only",
                                "source": "finance.loaders.macro.load_macro_series_observations",
                                "detail": "Reference preview only.",
                                "latest_date": "2024-05-06",
                                "coverage_start": "2024-01-02",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 1,
                            },
                            {
                                "id": "macro_unrate",
                                "label": "UNRATE labor backdrop",
                                "status": "AVAILABLE_REFERENCE",
                                "status_label": "참고",
                                "usage": "bucket preview only",
                                "source": "finance.loaders.macro.load_macro_series_observations",
                                "detail": "Reference preview only.",
                                "latest_date": "2024-05-06",
                                "coverage_start": "2024-01-02",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 1,
                            },
                            {
                                "id": "sentiment_aaii",
                                "label": "AAII sentiment backdrop",
                                "status": "DEFERRED",
                                "status_label": "보류",
                                "usage": "annotation only",
                                "source": "finance.loaders.sentiment",
                                "detail": "Sentiment remains annotation and is not applied to anchors.",
                                "latest_date": "2024-05-06",
                                "coverage_start": "2024-05-06",
                                "coverage_end": "2024-05-06",
                                "anchor_preview_count": 0,
                            },
                        ],
                    },
                    "rows": [],
                },
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("조건에는 쓰지 않은 Macro 배경", html)
        self.assertIn("참고 전용", html)
        self.assertIn("Macro 조건 상세", html)
        self.assertIn("T10Y3M yield curve proxy", html)
        self.assertIn("VIXCLS volatility backdrop", html)
        self.assertIn("BAA10Y credit spread backdrop", html)
        self.assertIn("10년물-3개월물 금리차", html)
        self.assertIn("VIX 지수", html)
        self.assertIn("BAA 회사채와 10년 국채 금리차", html)
        self.assertIn("Events calendar", html)
        self.assertIn("AAII sentiment backdrop", html)
        self.assertIn("ov-macro-backdrop-grid", html)
        self.assertIn("ov-macro-backdrop-state", html)
        self.assertIn("ov-macro-backdrop-ratio", html)
        self.assertIn("ov-macro-backdrop-fill", html)
        self.assertIn("ov-macro-dimension-group", html)
        self.assertIn("역전 금리곡선", html)
        self.assertIn("단기금리가 장기금리보다 높아진 역전 구간입니다.", html)
        self.assertIn("변동성 안정권", html)
        self.assertIn("VIX가 18 아래라 변동성은 비교적 안정권입니다.", html)
        self.assertIn("신용위험 안정권", html)
        self.assertIn("스프레드가 2%p 아래라 신용 부담은 안정권입니다.", html)
        self.assertIn("2 / 3", html)
        self.assertIn("참고", html)
        self.assertIn("보류", html)
        self.assertIn("같은 상태 2 / 3", html)
        self.assertIn("조건에는 쓰지 않은 참고 배경입니다", html)
        self.assertLess(html.index("조건에는 쓰지 않은 Macro 배경"), html.index("Macro 조건 상세"))
        for forbidden in ["예측", "추천", "매수", "매도", "신호", "가능성이 높다", "PASS", "BLOCKER"]:
            self.assertNotIn(forbidden, html)

    def test_historical_analog_html_uses_median_strength_gradient_for_matrix(self) -> None:
        from app.web.overview_ui_components import _macro_cockpit_historical_analog_html

        html = _macro_cockpit_historical_analog_html(
            {
                "status": "OK",
                "headline": "과거 유사 맥락 10회 발견",
                "detail": "Technology(XLK)가 SPY 대비 강했던 과거 구간 기준",
                "leadership_sector": "Technology",
                "proxy_etf": "XLK",
                "sample_count": 10,
                "condition_summary": "XLK 5D-SPY 5D 상대강도 >= +1.0%",
                "rows": [
                    {
                        "asset": "XLK",
                        "horizon": "5D",
                        "median_return_pct": 0.4,
                        "positive_rate_pct": 60.0,
                        "best_return_pct": 3.0,
                        "worst_return_pct": -2.0,
                        "sample_count": 10,
                    },
                    {
                        "asset": "XLK",
                        "horizon": "20D",
                        "median_return_pct": 8.0,
                        "positive_rate_pct": 90.0,
                        "best_return_pct": 12.0,
                        "worst_return_pct": -3.0,
                        "sample_count": 10,
                    },
                    {
                        "asset": "TLT",
                        "horizon": "20D",
                        "median_return_pct": -7.0,
                        "positive_rate_pct": 20.0,
                        "best_return_pct": 2.0,
                        "worst_return_pct": -9.0,
                        "sample_count": 10,
                    },
                ],
                "limitations": ["과거 통계는 미래 움직임 보장이 아님"],
            }
        )

        self.assertIn("--ov-analog-cell-strength:4.8%", html)
        self.assertIn("--ov-analog-cell-strength:20.0%", html)
        self.assertIn("--ov-analog-cell-strength:18.0%", html)
        self.assertIn("has-return-gradient is-positive", html)
        self.assertIn("has-return-gradient is-negative", html)
        self.assertIn("색상은 중간값 방향과 크기 기준", html)

    def test_sector_pressure_map_renders_weighted_returns_with_two_decimals(self) -> None:
        from app.web.overview_ui_components import _sector_pressure_map_html

        html = _sector_pressure_map_html(
            {
                "summary": {"headline": "Mixed participation"},
                "coverage": {"freshness": "2026-06-20 13:57"},
                "heatmap_rows": [
                    {
                        "group": "Technology",
                        "market_cap_weighted_return_pct": 1.234,
                        "positive_symbol_share_pct": 55.5,
                        "symbols": 82,
                        "tone": "positive",
                    }
                ],
            }
        )

        self.assertIn("+1.23%", html)
        self.assertNotIn("+1.2%", html)


class FuturesMarketMonitoringContractTests(unittest.TestCase):
    def test_futures_monitor_snapshot_scores_moves_and_stale_state(self) -> None:
        from app.services.futures_market_monitoring import build_futures_monitor_snapshot

        base = pd.Timestamp("2026-06-02 00:00:00", tz=timezone.utc)
        candle_rows: list[dict[str, object]] = []
        for idx in range(0, 61):
            ts = base - pd.Timedelta(minutes=60 - idx)
            es_close = 100.0 + idx * 0.01
            nq_close = 100.0 + idx * 0.025
            for symbol, close in (("ES=F", es_close), ("NQ=F", nq_close)):
                candle_rows.append(
                    {
                        "provider_symbol": symbol,
                        "interval_code": "1m",
                        "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": close - 0.05,
                        "high": close + 0.1,
                        "low": close - 0.1,
                        "close": close,
                        "volume": 1000 + idx,
                        "source": "yfinance",
                        "provider_status": "ok",
                    }
                )

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_instrument" in sql:
                return [
                    {"provider_symbol": "ES=F", "display_name": "E-mini S&P 500", "futures_group": "Equity Index", "source": "yfinance", "sort_order": 10},
                    {"provider_symbol": "NQ=F", "display_name": "E-mini Nasdaq 100", "futures_group": "Equity Index", "source": "yfinance", "sort_order": 20},
                ]
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            if "FROM futures_market_monitor_run" in sql:
                self.assertIn("WHERE interval_code = %s", sql)
                self.assertEqual(params, ["1m"])
                return [
                    {
                        "run_id": "run-1",
                        "interval_code": "1m",
                        "status": "success",
                        "symbols_requested": 2,
                        "symbols_processed": 2,
                        "rows_written": len(candle_rows),
                        "latest_candle_time_utc": "2026-06-02 00:00:00",
                        "finished_at": "2026-06-02 00:00:01",
                    }
                ]
            return []

        snapshot = build_futures_monitor_snapshot(
            group="Equity Index",
            symbols=["ES=F", "NQ=F"],
            selected_symbol="NQ=F",
            now=datetime(2026, 6, 2, 0, 1, tzinfo=timezone.utc),
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 2)
        self.assertEqual(snapshot["selected_symbol"], "NQ=F")
        self.assertFalse(snapshot["candles"].empty)
        self.assertFalse(snapshot["all_candles"].empty)
        self.assertEqual(set(snapshot["all_candles"]["Symbol"]), {"ES=F", "NQ=F"})
        self.assertEqual(snapshot["top_move"]["Symbol"], "NQ=F")
        nq_row = snapshot["rows"][snapshot["rows"]["Symbol"] == "NQ=F"].iloc[0]
        self.assertEqual(nq_row["State"], "Sharp")
        self.assertGreater(nq_row["60m %"], 1.0)

    def test_futures_monitor_anchors_chart_window_to_latest_stored_candle(self) -> None:
        from app.services.futures_market_monitoring import build_futures_monitor_snapshot

        latest = pd.Timestamp("2026-06-05 21:00:00", tz=timezone.utc)
        candle_rows: list[dict[str, object]] = []
        for idx in range(0, 61):
            ts = latest - pd.Timedelta(minutes=60 - idx)
            candle_rows.append(
                {
                    "provider_symbol": "NQ=F",
                    "interval_code": "1m",
                    "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": 19000.0 + idx,
                    "high": 19001.0 + idx,
                    "low": 18999.0 + idx,
                    "close": 19000.5 + idx,
                    "volume": 1000 + idx,
                    "source": "yfinance",
                    "provider_status": "ok",
                }
            )
        candle_sqls: list[str] = []

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_instrument" in sql:
                return [
                    {
                        "provider_symbol": "NQ=F",
                        "display_name": "E-mini Nasdaq 100",
                        "futures_group": "Equity Index",
                        "source": "yfinance",
                        "sort_order": 20,
                    }
                ]
            if "FROM futures_ohlcv" in sql:
                candle_sqls.append(sql)
                if "UTC_TIMESTAMP" in sql:
                    return []
                return candle_rows
            if "FROM futures_market_monitor_run" in sql:
                return [
                    {
                        "run_id": "run-stale",
                        "interval_code": "1m",
                        "status": "success",
                        "symbols_requested": 1,
                        "symbols_processed": 1,
                        "rows_written": len(candle_rows),
                        "latest_candle_time_utc": "2026-06-05 21:00:00",
                        "finished_at": "2026-06-05 21:00:01",
                    }
                ]
            return []

        snapshot = build_futures_monitor_snapshot(
            group="Equity Index",
            symbols=["NQ=F"],
            selected_symbol="NQ=F",
            lookback_minutes=60,
            now=datetime(2026, 6, 6, 9, 0, tzinfo=timezone.utc),
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "REVIEW")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 1)
        self.assertFalse(snapshot["candles"].empty)
        nq_row = snapshot["rows"][snapshot["rows"]["Symbol"] == "NQ=F"].iloc[0]
        self.assertEqual(nq_row["State"], "Stale")
        self.assertEqual(nq_row["Latest Candle UTC"], "2026-06-05 21:00")
        self.assertTrue(candle_sqls)
        self.assertNotIn("UTC_TIMESTAMP", candle_sqls[0])

    def test_futures_monitor_preopen_core_uses_cross_asset_symbols(self) -> None:
        from app.services.futures_market_monitoring import build_futures_monitor_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_instrument" in sql:
                return [
                    {"provider_symbol": "NQ=F", "display_name": "E-mini Nasdaq 100", "futures_group": "Equity Index", "source": "yfinance", "sort_order": 20},
                    {"provider_symbol": "ZN=F", "display_name": "10Y Treasury Note", "futures_group": "Rates", "source": "yfinance", "sort_order": 110},
                    {"provider_symbol": "CL=F", "display_name": "WTI Crude Oil", "futures_group": "Commodities", "source": "yfinance", "sort_order": 210},
                    {"provider_symbol": "6E=F", "display_name": "Euro FX", "futures_group": "FX Futures", "source": "yfinance", "sort_order": 310},
                ]
            return []

        snapshot = build_futures_monitor_snapshot(group="Pre-open Core", query_fn=query_fn)

        self.assertEqual(snapshot["symbols"], ["NQ=F", "ZN=F", "CL=F", "6E=F"])
        self.assertEqual(snapshot["selected_symbol"], "NQ=F")
        self.assertIn("Pre-open Core", snapshot["groups"])

    def test_futures_collector_normalizes_yfinance_frame_and_records_run(self) -> None:
        from finance.data import futures_market as fm

        idx = pd.date_range("2026-06-02 00:00:00", periods=120, freq="min", tz=timezone.utc)
        frame = pd.DataFrame(
            {
                ("Open", "ES=F"): [100.0 + idx * 0.01 for idx in range(120)],
                ("High", "ES=F"): [101.0 + idx * 0.01 for idx in range(120)],
                ("Low", "ES=F"): [99.0 + idx * 0.01 for idx in range(120)],
                ("Close", "ES=F"): [100.5 + idx * 0.01 for idx in range(120)],
                ("Adj Close", "ES=F"): [100.5 + idx * 0.01 for idx in range(120)],
                ("Volume", "ES=F"): [1000 + idx for idx in range(120)],
            },
            index=idx,
        )

        written_rows: list[dict[str, object]] = []
        run_rows: list[dict[str, object]] = []

        def downloader(symbols, *, period, interval):
            self.assertEqual(symbols, ["ES=F"])
            self.assertEqual(period, "1d")
            self.assertEqual(interval, "1m")
            return frame

        def capture_ohlcv(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        def capture_run(row, **kwargs):
            del kwargs
            run_rows.append(row)
            return 1

        with (
            patch.object(fm, "sync_futures_market_tables", return_value=None),
            patch.object(fm, "upsert_futures_instruments", return_value=1),
            patch.object(fm, "upsert_futures_ohlcv_rows", side_effect=capture_ohlcv),
            patch.object(fm, "upsert_futures_monitor_run", side_effect=capture_run),
        ):
            result = fm.collect_and_store_futures_ohlcv(
                ["ES=F"],
                period="1d",
                interval="1m",
                downloader=downloader,
                sleep_sec=0,
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 120)
        self.assertEqual(result["symbols_processed"], 1)
        self.assertEqual(written_rows[0]["provider_symbol"], "ES=F")
        self.assertEqual(written_rows[0]["interval_code"], "1m")
        self.assertEqual(written_rows[0]["provider_status"], "ok")
        self.assertEqual(run_rows[0]["status"], "success")
        self.assertEqual(run_rows[0]["latest_candle_time_utc"], "2026-06-02 01:59:00")

    def test_futures_collector_recovers_empty_1d_intraday_symbols_with_2d_retry(self) -> None:
        from finance.data import futures_market as fm

        one_day_idx = pd.date_range("2026-06-03 04:00:00", periods=120, freq="min", tz=timezone.utc)
        one_day_frame = pd.DataFrame(
            {
                ("Open", "NQ=F"): [None] * 120,
                ("High", "NQ=F"): [None] * 120,
                ("Low", "NQ=F"): [None] * 120,
                ("Close", "NQ=F"): [None] * 120,
                ("Adj Close", "NQ=F"): [None] * 120,
                ("Volume", "NQ=F"): [None] * 120,
                ("Open", "ZN=F"): [110.0 + idx * 0.01 for idx in range(120)],
                ("High", "ZN=F"): [110.2 + idx * 0.01 for idx in range(120)],
                ("Low", "ZN=F"): [109.9 + idx * 0.01 for idx in range(120)],
                ("Close", "ZN=F"): [110.1 + idx * 0.01 for idx in range(120)],
                ("Adj Close", "ZN=F"): [110.1 + idx * 0.01 for idx in range(120)],
                ("Volume", "ZN=F"): [100 + idx for idx in range(120)],
            },
            index=one_day_idx,
        )
        two_day_idx = pd.date_range("2026-06-03 03:58:00", periods=2, freq="min", tz=timezone.utc)
        two_day_frame = pd.DataFrame(
            {
                ("Open", "NQ=F"): [19000.0, 19001.0],
                ("High", "NQ=F"): [19002.0, 19003.0],
                ("Low", "NQ=F"): [18999.0, 19000.0],
                ("Close", "NQ=F"): [19001.0, 19002.0],
                ("Adj Close", "NQ=F"): [19001.0, 19002.0],
                ("Volume", "NQ=F"): [500, 520],
            },
            index=two_day_idx,
        )
        calls: list[tuple[tuple[str, ...], str, str]] = []
        written_rows: list[dict[str, object]] = []
        run_rows: list[dict[str, object]] = []

        def downloader(symbols, *, period, interval):
            calls.append((tuple(symbols), period, interval))
            if period == "1d":
                return one_day_frame
            if period == "2d":
                return two_day_frame
            return pd.DataFrame()

        def capture_ohlcv(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        def capture_run(row, **kwargs):
            del kwargs
            run_rows.append(row)
            return 1

        with (
            patch.object(fm, "sync_futures_market_tables", return_value=None),
            patch.object(fm, "upsert_futures_instruments", return_value=1),
            patch.object(fm, "upsert_futures_ohlcv_rows", side_effect=capture_ohlcv),
            patch.object(fm, "upsert_futures_monitor_run", side_effect=capture_run),
        ):
            result = fm.collect_and_store_futures_ohlcv(
                ["NQ=F", "ZN=F"],
                period="1d",
                interval="1m",
                downloader=downloader,
                sleep_sec=0,
            )

        self.assertEqual(calls, [(("NQ=F", "ZN=F"), "1d", "1m"), (("NQ=F",), "2d", "1m")])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 122)
        self.assertEqual(result["symbols_processed"], 2)
        self.assertEqual(result["failed_symbols"], [])
        self.assertEqual({row["provider_symbol"] for row in written_rows}, {"NQ=F", "ZN=F"})
        self.assertEqual(run_rows[0]["status"], "success")
        self.assertEqual(run_rows[0]["failed_symbols_json"], [])
        self.assertEqual(run_rows[0]["diagnostics_json"]["fallback_retries"][0]["period"], "2d")

    def test_futures_collector_recovers_sparse_1d_intraday_symbols_with_2d_retry(self) -> None:
        from finance.data import futures_market as fm

        sparse_idx = pd.date_range("2026-06-03 04:00:00", periods=24, freq="min", tz=timezone.utc)
        full_idx = pd.date_range("2026-06-02 22:35:00", periods=180, freq="min", tz=timezone.utc)
        one_day_frame = pd.DataFrame(
            {
                ("Open", "CL=F"): [94.0 + idx * 0.01 for idx in range(24)],
                ("High", "CL=F"): [94.1 + idx * 0.01 for idx in range(24)],
                ("Low", "CL=F"): [93.9 + idx * 0.01 for idx in range(24)],
                ("Close", "CL=F"): [94.05 + idx * 0.01 for idx in range(24)],
                ("Adj Close", "CL=F"): [94.05 + idx * 0.01 for idx in range(24)],
                ("Volume", "CL=F"): [10 + idx for idx in range(24)],
            },
            index=sparse_idx,
        )
        two_day_frame = pd.DataFrame(
            {
                ("Open", "CL=F"): [93.0 + idx * 0.01 for idx in range(180)],
                ("High", "CL=F"): [93.1 + idx * 0.01 for idx in range(180)],
                ("Low", "CL=F"): [92.9 + idx * 0.01 for idx in range(180)],
                ("Close", "CL=F"): [93.05 + idx * 0.01 for idx in range(180)],
                ("Adj Close", "CL=F"): [93.05 + idx * 0.01 for idx in range(180)],
                ("Volume", "CL=F"): [100 + idx for idx in range(180)],
            },
            index=full_idx,
        )
        calls: list[tuple[tuple[str, ...], str, str]] = []
        written_rows: list[dict[str, object]] = []
        run_rows: list[dict[str, object]] = []

        def downloader(symbols, *, period, interval):
            calls.append((tuple(symbols), period, interval))
            if period == "1d":
                return one_day_frame
            if period == "2d":
                return two_day_frame
            return pd.DataFrame()

        def capture_ohlcv(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        def capture_run(row, **kwargs):
            del kwargs
            run_rows.append(row)
            return 1

        with (
            patch.object(fm, "sync_futures_market_tables", return_value=None),
            patch.object(fm, "upsert_futures_instruments", return_value=1),
            patch.object(fm, "upsert_futures_ohlcv_rows", side_effect=capture_ohlcv),
            patch.object(fm, "upsert_futures_monitor_run", side_effect=capture_run),
        ):
            result = fm.collect_and_store_futures_ohlcv(
                ["CL=F"],
                period="1d",
                interval="1m",
                downloader=downloader,
                sleep_sec=0,
            )

        self.assertEqual(calls, [(("CL=F",), "1d", "1m"), (("CL=F",), "2d", "1m")])
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 180)
        self.assertEqual(result["failed_symbols"], [])
        self.assertEqual(len(written_rows), 180)
        self.assertEqual(written_rows[0]["candle_time_utc"], "2026-06-02 22:35:00")
        retry = run_rows[0]["diagnostics_json"]["fallback_retries"][0]
        self.assertEqual(retry["symbols"], ["CL=F"])
        self.assertEqual(retry["recovered_symbols"], ["CL=F"])
        self.assertEqual(retry["reason"], "sparse_1d_intraday_rows")
        self.assertEqual(retry["initial_rows_by_symbol"], {"CL=F": 24})

    def test_ingestion_job_wraps_futures_collection_summary(self) -> None:
        from app.jobs import ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_futures_ohlcv",
            return_value={
                "run_id": "run-job",
                "source": "yfinance",
                "period": "1d",
                "interval": "1m",
                "cadence_mode": "manual",
                "status": "partial_success",
                "rows_written": 10,
                "symbols_requested": 2,
                "symbols_processed": 1,
                "failed_symbols": ["NQ=F"],
                "latest_candle_time_utc": "2026-06-02 00:01:00",
                "diagnostics": {"batches": []},
            },
        ):
            result = jobs.run_collect_futures_ohlcv(["ES=F", "NQ=F"], max_symbols=2)

        self.assertEqual(result["job_name"], "collect_futures_ohlcv")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 10)
        self.assertEqual(result["failed_symbols"], ["NQ=F"])
        self.assertEqual(result["details"]["target_tables"][0], "finance_price.futures_ohlcv")


class FuturesMacroThermometerContractTests(unittest.TestCase):
    def _macro_score_frame(self, values: dict[str, int]) -> pd.DataFrame:
        return pd.DataFrame([{"Score": score, "Value": value} for score, value in values.items()])

    def _macro_symbol_frame(self, values: dict[str, float]) -> pd.DataFrame:
        return pd.DataFrame([{"Symbol": symbol, "Std Move": value} for symbol, value in values.items()])

    def _daily_rows(self, final_moves: dict[str, float], *, days: int = 260) -> list[dict[str, object]]:
        base = pd.Timestamp(date.today().isoformat(), tz=timezone.utc) - pd.Timedelta(days=days - 1)
        rows: list[dict[str, object]] = []
        for symbol_index, (symbol, final_move) in enumerate(final_moves.items()):
            price = 100.0 + symbol_index * 7.0
            for idx in range(days):
                daily_move = 0.0003 + 0.003 * ((idx % 9) - 4) / 4
                if idx == days - 1:
                    daily_move = final_move
                price *= 1.0 + daily_move
                ts = base + pd.Timedelta(days=idx)
                rows.append(
                    {
                        "provider_symbol": symbol,
                        "interval_code": "1d",
                        "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": price * 0.995,
                        "high": price * 1.005,
                        "low": price * 0.99,
                        "close": price,
                        "volume": 1000 + idx,
                        "source": "yfinance",
                        "provider_status": "ok",
                    }
                )
        return rows

    def _daily_rows_with_recent_5d_moves(
        self,
        five_day_moves: dict[str, float],
        *,
        days: int = 260,
    ) -> list[dict[str, object]]:
        base = pd.Timestamp(date.today().isoformat(), tz=timezone.utc) - pd.Timedelta(days=days - 1)
        rows: list[dict[str, object]] = []
        for symbol_index, (symbol, five_day_move) in enumerate(five_day_moves.items()):
            price = 100.0 + symbol_index * 7.0
            recent_daily_move = (1.0 + five_day_move) ** (1 / 5) - 1.0
            for idx in range(days):
                daily_move = 0.0002
                if idx >= days - 5:
                    daily_move = recent_daily_move
                price *= 1.0 + daily_move
                ts = base + pd.Timedelta(days=idx)
                rows.append(
                    {
                        "provider_symbol": symbol,
                        "interval_code": "1d",
                        "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": price * 0.995,
                        "high": price * 1.005,
                        "low": price * 0.99,
                        "close": price,
                        "volume": 1000 + idx,
                        "source": "yfinance",
                        "provider_status": "ok",
                    }
                )
        return rows

    def _risk_on_validation_rows(self, *, days: int = 150) -> tuple[list[str], list[dict[str, object]]]:
        symbols = [
            "ES=F",
            "NQ=F",
            "YM=F",
            "RTY=F",
            "ZN=F",
            "ZB=F",
            "CL=F",
            "GC=F",
            "SI=F",
            "HG=F",
            "NG=F",
            "6E=F",
            "6J=F",
            "6B=F",
            "6A=F",
            "6C=F",
        ]
        risk_growth = {"ES=F", "NQ=F", "YM=F", "RTY=F", "HG=F", "CL=F", "6A=F"}
        event_indices = {80, 105}
        base = pd.Timestamp("2026-01-01 00:00:00", tz=timezone.utc)
        rows: list[dict[str, object]] = []
        prices = {symbol: 100.0 + idx * 5.0 for idx, symbol in enumerate(symbols)}
        for idx in range(days):
            for symbol in symbols:
                daily_move = 0.0004 + 0.002 * ((idx % 7) - 3) / 3
                if idx in event_indices and symbol in risk_growth:
                    daily_move = 0.02
                elif any(event_idx < idx <= event_idx + 5 for event_idx in event_indices) and symbol in risk_growth:
                    daily_move = 0.006
                elif idx in event_indices and symbol in {"ZN=F", "ZB=F", "6E=F", "6J=F", "6B=F", "6C=F"}:
                    daily_move = 0.001
                prices[symbol] *= 1.0 + daily_move
                ts = base + pd.Timedelta(days=idx)
                rows.append(
                    {
                        "provider_symbol": symbol,
                        "interval_code": "1d",
                        "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": prices[symbol] * 0.995,
                        "high": prices[symbol] * 1.005,
                        "low": prices[symbol] * 0.99,
                        "close": prices[symbol],
                        "volume": 1000 + idx,
                        "source": "yfinance",
                        "provider_status": "ok",
                    }
                )
        return symbols, rows

    def test_macro_thermometer_inverts_rates_and_fx_pressure(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        symbols = [
            "ES=F",
            "NQ=F",
            "YM=F",
            "RTY=F",
            "ZN=F",
            "ZB=F",
            "CL=F",
            "GC=F",
            "SI=F",
            "HG=F",
            "NG=F",
            "6E=F",
            "6J=F",
            "6B=F",
            "6A=F",
            "6C=F",
        ]
        final_moves = {symbol: 0.001 for symbol in symbols}
        final_moves.update(
            {
                "ES=F": 0.018,
                "NQ=F": 0.024,
                "YM=F": 0.014,
                "RTY=F": 0.02,
                "ZN=F": -0.012,
                "ZB=F": -0.014,
                "6E=F": -0.01,
                "6J=F": -0.008,
                "6B=F": -0.011,
                "6A=F": -0.009,
                "6C=F": -0.008,
            }
        )
        candle_rows = self._daily_rows(final_moves)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=symbols, query_fn=query_fn)
        scores = snapshot["scores"].set_index("Score")

        self.assertEqual(snapshot["status"], "OK")
        self.assertGreater(scores.loc["Risk-On Score", "Value"], 20)
        self.assertGreater(scores.loc["Rate Pressure Score", "Value"], 20)
        self.assertGreater(scores.loc["Dollar Pressure Score", "Value"], 20)
        rate_components = snapshot["score_components"]
        zn_component = rate_components[
            (rate_components["Score"] == "Rate Pressure Score") & (rate_components["Symbol"] == "ZN=F")
        ].iloc[0]
        self.assertLess(zn_component["Raw Std Move"], 0)
        self.assertGreater(zn_component["Score Move"], 0)

    def test_macro_thermometer_detects_rate_pressure_scenario(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        symbols = ["ES=F", "NQ=F", "RTY=F", "ZN=F", "ZB=F", "GC=F", "HG=F", "CL=F", "6A=F"]
        final_moves = {symbol: 0.001 for symbol in symbols}
        final_moves.update({"NQ=F": -0.025, "ZN=F": -0.015, "ZB=F": -0.017, "GC=F": -0.018})
        candle_rows = self._daily_rows(final_moves)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=symbols, query_fn=query_fn)

        self.assertEqual(snapshot["summary"]["scenario"], "금리 상승 부담")
        self.assertIn("금리 상승 압력", snapshot["summary"]["summary"])
        self.assertGreater(snapshot["scores"].set_index("Score").loc["Rate Pressure Score", "Value"], 20)

    def test_macro_interpretation_explains_weak_growth_without_safe_haven_confirmation(self) -> None:
        from app.services.futures_macro_thermometer import generate_market_interpretation

        interpretation = generate_market_interpretation(
            self._macro_score_frame(
                {
                    "Risk-On Score": -27,
                    "Growth Score": -31,
                    "Rate Pressure Score": -14,
                    "Dollar Pressure Score": 3,
                    "Safe Haven Score": 10,
                    "Inflation Pressure Score": -23,
                }
            ),
            self._macro_symbol_frame(
                {
                    "ES=F": -1.06,
                    "NQ=F": -1.19,
                    "RTY=F": -0.75,
                    "HG=F": -1.25,
                    "CL=F": -0.68,
                    "GC=F": 0.25,
                    "ZN=F": 0.15,
                    "ZB=F": 0.05,
                    "6J=F": 0.10,
                }
            ),
        )

        self.assertEqual(interpretation["scenario"], "혼재된 매크로 흐름")
        self.assertEqual(interpretation["sub_scenario"], "성장 약세 + 방어 확인 부족")
        self.assertEqual(interpretation["regime_hint"], "Risk-off 후보")
        self.assertIn("하위 맥락", interpretation["summary"])
        self.assertNotEqual(interpretation["summary"], interpretation["mixed_reason"])
        self.assertIn("안전자산", interpretation["mixed_reason"])
        self.assertIn("성장 약세", " ".join(interpretation["evidence"]))

    def test_macro_interpretation_explains_risk_weakness_with_easing_rates(self) -> None:
        from app.services.futures_macro_thermometer import generate_market_interpretation

        interpretation = generate_market_interpretation(
            self._macro_score_frame(
                {
                    "Risk-On Score": -24,
                    "Growth Score": -8,
                    "Rate Pressure Score": -28,
                    "Dollar Pressure Score": 2,
                    "Safe Haven Score": -4,
                    "Inflation Pressure Score": -6,
                }
            ),
            self._macro_symbol_frame(
                {
                    "ES=F": -0.91,
                    "NQ=F": -1.04,
                    "RTY=F": -0.66,
                    "ZN=F": 1.10,
                    "ZB=F": 0.95,
                    "GC=F": -0.10,
                    "HG=F": -0.30,
                }
            ),
        )

        self.assertEqual(interpretation["scenario"], "혼재된 매크로 흐름")
        self.assertEqual(interpretation["sub_scenario"], "위험선호 약세 + 금리 부담 완화")
        self.assertEqual(interpretation["regime_hint"], "성장주 부담 완화 확인 필요")
        self.assertIn("금리 부담", interpretation["mixed_reason"])

    def test_macro_interpretation_keeps_low_signal_mixed_context_distinct(self) -> None:
        from app.services.futures_macro_thermometer import generate_market_interpretation

        interpretation = generate_market_interpretation(
            self._macro_score_frame(
                {
                    "Risk-On Score": 5,
                    "Growth Score": 4,
                    "Rate Pressure Score": -3,
                    "Dollar Pressure Score": 2,
                    "Safe Haven Score": 3,
                    "Inflation Pressure Score": -2,
                }
            ),
            self._macro_symbol_frame(
                {
                    "ES=F": 0.12,
                    "NQ=F": 0.18,
                    "RTY=F": -0.08,
                    "ZN=F": 0.10,
                    "ZB=F": -0.07,
                    "GC=F": 0.05,
                    "HG=F": 0.11,
                }
            ),
        )

        self.assertEqual(interpretation["scenario"], "혼재된 매크로 흐름")
        self.assertEqual(interpretation["sub_scenario"], "저신호 / 방향성 없음")
        self.assertEqual(interpretation["regime_hint"], "관망")
        self.assertIn("20점", interpretation["mixed_reason"])

    def test_macro_thermometer_builds_weekly_context_from_5d_moves(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        symbols = [
            "ES=F",
            "NQ=F",
            "RTY=F",
            "ZN=F",
            "ZB=F",
            "CL=F",
            "HG=F",
            "NG=F",
            "GC=F",
            "6E=F",
            "6J=F",
            "6B=F",
            "6A=F",
            "6C=F",
        ]
        five_day_moves = {symbol: 0.001 for symbol in symbols}
        five_day_moves.update(
            {
                "ES=F": 0.023,
                "NQ=F": 0.031,
                "RTY=F": 0.018,
                "ZN=F": -0.015,
                "ZB=F": -0.018,
                "CL=F": 0.028,
                "HG=F": 0.02,
                "6E=F": -0.012,
                "6A=F": -0.011,
            }
        )
        candle_rows = self._daily_rows_with_recent_5d_moves(five_day_moves)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=symbols, query_fn=query_fn)
        weekly = snapshot["weekly_context"]

        self.assertEqual(weekly["status"], "OK")
        self.assertIn("최근 1주", weekly["summary"])
        card_by_label = {card["label"]: card for card in weekly["cards"]}
        self.assertIn("위험선호", card_by_label)
        self.assertIn("금리 부담", card_by_label)
        self.assertGreater(card_by_label["금리 부담"]["raw_value"], 0)
        self.assertIn("채권선물", card_by_label["금리 부담"]["meaning"])

    def test_macro_thermometer_returns_current_state_evidence_reading(self) -> None:
        from app.services.futures_macro_thermometer import build_macro_evidence_reading

        sections = build_macro_evidence_reading(
            {
                "strong": ["Rate Pressure Score / ZN=F +1.85z"],
                "weak": ["Risk-On Score / ES=F +0.42z"],
                "conflicting": [],
                "missing": [],
                "counts": {"strong": 1, "weak": 1, "conflicting": 0, "missing": 0},
            }
        )

        self.assertEqual([section["key"] for section in sections], ["strong", "weak", "conflicting", "missing"])
        self.assertEqual([section["label"] for section in sections], ["강한 근거", "약한 근거", "충돌 근거", "자료 부족"])
        self.assertEqual([section["count"] for section in sections], [1, 1, 0, 0])
        empty_labels = {section["key"]: section["empty_label"] for section in sections}
        self.assertEqual(empty_labels["weak"], "약한 근거 없음")
        self.assertEqual(empty_labels["conflicting"], "충돌 신호 없음")
        self.assertEqual(empty_labels["missing"], "자료 부족 없음")

        strong_item = sections[0]["items"][0]
        self.assertEqual(strong_item["score_label"], "금리 부담")
        self.assertEqual(strong_item["symbol"], "ZN=F")
        self.assertEqual(strong_item["contribution_z"], "+1.85z")
        self.assertEqual(strong_item["impact_label"], "영향 강함")
        self.assertIn("강화합니다", strong_item["meaning"])
        flattened = " ".join(
            str(value)
            for section in sections
            for value in [section.get("label"), section.get("description"), section.get("empty_label")]
        )
        self.assertNotIn("어떻게 읽을까", flattened)

    def test_macro_thermometer_snapshot_exposes_current_evidence_counts(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        symbols = ["ES=F", "NQ=F", "RTY=F", "ZN=F", "ZB=F", "GC=F", "HG=F", "CL=F", "6A=F"]
        final_moves = {symbol: 0.001 for symbol in symbols}
        final_moves.update({"NQ=F": -0.025, "ZN=F": -0.015, "ZB=F": -0.017, "GC=F": -0.018})
        candle_rows = self._daily_rows(final_moves)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=symbols, query_fn=query_fn)
        sections = {section["key"]: section for section in snapshot["evidence_reading"]}

        self.assertIn("strong", sections)
        self.assertIn("missing", sections)
        self.assertIn("count", sections["strong"])
        strong_items = sections["strong"]["items"]
        self.assertTrue(strong_items)
        self.assertTrue(all({"meaning", "score_label", "symbol", "contribution_z", "impact_label"}.issubset(item) for item in strong_items))
        self.assertTrue(any("금리" in item["meaning"] or "위험선호" in item["meaning"] for item in strong_items))

    def test_macro_thermometer_warns_when_daily_history_is_short(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        candle_rows = self._daily_rows({"ES=F": 0.02, "NQ=F": 0.02}, days=20)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=["ES=F", "NQ=F"], query_fn=query_fn)

        self.assertEqual(snapshot["status"], "REVIEW")
        self.assertIn("less than 6 months", " ".join(snapshot["warnings"]))
        self.assertEqual(snapshot["coverage"]["standardized_count"], 0)

    def test_macro_validation_recomputes_point_in_time_scenario_hits(self) -> None:
        from app.services.futures_macro_validation import build_futures_macro_validation_snapshot

        symbols, candle_rows = self._risk_on_validation_rows()

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            if "FROM nyse_price_history" in sql:
                return []
            return []

        validation = build_futures_macro_validation_snapshot(
            symbols=symbols,
            query_fn=query_fn,
            current_snapshot={"summary": {"scenario": "좋은 risk-on"}},
            min_standardized_symbols=8,
        )
        summary = validation["scenario_summary"]

        self.assertIn(validation["status"], {"OK", "REVIEW"})
        self.assertFalse(validation["records"].empty)
        self.assertIn("좋은 risk-on", set(summary["Scenario"]))
        risk_on_row = summary[summary["Scenario"] == "좋은 risk-on"].iloc[0]
        self.assertGreaterEqual(risk_on_row["Sample 5D"], 1)
        self.assertIsNotNone(risk_on_row["Hit Rate 5D %"])
        self.assertGreaterEqual(risk_on_row["Hit Rate 5D %"], 50)

    def test_macro_validation_summary_focuses_current_scenario_before_raw_tables(self) -> None:
        from app.services.futures_macro_validation import build_current_scenario_validation_summary

        validation = {
            "coverage": {"validation_dates": 1212, "history_span_years": 5.05},
            "current_scenario_metrics": {
                "Scenario": "혼재된 매크로 흐름",
                "Occurrence Count": 950,
                "Sample 5D": 0,
                "Hit Rate 5D %": None,
                "False Positive 5D %": None,
                "Max Adverse 5D %": None,
                "Directional Hit Applicable": False,
            },
        }

        summary = build_current_scenario_validation_summary(validation, confidence_label="Medium Confidence")

        self.assertEqual(summary["title"], "과거 점검 요약")
        self.assertEqual(summary["scenario"], "혼재된 매크로 흐름")
        self.assertEqual(summary["occurrence"]["label"], "과거 발생")
        self.assertEqual(summary["occurrence"]["value"], "950회")
        self.assertEqual(summary["coverage"], "1212개 PIT 날짜 · 5.05년")
        self.assertFalse(summary["hit_rate_applicable"])
        self.assertIn("방향성 적중률", summary["interpretation"])
        self.assertIn("현재 confidence를 보조", summary["confidence_effect"])
        self.assertIn("매수/매도 신호", summary["confidence_effect"])
        self.assertIn("아닙니다", summary["confidence_effect"])

    def test_interpretation_confidence_uses_current_coverage_and_validation_sample(self) -> None:
        from app.services.futures_macro_validation import build_interpretation_confidence

        current_snapshot = {
            "coverage": {
                "symbol_count": 16,
                "standardized_count": 16,
                "min_data_days": 260,
                "latest_daily_date": date.today().isoformat(),
            },
            "evidence_groups": {
                "counts": {
                    "strong": 4,
                    "weak": 1,
                    "missing": 0,
                    "conflicting": 0,
                }
            },
        }
        validation_snapshot = {
            "coverage": {
                "validation_dates": 100,
                "history_span_years": 4.0,
            },
            "current_scenario_metrics": {
                "Scenario": "좋은 risk-on",
                "Sample 5D": 80,
                "Hit Rate 5D %": 61.0,
                "Directional Hit Applicable": True,
            },
        }

        confidence = build_interpretation_confidence(current_snapshot, validation_snapshot)

        self.assertIn(confidence["label"], {"High Confidence", "Medium Confidence"})
        self.assertEqual(confidence["sample_size"], 80)
        self.assertEqual(confidence["hit_rate_5d"], 61.0)

        low_snapshot = {
            "coverage": {
                "symbol_count": 16,
                "standardized_count": 0,
                "min_data_days": 20,
                "latest_daily_date": date.today().isoformat(),
            },
            "evidence_groups": {"counts": {}},
        }
        low_confidence = build_interpretation_confidence(low_snapshot, validation_snapshot)

        self.assertEqual(low_confidence["label"], "Not Enough History")

    def test_mixed_scenario_confidence_does_not_report_directional_hit_sample(self) -> None:
        from app.services.futures_macro_validation import build_interpretation_confidence

        current_snapshot = {
            "coverage": {
                "symbol_count": 16,
                "standardized_count": 16,
                "min_data_days": 260,
                "latest_daily_date": date.today().isoformat(),
            },
            "evidence_groups": {
                "counts": {
                    "strong": 3,
                    "weak": 2,
                    "missing": 0,
                    "conflicting": 0,
                }
            },
        }
        validation_snapshot = {
            "coverage": {
                "validation_dates": 100,
                "history_span_years": 4.0,
            },
            "current_scenario_metrics": {
                "Scenario": "혼재된 매크로 흐름",
                "Occurrence Count": 90,
                "Sample 5D": 0,
                "Hit Rate 5D %": None,
                "Directional Hit Applicable": False,
            },
        }

        confidence = build_interpretation_confidence(current_snapshot, validation_snapshot)

        self.assertEqual(confidence["sample_size"], 0)
        self.assertEqual(confidence["occurrence_count"], 90)
        self.assertFalse(confidence["hit_applicable"])
        self.assertIsNone(confidence["hit_rate_5d"])

    def test_basket_forward_return_reports_path_max_adverse_move(self) -> None:
        from app.services.futures_macro_validation import _basket_forward_return

        dates = pd.date_range("2026-01-01", periods=6, freq="D")
        futures_matrix = pd.DataFrame(
            {
                "ES=F": [100.0, 95.0, 98.0, 101.0, 103.0, 104.0],
                "NQ=F": [100.0, 94.0, 99.0, 102.0, 103.0, 105.0],
            },
            index=dates,
        )

        basket = _basket_forward_return(
            futures_matrix=futures_matrix,
            proxy_matrix=pd.DataFrame(),
            futures_symbols=("ES=F", "NQ=F"),
            as_of=dates[0],
            horizon=5,
        )

        self.assertGreater(basket.value, 0)
        self.assertLess(basket.max_adverse, 0)
        self.assertAlmostEqual(basket.max_adverse, -5.5, places=1)

    def test_overview_macro_snapshot_cache_can_be_cleared(self) -> None:
        import app.services.futures_macro_thermometer as macro_service

        calls: list[dict[str, Any]] = []
        original_builder = macro_service.build_futures_macro_thermometer_snapshot

        def fake_builder(**kwargs: Any) -> dict[str, Any]:
            calls.append(dict(kwargs))
            return {"call_count": len(calls)}

        try:
            macro_service.clear_overview_futures_macro_snapshot_cache()
            macro_service.build_futures_macro_thermometer_snapshot = fake_builder

            first = macro_service.load_overview_futures_macro_snapshot(cache_ttl_seconds=60)
            second = macro_service.load_overview_futures_macro_snapshot(cache_ttl_seconds=60)
            macro_service.clear_overview_futures_macro_snapshot_cache()
            third = macro_service.load_overview_futures_macro_snapshot(cache_ttl_seconds=60)

            self.assertIs(first, second)
            self.assertEqual(first["call_count"], 1)
            self.assertEqual(third["call_count"], 2)
            self.assertEqual(len(calls), 2)
        finally:
            macro_service.build_futures_macro_thermometer_snapshot = original_builder
            macro_service.clear_overview_futures_macro_snapshot_cache()

    def test_overview_macro_snapshot_cache_key_tracks_latest_daily_marker(self) -> None:
        import app.services.futures_macro_thermometer as macro_service

        calls: list[dict[str, Any]] = []
        marker = {"value": "2026-06-23 00:00:00"}
        original_builder = macro_service.build_futures_macro_thermometer_snapshot
        original_marker = macro_service._latest_daily_cache_marker

        def fake_builder(**kwargs: Any) -> dict[str, Any]:
            calls.append(dict(kwargs))
            return {"call_count": len(calls), "marker": marker["value"]}

        try:
            macro_service.clear_overview_futures_macro_snapshot_cache()
            macro_service.build_futures_macro_thermometer_snapshot = fake_builder
            macro_service._latest_daily_cache_marker = lambda query_fn, symbols: marker["value"]

            first = macro_service.load_overview_futures_macro_snapshot(cache_ttl_seconds=60)
            second = macro_service.load_overview_futures_macro_snapshot(cache_ttl_seconds=60)
            marker["value"] = "2026-06-24 00:00:00"
            third = macro_service.load_overview_futures_macro_snapshot(cache_ttl_seconds=60)

            self.assertIs(first, second)
            self.assertEqual(first["call_count"], 1)
            self.assertEqual(third["call_count"], 2)
            self.assertEqual(third["marker"], "2026-06-24 00:00:00")
            self.assertEqual(len(calls), 2)
        finally:
            macro_service.build_futures_macro_thermometer_snapshot = original_builder
            macro_service._latest_daily_cache_marker = original_marker
            macro_service.clear_overview_futures_macro_snapshot_cache()


class MarketIntelligenceIngestionContractTests(unittest.TestCase):
    def test_cnn_fear_greed_parser_builds_overall_history_and_component_rows(self) -> None:
        from finance.data import sentiment

        ts_current = int(pd.Timestamp("2026-06-04 23:10:00", tz=timezone.utc).timestamp() * 1000)
        ts_previous = int(pd.Timestamp("2026-06-03 00:00:00", tz=timezone.utc).timestamp() * 1000)
        payload = {
            "fear_and_greed": {
                "score": 54.7,
                "rating": "neutral",
                "timestamp": "2026-06-04T23:10:00+00:00",
                "previous_close": 54.0,
                "previous_1_week": 60.1,
            },
            "fear_and_greed_historical": {
                "data": [
                    {"x": ts_previous, "y": 54.0, "rating": "neutral"},
                    {"x": ts_current, "y": 54.7, "rating": "neutral"},
                ]
            },
            "stock_price_breadth": {
                "score": 31.4,
                "rating": "fear",
                "timestamp": ts_current,
            },
        }

        rows = sentiment.parse_cnn_fear_greed_graphdata(payload, collected_at="2026-06-04 23:11:00")
        by_key = {(row["series_id"], row["observation_date"]): row for row in rows}

        self.assertIn(("CNN_FEAR_GREED", "2026-06-04"), by_key)
        self.assertEqual(by_key[("CNN_FEAR_GREED", "2026-06-04")]["value"], 54.7)
        self.assertEqual(json.loads(by_key[("CNN_FEAR_GREED", "2026-06-04")]["missing_fields_json"])["rating"], "neutral")
        component = by_key[("CNN_FNG_STOCK_PRICE_BREADTH", "2026-06-04")]
        self.assertEqual(component["category"], "sentiment_component")
        self.assertEqual(component["value"], 31.4)
        self.assertEqual(json.loads(component["missing_fields_json"])["rating"], "fear")

    def test_aaii_sentiment_parser_builds_bearish_and_spread_rows(self) -> None:
        from finance.data import sentiment

        html = """
        <table>
          <tr><th>Reported Date</th><th>Bullish</th><th>Neutral</th><th>Bearish</th></tr>
          <tr><td>Jun 3</td><td>36.3%</td><td>26.7%</td><td>37.0%</td></tr>
          <tr><td>May 27</td><td>35.6%</td><td>22.6%</td><td>41.9%</td></tr>
        </table>
        """

        rows = sentiment.parse_aaii_sentiment_rows_from_html(
            html,
            collected_at="2026-06-04 14:50:00",
            today=date(2026, 6, 5),
        )
        by_key = {(row["series_id"], row["observation_date"]): row for row in rows}

        self.assertEqual(by_key[("AAII_BEARISH", "2026-06-03")]["value"], 37.0)
        self.assertEqual(by_key[("AAII_BULLISH", "2026-06-03")]["value"], 36.3)
        self.assertEqual(by_key[("AAII_NEUTRAL", "2026-06-03")]["value"], 26.7)
        self.assertAlmostEqual(by_key[("AAII_BULL_BEAR_SPREAD", "2026-06-03")]["value"], -0.7)
        self.assertEqual(by_key[("AAII_BEARISH", "2026-06-03")]["source"], "aaii_sentiment_survey")

    def test_aaii_fetcher_uses_browser_document_headers(self) -> None:
        from finance.data import sentiment

        captured_headers: dict[str, str] = {}

        def fake_fetcher(request, timeout: int) -> bytes:
            del timeout
            captured_headers.update({key.lower(): value for key, value in request.header_items()})
            return b"""
            <table>
              <tr><th>Reported Date</th><th>Bullish</th><th>Neutral</th><th>Bearish</th></tr>
              <tr><td>Jun 3</td><td>36.3%</td><td>26.7%</td><td>37.0%</td></tr>
            </table>
            """

        rows = sentiment.fetch_aaii_sentiment_rows(
            retries=1,
            today=date(2026, 6, 5),
            fetcher=fake_fetcher,
        )

        by_series = {row["series_id"]: row for row in rows}
        self.assertEqual(by_series["AAII_BEARISH"]["value"], 37.0)
        self.assertIn("chrome/", captured_headers["user-agent"].lower())
        self.assertEqual(captured_headers["referer"], "https://www.aaii.com/sentimentsurvey")
        self.assertEqual(captured_headers["sec-fetch-mode"], "navigate")

    def test_ingestion_job_wraps_market_sentiment_collection_summary(self) -> None:
        from app.jobs import ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_market_sentiment",
            return_value={
                "requested": 2,
                "stored": 260,
                "coverage": {"actual": 260},
                "sources": ["cnn_fear_greed", "aaii_sentiment_survey"],
                "missing": [],
                "failed": [],
            },
        ):
            result = jobs.run_collect_market_sentiment()

        self.assertEqual(result["job_name"], "collect_market_sentiment")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 260)
        self.assertEqual(result["symbols_processed"], 2)
        self.assertEqual(result["details"]["target_tables"], ["finance_meta.macro_series_observation"])

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

    def test_quote_gap_diagnostics_explain_batch_only_gap(self) -> None:
        from finance.data import market_intelligence as mi

        class EmptyTicker:
            fast_info = {}

            def __init__(self, symbol: str) -> None:
                self.symbol = symbol

        def quote_fetcher(symbols):
            self.assertEqual(symbols, ["AAA"])
            return [
                {
                    "symbol": "AAA",
                    "regularMarketPrice": 112.0,
                    "regularMarketPreviousClose": 100.0,
                }
            ]

        result = mi.diagnose_market_quote_gaps(
            ["AAA"],
            quote_fetcher=quote_fetcher,
            ticker_factory=EmptyTicker,
            history_downloader=lambda *args, **kwargs: pd.DataFrame(),
            db_previous_close_map={},
            profile_map={"AAA": {"status": "active"}},
        )

        self.assertEqual(result["diagnosis_counts"], {"batch_only_gap": 1})
        row = result["diagnostics"][0]
        self.assertEqual(row["Diagnosis"], "batch_only_gap")
        self.assertEqual(row["Quote Single Status"], "ok")
        self.assertIn("Single-symbol", row["Evidence Summary"])

    def test_quote_gap_diagnostics_explain_provider_quote_gap(self) -> None:
        from finance.data import market_intelligence as mi

        class EmptyTicker:
            fast_info = {}

            def __init__(self, symbol: str) -> None:
                self.symbol = symbol

        def history_downloader(symbols, **kwargs):
            self.assertEqual(symbols, ["BBB"])
            del kwargs
            return pd.DataFrame(
                {"Close": [100.0, 105.0], "Volume": [1000, 1200]},
                index=pd.to_datetime(["2026-05-27", "2026-05-28"]),
            )

        result = mi.diagnose_market_quote_gaps(
            ["BBB"],
            quote_fetcher=lambda symbols: [],
            ticker_factory=EmptyTicker,
            history_downloader=history_downloader,
            db_previous_close_map={"BBB": {"previous_close": 105.0, "previous_close_date": "2026-05-28"}},
            profile_map={"BBB": {"status": "active"}},
        )

        self.assertEqual(result["diagnosis_counts"], {"provider_quote_gap": 1})
        row = result["diagnostics"][0]
        self.assertEqual(row["Diagnosis"], "provider_quote_gap")
        self.assertEqual(row["History Status"], "ok")
        self.assertEqual(row["DB Price Status"], "ok")

    def test_quote_gap_diagnostics_build_persistent_issue_rows(self) -> None:
        from finance.data import market_intelligence as mi

        rows = mi.build_quote_gap_issue_rows(
            [
                {
                    "Symbol": "bbb",
                    "Diagnosis": "provider_quote_gap",
                    "Confidence": 0.82,
                    "Evidence Summary": "Alternate price evidence exists.",
                    "Recommended Action": "Rerun later.",
                }
            ],
            universe_code="top1000",
            interval_code="5m",
            snapshot_time_utc="2026-05-29 13:30:00",
            seen_at="2026-05-29 13:31:00",
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["issue_type"], "quote_gap")
        self.assertEqual(row["universe_code"], "TOP1000")
        self.assertEqual(row["symbol"], "BBB")
        self.assertEqual(row["diagnosis"], "provider_quote_gap")
        self.assertEqual(row["last_snapshot_time_utc"], "2026-05-29 13:30:00")
        self.assertIn("provider_quote_gap", row["raw_payload_json"])

    def test_quote_gap_job_persists_issue_history(self) -> None:
        from app.jobs import ingestion_jobs

        diagnosis = {
            "universe_code": "TOP1000",
            "interval_code": "5m",
            "snapshot_time_utc": "2026-05-29 13:30:00",
            "symbols_requested": 1,
            "symbols_processed": 1,
            "diagnosis_counts": {"provider_quote_gap": 1},
            "diagnostics": [{"Symbol": "BBB", "Diagnosis": "provider_quote_gap"}],
        }
        issue_history = [
            {
                "universe_code": "TOP1000",
                "symbol": "BBB",
                "diagnosis": "provider_quote_gap",
                "occurrence_count": 3,
            }
        ]

        with (
            patch.object(ingestion_jobs, "diagnose_market_quote_gaps", return_value=diagnosis),
            patch.object(
                ingestion_jobs,
                "persist_quote_gap_diagnostics",
                return_value={"rows_written": 1, "issues": issue_history},
            ) as persist,
        ):
            result = ingestion_jobs.run_diagnose_market_quote_gaps(
                symbols=["BBB"],
                universe_code="TOP1000",
                snapshot_time_utc="2026-05-29 13:30:00",
            )

        persist.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["details"]["issue_rows_written"], 1)
        self.assertEqual(result["details"]["issue_history"][0]["occurrence_count"], 3)
        self.assertIn("Persisted 1 issue row", result["message"])


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
            "source_type",
            "validation_status",
            "event_status",
            "superseded_by_event_key",
            "superseded_at",
            "source_url",
            "confidence",
            "collected_at",
            "raw_payload_json",
        ]:
            self.assertIn(column, schema_sql)
        self.assertIn("UNIQUE KEY uk_market_event_key", schema_sql)

    def test_market_data_issue_schema_tracks_repeated_quote_gaps(self) -> None:
        from finance.data.db.schema import MARKET_INTELLIGENCE_SCHEMAS

        schema_sql = MARKET_INTELLIGENCE_SCHEMAS["market_data_issue"]

        for column in [
            "issue_key",
            "issue_type",
            "universe_code",
            "symbol",
            "diagnosis",
            "occurrence_count",
            "first_seen_at",
            "last_seen_at",
            "latest_confidence",
            "latest_recommended_action",
            "raw_payload_json",
        ]:
            self.assertIn(column, schema_sql)
        self.assertIn("UNIQUE KEY uk_market_data_issue_key", schema_sql)

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

    def test_bls_macro_calendar_parser_builds_official_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        html = """
        <table>
          <thead><tr><th>Date Time</th><th>Release</th></tr></thead>
          <tbody>
            <tr><td>Wednesday, June 10, 2026 08:30 AM</td><td>Consumer Price Index for May 2026</td></tr>
            <tr><td>Thursday, June 11, 2026 08:30 AM</td><td>Producer Price Index for May 2026</td></tr>
            <tr><td>Friday, June 5, 2026 08:30 AM</td><td>Employment Situation for May 2026</td></tr>
            <tr><td>Friday, June 5, 2026 10:00 AM</td><td>Other Release for May 2026</td></tr>
          </tbody>
        </table>
        """

        rows = mi.parse_bls_macro_calendar_events_from_html(
            html,
            source_url="https://www.bls.gov/schedule/2026/",
            year=2026,
        )

        self.assertEqual([row["event_type"] for row in rows], ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT"])
        self.assertEqual(rows[0]["event_date"], "2026-06-10")
        self.assertEqual(rows[0]["source_type"], "official")
        self.assertEqual(rows[0]["validation_status"], "official")
        self.assertEqual(rows[0]["raw_payload"]["reference_period"], "May 2026")
        self.assertEqual(rows[0]["raw_payload"]["release_time_et"], "08:30")

    def test_bls_macro_calendar_ics_parser_builds_official_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        ics_text = """
BEGIN:VCALENDAR
BEGIN:VEVENT
UID:cpi-20260610@bls.gov
DTSTART:20260610T123000Z
SUMMARY:Consumer Price Index for May 2026
END:VEVENT
BEGIN:VEVENT
UID:ppi-20260611@bls.gov
DTSTART;TZID=America/New_York:20260611T083000
SUMMARY:Producer Price Index for May 2026
END:VEVENT
BEGIN:VEVENT
UID:jobs-20260605@bls.gov
DTSTART;VALUE=DATE:20260605
SUMMARY:Employment Situation for May
  2026
END:VEVENT
BEGIN:VEVENT
UID:other-20260605@bls.gov
DTSTART:20260605T140000Z
SUMMARY:Other Release for May 2026
END:VEVENT
END:VCALENDAR
        """

        rows = mi.parse_bls_macro_calendar_events_from_ics(
            ics_text,
            years=[2026],
            source_name="bls.ics",
        )

        self.assertEqual([row["event_type"] for row in rows], ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT"])
        self.assertEqual([row["event_date"] for row in rows], ["2026-06-10", "2026-06-11", "2026-06-05"])
        self.assertEqual(rows[0]["raw_payload"]["release_time_et"], "08:30")
        self.assertEqual(rows[0]["raw_payload"]["import_method"], "official_ics_file")
        self.assertEqual(rows[0]["raw_payload"]["source_file_name"], "bls.ics")
        self.assertEqual(rows[2]["raw_payload"]["reference_period"], "May 2026")

    def test_bls_macro_calendar_parsers_accept_abbreviated_cpi_ppi_titles(self) -> None:
        from finance.data import market_intelligence as mi

        html = """
        <table>
          <thead><tr><th>Date Time</th><th>Release</th></tr></thead>
          <tbody>
            <tr><td>Wednesday, June 10, 2026 08:30 AM</td><td>CPI for May 2026</td></tr>
            <tr><td>Thursday, June 11, 2026 08:30 AM</td><td>PPI for May 2026</td></tr>
            <tr><td>Friday, June 5, 2026 08:30 AM</td><td>The Employment Situation for May 2026</td></tr>
          </tbody>
        </table>
        """
        html_rows = mi.parse_bls_macro_calendar_events_from_html(
            html,
            source_url="https://www.bls.gov/schedule/2026/",
            year=2026,
        )

        ics_text = """
BEGIN:VCALENDAR
BEGIN:VEVENT
UID:cpi-short-20260610@bls.gov
DTSTART:20260610T123000Z
SUMMARY:CPI for May 2026
END:VEVENT
BEGIN:VEVENT
UID:ppi-short-20260611@bls.gov
DTSTART:20260611T123000Z
SUMMARY:PPI for May 2026
END:VEVENT
BEGIN:VEVENT
UID:jobs-20260605@bls.gov
DTSTART:20260605T123000Z
SUMMARY:The Employment Situation for May 2026
END:VEVENT
END:VCALENDAR
        """
        ics_rows = mi.parse_bls_macro_calendar_events_from_ics(
            ics_text,
            years=[2026],
            source_name="bls.ics",
        )

        self.assertEqual([row["event_type"] for row in html_rows], ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT"])
        self.assertEqual([row["event_type"] for row in ics_rows], ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT"])
        self.assertEqual(html_rows[0]["raw_payload"]["reference_period"], "May 2026")
        self.assertEqual(ics_rows[1]["raw_payload"]["reference_period"], "May 2026")

    def test_collect_bls_macro_calendar_ics_writes_events(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        ics_text = """
BEGIN:VCALENDAR
BEGIN:VEVENT
UID:cpi-20260610@bls.gov
DTSTART:20260610T123000Z
SUMMARY:Consumer Price Index for May 2026
END:VEVENT
END:VCALENDAR
        """

        with patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows):
            result = mi.collect_and_store_bls_macro_calendar_ics(
                ics_text,
                years=[2026],
                source_name="bls.ics",
            )

        self.assertEqual(result["source"], mi.BLS_MACRO_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "MACRO")
        self.assertEqual(result["method"], "official_ics_file")
        self.assertEqual(result["event_types"], ["MACRO_CPI"])
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_bea_gdp_calendar_parser_excludes_state_and_county_gdp(self) -> None:
        from finance.data import market_intelligence as mi

        html = """
        <table>
          <thead><tr><th>Year 2026</th><th>Type</th><th>Release</th><th></th></tr></thead>
          <tbody>
            <tr><td>June 25 8:30 AM</td><td>News</td><td>Gross Domestic Product, 1st Quarter 2026 (Third Estimate)</td><td></td></tr>
            <tr><td>June 30 8:30 AM</td><td>News</td><td>Gross Domestic Product by State, 1st Quarter 2026</td><td>View</td></tr>
            <tr><td>July 30 8:30 AM</td><td>News</td><td>GDP (Advance Estimate), 2nd Quarter 2026</td><td>View</td></tr>
          </tbody>
        </table>
        """

        rows = mi.parse_bea_gdp_calendar_events_from_html(
            html,
            source_url="https://www.bea.gov/index.php/news/schedule/full",
            years=[2026],
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual([row["event_date"] for row in rows], ["2026-06-25", "2026-07-30"])
        self.assertTrue(all(row["event_type"] == "MACRO_GDP" for row in rows))
        self.assertEqual(rows[0]["raw_payload"]["release_time_et"], "08:30")
        self.assertIsNone(rows[0]["raw_payload"]["source_row"]["Unnamed: 3"])

    def test_collect_macro_calendar_writes_events_and_reports_failed_sources(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        def fake_fetcher(**kwargs):
            self.assertEqual(kwargs["years"], [2026])
            return {
                "source": mi.MACRO_CALENDAR_SOURCE,
                "source_url": "https://example.test/macro",
                "event_type": "MACRO",
                "method": "official_html",
                "events": [
                    {
                        "event_date": "2026-06-10",
                        "event_type": "MACRO_CPI",
                        "title": "CPI: Consumer Price Index for May 2026",
                        "source": mi.BLS_MACRO_CALENDAR_SOURCE,
                        "source_type": "official",
                        "validation_status": "official",
                        "source_url": "https://www.bls.gov/schedule/2026/",
                        "confidence": 0.95,
                    }
                ],
                "events_found": 1,
                "failed_sources": ["BEA: temporary failure"],
            }

        with patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows):
            result = mi.collect_and_store_macro_calendar(years=[2026], macro_fetcher=fake_fetcher)

        self.assertEqual(result["source"], mi.MACRO_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "MACRO")
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(result["event_types"], ["MACRO_CPI"])
        self.assertEqual(result["failed_sources"], ["BEA: temporary failure"])
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
        self.assertEqual(row["source_type"], "provider_estimate")
        self.assertEqual(row["validation_status"], "estimate_only")
        self.assertEqual(row["raw_payload"]["provider_calendar"]["Earnings Average"], 1.23)
        self.assertEqual(result["symbols_with_events"], 1)
        self.assertEqual(result["missing_reason_counts"], {"no_provider_earnings_date": 1})
        self.assertEqual(result["symbol_diagnostics"][0]["status"], "event_found")
        self.assertEqual(result["symbol_diagnostics"][1]["reason"], "no_provider_earnings_date")
        self.assertEqual(row["raw_payload"]["collection_quality"]["in_window_date_count"], 1)

    def test_yfinance_earnings_calendar_diagnostics_explain_outside_window_and_errors(self) -> None:
        from finance.data import market_intelligence as mi

        calendars = {
            "AAA": {"Earnings Date": [date(2026, 12, 30)]},
            "BBB": RuntimeError("provider unavailable"),
        }

        class FakeTicker:
            def __init__(self, symbol: str) -> None:
                value = calendars[symbol]
                if isinstance(value, Exception):
                    raise value
                self.calendar = value

        result = mi.fetch_yfinance_earnings_calendar_events(
            ["AAA", "BBB"],
            start_date="2026-05-28",
            lookahead_days=30,
            ticker_factory=FakeTicker,
        )

        self.assertEqual(result["events_found"], 0)
        self.assertEqual(result["missing_symbols"], ["AAA"])
        self.assertEqual(result["failed_symbols"], ["BBB"])
        self.assertEqual(result["missing_reason_counts"], {"outside_window": 1})
        self.assertEqual(result["failed_reason_counts"], {"provider_error": 1})
        self.assertEqual(result["symbol_diagnostics"][0]["provider_dates"], ["2026-12-30"])
        self.assertEqual(result["symbol_diagnostics"][1]["detail"], "provider unavailable")

    def test_yfinance_earnings_calendar_can_cross_check_nasdaq_source(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeTicker:
            def __init__(self, symbol: str) -> None:
                self.calendar = {"Earnings Date": [date(2026, 7, 30)]}

        def fake_nasdaq_fetcher(dates, **kwargs):
            del kwargs
            self.assertEqual(dates, ["2026-07-30"])
            return {
                "2026-07-30": {
                    "symbols": ["AAA", "MSFT"],
                    "source": mi.NASDAQ_EARNINGS_CALENDAR_SOURCE,
                    "source_url": "https://api.nasdaq.test/calendar?date=2026-07-30",
                    "status": "ok",
                }
            }

        result = mi.fetch_yfinance_earnings_calendar_events(
            ["AAA"],
            start_date="2026-05-28",
            lookahead_days=120,
            validate_with_nasdaq=True,
            nasdaq_fetcher=fake_nasdaq_fetcher,
            ticker_factory=FakeTicker,
        )

        row = result["events"][0]
        self.assertEqual(result["validation_source"], mi.NASDAQ_EARNINGS_CALENDAR_SOURCE)
        self.assertEqual(row["validation_status"], "cross_checked")
        self.assertEqual(row["confidence"], 0.75)
        self.assertTrue(row["raw_payload"]["source_validation"]["fallback_order"][1]["matched"])

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
                        "source_type": "provider_estimate",
                        "validation_status": "estimate_only",
                        "source_url": "https://finance.yahoo.com/quote/AAA/analysis",
                        "confidence": 0.65,
                        "raw_payload": {"provider": mi.EARNINGS_CALENDAR_SOURCE},
                    }
                ],
                "events_found": 1,
                "missing_symbols": ["BBB"],
                "failed_symbols": [],
            }

        with (
            patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows),
            patch.object(mi, "mark_superseded_earnings_events", return_value=0),
            patch.object(mi, "mark_stale_earnings_estimates", return_value=0),
        ):
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
        self.assertEqual(result["superseded_rows_marked"], 0)
        self.assertEqual(result["stale_rows_marked"], 0)
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_resolve_earnings_collection_symbols_supports_universe_batches(self) -> None:
        from finance.data import market_intelligence as mi

        symbols, source = mi.resolve_earnings_collection_symbols(
            symbol_source="top1000",
            max_symbols=2,
            batch_offset=1,
            source_symbols_loader=lambda: ["AAA", "BBB", "CCC", "DDD"],
        )

        self.assertEqual(source, "top1000")
        self.assertEqual(symbols, ["BBB", "CCC"])

    def test_mark_superseded_earnings_events_marks_prior_active_rows(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeDb:
            def __init__(self) -> None:
                self.used_dbs: list[str] = []
                self.queries: list[tuple[str, list[object]]] = []
                self.executes: list[tuple[str, list[object]]] = []
                self.closed = False

            def use_db(self, db_name: str) -> None:
                self.used_dbs.append(db_name)

            def query(self, sql: str, params=None):
                self.queries.append((sql, list(params or [])))
                return [{"event_key": "old-key"}]

            def execute(self, sql: str, params=None) -> None:
                self.executes.append((sql, list(params or [])))

            def close(self) -> None:
                self.closed = True

        fake_db = FakeDb()
        with (
            patch.object(mi, "_db", return_value=fake_db),
            patch.object(mi, "sync_table_schema") as sync_schema,
        ):
            marked = mi.mark_superseded_earnings_events(
                [
                    {
                        "event_date": "2026-07-30",
                        "event_type": "EARNINGS",
                        "symbol": "AAA",
                        "title": "AAA Earnings Release",
                        "source": mi.EARNINGS_CALENDAR_SOURCE,
                    }
                ],
                superseded_at="2026-05-28 04:00:00",
            )

        self.assertEqual(marked, 1)
        self.assertEqual(fake_db.used_dbs, ["finance_meta"])
        sync_schema.assert_called_once()
        self.assertEqual(fake_db.executes[0][1][0], "superseded")
        self.assertEqual(fake_db.executes[0][1][-1], "old-key")
        self.assertTrue(fake_db.closed)

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
        self.assertEqual(captured["source_type"], "unknown")
        self.assertEqual(captured["validation_status"], "unknown")
        self.assertEqual(captured["event_status"], "active")
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
        self.assertIn("market_data_issue", synced_tables)
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
            "source_traits": {"is_weighted_mix": True},
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
            "construction_risk_audit": self._gate_audit(
                route="CONSTRUCTION_RISK_READY",
                label="Ready",
                criteria="Provider look-through coverage",
                status="PASS",
                ready=True,
                current="holdings 100.0% / exposure 100.0%",
                meaning="construction risk evidence attached",
            ),
            "risk_contribution_audit": self._gate_audit(
                route="RISK_CONTRIBUTION_READY",
                label="Ready",
                criteria="Risk contribution concentration",
                status="PASS",
                ready=True,
                current="max 35.0%",
                meaning="risk contribution evidence attached",
            ),
            "component_role_weight_audit": self._gate_audit(
                route="COMPONENT_ROLE_WEIGHT_READY",
                label="Ready",
                criteria="Component role source coverage",
                status="PASS",
                ready=True,
                current="explicit role weight 100.0%",
                meaning="component role and weight evidence attached",
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

    def _construction_gate_ready_audits(self) -> dict:
        return {
            "construction_risk_audit": self._gate_audit(
                route="CONSTRUCTION_RISK_READY",
                label="Ready",
                criteria="Provider look-through coverage",
                status="PASS",
                ready=True,
                current="holdings 100.0% / exposure 100.0%",
                meaning="construction risk evidence attached",
            ),
            "risk_contribution_audit": self._gate_audit(
                route="RISK_CONTRIBUTION_READY",
                label="Ready",
                criteria="Risk contribution concentration",
                status="PASS",
                ready=True,
                current="max 35.0%",
                meaning="risk contribution evidence attached",
            ),
            "component_role_weight_audit": self._gate_audit(
                route="COMPONENT_ROLE_WEIGHT_READY",
                label="Ready",
                criteria="Component role source coverage",
                status="PASS",
                ready=True,
                current="explicit role weight 100.0%",
                meaning="component role and weight evidence attached",
            ),
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
        self.assertEqual(row["판단 라벨"], "모니터링 후보 선정")
        self.assertEqual(row["Final Status"], "FINAL_REVIEW_DECISION_COMPLETE")
        self.assertEqual(row["Live Approval"], "Disabled")

    def test_saved_final_review_decision_review_summarizes_and_sorts_records(self) -> None:
        from app.services.backtest_evidence_read_model import build_saved_final_review_decision_review

        rows = [
            {
                "decision_id": "decision-hold",
                "updated_at": "2026-05-20T10:00:00",
                "decision_route": "HOLD_FOR_MORE_PAPER_TRACKING",
                "source_type": "practical_validation_result",
                "source_id": "validation-hold",
                "selected_components": [],
                "decision_evidence_snapshot": {"route": "READY_FOR_FINAL_DECISION", "score": 7.2},
                "operator_decision": {"reason": "more observation", "next_action": "paper tracking"},
                "investability_evidence_packet": {
                    "route": "INVESTABILITY_PACKET_REVIEW",
                    "gate_policy_snapshot": {
                        "outcome": "hold_or_re_review",
                        "select_allowed": False,
                        "review_required": ["Backtest realism review"],
                    },
                },
            },
            {
                "decision_id": "decision-selected",
                "updated_at": "2026-05-22T10:00:00",
                "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                "source_type": "practical_validation_result",
                "source_id": "validation-selected",
                "selected_components": [{"ticker": "SPY"}, {"ticker": "TLT"}],
                "decision_evidence_snapshot": {"route": "READY_FOR_FINAL_DECISION", "score": 8.8},
                "operator_decision": {"reason": "ready", "next_action": "dashboard recheck"},
                "investability_evidence_packet": {
                    "route": "INVESTABILITY_PACKET_READY",
                    "gate_policy_snapshot": {
                        "outcome": "select_ready",
                        "select_allowed": True,
                        "blockers": [],
                        "review_required": [],
                    },
                },
            },
            {
                "decision_id": "decision-reject",
                "updated_at": "2026-05-21T10:00:00",
                "decision_route": "REJECT_FOR_PRACTICAL_USE",
                "source_type": "practical_validation_result",
                "source_id": "validation-reject",
                "decision_evidence_snapshot": {"route": "REVIEW_REQUIRED", "score": 4.1, "blockers": ["missing data"]},
                "operator_decision": {"reason": "reject"},
            },
        ]

        review = build_saved_final_review_decision_review(rows)

        self.assertEqual(review["schema_version"], "final_review_saved_decision_review_v1")
        self.assertEqual(review["summary"]["total_records"], 3)
        self.assertEqual(review["summary"]["selected"], 1)
        self.assertEqual(review["summary"]["hold"], 1)
        self.assertEqual(review["summary"]["reject"], 1)
        self.assertEqual(review["summary"]["dashboard_eligible"], 1)
        self.assertEqual(review["summary"]["latest_decision_id"], "decision-selected")
        self.assertFalse(review["summary"]["live_approval"])
        self.assertIn("All", review["filter_options"])
        self.assertEqual(review["rows"][0]["Decision ID"], "decision-selected")
        self.assertEqual(review["rows"][0]["Route Family"], "Selected")
        self.assertEqual(review["rows"][0]["Dashboard Eligible"], "Yes")
        self.assertEqual(review["rows"][1]["Decision ID"], "decision-reject")
        self.assertEqual(review["rows"][2]["Evidence Issues"], 1)

    def test_final_review_decision_cockpit_summarizes_selected_route_state(self) -> None:
        from app.services.backtest_evidence_read_model import (
            build_final_review_candidate_board_rows,
            build_final_review_decision_cockpit,
            build_investability_evidence_packet,
        )

        validation = self._integrated_gate_ready_validation()
        source = {
            "source_type": "practical_validation_result",
            "source_id": validation["validation_id"],
            "source_title": "Ready candidate",
        }
        paper = {
            "route": "PAPER_OBSERVATION_READY",
            "blockers": [],
            "review_cadence": "monthly_or_rebalance_review",
            "tracking_benchmark": "SPY",
            "review_triggers": ["CAGR deterioration review"],
            "active_components": [{"title": "Ready component", "target_weight": 100.0}],
            "baseline_snapshot": {"target_weight_total": 100.0},
        }
        evidence = {"route": "READY_FOR_FINAL_DECISION", "blockers": []}
        packet = build_investability_evidence_packet(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
        )

        cockpit = build_final_review_decision_cockpit(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
            investability_packet=packet,
        )
        board_rows = build_final_review_candidate_board_rows(
            [
                {
                    "source": source,
                    "validation": validation,
                    "paper_observation": paper,
                    "decision_evidence": evidence,
                    "investability_packet": packet,
                }
            ]
        )

        self.assertEqual(cockpit["schema_version"], "final_review_decision_cockpit_v1")
        self.assertEqual(cockpit["state"], "SELECT_READY")
        self.assertTrue(cockpit["select_allowed"])
        self.assertEqual(cockpit["suggested_decision_route"], "SELECT_FOR_PRACTICAL_PORTFOLIO")
        self.assertEqual(cockpit["monitoring_handoff"]["tracking_benchmark"], "SPY")
        self.assertEqual(board_rows[0]["Decision State"], "모니터링 후보 가능")
        self.assertEqual(board_rows[0]["Select Allowed"], "Yes")
        self.assertEqual(board_rows[0]["Open Review"], 0)
        self.assertEqual(board_rows[0]["Candidate"], "Ready candidate")

    def test_final_review_decision_cockpit_surfaces_blocked_candidate_board_row(self) -> None:
        from app.services.backtest_evidence_read_model import (
            build_final_review_candidate_board_rows,
            build_final_review_decision_cockpit,
            build_investability_evidence_packet,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_id"] = "validation-blocked"
        validation["not_run_critical_domains"] = [
            {
                "domain": "stress_scenario_diagnostics",
                "title": "Stress scenario diagnostics",
                "next_action": "Run stress diagnostics before selection.",
            }
        ]
        validation["diagnostic_summary"]["status_counts"]["NOT_RUN"] = 1
        source = {
            "source_type": "practical_validation_result",
            "source_id": "validation-blocked",
            "source_title": "Blocked candidate",
        }
        paper = {"route": "PAPER_OBSERVATION_READY", "blockers": []}
        evidence = {"route": "READY_FOR_FINAL_DECISION", "blockers": []}
        packet = build_investability_evidence_packet(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
        )

        cockpit = build_final_review_decision_cockpit(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
            investability_packet=packet,
        )
        board_rows = build_final_review_candidate_board_rows(
            [
                {
                    "source": source,
                    "validation": validation,
                    "paper_observation": paper,
                    "decision_evidence": evidence,
                    "investability_packet": packet,
                }
            ]
        )

        self.assertEqual(cockpit["state"], "SELECT_BLOCKED")
        self.assertFalse(cockpit["select_allowed"])
        self.assertGreaterEqual(len(cockpit["must_fix_rows"]), 1)
        self.assertEqual(board_rows[0]["Decision State"], "선정 차단")
        self.assertEqual(board_rows[0]["Select Allowed"], "No")
        self.assertGreaterEqual(board_rows[0]["Blockers"], 1)
        self.assertEqual(board_rows[0]["NOT_RUN"], 1)

    def test_final_review_candidate_board_prioritizes_ready_candidates(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_candidate_board

        def candidate(label: str, outcome: str, score: float, *, blockers: int = 0, reviews: int = 0) -> dict:
            policy_rows = []
            policy_blockers = [
                "Risk Contribution: drop-one dependency missing",
            ][:blockers]
            policy_reviews = [
                "Backtest Realism: tax/account scope review",
            ][:reviews]
            if blockers:
                policy_rows.append(
                    {
                        "Criteria": "Risk Contribution",
                        "Severity": "BLOCK",
                        "Required Action": "drop-one dependency evidence를 보강합니다.",
                    }
                )
            if reviews:
                policy_rows.append(
                    {
                        "Criteria": "Backtest Realism",
                        "Severity": "REVIEW_REQUIRED",
                        "Required Action": "세금 / 계좌 scope를 최종 판단 전에 확인합니다.",
                    }
                )
            suggested = (
                "SELECT_FOR_PRACTICAL_PORTFOLIO"
                if outcome == "select_ready"
                else "RE_REVIEW_REQUIRED"
                if outcome == "blocked"
                else "HOLD_FOR_MORE_PAPER_TRACKING"
            )
            return {
                "source": {"source_title": label, "source_type": "practical_validation_result"},
                "validation": {"validation_id": f"validation-{label.lower()}"},
                "paper_observation": {"route": "PAPER_OBSERVATION_READY", "blockers": []},
                "decision_evidence": {"route": "READY_FOR_FINAL_DECISION", "blockers": []},
                "investability_packet": {
                    "route": "INVESTABILITY_PACKET_READY" if outcome == "select_ready" else "INVESTABILITY_PACKET_REVIEW",
                    "score": score,
                    "summary": {"not_run": 0, "review": reviews, "blocked": blockers},
                    "source_chain": {"validation_id": f"validation-{label.lower()}", "selection_source_id": f"source-{label.lower()}"},
                    "gate_policy_snapshot": {
                        "outcome": outcome,
                        "select_allowed": outcome == "select_ready",
                        "suggested_decision_route": suggested,
                        "blockers": policy_blockers,
                        "review_required": policy_reviews,
                        "policy_rows": policy_rows,
                    },
                },
            }

        board = build_final_review_candidate_board(
            [
                candidate("Blocked", "blocked", 6.1, blockers=1),
                candidate("Hold", "hold_or_re_review", 7.2, reviews=1),
                candidate("Ready", "select_ready", 8.8),
            ]
        )

        rows = board["rows"]
        self.assertEqual(board["schema_version"], "final_review_candidate_board_v1")
        self.assertEqual(board["summary"]["total_candidates"], 3)
        self.assertEqual(board["summary"]["select_ready"], 1)
        self.assertEqual(board["summary"]["hold_or_re_review"], 1)
        self.assertEqual(board["summary"]["blocked"], 1)
        self.assertEqual(rows[0]["Candidate"], "Ready")
        self.assertEqual(rows[0]["Review Priority"], "P1")
        self.assertEqual(rows[0]["Board Action"], "모니터링 후보 선정")
        self.assertEqual(rows[1]["Candidate"], "Hold")
        self.assertEqual(rows[2]["Candidate"], "Blocked")
        self.assertEqual(board["review_queue_rows"][0]["Action"], "모니터링 후보 선정")

    def test_final_review_decision_record_guide_blocks_selected_route_when_gate_blocks(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_final_review_decision_record_guide,
        )

        packet = {
            "route": "INVESTABILITY_PACKET_BLOCKED",
            "select_ready": False,
            "gate_policy_snapshot": {
                "outcome": "blocked",
                "select_allowed": False,
                "suggested_decision_route": "RE_REVIEW_REQUIRED",
                "blockers": ["Risk Contribution: missing drop-one dependency"],
                "review_required": [],
                "policy_rows": [
                    {
                        "Criteria": "Risk Contribution",
                        "Severity": "BLOCK",
                        "Required Action": "drop-one dependency evidence를 보강합니다.",
                    }
                ],
            },
        }

        guide = build_final_review_decision_record_guide(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            decision_evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=packet,
        )

        self.assertEqual(guide["schema_version"], "final_review_decision_record_guide_v1")
        self.assertEqual(guide["route_state"], "SELECT_ROUTE_BLOCKED")
        self.assertFalse(guide["recordable_route"])
        self.assertFalse(guide["selected_route_gate"]["Ready"])
        self.assertEqual(guide["suggested_decision_route"], "RE_REVIEW_REQUIRED")
        self.assertIn("Investability evidence packet", guide["blockers"])
        self.assertFalse(guide["record_boundary"]["live_approval"])

    def test_final_review_decision_record_guide_treats_non_select_route_as_status_only(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_decision_record_guide

        packet = {
            "route": "INVESTABILITY_PACKET_BLOCKED",
            "select_ready": False,
            "gate_policy_snapshot": {
                "outcome": "blocked",
                "select_allowed": False,
                "suggested_decision_route": "RE_REVIEW_REQUIRED",
                "blockers": ["Data Coverage: survivorship evidence missing"],
                "review_required": [],
            },
        }

        guide = build_final_review_decision_record_guide(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            decision_evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=packet,
        )

        self.assertEqual(guide["route_state"], "NON_SELECT_NOT_STORED")
        self.assertFalse(guide["recordable_route"])
        self.assertTrue(guide["selected_route_gate"]["Ready"])
        self.assertIn("Official selection route", guide["blockers"])
        self.assertIn("paper tracking", guide["route_templates"]["reason"])
        self.assertFalse(guide["record_boundary"]["non_select_persistence"])
        self.assertFalse(guide["record_boundary"]["waiver_persistence"])

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
        validation.update(self._construction_gate_ready_audits())

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
        self.assertIn("Construction Risk Audit", sections)
        self.assertIn("Risk Contribution Audit", sections)
        self.assertIn("Component Role / Weight Audit", sections)
        self.assertIn("Backtest Realism Audit", sections)
        self.assertEqual(packet["summary"]["validation_efficacy_route"], "VALIDATION_EFFICACY_READY")
        self.assertEqual(packet["summary"]["data_coverage_route"], "DATA_COVERAGE_READY")
        self.assertEqual(packet["summary"]["construction_risk_route"], "CONSTRUCTION_RISK_READY")
        self.assertEqual(packet["summary"]["risk_contribution_route"], "RISK_CONTRIBUTION_READY")
        self.assertEqual(packet["summary"]["component_role_weight_route"], "COMPONENT_ROLE_WEIGHT_READY")
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
        self.assertEqual(severities["construction_risk"], "PASS")
        self.assertEqual(severities["risk_contribution"], "PASS")
        self.assertEqual(severities["component_role_weight"], "PASS")
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

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(packet["gate_policy_snapshot"]["blockers"], [])
        self.assertFalse(packet["gate_policy_snapshot"]["waiver_required_for_select"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 4)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        severities = self._gate_policy_severities(packet)
        self.assertEqual(severities["provider_coverage"], "WATCH")
        self.assertEqual(severities["validation_efficacy"], "WATCH")
        self.assertEqual(severities["data_coverage"], "WATCH")
        self.assertEqual(severities["backtest_realism"], "WATCH")
        self.assertTrue(
            all(
                row["Selected Route"] == "Allowed with watch"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
                if row["Severity"] == "WATCH"
            )
        )

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

    def test_gate_policy_blocks_selected_route_on_construction_risk_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["construction_risk_audit"] = {
            "route": "CONSTRUCTION_RISK_NEEDS_INPUT",
            "route_label": "Evidence Input Needed",
            "rows": [
                {
                    "Criteria": "Provider look-through coverage",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "holdings 0.0% / exposure 0.0%",
                    "Meaning": "provider holdings / exposure evidence missing",
                    "Next Action": "ETF holdings / exposure provider snapshot을 먼저 보강합니다.",
                }
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "construction-risk-gap"},
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
            if row["Group"] == "construction_risk"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertIn("Provider look-through coverage", policy_row["Evidence"])
        self.assertIn("NEEDS_INPUT", policy_row["Current"])

    def test_gate_policy_requires_review_on_risk_contribution_review(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["risk_contribution_audit"] = {
            "route": "RISK_CONTRIBUTION_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Pairwise correlation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "avg 0.72 / max 0.91",
                    "Meaning": "component correlation is high",
                },
                {
                    "Criteria": "Risk contribution concentration",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "max 86.0%",
                    "Meaning": "one component dominates volatility contribution",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "risk-contribution-review"},
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
            if row["Group"] == "risk_contribution"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertIn("Pairwise correlation", policy_row["Evidence"])
        self.assertIn("Risk contribution concentration", policy_row["Evidence"])

    def test_gate_policy_blocks_selected_route_on_component_role_weight_blocked(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["component_role_weight_audit"] = {
            "route": "COMPONENT_ROLE_WEIGHT_BLOCKED",
            "route_label": "Blocked",
            "rows": [
                {
                    "Criteria": "Component role source coverage",
                    "Status": "BLOCKED",
                    "Ready": False,
                    "Current": "components 0 / explicit role weight 0.0%",
                    "Meaning": "active component role contract is unavailable",
                    "Next Action": "active component가 있는 source를 다시 선택합니다.",
                }
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "component-role-blocked"},
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
            if row["Group"] == "component_role_weight"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "BLOCK")
        self.assertIn("Component role source coverage", policy_row["Evidence"])

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
                **self._construction_gate_ready_audits(),
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

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
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
                **self._construction_gate_ready_audits(),
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
                **self._construction_gate_ready_audits(),
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
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertTrue(
            any(
                row["Group"] == "data_coverage" and row["Severity"] == "WATCH"
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
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertTrue(
            any(
                row["Group"] == "backtest_realism" and row["Severity"] == "WATCH"
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

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
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

    def test_practical_validation_selected_route_preflight_blocks_gross_only_review(self) -> None:
        from app.services.backtest_selected_route_preflight import (
            build_practical_validation_selected_route_preflight,
        )

        validation = self._integrated_gate_ready_validation()
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Net performance policy",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "gross-only / net cost curve proof missing",
                    "Meaning": "net performance proof is required before selected-route storage",
                }
            ],
        }

        preflight = build_practical_validation_selected_route_preflight(validation)

        self.assertFalse(preflight["select_allowed"])
        self.assertEqual(preflight["policy_outcome"], "hold_or_re_review")
        self.assertEqual(preflight["route"], "SELECTED_ROUTE_PREFLIGHT_NEEDS_INPUT")
        self.assertTrue(
            any("Backtest Realism" in item for item in preflight["review_required"])
        )

    def test_selected_route_preflight_blocks_equal_weight_missing_net_cost_proof(self) -> None:
        from app.services.backtest_selected_route_preflight import (
            build_practical_validation_selected_route_preflight,
        )

        validation = self._integrated_gate_ready_validation()
        validation["source_title"] = "Equal Weight proof-deficient regression"
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Net cost curve proof",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "not_proven / equal weight net curve missing",
                    "Meaning": "net cost curve proof is required before selected-route storage",
                },
                {
                    "Criteria": "Turnover evidence",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "not_estimated_missing_holdings",
                    "Meaning": "turnover proof is still missing",
                },
            ],
        }

        preflight = build_practical_validation_selected_route_preflight(validation)

        self.assertFalse(preflight["select_allowed"])
        self.assertEqual(preflight["policy_outcome"], "hold_or_re_review")
        self.assertEqual(preflight["route"], "SELECTED_ROUTE_PREFLIGHT_NEEDS_INPUT")
        self.assertTrue(any("Backtest Realism" in item for item in preflight["review_required"]))

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
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertTrue(
            any(
                row["Group"] == "provider_coverage" and row["Severity"] == "WATCH"
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
        self.assertFalse(hold["can_save"])
        self.assertIn("Official selection route", hold["blockers"])

    def test_final_review_decision_row_stores_compact_gate_policy_snapshot(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_decision_row

        selection_policy = {
            "schema_version": "final_review_selection_gate_policy_v1",
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
        }
        deployment_policy = {
            "schema_version": "deployment_readiness_gate_policy_v1",
            "outcome": "hold_or_re_review",
            "select_allowed": False,
            "policy_rows": [],
        }
        packet = {
            "route": "INVESTABILITY_PACKET_READY",
            "select_ready": True,
            "gate_policy_snapshot": selection_policy,
            "selection_gate_policy_snapshot": selection_policy,
            "deployment_readiness_policy_snapshot": deployment_policy,
            "open_review_items": [{"Group": "provider_coverage", "Criteria": "Provider / Look-through"}],
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
        self.assertEqual(row["selection_gate_policy_snapshot"]["schema_version"], "final_review_selection_gate_policy_v1")
        self.assertEqual(row["deployment_readiness_policy_snapshot"]["schema_version"], "deployment_readiness_gate_policy_v1")
        self.assertEqual(row["open_review_items"][0]["Group"], "provider_coverage")


class SelectedPortfolioMonitoringTimelineContractTests(unittest.TestCase):
    def _selected_row(self) -> dict:
        return {
            "decision_id": "decision-selected",
            "updated_at": "2026-05-28T10:00:00",
            "operation_status": "normal",
            "operation_status_label": "모니터링 기준 통과",
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
                "source_type": "practical_validation_result",
                "source_id": "source-selected",
                "source_title": "Selected portfolio source",
                "selection_source_id": "source-selected",
                "validation_id": "validation-selected",
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

    def _ready_recheck_preflight(self) -> dict:
        return {
            "schema_version": "selected_recheck_operations_preflight_v1",
            "route": "RECHECK_PREFLIGHT_READY",
            "route_label": "재검증 preflight 준비 완료",
            "conclusion": "ready",
            "metrics": {
                "missing_symbol_count": 0,
                "stale_symbol_count": 0,
                "watch_symbol_count": 0,
            },
        }

    def _needs_data_recheck_preflight(self) -> dict:
        return {
            "schema_version": "selected_recheck_operations_preflight_v1",
            "route": "RECHECK_PREFLIGHT_NEEDS_DATA",
            "route_label": "재검증 preflight 데이터 확인 필요",
            "conclusion": "needs data",
            "metrics": {
                "missing_symbol_count": 1,
                "stale_symbol_count": 0,
                "watch_symbol_count": 0,
            },
        }

    def _selected_row_with_open_issue(self) -> dict:
        row = self._selected_row()
        raw = dict(row["raw_decision"])
        raw["open_review_items"] = [
            {
                "Group": "provider_coverage",
                "Criteria": "Provider / Look-through",
                "Severity": "OPEN_REVIEW",
                "Current": "partial provider coverage",
                "Evidence": "Holdings coverage is partial.",
                "Required Action": "Provider holdings / exposure evidence를 보강합니다.",
                "Selection Gate Effect": "Open review item",
                "Deployment Gate Effect": "REVIEW_REQUIRED",
            }
        ]
        raw["deployment_readiness_policy_snapshot"] = {
            "schema_version": "deployment_readiness_gate_policy_v1",
            "outcome": "hold_or_re_review",
            "select_allowed": False,
            "policy_rows": [
                {
                    "Criteria": "Provider / Look-through",
                    "Group": "provider_coverage",
                    "Ready": False,
                    "Severity": "REVIEW_REQUIRED",
                    "Current": "partial provider coverage",
                    "Evidence": "Holdings coverage is partial.",
                    "Required Action": "Provider holdings / exposure evidence를 보강합니다.",
                }
            ],
        }
        row["raw_decision"] = raw
        return row

    def test_selected_dashboard_monitoring_portfolio_saved_state_crud_is_soft_delete(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import (
            add_selected_dashboard_portfolio_strategy,
            delete_selected_dashboard_portfolio,
            load_selected_dashboard_portfolios,
            remove_selected_dashboard_portfolio_strategy,
            save_selected_dashboard_portfolio,
            update_selected_dashboard_portfolio_strategy_slot,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "SELECTED_DASHBOARD_PORTFOLIOS.jsonl"
            record = save_selected_dashboard_portfolio(
                name="Core Monitor",
                description="selected candidates",
                now="2026-06-01T10:00:00",
                path=path,
            )

            self.assertEqual(record["schema_version"], 1)
            self.assertEqual(record["name"], "Core Monitor")
            self.assertEqual(record["selected_decision_ids"], [])
            self.assertEqual(record["strategy_slots"], [])
            self.assertFalse(record["storage_boundary"]["final_decision_registry_write"])
            self.assertFalse(record["storage_boundary"]["monitoring_log_auto_write"])

            add_result = add_selected_dashboard_portfolio_strategy(
                record["portfolio_id"],
                "decision-selected",
                start="2024-01-01",
                use_latest_end=True,
                initial_capital=10000.0,
                memo="core sleeve",
                now="2026-06-01T10:01:00",
                path=path,
            )
            duplicate_result = add_selected_dashboard_portfolio_strategy(
                record["portfolio_id"],
                "decision-selected",
                now="2026-06-01T10:02:00",
                path=path,
            )

            self.assertEqual(add_result["status"], "added")
            self.assertEqual(duplicate_result["status"], "duplicate")
            portfolios = load_selected_dashboard_portfolios(path=path)
            self.assertEqual(portfolios[0]["selected_decision_ids"], ["decision-selected"])
            self.assertEqual(portfolios[0]["strategy_slots"][0]["start"], "2024-01-01")
            self.assertEqual(portfolios[0]["strategy_slots"][0]["initial_capital"], 10000.0)

            update_result = update_selected_dashboard_portfolio_strategy_slot(
                record["portfolio_id"],
                "decision-selected",
                start="2024-02-01",
                end="2026-05-29",
                use_latest_end=False,
                initial_capital=12000.0,
                memo="updated sleeve",
                now="2026-06-01T10:02:30",
                path=path,
            )
            self.assertEqual(update_result["status"], "updated")
            updated_slot = load_selected_dashboard_portfolios(path=path)[0]["strategy_slots"][0]
            self.assertEqual(updated_slot["start"], "2024-02-01")
            self.assertEqual(updated_slot["end"], "2026-05-29")
            self.assertFalse(updated_slot["use_latest_end"])
            self.assertEqual(updated_slot["initial_capital"], 12000.0)

            remove_result = remove_selected_dashboard_portfolio_strategy(
                record["portfolio_id"],
                "decision-selected",
                now="2026-06-01T10:03:00",
                path=path,
            )
            self.assertEqual(remove_result["status"], "removed")
            self.assertEqual(load_selected_dashboard_portfolios(path=path)[0]["selected_decision_ids"], [])

            self.assertTrue(
                delete_selected_dashboard_portfolio(
                    record["portfolio_id"],
                    now="2026-06-01T10:04:00",
                    path=path,
                )
            )
            self.assertEqual(load_selected_dashboard_portfolios(path=path), [])
            deleted_rows = load_selected_dashboard_portfolios(include_deleted=True, path=path)
            self.assertEqual(deleted_rows[0]["deleted_at"], "2026-06-01T10:04:00")

    def test_selected_dashboard_portfolio_state_joins_selected_strategy_pool(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import (
            build_final_selected_portfolio_dashboard_row,
            build_selected_dashboard_portfolio_state,
        )

        dashboard_row = build_final_selected_portfolio_dashboard_row(self._selected_row()["raw_decision"])
        state = build_selected_dashboard_portfolio_state(
            portfolios=[
                {
                    "portfolio_id": "p1",
                    "name": "Core Monitor",
                    "selected_decision_ids": ["decision-selected", "decision-selected", "missing-decision"],
                    "updated_at": "2026-06-01T10:00:00",
                }
            ],
            dashboard_rows=[dashboard_row],
        )

        self.assertEqual(state["schema_version"], "selected_dashboard_monitoring_portfolio_state_v1")
        self.assertEqual(state["metrics"]["portfolio_count"], 1)
        self.assertEqual(state["metrics"]["selected_strategy_pool_count"], 1)
        self.assertEqual(state["metrics"]["duplicate_reference_count"], 1)
        self.assertEqual(state["metrics"]["missing_reference_count"], 1)
        portfolio = state["portfolios"][0]
        self.assertEqual(portfolio["strategy_count"], 1)
        self.assertEqual(portfolio["missing_strategy_count"], 1)
        self.assertEqual(portfolio["strategy_rows"][0]["decision_id"], "decision-selected")
        self.assertEqual(portfolio["complete_strategy_slot_count"], 1)
        self.assertEqual(portfolio["incomplete_strategy_slot_count"], 1)
        self.assertTrue(portfolio["strategy_rows"][0]["slot_input_complete"])
        self.assertFalse(state["execution_boundary"]["final_decision_registry_write"])
        self.assertFalse(state["execution_boundary"]["monitoring_log_auto_write"])

    def test_selected_dashboard_portfolio_state_marks_complete_strategy_slots_ready(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import (
            build_final_selected_portfolio_dashboard_row,
            build_selected_dashboard_portfolio_state,
        )

        dashboard_row = build_final_selected_portfolio_dashboard_row(self._selected_row()["raw_decision"])
        state = build_selected_dashboard_portfolio_state(
            portfolios=[
                {
                    "portfolio_id": "p1",
                    "name": "Core Monitor",
                    "strategy_slots": [
                        {
                            "decision_id": "decision-selected",
                            "start": "2024-01-01",
                            "end": "",
                            "use_latest_end": True,
                            "initial_capital": 30000.0,
                            "memo": "monitoring row",
                        }
                    ],
                    "updated_at": "2026-06-01T10:00:00",
                }
            ],
            dashboard_rows=[dashboard_row],
        )

        portfolio = state["portfolios"][0]
        self.assertEqual(portfolio["dashboard_status"], "Ready")
        self.assertEqual(portfolio["complete_strategy_slot_count"], 1)
        self.assertEqual(portfolio["incomplete_strategy_slot_count"], 0)
        self.assertEqual(portfolio["virtual_capital_total"], 30000.0)
        self.assertTrue(portfolio["strategy_rows"][0]["slot_input_complete"])

    def test_operations_overview_model_keeps_only_monitoring_and_health_lanes(self) -> None:
        spec = importlib.util.find_spec("app.web.operations_overview")
        self.assertIsNotNone(spec, "Operations Overview read model module should exist")

        from app.web.operations_overview import build_operations_overview_model

        model = build_operations_overview_model(
            selected_dashboard={
                "summary": {
                    "final_decision_count": 4,
                    "selected_decision_count": 2,
                    "dashboard_row_count": 2,
                    "status_counts": {"normal": 1, "watch": 1, "blocked": 0},
                },
                "portfolio_state": {
                    "metrics": {
                        "portfolio_count": 1,
                        "assigned_strategy_reference_count": 2,
                        "missing_reference_count": 0,
                    }
                },
            },
            run_history=[
                {
                    "job_name": "daily_market_update",
                    "status": "failed",
                    "started_at": "2026-06-03T09:00:00",
                }
            ],
            candidate_records=[{"registry_id": "cand-1"}, {"registry_id": "cand-2"}],
        )

        self.assertEqual(model["schema_version"], "operations_overview_v2")
        self.assertEqual(
            [lane["key"] for lane in model["lanes"]],
            ["portfolio_monitoring", "system_data_health"],
        )
        lane_by_key = {lane["key"]: lane for lane in model["lanes"]}
        self.assertEqual(lane_by_key["portfolio_monitoring"]["priority"], "primary")
        self.assertEqual(lane_by_key["portfolio_monitoring"]["status"], "Review Needed")
        self.assertEqual(lane_by_key["portfolio_monitoring"]["metrics"]["selected_decision_count"], 2)
        self.assertEqual(lane_by_key["portfolio_monitoring"]["metrics"]["watch_or_review_count"], 1)
        self.assertEqual(lane_by_key["system_data_health"]["status"], "Attention Needed")
        self.assertNotIn("archive_recovery", lane_by_key)
        self.assertNotIn("reference_reports", lane_by_key)

    def test_operations_overview_model_keeps_execution_boundary_disabled(self) -> None:
        spec = importlib.util.find_spec("app.web.operations_overview")
        self.assertIsNotNone(spec, "Operations Overview read model module should exist")

        from app.web.operations_overview import build_operations_overview_model

        model = build_operations_overview_model(
            selected_dashboard={"summary": {}, "portfolio_state": {"metrics": {}}},
            run_history=[],
            candidate_records=[],
        )

        self.assertFalse(model["execution_boundary"]["live_approval"])
        self.assertFalse(model["execution_boundary"]["broker_order"])
        self.assertFalse(model["execution_boundary"]["account_sync"])
        self.assertFalse(model["execution_boundary"]["auto_rebalance"])
        self.assertFalse(model["execution_boundary"]["registry_write"])
        self.assertEqual(model["lanes"][0]["target_surface"], "Operations > Portfolio Monitoring")

    def test_operations_console_model_hides_cleanup_artifacts_and_keeps_action_queue(self) -> None:
        from app.web.operations_overview import build_operations_overview_model

        model = build_operations_overview_model(
            selected_dashboard={
                "summary": {
                    "selected_decision_count": 3,
                    "dashboard_row_count": 3,
                    "status_counts": {"normal": 1, "watch": 1, "rebalance_needed": 1, "blocked": 0},
                },
                "portfolio_state": {
                    "metrics": {
                        "portfolio_count": 1,
                        "assigned_strategy_reference_count": 3,
                        "missing_reference_count": 0,
                    }
                },
            },
            run_history=[{"job_name": "daily_market_update", "status": "failed"}],
            candidate_records=[{"registry_id": "cand-1"}],
        )

        self.assertEqual(model["console_version"], "operations_console_v2")
        self.assertNotIn("stage_roadmap", model)
        self.assertNotIn("surface_audit", model)

        action_keys = {item["key"] for item in model["action_queue"]}
        self.assertIn("review_portfolio_monitoring", action_keys)
        self.assertIn("inspect_system_data_health", action_keys)
        self.assertNotIn("archive_recovery_available", action_keys)
        self.assertNotIn("place_order", action_keys)
        for item in model["action_queue"]:
            self.assertFalse(item["execution_boundary"]["order_instruction"])
            self.assertFalse(item["execution_boundary"]["auto_rebalance"])

    def test_operations_console_model_uses_korean_operator_facing_copy(self) -> None:
        from app.web.operations_overview import build_operations_overview_model

        model = build_operations_overview_model(
            selected_dashboard={
                "summary": {
                    "selected_decision_count": 2,
                    "dashboard_row_count": 2,
                    "status_counts": {"normal": 2, "watch": 0, "rebalance_needed": 0, "blocked": 0},
                },
                "portfolio_state": {
                    "metrics": {
                        "portfolio_count": 1,
                        "assigned_strategy_reference_count": 2,
                        "missing_reference_count": 0,
                    }
                },
            },
            run_history=[],
            candidate_records=[],
        )

        self.assertIn("일상 점검", model["action_queue"][0]["title"])
        self.assertIn("모니터링 후보", model["action_queue"][0]["reason"])
        self.assertIn("모니터링 후보", model["lanes"][0]["detail"])
        self.assertEqual(len(model["lanes"]), 2)

    def test_operations_review_queue_prioritizes_blockers_scenarios_reviews_and_system_health(self) -> None:
        from app.web.operations_overview import build_operations_overview_model

        model = build_operations_overview_model(
            selected_dashboard={
                "summary": {
                    "selected_decision_count": 3,
                    "dashboard_row_count": 3,
                    "status_counts": {"normal": 1, "watch": 1, "blocked": 1},
                },
                "portfolio_state": {
                    "metrics": {
                        "portfolio_count": 1,
                        "assigned_strategy_reference_count": 3,
                        "missing_reference_count": 1,
                        "incomplete_strategy_slot_count": 1,
                    },
                    "portfolios": [
                        {
                            "portfolio_id": "p1",
                            "strategy_rows": [
                                {
                                    "decision_id": "decision-1",
                                    "scenario_status": "stale",
                                    "latest_scenario_date": "2026-05-28",
                                    "open_review_items": [{"Group": "provider"}],
                                },
                                {
                                    "decision_id": "decision-2",
                                    "scenario_status": "current",
                                    "latest_scenario_date": "2026-06-02",
                                    "raw_decision": {
                                        "open_review_items": [{"Group": "risk"}],
                                    },
                                },
                                {
                                    "decision_id": "decision-3",
                                    "slot_input_complete": False,
                                    "slot_blockers": ["start date required"],
                                },
                            ],
                        }
                    ],
                },
            },
            run_history=[{"job_name": "daily_market_update", "status": "failed"}],
            candidate_records=[],
        )

        self.assertEqual(model["action_queue_schema_version"], "operations_review_queue_v1")
        queue = model["action_queue"]
        self.assertEqual(
            [item["key"] for item in queue],
            [
                "resolve_monitoring_setup_blockers",
                "inspect_system_data_health",
                "refresh_monitoring_scenarios",
                "review_portfolio_monitoring",
            ],
        )
        self.assertEqual([item["priority"] for item in queue], ["P0", "P0", "P1", "P2"])
        self.assertEqual([item["evidence_key"] for item in queue], ["open_review", "system_run_health", "scenario_freshness", "open_review"])
        self.assertEqual(queue[0]["summary_metric"], "3 blockers")
        self.assertEqual(queue[1]["target_surface"], "Operations > System / Data Health")
        self.assertIn("stale", queue[2]["reason"])
        self.assertIn("open review", queue[3]["reason"].lower())
        self.assertEqual([item["sort_rank"] for item in queue], sorted(item["sort_rank"] for item in queue))
        for item in queue:
            self.assertFalse(item["execution_boundary"]["registry_write"])
            self.assertFalse(item["execution_boundary"]["order_instruction"])
            self.assertFalse(item["execution_boundary"]["auto_rebalance"])

    def test_operations_review_queue_source_renders_priority_and_evidence(self) -> None:
        source = Path("app/web/operations_overview.py").read_text(encoding="utf-8")

        self.assertIn("Priority", source)
        self.assertIn("Evidence", source)
        self.assertIn("summary_metric", source)
        self.assertIn("sort_rank", source)
        self.assertIn("operations_review_queue_v1", source)

    def test_operations_overview_model_adds_portfolio_first_summary(self) -> None:
        from app.web.operations_overview import build_operations_overview_model

        model = build_operations_overview_model(
            selected_dashboard={
                "summary": {
                    "selected_decision_count": 3,
                    "dashboard_row_count": 3,
                    "status_counts": {"normal": 1, "watch": 1, "blocked": 1},
                },
                "portfolio_state": {
                    "metrics": {
                        "portfolio_count": 2,
                        "assigned_strategy_reference_count": 3,
                        "missing_reference_count": 1,
                        "incomplete_strategy_slot_count": 1,
                    },
                    "portfolios": [
                        {
                            "portfolio_id": "p1",
                            "name": "Core Monitor",
                            "dashboard_status": "Needs Review",
                            "strategy_rows": [
                                {
                                    "decision_id": "decision-1",
                                    "scenario_status": "stale",
                                    "latest_scenario_date": "2026-05-28",
                                    "open_review_items": [{"Group": "provider"}],
                                    "slot_input_complete": True,
                                    "raw_decision": {
                                        "selected_components": [
                                            {
                                                "title": "Risk-On Momentum",
                                                "period_end": "2026-05-29",
                                                "selection_history": [
                                                    {
                                                        "date": "2026-05-29",
                                                        "selected_tickers": ["QQQ", "SPY"],
                                                        "target_weights": [0.55, 0.45],
                                                    }
                                                ],
                                                "replay_contract": {
                                                    "settings_snapshot": {"rebalance_interval": 1}
                                                },
                                            }
                                        ],
                                    },
                                },
                                {
                                    "decision_id": "decision-2",
                                    "scenario_status": "current",
                                    "latest_scenario_date": "2026-06-02",
                                    "slot_input_complete": True,
                                    "raw_decision": {
                                        "open_review_items": [{"Group": "risk"}],
                                        "selected_components": [
                                            {
                                                "title": "Quality Value",
                                                "period_end": "2026-06-02",
                                                "replay_contract": {
                                                    "settings_snapshot": {"rebalance_interval": 1}
                                                },
                                            }
                                        ],
                                    },
                                },
                            ],
                        },
                        {
                            "portfolio_id": "p2",
                            "name": "Satellite Monitor",
                            "dashboard_status": "Needs Review",
                            "strategy_rows": [
                                {
                                    "decision_id": "decision-3",
                                    "slot_input_complete": False,
                                    "slot_blockers": ["start date required"],
                                }
                            ],
                        },
                    ],
                },
            },
            run_history=[],
            candidate_records=[],
        )

        summary = model["portfolio_summary"]
        self.assertEqual(summary["schema_version"], "operations_portfolio_summary_v1")
        self.assertEqual(summary["status"], "Blocked")
        self.assertEqual(summary["tone"], "danger")
        self.assertEqual(summary["active_portfolio_count"], 2)
        self.assertEqual(summary["assigned_strategy_count"], 3)
        self.assertEqual(summary["stale_scenario_count"], 1)
        self.assertEqual(summary["blocked_count"], 1)
        self.assertEqual(summary["missing_reference_count"], 1)
        self.assertEqual(summary["incomplete_strategy_slot_count"], 1)
        self.assertEqual(summary["open_review_item_count"], 2)
        self.assertEqual(summary["latest_scenario_date"], "2026-06-02")
        self.assertEqual(summary["target_snapshot_date"], "2026-06-02")
        self.assertEqual(summary["next_review_date"], "2026-06-30")
        self.assertFalse(summary["execution_boundary"]["auto_rebalance"])

    def test_operations_overview_model_adds_evidence_health_strip(self) -> None:
        from app.web.operations_overview import build_operations_overview_model

        selected_policy = {
            "schema_version": "final_review_selection_gate_policy_v1",
            "select_allowed": True,
            "outcome": "SELECT_ALLOWED",
            "review_required": [],
            "blockers": [],
        }
        model = build_operations_overview_model(
            selected_dashboard={
                "summary": {
                    "selected_decision_count": 2,
                    "dashboard_row_count": 2,
                    "status_counts": {"normal": 1, "watch": 1, "blocked": 0},
                },
                "portfolio_state": {
                    "metrics": {
                        "portfolio_count": 1,
                        "assigned_strategy_reference_count": 2,
                        "missing_reference_count": 0,
                        "incomplete_strategy_slot_count": 0,
                    },
                    "portfolios": [
                        {
                            "portfolio_id": "p1",
                            "strategy_rows": [
                                {
                                    "decision_id": "decision-1",
                                    "scenario_status": "stale",
                                    "latest_scenario_date": "2026-05-28",
                                    "open_review_items": [{"Group": "provider"}],
                                    "raw_decision": {
                                        "investability_evidence_packet": {
                                            "selection_gate_policy_snapshot": selected_policy,
                                        }
                                    },
                                },
                                {
                                    "decision_id": "decision-2",
                                    "scenario_status": "current",
                                    "latest_scenario_date": "2026-06-02",
                                    "raw_decision": {
                                        "selection_gate_policy_snapshot": selected_policy,
                                    },
                                },
                            ],
                        }
                    ],
                },
            },
            run_history=[{"job_name": "daily_market_update", "status": "partial_success"}],
            candidate_records=[],
        )

        evidence = model["evidence_health"]
        self.assertEqual(evidence["schema_version"], "operations_evidence_health_v1")
        self.assertEqual(evidence["overall_status"], "Review Needed")
        self.assertEqual(evidence["overall_tone"], "warning")
        item_by_key = {item["key"]: item for item in evidence["items"]}
        self.assertEqual(
            list(item_by_key),
            ["scenario_freshness", "selected_evidence", "open_review", "system_run_health"],
        )
        self.assertEqual(item_by_key["scenario_freshness"]["status"], "REVIEW")
        self.assertEqual(item_by_key["scenario_freshness"]["value"], "1 stale / 0 pending")
        self.assertEqual(item_by_key["selected_evidence"]["status"], "PASS")
        self.assertEqual(item_by_key["selected_evidence"]["value"], "2/2 ready")
        self.assertEqual(item_by_key["open_review"]["status"], "REVIEW")
        self.assertEqual(item_by_key["open_review"]["value"], "1 open")
        self.assertEqual(item_by_key["system_run_health"]["status"], "REVIEW")
        self.assertEqual(item_by_key["system_run_health"]["value"], "partial_success")
        self.assertFalse(evidence["execution_boundary"]["registry_write"])
        self.assertFalse(evidence["execution_boundary"]["auto_rebalance"])

    def test_operations_overview_source_renders_evidence_health_before_queue(self) -> None:
        source = Path("app/web/operations_overview.py").read_text(encoding="utf-8")

        self.assertIn("    _render_portfolio_summary(model)", source)
        self.assertIn("    _render_evidence_health_strip(model)", source)
        self.assertIn("    _render_action_queue(model", source)
        self.assertLess(source.index("    _render_portfolio_summary(model)"), source.index("    _render_evidence_health_strip(model)"))
        self.assertLess(source.index("    _render_evidence_health_strip(model)"), source.index("    _render_action_queue(model"))
        self.assertIn("Evidence Health", source)
        self.assertIn("Selected Evidence", source)
        self.assertIn("System Run Health", source)

    def test_operations_overview_source_renders_portfolio_summary_before_queue(self) -> None:
        source = Path("app/web/operations_overview.py").read_text(encoding="utf-8")

        self.assertIn("    _render_portfolio_summary(model)", source)
        self.assertIn("    _render_action_queue(model", source)
        self.assertLess(source.index("    _render_portfolio_summary(model)"), source.index("    _render_action_queue(model"))
        self.assertIn("Portfolio Monitoring Status", source)
        self.assertIn("Stale Scenarios", source)
        self.assertIn("Open Review", source)
        self.assertIn("Next Review", source)

    def test_operations_overview_source_hides_development_history_titles(self) -> None:
        source = Path("app/web/operations_overview.py").read_text(encoding="utf-8")

        self.assertNotIn("Operations restructuring roadmap", source)
        self.assertNotIn("Operations surface decisions", source)
        self.assertNotIn("Hidden archive", source)
        self.assertNotIn("Archive 도구", source)
        self.assertNotIn("과거 archive", source)

    def test_operations_navigation_hides_archive_pages_from_top_level_tabs(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")
        operations_block = source.split('"Operations": [', 1)[1].split("],", 1)[0]

        self.assertIn("operations_overview_page", operations_block)
        self.assertIn("selected_portfolio_dashboard_page", operations_block)
        self.assertIn("ops_review_page", operations_block)
        self.assertNotIn("backtest_history_page", operations_block)
        self.assertNotIn("candidate_library_page", operations_block)

    def test_portfolio_monitoring_rebalance_table_uses_target_snapshot_language(self) -> None:
        from app.web.final_selected_portfolio_dashboard import _build_rebalance_table

        table = _build_rebalance_table(
            [
                {
                    "source_title": "GRS Liquid Macro Top2",
                    "raw_decision": {
                        "selected_components": [
                            {
                                "title": "GRS Liquid Macro Top2",
                                "selection_history": [
                                    {
                                        "date": "2026-05-29",
                                        "selected_tickers": ["QQQ", "SPY"],
                                        "target_weights": [0.503, 0.503],
                                        "cash_share": 0.0,
                                    }
                                ],
                                "replay_contract": {"settings_snapshot": {"rebalance_interval": 1}},
                            }
                        ]
                    },
                }
            ]
        )

        self.assertIn("Target Snapshot Date", table.columns)
        self.assertIn("Next Review Date", table.columns)
        self.assertIn("Current Target Snapshot", table.columns)
        self.assertIn("Target Meaning", table.columns)
        self.assertIn("Execution Boundary", table.columns)
        self.assertNotIn("Last Rebalance", table.columns)
        self.assertNotIn("Next Rebalance", table.columns)

        row = table.iloc[0].to_dict()
        self.assertEqual(row["Target Snapshot Date"], "2026-05-29")
        self.assertEqual(row["Next Review Date"], "2026-06-30")
        self.assertIn("QQQ 50.3%", row["Current Target Snapshot"])
        self.assertIn("manual review", row["Target Meaning"])
        self.assertIn("No order", row["Execution Boundary"])

    def _ready_provider_evidence(self) -> dict:
        return {
            "schema_version": "selected_provider_evidence_v1",
            "route": "SELECTED_PROVIDER_READY",
            "route_label": "Provider 근거 준비 완료",
            "conclusion": "ready",
            "metrics": {
                "stale_count": 0,
                "partial_coverage_count": 0,
                "needs_input_count": 0,
            },
        }

    def _needs_data_provider_evidence(self) -> dict:
        return {
            "schema_version": "selected_provider_evidence_v1",
            "route": "SELECTED_PROVIDER_NEEDS_DATA",
            "route_label": "Provider DB 확인 필요",
            "conclusion": "needs data",
            "metrics": {
                "stale_count": 1,
                "partial_coverage_count": 1,
                "needs_input_count": 2,
            },
        }

    def test_selected_dashboard_handoff_review_links_selected_final_review_rows(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import (
            SELECTED_DASHBOARD_HANDOFF_SCHEMA_VERSION,
            build_selected_dashboard_handoff_review,
        )

        handoff = build_selected_dashboard_handoff_review([self._selected_row()])

        self.assertEqual(handoff["schema_version"], SELECTED_DASHBOARD_HANDOFF_SCHEMA_VERSION)
        self.assertEqual(handoff["route"], "HANDOFF_READY")
        self.assertEqual(handoff["destination"], "Operations > Selected Portfolio Dashboard")
        self.assertEqual(handoff["summary"]["final_decision_count"], 1)
        self.assertEqual(handoff["summary"]["selected_decision_count"], 1)
        self.assertEqual(handoff["summary"]["dashboard_row_count"], 1)
        self.assertEqual(handoff["summary"]["monitorable_count"], 1)
        self.assertEqual(handoff["rows"][0]["Decision ID"], "decision-selected")
        self.assertEqual(handoff["rows"][0]["Handoff Destination"], "Operations > Selected Portfolio Dashboard")
        self.assertEqual(handoff["rows"][0]["Live Approval"], "Disabled")
        checks = {row["Check"]: row for row in handoff["checklist"]}
        self.assertEqual(checks["Selected route record"]["Status"], "PASS")
        self.assertEqual(checks["Monitorable row"]["Status"], "PASS")
        self.assertFalse(handoff["execution_boundary"]["registry_write"])
        self.assertFalse(handoff["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(handoff["execution_boundary"]["live_approval"])
        self.assertFalse(handoff["execution_boundary"]["order_instruction"])
        self.assertFalse(handoff["execution_boundary"]["auto_rebalance"])

    def test_selected_dashboard_handoff_review_blocks_without_selected_route(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_dashboard_handoff_review

        row = dict(self._selected_row()["raw_decision"])
        row["decision_route"] = "HOLD_FOR_MORE_PAPER_TRACKING"
        row["selected_practical_portfolio"] = False

        handoff = build_selected_dashboard_handoff_review([row])

        self.assertEqual(handoff["route"], "HANDOFF_NO_SELECTED_DECISION")
        self.assertEqual(handoff["summary"]["final_decision_count"], 1)
        self.assertEqual(handoff["summary"]["selected_decision_count"], 0)
        self.assertEqual(handoff["summary"]["dashboard_row_count"], 0)
        self.assertEqual(handoff["rows"], [])
        checks = {item["Check"]: item for item in handoff["checklist"]}
        self.assertEqual(checks["Final Review decision record"]["Status"], "PASS")
        self.assertEqual(checks["Selected route record"]["Status"], "NEEDS_INPUT")
        self.assertFalse(handoff["execution_boundary"]["auto_rebalance"])

    def test_selected_dashboard_handoff_review_surfaces_blocked_dashboard_contract(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_dashboard_handoff_review

        row = dict(self._selected_row()["raw_decision"])
        row["selected_components"] = [
            {
                "title": "Incomplete Component",
                "registry_id": "candidate-incomplete",
                "target_weight": 80.0,
                "benchmark": "SPY",
            }
        ]

        handoff = build_selected_dashboard_handoff_review([row])

        self.assertEqual(handoff["route"], "HANDOFF_BLOCKED")
        self.assertEqual(handoff["summary"]["selected_decision_count"], 1)
        self.assertEqual(handoff["summary"]["monitorable_count"], 0)
        self.assertEqual(handoff["summary"]["blocked_count"], 1)
        self.assertEqual(handoff["rows"][0]["Dashboard Status"], "운영 대상 차단")
        self.assertIn("target weight", handoff["rows"][0]["Handoff Action"])
        checks = {item["Check"]: item for item in handoff["checklist"]}
        self.assertEqual(checks["Dashboard row build"]["Status"], "PASS")
        self.assertEqual(checks["Monitorable row"]["Status"], "BLOCKED")
        self.assertFalse(handoff["execution_boundary"]["order_instruction"])

    def _ready_recheck_result(self) -> dict:
        return {
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
        }

    def test_monitoring_timeline_is_read_only_and_requires_recheck_input(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_monitoring_timeline

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
        self.assertEqual(timeline["source_contract"]["schema_version"], "selected_decision_source_consistency_v1")
        self.assertEqual(timeline["source_contract"]["decision_id"], "decision-selected")
        self.assertEqual(timeline["source_contract"]["source_identity"], "practical_validation_result:source-selected")
        self.assertEqual(timeline["source_contract"]["durable_source"], "FINAL_PORTFOLIO_SELECTION_DECISIONS")
        self.assertFalse(timeline["source_contract"]["execution_boundary"]["registry_write"])
        self.assertFalse(timeline["source_contract"]["execution_boundary"]["monitoring_log_auto_write"])

    def test_monitoring_timeline_surfaces_recheck_breach_and_drift_watch(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_monitoring_timeline

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

    def test_allocation_drift_boundary_is_read_only_and_session_only(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import (
            SELECTED_ALLOCATION_DRIFT_BOUNDARY_SCHEMA_VERSION,
            build_selected_portfolio_allocation_drift_boundary,
            build_selected_portfolio_current_weight_inputs,
            build_selected_portfolio_drift_alert_preview,
            build_selected_portfolio_drift_check,
        )

        weight_inputs = build_selected_portfolio_current_weight_inputs(
            self._selected_row(),
            component_inputs={"candidate-selected": {"current_value": 10_000.0}},
            cash_value=0.0,
            input_mode="current_value",
        )
        drift_check = build_selected_portfolio_drift_check(
            self._selected_row(),
            current_weights=weight_inputs["current_weights"],
        )
        alert_preview = build_selected_portfolio_drift_alert_preview(
            self._selected_row(),
            drift_check=drift_check,
        )
        boundary = build_selected_portfolio_allocation_drift_boundary(
            self._selected_row(),
            weight_inputs=weight_inputs,
            drift_check=drift_check,
            alert_preview=alert_preview,
            input_mode="current_value",
        )

        self.assertEqual(boundary["schema_version"], SELECTED_ALLOCATION_DRIFT_BOUNDARY_SCHEMA_VERSION)
        self.assertEqual(boundary["route"], "ALLOCATION_DRIFT_BOUNDARY_READY")
        self.assertEqual(boundary["metrics"]["boundary_violation_count"], 0)
        rows = {row["Check"]: row for row in boundary["rows"]}
        self.assertEqual(rows["Current weight input source"]["Status"], "PASS")
        self.assertEqual(rows["Drift evidence"]["Status"], "PASS")
        self.assertEqual(rows["Alert preview evidence"]["Status"], "PASS")
        for contract in (weight_inputs, drift_check, alert_preview, boundary):
            execution_boundary = dict(contract.get("execution_boundary") or {})
            self.assertFalse(execution_boundary["db_write"])
            self.assertFalse(execution_boundary["registry_write"])
            self.assertFalse(execution_boundary["monitoring_log_auto_write"])
            self.assertFalse(execution_boundary["input_persistence"])
            self.assertFalse(execution_boundary["alert_persistence"])
            self.assertFalse(execution_boundary["account_connection"])
            self.assertFalse(execution_boundary["broker_sync"])
            self.assertFalse(execution_boundary["live_approval"])
            self.assertFalse(execution_boundary["order_instruction"])
            self.assertFalse(execution_boundary["auto_rebalance"])

    def test_allocation_drift_boundary_surfaces_breach_without_rebalance_action(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import (
            build_selected_portfolio_allocation_drift_boundary,
            build_selected_portfolio_drift_alert_preview,
            build_selected_portfolio_drift_check,
        )

        row = self._selected_row()
        row["raw_decision"]["selected_components"] = [
            {
                "title": "Selected Component A",
                "registry_id": "candidate-a",
                "target_weight": 50.0,
                "benchmark": "SPY",
                "period_start": "2020-01-01",
                "period_end": "2024-12-31",
            },
            {
                "title": "Selected Component B",
                "registry_id": "candidate-b",
                "target_weight": 50.0,
                "benchmark": "QQQ",
                "period_start": "2020-01-01",
                "period_end": "2024-12-31",
            },
        ]
        drift_check = build_selected_portfolio_drift_check(
            row,
            current_weights={"candidate-a": 60.0, "candidate-b": 40.0},
        )
        alert_preview = build_selected_portfolio_drift_alert_preview(row, drift_check=drift_check)
        boundary = build_selected_portfolio_allocation_drift_boundary(
            row,
            drift_check=drift_check,
            alert_preview=alert_preview,
            input_mode="current_weight",
        )

        self.assertEqual(drift_check["route"], "REBALANCE_NEEDED")
        self.assertEqual(boundary["route"], "ALLOCATION_DRIFT_BOUNDARY_BREACHED")
        rows = {row["Check"]: row for row in boundary["rows"]}
        self.assertEqual(rows["Drift evidence"]["Status"], "BREACHED")
        self.assertEqual(rows["Alert preview evidence"]["Status"], "BREACHED")
        self.assertFalse(boundary["execution_boundary"]["order_instruction"])
        self.assertFalse(boundary["execution_boundary"]["auto_rebalance"])
        self.assertFalse(boundary["execution_boundary"]["account_connection"])
        self.assertFalse(boundary["execution_boundary"]["broker_sync"])

    def test_selected_continuity_check_requires_recheck_input_without_writing(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_continuity_check

        continuity = build_selected_portfolio_continuity_check(self._selected_row())

        self.assertEqual(continuity["schema_version"], "selected_continuity_check_v1")
        self.assertEqual(continuity["route"], "CONTINUITY_NEEDS_INPUT")
        checks = {row["Check"]: row for row in continuity["checks"]}
        self.assertEqual(checks["Selected Final Review row"]["Status"], "PASS")
        self.assertEqual(checks["Decision source consistency"]["Status"], "PASS")
        self.assertEqual(checks["Component target contract"]["Status"], "PASS")
        self.assertEqual(checks["Performance Recheck input"]["Status"], "NEEDS_INPUT")
        self.assertTrue(continuity["metrics"]["source_contract_consistent"])
        self.assertEqual(continuity["source_contract"]["decision_id"], "decision-selected")
        self.assertFalse(continuity["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(continuity["execution_boundary"]["registry_write"])
        self.assertFalse(continuity["execution_boundary"]["live_approval"])

    def test_selected_continuity_check_blocks_mismatched_timeline_source_contract(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import (
            build_selected_portfolio_continuity_check,
            build_selected_portfolio_monitoring_timeline,
        )

        timeline = build_selected_portfolio_monitoring_timeline(self._selected_row())
        timeline["source_contract"]["decision_id"] = "different-decision"

        continuity = build_selected_portfolio_continuity_check(
            self._selected_row(),
            monitoring_timeline=timeline,
        )

        self.assertEqual(continuity["route"], "CONTINUITY_BLOCKED")
        checks = {row["Check"]: row for row in continuity["checks"]}
        self.assertEqual(checks["Decision source consistency"]["Status"], "BLOCKED")
        self.assertFalse(continuity["metrics"]["source_contract_consistent"])
        self.assertFalse(continuity["execution_boundary"]["registry_write"])

    def test_selected_continuity_check_blocks_non_selected_or_invalid_component_contract(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_continuity_check

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
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_comparison

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
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_comparison

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
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_comparison

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

    def test_review_signal_policy_ready_uses_recheck_comparison_rows(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_review_signal_policy

        policy = build_selected_portfolio_review_signal_policy(
            self._selected_row(),
            recheck_result=self._ready_recheck_result(),
            recheck_preflight=self._ready_recheck_preflight(),
            provider_evidence=self._ready_provider_evidence(),
        )

        self.assertEqual(policy["schema_version"], "selected_review_signal_policy_v1")
        self.assertEqual(policy["route"], "REVIEW_SIGNAL_CLEAR")
        self.assertEqual(policy["overall_status"], "CLEAR")
        rows = {row["Trigger"]: row for row in policy["rows"]}
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "CLEAR")
        self.assertEqual(rows["CAGR vs selected baseline"]["Policy Owner"], "Recheck Comparison")
        self.assertEqual(rows["MDD vs selected baseline"]["Policy Owner"], "Recheck Comparison")
        self.assertEqual(rows["Benchmark spread"]["Policy Owner"], "Recheck Comparison")
        self.assertFalse(policy["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(policy["execution_boundary"]["report_auto_write"])
        self.assertFalse(policy["execution_boundary"]["order_instruction"])
        self.assertEqual(policy["source_contract"]["decision_id"], "decision-selected")
        self.assertEqual(
            policy["source_contract"]["session_evidence_sources"],
            ["session_state.performance_recheck"],
        )

    def test_review_signal_policy_keeps_missing_recheck_and_data_gaps_out_of_clear(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_review_signal_policy

        policy = build_selected_portfolio_review_signal_policy(
            self._selected_row(),
            recheck_preflight=self._needs_data_recheck_preflight(),
            provider_evidence=self._needs_data_provider_evidence(),
        )

        self.assertEqual(policy["route"], "REVIEW_SIGNAL_NEEDS_INPUT")
        self.assertEqual(policy["overall_status"], "NEEDS_INPUT")
        rows = {row["Trigger"]: row for row in policy["rows"]}
        self.assertEqual(rows["Recheck operations preflight"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["Provider evidence freshness / coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["Performance Recheck input"]["Status"], "NEEDS_INPUT")
        self.assertGreaterEqual(policy["metrics"]["needs_input_count"], 3)
        self.assertFalse(policy["execution_boundary"]["registry_write"])

    def test_review_signal_policy_surfaces_comparison_breach(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_review_signal_policy

        breached_result = self._ready_recheck_result()
        breached_result["verdict_route"] = "PERFORMANCE_WEAKENED"
        breached_result["portfolio_summary"] = {"cagr": 0.04, "mdd": -0.22}
        breached_result["benchmark_summary"] = {"cagr": 0.06}
        breached_result["change_summary"] = {
            "cagr_delta_vs_baseline": -0.06,
            "mdd_delta_vs_baseline": -0.08,
            "benchmark_cagr": 0.06,
            "net_cagr_spread": -0.02,
        }

        policy = build_selected_portfolio_review_signal_policy(
            self._selected_row(),
            recheck_result=breached_result,
            recheck_preflight=self._ready_recheck_preflight(),
            provider_evidence=self._ready_provider_evidence(),
        )

        self.assertEqual(policy["route"], "REVIEW_SIGNAL_BREACHED")
        self.assertEqual(policy["overall_status"], "BREACHED")
        self.assertEqual(policy["recheck_comparison"]["route"], "RECHECK_COMPARISON_BREACHED")
        rows = {row["Trigger"]: row for row in policy["rows"]}
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "BREACHED")
        self.assertEqual(rows["Benchmark spread"]["Policy Owner"], "Recheck Comparison")
        self.assertFalse(policy["execution_boundary"]["auto_rebalance"])

    def test_recheck_readiness_blocks_missing_replay_contract_without_writing(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_readiness

        readiness = build_selected_portfolio_recheck_readiness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={},
        )

        self.assertEqual(readiness["schema_version"], "selected_recheck_readiness_v1")
        self.assertEqual(readiness["route"], "RECHECK_READINESS_BLOCKED")
        rows = {row["Check"]: row for row in readiness["rows"]}
        self.assertEqual(rows["Selected component contract"]["Status"], "PASS")
        self.assertEqual(rows["Selected replay contract"]["Status"], "BLOCKED")
        self.assertFalse(readiness["execution_boundary"]["db_write"])
        self.assertFalse(readiness["execution_boundary"]["registry_write"])
        self.assertFalse(readiness["execution_boundary"]["monitoring_log_auto_write"])

    def test_recheck_readiness_ready_when_db_latest_and_replay_contract_exist(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_readiness

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

    def test_recheck_readiness_uses_embedded_final_decision_contract_without_registry(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_readiness

        row = self._selected_row()
        row["raw_decision"]["selected_components"][0]["strategy_key"] = "equal_weight"
        row["raw_decision"]["selected_components"][0]["replay_contract"] = {
            "settings_snapshot": {
                "tickers": ["SPY", "QQQ"],
                "benchmark_ticker": "SPY",
                "start": "2020-01-01",
                "end": "2024-12-31",
                "rebalance_interval": 12,
            }
        }

        readiness = build_selected_portfolio_recheck_readiness(
            row,
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={},
        )

        self.assertEqual(readiness["route"], "RECHECK_READINESS_READY")
        self.assertEqual(readiness["metrics"]["embedded_replay_contract_count"], 1)
        self.assertEqual(readiness["metrics"]["candidate_registry_fallback_count"], 0)
        rows = {row["Check"]: row for row in readiness["rows"]}
        self.assertEqual(rows["Selected replay contract"]["Status"], "PASS")

    def test_recheck_symbol_freshness_detects_missing_and_stale_without_writing(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_symbol_freshness

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
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_symbol_freshness

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

    def test_recheck_operations_preflight_ready_when_readiness_and_freshness_are_ready(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_operations_preflight

        preflight = build_selected_portfolio_recheck_operations_preflight(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id=self._candidate_rows_by_id(),
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                    {"symbol": "QQQ", "latest_date": "2026-05-27", "row_count": 999},
                ]
            ),
        )

        self.assertEqual(preflight["schema_version"], "selected_recheck_operations_preflight_v1")
        self.assertEqual(preflight["route"], "RECHECK_PREFLIGHT_READY")
        self.assertEqual(preflight["metrics"]["replay_contract_count"], 1)
        self.assertEqual(preflight["metrics"]["missing_symbol_count"], 0)
        self.assertEqual(preflight["metrics"]["stale_symbol_count"], 0)
        self.assertEqual(preflight["readiness"]["route"], "RECHECK_READINESS_READY")
        self.assertEqual(preflight["symbol_freshness"]["route"], "SYMBOL_FRESHNESS_READY")
        self.assertFalse(preflight["execution_boundary"]["db_write"])
        self.assertFalse(preflight["execution_boundary"]["registry_write"])
        self.assertFalse(preflight["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(preflight["execution_boundary"]["order_instruction"])
        self.assertFalse(preflight["execution_boundary"]["auto_rebalance"])

    def test_recheck_operations_preflight_routes_missing_price_to_needs_data(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_operations_preflight

        preflight = build_selected_portfolio_recheck_operations_preflight(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id=self._candidate_rows_by_id(),
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                ]
            ),
        )

        self.assertEqual(preflight["route"], "RECHECK_PREFLIGHT_NEEDS_DATA")
        self.assertEqual(preflight["symbol_freshness"]["route"], "SYMBOL_FRESHNESS_MISSING")
        self.assertEqual(preflight["metrics"]["missing_symbol_count"], 1)
        rows = {row["Area"]: row for row in preflight["rows"]}
        self.assertEqual(rows["Symbol Freshness"]["Status"], "NEEDS_INPUT")

    def test_recheck_operations_preflight_blocks_missing_replay_contract(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_recheck_operations_preflight

        preflight = build_selected_portfolio_recheck_operations_preflight(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={},
            freshness_df=pd.DataFrame(),
        )

        self.assertEqual(preflight["route"], "RECHECK_PREFLIGHT_BLOCKED")
        self.assertEqual(preflight["readiness"]["route"], "RECHECK_READINESS_BLOCKED")
        self.assertEqual(preflight["symbol_freshness"]["route"], "SYMBOL_FRESHNESS_BLOCKED")
        rows = {row["Area"]: row for row in preflight["rows"]}
        self.assertEqual(rows["Recheck Readiness"]["Status"], "BLOCKED")
        self.assertEqual(rows["Symbol Freshness"]["Status"], "BLOCKED")

    def test_open_issue_followup_surfaces_final_review_open_items(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_open_issue_followup

        followup = build_selected_portfolio_open_issue_followup(self._selected_row_with_open_issue())

        self.assertEqual(followup["schema_version"], "selected_open_issue_followup_v1")
        self.assertEqual(followup["route"], "OPEN_ISSUES_PRESENT")
        self.assertEqual(followup["metrics"]["open_review_item_count"], 1)
        self.assertEqual(followup["metrics"]["review_trigger_count"], 1)
        rows = {row["Area"]: row for row in followup["rows"]}
        self.assertEqual(rows["Provider / Look-through"]["Status"], "REVIEW")
        self.assertIn("Provider holdings", rows["Provider / Look-through"]["Next Action"])
        self.assertFalse(followup["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(followup["execution_boundary"]["live_approval"])

    def test_deployment_readiness_preflight_is_read_only_and_keeps_review_open(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_deployment_readiness_preflight

        preflight = build_selected_portfolio_deployment_readiness_preflight(
            self._selected_row_with_open_issue(),
            recheck_preflight=self._ready_recheck_preflight(),
            provider_evidence={
                "schema_version": "selected_provider_evidence_v1",
                "route": "SELECTED_PROVIDER_READY",
                "route_label": "Provider 근거 준비 완료",
                "conclusion": "provider ready",
            },
            continuity_check={
                "schema_version": "selected_continuity_check_v1",
                "route": "CONTINUITY_READY",
                "route_label": "사후 점검 준비 완료",
                "next_action": "continue monitoring",
            },
            review_signal_policy={
                "schema_version": "selected_review_signal_policy_v1",
                "route": "REVIEW_SIGNAL_CLEAR",
                "route_label": "운영 신호 정상",
                "conclusion": "signals clear",
            },
            allocation_boundary={
                "schema_version": "selected_allocation_drift_evidence_boundary_v1",
                "route": "ALLOCATION_DRIFT_BOUNDARY_OPTIONAL",
                "route_label": "비중 근거 선택 점검",
                "conclusion": "allocation optional",
            },
        )

        self.assertEqual(preflight["schema_version"], "selected_deployment_readiness_preflight_v1")
        self.assertEqual(preflight["route"], "DEPLOYMENT_READINESS_REVIEW")
        self.assertEqual(preflight["metrics"]["review_count"], 3)
        rows = {row["Area"]: row for row in preflight["rows"]}
        self.assertEqual(rows["Deployment Gate Policy"]["Status"], "REVIEW")
        self.assertEqual(rows["Policy: Provider / Look-through"]["Status"], "REVIEW")
        self.assertEqual(rows["Open Issues / Follow-up"]["Status"], "REVIEW")
        self.assertFalse(preflight["execution_boundary"]["live_approval"])
        self.assertFalse(preflight["execution_boundary"]["order_instruction"])
        self.assertFalse(preflight["execution_boundary"]["auto_rebalance"])

    def test_selected_provider_evidence_ready_from_injected_provider_context(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_provider_evidence

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
        self.assertEqual(
            evidence["staleness_contract"]["schema_version"],
            "selected_provider_evidence_staleness_contract_v1",
        )
        self.assertEqual(evidence["metrics"]["provider_symbol_count"], 2)
        self.assertEqual(evidence["metrics"]["needs_input_count"], 0)
        self.assertEqual(evidence["metrics"]["stale_count"], 0)
        self.assertEqual(evidence["metrics"]["partial_coverage_count"], 0)
        self.assertEqual(evidence["symbol_weights"], {"QQQ": 50.0, "SPY": 50.0})
        self.assertFalse(evidence["execution_boundary"]["db_write"])
        self.assertFalse(evidence["execution_boundary"]["provider_collection"])
        self.assertFalse(evidence["execution_boundary"]["monitoring_log_auto_write"])

    def test_selected_provider_evidence_surfaces_not_run_without_writing(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_provider_evidence

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
        self.assertEqual(evidence["metrics"]["needs_input_count"], 2)
        self.assertEqual(evidence["metrics"]["review_count"], 1)
        self.assertEqual(evidence["metrics"]["stale_count"], 1)
        self.assertEqual(evidence["metrics"]["partial_coverage_count"], 1)
        self.assertGreaterEqual(evidence["metrics"]["missing_coverage_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["ETF Exposure"]["Status"], "REVIEW")
        self.assertEqual(rows["Look-through Coverage"]["Status"], "NEEDS_INPUT")
        self.assertFalse(evidence["execution_boundary"]["registry_write"])
        self.assertFalse(evidence["execution_boundary"]["order_instruction"])

    def test_selected_provider_evidence_marks_component_fallback_as_review(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_provider_evidence

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
                    }
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_REVIEW")
        self.assertEqual(evidence["symbol_weights"], {"QQQ": 50.0, "SPY": 50.0})
        self.assertEqual(evidence["metrics"]["fallback_contract_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["Selected Symbol Contract"]["Status"], "REVIEW")
        self.assertFalse(evidence["execution_boundary"]["monitoring_log_auto_write"])

    def test_selected_provider_evidence_downgrades_stale_actual_pass_to_review(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_provider_evidence

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
                        "Freshness": "stale",
                        "As Of Range": "2026-03-01 -> 2026-03-01",
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
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_REVIEW")
        self.assertEqual(evidence["metrics"]["stale_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "REVIEW")
        self.assertIn("freshness=stale", rows["ETF Holdings"]["Policy Reason"])

    def test_selected_provider_evidence_downgrades_partial_pass_to_review(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_provider_evidence

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
                        "Coverage": "partial",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 75.0,
                        "Source Mix": "official: 75.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF holdings snapshot covers 75.0% of target weight.",
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
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 75.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_REVIEW")
        self.assertGreaterEqual(evidence["metrics"]["partial_coverage_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "REVIEW")
        self.assertEqual(rows["Look-through Coverage"]["Status"], "REVIEW")

    def test_selected_provider_evidence_requires_core_provider_areas(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_provider_evidence

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
                    }
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_NEEDS_DATA")
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["ETF Exposure"]["Status"], "NEEDS_INPUT")
        self.assertIn("required_provider_area_missing", rows["ETF Holdings"]["Policy Reason"])


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
        self.assertFalse(dossier["execution_boundary"]["db_write"])
        self.assertFalse(dossier["execution_boundary"]["registry_write"])
        self.assertFalse(dossier["execution_boundary"]["report_auto_write"])
        self.assertFalse(dossier["execution_boundary"]["live_approval"])
        self.assertEqual(dossier["source_contract"]["schema_version"], "selected_decision_source_consistency_v1")
        self.assertEqual(dossier["source_contract"]["source_identity"], "practical_validation_result:source-dossier")
        self.assertTrue(dossier["metrics"]["source_contract_consistent"])
        self.assertIn("# Final Decision Dossier", dossier["markdown"])
        self.assertIn("## Source Contract", dossier["markdown"])
        self.assertIn("decision-dossier", dossier["filename"])
        self.assertIn("not live approval", dossier["markdown"])

    def test_decision_dossier_can_include_selected_monitoring_timeline(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_monitoring_timeline
        from app.services.backtest_evidence_read_model import build_decision_dossier

        selected_row = {"raw_decision": self._final_decision_row()}
        timeline = build_selected_portfolio_monitoring_timeline(
            selected_row,
            recheck_result={
                "status": "ok",
                "verdict_route": "SELECTION_THESIS_HOLDS",
                "verdict": "선정 근거가 유지됩니다.",
                "period": {"start": "2026-01-01", "end": "2026-05-28"},
                "change_summary": {"cagr_delta_vs_baseline": 0.01},
            },
        )

        dossier = build_decision_dossier(
            selected_row,
            monitoring_timeline=timeline,
        )

        self.assertTrue(dossier["monitoring_timeline"]["present"])
        self.assertTrue(dossier["metrics"]["monitoring_timeline_present"])
        self.assertTrue(dossier["source_contract"]["timeline_contract_present"])
        self.assertTrue(dossier["source_contract"]["timeline_contract_consistent"])
        self.assertEqual(
            dossier["source_contract"]["session_evidence_sources"],
            ["session_state.performance_recheck"],
        )
        self.assertIn("Performance Recheck", dossier["markdown"])
        self.assertFalse(dossier["execution_boundary"]["monitoring_log_auto_write"])

    def test_decision_dossier_surfaces_mismatched_timeline_source_contract(self) -> None:
        from app.runtime.backtest.read_models.final_selected_portfolios import build_selected_portfolio_monitoring_timeline
        from app.services.backtest_evidence_read_model import build_decision_dossier

        selected_row = {"raw_decision": self._final_decision_row()}
        timeline = build_selected_portfolio_monitoring_timeline(selected_row)
        timeline["source_contract"]["source_id"] = "different-source"

        dossier = build_decision_dossier(
            selected_row,
            monitoring_timeline=timeline,
        )

        self.assertTrue(dossier["source_contract"]["timeline_contract_present"])
        self.assertFalse(dossier["source_contract"]["timeline_contract_consistent"])
        self.assertFalse(dossier["metrics"]["source_contract_consistent"])
        self.assertIn("Timeline Contract Consistent: `False`", dossier["markdown"])


if __name__ == "__main__":
    unittest.main()
