from __future__ import annotations

from app.runtime.backtest.runners.price_common import *  # noqa: F401,F403

def run_gtaa_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = 3,
    interval: int = GTAA_DEFAULT_SIGNAL_INTERVAL,
    min_price_filter: float | None = None,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float | None = None,
    benchmark_ticker: str | None = None,
    score_lookback_months: Sequence[int] | None = None,
    score_return_columns: Sequence[str] | None = None,
    score_weights: dict[str, float] | None = None,
    trend_filter_window: int = GTAA_DEFAULT_TREND_FILTER_WINDOW,
    risk_off_mode: str = GTAA_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    crash_guardrail_enabled: bool = GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    crash_guardrail_drawdown_threshold: float = GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    crash_guardrail_lookback_months: int = GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
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
    """
    Public UI-facing runtime wrapper for the second DB-backed backtest screen.
    """
    normalized_tickers = _normalize_tickers(tickers)
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)
    price_freshness = _runtime_hook("inspect_strict_annual_price_freshness", inspect_strict_annual_price_freshness, __name__)(
        tickers=normalized_tickers,
        end=end,
        timeframe=timeframe,
        context_label="GTAA universe",
    )
    _runtime_hook("_preflight_price_strategy_data", _preflight_price_strategy_data, __name__)(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if (market_regime_enabled or crash_guardrail_enabled) and market_regime_benchmark:
        benchmark_symbol = str(market_regime_benchmark).strip().upper()
        if benchmark_symbol and benchmark_symbol not in normalized_tickers:
            _runtime_hook("_preflight_price_strategy_data", _preflight_price_strategy_data, __name__)(
                tickers=[benchmark_symbol],
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

    normalized_score_lookback_months = [
        int(value)
        for value in (
            list(score_lookback_months)
            if score_lookback_months is not None
            else list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS)
        )
    ]
    normalized_score_return_columns = [f"{months}MReturn" for months in normalized_score_lookback_months]
    normalized_score_weights = (
        {f"{months}MReturn": 1.0 for months in normalized_score_lookback_months}
        if score_weights is None
        else dict(score_weights)
    )
    promotion_policy = _resolve_dynamic_etf_promotion_policy_defaults(
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )

    result_df = _runtime_hook("get_gtaa3_from_db", get_gtaa3_from_db, __name__)(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        interval=interval,
        min_price=min_price_filter,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m_filter,
        score_lookback_months=normalized_score_lookback_months,
        score_return_columns=normalized_score_return_columns,
        score_weights=normalized_score_weights,
        trend_filter_window=trend_filter_window,
        risk_off_mode=risk_off_mode,
        defensive_tickers=list(defensive_tickers or GTAA_DEFAULT_DEFENSIVE_TICKERS),
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        crash_guardrail_enabled=crash_guardrail_enabled,
        crash_guardrail_drawdown_threshold=crash_guardrail_drawdown_threshold,
        crash_guardrail_lookback_months=crash_guardrail_lookback_months,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
    )

    warnings: list[str] = []
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 점검에서 주의가 필요합니다. "
            + price_freshness["message"]
            + " 결과 기간이 요청 종료일보다 짧아질 수 있으므로 `Data Trust Summary`와 원본 가격 데이터를 함께 확인하세요."
        )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="GTAA",
        strategy_key="gtaa",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top,
            "rebalance_interval": interval,
            "min_price_filter": min_price_filter,
            "min_avg_dollar_volume_20d_m_filter": min_avg_dollar_volume_20d_m_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            **promotion_policy,
            "score_lookback_months": normalized_score_lookback_months,
            "score_return_columns": normalized_score_return_columns,
            "score_weights": normalized_score_weights,
            "trend_filter_window": trend_filter_window,
            "risk_off_mode": risk_off_mode,
            "defensive_tickers": list(defensive_tickers or GTAA_DEFAULT_DEFENSIVE_TICKERS),
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "crash_guardrail_enabled": crash_guardrail_enabled,
            "crash_guardrail_drawdown_threshold": crash_guardrail_drawdown_threshold,
            "crash_guardrail_lookback_months": crash_guardrail_lookback_months,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "drawdown_guardrail_enabled": drawdown_guardrail_enabled,
            "drawdown_guardrail_window_months": drawdown_guardrail_window_months,
            "drawdown_guardrail_strategy_threshold": drawdown_guardrail_strategy_threshold,
            "drawdown_guardrail_gap_threshold": drawdown_guardrail_gap_threshold,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
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
