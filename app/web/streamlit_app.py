from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
import subprocess

import streamlit as st

# Ensure the project root is importable when Streamlit executes this file directly.
DIRECT_RUN_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(DIRECT_RUN_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(DIRECT_RUN_PROJECT_ROOT))

from app.web.final_selected_portfolio_dashboard import (
    configure_portfolio_monitoring_page_targets,
    render_final_selected_portfolio_dashboard_page,
)
from app.web.ingestion_console import (
    apply_pending_ingestion_prefill,
    init_ingestion_state,
    promote_pending_job,
    render_ingestion_page,
)
from app.web.institutional_portfolios import render_institutional_portfolios_page
from app.web.overview_dashboard import render_overview_dashboard
from app.web.backtest_page import render_backtest_tab
from app.web import reference_contextual_help as reference_contextual_help_module
from app.web.reference_center import (
    configure_reference_center_page_targets,
    render_reference_center_page,
)
from app.web.today_page import configure_today_page_targets, render_today_page
from app.workspace_paths import PROJECT_ROOT


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


def _configure_reference_contextual_help_page_targets(page_targets: dict[str, object]) -> None:
    configure = getattr(reference_contextual_help_module, "configure_reference_contextual_help_page_targets", None)
    if callable(configure):
        configure(page_targets)


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
    render_ingestion_page(
        runtime_marker=APP_RUNTIME_MARKER,
        loaded_at=APP_RUNTIME_LOADED_AT,
        git_sha=CURRENT_GIT_SHORT_SHA,
    )


def _render_institutional_portfolios_page() -> None:
    render_institutional_portfolios_page()


def _render_backtest_page() -> None:
    render_backtest_tab()


def _render_selected_portfolio_dashboard_page() -> None:
    render_final_selected_portfolio_dashboard_page()


def main() -> None:
    st.set_page_config(
        page_title="Finance Console",
        page_icon="F",
        layout="wide",
    )
    _install_copy_shortcut_guard()
    init_ingestion_state()
    promote_pending_job()
    apply_pending_ingestion_prefill()

    today_page = st.Page(
        render_today_page,
        title="Today",
        icon="☀️",
        default=True,
        url_path="today",
    )
    overview_page = st.Page(
        _render_overview_page,
        title="Market Research",
        icon="🔎",
        url_path="overview",
    )
    institutional_portfolios_page = st.Page(
        _render_institutional_portfolios_page,
        title="Institutional Holdings",
        icon="🏛️",
        url_path="institutional-portfolios",
    )
    ingestion_page = st.Page(
        _render_ingestion_page,
        title="Data Operations",
        icon="🛠️",
        url_path="ingestion",
    )
    backtest_page = st.Page(
        _render_backtest_page,
        title="Portfolio Lab",
        icon="📈",
        url_path="backtest",
    )

    selected_portfolio_dashboard_page = st.Page(
        _render_selected_portfolio_dashboard_page,
        title="Portfolio Monitoring",
        icon="📊",
        url_path="selected-portfolio-dashboard",
    )
    reference_page = st.Page(
        render_reference_center_page,
        title="Reference Center",
        icon="📚",
        url_path="reference",
    )
    configure_today_page_targets(
        {
            "market_research": overview_page,
            "stock_research": overview_page,
            "portfolio_monitoring": selected_portfolio_dashboard_page,
        }
    )
    configure_portfolio_monitoring_page_targets({"backtest": backtest_page})
    configure_reference_center_page_targets(
        {
            "overview": overview_page,
            "institutional_portfolios": institutional_portfolios_page,
            "ingestion": ingestion_page,
            "backtest": backtest_page,
            "portfolio_monitoring": selected_portfolio_dashboard_page,
        }
    )
    _configure_reference_contextual_help_page_targets(
        {
            "reference": reference_page,
        }
    )
    navigation = st.navigation(
        {
            "Research": [
                today_page,
                overview_page,
                institutional_portfolios_page,
            ],
            "Portfolio": [
                backtest_page,
                selected_portfolio_dashboard_page,
            ],
            "Data": [
                ingestion_page,
            ],
            "Help": [
                reference_page,
            ],
        },
        position="top",
    )
    navigation.run()

if __name__ == "__main__":
    main()
