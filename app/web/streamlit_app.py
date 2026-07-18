from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
import subprocess

import pandas as pd
import streamlit as st

# Ensure the project root is importable when Streamlit executes this file directly.
DIRECT_RUN_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(DIRECT_RUN_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(DIRECT_RUN_PROJECT_ROOT))

from app.web.final_selected_portfolio_dashboard import render_final_selected_portfolio_dashboard_page
from app.web.ingestion_console import (
    apply_pending_ingestion_prefill,
    init_ingestion_state,
    promote_pending_job,
    render_ingestion_page,
)
from app.web.institutional_portfolios import render_institutional_portfolios_page
from app.web.operations_overview import render_operations_overview_page
from app.web.ops_review import render_operations_dashboard
from app.web.overview_dashboard import render_overview_dashboard
from app.web.backtest_page import render_backtest_tab
from app.web import reference_contextual_help as reference_contextual_help_module
from app.web.reference_guides import render_reference_guides_page
from app.services.reference_glossary_catalog import (
    get_reference_concept_dictionary,
    load_glossary_sections_from_markdown,
    search_glossary_sections,
    search_reference_concepts,
)
from app.workspace_paths import GLOSSARY_DOC_PATH, PROJECT_ROOT


LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"
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


@st.cache_data(show_spinner=False)
def _load_glossary_sections() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    return load_glossary_sections_from_markdown(GLOSSARY_DOC_PATH)


@st.cache_data(show_spinner=False)
def _load_reference_concepts() -> list[dict[str, object]]:
    return get_reference_concept_dictionary()


def _format_concept_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    formatted: list[dict[str, object]] = []
    for row in rows:
        formatted.append(
            {
                "term": row.get("term", ""),
                "category": row.get("category", ""),
                "plain_meaning": row.get("plain_meaning", ""),
                "owner_screen": row.get("owner_screen", ""),
                "progress_implication": row.get("progress_implication", ""),
                "where_to_fix": row.get("where_to_fix", ""),
                "source": row.get("source", ""),
                "keywords": ", ".join(str(item) for item in row.get("keywords", []) or []),
            }
        )
    return formatted


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


def _render_ops_review_page() -> None:
    render_operations_dashboard(
        runtime_marker=APP_RUNTIME_MARKER,
        loaded_at=APP_RUNTIME_LOADED_AT,
        git_sha=CURRENT_GIT_SHORT_SHA,
        running_job=st.session_state.get("running_job"),
        recent_results=st.session_state.get("recent_results") or [],
        log_dir=LOG_DIR,
        csv_dir=CSV_DIR,
        render_runtime_snapshot=_render_runtime_build_indicator,
    )


def _render_selected_portfolio_dashboard_page() -> None:
    render_final_selected_portfolio_dashboard_page()


def _render_guides_page() -> None:
    render_reference_guides_page(
        runtime_marker=APP_RUNTIME_MARKER,
        loaded_at=APP_RUNTIME_LOADED_AT,
        git_sha=CURRENT_GIT_SHORT_SHA,
        render_runtime_snapshot=_render_runtime_build_indicator,
    )


def _render_glossary_page() -> None:
    st.title("Glossary")
    st.caption("현재 퀀트 프로그램에서 쓰는 용어와 상태 의미를 검색하고 다시 확인하는 reference 페이지입니다.")
    _render_runtime_build_indicator()

    meta_sections, term_sections = _load_glossary_sections()
    concept_rows = _load_reference_concepts()
    if not term_sections and not meta_sections and not concept_rows:
        st.error("Glossary 문서와 concept dictionary를 읽지 못했습니다. 문서 경로와 service catalog를 먼저 확인해 주세요.")
        st.code(str(GLOSSARY_DOC_PATH), language="text")
        return

    with st.container(border=True):
        st.markdown("### 용어 검색")
        st.caption("용어 제목만 검색할 수도 있고, 본문까지 같이 검색해서 관련 설명을 더 넓게 찾을 수도 있습니다.")
        query = st.text_input(
            "검색어",
            value="",
            key="reference_glossary_query",
            placeholder="예: promotion, shortlist, liquidity, universe",
        )
        search_body = st.checkbox(
            "본문까지 함께 검색",
            value=True,
            key="reference_glossary_search_body",
        )

        matched_concepts = search_reference_concepts(concept_rows, query)
        matched_sections = search_glossary_sections(term_sections, query, search_body=search_body)
        metric_cols = st.columns(4)
        metric_cols[0].metric("핵심 운영 용어", len(concept_rows))
        metric_cols[1].metric("문서 용어 수", len(term_sections))
        metric_cols[2].metric("Concept 결과", len(matched_concepts))
        metric_cols[3].metric("문서 결과", len(matched_sections))
        st.caption("source: shared concept dictionary + `.aiworkspace/note/finance/docs/GLOSSARY.md`")

    if meta_sections:
        with st.expander("이 reference를 어떻게 읽으면 되나", expanded=False):
            for section in meta_sections:
                with st.container(border=True):
                    st.markdown(f"#### {section['title']}")
                    st.markdown(section["body"])

    if query.strip() and not matched_concepts and not matched_sections:
        st.warning("검색 결과가 없습니다. 검색어를 조금 줄이거나 영어/한글 핵심 단어만 넣어 다시 확인해 주세요.")
        st.caption("예: `promotion`, `guardrail`, `유동성`, `benchmark`, `PIT`")
        return

    st.markdown("### 핵심 운영 용어")
    st.caption("Guides의 상태 / 용어 lookup과 같은 curated concept dictionary입니다.")
    if matched_concepts:
        st.dataframe(pd.DataFrame(_format_concept_rows(matched_concepts)), width="stretch", hide_index=True)
    else:
        st.info("핵심 운영 용어 결과가 없습니다. 아래 문서 용어 검색 결과를 확인하세요.")

    st.markdown("### 문서 용어 목록")
    if not query.strip():
        st.caption("검색어가 없어서 전체 용어를 보여주고 있습니다.")
    elif len(matched_sections) <= 5:
        st.caption("검색 결과가 적어서 관련 용어를 바로 펼쳐 보여줍니다.")
    else:
        st.caption("검색 결과가 많아서 제목 순서대로 정리했습니다. 필요한 항목만 펼쳐서 보시면 됩니다.")

    preview_titles = ", ".join(section["title"] for section in matched_sections[:8])
    if preview_titles:
        st.caption(f"빠른 훑어보기: {preview_titles}")

    auto_expand = bool(query.strip() and len(matched_sections) <= 5)
    for section in matched_sections:
        with st.expander(section["title"], expanded=auto_expand):
            st.markdown(section["body"])


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

    overview_page = st.Page(_render_overview_page, title="Overview", icon="🏠", default=True, url_path="overview")
    institutional_portfolios_page = st.Page(
        _render_institutional_portfolios_page,
        title="Institutional Portfolios",
        icon="🏛️",
        url_path="institutional-portfolios",
    )
    ingestion_page = st.Page(_render_ingestion_page, title="Ingestion", icon="🛠️", url_path="ingestion")
    backtest_page = st.Page(_render_backtest_page, title="Backtest", icon="📈", url_path="backtest")
    ops_review_page = st.Page(_render_ops_review_page, title="System / Data Health", icon="🧾", url_path="ops-review")

    selected_portfolio_dashboard_page = st.Page(
        _render_selected_portfolio_dashboard_page,
        title="Portfolio Monitoring",
        icon="📊",
        url_path="selected-portfolio-dashboard",
    )
    guides_page = st.Page(_render_guides_page, title="Guides", icon="📚", url_path="guides")
    glossary_page = st.Page(_render_glossary_page, title="Glossary", icon="📖", url_path="glossary")
    _configure_reference_contextual_help_page_targets(
        {
            "guides": guides_page,
            "glossary": glossary_page,
        }
    )
    operations_overview_page = st.Page(
        lambda: render_operations_overview_page(
            page_targets={
                "portfolio_monitoring": selected_portfolio_dashboard_page,
                "system_data_health": ops_review_page,
                "reference_guides": guides_page,
            }
        ),
        title="Operations Overview",
        icon="🧭",
        url_path="operations",
    )

    navigation = st.navigation(
        {
            "Workspace": [
                overview_page,
                institutional_portfolios_page,
                ingestion_page,
                backtest_page,
            ],
            "Operations": [
                operations_overview_page,
                selected_portfolio_dashboard_page,
                ops_review_page,
            ],
            "Reference": [
                guides_page,
                glossary_page,
            ],
        },
        position="top",
    )
    navigation.run()

if __name__ == "__main__":
    main()
