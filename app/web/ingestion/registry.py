"""Action registry and section metadata for Workspace > Ingestion."""

from __future__ import annotations

from typing import Any

INGESTION_COLLECTION_OPERATIONAL = "일상 운영 / 검증 데이터"
INGESTION_COLLECTION_MANUAL = "수동 복구 / 진단"
INGESTION_COLLECTION_RECORDS = "실행 기록 / 결과"
INGESTION_COLLECTION_SECTIONS = (
    INGESTION_COLLECTION_OPERATIONAL,
    INGESTION_COLLECTION_MANUAL,
    INGESTION_COLLECTION_RECORDS,
)
MANUAL_COLLECTION_ACTIONS = {
    "collect_ohlcv",
    "collect_asset_profiles",
    "collect_financial_statements",
    "rebuild_statement_shadow",
}
COLLECTION_ENTRY_RELATIONSHIPS = {
    "daily_market_update": (
        "운영용 가격 갱신 entry입니다. 같은 OHLCV writer를 쓰지만, 수동 가격 이력 수집보다 "
        "운영 universe / execution profile / 결과 해석을 먼저 보게 합니다."
    ),
    "collect_ohlcv": (
        "복구용 수동 가격 이력 수집 entry입니다. 일상 운영 전체 갱신보다 의심 심볼과 기간을 좁혀 실행할 때 사용합니다."
    ),
    "metadata_refresh": (
        "운영용 종목 메타데이터 업데이트 entry입니다. 수동 자산 프로필 수집과 같은 asset profile collector를 쓰지만, "
        "stock / ETF 운영 scope를 갱신하는 흐름입니다."
    ),
    "collect_asset_profiles": (
        "복구용 수동 자산 프로필 수집 entry입니다. metadata refresh와 같은 저장 테이블을 쓰되 필요한 kind만 좁혀 재수집합니다."
    ),
    "extended_statement_refresh": (
        "운영용 EDGAR annual 재무제표 갱신 entry입니다. raw statement 수집 뒤 statement shadow fundamentals / factors까지 이어서 준비합니다."
    ),
    "collect_financial_statements": (
        "복구용 상세 재무제표 수동 수집 entry입니다. EDGAR annual 운영 refresh보다 낮은 수준의 raw ledger 재수집입니다."
    ),
}
INGESTION_ACTION_REGISTRY: dict[str, dict[str, Any]] = {
    "daily_market_update": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_price.nyse_price_history"],
        "progress": "batch",
    },
    "collect_futures_ohlcv": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_price.futures_ohlcv",
            "finance_meta.futures_instrument",
            "finance_meta.futures_market_monitor_run",
        ],
        "progress": "stage",
    },
    "collect_market_sentiment": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.macro_series_observation"],
        "progress": "stage",
    },
    "extended_statement_refresh": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_fundamental.nyse_financial_statement_filings",
            "finance_fundamental.nyse_financial_statement_labels",
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "progress": "batch_and_stage",
    },
    "metadata_refresh": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.nyse_asset_profile"],
        "progress": "stage",
    },
    "collect_fomc_calendar": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational_low_frequency",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.market_event_calendar"],
        "progress": "stage",
    },
    "collect_macro_calendar": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational_low_frequency",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.market_event_calendar"],
        "progress": "stage",
    },
    "collect_market_structure_calendar": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational_low_frequency",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.market_event_calendar"],
        "progress": "stage",
    },
    "import_bls_macro_calendar_ics": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "manual_official_file_import",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.market_event_calendar"],
        "progress": "stage",
    },
    "import_sp500_index_earnings_xlsx": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "manual_official_file_import",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.sp500_index_earnings"],
        "progress": "none",
    },
    "collect_earnings_calendar": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational_low_frequency",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.market_event_calendar"],
        "progress": "stage",
    },
    "discover_etf_provider_source_map": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.etf_provider_source_map"],
        "progress": "stage",
    },
    "collect_etf_operability_provider": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.etf_operability_snapshot"],
        "progress": "stage",
    },
    "collect_etf_holdings_exposure": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_meta.etf_holdings_snapshot",
            "finance_meta.etf_exposure_snapshot",
        ],
        "progress": "stage",
    },
    "collect_macro_market_context": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.macro_series_observation"],
        "progress": "stage",
    },
    "collect_sec_form25_delistings": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.nyse_symbol_lifecycle"],
        "progress": "stage",
    },
    "collect_sec_13f_dataset": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational_low_frequency",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_meta.institutional_13f_manager",
            "finance_meta.institutional_13f_filing",
            "finance_meta.institutional_13f_holding",
            "finance_meta.institutional_13f_cusip_symbol_map",
            "finance_meta.institutional_13f_refresh_status",
        ],
        "progress": "stage",
    },
    "collect_symbol_directory_snapshots": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.nyse_symbol_lifecycle"],
        "progress": "stage",
    },
    "collect_sec_company_ticker_crosscheck": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.nyse_symbol_lifecycle"],
        "progress": "stage",
    },
    "collect_computed_snapshot_lifecycle": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "operational",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.nyse_symbol_lifecycle"],
        "progress": "stage",
    },
    "collect_ohlcv": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "manual",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_price.nyse_price_history"],
        "progress": "batch",
    },
    "collect_asset_profiles": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "manual",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.nyse_asset_profile"],
        "progress": "stage",
    },
    "collect_financial_statements": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "manual",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_fundamental.nyse_financial_statement_filings",
            "finance_fundamental.nyse_financial_statement_labels",
            "finance_fundamental.nyse_financial_statement_values",
        ],
        "progress": "batch",
    },
    "rebuild_statement_shadow": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "manual",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "progress": "stage",
    },
    "diagnose_price_stale": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "diagnostic",
        "active": True,
        "compatibility": False,
        "write_behavior": "read_only",
        "target_tables": ["finance_price.nyse_price_history", "finance_meta.nyse_asset_profile"],
        "progress": "stage",
    },
    "diagnose_statement_universe_coverage": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "diagnostic",
        "active": True,
        "compatibility": False,
        "write_behavior": "read_only",
        "target_tables": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "progress": "stage",
    },
    "diagnose_statement_coverage": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "diagnostic",
        "active": True,
        "compatibility": False,
        "write_behavior": "read_only",
        "target_tables": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
        ],
        "progress": "stage",
    },
    "inspect_statement_pit": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "diagnostic",
        "active": True,
        "compatibility": False,
        "write_behavior": "read_only",
        "target_tables": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
        ],
        "progress": "stage",
    },
    "pipeline_core_market_data": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "compatibility",
        "active": False,
        "compatibility": True,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_price.nyse_price_history",
            "finance_fundamental.nyse_fundamentals",
            "finance_fundamental.nyse_factors",
        ],
        "progress": "batch_and_stage",
    },
    "weekly_fundamental_refresh": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "compatibility",
        "active": False,
        "compatibility": True,
        "write_behavior": "db_write",
        "target_tables": [
            "finance_fundamental.nyse_fundamentals",
            "finance_fundamental.nyse_factors",
        ],
        "progress": "stage",
    },
    "collect_fundamentals": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "compatibility",
        "active": False,
        "compatibility": True,
        "write_behavior": "db_write",
        "target_tables": ["finance_fundamental.nyse_fundamentals"],
        "progress": "none",
    },
    "calculate_factors": {
        "section": INGESTION_COLLECTION_MANUAL,
        "mode": "compatibility",
        "active": False,
        "compatibility": True,
        "write_behavior": "db_write",
        "target_tables": ["finance_fundamental.nyse_factors"],
        "progress": "none",
    },
}


def _active_ingestion_actions(*, section: str | None = None) -> tuple[str, ...]:
    return tuple(
        action
        for action, definition in INGESTION_ACTION_REGISTRY.items()
        if definition.get("active") is True and (section is None or definition.get("section") == section)
    )


def _compatibility_ingestion_actions() -> tuple[str, ...]:
    return tuple(
        action
        for action, definition in INGESTION_ACTION_REGISTRY.items()
        if definition.get("compatibility") is True
    )


def _is_compatibility_ingestion_action(action: str | None) -> bool:
    return str(action or "") in _compatibility_ingestion_actions()


def _infer_ingestion_collection_section(job: dict[str, Any] | None) -> str:
    if not job:
        return INGESTION_COLLECTION_OPERATIONAL
    section = job.get("collection_section") or (job.get("run_metadata") or {}).get("collection_section")
    if section in INGESTION_COLLECTION_SECTIONS:
        return str(section)
    action_definition = INGESTION_ACTION_REGISTRY.get(str(job.get("action") or ""))
    registry_section = action_definition.get("section") if action_definition else None
    if registry_section in INGESTION_COLLECTION_SECTIONS:
        return str(registry_section)
    if job.get("action") in MANUAL_COLLECTION_ACTIONS:
        return INGESTION_COLLECTION_MANUAL
    return INGESTION_COLLECTION_OPERATIONAL


active_ingestion_actions = _active_ingestion_actions
compatibility_ingestion_actions = _compatibility_ingestion_actions
is_compatibility_ingestion_action = _is_compatibility_ingestion_action
infer_ingestion_collection_section = _infer_ingestion_collection_section
