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
    run_collect_asset_profiles,
    run_collect_financial_statements,
    run_calculate_factors,
    run_collect_fundamentals,
    run_collect_ohlcv,
    run_pipeline_core_market_data,
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


JobResult = dict[str, Any]
LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"
SYMBOL_PRESETS = {
    "Big Tech": "AAPL,MSFT,GOOG",
    "Core ETFs": "SPY,QQQ,TLT,GLD",
    "Dividend ETFs": "VIG,SCHD,DGRO,GLD",
    "Custom": "",
}
PERIOD_PRESETS = ["1d", "7d", "1mo", "3mo", "6mo", "1y", "5y", "10y", "15y"]
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
        "writes_to": "finance_fundamental.nyse_financial_statement_labels, finance_fundamental.nyse_financial_statement_values",
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


def _clear_running_job() -> None:
    st.session_state.running_job = None


def _dispatch_job(job: dict[str, Any], *, progress_callback: Any = None) -> JobResult:
    action = job["action"]
    params = dict(job["params"])

    if action == "pipeline_core_market_data":
        params["progress_callback"] = progress_callback
        return run_pipeline_core_market_data(**params)
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

    if action not in {"collect_ohlcv", "pipeline_core_market_data"} or symbol_count < 100:
        _render_inline_running_hint(action, label)
        return None

    progress_text = st.empty()
    progress_meta = st.empty()
    progress_bar = st.progress(0)

    if action == "collect_ohlcv":
        progress_text.info(f"`{label}` is running with live OHLCV progress.")
    else:
        progress_text.info(f"`{label}` is running with pipeline-stage progress.")

    def _callback(event: dict[str, Any]) -> None:
        event_type = event.get("event")

        if action == "collect_ohlcv" and event_type == "batch_progress":
            total_symbols = max(int(event.get("total_symbols", symbol_count) or symbol_count), 1)
            processed_symbols = min(int(event.get("processed_symbols", 0) or 0), total_symbols)
            percent = int((processed_symbols / total_symbols) * 100)
            progress_bar.progress(percent)
            progress_meta.caption(
                "Processed "
                f"`{processed_symbols}/{total_symbols}` symbols | "
                f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
                f"rows written `{event.get('rows_written', 0)}`"
            )
            return

        if action == "pipeline_core_market_data":
            total_stages = max(int(event.get("total_stages", 3) or 3), 1)
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
                progress_meta.caption(
                    "Current stage: `OHLCV` | "
                    f"processed `{processed_symbols}/{total_symbols}` symbols | "
                    f"batch `{event.get('batch_index', 0)}/{event.get('total_batches', 0)}` | "
                    f"rows written `{event.get('rows_written', 0)}`"
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

    steps = result.get("details", {}).get("steps")
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
        rows.append(
            {
                "job_name": item.get("job_name"),
                "status": item.get("status"),
                "started_at": item.get("started_at"),
                "finished_at": item.get("finished_at"),
                "rows_written": item.get("rows_written"),
                "symbols_requested": item.get("symbols_requested"),
                "duration_sec": item.get("duration_sec"),
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


def _resolve_symbols(preset_name: str, manual_value: str) -> str:
    preset_value = SYMBOL_PRESETS.get(preset_name, "")
    return preset_value if preset_name != "Custom" else manual_value


def _render_symbol_source_inputs(prefix: str, title: str = "Symbols") -> list[str]:
    source_mode = st.selectbox(
        f"{title} Source",
        SYMBOL_SOURCE_OPTIONS,
        index=0,
        key=f"{prefix}_source_mode",
    )

    manual_symbols: list[str] = []
    if source_mode == "Manual":
        preset_name = st.selectbox(
            f"{title} Preset",
            list(SYMBOL_PRESETS.keys()),
            index=0,
            key=f"{prefix}_preset",
        )
        manual_text = st.text_area(
            title,
            value=SYMBOL_PRESETS["Big Tech"],
            key=f"{prefix}_symbols_input",
        )
        manual_symbols = [s.strip() for s in _resolve_symbols(preset_name, manual_text).split(",") if s.strip()]

    source_result = resolve_symbol_source(source_mode, manual_symbols)
    if source_result["status"] == "ok":
        st.info(f'{source_result["message"]} Count: {source_result["count"]}')
        preview = ", ".join(source_result["symbols"][:10])
        if preview:
            st.caption(f"Preview: {preview}")
    else:
        st.error(source_result["message"])

    return source_result["symbols"]


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


def main() -> None:
    st.set_page_config(
        page_title="Finance Admin",
        page_icon="F",
        layout="wide",
    )
    _init_state()
    _promote_pending_job()

    st.title("Finance Data Collection Admin")
    st.caption("Phase 1 internal web app for ingestion jobs")
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

        with st.container(border=True):
            st.markdown("### Core Market Data Pipeline")
            st.write("Run OHLCV collection, fundamentals ingestion, and factor calculation in sequence.")
            st.caption(
                "Execution order: OHLCV -> Fundamentals -> Factors. "
                "This is the safest button when you want factors for the current symbol set."
            )
            st.caption("Writes to: `finance_price.nyse_price_history`, `finance_fundamental.nyse_fundamentals`, `finance_fundamental.nyse_factors`")
            pipeline_symbols_input = _render_symbol_source_inputs("pipeline", "Pipeline Symbols")
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
            ohlcv_symbols_input = _render_symbol_source_inputs("ohlcv", "OHLCV Symbols")
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
            fundamentals_symbols_input = _render_symbol_source_inputs("fundamentals", "Fundamentals Symbols")
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
            factor_symbols_input = _render_symbol_source_inputs("factor", "Factor Symbols")
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
            st.caption("Writes to: `finance_fundamental.nyse_financial_statement_labels`, `finance_fundamental.nyse_financial_statement_values`")
            fs_symbols_input = _render_symbol_source_inputs("fs", "Financial Statement Symbols")
            fs_col1, fs_col2, fs_col3 = st.columns(3)
            fs_freq_input = fs_col1.selectbox("Financial Statement Freq", ["annual", "quarterly"], index=0, key="fs_freq_input")
            fs_periods_input = fs_col2.number_input("Financial Statement Periods", min_value=1, max_value=12, value=4, step=1, key="fs_periods_input")
            fs_period_input = fs_col3.selectbox("Financial Statement Period Type", ["annual", "quarterly"], index=0, key="fs_period_input")
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
                    }
                )
            if _is_running_action("collect_financial_statements"):
                current_progress_callback = _build_progress_callback(
                    st.session_state.running_job,
                    label="Financial Statement Ingestion",
                )

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

if __name__ == "__main__":
    main()
