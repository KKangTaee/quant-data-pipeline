from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill

def _render_risk_on_momentum_5d_form() -> None:
    st.markdown("### Risk-On Momentum 5D")
    st.caption("DB-backed short-term stock swing strategy with D+1 open execution.")
    _apply_single_strategy_prefill("risk_on_momentum_5d")

    universe_mode = st.radio(
        "Universe Mode",
        options=["Top1000", "Top2000", "S&P 500", "Manual"],
        horizontal=True,
        key="rom_universe_mode",
    )
    manual_tickers = ""
    if universe_mode == "Manual":
        manual_tickers = st.text_input(
            "Tickers",
            value="NVDA,MSFT,AAPL,AMZN,META,AVGO,AMD,TSLA",
            key="rom_manual_tickers",
        )
        tickers = _parse_manual_tickers(manual_tickers)
    else:
        tickers = []
        st.caption(f"{universe_mode} managed universe will be resolved from DB asset-profile market cap data.")

    with st.form("risk_on_momentum_5d_backtest_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date(2021, 6, 1), key="rom_start")
        with col2:
            end_date = st.date_input("End Date", value=DEFAULT_BACKTEST_END_DATE, key="rom_end")
        with col3:
            start_balance = st.number_input(
                "Start Balance",
                min_value=1_000.0,
                max_value=10_000_000.0,
                value=10_000.0,
                step=1_000.0,
                key="rom_start_balance",
            )

        with st.expander("전략·보유 규칙 · 실행/청산", expanded=True):
            exec_col, exit_col = st.columns(2)
            with exec_col:
                execution_mode = st.selectbox("Execution Mode", options=["close_based"], index=0, key="rom_execution_mode")
                max_new_positions_per_day = int(
                    st.number_input(
                        "Max New Positions / Day",
                        min_value=1,
                        max_value=10,
                        value=3,
                        step=1,
                        key="rom_max_new_positions_per_day",
                    )
                )
                max_total_positions = int(
                    st.number_input(
                        "Max Total Positions",
                        min_value=1,
                        max_value=20,
                        value=3,
                        step=1,
                        key="rom_max_total_positions",
                    )
                )
            with exit_col:
                exit_mode = st.selectbox("Exit Mode", options=["fixed_pct", "atr_based"], index=0, key="rom_exit_mode")
                max_holding_days = int(
                    st.number_input(
                        "Max Holding Days",
                        min_value=1,
                        max_value=20,
                        value=5,
                        step=1,
                        key="rom_max_holding_days",
                    )
                )
                stop_loss_pct = st.number_input(
                    "Stop Loss %",
                    min_value=-50.0,
                    max_value=0.0,
                    value=-2.5,
                    step=0.5,
                    key="rom_stop_loss_pct",
                )
                take_profit_pct = st.number_input(
                    "Take Profit %",
                    min_value=0.5,
                    max_value=100.0,
                    value=5.0,
                    step=0.5,
                    key="rom_take_profit_pct",
                )
                atr_settings = st.columns(3)
                with atr_settings[0]:
                    atr_period = int(
                        st.number_input(
                            "ATR Period",
                            min_value=2,
                            max_value=100,
                            value=14,
                            step=1,
                            key="rom_atr_period",
                        )
                    )
                with atr_settings[1]:
                    stop_atr_multiple = st.number_input(
                        "Stop ATR x",
                        min_value=0.1,
                        max_value=10.0,
                        value=1.0,
                        step=0.1,
                        key="rom_stop_atr_multiple",
                    )
                with atr_settings[2]:
                    take_profit_atr_multiple = st.number_input(
                        "Take ATR x",
                        min_value=0.1,
                        max_value=20.0,
                        value=2.0,
                        step=0.1,
                        key="rom_take_profit_atr_multiple",
                    )

        with st.expander("전략·보유 규칙 · Macro/후보", expanded=True):
            macro_filter_mode = st.selectbox(
                "Macro Filter Mode",
                options=["hard_filter", "ranking_penalty", "off"],
                index=0,
                key="rom_macro_filter_mode",
            )
            macro_filter_enabled = macro_filter_mode != "off"
            macro_cols = st.columns(4)
            with macro_cols[0]:
                risk_on_min = st.number_input("Risk-On Min Mean Z", value=0.0, step=0.1, key="rom_risk_on_min")
            with macro_cols[1]:
                rate_pressure_max = st.number_input("Rate Pressure Max Mean Z", value=1.0, step=0.1, key="rom_rate_pressure_max")
            with macro_cols[2]:
                dollar_pressure_max = st.number_input("Dollar Pressure Max Mean Z", value=1.0, step=0.1, key="rom_dollar_pressure_max")
            with macro_cols[3]:
                safe_haven_max = st.number_input("Safe Haven Max Mean Z", value=1.0, step=0.1, key="rom_safe_haven_max")

            penalty_cols = st.columns(3)
            with penalty_cols[0]:
                rate_pressure_penalty_weight = st.number_input(
                    "Rate Penalty Weight",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    key="rom_rate_pressure_penalty_weight",
                )
            with penalty_cols[1]:
                dollar_pressure_penalty_weight = st.number_input(
                    "Dollar Penalty Weight",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    key="rom_dollar_pressure_penalty_weight",
                )
            with penalty_cols[2]:
                safe_haven_penalty_weight = st.number_input(
                    "Safe-Haven Penalty Weight",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    key="rom_safe_haven_penalty_weight",
                )

            filter_cols = st.columns(3)
            with filter_cols[0]:
                min_price = st.number_input("Min Price", min_value=0.0, value=5.0, step=1.0, key="rom_min_price")
            with filter_cols[1]:
                min_adv20d_m = st.number_input(
                    "Min ADV 20D ($M)",
                    min_value=0.0,
                    value=20.0,
                    step=5.0,
                    key="rom_min_adv20d_m",
                )
            with filter_cols[2]:
                min_avg_volume_20d = int(
                    st.number_input(
                        "Min Avg Volume 20D",
                        min_value=0,
                        value=500_000,
                        step=50_000,
                        key="rom_min_avg_volume_20d",
                    )
                )

        with st.expander("비용·Guardrail", expanded=False):
            cost_cols = st.columns(4)
            with cost_cols[0]:
                transaction_cost_bps = st.number_input(
                    "Transaction Cost bps",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    key="rom_transaction_cost_bps",
                )
            with cost_cols[1]:
                slippage_bps = st.number_input(
                    "Slippage bps",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    key="rom_slippage_bps",
                )
            with cost_cols[2]:
                random_iterations = int(
                    st.number_input(
                        "Random Iterations",
                        min_value=0,
                        max_value=100,
                        value=50,
                        step=5,
                        key="rom_random_iterations",
                    )
                )
            with cost_cols[3]:
                scanner_top_n_per_day = int(
                    st.number_input(
                        "Scanner Rows / Day",
                        min_value=1,
                        max_value=200,
                        value=50,
                        step=5,
                        key="rom_scanner_top_n_per_day",
                    )
                )
            suite_cols = st.columns(2)
            with suite_cols[0]:
                run_comparison_suite = st.checkbox(
                    "Run V2 Comparison Suite",
                    value=True,
                    key="rom_run_comparison_suite",
                )
            with suite_cols[1]:
                run_sensitivity_suite = st.checkbox(
                    "Run V2 Sensitivity Suite",
                    value=False,
                    key="rom_run_sensitivity_suite",
                )
            st.caption("V2 suites are historical research diagnostics for daily swing behavior, not Practical Validation or live trading approval.")

        submitted = st.form_submit_button("Run Risk-On Momentum 5D Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if universe_mode == "Manual" and not tickers:
        validation_errors.append("At least one ticker is required for Manual universe.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")
    if max_new_positions_per_day > max_total_positions:
        validation_errors.append("Max New Positions / Day must be less than or equal to Max Total Positions.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    universe_payload = {
        "Top1000": ("top1000", "Top1000", 1000),
        "Top2000": ("top2000", "Top2000", 2000),
        "S&P 500": ("sp500", "S&P 500", 500),
        "Manual": ("manual_tickers", None, len(tickers)),
    }[universe_mode]
    payload = {
        "strategy_key": "risk_on_momentum_5d",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": "1d",
        "option": "close_based",
        "universe_mode": universe_payload[0],
        "preset_name": universe_payload[1],
        "universe_limit": universe_payload[2],
        "start_balance": float(start_balance),
        "execution_mode": execution_mode,
        "exit_mode": exit_mode,
        "max_holding_days": int(max_holding_days),
        "stop_loss_pct": float(stop_loss_pct),
        "take_profit_pct": float(take_profit_pct),
        "atr_period": int(atr_period),
        "stop_atr_multiple": float(stop_atr_multiple),
        "take_profit_atr_multiple": float(take_profit_atr_multiple),
        "max_new_positions_per_day": int(max_new_positions_per_day),
        "max_total_positions": int(max_total_positions),
        "transaction_cost_bps": float(transaction_cost_bps),
        "slippage_bps": float(slippage_bps),
        "macro_filter_enabled": bool(macro_filter_enabled),
        "macro_filter_mode": macro_filter_mode,
        "risk_on_min": float(risk_on_min),
        "rate_pressure_max": float(rate_pressure_max),
        "dollar_pressure_max": float(dollar_pressure_max),
        "safe_haven_max": float(safe_haven_max),
        "rate_pressure_penalty_weight": float(rate_pressure_penalty_weight),
        "dollar_pressure_penalty_weight": float(dollar_pressure_penalty_weight),
        "safe_haven_penalty_weight": float(safe_haven_penalty_weight),
        "min_price": float(min_price),
        "min_avg_dollar_volume_20d": float(min_adv20d_m) * 1_000_000.0,
        "min_avg_volume_20d": int(min_avg_volume_20d),
        "random_iterations": int(random_iterations),
        "scanner_top_n_per_day": int(scanner_top_n_per_day),
        "run_comparison_suite": bool(run_comparison_suite),
        "run_sensitivity_suite": bool(run_sensitivity_suite),
    }

    _handle_backtest_run(payload, strategy_name="Risk-On Momentum 5D")
