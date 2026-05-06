from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.final_selected_portfolio_dashboard_helpers import (
    build_selected_portfolio_current_weight_input_table,
    build_selected_portfolio_drift_alert_table,
    build_selected_portfolio_drift_table,
    build_selected_portfolio_component_table,
    build_selected_portfolio_dashboard_table,
    build_selected_portfolio_evidence_table,
    filter_selected_portfolio_rows,
    final_selected_portfolio_label,
    selected_portfolio_active_components,
    selected_portfolio_benchmark_options,
    selected_portfolio_component_default_symbol,
    selected_portfolio_source_type_options,
    selected_portfolio_status_options,
)
from app.web.runtime import (
    FINAL_SELECTED_PORTFOLIO_STATUS_LABELS,
    FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS,
    FINAL_SELECTION_DECISION_REGISTRY_FILE,
    build_selected_portfolio_current_weight_inputs,
    build_selected_portfolio_drift_alert_preview,
    build_selected_portfolio_drift_check,
    build_selected_portfolio_performance_recheck,
    build_selected_portfolio_recheck_defaults,
    load_final_selected_portfolio_dashboard,
    load_latest_selected_portfolio_prices,
)


def _status_tone(status: str) -> str:
    if status in {"normal"}:
        return "positive"
    if status in {"watch", "rebalance_needed", "re_review_needed"}:
        return "warning"
    if status == "blocked":
        return "danger"
    return "neutral"


def _alert_tone(alert_route: str) -> str:
    if alert_route == "NO_ALERT":
        return "positive"
    if alert_route in {"WATCH_ALERT", "INPUT_REVIEW_ALERT"}:
        return "warning"
    if alert_route == "REBALANCE_REVIEW_ALERT":
        return "danger"
    return "neutral"


def _format_pct(value: Any, *, default: str = "-") -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return f"{numeric:.2%}"


def _format_money(value: Any, *, default: str = "-") -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return f"{numeric:,.0f}"


def _coerce_date(value: Any, fallback: date) -> date:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return fallback
    return parsed.date()


def _summary_cards(summary: dict[str, Any]) -> list[dict[str, Any]]:
    status_counts = dict(summary.get("status_counts") or {})
    return [
        {
            "title": "Final Review Records",
            "value": summary.get("final_decision_count", 0),
            "detail": "Final Review 전체 판단 row",
            "tone": "positive" if summary.get("final_decision_count") else "neutral",
        },
        {
            "title": "Selected Portfolios",
            "value": summary.get("selected_decision_count", 0),
            "detail": "최신 기간 재검증 대상",
            "tone": "positive" if summary.get("selected_decision_count") else "neutral",
        },
        {
            "title": "Normal",
            "value": status_counts.get("normal", 0),
            "detail": "선정 row / allocation / blocker 기준 통과",
            "tone": "positive" if status_counts.get("normal") else "neutral",
        },
        {
            "title": "Watch / Review",
            "value": status_counts.get("watch", 0)
            + status_counts.get("rebalance_needed", 0)
            + status_counts.get("re_review_needed", 0),
            "detail": "관찰 또는 재검토 필요",
            "tone": "warning" if (
                status_counts.get("watch", 0)
                + status_counts.get("rebalance_needed", 0)
                + status_counts.get("re_review_needed", 0)
            ) else "neutral",
        },
        {
            "title": "Blocked",
            "value": status_counts.get("blocked", 0),
            "detail": "운영 대상으로 보기 전 보강 필요",
            "tone": "danger" if status_counts.get("blocked") else "neutral",
        },
        {
            "title": "Live Approval / Order",
            "value": "Disabled",
            "detail": "Phase36은 승인/주문을 만들지 않음",
            "tone": "neutral",
        },
    ]


def _render_empty_state(summary: dict[str, Any]) -> None:
    if not summary.get("final_decision_count"):
        st.info("아직 Final Review에서 기록된 최종 판단 row가 없습니다.")
        st.caption(f"Path: {FINAL_SELECTION_DECISION_REGISTRY_FILE}")
        return
    st.warning(
        "Final Review 기록은 있지만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 포트폴리오가 없습니다. "
        "`Backtest > Final Review`에서 최종 판단이 선정으로 저장된 row만 이 대시보드에 운영 대상으로 표시됩니다."
    )
    st.caption(f"Path: {FINAL_SELECTION_DECISION_REGISTRY_FILE}")


def _render_selected_row_detail(row: dict[str, Any]) -> None:
    st.markdown("#### Snapshot")
    render_badge_strip(
        [
            {
                "label": "Status",
                "value": row.get("operation_status_label"),
                "tone": _status_tone(str(row.get("operation_status") or "")),
            },
            {"label": "Decision ID", "value": row.get("decision_id"), "tone": "neutral"},
            {"label": "Source", "value": f"{row.get('source_type')} / {row.get('source_id')}", "tone": "neutral"},
            {"label": "Target Weight", "value": f"{float(row.get('target_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Benchmark", "value": row.get("benchmark_label"), "tone": "neutral"},
            {"label": "Original Period", "value": f"{row.get('baseline_start') or '-'} -> {row.get('baseline_end') or '-'}", "tone": "neutral"},
            {"label": "Baseline CAGR", "value": _format_pct(row.get("baseline_cagr")), "tone": "positive"},
            {"label": "Baseline MDD", "value": _format_pct(row.get("baseline_mdd")), "tone": "warning"},
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    st.caption(str(row.get("status_reason") or "-"))

    _render_performance_recheck(row)

    component_df = build_selected_portfolio_component_table(row)
    if component_df.empty:
        st.warning("선택된 포트폴리오에 active component가 없습니다.")
    else:
        st.markdown("#### Allocation")
        st.caption("Final Review에서 선정한 target allocation입니다. 실제 보유 상태 점검은 아래 Allocation Check에서 별도로 확인합니다.")
        st.dataframe(component_df, width="stretch", hide_index=True)

    _render_operator_context(row)

    with st.expander("Allocation Check: 실제 보유 상태 / drift 점검", expanded=False):
        _render_selected_row_drift_check(row)

    _render_execution_boundary()

    with st.expander("Audit / Developer Details", expanded=False):
        st.caption("일반 QA에서는 이 원본 JSON을 보지 않아도 됩니다. 저장 row 구조를 확인할 때만 펼쳐 봅니다.")
        st.json(row.get("raw_decision") or {})


def _render_operator_context(row: dict[str, Any]) -> None:
    st.markdown("#### Operator Context")
    detail_cols = st.columns(2, gap="small")
    with detail_cols[0]:
        with st.container(border=True):
            st.markdown("##### 운영 판단")
            st.markdown(f"**선정 사유**  \n{row.get('operator_reason') or '-'}")
            st.markdown(f"**제약 조건**  \n{row.get('operator_constraints') or '-'}")
            st.markdown(f"**다음 행동**  \n{row.get('operator_next_action') or '-'}")
    with detail_cols[1]:
        with st.container(border=True):
            st.markdown("##### 관찰 기준")
            st.markdown(f"**점검 주기**  \n{row.get('review_cadence') or '-'}")
            triggers = [str(trigger) for trigger in list(row.get("review_triggers") or []) if str(trigger)]
            blockers = [str(blocker) for blocker in list(row.get("blockers") or []) if str(blocker)]
            if triggers:
                st.markdown("**재검토 trigger**")
                for trigger in triggers:
                    st.markdown(f"- {trigger}")
            else:
                st.caption("등록된 review trigger가 없습니다.")
            if blockers:
                st.warning("남아 있는 blocker: " + ", ".join(blockers))

    evidence_df = build_selected_portfolio_evidence_table(row)
    with st.expander("Final Review 검증 근거", expanded=False):
        if evidence_df.empty:
            st.info("표시할 evidence check row가 없습니다.")
        else:
            st.dataframe(evidence_df, width="stretch", hide_index=True)


def _render_execution_boundary() -> None:
    with st.container(border=True):
        st.markdown("#### Execution Boundary")
        st.caption(
            "이 대시보드는 최종 선정 포트폴리오를 운영 대상으로 읽는 화면입니다. "
            "기간 확장 재검증과 drift 점검은 read-only이며 실제 투자 승인, broker 주문, 자동 리밸런싱은 만들지 않습니다."
        )
        action_cols = st.columns(3, gap="small")
        action_cols[0].button("Live Approval", disabled=True, width="stretch")
        action_cols[1].button("Broker Order", disabled=True, width="stretch")
        action_cols[2].button("Auto Rebalance", disabled=True, width="stretch")


def _render_performance_recheck(row: dict[str, Any]) -> None:
    st.markdown("#### Performance Recheck")
    st.caption(
        "선정 당시의 component contract를 다시 실행해, 사용자가 지정한 기간에서 포트폴리오 성과가 유지되는지 확인합니다. "
        "기본 종료일은 DB에 있는 최신 시장일입니다."
    )
    defaults = build_selected_portfolio_recheck_defaults(row)
    if defaults.get("latest_market_date_error"):
        st.warning(f"최신 시장일 확인 실패: {defaults.get('latest_market_date_error')}")

    fallback_start = date(2016, 1, 1)
    fallback_end = date.today()
    default_start = _coerce_date(defaults.get("default_start"), fallback_start)
    default_end = _coerce_date(defaults.get("default_end"), fallback_end)
    decision_id = str(row.get("decision_id") or "selected_portfolio")
    form_cols = st.columns([0.22, 0.22, 0.24, 0.18, 0.14], gap="small")
    with form_cols[0]:
        recheck_start = st.date_input(
            "Recheck start",
            value=default_start,
            key=f"selected_portfolio_recheck_start_{decision_id}",
        )
    with form_cols[1]:
        recheck_end = st.date_input(
            "Recheck end",
            value=default_end,
            key=f"selected_portfolio_recheck_end_{decision_id}",
        )
    with form_cols[2]:
        initial_capital = st.number_input(
            "Virtual capital",
            min_value=1_000.0,
            value=10_000.0,
            step=1_000.0,
            key=f"selected_portfolio_recheck_capital_{decision_id}",
        )
    with form_cols[3]:
        st.metric("Original End", defaults.get("baseline_end") or "-")
    with form_cols[4]:
        run_clicked = st.button(
            "Run Recheck",
            key=f"selected_portfolio_run_recheck_{decision_id}",
            width="stretch",
        )

    result_key = f"selected_portfolio_recheck_result_{decision_id}"
    if run_clicked:
        with st.spinner("선정 포트폴리오 contract를 재실행하는 중입니다..."):
            st.session_state[result_key] = build_selected_portfolio_performance_recheck(
                row,
                start=str(recheck_start),
                end=str(recheck_end),
                initial_capital=float(initial_capital),
            )

    result = dict(st.session_state.get(result_key) or {})
    if not result:
        st.info("날짜 범위와 가상 투자금을 확인한 뒤 `Run Recheck`를 누르면 최신 기간 기준 성과를 바로 계산합니다.")
        return
    if result.get("status") == "error":
        st.error(str(result.get("error") or "Performance recheck failed."))
        for blocker in list(result.get("blockers") or []):
            st.warning(str(blocker))
        return

    for blocker in list(result.get("blockers") or []):
        st.warning(str(blocker))

    portfolio_summary = dict(result.get("portfolio_summary") or {})
    benchmark_summary = dict(result.get("benchmark_summary") or {})
    baseline_summary = dict(result.get("baseline_summary") or {})
    change_summary = dict(result.get("change_summary") or {})
    period = dict(result.get("period") or {})
    render_status_card_grid(
        [
            {
                "title": "Recheck Verdict",
                "value": result.get("verdict_route"),
                "detail": result.get("verdict"),
                "tone": "positive" if result.get("verdict_route") == "SELECTION_THESIS_HOLDS" else "warning",
            },
            {
                "title": "Portfolio Value",
                "value": _format_money(portfolio_summary.get("end_balance")),
                "detail": f"Total return {_format_pct(portfolio_summary.get('total_return'))}",
                "tone": "positive",
            },
            {
                "title": "Recheck CAGR",
                "value": _format_pct(portfolio_summary.get("cagr")),
                "detail": f"Original {_format_pct(baseline_summary.get('cagr'))}",
                "tone": "positive" if (change_summary.get("cagr_delta_vs_baseline") or 0.0) >= 0 else "warning",
            },
            {
                "title": "Recheck MDD",
                "value": _format_pct(portfolio_summary.get("mdd")),
                "detail": f"Original {_format_pct(baseline_summary.get('mdd'))}",
                "tone": "warning",
            },
            {
                "title": "Benchmark Spread",
                "value": _format_pct(change_summary.get("net_cagr_spread")),
                "detail": f"Benchmark {result.get('benchmark_label') or '-'} CAGR {_format_pct(benchmark_summary.get('cagr'))}",
                "tone": "positive" if (change_summary.get("net_cagr_spread") or 0.0) >= 0 else "warning",
            },
        ]
    )
    st.caption(
        f"Original period: {period.get('baseline_start') or '-'} -> {period.get('baseline_end') or '-'} | "
        f"Recheck period: {period.get('start') or '-'} -> {period.get('end') or '-'}"
    )

    chart_df = result.get("chart_df")
    if isinstance(chart_df, pd.DataFrame) and not chart_df.empty:
        chart_view = chart_df.copy()
        chart_view["Date"] = pd.to_datetime(chart_view["Date"], errors="coerce")
        chart_view = chart_view.dropna(subset=["Date"]).set_index("Date")
        st.line_chart(chart_view)

    st.markdown("#### What Changed")
    comparison_df = pd.DataFrame(
        [
            {
                "Metric": "CAGR",
                "Original": baseline_summary.get("cagr"),
                "Recheck": portfolio_summary.get("cagr"),
                "Change": change_summary.get("cagr_delta_vs_baseline"),
            },
            {
                "Metric": "Maximum Drawdown",
                "Original": baseline_summary.get("mdd"),
                "Recheck": portfolio_summary.get("mdd"),
                "Change": change_summary.get("mdd_delta_vs_baseline"),
            },
            {
                "Metric": "Benchmark CAGR Spread",
                "Original": None,
                "Recheck": change_summary.get("net_cagr_spread"),
                "Change": None,
            },
        ]
    )
    for column in ["Original", "Recheck", "Change"]:
        comparison_df[column] = comparison_df[column].map(lambda value: _format_pct(value) if value is not None else "-")
    st.dataframe(comparison_df, width="stretch", hide_index=True)

    component_df = pd.DataFrame(list(result.get("component_rows") or []))
    if not component_df.empty:
        st.markdown("##### Component contribution")
        for column in ["Total Return", "Weighted Contribution", "CAGR", "MDD"]:
            if column in component_df.columns:
                component_df[column] = component_df[column].map(lambda value: _format_pct(value) if value is not None else "-")
        if "Target Weight" in component_df.columns:
            component_df["Target Weight"] = component_df["Target Weight"].map(
                lambda value: f"{float(value):.1f}%" if value is not None and not pd.isna(value) else "-"
            )
        st.dataframe(component_df, width="stretch", hide_index=True)

    extremes = dict(result.get("period_extremes") or {})
    extreme_cols = st.columns(2, gap="small")
    with extreme_cols[0]:
        best_df = pd.DataFrame(extremes.get("best") or [])
        st.markdown("##### Strongest periods")
        if best_df.empty:
            st.caption("표시할 strong period가 없습니다.")
        else:
            if "Total Return" in best_df.columns:
                best_df["Total Return"] = best_df["Total Return"].map(lambda value: _format_pct(value))
            if "Total Balance" in best_df.columns:
                best_df["Total Balance"] = best_df["Total Balance"].map(lambda value: _format_money(value))
            st.dataframe(best_df, width="stretch", hide_index=True)
    with extreme_cols[1]:
        worst_df = pd.DataFrame(extremes.get("worst") or [])
        st.markdown("##### Weakest periods")
        if worst_df.empty:
            st.caption("표시할 weak period가 없습니다.")
        else:
            if "Total Return" in worst_df.columns:
                worst_df["Total Return"] = worst_df["Total Return"].map(lambda value: _format_pct(value))
            if "Total Balance" in worst_df.columns:
                worst_df["Total Balance"] = worst_df["Total Balance"].map(lambda value: _format_money(value))
            st.dataframe(worst_df, width="stretch", hide_index=True)


def _render_selected_row_drift_check(row: dict[str, Any]) -> None:
    st.markdown("##### Allocation Check")
    st.caption(
        "이 영역은 성과 재검증이 아니라, 실제 또는 가정 보유 상태가 target allocation에서 얼마나 벗어났는지 보는 고급 점검입니다. "
        "입력값은 저장되지 않고 주문도 만들지 않습니다."
    )
    components = selected_portfolio_active_components(row)
    if not components:
        st.info("drift를 계산할 active component가 없습니다.")
        return

    threshold_cols = st.columns([0.34, 0.33, 0.33], gap="small")
    with threshold_cols[0]:
        drift_threshold = st.number_input(
            "Rebalance threshold (%)",
            min_value=0.5,
            max_value=50.0,
            value=5.0,
            step=0.5,
            key=f"selected_portfolio_drift_threshold_{row.get('decision_id')}",
            help="component별 target/current 차이가 이 값 이상이면 리밸런싱 검토 필요로 봅니다.",
        )
    with threshold_cols[1]:
        watch_threshold = st.number_input(
            "Watch threshold (%)",
            min_value=0.1,
            max_value=50.0,
            value=2.0,
            step=0.5,
            key=f"selected_portfolio_watch_threshold_{row.get('decision_id')}",
            help="리밸런싱 전 관찰이 필요한 drift 기준입니다.",
        )
    with threshold_cols[2]:
        total_tolerance = st.number_input(
            "Total tolerance (%)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            key=f"selected_portfolio_total_tolerance_{row.get('decision_id')}",
            help="현재 비중 합계가 100%에서 이 범위 이상 벗어나면 입력 확인이 필요합니다.",
        )

    current_weights: dict[str, float] = {}
    input_mode = st.radio(
        "현재 보유 상태 입력 방식",
        options=["current_value", "shares_x_price", "current_weight"],
        format_func=lambda mode: FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(mode, mode),
        horizontal=True,
        key=f"selected_portfolio_current_input_mode_{row.get('decision_id')}",
    )
    value_input_contract: dict[str, Any] | None = None
    if input_mode == "current_weight":
        st.caption("이미 다른 곳에서 현재 비중을 계산해 둔 경우에만 씁니다. 기본값은 target weight입니다.")
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            target_weight = float(component.get("target_weight") or 0.0)
            with input_cols[index % 2]:
                current_weights[component_id] = st.number_input(
                    f"{title} current weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=target_weight,
                    step=0.5,
                    key=f"selected_portfolio_current_weight_{row.get('decision_id')}_{component_id}",
                )
    elif input_mode == "current_value":
        st.caption(
            "실제 또는 가정 보유금액을 component별로 입력하면 전체 평가금액 대비 현재 비중으로 변환합니다. "
            "통화 단위는 모두 같기만 하면 됩니다."
        )
        cash_value = st.number_input(
            "Unassigned cash / outside value",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"selected_portfolio_cash_value_{row.get('decision_id')}",
            help="target component 밖에 남아 있는 현금이나 제외 자산이 있으면 입력합니다.",
        )
        component_inputs: dict[str, dict[str, Any]] = {}
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            target_weight = float(component.get("target_weight") or 0.0)
            with input_cols[index % 2]:
                component_inputs[component_id] = {
                    "current_value": st.number_input(
                        f"{title} current value",
                        min_value=0.0,
                        value=target_weight,
                        step=1.0,
                        key=f"selected_portfolio_current_value_{row.get('decision_id')}_{component_id}",
                    ),
                    "price_source": "manual_current_value",
                }
        value_input_contract = build_selected_portfolio_current_weight_inputs(
            row,
            component_inputs=component_inputs,
            cash_value=cash_value,
            input_mode="current_value",
        )
        current_weights = dict(value_input_contract.get("current_weights") or {})
    else:
        st.caption(
            "실제 보유 수량과 현재가를 알고 있을 때 쓰는 고급 입력입니다. "
            "DB latest close는 보조값이며, 가격과 수량은 저장되지 않습니다."
        )
        component_symbols: dict[str, str] = {}
        symbol_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            default_symbol = selected_portfolio_component_default_symbol(component)
            with symbol_cols[index % 2]:
                component_symbols[component_id] = st.text_input(
                    f"{title} holding symbol",
                    value=default_symbol,
                    key=f"selected_portfolio_holding_symbol_{row.get('decision_id')}_{component_id}",
                    help="DB latest close 조회에만 쓰는 선택 입력입니다.",
                ).strip().upper()

        fetch_cols = st.columns([0.35, 0.35, 0.30], gap="small")
        with fetch_cols[0]:
            price_end = st.text_input(
                "DB price end date",
                value="",
                placeholder="YYYY-MM-DD",
                key=f"selected_portfolio_price_end_{row.get('decision_id')}",
            ).strip()
        symbols_to_fetch = sorted({symbol for symbol in component_symbols.values() if symbol})
        fetch_key = f"selected_portfolio_latest_price_result_{row.get('decision_id')}"
        with fetch_cols[1]:
            if st.button(
                "Load latest close",
                disabled=not symbols_to_fetch,
                key=f"selected_portfolio_load_latest_price_{row.get('decision_id')}",
                width="stretch",
            ):
                price_result = load_latest_selected_portfolio_prices(symbols_to_fetch, end=price_end or None)
                st.session_state[fetch_key] = price_result
                price_by_symbol = dict(price_result.get("price_by_symbol") or {})
                for index, component in enumerate(components):
                    component_id = str(component.get("component_id") or f"component_{index + 1}")
                    symbol = component_symbols.get(component_id)
                    price_row = dict(price_by_symbol.get(symbol) or {})
                    if price_row.get("price") is not None:
                        st.session_state[
                            f"selected_portfolio_holding_price_{row.get('decision_id')}_{component_id}"
                        ] = float(price_row.get("price") or 0.0)
                        st.session_state[
                            f"selected_portfolio_holding_price_date_{row.get('decision_id')}_{component_id}"
                        ] = price_row.get("latest_date")
        with fetch_cols[2]:
            st.metric("Symbols", len(symbols_to_fetch))

        latest_price_result = dict(st.session_state.get(fetch_key) or {})
        if latest_price_result.get("status") == "error":
            st.warning(f"DB latest close 조회 실패: {latest_price_result.get('error')}")
        elif latest_price_result.get("rows"):
            with st.expander("Loaded latest close rows", expanded=False):
                st.dataframe(list(latest_price_result.get("rows") or []), width="stretch", hide_index=True)
                missing = list(latest_price_result.get("missing_symbols") or [])
                if missing:
                    st.caption(f"missing symbols: {', '.join(missing)}")

        cash_value = st.number_input(
            "Unassigned cash / outside value",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"selected_portfolio_holding_cash_value_{row.get('decision_id')}",
            help="target component 밖에 남아 있는 현금이나 제외 자산이 있으면 입력합니다.",
        )
        component_inputs = {}
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            price_key = f"selected_portfolio_holding_price_{row.get('decision_id')}_{component_id}"
            price_date_key = f"selected_portfolio_holding_price_date_{row.get('decision_id')}_{component_id}"
            with input_cols[index % 2]:
                shares = st.number_input(
                    f"{title} shares",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key=f"selected_portfolio_holding_shares_{row.get('decision_id')}_{component_id}",
                )
                price_kwargs = {
                    "min_value": 0.0,
                    "step": 0.01,
                    "key": price_key,
                }
                if price_key not in st.session_state:
                    price_kwargs["value"] = 0.0
                price = st.number_input(f"{title} current price", **price_kwargs)
            component_inputs[component_id] = {
                "symbol": component_symbols.get(component_id),
                "shares": shares,
                "price": price,
                "price_date": st.session_state.get(price_date_key),
                "price_source": "db_latest_close" if st.session_state.get(price_date_key) else "manual_price",
            }
        value_input_contract = build_selected_portfolio_current_weight_inputs(
            row,
            component_inputs=component_inputs,
            cash_value=cash_value,
            input_mode="shares_x_price",
        )
        current_weights = dict(value_input_contract.get("current_weights") or {})

    if value_input_contract is not None:
        value_metrics = dict(value_input_contract.get("metrics") or {})
        render_badge_strip(
            [
                {"label": "Input Mode", "value": value_input_contract.get("input_mode_label"), "tone": "neutral"},
                {"label": "Portfolio Value", "value": f"{float(value_metrics.get('portfolio_value_total') or 0.0):,.2f}", "tone": "neutral"},
                {"label": "Cash / Outside", "value": f"{float(value_metrics.get('cash_value') or 0.0):,.2f}", "tone": "neutral"},
                {"label": "Weight Total", "value": f"{float(value_metrics.get('current_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            ]
        )
        input_df = build_selected_portfolio_current_weight_input_table(value_input_contract)
        if not input_df.empty:
            st.dataframe(input_df, width="stretch", hide_index=True)
        for blocker in list(value_input_contract.get("blockers") or []):
            st.warning(str(blocker))

    drift_check = build_selected_portfolio_drift_check(
        row,
        current_weights=current_weights,
        drift_threshold_pct=float(drift_threshold),
        watch_threshold_pct=float(watch_threshold),
        total_weight_tolerance_pct=float(total_tolerance),
    )
    metrics = dict(drift_check.get("metrics") or {})
    render_badge_strip(
        [
            {"label": "Drift Route", "value": drift_check.get("route_label"), "tone": _status_tone("rebalance_needed" if drift_check.get("route") == "REBALANCE_NEEDED" else "normal" if drift_check.get("route") == "DRIFT_ALIGNED" else "watch")},
            {"label": "Current Total", "value": f"{float(metrics.get('current_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Target Total", "value": f"{float(metrics.get('target_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Max Drift", "value": f"{float(metrics.get('max_abs_drift') or 0.0):.1f}%", "tone": "warning" if float(metrics.get("max_abs_drift") or 0.0) >= float(drift_threshold) else "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    st.caption(str(drift_check.get("verdict") or "-"))
    drift_df = build_selected_portfolio_drift_table(drift_check)
    if not drift_df.empty:
        st.dataframe(drift_df, width="stretch", hide_index=True)
    if drift_check.get("blockers"):
        for blocker in list(drift_check.get("blockers") or []):
            st.warning(str(blocker))
    alert_preview = build_selected_portfolio_drift_alert_preview(row, drift_check=drift_check)
    alert_metrics = dict(alert_preview.get("metrics") or {})
    st.markdown("##### Drift Alert / Review Trigger Preview")
    st.caption(
        "drift 결과를 운영 경고와 Final Review review trigger 관점으로 다시 읽습니다. "
        "이 preview는 alert registry를 저장하지 않고 주문 지시도 만들지 않습니다."
    )
    render_badge_strip(
        [
            {
                "label": "Alert Route",
                "value": alert_preview.get("alert_route_label"),
                "tone": _alert_tone(str(alert_preview.get("alert_route") or "")),
            },
            {"label": "Alert Level", "value": alert_preview.get("alert_level"), "tone": "neutral"},
            {
                "label": "Review Triggers",
                "value": alert_metrics.get("review_trigger_count", 0),
                "tone": "neutral",
            },
            {"label": "Alert Save", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    st.caption(str(alert_preview.get("verdict") or "-"))
    alert_df = build_selected_portfolio_drift_alert_table(alert_preview)
    if alert_df.empty:
        st.info("표시할 drift alert / review trigger row가 없습니다.")
    else:
        st.dataframe(alert_df, width="stretch", hide_index=True)
    st.info(str(drift_check.get("next_action") or "-"))
    st.info(str(alert_preview.get("next_action") or "-"))


def render_final_selected_portfolio_dashboard_page() -> None:
    st.title("Selected Portfolio Dashboard")
    st.caption(
        "Final Review에서 실전 후보로 선정한 포트폴리오를 최신 기간으로 다시 계산하고, "
        "선정 당시 근거가 유지되는지 확인하는 Phase36 대시보드입니다."
    )

    dashboard = load_final_selected_portfolio_dashboard()
    summary = dict(dashboard.get("summary") or {})
    rows = list(dashboard.get("dashboard_rows") or [])

    render_status_card_grid(_summary_cards(summary))

    with st.container(border=True):
        st.markdown("#### 데이터 출처와 화면 경계")
        data_cols = st.columns(3, gap="small")
        data_cols[0].metric("Source", "Final Review Decisions")
        data_cols[0].caption(str(FINAL_SELECTION_DECISION_REGISTRY_FILE))
        data_cols[1].metric("Selected Filter", "Practical Portfolio")
        data_cols[1].caption("`SELECT_FOR_PRACTICAL_PORTFOLIO` 또는 `selected_practical_portfolio=true`")
        data_cols[2].metric("Write Policy", "Read Only")
        data_cols[2].caption("재검증과 drift 점검은 새 판단 row나 주문 row를 저장하지 않습니다.")

    if not rows:
        _render_empty_state(summary)
        return

    st.markdown("#### 운영 대상 목록")
    filter_cols = st.columns([0.32, 0.28, 0.24, 0.16], gap="small")
    status_options = selected_portfolio_status_options(rows)
    source_type_options = selected_portfolio_source_type_options(rows)
    benchmark_options = selected_portfolio_benchmark_options(rows)
    with filter_cols[0]:
        selected_statuses = st.multiselect(
            "Status",
            options=status_options,
            default=status_options,
            format_func=lambda status: FINAL_SELECTED_PORTFOLIO_STATUS_LABELS.get(status, status),
            key="selected_portfolio_dashboard_status_filter",
        )
    with filter_cols[1]:
        selected_source_types = st.multiselect(
            "Source Type",
            options=source_type_options,
            default=source_type_options,
            key="selected_portfolio_dashboard_source_filter",
        )
    with filter_cols[2]:
        selected_benchmark = st.selectbox(
            "Benchmark",
            options=benchmark_options,
            key="selected_portfolio_dashboard_benchmark_filter",
        )
    with filter_cols[3]:
        st.metric("Total", len(rows))

    filtered_rows = filter_selected_portfolio_rows(
        rows,
        statuses=selected_statuses,
        source_types=selected_source_types,
        benchmark=str(selected_benchmark),
    )
    filter_cols[3].metric("Shown", len(filtered_rows))
    if not filtered_rows:
        st.warning("현재 filter 조건에 맞는 선정 포트폴리오가 없습니다.")
        return

    st.dataframe(build_selected_portfolio_dashboard_table(filtered_rows), width="stretch", hide_index=True)
    labels = [final_selected_portfolio_label(row) for row in filtered_rows]
    selected_label = st.selectbox(
        "상세 확인",
        options=labels,
        key="selected_portfolio_dashboard_selected_row",
    )
    selected_row = filtered_rows[labels.index(selected_label)]
    _render_selected_row_detail(selected_row)
