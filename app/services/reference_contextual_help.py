from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.reference_center import get_reference_center_items


ALLOWED_REFERENCE_HELP_TARGETS = {"/reference"}


REFERENCE_CONTEXTUAL_HELP: list[dict[str, Any]] = [
    {
        "surface_key": "overview",
        "surface": "Overview",
        "title": "시장 관점을 어디서부터 읽을지 막힐 때",
        "summary": "Market Context를 시작점으로 현재 시장, 경기, 움직임, 심리, 이벤트의 역할을 구분합니다.",
        "reference_item_ids": ["journey.market_understanding", "feature.market_context"],
        "next_checks": [
            "Market Context의 결론과 자료 제한을 먼저 읽습니다.",
            "가격 움직임은 Market Movers, 선물·거시는 Futures Macro에서 보강합니다.",
            "Economic Cycle의 잠정·검증 상태를 같은 확정도로 읽지 않습니다.",
        ],
        "boundaries": [
            "Overview는 시장 맥락을 설명하며 자동 매매나 주문 지시를 만들지 않습니다.",
            "심리와 이벤트는 판단을 보조하는 근거이며 독립 gate가 아닙니다.",
        ],
        "links": [
            {"label": "시장 이해 흐름", "target": "/reference", "item_id": "journey.market_understanding"},
            {"label": "Market Context 의미", "target": "/reference", "item_id": "feature.market_context"},
        ],
    },
    {
        "surface_key": "institutional_portfolios",
        "surface": "Institutional Portfolios",
        "title": "13F 보유를 어떻게 읽어야 할지 막힐 때",
        "summary": "기관, 보고기간, 전체 보유, 개별 종목과 provider coverage를 순서대로 확인합니다.",
        "reference_item_ids": ["journey.institutional_portfolios", "concept.provider_coverage"],
        "next_checks": [
            "선택 기관과 최신 report period가 의도한 대상인지 확인합니다.",
            "전체 보유와 mapping coverage를 확인한 뒤 개별 종목으로 내려갑니다.",
            "13F 변화는 지연된 공개 보고 차이이며 실시간 매수·매도 신호가 아닙니다.",
        ],
        "boundaries": [
            "공개 13F 자료는 보고 시차가 있으며 현재 실제 보유를 보장하지 않습니다.",
            "이 화면은 추천, 승인, broker order를 만들지 않습니다.",
        ],
        "links": [
            {"label": "기관 보유 해석 흐름", "target": "/reference", "item_id": "journey.institutional_portfolios"},
            {"label": "Provider Coverage 의미", "target": "/reference", "item_id": "concept.provider_coverage"},
        ],
    },
    {
        "surface_key": "ingestion",
        "surface": "Ingestion",
        "title": "어떤 데이터를 준비해야 할지 막힐 때",
        "summary": "분석 화면에서 확인한 결측의 데이터 종류, 대상, 기간과 owning collection action을 찾습니다.",
        "reference_item_ids": ["journey.data_preparation", "playbook.ingestion_data_missing"],
        "next_checks": [
            "원래 분석 화면에서 부족한 데이터 종류와 대상을 먼저 확인합니다.",
            "필요한 provider와 기간에 해당하는 bounded action만 선택합니다.",
            "수집 후 원래 분석 화면으로 돌아가 결과를 다시 확인합니다.",
        ],
        "boundaries": [
            "Reference help는 수집 작업을 실행하지 않습니다.",
            "무관한 전체 수집보다 확인된 결측 범위를 우선합니다.",
        ],
        "links": [
            {"label": "데이터 준비 흐름", "target": "/reference", "item_id": "journey.data_preparation"},
            {"label": "자료 부족 해결", "target": "/reference", "item_id": "playbook.ingestion_data_missing"},
        ],
    },
    {
        "surface_key": "backtest_analysis",
        "surface": "Backtest Analysis",
        "title": "후보 source를 만들 때 막히면",
        "summary": "전략과 mix 결과가 어떤 다음 단계로 이어지는지 확인합니다.",
        "reference_item_ids": ["journey.candidate_creation", "concept.saved_portfolio", "concept.data_trust"],
        "next_checks": [
            "실행 결과와 Data Trust를 먼저 확인합니다.",
            "저장 setup인지 Practical Validation source인지 구분합니다.",
            "후보 생성은 Final Review selected decision을 대체하지 않습니다.",
        ],
        "boundaries": [
            "후보 source 생성 화면이며 live approval, broker order, auto rebalance를 만들지 않습니다.",
            "Saved Portfolio는 재사용 setup이고 validation 결과나 selected decision이 아닙니다.",
        ],
        "links": [
            {"label": "후보 생성 흐름", "target": "/reference", "item_id": "journey.candidate_creation"},
            {"label": "Saved Portfolio 의미", "target": "/reference", "item_id": "concept.saved_portfolio"},
        ],
    },
    {
        "surface_key": "practical_validation",
        "surface": "Practical Validation",
        "title": "검증 row가 왜 막혔는지 볼 때",
        "summary": "NOT_RUN, REVIEW, BLOCKED가 pass인지 blocker인지 구분하고 evidence owner를 찾습니다.",
        "reference_item_ids": [
            "status.not_run",
            "status.review",
            "status.blocked",
            "playbook.practical_validation_not_run",
        ],
        "next_checks": [
            "NOT_RUN은 pass가 아니라 실행되지 않았거나 evidence가 없는 상태입니다.",
            "Provider Coverage가 partial 또는 proxy이면 review evidence로 해석합니다.",
            "blocker가 있으면 자료 보강과 replay 후 validation을 다시 저장합니다.",
        ],
        "boundaries": [
            "Practical Validation은 검증 근거 화면이며 최종 사용자 판단은 Final Review가 소유합니다.",
            "provider gap 수집은 명시 버튼으로만 실행되며 help box는 아무 작업도 실행하지 않습니다.",
        ],
        "links": [
            {"label": "NOT_RUN 의미 확인", "target": "/reference", "item_id": "status.not_run"},
            {
                "label": "NOT_RUN 해결 순서",
                "target": "/reference",
                "item_id": "playbook.practical_validation_not_run",
            },
        ],
    },
    {
        "surface_key": "final_review",
        "surface": "Final Review",
        "title": "모니터링 후보로 저장해도 되는지 볼 때",
        "summary": "selected-route gate, decision record, Portfolio Monitoring handoff의 의미를 확인합니다.",
        "reference_item_ids": [
            "journey.validation_decision",
            "concept.selected_route_gate",
            "playbook.final_review_candidate_missing",
        ],
        "next_checks": [
            "Practical Validation Gate를 통과한 후보만 Final Review 검토 대상입니다.",
            "Selected-route Gate가 blocked이면 정식 선정 저장으로 진행하지 않습니다.",
            "저장된 selected decision은 Portfolio Monitoring에서 read-only로 다시 읽습니다.",
        ],
        "boundaries": [
            "모니터링 후보 선정 기록은 broker order가 아닙니다.",
            "Final Review는 live approval, account sync, auto rebalance를 만들지 않습니다.",
        ],
        "links": [
            {
                "label": "Selected-route Gate 의미",
                "target": "/reference",
                "item_id": "concept.selected_route_gate",
            },
            {
                "label": "후보가 안 보일 때",
                "target": "/reference",
                "item_id": "playbook.final_review_candidate_missing",
            },
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
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    return sorted(duplicates)


def build_reference_contextual_help_drift_report() -> dict[str, Any]:
    """Return Streamlit-free referential integrity for contextual Reference help."""
    catalog = get_reference_contextual_help_catalog()
    reference_item_ids = {str(item["id"]) for item in get_reference_center_items()}
    missing_reference_item_ids: list[dict[str, str]] = []
    invalid_links: list[dict[str, str]] = []
    contextual_item_ids: set[str] = set()
    link_count = 0

    for item in catalog:
        surface_key = str(item.get("surface_key") or "").strip()
        for item_id in list(item.get("reference_item_ids") or []):
            normalized_item_id = str(item_id or "").strip()
            contextual_item_ids.add(normalized_item_id)
            if normalized_item_id not in reference_item_ids:
                missing_reference_item_ids.append(
                    {"surface_key": surface_key, "item_id": normalized_item_id}
                )

        for link in list(item.get("links") or []):
            link_count += 1
            target = str(link.get("target") or "").strip()
            item_id = str(link.get("item_id") or "").strip()
            contextual_item_ids.add(item_id)
            if target not in ALLOWED_REFERENCE_HELP_TARGETS or item_id not in reference_item_ids:
                invalid_links.append(
                    {"surface_key": surface_key, "target": target, "item_id": item_id}
                )
            if item_id not in reference_item_ids:
                missing_reference_item_ids.append(
                    {"surface_key": surface_key, "item_id": item_id}
                )

    duplicate_surface_keys = _duplicate_surface_keys(catalog)
    has_issues = any([missing_reference_item_ids, invalid_links, duplicate_surface_keys])
    return {
        "status": "REVIEW" if has_issues else "PASS",
        "metrics": {
            "surface_count": len(catalog),
            "reference_item_count": len(contextual_item_ids),
            "link_count": link_count,
        },
        "missing_reference_item_ids": missing_reference_item_ids,
        "invalid_links": invalid_links,
        "duplicate_surface_keys": duplicate_surface_keys,
    }
