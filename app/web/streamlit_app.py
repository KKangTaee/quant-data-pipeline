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

from app.web.backtest_candidate_library import render_candidate_library_page
from app.web.backtest_history import render_backtest_run_history_page
from app.web.final_selected_portfolio_dashboard import render_final_selected_portfolio_dashboard_page
from app.web.ingestion_console import (
    apply_pending_ingestion_prefill,
    init_ingestion_state,
    promote_pending_job,
    render_ingestion_page,
)
from app.web.operations_overview import render_operations_overview_page
from app.web.ops_review import render_operations_dashboard
from app.web.overview_dashboard import render_overview_dashboard
from app.web.pages.backtest import render_backtest_tab
from app.web.reference_guides import render_reference_guides_page
from app.workspace_paths import GLOSSARY_DOC_PATH, PROJECT_ROOT


LOG_DIR = PROJECT_ROOT / "logs"
CSV_DIR = PROJECT_ROOT / "csv"
GLOSSARY_META_SECTION_TITLES = {"목적", "사용 원칙"}
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
    if not GLOSSARY_DOC_PATH.exists():
        return [], []

    text = GLOSSARY_DOC_PATH.read_text(encoding="utf-8")
    sections: list[dict[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections.append(
                    {
                        "title": current_title,
                        "body": "\n".join(current_lines).strip(),
                    }
                )
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append(
            {
                "title": current_title,
                "body": "\n".join(current_lines).strip(),
            }
        )

    meta_sections = [section for section in sections if section["title"] in GLOSSARY_META_SECTION_TITLES]
    term_sections = [section for section in sections if section["title"] not in GLOSSARY_META_SECTION_TITLES]
    return meta_sections, term_sections


def _filter_glossary_sections(
    sections: list[dict[str, str]],
    query: str,
    *,
    search_body: bool,
) -> list[dict[str, str]]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return sections

    matched: list[dict[str, str]] = []
    for section in sections:
        title = str(section.get("title") or "")
        body = str(section.get("body") or "")
        title_hit = normalized_query in title.lower()
        body_hit = search_body and normalized_query in body.lower()
        if title_hit or body_hit:
            matched.append(section)
    return matched


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


def _render_backtest_page() -> None:
    st.title("Backtest")
    st.caption("백테스트 실행부터 비교, 후보 검토, Pre-Live 운영 기록, Portfolio Proposal까지 이어지는 후보 검토 작업 공간입니다.")
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


def _render_backtest_run_history_page(open_backtest_page) -> None:
    render_backtest_run_history_page(open_backtest_page=open_backtest_page)


# Render the saved candidate library and replay surface under Operations.
def _render_candidate_library_page() -> None:
    render_candidate_library_page()


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
    st.caption("현재 퀀트 프로그램에서 쓰는 용어를 검색하고 다시 확인하는 reference 페이지입니다.")
    _render_runtime_build_indicator()

    meta_sections, term_sections = _load_glossary_sections()
    if not term_sections and not meta_sections:
        st.error("`.aiworkspace/note/finance/docs/GLOSSARY.md`를 읽지 못했습니다. 문서 경로를 먼저 확인해 주세요.")
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

        matched_sections = _filter_glossary_sections(term_sections, query, search_body=search_body)
        metric_cols = st.columns(3)
        metric_cols[0].metric("총 용어 수", len(term_sections))
        metric_cols[1].metric("검색 결과", len(matched_sections))
        metric_cols[2].metric("검색 범위", "제목+본문" if search_body else "제목만")
        st.caption("source: `.aiworkspace/note/finance/docs/GLOSSARY.md`")

    if meta_sections:
        with st.expander("이 reference를 어떻게 읽으면 되나", expanded=False):
            for section in meta_sections:
                with st.container(border=True):
                    st.markdown(f"#### {section['title']}")
                    st.markdown(section["body"])

    if query.strip() and not matched_sections:
        st.warning("검색 결과가 없습니다. 검색어를 조금 줄이거나 영어/한글 핵심 단어만 넣어 다시 확인해 주세요.")
        st.caption("예: `promotion`, `guardrail`, `유동성`, `benchmark`, `PIT`")
        return

    st.markdown("### 용어 목록")
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
    ingestion_page = st.Page(_render_ingestion_page, title="Ingestion", icon="🛠️", url_path="ingestion")
    backtest_page = st.Page(_render_backtest_page, title="Backtest", icon="📈", url_path="backtest")
    ops_review_page = st.Page(_render_ops_review_page, title="System / Data Health", icon="🧾", url_path="ops-review")

    def open_backtest_page() -> None:
        st.switch_page(backtest_page)

    backtest_history_page = st.Page(
        lambda: _render_backtest_run_history_page(open_backtest_page),
        title="Archive: Backtest Runs",
        icon="🗂️",
        url_path="backtest-run-history",
    )
    candidate_library_page = st.Page(
        _render_candidate_library_page,
        title="Archive: Candidates",
        icon="📌",
        url_path="candidate-library",
    )
    selected_portfolio_dashboard_page = st.Page(
        _render_selected_portfolio_dashboard_page,
        title="Portfolio Monitoring",
        icon="📊",
        url_path="selected-portfolio-dashboard",
    )
    guides_page = st.Page(_render_guides_page, title="Guides", icon="📚", url_path="guides")
    glossary_page = st.Page(_render_glossary_page, title="Glossary", icon="📖", url_path="glossary")
    operations_overview_page = st.Page(
        lambda: render_operations_overview_page(
            page_targets={
                "portfolio_monitoring": selected_portfolio_dashboard_page,
                "system_data_health": ops_review_page,
                "archive_backtest_runs": backtest_history_page,
                "archive_candidates": candidate_library_page,
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
                ingestion_page,
                backtest_page,
            ],
            "Operations": [
                operations_overview_page,
                selected_portfolio_dashboard_page,
                ops_review_page,
                backtest_history_page,
                candidate_library_page,
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
