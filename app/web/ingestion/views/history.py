"""Compact, task-oriented activity history for Data Operations."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import streamlit as st

from app.jobs.run_history import load_run_history
from app.web.ingestion.guides import _job_guide, _job_title, _status_label
from app.web.ingestion.registry import active_ingestion_actions
from app.web.ingestion.workflows import ACTION_WORKFLOW_OWNERSHIP


PURPOSE_LABELS = {
    "market_research": "Market Research",
    "portfolio_lab": "Portfolio Lab",
    "institutional_holdings": "Institutional Holdings",
    "practical_validation": "Practical Validation",
    "official_import": "공식 파일 등록",
    "recovery_diagnosis": "원인 진단",
    "recovery_manual": "문제 복구",
}


def filter_data_operations_history(
    records: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Keep only runs owned by an active Data Operations action."""

    active_actions = set(active_ingestion_actions())
    return [
        record
        for record in records
        if str(record.get("job_name") or "") in active_actions
    ]


def _purpose_label(job_name: str) -> str:
    owners = ACTION_WORKFLOW_OWNERSHIP.get(job_name, ())
    labels = [PURPOSE_LABELS[owner] for owner in owners if owner in PURPOSE_LABELS]
    return " · ".join(labels) or "Data Operations"


def _scope_label(record: dict[str, Any]) -> str:
    metadata = record.get("run_metadata") or {}
    count = metadata.get("symbol_count")
    if count in {None, ""}:
        count = record.get("symbols_requested")
    try:
        numeric_count = int(count)
    except (TypeError, ValueError):
        numeric_count = 0
    if numeric_count > 0:
        return f"{numeric_count:,}개 대상"
    return "선택 범위"


def _result_label(record: dict[str, Any]) -> str:
    status = str(record.get("status") or "")
    if status == "failed":
        return "실행 실패"

    rows_written = record.get("rows_written")
    try:
        numeric_rows = int(rows_written)
    except (TypeError, ValueError):
        numeric_rows = 0
    result = f"{numeric_rows:,} rows 저장" if numeric_rows > 0 else "실행 완료"

    failed_symbols = record.get("failed_symbols") or []
    if isinstance(failed_symbols, (list, tuple, set)) and failed_symbols:
        result += f" · {len(failed_symbols):,}개 누락/실패"
    return result


def build_data_activity_row(record: dict[str, Any]) -> dict[str, str]:
    """Project one raw run record into the small user-facing activity contract."""

    job_name = str(record.get("job_name") or "")
    guide = _job_guide(job_name)
    return {
        "실행 시각": str(
            record.get("finished_at")
            or record.get("started_at")
            or "-"
        ),
        "작업": _job_title(job_name),
        "목적": _purpose_label(job_name),
        "상태": _status_label(record.get("status")),
        "범위": _scope_label(record),
        "결과": _result_label(record),
        "다음 행동": str(
            guide.get("next_action")
            or "관련 화면에서 최신 데이터를 확인하세요."
        ),
    }


def render_history_view(
    *,
    on_action_focus: Callable[[str], None],
) -> None:
    """Render recent Data Operations activity without raw payloads or file paths."""

    st.subheader("실행 이력")
    st.caption(
        "Data Operations에서 직접 실행한 작업만 보여줍니다. "
        "성공 여부와 다음 행동을 확인하고 필요한 설정으로 바로 돌아갈 수 있습니다."
    )
    history = filter_data_operations_history(load_run_history(limit=200))[:30]
    if not history:
        st.info("아직 Data Operations 실행 이력이 없습니다.")
        return

    rows = [build_data_activity_row(record) for record in history]
    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_order=[
            "실행 시각",
            "작업",
            "목적",
            "상태",
            "범위",
            "결과",
            "다음 행동",
        ],
    )

    attention_records = [
        record
        for record in history
        if record.get("status") in {"partial_success", "failed"}
    ]
    if attention_records:
        st.markdown("### 다시 확인할 작업")
        selected_index = st.selectbox(
            "다시 확인할 작업",
            options=range(len(attention_records)),
            format_func=lambda index: (
                f"{_job_title(attention_records[index].get('job_name'))} · "
                f"{_status_label(attention_records[index].get('status'))} · "
                f"{attention_records[index].get('finished_at') or attention_records[index].get('started_at') or '-'}"
            ),
            key="data_operations_history_attention",
            label_visibility="collapsed",
        )
        selected = attention_records[int(selected_index)]
        selected_row = build_data_activity_row(selected)
        st.warning(selected_row["다음 행동"])
        if st.button(
            "이 작업 설정 다시 열기",
            key="data_operations_history_reopen",
            use_container_width=True,
        ):
            on_action_focus(str(selected.get("job_name") or ""))


__all__ = [
    "build_data_activity_row",
    "filter_data_operations_history",
    "render_history_view",
]
