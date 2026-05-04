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
from app.web.overview_dashboard import render_overview_dashboard
from app.web.pages.backtest import render_backtest_tab
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
    st.title("Ops Review")
    st.caption("최근 실행 결과, persistent history, 로그와 failure artifact를 운영 관점에서 한 곳에 모아 봅니다.")
    _render_running_banner()
    _render_runtime_build_indicator()

    left, right = st.columns([3, 2])
    with left:
        _render_recent_results()
        st.divider()
        _render_persistent_run_history()
    with right:
        _render_recent_logs()
        st.divider()
        _render_failure_csv_preview()


def _render_backtest_run_history_page(open_backtest_page) -> None:
    render_backtest_run_history_page(open_backtest_page=open_backtest_page)


# Render the saved candidate library and replay surface under Operations.
def _render_candidate_library_page() -> None:
    render_candidate_library_page()


def _render_guides_page() -> None:
    st.title("Guides")
    st.caption("현재 운영 기준과 phase 문서를 빠르게 찾는 참고 페이지입니다.")
    _render_runtime_build_indicator()

    st.markdown("### 핵심 개념 가이드")
    st.caption("Real-Money 해석, contract 입력, GTAA Risk-Off처럼 단계 진행 전에 자주 헷갈리는 개념을 모았습니다.")

    with st.expander("실전 승격 흐름 빠른 설명", expanded=True):
        st.caption("Backtest 결과 화면의 `Real-Money > 현재 판단`에서 보이는 값을 먼저 이해하기 위한 요약입니다.")
        st.code("Backtest 결과 -> Real-Money -> 현재 판단", language="text")

        stage_tabs = st.tabs(["Promotion", "Shortlist", "어떻게 다음 단계로 가나"])

        with stage_tabs[0]:
            st.markdown(
                """
                `Promotion`은 이 전략을 실전형 후보로 어디까지 올릴 수 있는지 보는 상위 판단입니다.

                - `hold`
                  아직 실전형 후보로 올리지 않습니다. 연구용/추가 검토용 상태입니다.
                - `production_candidate`
                  운영 후보로는 볼 수 있지만, 아직 보수적인 검토가 더 필요합니다.
                - `real_money_candidate`
                  실전형 후보까지 올라온 상태입니다. 다음은 `paper probation`이나 `small capital trial` 단계입니다.
                """
            )
            st.info(
                "한 줄로 보면 `hold -> production_candidate -> real_money_candidate` 순서로 승격됩니다."
            )

        with stage_tabs[1]:
            st.markdown(
                """
                `Shortlist`는 promotion 결과를 실제 운용 후보 상태로 번역한 값입니다.

                - `hold`
                  아직 운용 후보군에 올리지 않습니다.
                - `watchlist`
                  관찰 후보입니다. 버릴 전략은 아니지만, 아직 한 단계 더 검토가 필요합니다.
                - `paper_probation`
                  paper tracking / 종이매매 추적 단계까지 올릴 수 있습니다.
                - `small_capital_trial`
                  아주 작은 실전 자금 시험까지 고려 가능한 상태입니다.
                """
            )
            st.info(
                "한 줄로 보면 `hold -> watchlist -> paper_probation -> small_capital_trial` 흐름으로 읽으면 됩니다."
            )

        with stage_tabs[2]:
            promo_col, shortlist_col = st.columns(2)

            with promo_col:
                with st.container(border=True):
                    st.markdown("#### Promotion이 올라가려면")
                    st.caption("먼저 `hold`를 벗기고, 그 다음 `real_money_candidate`까지 올리는 흐름입니다.")
                    st.markdown("**1. `hold -> production_candidate`**")
                    st.markdown(
                        """
                        아래 항목들에서 `caution`, `unavailable`, `error`를 먼저 줄여야 합니다.

                        - `Validation`
                        - `Benchmark Policy`
                        - `Liquidity Policy`
                        - `Validation Policy`
                        - `Portfolio Guardrail Policy`
                        - ETF 전략이면 `ETF Operability`
                        - `Price Freshness`
                        """
                    )
                    st.markdown("**2. `production_candidate -> real_money_candidate`**")
                    st.markdown(
                        """
                        이 단계는 더 엄격합니다.

                        - 핵심 정책 상태가 대부분 `normal`이어야 합니다.
                        - benchmark가 있어야 합니다.
                        - static universe가 아니어야 합니다.
                        - freshness가 `warning`이나 `error`가 아니어야 합니다.
                        """
                    )

            with shortlist_col:
                with st.container(border=True):
                    st.markdown("#### Shortlist가 올라가려면")
                    st.caption("Promotion 결과를 실제 운용 후보 상태로 번역하는 단계입니다.")
                    st.markdown("**1. `shortlist = hold`**")
                    st.markdown(
                        """
                        보통 `promotion = hold`에서 같이 나옵니다.

                        - 먼저 promotion 쪽 blocker를 푸는 것이 우선입니다.
                        """
                    )
                    st.markdown("**2. `watchlist -> paper_probation`**")
                    st.markdown(
                        """
                        보통 `promotion`이 `real_money_candidate`까지 올라가야 자연스럽게 이동합니다.
                        """
                    )
                    st.markdown("**3. `paper_probation -> small_capital_trial`**")
                    st.markdown(
                        """
                        이 단계는 조건이 더 엄격합니다.

                        - 현재 기준으로는 non-ETF strict annual family가 유리합니다.
                        - guardrail이 켜져 있어야 합니다.
                        - benchmark가 있어야 합니다.
                        - static universe가 아니어야 합니다.
                        - `Candidate Universe Equal-Weight` benchmark contract까지 맞아야 합니다.
                        """
                    )

            st.warning(
                "실무적으로는 먼저 `Promotion != hold`, `Deployment != blocked`를 만드는 것이 최소 목표입니다."
            )

            with st.container(border=True):
                st.markdown("#### 상태는 어디에서 보나")
                st.caption("`caution`, `unavailable`, `error`, `warning` 같은 상태는 아래 위치에서 직접 확인할 수 있습니다.")
                st.markdown(
                    """
                    - `Validation`: `Real-Money > 검토 근거 > Validation Surface`
                    - `Benchmark Policy`: `Real-Money > 검토 근거 > 세부 정책 기준 보기 > Benchmark Policy`
                    - `Liquidity Policy`: `Real-Money > 실행 부담 > Liquidity Policy`
                    - `Validation Policy`: `Real-Money > 검토 근거 > 세부 정책 기준 보기 > Validation Policy`
                    - `Portfolio Guardrail Policy`: `Real-Money > 검토 근거 > 세부 정책 기준 보기 > Portfolio Guardrail Policy`
                    - `ETF Operability`: `Real-Money > 실행 부담 > ETF 운용 가능성`
                    - `Price Freshness`: 결과 상단 안내 / `Execution Context`
                    """
                )

            with st.container(border=True):
                st.markdown("#### 상태가 뜻하는 바")
                st.caption(
                    "아래 상태는 주로 `Validation`, `Benchmark Policy`, `Liquidity Policy`, "
                    "`Validation Policy`, `Portfolio Guardrail Policy`, `ETF Operability`, `Price Freshness` 같은 항목에서 보입니다."
                )
                status_rows = pd.DataFrame(
                    [
                        {
                            "상태": "Watch",
                            "이 상태의 의미": "지금 바로 승격을 막는다고 단정하긴 어렵지만, 추가 검토가 권장되는 상태입니다.",
                            "자주 나오는 경우": "최근 구간이 조금 흔들리거나, 일부 policy 지표가 기준선 근처에서 약한 경우",
                            "먼저 해볼 일": "해당 섹션의 실제 값과 rationale을 먼저 확인하고, benchmark/기간/계약이 자연스러운지 다시 봅니다.",
                        },
                        {
                            "상태": "Caution",
                            "이 상태의 의미": "현재 승격 판단을 직접 막고 있는 강한 경고 상태입니다.",
                            "자주 나오는 경우": "underperformance share가 높거나, liquidity clean coverage가 낮거나, drawdown gap이 큰 경우",
                            "먼저 해볼 일": "해당 항목의 threshold와 actual 값을 비교해 보고, universe/benchmark/guardrail/유동성 계약을 먼저 재검토합니다.",
                        },
                        {
                            "상태": "Unavailable",
                            "이 상태의 의미": "판단에 필요한 데이터나 계약이 부족해서 지금은 해석 자체를 확정하기 어려운 상태입니다.",
                            "자주 나오는 경우": "benchmark가 없거나, 유동성 필터가 꺼져 있거나, aligned history가 부족한 경우",
                            "먼저 해볼 일": "benchmark 연결, liquidity filter, profile/coverage 데이터처럼 판단 근거를 먼저 채웁니다.",
                        },
                        {
                            "상태": "Warning",
                            "이 상태의 의미": "오류는 아니지만 보수적으로 읽어야 하는 경고 상태입니다.",
                            "자주 나오는 경우": "price freshness가 조금 늦거나, 부분적인 품질 신호가 약한 경우",
                            "먼저 해볼 일": "관련 최신성/품질 값을 먼저 확인한 뒤, 바로 승격보다 재실행 또는 추가 review를 우선합니다.",
                        },
                        {
                            "상태": "Error",
                            "이 상태의 의미": "데이터 또는 계산 오류라서 현재 결과를 신뢰하기 어렵다는 뜻입니다.",
                            "자주 나오는 경우": "freshness 오류, 계산 실패, 필요한 series 부재 같은 경우",
                            "먼저 해볼 일": "데이터 refresh나 실패 원인 해결을 먼저 하고, 그 다음 다시 백테스트합니다.",
                        },
                    ]
                )
                st.dataframe(status_rows, use_container_width=True, hide_index=True)
                st.info(
                    "`Hold 해결 가이드`는 별도 탭이 아니라, "
                    "`Backtest 결과 > Real-Money > 현재 판단 > 전략 승격 판단` 안에서 "
                    "`Promotion Decision = hold`일 때만 함께 보이는 표입니다."
                )

            with st.container(border=True):
                st.markdown("#### 결과 surface는 어디에 있나")
                st.caption("아래 항목들은 이름이 비슷해 보여도 서로 다른 위치와 역할을 가집니다.")
                st.markdown(
                    """
                    - `Hold 해결 가이드`: `Backtest 결과 > Real-Money > 현재 판단 > 전략 승격 판단`
                      `Promotion Decision = hold`일 때만 나타나며, 지금 막는 항목과 바로 해볼 일을 보여줍니다.
                    - `Probation / Monitoring`: `Backtest 결과 > Real-Money > 현재 판단 > Probation / Monitoring`
                      shortlist 이후의 관찰/점검 단계를 보여줍니다.
                    - `최근 구간 / Out-of-Sample Review`: `Backtest 결과 > Real-Money > 검토 근거 > 최근 구간 / Out-of-Sample Review`
                      최근 구간 consistency와 전후반 구간 robustness를 따로 봅니다.
                    - `Deployment Readiness`: `Backtest 결과 > Real-Money > 현재 판단 > Deployment Readiness`
                      실제 배치 직전 checklist 결과를 요약합니다.
                    - `Strategy Highlights`: `Compare 결과 > Strategy Comparison > Strategy Highlights`
                      compare 전용 요약 표면이며, single run의 `Real-Money` 탭과는 다른 위치입니다.
                    """
                )

            with st.container(border=True):
                st.markdown("#### 운영 해석 용어 빠른 연결")
                st.caption("Phase 13 체크리스트에서 자주 보는 용어를 어디서 읽고 어떻게 해석할지 먼저 연결해 둡니다.")
                ops_rows = pd.DataFrame(
                    [
                        {
                            "항목": "Probation",
                            "어디에 보이나": "Real-Money > 현재 판단 > Probation / Monitoring",
                            "짧은 해석": "paper tracking 또는 소액 trial 전 관찰 단계",
                        },
                        {
                            "항목": "Monitoring",
                            "어디에 보이나": "Real-Money > 현재 판단 > Probation / Monitoring",
                            "짧은 해석": "지금 review 강도가 routine인지, heightened인지, breach watch인지 보여줌",
                        },
                        {
                            "항목": "Rolling Review",
                            "어디에 보이나": "Real-Money > 검토 근거 > 최근 구간 / Out-of-Sample Review",
                            "짧은 해석": "최근 구간에서 benchmark 대비 consistency가 어떤지 보여줌",
                        },
                        {
                            "항목": "Out-of-Sample Review",
                            "어디에 보이나": "Real-Money > 검토 근거 > 최근 구간 / Out-of-Sample Review",
                            "짧은 해석": "전후반 구간의 상대 성과가 크게 무너지지 않았는지 봄",
                        },
                        {
                            "항목": "Deployment Readiness",
                            "어디에 보이나": "Real-Money > 현재 판단 > Deployment Readiness",
                            "짧은 해석": "실제 배치 직전 checklist를 pass/watch/fail/unavailable 개수로 요약함",
                        },
                        {
                            "항목": "Strategy Highlights",
                            "어디에 보이나": "Compare 결과 > Strategy Comparison > Strategy Highlights",
                            "짧은 해석": "여러 전략을 한 번에 훑는 compare 전용 요약 표면",
                        },
                    ]
                )
                st.dataframe(ops_rows, use_container_width=True, hide_index=True)

    with st.expander("Real-Money Contract 값 해설", expanded=False):
        st.caption(
            "전략 폼의 `Advanced Inputs > Real-Money Contract`에 보이는 값이 "
            "무엇을 뜻하고, 왜 필요한지, 결과에서 어디에 영향을 주는지 빠르게 정리합니다."
        )
        st.code("Backtest > 전략 선택 > Advanced Inputs > Real-Money Contract", language="text")

        contract_tabs = st.tabs(["공통 입력", "Strict Annual 전용", "ETF 전용", "읽는 순서"])

        with contract_tabs[0]:
            common_rows = pd.DataFrame(
                [
                    {
                        "값": "Minimum Price",
                        "무엇을 뜻하나": "너무 낮은 가격의 종목/ETF를 후보에서 제외하는 최소 가격선",
                        "왜 필요한가": "낮은 가격 자산은 스프레드와 체결 품질이 나쁠 가능성이 커서 실전성이 떨어질 수 있음",
                        "결과에 주는 영향": "해당 값보다 싼 자산은 그 날짜 후보에서 빠지고, 너무 높이면 후보 수가 줄어듦",
                    },
                    {
                        "값": "Transaction Cost (bps)",
                        "무엇을 뜻하나": "리밸런싱 turnover에 곱하는 왕복 거래비용 가정",
                        "왜 필요한가": "gross 성과만 보면 실전 비용이 반영되지 않기 때문",
                        "결과에 주는 영향": "`net` 성과, `Estimated Cost`, `Cumulative Estimated Cost`에 직접 반영됨",
                    },
                    {
                        "값": "Benchmark Ticker",
                        "무엇을 뜻하나": "전략을 비교할 기준 ETF 또는 지수형 ETF",
                        "왜 필요한가": "절대 수익뿐 아니라 기준 대비로도 이 전략을 쓸 이유가 있는지 보기 위해서",
                        "결과에 주는 영향": "`Validation`, `Benchmark Policy`, 일부 guardrail, `Execution Context` 해석의 기준이 됨",
                    },
                ]
            )
            st.dataframe(common_rows, use_container_width=True, hide_index=True)

        with contract_tabs[1]:
            strict_rows = pd.DataFrame(
                [
                    {
                        "값": "Minimum History (Months)",
                        "무엇을 뜻하나": "후보 자산이 최소 몇 개월 가격 이력을 가져야 하는지",
                        "왜 필요한가": "이력이 너무 짧으면 모멘텀/낙폭/benchmark 비교가 불안정해짐",
                        "결과에 주는 영향": "이력이 짧은 자산이 후보에서 빠지고, `History Excluded Count` 같은 해석에 연결됨",
                    },
                    {
                        "값": "Min Avg Dollar Volume 20D ($M)",
                        "무엇을 뜻하나": "최근 20거래일 평균 하루 거래대금의 최소 기준",
                        "왜 필요한가": "거래가 너무 얇은 종목을 실전 후보에서 걸러내기 위해서",
                        "결과에 주는 영향": "`Liquidity Policy`, `Liquidity Clean Coverage`, 유동성 제외 count에 직접 영향",
                    },
                    {
                        "값": "Benchmark Contract",
                        "무엇을 뜻하나": "`SPY` 같은 ticker benchmark로 볼지, 후보군 equal-weight로 볼지 정하는 비교 계약",
                        "왜 필요한가": "무엇과 비교할지에 따라 validation과 승격 해석이 달라지기 때문",
                        "결과에 주는 영향": "`Benchmark Policy`, `Validation`, `Promotion` 해석의 기준 자체를 바꿈",
                    },
                    {
                        "값": "Min Benchmark Coverage / Min Net CAGR Spread",
                        "무엇을 뜻하나": "benchmark와 충분히 겹쳐 비교됐는지, net 기준으로 얼마나 앞서야 하는지 정하는 승격 기준",
                        "왜 필요한가": "benchmark가 있어도 비교 구간이 약하거나 상대 성과가 너무 약하면 굳이 이 전략을 쓸 이유가 약해짐",
                        "결과에 주는 영향": "`Benchmark Policy`가 `normal/watch/caution`으로 갈리는 핵심 기준",
                    },
                    {
                        "값": "Min Liquidity Clean Coverage",
                        "무엇을 뜻하나": "리밸런싱 행 대부분이 유동성 제외 없이 지나가야 한다는 later-pass 기준",
                        "왜 필요한가": "유동성 필터가 켜져 있다는 사실보다, 실제로 얼마나 자주 막히는지가 더 중요하기 때문",
                        "결과에 주는 영향": "`Liquidity Policy`와 `Promotion` 해석에 직접 연결됨",
                    },
                    {
                        "값": "Max Underperformance Share / Min Worst Rolling Excess",
                        "무엇을 뜻하나": "benchmark 대비로 얼마나 자주, 얼마나 크게 밀릴 수 있는지를 제한하는 기준",
                        "왜 필요한가": "전체 CAGR이 좋아도 rolling 구간 consistency가 너무 나쁘면 실전형 승격을 보수적으로 봐야 하기 때문",
                        "결과에 주는 영향": "`Validation Policy`와 repeated `hold`의 핵심 blocker로 자주 작동함",
                    },
                    {
                        "값": "Max Strategy Drawdown / Max Drawdown Gap vs Benchmark",
                        "무엇을 뜻하나": "전략 자체 최대낙폭과 benchmark 대비 낙폭 열세 허용 범위",
                        "왜 필요한가": "수익률이 좋아도 손실 구간이 너무 깊으면 실전 해석이 달라지기 때문",
                        "결과에 주는 영향": "`Portfolio Guardrail Policy`, `Promotion`, `Deployment` 해석에 영향",
                    },
                ]
            )
            st.dataframe(strict_rows, use_container_width=True, hide_index=True)

        with contract_tabs[2]:
            etf_rows = pd.DataFrame(
                [
                    {
                        "값": "Min ETF AUM ($B)",
                        "무엇을 뜻하나": "현재 ETF 운용자산 규모의 최소 기준",
                        "왜 필요한가": "너무 작은 ETF는 거래가 얇거나 상품 안정성이 떨어질 가능성이 높음",
                        "결과에 주는 영향": "`ETF Operability` 상태를 결정하는 핵심 입력 중 하나",
                    },
                    {
                        "값": "Max Bid-Ask Spread (%)",
                        "무엇을 뜻하나": "현재 호가 스프레드의 최대 허용치",
                        "왜 필요한가": "spread가 넓으면 실제 체결 비용이 커져 백테스트보다 실전 성과가 나빠질 수 있음",
                        "결과에 주는 영향": "`ETF Operability`와 `Promotion` 해석에 직접 반영됨",
                    },
                    {
                        "값": "ETF Real-Money Contract 전체",
                        "무엇을 뜻하나": "가격/비용/benchmark/current operability를 함께 읽는 ETF 전용 계약",
                        "왜 필요한가": "ETF 전략은 수익률뿐 아니라 현재 상품 규모와 거래 상태까지 같이 봐야 하기 때문",
                        "결과에 주는 영향": "`실행 부담 > ETF 운용 가능성`, `Execution Context`, `Promotion`에서 같이 읽힘",
                    },
                ]
            )
            st.dataframe(etf_rows, use_container_width=True, hide_index=True)

        with contract_tabs[3]:
            st.markdown(
                """
                1. **먼저 investability filter부터 읽습니다.**
                - `Minimum Price`, `Minimum History`, `Min Avg Dollar Volume 20D`는
                  "후보 자산이 애초에 실전형 후보로 들어올 수 있나?"를 정하는 1차 필터입니다.

                2. **그 다음 benchmark 계약을 읽습니다.**
                - `Benchmark Ticker`, `Benchmark Contract`, `Min Benchmark Coverage`, `Min Net CAGR Spread`는
                  "무엇과 비교하고, 어느 정도는 이겨야 하는가?"를 정합니다.

                3. **그 다음 robustness / guardrail 기준을 읽습니다.**
                - `Max Underperformance Share`, `Min Worst Rolling Excess`,
                  `Max Strategy Drawdown`, `Max Drawdown Gap vs Benchmark`는
                  "좋아 보여도 너무 흔들리면 보수적으로 본다"는 later-pass 승격 기준입니다.

                4. **ETF 전략이면 current operability를 따로 읽습니다.**
                - `Min ETF AUM`, `Max Bid-Ask Spread`는
                  "지금 이 ETF를 실제로 쓰기 무난한가?"를 보는 현재 시점 기준입니다.

                5. **실행 후에는 아래 순서로 결과를 다시 봅니다.**
                - `Real-Money > 실행 부담`
                - `Real-Money > 검토 근거`
                - `Real-Money > 현재 판단`

                `Real-Money Contract`는 raw 성과를 직접 바꾸는 값과
                승격/배치 해석을 바꾸는 값이 섞여 있습니다.
                예를 들어 `Transaction Cost`는 `net` 성과를 바꾸고,
                benchmark / policy threshold는 주로 `Promotion`, `Shortlist`, `Deployment` 해석을 바꿉니다.
                """
            )
            st.info(
                "값이 많아 보여도 읽는 순서는 단순합니다. "
                "`후보 진입 조건 -> benchmark 비교 계약 -> robustness 기준 -> ETF operability -> 실행 후 Real-Money 해석` 순서로 보면 됩니다."
            )

    with st.expander("GTAA Risk-Off 후보군 보는 법", expanded=False):
        st.caption(
            "`Risk-Off Contract`는 GTAA가 점수로 고른 ETF를 그대로 보유할지, "
            "추세가 약한 자리는 현금이나 방어 ETF로 비울지 정하는 실행 규칙입니다."
        )
        st.code(
            "Backtest > Single Strategy > GTAA > Advanced Inputs > Risk-Off Overlay > Risk-Off Contract",
            language="text",
        )
        st.info(
            "`Defensive Tickers`에 적은 ETF가 자동으로 새 후보군에 추가되는 것은 아닙니다. "
            "현재 구현에서는 GTAA universe 안에도 들어 있는 defensive ticker만 실제 대체 후보로 사용할 수 있습니다."
        )

        risk_off_rows = pd.DataFrame(
            [
                {
                    "입력 / 개념": "GTAA Tickers",
                    "무엇을 뜻하나": "GTAA가 점수를 매기고 실제 가격 데이터를 읽는 기본 후보군",
                    "확인할 점": "방어 ETF를 실제 fallback 후보로 쓰려면 이 universe에도 포함되어 있어야 합니다.",
                },
                {
                    "입력 / 개념": "Top Assets",
                    "무엇을 뜻하나": "리밸런싱 때 점수 상위 몇 개 슬롯을 만들지 정하는 값",
                    "확인할 점": "`Top=2`면 최종 슬롯은 2개이며, 통과한 슬롯은 기본적으로 50%씩 들어갑니다.",
                },
                {
                    "입력 / 개념": "Trend Filter Window",
                    "무엇을 뜻하나": "선택 후보가 이동평균선 위에 있는지 보는 추세 필터",
                    "확인할 점": "`200`이면 `Close >= MA200`인 ETF만 최종 후보로 남습니다.",
                },
                {
                    "입력 / 개념": "Fallback Mode",
                    "무엇을 뜻하나": "빈 슬롯이나 위험구간에서 현금만 둘지, 방어 ETF를 먼저 찾을지 정하는 값",
                    "확인할 점": "`Defensive Bond Preference`면 usable defensive ticker를 먼저 찾고, 없으면 현금으로 남깁니다.",
                },
                {
                    "입력 / 개념": "Defensive Tickers",
                    "무엇을 뜻하나": "fallback 때 우선 검토할 방어 ETF 목록",
                    "확인할 점": "이 목록과 GTAA universe의 교집합만 실제 fallback 후보가 됩니다.",
                },
            ]
        )
        st.dataframe(risk_off_rows, use_container_width=True, hide_index=True)

        risk_off_tabs = st.tabs(["읽는 순서", "이번 GTAA 예시", "결과에서 확인할 곳"])
        with risk_off_tabs[0]:
            st.markdown(
                """
                1. **먼저 GTAA universe를 봅니다.**
                - 이 목록이 실제 점수 계산과 가격 로딩의 후보군입니다.

                2. **Defensive Tickers와 universe의 교집합을 봅니다.**
                - `Defensive Tickers`에 있어도 universe에 없으면 현재 run에서는 실제 대체 후보가 아닙니다.

                3. **점수 상위 `Top Assets`를 고릅니다.**
                - 예를 들어 `Top=2`면 우선 점수 상위 2개 ETF를 고릅니다.

                4. **Trend Filter를 적용합니다.**
                - `Trend Filter Window=200`이면 `Close >= MA200`인 후보만 통과합니다.

                5. **빈 슬롯을 채웁니다.**
                - `Fallback Mode=Cash Only`면 빈 슬롯은 현금입니다.
                - `Fallback Mode=Defensive Bond Preference`면 usable defensive ticker 중 `Close >= MA200`인 후보를 먼저 넣고,
                  그래도 남는 슬롯은 현금으로 둡니다.

                6. **비중을 읽습니다.**
                - 현재 GTAA 구현은 `Top Assets` 슬롯 기준으로 균등 배분합니다.
                - `Top=2`에서 최종 후보가 2개면 `50% / 50%`, 최종 후보가 1개면 `50% / 현금 50%`,
                  최종 후보가 없으면 `현금 100%`로 읽습니다.
                """
            )

        with risk_off_tabs[1]:
            example_rows = pd.DataFrame(
                [
                    {
                        "항목": "GTAA Tickers",
                        "값": "SPY, QQQ, GLD, IEF",
                        "해석": "이번 run에서 실제 점수 계산과 fallback 검토가 가능한 universe",
                    },
                    {
                        "항목": "Defensive Tickers",
                        "값": "TLT, IEF, LQD, BIL",
                        "해석": "방어 후보로 적은 목록",
                    },
                    {
                        "항목": "실제 usable defensive 후보",
                        "값": "IEF",
                        "해석": "두 목록의 교집합이 IEF뿐이므로 현재 run에서는 IEF만 실제 방어 대체 후보",
                    },
                    {
                        "항목": "Top Assets",
                        "값": "2",
                        "해석": "최종 후보 2개가 통과하면 각각 50%씩, 1개만 통과하면 나머지 50%는 현금",
                    },
                ]
            )
            st.dataframe(example_rows, use_container_width=True, hide_index=True)
            st.warning(
                "`TLT`, `LQD`, `BIL`도 실제 방어 후보로 쓰고 싶다면 "
                "GTAA Tickers에도 함께 넣어야 합니다. Defensive Tickers 입력만으로는 universe가 확장되지 않습니다."
            )

        with risk_off_tabs[2]:
            result_rows = pd.DataFrame(
                [
                    {
                        "결과 항목": "Raw Selected Ticker",
                        "무엇을 보나": "점수 기준으로 먼저 뽑힌 Top 후보",
                    },
                    {
                        "결과 항목": "Overlay Rejected Ticker",
                        "무엇을 보나": "Trend Filter 또는 가격 조건 때문에 탈락한 후보",
                    },
                    {
                        "결과 항목": "Defensive Fallback Ticker",
                        "무엇을 보나": "빈 슬롯을 채우기 위해 실제로 들어간 방어 후보",
                    },
                    {
                        "결과 항목": "Next Ticker",
                        "무엇을 보나": "다음 리밸런싱 구간에 들고 갈 최종 후보",
                    },
                    {
                        "결과 항목": "Cash",
                        "무엇을 보나": "채워지지 않은 슬롯이 현금으로 남은 금액",
                    },
                ]
            )
            st.dataframe(result_rows, use_container_width=True, hide_index=True)
            st.caption(
                "`Risk-Off Contract`는 전략의 보유 후보와 현금 비중을 바꾸는 실행 규칙이고, "
                "`Real-Money Contract`는 거래비용, benchmark, ETF AUM, spread 같은 실전 검토 기준입니다."
            )

    with st.expander("Interval / Rebalance Interval 읽는 법", expanded=False):
        st.caption(
            "`option=month_end`로 실행할 때 interval 숫자는 주 단위가 아니라 "
            "월말 데이터 row를 몇 개마다 사용할지 정하는 값입니다."
        )
        interval_rows = pd.DataFrame(
            [
                {
                    "입력값": "`1`",
                    "month_end 기준 의미": "매월 리밸런싱 / 매월 신호 갱신",
                    "헷갈리기 쉬운 표현": "대략 4주마다로 볼 수 있음",
                },
                {
                    "입력값": "`4`",
                    "month_end 기준 의미": "4번째 월말 row마다 리밸런싱 / 신호 갱신",
                    "헷갈리기 쉬운 표현": "4주가 아니라 대략 4개월 cadence",
                },
                {
                    "입력값": "`12`",
                    "month_end 기준 의미": "12번째 월말 row마다 리밸런싱",
                    "헷갈리기 쉬운 표현": "연 1회 cadence",
                },
            ]
        )
        st.dataframe(interval_rows, use_container_width=True, hide_index=True)
        st.info(
            "따라서 `SPY, QQQ, GLD, IEF` Equal Weight를 4주/월간 리밸런싱으로 보려면 "
            "`Rebalance Interval = 1`을 사용합니다. "
            "기존 GTAA 실습 후보의 `Interval = 4`는 후보 계약을 맞춘 값이지 4주 리밸런싱이 아닙니다."
        )

    with st.expander("Compare 대상 선정법", expanded=False):
        st.caption(
            "5단계 Compare는 아무 전략과 비교하는 절차가 아니라, "
            "현재 후보가 비교할 만한 기준 앞에서도 남길 이유가 있는지 확인하는 단계입니다."
        )
        comparator_rows = pd.DataFrame(
            [
                {
                    "비교 대상 역할": "Naive baseline",
                    "무엇을 확인하나": "복잡한 전략을 쓸 이유가 있는지",
                    "예시": "같은 universe Equal Weight",
                },
                {
                    "비교 대상 역할": "Market benchmark",
                    "무엇을 확인하나": "단순 시장 노출보다 나은지",
                    "예시": "SPY, 60/40, AGG / BIL 조합",
                },
                {
                    "비교 대상 역할": "가까운 대안 전략",
                    "무엇을 확인하나": "비슷한 목적의 다른 방식보다 나은지",
                    "예시": "GTAA vs Global Relative Strength",
                },
                {
                    "비교 대상 역할": "위험 기준 대안",
                    "무엇을 확인하나": "수익과 낙폭 / 변동성의 교환이 납득되는지",
                    "예시": "Risk Parity Trend, 방어형 allocation",
                },
                {
                    "비교 대상 역할": "기존 강한 후보",
                    "무엇을 확인하나": "이미 남아 있는 후보보다 새 후보를 추가할 이유가 있는지",
                    "예시": "Current Candidate Registry의 active 후보",
                },
            ]
        )
        st.dataframe(comparator_rows, use_container_width=True, hide_index=True)
        st.markdown(
            """
            **좋은 비교군의 조건**

            - 같은 투자 문제를 풀어야 합니다.
            - 기간, timeframe, option은 먼저 맞춥니다.
            - universe, cadence, 거래비용, risk-off 조건이 다르면 그 차이를 Review Note에 남깁니다.
            - 일부러 약한 strawman만 두지 않습니다.
            - 최소 하나는 단순하고 강한 기준이어야 합니다.
            """
        )
        st.info(
            "GTAA 실습에서는 같은 universe Equal Weight, 가까운 momentum 대안인 Global Relative Strength, "
            "위험 기준 대안인 Risk Parity Trend를 함께 두면 비교 의미가 살아납니다."
        )
        st.markdown("**상황 예시: GTAA Balanced Top-2를 5단계에서 비교한다면**")
        gtaa_example_rows = pd.DataFrame(
            [
                {
                    "비교 대상": "Equal Weight Same Universe",
                    "설정 예": "`SPY, QQQ, GLD, IEF`, 후보와 같은 cadence",
                    "왜 비교하나": "같은 ETF를 그냥 균등 보유하는 것보다 GTAA를 쓸 이유가 있는지 확인",
                    "통과 해석": "수익 / End Balance가 우위이고 MDD도 과도하게 나빠지지 않으면 기본 근거가 생김",
                },
                {
                    "비교 대상": "Global Relative Strength",
                    "설정 예": "`SPY, QQQ, GLD, IEF`, Top 2, 같은 score horizon",
                    "왜 비교하나": "비슷한 momentum ETF 전략보다 GTAA 구조가 나은지 확인",
                    "통과 해석": "성과가 더 좋거나, 성과가 비슷해도 낙폭 / 안정성이 더 납득되면 근거가 생김",
                },
                {
                    "비교 대상": "Risk Parity Trend",
                    "설정 예": "기본 Risk Parity universe, 후보와 같은 cadence",
                    "왜 비교하나": "위험 균형형 접근보다 GTAA의 수익 / 낙폭 교환이 납득되는지 확인",
                    "통과 해석": "MDD가 더 크더라도 수익 보상이 충분하거나, MDD도 함께 우위면 강한 근거",
                },
                {
                    "비교 대상": "SPY 또는 60/40",
                    "설정 예": "단순 market benchmark 또는 주식/채권 혼합 benchmark",
                    "왜 비교하나": "아주 단순한 시장 노출보다 전략을 운영할 이유가 있는지 확인",
                    "통과 해석": "복잡한 tactical 전략을 쓸 만큼 risk-adjusted 근거가 설명되어야 함",
                },
            ]
        )
        st.dataframe(gtaa_example_rows, use_container_width=True, hide_index=True)
        st.caption(
            "이 예시에서 비교 대상 하나만 이기는 것이 목표가 아닙니다. "
            "각 비교 대상 앞에서 후보의 역할을 말할 수 있어야 6단계 Candidate Packaging으로 넘길 근거가 생깁니다."
        )

    with st.expander("Portfolio Proposal -> Final Review -> 최종 판단 완료", expanded=False):
        st.caption(
            "Phase35 보정 이후 현재 active workflow는 별도 Post-Selection Guide 없이 "
            "`Portfolio Proposal -> Final Review -> 최종 판단 완료`에서 끝납니다."
        )
        final_flow_rows = pd.DataFrame(
            [
                {
                    "구간": "Portfolio Proposal",
                    "하는 일": "단일 후보는 추가 proposal 저장 없이 Final Review 입력 후보로 읽고, 여러 후보는 목적 / 역할 / 비중이 있는 proposal draft로 묶습니다.",
                    "통과 후 의미": "검증과 최종 판단으로 넘길 후보 형태가 준비됨",
                },
                {
                    "구간": "Final Review 검증",
                    "하는 일": "Validation, Robustness, Stress / Sensitivity, Paper Observation 기준을 한 화면에서 확인합니다.",
                    "통과 후 의미": "최종 판단을 기록해도 되는 근거가 모였는지 확인됨",
                },
                {
                    "구간": "Final Review 최종 판단",
                    "하는 일": "실전 후보로 선정 / 보류 / 거절 / 재검토 중 하나를 이유와 함께 기록합니다.",
                    "통과 후 의미": "사용자가 마지막으로 확인할 최종 판단 원본이 저장됨",
                },
                {
                    "구간": "기록된 최종 검토 결과 확인",
                    "하는 일": "저장된 final decision을 다시 열어 투자 가능 후보인지, 관찰이 더 필요한지, 투자하면 안 되는지 확인합니다.",
                    "통과 후 의미": "실전 후보 선정 여부가 확인됨",
                },
            ]
        )
        st.dataframe(final_flow_rows, use_container_width=True, hide_index=True)

        route_rows = pd.DataFrame(
            [
                {
                    "Final Review 판단": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "화면에서 읽을 말": "실전 후보로 선정",
                    "의미": "현재 근거 기준으로 실전 후보군에 올릴 수 있다는 판단",
                },
                {
                    "Final Review 판단": "HOLD_FOR_MORE_PAPER_TRACKING",
                    "화면에서 읽을 말": "내용 부족 / 관찰 필요",
                    "의미": "당장 선정하기에는 paper observation이나 근거가 더 필요함",
                },
                {
                    "Final Review 판단": "REJECT_FOR_PRACTICAL_USE",
                    "화면에서 읽을 말": "투자하면 안 됨",
                    "의미": "현재 근거로는 실전 후보에서 제외해야 함",
                },
                {
                    "Final Review 판단": "RE_REVIEW_REQUIRED",
                    "화면에서 읽을 말": "재검토 필요",
                    "의미": "조건 / 데이터 / 구성 변경 후 다시 검토해야 함",
                },
            ]
        )
        st.dataframe(route_rows, use_container_width=True, hide_index=True)
        st.warning(
            "`실전 후보로 선정`은 live approval, broker order, 자동매매 지시가 아닙니다. "
            "이 프로그램의 현재 최종 지점은 투자 후보 선정 여부 확인입니다."
        )

    st.markdown("### 1~10 단계 실행 흐름")

    with st.container(border=True):
        st.markdown("### 테스트에서 상용화 후보 검토까지 사용하는 흐름")
        st.caption(
            "이 프로그램은 단순 백테스트 숫자 확인을 넘어서, "
            "실전 후보를 어떻게 좁히고 어떤 단계에서 멈춰야 하는지까지 읽는 데 초점을 둡니다."
        )
        st.warning(
            "여기서 말하는 `상용화`는 곧바로 큰 자금을 live로 넣는다는 뜻이 아니라, "
            "`실전 후보 검토 -> paper probation -> 소액 trial`까지 이어지는 운영 흐름을 말합니다."
        )
        st.info(
            "`Real-Money`는 개별 백테스트 실행에 붙는 **검증 신호**입니다. "
            "거래비용, benchmark, drawdown, ETF 운용 가능성 같은 위험 신호를 보여줍니다. "
            "반면 `Candidate Review`와 `Pre-Live 운영 점검`은 그 신호를 보고 "
            "후보로 남길지, 비교할지, paper tracking / watchlist / 보류 / 재검토로 둘지 정하는 **별도 운영 절차**입니다."
        )
        st.caption(
            "큰 흐름으로는 1-5단계가 데이터 / 백테스트 / 비교 구간, 6단계가 후보 패키징 구간, "
            "7단계가 Portfolio Proposal 구성 구간, 8-10단계가 Final Review 검증과 최종 판단 확인 구간입니다."
        )

        step_rows = [
            {
                "title": "1단계. 데이터 최신화부터 시작",
                "path": "Ingestion",
                "goal": "가격, 재무제표, factor, profile 같은 기본 데이터를 먼저 최신 상태로 맞춥니다.",
                "check": [
                    "`Daily Market Update`로 가격 최신화",
                    "필요하면 statement / factor refresh 실행",
                    "`Price Freshness`가 warning/error가 아닌지 확인",
                ],
                "next_step": "데이터 최신화가 끝나면 single backtest로 전략 하나를 먼저 읽습니다.",
            },
            {
                "title": "2단계. Single Strategy로 전략 하나를 먼저 읽기",
                "path": "Backtest > Single Strategy",
                "goal": "전략 하나의 기본 성과, 계약, data trust, meta를 먼저 이해합니다.",
                "check": [
                    "`Summary`, `Equity Curve`, `Data Trust Summary`, `Execution Context`를 먼저 확인",
                    "필요한 universe / factor / overlay / real-money contract를 입력",
                    "single run 기준으로 숫자와 meta가 자연스러운지 확인",
                ],
                "next_step": "single run이 이상 없으면 `Real-Money` 탭으로 내려가 운영 해석을 시작합니다.",
            },
            {
                "title": "3단계. Real-Money 검증 신호 확인",
                "path": "Backtest 결과 > Real-Money",
                "goal": "개별 백테스트 결과에 붙은 실전 검토 신호를 읽습니다. 이 단계는 투자 실행 승인이 아니라 위험/검증 신호 확인입니다.",
                "check": [
                    "`현재 판단`: Promotion / Shortlist / Probation / Deployment 확인",
                    "`검토 근거`: Validation / Benchmark / Rolling / OOS 확인",
                    "`실행 부담`: Liquidity / ETF Operability / Guardrail 상태 확인",
                ],
                "next_step": "`Promotion != hold`, `Deployment != blocked`여도 바로 투자하지 않고, 이후 Pre-Live 운영 점검으로 넘길 수 있는지만 봅니다.",
            },
            {
                "title": "4단계. Hold면 먼저 막히는 항목 해결",
                "path": "Real-Money > 현재 판단 > 전략 승격 판단 > Hold 해결 가이드",
                "goal": "왜 막혔는지 추측하지 말고, 실제 blocker와 화면 위치를 보고 해결합니다.",
                "check": [
                    "`항목 / 현재 상태 / 상태를 보는 위치 / 바로 해볼 일` 확인",
                    "`caution / unavailable / error` 항목부터 먼저 정리",
                    "필요하면 `검토 근거`와 `실행 부담`으로 바로 이동해서 실제 값을 비교",
                ],
                "next_step": "hold를 벗긴 뒤 다시 실행해서 promotion과 shortlist가 올라가는지 확인합니다.",
            },
            {
                "title": "5단계. Compare로 후보를 서로 비교",
                "path": "Backtest > Compare & Portfolio Builder",
                "goal": "여러 전략이나 registry 후보를 한 번에 놓고 shortlist / deployment / data trust 상태를 비교합니다.",
                "check": [
                    "`Strategy Highlights`에서 전략별 상태를 한 줄씩 비교",
                    "`Data Trust`에서 결과 기간과 가격 최신성 차이 확인",
                    "`Focused Strategy > Real-Money Contract`로 한 전략씩 깊게 읽기",
                    "`Candidate Review > 보조 도구: Send Candidates To Compare`에서 보낸 후보 묶음이 의도대로 채워졌는지 확인",
                ],
                "next_step": "여기서 후보를 좁힌 뒤, 좋은 run이나 비교할 만한 run은 Candidate Packaging으로 넘겨 운영 기록과 Proposal 진입 준비를 합니다.",
            },
            {
                "title": "6단계. Candidate Packaging으로 운영 기록과 Proposal 진입 준비",
                "path": "Backtest > Candidate Review > 6단계 Candidate Packaging Flow",
                "goal": "좋아 보이는 결과를 바로 다음 단계로 보내지 않고, Review Note와 registry row, Pre-Live 운영 기록으로 남긴 뒤 Portfolio Proposal이 읽을 수 있는 후보 패키지인지 확인합니다.",
                "check": [
                    "`Review As Candidate Draft`로 `Candidate Review > 1. Draft 확인 / Review Note 저장` 이동",
                    "후보 이름 / source / result snapshot / Data Trust / Real-Money signal / settings snapshot 확인",
                    "`Candidate Packaging 저장 준비`에서 Review Note 저장 가능 여부 확인",
                    "`Review Decision`, `Operator Reason`, `Next Action` 작성",
                    "`Save Candidate Review Note` 클릭",
                    "`2. Registry 저장`에서 Current / Near Miss / Scenario / Stop 범위 확인",
                    "`Registry ID`, `Record Type`, `Strategy Family`, `Candidate Role` 확인",
                    "같은 Review Note가 이미 registry에 저장되어 있는지 확인",
                    "`Append To Current Candidate Registry`가 자동 승격이 아니라 명시적 저장인지 확인",
                    "`3. 운영 기록 저장 및 Portfolio Proposal 이동`에서 방금 저장한 후보가 선택되었는지 확인",
                    "`선택 후보 확인`에서 Route가 `PRE_LIVE_READY`인지 확인",
                    "`운영 기록 저장 및 다음 단계 판단`에서 운영 상태 / 이유 / 다음 행동 / 점검일 작성",
                    "`Save Pre-Live Record` 저장 후 `Open Portfolio Proposal` 활성화 여부 확인",
                    "`COMPARE_REVIEW_READY`이면 Compare Picker에서 비교할 후보를 추가해 다시 비교",
                ],
                "next_step": "`PORTFOLIO_PROPOSAL_READY`인 후보만 Portfolio Proposal로 넘깁니다. `COMPARE_REVIEW_READY`는 실패가 아니라 Compare 재검토 경로입니다.",
            },
            {
                "title": "7단계. 단일 후보 직행 평가 또는 Portfolio Proposal 초안 작성",
                "path": "Backtest > Portfolio Proposal",
                "goal": "Candidate Review를 통과한 후보가 1개면 저장을 반복하지 않고 Final Review 입력 후보로 읽습니다. 여러 후보를 묶을 때만 목적, 역할, 비중, capital scope가 있는 포트폴리오 초안으로 저장합니다.",
                "check": [
                    "`Candidate Review > Open Portfolio Proposal`로 넘어온 후보가 component 선택에 들어왔는지 확인",
                    "후보가 1개면 `단일 후보 직행 평가`를 먼저 사용하고, `Proposal Draft 저장 불필요`로 표시되는지 확인",
                    "후보가 2개 이상이면 `포트폴리오 초안 작성` 경로에서 후보별 proposal role, target weight, 비중 근거를 작성",
                    "`Live Readiness 직행 평가` 또는 `Live Readiness 진입 평가`는 현재 흐름에서 Final Review 입력 준비 상태로 읽고 route, readiness score, blocker를 확인",
                    "다중 후보 proposal draft를 저장했다면 저장 목록에서 다시 열 수 있는지 확인",
                ],
                "next_step": "단일 후보 직행 평가나 다중 후보 proposal 초안 모두 투자 승인이 아닙니다. 실제 실전 후보 선정 여부는 Final Review에서 검증하고 판단합니다.",
            },
            {
                "title": "8단계. Final Review에서 검증 근거와 관찰 기준 확인",
                "path": "Backtest > Final Review > 1~4. 최종 검토 대상 / 검증 근거 / Robustness / Paper Observation",
                "goal": "단일 후보나 저장된 proposal을 최종 검토 대상으로 선택하고, validation / robustness / paper observation 기준이 최종 판단을 기록할 만큼 충분한지 확인합니다.",
                "check": [
                    "`1. 최종 검토 대상 선택`에서 current candidate 또는 saved proposal을 선택",
                    "`2. Portfolio Risk / Validation Pack`에서 route, score, blocker, component risk 확인",
                    "`3. Robustness / Stress Validation Preview`에서 기간 / benchmark / drawdown / stress readiness 확인",
                    "`4. Paper Observation`에서 paper tracking 관찰 조건과 남은 보강 항목 확인",
                    "preview를 여는 것만으로 proposal draft 저장이나 live approval이 자동 수행되지 않는지 확인",
                ],
                "next_step": "hard blocker가 없고 검증 근거가 충분하면 9단계 최종 판단 및 테스트 검증으로 넘어갑니다.",
            },
            {
                "title": "9단계. 최종 판단 및 테스트 검증 기록",
                "path": "Backtest > Final Review > 5. 최종 판단 및 테스트 검증",
                "goal": "실전 후보로 선정할지, 관찰을 더 할지, 거절할지, 재검토할지를 사람의 이유와 함께 하나의 최종 검토 결과로 기록합니다.",
                "check": [
                    "`Final Decision Route`가 의도한 판단인지 확인",
                    "`Operator Reason`, `Constraints`, `Next Action`을 비워 두지 않음",
                    "`Record Route`가 `FINAL_REVIEW_RECORD_READY`인지 확인",
                    "`최종 검토 결과 기록` 버튼이 live approval이나 주문 지시가 아님을 확인",
                    "저장 후 기존 candidate / proposal registry를 덮어쓰지 않는지 확인",
                ],
                "next_step": "저장된 최종 판단은 10단계에서 다시 열어 실전 후보 선정 여부를 확인합니다.",
            },
            {
                "title": "10단계. 기록된 최종 검토 결과로 실전 후보 선정 여부 확인",
                "path": "Backtest > Final Review > 6. 기록된 최종 검토 결과 확인",
                "goal": "저장된 final decision을 다시 열어 이 포트폴리오가 실전 후보로 선정되었는지, 아직 보류인지, 제외인지, 재검토인지 최종 확인합니다.",
                "check": [
                    "`투자 가능성`이 `실전 후보로 선정`, `내용 부족 / 관찰 필요`, `투자하면 안 됨`, `재검토 필요` 중 무엇인지 확인",
                    "`Final Review Status`가 현재 흐름의 최종 판단 완료 문구로 읽히는지 확인",
                    "source candidate / proposal과 target components / weights가 저장 당시 조건과 맞는지 확인",
                    "`live_approval=false`, `order_instruction=false` 경계가 유지되는지 확인",
                    "선정된 경우에도 실제 주문 전에는 투입 금액, 리밸런싱, 모니터링, stop / re-review 기준을 별도 운영 판단으로 정리해야 함을 확인",
                ],
                "next_step": "`SELECT_FOR_PRACTICAL_PORTFOLIO`이면 이 프로그램 기준 실전 후보로 선정된 것입니다. 다만 이 결과는 주문 실행이나 자동 승인과는 분리됩니다.",
            },
        ]

        for row in step_rows:
            with st.expander(row["title"], expanded=row["title"].startswith("1단계")):
                st.caption(f"위치: {row['path']}")
                st.markdown(f"**무엇을 하는 단계인가**  \n{row['goal']}")
                st.markdown("**이 단계에서 볼 것**")
                for item in row["check"]:
                    st.markdown(f"- {item}")
                st.info(row["next_step"])

    with st.container(border=True):
        st.markdown("### 단계 통과 기준")
        st.caption(
            "아래 기준은 단계형 Guide 중간에 끼워 넣지 않고, "
            "각 단계에서 멈출지 다음 단계로 갈지 판단할 때 따로 보는 기준입니다."
        )

        with st.expander("4단계에서 5단계로 넘어가는 최소 기준", expanded=True):
            st.caption(
                "이 기준은 투자 승인 기준이 아니라, `Hold 해결`을 마치고 "
                "`Compare`에서 다른 후보와 비교해 볼 수 있는지 판단하는 기준입니다."
            )
            pass_rows = pd.DataFrame(
                [
                    {
                        "확인 항목": "Promotion Decision",
                        "5단계 진행 가능": "`real_money_candidate` 또는 `production_candidate`처럼 `hold`가 아닌 상태",
                        "멈춰야 하는 경우": "`hold`이면 Hold 해결 가이드의 blocker를 먼저 봅니다.",
                    },
                    {
                        "확인 항목": "Deployment Readiness / Deployment Status",
                        "5단계 진행 가능": "`paper_only`, `watchlist_only`, `review_required`처럼 `blocked`가 아닌 상태",
                        "멈춰야 하는 경우": "`blocked`이면 deployment checklist와 blocker를 먼저 확인합니다.",
                    },
                    {
                        "확인 항목": "Hold 해결 가이드 / Blocker",
                        "5단계 진행 가능": "핵심 blocker가 없거나, 남은 항목을 알고 Compare에서 더 검토하기로 정리한 상태",
                        "멈춰야 하는 경우": "데이터 오류, benchmark 부재, ETF operability caution처럼 승격을 직접 막는 blocker가 남은 상태",
                    },
                ]
            )
            st.dataframe(pass_rows, use_container_width=True, hide_index=True)
            st.success(
                "`Promotion Decision != hold`, `Deployment != blocked`, 핵심 blocker 없음이면 "
                "4단계는 pass로 보고 5단계 Compare로 넘어갈 수 있습니다."
            )
            st.warning(
                "`real_money_candidate`는 다음 단계로 넘길 수 있다는 강한 신호일 뿐, "
                "live trading 승인이나 주문 지시가 아닙니다."
            )

        with st.expander("5단계에서 6단계로 넘어가는 최소 기준", expanded=True):
            st.caption(
                "이 기준은 `Compare` 결과를 보고 선택 후보를 `Candidate Packaging`으로 넘겨도 되는지 판단하는 기준입니다. "
                "후보 registry 저장이나 투자 승인이 아니라, 운영 기록과 Proposal 진입 준비 단계로 보낼 수 있는지 보는 진입 조건입니다."
            )
            draft_rows = pd.DataFrame(
                [
                    {
                        "확인 항목": "Compare Run",
                        "6단계 진행 가능": "2개 이상 전략이 같은 기간 / 같은 option으로 정상 비교됨",
                        "멈춰야 하는 경우": "비교 전략이 1개뿐이거나 실행 오류 / 빈 결과가 있음",
                    },
                    {
                        "확인 항목": "Data Trust",
                        "6단계 진행 가능": "선택 후보의 Data Trust가 `OK` 또는 Review Note에 남길 수 있는 `WARNING` 상태",
                        "멈춰야 하는 경우": "가격 최신성 error, 결과 기간이 크게 비는 경우처럼 Data Trust가 `BLOCKED` 상태",
                    },
                    {
                        "확인 항목": "Real-Money Gate",
                        "6단계 진행 가능": "`Promotion != hold`, `Deployment != blocked`, 핵심 blocker 없음",
                        "멈춰야 하는 경우": "4단계 blocker가 다시 나타나거나 Real-Money signal이 비어 있음",
                    },
                    {
                        "확인 항목": "Relative Evidence",
                        "6단계 진행 가능": "CAGR, End Balance, MDD, Sharpe 중 최소 하나 이상의 설명 가능한 상대 근거가 있음",
                        "멈춰야 하는 경우": "선택 후보가 성과와 낙폭 모두 비교군 최하위이고 설명할 역할이 없음",
                    },
                ]
            )
            st.dataframe(draft_rows, use_container_width=True, hide_index=True)
            st.success(
                "`Compare 정상 실행`, `Data Trust 해석 가능`, `Real-Money blocker 없음`, "
                "상대 비교 근거가 있으면 6단계 Candidate Packaging으로 넘길 수 있습니다."
            )
            st.warning(
                "Data Trust warning은 Draft Score를 강제로 cap하지 않고 별도 gate로 표시합니다. "
                "6단계 진입은 후보 패키징 초안으로 보내는 것일 뿐, current candidate registry 저장이나 Pre-Live 운영 record 저장과는 분리됩니다."
            )

        with st.expander("6단계 Candidate Packaging에서 7단계 Portfolio Proposal로 넘어가는 최소 기준", expanded=True):
            st.caption(
                "이 기준은 Draft 확인, Review Note 저장, registry 저장, Pre-Live 운영 기록, Proposal 진입 평가를 하나의 Candidate Packaging 단계로 묶어 봅니다. "
                "`PORTFOLIO_PROPOSAL_READY`인 후보만 다음 단계인 Portfolio Proposal로 넘어갑니다."
            )
            packaging_rows = pd.DataFrame(
                [
                    {
                        "확인 항목": "후보 식별 / Source",
                        "Portfolio Proposal 진행 가능": "후보 이름 또는 strategy key와 source가 확인됨",
                        "멈춰야 하는 경우": "어떤 실행 결과에서 온 초안인지 식별할 수 없음",
                    },
                    {
                        "확인 항목": "Result Snapshot",
                        "Portfolio Proposal 진행 가능": "CAGR, MDD, End Balance 같은 핵심 결과 snapshot이 Review Note와 registry row에 남아 있음",
                        "멈춰야 하는 경우": "성과 snapshot이 비어 있어 다음 사람이 판단 근거를 재현하기 어려움",
                    },
                    {
                        "확인 항목": "Data Trust / Real-Money / Settings",
                        "Portfolio Proposal 진행 가능": "Data Trust가 OK 또는 설명 가능한 warning이고, Real-Money signal과 설정 snapshot이 남아 있음",
                        "멈춰야 하는 경우": "Data Trust error, Real-Money signal 공백, universe / ticker / cadence 정보 부족",
                    },
                    {
                        "확인 항목": "Operator Reason / Next Action",
                        "Portfolio Proposal 진행 가능": "왜 이 판단을 남기는지와 다음 행동이 작성됨",
                        "멈춰야 하는 경우": "저장 버튼만 누르고 사람이 판단한 이유가 남지 않음",
                    },
                    {
                        "확인 항목": "Registry Scope / Record Type",
                        "Portfolio Proposal 진행 가능": "Current Candidate로 남길 후보는 `current_candidate`, 참고 후보는 `near_miss` 또는 `scenario`로 맞게 저장됨",
                        "멈춰야 하는 경우": "Current 후보 근거가 부족한데 `current_candidate`로 저장하려 하거나 Stop 범위임",
                    },
                    {
                        "확인 항목": "중복 저장",
                        "Portfolio Proposal 진행 가능": "같은 Review Note가 이미 저장된 경우 기본 append를 막고, 의도적 revision일 때만 체크박스를 켬",
                        "멈춰야 하는 경우": "같은 판단을 의미 없이 반복 append하려는 경우",
                    },
                    {
                        "확인 항목": "Pre-Live 운영 기록 / Proposal Route",
                        "Portfolio Proposal 진행 가능": "`3. 운영 기록 저장 및 Portfolio Proposal 이동`에서 `Save Record=가능`, `Next Route=PORTFOLIO_PROPOSAL_READY`",
                        "멈춰야 하는 경우": "`COMPARE_REVIEW_READY`는 Compare 재검토, `BOARD_HOLD`는 보강 필요",
                    },
                ]
            )
            st.dataframe(packaging_rows, use_container_width=True, hide_index=True)
            st.success(
                "`Candidate Packaging 저장 준비`가 저장 가능이고, Review Note / registry row / Pre-Live 운영 record가 남았으며, "
                "`운영 기록 저장 및 다음 단계 판단` Route가 `PORTFOLIO_PROPOSAL_READY`이면 7단계 Portfolio Proposal로 넘어갑니다."
            )
            st.warning(
                "`COMPARE_REVIEW_READY`는 실패가 아니라 다른 경로입니다. 이 경우 Proposal로 바로 가지 말고 Compare에서 비교 후보를 추가해 다시 검토합니다."
            )

        with st.expander("7단계 Portfolio Proposal에서 8단계 Final Review로 넘어가는 최소 기준", expanded=True):
            st.caption(
                "이 기준은 단일 후보나 다중 후보 proposal을 Final Review가 읽을 수 있는지 판단하는 기준입니다. "
                "단일 후보는 추가 proposal 저장 없이 넘어가고, 다중 후보는 draft 저장이 필요합니다."
            )
            proposal_rows = pd.DataFrame(
                [
                    {
                        "확인 항목": "진행 방식",
                        "Final Review 진행 가능": "후보 1개는 단일 후보 직행 평가, 후보 2개 이상은 포트폴리오 초안 작성으로 진행",
                        "멈춰야 하는 경우": "후보가 없거나 여러 후보를 골라 놓고 역할 / 비중을 정하지 않음",
                    },
                    {
                        "확인 항목": "단일 후보 직행",
                        "Final Review 진행 가능": "candidate identity, result snapshot, paper_tracking, Real-Money signal, Data Trust가 확인됨",
                        "멈춰야 하는 경우": "Pre-Live record가 없거나 Real-Money hold / blocked, Data Trust snapshot 공백",
                    },
                    {
                        "확인 항목": "다중 후보 구성",
                        "Final Review 진행 가능": "target weight 합계가 100%이고 최소 1개 core anchor가 있음",
                        "멈춰야 하는 경우": "비중 합계가 맞지 않거나 포트폴리오 중심 후보가 없음",
                    },
                    {
                        "확인 항목": "Pre-Live 상태",
                        "Final Review 진행 가능": "active weight 후보가 paper_tracking 상태",
                        "멈춰야 하는 경우": "active 후보가 not_started, hold, reject, re_review 상태",
                    },
                    {
                        "확인 항목": "Proposal 저장 필요 여부",
                        "Final Review 진행 가능": "단일 후보 직행 평가는 저장 불필요, 다중 후보 구성은 proposal draft 저장 필요",
                        "멈춰야 하는 경우": "단일 후보인데 의미 없는 proposal 저장을 반복하거나, 다중 후보인데 구성 초안을 저장하지 않음",
                    },
                    {
                        "확인 항목": "Blocker",
                        "Final Review 진행 가능": "rejected 후보 active weight, blocked core anchor 같은 hard blocker가 없음",
                        "멈춰야 하는 경우": "저장 blocker가 남아 있음",
                    },
                ]
            )
            st.dataframe(proposal_rows, use_container_width=True, hide_index=True)
            st.success(
                "현재 Portfolio Proposal UI의 route label은 `LIVE_READINESS_DIRECT_READY` / `LIVE_READINESS_CANDIDATE_READY`로 남아 있을 수 있습니다. "
                "현재 제품 흐름에서는 이 상태를 Final Review가 읽을 수 있는 후보 형태로 해석합니다."
            )
            st.warning(
                "Portfolio Proposal은 최종 승인 단계가 아닙니다. 다중 후보 구성일 때만 `Save Portfolio Proposal Draft`를 사용하고, "
                "실전 후보 선정 여부는 Final Review에서 판단합니다."
            )

        with st.expander("8단계 Final Review 검증에서 9단계 최종 판단 기록으로 넘어가는 최소 기준", expanded=True):
            st.caption(
                "이 기준은 validation / robustness / paper observation을 확인한 뒤 최종 판단을 기록해도 되는지 보는 기준입니다."
            )
            validation_rows = pd.DataFrame(
                [
                    {
                        "확인 항목": "검토 대상",
                        "최종 판단 기록 가능": "단일 current candidate 또는 saved portfolio proposal이 명확히 선택됨",
                        "멈춰야 하는 경우": "source가 비어 있거나 저장 당시 후보 / proposal과 현재 선택이 맞지 않음",
                    },
                    {
                        "확인 항목": "Validation Pack",
                        "최종 판단 기록 가능": "route, score, blocker, component risk가 해석 가능하고 hard blocker가 없음",
                        "멈춰야 하는 경우": "Portfolio Construction, Data Trust, Blocking Scope 같은 hard blocker가 남음",
                    },
                    {
                        "확인 항목": "Robustness / Stress",
                        "최종 판단 기록 가능": "기간, benchmark, CAGR / MDD, stress preview가 판단 근거로 읽힘",
                        "멈춰야 하는 경우": "benchmark 부재, 기간 부족, drawdown gap 미해석처럼 검증 근거가 비어 있음",
                    },
                    {
                        "확인 항목": "Paper Observation",
                        "최종 판단 기록 가능": "paper tracking 또는 관찰 기준이 final record 안에서 설명 가능",
                        "멈춰야 하는 경우": "실전 전 관찰 조건이 전혀 없거나 남은 보강 항목을 설명하지 못함",
                    },
                    {
                        "확인 항목": "자동 실행 경계",
                        "최종 판단 기록 가능": "preview를 열어도 proposal 저장, live approval, broker order가 자동 수행되지 않음",
                        "멈춰야 하는 경우": "검증 surface가 저장 / 승인 / 주문처럼 오해될 수 있음",
                    },
                ]
            )
            st.dataframe(validation_rows, use_container_width=True, hide_index=True)
            st.success(
                "검토 대상이 명확하고 validation / robustness / paper observation의 hard blocker가 없으면 "
                "9단계에서 final decision route를 기록할 수 있습니다."
            )
            st.warning(
                "검증 통과는 주문 실행이 아닙니다. 이 단계는 최종 판단 기록으로 넘어갈 수 있는지 확인하는 stop/go 기준입니다."
            )

        with st.expander("9단계 최종 판단 기록에서 10단계 저장 결과 확인으로 넘어가는 최소 기준", expanded=True):
            st.caption(
                "이 기준은 `최종 검토 결과 기록`을 append-only final decision으로 남긴 뒤 다시 열어 볼 수 있는지 확인하는 기준입니다."
            )
            record_rows = pd.DataFrame(
                [
                    {
                        "확인 항목": "Final Decision Route",
                        "저장 결과 확인 가능": "`SELECT_FOR_PRACTICAL_PORTFOLIO`, `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, `RE_REVIEW_REQUIRED` 중 하나",
                        "멈춰야 하는 경우": "판단 route가 비어 있거나 화면 문구와 실제 route가 어긋남",
                    },
                    {
                        "확인 항목": "Operator Reason",
                        "저장 결과 확인 가능": "왜 선정 / 보류 / 거절 / 재검토인지 사람이 읽을 이유가 작성됨",
                        "멈춰야 하는 경우": "이유 없이 저장만 눌러 나중에 판단 근거를 복원할 수 없음",
                    },
                    {
                        "확인 항목": "Constraints / Next Action",
                        "저장 결과 확인 가능": "남은 제약과 다음 행동이 Final Review record 안에 남음",
                        "멈춰야 하는 경우": "선정했지만 어떤 조건에서 운용해야 하는지, 보류했지만 무엇을 더 볼지 모름",
                    },
                    {
                        "확인 항목": "Record Route",
                        "저장 결과 확인 가능": "`FINAL_REVIEW_RECORD_READY` 상태로 `최종 검토 결과 기록` 저장",
                        "멈춰야 하는 경우": "save readiness blocker가 남아 있거나 duplicate id가 충돌함",
                    },
                ]
            )
            st.dataframe(record_rows, use_container_width=True, hide_index=True)
            st.success(
                "`FINAL_REVIEW_RECORD_READY`이고 최종 판단 / 이유 / 다음 행동이 남아 있으면 "
                "10단계 `기록된 최종 검토 결과 확인`에서 결과를 다시 확인합니다."
            )
            st.warning(
                "Final Selection Decision Registry는 최종 판단 원본입니다. current candidate, Pre-Live, Portfolio Proposal registry를 덮어쓰지 않습니다."
            )

        with st.expander("10단계에서 실전 후보 선정 여부를 최종 확인하는 기준", expanded=True):
            st.caption(
                "이 기준은 사용자가 마지막으로 `이 포트폴리오가 실전 후보로 선정되었는가`를 읽는 기준입니다."
            )
            final_rows = pd.DataFrame(
                [
                    {
                        "저장 판단": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                        "화면 해석": "실전 후보로 선정",
                        "다음에 할 일": "실제 주문 전 투입 금액, 리밸런싱, 모니터링, stop / re-review 기준을 별도 운영 판단으로 정리",
                    },
                    {
                        "저장 판단": "HOLD_FOR_MORE_PAPER_TRACKING",
                        "화면 해석": "내용 부족 / 관찰 필요",
                        "다음에 할 일": "paper observation 기간과 추가 확인 지표를 채운 뒤 다시 Final Review",
                    },
                    {
                        "저장 판단": "REJECT_FOR_PRACTICAL_USE",
                        "화면 해석": "투자하면 안 됨",
                        "다음에 할 일": "실전 후보군에서 제외하고 필요하면 near-miss / rejected 근거로 보관",
                    },
                    {
                        "저장 판단": "RE_REVIEW_REQUIRED",
                        "화면 해석": "재검토 필요",
                        "다음에 할 일": "데이터 / 기간 / 후보 구성 / 비중 조건을 바꾼 뒤 다시 검토",
                    },
                ]
            )
            st.dataframe(final_rows, use_container_width=True, hide_index=True)
            st.success(
                "`SELECT_FOR_PRACTICAL_PORTFOLIO`로 저장된 record가 있으면, 현재 프로그램 기준으로는 "
                "실전 후보 선정 여부 확인까지 도달한 것입니다."
            )
            st.warning(
                "이 최종 확인도 live approval, broker order, 자동매매 지시가 아닙니다. "
                "화면의 `Live Approval / Order` 경계가 disabled 상태인지 함께 확인합니다."
            )

    st.markdown("### 문서와 파일")

    with st.container(border=True):
        st.markdown("#### 지금 먼저 보면 좋은 문서")
        docs_rows = pd.DataFrame(
            [
                {
                    "상황": "현재 finance 전체 구조를 잡고 싶을 때",
                    "문서": ".note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md",
                    "역할": "finance package의 현재 제품 표면, data / strategy / review layer 요약",
                },
                {
                    "상황": "과거 walkthrough 실습 맥락을 참고할 때",
                    "문서": ".note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md",
                    "역할": "초기 1~11 실습 세션의 질문 / 후보 예시 / Guide 보조 기능 기록. 현재 Guides 실행 흐름은 1~10단계 기준",
                },
                {
                    "상황": "Backtest 화면이 어떤 순서로 동작하는지 볼 때",
                    "문서": ".note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md",
                    "역할": "Single / Compare / Candidate Review / Portfolio Proposal / Final Review UI 흐름",
                },
                {
                    "상황": "포트폴리오 초안 저장소를 이해할 때",
                    "문서": ".note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md",
                    "역할": "여러 후보를 묶은 portfolio proposal draft가 무엇이고 언제 저장되는지 설명",
                },
                {
                    "상황": "과거 paper tracking ledger 기록을 해석할 때",
                    "문서": ".note/finance/operations/PAPER_PORTFOLIO_TRACKING_LEDGER_GUIDE.md",
                    "역할": "Phase33 ledger의 호환성 / 관찰 기록 의미 설명. 현재 main flow는 Final Review inline paper observation 기준",
                },
                {
                    "상황": "최종 판단 기록을 확인할 때",
                    "문서": ".note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md",
                    "역할": "Final Review에서 저장한 선정 / 보류 / 거절 / 재검토 판단 기록 사용법",
                },
                {
                    "상황": "용어가 헷갈릴 때",
                    "문서": ".note/finance/FINANCE_TERM_GLOSSARY.md",
                    "역할": "Real-Money, Pre-Live, Candidate Registry 같은 반복 용어 설명",
                },
                {
                    "상황": "프로젝트의 큰 phase 위치를 확인할 때",
                    "문서": ".note/finance/MASTER_PHASE_ROADMAP.md",
                    "역할": "전체 phase 흐름, 현재 방향, 이후 작업 축",
                },
                {
                    "상황": "최신 문서 목록을 훑고 싶을 때",
                    "문서": ".note/finance/FINANCE_DOC_INDEX.md",
                    "역할": "finance 문서의 상위 index",
                },
            ]
        )
        st.dataframe(docs_rows, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.markdown("#### 주요 파일 경로")
        st.caption(
            "JSONL 파일은 앱이 로컬에 남기는 append-only 기록입니다. "
            "같은 JSONL이라도 후보 정의, 관찰 상태, 포트폴리오 초안, 최종 판단처럼 맡는 역할이 다릅니다."
        )

        jsonl_tabs = st.tabs(["후보 검토 기록", "실행 / 재사용 기록", "문서 경로 모음"])

        with jsonl_tabs[0]:
            st.markdown("##### 후보 검토 JSONL 저장소")
            registry_rows = pd.DataFrame(
                [
                    {
                        "흐름 단계": "6단계 Candidate Packaging",
                        "파일": "CANDIDATE_REVIEW_NOTES.jsonl",
                        "담는 데이터": "후보 초안을 보고 사람이 남긴 Review Decision, 이유, 다음 행동",
                        "화면 위치": "Backtest > Candidate Review > 1. Draft 확인 / Review Note 저장",
                        "읽는 법": "저장 전 검토 메모입니다. 후보 자체를 확정한 registry는 아닙니다.",
                    },
                    {
                        "흐름 단계": "6단계 Candidate Packaging",
                        "파일": "CURRENT_CANDIDATE_REGISTRY.jsonl",
                        "담는 데이터": "명시적으로 남긴 current candidate, near-miss, scenario, stop 후보 row",
                        "화면 위치": "Backtest > Candidate Review > 2. Registry 저장 / Operations > Candidate Library",
                        "읽는 법": "이 프로그램이 다시 열어 볼 후보 정의 목록입니다.",
                    },
                    {
                        "흐름 단계": "6단계 Candidate Packaging",
                        "파일": "PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
                        "담는 데이터": "후보를 paper tracking, watchlist, hold, re-review 중 어떤 운영 상태로 둘지 남긴 기록",
                        "화면 위치": "Backtest > Candidate Review > 3. 운영 기록 저장 및 Portfolio Proposal 이동",
                        "읽는 법": "실제 돈을 넣기 전 관찰 / 보류 상태 기록입니다.",
                    },
                    {
                        "흐름 단계": "7단계 Portfolio Proposal",
                        "파일": "PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
                        "담는 데이터": "여러 후보를 묶은 목적, 역할, target weight, 비중 근거, blocker가 있는 proposal draft",
                        "화면 위치": "Backtest > Portfolio Proposal",
                        "읽는 법": "포트폴리오 구성 초안입니다. live approval이나 주문 지시가 아닙니다.",
                    },
                    {
                        "흐름 단계": "8단계 Final Review 검증",
                        "파일": "PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl",
                        "담는 데이터": "과거 Phase33에서 만든 paper tracking 관찰 조건과 trigger 기록",
                        "화면 위치": "Backtest > Portfolio Proposal / Final Review 호환 영역",
                        "읽는 법": "현재 main flow에서는 Final Review의 inline paper observation 기준으로 흡수해서 읽습니다.",
                    },
                    {
                        "흐름 단계": "9~10단계 Final Review",
                        "파일": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
                        "담는 데이터": "실전 후보 선정, 관찰 보류, 거절, 재검토 판단과 이유",
                        "화면 위치": "Backtest > Final Review > 최종 판단 및 테스트 검증 / 기록된 최종 검토 결과 확인",
                        "읽는 법": "최종 판단 원본입니다. `SELECT_FOR_PRACTICAL_PORTFOLIO`이면 실전 후보로 선정된 것으로 읽습니다.",
                    },
                ]
            )
            st.dataframe(registry_rows, use_container_width=True, hide_index=True)

            lineage_cols = st.columns(3)
            with lineage_cols[0]:
                with st.container(border=True):
                    st.markdown("**후보를 남기는 기록**")
                    st.caption("Candidate Review에서 생깁니다.")
                    st.markdown(
                        """
                        - `CANDIDATE_REVIEW_NOTES.jsonl`
                        - `CURRENT_CANDIDATE_REGISTRY.jsonl`
                        - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`
                        """
                    )
            with lineage_cols[1]:
                with st.container(border=True):
                    st.markdown("**포트폴리오로 묶는 기록**")
                    st.caption("Portfolio Proposal에서 생깁니다.")
                    st.markdown(
                        """
                        - `PORTFOLIO_PROPOSAL_REGISTRY.jsonl`
                        - `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl`
                        """
                    )
            with lineage_cols[2]:
                with st.container(border=True):
                    st.markdown("**최종 판단 기록**")
                    st.caption("Final Review에서 생깁니다.")
                    st.markdown(
                        """
                        - `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
                        - live approval 아님
                        - broker order 아님
                        """
                    )

            st.info(
                "흐름으로 읽으면 `Review Note -> Current Candidate -> Pre-Live 운영 기록 -> Portfolio Proposal -> Final Review Decision`입니다. "
                "각 저장소는 서로 덮어쓰지 않고, 단계별 판단을 따로 남깁니다."
            )

        with jsonl_tabs[1]:
            st.markdown("##### 실행 / 재사용 JSONL 저장소")
            runtime_rows = pd.DataFrame(
                [
                    {
                        "파일": "BACKTEST_RUN_HISTORY.jsonl",
                        "폴더": ".note/finance/run_history/",
                        "담는 데이터": "Backtest 실행 payload, 결과 요약, replay에 필요한 실행 기록",
                        "화면 위치": "Operations > Backtest Run History",
                        "읽는 법": "과거 실행을 다시 열거나 Candidate Draft로 넘기는 실행 이력입니다.",
                    },
                    {
                        "파일": "WEB_APP_RUN_HISTORY.jsonl",
                        "폴더": ".note/finance/run_history/",
                        "담는 데이터": "웹 앱 로컬 실행 / 운영 로그 성격의 runtime artifact",
                        "화면 위치": "로컬 운영 보조 기록",
                        "읽는 법": "일반적으로 commit하지 않는 generated artifact입니다.",
                    },
                    {
                        "파일": "SAVED_PORTFOLIOS.jsonl",
                        "폴더": ".note/finance/saved/",
                        "담는 데이터": "Compare에서 만든 재사용 가능한 portfolio mix setup",
                        "화면 위치": "Backtest > Compare & Portfolio Builder > 저장 Mix 다시 열기",
                        "읽는 법": "포트폴리오 proposal이나 후보 registry가 아니라, 다시 불러오거나 replay할 수 있는 weight setup입니다.",
                    },
                ]
            )
            st.dataframe(runtime_rows, use_container_width=True, hide_index=True)
            st.warning(
                "`run_history`와 `saved`의 JSONL은 연구 / 재현 편의 기록입니다. "
                "최종 후보 선정 여부는 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에서 확인합니다."
            )

        with jsonl_tabs[2]:
            st.markdown("##### 전체 경로 모음")
            st.code(
                "\n".join(
                    [
                        ".note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md",
                        ".note/finance/FINANCE_DOC_INDEX.md",
                        ".note/finance/MASTER_PHASE_ROADMAP.md",
                        ".note/finance/FINANCE_TERM_GLOSSARY.md",
                        ".note/finance/operations/BACKTEST_1_TO_11_WALKTHROUGH_SESSION.md",
                        ".note/finance/operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md",
                        ".note/finance/operations/PAPER_PORTFOLIO_TRACKING_LEDGER_GUIDE.md",
                        ".note/finance/operations/FINAL_PORTFOLIO_SELECTION_DECISIONS_GUIDE.md",
                        ".note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md",
                        ".note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl",
                        ".note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl",
                        ".note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
                        ".note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
                        ".note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl",
                        ".note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
                        ".note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl",
                        ".note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl",
                        ".note/finance/saved/SAVED_PORTFOLIOS.jsonl",
                        ".note/finance/WORK_PROGRESS.md",
                        ".note/finance/QUESTION_AND_ANALYSIS_LOG.md",
                    ]
                ),
                language="text",
            )

    with st.container(border=True):
        st.markdown("#### Guides에서 같이 기억할 경계")
        st.markdown(
            """
            - `Real-Money`는 개별 backtest 결과에 붙는 검증 신호입니다.
            - `Compare`는 후보를 서로 비교해 다음 검토 초안으로 보낼지 판단하는 단계입니다.
            - `Saved Portfolio Mix`는 Compare에서 만든 비중 조합을 다시 열기 위한 saved setup이며, 후보 registry나 최종 판단 기록이 아닙니다.
            - `Candidate Packaging`은 Draft 확인 / Review Note 저장 / Registry 저장 / Pre-Live 운영 기록 / Portfolio Proposal 이동 판단을 하나로 묶은 단계입니다.
            - `Candidate Draft`와 `Review Note`는 Candidate Packaging 안에서 쓰는 저장 전 검토 기록입니다.
            - `Current Candidate Registry`는 명시적으로 남긴 후보 목록입니다.
            - `Pre-Live 운영 기록`은 paper / watchlist / hold / re-review 같은 실전 전 운영 상태 기록입니다.
            - `Portfolio Proposal`은 단일 후보라면 저장을 반복하지 않고 Final Review 입력 후보로 읽고, 여러 후보를 묶을 때만 포트폴리오 초안을 저장하는 단계입니다.
            - `Proposal Components`는 비교 기능이 아니라 포트폴리오에 넣을 구성 후보 선택입니다. 비교는 `Compare & Portfolio Builder`에서 합니다.
            - `Paper Tracking Ledger`는 과거 Phase33 / 호환성 기록으로 남아 있지만, 현재 main flow에서는 Final Review의 paper observation 기준으로 흡수합니다.
            - `Final Review`는 validation, robustness, paper observation, 최종 판단 기록, 저장 결과 확인을 담당하는 마지막 active panel입니다.
            - `SELECT_FOR_PRACTICAL_PORTFOLIO`는 실전 후보로 선정되었다는 뜻이지 live approval, broker order, 자동매매 지시가 아닙니다.
            - `Live Approval / Order`는 현재 제품 범위 밖이며 화면에서도 disabled 경계로 읽습니다.
            """
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
