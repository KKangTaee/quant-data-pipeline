from __future__ import annotations

import sys
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
from app.jobs.run_history import HISTORY_FILE, append_run_history, load_run_history


JobResult = dict[str, Any]
LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"


def _init_state() -> None:
    if "recent_results" not in st.session_state:
        st.session_state.recent_results = []


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


def _render_result_summary(result: JobResult) -> None:
    banner = _status_to_banner(result["status"])
    banner(f'[{result["job_name"]}] {result["message"]}')

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Status", result["status"])
    col2.metric("Rows Written", result["rows_written"] or 0)
    col3.metric("Symbols Requested", result["symbols_requested"] or 0)
    col4.metric("Duration (sec)", result["duration_sec"])

    with st.expander("Result Details", expanded=False):
        st.json(result)

    steps = result.get("details", {}).get("steps")
    if steps:
        with st.expander("Pipeline Steps", expanded=False):
            for idx, step in enumerate(steps, start=1):
                st.markdown(
                    f'{idx}. `{step["job_name"]}` | status=`{step["status"]}` | '
                    f'rows={step.get("rows_written") or 0} | message={step["message"]}'
                )


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
                f'Finished: `{result["finished_at"]}`'
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


def main() -> None:
    st.set_page_config(
        page_title="Finance Admin",
        page_icon="F",
        layout="wide",
    )
    _init_state()

    st.title("Finance Data Collection Admin")
    st.caption("Phase 1 internal web app for ingestion jobs")

    with st.sidebar:
        st.header("Shared Inputs")
        symbols_input = st.text_area(
            "Symbols",
            value="AAPL,MSFT,GOOG",
            help="Comma-separated tickers. Fundamentals requires explicit symbols.",
        )
        period_input = st.text_input("Period", value="1y")
        interval_input = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)
        start_input = st.text_input("Start", value="")
        end_input = st.text_input("End", value="")
        freq_input = st.selectbox("Fundamental Frequency", ["annual", "quarterly"], index=0)
        fs_periods_input = st.number_input("Financial Statement Periods", min_value=1, max_value=12, value=4, step=1)
        fs_period_input = st.selectbox("Financial Statement Period Type", ["annual", "quarterly"], index=0)
        profile_kind_options = st.multiselect(
            "Asset Profile Kinds",
            options=["stock", "etf"],
            default=["stock", "etf"],
        )

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Run Jobs")

        with st.container(border=True):
            st.markdown("### Core Market Data Pipeline")
            st.write("Run OHLCV collection, fundamentals ingestion, and factor calculation in sequence.")
            if st.button("Run Core Pipeline", use_container_width=True):
                with st.spinner("Running core market-data pipeline..."):
                    result = run_pipeline_core_market_data(
                        symbols_input,
                        start=start_input or None,
                        end=end_input or None,
                        period=period_input,
                        interval=interval_input,
                        freq=freq_input,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### OHLCV Collection")
            st.write("Collect market price history and store it in MySQL.")
            if st.button("Run OHLCV Collection", use_container_width=True):
                with st.spinner("Running OHLCV collection..."):
                    result = run_collect_ohlcv(
                        symbols_input,
                        start=start_input or None,
                        end=end_input or None,
                        period=period_input,
                        interval=interval_input,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### Fundamentals Ingestion")
            st.write("Collect normalized financial statement snapshots and store them in MySQL.")
            if st.button("Run Fundamentals Ingestion", use_container_width=True):
                with st.spinner("Running fundamentals ingestion..."):
                    result = run_collect_fundamentals(
                        symbols_input,
                        freq=freq_input,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### Factor Calculation")
            st.write("Read stored fundamentals and prices, calculate factors, and store results.")
            if st.button("Run Factor Calculation", use_container_width=True):
                with st.spinner("Running factor calculation..."):
                    result = run_calculate_factors(
                        symbols_input,
                        freq=freq_input,
                        start=start_input or None,
                        end=end_input or None,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### Asset Profile Collection")
            st.write("Collect stock and ETF profile metadata using the existing NYSE universe tables.")
            if st.button("Run Asset Profile Collection", use_container_width=True):
                with st.spinner("Running asset profile collection..."):
                    kinds = tuple(profile_kind_options) if profile_kind_options else ("stock", "etf")
                    result = run_collect_asset_profiles(
                        kinds=kinds,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### Financial Statement Ingestion")
            st.write("Collect detailed financial statements from EDGAR for the provided symbols.")
            if st.button("Run Financial Statement Ingestion", use_container_width=True):
                with st.spinner("Running financial statement ingestion..."):
                    result = run_collect_financial_statements(
                        symbols_input,
                        freq=freq_input,
                        periods=int(fs_periods_input),
                        period=fs_period_input,
                    )
                _push_result(result)
                _render_result_summary(result)

    with col_right:
        _render_recent_results()
        st.divider()
        _render_persistent_run_history()
        st.divider()
        _render_recent_logs()
        st.divider()
        _render_failure_csv_preview()


if __name__ == "__main__":
    main()
