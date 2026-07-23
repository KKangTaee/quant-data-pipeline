from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
from math import isfinite
from typing import Any, Mapping, Sequence

from app.services.today_market_session import build_us_market_session_model


TODAY_SCHEMA_VERSION = "today_home_v4"
_UNAVAILABLE_STATUSES = {
    "",
    "ERROR",
    "FAILED",
    "MISSING",
    "NO_DATA",
    "NOT_RUN",
    "UNAVAILABLE",
}
_SIGNAL_LABELS = {
    "support": ("지지 신호", "위험도 낮음"),
    "neutral": ("중립 신호", "위험도 중간"),
    "watch": ("주의 신호", "위험도 높음"),
    "limited": ("자료 제한", "판단 제한"),
}


def _as_mapping(value: Any) -> dict[str, Any]:
    if is_dataclass(value) and not isinstance(value, type):
        return dict(asdict(value))
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _records(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if hasattr(value, "to_dict"):
        try:
            rows = value.to_dict(orient="records")
        except TypeError:
            rows = value.to_dict()
        if isinstance(rows, list):
            return [_as_mapping(row) for row in rows]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_as_mapping(row) for row in value]
    return []


def _safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if isfinite(numeric) else None


def _text(value: Any, default: str = "-") -> str:
    text = str(value or "").strip()
    return text if text else default


def _date_text(value: Any) -> str | None:
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]
    text = str(value or "").strip()
    return text[:10] if text else None


def _status(value: Any) -> str:
    return str(value or "").strip().upper()


def _available(value: Any) -> bool:
    return _status(value) not in _UNAVAILABLE_STATUSES


def _economic_cycle_evidence(model: Any) -> dict[str, Any]:
    source = _as_mapping(model)
    headline = _as_mapping(source.get("headline"))
    source_status = _status(source.get("status"))
    if not _available(source_status):
        return {
            "key": "economic_cycle",
            "label": "경제 사이클",
            "status": "UNAVAILABLE",
            "title": "자료 없음",
            "detail": "저장된 경제사이클 판단을 확인할 수 없습니다.",
            "as_of_date": _date_text(source.get("as_of_date")),
            "tone": "neutral",
            "_semantic_code": "",
        }
    return {
        "key": "economic_cycle",
        "label": "경제 사이클",
        "status": "READY" if source_status == "READY" else "PARTIAL",
        "title": _text(headline.get("phase_label"), "판단 제한"),
        "detail": _text(headline.get("summary"), "경제 국면 근거가 제한적입니다."),
        "as_of_date": _date_text(source.get("as_of_date")),
        "tone": "positive" if source_status == "READY" else "warning",
        "_semantic_code": _text(headline.get("phase"), ""),
    }


def _sp500_evidence(model: Any) -> dict[str, Any]:
    source = _as_mapping(model)
    multiple = _as_mapping(source.get("multiple_regime"))
    source_status = _status(multiple.get("status") or source.get("status"))
    current = _safe_float(multiple.get("current_pe"))
    mean = _safe_float(multiple.get("mean_multiple"))
    basis_date = _date_text(multiple.get("current_basis_date"))
    status_ready = source_status in {"OK", "READY"}
    has_usable_range = current is not None and mean is not None and basis_date is not None
    if not status_ready and not has_usable_range:
        return {
            "key": "sp500",
            "label": "S&P 500",
            "status": "UNAVAILABLE",
            "title": "자료 없음",
            "detail": "저장된 후행 PER 범위를 확인할 수 없습니다.",
            "as_of_date": basis_date,
            "tone": "neutral",
            "provisional": False,
            "_semantic_code": "",
        }
    bucket = _text(multiple.get("bucket"), "UNKNOWN").upper()
    bucket_label = {
        "VERY_HIGH": "매우 높은 구간",
        "HIGH": "상단 구간",
        "MID": "중간 구간",
        "NEUTRAL": "중간 구간",
        "LOW": "하단 구간",
        "VERY_LOW": "매우 낮은 구간",
    }.get(bucket, "범위 확인")
    detail = "후행 PER의 저장 범위를 확인합니다."
    if current is not None and mean is not None:
        detail = f"후행 PER {current:.1f}배 · 60개월 중심 {mean:.1f}배"
    provisional = bool(multiple.get("current_is_provisional")) or not status_ready
    return {
        "key": "sp500",
        "label": "S&P 500",
        "status": "PARTIAL" if provisional else "READY",
        "title": bucket_label,
        "detail": detail,
        "as_of_date": basis_date,
        "tone": "warning" if bucket in {"HIGH", "VERY_HIGH"} else "neutral",
        "provisional": provisional,
        "_semantic_code": bucket,
    }


def _futures_evidence(model: Any) -> dict[str, Any]:
    source = _as_mapping(model)
    source_status = _status(source.get("status"))
    metadata = _as_mapping(source.get("metadata"))
    if source_status != "READY":
        return {
            "key": "futures_macro",
            "label": "선물 매크로",
            "status": "UNAVAILABLE",
            "title": "자료 없음",
            "detail": _text(
                source.get("reason"),
                "저장된 선물 매크로 snapshot을 확인할 수 없습니다.",
            ),
            "as_of_date": _date_text(metadata.get("as_of_date")),
            "tone": "neutral",
            "_semantic_code": "",
        }
    macro = _as_mapping(source.get("macro"))
    summary = _as_mapping(macro.get("summary"))
    macro_status = _status(macro.get("status"))
    return {
        "key": "futures_macro",
        "label": "선물 매크로",
        "status": "READY" if macro_status in {"OK", "READY"} else "PARTIAL",
        "title": _text(summary.get("scenario"), "현재 재가격화 확인"),
        "detail": _text(summary.get("summary"), "저장된 선물 일봉의 현재 패턴을 확인합니다."),
        "as_of_date": _date_text(metadata.get("as_of_date")),
        "tone": _text(summary.get("tone") or macro.get("tone"), "neutral"),
        "_semantic_code": _text(summary.get("tone") or macro.get("tone"), "neutral"),
    }


def _sentiment_evidence(model: Any) -> dict[str, Any]:
    source = _as_mapping(model)
    source_status = _status(source.get("status"))
    analysis = _as_mapping(source.get("analysis"))
    coverage = _as_mapping(source.get("coverage"))
    axes = _as_mapping(analysis.get("axes"))
    behavior = _as_mapping(axes.get("market_behavior"))
    survey = _as_mapping(axes.get("investor_survey"))
    dates = [
        value
        for value in (
            _date_text(behavior.get("latest_date")),
            _date_text(survey.get("latest_date")),
        )
        if value
    ]
    if not _available(source_status):
        return {
            "key": "sentiment",
            "label": "시장 심리",
            "status": "UNAVAILABLE",
            "title": "자료 없음",
            "detail": "CNN·AAII 저장 관측을 확인할 수 없습니다.",
            "as_of_date": max(dates) if dates else None,
            "tone": "neutral",
            "_semantic_code": "",
        }
    stale_count = int(_safe_float(coverage.get("stale_count")) or 0)
    missing_count = int(_safe_float(coverage.get("missing_count")) or 0)
    return {
        "key": "sentiment",
        "label": "시장 심리",
        "status": "PARTIAL" if stale_count or missing_count else "READY",
        "title": _text(analysis.get("phase_label"), "심리 판단 제한"),
        "detail": _text(analysis.get("headline"), "저장된 심리 관측을 확인합니다."),
        "as_of_date": max(dates) if dates else None,
        "tone": _text(analysis.get("tone"), "neutral"),
        "_semantic_code": _text(analysis.get("tone"), "neutral"),
    }


def _evidence_presentation(row: Mapping[str, Any]) -> dict[str, Any]:
    """Attach explicit display categories without creating a market score."""

    result = dict(row)
    key = str(result.get("key") or "")
    status = _status(result.get("status"))
    semantic_code = str(result.pop("_semantic_code", "") or "").upper()
    normalized_tone = str(result.get("tone") or "neutral").strip().lower()
    if status == "UNAVAILABLE":
        level = "limited"
    elif key == "economic_cycle":
        level = {
            "RECOVERY": "support",
            "EXPANSION": "support",
            "SLOWDOWN": "watch",
            "RECESSION": "watch",
        }.get(semantic_code, "neutral")
    elif key == "sp500":
        level = {
            "VERY_HIGH": "watch",
            "HIGH": "watch",
            "MID": "neutral",
            "NEUTRAL": "neutral",
            "LOW": "support",
            "VERY_LOW": "support",
        }.get(semantic_code, "limited")
    elif normalized_tone in {"positive", "support"}:
        level = "support"
    elif normalized_tone in {"warning", "negative", "danger", "burden"}:
        level = "watch"
    elif normalized_tone in {"neutral", "mixed"}:
        level = "neutral"
    else:
        level = "limited"
    signal_label, risk_label = _SIGNAL_LABELS[level]
    result.update(
        {
            "signal_level": level,
            "signal_label": signal_label,
            "risk_label": risk_label,
            "data_quality_label": (
                "자료 제한"
                if status != "READY" or bool(result.get("provisional"))
                else "자료 확인"
            ),
        }
    )
    return result


def _event_projection(model: Any) -> dict[str, Any] | None:
    source = _as_mapping(model)
    if not _available(source.get("status")):
        return None
    rows = _records(source.get("rows"))
    upcoming: list[tuple[int, str, dict[str, Any]]] = []
    for row in rows:
        raw_days = _safe_float(row.get("Days Until"))
        if raw_days is not None and raw_days < 0:
            continue
        day_rank = int(raw_days) if raw_days is not None else 99999
        event_date = _date_text(row.get("Date")) or "9999-12-31"
        upcoming.append((day_rank, event_date, row))
    if not upcoming:
        return None
    row = sorted(upcoming, key=lambda item: (item[0], item[1]))[0][2]
    return {
        "date": _date_text(row.get("Date")),
        "days_until": int(_safe_float(row.get("Days Until")) or 0),
        "type": _text(row.get("Type"), "EVENT"),
        "title": _text(row.get("Title") or row.get("Symbol"), "주요 일정"),
        "importance": _text(row.get("Importance"), "-"),
    }


def _project_market_evidence(
    economic_cycle: Any,
    sp500: Any,
    futures_macro: Any,
    sentiment: Any,
) -> list[dict[str, Any]]:
    """Project existing market sources without creating a new market score."""

    return [
        _evidence_presentation(row)
        for row in (
            _economic_cycle_evidence(economic_cycle),
            _sp500_evidence(sp500),
            _futures_evidence(futures_macro),
            _sentiment_evidence(sentiment),
        )
    ]


def _portfolio_curve_projection(curve: Any) -> dict[str, Any]:
    """Project at most 60 actual daily close observations with explicit units."""

    rows: list[dict[str, Any]] = []
    for row in _records(curve):
        on_date = _date_text(row.get("date"))
        unit_value = _safe_float(row.get("unit_value"))
        if on_date is None or unit_value is None:
            continue
        rows.append(
            {
                "date": on_date,
                "unit_value": unit_value,
                "total_value": _safe_float(row.get("total_value")),
                "cumulative_return": unit_value - 1.0,
            }
        )
    rows = sorted(rows, key=lambda item: str(item["date"]))[-60:]
    latest_return = None
    return_from_date = None
    return_to_date = None
    if len(rows) >= 2 and rows[-2]["unit_value"] != 0:
        latest_return = rows[-1]["unit_value"] / rows[-2]["unit_value"] - 1.0
        return_from_date = rows[-2]["date"]
        return_to_date = rows[-1]["date"]
    return {
        "rows": rows,
        "latest_observation_return": latest_return,
        "return_from_date": return_from_date,
        "return_to_date": return_to_date,
        "metadata": {
            "interval": "daily",
            "price_basis": "stored_close",
            "aggregation": "none",
            "intraday": False,
            "observation_count": len(rows),
            "start_date": rows[0]["date"] if rows else None,
            "end_date": rows[-1]["date"] if rows else None,
        },
    }


def _contributor_tone(value: float) -> str:
    """Classify contribution direction without treating zero as a loss."""

    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def _sort_contributors(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Order contributors by portfolio impact with deterministic ties."""

    return sorted(
        rows,
        key=lambda row: (
            -abs(float(row["contribution_value"])),
            str(row.get("symbol") or ""),
        ),
    )


def _project_portfolio(workspace: Any) -> dict[str, Any]:
    source = _as_mapping(workspace)
    boundaries = _as_mapping(source.get("boundaries"))
    groups = [_as_mapping(row) for row in source.get("groups") or []]
    group = next((row for row in groups if row.get("is_default")), None)
    group = group or next((row for row in groups if row.get("selected")), None)
    group = group or (groups[0] if groups else None)
    empty_curve = _portfolio_curve_projection([])
    empty_metrics = {
        "current_value": None,
        "latest_observation_return": None,
        "return_from_date": None,
        "return_to_date": None,
        "total_return": None,
    }
    source_status = _status(source.get("status"))
    storage_unavailable = (
        (bool(source_status) and source_status in _UNAVAILABLE_STATUSES)
        or boundaries.get("storage_ready") is False
        or any(_status(row.get("status")) == "STORAGE_UNAVAILABLE" for row in groups)
    )
    if storage_unavailable:
        return {
            "status": "UNAVAILABLE",
            "name": _text((group or {}).get("name"), "대표 포트폴리오"),
            "basis_date": None,
            "summary": "대표 포트폴리오의 저장 결과를 확인할 수 없습니다.",
            "metrics": empty_metrics,
            "curve": [],
            "curve_metadata": empty_curve["metadata"],
            "contributors": [],
            "review_items": [],
            "active_item_count": 0,
        }
    if group is None:
        return {
            "status": "EMPTY",
            "name": "대표 포트폴리오 없음",
            "basis_date": None,
            "summary": "Portfolio Monitoring에서 대표 포트폴리오를 설정해 주세요.",
            "metrics": empty_metrics,
            "curve": [],
            "curve_metadata": empty_curve["metadata"],
            "contributors": [],
            "review_items": [],
            "active_item_count": 0,
        }
    active = _as_mapping(source.get("active_group"))
    active_count = int(
        _safe_float(active.get("active_item_count"))
        or _safe_float(group.get("active_item_count"))
        or 0
    )
    if active_count <= 0:
        return {
            "status": "EMPTY",
            "name": _text(group.get("name"), "대표 포트폴리오"),
            "basis_date": _date_text(active.get("basis_date")),
            "summary": "추적 중인 종목이나 전략이 없습니다. Portfolio Monitoring에서 추가해 주세요.",
            "metrics": empty_metrics,
            "curve": [],
            "curve_metadata": empty_curve["metadata"],
            "contributors": [],
            "review_items": [],
            "active_item_count": 0,
        }
    if not active:
        return {
            "status": "UNAVAILABLE",
            "name": _text(group.get("name"), "대표 포트폴리오"),
            "basis_date": None,
            "summary": "대표 포트폴리오의 평가 결과를 확인할 수 없습니다.",
            "metrics": empty_metrics,
            "curve": [],
            "curve_metadata": empty_curve["metadata"],
            "contributors": [],
            "review_items": [],
            "active_item_count": active_count,
        }

    metrics = _as_mapping(active.get("metrics"))
    item_rows = [_as_mapping(row) for row in active.get("item_rows") or []]
    items_by_id = {
        str(row.get("monitoring_item_id") or ""): {
            "symbol": _text(row.get("source_ref")),
            "total_return": _safe_float(row.get("total_return")),
        }
        for row in item_rows
    }
    raw_contributions = _as_mapping(metrics.get("contribution_by_item"))
    contribution_rows = []
    for item_id, raw_value in raw_contributions.items():
        contribution_value = _safe_float(raw_value)
        if contribution_value is None:
            continue
        item = items_by_id.get(str(item_id), {})
        contribution_rows.append(
            {
                "symbol": _text(item.get("symbol"), str(item_id)),
                "contribution_value": contribution_value,
                "value": contribution_value,
                "total_return": _safe_float(item.get("total_return")),
                "tone": _contributor_tone(contribution_value),
            }
        )
    review_items = [
        {
            "severity": _text(row.get("severity"), "INFO"),
            "meaning": _text(row.get("meaning"), "확인할 항목이 있습니다."),
        }
        for row in (_as_mapping(item) for item in source.get("now_to_review") or [])
    ][:3]
    failures = _as_mapping(active.get("failures"))
    active_status = _status(active.get("status"))
    status = "PARTIAL" if failures or active_status == "PARTIAL" else "READY"
    curve_projection = _portfolio_curve_projection(active.get("curve"))
    return {
        "status": status,
        "name": _text(group.get("name"), "대표 포트폴리오"),
        "basis_date": _date_text(active.get("basis_date")),
        "summary": (
            "일부 종목의 평가가 제한되어 계산 가능한 범위만 표시합니다."
            if status == "PARTIAL"
            else "저장된 가격 기준 대표 포트폴리오의 현재 상태입니다."
        ),
        "metrics": {
            "current_value": _safe_float(metrics.get("current_value")),
            "latest_observation_return": curve_projection["latest_observation_return"],
            "return_from_date": curve_projection["return_from_date"],
            "return_to_date": curve_projection["return_to_date"],
            "total_return": _safe_float(metrics.get("total_return")),
        },
        "curve": curve_projection["rows"],
        "curve_metadata": curve_projection["metadata"],
        "contributors": _sort_contributors(contribution_rows),
        "review_items": review_items,
        "active_item_count": active_count,
    }


def _inactive_live_portfolio() -> dict[str, Any]:
    return {
        "status": "INACTIVE",
        "label": "확정 종가",
        "as_of_utc": None,
        "trade_date": None,
        "coverage": {"fresh": 0, "expected": 0, "fallback_symbols": []},
        "metrics": None,
        "contributors": [],
        "curve_point": None,
        "message": "저장된 확정 종가 기준입니다.",
    }


def _project_live_portfolio(model: Any) -> dict[str, Any]:
    source = _as_mapping(model)
    status = _status(source.get("status"))
    if status not in {"LIVE_READY", "LIVE_PARTIAL", "EOD_WAITING"}:
        return _inactive_live_portfolio()
    coverage = _as_mapping(source.get("coverage"))
    fallback_symbols = [
        str(symbol).strip().upper()
        for symbol in source.get("fallback_symbols")
        or coverage.get("fallback_symbols")
        or []
        if str(symbol).strip()
    ]
    raw_metrics = _as_mapping(source.get("metrics"))
    metrics = (
        {
            "current_value": _safe_float(raw_metrics.get("current_value")),
            "latest_observation_return": _safe_float(
                raw_metrics.get("latest_observation_return")
            ),
            "return_from_date": _date_text(raw_metrics.get("return_from_date")),
            "return_to_date": _date_text(raw_metrics.get("return_to_date")),
            "total_return": _safe_float(raw_metrics.get("total_return")),
        }
        if raw_metrics
        else None
    )
    raw_point = _as_mapping(source.get("curve_point"))
    curve_point = (
        {
            "date": _text(raw_point.get("date")),
            "timestamp_utc": _text(raw_point.get("timestamp_utc")),
            "kind": "intraday",
            "unit_value": _safe_float(raw_point.get("unit_value")),
            "total_value": _safe_float(raw_point.get("total_value")),
            "cumulative_return": _safe_float(raw_point.get("cumulative_return")),
        }
        if raw_point and raw_point.get("kind") == "intraday"
        else None
    )
    contributors = []
    for raw_row in source.get("contributors") or []:
        row = _as_mapping(raw_row)
        value = _safe_float(row.get("contribution_value"))
        if value is None:
            continue
        contributors.append(
            {
                "symbol": _text(row.get("symbol")),
                "contribution_value": value,
                "value": value,
                "total_return": _safe_float(row.get("total_return")),
                "tone": _contributor_tone(value),
            }
        )
    labels = {
        "LIVE_READY": "장중 임시",
        "LIVE_PARTIAL": "일부 장중 임시",
        "EOD_WAITING": "종가 반영 대기",
    }
    messages = {
        "LIVE_READY": "직접 종목의 최신 장중 가격을 반영했습니다.",
        "LIVE_PARTIAL": "일부 직접 종목은 마지막 확정 종가를 유지합니다.",
        "EOD_WAITING": "정규장 종료 후 당일 확정 종가 반영을 기다리고 있습니다.",
    }
    return {
        "status": status,
        "label": labels[status],
        "as_of_utc": _text(source.get("as_of_utc"), "") or None,
        "trade_date": _date_text(source.get("trade_date")),
        "coverage": {
            "fresh": int(coverage.get("fresh") or 0),
            "expected": int(coverage.get("expected") or 0),
            "fallback_symbols": fallback_symbols,
        },
        "metrics": metrics,
        "contributors": _sort_contributors(contributors),
        "curve_point": curve_point,
        "message": messages[status],
    }


def project_today_portfolio_live(model: Any) -> dict[str, Any]:
    """Expose the allowlisted live projection for DB-backed page refreshes."""

    return _project_live_portfolio(model)


def project_today_portfolio(
    workspace: Any,
    *,
    portfolio_live: Any | None = None,
) -> dict[str, Any]:
    """Project only the portfolio branch for lightweight Today refreshes."""

    portfolio = _project_portfolio(workspace)
    portfolio["live"] = _project_live_portfolio(portfolio_live)
    return portfolio


def _market_headline(evidence: list[dict[str, Any]], ready_count: int) -> str:
    if ready_count < 3:
        return "현재 자료로 종합 판단 보류"
    by_key = {row["key"]: row for row in evidence}
    cycle = _text(by_key.get("economic_cycle", {}).get("title"), "경기")
    valuation = _text(by_key.get("sp500", {}).get("title"), "가치평가 범위")
    sentiment = _text(by_key.get("sentiment", {}).get("title"), "심리 혼재")
    return f"{cycle} 국면 가능성, S&P 500 {valuation}·{sentiment} 심리를 함께 확인"


def build_today_read_model(
    *,
    economic_cycle: Any,
    sp500: Any,
    futures_macro: Any,
    sentiment: Any,
    events: Any,
    portfolio: Any,
    market_calendar: Any = None,
    portfolio_live: Mapping[str, Any] | None = None,
    generated_at: datetime | None = None,
) -> dict[str, object]:
    """Compose the read-only Today payload from existing persisted read models."""

    timestamp = generated_at or datetime.now(timezone.utc)
    evidence = _project_market_evidence(
        economic_cycle,
        sp500,
        futures_macro,
        sentiment,
    )
    next_event = _event_projection(events)
    event_status = _status(_as_mapping(events).get("status"))
    event_available = next_event is not None or _available(event_status)
    event_ready = event_status in {"OK", "READY"}
    available_market_count = sum(row["status"] != "UNAVAILABLE" for row in evidence)
    ready_market_count = sum(row["status"] == "READY" for row in evidence)
    ready_count = ready_market_count + int(event_ready)
    available_count = available_market_count + int(event_available)
    if available_market_count < 3:
        market_status = "UNAVAILABLE"
    elif ready_market_count == len(evidence) and event_ready:
        market_status = "READY"
    else:
        market_status = "PARTIAL"
    watch_items: list[str] = []
    for row in evidence:
        if row["status"] == "UNAVAILABLE":
            watch_items.append(f"{row['label']} 자료를 확인할 수 없습니다.")
        elif row.get("provisional"):
            watch_items.append("S&P 500 최신 후행 PER는 잠정 EPS 기준입니다.")
        elif row["status"] == "PARTIAL":
            watch_items.append(f"{row['label']} 근거에 제한이 있습니다.")
    if next_event and next_event.get("importance") == "High" and int(next_event.get("days_until") or 0) <= 7:
        watch_items.append(f"{next_event['date']} {next_event['title']} 일정을 확인합니다.")
    portfolio_model = project_today_portfolio(
        portfolio,
        portfolio_live=portfolio_live,
    )
    calendar = _as_mapping(market_calendar)
    market_session = build_us_market_session_model(
        generated_at=timestamp,
        holiday_rows=calendar.get("holiday_rows"),
        early_close_rows=calendar.get("early_close_rows"),
        calendar_statuses=calendar.get("statuses"),
    )
    date_candidates = [
        row.get("as_of_date")
        for row in evidence
        if row.get("as_of_date")
    ]
    if portfolio_model.get("basis_date"):
        date_candidates.append(portfolio_model["basis_date"])
    header_as_of = max(date_candidates) if date_candidates else timestamp.date().isoformat()
    return {
        "schema_version": TODAY_SCHEMA_VERSION,
        "generated_at": timestamp.isoformat(timespec="seconds"),
        "header": {
            "as_of_date": header_as_of,
            "source_count": len(evidence) + 1,
            "source_ready_count": ready_count,
            "source_available_count": available_count,
            "status": market_status,
            "status_label": {
                "READY": "주요 자료 확인",
                "PARTIAL": "일부 자료 제한",
                "UNAVAILABLE": "판단 자료 부족",
            }[market_status],
        },
        "market": {
            "status": market_status,
            "tone": "warning" if market_status != "READY" or watch_items else "neutral",
            "headline": _market_headline(evidence, available_market_count),
            "summary": (
                "기존 저장 근거를 함께 읽은 시장 context이며 공식 적정가·확정 예측·매매 신호가 아닙니다."
            ),
            "evidence": evidence,
            "next_event": next_event,
            "watch_items": watch_items[:3],
        },
        "market_session": market_session,
        "portfolio": portfolio_model,
        "actions": [
            {"key": "market_research", "label": "시장 근거 자세히 보기"},
            {"key": "stock_research", "label": "영향이 큰 종목 조사"},
            {"key": "portfolio_monitoring", "label": "포트폴리오 전체 점검"},
        ],
        "boundaries": {
            "db_only": True,
            "provider_fetch": False,
            "ingestion_job": False,
            "registry_write": False,
            "monitoring_log_write": False,
            "trading_signal": False,
            "live_orders": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "TODAY_SCHEMA_VERSION",
    "build_today_read_model",
    "project_today_portfolio",
    "project_today_portfolio_live",
]
