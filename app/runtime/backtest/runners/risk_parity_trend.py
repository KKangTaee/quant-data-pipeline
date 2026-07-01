from __future__ import annotations

from app.runtime.backtest.runners.price_common import *  # noqa: F401,F403

def run_risk_parity_trend_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 1,
    vol_window: int = 6,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    promotion_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    promotion_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    promotion_min_benchmark_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float | None = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float | None = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float | None = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float | None = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float | None = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)
    promotion_policy = _resolve_dynamic_etf_promotion_policy_defaults(
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )
    _runtime_hook("_preflight_price_strategy_data", _preflight_price_strategy_data, __name__)(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if (underperformance_guardrail_enabled or drawdown_guardrail_enabled) and benchmark_ticker:
        guardrail_symbol = str(benchmark_ticker).strip().upper()
        if guardrail_symbol and guardrail_symbol not in normalized_tickers:
            _runtime_hook("_preflight_price_strategy_data", _preflight_price_strategy_data, __name__)(
                tickers=[guardrail_symbol],
                start=start,
                end=end,
                timeframe=timeframe,
            )

    result_df = _runtime_hook("get_risk_parity_trend_from_db", get_risk_parity_trend_from_db, __name__)(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        rebalance_interval=rebalance_interval,
        vol_window=vol_window,
        min_price=min_price_filter,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
    )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Risk Parity Trend",
        strategy_key="risk_parity_trend",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "rebalance_interval": rebalance_interval,
            "vol_window": vol_window,
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "drawdown_guardrail_enabled": drawdown_guardrail_enabled,
            "drawdown_guardrail_window_months": drawdown_guardrail_window_months,
            "drawdown_guardrail_strategy_threshold": drawdown_guardrail_strategy_threshold,
            "drawdown_guardrail_gap_threshold": drawdown_guardrail_gap_threshold,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            **promotion_policy,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )
    bundle["meta"]["risk_parity_trend_contract"] = _build_risk_parity_trend_contract(
        vol_window=vol_window,
        rebalance_interval=rebalance_interval,
        min_price_filter=min_price_filter,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
    )
    bundle["meta"]["risk_parity_inverse_vol_summary"] = _build_risk_parity_inverse_vol_summary(result_df)
    bundle = _runtime_hook("_apply_real_money_hardening", _apply_real_money_hardening, __name__)(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=normalized_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        **promotion_policy,
    )
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Underperformance Guardrail enabled: rebalance candidates move to cash when trailing strategy excess return "
            f"vs `{benchmark_ticker}` over `{underperformance_guardrail_window_months}M` falls below "
            f"`{underperformance_guardrail_threshold:.0%}`."
        ]
    if drawdown_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Drawdown Guardrail enabled: rebalance candidates move to cash when trailing strategy drawdown over "
            f"`{drawdown_guardrail_window_months}M` falls below `{drawdown_guardrail_strategy_threshold:.0%}` "
            f"or drawdown gap vs `{benchmark_ticker}` rises above `{drawdown_guardrail_gap_threshold:.0%}`."
        ]
    return bundle

