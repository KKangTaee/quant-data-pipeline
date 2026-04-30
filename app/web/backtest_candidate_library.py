from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.web.backtest_candidate_library_helpers import (
    build_candidate_badges,
    build_candidate_library_rows,
    build_candidate_replay_payload,
    build_candidate_snapshot_cards,
    candidate_library_record_label,
    load_candidate_library_records,
    run_candidate_replay_payload,
)
from app.web.backtest_common import _render_summary_metrics
from app.web.backtest_result_display import (
    _build_balance_extremes_tables,
    _build_period_extremes_tables,
    _render_balance_chart_with_markers,
    _render_data_trust_summary,
    _render_dynamic_universe_details,
    _render_real_money_details,
)
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.runtime import CURRENT_CANDIDATE_REGISTRY_FILE, PRE_LIVE_CANDIDATE_REGISTRY_FILE
from app.web.runtime.backtest import BacktestDataError, BacktestInputError


# Render the Operations-owned saved candidate inspector and replay surface.
def render_candidate_library_page() -> None:
    st.title("Candidate Library")
    st.caption(
        "저장된 Current Candidate / Pre-Live 후보를 다시 열어 보고, 필요하면 저장된 contract로 결과 곡선을 재생성합니다."
    )

    records = load_candidate_library_records()
    if not records:
        st.info("저장된 current candidate가 아직 없습니다. Backtest > Candidate Review에서 후보를 registry에 저장하면 여기에 표시됩니다.")
        st.caption(f"Current Candidate path: {CURRENT_CANDIDATE_REGISTRY_FILE}")
        return

    st.info(
        "Candidate Library는 새 workflow 단계가 아니라 보관함입니다. "
        "후보를 다시 검토하거나 그래프를 확인할 때 쓰고, 후보 등록 / 운영 기록 / 제안 판단은 기존 Backtest 흐름에서 처리합니다."
    )
    st.caption(f"Current Candidate path: {CURRENT_CANDIDATE_REGISTRY_FILE}")
    st.caption(f"Pre-Live path: {PRE_LIVE_CANDIDATE_REGISTRY_FILE}")

    library_df = build_candidate_library_rows(records)
    filtered_df = _render_candidate_filters(library_df)
    if filtered_df.empty:
        st.warning("현재 필터 조건에 맞는 후보가 없습니다.")
        return

    display_df = filtered_df.drop(columns=["_record_index", "_search_text"], errors="ignore").copy()
    st.dataframe(
        _format_candidate_table(display_df),
        use_container_width=True,
        hide_index=True,
    )

    filtered_records = [records[int(index)] for index in filtered_df["_record_index"].tolist()]
    selected_record = _select_candidate_record(filtered_records)
    if not selected_record:
        return

    _render_selected_candidate(selected_record)
    _render_candidate_replay(selected_record)


# Render filters that keep the candidate table as a searchable library.
def _render_candidate_filters(library_df: pd.DataFrame) -> pd.DataFrame:
    filter_cols = st.columns([1.0, 1.0, 1.4], gap="large")
    with filter_cols[0]:
        family_options = ["All"] + sorted(library_df["Family"].dropna().astype(str).unique().tolist())
        selected_family = st.selectbox("Strategy Family", options=family_options, key="candidate_library_family_filter")
    with filter_cols[1]:
        pre_live_options = ["All"] + sorted(library_df["Pre-Live"].dropna().astype(str).unique().tolist())
        selected_pre_live = st.selectbox("Pre-Live Status", options=pre_live_options, key="candidate_library_pre_live_filter")
    with filter_cols[2]:
        search_text = st.text_input(
            "Search",
            value="",
            placeholder="title, registry id, ticker",
            key="candidate_library_search",
        ).strip().lower()

    filtered_df = library_df.copy()
    if selected_family != "All":
        filtered_df = filtered_df[filtered_df["Family"].astype(str) == selected_family]
    if selected_pre_live != "All":
        filtered_df = filtered_df[filtered_df["Pre-Live"].astype(str) == selected_pre_live]
    if search_text:
        filtered_df = filtered_df[filtered_df["_search_text"].str.contains(search_text, na=False)]
    return filtered_df.reset_index(drop=True)


# Pick the candidate whose stored snapshot or replay result should be shown.
def _select_candidate_record(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    labels = [candidate_library_record_label(record) for record in records]
    if not labels:
        return None
    selected_label = st.selectbox(
        "Inspect Candidate",
        options=labels,
        index=0,
        key="candidate_library_selected_record",
    )
    return records[labels.index(selected_label)]


# Show the registry snapshot before running any expensive replay.
def _render_selected_candidate(record: dict[str, Any]) -> None:
    current = record.get("current") or {}
    pre_live = record.get("pre_live") or {}
    render_status_card_grid(build_candidate_snapshot_cards(record))
    render_badge_strip(build_candidate_badges(record))

    snapshot_tab, contract_tab, pre_live_tab, raw_tab = st.tabs(
        ["Stored Snapshot", "Replay Contract", "Pre-Live Record", "Raw Records"]
    )
    with snapshot_tab:
        result = current.get("result") or {}
        review_context = current.get("review_context") or {}
        st.markdown("##### Registry Snapshot")
        st.json(
            {
                "registry_id": current.get("registry_id"),
                "revision_id": current.get("revision_id"),
                "recorded_at": current.get("recorded_at"),
                "record_type": current.get("record_type"),
                "candidate_role": current.get("candidate_role"),
                "title": current.get("title"),
                "result": result,
                "compare_readiness": review_context.get("compare_readiness_evaluation"),
            }
        )
    with contract_tab:
        st.markdown("##### Contract Used For Replay")
        st.caption("이 값으로 DB-backed 백테스트를 다시 실행해 그래프와 상세 결과표를 복원합니다.")
        try:
            st.json(build_candidate_replay_payload(current))
        except BacktestInputError as exc:
            st.warning(str(exc))
            st.json(current.get("contract") or {})
    with pre_live_tab:
        if pre_live:
            st.json(pre_live)
        else:
            st.info("이 후보와 연결된 Pre-Live 운영 기록이 아직 없습니다.")
    with raw_tab:
        st.markdown("##### Current Candidate Row")
        st.json(current)
        st.markdown("##### Matched Pre-Live Row")
        st.json(pre_live or {})


# Run or display the cached candidate replay result.
def _render_candidate_replay(record: dict[str, Any]) -> None:
    current = record.get("current") or {}
    registry_id = str(current.get("registry_id") or "")
    replay_state = st.session_state.get("candidate_library_replay_state") or {}
    cached_result = replay_state.get(registry_id)

    st.markdown("### Rebuild Result Curve")
    st.caption(
        "registry에는 compact snapshot만 저장됩니다. 아래 버튼은 저장된 contract로 백테스트를 다시 실행해 "
        "Single Strategy와 같은 그래프 / extremes / result table을 화면에 복원합니다."
    )

    action_cols = st.columns([0.26, 0.74], gap="large")
    with action_cols[0]:
        if st.button("Rebuild Result Curve", key="candidate_library_rebuild_result", use_container_width=True):
            try:
                payload = build_candidate_replay_payload(current)
                with st.spinner("Rebuilding candidate result from stored contract..."):
                    bundle = run_candidate_replay_payload(payload, current_row=current)
                replay_state[registry_id] = {"payload": payload, "bundle": bundle}
                st.session_state.candidate_library_replay_state = replay_state
                st.success("후보 결과 곡선을 다시 만들었습니다.")
                st.rerun()
            except BacktestInputError as exc:
                st.warning(f"Replay input issue: {exc}")
            except BacktestDataError as exc:
                st.error(f"Replay data issue: {exc}")
            except Exception as exc:
                st.error(f"Candidate replay failed: {exc}")
    with action_cols[1]:
        if cached_result:
            meta = cached_result.get("bundle", {}).get("meta") or {}
            replay_meta = meta.get("candidate_library_replay") or {}
            st.success(
                "현재 선택 후보의 replay 결과가 화면 캐시에 있습니다. "
                f"Replayed at: {replay_meta.get('replayed_at') or '-'}"
            )
        else:
            st.info("아직 이 후보의 result curve를 재생성하지 않았습니다.")

    if cached_result:
        _render_candidate_result_bundle(cached_result["bundle"])


# Render a replayed candidate bundle with the same core views as Single Strategy.
def _render_candidate_result_bundle(bundle: dict[str, Any]) -> None:
    summary_df = bundle["summary_df"]
    chart_df = bundle["chart_df"]
    result_df = bundle["result_df"]
    meta = dict(bundle.get("meta") or {})
    warnings = list(meta.get("warnings") or [])
    has_real_money_details = bool(meta.get("real_money_hardening"))
    has_dynamic_details = bool(bundle.get("dynamic_universe_snapshot_rows") or bundle.get("dynamic_candidate_status_rows"))

    st.markdown(f"#### Rebuilt Result: {bundle.get('strategy_name') or meta.get('strategy_name') or 'Candidate'}")
    if warnings:
        st.warning("이번 replay에서 같이 봐야 할 주의 사항이 있습니다.\n\n" + "\n".join(f"- {item}" for item in warnings))
    _render_data_trust_summary(meta)
    _render_summary_metrics(summary_df)

    tab_labels = ["Summary", "Equity Curve", "Balance Extremes", "Period Extremes"]
    if has_real_money_details:
        tab_labels.append("Real-Money")
    if has_dynamic_details:
        tab_labels.append("Dynamic Universe")
    tab_labels.extend(["Result Table", "Meta"])
    tabs = st.tabs(tab_labels)
    tab_iter = iter(tabs)
    summary_tab = next(tab_iter)
    curve_tab = next(tab_iter)
    balance_tab = next(tab_iter)
    periods_tab = next(tab_iter)
    real_money_tab = next(tab_iter) if has_real_money_details else None
    dynamic_tab = next(tab_iter) if has_dynamic_details else None
    table_tab = next(tab_iter)
    meta_tab = next(tab_iter)

    with summary_tab:
        st.dataframe(summary_df, use_container_width=True)
    with curve_tab:
        _render_balance_chart_with_markers(chart_df, result_df=result_df, title="Candidate Replay Equity Curve")
    with balance_tab:
        high_df, low_df = _build_balance_extremes_tables(chart_df, top_n=3)
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Top 3 Balance Highs")
            st.dataframe(high_df, use_container_width=True, hide_index=True)
        with right:
            st.markdown("##### Top 3 Balance Lows")
            st.dataframe(low_df, use_container_width=True, hide_index=True)
    with periods_tab:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=3)
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Top 3 Best Periods")
            st.dataframe(best_df, use_container_width=True, hide_index=True)
        with right:
            st.markdown("##### Top 3 Worst Periods")
            st.dataframe(worst_df, use_container_width=True, hide_index=True)
    if real_money_tab is not None:
        with real_money_tab:
            _render_real_money_details(bundle)
    if dynamic_tab is not None:
        with dynamic_tab:
            _render_dynamic_universe_details(bundle)
    with table_tab:
        st.dataframe(result_df, use_container_width=True)
    with meta_tab:
        st.json(meta)


def _format_candidate_table(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    for col in ["CAGR", "MDD"]:
        if col in formatted.columns:
            formatted[col] = formatted[col].map(_format_percent)
    if "Sharpe" in formatted.columns:
        formatted["Sharpe"] = formatted["Sharpe"].map(_format_number)
    if "End Balance" in formatted.columns:
        formatted["End Balance"] = formatted["End Balance"].map(_format_currency)
    return formatted


def _format_percent(value: Any) -> str:
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return "-"


def _format_number(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "-"


def _format_currency(value: Any) -> str:
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "-"
