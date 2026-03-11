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
from app.jobs.preflight_checks import (
    check_asset_profile_prerequisites,
    check_factor_prerequisites,
    check_symbol_input,
)
from app.jobs.run_history import HISTORY_FILE, append_run_history, load_run_history
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
PERIOD_PRESETS = ["1mo", "3mo", "6mo", "1y", "5y", "10y", "15y"]
SYMBOL_SOURCE_OPTIONS = [
    "Manual",
    "NYSE Stocks",
    "NYSE ETFs",
    "NYSE Stocks + ETFs",
    "Profile Filtered Stocks",
    "Profile Filtered ETFs",
    "Profile Filtered Stocks + ETFs",
]


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


def main() -> None:
    st.set_page_config(
        page_title="Finance Admin",
        page_icon="F",
        layout="wide",
    )
    _init_state()

    st.title("Finance Data Collection Admin")
    st.caption("Phase 1 internal web app for ingestion jobs")
    st.info(
        "Inputs are now grouped by job. Symbol-based jobs use their own symbol input. "
        "`Asset Profile Collection` does not use symbols; it uses the existing NYSE universe tables in MySQL."
    )

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
            pipeline_symbols_input = _render_symbol_source_inputs("pipeline", "Pipeline Symbols")
            pipe_col1, pipe_col2 = st.columns(2)
            pipeline_period_input = pipe_col1.selectbox("Pipeline Period", PERIOD_PRESETS, index=3, key="pipeline_period_input")
            pipeline_interval_input = pipe_col2.selectbox("Pipeline Interval", ["1d", "1wk", "1mo"], index=0, key="pipeline_interval_input")
            pipe_col3, pipe_col4, pipe_col5 = st.columns(3)
            pipeline_start_input = pipe_col3.text_input("Pipeline Start", value="", key="pipeline_start_input")
            pipeline_end_input = pipe_col4.text_input("Pipeline End", value="", key="pipeline_end_input")
            pipeline_freq_input = pipe_col5.selectbox("Pipeline Freq", ["annual", "quarterly"], index=0, key="pipeline_freq_input")
            pipeline_symbol_check = check_symbol_input(pipeline_symbols_input)
            _render_check_result(pipeline_symbol_check)
            if st.button("Run Core Pipeline", use_container_width=True, disabled=_is_blocking(pipeline_symbol_check)):
                with st.spinner("Running core market-data pipeline..."):
                    result = run_pipeline_core_market_data(
                        pipeline_symbols_input,
                        start=pipeline_start_input or None,
                        end=pipeline_end_input or None,
                        period=pipeline_period_input,
                        interval=pipeline_interval_input,
                        freq=pipeline_freq_input,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### OHLCV Collection")
            st.write("Collect market price history and store it in MySQL.")
            st.caption(
                "Uses the `Symbols` input. Recommended before running Factors. "
                "Current date-range handling is more reliable with `period` than with `end`."
            )
            ohlcv_symbols_input = _render_symbol_source_inputs("ohlcv", "OHLCV Symbols")
            ohlcv_col1, ohlcv_col2 = st.columns(2)
            ohlcv_period_input = ohlcv_col1.selectbox("OHLCV Period", PERIOD_PRESETS, index=3, key="ohlcv_period_input")
            ohlcv_interval_input = ohlcv_col2.selectbox("OHLCV Interval", ["1d", "1wk", "1mo"], index=0, key="ohlcv_interval_input")
            ohlcv_col3, ohlcv_col4 = st.columns(2)
            ohlcv_start_input = ohlcv_col3.text_input("OHLCV Start", value="", key="ohlcv_start_input")
            ohlcv_end_input = ohlcv_col4.text_input("OHLCV End", value="", key="ohlcv_end_input")
            ohlcv_symbol_check = check_symbol_input(ohlcv_symbols_input)
            _render_check_result(ohlcv_symbol_check)
            if st.button("Run OHLCV Collection", use_container_width=True, disabled=_is_blocking(ohlcv_symbol_check)):
                with st.spinner("Running OHLCV collection..."):
                    result = run_collect_ohlcv(
                        ohlcv_symbols_input,
                        start=ohlcv_start_input or None,
                        end=ohlcv_end_input or None,
                        period=ohlcv_period_input,
                        interval=ohlcv_interval_input,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### Fundamentals Ingestion")
            st.write("Collect normalized financial statement snapshots and store them in MySQL.")
            st.caption(
                "Uses the `Symbols` input. Required before `Factor Calculation` for those symbols."
            )
            fundamentals_symbols_input = _render_symbol_source_inputs("fundamentals", "Fundamentals Symbols")
            fundamentals_freq_input = st.selectbox(
                "Fundamentals Frequency",
                ["annual", "quarterly"],
                index=0,
                key="fundamentals_freq_input",
            )
            fundamentals_symbol_check = check_symbol_input(fundamentals_symbols_input)
            _render_check_result(fundamentals_symbol_check)
            if st.button("Run Fundamentals Ingestion", use_container_width=True, disabled=_is_blocking(fundamentals_symbol_check)):
                with st.spinner("Running fundamentals ingestion..."):
                    result = run_collect_fundamentals(
                        fundamentals_symbols_input,
                        freq=fundamentals_freq_input,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### Factor Calculation")
            st.write("Read stored fundamentals and prices, calculate factors, and store results.")
            st.caption(
                "Uses the `Symbols` input. Requires matching OHLCV and fundamentals data to already exist in MySQL."
            )
            factor_symbols_input = _render_symbol_source_inputs("factor", "Factor Symbols")
            factor_col1, factor_col2, factor_col3 = st.columns(3)
            factor_freq_input = factor_col1.selectbox("Factor Frequency", ["annual", "quarterly"], index=0, key="factor_freq_input")
            factor_start_input = factor_col2.text_input("Factor Start", value="", key="factor_start_input")
            factor_end_input = factor_col3.text_input("Factor End", value="", key="factor_end_input")
            factor_check = check_factor_prerequisites(factor_symbols_input, freq=factor_freq_input)
            _render_check_result(factor_check)
            if st.button("Run Factor Calculation", use_container_width=True, disabled=_is_blocking(factor_check)):
                with st.spinner("Running factor calculation..."):
                    result = run_calculate_factors(
                        factor_symbols_input,
                        freq=factor_freq_input,
                        start=factor_start_input or None,
                        end=factor_end_input or None,
                    )
                _push_result(result)
                _render_result_summary(result)

        with st.container(border=True):
            st.markdown("### Asset Profile Collection")
            st.write("Collect stock and ETF profile metadata using the existing NYSE universe tables.")
            st.caption(
                "Does not use the `Symbols` input. Uses the selected `Asset Profile Kinds` and reads from "
                "`nyse_stock` / `nyse_etf` in MySQL."
            )
            profile_kind_options = st.multiselect(
                "Asset Profile Kinds",
                options=["stock", "etf"],
                default=["stock", "etf"],
                key="profile_kind_options",
            )
            kinds = tuple(profile_kind_options) if profile_kind_options else ()
            asset_profile_check = check_asset_profile_prerequisites(kinds)
            _render_check_result(asset_profile_check)
            if st.button("Run Asset Profile Collection", use_container_width=True, disabled=_is_blocking(asset_profile_check)):
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
            st.caption(
                "Uses the `Symbols` input. This job is usually slower than the normalized fundamentals job and may "
                "produce partial success if some issuers fail."
            )
            fs_symbols_input = _render_symbol_source_inputs("fs", "Financial Statement Symbols")
            fs_col1, fs_col2, fs_col3 = st.columns(3)
            fs_freq_input = fs_col1.selectbox("Financial Statement Freq", ["annual", "quarterly"], index=0, key="fs_freq_input")
            fs_periods_input = fs_col2.number_input("Financial Statement Periods", min_value=1, max_value=12, value=4, step=1, key="fs_periods_input")
            fs_period_input = fs_col3.selectbox("Financial Statement Period Type", ["annual", "quarterly"], index=0, key="fs_period_input")
            fs_symbol_check = check_symbol_input(fs_symbols_input)
            _render_check_result(fs_symbol_check)
            if st.button("Run Financial Statement Ingestion", use_container_width=True, disabled=_is_blocking(fs_symbol_check)):
                with st.spinner("Running financial statement ingestion..."):
                    result = run_collect_financial_statements(
                        fs_symbols_input,
                        freq=fs_freq_input,
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
