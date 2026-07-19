from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill
from app.web.backtest_single_settings_workspace import single_settings_section

def _render_risk_on_momentum_5d_form() -> None:
    _apply_single_strategy_prefill("risk_on_momentum_5d")

    with single_settings_section(
        "핵심 실행 설정",
        "검증 기간과 시작 자산을 먼저 정합니다.",
    ):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("시작일", value=date(2021, 6, 1), key="rom_start")
        with col2:
            end_date = st.date_input("종료일", value=DEFAULT_BACKTEST_END_DATE, key="rom_end")
        with col3:
            start_balance = st.number_input(
                "시작 자산",
                min_value=1_000.0,
                max_value=10_000_000.0,
                value=10_000.0,
                step=1_000.0,
                key="rom_start_balance",
            )

    with single_settings_section(
        "투자 대상 Universe",
        "DB의 시가총액 기준 Universe를 사용하거나 직접 종목을 지정합니다.",
    ):
        universe_mode = st.radio(
            "투자 대상 선택",
            options=["Top1000", "Top2000", "S&P 500", "Manual"],
            format_func=lambda value: {
                "Top1000": "미국 시가총액 상위 1,000",
                "Top2000": "미국 시가총액 상위 2,000",
                "S&P 500": "S&P 500",
                "Manual": "종목 직접 입력",
            }[value],
            horizontal=True,
            key="rom_universe_mode",
        )
        manual_tickers = ""
        if universe_mode == "Manual":
            manual_tickers = st.text_input(
                "검증할 종목",
                value="NVDA,MSFT,AAPL,AMZN,META,AVGO,AMD,TSLA",
                key="rom_manual_tickers",
            )
            tickers = _parse_manual_tickers(manual_tickers)
            render_compact_ticker_summary(tickers)
        else:
            tickers = []
            st.caption("실행 시점에 DB 자산 프로필에서 해당 범위의 종목을 확정합니다.")

    with st.form("risk_on_momentum_5d_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "진입 수, 청산 기준, 시장 필터와 유동성 조건을 정합니다.",
        ):
          with st.expander("실행·청산 규칙", expanded=True):
            exec_col, exit_col = st.columns(2)
            with exec_col:
                execution_mode = st.selectbox(
                    "실행 기준",
                    options=["close_based"],
                    format_func=lambda _: "종가 신호 · 다음 거래일 실행",
                    index=0,
                    key="rom_execution_mode",
                )
                max_new_positions_per_day = int(
                    st.number_input(
                        "하루 최대 신규 편입 수",
                        min_value=1,
                        max_value=10,
                        value=3,
                        step=1,
                        key="rom_max_new_positions_per_day",
                    )
                )
                max_total_positions = int(
                    st.number_input(
                        "최대 동시 보유 수",
                        min_value=1,
                        max_value=20,
                        value=3,
                        step=1,
                        key="rom_max_total_positions",
                    )
                )
            with exit_col:
                exit_mode = st.selectbox(
                    "청산 기준",
                    options=["fixed_pct", "atr_based"],
                    format_func=lambda value: "고정 손익률" if value == "fixed_pct" else "ATR 변동성",
                    index=0,
                    key="rom_exit_mode",
                )
                max_holding_days = int(
                    st.number_input(
                        "최대 보유일",
                        min_value=1,
                        max_value=20,
                        value=5,
                        step=1,
                        key="rom_max_holding_days",
                    )
                )
                stop_loss_pct = st.number_input(
                    "손절 기준 (%)",
                    min_value=-50.0,
                    max_value=0.0,
                    value=-2.5,
                    step=0.5,
                    key="rom_stop_loss_pct",
                )
                take_profit_pct = st.number_input(
                    "익절 기준 (%)",
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
                            "ATR 계산 기간",
                            min_value=2,
                            max_value=100,
                            value=14,
                            step=1,
                            key="rom_atr_period",
                        )
                    )
                with atr_settings[1]:
                    stop_atr_multiple = st.number_input(
                        "손절 ATR 배수",
                        min_value=0.1,
                        max_value=10.0,
                        value=1.0,
                        step=0.1,
                        key="rom_stop_atr_multiple",
                    )
                with atr_settings[2]:
                    take_profit_atr_multiple = st.number_input(
                        "익절 ATR 배수",
                        min_value=0.1,
                        max_value=20.0,
                        value=2.0,
                        step=0.1,
                        key="rom_take_profit_atr_multiple",
                    )

          with st.expander("시장·후보 필터", expanded=True):
            macro_filter_mode = st.selectbox(
                "시장 필터 방식",
                options=["hard_filter", "ranking_penalty", "off"],
                format_func=lambda value: {
                    "hard_filter": "조건 미충족 후보 제외",
                    "ranking_penalty": "순위 감점",
                    "off": "사용하지 않음",
                }[value],
                index=0,
                key="rom_macro_filter_mode",
            )
            macro_filter_enabled = macro_filter_mode != "off"
            macro_cols = st.columns(4)
            with macro_cols[0]:
                risk_on_min = st.number_input("위험선호 최소 평균 Z", value=0.0, step=0.1, key="rom_risk_on_min")
            with macro_cols[1]:
                rate_pressure_max = st.number_input("금리 압력 최대 평균 Z", value=1.0, step=0.1, key="rom_rate_pressure_max")
            with macro_cols[2]:
                dollar_pressure_max = st.number_input("달러 압력 최대 평균 Z", value=1.0, step=0.1, key="rom_dollar_pressure_max")
            with macro_cols[3]:
                safe_haven_max = st.number_input("안전자산 선호 최대 평균 Z", value=1.0, step=0.1, key="rom_safe_haven_max")

            penalty_cols = st.columns(3)
            with penalty_cols[0]:
                rate_pressure_penalty_weight = st.number_input(
                    "금리 압력 감점",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    key="rom_rate_pressure_penalty_weight",
                )
            with penalty_cols[1]:
                dollar_pressure_penalty_weight = st.number_input(
                    "달러 압력 감점",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    key="rom_dollar_pressure_penalty_weight",
                )
            with penalty_cols[2]:
                safe_haven_penalty_weight = st.number_input(
                    "안전자산 선호 감점",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    key="rom_safe_haven_penalty_weight",
                )

            filter_cols = st.columns(3)
            with filter_cols[0]:
                min_price = st.number_input("최소 주가", min_value=0.0, value=5.0, step=1.0, key="rom_min_price")
            with filter_cols[1]:
                min_adv20d_m = st.number_input(
                    "최소 20일 평균 거래대금 ($M)",
                    min_value=0.0,
                    value=20.0,
                    step=5.0,
                    key="rom_min_adv20d_m",
                )
            with filter_cols[2]:
                min_avg_volume_20d = int(
                    st.number_input(
                        "최소 20일 평균 거래량",
                        min_value=0,
                        value=500_000,
                        step=50_000,
                        key="rom_min_avg_volume_20d",
                    )
                )

        with single_settings_section(
            "비용·위험 기준",
            "거래 비용과 추가 연구 진단 범위를 정합니다.",
        ):
            cost_cols = st.columns(4)
            with cost_cols[0]:
                transaction_cost_bps = st.number_input(
                    "거래 비용 (bps)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    key="rom_transaction_cost_bps",
                )
            with cost_cols[1]:
                slippage_bps = st.number_input(
                    "슬리피지 (bps)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    key="rom_slippage_bps",
                )
            with cost_cols[2]:
                random_iterations = int(
                    st.number_input(
                        "무작위 검증 반복 횟수",
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
                        "일별 후보 저장 수",
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
                    "비교 진단 함께 실행",
                    value=True,
                    key="rom_run_comparison_suite",
                )
            with suite_cols[1]:
                run_sensitivity_suite = st.checkbox(
                    "민감도 진단 함께 실행",
                    value=False,
                    key="rom_run_sensitivity_suite",
                )
            st.caption("추가 진단은 단기 스윙 전략의 과거 민감도를 확인하며 실전 승인이나 주문을 수행하지 않습니다.")

        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []
    if universe_mode == "Manual" and not tickers:
        validation_errors.append("직접 입력을 선택했다면 종목을 한 개 이상 입력해야 합니다.")
    if start_date > end_date:
        validation_errors.append("시작일은 종료일보다 늦을 수 없습니다.")
    if max_new_positions_per_day > max_total_positions:
        validation_errors.append("하루 최대 신규 편입 수는 최대 동시 보유 수보다 클 수 없습니다.")

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
