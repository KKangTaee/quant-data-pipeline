from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill

def _render_gtaa_form() -> None:
    st.markdown("### GTAA")
    st.caption("자산군 ETF의 상대강도와 추세를 기준으로 상위 자산을 선택하고, 필요하면 방어 sleeve로 전환합니다.")
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

        with st.expander("전략·보유 규칙", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0, key="gtaa_timeframe")
            option = st.selectbox("Option", options=["month_end"], index=0, key="gtaa_option")
            top_key = "gtaa_top"
            top = st.number_input(
                "Top Assets",
                min_value=1,
                max_value=12,
                step=1,
                help="GTAA는 평균 score 상위 자산을 선택합니다.",
                key=top_key,
                **_session_state_default_arg(top_key, "value", 3),
            )
            interval_key = "gtaa_interval"
            interval = st.number_input(
                "Signal Interval (months)",
                min_value=1,
                max_value=12,
                step=1,
                help="현재 기본값은 1입니다. 1이면 매월, 2면 격월로 신호를 계산합니다.",
                key=interval_key,
                **_session_state_default_arg(interval_key, "value", GTAA_DEFAULT_SIGNAL_INTERVAL),
            )
            score_lookback_months, score_weights = _render_gtaa_score_weight_inputs(key_prefix="gtaa")
            _render_advanced_group_caption("핵심 실행 계약은 위에 두고, 추가 overlay / 실전 계약 / guardrail은 아래 그룹으로 분리했습니다.")
            with st.expander("Risk-Off Overlay", expanded=False):
                risk_off_contract = _render_gtaa_risk_off_contract_inputs(key_prefix="gtaa")
            with st.expander("비용·Guardrail", expanded=False):
                (
                    min_price_filter,
                    transaction_cost_bps,
                    benchmark_ticker,
                    promotion_min_etf_aum_b,
                    promotion_max_bid_ask_spread_pct,
                ) = _render_etf_real_money_inputs(
                    key_prefix="gtaa",
                )
                min_adv_key = "gtaa_min_avg_dollar_volume_20d_m_filter"
                min_avg_dollar_volume_20d_m_filter = float(
                    st.number_input(
                        "Min Avg Dollar Volume 20D ($M)",
                        min_value=0.0,
                        max_value=100000.0,
                        step=5.0,
                        key=min_adv_key,
                        help=(
                            "최근 20거래일 평균 거래대금이 이 값보다 낮은 ETF는 해당 리밸런싱 시점 후보에서 제외합니다."
                        ),
                        **_session_state_default_arg(
                            min_adv_key,
                            "value",
                            STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
                        ),
                    )
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
        "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter),
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
        "universe_mode": _universe_mode,
        "preset_name": preset_name,
    }

    _handle_backtest_run(payload, strategy_name="GTAA")
