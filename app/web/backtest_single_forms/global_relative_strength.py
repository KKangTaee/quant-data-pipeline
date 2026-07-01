from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill

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
            with st.expander("Promotion Policy Signal", expanded=False):
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
        **_dynamic_etf_promotion_policy_defaults(),
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="Global Relative Strength")

