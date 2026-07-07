from __future__ import annotations

import json

import os

import re

import urllib.request

from collections import Counter
from collections.abc import Callable, Sequence

from datetime import date, datetime, timezone, timedelta

from html import unescape

from typing import Any

from urllib.parse import quote, quote_plus, urlencode, urlparse

from xml.etree import ElementTree

import pandas as pd

from finance.loaders.sentiment import (
    CNN_COMPONENT_SERIES,
    CORE_SENTIMENT_SERIES,
    load_market_sentiment_history,
    load_market_sentiment_snapshot,
)

QueryFn = Callable[[str, str, Sequence[Any] | None], list[dict[str, Any]]]

EVENT_ESTIMATE_STALE_DAYS = 14

EVENT_RECENT_WINDOW_DAYS = 7

MAJOR_MACRO_EVENT_TYPES = {
    "FOMC_MEETING",
    "MACRO_CPI",
    "MACRO_PPI",
    "MACRO_EMPLOYMENT",
    "MACRO_GDP",
    "MACRO_JOLTS",
    "MACRO_ECI",
    "MACRO_PCE",
    "MACRO_RETAIL_SALES",
    "MACRO_DURABLE_GOODS",
    "MACRO_HOUSING",
    "MACRO_CONSTRUCTION_SPENDING",
    "MACRO_TRADE",
    "MACRO_ISM_MANUFACTURING_PMI",
    "MACRO_ISM_SERVICES_PMI",
    "TREASURY_AUCTION",
}

EVENT_TAXONOMY = {
    "event_families": [
        "central_bank",
        "macro",
        "earnings",
        "fixed_income",
        "market_structure",
        "corporate_action",
        "other",
    ],
    "source_authorities": [
        "official",
        "issuer_confirmed",
        "provider_estimate",
        "cross_checked",
        "not_confirmed",
        "conflict",
        "unknown",
    ],
    "universe_scopes": [
        "official_macro",
        "all_us",
        "sp500",
        "nasdaq100",
        "portfolio",
        "watchlist",
        "latest_movers",
        "major_cap",
        "unknown",
    ],
}

EVENT_FAMILY_LABELS_KO = {
    "all": "전체",
    "central_bank": "FOMC",
    "macro": "매크로",
    "earnings": "실적",
    "fixed_income": "국채 / 금리",
    "market_structure": "시장 구조",
    "corporate_action": "기업 이벤트",
    "other": "기타",
    "unknown": "미분류",
}

EVENT_SOURCE_STATE_LABELS_KO = {
    "all": "전체",
    "review": "확인 필요",
    "official": "공식 / 확인됨",
    "estimate": "추정 / 미확정",
}

EVENT_SOURCE_AUTHORITY_LABELS_KO = {
    "official": "공식 일정",
    "issuer_confirmed": "기업 확인",
    "provider_estimate": "제공사 추정",
    "cross_checked": "교차 확인",
    "not_confirmed": "미확정",
    "conflict": "충돌",
    "unknown": "출처 미확인",
}

EVENT_UNIVERSE_SCOPE_LABELS_KO = {
    "official_macro": "공식 매크로",
    "all_us": "미국 시장 전체",
    "sp500": "S&P 500",
    "nasdaq100": "Nasdaq-100",
    "portfolio": "포트폴리오",
    "watchlist": "관심목록",
    "latest_movers": "최근 Movers",
    "major_cap": "대형주",
    "unknown": "범위 미확인",
}

EVENT_VALIDATION_LABELS_KO = {
    "official": "공식 일정",
    "estimate_only": "추정만 있음",
    "cross_checked": "교차 확인",
    "not_confirmed": "미확정",
    "conflict": "일정 충돌",
    "unknown": "확인 상태 미상",
}

EVENT_FRESHNESS_LABELS_KO = {
    "official": "공식 일정",
    "current_estimate": "최근 추정",
    "stale_estimate": "오래된 추정",
    "estimate_age_unknown": "추정 수집일 미상",
    "current_source": "최근 수집",
    "stale_source": "오래된 수집",
    "collection_age_unknown": "수집일 미상",
    "superseded": "대체된 일정",
}

MARKET_STRUCTURE_EVENT_TYPES = {
    "MARKET_HOLIDAY",
    "TRADING_HOLIDAY",
    "EXCHANGE_HOLIDAY",
    "EARLY_CLOSE",
    "OPTIONS_EXPIRATION",
    "OPEX",
    "INDEX_REBALANCE",
    "RUSSELL_RECONSTITUTION",
    "SP500_REBALANCE",
    "NASDAQ100_RECONSTITUTION",
}

CORPORATE_ACTION_EVENT_TYPES = {
    "DIVIDEND",
    "SPLIT",
    "STOCK_SPLIT",
    "IPO",
    "SPO",
    "INVESTOR_DAY",
}

FIXED_INCOME_EVENT_TYPES = {
    "TREASURY_AUCTION",
    "TREASURY_REFUNDING",
}

EVENT_COLUMNS = [
    "Date",
    "Days Until",
    "Window",
    "Type",
    "Event Family",
    "Event Subtype",
    "Universe Scope",
    "Source Authority",
    "Event Time",
    "Event Datetime UTC",
    "Symbol",
    "Title",
    "Importance",
    "Focus",
    "Source Type",
    "Validation",
    "Freshness",
    "Quality Action",
    "Event Status",
    "Age Days",
    "Source",
    "Confidence",
    "Collected At",
    "Source URL",
]

def _default_query(db_name: str, sql: str, params: Sequence[Any] | None = None) -> list[dict[str, Any]]:
    import pymysql

    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        port=3306,
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cur.execute(f"USE {db_name}")
            cur.execute(sql, params)
            return list(cur.fetchall())
    finally:
        conn.close()

def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric

def _normalize_taxonomy_value(value: Any) -> str | None:
    normalized = str(value or "").strip().lower().replace(" ", "_")
    return normalized or None

def _iso_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d")

def _display_datetime(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d %H:%M")

def _normalize_limit(value: int, *, default: int, min_value: int, max_value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(min_value, min(parsed, max_value))

def _empty_events_snapshot(
    *,
    status: str,
    start_date: str,
    end_date: str,
    event_type: str | None,
    message: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "event_type": event_type or "All",
        "rows": pd.DataFrame(columns=EVENT_COLUMNS),
        "date_window": {"start_date": start_date, "end_date": end_date},
        "coverage": {
            "event_count": 0,
            "next_event_date": None,
            "latest_recent_event_date": None,
            "latest_collected_at": None,
            "source_count": 0,
            "official_count": 0,
            "estimate_count": 0,
            "estimate_only_count": 0,
            "cross_checked_count": 0,
            "not_confirmed_count": 0,
            "stale_estimate_count": 0,
            "action_required_count": 0,
            "high_importance_count": 0,
            "needs_review_count": 0,
            "this_week_count": 0,
            "next_30d_count": 0,
            "recent_event_count": 0,
            "upcoming_event_count": 0,
            "recent_high_importance_count": 0,
            "upcoming_high_importance_count": 0,
            "superseded_count": 0,
            "family_counts": {},
            "source_authority_counts": {},
            "universe_scope_counts": {},
        },
        "schema_version": "market_events_snapshot_v2",
        "taxonomy": EVENT_TAXONOMY,
        "warnings": [message] if message else [],
    }

def _normalize_event_type_value(value: str | None) -> str | None:
    normalized = str(value or "").strip().upper().replace(" ", "_")
    return normalized or None

def _raw_payload(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("raw_payload_json")
    if isinstance(value, dict):
        return value
    if value in (None, ""):
        return {}
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}

def _event_family(row: dict[str, Any]) -> str:
    persisted = _normalize_taxonomy_value(row.get("event_family"))
    if persisted in EVENT_TAXONOMY["event_families"]:
        return persisted
    event_type = _normalize_event_type_value(row.get("event_type"))
    if event_type in {"FOMC_MEETING", "FOMC"}:
        return "central_bank"
    if event_type == "MACRO" or str(event_type or "").startswith("MACRO_"):
        return "macro"
    if event_type == "EARNINGS":
        return "earnings"
    if event_type in FIXED_INCOME_EVENT_TYPES:
        return "fixed_income"
    if event_type in MARKET_STRUCTURE_EVENT_TYPES:
        return "market_structure"
    if event_type in CORPORATE_ACTION_EVENT_TYPES:
        return "corporate_action"
    return "other"

def _event_subtype(row: dict[str, Any]) -> str:
    persisted = _normalize_taxonomy_value(row.get("event_subtype"))
    if persisted:
        return persisted
    event_type = _normalize_event_type_value(row.get("event_type"))
    if not event_type:
        return "unknown"
    if event_type.startswith("MACRO_"):
        return event_type.replace("MACRO_", "").lower()
    return event_type.lower()

def _event_universe_scope(row: dict[str, Any]) -> str:
    persisted = _normalize_taxonomy_value(row.get("universe_scope"))
    if persisted:
        return persisted
    payload = _raw_payload(row)
    payload_scope = _normalize_taxonomy_value(payload.get("universe_scope"))
    if payload_scope:
        return payload_scope
    family = _event_family(row)
    if family in {"central_bank", "macro", "fixed_income"}:
        return "official_macro"
    if family == "market_structure":
        return "all_us"
    if family == "earnings":
        return "latest_movers"
    return "unknown"

def _event_source_authority(row: dict[str, Any]) -> str:
    persisted = _normalize_taxonomy_value(row.get("source_authority"))
    if persisted in EVENT_TAXONOMY["source_authorities"]:
        return persisted
    validation = str(row.get("validation_status") or "").strip().lower()
    source_type = str(row.get("source_type") or "").strip().lower()
    source = str(row.get("source") or "").strip().lower()
    inferred_source_type = _event_source_type(row)
    if validation == "conflict":
        return "conflict"
    if validation == "cross_checked":
        return "cross_checked"
    if validation == "not_confirmed":
        return "not_confirmed"
    if source_type == "official" or validation == "official" or inferred_source_type == "Official":
        if "company_ir" in source:
            return "issuer_confirmed"
        return "official"
    if (
        source_type == "provider_estimate"
        or validation == "estimate_only"
        or inferred_source_type == "Provider Estimate"
    ):
        return "provider_estimate"
    return "unknown"

def _event_time_label(row: dict[str, Any]) -> str:
    value = str(row.get("event_time_label") or "").strip()
    if value:
        return value
    payload = _raw_payload(row)
    for key in ("event_time_label", "release_time_et", "report_time", "time_label"):
        payload_value = str(payload.get(key) or "").strip()
        if payload_value:
            return payload_value
    return "-"

def _event_datetime_utc_label(row: dict[str, Any]) -> str:
    value = row.get("event_datetime_utc")
    if value not in (None, ""):
        return _display_datetime(value) or "-"
    payload = _raw_payload(row)
    payload_value = payload.get("event_datetime_utc")
    if payload_value not in (None, ""):
        return _display_datetime(payload_value) or "-"
    return "-"

def _load_market_event_rows(
    *,
    start_date: str,
    end_date: str,
    event_type: str | None,
    limit: int,
    query_fn: QueryFn,
) -> list[dict[str, Any]]:
    conditions = ["event_date >= %s", "event_date <= %s"]
    params: list[Any] = [start_date, end_date]
    normalized_type = _normalize_event_type_value(event_type)
    if normalized_type and normalized_type != "ALL":
        if normalized_type == "MACRO":
            conditions.append("event_type LIKE %s")
            params.append("MACRO_%")
        else:
            conditions.append("event_type = %s")
            params.append(normalized_type)
    bounded_limit = _normalize_limit(limit, default=200, min_value=1, max_value=1000)
    active_conditions = conditions + ["COALESCE(event_status, 'active') <> %s"]
    active_params = params + ["superseded", bounded_limit]
    try:
        return query_fn(
            "finance_meta",
            f"""
            SELECT
                event_date,
                event_type,
                event_family,
                event_subtype,
                event_time_label,
                event_datetime_utc,
                universe_scope,
                source_authority,
                symbol,
                title,
                source,
                source_type,
                validation_status,
                event_status,
                superseded_by_event_key,
                superseded_at,
                source_url,
                confidence,
                collected_at,
                raw_payload_json
            FROM market_event_calendar
            WHERE {" AND ".join(active_conditions)}
            ORDER BY event_date ASC, event_type ASC, COALESCE(symbol, '') ASC, title ASC
            LIMIT %s
            """,
            active_params,
        )
    except Exception:
        try:
            return query_fn(
                "finance_meta",
                f"""
                SELECT
                    event_date,
                    event_type,
                    symbol,
                    title,
                    source,
                    source_url,
                    confidence,
                    collected_at
                FROM market_event_calendar
                WHERE {" AND ".join(conditions)}
                ORDER BY event_date ASC, event_type ASC, COALESCE(symbol, '') ASC, title ASC
                LIMIT %s
                """,
                params + [bounded_limit],
            )
        except Exception:
            return []

def _event_source_type(row: dict[str, Any]) -> str:
    persisted = str(row.get("source_type") or "").strip().lower()
    if persisted == "official":
        return "Official"
    if persisted == "provider_estimate":
        return "Provider Estimate"
    if persisted == "unknown":
        return "Unknown"
    event_type = _normalize_event_type_value(row.get("event_type"))
    source = str(row.get("source") or "").strip().lower()
    if source == "federal_reserve_fomc_calendar":
        return "Official"
    if event_type == "MACRO" or str(event_type or "").startswith("MACRO_"):
        if any(term in source for term in ["bureau_labor_statistics", "bureau_economic_analysis", "bea"]):
            return "Official"
    if event_type == "EARNINGS":
        if "official" in source or "company" in source:
            return "Official"
        return "Provider Estimate"
    if source:
        return "Provider"
    return "Unknown"

def _event_validation_label(row: dict[str, Any]) -> str:
    status = str(row.get("validation_status") or "").strip().lower()
    if not status and _event_source_type(row) == "Provider Estimate":
        status = "estimate_only"
    labels = {
        "official": "Official",
        "estimate_only": "Estimate only",
        "cross_checked": "Cross-checked",
        "not_confirmed": "Not confirmed",
        "conflict": "Conflict",
        "unknown": "Unknown",
    }
    return labels.get(status, "Unknown" if not status else status.replace("_", " ").title())

def _event_status_label(row: dict[str, Any]) -> str:
    status = str(row.get("event_status") or "active").strip().lower()
    labels = {
        "active": "Active",
        "superseded": "Superseded",
        "stale": "Stale",
    }
    return labels.get(status, status.replace("_", " ").title())

def _event_collected_age_days(row: dict[str, Any], *, today: date) -> int | None:
    value = row.get("collected_at")
    if value in (None, ""):
        return None
    try:
        collected_at = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(collected_at):
        return None
    if collected_at.tzinfo is not None:
        collected_at = collected_at.tz_convert(None)
    age = pd.Timestamp(today).normalize() - collected_at.normalize()
    return max(0, int(age.days))

def _event_freshness(row: dict[str, Any], *, today: date) -> str:
    event_status = str(row.get("event_status") or "active").strip().lower()
    if event_status == "superseded":
        return "Superseded"
    if event_status == "stale":
        return "Stale estimate"
    source_type = _event_source_type(row)
    age_days = _event_collected_age_days(row, today=today)
    if source_type == "Official":
        return "Official"
    if source_type == "Provider Estimate":
        if age_days is None:
            return "Estimate age unknown"
        if age_days > EVENT_ESTIMATE_STALE_DAYS:
            return "Stale estimate"
        return "Current estimate"
    if age_days is None:
        return "Collection age unknown"
    if age_days > EVENT_ESTIMATE_STALE_DAYS:
        return "Stale source"
    return "Current source"

def _event_quality_action(row: dict[str, Any], *, today: date) -> str:
    event_type = _normalize_event_type_value(row.get("event_type"))
    validation = _event_validation_label(row)
    freshness = _event_freshness(row, today=today)
    source_type = _event_source_type(row)
    if freshness == "Stale estimate":
        return "Refresh earnings calendar"
    if event_type == "EARNINGS":
        if validation == "Cross-checked":
            return "No action"
        if validation == "Not confirmed":
            return "Treat as unconfirmed; retry later or inspect source"
        if validation == "Estimate only":
            return "Enable cross-check or refresh closer to date"
        if source_type == "Official":
            return "No action"
        return "Inspect provider source"
    if source_type == "Official":
        return "No action"
    return "Inspect source freshness"

def _event_days_until(row: dict[str, Any], *, today: date) -> int | None:
    event_date = row.get("event_date")
    if event_date in (None, ""):
        return None
    try:
        event_value = pd.Timestamp(event_date).normalize()
    except (TypeError, ValueError):
        return None
    if pd.isna(event_value):
        return None
    today_value = pd.Timestamp(today).normalize()
    return int((event_value - today_value).days)

def _is_major_macro_event_type(value: Any) -> bool:
    normalized = _normalize_event_type_value(value)
    return bool(normalized in MAJOR_MACRO_EVENT_TYPES)

def _event_window_label(row: dict[str, Any], *, today: date, recent_days: int = EVENT_RECENT_WINDOW_DAYS) -> str:
    days_until = _event_days_until(row, today=today)
    if days_until is None:
        return "Unknown"
    if days_until < 0:
        return "Recent" if abs(days_until) <= max(0, int(recent_days or 0)) else "Past"
    return "Upcoming"

def _event_sort_key(row: dict[str, Any], *, today: date, recent_days: int) -> tuple[int, int, int, str, str]:
    days_until = _event_days_until(row, today=today)
    major_rank = 0 if _is_major_macro_event_type(row.get("event_type")) else 1
    if days_until is None:
        return (5, major_rank, 9999, str(row.get("event_type") or ""), str(row.get("title") or ""))
    if _is_major_macro_event_type(row.get("event_type")) and days_until < 0 and abs(days_until) <= recent_days:
        return (0, major_rank, abs(days_until), str(row.get("event_type") or ""), str(row.get("title") or ""))
    if _is_major_macro_event_type(row.get("event_type")) and days_until >= 0:
        return (1, major_rank, days_until, str(row.get("event_type") or ""), str(row.get("title") or ""))
    if days_until >= 0:
        return (2, major_rank, days_until, str(row.get("event_type") or ""), str(row.get("title") or ""))
    if abs(days_until) <= recent_days:
        return (3, major_rank, abs(days_until), str(row.get("event_type") or ""), str(row.get("title") or ""))
    return (4, major_rank, abs(days_until), str(row.get("event_type") or ""), str(row.get("title") or ""))

def _prioritize_event_rows(rows: list[dict[str, Any]], *, today: date, recent_days: int) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: _event_sort_key(row, today=today, recent_days=recent_days))

def _event_importance_label(row: dict[str, Any]) -> str:
    event_type = _normalize_event_type_value(row.get("event_type"))
    if event_type == "FOMC_MEETING" or event_type == "MACRO" or str(event_type or "").startswith("MACRO_"):
        return "High"
    if str(event_type or "").startswith("TREASURY_"):
        return "High"
    if event_type == "EARNINGS":
        return "Medium"
    if event_type in MARKET_STRUCTURE_EVENT_TYPES:
        return "Medium"
    return "Low"

def _event_focus_label(row: dict[str, Any], *, today: date) -> str:
    if _event_quality_action(row, today=today) != "No action":
        return "Needs Review"
    days_until = _event_days_until(row, today=today)
    if days_until is None:
        return "Unknown"
    if days_until < 0:
        return "Past"
    if days_until == 0:
        return "Today"
    if days_until <= 7:
        return "This Week"
    if days_until <= 30:
        return "Next 30D"
    return "Later"

def _event_coverage(rows: list[dict[str, Any]], *, today: date, recent_days: int = EVENT_RECENT_WINDOW_DAYS) -> dict[str, Any]:
    source_types = [_event_source_type(row) for row in rows]
    freshness = [_event_freshness(row, today=today) for row in rows]
    validation = [_event_validation_label(row) for row in rows]
    statuses = [_event_status_label(row) for row in rows]
    importance = [_event_importance_label(row) for row in rows]
    focus = [_event_focus_label(row, today=today) for row in rows]
    family_counts = Counter(_event_family(row) for row in rows)
    source_authority_counts = Counter(_event_source_authority(row) for row in rows)
    universe_scope_counts = Counter(_event_universe_scope(row) for row in rows)
    days_until = [_event_days_until(row, today=today) for row in rows]
    upcoming_pairs = [(row, days) for row, days in zip(rows, days_until) if days is not None and days >= 0]
    recent_pairs = [
        (row, days)
        for row, days in zip(rows, days_until)
        if days is not None and days < 0 and abs(days) <= max(0, int(recent_days or 0))
    ]
    recent_major_pairs = [
        (row, days) for row, days in recent_pairs if _is_major_macro_event_type(row.get("event_type"))
    ]
    upcoming_major_pairs = [
        (row, days) for row, days in upcoming_pairs if _is_major_macro_event_type(row.get("event_type"))
    ]
    next_row = min(upcoming_pairs, key=lambda item: (item[1], str(item[0].get("event_type") or "")))[0] if upcoming_pairs else None
    latest_recent_source = recent_major_pairs or recent_pairs
    latest_recent_row = (
        max(latest_recent_source, key=lambda item: (_iso_date(item[0].get("event_date")) or "", str(item[0].get("event_type") or "")))[0]
        if latest_recent_source
        else None
    )
    latest_collected_at = max(
        (_display_datetime(row.get("collected_at")) or "" for row in rows),
        default="",
    ) or None
    return {
        "event_count": len(rows),
        "next_event_date": _iso_date(next_row.get("event_date")) if next_row else None,
        "latest_recent_event_date": _iso_date(latest_recent_row.get("event_date")) if latest_recent_row else None,
        "latest_collected_at": latest_collected_at,
        "source_count": len({str(row.get("source") or "") for row in rows if row.get("source")}),
        "official_count": source_types.count("Official"),
        "estimate_count": source_types.count("Provider Estimate"),
        "estimate_only_count": validation.count("Estimate only"),
        "cross_checked_count": validation.count("Cross-checked"),
        "not_confirmed_count": validation.count("Not confirmed"),
        "stale_estimate_count": freshness.count("Stale estimate"),
        "action_required_count": sum(
            1
            for row in rows
            if _event_quality_action(row, today=today) != "No action"
        ),
        "high_importance_count": importance.count("High"),
        "needs_review_count": focus.count("Needs Review"),
        "this_week_count": sum(1 for value in focus if value in {"Today", "This Week"}),
        "next_30d_count": sum(1 for value in days_until if value is not None and 0 <= value <= 30),
        "recent_event_count": len(recent_pairs),
        "upcoming_event_count": len(upcoming_pairs),
        "recent_high_importance_count": len(recent_major_pairs),
        "upcoming_high_importance_count": len(upcoming_major_pairs),
        "superseded_count": statuses.count("Superseded"),
        "family_counts": dict(sorted(family_counts.items())),
        "source_authority_counts": dict(sorted(source_authority_counts.items())),
        "universe_scope_counts": dict(sorted(universe_scope_counts.items())),
    }

def _event_warnings(coverage: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    stale_estimates = int(coverage.get("stale_estimate_count") or 0)
    if stale_estimates > 0:
        warnings.append(
            f"{stale_estimates} earnings estimate row(s) were collected more than "
            f"{EVENT_ESTIMATE_STALE_DAYS} days ago. Refresh Earnings Calendar before acting on those dates."
        )
    not_confirmed = int(coverage.get("not_confirmed_count") or 0)
    if not_confirmed > 0:
        warnings.append(
            f"{not_confirmed} earnings estimate row(s) were not confirmed by the alternate Nasdaq calendar cross-check."
        )
    return warnings

def _event_rows_frame(
    rows: list[dict[str, Any]],
    *,
    today: date,
    recent_days: int = EVENT_RECENT_WINDOW_DAYS,
) -> pd.DataFrame:
    out = [
        {
            "Date": _iso_date(row.get("event_date")) or "-",
            "Days Until": _event_days_until(row, today=today),
            "Window": _event_window_label(row, today=today, recent_days=recent_days),
            "Type": row.get("event_type") or "-",
            "Event Family": _event_family(row),
            "Event Subtype": _event_subtype(row),
            "Universe Scope": _event_universe_scope(row),
            "Source Authority": _event_source_authority(row),
            "Event Time": _event_time_label(row),
            "Event Datetime UTC": _event_datetime_utc_label(row),
            "Symbol": row.get("symbol") or "-",
            "Title": row.get("title") or "-",
            "Importance": _event_importance_label(row),
            "Focus": _event_focus_label(row, today=today),
            "Source Type": _event_source_type(row),
            "Validation": _event_validation_label(row),
            "Freshness": _event_freshness(row, today=today),
            "Quality Action": _event_quality_action(row, today=today),
            "Event Status": _event_status_label(row),
            "Age Days": _event_collected_age_days(row, today=today),
            "Source": row.get("source") or "-",
            "Confidence": (
                round(float(row["confidence"]), 2)
                if _safe_float(row.get("confidence")) is not None
                else None
            ),
            "Collected At": _display_datetime(row.get("collected_at")) or "-",
            "Source URL": row.get("source_url") or "-",
        }
        for row in rows
    ]
    return pd.DataFrame(out, columns=EVENT_COLUMNS)

def build_market_events_snapshot(
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    event_type: str | None = "FOMC_MEETING",
    horizon_days: int = 365,
    recent_days: int = EVENT_RECENT_WINDOW_DAYS,
    limit: int = 200,
    today: date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, Any]:
    today_value = today or date.today()
    bounded_recent_days = max(0, int(recent_days or 0))
    normalized_start = _iso_date(start_date) or (today_value - timedelta(days=bounded_recent_days)).isoformat()
    normalized_end = _iso_date(end_date) or (today_value + timedelta(days=int(horizon_days or 365))).isoformat()
    normalized_type = _normalize_event_type_value(event_type)
    query = query_fn or _default_query
    try:
        rows = _load_market_event_rows(
            start_date=normalized_start,
            end_date=normalized_end,
            event_type=normalized_type,
            limit=limit,
            query_fn=query,
        )
        if not rows:
            return _empty_events_snapshot(
                status="NO_EVENTS",
                start_date=normalized_start,
                end_date=normalized_end,
                event_type=normalized_type,
                message="No stored market events match the selected window. Run a matching event calendar collector first.",
            )
        rows = _prioritize_event_rows(rows, today=today_value, recent_days=bounded_recent_days)
        coverage = _event_coverage(rows, today=today_value, recent_days=bounded_recent_days)
        return {
            "schema_version": "market_events_snapshot_v2",
            "status": "OK",
            "event_type": normalized_type or "All",
            "rows": _event_rows_frame(rows, today=today_value, recent_days=bounded_recent_days),
            "date_window": {"start_date": normalized_start, "end_date": normalized_end},
            "coverage": coverage,
            "taxonomy": EVENT_TAXONOMY,
            "warnings": _event_warnings(coverage),
        }
    except Exception as exc:
        return _empty_events_snapshot(
            status="ERROR",
            start_date=normalized_start,
            end_date=normalized_end,
            event_type=normalized_type,
            message=f"Market events snapshot failed: {exc}",
        )

def _cockpit_frame(snapshot: dict[str, Any], key: str = "rows") -> pd.DataFrame:
    rows = snapshot.get(key)
    if isinstance(rows, pd.DataFrame):
        return rows
    if isinstance(rows, list):
        return pd.DataFrame(rows)
    return pd.DataFrame()

def _cockpit_int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0

def _workbench_records(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    frame = _cockpit_frame(snapshot)
    if frame.empty:
        return []
    records: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        record: dict[str, Any] = {}
        for key, value in row.to_dict().items():
            if isinstance(value, float) and pd.isna(value):
                record[key] = None
            else:
                record[key] = value
        records.append(record)
    return sorted(
        records,
        key=lambda item: (
            str(item.get("Date") or ""),
            _cockpit_int(item.get("Days Until")) if item.get("Days Until") is not None else 9999,
            str(item.get("Type") or ""),
            str(item.get("Symbol") or ""),
            str(item.get("Title") or ""),
        ),
    )

def _workbench_days_until(record: dict[str, Any]) -> int | None:
    value = _safe_float(record.get("Days Until"))
    if value is None:
        return None
    return int(value)

def _workbench_row_needs_review(record: dict[str, Any]) -> bool:
    action = str(record.get("Quality Action") or "").strip()
    freshness = str(record.get("Freshness") or "").strip().lower()
    validation = str(record.get("Validation") or "").strip().lower()
    if action and action != "No action":
        return True
    return "stale" in freshness or validation in {"not confirmed", "estimate only", "conflict"}

def _display_key(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")

def _display_label(mapping: dict[str, str], value: Any, *, fallback: str = "-") -> str:
    key = _display_key(value)
    if not key:
        return fallback
    return mapping.get(key, str(value or fallback).replace("_", " ").title())

def _workbench_item(record: dict[str, Any]) -> dict[str, Any]:
    days_until = _workbench_days_until(record)
    family = str(record.get("Event Family") or "unknown")
    source_authority = str(record.get("Source Authority") or "unknown")
    universe_scope = str(record.get("Universe Scope") or "unknown")
    freshness = str(record.get("Freshness") or "Unknown")
    validation = str(record.get("Validation") or "Unknown")
    badges = [
        {"label": _display_label(EVENT_FAMILY_LABELS_KO, family), "kind": "family"},
        {"label": _display_label(EVENT_SOURCE_AUTHORITY_LABELS_KO, source_authority), "kind": "source_authority"},
        {"label": _display_label(EVENT_UNIVERSE_SCOPE_LABELS_KO, universe_scope), "kind": "universe_scope"},
    ]
    if "stale" in freshness.lower():
        badges.append({"label": _display_label(EVENT_FRESHNESS_LABELS_KO, freshness), "kind": "freshness"})
    if validation not in {"Official", "Unknown"}:
        badges.append({"label": _display_label(EVENT_VALIDATION_LABELS_KO, validation), "kind": "validation"})
    return {
        "date": str(record.get("Date") or "-"),
        "days_until": days_until,
        "window": str(record.get("Window") or "-"),
        "type": str(record.get("Type") or "-"),
        "family": family,
        "subtype": str(record.get("Event Subtype") or "unknown"),
        "symbol": "" if str(record.get("Symbol") or "-") == "-" else str(record.get("Symbol") or ""),
        "title": str(record.get("Title") or "-"),
        "importance": str(record.get("Importance") or "Low"),
        "focus": str(record.get("Focus") or "-"),
        "source_type": str(record.get("Source Type") or "-"),
        "source_authority": source_authority,
        "universe_scope": universe_scope,
        "validation": validation,
        "freshness": freshness,
        "quality_action": str(record.get("Quality Action") or "No action"),
        "event_status": str(record.get("Event Status") or "-"),
        "event_time": str(record.get("Event Time") or "-"),
        "event_datetime_utc": str(record.get("Event Datetime UTC") or "-"),
        "source": str(record.get("Source") or "-"),
        "source_url": str(record.get("Source URL") or "-"),
        "confidence": record.get("Confidence"),
        "collected_at": str(record.get("Collected At") or "-"),
        "needs_review": _workbench_row_needs_review(record),
        "badges": badges,
    }

def _workbench_rail(key: str, label: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    items = [_workbench_item(record) for record in records]
    return {
        "key": key,
        "label": label,
        "count": len(items),
        "review_count": sum(1 for item in items if item["needs_review"]),
        "items": items,
    }

def _events_workbench_filters() -> dict[str, Any]:
    return {
        "family": {
            "label": "일정 타입",
            "options": [
                {"id": key, "label": label}
                for key, label in [
                    ("all", "전체"),
                    ("central_bank", "FOMC"),
                    ("macro", "매크로"),
                    ("earnings", "실적"),
                    ("market_structure", "시장 구조"),
                ]
            ],
        },
        "source_state": {
            "label": "자료 상태",
            "options": [
                {"id": key, "label": label}
                for key, label in [
                    ("all", "전체"),
                    ("review", "확인 필요"),
                    ("official", "공식 / 확인됨"),
                    ("estimate", "추정 / 미확정"),
                ]
            ],
        },
    }

def _events_workbench_rail_tabs(
    *,
    recent_major_records: list[dict[str, Any]],
    today_records: list[dict[str, Any]],
    this_week_records: list[dict[str, Any]],
    next_30d_records: list[dict[str, Any]],
    later_records: list[dict[str, Any]],
) -> dict[str, Any]:
    tabs = [
        _workbench_rail("recent_major", "최근 중요", recent_major_records),
        _workbench_rail("near_term", "오늘 / 이번 주", today_records + this_week_records),
        _workbench_rail("next_30d", "30일 내", next_30d_records),
        _workbench_rail("later", "나중", later_records),
    ]
    default_key = "near_term"
    if not any(tab["key"] == default_key and tab["count"] for tab in tabs):
        default_key = next((tab["key"] for tab in tabs if tab["count"]), "near_term")
    return {
        "default_key": default_key,
        "tabs": tabs,
        "empty_text": "선택한 조건에 맞는 일정이 없습니다.",
    }

def _workbench_week_start(date_text: str) -> str | None:
    try:
        day = pd.Timestamp(date_text).date()
    except (TypeError, ValueError):
        return None
    if pd.isna(pd.Timestamp(day)):
        return None
    return (day - timedelta(days=day.weekday())).isoformat()

def _events_workbench_calendar(records: list[dict[str, Any]], *, today: date) -> dict[str, Any]:
    by_day: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        date_text = str(record.get("Date") or "")
        if not date_text or date_text == "-":
            continue
        by_day.setdefault(date_text, []).append(record)

    days: list[dict[str, Any]] = []
    weekly: dict[str, dict[str, Any]] = {}
    for date_text, day_records in sorted(by_day.items()):
        families = Counter(str(record.get("Event Family") or "unknown") for record in day_records)
        stale_count = sum(1 for record in day_records if "stale" in str(record.get("Freshness") or "").lower())
        review_count = sum(1 for record in day_records if _workbench_row_needs_review(record))
        day_payload = {
            "date": date_text,
            "count": len(day_records),
            "by_family": dict(sorted(families.items())),
            "review_count": review_count,
            "stale_count": stale_count,
            "top_titles": [str(record.get("Title") or "-") for record in day_records[:3]],
            "items": [_workbench_item(record) for record in day_records],
        }
        days.append(day_payload)
        week_start = _workbench_week_start(date_text)
        if week_start:
            bucket = weekly.setdefault(
                week_start,
                {"week_start": week_start, "count": 0, "review_count": 0, "stale_count": 0, "by_family": Counter()},
            )
            bucket["count"] += len(day_records)
            bucket["review_count"] += review_count
            bucket["stale_count"] += stale_count
            bucket["by_family"].update(families)

    density = []
    for week_start, bucket in sorted(weekly.items()):
        density.append(
            {
                "week_start": week_start,
                "count": int(bucket["count"]),
                "review_count": int(bucket["review_count"]),
                "stale_count": int(bucket["stale_count"]),
                "by_family": dict(sorted(bucket["by_family"].items())),
            }
        )
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    return {
        "today": today.isoformat(),
        "current_week_start": current_week_start.isoformat(),
        "current_week_end": current_week_end.isoformat(),
        "days": days,
        "density": density,
        "weekday_labels": ["월", "화", "수", "목", "금", "토", "일"],
    }

def _events_workbench_trust_review(
    records: list[dict[str, Any]],
    *,
    coverage: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    stale_items = [_workbench_item(record) for record in records if "stale" in str(record.get("Freshness") or "").lower()]
    not_confirmed_items = [
        _workbench_item(record) for record in records if str(record.get("Validation") or "").strip() == "Not confirmed"
    ]
    estimate_only_items = [
        _workbench_item(record) for record in records if str(record.get("Validation") or "").strip() == "Estimate only"
    ]
    conflict_items = [
        _workbench_item(record) for record in records if str(record.get("Validation") or "").strip() == "Conflict"
    ]
    return {
        "eyebrow": "자료 상태",
        "title": "일정 확정성 / 추정 일정 점검",
        "description": (
            "이 섹션은 일정이 공식 발표인지, 제공사 추정인지, 오래된 추정인지 확인하는 곳입니다. "
            "시장 배경 근거이며 매수/매도 신호가 아닙니다."
        ),
        "official_count": int(coverage.get("official_count") or 0),
        "provider_estimate_count": int(coverage.get("estimate_count") or 0),
        "estimate_only_count": int(coverage.get("estimate_only_count") or 0),
        "cross_checked_count": int(coverage.get("cross_checked_count") or 0),
        "not_confirmed_count": int(coverage.get("not_confirmed_count") or 0),
        "stale_estimate_count": int(coverage.get("stale_estimate_count") or 0),
        "conflict_count": len(conflict_items),
        "source_authority_counts": dict(coverage.get("source_authority_counts") or {}),
        "universe_scope_counts": dict(coverage.get("universe_scope_counts") or {}),
        "warnings": list(warnings),
        "sections": [
            {"key": "stale_estimates", "label": "오래된 추정 일정", "count": len(stale_items), "items": stale_items},
            {"key": "not_confirmed", "label": "미확정 일정", "count": len(not_confirmed_items), "items": not_confirmed_items},
            {"key": "estimate_only", "label": "추정만 있음", "count": len(estimate_only_items), "items": estimate_only_items},
            {"key": "conflicts", "label": "일정 충돌", "count": len(conflict_items), "items": conflict_items},
        ],
        "source_boundary": (
            "공식 일정인 매크로/FOMC/시장 구조 일정과 제공사 추정 실적 일정은 한 화면에서 함께 보이지만, "
            "제공사 추정은 교차 확인 또는 기업 확인 전까지 미확정 일정으로 봅니다."
        ),
    }

def _events_workbench_command() -> dict[str, Any]:
    return {
        "title": "화면 / 수집 갱신",
        "refresh_boundary": (
            "화면 새로고침은 DB에 저장된 이벤트 rows를 다시 읽습니다. "
            "수집 갱신은 provider/job을 실행해 DB rows를 새로 저장할 수 있습니다."
        ),
        "actions": [
            {
                "id": "reload",
                "label": "화면 새로고침",
                "kind": "secondary",
                "detail": "DB에 저장된 이벤트 rows를 다시 읽습니다.",
            },
            {
                "id": "refresh_all",
                "label": "전체 일정 갱신",
                "kind": "primary",
                "detail": "FOMC, 매크로, 시장 구조, 실적 추정 일정 collector를 순차 실행합니다.",
            },
            {
                "id": "refresh_fomc",
                "label": "FOMC 공식 일정 갱신",
                "kind": "secondary",
                "detail": "Federal Reserve 공식 calendar provider/job을 실행합니다.",
            },
            {
                "id": "refresh_macro",
                "label": "매크로 공식 일정 갱신",
                "kind": "secondary",
                "detail": "BLS/BEA/Census/ISM/Treasury calendar provider/job을 실행합니다.",
            },
            {
                "id": "refresh_market_structure",
                "label": "시장 구조 일정 갱신",
                "kind": "secondary",
                "detail": "Nasdaq/Cboe/Russell market-structure provider/job을 실행합니다.",
            },
            {
                "id": "refresh_earnings",
                "label": "실적 예상 일정 갱신",
                "kind": "secondary",
                "detail": "S&P 500 movers 기반 earnings estimate provider/job을 실행합니다.",
            },
        ],
        "earnings_universe": {
            "label": "실적 예상 일정 기준",
            "symbol_source": "latest_movers",
            "universe_code": "SP500",
            "description": (
                "최근 S&P 500 movers snapshot의 상위 최대 20개 후보를 기준으로 삼고, "
                "provider 호출은 최대 50개 symbol까지 제한합니다."
            ),
            "top_movers_limit": 20,
            "max_symbols": 50,
            "lookahead_days": 120,
            "cross_check": "Nasdaq calendar cross-check 사용",
        },
        "last_results": [],
    }

def build_events_workbench_payload(
    events_snapshot: dict[str, Any] | None = None,
    *,
    today: date | None = None,
    horizon_days: int = 90,
    recent_days: int = EVENT_RECENT_WINDOW_DAYS,
    limit: int = 500,
) -> dict[str, Any]:
    """Build a React-ready Events payload while keeping interpretation in Python."""
    today_value = today or date.today()
    snapshot = events_snapshot or build_market_events_snapshot(
        event_type=None,
        today=today_value,
        horizon_days=horizon_days,
        recent_days=recent_days,
        limit=limit,
    )
    records = _workbench_records(snapshot)
    coverage = dict(snapshot.get("coverage") or {})
    warnings = list(snapshot.get("warnings") or [])
    items = [_workbench_item(record) for record in records]
    upcoming_items = [item for item in items if item["days_until"] is not None and item["days_until"] >= 0]
    next_event = upcoming_items[0] if upcoming_items else None

    recent_major_records = [
        record
        for record in records
        if (_workbench_days_until(record) is not None and _workbench_days_until(record) < 0)
        and str(record.get("Importance") or "") == "High"
    ]
    today_records = [record for record in records if _workbench_days_until(record) == 0]
    this_week_records = [
        record
        for record in records
        if (_workbench_days_until(record) is not None and 1 <= _workbench_days_until(record) <= 7)
    ]
    next_30d_records = [
        record
        for record in records
        if (_workbench_days_until(record) is not None and 8 <= _workbench_days_until(record) <= 30)
    ]
    later_records = [
        record
        for record in records
        if (_workbench_days_until(record) is None or _workbench_days_until(record) > 30)
    ]

    today_count = len(today_records)
    this_week_count = sum(
        1 for item in items if item["days_until"] is not None and 0 <= item["days_until"] <= 7
    )
    next_30d_count = sum(
        1 for item in items if item["days_until"] is not None and 0 <= item["days_until"] <= 30
    )
    freshness_summary = {
        "latest_collected_at": coverage.get("latest_collected_at"),
        "stale_estimate_count": int(coverage.get("stale_estimate_count") or 0),
        "has_stale_estimates": int(coverage.get("stale_estimate_count") or 0) > 0,
        "warning_count": len(warnings),
    }

    return {
        "schema_version": "events_workbench_v1",
        "status": snapshot.get("status") or "UNKNOWN",
        "date_window": dict(snapshot.get("date_window") or {}),
        "brief": {
            "title": "다가오는 시장 이벤트 브리프",
            "boundary_note": "이 화면은 거래 신호가 아니라 시장 배경 확인용입니다.",
            "next_event": next_event,
            "counts": {
                "today": today_count,
                "this_week": this_week_count,
                "next_30d": next_30d_count,
                "total": len(items),
            },
            "source_summary": {
                "official": int(coverage.get("official_count") or 0),
                "provider_estimate": int(coverage.get("estimate_count") or 0),
                "cross_checked": int(coverage.get("cross_checked_count") or 0),
                "not_confirmed": int(coverage.get("not_confirmed_count") or 0),
            },
            "freshness_summary": freshness_summary,
            "family_counts": dict(coverage.get("family_counts") or {}),
        },
        "rails": [
            _workbench_rail("recent_major", "최근 중요", recent_major_records),
            _workbench_rail("today", "오늘", today_records),
            _workbench_rail("this_week", "이번 주", this_week_records),
            _workbench_rail("next_30d", "30일 내", next_30d_records),
            _workbench_rail("later", "나중", later_records),
        ],
        "rail_tabs": _events_workbench_rail_tabs(
            recent_major_records=recent_major_records,
            today_records=today_records,
            this_week_records=this_week_records,
            next_30d_records=next_30d_records,
            later_records=later_records,
        ),
        "filters": _events_workbench_filters(),
        "command": _events_workbench_command(),
        "trust_review": _events_workbench_trust_review(records, coverage=coverage, warnings=warnings),
        "calendar": _events_workbench_calendar(records, today=today_value),
        "evidence": {
            "raw_fields": list(EVENT_COLUMNS),
            "rows": records[: max(1, int(limit or 500))],
            "row_count": len(records),
        },
        "warnings": warnings,
        "taxonomy": dict(snapshot.get("taxonomy") or EVENT_TAXONOMY),
    }

def _macro_week_cluster_label(event_type: Any) -> str:
    normalized = str(event_type or "").strip().upper()
    if normalized in {"FOMC_MEETING", "FOMC"}:
        return "FOMC"
    if normalized in {"MACRO_CPI", "CPI"}:
        return "CPI"
    if normalized in {"MACRO_PPI", "PPI"}:
        return "PPI"
    if normalized in {"MACRO_EMPLOYMENT", "EMPLOYMENT", "JOBS"}:
        return "Employment"
    if normalized in {"MACRO_GDP", "GDP"}:
        return "GDP"
    if normalized in {"MACRO_PCE", "PCE"}:
        return "PCE"
    if normalized in {"MACRO_JOLTS", "JOLTS"}:
        return "JOLTS"
    if normalized in {"MACRO_ECI", "ECI"}:
        return "ECI"
    if normalized in {"MACRO_RETAIL_SALES", "RETAIL_SALES"}:
        return "Retail Sales"
    if normalized in {"MACRO_DURABLE_GOODS", "DURABLE_GOODS"}:
        return "Durable Goods"
    if normalized in {"MACRO_HOUSING", "HOUSING"}:
        return "Housing"
    if normalized in {"MACRO_ISM_MANUFACTURING_PMI", "ISM_MANUFACTURING"}:
        return "ISM Mfg"
    if normalized in {"MACRO_ISM_SERVICES_PMI", "ISM_SERVICES"}:
        return "ISM Services"
    if normalized in {"TREASURY_AUCTION", "TREASURY"}:
        return "Treasury"
    if normalized in {"EARNINGS", "EARNINGS CALENDAR"}:
        return "Earnings"
    if normalized.startswith("MACRO_"):
        return normalized.replace("MACRO_", "").replace("_", " ").title()
    return "Other"

def _macro_week_event_needs_review(row: dict[str, Any]) -> bool:
    action = str(row.get("Quality Action") or "").strip().lower()
    freshness = str(row.get("Freshness") or "").strip().lower()
    validation = str(row.get("Validation") or "").strip().lower()
    if action and action != "no action":
        return True
    return any(token in freshness for token in ("stale", "unknown")) or any(
        token in validation for token in ("not confirmed", "estimate only")
    )

def _macro_week_item_tone(row: dict[str, Any]) -> str:
    if _macro_week_event_needs_review(row):
        return "warning"
    cluster = _macro_week_cluster_label(row.get("Type"))
    if cluster == "Earnings":
        return "earnings"
    if cluster != "Other":
        return "macro"
    return "neutral"

def _macro_week_is_major_macro(row: dict[str, Any]) -> bool:
    return _macro_week_cluster_label(row.get("Type")) not in {"Earnings", "Other"}

def _macro_week_item_from_row(row: dict[str, Any], *, days_until: int | None, window: str) -> dict[str, Any]:
    return {
        "date": str(row.get("Date") or "-"),
        "days_until": days_until,
        "window": window,
        "type": str(row.get("Type") or "-"),
        "cluster": _macro_week_cluster_label(row.get("Type")),
        "title": str(row.get("Title") or "-"),
        "symbol": str(row.get("Symbol") or "-"),
        "source_type": str(row.get("Source Type") or "-"),
        "validation": str(row.get("Validation") or "-"),
        "freshness": str(row.get("Freshness") or "-"),
        "quality_action": str(row.get("Quality Action") or "-"),
        "importance": str(row.get("Importance") or "-"),
        "tone": _macro_week_item_tone(row),
    }

def build_overview_macro_week_lane(
    events_snapshot: dict[str, Any] | None = None,
    *,
    horizon_days: int = 14,
    recent_days: int = EVENT_RECENT_WINDOW_DAYS,
    limit: int = 8,
) -> dict[str, Any]:
    """Summarize existing event-calendar rows into a recent + upcoming macro context lane."""
    snapshot = events_snapshot or {}
    rows = _cockpit_frame(snapshot)
    coverage = dict(snapshot.get("coverage") or {})
    bounded_horizon_days = max(0, int(horizon_days or 14))
    bounded_recent_days = max(0, int(recent_days or 0))
    boundary_note = "context 전용 이벤트 캘린더입니다. 거래 실행이나 다른 화면의 승인/운영 판단을 만들지 않습니다."
    if rows.empty or "Days Until" not in rows:
        return {
            "schema_version": "overview_macro_week_lane_v2",
            "status": "NO_DATA",
            "summary": {
                "headline": "Macro week context unavailable",
                "detail": str(snapshot.get("message") or "No stored event rows are available."),
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "next_event_label": "No event in view",
            },
            "coverage": {
                "event_count": coverage.get("event_count"),
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "official_count": coverage.get("official_count"),
                "estimate_count": coverage.get("estimate_count"),
                "latest_collected_at": coverage.get("latest_collected_at"),
            },
            "clusters": {},
            "recent_items": [],
            "upcoming_items": [],
            "items": [],
            "boundary_note": boundary_note,
        }

    working = rows.copy()
    if "Type" not in working.columns:
        working["Type"] = working["Type Label"] if "Type Label" in working.columns else "Other"
    elif "Type Label" in working.columns:
        type_values = working["Type"].astype(str).str.strip()
        working["Type"] = working["Type"].where(type_values.ne("") & type_values.ne("nan"), working["Type Label"])
    working["_days_until"] = working["Days Until"].map(_safe_float)
    recent_rows = working[
        working["_days_until"].notna()
        & (working["_days_until"] < 0)
        & (working["_days_until"] >= -bounded_recent_days)
    ].copy()
    if not recent_rows.empty:
        recent_rows = recent_rows[
            recent_rows.apply(lambda row_value: _macro_week_is_major_macro(dict(row_value.dropna().to_dict())), axis=1)
        ].copy()
    upcoming_rows = working[
        working["_days_until"].notna()
        & (working["_days_until"] >= 0)
        & (working["_days_until"] <= bounded_horizon_days)
    ].copy()
    near_rows = pd.concat([recent_rows, upcoming_rows], ignore_index=True)
    if near_rows.empty:
        return {
            "schema_version": "overview_macro_week_lane_v2",
            "status": snapshot.get("status") or "OK",
            "summary": {
                "headline": f"No stored major events from the last {bounded_recent_days} days through the next {bounded_horizon_days} days",
                "detail": "Open Events for the full calendar and source quality view.",
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "next_event_label": "No event in view",
            },
            "coverage": {
                "event_count": coverage.get("event_count"),
                "near_event_count": 0,
                "recent_event_count": 0,
                "upcoming_event_count": 0,
                "official_count": coverage.get("official_count"),
                "estimate_count": coverage.get("estimate_count"),
                "latest_collected_at": coverage.get("latest_collected_at"),
            },
            "clusters": {},
            "recent_items": [],
            "upcoming_items": [],
            "items": [],
            "boundary_note": boundary_note,
        }

    recent_rows = recent_rows.sort_values(by=["_days_until", "Date", "Type"], ascending=[False, False, True], kind="mergesort")
    upcoming_rows = upcoming_rows.sort_values(by=["_days_until", "Date", "Type"], kind="mergesort")
    near_rows = pd.concat([recent_rows, upcoming_rows], ignore_index=True)
    recent_items: list[dict[str, Any]] = []
    upcoming_items: list[dict[str, Any]] = []
    cluster_order = [
        "FOMC",
        "CPI",
        "PPI",
        "Employment",
        "GDP",
        "PCE",
        "JOLTS",
        "ECI",
        "ISM Mfg",
        "ISM Services",
        "Treasury",
        "Earnings",
        "Other",
    ]
    clusters: dict[str, dict[str, Any]] = {
        label: {"label": label, "count": 0, "review_count": 0, "next_date": None, "tone": "neutral"}
        for label in cluster_order
    }

    for _, row_value in near_rows.iterrows():
        row = dict(row_value.drop(labels=["_days_until"], errors="ignore").dropna().to_dict())
        days_until = _cockpit_int(row_value.get("_days_until"))
        cluster = _macro_week_cluster_label(row.get("Type"))
        if cluster not in clusters:
            clusters[cluster] = {"label": cluster, "count": 0, "review_count": 0, "next_date": None, "tone": "neutral"}
        needs_review = _macro_week_event_needs_review(row)
        tone = _macro_week_item_tone(row)
        clusters[cluster]["count"] += 1
        clusters[cluster]["review_count"] += 1 if needs_review else 0
        clusters[cluster]["next_date"] = clusters[cluster]["next_date"] or str(row.get("Date") or "-")
        clusters[cluster]["tone"] = "warning" if clusters[cluster]["review_count"] else tone
        item = _macro_week_item_from_row(
            row,
            days_until=days_until,
            window="recent" if days_until is not None and days_until < 0 else "upcoming",
        )
        if item["window"] == "recent":
            recent_items.append(item)
        else:
            upcoming_items.append(item)

    clusters = {label: value for label, value in clusters.items() if int(value.get("count") or 0) > 0}
    review_count = sum(1 for _, row_value in near_rows.iterrows() if _macro_week_event_needs_review(dict(row_value.to_dict())))
    items = (recent_items + upcoming_items)[: max(1, int(limit or 8))]
    recent_items = recent_items[: max(1, int(limit or 8))]
    upcoming_items = upcoming_items[: max(1, int(limit or 8))]
    next_item = upcoming_items[0] if upcoming_items else {}
    next_event_label = (
        f"{next_item.get('type')} in {next_item.get('days_until')}d"
        if next_item
        else "No event in view"
    )
    official_near_count = int(
        near_rows.get("Source Type", pd.Series(dtype=str)).fillna("").astype(str).str.lower().eq("official").sum()
    )
    earnings_near_count = int(
        near_rows.get("Type", pd.Series(dtype=str)).fillna("").astype(str).str.upper().eq("EARNINGS").sum()
    )

    return {
        "schema_version": "overview_macro_week_lane_v2",
        "status": "REVIEW" if review_count else (snapshot.get("status") or "OK"),
        "summary": {
            "headline": (
                f"{len(recent_items)} recent major event(s) and {len(upcoming_rows)} upcoming event(s) in view"
                if recent_items
                else f"{len(upcoming_rows)} upcoming event(s) in the next {bounded_horizon_days} days"
            ),
            "detail": f"{official_near_count} official macro rows · {earnings_near_count} earnings rows · {review_count} need source review",
            "near_event_count": int(len(near_rows)),
            "recent_event_count": int(len(recent_rows)),
            "upcoming_event_count": int(len(upcoming_rows)),
            "next_event_label": next_event_label,
        },
        "coverage": {
            "event_count": coverage.get("event_count"),
            "near_event_count": int(len(near_rows)),
            "recent_event_count": int(len(recent_rows)),
            "upcoming_event_count": int(len(upcoming_rows)),
            "official_count": coverage.get("official_count"),
            "estimate_count": coverage.get("estimate_count"),
            "latest_collected_at": coverage.get("latest_collected_at"),
            "review_count": review_count,
        },
        "clusters": clusters,
        "recent_items": recent_items,
        "upcoming_items": upcoming_items,
        "items": items,
        "boundary_note": boundary_note,
    }

__all__ = [
    "build_events_workbench_payload",
    "build_market_events_snapshot",
    "build_overview_macro_week_lane",
]
