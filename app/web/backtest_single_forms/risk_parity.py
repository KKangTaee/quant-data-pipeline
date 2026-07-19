from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill
from app.web.backtest_single_settings_workspace import single_settings_section

def _render_risk_parity_form() -> None:
    _apply_single_strategy_prefill("risk_parity_trend")

    with single_settings_section(
        "핵심 실행 설정",
        "검증 기간, 리밸런싱 주기와 위험 계산 기간을 정합니다.",
    ):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=date(2016, 1, 1), key="rp_start")
        with col2:
            end_date = st.date_input("종료일", value=DEFAULT_BACKTEST_END_DATE, key="rp_end")
        setting_cols = st.columns(2)
        with setting_cols[0]:
            rebalance_interval = int(
                st.number_input(
                    "리밸런싱 간격(개월)",
                    min_value=1,
                    max_value=12,
                    value=1,
                    step=1,
                    key="rp_rebalance_interval",
                )
            )
        with setting_cols[1]:
            vol_window = int(
                st.number_input(
                    "변동성 계산 기간(개월)",
                    min_value=1,
                    max_value=24,
                    value=6,
                    step=1,
                    key="rp_vol_window",
                )
            )

    with single_settings_section(
        "투자 대상 Universe",
        "위험을 나눠 담을 자산 구성을 선택합니다.",
    ):
        universe_mode = st.radio(
            "투자 대상 선택",
            options=["Preset", "Manual"],
            format_func=lambda value: "기본 구성" if value == "Preset" else "직접 입력",
            horizontal=True,
            help="Risk Parity Trend도 기본적으로 preset universe 사용을 권장합니다.",
            key="rp_universe_mode",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "기본 구성",
                options=list(RISK_PARITY_PRESETS.keys()),
                index=0,
                key="rp_preset",
            )
            tickers = RISK_PARITY_PRESETS[preset_name]
            _render_ticker_preview(tickers)
        else:
            manual_tickers = st.text_input(
                "종목 직접 입력",
                value="SPY,TLT,GLD,IEF,LQD",
                help="쉼표로 구분합니다. 예: SPY,TLT,GLD,IEF,LQD",
                key="rp_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)
            _render_ticker_preview(tickers)

    timeframe = "1d"
    option = "month_end"
    with st.form("risk_parity_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "최근 변동성이 낮은 자산에 더 큰 비중을 배정하고 월말에 조정합니다.",
        ):
            st.caption("변동성 역수 기준 비중과 추세 조건을 적용합니다.")
        with single_settings_section(
            "비용·위험 기준",
            "거래 비용, 비교 기준과 성과·낙폭 guardrail을 설정합니다.",
        ):
            (
                min_price_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_etf_aum_b,
                promotion_max_bid_ask_spread_pct,
            ) = _render_etf_real_money_inputs(
                key_prefix="rp",
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
                    key_prefix="rp",
                    label_prefix="Risk Parity ",
                )

        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if not tickers:
        validation_errors.append("투자 대상 자산을 한 개 이상 선택해 주세요.")
    if start_date > end_date:
        validation_errors.append("시작일은 종료일보다 늦을 수 없습니다.")

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

    _handle_backtest_run(payload, strategy_name="Risk Parity Trend")
