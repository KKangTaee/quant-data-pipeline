from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from html import escape
from textwrap import dedent
from typing import Any

import pandas as pd
import streamlit as st


GUIDE_ROUTE_OPTIONS = [
    "단일 후보",
    "여러 후보 포트폴리오",
    "저장 Mix",
    "막힘 해결",
]


def _route_cards() -> dict[str, dict[str, Any]]:
    return {
        "단일 후보": {
            "headline": "전략 하나를 끝까지 검토",
            "summary": "후보 1개를 Current Candidate와 Pre-Live 기록으로 남기고 Final Review가 직접 읽는 경로입니다.",
            "primary_action": "Single Strategy 또는 Compare 결과에서 Candidate Review로 보냅니다.",
            "skip": "Portfolio Proposal draft 저장은 반복하지 않습니다.",
            "next_screen": "Backtest > Candidate Review",
            "records": "Review Note, Current Candidate, Pre-Live, Final Decision",
            "dot": [
                ("single", "1-2\\nSingle Strategy", "run"),
                ("realmoney", "3-4\\nReal-Money Gate", "gate"),
                ("compare", "5\\nCompare", "compare"),
                ("candidate", "6\\nCandidate Review", "candidate"),
                ("direct", "7\\nDirect Candidate", "proposal"),
                ("final", "8-10\\nFinal Review", "final"),
            ],
            "edges": [
                ("single", "realmoney", "signal"),
                ("realmoney", "compare", "not hold"),
                ("compare", "candidate", "PASS / CONDITIONAL"),
                ("candidate", "direct", "PORTFOLIO_PROPOSAL_READY"),
                ("direct", "final", "검증"),
            ],
        },
        "여러 후보 포트폴리오": {
            "headline": "여러 후보를 하나의 proposal로 구성",
            "summary": "여러 current candidate를 목적, 역할, target weight가 있는 포트폴리오 초안으로 저장하는 경로입니다.",
            "primary_action": "각 후보를 Candidate Review에서 저장한 뒤 Portfolio Proposal에서 역할과 비중을 설계합니다.",
            "skip": "단일 후보 직행 평가는 쓰지 않습니다.",
            "next_screen": "Backtest > Portfolio Proposal",
            "records": "Current Candidate, Pre-Live, Portfolio Proposal, Final Decision",
            "dot": [
                ("candidates", "1-6\\nCandidate Pool", "candidate"),
                ("roles", "7A\\nRoles / Weights", "proposal"),
                ("draft", "7B\\nSave Proposal", "proposal"),
                ("validation", "8\\nValidation Pack", "gate"),
                ("final", "9-10\\nFinal Decision", "final"),
            ],
            "edges": [
                ("candidates", "roles", "2개 이상"),
                ("roles", "draft", "weight=100%"),
                ("draft", "validation", "proposal ready"),
                ("validation", "final", "hard blocker 없음"),
            ],
        },
        "저장 Mix": {
            "headline": "이미 저장된 weight setup을 workflow 기록으로 연결",
            "summary": "Compare에서 저장한 mix를 replay한 뒤 Candidate Review가 아니라 Portfolio Proposal 초안으로 연결합니다.",
            "primary_action": "Replay Saved Mix 후 Workflow Registry가 비어 있으면 Use This Mix In Portfolio Proposal을 사용합니다.",
            "skip": "Candidate Review는 건너뜁니다.",
            "next_screen": "Backtest > Compare & Portfolio Builder > 저장 Mix 다시 열기",
            "records": "Saved Portfolio, Portfolio Proposal, Final Decision",
            "dot": [
                ("saved", "5A\\nSaved Mix", "compare"),
                ("replay", "5B\\nReplay / Mix Board", "gate"),
                ("proposal", "7\\nUse In Proposal", "proposal"),
                ("final", "8-10\\nFinal Review", "final"),
            ],
            "edges": [
                ("saved", "replay", "replay"),
                ("replay", "proposal", "NOT RECORDED"),
                ("proposal", "final", "proposal saved"),
            ],
        },
        "막힘 해결": {
            "headline": "멈춰야 할 이유를 원인 화면으로 되돌림",
            "summary": "hold, blocked, evidence 부족, re-review가 나오면 Final Review 직행이 아니라 원인 화면으로 돌아갑니다.",
            "primary_action": "현재 막힌 항목을 먼저 고르고, 해당 화면에서 설정 / 데이터 / 후보 구성을 보강합니다.",
            "skip": "막힘 상태에서는 최종 판단 저장을 목표로 하지 않습니다.",
            "next_screen": "Real-Money, Compare, Candidate Review, Portfolio Proposal 중 원인 화면",
            "records": "필요할 때만 Review Note 또는 Final Decision에 보류 사유 기록",
            "dot": [
                ("hold", "3-4\\nHold / Blocker", "stop"),
                ("compare", "5\\nCompare 재검토", "compare"),
                ("candidate", "6\\nPackaging 보강", "candidate"),
                ("proposal", "7\\nProposal 수정", "proposal"),
                ("review", "8-9\\nHOLD / RE_REVIEW", "final"),
            ],
            "edges": [
                ("hold", "compare", "blocker 해결"),
                ("compare", "candidate", "근거 확보"),
                ("candidate", "proposal", "route ready"),
                ("proposal", "review", "검증"),
                ("review", "hold", "재검토 루프"),
            ],
        },
    }


def _decision_gate_rows() -> list[dict[str, str]]:
    return [
        {
            "gate": "Compare로 가도 되는가",
            "go": "Promotion이 hold가 아니고 Deployment가 blocked가 아님",
            "review": "warning은 있지만 원인과 보강 항목을 설명할 수 있음",
            "stop": "price freshness error, benchmark 부재, hard blocker",
            "screen": "Backtest 결과 > Real-Money",
        },
        {
            "gate": "Candidate로 남겨도 되는가",
            "go": "Compare PASS 또는 CONDITIONAL, 상대 근거와 Data Trust 해석 가능",
            "review": "상대 성과 약점은 있지만 포트폴리오 역할이 명확함",
            "stop": "비교 실패, Real-Money signal 공백, 상대 근거 없음",
            "screen": "Compare & Portfolio Builder",
        },
        {
            "gate": "Proposal로 묶어도 되는가",
            "go": "Current Candidate와 Pre-Live 운영 기록이 있고 route가 proposal ready",
            "review": "후보 수는 충분하지만 역할 / 비중 근거 보강 필요",
            "stop": "Pre-Live record 없음, active 후보 hold/reject, source 식별 불가",
            "screen": "Candidate Review / Portfolio Proposal",
        },
        {
            "gate": "Final Review를 기록해도 되는가",
            "go": "Validation, robustness, paper observation 기준이 해석 가능",
            "review": "관찰 기간 또는 제약 조건을 남기고 HOLD 기록 가능",
            "stop": "hard blocker가 남아 있거나 최종 판단 이유가 비어 있음",
            "screen": "Final Review",
        },
    ]


def _concept_rows() -> list[dict[str, str]]:
    return [
        {
            "개념": "Real-Money",
            "제품 안에서의 의미": "개별 backtest 결과에 붙는 실전 검토 신호",
            "사용자가 볼 곳": "Backtest 결과 > Real-Money",
        },
        {
            "개념": "Candidate Review",
            "제품 안에서의 의미": "좋아 보이는 결과를 후보 기록으로 남길지 판단하는 packaging 화면",
            "사용자가 볼 곳": "Backtest > Candidate Review",
        },
        {
            "개념": "Portfolio Proposal",
            "제품 안에서의 의미": "여러 후보를 목적 / 역할 / 비중이 있는 포트폴리오 초안으로 묶는 화면",
            "사용자가 볼 곳": "Backtest > Portfolio Proposal",
        },
        {
            "개념": "Final Review",
            "제품 안에서의 의미": "선정 / 보류 / 거절 / 재검토를 기록하는 마지막 판단 화면",
            "사용자가 볼 곳": "Backtest > Final Review",
        },
    ]


def _storage_rows() -> list[dict[str, str]]:
    return [
        {
            "기록": "Current Candidate Registry",
            "담는 내용": "다시 열어 볼 후보 정의",
            "생성 화면": "Candidate Review",
        },
        {
            "기록": "Pre-Live Candidate Registry",
            "담는 내용": "paper / watchlist / hold 같은 운영 상태",
            "생성 화면": "Candidate Review",
        },
        {
            "기록": "Saved Portfolio",
            "담는 내용": "Compare에서 저장한 재사용 weight setup",
            "생성 화면": "Compare & Portfolio Builder",
        },
        {
            "기록": "Portfolio Proposal Registry",
            "담는 내용": "목적 / 역할 / 비중이 있는 proposal draft",
            "생성 화면": "Portfolio Proposal",
        },
        {
            "기록": "Final Selection Decision",
            "담는 내용": "선정 / 보류 / 거절 / 재검토 최종 판단",
            "생성 화면": "Final Review",
        },
    ]


def _detail_step_rows() -> list[dict[str, str]]:
    return [
        {"단계": "1", "화면": "Ingestion", "목적": "가격 / 재무제표 / factor / profile 최신화"},
        {"단계": "2", "화면": "Single Strategy", "목적": "전략 하나의 성과와 실행 계약 확인"},
        {"단계": "3-4", "화면": "Real-Money", "목적": "승격 신호와 hold blocker 확인"},
        {"단계": "5", "화면": "Compare", "목적": "다른 전략 / 기준과 상대 근거 확인"},
        {"단계": "6", "화면": "Candidate Review", "목적": "Review Note, registry, Pre-Live 기록"},
        {"단계": "7", "화면": "Portfolio Proposal", "목적": "단일 후보 직행 또는 다중 후보 proposal 구성"},
        {"단계": "8-10", "화면": "Final Review", "목적": "검증 근거 확인, 최종 판단 저장, 결과 재확인"},
    ]


def _render_page_style() -> None:
    st.html(
        """
        <style>
          .qg-hero {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            padding: 1.1rem 1.2rem;
            background: linear-gradient(135deg, #f8fafc 0%, #eef4f8 100%);
            margin: 0.25rem 0 1rem;
          }
          .qg-hero-label {
            color: #4b5563;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
          }
          .qg-hero-title {
            color: #111827;
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 0.35rem;
          }
          .qg-hero-copy {
            color: #374151;
            font-size: 0.98rem;
            line-height: 1.55;
            max-width: 920px;
          }
          .qg-status-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.85rem;
          }
          .qg-chip {
            border: 1px solid #cbd5e1;
            border-radius: 999px;
            background: #ffffff;
            color: #334155;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.28rem 0.62rem;
          }
          .qg-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 0.7rem;
            margin: 0.7rem 0 1rem;
          }
          .qg-card {
            border: 1px solid #d8dee8;
            border-radius: 8px;
            background: #ffffff;
            padding: 0.85rem;
          }
          .qg-card-kicker {
            color: #64748b;
            font-size: 0.76rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
          }
          .qg-card-title {
            color: #111827;
            font-size: 1rem;
            font-weight: 800;
            line-height: 1.35;
            margin-bottom: 0.3rem;
          }
          .qg-card-copy {
            color: #374151;
            font-size: 0.86rem;
            line-height: 1.45;
          }
          .qg-route-summary {
            border-left: 4px solid #2f6f9f;
            padding: 0.2rem 0 0.2rem 0.8rem;
            margin: 0.2rem 0 0.8rem;
          }
          .qg-route-summary strong {
            display: block;
            color: #111827;
            font-size: 1.05rem;
            margin-bottom: 0.15rem;
          }
          .qg-route-summary span {
            color: #4b5563;
            font-size: 0.9rem;
            line-height: 1.45;
          }
        </style>
        """
    )


def _render_hero(runtime_marker: str | None, git_sha: str | None) -> None:
    runtime_text = escape(runtime_marker or "-")
    git_text = escape(git_sha or "-")
    st.html(
        f"""
        <section class="qg-hero">
          <div class="qg-hero-label">Portfolio Selection Guide</div>
          <div class="qg-hero-title">실전 후보 포트폴리오를 찾는 운영 가이드</div>
          <div class="qg-hero-copy">
            이 화면은 문서 목록이 아니라 의사결정 안내입니다. 먼저 지금 만들려는 포트폴리오 경로를 고르고,
            그 경로에서 어떤 화면을 지나고 어느 조건에서 멈춰야 하는지 확인합니다.
          </div>
          <div class="qg-status-strip">
            <span class="qg-chip">Current workflow: Portfolio Proposal -> Final Review</span>
            <span class="qg-chip">Runtime {runtime_text}</span>
            <span class="qg-chip">Git {git_text}</span>
          </div>
        </section>
        """
    )


def _render_orientation_cards(selected_route: str, route: dict[str, Any]) -> None:
    rows = [
        ("현재 경로", route["headline"], route["summary"]),
        ("다음 행동", route["next_screen"], route["primary_action"]),
        ("주의할 점", route["skip"], "이 경계가 Candidate Review와 Portfolio Proposal의 역할을 나눕니다."),
        ("읽는 기록", route["records"], "저장소는 서로 덮어쓰지 않고 단계별 판단을 따로 남깁니다."),
    ]
    card_html = []
    for kicker, title, copy in rows:
        card_html.append(
            f"""
            <div class="qg-card">
              <div class="qg-card-kicker">{escape(kicker)}</div>
              <div class="qg-card-title">{escape(title)}</div>
              <div class="qg-card-copy">{escape(copy)}</div>
            </div>
            """
        )
    st.html(f'<div class="qg-card-grid">{"".join(card_html)}</div>')

    st.caption(
        f"`{selected_route}` 경로를 보고 있습니다. 다른 portfolio 유형이면 위 선택 버튼에서 경로를 바꿔 확인합니다."
    )


def _dot_for_route(route: dict[str, Any]) -> str:
    palette = {
        "run": ("#e8f1f8", "#2f6f9f"),
        "gate": ("#fff7df", "#9a6a1d"),
        "compare": ("#edf7ed", "#4f7c45"),
        "candidate": ("#eaf6ef", "#2f7d57"),
        "proposal": ("#f7f0e3", "#9a6a1d"),
        "final": ("#eef0f6", "#5f6477"),
        "stop": ("#fff1e6", "#b45309"),
    }
    lines = [
        "digraph G {",
        "  graph [rankdir=LR, bgcolor=\"transparent\", pad=\"0.2\", nodesep=\"0.45\", ranksep=\"0.75\", splines=ortho];",
        "  node [shape=rect, style=\"rounded,filled\", fontname=\"Arial\", fontsize=12, margin=\"0.16,0.10\", penwidth=1.7];",
        "  edge [fontname=\"Arial\", fontsize=10, color=\"#64748b\", fontcolor=\"#475569\", arrowsize=0.7, penwidth=1.5];",
    ]
    for node_id, label, tone in route["dot"]:
        fill, border = palette.get(tone, palette["run"])
        shape = "diamond" if tone in {"gate", "stop"} else "rect"
        lines.append(
            f'  {node_id} [label="{label}", fillcolor="{fill}", color="{border}", shape={shape}];'
        )
    for src, dst, label in route["edges"]:
        lines.append(f'  {src} -> {dst} [label="{label}"];')
    lines.append("}")
    return "\n".join(lines)


def _render_css_flow_fallback(route: dict[str, Any]) -> None:
    cards = []
    for index, (node_id, label, tone) in enumerate(route["dot"]):
        del node_id
        step_label = escape(label.replace("\\n", " / "))
        cards.append(
            f'<span class="qg-chip">{step_label}</span>'
        )
        if index < len(route["dot"]) - 1:
            cards.append('<span class="qg-chip">-&gt;</span>')
    st.html(f'<div class="qg-status-strip">{"".join(cards)}</div>')


def _render_flow_visual(selected_route: str, route: dict[str, Any]) -> None:
    st.markdown("### Portfolio Flow")
    st.html(
        f"""
        <div class="qg-route-summary">
          <strong>{escape(route["headline"])}</strong>
          <span>{escape(route["summary"])}</span>
        </div>
        """
    )
    try:
        st.graphviz_chart(_dot_for_route(route), width="stretch", height=360)
    except Exception:
        _render_css_flow_fallback(route)
        st.caption("현재 환경에서 GraphViz 렌더링을 사용할 수 없어 compact visual fallback으로 표시했습니다.")
    st.caption(
        f"`{selected_route}` flow는 live approval이나 주문 지시가 아니라, Final Review에 도달하기 전의 검토 경로입니다."
    )


def _render_decision_gates() -> None:
    st.markdown("### Decision Gates")
    st.caption("단계 번호보다 사용자가 실제로 묻는 질문을 기준으로 Go / Review / Stop을 구분합니다.")
    rows = _decision_gate_rows()
    for row in rows:
        with st.container(border=True):
            st.markdown(f"#### {row['gate']}")
            cols = st.columns(3)
            cols[0].success(f"Go: {row['go']}")
            cols[1].warning(f"Review: {row['review']}")
            cols[2].error(f"Stop: {row['stop']}")
            st.caption(f"확인 위치: {row['screen']}")


def _render_reference_drawer() -> None:
    st.markdown("### Reference Drawer")
    st.caption("상세 설명, 저장소 의미, 운영 경계는 필요할 때만 펼쳐 확인합니다.")
    tabs = st.tabs(["핵심 개념", "상세 단계", "기록 저장소", "운영 경계"])
    with tabs[0]:
        st.dataframe(pd.DataFrame(_concept_rows()), width="stretch", hide_index=True)
    with tabs[1]:
        st.dataframe(pd.DataFrame(_detail_step_rows()), width="stretch", hide_index=True)
        with st.expander("1~10단계 전체를 어떻게 읽나", expanded=False):
            st.markdown(
                """
                - `1-5`: 데이터, 단일 전략, Real-Money, Compare로 후보 근거를 만든다.
                - `6`: Candidate Review에서 후보로 남길지와 Pre-Live 운영 상태를 기록한다.
                - `7`: 단일 후보는 direct candidate로 읽고, 여러 후보는 proposal draft로 묶는다.
                - `8-10`: Final Review에서 검증 근거와 최종 판단을 남기고 다시 확인한다.
                """
            )
    with tabs[2]:
        st.dataframe(pd.DataFrame(_storage_rows()), width="stretch", hide_index=True)
        st.info(
            "Saved Portfolio는 재사용 setup이고, Portfolio Proposal은 workflow 기록입니다. "
            "saved mix는 Candidate Review가 아니라 Portfolio Proposal로 연결합니다."
        )
    with tabs[3]:
        st.warning(
            "`SELECT_FOR_PRACTICAL_PORTFOLIO`는 실전 후보 선정 신호이지 live approval, broker order, 자동매매 지시가 아닙니다."
        )
        st.markdown(
            """
            - `Real-Money`는 검증 신호입니다.
            - `Candidate Review`는 후보 기록입니다.
            - `Portfolio Proposal`은 후보 묶음 초안입니다.
            - `Final Review`는 현재 workflow의 마지막 판단 기록입니다.
            - `Live Approval / Order`는 현재 제품 범위 밖입니다.
            """
        )


def _render_runtime_reference(
    loaded_at: datetime | None,
    render_runtime_snapshot: Callable[[], None] | None,
) -> None:
    with st.expander("System status", expanded=False):
        if render_runtime_snapshot is not None:
            render_runtime_snapshot()
            return
        if loaded_at is not None:
            st.caption(f"Loaded at: {loaded_at:%Y-%m-%d %H:%M:%S}")


def render_reference_guides_page(
    *,
    runtime_marker: str | None = None,
    loaded_at: datetime | None = None,
    git_sha: str | None = None,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    """Render the product-facing reference guide for portfolio selection workflows."""

    _render_page_style()
    st.title("Guides")
    st.caption("포트폴리오 후보 선정 흐름을 빠르게 고르고, 다음 화면과 멈춤 기준을 확인하는 안내 화면입니다.")
    _render_hero(runtime_marker, git_sha)

    routes = _route_cards()
    state_key = "reference_guides_primary_route"
    if st.session_state.get(state_key) not in GUIDE_ROUTE_OPTIONS:
        st.session_state[state_key] = GUIDE_ROUTE_OPTIONS[0]

    if hasattr(st, "segmented_control"):
        st.segmented_control(
            "지금 확인할 경로",
            options=GUIDE_ROUTE_OPTIONS,
            selection_mode="single",
            required=True,
            key=state_key,
            width="stretch",
        )
        selected_route = str(st.session_state.get(state_key) or GUIDE_ROUTE_OPTIONS[0])
    else:
        selected_route = st.radio(
            "지금 확인할 경로",
            options=GUIDE_ROUTE_OPTIONS,
            horizontal=True,
            key=state_key,
        )

    route = routes[selected_route]
    _render_orientation_cards(selected_route, route)
    _render_flow_visual(selected_route, route)
    _render_decision_gates()
    _render_reference_drawer()
    _render_runtime_reference(loaded_at, render_runtime_snapshot)
