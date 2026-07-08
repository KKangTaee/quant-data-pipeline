from __future__ import annotations

from app.runtime.backtest.runners.price_common import *  # noqa: F401,F403

def run_global_relative_strength_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    cash_ticker: str | None = GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    interval: int = GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    min_price_filter: float | None = None,
    transaction_cost_bps: float | None = None,
    benchmark_ticker: str | None = None,
    benchmark_contract: str | None = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    score_lookback_months: Sequence[int] | None = None,
    score_return_columns: Sequence[str] | None = None,
    score_weights: dict[str, float] | None = None,
    trend_filter_window: int = GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
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
    normalized_tickers = _normalize_tickers(tickers or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS)
    normalized_cash_ticker = str(cash_ticker or "").strip().upper() or None
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    normalized_benchmark_contract = str(benchmark_contract or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower()
    _validate_backtest_date_range(start, end)

    preflight_tickers = list(normalized_tickers)
    if normalized_cash_ticker and normalized_cash_ticker not in preflight_tickers:
        preflight_tickers.append(normalized_cash_ticker)
    price_freshness = _runtime_hook("inspect_strict_annual_price_freshness", inspect_strict_annual_price_freshness, __name__)(
        tickers=preflight_tickers,
        end=end,
        timeframe=timeframe,
        context_label="Global Relative Strength universe",
    )
    if normalized_cash_ticker:
        _runtime_hook("_preflight_price_strategy_data", _preflight_price_strategy_data, __name__)(
            tickers=[normalized_cash_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if (
        normalized_benchmark_contract == STRICT_BENCHMARK_CONTRACT_TICKER
        and benchmark_ticker
        and benchmark_ticker != normalized_cash_ticker
    ):
        _runtime_hook("_preflight_price_strategy_data", _preflight_price_strategy_data, __name__)(
            tickers=[benchmark_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )

    (
        normalized_score_lookback_months,
        normalized_score_return_columns,
        normalized_score_weights,
    ) = _normalize_grs_score_contract(
        score_lookback_months=score_lookback_months,
        score_return_columns=score_return_columns,
        score_weights=score_weights,
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

    result_df = _runtime_hook("get_global_relative_strength_from_db", get_global_relative_strength_from_db, __name__)(
        tickers=normalized_tickers,
        cash_ticker=normalized_cash_ticker,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        interval=interval,
        min_price=min_price_filter,
        score_lookback_months=normalized_score_lookback_months,
        score_return_columns=normalized_score_return_columns,
        score_weights=normalized_score_weights,
        trend_filter_window=trend_filter_window,
    )
    effective_tickers = _normalize_tickers(result_df.attrs.get("effective_tickers") or normalized_tickers)
    requested_tickers = _normalize_tickers(result_df.attrs.get("requested_tickers") or normalized_tickers)
    excluded_tickers_raw = result_df.attrs.get("excluded_tickers") or []
    excluded_tickers = _normalize_tickers(excluded_tickers_raw) if excluded_tickers_raw else []
    malformed_price_rows = list(result_df.attrs.get("malformed_price_rows") or [])
    warnings: list[str] = []
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 점검에서 주의가 필요합니다. "
            + price_freshness["message"]
            + " 결과 기간이 요청 종료일보다 짧아질 수 있으므로 `Data Trust Summary`와 원본 가격 데이터를 함께 확인하세요."
        )
    if excluded_tickers:
        warnings.append(
            "Global Relative Strength 실행에서 이동평균/상대강도 계산에 필요한 가격 이력이 부족한 티커를 제외했습니다: "
            + ", ".join(excluded_tickers)
            + ". 결과를 해석하기 전에 해당 티커의 DB 가격 데이터를 보강하거나 universe에서 제외하는 것이 좋습니다."
        )
    if malformed_price_rows:
        malformed_preview = []
        for row in malformed_price_rows[:5]:
            ticker = str(row.get("ticker") or "").strip().upper()
            count = int(row.get("count") or 0)
            sample_dates = row.get("sample_dates") or []
            sample_text = ", ".join(str(value) for value in sample_dates[:3])
            malformed_preview.append(f"{ticker} {count}건({sample_text})")
        more = ""
        if len(malformed_price_rows) > 5:
            more = f" 외 {len(malformed_price_rows) - 5}개 티커"
        warnings.append(
            "가격 데이터에 결측 행이 있어 공통 리밸런싱 날짜가 보수적으로 줄어들 수 있습니다: "
            + "; ".join(malformed_preview)
            + more
            + ". 값을 임의로 채우거나 보정하지 않았으므로, 원본 DB 가격 데이터를 점검하거나 재수집하는 것이 좋습니다."
        )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Global Relative Strength",
        strategy_key="global_relative_strength",
        input_params={
            "tickers": effective_tickers,
            "requested_tickers": requested_tickers,
            "excluded_tickers": excluded_tickers,
            "malformed_price_rows": malformed_price_rows,
            "cash_ticker": normalized_cash_ticker,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top,
            "rebalance_interval": interval,
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "benchmark_contract": normalized_benchmark_contract,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            **promotion_policy,
            "score_lookback_months": normalized_score_lookback_months,
            "score_return_columns": normalized_score_return_columns,
            "score_weights": normalized_score_weights,
            "trend_filter_enabled": True,
            "trend_filter_window": trend_filter_window,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "research_source": "/Users/taeho/Project/quant-research/.note/research/strategies/2026-04-15-global-relative-strength-allocation-with-trend-safety-net.md",
        },
        summary_freq=_summary_frequency(option, timeframe),
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    bundle["meta"]["grs_strategy_contract"] = _build_grs_strategy_contract(
        cash_ticker=normalized_cash_ticker,
        benchmark_contract=normalized_benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        top=top,
        interval=interval,
        trend_filter_window=trend_filter_window,
        score_lookback_months=normalized_score_lookback_months,
        score_return_columns=normalized_score_return_columns,
        score_weights=normalized_score_weights,
    )
    bundle["meta"]["grs_top_n_concentration"] = _build_grs_top_n_concentration_summary(result_df)
    return _runtime_hook("_apply_real_money_hardening", _apply_real_money_hardening, __name__)(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=normalized_benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=effective_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        **promotion_policy,
    )
