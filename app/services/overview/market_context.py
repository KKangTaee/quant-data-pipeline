from __future__ import annotations

import json
import os
import re
import urllib.request
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

from app.services.overview.data_health import (
    build_collection_ops_snapshot,
    build_overview_data_health_ingestion_handoff,
)
from app.services.overview.events import (
    build_market_events_snapshot,
    build_overview_macro_week_lane,
)
from app.services.overview.market_movers import (
    build_group_leadership_snapshot,
    build_market_movers_snapshot,
    build_overview_breadth_heatmap_summary,
)
from app.services.overview.sentiment import build_market_sentiment_snapshot

EVENT_RECENT_WINDOW_DAYS = 7

MAJOR_MACRO_EVENT_TYPES = {
    "FOMC_MEETING",
    "MACRO_CPI",
    "MACRO_PPI",
    "MACRO_EMPLOYMENT",
    "MACRO_GDP",
}

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

def _iso_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d")

def _normalize_event_type_value(value: str | None) -> str | None:
    normalized = str(value or "").strip().upper().replace(" ", "_")
    return normalized or None

def _is_major_macro_event_type(value: Any) -> bool:
    normalized = _normalize_event_type_value(value)
    return bool(normalized in MAJOR_MACRO_EVENT_TYPES)

def _cockpit_error_snapshot(label: str, exc: Exception) -> dict[str, Any]:
    return {
        "status": "ERROR",
        "message": f"{label} snapshot failed: {exc}",
        "coverage": {},
        "rows": pd.DataFrame(),
    }

def _cockpit_frame(snapshot: dict[str, Any], key: str = "rows") -> pd.DataFrame:
    rows = snapshot.get(key)
    if isinstance(rows, pd.DataFrame):
        return rows
    if isinstance(rows, list):
        return pd.DataFrame(rows)
    return pd.DataFrame()

def _cockpit_first_row(snapshot: dict[str, Any], key: str = "rows") -> dict[str, Any]:
    frame = _cockpit_frame(snapshot, key=key)
    if frame.empty:
        return {}
    return dict(frame.iloc[0].dropna().to_dict())

def _cockpit_int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0

def _cockpit_status_text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("label") or value.get("status") or "").strip()
    return str(value or "").strip()

def _cockpit_status_tone(status: Any) -> str:
    if isinstance(status, dict) and status.get("tone"):
        return str(status.get("tone"))
    normalized = _cockpit_status_text(status).lower()
    if normalized in {"ok", "success", "actual", "high", "fresh"}:
        return "positive"
    if normalized in {"reference_limit", "meta"}:
        return "neutral"
    if normalized in {"failed", "error", "missing", "no_universe", "insufficient_data"}:
        return "danger"
    if normalized in {"review", "due", "stale", "partial", "not_run", "no_data"}:
        return "warning"
    return "neutral"

def _cockpit_card_status(*values: Any) -> str:
    for value in values:
        normalized = _cockpit_status_text(value)
        if normalized and normalized.upper() not in {"OK", "SUCCESS", "ACTUAL"}:
            return normalized
    return "OK"

def _cockpit_percent(value: Any, *, digits: int = 1) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return "-"
    return f"{numeric:+.{digits}f}%"

def _overview_round(value: Any, *, digits: int = 1) -> float | None:
    numeric = _safe_float(value)
    if numeric is None:
        return None
    return round(numeric, digits)

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
    if normalized in {"EARNINGS", "EARNINGS CALENDAR"}:
        return "Earnings"
    if normalized.startswith("MACRO_"):
        return normalized.replace("MACRO_", "").replace("_", " ").title()
    return "Other"

def _source_confidence_status(
    snapshot: dict[str, Any],
    *,
    review_hint: bool = False,
    no_data_if_empty: bool = False,
    row_key: str = "rows",
) -> str:
    rows = _cockpit_frame(snapshot, key=row_key)
    if no_data_if_empty and rows.empty:
        return "NO_DATA"
    status = _cockpit_card_status(snapshot.get("status"))
    normalized = status.strip().upper()
    if review_hint or normalized in {"REVIEW", "DUE", "STALE", "PARTIAL", "MISSING", "FAILED", "ERROR", "NO_DATA"}:
        return "REVIEW" if normalized != "NO_DATA" else "NO_DATA"
    return "OK"

def _source_confidence_item(
    *,
    item_id: str,
    title: str,
    surface: str,
    source: str,
    owner: str,
    status: str,
    freshness: Any,
    detail: str,
    caveat: str,
    next_check: str,
    source_role: str = "brief_source",
    actionability: str = "actionable",
    counts_for_status: bool = True,
    status_label: str | None = None,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "title": title,
        "surface": surface,
        "source": source,
        "owner": owner,
        "status": status,
        "status_label": status_label or _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "freshness": str(freshness or "-"),
        "freshness_label": _cockpit_freshness_label(freshness),
        "detail": detail,
        "caveat": caveat,
        "next_check": next_check,
        "source_role": source_role,
        "actionability": actionability,
        "counts_for_status": bool(counts_for_status),
    }

def _source_confidence_data_review_count(collection_ops_snapshot: dict[str, Any]) -> int:
    coverage = dict(collection_ops_snapshot.get("coverage") or {})
    return sum(
        _cockpit_int(coverage.get(key))
        for key in ("due_count", "stale_count", "partial_count", "missing_count", "failed_count")
    )

def _event_review_action_summary(events_snapshot: dict[str, Any]) -> dict[str, Any]:
    """Summarize event source actions without merging official and estimate caveats."""
    coverage = dict(events_snapshot.get("coverage") or {})
    rows = _cockpit_frame(events_snapshot)
    if rows.empty:
        return {
            "detail": "event rows unavailable",
            "primary_title": "이벤트 자료 확인",
            "primary_reason": "저장된 event row가 없어 Events 탭의 source 상태를 먼저 봅니다.",
            "primary_action": "Events calendar 수집 상태와 공식/추정 source 구분이 이벤트 자료 주의점입니다.",
            "source_area": "Events",
            "freshness": coverage.get("latest_collected_at") or "-",
            "needs_action": False,
        }

    def series_value(column: str) -> pd.Series:
        if column in rows:
            return rows[column].fillna("").astype(str)
        return pd.Series([""] * len(rows), index=rows.index, dtype=str)

    quality_action = series_value("Quality Action")
    freshness = series_value("Freshness")
    source_type = series_value("Source Type")
    validation = series_value("Validation")
    event_type = series_value("Type")
    type_label = series_value("Type Label")
    quality_review = quality_action.str.strip().ne("") & (quality_action.str.lower() != "no action")
    freshness_review = freshness.str.strip().ne("") & freshness.str.lower().str.contains("stale|unknown|age unknown", regex=True)
    validation_review = validation.str.strip().ne("") & validation.str.lower().isin({"estimate only", "not confirmed", "conflict", "unknown"})
    review_mask = (
        quality_review
        | freshness_review
        | validation_review
    )
    estimate_mask = source_type.str.lower().str.contains("estimate", regex=False) | event_type.str.upper().eq("EARNINGS")
    major_macro_mask = event_type.map(_is_major_macro_event_type)
    official_macro_review_count = int(((major_macro_mask) & review_mask).sum())
    estimate_review_count = int((estimate_mask & review_mask).sum())
    stale_estimate_count = max(
        _cockpit_int(coverage.get("stale_estimate_count")),
        int((freshness.str.lower() == "stale estimate").sum()),
    )
    not_confirmed_count = max(
        _cockpit_int(coverage.get("not_confirmed_count")),
        int((validation.str.lower() == "not confirmed").sum()),
    )
    estimate_only_count = max(
        _cockpit_int(coverage.get("estimate_only_count")),
        int((validation.str.lower() == "estimate only").sum()),
    )
    review_count = max(
        _cockpit_int(coverage.get("needs_review_count")),
        _cockpit_int(coverage.get("action_required_count")),
        int(review_mask.sum()),
    )

    parts: list[str] = []
    if official_macro_review_count:
        parts.append(f"공식 macro/source 확인 {official_macro_review_count}")
    if estimate_review_count:
        parts.append(f"추정 일정 확인 {estimate_review_count}")
    if stale_estimate_count:
        parts.append(f"stale estimate {stale_estimate_count}")
    if not_confirmed_count:
        parts.append(f"미확인 earnings {not_confirmed_count}")
    if estimate_only_count:
        parts.append(f"estimate-only {estimate_only_count}")
    if not parts and review_count:
        parts.append(f"확인 필요 {review_count}")
    if not parts:
        parts.append("공식/추정 source 구분 완료")

    review_rows = rows[review_mask].copy()
    focus_row: dict[str, Any] = {}
    if not review_rows.empty:
        focus_row = dict(review_rows.iloc[0].dropna().to_dict())
    else:
        major_rows = rows[major_macro_mask].copy()
        if not major_rows.empty:
            focus_row = dict(major_rows.iloc[0].dropna().to_dict())
        else:
            focus_row = dict(rows.iloc[0].dropna().to_dict())

    focus_type = str(focus_row.get("Type Label") or focus_row.get("Type") or type_label.iloc[0] or "Event")
    focus_title = str(focus_row.get("Title") or focus_type)
    focus_action = _event_action_copy(focus_row.get("Quality Action"))

    if estimate_review_count or stale_estimate_count or not_confirmed_count or estimate_only_count:
        primary_title = "추정 일정 확인"
        primary_reason = (
            f"{_cockpit_int(coverage.get('estimate_count'))}개 추정 일정 중 "
            f"{estimate_review_count or stale_estimate_count or not_confirmed_count or estimate_only_count}개는 검증/신선도 확인이 필요합니다."
        )
        primary_action = focus_action or "earnings estimate의 cross-check, stale 여부, superseded 여부가 이벤트 자료 주의점입니다."
        source_area = "Events · Earnings estimates"
    elif official_macro_review_count:
        primary_title = "공식 macro 일정 확인"
        primary_reason = f"{focus_type} row의 official source 또는 freshness를 확인해야 합니다."
        primary_action = focus_action or "FOMC/CPI/PPI/Employment/GDP row의 official source와 collected_at 기준이 이벤트 자료 주의점입니다."
        source_area = "Events · Official macro"
    else:
        primary_title = "가까운 주요 이벤트 확인"
        primary_reason = f"{focus_title}가 현재 시장 해석을 바꿀 수 있는 가까운 event입니다."
        primary_action = "recent/upcoming 주요 일정과 source type이 이벤트 배경 근거입니다."
        source_area = "Events · Macro calendar"

    return {
        "detail": " · ".join(parts),
        "primary_title": primary_title,
        "primary_reason": primary_reason,
        "primary_action": primary_action,
        "source_area": source_area,
        "freshness": coverage.get("latest_collected_at") or str(focus_row.get("Collected At") or "-"),
        "focus_title": focus_title,
        "needs_action": bool(review_count),
        "review_count": review_count,
        "official_macro_review_count": official_macro_review_count,
        "estimate_review_count": estimate_review_count,
        "stale_estimate_count": stale_estimate_count,
    }

def _event_action_copy(value: Any) -> str:
    text = str(value or "").strip()
    mapping = {
        "Refresh earnings calendar": "Earnings Calendar 재수집이 추정 일정 신선도 보강 경로입니다.",
        "Treat as unconfirmed; retry later or inspect source": "미확인 추정 일정으로 분류되며, 재수집 또는 source 재검토가 필요합니다.",
        "Enable cross-check or refresh closer to date": "대체 일정 cross-check 또는 발표일 근접 재수집이 보강 경로입니다.",
        "Inspect provider source": "provider source와 수집 시각 기준이 제한입니다.",
        "Inspect source freshness": "공식/source freshness와 collected_at 기준이 제한입니다.",
        "No action": "",
    }
    return mapping.get(text, text)

def build_overview_source_confidence_catalog(
    *,
    market_movers_snapshot: dict[str, Any] | None = None,
    group_leadership_snapshot: dict[str, Any] | None = None,
    futures_macro_snapshot: dict[str, Any] | None = None,
    sentiment_snapshot: dict[str, Any] | None = None,
    events_snapshot: dict[str, Any] | None = None,
    collection_ops_snapshot: dict[str, Any] | None = None,
    market_session_context: dict[str, Any] | None = None,
    include_futures_context: bool = True,
) -> dict[str, Any]:
    """Build a read-only source/provider confidence catalog from already loaded Overview snapshots."""
    movers = market_movers_snapshot or {}
    movers_coverage = dict(movers.get("coverage") or {})
    refresh_state = movers_coverage.get("refresh_state")
    refresh_label = _cockpit_status_text(refresh_state)
    refresh_detail = refresh_state.get("detail") if isinstance(refresh_state, dict) else None
    prices_review = bool(refresh_label and refresh_label.upper() not in {"OK", "SUCCESS", "FRESH"})
    prices_status = _source_confidence_status(movers, review_hint=prices_review, no_data_if_empty=True)
    if _closed_session_intraday_stale(refresh_state or prices_status, "S&P 500 Daily Snapshot", market_session_context):
        prices_status = "OK"
        refresh_label = "Closed session basis"
        refresh_detail = dict(market_session_context or {}).get("brief_subtitle") or refresh_detail
    prices_returnable = _cockpit_int(movers_coverage.get("returnable_count"))
    prices_universe = _cockpit_int(movers_coverage.get("universe_count"))

    groups = group_leadership_snapshot or {}
    group_coverage = dict(groups.get("coverage") or {})
    breadth_status = _source_confidence_status(groups, no_data_if_empty=True)

    futures = futures_macro_snapshot or {}
    futures_coverage = dict(futures.get("coverage") or {})
    futures_status = _source_confidence_status(futures)
    standardized_count = _cockpit_int(futures_coverage.get("standardized_count"))
    futures_symbol_count = _cockpit_int(futures_coverage.get("symbol_count"))

    sentiment = sentiment_snapshot or {}
    sentiment_analysis = dict(sentiment.get("analysis") or {})
    sentiment_confidence = dict(sentiment_analysis.get("data_confidence") or {})
    sentiment_status_text = str(sentiment_confidence.get("status") or sentiment.get("status") or "NO_DATA")
    sentiment_status_normalized = sentiment_status_text.strip().lower()
    if sentiment_status_normalized in {"high", "ok", "fresh"}:
        sentiment_status = "OK"
    elif sentiment_status_normalized == "no_data":
        sentiment_status = "NO_DATA"
    else:
        sentiment_status = _source_confidence_status(sentiment, review_hint=True)
    sentiment_coverage = dict(sentiment.get("coverage") or {})

    events = events_snapshot or {}
    events_coverage = dict(events.get("coverage") or {})
    event_action_summary = _event_review_action_summary(events)
    event_review_count = max(
        _cockpit_int(events_coverage.get("needs_review_count")),
        _cockpit_int(events_coverage.get("action_required_count")),
        _cockpit_int(events_coverage.get("stale_estimate_count")),
        _cockpit_int(event_action_summary.get("review_count")),
    )
    raw_events_status = _source_confidence_status(
        events,
        review_hint=event_review_count > 0,
        no_data_if_empty=True,
    )
    events_status = "REFERENCE_LIMIT" if raw_events_status != "OK" else "OK"

    data_health = collection_ops_snapshot or {}
    data_coverage = dict(data_health.get("coverage") or {})
    data_review_count = _source_confidence_data_review_count(data_health)
    data_status = "META"

    items = [
        _source_confidence_item(
            item_id="prices",
            title="Prices / Movers",
            surface="Market Movers",
            source="Stored price rows and intraday snapshot tables",
            owner="Workspace > Ingestion plus approved Overview bounded refresh",
            status=prices_status,
            freshness=movers_coverage.get("snapshot_time_utc")
            or refresh_detail
            or movers_coverage.get("effective_end_date"),
            detail=f"{prices_returnable}/{prices_universe} symbols returnable · 갱신 상태 {refresh_label or _cockpit_status_label(prices_status)}",
            caveat="가격 맥락은 오래됐거나 부분적일 수 있으며, 주문 실행용 가격이 아닙니다.",
            next_check="Market Movers 기준일과 누락 상태가 가격 맥락의 신뢰도 주의점입니다.",
        ),
        _source_confidence_item(
            item_id="breadth",
            title="Breadth / Groups",
            surface="Sector / Industry",
            source="Stored price rows plus profile sector / industry metadata",
            owner="Overview group leadership read model",
            status=breadth_status,
            freshness=group_coverage.get("snapshot_time_utc") or group_coverage.get("effective_end_date"),
            detail=f"{_cockpit_int(group_coverage.get('returnable_count'))}/{_cockpit_int(group_coverage.get('universe_count'))} symbols grouped",
            caveat="시장 폭은 참여도와 집중도를 요약할 뿐 종목 선택 규칙이 아닙니다.",
            next_check="Sector / Industry freshness와 그룹 coverage가 breadth 맥락의 주의점입니다.",
        ),
        *(
            [
                _source_confidence_item(
                    item_id="futures",
                    title="Futures Context",
                    surface="Futures Macro",
                    source="Stored futures OHLCV read by Macro Thermometer",
                    owner="Workspace > Ingestion futures collector / Overview bounded refresh",
                    status=futures_status,
                    freshness=futures_coverage.get("latest_date") or futures_coverage.get("latest_candle_time"),
                    detail=f"{standardized_count}/{futures_symbol_count} futures symbols standardized",
                    caveat="무료 선물 provider 기반의 배경 자료입니다. 오래됨과 공백은 그대로 보이며 신뢰 보장이 아닙니다.",
                    next_check="Futures Macro의 risk-on, 금리 압력, 안전자산 근거가 macro 배경 자료입니다.",
                )
            ]
            if include_futures_context
            else []
        ),
        _source_confidence_item(
            item_id="sentiment",
            title="Sentiment",
            surface="Sentiment",
            source="CNN Fear & Greed and AAII sentiment observations",
            owner="Market sentiment ingestion and loader",
            status=sentiment_status,
            freshness=sentiment_confidence.get("detail") or sentiment_coverage.get("latest_observation_date"),
            detail=(
                f"CNN {_overview_round(sentiment_coverage.get('cnn_score'))} · "
                f"AAII spread {_overview_round(sentiment_coverage.get('aaii_bull_bear_spread'))}"
            ),
            caveat="심리는 배경 자료일 뿐 다른 화면의 판단이나 운영 상태를 바꾸지 않습니다.",
            next_check="Sentiment 출처 수, 오래된 자료, 신뢰도 저하가 심리 맥락의 주의점입니다.",
        ),
        _source_confidence_item(
            item_id="events",
            title="Events",
            surface="Events",
            source="Official macro calendars plus provider-estimated earnings rows",
            owner="Market event calendar collectors",
            status=events_status,
            freshness=events_coverage.get("latest_collected_at"),
            detail=(
                f"{_cockpit_int(events_coverage.get('event_count'))} events · "
                f"{_cockpit_int(events_coverage.get('official_count'))} official · "
                f"{_cockpit_int(events_coverage.get('estimate_count'))} estimates · "
                f"{event_action_summary['detail']}"
            ),
            caveat="공식 macro 일정과 provider 추정 실적 일정은 구분해서 읽어야 합니다.",
            next_check="-",
            source_role="reference_context",
            actionability="not_actionable",
            counts_for_status=False,
        ),
        _source_confidence_item(
            item_id="data_health",
            title="Data Health",
            surface="Data Health",
            source="DB freshness summaries and local run history",
            owner="Data Health read model and owning collection surfaces",
            status=data_status,
            freshness=data_coverage.get("latest_success_at") or data_coverage.get("latest_auto_at"),
            detail=(
                f"OK {_cockpit_int(data_coverage.get('ok_count'))} · "
                f"확인 필요 {data_review_count}"
            ),
            caveat="Data Health는 자료 관리 메타입니다. 보강 가능한 항목은 필요 자료 보강에 반영됩니다.",
            next_check="-",
            source_role="management_meta",
            actionability="meta",
            counts_for_status=False,
        ),
    ]

    review_items = [item for item in items if item["counts_for_status"] and item["status"] != "OK"]
    reference_items = [item for item in items if not item["counts_for_status"] and item["status"] != "OK"]
    status = "REVIEW" if review_items else "OK"
    status_label = (
        "자료 보강 필요"
        if review_items
        else "자료 정상 · 참고 제한"
        if reference_items
        else "자료 정상"
    )
    prioritized_review_items = sorted(
        review_items,
        key=lambda item: (0 if item["id"] in {"prices", "futures"} else 1, item["id"]),
    )
    return {
        "schema_version": "overview_source_confidence_catalog_v1",
        "status": status,
        "status_label": status_label,
        "summary": {
            "headline": (
                f"확인할 자료 영역 {len(review_items)}개"
                if review_items
                else "자료 기준 정상 · 참고 제한 있음"
                if reference_items
                else "자료 기준 정상"
            ),
            "detail": "같은 저장 자료의 출처, 기준일, 관리 위치, 참고 위치입니다.",
            "review_count": len(review_items),
            "reference_count": len(reference_items),
        },
        "items": items,
        "next_checks": [
            {
                "target_tab": item["surface"],
                "surface": item["surface"],
                "title": item["title"],
                "reason": item["detail"],
                "action": item["next_check"],
                "source_area": item["title"],
                "freshness": item["freshness"],
                "priority": f"P{index}",
                "status": item["status"],
                "status_label": item["status_label"],
                "tone": item["tone"],
            }
            for index, item in enumerate(prioritized_review_items[:4], start=1)
        ],
        "boundary_note": (
            "자료 기준은 context 전용입니다. 거래 실행, 승인/차단 판단, provider 직접 호출, "
            "registry/saved 기록 생성을 하지 않습니다."
        ),
    }

def _cockpit_status_label(status: Any) -> str:
    normalized = _cockpit_status_text(status).strip().lower()
    if normalized in {"ok", "success", "actual", "fresh", "high"}:
        return "자료 정상"
    if normalized == "reference_limit":
        return "참고 제한"
    if normalized == "meta":
        return "관리 메타"
    if normalized in {"review", "due", "partial"}:
        return "자료 확인 필요"
    if normalized == "stale":
        return "자료 오래됨"
    if normalized in {"missing", "no_data", "not_run", "insufficient_data", "no_universe"}:
        return "자료 부족"
    if normalized in {"failed", "error"}:
        return "확인 실패"
    return _cockpit_status_text(status) or "상태 미확인"

def _cockpit_badge_label(label: Any) -> str:
    text = str(label or "").strip()
    mapping = {
        "coverage": "자료 범위",
        "state": "자료 상태",
        "participation": "참여 비율",
        "confidence": "자료 신뢰도",
        "AAII spread": "AAII 온도차",
        "events": "일정",
        "review": "확인 필요",
        "OK": "정상",
        "Risk-On": "위험선호",
        "Rate Pressure": "금리 압력",
        "Safe Haven": "안전자산",
    }
    return mapping.get(text, text)

def _cockpit_freshness_label(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text == "-":
        return "기준일 없음"
    return text

def _cockpit_copy_value(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    if not text or text == "-":
        return fallback
    return text

def _cockpit_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "open", "장중"}:
        return True
    if text in {"0", "false", "no", "n", "off", "closed", "휴장"}:
        return False
    return default

def _market_context_basis_date(*snapshots: dict[str, Any]) -> str | None:
    for snapshot in snapshots:
        coverage = dict((snapshot or {}).get("coverage") or {})
        date_window = dict((snapshot or {}).get("date_window") or {})
        for value in (
            coverage.get("effective_end_date"),
            date_window.get("effective_end_date"),
            coverage.get("snapshot_time_utc"),
            date_window.get("end_date"),
            coverage.get("latest_date"),
            coverage.get("latest_candle_time"),
        ):
            normalized = _iso_date(value)
            if normalized:
                return normalized
    return None

def _market_session_context_model(
    context: dict[str, Any] | None,
    *,
    basis_date: str | None,
) -> dict[str, Any]:
    raw = dict(context or {})
    basis_date = _iso_date(raw.get("basis_date")) or basis_date
    phase = str(raw.get("phase") or raw.get("status") or "장중").strip()
    open_value = raw.get("is_market_open_now", raw.get("is_market_open"))
    is_market_open = _cockpit_bool(open_value, default=phase == "장중")
    trading_value = raw.get("is_trading_day")
    is_trading_day = _cockpit_bool(trading_value, default=phase != "휴장")
    session_date = str(raw.get("session_date") or "").strip()
    reason = str(raw.get("reason") or "").strip()
    basis_text = basis_date or "-"

    if is_market_open:
        title = "오늘의 시장 브리프"
        headline_prefix = "오늘은"
        status_label = "미국장 장중"
        rail_ok_label = "자료 정상"
    elif phase == "장 시작 전":
        title = "개장 전 시장 기준"
        headline_prefix = "개장 전에는"
        status_label = "미국장 장 시작 전"
        rail_ok_label = "자료 정상 · 개장 전 기준"
    elif phase == "장 종료":
        title = "장 마감 기준 시장 브리프"
        headline_prefix = "장 마감 후에는"
        status_label = "미국장 장 종료"
        rail_ok_label = "자료 정상 · 장 마감 기준"
    else:
        title = "마지막 거래일 시장 브리프"
        headline_prefix = "마지막 거래일에는"
        status_label = "미국장 휴장"
        rail_ok_label = "자료 정상 · 휴장 기준"

    subtitle_parts = [f"기준: {basis_text}"]
    if session_date:
        subtitle_parts.append(f"세션: {session_date}")
    subtitle_parts.append(status_label)
    if reason:
        subtitle_parts.append(reason)

    return {
        "phase": phase,
        "session_date": session_date,
        "reason": reason,
        "is_trading_day": is_trading_day,
        "is_market_open_now": is_market_open,
        "is_closed_session": not is_market_open,
        "basis_date": basis_date,
        "brief_title": title,
        "brief_subtitle": " · ".join(part for part in subtitle_parts if part),
        "headline_prefix": headline_prefix,
        "status_label": status_label,
        "rail_ok_label": rail_ok_label,
        "suppress_intraday_refresh": not is_market_open,
    }

def _closed_session_intraday_stale(status: Any, source_area: Any, session_context: dict[str, Any] | None) -> bool:
    if not dict(session_context or {}).get("suppress_intraday_refresh"):
        return False
    source = str(source_area or "").lower()
    status_text = _cockpit_status_text(status).lower()
    if status_text not in {"stale", "due", "update due"}:
        return False
    return any(marker in source for marker in ("intraday", "daily snapshot", "1m ohlcv", "1m", "장중"))

def _apply_market_session_basis_to_cards(cards: list[dict[str, Any]], market_session: dict[str, Any]) -> None:
    if not market_session.get("is_closed_session"):
        return
    basis_date = str(market_session.get("basis_date") or "").strip()
    if not basis_date:
        return
    for card in cards:
        card_id = str(card.get("id") or "")
        if card_id in {"movement", "breadth"}:
            card["freshness"] = basis_date
            card["freshness_label"] = basis_date
        if card_id == "movement" and _closed_session_intraday_stale(
            card.get("status"),
            "S&P 500 Daily Snapshot",
            market_session,
        ):
            card["status"] = "OK"
            card["status_label"] = "휴장 기준"
            card["tone"] = "neutral"
            for badge in list(card.get("badges") or []):
                if str(badge.get("label") or "") == "자료 상태":
                    badge["value"] = "휴장 기준"
                    badge["tone"] = "neutral"

def _build_cockpit_summary_copy(
    cards: Sequence[dict[str, Any]],
    *,
    context_review_count: int,
    market_session: dict[str, Any] | None = None,
) -> tuple[str, str]:
    card_by_id = {str(card.get("id") or ""): card for card in cards}
    movement_card = card_by_id.get("movement") or (cards[0] if len(cards) > 0 else {})
    breadth_card = card_by_id.get("breadth") or (cards[1] if len(cards) > 1 else {})
    futures_card = card_by_id.get("futures")
    movement_value = _cockpit_copy_value(movement_card.get("value"), "")
    breadth_value = _cockpit_copy_value(breadth_card.get("value"), "섹터 리더십 미확인")
    futures_value = _cockpit_copy_value(futures_card.get("value"), "") if futures_card else ""
    headline_prefix = str((market_session or {}).get("headline_prefix") or "오늘은")

    headline = (
        f"{headline_prefix} {movement_value} 같은 상위 움직임을 섹터 확산과 함께 읽는 구간입니다."
        if movement_value
        else f"{headline_prefix} 아직 뚜렷한 상위 변동 종목보다 자료 상태와 확산 여부를 먼저 봅니다."
    )
    breadth_clause = (
        "섹터 리더십은 아직 뚜렷하지 않고"
        if breadth_value == "섹터 리더십 미확인"
        else f"{breadth_value} 리더십이 확인되고"
    )
    if context_review_count:
        next_sentence = (
            f"보강 가능한 자료 {context_review_count}개를 먼저 분리한 뒤 가격 움직임과 배경 근거를 함께 읽으세요."
        )
    else:
        next_sentence = "저장된 DB 자료 기준으로 가격 움직임과 배경 근거를 바로 이어서 읽을 수 있습니다."
    if futures_value:
        detail = f"{breadth_clause}, 선물/매크로 배경은 {futures_value}입니다. {next_sentence}"
    else:
        detail = f"{breadth_clause}, 가까운 이벤트와 자료 상태는 보조 근거로 분리해 읽습니다. {next_sentence}"
    return headline, detail

def _cockpit_score_badges(scores: pd.DataFrame, *, limit: int = 3) -> list[dict[str, Any]]:
    badges: list[dict[str, Any]] = []
    if scores.empty:
        return badges
    for _, row in scores.head(limit).iterrows():
        score_name = str(row.get("Score") or row.get("score") or "-").replace(" Score", "")
        score_value = row.get("Value") if "Value" in row else row.get("value")
        tone = row.get("Tone") if "Tone" in row else row.get("tone")
        badges.append(
            {
                "label": _cockpit_badge_label(score_name),
                "value": "-" if score_value in (None, "") else str(score_value),
                "tone": tone or _cockpit_status_tone(score_value),
            }
        )
    return badges

def _build_cockpit_movement_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    top_row = _cockpit_first_row(snapshot)
    symbol = str(top_row.get("Symbol") or "-")
    move = _cockpit_percent(top_row.get("Return %"))
    name = top_row.get("Name") or symbol
    sector = top_row.get("Sector") or "Unknown sector"
    period = snapshot.get("period_label") or snapshot.get("period") or "Market"
    universe = snapshot.get("universe_label") or snapshot.get("universe_code") or "selected universe"
    refresh_state = coverage.get("refresh_state")
    refresh_detail = refresh_state.get("detail") if isinstance(refresh_state, dict) else None
    status = _cockpit_card_status(refresh_state, snapshot.get("status"))
    if not top_row:
        value = str(snapshot.get("status") or "No data")
        detail = str(snapshot.get("message") or "No stored mover rows are available.")
    else:
        value = f"{symbol} {move}"
        detail = f"{name} · {sector} · {period} · {universe}"
    return {
        "id": "movement",
        "title": "Market Movement",
        "question": "지금 무엇이 움직이나요?",
        "value": value,
        "detail": detail,
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "source": "Market Movers",
        "freshness": coverage.get("effective_end_date") or refresh_detail or coverage.get("snapshot_time_utc") or "-",
        "freshness_label": _cockpit_freshness_label(
            coverage.get("effective_end_date") or refresh_detail or coverage.get("snapshot_time_utc")
        ),
        "target_tab": "Market Movers",
        "badges": [
            {"label": "자료 범위", "value": f"{coverage.get('returnable_count') or 0}/{coverage.get('universe_count') or 0}", "tone": "neutral"},
            {"label": "자료 상태", "value": _cockpit_status_label(status), "tone": _cockpit_status_tone(status)},
        ],
    }

def _build_cockpit_breadth_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    top_row = _cockpit_first_row(snapshot)
    status = _cockpit_card_status(snapshot.get("status"))
    if not top_row:
        value = str(snapshot.get("status") or "No data")
        detail = str(snapshot.get("message") or "No stored sector / industry leadership rows are available.")
        share_value = "-"
    else:
        group = str(top_row.get("Group") or "-")
        weighted = _cockpit_percent(top_row.get("Market Cap Weighted Return %"))
        positive_share = _safe_float(top_row.get("Positive Symbol Share %"))
        share_value = "-" if positive_share is None else f"{positive_share:.0f}%"
        breadth_label = "넓게 확산" if positive_share is not None and positive_share >= 65 else "일부 그룹 집중"
        value = group
        detail = f"{group} 리더십: 시총가중 {weighted} · 상승 종목 {share_value} · {breadth_label}"
    return {
        "id": "breadth",
        "title": "Breadth / Concentration",
        "question": "움직임이 넓게 퍼졌나요, 일부에 집중됐나요?",
        "value": value,
        "detail": detail,
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "source": "Sector / Industry",
        "freshness": coverage.get("effective_end_date") or "-",
        "freshness_label": _cockpit_freshness_label(coverage.get("effective_end_date")),
        "target_tab": "Sector / Industry",
        "badges": [
            {"label": "자료 범위", "value": f"{coverage.get('returnable_count') or 0}/{coverage.get('universe_count') or 0}", "tone": "neutral"},
            {"label": "참여 비율", "value": share_value, "tone": "positive" if share_value != "-" else "neutral"},
        ],
    }

def _build_cockpit_futures_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    summary = dict(snapshot.get("summary") or {})
    scores = _cockpit_frame(snapshot, key="scores")
    status = _cockpit_card_status(snapshot.get("status"))
    scenario = str(summary.get("scenario") or snapshot.get("status") or "Futures context pending")
    detail = str(summary.get("summary") or "Stored futures daily OHLCV provides context only.")
    return {
        "id": "futures",
        "title": "Futures Background",
        "question": "risk-on, rate pressure, safe-haven 중 어떤 배경인가요?",
        "value": scenario,
        "detail": detail,
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(status),
        "source": "Futures Macro Thermometer",
        "freshness": coverage.get("latest_date") or "-",
        "freshness_label": _cockpit_freshness_label(coverage.get("latest_date")),
        "target_tab": "Futures Macro",
        "badges": _cockpit_score_badges(scores) or [
            {"label": "자료 범위", "value": f"{coverage.get('standardized_count') or 0}/{coverage.get('symbol_count') or 0}", "tone": "neutral"}
        ],
    }

def _build_cockpit_sentiment_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    analysis = dict(snapshot.get("analysis") or {})
    confidence = dict(analysis.get("data_confidence") or {})
    confidence_status = confidence.get("status") or snapshot.get("status")
    status = _cockpit_card_status(snapshot.get("status"))
    cnn_score = coverage.get("cnn_score")
    cnn_rating = coverage.get("cnn_rating") or "-"
    spread = coverage.get("aaii_bull_bear_spread")
    return {
        "id": "sentiment",
        "title": "Sentiment Backdrop",
        "question": "시장 심리 배경은 어떤가요?",
        "value": analysis.get("phase_label") or cnn_rating or status,
        "detail": analysis.get("headline") or "CNN Fear & Greed / AAII context is unavailable.",
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": _cockpit_status_tone(confidence_status),
        "source": "CNN Fear & Greed / AAII",
        "freshness": confidence.get("detail") or "-",
        "freshness_label": _cockpit_freshness_label(confidence.get("detail")),
        "target_tab": "Sentiment",
        "badges": [
            {"label": "CNN", "value": "-" if cnn_score in (None, "") else f"{float(cnn_score):.1f} {cnn_rating}", "tone": "neutral"},
            {"label": "AAII 온도차", "value": "-" if spread in (None, "") else f"{float(spread):+.1f}pp", "tone": "neutral"},
            {"label": "자료 신뢰도", "value": _cockpit_status_label(confidence_status), "tone": _cockpit_status_tone(confidence_status)},
        ],
    }

def _cockpit_event_label(row: dict[str, Any]) -> str:
    type_label = str(row.get("Type Label") or "").strip()
    if type_label and type_label != "-":
        return type_label
    return _macro_week_cluster_label(row.get("Type"))

def _cockpit_event_days_value(row: dict[str, Any]) -> int | None:
    value = row.get("Days Until") if row else None
    if value in (None, ""):
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    safe_value = _safe_float(value)
    return int(safe_value) if safe_value is not None else None

def _cockpit_event_days_korean(days: int | None) -> str:
    if days is None:
        return "일정일 확인 필요"
    if days < 0:
        return f"{abs(days)}일 전"
    if days == 0:
        return "오늘"
    return f"{days}일 후"

def _cockpit_major_event_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty or "Type" not in rows:
        return pd.DataFrame()
    return rows[rows["Type"].map(_is_major_macro_event_type)].copy()

def _build_cockpit_events_card(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    rows = _cockpit_frame(snapshot)
    major_rows = _cockpit_major_event_rows(rows)
    if not major_rows.empty and "Days Until" in major_rows:
        major_rows["Days Until"] = pd.to_numeric(major_rows["Days Until"], errors="coerce")
    recent_major = pd.DataFrame()
    upcoming_major = pd.DataFrame()
    if not major_rows.empty and "Days Until" in major_rows:
        recent_major = major_rows[(major_rows["Days Until"] < 0) & (major_rows["Days Until"] >= -EVENT_RECENT_WINDOW_DAYS)].sort_values(
            ["Days Until", "Date", "Type"],
            ascending=[False, False, True],
            kind="mergesort",
        )
        upcoming_major = major_rows[major_rows["Days Until"] >= 0].sort_values(
            ["Days Until", "Date", "Type"],
            kind="mergesort",
        )
    row = dict(recent_major.iloc[0].dropna().to_dict()) if not recent_major.empty else _cockpit_first_row(snapshot)
    next_major = dict(upcoming_major.iloc[0].dropna().to_dict()) if not upcoming_major.empty else {}
    status = _cockpit_card_status(snapshot.get("status"))
    next_date = coverage.get("next_event_date") or next_major.get("Date") or row.get("Date") or row.get("event_date")
    title = row.get("Title") or row.get("title") or row.get("Type Label") or "Upcoming events"
    days = _cockpit_event_days_value(row)
    event_count = _cockpit_int(coverage.get("event_count"))
    review_count = _cockpit_int(coverage.get("needs_review_count"))
    event_label = _cockpit_event_label(row)
    if row and days is not None and days < 0 and _is_major_macro_event_type(row.get("Type")):
        value = f"최근 {event_label} 발표 확인 필요"
    elif next_major:
        next_days = _cockpit_event_days_value(next_major)
        value = f"다음 {_cockpit_event_label(next_major)} {_cockpit_event_days_korean(next_days)}"
    else:
        value = str(next_date or "No upcoming event")
    detail_parts = [str(title), _cockpit_event_days_korean(days)]
    if next_major and row and next_major.get("Type") != row.get("Type"):
        next_days = _cockpit_event_days_value(next_major)
        detail_parts.append(f"다음 {_cockpit_event_label(next_major)} {_cockpit_event_days_korean(next_days)}")
    detail_parts.append(f"주요 일정 {event_count}개")
    return {
        "id": "events",
        "title": "Near Events",
        "question": "가까운 주요 이벤트가 있나요?",
        "value": value,
        "detail": " · ".join(part for part in detail_parts if part and part != "-"),
        "status": "Review" if review_count else status,
        "status_label": _cockpit_status_label("Review" if review_count else status),
        "tone": "warning" if review_count else _cockpit_status_tone(status),
        "source": "Market Event Calendar",
        "freshness": coverage.get("latest_collected_at") or "-",
        "freshness_label": _cockpit_freshness_label(coverage.get("latest_collected_at")),
        "target_tab": "Events",
        "badges": [
            {"label": "일정", "value": str(event_count), "tone": "neutral"},
            {"label": "확인 필요", "value": str(review_count), "tone": "warning" if review_count else "positive"},
        ],
    }

def _build_cockpit_data_card(snapshot: dict[str, Any]) -> tuple[dict[str, Any], int]:
    coverage = dict(snapshot.get("coverage") or {})
    review_count = sum(
        _cockpit_int(coverage.get(key))
        for key in ("due_count", "stale_count", "partial_count", "missing_count", "failed_count")
    )
    status = "META" if review_count else _cockpit_card_status(snapshot.get("status"))
    value = "관리 메타" if review_count else "자료 정상"
    detail = (
        f"Data Health 확인 항목 {review_count}개 중 보강 가능한 항목은 필요 자료 보강에 반영됩니다."
        if review_count
        else "현재 추적 중인 Overview 자료는 바로 참고할 수 있습니다."
    )
    return (
        {
            "id": "data",
            "title": "Data Confidence",
            "question": "이 context를 그대로 참고해도 되나요?",
            "value": value,
            "detail": detail,
            "status": status,
            "status_label": _cockpit_status_label(status),
            "tone": _cockpit_status_tone(status),
            "source": "Data Health",
            "freshness": coverage.get("latest_success_at") or coverage.get("latest_auto_at") or "-",
            "freshness_label": _cockpit_freshness_label(coverage.get("latest_success_at") or coverage.get("latest_auto_at")),
            "target_tab": "Data Health",
            "badges": [
                {"label": "정상", "value": str(coverage.get("ok_count") or 0), "tone": "positive"},
                {"label": "확인 필요", "value": str(review_count), "tone": "warning" if review_count else "positive"},
            ],
        },
        review_count,
    )

def _data_health_collection_action_copy(area: Any, action: Any) -> str:
    area_text = str(area or "").strip()
    mapping = {
        "Futures Monitor 1m OHLCV": "기존 Futures OHLCV 수집 또는 Overview bounded refresh로 선물 가격 이력을 갱신하세요.",
        "Futures Monitor Daily OHLCV": "기존 Futures OHLCV 수집으로 daily 선물 가격 이력을 갱신하세요.",
        "FOMC Calendar": "FOMC calendar 수집을 다시 실행해 공식 일정 row를 보강하세요.",
        "Macro Calendar": "공식 macro calendar 수집 또는 BLS .ics import로 발표 일정을 보강하세요.",
        "Earnings Calendar": "bounded symbol source로 Earnings Calendar를 다시 수집하고 추정 일정 검증 상태를 보강하세요.",
        "S&P 500 Daily Snapshot": "Market Movers의 S&P 500 일중 스냅샷 갱신을 실행하세요.",
        "S&P 500 Universe": "Overview 유니버스 갱신 경로로 S&P 500 constituent snapshot을 갱신하세요.",
        "Market Sentiment": "Market Sentiment 수집으로 CNN / AAII 관측값을 갱신하세요.",
    }
    if area_text in mapping:
        return mapping[area_text]
    text = str(action or "").strip()
    fallback = {
        "Run futures OHLCV collection; Overview bounded refresh is also available for the Futures Monitor.": "기존 Futures OHLCV 수집 또는 Overview bounded refresh를 실행하세요.",
        "Run FOMC calendar collection from the existing market events collector.": "기존 market events collector로 FOMC calendar 수집을 실행하세요.",
        "Run official macro calendar collection or import the BLS .ics file.": "공식 macro calendar 수집 또는 BLS .ics import를 실행하세요.",
        "Run earnings calendar collection with a bounded symbol source.": "bounded symbol source로 earnings calendar 수집을 실행하세요.",
    }
    return fallback.get(text, text or "Owning collection surface에서 필요한 bounded collection을 실행하세요.")

def _cockpit_ops_next_check(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    priority_items = snapshot.get("priority_items")
    if isinstance(priority_items, list) and priority_items:
        item = dict(priority_items[0] or {})
        area = str(item.get("area") or "Data Health")
        target_surface = str(item.get("target_surface") or "Workspace > Ingestion")
        action = _data_health_collection_action_copy(area, item.get("collection_action") or item.get("next_action"))
        return {
            "id": "data_health",
            "target_tab": "Data Health",
            "title": f"{area} 확인",
            "reason": str(item.get("reason") or f"{item.get('status') or 'Review'} · {item.get('freshness') or '-'}"),
            "action": f"{area} 자료 주의점입니다. 필요하면 {target_surface}에서 {action}",
            "source_area": area,
            "freshness": str(item.get("freshness") or "-"),
            "priority": f"P{item.get('rank') or 1}",
            "status": item.get("status") or "REVIEW",
            "status_label": _cockpit_status_label(item.get("status") or "REVIEW"),
            "tone": item.get("tone") or _cockpit_status_tone(item.get("status")),
        }

    rows = _cockpit_frame(snapshot)
    if rows.empty or "Status" not in rows:
        return None
    review_rows = rows[~rows["Status"].astype(str).str.upper().isin(["OK", "SUCCESS"])]
    if review_rows.empty:
        return None
    row = dict(review_rows.iloc[0].dropna().to_dict())
    return {
        "target_tab": "Data Health",
        "title": str(row.get("Area") or "Data Health"),
        "reason": f"{_cockpit_status_label(row.get('Status') or 'Review')} · 자료 기준 {_cockpit_freshness_label(row.get('Data Freshness'))}",
        "action": "Data Health 자료 관리 위치와 필요한 갱신 경로를 봅니다.",
        "source_area": str(row.get("Area") or "Data Health"),
        "freshness": str(row.get("Data Freshness") or "-"),
        "priority": "P1",
        "status": row.get("Status") or "REVIEW",
        "status_label": _cockpit_status_label(row.get("Status") or "REVIEW"),
        "tone": _cockpit_status_tone(row.get("Status")),
    }

def _cockpit_context_finding(
    *,
    item_id: str,
    label: str,
    conclusion: str,
    interpretation: str,
    evidence: str,
    source_area: str,
    freshness: Any,
    priority: str,
    status: Any,
    tone: Any = None,
    repair_hint: str | None = None,
) -> dict[str, Any]:
    status_text = _cockpit_card_status(status)
    finding = {
        "id": item_id,
        "label": label,
        "conclusion": conclusion,
        "interpretation": interpretation,
        "evidence": evidence,
        "source_area": source_area,
        "freshness": str(freshness or "-"),
        "priority": priority,
        "status": status_text,
        "status_label": _cockpit_status_label(status_text),
        "tone": str(tone or _cockpit_status_tone(status_text)),
    }
    if repair_hint:
        finding["repair_hint"] = repair_hint
    return finding

def _cockpit_market_movers_finding(card: dict[str, Any]) -> dict[str, Any]:
    value = str(card.get("value") or "-")
    detail = str(card.get("detail") or "Stored mover rows unavailable.")
    if value == "-" or value.lower() in {"no data", "error", "review"}:
        conclusion = "가격 움직임 자료가 충분하지 않아 상위 움직임 결론의 신뢰도가 낮습니다."
    else:
        conclusion = f"상위 움직임은 {value}입니다."
    return _cockpit_context_finding(
        item_id="market_movers",
        label="가격 움직임",
        conclusion=conclusion,
        interpretation="오늘 브리프의 출발점이며, 섹터 확산과 함께 읽어 단일 종목 영향인지 분리합니다.",
        evidence=detail,
        source_area="Prices / Movers",
        freshness=card.get("freshness_label") or card.get("freshness"),
        priority="P1",
        status=card.get("status"),
        tone=card.get("tone"),
    )

def _cockpit_futures_finding(card: dict[str, Any]) -> dict[str, Any]:
    value = str(card.get("value") or "Futures context pending")
    detail = str(card.get("detail") or "Stored futures OHLCV context unavailable.")
    combined = f"{value} {detail}".lower()
    if "rate pressure" in combined or "금리" in combined:
        interpretation = "주식 강세를 단순 위험선호로만 읽기 어렵고, 금리 민감 영역은 따로 조심해서 읽습니다."
    elif "safe" in combined or "haven" in combined or "안전" in combined:
        interpretation = "위험선호와 안전자산 배경이 섞였는지 보는 보조 맥락입니다."
    else:
        interpretation = "오늘 브리프의 macro backdrop이며, 가격 움직임을 확정하는 근거로 쓰지 않습니다."
    return _cockpit_context_finding(
        item_id="futures",
        label="Futures / Macro",
        conclusion=f"저장된 선물 맥락은 {value} 상태입니다.",
        interpretation=interpretation,
        evidence=detail,
        source_area="Futures Macro Thermometer",
        freshness=card.get("freshness_label") or card.get("freshness"),
        priority="P2",
        status=card.get("status"),
        tone=card.get("tone"),
    )

def _event_context_conclusion(event_action_summary: dict[str, Any]) -> str:
    estimate_limited = (
        _cockpit_int(event_action_summary.get("estimate_review_count"))
        or _cockpit_int(event_action_summary.get("stale_estimate_count"))
        or _cockpit_int(event_action_summary.get("not_confirmed_count"))
        or _cockpit_int(event_action_summary.get("estimate_only_count"))
    )
    if estimate_limited:
        return f"추정 일정 {estimate_limited}개는 검증/신선도 제한이 있어 확정 일정처럼 읽으면 안 됩니다."
    if _cockpit_int(event_action_summary.get("official_macro_review_count")):
        focus_title = str(event_action_summary.get("focus_title") or "공식 macro 일정")
        return f"{focus_title} row는 official source 또는 freshness 제한이 있어 이벤트 배경의 신뢰도가 낮습니다."
    reason = str(event_action_summary.get("primary_reason") or "").strip()
    if reason:
        return (
            reason
            .replace("확인이 필요합니다", "제한이 있습니다")
            .replace("확인해야 합니다", "제한이 있습니다")
            .replace("확인 필요", "자료 제한")
        )
    focus_title = str(event_action_summary.get("focus_title") or "가까운 주요 이벤트")
    return f"{focus_title}가 현재 시장 해석을 바꿀 수 있는 가까운 event입니다."

def _cockpit_events_finding(snapshot: dict[str, Any], card: dict[str, Any]) -> dict[str, Any] | None:
    event_action_summary = _event_review_action_summary(snapshot)
    if not event_action_summary and not card:
        return None
    review_count = _cockpit_int(event_action_summary.get("review_count"))
    status = "REVIEW" if review_count else card.get("status")
    evidence_parts = [
        str(event_action_summary.get("detail") or "").strip(),
        str(event_action_summary.get("focus_title") or card.get("detail") or "").strip(),
    ]
    evidence = " · ".join(part for part in evidence_parts if part and part != "-") or str(card.get("detail") or "-")
    interpretation = (
        "이벤트 자료 제한은 오늘 브리프의 주의점입니다. 공식 macro와 provider 추정 일정은 구분해서 읽습니다."
        if review_count
        else "이벤트는 시장 흐름을 확정하는 근거가 아니라, 오늘 브리프를 읽을 때의 배경 변수입니다."
    )
    return _cockpit_context_finding(
        item_id="events",
        label="Events",
        conclusion=_event_context_conclusion(event_action_summary),
        interpretation=interpretation,
        evidence=evidence,
        source_area=str(event_action_summary.get("source_area") or "Events"),
        freshness=event_action_summary.get("freshness") or card.get("freshness_label") or card.get("freshness"),
        priority="P3" if review_count else "P4",
        status=status,
        tone="warning" if review_count else card.get("tone"),
    )

def _cockpit_data_health_finding(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    data_check = _cockpit_ops_next_check(snapshot)
    if not data_check:
        return None
    source_area = str(data_check.get("source_area") or "Data Health")
    status_label = str(data_check.get("status_label") or _cockpit_status_label(data_check.get("status")))
    reason = str(data_check.get("reason") or "-")
    return _cockpit_context_finding(
        item_id="data_health",
        label="자료 신뢰도",
        conclusion=f"{source_area} 자료 상태가 {status_label}입니다.",
        interpretation="시장 결론을 바꾸는 근거가 아니라, 현재 브리프를 읽을 때의 자료 주의점입니다.",
        evidence=reason,
        source_area=source_area,
        freshness=data_check.get("freshness"),
        priority="P4",
        status=data_check.get("status"),
        tone=data_check.get("tone"),
        repair_hint="필요 자료 보강에서 기존 Overview 갱신 경로로 보강할 수 있습니다.",
    )

def _build_cockpit_context_findings(
    *,
    cards: list[dict[str, Any]],
    events_snapshot: dict[str, Any],
    data_health_handoff: dict[str, Any],
) -> list[dict[str, Any]]:
    card_by_id = {str(card.get("id") or ""): card for card in cards}
    findings: list[dict[str, Any] | None] = [
        _cockpit_market_movers_finding(card_by_id.get("movement") or {}),
        _cockpit_futures_finding(card_by_id.get("futures") or {}) if "futures" in card_by_id else None,
        _cockpit_events_finding(events_snapshot, card_by_id.get("events") or {}),
        _cockpit_data_health_finding(data_health_handoff),
    ]
    return [finding for finding in findings if finding is not None][:4]

def _cockpit_brief_row(card: dict[str, Any], *, label: str) -> dict[str, Any]:
    """Project an existing cockpit card into a sentence-first brief row."""
    return {
        "id": card.get("id"),
        "label": label,
        "value": card.get("value"),
        "detail": card.get("detail"),
        "status": card.get("status"),
        "status_label": card.get("status_label"),
        "tone": card.get("tone"),
        "target_tab": card.get("target_tab"),
        "source": card.get("source"),
        "freshness_label": card.get("freshness_label"),
        "badges": card.get("badges"),
    }

def _cockpit_event_brief_row(finding: dict[str, Any]) -> dict[str, Any]:
    """Project event context into the market brief as an interpretation result."""
    finding_id = str(finding.get("id") or "").strip()
    source_area = str(finding.get("source_area") or finding.get("label") or "-").strip()
    conclusion = str(finding.get("conclusion") or "").strip()
    evidence = str(finding.get("evidence") or "").strip()
    lower_text = f"{source_area} {conclusion} {evidence}".lower()
    status = str(finding.get("status") or "").strip().upper()
    if "추정" in conclusion or "estimate" in lower_text or status == "REVIEW":
        value = "직접 원인 근거 약함"
        if "추정" in conclusion or "estimate" in lower_text:
            detail = "추정 일정이 많아 오늘 움직임의 원인을 이벤트로 단정하지 않습니다."
        else:
            detail = f"{conclusion} 오늘 움직임의 원인으로 단정하지 않습니다."
    elif "확인" in conclusion or "제한" in lower_text or "review" in lower_text:
        value = "이벤트 원인 해석 보류"
        detail = f"{conclusion} 오늘 움직임과 직접 연결하기보다 배경 변수로만 둡니다."
    else:
        value = "가까운 이벤트 참고"
        detail = f"{conclusion} 오늘 가격 움직임의 직접 원인으로 단정하지는 않습니다."
    detail = detail.replace("event", "이벤트")
    return {
        "id": finding_id or "events",
        "label": "이벤트 배경",
        "value": value,
        "detail": detail,
        "status": finding.get("status"),
        "status_label": finding.get("status_label"),
        "tone": finding.get("tone"),
        "target_tab": source_area,
        "source": source_area,
        "freshness": finding.get("freshness"),
        "freshness_label": finding.get("freshness"),
        "evidence": finding.get("evidence"),
    }

def _cockpit_apply_futures_data_limit(
    row: dict[str, Any],
    findings: list[dict[str, Any]],
    data_health_handoff: dict[str, Any],
    market_session_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fold a Futures data-health limitation into the Futures/Macro brief row."""
    handoff_items = [
        {
            "id": "data_health",
            "source_area": item.get("area"),
            "freshness": item.get("freshness"),
            "status": item.get("status"),
            "status_label": _cockpit_status_label(item.get("status") or "REVIEW"),
        }
        for item in list(data_health_handoff.get("priority_items") or [])
        if isinstance(item, dict)
    ]
    data_finding = next(
        (
            finding
            for finding in [*findings, *handoff_items]
            if str(finding.get("id") or "").strip() == "data_health"
            and any(
                marker in str(finding.get("source_area") or finding.get("evidence") or "").lower()
                for marker in ("futures", "ohlcv", "선물")
            )
        ),
        None,
    )
    if not data_finding:
        return row
    if _closed_session_intraday_stale(
        data_finding.get("status"),
        data_finding.get("source_area") or data_finding.get("evidence"),
        market_session_context,
    ):
        return row
    limited = dict(row)
    source_area = str(data_finding.get("source_area") or "Futures Monitor 1m OHLCV").strip()
    limited["value"] = "장중 macro 해석 보류"
    limited["detail"] = f"{source_area}가 오래되어 risk-on / 금리 압력 설명은 낮게 봅니다."
    limited["status"] = data_finding.get("status") or row.get("status")
    limited["status_label"] = data_finding.get("status_label") or row.get("status_label")
    limited["tone"] = "warning"
    limited["target_tab"] = "Futures Monitor"
    limited["source"] = source_area
    limited["source_area"] = source_area
    limited["freshness_label"] = data_finding.get("freshness") or row.get("freshness_label")
    return limited

REFRESH_PLAN_BY_AREA: dict[str, dict[str, str]] = {
    "S&P 500 Daily Snapshot": {
        "action_id": "sp500_intraday_snapshot",
        "label": "S&P 500 snapshot",
        "resolution": "resolvable",
        "limitation": "시장 휴장 또는 provider 지연이면 최신 snapshot이 없을 수 있습니다.",
    },
    "Top1000 Daily Snapshot": {
        "action_id": "top1000_intraday_snapshot",
        "label": "Top1000 snapshot",
        "resolution": "resolvable",
        "limitation": "시장 휴장 또는 provider 지연이면 최신 snapshot이 없을 수 있습니다.",
    },
    "Top2000 Daily Snapshot": {
        "action_id": "top2000_intraday_snapshot",
        "label": "Top2000 snapshot",
        "resolution": "resolvable",
        "limitation": "시장 휴장 또는 provider 지연이면 최신 snapshot이 없을 수 있습니다.",
    },
    "S&P 500 Universe": {
        "action_id": "sp500_universe",
        "label": "S&P 500 universe",
        "resolution": "resolvable",
        "limitation": "공식 구성 변경 반영 시점에 따라 기존 universe가 유지될 수 있습니다.",
    },
    "Futures Monitor 1m OHLCV": {
        "action_id": "futures_1m",
        "label": "Futures 1m",
        "resolution": "resolvable",
        "limitation": "시장 휴장 또는 provider 지연이면 stale 상태가 남을 수 있습니다.",
    },
    "Futures Monitor Daily OHLCV": {
        "action_id": "futures_daily",
        "label": "Futures daily",
        "resolution": "resolvable",
        "limitation": "provider daily bar 지연이면 최근 기준일이 남을 수 있습니다.",
    },
    "Market Sentiment": {
        "action_id": "market_sentiment",
        "label": "Sentiment",
        "resolution": "resolvable",
        "limitation": "CNN / AAII source 지연이나 실패가 있으면 기존 관측값을 유지합니다.",
    },
    "FOMC Calendar": {
        "action_id": "fomc_calendar",
        "label": "FOMC calendar",
        "resolution": "resolvable",
        "limitation": "공식 일정 page가 변하지 않았다면 표시 내용이 그대로일 수 있습니다.",
    },
    "Macro Calendar": {
        "action_id": "macro_calendar",
        "label": "Macro calendar",
        "resolution": "resolvable",
        "limitation": "공식 source coverage 밖의 이벤트는 보강 후에도 비어 있을 수 있습니다.",
    },
    "Earnings Calendar": {
        "action_id": "earnings_calendar",
        "label": "Earnings calendar",
        "resolution": "partial",
        "limitation": "재수집해도 provider 추정 일정이면 직접 원인 근거로 쓰지 않습니다.",
    },
}

REFRESH_PLAN_ACTION_ORDER = {
    "sp500_intraday_snapshot": 10,
    "top1000_intraday_snapshot": 11,
    "top2000_intraday_snapshot": 12,
    "sp500_universe": 13,
    "futures_1m": 20,
    "futures_daily": 21,
    "market_sentiment": 30,
    "fomc_calendar": 40,
    "macro_calendar": 41,
    "earnings_calendar": 50,
}

MARKET_CONTEXT_DIRECT_REFRESH_AREAS = {
    "S&P 500 Daily Snapshot",
    "S&P 500 Universe",
    "Market Sentiment",
    "FOMC Calendar",
    "Macro Calendar",
    "Earnings Calendar",
}

def _refresh_plan_item(
    *,
    source_area: str,
    status: Any,
    freshness: Any,
    reason: Any,
    target_surface: Any = None,
) -> dict[str, Any] | None:
    spec = REFRESH_PLAN_BY_AREA.get(source_area)
    if not spec:
        return None
    resolution = str(spec["resolution"])
    return {
        "source_area": source_area,
        "label": spec["label"],
        "action_id": spec["action_id"],
        "resolution": resolution,
        "resolution_label": "보강 가능" if resolution == "resolvable" else "일부 보강",
        "status": status,
        "status_label": _cockpit_status_label(status),
        "tone": "warning" if resolution == "partial" else _cockpit_status_tone(status),
        "freshness": str(freshness or "-"),
        "reason": str(reason or "-"),
        "limitation": spec["limitation"],
        "target_surface": str(target_surface or "-"),
    }

def _refresh_plan_excluded_event(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_area": "Events",
        "label": "Events calendar caveat",
        "action_id": None,
        "resolution": "not_actionable",
        "resolution_label": "보강 대상 아님",
        "status": finding.get("status") or "REVIEW",
        "status_label": _cockpit_status_label(finding.get("status") or "REVIEW"),
        "tone": "neutral",
        "freshness": str(finding.get("freshness") or "-"),
        "reason": str(finding.get("conclusion") or "이벤트 일정은 참고 정보입니다."),
        "limitation": "현재 이벤트 정보는 원인 분석 엔진이 아니므로 시장 브리프의 직접 결론으로 쓰지 않습니다.",
        "target_surface": "Events",
    }

def _cockpit_refresh_plan(
    *,
    cards: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    data_health_handoff: dict[str, Any],
    market_session_context: dict[str, Any] | None = None,
    direct_market_context_refresh_only: bool = False,
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    excluded_items: list[dict[str, Any]] = []
    seen_actions: set[str] = set()

    movement = cards[0] if cards else {}
    if (
        _cockpit_status_tone(movement.get("status")) in {"warning", "danger"}
        and not _closed_session_intraday_stale(
            movement.get("status"),
            "S&P 500 Daily Snapshot",
            market_session_context,
        )
    ):
        item = _refresh_plan_item(
            source_area="S&P 500 Daily Snapshot",
            status=movement.get("status"),
            freshness=movement.get("freshness_label") or movement.get("freshness"),
            reason=movement.get("detail"),
            target_surface="Workspace > Overview > Market Movers > 일중 스냅샷 갱신",
        )
        if item and str(item["action_id"]) not in seen_actions:
            seen_actions.add(str(item["action_id"]))
            items.append(item)

    for priority_item in list(data_health_handoff.get("priority_items") or []):
        if not isinstance(priority_item, dict):
            continue
        source_area = str(priority_item.get("area") or "").strip()
        if direct_market_context_refresh_only and source_area not in MARKET_CONTEXT_DIRECT_REFRESH_AREAS:
            continue
        if _closed_session_intraday_stale(priority_item.get("status"), source_area, market_session_context):
            continue
        item = _refresh_plan_item(
            source_area=source_area,
            status=priority_item.get("status"),
            freshness=priority_item.get("freshness"),
            reason=priority_item.get("reason") or priority_item.get("next_action"),
            target_surface=priority_item.get("target_surface") or priority_item.get("alternate_surface"),
        )
        if item and str(item["action_id"]) not in seen_actions:
            seen_actions.add(str(item["action_id"]))
            items.append(item)

    for finding in findings:
        if str(finding.get("id") or "").strip() == "events" and str(finding.get("status") or "").upper() != "OK":
            excluded_items.append(_refresh_plan_excluded_event(finding))

    items = sorted(
        items,
        key=lambda item: (
            REFRESH_PLAN_ACTION_ORDER.get(str(item.get("action_id") or ""), 999),
            str(item.get("source_area") or ""),
        ),
    )
    partial_count = sum(1 for item in items if item.get("resolution") == "partial")
    closed_session = bool(dict(market_session_context or {}).get("is_closed_session"))
    return {
        "schema_version": "overview_market_context_refresh_plan_v1",
        "status": "READY" if items else "NO_ACTION",
        "summary": {
            "headline": f"현재 보강 대상 {len(items)}개" if items else "현재 보강할 자료 이슈 없음",
            "detail": (
                "현재 브리프에서 실제 갱신 가능한 자료만 실행합니다."
                if items
                else "미국장 휴장 / 장외 시간에는 장중 snapshot 경과 시간만으로 보강하지 않습니다."
                if closed_session
                else "이벤트 caveat처럼 수집으로 해결되지 않는 제한은 보강 대상에서 제외합니다."
            ),
            "action_count": len(items),
            "partial_count": partial_count,
            "excluded_count": len(excluded_items),
            "primary_button_label": "현재 이슈만 보강" if items else "현재 보강 없음",
            "full_refresh_label": "전체 Market Context 자료 보강",
            "closed_session": closed_session,
        },
        "items": items,
        "excluded_items": excluded_items,
        "action_ids": [str(item["action_id"]) for item in items if item.get("action_id")],
        "boundary_note": "Smart refresh는 저장 자료 보강 job만 실행하며 시장 결론, 추천, 검증 gate, 운영 signal을 만들지 않습니다.",
    }

def build_overview_macro_context_cockpit(
    *,
    market_movers_snapshot: dict[str, Any] | None = None,
    group_leadership_snapshot: dict[str, Any] | None = None,
    futures_macro_snapshot: dict[str, Any] | None = None,
    sentiment_snapshot: dict[str, Any] | None = None,
    events_snapshot: dict[str, Any] | None = None,
    collection_ops_snapshot: dict[str, Any] | None = None,
    historical_analog_snapshot: dict[str, Any] | None = None,
    market_session_context: dict[str, Any] | None = None,
    include_futures_macro: bool = True,
    direct_market_context_refresh_only: bool = False,
) -> dict[str, Any]:
    """Build a summary-first Overview cockpit from existing read-only market context snapshots."""
    if market_movers_snapshot is None:
        try:
            market_movers_snapshot = build_market_movers_snapshot(
                universe_code="SP500",
                period="daily",
                top_n=10,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            market_movers_snapshot = _cockpit_error_snapshot("Market movers", exc)
    if group_leadership_snapshot is None:
        try:
            group_leadership_snapshot = build_group_leadership_snapshot(
                universe_code="SP500",
                group_by="sector",
                period="daily",
                top_n=10,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            group_leadership_snapshot = _cockpit_error_snapshot("Sector leadership", exc)
    if include_futures_macro and futures_macro_snapshot is None:
        try:
            from app.services.futures_macro_thermometer import load_overview_futures_macro_snapshot

            futures_macro_snapshot = load_overview_futures_macro_snapshot()
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            futures_macro_snapshot = _cockpit_error_snapshot("Futures macro", exc)
    if sentiment_snapshot is None:
        try:
            sentiment_snapshot = build_market_sentiment_snapshot()
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            sentiment_snapshot = _cockpit_error_snapshot("Market sentiment", exc)
    if events_snapshot is None:
        try:
            events_snapshot = build_market_events_snapshot(event_type=None, horizon_days=60, limit=100)
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            events_snapshot = _cockpit_error_snapshot("Market events", exc)
    if collection_ops_snapshot is None:
        try:
            collection_ops_snapshot = build_collection_ops_snapshot()
        except Exception as exc:  # pragma: no cover - defensive fallback for UI display
            collection_ops_snapshot = _cockpit_error_snapshot("Data Health", exc)

    movement_card = _build_cockpit_movement_card(market_movers_snapshot)
    breadth_card = _build_cockpit_breadth_card(group_leadership_snapshot)
    futures_card = _build_cockpit_futures_card(futures_macro_snapshot or {}) if include_futures_macro else None
    sentiment_card = _build_cockpit_sentiment_card(sentiment_snapshot)
    events_card = _build_cockpit_events_card(events_snapshot)
    cards = [
        movement_card,
        breadth_card,
        *([futures_card] if futures_card is not None else []),
        sentiment_card,
        events_card,
    ]
    data_card, data_review_count = _build_cockpit_data_card(collection_ops_snapshot)
    cards.append(data_card)
    card_by_id = {str(card.get("id") or ""): card for card in cards}
    market_session = _market_session_context_model(
        market_session_context,
        basis_date=_market_context_basis_date(
            market_movers_snapshot,
            group_leadership_snapshot,
            futures_macro_snapshot if include_futures_macro else {},
        ),
    )
    _apply_market_session_basis_to_cards(cards, market_session)

    review_cards = [
        card for card in cards
        if str(card.get("id") or "") not in {"events", "data"}
        and _cockpit_status_tone(card.get("status")) in {"warning", "danger"}
        and not _closed_session_intraday_stale(card.get("status"), card.get("source") or card.get("title"), market_session)
    ]
    source_confidence = build_overview_source_confidence_catalog(
        market_movers_snapshot=market_movers_snapshot,
        group_leadership_snapshot=group_leadership_snapshot,
        futures_macro_snapshot=futures_macro_snapshot,
        sentiment_snapshot=sentiment_snapshot,
        events_snapshot=events_snapshot,
        collection_ops_snapshot=collection_ops_snapshot,
        market_session_context=market_session,
        include_futures_context=include_futures_macro,
    )
    data_health_handoff = build_overview_data_health_ingestion_handoff(collection_ops_snapshot, limit=3)
    context_findings = _build_cockpit_context_findings(
        cards=cards,
        events_snapshot=events_snapshot,
        data_health_handoff=data_health_handoff,
    )
    brief_context_findings = [
        item
        for item in context_findings
        if str(item.get("id") or "").strip() in {"events", "data_health"}
    ]
    refresh_plan = _cockpit_refresh_plan(
        cards=cards,
        findings=brief_context_findings,
        data_health_handoff=data_health_handoff,
        market_session_context=market_session,
        direct_market_context_refresh_only=direct_market_context_refresh_only,
    )
    refresh_summary = dict(refresh_plan.get("summary") or {})
    actionable_refresh_count = _cockpit_int(refresh_summary.get("action_count"))
    reference_limit_count = _cockpit_int(refresh_summary.get("excluded_count")) + _cockpit_int(
        dict(source_confidence.get("summary") or {}).get("reference_count")
    )
    status = "REVIEW" if actionable_refresh_count or review_cards else "OK"
    summary_status_label = (
        "자료 보강 필요"
        if actionable_refresh_count
        else str(market_session.get("rail_ok_label"))
        if market_session.get("is_closed_session")
        else "자료 정상 · 참고 제한"
        if reference_limit_count
        else "자료 정상"
    )
    context_review_count = actionable_refresh_count
    next_path = " → ".join(
        str(item.get("source_area") or item.get("label") or "-")
        for item in list(refresh_plan.get("items") or [])
        if str(item.get("source_area") or item.get("label") or "").strip()
    ) or ("참고 제한 분리" if reference_limit_count else "추가 보조 맥락 없음")
    sector_pressure = build_overview_breadth_heatmap_summary(group_leadership_snapshot)
    event_timeline = build_overview_macro_week_lane(events_snapshot, horizon_days=14, limit=6)
    summary_headline, summary_detail = _build_cockpit_summary_copy(
        cards,
        context_review_count=context_review_count,
        market_session=market_session,
    )
    rail = [
        {
            "label": "자료 상태",
            "value": (
                f"보강 가능 자료 {actionable_refresh_count}개"
                if actionable_refresh_count
                else str(market_session.get("rail_ok_label"))
                if market_session.get("is_closed_session")
                else "자료 정상 · 참고 제한 있음"
                if reference_limit_count
                else "자료 정상"
            ),
            "detail": (
                "필요 자료 보강에서 실행 가능"
                if actionable_refresh_count
                else str(market_session.get("brief_subtitle") or "마지막 저장 기준")
                if market_session.get("is_closed_session")
                else "참고 제한 / 관리 메타는 근거에 분리"
                if reference_limit_count
                else "바로 참고 가능"
            ),
            "tone": _cockpit_status_tone(status),
        },
        {
            "label": "Top Mover",
            "value": str(card_by_id.get("movement", {}).get("value") or "-"),
            "detail": str(card_by_id.get("movement", {}).get("freshness_label") or card_by_id.get("movement", {}).get("target_tab") or "Market Movers"),
            "tone": card_by_id.get("movement", {}).get("tone") or "neutral",
        },
        {
            "label": "Breadth",
            "value": str(card_by_id.get("breadth", {}).get("value") or "-"),
            "detail": str(card_by_id.get("breadth", {}).get("freshness_label") or card_by_id.get("breadth", {}).get("target_tab") or "Group Leadership"),
            "tone": card_by_id.get("breadth", {}).get("tone") or "neutral",
        },
        *(
            [
                {
                    "label": "Macro",
                    "value": str(card_by_id.get("futures", {}).get("value") or "-"),
                    "detail": str(card_by_id.get("futures", {}).get("freshness_label") or card_by_id.get("futures", {}).get("target_tab") or "Futures Macro"),
                    "tone": card_by_id.get("futures", {}).get("tone") or "neutral",
                }
            ]
            if include_futures_macro
            else []
        ),
        {
            "label": "Next Event",
            "value": str(card_by_id.get("events", {}).get("value") or "-"),
            "detail": str(card_by_id.get("events", {}).get("freshness_label") or card_by_id.get("events", {}).get("target_tab") or "Events"),
            "tone": card_by_id.get("events", {}).get("tone") or "neutral",
        },
    ]
    for index, card in enumerate(cards):
        card_id = str(card.get("id") or "")
        card["group"] = "core" if card_id in {"movement", "breadth", "futures"} else "supporting"
        card["priority_label"] = "시장 브리프" if card_id in {"movement", "breadth", "futures"} else ("근거" if card_id == "data" else "다음 맥락")

    brief_rows = [
        _cockpit_brief_row(card_by_id.get("movement") or {}, label="무엇이 움직였나"),
        _cockpit_brief_row(card_by_id.get("breadth") or {}, label="확산/집중인가"),
    ]
    if include_futures_macro and "futures" in card_by_id:
        brief_rows.append(
            _cockpit_apply_futures_data_limit(
                _cockpit_brief_row(card_by_id["futures"], label="Futures/Macro 배경"),
                brief_context_findings,
                data_health_handoff,
                market_session,
            )
        )
    else:
        event_finding = next(
            (item for item in context_findings if str(item.get("id") or "") == "events"),
            None,
        )
        if event_finding:
            brief_rows.append(_cockpit_event_brief_row(event_finding))
    interpretation_cues = [
        _cockpit_brief_row(card_by_id.get("events") or {}, label="이벤트 압력"),
        _cockpit_brief_row(card_by_id.get("sentiment") or {}, label="심리 확인"),
    ]
    if include_futures_macro and "futures" in card_by_id:
        interpretation_cues.append(_cockpit_brief_row(card_by_id["futures"], label="매크로 확인"))

    return {
        "schema_version": "overview_macro_context_cockpit_v1",
        "status": status,
        "summary": {
            "headline": summary_headline,
            "detail": summary_detail,
            "tone": _cockpit_status_tone(status),
            "status_label": summary_status_label,
            "review_count": context_review_count,
            "data_review_count": data_review_count,
            "next_path": next_path,
            "rail": rail,
        },
        "brief_rows": brief_rows,
        "market_session": market_session,
        "refresh_plan": refresh_plan,
        "interpretation_cues": interpretation_cues,
        "sector_pressure": sector_pressure,
        "event_timeline": event_timeline,
        "historical_analog": historical_analog_snapshot or {},
        "cards": cards,
        "context_findings": context_findings,
        "brief_context_findings": brief_context_findings,
        "next_checks": context_findings,
        "data_health_handoff": data_health_handoff,
        "source_confidence": source_confidence,
        "boundary_note": (
            "context 전용 market backdrop입니다. 이 cockpit은 거래 실행, 승인/차단 판단, "
            "registry/saved 기록, broker order, auto rebalance를 만들지 않습니다."
        ),
    }

__all__ = [
    "build_overview_source_confidence_catalog",
    "build_overview_macro_context_cockpit",
]
