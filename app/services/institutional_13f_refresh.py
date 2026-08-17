from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Sequence

import pandas as pd

from finance.data.institutional_13f import form_13f_due_date

_FIRST_SUPPORTED_REPORT_PERIOD = pd.Timestamp("1975-03-31")


def _as_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    parsed = pd.Timestamp(value)
    if pd.isna(parsed):
        raise ValueError("date value is required")
    return parsed.date()


def _quarter_end(value: str | date) -> pd.Timestamp:
    parsed = pd.Timestamp(_as_date(value))
    quarter_end = parsed.to_period("Q").end_time.normalize()
    if parsed != quarter_end:
        raise ValueError(f"report period must be a calendar quarter end: {parsed.date().isoformat()}")
    return quarter_end


def latest_due_report_period(as_of_date: str | date) -> str | None:
    """Return the newest calendar quarter whose Form 13F deadline has passed."""

    as_of = pd.Timestamp(_as_date(as_of_date)).normalize()
    candidate = as_of.to_period("Q").end_time.normalize()
    while candidate >= _FIRST_SUPPORTED_REPORT_PERIOD:
        if pd.Timestamp(form_13f_due_date(candidate.date())) <= as_of:
            return candidate.date().isoformat()
        candidate = (candidate.to_period("Q") - 1).end_time.normalize()
    return None


def _next_due_date(report_period: str) -> str:
    current = _quarter_end(report_period)
    following = (current.to_period("Q") + 1).end_time.normalize()
    return form_13f_due_date(following.date()).isoformat()


def _quarter_label(report_period: str) -> str:
    period = _quarter_end(report_period).to_period("Q")
    return f"{period.year}년 {period.quarter}분기"


def build_institutional_refresh_action(
    *,
    as_of_date: str | date,
    manager_periods: Mapping[str, str | date | None],
    expected_ciks: Sequence[str],
    last_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a local-only refresh decision for the curated manager watchlist."""

    target = latest_due_report_period(as_of_date)
    expected = [str(cik).zfill(10) for cik in expected_ciks]
    if target is None:
        return {
            "action_id": "refresh_institutional_13f",
            "visible": False,
            "status": "not_ready",
            "target_report_period": None,
            "target_quarter_label": "",
            "label": "",
            "description": "아직 확인할 13F 보고 분기가 없습니다.",
            "completed_managers": 0,
            "expected_managers": len(expected),
            "pending_ciks": expected,
            "next_due_date": None,
        }

    normalized_periods = {
        str(cik).zfill(10): (_quarter_end(period).date().isoformat() if period else None)
        for cik, period in manager_periods.items()
    }
    pending = [cik for cik in expected if not normalized_periods.get(cik) or normalized_periods[cik] < target]
    completed = len(expected) - len(pending)
    if not pending:
        status = "current"
    elif completed:
        status = "partial"
    else:
        status = "due"

    quarter_label = _quarter_label(target)
    action = {
        "action_id": "refresh_institutional_13f",
        "visible": bool(pending),
        "status": status,
        "target_report_period": target,
        "target_quarter_label": quarter_label,
        "label": f"{quarter_label} 업데이트 확인 및 갱신",
        "description": "버튼을 누르면 SEC 공개 자료를 확인한 뒤 가능한 기관을 갱신합니다.",
        "completed_managers": completed,
        "expected_managers": len(expected),
        "pending_ciks": pending,
        "next_due_date": _next_due_date(target),
    }
    if last_result is not None:
        action["last_result"] = dict(last_result)
    return action
