from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.runtime.backtest import (
    BacktestDataError,
    BacktestInputError,
    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    STRICT_DEFAULT_BENCHMARK_CONTRACT,
    STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    run_dual_momentum_backtest_from_db,
    run_equal_weight_backtest_from_db,
    run_global_relative_strength_backtest_from_db,
    run_gtaa_backtest_from_db,
    run_quality_snapshot_backtest_from_db,
    run_quality_snapshot_strict_annual_backtest_from_db,
    run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_quality_value_snapshot_strict_annual_backtest_from_db,
    run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
    run_risk_parity_trend_backtest_from_db,
    run_risk_on_momentum_5d_backtest_from_db,
    run_value_snapshot_strict_annual_backtest_from_db,
    run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
)
from app.runtime.backtest.runner_catalog import require_runner_definition
from finance.sample import (
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    STATIC_MANAGED_RESEARCH_UNIVERSE,
    STRICT_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_RISK_OFF_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_ENABLED,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    STRICT_TREND_FILTER_DEFAULT_ENABLED,
    STRICT_TREND_FILTER_DEFAULT_WINDOW,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
)


@dataclass(frozen=True)
class BacktestExecutionResult:
    ok: bool
    bundle: dict[str, Any] | None = None
    error_kind: str | None = None
    error_message: str | None = None
    elapsed_seconds: float = 0.0


def _payload_or_default(payload: Mapping[str, Any], key: str, default: Any) -> Any:
    value = payload.get(key)
    return default if value is None else value


def _dynamic_etf_promotion_policy_kwargs(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "promotion_min_benchmark_coverage": _payload_or_default(
            payload,
            "promotion_min_benchmark_coverage",
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
        ),
        "promotion_min_net_cagr_spread": _payload_or_default(
            payload,
            "promotion_min_net_cagr_spread",
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        ),
        "promotion_min_liquidity_clean_coverage": _payload_or_default(
            payload,
            "promotion_min_liquidity_clean_coverage",
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        ),
        "promotion_max_underperformance_share": _payload_or_default(
            payload,
            "promotion_max_underperformance_share",
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        ),
        "promotion_min_worst_rolling_excess_return": _payload_or_default(
            payload,
            "promotion_min_worst_rolling_excess_return",
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        ),
        "promotion_max_strategy_drawdown": _payload_or_default(
            payload,
            "promotion_max_strategy_drawdown",
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
        ),
        "promotion_max_drawdown_gap_vs_benchmark": _payload_or_default(
            payload,
            "promotion_max_drawdown_gap_vs_benchmark",
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        ),
    }


def _strict_factor_contract_kwargs(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "min_price_filter": _payload_or_default(payload, "min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
        "min_history_months_filter": _payload_or_default(
            payload,
            "min_history_months_filter",
            STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
        ),
        "min_avg_dollar_volume_20d_m_filter": _payload_or_default(
            payload,
            "min_avg_dollar_volume_20d_m_filter",
            STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
        ),
        "transaction_cost_bps": _payload_or_default(
            payload,
            "transaction_cost_bps",
            ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
        ),
        "benchmark_contract": _payload_or_default(
            payload,
            "benchmark_contract",
            STRICT_DEFAULT_BENCHMARK_CONTRACT,
        ),
        "benchmark_ticker": _payload_or_default(
            payload,
            "benchmark_ticker",
            ETF_REAL_MONEY_DEFAULT_BENCHMARK,
        ),
        "guardrail_reference_ticker": _payload_or_default(
            payload,
            "guardrail_reference_ticker",
            payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
        ),
        **_dynamic_etf_promotion_policy_kwargs(payload),
        "underperformance_guardrail_enabled": _payload_or_default(
            payload,
            "underperformance_guardrail_enabled",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
        ),
        "underperformance_guardrail_window_months": _payload_or_default(
            payload,
            "underperformance_guardrail_window_months",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        ),
        "underperformance_guardrail_threshold": _payload_or_default(
            payload,
            "underperformance_guardrail_threshold",
            STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
        ),
        "drawdown_guardrail_enabled": _payload_or_default(
            payload,
            "drawdown_guardrail_enabled",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
        ),
        "drawdown_guardrail_window_months": _payload_or_default(
            payload,
            "drawdown_guardrail_window_months",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        ),
        "drawdown_guardrail_strategy_threshold": _payload_or_default(
            payload,
            "drawdown_guardrail_strategy_threshold",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
        ),
        "drawdown_guardrail_gap_threshold": _payload_or_default(
            payload,
            "drawdown_guardrail_gap_threshold",
            STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
        ),
    }


def execute_single_backtest(
    payload: Mapping[str, Any],
    *,
    strategy_name: str,
) -> BacktestExecutionResult:
    """Run a single-strategy DB backtest without depending on Streamlit UI state."""

    started_at = time.perf_counter()
    try:
        runner_definition = require_runner_definition(payload.get("strategy_key"))
        bundle = _dispatch_single_backtest(payload)
    except BacktestInputError as exc:
        return BacktestExecutionResult(
            ok=False,
            error_kind="input",
            error_message=f"Backtest input issue: {exc}",
        )
    except KeyError as exc:
        return BacktestExecutionResult(
            ok=False,
            error_kind="input",
            error_message=f"Backtest input issue: {exc}",
        )
    except BacktestDataError as exc:
        return BacktestExecutionResult(
            ok=False,
            error_kind="data",
            error_message=f"Backtest data issue: {exc}",
        )
    except Exception as exc:
        return BacktestExecutionResult(
            ok=False,
            error_kind="system",
            error_message=f"Backtest execution failed: {exc}",
        )

    elapsed_seconds = time.perf_counter() - started_at
    normalized_bundle = dict(bundle)
    meta = dict(normalized_bundle.get("meta") or {})
    meta["ui_elapsed_seconds"] = round(elapsed_seconds, 3)
    meta["runner_catalog_key"] = runner_definition.strategy_key
    meta["runner_runtime_module"] = runner_definition.runtime_module
    meta["runner_runtime_family"] = runner_definition.runtime_family
    normalized_bundle["meta"] = meta

    return BacktestExecutionResult(
        ok=True,
        bundle=normalized_bundle,
        elapsed_seconds=elapsed_seconds,
    )


def _dispatch_single_backtest(payload: Mapping[str, Any]) -> dict[str, Any]:
    strategy_key = payload["strategy_key"]

    if strategy_key == "risk_on_momentum_5d":
        return run_risk_on_momentum_5d_backtest_from_db(
            tickers=payload.get("tickers"),
            start=payload.get("start"),
            end=payload.get("end"),
            timeframe=payload.get("timeframe") or "1d",
            option=payload.get("option") or "close_based",
            universe_mode=payload.get("universe_mode") or "top1000",
            preset_name=payload.get("preset_name"),
            universe_limit=payload.get("universe_limit"),
            start_balance=payload.get("start_balance", 10_000.0),
            execution_mode=payload.get("execution_mode", "close_based"),
            exit_mode=payload.get("exit_mode", "fixed_pct"),
            max_holding_days=payload.get("max_holding_days", 5),
            stop_loss_pct=payload.get("stop_loss_pct", -2.5),
            take_profit_pct=payload.get("take_profit_pct", 5.0),
            atr_period=payload.get("atr_period", 14),
            stop_atr_multiple=payload.get("stop_atr_multiple", 1.0),
            take_profit_atr_multiple=payload.get("take_profit_atr_multiple", 2.0),
            max_new_positions_per_day=payload.get("max_new_positions_per_day", 3),
            max_total_positions=payload.get("max_total_positions", 3),
            transaction_cost_bps=payload.get("transaction_cost_bps", 0.0),
            slippage_bps=payload.get("slippage_bps", 0.0),
            macro_filter_enabled=payload.get("macro_filter_enabled", True),
            macro_filter_mode=payload.get("macro_filter_mode", "hard_filter"),
            risk_on_min=payload.get("risk_on_min", 0.0),
            rate_pressure_max=payload.get("rate_pressure_max", 1.0),
            dollar_pressure_max=payload.get("dollar_pressure_max", 1.0),
            safe_haven_max=payload.get("safe_haven_max", 1.0),
            rate_pressure_penalty_weight=payload.get("rate_pressure_penalty_weight", 10.0),
            dollar_pressure_penalty_weight=payload.get("dollar_pressure_penalty_weight", 10.0),
            safe_haven_penalty_weight=payload.get("safe_haven_penalty_weight", 10.0),
            min_price=payload.get("min_price", 5.0),
            min_avg_dollar_volume_20d=payload.get("min_avg_dollar_volume_20d", 20_000_000.0),
            min_avg_volume_20d=payload.get("min_avg_volume_20d", 500_000.0),
            random_iterations=payload.get("random_iterations", 50),
            random_seed=payload.get("random_seed", 42),
            scanner_top_n_per_day=payload.get("scanner_top_n_per_day", 50),
            run_comparison_suite=payload.get("run_comparison_suite", True),
            run_sensitivity_suite=payload.get("run_sensitivity_suite", False),
        )

    if strategy_key == "equal_weight":
        return run_equal_weight_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            rebalance_interval=payload["rebalance_interval"],
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            guardrail_reference_ticker=payload.get("guardrail_reference_ticker"),
            promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            promotion_max_bid_ask_spread_pct=payload.get(
                "promotion_max_bid_ask_spread_pct",
                ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
            ),
            promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage"),
            promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread"),
            promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage"),
            promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share"),
            promotion_min_worst_rolling_excess_return=payload.get("promotion_min_worst_rolling_excess_return"),
            promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown"),
            promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark"),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
        )
    if strategy_key == "gtaa":
        return run_gtaa_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            top=payload["top"],
            interval=payload["interval"],
            score_lookback_months=payload.get("score_lookback_months"),
            score_return_columns=payload.get("score_return_columns"),
            score_weights=payload.get("score_weights"),
            trend_filter_window=payload.get("trend_filter_window", GTAA_DEFAULT_TREND_FILTER_WINDOW),
            risk_off_mode=payload.get("risk_off_mode", GTAA_DEFAULT_RISK_OFF_MODE),
            defensive_tickers=payload.get("defensive_tickers", GTAA_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=payload.get("market_regime_enabled", False),
            market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
            crash_guardrail_enabled=payload.get("crash_guardrail_enabled", GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED),
            crash_guardrail_drawdown_threshold=payload.get(
                "crash_guardrail_drawdown_threshold",
                GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
            ),
            crash_guardrail_lookback_months=payload.get(
                "crash_guardrail_lookback_months",
                GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
            ),
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            min_avg_dollar_volume_20d_m_filter=payload.get(
                "min_avg_dollar_volume_20d_m_filter",
                STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
            ),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            underperformance_guardrail_enabled=payload.get(
                "underperformance_guardrail_enabled",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=payload.get(
                "underperformance_guardrail_window_months",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=payload.get(
                "underperformance_guardrail_threshold",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=payload.get(
                "drawdown_guardrail_enabled",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=payload.get(
                "drawdown_guardrail_window_months",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=payload.get(
                "drawdown_guardrail_strategy_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=payload.get(
                "drawdown_guardrail_gap_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
            promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            promotion_max_bid_ask_spread_pct=payload.get(
                "promotion_max_bid_ask_spread_pct",
                ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
            ),
            **_dynamic_etf_promotion_policy_kwargs(payload),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
        )
    if strategy_key == "global_relative_strength":
        return run_global_relative_strength_backtest_from_db(
            tickers=payload["tickers"],
            cash_ticker=payload.get("cash_ticker", GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER),
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            top=payload.get("top", GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP),
            interval=payload.get("interval", GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL),
            score_lookback_months=payload.get("score_lookback_months"),
            score_return_columns=payload.get("score_return_columns"),
            score_weights=payload.get("score_weights"),
            trend_filter_window=payload.get(
                "trend_filter_window",
                GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
            ),
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            promotion_max_bid_ask_spread_pct=payload.get(
                "promotion_max_bid_ask_spread_pct",
                ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
            ),
            **_dynamic_etf_promotion_policy_kwargs(payload),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
        )
    if strategy_key == "risk_parity_trend":
        return run_risk_parity_trend_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            rebalance_interval=payload.get("rebalance_interval", 1),
            vol_window=payload.get("vol_window", 6),
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            underperformance_guardrail_enabled=payload.get(
                "underperformance_guardrail_enabled",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=payload.get(
                "underperformance_guardrail_window_months",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=payload.get(
                "underperformance_guardrail_threshold",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=payload.get(
                "drawdown_guardrail_enabled",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=payload.get(
                "drawdown_guardrail_window_months",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=payload.get(
                "drawdown_guardrail_strategy_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=payload.get(
                "drawdown_guardrail_gap_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
            promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            promotion_max_bid_ask_spread_pct=payload.get(
                "promotion_max_bid_ask_spread_pct",
                ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
            ),
            **_dynamic_etf_promotion_policy_kwargs(payload),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
        )
    if strategy_key == "dual_momentum":
        return run_dual_momentum_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            top=payload.get("top", 1),
            rebalance_interval=payload.get("rebalance_interval", 1),
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            underperformance_guardrail_enabled=payload.get(
                "underperformance_guardrail_enabled",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=payload.get(
                "underperformance_guardrail_window_months",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=payload.get(
                "underperformance_guardrail_threshold",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=payload.get(
                "drawdown_guardrail_enabled",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=payload.get(
                "drawdown_guardrail_window_months",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=payload.get(
                "drawdown_guardrail_strategy_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=payload.get(
                "drawdown_guardrail_gap_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
            promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
            promotion_max_bid_ask_spread_pct=payload.get(
                "promotion_max_bid_ask_spread_pct",
                ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
            ),
            **_dynamic_etf_promotion_policy_kwargs(payload),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
        )
    if strategy_key == "quality_snapshot":
        return run_quality_snapshot_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            factor_freq=payload["factor_freq"],
            rebalance_freq=payload["rebalance_freq"],
            quality_factors=payload["quality_factors"],
            top_n=payload["top"],
            snapshot_mode=payload["snapshot_mode"],
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
        )
    if strategy_key == "quality_snapshot_strict_annual":
        return run_quality_snapshot_strict_annual_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            quality_factors=payload["quality_factors"],
            top_n=payload["top"],
            rebalance_interval=payload.get("rebalance_interval", 1),
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            min_history_months_filter=payload.get(
                "min_history_months_filter",
                STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
            ),
            min_avg_dollar_volume_20d_m_filter=payload.get(
                "min_avg_dollar_volume_20d_m_filter",
                STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
            ),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            guardrail_reference_ticker=payload.get(
                "guardrail_reference_ticker",
                payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            ),
            promotion_min_benchmark_coverage=payload.get(
                "promotion_min_benchmark_coverage",
                STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
            ),
            promotion_min_net_cagr_spread=payload.get(
                "promotion_min_net_cagr_spread",
                STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
            ),
            promotion_min_liquidity_clean_coverage=payload.get(
                "promotion_min_liquidity_clean_coverage",
                STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
            ),
            promotion_max_underperformance_share=payload.get(
                "promotion_max_underperformance_share",
                STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
            ),
            promotion_min_worst_rolling_excess_return=payload.get(
                "promotion_min_worst_rolling_excess_return",
                STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
            ),
            promotion_max_strategy_drawdown=payload.get(
                "promotion_max_strategy_drawdown",
                STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
            ),
            promotion_max_drawdown_gap_vs_benchmark=payload.get(
                "promotion_max_drawdown_gap_vs_benchmark",
                STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
            ),
            trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
            trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
            weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
            rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
            rejected_slot_fill_enabled=payload.get(
                "rejected_slot_fill_enabled",
                STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
            ),
            partial_cash_retention_enabled=payload.get(
                "partial_cash_retention_enabled",
                STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
            ),
            risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
            defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
            market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
            underperformance_guardrail_enabled=payload.get(
                "underperformance_guardrail_enabled",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=payload.get(
                "underperformance_guardrail_window_months",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=payload.get(
                "underperformance_guardrail_threshold",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=payload.get(
                "drawdown_guardrail_enabled",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=payload.get(
                "drawdown_guardrail_window_months",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=payload.get(
                "drawdown_guardrail_strategy_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=payload.get(
                "drawdown_guardrail_gap_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
            universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
            dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
            dynamic_target_size=payload.get("dynamic_target_size"),
        )
    if strategy_key == "quality_snapshot_strict_quarterly_prototype":
        return run_quality_snapshot_strict_quarterly_prototype_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            quality_factors=payload["quality_factors"],
            top_n=payload["top"],
            rebalance_interval=payload.get("rebalance_interval", 1),
            **_strict_factor_contract_kwargs(payload),
            trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
            trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
            weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
            rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
            rejected_slot_fill_enabled=payload.get(
                "rejected_slot_fill_enabled",
                STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
            ),
            partial_cash_retention_enabled=payload.get(
                "partial_cash_retention_enabled",
                STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
            ),
            risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
            defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
            market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
            universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
            dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
            dynamic_target_size=payload.get("dynamic_target_size"),
        )
    if strategy_key == "value_snapshot_strict_annual":
        return run_value_snapshot_strict_annual_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            value_factors=payload["value_factors"],
            top_n=payload["top"],
            rebalance_interval=payload.get("rebalance_interval", 1),
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            min_history_months_filter=payload.get(
                "min_history_months_filter",
                STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
            ),
            min_avg_dollar_volume_20d_m_filter=payload.get(
                "min_avg_dollar_volume_20d_m_filter",
                STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
            ),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            guardrail_reference_ticker=payload.get(
                "guardrail_reference_ticker",
                payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            ),
            promotion_min_benchmark_coverage=payload.get(
                "promotion_min_benchmark_coverage",
                STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
            ),
            promotion_min_net_cagr_spread=payload.get(
                "promotion_min_net_cagr_spread",
                STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
            ),
            promotion_min_liquidity_clean_coverage=payload.get(
                "promotion_min_liquidity_clean_coverage",
                STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
            ),
            promotion_max_underperformance_share=payload.get(
                "promotion_max_underperformance_share",
                STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
            ),
            promotion_min_worst_rolling_excess_return=payload.get(
                "promotion_min_worst_rolling_excess_return",
                STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
            ),
            promotion_max_strategy_drawdown=payload.get(
                "promotion_max_strategy_drawdown",
                STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
            ),
            promotion_max_drawdown_gap_vs_benchmark=payload.get(
                "promotion_max_drawdown_gap_vs_benchmark",
                STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
            ),
            trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
            trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
            weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
            rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
            rejected_slot_fill_enabled=payload.get(
                "rejected_slot_fill_enabled",
                STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
            ),
            partial_cash_retention_enabled=payload.get(
                "partial_cash_retention_enabled",
                STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
            ),
            risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
            defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
            market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
            underperformance_guardrail_enabled=payload.get(
                "underperformance_guardrail_enabled",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=payload.get(
                "underperformance_guardrail_window_months",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=payload.get(
                "underperformance_guardrail_threshold",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=payload.get(
                "drawdown_guardrail_enabled",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=payload.get(
                "drawdown_guardrail_window_months",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=payload.get(
                "drawdown_guardrail_strategy_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=payload.get(
                "drawdown_guardrail_gap_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
            universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
            dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
            dynamic_target_size=payload.get("dynamic_target_size"),
        )
    if strategy_key == "value_snapshot_strict_quarterly_prototype":
        return run_value_snapshot_strict_quarterly_prototype_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            value_factors=payload["value_factors"],
            top_n=payload["top"],
            rebalance_interval=payload.get("rebalance_interval", 1),
            **_strict_factor_contract_kwargs(payload),
            trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
            trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
            weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
            rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
            rejected_slot_fill_enabled=payload.get(
                "rejected_slot_fill_enabled",
                STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
            ),
            partial_cash_retention_enabled=payload.get(
                "partial_cash_retention_enabled",
                STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
            ),
            risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
            defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
            market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
            universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
            dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
            dynamic_target_size=payload.get("dynamic_target_size"),
        )
    if strategy_key == "quality_value_snapshot_strict_annual":
        return run_quality_value_snapshot_strict_annual_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            quality_factors=payload["quality_factors"],
            value_factors=payload["value_factors"],
            top_n=payload["top"],
            rebalance_interval=payload.get("rebalance_interval", 1),
            min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
            min_history_months_filter=payload.get(
                "min_history_months_filter",
                STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
            ),
            min_avg_dollar_volume_20d_m_filter=payload.get(
                "min_avg_dollar_volume_20d_m_filter",
                STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
            ),
            transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
            benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
            benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            guardrail_reference_ticker=payload.get(
                "guardrail_reference_ticker",
                payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
            ),
            promotion_min_benchmark_coverage=payload.get(
                "promotion_min_benchmark_coverage",
                STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
            ),
            promotion_min_net_cagr_spread=payload.get(
                "promotion_min_net_cagr_spread",
                STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
            ),
            promotion_min_liquidity_clean_coverage=payload.get(
                "promotion_min_liquidity_clean_coverage",
                STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
            ),
            promotion_max_underperformance_share=payload.get(
                "promotion_max_underperformance_share",
                STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
            ),
            promotion_min_worst_rolling_excess_return=payload.get(
                "promotion_min_worst_rolling_excess_return",
                STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
            ),
            promotion_max_strategy_drawdown=payload.get(
                "promotion_max_strategy_drawdown",
                STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
            ),
            promotion_max_drawdown_gap_vs_benchmark=payload.get(
                "promotion_max_drawdown_gap_vs_benchmark",
                STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
            ),
            trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
            trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
            weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
            rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
            rejected_slot_fill_enabled=payload.get(
                "rejected_slot_fill_enabled",
                STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
            ),
            partial_cash_retention_enabled=payload.get(
                "partial_cash_retention_enabled",
                STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
            ),
            risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
            defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
            market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
            underperformance_guardrail_enabled=payload.get(
                "underperformance_guardrail_enabled",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=payload.get(
                "underperformance_guardrail_window_months",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=payload.get(
                "underperformance_guardrail_threshold",
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=payload.get(
                "drawdown_guardrail_enabled",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=payload.get(
                "drawdown_guardrail_window_months",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=payload.get(
                "drawdown_guardrail_strategy_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=payload.get(
                "drawdown_guardrail_gap_threshold",
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
            universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
            dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
            dynamic_target_size=payload.get("dynamic_target_size"),
        )
    if strategy_key == "quality_value_snapshot_strict_quarterly_prototype":
        return run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db(
            tickers=payload["tickers"],
            start=payload["start"],
            end=payload["end"],
            timeframe=payload["timeframe"],
            option=payload["option"],
            quality_factors=payload["quality_factors"],
            value_factors=payload["value_factors"],
            top_n=payload["top"],
            rebalance_interval=payload.get("rebalance_interval", 1),
            **_strict_factor_contract_kwargs(payload),
            trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
            trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
            weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
            rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
            rejected_slot_fill_enabled=payload.get(
                "rejected_slot_fill_enabled",
                STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
            ),
            partial_cash_retention_enabled=payload.get(
                "partial_cash_retention_enabled",
                STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
            ),
            risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
            defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
            market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
            universe_mode=payload["universe_mode"],
            preset_name=payload["preset_name"],
            universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
            dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
            dynamic_target_size=payload.get("dynamic_target_size"),
        )

    raise BacktestInputError(f"Unsupported strategy key: {strategy_key}")


__all__ = ["BacktestExecutionResult", "execute_single_backtest"]
