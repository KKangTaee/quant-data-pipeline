from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_single_forms import _apply_single_strategy_prefill
from app.web.backtest_single_settings_workspace import single_settings_section

def _render_equal_weight_form() -> None:
    _apply_single_strategy_prefill("equal_weight")

    with single_settings_section(
        "핵심 실행 설정",
        "검증할 기간과 동일 비중 포트폴리오의 조정 주기를 정합니다.",
    ):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=date(2016, 1, 1), key="eq_start")
        with col2:
            end_date = st.date_input("종료일", value=DEFAULT_BACKTEST_END_DATE, key="eq_end")
        rebalance_interval = st.number_input(
            "리밸런싱 간격(개월)",
            min_value=1,
            max_value=36,
            value=12,
            step=1,
            help="1은 매월, 12는 연 1회 비중을 다시 맞춥니다.",
            key="eq_rebalance_interval",
        )

    with single_settings_section(
        "투자 대상 Universe",
        "기본 자산 구성을 사용하거나 검증할 ETF·자산을 직접 입력합니다.",
    ):
        _universe_mode, preset_name, tickers = _render_equal_weight_universe_inputs(
            key_prefix="eq",
        )

    timeframe = "1d"
    option = "month_end"
    with st.form("equal_weight_backtest_form", clear_on_submit=False, border=False):
        with single_settings_section(
            "선택·보유 규칙",
            "선택한 자산을 같은 비중으로 보유하며 위에서 정한 간격마다 조정합니다.",
        ):
            st.caption("일별 가격과 월말 기준으로 동일 비중을 계산합니다.")
        with single_settings_section(
            "비용·위험 기준",
            "거래 비용, 비교 기준, ETF 운용 가능성 기준을 필요할 때 조정합니다.",
        ):
            (
                min_price_filter,
                transaction_cost_bps,
                benchmark_ticker,
                promotion_min_etf_aum_b,
                promotion_max_bid_ask_spread_pct,
            ) = _render_etf_real_money_inputs(key_prefix="eq")

        submitted = st.form_submit_button("이 설정으로 백테스트 실행", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []

    if not tickers:
        validation_errors.append("투자 대상 종목을 한 개 이상 선택해 주세요.")
    if start_date > end_date:
        validation_errors.append("시작일은 종료일보다 늦을 수 없습니다.")

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
