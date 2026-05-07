from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
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


JobResult = dict[str, Any]
LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"
GLOSSARY_DOC_PATH = PROJECT_ROOT / ".note" / "finance" / "FINANCE_TERM_GLOSSARY.md"
GLOSSARY_META_SECTION_TITLES = {"목적", "사용 원칙"}
APP_RUNTIME_LOADED_AT = datetime.now()


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
SYMBOL_SOURCE_OPTIONS = [
    "Manual",
    "NYSE Stocks",
    "NYSE ETFs",
    "NYSE Stocks + ETFs",
    "Profile Filtered Stocks",
    "Profile Filtered ETFs",
    "Profile Filtered Stocks + ETFs",
]


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

    st.subheader("Latest Completed Run")
    _render_result_summary(result)
    st.session_state.last_completed_result = None


def _render_inline_last_completed_result(*job_names: str) -> None:
    result = st.session_state.last_completed_result
    if result is None:
        return
    if result.get("job_name") not in set(job_names):
        return
    st.markdown("#### Latest Completed Run")
    _render_result_summary(result)
    st.session_state.last_completed_result = None


def _render_result_summary(result: JobResult) -> None:
    banner = _status_to_banner(result["status"])
    banner(f'[{result["job_name"]}] {result["message"]}')

    failed_count = len(result.get("failed_symbols") or [])
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Status", result["status"])
    col2.metric("Rows Written", result["rows_written"] or 0)
    col3.metric("Symbols Requested", result["symbols_requested"] or 0)
    col4.metric("Failed Symbols", failed_count)
    col5.metric("Duration (sec)", result["duration_sec"])

    run_metadata = result.get("run_metadata") or {}
    if run_metadata:
        meta_cols = st.columns(3)
        meta_cols[0].metric("Execution Mode", run_metadata.get("execution_mode") or "-")
        meta_cols[1].metric("Pipeline Type", run_metadata.get("pipeline_type") or "-")
        meta_cols[2].metric("Runtime Marker", run_metadata.get("runtime_marker") or "-")
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
        st.write("Failed Symbols:", ", ".join((result.get("failed_symbols") or [])[:20]))

    with st.expander("Result Details", expanded=False):
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
        with st.expander("OHLCV Diagnostics", expanded=False):
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
        with st.expander("Pipeline Steps", expanded=False):
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
        with st.expander("Run Artifacts", expanded=False):
            st.caption(
                "Each run now emits a standardized JSON artifact, and when symbol-level issues exist it also emits a standardized failure CSV."
            )
            st.json(artifact_info, expanded=False)


def _render_recent_results() -> None:
    st.subheader("Recent Runs")
    results = st.session_state.recent_results
    if not results:
        st.info("No runs executed in this session yet.")
        return

    for idx, result in enumerate(results):
        with st.container(border=True):
            st.markdown(f'**{idx + 1}. {result["job_name"]}**')
            st.write(
                f'Status: `{result["status"]}` | '
                f'Started: `{result["started_at"]}` | '
                f'Finished: `{result["finished_at"]}` | '
                f'Failed Symbols: `{len(result.get("failed_symbols") or [])}`'
            )
            run_metadata = result.get("run_metadata") or {}
            symbol_source = run_metadata.get("symbol_source")
            execution_mode = run_metadata.get("execution_mode")
            pipeline_type = run_metadata.get("pipeline_type")
            execution_context = run_metadata.get("execution_context")
            if execution_mode:
                st.write(f"Execution Mode: `{execution_mode}`")
            if pipeline_type:
                st.write(f"Pipeline Type: `{pipeline_type}`")
            if symbol_source:
                st.write(f"Symbol Source: `{symbol_source}`")
            if execution_context:
                st.write(f"Execution Context: {execution_context}")
            st.write(result["message"])
            if result.get("failed_symbols"):
                st.write("Failed Symbols:", ", ".join(result["failed_symbols"]))


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
    st.subheader("Recent Logs")
    st.caption("Shows the 5 most recently updated `*.log` files under `logs/` and renders the last 20 lines of the selected file.")
    log_files = _get_recent_files(LOG_DIR, "*.log", limit=5)
    if not log_files:
        st.info("No log files found.")
        return

    labels = [p.name for p in log_files]
    selected_name = st.selectbox("Log File", labels, key="recent_log_file")
    selected = next(p for p in log_files if p.name == selected_name)

    st.caption(f"Path: {selected}")
    st.code(_read_tail(selected, max_lines=20), language="text")


def _render_failure_csv_preview() -> None:
    st.subheader("Failure CSV Preview")
    st.caption(
        "Shows recent `*failures*.csv` artifacts under `csv/`. "
        "Recent web-app runs now emit standardized failure CSVs when symbol-level issues are present, so this panel should become more useful over time."
    )
    csv_files = _get_recent_files(CSV_DIR, "*failures*.csv", limit=5)
    if not csv_files:
        st.info("No failure CSV files found.")
        return

    labels = [p.name for p in csv_files]
    selected_name = st.selectbox("Failure CSV", labels, key="failure_csv_file")
    selected = next(p for p in csv_files if p.name == selected_name)

    st.caption(f"Path: {selected}")
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
    job_name = record.get("job_name") or "-"
    status = record.get("status") or "-"
    return f"{started_at} | {job_name} | {status}"


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
    st.markdown("#### Run Inspector")
    st.caption(
        "Pick a persisted run to inspect its inputs, pipeline steps, runtime marker, related artifacts, and likely log files."
    )
    options = { _history_record_label(item): item for item in history }
    selected_label = st.selectbox(
        "Inspect Persisted Run",
        options=list(options.keys()),
        key="persistent_run_history_inspector",
    )
    selected = options[selected_label]
    _render_result_summary(selected)

    related_logs = _find_related_logs(selected)
    if related_logs:
        with st.expander("Related Logs", expanded=False):
            log_labels = [path.name for path in related_logs]
            log_name = st.selectbox(
                "Related Log File",
                options=log_labels,
                key=f"run_inspector_log_{selected.get('started_at')}_{selected.get('job_name')}",
            )
            chosen = next(path for path in related_logs if path.name == log_name)
            st.caption(f"Path: {chosen}")
            st.code(_read_tail(chosen, max_lines=20), language="text")


def _render_persistent_run_history() -> None:
    st.subheader("Persistent Run History")
    history = load_run_history(limit=30)
    if not history:
        st.info("No persisted run history found yet.")
        return

    st.caption(f"Path: {HISTORY_FILE}")
    rows = []
    for item in history:
        run_metadata = item.get("run_metadata") or {}
        input_params = run_metadata.get("input_params") or {}
        rows.append(
            {
                "started_at": item.get("started_at"),
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
        "Recent runs now also carry runtime/build metadata and standardized artifact paths. Use the inspector below to see the full payload."
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
        st.write("Run a read-only diagnosis to separate DB ingestion gaps from provider gaps and likely symbol-status issues.")
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
            "Run Price Stale Diagnosis",
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
        st.write("Run a read-only diagnosis to understand why strict statement coverage is missing and what the next action should be.")
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
            "Run Statement Coverage Diagnosis",
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
            "Run Statement PIT Inspection",
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


def _render_symbol_source_inputs(
    prefix: str,
    title: str = "Symbols",
    *,
    default_source_mode: str = "Manual",
) -> dict[str, Any]:
    default_source_index = SYMBOL_SOURCE_OPTIONS.index(default_source_mode) if default_source_mode in SYMBOL_SOURCE_OPTIONS else 0
    source_mode = st.selectbox(
        f"{title} Source",
        SYMBOL_SOURCE_OPTIONS,
        index=default_source_index,
        key=f"{prefix}_source_mode",
    )

    manual_symbols: list[str] = []
    if source_mode == "Manual":
        text_key = f"{prefix}_symbols_input"
        preset_applied_key = f"{prefix}_preset_applied"
        preset_name = st.selectbox(
            f"{title} Preset",
            list(SYMBOL_PRESETS.keys()),
            index=0,
            key=f"{prefix}_preset",
        )
        if preset_name != "Custom":
            preset_value = SYMBOL_PRESETS.get(preset_name, "")
            if st.session_state.get(preset_applied_key) != preset_name:
                st.session_state[text_key] = preset_value
                st.session_state[preset_applied_key] = preset_name
            manual_text = st.text_area(
                title,
                key=text_key,
                disabled=True,
            )
            manual_symbols = [s.strip() for s in preset_value.split(",") if s.strip()]
        else:
            if text_key not in st.session_state:
                st.session_state[text_key] = ""
            st.session_state[preset_applied_key] = preset_name
            manual_text = st.text_area(
                title,
                key=text_key,
            )
            manual_symbols = [s.strip() for s in manual_text.split(",") if s.strip()]

    source_result = resolve_symbol_source(source_mode, manual_symbols)
    if source_result["status"] == "ok":
        st.info(f'{source_result["message"]} Count: {source_result["count"]}')
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
    _render_runtime_build_indicator()
    prefill_notice = st.session_state.get("ingestion_prefill_notice")
    if prefill_notice:
        st.success(prefill_notice)
        st.session_state.ingestion_prefill_notice = None
    st.info(
        "Inputs are now grouped by job. Symbol-based jobs use their own symbol input. "
        "`Asset Profile Collection` does not use symbols; it uses the existing NYSE universe tables in MySQL."
    )

    current_progress_callback = None
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Run Jobs")
        st.caption(
            "수집 관련 작업을 `운영 파이프라인`과 `수동/진단 작업`으로 분리했습니다. "
            "정기 운영은 앞 탭, 예외 처리/디버깅/실험은 뒤 탭에서 보시면 됩니다."
        )

        operational_tab, manual_tab = st.tabs(["Operational Pipelines", "Manual Jobs / Inspection"])

        with operational_tab:
            st.info(
                "운영 파이프라인: 일상적으로 반복 실행하는 수집 작업입니다. "
                "일별 가격, 주간 펀더멘털, 확장 statement refresh, metadata refresh 같은 정기 운영 작업을 담당합니다."
            )

            with st.expander("Daily Market Update", expanded=True):
                st.write("Refresh price history for the current operating universe.")
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
                    "Run Daily Market Update",
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

            with st.expander("Weekly Fundamental Refresh", expanded=False):
                st.write("Refresh normalized fundamentals and recompute factors for the selected universe.")
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
                    "Run Weekly Fundamental Refresh",
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

            with st.expander("Extended Statement Refresh", expanded=False):
                st.write("Refresh detailed financial statement ledgers and rebuild statement shadow tables for longer-history and account-level analysis.")
                st.caption("Recommended cadence: monthly, or before deep factor research and long-horizon backtest preparation.")
                st.caption("Recommended symbol source: `Profile Filtered Stocks` or a narrower research universe, because this job is heavier than summary fundamentals refresh.")
                st.caption(
                    "If you are looking for the older lower-level `Financial Statement Ingestion` card from the checklist, "
                    "it still exists under the `Manual Jobs / Inspection` tab. For routine Phase 7/8 recovery work, start from this card."
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
                    "Run Extended Statement Refresh",
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

            with st.expander("Metadata Refresh", expanded=False):
                st.write("Refresh asset profile metadata for the currently tracked stock and ETF universes.")
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
                    "Run Metadata Refresh",
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

        with manual_tab:
            st.info(
                "수동/진단 작업: 예외 처리, 부분 재실행, 디버깅, 실험용 작업입니다. "
                "정기 운영보다는 특정 심볼 재수집, 저수준 파이프라인 확인, PIT inspection 같은 보조 작업을 담당합니다."
            )
            with st.expander("Core Market Data Pipeline", expanded=True):
                st.write("Run OHLCV collection, fundamentals ingestion, and factor calculation in sequence.")
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
                    "Run Core Pipeline",
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

            with st.expander("OHLCV Collection", expanded=False):
                st.write("Collect market price history and store it in MySQL.")
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
                    "Run OHLCV Collection",
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

            with st.expander("Fundamentals Ingestion", expanded=False):
                st.write("Collect normalized financial statement snapshots and store them in MySQL.")
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
                    "Run Fundamentals Ingestion",
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

            with st.expander("Factor Calculation", expanded=False):
                st.write("Read stored fundamentals and prices, calculate factors, and store results.")
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
                    "Run Factor Calculation",
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

            with st.expander("Asset Profile Collection", expanded=False):
                st.write("Collect stock and ETF profile metadata using the existing NYSE universe tables.")
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
                    "Run Asset Profile Collection",
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

            with st.expander("Financial Statement Ingestion", expanded=False):
                st.write("Collect detailed financial statements from EDGAR for the provided symbols.")
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
                    "Run Financial Statement Ingestion",
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

            with st.expander("Statement Shadow Rebuild Only", expanded=False):
                st.write("Rebuild statement shadow tables using already stored raw statement ledgers, without re-calling EDGAR.")
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
                    "Run Statement Shadow Rebuild",
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

            with st.expander("Price Stale Diagnosis", expanded=False):
                _render_price_stale_diagnosis_card()

            with st.expander("Statement Coverage Diagnosis", expanded=False):
                _render_statement_coverage_diagnosis_card()

            with st.expander("Statement PIT Inspection", expanded=False):
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
    st.title("Ingestion")
    st.caption("운영 파이프라인, 수동 수집, 진단 작업을 실행하는 작업 공간입니다.")
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
        st.error("`FINANCE_TERM_GLOSSARY.md`를 읽지 못했습니다. 문서 경로를 먼저 확인해 주세요.")
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
        st.caption("source: `.note/finance/FINANCE_TERM_GLOSSARY.md`")

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
