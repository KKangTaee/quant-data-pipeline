from __future__ import annotations

from app.runtime.backtest.runners.price_common import *  # noqa: F401,F403

def run_equal_weight_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 12,
    min_price_filter: float | None = None,
    transaction_cost_bps: float | None = None,
    benchmark_ticker: str | None = None,
    guardrail_reference_ticker: str | None = None,
    promotion_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    promotion_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    promotion_min_benchmark_coverage: float | None = None,
    promotion_min_net_cagr_spread: float | None = None,
    promotion_min_liquidity_clean_coverage: float | None = None,
    promotion_max_underperformance_share: float | None = None,
    promotion_min_worst_rolling_excess_return: float | None = None,
    promotion_max_strategy_drawdown: float | None = None,
    promotion_max_drawdown_gap_vs_benchmark: float | None = None,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    """
    Public UI-facing runtime wrapper for static equal-weight ETF baskets with Real-Money diagnostics.
    """
    normalized_tickers = _normalize_tickers(tickers)
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)
    price_freshness = inspect_strict_annual_price_freshness(
        tickers=normalized_tickers,
        end=end,
        timeframe=timeframe,
        context_label="Equal Weight universe",
    )
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if benchmark_ticker and benchmark_ticker not in normalized_tickers:
        _preflight_price_strategy_data(
            tickers=[benchmark_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )

    result_df = get_equal_weight_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        interval=rebalance_interval,
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
        strategy_name="Equal Weight",
        strategy_key="equal_weight",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "rebalance_interval": rebalance_interval,
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "guardrail_reference_ticker": guardrail_reference_ticker,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            "promotion_min_benchmark_coverage": promotion_min_benchmark_coverage,
            "promotion_min_net_cagr_spread": promotion_min_net_cagr_spread,
            "promotion_min_liquidity_clean_coverage": promotion_min_liquidity_clean_coverage,
            "promotion_max_underperformance_share": promotion_max_underperformance_share,
            "promotion_min_worst_rolling_excess_return": promotion_min_worst_rolling_excess_return,
            "promotion_max_strategy_drawdown": promotion_max_strategy_drawdown,
            "promotion_max_drawdown_gap_vs_benchmark": promotion_max_drawdown_gap_vs_benchmark,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=guardrail_reference_ticker,
        benchmark_universe_tickers=normalized_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )


