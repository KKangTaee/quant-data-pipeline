from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.web.backtest_practical_validation_helpers import (
    VALIDATION_PROFILE_OPTIONS,
    VALIDATION_PROFILE_QUESTIONS,
    build_practical_validation_result,
    build_validation_profile,
    queue_final_review_source_from_validation,
    save_practical_validation_result,
    source_components_dataframe,
)
from app.web.backtest_practical_validation_replay import (
    RECHECK_MODE_EXTEND_TO_LATEST,
    RECHECK_MODE_LABELS,
    build_practical_validation_recheck_plan,
    run_practical_validation_actual_replay,
)
from app.web.backtest_ui_components import (
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.runtime import (
    PORTFOLIO_SELECTION_SOURCE_FILE,
    PRACTICAL_VALIDATION_RESULT_FILE,
    load_portfolio_selection_sources,
    load_practical_validation_results,
)


def _source_label(row: dict[str, Any]) -> str:
    return (
        f"{row.get('created_at') or '-'} | "
        f"{row.get('source_kind') or '-'} | "
        f"{row.get('source_title') or row.get('selection_source_id') or '-'}"
    )


def _render_source_summary(source: dict[str, Any]) -> None:
    summary = dict(source.get("summary") or {})
    period = dict(source.get("period") or {})
    construction = dict(source.get("construction") or {})
    render_badge_strip(
        [
            {"label": "Source", "value": source.get("source_kind") or "-", "tone": "neutral"},
            {"label": "Period", "value": f"{period.get('actual_start') or period.get('start') or '-'} -> {period.get('actual_end') or period.get('end') or '-'}", "tone": "neutral"},
            {"label": "CAGR", "value": summary.get("cagr") if summary.get("cagr") is not None else "-", "tone": "neutral"},
            {"label": "MDD", "value": summary.get("mdd") if summary.get("mdd") is not None else "-", "tone": "neutral"},
            {"label": "Weight Total", "value": f"{construction.get('target_weight_total', 0)}%", "tone": "neutral"},
        ]
    )
    component_df = source_components_dataframe(source)
    if component_df.empty:
        st.info("선택된 source에 component snapshot이 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)


def _render_validation_profile_form() -> dict[str, Any]:
    profile_options = list(VALIDATION_PROFILE_OPTIONS.keys())
    profile_id = st.selectbox(
        "검증 프로필",
        options=profile_options,
        format_func=lambda key: (
            f"{VALIDATION_PROFILE_OPTIONS[key]['label']} - "
            f"{VALIDATION_PROFILE_OPTIONS[key]['description']}"
        ),
        key="practical_validation_profile_id",
    )
    answers: dict[str, str] = {}
    question_items = list(VALIDATION_PROFILE_QUESTIONS.items())
    for start in range(0, len(question_items), 2):
        cols = st.columns(2, gap="small")
        for offset, col in enumerate(cols):
            if start + offset >= len(question_items):
                continue
            question_key, question = question_items[start + offset]
            options = list(dict(question.get("options") or {}).keys())
            labels = dict(question.get("options") or {})
            with col:
                answers[question_key] = st.selectbox(
                    str(question.get("label") or question_key),
                    options=options,
                    format_func=lambda option, labels=labels: labels.get(option, option),
                    index=options.index(question.get("default")) if question.get("default") in options else 0,
                    key=f"practical_validation_profile_answer_{question_key}",
                )
    profile = build_validation_profile(profile_id, answers)
    render_badge_strip(
        [
            {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
            {"label": "Rolling", "value": f"{dict(profile.get('thresholds') or {}).get('rolling_window_months')}M", "tone": "neutral"},
            {"label": "Cost", "value": f"{dict(profile.get('thresholds') or {}).get('one_way_cost_bps')} bps", "tone": "neutral"},
            {"label": "MDD Line", "value": dict(profile.get("thresholds") or {}).get("mdd_review_line"), "tone": "neutral"},
        ]
    )
    return {"profile_id": profile_id, "answers": answers}


def _replay_state_key(source: dict[str, Any], mode: str) -> str:
    return f"practical_validation_recheck_{source.get('selection_source_id') or 'source'}_{mode}"


def _render_actual_replay_panel(source: dict[str, Any]) -> dict[str, Any] | None:
    source_id = source.get("selection_source_id") or "source"
    mode = st.radio(
        "재검증 방식",
        options=list(RECHECK_MODE_LABELS.keys()),
        format_func=lambda value: RECHECK_MODE_LABELS.get(value, value),
        horizontal=True,
        key=f"practical_validation_recheck_mode_{source_id}",
    )
    recheck_plan = build_practical_validation_recheck_plan(source, mode=mode)
    replay_key = _replay_state_key(source, mode)
    replay_result = st.session_state.get(replay_key)
    render_badge_strip(
        [
            {"label": "Mode", "value": recheck_plan.get("mode_label") or "-", "tone": "neutral"},
            {"label": "Stored End", "value": dict(recheck_plan.get("stored_period") or {}).get("end") or "-", "tone": "neutral"},
            {"label": "Recheck End", "value": dict(recheck_plan.get("requested_period") or {}).get("end") or "-", "tone": "neutral"},
            {
                "label": "Extension",
                "value": f"{recheck_plan.get('extension_days', 0)} days",
                "tone": "neutral",
            },
        ]
    )
    if recheck_plan.get("latest_market_date_error"):
        st.warning(f"최신 DB 시장일 조회 실패: {recheck_plan.get('latest_market_date_error')}")
    elif mode == RECHECK_MODE_EXTEND_TO_LATEST:
        st.caption(
            f"DB 최신 시장일 `{recheck_plan.get('latest_market_date') or '-'}` 기준입니다. "
            f"{recheck_plan.get('status_reason') or ''}"
        )
    else:
        st.caption(str(recheck_plan.get("status_reason") or ""))
    st.caption(
        "이 버튼은 새 전략을 만들지 않고 기존 Backtest runtime으로 source를 재검증합니다. "
        "실패해도 저장 snapshot / DB price proxy 기반 진단은 계속 볼 수 있습니다."
    )
    if st.button("전략 재검증 실행", key=f"{replay_key}_run", width="stretch"):
        with st.spinner("기존 strategy runtime으로 Practical Validation source를 재검증 중입니다..."):
            replay_result = run_practical_validation_actual_replay(source, mode=mode)
        st.session_state[replay_key] = replay_result
        if replay_result.get("status") == "PASS":
            st.success("전략 재검증이 완료되었습니다.")
        elif replay_result.get("status") == "REVIEW":
            st.warning("전략 재검증은 완료되었지만 기간 coverage 또는 일부 component 확인이 필요합니다.")
        else:
            st.warning("전략 재검증이 일부 실패했습니다. 세부 결과를 확인하세요.")
    replay_result = st.session_state.get(replay_key)
    if isinstance(replay_result, dict) and replay_result:
        summary = dict(replay_result.get("summary") or {})
        period_coverage = dict(replay_result.get("period_coverage") or {})
        actual_period = dict(period_coverage.get("actual_period") or replay_result.get("actual_period") or {})
        render_badge_strip(
            [
                {
                    "label": "Recheck",
                    "value": replay_result.get("status") or "NOT_RUN",
                    "tone": _status_tone(replay_result.get("status")),
                },
                {"label": "Recheck ID", "value": replay_result.get("replay_id") or "-", "tone": "neutral"},
                {"label": "Elapsed", "value": f"{replay_result.get('elapsed_ms', 0)} ms", "tone": "neutral"},
                {"label": "CAGR", "value": summary.get("cagr") if summary else "-", "tone": "neutral"},
                {"label": "MDD", "value": summary.get("mdd") if summary else "-", "tone": "neutral"},
            ]
        )
        render_badge_strip(
            [
                {
                    "label": "Coverage",
                    "value": period_coverage.get("status") or "NOT_RUN",
                    "tone": _status_tone(period_coverage.get("status")),
                },
                {"label": "Actual End", "value": actual_period.get("end") or "-", "tone": "neutral"},
                {"label": "End Gap", "value": f"{period_coverage.get('end_gap_days', '-')} days", "tone": "neutral"},
                {"label": "Latest DB", "value": replay_result.get("latest_market_date") or "-", "tone": "neutral"},
            ]
        )
        if period_coverage.get("summary"):
            st.caption(str(period_coverage.get("summary")))
        component_rows = list(replay_result.get("component_results") or [])
        if component_rows:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Component": row.get("title"),
                            "Strategy": row.get("strategy_key"),
                            "Weight": row.get("target_weight"),
                            "Status": row.get("status"),
                            "Rows": row.get("result_rows"),
                            "Requested Start": row.get("requested_start"),
                            "Requested End": row.get("requested_end"),
                            "Start": row.get("actual_start"),
                            "End": row.get("actual_end"),
                            "Error": row.get("error"),
                        }
                        for row in component_rows
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        coverage_rows = list(period_coverage.get("component_rows") or [])
        if coverage_rows:
            st.dataframe(pd.DataFrame(coverage_rows), width="stretch", hide_index=True)
    return dict(replay_result) if isinstance(replay_result, dict) else None


def _status_tone(status: Any) -> str:
    status_text = str(status or "").upper()
    if status_text == "PASS":
        return "positive"
    if status_text == "BLOCKED":
        return "danger"
    if status_text == "REVIEW":
        return "warning"
    return "neutral"


def _render_validation_result(validation_result: dict[str, Any]) -> None:
    profile = dict(validation_result.get("validation_profile") or {})
    status_counts = dict(dict(validation_result.get("diagnostic_summary") or {}).get("status_counts") or {})
    render_readiness_route_panel(
        route_label=str(validation_result.get("validation_route") or "-"),
        score=float(validation_result.get("validation_score") or 0.0),
        blockers_count=len(validation_result.get("hard_blockers") or []),
        verdict=str(validation_result.get("verdict") or "-"),
        next_action=str(validation_result.get("next_action") or "-"),
        route_title="Practical Validation",
        score_title="Validation Score",
    )
    render_badge_strip(
        [
            {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
            {"label": "PASS", "value": status_counts.get("PASS", 0), "tone": "positive"},
            {"label": "REVIEW", "value": status_counts.get("REVIEW", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": status_counts.get("BLOCKED", 0), "tone": "danger"},
            {"label": "NOT_RUN", "value": status_counts.get("NOT_RUN", 0), "tone": "neutral"},
        ]
    )
    st.markdown("##### Input Evidence")
    st.dataframe(pd.DataFrame(validation_result.get("checks") or []), width="stretch", hide_index=True)
    st.markdown("##### Practical Diagnostics")
    diagnostic_rows = list(validation_result.get("diagnostic_display_rows") or [])
    if diagnostic_rows:
        st.dataframe(pd.DataFrame(diagnostic_rows), width="stretch", hide_index=True)
    else:
        st.info("표시할 diagnostic row가 없습니다.")

    provider_rows = list(validation_result.get("provider_coverage_display_rows") or [])
    if provider_rows:
        st.markdown("##### Provider Coverage")
        st.caption(
            "Ingestion에서 저장한 ETF provider / FRED snapshot이 Practical Diagnostics에 어떻게 연결됐는지 보여줍니다."
        )
        st.dataframe(pd.DataFrame(provider_rows), width="stretch", hide_index=True)

    mismatch_warnings = list(validation_result.get("intent_mismatch_warnings") or [])
    if mismatch_warnings:
        st.warning("사용자 프로필과 후보 특성이 충돌할 수 있습니다.")
        for warning in mismatch_warnings:
            st.caption(f"- {warning}")
    if validation_result.get("hard_blockers"):
        for blocker in list(validation_result.get("hard_blockers") or []):
            st.error(str(blocker))
    if validation_result.get("review_gaps"):
        for gap in list(validation_result.get("review_gaps") or []):
            st.warning(str(gap))
    not_run_critical = list(validation_result.get("not_run_critical_domains") or [])
    if not_run_critical:
        st.info("아래 NOT_RUN 항목은 Final Review에서 선택/보류/재검토 판단 근거로 확인해야 합니다.")
        st.dataframe(pd.DataFrame(not_run_critical), width="stretch", hide_index=True)
    curve_evidence = dict(validation_result.get("curve_evidence") or {})
    if curve_evidence:
        st.markdown("##### Curve / Recheck Evidence")
        render_badge_strip(
            [
                {"label": "Portfolio Curve", "value": curve_evidence.get("portfolio_curve_source") or "-", "tone": "positive" if curve_evidence.get("portfolio_curve_rows") else "warning"},
                {"label": "Rows", "value": curve_evidence.get("portfolio_curve_rows", 0), "tone": "neutral"},
                {"label": "Benchmark", "value": curve_evidence.get("benchmark_ticker") or "-", "tone": "neutral"},
                {"label": "Benchmark Rows", "value": curve_evidence.get("benchmark_curve_rows", 0), "tone": "neutral"},
            ]
        )
        component_curve_rows = list(curve_evidence.get("component_curve_rows") or [])
        if component_curve_rows:
            st.dataframe(pd.DataFrame(component_curve_rows), width="stretch", hide_index=True)
        benchmark_parity = dict(curve_evidence.get("benchmark_parity") or {})
        if benchmark_parity:
            render_badge_strip(
                [
                    {
                        "label": "Benchmark Parity",
                        "value": benchmark_parity.get("status") or "-",
                        "tone": _status_tone(benchmark_parity.get("status")),
                    },
                    {
                        "label": "Coverage",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("coverage_ratio", "-"),
                        "tone": "neutral",
                    },
                    {
                        "label": "Same Period",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("same_period", "-"),
                        "tone": "neutral",
                    },
                    {
                        "label": "Same Frequency",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("same_frequency", "-"),
                        "tone": "neutral",
                    },
                ]
            )
            parity_rows = list(benchmark_parity.get("rows") or [])
            if parity_rows:
                st.dataframe(pd.DataFrame(parity_rows), width="stretch", hide_index=True)
        curve_provenance = dict(curve_evidence.get("curve_provenance") or {})
        if curve_provenance:
            with st.expander("Curve provenance", expanded=False):
                st.json(curve_provenance)

    with st.expander("진단 세부 근거", expanded=False):
        for diagnostic in list(validation_result.get("diagnostic_results") or []):
            st.markdown(f"**{diagnostic.get('title')}**")
            render_badge_strip(
                [
                    {"label": "Status", "value": diagnostic.get("status") or "-", "tone": _status_tone(diagnostic.get("status"))},
                    {"label": "Metric", "value": diagnostic.get("key_metric") or "-", "tone": "neutral"},
                    {"label": "Origin", "value": diagnostic.get("origin") or "-", "tone": "neutral"},
                ]
            )
            st.caption(str(diagnostic.get("summary") or "-"))
            evidence_rows = list(diagnostic.get("evidence_rows") or [])
            if evidence_rows:
                st.dataframe(pd.DataFrame(evidence_rows), width="stretch", hide_index=True)
            limitations = list(diagnostic.get("limitations") or [])
            if limitations:
                st.caption("Limitations: " + " / ".join(str(item) for item in limitations))
    profile_score_rows = list(validation_result.get("profile_score_rows") or [])
    if profile_score_rows:
        with st.expander("Profile-aware score breakdown", expanded=False):
            st.dataframe(pd.DataFrame(profile_score_rows), width="stretch", hide_index=True)


def render_practical_validation_workspace() -> None:
    st.markdown("### Practical Validation")
    st.caption(
        "Backtest Analysis에서 선택한 후보를 실전 투입 전 관점으로 검증합니다. "
        "최종 사용자 메모와 최종 판단은 Final Review에서만 남깁니다."
    )

    sources = load_portfolio_selection_sources(limit=100)
    validation_rows = load_practical_validation_results(limit=100)
    session_source = st.session_state.get("backtest_practical_validation_source")
    notice = st.session_state.pop("backtest_practical_validation_notice", None)
    if notice:
        st.success(str(notice))

    render_status_card_grid(
        [
            {"title": "Selection Sources", "value": len(sources), "tone": "positive" if sources else "neutral"},
            {"title": "Validation Results", "value": len(validation_rows), "tone": "positive" if validation_rows else "neutral"},
            {"title": "Final Memo", "value": "Final Review Only", "tone": "neutral"},
            {"title": "Live Approval", "value": "Disabled", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        render_stage_brief(
            purpose="선택된 단일 전략, Compare 후보, 저장 Mix를 같은 Clean V2 source로 읽습니다.",
            result="Practical Validation result",
        )
        st.caption(f"Sources: `{PORTFOLIO_SELECTION_SOURCE_FILE}`")
        st.caption(f"Validation: `{PRACTICAL_VALIDATION_RESULT_FILE}`")

    selectable_sources: list[dict[str, Any]] = []
    if isinstance(session_source, dict) and session_source:
        selectable_sources.append(dict(session_source))
    existing_ids = {str(row.get("selection_source_id") or "") for row in selectable_sources}
    for row in sources:
        source_id = str(row.get("selection_source_id") or "")
        if source_id in existing_ids:
            continue
        selectable_sources.append(dict(row))

    if not selectable_sources:
        st.info("아직 Practical Validation으로 보낸 Clean V2 source가 없습니다.")
        st.caption("Backtest Analysis에서 Single / Compare / Saved Mix 결과를 선택하면 여기에 표시됩니다.")
        return

    labels = [_source_label(row) for row in selectable_sources]
    selected_label = st.selectbox("검증할 후보 source", options=labels, key="practical_validation_source_selected")
    source = selectable_sources[labels.index(selected_label)]

    st.markdown("#### 1. 선택 후보 확인")
    with st.container(border=True):
        _render_source_summary(source)

    st.markdown("#### 2. 검증 프로필")
    with st.container(border=True):
        validation_profile = _render_validation_profile_form()

    st.markdown("#### 3. 최신 데이터 기준 전략 재검증")
    with st.container(border=True):
        replay_result = _render_actual_replay_panel(source)

    validation_result = build_practical_validation_result(
        source,
        validation_profile=validation_profile,
        replay_result=replay_result,
    )
    st.markdown("#### 4. 실전 진단 보드")
    with st.container(border=True):
        _render_validation_result(validation_result)

    st.markdown("#### 5. 다음 단계")
    with st.container(border=True):
        st.info(
            "이 단계는 구조화된 검증 자료를 저장합니다. "
            "선정 / 보류 / 거절 / 재검토 판단과 최종 메모는 Final Review에서 기록합니다."
        )
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button("검증 결과 저장", key="practical_validation_save_result", width="stretch"):
                save_practical_validation_result(validation_result)
                st.success(f"검증 결과 `{validation_result['validation_id']}`를 저장했습니다.")
        with action_cols[1]:
            is_blocked = validation_result.get("validation_route") == "BLOCKED"
            if st.button(
                "Final Review로 이동",
                key="practical_validation_send_final_review",
                width="stretch",
                disabled=is_blocked,
            ):
                queue_final_review_source_from_validation(
                    source=source,
                    validation_result=validation_result,
                    persist_validation=True,
                )
                st.rerun()
            if is_blocked:
                st.caption("BLOCKED 상태는 Backtest Analysis에서 source를 보강한 뒤 Final Review로 보낼 수 있습니다.")

    with st.expander("Clean V2 Source JSON", expanded=False):
        st.json(source)
    with st.expander("Practical Validation Result JSON", expanded=False):
        st.json(validation_result)
