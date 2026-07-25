from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from typing import Any

ACTION = {
    "id": "refresh_economic_cycle_data",
    "label": "최신 데이터로 다시 계산",
    "enabled": True,
}


def _as_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def latest_economic_cycle_refresh_date(
    value: date | datetime | None = None,
) -> date:
    """Return the latest weekday eligible for a manual economic-cycle cutoff."""
    resolved = _as_date(value) or date.today()
    while resolved.weekday() >= 5:
        resolved -= timedelta(days=1)
    return resolved


def build_economic_cycle_freshness(
    intramonth: Mapping[str, Any] | None,
    *,
    today: date | datetime | None = None,
    read_error: bool = False,
) -> dict[str, Any]:
    """Compare one persisted intramonth cutoff with the latest eligible weekday."""
    target = latest_economic_cycle_refresh_date(today)
    persisted = _as_date(dict(intramonth or {}).get("as_of_date"))
    if read_error:
        status = "ERROR"
        message = (
            "저장된 최신 계산일을 확인하지 못했습니다. "
            "수동으로 다시 확인할 수 있습니다."
        )
    elif persisted is None:
        status = "MISSING"
        message = (
            f"월중 계산 결과가 없습니다. {target.isoformat()} 기준으로 "
            "다시 계산할 수 있습니다."
        )
    elif persisted < target:
        status = "REFRESH_AVAILABLE"
        message = (
            f"현재 계산일 {persisted.isoformat()} · "
            f"최신 계산 가능일 {target.isoformat()}"
        )
    else:
        status = "READY"
        message = f"최신 계산 기준 {persisted.isoformat()}"
    result: dict[str, Any] = {
        "status": status,
        "persisted_as_of_date": persisted.isoformat() if persisted else None,
        "target_as_of_date": target.isoformat(),
        "refresh_required": status != "READY",
        "message": message,
    }
    if status != "READY":
        result["action"] = dict(ACTION)
    return result
