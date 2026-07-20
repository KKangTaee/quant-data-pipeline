"""Streamlit render and session-state boundary for Workspace > Ingestion."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

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
from app.services.ingestion_diagnostics import load_price_window_preflight_summary
from app.web.backtest_common import QUALITY_STRICT_PRESETS, clear_backtest_preview_caches
from app.web.reference_contextual_help import render_reference_contextual_help
from app.workspace_paths import PROJECT_ROOT


JobResult = dict[str, Any]
LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"
_runtime_marker = "unknown"
_runtime_loaded_at: datetime | None = None
_runtime_git_sha: str | None = None
from app.web.ingestion.dispatcher import (
    diagnostic_state_key as _diagnostic_state_key,
    dispatch_job as _dispatch_job,
)
from app.web.ingestion.guides import (
    COMPOSITE_PRICE_JOBS,
    DIAGNOSTIC_PROGRESS_JOBS,
    ETF_PROVIDER_JOBS,
    EVENT_CALENDAR_JOBS,
    JOB_GUIDE,
    LIFECYCLE_EVIDENCE_JOBS,
    MACRO_CONTEXT_JOBS,
    PARTIAL_LIFECYCLE_EVIDENCE_JOBS,
    PRICE_COLLECTION_JOBS,
    PROGRESS_ENABLED_ACTIONS,
    _job_domain,
    _job_guide,
    _job_title,
    _result_metric_labels,
    _status_label,
)
from app.web.ingestion.sections import (
    render_manual_section as _render_ingestion_manual_section,
    render_operational_section as _render_ingestion_operational_section,
    render_selected_section as _render_selected_ingestion_collection_section,
)
from app.web.ingestion.results import (
    _format_count,
    _format_duration,
    build_common_last_result_summary as _build_common_last_result_summary,
    build_statement_refresh_action_summary as _build_statement_refresh_action_summary,
)
from app.web.ingestion.styles import install_ingestion_responsive_styles as _install_ingestion_responsive_styles
from app.web.ingestion.registry import (
    COLLECTION_ENTRY_RELATIONSHIPS,
    INGESTION_ACTION_REGISTRY,
    INGESTION_COLLECTION_MANUAL,
    INGESTION_COLLECTION_OPERATIONAL,
    INGESTION_COLLECTION_RECORDS,
    INGESTION_COLLECTION_SECTIONS,
    MANUAL_COLLECTION_ACTIONS,
    _active_ingestion_actions,
    _compatibility_ingestion_actions,
    _infer_ingestion_collection_section,
    _is_compatibility_ingestion_action,
)
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


def _build_ohlcv_collection_params(
    *,
    symbols: list[str],
    start: str | None,
    end: str | None,
    period: str | None,
    interval: str,
    execution_profile: str | None = None,
    excluded_symbols: list[str] | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "symbols": symbols,
        "start": start,
        "end": end,
        "period": period,
        "interval": interval,
    }
    if execution_profile:
        params["execution_profile"] = execution_profile
    if excluded_symbols is not None:
        params["excluded_symbols"] = excluded_symbols
    return params


def _build_asset_profile_job(
    *,
    action: str,
    job_name: str,
    spinner_text: str,
    kinds: tuple[str, ...],
    pipeline_type: str,
    execution_mode: str,
    execution_context: str,
) -> dict[str, Any]:
    resolved_kinds = kinds or ("stock", "etf")
    return {
        "action": action,
        "job_name": job_name,
        "spinner_text": spinner_text,
        "params": {"kinds": resolved_kinds},
        "run_metadata": _job_metadata(
            pipeline_type=pipeline_type,
            execution_mode=execution_mode,
            symbol_source=None,
            symbol_count=None,
            execution_context=execution_context,
            input_params={"kinds": resolved_kinds},
        ),
    }


def _store_diagnostic_result_if_needed(result: JobResult) -> None:
    state_key = _diagnostic_state_key(str(result.get("job_name") or ""))
    if not state_key:
        return
    diagnostic_result = (result.get("details") or {}).get("diagnostic_result")
    if diagnostic_result is not None:
        st.session_state[state_key] = diagnostic_result


def _clear_running_job() -> None:
    st.session_state.running_job = None


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

    if action not in PROGRESS_ENABLED_ACTIONS:
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
        event_type = event.get("event") or event.get("type")

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
    render_reference_contextual_help("ingestion", expanded=False)
    render_ingestion_console()
