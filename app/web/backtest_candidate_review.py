from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from app.web.backtest_candidate_review_helpers import (
    CANDIDATE_REVIEW_DECISION_OPTIONS,
    CURRENT_CANDIDATE_RECORD_TYPE_OPTIONS,
    PRE_LIVE_STATUS_OPTIONS,
    _build_candidate_board_operating_evaluation,
    _build_candidate_intake_readiness_evaluation,
    _build_candidate_registry_scope_evaluation,
    _build_candidate_review_board_rows_for_display,
    _build_candidate_review_note_from_draft,
    _build_candidate_review_notes_rows_for_display,
    _build_current_candidate_registry_row_from_review_note,
    _build_current_candidate_registry_rows_for_display,
    _build_existing_review_note_registry_rows_for_display,
    _build_pre_live_draft_from_current_candidate,
    _build_pre_live_operating_readiness_evaluation,
    _build_pre_live_registry_rows_for_display,
    _candidate_review_decision_label,
    _candidate_review_draft_widget_key,
    _candidate_review_next_step,
    _candidate_review_note_existing_registry_rows,
    _candidate_review_note_to_registry_defaults,
    _candidate_review_note_widget_key,
    _candidate_review_reason,
    _candidate_review_stage,
    _current_candidate_record_type_label,
    _current_candidate_registry_contract_summary,
    _current_candidate_registry_selection_label,
    _default_candidate_review_decision_from_draft,
    _default_candidate_review_next_action,
    _default_candidate_review_operator_reason,
    _default_pre_live_next_action,
    _default_pre_live_operator_reason,
    _default_pre_live_status_from_current_candidate,
    _pre_live_status_korean_label,
    _pre_live_status_suggestion_reason,
)
from app.web.backtest_ui_components import (
    render_artifact_pipeline,
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
)
from app.web.runtime import (
    CANDIDATE_REVIEW_NOTES_FILE,
    CURRENT_CANDIDATE_REGISTRY_FILE,
    PRE_LIVE_CANDIDATE_REGISTRY_FILE,
    append_candidate_review_note as _append_candidate_review_note,
    append_current_candidate_registry_row as _append_current_candidate_registry_row,
    append_pre_live_candidate_registry_row as _append_pre_live_candidate_registry_row,
    load_candidate_review_notes as _load_candidate_review_notes,
    load_current_candidate_registry_latest as _load_current_candidate_registry_latest,
    load_pre_live_candidate_registry_latest as _load_pre_live_candidate_registry_latest,
)


def render_candidate_review_workspace() -> None:
    from app.web.pages import backtest as bt

    _queue_current_candidate_compare_prefill = bt._queue_current_candidate_compare_prefill
    _request_backtest_panel = bt._request_backtest_panel

    st.markdown("### Candidate Review")
    st.caption(
        "6단계 Candidate Packaging 작업 공간입니다. 백테스트 후보를 바로 투자 추천으로 확정하는 화면이 아니라, "
        "후보 초안 확인, Review Note 작성, registry row 저장, Pre-Live 운영 기록, Portfolio Proposal 이동 판단을 한 화면에서 정리합니다."
    )

    rows = _load_current_candidate_registry_latest()
    pre_live_rows = _load_pre_live_candidate_registry_latest()
    review_notes = _load_candidate_review_notes()
    candidate_draft = dict(st.session_state.get("backtest_candidate_review_draft") or {})

    summary_cols = st.columns(5, gap="small")
    summary_cols[0].metric("Active Candidates", len(rows))
    summary_cols[1].metric(
        "Current Anchors",
        len([row for row in rows if str(row.get("record_type") or "") == "current_candidate"]),
    )
    summary_cols[2].metric(
        "Near Miss / Scenario",
        len([row for row in rows if str(row.get("record_type") or "") != "current_candidate"]),
    )
    summary_cols[3].metric("Pre-Live Records", len(pre_live_rows))
    summary_cols[4].metric("Review Notes", len(review_notes))

    with st.container(border=True):
        st.markdown("#### Candidate Packaging 산출물 흐름")
        render_artifact_pipeline(
            [
                {
                    "title": "후보 초안",
                    "detail": "Backtest 결과를 후보로 검토할 준비",
                    "status": "준비됨" if candidate_draft else "대기",
                    "tone": "positive" if candidate_draft else "neutral",
                },
                {
                    "title": "Review Note",
                    "detail": "사람의 판단과 다음 행동 저장",
                    "status": f"{len(review_notes)}개 저장" if review_notes else "대기",
                    "tone": "positive" if review_notes else "neutral",
                },
                {
                    "title": "Current Candidate",
                    "detail": "후보 목록에서 다시 찾을 수 있는 record",
                    "status": f"{len(rows)}개 active" if rows else "대기",
                    "tone": "positive" if rows else "neutral",
                },
                {
                    "title": "Pre-Live Record",
                    "detail": "paper / watchlist / hold 운영 상태 저장",
                    "status": f"{len(pre_live_rows)}개 저장" if pre_live_rows else "대기",
                    "tone": "positive" if pre_live_rows else "neutral",
                },
                {
                    "title": "Proposal Ready",
                    "detail": "Portfolio Proposal로 넘길 수 있는지 판정",
                    "status": "3번에서 판정",
                    "tone": "warning" if rows else "neutral",
                },
            ]
        )

    with st.expander("How To Use Candidate Review", expanded=False):
        st.markdown(
            "- `Candidate Review`는 6단계 Candidate Packaging 작업 공간입니다.\n"
            "- 화면은 `1. Draft 확인`, `2. Registry 저장`, `3. 운영 기록 저장 및 Portfolio Proposal 이동` 순서로 진행합니다.\n"
            "- 각 버튼은 자동 처리 버튼이 아니라 사람이 확인한 뒤 다음 기록을 남기는 수동 저장 버튼입니다.\n"
            "- `Draft 확인`: 후보 검토 초안의 핵심 정보가 들어왔는지 확인한 뒤 Review Note를 저장합니다.\n"
            "- `Registry 저장`: 저장된 판단을 current / near miss / scenario 중 어디로 남길지 정하고 registry row로 저장합니다.\n"
            "- `운영 기록 저장 및 Portfolio Proposal 이동`: 저장된 후보를 실제 돈 없이 어떻게 추적할지 기록하고 다음 단계 가능 여부를 확인합니다.\n"
            "- 하단 보조 도구에서는 저장된 보드, note archive, raw candidate, compare 전송을 다시 확인할 수 있습니다.\n"
            "- 이 화면은 live trading 승인이나 최종 투자 판단을 하지 않습니다.\n"
            "- 후보 목록은 `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`의 active row 기준입니다."
        )

    if not rows:
        st.info("현재 current candidate registry에 active 후보가 없습니다.")
        st.caption(f"Path: {CURRENT_CANDIDATE_REGISTRY_FILE}")

    note_notice = st.session_state.get("backtest_candidate_review_note_notice")
    if note_notice:
        st.success(note_notice)
        st.session_state.backtest_candidate_review_note_notice = None

    st.divider()
    st.markdown("#### 1. Draft 확인 / Review Note 저장")
    with st.container(border=True):
        render_stage_brief(
            purpose="백테스트 실행 결과를 바로 후보로 확정하지 않고, 먼저 검토 메모로 고정합니다.",
            result="Candidate Review Note",
        )
        draft_notice = st.session_state.get("backtest_candidate_review_draft_notice")
        if draft_notice:
            st.info(draft_notice)
            st.session_state.backtest_candidate_review_draft_notice = None
        draft = candidate_draft
        if not draft:
            st.info(
                "아직 후보 검토 초안이 없습니다. "
                "`Latest Backtest Run` 또는 `Operations > Backtest Run History > Selected History Run`에서 `Review As Candidate Draft`를 누르면 여기에 표시됩니다."
            )
        else:
            result_snapshot = dict(draft.get("result_snapshot") or {})
            signal = dict(draft.get("real_money_signal") or {})
            data_trust = dict(draft.get("data_trust_snapshot") or {})
            st.markdown(f"##### {draft.get('strategy_name') or draft.get('strategy_key') or 'Candidate Review Draft'}")
            st.caption(
                "`Suggested Record Type`은 자동 등록값이 아니라 사람이 검토할 때 참고하는 초안 분류입니다."
            )
            draft_metric_cols = st.columns(5, gap="small")
            draft_metric_cols[0].metric("Suggested Type", str(draft.get("suggested_record_type_label") or "-"))
            draft_metric_cols[1].metric("CAGR", str(result_snapshot.get("cagr") or "-"))
            draft_metric_cols[2].metric("MDD", str(result_snapshot.get("maximum_drawdown") or "-"))
            draft_metric_cols[3].metric("Promotion", str(signal.get("promotion") or "-"))
            draft_metric_cols[4].metric("Shortlist", str(signal.get("shortlist") or "-"))
            st.markdown("**Suggested Next Step**")
            st.write(draft.get("suggested_next_step") or "-")
            st.markdown("**Data Trust Snapshot**")
            st.dataframe(pd.DataFrame([data_trust]), use_container_width=True, hide_index=True)
            with st.expander("Candidate Review Draft JSON", expanded=False):
                st.json(draft)
            st.markdown("#### Save As Candidate Review Note")
            st.caption(
                "여기서 저장하는 것은 current candidate 등록이 아닙니다. "
                "초안을 본 뒤 사람이 남기는 검토 판단과 다음 행동 메모입니다."
            )
            draft_key = _candidate_review_draft_widget_key(draft)
            default_decision = _default_candidate_review_decision_from_draft(draft)
            decision = st.selectbox(
                "Review Decision",
                options=CANDIDATE_REVIEW_DECISION_OPTIONS,
                index=(
                    CANDIDATE_REVIEW_DECISION_OPTIONS.index(default_decision)
                    if default_decision in CANDIDATE_REVIEW_DECISION_OPTIONS
                    else 0
                ),
                format_func=_candidate_review_decision_label,
                key=f"candidate_review_decision_{draft_key}",
                help="이 초안을 어떤 검토 상태로 남길지 고릅니다. 이 값은 투자 승인이나 registry 자동 등록이 아닙니다.",
            )
            operator_reason = st.text_area(
                "Operator Reason",
                value=_default_candidate_review_operator_reason(draft, decision),
                key=f"candidate_review_operator_reason_{draft_key}_{decision}",
                help="왜 이 판단을 했는지 다음에 읽는 사람이 이해할 수 있게 남깁니다.",
            )
            next_action = st.text_area(
                "Next Action",
                value=_default_candidate_review_next_action(decision),
                key=f"candidate_review_next_action_{draft_key}_{decision}",
                help="다음에 무엇을 확인하거나 실행할지 남깁니다.",
            )
            default_use_review_date = decision in {"needs_more_evidence", "consider_registry_candidate"}
            use_review_date = st.checkbox(
                "Review Date 지정",
                value=default_use_review_date,
                key=f"candidate_review_use_review_date_{draft_key}_{decision}",
                help="다음 재검토 날짜가 필요하면 켭니다.",
            )
            review_date_value: date | None = None
            if use_review_date:
                review_date_value = st.date_input(
                    "Review Date",
                    value=date.today() + timedelta(days=14),
                    key=f"candidate_review_review_date_{draft_key}_{decision}",
                )
            intake_readiness = _build_candidate_intake_readiness_evaluation(
                draft,
                operator_reason=operator_reason,
                next_action=next_action,
            )
            with st.container(border=True):
                st.markdown("##### Candidate Packaging 저장 준비")
                st.caption(
                    "이 박스는 전략 품질 점수가 아니라, Candidate Draft가 Review Note로 저장될 만큼 "
                    "필수 정보와 운영자 판단을 갖췄는지 보는 체크입니다."
                )
                readiness_cols = st.columns([0.22, 0.18, 0.2, 0.4], gap="small")
                readiness_cols[0].metric(
                    "Intake Status",
                    "READY_TO_SAVE" if intake_readiness["ready"] else "NEEDS_FIX",
                )
                readiness_cols[1].metric("Completeness", f"{float(intake_readiness['score']):.1f} / 10")
                readiness_cols[2].metric("Blockers", len(intake_readiness["blocking_reasons"]))
                with readiness_cols[3]:
                    st.caption("판정")
                    st.markdown(f"**{intake_readiness['verdict']}**")
                    st.caption("다음 행동")
                    st.markdown(str(intake_readiness["next_action"]))
                st.progress(max(0.0, min(float(intake_readiness["score"]) / 10.0, 1.0)))
                st.dataframe(pd.DataFrame(intake_readiness["criteria_rows"]), use_container_width=True, hide_index=True)
                if intake_readiness["ready"]:
                    st.success("Draft 확인과 운영자 메모가 저장 가능한 상태입니다.")
                else:
                    st.error("저장 전 먼저 채울 항목: " + ", ".join(str(item) for item in intake_readiness["blocking_reasons"]))
                if intake_readiness["warning_reasons"]:
                    st.warning("Review Note에 함께 남길 주의 항목: " + ", ".join(str(item) for item in intake_readiness["warning_reasons"]))
            review_note = _build_candidate_review_note_from_draft(
                draft,
                review_decision=decision,
                operator_reason=operator_reason,
                next_action=next_action,
                review_date_value=review_date_value,
            )
            with st.expander("Candidate Review Note JSON Preview", expanded=False):
                st.json(review_note)
            if st.button(
                "Save Candidate Review Note",
                key=f"save_candidate_review_note_{draft_key}",
                disabled=not bool(intake_readiness["ready"]),
                use_container_width=True,
            ):
                _append_candidate_review_note(review_note)
                st.session_state.backtest_candidate_review_note_notice = (
                    f"Candidate Review Note `{review_note['review_note_id']}`를 저장했습니다. "
                    "다음은 같은 Candidate Packaging 안에서 registry에 남길 범위를 정하는 작업입니다."
                )
                st.rerun()
            if st.button("Clear Candidate Draft", key="clear_candidate_review_draft", use_container_width=True):
                st.session_state.backtest_candidate_review_draft = None
                st.rerun()

    st.divider()
    st.markdown("#### 2. Registry 저장")
    with st.container(border=True):
        render_stage_brief(
            purpose="Review Note를 실제 후보 목록에서 다시 찾을 수 있는 registry row로 바꿉니다.",
            result="Current Candidate Registry Row",
        )
        if not review_notes:
            st.info("아직 저장된 Candidate Review Note가 없습니다. 먼저 위 1번에서 Review Note를 저장하세요.")
        else:
            note_labels = [
                f"{row.get('recorded_at')} | {_candidate_review_decision_label(str(row.get('review_decision') or ''))} | {row.get('strategy_name') or row.get('strategy_key') or row.get('review_note_id')}"
                for row in review_notes
            ]
            selected_note_label = st.selectbox(
                "Registry로 보낼 Review Note",
                options=note_labels,
                key="candidate_review_note_to_inspect",
                help="보통 가장 최근에 저장한 Review Note를 선택합니다.",
            )
            selected_note = review_notes[note_labels.index(selected_note_label)]
            with st.expander("Selected Review Note JSON", expanded=False):
                st.json(selected_note)
            with st.expander("Review Notes Archive", expanded=False):
                st.dataframe(_build_candidate_review_notes_rows_for_display(review_notes), use_container_width=True, hide_index=True)
            review_decision = str(selected_note.get("review_decision") or "")
            if review_decision == "reject_for_now":
                st.warning(
                    "`Reject For Now` review note는 보통 current candidate registry에 올리지 않습니다. "
                    "후보로 다시 볼 근거가 생긴 뒤 새 review note를 만드는 편이 안전합니다."
                )
            registry_defaults = _candidate_review_note_to_registry_defaults(selected_note)
            registry_scope = _build_candidate_registry_scope_evaluation(selected_note)
            registry_key = _candidate_review_note_widget_key(selected_note)
            with st.container(border=True):
                st.markdown("##### 저장 범위 판단")
                render_readiness_route_panel(
                    route_label=str(registry_scope["scope_label"]),
                    score=float(registry_scope["score"]),
                    blockers_count=len(registry_scope["blocking_reasons"]),
                    verdict=str(registry_scope["verdict"]),
                    next_action=str(registry_scope["next_action"]),
                    route_title="Scope",
                    score_title="Scope Score",
                )
                render_badge_strip(
                    [
                        {
                            "label": "Recommended",
                            "value": str(registry_scope["recommended_record_type_label"]),
                            "tone": "positive" if registry_scope["can_prepare_registry_row"] else "warning",
                        },
                        {
                            "label": "Allowed",
                            "value": ", ".join(str(item) for item in registry_scope.get("allowed_record_types") or []) or "-",
                            "tone": "neutral",
                        },
                        {
                            "label": "Decision",
                            "value": _candidate_review_decision_label(review_decision),
                            "tone": "neutral",
                        },
                    ]
                )
                st.progress(max(0.0, min(float(registry_scope["score"]) / 10.0, 1.0)))
                with st.expander("저장 범위 판단 기준 보기", expanded=False):
                    st.dataframe(pd.DataFrame(registry_scope["criteria_rows"]), use_container_width=True, hide_index=True)
                if registry_scope["can_prepare_registry_row"]:
                    st.success("이 Review Note는 표시된 범위 안에서 registry row preview로 넘길 수 있습니다.")
                else:
                    st.error("registry 저장 전 멈출 항목: " + ", ".join(str(item) for item in registry_scope["blocking_reasons"]))
                if registry_scope["warning_reasons"]:
                    st.warning("Registry notes에 함께 남길 주의 항목: " + ", ".join(str(item) for item in registry_scope["warning_reasons"]))
            existing_review_note_registry_rows = _candidate_review_note_existing_registry_rows(selected_note)
            if existing_review_note_registry_rows:
                st.success(
                    "이 Review Note는 이미 Current Candidate Registry에 저장되어 있습니다. "
                    "Saved Candidate Board에는 같은 Registry ID의 최신 revision만 보이기 때문에 반복 클릭 후에도 변화가 작게 보일 수 있습니다."
                )
                with st.expander("기존 registry 저장 기록 보기", expanded=False):
                    st.dataframe(
                        _build_existing_review_note_registry_rows_for_display(existing_review_note_registry_rows),
                        use_container_width=True,
                        hide_index=True,
                    )
                allow_registry_revision_append = st.checkbox(
                    "같은 Review Note를 새 registry revision으로 다시 저장",
                    value=False,
                    key=f"candidate_registry_allow_revision_append_{registry_key}",
                    help="의도적으로 같은 Review Note를 append-only registry에 새 revision으로 남길 때만 켭니다.",
                )
            else:
                allow_registry_revision_append = True
            existing_registry_ids = {str(row.get("registry_id") or "") for row in _load_current_candidate_registry_latest()}
            st.markdown("##### 저장될 후보 Row")
            st.caption("대부분은 기본값 그대로 저장하면 됩니다. 화면에서 다시 찾을 이름과 후보 범위만 먼저 확인하세요.")
            registry_id = st.text_input(
                "Registry ID",
                value=registry_defaults["registry_id"],
                key=f"candidate_registry_draft_id_{registry_key}",
                help="append-only registry에서 이 후보를 다시 찾을 때 쓰는 ID입니다. 기존 ID를 쓰면 새 revision처럼 기록됩니다.",
            )
            if registry_id in existing_registry_ids:
                st.warning(
                    "같은 Registry ID가 이미 active 후보에 있습니다. "
                    "저장하면 append-only 방식으로 새 row가 추가되고 latest view에서는 더 최근 row가 보입니다."
                )
            row_core_cols = st.columns([0.36, 0.64], gap="small")
            with row_core_cols[0]:
                record_type = st.selectbox(
                    "Record Type",
                    options=CURRENT_CANDIDATE_RECORD_TYPE_OPTIONS,
                    index=CURRENT_CANDIDATE_RECORD_TYPE_OPTIONS.index(
                        str(registry_scope.get("recommended_record_type") or registry_defaults["record_type"])
                        if str(registry_scope.get("recommended_record_type") or registry_defaults["record_type"])
                        in CURRENT_CANDIDATE_RECORD_TYPE_OPTIONS
                        else registry_defaults["record_type"]
                    ),
                    format_func=_current_candidate_record_type_label,
                    key=f"candidate_registry_draft_record_type_{registry_key}",
                    help="current anchor인지, near-miss 대안인지, scenario 비교 후보인지 고릅니다.",
                )
            with row_core_cols[1]:
                title = st.text_input(
                    "Candidate Title",
                    value=registry_defaults["title"],
                    key=f"candidate_registry_draft_title_{registry_key}",
                )
            allowed_record_types = set(registry_scope.get("allowed_record_types") or [])
            if allowed_record_types and record_type not in allowed_record_types:
                st.error(
                    "선택한 Record Type이 registry 범위 판단과 맞지 않습니다. "
                    "권장 범위로 바꾸거나 Review Note를 다시 확인하세요."
                )
            with st.expander("고급 식별값 수정", expanded=False):
                st.caption("후보가 여러 개라 이름이 헷갈릴 때만 수정합니다. 보통은 자동 생성값을 그대로 둡니다.")
                input_cols = st.columns(3, gap="small")
                with input_cols[0]:
                    strategy_family = st.text_input(
                        "Strategy Family",
                        value=registry_defaults["strategy_family"],
                        key=f"candidate_registry_draft_family_{registry_key}",
                    )
                with input_cols[1]:
                    strategy_name = st.text_input(
                        "Strategy Name",
                        value=registry_defaults["strategy_name"],
                        key=f"candidate_registry_draft_strategy_{registry_key}",
                    )
                with input_cols[2]:
                    candidate_role = st.text_input(
                        "Candidate Role",
                        value=registry_defaults["candidate_role"],
                        key=f"candidate_registry_draft_role_{registry_key}",
                    )
            registry_note_text = st.text_area(
                "Registry Notes",
                value=registry_defaults["notes"],
                key=f"candidate_registry_draft_notes_{registry_key}",
                help="왜 이 review note를 후보 registry에 남기는지 설명합니다.",
            )
            registry_row = _build_current_candidate_registry_row_from_review_note(
                selected_note,
                registry_id=registry_id,
                record_type=record_type,
                strategy_family=strategy_family,
                strategy_name=strategy_name,
                candidate_role=candidate_role,
                title=title,
                notes=registry_note_text,
            )
            with st.expander("Current Candidate Registry Row JSON Preview", expanded=False):
                st.json(registry_row)
            packaging_candidate_label = _current_candidate_registry_selection_label(registry_row)
            st.markdown("##### 다음 단계에서 찾을 이름")
            st.code(packaging_candidate_label, language="text")
            st.caption(
                "`Append To Current Candidate Registry`를 누르면 "
                "`3. 운영 기록 저장 및 Portfolio Proposal 이동 > Packaging 확인 후보`에서 이 이름으로 자동 선택됩니다."
            )
            save_disabled = (
                not bool(registry_scope["can_prepare_registry_row"])
                or review_decision == "reject_for_now"
                or (bool(allowed_record_types) and record_type not in allowed_record_types)
                or not str(registry_id).strip()
                or not str(strategy_family).strip()
                or not str(strategy_name).strip()
                or not str(candidate_role).strip()
                or (bool(existing_review_note_registry_rows) and not bool(allow_registry_revision_append))
            )
            if save_disabled and review_decision != "reject_for_now":
                if not bool(registry_scope["can_prepare_registry_row"]):
                    st.error("Registry 범위 판단이 통과되어야 append를 진행할 수 있습니다.")
                elif bool(allowed_record_types) and record_type not in allowed_record_types:
                    st.error("허용된 Record Type 범위 안에서만 append할 수 있습니다.")
                elif bool(existing_review_note_registry_rows) and not bool(allow_registry_revision_append):
                    st.info(
                        "이미 저장된 Review Note입니다. 같은 판단을 새 revision으로 다시 남길 이유가 있을 때만 "
                        "위 체크박스를 켠 뒤 저장하세요."
                    )
                else:
                    st.error("Registry ID, Strategy Family, Strategy Name, Candidate Role은 필수입니다.")
            if st.button(
                "Append To Current Candidate Registry",
                key=f"append_candidate_registry_row_{registry_key}",
                disabled=save_disabled,
                use_container_width=True,
            ):
                _append_current_candidate_registry_row(registry_row)
                registry_label = _current_candidate_registry_selection_label(registry_row)
                st.session_state["candidate_packaging_recent_registry_id"] = registry_row["registry_id"]
                st.session_state["candidate_packaging_recent_revision_id"] = registry_row["revision_id"]
                st.session_state["candidate_packaging_recent_label"] = registry_label
                st.session_state["candidate_packaging_focus_recent_registry_id"] = registry_row["registry_id"]
                st.session_state["candidate_packaging_focus_recent_revision_id"] = registry_row["revision_id"]
                st.session_state.backtest_candidate_review_note_notice = (
                    f"Current Candidate Registry row `{registry_row['registry_id']}`를 append했습니다. "
                    "이 기록도 투자 승인이나 live trading 승인은 아닙니다. "
                    "아래 `3. 운영 기록 저장 및 Portfolio Proposal 이동`에서 방금 저장한 후보를 자동 선택했습니다."
                )
                st.rerun()

    st.divider()
    st.markdown("#### 3. 운영 기록 저장 및 Portfolio Proposal 이동")
    with st.container(border=True):
        render_stage_brief(
            purpose="후보를 바로 포트폴리오로 보내지 않고, 실제 돈 없이 어떻게 추적할지 먼저 정합니다.",
            result="Pre-Live Record 저장 / Proposal 이동",
        )
        if not rows:
            st.info("현재 평가할 active current candidate가 없습니다. 먼저 위 2번에서 Registry에 저장하세요.")
        else:
            board_label_to_row = {_current_candidate_registry_selection_label(row): row for row in rows}
            focus_registry_id = str(st.session_state.get("candidate_packaging_focus_recent_registry_id") or "").strip()
            focus_revision_id = str(st.session_state.get("candidate_packaging_focus_recent_revision_id") or "").strip()
            recent_registry_id = str(st.session_state.get("candidate_packaging_recent_registry_id") or "").strip()
            recent_revision_id = str(st.session_state.get("candidate_packaging_recent_revision_id") or "").strip()
            recent_label = ""
            focus_label = ""
            for candidate_label, candidate_row in board_label_to_row.items():
                row_registry_id = str(candidate_row.get("registry_id") or "").strip()
                row_revision_id = str(candidate_row.get("revision_id") or "").strip()
                if recent_registry_id and row_registry_id == recent_registry_id and (
                    not recent_revision_id or row_revision_id == recent_revision_id
                ):
                    recent_label = candidate_label
                if focus_registry_id and row_registry_id == focus_registry_id and (
                    not focus_revision_id or row_revision_id == focus_revision_id
                ):
                    focus_label = candidate_label
            if focus_label:
                st.session_state["candidate_board_step8_candidate"] = focus_label
                st.session_state["candidate_packaging_focus_recent_registry_id"] = None
                st.session_state["candidate_packaging_focus_recent_revision_id"] = None
            current_board_selection = st.session_state.get("candidate_board_step8_candidate")
            if current_board_selection not in board_label_to_row:
                st.session_state["candidate_board_step8_candidate"] = (
                    focus_label or recent_label or next(iter(board_label_to_row.keys()))
                )
            selected_board_label = st.selectbox(
                "Packaging 확인 후보",
                options=list(board_label_to_row.keys()),
                key="candidate_board_step8_candidate",
                help="Candidate Packaging에서 다음 운영 경로를 판단할 후보를 고릅니다.",
            )
            selected_board_row = board_label_to_row[selected_board_label]
            selected_registry_id = str(selected_board_row.get("registry_id") or "").strip()
            selected_revision_id = str(selected_board_row.get("revision_id") or "").strip()
            if recent_label and selected_registry_id == recent_registry_id and (
                not recent_revision_id or selected_revision_id == recent_revision_id
            ):
                st.success(f"방금 `2. Registry 저장`에서 append한 후보가 선택되어 있습니다: `{selected_board_label}`")
                with st.expander("방금 저장한 후보 식별값 보기", expanded=False):
                    st.dataframe(
                        pd.DataFrame(
                            [
                                {
                                    "Registry ID": selected_board_row.get("registry_id"),
                                    "Revision ID": selected_board_row.get("revision_id"),
                                    "Record Type": selected_board_row.get("record_type"),
                                    "Strategy Family": selected_board_row.get("strategy_family"),
                                    "Strategy Name": selected_board_row.get("strategy_name"),
                                    "Title": selected_board_row.get("title"),
                                    "Source Review Note": selected_board_row.get("source_review_note_id"),
                                    "Recorded At": selected_board_row.get("recorded_at"),
                                }
                            ]
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
            selected_result = dict(selected_board_row.get("result") or {})
            board_evaluation = _build_candidate_board_operating_evaluation(selected_board_row)
            candidate_route_tone = (
                "positive"
                if board_evaluation["can_move_to_pre_live"]
                else "warning"
                if board_evaluation["can_move_to_compare"]
                else "danger"
            )
            with st.container(border=True):
                st.markdown("##### 선택 후보 확인")
                render_badge_strip(
                    [
                        {"label": "Route", "value": str(board_evaluation["route_label"]), "tone": candidate_route_tone},
                        {
                            "label": "Record Type",
                            "value": str(selected_board_row.get("record_type") or "-"),
                            "tone": "neutral",
                        },
                        {"label": "Promotion", "value": str(selected_result.get("promotion") or "-"), "tone": "neutral"},
                        {"label": "Deployment", "value": str(selected_result.get("deployment") or "-"), "tone": "neutral"},
                    ]
                )
                if board_evaluation["can_move_to_pre_live"]:
                    st.success("이 후보는 운영 기록을 저장할 수 있는 current candidate입니다.")
                elif board_evaluation["can_move_to_compare"]:
                    st.info("이 후보는 운영 기록보다 Compare 재검토가 먼저인 후보입니다.")
                else:
                    st.error("운영 기록으로 넘기기 전 확인 필요: " + ", ".join(str(item) for item in board_evaluation["blocking_reasons"]))
                if board_evaluation["warning_reasons"]:
                    st.warning("주의 항목: " + ", ".join(str(item) for item in board_evaluation["warning_reasons"]))
                with st.expander("선택 후보 확인 기준 보기", expanded=False):
                    st.dataframe(pd.DataFrame(board_evaluation["criteria_rows"]), use_container_width=True, hide_index=True)

            if board_evaluation["can_move_to_pre_live"]:
                st.markdown("##### 운영 기록 저장 및 다음 단계 판단")
                default_status = _default_pre_live_status_from_current_candidate(selected_board_row)
                existing_pre_live_rows = [
                    row
                    for row in pre_live_rows
                    if str(row.get("source_candidate_registry_id") or "").strip() == selected_registry_id
                    and str(row.get("record_status") or "active").strip().lower() == "active"
                ]
                latest_existing_pre_live = existing_pre_live_rows[0] if existing_pre_live_rows else None
                if latest_existing_pre_live:
                    st.info(
                        "이미 이 candidate에 연결된 active Pre-Live 운영 기록이 있습니다. "
                        "다시 저장하면 append-only 방식으로 새 revision이 추가되고 latest view에서는 새 기록이 보입니다."
                    )
                render_badge_strip(
                    [
                        {"label": "Promotion", "value": str(selected_result.get("promotion") or "-"), "tone": "positive"},
                        {"label": "Shortlist", "value": str(selected_result.get("shortlist") or "-"), "tone": "neutral"},
                        {"label": "Deployment", "value": str(selected_result.get("deployment") or "-"), "tone": "warning"},
                        {
                            "label": "Suggested",
                            "value": _pre_live_status_korean_label(default_status),
                            "tone": "positive" if default_status == "paper_tracking" else "neutral",
                        },
                    ]
                )
                with st.expander("운영 상태 추천 근거 보기", expanded=False):
                    st.info(_pre_live_status_suggestion_reason(selected_board_row, default_status))
                pre_live_key = f"{selected_registry_id}_{selected_revision_id}"
                selected_status = st.selectbox(
                    "Operator Final Status",
                    options=PRE_LIVE_STATUS_OPTIONS,
                    index=PRE_LIVE_STATUS_OPTIONS.index(default_status) if default_status in PRE_LIVE_STATUS_OPTIONS else 0,
                    format_func=_pre_live_status_korean_label,
                    key=f"candidate_review_pre_live_status_{pre_live_key}",
                    help="이 값이 Pre-Live registry에 저장됩니다. 투자 승인 상태가 아니라 실전 전 운영 상태입니다.",
                )
                if selected_status != default_status:
                    st.warning(
                        "Operator Final Status가 System Suggested Status와 다릅니다. "
                        "의도적으로 다른 결정을 내리는 경우 Operator Reason에 근거를 남겨주세요."
                    )
                operator_reason = st.text_area(
                    "Operator Reason",
                    value=_default_pre_live_operator_reason(selected_board_row, selected_status),
                    key=f"candidate_review_pre_live_reason_{pre_live_key}_{selected_status}",
                    help="왜 이 후보를 이 상태로 두는지 사람이 읽을 수 있게 남깁니다.",
                )
                next_action = st.text_area(
                    "Next Action",
                    value=_default_pre_live_next_action(selected_status),
                    key=f"candidate_review_pre_live_next_action_{pre_live_key}_{selected_status}",
                    help="다음에 무엇을 확인하거나 실행할지 남깁니다.",
                )
                default_use_review_date = selected_status in {"paper_tracking", "re_review"}
                use_review_date = st.checkbox(
                    "Review Date 지정",
                    value=default_use_review_date,
                    key=f"candidate_review_pre_live_use_review_date_{pre_live_key}_{selected_status}",
                    help="paper tracking과 re-review는 다음 점검일을 두는 것이 안전합니다.",
                )
                review_date_value: date | None = None
                if use_review_date or selected_status in {"paper_tracking", "re_review"}:
                    review_date_value = st.date_input(
                        "Review Date",
                        value=date.today() + timedelta(days=30),
                        key=f"candidate_review_pre_live_review_date_{pre_live_key}_{selected_status}",
                    )

                pre_live_draft = _build_pre_live_draft_from_current_candidate(
                    selected_board_row,
                    pre_live_status=selected_status,
                    operator_reason=operator_reason,
                    next_action=next_action,
                    review_date_value=review_date_value,
                )
                pre_live_readiness = _build_pre_live_operating_readiness_evaluation(
                    selected_board_row,
                    pre_live_status=selected_status,
                    operator_reason=operator_reason,
                    next_action=next_action,
                    review_date_value=review_date_value,
                )
                next_route_tone = (
                    "positive"
                    if pre_live_readiness["can_move_to_portfolio_proposal"]
                    else "warning"
                    if pre_live_readiness["can_save_record"]
                    else "danger"
                )
                render_badge_strip(
                    [
                        {
                            "label": "Save Record",
                            "value": "가능" if pre_live_readiness["can_save_record"] else "확인 필요",
                            "tone": "positive" if pre_live_readiness["can_save_record"] else "danger",
                        },
                        {"label": "Next Route", "value": str(pre_live_readiness["route_label"]), "tone": next_route_tone},
                        {
                            "label": "Proposal",
                            "value": "저장 후 이동 가능"
                            if pre_live_readiness["can_move_to_portfolio_proposal"]
                            else "직행 아님",
                            "tone": "positive"
                            if pre_live_readiness["can_move_to_portfolio_proposal"]
                            else "warning",
                        },
                        {
                            "label": "Blockers",
                            "value": str(len(pre_live_readiness["blocking_reasons"])),
                            "tone": "positive" if not pre_live_readiness["blocking_reasons"] else "danger",
                        },
                    ]
                )
                if pre_live_readiness["can_move_to_portfolio_proposal"]:
                    st.success("이 운영 기록을 저장하면 Portfolio Proposal로 이동할 수 있습니다.")
                elif pre_live_readiness["can_save_record"]:
                    st.info("Pre-Live 기록 저장은 가능하지만, 현재 상태는 Portfolio Proposal 직행 경로가 아닙니다.")
                else:
                    st.error("저장 전 확인 필요: " + ", ".join(str(item) for item in pre_live_readiness["blocking_reasons"]))
                if pre_live_readiness["warning_reasons"]:
                    st.warning("주의 항목: " + ", ".join(str(item) for item in pre_live_readiness["warning_reasons"]))
                with st.expander("운영 기록 / 다음 단계 판단 기준 보기", expanded=False):
                    st.dataframe(pd.DataFrame(pre_live_readiness["criteria_rows"]), use_container_width=True, hide_index=True)
                with st.expander("Pre-Live Record JSON Preview", expanded=False):
                    st.json(pre_live_draft)

                matching_saved_record = bool(
                    latest_existing_pre_live
                    and str(latest_existing_pre_live.get("pre_live_status") or "") == selected_status
                )
                action_cols = st.columns([0.28, 0.28, 0.44], gap="small")
                with action_cols[0]:
                    if st.button(
                        "Save Pre-Live Record",
                        key=f"candidate_review_save_pre_live_record_{pre_live_key}",
                        disabled=not bool(pre_live_readiness["can_save_record"]),
                        use_container_width=True,
                    ):
                        _append_pre_live_candidate_registry_row(pre_live_draft)
                        st.session_state["pre_live_recent_record_id"] = pre_live_draft["pre_live_id"]
                        st.session_state["pre_live_recent_revision_id"] = pre_live_draft["revision_id"]
                        st.success(f"Pre-Live 기록 `{pre_live_draft['pre_live_id']}`를 저장했습니다.")
                        st.rerun()
                with action_cols[1]:
                    proposal_disabled = not bool(pre_live_readiness["can_move_to_portfolio_proposal"]) or not matching_saved_record
                    if st.button(
                        "Open Portfolio Proposal",
                        key=f"candidate_review_open_portfolio_proposal_{pre_live_key}",
                        disabled=proposal_disabled,
                        use_container_width=True,
                        help="paper_tracking 상태의 저장된 Pre-Live record가 있을 때 Portfolio Proposal로 이동합니다.",
                    ):
                        st.session_state["portfolio_proposal_component_selection"] = [selected_board_label]
                        st.session_state["portfolio_proposal_from_pre_live_notice"] = (
                            f"`{selected_board_row.get('title') or selected_registry_id}` 후보를 Candidate Review에서 Portfolio Proposal로 열었습니다."
                        )
                        _request_backtest_panel("Portfolio Proposal")
                        st.rerun()
                with action_cols[2]:
                    st.caption(
                        "`Open Portfolio Proposal`은 같은 후보의 현재 선택 상태가 저장된 Pre-Live record와 맞을 때 활성화됩니다. "
                        "저장해도 live trading이 열리는 것은 아닙니다."
                    )

            if board_evaluation["can_move_to_compare"]:
                if st.button(
                    "Open Compare Picker For Selected Candidate",
                    key="candidate_board_open_compare_picker",
                    disabled=not bool(board_evaluation["can_move_to_compare"]),
                    use_container_width=True,
                ):
                    st.session_state["current_candidate_bundle_selection"] = [selected_board_label]
                    st.session_state.backtest_compare_prefill_notice = (
                        f"`{selected_board_row.get('title') or selected_board_row.get('registry_id')}` 후보를 "
                        "Compare 후보 선택 목록에 표시했습니다. Compare 실행 전 비교할 후보를 하나 이상 더 고르세요."
                    )
                    _request_backtest_panel("Compare & Portfolio Builder")
                    st.rerun()

            with st.expander("Selected Candidate Detail", expanded=False):
                selected_result = dict(selected_board_row.get("result") or {})
                st.markdown(f"##### {selected_board_row.get('title') or selected_board_row.get('registry_id')}")
                st.caption(_candidate_review_reason(selected_board_row))
                metric_cols = st.columns(5, gap="small")
                metric_cols[0].metric("Review Stage", _candidate_review_stage(selected_board_row))
                metric_cols[1].metric("CAGR", str(selected_result.get("cagr") or "-"))
                metric_cols[2].metric("MDD", str(selected_result.get("mdd") or "-"))
                metric_cols[3].metric("Promotion", str(selected_result.get("promotion") or "-"))
                metric_cols[4].metric("Shortlist", str(selected_result.get("shortlist") or "-"))
                st.markdown("**Suggested Next Step**")
                st.write(_candidate_review_next_step(selected_board_row))
                st.markdown("**Contract Summary**")
                st.write(_current_candidate_registry_contract_summary(selected_board_row))
                st.markdown("**Raw Candidate Registry Row**")
                st.json(selected_board_row)

    st.divider()
    with st.expander("보조 도구: Saved Candidate Board", expanded=False):
        st.caption(
            "현재 registry에 저장된 후보 보드입니다. 성과 순위표가 아니라 후보 역할과 다음 작업을 확인하는 보조 표입니다."
        )
        if rows:
            st.dataframe(_build_candidate_review_board_rows_for_display(rows), use_container_width=True, hide_index=True)
        else:
            st.info("표시할 active current candidate가 없습니다.")

    with st.expander("보조 도구: 저장된 Pre-Live 운영 기록 확인", expanded=False):
        st.caption(
            "Candidate Review 3번에서 저장한 Pre-Live 운영 기록입니다. "
            "이 기록은 live trading 승인이 아니라 Portfolio Proposal이 읽을 수 있는 운영 상태 로그입니다."
        )
        st.caption(f"Path: {PRE_LIVE_CANDIDATE_REGISTRY_FILE}")
        if pre_live_rows:
            st.dataframe(_build_pre_live_registry_rows_for_display(pre_live_rows), use_container_width=True, hide_index=True)
            pre_live_record_labels = [
                f"{row.get('pre_live_status')} | {row.get('title')} | {row.get('recorded_at')}"
                for row in pre_live_rows
            ]
            selected_pre_live_record_label = st.selectbox(
                "Inspect Pre-Live Record",
                options=pre_live_record_labels,
                key="candidate_review_selected_pre_live_record",
            )
            selected_pre_live_record = pre_live_rows[pre_live_record_labels.index(selected_pre_live_record_label)]
            st.json(selected_pre_live_record)
        else:
            st.info("아직 저장된 Pre-Live 운영 기록이 없습니다.")

    with st.expander("보조 도구: Send Candidates To Compare", expanded=False):
        st.caption(
            "대표 후보나 near-miss 후보를 compare form에 다시 채워 넣습니다. "
            "이 단계는 compare 실행이 아니라 입력값 prefill입니다."
        )
        if not rows:
            st.info("Compare로 보낼 active current candidate가 없습니다.")
        else:
            display_df = _build_current_candidate_registry_rows_for_display(rows)
            anchor_rows = [row for row in rows if str(row.get("record_type") or "") == "current_candidate"]
            near_miss_rows = [row for row in rows if str(row.get("record_type") or "") != "current_candidate"]
            label_to_row = {_current_candidate_registry_selection_label(row): row for row in rows}
            quick_action_cols = st.columns(2, gap="small")
            with quick_action_cols[0]:
                if st.button(
                    "Load Recommended Candidates",
                    key="candidate_review_load_current_candidate_anchors",
                    use_container_width=True,
                ):
                    try:
                        _queue_current_candidate_compare_prefill(anchor_rows)
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
                st.caption(f"대표 후보 `{len(anchor_rows)}`개를 compare form에 채웁니다.")
            with quick_action_cols[1]:
                if st.button(
                    "Load Lower-MDD Alternatives",
                    key="candidate_review_load_current_candidate_near_misses",
                    use_container_width=True,
                ):
                    try:
                        _queue_current_candidate_compare_prefill(near_miss_rows)
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
                st.caption(f"대안 / scenario 후보 `{len(near_miss_rows)}`개를 compare form에 채웁니다.")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            selected_labels = st.multiselect(
                "Choose Specific Candidates To Load Into Compare",
                options=list(label_to_row.keys()),
                max_selections=4,
                help="최소 2개 후보를 고르면 compare form으로 바로 불러올 수 있습니다. 같은 family 후보는 한 번에 하나만 지원합니다.",
                key="candidate_review_current_candidate_bundle_selection",
            )
            if st.button(
                "Load Selected Candidates Into Compare",
                key="candidate_review_load_selected_candidate_bundle",
                use_container_width=True,
            ):
                try:
                    selected_rows = [label_to_row[label] for label in selected_labels]
                    _queue_current_candidate_compare_prefill(selected_rows)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
