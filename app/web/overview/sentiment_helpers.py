from __future__ import annotations

from datetime import date
from html import escape
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_market_sentiment,
)
from app.web.backtest_ui_components import render_status_card_grid
from app.web.overview.session_helpers import _snapshot_value
from app.web.overview_dashboard_helpers import load_overview_market_sentiment_snapshot
from app.web.overview.components.common import (
    OVERVIEW_COLOR_DANGER,
    OVERVIEW_COLOR_NEUTRAL,
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_PRIMARY,
    OVERVIEW_COLOR_WARNING,
    OVERVIEW_SERIES_COLORS,
)
from app.web.overview.sentiment_react_component import (
    render_sentiment_react_workbench,
    sentiment_react_component_available,
)


OVERVIEW_SENTIMENT_REACT_EVENT_KEY = "overview_sentiment_react_last_event"


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


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def _render_market_job_result(result_key: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    status = result.get("status")
    message = result.get("message") or ""
    if status == "success":
        st.success(message)
    elif status == "partial_success":
        st.warning(message)
    else:
        st.error(message)
    details = result.get("details") or {}
    if details:
        source = details.get("source") or "-"
        method = details.get("method") or details.get("method_requested") or "-"
        duration = result.get("duration_sec")
        st.caption(
            "Rows: "
            f"{result.get('rows_written') or 0}, "
            f"Events: {details.get('events_found') or '-'}, "
            f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
        )


def render_sentiment_header() -> None:
    st.markdown("### 시장 심리 컨텍스트")


def render_sentiment_controls() -> None:
    control_cols = st.columns([1.1, 1, 1], gap="small", vertical_alignment="bottom")
    if control_cols[0].button(
        "시장 심리 갱신",
        key="overview_market_sentiment_refresh",
        use_container_width=True,
        type="primary",
    ):
        _refresh_sentiment_for_ui()
        st.rerun()
    if control_cols[1].button(
        "화면 새로고침",
        key="overview_market_sentiment_reload",
        use_container_width=True,
    ):
        _reload_sentiment_snapshot_for_ui()
        st.rerun()
    control_cols[2].caption("CNN / AAII 저장 데이터 기준")


def render_sentiment_job_result() -> None:
    _render_market_job_result("overview_market_sentiment_result")


def load_sentiment_snapshot() -> dict[str, Any]:
    return load_overview_market_sentiment_snapshot()


def _refresh_sentiment_for_ui() -> None:
    with st.spinner("Refreshing CNN Fear & Greed / AAII sentiment..."):
        _store_overview_job_result(
            "overview_market_sentiment_result",
            run_overview_market_sentiment(),
        )
        load_overview_market_sentiment_snapshot.clear()


def _reload_sentiment_snapshot_for_ui() -> None:
    load_overview_market_sentiment_snapshot.clear()


def _sentiment_react_event_payload(event: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    nested = event.get("event")
    if isinstance(nested, dict):
        return dict(nested)
    return event


def _handle_sentiment_react_event(event: dict[str, Any] | None) -> None:
    payload = _sentiment_react_event_payload(event)
    action_id = str(payload.get("id") or payload.get("action_id") or "")
    if not action_id:
        return
    nonce = payload.get("nonce") or payload.get("token") or action_id
    event_key = f"{action_id}:{nonce}"
    if st.session_state.get(OVERVIEW_SENTIMENT_REACT_EVENT_KEY) == event_key:
        return
    st.session_state[OVERVIEW_SENTIMENT_REACT_EVENT_KEY] = event_key
    if action_id == "refresh":
        _refresh_sentiment_for_ui()
        st.rerun()
    if action_id == "reload":
        _reload_sentiment_snapshot_for_ui()
        st.rerun()


def _sentiment_status_tone(status: Any) -> str:
    normalized = str(status or "").upper()
    if normalized == "OK":
        return "positive"
    if normalized in {"REVIEW", "DUE"}:
        return "warning"
    if normalized in {"MISSING", "ERROR", "STALE"}:
        return "danger"
    return "neutral"


def _sentiment_tone(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"positive", "warning", "danger", "neutral"}:
        return normalized
    return _sentiment_status_tone(value)


def _display_text(value: Any, default: str = "-") -> str:
    text = str(value or "").strip()
    return text if text else default


def _json_safe_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return value


def _records_from_frame(frame: Any) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return []
    records: list[dict[str, Any]] = []
    for row in frame.to_dict("records"):
        records.append({str(key): _json_safe_value(value) for key, value in row.items()})
    return records


def _sentiment_metric(label: str, value: Any, *, detail: Any = "", tone: str = "neutral") -> dict[str, str]:
    return {
        "label": label,
        "value": _display_text(value),
        "detail": _display_text(detail, ""),
        "tone": _sentiment_tone(tone),
    }


def _format_sentiment_score(value: Any) -> str:
    numeric = _safe_float(value)
    return "-" if numeric is None else f"{numeric:.1f}"


def _format_sentiment_percent(value: Any) -> str:
    numeric = _safe_float(value)
    return "-" if numeric is None else f"{numeric:.1f}%"


def _format_sentiment_pp(value: Any) -> str:
    numeric = _safe_float(value)
    return "-" if numeric is None else f"{numeric:+.1f} pp"


def _latest_observation_date(rows: list[dict[str, Any]]) -> str:
    dates = [
        str(row.get("Observation Date") or "").strip()
        for row in rows
        if str(row.get("Observation Date") or "").strip() and str(row.get("Observation Date") or "").strip() != "-"
    ]
    return max(dates) if dates else "-"


def _sentiment_core_metrics(coverage: dict[str, Any], analysis: dict[str, Any]) -> list[dict[str, str]]:
    confidence = dict(analysis.get("data_confidence") or {})
    cnn_score = _safe_float(coverage.get("cnn_score"))
    aaii_bearish = _safe_float(coverage.get("aaii_bearish"))
    bull_bear_spread = _safe_float(coverage.get("aaii_bull_bear_spread"))
    return [
        _sentiment_metric(
            "CNN Fear & Greed",
            _format_sentiment_score(cnn_score),
            detail=coverage.get("cnn_rating") or "-",
            tone="positive" if cnn_score is not None and cnn_score >= 55 else "warning" if cnn_score is not None and cnn_score < 45 else "neutral",
        ),
        _sentiment_metric(
            "AAII Bearish",
            _format_sentiment_percent(aaii_bearish),
            detail="weekly bearish sentiment",
            tone="warning" if aaii_bearish is not None and aaii_bearish >= 35 else "neutral",
        ),
        _sentiment_metric(
            "Bull-Bear Spread",
            _format_sentiment_pp(bull_bear_spread),
            detail="AAII bullish minus bearish",
            tone="positive" if bull_bear_spread is not None and bull_bear_spread > 0 else "warning" if bull_bear_spread is not None else "neutral",
        ),
        _sentiment_metric(
            "Data Confidence",
            confidence.get("status") or "-",
            detail=confidence.get("detail") or "",
            tone=confidence.get("tone") or "neutral",
        ),
    ]


def _sentiment_driver_lanes(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    groups = dict(analysis.get("driver_groups") or {})
    labels = [
        ("greed", "탐욕 드라이버", "positive"),
        ("fear", "공포 드라이버", "warning"),
        ("neutral", "중립 드라이버", "neutral"),
    ]
    lanes: list[dict[str, Any]] = []
    for key, label, tone in labels:
        items = []
        for item in list(groups.get(key) or []):
            if not isinstance(item, dict):
                continue
            items.append(
                {
                    "series": _display_text(item.get("series")),
                    "label_ko": _display_text(item.get("label_ko") or item.get("series")),
                    "score": _format_sentiment_score(item.get("score")),
                    "rating": _display_text(item.get("rating_label_ko") or item.get("rating")),
                    "tone": _sentiment_tone(item.get("tone") or tone),
                    "direction": _display_text(item.get("direction"), key),
                    "current_reading": _display_text(item.get("current_reading"), ""),
                }
            )
        lanes.append({"key": key, "label": label, "tone": tone, "count": len(items), "items": items})
    return lanes


def _sentiment_history_chart_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    series = []
    for row in rows:
        series.append(
            {
                "date": _display_text(row.get("Date")),
                "series": _display_text(row.get("Series")),
                "value": _json_safe_value(row.get("Value")),
                "source": _display_text(row.get("Source"), ""),
            }
        )
    return {
        "title": "심리 흐름",
        "basis": "Stored CNN Fear & Greed / AAII bearish / bull-bear spread history",
        "series": series,
    }


def _sentiment_component_chart_payload(component_rows: list[dict[str, Any]], analysis: dict[str, Any]) -> dict[str, Any]:
    explanations = {
        str(item.get("series") or ""): dict(item)
        for item in list(analysis.get("component_explanations") or [])
        if isinstance(item, dict)
    }
    items = []
    for row in component_rows:
        series = _display_text(row.get("Series"))
        explanation = explanations.get(series, {})
        items.append(
            {
                "series": series,
                "score": _json_safe_value(row.get("Score")),
                "rating": _display_text(explanation.get("rating_label_ko") or row.get("Rating")),
                "tone": _sentiment_tone(explanation.get("tone") or row.get("Status")),
                "direction": _display_text(explanation.get("direction"), "neutral"),
                "observation_date": _display_text(row.get("Observation Date")),
                "current_reading": _display_text(explanation.get("current_reading"), ""),
            }
        )
    return {"title": "CNN 구성요소", "basis": "CNN Fear & Greed 7 component scores", "items": items}


def _sentiment_range_context_payload(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in list(analysis.get("range_context") or []):
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "series_id": _display_text(item.get("series_id"), ""),
                "series": _display_text(item.get("series")),
                "latest_value": _json_safe_value(item.get("latest_value")),
                "sample_count": int(item.get("sample_count") or 0),
                "min_value": _json_safe_value(item.get("min_value")),
                "max_value": _json_safe_value(item.get("max_value")),
                "median_value": _json_safe_value(item.get("median_value")),
                "percentile": _json_safe_value(item.get("percentile")),
                "position_label": _display_text(item.get("position_label"), ""),
                "tone": _sentiment_tone(item.get("tone") or "neutral"),
                "detail": _display_text(item.get("detail"), ""),
            }
        )
    return items


def _sentiment_divergence_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    divergence = analysis.get("divergence")
    if not isinstance(divergence, dict):
        divergence = {}
    items: list[dict[str, str]] = []
    for item in list(divergence.get("items") or []):
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "label": _display_text(item.get("label")),
                "direction": _display_text(item.get("direction"), ""),
                "direction_label": _display_text(item.get("direction_label") or item.get("status"), ""),
                "detail": _display_text(item.get("detail"), ""),
                "tone": _sentiment_tone(item.get("tone") or "neutral"),
            }
        )
    return {
        "status": _display_text(divergence.get("status"), ""),
        "tone": _sentiment_tone(divergence.get("tone") or "neutral"),
        "headline_direction": _display_text(divergence.get("headline_direction"), ""),
        "component_direction": _display_text(divergence.get("component_direction"), ""),
        "aaii_direction": _display_text(divergence.get("aaii_direction"), ""),
        "summary": _display_text(divergence.get("summary"), ""),
        "items": items,
    }


def _sentiment_component_history_payload(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in list(analysis.get("component_history") or []):
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "series_id": _display_text(item.get("series_id"), ""),
                "series": _display_text(item.get("series")),
                "label_ko": _display_text(item.get("label_ko") or item.get("series")),
                "latest": _json_safe_value(item.get("latest")),
                "latest_date": _display_text(item.get("latest_date"), ""),
                "previous": _json_safe_value(item.get("previous")),
                "previous_date": _display_text(item.get("previous_date"), ""),
                "change": _json_safe_value(item.get("change")),
                "change_direction": _display_text(item.get("change_direction"), "flat"),
                "tone": _sentiment_tone(item.get("tone") or "neutral"),
                "detail": _display_text(item.get("detail"), ""),
            }
        )
    return items


def _sentiment_axis_payload(axis: Any, *, fallback_label: str) -> dict[str, Any]:
    source = dict(axis) if isinstance(axis, dict) else {}
    return {
        **source,
        "label": _display_text(source.get("label"), fallback_label),
        "source": _display_text(source.get("source"), "-"),
        "available": bool(source.get("available")),
        "direction": _display_text(source.get("direction"), "unavailable"),
        "direction_label": _display_text(source.get("direction_label"), "판정 보류"),
        "tone": _sentiment_tone(source.get("tone") or "neutral"),
        "current": _json_safe_value(source.get("current")),
        "previous": _json_safe_value(source.get("previous")),
        "change": _json_safe_value(source.get("change")),
        "detail": _display_text(source.get("detail"), ""),
    }


def _sentiment_cnn_evidence_payload(
    component_rows: list[dict[str, Any]],
    analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    explanations = {
        str(item.get("series") or ""): dict(item)
        for item in list(analysis.get("component_explanations") or [])
        if isinstance(item, dict)
    }
    changes = {
        str(item.get("series") or ""): dict(item)
        for item in list(analysis.get("component_history") or [])
        if isinstance(item, dict)
    }
    items: list[dict[str, Any]] = []
    for row in component_rows:
        series = _display_text(row.get("Series"))
        explanation = explanations.get(series, {})
        change = changes.get(series, {})
        items.append(
            {
                "series": series,
                "label_ko": _display_text(explanation.get("label_ko") or series),
                "score": _json_safe_value(row.get("Score")),
                "rating": _display_text(explanation.get("rating_label_ko") or row.get("Rating")),
                "direction": _display_text(explanation.get("direction"), "neutral"),
                "tone": _sentiment_tone(explanation.get("tone") or row.get("Status")),
                "what_it_checks": _display_text(explanation.get("what_it_checks"), ""),
                "current_reading": _display_text(explanation.get("current_reading"), ""),
                "latest": _json_safe_value(change.get("latest", row.get("Score"))),
                "latest_date": _display_text(change.get("latest_date") or row.get("Observation Date"), ""),
                "previous": _json_safe_value(change.get("previous")),
                "previous_date": _display_text(change.get("previous_date"), ""),
                "change": _json_safe_value(change.get("change")),
                "change_direction": _display_text(change.get("change_direction"), "flat"),
            }
        )
    return items


def _sentiment_aaii_comparison_payload(axis: dict[str, Any]) -> list[dict[str, Any]]:
    comparisons = dict(axis.get("long_term_comparison") or {})
    labels = (("bullish", "Bullish"), ("neutral", "Neutral"), ("bearish", "Bearish"))
    items: list[dict[str, Any]] = []
    for key, label in labels:
        comparison = dict(comparisons.get(key) or {})
        difference = _json_safe_value(comparison.get("difference_pp"))
        numeric_difference = _safe_float(difference)
        tone = "positive" if key == "bullish" and numeric_difference is not None and numeric_difference > 0 else "warning" if key == "bearish" and numeric_difference is not None and numeric_difference > 0 else "neutral"
        items.append(
            {
                "key": key,
                "label": label,
                "current": _json_safe_value(comparison.get("current")),
                "historical_average": _json_safe_value(comparison.get("historical_average")),
                "difference_pp": difference,
                "tone": tone,
            }
        )
    return items


def _sentiment_chart_points(rows: list[dict[str, Any]], allowed_series: set[str]) -> list[dict[str, Any]]:
    return [
        {
            "date": _display_text(row.get("Date")),
            "series": _display_text(row.get("Series")),
            "value": _json_safe_value(row.get("Value")),
            "source": _display_text(row.get("Source"), ""),
            "status_label": _display_text(row.get("State"), ""),
        }
        for row in rows
        if _display_text(row.get("Series")) in allowed_series
    ]


def _sentiment_probability_rows(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in list(value or []):
        if not isinstance(item, dict):
            continue
        probability = _safe_float(item.get("value"))
        if probability is None or probability < 0 or probability > 1:
            continue
        rows.append(
            {
                "key": _display_text(item.get("key") or item.get("label")),
                "label": _display_text(item.get("label")),
                "value": probability,
                "baseline": _safe_float(item.get("baseline")),
                "difference_pp": _safe_float(item.get("difference_pp")),
            }
        )
    return rows


def _sentiment_outlook_payload(value: Any) -> dict[str, Any]:
    """Serialize forecast slots while suppressing distributions without validation evidence."""
    source = dict(value) if isinstance(value, dict) else {}
    source_by_key = {
        str(item.get("key") or ""): dict(item)
        for item in list(source.get("horizons") or [])
        if isinstance(item, dict)
    }
    horizons: list[dict[str, Any]] = []
    for key, label, period_label, trading_days in (
        ("1W", "1주", "다음 5거래일", 5),
        ("1M", "1개월", "다음 20거래일", 20),
    ):
        item = source_by_key.get(key, {})
        status = str(item.get("status") or "UNAVAILABLE").upper()
        if status not in {"VERIFIED", "PROVISIONAL", "UNAVAILABLE"}:
            status = "UNAVAILABLE"
        can_publish = status in {"VERIFIED", "PROVISIONAL"} and bool(item.get("validation_evidence"))
        horizons.append(
            {
                "key": key,
                "label": label,
                "period_label": period_label,
                "trading_days": trading_days,
                "status": status if can_publish else "UNAVAILABLE",
                "status_label": _display_text(
                    item.get("status_label") if can_publish else "통계적 판단 불가"
                ),
                "dominant_path": _display_text(item.get("dominant_path"), "") if can_publish else "",
                "probabilities": _sentiment_probability_rows(item.get("probabilities")) if can_publish else [],
                "baseline": _json_safe_value(item.get("baseline")) if can_publish else None,
                "episode_count": int(item.get("episode_count") or 0) if can_publish else 0,
                "validation_evidence": list(item.get("validation_evidence") or []) if can_publish else [],
                "status_reason": _display_text(
                    item.get("status_reason"),
                    "장기 이력과 point-in-time 검증이 부족해 확률을 공개하지 않습니다.",
                ),
            }
        )
    return {
        "status": "UNAVAILABLE" if all(row["status"] == "UNAVAILABLE" for row in horizons) else "AVAILABLE",
        "summary": _display_text(
            source.get("summary"),
            "현재는 확률 전망 대신 다음 CNN·AAII 관측 조건을 확인합니다.",
        ),
        "horizons": horizons,
    }


def build_sentiment_react_workbench_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Adapt the service-owned sentiment snapshot into a serializable React display payload."""
    coverage = dict(snapshot.get("coverage") or {})
    analysis = dict(snapshot.get("analysis") or {})
    rows = _records_from_frame(snapshot.get("rows"))
    component_rows = _records_from_frame(snapshot.get("component_rows"))
    history_rows = _records_from_frame(snapshot.get("history_rows"))
    coverage_source = dict(snapshot.get("history_coverage") or {})
    data_confidence = dict(analysis.get("data_confidence") or {})
    axes_source = dict(analysis.get("axes") or {})
    market_behavior = _sentiment_axis_payload(axes_source.get("market_behavior"), fallback_label="시장 행동")
    investor_survey = _sentiment_axis_payload(axes_source.get("investor_survey"), fallback_label="개인투자자 설문")
    cross_read_source = dict(analysis.get("cross_read") or {})
    cross_read = {
        "phase": _display_text(cross_read_source.get("phase") or analysis.get("phase"), "PARTIAL_DATA"),
        "phase_label": _display_text(cross_read_source.get("phase_label") or analysis.get("phase_label"), "데이터 확인"),
        "status": _display_text(cross_read_source.get("status"), "한 축만 확인 가능"),
        "tone": _sentiment_tone(cross_read_source.get("tone") or analysis.get("tone")),
        "headline": _display_text(cross_read_source.get("headline") or analysis.get("headline"), "시장 심리 해석을 확인할 수 없습니다."),
        "meaning": _display_text(cross_read_source.get("meaning") or analysis.get("summary"), ""),
        "confidence_note": _display_text(cross_read_source.get("confidence_note"), ""),
        "market_direction": _display_text(cross_read_source.get("market_direction"), market_behavior["direction"]),
        "survey_direction": _display_text(cross_read_source.get("survey_direction"), investor_survey["direction"]),
    }
    latest_date = _latest_observation_date(rows)
    stale_count = int(coverage.get("stale_count") or 0)
    missing_count = int(coverage.get("missing_count") or 0)
    freshness_tone = "positive" if stale_count == 0 and missing_count == 0 else "warning"

    def history_coverage_payload(key: str) -> dict[str, Any]:
        source = dict(coverage_source.get(key) or {})
        return {
            "canonical_start": _display_text(source.get("canonical_start"), ""),
            "canonical_end": _display_text(source.get("canonical_end"), ""),
            "observation_count": int(source.get("observation_count") or 0),
            "pit_start_at": _display_text(source.get("pit_start_at"), ""),
            "latest_capture_at": _display_text(source.get("latest_capture_at"), ""),
            "capture_count": int(source.get("capture_count") or 0),
        }

    aligned_source = dict(coverage_source.get("aligned") or {})
    aligned_history_coverage = {
        "canonical_start": _display_text(
            aligned_source.get("canonical_start"),
            "",
        ),
        "canonical_end": _display_text(
            aligned_source.get("canonical_end"),
            "",
        ),
        "available": bool(aligned_source.get("available")),
    }

    return {
        "schema_version": "sentiment_react_workbench_v2",
        "component": "SentimentWorkbench",
        "command": {
            "title": "시장 심리 컨텍스트",
            "detail": "CNN Fear & Greed / AAII 저장 데이터 기준",
            "actions": [
                {
                    "id": "refresh",
                    "label": "시장 심리 갱신",
                    "kind": "primary",
                    "detail": "CNN Fear & Greed와 AAII sentiment를 수집해 DB에 저장합니다.",
                },
                {
                    "id": "reload",
                    "label": "화면 다시 읽기",
                    "kind": "secondary",
                    "detail": "외부 수집 없이 현재 DB snapshot cache를 비우고 다시 읽습니다.",
                },
            ],
        },
        "summary": {
            "phase": cross_read["phase"],
            "phase_label": cross_read["phase_label"],
            "status": cross_read["status"],
            "tone": cross_read["tone"],
            "headline": cross_read["headline"],
            "summary": cross_read["meaning"],
            "latest_observation_date": latest_date,
            "data_confidence": {
                "status": _display_text(data_confidence.get("status"), snapshot.get("status") or "-"),
                "detail": _display_text(data_confidence.get("detail"), ""),
                "tone": _sentiment_tone(data_confidence.get("tone") or snapshot.get("status")),
            },
        },
        "axes": {
            "market_behavior": market_behavior,
            "investor_survey": investor_survey,
        },
        "cross_read": cross_read,
        "freshness": {
            "latest_observation_date": latest_date,
            "source_count": int(coverage.get("source_count") or 0),
            "stale_count": stale_count,
            "missing_count": missing_count,
            "tone": freshness_tone,
            "detail": f"latest {latest_date} · missing {missing_count} · stale {stale_count}",
        },
        "history_coverage": {
            "default_period": "6M",
            "periods": ["6M", "1Y", "ALL"],
            "aligned": aligned_history_coverage,
            "cnn": history_coverage_payload("cnn"),
            "aaii": history_coverage_payload("aaii"),
            "cnn_components_note": _display_text(
                coverage_source.get("cnn_components_note"),
                "수집 시작 이후 현재값을 축적 중",
            ),
        },
        "evidence": {
            "cnn_components": _sentiment_cnn_evidence_payload(component_rows, analysis),
            "aaii_comparison": _sentiment_aaii_comparison_payload(investor_survey),
        },
        "outlook": _sentiment_outlook_payload(analysis.get("outlook")),
        "watch_conditions": [
            {
                "key": _display_text(item.get("key"), "persist"),
                "label": _display_text(item.get("label")),
                "condition": _display_text(item.get("condition"), ""),
                "basis": _display_text(item.get("basis"), ""),
                "tone": _sentiment_tone(item.get("tone") or "neutral"),
            }
            for item in list(analysis.get("watch_conditions") or [])
            if isinstance(item, dict)
        ],
        "charts": {
            "cnn": {
                "title": "CNN 시장 행동",
                "basis": "CNN Fear & Greed 일간 관측 · 0~100",
                "unit": "score_0_100",
                "latest": {
                    "date": market_behavior.get("latest_date") or "-",
                    "value": market_behavior.get("current"),
                    "label": market_behavior.get("direction_label") or "판정 보류",
                },
                "series": _sentiment_chart_points(history_rows, {"CNN Fear & Greed"}),
            },
            "aaii_responses": {
                "title": "AAII 응답 구성",
                "basis": "AAII Bullish / Neutral / Bearish 주간 조사 · %",
                "unit": "percent",
                "latest": {
                    "date": investor_survey.get("latest_date") or "-",
                    "value": None,
                    "label": (
                        f"Bullish {_format_sentiment_percent(dict(investor_survey.get('responses') or {}).get('bullish'))} · "
                        f"Neutral {_format_sentiment_percent(dict(investor_survey.get('responses') or {}).get('neutral'))} · "
                        f"Bearish {_format_sentiment_percent(dict(investor_survey.get('responses') or {}).get('bearish'))}"
                    ),
                },
                "series": _sentiment_chart_points(history_rows, {"AAII Bullish", "AAII Neutral", "AAII Bearish"}),
            },
            "aaii_spread": {
                "title": "AAII Bull-Bear Spread",
                "basis": "AAII Bullish - Bearish 주간 조사 · pp",
                "unit": "percentage_point",
                "latest": {
                    "date": investor_survey.get("latest_date") or "-",
                    "value": investor_survey.get("spread"),
                    "label": investor_survey.get("direction_label") or "판정 보류",
                },
                "series": _sentiment_chart_points(history_rows, {"AAII Bull-Bear Spread"}),
            },
        },
        "raw_evidence": {
            "sentiment_rows": rows,
            "component_rows": component_rows,
            "history_rows": history_rows,
            "warnings": [str(warning) for warning in list(snapshot.get("warnings") or []) if str(warning).strip()],
        },
        "action_boundary": "python_dispatch_only",
        "boundary_note": "시장 배경 / 조사 단서입니다. 매수/매도 신호, validation gate, monitoring signal, 자동 action이 아닙니다.",
    }


def render_sentiment_react_workbench_section(snapshot: dict[str, Any]) -> bool:
    if not sentiment_react_component_available():
        return False
    react_event = render_sentiment_react_workbench(
        build_sentiment_react_workbench_payload(snapshot),
        key="overview_sentiment_workbench",
    )
    _handle_sentiment_react_event(react_event)
    return True


def _sentiment_trend_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        rows = pd.DataFrame([{"Date": date.today().isoformat(), "Series": "No Data", "Value": 0.0, "Source": "-"}])
    chart_rows = rows.copy()
    chart_rows["Date Parsed"] = pd.to_datetime(chart_rows.get("Date"), errors="coerce")
    chart_rows["Value"] = pd.to_numeric(chart_rows.get("Value"), errors="coerce")
    chart_rows = chart_rows.dropna(subset=["Date Parsed", "Value"])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Date Parsed": pd.Timestamp(date.today()), "Series": "No Data", "Value": 0.0, "Source": "-"}])
    return (
        alt.Chart(chart_rows)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("Date Parsed:T", title=None, axis=alt.Axis(format="%b %d", labelAngle=-35)),
            y=alt.Y("Value:Q", title=None),
            color=alt.Color(
                "Series:N",
                title=None,
                legend=alt.Legend(orient="bottom"),
                scale=alt.Scale(range=OVERVIEW_SERIES_COLORS),
            ),
            tooltip=["Date Parsed:T", "Series:N", "Value:Q", "Source:N"],
        )
        .properties(height=260)
    )


def _sentiment_component_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        rows = pd.DataFrame([{"Series": "No Data", "Score": 0.0, "Rating": "-", "Status": "-"}])
    chart_rows = rows.copy()
    chart_rows["Score"] = pd.to_numeric(chart_rows.get("Score"), errors="coerce").fillna(0.0)
    chart_rows["Bar Color"] = chart_rows["Score"].map(
        lambda value: OVERVIEW_COLOR_DANGER
        if value < 25
        else OVERVIEW_COLOR_WARNING
        if value < 45
        else OVERVIEW_COLOR_NEUTRAL
        if value < 55
        else OVERVIEW_COLOR_POSITIVE
        if value < 75
        else OVERVIEW_COLOR_PRIMARY
    )
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Score:Q", title=None, scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Series:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180)),
            color=alt.Color("Bar Color:N", scale=None, legend=None),
            tooltip=["Series:N", "Score:Q", "Rating:N", "Status:N"],
        )
        .properties(height=max(220, min(390, len(chart_rows) * 38)))
    )


def _render_sentiment_analysis_panel(analysis: dict[str, Any]) -> None:
    phase_label = escape(str(analysis.get("phase_label") or "-"))
    headline = escape(str(analysis.get("headline") or "-"))
    summary = escape(str(analysis.get("summary") or ""))
    tone = escape(_sentiment_tone(analysis.get("tone") or "neutral"))
    data_confidence = dict(analysis.get("data_confidence") or {})
    confidence_status = escape(str(data_confidence.get("status") or "-"))
    confidence_detail = escape(str(data_confidence.get("detail") or ""))

    st.markdown(
        """
        <style>
          .ov-sentiment-brief {
            margin: 0.45rem 0 0.8rem 0;
            padding: 0.92rem 1rem;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-left: 4px solid var(--ov-sentiment-tone, #64748b);
            border-radius: 8px;
            background: linear-gradient(135deg, color-mix(in srgb, var(--ov-sentiment-tone, #64748b) 8%, transparent), rgba(255,255,255,0.96));
          }
          .ov-sentiment-eyebrow {
            color: #475569;
            font-size: 0.75rem;
            font-weight: 760;
            letter-spacing: 0;
            text-transform: uppercase;
          }
          .ov-sentiment-headline {
            margin-top: 0.34rem;
            color: #111827;
            font-size: 1.08rem;
            line-height: 1.26;
            font-weight: 820;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-summary {
            margin-top: 0.35rem;
            max-width: 76rem;
            color: #334155;
            font-size: 0.88rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-meta {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.58rem;
          }
          .ov-sentiment-pill {
            display: inline-flex;
            align-items: center;
            min-height: 1.38rem;
            padding: 0.16rem 0.52rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--ov-sentiment-tone, #64748b) 13%, transparent);
            color: #111827;
            font-size: 0.76rem;
            font-weight: 760;
            line-height: 1.15;
          }
          .ov-sentiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
            gap: 0.58rem;
            margin: 0.35rem 0 0.85rem 0;
          }
          .ov-sentiment-step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
            gap: 0.72rem;
            margin: 0.4rem 0 0.95rem 0;
          }
          .ov-sentiment-step {
            min-height: 148px;
            padding: 0.86rem 0.92rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-left: 4px solid var(--ov-step-tone, #64748b);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.94);
          }
          .ov-sentiment-step-num {
            display: inline-flex;
            align-items: center;
            min-height: 1.32rem;
            padding: 0.12rem 0.42rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--ov-step-tone, #64748b) 11%, transparent);
            color: var(--ov-step-tone, #64748b);
            font-size: 0.72rem;
            font-weight: 820;
          }
          .ov-sentiment-step-title {
            margin-top: 0.42rem;
            color: #111827;
            font-size: 0.98rem;
            line-height: 1.25;
            font-weight: 800;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-step-status {
            margin-top: 0.34rem;
            color: #111827;
            font-size: 0.82rem;
            line-height: 1.2;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-step-detail {
            margin-top: 0.34rem;
            color: #334155;
            font-size: 0.8rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-driver {
            min-height: 92px;
            padding: 0.62rem 0.7rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-left: 3px solid var(--ov-driver-tone, #64748b);
            border-radius: 8px;
            background: rgba(255,255,255,0.92);
          }
          .ov-sentiment-driver-title {
            color: #111827;
            font-size: 0.82rem;
            line-height: 1.25;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-driver-detail {
            margin-top: 0.22rem;
            color: #334155;
            font-size: 0.75rem;
            line-height: 1.32;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning {
            min-height: 184px;
            padding: 0.78rem 0.82rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-top: 4px solid var(--ov-learning-tone, #64748b);
            border-radius: 8px;
            background: rgba(255,255,255,0.94);
          }
          .ov-sentiment-learning-title {
            color: #111827;
            font-size: 0.92rem;
            line-height: 1.25;
            font-weight: 820;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning-score {
            margin-top: 0.3rem;
            color: var(--ov-learning-tone, #64748b);
            font-size: 0.82rem;
            line-height: 1.24;
            font-weight: 800;
          }
          .ov-sentiment-learning-body {
            margin-top: 0.34rem;
            color: #334155;
            font-size: 0.76rem;
            line-height: 1.38;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning-body strong {
            color: #111827;
            font-weight: 780;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    tone_color = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
        "neutral": OVERVIEW_COLOR_NEUTRAL,
    }.get(tone, OVERVIEW_COLOR_NEUTRAL)
    st.markdown(
        f"""
        <section class="ov-sentiment-brief" style="--ov-sentiment-tone:{tone_color};">
          <div class="ov-sentiment-eyebrow">시장 심리 컨텍스트</div>
          <div class="ov-sentiment-headline">{headline}</div>
          <div class="ov-sentiment-summary">{summary}</div>
          <div class="ov-sentiment-meta">
            <span class="ov-sentiment-pill">{phase_label}</span>
            <span class="ov-sentiment-pill">데이터 신뢰도: {confidence_status}</span>
            <span class="ov-sentiment-pill">{confidence_detail}</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_sentiment_analysis_steps(analysis: dict[str, Any]) -> None:
    steps = list(analysis.get("analysis_steps") or [])
    if not steps:
        return
    html_steps: list[str] = []
    for index, step in enumerate(steps, start=1):
        tone = _sentiment_tone(step.get("tone") or "neutral")
        tone_color = {
            "positive": OVERVIEW_COLOR_POSITIVE,
            "warning": OVERVIEW_COLOR_WARNING,
            "danger": OVERVIEW_COLOR_DANGER,
            "neutral": OVERVIEW_COLOR_NEUTRAL,
        }.get(tone, OVERVIEW_COLOR_NEUTRAL)
        html_steps.append(
            f'<div class="ov-sentiment-step" style="--ov-step-tone:{tone_color};">'
            f'<div class="ov-sentiment-step-num">STEP {index}</div>'
            f'<div class="ov-sentiment-step-title">{escape(str(step.get("title") or "-"))}</div>'
            f'<div class="ov-sentiment-step-status">{escape(str(step.get("status") or "-"))}</div>'
            f'<div class="ov-sentiment-step-detail">{escape(str(step.get("detail") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### 시장 심리 읽기 - 6단계")
    st.markdown(f'<div class="ov-sentiment-step-grid">{"".join(html_steps)}</div>', unsafe_allow_html=True)


def _render_sentiment_driver_groups(analysis: dict[str, Any]) -> None:
    groups = dict(analysis.get("driver_groups") or {})
    labels = [
        ("greed", "탐욕 드라이버", OVERVIEW_COLOR_POSITIVE),
        ("fear", "공포 드라이버", OVERVIEW_COLOR_WARNING),
        ("neutral", "중립 드라이버", OVERVIEW_COLOR_NEUTRAL),
    ]
    html_cards: list[str] = []
    for key, title, color in labels:
        rows = list(groups.get(key) or [])
        if rows:
            detail = " / ".join(
                f"{row.get('label_ko') or row.get('series')}: {row.get('score')} ({row.get('rating_label_ko') or row.get('rating')})"
                for row in rows[:4]
            )
        else:
            detail = "이 구간의 활성 드라이버가 없습니다."
        html_cards.append(
            f'<div class="ov-sentiment-driver" style="--ov-driver-tone:{color};">'
            f'<div class="ov-sentiment-driver-title">{escape(title)} · {len(rows)}</div>'
            f'<div class="ov-sentiment-driver-detail">{escape(detail)}</div>'
            "</div>"
        )
    st.markdown("#### 드라이버 분해")
    st.markdown(f'<div class="ov-sentiment-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _render_sentiment_component_learning_cards(analysis: dict[str, Any]) -> None:
    explanations = list(analysis.get("component_explanations") or [])
    if not explanations:
        return
    tone_colors = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
        "neutral": OVERVIEW_COLOR_NEUTRAL,
    }
    html_cards: list[str] = []
    for item in explanations:
        tone_color = tone_colors.get(_sentiment_tone(item.get("tone") or "neutral"), OVERVIEW_COLOR_NEUTRAL)
        score = "-" if item.get("score") is None else f"{float(item.get('score')):.1f}"
        title = f"{item.get('label_ko') or '-'} · {item.get('series') or '-'}"
        html_cards.append(
            f'<div class="ov-sentiment-learning" style="--ov-learning-tone:{tone_color};">'
            f'<div class="ov-sentiment-learning-title">{escape(str(title))}</div>'
            f'<div class="ov-sentiment-learning-score">현재 {score} · {escape(str(item.get("rating_label_ko") or item.get("rating") or "-"))}</div>'
            f'<div class="ov-sentiment-learning-body"><strong>보는 것</strong><br>{escape(str(item.get("what_it_checks") or ""))}</div>'
            f'<div class="ov-sentiment-learning-body"><strong>현재 읽기</strong><br>{escape(str(item.get("current_reading") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### CNN 구성요소 학습 노트")
    st.markdown(f'<div class="ov-sentiment-step-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _render_sentiment_next_checks(analysis: dict[str, Any]) -> None:
    checks = list(analysis.get("next_checks") or [])
    if not checks:
        return
    html_cards: list[str] = []
    for check in checks:
        html_cards.append(
            f'<div class="ov-sentiment-driver" style="--ov-driver-tone:{OVERVIEW_COLOR_PRIMARY};">'
            f'<div class="ov-sentiment-driver-title">{escape(str(check.get("target") or "-"))}</div>'
            f'<div class="ov-sentiment-driver-detail"><strong>왜</strong> {escape(str(check.get("reason") or ""))}</div>'
            f'<div class="ov-sentiment-driver-detail"><strong>볼 것</strong> {escape(str(check.get("watch_for") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### 다음 확인")
    st.markdown(f'<div class="ov-sentiment-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _sentiment_status_cards(
    snapshot: dict[str, Any],
    coverage: dict[str, Any],
    analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "title": "데이터 신뢰도",
            "value": dict(analysis.get("data_confidence") or {}).get("status") or snapshot.get("status") or "-",
            "detail": f"{coverage.get('missing_count') or 0} missing · {coverage.get('stale_count') or 0} stale",
            "tone": _sentiment_tone(
                dict(analysis.get("data_confidence") or {}).get("tone") or snapshot.get("status")
            ),
        },
        {
            "title": "CNN Fear & Greed",
            "value": "-" if coverage.get("cnn_score") is None else f"{float(coverage['cnn_score']):.1f}",
            "detail": str(coverage.get("cnn_rating") or "-"),
            "tone": "positive"
            if _safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) >= 55
            else "warning"
            if _safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) < 45
            else "neutral",
        },
        {
            "title": "AAII Bearish",
            "value": "-" if coverage.get("aaii_bearish") is None else f"{float(coverage['aaii_bearish']):.1f}%",
            "detail": "weekly bearish sentiment",
            "tone": "warning"
            if _safe_float(coverage.get("aaii_bearish")) is not None
            and float(coverage["aaii_bearish"]) >= 40
            else "neutral",
        },
        {
            "title": "Bull-Bear Spread",
            "value": "-"
            if coverage.get("aaii_bull_bear_spread") is None
            else f"{float(coverage['aaii_bull_bear_spread']):+.1f} pp",
            "detail": "AAII bullish minus bearish",
            "tone": "positive"
            if _safe_float(coverage.get("aaii_bull_bear_spread")) is not None
            and float(coverage["aaii_bull_bear_spread"]) > 0
            else "warning"
            if _safe_float(coverage.get("aaii_bull_bear_spread")) is not None
            else "neutral",
        },
    ]


def render_sentiment_snapshot_overview(snapshot: dict[str, Any]) -> None:
    coverage = dict(snapshot.get("coverage") or {})
    analysis = dict(snapshot.get("analysis") or {})
    _render_sentiment_analysis_panel(analysis)
    _render_sentiment_analysis_steps(analysis)
    render_status_card_grid(_sentiment_status_cards(snapshot, coverage, analysis))
    for warning in snapshot.get("warnings") or []:
        st.warning(str(warning))


def has_sentiment_rows(snapshot: dict[str, Any]) -> bool:
    rows = snapshot.get("rows")
    return isinstance(rows, pd.DataFrame) and not rows.empty


def render_sentiment_empty_state() -> None:
    st.info("Stored sentiment rows are not available yet. Run Market Sentiment refresh first.")


def render_sentiment_detail_sections(snapshot: dict[str, Any]) -> None:
    analysis = dict(snapshot.get("analysis") or {})
    rows = snapshot.get("rows")
    component_rows = snapshot.get("component_rows")
    history_rows = snapshot.get("history_rows")

    _render_sentiment_driver_groups(analysis)
    _render_sentiment_component_learning_cards(analysis)
    _render_sentiment_next_checks(analysis)

    trend_tab, components_tab, table_tab = st.tabs(["추세 근거", "CNN 구성 상세", "원천 테이블"])
    with trend_tab:
        st.altair_chart(
            _sentiment_trend_chart(
                history_rows if isinstance(history_rows, pd.DataFrame) else pd.DataFrame()
            ),
            width="stretch",
        )
    with components_tab:
        st.altair_chart(
            _sentiment_component_chart(
                component_rows if isinstance(component_rows, pd.DataFrame) else pd.DataFrame()
            ),
            width="stretch",
        )
        if isinstance(component_rows, pd.DataFrame) and not component_rows.empty:
            st.dataframe(component_rows, width="stretch", hide_index=True)
    with table_tab:
        st.dataframe(rows, width="stretch", hide_index=True)
