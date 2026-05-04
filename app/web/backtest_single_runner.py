from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403

def _handle_backtest_run(payload: dict, *, strategy_name: str) -> bool:
    st.markdown("#### Runtime Payload")
    st.json(payload)

    try:
        spinner_text = f"Running {strategy_name} backtest from DB..."
        started_at = time.perf_counter()
        with st.spinner(spinner_text):
            if payload["strategy_key"] == "equal_weight":
                bundle = run_equal_weight_backtest_from_db(
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
                    promotion_min_worst_rolling_excess_return=payload.get(
                        "promotion_min_worst_rolling_excess_return"
                    ),
                    promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown"),
                    promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark"),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "gtaa":
                bundle = run_gtaa_backtest_from_db(
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
                    crash_guardrail_drawdown_threshold=payload.get("crash_guardrail_drawdown_threshold", GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD),
                    crash_guardrail_lookback_months=payload.get("crash_guardrail_lookback_months", GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                    promotion_max_bid_ask_spread_pct=payload.get("promotion_max_bid_ask_spread_pct", ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "global_relative_strength":
                bundle = run_global_relative_strength_backtest_from_db(
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
                    transaction_cost_bps=payload.get(
                        "transaction_cost_bps",
                        ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
                    ),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    promotion_min_etf_aum_b=payload.get(
                        "promotion_min_etf_aum_b",
                        ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
                    ),
                    promotion_max_bid_ask_spread_pct=payload.get(
                        "promotion_max_bid_ask_spread_pct",
                        ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
                    ),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "risk_parity_trend":
                bundle = run_risk_parity_trend_backtest_from_db(
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
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                    promotion_max_bid_ask_spread_pct=payload.get("promotion_max_bid_ask_spread_pct", ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "dual_momentum":
                bundle = run_dual_momentum_backtest_from_db(
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
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    promotion_min_etf_aum_b=payload.get("promotion_min_etf_aum_b", ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
                    promotion_max_bid_ask_spread_pct=payload.get("promotion_max_bid_ask_spread_pct", ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                )
            elif payload["strategy_key"] == "quality_snapshot":
                bundle = run_quality_snapshot_backtest_from_db(
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
            elif payload["strategy_key"] == "quality_snapshot_strict_annual":
                bundle = run_quality_snapshot_strict_annual_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    quality_factors=payload["quality_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    min_history_months_filter=payload.get("min_history_months_filter", STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS),
                    min_avg_dollar_volume_20d_m_filter=payload.get("min_avg_dollar_volume_20d_m_filter", STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    guardrail_reference_ticker=payload.get("guardrail_reference_ticker", payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK)),
                    promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage", STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE),
                    promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread", STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD),
                    promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage", STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE),
                    promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share", STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE),
                    promotion_min_worst_rolling_excess_return=payload.get("promotion_min_worst_rolling_excess_return", STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN),
                    promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown", STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN),
                    promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark", STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
                    rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
                    rejected_slot_fill_enabled=payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED),
                    partial_cash_retention_enabled=payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED),
                    risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
                    defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "quality_snapshot_strict_quarterly_prototype":
                bundle = run_quality_snapshot_strict_quarterly_prototype_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    quality_factors=payload["quality_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
                    rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
                    rejected_slot_fill_enabled=payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED),
                    partial_cash_retention_enabled=payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED),
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
            elif payload["strategy_key"] == "value_snapshot_strict_annual":
                bundle = run_value_snapshot_strict_annual_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    value_factors=payload["value_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    min_price_filter=payload.get("min_price_filter", ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
                    min_history_months_filter=payload.get("min_history_months_filter", STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS),
                    min_avg_dollar_volume_20d_m_filter=payload.get("min_avg_dollar_volume_20d_m_filter", STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    guardrail_reference_ticker=payload.get("guardrail_reference_ticker", payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK)),
                    promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage", STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE),
                    promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread", STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD),
                    promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage", STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE),
                    promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share", STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE),
                    promotion_min_worst_rolling_excess_return=payload.get("promotion_min_worst_rolling_excess_return", STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN),
                    promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown", STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN),
                    promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark", STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
                    rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
                    rejected_slot_fill_enabled=payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED),
                    partial_cash_retention_enabled=payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED),
                    risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
                    defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "value_snapshot_strict_quarterly_prototype":
                bundle = run_value_snapshot_strict_quarterly_prototype_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    value_factors=payload["value_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
                    rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
                    rejected_slot_fill_enabled=payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED),
                    partial_cash_retention_enabled=payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED),
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
            elif payload["strategy_key"] == "quality_value_snapshot_strict_annual":
                bundle = run_quality_value_snapshot_strict_annual_backtest_from_db(
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
                    min_history_months_filter=payload.get("min_history_months_filter", STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS),
                    min_avg_dollar_volume_20d_m_filter=payload.get("min_avg_dollar_volume_20d_m_filter", STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M),
                    transaction_cost_bps=payload.get("transaction_cost_bps", ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS),
                    benchmark_contract=payload.get("benchmark_contract", STRICT_DEFAULT_BENCHMARK_CONTRACT),
                    benchmark_ticker=payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK),
                    guardrail_reference_ticker=payload.get("guardrail_reference_ticker", payload.get("benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK)),
                    promotion_min_benchmark_coverage=payload.get("promotion_min_benchmark_coverage", STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE),
                    promotion_min_net_cagr_spread=payload.get("promotion_min_net_cagr_spread", STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD),
                    promotion_min_liquidity_clean_coverage=payload.get("promotion_min_liquidity_clean_coverage", STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE),
                    promotion_max_underperformance_share=payload.get("promotion_max_underperformance_share", STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE),
                    promotion_min_worst_rolling_excess_return=payload.get("promotion_min_worst_rolling_excess_return", STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN),
                    promotion_max_strategy_drawdown=payload.get("promotion_max_strategy_drawdown", STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN),
                    promotion_max_drawdown_gap_vs_benchmark=payload.get("promotion_max_drawdown_gap_vs_benchmark", STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
                    rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
                    rejected_slot_fill_enabled=payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED),
                    partial_cash_retention_enabled=payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED),
                    risk_off_mode=payload.get("risk_off_mode", STRICT_DEFAULT_RISK_OFF_MODE),
                    defensive_tickers=payload.get("defensive_tickers", STRICT_DEFAULT_DEFENSIVE_TICKERS),
                    market_regime_enabled=payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED),
                    market_regime_window=payload.get("market_regime_window", STRICT_MARKET_REGIME_DEFAULT_WINDOW),
                    market_regime_benchmark=payload.get("market_regime_benchmark", STRICT_MARKET_REGIME_DEFAULT_BENCHMARK),
                    underperformance_guardrail_enabled=payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED),
                    underperformance_guardrail_window_months=payload.get("underperformance_guardrail_window_months", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    underperformance_guardrail_threshold=payload.get("underperformance_guardrail_threshold", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD),
                    drawdown_guardrail_enabled=payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED),
                    drawdown_guardrail_window_months=payload.get("drawdown_guardrail_window_months", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS),
                    drawdown_guardrail_strategy_threshold=payload.get("drawdown_guardrail_strategy_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD),
                    drawdown_guardrail_gap_threshold=payload.get("drawdown_guardrail_gap_threshold", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD),
                    universe_mode=payload["universe_mode"],
                    preset_name=payload["preset_name"],
                    universe_contract=payload.get("universe_contract", STATIC_MANAGED_RESEARCH_UNIVERSE),
                    dynamic_candidate_tickers=payload.get("dynamic_candidate_tickers"),
                    dynamic_target_size=payload.get("dynamic_target_size"),
                )
            elif payload["strategy_key"] == "quality_value_snapshot_strict_quarterly_prototype":
                bundle = run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db(
                    tickers=payload["tickers"],
                    start=payload["start"],
                    end=payload["end"],
                    timeframe=payload["timeframe"],
                    option=payload["option"],
                    quality_factors=payload["quality_factors"],
                    value_factors=payload["value_factors"],
                    top_n=payload["top"],
                    rebalance_interval=payload.get("rebalance_interval", 1),
                    trend_filter_enabled=payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED),
                    trend_filter_window=payload.get("trend_filter_window", STRICT_TREND_FILTER_DEFAULT_WINDOW),
                    weighting_mode=payload.get("weighting_mode", STRICT_DEFAULT_WEIGHTING_MODE),
                    rejected_slot_handling_mode=payload.get("rejected_slot_handling_mode"),
                    rejected_slot_fill_enabled=payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED),
                    partial_cash_retention_enabled=payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED),
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
            else:
                raise BacktestInputError(f"Unsupported strategy key: {payload['strategy_key']}")
    except BacktestInputError as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "input"
        st.session_state.backtest_last_error = f"Backtest input issue: {exc}"
        return False
    except BacktestDataError as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "data"
        st.session_state.backtest_last_error = f"Backtest data issue: {exc}"
        return False
    except Exception as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "system"
        st.session_state.backtest_last_error = f"Backtest execution failed: {exc}"
        return False

    elapsed_seconds = time.perf_counter() - started_at
    bundle = dict(bundle)
    meta = dict(bundle.get("meta") or {})
    meta["ui_elapsed_seconds"] = round(elapsed_seconds, 3)
    bundle["meta"] = meta

    st.session_state.backtest_last_bundle = bundle
    st.session_state.backtest_last_error = None
    st.session_state.backtest_last_error_kind = None
    append_backtest_run_history(bundle=bundle, run_kind="single_strategy")
    st.success(f"{strategy_name} backtest execution completed in {elapsed_seconds:.3f}s.")
    return True

__all__ = ["_handle_backtest_run"]
