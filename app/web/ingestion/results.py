"""Pure result-summary helpers for Workspace > Ingestion."""

from __future__ import annotations

from typing import Any

from app.web.ingestion.guides import _job_guide, _job_title, _status_label


JobResult = dict[str, Any]

def _format_count(value: Any) -> str:
    try:
        if value is None:
            return "0"
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value or "0")


def _format_duration(value: Any) -> str:
    try:
        numeric = float(value or 0)
    except (TypeError, ValueError):
        return str(value or "-")
    return f"{numeric:,.2f}"


def build_common_last_result_summary(result: JobResult) -> dict[str, str]:
    job_name = str(result.get("job_name") or "")
    guide = _job_guide(job_name)
    failed_count = len(result.get("failed_symbols") or [])
    status = str(result.get("status") or "")
    attention = ""
    if status == "partial_success":
        attention = "부분 성공은 pass가 아니므로 downstream validation에서 coverage gap으로 남을 수 있습니다."
    elif status == "failed":
        attention = "저장 row가 0이면 source 차단, 잘못된 입력, provider no-data를 먼저 구분하세요."
    elif failed_count:
        attention = "누락 / 실패 대상이 있으므로 상세 reason과 재실행 payload를 확인하세요."

    return {
        "title": _job_title(job_name),
        "job_name": job_name,
        "status": _status_label(status),
        "raw_status": status,
        "rows": _format_count(result.get("rows_written")),
        "requested": _format_count(result.get("symbols_requested")),
        "failed": _format_count(failed_count),
        "duration": _format_duration(result.get("duration_sec")),
        "message": str(result.get("message") or ""),
        "next_action": str(guide.get("next_action") or "실행 기록 / 결과 탭에서 상세 payload와 관련 로그를 확인하세요."),
        "attention": attention,
    }


def build_statement_refresh_action_summary(result: JobResult) -> dict[str, str]:
    details = result.get("details") or {}
    requested = int(result.get("symbols_requested") or 0)
    processed = int(result.get("symbols_processed") or 0)
    failed_count = len(result.get("failed_symbols") or [])
    rows_written = int(result.get("rows_written") or 0)
    freq = str(details.get("freq") or details.get("period") or "statement").strip() or "statement"
    raw_steps = details.get("steps") or []
    steps = [step for step in raw_steps if isinstance(step, dict)]
    failed_steps = [
        str(step.get("job_name") or "-")
        for step in steps
        if str(step.get("status") or "") != "success"
    ]

    coverage = f"{processed}/{requested} symbols processed" if requested else f"{processed} symbols processed"
    failed = f"{failed_count} failed"
    freshness = (
        f"{freq} EDGAR statement freshness is interpreted from accepted_at / available_at, "
        "not from provider fetch time."
    )

    if failed_steps:
        next_action = (
            f"Check failed step(s): {', '.join(failed_steps[:5])}. "
            "Run Statement Coverage Diagnosis, then rerun EDGAR annual refresh or shadow rebuild for affected symbols."
        )
    elif failed_count or str(result.get("status") or "") != "success":
        next_action = (
            "Run Statement Coverage Diagnosis, check SEC_USER_AGENT / fair-access pacing, "
            "then rerun affected symbols."
        )
    else:
        next_action = "Review statement shadow coverage and continue to Backtest strict annual preflight."

    return {
        "coverage": coverage,
        "freshness": freshness,
        "failed": failed,
        "next_action": next_action,
        "rows": f"{rows_written:,} rows written",
    }
