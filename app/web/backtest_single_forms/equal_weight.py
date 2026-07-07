from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill

def _render_equal_weight_form() -> None:
    st.markdown("### Equal Weight")
    st.caption("선택한 ETF / 자산 universe를 동일 비중으로 보유하고 지정한 주기로 리밸런싱합니다.")
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
        with st.expander("Promotion Policy Signal", expanded=False):
            (
                min_price_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_etf_aum_b,
                promotion_max_bid_ask_spread_pct,
            ) = _render_etf_real_money_inputs(key_prefix="eq")

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
        "min_price_filter": float(min_price_filter),
        "transaction_cost_bps": float(transaction_cost_bps),
        "benchmark_ticker": benchmark_ticker,
        "promotion_min_etf_aum_b": float(promotion_min_etf_aum_b),
        "promotion_max_bid_ask_spread_pct": float(promotion_max_bid_ask_spread_pct),
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Equal Weight")
