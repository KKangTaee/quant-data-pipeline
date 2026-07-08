from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill

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
            with st.expander("Promotion Policy Signal", expanded=False):
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
        **_dynamic_etf_promotion_policy_defaults(),
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
