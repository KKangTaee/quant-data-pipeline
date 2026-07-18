from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run

def _render_single_strategy_family_form(strategy_choice: str, selected_variant: str | None = None) -> None:
    variant_key = _single_family_variant_session_key(strategy_choice)
    variant_options = family_variant_options(strategy_choice)
    if not variant_key or not variant_options:
        return

    if selected_variant not in variant_options:
        selected_variant = variant_options[0]
    concrete_strategy_name = resolve_concrete_strategy_display_name(strategy_choice, selected_variant)

    if concrete_strategy_name == "Quality Snapshot":
        _render_quality_snapshot_form()
    elif concrete_strategy_name == "Quality Snapshot (Strict Annual)":
        _render_quality_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Quality Snapshot (Strict Quarterly)":
        _render_quality_snapshot_strict_quarterly_prototype_form()
    elif concrete_strategy_name == "Value Snapshot (Strict Annual)":
        _render_value_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Value Snapshot (Strict Quarterly)":
        _render_value_snapshot_strict_quarterly_prototype_form()
    elif concrete_strategy_name == "Quality + Value Snapshot (Strict Annual)":
        _render_quality_value_snapshot_strict_annual_form()
    elif concrete_strategy_name == "Quality + Value Snapshot (Strict Quarterly)":
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
        st.session_state["eq_min_price_filter"] = float(
            payload.get("min_price_filter") or ETF_REAL_MONEY_DEFAULT_MIN_PRICE
        )
        st.session_state["eq_transaction_cost_bps"] = float(
            payload.get("transaction_cost_bps") or ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS
        )
        st.session_state["eq_benchmark_ticker"] = str(
            payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK
        ).strip().upper()
        st.session_state["eq_promotion_min_etf_aum_b"] = float(
            payload.get("promotion_min_etf_aum_b") or ETF_OPERABILITY_DEFAULT_MIN_AUM_B
        )
        st.session_state["eq_promotion_max_bid_ask_spread_pct"] = float(
            (payload.get("promotion_max_bid_ask_spread_pct") or ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT) * 100.0
        )
    elif strategy_key == "gtaa":
        st.session_state["gtaa_universe_mode"] = "Preset" if universe_mode == "preset" and preset_name in GTAA_PRESETS else "Manual"
        if st.session_state["gtaa_universe_mode"] == "Preset":
            st.session_state["gtaa_preset"] = preset_name
            st.session_state["gtaa_applied_preset_defaults"] = preset_name
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
        st.session_state["gtaa_min_avg_dollar_volume_20d_m_filter"] = float(
            payload.get("min_avg_dollar_volume_20d_m_filter")
            or STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M
        )
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
    elif strategy_key == "risk_on_momentum_5d":
        if universe_mode == "sp500":
            st.session_state["rom_universe_mode"] = "S&P 500"
        elif universe_mode == "top2000":
            st.session_state["rom_universe_mode"] = "Top2000"
        elif universe_mode in {"manual", "manual_tickers"}:
            st.session_state["rom_universe_mode"] = "Manual"
            st.session_state["rom_manual_tickers"] = tickers_text
        else:
            st.session_state["rom_universe_mode"] = "Top1000"
        st.session_state["rom_start"] = start_date
        st.session_state["rom_end"] = end_date
        st.session_state["rom_start_balance"] = float(payload.get("start_balance") or 10_000.0)
        st.session_state["rom_execution_mode"] = payload.get("execution_mode") or "close_based"
        st.session_state["rom_exit_mode"] = payload.get("exit_mode") or "fixed_pct"
        st.session_state["rom_max_holding_days"] = int(payload.get("max_holding_days") or 5)
        st.session_state["rom_stop_loss_pct"] = float(payload.get("stop_loss_pct") or -2.5)
        st.session_state["rom_take_profit_pct"] = float(payload.get("take_profit_pct") or 5.0)
        st.session_state["rom_atr_period"] = int(payload.get("atr_period") or 14)
        st.session_state["rom_stop_atr_multiple"] = float(payload.get("stop_atr_multiple") or 1.0)
        st.session_state["rom_take_profit_atr_multiple"] = float(payload.get("take_profit_atr_multiple") or 2.0)
        st.session_state["rom_max_new_positions_per_day"] = int(payload.get("max_new_positions_per_day") or 3)
        st.session_state["rom_max_total_positions"] = int(payload.get("max_total_positions") or 3)
        st.session_state["rom_transaction_cost_bps"] = float(payload.get("transaction_cost_bps") or 0.0)
        st.session_state["rom_slippage_bps"] = float(payload.get("slippage_bps") or 0.0)
        st.session_state["rom_macro_filter_enabled"] = bool(payload.get("macro_filter_enabled", True))
        st.session_state["rom_macro_filter_mode"] = payload.get("macro_filter_mode") or ("hard_filter" if payload.get("macro_filter_enabled", True) else "off")
        st.session_state["rom_risk_on_min"] = float(payload.get("risk_on_min") or 0.0)
        st.session_state["rom_rate_pressure_max"] = float(payload.get("rate_pressure_max") or 1.0)
        st.session_state["rom_dollar_pressure_max"] = float(payload.get("dollar_pressure_max") or 1.0)
        st.session_state["rom_safe_haven_max"] = float(payload.get("safe_haven_max") or 1.0)
        st.session_state["rom_rate_pressure_penalty_weight"] = float(payload.get("rate_pressure_penalty_weight") or 10.0)
        st.session_state["rom_dollar_pressure_penalty_weight"] = float(payload.get("dollar_pressure_penalty_weight") or 10.0)
        st.session_state["rom_safe_haven_penalty_weight"] = float(payload.get("safe_haven_penalty_weight") or 10.0)
        st.session_state["rom_min_price"] = float(payload.get("min_price") or 5.0)
        st.session_state["rom_min_adv20d_m"] = float(payload.get("min_avg_dollar_volume_20d", 20_000_000.0)) / 1_000_000.0
        st.session_state["rom_min_avg_volume_20d"] = int(payload.get("min_avg_volume_20d") or 500_000)
        st.session_state["rom_random_iterations"] = int(payload.get("random_iterations") or 50)
        st.session_state["rom_scanner_top_n_per_day"] = int(payload.get("scanner_top_n_per_day") or 50)
        st.session_state["rom_run_comparison_suite"] = bool(payload.get("run_comparison_suite", True))
        st.session_state["rom_run_sensitivity_suite"] = bool(payload.get("run_sensitivity_suite", False))
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
        st.session_state["qss_universe_contract"] = strict_universe_contract_label_for_input(
            payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
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
        st.session_state["qsqp_universe_contract"] = strict_universe_contract_label_for_input(
            payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
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
        st.session_state["vss_universe_contract"] = strict_universe_contract_label_for_input(
            payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
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
        st.session_state["vsqp_universe_contract"] = strict_universe_contract_label_for_input(
            payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
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
        st.session_state["qvss_universe_contract"] = strict_universe_contract_label_for_input(
            payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
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
        st.session_state["qvqp_universe_contract"] = strict_universe_contract_label_for_input(
            payload.get("universe_contract") or STATIC_MANAGED_RESEARCH_UNIVERSE
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


from app.web.backtest_single_forms.equal_weight import _render_equal_weight_form
from app.web.backtest_single_forms.gtaa import _render_gtaa_form
from app.web.backtest_single_forms.global_relative_strength import _render_global_relative_strength_form
from app.web.backtest_single_forms.risk_parity import _render_risk_parity_form
from app.web.backtest_single_forms.dual_momentum import _render_dual_momentum_form
from app.web.backtest_single_forms.risk_on_momentum import _render_risk_on_momentum_5d_form
from app.web.backtest_single_forms.strict_factor import (
    _render_quality_snapshot_form,
    _render_quality_snapshot_strict_annual_form,
    _render_quality_snapshot_strict_quarterly_prototype_form,
    _render_quality_value_snapshot_strict_annual_form,
    _render_quality_value_snapshot_strict_quarterly_prototype_form,
    _render_value_snapshot_strict_annual_form,
    _render_value_snapshot_strict_quarterly_prototype_form,
)

__all__ = [name for name in globals() if name.startswith("_render_") or name == "_apply_single_strategy_prefill"]
