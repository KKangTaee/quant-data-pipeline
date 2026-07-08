from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import pandas as pd
import streamlit as st

from app.services.institutional_portfolios import (
    INSTITUTIONAL_PORTFOLIO_CAVEATS,
    build_institutional_preview_workbench_payload,
    build_institutional_workbench_payload,
    load_institutional_interest_model,
    load_institutional_manager_choices,
    load_institutional_portfolio_model,
)
from app.web.institutional_portfolios_react_component import (
    institutional_portfolios_react_component_available,
    render_institutional_portfolios_workbench,
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


def _selected_manager(managers: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not managers:
        return None
    selected_cik = str(st.session_state.get("institutional_portfolios_selected_cik") or "")
    for row in managers:
        if str(row.get("cik") or "") == selected_cik:
            return row
    first = managers[0]
    st.session_state["institutional_portfolios_selected_cik"] = str(first.get("cik") or "")
    return first


def _handle_workbench_event(event: dict[str, Any] | None) -> None:
    if not event:
        return
    event_name = event.get("event")
    if event_name == "select_manager":
        cik = str(event.get("cik") or "")
        if cik and cik != st.session_state.get("institutional_portfolios_selected_cik"):
            st.session_state["institutional_portfolios_selected_cik"] = cik
            st.rerun()
    if event_name == "drilldown":
        query = str(event.get("query") or "").strip()
        if query and query != st.session_state.get("institutional_interest_query"):
            st.session_state["institutional_interest_query"] = query
            st.rerun()


def _render_workbench_or_fallback(payload: dict[str, Any], *, key: str) -> None:
    if institutional_portfolios_react_component_available():
        event = render_institutional_portfolios_workbench(payload, key=key)
        _handle_workbench_event(event)
        return

    st.info("React workbench build is unavailable. Run the component build step to render the visual portfolio explorer.")
    st.json(
        {
            "mode": payload.get("mode"),
            "manager": (payload.get("hero") or {}).get("manager_name"),
            "allocation": payload.get("allocation"),
            "change_board": payload.get("change_board"),
        }
    )


def render_institutional_portfolios_page(
    *,
    runtime_marker: str | None = None,
    loaded_at: datetime | None = None,
    git_sha: str | None = None,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    st.title("Institutional Portfolios")
    st.caption(
        "Explore delayed SEC Form 13F portfolios by manager, allocation, reported change, and holder lookup. "
        "This is a read-only research workspace, separate from Market Movers."
    )

    if render_runtime_snapshot is not None:
        with st.expander("Runtime / Build", expanded=False):
            render_runtime_snapshot()
    elif runtime_marker or loaded_at or git_sha:
        st.caption(f"Runtime: {runtime_marker or '-'} · Loaded: {loaded_at or '-'} · Git: {git_sha or '-'}")

    search = st.text_input(
        "Search manager / institution",
        value="",
        key="institutional_portfolios_manager_search",
        placeholder="Berkshire Hathaway, Pershing Square, BlackRock",
    )
    manager_result = load_institutional_manager_choices(search, limit=24)
    if manager_result["status"] != "ok":
        payload = build_institutional_preview_workbench_payload(
            "Local 13F data is not ready yet. This preview shows the visual portfolio workflow before official SEC rows are loaded."
        )
        _render_workbench_or_fallback(payload, key="institutional_portfolios_preview_error")
        with st.expander("Source caveats and setup", expanded=False):
            _render_caveats()
            _render_diagnostic_detail(manager_result.get("message"))
        return

    managers = list(manager_result.get("managers") or [])
    selected_manager = _selected_manager(managers)
    if selected_manager is None:
        payload = build_institutional_preview_workbench_payload("Local 13F DB has no manager rows yet. Preview mode is shown until data is collected.")
        _render_workbench_or_fallback(payload, key="institutional_portfolios_preview_empty")
        with st.expander("Source caveats and setup", expanded=False):
            _render_caveats()
        return

    portfolio_result = load_institutional_portfolio_model(str(selected_manager.get("cik") or ""))
    if portfolio_result["status"] != "ok":
        payload = build_institutional_preview_workbench_payload(
            "The selected manager portfolio is not available in the local 13F snapshot. Preview mode shows the intended visual workflow."
        )
        _render_workbench_or_fallback(payload, key="institutional_portfolios_preview_model_error")
        with st.expander("Source caveats and setup", expanded=False):
            _render_caveats()
            _render_diagnostic_detail(portfolio_result.get("message"))
        return

    model = dict(portfolio_result.get("model") or {})
    interest_query = str(st.session_state.get("institutional_interest_query") or "").strip()
    interest_model: dict[str, Any] | None = None
    if interest_query:
        interest_result = load_institutional_interest_model(interest_query, limit=100)
        if interest_result["status"] == "ok":
            interest_model = dict(interest_result.get("model") or {})

    payload = build_institutional_workbench_payload(
        model=model,
        managers=managers,
        selected_cik=str(selected_manager.get("cik") or ""),
        interest_model=interest_model,
        mode="live",
    )
    _render_workbench_or_fallback(payload, key=f"institutional_portfolios_{selected_manager.get('cik') or 'unknown'}")

    with st.expander("Detailed filings / table fallback", expanded=False):
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
