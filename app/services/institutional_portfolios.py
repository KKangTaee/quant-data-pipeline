from __future__ import annotations

import json
from typing import Any

import pandas as pd

from finance.data.institutional_13f import DEFAULT_SEC_13F_DATASET_LABEL, DEFAULT_SEC_13F_DATASET_URL, SEC_13F_SOURCE_CAVEATS
from finance.loaders.institutional_13f import (
    load_institutional_13f_interest,
    load_institutional_13f_managers,
    load_institutional_13f_portfolio_bundle,
    load_institutional_13f_refresh_status,
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
CHANGE_LABELS = {
    "reported_new": "Newly reported",
    "increased": "Increased",
    "reduced": "Reduced",
    "no_longer_reported": "No longer reported",
    "unchanged": "Unchanged",
}
CHANGE_DESCRIPTIONS = {
    "reported_new": "이번 보고서에 새로 등장한 보유 종목",
    "increased": "이전 보고 분기 대비 수량 또는 보고가치가 증가",
    "reduced": "이전 보고 분기 대비 수량 또는 보고가치가 감소",
    "no_longer_reported": "최신 보고서에는 더 이상 보이지 않는 종목",
    "unchanged": "주식 수와 보고가치 변화가 거의 없는 종목",
}
WORKBENCH_COLORS = [
    "#2563eb",
    "#14b8a6",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#22c55e",
    "#0ea5e9",
    "#f97316",
    "#64748b",
    "#d946ef",
    "#94a3b8",
]
INSTITUTIONAL_MANAGER_WATCHLIST = [
    {
        "cik": "0001067983",
        "manager_name": "BERKSHIRE HATHAWAY INC",
        "watchlist_label": "Warren Buffett",
        "priority": 10,
        "external_links": [{"label": "SEC filings", "url": "https://www.sec.gov/edgar/browse/?CIK=1067983"}],
    },
    {
        "cik": "0001336528",
        "manager_name": "PERSHING SQUARE CAPITAL MANAGEMENT, L.P.",
        "watchlist_label": "Bill Ackman",
        "priority": 20,
        "external_links": [{"label": "SEC filings", "url": "https://www.sec.gov/edgar/browse/?CIK=1336528"}],
    },
    {
        "cik": "0001656456",
        "manager_name": "APPALOOSA LP",
        "watchlist_label": "David Tepper",
        "priority": 30,
        "external_links": [{"label": "SEC filings", "url": "https://www.sec.gov/edgar/browse/?CIK=1656456"}],
    },
    {
        "cik": "0001061768",
        "manager_name": "BAUPOST GROUP LLC/MA",
        "watchlist_label": "Seth Klarman",
        "priority": 40,
        "external_links": [{"label": "SEC filings", "url": "https://www.sec.gov/edgar/browse/?CIK=1061768"}],
    },
]


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


def _money_label(value: Any) -> str:
    numeric = _num(value)
    if abs(numeric) >= 1_000_000_000:
        return f"{numeric / 1_000_000_000:.1f}B"
    if abs(numeric) >= 1_000_000:
        return f"{numeric / 1_000_000:.1f}M"
    if abs(numeric) >= 1_000:
        return f"{numeric / 1_000:.1f}K"
    return f"{numeric:,.0f}"


def _pct_label(value: Any) -> str:
    return f"{_num(value):.1f}%"


def _date_label(value: Any) -> str | None:
    if value is None:
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return _text(value)
    return parsed.date().isoformat()


def _cik_text(value: Any) -> str | None:
    text = str(value or "").strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(10)[-10:]


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


def build_institutional_manager_rail(managers: list[dict[str, Any]], selected_cik: str | None) -> list[dict[str, Any]]:
    """Merge stored manager search results with the curated watchlist rail."""
    selected = _cik_text(selected_cik)
    by_cik: dict[str, dict[str, Any]] = {}
    for row in managers:
        cik = _cik_text(row.get("cik"))
        if cik:
            by_cik[cik] = dict(row, cik=cik)

    items: list[dict[str, Any]] = []
    included: set[str] = set()
    for seed in sorted(INSTITUTIONAL_MANAGER_WATCHLIST, key=lambda row: int(row.get("priority") or 100)):
        cik = str(seed["cik"])
        row = {**seed, **by_cik.get(cik, {})}
        latest_period = _date_label(row.get("latest_report_period")) or _text(row.get("latest_report_period")) or "Collect 13F data"
        items.append(
            {
                "cik": cik,
                "manager_name": _text(row.get("manager_name")) or "Unknown manager",
                "latest_report_period": latest_period,
                "watchlist_label": _text(seed.get("watchlist_label")),
                "watchlist_priority": int(seed.get("priority") or 100),
                "external_links": list(seed.get("external_links") or []),
                "selected": bool(cik and selected and cik == selected),
            }
        )
        included.add(cik)

    for row in managers[:24]:
        cik = _cik_text(row.get("cik"))
        if not cik or cik in included:
            continue
        latest_period = _date_label(row.get("latest_report_period")) or _text(row.get("latest_report_period")) or "-"
        items.append(
            {
                "cik": cik,
                "manager_name": _text(row.get("manager_name")) or "Unknown manager",
                "latest_report_period": latest_period,
                "watchlist_label": None,
                "watchlist_priority": None,
                "external_links": [{"label": "SEC filings", "url": f"https://www.sec.gov/edgar/browse/?CIK={int(cik)}"}],
                "selected": bool(cik and selected and cik == selected),
            }
        )
    return items


def _manager_picker_items(managers: list[dict[str, Any]], selected_cik: str | None) -> list[dict[str, Any]]:
    return build_institutional_manager_rail(managers, selected_cik)[:24]


def _parse_source_limitations(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return [value]
        if isinstance(parsed, list):
            return [str(item) for item in parsed if item]
    return list(INSTITUTIONAL_PORTFOLIO_CAVEATS)


def build_institutional_refresh_status_model(row: dict[str, Any] | None = None, *, error_message: str | None = None) -> dict[str, Any]:
    source = dict(row or {})
    if not source:
        return {
            "source_key": "sec_form_13f_dataset",
            "source_dataset": None,
            "source_ref": None,
            "status": "missing",
            "last_collected_at": None,
            "latest_report_period": None,
            "latest_filing_date": None,
            "rows_written": 0,
            "managers_written": 0,
            "filings_written": 0,
            "holdings_written": 0,
            "is_stale": True,
            "stale_reason": error_message or "SEC Form 13F data has not been collected into the local DB yet.",
            "source_limitations": list(INSTITUTIONAL_PORTFOLIO_CAVEATS),
        }
    return {
        "source_key": _text(source.get("source_key")) or "sec_form_13f_dataset",
        "source_dataset": _text(source.get("source_dataset")),
        "source_ref": _text(source.get("source_ref")),
        "status": _text(source.get("status")) or "unknown",
        "last_collected_at": _text(source.get("last_collected_at")),
        "latest_report_period": _date_label(source.get("latest_report_period")),
        "latest_filing_date": _date_label(source.get("latest_filing_date")),
        "rows_written": int(_num(source.get("rows_written"))),
        "managers_written": int(_num(source.get("managers_written"))),
        "filings_written": int(_num(source.get("filings_written"))),
        "holdings_written": int(_num(source.get("holdings_written"))),
        "is_stale": bool(int(_num(source.get("is_stale"), 1.0))),
        "stale_reason": _text(source.get("stale_reason")) or error_message or "",
        "source_limitations": _parse_source_limitations(source.get("source_limitations_json")),
    }


def _refresh_action_payload() -> dict[str, Any]:
    return {
        "action_id": "collect_sec_13f_dataset",
        "label": "Refresh SEC 13F data",
        "primary": False,
        "description": "Runs the SEC official Form 13F dataset ingestion into MySQL; the UI only reads stored rows.",
        "default_dataset_label": DEFAULT_SEC_13F_DATASET_LABEL,
        "default_dataset_url": DEFAULT_SEC_13F_DATASET_URL,
    }


def _allocation_segments(holdings: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    visible = holdings[: max(1, limit)]
    segments: list[dict[str, Any]] = []
    for idx, row in enumerate(visible):
        symbol = _text(row.get("holding_symbol"))
        issuer = _text(row.get("issuer_name")) or "-"
        label = symbol or issuer
        segments.append(
            {
                "key": _text(row.get("cusip")) or symbol or issuer,
                "label": label,
                "symbol": symbol,
                "issuer_name": issuer,
                "weight_pct": round(_num(row.get("weight_pct")), 4),
                "weight_label": _pct_label(row.get("weight_pct")),
                "reported_value": _num(row.get("reported_value")),
                "value_label": _money_label(row.get("reported_value")),
                "color": WORKBENCH_COLORS[idx % len(WORKBENCH_COLORS)],
                "drilldown_query": symbol or _text(row.get("cusip")) or issuer,
            }
        )

    remaining = holdings[max(1, limit) :]
    other_weight = sum(_num(row.get("weight_pct")) for row in remaining)
    other_value = sum(_num(row.get("reported_value")) for row in remaining)
    if remaining and other_weight > 0:
        segments.append(
            {
                "key": "other",
                "label": "Other",
                "symbol": None,
                "issuer_name": f"{len(remaining)} remaining holdings",
                "weight_pct": round(other_weight, 4),
                "weight_label": _pct_label(other_weight),
                "reported_value": round(other_value, 4),
                "value_label": _money_label(other_value),
                "color": WORKBENCH_COLORS[-1],
                "drilldown_query": "",
            }
        )
    return segments


def _top_holding_rows(holdings: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(holdings[:limit]):
        symbol = _text(row.get("holding_symbol"))
        issuer = _text(row.get("issuer_name")) or "-"
        rows.append(
            {
                "key": _text(row.get("cusip")) or symbol or issuer,
                "rank": idx + 1,
                "symbol": symbol,
                "issuer_name": issuer,
                "label": symbol or issuer,
                "cusip": _text(row.get("cusip")),
                "sector": _text(row.get("sector")) or "Unmapped",
                "weight_pct": round(_num(row.get("weight_pct")), 4),
                "weight_label": _pct_label(row.get("weight_pct")),
                "reported_value": _num(row.get("reported_value")),
                "value_label": _money_label(row.get("reported_value")),
                "drilldown_query": symbol or _text(row.get("cusip")) or issuer,
                "color": WORKBENCH_COLORS[idx % len(WORKBENCH_COLORS)],
            }
        )
    return rows


def _change_groups(changes: list[dict[str, Any]], *, limit: int) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for change_type in ["reported_new", "increased", "reduced", "no_longer_reported"]:
        rows = [row for row in changes if row.get("change_type") == change_type]
        groups[change_type] = {
            "label": CHANGE_LABELS[change_type],
            "description": CHANGE_DESCRIPTIONS[change_type],
            "count": len(rows),
            "items": [
                {
                    "label": _text(row.get("holding_symbol")) or _text(row.get("issuer_name")) or "-",
                    "issuer_name": _text(row.get("issuer_name")) or "-",
                    "symbol": _text(row.get("holding_symbol")),
                    "weight_label": _pct_label(row.get("weight_pct")),
                    "value_delta": _num(row.get("value_delta")),
                    "value_delta_label": _money_label(row.get("value_delta")),
                    "drilldown_query": _text(row.get("holding_symbol")) or _text(row.get("cusip")) or _text(row.get("issuer_name")) or "",
                }
                for row in rows[:limit]
            ],
        }
    return groups


def _sector_bars(exposure: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    max_weight = max((_num(row.get("weight_pct")) for row in exposure), default=0.0)
    bars: list[dict[str, Any]] = []
    for idx, row in enumerate(exposure[:limit]):
        weight = _num(row.get("weight_pct"))
        bars.append(
            {
                "sector": _text(row.get("sector")) or "Unmapped",
                "weight_pct": round(weight, 4),
                "weight_label": _pct_label(weight),
                "reported_value": _num(row.get("reported_value")),
                "value_label": _money_label(row.get("reported_value")),
                "holding_count": int(_num(row.get("holding_count"))),
                "bar_width_pct": round((weight / max_weight) * 100.0, 2) if max_weight > 0 else 0.0,
                "color": WORKBENCH_COLORS[idx % len(WORKBENCH_COLORS)],
            }
        )
    return bars


def _workbench_holdings_rows(holdings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "issuer_name": row.get("issuer_name"),
            "symbol": row.get("holding_symbol"),
            "cusip": row.get("cusip"),
            "sector": row.get("sector") or "Unmapped",
            "industry": row.get("industry"),
            "weight_pct": row.get("weight_pct"),
            "weight_label": _pct_label(row.get("weight_pct")),
            "reported_value": row.get("reported_value"),
            "value_label": _money_label(row.get("reported_value")),
            "shares_or_principal_amount": row.get("shares_or_principal_amount"),
            "drilldown_query": row.get("holding_symbol") or row.get("cusip") or row.get("issuer_name"),
        }
        for row in holdings
    ]


def _interest_payload(interest_model: dict[str, Any] | None) -> dict[str, Any]:
    model = dict(interest_model or {})
    holders = [
        {
            "manager_name": row.get("manager_name"),
            "cik": row.get("cik"),
            "period_of_report": row.get("period_of_report"),
            "filing_date": row.get("filing_date"),
            "issuer_name": row.get("issuer_name"),
            "symbol": row.get("holding_symbol"),
            "cusip": row.get("cusip"),
            "weight_label": _pct_label(row.get("weight_pct")),
            "reported_value": row.get("reported_value"),
            "value_label": _money_label(row.get("reported_value")),
            "source_ref": row.get("source_ref"),
        }
        for row in list(model.get("holders") or [])[:50]
    ]
    return {
        "query": model.get("query") or "",
        "holder_count": int(model.get("holder_count") or len(holders)),
        "holders": holders,
        "empty_text": "종목을 클릭하거나 검색하면 최신 저장 13F 기준 보유 기관을 보여줍니다.",
    }


def build_institutional_workbench_payload(
    *,
    model: dict[str, Any],
    managers: list[dict[str, Any]] | None,
    selected_cik: str | None,
    interest_model: dict[str, Any] | None,
    mode: str = "live",
    data_message: str = "",
    refresh_status: dict[str, Any] | None = None,
    allocation_limit: int = 10,
    row_limit: int = 12,
) -> dict[str, Any]:
    summary = dict(model.get("summary") or {})
    holdings = list(model.get("holdings") or [])
    changes = list(model.get("changes") or [])
    sector_exposure = list(model.get("sector_exposure") or [])
    manager_name = _text(summary.get("manager_name")) or "Unknown manager"
    report_period = _text(summary.get("latest_report_period")) or "-"
    previous_period = _text(summary.get("previous_report_period")) or "-"
    filing_date = _text(summary.get("latest_filing_date")) or "-"
    total_value = _num(summary.get("total_reported_value"))
    is_preview = mode == "preview"
    freshness = build_institutional_refresh_status_model(refresh_status)
    data_state_label = "Preview sample" if is_preview else "Stored SEC 13F snapshot"
    data_state_message = data_message or (
        "샘플 데이터입니다. 실제 13F 수집 후 저장 DB 기준 화면으로 바뀝니다."
        if is_preview
        else "SEC Form 13F 저장 snapshot 기준입니다. 최신 거래 의도가 아닙니다."
    )

    return {
        "schema_version": "institutional_portfolios_workbench_v1",
        "component": "InstitutionalPortfoliosWorkbench",
        "mode": mode,
        "data_state": {
            "label": data_state_label,
            "message": data_state_message,
            "is_preview": is_preview,
            "as_of_label": report_period,
        },
        "manager_picker": {
            "selected_cik": selected_cik,
            "items": _manager_picker_items(list(managers or []), selected_cik),
        },
        "freshness": freshness,
        "refresh_action": _refresh_action_payload(),
        "hero": {
            "manager_name": manager_name,
            "cik": _text(summary.get("cik")) or selected_cik,
            "latest_report_period": report_period,
            "latest_filing_date": filing_date,
            "previous_report_period": previous_period,
            "total_reported_value": total_value,
            "total_reported_value_label": _money_label(total_value),
            "holding_count": int(_num(summary.get("holding_count"))),
            "source_ref": _text(summary.get("source_ref")),
            "facts": [
                {"label": "Report period", "value": report_period},
                {"label": "Filing date", "value": filing_date},
                {"label": "Data refreshed", "value": freshness.get("last_collected_at") or "Not collected"},
                {"label": "Holdings", "value": f"{int(_num(summary.get('holding_count'))):,}"},
                {"label": "Reported value", "value": _money_label(total_value)},
            ],
            "caveat": "13F는 분기 지연 자료이며 실시간 매수/매도 신호가 아닙니다.",
        },
        "allocation": {
            "title": "Portfolio Allocation",
            "subtitle": "Top holdings by reported value, grouped with Other for scanability.",
            "total_label": _money_label(total_value),
            "segments": _allocation_segments(holdings, limit=allocation_limit),
            "top_holdings": _top_holding_rows(holdings, limit=row_limit),
        },
        "change_board": {
            "title": "Reported Quarter Changes",
            "subtitle": f"{previous_period} -> {report_period}",
            "groups": _change_groups(changes, limit=5),
        },
        "sector_exposure": {
            "title": "Sector Exposure",
            "subtitle": "Best-effort sector mapping from stored symbol metadata.",
            "bars": _sector_bars(sector_exposure, limit=8),
        },
        "holdings_table": {
            "columns": ["issuer_name", "symbol", "weight_label", "value_label", "sector", "cusip"],
            "rows": _workbench_holdings_rows(holdings),
        },
        "interest": _interest_payload(interest_model),
        "source_caveats": {
            "visible": True,
            "items": list(model.get("caveats") or INSTITUTIONAL_PORTFOLIO_CAVEATS),
        },
        "boundary": dict(
            model.get("boundary")
            or {
                "recommendation": False,
                "trade_signal": False,
                "live_trading": False,
                "registry_write": False,
                "saved_portfolio_write": False,
            }
        ),
    }


def build_institutional_preview_workbench_payload(message: str = "") -> dict[str, Any]:
    preview_model = build_institutional_portfolio_model(
        manager={"cik": "PREVIEW", "manager_name": "Sample Superinvestor Portfolio"},
        latest_filing={
            "period_of_report": "Sample quarter",
            "filing_date": "Not filed",
            "source_ref": None,
        },
        latest_holdings=pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 44000,
                    "shares_or_principal_amount": 100,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
                {
                    "cusip": "060505104",
                    "holding_symbol": "BAC",
                    "issuer_name": "BANK OF AMERICA CORP",
                    "reported_value": 32000,
                    "shares_or_principal_amount": 100,
                    "sector": "Financial Services",
                    "industry": "Banks",
                },
                {
                    "cusip": "023135106",
                    "holding_symbol": "AMZN",
                    "issuer_name": "AMAZON COM INC",
                    "reported_value": 16000,
                    "shares_or_principal_amount": 50,
                    "sector": "Consumer Cyclical",
                    "industry": "Internet Retail",
                },
                {
                    "cusip": "594918104",
                    "holding_symbol": "MSFT",
                    "issuer_name": "MICROSOFT CORP",
                    "reported_value": 8000,
                    "shares_or_principal_amount": 30,
                    "sector": "Technology",
                    "industry": "Software",
                },
            ]
        ),
        previous_filing={"period_of_report": "Previous sample quarter", "filing_date": "Not filed"},
        previous_holdings=pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 40000,
                    "shares_or_principal_amount": 95,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
                {
                    "cusip": "060505104",
                    "holding_symbol": "BAC",
                    "issuer_name": "BANK OF AMERICA CORP",
                    "reported_value": 34000,
                    "shares_or_principal_amount": 120,
                    "sector": "Financial Services",
                    "industry": "Banks",
                },
                {
                    "cusip": "459200101",
                    "holding_symbol": "IBM",
                    "issuer_name": "IBM",
                    "reported_value": 5000,
                    "shares_or_principal_amount": 20,
                    "sector": "Technology",
                    "industry": "IT Services",
                },
            ]
        ),
    )
    payload = build_institutional_workbench_payload(
        model=preview_model,
        managers=[
            {"cik": "PREVIEW", "manager_name": "Sample Superinvestor Portfolio", "latest_report_period": "Sample"},
            {"cik": "0001067983", "manager_name": "Berkshire Hathaway", "latest_report_period": "after SEC load"},
            {"cik": "0001336528", "manager_name": "Pershing Square", "latest_report_period": "after SEC load"},
        ],
        selected_cik="PREVIEW",
        interest_model=None,
        mode="preview",
        data_message=message or "Local 13F DB is empty. This preview shows the intended visual layout, not live or current holdings.",
        allocation_limit=3,
    )
    payload["data_state"]["label"] = "Preview sample - not live data"
    return payload


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


def load_institutional_refresh_status() -> dict[str, Any]:
    try:
        row = load_institutional_13f_refresh_status()
    except Exception as exc:
        return {"status": "error", "message": str(exc), "model": build_institutional_refresh_status_model(error_message=str(exc))}
    return {"status": "ok", "message": "", "model": build_institutional_refresh_status_model(row)}


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
