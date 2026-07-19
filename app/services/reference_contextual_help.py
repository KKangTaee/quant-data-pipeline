from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.reference_glossary_catalog import get_reference_concept_dictionary


ALLOWED_REFERENCE_HELP_TARGETS = {"/guides", "/glossary"}


REFERENCE_CONTEXTUAL_HELP: list[dict[str, Any]] = [
    {
        "surface_key": "backtest_analysis",
        "surface": "Backtest > Backtest Analysis",
        "title": "후보 source를 만들 때 막히면",
        "summary": "Single Strategy와 Portfolio Mix Builder에서 만든 결과가 어떤 다음 단계로 이어지는지 확인합니다.",
        "guide_focus": "제품 흐름 / Backtest Analysis / Portfolio Selection Journey",
        "glossary_terms": ["Promotion Policy Signal", "Data Trust", "Saved Portfolio"],
        "next_checks": [
            "Workspace > Ingestion > 실행 기록 / 결과에서 source 상태와 실패 원인을 확인합니다.",
            "Portfolio Mix 결과는 저장 setup인지, Practical Validation source인지 구분합니다.",
            "Promotion Policy Signal은 Final Review selected decision을 대체하지 않습니다.",
        ],
        "boundaries": [
            "후보 source 생성 화면이며 live approval, broker order, auto rebalance를 만들지 않습니다.",
            "Saved Portfolio는 재사용 setup이고 validation 결과나 selected decision이 아닙니다.",
        ],
        "links": [
            {"label": "Guides에서 workflow 확인", "target": "/guides"},
            {"label": "Glossary에서 용어 확인", "target": "/glossary"},
        ],
    },
    {
        "surface_key": "practical_validation",
        "surface": "Backtest > Practical Validation",
        "title": "검증 row가 왜 막혔는지 볼 때",
        "summary": "NOT_RUN, REVIEW, BLOCKED 상태가 pass인지 blocker인지 구분하고 evidence owner를 찾습니다.",
        "guide_focus": "상태 / 용어 / NOT_RUN / REVIEW / BLOCKED, 문제 해결 / Practical Validation NOT_RUN",
        "glossary_terms": ["NOT_RUN", "REVIEW", "BLOCKED", "Provider Coverage"],
        "next_checks": [
            "NOT_RUN은 pass가 아니라 실행되지 않았거나 evidence가 없는 상태입니다.",
            "Provider Coverage가 partial/proxy이면 review evidence로 해석합니다.",
            "Final Review Gate가 막히면 관련 audit board와 evidence owner를 먼저 확인합니다.",
        ],
        "boundaries": [
            "Practical Validation은 검증 근거 저장 화면이며 최종 사용자 판단 메모는 Final Review에서만 남깁니다.",
            "provider gap 수집은 명시 버튼으로만 실행되며 이 help box는 아무 작업도 실행하지 않습니다.",
        ],
        "links": [
            {"label": "Guides에서 validation 흐름 확인", "target": "/guides"},
            {"label": "Glossary에서 상태 의미 확인", "target": "/glossary"},
        ],
    },
    {
        "surface_key": "final_review",
        "surface": "Backtest > Final Review",
        "title": "모니터링 후보로 저장해도 되는지 볼 때",
        "summary": "selected-route gate, decision record, Portfolio Monitoring handoff의 의미를 확인합니다.",
        "guide_focus": "제품 흐름 / Final Review, 상태 / 용어 / Selected-route Gate",
        "glossary_terms": ["Selected-route Gate", "Provider Coverage", "Data Trust"],
        "next_checks": [
            "Practical Validation Gate를 통과한 후보만 Final Review 검토 대상입니다.",
            "Selected-route Gate가 blocked이면 정식 선정 저장으로 진행하지 않습니다.",
            "저장된 selected decision은 Portfolio Monitoring에서 read-only로 다시 읽습니다.",
        ],
        "boundaries": [
            "`SELECT_FOR_PRACTICAL_PORTFOLIO`는 monitoring 후보 선정 기록이지 broker order가 아닙니다.",
            "Final Review는 live approval, account sync, auto rebalance를 만들지 않습니다.",
        ],
        "links": [
            {"label": "Guides에서 final route 확인", "target": "/guides"},
            {"label": "Glossary에서 gate 용어 확인", "target": "/glossary"},
        ],
    },
    {
        "surface_key": "portfolio_monitoring",
        "surface": "Operations > Portfolio Monitoring",
        "title": "모니터링 시나리오가 stale이거나 비어 있을 때",
        "summary": "Final Review selected row, portfolio setup, scenario replay 결과의 차이를 확인합니다.",
        "guide_focus": "제품 흐름 / Operations / Portfolio Monitoring, 문제 해결 / stale scenario",
        "glossary_terms": ["Portfolio Monitoring Scenario", "Saved Portfolio", "Selected-route Gate"],
        "next_checks": [
            "Final Review에서 저장된 selected decision row가 있는지 확인합니다.",
            "전략 slot signature, start/latest mode, balance가 바뀌면 scenario update가 필요합니다.",
            "Monitoring Scenario는 사후 관찰 근거이며 새 최종 판단이나 주문 지시가 아닙니다.",
        ],
        "boundaries": [
            "Portfolio Monitoring은 read-only monitoring surface이며 live approval, broker order, auto rebalance를 만들지 않습니다.",
            "사용자 portfolio setup은 saved setup이며 validation / approval record가 아닙니다.",
        ],
        "links": [
            {"label": "Guides에서 monitoring 흐름 확인", "target": "/guides"},
            {"label": "Glossary에서 scenario 용어 확인", "target": "/glossary"},
        ],
    },
]


def get_reference_contextual_help_catalog() -> list[dict[str, Any]]:
    return deepcopy(REFERENCE_CONTEXTUAL_HELP)


def get_reference_contextual_help(surface_key: str) -> dict[str, Any] | None:
    normalized_key = str(surface_key or "").strip()
    for item in REFERENCE_CONTEXTUAL_HELP:
        if item["surface_key"] == normalized_key:
            return deepcopy(item)
    return None


def _duplicate_surface_keys(catalog: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in catalog:
        key = str(item.get("surface_key") or "").strip()
        if not key:
            continue
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    return sorted(duplicates)


def build_reference_contextual_help_drift_report() -> dict[str, Any]:
    """Return a Streamlit-free alignment report for contextual Reference help."""
    catalog = get_reference_contextual_help_catalog()
    concept_terms = {
        str(row.get("term") or "").strip()
        for row in get_reference_concept_dictionary()
        if str(row.get("term") or "").strip()
    }

    missing_glossary_terms: list[dict[str, str]] = []
    invalid_links: list[dict[str, str]] = []
    raw_guide_focus_markers: list[dict[str, str]] = []
    contextual_terms: set[str] = set()
    link_count = 0

    for item in catalog:
        surface_key = str(item.get("surface_key") or "").strip()
        guide_focus = str(item.get("guide_focus") or "")
        if ">" in guide_focus:
            raw_guide_focus_markers.append(
                {
                    "surface_key": surface_key,
                    "guide_focus": guide_focus,
                }
            )

        for term in list(item.get("glossary_terms") or []):
            normalized_term = str(term or "").strip()
            if not normalized_term:
                continue
            contextual_terms.add(normalized_term)
            if normalized_term not in concept_terms:
                missing_glossary_terms.append(
                    {
                        "surface_key": surface_key,
                        "term": normalized_term,
                    }
                )

        for link in list(item.get("links") or []):
            link_count += 1
            target = str(link.get("target") or "").strip()
            if target not in ALLOWED_REFERENCE_HELP_TARGETS:
                invalid_links.append(
                    {
                        "surface_key": surface_key,
                        "target": target,
                    }
                )

    duplicate_surface_keys = _duplicate_surface_keys(catalog)
    has_issues = any(
        [
            missing_glossary_terms,
            invalid_links,
            duplicate_surface_keys,
            raw_guide_focus_markers,
        ]
    )
    return {
        "status": "REVIEW" if has_issues else "PASS",
        "metrics": {
            "surface_count": len(catalog),
            "glossary_term_count": len(contextual_terms),
            "link_count": link_count,
        },
        "missing_glossary_terms": missing_glossary_terms,
        "invalid_links": invalid_links,
        "duplicate_surface_keys": duplicate_surface_keys,
        "raw_guide_focus_markers": raw_guide_focus_markers,
    }
