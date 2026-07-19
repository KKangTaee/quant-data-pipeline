from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from app.services.nyse_calendar import latest_completed_nyse_session


SCOPE_ORDER = ("asset_profile", "prices", "sec_identity", "sec_statements")
REASON_CODES = {
    "asset_profile": "PROFILE_PRICE_BASIS_MISALIGNED",
    "prices": "PRICE_BEHIND_COMPLETED_SESSION",
    "sec_identity": "SEC_IDENTITY_MISSING",
    "sec_statements": "STATEMENT_RAW_GAP",
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


def build_us_stock_data_freshness(
    symbol: str,
    *,
    per_model: Mapping[str, Any],
    turnaround_model: Mapping[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Combine DB-only PER and turnaround evidence into one repair action."""
    normalized = str(symbol or "").strip().upper()
    selection = dict(per_model.get("selection") or {})
    if not normalized or str(selection.get("symbol") or "").strip().upper() != normalized:
        return {
            "status": "BLOCKED",
            "reason_code": "IDENTITY_UNAVAILABLE",
            "reason": "선택 종목 identity를 확인한 뒤 최신성을 판정할 수 있습니다.",
            "expected_price_date": latest_completed_nyse_session(now).isoformat(),
            "price_basis_date": None,
            "profile_basis_date": None,
            "statement_period_end": None,
            "statement_available_at": None,
            "gaps": [],
        }
    coverage = dict(turnaround_model.get("coverage") or {})
    turnaround_plan = dict(turnaround_model.get("collection_plan") or {})
    per_action = dict(per_model.get("collection_action") or {})
    expected = latest_completed_nyse_session(now)
    price_basis = _as_date(
        selection.get("latest_price_date") or coverage.get("price_basis_date")
    )
    profile_basis = _as_date(coverage.get("profile_basis_date"))

    scopes = {
        str(scope)
        for scope in [
            *(turnaround_plan.get("scopes") or []),
            *(per_action.get("scopes") or []),
        ]
        if str(scope) in SCOPE_ORDER and str(scope) != "sec_identity"
    }
    if price_basis is None or price_basis < expected:
        scopes.add("prices")
    if (
        profile_basis is None
        or price_basis is None
        or abs((profile_basis - price_basis).days) > 7
    ):
        scopes.add("asset_profile")
    if coverage.get("statement_core_missing"):
        scopes.add("sec_statements")
    if "sec_statements" in scopes and not str(selection.get("cik") or "").strip():
        scopes.add("sec_identity")

    ordered_scopes = [scope for scope in SCOPE_ORDER if scope in scopes]
    gaps = [
        {
            "scope": scope,
            "reason_code": REASON_CODES[scope],
            "repairable": True,
        }
        for scope in ordered_scopes
    ]
    result: dict[str, Any] = {
        "status": "REFRESH_AVAILABLE" if ordered_scopes else "READY",
        "expected_price_date": expected.isoformat(),
        "price_basis_date": price_basis.isoformat() if price_basis else None,
        "profile_basis_date": profile_basis.isoformat() if profile_basis else None,
        "statement_period_end": coverage.get("statement_period_end"),
        "statement_available_at": coverage.get("statement_available_at"),
        "gaps": gaps,
    }
    if normalized and ordered_scopes:
        result["action"] = {
            "id": "refresh_us_stock_data",
            "label": "최신 데이터로 다시 계산",
            "detail": "선택 종목의 뒤처진 가격·시장가치와 실제 재무 원자료만 갱신합니다.",
            "symbol": normalized,
            "scopes": ordered_scopes,
            "enabled": True,
        }
    return result
