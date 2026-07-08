from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import pandas as pd
import streamlit as st

from app.services.institutional_portfolios import (
    INSTITUTIONAL_PORTFOLIO_CAVEATS,
    load_institutional_interest_model,
    load_institutional_manager_choices,
    load_institutional_portfolio_model,
)


def _as_frame(rows: list[dict[str, Any]], columns: list[str] | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(rows or [])
    if columns:
        for column in columns:
            if column not in frame.columns:
                frame[column] = None
        return frame[columns]
    return frame


def _render_caveats() -> None:
    with st.container(border=True):
        st.markdown("### Source Caveats")
        for caveat in INSTITUTIONAL_PORTFOLIO_CAVEATS[:5]:
            st.caption(f"- {caveat}")
        st.caption("원문 filing과 SEC data set link를 함께 확인하세요. 이 화면은 추천 / 승인 / 주문 workflow가 아닙니다.")


def _manager_label(row: dict[str, Any]) -> str:
    name = str(row.get("manager_name") or "Unknown manager")
    cik = str(row.get("cik") or "")
    period = row.get("latest_report_period") or "-"
    return f"{name} · CIK {cik} · latest {period}"


def _render_summary(model: dict[str, Any]) -> None:
    summary = dict(model.get("summary") or {})
    st.markdown("### Latest Portfolio Summary")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Report Period", summary.get("latest_report_period") or "-")
    metric_cols[1].metric("Filing Date", summary.get("latest_filing_date") or "-")
    metric_cols[2].metric("Holdings", f"{int(summary.get('holding_count') or 0):,}")
    metric_cols[3].metric("Reported Value", f"{float(summary.get('total_reported_value') or 0.0):,.0f}")

    source_ref = summary.get("source_ref")
    if source_ref:
        st.link_button("Open SEC source filing", str(source_ref), use_container_width=False)
    previous_period = summary.get("previous_report_period")
    if previous_period:
        st.caption(f"Previous comparable report: {previous_period} filed {summary.get('previous_filing_date') or '-'}")
    else:
        st.caption("Previous comparable filing is not available in the local 13F DB snapshot.")


def _render_holdings(model: dict[str, Any]) -> None:
    holdings = _as_frame(
        list(model.get("holdings") or []),
        [
            "issuer_name",
            "holding_symbol",
            "cusip",
            "title_of_class",
            "weight_pct",
            "reported_value",
            "shares_or_principal_amount",
            "sector",
            "industry",
        ],
    )
    st.markdown("### Holdings")
    if holdings.empty:
        st.info("No holdings are stored for this filing yet.")
        return
    st.dataframe(holdings, width="stretch", hide_index=True)


def _render_changes(model: dict[str, Any]) -> None:
    st.markdown("### Quarter-over-Quarter Changes")
    summary = dict(model.get("change_summary") or {})
    cols = st.columns(5)
    cols[0].metric("Newly Reported", summary.get("reported_new", 0))
    cols[1].metric("Increased", summary.get("increased", 0))
    cols[2].metric("Reduced", summary.get("reduced", 0))
    cols[3].metric("No Longer Reported", summary.get("no_longer_reported", 0))
    cols[4].metric("Unchanged", summary.get("unchanged", 0))
    st.caption("These are reported filing differences, not live buy / sell signals.")

    changes = _as_frame(
        list(model.get("changes") or []),
        [
            "change_type",
            "issuer_name",
            "holding_symbol",
            "cusip",
            "weight_pct",
            "latest_reported_value",
            "previous_reported_value",
            "value_delta",
            "latest_shares_or_principal",
            "previous_shares_or_principal",
            "share_delta",
        ],
    )
    if changes.empty:
        st.info("No previous filing comparison is available yet.")
        return
    st.dataframe(changes, width="stretch", hide_index=True)


def _render_exposure(model: dict[str, Any]) -> None:
    exposure = _as_frame(
        list(model.get("sector_exposure") or []),
        ["sector", "weight_pct", "reported_value", "holding_count"],
    )
    st.markdown("### Sector Exposure")
    if exposure.empty:
        st.info("Sector exposure is unavailable until holdings can be mapped to sector metadata.")
        return
    st.dataframe(exposure, width="stretch", hide_index=True)
    if "Unmapped" in set(exposure["sector"].astype(str)):
        st.warning("Some holdings are unmapped because official 13F rows do not contain reliable tickers.")


def _render_reverse_lookup() -> None:
    st.markdown("### Institutional Interest")
    st.caption("Search by ticker, CUSIP, or issuer text. Results use latest stored 13F filings and remain delayed reported ownership context.")
    query = st.text_input(
        "Ticker / CUSIP / Issuer",
        value="",
        key="institutional_interest_query",
        placeholder="AAPL, 037833100, Apple",
    )
    if not query.strip():
        return

    result = load_institutional_interest_model(query.strip(), limit=100)
    if result["status"] != "ok":
        st.warning("Institutional Interest lookup is unavailable until the SEC Form 13F dataset is collected.")
        _render_diagnostic_detail(result.get("message"))
        return
    model = dict(result.get("model") or {})
    st.metric("Latest filing holders", int(model.get("holder_count") or 0))
    holders = _as_frame(
        list(model.get("holders") or []),
        [
            "manager_name",
            "cik",
            "period_of_report",
            "filing_date",
            "issuer_name",
            "holding_symbol",
            "cusip",
            "weight_pct",
            "reported_value",
            "shares_or_principal_amount",
            "source_ref",
        ],
    )
    if holders.empty:
        st.info("No latest-filing holders matched the query in the local 13F DB snapshot.")
    else:
        st.dataframe(holders, width="stretch", hide_index=True)
    with st.expander("Lookup caveats", expanded=False):
        for caveat in model.get("caveats") or []:
            st.caption(f"- {caveat}")


def _render_diagnostic_detail(message: str | None) -> None:
    if not message:
        return
    with st.expander("Technical detail", expanded=False):
        st.caption(str(message))


def render_institutional_portfolios_page(
    *,
    runtime_marker: str | None = None,
    loaded_at: datetime | None = None,
    git_sha: str | None = None,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    st.title("Institutional Portfolios")
    st.caption(
        "Explore delayed SEC Form 13F institutional portfolio filings by manager and holding. "
        "This workspace is separate from Market Movers and does not create recommendations."
    )

    _render_caveats()
    if render_runtime_snapshot is not None:
        with st.expander("Runtime / Build", expanded=False):
            render_runtime_snapshot()
    elif runtime_marker or loaded_at or git_sha:
        st.caption(f"Runtime: {runtime_marker or '-'} · Loaded: {loaded_at or '-'} · Git: {git_sha or '-'}")

    with st.container(border=True):
        st.markdown("### Manager Search")
        search = st.text_input(
            "Manager / Institution",
            value="",
            key="institutional_portfolios_manager_search",
            placeholder="Berkshire Hathaway, Pershing Square, BlackRock",
        )
        result = load_institutional_manager_choices(search, limit=100)
        if result["status"] != "ok":
            st.warning(
                "Institutional 13F DB tables are not ready yet. "
                "Run `Workspace > Ingestion > SEC Form 13F 데이터셋 수집` first."
            )
            _render_diagnostic_detail(result.get("message"))
            _render_reverse_lookup()
            return

        managers = list(result.get("managers") or [])
        if not managers:
            st.info("No institutional 13F manager rows are available. Run the SEC Form 13F dataset collection first.")
            _render_reverse_lookup()
            return

        label_to_manager = {_manager_label(row): row for row in managers}
        selected_label = st.selectbox(
            "Select Manager",
            options=list(label_to_manager.keys()),
            index=0,
            key="institutional_portfolios_selected_manager",
        )
        selected_manager = label_to_manager[selected_label]

    portfolio_result = load_institutional_portfolio_model(str(selected_manager.get("cik") or ""))
    if portfolio_result["status"] != "ok":
        st.warning("Portfolio model is unavailable for this manager.")
        _render_diagnostic_detail(portfolio_result.get("message"))
        _render_reverse_lookup()
        return

    model = dict(portfolio_result.get("model") or {})
    _render_summary(model)
    holdings_tab, changes_tab, exposure_tab, lookup_tab = st.tabs(
        ["Holdings", "Reported Changes", "Sector Exposure", "Institutional Interest"]
    )
    with holdings_tab:
        _render_holdings(model)
    with changes_tab:
        _render_changes(model)
    with exposure_tab:
        _render_exposure(model)
    with lookup_tab:
        _render_reverse_lookup()
