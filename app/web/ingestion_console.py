"""Streamlit render and session-state boundary for Workspace > Ingestion."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from app.jobs.ingestion_jobs import (
    run_collect_computed_snapshot_lifecycle,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_futures_ohlcv,
    run_collect_macro_calendar,
    run_collect_market_sentiment,
    run_collect_sec_company_ticker_crosscheck,
    run_import_bls_macro_calendar_ics,
    run_collect_etf_holdings_exposure,
    run_collect_etf_operability_provider,
    run_collect_sec_form25_delistings,
    run_collect_symbol_directory_snapshots,
    run_discover_etf_provider_source_map,
    run_collect_macro_market_context,
    run_daily_market_update,
    run_extended_statement_refresh,
    run_rebuild_statement_shadow,
    run_metadata_refresh,
    run_collect_asset_profiles,
    run_collect_financial_statements,
    run_calculate_factors,
    run_collect_fundamentals,
    run_collect_ohlcv,
    run_pipeline_core_market_data,
    run_weekly_fundamental_refresh,
)
from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS
from app.jobs.result_artifacts import write_run_artifacts
from app.jobs.preflight_checks import (
    check_asset_profile_prerequisites,
    check_symbol_input,
)
from app.jobs.run_history import (
    HISTORY_FILE,
    append_run_history,
    estimate_duration_from_history,
    load_run_history,
)
from app.jobs.symbol_sources import resolve_symbol_source
from app.jobs.symbol_sources import filter_non_plain_symbols
from app.services.ingestion_diagnostics import (
    load_price_window_preflight_summary,
    run_price_stale_diagnosis,
    run_statement_coverage_diagnosis,
    run_statement_pit_inspection,
    run_statement_universe_coverage_qa,
)
from app.web.backtest_common import QUALITY_STRICT_PRESETS, clear_backtest_preview_caches
from app.workspace_paths import PROJECT_ROOT


JobResult = dict[str, Any]
LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"
_runtime_marker = "unknown"
_runtime_loaded_at: datetime | None = None
_runtime_git_sha: str | None = None
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
    "import_bls_macro_calendar_ics": {
        "section": INGESTION_COLLECTION_OPERATIONAL,
        "mode": "manual_official_file_import",
        "active": True,
        "compatibility": False,
        "write_behavior": "db_write",
        "target_tables": ["finance_meta.market_event_calendar"],
        "progress": "stage",
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


def _set_runtime_context(*, runtime_marker: str, loaded_at: datetime, git_sha: str | None) -> None:
    global _runtime_marker, _runtime_loaded_at, _runtime_git_sha
    _runtime_marker = runtime_marker
    _runtime_loaded_at = loaded_at
    _runtime_git_sha = git_sha


def _runtime_loaded_at_text() -> str:
    if _runtime_loaded_at is None:
        return "unknown"
    return _runtime_loaded_at.strftime("%Y-%m-%d %H:%M:%S")


def _runtime_metadata() -> dict[str, Any]:
    return {
        "runtime_marker": _runtime_marker,
        "runtime_loaded_at": _runtime_loaded_at_text(),
        "git_sha": _runtime_git_sha,
    }


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


def _format_job_elapsed(job: dict[str, Any] | None, *, now: datetime | None = None) -> str:
    started_at = (job or {}).get("ui_started_at")
    if isinstance(started_at, datetime):
        started_at_dt = started_at
    elif started_at:
        try:
            started_at_dt = datetime.fromisoformat(str(started_at))
        except ValueError:
            return "00:00:00"
    else:
        return "00:00:00"

    elapsed_seconds = max(int(((now or datetime.now()) - started_at_dt).total_seconds()), 0)
    hours, remainder = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


JOB_GUIDE: dict[str, dict[str, Any]] = {
    "daily_market_update": {
        "title": "일별 가격 업데이트",
        "purpose": "선택한 운용 universe의 OHLCV, 배당, 분할 가격 이력을 갱신합니다.",
        "targets": ["finance_price.nyse_price_history"],
        "used_by": ["Backtest Analysis", "Data Coverage Audit", "Selected Dashboard symbol freshness"],
        "caveats": [
            "무료 provider no-data와 rate limit이 발생할 수 있습니다.",
            "요청 기간 대비 실제 DB coverage와 최신 거래일을 결과에서 확인해야 합니다.",
        ],
        "next_action": "부분 성공이면 Price Stale Diagnosis로 provider gap과 DB 수집 누락을 분리하세요.",
    },
    "weekly_fundamental_refresh": {
        "title": "Archived legacy broad yfinance fundamentals / factors",
        "purpose": (
            "Archived legacy broad yfinance compatibility path for historical nyse_fundamentals / nyse_factors replay; "
            "not an active financial statement refresh workflow."
        ),
        "targets": ["finance_fundamental.nyse_fundamentals", "finance_fundamental.nyse_factors"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": [
            "broad fundamentals / factors는 strict filing-time PIT source가 아닙니다.",
            "strict annual backtests use EDGAR statement shadow.",
        ],
        "next_action": "새 financial statement coverage가 필요하면 EDGAR annual 재무제표 갱신을 먼저 실행하세요.",
    },
    "extended_statement_refresh": {
        "title": "EDGAR annual 재무제표 갱신",
        "purpose": (
            "EDGAR detailed statement ledger를 수집하고 statement shadow fundamentals / factors를 재구성하는 "
            "primary financial statement refresh입니다."
        ),
        "targets": [
            "finance_fundamental.nyse_financial_statement_filings",
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "used_by": ["Strict annual factor runtime", "Market Movers financial snapshot", "Statement PIT inspection"],
        "caveats": [
            "period_end와 accepted_at / available_at를 구분해서 해석해야 합니다.",
            "SEC fair access를 위해 User-Agent와 pacing을 지켜야 합니다.",
        ],
        "next_action": "부분 성공이면 Statement Coverage Diagnosis로 raw 누락과 shadow rebuild 대상을 분리하세요.",
    },
    "metadata_refresh": {
        "title": "종목 메타데이터 업데이트",
        "purpose": "현재 NYSE stock / ETF universe의 asset profile과 ETF current-operability bridge fields를 갱신합니다.",
        "targets": ["finance_meta.nyse_asset_profile"],
        "used_by": ["Universe filter", "ETF operability bridge", "Overview Top1000 / Top2000 universe"],
        "caveats": ["asset profile은 current snapshot이며 historical universe proof가 아닙니다."],
        "next_action": "Profile filter 결과가 달라졌다면 가격 / provider snapshot도 이어서 갱신하세요.",
    },
    "collect_fomc_calendar": {
        "title": "FOMC 일정 수집",
        "purpose": "Federal Reserve 공식 calendar에서 FOMC meeting 일정을 수집합니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["event row는 수집 시점의 calendar snapshot입니다."],
        "next_action": "Overview Events에서 일정 fresh 상태를 확인하세요.",
    },
    "collect_macro_calendar": {
        "title": "공식 매크로 발표 일정 수집",
        "purpose": "BLS / BEA 공식 release schedule에서 CPI, PPI, Jobs, GDP 발표 일정을 수집합니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["BLS 자동 요청은 차단될 수 있으며, 실패 시 BLS .ics import를 사용합니다."],
        "next_action": "partial_success면 실패 source를 확인하고 BLS .ics fallback을 실행하세요.",
    },
    "import_bls_macro_calendar_ics": {
        "title": "BLS 공식 .ics 일정 가져오기",
        "purpose": "브라우저로 받은 BLS 공식 calendar 파일에서 CPI / PPI / Jobs 발표 일정을 가져옵니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["업로드한 파일의 source year 범위와 최신성을 확인해야 합니다."],
        "next_action": "Overview Events에서 BLS row가 보강됐는지 확인하세요.",
    },
    "collect_earnings_calendar": {
        "title": "실적 발표 예상 일정 수집",
        "purpose": "bounded symbol set의 upcoming earnings estimate를 yfinance와 선택적 Nasdaq cross-check로 수집합니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["무료 provider estimate이며 공식 확정 IR 일정이 아닙니다."],
        "next_action": "missing / failed symbol은 Earnings Diagnostics에서 reason을 확인하세요.",
    },
    "collect_futures_ohlcv": {
        "title": "선물 1분봉 OHLCV 수집",
        "purpose": "Overview Futures Monitor에서 읽을 주요 선물 OHLCV 캔들을 yfinance pilot source로 수집합니다.",
        "targets": [
            "finance_price.futures_ohlcv",
            "finance_meta.futures_instrument",
            "finance_meta.futures_market_monitor_run",
        ],
        "used_by": ["Workspace > Overview > Futures Monitor", "Workspace > Overview > Data Health"],
        "caveats": [
            "무료 provider pilot source이며 exchange-grade realtime feed가 아닙니다.",
            "provider 실패 / stale 상태는 Overview에서 그대로 표시합니다.",
        ],
        "next_action": "부분 성공이면 failed symbols를 줄여 다시 실행하거나 provider 상태를 확인하세요.",
    },
    "collect_market_sentiment": {
        "title": "시장 심리 수집",
        "purpose": "CNN Fear & Greed와 AAII Sentiment Survey를 수집해 Overview Sentiment에서 읽을 시장 심리 context를 저장합니다.",
        "targets": ["finance_meta.macro_series_observation"],
        "used_by": ["Workspace > Overview > Sentiment", "Workspace > Overview > Data Health"],
        "caveats": [
            "시장 심리는 trade signal이나 live approval이 아닙니다.",
            "CNN / AAII source 차단 또는 stale 상태는 Overview에서 그대로 표시합니다.",
        ],
        "next_action": "partial_success이면 failed source를 확인하고 다시 실행하세요.",
    },
    "discover_etf_provider_source_map": {
        "title": "ETF 공식 소스 매핑 발견",
        "purpose": "ETF별 공식 운용사 endpoint와 parser mapping을 찾아 verified cache로 저장합니다.",
        "targets": ["finance_meta.etf_provider_source_map"],
        "used_by": ["ETF operability / holdings / exposure collection", "Provider Data Gaps"],
        "caveats": ["provider 사이트 구조가 바뀌면 verified row도 다시 확인해야 합니다."],
        "next_action": "verified row가 부족하면 ETF provider connector 보강 후보로 기록하세요.",
    },
    "collect_etf_operability_provider": {
        "title": "ETF 운용성 스냅샷 수집",
        "purpose": "ETF 비용, 규모, 유동성, spread, premium/discount 관련 snapshot을 수집합니다.",
        "targets": ["finance_meta.etf_operability_snapshot"],
        "used_by": ["Practical Validation operability / cost / liquidity"],
        "caveats": ["current snapshot이며 과거 특정 시점의 PIT 운용성 truth가 아닙니다."],
        "next_action": "coverage gap이 있으면 source map 또는 DB bridge 수집 경로를 확인하세요.",
    },
    "collect_etf_holdings_exposure": {
        "title": "ETF 구성 / 노출 스냅샷 수집",
        "purpose": "ETF holdings row와 asset / sector / country / currency exposure summary를 수집합니다.",
        "targets": ["finance_meta.etf_holdings_snapshot", "finance_meta.etf_exposure_snapshot"],
        "used_by": ["Practical Validation asset allocation / concentration / overlap"],
        "caveats": ["current holdings snapshot이며 과거 holdings PIT truth가 아닙니다."],
        "next_action": "partial_success이면 unsupported parser와 missing ETF를 먼저 확인하세요.",
    },
    "collect_macro_market_context": {
        "title": "FRED 시장환경 수집",
        "purpose": "VIX, yield curve, credit spread 같은 validation용 market-context series를 수집합니다.",
        "targets": ["finance_meta.macro_series_observation"],
        "used_by": ["Practical Validation macro / regime / risk-on-off diagnostics"],
        "caveats": ["FRED observation date 기준이며 ALFRED vintage PIT는 아닙니다."],
        "next_action": "Macro freshness가 stale이면 동일 series와 기간으로 다시 수집하세요.",
    },
    "collect_sec_form25_delistings": {
        "title": "SEC Form 25 상폐 근거 수집",
        "purpose": "SEC EDGAR Form 25 / 25-NSE filing metadata로 delisting evidence를 저장합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit survivorship / delisting control"],
        "caveats": ["Form 25 부재는 active listing proof가 아닙니다."],
        "next_action": "unmapped / no Form 25 symbol은 별도 historical listing source가 필요한지 검토하세요.",
    },
    "collect_symbol_directory_snapshots": {
        "title": "Nasdaq 상장 관찰치 수집",
        "purpose": "Nasdaq public Symbol Directory current files를 partial listing_observed evidence로 저장합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit lifecycle evidence"],
        "caveats": ["current listing snapshot이며 historical membership PASS 근거가 아닙니다."],
        "next_action": "반복 관찰이 쌓이면 computed lifecycle 요약을 실행하세요.",
    },
    "collect_sec_company_ticker_crosscheck": {
        "title": "SEC CIK / 티커 교차확인",
        "purpose": "SEC current CIK / ticker / exchange association을 identity cross-check evidence로 저장합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit lifecycle evidence"],
        "caveats": ["current identity row이며 delisting이나 historical membership proof가 아닙니다."],
        "next_action": "requested missing symbol은 SEC ticker mapping 한계를 따로 확인하세요.",
    },
    "collect_computed_snapshot_lifecycle": {
        "title": "반복 관찰 lifecycle 요약",
        "purpose": "기존 current snapshot rows의 반복 관찰 window를 보수적인 partial lifecycle evidence로 요약합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit lifecycle evidence"],
        "caveats": ["absence를 delisting proof로 해석하지 않으며 PASS eligible evidence가 아닙니다."],
        "next_action": "actual historical membership source가 필요한 symbol은 별도 source review로 넘기세요.",
    },
    "pipeline_core_market_data": {
        "title": "Archived broad core market-data pipeline",
        "purpose": "Archived legacy compatibility job that chained OHLCV, broad yfinance fundamentals, and broad factor calculation.",
        "targets": ["finance_price.nyse_price_history", "finance_fundamental.nyse_fundamentals", "finance_fundamental.nyse_factors"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": ["financial statement canonical refresh는 EDGAR annual path입니다."],
        "next_action": "새 재무제표 / factor 준비는 EDGAR annual refresh와 statement shadow path를 사용하세요.",
    },
    "collect_ohlcv": {
        "title": "가격 이력 수동 수집",
        "purpose": "선택한 symbol과 기간의 OHLCV, dividend, split row를 수동으로 수집합니다.",
        "targets": ["finance_price.nyse_price_history"],
        "used_by": ["Backtest Analysis", "freshness diagnostics"],
        "caveats": ["요청 범위와 실제 provider 응답 범위가 다를 수 있습니다."],
        "next_action": "누락 symbol은 Price Stale Diagnosis로 원인을 분류하세요.",
    },
    "diagnose_price_stale": {
        "title": "가격 stale 원인 진단",
        "purpose": "DB latest date, provider probe, asset profile 상태를 읽어 가격 stale 원인을 분리합니다.",
        "targets": ["finance_price.nyse_price_history", "finance_meta.nyse_asset_profile"],
        "used_by": ["Manual recovery", "Data Coverage Audit", "Price Freshness Preflight"],
        "caveats": ["읽기 전용 진단이며 새 가격 row를 저장하지 않습니다."],
        "next_action": "local ingestion gap이면 가격 이력 수동 수집으로 기간을 좁혀 보강하세요.",
    },
    "diagnose_statement_universe_coverage": {
        "title": "재무제표 universe coverage QA",
        "purpose": "Top1000 / Top2000 / Nasdaq 등 universe 단위로 EDGAR statement coverage 원인을 점검합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "used_by": ["Strict statement coverage review", "Statement recovery planning"],
        "caveats": ["읽기 전용 QA이며 paid provider나 yfinance statement data를 primary source로 읽지 않습니다."],
        "next_action": "raw present / shadow missing이면 shadow rebuild, raw missing이면 EDGAR refresh로 분리하세요.",
    },
    "diagnose_statement_coverage": {
        "title": "재무제표 coverage 원인 진단",
        "purpose": "선택 symbol의 raw statement, shadow table, live EDGAR sample 상태를 비교합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
        ],
        "used_by": ["Manual statement recovery", "PIT inspection"],
        "caveats": ["읽기 전용 진단이며 EDGAR sample 조회는 source shape 확인 목적입니다."],
        "next_action": "source-present raw-missing이면 EDGAR refresh, raw-present shadow-missing이면 shadow rebuild를 실행하세요.",
    },
    "inspect_statement_pit": {
        "title": "재무제표 PIT inspection",
        "purpose": "저장된 statement timing row와 EDGAR source payload shape를 UI에서 점검합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
        ],
        "used_by": ["Point-in-time validation", "Statement source review"],
        "caveats": ["읽기 전용 inspection이며 live source sample은 대표 payload 확인용입니다."],
        "next_action": "accepted_at / available_at 의미가 어긋나면 factor PIT 변환 경계를 먼저 점검하세요.",
    },
    "collect_fundamentals": {
        "title": "Archived broad fundamentals manual collection",
        "purpose": "Archived legacy compatibility job for broad yfinance normalized fundamentals.",
        "targets": ["finance_fundamental.nyse_fundamentals"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": ["canonical financial statement source가 아닙니다."],
        "next_action": "새 재무제표 source가 필요하면 EDGAR annual refresh를 사용하세요.",
    },
    "calculate_factors": {
        "title": "Archived broad factor manual calculation",
        "purpose": "Archived legacy compatibility job for calculating broad factors from nyse_fundamentals.",
        "targets": ["finance_fundamental.nyse_factors"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": ["strict annual strategies use statement shadow factors."],
        "next_action": "새 factor 준비는 statement shadow factor path를 우선 사용하세요.",
    },
    "collect_asset_profiles": {
        "title": "자산 프로필 수동 수집",
        "purpose": "NYSE universe table을 기준으로 stock / ETF profile metadata를 수집합니다.",
        "targets": ["finance_meta.nyse_asset_profile"],
        "used_by": ["Universe filter", "metadata refresh"],
        "caveats": ["current profile snapshot입니다."],
        "next_action": "profile table이 비어 있으면 NYSE universe 적재 상태부터 확인하세요.",
    },
    "collect_financial_statements": {
        "title": "상세 재무제표 수동 수집",
        "purpose": "선택한 symbol의 EDGAR detailed statement raw ledger를 수집합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_filings",
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_financial_statement_labels",
        ],
        "used_by": ["Statement shadow rebuild", "PIT inspection"],
        "caveats": ["issuer별 form 구조와 concept coverage가 다를 수 있습니다."],
        "next_action": "routine strict coverage 복구는 Extended Statement Refresh를 우선 사용하세요.",
    },
    "rebuild_statement_shadow": {
        "title": "재무제표 shadow 재구성",
        "purpose": "이미 저장된 raw statement ledger로 statement fundamentals / factors shadow를 재구성합니다.",
        "targets": ["finance_fundamental.nyse_fundamentals_statement", "finance_fundamental.nyse_factors_statement"],
        "used_by": ["Strict annual / quarterly factor runtime"],
        "caveats": ["raw statement rows가 없으면 shadow row도 생성되지 않습니다."],
        "next_action": "raw present / shadow missing이면 이 job, raw missing이면 Extended Statement Refresh를 실행하세요.",
    },
}

PRICE_COLLECTION_JOBS = {"daily_market_update", "collect_ohlcv"}
COMPOSITE_PRICE_JOBS = {"pipeline_core_market_data"}
LIFECYCLE_EVIDENCE_JOBS = {
    "collect_sec_form25_delistings",
    "collect_symbol_directory_snapshots",
    "collect_sec_company_ticker_crosscheck",
    "collect_computed_snapshot_lifecycle",
}
PARTIAL_LIFECYCLE_EVIDENCE_JOBS = {
    "collect_symbol_directory_snapshots",
    "collect_sec_company_ticker_crosscheck",
    "collect_computed_snapshot_lifecycle",
}
ETF_PROVIDER_JOBS = {
    "discover_etf_provider_source_map",
    "collect_etf_operability_provider",
    "collect_etf_holdings_exposure",
}
EVENT_CALENDAR_JOBS = {
    "collect_fomc_calendar",
    "collect_macro_calendar",
    "import_bls_macro_calendar_ics",
    "collect_earnings_calendar",
}
MACRO_CONTEXT_JOBS = {"collect_macro_market_context", "collect_market_sentiment"}


def _preset_csv(name: str, fallback_name: str = "US Statement Coverage 300") -> str:
    tickers = QUALITY_STRICT_PRESETS.get(name) or QUALITY_STRICT_PRESETS.get(fallback_name, [])
    return ",".join(tickers)


SYMBOL_PRESETS = {
    "Big Tech": "AAPL,MSFT,GOOG",
    "Core ETFs": "SPY,QQQ,TLT,GLD",
    "Dividend ETFs": "VIG,SCHD,DGRO,GLD",
    "US Statement Coverage 100": _preset_csv("US Statement Coverage 100"),
    "US Statement Coverage 300": _preset_csv("US Statement Coverage 300"),
    "US Statement Coverage 500": _preset_csv("US Statement Coverage 500"),
    "US Statement Coverage 1000": _preset_csv("US Statement Coverage 1000"),
    "Custom": "",
}
PERIOD_PRESETS = ["1d", "7d", "1mo", "3mo", "6mo", "1y", "5y", "10y", "15y", "20y"]
P2_PROVIDER_OPERABILITY_SYMBOLS = "AOR, IEF, TLT, SPY, BIL, GLD, QQQ"
P2_PROVIDER_HOLDINGS_SYMBOLS = "AOR, IEF, TLT, SPY, BIL, QQQ"
P2_PROVIDER_SOURCE_MAP_SYMBOLS = "AOR, IEF, TLT, SPY, BIL, GLD, QQQ"
P2_PROVIDER_MACRO_SERIES = "VIXCLS, T10Y3M, BAA10Y"
SEC_FORM25_DEFAULT_SYMBOLS = ""
SYMBOL_SOURCE_OPTIONS = [
    "Manual",
    "NYSE Stocks",
    "NYSE ETFs",
    "NYSE Stocks + ETFs",
    "Profile Filtered Stocks",
    "Profile Filtered ETFs",
    "Profile Filtered Stocks + ETFs",
]
SYMBOL_SOURCE_DISPLAY_LABELS = {
    "Manual": "직접 입력",
    "NYSE Stocks": "NYSE 주식 전체",
    "NYSE ETFs": "NYSE ETF 전체",
    "NYSE Stocks + ETFs": "NYSE 주식+ETF 전체",
    "Profile Filtered Stocks": "프로필 필터 주식",
    "Profile Filtered ETFs": "프로필 필터 ETF",
    "Profile Filtered Stocks + ETFs": "프로필 필터 주식+ETF",
}
SYMBOL_PRESET_DISPLAY_LABELS = {
    "Big Tech": "빅테크 기본",
    "Core ETFs": "핵심 ETF",
    "Dividend ETFs": "배당 ETF",
    "US Statement Coverage 100": "미국 재무제표 100",
    "US Statement Coverage 300": "미국 재무제표 300",
    "US Statement Coverage 500": "미국 재무제표 500",
    "US Statement Coverage 1000": "미국 재무제표 1000",
    "Custom": "직접 입력",
}
SYMBOL_INPUT_DISPLAY_TITLES = {
    "Diagnosis Symbols": "진단 대상",
    "Inspection Symbols": "검사 대상",
    "Daily Market Symbols": "일별 가격 대상",
    "Weekly Refresh Symbols": "주간 펀더멘털 대상",
    "Extended Statement Symbols": "상세 재무제표 대상",
    "Pipeline Symbols": "핵심 파이프라인 대상",
    "OHLCV Symbols": "가격 이력 대상",
    "Fundamentals Symbols": "펀더멘털 대상",
    "Factor Symbols": "팩터 계산 대상",
    "Financial Statement Symbols": "재무제표 수집 대상",
    "Shadow Rebuild Symbols": "Shadow 재구성 대상",
}


def _format_symbol_source_label(value: str) -> str:
    return SYMBOL_SOURCE_DISPLAY_LABELS.get(value, value)


def _format_symbol_preset_label(value: str) -> str:
    return SYMBOL_PRESET_DISPLAY_LABELS.get(value, value)


def _format_symbol_input_title(value: str) -> str:
    return SYMBOL_INPUT_DISPLAY_TITLES.get(value, value)


def init_ingestion_state() -> None:
    if "recent_results" not in st.session_state:
        st.session_state.recent_results = []
    if "pending_job" not in st.session_state:
        st.session_state.pending_job = None
    if "running_job" not in st.session_state:
        st.session_state.running_job = None
    if "last_completed_result" not in st.session_state:
        st.session_state.last_completed_result = None
    if "statement_pit_inspection_result" not in st.session_state:
        st.session_state.statement_pit_inspection_result = None
    if "price_stale_diagnosis_result" not in st.session_state:
        st.session_state.price_stale_diagnosis_result = None
    if "statement_coverage_diagnosis_result" not in st.session_state:
        st.session_state.statement_coverage_diagnosis_result = None
    if "statement_universe_coverage_qa_result" not in st.session_state:
        st.session_state.statement_universe_coverage_qa_result = None
    if "ingestion_prefill_request" not in st.session_state:
        st.session_state.ingestion_prefill_request = None
    if "ingestion_prefill_notice" not in st.session_state:
        st.session_state.ingestion_prefill_notice = None


def apply_pending_ingestion_prefill() -> None:
    request = st.session_state.get("ingestion_prefill_request")
    if not request:
        return

    target = str(request.get("target") or "").strip()
    symbols_csv = str(request.get("symbols_csv") or "").strip()
    if not target or not symbols_csv:
        st.session_state.ingestion_prefill_request = None
        return

    prefix_map = {
        "extended_statement_refresh": "extended_statement",
        "statement_shadow_rebuild": "shadow_rebuild",
        "statement_coverage_diagnosis": "statement_coverage_diag",
    }
    prefix = prefix_map.get(target)
    if prefix is None:
        st.session_state.ingestion_prefill_request = None
        return

    st.session_state[f"{prefix}_source_mode"] = "Manual"
    st.session_state[f"{prefix}_preset"] = "Custom"
    st.session_state[f"{prefix}_preset_applied"] = "Custom"
    st.session_state[f"{prefix}_symbols_input"] = symbols_csv

    for key, value in (request.get("widget_values") or {}).items():
        st.session_state[key] = value

    notice = request.get("notice")
    if notice:
        st.session_state.ingestion_prefill_notice = str(notice)

    st.session_state.ingestion_prefill_request = None


def _push_result(result: JobResult) -> None:
    artifact_info = write_run_artifacts(result)
    result.setdefault("details", {})
    result["details"]["result_artifacts"] = artifact_info
    results = st.session_state.recent_results
    results.insert(0, result)
    st.session_state.recent_results = results[:10]
    append_run_history(result)


def _status_to_banner(status: str):
    if status == "success":
        return st.success
    if status == "partial_success":
        return st.warning
    return st.error


def _install_ingestion_responsive_styles() -> None:
    st.markdown(
        """
        <style>
          .ingestion-meta-list {
            display: grid;
            gap: 0.5rem;
            margin: 0.35rem 0 0.65rem;
          }
          .ingestion-meta-row {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-start;
            gap: 0.35rem 0.45rem;
            min-width: 0;
          }
          .ingestion-meta-label {
            color: #7a7f8c;
            font-size: 0.9rem;
            font-weight: 700;
            line-height: 1.35;
            white-space: nowrap;
          }
          .ingestion-pill {
            background: rgba(125, 130, 150, 0.12);
            border: 1px solid rgba(49, 51, 63, 0.08);
            border-radius: 0.4rem;
            color: #246b3f;
            display: inline-block;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.8rem;
            line-height: 1.35;
            max-width: 100%;
            overflow-wrap: anywhere;
            padding: 0.12rem 0.36rem;
            word-break: break-word;
          }
          .ingestion-text-value {
            color: inherit;
            display: inline-block;
            line-height: 1.35;
            max-width: 100%;
            overflow-wrap: anywhere;
            word-break: keep-all;
          }
          .ingestion-text-value + .ingestion-text-value::before {
            color: #8b909b;
            content: " · ";
          }
          .ingestion-stat-grid {
            display: grid;
            gap: 0.65rem;
            grid-template-columns: repeat(auto-fit, minmax(7.5rem, 1fr));
            margin: 0.75rem 0 0.95rem;
          }
          .ingestion-stat-card {
            background: rgba(125, 130, 150, 0.08);
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 0.5rem;
            min-width: 0;
            padding: 0.72rem 0.82rem;
          }
          .ingestion-stat-card.status-success {
            background: #eaf8ef;
            border-color: rgba(34, 139, 73, 0.22);
          }
          .ingestion-stat-card.status-success .ingestion-stat-value,
          .ingestion-stat-card.status-success .ingestion-stat-label {
            color: #14783f;
          }
          .ingestion-stat-card.status-partial_success {
            background: #fff7e6;
            border-color: rgba(184, 121, 0, 0.22);
          }
          .ingestion-stat-card.status-partial_success .ingestion-stat-value,
          .ingestion-stat-card.status-partial_success .ingestion-stat-label {
            color: #8a5a00;
          }
          .ingestion-stat-card.status-failed {
            background: #fff0f0;
            border-color: rgba(210, 56, 56, 0.22);
          }
          .ingestion-stat-card.status-failed .ingestion-stat-value,
          .ingestion-stat-card.status-failed .ingestion-stat-label {
            color: #9f2626;
          }
          .ingestion-stat-label {
            color: #6f7480;
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1.25;
            overflow-wrap: anywhere;
          }
          .ingestion-stat-value {
            color: inherit;
            font-size: clamp(1.55rem, 4.5vw, 2.35rem);
            font-weight: 760;
            letter-spacing: 0;
            line-height: 1.08;
            margin-top: 0.32rem;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .ingestion-meta-grid {
            display: grid;
            gap: 0.65rem;
            grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
            margin: 0.35rem 0 0.75rem;
          }
          .ingestion-meta-card {
            background: rgba(125, 130, 150, 0.08);
            border: 1px solid rgba(49, 51, 63, 0.09);
            border-radius: 0.5rem;
            min-width: 0;
            padding: 0.62rem 0.72rem;
          }
          .ingestion-meta-card-label {
            color: #6f7480;
            font-size: 0.76rem;
            font-weight: 700;
            line-height: 1.2;
          }
          .ingestion-meta-card-value {
            color: inherit;
            font-size: 1rem;
            font-weight: 650;
            line-height: 1.3;
            margin-top: 0.26rem;
            overflow-wrap: anywhere;
            word-break: break-word;
          }
          .ingestion-select-caption {
            color: inherit;
            font-size: 0.9rem;
            line-height: 1.35;
            margin: -0.25rem 0 0.45rem;
            overflow-wrap: anywhere;
          }
          .ingestion-workflow-grid {
            display: grid;
            gap: 0.75rem;
            grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
            margin: 0.85rem 0 1.1rem;
          }
          .ingestion-workflow-card {
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 0.5rem;
            min-width: 0;
            padding: 0.78rem 0.86rem;
          }
          .ingestion-workflow-step {
            color: #6f7480;
            font-size: 0.75rem;
            font-weight: 800;
            line-height: 1.2;
            text-transform: uppercase;
          }
          .ingestion-workflow-title {
            font-size: 0.98rem;
            font-weight: 760;
            line-height: 1.25;
            margin-top: 0.18rem;
          }
          .ingestion-workflow-body {
            color: #6f7480;
            font-size: 0.84rem;
            line-height: 1.4;
            margin-top: 0.28rem;
            overflow-wrap: anywhere;
          }
          .ingestion-contract-panel,
          .ingestion-callout {
            border: 1px solid rgba(49, 51, 63, 0.12);
            border-radius: 0.5rem;
            margin: 0.7rem 0 0.9rem;
            padding: 0.8rem 0.9rem;
          }
          .ingestion-callout.warning {
            background: #fff7e6;
            border-color: rgba(184, 121, 0, 0.24);
          }
          .ingestion-callout.danger {
            background: #fff0f0;
            border-color: rgba(210, 56, 56, 0.24);
          }
          .ingestion-callout.info {
            background: rgba(41, 111, 214, 0.08);
            border-color: rgba(41, 111, 214, 0.18);
          }
          .ingestion-callout.success {
            background: #eaf8ef;
            border-color: rgba(34, 139, 73, 0.22);
          }
          .ingestion-callout-title,
          .ingestion-contract-title {
            font-size: 0.95rem;
            font-weight: 800;
            line-height: 1.25;
          }
          .ingestion-callout-body {
            font-size: 0.9rem;
            line-height: 1.45;
            margin-top: 0.32rem;
            overflow-wrap: anywhere;
          }
          .ingestion-contract-grid {
            display: grid;
            gap: 0.52rem;
            grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
            margin-top: 0.62rem;
          }
          .ingestion-contract-item {
            min-width: 0;
          }
          .ingestion-contract-label {
            color: #6f7480;
            font-size: 0.74rem;
            font-weight: 800;
            line-height: 1.2;
          }
          .ingestion-contract-value {
            font-size: 0.94rem;
            font-weight: 650;
            line-height: 1.32;
            margin-top: 0.18rem;
            overflow-wrap: anywhere;
          }
          .ingestion-contract-note {
            color: #6f7480;
            font-size: 0.83rem;
            line-height: 1.4;
            margin-top: 0.62rem;
            overflow-wrap: anywhere;
          }
          @media (max-width: 760px) {
            div[data-testid="column"] {
              flex: 1 1 100% !important;
              max-width: 100% !important;
              min-width: 0 !important;
              width: 100% !important;
            }
            .ingestion-stat-grid {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .ingestion-meta-grid {
              grid-template-columns: minmax(0, 1fr);
            }
            .ingestion-workflow-grid,
            .ingestion-contract-grid {
              grid-template-columns: minmax(0, 1fr);
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _html_join_pills(values: list[str]) -> str:
    return " ".join(f'<span class="ingestion-pill">{escape(value)}</span>' for value in values if value)


def _render_ingestion_meta_rows(rows: list[tuple[str, list[str], bool]]) -> None:
    rendered_rows: list[str] = []
    for label, values, monospace in rows:
        clean_values = [str(value) for value in values if str(value).strip()]
        if not clean_values:
            continue
        value_html = (
            _html_join_pills(clean_values)
            if monospace
            else " ".join(f'<span class="ingestion-text-value">{escape(value)}</span>' for value in clean_values)
        )
        rendered_rows.append(
            '<div class="ingestion-meta-row">'
            f'<span class="ingestion-meta-label">{escape(label)}:</span>'
            f"{value_html}</div>"
        )
    if rendered_rows:
        st.markdown(
            '<div class="ingestion-meta-list">' + "".join(rendered_rows) + "</div>",
            unsafe_allow_html=True,
        )


def _format_count(value: Any) -> str:
    try:
        if value is None:
            return "0"
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value or "0")


def _format_duration(value: Any) -> str:
    try:
        numeric = float(value or 0)
    except (TypeError, ValueError):
        return str(value or "-")
    return f"{numeric:,.2f}"


def _render_ingestion_stat_grid(items: list[tuple[str, str, str | None]]) -> None:
    cards = []
    for label, value, status_class in items:
        extra_class = f" status-{status_class}" if status_class else ""
        cards.append(
            f'<div class="ingestion-stat-card{extra_class}">'
            f'<div class="ingestion-stat-label">{escape(label)}</div>'
            f'<div class="ingestion-stat-value">{escape(str(value))}</div>'
            "</div>"
        )
    st.markdown(
        '<div class="ingestion-stat-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def _render_ingestion_meta_grid(items: list[tuple[str, str]]) -> None:
    cards = []
    for label, value in items:
        cards.append(
            '<div class="ingestion-meta-card">'
            f'<div class="ingestion-meta-card-label">{escape(label)}</div>'
            f'<div class="ingestion-meta-card-value">{escape(str(value or "-"))}</div>'
            "</div>"
        )
    if cards:
        st.markdown(
            '<div class="ingestion-meta-grid">' + "".join(cards) + "</div>",
            unsafe_allow_html=True,
        )


def _render_ingestion_workflow_overview() -> None:
    cards = [
        (
            "Step 1",
            "수집 범위 선택",
            "심볼 source, 기간, provider 옵션은 기존처럼 사용자가 직접 정합니다.",
        ),
        (
            "Step 2",
            "Preflight 확인",
            "입력값, 대상 수, 기존 DB coverage, 대량 실행 위험을 먼저 확인합니다.",
        ),
        (
            "Step 3",
            "DB 저장",
            "외부 API / 공식 파일 / provider page 결과를 MySQL table에 저장합니다.",
        ),
        (
            "Step 4",
            "결과 해석",
            "row 수, symbol 누락, partial evidence 의미를 job 유형별로 구분해서 확인합니다.",
        ),
    ]
    html = []
    for step, title, body in cards:
        html.append(
            '<div class="ingestion-workflow-card">'
            f'<div class="ingestion-workflow-step">{escape(step)}</div>'
            f'<div class="ingestion-workflow-title">{escape(title)}</div>'
            f'<div class="ingestion-workflow-body">{escape(body)}</div>'
            "</div>"
        )
    st.markdown(
        '<div class="ingestion-workflow-grid">' + "".join(html) + "</div>",
        unsafe_allow_html=True,
    )


def _render_data_quality_callout(title: str, body: str, *, tone: str = "info") -> None:
    st.markdown(
        f'<div class="ingestion-callout {escape(tone)}">'
        f'<div class="ingestion-callout-title">{escape(title)}</div>'
        f'<div class="ingestion-callout-body">{escape(body)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def _render_collection_contract(
    title: str,
    items: list[tuple[str, Any]],
    *,
    note: str | None = None,
) -> None:
    rendered_items = []
    for label, value in items:
        rendered_items.append(
            '<div class="ingestion-contract-item">'
            f'<div class="ingestion-contract-label">{escape(label)}</div>'
            f'<div class="ingestion-contract-value">{escape(str(value if value not in (None, "") else "-"))}</div>'
            "</div>"
        )
    note_html = (
        f'<div class="ingestion-contract-note">{escape(note)}</div>'
        if note
        else ""
    )
    st.markdown(
        '<div class="ingestion-contract-panel">'
        f'<div class="ingestion-contract-title">{escape(title)}</div>'
        '<div class="ingestion-contract-grid">'
        + "".join(rendered_items)
        + "</div>"
        + note_html
        + "</div>",
        unsafe_allow_html=True,
    )


def _job_domain(job_name: str | None) -> str:
    normalized = str(job_name or "")
    if normalized in PRICE_COLLECTION_JOBS:
        return "price"
    if normalized in COMPOSITE_PRICE_JOBS:
        return "pipeline"
    if normalized in LIFECYCLE_EVIDENCE_JOBS:
        return "lifecycle"
    if normalized in ETF_PROVIDER_JOBS:
        return "provider"
    if normalized in MACRO_CONTEXT_JOBS:
        return "macro"
    if normalized in EVENT_CALENDAR_JOBS:
        return "event"
    if "statement" in normalized:
        return "statement"
    if "fundamental" in normalized or "factor" in normalized:
        return "fundamental"
    if "profile" in normalized or "metadata" in normalized:
        return "metadata"
    return "generic"


def _result_metric_labels(job_name: str | None) -> tuple[str, str, str, str, str]:
    domain = _job_domain(job_name)
    if domain == "lifecycle":
        return ("상태", "증거 Row", "관찰 / 요청", "누락 Source/Symbol", "소요 시간(초)")
    if domain in {"provider", "macro", "event"}:
        return ("상태", "저장 Row", "수집 대상", "누락 / 실패", "소요 시간(초)")
    if domain == "price":
        return ("상태", "가격 Row", "요청 Symbol", "누락 / 실패", "소요 시간(초)")
    if domain == "pipeline":
        return ("상태", "총 저장 Row", "요청 Symbol", "누락 / 실패", "소요 시간(초)")
    return ("상태", "저장 Row", "요청 대상", "누락 / 실패", "소요 시간(초)")


def _format_contract_window(*, period: str | None, start: str | None, end: str | None) -> str:
    if start or end:
        return f"start={start or '-'}, end={end or '-'}"
    return f"period={period or '-'}"


@st.cache_data(ttl=60, show_spinner=False)
def _load_price_window_preflight_summary_cached(
    symbols: tuple[str, ...],
    start: str | None,
    end: str | None,
    timeframe: str,
) -> pd.DataFrame:
    return load_price_window_preflight_summary(
        symbols,
        start=start,
        end=end,
        timeframe=timeframe,
    )


def _render_price_window_preflight(
    *,
    symbols: list[str],
    start: str | None,
    end: str | None,
    timeframe: str,
    max_symbols: int = 300,
) -> None:
    if not symbols:
        return
    if not start and not end:
        st.caption(
            "DB coverage quick check는 명시적인 start/end가 있을 때 실행합니다. "
            "period 기반 수집은 실행 후 결과의 최신 거래일과 Price Stale Diagnosis로 확인하세요."
        )
        return
    if len(symbols) > max_symbols:
        st.caption(
            f"DB coverage quick check는 {max_symbols}개 이하의 bounded run에서만 자동 실행합니다. "
            f"현재 대상은 {len(symbols):,}개이므로 실행 후 결과와 진단 payload를 확인하세요."
        )
        return

    try:
        coverage = _load_price_window_preflight_summary_cached(tuple(symbols), start, end, timeframe)
    except Exception as exc:
        st.warning(f"DB coverage quick check를 실행하지 못했습니다: {exc}")
        return

    if coverage.empty:
        _render_data_quality_callout(
            "DB coverage quick check",
            "선택한 대상의 기존 가격 row를 찾지 못했습니다. 이 실행은 신규 보강 또는 provider 확인 성격으로 봐야 합니다.",
            tone="warning",
        )
        return

    coverage = coverage.copy()
    coverage["window_row_count"] = pd.to_numeric(coverage.get("window_row_count"), errors="coerce").fillna(0)
    symbols_with_window = set(coverage.loc[coverage["window_row_count"] > 0, "symbol"].astype(str))
    missing_window = [sym for sym in symbols if sym not in symbols_with_window]
    message = (
        f"기존 DB window row 확인: {len(symbols_with_window):,}/{len(symbols):,} symbols. "
        "이 값은 실행 전 상태이며, provider 수집 결과와 별도로 봐야 합니다."
    )
    if missing_window:
        message += f" window row가 없는 sample: {', '.join(missing_window[:8])}."
        tone = "warning"
    else:
        tone = "info"
    _render_data_quality_callout("DB coverage quick check", message, tone=tone)


def _job_guide(job_name: str | None) -> dict[str, Any]:
    return JOB_GUIDE.get(str(job_name or ""), {})


def _job_title(job_name: str | None) -> str:
    guide = _job_guide(job_name)
    return str(guide.get("title") or job_name or "-")


def _status_label(status: str | None) -> str:
    return {
        "success": "성공",
        "partial_success": "부분 성공",
        "failed": "실패",
    }.get(str(status or ""), str(status or "-"))


def _collection_entry_relationship_note(job_name: str | None) -> str:
    return COLLECTION_ENTRY_RELATIONSHIPS.get(str(job_name or ""), "")


def _render_job_brief(job_name: str) -> None:
    guide = _job_guide(job_name)
    if not guide:
        return

    st.markdown(f"#### {guide['title']}")
    st.caption(f"내부 job id: `{job_name}`")
    st.write(guide["purpose"])

    _render_ingestion_meta_rows(
        [
            ("저장 위치", [str(item) for item in guide.get("targets") or []], True),
            ("사용 위치", [str(item) for item in guide.get("used_by") or []], False),
        ]
    )

    relationship_note = _collection_entry_relationship_note(job_name)
    if relationship_note:
        st.caption("흐름 구분: " + relationship_note)

    caveats = [str(item) for item in guide.get("caveats") or [] if str(item).strip()]
    if caveats:
        st.caption("데이터 품질 주의: " + " / ".join(caveats))


def _build_common_last_result_summary(result: JobResult) -> dict[str, str]:
    job_name = str(result.get("job_name") or "")
    guide = _job_guide(job_name)
    failed_count = len(result.get("failed_symbols") or [])
    status = str(result.get("status") or "")
    attention = ""
    if status == "partial_success":
        attention = "부분 성공은 pass가 아니므로 downstream validation에서 coverage gap으로 남을 수 있습니다."
    elif status == "failed":
        attention = "저장 row가 0이면 source 차단, 잘못된 입력, provider no-data를 먼저 구분하세요."
    elif failed_count:
        attention = "누락 / 실패 대상이 있으므로 상세 reason과 재실행 payload를 확인하세요."

    return {
        "title": _job_title(job_name),
        "job_name": job_name,
        "status": _status_label(status),
        "raw_status": status,
        "rows": _format_count(result.get("rows_written")),
        "requested": _format_count(result.get("symbols_requested")),
        "failed": _format_count(failed_count),
        "duration": _format_duration(result.get("duration_sec")),
        "message": str(result.get("message") or ""),
        "next_action": str(guide.get("next_action") or "실행 기록 / 결과 탭에서 상세 payload와 관련 로그를 확인하세요."),
        "attention": attention,
    }


def _render_common_last_result_summary() -> None:
    recent_results = st.session_state.get("recent_results") or []
    if not recent_results:
        return

    summary = _build_common_last_result_summary(recent_results[0])
    with st.container(border=True):
        st.markdown("#### 최근 실행 요약")
        st.caption(f"{summary['title']} · 내부 job id: `{summary['job_name']}`")
        _render_ingestion_stat_grid(
            [
                ("상태", summary["status"], summary["raw_status"]),
                ("저장 Row", summary["rows"], None),
                ("대상", summary["requested"], None),
                ("누락 / 실패", summary["failed"], None),
                ("소요 시간", summary["duration"], None),
            ]
        )
        if summary["message"]:
            st.caption(summary["message"])
        if summary["attention"]:
            st.warning(summary["attention"])
        st.caption("다음 확인: " + summary["next_action"])


def _render_result_guidance(result: JobResult) -> None:
    guide = _job_guide(result.get("job_name"))
    guidance: list[str] = []
    next_action = guide.get("next_action")
    if next_action:
        guidance.append(str(next_action))

    failed_symbols = result.get("failed_symbols") or []
    if failed_symbols:
        guidance.append("누락 / 실패 대상이 있으므로 상세 reason과 재실행 payload를 먼저 확인하세요.")

    if result.get("status") == "failed":
        guidance.append("저장 row가 0이면 source 차단, 잘못된 입력, 이미 없는 provider row를 구분해야 합니다.")
    elif result.get("status") == "partial_success":
        guidance.append("부분 성공은 pass가 아니므로 downstream validation에서 coverage gap으로 남을 수 있습니다.")

    if not guidance:
        return

    with st.expander("다음 확인 액션", expanded=True):
        for item in dict.fromkeys(guidance):
            st.markdown(f"- {item}")


def _build_statement_refresh_action_summary(result: JobResult) -> dict[str, str]:
    details = result.get("details") or {}
    requested = int(result.get("symbols_requested") or 0)
    processed = int(result.get("symbols_processed") or 0)
    failed_count = len(result.get("failed_symbols") or [])
    rows_written = int(result.get("rows_written") or 0)
    freq = str(details.get("freq") or details.get("period") or "statement").strip() or "statement"
    raw_steps = details.get("steps") or []
    steps = [step for step in raw_steps if isinstance(step, dict)]
    failed_steps = [
        str(step.get("job_name") or "-")
        for step in steps
        if str(step.get("status") or "") != "success"
    ]

    coverage = f"{processed}/{requested} symbols processed" if requested else f"{processed} symbols processed"
    failed = f"{failed_count} failed"
    freshness = (
        f"{freq} EDGAR statement freshness is interpreted from accepted_at / available_at, "
        "not from provider fetch time."
    )

    if failed_steps:
        next_action = (
            f"Check failed step(s): {', '.join(failed_steps[:5])}. "
            "Run Statement Coverage Diagnosis, then rerun EDGAR annual refresh or shadow rebuild for affected symbols."
        )
    elif failed_count or str(result.get("status") or "") != "success":
        next_action = (
            "Run Statement Coverage Diagnosis, check SEC_USER_AGENT / fair-access pacing, "
            "then rerun affected symbols."
        )
    else:
        next_action = "Review statement shadow coverage and continue to Backtest strict annual preflight."

    return {
        "coverage": coverage,
        "freshness": freshness,
        "failed": failed,
        "next_action": next_action,
        "rows": f"{rows_written:,} rows written",
    }


def _render_result_interpretation(result: JobResult) -> None:
    job_name = str(result.get("job_name") or "")
    domain = _job_domain(job_name)
    status = str(result.get("status") or "")
    details = result.get("details") or {}
    failed_count = len(result.get("failed_symbols") or [])

    if domain == "price":
        missing = len(details.get("missing_symbols") or [])
        provider_no_data = len(details.get("provider_no_data_symbols") or [])
        rate_limited = len(details.get("rate_limited_symbols") or [])
        if status != "success" or missing or provider_no_data or rate_limited:
            _render_data_quality_callout(
                "가격 수집 결과 해석",
                "저장 row가 있더라도 요청 symbol 전체가 같은 기간을 채웠다는 뜻은 아닙니다. "
                f"missing={missing:,}, provider no-data={provider_no_data:,}, rate-limit={rate_limited:,} 상태를 확인하고 "
                "필요하면 rerun payload 또는 Price Stale Diagnosis로 원인을 분리하세요.",
                tone="warning",
            )
        else:
            _render_data_quality_callout(
                "가격 수집 결과 해석",
                "provider가 row를 반환한 대상은 저장되었습니다. 실제 backtest 기간 coverage는 Data Coverage Audit이나 "
                "bounded DB coverage check로 다시 확인하는 것이 안전합니다.",
                tone="info",
            )
        return

    if domain == "pipeline":
        steps = details.get("steps") or []
        partial_steps = [step.get("job_name") for step in steps if step.get("status") != "success"]
        if partial_steps:
            _render_data_quality_callout(
                "Pipeline 결과 해석",
                "Composite job은 OHLCV, fundamentals, factors 중 하나만 partial이어도 downstream coverage gap이 남습니다. "
                f"확인 필요 step: {', '.join(str(item) for item in partial_steps[:5])}.",
                tone="warning",
            )
        else:
            _render_data_quality_callout(
                "Pipeline 결과 해석",
                "세부 step이 모두 성공이면 기본 데이터 연결은 완료된 상태입니다. 그래도 기간 coverage와 factor prerequisite은 "
                "실제 backtest 범위 기준으로 다시 확인하세요.",
                tone="info",
            )
        return

    if domain == "statement":
        summary = _build_statement_refresh_action_summary(result)
        tone = "warning" if status != "success" or failed_count else "info"
        _render_ingestion_meta_grid(
            [
                ("Coverage", summary["coverage"]),
                ("Freshness", summary["freshness"]),
                ("Failed", summary["failed"]),
                ("Rows", summary["rows"]),
            ]
        )
        _render_data_quality_callout(
            "EDGAR statement refresh 해석",
            "Coverage와 freshness를 먼저 확인한 뒤 다음 행동을 고르세요. "
            f"{summary['next_action']}",
            tone=tone,
        )
        return

    if domain == "lifecycle":
        if job_name in PARTIAL_LIFECYCLE_EVIDENCE_JOBS:
            _render_data_quality_callout(
                "Lifecycle evidence 해석",
                "이 결과는 current snapshot 또는 repeated observation 기반 partial evidence입니다. "
                "historical membership PASS나 active listing proof로 해석하면 안 됩니다.",
                tone="warning",
            )
        else:
            _render_data_quality_callout(
                "Lifecycle evidence 해석",
                "SEC Form 25 row는 delisting evidence로 유효하지만, Form 25가 없다는 사실은 active listing proof가 아닙니다.",
                tone="info",
            )
        return

    if domain == "provider":
        tone = "warning" if status != "success" or failed_count else "info"
        _render_data_quality_callout(
            "Provider snapshot 해석",
            "이 row는 현재 provider snapshot입니다. Practical Validation은 이 DB snapshot을 읽지만, 과거 특정 시점의 "
            "PIT holdings / operability truth로 보지는 않습니다. partial이면 unsupported parser와 missing ETF를 먼저 확인하세요.",
            tone=tone,
        )
        return

    if domain == "macro":
        _render_data_quality_callout(
            "Macro context 해석",
            "FRED observation date 기준 series입니다. ALFRED vintage PIT가 아니므로 과거 시점 의사결정 재현에는 한계가 있습니다.",
            tone="info" if status == "success" else "warning",
        )
        return

    if domain == "event":
        _render_data_quality_callout(
            "Event calendar 해석",
            "시장 이벤트 row는 수집 시점의 calendar snapshot 또는 free-provider estimate입니다. 실적 발표 일정은 공식 확정 IR 일정으로 보지 않습니다.",
            tone="info" if status == "success" else "warning",
        )


def _render_result_data_quality_notes(job_name: str | None) -> None:
    guide = _job_guide(job_name)
    caveats = [str(item) for item in guide.get("caveats") or [] if str(item).strip()]
    if not caveats:
        return
    with st.expander("데이터 품질 주의", expanded=False):
        for item in caveats:
            st.markdown(f"- {item}")


def _has_running_job() -> bool:
    return bool(st.session_state.running_job)


def _is_running_action(action: str) -> bool:
    job = st.session_state.running_job
    return bool(job and job.get("action") == action)


def promote_pending_job() -> None:
    if st.session_state.running_job is None and st.session_state.pending_job is not None:
        st.session_state.running_job = st.session_state.pending_job
        st.session_state.pending_job = None


def _schedule_job(job: dict[str, Any]) -> None:
    if _has_running_job():
        st.warning("다른 Ingestion job이 실행 중입니다. 완료 후 새 작업을 시작하세요.")
        return
    job = dict(job)
    collection_section = _infer_ingestion_collection_section(job)
    job["collection_section"] = collection_section
    run_metadata = dict(job.get("run_metadata") or {})
    run_metadata["collection_section"] = collection_section
    job["run_metadata"] = run_metadata
    job["ui_started_at"] = datetime.now().isoformat(timespec="seconds")
    st.session_state.pending_job = job
    st.session_state.ingestion_collection_section_pending = collection_section
    st.rerun()


def _job_metadata(
    *,
    pipeline_type: str | None = None,
    execution_mode: str | None = None,
    symbol_source: str | None = None,
    symbol_count: int | None = None,
    input_params: dict[str, Any] | None = None,
    execution_context: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "pipeline_type": pipeline_type,
        "execution_mode": execution_mode,
        "symbol_source": symbol_source,
        "symbol_count": symbol_count,
        "input_params": input_params or {},
        **_runtime_metadata(),
    }
    if execution_context:
        metadata["execution_context"] = execution_context
    if notes:
        metadata["notes"] = notes
    return metadata


def _diagnostic_state_key(action: str) -> str | None:
    return {
        "diagnose_price_stale": "price_stale_diagnosis_result",
        "diagnose_statement_universe_coverage": "statement_universe_coverage_qa_result",
        "diagnose_statement_coverage": "statement_coverage_diagnosis_result",
        "inspect_statement_pit": "statement_pit_inspection_result",
    }.get(action)


def _diagnostic_status_to_job_status(status: Any) -> str:
    normalized = str(status or "").strip().lower()
    if normalized in {"ok", "success", "passed", "pass"}:
        return "success"
    if normalized in {"warning", "partial_success", "review", "needs_review"}:
        return "partial_success"
    return "failed"


def _count_diagnostic_symbols(params: dict[str, Any]) -> int:
    symbols = params.get("symbols")
    if isinstance(symbols, str):
        return len(_parse_csv_items(symbols))
    if isinstance(symbols, (list, tuple, set)):
        return len([symbol for symbol in symbols if str(symbol).strip()])
    return 0


def _build_diagnostic_job_result(
    *,
    action: str,
    params: dict[str, Any],
    diagnostic_result: dict[str, Any],
    started_at: datetime,
    finished_at: datetime,
) -> JobResult:
    status = _diagnostic_status_to_job_status(diagnostic_result.get("status"))
    symbols_requested = _count_diagnostic_symbols(params)
    return {
        "job_name": action,
        "status": status,
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": finished_at.isoformat(timespec="seconds"),
        "duration_sec": round((finished_at - started_at).total_seconds(), 3),
        "rows_written": 0,
        "symbols_requested": symbols_requested,
        "symbols_processed": symbols_requested if status in {"success", "partial_success"} else 0,
        "failed_symbols": [],
        "message": diagnostic_result.get("message") or f"{_job_title(action)} completed.",
        "details": {
            "action": action,
            "diagnostic_result": diagnostic_result,
            "write_behavior": "read_only",
        },
    }


def _dispatch_diagnostic_job(
    action: str,
    params: dict[str, Any],
    *,
    progress_callback: Any = None,
) -> JobResult:
    started_at = datetime.now()
    if progress_callback:
        progress_callback({"type": "stage_start", "stage": action, "stage_index": 1, "total_stages": 1})

    if action == "diagnose_price_stale":
        diagnostic_result = run_price_stale_diagnosis(
            params.get("symbols") or [],
            end=params.get("end"),
            timeframe=params.get("timeframe", "1d"),
        )
    elif action == "diagnose_statement_universe_coverage":
        diagnostic_result = run_statement_universe_coverage_qa(
            universe_code=params.get("universe_code", "TOP1000"),
            universe_limit=params.get("universe_limit"),
            freq=params.get("freq", "annual"),
            as_of_date=params.get("as_of_date"),
        )
    elif action == "diagnose_statement_coverage":
        diagnostic_result = run_statement_coverage_diagnosis(
            params.get("symbols") or [],
            freq=params.get("freq", "quarterly"),
            sample_size=int(params.get("sample_size", 2) or 2),
        )
    elif action == "inspect_statement_pit":
        diagnostic_result = run_statement_pit_inspection(
            symbols=params.get("symbols") or [],
            inspect_freq=params.get("inspect_freq", "quarterly"),
            audit_symbol_limit=int(params.get("audit_symbol_limit", 3) or 3),
            audit_limit_per_symbol=int(params.get("audit_limit_per_symbol", 5) or 5),
            source_symbol=params.get("source_symbol"),
            source_sample_size=int(params.get("source_sample_size", 2) or 2),
        )
    else:
        raise ValueError(f"Unsupported diagnostic action: {action}")

    finished_at = datetime.now()
    if progress_callback:
        progress_callback({"type": "stage_complete", "stage": action, "stage_index": 1, "total_stages": 1})
    return _build_diagnostic_job_result(
        action=action,
        params=params,
        diagnostic_result=diagnostic_result,
        started_at=started_at,
        finished_at=finished_at,
    )


def _store_diagnostic_result_if_needed(result: JobResult) -> None:
    state_key = _diagnostic_state_key(str(result.get("job_name") or ""))
    if not state_key:
        return
    diagnostic_result = (result.get("details") or {}).get("diagnostic_result")
    if diagnostic_result is not None:
        st.session_state[state_key] = diagnostic_result


def _clear_running_job() -> None:
    st.session_state.running_job = None


def _dispatch_job(job: dict[str, Any], *, progress_callback: Any = None) -> JobResult:
    action = job["action"]
    params = dict(job["params"])

    if _diagnostic_state_key(action):
        return _dispatch_diagnostic_job(action, params, progress_callback=progress_callback)
    if action == "pipeline_core_market_data":
        params["progress_callback"] = progress_callback
        return run_pipeline_core_market_data(**params)
    if action == "daily_market_update":
        params["progress_callback"] = progress_callback
        return run_daily_market_update(**params)
    if action == "weekly_fundamental_refresh":
        params["progress_callback"] = progress_callback
        return run_weekly_fundamental_refresh(**params)
    if action == "extended_statement_refresh":
        params["progress_callback"] = progress_callback
        return run_extended_statement_refresh(**params)
    if action == "rebuild_statement_shadow":
        params["progress_callback"] = progress_callback
        return run_rebuild_statement_shadow(**params)
    if action == "metadata_refresh":
        return run_metadata_refresh(**params)
    if action == "discover_etf_provider_source_map":
        return run_discover_etf_provider_source_map(**params)
    if action == "collect_etf_operability_provider":
        params["progress_callback"] = progress_callback
        return run_collect_etf_operability_provider(**params)
    if action == "collect_etf_holdings_exposure":
        params["progress_callback"] = progress_callback
        return run_collect_etf_holdings_exposure(**params)
    if action == "collect_macro_market_context":
        params["progress_callback"] = progress_callback
        return run_collect_macro_market_context(**params)
    if action == "collect_market_sentiment":
        params["progress_callback"] = progress_callback
        return run_collect_market_sentiment(**params)
    if action == "collect_sec_form25_delistings":
        return run_collect_sec_form25_delistings(**params)
    if action == "collect_symbol_directory_snapshots":
        return run_collect_symbol_directory_snapshots(**params)
    if action == "collect_sec_company_ticker_crosscheck":
        return run_collect_sec_company_ticker_crosscheck(**params)
    if action == "collect_computed_snapshot_lifecycle":
        return run_collect_computed_snapshot_lifecycle(**params)
    if action == "collect_fomc_calendar":
        return run_collect_fomc_calendar(**params)
    if action == "collect_earnings_calendar":
        return run_collect_earnings_calendar(**params)
    if action == "collect_futures_ohlcv":
        return run_collect_futures_ohlcv(**params)
    if action == "collect_macro_calendar":
        return run_collect_macro_calendar(**params)
    if action == "import_bls_macro_calendar_ics":
        return run_import_bls_macro_calendar_ics(**params)
    if action == "collect_ohlcv":
        params["progress_callback"] = progress_callback
        return run_collect_ohlcv(**params)
    if action == "collect_fundamentals":
        return run_collect_fundamentals(**params)
    if action == "calculate_factors":
        return run_calculate_factors(**params)
    if action == "collect_asset_profiles":
        return run_collect_asset_profiles(**params)
    if action == "collect_financial_statements":
        params["progress_callback"] = progress_callback
        return run_collect_financial_statements(**params)
    raise ValueError(f"Unsupported job action: {action}")


def _run_scheduled_job(progress_callback: Any = None) -> None:
    job = st.session_state.running_job
    if job is None:
        return

    try:
        with st.spinner(job["spinner_text"]):
            result = _dispatch_job(job, progress_callback=progress_callback)
    except Exception as exc:
        result = {
            "job_name": job["job_name"],
            "status": "failed",
            "started_at": None,
            "finished_at": None,
            "duration_sec": 0.0,
            "rows_written": 0,
            "symbols_requested": len(job.get("params", {}).get("symbols", []) or []),
            "failed_symbols": job.get("params", {}).get("symbols", []) or [],
            "message": f"Unhandled UI job execution error: {exc}",
            "details": {"action": job["action"]},
        }

    result["run_metadata"] = job.get("run_metadata") or {}
    _store_diagnostic_result_if_needed(result)
    _push_result(result)
    st.session_state.last_completed_result = result
    if job.get("action") in {"extended_statement_refresh", "collect_financial_statements", "rebuild_statement_shadow"}:
        clear_backtest_preview_caches()
    _clear_running_job()
    st.rerun()


def _render_running_banner() -> None:
    job = st.session_state.running_job
    if not job:
        return
    symbol_count = len(job.get("params", {}).get("symbols", []) or [])
    count_suffix = f" Target symbols: `{symbol_count}`." if symbol_count else ""
    elapsed_suffix = f" 경과 `{_format_job_elapsed(job)}`."
    st.warning(
        f'`{job["job_name"]}` is currently running. All execution buttons are temporarily disabled until it finishes.{count_suffix}{elapsed_suffix}'
    )


def _render_runtime_build_indicator() -> None:
    with st.container(border=True):
        st.markdown("### Runtime / Build")
        st.caption(
            "이 정보는 현재 Streamlit 프로세스가 어떤 코드 상태로 떠 있는지 보여줍니다. "
            "코드를 고친 뒤 결과가 기대와 다르면 먼저 이 `Loaded At`과 `Git SHA`를 확인하는 것이 좋습니다."
        )
        col1, col2, col3 = st.columns(3)
        col1.metric("Runtime Marker", _runtime_marker)
        col2.metric("Loaded At", _runtime_loaded_at_text())
        col3.metric("Git SHA", _runtime_git_sha or "unknown")


def _render_ingestion_runtime_build_indicator() -> None:
    with st.container(border=True):
        st.markdown("### Runtime / Build")
        st.caption(
            "이 정보는 현재 Streamlit 프로세스가 어떤 코드 상태로 떠 있는지 보여줍니다. "
            "코드를 고친 뒤 결과가 기대와 다르면 먼저 이 `Loaded At`과 `Git SHA`를 확인하는 것이 좋습니다."
        )
        _render_ingestion_meta_grid(
            [
                ("Runtime Marker", _runtime_marker),
                ("Loaded At", _runtime_loaded_at_text()),
                ("Git SHA", _runtime_git_sha or "unknown"),
            ]
        )


def _render_inline_running_hint(action: str, label: str, *, job: dict[str, Any] | None = None) -> None:
    if _is_running_action(action):
        st.info(
            f"`{label}` 실행 중입니다. 현재 실행은 동기 처리라 job이 끝난 뒤 화면이 다시 갱신됩니다. "
            f"경과 `{_format_job_elapsed(job or st.session_state.running_job)}`."
        )


def _render_ingestion_collection_section_selector() -> str:
    pending_section = st.session_state.get("ingestion_collection_section_pending")
    if pending_section is not None:
        del st.session_state["ingestion_collection_section_pending"]

    running_or_pending_job = st.session_state.running_job or st.session_state.pending_job
    forced_section = _infer_ingestion_collection_section(running_or_pending_job) if running_or_pending_job else None
    selected_section = (
        pending_section
        or forced_section
        or st.session_state.get("ingestion_collection_section_choice")
        or INGESTION_COLLECTION_OPERATIONAL
    )
    if selected_section not in INGESTION_COLLECTION_SECTIONS:
        selected_section = INGESTION_COLLECTION_OPERATIONAL

    if forced_section or pending_section or "ingestion_collection_section_choice" not in st.session_state:
        st.session_state.ingestion_collection_section_choice = selected_section

    selected = st.pills(
        "수집 작업 구분",
        options=list(INGESTION_COLLECTION_SECTIONS),
        key="ingestion_collection_section_choice",
        label_visibility="collapsed",
    )
    if selected not in INGESTION_COLLECTION_SECTIONS:
        selected = selected_section
    st.session_state.ingestion_collection_section = selected
    return str(selected)


def _build_progress_callback(job: dict[str, Any], *, label: str) -> Any:
    action = job.get("action")
    symbol_count = len(job.get("params", {}).get("symbols", []) or [])

    if action not in {
        "collect_ohlcv",
        "pipeline_core_market_data",
        "daily_market_update",
        "weekly_fundamental_refresh",
        "extended_statement_refresh",
        "rebuild_statement_shadow",
        "collect_financial_statements",
    } or symbol_count < 100:
        _render_inline_running_hint(action, label, job=job)
        return None

    progress_text = st.empty()
    progress_meta = st.empty()
    progress_bar = st.progress(0)

    if action in {"collect_ohlcv", "daily_market_update"}:
        progress_text.info(f"`{label}` 실행 중입니다. OHLCV batch 진행률과 경과 시간을 표시합니다.")
    elif action in {"extended_statement_refresh", "collect_financial_statements"}:
        progress_text.info(f"`{label}` 실행 중입니다. statement ingestion 진행률과 경과 시간을 표시합니다.")
    else:
        progress_text.info(f"`{label}` 실행 중입니다. pipeline stage 진행률과 경과 시간을 표시합니다.")

    def _callback(event: dict[str, Any]) -> None:
        event_type = event.get("event")

        if action in {"collect_ohlcv", "daily_market_update"} and event_type == "batch_progress":
            total_symbols = max(int(event.get("total_symbols", symbol_count) or symbol_count), 1)
            processed_symbols = min(int(event.get("processed_symbols", 0) or 0), total_symbols)
            percent = int((processed_symbols / total_symbols) * 100)
            progress_bar.progress(percent)
            progress_meta.caption(
                "처리 "
                f"`{processed_symbols}/{total_symbols}` symbols | "
                f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
                f"경과 `{_format_job_elapsed(job)}` | "
                f"저장 rows `{event.get('rows_written', 0)}` | "
                f"rate-limited `{event.get('rate_limited_symbols', 0)}`"
            )
            return

        if action in {"collect_ohlcv", "daily_market_update"} and event_type == "rate_limit_cooldown":
            progress_text.warning(
                f"`{label}`에서 provider rate-limit이 감지되었습니다. 다음 batch 전에 cooldown을 적용합니다."
            )
            progress_meta.caption(
                f"처리 `{event.get('processed_symbols', 0)}/{event.get('total_symbols', symbol_count)}` symbols | "
                f"cooldown `{event.get('cooldown_sec', 0)}` sec | "
                f"경과 `{_format_job_elapsed(job)}` | "
                f"next chunk `{event.get('current_chunk_size', 0)}` | "
                f"workers `{event.get('current_max_workers', 0)}`"
            )
            return

        if action in {"pipeline_core_market_data", "weekly_fundamental_refresh"}:
            fallback_total_stages = 3 if action == "pipeline_core_market_data" else 2
            total_stages = max(int(event.get("total_stages", fallback_total_stages) or fallback_total_stages), 1)
            stage_index = int(event.get("stage_index", 1) or 1)
            stage = str(event.get("stage", "") or "").upper()

            if event_type == "stage_start":
                percent = int(((stage_index - 1) / total_stages) * 100)
                progress_bar.progress(percent)
                progress_meta.caption(f"현재 stage: `{stage}` ({stage_index}/{total_stages}) | 경과 `{_format_job_elapsed(job)}`")
                return

            if event_type == "stage_complete":
                percent = int((stage_index / total_stages) * 100)
                progress_bar.progress(percent)
                progress_meta.caption(f"완료 stage: `{stage}` ({stage_index}/{total_stages}) | 경과 `{_format_job_elapsed(job)}`")
                return

            if event_type == "batch_progress":
                total_symbols = max(int(event.get("total_symbols", symbol_count) or symbol_count), 1)
                processed_symbols = min(int(event.get("processed_symbols", 0) or 0), total_symbols)
                stage_fraction = processed_symbols / total_symbols
                percent = int((((stage_index - 1) + stage_fraction) / total_stages) * 100)
                progress_bar.progress(percent)
                if action == "pipeline_core_market_data":
                    progress_meta.caption(
                        "현재 stage: `OHLCV` | "
                        f"처리 `{processed_symbols}/{total_symbols}` symbols | "
                        f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
                        f"경과 `{_format_job_elapsed(job)}` | "
                        f"저장 rows `{event.get('rows_written', 0)}`"
                    )
                return

        if action in {"extended_statement_refresh", "collect_financial_statements"} and event_type == "batch_progress":
            total_symbols = max(int(event.get("total_symbols", symbol_count) or symbol_count), 1)
            processed_symbols = min(int(event.get("processed_symbols", 0) or 0), total_symbols)
            percent = int((processed_symbols / total_symbols) * 100)
            progress_bar.progress(percent)
            progress_meta.caption(
                "처리 "
                f"`{processed_symbols}/{total_symbols}` symbols | "
                f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
                f"경과 `{_format_job_elapsed(job)}` | "
                f"values `{event.get('inserted_values', 0)}` | "
                f"labels `{event.get('upserted_labels', 0)}` | "
                f"filings `{event.get('upserted_filings', 0)}` | "
                f"failed `{event.get('failed_symbols_count', 0)}`"
            )
            return

        if event_type in {"stage_start", "stage_complete"}:
            total_stages = max(int(event.get("total_stages", 1) or 1), 1)
            stage_index = int(event.get("stage_index", 1) or 1)
            stage = str(event.get("stage", "") or "").upper()
            if event_type == "stage_start":
                percent = int(((stage_index - 1) / total_stages) * 100)
                progress_bar.progress(percent)
                progress_meta.caption(f"현재 stage: `{stage}` ({stage_index}/{total_stages}) | 경과 `{_format_job_elapsed(job)}`")
            else:
                percent = int((stage_index / total_stages) * 100)
                progress_bar.progress(percent)
                progress_meta.caption(f"완료 stage: `{stage}` ({stage_index}/{total_stages}) | 경과 `{_format_job_elapsed(job)}`")

    return _callback


def _render_last_completed_result() -> None:
    result = st.session_state.last_completed_result
    if result is None:
        return

    st.subheader("최근 완료된 수집")
    _render_result_summary(result)
    st.session_state.last_completed_result = None


def _render_inline_last_completed_result(*job_names: str) -> None:
    result = st.session_state.last_completed_result
    if result is None:
        return
    if result.get("job_name") not in set(job_names):
        return
    st.markdown("#### 최근 완료된 수집")
    _render_result_summary(result)
    st.session_state.last_completed_result = None


def _render_earnings_diagnostics(details: dict[str, Any]) -> None:
    diagnostics = [item for item in details.get("symbol_diagnostics") or [] if isinstance(item, dict)]
    if not diagnostics:
        return
    issue_rows = [
        {
            "Symbol": item.get("symbol") or "-",
            "Status": item.get("status") or "-",
            "Reason": item.get("reason") or "-",
            "Detail": item.get("detail") or "-",
            "Provider Dates": ", ".join(str(value) for value in item.get("provider_dates") or []),
            "Event Dates": ", ".join(str(value) for value in item.get("event_dates") or []),
        }
        for item in diagnostics
        if item.get("status") != "event_found"
    ]
    with st.expander(f"Earnings Diagnostics ({len(issue_rows)} issue symbols)", expanded=False):
        metric_cols = st.columns(4)
        metric_cols[0].metric("With Events", details.get("symbols_with_events") or 0)
        metric_cols[1].metric("Missing", details.get("symbols_missing_count") or len(details.get("missing_symbols") or []))
        metric_cols[2].metric("Failed", details.get("symbols_failed_count") or len(details.get("failed_symbols") or []))
        metric_cols[3].metric("Events Found", details.get("events_found") or 0)
        reason_rows = [
            {"Status": "missing", "Reason": key, "Count": value}
            for key, value in (details.get("missing_reason_counts") or {}).items()
        ] + [
            {"Status": "failed", "Reason": key, "Count": value}
            for key, value in (details.get("failed_reason_counts") or {}).items()
        ]
        if reason_rows:
            st.caption("Issue reason counts")
            st.dataframe(pd.DataFrame(reason_rows), width="stretch", hide_index=True)
        if issue_rows:
            st.caption("Symbol-level issues")
            st.dataframe(pd.DataFrame(issue_rows), width="stretch", hide_index=True)
        else:
            st.success("All requested symbols had at least one earnings date in the selected window.")


def _render_result_summary(result: JobResult) -> None:
    job_name = str(result.get("job_name") or "")
    guide = _job_guide(job_name)
    if guide:
        st.markdown(f"### {_job_title(job_name)}")
        st.caption(f"내부 job id: `{job_name}`")
        st.write(guide.get("purpose") or "")
        _render_ingestion_meta_rows(
            [
                ("저장 위치", [str(item) for item in guide.get("targets") or []], True),
                ("사용 위치", [str(item) for item in guide.get("used_by") or []], False),
            ]
        )

    banner = _status_to_banner(result["status"])
    banner(f'[{_job_title(job_name)}] {result["message"]}')

    failed_count = len(result.get("failed_symbols") or [])
    status = str(result.get("status") or "")
    status_label, rows_label, requested_label, failed_label, duration_label = _result_metric_labels(job_name)
    _render_ingestion_stat_grid(
        [
            (status_label, _status_label(status), status),
            (rows_label, _format_count(result.get("rows_written")), None),
            (requested_label, _format_count(result.get("symbols_requested")), None),
            (failed_label, _format_count(failed_count), None),
            (duration_label, _format_duration(result.get("duration_sec")), None),
        ]
    )
    _render_result_interpretation(result)

    run_metadata = result.get("run_metadata") or {}
    if run_metadata:
        _render_ingestion_meta_grid(
            [
                ("실행 모드", str(run_metadata.get("execution_mode") or "-")),
                ("파이프라인", str(run_metadata.get("pipeline_type") or "-")),
                ("Runtime Marker", str(run_metadata.get("runtime_marker") or "-")),
            ]
        )
        runtime_loaded_at = run_metadata.get("runtime_loaded_at")
        git_sha = run_metadata.get("git_sha")
        extra_parts = []
        if runtime_loaded_at:
            extra_parts.append(f"loaded_at=`{runtime_loaded_at}`")
        if git_sha:
            extra_parts.append(f"git_sha=`{git_sha}`")
        if extra_parts:
            st.caption(" | ".join(extra_parts))

    if failed_count:
        st.write("누락 / 실패 대상:", ", ".join((result.get("failed_symbols") or [])[:20]))

    _render_result_guidance(result)
    _render_result_data_quality_notes(job_name)

    _render_earnings_diagnostics(result.get("details") or {})

    with st.expander("상세 결과 JSON", expanded=False):
        st.json(result)

    details = result.get("details") or {}
    if any(
        details.get(key)
        for key in (
            "rate_limited_symbols",
            "provider_no_data_symbols",
            "excluded_symbols",
            "cooldown_events",
            "rerun_rate_limited_payload",
            "rerun_missing_payload",
            "timing_breakdown",
        )
    ):
        with st.expander("가격 수집 진단", expanded=False):
            diag_col1, diag_col2, diag_col3, diag_col4 = st.columns(4)
            diag_col1.metric("Rate-Limited", len(details.get("rate_limited_symbols") or []))
            diag_col2.metric("Provider No-Data", len(details.get("provider_no_data_symbols") or []))
            diag_col3.metric("Filtered Symbols", len(details.get("excluded_symbols") or []))
            diag_col4.metric("Cooldown Events", len(details.get("cooldown_events") or []))
            timing_breakdown = details.get("timing_breakdown") or {}
            if timing_breakdown:
                st.caption("시간 breakdown")
                time_col1, time_col2, time_col3, time_col4 = st.columns(4)
                time_col1.metric("Fetch (sec)", timing_breakdown.get("fetch_sec", 0.0))
                time_col2.metric("Delete (sec)", timing_breakdown.get("delete_sec", 0.0))
                time_col3.metric("Upsert (sec)", timing_breakdown.get("upsert_sec", 0.0))
                time_col4.metric("Cooldown (sec)", timing_breakdown.get("cooldown_sleep_sec", 0.0))
                time_col5, time_col6, time_col7, time_col8 = st.columns(4)
                time_col5.metric("Retry Sleep (sec)", timing_breakdown.get("retry_sleep_sec", 0.0))
                time_col6.metric("Inter-batch Sleep (sec)", timing_breakdown.get("inter_batch_sleep_sec", 0.0))
                time_col7.metric("Batch Count", timing_breakdown.get("batch_count", 0))
                time_col8.metric("Avg Fetch / Batch", timing_breakdown.get("avg_fetch_sec_per_batch", 0.0))
            if details.get("rerun_rate_limited_payload"):
                st.caption("rate-limit 대상 재실행 payload")
                st.code(details["rerun_rate_limited_payload"], language="text")
            if details.get("rerun_missing_payload"):
                st.caption("missing-provider 대상 재실행 payload")
                st.code(details["rerun_missing_payload"], language="text")
            provider_message_batches = details.get("provider_message_batches") or []
            if provider_message_batches:
                st.caption("Provider message 일부")
                st.json(provider_message_batches[:5])

    steps = details.get("steps")
    if steps:
        with st.expander("파이프라인 단계", expanded=False):
            rows = []
            for idx, step in enumerate(steps, start=1):
                rows.append(
                    {
                        "step": idx,
                        "job_name": step["job_name"],
                        "status": step["status"],
                        "rows_written": step.get("rows_written") or 0,
                        "failed_symbols": len(step.get("failed_symbols") or []),
                        "message": step["message"],
                    }
                )
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    artifact_info = details.get("result_artifacts") or {}
    if artifact_info:
        with st.expander("실행 artifact", expanded=False):
            st.caption(
                "Each run now emits a standardized JSON artifact, and when symbol-level issues exist it also emits a standardized failure CSV."
            )
            st.json(artifact_info, expanded=False)


def _render_recent_results() -> None:
    st.subheader("세션 내 최근 수집")
    results = st.session_state.recent_results
    if not results:
        st.info("현재 세션에서 실행한 수집 작업이 아직 없습니다.")
        return

    for idx, result in enumerate(results):
        with st.container(border=True):
            job_name = str(result.get("job_name") or "")
            st.markdown(f"**{idx + 1}. {_job_title(job_name)}**")
            st.caption(f"내부 job id: `{job_name}`")
            st.write(
                f'상태: `{_status_label(result["status"])}` | '
                f'시작: `{result["started_at"]}` | '
                f'종료: `{result["finished_at"]}` | '
                f'누락 / 실패: `{len(result.get("failed_symbols") or [])}`'
            )
            run_metadata = result.get("run_metadata") or {}
            symbol_source = run_metadata.get("symbol_source")
            execution_mode = run_metadata.get("execution_mode")
            pipeline_type = run_metadata.get("pipeline_type")
            execution_context = run_metadata.get("execution_context")
            if execution_mode:
                st.write(f"실행 모드: `{execution_mode}`")
            if pipeline_type:
                st.write(f"파이프라인: `{pipeline_type}`")
            if symbol_source:
                st.write(f"심볼 소스: `{symbol_source}`")
            if execution_context:
                st.write(f"실행 맥락: {execution_context}")
            st.write(result["message"])
            if result.get("failed_symbols"):
                st.write("누락 / 실패 대상:", ", ".join(result["failed_symbols"]))


def _get_recent_files(directory: Path, pattern: str, limit: int = 5) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(
        directory.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:limit]


def _read_tail(path: Path, max_lines: int = 20) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as exc:
        return f"Failed to read log file: {exc}"

    if not lines:
        return "(empty file)"
    return "\n".join(lines[-max_lines:])


def _render_recent_logs() -> None:
    st.subheader("최근 로그")
    st.caption("`logs/` 아래에서 최근 갱신된 `*.log` 5개를 보여주고, 선택한 파일의 마지막 20줄을 표시합니다.")
    log_files = _get_recent_files(LOG_DIR, "*.log", limit=5)
    if not log_files:
        st.info("표시할 로그 파일이 없습니다.")
        return

    labels = [p.name for p in log_files]
    selected_name = st.selectbox("로그 파일", labels, key="recent_log_file")
    selected = next(p for p in log_files if p.name == selected_name)

    st.caption(f"경로: {selected}")
    st.code(_read_tail(selected, max_lines=20), language="text")


def _render_failure_csv_preview() -> None:
    st.subheader("실패 CSV 미리보기")
    st.caption(
        "`csv/` 아래의 최근 `*failures*.csv` artifact를 보여줍니다. "
        "심볼 단위 문제가 있는 실행은 표준 failure CSV를 남기므로, 재실행 대상을 확인할 때 사용합니다."
    )
    csv_files = _get_recent_files(CSV_DIR, "*failures*.csv", limit=5)
    if not csv_files:
        st.info("표시할 failure CSV가 없습니다.")
        return

    labels = [p.name for p in csv_files]
    selected_name = st.selectbox("Failure CSV", labels, key="failure_csv_file")
    selected = next(p for p in csv_files if p.name == selected_name)

    st.caption(f"경로: {selected}")
    try:
        df = pd.read_csv(selected)
    except Exception as exc:
        st.error(f"Failed to read failure CSV: {exc}")
        return

    if df.empty:
        st.info("Selected failure CSV is empty.")
        return

    st.dataframe(df.head(20), use_container_width=True)


def _history_record_label(record: dict[str, Any]) -> str:
    started_at = record.get("started_at") or "-"
    if isinstance(started_at, str) and len(started_at) >= 16:
        started_at = started_at[5:16]
    job_name = record.get("job_name") or "-"
    status = _status_label(record.get("status"))
    return f"{started_at} · {_job_title(job_name)} · {status}"


def _history_record_full_label(record: dict[str, Any]) -> str:
    started_at = record.get("started_at") or "-"
    job_name = record.get("job_name") or "-"
    status = _status_label(record.get("status"))
    return f"{started_at} | {_job_title(job_name)} | {status}"


def _related_log_patterns(job_name: str | None) -> list[str]:
    mapping = {
        "daily_market_update": ["*price*.log", "*ohlcv*.log"],
        "collect_ohlcv": ["*price*.log", "*ohlcv*.log"],
        "pipeline_core_market_data": ["*price*.log", "*fundamentals*.log", "*factors*.log"],
        "weekly_fundamental_refresh": ["*fundamentals*.log", "*factors*.log"],
        "collect_fundamentals": ["*fundamentals*.log"],
        "calculate_factors": ["*factors*.log"],
        "extended_statement_refresh": ["*financial_statements*.log", "*fundamentals*.log", "*factors*.log"],
        "collect_financial_statements": ["*financial_statements*.log"],
        "rebuild_statement_shadow": ["*fundamentals*.log", "*factors*.log"],
        "collect_asset_profiles": ["*profile*.log"],
        "metadata_refresh": ["*profile*.log"],
    }
    return mapping.get(str(job_name or ""), ["*.log"])


def _find_related_logs(record: dict[str, Any], limit: int = 5) -> list[Path]:
    matched: list[Path] = []
    seen: set[Path] = set()
    for pattern in _related_log_patterns(record.get("job_name")):
        for path in _get_recent_files(LOG_DIR, pattern, limit=limit):
            if path in seen:
                continue
            seen.add(path)
            matched.append(path)
    return matched[:limit]


def _render_run_history_inspector(history: list[dict[str, Any]]) -> None:
    st.markdown("#### 실행 기록 상세")
    st.caption(
        "저장된 실행 기록을 선택해 입력값, 파이프라인 단계, runtime marker, artifact, 관련 로그를 확인합니다."
    )
    options = list(range(len(history)))
    st.markdown("**저장된 실행 선택**")
    selected_idx = st.selectbox(
        "저장된 실행 선택",
        options=options,
        format_func=lambda idx: _history_record_label(history[idx]),
        key="persistent_run_history_inspector",
        label_visibility="collapsed",
    )
    selected = history[selected_idx]
    selected_label = _history_record_full_label(selected)
    st.markdown(
        f'<div class="ingestion-select-caption">현재 선택: {escape(selected_label)}</div>',
        unsafe_allow_html=True,
    )
    _render_result_summary(selected)

    related_logs = _find_related_logs(selected)
    if related_logs:
        with st.expander("관련 로그", expanded=False):
            log_labels = [path.name for path in related_logs]
            log_name = st.selectbox(
                "관련 로그 파일",
                options=log_labels,
                key=f"run_inspector_log_{selected.get('started_at')}_{selected.get('job_name')}",
            )
            chosen = next(path for path in related_logs if path.name == log_name)
            st.caption(f"경로: {chosen}")
            st.code(_read_tail(chosen, max_lines=20), language="text")


def _render_persistent_run_history() -> None:
    st.subheader("누적 실행 기록")
    history = load_run_history(limit=30)
    if not history:
        st.info("아직 저장된 실행 기록이 없습니다.")
        return

    st.caption(f"경로: {HISTORY_FILE}")
    rows = []
    for item in history:
        run_metadata = item.get("run_metadata") or {}
        input_params = run_metadata.get("input_params") or {}
        rows.append(
            {
                "started_at": item.get("started_at"),
                "job": _job_title(item.get("job_name")),
                "job_name": item.get("job_name"),
                "status": item.get("status"),
                "mode": run_metadata.get("execution_mode"),
                "pipeline": run_metadata.get("pipeline_type"),
                "source": run_metadata.get("symbol_source"),
                "runtime": run_metadata.get("runtime_marker"),
                "symbols": item.get("symbols_requested"),
                "rows_written": item.get("rows_written"),
                "duration_sec": item.get("duration_sec"),
                "context": run_metadata.get("execution_context"),
                "params": ", ".join(f"{k}={v}" for k, v in input_params.items()),
                "message": item.get("message"),
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(
        "최근 실행 기록에는 runtime/build metadata와 표준 artifact 경로가 함께 저장됩니다. 아래 상세 보기에서 전체 payload를 확인할 수 있습니다."
    )
    _render_run_history_inspector(history)


def _render_ingestion_records_section() -> None:
    st.info(
        "실행 기록 / 결과: 현재 세션에서 끝난 수집, 저장된 누적 실행 기록, 관련 로그와 failure CSV를 한곳에서 확인합니다. "
        "수집 실행 화면과 분리해, 완료 후 원인 파악과 재실행 payload 확인에 집중할 수 있게 했습니다."
    )
    _render_recent_results()
    st.divider()
    _render_persistent_run_history()
    st.divider()
    _render_recent_logs()
    st.divider()
    _render_failure_csv_preview()


def _render_check_result(result: dict[str, Any]) -> None:
    status = result.get("status")
    message = result.get("message", "")
    if status == "ok":
        st.info(message)
    elif status == "warning":
        st.warning(message)
    else:
        st.error(message)

    details = result.get("details") or {}
    if details:
        with st.expander("Preflight 상세", expanded=False):
            st.json(details)


def _is_blocking(result: dict[str, Any]) -> bool:
    return result.get("status") == "error"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, (pd.Timestamp, date)):
        return str(value)
    return value


def _render_statement_pit_inspection_result(result: dict[str, Any]) -> None:
    coverage_df = result.get("coverage_df")
    audit_df = result.get("audit_df")
    source_payload = result.get("source_payload")
    source_symbol = result.get("source_symbol")
    inspect_freq = result.get("inspect_freq")
    audit_scope = result.get("audit_scope") or []

    st.markdown("#### Inspection Result")
    summary_cols = st.columns(4)
    summary_cols[0].metric("Inspection Freq", inspect_freq or "-")
    summary_cols[1].metric("Coverage Symbols", len(coverage_df) if isinstance(coverage_df, pd.DataFrame) else 0)
    summary_cols[2].metric("Audit Symbols", len(audit_scope))
    summary_cols[3].metric("Source Sample", source_symbol or "-")

    if isinstance(coverage_df, pd.DataFrame) and not coverage_df.empty:
        st.markdown("##### Coverage Summary")
        st.caption(
            "이 표는 DB에 이미 저장된 quarterly/annual statement ledger coverage를 읽습니다. "
            "`min_period_end`는 히스토리가 어디까지 오래 내려가는지, `max_period_end`는 최신 분기/연도 기준을 뜻합니다."
        )
        view = coverage_df.copy()
        for column in ["min_period_end", "max_period_end", "min_available_at", "max_available_at"]:
            if column in view.columns:
                view[column] = pd.to_datetime(view[column], errors="coerce").dt.strftime("%Y-%m-%d")
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.info("Coverage summary returned no rows for the selected symbols/frequency.")

    if isinstance(audit_df, pd.DataFrame) and not audit_df.empty:
        st.markdown("##### Timing Audit")
        st.caption(
            "이 표는 선택한 심볼의 최근 timing row를 보여줍니다. "
            "`period_end`는 재무 기준 시점, `filing_date/accepted_at/available_at`는 실제로 언제 사용 가능해졌는지 확인하는 용도입니다."
        )
        audit_view = audit_df.copy()
        for column in ["period_start", "period_end", "filing_date", "accepted_at", "available_at", "report_date"]:
            if column in audit_view.columns:
                audit_view[column] = pd.to_datetime(audit_view[column], errors="coerce").astype(str).replace("NaT", "")
        st.dataframe(audit_view, use_container_width=True, hide_index=True)
    else:
        st.info("Timing audit returned no rows for the selected audit scope.")

    if source_payload:
        st.markdown("##### Source Payload Inspection")
        st.caption(
            "이 섹션만 live EDGAR sample을 읽습니다. "
            "`form_counts`와 `fiscal_period_counts`는 원본 source가 어떤 filing/form 조합을 주는지, "
            "`timing_field_inventory`는 timing 관련 필드가 실제로 얼마나 채워져 있는지 보는 용도입니다."
        )
        top_level = {
            "symbol": source_payload.get("symbol"),
            "statement_fact_count": source_payload.get("statement_fact_count"),
            "filing_count": source_payload.get("filing_count"),
            "form_counts": source_payload.get("form_counts"),
            "fiscal_period_counts": source_payload.get("fiscal_period_counts"),
            "timing_field_inventory": source_payload.get("timing_field_inventory"),
        }
        st.json(_json_safe(top_level), expanded=False)

        sample_filings = source_payload.get("sample_filings") or []
        if sample_filings:
            st.caption("Sample Filings")
            st.dataframe(pd.DataFrame(_json_safe(sample_filings)), use_container_width=True, hide_index=True)

        sample_facts = source_payload.get("sample_facts") or []
        if sample_facts:
            st.caption("Sample Facts")
            st.dataframe(pd.DataFrame(_json_safe(sample_facts)), use_container_width=True, hide_index=True)
    else:
        st.info("Source payload inspection was not available for the selected symbol.")


def _render_price_stale_diagnosis_result(result: dict[str, Any]) -> None:
    st.markdown("#### Diagnosis Result")
    details = result.get("details") or {}
    status = result.get("status")
    if status == "ok":
        st.success(result.get("message") or "Price stale diagnosis completed.")
    elif status == "warning":
        st.warning(result.get("message") or "Price stale diagnosis completed with warnings.")
    else:
        st.error(result.get("message") or "Price stale diagnosis failed.")

    st.caption(
        "이 결과는 `DB latest date + provider 재조회 + asset profile status`를 합쳐서 "
        "이 심볼이 로컬 수집 누락인지, provider gap인지, 상폐/심볼변경 쪽인지 좁혀보는 진단용 결과입니다."
    )
    meta_cols = st.columns(4)
    meta_cols[0].metric("Requested", details.get("requested_count", 0))
    meta_cols[1].metric("Effective Trading End", details.get("effective_end_date", "-"))
    meta_cols[2].metric("Daily Timeframe", details.get("timeframe", "-"))
    meta_cols[3].metric("Probe Windows", ", ".join(details.get("provider_probe_periods") or []))

    invalid_symbols = details.get("invalid_symbols") or []
    if invalid_symbols:
        st.caption("Ignored invalid symbols:")
        st.code(", ".join(invalid_symbols))

    diagnosis_counts = details.get("diagnosis_counts") or {}
    if diagnosis_counts:
        st.markdown("##### Diagnosis Summary")
        summary_df = pd.DataFrame(
            [{"Diagnosis": diagnosis, "Count": count} for diagnosis, count in diagnosis_counts.items()]
        ).sort_values(["Count", "Diagnosis"], ascending=[False, True])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    rows = details.get("rows") or []
    if rows:
        st.markdown("##### Detailed Classification")
        st.caption(
            "`local_ingestion_gap`이면 DB만 뒤처진 것이고, "
            "`provider_source_gap`이면 provider도 최신 row를 안 주는 상태이며, "
            "`likely_delisted_or_symbol_changed`이면 상폐/심볼변경 가능성을 먼저 보는 것이 좋습니다."
        )
        diagnosis_df = pd.DataFrame(rows).rename(
            columns={
                "symbol": "Symbol",
                "db_latest": "DB Latest",
                "db_lag_days": "DB Lag Days",
                "db_row_count": "DB Rows",
                "provider_latest": "Provider Latest",
                "provider_lag_days": "Provider Lag Days",
                "probe_status": "Probe Status",
                "profile_status": "Profile Status",
                "delisted_at": "Delisted At",
                "diagnosis": "Diagnosis",
                "recommended_action": "Recommended Action",
                "note": "Note",
            }
        )
        st.dataframe(diagnosis_df, use_container_width=True, hide_index=True)

    probe_rows = details.get("probe_rows") or []
    if probe_rows:
        with st.expander("Provider Probe Details", expanded=False):
            st.caption(
                "각 심볼을 `5d`, `1mo`, `3mo`로 다시 조회해 최신 row 유무와 provider 메시지를 비교합니다. "
                "여기서 provider도 최신 데이터를 주는지, 아예 no-data인지, rate limit이 있었는지를 봅니다."
            )
            probe_df = pd.DataFrame(probe_rows).rename(
                columns={
                    "symbol": "Symbol",
                    "period": "Probe Window",
                    "row_count": "Rows",
                    "latest_date": "Latest Date",
                    "rate_limit_hit": "Rate Limit",
                    "provider_no_data_hit": "Provider No-Data",
                    "provider_output_excerpt": "Provider Output Excerpt",
                }
            )
            st.dataframe(probe_df, use_container_width=True, hide_index=True)

    payload = details.get("targeted_daily_market_payload")
    if payload is not None:
        st.markdown("##### Suggested Daily Market Update Payload")
        st.caption(
            "Only symbols classified as `local_ingestion_gap` or `local_ingestion_gap_partial` are included here. "
            "즉 provider에는 더 최신 row가 있는데 DB만 뒤처진 경우에만 재수집 payload를 만듭니다."
        )
        left, right = st.columns(2)
        left.metric("Refresh Symbols", len(payload.get("symbols") or []))
        right.metric("Suggested Window", f"{payload.get('start')} -> {payload.get('end')}")
        st.code(payload.get("payload_block") or "", language="text")


def _render_statement_coverage_diagnosis_result(result: dict[str, Any]) -> None:
    st.markdown("#### Diagnosis Result")
    details = result.get("details") or {}
    status = result.get("status")
    if status == "ok":
        st.success(result.get("message") or "Statement coverage diagnosis completed.")
    elif status == "warning":
        st.warning(result.get("message") or "Statement coverage diagnosis completed with guidance.")
    else:
        st.error(result.get("message") or "Statement coverage diagnosis failed.")

    st.caption(
        "이 결과는 `DB raw coverage + DB shadow coverage + live EDGAR source sample`을 합쳐서 "
        "이 심볼이 재수집 대상인지, shadow rebuild 대상인지, 아니면 구조적으로 현재 파이프라인과 잘 맞지 않는지 좁혀보는 진단용 결과입니다."
    )
    meta_cols = st.columns(3)
    meta_cols[0].metric("Requested", details.get("requested_count", 0))
    meta_cols[1].metric("Frequency", details.get("freq", "-"))
    meta_cols[2].metric("Invalid Symbols", len(details.get("invalid_symbols") or []))

    diagnosis_counts = details.get("diagnosis_counts") or {}
    if diagnosis_counts:
        st.markdown("##### Diagnosis Summary")
        summary_df = pd.DataFrame(
            [{"Diagnosis": diagnosis, "Count": count} for diagnosis, count in diagnosis_counts.items()]
        ).sort_values(["Count", "Diagnosis"], ascending=[False, True])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    rows = details.get("rows") or []
    if rows:
        st.markdown("##### Recovery Guidance")
        st.caption(
            "`source_present_raw_missing`이면 먼저 `Extended Statement Refresh`, "
            "`raw_present_shadow_missing`이면 먼저 `Statement Shadow Rebuild Only`, "
            "`foreign_or_nonstandard_form_structure`면 재수집보다 form support / exclusion 판단이 우선입니다."
        )
        diagnosis_df = pd.DataFrame(rows).rename(
            columns={
                "symbol": "Symbol",
                "raw_strict_rows": "Raw Strict Rows",
                "shadow_rows": "Shadow Rows",
                "source_fact_count": "Source Facts",
                "source_filing_count": "Source Filings",
                "dominant_forms": "Dominant Forms",
                "diagnosis": "Diagnosis",
                "recommended_action": "Recommended Action",
                "note": "Note",
                "stepwise_guidance": "Stepwise Guidance",
            }
        )
        st.dataframe(diagnosis_df, use_container_width=True, hide_index=True)

    source_rows = details.get("source_rows") or []
    if source_rows:
        with st.expander("Source Payload Details", expanded=False):
            st.caption(
                "각 심볼별 live EDGAR sample을 다시 요약해서 보여줍니다. "
                "특히 `statement_fact_count`, `form_counts`, `timing_field_inventory`를 보면 "
                "source가 비어 있는지, foreign/non-standard form 위주인지, supported form인데도 DB에 안 들어온 건지 구분하는 데 도움이 됩니다."
            )
            source_df = pd.DataFrame(
                [
                    {
                        "Symbol": row.get("symbol"),
                        "Source Facts": row.get("statement_fact_count"),
                        "Source Filings": row.get("filing_count"),
                        "Form Counts": row.get("form_counts"),
                        "Fiscal Period Counts": row.get("fiscal_period_counts"),
                        "Timing Field Inventory": row.get("timing_field_inventory"),
                    }
                    for row in source_rows
                ]
            )
            st.dataframe(source_df, use_container_width=True, hide_index=True)

    refresh_payload = details.get("extended_refresh_payload")
    if refresh_payload:
        st.markdown("##### Suggested Extended Statement Refresh Payload")
        st.caption(
            "Only symbols classified as `source_present_raw_missing` are included here. "
            "즉 source에는 usable facts가 보이는데 DB strict raw rows가 없는 경우만 다시 수집 대상으로 제안합니다."
        )
        st.code(refresh_payload.get("payload_block") or "", language="text")

    rebuild_payload = details.get("shadow_rebuild_payload")
    if rebuild_payload:
        st.markdown("##### Suggested Statement Shadow Rebuild Payload")
        st.caption(
            "Only symbols classified as `raw_present_shadow_missing` are included here. "
            "즉 raw strict rows는 이미 있고 shadow만 비어 있는 경우만 rebuild 대상으로 제안합니다."
        )
        st.code(rebuild_payload.get("payload_block") or "", language="text")


def _render_statement_universe_coverage_qa_result(result: dict[str, Any]) -> None:
    st.markdown("#### Statement Universe Coverage QA Result")
    details = result.get("details") or {}
    coverage = details.get("coverage") or {}
    status = result.get("status")
    if status == "ok":
        st.success(result.get("message") or "Statement universe coverage QA completed.")
    elif status == "warning":
        st.warning(result.get("message") or "Statement universe coverage QA found coverage gaps.")
    else:
        st.error(result.get("message") or "Statement universe coverage QA failed.")

    st.caption(
        "EDGAR annual coverage by universe. This is DB-backed source QA: it reads stored raw/shadow/profile rows and does not "
        "read yfinance statement data."
    )
    _render_ingestion_meta_grid(
        [
            ("Universe", str(details.get("universe_label") or details.get("universe_code") or "-")),
            ("Coverage Basis", str(details.get("coverage_basis") or "-")),
            ("Frequency", str(details.get("freq") or "-")),
            ("As Of", str(details.get("as_of_date") or "-")),
        ]
    )
    _render_ingestion_stat_grid(
        [
            ("Universe", _format_count(details.get("universe_count")), None),
            ("Shadow Ready", _format_count(coverage.get("shadow_available_count")), None),
            ("Raw Present", _format_count(coverage.get("raw_available_count")), None),
            ("Not Ready", _format_count(coverage.get("missing_or_not_ready_count")), None),
            ("Coverage %", f"{float(coverage.get('shadow_coverage_pct') or 0):.2f}%", None),
        ]
    )

    reason_counts = details.get("reason_counts") or {}
    if reason_counts:
        st.markdown("##### Missing Reason Groups")
        reason_df = pd.DataFrame(
            [{"Reason Group": reason, "Count": count} for reason, count in reason_counts.items()]
        ).sort_values(["Count", "Reason Group"], ascending=[False, True])
        st.dataframe(reason_df, use_container_width=True, hide_index=True)

    rows = details.get("rows") or []
    if rows:
        st.markdown("##### Sample Source QA Rows")
        qa_df = pd.DataFrame(rows).rename(
            columns={
                "symbol": "Symbol",
                "name": "Name",
                "country": "Country",
                "profile_status": "Profile Status",
                "raw_strict_rows": "Raw Strict Rows",
                "raw_max_period_end": "Raw Max Period End",
                "shadow_rows": "Shadow Rows",
                "shadow_max_period_end": "Shadow Max Period End",
                "reason_group": "Reason Group",
                "recommended_action": "Recommended Action",
                "note": "Note",
            }
        )
        st.dataframe(qa_df.head(80), use_container_width=True, hide_index=True)

    next_actions = [str(item) for item in details.get("next_actions") or [] if str(item).strip()]
    if next_actions:
        st.markdown("##### Next Actions")
        for item in next_actions:
            st.markdown(f"- {item}")


def _render_price_stale_diagnosis_card() -> None:
    with st.container(border=True):
        st.markdown("### Price Stale Diagnosis")
        st.write("DB 수집 누락, provider gap, 상폐 / 심볼 변경 가능성을 분리하는 읽기 전용 진단입니다.")
        st.caption(
            "Use this after `Price Freshness Preflight` goes yellow and you want to know whether a lagging symbol is stale because DB is behind, "
            "because the provider is not returning fresh rows, or because the symbol may be delisted / changed."
        )
        with st.expander("이 카드 읽는 법", expanded=False):
            st.markdown(
                """
                - 이 카드는 **새 데이터를 저장하지 않습니다.**
                - 먼저 DB의 latest daily date를 봅니다.
                - 그다음 같은 심볼을 provider에 다시 `5d`, `1mo`, `3mo`로 조회합니다.
                - 마지막으로 asset profile 상태를 같이 보고, 원인을 아래처럼 좁힙니다.
                  - `local_ingestion_gap`: provider는 최신 데이터를 주는데 DB만 뒤처짐
                  - `provider_source_gap`: provider도 최신 rows를 안 줌
                  - `likely_delisted_or_symbol_changed`: 상폐/심볼변경 가능성이 높음
                  - `rate_limited_during_probe`: provider probe 자체가 막혀서 확정 보류
                - 추천 사용 범위는 **소수의 의심 심볼 수동 진단**입니다. 한 번에 최대 20개까지만 권장합니다.
                """
            )

        diag_symbol_result = _render_symbol_source_inputs(
            "price_stale_diag",
            "Diagnosis Symbols",
            default_source_mode="Manual",
        )
        diag_symbols_input = diag_symbol_result["symbols"]
        diag_symbol_check = check_symbol_input(diag_symbols_input)
        _render_check_result(diag_symbol_check)

        col1, col2 = st.columns(2)
        diag_end_input = col1.date_input(
            "Diagnosis End Date",
            value=date.today(),
            key="price_stale_diag_end_date",
            help="weekend/holiday를 넣어도 DB latest market date 기준의 effective trading end로 비교합니다.",
        )
        col2.caption(
            "Daily-only diagnosis: this card is aligned to the same daily latest-date logic used by strict backtest preflight."
        )
        st.caption("Provider probe windows are fixed to `5d`, `1mo`, `3mo` for a quick freshness check without writing DB rows.")

        if st.button(
            "가격 stale 원인 진단 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(diag_symbol_check),
        ):
            _schedule_job(
                {
                    "action": "diagnose_price_stale",
                    "job_name": "diagnose_price_stale",
                    "spinner_text": "Running price stale diagnosis...",
                    "params": {
                        "symbols": diag_symbols_input,
                        "end": diag_end_input.isoformat(),
                        "timeframe": "1d",
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="price_stale_diagnosis",
                        execution_mode="diagnostic",
                        symbol_source=diag_symbol_result.get("source_mode"),
                        symbol_count=len(diag_symbols_input),
                        execution_context="Read-only price stale diagnosis for selected symbols.",
                        input_params={
                            "end": diag_end_input.isoformat(),
                            "timeframe": "1d",
                        },
                    ),
                }
            )

        result = st.session_state.get("price_stale_diagnosis_result")
        if result:
            _render_price_stale_diagnosis_result(result)


def _render_statement_universe_coverage_qa_card() -> None:
    with st.container(border=True):
        st.markdown("### Statement Universe Coverage QA")
        st.write("Top1000 / Top2000 / Nasdaq workflow의 EDGAR annual statement coverage를 universe 단위로 점검합니다.")
        st.caption(
            "EDGAR annual coverage by universe is DB-backed source QA. It groups missing reasons such as raw-present/shadow-missing, "
            "non-US issuer / foreign-form expectation, stale annual period, and CIK mapping or EDGAR unavailability candidates."
        )
        st.caption("이 카드는 새 데이터를 저장하지 않고, paid provider나 yfinance statement data를 primary source로 읽지 않습니다.")

        qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)
        universe_code = qa_col1.selectbox(
            "Statement Universe",
            ["SP500", "TOP1000", "TOP2000", "NASDAQ"],
            index=1,
            key="statement_universe_coverage_code",
        )
        universe_limit = int(
            qa_col2.number_input(
                "Universe Limit",
                min_value=0,
                max_value=5000,
                value=1000,
                step=100,
                key="statement_universe_coverage_limit",
                help="`0`이면 선택 universe의 기본 범위를 사용합니다.",
            )
        )
        qa_freq = qa_col3.selectbox(
            "QA Frequency",
            ["annual", "quarterly"],
            index=0,
            key="statement_universe_coverage_freq",
        )
        qa_as_of = qa_col4.date_input(
            "QA As Of",
            value=date.today(),
            key="statement_universe_coverage_as_of",
        )

        if st.button(
            "Statement Universe Coverage QA 실행",
            use_container_width=True,
            disabled=_has_running_job(),
        ):
            _schedule_job(
                {
                    "action": "diagnose_statement_universe_coverage",
                    "job_name": "diagnose_statement_universe_coverage",
                    "spinner_text": "Running DB-backed statement universe coverage QA...",
                    "params": {
                        "universe_code": universe_code,
                        "universe_limit": universe_limit or None,
                        "freq": qa_freq,
                        "as_of_date": qa_as_of.isoformat(),
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="statement_universe_coverage_qa",
                        execution_mode="diagnostic",
                        symbol_source=universe_code,
                        symbol_count=universe_limit or None,
                        execution_context="Read-only DB-backed statement universe coverage QA.",
                        input_params={
                            "universe_code": universe_code,
                            "universe_limit": universe_limit or None,
                            "freq": qa_freq,
                            "as_of_date": qa_as_of.isoformat(),
                        },
                    ),
                }
            )

        result = st.session_state.get("statement_universe_coverage_qa_result")
        if result:
            _render_statement_universe_coverage_qa_result(result)


def _render_statement_coverage_diagnosis_card() -> None:
    with st.container(border=True):
        st.markdown("### Statement Coverage Diagnosis")
        st.write("strict statement coverage가 왜 부족한지와 다음 조치를 분리하는 읽기 전용 진단입니다.")
        st.caption(
            "Use this when `Statement Shadow Coverage Preview` or `Coverage Gap Drilldown` tells you a symbol is missing. "
            "This card helps separate normal re-collection cases from shadow-only rebuild cases and source-structure issues."
        )
        with st.expander("이 카드 읽는 법", expanded=False):
            st.markdown(
                """
                - 이 카드는 **새 데이터를 저장하지 않습니다.**
                - 먼저 DB의 strict raw statement coverage와 statement shadow coverage를 봅니다.
                - 그다음 같은 심볼을 live EDGAR sample로 다시 읽습니다.
                - 마지막으로 아래처럼 원인을 좁힙니다.
                  - `source_present_raw_missing`: 먼저 `Extended Statement Refresh`
                  - `raw_present_shadow_missing`: 먼저 `Statement Shadow Rebuild Only`
                  - `foreign_or_nonstandard_form_structure`: 재수집보다 foreign/non-standard form support 여부 판단 우선
                  - `source_empty_or_symbol_issue`: source 자체가 비어 있어서 symbol/source validity 점검 우선
                - 추천 사용 범위는 **소수의 coverage-missing symbol 수동 진단**입니다.
                """
            )

        diag_symbol_result = _render_symbol_source_inputs(
            "statement_coverage_diag",
            "Coverage Diagnosis Symbols",
            default_source_mode="Manual",
        )
        diag_symbols_input = diag_symbol_result["symbols"]
        diag_symbol_check = check_symbol_input(diag_symbols_input)
        _render_check_result(diag_symbol_check)

        col1, col2 = st.columns(2)
        diag_freq_input = col1.selectbox(
            "Coverage Diagnosis Frequency",
            ["annual", "quarterly"],
            index=1,
            key="statement_coverage_diag_freq",
        )
        diag_sample_size = int(
            col2.number_input(
                "Source Sample Size",
                min_value=1,
                max_value=5,
                value=2,
                step=1,
                key="statement_coverage_diag_sample_size",
                help="진단용 source sample row 수입니다. sample이 많을수록 느려질 수 있습니다.",
            )
        )

        if st.button(
            "재무제표 coverage 원인 진단 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(diag_symbol_check),
        ):
            _schedule_job(
                {
                    "action": "diagnose_statement_coverage",
                    "job_name": "diagnose_statement_coverage",
                    "spinner_text": "Running statement coverage diagnosis...",
                    "params": {
                        "symbols": diag_symbols_input,
                        "freq": diag_freq_input,
                        "sample_size": diag_sample_size,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="statement_coverage_diagnosis",
                        execution_mode="diagnostic",
                        symbol_source=diag_symbol_result.get("source_mode"),
                        symbol_count=len(diag_symbols_input),
                        execution_context="Read-only statement coverage diagnosis for selected symbols.",
                        input_params={
                            "freq": diag_freq_input,
                            "sample_size": diag_sample_size,
                        },
                    ),
                }
            )

        result = st.session_state.get("statement_coverage_diagnosis_result")
        if result:
            _render_statement_coverage_diagnosis_result(result)


def _render_statement_pit_inspection_card() -> None:
    with st.container(border=True):
        st.markdown("### Statement PIT Inspection")
        st.write("Inspect statement coverage, timing rows, and source payload shape without leaving the UI.")
        st.caption(
            "Phase 7 helper card: read-only inspection for quarterly/annual PIT validation. This reduces the need for notebook snippets during manual checks."
        )
        st.caption(
            "This card does not collect or write new statement rows. "
            "`Coverage Summary` and `Timing Audit` read already stored MySQL statement ledgers, and "
            "`Source Payload Inspection` fetches one live EDGAR sample payload only for field inspection."
        )
        with st.expander("이 카드 읽는 법", expanded=False):
            st.markdown(
                """
                - `Coverage Summary`: DB에 저장된 statement ledger가 얼마나 오래/넓게 쌓였는지 확인합니다.
                - `Timing Audit`: 각 row가 어떤 `period_end` 기준이며, 실제로 언제 공시/접수/사용 가능해졌는지 확인합니다.
                - `Source Payload Inspection`: EDGAR 원본 payload 예시를 보고, source가 어떤 form/fiscal-period/timing 필드를 주는지 확인합니다.
                - `Inspection Frequency = quarterly`이면 coverage와 timing audit는 quarterly ledger 기준으로 읽습니다.
                - `Timing Audit Symbols`는 timing audit 표에 포함할 심볼 개수, `Rows / Symbol`은 심볼당 최근 몇 개 row를 보여줄지 뜻합니다.
                - `Source Sample Size`는 source 예시 row 수, `Source Inspection Symbol`은 live payload를 읽을 대표 심볼 1개입니다.
                """
            )

        inspect_symbol_result = _render_symbol_source_inputs(
            "statement_pit",
            "Inspection Symbols",
            default_source_mode="Manual",
        )
        inspect_symbols_input = inspect_symbol_result["symbols"]
        inspect_symbol_check = check_symbol_input(inspect_symbols_input)
        _render_check_result(inspect_symbol_check)

        col1, col2, col3, col4 = st.columns(4)
        inspect_freq = col1.selectbox(
            "Inspection Frequency",
            ["annual", "quarterly"],
            index=1,
            key="statement_pit_freq",
        )
        audit_symbol_limit = int(
            col2.number_input(
                "Timing Audit Symbols",
                min_value=1,
                max_value=20,
                value=3,
                step=1,
                key="statement_pit_audit_symbol_limit",
                help="Timing audit는 선택한 심볼 중 앞쪽 일부만 대상으로 읽습니다.",
            )
        )
        audit_limit_per_symbol = int(
            col3.number_input(
                "Rows / Symbol",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                key="statement_pit_audit_limit_per_symbol",
                help="Timing Audit 표에서 심볼당 몇 개의 최근 row를 보여줄지 정합니다. 진단용 표시 수만 바뀌고 DB 데이터는 바뀌지 않습니다.",
            )
        )
        source_sample_size = int(
            col4.number_input(
                "Source Sample Size",
                min_value=1,
                max_value=10,
                value=2,
                step=1,
                key="statement_pit_source_sample_size",
                help="Source Payload Inspection에서 EDGAR 원본 payload 예시를 몇 건까지 보여줄지 정합니다. inspection용 샘플 표시 수만 바뀝니다.",
            )
        )

        source_symbol_options = inspect_symbols_input[:20]
        source_symbol = st.selectbox(
            "Source Inspection Symbol",
            options=source_symbol_options if source_symbol_options else [""],
            index=0,
            key="statement_pit_source_symbol",
            help="EDGAR source payload inspection은 한 번에 한 심볼만 대상으로 합니다. 선택한 심볼 1개의 live payload를 읽어서 필드 구조를 보여줍니다.",
        )

        if st.button(
            "재무제표 PIT inspection 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(inspect_symbol_check),
        ):
            _schedule_job(
                {
                    "action": "inspect_statement_pit",
                    "job_name": "inspect_statement_pit",
                    "spinner_text": "Running statement PIT inspection...",
                    "params": {
                        "symbols": inspect_symbols_input,
                        "inspect_freq": inspect_freq,
                        "audit_symbol_limit": audit_symbol_limit,
                        "audit_limit_per_symbol": audit_limit_per_symbol,
                        "source_symbol": source_symbol,
                        "source_sample_size": source_sample_size,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="statement_pit_inspection",
                        execution_mode="diagnostic",
                        symbol_source=inspect_symbol_result.get("source_mode"),
                        symbol_count=len(inspect_symbols_input),
                        execution_context="Read-only statement PIT inspection for selected symbols.",
                        input_params={
                            "inspect_freq": inspect_freq,
                            "audit_symbol_limit": audit_symbol_limit,
                            "audit_limit_per_symbol": audit_limit_per_symbol,
                            "source_symbol": source_symbol,
                            "source_sample_size": source_sample_size,
                        },
                    ),
                }
            )

        result = st.session_state.get("statement_pit_inspection_result")
        if result:
            _render_statement_pit_inspection_result(result)


def _resolve_symbols(preset_name: str, manual_value: str) -> str:
    preset_value = SYMBOL_PRESETS.get(preset_name, "")
    return preset_value if preset_name != "Custom" else manual_value


def _parse_csv_items(value: str) -> list[str]:
    return [item.strip().upper() for item in str(value or "").replace("\n", ",").split(",") if item.strip()]


def _render_symbol_source_inputs(
    prefix: str,
    title: str = "Symbols",
    *,
    default_source_mode: str = "Manual",
) -> dict[str, Any]:
    default_source_index = SYMBOL_SOURCE_OPTIONS.index(default_source_mode) if default_source_mode in SYMBOL_SOURCE_OPTIONS else 0
    display_title = _format_symbol_input_title(title)
    st.markdown(f"**{display_title} 소스**")
    source_mode = st.selectbox(
        f"{display_title} 소스",
        SYMBOL_SOURCE_OPTIONS,
        index=default_source_index,
        key=f"{prefix}_source_mode",
        format_func=_format_symbol_source_label,
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div class="ingestion-select-caption">현재 선택: {escape(_format_symbol_source_label(source_mode))}</div>',
        unsafe_allow_html=True,
    )

    manual_symbols: list[str] = []
    if source_mode == "Manual":
        text_key = f"{prefix}_symbols_input"
        preset_applied_key = f"{prefix}_preset_applied"
        st.markdown(f"**{display_title} 프리셋**")
        preset_name = st.selectbox(
            f"{display_title} 프리셋",
            list(SYMBOL_PRESETS.keys()),
            index=0,
            key=f"{prefix}_preset",
            format_func=_format_symbol_preset_label,
            label_visibility="collapsed",
        )
        st.markdown(
            f'<div class="ingestion-select-caption">현재 프리셋: {escape(_format_symbol_preset_label(preset_name))}</div>',
            unsafe_allow_html=True,
        )
        if preset_name != "Custom":
            preset_value = SYMBOL_PRESETS.get(preset_name, "")
            if st.session_state.get(preset_applied_key) != preset_name:
                st.session_state[text_key] = preset_value
                st.session_state[preset_applied_key] = preset_name
            manual_text = st.text_area(
                display_title,
                key=text_key,
                disabled=True,
            )
            manual_symbols = [s.strip() for s in preset_value.split(",") if s.strip()]
        else:
            if text_key not in st.session_state:
                st.session_state[text_key] = ""
            st.session_state[preset_applied_key] = preset_name
            manual_text = st.text_area(
                display_title,
                key=text_key,
            )
            manual_symbols = [s.strip() for s in manual_text.split(",") if s.strip()]

    source_result = resolve_symbol_source(source_mode, manual_symbols)
    if source_result["status"] == "ok":
        st.info(f'{_format_symbol_source_label(source_mode)} 준비 완료. 대상: {source_result["count"]:,}개')
        preview = ", ".join(source_result["symbols"][:10])
        if preview:
            st.caption(f"미리보기: {preview}")
    else:
        st.error(source_result["message"])

    return source_result


def _render_large_run_guard(
    *,
    prefix: str,
    job_name: str,
    symbols: list[str],
    warn_threshold: int = 200,
) -> bool:
    count = len(symbols)
    estimate = estimate_duration_from_history(job_name, count)

    if count == 0:
        return False

    if count >= warn_threshold:
        st.warning(f"대량 실행입니다: {count:,} symbols.")
        if estimate.get("available"):
            st.caption(estimate["message"])
        else:
            st.caption("아직 예상 소요 시간을 계산할 실행 기록이 없습니다. 대량 실행은 수 분 이상 걸릴 수 있습니다.")

    return True


def _normalize_ohlcv_window(period: str, start: str | None, end: str | None) -> tuple[str | None, str | None, str | None]:
    clean_start = start or None
    clean_end = end or None

    if clean_start or clean_end:
        return None, clean_start, clean_end

    if period == "7d":
        resolved_end = date.today()
        resolved_start = resolved_end - timedelta(days=7)
        return None, resolved_start.isoformat(), resolved_end.isoformat()

    return period, clean_start, clean_end


def _is_short_daily_refresh_window(
    *,
    period: str | None,
    start: str | None,
    end: str | None,
    interval: str,
) -> bool:
    if interval != "1d":
        return False

    normalized_period = str(period or "").strip().lower()
    if normalized_period == "1d":
        return True

    if not start and not end:
        return False

    try:
        resolved_start = pd.to_datetime(start).date() if start else None
        resolved_end = pd.to_datetime(end).date() if end else date.today()
    except Exception:
        return False

    if resolved_start is None:
        return False

    return (resolved_end - resolved_start).days <= 10


def _resolve_daily_market_execution_profile(
    source_mode: str,
    *,
    period: str | None,
    start: str | None,
    end: str | None,
    interval: str,
) -> tuple[str, str]:
    raw_source_modes = {"NYSE Stocks", "NYSE ETFs", "NYSE Stocks + ETFs"}
    if source_mode in raw_source_modes:
        return (
            "raw_heavy",
            "Execution profile: `raw_heavy` | raw universe 대량 sweep용입니다. batch를 작게 나누고 cooldown을 길게 둡니다.",
        )
    managed_source_modes = {
        "Profile Filtered Stocks",
        "Profile Filtered ETFs",
        "Profile Filtered Stocks + ETFs",
    }
    if (
        source_mode in managed_source_modes
        and _is_short_daily_refresh_window(period=period, start=start, end=end, interval=interval)
    ):
        return (
            "managed_refresh_short",
            "Execution profile: `managed_refresh_short` | 짧은 daily refresh용입니다. batch를 키우되 rate-limit fallback은 유지합니다.",
        )
    if source_mode == "Profile Filtered Stocks + ETFs":
        return (
            "managed_fast",
            "Execution profile: `managed_fast` | 관리된 universe를 빠르게 갱신합니다. raw sweep보다 cooldown이 가볍습니다.",
        )
    return (
        "managed_safe",
        "Execution profile: `managed_safe` | 좁은 범위나 수동 입력에 맞춘 기본 안전 모드입니다.",
    )


def _render_ingestion_operational_section() -> Any:
    current_progress_callback = None
    st.info(
        "일상 운영 / 검증 데이터: 백테스트와 Practical Validation, Overview가 DB에서 읽을 데이터를 채웁니다. "
        "수집 결과가 부분 성공이면 downstream 화면에서도 coverage gap으로 남을 수 있습니다."
    )

    with st.expander("일별 가격 업데이트", expanded=True):
        _render_job_brief("daily_market_update")
        st.caption("권장 주기: 매 거래일 장 마감 후 또는 다음 backtest/data sync 전에 실행합니다.")
        st.caption(
            "권장 source: 평소 운영은 `Profile Filtered Stocks + ETFs`를 사용합니다. "
            "raw `NYSE Stocks + ETFs`는 넓은 universe를 다시 훑어야 할 때만 사용하세요."
        )
        st.caption("기본값: `Profile Filtered Stocks + ETFs`, `1d`, `1d`.")
        st.caption("저장 테이블: `finance_price.nyse_price_history`")
        daily_symbol_result = _render_symbol_source_inputs(
            "daily_market",
            "Daily Market Symbols",
            default_source_mode="Profile Filtered Stocks + ETFs",
        )
        daily_symbols_input = daily_symbol_result["symbols"]
        daily_source_mode = daily_symbol_result.get("source_mode") or "Manual"
        daily_raw_source_modes = {"NYSE Stocks", "NYSE ETFs", "NYSE Stocks + ETFs"}
        daily_filter_non_plain = st.checkbox(
            "Exclude special share-class / non-plain symbols",
            value=True,
            key="daily_filter_non_plain_symbols",
            help=(
                "When raw NYSE universes are selected, exclude symbols such as preferred/unit/special share classes. "
                "This usually reduces noisy provider failures and wasted requests."
            ),
        )
        daily_filtered_symbols: list[str] = list(daily_symbols_input)
        daily_excluded_symbols: list[str] = []
        if daily_filter_non_plain and daily_source_mode in daily_raw_source_modes:
            daily_filtered_symbols, daily_excluded_symbols = filter_non_plain_symbols(daily_symbols_input)
            if daily_excluded_symbols:
                st.info(
                    "provider 안정성을 위해 특수 share-class / non-plain symbol을 제외했습니다: "
                    f"`{len(daily_excluded_symbols)}`개 제외, `{len(daily_filtered_symbols)}`개 실행 대상."
                )
                st.caption(f"제외 sample: {', '.join(daily_excluded_symbols[:10])}")
        daily_symbols_input = daily_filtered_symbols
        daily_col1, daily_col2 = st.columns(2)
        daily_period_input = daily_col1.selectbox("Daily Period", PERIOD_PRESETS, index=0, key="daily_period_input")
        daily_interval_input = daily_col2.selectbox("Daily Interval", ["1d", "1wk", "1mo"], index=0, key="daily_interval_input")
        daily_col3, daily_col4 = st.columns(2)
        daily_start_input = daily_col3.text_input("Daily Start", value="", key="daily_start_input")
        daily_end_input = daily_col4.text_input("Daily End", value="", key="daily_end_input")
        daily_resolved_period, daily_resolved_start, daily_resolved_end = _normalize_ohlcv_window(
            daily_period_input,
            daily_start_input,
            daily_end_input,
        )
        daily_execution_profile, daily_profile_caption = _resolve_daily_market_execution_profile(
            daily_source_mode,
            period=daily_resolved_period,
            start=daily_resolved_start,
            end=daily_resolved_end,
            interval=daily_interval_input,
        )
        st.caption(daily_profile_caption)
        _render_collection_contract(
            "실행 전 확인",
            [
                ("Source", _format_symbol_source_label(daily_source_mode)),
                ("대상 수", f"{len(daily_symbols_input):,} symbols"),
                (
                    "기간",
                    _format_contract_window(
                        period=daily_resolved_period,
                        start=daily_resolved_start,
                        end=daily_resolved_end,
                    ),
                ),
                ("Interval", daily_interval_input),
                ("Execution profile", daily_execution_profile),
            ],
            note=(
                "이 설정으로 가격 row를 저장합니다. 저장 row 수가 있어도 요청 기간 전체 coverage를 뜻하지는 않으므로 "
                "결과 해석과 DB coverage quick check를 함께 보세요."
            ),
        )
        _render_price_window_preflight(
            symbols=daily_symbols_input,
            start=daily_resolved_start,
            end=daily_resolved_end,
            timeframe=daily_interval_input,
        )
        daily_symbol_check = check_symbol_input(daily_symbols_input)
        _render_check_result(daily_symbol_check)
        daily_run_allowed = _render_large_run_guard(
            prefix="daily_market",
            job_name="daily_market_update",
            symbols=daily_symbols_input,
        )
        if st.button(
            "일별 가격 업데이트 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(daily_symbol_check) or not daily_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "daily_market_update",
                    "job_name": "daily_market_update",
                    "spinner_text": "Running daily market update...",
                    "params": {
                        "symbols": daily_symbols_input,
                        "start": daily_resolved_start,
                        "end": daily_resolved_end,
                        "period": daily_resolved_period,
                        "interval": daily_interval_input,
                        "execution_profile": daily_execution_profile,
                        "excluded_symbols": daily_excluded_symbols,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="daily_market_update",
                        execution_mode="operational",
                        symbol_source=daily_symbol_result.get("source_mode"),
                        symbol_count=len(daily_symbols_input),
                        execution_context=(
                            "Routine daily price-history refresh for the selected operating universe. "
                            "Managed universes use managed execution profiles; raw NYSE sweeps use the heavy profile."
                        ),
                        input_params={
                            "start": daily_resolved_start,
                            "end": daily_resolved_end,
                            "period": daily_resolved_period,
                            "interval": daily_interval_input,
                            "execution_profile": daily_execution_profile,
                            "exclude_non_plain_symbols": daily_filter_non_plain,
                        },
                    ),
                }
            )
        if _is_running_action("daily_market_update"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Daily Market Update",
            )
        _render_inline_last_completed_result("daily_market_update")

    with st.expander("선물 OHLCV 수집", expanded=False):
        _render_job_brief("collect_futures_ohlcv")
        st.caption("Overview Futures Monitor에서 사용할 선물 캔들 데이터를 수집합니다.")
        st.caption("기본값은 주요 지수 / 금리 / 원자재 / FX 선물이며, 저장 테이블은 `finance_price.futures_ohlcv`입니다.")
        futures_symbols_text = st.text_area(
            "Futures Symbols",
            value=", ".join(DEFAULT_CORE_FUTURES_SYMBOLS),
            key="futures_ohlcv_symbols_input",
            help="Yahoo/yfinance futures ticker를 쉼표 또는 줄바꿈으로 입력합니다.",
        )
        futures_symbols_input = [
            item.strip().upper()
            for item in futures_symbols_text.replace("\n", ",").split(",")
            if item.strip()
        ]
        futures_col1, futures_col2, futures_col3 = st.columns(3)
        futures_period_input = futures_col1.selectbox(
            "Futures Period",
            ["1d", "5d", "7d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=0,
            key="futures_ohlcv_period_input",
        )
        futures_interval_input = futures_col2.selectbox(
            "Futures Interval",
            ["1m", "2m", "5m", "15m", "1h", "1d"],
            index=0,
            key="futures_ohlcv_interval_input",
        )
        futures_max_symbols = int(
            futures_col3.number_input(
                "Max Symbols",
                min_value=1,
                max_value=24,
                value=min(24, max(1, len(futures_symbols_input))),
                step=1,
                key="futures_ohlcv_max_symbols",
            )
        )
        _render_collection_contract(
            "실행 전 확인",
            [
                ("Source", "yfinance pilot"),
                (
                    "대상 수",
                    f"{min(len(futures_symbols_input), futures_max_symbols):,} / {len(futures_symbols_input):,} symbols",
                ),
                ("기간", futures_period_input),
                ("Interval", futures_interval_input),
                ("Cadence", "manual"),
            ],
            note=(
                "이 수집은 선물 시장 컨텍스트용입니다. 무료 provider 지연 / 누락 가능성이 있어 "
                "Overview에서 stale / failed 상태를 함께 확인해야 합니다."
            ),
        )
        futures_symbol_check = check_symbol_input(futures_symbols_input)
        _render_check_result(futures_symbol_check)
        if st.button(
            "선물 OHLCV 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(futures_symbol_check),
        ):
            _schedule_job(
                {
                    "action": "collect_futures_ohlcv",
                    "job_name": "collect_futures_ohlcv",
                    "spinner_text": "Running futures OHLCV collection...",
                    "params": {
                        "symbols": futures_symbols_input,
                        "period": futures_period_input,
                        "interval": futures_interval_input,
                        "cadence_mode": "manual",
                        "max_symbols": futures_max_symbols,
                        "batch_size": 6,
                        "sleep_sec": 0.1,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="overview_futures_market_monitor",
                        execution_mode="manual",
                        symbol_source="manual_futures_watchlist",
                        symbol_count=min(len(futures_symbols_input), futures_max_symbols),
                        execution_context="Manual futures OHLCV refresh for Overview Futures Monitor.",
                        input_params={
                            "period": futures_period_input,
                            "interval": futures_interval_input,
                            "max_symbols": futures_max_symbols,
                        },
                    ),
                }
            )
        _render_inline_last_completed_result("collect_futures_ohlcv")

    with st.expander("시장 심리 수집", expanded=False):
        _render_job_brief("collect_market_sentiment")
        st.caption("저장 테이블: `finance_meta.macro_series_observation`")
        sentiment_cols = st.columns(2)
        include_cnn = sentiment_cols[0].checkbox(
            "CNN Fear & Greed",
            value=True,
            key="market_sentiment_include_cnn",
        )
        include_aaii = sentiment_cols[1].checkbox(
            "AAII Sentiment Survey",
            value=True,
            key="market_sentiment_include_aaii",
        )
        _render_collection_contract(
            "실행 전 확인",
            [
                ("CNN", "enabled" if include_cnn else "disabled"),
                ("AAII", "enabled" if include_aaii else "disabled"),
                ("저장 위치", "finance_meta.macro_series_observation"),
            ],
            note=(
                "이 수집은 Overview 시장 심리 context용입니다. source 차단이나 partial result는 "
                "Overview Sentiment / Data Health에 그대로 남깁니다."
            ),
        )
        if st.button(
            "시장 심리 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or not (include_cnn or include_aaii),
        ):
            _schedule_job(
                {
                    "action": "collect_market_sentiment",
                    "job_name": "collect_market_sentiment",
                    "spinner_text": "Running market sentiment collection...",
                    "params": {
                        "include_cnn": bool(include_cnn),
                        "include_aaii": bool(include_aaii),
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="overview_market_sentiment",
                        execution_mode="manual",
                        symbol_source="CNN Fear & Greed / AAII Sentiment Survey",
                        symbol_count=int(bool(include_cnn)) + int(bool(include_aaii)),
                        execution_context="Manual market sentiment refresh for Overview Sentiment.",
                        input_params={
                            "include_cnn": bool(include_cnn),
                            "include_aaii": bool(include_aaii),
                        },
                    ),
                }
            )
        if _is_running_action("collect_market_sentiment"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Market Sentiment",
            )
        _render_inline_last_completed_result("collect_market_sentiment")

    with st.expander("EDGAR annual 재무제표 갱신", expanded=False):
        _render_job_brief("extended_statement_refresh")
        st.caption("권장 주기: 월 1회 또는 긴 기간 factor research / backtest 준비 전에 실행합니다.")
        st.caption("권장 source: `Profile Filtered Stocks`나 statement coverage preset부터 시작하세요.")
        st.caption(
            "새 재무제표 coverage와 strict annual factor 준비는 이 EDGAR annual refresh에서 시작합니다. "
            "수동 `Financial Statement Ingestion` card는 복구 / 진단용으로 남아 있습니다."
        )
        st.caption(
            "symbol preset dropdown에는 관리용 coverage preset도 있습니다: "
            "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, and `US Statement Coverage 1000`."
        )
        st.caption("기본값: `Profile Filtered Stocks`, `annual`, `0 periods (all available)`.")
        st.caption("SEC fair access를 위해 `SEC_USER_AGENT`와 pacing을 확인한 뒤 대량 실행하세요.")
        st.caption(
            "저장 테이블: "
            "`finance_fundamental.nyse_financial_statement_filings`, "
            "`finance_fundamental.nyse_financial_statement_labels`, "
            "`finance_fundamental.nyse_financial_statement_values`, "
            "`finance_fundamental.nyse_fundamentals_statement`, "
            "`finance_fundamental.nyse_factors_statement`"
        )
        ext_symbol_result = _render_symbol_source_inputs(
            "extended_statement",
            "EDGAR Statement Symbols",
            default_source_mode="Profile Filtered Stocks",
        )
        ext_symbols_input = ext_symbol_result["symbols"]
        ext_col1, ext_col2 = st.columns(2)
        ext_period_input = ext_col1.selectbox("EDGAR Statement Period Type", ["annual", "quarterly"], index=0, key="ext_period_input")
        ext_periods_input = ext_col2.number_input(
            "EDGAR Statement Periods",
            min_value=0,
            max_value=80,
            value=0,
            step=1,
            key="ext_periods_input",
            help="`0` means collect all available statement periods from the source. Use this for PIT recovery and quarterly history hardening.",
        )
        st.caption("`freq`는 선택한 `Period Type`에 자동으로 맞춰 실행됩니다.")
        st.caption("Tip: `0 = all available periods`. 짧은 rolling refresh를 의도할 때만 양수를 입력하세요.")
        ext_symbol_check = check_symbol_input(ext_symbols_input)
        _render_check_result(ext_symbol_check)
        ext_run_allowed = _render_large_run_guard(
            prefix="extended_statement",
            job_name="extended_statement_refresh",
            symbols=ext_symbols_input,
        )
        if st.button(
            "EDGAR annual 재무제표 갱신 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(ext_symbol_check) or not ext_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "extended_statement_refresh",
                    "job_name": "extended_statement_refresh",
                    "spinner_text": "Running EDGAR annual statement refresh...",
                    "params": {
                        "symbols": ext_symbols_input,
                        "freq": ext_period_input,
                        "periods": int(ext_periods_input),
                        "period": ext_period_input,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="extended_statement_refresh",
                        execution_mode="operational",
                        symbol_source=ext_symbol_result.get("source_mode"),
                        symbol_count=len(ext_symbols_input),
                        execution_context="Primary EDGAR annual financial statement refresh and statement shadow rebuild.",
                        input_params={
                            "freq": ext_period_input,
                            "periods": int(ext_periods_input),
                            "period": ext_period_input,
                        },
                    ),
                }
            )
        if _is_running_action("extended_statement_refresh"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="EDGAR Statement Refresh",
            )
        _render_inline_last_completed_result("extended_statement_refresh")

    with st.expander("종목 메타데이터 업데이트", expanded=False):
        _render_job_brief("metadata_refresh")
        st.caption("권장 주기: 주 1회 또는 tracked universe / profile filter가 바뀐 뒤 실행합니다.")
        st.caption("권장 scope: 한쪽만 갱신할 의도가 아니라면 `stock`과 `etf`를 함께 선택하세요.")
        st.caption("저장 테이블: `finance_meta.nyse_asset_profile`")
        metadata_kind_options = st.multiselect(
            "Metadata Refresh Kinds",
            options=["stock", "etf"],
            default=["stock", "etf"],
            key="metadata_kind_options",
        )
        metadata_kinds = tuple(metadata_kind_options) if metadata_kind_options else ()
        metadata_check = check_asset_profile_prerequisites(metadata_kinds)
        _render_check_result(metadata_check)
        if st.button(
            "종목 메타데이터 업데이트 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(metadata_check),
        ):
            _schedule_job(
                {
                    "action": "metadata_refresh",
                    "job_name": "metadata_refresh",
                    "spinner_text": "Running metadata refresh...",
                    "params": {
                        "kinds": tuple(metadata_kind_options) if metadata_kind_options else ("stock", "etf"),
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="metadata_refresh",
                        execution_mode="operational",
                        symbol_source=None,
                        symbol_count=None,
                        execution_context="Routine metadata refresh for tracked stock and ETF asset profiles.",
                        input_params={
                            "kinds": tuple(metadata_kind_options) if metadata_kind_options else ("stock", "etf"),
                        },
                    ),
                }
            )
        if _is_running_action("metadata_refresh"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Metadata Refresh",
            )
        _render_inline_last_completed_result("metadata_refresh")

    with st.expander("시장 이벤트 캘린더 수집", expanded=False):
        st.write("Overview Events 탭에서 읽을 시장 이벤트 캘린더를 공식 무료 소스에서 수집합니다.")
        st.caption(
            "현재 구현 대상: Federal Reserve FOMC, BLS/BEA macro release schedule, "
            "yfinance + Nasdaq cross-check 기반 earnings estimate."
        )
        st.caption("저장 테이블: `finance_meta.market_event_calendar`")
        fomc_tab, macro_event_tab, earnings_tab = st.tabs(["FOMC 일정", "매크로 발표", "실적 발표"])
        with fomc_tab:
            _render_job_brief("collect_fomc_calendar")
            current_year = date.today().year
            fomc_year_options = list(range(current_year - 1, current_year + 3))
            fomc_years = st.multiselect(
                "FOMC Years",
                options=fomc_year_options,
                default=[current_year, current_year + 1],
                key="overview_fomc_calendar_years",
                help="비워두면 Fed 페이지에서 파싱 가능한 모든 연도 row를 수집합니다.",
            )
            if st.button(
                "FOMC 일정 수집",
                use_container_width=True,
                disabled=_has_running_job(),
            ):
                _schedule_job(
                    {
                        "action": "collect_fomc_calendar",
                        "job_name": "collect_fomc_calendar",
                        "spinner_text": "Collecting FOMC calendar from the official Fed page...",
                        "params": {
                            "years": tuple(fomc_years) if fomc_years else None,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="overview_market_event_calendar",
                            execution_mode="operational",
                            symbol_source="Federal Reserve official FOMC calendar",
                            symbol_count=None,
                            execution_context=(
                                "Overview Events 탭에서 사용할 FOMC meeting calendar를 Fed 공식 HTML에서 파싱해 DB에 저장합니다."
                            ),
                            input_params={
                                "years": tuple(fomc_years) if fomc_years else None,
                            },
                        ),
                    }
                )
        with macro_event_tab:
            _render_job_brief("collect_macro_calendar")
            current_year = date.today().year
            macro_year_options = list(range(current_year - 1, current_year + 3))
            macro_years = st.multiselect(
                "Macro Calendar Years",
                options=macro_year_options,
                default=[current_year, current_year + 1],
                key="overview_macro_calendar_years",
                help="BLS는 선택 연도별 schedule page를, BEA는 full release schedule에서 일치하는 연도를 수집합니다.",
            )
            macro_source_cols = st.columns(2, gap="small")
            macro_include_bls = macro_source_cols[0].checkbox(
                "BLS CPI / PPI / Jobs",
                value=True,
                key="overview_macro_include_bls",
            )
            macro_include_bea = macro_source_cols[1].checkbox(
                "BEA GDP",
                value=True,
                key="overview_macro_include_bea",
            )
            st.caption(
                "BLS request는 네트워크/정책에 따라 차단될 수 있습니다. 실패하면 job result와 Data Health에서 확인합니다."
            )
            if st.button(
                "공식 매크로 발표 일정 수집",
                use_container_width=True,
                disabled=_has_running_job() or not (macro_include_bls or macro_include_bea),
            ):
                _schedule_job(
                    {
                        "action": "collect_macro_calendar",
                        "job_name": "collect_macro_calendar",
                        "spinner_text": "Collecting CPI / PPI / Jobs / GDP release dates from official schedules...",
                        "params": {
                            "years": tuple(macro_years) if macro_years else None,
                            "include_bls": macro_include_bls,
                            "include_bea": macro_include_bea,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="overview_market_event_calendar",
                            execution_mode="operational_low_frequency",
                            symbol_source="BLS and BEA official release schedules",
                            symbol_count=None,
                            execution_context=(
                                "Overview Events 탭에서 사용할 CPI, PPI, Employment Situation, GDP release calendar를 공식 HTML schedule에서 파싱해 DB에 저장합니다."
                            ),
                            input_params={
                                "years": tuple(macro_years) if macro_years else None,
                                "include_bls": macro_include_bls,
                                "include_bea": macro_include_bea,
                            },
                        ),
                    }
                )
            st.divider()
            _render_job_brief("import_bls_macro_calendar_ics")
            bls_ics_file = st.file_uploader(
                "BLS Calendar .ics File",
                type=["ics"],
                key="overview_macro_bls_ics_file",
                help="BLS 공식 release schedule 캘린더 파일을 브라우저에서 내려받은 뒤 업로드합니다.",
            )
            if st.button(
                "BLS 공식 .ics 일정 가져오기",
                use_container_width=True,
                disabled=_has_running_job() or bls_ics_file is None,
            ):
                try:
                    bls_ics_text = bls_ics_file.getvalue().decode("utf-8-sig", errors="replace")
                except Exception as exc:
                    st.error(f"BLS .ics file could not be read: {exc}")
                else:
                    _schedule_job(
                        {
                            "action": "import_bls_macro_calendar_ics",
                            "job_name": "import_bls_macro_calendar_ics",
                            "spinner_text": "Importing BLS CPI / PPI / Jobs release dates from the uploaded .ics file...",
                            "params": {
                                "ics_text": bls_ics_text,
                                "years": tuple(macro_years) if macro_years else None,
                                "source_name": bls_ics_file.name,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="overview_macro_calendar_collection",
                                execution_mode="manual_official_file_import",
                                symbol_source="BLS official release schedule ICS file",
                                symbol_count=None,
                                execution_context=(
                                    "BLS backend request 차단 시 사용자가 내려받은 공식 .ics 파일에서 CPI, PPI, Employment Situation 일정을 파싱해 DB에 저장합니다."
                                ),
                                input_params={
                                    "years": tuple(macro_years) if macro_years else None,
                                    "source_name": bls_ics_file.name,
                                },
                            ),
                        }
                    )
        with earnings_tab:
            _render_job_brief("collect_earnings_calendar")
            earnings_source_mode = st.selectbox(
                "Symbol Source",
                ["Latest S&P 500 Movers", "S&P 500 Universe Batch", "Top1000 Batch", "Top2000 Batch", "Manual Symbols"],
                index=0,
                key="overview_earnings_symbol_source",
            )
            earnings_cols = st.columns(4, gap="small")
            earnings_top_movers_limit = int(
                earnings_cols[0].number_input(
                    "Top Movers",
                    min_value=5,
                    max_value=100,
                    value=20,
                    step=5,
                    key="overview_earnings_top_movers_limit",
                    disabled=earnings_source_mode != "Latest S&P 500 Movers",
                )
            )
            earnings_lookahead_days = int(
                earnings_cols[1].number_input(
                    "Lookahead Days",
                    min_value=7,
                    max_value=365,
                    value=120 if earnings_source_mode == "Latest S&P 500 Movers" else 30,
                    step=7,
                    key="overview_earnings_lookahead_days",
                )
            )
            earnings_max_symbols = int(
                earnings_cols[2].number_input(
                    "Max Symbols",
                    min_value=5,
                    max_value=200,
                    value=50 if earnings_source_mode == "Latest S&P 500 Movers" else 100,
                    step=5,
                    key="overview_earnings_max_symbols",
                )
            )
            earnings_batch_offset = int(
                earnings_cols[3].number_input(
                    "Batch Offset",
                    min_value=0,
                    max_value=2000,
                    value=0,
                    step=50,
                    key="overview_earnings_batch_offset",
                    disabled=earnings_source_mode in {"Latest S&P 500 Movers", "Manual Symbols"},
                )
            )
            earnings_validation_cols = st.columns(2, gap="small")
            earnings_validate_with_nasdaq = earnings_validation_cols[0].checkbox(
                "Nasdaq cross-check",
                value=True,
                key="overview_earnings_validate_with_nasdaq",
                help="Cross-check yfinance earnings dates against Nasdaq's free earnings calendar endpoint when possible.",
            )
            earnings_request_sleep_sec = float(
                earnings_validation_cols[1].number_input(
                    "Ticker Cooldown Sec",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.1 if earnings_source_mode != "Latest S&P 500 Movers" else 0.0,
                    step=0.1,
                    key="overview_earnings_request_sleep_sec",
                )
            )
            manual_earnings_text = ""
            if earnings_source_mode == "Manual Symbols":
                manual_earnings_text = st.text_area(
                    "Symbols",
                    value="AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA",
                    key="overview_earnings_manual_symbols",
                )
            st.caption(
                "Latest movers mode uses the latest stored S&P 500 intraday snapshot. Universe batch modes are low-frequency sweeps; keep Max Symbols bounded and use Batch Offset to continue later."
            )
            if st.button(
                "실적 발표 예상 일정 수집",
                use_container_width=True,
                disabled=_has_running_job(),
            ):
                manual_symbols = _parse_csv_items(manual_earnings_text)
                symbol_source = {
                    "Latest S&P 500 Movers": "latest_movers",
                    "S&P 500 Universe Batch": "sp500_universe",
                    "Top1000 Batch": "top1000",
                    "Top2000 Batch": "top2000",
                    "Manual Symbols": "manual",
                }[earnings_source_mode]
                earnings_universe_code = {
                    "top1000": "TOP1000",
                    "top2000": "TOP2000",
                }.get(symbol_source, "SP500")
                earnings_universe_limit = {
                    "top1000": 1000,
                    "top2000": 2000,
                }.get(symbol_source)
                _schedule_job(
                    {
                        "action": "collect_earnings_calendar",
                        "job_name": "collect_earnings_calendar",
                        "spinner_text": "Collecting earnings dates from yfinance calendar and optional Nasdaq cross-check...",
                        "params": {
                            "symbols": manual_symbols if symbol_source == "manual" else None,
                            "symbol_source": symbol_source,
                            "universe_code": earnings_universe_code,
                            "universe_limit": earnings_universe_limit,
                            "top_movers_limit": earnings_top_movers_limit,
                            "lookahead_days": earnings_lookahead_days,
                            "max_symbols": earnings_max_symbols,
                            "batch_offset": earnings_batch_offset,
                            "validate_with_nasdaq": earnings_validate_with_nasdaq,
                            "request_sleep_sec": earnings_request_sleep_sec,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="overview_market_event_calendar",
                            execution_mode="operational_low_frequency",
                            symbol_source=symbol_source,
                            symbol_count=len(manual_symbols) if symbol_source == "manual" else earnings_max_symbols,
                            execution_context=(
                                "Overview Events 탭에서 사용할 upcoming earnings calendar estimate를 무료 provider source로 수집하고 source validation metadata를 저장합니다."
                            ),
                            input_params={
                                "symbol_source": symbol_source,
                                "universe_code": earnings_universe_code,
                                "universe_limit": earnings_universe_limit,
                                "top_movers_limit": earnings_top_movers_limit,
                                "lookahead_days": earnings_lookahead_days,
                                "max_symbols": earnings_max_symbols,
                                "batch_offset": earnings_batch_offset,
                                "validate_with_nasdaq": earnings_validate_with_nasdaq,
                                "request_sleep_sec": earnings_request_sleep_sec,
                            },
                        ),
                    }
                )
        _render_inline_last_completed_result("collect_fomc_calendar", "collect_macro_calendar", "collect_earnings_calendar")

    with st.expander("Practical Validation 검증 데이터 보강", expanded=False):
        st.write("Practical Validation에서 포트폴리오를 검토할 때 사용할 provider snapshot 데이터를 수집합니다.")
        st.caption(
            "ETF의 운용 가능성, ETF 내부 구성, 시장 환경 데이터를 DB에 저장해 둡니다. "
            "이후 Practical Validation은 저장된 snapshot을 읽어서 비용 / 유동성, 자산배분, 집중도, 시장 국면 판단의 근거로 사용합니다."
        )
        st.caption(
            "전체 저장 대상: `finance_meta.etf_provider_source_map`, `finance_meta.etf_operability_snapshot`, "
            "`finance_meta.etf_holdings_snapshot`, `finance_meta.etf_exposure_snapshot`, "
            "`finance_meta.macro_series_observation`, `finance_meta.nyse_symbol_lifecycle`"
        )
        source_map_tab, provider_tab, holdings_tab, macro_tab, lifecycle_tab = st.tabs(
            [
                "ETF 소스 매핑",
                "ETF 운용성",
                "ETF 구성 / 노출",
                "FRED 시장환경",
                "상장 / 상폐 근거",
            ]
        )

        with source_map_tab:
            _render_job_brief("discover_etf_provider_source_map")
            st.caption(
                "`nyse_etf`와 ETF asset profile을 기준으로 운용사와 공식 endpoint 후보를 찾고 검증합니다. "
                "이 테이블이 채워져야 새 ETF도 holdings / exposure 수집 대상인지 자동으로 판단할 수 있습니다."
            )
            st.caption("저장 테이블: `finance_meta.etf_provider_source_map`")
            source_map_symbols_text = st.text_area(
                "ETF Symbols",
                value=P2_PROVIDER_SOURCE_MAP_SYMBOLS,
                key="p2_provider_source_map_symbols_input",
                help="비워두면 DB의 `nyse_etf` 전체를 대상으로 source map 후보를 만듭니다. 처음에는 현재 검증 ETF부터 실행하는 것을 권장합니다.",
            )
            source_map_symbols = _parse_csv_items(source_map_symbols_text)
            source_map_cols = st.columns(2)
            source_map_limit = int(
                source_map_cols[0].number_input(
                    "Universe Limit",
                    min_value=0,
                    max_value=5000,
                    value=0,
                    step=50,
                    key="p2_provider_source_map_limit",
                    help="0이면 제한 없이 실행합니다. 전체 NYSE ETF를 한 번에 탐색하기 전에 작은 값으로 smoke 확인할 수 있습니다.",
                )
            )
            source_map_verify = source_map_cols[1].checkbox(
                "Verify Official URLs",
                value=True,
                key="p2_provider_source_map_verify",
                help="공식 URL / 다운로드 endpoint가 실제 응답하는지 확인한 row만 verified로 저장합니다.",
            )
            if source_map_symbols:
                _render_check_result(check_symbol_input(source_map_symbols))
            else:
                st.info("심볼 입력을 비우면 `nyse_etf` 전체를 대상으로 source map을 탐색합니다.")
            if st.button(
                "ETF 공식 소스 매핑 발견 실행",
                use_container_width=True,
                disabled=_has_running_job(),
            ):
                _schedule_job(
                    {
                        "action": "discover_etf_provider_source_map",
                        "job_name": "discover_etf_provider_source_map",
                        "spinner_text": "Discovering ETF provider source map...",
                        "params": {
                            "symbols": source_map_symbols or None,
                            "limit": source_map_limit or None,
                            "verify": bool(source_map_verify),
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_provider_source_map",
                            execution_mode="operational",
                            symbol_source="nyse_etf / nyse_asset_profile",
                            symbol_count=len(source_map_symbols) if source_map_symbols else None,
                            execution_context=(
                                "Practical Validation에서 ETF holdings / exposure connector를 자동 판정할 수 있도록 "
                                "운용사 공식 URL과 parser mapping을 발견하고 검증합니다."
                            ),
                            input_params={
                                "symbols": source_map_symbols or None,
                                "limit": source_map_limit or None,
                                "verify": bool(source_map_verify),
                            },
                        ),
                    }
                )
            if _is_running_action("discover_etf_provider_source_map"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="Provider Source Map Discovery",
                )
            _render_inline_last_completed_result("discover_etf_provider_source_map")

        with provider_tab:
            _render_job_brief("collect_etf_operability_provider")
            st.caption(
                "ETF가 현재 실전 운용 대상으로 적절한지 확인하기 위한 비용, 규모, 유동성, 가격 괴리, 레버리지 / 인버스 정보를 수집합니다. "
                "Practical Validation에서는 거래 가능성, 비용 부담, 레버리지 / 인버스 상품 여부를 판단하는 근거로 사용합니다."
            )
            st.caption(
                "저장 테이블: `finance_meta.etf_operability_snapshot`"
            )
            operability_symbols_text = st.text_area(
                "ETF Symbols",
                value=P2_PROVIDER_OPERABILITY_SYMBOLS,
                key="p2_operability_symbols_input",
                help="초기 공식 provider 수집 지원 대상: AOR, IEF, TLT, SPY, BIL, GLD, QQQ.",
            )
            operability_symbols = _parse_csv_items(operability_symbols_text)
            operability_cols = st.columns(4)
            operability_provider = operability_cols[0].selectbox(
                "Provider",
                ["official", "auto", "db_bridge", "ishares", "ssga", "invesco"],
                index=0,
                key="p2_operability_provider",
            )
            operability_as_of = operability_cols[1].text_input(
                "As Of Date",
                value="",
                key="p2_operability_as_of",
                help="선택 사항입니다. YYYY-MM-DD 형식으로 입력합니다. 비워두면 provider 또는 DB의 최신 기준일을 사용합니다.",
            )
            operability_lookback = int(
                operability_cols[2].number_input(
                    "Bridge Lookback Days",
                    min_value=5,
                    max_value=252,
                    value=60,
                    step=5,
                    key="p2_operability_lookback",
                )
            )
            operability_timeframe = operability_cols[3].selectbox(
                "Bridge Timeframe",
                ["1d", "1wk", "1mo"],
                index=0,
                key="p2_operability_timeframe",
            )
            operability_check = check_symbol_input(operability_symbols)
            _render_check_result(operability_check)
            if st.button(
                "ETF 운용성 스냅샷 수집",
                use_container_width=True,
                disabled=_has_running_job() or _is_blocking(operability_check),
            ):
                _schedule_job(
                    {
                        "action": "collect_etf_operability_provider",
                        "job_name": "collect_etf_operability_provider",
                        "spinner_text": "Running ETF operability provider snapshot...",
                        "params": {
                            "symbols": operability_symbols,
                            "as_of_date": operability_as_of or None,
                            "provider": operability_provider,
                            "lookback_days": operability_lookback,
                            "timeframe": operability_timeframe,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_provider_operability",
                            execution_mode="operational",
                            symbol_source="Practical Validation provider source map",
                            symbol_count=len(operability_symbols),
                            execution_context=(
                                "Practical Validation에서 비용 / 유동성 / 거래 가능성을 판단할 때 사용할 ETF operability snapshot을 수집합니다."
                            ),
                            input_params={
                                "provider": operability_provider,
                                "as_of_date": operability_as_of or None,
                                "lookback_days": operability_lookback,
                                "timeframe": operability_timeframe,
                            },
                        ),
                    }
                )
            if _is_running_action("collect_etf_operability_provider"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="ETF Operability Snapshot",
                )
            _render_inline_last_completed_result("collect_etf_operability_provider")

        with holdings_tab:
            _render_job_brief("collect_etf_holdings_exposure")
            st.caption(
                "ETF 안에 무엇이 들어있는지와 자산군 / 섹터 / 국가 / 통화 노출이 어떻게 나뉘는지 수집합니다. "
                "Practical Validation에서는 포트폴리오 자산배분, 집중도, 중복 노출을 판단하는 근거로 사용합니다. "
                "`GLD`의 row-level holdings는 아직 수집 대기 상태라 기본 목록에는 넣지 않습니다."
            )
            st.caption(
                "저장 테이블: `finance_meta.etf_holdings_snapshot`, `finance_meta.etf_exposure_snapshot`"
            )
            holdings_symbols_text = st.text_area(
                "ETF Symbols",
                value=P2_PROVIDER_HOLDINGS_SYMBOLS,
                key="p2_holdings_symbols_input",
                help="초기 row-level holdings 수집 지원 대상: AOR, IEF, TLT, SPY, BIL, QQQ.",
            )
            holdings_symbols = _parse_csv_items(holdings_symbols_text)
            holdings_cols = st.columns(3)
            holdings_provider = holdings_cols[0].selectbox(
                "Provider",
                ["official", "ishares", "ssga", "invesco"],
                index=0,
                key="p2_holdings_provider",
            )
            holdings_as_of = holdings_cols[1].text_input(
                "As Of Date",
                value="",
                key="p2_holdings_as_of",
                help="선택 사항입니다. YYYY-MM-DD 형식으로 입력합니다. 비워두면 provider 최신 holdings와 최신 저장 holdings를 사용해 exposure를 집계합니다.",
            )
            holdings_include_aggregates = holdings_cols[2].checkbox(
                "Provider Aggregate Sectors",
                value=True,
                key="p2_holdings_include_aggregates",
                help="provider가 공식 sector aggregate를 제공하면 함께 저장합니다. 현재는 SPY / QQQ에서 사용합니다.",
            )
            holdings_check = check_symbol_input(holdings_symbols)
            _render_check_result(holdings_check)
            if st.button(
                "ETF 구성 / 노출 스냅샷 수집",
                use_container_width=True,
                disabled=_has_running_job() or _is_blocking(holdings_check),
            ):
                _schedule_job(
                    {
                        "action": "collect_etf_holdings_exposure",
                        "job_name": "collect_etf_holdings_exposure",
                        "spinner_text": "Running ETF holdings and exposure snapshots...",
                        "params": {
                            "symbols": holdings_symbols,
                            "as_of_date": holdings_as_of or None,
                            "provider": holdings_provider,
                            "include_provider_aggregates": bool(holdings_include_aggregates),
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_provider_holdings_exposure",
                            execution_mode="operational",
                            symbol_source="Practical Validation provider source map",
                            symbol_count=len(holdings_symbols),
                            execution_context=(
                                "Practical Validation에서 자산배분 / 집중도 / 중복 노출을 판단할 때 사용할 ETF holdings와 exposure snapshot을 수집합니다."
                            ),
                            input_params={
                                "provider": holdings_provider,
                                "as_of_date": holdings_as_of or None,
                                "include_provider_aggregates": bool(holdings_include_aggregates),
                            },
                        ),
                    }
                )
            if _is_running_action("collect_etf_holdings_exposure"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="ETF Holdings / Exposure Snapshot",
                )
            _render_inline_last_completed_result("collect_etf_holdings_exposure")

        with macro_tab:
            _render_job_brief("collect_macro_market_context")
            st.caption(
                "VIX, 금리곡선, 신용스프레드 같은 시장 환경 데이터를 수집합니다. "
                "Practical Validation에서는 현재 시장 국면과 risk-on / risk-off 환경을 해석하는 근거로 사용합니다."
            )
            st.caption(
                "저장 테이블: `finance_meta.macro_series_observation`"
            )
            macro_series_text = st.text_area(
                "Macro Series IDs",
                value=P2_PROVIDER_MACRO_SERIES,
                key="p2_macro_series_input",
                help="기본 수집 series: VIXCLS, T10Y3M, BAA10Y.",
            )
            macro_series = _parse_csv_items(macro_series_text)
            macro_cols = st.columns(3)
            macro_start = macro_cols[0].text_input("Start", value="2016-01-01", key="p2_macro_start")
            macro_end = macro_cols[1].text_input("End", value=date.today().isoformat(), key="p2_macro_end")
            macro_source_mode = macro_cols[2].selectbox(
                "Source Mode",
                ["auto", "csv", "api"],
                index=0,
                key="p2_macro_source_mode",
                help="`auto`는 `FRED_API_KEY`가 있으면 FRED API를 사용하고, 없으면 FRED 공식 CSV download를 사용합니다.",
            )
            macro_check = check_symbol_input(macro_series)
            _render_check_result(macro_check)
            if st.button(
                "FRED 시장환경 수집",
                use_container_width=True,
                disabled=_has_running_job() or _is_blocking(macro_check),
            ):
                _schedule_job(
                    {
                        "action": "collect_macro_market_context",
                        "job_name": "collect_macro_market_context",
                        "spinner_text": "Running macro market-context snapshot...",
                        "params": {
                            "series_ids": macro_series,
                            "start": macro_start or None,
                            "end": macro_end or None,
                            "source_mode": macro_source_mode,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="practical_validation_macro_market_context",
                            execution_mode="operational",
                            symbol_source="FRED market-context source map",
                            symbol_count=len(macro_series),
                            execution_context=(
                                "Practical Validation에서 시장 국면과 risk-on / risk-off 환경을 해석할 때 사용할 FRED market-context observations를 수집합니다."
                            ),
                            input_params={
                                "series_ids": macro_series,
                                "start": macro_start or None,
                                "end": macro_end or None,
                                "source_mode": macro_source_mode,
                            },
                        ),
                    }
                )
            if _is_running_action("collect_macro_market_context"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="Macro Context Snapshot",
                )
            _render_inline_last_completed_result("collect_macro_market_context")

        with lifecycle_tab:
            _render_data_quality_callout(
                "상장 / 상폐 근거 해석 기준",
                "상장 / 상폐 근거는 Data Coverage Audit의 survivorship 해석을 보강합니다. "
                "current snapshot 계열은 historical membership PASS 근거가 아니며, 실제 historical source나 delisting source와 구분해서 봅니다.",
                tone="warning",
            )
            form25_tab, symdir_tab, sec_cik_tab, computed_tab = st.tabs(
                ["SEC Form 25", "Nasdaq 현재 상장", "SEC CIK 교차확인", "반복 관찰 요약"]
            )

            with form25_tab:
                _render_job_brief("collect_sec_form25_delistings")
                st.caption(
                    "SEC Form 25 / 25-NSE filing metadata를 읽어 delisting / withdrawal evidence를 저장합니다. "
                    "Data Coverage Audit의 survivorship / delisting control 근거를 보강하는 용도입니다."
                )
                st.caption(
                    "저장 테이블: `finance_meta.nyse_symbol_lifecycle` "
                    "(`source_type=delisting_feed`, `coverage_status=actual`)"
                )
                st.caption(
                    "Form 25가 없다는 사실은 active listing proof가 아닙니다. "
                    "complete historical universe membership은 별도 historical listing source가 필요합니다."
                )
                sec_form25_symbols_text = st.text_area(
                    "Symbols",
                    value=SEC_FORM25_DEFAULT_SYMBOLS,
                    key="sec_form25_symbols_input",
                    help="SEC ticker / CIK mapping으로 조회할 심볼을 입력합니다. 예: 과거 delisting이 의심되는 후보 ticker 목록.",
                )
                sec_form25_symbols = _parse_csv_items(sec_form25_symbols_text)
                sec_form25_user_agent = st.text_input(
                    "SEC User-Agent Override",
                    value="",
                    key="sec_form25_user_agent",
                    help="선택 사항입니다. 비워두면 `SEC_USER_AGENT` 환경변수 또는 collector 기본값을 사용합니다.",
                )
                sec_form25_cols = st.columns(2)
                sec_form25_include_archive = sec_form25_cols[0].checkbox(
                    "Search Archived Filing Files",
                    value=True,
                    key="sec_form25_include_archive",
                    help="recent filing 목록 밖의 archive JSON 파일도 일부 확인합니다.",
                )
                sec_form25_max_archive = int(
                    sec_form25_cols[1].number_input(
                        "Max Archive Files",
                        min_value=0,
                        max_value=20,
                        value=5,
                        step=1,
                        key="sec_form25_max_archive_files",
                    )
                )
                sec_form25_check = check_symbol_input(sec_form25_symbols)
                _render_check_result(sec_form25_check)
                if st.button(
                    "SEC Form 25 상폐 근거 수집",
                    width="stretch",
                    disabled=_has_running_job() or _is_blocking(sec_form25_check),
                ):
                    _schedule_job(
                        {
                            "action": "collect_sec_form25_delistings",
                            "job_name": "collect_sec_form25_delistings",
                            "spinner_text": "Running SEC Form 25 delisting evidence collection...",
                            "params": {
                                "symbols": sec_form25_symbols,
                                "user_agent": sec_form25_user_agent or None,
                                "include_archive_files": bool(sec_form25_include_archive),
                                "max_archive_files": sec_form25_max_archive,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_delisting_evidence",
                                execution_mode="operational",
                                symbol_source="SEC EDGAR company_tickers / submissions API",
                                symbol_count=len(sec_form25_symbols),
                                execution_context=(
                                    "Data Coverage Audit의 survivorship / delisting control을 보강하기 위해 "
                                    "SEC Form 25 / 25-NSE delisting evidence를 DB lifecycle table에 수집합니다."
                                ),
                                input_params={
                                    "include_archive_files": bool(sec_form25_include_archive),
                                    "max_archive_files": sec_form25_max_archive,
                                    "user_agent_override": bool(sec_form25_user_agent),
                                },
                            ),
                        }
                    )
                if _is_running_action("collect_sec_form25_delistings"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="SEC Form 25 Delisting Evidence",
                    )
                _render_inline_last_completed_result("collect_sec_form25_delistings")

            with symdir_tab:
                _render_job_brief("collect_symbol_directory_snapshots")
                st.caption(
                    "Nasdaq public Symbol Directory의 현재 listing 관찰치를 partial lifecycle evidence로 저장합니다. "
                    "이 row는 historical membership proof가 아니라 current observation입니다."
                )
                symdir_sources = st.multiselect(
                    "수집 파일",
                    options=["nasdaqlisted", "otherlisted"],
                    default=["nasdaqlisted", "otherlisted"],
                    key="symbol_directory_sources",
                    help="nasdaqlisted는 Nasdaq-listed, otherlisted는 NYSE/NYSE American 등 other-listed current file입니다.",
                )
                symdir_cols = st.columns(3)
                symdir_snapshot_date = symdir_cols[0].text_input(
                    "Snapshot Date",
                    value="",
                    key="symbol_directory_snapshot_date",
                    help="선택 사항입니다. 비워두면 source file creation date 또는 오늘 날짜를 사용합니다.",
                )
                symdir_include_test = symdir_cols[1].checkbox(
                    "Include Test Issues",
                    value=False,
                    key="symbol_directory_include_test_issues",
                )
                symdir_user_agent = symdir_cols[2].text_input(
                    "User-Agent Override",
                    value="",
                    key="symbol_directory_user_agent",
                )
                if st.button(
                    "Nasdaq 상장 관찰치 수집",
                    width="stretch",
                    disabled=_has_running_job() or not symdir_sources,
                ):
                    _schedule_job(
                        {
                            "action": "collect_symbol_directory_snapshots",
                            "job_name": "collect_symbol_directory_snapshots",
                            "spinner_text": "Collecting Nasdaq Symbol Directory current snapshots...",
                            "params": {
                                "sources": tuple(symdir_sources),
                                "user_agent": symdir_user_agent or None,
                                "include_test_issues": bool(symdir_include_test),
                                "snapshot_date": symdir_snapshot_date or None,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_lifecycle_current_snapshot",
                                execution_mode="operational",
                                symbol_source="Nasdaq public Symbol Directory",
                                symbol_count=None,
                                execution_context=(
                                    "Nasdaq public Symbol Directory current files를 partial listing_observed lifecycle evidence로 저장합니다."
                                ),
                                input_params={
                                    "sources": tuple(symdir_sources),
                                    "include_test_issues": bool(symdir_include_test),
                                    "snapshot_date": symdir_snapshot_date or None,
                                    "user_agent_override": bool(symdir_user_agent),
                                },
                            ),
                        }
                    )
                _render_inline_last_completed_result("collect_symbol_directory_snapshots")

            with sec_cik_tab:
                _render_job_brief("collect_sec_company_ticker_crosscheck")
                st.caption(
                    "SEC current CIK / ticker / exchange association을 identity cross-check로 저장합니다. "
                    "심볼 입력을 비우면 SEC file 전체를 대상으로 합니다."
                )
                sec_cik_symbols_text = st.text_area(
                    "Symbols",
                    value="",
                    key="sec_cik_crosscheck_symbols_input",
                    help="선택 사항입니다. 특정 심볼만 확인하려면 쉼표로 입력합니다.",
                )
                sec_cik_symbols = _parse_csv_items(sec_cik_symbols_text)
                if sec_cik_symbols:
                    sec_cik_check = check_symbol_input(sec_cik_symbols)
                    _render_check_result(sec_cik_check)
                else:
                    sec_cik_check = {"status": "ok", "message": "전체 SEC current association file을 대상으로 실행합니다."}
                    st.info(sec_cik_check["message"])
                sec_cik_cols = st.columns(2)
                sec_cik_snapshot_date = sec_cik_cols[0].text_input(
                    "Snapshot Date",
                    value="",
                    key="sec_cik_snapshot_date",
                )
                sec_cik_user_agent = sec_cik_cols[1].text_input(
                    "SEC User-Agent Override",
                    value="",
                    key="sec_cik_user_agent",
                )
                if st.button(
                    "SEC CIK / 티커 교차확인 수집",
                    width="stretch",
                    disabled=_has_running_job() or _is_blocking(sec_cik_check),
                ):
                    _schedule_job(
                        {
                            "action": "collect_sec_company_ticker_crosscheck",
                            "job_name": "collect_sec_company_ticker_crosscheck",
                            "spinner_text": "Collecting SEC CIK / ticker / exchange crosscheck evidence...",
                            "params": {
                                "symbols": sec_cik_symbols or None,
                                "user_agent": sec_cik_user_agent or None,
                                "snapshot_date": sec_cik_snapshot_date or None,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_lifecycle_identity_crosscheck",
                                execution_mode="operational",
                                symbol_source="SEC company_tickers_exchange.json",
                                symbol_count=len(sec_cik_symbols) if sec_cik_symbols else None,
                                execution_context=(
                                    "SEC current CIK / ticker / exchange association을 partial identity lifecycle evidence로 저장합니다."
                                ),
                                input_params={
                                    "symbols": sec_cik_symbols or None,
                                    "snapshot_date": sec_cik_snapshot_date or None,
                                    "user_agent_override": bool(sec_cik_user_agent),
                                },
                            ),
                        }
                    )
                _render_inline_last_completed_result("collect_sec_company_ticker_crosscheck")

            with computed_tab:
                _render_job_brief("collect_computed_snapshot_lifecycle")
                st.caption(
                    "이미 저장된 current listing snapshot rows를 읽어 반복 관찰 window를 partial lifecycle evidence로 요약합니다. "
                    "상폐나 historical membership을 증명하지 않습니다."
                )
                computed_symbols_text = st.text_area(
                    "Symbols",
                    value="",
                    key="computed_lifecycle_symbols_input",
                    help="선택 사항입니다. 비워두면 기존 current snapshot rows 전체를 요약합니다.",
                )
                computed_symbols = _parse_csv_items(computed_symbols_text)
                if computed_symbols:
                    computed_check = check_symbol_input(computed_symbols)
                    _render_check_result(computed_check)
                else:
                    computed_check = {"status": "ok", "message": "전체 current snapshot rows를 대상으로 실행합니다."}
                    st.info(computed_check["message"])
                computed_min_observations = int(
                    st.number_input(
                        "Minimum Observation Dates",
                        min_value=2,
                        max_value=10,
                        value=2,
                        step=1,
                        key="computed_lifecycle_min_observation_dates",
                        help="서로 다른 관찰일이 이 값 이상인 symbol만 partial summary row를 만듭니다.",
                    )
                )
                if st.button(
                    "반복 관찰 lifecycle 요약 생성",
                    width="stretch",
                    disabled=_has_running_job() or _is_blocking(computed_check),
                ):
                    _schedule_job(
                        {
                            "action": "collect_computed_snapshot_lifecycle",
                            "job_name": "collect_computed_snapshot_lifecycle",
                            "spinner_text": "Computing conservative lifecycle evidence from current snapshots...",
                            "params": {
                                "symbols": computed_symbols or None,
                                "min_observation_dates": computed_min_observations,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="data_coverage_lifecycle_computed_snapshot",
                                execution_mode="operational",
                                symbol_source="finance_meta.nyse_symbol_lifecycle current snapshots",
                                symbol_count=len(computed_symbols) if computed_symbols else None,
                                execution_context=(
                                    "기존 current snapshot rows의 반복 관찰 window를 partial computed lifecycle evidence로 요약합니다."
                                ),
                                input_params={
                                    "symbols": computed_symbols or None,
                                    "min_observation_dates": computed_min_observations,
                                },
                            ),
                        }
                    )
                _render_inline_last_completed_result("collect_computed_snapshot_lifecycle")
    return current_progress_callback


def _render_ingestion_manual_section() -> Any:
    current_progress_callback = None
    st.info(
        "수동 복구 / 진단: 특정 심볼 재수집, 저수준 파이프라인 확인, PIT inspection 같은 보조 작업입니다. "
        "정기 운영보다 느리거나 실험적인 작업은 이곳에서 필요한 범위만 좁혀 실행합니다."
    )
    with st.expander("가격 이력 수동 수집", expanded=False):
        _render_job_brief("collect_ohlcv")
        st.caption(
            "`Symbols` 입력을 사용합니다. Factors 계산 전에 가격 row를 좁은 범위로 보강할 때 적합합니다. "
            "date-range가 애매하면 `period` 기반 실행이 더 단순합니다."
        )
        st.caption("저장 테이블: `finance_price.nyse_price_history`")
        ohlcv_symbol_result = _render_symbol_source_inputs("ohlcv", "OHLCV Symbols")
        ohlcv_symbols_input = ohlcv_symbol_result["symbols"]
        ohlcv_col1, ohlcv_col2 = st.columns(2)
        ohlcv_period_input = ohlcv_col1.selectbox("OHLCV Period", PERIOD_PRESETS, index=3, key="ohlcv_period_input")
        ohlcv_interval_input = ohlcv_col2.selectbox("OHLCV Interval", ["1d", "1wk", "1mo"], index=0, key="ohlcv_interval_input")
        ohlcv_col3, ohlcv_col4 = st.columns(2)
        ohlcv_start_input = ohlcv_col3.text_input("OHLCV Start", value="", key="ohlcv_start_input")
        ohlcv_end_input = ohlcv_col4.text_input("OHLCV End", value="", key="ohlcv_end_input")
        ohlcv_resolved_period, ohlcv_resolved_start, ohlcv_resolved_end = _normalize_ohlcv_window(
            ohlcv_period_input,
            ohlcv_start_input,
            ohlcv_end_input,
        )
        if ohlcv_period_input == "7d" and not ohlcv_start_input and not ohlcv_end_input:
            st.caption(
                f"`7d`는 rolling date window로 변환됩니다: start=`{ohlcv_resolved_start}`, end=`{ohlcv_resolved_end}`."
            )
        _render_collection_contract(
            "실행 전 확인",
            [
                ("Source", _format_symbol_source_label(ohlcv_symbol_result.get("source_mode") or "Manual")),
                ("대상 수", f"{len(ohlcv_symbols_input):,} symbols"),
                (
                    "기간",
                    _format_contract_window(
                        period=ohlcv_resolved_period,
                        start=ohlcv_resolved_start,
                        end=ohlcv_resolved_end,
                    ),
                ),
                ("Interval", ohlcv_interval_input),
            ],
            note="수동 OHLCV 수집은 요청 범위 보강용입니다. 실행 후 missing / no-data / rate-limit payload를 확인하세요.",
        )
        _render_price_window_preflight(
            symbols=ohlcv_symbols_input,
            start=ohlcv_resolved_start,
            end=ohlcv_resolved_end,
            timeframe=ohlcv_interval_input,
        )
        ohlcv_symbol_check = check_symbol_input(ohlcv_symbols_input)
        _render_check_result(ohlcv_symbol_check)
        ohlcv_run_allowed = _render_large_run_guard(
            prefix="ohlcv",
            job_name="collect_ohlcv",
            symbols=ohlcv_symbols_input,
        )
        if st.button(
            "가격 이력 수동 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(ohlcv_symbol_check) or not ohlcv_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "collect_ohlcv",
                    "job_name": "collect_ohlcv",
                    "spinner_text": "Running OHLCV collection...",
                    "params": {
                        "symbols": ohlcv_symbols_input,
                        "start": ohlcv_resolved_start,
                        "end": ohlcv_resolved_end,
                        "period": ohlcv_resolved_period,
                        "interval": ohlcv_interval_input,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="manual_ohlcv_collection",
                        execution_mode="manual",
                        symbol_source=ohlcv_symbol_result.get("source_mode"),
                        symbol_count=len(ohlcv_symbols_input),
                        execution_context="Manual OHLCV ingestion for the selected symbols or universe source.",
                        input_params={
                            "start": ohlcv_resolved_start,
                            "end": ohlcv_resolved_end,
                            "period": ohlcv_resolved_period,
                            "interval": ohlcv_interval_input,
                        },
                    ),
                }
            )
        if _is_running_action("collect_ohlcv"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="OHLCV Collection",
            )
        _render_inline_last_completed_result("collect_ohlcv")

    with st.expander("자산 프로필 수동 수집", expanded=False):
        _render_job_brief("collect_asset_profiles")
        st.caption(
            "`Symbols` 입력은 사용하지 않습니다. 선택한 `Asset Profile Kinds`와 MySQL의 "
            "`nyse_stock` / `nyse_etf` universe table을 기준으로 실행합니다."
        )
        st.caption("저장 테이블: `finance_meta.nyse_asset_profile`")
        profile_kind_options = st.multiselect(
            "Asset Profile Kinds",
            options=["stock", "etf"],
            default=["stock", "etf"],
            key="profile_kind_options",
        )
        kinds = tuple(profile_kind_options) if profile_kind_options else ()
        asset_profile_check = check_asset_profile_prerequisites(kinds)
        _render_check_result(asset_profile_check)
        if st.button(
            "자산 프로필 수동 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(asset_profile_check),
        ):
            _schedule_job(
                {
                    "action": "collect_asset_profiles",
                    "job_name": "collect_asset_profiles",
                    "spinner_text": "Running asset profile collection...",
                    "params": {
                        "kinds": tuple(profile_kind_options) if profile_kind_options else ("stock", "etf"),
                    },
                }
            )
        if _is_running_action("collect_asset_profiles"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Asset Profile Collection",
            )
        _render_inline_last_completed_result("collect_asset_profiles")

    with st.expander("상세 재무제표 수동 수집", expanded=False):
        _render_job_brief("collect_financial_statements")
        st.caption(
            "`Symbols` 입력을 사용합니다. normalized fundamentals보다 느리고, issuer별 실패가 있으면 partial success가 될 수 있습니다."
        )
        st.caption(
            "이 card는 낮은 수준의 수동 수집입니다. 일상적인 statement history 복구와 quarterly coverage 보강은 "
            "위의 `Extended Statement Refresh`를 우선 사용하세요."
        )
        st.caption(
            "strict annual 운영 run에는 symbol preset dropdown의 "
            "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, `US Statement Coverage 1000`도 사용할 수 있습니다."
        )
        st.caption("저장 테이블: `finance_fundamental.nyse_financial_statement_filings`, `finance_fundamental.nyse_financial_statement_labels`, `finance_fundamental.nyse_financial_statement_values`")
        fs_symbol_result = _render_symbol_source_inputs("fs", "Financial Statement Symbols")
        fs_symbols_input = fs_symbol_result["symbols"]
        fs_col1, fs_col2 = st.columns(2)
        fs_mode_input = fs_col1.selectbox(
            "Statement Mode",
            ["annual", "quarterly"],
            index=0,
            key="fs_mode_input",
            help="일반 운영에서는 annual/quarterly 중 하나를 고르면 내부적으로 freq와 EDGAR period request를 같은 값으로 맞춰 실행합니다.",
        )
        fs_periods_input = fs_col2.number_input(
            "Financial Statement Periods",
            min_value=0,
            max_value=80,
            value=0,
            step=1,
            key="fs_periods_input",
            help="`0`이면 각 symbol에 대해 EDGAR에서 가능한 모든 statement period를 수집합니다.",
        )
        st.caption("Tip: `0 = all available periods`. quarterly strict coverage를 다시 채울 때 권장합니다.")
        st.caption(
            "`Statement Mode`는 operator용 단일 입력입니다. "
            "내부적으로는 `freq`와 `period`를 같은 값으로 맞춰 실행합니다."
        )
        fs_symbol_check = check_symbol_input(fs_symbols_input)
        _render_check_result(fs_symbol_check)
        fs_run_allowed = _render_large_run_guard(
            prefix="financial_statements",
            job_name="collect_financial_statements",
            symbols=fs_symbols_input,
        )
        if st.button(
            "상세 재무제표 수동 수집 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(fs_symbol_check) or not fs_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "collect_financial_statements",
                    "job_name": "collect_financial_statements",
                    "spinner_text": "Running financial statement ingestion...",
                    "params": {
                        "symbols": fs_symbols_input,
                        "freq": fs_mode_input,
                        "periods": int(fs_periods_input),
                        "period": fs_mode_input,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="manual_financial_statement_ingestion",
                        execution_mode="manual",
                        symbol_source=fs_symbol_result.get("source_mode"),
                        symbol_count=len(fs_symbols_input),
                        execution_context="Manual detailed financial statement ingestion for the selected symbols or universe source.",
                        input_params={
                            "statement_mode": fs_mode_input,
                            "freq": fs_mode_input,
                            "periods": int(fs_periods_input),
                            "period": fs_mode_input,
                        },
                    ),
                }
            )
        if _is_running_action("collect_financial_statements"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Financial Statement Ingestion",
            )
        _render_inline_last_completed_result("collect_financial_statements")

    with st.expander("재무제표 shadow 재구성", expanded=False):
        _render_job_brief("rebuild_statement_shadow")
        st.caption(
            "`Statement Shadow Coverage Preview`가 `raw_statement_present_but_shadow_missing`라고 표시할 때 사용합니다. "
            "raw statement row가 이미 있으면 이 경로가 더 빠릅니다."
        )
        st.caption("저장 테이블: `finance_fundamental.nyse_fundamentals_statement`, `finance_fundamental.nyse_factors_statement`")
        shadow_symbol_result = _render_symbol_source_inputs(
            "shadow_rebuild",
            "Shadow Rebuild Symbols",
            default_source_mode="Manual",
        )
        shadow_symbols_input = shadow_symbol_result["symbols"]
        shadow_freq_input = st.selectbox(
            "Shadow Rebuild Frequency",
            ["annual", "quarterly"],
            index=1,
            key="shadow_rebuild_freq_input",
            help="이미 저장된 raw statement row를 사용해 선택한 statement frequency의 shadow table을 재구성합니다.",
        )
        shadow_symbol_check = check_symbol_input(shadow_symbols_input)
        _render_check_result(shadow_symbol_check)
        shadow_run_allowed = _render_large_run_guard(
            prefix="shadow_rebuild",
            job_name="rebuild_statement_shadow",
            symbols=shadow_symbols_input,
        )
        if st.button(
            "재무제표 shadow 재구성 실행",
            use_container_width=True,
            disabled=_has_running_job() or _is_blocking(shadow_symbol_check) or not shadow_run_allowed,
        ):
            _schedule_job(
                {
                    "action": "rebuild_statement_shadow",
                    "job_name": "rebuild_statement_shadow",
                    "spinner_text": "Running statement shadow rebuild...",
                    "params": {
                        "symbols": shadow_symbols_input,
                        "freq": shadow_freq_input,
                    },
                    "run_metadata": _job_metadata(
                        pipeline_type="statement_shadow_rebuild",
                        execution_mode="manual",
                        symbol_source=shadow_symbol_result.get("source_mode"),
                        symbol_count=len(shadow_symbols_input),
                        execution_context="Manual rebuild of statement shadow tables using already stored raw statement ledgers.",
                        input_params={"freq": shadow_freq_input},
                    ),
                }
            )
        if _is_running_action("rebuild_statement_shadow"):
            current_progress_callback = _build_progress_callback(
                st.session_state.running_job,
                label="Statement Shadow Rebuild Only",
            )
        _render_inline_last_completed_result("rebuild_statement_shadow")

    with st.expander("가격 stale 원인 진단", expanded=False):
        _render_price_stale_diagnosis_card()
    if _is_running_action("diagnose_price_stale"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Price Stale Diagnosis",
        )

    with st.expander("재무제표 universe coverage QA", expanded=False):
        _render_statement_universe_coverage_qa_card()
    if _is_running_action("diagnose_statement_universe_coverage"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Statement Universe Coverage QA",
        )

    with st.expander("재무제표 coverage 원인 진단", expanded=False):
        _render_statement_coverage_diagnosis_card()
    if _is_running_action("diagnose_statement_coverage"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Statement Coverage Diagnosis",
        )

    with st.expander("재무제표 PIT inspection", expanded=False):
        _render_statement_pit_inspection_card()
    if _is_running_action("inspect_statement_pit"):
        current_progress_callback = _build_progress_callback(
            st.session_state.running_job,
            label="Statement PIT Inspection",
        )
    return current_progress_callback


def _render_selected_ingestion_collection_section(selected_collection_section: str) -> Any:
    if selected_collection_section == INGESTION_COLLECTION_OPERATIONAL:
        return _render_ingestion_operational_section()
    if selected_collection_section == INGESTION_COLLECTION_MANUAL:
        return _render_ingestion_manual_section()
    if selected_collection_section == INGESTION_COLLECTION_RECORDS:
        _render_ingestion_records_section()
    return None


def render_ingestion_console() -> None:
    _render_running_banner()
    _render_ingestion_runtime_build_indicator()
    prefill_notice = st.session_state.get("ingestion_prefill_notice")
    if prefill_notice:
        st.success(prefill_notice)
        st.session_state.ingestion_prefill_notice = None
    st.info(
        "이 화면은 외부 API / 공식 파일 / provider page에서 데이터를 수집해 MySQL에 저장하는 운영 콘솔입니다. "
        "각 작업은 기존처럼 사용자가 심볼, 기간, 소스, 옵션을 직접 정하되, 무엇을 수집하고 어디에 쓰이는지 먼저 보여줍니다."
    )
    _render_ingestion_workflow_overview()
    _render_common_last_result_summary()

    current_progress_callback = None
    collection_body = st.container()

    with collection_body:
        st.subheader("작업 영역")
        st.caption(
            "정기적으로 돌리는 일상 업데이트, 검증 데이터 보강, 수동 복구 / 진단, 실행 기록 확인을 목적별로 분리했습니다. "
            "영어 job id는 실행 기록 추적용으로만 보시면 됩니다."
        )

        selected_collection_section = _render_ingestion_collection_section_selector()

        current_progress_callback = _render_selected_ingestion_collection_section(selected_collection_section)

    if _has_running_job():
        _run_scheduled_job(progress_callback=current_progress_callback)




def render_ingestion_page(*, runtime_marker: str, loaded_at: datetime, git_sha: str | None) -> None:
    _set_runtime_context(runtime_marker=runtime_marker, loaded_at=loaded_at, git_sha=git_sha)
    _install_ingestion_responsive_styles()
    st.title("Ingestion")
    st.caption("API / 공식 파일 / provider page에서 데이터를 수집하고 DB에 저장하는 작업 공간입니다.")
    render_ingestion_console()
