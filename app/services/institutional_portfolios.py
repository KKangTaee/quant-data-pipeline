from __future__ import annotations

from typing import Any

import pandas as pd

from finance.data.institutional_13f import SEC_13F_SOURCE_CAVEATS
from finance.loaders.institutional_13f import (
    load_institutional_13f_interest,
    load_institutional_13f_managers,
    load_institutional_13f_portfolio_bundle,
)


INSTITUTIONAL_PORTFOLIO_CAVEATS = [
    *SEC_13F_SOURCE_CAVEATS,
    "Change labels mean reported quarter-over-quarter differences, not current trading intent.",
]
CHANGE_ORDER = {
    "increased": 0,
    "reported_new": 1,
    "reduced": 2,
    "unchanged": 3,
    "no_longer_reported": 4,
}


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    return text


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _date_label(value: Any) -> str | None:
    if value is None:
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return _text(value)
    return parsed.date().isoformat()


def _records(frame: pd.DataFrame | None) -> list[dict[str, Any]]:
    if frame is None or frame.empty:
        return []
    work = frame.copy()
    work = work.where(pd.notna(work), None)
    return work.to_dict(orient="records")


def _holding_key(row: dict[str, Any]) -> str:
    cusip = _text(row.get("cusip"))
    put_call = _text(row.get("put_call")) or ""
    symbol = _text(row.get("holding_symbol")) or ""
    issuer = _text(row.get("issuer_name")) or ""
    if cusip:
        return f"cusip:{cusip}:{put_call}"
    if symbol:
        return f"symbol:{symbol}:{put_call}"
    return f"issuer:{issuer}:{put_call}"


def _prepared_holdings(frame: pd.DataFrame | None) -> tuple[list[dict[str, Any]], float]:
    rows = _records(frame)
    total_value = sum(_num(row.get("reported_value")) for row in rows)
    prepared: list[dict[str, Any]] = []
    for row in rows:
        value = _num(row.get("reported_value"))
        shares = _num(row.get("shares_or_principal_amount"))
        prepared.append(
            {
                "issuer_name": _text(row.get("issuer_name")) or "-",
                "holding_symbol": _text(row.get("holding_symbol")),
                "cusip": _text(row.get("cusip")),
                "figi": _text(row.get("figi")),
                "title_of_class": _text(row.get("title_of_class")),
                "reported_value": value,
                "shares_or_principal_amount": shares,
                "amount_type": _text(row.get("amount_type")),
                "put_call": _text(row.get("put_call")),
                "sector": _text(row.get("sector")),
                "industry": _text(row.get("industry")),
                "weight_pct": round((value / total_value) * 100.0, 4) if total_value > 0 else 0.0,
                "source_ref": _text(row.get("source_ref")),
            }
        )
    prepared.sort(key=lambda row: (row["reported_value"], row["issuer_name"]), reverse=True)
    return prepared, float(total_value)


def _change_type(latest: dict[str, Any], previous: dict[str, Any] | None) -> str:
    if previous is None:
        return "reported_new"
    latest_shares = _num(latest.get("shares_or_principal_amount"))
    previous_shares = _num(previous.get("shares_or_principal_amount"))
    latest_value = _num(latest.get("reported_value"))
    previous_value = _num(previous.get("reported_value"))
    if latest_shares > previous_shares or (latest_shares == previous_shares and latest_value > previous_value):
        return "increased"
    if latest_shares < previous_shares or (latest_shares == previous_shares and latest_value < previous_value):
        return "reduced"
    return "unchanged"


def _build_changes(latest_rows: list[dict[str, Any]], previous_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    previous_by_key = {_holding_key(row): row for row in previous_rows}
    latest_keys: set[str] = set()
    changes: list[dict[str, Any]] = []
    for latest in latest_rows:
        key = _holding_key(latest)
        latest_keys.add(key)
        previous = previous_by_key.get(key)
        change_type = _change_type(latest, previous)
        changes.append(
            {
                "change_type": change_type,
                "issuer_name": latest.get("issuer_name"),
                "holding_symbol": latest.get("holding_symbol"),
                "cusip": latest.get("cusip"),
                "latest_reported_value": latest.get("reported_value"),
                "previous_reported_value": previous.get("reported_value") if previous else None,
                "value_delta": round(_num(latest.get("reported_value")) - _num(previous.get("reported_value") if previous else 0.0), 4),
                "latest_shares_or_principal": latest.get("shares_or_principal_amount"),
                "previous_shares_or_principal": previous.get("shares_or_principal_amount") if previous else None,
                "share_delta": round(
                    _num(latest.get("shares_or_principal_amount"))
                    - _num(previous.get("shares_or_principal_amount") if previous else 0.0),
                    4,
                ),
                "weight_pct": latest.get("weight_pct"),
            }
        )

    for key, previous in previous_by_key.items():
        if key in latest_keys:
            continue
        changes.append(
            {
                "change_type": "no_longer_reported",
                "issuer_name": previous.get("issuer_name"),
                "holding_symbol": previous.get("holding_symbol"),
                "cusip": previous.get("cusip"),
                "latest_reported_value": None,
                "previous_reported_value": previous.get("reported_value"),
                "value_delta": -_num(previous.get("reported_value")),
                "latest_shares_or_principal": None,
                "previous_shares_or_principal": previous.get("shares_or_principal_amount"),
                "share_delta": -_num(previous.get("shares_or_principal_amount")),
                "weight_pct": None,
            }
        )

    changes.sort(key=lambda row: (CHANGE_ORDER.get(str(row.get("change_type")), 99), -abs(_num(row.get("value_delta")))))
    return changes


def _change_summary(changes: list[dict[str, Any]]) -> dict[str, int]:
    summary = {key: 0 for key in CHANGE_ORDER}
    for row in changes:
        change_type = str(row.get("change_type") or "")
        if change_type in summary:
            summary[change_type] += 1
    return summary


def _sector_exposure(holdings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_sector: dict[str, dict[str, Any]] = {}
    for row in holdings:
        sector = _text(row.get("sector")) or "Unmapped"
        bucket = by_sector.setdefault(sector, {"sector": sector, "reported_value": 0.0, "weight_pct": 0.0, "holding_count": 0})
        bucket["reported_value"] += _num(row.get("reported_value"))
        bucket["weight_pct"] += _num(row.get("weight_pct"))
        bucket["holding_count"] += 1
    out = list(by_sector.values())
    for row in out:
        row["reported_value"] = round(_num(row["reported_value"]), 4)
        row["weight_pct"] = round(_num(row["weight_pct"]), 4)
    out.sort(key=lambda row: row["weight_pct"], reverse=True)
    return out


def build_institutional_portfolio_model(
    *,
    manager: dict[str, Any] | None,
    latest_filing: dict[str, Any] | None,
    latest_holdings: pd.DataFrame | None,
    previous_filing: dict[str, Any] | None = None,
    previous_holdings: pd.DataFrame | None = None,
) -> dict[str, Any]:
    latest_rows, total_value = _prepared_holdings(latest_holdings)
    previous_rows, _ = _prepared_holdings(previous_holdings)
    changes = _build_changes(latest_rows, previous_rows)
    manager_name = _text((manager or {}).get("manager_name")) or _text((latest_filing or {}).get("manager_name")) or "Unknown manager"
    cik = _text((manager or {}).get("cik")) or _text((latest_filing or {}).get("cik"))
    return {
        "summary": {
            "manager_name": manager_name,
            "cik": cik,
            "latest_report_period": _date_label((latest_filing or {}).get("period_of_report")),
            "latest_filing_date": _date_label((latest_filing or {}).get("filing_date")),
            "previous_report_period": _date_label((previous_filing or {}).get("period_of_report")),
            "previous_filing_date": _date_label((previous_filing or {}).get("filing_date")),
            "accession_number": _text((latest_filing or {}).get("accession_number")),
            "source_ref": _text((latest_filing or {}).get("source_ref")),
            "total_reported_value": round(total_value, 4),
            "holding_count": len(latest_rows),
        },
        "holdings": latest_rows,
        "changes": changes,
        "change_summary": _change_summary(changes),
        "sector_exposure": _sector_exposure(latest_rows),
        "caveats": list(INSTITUTIONAL_PORTFOLIO_CAVEATS),
        "boundary": {
            "recommendation": False,
            "trade_signal": False,
            "live_trading": False,
            "registry_write": False,
            "saved_portfolio_write": False,
        },
    }


def build_institutional_interest_model(query: str, holder_rows: pd.DataFrame | None) -> dict[str, Any]:
    rows = _records(holder_rows)
    holders: list[dict[str, Any]] = []
    for row in rows:
        holders.append(
            {
                "manager_name": _text(row.get("manager_name")) or "Unknown manager",
                "cik": _text(row.get("cik")),
                "period_of_report": _date_label(row.get("period_of_report")),
                "filing_date": _date_label(row.get("filing_date")),
                "issuer_name": _text(row.get("issuer_name")),
                "holding_symbol": _text(row.get("holding_symbol")),
                "cusip": _text(row.get("cusip")),
                "reported_value": _num(row.get("reported_value")),
                "shares_or_principal_amount": _num(row.get("shares_or_principal_amount")),
                "weight_pct": round(_num(row.get("weight_pct")), 4),
                "source_ref": _text(row.get("source_ref")),
            }
        )
    holders.sort(key=lambda row: (row["weight_pct"], row["reported_value"]), reverse=True)
    return {
        "query": str(query or "").strip().upper(),
        "holder_count": len(holders),
        "holders": holders,
        "caveats": [
            "CUSIP-symbol mapping can be incomplete; confirm unmapped rows from original 13F filings.",
            "Institutional Interest is delayed reported ownership context, not live accumulation.",
            *INSTITUTIONAL_PORTFOLIO_CAVEATS,
        ],
    }


def load_institutional_manager_choices(query: str | None = None, *, limit: int = 100) -> dict[str, Any]:
    try:
        frame = load_institutional_13f_managers(query, limit=limit)
    except Exception as exc:
        return {"status": "error", "message": str(exc), "managers": []}
    return {"status": "ok", "message": "", "managers": _records(frame)}


def load_institutional_portfolio_model(cik: str) -> dict[str, Any]:
    try:
        bundle = load_institutional_13f_portfolio_bundle(cik)
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "model": build_institutional_portfolio_model(
                manager=None,
                latest_filing=None,
                latest_holdings=pd.DataFrame(),
            ),
        }
    model = build_institutional_portfolio_model(
        manager=bundle.get("manager"),
        latest_filing=bundle.get("latest_filing"),
        latest_holdings=bundle.get("latest_holdings"),
        previous_filing=bundle.get("previous_filing"),
        previous_holdings=bundle.get("previous_holdings"),
    )
    return {"status": "ok", "message": "", "model": model}


def load_institutional_interest_model(query: str, *, limit: int = 100) -> dict[str, Any]:
    try:
        rows = load_institutional_13f_interest(query, limit=limit)
    except Exception as exc:
        return {"status": "error", "message": str(exc), "model": build_institutional_interest_model(query, pd.DataFrame())}
    return {"status": "ok", "message": "", "model": build_institutional_interest_model(query, rows)}
