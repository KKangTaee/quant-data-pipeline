from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
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
    run_metadata_refresh,
    run_collect_asset_profiles,
    run_collect_financial_statements,
    run_calculate_factors,
    run_collect_fundamentals,
    run_collect_ohlcv,
    run_pipeline_core_market_data,
    run_weekly_fundamental_refresh,
)
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
from app.web.pages.backtest import QUALITY_STRICT_PRESETS, render_backtest_tab
from finance.data.financial_statements import inspect_financial_statement_source
from finance.loaders import load_statement_coverage_summary, load_statement_timing_audit


JobResult = dict[str, Any]
LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"


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
WRITE_TARGETS = [
    {
        "job": "Daily Market Update",
        "writes_to": "finance_price.nyse_price_history",
    },
    {
        "job": "Weekly Fundamental Refresh",
        "writes_to": "finance_fundamental.nyse_fundamentals, finance_fundamental.nyse_factors",
    },
    {
        "job": "Extended Statement Refresh",
        "writes_to": "finance_fundamental.nyse_financial_statement_filings, finance_fundamental.nyse_financial_statement_labels, finance_fundamental.nyse_financial_statement_values",
    },
    {
        "job": "Metadata Refresh",
        "writes_to": "finance_meta.nyse_asset_profile",
    },
    {
        "job": "Core Market Data Pipeline",
        "writes_to": "finance_price.nyse_price_history, finance_fundamental.nyse_fundamentals, finance_fundamental.nyse_factors",
    },
    {
        "job": "OHLCV Collection",
        "writes_to": "finance_price.nyse_price_history",
    },
    {
        "job": "Fundamentals Ingestion",
        "writes_to": "finance_fundamental.nyse_fundamentals",
    },
    {
        "job": "Factor Calculation",
        "writes_to": "finance_fundamental.nyse_factors",
    },
    {
        "job": "Asset Profile Collection",
        "writes_to": "finance_meta.nyse_asset_profile",
    },
    {
        "job": "Financial Statement Ingestion",
        "writes_to": "finance_fundamental.nyse_financial_statement_filings, finance_fundamental.nyse_financial_statement_labels, finance_fundamental.nyse_financial_statement_values",
    },
]


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


def _push_result(result: JobResult) -> None:
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

    return _callback


def _render_last_completed_result() -> None:
    result = st.session_state.last_completed_result
    if result is None:
        return

    st.subheader("Latest Completed Run")
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
                "symbols": item.get("symbols_requested"),
                "rows_written": item.get("rows_written"),
                "duration_sec": item.get("duration_sec"),
                "context": run_metadata.get("execution_context"),
                "params": ", ".join(f"{k}={v}" for k, v in input_params.items()),
                "message": item.get("message"),
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


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
        view = coverage_df.copy()
        for column in ["min_period_end", "max_period_end", "min_available_at", "max_available_at"]:
            if column in view.columns:
                view[column] = pd.to_datetime(view[column], errors="coerce").dt.strftime("%Y-%m-%d")
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.info("Coverage summary returned no rows for the selected symbols/frequency.")

    if isinstance(audit_df, pd.DataFrame) and not audit_df.empty:
        st.markdown("##### Timing Audit")
        audit_view = audit_df.copy()
        for column in ["period_start", "period_end", "filing_date", "accepted_at", "available_at", "report_date"]:
            if column in audit_view.columns:
                audit_view[column] = pd.to_datetime(audit_view[column], errors="coerce").astype(str).replace("NaT", "")
        st.dataframe(audit_view, use_container_width=True, hide_index=True)
    else:
        st.info("Timing audit returned no rows for the selected audit scope.")

    if source_payload:
        st.markdown("##### Source Payload Inspection")
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


def _render_statement_pit_inspection_card() -> None:
    with st.container(border=True):
        st.markdown("### Statement PIT Inspection")
        st.write("Inspect statement coverage, timing rows, and source payload shape without leaving the UI.")
        st.caption(
            "Phase 7 helper card: read-only inspection for quarterly/annual PIT validation. This reduces the need for notebook snippets during manual checks."
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
            )
        )

        source_symbol_options = inspect_symbols_input[:20]
        source_symbol = st.selectbox(
            "Source Inspection Symbol",
            options=source_symbol_options if source_symbol_options else [""],
            index=0,
            key="statement_pit_source_symbol",
            help="EDGAR source payload inspection은 한 번에 한 심볼만 대상으로 합니다.",
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


def _render_write_target_table() -> None:
    st.subheader("Write Targets")
    st.caption("Each button below calls existing ingestion logic and writes to these MySQL tables.")
    st.dataframe(pd.DataFrame(WRITE_TARGETS), use_container_width=True, hide_index=True)


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


def _resolve_daily_market_execution_profile(source_mode: str) -> tuple[str, str]:
    raw_source_modes = {"NYSE Stocks", "NYSE ETFs", "NYSE Stocks + ETFs"}
    if source_mode in raw_source_modes:
        return (
            "raw_heavy",
            "Execution profile: `raw_heavy` | smaller batches, single-worker mode, longer cooldown, raw-universe operator sweep.",
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
    st.info(
        "Inputs are now grouped by job. Symbol-based jobs use their own symbol input. "
        "`Asset Profile Collection` does not use symbols; it uses the existing NYSE universe tables in MySQL."
    )
    _render_write_target_table()
    _render_last_completed_result()

    current_progress_callback = None
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Run Jobs")

        st.markdown("## Operational Pipelines")
        st.caption(
            "Use these buttons for routine daily / weekly / extended refresh workflows. "
            "Choose this section first when you are doing normal recurring operations."
        )

        with st.container(border=True):
            st.markdown("### Daily Market Update")
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
            daily_execution_profile, daily_profile_caption = _resolve_daily_market_execution_profile(daily_source_mode)
            st.caption(daily_profile_caption)
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

        with st.container(border=True):
            st.markdown("### Weekly Fundamental Refresh")
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

        with st.container(border=True):
            st.markdown("### Extended Statement Refresh")
            st.write("Refresh detailed financial statement ledgers for longer-history and account-level analysis.")
            st.caption("Recommended cadence: monthly, or before deep factor research and long-horizon backtest preparation.")
            st.caption("Recommended symbol source: `Profile Filtered Stocks` or a narrower research universe, because this job is heavier than summary fundamentals refresh.")
            st.caption(
                "Managed annual coverage presets are also available in the symbol preset dropdown: "
                "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, and `US Statement Coverage 1000`."
            )
            st.caption("Current defaults: `Profile Filtered Stocks`, `annual`, `0 periods (all available)`.")
            st.caption("Writes to: `finance_fundamental.nyse_financial_statement_filings`, `finance_fundamental.nyse_financial_statement_labels`, `finance_fundamental.nyse_financial_statement_values`")
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

        with st.container(border=True):
            st.markdown("### Metadata Refresh")
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

        st.markdown("## Manual Jobs")
        st.caption(
            "Use the cards below for exception handling, partial reruns, debugging, or fine-grained control. "
            "These are lower-level jobs and are not the default choice for routine operations."
        )

        with st.container(border=True):
            st.markdown("### Core Market Data Pipeline")
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

        with st.container(border=True):
            st.markdown("### OHLCV Collection")
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

        with st.container(border=True):
            st.markdown("### Fundamentals Ingestion")
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

        with st.container(border=True):
            st.markdown("### Factor Calculation")
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

        with st.container(border=True):
            st.markdown("### Asset Profile Collection")
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

        with st.container(border=True):
            st.markdown("### Financial Statement Ingestion")
            st.write("Collect detailed financial statements from EDGAR for the provided symbols.")
            st.caption(
                "Uses the `Symbols` input. This job is usually slower than the normalized fundamentals job and may "
                "produce partial success if some issuers fail."
            )
            st.caption(
                "For strict annual operator runs, the symbol preset dropdown also exposes "
                "`US Statement Coverage 100`, `US Statement Coverage 300`, `US Statement Coverage 500`, and `US Statement Coverage 1000`."
            )
            st.caption("Writes to: `finance_fundamental.nyse_financial_statement_filings`, `finance_fundamental.nyse_financial_statement_labels`, `finance_fundamental.nyse_financial_statement_values`")
            fs_symbol_result = _render_symbol_source_inputs("fs", "Financial Statement Symbols")
            fs_symbols_input = fs_symbol_result["symbols"]
            fs_col1, fs_col2, fs_col3 = st.columns(3)
            fs_freq_input = fs_col1.selectbox("Financial Statement Freq", ["annual", "quarterly"], index=0, key="fs_freq_input")
            fs_periods_input = fs_col2.number_input(
                "Financial Statement Periods",
                min_value=0,
                max_value=80,
                value=0,
                step=1,
                key="fs_periods_input",
                help="`0` means collect all available statement periods from EDGAR for each symbol.",
            )
            fs_period_input = fs_col3.selectbox("Financial Statement Period Type", ["annual", "quarterly"], index=0, key="fs_period_input")
            st.caption("Tip: `0 = all available periods`. This is recommended when rebuilding quarterly strict coverage.")
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
                            "freq": fs_freq_input,
                            "periods": int(fs_periods_input),
                            "period": fs_period_input,
                        },
                        "run_metadata": _job_metadata(
                            pipeline_type="manual_financial_statement_ingestion",
                            execution_mode="manual",
                            symbol_source=fs_symbol_result.get("source_mode"),
                            symbol_count=len(fs_symbols_input),
                            execution_context="Manual detailed financial statement ingestion for the selected symbols or universe source.",
                            input_params={
                                "freq": fs_freq_input,
                                "periods": int(fs_periods_input),
                                "period": fs_period_input,
                            },
                        ),
                    }
                )
            if _is_running_action("collect_financial_statements"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="Financial Statement Ingestion",
                )

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


def main() -> None:
    st.set_page_config(
        page_title="Finance Console",
        page_icon="F",
        layout="wide",
    )
    _init_state()
    _promote_pending_job()

    st.title("Finance Console")
    st.caption("Unified internal app for ingestion operations and backtest workflows")

    ingestion_tab, backtest_tab = st.tabs(["Ingestion", "Backtest"])

    with ingestion_tab:
        _render_ingestion_console()

    with backtest_tab:
        render_backtest_tab()

if __name__ == "__main__":
    main()
