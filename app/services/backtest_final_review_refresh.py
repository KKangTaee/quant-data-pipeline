from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

import pandas as pd

from app.services.backtest_price_refresh import latest_completed_nyse_session
from app.services.backtest_practical_validation_replay import (
    build_replay_market_date_contract,
)


FRESHNESS_SCHEMA_VERSION = "final_review_observation_freshness_v1"
REFRESH_RESULT_SCHEMA_VERSION = "final_review_observation_refresh_result_v1"


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _selection_source(
    source: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    snapshot = dict(validation.get("selection_source_snapshot") or {})
    if snapshot:
        return snapshot
    row = dict(source.get("row") or {})
    nested = dict(row.get("selection_source_snapshot") or {})
    if nested:
        return nested
    return dict(source or {})


def _stored_curve_end(validation: Mapping[str, Any]) -> str | None:
    replay = dict(dict(validation.get("curve_evidence") or {}).get("replay_attempt") or {})
    points = [
        dict(row)
        for row in list(replay.get("portfolio_curve") or [])
        if isinstance(row, Mapping)
    ]
    dates = [_date_text(row.get("Date") or row.get("date")) for row in points]
    dates = [value for value in dates if value]
    if dates:
        return max(dates)
    period = dict(replay.get("actual_period") or {})
    coverage = dict(replay.get("period_coverage") or {})
    coverage_period = dict(coverage.get("actual_period") or {})
    source_period = dict(dict(validation.get("input_evidence") or {}).get("source_period") or {})
    return _date_text(
        period.get("end")
        or coverage_period.get("end")
        or source_period.get("actual_end")
    )


def _normalize_symbols(values: Any) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in list(values or []):
        symbol = str(value or "").strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        output.append(symbol)
    return output


def _status_payload(
    *,
    status: str,
    selection_source_id: str,
    validation_id: str,
    stored_curve_end: str | None,
    latest_completed_market_date: str,
    market_contract: Mapping[str, Any],
    provider_gap_symbols: list[str],
    refreshable_symbols: list[str],
    summary: str,
    detail: str,
) -> dict[str, Any]:
    presentation = {
        "up_to_date": ("positive", "최신"),
        "replay_available": ("warning", "재계산 가능"),
        "price_refresh_available": ("warning", "가격 최신화 필요"),
        "partial_refresh": ("neutral", "일부 최신화"),
        "blocked": ("danger", "갱신 불가"),
    }
    tone, label = presentation[status]
    can_refresh = status in {"replay_available", "price_refresh_available"}
    return {
        "schema_version": FRESHNESS_SCHEMA_VERSION,
        "status": status,
        "tone": tone,
        "label": label,
        "summary": summary,
        "detail": detail,
        "selection_source_id": selection_source_id,
        "validation_id": validation_id,
        "stored_curve_end": stored_curve_end,
        "latest_completed_market_date": latest_completed_market_date,
        "db_common_price_date": market_contract.get("latest_common_price_date"),
        "refresh_target_date": latest_completed_market_date,
        "limiting_symbols": _normalize_symbols(market_contract.get("limiting_symbols")),
        "stale_symbols": _normalize_symbols(market_contract.get("stale_symbols")),
        "missing_symbols": _normalize_symbols(market_contract.get("missing_symbols")),
        "provider_gap_symbols": provider_gap_symbols,
        "refreshable_symbols": refreshable_symbols,
        "can_refresh": can_refresh,
        "selection_blocked": status in {
            "replay_available",
            "price_refresh_available",
            "blocked",
        },
        "button_label": "최신 데이터로 다시 계산",
    }


def build_final_review_refresh_status(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    now: datetime | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """Build a read-only observation freshness model for one current validation."""

    source_row = _selection_source(source, validation)
    source_id = str(
        source_row.get("selection_source_id")
        or validation.get("selection_source_id")
        or ""
    ).strip()
    validation_id = str(validation.get("validation_id") or "").strip()
    curve_end = _stored_curve_end(validation)
    target = latest_completed_nyse_session(now).isoformat()
    empty_contract: dict[str, Any] = {
        "latest_common_price_date": None,
        "limiting_symbols": [],
        "stale_symbols": [],
        "missing_symbols": [],
    }
    if not source_id or not source_row or not curve_end:
        return _status_payload(
            status="blocked",
            selection_source_id=source_id,
            validation_id=validation_id,
            stored_curve_end=curve_end,
            latest_completed_market_date=target,
            market_contract=empty_contract,
            provider_gap_symbols=[],
            refreshable_symbols=[],
            summary="최신 관측을 계산할 source 계약이 없습니다.",
            detail="현재 후보의 저장 source와 replay curve를 확인한 뒤 다시 시도하세요.",
        )

    market_contract = build_replay_market_date_contract(
        source_row,
        requested_end=target,
        freshness_loader=freshness_loader,
    )
    symbols = _normalize_symbols(market_contract.get("symbols"))
    if not symbols:
        return _status_payload(
            status="blocked",
            selection_source_id=source_id,
            validation_id=validation_id,
            stored_curve_end=curve_end,
            latest_completed_market_date=target,
            market_contract=market_contract,
            provider_gap_symbols=[],
            refreshable_symbols=[],
            summary="최신 관측에 필요한 구성 종목을 확인할 수 없습니다.",
            detail="저장된 replay contract에 active ticker가 필요합니다.",
        )

    stale_symbols = _normalize_symbols(market_contract.get("stale_symbols"))
    snapshot = dict(validation.get("observation_refresh_snapshot") or {})
    provider_gap_symbols = []
    if _date_text(snapshot.get("target_market_date")) == target:
        known_gap_set = set(_normalize_symbols(snapshot.get("provider_gap_symbols")))
        provider_gap_symbols = [symbol for symbol in stale_symbols if symbol in known_gap_set]
    provider_gap_set = set(provider_gap_symbols)
    refreshable_symbols = [
        symbol for symbol in stale_symbols if symbol not in provider_gap_set
    ]
    common_date = _date_text(market_contract.get("latest_common_price_date"))

    if refreshable_symbols:
        status = "price_refresh_available"
        summary = f"{len(refreshable_symbols)}개 구성 종목의 가격을 최신화할 수 있습니다."
        detail = "가격 수집 후 같은 포트폴리오를 다시 계산해 새 검증 결과로 저장합니다."
    elif provider_gap_symbols:
        status = "partial_refresh"
        summary = "현재 provider에서 자동으로 더 최신화할 수 없는 종목이 남아 있습니다."
        detail = f"제한 종목: {', '.join(provider_gap_symbols)}"
    elif common_date and common_date > curve_end:
        status = "replay_available"
        summary = f"저장 가격은 {common_date}까지 있어 다시 계산할 수 있습니다."
        detail = "추가 수집 없이 같은 포트폴리오를 재현해 새 검증 결과로 저장합니다."
    elif common_date and common_date >= target and curve_end >= target:
        status = "up_to_date"
        summary = f"누적 성과와 낙폭이 최신 완료 거래일 {target}까지 반영됐습니다."
        detail = "추가 최신화가 필요하지 않습니다."
    elif common_date and curve_end >= common_date:
        status = "up_to_date"
        summary = f"현재 확보 가능한 공통 가격일 {common_date}까지 반영됐습니다."
        detail = "추가 자동 수집 대상은 없습니다."
    else:
        status = "blocked"
        summary = "현재 가격 범위로 새 관측을 계산할 수 없습니다."
        detail = "source별 공통 가격일과 replay curve를 확인하세요."

    return _status_payload(
        status=status,
        selection_source_id=source_id,
        validation_id=validation_id,
        stored_curve_end=curve_end,
        latest_completed_market_date=target,
        market_contract=market_contract,
        provider_gap_symbols=provider_gap_symbols,
        refreshable_symbols=refreshable_symbols,
        summary=summary,
        detail=detail,
    )
