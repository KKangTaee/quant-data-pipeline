from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import date, datetime, timedelta
from typing import Any

ACTION = {
    "id": "refresh_economic_cycle_data",
    "label": "최신 발표 확인·재계산",
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
    """Return the latest closed official monthly cycle date."""
    return latest_closed_economic_cycle_month_end(value)


def latest_closed_economic_cycle_month_end(
    value: date | datetime | None = None,
) -> date:
    """Return the month-end immediately preceding the reference date's month."""
    resolved = _as_date(value) or date.today()
    return resolved.replace(day=1) - timedelta(days=1)


def _latest_source_observation_date(
    intramonth: Mapping[str, Any],
) -> date | None:
    coverage = intramonth.get("source_coverage")
    series = coverage.get("series") if isinstance(coverage, Mapping) else None
    if not isinstance(series, (list, tuple)):
        observed = intramonth.get("observed_state_json")
        if not isinstance(observed, Mapping):
            try:
                observed = json.loads(str(observed or "{}"))
            except (TypeError, ValueError, json.JSONDecodeError):
                observed = {}
        series = (
            observed.get("series_quality")
            if isinstance(observed, Mapping)
            else None
        )
    if not isinstance(series, (list, tuple)):
        return None
    dates = [
        parsed
        for item in series
        if isinstance(item, Mapping)
        and (parsed := _as_date(item.get("latest_observation_date"))) is not None
    ]
    return max(dates) if dates else None


def economic_cycle_quality_refresh_required(
    snapshot: Mapping[str, Any] | None,
) -> bool:
    """Identify persisted RTDSM rows written before the quality contract."""

    row = dict(snapshot or {})
    if "observed_state_json" not in row:
        return False
    observed = row.get("observed_state_json")
    if not isinstance(observed, Mapping):
        try:
            observed = json.loads(str(observed or "{}"))
        except (TypeError, ValueError, json.JSONDecodeError):
            return True
    if not isinstance(observed, Mapping):
        return True
    if str(observed.get("source") or "") != "philadelphia_fed_rtdsm":
        return False
    return not (
        observed.get("available_series") is not None
        and observed.get("total_series") == 4
        and "series_quality" in observed
    )


def build_economic_cycle_freshness(
    intramonth: Mapping[str, Any] | None,
    *,
    today: date | datetime | None = None,
    read_error: bool = False,
) -> dict[str, Any]:
    """Compare the persisted official snapshot with the latest closed month."""
    target = latest_closed_economic_cycle_month_end(today)
    resolved_intramonth = dict(intramonth or {})
    persisted = _as_date(resolved_intramonth.get("as_of_date"))
    successful_collection_at = str(
        resolved_intramonth.get("source_collected_at") or ""
    ).strip()
    latest_source = _latest_source_observation_date(resolved_intramonth)
    quality_refresh_required = economic_cycle_quality_refresh_required(
        resolved_intramonth
    )
    if read_error:
        status = "ERROR"
        message = (
            "저장된 최신 계산일을 확인하지 못했습니다. "
            "수동으로 다시 확인할 수 있습니다."
        )
    elif persisted is None:
        status = "MISSING"
        message = (
            f"공식 월간 관측 결과가 없습니다. {target.isoformat()} 기준으로 "
            "발표 자료를 다시 확인할 수 있습니다."
        )
    elif persisted < target or quality_refresh_required:
        status = "REFRESH_AVAILABLE"
        message = (
            "공식 관측 월은 최신이지만 RTDSM 품질 정보를 한 번 다시 반영해야 합니다."
            if persisted >= target and quality_refresh_required
            else f"현재 공식 관측 {persisted.isoformat()} · 최신 종료 월 {target.isoformat()}"
        )
    else:
        status = "READY"
        message = f"최신 공식 관측 {persisted.isoformat()}"
    result: dict[str, Any] = {
        "status": status,
        "persisted_as_of_date": persisted.isoformat() if persisted else None,
        "target_as_of_date": target.isoformat(),
        "last_successful_collection_at": successful_collection_at or None,
        "latest_source_observation_date": (
            latest_source.isoformat() if latest_source else None
        ),
        "quality_refresh_required": quality_refresh_required,
        "refresh_required": status != "READY",
        "message": message,
    }
    if status != "READY":
        result["action"] = dict(ACTION)
    return result
