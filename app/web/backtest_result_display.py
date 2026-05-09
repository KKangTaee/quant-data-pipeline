from __future__ import annotations

from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_ui_components import render_status_card_grid


def _render_compare_altair_chart(
    compare_df: pd.DataFrame,
    *,
    title: str,
    y_title: str,
    show_end_markers: bool = False,
) -> None:
    long_df = (
        compare_df.reset_index()
        .melt(id_vars="Date", var_name="Strategy", value_name="Value")
        .dropna(subset=["Value"])
    )

    chart = (
        alt.Chart(long_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Value:Q", title=y_title),
            color=alt.Color("Strategy:N", title="Strategy"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Strategy:N", title="Strategy"),
                alt.Tooltip("Value:Q", title=y_title, format=",.3f"),
            ],
        )
        .properties(title=title, height=360)
    )

    if not show_end_markers:
        st.altair_chart(chart, use_container_width=True)
        return

    marker_df = long_df.sort_values("Date").groupby("Strategy", as_index=False).tail(1)
    end_points = (
        alt.Chart(marker_df)
        .mark_point(size=90, filled=True)
        .encode(
            x="Date:T",
            y="Value:Q",
            color=alt.Color("Strategy:N", legend=None),
            tooltip=[
                alt.Tooltip("Date:T", title="End Date"),
                alt.Tooltip("Strategy:N", title="Strategy"),
                alt.Tooltip("Value:Q", title=y_title, format=",.3f"),
            ],
        )
    )
    end_labels = (
        alt.Chart(marker_df)
        .mark_text(align="left", dx=8, dy=-8, fontSize=11)
        .encode(
            x="Date:T",
            y="Value:Q",
            text="Strategy:N",
            color=alt.Color("Strategy:N", legend=None),
        )
    )
    st.altair_chart(chart + end_points + end_labels, use_container_width=True)


def _render_data_trust_summary(meta: dict[str, Any]) -> None:
    price_freshness = meta.get("price_freshness") or {}
    freshness_details = price_freshness.get("details") or {}
    excluded_tickers = list(meta.get("excluded_tickers") or [])
    malformed_price_rows = list(meta.get("malformed_price_rows") or [])

    st.markdown("#### Data Trust Summary")
    st.caption(
        "이번 결과가 어떤 데이터 범위에서 계산됐는지 먼저 확인하는 요약입니다. "
        "성과 해석 전에 요청 기간과 실제 결과 기간, 가격 최신성, 제외 ticker를 같이 봅니다."
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Requested End", meta.get("end") or "-")
    metric_cols[1].metric("Actual Result End", meta.get("actual_result_end") or "-")
    metric_cols[2].metric("Result Rows", meta.get("result_rows", "-"))
    metric_cols[3].metric("Excluded Tickers", len(excluded_tickers))

    if freshness_details:
        fresh_cols = st.columns(4)
        fresh_cols[0].metric("Effective Trading End", freshness_details.get("effective_end_date") or "-")
        fresh_cols[1].metric("Common Latest Price", freshness_details.get("common_latest_date") or "-")
        fresh_cols[2].metric("Newest Latest Price", freshness_details.get("newest_latest_date") or "-")
        fresh_cols[3].metric("Latest-Date Spread", f"{freshness_details.get('spread_days', 0)}d")
        status = str(price_freshness.get("status") or "").strip().lower()
        message = price_freshness.get("message")
        if status == "ok":
            st.success(message or "가격 최신성 점검이 통과되었습니다.")
        elif status == "warning":
            st.warning(message or "가격 최신성 점검에서 주의가 필요합니다.")
        elif status == "error":
            st.error(message or "가격 최신성 점검에 실패했습니다.")

    if excluded_tickers or malformed_price_rows:
        with st.expander("Data Quality Details", expanded=False):
            if excluded_tickers:
                st.markdown("**Excluded Tickers**")
                st.caption("전략 계산에 필요한 가격 이력이나 파생 지표가 부족해 이번 실행에서 제외된 ticker입니다.")
                st.code(", ".join(excluded_tickers))
            if malformed_price_rows:
                st.markdown("**Malformed / Missing Price Rows**")
                st.caption("가격 컬럼에 결측이 있는 ticker입니다. 공통 계산 가능 날짜가 짧아질 수 있습니다.")
                malformed_df = pd.DataFrame(malformed_price_rows).rename(
                    columns={
                        "ticker": "Ticker",
                        "price_col": "Price Column",
                        "count": "Missing Row Count",
                        "first_date": "First Missing Date",
                        "last_date": "Last Missing Date",
                        "sample_dates": "Sample Missing Dates",
                    }
                )
                st.dataframe(malformed_df, use_container_width=True, hide_index=True)

def _data_trust_status_label(status: str | None) -> str:
    normalized = str(status or "").strip().lower()
    if normalized == "ok":
        return "OK"
    if normalized == "warning":
        return "Warning"
    if normalized == "error":
        return "Error"
    return "-"

def _build_strategy_data_trust_rows(bundles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        meta = dict(bundle.get("meta") or {})
        result_df = bundle.get("result_df")
        price_freshness = dict(meta.get("price_freshness") or {})
        freshness_details = dict(price_freshness.get("details") or {})
        excluded_tickers = list(meta.get("excluded_tickers") or [])
        malformed_price_rows = list(meta.get("malformed_price_rows") or [])
        warnings = list(meta.get("warnings") or [])

        requested_end = meta.get("end") or meta.get("requested_end") or meta.get("input_end")
        actual_end = meta.get("actual_result_end")
        if not actual_end and isinstance(result_df, pd.DataFrame) and not result_df.empty and "Date" in result_df.columns:
            actual_end = str(pd.to_datetime(result_df["Date"], errors="coerce").max().date())
        actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
        requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
        result_period_shortened = (
            pd.notna(actual_end_ts)
            and pd.notna(requested_end_ts)
            and actual_end_ts.date() < requested_end_ts.date()
        )
        issue_count = len(excluded_tickers) + len(malformed_price_rows) + len(warnings)
        freshness_status = str(price_freshness.get("status") or "").strip().lower()

        if freshness_status in {"warning", "error"}:
            interpretation = "가격 최신성 확인 필요"
        elif excluded_tickers or malformed_price_rows:
            interpretation = "제외/결측 ticker 확인 필요"
        elif result_period_shortened:
            interpretation = "실제 결과 종료일이 요청 종료일보다 짧음"
        elif issue_count == 0:
            interpretation = "눈에 띄는 데이터 이슈 없음"
        else:
            interpretation = "주의사항 확인 필요"

        rows.append(
            {
                "Strategy": bundle.get("strategy_name") or meta.get("strategy_name") or "-",
                "Requested End": requested_end or "-",
                "Actual Result End": actual_end or "-",
                "Result Rows": meta.get("result_rows", len(result_df) if isinstance(result_df, pd.DataFrame) else "-"),
                "Price Freshness": _data_trust_status_label(freshness_status),
                "Common Latest Price": freshness_details.get("common_latest_date") or "-",
                "Newest Latest Price": freshness_details.get("newest_latest_date") or "-",
                "Latest-Date Spread": (
                    f"{freshness_details.get('spread_days')}d"
                    if freshness_details.get("spread_days") is not None
                    else "-"
                ),
                "Excluded Tickers": len(excluded_tickers),
                "Malformed Tickers": len(malformed_price_rows),
                "Warnings": len(warnings),
                "Interpretation": interpretation,
            }
        )
    return rows

def _render_strategy_data_trust_details(bundles: list[dict[str, Any]]) -> None:
    detail_found = False
    for bundle in bundles:
        meta = dict(bundle.get("meta") or {})
        excluded_tickers = list(meta.get("excluded_tickers") or [])
        malformed_price_rows = list(meta.get("malformed_price_rows") or [])
        warnings = list(meta.get("warnings") or [])
        price_freshness = dict(meta.get("price_freshness") or {})
        message = price_freshness.get("message")
        if not any([excluded_tickers, malformed_price_rows, warnings, message]):
            continue

        detail_found = True
        st.markdown(f"##### {bundle.get('strategy_name') or '-'}")
        if message:
            st.caption(str(message))
        if warnings:
            st.markdown("**Warnings**")
            for warning in warnings:
                st.warning(str(warning))
        if excluded_tickers:
            st.markdown("**Excluded Tickers**")
            st.code(", ".join(excluded_tickers))
        if malformed_price_rows:
            st.markdown("**Malformed / Missing Price Rows**")
            malformed_df = pd.DataFrame(malformed_price_rows).rename(
                columns={
                    "ticker": "Ticker",
                    "price_col": "Price Column",
                    "count": "Missing Row Count",
                    "first_date": "First Missing Date",
                    "last_date": "Last Missing Date",
                    "sample_dates": "Sample Missing Dates",
                }
            )
            st.dataframe(malformed_df, use_container_width=True, hide_index=True)
    if not detail_found:
        st.caption("이번 compare 구성에서는 별도 excluded ticker, malformed row, warning detail이 기록되지 않았습니다.")

def _render_strategy_data_trust_snapshot(
    bundles: list[dict[str, Any]],
    *,
    title: str = "Data Trust Snapshot",
    caption: str | None = None,
) -> list[dict[str, Any]]:
    rows = _build_strategy_data_trust_rows(bundles)
    if not rows:
        return []

    st.markdown(f"##### {title}")
    st.caption(
        caption
        or "여러 전략을 비교하거나 섞기 전에 각 전략이 실제로 어떤 데이터 기간과 품질 조건에서 계산됐는지 확인합니다."
    )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    with st.expander("Data Quality Details Across Strategies", expanded=False):
        _render_strategy_data_trust_details(bundles)
    return rows

def _render_last_run() -> None:
    error = st.session_state.backtest_last_error
    error_kind = st.session_state.backtest_last_error_kind
    bundle = st.session_state.backtest_last_bundle

    if error:
        if error_kind == "input":
            st.warning(error)
        elif error_kind == "data":
            st.error(error)
            st.caption("Hint: run the ingestion pipeline for the requested tickers and date range, then try again.")
        else:
            st.error(error)

    if not bundle:
        return

    summary_df = bundle["summary_df"]
    chart_df = bundle["chart_df"]
    result_df = bundle["result_df"]
    meta = bundle["meta"]
    warnings = list(meta.get("warnings") or [])

    st.markdown("### Latest Backtest Run")
    strategy_key = meta.get("strategy_key")
    has_selection_history = strategy_key in SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS

    dynamic_snapshot_rows = bundle.get("dynamic_universe_snapshot_rows") or []
    dynamic_candidate_status_rows = bundle.get("dynamic_candidate_status_rows") or []
    has_dynamic_details = bool(
        dynamic_snapshot_rows
        or dynamic_candidate_status_rows
        or meta.get("universe_contract") == HISTORICAL_DYNAMIC_PIT_UNIVERSE
    )
    has_real_money_details = bool(meta.get("real_money_hardening"))

    st.info(
        "가장 최근 실행한 백테스트 결과입니다. "
        "먼저 `Summary`에서 핵심 숫자를 보고, `Equity Curve`에서 흐름을 확인한 뒤, "
        "`Real-Money`와 `Meta`에서 실전형 해석과 실행 조건을 읽으면 가장 자연스럽습니다."
    )

    guide_left, guide_right = st.columns([1.4, 1.0], gap="small")
    with guide_left:
        st.markdown("##### 결과 읽는 순서")
        st.markdown(
            "- `Summary`: 수익률과 위험의 핵심 숫자 확인\n"
            "- `Equity Curve`: 전략 흐름과 회복 구간 확인\n"
            "- `Selection History`: 각 리밸런싱에서 실제로 어떤 종목이 선택되고 어떻게 처리됐는지 확인\n"
            "- `Real-Money`: 실전 후보 해석, 검토 근거, 실행 부담 확인\n"
            "- `Meta`: 이번 실행의 계약과 세부 설정 재확인"
        )
    with guide_right:
        st.markdown("##### 이번 실행에 포함된 보기")
        availability_lines = [
            f"- `Selection History`: {'있음' if has_selection_history else '없음'}",
            f"- `Dynamic Universe`: {'있음' if has_dynamic_details else '없음'}",
            f"- `Real-Money`: {'있음' if has_real_money_details else '없음'}",
        ]
        st.markdown("\n".join(availability_lines))

    _render_data_trust_summary(meta)

    with st.expander("Practical Validation Handoff", expanded=False):
        st.caption(
            "이번 실행 결과를 Clean V2 source로 저장하고 Practical Validation에서 실전 검증 자료로 읽어봅니다. "
            "이 동작은 최종 선택, 투자 추천, live 승인, 주문 지시가 아닙니다."
        )
        handoff_cols = st.columns([0.28, 0.72], gap="small")
        with handoff_cols[0]:
            if st.button("Practical Validation으로 보내기", key="latest_run_candidate_review_draft", use_container_width=True):
                _queue_candidate_review_draft(_candidate_review_draft_from_bundle(bundle))
                st.rerun()
        with handoff_cols[1]:
            st.caption(
                "`Practical Validation`에서 Data Trust, Real-Money signal, 구성 / 비중 조건을 확인한 뒤 "
                "`Final Review`에서 최종 선택 / 보류 / 거절 / 재검토를 판단합니다."
            )

    if warnings:
        warning_lines = "\n".join(f"- {warning}" for warning in warnings)
        st.warning(
            "이번 실행에서 같이 봐야 할 주의 사항이 있습니다.\n\n"
            + warning_lines
        )

    st.markdown(f"#### {bundle['strategy_name']}")
    _render_summary_metrics(summary_df)

    tab_labels = ["Summary", "Equity Curve", "Balance Extremes", "Period Extremes"]
    if has_selection_history:
        tab_labels.append("Selection History")
    if has_dynamic_details:
        tab_labels.append("Dynamic Universe")
    if has_real_money_details:
        tab_labels.append("Real-Money")
    tab_labels.extend(["Result Table", "Meta"])
    tabs = st.tabs(tab_labels)
    tab_iter = iter(tabs)
    summary_tab = next(tab_iter)
    curve_tab = next(tab_iter)
    balance_tab = next(tab_iter)
    periods_tab = next(tab_iter)
    selection_tab = next(tab_iter) if has_selection_history else None
    dynamic_tab = next(tab_iter) if has_dynamic_details else None
    real_money_tab = next(tab_iter) if has_real_money_details else None
    table_tab = next(tab_iter)
    meta_tab = next(tab_iter)

    with summary_tab:
        st.dataframe(summary_df, use_container_width=True)

    with curve_tab:
        _render_balance_chart_with_markers(
            chart_df,
            result_df=result_df,
            title="Equity Curve",
        )
        st.caption(
            "고점 / 저점 / 마지막 지점과 최고 / 최저 기간 마커를 같이 보여줘서, "
            "단순 선 그래프보다 전략 흐름을 더 쉽게 읽을 수 있습니다."
        )

    with balance_tab:
        high_df, low_df = _build_balance_extremes_tables(chart_df, top_n=3)
        high_col, low_col = st.columns(2, gap="large")
        with high_col:
            st.markdown("##### Top 3 Balance Highs")
            st.dataframe(high_df, use_container_width=True, hide_index=True)
        with low_col:
            st.markdown("##### Top 3 Balance Lows")
            st.dataframe(low_df, use_container_width=True, hide_index=True)

    with periods_tab:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=3)
        best_col, worst_col = st.columns(2, gap="large")
        with best_col:
            st.markdown("##### Top 3 Best Periods")
            st.dataframe(best_df, use_container_width=True, hide_index=True)
        with worst_col:
            st.markdown("##### Top 3 Worst Periods")
            st.dataframe(worst_df, use_container_width=True, hide_index=True)

    if selection_tab is not None:
        with selection_tab:
            _render_snapshot_selection_history(
                result_df,
                strategy_name=bundle["strategy_name"],
                factor_names=(meta.get("quality_factors") or []) + [
                    name for name in (meta.get("value_factors") or [])
                    if name not in (meta.get("quality_factors") or [])
                ],
                snapshot_mode=meta.get("snapshot_mode"),
                snapshot_source=meta.get("snapshot_source"),
            )

    if dynamic_tab is not None:
        with dynamic_tab:
            _render_dynamic_universe_details(bundle)

    if real_money_tab is not None:
        with real_money_tab:
            _render_real_money_details(bundle)

    with table_tab:
        st.dataframe(result_df, use_container_width=True)

    with meta_tab:
        left, right = st.columns([1.1, 1.2], gap="large")
        with left:
            st.markdown("##### Execution Context")
            st.markdown(f"- `Mode`: `{meta['execution_mode']}`")
            st.markdown(f"- `Data`: `{meta['data_mode']}`")
            st.markdown(f"- `Universe`: `{meta['universe_mode']}`")
            if meta.get("universe_contract"):
                st.markdown(f"- `Universe Contract`: `{meta['universe_contract']}`")
            st.markdown(f"- `Tickers`: `{', '.join(meta['tickers'])}`")
            st.markdown(f"- `Period`: `{meta['start']}` -> `{meta['end']}`")
            if meta.get("ui_elapsed_seconds") is not None:
                st.markdown(f"- `Elapsed`: `{meta['ui_elapsed_seconds']:.3f}s`")
            if meta.get("top") is not None:
                st.markdown(f"- `Top`: `{meta['top']}`")
            if meta.get("min_price_filter") is not None:
                st.markdown(f"- `Minimum Price`: `{float(meta['min_price_filter']):.2f}`")
            if meta.get("min_history_months_filter") is not None:
                st.markdown(f"- `Minimum History`: `{int(meta.get('min_history_months_filter') or 0)}M`")
            if meta.get("min_avg_dollar_volume_20d_m_filter") is not None:
                st.markdown(
                    f"- `Min Avg Dollar Volume 20D`: `{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M`"
                )
                if meta.get("liquidity_excluded_total") is not None:
                    st.markdown(
                        f"- `Liquidity Excluded`: total `{int(meta.get('liquidity_excluded_total') or 0)}`, "
                        f"rows `{int(meta.get('liquidity_excluded_active_rows') or 0)}`"
                    )
                if meta.get("liquidity_clean_coverage") is not None:
                    st.markdown(
                        f"- `Liquidity Clean Coverage`: `{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}`"
                    )
            if meta.get("transaction_cost_bps") is not None:
                st.markdown(f"- `Transaction Cost`: `{float(meta['transaction_cost_bps']):.1f} bps`")
            if meta.get("promotion_min_etf_aum_b") is not None:
                st.markdown(
                    f"- `Min ETF AUM`: `${float(meta.get('promotion_min_etf_aum_b') or 0.0):.1f}B`"
                )
            if meta.get("promotion_max_bid_ask_spread_pct") is not None:
                st.markdown(
                    f"- `Max Bid-Ask Spread`: `{float(meta.get('promotion_max_bid_ask_spread_pct') or 0.0):.2%}`"
                )
            if meta.get("benchmark_contract"):
                st.markdown(
                    f"- `Benchmark Contract`: `{_benchmark_contract_value_to_label(meta.get('benchmark_contract'))}`"
                )
            if meta.get("benchmark_ticker"):
                st.markdown(f"- `Benchmark Ticker`: `{meta['benchmark_ticker']}`")
            if _raw_guardrail_reference_ticker_value(meta):
                st.markdown(
                    f"- `Guardrail / Reference Ticker`: `{_raw_guardrail_reference_ticker_value(meta)}`"
                )
            elif meta.get("benchmark_ticker"):
                st.markdown("- `Guardrail / Reference Ticker`: `Same as Benchmark Ticker`")
            if meta.get("benchmark_symbol_count") is not None:
                st.markdown(f"- `Benchmark Universe`: `{int(meta.get('benchmark_symbol_count') or 0)}`")
            if meta.get("benchmark_eligible_symbol_count") is not None:
                st.markdown(f"- `Benchmark Eligible`: `{int(meta.get('benchmark_eligible_symbol_count') or 0)}`")
            if meta.get("benchmark_cagr") is not None:
                st.markdown(f"- `Benchmark CAGR`: `{float(meta['benchmark_cagr']):.2%}`")
            if meta.get("net_cagr_spread") is not None:
                st.markdown(f"- `Net CAGR Spread`: `{float(meta['net_cagr_spread']):.2%}`")
            if meta.get("benchmark_row_coverage") is not None:
                st.markdown(f"- `Benchmark Coverage`: `{float(meta['benchmark_row_coverage']):.2%}`")
            if meta.get("promotion_min_benchmark_coverage") is not None:
                st.markdown(
                    f"- `Min Benchmark Coverage`: `{float(meta.get('promotion_min_benchmark_coverage') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_net_cagr_spread") is not None:
                st.markdown(
                    f"- `Min Net CAGR Spread`: `{float(meta.get('promotion_min_net_cagr_spread') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_liquidity_clean_coverage") is not None:
                st.markdown(
                    f"- `Min Liquidity Clean Coverage`: `{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_underperformance_share") is not None:
                st.markdown(
                    f"- `Max Underperformance Share`: `{float(meta.get('promotion_max_underperformance_share') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_worst_rolling_excess_return") is not None:
                st.markdown(
                    f"- `Min Worst Rolling Excess`: `{float(meta.get('promotion_min_worst_rolling_excess_return') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_strategy_drawdown") is not None:
                st.markdown(
                    f"- `Max Strategy Drawdown`: `{float(meta.get('promotion_max_strategy_drawdown') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
                st.markdown(
                    f"- `Max Drawdown Gap`: `{float(meta.get('promotion_max_drawdown_gap_vs_benchmark') or 0.0):.0%}`"
                )
            if meta.get("etf_operability_status"):
                st.markdown(f"- `ETF Operability Status`: `{meta.get('etf_operability_status')}`")
            if _should_show_guardrail_surface(meta):
                under_enabled = bool(meta.get("underperformance_guardrail_enabled"))
                draw_enabled = bool(meta.get("drawdown_guardrail_enabled"))
                st.markdown(
                    f"- `Underperformance Guardrail`: "
                    f"`{'ON' if under_enabled else 'OFF'}`, "
                    f"`{int(meta.get('underperformance_guardrail_window_months') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
                    f"`{float(meta.get('underperformance_guardrail_threshold') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD):.0%}`"
                )
                st.markdown(
                    f"- `Underperformance Trigger`: "
                    f"`{int(meta.get('underperformance_guardrail_trigger_count') or 0)}` / "
                    f"`{float(meta.get('underperformance_guardrail_trigger_share') or 0.0):.2%}`"
                )
                st.markdown(
                    f"- `Drawdown Guardrail`: "
                    f"`{'ON' if draw_enabled else 'OFF'}`, "
                    f"`{int(meta.get('drawdown_guardrail_window_months') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
                    f"`{float(meta.get('drawdown_guardrail_strategy_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD):.0%}`, "
                    f"`gap {float(meta.get('drawdown_guardrail_gap_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD):.0%}`"
                )
                st.markdown(
                    f"- `Drawdown Trigger`: "
                    f"`{int(meta.get('drawdown_guardrail_trigger_count') or 0)}` / "
                    f"`{float(meta.get('drawdown_guardrail_trigger_share') or 0.0):.2%}`"
                )
            if meta.get("avg_turnover") is not None:
                st.markdown(f"- `Average Turnover`: `{float(meta['avg_turnover']):.2%}`")
            if meta.get("estimated_cost_total") is not None:
                st.markdown(f"- `Estimated Cost Total`: `{float(meta['estimated_cost_total']):,.1f}`")
            if meta.get("validation_status"):
                st.markdown(f"- `Validation Status`: `{meta['validation_status']}`")
            if meta.get("benchmark_policy_status"):
                st.markdown(f"- `Benchmark Policy Status`: `{meta['benchmark_policy_status']}`")
            if meta.get("liquidity_policy_status"):
                st.markdown(f"- `Liquidity Policy Status`: `{meta['liquidity_policy_status']}`")
            if meta.get("validation_policy_status"):
                st.markdown(f"- `Validation Policy Status`: `{meta['validation_policy_status']}`")
            if meta.get("guardrail_policy_status"):
                st.markdown(f"- `Guardrail Policy Status`: `{meta['guardrail_policy_status']}`")
            if meta.get("promotion_decision"):
                st.markdown(f"- `Promotion Decision`: `{meta['promotion_decision']}`")
            if meta.get("promotion_next_step"):
                st.markdown(f"- `Promotion Next Step`: `{meta['promotion_next_step']}`")
            if meta.get("shortlist_status"):
                st.markdown(
                    f"- `Shortlist Status`: `{meta['shortlist_status']}` "
                    f"(`{_shortlist_status_value_to_label(meta.get('shortlist_status'))}`)"
                )
            if meta.get("shortlist_next_step"):
                st.markdown(f"- `Shortlist Next Step`: `{meta['shortlist_next_step']}`")
            if meta.get("shortlist_family"):
                st.markdown(f"- `Shortlist Family`: `{meta['shortlist_family']}`")
            if meta.get("probation_status"):
                st.markdown(
                    f"- `Probation Status`: `{meta['probation_status']}` "
                    f"(`{_probation_status_value_to_label(meta.get('probation_status'))}`)"
                )
            if meta.get("probation_stage"):
                st.markdown(f"- `Probation Stage`: `{meta['probation_stage']}`")
            if meta.get("probation_review_frequency"):
                st.markdown(f"- `Probation Review Frequency`: `{meta['probation_review_frequency']}`")
            if meta.get("probation_next_step"):
                st.markdown(f"- `Probation Next Step`: `{meta['probation_next_step']}`")
            if meta.get("monitoring_status"):
                st.markdown(
                    f"- `Monitoring Status`: `{meta['monitoring_status']}` "
                    f"(`{_monitoring_status_value_to_label(meta.get('monitoring_status'))}`)"
                )
            if meta.get("monitoring_review_frequency"):
                st.markdown(f"- `Monitoring Review Frequency`: `{meta['monitoring_review_frequency']}`")
            if meta.get("monitoring_next_step"):
                st.markdown(f"- `Monitoring Next Step`: `{meta['monitoring_next_step']}`")
            if meta.get("monitoring_focus"):
                st.markdown(
                    "- `Monitoring Focus`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("monitoring_focus") or []))
                )
            if meta.get("monitoring_breach_signals"):
                st.markdown(
                    "- `Monitoring Breach Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("monitoring_breach_signals") or []))
                )
            if meta.get("deployment_readiness_status"):
                st.markdown(
                    f"- `Deployment Readiness`: `{meta['deployment_readiness_status']}` "
                    f"(`{_deployment_readiness_status_value_to_label(meta.get('deployment_readiness_status'))}`)"
                )
            if meta.get("deployment_readiness_next_step"):
                st.markdown(f"- `Deployment Next Step`: `{meta['deployment_readiness_next_step']}`")
            if meta.get("deployment_check_pass_count") is not None:
                st.markdown(
                    f"- `Deployment Checklist Counts`: pass `{int(meta.get('deployment_check_pass_count') or 0)}`, "
                    f"watch `{int(meta.get('deployment_check_watch_count') or 0)}`, "
                    f"fail `{int(meta.get('deployment_check_fail_count') or 0)}`, "
                    f"unavailable `{int(meta.get('deployment_check_unavailable_count') or 0)}`"
                )
            if meta.get("rolling_review_status"):
                st.markdown(
                    f"- `Rolling Review`: `{meta['rolling_review_status']}` "
                    f"(`{_review_status_value_to_label(meta.get('rolling_review_status'))}`)"
                )
            if meta.get("rolling_review_window_label"):
                st.markdown(f"- `Rolling Review Window`: `{meta['rolling_review_window_label']}`")
            if meta.get("rolling_review_recent_excess_return") is not None:
                st.markdown(
                    f"- `Recent Window Excess`: `{float(meta.get('rolling_review_recent_excess_return') or 0.0):.2%}`"
                )
            if meta.get("out_of_sample_review_status"):
                st.markdown(
                    f"- `Out-Of-Sample Review`: `{meta['out_of_sample_review_status']}` "
                    f"(`{_review_status_value_to_label(meta.get('out_of_sample_review_status'))}`)"
                )
            if meta.get("out_of_sample_out_sample_excess_return") is not None:
                st.markdown(
                    f"- `Out-Of-Sample Excess`: `{float(meta.get('out_of_sample_out_sample_excess_return') or 0.0):.2%}`"
                )
            if meta.get("strategy_max_drawdown") is not None:
                st.markdown(f"- `Strategy Max Drawdown`: `{float(meta['strategy_max_drawdown']):.2%}`")
            if meta.get("benchmark_max_drawdown") is not None:
                st.markdown(f"- `Benchmark Max Drawdown`: `{float(meta['benchmark_max_drawdown']):.2%}`")
            if meta.get("drawdown_gap_vs_benchmark") is not None:
                st.markdown(f"- `Drawdown Gap vs Benchmark`: `{float(meta['drawdown_gap_vs_benchmark']):.2%}`")
            if meta.get("rolling_underperformance_share") is not None:
                st.markdown(
                    f"- `Rolling Underperformance`: share `{float(meta['rolling_underperformance_share']):.2%}`, "
                    f"current streak `{int(meta.get('rolling_underperformance_current_streak') or 0)}`, "
                    f"worst excess `{float(meta.get('rolling_underperformance_worst_excess_return') or 0.0):.2%}`"
                )
            if meta.get("promotion_rationale"):
                st.markdown(
                    "- `Promotion Rationale`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("promotion_rationale") or []))
                )
            if meta.get("benchmark_policy_watch_signals"):
                st.markdown(
                    "- `Benchmark Policy Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("benchmark_policy_watch_signals") or []))
                )
            if meta.get("guardrail_policy_watch_signals"):
                st.markdown(
                    "- `Guardrail Policy Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("guardrail_policy_watch_signals") or []))
                )
            if meta.get("dynamic_candidate_count") is not None:
                st.markdown(
                    f"- `Dynamic Candidate Pool`: `{meta.get('dynamic_candidate_count')}` "
                    f"(target `{meta.get('dynamic_target_size') or '-'}`)"
                )
            if dynamic_snapshot_rows or dynamic_candidate_status_rows:
                st.markdown(
                    f"- `Dynamic Detail Rows`: snapshot `{len(dynamic_snapshot_rows)}`, "
                    f"candidate `{len(dynamic_candidate_status_rows)}`"
                )
            if meta.get("trend_filter_enabled"):
                st.markdown(f"- `Trend Filter`: `MA{meta.get('trend_filter_window', STRICT_TREND_FILTER_DEFAULT_WINDOW)}`")
            if meta.get("market_regime_enabled"):
                st.markdown(
                    f"- `Market Regime`: `{meta.get('market_regime_benchmark', STRICT_MARKET_REGIME_DEFAULT_BENCHMARK)} < MA{meta.get('market_regime_window', STRICT_MARKET_REGIME_DEFAULT_WINDOW)} => cash`"
                )
            price_freshness = meta.get("price_freshness") or {}
            freshness_details = price_freshness.get("details") or {}
            if freshness_details:
                st.markdown(
                    f"- `Price Freshness`: common `{freshness_details.get('common_latest_date', '-')}`, "
                    f"newest `{freshness_details.get('newest_latest_date', '-')}`, "
                    f"spread `{freshness_details.get('spread_days', 0)}d`"
                )
            universe_debug = meta.get("universe_debug") or {}
            if universe_debug:
                st.markdown(
                    f"- `Membership Count`: avg `{universe_debug.get('avg_membership_count', '-')}`, "
                    f"min `{universe_debug.get('min_membership_count', '-')}`, "
                    f"max `{universe_debug.get('max_membership_count', '-')}`"
                )
                if universe_debug.get("price_window_start") or universe_debug.get("price_window_end"):
                    st.markdown(
                        f"- `Price Window`: `{universe_debug.get('price_window_start', '-')}` -> `{universe_debug.get('price_window_end', '-')}`"
                    )
                if universe_debug.get("profile_delisted_count") is not None or universe_debug.get("profile_issue_count") is not None:
                    st.markdown(
                        f"- `Profile Diagnostics`: active `{universe_debug.get('profile_active_count', '-')}`, "
                        f"delisted `{universe_debug.get('profile_delisted_count', '-')}`, "
                        f"issue `{universe_debug.get('profile_issue_count', '-')}`"
                    )
        with right:
            st.markdown("##### Runtime Metadata")
            st.json(meta)

def _build_balance_compare_view(bundles: list[dict]) -> pd.DataFrame:
    series_list = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy()
        name = bundle["strategy_name"]
        series = chart_df.set_index("Date")["Total Balance"].rename(name)
        series_list.append(series)

    return pd.concat(series_list, axis=1).sort_index()

def _build_monthly_component_balance_views(
    bundles: list[dict],
    *,
    strategy_names: list[str],
    weights: list[float],
    date_policy: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly_balances = []
    for bundle, strategy_name in zip(bundles, strategy_names):
        result_df = bundle["result_df"].copy()
        result_df["Date"] = pd.to_datetime(result_df["Date"])
        result_df["_month"] = result_df["Date"].dt.to_period("M")
        monthly_df = result_df.groupby("_month", as_index=False).agg(TotalBalance=("Total Balance", "mean"))
        monthly_df["Date"] = monthly_df["_month"].dt.to_timestamp("M")
        monthly_df = monthly_df.drop(columns=["_month"]).set_index("Date").sort_index()
        monthly_balances.append(monthly_df.rename(columns={"TotalBalance": strategy_name}))

    join_how = "outer" if date_policy == "union" else "inner"
    balance_wide = pd.concat(monthly_balances, axis=1, join=join_how).sort_index()

    normalized_weights = pd.Series(weights, index=strategy_names, dtype=float)
    normalized_weights = normalized_weights / normalized_weights.sum()

    weight_frame = balance_wide.notna().mul(normalized_weights, axis=1)
    denominator = weight_frame.sum(axis=1).replace(0, pd.NA)
    contribution_amount = balance_wide.mul(normalized_weights, axis=1).div(denominator, axis=0)
    contribution_share = contribution_amount.div(contribution_amount.sum(axis=1), axis=0)

    return contribution_amount, contribution_share

def _build_drawdown_compare_view(bundles: list[dict]) -> pd.DataFrame:
    drawdown_frames = []
    for bundle in bundles:
        result_df = bundle["result_df"].copy().sort_values("Date")
        balance = result_df["Total Balance"]
        drawdown = (balance / balance.cummax() - 1).rename(bundle["strategy_name"])
        drawdown_frames.append(pd.DataFrame({"Date": result_df["Date"], bundle["strategy_name"]: drawdown}))

    merged = drawdown_frames[0]
    for frame in drawdown_frames[1:]:
        merged = merged.merge(frame, on="Date", how="outer")

    return merged.sort_values("Date").set_index("Date")

def _build_total_return_compare_view(bundles: list[dict]) -> pd.DataFrame:
    series_list = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy()
        name = bundle["strategy_name"]
        series = chart_df.set_index("Date")["Total Return"].rename(name)
        series_list.append(series)

    return pd.concat(series_list, axis=1).sort_index()

def _build_period_extremes_tables(result_df: pd.DataFrame, top_n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    period_df = (
        result_df[["Date", "Total Return", "Total Balance"]]
        .dropna(subset=["Total Return"])
        .sort_values("Date")
        .copy()
    )

    best = (
        period_df.sort_values("Total Return", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    worst = (
        period_df.sort_values("Total Return", ascending=True)
        .head(top_n)
        .reset_index(drop=True)
    )
    return best, worst

def _build_balance_extremes_tables(chart_df: pd.DataFrame, top_n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    balance_df = (
        chart_df[["Date", "Total Balance", "Total Return"]]
        .dropna(subset=["Total Balance"])
        .sort_values("Date")
        .copy()
    )

    highs = (
        balance_df.sort_values("Total Balance", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    lows = (
        balance_df.sort_values("Total Balance", ascending=True)
        .head(top_n)
        .reset_index(drop=True)
    )
    return highs, lows

def _build_balance_marker_df(chart_df: pd.DataFrame, result_df: pd.DataFrame | None = None) -> pd.DataFrame:
    base_df = chart_df.copy()
    base_df["Date"] = pd.to_datetime(base_df["Date"])

    high_idx = base_df["Total Balance"].idxmax()
    low_idx = base_df["Total Balance"].idxmin()
    end_idx = base_df.index[-1]

    marker_df = pd.concat(
        [
            pd.DataFrame([base_df.loc[high_idx]]).assign(Marker="High"),
            pd.DataFrame([base_df.loc[low_idx]]).assign(Marker="Low"),
            pd.DataFrame([base_df.loc[end_idx]]).assign(Marker="End"),
        ],
        ignore_index=True,
    ).drop_duplicates(subset=["Date", "Marker"])

    if result_df is not None and not result_df.empty:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=1)
        if not best_df.empty:
            best_row = base_df.loc[base_df["Date"] == pd.to_datetime(best_df.iloc[0]["Date"])]
            if not best_row.empty:
                marker_df = pd.concat(
                    [marker_df, best_row.assign(Marker="Best Period")],
                    ignore_index=True,
                )
        if not worst_df.empty:
            worst_row = base_df.loc[base_df["Date"] == pd.to_datetime(worst_df.iloc[0]["Date"])]
            if not worst_row.empty:
                marker_df = pd.concat(
                    [marker_df, worst_row.assign(Marker="Worst Period")],
                    ignore_index=True,
                )

    return marker_df.drop_duplicates(subset=["Date", "Marker"])

def _render_balance_chart_with_markers(
    chart_df: pd.DataFrame,
    *,
    result_df: pd.DataFrame | None = None,
    title: str = "Equity Curve",
) -> None:
    base_df = chart_df.copy()
    base_df["Date"] = pd.to_datetime(base_df["Date"])
    marker_df = _build_balance_marker_df(chart_df, result_df)

    line = (
        alt.Chart(base_df)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Total Balance:Q", title="Total Balance"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Total Balance:Q", title="Total Balance", format=",.1f"),
                alt.Tooltip("Total Return:Q", title="Total Return", format=".3f"),
            ],
        )
    )

    points = (
        alt.Chart(marker_df)
        .mark_point(size=90, filled=True)
        .encode(
            x="Date:T",
            y="Total Balance:Q",
            color=alt.Color(
                "Marker:N",
                scale=alt.Scale(
                    domain=["High", "Low", "End", "Best Period", "Worst Period"],
                    range=["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"],
                ),
            ),
            tooltip=[
                alt.Tooltip("Marker:N", title="Marker"),
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Total Balance:Q", title="Total Balance", format=",.1f"),
            ],
        )
    )

    labels = (
        alt.Chart(marker_df)
        .mark_text(align="left", dx=8, dy=-8, fontSize=12)
        .encode(
            x="Date:T",
            y="Total Balance:Q",
            text="Marker:N",
            color=alt.value("#444"),
        )
    )

    st.altair_chart(
        (line + points + labels).properties(height=360, title=title),
        use_container_width=True,
    )

def _render_dynamic_universe_details(bundle: dict[str, Any]) -> None:
    meta = bundle.get("meta") or {}
    universe_debug = meta.get("universe_debug") or {}
    snapshot_rows = bundle.get("dynamic_universe_snapshot_rows") or []
    candidate_status_rows = bundle.get("dynamic_candidate_status_rows") or []

    if (
        not snapshot_rows
        and not candidate_status_rows
        and meta.get("universe_contract") != HISTORICAL_DYNAMIC_PIT_UNIVERSE
    ):
        st.caption("이번 결과는 `Historical Dynamic PIT Universe` run이 아니어서 dynamic universe 상세가 없습니다.")
        return

    st.caption(
        "`Historical Dynamic PIT Universe`에서는 리밸런싱 날짜마다 모집군을 다시 계산합니다. "
        "`dynamic_universe_snapshot_rows`는 날짜별 membership/continuity 요약이고, "
        "`dynamic_candidate_status_rows`는 후보 심볼별 가격 이력과 profile 상태를 보여줍니다."
    )

    if universe_debug:
        summary_cols = st.columns(4)
        summary_cols[0].metric("Candidate Pool", universe_debug.get("candidate_pool_count", "-"))
        summary_cols[1].metric("Target Size", universe_debug.get("target_size", "-"))
        summary_cols[2].metric("Membership Avg", universe_debug.get("avg_membership_count", "-"))
        summary_cols[3].metric("Turnover Avg", universe_debug.get("avg_turnover_count", "-"))

    if snapshot_rows:
        st.markdown("##### dynamic_universe_snapshot_rows")
        st.caption(
            "각 행은 리밸런싱 날짜 1개입니다. "
            "`membership_count`는 실제 편입 수, "
            "`continuity_ready_count`는 그 날짜를 가격 이력상 자연스럽게 커버하는 후보 수, "
            "`pre_listing_excluded_count` / `post_last_price_excluded_count`는 상장 전 또는 마지막 가격 이후라 제외된 후보 수입니다."
        )
        st.dataframe(pd.DataFrame(snapshot_rows), use_container_width=True, hide_index=True)

    if candidate_status_rows:
        st.markdown("##### dynamic_candidate_status_rows")
        st.caption(
            "각 행은 후보 심볼 1개입니다. "
            "`first_price_date` / `last_price_date`는 현재 DB 가격 이력 범위, "
            "`profile_status` / `profile_delisted_at`는 asset profile 기준 continuity 힌트입니다."
        )
        st.dataframe(pd.DataFrame(candidate_status_rows), use_container_width=True, hide_index=True)

def _build_next_step_readiness_evaluation(meta: dict[str, Any]) -> dict[str, Any]:
    promotion = str(meta.get("promotion_decision") or "").strip().lower()
    deployment = str(meta.get("deployment_readiness_status") or "").strip().lower()
    issue_rows = _build_stage_issue_resolution_rows(meta)
    severe_statuses = {"caution", "unavailable", "error", "missing"}
    severe_issue_rows = [
        row
        for row in issue_rows
        if str(row.get("현재 상태") or "").strip().lower() in severe_statuses
    ]
    softer_issue_rows = [
        row
        for row in issue_rows
        if str(row.get("현재 상태") or "").strip().lower() in {"watch", "warning"}
    ]

    fail_count = int(meta.get("deployment_check_fail_count") or 0)
    watch_count = int(meta.get("deployment_check_watch_count") or 0)
    unavailable_count = int(meta.get("deployment_check_unavailable_count") or 0)

    if promotion == "real_money_candidate":
        promotion_score = 4.0
        promotion_judgment = "강한 통과 신호"
    elif promotion == "production_candidate":
        promotion_score = 3.0
        promotion_judgment = "비교 가능, 추가 검토 필요"
    elif promotion and promotion != "hold":
        promotion_score = 2.0
        promotion_judgment = "비교 가능성은 있으나 보수적 확인 필요"
    else:
        promotion_score = 0.0
        promotion_judgment = "hold 해결 전에는 다음 단계 보류"

    if deployment == "small_capital_ready":
        deployment_score = 3.0
        deployment_judgment = "deployment checklist가 강함"
    elif deployment in {"small_capital_ready_with_review", "paper_only"}:
        deployment_score = 2.5
        deployment_judgment = "다음 검토로 넘기기 충분"
    elif deployment == "watchlist_only":
        deployment_score = 2.0
        deployment_judgment = "watchlist로 비교 가능"
    elif deployment == "review_required":
        deployment_score = 1.5
        deployment_judgment = "비교는 가능하지만 checklist 재확인 필요"
    else:
        deployment_score = 0.0
        deployment_judgment = "blocked 또는 상태 부족"

    if severe_issue_rows:
        blocker_score = 0.0
        blocker_judgment = "핵심 blocker가 남아 있음"
    elif fail_count > 0 or watch_count > 0 or unavailable_count > 0 or softer_issue_rows:
        blocker_score = 2.0
        blocker_judgment = "진행 가능하지만 개선 항목 있음"
    else:
        blocker_score = 3.0
        blocker_judgment = "핵심 blocker 없음"

    score = round(promotion_score + deployment_score + blocker_score, 1)
    can_move_to_compare = (
        promotion not in {"", "hold"}
        and deployment not in {"", "blocked"}
        and not severe_issue_rows
    )

    if can_move_to_compare and score >= 8.0:
        verdict = "5단계 Compare 진행 가능"
        tone = "success"
        next_action = "Compare에서 다른 후보와 성과, data trust, Real-Money 상태를 비교합니다."
    elif can_move_to_compare:
        verdict = "5단계 Compare 진행 가능, 개선 항목 동시 확인"
        tone = "warning"
        next_action = "Compare로 넘기되 watch / checklist 항목을 같이 열어보고 후보 등록은 보수적으로 판단합니다."
    else:
        verdict = "4단계에서 먼저 blocker 해결"
        tone = "error"
        next_action = "Hold 해결 가이드, Deployment checklist, 실행 부담 / 검토 근거의 caution 항목을 먼저 정리합니다."

    blocking_reasons: list[str] = []
    if promotion in {"", "hold"}:
        blocking_reasons.append("Promotion Decision이 hold이거나 비어 있음")
    if deployment in {"", "blocked"}:
        blocking_reasons.append("Deployment Readiness가 blocked이거나 비어 있음")
    blocking_reasons.extend(
        f"{row.get('항목')}: {row.get('현재 상태')}"
        for row in severe_issue_rows
    )

    review_reasons: list[str] = []
    if fail_count > 0:
        review_reasons.append(f"Deployment checklist fail {fail_count}개")
    if watch_count > 0:
        review_reasons.append(f"Deployment checklist watch {watch_count}개")
    if unavailable_count > 0:
        review_reasons.append(f"Deployment checklist unavailable {unavailable_count}개")
    review_reasons.extend(
        f"{row.get('항목')}: {row.get('현재 상태')}"
        for row in softer_issue_rows
    )

    criteria_rows = [
        {
            "기준": "Promotion Decision",
            "현재 값": promotion or "-",
            "점수": f"{promotion_score:g} / 4",
            "판단": promotion_judgment,
        },
        {
            "기준": "Deployment Readiness",
            "현재 값": deployment or "-",
            "점수": f"{deployment_score:g} / 3",
            "판단": deployment_judgment,
        },
        {
            "기준": "Core Blocker",
            "현재 값": "없음" if not severe_issue_rows else f"{len(severe_issue_rows)}개",
            "점수": f"{blocker_score:g} / 3",
            "판단": blocker_judgment,
        },
    ]

    return {
        "score": score,
        "verdict": verdict,
        "tone": tone,
        "next_action": next_action,
        "can_move_to_compare": can_move_to_compare,
        "criteria_rows": criteria_rows,
        "blocking_reasons": blocking_reasons,
        "review_reasons": review_reasons,
    }

def _render_next_step_readiness_box(meta: dict[str, Any]) -> None:
    evaluation = _build_next_step_readiness_evaluation(meta)
    score = float(evaluation["score"])
    tone = str(evaluation["tone"])

    with st.container(border=True):
        st.markdown("##### 5단계 Compare 진입 평가")
        st.caption(
            "이 박스는 투자 승인 기준이 아니라, `Hold 해결`을 마치고 "
            "`Compare`에서 다른 후보와 비교해 볼 수 있는지 빠르게 판단하는 표지입니다."
        )
        metric_cols = st.columns([0.24, 0.76], gap="small")
        metric_cols[0].metric("Readiness Score", f"{score:.1f} / 10")
        with metric_cols[1]:
            st.caption("판정")
            st.markdown(f"**{evaluation['verdict']}**")
            st.caption("다음 행동")
            st.markdown(str(evaluation["next_action"]))
        st.progress(max(0.0, min(score / 10.0, 1.0)))
        st.caption(
            "점수 기준: `8.0점 이상`은 깔끔한 진행, `8.0점 미만`이어도 핵심 3조건을 만족하면 조건부 진행, "
            "핵심 3조건을 만족하지 못하면 점수와 무관하게 4단계에서 먼저 멈춥니다."
        )

        message = (
            f"{evaluation['verdict']}: "
            f"`Promotion Decision != hold`, `Deployment != blocked`, 핵심 blocker 없음 기준으로 계산했습니다."
        )
        if tone == "success":
            st.success(message)
        elif tone == "warning":
            st.warning(message)
        else:
            st.error(message)

        if evaluation["blocking_reasons"]:
            st.caption("막는 항목: " + ", ".join(f"`{item}`" for item in evaluation["blocking_reasons"]))
        elif evaluation["review_reasons"]:
            st.caption("같이 볼 개선 항목: " + ", ".join(f"`{item}`" for item in evaluation["review_reasons"]))
        else:
            st.caption("핵심 blocker가 보이지 않습니다. Compare로 넘겨 상대 후보와 비교해도 되는 상태입니다.")

        with st.expander("점수 계산 기준 보기", expanded=False):
            st.dataframe(pd.DataFrame(evaluation["criteria_rows"]), use_container_width=True, hide_index=True)
            st.caption(
                "`real_money_candidate`는 가장 강한 Compare 진입 신호이고, "
                "`production_candidate`는 Compare에는 올릴 수 있지만 후보 등록 전 추가 검토가 필요한 상태입니다."
            )

def _render_real_money_details(bundle: dict[str, Any]) -> None:
    meta = bundle.get("meta") or {}
    if not meta.get("real_money_hardening"):
        st.caption("이 결과에는 Phase 12 real-money hardening 정보가 없습니다.")
        return

    result_df = bundle.get("result_df")
    benchmark_chart_df = bundle.get("benchmark_chart_df")
    benchmark_summary_df = bundle.get("benchmark_summary_df")

    def _render_value_list_caption(prefix: str, values: list[Any] | tuple[Any, ...] | None) -> None:
        if values:
            st.caption(prefix + ": " + ", ".join(f"`{value}`" for value in list(values)))

    def _section_header(title: str, description: str):
        section = st.container(border=True)
        with section:
            st.markdown(f"##### {title}")
            st.caption(description)
        return section

    def _status_tone(value: Any) -> str:
        normalized = str(value or "").strip().lower()
        if any(term in normalized for term in ["hold", "blocked", "reject", "fail", "caution", "breach"]):
            return "danger"
        if any(term in normalized for term in ["watch", "review", "production", "unavailable"]):
            return "warning"
        if any(term in normalized for term in ["real_money", "paper", "small_capital", "routine", "normal", "ready"]):
            return "positive"
        return "neutral"

    def _render_real_money_cards(cards: list[dict[str, Any]]) -> None:
        render_status_card_grid(cards)

    st.info(
        "이 탭은 실전형 해석을 한 번에 보기 위한 화면입니다. "
        "먼저 `현재 판단`에서 지금 상태를 보고, "
        "그다음 `검토 근거`에서 왜 그런 판단이 나왔는지 확인하고, "
        "`실행 부담`에서 비용/유동성/ETF 운용 가능성을 본 뒤, "
        "마지막 `상세 데이터`에서 원자료를 확인하면 됩니다."
    )

    _render_real_money_cards(
        [
            {
                "title": "Promotion",
                "value": str(meta.get("promotion_decision") or "-").upper(),
                "detail": meta.get("promotion_next_step") or "",
                "tone": _status_tone(meta.get("promotion_decision")),
            },
            {
                "title": "Shortlist",
                "value": _shortlist_status_value_to_label(meta.get("shortlist_status")),
                "detail": meta.get("shortlist_next_step") or "",
                "tone": _status_tone(meta.get("shortlist_status")),
            },
            {
                "title": "Probation",
                "value": _probation_status_value_to_label(meta.get("probation_status")),
                "detail": meta.get("probation_review_frequency") or "",
                "tone": _status_tone(meta.get("probation_status")),
            },
            {
                "title": "Deployment",
                "value": _deployment_readiness_status_value_to_label(meta.get("deployment_readiness_status")),
                "detail": meta.get("deployment_readiness_next_step") or "",
                "tone": _status_tone(meta.get("deployment_readiness_status")),
            },
            {
                "title": "Rolling Review",
                "value": _review_status_value_to_label(meta.get("rolling_review_status")),
                "detail": meta.get("rolling_review_window_label") or "",
                "tone": _status_tone(meta.get("rolling_review_status")),
            },
            {
                "title": "Validation",
                "value": _review_status_value_to_label(meta.get("validation_status")),
                "detail": meta.get("validation_window_label") or "",
                "tone": _status_tone(meta.get("validation_status")),
            },
        ]
    )

    overview_tab, review_tab, execution_tab, detail_tab = st.tabs(
        ["현재 판단", "검토 근거", "실행 부담", "상세 데이터"]
    )

    with overview_tab:
        st.caption(
            "이 섹션은 이 전략을 지금 어떤 단계로 해석해야 하는지 보여줍니다. "
            "즉 `당장 보류할지`, `paper probation으로 둘지`, `소액 trial까지 볼지`를 먼저 판단하는 곳입니다."
        )
        _render_next_step_readiness_box(meta)

        if meta.get("promotion_decision"):
            with _section_header("전략 승격 판단", "이 전략이 현재 계약 기준에서 어느 정도까지 올라왔는지 보여줍니다."):
                decision = str(meta.get("promotion_decision") or "-")
                next_step = str(meta.get("promotion_next_step") or "-")
                _render_real_money_cards(
                    [
                        {
                            "title": "Decision",
                            "value": decision.upper(),
                            "detail": "현재 승격 판정",
                            "tone": _status_tone(decision),
                        },
                        {
                            "title": "Next Step",
                            "value": next_step,
                            "detail": "이 판정에서 이어지는 처리",
                            "tone": _status_tone(decision),
                        },
                    ]
                )
                rationale = list(meta.get("promotion_rationale") or [])
                if rationale:
                    st.caption("왜 이렇게 판단했는지: " + ", ".join(f"`{item}`" for item in rationale))
                if decision == "real_money_candidate":
                    st.success(
                        "현재 계약 기준에서는 실전형 후보로 읽을 수 있는 상태입니다. "
                        "다음 단계는 paper tracking 또는 소액 probation이 자연스럽습니다."
                    )
                elif decision == "production_candidate":
                    st.info(
                        "지금은 많이 정리된 상태이지만, 더 강한 robustness 검토 전까지는 "
                        "production candidate로 두는 편이 맞습니다."
                    )
                elif decision == "hold":
                    st.warning(
                        "현재 run은 바로 승격하기보다 hold로 보는 편이 맞습니다. "
                        "validation gap 또는 contract issue를 먼저 정리하는 것이 좋습니다."
                    )
                    hold_guidance_rows = _build_hold_resolution_guidance_rows(meta)
                    with st.container(border=True):
                        st.markdown("##### Hold 해결 가이드")
                        st.caption(
                            "이 전략이 무조건 나쁘다는 뜻은 아닙니다. "
                            "지금은 승격 전에 먼저 풀어야 하는 검증 blocker가 있다는 뜻입니다."
                        )
                        st.caption(
                            "아래 표에서 `현재 상태`는 지금 막히는 정도를, "
                            "`상태를 보는 위치`는 실제 화면 위치를, "
                            "`바로 해볼 일`은 가장 먼저 손댈 설정이나 데이터를 뜻합니다."
                        )
                        if hold_guidance_rows:
                            st.dataframe(
                                pd.DataFrame(hold_guidance_rows),
                                use_container_width=True,
                                hide_index=True,
                            )
                        st.info(
                            "먼저 `검토 근거`에서 막히는 항목을 확인하고, "
                            "필요하면 `실행 부담`에서 유동성 / 비용 / ETF 운용 가능성까지 같이 점검하면 가장 빠릅니다."
                        )

        if meta.get("shortlist_status"):
            with _section_header("후보 전략 숏리스트", "실전 후보 목록 안에서 현재 어느 단계인지 보여줍니다."):
                shortlist_status = str(meta.get("shortlist_status") or "-")
                shortlist_next_step = str(meta.get("shortlist_next_step") or "-")
                shortlist_family = str(meta.get("shortlist_family") or meta.get("strategy_family") or "-")
                _render_real_money_cards(
                    [
                        {
                            "title": "Family",
                            "value": shortlist_family,
                            "detail": "후보가 속한 전략군",
                            "tone": "neutral",
                        },
                        {
                            "title": "Status",
                            "value": _shortlist_status_value_to_label(shortlist_status),
                            "detail": "숏리스트 단계",
                            "tone": _status_tone(shortlist_status),
                        },
                        {
                            "title": "Next Step",
                            "value": shortlist_next_step,
                            "detail": "다음 검토 행동",
                            "tone": _status_tone(shortlist_status),
                        },
                    ]
                )
                shortlist_rationale = list(meta.get("shortlist_rationale") or [])
                if shortlist_rationale:
                    st.caption("숏리스트 판단 근거: " + ", ".join(f"`{item}`" for item in shortlist_rationale))
                if shortlist_status == "small_capital_trial":
                    st.success(
                        "현재 계약 기준에서는 소액 실전 trial까지 검토할 수 있는 shortlist 상태입니다. "
                        "다만 월별 review 기록은 계속 남기는 편이 맞습니다."
                    )
                elif shortlist_status == "paper_probation":
                    st.info(
                        "현재 run은 paper probation으로 먼저 관찰하는 편이 가장 자연스럽습니다. "
                        "다음 review를 통과하면 소액 trial을 검토할 수 있습니다."
                    )
                elif shortlist_status == "watchlist":
                    st.info(
                        "지금은 shortlist watchlist로 두고, 추가 robustness / monitoring review를 거친 뒤 "
                        "paper probation으로 올리는 편이 맞습니다."
                    )
                elif shortlist_status == "hold":
                    st.warning(
                        "현재 run은 shortlist 단계로 올리기보다 hold로 두는 편이 맞습니다. "
                        "promotion / policy gap을 먼저 정리한 뒤 다시 보는 것이 좋습니다."
                    )

        if meta.get("probation_status") or meta.get("monitoring_status"):
            with _section_header(
                "Probation / Monitoring",
                "실제 운용 전 관찰 단계입니다. paper tracking 중인지, routine review로 충분한지, breach 신호가 있는지를 봅니다.",
            ):
                probation_status = str(meta.get("probation_status") or "-")
                probation_stage = str(meta.get("probation_stage") or "-")
                probation_review_frequency = str(meta.get("probation_review_frequency") or "-")
                monitoring_status = str(meta.get("monitoring_status") or "-")
                monitoring_review_frequency = str(meta.get("monitoring_review_frequency") or "-")
                _render_real_money_cards(
                    [
                        {
                            "title": "Probation",
                            "value": _probation_status_value_to_label(probation_status),
                            "detail": "운영 전 관찰 상태",
                            "tone": _status_tone(probation_status),
                        },
                        {
                            "title": "Stage",
                            "value": probation_stage,
                            "detail": "현재 probation 단계",
                            "tone": _status_tone(probation_status),
                        },
                        {
                            "title": "Probation Review",
                            "value": probation_review_frequency,
                            "detail": "점검 주기",
                            "tone": "neutral",
                        },
                        {
                            "title": "Monitoring",
                            "value": _monitoring_status_value_to_label(monitoring_status),
                            "detail": meta.get("monitoring_next_step") or "운영 감시 상태",
                            "tone": _status_tone(monitoring_status),
                        },
                        {
                            "title": "Monitoring Review",
                            "value": monitoring_review_frequency,
                            "detail": "감시 점검 주기",
                            "tone": "neutral",
                        },
                    ]
                )
                if meta.get("probation_next_step"):
                    st.caption(f"다음 probation 액션: `{meta.get('probation_next_step')}`")
                probation_rationale = list(meta.get("probation_rationale") or [])
                if probation_rationale:
                    st.caption("Probation 판단 근거: " + ", ".join(f"`{item}`" for item in probation_rationale))
                monitoring_focus = list(meta.get("monitoring_focus") or [])
                if monitoring_focus:
                    st.caption("지켜볼 항목: " + ", ".join(f"`{item}`" for item in monitoring_focus))
                monitoring_breach_signals = list(meta.get("monitoring_breach_signals") or [])
                if monitoring_breach_signals:
                    st.caption("경고 신호: " + ", ".join(f"`{item}`" for item in monitoring_breach_signals))

                if monitoring_status == "breach_watch":
                    st.warning(
                        "현재 probation 단계에서 breach signal이 관찰됐습니다. "
                        "비중 확대보다는 월별 review와 rule re-check를 먼저 하는 편이 맞습니다."
                    )
                elif monitoring_status == "heightened_review":
                    st.info(
                        "지금은 monitoring watch signal이 있어서, routine review보다 조금 더 보수적으로 월별 확인을 이어가는 편이 좋습니다."
                    )
                elif monitoring_status == "routine_review":
                    st.success("현재 기준에서는 routine monthly review로 probation을 이어갈 수 있는 상태입니다.")

        if meta.get("deployment_readiness_status"):
            with _section_header(
                "Deployment Readiness",
                "실제 배치 직전 체크리스트입니다. pass / watch / fail / unavailable 개수를 보고 지금 배치를 열어도 되는지 판단합니다.",
            ):
                deployment_status = str(meta.get("deployment_readiness_status") or "-")
                deployment_next_step = str(meta.get("deployment_readiness_next_step") or "-")
                _render_real_money_cards(
                    [
                        {
                            "title": "Status",
                            "value": _deployment_readiness_status_value_to_label(deployment_status),
                            "detail": "현재 배치 준비 상태",
                            "tone": _status_tone(deployment_status),
                        },
                        {
                            "title": "Next Step",
                            "value": deployment_next_step,
                            "detail": "다음 처리",
                            "tone": _status_tone(deployment_status),
                        },
                        {
                            "title": "Pass",
                            "value": str(int(meta.get("deployment_check_pass_count") or 0)),
                            "detail": "통과 체크",
                            "tone": "positive",
                        },
                        {
                            "title": "Watch",
                            "value": str(int(meta.get("deployment_check_watch_count") or 0)),
                            "detail": "관찰 체크",
                            "tone": "warning" if int(meta.get("deployment_check_watch_count") or 0) else "neutral",
                        },
                        {
                            "title": "Fail",
                            "value": str(int(meta.get("deployment_check_fail_count") or 0)),
                            "detail": "막는 체크",
                            "tone": "danger" if int(meta.get("deployment_check_fail_count") or 0) else "neutral",
                        },
                        {
                            "title": "Unavailable",
                            "value": str(int(meta.get("deployment_check_unavailable_count") or 0)),
                            "detail": "판단 불가 체크",
                            "tone": "warning" if int(meta.get("deployment_check_unavailable_count") or 0) else "neutral",
                        },
                    ]
                )

                deployment_rationale = list(meta.get("deployment_readiness_rationale") or [])
                if deployment_rationale:
                    st.caption("Deployment 판단 근거: " + ", ".join(f"`{item}`" for item in deployment_rationale))

                checklist_rows = list(meta.get("deployment_checklist_rows") or [])
                if checklist_rows:
                    with st.expander("Checklist 상세 보기", expanded=deployment_status in {"review_required", "blocked"}):
                        st.dataframe(pd.DataFrame(checklist_rows), use_container_width=True, hide_index=True)

                if deployment_status == "small_capital_ready":
                    st.success("현재 checklist 기준에서는 small-capital trial까지 비교적 자연스럽게 볼 수 있는 상태입니다.")
                elif deployment_status == "small_capital_ready_with_review":
                    st.info(
                        "현재 checklist 기준에서는 소액 trial은 가능하지만, watch / unavailable 항목을 같이 보면서 더 보수적으로 운용하는 편이 맞습니다."
                    )
                elif deployment_status == "paper_only":
                    st.info("지금은 deployment-ready보다는 paper probation 단계로 두는 편이 맞습니다.")
                elif deployment_status == "review_required":
                    st.warning("failed checklist 항목이 있어, 수동 review 없이 바로 비중을 늘리는 것은 보수적이지 않습니다.")
                elif deployment_status == "blocked":
                    st.warning("현재 checklist 기준에서는 deployment를 열기보다 blocker를 먼저 해결하는 편이 맞습니다.")

    with review_tab:
        st.caption(
            "이 섹션은 왜 이런 결론이 나왔는지 보여줍니다. "
            "benchmark 대비 성과, 최근 구간 consistency, 정책 기준 통과 여부를 함께 보시면 됩니다."
        )

        if meta.get("benchmark_available") or meta.get("benchmark_contract") or meta.get("benchmark_ticker"):
            with _section_header(
                "Benchmark / Validation 요약",
                "benchmark와 비교했을 때 현재 run이 어느 정도로 버티는지 빠르게 읽는 요약입니다.",
            ):
                benchmark_cols = st.columns(6, gap="small")
                benchmark_cols[0].metric("Benchmark Contract", _benchmark_contract_value_to_label(meta.get("benchmark_contract")))
                benchmark_cols[1].metric(
                    "Benchmark Baseline",
                    str(
                        meta.get("benchmark_label")
                        if meta.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT
                        else meta.get("benchmark_ticker") or meta.get("benchmark_label") or "-"
                    ),
                )
                benchmark_cols[2].metric(
                    "Guardrail Reference",
                    _resolve_guardrail_reference_ticker_value(meta) or "-",
                )
                benchmark_cols[3].metric("Benchmark Available", "Yes" if meta.get("benchmark_available") else "No")
                if meta.get("benchmark_symbol_count") is not None:
                    benchmark_cols[4].metric("Benchmark Universe", str(int(meta.get("benchmark_symbol_count") or 0)))
                if meta.get("benchmark_eligible_symbol_count") is not None:
                    benchmark_cols[5].metric("Benchmark Eligible", str(int(meta.get("benchmark_eligible_symbol_count") or 0)))
                if meta.get("benchmark_end_balance") is not None:
                    st.caption(f"Benchmark End Balance `{float(meta.get('benchmark_end_balance')):,.1f}`")
                summary_lines: list[str] = []
                if meta.get("benchmark_cagr") is not None:
                    summary_lines.append(f"Benchmark CAGR `{float(meta.get('benchmark_cagr')):.2%}`")
                if meta.get("net_cagr_spread") is not None:
                    summary_lines.append(f"Net CAGR Spread `{float(meta.get('net_cagr_spread')):.2%}`")
                if meta.get("net_excess_end_balance") is not None:
                    summary_lines.append(f"Net Excess End Balance `{float(meta.get('net_excess_end_balance')):,.1f}`")
                if meta.get("benchmark_row_coverage") is not None:
                    summary_lines.append(f"Coverage `{float(meta.get('benchmark_row_coverage')):.2%}`")
                if summary_lines:
                    st.caption(" | ".join(summary_lines))
                if meta.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
                    st.caption(
                        "Candidate-universe equal-weight benchmark는 같은 후보 universe를 단순히 균등 보유했을 때의 reference curve입니다."
                    )
                    st.caption(
                        "이 경우 `Guardrail Reference`는 benchmark curve 자체가 아니라 underperformance / drawdown guardrail이 따로 참고하는 ticker입니다."
                    )

        if meta.get("benchmark_available"):
            with _section_header(
                "Validation Surface",
                "benchmark 대비 최근 구간에서 얼마나 자주 뒤처졌는지, 낙폭이 얼마나 깊었는지를 요약합니다.",
            ):
                validation_cols = st.columns(4, gap="small")
                validation_cols[0].metric("Validation Status", str(meta.get("validation_status") or "normal").upper())
                if meta.get("strategy_max_drawdown") is not None:
                    validation_cols[1].metric("Strategy Max Drawdown", f"{float(meta.get('strategy_max_drawdown')):.2%}")
                if meta.get("benchmark_max_drawdown") is not None:
                    validation_cols[2].metric("Benchmark Max Drawdown", f"{float(meta.get('benchmark_max_drawdown')):.2%}")
                validation_cols[3].metric("Rolling Window", str(meta.get("validation_window_label") or "-"))

                rolling_cols = st.columns(4, gap="small")
                if meta.get("rolling_underperformance_share") is not None:
                    rolling_cols[0].metric("Underperformance Share", f"{float(meta.get('rolling_underperformance_share')):.2%}")
                rolling_cols[1].metric("Current Underperf Streak", str(int(meta.get("rolling_underperformance_current_streak") or 0)))
                rolling_cols[2].metric("Longest Underperf Streak", str(int(meta.get("rolling_underperformance_longest_streak") or 0)))
                if meta.get("rolling_underperformance_worst_excess_return") is not None:
                    rolling_cols[3].metric(
                        "Worst Rolling Excess",
                        f"{float(meta.get('rolling_underperformance_worst_excess_return')):.2%}",
                    )
                _render_value_list_caption("Validation watch signals", meta.get("validation_watch_signals"))

                status = str(meta.get("validation_status") or "normal")
                if status == "caution":
                    st.warning(
                        "Benchmark-relative drawdown 또는 rolling underperformance 진단이 높게 나왔습니다. "
                        "실전 승격 전 재검토가 필요한 상태로 보는 편이 맞습니다."
                    )
                elif status == "watch":
                    st.info(
                        "일부 benchmark-relative validation 지표가 watch 상태입니다. "
                        "추가 구간 검증이나 contract robustness 확인이 권장됩니다."
                    )

        if meta.get("rolling_review_status") or meta.get("out_of_sample_review_status"):
            with _section_header(
                "최근 구간 / Out-of-Sample Review",
                "최근 구간과 전후반 구간을 따로 봐서, 특정 시기 우연인지 아니면 비교적 꾸준한지 확인하는 섹션입니다.",
            ):
                review_cols = st.columns(5, gap="small")
                review_cols[0].metric("Rolling Review", _review_status_value_to_label(meta.get("rolling_review_status")))
                review_cols[1].metric("Rolling Window", str(meta.get("rolling_review_window_label") or "-"))
                if meta.get("rolling_review_recent_excess_return") is not None:
                    review_cols[2].metric("Recent Excess", f"{float(meta.get('rolling_review_recent_excess_return')):.2%}")
                if meta.get("rolling_review_recent_drawdown_gap") is not None:
                    review_cols[3].metric("Recent DD Gap", f"{float(meta.get('rolling_review_recent_drawdown_gap')):.2%}")
                review_cols[4].metric("OOS Review", _review_status_value_to_label(meta.get("out_of_sample_review_status")))

                split_cols = st.columns(3, gap="small")
                if meta.get("out_of_sample_in_sample_excess_return") is not None:
                    split_cols[0].metric("In-Sample Excess", f"{float(meta.get('out_of_sample_in_sample_excess_return')):.2%}")
                if meta.get("out_of_sample_out_sample_excess_return") is not None:
                    split_cols[1].metric("Out-Sample Excess", f"{float(meta.get('out_of_sample_out_sample_excess_return')):.2%}")
                if meta.get("out_of_sample_excess_change") is not None:
                    split_cols[2].metric("Excess Change", f"{float(meta.get('out_of_sample_excess_change')):.2%}")

                if meta.get("rolling_review_recent_start") is not None and meta.get("rolling_review_recent_end") is not None:
                    st.caption(
                        "Recent review window: "
                        f"`{meta.get('rolling_review_recent_start')}` -> `{meta.get('rolling_review_recent_end')}`"
                    )
                rolling_review_rationale = list(meta.get("rolling_review_rationale") or [])
                if rolling_review_rationale:
                    st.caption("Rolling review rationale: " + ", ".join(f"`{item}`" for item in rolling_review_rationale))
                if meta.get("out_of_sample_in_sample_start") is not None and meta.get("out_of_sample_out_sample_end") is not None:
                    st.caption(
                        "Split-period review: "
                        f"in-sample `{meta.get('out_of_sample_in_sample_start')}` -> `{meta.get('out_of_sample_in_sample_end')}`, "
                        f"out-sample `{meta.get('out_of_sample_out_sample_start')}` -> `{meta.get('out_of_sample_out_sample_end')}`"
                    )
                out_of_sample_review_rationale = list(meta.get("out_of_sample_review_rationale") or [])
                if out_of_sample_review_rationale:
                    st.caption("Out-of-sample rationale: " + ", ".join(f"`{item}`" for item in out_of_sample_review_rationale))

                if str(meta.get("rolling_review_status") or "").strip().lower() == "caution" or str(
                    meta.get("out_of_sample_review_status") or ""
                ).strip().lower() == "caution":
                    st.warning(
                        "최근 구간 또는 split-period review에서 caution이 잡혔습니다. "
                        "지금은 비중 확대보다 recent regime robustness review를 먼저 하는 편이 맞습니다."
                    )
                elif str(meta.get("rolling_review_status") or "").strip().lower() == "watch" or str(
                    meta.get("out_of_sample_review_status") or ""
                ).strip().lower() == "watch":
                    st.info(
                        "최근 구간 review는 완전히 깨지진 않았지만, current regime robustness를 조금 더 보수적으로 해석하는 편이 좋습니다."
                    )

        if (
            meta.get("benchmark_policy_status")
            or meta.get("liquidity_policy_status")
            or meta.get("validation_policy_status")
            or meta.get("guardrail_policy_status")
        ):
            with st.expander("세부 정책 기준 보기", expanded=False):
                st.caption(
                    "아래 항목은 승격 판단에 사용된 세부 정책 기준입니다. "
                    "평소에는 summary만 보고, 정책이 왜 `watch`나 `caution`인지 확인할 때만 펼쳐 보면 됩니다."
                )

                if meta.get("benchmark_policy_status"):
                    st.markdown("##### Benchmark Policy")
                    policy_cols = st.columns(5, gap="small")
                    policy_cols[0].metric("Policy Status", str(meta.get("benchmark_policy_status") or "normal").upper())
                    if meta.get("promotion_min_benchmark_coverage") is not None:
                        policy_cols[1].metric("Min Coverage", f"{float(meta.get('promotion_min_benchmark_coverage') or 0.0):.0%}")
                    if meta.get("benchmark_row_coverage") is not None:
                        policy_cols[2].metric("Actual Coverage", f"{float(meta.get('benchmark_row_coverage') or 0.0):.2%}")
                    if meta.get("promotion_min_net_cagr_spread") is not None:
                        policy_cols[3].metric("Min Net CAGR Spread", f"{float(meta.get('promotion_min_net_cagr_spread') or 0.0):.0%}")
                    if meta.get("net_cagr_spread") is not None:
                        policy_cols[4].metric("Actual Net CAGR Spread", f"{float(meta.get('net_cagr_spread') or 0.0):.2%}")
                    _render_value_list_caption("Benchmark policy signals", meta.get("benchmark_policy_watch_signals"))
                    policy_status = str(meta.get("benchmark_policy_status") or "normal").lower()
                    if policy_status == "caution":
                        st.warning("현재 benchmark policy 기준에서는 coverage 또는 상대 CAGR이 충분하지 않습니다. 승격 전 추가 검토가 필요한 상태입니다.")
                    elif policy_status == "watch":
                        st.info("Benchmark policy 기준에서 일부 watch 신호가 있습니다. 실전 승격 전 robustness 확인을 더 하는 편이 좋습니다.")

                if meta.get("liquidity_policy_status"):
                    st.markdown("##### Liquidity Policy")
                    liquidity_policy_cols = st.columns(4, gap="small")
                    liquidity_policy_cols[0].metric("Policy Status", str(meta.get("liquidity_policy_status") or "normal").upper())
                    if meta.get("promotion_min_liquidity_clean_coverage") is not None:
                        liquidity_policy_cols[1].metric("Min Clean Coverage", f"{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}")
                    if meta.get("liquidity_clean_coverage") is not None:
                        liquidity_policy_cols[2].metric("Actual Clean Coverage", f"{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}")
                    if meta.get("liquidity_excluded_active_rows") is not None:
                        liquidity_policy_cols[3].metric("Liquidity Excluded Rows", str(int(meta.get("liquidity_excluded_active_rows") or 0)))
                    _render_value_list_caption("Liquidity policy signals", meta.get("liquidity_policy_watch_signals"))
                    liquidity_policy_status = str(meta.get("liquidity_policy_status") or "normal").lower()
                    if liquidity_policy_status == "caution":
                        st.warning("현재 liquidity policy 기준에서는 유동성 제외가 너무 자주 발생했습니다. 실전 승격 전 후보군 또는 investability 계약을 다시 점검하는 편이 맞습니다.")
                    elif liquidity_policy_status == "watch":
                        st.info("Liquidity policy 기준에서 watch 신호가 있습니다. 유동성 제외 빈도와 후보군 구성을 한 번 더 검토하는 편이 좋습니다.")
                    elif liquidity_policy_status == "unavailable":
                        st.info("Liquidity policy는 현재 unavailable 상태입니다. 실전 승격 기준으로 보려면 `Min Avg Dollar Volume 20D` 필터를 함께 사용하는 편이 좋습니다.")

                if meta.get("validation_policy_status"):
                    st.markdown("##### Validation Policy")
                    validation_policy_cols = st.columns(5, gap="small")
                    validation_policy_cols[0].metric("Policy Status", str(meta.get("validation_policy_status") or "normal").upper())
                    if meta.get("promotion_max_underperformance_share") is not None:
                        validation_policy_cols[1].metric("Max Underperf Share", f"{float(meta.get('promotion_max_underperformance_share') or 0.0):.0%}")
                    if meta.get("rolling_underperformance_share") is not None:
                        validation_policy_cols[2].metric("Actual Underperf Share", f"{float(meta.get('rolling_underperformance_share') or 0.0):.2%}")
                    if meta.get("promotion_min_worst_rolling_excess_return") is not None:
                        validation_policy_cols[3].metric("Min Worst Excess", f"{float(meta.get('promotion_min_worst_rolling_excess_return') or 0.0):.0%}")
                    if meta.get("rolling_underperformance_worst_excess_return") is not None:
                        validation_policy_cols[4].metric("Actual Worst Excess", f"{float(meta.get('rolling_underperformance_worst_excess_return') or 0.0):.2%}")
                    _render_value_list_caption("Validation policy signals", meta.get("validation_policy_watch_signals"))
                    validation_policy_status = str(meta.get("validation_policy_status") or "normal").lower()
                    if validation_policy_status == "caution":
                        st.warning("현재 validation policy 기준에서는 rolling underperformance robustness가 충분하지 않습니다. 실전 승격 전 계약을 더 보수적으로 보는 편이 맞습니다.")
                    elif validation_policy_status == "watch":
                        st.info("Validation policy 기준에서 watch 신호가 있습니다. 추가 구간 robustness 검증을 더 하는 편이 좋습니다.")
                    elif validation_policy_status == "unavailable":
                        st.info("Validation policy는 현재 unavailable 상태입니다. aligned benchmark validation history가 있어야 승격 기준으로 해석할 수 있습니다.")

                if meta.get("guardrail_policy_status"):
                    st.markdown("##### Portfolio Guardrail Policy")
                    guardrail_policy_cols = st.columns(5, gap="small")
                    guardrail_policy_cols[0].metric("Policy Status", str(meta.get("guardrail_policy_status") or "normal").upper())
                    if meta.get("promotion_max_strategy_drawdown") is not None:
                        guardrail_policy_cols[1].metric("Max Strategy DD", f"{float(meta.get('promotion_max_strategy_drawdown') or 0.0):.0%}")
                    if meta.get("strategy_max_drawdown") is not None:
                        guardrail_policy_cols[2].metric("Actual Strategy DD", f"{float(meta.get('strategy_max_drawdown') or 0.0):.2%}")
                    if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
                        guardrail_policy_cols[3].metric("Max DD Gap", f"{float(meta.get('promotion_max_drawdown_gap_vs_benchmark') or 0.0):.0%}")
                    if meta.get("drawdown_gap_vs_benchmark") is not None:
                        guardrail_policy_cols[4].metric("Actual DD Gap", f"{float(meta.get('drawdown_gap_vs_benchmark') or 0.0):.2%}")
                    _render_value_list_caption("Guardrail policy signals", meta.get("guardrail_policy_watch_signals"))
                    guardrail_policy_status = str(meta.get("guardrail_policy_status") or "normal").lower()
                    if guardrail_policy_status == "caution":
                        st.warning("현재 portfolio guardrail policy 기준에서는 낙폭 방어가 충분하지 않습니다. 실전 승격 전 drawdown contract를 더 보수적으로 보는 편이 맞습니다.")
                    elif guardrail_policy_status == "watch":
                        st.info("Portfolio guardrail policy 기준에서 watch 신호가 있습니다. 최대 낙폭과 benchmark 대비 drawdown gap을 한 번 더 점검하는 편이 좋습니다.")
                    elif guardrail_policy_status == "unavailable":
                        st.info("Portfolio guardrail policy는 현재 unavailable 상태입니다. 실전 승격 기준으로 보려면 usable benchmark drawdown history가 필요합니다.")

        if benchmark_chart_df is not None and result_df is not None:
            with _section_header(
                "Strategy vs Benchmark Chart",
                "전략의 net 곡선과 benchmark reference curve를 겹쳐서 봅니다. 최근 구간에서 벌어지는 방향을 읽을 때 유용합니다.",
            ):
                strategy_line = (
                    bundle["chart_df"][["Date", "Total Balance"]]
                    .rename(columns={"Total Balance": bundle["strategy_name"]})
                    .set_index("Date")
                )
                benchmark_line = (
                    benchmark_chart_df[["Date", "Benchmark Total Balance"]]
                    .rename(
                        columns={
                            "Benchmark Total Balance": str(
                                meta.get("benchmark_label") or meta.get("benchmark_ticker") or "Benchmark"
                            )
                        }
                    )
                    .set_index("Date")
                )
                overlay_df = pd.concat([strategy_line, benchmark_line], axis=1).sort_index()
                _render_compare_altair_chart(
                    overlay_df,
                    title="Net Strategy vs Benchmark",
                    y_title="Total Balance",
                    show_end_markers=True,
                )
                st.caption("전략은 비용 반영 후 `net` 곡선이고, benchmark는 비용을 반영하지 않은 단순 reference curve입니다.")

    with execution_tab:
        st.caption(
            "이 섹션은 이 전략을 실제로 운용할 때 드는 부담을 봅니다. "
            "가격/유동성/turnover/비용/ETF 운용 가능성, 그리고 실제 방어 규칙이 여기에 모여 있습니다."
        )

        with _section_header(
            "실행 계약 요약",
            "가격, 이력, 유동성, turnover, 비용처럼 실제 운용 시 바로 영향을 주는 기본 조건을 보여줍니다.",
        ):
            top_cols = st.columns(6, gap="small")
            top_cols[0].metric("Minimum Price", f"{float(meta.get('min_price_filter') or 0.0):.2f}")
            top_cols[1].metric("Minimum History", f"{int(meta.get('min_history_months_filter') or 0)}M")
            top_cols[2].metric("Min Avg Dollar Volume 20D", f"{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M")
            top_cols[3].metric("Transaction Cost", f"{float(meta.get('transaction_cost_bps') or 0.0):.1f} bps")
            top_cols[4].metric("Avg Turnover", f"{float(meta.get('avg_turnover') or 0.0):.2%}")
            top_cols[5].metric("Estimated Cost Total", f"{float(meta.get('estimated_cost_total') or 0.0):,.1f}")
            if meta.get("liquidity_excluded_total") is not None:
                st.caption(
                    "Liquidity excluded candidates: "
                    f"`{int(meta.get('liquidity_excluded_total') or 0)}` total, "
                    f"`{int(meta.get('liquidity_excluded_active_rows') or 0)}` rows."
                )
            if meta.get("liquidity_clean_coverage") is not None:
                st.caption("Liquidity clean coverage on rebalance rows: " f"`{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}`")

        if meta.get("liquidity_policy_status") or meta.get("promotion_min_liquidity_clean_coverage") is not None:
            with _section_header(
                "Liquidity Policy",
                "유동성 때문에 실제 운용 해석이 가능한지 보는 섹션입니다. "
                "특히 `unavailable`이면 현재 설정만으로는 유동성 검증을 아예 하지 못하고 있다는 뜻입니다.",
            ):
                liquidity_policy_status = str(meta.get("liquidity_policy_status") or "unavailable").lower()
                liquidity_policy_cols = st.columns(5, gap="small")
                liquidity_policy_cols[0].metric("Policy Status", liquidity_policy_status.upper())
                liquidity_policy_cols[1].metric(
                    "Min Avg Dollar Volume 20D",
                    f"{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M",
                )
                liquidity_policy_cols[2].metric(
                    "Min Clean Coverage",
                    f"{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}",
                )
                liquidity_policy_cols[3].metric(
                    "Actual Clean Coverage",
                    (
                        f"{float(meta.get('liquidity_clean_coverage')):.2%}"
                        if meta.get("liquidity_clean_coverage") is not None
                        else "-"
                    ),
                )
                liquidity_policy_cols[4].metric(
                    "Liquidity Excluded Rows",
                    str(int(meta.get("liquidity_excluded_active_rows") or 0)),
                )

                st.caption(
                    "`Min Avg Dollar Volume 20D`는 최근 20거래일 평균 거래대금 기준이고, "
                    "`Liquidity Clean Coverage`는 리밸런싱 시점 중 유동성 제외 없이 지나간 비율입니다."
                )

                liquidity_policy_signals = [
                    _liquidity_policy_signal_to_korean_label(item)
                    for item in list(meta.get("liquidity_policy_watch_signals") or [])
                ]
                _render_value_list_caption("Liquidity policy signals", liquidity_policy_signals)

                min_avg_dollar_volume = float(meta.get("min_avg_dollar_volume_20d_m_filter") or 0.0)
                clean_coverage = meta.get("liquidity_clean_coverage")

                if liquidity_policy_status == "normal":
                    st.success(
                        "현재 유동성 정책 기준에서는 특별한 blocker가 없습니다. "
                        "실전 해석에서 유동성 쪽은 비교적 안정적으로 통과한 상태입니다."
                    )
                elif liquidity_policy_status == "watch":
                    st.info(
                        "현재 유동성 정책은 watch 상태입니다. "
                        "당장 막히는 수준은 아니지만, 유동성 제외 빈도가 기준에 가까워서 후보군을 조금 더 점검하는 편이 좋습니다."
                    )
                elif liquidity_policy_status == "caution":
                    st.warning(
                        "현재 유동성 정책은 caution 상태입니다. "
                        "리밸런싱 시점에서 유동성 제외가 너무 자주 발생해 실전 승격을 바로 열기 어렵습니다."
                    )
                    st.info(
                        "먼저 `Min Avg Dollar Volume 20D` 기준을 확인하고, 거래가 얇은 종목이 자주 걸리는지 후보군을 다시 점검해보세요."
                    )
                elif liquidity_policy_status == "unavailable":
                    if min_avg_dollar_volume <= 0.0:
                        st.warning(
                            "현재는 `Min Avg Dollar Volume 20D`가 `0.0M`이라 유동성 정책을 실제로 판정하지 못했습니다."
                        )
                        st.info(
                            "해결 방법: `Advanced Inputs`에서 `Min Avg Dollar Volume 20D`를 `0`보다 큰 값으로 설정한 뒤 다시 실행하세요. "
                            "즉 지금은 유동성 필터를 꺼둔 상태라, 승격 판단용 liquidity review가 비활성화된 것입니다."
                        )
                    elif clean_coverage is None:
                        st.warning(
                            "유동성 필터 값은 있지만, `Liquidity Clean Coverage`가 계산되지 않아 정책 판단을 못 하고 있습니다."
                        )
                        st.info(
                            "해결 방법: 결과 데이터에 유동성 제외/coverage가 실제로 계산됐는지 확인하고, 필요하면 기간이나 universe contract를 다시 점검하세요."
                        )
                    else:
                        st.info(
                            "현재 설정만으로는 유동성 정책을 충분히 해석하기 어렵습니다. "
                            "유동성 필터 값과 clean coverage 계산 여부를 함께 확인하는 편이 좋습니다."
                        )

        if (
            meta.get("promotion_min_etf_aum_b") is not None
            or meta.get("promotion_max_bid_ask_spread_pct") is not None
            or meta.get("etf_operability_status")
        ):
            with _section_header(
                "ETF 운용 가능성",
                "ETF 전략에서만 보이는 항목입니다. 현재 시점 기준으로 ETF 규모와 bid-ask spread가 너무 불안정하지 않은지 확인합니다.",
            ):
                etf_cols = st.columns(5, gap="small")
                etf_cols[0].metric("Policy Status", str(meta.get("etf_operability_status") or "unavailable").upper())
                if meta.get("promotion_min_etf_aum_b") is not None:
                    etf_cols[1].metric("Min ETF AUM", f"${float(meta.get('promotion_min_etf_aum_b') or 0.0):.1f}B")
                if meta.get("promotion_max_bid_ask_spread_pct") is not None:
                    etf_cols[2].metric("Max Bid-Ask Spread", f"{float(meta.get('promotion_max_bid_ask_spread_pct') or 0.0):.2%}")
                if meta.get("etf_operability_clean_coverage") is not None:
                    etf_cols[3].metric("Clean Coverage", f"{float(meta.get('etf_operability_clean_coverage') or 0.0):.2%}")
                if meta.get("etf_operability_clean_pass_count") is not None:
                    etf_cols[4].metric("Clean Pass", f"{int(meta.get('etf_operability_clean_pass_count') or 0)} / {int(meta.get('etf_symbol_count') or 0)}")
                if meta.get("etf_operability_data_coverage") is not None:
                    st.caption(f"ETF operability data coverage: `{float(meta.get('etf_operability_data_coverage') or 0.0):.2%}`")
                if meta.get("etf_aum_pass_count") is not None or meta.get("etf_spread_pass_count") is not None:
                    st.caption(
                        "Pass counts: "
                        f"AUM `{int(meta.get('etf_aum_pass_count') or 0)}` / `{int(meta.get('etf_symbol_count') or 0)}`, "
                        f"Spread `{int(meta.get('etf_spread_pass_count') or 0)}` / `{int(meta.get('etf_symbol_count') or 0)}`"
                    )
                with st.expander("문제 ETF / 누락 데이터 보기", expanded=False):
                    _render_value_list_caption("AUM-below-policy ETF", meta.get("etf_aum_failed_symbols"))
                    _render_value_list_caption("Spread-above-policy ETF", meta.get("etf_spread_failed_symbols"))
                    _render_value_list_caption("Missing ETF operability fields", meta.get("etf_operability_missing_data_symbols"))
                    _render_value_list_caption("ETF operability signals", meta.get("etf_operability_watch_signals"))
                etf_status = str(meta.get("etf_operability_status") or "unavailable").lower()
                if etf_status == "caution":
                    st.warning("현재 ETF operability policy 기준에서는 자산 규모나 bid-ask spread가 충분히 안정적이지 않습니다. 실전 승격 전 ETF universe를 다시 점검하는 편이 맞습니다.")
                elif etf_status == "watch":
                    st.info("ETF operability policy 기준에서 일부 watch 신호가 있습니다. 현재 AUM과 bid-ask spread를 한 번 더 점검하는 편이 좋습니다.")
                elif etf_status == "unavailable":
                    st.info("ETF operability policy는 현재 unavailable 상태입니다. ETF asset profile을 새로 수집한 뒤 다시 해석하는 편이 맞습니다.")

        if _should_show_guardrail_surface(meta):
            with _section_header(
                "실제 방어 규칙",
                "경고만 보여주는 것이 아니라, 조건이 깨지면 실제 rebalance를 더 보수적으로 만들 수 있는 규칙입니다.",
            ):
                under_enabled = bool(meta.get("underperformance_guardrail_enabled"))
                draw_enabled = bool(meta.get("drawdown_guardrail_enabled"))

                guardrail_cols = st.columns(5, gap="small")
                guardrail_cols[0].metric("Underperformance Guardrail", "ON" if under_enabled else "OFF")
                guardrail_cols[1].metric(
                    "Underperf Window",
                    f"{int(meta.get('underperformance_guardrail_window_months') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M",
                )
                guardrail_cols[2].metric(
                    "Underperf Threshold",
                    f"{float(meta.get('underperformance_guardrail_threshold') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD):.0%}",
                )
                guardrail_cols[3].metric(
                    "Underperf Trigger Count",
                    str(int(meta.get("underperformance_guardrail_trigger_count") or 0)),
                )
                guardrail_cols[4].metric(
                    "Underperf Trigger Share",
                    f"{float(meta.get('underperformance_guardrail_trigger_share') or 0.0):.2%}",
                )

                drawdown_guardrail_cols = st.columns(5, gap="small")
                drawdown_guardrail_cols[0].metric("Drawdown Guardrail", "ON" if draw_enabled else "OFF")
                drawdown_guardrail_cols[1].metric(
                    "Drawdown Window",
                    f"{int(meta.get('drawdown_guardrail_window_months') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M",
                )
                drawdown_guardrail_cols[2].metric(
                    "Strategy DD Threshold",
                    f"{float(meta.get('drawdown_guardrail_strategy_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD):.0%}",
                )
                drawdown_guardrail_cols[3].metric(
                    "DD Gap Threshold",
                    f"{float(meta.get('drawdown_guardrail_gap_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD):.0%}",
                )
                drawdown_guardrail_cols[4].metric(
                    "Drawdown Trigger Count",
                    str(int(meta.get("drawdown_guardrail_trigger_count") or 0)),
                )
                st.caption(
                    "Drawdown trigger share: "
                    f"`{float(meta.get('drawdown_guardrail_trigger_share') or 0.0):.2%}`"
                )

                if not under_enabled and not draw_enabled:
                    st.info(
                        "현재 run에서는 두 guardrail이 꺼져 있습니다. "
                        "그래도 여기서 기본 계약과 trigger 수를 확인할 수 있게 계속 노출합니다."
                    )

    with detail_tab:
        st.caption(
            "이 섹션은 원자료 확인용입니다. "
            "요약 판단은 앞의 세 탭에서 끝내고, 여기서는 세부 숫자나 표를 다시 확인할 때만 보시면 됩니다."
        )

        detail_cols: list[str] = []
        if result_df is not None and "Estimated Cost" in result_df.columns:
            with _section_header(
                "Cost Detail Preview",
                "비용이 실제로 어떻게 누적됐는지 확인하는 원자료 미리보기입니다.",
            ):
                detail_cols.append("Date")
                detail_cols.extend(
                    [
                        column
                        for column in [
                            "Gross Total Balance",
                            "Total Balance",
                            "Turnover",
                            "Estimated Cost",
                            "Cumulative Estimated Cost",
                        ]
                        if column in result_df.columns
                    ]
                )
                st.dataframe(result_df[detail_cols].head(12), use_container_width=True, hide_index=True)

        if benchmark_summary_df is not None:
            with _section_header(
                "Benchmark Summary",
                "benchmark와의 비교 결과를 표 형태로 다시 확인하는 상세 데이터입니다.",
            ):
                st.dataframe(benchmark_summary_df, use_container_width=True, hide_index=True)

def _build_snapshot_selection_history(result_df: pd.DataFrame) -> pd.DataFrame:
    if result_df.empty or "Selected Count" not in result_df.columns:
        return pd.DataFrame()

    selection_df = result_df.copy()

    def _first_series(frame: pd.DataFrame, column: str) -> pd.Series | None:
        if column not in frame.columns:
            return None
        value = frame[column]
        if isinstance(value, pd.DataFrame):
            return value.iloc[:, 0]
        return value

    if selection_df.columns.duplicated().any():
        selection_df = selection_df.loc[:, ~selection_df.columns.duplicated()].copy()

    selection_df["Date"] = pd.to_datetime(selection_df["Date"], errors="coerce")
    selection_df = selection_df.dropna(subset=["Date"])

    if "Rebalancing" in selection_df.columns:
        selection_df = selection_df[selection_df["Rebalancing"].fillna(False)]

    selected_count_series = _first_series(selection_df, "Selected Count")
    raw_selected_count_series = _first_series(selection_df, "Raw Selected Count")
    selected_count = selected_count_series.fillna(0) if selected_count_series is not None else 0
    raw_selected_count = raw_selected_count_series.fillna(0) if raw_selected_count_series is not None else 0
    selection_df = selection_df[(selected_count > 0) | (raw_selected_count > 0)].copy()
    if selection_df.empty:
        return pd.DataFrame()

    selection_df["Rejected Slot Handling"] = selection_df.apply(
        lambda row: _strict_rejection_handling_label_from_flags(
            rejected_slot_fill_enabled=bool(row.get("Rejected Slot Fill Enabled") or False),
            partial_cash_retention_enabled=bool(row.get("Partial Cash Retention Enabled") or False),
        ),
        axis=1,
    )
    selection_df["Weighting Contract"] = selection_df["Weighting Mode"].apply(_strict_weighting_mode_value_to_label)
    selection_df["Risk-Off Contract"] = selection_df["Risk-Off Mode"].apply(_strict_risk_off_mode_value_to_label)
    selection_df["Risk-Off Reasons"] = selection_df["Risk-Off Reason"].apply(
        lambda value: _stringify_label_list(value, label_fn=_strict_risk_off_reason_to_label)
    )

    keep_columns = [
        "Date",
        "Raw Selected Ticker",
        "Raw Selected Count",
        "Raw Selected Score",
        "Overlay Rejected Ticker",
        "Overlay Rejected Count",
        "Rejected Slot Handling",
        "Rejected Slot Fill Enabled",
        "Rejected Slot Fill Active",
        "Rejected Slot Fill Ticker",
        "Rejected Slot Fill Count",
        "Partial Cash Retention Enabled",
        "Partial Cash Retention Active",
        "Risk-Off Contract",
        "Risk-Off Mode",
        "Risk-Off Reason",
        "Risk-Off Reasons",
        "Defensive Sleeve Ticker",
        "Defensive Sleeve Count",
        "Regime Blocked Ticker",
        "Regime Blocked Count",
        "Next Ticker",
        "Selected Count",
        "Selected Score",
        "Trend Filter Enabled",
        "Trend Filter Column",
        "Weighting Contract",
        "Weighting Mode",
        "Market Regime Enabled",
        "Market Regime Benchmark",
        "Market Regime Column",
        "Market Regime State",
        "Cash",
        "Total Balance",
        "Total Return",
    ]
    existing = [column for column in keep_columns if column in selection_df.columns]
    selection_df = selection_df[existing].copy()
    rename_map = {
        "Next Ticker": "Selected Tickers",
        "Selected Score": "Selection Score",
        "Raw Selected Ticker": "Raw Selected Tickers",
        "Raw Selected Score": "Raw Selection Score",
        "Overlay Rejected Ticker": "Overlay Rejected Tickers",
        "Rejected Slot Fill Ticker": "Filled Tickers",
        "Rejected Slot Fill Count": "Filled Count",
        "Defensive Sleeve Ticker": "Defensive Sleeve Tickers",
        "Regime Blocked Ticker": "Regime Blocked Tickers",
    }
    selection_df = selection_df.rename(columns=rename_map).reset_index(drop=True)

    list_columns = [
        "Raw Selected Tickers",
        "Overlay Rejected Tickers",
        "Filled Tickers",
        "Defensive Sleeve Tickers",
        "Regime Blocked Tickers",
        "Selected Tickers",
    ]
    score_list_columns = [
        "Raw Selection Score",
        "Selection Score",
    ]
    for column in list_columns:
        if column in selection_df.columns:
            selection_df[column] = selection_df[column].apply(_stringify_symbol_list)
    for column in score_list_columns:
        if column in selection_df.columns:
            selection_df[column] = selection_df[column].apply(_stringify_score_list)

    cash_series = _first_series(selection_df, "Cash")
    total_balance_series = _first_series(selection_df, "Total Balance")
    if cash_series is not None and total_balance_series is not None:
        total_balance = pd.to_numeric(total_balance_series, errors="coerce")
        cash_balance = pd.to_numeric(cash_series, errors="coerce").fillna(0.0)
        selection_df["Cash Share Ratio"] = np.where(
            total_balance > 0,
            cash_balance / total_balance,
            np.nan,
        )
    else:
        selection_df["Cash Share Ratio"] = np.nan

    def _build_interpretation(row: pd.Series) -> str:
        raw_count = int(row.get("Raw Selected Count") or 0)
        rejected_count = int(row.get("Overlay Rejected Count") or 0)
        regime_blocked_count = int(row.get("Regime Blocked Count") or 0)
        selected_count = int(row.get("Selected Count") or 0)
        regime_state = str(row.get("Market Regime State") or "").strip().lower()
        regime_benchmark = str(row.get("Market Regime Benchmark") or "").strip() or "benchmark"
        risk_off_contract = str(row.get("Risk-Off Contract") or "Cash Only").strip()
        risk_off_reasons = str(row.get("Risk-Off Reasons") or "").strip()
        weighting_contract = str(row.get("Weighting Contract") or "Equal Weight").strip()
        defensive_sleeve_count = int(row.get("Defensive Sleeve Count") or 0)
        defensive_sleeve_tickers = str(row.get("Defensive Sleeve Tickers") or "").strip()
        cash_share = row.get("Cash Share Ratio")
        cash_share_text = (
            f"{float(cash_share) * 100:.1f}%"
            if pd.notna(cash_share)
            else "n/a"
        )

        if raw_count <= 0:
            return "No usable ranked candidates were available at this rebalance, so the portfolio stayed in cash."
        if regime_blocked_count > 0 and regime_state == "risk_off":
            if risk_off_contract == "Defensive Sleeve Preference" and defensive_sleeve_count > 0:
                return (
                    f"Market regime overlay moved the portfolio into defensive sleeve `{defensive_sleeve_tickers}` "
                    f"because `{regime_benchmark}` was in risk-off state at this rebalance. "
                    f"It blocked {regime_blocked_count} post-filter candidate(s)."
                )
            return (
                f"Market regime overlay moved the portfolio fully to cash because `{regime_benchmark}` "
                f"was in risk-off state at this rebalance. It blocked {regime_blocked_count} post-filter candidate(s)."
            )
        if selected_count <= 0 and risk_off_reasons:
            destination_text = (
                f"rotated into defensive sleeve `{defensive_sleeve_tickers}`"
                if risk_off_contract == "Defensive Sleeve Preference" and defensive_sleeve_count > 0
                else "moved fully to cash"
            )
            return (
                f"Portfolio-wide risk-off rule (`{risk_off_contract}`) {destination_text} because "
                f"`{risk_off_reasons}` triggered after candidate selection."
            )
        if selected_count <= 0 and rejected_count > 0:
            handling_label = str(row.get("Rejected Slot Handling") or "current rejection handling")
            return (
                f"Trend overlay rejected all {raw_count} raw candidates under `{handling_label}`, "
                "so the portfolio moved fully to cash."
            )
        if rejected_count > 0:
            handling_label = str(row.get("Rejected Slot Handling") or "current rejection handling")
            fill_count = int(row.get("Rejected Slot Fill Count") or 0)
            fill_active = bool(row.get("Rejected Slot Fill Active") or False)
            partial_cash_retention_active = bool(row.get("Partial Cash Retention Active") or False)
            if fill_active and fill_count > 0:
                unfilled_count = max(rejected_count - fill_count, 0)
                fill_text = (
                    f"`{handling_label}` refilled {fill_count} rejected slot(s) with next-ranked eligible names"
                    + (
                        f" and left {unfilled_count} slot(s) in cash. Cash share after rebalance: {cash_share_text}."
                        if partial_cash_retention_active and unfilled_count > 0
                        else f". Cash share after rebalance: {cash_share_text}."
                    )
                )
                if not partial_cash_retention_active and selected_count < raw_count:
                    fill_text = (
                        f"`{handling_label}` refilled {fill_count} rejected slot(s), then reweighted the final survivors after "
                        f"{rejected_count} original rejection(s). Cash share after rebalance: {cash_share_text}."
                    )
                return (
                    f"Trend overlay kept {selected_count} of {raw_count} raw candidates and {fill_text} "
                    f"Final weighting contract: `{weighting_contract}`."
                )
            return (
                f"Trend overlay kept {selected_count} of {raw_count} raw candidates and "
                + (
                    f"`{handling_label}` left {rejected_count} rejected slot(s) in cash. Cash share after rebalance: {cash_share_text}. Final weighting contract: `{weighting_contract}`."
                    if partial_cash_retention_active
                    else f"`{handling_label}` reweighted the survivors after rejecting {rejected_count} name(s). Cash share after rebalance: {cash_share_text}. Final weighting contract: `{weighting_contract}`."
                )
            )
        if pd.notna(cash_share) and float(cash_share) > 0:
            return (
                f"All final candidates passed the current filters, but the portfolio still kept "
                f"{cash_share_text} in cash because fewer names were investable than the nominal top-N. "
                f"Final weighting contract: `{weighting_contract}`."
            )
        return (
            "All selected candidates passed the current rules and the portfolio remained fully invested. "
            f"Final weighting contract: `{weighting_contract}`."
        )

    selection_df["Interpretation"] = selection_df.apply(_build_interpretation, axis=1)
    if "Cash Share Ratio" in selection_df.columns:
        selection_df["Cash Share"] = selection_df["Cash Share Ratio"].apply(
            lambda value: f"{float(value) * 100:.1f}%" if pd.notna(value) else ""
        )

    return selection_df

def _build_overlay_rejection_frequency_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Overlay Rejected Tickers" not in selection_df.columns:
        return pd.DataFrame()

    exploded_rows: list[dict[str, Any]] = []
    for _, row in selection_df.iterrows():
        row_date = pd.to_datetime(row.get("Date"), errors="coerce")
        rejected_tickers = _normalize_symbol_sequence(row.get("Overlay Rejected Tickers"))
        for symbol in rejected_tickers:
            exploded_rows.append({"symbol": symbol, "Date": row_date})

    if not exploded_rows:
        return pd.DataFrame()

    exploded_df = pd.DataFrame(exploded_rows)
    rejection_df = (
        exploded_df.groupby("symbol", as_index=False)
        .agg(
            RejectedEvents=("Date", "size"),
            FirstRejected=("Date", "min"),
            LastRejected=("Date", "max"),
        )
        .sort_values(["RejectedEvents", "symbol"], ascending=[False, True])
        .reset_index(drop=True)
    )
    rejection_df["FirstRejected"] = pd.to_datetime(rejection_df["FirstRejected"]).dt.strftime("%Y-%m-%d")
    rejection_df["LastRejected"] = pd.to_datetime(rejection_df["LastRejected"]).dt.strftime("%Y-%m-%d")
    return rejection_df

def _build_market_regime_event_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Market Regime State" not in selection_df.columns:
        return pd.DataFrame()

    regime_df = selection_df.copy()
    regime_df = regime_df[regime_df["Market Regime State"].astype(str).str.lower() == "risk_off"].copy()
    if regime_df.empty:
        return pd.DataFrame()

    keep = [
        "Date",
        "Market Regime Benchmark",
        "Market Regime Column",
        "Raw Selected Count",
        "Regime Blocked Count",
        "Regime Blocked Tickers",
        "Cash Share",
    ]
    keep = [column for column in keep if column in regime_df.columns]
    event_df = regime_df[keep].copy()
    event_df["Date"] = pd.to_datetime(event_df["Date"]).dt.strftime("%Y-%m-%d")
    return event_df.reset_index(drop=True)

def _build_selection_interpretation_summary(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty:
        return pd.DataFrame()

    def _series_or_default(column: str, *, default: Any, dtype: str | None = None) -> pd.Series:
        if column in selection_df.columns:
            value = selection_df[column]
            if isinstance(value, pd.DataFrame):
                value = value.iloc[:, 0]
            return value
        return pd.Series([default] * len(selection_df), index=selection_df.index, dtype=dtype)

    raw_candidate_events = int(pd.to_numeric(_series_or_default("Raw Selected Count", default=0), errors="coerce").fillna(0).sum())
    final_selected_events = int(pd.to_numeric(_series_or_default("Selected Count", default=0), errors="coerce").fillna(0).sum())
    overlay_rejections = int(pd.to_numeric(_series_or_default("Overlay Rejected Count", default=0), errors="coerce").fillna(0).sum())
    filled_events = int(
        (
            pd.to_numeric(_series_or_default("Filled Count", default=0), errors="coerce")
            .fillna(0)
            .gt(0)
        ).sum()
    )
    cash_retained_events = int(
        (
            _series_or_default("Partial Cash Retention Active", default=False, dtype=bool)
            .fillna(False)
            .astype(bool)
        ).sum()
    )
    regime_rejections = int(pd.to_numeric(_series_or_default("Regime Blocked Count", default=0), errors="coerce").fillna(0).sum())
    regime_cash_rebalances = int(
        (
            _series_or_default("Market Regime State", default="", dtype=object)
            .astype(str)
            .str.lower()
            .eq("risk_off")
        ).sum()
    )
    cash_only_rebalances = int(
        (pd.to_numeric(_series_or_default("Selected Count", default=0), errors="coerce").fillna(0) <= 0).sum()
    )
    avg_selected_count = float(
        pd.to_numeric(_series_or_default("Selected Count", default=0), errors="coerce").fillna(0).mean()
    )
    cash_share_series = pd.to_numeric(_series_or_default("Cash Share Ratio", default=np.nan), errors="coerce")
    avg_cash_share = float(cash_share_series.fillna(0).mean())
    weighting_values = [
        str(value).strip()
        for value in _series_or_default("Weighting Contract", default="", dtype=object).tolist()
        if str(value).strip()
    ]
    unique_weighting = sorted(dict.fromkeys(weighting_values))
    weighting_summary = ", ".join(unique_weighting) if unique_weighting else "n/a"
    risk_off_values = [
        str(value).strip()
        for value in _series_or_default("Risk-Off Contract", default="", dtype=object).tolist()
        if str(value).strip()
    ]
    unique_risk_off = sorted(dict.fromkeys(risk_off_values))
    risk_off_summary = ", ".join(unique_risk_off) if unique_risk_off else "n/a"
    defensive_sleeve_activations = int(
        (
            pd.to_numeric(_series_or_default("Defensive Sleeve Count", default=0), errors="coerce")
            .fillna(0)
            .gt(0)
        ).sum()
    )
    handling_values = [
        str(value).strip()
        for value in _series_or_default("Rejected Slot Handling", default="", dtype=object).tolist()
        if str(value).strip()
    ]
    unique_handling = sorted(dict.fromkeys(handling_values))
    handling_summary = ", ".join(unique_handling) if unique_handling else "n/a"

    return pd.DataFrame(
        [
            {
                "Raw Candidate Events": raw_candidate_events,
                "Final Selected Events": final_selected_events,
                "Overlay Rejections": overlay_rejections,
                "Rejected Slot Handling": handling_summary,
                "Weighting Contract": weighting_summary,
                "Risk-Off Contract": risk_off_summary,
                "Filled Events": filled_events,
                "Cash-Retained Events": cash_retained_events,
                "Defensive Sleeve Activations": defensive_sleeve_activations,
                "Regime Blocked Events": regime_rejections,
                "Regime Cash Rebalances": regime_cash_rebalances,
                "Cash-Only Rebalances": cash_only_rebalances,
                "Avg Selected Count": round(avg_selected_count, 2),
                "Avg Cash Share": f"{avg_cash_share * 100:.1f}%",
            }
        ]
    )

def _normalize_symbol_sequence(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(symbol).strip() for symbol in value if str(symbol).strip()]

    raw = str(value).strip()
    if not raw:
        return []

    raw = raw.strip("[]")
    cleaned = [part.strip().strip("'").strip('"') for part in raw.split(",")]
    return [symbol for symbol in cleaned if symbol]

def _stringify_symbol_list(value: Any) -> str:
    symbols = _normalize_symbol_sequence(value)
    return ", ".join(symbols)

def _stringify_score_list(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(f"{float(item):.3f}" for item in value)
    return str(value)

def _build_selection_frequency_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Selected Tickers" not in selection_df.columns:
        return pd.DataFrame()

    exploded_rows: list[dict[str, Any]] = []
    for _, row in selection_df.iterrows():
        row_date = pd.to_datetime(row.get("Date"), errors="coerce")
        selected_tickers = _normalize_symbol_sequence(row.get("Selected Tickers"))
        for symbol in selected_tickers:
            exploded_rows.append({"symbol": symbol, "Date": row_date})

    if not exploded_rows:
        return pd.DataFrame()

    exploded_df = pd.DataFrame(exploded_rows)
    frequency_df = (
        exploded_df.groupby("symbol", as_index=False)
        .agg(
            SelectedEvents=("Date", "size"),
            FirstSelected=("Date", "min"),
            LastSelected=("Date", "max"),
        )
        .sort_values(["SelectedEvents", "symbol"], ascending=[False, True])
        .reset_index(drop=True)
    )
    frequency_df["FirstSelected"] = pd.to_datetime(frequency_df["FirstSelected"]).dt.strftime("%Y-%m-%d")
    frequency_df["LastSelected"] = pd.to_datetime(frequency_df["LastSelected"]).dt.strftime("%Y-%m-%d")
    return frequency_df

def _render_snapshot_selection_history(
    result_df: pd.DataFrame,
    *,
    strategy_name: str,
    factor_names: list[str],
    snapshot_mode: str | None,
    snapshot_source: str | None,
) -> None:
    try:
        selection_df = _build_snapshot_selection_history(result_df)
    except Exception as exc:  # pragma: no cover - UI fallback path
        st.warning(
            "Selection history could not be rendered for this run payload. "
            "Try rerunning the backtest to rebuild the latest result bundle."
        )
        st.caption(f"Renderer detail: {type(exc).__name__}: {exc}")
        return

    if selection_df.empty:
        st.info("No active selection history is available for this run.")
        return

    first_active = pd.to_datetime(selection_df.iloc[0]["Date"]).strftime("%Y-%m-%d")
    event_count = len(selection_df)
    distinct_names = sorted(
        {
            symbol.strip()
            for value in selection_df["Selected Tickers"].dropna()
            for symbol in _normalize_symbol_sequence(value)
            if symbol.strip()
        }
    )
    overlay_active = (
        "Trend Filter Enabled" in selection_df.columns
        and selection_df["Trend Filter Enabled"].fillna(False).astype(bool).any()
    )
    regime_active = (
        "Market Regime Enabled" in selection_df.columns
        and selection_df["Market Regime Enabled"].fillna(False).astype(bool).any()
    )

    st.caption(
        "이 화면은 strict annual 전략 검증에서 가장 실무적인 질문인 "
        "‘각 리밸런싱 날짜에 실제로 어떤 종목이 선택되었는가?’를 읽기 쉽게 보여주기 위한 뷰입니다."
    )
    left, center, right = st.columns(3, gap="large")
    with left:
        st.metric("First Active Date", first_active)
    with center:
        st.metric("Active Rebalances", f"{event_count}")
    with right:
        st.metric("Distinct Selected Names", f"{len(distinct_names)}")

    meta_df = pd.DataFrame(
        [
            {
                "Strategy": strategy_name,
                "Snapshot Mode": snapshot_mode,
                "Snapshot Source": snapshot_source or "n/a",
                "Factors": ", ".join(factor_names) if factor_names else "n/a",
                "Trend Overlay": (
                    selection_df.loc[selection_df["Trend Filter Enabled"].fillna(False), "Trend Filter Column"].iloc[0]
                    if overlay_active and "Trend Filter Column" in selection_df.columns
                    else "off"
                ),
                "Rejected Slot Handling": (
                    ", ".join(
                        sorted(
                            dict.fromkeys(
                                str(value).strip()
                                for value in selection_df.get("Rejected Slot Handling", pd.Series(dtype=object)).tolist()
                                if str(value).strip()
                            )
                        )
                    )
                    or "n/a"
                ),
                "Weighting Contract": (
                    ", ".join(
                        sorted(
                            dict.fromkeys(
                                str(value).strip()
                                for value in selection_df.get("Weighting Contract", pd.Series(dtype=object)).tolist()
                                if str(value).strip()
                            )
                        )
                    )
                    or "n/a"
                ),
                "Risk-Off Contract": (
                    ", ".join(
                        sorted(
                            dict.fromkeys(
                                str(value).strip()
                                for value in selection_df.get("Risk-Off Contract", pd.Series(dtype=object)).tolist()
                                if str(value).strip()
                            )
                        )
                    )
                    or "n/a"
                ),
                "Market Regime Overlay": (
                    (
                        f"{selection_df.loc[selection_df['Market Regime Enabled'].fillna(False), 'Market Regime Benchmark'].iloc[0]} / "
                        f"{selection_df.loc[selection_df['Market Regime Enabled'].fillna(False), 'Market Regime Column'].iloc[0]}"
                    )
                    if regime_active
                    else "off"
                ),
            }
        ]
    )
    st.dataframe(meta_df, use_container_width=True, hide_index=True)
    if overlay_active:
        st.caption(
            "Raw Selected는 팩터 랭킹으로 뽑힌 1차 후보이고, Final Selected는 오버레이까지 반영한 실제 보유 후보입니다. Overlay Rejected는 월말 추세 필터를 통과하지 못한 원래 후보이고, Filled Tickers가 있으면 그 자리를 다음 순위의 추세 통과 종목으로 보충했다는 뜻입니다."
        )
    if regime_active:
        st.caption(
            "Market Regime은 개별 종목 필터가 아니라 시장 전체 상태를 보는 상위 오버레이입니다. risk-off로 판정된 리밸런싱에서는 strict factor 후보가 있어도 포트폴리오 전체가 현금으로 이동할 수 있습니다."
        )

    history_tab, interpretation_tab, frequency_tab = st.tabs(["Selection History Table", "Interpretation Summary", "Selection Frequency"])
    with history_tab:
        st.caption(
            "이 표는 각 리밸런싱 날짜별 실제 선택 결과입니다. "
            "`Rejected Slot Handling`, `Weighting Contract`, `Risk-Off Contract`와 함께 "
            "`Interpretation` 열을 보면 그 날짜에 무슨 일이 있었는지 한 줄로 읽을 수 있습니다."
        )
        cash_title_col, cash_help_col = st.columns([0.92, 0.08], gap="small")
        with cash_title_col:
            st.caption("`Cash Share`는 각 리밸런싱 직후 포트폴리오에서 현금으로 남아 있는 비중입니다.")
        with cash_help_col:
            _render_cash_share_help_popover()
        st.dataframe(
            selection_df.drop(
                columns=[
                    "Cash Share Ratio",
                    "Rejected Slot Fill Enabled",
                    "Rejected Slot Fill Active",
                    "Partial Cash Retention Enabled",
                    "Partial Cash Retention Active",
                    "Weighting Mode",
                    "Risk-Off Mode",
                    "Risk-Off Reason",
                ],
                errors="ignore",
            ),
            use_container_width=True,
            hide_index=True,
        )
    with interpretation_tab:
        interpretation_summary_df = _build_selection_interpretation_summary(selection_df)
        if not interpretation_summary_df.empty:
            summary_title_col, summary_help_col = st.columns([0.92, 0.08], gap="small")
            with summary_title_col:
                st.markdown("##### Interpretation Summary")
            with summary_help_col:
                _render_interpretation_summary_help_popover()
            st.caption(
                "이 표는 행별 문장이 아니라 실행 전체 요약입니다. "
                "`Rejected Slot Handling`, `Weighting Contract`, `Risk-Off Contract`, "
                "`Filled Events`, `Cash-Retained Events`, `Defensive Sleeve Activations`를 먼저 보면 됩니다."
            )
            st.caption("참고: 이 표의 Raw / Final 값은 전체 모집군 크기가 아니라 리밸런싱별 선택 이벤트의 누적 합계입니다.")
            st.dataframe(interpretation_summary_df, use_container_width=True, hide_index=True)
        rejection_df = _build_overlay_rejection_frequency_view(selection_df)
        if not rejection_df.empty:
            reject_title_col, reject_help_col = st.columns([0.92, 0.08], gap="small")
            with reject_title_col:
                st.markdown("##### Overlay Rejection Frequency")
            with reject_help_col:
                _render_overlay_rejection_frequency_help_popover()
            st.dataframe(rejection_df, use_container_width=True, hide_index=True)
        else:
            st.caption("이번 실행에서는 오버레이로 제외된 종목이 기록되지 않았습니다.")
        regime_event_df = _build_market_regime_event_view(selection_df)
        if not regime_event_df.empty:
            regime_title_col, regime_help_col = st.columns([0.92, 0.08], gap="small")
            with regime_title_col:
                st.markdown("##### Market Regime Events")
            with regime_help_col:
                _render_market_regime_events_help_popover()
            st.dataframe(regime_event_df, use_container_width=True, hide_index=True)
    with frequency_tab:
        frequency_df = _build_selection_frequency_view(selection_df)
        if frequency_df.empty:
            st.info("이번 실행에서는 선택 빈도 요약을 만들 수 있는 데이터가 없습니다.")
        else:
            st.caption("이 표는 전략이 여러 리밸런싱에 걸쳐 반복적으로 선택하는 종목이 무엇인지 보기 위한 요약입니다.")
            st.dataframe(frequency_df, use_container_width=True, hide_index=True)

__all__ = [name for name in globals() if not name.startswith("__")]
