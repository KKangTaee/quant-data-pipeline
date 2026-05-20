from __future__ import annotations

import inspect
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.runtime.backtest import (
    BacktestInputError,
    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
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
    run_value_snapshot_strict_annual_backtest_from_db,
    run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
)
from finance.sample import (
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS,
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_SCORE_WEIGHTS,
    GTAA_DEFAULT_SIGNAL_INTERVAL,
    GTAA_DEFAULT_TICKERS,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    GTAA_SCORE_RETURN_COLUMNS,
    QUALITY_STRICT_DEFAULT_FACTORS,
    STRICT_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_REJECTION_HANDLING_MODE,
    STRICT_DEFAULT_RISK_OFF_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    VALUE_STRICT_DEFAULT_FACTORS,
)


@dataclass(frozen=True)
class ComparePresetCatalog:
    equal_weight_presets: Mapping[str, list[str]]
    gtaa_presets: Mapping[str, list[str]]
    global_relative_strength_presets: Mapping[str, list[str]]
    quality_strict_presets: Mapping[str, list[str]]
    value_strict_presets: Mapping[str, list[str]]
    strict_annual_compare_default_preset: str
    strict_quarterly_prototype_default_preset: str


def run_compare_strategy(
    strategy_name: str,
    *,
    start: str,
    end: str,
    timeframe: str,
    option: str,
    overrides: Mapping[str, Any] | None = None,
    preset_catalog: ComparePresetCatalog,
) -> dict[str, Any]:
    config = _strategy_compare_defaults(strategy_name, preset_catalog=preset_catalog)
    runner = config["runner"]
    params = dict(config["extra"])
    if overrides:
        params.update(overrides)

    tickers = config["tickers"]
    preset_name = config["preset_name"]
    universe_mode = "preset"
    if strategy_name == "Equal Weight":
        universe_mode = params.pop("universe_mode", "preset")
        preset_name = params.pop("preset_name", preset_name)
        tickers = list(params.pop("tickers", tickers))
        if universe_mode == "preset" and preset_name in preset_catalog.equal_weight_presets:
            tickers = list(preset_catalog.equal_weight_presets[preset_name])
        else:
            universe_mode = "manual_tickers"
            preset_name = None
    elif strategy_name == "GTAA":
        universe_mode = params.pop("universe_mode", "preset")
        preset_name = params.pop("preset_name", preset_name)
        tickers = list(params.pop("tickers", tickers))
        if universe_mode == "preset" and preset_name in preset_catalog.gtaa_presets:
            tickers = list(preset_catalog.gtaa_presets[preset_name])
        else:
            universe_mode = "manual_tickers"
            preset_name = None
    elif strategy_name == "Global Relative Strength":
        universe_mode = params.pop("universe_mode", "preset")
        preset_name = params.pop("preset_name", preset_name)
        tickers = list(params.pop("tickers", tickers))
        if universe_mode == "preset" and preset_name in preset_catalog.global_relative_strength_presets:
            tickers = list(preset_catalog.global_relative_strength_presets[preset_name])
        else:
            universe_mode = "manual_tickers"
            preset_name = None
    elif strategy_name in {
        "Quality Snapshot (Strict Annual)",
        "Quality Snapshot (Strict Quarterly Prototype)",
        "Value Snapshot (Strict Annual)",
        "Value Snapshot (Strict Quarterly Prototype)",
        "Quality + Value Snapshot (Strict Annual)",
        "Quality + Value Snapshot (Strict Quarterly Prototype)",
    }:
        tickers, preset_name = _resolve_compare_strategy_universe(
            strategy_name,
            preset_name=params.pop("preset_name", preset_name),
            fallback_tickers=params.pop("tickers", tickers),
            preset_catalog=preset_catalog,
        )
        universe_mode = params.pop("universe_mode", "preset")

    runner_signature = inspect.signature(runner)
    if not any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in runner_signature.parameters.values()
    ):
        params = {
            key: value
            for key, value in params.items()
            if key in runner_signature.parameters
        }

    return runner(
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        universe_mode=universe_mode,
        preset_name=preset_name,
        **params,
    )


def _strategy_compare_defaults(
    strategy_name: str,
    *,
    preset_catalog: ComparePresetCatalog,
) -> dict[str, Any]:
    if strategy_name == "Equal Weight":
        return {
            "tickers": ["VIG", "SCHD", "DGRO", "GLD"],
            "preset_name": "Dividend ETFs",
            "runner": run_equal_weight_backtest_from_db,
            "extra": {
                "rebalance_interval": 12,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
            },
        }
    if strategy_name == "GTAA":
        return {
            "tickers": list(GTAA_DEFAULT_TICKERS),
            "preset_name": "GTAA Universe",
            "runner": run_gtaa_backtest_from_db,
            "extra": {
                "top": 3,
                "interval": GTAA_DEFAULT_SIGNAL_INTERVAL,
                "score_lookback_months": list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
                "score_return_columns": list(GTAA_SCORE_RETURN_COLUMNS),
                "score_weights": dict(GTAA_DEFAULT_SCORE_WEIGHTS),
                "trend_filter_window": GTAA_DEFAULT_TREND_FILTER_WINDOW,
                "risk_off_mode": GTAA_DEFAULT_RISK_OFF_MODE,
                "defensive_tickers": list(GTAA_DEFAULT_DEFENSIVE_TICKERS),
                "market_regime_enabled": False,
                "market_regime_window": STRICT_MARKET_REGIME_DEFAULT_WINDOW,
                "market_regime_benchmark": STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
                "crash_guardrail_enabled": GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
                "crash_guardrail_drawdown_threshold": GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
                "crash_guardrail_lookback_months": GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            },
        }
    if strategy_name == "Global Relative Strength":
        return {
            "tickers": list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS),
            "preset_name": "Global Relative Strength Core ETF Universe",
            "runner": run_global_relative_strength_backtest_from_db,
            "extra": {
                "cash_ticker": GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
                "top": GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
                "interval": GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
                "score_lookback_months": list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS),
                "score_return_columns": list(GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS),
                "score_weights": dict(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_WEIGHTS),
                "trend_filter_window": GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            },
        }
    if strategy_name == "Risk Parity Trend":
        return {
            "tickers": ["SPY", "TLT", "GLD", "IEF", "LQD"],
            "preset_name": "Risk Parity Universe",
            "runner": run_risk_parity_trend_backtest_from_db,
            "extra": {
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            },
        }
    if strategy_name == "Dual Momentum":
        return {
            "tickers": ["QQQ", "SPY", "IWM", "SOXX", "BIL"],
            "preset_name": "Dual Momentum Universe",
            "runner": run_dual_momentum_backtest_from_db,
            "extra": {
                "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
                "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                "promotion_min_etf_aum_b": ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                "promotion_max_bid_ask_spread_pct": ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
            },
        }
    if strategy_name == "Quality Snapshot":
        return {
            "tickers": ["AAPL", "MSFT", "GOOG"],
            "preset_name": "Big Tech Quality Trial",
            "runner": run_quality_snapshot_backtest_from_db,
            "extra": {
                "factor_freq": "annual",
                "rebalance_freq": "monthly",
                "quality_factors": ["roe", "gross_margin", "operating_margin", "debt_ratio"],
                "top_n": 2,
                "snapshot_mode": "broad_research",
            },
        }
    if strategy_name == "Quality Snapshot (Strict Annual)":
        default_preset = preset_catalog.strict_annual_compare_default_preset
        return {
            "tickers": list(preset_catalog.quality_strict_presets[default_preset]),
            "preset_name": default_preset,
            "runner": run_quality_snapshot_strict_annual_backtest_from_db,
            "extra": _strict_factor_extra("quality"),
        }
    if strategy_name == "Quality Snapshot (Strict Quarterly Prototype)":
        default_preset = preset_catalog.strict_quarterly_prototype_default_preset
        return {
            "tickers": list(preset_catalog.quality_strict_presets[default_preset]),
            "preset_name": default_preset,
            "runner": run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
            "extra": {
                "quality_factors": list(QUALITY_STRICT_DEFAULT_FACTORS),
                "top_n": 2,
            },
        }
    if strategy_name == "Value Snapshot (Strict Annual)":
        default_preset = preset_catalog.strict_annual_compare_default_preset
        return {
            "tickers": list(preset_catalog.value_strict_presets[default_preset]),
            "preset_name": default_preset,
            "runner": run_value_snapshot_strict_annual_backtest_from_db,
            "extra": _strict_factor_extra("value"),
        }
    if strategy_name == "Value Snapshot (Strict Quarterly Prototype)":
        default_preset = preset_catalog.strict_quarterly_prototype_default_preset
        return {
            "tickers": list(preset_catalog.value_strict_presets[default_preset]),
            "preset_name": default_preset,
            "runner": run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
            "extra": {
                "value_factors": list(VALUE_STRICT_DEFAULT_FACTORS),
                "top_n": 10,
            },
        }
    if strategy_name == "Quality + Value Snapshot (Strict Annual)":
        default_preset = preset_catalog.strict_annual_compare_default_preset
        return {
            "tickers": list(preset_catalog.quality_strict_presets[default_preset]),
            "preset_name": default_preset,
            "runner": run_quality_value_snapshot_strict_annual_backtest_from_db,
            "extra": _strict_factor_extra("quality_value"),
        }
    if strategy_name == "Quality + Value Snapshot (Strict Quarterly Prototype)":
        default_preset = preset_catalog.strict_quarterly_prototype_default_preset
        return {
            "tickers": list(preset_catalog.quality_strict_presets[default_preset]),
            "preset_name": default_preset,
            "runner": run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
            "extra": {
                "quality_factors": list(QUALITY_STRICT_DEFAULT_FACTORS),
                "value_factors": list(VALUE_STRICT_DEFAULT_FACTORS),
                "top_n": 10,
            },
        }
    raise BacktestInputError(f"Unsupported compare strategy: {strategy_name}")


def _strict_factor_extra(kind: str) -> dict[str, Any]:
    extra = {
        "top_n": 10 if kind in {"value", "quality_value"} else 2,
        "weighting_mode": STRICT_DEFAULT_WEIGHTING_MODE,
        "rejected_slot_handling_mode": STRICT_DEFAULT_REJECTION_HANDLING_MODE,
        "rejected_slot_fill_enabled": STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
        "partial_cash_retention_enabled": STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
        "risk_off_mode": STRICT_DEFAULT_RISK_OFF_MODE,
        "defensive_tickers": list(STRICT_DEFAULT_DEFENSIVE_TICKERS),
        "min_price_filter": ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
        "min_history_months_filter": STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
        "min_avg_dollar_volume_20d_m_filter": STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
        "transaction_cost_bps": ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
        "benchmark_ticker": ETF_REAL_MONEY_DEFAULT_BENCHMARK,
        "promotion_min_benchmark_coverage": STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
        "promotion_min_net_cagr_spread": STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        "promotion_min_liquidity_clean_coverage": STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        "promotion_max_underperformance_share": STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        "promotion_min_worst_rolling_excess_return": STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        "promotion_max_strategy_drawdown": STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
        "promotion_max_drawdown_gap_vs_benchmark": STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        "underperformance_guardrail_enabled": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
        "underperformance_guardrail_window_months": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        "underperformance_guardrail_threshold": STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
        "drawdown_guardrail_enabled": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
        "drawdown_guardrail_window_months": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
        "drawdown_guardrail_strategy_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
        "drawdown_guardrail_gap_threshold": STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    }
    if kind in {"quality", "quality_value"}:
        extra["quality_factors"] = list(QUALITY_STRICT_DEFAULT_FACTORS)
    if kind in {"value", "quality_value"}:
        extra["value_factors"] = list(VALUE_STRICT_DEFAULT_FACTORS)
    return extra


def _resolve_compare_strategy_universe(
    strategy_name: str,
    *,
    preset_name: str | None,
    fallback_tickers: list[str],
    preset_catalog: ComparePresetCatalog,
) -> tuple[list[str], str | None]:
    if strategy_name in {
        "Quality Snapshot (Strict Annual)",
        "Quality Snapshot (Strict Quarterly Prototype)",
        "Quality + Value Snapshot (Strict Annual)",
        "Quality + Value Snapshot (Strict Quarterly Prototype)",
    }:
        if preset_name in preset_catalog.quality_strict_presets:
            return list(preset_catalog.quality_strict_presets[preset_name]), preset_name
    elif strategy_name in {
        "Value Snapshot (Strict Annual)",
        "Value Snapshot (Strict Quarterly Prototype)",
    }:
        if preset_name in preset_catalog.value_strict_presets:
            return list(preset_catalog.value_strict_presets[preset_name]), preset_name

    return list(fallback_tickers), preset_name


__all__ = ["ComparePresetCatalog", "run_compare_strategy"]
