from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from app.jobs.ingestion_jobs import (
    run_collect_etf_holdings_exposure,
    run_collect_etf_operability_provider,
    run_collect_macro_market_context,
    run_discover_etf_provider_source_map,
)
from app.jobs.run_history import append_run_history
from app.services.backtest_practical_validation_diagnostics import (
    build_practical_validation_result as _build_practical_validation_result,
)
from app.services.backtest_practical_validation_source import (
    VALIDATION_PROFILE_OPTIONS,
    VALIDATION_PROFILE_QUESTIONS,
    build_validation_profile,
    source_components_dataframe,
)
from app.services.overview.sentiment import build_market_sentiment_snapshot
from app.runtime import append_portfolio_selection_source, append_practical_validation_result
from finance.data.etf_provider import (
    EXPOSURE_PROVIDER_SOURCES,
    HOLDINGS_PROVIDER_SOURCES,
    OFFICIAL_PROVIDER_SOURCES,
    load_etf_provider_source_map,
)


PROVIDER_GAP_STATE_PREFIX = "practical_validation_provider_gap_results"


@dataclass(frozen=True)
class PracticalValidationSourceHandoff:
    """UI-neutral contract for moving a selection source into Practical Validation."""

    source_payload: dict[str, Any]
    notice: str
    mode: str = "Selected Source"
    requested_panel: str = "Practical Validation"
    persisted: bool = False


@dataclass(frozen=True)
class PracticalValidationFinalReviewHandoff:
    """UI-neutral contract for moving a validation result into Final Review."""

    session_payload: dict[str, Any]
    notice: str
    requested_panel: str = "Final Review"
    persisted: bool = False


def build_practical_validation_result(
    source: dict[str, Any],
    *,
    validation_profile: dict[str, Any] | None = None,
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the Practical Validation result without depending on Streamlit state."""

    return _build_practical_validation_result(
        source,
        validation_profile=validation_profile,
        replay_result=replay_result,
    )


def _sentiment_risk_context(analysis: dict[str, Any]) -> dict[str, str]:
    phase = str(analysis.get("phase") or "DATA_REVIEW").upper()
    if phase in {"GREED_LEANING", "EUPHORIA_RISK"}:
        state = "risk-on"
        state_label = "Risk-on"
        tone = "positive" if phase == "GREED_LEANING" else "warning"
    elif phase in {"FEAR_STRESS", "FEAR_LEANING"}:
        state = "risk-off"
        state_label = "Risk-off"
        tone = "danger" if phase == "FEAR_STRESS" else "warning"
    elif phase in {"MIXED_NEUTRAL", "STALE_REVIEW", "DATA_REVIEW"}:
        state = "neutral"
        state_label = "Neutral"
        tone = "neutral" if phase == "MIXED_NEUTRAL" else "warning"
    else:
        state = "neutral"
        state_label = "Neutral"
        tone = str(analysis.get("tone") or "neutral")
    return {
        "state": state,
        "state_label": state_label,
        "source_phase": phase,
        "source_phase_label": str(analysis.get("phase_label") or "-"),
        "tone": tone,
    }


def _sentiment_evidence_rows(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        return []
    evidence_rows: list[dict[str, Any]] = []
    for row in rows.to_dict("records"):
        metric = str(row.get("Series") or "-")
        evidence_rows.append(
            {
                "Metric": metric,
                "Value": row.get("Value") or "-",
                "Label": row.get("Label") or "-",
                "Observation Date": row.get("Observation Date") or "-",
                "Status": row.get("Status") or "-",
                "Source": row.get("Source") or "-",
            }
        )
    return evidence_rows


def build_market_sentiment_context_overlay(
    *,
    snapshot_rows: pd.DataFrame | None = None,
    history_rows: pd.DataFrame | None = None,
    today: date | None = None,
    surface: str = "Practical Validation",
) -> dict[str, Any]:
    """Build a read-only market sentiment overlay from stored CNN / AAII sentiment."""

    snapshot = build_market_sentiment_snapshot(
        snapshot_rows=snapshot_rows,
        history_rows=history_rows,
        today=today,
    )
    analysis = dict(snapshot.get("analysis") or {})
    coverage = dict(snapshot.get("coverage") or {})
    risk_context = _sentiment_risk_context(analysis)
    evidence_rows = _sentiment_evidence_rows(snapshot.get("rows"))
    surface_label = str(surface or "Practical Validation").strip() or "Practical Validation"
    return {
        "title": "Market Sentiment Context Overlay",
        "surface": surface_label,
        "status": str(snapshot.get("status") or "MISSING"),
        "risk_context": risk_context,
        "headline": str(analysis.get("headline") or "시장 심리 context를 확인할 수 없습니다."),
        "summary": str(analysis.get("summary") or ""),
        "data_confidence": dict(analysis.get("data_confidence") or {}),
        "metrics": {
            "cnn_fear_greed": coverage.get("cnn_score"),
            "cnn_rating": coverage.get("cnn_rating"),
            "aaii_bearish": coverage.get("aaii_bearish"),
            "aaii_bull_bear_spread": coverage.get("aaii_bull_bear_spread"),
            "source_count": coverage.get("source_count"),
            "missing_count": coverage.get("missing_count"),
            "stale_count": coverage.get("stale_count"),
        },
        "evidence_rows": evidence_rows,
        "warnings": list(snapshot.get("warnings") or []),
        "next_action": (
            f"Sentiment is context only on {surface_label}. Keep Final Review Gate, selected-route preflight, and validation modules as the decision owner."
            if str(snapshot.get("status") or "").upper() == "OK"
            else "Refresh Market Sentiment from Workspace > Overview > Sentiment or Workspace > Ingestion before relying on this context."
        ),
        "boundary": {
            "surface": surface_label,
            "context_only": True,
            "gate_effect": "none",
            "affects_pass_blocker": False,
            "trade_signal": False,
            "live_approval": False,
            "broker_order": False,
            "auto_rebalance": False,
            "registry_write": False,
            "saved_setup_write": False,
            "monitoring_signal": False,
            "message": (
                f"CNN Fear & Greed / AAII sentiment is displayed on {surface_label} as market context only. "
                "It does not pass, block, approve, order, or auto-rebalance any candidate."
            ),
        },
    }


def save_practical_validation_result(result: dict[str, Any]) -> None:
    append_practical_validation_result(dict(result or {}))


def prepare_practical_validation_source_handoff(
    source: dict[str, Any],
    *,
    persist: bool = True,
) -> PracticalValidationSourceHandoff:
    """Persist a selection source when requested and return the UI session contract."""

    source_row = dict(source or {})
    persisted = False
    if persist:
        append_portfolio_selection_source(source_row)
        persisted = True

    title = source_row.get("source_title") or source_row.get("selection_source_id")
    return PracticalValidationSourceHandoff(
        source_payload=source_row,
        notice=(
            f"`{title}`를 Practical Validation으로 보냈습니다. "
            "이 기록은 후보 검증 자료이며 live approval이나 주문 지시가 아닙니다."
        ),
        persisted=persisted,
    )


def prepare_final_review_handoff_from_validation(
    *,
    source: dict[str, Any],
    validation_result: dict[str, Any],
    persist_validation: bool = True,
) -> PracticalValidationFinalReviewHandoff:
    """Persist validation when requested and return the Final Review handoff payload."""

    persisted = False
    if persist_validation:
        save_practical_validation_result(validation_result)
        persisted = True

    title = validation_result.get("source_title") or validation_result.get("selection_source_id")
    return PracticalValidationFinalReviewHandoff(
        session_payload={
            "source": dict(source or {}),
            "validation_result": dict(validation_result or {}),
        },
        notice=f"`{title}`를 Final Review로 보냈습니다.",
        persisted=persisted,
    )


def _upper_symbol_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        raw_values = values.replace("\n", ",").split(",")
    else:
        raw_values = list(values or [])
    return {str(value or "").strip().upper() for value in raw_values if str(value or "").strip()}


def provider_gap_state_key(validation_result: dict[str, Any]) -> str:
    """Return the stable UI session key for the latest provider gap collection results."""

    source_id = str(validation_result.get("selection_source_id") or "source").strip() or "source"
    return f"{PROVIDER_GAP_STATE_PREFIX}_{source_id}"


def _verified_provider_source_maps(symbols: set[str]) -> dict[str, dict[str, dict[str, Any]]]:
    if not symbols:
        return {"operability": {}, "holdings": {}, "exposure": {}}
    try:
        rows = load_etf_provider_source_map(sorted(symbols), only_verified=True)
    except Exception:
        return {"operability": {}, "holdings": {}, "exposure": {}}

    maps: dict[str, dict[str, dict[str, Any]]] = {"operability": {}, "holdings": {}, "exposure": {}}
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        data_kind = str(row.get("data_kind") or "").strip().lower()
        if symbol and data_kind in maps:
            maps[data_kind][symbol] = dict(row)
    return maps


def _source_map_status(row: dict[str, Any], *, fallback_label: str) -> str:
    provider = str(row.get("provider") or fallback_label).strip() or fallback_label
    parser = str(row.get("parser") or "").strip()
    if parser == "commodity_gold":
        return "금/원자재 구성 rule 검증됨"
    parser_label = f" / {parser}" if parser else ""
    return f"{provider}{parser_label} source map 검증됨"


def _holdings_source_status(
    symbol: str,
    source_maps: dict[str, dict[str, dict[str, Any]]] | None = None,
) -> tuple[str, bool]:
    mapped = dict((source_maps or {}).get("holdings") or {}).get(symbol)
    if mapped:
        return _source_map_status(mapped, fallback_label="official"), True
    source_info = HOLDINGS_PROVIDER_SOURCES.get(symbol)
    if not source_info:
        return "source map 미검증 / 자동 탐색 필요", False
    parser = str(source_info.get("parser") or "").strip().lower()
    if parser == "pending":
        return "source 준비 중", False
    return f"{source_info.get('source') or 'official'} 수집 가능", True


def _exposure_source_status(
    symbol: str,
    source_maps: dict[str, dict[str, dict[str, Any]]] | None = None,
) -> tuple[str, bool]:
    mapped = dict((source_maps or {}).get("exposure") or {}).get(symbol)
    if mapped:
        return _source_map_status(mapped, fallback_label="official"), True
    source_info = EXPOSURE_PROVIDER_SOURCES.get(symbol)
    if source_info:
        return f"{source_info.get('source') or 'official'} aggregate 가능", True
    holdings_status, holdings_collectable = _holdings_source_status(symbol, source_maps)
    if holdings_collectable:
        return "holdings 기반 집계 가능", True
    return holdings_status, False


def build_provider_gap_rows(validation_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Build ETF-level provider coverage rows without depending on Streamlit."""

    provider_context = dict(validation_result.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    weights = {
        str(symbol or "").strip().upper(): float(weight or 0.0)
        for symbol, weight in dict(provider_context.get("symbol_weights") or {}).items()
        if str(symbol or "").strip()
    }
    symbols = list(provider_context.get("symbols") or sorted(weights))
    symbols = sorted(_upper_symbol_set(symbols) | set(weights))

    operability = dict(coverage.get("operability") or {})
    holdings = dict(coverage.get("holdings") or {})
    exposure = dict(coverage.get("exposure") or {})
    operability_missing = _upper_symbol_set(operability.get("missing_symbols"))
    holdings_missing = _upper_symbol_set(holdings.get("missing_symbols"))
    exposure_missing = _upper_symbol_set(exposure.get("missing_symbols"))
    source_maps = _verified_provider_source_maps(set(symbols))

    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        op_missing = symbol in operability_missing
        holdings_is_missing = symbol in holdings_missing
        exposure_is_missing = symbol in exposure_missing
        mapped_operability = dict(source_maps.get("operability") or {}).get(symbol)
        op_source_status = (
            _source_map_status(mapped_operability, fallback_label="official")
            if mapped_operability
            else "official 수집 가능"
            if symbol in OFFICIAL_PROVIDER_SOURCES
            else "official map 미검증 / DB bridge 가능"
        )
        holdings_source_status, holdings_collectable = _holdings_source_status(symbol, source_maps)
        exposure_source_status, exposure_collectable = _exposure_source_status(symbol, source_maps)
        actions: list[str] = []
        if op_missing:
            actions.append("운용성 보강")
        if holdings_is_missing or exposure_is_missing:
            if holdings_collectable or exposure_collectable:
                actions.append("holdings/exposure 수집")
            else:
                actions.append("source map 자동 탐색")
        rows.append(
            {
                "ETF": symbol,
                "Target Weight": round(weights.get(symbol, 0.0), 4),
                "Operability": "부족" if op_missing else "있음",
                "Operability Source": op_source_status,
                "Holdings": "부족" if holdings_is_missing else "있음",
                "Holdings Source": holdings_source_status,
                "Exposure": "부족" if exposure_is_missing else "있음",
                "Exposure Source": exposure_source_status,
                "Action": ", ".join(actions) if actions else "조치 없음",
            }
        )
    return rows


def build_provider_gap_collection_plan(validation_result: dict[str, Any]) -> dict[str, Any]:
    """Plan only the provider collectors that can improve the current validation source."""

    provider_context = dict(validation_result.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    operability_missing = _upper_symbol_set(dict(coverage.get("operability") or {}).get("missing_symbols"))
    holdings_missing = _upper_symbol_set(dict(coverage.get("holdings") or {}).get("missing_symbols"))
    exposure_missing = _upper_symbol_set(dict(coverage.get("exposure") or {}).get("missing_symbols"))
    holdings_targets = sorted(holdings_missing | exposure_missing)
    provider_symbols = sorted(
        _upper_symbol_set(provider_context.get("symbols"))
        | _upper_symbol_set(dict(provider_context.get("symbol_weights") or {}).keys())
        | operability_missing
        | holdings_missing
        | exposure_missing
    )
    source_maps = _verified_provider_source_maps(set(provider_symbols))
    holdings_collectable = [
        symbol
        for symbol in holdings_targets
        if _holdings_source_status(symbol, source_maps)[1] or _exposure_source_status(symbol, source_maps)[1]
    ]
    source_map_discovery = sorted(
        symbol
        for symbol in holdings_targets
        if symbol not in set(holdings_collectable)
    )
    macro = dict(coverage.get("macro") or {})
    macro_needs_collection = str(macro.get("diagnostic_status") or "").upper() in {"NOT_RUN", "REVIEW"} and (
        int(macro.get("series_count") or 0) < 3 or int(macro.get("stale_count") or 0) > 0
    )
    return {
        "source_map_discovery": source_map_discovery,
        "source_symbols": provider_symbols,
        "operability_official": sorted(
            symbol
            for symbol in operability_missing
            if symbol in OFFICIAL_PROVIDER_SOURCES or symbol in dict(source_maps.get("operability") or {})
        ),
        "operability_bridge": sorted(operability_missing),
        "holdings_exposure": holdings_collectable,
        "mapping_needed": [],
        "macro": macro_needs_collection,
    }


def _record_provider_gap_result(result: dict[str, Any], *, source_id: str, area: str) -> dict[str, Any]:
    record = dict(result)
    metadata = dict(record.get("run_metadata") or {})
    metadata.update(
        {
            "pipeline_type": "practical_validation_provider_gap_collection",
            "execution_mode": "interactive",
            "symbol_source": "Practical Validation Provider Data Gaps",
            "symbol_count": record.get("symbols_requested"),
            "execution_context": (
                "Practical Validation 화면에서 현재 source의 부족한 provider snapshot을 보강하기 위해 실행했습니다."
            ),
            "input_params": {
                "selection_source_id": source_id,
                "provider_area": area,
            },
        }
    )
    record["run_metadata"] = metadata
    append_run_history(record)
    return record


def run_provider_gap_collection(validation_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Run provider snapshot collectors for the current Practical Validation source."""

    source_id = str(validation_result.get("selection_source_id") or "-")
    plan = build_provider_gap_collection_plan(validation_result)
    results: list[dict[str, Any]] = []

    if plan["source_map_discovery"]:
        result = run_discover_etf_provider_source_map(
            plan["source_symbols"] or plan["source_map_discovery"],
            verify=True,
        )
        results.append(_record_provider_gap_result(result, source_id=source_id, area="etf_provider_source_map"))
        plan = build_provider_gap_collection_plan(validation_result)

    if plan["operability_official"]:
        result = run_collect_etf_operability_provider(
            plan["operability_official"],
            provider="official",
            as_of_date=None,
            lookback_days=60,
            timeframe="1d",
        )
        results.append(_record_provider_gap_result(result, source_id=source_id, area="etf_operability_official"))

    if plan["operability_bridge"]:
        result = run_collect_etf_operability_provider(
            plan["operability_bridge"],
            provider="db_bridge",
            as_of_date=None,
            lookback_days=60,
            timeframe="1d",
        )
        results.append(_record_provider_gap_result(result, source_id=source_id, area="etf_operability_db_bridge"))

    if plan["holdings_exposure"]:
        result = run_collect_etf_holdings_exposure(
            plan["holdings_exposure"],
            provider="official",
            as_of_date=None,
            include_provider_aggregates=True,
            refresh_mode="canonical_refresh",
        )
        results.append(_record_provider_gap_result(result, source_id=source_id, area="etf_holdings_exposure"))

    if plan["macro"]:
        result = run_collect_macro_market_context()
        results.append(_record_provider_gap_result(result, source_id=source_id, area="macro_context"))

    return results


__all__ = [
    "PracticalValidationFinalReviewHandoff",
    "PracticalValidationSourceHandoff",
    "PROVIDER_GAP_STATE_PREFIX",
    "VALIDATION_PROFILE_OPTIONS",
    "VALIDATION_PROFILE_QUESTIONS",
    "build_market_sentiment_context_overlay",
    "build_provider_gap_collection_plan",
    "build_provider_gap_rows",
    "build_practical_validation_result",
    "build_validation_profile",
    "prepare_final_review_handoff_from_validation",
    "prepare_practical_validation_source_handoff",
    "provider_gap_state_key",
    "run_provider_gap_collection",
    "save_practical_validation_result",
    "source_components_dataframe",
]
