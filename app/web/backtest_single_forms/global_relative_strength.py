from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill
from app.web.backtest_single_settings_workspace import single_settings_section

def _render_global_relative_strength_form() -> None:
    _apply_single_strategy_prefill("global_relative_strength")

    with single_settings_section(
        "핵심 실행 설정",
        "검증 기간, 보유 자산 수, 신호 갱신 주기를 정합니다.",
    ):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=date(2016, 1, 1), key="grs_start")
        with col2:
            end_date = st.date_input("종료일", value=DEFAULT_BACKTEST_END_DATE, key="grs_end")
        setting_cols = st.columns(2)
        with setting_cols[0]:
            top = st.number_input(
                "보유 자산 수",
                min_value=1,
                max_value=12,
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
                step=1,
                help="상대강도 점수가 높은 ETF를 몇 개까지 보유할지 정합니다.",
                key="grs_top",
            )
        with setting_cols[1]:
            interval = st.number_input(
                "신호 갱신 간격(개월)",
                min_value=1,
                max_value=12,
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
                step=1,
                help="1이면 매월, 3이면 3개월마다 신호를 갱신합니다.",
                key="grs_interval",
            )

    with single_settings_section(
        "투자 대상 Universe",
        "글로벌 자산군 구성을 선택하고 가격 데이터 준비 상태를 확인합니다.",
    ):
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
        with st.expander("Universe 근거", expanded=False):
            _render_strict_price_freshness_preflight(
                tickers=preflight_tickers,
                end_value=end_date,
                timeframe="1d",
                strategy_label="Global Relative Strength",
            )

    timeframe = "1d"
    option = "month_end"
    with st.form("global_relative_strength_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "상대강도 기간, 방어 자산과 추세 기준을 설정합니다.",
        ):
            cash_ticker = st.text_input(
                "방어 자산 ticker",
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
                help="선택된 ETF가 200일선 아래에 있으면 이 ticker로 대피합니다. 기본값은 BIL입니다.",
                key="grs_cash_ticker",
            )
            score_lookback_months, score_weights = _render_global_relative_strength_score_weight_inputs(
                key_prefix="grs"
            )
            trend_filter_window = st.number_input(
                "추세 확인 기간(거래일)",
                min_value=20,
                max_value=400,
                value=GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
                step=10,
                help="가격이 이 이동평균 아래에 있으면 cash ticker로 대피합니다.",
                key="grs_trend_filter_window",
            )

        with single_settings_section(
            "비용·위험 기준",
            "거래 비용, 비교 기준과 ETF 운용 가능성 기준을 설정합니다.",
        ):
            (
                min_price_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_etf_aum_b,
                promotion_max_bid_ask_spread_pct,
            ) = _render_etf_real_money_inputs(
                key_prefix="grs",
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
    normalized_cash_ticker = str(cash_ticker or "").strip().upper()
    if not normalized_cash_ticker:
        validation_errors.append("방어 자산 ticker를 입력해 주세요.")

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
