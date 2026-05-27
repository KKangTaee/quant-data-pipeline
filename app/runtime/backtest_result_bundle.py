from __future__ import annotations

from typing import Any

import pandas as pd

from finance.performance import portfolio_performance_summary


def _infer_strategy_family(strategy_key: str, strategy_name: str) -> str:
    key = str(strategy_key or "").strip().lower()
    if key.startswith("quality_value"):
        return "Quality + Value"
    if key.startswith("quality"):
        return "Quality"
    if key.startswith("value"):
        return "Value"
    if key == "gtaa":
        return "GTAA"
    if key == "dual_momentum":
        return "Dual Momentum"
    if key == "risk_parity_trend":
        return "Risk Parity Trend"
    if key == "equal_weight":
        return "Equal Weight"
    return strategy_name


def build_backtest_result_bundle(
    result_df: pd.DataFrame,
    *,
    strategy_name: str,
    strategy_key: str,
    input_params: dict[str, Any],
    execution_mode: str = "db",
    data_mode: str = "db_backed",
    summary_freq: str = "M",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Build the minimal UI-facing bundle for a single backtest run."""

    if result_df is None or result_df.empty:
        raise ValueError("Backtest result is empty.")

    required_columns = {"Date", "Total Balance", "Total Return"}
    missing = required_columns.difference(result_df.columns)
    if missing:
        raise ValueError(f"Backtest result is missing required columns: {sorted(missing)}")

    result_df = result_df.copy()
    result_df["Date"] = pd.to_datetime(result_df["Date"])
    result_df = result_df.sort_values("Date").reset_index(drop=True)

    summary_df = portfolio_performance_summary(
        result_df,
        name=strategy_name,
        freq=summary_freq,
    )
    chart_df = result_df[["Date", "Total Balance", "Total Return"]].copy()

    meta = {
        "execution_mode": execution_mode,
        "data_mode": data_mode,
        "strategy_key": strategy_key,
        "strategy_name": strategy_name,
        "strategy_family": _infer_strategy_family(strategy_key, strategy_name),
        "result_rows": int(len(result_df)),
        "actual_result_start": result_df["Date"].min().strftime("%Y-%m-%d"),
        "actual_result_end": result_df["Date"].max().strftime("%Y-%m-%d"),
        "tickers": input_params.get("tickers", []),
        "start": input_params.get("start"),
        "end": input_params.get("end"),
        "timeframe": input_params.get("timeframe"),
        "option": input_params.get("option"),
        "rebalance_interval": input_params.get("rebalance_interval"),
        "universe_mode": input_params.get("universe_mode"),
        "preset_name": input_params.get("preset_name"),
        "warnings": warnings or [],
    }
    if input_params.get("top") is not None:
        meta["top"] = input_params.get("top")
    if input_params.get("cash_ticker") is not None:
        meta["cash_ticker"] = input_params.get("cash_ticker")
    if input_params.get("vol_window") is not None:
        meta["vol_window"] = input_params.get("vol_window")
    if input_params.get("factor_freq") is not None:
        meta["factor_freq"] = input_params.get("factor_freq")
    if input_params.get("rebalance_freq") is not None:
        meta["rebalance_freq"] = input_params.get("rebalance_freq")
    if input_params.get("snapshot_mode") is not None:
        meta["snapshot_mode"] = input_params.get("snapshot_mode")
    if input_params.get("quality_factors") is not None:
        meta["quality_factors"] = input_params.get("quality_factors")
    if input_params.get("value_factors") is not None:
        meta["value_factors"] = input_params.get("value_factors")
    if input_params.get("trend_filter_enabled") is not None:
        meta["trend_filter_enabled"] = input_params.get("trend_filter_enabled")
    if input_params.get("trend_filter_window") is not None:
        meta["trend_filter_window"] = input_params.get("trend_filter_window")
    if input_params.get("weighting_mode") is not None:
        meta["weighting_mode"] = input_params.get("weighting_mode")
    if input_params.get("rejected_slot_handling_mode") is not None:
        meta["rejected_slot_handling_mode"] = input_params.get("rejected_slot_handling_mode")
    if input_params.get("rejected_slot_fill_enabled") is not None:
        meta["rejected_slot_fill_enabled"] = input_params.get("rejected_slot_fill_enabled")
    if input_params.get("partial_cash_retention_enabled") is not None:
        meta["partial_cash_retention_enabled"] = input_params.get("partial_cash_retention_enabled")
    if input_params.get("market_regime_enabled") is not None:
        meta["market_regime_enabled"] = input_params.get("market_regime_enabled")
    if input_params.get("market_regime_window") is not None:
        meta["market_regime_window"] = input_params.get("market_regime_window")
    if input_params.get("market_regime_benchmark") is not None:
        meta["market_regime_benchmark"] = input_params.get("market_regime_benchmark")
    if input_params.get("min_price_filter") is not None:
        meta["min_price_filter"] = input_params.get("min_price_filter")
    if input_params.get("min_history_months_filter") is not None:
        meta["min_history_months_filter"] = input_params.get("min_history_months_filter")
    if input_params.get("min_avg_dollar_volume_20d_m_filter") is not None:
        meta["min_avg_dollar_volume_20d_m_filter"] = input_params.get("min_avg_dollar_volume_20d_m_filter")
    if input_params.get("transaction_cost_bps") is not None:
        meta["transaction_cost_bps"] = input_params.get("transaction_cost_bps")
    if input_params.get("promotion_min_etf_aum_b") is not None:
        meta["promotion_min_etf_aum_b"] = input_params.get("promotion_min_etf_aum_b")
    if input_params.get("promotion_max_bid_ask_spread_pct") is not None:
        meta["promotion_max_bid_ask_spread_pct"] = input_params.get("promotion_max_bid_ask_spread_pct")
    if input_params.get("benchmark_ticker") is not None:
        meta["benchmark_ticker"] = input_params.get("benchmark_ticker")
    if input_params.get("guardrail_reference_ticker") is not None:
        meta["guardrail_reference_ticker"] = input_params.get("guardrail_reference_ticker")
    if input_params.get("promotion_min_benchmark_coverage") is not None:
        meta["promotion_min_benchmark_coverage"] = input_params.get("promotion_min_benchmark_coverage")
    if input_params.get("promotion_min_net_cagr_spread") is not None:
        meta["promotion_min_net_cagr_spread"] = input_params.get("promotion_min_net_cagr_spread")
    if input_params.get("promotion_min_liquidity_clean_coverage") is not None:
        meta["promotion_min_liquidity_clean_coverage"] = input_params.get("promotion_min_liquidity_clean_coverage")
    if input_params.get("promotion_max_underperformance_share") is not None:
        meta["promotion_max_underperformance_share"] = input_params.get("promotion_max_underperformance_share")
    if input_params.get("promotion_min_worst_rolling_excess_return") is not None:
        meta["promotion_min_worst_rolling_excess_return"] = input_params.get("promotion_min_worst_rolling_excess_return")
    if input_params.get("promotion_max_strategy_drawdown") is not None:
        meta["promotion_max_strategy_drawdown"] = input_params.get("promotion_max_strategy_drawdown")
    if input_params.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
        meta["promotion_max_drawdown_gap_vs_benchmark"] = input_params.get("promotion_max_drawdown_gap_vs_benchmark")
    if input_params.get("underperformance_guardrail_enabled") is not None:
        meta["underperformance_guardrail_enabled"] = input_params.get("underperformance_guardrail_enabled")
    if input_params.get("underperformance_guardrail_window_months") is not None:
        meta["underperformance_guardrail_window_months"] = input_params.get("underperformance_guardrail_window_months")
    if input_params.get("underperformance_guardrail_threshold") is not None:
        meta["underperformance_guardrail_threshold"] = input_params.get("underperformance_guardrail_threshold")
    if input_params.get("drawdown_guardrail_enabled") is not None:
        meta["drawdown_guardrail_enabled"] = input_params.get("drawdown_guardrail_enabled")
    if input_params.get("drawdown_guardrail_window_months") is not None:
        meta["drawdown_guardrail_window_months"] = input_params.get("drawdown_guardrail_window_months")
    if input_params.get("drawdown_guardrail_strategy_threshold") is not None:
        meta["drawdown_guardrail_strategy_threshold"] = input_params.get("drawdown_guardrail_strategy_threshold")
    if input_params.get("drawdown_guardrail_gap_threshold") is not None:
        meta["drawdown_guardrail_gap_threshold"] = input_params.get("drawdown_guardrail_gap_threshold")
    if input_params.get("snapshot_source") is not None:
        meta["snapshot_source"] = input_params.get("snapshot_source")
    if input_params.get("universe_contract") is not None:
        meta["universe_contract"] = input_params.get("universe_contract")
    if input_params.get("dynamic_target_size") is not None:
        meta["dynamic_target_size"] = input_params.get("dynamic_target_size")
    if input_params.get("dynamic_candidate_count") is not None:
        meta["dynamic_candidate_count"] = input_params.get("dynamic_candidate_count")
    if input_params.get("dynamic_candidate_preview") is not None:
        meta["dynamic_candidate_preview"] = input_params.get("dynamic_candidate_preview")
    if input_params.get("universe_builder_scope") is not None:
        meta["universe_builder_scope"] = input_params.get("universe_builder_scope")
    if input_params.get("universe_debug") is not None:
        meta["universe_debug"] = input_params.get("universe_debug")
    if input_params.get("score_weights") is not None:
        meta["score_weights"] = input_params.get("score_weights")
    if input_params.get("score_lookback_months") is not None:
        meta["score_lookback_months"] = input_params.get("score_lookback_months")
    if input_params.get("score_return_columns") is not None:
        meta["score_return_columns"] = input_params.get("score_return_columns")
    if input_params.get("requested_tickers") is not None:
        meta["requested_tickers"] = input_params.get("requested_tickers")
    if input_params.get("excluded_tickers") is not None:
        meta["excluded_tickers"] = input_params.get("excluded_tickers")
    if input_params.get("malformed_price_rows") is not None:
        meta["malformed_price_rows"] = input_params.get("malformed_price_rows")
    if input_params.get("risk_off_mode") is not None:
        meta["risk_off_mode"] = input_params.get("risk_off_mode")
    if input_params.get("defensive_tickers") is not None:
        meta["defensive_tickers"] = input_params.get("defensive_tickers")
    if input_params.get("crash_guardrail_enabled") is not None:
        meta["crash_guardrail_enabled"] = input_params.get("crash_guardrail_enabled")
    if input_params.get("crash_guardrail_drawdown_threshold") is not None:
        meta["crash_guardrail_drawdown_threshold"] = input_params.get("crash_guardrail_drawdown_threshold")
    if input_params.get("crash_guardrail_lookback_months") is not None:
        meta["crash_guardrail_lookback_months"] = input_params.get("crash_guardrail_lookback_months")
    if input_params.get("research_source") is not None:
        meta["research_source"] = input_params.get("research_source")

    return {
        "strategy_name": strategy_name,
        "result_df": result_df,
        "summary_df": summary_df,
        "chart_df": chart_df,
        "meta": meta,
    }


__all__ = ["build_backtest_result_bundle"]
