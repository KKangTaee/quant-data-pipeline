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
from app.jobs.run_history import append_run_history, load_run_history
from app.services.backtest_practical_validation_diagnostics import (
    build_practical_validation_result as _build_practical_validation_result,
)
from app.services.backtest_practical_validation_source import (
    VALIDATION_PROFILE_OPTIONS,
    VALIDATION_PROFILE_QUESTIONS,
    build_validation_profile,
    source_components_dataframe,
)
from app.services.backtest_practical_validation_workspace import build_practical_validation_workspace
from app.services.backtest_practical_validation_decision_workspace import (
    build_practical_validation_decision_workspace,
)
from app.services.backtest_evidence_closure import build_evidence_closure_contract
from app.services.overview.sentiment import build_market_sentiment_snapshot
from app.runtime import append_portfolio_selection_source, append_practical_validation_result
from finance.data.etf_provider import (
    EXPOSURE_PROVIDER_SOURCES,
    HOLDINGS_PROVIDER_SOURCES,
    OFFICIAL_PROVIDER_SOURCES,
    load_etf_provider_source_map,
)


PROVIDER_GAP_STATE_PREFIX = "practical_validation_provider_gap_results"
SUPPORTED_HOLDINGS_COLLECTOR_PARSERS = frozenset(
    {
        "commodity_gold",
        "invesco_json",
        "ishares_csv",
        "ssga_xlsx",
    }
)


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

    result = _build_practical_validation_result(
        source,
        validation_profile=validation_profile,
        replay_result=replay_result,
    )
    provider_plan = build_provider_gap_collection_plan(result)
    result["provider_gap_collection_plan"] = provider_plan
    pre_final_gate = build_pre_final_enrichment_gate(result, provider_plan=provider_plan)
    _apply_pre_final_enrichment_gate(result, pre_final_gate)
    result["evidence_closure"] = build_evidence_closure_contract(result)
    result["practical_validation_workspace"] = build_practical_validation_workspace(result)
    return result


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
            f"Sentiment is context only on {surface_label}. Keep Final Review readiness preview and validation modules as the decision owner."
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


def _verified_source_map_priority(
    data_kind: str,
    row: dict[str, Any] | None,
) -> int:
    """Prefer verified contracts the current collector can actually execute."""

    if not row:
        return -1
    if data_kind != "holdings":
        return 1
    parser = str(row.get("parser") or "").strip().lower()
    return 2 if parser in SUPPORTED_HOLDINGS_COLLECTOR_PARSERS else 0


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
            current = maps[data_kind].get(symbol)
            if _verified_source_map_priority(
                data_kind,
                dict(row),
            ) > _verified_source_map_priority(data_kind, current):
                maps[data_kind][symbol] = dict(row)
    return maps


def _is_terminal_provider_source_map(row: dict[str, Any] | None) -> bool:
    """Distinguish completed/failed contracts from unverified discovery candidates."""

    if not row:
        return False
    source_status = str(row.get("source_status") or "").strip().lower()
    return source_status not in {
        "candidate",
        "draft",
        "pending",
        "discovered",
        "unverified",
    }


def _known_provider_source_maps(
    symbols: set[str],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Load attempted provider contracts, including failed or unsupported rows."""

    if not symbols:
        return {"operability": {}, "holdings": {}, "exposure": {}}
    try:
        rows = load_etf_provider_source_map(
            sorted(symbols),
            only_verified=False,
        )
    except Exception:
        return {"operability": {}, "holdings": {}, "exposure": {}}

    maps: dict[str, dict[str, dict[str, Any]]] = {
        "operability": {},
        "holdings": {},
        "exposure": {},
    }
    for row in rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        data_kind = str(row.get("data_kind") or "").strip().lower()
        if symbol and data_kind in maps:
            current = maps[data_kind].get(symbol)
            if (
                not current
                or (
                    _is_terminal_provider_source_map(dict(row))
                    and not _is_terminal_provider_source_map(current)
                )
            ):
                maps[data_kind][symbol] = dict(row)
    return maps


def _attempted_provider_source_map_symbols(source_id: str) -> set[str]:
    """Return symbols already included in this source's discovery action."""

    if not source_id:
        return set()
    try:
        rows = load_run_history(limit=500)
    except Exception:
        return set()
    symbols: set[str] = set()
    for row in rows:
        metadata = dict(dict(row or {}).get("run_metadata") or {})
        input_params = dict(metadata.get("input_params") or {})
        if (
            metadata.get("pipeline_type")
            != "practical_validation_provider_gap_collection"
            or input_params.get("provider_area")
            != "etf_provider_source_map"
            or str(input_params.get("selection_source_id") or "")
            != source_id
        ):
            continue
        details = dict(dict(row or {}).get("details") or {})
        symbols.update(_upper_symbol_set(input_params.get("requested_symbols")))
        symbols.update(_upper_symbol_set(details.get("symbols")))
        symbols.update(_upper_symbol_set(dict(row or {}).get("failed_symbols")))
    return symbols


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
        parser = str(mapped.get("parser") or "").strip().lower()
        if parser not in SUPPORTED_HOLDINGS_COLLECTOR_PARSERS:
            provider = str(mapped.get("provider") or "official").strip() or "official"
            parser_label = parser or "parser 미지정"
            return (
                f"{provider} / {parser_label}는 현재 자동 수집기 미지원",
                False,
            )
        return _source_map_status(mapped, fallback_label="official"), True
    source_info = HOLDINGS_PROVIDER_SOURCES.get(symbol)
    if not source_info:
        return "source map 미검증 / 자동 탐색 필요", False
    parser = str(source_info.get("parser") or "").strip().lower()
    if parser not in SUPPORTED_HOLDINGS_COLLECTOR_PARSERS:
        return "현재 자동 수집기가 지원하지 않는 holdings source", False
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
    operability_stale = _upper_symbol_set(dict(operability.get("provenance") or {}).get("stale_symbols"))
    holdings_missing = _upper_symbol_set(holdings.get("missing_symbols"))
    exposure_missing = _upper_symbol_set(exposure.get("missing_symbols"))
    source_maps = _verified_provider_source_maps(set(symbols))

    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        op_missing = symbol in operability_missing
        op_stale = symbol in operability_stale
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
        elif op_stale:
            actions.append("운용성 최신화")
        if holdings_is_missing or exposure_is_missing:
            if holdings_collectable or exposure_collectable:
                actions.append("holdings/exposure 수집")
            else:
                actions.append("source map 자동 탐색")
        rows.append(
            {
                "ETF": symbol,
                "Target Weight": round(weights.get(symbol, 0.0), 4),
                "Operability": "부족" if op_missing else "오래됨" if op_stale else "있음",
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
    operability = dict(coverage.get("operability") or {})
    operability_missing = _upper_symbol_set(operability.get("missing_symbols"))
    operability_stale = _upper_symbol_set(dict(operability.get("provenance") or {}).get("stale_symbols"))
    operability_targets = operability_missing | operability_stale
    holdings_missing = _upper_symbol_set(dict(coverage.get("holdings") or {}).get("missing_symbols"))
    exposure_missing = _upper_symbol_set(dict(coverage.get("exposure") or {}).get("missing_symbols"))
    holdings_targets = sorted(holdings_missing | exposure_missing)
    provider_symbols = sorted(
        _upper_symbol_set(provider_context.get("symbols"))
        | _upper_symbol_set(dict(provider_context.get("symbol_weights") or {}).keys())
        | operability_targets
        | holdings_missing
        | exposure_missing
    )
    source_maps = _verified_provider_source_maps(set(provider_symbols))
    known_source_maps = _known_provider_source_maps(set(provider_symbols))
    attempted_discovery = _attempted_provider_source_map_symbols(
        str(validation_result.get("selection_source_id") or "")
    )
    holdings_collectable: list[str] = []
    source_map_discovery: list[str] = []
    mapping_needed: list[str] = []
    for symbol in holdings_targets:
        if symbol in holdings_missing:
            collectable = _holdings_source_status(symbol, source_maps)[1]
            known_contract = _is_terminal_provider_source_map(
                dict(known_source_maps.get("holdings") or {}).get(symbol)
            ) or bool(
                HOLDINGS_PROVIDER_SOURCES.get(symbol)
            )
        else:
            collectable = _exposure_source_status(symbol, source_maps)[1]
            known_contract = any(
                _is_terminal_provider_source_map(row)
                for row in (
                    dict(known_source_maps.get("exposure") or {}).get(symbol),
                    dict(known_source_maps.get("holdings") or {}).get(symbol),
                )
            ) or bool(
                EXPOSURE_PROVIDER_SOURCES.get(symbol)
                or HOLDINGS_PROVIDER_SOURCES.get(symbol)
            )
        if collectable:
            holdings_collectable.append(symbol)
        elif known_contract or symbol in attempted_discovery:
            mapping_needed.append(symbol)
        else:
            source_map_discovery.append(symbol)
    macro = dict(coverage.get("macro") or {})
    macro_needs_collection = str(macro.get("diagnostic_status") or "").upper() in {"NOT_RUN", "REVIEW"} and (
        int(macro.get("series_count") or 0) < 3 or int(macro.get("stale_count") or 0) > 0
    )
    return {
        "source_map_discovery": sorted(source_map_discovery),
        "source_symbols": provider_symbols,
        "operability_stale": sorted(operability_stale),
        "operability_official": sorted(
            symbol
            for symbol in operability_targets
            if symbol in OFFICIAL_PROVIDER_SOURCES or symbol in dict(source_maps.get("operability") or {})
        ),
        "operability_bridge": sorted(operability_targets),
        "holdings_exposure": sorted(holdings_collectable),
        "mapping_needed": sorted(mapping_needed),
        "macro": macro_needs_collection,
    }


def build_pre_final_enrichment_gate(
    validation_result: dict[str, Any],
    *,
    provider_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Identify executable provider gaps that must be resolved before Final Review."""

    plan = dict(provider_plan or build_provider_gap_collection_plan(validation_result))
    items: list[dict[str, Any]] = []
    discovery_symbols = sorted(set(plan.get("source_map_discovery") or []))
    if discovery_symbols:
        items.append(
            {
                "category": "source_map_discovery",
                "label": "ETF 공식 source 계약 확인",
                "symbols": discovery_symbols,
                "detail": (
                    "현재 source 계약이 없는 ETF를 공식 provider 목록에서 한 번 확인합니다. "
                    "확인 후에도 계약이 없으면 개발 필요 항목으로 전환합니다."
                ),
            }
        )
    operability_symbols = sorted(
        set(plan.get("operability_official") or [])
        | set(plan.get("operability_bridge") or [])
    )
    if operability_symbols:
        items.append(
            {
                "category": "operability",
                "label": "ETF 거래 가능성 자료",
                "symbols": operability_symbols,
                "detail": "공식 source 또는 DB bridge에서 오래되거나 누락된 운용성 자료를 갱신합니다.",
            }
        )
    holdings_symbols = sorted(set(plan.get("holdings_exposure") or []))
    if holdings_symbols:
        items.append(
            {
                "category": "holdings_exposure",
                "label": "ETF 보유 종목·노출",
                "symbols": holdings_symbols,
                "detail": "검증된 공식 source에서 holdings와 exposure를 보강합니다.",
            }
        )
    if bool(plan.get("macro")):
        items.append(
            {
                "category": "macro",
                "label": "시장 환경 자료",
                "symbols": ["VIXCLS", "T10Y3M", "BAA10Y"],
                "detail": "현재 검증에 필요한 FRED 시장 환경 series를 갱신합니다.",
            }
        )
    engineering_symbols = sorted(set(plan.get("mapping_needed") or []))
    engineering_items = (
        [
            {
                "category": "holdings_contract",
                "label": "ETF 보유종목 수집기",
                "symbols": engineering_symbols,
                "detail": (
                    "검증 가능한 공식 source 계약이 없거나 현재 자동 수집기가 처리할 수 없어 "
                    "지원 parser 또는 evidence adapter 개발이 필요합니다."
                ),
            }
        ]
        if engineering_symbols
        else []
    )
    unique_symbols = {
        str(symbol)
        for item in items
        for symbol in list(item.get("symbols") or [])
        if str(symbol).strip()
    }
    required = bool(items)
    engineering_required = bool(engineering_items)
    return {
        "required": required,
        "blocking": required,
        "engineering_required": engineering_required,
        "engineering_blocking": engineering_required,
        "item_count": len(items),
        "symbol_count": len(unique_symbols),
        "items": items,
        "engineering_item_count": len(engineering_items),
        "engineering_symbol_count": len(engineering_symbols),
        "engineering_items": engineering_items,
        "reason": (
            "현재 수집 가능한 필수 외부 데이터가 남아 있습니다."
            if required
            else "현재 자동 수집기로 해결할 수 없는 필수 데이터 계약이 남아 있습니다."
            if engineering_required
            else "승격 전 필수 데이터 보강이 없습니다."
        ),
        "next_action": (
            "필수 데이터를 보강한 뒤 Flow 2 재검증을 실행합니다."
            if required
            else "지원 parser 또는 evidence adapter를 개발한 뒤 Flow 2 재검증을 실행합니다."
            if engineering_required
            else "Final Review 판단을 이어갑니다."
        ),
    }


def _apply_pre_final_enrichment_gate(
    validation_result: dict[str, Any],
    enrichment_gate: dict[str, Any],
) -> None:
    """Merge executable and engineering provider gaps into the Final Review Gate."""

    gate_contract = dict(enrichment_gate or {})
    validation_result["pre_final_enrichment_gate"] = gate_contract
    blockers: list[dict[str, Any]] = []
    if gate_contract.get("blocking"):
        blockers.append(
            {
                "module_id": "pre_final_data_enrichment",
                "label": "승격 전 필수 데이터 보강",
                "group": "Final Review Readiness Preview",
                "status": "NEEDS_INPUT",
                "requirement": "REQUIRED",
                "module_type": "Required",
                "stage_owner": "practical_validation",
                "applies": True,
                "reason": "현재 자동으로 보강할 수 있는 필수 외부 데이터가 남아 있습니다.",
                "next_action": "필수 데이터를 보강한 뒤 최신 데이터 기준 재검증을 실행합니다.",
                "resolution_surface": "3단계 · 지금 해야 할 일",
                "resolution_action": "필수 데이터 보강을 먼저 실행하고, 이어서 최신 데이터 기준 재검증을 실행합니다.",
                "gate_effect": "Blocks Final Review",
                "gate_reason": "Final Review 이동 전 실행 가능한 필수 외부 데이터 보강과 새 replay가 필요합니다.",
                "review_role": "final_readiness_blocker",
                "review_role_label": "저장 전 보강",
                "action_id": "run_practical_validation_provider_gap_collection",
                "actionable_now": True,
                "completion_criteria": (
                    "필수 데이터 보강 후 새 replay에서 실행 가능한 데이터 blocker가 "
                    "0건인지 확인합니다."
                ),
                "stage_decision_surface": "Practical Validation",
                "pv_visibility": "handoff_reference",
                "final_review_visibility": "selected_route_gate",
                "monitoring_visibility": "hidden",
                "item_count": int(gate_contract.get("item_count") or 0),
                "symbol_count": int(gate_contract.get("symbol_count") or 0),
                "items": list(gate_contract.get("items") or []),
                "evidence_state": "observed",
            }
        )
    if gate_contract.get("engineering_required"):
        engineering_symbols = sorted(
            {
                str(symbol)
                for item in list(gate_contract.get("engineering_items") or [])
                for symbol in list(dict(item or {}).get("symbols") or [])
                if str(symbol).strip()
            }
        )
        symbol_text = ", ".join(engineering_symbols[:8])
        if len(engineering_symbols) > 8:
            symbol_text += f" 외 {len(engineering_symbols) - 8}개"
        blockers.append(
            {
                "module_id": "pre_final_data_contract",
                "label": "필수 데이터 수집기 개발 필요",
                "group": "Final Review Readiness Preview",
                "status": "NOT_RUN",
                "requirement": "REQUIRED",
                "module_type": "Required",
                "stage_owner": "development",
                "applies": True,
                "reason": (
                    f"{symbol_text or '일부 ETF'}의 보유종목 근거는 검증 가능한 공식 source "
                    "계약이 없거나 현재 자동 수집기가 처리하지 못합니다."
                ),
                "next_action": "지원 parser 또는 evidence adapter를 개발한 뒤 새 replay로 검증합니다.",
                "resolution_surface": "개발 후 재검토",
                "resolution_action": "지원 parser 또는 evidence adapter를 구현하고 동일 후보를 다시 검증합니다.",
                "gate_effect": "Blocks Final Review",
                "gate_reason": "검증되지 않은 필수 데이터 계약은 Final Review로 넘기지 않습니다.",
                "review_role": "final_readiness_blocker",
                "review_role_label": "개발 필요",
                "action_id": None,
                "actionable_now": False,
                "completion_criteria": (
                    "지원 parser 또는 evidence adapter 구현 후 해당 ETF의 holdings/exposure "
                    "근거가 새 validation에 저장됩니다."
                ),
                "stage_decision_surface": "Development",
                "pv_visibility": "engineering_required",
                "final_review_visibility": "blocked",
                "monitoring_visibility": "hidden",
                "item_count": int(gate_contract.get("engineering_item_count") or 0),
                "symbol_count": int(gate_contract.get("engineering_symbol_count") or 0),
                "items": list(gate_contract.get("engineering_items") or []),
                "evidence_state": "missing",
            }
        )
    if not blockers:
        return

    blocker_ids = {str(blocker.get("module_id") or "") for blocker in blockers}
    modules = list(validation_result.get("validation_modules") or [])
    modules = [
        module
        for module in modules
        if str(dict(module or {}).get("module_id") or "") not in blocker_ids
    ]
    modules.extend(blockers)
    validation_result["validation_modules"] = modules

    final_gate = dict(validation_result.get("final_review_gate") or {})
    blocking_modules = [
        dict(module)
        for module in list(final_gate.get("blocking_modules") or [])
        if str(dict(module).get("module_id") or "") not in blocker_ids
    ]
    blocking_modules.extend(blockers)
    has_actionable = any(blocker.get("actionable_now") for blocker in blockers)
    has_engineering = any(
        blocker.get("module_id") == "pre_final_data_contract"
        for blocker in blockers
    )
    if has_actionable and has_engineering:
        verdict = "자동 보강 항목과 수집기 개발 항목이 남아 있어 Final Review 이동을 막습니다."
        next_action = "자동 보강을 실행하고, 미지원 데이터 수집기를 개발한 뒤 새 replay를 실행합니다."
    elif has_actionable:
        verdict = "수집 가능한 필수 외부 데이터가 남아 있어 Final Review 이동을 막습니다."
        next_action = blockers[0]["resolution_action"]
    else:
        verdict = "현재 자동 수집기가 지원하지 않는 필수 데이터 계약이 Final Review 이동을 막습니다."
        next_action = blockers[0]["resolution_action"]
    final_gate.update(
        {
            "route": "BLOCKED_FOR_FINAL_REVIEW",
            "can_save_and_move": False,
            "verdict": verdict,
            "next_action": next_action,
            "blocking_modules": blocking_modules,
            "pre_final_enrichment_gate": gate_contract,
        }
    )
    validation_result["final_review_gate"] = final_gate
    validation_result["validation_route"] = "BLOCKED_FOR_FINAL_REVIEW"

    handoff = dict(validation_result.get("final_review_handoff") or {})
    handoff.update(
        {
            "route": "BLOCKED_FOR_FINAL_REVIEW",
            "allowed": False,
            "module_gate": final_gate,
        }
    )
    validation_result["final_review_handoff"] = handoff


def _record_provider_gap_result(
    result: dict[str, Any],
    *,
    source_id: str,
    area: str,
    requested_symbols: list[str] | None = None,
) -> dict[str, Any]:
    record = dict(result)
    metadata = dict(record.get("run_metadata") or {})
    normalized_requested_symbols = sorted(
        _upper_symbol_set(requested_symbols)
    )
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
                "requested_symbols": normalized_requested_symbols,
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
        requested_symbols = (
            plan["source_symbols"]
            or plan["source_map_discovery"]
        )
        result = run_discover_etf_provider_source_map(
            requested_symbols,
            verify=True,
        )
        results.append(
            _record_provider_gap_result(
                result,
                source_id=source_id,
                area="etf_provider_source_map",
                requested_symbols=requested_symbols,
            )
        )
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
    "build_pre_final_enrichment_gate",
    "build_provider_gap_collection_plan",
    "build_provider_gap_rows",
    "build_practical_validation_result",
    "build_practical_validation_decision_workspace",
    "build_validation_profile",
    "prepare_final_review_handoff_from_validation",
    "prepare_practical_validation_source_handoff",
    "provider_gap_state_key",
    "run_provider_gap_collection",
    "save_practical_validation_result",
    "source_components_dataframe",
]
