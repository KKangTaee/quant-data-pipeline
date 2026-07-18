from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill
from app.web.backtest_single_settings_workspace import single_settings_section

def _render_gtaa_form() -> None:
    _apply_single_strategy_prefill("gtaa")
    current_preset = st.session_state.get("gtaa_preset") or next(iter(GTAA_PRESETS))
    _apply_gtaa_preset_parameter_defaults(
        key_prefix="gtaa",
        preset_name=str(current_preset),
    )

    with single_settings_section(
        "핵심 실행 설정",
        "검증 기간, 보유 자산 수, 신호 갱신 주기를 먼저 정합니다.",
    ):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=date(2016, 1, 1), key="gtaa_start")
        with col2:
            end_date = st.date_input("종료일", value=DEFAULT_BACKTEST_END_DATE, key="gtaa_end")
        setting_cols = st.columns(2)
        with setting_cols[0]:
            top = st.number_input(
                "보유 자산 수",
                min_value=1,
                max_value=12,
                step=1,
                help="GTAA는 평균 score 상위 자산을 선택합니다.",
                key="gtaa_top",
                **_session_state_default_arg("gtaa_top", "value", 3),
            )
        with setting_cols[1]:
            interval = st.number_input(
                "신호 갱신 간격(개월)",
                min_value=1,
                max_value=12,
                step=1,
                help="1이면 매월, 3이면 3개월마다 신호를 다시 계산합니다.",
                key="gtaa_interval",
                **_session_state_default_arg(
                    "gtaa_interval",
                    "value",
                    GTAA_DEFAULT_SIGNAL_INTERVAL,
                ),
            )

    with single_settings_section(
        "투자 대상 Universe",
        "자산군 구성을 선택합니다. 구성에 포함된 전체 ETF는 접힌 근거에서 확인합니다.",
    ):
        _universe_mode, preset_name, tickers = _render_gtaa_universe_inputs(
            key_prefix="gtaa",
        )

    timeframe = "1d"
    option = "month_end"
    with st.form("gtaa_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "상대강도 계산 기간과 위험회피 전환 조건을 설정합니다.",
        ):
            score_lookback_months, score_weights = _render_gtaa_score_weight_inputs(key_prefix="gtaa")
            with st.expander("위험회피 전환 규칙", expanded=False):
                risk_off_contract = _render_gtaa_risk_off_contract_inputs(key_prefix="gtaa")

        with single_settings_section(
            "비용·위험 기준",
            "거래 비용, 유동성, 비교 기준과 성과 악화 guardrail을 설정합니다.",
        ):
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
                    "최근 20일 최소 평균 거래대금($M)",
                    min_value=0.0,
                    max_value=100000.0,
                    step=5.0,
                    key=min_adv_key,
                    help="기준보다 거래대금이 낮은 ETF는 해당 리밸런싱 후보에서 제외합니다.",
                    **_session_state_default_arg(
                        min_adv_key,
                        "value",
                        STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
                    ),
                )
            )
            with st.expander("성과·낙폭 guardrail", expanded=False):
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

        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 자산을 한 개 이상 선택해 주세요.")
    if start_date > end_date:
        validation_errors.append("시작일은 종료일보다 늦을 수 없습니다.")
    if not score_lookback_months:
        validation_errors.append("상대강도 계산 기간을 한 개 이상 선택해 주세요.")

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
