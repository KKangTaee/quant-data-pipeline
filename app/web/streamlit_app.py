from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
import subprocess
from typing import Any

import pandas as pd
import streamlit as st

# Ensure the project root is importable when Streamlit executes this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.jobs.ingestion_jobs import (
    run_collect_computed_snapshot_lifecycle,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_macro_calendar,
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
from app.jobs.diagnostics import inspect_price_stale_symbols, inspect_statement_coverage_symbols
from app.jobs.result_artifacts import write_run_artifacts
from app.jobs.preflight_checks import (
    check_asset_profile_prerequisites,
    check_factor_prerequisites,
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
from app.web.backtest_common import QUALITY_STRICT_PRESETS, clear_backtest_preview_caches
from app.web.backtest_candidate_library import render_candidate_library_page
from app.web.backtest_history import render_backtest_run_history_page
from app.web.final_selected_portfolio_dashboard import render_final_selected_portfolio_dashboard_page
from app.web.ops_review import render_operations_dashboard
from app.web.overview_dashboard import render_overview_dashboard
from app.web.pages.backtest import render_backtest_tab
from app.web.reference_guides import render_reference_guides_page
from finance.data.financial_statements import inspect_financial_statement_source
from finance.loaders import load_statement_coverage_summary, load_statement_timing_audit
from app.workspace_paths import GLOSSARY_DOC_PATH, PROJECT_ROOT as CANONICAL_PROJECT_ROOT


JobResult = dict[str, Any]
PROJECT_ROOT = CANONICAL_PROJECT_ROOT
LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"
GLOSSARY_META_SECTION_TITLES = {"목적", "사용 원칙"}
APP_RUNTIME_LOADED_AT = datetime.now()


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
        "title": "주간 펀더멘털 / 팩터 업데이트",
        "purpose": "정규화된 fundamentals를 수집하고 broad factor table을 다시 계산합니다.",
        "targets": ["finance_fundamental.nyse_fundamentals", "finance_fundamental.nyse_factors"],
        "used_by": ["Factor strategy prototype", "Backtest Analysis"],
        "caveats": ["broad fundamentals / factors는 strict filing-time PIT source가 아닙니다."],
        "next_action": "PIT가 중요한 전략은 Financial Statement / Shadow 계층 coverage를 함께 확인하세요.",
    },
    "extended_statement_refresh": {
        "title": "상세 재무제표 확장 수집",
        "purpose": "EDGAR 상세 statement ledger를 수집하고 statement shadow fundamentals / factors를 재구성합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_filings",
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "used_by": ["Strict annual / quarterly factor runtime", "Statement PIT inspection"],
        "caveats": ["period_end와 accepted_at / available_at를 구분해서 해석해야 합니다."],
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
        "title": "핵심 시장 데이터 일괄 수집",
        "purpose": "OHLCV, fundamentals, factor calculation을 순서대로 실행하는 수동 composite job입니다.",
        "targets": ["finance_price.nyse_price_history", "finance_fundamental.nyse_fundamentals", "finance_fundamental.nyse_factors"],
        "used_by": ["Backtest Analysis", "factor prototype"],
        "caveats": ["대량 실행은 rate limit과 partial coverage 가능성이 큽니다."],
        "next_action": "Pipeline Steps에서 어느 단계가 partial / failed인지 먼저 확인하세요.",
    },
    "collect_ohlcv": {
        "title": "가격 이력 수동 수집",
        "purpose": "선택한 symbol과 기간의 OHLCV, dividend, split row를 수동으로 수집합니다.",
        "targets": ["finance_price.nyse_price_history"],
        "used_by": ["Backtest Analysis", "freshness diagnostics"],
        "caveats": ["요청 범위와 실제 provider 응답 범위가 다를 수 있습니다."],
        "next_action": "누락 symbol은 Price Stale Diagnosis로 원인을 분류하세요.",
    },
    "collect_fundamentals": {
        "title": "펀더멘털 수동 수집",
        "purpose": "선택한 symbol의 normalized fundamentals summary를 수동으로 수집합니다.",
        "targets": ["finance_fundamental.nyse_fundamentals"],
        "used_by": ["Factor calculation"],
        "caveats": ["strict filing-time PIT source가 아닙니다."],
        "next_action": "factor 계산 전에 price와 fundamentals preflight를 확인하세요.",
    },
    "calculate_factors": {
        "title": "팩터 수동 계산",
        "purpose": "저장된 price와 fundamentals를 읽어 broad factor table을 계산합니다.",
        "targets": ["finance_fundamental.nyse_factors"],
        "used_by": ["Factor strategy prototype"],
        "caveats": ["입력 price / fundamentals coverage가 부족하면 row가 생성되지 않을 수 있습니다."],
        "next_action": "missing prerequisite warning이 있으면 OHLCV / fundamentals를 먼저 보강하세요.",
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


def _read_git_short_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    sha = (result.stdout or "").strip()
    return sha or None


CURRENT_GIT_SHORT_SHA = _read_git_short_sha()
APP_RUNTIME_MARKER = (
    f"{APP_RUNTIME_LOADED_AT.strftime('%Y%m%d-%H%M%S')}"
    + (f"-{CURRENT_GIT_SHORT_SHA}" if CURRENT_GIT_SHORT_SHA else "")
)


# Stop Streamlit's clear-cache shortcut from intercepting normal browser copy.
def _install_copy_shortcut_guard() -> None:
    st.html(
        """
        <script>
        (function () {
          try {
            if (document.__quantCopyShortcutGuardInstalled) {
              return;
            }
            document.__quantCopyShortcutGuardInstalled = true;
            document.addEventListener(
              "keydown",
              function (event) {
                const key = String(event.key || "").toLowerCase();
                if ((event.metaKey || event.ctrlKey) && key === "c") {
                  event.stopImmediatePropagation();
                }
              },
              true
            );
          } catch (error) {
            // If parent document access is unavailable, leave Streamlit defaults untouched.
          }
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


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


@st.cache_data(show_spinner=False)
def _load_glossary_sections() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not GLOSSARY_DOC_PATH.exists():
        return [], []

    text = GLOSSARY_DOC_PATH.read_text(encoding="utf-8")
    sections: list[dict[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections.append(
                    {
                        "title": current_title,
                        "body": "\n".join(current_lines).strip(),
                    }
                )
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append(
            {
                "title": current_title,
                "body": "\n".join(current_lines).strip(),
            }
        )

    meta_sections = [section for section in sections if section["title"] in GLOSSARY_META_SECTION_TITLES]
    term_sections = [section for section in sections if section["title"] not in GLOSSARY_META_SECTION_TITLES]
    return meta_sections, term_sections


def _filter_glossary_sections(
    sections: list[dict[str, str]],
    query: str,
    *,
    search_body: bool,
) -> list[dict[str, str]]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return sections

    matched: list[dict[str, str]] = []
    for section in sections:
        title = str(section.get("title") or "")
        body = str(section.get("body") or "")
        title_hit = normalized_query in title.lower()
        body_hit = search_body and normalized_query in body.lower()
        if title_hit or body_hit:
            matched.append(section)
    return matched


def _init_state() -> None:
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
    if "ingestion_prefill_request" not in st.session_state:
        st.session_state.ingestion_prefill_request = None
    if "ingestion_prefill_notice" not in st.session_state:
        st.session_state.ingestion_prefill_notice = None


def _apply_pending_ingestion_prefill() -> None:
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
          div[data-baseweb="select"] > div {
            min-height: 2.75rem;
          }
          div[data-baseweb="select"] > div > div {
            min-width: 0;
            overflow: visible;
            white-space: normal;
          }
          div[role="listbox"] [role="option"] {
            min-height: 2.45rem;
            white-space: normal;
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

    caveats = [str(item) for item in guide.get("caveats") or [] if str(item).strip()]
    if caveats:
        st.caption("데이터 품질 주의: " + " / ".join(caveats))


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


def _promote_pending_job() -> None:
    if st.session_state.running_job is None and st.session_state.pending_job is not None:
        st.session_state.running_job = st.session_state.pending_job
        st.session_state.pending_job = None


def _schedule_job(job: dict[str, Any]) -> None:
    if _has_running_job():
        st.warning("Another ingestion job is already running. Wait for it to finish before starting a new one.")
        return
    st.session_state.pending_job = job
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
        "runtime_marker": APP_RUNTIME_MARKER,
        "runtime_loaded_at": APP_RUNTIME_LOADED_AT.strftime("%Y-%m-%d %H:%M:%S"),
        "git_sha": CURRENT_GIT_SHORT_SHA,
    }
    if execution_context:
        metadata["execution_context"] = execution_context
    if notes:
        metadata["notes"] = notes
    return metadata


def _clear_running_job() -> None:
    st.session_state.running_job = None


def _dispatch_job(job: dict[str, Any], *, progress_callback: Any = None) -> JobResult:
    action = job["action"]
    params = dict(job["params"])

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
    st.warning(
        f'`{job["job_name"]}` is currently running. All execution buttons are temporarily disabled until it finishes.{count_suffix}'
    )


def _render_runtime_build_indicator() -> None:
    with st.container(border=True):
        st.markdown("### Runtime / Build")
        st.caption(
            "이 정보는 현재 Streamlit 프로세스가 어떤 코드 상태로 떠 있는지 보여줍니다. "
            "코드를 고친 뒤 결과가 기대와 다르면 먼저 이 `Loaded At`과 `Git SHA`를 확인하는 것이 좋습니다."
        )
        col1, col2, col3 = st.columns(3)
        col1.metric("Runtime Marker", APP_RUNTIME_MARKER)
        col2.metric("Loaded At", APP_RUNTIME_LOADED_AT.strftime("%Y-%m-%d %H:%M:%S"))
        col3.metric("Git SHA", CURRENT_GIT_SHORT_SHA or "unknown")


def _render_ingestion_runtime_build_indicator() -> None:
    with st.container(border=True):
        st.markdown("### Runtime / Build")
        st.caption(
            "이 정보는 현재 Streamlit 프로세스가 어떤 코드 상태로 떠 있는지 보여줍니다. "
            "코드를 고친 뒤 결과가 기대와 다르면 먼저 이 `Loaded At`과 `Git SHA`를 확인하는 것이 좋습니다."
        )
        _render_ingestion_meta_grid(
            [
                ("Runtime Marker", APP_RUNTIME_MARKER),
                ("Loaded At", APP_RUNTIME_LOADED_AT.strftime("%Y-%m-%d %H:%M:%S")),
                ("Git SHA", CURRENT_GIT_SHORT_SHA or "unknown"),
            ]
        )


def _render_inline_running_hint(action: str, label: str) -> None:
    if _is_running_action(action):
        st.info(f"`{label}` is running. Progress is still synchronous, so the page will update again when the job finishes.")


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
        _render_inline_running_hint(action, label)
        return None

    progress_text = st.empty()
    progress_meta = st.empty()
    progress_bar = st.progress(0)

    if action in {"collect_ohlcv", "daily_market_update"}:
        progress_text.info(f"`{label}` is running with live OHLCV progress.")
    elif action in {"extended_statement_refresh", "collect_financial_statements"}:
        progress_text.info(f"`{label}` is running with live statement-ingestion progress.")
    else:
        progress_text.info(f"`{label}` is running with pipeline-stage progress.")

    def _callback(event: dict[str, Any]) -> None:
        event_type = event.get("event")

        if action in {"collect_ohlcv", "daily_market_update"} and event_type == "batch_progress":
            total_symbols = max(int(event.get("total_symbols", symbol_count) or symbol_count), 1)
            processed_symbols = min(int(event.get("processed_symbols", 0) or 0), total_symbols)
            percent = int((processed_symbols / total_symbols) * 100)
            progress_bar.progress(percent)
            progress_meta.caption(
                "Processed "
                f"`{processed_symbols}/{total_symbols}` symbols | "
                f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
                f"rows written `{event.get('rows_written', 0)}` | "
                f"rate-limited `{event.get('rate_limited_symbols', 0)}`"
            )
            return

        if action in {"collect_ohlcv", "daily_market_update"} and event_type == "rate_limit_cooldown":
            progress_text.warning(
                f"`{label}` detected provider rate limiting. Applying cooldown before the next batch window."
            )
            progress_meta.caption(
                f"Processed `{event.get('processed_symbols', 0)}/{event.get('total_symbols', symbol_count)}` symbols | "
                f"cooldown `{event.get('cooldown_sec', 0)}` sec | "
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
                progress_meta.caption(f"Current stage: `{stage}` ({stage_index}/{total_stages})")
                return

            if event_type == "stage_complete":
                percent = int((stage_index / total_stages) * 100)
                progress_bar.progress(percent)
                progress_meta.caption(f"Completed stage: `{stage}` ({stage_index}/{total_stages})")
                return

            if event_type == "batch_progress":
                total_symbols = max(int(event.get("total_symbols", symbol_count) or symbol_count), 1)
                processed_symbols = min(int(event.get("processed_symbols", 0) or 0), total_symbols)
                stage_fraction = processed_symbols / total_symbols
                percent = int((((stage_index - 1) + stage_fraction) / total_stages) * 100)
                progress_bar.progress(percent)
                if action == "pipeline_core_market_data":
                    progress_meta.caption(
                        "Current stage: `OHLCV` | "
                        f"processed `{processed_symbols}/{total_symbols}` symbols | "
                        f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
                        f"rows written `{event.get('rows_written', 0)}`"
                    )
                return

        if action in {"extended_statement_refresh", "collect_financial_statements"} and event_type == "batch_progress":
            total_symbols = max(int(event.get("total_symbols", symbol_count) or symbol_count), 1)
            processed_symbols = min(int(event.get("processed_symbols", 0) or 0), total_symbols)
            percent = int((processed_symbols / total_symbols) * 100)
            progress_bar.progress(percent)
            progress_meta.caption(
                "Processed "
                f"`{processed_symbols}/{total_symbols}` symbols | "
                f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
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
                progress_meta.caption(f"Current stage: `{stage}` ({stage_index}/{total_stages})")
            else:
                percent = int((stage_index / total_stages) * 100)
                progress_bar.progress(percent)
                progress_meta.caption(f"Completed stage: `{stage}` ({stage_index}/{total_stages})")

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
    _render_ingestion_stat_grid(
        [
            ("상태", _status_label(status), status),
            ("저장 Row", _format_count(result.get("rows_written")), None),
            ("요청 대상", _format_count(result.get("symbols_requested")), None),
            ("누락 / 실패", _format_count(failed_count), None),
            ("소요 시간(초)", _format_duration(result.get("duration_sec")), None),
        ]
    )

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
                st.caption("Timing Breakdown")
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
                st.caption("Retry payload for rate-limited symbols")
                st.code(details["rerun_rate_limited_payload"], language="text")
            if details.get("rerun_missing_payload"):
                st.caption("Retry payload for missing-provider symbols")
                st.code(details["rerun_missing_payload"], language="text")
            provider_message_batches = details.get("provider_message_batches") or []
            if provider_message_batches:
                st.caption("Provider message excerpts")
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
        st.info("No persisted run history found yet.")
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
        with st.expander("Preflight Details", expanded=False):
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
            with st.spinner("Running price stale diagnosis..."):
                result = inspect_price_stale_symbols(
                    diag_symbols_input,
                    end=diag_end_input.isoformat(),
                    timeframe="1d",
                )
            st.session_state.price_stale_diagnosis_result = result

        result = st.session_state.get("price_stale_diagnosis_result")
        if result:
            _render_price_stale_diagnosis_result(result)


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
            with st.spinner("Running statement coverage diagnosis..."):
                result = inspect_statement_coverage_symbols(
                    diag_symbols_input,
                    freq=diag_freq_input,
                    sample_size=diag_sample_size,
                )
            st.session_state.statement_coverage_diagnosis_result = result

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
            audit_scope = inspect_symbols_input[:audit_symbol_limit]
            with st.spinner("Running statement PIT inspection..."):
                coverage_df = load_statement_coverage_summary(
                    symbols=inspect_symbols_input,
                    freq=inspect_freq,
                )
                audit_df = load_statement_timing_audit(
                    symbols=audit_scope,
                    freq=inspect_freq,
                    limit_per_symbol=audit_limit_per_symbol,
                )
                source_payload = (
                    inspect_financial_statement_source(source_symbol, sample_size=source_sample_size)
                    if source_symbol
                    else None
                )

            st.session_state.statement_pit_inspection_result = {
                "inspect_freq": inspect_freq,
                "coverage_df": coverage_df,
                "audit_df": audit_df,
                "audit_scope": audit_scope,
                "source_symbol": source_symbol,
                "source_payload": source_payload,
            }

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
        st.info(f'{_format_symbol_source_label(source_mode)} ready. Count: {source_result["count"]}')
        preview = ", ".join(source_result["symbols"][:10])
        if preview:
            st.caption(f"Preview: {preview}")
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
        st.warning(f"Large run detected: {count} symbols.")
        if estimate.get("available"):
            st.caption(estimate["message"])
        else:
            st.caption("Estimated runtime unavailable. Large runs may take several minutes or longer.")

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
            "Execution profile: `raw_heavy` | smaller batches, single-worker mode, longer cooldown, raw-universe operator sweep.",
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
            "Execution profile: `managed_refresh_short` | short-window daily refresh, larger batches, two-worker first pass, rate-limit fallback still enabled.",
        )
    if source_mode == "Profile Filtered Stocks + ETFs":
        return (
            "managed_fast",
            "Execution profile: `managed_fast` | larger managed-universe batches, shorter idle sleep, lighter cooldown.",
        )
    return (
        "managed_safe",
        "Execution profile: `managed_safe` | moderate batching for narrower or manual universes with built-in cooldown.",
    )


def _render_ingestion_console() -> None:
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

    current_progress_callback = None
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("수집 작업")
        st.caption(
            "정기적으로 돌리는 일상 업데이트와, 검증 데이터 보강 / 수동 복구 / 진단 작업을 분리했습니다. "
            "영어 job id는 실행 기록 추적용으로만 보시면 됩니다."
        )

        operational_tab, manual_tab = st.tabs(["일상 운영 / 검증 데이터", "수동 복구 / 진단"])

        with operational_tab:
            st.info(
                "일상 운영 / 검증 데이터: 백테스트와 Practical Validation, Overview가 DB에서 읽을 데이터를 채웁니다. "
                "수집 결과가 부분 성공이면 downstream 화면에서도 coverage gap으로 남을 수 있습니다."
            )

            with st.expander("일별 가격 업데이트", expanded=True):
                _render_job_brief("daily_market_update")
                st.caption("Recommended cadence: every trading day after market close or before the next backtest/data sync.")
                st.caption(
                    "Recommended symbol source: use `Profile Filtered Stocks + ETFs` for routine refreshes. "
                    "Use raw `NYSE Stocks + ETFs` only for broad operator sweeps."
                )
                st.caption("Current defaults: `Profile Filtered Stocks + ETFs`, `1d`, `1d`.")
                st.caption("Writes to: `finance_price.nyse_price_history`")
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
                            "Filtered non-plain symbols for provider stability: "
                            f"`{len(daily_excluded_symbols)}` excluded, `{len(daily_filtered_symbols)}` remain."
                        )
                        st.caption(f"Excluded sample: {', '.join(daily_excluded_symbols[:10])}")
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

            with st.expander("주간 펀더멘털 / 팩터 업데이트", expanded=False):
                _render_job_brief("weekly_fundamental_refresh")
                st.caption("Recommended cadence: once per week, or after a meaningful batch of earnings / filing updates.")
                st.caption("Recommended symbol source: match the same stock universe used by Daily Market Update so factor coverage stays aligned.")
                st.caption("Current defaults: `NYSE Stocks`, `quarterly`.")
                st.caption("Large NYSE stock runs can take noticeably longer than OHLCV refreshes because this job executes both fundamentals ingestion and factor recomputation.")
                st.caption("Writes to: `finance_fundamental.nyse_fundamentals`, `finance_fundamental.nyse_factors`")
                weekly_symbol_result = _render_symbol_source_inputs(
                    "weekly_fundamental",
                    "Weekly Refresh Symbols",
                    default_source_mode="NYSE Stocks",
                )
                weekly_symbols_input = weekly_symbol_result["symbols"]
                weekly_freq_input = st.selectbox(
                    "Weekly Refresh Frequency",
                    ["annual", "quarterly"],
                    index=1,
                    key="weekly_refresh_freq_input",
                )
                weekly_symbol_check = check_symbol_input(weekly_symbols_input)
                _render_check_result(weekly_symbol_check)
                weekly_run_allowed = _render_large_run_guard(
                    prefix="weekly_fundamental",
                    job_name="weekly_fundamental_refresh",
                    symbols=weekly_symbols_input,
                )
                if st.button(
                    "주간 펀더멘털 / 팩터 업데이트 실행",
                    use_container_width=True,
                    disabled=_has_running_job() or _is_blocking(weekly_symbol_check) or not weekly_run_allowed,
                ):
                    _schedule_job(
                        {
                            "action": "weekly_fundamental_refresh",
                            "job_name": "weekly_fundamental_refresh",
                            "spinner_text": "Running weekly fundamental refresh...",
                            "params": {
                                "symbols": weekly_symbols_input,
                                "freq": weekly_freq_input,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="weekly_fundamental_refresh",
                                execution_mode="operational",
                                symbol_source=weekly_symbol_result.get("source_mode"),
                                symbol_count=len(weekly_symbols_input),
                                execution_context="Routine weekly refresh of normalized fundamentals and derived factors.",
                                input_params={"freq": weekly_freq_input},
                            ),
                        }
                    )
                if _is_running_action("weekly_fundamental_refresh"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="Weekly Fundamental Refresh",
                    )
                _render_inline_last_completed_result("weekly_fundamental_refresh")

            with st.expander("상세 재무제표 확장 수집", expanded=False):
                _render_job_brief("extended_statement_refresh")
                st.caption("Recommended cadence: monthly, or before deep factor research and long-horizon backtest preparation.")
                st.caption("Recommended symbol source: `Profile Filtered Stocks` or a narrower research universe, because this job is heavier than summary fundamentals refresh.")
                st.caption(
                    "If you are looking for the older lower-level `Financial Statement Ingestion` card from the checklist, "
                    "it still exists under the `수동 복구 / 진단` tab. For routine Phase 7/8 recovery work, start from this card."
                )
                st.caption(
                    "Managed annual coverage presets are also available in the symbol preset dropdown: "
                    "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, and `US Statement Coverage 1000`."
                )
                st.caption("Current defaults: `Profile Filtered Stocks`, `annual`, `0 periods (all available)`.")
                st.caption(
                    "Writes to: "
                    "`finance_fundamental.nyse_financial_statement_filings`, "
                    "`finance_fundamental.nyse_financial_statement_labels`, "
                    "`finance_fundamental.nyse_financial_statement_values`, "
                    "`finance_fundamental.nyse_fundamentals_statement`, "
                    "`finance_fundamental.nyse_factors_statement`"
                )
                ext_symbol_result = _render_symbol_source_inputs(
                    "extended_statement",
                    "Extended Statement Symbols",
                    default_source_mode="Profile Filtered Stocks",
                )
                ext_symbols_input = ext_symbol_result["symbols"]
                ext_col1, ext_col2 = st.columns(2)
                ext_period_input = ext_col1.selectbox("Extended Statement Period Type", ["annual", "quarterly"], index=0, key="ext_period_input")
                ext_periods_input = ext_col2.number_input(
                    "Extended Statement Periods",
                    min_value=0,
                    max_value=80,
                    value=0,
                    step=1,
                    key="ext_periods_input",
                    help="`0` means collect all available statement periods from the source. Use this for PIT recovery and quarterly history hardening.",
                )
                st.caption("`freq` is automatically matched to the selected `Period Type` for this operational pipeline.")
                st.caption("Tip: `0 = all available periods`. Use a positive number only when you intentionally want a shorter rolling refresh.")
                ext_symbol_check = check_symbol_input(ext_symbols_input)
                _render_check_result(ext_symbol_check)
                ext_run_allowed = _render_large_run_guard(
                    prefix="extended_statement",
                    job_name="extended_statement_refresh",
                    symbols=ext_symbols_input,
                )
                if st.button(
                    "상세 재무제표 확장 수집 실행",
                    use_container_width=True,
                    disabled=_has_running_job() or _is_blocking(ext_symbol_check) or not ext_run_allowed,
                ):
                    _schedule_job(
                        {
                            "action": "extended_statement_refresh",
                            "job_name": "extended_statement_refresh",
                            "spinner_text": "Running extended statement refresh...",
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
                                execution_context="Extended refresh of detailed financial statement ledgers for long-horizon analysis.",
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
                        label="Extended Statement Refresh",
                    )
                _render_inline_last_completed_result("extended_statement_refresh")

            with st.expander("종목 메타데이터 업데이트", expanded=False):
                _render_job_brief("metadata_refresh")
                st.caption("Recommended cadence: weekly or whenever the tracked universe definition / profile filters change.")
                st.caption("Recommended source scope: keep both `stock` and `etf` selected unless you are intentionally refreshing only one side of the universe.")
                st.caption("Writes to: `finance_meta.nyse_asset_profile`")
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
                    st.caption(
                        "상장 / 상폐 근거는 Data Coverage Audit의 survivorship 해석을 보강합니다. "
                        "current snapshot 계열은 historical membership PASS 근거가 아니며, 실제 historical source나 delisting source와 구분해서 봅니다."
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

        with manual_tab:
            st.info(
                "수동 복구 / 진단: 특정 심볼 재수집, 저수준 파이프라인 확인, PIT inspection 같은 보조 작업입니다. "
                "정기 운영보다 느리거나 실험적인 작업은 이곳에서 필요한 범위만 좁혀 실행합니다."
            )
            with st.expander("핵심 시장 데이터 일괄 수집", expanded=True):
                _render_job_brief("pipeline_core_market_data")
                st.caption(
                    "Execution order: OHLCV -> Fundamentals -> Factors. "
                    "This is a manual composite job for one-off full reruns on the current symbol set."
                )
                st.caption("Writes to: `finance_price.nyse_price_history`, `finance_fundamental.nyse_fundamentals`, `finance_fundamental.nyse_factors`")
                pipeline_symbol_result = _render_symbol_source_inputs("pipeline", "Pipeline Symbols")
                pipeline_symbols_input = pipeline_symbol_result["symbols"]
                pipe_col1, pipe_col2 = st.columns(2)
                pipeline_period_input = pipe_col1.selectbox("Pipeline Period", PERIOD_PRESETS, index=3, key="pipeline_period_input")
                pipeline_interval_input = pipe_col2.selectbox("Pipeline Interval", ["1d", "1wk", "1mo"], index=0, key="pipeline_interval_input")
                pipe_col3, pipe_col4, pipe_col5 = st.columns(3)
                pipeline_start_input = pipe_col3.text_input("Pipeline Start", value="", key="pipeline_start_input")
                pipeline_end_input = pipe_col4.text_input("Pipeline End", value="", key="pipeline_end_input")
                pipeline_freq_input = pipe_col5.selectbox("Pipeline Freq", ["annual", "quarterly"], index=0, key="pipeline_freq_input")
                pipeline_resolved_period, pipeline_resolved_start, pipeline_resolved_end = _normalize_ohlcv_window(
                    pipeline_period_input,
                    pipeline_start_input,
                    pipeline_end_input,
                )
                if pipeline_period_input == "7d" and not pipeline_start_input and not pipeline_end_input:
                    st.caption(
                        f"`7d` is handled as a rolling date window: start=`{pipeline_resolved_start}`, end=`{pipeline_resolved_end}`."
                    )
                pipeline_symbol_check = check_symbol_input(pipeline_symbols_input)
                _render_check_result(pipeline_symbol_check)
                pipeline_run_allowed = _render_large_run_guard(
                    prefix="pipeline",
                    job_name="pipeline_core_market_data",
                    symbols=pipeline_symbols_input,
                )
                if st.button(
                    "핵심 시장 데이터 일괄 수집 실행",
                    use_container_width=True,
                    disabled=_has_running_job() or _is_blocking(pipeline_symbol_check) or not pipeline_run_allowed,
                ):
                    _schedule_job(
                        {
                            "action": "pipeline_core_market_data",
                            "job_name": "pipeline_core_market_data",
                            "spinner_text": "Running core market-data pipeline...",
                            "params": {
                                "symbols": pipeline_symbols_input,
                                "start": pipeline_resolved_start,
                                "end": pipeline_resolved_end,
                                "period": pipeline_resolved_period,
                                "interval": pipeline_interval_input,
                                "freq": pipeline_freq_input,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="core_market_data_pipeline",
                                execution_mode="manual",
                                symbol_source=pipeline_symbol_result.get("source_mode"),
                                symbol_count=len(pipeline_symbols_input),
                                execution_context="Manual composite run of OHLCV, fundamentals, and factor calculation in sequence.",
                                input_params={
                                    "start": pipeline_resolved_start,
                                    "end": pipeline_resolved_end,
                                    "period": pipeline_resolved_period,
                                    "interval": pipeline_interval_input,
                                    "freq": pipeline_freq_input,
                                },
                            ),
                        }
                    )
                if _is_running_action("pipeline_core_market_data"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="Core Market Data Pipeline",
                    )
                _render_inline_last_completed_result("pipeline_core_market_data")

            with st.expander("가격 이력 수동 수집", expanded=False):
                _render_job_brief("collect_ohlcv")
                st.caption(
                    "Uses the `Symbols` input. Recommended before running Factors. "
                    "Current date-range handling is more reliable with `period` than with `end`."
                )
                st.caption("Writes to: `finance_price.nyse_price_history`")
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
                        f"`7d` is handled as a rolling date window: start=`{ohlcv_resolved_start}`, end=`{ohlcv_resolved_end}`."
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

            with st.expander("펀더멘털 수동 수집", expanded=False):
                _render_job_brief("collect_fundamentals")
                st.caption(
                    "Uses the `Symbols` input. Required before `Factor Calculation` for those symbols."
                )
                st.caption("Writes to: `finance_fundamental.nyse_fundamentals`")
                fundamentals_symbol_result = _render_symbol_source_inputs("fundamentals", "Fundamentals Symbols")
                fundamentals_symbols_input = fundamentals_symbol_result["symbols"]
                fundamentals_freq_input = st.selectbox(
                    "Fundamentals Frequency",
                    ["annual", "quarterly"],
                    index=0,
                    key="fundamentals_freq_input",
                )
                fundamentals_symbol_check = check_symbol_input(fundamentals_symbols_input)
                _render_check_result(fundamentals_symbol_check)
                fundamentals_run_allowed = _render_large_run_guard(
                    prefix="fundamentals",
                    job_name="collect_fundamentals",
                    symbols=fundamentals_symbols_input,
                )
                if st.button(
                    "펀더멘털 수동 수집 실행",
                    use_container_width=True,
                    disabled=_has_running_job() or _is_blocking(fundamentals_symbol_check) or not fundamentals_run_allowed,
                ):
                    _schedule_job(
                        {
                            "action": "collect_fundamentals",
                            "job_name": "collect_fundamentals",
                            "spinner_text": "Running fundamentals ingestion...",
                            "params": {
                                "symbols": fundamentals_symbols_input,
                                "freq": fundamentals_freq_input,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="manual_fundamentals_ingestion",
                                execution_mode="manual",
                                symbol_source=fundamentals_symbol_result.get("source_mode"),
                                symbol_count=len(fundamentals_symbols_input),
                                execution_context="Manual normalized fundamentals ingestion for the selected symbols or universe source.",
                                input_params={"freq": fundamentals_freq_input},
                            ),
                        }
                    )
                if _is_running_action("collect_fundamentals"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="Fundamentals Ingestion",
                    )
                _render_inline_last_completed_result("collect_fundamentals")

            with st.expander("팩터 수동 계산", expanded=False):
                _render_job_brief("calculate_factors")
                st.caption(
                    "Uses the `Symbols` input. Requires matching OHLCV and fundamentals data to already exist in MySQL."
                )
                st.caption("Writes to: `finance_fundamental.nyse_factors`")
                factor_symbol_result = _render_symbol_source_inputs("factor", "Factor Symbols")
                factor_symbols_input = factor_symbol_result["symbols"]
                factor_col1, factor_col2, factor_col3 = st.columns(3)
                factor_freq_input = factor_col1.selectbox("Factor Frequency", ["annual", "quarterly"], index=0, key="factor_freq_input")
                factor_start_input = factor_col2.text_input("Factor Start", value="", key="factor_start_input")
                factor_end_input = factor_col3.text_input("Factor End", value="", key="factor_end_input")
                factor_check = check_factor_prerequisites(factor_symbols_input, freq=factor_freq_input)
                _render_check_result(factor_check)
                factor_run_allowed = _render_large_run_guard(
                    prefix="factor",
                    job_name="calculate_factors",
                    symbols=factor_symbols_input,
                )
                if st.button(
                    "팩터 수동 계산 실행",
                    use_container_width=True,
                    disabled=_has_running_job() or _is_blocking(factor_check) or not factor_run_allowed,
                ):
                    _schedule_job(
                        {
                            "action": "calculate_factors",
                            "job_name": "calculate_factors",
                            "spinner_text": "Running factor calculation...",
                            "params": {
                                "symbols": factor_symbols_input,
                                "freq": factor_freq_input,
                                "start": factor_start_input or None,
                                "end": factor_end_input or None,
                            },
                            "run_metadata": _job_metadata(
                                pipeline_type="manual_factor_calculation",
                                execution_mode="manual",
                                symbol_source=factor_symbol_result.get("source_mode"),
                                symbol_count=len(factor_symbols_input),
                                execution_context="Manual factor calculation using already stored prices and fundamentals.",
                                input_params={
                                    "freq": factor_freq_input,
                                    "start": factor_start_input or None,
                                    "end": factor_end_input or None,
                                },
                            ),
                        }
                    )
                if _is_running_action("calculate_factors"):
                    current_progress_callback = _build_progress_callback(
                        st.session_state.running_job,
                        label="Factor Calculation",
                    )
                _render_inline_last_completed_result("calculate_factors")

            with st.expander("자산 프로필 수동 수집", expanded=False):
                _render_job_brief("collect_asset_profiles")
                st.caption(
                    "Does not use the `Symbols` input. Uses the selected `Asset Profile Kinds` and reads from "
                    "`nyse_stock` / `nyse_etf` in MySQL."
                )
                st.caption("Writes to: `finance_meta.nyse_asset_profile`")
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
                    "Uses the `Symbols` input. This job is usually slower than the normalized fundamentals job and may "
                    "produce partial success if some issuers fail."
                )
                st.caption(
                    "This is the lower-level manual ingestion card. For routine statement history recovery and quarterly coverage work, "
                    "prefer `Extended Statement Refresh` above."
                )
                st.caption(
                    "For strict annual operator runs, the symbol preset dropdown also exposes "
                    "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, and `US Statement Coverage 1000`."
                )
                st.caption("Writes to: `finance_fundamental.nyse_financial_statement_filings`, `finance_fundamental.nyse_financial_statement_labels`, `finance_fundamental.nyse_financial_statement_values`")
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
                    help="`0` means collect all available statement periods from EDGAR for each symbol.",
                )
                st.caption("Tip: `0 = all available periods`. This is recommended when rebuilding quarterly strict coverage.")
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
                    "Use this when `Statement Shadow Coverage Preview` says `raw_statement_present_but_shadow_missing`. "
                    "This is the faster recovery path when raw statement rows already exist."
                )
                st.caption("Writes to: `finance_fundamental.nyse_fundamentals_statement`, `finance_fundamental.nyse_factors_statement`")
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
                    help="Rebuild the shadow tables for the selected statement frequency using already stored raw statement rows.",
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

            with st.expander("재무제표 coverage 원인 진단", expanded=False):
                _render_statement_coverage_diagnosis_card()

            with st.expander("재무제표 PIT inspection", expanded=False):
                _render_statement_pit_inspection_card()

    with col_right:
        _render_recent_results()
        st.divider()
        _render_persistent_run_history()
        st.divider()
        _render_recent_logs()
        st.divider()
        _render_failure_csv_preview()

    if _has_running_job():
        _run_scheduled_job(progress_callback=current_progress_callback)


def _render_overview_page() -> None:
    _render_running_banner()
    render_overview_dashboard(
        runtime_marker=APP_RUNTIME_MARKER,
        loaded_at=APP_RUNTIME_LOADED_AT,
        git_sha=CURRENT_GIT_SHORT_SHA,
        latest_result=st.session_state.get("last_completed_result"),
        recent_results=st.session_state.get("recent_results") or [],
        render_runtime_snapshot=_render_runtime_build_indicator,
    )


def _render_ingestion_page() -> None:
    _install_ingestion_responsive_styles()
    st.title("Ingestion")
    st.caption("API / 공식 파일 / provider page에서 데이터를 수집하고 DB에 저장하는 작업 공간입니다.")
    _render_ingestion_console()


def _render_backtest_page() -> None:
    st.title("Backtest")
    st.caption("백테스트 실행부터 비교, 후보 검토, Pre-Live 운영 기록, Portfolio Proposal까지 이어지는 후보 검토 작업 공간입니다.")
    render_backtest_tab()


def _render_ops_review_page() -> None:
    render_operations_dashboard(
        runtime_marker=APP_RUNTIME_MARKER,
        loaded_at=APP_RUNTIME_LOADED_AT,
        git_sha=CURRENT_GIT_SHORT_SHA,
        running_job=st.session_state.get("running_job"),
        recent_results=st.session_state.get("recent_results") or [],
        log_dir=LOG_DIR,
        csv_dir=CSV_DIR,
        render_runtime_snapshot=_render_runtime_build_indicator,
    )


def _render_backtest_run_history_page(open_backtest_page) -> None:
    render_backtest_run_history_page(open_backtest_page=open_backtest_page)


# Render the saved candidate library and replay surface under Operations.
def _render_candidate_library_page() -> None:
    render_candidate_library_page()


def _render_selected_portfolio_dashboard_page() -> None:
    render_final_selected_portfolio_dashboard_page()


def _render_guides_page() -> None:
    render_reference_guides_page(
        runtime_marker=APP_RUNTIME_MARKER,
        loaded_at=APP_RUNTIME_LOADED_AT,
        git_sha=CURRENT_GIT_SHORT_SHA,
        render_runtime_snapshot=_render_runtime_build_indicator,
    )


def _render_glossary_page() -> None:
    st.title("Glossary")
    st.caption("현재 퀀트 프로그램에서 쓰는 용어를 검색하고 다시 확인하는 reference 페이지입니다.")
    _render_runtime_build_indicator()

    meta_sections, term_sections = _load_glossary_sections()
    if not term_sections and not meta_sections:
        st.error("`.aiworkspace/note/finance/docs/GLOSSARY.md`를 읽지 못했습니다. 문서 경로를 먼저 확인해 주세요.")
        st.code(str(GLOSSARY_DOC_PATH), language="text")
        return

    with st.container(border=True):
        st.markdown("### 용어 검색")
        st.caption("용어 제목만 검색할 수도 있고, 본문까지 같이 검색해서 관련 설명을 더 넓게 찾을 수도 있습니다.")
        query = st.text_input(
            "검색어",
            value="",
            key="reference_glossary_query",
            placeholder="예: promotion, shortlist, liquidity, universe",
        )
        search_body = st.checkbox(
            "본문까지 함께 검색",
            value=True,
            key="reference_glossary_search_body",
        )

        matched_sections = _filter_glossary_sections(term_sections, query, search_body=search_body)
        metric_cols = st.columns(3)
        metric_cols[0].metric("총 용어 수", len(term_sections))
        metric_cols[1].metric("검색 결과", len(matched_sections))
        metric_cols[2].metric("검색 범위", "제목+본문" if search_body else "제목만")
        st.caption("source: `.aiworkspace/note/finance/docs/GLOSSARY.md`")

    if meta_sections:
        with st.expander("이 reference를 어떻게 읽으면 되나", expanded=False):
            for section in meta_sections:
                with st.container(border=True):
                    st.markdown(f"#### {section['title']}")
                    st.markdown(section["body"])

    if query.strip() and not matched_sections:
        st.warning("검색 결과가 없습니다. 검색어를 조금 줄이거나 영어/한글 핵심 단어만 넣어 다시 확인해 주세요.")
        st.caption("예: `promotion`, `guardrail`, `유동성`, `benchmark`, `PIT`")
        return

    st.markdown("### 용어 목록")
    if not query.strip():
        st.caption("검색어가 없어서 전체 용어를 보여주고 있습니다.")
    elif len(matched_sections) <= 5:
        st.caption("검색 결과가 적어서 관련 용어를 바로 펼쳐 보여줍니다.")
    else:
        st.caption("검색 결과가 많아서 제목 순서대로 정리했습니다. 필요한 항목만 펼쳐서 보시면 됩니다.")

    preview_titles = ", ".join(section["title"] for section in matched_sections[:8])
    if preview_titles:
        st.caption(f"빠른 훑어보기: {preview_titles}")

    auto_expand = bool(query.strip() and len(matched_sections) <= 5)
    for section in matched_sections:
        with st.expander(section["title"], expanded=auto_expand):
            st.markdown(section["body"])


def main() -> None:
    st.set_page_config(
        page_title="Finance Console",
        page_icon="F",
        layout="wide",
    )
    _install_copy_shortcut_guard()
    _init_state()
    _promote_pending_job()
    _apply_pending_ingestion_prefill()

    overview_page = st.Page(_render_overview_page, title="Overview", icon="🏠", default=True, url_path="overview")
    ingestion_page = st.Page(_render_ingestion_page, title="Ingestion", icon="🛠️", url_path="ingestion")
    backtest_page = st.Page(_render_backtest_page, title="Backtest", icon="📈", url_path="backtest")
    ops_review_page = st.Page(_render_ops_review_page, title="Ops Review", icon="🧾", url_path="ops-review")

    def open_backtest_page() -> None:
        st.switch_page(backtest_page)

    backtest_history_page = st.Page(
        lambda: _render_backtest_run_history_page(open_backtest_page),
        title="Backtest Run History",
        icon="🗂️",
        url_path="backtest-run-history",
    )
    candidate_library_page = st.Page(
        _render_candidate_library_page,
        title="Candidate Library",
        icon="📌",
        url_path="candidate-library",
    )
    selected_portfolio_dashboard_page = st.Page(
        _render_selected_portfolio_dashboard_page,
        title="Selected Portfolio Dashboard",
        icon="📊",
        url_path="selected-portfolio-dashboard",
    )
    guides_page = st.Page(_render_guides_page, title="Guides", icon="📚", url_path="guides")
    glossary_page = st.Page(_render_glossary_page, title="Glossary", icon="📖", url_path="glossary")

    navigation = st.navigation(
        {
            "Workspace": [
                overview_page,
                ingestion_page,
                backtest_page,
            ],
            "Operations": [
                ops_review_page,
                selected_portfolio_dashboard_page,
                backtest_history_page,
                candidate_library_page,
            ],
            "Reference": [
                guides_page,
                glossary_page,
            ],
        },
        position="top",
    )
    navigation.run()

if __name__ == "__main__":
    main()
