from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from typing import Any

from app.services.nyse_calendar import (
    latest_completed_nyse_session,
    previous_nyse_trading_day,
)


ACTION = {
    "id": "refresh_sp500_price_data",
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
    except ValueError:
        return None


def _basis_date(model: Mapping[str, Any], symbol_key: str) -> date | None:
    basis = dict(model.get("basis") or {})
    row = dict(basis.get(symbol_key) or {})
    return _as_date(row.get("date") or row.get("price_basis_date"))


def _nyse_session_gap(start_exclusive: date, end_inclusive: date) -> int:
    current = start_exclusive + timedelta(days=1)
    count = 0
    while current <= end_inclusive:
        if previous_nyse_trading_day(current) == current:
            count += 1
        current += timedelta(days=1)
    return count


def build_sp500_price_freshness(
    model: Mapping[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Compare persisted SPX/SPY price dates with the last completed NYSE session."""
    spx_date: date | None = None
    spy_date: date | None = None
    try:
        spx_date = _basis_date(model, "spx")
        spy_date = _basis_date(model, "spy")
        expected = latest_completed_nyse_session(now)
        warnings: list[str] = []
        if spx_date and spx_date > expected:
            warnings.append("SPX_PRICE_DATE_AFTER_COMPLETED_SESSION")
        if spy_date and spy_date > expected:
            warnings.append("SPY_PRICE_DATE_AFTER_COMPLETED_SESSION")

        if spx_date is None:
            status = "MISSING"
            gap_sessions = None
            message = (
                f"SPX 가격 기준일이 없습니다. 최신 완료 장 {expected.isoformat()} "
                "자료를 수동으로 확인할 수 있습니다."
            )
        elif spx_date < expected:
            status = "REFRESH_AVAILABLE"
            gap_sessions = _nyse_session_gap(spx_date, expected)
            message = (
                f"가격 기준일 {spx_date.isoformat()} · "
                f"최신 완료 장 {expected.isoformat()}"
            )
        else:
            status = "READY"
            gap_sessions = 0
            message = f"최신 완료 장 {expected.isoformat()} 가격을 사용합니다."

        result: dict[str, Any] = {
            "status": status,
            "expected_price_date": expected.isoformat(),
            "price_basis_date": spx_date.isoformat() if spx_date else None,
            "spy_price_basis_date": spy_date.isoformat() if spy_date else None,
            "gap_sessions": gap_sessions,
            "message": message,
            "warnings": warnings,
        }
        if status != "READY":
            result["action"] = dict(ACTION)
        return result
    except Exception as exc:
        return {
            "status": "ERROR",
            "expected_price_date": None,
            "price_basis_date": spx_date.isoformat() if spx_date else None,
            "spy_price_basis_date": spy_date.isoformat() if spy_date else None,
            "gap_sessions": None,
            "message": f"최신 완료 장을 확인하지 못했습니다: {type(exc).__name__}",
            "warnings": ["FRESHNESS_CALCULATION_FAILED"],
            "action": dict(ACTION),
        }
