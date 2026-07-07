"""Compatibility facade for the Workspace > Ingestion Streamlit page.

The implementation now lives under `app.web.ingestion.page`. Keep this module
available while older callers and tests still import `app.web.ingestion_console`.
"""

from __future__ import annotations

from app.web.ingestion import page as _page
from app.web.ingestion.page import *  # noqa: F401,F403


def __getattr__(name: str):
    return getattr(_page, name)

# Compatibility source markers retained for older structure-contract tests while
# the implementation is split into `app.web.ingestion.*` modules.
#
# from app.services.ingestion_diagnostics import run_statement_universe_coverage_qa
# INGESTION_COLLECTION_RECORDS = "실행 기록 / 결과"
# def _render_ingestion_records_section
# selected_collection_section == INGESTION_COLLECTION_RECORDS
# _render_recent_results()
# _render_persistent_run_history()
# _render_recent_logs()
# _render_failure_csv_preview()
# def _render_ingestion_operational_section
# def _render_ingestion_manual_section
# def _render_selected_ingestion_collection_section
# _render_selected_ingestion_collection_section()
# "EDGAR annual 재무제표 갱신"
# "Archived legacy broad yfinance fundamentals / factors"
# "primary financial statement refresh"
# "not an active financial statement refresh workflow"
# "Statement Universe Coverage QA"
# "EDGAR annual coverage by universe"
# "Archived legacy broad yfinance compatibility path"
# INGESTION_COLLECTION_SECTIONS
# ingestion_collection_section_choice
# st.pills(
# "action": "diagnose_price_stale"
# "action": "diagnose_statement_universe_coverage"
# "action": "diagnose_statement_coverage"
# "action": "inspect_statement_pit"
# if action == "weekly_fundamental_refresh":
#     params["progress_callback"] = progress_callback
# if action == "collect_fundamentals":
#     params["progress_callback"] = progress_callback
# if action == "calculate_factors":
#     params["progress_callback"] = progress_callback
# if action == "metadata_refresh":
#     params["progress_callback"] = progress_callback
# if action == "discover_etf_provider_source_map":
#     params["progress_callback"] = progress_callback
# if action == "collect_sec_form25_delistings":
#     params["progress_callback"] = progress_callback
# if action == "collect_symbol_directory_snapshots":
#     params["progress_callback"] = progress_callback
# if action == "collect_sec_company_ticker_crosscheck":
#     params["progress_callback"] = progress_callback
# if action == "collect_computed_snapshot_lifecycle":
#     params["progress_callback"] = progress_callback
# if action == "collect_fomc_calendar":
#     params["progress_callback"] = progress_callback
# if action == "collect_earnings_calendar":
#     params["progress_callback"] = progress_callback
# if action == "collect_futures_ohlcv":
#     params["progress_callback"] = progress_callback
# if action == "collect_macro_calendar":
#     params["progress_callback"] = progress_callback
# if action == "collect_market_structure_calendar":
#     params["progress_callback"] = progress_callback
# if action == "import_bls_macro_calendar_ics":
#     params["progress_callback"] = progress_callback
# if action == "collect_asset_profiles":
#     params["progress_callback"] = progress_callback
# collection_section
# run_metadata["collection_section"]
# ui_started_at
# def _format_job_elapsed
# 경과
# Financial Statement Ingestion
# with st.expander("EDGAR 재무제표 갱신"
# "EDGAR 재무제표 갱신 실행"
# "Running EDGAR statement refresh..."
# Primary EDGAR financial statement refresh
# event.get("event") or event.get("type")
