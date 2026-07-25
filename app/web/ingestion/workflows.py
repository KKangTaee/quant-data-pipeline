"""Pure product workflow catalog for Data Operations."""

from __future__ import annotations

from typing import Any

from app.web.ingestion.registry import (
    INGESTION_ACTION_REGISTRY,
    _active_ingestion_actions,
)


DATA_OPERATIONS_SECTION_PREPARATION = "데이터 준비"
DATA_OPERATIONS_SECTION_IMPORTS = "공식 파일"
DATA_OPERATIONS_SECTION_RECOVERY = "문제 복구"
DATA_OPERATIONS_SECTION_HISTORY = "실행 이력"
DATA_OPERATIONS_SECTION_ADVANCED = "고급 도구"
DATA_OPERATIONS_SECTIONS = (
    DATA_OPERATIONS_SECTION_PREPARATION,
    DATA_OPERATIONS_SECTION_IMPORTS,
    DATA_OPERATIONS_SECTION_RECOVERY,
    DATA_OPERATIONS_SECTION_HISTORY,
    DATA_OPERATIONS_SECTION_ADVANCED,
)

DATA_OPERATIONS_WORKFLOWS: tuple[dict[str, Any], ...] = (
    {
        "id": "market_research",
        "title": "Market Research 데이터 준비",
        "purpose": "시장·종목 리서치가 읽는 가격, 선물, 심리와 일정을 갱신합니다.",
        "included": "미국 종목 기준 · 가격 · 선물 · 심리 · 일정",
        "cadence": "가격은 거래일 기준, 나머지는 자료 발표 주기에 맞춰 실행",
        "actions": (
            "refresh_nyse_listing_universe",
            "daily_market_update",
            "metadata_refresh",
            "collect_futures_ohlcv",
            "collect_market_sentiment",
            "collect_fomc_calendar",
            "collect_macro_calendar",
            "collect_market_structure_calendar",
            "collect_earnings_calendar",
        ),
    },
    {
        "id": "portfolio_lab",
        "title": "Portfolio Lab 데이터 준비",
        "purpose": "백테스트와 factor 계산이 읽는 가격과 EDGAR 재무제표를 준비합니다.",
        "included": "가격 · EDGAR 재무제표 · 종목 메타데이터",
        "cadence": "새 분석 전 또는 데이터 누락이 확인됐을 때 실행",
        "actions": (
            "daily_market_update",
            "extended_statement_refresh",
            "metadata_refresh",
        ),
    },
    {
        "id": "institutional_holdings",
        "title": "Institutional Holdings 데이터 준비",
        "purpose": "SEC 13F 분기 데이터와 안전한 ticker identity 연결을 준비합니다.",
        "included": "SEC 13F dataset · OpenFIGI identifier mapping",
        "cadence": "SEC 분기 dataset 공개 이후 실행",
        "actions": (
            "collect_sec_13f_dataset",
            "collect_sec_13f_identifier_mappings",
        ),
    },
    {
        "id": "practical_validation",
        "title": "Practical Validation 데이터 보강",
        "purpose": "ETF 운용성·구성, macro와 lifecycle 검증 근거를 보강합니다.",
        "included": "ETF provider · FRED · listing/delisting evidence",
        "cadence": "검증 후보의 근거가 부족하거나 stale할 때 실행",
        "actions": (
            "discover_etf_provider_source_map",
            "collect_etf_operability_provider",
            "collect_etf_holdings_exposure",
            "collect_macro_market_context",
            "collect_sec_form25_delistings",
            "collect_symbol_directory_snapshots",
            "collect_sec_company_ticker_crosscheck",
            "collect_computed_snapshot_lifecycle",
        ),
    },
)

OFFICIAL_IMPORT_ACTIONS = (
    "import_sp500_index_earnings_xlsx",
    "import_bls_macro_calendar_ics",
)
RECOVERY_DIAGNOSTIC_ACTIONS = (
    "diagnose_price_stale",
    "diagnose_statement_universe_coverage",
    "diagnose_statement_coverage",
    "inspect_statement_pit",
)
RECOVERY_MANUAL_ACTIONS = (
    "collect_ohlcv",
    "collect_asset_profiles",
    "collect_financial_statements",
    "rebuild_statement_shadow",
)


def _build_action_workflow_ownership() -> dict[str, tuple[str, ...]]:
    ownership: dict[str, list[str]] = {}
    for workflow in DATA_OPERATIONS_WORKFLOWS:
        workflow_id = str(workflow["id"])
        for action in workflow["actions"]:
            ownership.setdefault(str(action), []).append(workflow_id)
    for action in OFFICIAL_IMPORT_ACTIONS:
        ownership.setdefault(action, []).append("official_import")
    for action in RECOVERY_DIAGNOSTIC_ACTIONS:
        ownership.setdefault(action, []).append("recovery_diagnosis")
    for action in RECOVERY_MANUAL_ACTIONS:
        ownership.setdefault(action, []).append("recovery_manual")
    return {action: tuple(owners) for action, owners in ownership.items()}


ACTION_WORKFLOW_OWNERSHIP = _build_action_workflow_ownership()


def workflow_for_id(workflow_id: str) -> dict[str, Any]:
    """Return one consumer workflow or fail closed for an unknown id."""

    for workflow in DATA_OPERATIONS_WORKFLOWS:
        if workflow["id"] == workflow_id:
            return workflow
    raise KeyError(f"Unknown Data Operations workflow: {workflow_id}")


def action_definition(action: str) -> dict[str, Any]:
    """Return an active action definition without promoting compatibility actions."""

    definition = INGESTION_ACTION_REGISTRY.get(str(action))
    if not definition or definition.get("active") is not True:
        raise KeyError(f"Unknown or inactive Data Operations action: {action}")
    return definition


def validate_workflow_inventory() -> dict[str, Any]:
    """Compare the product workflow catalog with the active execution registry."""

    active_actions = set(_active_ingestion_actions())
    owned_actions = set(ACTION_WORKFLOW_OWNERSHIP)
    return {
        "active_action_count": len(active_actions),
        "owned_action_count": len(owned_actions),
        "unowned_actions": tuple(sorted(active_actions - owned_actions)),
        "unknown_actions": tuple(sorted(owned_actions - active_actions)),
    }


__all__ = [
    "ACTION_WORKFLOW_OWNERSHIP",
    "DATA_OPERATIONS_SECTION_ADVANCED",
    "DATA_OPERATIONS_SECTION_HISTORY",
    "DATA_OPERATIONS_SECTION_IMPORTS",
    "DATA_OPERATIONS_SECTION_PREPARATION",
    "DATA_OPERATIONS_SECTION_RECOVERY",
    "DATA_OPERATIONS_SECTIONS",
    "DATA_OPERATIONS_WORKFLOWS",
    "OFFICIAL_IMPORT_ACTIONS",
    "RECOVERY_DIAGNOSTIC_ACTIONS",
    "RECOVERY_MANUAL_ACTIONS",
    "action_definition",
    "validate_workflow_inventory",
    "workflow_for_id",
]
