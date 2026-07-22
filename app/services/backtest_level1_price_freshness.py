from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import date, datetime
from typing import Any

from app.services.backtest_price_refresh import (
    price_refresh_result_requires_backtest_rerun,
)


def _normalize_symbols(values: Iterable[Any] | Any | None) -> list[str]:
    if values in (None, ""):
        return []
    source = values if isinstance(values, (list, tuple, set)) else [values]
    result: list[str] = []
    seen: set[str] = set()
    for raw in source:
        symbol = str(raw or "").strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        result.append(symbol)
    return result


def _extend_unique(target: list[str], values: Iterable[Any] | Any | None) -> None:
    seen = set(target)
    for symbol in _normalize_symbols(values):
        if symbol in seen:
            continue
        seen.add(symbol)
        target.append(symbol)


def _date_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def _earliest_date(values: Iterable[Any]) -> str | None:
    dates = [value for raw in values if (value := _date_text(raw))]
    return min(dates) if dates else None


def _bundle_meta(bundle: Mapping[str, Any]) -> dict[str, Any]:
    meta = dict(bundle.get("meta") or {})
    for key in (
        "tickers",
        "symbols",
        "cash_ticker",
        "benchmark_ticker",
        "guardrail_reference_ticker",
        "market_regime_benchmark",
        "defensive_tickers",
        "start",
        "end",
        "actual_result_end",
        "price_freshness",
    ):
        if key not in meta and key in bundle:
            meta[key] = bundle.get(key)
    return meta


def _configuration_value(
    configuration: Mapping[str, Any] | None,
    sources: Sequence[Mapping[str, Any]],
    key: str,
) -> Any:
    if configuration and configuration.get(key) not in (None, ""):
        return configuration.get(key)
    for source in sources:
        value = source.get(key)
        if value not in (None, ""):
            return value
    return None


def build_level1_price_refresh_meta(
    *,
    result_bundle: Mapping[str, Any],
    component_bundles: Sequence[Mapping[str, Any]] = (),
    configuration: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize the exact Level1 symbols and date evidence used by refresh planning."""

    source_bundles = [result_bundle, *component_bundles]
    sources = [_bundle_meta(bundle) for bundle in source_bundles]
    tickers: list[str] = []
    refresh_symbols: list[str] = []
    stale_symbols: list[str] = []
    missing_symbols: list[str] = []
    common_latest_values: list[Any] = []
    effective_end_values: list[Any] = []
    actual_end_values: list[Any] = []
    classification_rows: list[dict[str, Any]] = []
    classification_keys: set[tuple[str, str]] = set()
    freshness_statuses: list[str] = []

    for source in sources:
        for key in (
            "tickers",
            "symbols",
            "cash_ticker",
            "benchmark_ticker",
            "guardrail_reference_ticker",
            "market_regime_benchmark",
            "defensive_tickers",
        ):
            _extend_unique(tickers, source.get(key))

        freshness = dict(source.get("price_freshness") or {})
        freshness_statuses.append(str(freshness.get("status") or "").strip().lower())
        details = dict(freshness.get("details") or {})
        _extend_unique(
            refresh_symbols,
            details.get("refresh_symbols_all")
            or [
                *list(details.get("stale_symbols_all") or details.get("stale_symbols") or []),
                *list(details.get("missing_symbols_all") or details.get("missing_symbols") or []),
            ],
        )
        _extend_unique(
            stale_symbols,
            details.get("stale_symbols_all") or details.get("stale_symbols"),
        )
        _extend_unique(
            missing_symbols,
            details.get("missing_symbols_all") or details.get("missing_symbols"),
        )
        common_latest_values.append(details.get("common_latest_date"))
        effective_end_values.append(details.get("effective_end_date"))
        actual_end_values.append(source.get("actual_result_end"))
        for raw_row in details.get("classification_rows") or []:
            if not isinstance(raw_row, Mapping):
                continue
            row = dict(raw_row)
            symbols = _normalize_symbols(row.get("symbol"))
            if not symbols:
                continue
            row["symbol"] = symbols[0]
            reason = str(row.get("reason") or "").strip()
            key = (symbols[0], reason)
            if key in classification_keys:
                continue
            classification_keys.add(key)
            classification_rows.append(row)

    common_latest = _earliest_date(common_latest_values)
    effective_end = _earliest_date(effective_end_values)
    actual_result_end = common_latest or _earliest_date(actual_end_values)
    status = (
        "warning"
        if refresh_symbols or any(value in {"warning", "error"} for value in freshness_statuses)
        else "ok"
    )
    details = {
        "common_latest_date": common_latest,
        "effective_end_date": effective_end,
        "refresh_symbols_all": refresh_symbols,
        "stale_symbols_all": stale_symbols,
        "missing_symbols_all": missing_symbols,
        "classification_rows": classification_rows,
    }
    return {
        "tickers": tickers,
        "symbols": list(tickers),
        "start": _date_text(_configuration_value(configuration, sources, "start")),
        "end": _date_text(_configuration_value(configuration, sources, "end")),
        "actual_result_end": actual_result_end,
        "price_freshness": {
            "status": status,
            "details": details,
        },
    }


def _refresh_unresolved_symbols(
    refresh_result: Mapping[str, Any] | None,
) -> list[str]:
    details = dict((refresh_result or {}).get("details") or {})
    return _normalize_symbols(details.get("post_refresh_unresolved_symbols"))


def _action_base(plan: Mapping[str, Any] | None) -> dict[str, Any]:
    value = dict(plan or {})
    affected = _normalize_symbols(
        value.get("source_tickers")
        or value.get("tickers")
        or value.get("provider_gap_symbols")
    )
    return {
        "requested_end": _date_text(value.get("requested_end") or value.get("target_end")),
        "target_trading_end": _date_text(value.get("target_end")),
        "current_common_latest": _date_text(value.get("current_common_latest")),
        "affected_symbol_count": len(affected),
        "affected_symbol_sample": affected[:8],
        "feedback": None,
    }


def build_level1_price_freshness_action(
    *,
    plan: Mapping[str, Any] | None,
    refresh_result: Mapping[str, Any] | None = None,
    result_requires_rerun: bool = False,
) -> dict[str, Any]:
    """Project a refresh plan/result into one user action and a Level2 gate."""

    value = dict(plan or {})
    base = _action_base(value)
    unresolved = _refresh_unresolved_symbols(refresh_result)
    feedback = str((refresh_result or {}).get("message") or "").strip() or None

    if result_requires_rerun and price_refresh_result_requires_backtest_rerun(
        refresh_result
    ):
        return {
            **base,
            "state": "rerun_required",
            "summary": "가격 데이터 최신화를 반영하려면 백테스트를 다시 실행해야 합니다.",
            "guidance": "현재 결과는 가격 갱신 전 결과이므로 참고용으로만 확인하세요.",
            "handoff_blocked": True,
            "primary_action": {
                "id": "rerun_same_configuration",
                "label": "같은 설정으로 다시 백테스트",
                "enabled": True,
            },
            "feedback": feedback,
        }

    if refresh_result is not None and unresolved:
        return {
            **base,
            "state": "provider_gap",
            "affected_symbol_count": len(unresolved),
            "affected_symbol_sample": unresolved[:8],
            "summary": "자동 최신화 후에도 가격 데이터가 부족한 종목이 남았습니다.",
            "guidance": "동일 작업을 반복하기보다 종목의 provider/source 상태를 확인하거나 Universe를 조정하세요.",
            "handoff_blocked": True,
            "primary_action": None,
            "feedback": feedback,
        }

    status = str(value.get("status") or "").strip().lower()
    if status == "provider_gap_only" or (
        status == "unavailable" and value.get("provider_gap_symbols")
    ):
        provider_gaps = _normalize_symbols(value.get("provider_gap_symbols"))
        return {
            **base,
            "state": "provider_gap",
            "affected_symbol_count": len(provider_gaps),
            "affected_symbol_sample": provider_gaps[:8],
            "summary": "가격 업데이트로 해결하기 어려운 종목이 남았습니다.",
            "guidance": "provider/source 상태를 확인하거나 Universe를 조정한 뒤 다시 백테스트하세요.",
            "handoff_blocked": True,
            "primary_action": None,
            "feedback": feedback,
        }

    if bool(value.get("eligible")) and status == "refresh_available":
        return {
            **base,
            "state": "refresh_required",
            "summary": "요청 종료일 기준 데이터가 부족합니다.",
            "guidance": "포트폴리오 계산에 필요한 종목 가격을 최신화한 뒤 같은 설정으로 다시 백테스트하세요.",
            "handoff_blocked": True,
            "primary_action": {
                "id": "refresh_prices",
                "label": "종목 데이터 최신화",
                "enabled": True,
            },
            "feedback": feedback,
        }

    return {
        **base,
        "state": "current",
        "summary": "요청 종료일 기준 가격 데이터가 준비되어 있습니다.",
        "guidance": "현재 결과의 기존 Level2 인계 기준을 적용합니다.",
        "handoff_blocked": False,
        "primary_action": None,
        "feedback": feedback,
    }


__all__ = [
    "build_level1_price_freshness_action",
    "build_level1_price_refresh_meta",
]
