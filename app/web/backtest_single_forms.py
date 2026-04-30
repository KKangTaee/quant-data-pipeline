from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run

def _render_single_strategy_family_form(strategy_choice: str) -> None:
    variant_key = _single_family_variant_session_key(strategy_choice)
    variant_options = family_variant_options(strategy_choice)
    if not variant_key or not variant_options:
        return

    st.caption("이 카테고리 안에서 실행 variant를 선택합니다.")
    selected_variant = st.selectbox(
        f"{strategy_choice} Variant",
        options=variant_options,
        key=variant_key,
    )
    concrete_strategy_name = resolve_concrete_strategy_display_name(strategy_choice, selected_variant)
    _render_strategy_capability_snapshot(concrete_strategy_name)

    if concrete_strategy_name == "Quality Snapshot":
        _render_quality_snapshot_form()
    elif concrete_strategy_name == "Quality Snapshot (Strict Annual)":
        _render_quality_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Quality Snapshot (Strict Quarterly Prototype)":
        _render_quality_snapshot_strict_quarterly_prototype_form()
    elif concrete_strategy_name == "Value Snapshot (Strict Annual)":
        _render_value_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Value Snapshot (Strict Quarterly Prototype)":
        _render_value_snapshot_strict_quarterly_prototype_form()
    elif concrete_strategy_name == "Quality + Value Snapshot (Strict Annual)":
        _render_quality_value_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Quality + Value Snapshot (Strict Quarterly Prototype)":
        _render_quality_value_snapshot_strict_quarterly_prototype_form()

def _apply_single_strategy_prefill(strategy_key: str) -> None:
    payload = st.session_state.get("backtest_prefill_payload")
    pending = st.session_state.get("backtest_prefill_pending")
    if not payload or not pending or payload.get("strategy_key") != strategy_key:
        return

    start_date = pd.to_datetime(payload.get("start")).date() if payload.get("start") else date(2016, 1, 1)
    end_date = pd.to_datetime(payload.get("end")).date() if payload.get("end") else DEFAULT_BACKTEST_END_DATE
    tickers_text = ",".join(payload.get("tickers", []))
    preset_name = payload.get("preset_name")
    universe_mode = payload.get("universe_mode")

    if strategy_key == "equal_weight":
        st.session_state["eq_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in EQUAL_WEIGHT_PRESETS else "Manual"
        if st.session_state["eq_universe_mode"] == "Preset":
            st.session_state["eq_preset"] = preset_name
        else:
            st.session_state["eq_manual_tickers"] = tickers_text
        st.session_state["eq_start"] = start_date
        st.session_state["eq_end"] = end_date
        st.session_state["eq_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["eq_option"] = payload.get("option") or "month_end"
        st.session_state["eq_rebalance_interval"] = int(payload.get("rebalance_interval") or 12)
    elif strategy_key == "gtaa":
        st.session_state["gtaa_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in GTAA_PRESETS else "Manual"
        if st.session_state["gtaa_universe_mode"] == "Preset":
            st.session_state["gtaa_preset"] = preset_name
        else:
            st.session_state["gtaa_manual_tickers"] = tickers_text
        st.session_state["gtaa_start"] = start_date
        st.session_state["gtaa_end"] = end_date
        st.session_state["gtaa_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["gtaa_option"] = payload.get("option") or "month_end"
        st.session_state["gtaa_top"] = int(payload.get("top") or 3)
        st.session_state["gtaa_interval"] = int(payload.get("interval") or GTAA_DEFAULT_SIGNAL_INTERVAL)
        _set_gtaa_score_selection_state(
            key_prefix="gtaa",
            score_lookback_months=list(
                payload.get("score_lookback_months")
                or [_gtaa_months_from_return_col(col) for col in list(payload.get("score_return_columns") or GTAA_SCORE_RETURN_COLUMNS)]
            ),
        )
        st.session_state["gtaa_trend_filter_window"] = int(payload.get("trend_filter_window") or GTAA_DEFAULT_TREND_FILTER_WINDOW)
        st.session_state["gtaa_risk_off_mode"] = _risk_off_mode_value_to_label(payload.get("risk_off_mode") or GTAA_DEFAULT_RISK_OFF_MODE)
        st.session_state["gtaa_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or GTAA_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["gtaa_risk_off_market_regime_enabled"] = bool(
            payload.get("market_regime_enabled", False)
        )
        st.session_state["gtaa_risk_off_market_regime_window"] = int(
            payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW
        )
        st.session_state["gtaa_risk_off_market_regime_benchmark"] = (
            payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        )
        st.session_state["gtaa_crash_guardrail_enabled"] = bool(
            payload.get("crash_guardrail_enabled", GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED)
        )
        st.session_state["gtaa_crash_guardrail_drawdown_threshold"] = float(
            (payload.get("crash_guardrail_drawdown_threshold") or GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD) * 100.0
        )
        st.session_state["gtaa_crash_guardrail_lookback_months"] = int(
            payload.get("crash_guardrail_lookback_months") or GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS
        )
        st.session_state["gtaa_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["gtaa_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["gtaa_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["gtaa_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["gtaa_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["gtaa_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["gtaa_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["gtaa_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["gtaa_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["gtaa_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["gtaa_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["gtaa_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
    elif strategy_key == "global_relative_strength":
        st.session_state["grs_universe_mode"] = (
            "Preset"
            if universe_mode == "preset" and preset_name in GLOBAL_RELATIVE_STRENGTH_PRESETS
            else "Manual"
        )
        if st.session_state["grs_universe_mode"] == "Preset":
            st.session_state["grs_preset"] = preset_name or "Global Relative Strength Core ETF Universe"
        else:
            st.session_state["grs_manual_tickers"] = tickers_text
        st.session_state["grs_start"] = start_date
        st.session_state["grs_end"] = end_date
        st.session_state["grs_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["grs_option"] = payload.get("option") or "month_end"
        st.session_state["grs_cash_ticker"] = str(
            payload.get("cash_ticker") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER
        ).strip().upper()
        st.session_state["grs_top"] = int(payload.get("top") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP)
        st.session_state["grs_interval"] = int(
            payload.get("interval")
            or payload.get("rebalance_interval")
            or GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL
        )
        _set_global_relative_strength_score_selection_state(
            key_prefix="grs",
            score_lookback_months=list(
                payload.get("score_lookback_months")
                or [
                    _gtaa_months_from_return_col(col)
                    for col in list(payload.get("score_return_columns") or GLOBAL_RELATIVE_STRENGTH_SCORE_RETURN_COLUMNS)
                ]
            ),
        )
        st.session_state["grs_trend_filter_window"] = int(
            payload.get("trend_filter_window") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW
        )
        st.session_state["grs_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["grs_transaction_cost_bps"] = float(
            payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS
        )
        st.session_state["grs_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["grs_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["grs_benchmark_ticker"] = str(
            payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK
        ).strip().upper()
    elif strategy_key == "risk_parity_trend":
        st.session_state["rp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in RISK_PARITY_PRESETS else "Manual"
        if st.session_state["rp_universe_mode"] == "Preset":
            st.session_state["rp_preset"] = preset_name
        else:
            st.session_state["rp_manual_tickers"] = tickers_text
        st.session_state["rp_start"] = start_date
        st.session_state["rp_end"] = end_date
        st.session_state["rp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["rp_option"] = payload.get("option") or "month_end"
        st.session_state["rp_rebalance_interval"] = int(payload.get("rebalance_interval") or 1)
        st.session_state["rp_vol_window"] = int(payload.get("vol_window") or 6)
        st.session_state["rp_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["rp_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["rp_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["rp_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["rp_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["rp_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["rp_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["rp_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["rp_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["rp_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["rp_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["rp_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
    elif strategy_key == "dual_momentum":
        st.session_state["dm_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in DUAL_MOMENTUM_PRESETS else "Manual"
        if st.session_state["dm_universe_mode"] == "Preset":
            st.session_state["dm_preset"] = preset_name
        else:
            st.session_state["dm_manual_tickers"] = tickers_text
        st.session_state["dm_start"] = start_date
        st.session_state["dm_end"] = end_date
        st.session_state["dm_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["dm_option"] = payload.get("option") or "month_end"
        st.session_state["dm_top"] = int(payload.get("top") or 1)
        st.session_state["dm_rebalance_interval"] = int(payload.get("rebalance_interval") or 1)
        st.session_state["dm_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["dm_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["dm_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["dm_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
        st.session_state["dm_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["dm_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["dm_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["dm_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["dm_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["dm_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["dm_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["dm_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
    elif strategy_key == "quality_snapshot":
        st.session_state["qs_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_BROAD_PRESETS else "Manual"
        if st.session_state["qs_universe_mode"] == "Preset":
            st.session_state["qs_preset"] = preset_name
        else:
            st.session_state["qs_manual_tickers"] = tickers_text
        st.session_state["qs_start"] = start_date
        st.session_state["qs_end"] = end_date
        st.session_state["qs_top_n"] = int(payload.get("top") or 2)
        st.session_state["qs_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qs_option"] = payload.get("option") or "month_end"
        st.session_state["qs_factor_freq"] = payload.get("factor_freq") or "annual"
        st.session_state["qs_snapshot_mode"] = payload.get("snapshot_mode") or "broad_research"
        st.session_state["qs_quality_factors"] = payload.get("quality_factors") or ["roe", "gross_margin", "operating_margin", "debt_ratio"]
    elif strategy_key == "quality_snapshot_strict_annual":
        st.session_state["qss_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qss_universe_mode"] == "Preset":
            st.session_state["qss_preset"] = preset_name
        else:
            st.session_state["qss_manual_tickers"] = tickers_text
        st.session_state["qss_start"] = start_date
        st.session_state["qss_end"] = end_date
        st.session_state["qss_top_n"] = int(payload.get("top") or 2)
        st.session_state["qss_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qss_option"] = payload.get("option") or "month_end"
        st.session_state["qss_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qss_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qss_weighting_mode"] = _strict_weighting_mode_value_to_label(
            payload.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
        )
        st.session_state["qss_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            resolve_strict_rejection_handling_mode(
                payload.get("rejected_slot_handling_mode"),
                rejected_slot_fill_enabled=bool(
                    payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
                ),
                partial_cash_retention_enabled=bool(
                    payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
                ),
            )
        )
        st.session_state["qss_rejected_slot_fill_enabled"] = bool(
            payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
        )
        st.session_state["qss_partial_cash_retention_enabled"] = bool(
            payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
        )
        st.session_state["qss_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
            payload.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
        )
        st.session_state["qss_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["qss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        st.session_state["qss_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qss_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qss_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["qss_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qss_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qss_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["qss_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        st.session_state["qss_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["qss_min_history_months_filter"] = int(
            payload.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
        )
        st.session_state["qss_min_avg_dollar_volume_20d_m_filter"] = float(
            payload.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
        st.session_state["qss_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["qss_benchmark_contract"] = _benchmark_contract_value_to_label(
            payload.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
        )
        st.session_state["qss_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["qss_guardrail_reference_ticker"] = str(payload.get("guardrail_reference_ticker") or "").strip().upper()
        st.session_state["qss_promotion_min_benchmark_coverage"] = float(
            (payload.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE) * 100.0
        )
        st.session_state["qss_promotion_min_net_cagr_spread"] = float(
            (payload.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD) * 100.0
        )
        st.session_state["qss_promotion_min_liquidity_clean_coverage"] = float(
            (payload.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE) * 100.0
        )
        st.session_state["qss_promotion_max_underperformance_share"] = float(
            (payload.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE) * 100.0
        )
        st.session_state["qss_promotion_min_worst_rolling_excess_return"] = float(
            (payload.get("promotion_min_worst_rolling_excess_return") or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN) * 100.0
        )
        st.session_state["qss_promotion_max_strategy_drawdown"] = float(
            (payload.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN) * 100.0
        )
        st.session_state["qss_promotion_max_drawdown_gap_vs_benchmark"] = float(
            (payload.get("promotion_max_drawdown_gap_vs_benchmark") or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK) * 100.0
        )
    elif strategy_key == "quality_snapshot_strict_quarterly_prototype":
        st.session_state["qsqp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qsqp_universe_mode"] == "Preset":
            st.session_state["qsqp_preset"] = preset_name
        else:
            st.session_state["qsqp_manual_tickers"] = tickers_text
        st.session_state["qsqp_start"] = start_date
        st.session_state["qsqp_end"] = end_date
        st.session_state["qsqp_top_n"] = int(payload.get("top") or 2)
        st.session_state["qsqp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qsqp_option"] = payload.get("option") or "month_end"
        st.session_state["qsqp_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qsqp_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qsqp_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qsqp_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qsqp_weighting_mode"] = _strict_weighting_mode_value_to_label(
            payload.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
        )
        st.session_state["qsqp_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            resolve_strict_rejection_handling_mode(
                payload.get("rejected_slot_handling_mode"),
                rejected_slot_fill_enabled=bool(
                    payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
                ),
                partial_cash_retention_enabled=bool(
                    payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
                ),
            )
        )
        st.session_state["qsqp_rejected_slot_fill_enabled"] = bool(
            payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
        )
        st.session_state["qsqp_partial_cash_retention_enabled"] = bool(
            payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
        )
        st.session_state["qsqp_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
            payload.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
        )
        st.session_state["qsqp_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["qsqp_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qsqp_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qsqp_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    elif strategy_key == "value_snapshot_strict_annual":
        st.session_state["vss_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in VALUE_STRICT_PRESETS else "Manual"
        if st.session_state["vss_universe_mode"] == "Preset":
            st.session_state["vss_preset"] = preset_name
        else:
            st.session_state["vss_manual_tickers"] = tickers_text
        st.session_state["vss_start"] = start_date
        st.session_state["vss_end"] = end_date
        st.session_state["vss_top_n"] = int(payload.get("top") or 10)
        st.session_state["vss_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["vss_option"] = payload.get("option") or "month_end"
        st.session_state["vss_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["vss_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["vss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["vss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["vss_weighting_mode"] = _strict_weighting_mode_value_to_label(
            payload.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
        )
        st.session_state["vss_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            resolve_strict_rejection_handling_mode(
                payload.get("rejected_slot_handling_mode"),
                rejected_slot_fill_enabled=bool(
                    payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
                ),
                partial_cash_retention_enabled=bool(
                    payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
                ),
            )
        )
        st.session_state["vss_rejected_slot_fill_enabled"] = bool(
            payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
        )
        st.session_state["vss_partial_cash_retention_enabled"] = bool(
            payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
        )
        st.session_state["vss_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
            payload.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
        )
        st.session_state["vss_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["vss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["vss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["vss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        st.session_state["vss_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["vss_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["vss_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["vss_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["vss_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["vss_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["vss_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        st.session_state["vss_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["vss_min_history_months_filter"] = int(
            payload.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
        )
        st.session_state["vss_min_avg_dollar_volume_20d_m_filter"] = float(
            payload.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
        st.session_state["vss_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["vss_benchmark_contract"] = _benchmark_contract_value_to_label(
            payload.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
        )
        st.session_state["vss_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["vss_guardrail_reference_ticker"] = str(payload.get("guardrail_reference_ticker") or "").strip().upper()
        st.session_state["vss_promotion_min_benchmark_coverage"] = float(
            (payload.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE) * 100.0
        )
        st.session_state["vss_promotion_min_net_cagr_spread"] = float(
            (payload.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD) * 100.0
        )
        st.session_state["vss_promotion_min_liquidity_clean_coverage"] = float(
            (payload.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE) * 100.0
        )
        st.session_state["vss_promotion_max_underperformance_share"] = float(
            (payload.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE) * 100.0
        )
        st.session_state["vss_promotion_min_worst_rolling_excess_return"] = float(
            (payload.get("promotion_min_worst_rolling_excess_return") or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN) * 100.0
        )
        st.session_state["vss_promotion_max_strategy_drawdown"] = float(
            (payload.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN) * 100.0
        )
        st.session_state["vss_promotion_max_drawdown_gap_vs_benchmark"] = float(
            (payload.get("promotion_max_drawdown_gap_vs_benchmark") or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK) * 100.0
        )
    elif strategy_key == "value_snapshot_strict_quarterly_prototype":
        st.session_state["vsqp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in VALUE_STRICT_PRESETS else "Manual"
        if st.session_state["vsqp_universe_mode"] == "Preset":
            st.session_state["vsqp_preset"] = preset_name
        else:
            st.session_state["vsqp_manual_tickers"] = tickers_text
        st.session_state["vsqp_start"] = start_date
        st.session_state["vsqp_end"] = end_date
        st.session_state["vsqp_top_n"] = int(payload.get("top") or 10)
        st.session_state["vsqp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["vsqp_option"] = payload.get("option") or "month_end"
        st.session_state["vsqp_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["vsqp_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["vsqp_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["vsqp_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["vsqp_weighting_mode"] = _strict_weighting_mode_value_to_label(
            payload.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
        )
        st.session_state["vsqp_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            resolve_strict_rejection_handling_mode(
                payload.get("rejected_slot_handling_mode"),
                rejected_slot_fill_enabled=bool(
                    payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
                ),
                partial_cash_retention_enabled=bool(
                    payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
                ),
            )
        )
        st.session_state["vsqp_rejected_slot_fill_enabled"] = bool(
            payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
        )
        st.session_state["vsqp_partial_cash_retention_enabled"] = bool(
            payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
        )
        st.session_state["vsqp_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
            payload.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
        )
        st.session_state["vsqp_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["vsqp_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["vsqp_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["vsqp_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
    elif strategy_key == "quality_value_snapshot_strict_annual":
        st.session_state["qvss_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qvss_universe_mode"] == "Preset":
            st.session_state["qvss_preset"] = preset_name
        else:
            st.session_state["qvss_manual_tickers"] = tickers_text
        st.session_state["qvss_start"] = start_date
        st.session_state["qvss_end"] = end_date
        st.session_state["qvss_top_n"] = int(payload.get("top") or 10)
        st.session_state["qvss_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qvss_option"] = payload.get("option") or "month_end"
        st.session_state["qvss_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qvss_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["qvss_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qvss_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qvss_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qvss_weighting_mode"] = _strict_weighting_mode_value_to_label(
            payload.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
        )
        st.session_state["qvss_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            resolve_strict_rejection_handling_mode(
                payload.get("rejected_slot_handling_mode"),
                rejected_slot_fill_enabled=bool(
                    payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
                ),
                partial_cash_retention_enabled=bool(
                    payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
                ),
            )
        )
        st.session_state["qvss_rejected_slot_fill_enabled"] = bool(
            payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
        )
        st.session_state["qvss_partial_cash_retention_enabled"] = bool(
            payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
        )
        st.session_state["qvss_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
            payload.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
        )
        st.session_state["qvss_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["qvss_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qvss_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qvss_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK
        st.session_state["qvss_underperformance_guardrail_enabled"] = bool(
            payload.get("underperformance_guardrail_enabled", STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qvss_underperformance_guardrail_window_months"] = int(
            payload.get("underperformance_guardrail_window_months") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qvss_underperformance_guardrail_threshold"] = float(
            (payload.get("underperformance_guardrail_threshold") or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD) * 100.0
        )
        st.session_state["qvss_drawdown_guardrail_enabled"] = bool(
            payload.get("drawdown_guardrail_enabled", STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED)
        )
        st.session_state["qvss_drawdown_guardrail_window_months"] = int(
            payload.get("drawdown_guardrail_window_months") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS
        )
        st.session_state["qvss_drawdown_guardrail_strategy_threshold"] = float(
            (payload.get("drawdown_guardrail_strategy_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD) * 100.0
        )
        st.session_state["qvss_drawdown_guardrail_gap_threshold"] = float(
            (payload.get("drawdown_guardrail_gap_threshold") or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD) * 100.0
        )
        st.session_state["qvss_min_price_filter"] = float(payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE)
        st.session_state["qvss_min_history_months_filter"] = int(
            payload.get("min_history_months_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS
        )
        st.session_state["qvss_min_avg_dollar_volume_20d_m_filter"] = float(
            payload.get("min_avg_dollar_volume_20d_m_filter") or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
        st.session_state["qvss_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS)
        st.session_state["qvss_benchmark_contract"] = _benchmark_contract_value_to_label(
            payload.get("benchmark_contract") or STRICT_DEFAULT_BENCHMARK_CONTRACT
        )
        st.session_state["qvss_benchmark_ticker"] = str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
        st.session_state["qvss_guardrail_reference_ticker"] = str(payload.get("guardrail_reference_ticker") or "").strip().upper()
        st.session_state["qvss_promotion_min_benchmark_coverage"] = float(
            (payload.get("promotion_min_benchmark_coverage") or STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE) * 100.0
        )
        st.session_state["qvss_promotion_min_net_cagr_spread"] = float(
            (payload.get("promotion_min_net_cagr_spread") or STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD) * 100.0
        )
        st.session_state["qvss_promotion_min_liquidity_clean_coverage"] = float(
            (payload.get("promotion_min_liquidity_clean_coverage") or STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE) * 100.0
        )
        st.session_state["qvss_promotion_max_underperformance_share"] = float(
            (payload.get("promotion_max_underperformance_share") or STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE) * 100.0
        )
        st.session_state["qvss_promotion_min_worst_rolling_excess_return"] = float(
            (payload.get("promotion_min_worst_rolling_excess_return") or STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN) * 100.0
        )
        st.session_state["qvss_promotion_max_strategy_drawdown"] = float(
            (payload.get("promotion_max_strategy_drawdown") or STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN) * 100.0
        )
        st.session_state["qvss_promotion_max_drawdown_gap_vs_benchmark"] = float(
            (payload.get("promotion_max_drawdown_gap_vs_benchmark") or STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK) * 100.0
        )
    elif strategy_key == "quality_value_snapshot_strict_quarterly_prototype":
        st.session_state["qvqp_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in QUALITY_STRICT_PRESETS else "Manual"
        if st.session_state["qvqp_universe_mode"] == "Preset":
            st.session_state["qvqp_preset"] = preset_name
        else:
            st.session_state["qvqp_manual_tickers"] = tickers_text
        st.session_state["qvqp_start"] = start_date
        st.session_state["qvqp_end"] = end_date
        st.session_state["qvqp_top_n"] = int(payload.get("top") or 10)
        st.session_state["qvqp_timeframe"] = payload.get("timeframe") or "1d"
        st.session_state["qvqp_option"] = payload.get("option") or "month_end"
        st.session_state["qvqp_quality_factors"] = payload.get("quality_factors") or QUALITY_STRICT_DEFAULT_FACTORS
        st.session_state["qvqp_value_factors"] = payload.get("value_factors") or VALUE_STRICT_DEFAULT_FACTORS
        st.session_state["qvqp_universe_contract"] = next(
            (label for label, value in STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.items() if value == (payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE)),
            "Static Managed Research Universe",
        )
        st.session_state["qvqp_trend_filter_enabled"] = bool(payload.get("trend_filter_enabled", STRICT_TREND_FILTER_DEFAULT_ENABLED))
        st.session_state["qvqp_trend_filter_window"] = int(payload.get("trend_filter_window") or STRICT_TREND_FILTER_DEFAULT_WINDOW)
        st.session_state["qvqp_weighting_mode"] = _strict_weighting_mode_value_to_label(
            payload.get("weighting_mode") or STRICT_DEFAULT_WEIGHTING_MODE
        )
        st.session_state["qvqp_rejected_slot_handling_mode"] = _strict_rejection_handling_mode_value_to_label(
            resolve_strict_rejection_handling_mode(
                payload.get("rejected_slot_handling_mode"),
                rejected_slot_fill_enabled=bool(
                    payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
                ),
                partial_cash_retention_enabled=bool(
                    payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
                ),
            )
        )
        st.session_state["qvqp_rejected_slot_fill_enabled"] = bool(
            payload.get("rejected_slot_fill_enabled", STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED)
        )
        st.session_state["qvqp_partial_cash_retention_enabled"] = bool(
            payload.get("partial_cash_retention_enabled", STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED)
        )
        st.session_state["qvqp_risk_off_mode"] = _strict_risk_off_mode_value_to_label(
            payload.get("risk_off_mode") or STRICT_DEFAULT_RISK_OFF_MODE
        )
        st.session_state["qvqp_defensive_tickers"] = ",".join(
            list(payload.get("defensive_tickers") or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        )
        st.session_state["qvqp_market_regime_enabled"] = bool(payload.get("market_regime_enabled", STRICT_MARKET_REGIME_DEFAULT_ENABLED))
        st.session_state["qvqp_market_regime_window"] = int(payload.get("market_regime_window") or STRICT_MARKET_REGIME_DEFAULT_WINDOW)
        st.session_state["qvqp_market_regime_benchmark"] = payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK

    st.session_state.backtest_prefill_pending = False

def _render_equal_weight_form() -> None:
    st.markdown("### Equal Weight")
    st.caption("DB-backed equal-weight portfolio execution using the first public runtime wrapper.")
    _apply_single_strategy_prefill("equal_weight")

    _universe_mode, preset_name, tickers = _render_equal_weight_universe_inputs(
        key_prefix="eq",
    )

    with st.form("equal_weight_backtest_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="eq_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="eq_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="eq_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="eq_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=36,
                value=12,
                step=1,
                help=(
                    "`option=month_end` 기준으로 1=매월(대략 4주), 4=4개월마다, 12=연 1회입니다. "
                    "Equal Weight sample 기본값은 12입니다."
                ),
                key="eq_rebalance_interval",
            )

        submitted = st.form_submit_button("Run Equal Weight Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []

    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "equal_weight",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "rebalance_interval": int(rebalance_interval),
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Equal Weight")

def _render_gtaa_form() -> None:
    st.markdown("### GTAA")
    st.caption("DB-backed GTAA execution using the second public runtime wrapper.")
    _apply_single_strategy_prefill("gtaa")

    _universe_mode, preset_name, tickers = _render_gtaa_universe_inputs(
        key_prefix="gtaa",
    )

    with st.form("gtaa_backtest_form", clear_on_submit=False):

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="gtaa_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="gtaa_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="gtaa_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="gtaa_option")
            top = st.number_input(
                "Top Assets",
                min_value=1,
                max_value=12,
                value=3,
                step=1,
                help="GTAA는 평균 score 상위 자산을 선택합니다.",
                key="gtaa_top",
            )
            interval = st.number_input(
                "Signal Interval (months)",
                min_value=1,
                max_value=12,
                value=GTAA_DEFAULT_SIGNAL_INTERVAL,
                step=1,
                help="현재 기본값은 1입니다. 1이면 매월, 2면 격월로 신호를 계산합니다.",
                key="gtaa_interval",
            )
            score_lookback_months, score_weights = _render_gtaa_score_weight_inputs(key_prefix="gtaa")
            _render_advanced_group_caption("핵심 실행 계약은 위에 두고, 추가 overlay / 실전 계약 / guardrail은 아래 그룹으로 분리했습니다.")
            with st.expander("Risk-Off Overlay", expanded=False):
                risk_off_contract = _render_gtaa_risk_off_contract_inputs(key_prefix="gtaa")
            with st.expander("Real-Money Contract", expanded=False):
                (
                    min_price_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_etf_aum_b,
                    promotion_max_bid_ask_spread_pct,
                ) = _render_etf_real_money_inputs(
                    key_prefix="gtaa",
                )
            with st.expander("ETF Guardrails", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_etf_guardrail_inputs(
                    key_prefix="gtaa",
                    label_prefix="GTAA ",
                )

        submitted = st.form_submit_button("Run GTAA Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not score_lookback_months:
        validation_errors.append("GTAA Score Horizons must contain at least one lookback window.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "gtaa",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top),
        "interval": int(interval),
        "score_lookback_months": list(score_lookback_months),
        "score_return_columns": [_gtaa_return_col_from_months(months) for months in score_lookback_months],
        "score_weights": score_weights,
        "trend_filter_window": int(risk_off_contract["trend_filter_window"]),
        "risk_off_mode": risk_off_contract["risk_off_mode"],
        "defensive_tickers": list(risk_off_contract["defensive_tickers"]),
        "market_regime_enabled": bool(risk_off_contract["market_regime_enabled"]),
        "market_regime_window": int(risk_off_contract["market_regime_window"]),
        "market_regime_benchmark": risk_off_contract["market_regime_benchmark"],
        "crash_guardrail_enabled": bool(risk_off_contract["crash_guardrail_enabled"]),
        "crash_guardrail_drawdown_threshold": float(risk_off_contract["crash_guardrail_drawdown_threshold"]),
        "crash_guardrail_lookback_months": int(risk_off_contract["crash_guardrail_lookback_months"]),
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="GTAA")

def _render_global_relative_strength_form() -> None:
    st.markdown("### Global Relative Strength")
    st.caption(
        "Phase 24 신규 ETF 전략입니다. 여러 자산군 ETF 중 최근 상대강도가 좋은 자산을 고르고, "
        "추세가 약한 자산은 cash ticker로 피하는 구조입니다."
    )
    _apply_single_strategy_prefill("global_relative_strength")

    _universe_mode, preset_name, tickers = _render_global_relative_strength_universe_inputs(
        key_prefix="grs",
    )
    preflight_tickers = list(tickers)
    cash_for_preflight = str(
        st.session_state.get("grs_cash_ticker", GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER) or ""
    ).strip().upper()
    benchmark_for_preflight = str(
        st.session_state.get("grs_benchmark_ticker", ETF_REAL_MONEY_DEFAULT_BENCHMARK) or ""
    ).strip().upper()
    for extra_ticker in [cash_for_preflight, benchmark_for_preflight]:
        if extra_ticker and extra_ticker not in preflight_tickers:
            preflight_tickers.append(extra_ticker)
    _render_strict_price_freshness_preflight(
        tickers=preflight_tickers,
        end_value=st.session_state.get("grs_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("grs_timeframe", "1d"),
        strategy_label="Global Relative Strength",
    )

    with st.form("global_relative_strength_backtest_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="grs_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="grs_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="grs_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="grs_option")
            cash_ticker = st.text_input(
                "Cash / Defensive Ticker",
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
                help="선택된 ETF가 200일선 아래에 있으면 이 ticker로 대피합니다. 기본값은 BIL입니다.",
                key="grs_cash_ticker",
            )
            top = st.number_input(
                "Top Assets",
                min_value=1,
                max_value=12,
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
                step=1,
                help="상대강도 점수가 높은 ETF를 몇 개까지 보유할지 정합니다.",
                key="grs_top",
            )
            interval = st.number_input(
                "Signal Interval (months)",
                min_value=1,
                max_value=12,
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
                step=1,
                help="1이면 매월, 3이면 3개월마다 신호를 갱신합니다.",
                key="grs_interval",
            )
            score_lookback_months, score_weights = _render_global_relative_strength_score_weight_inputs(
                key_prefix="grs"
            )
            trend_filter_window = st.number_input(
                "Trend Filter Window",
                min_value=20,
                max_value=400,
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
                step=10,
                help="가격이 이 이동평균 아래에 있으면 cash ticker로 대피합니다.",
                key="grs_trend_filter_window",
            )
            with st.expander("Real-Money Contract", expanded=False):
                (
                    min_price_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_etf_aum_b,
                    promotion_max_bid_ask_spread_pct,
                ) = _render_etf_real_money_inputs(
                    key_prefix="grs",
                )

        submitted = st.form_submit_button("Run Global Relative Strength Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not score_lookback_months:
        validation_errors.append("Score Horizons must contain at least one lookback window.")
    normalized_cash_ticker = str(cash_ticker or "").strip().upper()
    if not normalized_cash_ticker:
        validation_errors.append("Cash / Defensive Ticker is required.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "global_relative_strength",
        "tickers": tickers,
        "cash_ticker": normalized_cash_ticker,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top),
        "interval": int(interval),
        "score_lookback_months": list(score_lookback_months),
        "score_return_columns": [_gtaa_return_col_from_months(months) for months in score_lookback_months],
        "score_weights": score_weights,
        "trend_filter_enabled": True,
        "trend_filter_window": int(trend_filter_window),
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Global Relative Strength")

def _render_risk_parity_form() -> None:
    st.markdown("### Risk Parity Trend")
    st.caption("DB-backed risk-parity trend execution using the third public runtime wrapper.")
    _apply_single_strategy_prefill("risk_parity_trend")

    with st.form("risk_parity_backtest_form", clear_on_submit=False):
        universe_mode = st.radio(
            "Universe Mode",
            options=["Preset", "Manual"],
            horizontal=True,
            help="Risk Parity Trend도 기본적으로 preset universe 사용을 권장합니다.",
            key="rp_universe_mode",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "Preset",
                options=list(RISK_PARITY_PRESETS.keys()),
                index=0,
                key="rp_preset",
            )
            tickers = RISK_PARITY_PRESETS[preset_name]
            st.caption(f"Selected tickers: `{', '.join(tickers)}`")
        else:
            manual_tickers = st.text_input(
                "Tickers",
                value="SPY,TLT,GLD,IEF,LQD",
                help="Comma-separated tickers. Example: SPY,TLT,GLD,IEF,LQD",
                key="rp_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="rp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="rp_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="rp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="rp_option")
            rebalance_interval = int(
                st.number_input(
                    "Rebalance Interval (months)",
                    min_value=1,
                    max_value=12,
                    value=1,
                    step=1,
                    key="rp_rebalance_interval",
                )
            )
            vol_window = int(
                st.number_input(
                    "Volatility Window (months)",
                    min_value=1,
                    max_value=24,
                    value=6,
                    step=1,
                    key="rp_vol_window",
                )
            )
            _render_advanced_group_caption("핵심 실행 계약은 위에 두고, 실전 계약과 guardrail은 아래 그룹으로 분리했습니다.")
            with st.expander("Real-Money Contract", expanded=False):
                (
                    min_price_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_etf_aum_b,
                    promotion_max_bid_ask_spread_pct,
                ) = _render_etf_real_money_inputs(
                    key_prefix="rp",
                )
            with st.expander("ETF Guardrails", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_etf_guardrail_inputs(
                    key_prefix="rp",
                    label_prefix="Risk Parity ",
                )

        submitted = st.form_submit_button("Run Risk Parity Trend Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "risk_parity_trend",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "rebalance_interval": int(rebalance_interval),
        "vol_window": int(vol_window),
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Risk Parity Trend")

def _render_dual_momentum_form() -> None:
    st.markdown("### Dual Momentum")
    st.caption("DB-backed dual momentum execution using the fourth public runtime wrapper.")
    _apply_single_strategy_prefill("dual_momentum")

    with st.form("dual_momentum_backtest_form", clear_on_submit=False):
        universe_mode = st.radio(
            "Universe Mode",
            options=["Preset", "Manual"],
            horizontal=True,
            help="Dual Momentum도 기본 preset universe를 기준으로 시작하는 편이 안전합니다.",
            key="dm_universe_mode",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "Preset",
                options=list(DUAL_MOMENTUM_PRESETS.keys()),
                index=0,
                key="dm_preset",
            )
            tickers = DUAL_MOMENTUM_PRESETS[preset_name]
            st.caption(f"Selected tickers: `{', '.join(tickers)}`")
        else:
            manual_tickers = st.text_input(
                "Tickers",
                value="QQQ,SPY,IWM,SOXX,BIL",
                help="Comma-separated tickers. Example: QQQ,SPY,IWM,SOXX,BIL",
                key="dm_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="dm_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="dm_end")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="dm_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="dm_option")
            top = int(
                st.number_input(
                    "Top Assets",
                    min_value=1,
                    max_value=5,
                    value=1,
                    step=1,
                    key="dm_top",
                )
            )
            rebalance_interval = int(
                st.number_input(
                    "Rebalance Interval (months)",
                    min_value=1,
                    max_value=12,
                    value=1,
                    step=1,
                    key="dm_rebalance_interval",
                )
            )
            _render_advanced_group_caption("핵심 실행 계약은 위에 두고, 실전 계약과 guardrail은 아래 그룹으로 분리했습니다.")
            with st.expander("Real-Money Contract", expanded=False):
                (
                    min_price_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_etf_aum_b,
                    promotion_max_bid_ask_spread_pct,
                ) = _render_etf_real_money_inputs(
                    key_prefix="dm",
                )
            with st.expander("ETF Guardrails", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_etf_guardrail_inputs(
                    key_prefix="dm",
                    label_prefix="Dual Momentum ",
                )

        submitted = st.form_submit_button("Run Dual Momentum Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "dual_momentum",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top),
        "rebalance_interval": int(rebalance_interval),
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Dual Momentum")

def _render_quality_snapshot_form() -> None:
    st.markdown("### Quality Snapshot")
    st.caption("Research-oriented quality snapshot strategy using broad-research factor snapshots. This first pass ranks quality factors and holds top names equally between monthly rebalances.")
    _render_quality_family_guide("quality_broad")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Weekly Fundamental Refresh`로 **`nyse_fundamentals` + `nyse_factors`**를 채워야 합니다.\n"
            "- 현재 공개 버전은 **`Extended Statement Refresh`가 필수는 아닙니다**. 이 전략은 detailed statement ledger를 직접 읽지 않습니다.\n"
            "- 첫 공개 버전은 **stock-oriented** 입니다. ETF 위주 유니버스는 quality factor snapshot이 비거나 의미가 약할 수 있습니다.\n"
            "- 현재 `Factor Frequency`는 `annual`만 지원하므로, 같은 universe에 대해 `Weekly Fundamental Refresh (annual)`를 맞춰서 돌리는 편이 가장 자연스럽습니다."
        )
        st.caption("Current public mode: `broad_research` (research-oriented snapshot, not strict PIT)")
    _apply_single_strategy_prefill("quality_snapshot")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="첫 factor strategy는 stock-only quality universe를 기준으로 시작하는 편이 안전합니다.",
        key="qs_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []

    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_BROAD_PRESETS.keys()),
            index=0,
            key="qs_preset",
        )
        tickers = QUALITY_BROAD_PRESETS[preset_name]
        _render_ticker_preview(tickers)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="Comma-separated stock tickers. Example: AAPL,MSFT,GOOG",
            key="qs_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    with st.form("quality_snapshot_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qs_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qs_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="Quality score 상위 종목 수입니다.",
                key="qs_top_n",
            )

        st.caption("Hidden defaults in this first pass: `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qs_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qs_option")
            factor_freq = st.selectbox(
                "Factor Frequency",
                options=["annual"],
                index=0,
                key="qs_factor_freq",
                help="첫 버전은 annual quality snapshot만 지원합니다.",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                default=["roe", "gross_margin", "operating_margin", "debt_ratio"],
                key="qs_quality_factors",
                help="높을수록 좋은 factor와 낮을수록 좋은 factor를 내부 score rule로 함께 처리합니다.",
            )
            snapshot_mode = st.selectbox(
                "Snapshot Mode",
                options=["broad_research"],
                index=0,
                key="qs_snapshot_mode",
                help="첫 공개 버전은 broad-research snapshot을 사용합니다. strict PIT mode는 후속 단계로 남겨둡니다.",
            )

        submitted = st.form_submit_button("Run Quality Snapshot Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "factor_freq": factor_freq,
        "rebalance_freq": "monthly",
        "snapshot_mode": snapshot_mode,
        "quality_factors": quality_factors,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot")

def _render_quality_snapshot_strict_annual_form() -> None:
    st.markdown("### Quality Snapshot (Strict Annual)")
    st.caption("Strict annual statement-driven quality strategy. This public candidate ranks annual statement shadow factors, then by default holds the top names equally between monthly rebalances.")
    _render_quality_family_guide("quality_strict")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`를 **annual** 기준으로 먼저 채워야 합니다.\n"
            "- 이 경로는 현재 **strict annual statement shadow factors**를 사용합니다.\n"
            "- wider annual coverage 검증은 **US / EDGAR-friendly top-300 stock universe** 기준으로 확인되었습니다.\n"
            "- 현재는 stock-oriented path이며, ETF 중심 universe에는 적합하지 않습니다."
        )
        st.caption("Current public candidate mode: `strict_statement_annual` + `shadow_factors`")
    _apply_single_strategy_prefill("quality_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="Single Strategy에서는 annual statement coverage가 검증된 미국 주식 preset을 기본값으로 사용합니다.",
        key="qss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="qss_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qss_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qss_timeframe", "1d"),
        strategy_label="Quality Snapshot (Strict Annual)",
    )

    with st.form("quality_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qss_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="strict annual quality 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement snapshots`, `monthly rebalance`, `equal-weight holding by default`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qss_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qss_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict에서만 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_annual_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qss_quality_factors",
                help="기본은 coverage-first 팩터 조합입니다. 필요하면 예전 quality factor도 다시 포함할 수 있습니다.",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qss_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qss",
                    label_prefix="",
                )
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality",
                )
            with st.expander("Real-Money Contract", expanded=False):
                (
                    benchmark_contract,
                    min_price_filter,
                    min_history_months_filter,
                    min_avg_dollar_volume_20d_m_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_benchmark_coverage,
                    promotion_min_net_cagr_spread,
                    promotion_min_liquidity_clean_coverage,
                    promotion_max_underperformance_share,
                    promotion_min_worst_rolling_excess_return,
                    promotion_max_strategy_drawdown,
                    promotion_max_drawdown_gap_vs_benchmark,
                ) = _render_strict_annual_real_money_inputs(
                    key_prefix="qss",
                )
            with st.expander("Guardrails", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                ) = _render_underperformance_guardrail_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality ",
                )
                (
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_drawdown_guardrail_inputs(
                    key_prefix="qss",
                    label_prefix="Strict Annual Quality ",
                )
                guardrail_reference_ticker = _render_guardrail_reference_ticker_input(
                    key_prefix="qss",
                    benchmark_ticker=benchmark_ticker,
                    default_guardrail_reference_ticker=st.session_state.get("qss_guardrail_reference_ticker"),
                    underperformance_guardrail_enabled=underperformance_guardrail_enabled,
                    drawdown_guardrail_enabled=drawdown_guardrail_enabled,
                )

        submitted = st.form_submit_button("Run Strict Annual Quality Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "quality_factors": quality_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "guardrail_reference_ticker": guardrail_reference_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot (Strict Annual)")

def _render_quality_snapshot_strict_quarterly_prototype_form() -> None:
    st.markdown("### Quality Snapshot (Strict Quarterly Prototype)")
    st.caption("Research-only quarterly strict quality strategy. This Phase 7 path ranks quarterly statement shadow factors and keeps the top names equally between monthly rebalances.")
    _render_strict_quarterly_productionization_note(family_label="Quality Snapshot (Strict Quarterly Prototype)")
    _apply_single_strategy_prefill("quality_snapshot_strict_quarterly_prototype")

    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`와 statement shadow factor rebuild가 **quarterly** 기준으로 준비되어 있어야 합니다.\n"
            "- 이 경로는 현재 **research-only quarterly strict prototype** 입니다.\n"
            "- annual strict public family와 달리, coverage / freshness / runtime 검증이 이번 Phase 7에서 함께 진행됩니다."
        )
        st.caption("Current prototype mode: `strict_statement_quarterly` + `shadow_factors` + `research_only`")
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "Phase 7 first pass 이후 `US Statement Coverage 100` 기본 preset은 다시 2016 부근부터 열리지만, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦을 수 있습니다."
        )

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly prototype first pass는 검증 비용을 낮추기 위해 `US Statement Coverage 100`을 기본 preset으로 둡니다.",
        key="qsqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="qsqp_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qsqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qsqp_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qsqp_timeframe", "1d"),
        strategy_label="Quality Snapshot (Strict Quarterly Prototype)",
    )
    _render_statement_shadow_coverage_preview(
        tickers=tickers,
        freq="quarterly",
        strategy_label="Quality Snapshot (Strict Quarterly Prototype)",
    )

    with st.form("quality_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qsqp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qsqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=20,
                value=2,
                step=1,
                help="strict quarterly quality 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qsqp_top_n",
            )

        st.caption("Research-only defaults in this first pass: `quarterly statement snapshots`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qsqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qsqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qsqp_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qsqp_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
                statement_freq="quarterly",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qsqp_quality_factors",
                help="first-pass quarterly prototype도 quality strict와 같은 coverage-first 팩터 조합을 기본값으로 사용합니다.",
            )
            _render_advanced_group_caption(
                "Phase 23에서는 quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qsqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qsqp_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality ",
                )
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qsqp",
                    label_prefix="Strict Quarterly Quality",
                )
                st.caption(
                    "Phase 23 첫 구현 단위에서는 이 contract들을 quarterly payload와 replay surface에 연결합니다. "
                    "Real-Money Contract와 Promotion 판단은 아직 annual strict 중심으로 유지합니다."
                )

        submitted = st.form_submit_button("Run Strict Quarterly Quality Prototype", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "quality_factors": quality_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality Snapshot (Strict Quarterly Prototype)")

def _render_value_snapshot_strict_quarterly_prototype_form() -> None:
    st.markdown("### Value Snapshot (Strict Quarterly Prototype)")
    st.caption(
        "Research-only quarterly strict value strategy. This Phase 8 path ranks quarterly statement shadow value factors and holds the cheapest names equally between monthly rebalances."
    )
    _render_strict_quarterly_productionization_note(family_label="Value Snapshot (Strict Quarterly Prototype)")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`와 statement shadow factor rebuild가 **quarterly** 기준으로 준비되어 있어야 합니다.\n"
            "- 이 경로는 현재 **research-only quarterly strict value prototype** 입니다.\n"
            "- annual strict value public candidate와 달리, coverage / freshness / interpretation parity를 이번 Phase 8에서 함께 검증합니다."
        )
        st.caption("Current prototype mode: `strict_statement_quarterly` + `shadow_factors` + `research_only`")
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "`US Statement Coverage 100` 기본 preset은 검증용 anchor일 뿐이고, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦게 열릴 수 있습니다."
        )
    _apply_single_strategy_prefill("value_snapshot_strict_quarterly_prototype")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly strict value prototype first pass는 검증 비용을 낮추기 위해 `US Statement Coverage 100`을 기본 preset으로 둡니다.",
        key="vsqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(VALUE_STRICT_PRESETS.keys()),
            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="vsqp_preset",
        )
        tickers = VALUE_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="vsqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("vsqp_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("vsqp_timeframe", "1d"),
        strategy_label="Value Snapshot (Strict Quarterly Prototype)",
    )
    _render_statement_shadow_coverage_preview(
        tickers=tickers,
        freq="quarterly",
        strategy_label="Value Snapshot (Strict Quarterly Prototype)",
    )

    with st.form("value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="vsqp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="vsqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                help="strict quarterly value 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="vsqp_top_n",
            )

        st.caption("Research-only defaults in this first pass: `quarterly statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="vsqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="vsqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="vsqp_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="vsqp_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
                statement_freq="quarterly",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vsqp_value_factors",
                help="quarterly prototype도 yield / book-to-market 중심의 coverage-first 기본 조합을 사용합니다.",
            )
            _render_advanced_group_caption(
                "Phase 23에서는 quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="vsqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="vsqp_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value ",
                )
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="vsqp",
                    label_prefix="Strict Quarterly Value",
                )
                st.caption(
                    "Phase 23 첫 구현 단위에서는 이 contract들을 quarterly payload와 replay surface에 연결합니다. "
                    "Real-Money Contract와 Promotion 판단은 아직 annual strict 중심으로 유지합니다."
                )

        submitted = st.form_submit_button("Run Strict Quarterly Value Prototype", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "value_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "snapshot_source": "shadow_factors",
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Value Snapshot (Strict Quarterly Prototype)")

def _render_value_snapshot_strict_annual_form() -> None:
    st.markdown("### Value Snapshot (Strict Annual)")
    st.caption("Strict annual statement-driven value strategy. This public candidate ranks precomputed annual statement shadow factors and by default holds the cheapest names equally between monthly rebalances.")
    _render_quality_family_guide("value_strict")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`를 **annual** 기준으로 먼저 채워야 합니다.\n"
            "- 현재 value strict path는 **statement shadow factors**를 사용합니다.\n"
            "- valuation 계열은 statement + nearest-period shares fallback hybrid 의미를 가질 수 있습니다.\n"
            "- wider annual coverage 검증은 **US / EDGAR-friendly top-300 stock universe** 기준으로 확인되었습니다."
        )
        st.caption("Current public candidate mode: `strict_statement_annual` + `shadow_factors`")
    _apply_single_strategy_prefill("value_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="strict annual value도 annual coverage가 확인된 preset을 기본값으로 사용합니다.",
        key="vss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(VALUE_STRICT_PRESETS.keys()),
            index=list(VALUE_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="vss_preset",
        )
        tickers = VALUE_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="vss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("vss_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("vss_timeframe", "1d"),
        strategy_label="Value Snapshot (Strict Annual)",
    )

    with st.form("value_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="vss_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="vss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                help="strict annual value 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="vss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement shadow factors`, `monthly rebalance`, `equal-weight holding by default`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="vss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="vss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="vss_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="vss_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict에서만 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_annual_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="vss_value_factors",
                help="높을수록 좋은 yield / book-to-market 계열과 낮을수록 좋은 inverse multiple 계열을 함께 지원합니다.",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="vss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="vss_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="vss",
                    label_prefix="",
                )
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value",
                )
            with st.expander("Real-Money Contract", expanded=False):
                (
                    benchmark_contract,
                    min_price_filter,
                    min_history_months_filter,
                    min_avg_dollar_volume_20d_m_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_benchmark_coverage,
                    promotion_min_net_cagr_spread,
                    promotion_min_liquidity_clean_coverage,
                    promotion_max_underperformance_share,
                    promotion_min_worst_rolling_excess_return,
                    promotion_max_strategy_drawdown,
                    promotion_max_drawdown_gap_vs_benchmark,
                ) = _render_strict_annual_real_money_inputs(
                    key_prefix="vss",
                )
            with st.expander("Guardrails", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                ) = _render_underperformance_guardrail_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value ",
                )
                (
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_drawdown_guardrail_inputs(
                    key_prefix="vss",
                    label_prefix="Strict Annual Value ",
                )
                guardrail_reference_ticker = _render_guardrail_reference_ticker_input(
                    key_prefix="vss",
                    benchmark_ticker=benchmark_ticker,
                    default_guardrail_reference_ticker=st.session_state.get("vss_guardrail_reference_ticker"),
                    underperformance_guardrail_enabled=underperformance_guardrail_enabled,
                    drawdown_guardrail_enabled=drawdown_guardrail_enabled,
                )

        submitted = st.form_submit_button("Run Strict Annual Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "value_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "snapshot_source": "shadow_factors",
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "guardrail_reference_ticker": guardrail_reference_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Value Snapshot (Strict Annual)")

def _render_quality_value_snapshot_strict_quarterly_prototype_form() -> None:
    st.markdown("### Quality + Value Snapshot (Strict Quarterly Prototype)")
    st.caption(
        "Research-only quarterly strict multi-factor strategy. This Phase 8 path blends quarterly quality and value shadow factors, then holds the combined top names equally between monthly rebalances."
    )
    _render_strict_quarterly_productionization_note(family_label="Quality + Value Snapshot (Strict Quarterly Prototype)")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`와 statement shadow factor rebuild가 **quarterly** 기준으로 준비되어 있어야 합니다.\n"
            "- 이 경로는 현재 **research-only quarterly strict multi-factor prototype** 입니다.\n"
            "- quality + value availability가 동시에 필요하므로 quarterly quality/value 단독 경로보다 usable history가 조금 더 보수적으로 보일 수 있습니다."
        )
        st.caption("Current prototype mode: `strict_statement_quarterly` + `shadow_factors` + `quality_value_blend` + `research_only`")
        st.caption(
            "주의: 현재 DB의 quarterly shadow coverage 상태에 따라 실제 투자 구간이 요청한 시작일보다 늦게 열릴 수 있습니다. "
            "`US Statement Coverage 100` 기본 preset은 검증 anchor이고, 다른 universe나 수동 ticker 조합은 coverage 상태에 따라 더 늦게 열릴 수 있습니다."
        )
    _apply_single_strategy_prefill("quality_value_snapshot_strict_quarterly_prototype")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="quarterly strict multi-factor prototype first pass는 검증 비용을 낮추기 위해 `US Statement Coverage 100`을 기본 preset으로 둡니다.",
        key="qvqp_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET),
            key="qvqp_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qvqp_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qvqp_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qvqp_timeframe", "1d"),
        strategy_label="Quality + Value Snapshot (Strict Quarterly Prototype)",
    )
    _render_statement_shadow_coverage_preview(
        tickers=tickers,
        freq="quarterly",
        strategy_label="Quality + Value Snapshot (Strict Quarterly Prototype)",
    )

    with st.form("quality_value_snapshot_strict_quarterly_prototype_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qvqp_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qvqp_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                help="strict quarterly multi-factor 종합 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qvqp_top_n",
            )

        st.caption("Research-only defaults in this first pass: `quarterly statement shadow factors`, `monthly rebalance`, `equal-weight holding`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qvqp_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qvqp_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, quarterly snapshot 자체는 가장 최근 usable filing 기준으로 따라갑니다.",
                key="qvqp_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qvqp_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, quarterly strict에서도 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_dynamic_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
                statement_freq="quarterly",
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvqp_quality_factors",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvqp_value_factors",
            )
            _render_advanced_group_caption(
                "Phase 23에서는 quarterly도 annual strict처럼 overlay와 portfolio handling contract를 같은 payload에 저장합니다."
            )
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qvqp_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qvqp_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor ",
                )
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qvqp",
                    label_prefix="Strict Quarterly Multi-Factor",
                )
                st.caption(
                    "Phase 23 첫 구현 단위에서는 이 contract들을 quarterly payload와 replay surface에 연결합니다. "
                    "Real-Money Contract와 Promotion 판단은 아직 annual strict 중심으로 유지합니다."
                )

        submitted = st.form_submit_button("Run Strict Quarterly Quality + Value Prototype", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_value_snapshot_strict_quarterly_prototype",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "quarterly",
        "snapshot_mode": "strict_statement_quarterly",
        "snapshot_source": "shadow_factors",
        "quality_factors": quality_factors,
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality + Value Snapshot (Strict Quarterly Prototype)")

def _render_quality_value_snapshot_strict_annual_form() -> None:
    st.markdown("### Quality + Value Snapshot (Strict Annual)")
    st.caption(
        "Strict annual multi-factor strategy. This public candidate blends coverage-first quality signals "
        "with annual statement-driven valuation factors, then by default holds the combined top names equally between monthly rebalances."
    )
    _render_quality_family_guide("quality_value_strict")
    with st.expander("Data Requirements", expanded=False):
        st.markdown(
            "- `Daily Market Update` 또는 OHLCV 수집으로 **가격 데이터**를 먼저 채워야 합니다.\n"
            "- `Extended Statement Refresh`를 **annual** 기준으로 먼저 채워야 합니다.\n"
            "- 현재 multi-factor strict path는 **statement shadow factors**를 사용합니다.\n"
            "- quality + value factor availability가 동시에 필요하므로 usable history는 quality strict보다 조금 더 보수적으로 보셔야 합니다.\n"
            "- wider annual coverage 검증은 **US / EDGAR-friendly stock universe** 기준으로 진행합니다."
        )
        st.caption("Current public candidate mode: `strict_statement_annual` + `shadow_factors` + `quality_value_blend`")
    _apply_single_strategy_prefill("quality_value_snapshot_strict_annual")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Preset", "Manual"],
        horizontal=True,
        help="strict annual multi-factor도 annual coverage가 검증된 preset을 기본값으로 사용합니다.",
        key="qvss_universe_mode",
    )

    preset_name = None
    tickers: list[str] = []
    if universe_mode == "Preset":
        preset_name = st.selectbox(
            "Preset",
            options=list(QUALITY_STRICT_PRESETS.keys()),
            index=list(QUALITY_STRICT_PRESETS.keys()).index(STRICT_ANNUAL_SINGLE_DEFAULT_PRESET),
            key="qvss_preset",
        )
        tickers = QUALITY_STRICT_PRESETS[preset_name]
        _render_ticker_preview(tickers)
        _render_historical_universe_caption()
        _render_strict_preset_status_note(preset_name)
    else:
        manual_tickers = st.text_input(
            "Tickers",
            value="AAPL,MSFT,GOOG",
            help="쉼표로 구분한 주식 티커를 입력합니다. 예: AAPL,MSFT,GOOG",
            key="qvss_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
        _render_ticker_preview(tickers)

    _render_strict_price_freshness_preflight(
        tickers=tickers,
        end_value=st.session_state.get("qvss_end", DEFAULT_BACKTEST_END_DATE),
        timeframe=st.session_state.get("qvss_timeframe", "1d"),
        strategy_label="Quality + Value Snapshot (Strict Annual)",
    )

    with st.form("quality_value_snapshot_strict_annual_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1), key="qvss_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="qvss_end")
        with col3:
            top_n = st.number_input(
                "Top N",
                min_value=1,
                max_value=30,
                value=10,
                step=1,
                help="strict annual multi-factor 종합 점수 기준으로 상위 몇 개 종목을 선택할지 정합니다.",
                key="qvss_top_n",
            )

        st.caption("Hidden defaults in this first pass: `annual statement shadow factors`, `monthly rebalance`, `equal-weight holding by default`.")

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="qvss_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="qvss_option")
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=12,
                value=1,
                step=1,
                help="기본은 매월 리밸런싱(1)이며, 연구 목적이면 몇 달 간격으로 건너뛸 수도 있습니다.",
                key="qvss_rebalance_interval",
            )
            universe_contract_label = st.selectbox(
                "Universe Contract",
                options=list(STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS.keys()),
                index=0,
                key="qvss_universe_contract",
                help="Static은 현재 managed preset을 고정해서 사용합니다. Dynamic PIT는 Phase 10 first pass로, annual strict에서만 각 리밸런싱 날짜 기준 모집군을 다시 계산합니다.",
            )
            universe_contract = STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS[universe_contract_label]
            dynamic_candidate_tickers, dynamic_target_size = _render_strict_annual_universe_contract_note(
                universe_contract=universe_contract,
                tickers=tickers,
                preset_name=preset_name,
            )
            quality_factors = st.multiselect(
                "Quality Factors",
                options=QUALITY_STRICT_FACTOR_OPTIONS,
                default=QUALITY_STRICT_DEFAULT_FACTORS,
                key="qvss_quality_factors",
            )
            value_factors = st.multiselect(
                "Value Factors",
                options=VALUE_STRICT_FACTOR_OPTIONS,
                default=VALUE_STRICT_DEFAULT_FACTORS,
                key="qvss_value_factors",
            )
            _render_advanced_group_caption("핵심 factor / universe 계약은 위에 두고, overlay와 포트폴리오 처리 규칙은 아래 펼쳐보기로 묶었습니다.")
            with st.expander("Overlay", expanded=False):
                _render_strict_overlay_section_intro()
                trend_title_col, trend_help_col = st.columns([0.92, 0.08], gap="small")
                with trend_title_col:
                    st.markdown("##### Trend Filter Overlay")
                with trend_help_col:
                    _render_trend_filter_help_popover()
                trend_filter_enabled = st.checkbox(
                    "Enable",
                    value=STRICT_TREND_FILTER_DEFAULT_ENABLED,
                    key="qvss_trend_filter_enabled",
                )
                trend_filter_window = int(
                    st.number_input(
                        "Trend Filter Window",
                        min_value=20,
                        max_value=400,
                        value=STRICT_TREND_FILTER_DEFAULT_WINDOW,
                        step=10,
                        key="qvss_trend_filter_window",
                    )
                )
                market_regime_enabled, market_regime_window, market_regime_benchmark = _render_market_regime_overlay_inputs(
                    key_prefix="qvss",
                    label_prefix="",
                )
            with st.expander("Portfolio Handling & Defensive Rules", expanded=False):
                _render_strict_portfolio_handling_contracts_intro()
                weighting_mode = _render_strict_weighting_contract_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor",
                )
                rejected_slot_handling_mode = _render_strict_rejected_slot_handling_contract_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor",
                )
                rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
                    rejected_slot_handling_mode
                )
                risk_off_mode, defensive_tickers = _render_strict_defensive_sleeve_contract_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor",
                )
            with st.expander("Real-Money Contract", expanded=False):
                (
                    benchmark_contract,
                    min_price_filter,
                    min_history_months_filter,
                    min_avg_dollar_volume_20d_m_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_benchmark_coverage,
                    promotion_min_net_cagr_spread,
                    promotion_min_liquidity_clean_coverage,
                    promotion_max_underperformance_share,
                    promotion_min_worst_rolling_excess_return,
                    promotion_max_strategy_drawdown,
                    promotion_max_drawdown_gap_vs_benchmark,
                ) = _render_strict_annual_real_money_inputs(
                    key_prefix="qvss",
                )
            with st.expander("Guardrails", expanded=False):
                (
                    underperformance_guardrail_enabled,
                    underperformance_guardrail_window_months,
                    underperformance_guardrail_threshold,
                ) = _render_underperformance_guardrail_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor ",
                )
                (
                    drawdown_guardrail_enabled,
                    drawdown_guardrail_window_months,
                    drawdown_guardrail_strategy_threshold,
                    drawdown_guardrail_gap_threshold,
                ) = _render_drawdown_guardrail_inputs(
                    key_prefix="qvss",
                    label_prefix="Strict Annual Multi-Factor ",
                )
                guardrail_reference_ticker = _render_guardrail_reference_ticker_input(
                    key_prefix="qvss",
                    benchmark_ticker=benchmark_ticker,
                    default_guardrail_reference_ticker=st.session_state.get("qvss_guardrail_reference_ticker"),
                    underperformance_guardrail_enabled=underperformance_guardrail_enabled,
                    drawdown_guardrail_enabled=drawdown_guardrail_enabled,
                )

        submitted = st.form_submit_button("Run Strict Annual Quality + Value Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if not quality_factors:
        validation_errors.append("Select at least one quality factor.")
    if not value_factors:
        validation_errors.append("Select at least one value factor.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "quality_value_snapshot_strict_annual",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "top": int(top_n),
        "rebalance_interval": int(rebalance_interval),
        "factor_freq": "annual",
        "snapshot_mode": "strict_statement_annual",
        "snapshot_source": "shadow_factors",
        "quality_factors": quality_factors,
        "value_factors": value_factors,
        "trend_filter_enabled": bool(trend_filter_enabled),
        "trend_filter_window": int(trend_filter_window),
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": bool(rejected_slot_fill_enabled),
        "partial_cash_retention_enabled": bool(partial_cash_retention_enabled),
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": defensive_tickers,
        "market_regime_enabled": bool(market_regime_enabled),
        "market_regime_window": int(market_regime_window),
        "market_regime_benchmark": market_regime_benchmark,
        "min_price_filter": float(min_price_filter),
        "min_history_months_filter": int(min_history_months_filter),
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_contract": benchmark_contract,
        "benchmark_ticker": benchmark_ticker,
        "guardrail_reference_ticker": guardrail_reference_ticker,
        "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
        "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
        "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
        "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
        "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
        "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
        "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
        "underperformance_guardrail_enabled": bool(underperformance_guardrail_enabled),
        "underperformance_guardrail_window_months": int(underperformance_guardrail_window_months),
        "underperformance_guardrail_threshold": float(underperformance_guardrail_threshold),
        "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
        "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
        "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
        "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
        "universe_contract": universe_contract,
        "dynamic_candidate_tickers": dynamic_candidate_tickers,
        "dynamic_target_size": dynamic_target_size,
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Quality + Value Snapshot (Strict Annual)")

__all__ = [name for name in globals() if not name.startswith("__")]
