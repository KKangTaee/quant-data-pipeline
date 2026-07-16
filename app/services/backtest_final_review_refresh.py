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


def _price_refresh_meta(
    *,
    selection_source: Mapping[str, Any],
    freshness: Mapping[str, Any],
) -> dict[str, Any]:
    period = dict(selection_source.get("period") or {})
    symbols = _normalize_symbols(freshness.get("stale_symbols"))
    refreshable = _normalize_symbols(freshness.get("refreshable_symbols"))
    missing = set(_normalize_symbols(freshness.get("missing_symbols")))
    return {
        "tickers": symbols,
        "symbols": symbols,
        "start": period.get("actual_start") or period.get("start"),
        "end": freshness.get("refresh_target_date"),
        "actual_result_end": freshness.get("stored_curve_end"),
        "price_freshness": {
            "status": "warning",
            "details": {
                "common_latest_date": freshness.get("db_common_price_date"),
                "effective_end_date": freshness.get("refresh_target_date"),
                "stale_symbols_all": refreshable,
                "missing_symbols_all": [
                    symbol for symbol in refreshable if symbol in missing
                ],
                "refresh_symbols_all": refreshable,
                "classification_rows": [],
            },
        },
    }


def _provider_gap_symbols(result: Mapping[str, Any]) -> list[str]:
    details = dict(result.get("details") or {})
    post = dict(details.get("post_refresh_price_freshness") or {})
    rows = list(dict(post.get("details") or {}).get("classification_rows") or [])
    markers = (
        "persistent_source_gap",
        "provider_source_gap",
        "provider_no_data",
        "likely_delisted",
        "symbol_changed",
        "asset_profile_error",
        "unavailable_from_provider",
    )
    return sorted(
        {
            str(row.get("symbol") or "").strip().upper()
            for row in rows
            if isinstance(row, Mapping)
            and any(marker in str(row.get("reason") or "").lower() for marker in markers)
            and str(row.get("symbol") or "").strip()
        }
    )


def _refresh_result(
    *,
    status: str,
    message: str,
    selection_source_id: str,
    previous_validation_id: str,
    previous_curve_end: str | None,
    refreshed_curve_end: str | None,
    freshness: Mapping[str, Any],
    provider_gap_symbols: list[str],
    price_refresh_executed: bool,
    price_rows_written: int,
    replay_executed: bool,
    validation_saved: bool,
    new_validation_id: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": REFRESH_RESULT_SCHEMA_VERSION,
        "status": status,
        "message": message,
        "selection_source_id": selection_source_id,
        "previous_validation_id": previous_validation_id,
        "new_validation_id": new_validation_id,
        "previous_curve_end": previous_curve_end,
        "refreshed_curve_end": refreshed_curve_end,
        "target_market_date": freshness.get("refresh_target_date"),
        "db_common_price_date": freshness.get("db_common_price_date"),
        "limiting_symbols": _normalize_symbols(freshness.get("limiting_symbols")),
        "provider_gap_symbols": provider_gap_symbols,
        "price_refresh_executed": price_refresh_executed,
        "price_rows_written": price_rows_written,
        "replay_executed": replay_executed,
        "validation_saved": validation_saved,
    }


def _replay_curve_end(replay: Mapping[str, Any]) -> str | None:
    points = [
        dict(row)
        for row in list(replay.get("portfolio_curve") or [])
        if isinstance(row, Mapping)
    ]
    dates = [_date_text(row.get("Date") or row.get("date")) for row in points]
    dates = [value for value in dates if value]
    if dates:
        return max(dates)
    actual_period = dict(replay.get("actual_period") or {})
    coverage_period = dict(dict(replay.get("period_coverage") or {}).get("actual_period") or {})
    return _date_text(actual_period.get("end") or coverage_period.get("end"))


def run_final_review_observation_refresh(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    now: datetime | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
    price_refresh_runner: Callable[..., Mapping[str, Any]] | None = None,
    replay_runner: Callable[..., dict[str, Any]] | None = None,
    validation_builder: Callable[..., dict[str, Any]] | None = None,
    validation_saver: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Refresh observations and append a new validation only after safe replay."""

    if price_refresh_runner is None:
        from app.services.backtest_price_refresh import run_backtest_price_refresh

        price_refresh_runner = run_backtest_price_refresh
    if replay_runner is None:
        from app.services.backtest_practical_validation_replay import (
            run_practical_validation_actual_replay,
        )

        replay_runner = run_practical_validation_actual_replay
    if validation_builder is None or validation_saver is None:
        from app.services.backtest_practical_validation import (
            build_practical_validation_result,
            save_practical_validation_result,
        )

        validation_builder = validation_builder or build_practical_validation_result
        validation_saver = validation_saver or save_practical_validation_result

    selection_source = _selection_source(source, validation)
    source_id = str(selection_source.get("selection_source_id") or "").strip()
    previous_validation_id = str(validation.get("validation_id") or "").strip()
    previous_curve_end = _stored_curve_end(validation)
    initial = build_final_review_refresh_status(
        source=source,
        validation=validation,
        now=now,
        freshness_loader=freshness_loader,
    )
    common_args = {
        "selection_source_id": source_id,
        "previous_validation_id": previous_validation_id,
        "previous_curve_end": previous_curve_end,
    }
    if initial.get("status") in {"up_to_date", "partial_refresh", "blocked"}:
        return _refresh_result(
            status=str(initial.get("status")),
            message=str(initial.get("summary") or ""),
            refreshed_curve_end=previous_curve_end,
            freshness=initial,
            provider_gap_symbols=_normalize_symbols(initial.get("provider_gap_symbols")),
            price_refresh_executed=False,
            price_rows_written=0,
            replay_executed=False,
            validation_saved=False,
            **common_args,
        )

    price_refresh_executed = False
    price_rows_written = 0
    provider_gap_symbols: list[str] = []
    current = initial
    try:
        if initial.get("status") == "price_refresh_available":
            price_refresh_executed = True
            price_result = dict(
                price_refresh_runner(
                    _price_refresh_meta(
                        selection_source=selection_source,
                        freshness=initial,
                    ),
                    now=now,
                )
            )
            price_rows_written = int(price_result.get("rows_written") or 0)
            provider_gap_symbols = _provider_gap_symbols(price_result)
            current = build_final_review_refresh_status(
                source=source,
                validation=validation,
                now=now,
                freshness_loader=freshness_loader,
            )
            current_common = _date_text(current.get("db_common_price_date"))
            if (
                not current_common
                or not previous_curve_end
                or current_common <= previous_curve_end
            ):
                return _refresh_result(
                    status="partial_refresh",
                    message="가격을 확인했지만 공통 관측 종료일은 늘어나지 않았습니다.",
                    refreshed_curve_end=previous_curve_end,
                    freshness=current,
                    provider_gap_symbols=provider_gap_symbols,
                    price_refresh_executed=True,
                    price_rows_written=price_rows_written,
                    replay_executed=False,
                    validation_saved=False,
                    **common_args,
                )

        replay = dict(
            replay_runner(
                selection_source,
                mode="extend_to_latest",
                end_override=current.get("refresh_target_date"),
            )
        )
        replay_status = str(replay.get("status") or "").upper()
        refreshed_curve_end = _replay_curve_end(replay)
        if (
            replay_status not in {"PASS", "REVIEW"}
            or not refreshed_curve_end
            or not previous_curve_end
            or refreshed_curve_end <= previous_curve_end
        ):
            return _refresh_result(
                status=(
                    "failed_after_price_refresh"
                    if price_refresh_executed and price_rows_written > 0
                    else "failed"
                ),
                message="최신 가격 이후 포트폴리오 재계산 결과를 만들지 못했습니다.",
                refreshed_curve_end=refreshed_curve_end,
                freshness=current,
                provider_gap_symbols=provider_gap_symbols,
                price_refresh_executed=price_refresh_executed,
                price_rows_written=price_rows_written,
                replay_executed=True,
                validation_saved=False,
                **common_args,
            )

        profile = dict(validation.get("validation_profile") or {})
        validation_profile = {
            "profile_id": profile.get("profile_id") or "balanced_core",
            "answers": dict(profile.get("answers") or {}),
        }
        new_validation = dict(
            validation_builder(
                selection_source,
                validation_profile=validation_profile,
                replay_result=replay,
            )
        )
        new_source_id = str(new_validation.get("selection_source_id") or "").strip()
        final_gate = dict(new_validation.get("final_review_gate") or {})
        if new_source_id != source_id or not bool(final_gate.get("can_save_and_move")):
            return _refresh_result(
                status="blocked",
                message="새 검증 결과가 Final Review 저장 조건을 충족하지 못했습니다.",
                refreshed_curve_end=refreshed_curve_end,
                freshness=current,
                provider_gap_symbols=provider_gap_symbols,
                price_refresh_executed=price_refresh_executed,
                price_rows_written=price_rows_written,
                replay_executed=True,
                validation_saved=False,
                **common_args,
            )

        new_validation["observation_refresh_snapshot"] = {
            "schema_version": "final_review_observation_refresh_snapshot_v1",
            "attempted_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "target_market_date": current.get("refresh_target_date"),
            "previous_curve_end": previous_curve_end,
            "refreshed_curve_end": refreshed_curve_end,
            "db_common_price_date": current.get("db_common_price_date"),
            "limiting_symbols": _normalize_symbols(current.get("limiting_symbols")),
            "provider_gap_symbols": provider_gap_symbols,
            "price_refresh_executed": price_refresh_executed,
            "price_rows_written": price_rows_written,
        }
        validation_saver(new_validation)
        target = _date_text(current.get("refresh_target_date"))
        result_status = (
            "refreshed"
            if target and refreshed_curve_end >= target
            else "partial_refresh"
        )
        return _refresh_result(
            status=result_status,
            message=(
                f"누적 성과와 낙폭을 {refreshed_curve_end}까지 다시 계산했습니다."
            ),
            new_validation_id=str(new_validation.get("validation_id") or "") or None,
            refreshed_curve_end=refreshed_curve_end,
            freshness=current,
            provider_gap_symbols=provider_gap_symbols,
            price_refresh_executed=price_refresh_executed,
            price_rows_written=price_rows_written,
            replay_executed=True,
            validation_saved=True,
            **common_args,
        )
    except Exception as exc:
        return _refresh_result(
            status=(
                "failed_after_price_refresh"
                if price_refresh_executed and price_rows_written > 0
                else "failed"
            ),
            message=f"최신 관측 갱신 중 오류가 발생했습니다: {exc}",
            refreshed_curve_end=previous_curve_end,
            freshness=current,
            provider_gap_symbols=provider_gap_symbols,
            price_refresh_executed=price_refresh_executed,
            price_rows_written=price_rows_written,
            replay_executed=False,
            validation_saved=False,
            **common_args,
        )
