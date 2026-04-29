from __future__ import annotations

from datetime import date, timedelta
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from app.web.backtest_candidate_review_helpers import (
    _build_current_candidate_registry_rows_for_display,
    _current_candidate_registry_selection_label,
)
from app.web.backtest_pre_live_review_helpers import (
    PRE_LIVE_STATUS_OPTIONS,
    _build_pre_live_draft_from_current_candidate,
    _build_pre_live_operating_readiness_evaluation,
    _build_pre_live_registry_rows_for_display,
    _default_pre_live_next_action,
    _default_pre_live_operator_reason,
    _default_pre_live_status_from_current_candidate,
    _pre_live_status_korean_label,
    _pre_live_status_suggestion_reason,
)
from app.web.runtime import (
    CURRENT_CANDIDATE_REGISTRY_FILE,
    PRE_LIVE_CANDIDATE_REGISTRY_FILE,
    append_pre_live_candidate_registry_row as _append_pre_live_candidate_registry_row,
    load_current_candidate_registry_latest as _load_current_candidate_registry_latest,
    load_pre_live_candidate_registry_latest as _load_pre_live_candidate_registry_latest,
)


# Render long Pre-Live status strings as wrapping cards instead of truncating Streamlit metrics.
def _render_status_card_grid(cards: list[dict[str, Any]]) -> None:
    html_cards: list[str] = []
    for card in cards:
        title = escape(str(card.get("title") or ""))
        value = escape(str(card.get("value") or "-"))
        detail = escape(str(card.get("detail") or ""))
        tone = escape(str(card.get("tone") or "neutral"))
        detail_html = f'<div class="pl-status-card-detail">{detail}</div>' if detail else ""
        html_cards.append(
            f'<div class="pl-status-card pl-status-card-{tone}">'
            f'<div class="pl-status-card-title">{title}</div>'
            f'<div class="pl-status-card-value">{value}</div>'
            f"{detail_html}"
            "</div>"
        )
    st.markdown(
        """
        <style>
          .pl-status-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.75rem;
            margin: 0.35rem 0 1rem 0;
          }
          .pl-status-card {
            min-height: 104px;
            padding: 0.9rem 1rem;
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-top: 4px solid #64748b;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
          }
          .pl-status-card-positive { border-top-color: #0f766e; }
          .pl-status-card-warning { border-top-color: #b45309; }
          .pl-status-card-danger { border-top-color: #b91c1c; }
          .pl-status-card-neutral { border-top-color: #475569; }
          .pl-status-card-title {
            font-size: 0.86rem;
            font-weight: 650;
            color: #475569;
            margin-bottom: 0.45rem;
            overflow-wrap: anywhere;
          }
          .pl-status-card-value {
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.25;
            color: #111827;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .pl-status-card-detail {
            margin-top: 0.45rem;
            font-size: 0.82rem;
            line-height: 1.3;
            color: #64748b;
            overflow-wrap: anywhere;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="pl-status-card-grid">{"".join(html_cards)}</div>',
        unsafe_allow_html=True,
    )


def render_pre_live_review_workspace() -> None:
    from app.web.pages import backtest as bt

    _request_backtest_panel = bt._request_backtest_panel

    st.markdown("### Pre-Live Review")
    st.caption(
        "7단계 Pre-Live 운영 점검 화면입니다. Candidate Packaging을 통과한 후보나 직접 선택한 current candidate를 "
        "실제 돈 투입 전 운영 상태로 분류하고, 다음 점검 계획을 남깁니다."
    )

    candidate_review_notice = st.session_state.get("candidate_review_to_pre_live_notice")
    if candidate_review_notice:
        st.info(candidate_review_notice)
        st.session_state.candidate_review_to_pre_live_notice = None

    current_rows = _load_current_candidate_registry_latest()
    pre_live_rows = _load_pre_live_candidate_registry_latest()

    _render_status_card_grid(
        [
            {"title": "Current Candidates", "value": len(current_rows), "tone": "neutral"},
            {"title": "Pre-Live Active Records", "value": len(pre_live_rows), "tone": "positive"},
            {"title": "Live Trading", "value": "Disabled", "tone": "danger", "detail": "Pre-Live는 투자 승인 단계가 아닙니다."},
        ]
    )

    with st.container(border=True):
        st.markdown("#### 7단계 Pre-Live 운영 점검")
        st.caption(
            "이 단계는 전략을 다시 백테스트하는 곳이 아니라, 이미 후보로 남긴 Candidate를 실제 돈 없이 어떻게 관찰할지 정하는 운영 기록 단계입니다."
        )
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "확인 영역": "후보 연결",
                        "무엇을 확인하나": "6단계 Candidate Packaging에서 넘어온 후보인지, 직접 선택한 current candidate인지 확인",
                        "얻는 정보": "운영 점검 대상 후보의 registry identity",
                    },
                    {
                        "확인 영역": "운영 상태",
                        "무엇을 확인하나": "paper tracking / watchlist / hold / reject / re-review 중 어디에 둘지 결정",
                        "얻는 정보": "실제 돈 투입 전 추적 방식",
                    },
                    {
                        "확인 영역": "다음 단계",
                        "무엇을 확인하나": "Portfolio Proposal로 넘길 수 있는지, 아니면 관찰/보류/종료인지 판단",
                        "얻는 정보": "8단계 진입 route와 blocker",
                    },
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            f"저장 위치: `{PRE_LIVE_CANDIDATE_REGISTRY_FILE}`. "
            "`Save Pre-Live Record`를 누르기 전까지는 저장 전 초안입니다."
        )

    if not current_rows:
        st.info("현재 current candidate registry에 active 후보가 없습니다.")
        st.caption(f"Path: {CURRENT_CANDIDATE_REGISTRY_FILE}")
    else:
        st.markdown("#### 1. 운영 후보 확인")
        label_to_row = {_current_candidate_registry_selection_label(row): row for row in current_rows}
        focus_label = str(st.session_state.get("pre_live_focus_candidate_label") or "").strip()
        focus_registry_id = str(st.session_state.get("pre_live_focus_registry_id") or "").strip()
        focus_revision_id = str(st.session_state.get("pre_live_focus_revision_id") or "").strip()
        if focus_label in label_to_row:
            st.session_state["pre_live_candidate_to_review"] = focus_label
        elif focus_registry_id:
            for candidate_label, candidate_row in label_to_row.items():
                row_registry_id = str(candidate_row.get("registry_id") or "").strip()
                row_revision_id = str(candidate_row.get("revision_id") or "").strip()
                if row_registry_id == focus_registry_id and (not focus_revision_id or row_revision_id == focus_revision_id):
                    st.session_state["pre_live_candidate_to_review"] = candidate_label
                    break
        if st.session_state.get("pre_live_candidate_to_review") not in label_to_row:
            st.session_state["pre_live_candidate_to_review"] = next(iter(label_to_row.keys()))

        selected_label = st.selectbox(
            "Pre-Live 운영 점검 후보",
            options=list(label_to_row.keys()),
            key="pre_live_candidate_to_review",
            help="Candidate Packaging에서 넘어온 후보가 있으면 자동 선택됩니다. 직접 들어온 경우 여기서 후보를 고르면 됩니다.",
        )
        selected_row = label_to_row[selected_label]
        registry_id = str(selected_row.get("registry_id") or "unknown")
        result = dict(selected_row.get("result") or {})
        incoming_from_packaging = (
            bool(focus_registry_id)
            and str(selected_row.get("registry_id") or "").strip() == focus_registry_id
            and (not focus_revision_id or str(selected_row.get("revision_id") or "").strip() == focus_revision_id)
        )
        if incoming_from_packaging:
            st.success("Candidate Packaging에서 넘어온 후보가 선택되어 있습니다.")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Registry ID": selected_row.get("registry_id"),
                            "Revision ID": selected_row.get("revision_id"),
                            "Record Type": selected_row.get("record_type"),
                            "Strategy Family": selected_row.get("strategy_family"),
                            "Strategy Name": selected_row.get("strategy_name"),
                            "Title": selected_row.get("title"),
                        }
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("직접 Pre-Live Review로 들어온 경우에도 여기서 후보를 선택해 7단계를 시작할 수 있습니다.")
        with st.expander("Current Candidate 후보 목록", expanded=False):
            st.dataframe(_build_current_candidate_registry_rows_for_display(current_rows), use_container_width=True, hide_index=True)

        default_status = _default_pre_live_status_from_current_candidate(selected_row)
        existing_pre_live_rows = [
            row
            for row in pre_live_rows
            if str(row.get("source_candidate_registry_id") or "").strip() == registry_id
            and str(row.get("record_status") or "active").strip().lower() == "active"
        ]
        latest_existing_pre_live = existing_pre_live_rows[0] if existing_pre_live_rows else None
        if latest_existing_pre_live:
            st.info(
                "이미 이 candidate에 연결된 active Pre-Live 기록이 있습니다. "
                "다시 저장하면 append-only 방식으로 새 revision이 추가되고 latest view에서는 새 기록이 보입니다."
            )

        st.markdown("#### 2. 운영 상태 / 추적 계획 결정")
        _render_status_card_grid(
            [
                {"title": "Promotion", "value": str(result.get("promotion") or "-"), "tone": "positive"},
                {"title": "Shortlist", "value": str(result.get("shortlist") or "-"), "tone": "neutral"},
                {"title": "Deployment", "value": str(result.get("deployment") or "-"), "tone": "warning"},
                {
                    "title": "System Suggested Status",
                    "value": _pre_live_status_korean_label(default_status),
                    "tone": "positive" if default_status == "paper_tracking" else "neutral",
                },
            ]
        )
        with st.container(border=True):
            st.markdown("##### Status Recommendation")
            st.caption(
                "System Suggested Status는 선택한 current candidate의 Real-Money 신호와 blocker를 바탕으로 계산한 추천값입니다. "
                "Operator Final Status가 실제 저장되는 운영 판단입니다."
            )
            st.info(_pre_live_status_suggestion_reason(selected_row, default_status))
        with st.expander("Pre-Live Status 의미", expanded=False):
            st.dataframe(
                pd.DataFrame(
                    [
                        {"Status": "paper_tracking", "의미": "실제 돈 없이 성과와 blocker 변화를 추적", "다음 단계": "Portfolio Proposal 후보로 검토 가능"},
                        {"Status": "watchlist", "의미": "다시 볼 후보로 남기되 아직 paper tracking 전", "다음 단계": "후보 비교 또는 데이터 업데이트 후 재검토"},
                        {"Status": "hold", "의미": "blocker나 미확인 요소가 남아 보류", "다음 단계": "보류 사유 해소 후 재검토"},
                        {"Status": "reject", "의미": "현재 기준에서는 추적 종료", "다음 단계": "새 근거가 생기면 새 후보로 재검토"},
                        {"Status": "re_review", "의미": "정해진 날짜에 다시 확인", "다음 단계": "review date에 상태 재분류"},
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )
        selected_status = st.selectbox(
            "Operator Final Status",
            options=PRE_LIVE_STATUS_OPTIONS,
            index=PRE_LIVE_STATUS_OPTIONS.index(default_status) if default_status in PRE_LIVE_STATUS_OPTIONS else 0,
            format_func=_pre_live_status_korean_label,
            key=f"pre_live_status_{registry_id}",
            help="이 값이 Pre-Live registry에 저장됩니다. 투자 승인 상태가 아니라 실전 전 운영 상태입니다.",
        )
        if selected_status != default_status:
            st.warning(
                "Operator Final Status가 System Suggested Status와 다릅니다. "
                "의도적으로 다른 결정을 내리는 경우 Operator Reason에 근거를 남겨주세요."
            )
        operator_reason = st.text_area(
            "Operator Reason",
            value=_default_pre_live_operator_reason(selected_row, selected_status),
            key=f"pre_live_reason_{registry_id}_{selected_status}",
            help="왜 이 후보를 이 상태로 두는지 사람이 읽을 수 있게 남깁니다.",
        )
        next_action = st.text_area(
            "Next Action",
            value=_default_pre_live_next_action(selected_status),
            key=f"pre_live_next_action_{registry_id}_{selected_status}",
            help="다음에 무엇을 확인하거나 실행할지 남깁니다.",
        )
        default_use_review_date = selected_status in {"paper_tracking", "re_review"}
        use_review_date = st.checkbox(
            "Review Date 지정",
            value=default_use_review_date,
            key=f"pre_live_use_review_date_{registry_id}_{selected_status}",
            help="paper tracking과 re-review는 다음 점검일을 두는 것이 안전합니다.",
        )
        review_date_value: date | None = None
        if use_review_date or selected_status in {"paper_tracking", "re_review"}:
            review_date_value = st.date_input(
                "Review Date",
                value=date.today() + timedelta(days=30),
                key=f"pre_live_review_date_{registry_id}_{selected_status}",
            )

        draft = _build_pre_live_draft_from_current_candidate(
            selected_row,
            pre_live_status=selected_status,
            operator_reason=operator_reason,
            next_action=next_action,
            review_date_value=review_date_value,
        )
        readiness = _build_pre_live_operating_readiness_evaluation(
            selected_row,
            pre_live_status=selected_status,
            operator_reason=operator_reason,
            next_action=next_action,
            review_date_value=review_date_value,
        )

        st.markdown("#### 3. Portfolio Proposal 진입 평가")
        with st.container(border=True):
            st.caption(
                "이 점수는 전략 성과 점수가 아니라, Pre-Live 운영 기록이 8단계 Portfolio Proposal에서 읽을 수 있을 만큼 "
                "후보 식별, 운영 상태, 추적 계획을 갖췄는지 보는 체크입니다."
            )
            eval_cols = st.columns([0.24, 0.18, 0.18, 0.4], gap="small")
            eval_cols[0].metric("Route", str(readiness["route_label"]))
            eval_cols[1].metric("Readiness", f"{float(readiness['score']):.1f} / 10")
            eval_cols[2].metric("Blockers", len(readiness["blocking_reasons"]))
            with eval_cols[3]:
                st.caption("판정")
                st.markdown(f"**{readiness['verdict']}**")
                st.caption("다음 행동")
                st.markdown(str(readiness["next_action"]))
            st.progress(max(0.0, min(float(readiness["score"]) / 10.0, 1.0)))
            st.dataframe(pd.DataFrame(readiness["criteria_rows"]), use_container_width=True, hide_index=True)
            if readiness["can_move_to_portfolio_proposal"]:
                st.success("7단계 통과: Pre-Live record를 저장하면 8단계 Portfolio Proposal에서 후보로 사용할 수 있습니다.")
            elif readiness["can_save_record"]:
                st.info("Pre-Live 기록 저장은 가능하지만, 현재 route는 Portfolio Proposal 직행이 아닙니다.")
            else:
                st.error("저장 전 확인 필요: " + ", ".join(str(item) for item in readiness["blocking_reasons"]))
            if readiness["warning_reasons"]:
                st.warning("주의 항목: " + ", ".join(str(item) for item in readiness["warning_reasons"]))

        st.markdown("#### 4. 저장 및 다음 단계")
        st.caption(
            "아래 JSON은 저장 전 초안입니다. `Save Pre-Live Record`를 눌러야 실제 registry에 기록됩니다."
        )
        with st.expander("Pre-Live Record JSON Preview", expanded=False):
            st.json(draft)

        save_disabled = not bool(readiness["can_save_record"])
        matching_saved_record = bool(
            latest_existing_pre_live
            and str(latest_existing_pre_live.get("pre_live_status") or "") == selected_status
        )
        action_cols = st.columns([0.28, 0.28, 0.44], gap="small")
        with action_cols[0]:
            if st.button(
                "Save Pre-Live Record",
                key=f"save_pre_live_record_{registry_id}",
                disabled=save_disabled,
                use_container_width=True,
            ):
                _append_pre_live_candidate_registry_row(draft)
                st.session_state["pre_live_recent_record_id"] = draft["pre_live_id"]
                st.session_state["pre_live_recent_revision_id"] = draft["revision_id"]
                st.success(f"Pre-Live 기록 `{draft['pre_live_id']}`를 저장했습니다.")
                st.rerun()
        with action_cols[1]:
            proposal_disabled = not bool(readiness["can_move_to_portfolio_proposal"]) or not matching_saved_record
            if st.button(
                "Open Portfolio Proposal",
                key=f"open_portfolio_proposal_from_pre_live_{registry_id}",
                disabled=proposal_disabled,
                use_container_width=True,
                help="paper_tracking 상태의 저장된 Pre-Live record가 있을 때 Portfolio Proposal로 이동합니다.",
            ):
                st.session_state["portfolio_proposal_component_selection"] = [selected_label]
                st.session_state["portfolio_proposal_from_pre_live_notice"] = (
                    f"`{selected_row.get('title') or registry_id}` 후보를 Pre-Live Review에서 Portfolio Proposal로 열었습니다."
                )
                _request_backtest_panel("Portfolio Proposal")
                st.rerun()
        with action_cols[2]:
            st.caption(
                "`Open Portfolio Proposal`은 같은 후보의 현재 선택 상태가 저장된 Pre-Live record와 맞을 때 활성화됩니다. "
                "저장해도 live trading이 열리는 것은 아닙니다."
            )

    st.divider()
    with st.expander("보조 도구: 저장된 Pre-Live 기록 확인", expanded=False):
        st.markdown("#### 저장된 Pre-Live Registry")
        st.caption(f"Path: {PRE_LIVE_CANDIDATE_REGISTRY_FILE}")
        if not pre_live_rows:
            st.info("아직 저장된 Pre-Live 운영 기록이 없습니다.")
        else:
            st.dataframe(_build_pre_live_registry_rows_for_display(pre_live_rows), use_container_width=True, hide_index=True)
            record_labels = [
                f"{row.get('pre_live_status')} | {row.get('title')} | {row.get('recorded_at')}"
                for row in pre_live_rows
            ]
            selected_record_label = st.selectbox(
                "Inspect Pre-Live Record",
                options=record_labels,
                key="pre_live_selected_record",
            )
            selected_record = pre_live_rows[record_labels.index(selected_record_label)]
            st.json(selected_record)
