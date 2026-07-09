from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import pandas as pd
import streamlit as st

from app.jobs.ingestion_jobs import run_collect_sec_13f_dataset
from app.services.institutional_portfolios import (
    INSTITUTIONAL_MANAGER_WATCHLIST,
    INSTITUTIONAL_PORTFOLIO_CAVEATS,
    build_institutional_preview_workbench_payload,
    build_institutional_workbench_payload,
    load_institutional_refresh_status,
    load_institutional_interest_model,
    load_institutional_manager_choices,
    load_institutional_portfolio_model,
)
from app.web.institutional_portfolios_react_component import (
    institutional_portfolios_react_component_available,
    render_institutional_portfolios_workbench,
)
from finance.data.institutional_13f import DEFAULT_SEC_13F_DATASET_LABEL, DEFAULT_SEC_13F_DATASET_URL


def _cik_text(value: Any) -> str | None:
    text = str(value or "").strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(10)[-10:]


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


def _render_refresh_status_panel(refresh_status: dict[str, Any]) -> None:
    refresh_panel_expanded = bool(st.session_state.pop("institutional_13f_refresh_panel_expanded", False))
    with st.expander("SEC 13F data refresh", expanded=refresh_panel_expanded):
        st.caption(
            "보조 액션입니다. 포트폴리오 화면은 저장된 DB snapshot을 읽고, 이 버튼은 공식 SEC 13F dataset을 DB에 다시 적재합니다."
        )
        status_cols = st.columns(4)
        status_cols[0].metric("Status", str(refresh_status.get("status") or "missing"))
        status_cols[1].metric("Latest report", str(refresh_status.get("latest_report_period") or "-"))
        status_cols[2].metric("Latest filing", str(refresh_status.get("latest_filing_date") or "-"))
        status_cols[3].metric("Rows", f"{int(refresh_status.get('rows_written') or 0):,}")
        last_collected = refresh_status.get("last_collected_at")
        if last_collected:
            st.caption(f"Last collected: {last_collected}")
        stale_reason = str(refresh_status.get("stale_reason") or "").strip()
        if refresh_status.get("is_stale") and stale_reason:
            st.warning(stale_reason)

        result = st.session_state.get("institutional_13f_refresh_result")
        if isinstance(result, dict):
            status = str(result.get("status") or "")
            message = str(result.get("message") or "")
            if status == "success":
                st.success(message or "SEC Form 13F refresh completed.")
            elif status:
                st.warning(message or f"SEC Form 13F refresh returned {status}.")

        dataset_label = st.text_input(
            "Dataset Label",
            value=str(refresh_status.get("source_dataset") or DEFAULT_SEC_13F_DATASET_LABEL),
            key="institutional_13f_refresh_dataset_label",
        )
        dataset_url = st.text_input(
            "SEC 13F Dataset URL",
            value=str(refresh_status.get("source_ref") or DEFAULT_SEC_13F_DATASET_URL),
            key="institutional_13f_refresh_dataset_url",
        )
        local_zip_path = st.text_input(
            "Local Zip Path",
            value="",
            key="institutional_13f_refresh_local_zip_path",
            help="입력하면 URL download 대신 이 zip 파일을 사용합니다.",
        )
        user_agent = st.text_input(
            "SEC User-Agent Override",
            value="",
            key="institutional_13f_refresh_user_agent",
            help="비워두면 SEC_USER_AGENT 환경변수 또는 collector 기본값을 사용합니다.",
        )
        if st.button(
            "최신 13F 데이터 갱신",
            key="institutional_13f_refresh_button",
            type="secondary",
            disabled=not (dataset_url.strip() or local_zip_path.strip()),
        ):
            with st.spinner("Collecting official SEC Form 13F dataset into DB..."):
                st.session_state["institutional_13f_refresh_result"] = run_collect_sec_13f_dataset(
                    dataset_url=None if local_zip_path.strip() else dataset_url.strip(),
                    dataset_zip_path=local_zip_path.strip() or None,
                    source_dataset=dataset_label.strip() or None,
                    user_agent=user_agent.strip() or None,
                )
            st.session_state["institutional_13f_refresh_panel_expanded"] = True
            st.rerun()


def _should_show_refresh_panel_on_entry(refresh_status: dict[str, Any]) -> bool:
    status = str(refresh_status.get("status") or "").strip().lower()
    latest_report_period = str(refresh_status.get("latest_report_period") or "").strip()
    rows_written = int(refresh_status.get("rows_written") or 0)
    if status in {"missing", "error", "failed", "not_ready", "unavailable"}:
        return True
    return not latest_report_period or rows_written <= 0


def _render_requested_refresh_status_panel(refresh_status: dict[str, Any]) -> bool:
    should_open = bool(st.session_state.get("institutional_13f_refresh_panel_expanded"))
    if not should_open and not _should_show_refresh_panel_on_entry(refresh_status):
        return False
    st.session_state["institutional_13f_refresh_panel_expanded"] = True
    _render_refresh_status_panel(refresh_status)
    return True


def _resolve_selected_manager(managers: list[dict[str, Any]], selected_cik: str | None) -> dict[str, Any] | None:
    if not managers:
        manager_rows: list[dict[str, Any]] = []
    else:
        manager_rows = [dict(row) for row in managers]

    by_cik: dict[str, dict[str, Any]] = {}
    for row in manager_rows:
        cik = _cik_text(row.get("cik"))
        if cik:
            by_cik[cik] = dict(row, cik=cik)

    selected = _cik_text(selected_cik)
    if selected and selected in by_cik:
        return by_cik[selected]

    for seed in sorted(INSTITUTIONAL_MANAGER_WATCHLIST, key=lambda row: int(row.get("priority") or 100)):
        seed_cik = _cik_text(seed.get("cik"))
        if not seed_cik:
            continue
        row = {**seed, **by_cik.get(seed_cik, {})}
        normalized = {
            "cik": seed_cik,
            "manager_name": row.get("manager_name") or row.get("display_name") or "Unknown manager",
            "latest_report_period": row.get("latest_report_period"),
            "latest_filing_date": row.get("latest_filing_date"),
            "source_ref": row.get("source_ref"),
        }
        if selected and selected == seed_cik:
            return normalized
        if not selected:
            return normalized

    return manager_rows[0] if manager_rows else None


def _selected_manager(managers: list[dict[str, Any]]) -> dict[str, Any] | None:
    selected = _resolve_selected_manager(managers, str(st.session_state.get("institutional_portfolios_selected_cik") or ""))
    if selected is not None:
        st.session_state["institutional_portfolios_selected_cik"] = str(selected.get("cik") or "")
    return selected


def _workbench_event_payload(event: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    nested = event.get("event")
    if isinstance(nested, dict):
        return dict(nested)
    return event


def _consume_workbench_event(payload: dict[str, Any], last_event_key: str | None) -> tuple[bool, str | None]:
    event_name = str(payload.get("id") or payload.get("event") or "").strip()
    if not event_name:
        return False, last_event_key
    nonce = str(payload.get("nonce") or payload.get("event_id") or "").strip()
    event_key = f"{event_name}:{nonce}" if nonce else f"{event_name}:{payload}"
    if event_key == last_event_key:
        return False, event_key
    return True, event_key


def _handle_workbench_event(event: dict[str, Any] | None) -> None:
    payload = _workbench_event_payload(event)
    if not payload:
        return
    should_handle, event_key = _consume_workbench_event(
        payload,
        str(st.session_state.get("institutional_portfolios_last_workbench_event_key") or ""),
    )
    if not should_handle:
        return
    st.session_state["institutional_portfolios_last_workbench_event_key"] = event_key
    event_name = str(payload.get("id") or payload.get("event") or "")
    if event_name == "open_refresh":
        event_id = str(payload.get("nonce") or payload.get("event_id") or event_name)
        if event_id != st.session_state.get("institutional_13f_last_refresh_open_event_id"):
            st.session_state["institutional_13f_last_refresh_open_event_id"] = event_id
            st.session_state["institutional_13f_refresh_panel_expanded"] = True
            st.rerun()
        return
    if event_name == "select_manager":
        cik = str(payload.get("cik") or "")
        if cik and cik != st.session_state.get("institutional_portfolios_selected_cik"):
            st.session_state["institutional_portfolios_selected_cik"] = cik
            st.session_state["institutional_interest_query_needs_load"] = False
            st.rerun()
    if event_name == "drilldown":
        query = str(payload.get("query") or "").strip()
        if query and query != st.session_state.get("institutional_interest_query"):
            st.session_state["institutional_interest_query"] = query
            st.session_state["institutional_interest_query_needs_load"] = True
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
        "저장된 SEC Form 13F 기준으로 기관 / 투자 대가의 포트폴리오, 분기 보고 변화, 보유 기관 역조회를 탐색합니다. "
        "이 화면은 읽기 전용 리서치 화면이며 Market Movers와 분리되어 있습니다."
    )

    if render_runtime_snapshot is not None:
        with st.expander("Runtime / Build", expanded=False):
            render_runtime_snapshot()
    elif runtime_marker or loaded_at or git_sha:
        st.caption(f"Runtime: {runtime_marker or '-'} · Loaded: {loaded_at or '-'} · Git: {git_sha or '-'}")

    search = st.text_input(
        "기관 / 투자 대가 검색",
        value="",
        key="institutional_portfolios_manager_search",
        placeholder="Berkshire Hathaway, Pershing Square, BlackRock",
    )
    refresh_result = load_institutional_refresh_status()
    refresh_status = dict(refresh_result.get("model") or {})
    refresh_panel_rendered = _render_requested_refresh_status_panel(refresh_status)
    manager_result = load_institutional_manager_choices(search, limit=24)
    if manager_result["status"] != "ok":
        payload = build_institutional_preview_workbench_payload(
            "Local 13F data is not ready yet. This preview shows the visual portfolio workflow before official SEC rows are loaded."
        )
        _render_workbench_or_fallback(payload, key="institutional_portfolios_preview_error")
        if not refresh_panel_rendered:
            _render_refresh_status_panel(refresh_status)
        with st.expander("Source caveats and setup", expanded=False):
            _render_caveats()
            _render_diagnostic_detail(manager_result.get("message"))
        return

    managers = list(manager_result.get("managers") or [])
    selected_manager = _selected_manager(managers)
    if selected_manager is None:
        payload = build_institutional_preview_workbench_payload("Local 13F DB has no manager rows yet. Preview mode is shown until data is collected.")
        _render_workbench_or_fallback(payload, key="institutional_portfolios_preview_empty")
        if not refresh_panel_rendered:
            _render_refresh_status_panel(refresh_status)
        with st.expander("Source caveats and setup", expanded=False):
            _render_caveats()
        return

    portfolio_result = load_institutional_portfolio_model(str(selected_manager.get("cik") or ""))
    if portfolio_result["status"] != "ok":
        payload = build_institutional_preview_workbench_payload(
            "The selected manager portfolio is not available in the local 13F snapshot. Preview mode shows the intended visual workflow."
        )
        _render_workbench_or_fallback(payload, key="institutional_portfolios_preview_model_error")
        if not refresh_panel_rendered:
            _render_refresh_status_panel(refresh_status)
        with st.expander("Source caveats and setup", expanded=False):
            _render_caveats()
            _render_diagnostic_detail(portfolio_result.get("message"))
        return

    model = dict(portfolio_result.get("model") or {})
    interest_query = str(st.session_state.get("institutional_interest_query") or "").strip()
    interest_model: dict[str, Any] | None = None
    if interest_query:
        cache = st.session_state.get("institutional_interest_model_cache")
        if isinstance(cache, dict) and cache.get("query") == interest_query:
            interest_model = dict(cache.get("model") or {})
        elif st.session_state.pop("institutional_interest_query_needs_load", False):
            interest_result = load_institutional_interest_model(interest_query, limit=100)
            if interest_result["status"] == "ok":
                interest_model = dict(interest_result.get("model") or {})
                st.session_state["institutional_interest_model_cache"] = {
                    "query": interest_query,
                    "model": interest_model,
                }

    payload = build_institutional_workbench_payload(
        model=model,
        managers=managers,
        selected_cik=str(selected_manager.get("cik") or ""),
        interest_model=interest_model,
        mode="live",
        refresh_status=refresh_status,
    )
    _render_workbench_or_fallback(payload, key=f"institutional_portfolios_{selected_manager.get('cik') or 'unknown'}")
    if not refresh_panel_rendered:
        _render_refresh_status_panel(refresh_status)

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
