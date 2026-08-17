from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

import pandas as pd

from finance.loaders.institutional_13f import load_institutional_13f_effective_history
from finance.loaders.price import load_price_history


_CHANGE_SORT = {"NEW": 0, "ADD": 1, "REDUCE": 2, "DROP": 3, "KEEP": 4, "NOT_COMPARABLE": 5}


def _text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _number(value: Any) -> float | None:
    parsed = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return None if pd.isna(parsed) else float(parsed)


def _records(frame: pd.DataFrame | None) -> list[dict[str, Any]]:
    if frame is None or frame.empty:
        return []
    return frame.where(pd.notna(frame), None).to_dict(orient="records")


def _position_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _text(row.get("cusip")).upper(),
        _text(row.get("title_of_class")).upper(),
        _text(row.get("put_call")).upper(),
        _text(row.get("amount_type")).upper(),
    )


def _aggregate_positions(frame: pd.DataFrame | None) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in _records(frame):
        key = _position_key(row)
        if key[0]:
            grouped[key].append(row)

    out: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for key, rows in grouped.items():
        amounts = [_number(row.get("shares_or_principal_amount")) for row in rows]
        values = [_number(row.get("reported_value")) for row in rows]
        first = rows[0]
        out[key] = {
            "cusip": key[0],
            "title_of_class": key[1],
            "put_call": key[2],
            "amount_type": key[3],
            "issuer_name": next((_text(row.get("issuer_name")) for row in rows if _text(row.get("issuer_name"))), ""),
            "holding_symbol": next(
                (_text(row.get("holding_symbol")).upper() for row in rows if _text(row.get("holding_symbol"))),
                "",
            ),
            "sector": next((_text(row.get("sector")) for row in rows if _text(row.get("sector"))), ""),
            "mapping_status": next(
                (_text(row.get("mapping_status")) for row in rows if _text(row.get("mapping_status"))),
                "",
            ),
            "amount": sum(value for value in amounts if value is not None) if all(value is not None for value in amounts) else None,
            "reported_value": sum(value for value in values if value is not None) if any(value is not None for value in values) else None,
            "source_ref": _text(first.get("source_ref")),
        }
    return out


def build_institutional_position_changes(
    previous_holdings: pd.DataFrame | None,
    current_holdings: pd.DataFrame | None,
) -> list[dict[str, Any]]:
    """Classify reported position changes from share/principal amounts, never market value alone."""

    previous = _aggregate_positions(previous_holdings)
    current = _aggregate_positions(current_holdings)
    previous_total = sum(max(0.0, row.get("reported_value") or 0.0) for row in previous.values())
    current_total = sum(max(0.0, row.get("reported_value") or 0.0) for row in current.values())
    changes: list[dict[str, Any]] = []
    for key in sorted(set(previous) | set(current)):
        before = previous.get(key)
        after = current.get(key)
        if before is None:
            change_type = "NEW"
        elif after is None:
            change_type = "DROP"
        elif before["amount"] is None or after["amount"] is None:
            change_type = "NOT_COMPARABLE"
        elif after["amount"] > before["amount"]:
            change_type = "ADD"
        elif after["amount"] < before["amount"]:
            change_type = "REDUCE"
        else:
            change_type = "KEEP"
        representative = after or before or {}
        previous_value = before.get("reported_value") if before else None
        current_value = after.get("reported_value") if after else None
        changes.append(
            {
                "cusip": key[0],
                "title_of_class": key[1],
                "put_call": key[2],
                "amount_type": key[3],
                "issuer_name": representative.get("issuer_name") or "",
                "holding_symbol": representative.get("holding_symbol") or "",
                "sector": representative.get("sector") or "",
                "mapping_status": representative.get("mapping_status") or "",
                "change_type": change_type,
                "previous_amount": before.get("amount") if before else None,
                "current_amount": after.get("amount") if after else None,
                "amount_delta": (
                    after["amount"] - before["amount"]
                    if before and after and before["amount"] is not None and after["amount"] is not None
                    else None
                ),
                "previous_reported_value": previous_value,
                "current_reported_value": current_value,
                "previous_weight_pct": round((previous_value or 0.0) / previous_total * 100.0, 4) if previous_total else 0.0,
                "current_weight_pct": round((current_value or 0.0) / current_total * 100.0, 4) if current_total else 0.0,
            }
        )
    return sorted(
        changes,
        key=lambda row: (
            -float(row["previous_weight_pct"]),
            -float(row["current_weight_pct"]),
            _CHANGE_SORT[row["change_type"]],
            row["cusip"],
            row["put_call"],
        ),
    )


def _coverage_status(coverage_weight_pct: float) -> str:
    if coverage_weight_pct >= 80.0:
        return "READY"
    if coverage_weight_pct >= 50.0:
        return "LIMITED"
    return "NOT_AVAILABLE"


def _is_common_equity_position(position: dict[str, Any]) -> bool:
    amount_type = _text(position.get("amount_type")).upper()
    title = _text(position.get("title_of_class")).upper()
    non_common_tokens = ("PRN", "NOTE", "BOND", "DEBT", "PFD", "PREF", "CONV")
    return amount_type == "SH" and not any(token in title for token in non_common_tokens)


def build_institutional_price_proxy(
    holdings: pd.DataFrame | None,
    price_history: pd.DataFrame | None,
    *,
    start_date: str,
    end_date: str,
    proxy_id: str,
) -> dict[str, Any]:
    """Calculate a covered-sleeve long-holdings price proxy with explicit missing weight."""

    positions = _aggregate_positions(holdings)
    total_value = sum(max(0.0, row.get("reported_value") or 0.0) for row in positions.values())
    prices = price_history.copy() if isinstance(price_history, pd.DataFrame) else pd.DataFrame()
    if not prices.empty:
        prices["symbol"] = prices["symbol"].astype(str).str.upper()
        prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
        prices["adj_close"] = pd.to_numeric(prices.get("adj_close"), errors="coerce")
        prices = prices.dropna(subset=["symbol", "date"])
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    rows: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    covered_value = 0.0

    for position in positions.values():
        reported_value = max(0.0, position.get("reported_value") or 0.0)
        weight_pct = (reported_value / total_value * 100.0) if total_value else 0.0
        symbol = _text(position.get("holding_symbol")).upper()
        if position.get("put_call"):
            missing.append({**position, "weight_pct": round(weight_pct, 4), "reason": "option_excluded"})
            continue
        if not _is_common_equity_position(position):
            missing.append({**position, "weight_pct": round(weight_pct, 4), "reason": "non_common_instrument"})
            continue
        if not symbol:
            missing.append({**position, "weight_pct": round(weight_pct, 4), "reason": "unmapped_identifier"})
            continue
        symbol_prices = prices[prices["symbol"] == symbol].sort_values("date") if not prices.empty else pd.DataFrame()
        start_rows = symbol_prices[symbol_prices["date"] >= start_ts] if not symbol_prices.empty else pd.DataFrame()
        end_rows = symbol_prices[symbol_prices["date"] <= end_ts] if not symbol_prices.empty else pd.DataFrame()
        if start_rows.empty or end_rows.empty:
            missing.append({**position, "weight_pct": round(weight_pct, 4), "reason": "price_boundary_unavailable"})
            continue
        start_row = start_rows.iloc[0]
        end_row = end_rows.iloc[-1]
        if pd.isna(start_row.get("adj_close")) or pd.isna(end_row.get("adj_close")):
            missing.append({**position, "weight_pct": round(weight_pct, 4), "reason": "adjusted_price_unavailable"})
            continue
        start_price = float(start_row["adj_close"])
        end_price = float(end_row["adj_close"])
        if end_row["date"] < start_row["date"] or start_price <= 0:
            missing.append({**position, "weight_pct": round(weight_pct, 4), "reason": "price_boundary_unavailable"})
            continue
        return_pct = (end_price / start_price - 1.0) * 100.0
        contribution_pct = weight_pct * return_pct / 100.0
        covered_value += reported_value
        rows.append(
            {
                "cusip": position["cusip"],
                "holding_symbol": symbol,
                "issuer_name": position.get("issuer_name") or symbol,
                "weight_pct": round(weight_pct, 4),
                "start_date": start_row["date"].date().isoformat(),
                "end_date": end_row["date"].date().isoformat(),
                "start_price": round(start_price, 4),
                "end_price": round(end_price, 4),
                "return_pct": round(return_pct, 4),
                "contribution_pct": round(contribution_pct, 4),
            }
        )

    coverage_pct = covered_value / total_value * 100.0 if total_value else 0.0
    contribution_sum = sum(row["contribution_pct"] for row in rows)
    covered_return = contribution_sum * 100.0 / coverage_pct if coverage_pct else None
    rows.sort(key=lambda row: row["weight_pct"], reverse=True)
    return {
        "proxy_id": proxy_id,
        "status": _coverage_status(coverage_pct),
        "start_date": start_date,
        "end_date": end_date,
        "coverage_weight_pct": round(coverage_pct, 4),
        "missing_weight_pct": round(max(0.0, 100.0 - coverage_pct), 4),
        "covered_sleeve_return_pct": round(covered_return, 4) if covered_return is not None else None,
        "price_basis": "adjusted_close_total_return_when_available",
        "rows": rows,
        "missing_positions": sorted(missing, key=lambda row: row["weight_pct"], reverse=True),
        "top_contributors": sorted(rows, key=lambda row: row["contribution_pct"], reverse=True)[:5],
        "top_detractors": sorted(rows, key=lambda row: row["contribution_pct"])[:5],
        "caveat": "Adjusted-close common-equity proxy; dividends and splits follow the stored adjusted series. Missing or non-common holdings are excluded, never assigned a zero return.",
    }


def build_institutional_quarter_review(
    *,
    previous_effective: dict[str, Any] | None,
    current_effective: dict[str, Any] | None,
    price_history: pd.DataFrame | None,
) -> dict[str, Any]:
    """Build one previous-to-current 13F transition with two distinct price proxies."""

    if not previous_effective or not previous_effective.get("available"):
        return {
            "available": False,
            "reason": "비교할 이전 보고 분기가 저장되어 있지 않습니다.",
            "transition": {},
            "change_summary": {},
            "changes": [],
            "proxies": {},
        }
    if not current_effective or not current_effective.get("available"):
        return {
            "available": False,
            "reason": "비교할 최신 유효 보고 분기를 구성할 수 없습니다.",
            "transition": {},
            "change_summary": {},
            "changes": [],
            "proxies": {},
        }

    previous_filing = dict(previous_effective.get("filing") or {})
    current_filing = dict(current_effective.get("filing") or {})
    required_dates = {
        "previous_report_period": _text(previous_filing.get("period_of_report")),
        "current_report_period": _text(current_filing.get("period_of_report")),
        "previous_filing_date": _text(previous_filing.get("filing_date")),
        "current_filing_date": _text(current_filing.get("filing_date")),
    }
    if not all(required_dates.values()):
        return {
            "available": False,
            "reason": "두 보고 분기의 기준일 또는 제출일이 완전하지 않습니다.",
            "transition": required_dates,
            "change_summary": {},
            "changes": [],
            "proxies": {},
        }

    previous_holdings = previous_effective.get("holdings")
    current_holdings = current_effective.get("holdings")
    changes = build_institutional_position_changes(previous_holdings, current_holdings)
    quarter_proxy = build_institutional_price_proxy(
        previous_holdings,
        price_history,
        start_date=required_dates["previous_report_period"],
        end_date=required_dates["current_report_period"],
        proxy_id="quarter_holdings_proxy",
    )
    public_proxy = build_institutional_price_proxy(
        previous_holdings,
        price_history,
        start_date=required_dates["previous_filing_date"],
        end_date=required_dates["current_filing_date"],
        proxy_id="public_follow_proxy",
    )
    quarter_evidence = {row["cusip"]: row for row in quarter_proxy["rows"]}
    for change in changes:
        evidence = quarter_evidence.get(change["cusip"]) if not change.get("put_call") else None
        change["symbol_return_pct"] = evidence.get("return_pct") if evidence else None
        change["contribution_pct"] = evidence.get("contribution_pct") if evidence else None

    change_summary = {label: 0 for label in _CHANGE_SORT}
    for change in changes:
        change_summary[change["change_type"]] += 1
    return {
        "available": True,
        "reason": "",
        "manager": dict(current_effective.get("manager") or {}),
        "transition": {
            **required_dates,
            "previous_source_accessions": list(previous_effective.get("source_accessions") or []),
            "current_source_accessions": list(current_effective.get("source_accessions") or []),
        },
        "change_summary": change_summary,
        "changes": changes,
        "proxies": {
            "quarter_holdings_proxy": quarter_proxy,
            "public_follow_proxy": public_proxy,
        },
        "caveat": (
            "13F reported-long-holdings proxy only; it excludes intra-quarter trades, cash, shorts, "
            "many derivatives, fees, and hedge structure."
        ),
    }


def load_institutional_quarter_review_model(cik: str) -> dict[str, Any]:
    """Load saved effective transitions and one combined stored-price window."""

    history = load_institutional_13f_effective_history(cik, limit=8)
    available = [row for row in history if row.get("available")]
    if len(available) < 2:
        return build_institutional_quarter_review(
            previous_effective=None,
            current_effective=available[0] if available else None,
            price_history=pd.DataFrame(),
        )

    date_candidates: list[str] = []
    for effective in available:
        filing = dict(effective.get("filing") or {})
        date_candidates.extend(
            [_text(filing.get("period_of_report")), _text(filing.get("filing_date"))]
        )
    present_dates = [value for value in date_candidates if value]
    previous_positions = [
        _aggregate_positions(effective.get("holdings"))
        for effective in available[1:]
    ]
    symbols = sorted(
        {
            _text(row.get("holding_symbol")).upper()
            for positions in previous_positions
            for row in positions.values()
            if _text(row.get("holding_symbol"))
            and not row.get("put_call")
            and _is_common_equity_position(row)
        }
    )
    prices = pd.DataFrame()
    if symbols and present_dates:
        prices = load_price_history(
            symbols=symbols,
            start=min(present_dates),
            end=max(present_dates),
            timeframe="1d",
        )
    transitions = [
        build_institutional_quarter_review(
            previous_effective=available[index + 1],
            current_effective=available[index],
            price_history=prices,
        )
        for index in range(len(available) - 1)
    ]
    latest = dict(transitions[0])
    latest["transitions"] = transitions
    return latest
