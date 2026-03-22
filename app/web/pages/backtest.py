from __future__ import annotations

from datetime import date

import streamlit as st

from app.web.runtime import run_equal_weight_backtest_from_db
from app.web.runtime.backtest import BacktestDataError, BacktestInputError


BACKTEST_PRESETS = {
    "Dividend ETFs": ["VIG", "SCHD", "DGRO", "GLD"],
    "Core ETFs": ["SPY", "QQQ", "TLT", "GLD"],
    "Big Tech": ["AAPL", "MSFT", "GOOG"],
}


def _init_backtest_state() -> None:
    if "backtest_last_bundle" not in st.session_state:
        st.session_state.backtest_last_bundle = None
    if "backtest_last_error" not in st.session_state:
        st.session_state.backtest_last_error = None
    if "backtest_last_error_kind" not in st.session_state:
        st.session_state.backtest_last_error_kind = None


def _parse_manual_tickers(text: str) -> list[str]:
    seen: set[str] = set()
    tickers: list[str] = []

    for raw in text.split(","):
        symbol = raw.strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        tickers.append(symbol)

    return tickers


def _format_currency(value: float) -> str:
    return f"${value:,.1f}"


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _format_ratio(value: float) -> str:
    return f"{value:.3f}"


def _render_summary_metrics(summary_df) -> None:
    row = summary_df.iloc[0]

    metric_cols = st.columns(4)
    metric_cols[0].metric("End Balance", _format_currency(float(row["End Balance"])))
    metric_cols[1].metric("CAGR", _format_percent(float(row["CAGR"])))
    metric_cols[2].metric("Sharpe Ratio", _format_ratio(float(row["Sharpe Ratio"])))
    metric_cols[3].metric("Maximum Drawdown", _format_percent(float(row["Maximum Drawdown"])))


def _render_last_run() -> None:
    error = st.session_state.backtest_last_error
    error_kind = st.session_state.backtest_last_error_kind
    bundle = st.session_state.backtest_last_bundle

    if error:
        if error_kind == "input":
            st.warning(error)
        elif error_kind == "data":
            st.error(error)
            st.caption("Hint: run the ingestion pipeline for the requested tickers and date range, then try again.")
        else:
            st.error(error)

    if not bundle:
        return

    summary_df = bundle["summary_df"]
    chart_df = bundle["chart_df"]
    result_df = bundle["result_df"]
    meta = bundle["meta"]

    st.markdown("### Latest Backtest Run")
    st.caption("First-pass result view. Summary, equity curve, preview table, and execution meta are separated so the screen reads more like a product surface.")

    st.markdown(f"#### {bundle['strategy_name']}")
    _render_summary_metrics(summary_df)

    summary_tab, curve_tab, table_tab, meta_tab = st.tabs(
        ["Summary", "Equity Curve", "Result Table", "Meta"]
    )

    with summary_tab:
        st.dataframe(summary_df, use_container_width=True)

    with curve_tab:
        chart_view = chart_df.copy().set_index("Date")
        st.line_chart(chart_view["Total Balance"], use_container_width=True)
        st.caption("The first chart view focuses on Total Balance only. Total Return overlays or comparison charts can be added later.")

    with table_tab:
        st.dataframe(result_df, use_container_width=True)

    with meta_tab:
        left, right = st.columns([1.1, 1.2], gap="large")
        with left:
            st.markdown("##### Execution Context")
            st.markdown(f"- `Mode`: `{meta['execution_mode']}`")
            st.markdown(f"- `Data`: `{meta['data_mode']}`")
            st.markdown(f"- `Universe`: `{meta['universe_mode']}`")
            st.markdown(f"- `Tickers`: `{', '.join(meta['tickers'])}`")
            st.markdown(f"- `Period`: `{meta['start']}` -> `{meta['end']}`")
        with right:
            st.markdown("##### Runtime Metadata")
            st.json(meta)


def _render_equal_weight_form() -> None:
    st.markdown("### Equal Weight")
    st.caption("Phase 4 first execution form. This step now runs the first DB-backed wrapper and keeps the result view intentionally simple.")

    with st.form("equal_weight_backtest_form", clear_on_submit=False):
        universe_mode = st.radio(
            "Universe Mode",
            options=["Preset", "Manual"],
            horizontal=True,
            help="Preset은 빠른 실행용, Manual은 직접 종목을 입력하는 방식입니다.",
        )

        preset_name = None
        tickers: list[str] = []

        if universe_mode == "Preset":
            preset_name = st.selectbox(
                "Preset",
                options=list(BACKTEST_PRESETS.keys()),
                index=0,
            )
            tickers = BACKTEST_PRESETS[preset_name]
            st.caption(f"Selected tickers: `{', '.join(tickers)}`")
        else:
            manual_tickers = st.text_input(
                "Tickers",
                value="VIG,SCHD,DGRO,GLD",
                help="Comma-separated tickers. Example: VIG,SCHD,DGRO,GLD",
            )
            tickers = _parse_manual_tickers(manual_tickers)

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2016, 1, 1))
        with col2:
            end_date = st.date_input("End Date", value=date(2026, 3, 20))

        with st.expander("Advanced Inputs", expanded=False):
            timeframe = st.selectbox("Timeframe", options=["1d"], index=0)
            option = st.selectbox("Option", options=["month_end"], index=0)
            rebalance_interval = st.number_input(
                "Rebalance Interval",
                min_value=1,
                max_value=36,
                value=12,
                step=1,
                help="Equal Weight sample 기준 기본값은 12입니다.",
            )

        submitted = st.form_submit_button("Run Equal Weight Backtest", use_container_width=True)

    if not submitted:
        return

    validation_errors: list[str] = []

    if not tickers:
        validation_errors.append("At least one ticker is required.")
    if start_date > end_date:
        validation_errors.append("Start Date must be earlier than or equal to End Date.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    payload = {
        "strategy_key": "equal_weight",
        "tickers": tickers,
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "timeframe": timeframe,
        "option": option,
        "rebalance_interval": int(rebalance_interval),
        "universe_mode": "preset" if universe_mode == "Preset" else "manual_tickers",
        "preset_name": preset_name,
    }

    st.markdown("#### Runtime Payload")
    st.json(payload)

    try:
        with st.spinner("Running Equal Weight backtest from DB..."):
            bundle = run_equal_weight_backtest_from_db(
                tickers=payload["tickers"],
                start=payload["start"],
                end=payload["end"],
                timeframe=payload["timeframe"],
                option=payload["option"],
                rebalance_interval=payload["rebalance_interval"],
                universe_mode=payload["universe_mode"],
                preset_name=payload["preset_name"],
            )
    except BacktestInputError as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "input"
        st.session_state.backtest_last_error = f"Backtest input issue: {exc}"
        return
    except BacktestDataError as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "data"
        st.session_state.backtest_last_error = f"Backtest data issue: {exc}"
        return
    except Exception as exc:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "system"
        st.session_state.backtest_last_error = f"Backtest execution failed: {exc}"
        return

    st.session_state.backtest_last_bundle = bundle
    st.session_state.backtest_last_error = None
    st.session_state.backtest_last_error_kind = None
    st.success("Backtest execution completed.")


def render_backtest_tab() -> None:
    _init_backtest_state()

    st.subheader("Backtest")
    st.caption("Phase 4 first-pass backtest tab")

    st.info(
        "This tab is intentionally being opened in small steps. "
        "The app structure is now unified, but the public runtime boundary and first execution screen "
        "will be implemented after each product choice is confirmed."
    )

    left, right = st.columns([1.2, 1.0], gap="large")

    with left:
        st.markdown("### Current Direction")
        st.markdown(
            """
            - One main app
            - Separate `Ingestion` and `Backtest` tabs
            - Internal code split by tab / concern
            - DB-backed price-only strategies first
            - `Equal Weight` is the first public strategy
            """
        )

        st.markdown("### Planned First Strategies")
        st.markdown(
            """
            - Equal Weight (first public wrapper)
            - GTAA
            - Risk Parity Trend
            - Dual Momentum
            """
        )

    with right:
        st.markdown("### Current Phase 4 Status")
        st.markdown(
            """
            - UI structure: chosen
            - Runtime public boundary: Equal Weight first
            - First screen scope: Equal Weight form first
            - Strategy execution UI: basic result layout connected
            """
        )

        st.markdown("### Next Step")
        st.markdown(
            """
            The next implementation step is to harden empty/error handling and decide whether to add the second strategy.
            """
        )

    st.divider()
    _render_equal_weight_form()
    st.divider()
    _render_last_run()
