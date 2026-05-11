from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.jobs.ingestion_jobs import (
    run_collect_etf_holdings_exposure,
    run_collect_etf_operability_provider,
    run_collect_macro_market_context,
    run_discover_etf_provider_source_map,
)
from app.jobs.run_history import append_run_history
from app.web.backtest_practical_validation_helpers import (
    VALIDATION_PROFILE_OPTIONS,
    VALIDATION_PROFILE_QUESTIONS,
    build_practical_validation_result,
    build_validation_profile,
    queue_final_review_source_from_validation,
    save_practical_validation_result,
    source_components_dataframe,
)
from app.web.backtest_practical_validation_replay import (
    RECHECK_MODE_EXTEND_TO_LATEST,
    RECHECK_MODE_LABELS,
    build_practical_validation_recheck_plan,
    run_practical_validation_actual_replay,
)
from app.web.backtest_ui_components import (
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.runtime import (
    PORTFOLIO_SELECTION_SOURCE_FILE,
    PRACTICAL_VALIDATION_RESULT_FILE,
    load_portfolio_selection_sources,
    load_practical_validation_results,
)
from finance.data.etf_provider import (
    EXPOSURE_PROVIDER_SOURCES,
    HOLDINGS_PROVIDER_SOURCES,
    OFFICIAL_PROVIDER_SOURCES,
    load_etf_provider_source_map,
)


PROVIDER_GAP_STATE_PREFIX = "practical_validation_provider_gap_results"


def _source_label(row: dict[str, Any]) -> str:
    return (
        f"{row.get('created_at') or '-'} | "
        f"{row.get('source_kind') or '-'} | "
        f"{row.get('source_title') or row.get('selection_source_id') or '-'}"
    )


def _render_source_summary(source: dict[str, Any]) -> None:
    summary = dict(source.get("summary") or {})
    period = dict(source.get("period") or {})
    construction = dict(source.get("construction") or {})
    render_badge_strip(
        [
            {"label": "Source", "value": source.get("source_kind") or "-", "tone": "neutral"},
            {"label": "Period", "value": f"{period.get('actual_start') or period.get('start') or '-'} -> {period.get('actual_end') or period.get('end') or '-'}", "tone": "neutral"},
            {"label": "CAGR", "value": summary.get("cagr") if summary.get("cagr") is not None else "-", "tone": "neutral"},
            {"label": "MDD", "value": summary.get("mdd") if summary.get("mdd") is not None else "-", "tone": "neutral"},
            {"label": "Weight Total", "value": f"{construction.get('target_weight_total', 0)}%", "tone": "neutral"},
        ]
    )
    component_df = source_components_dataframe(source)
    if component_df.empty:
        st.info("선택된 source에 component snapshot이 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)


def _render_validation_profile_form() -> dict[str, Any]:
    profile_options = list(VALIDATION_PROFILE_OPTIONS.keys())
    profile_id = st.selectbox(
        "검증 프로필",
        options=profile_options,
        format_func=lambda key: (
            f"{VALIDATION_PROFILE_OPTIONS[key]['label']} - "
            f"{VALIDATION_PROFILE_OPTIONS[key]['description']}"
        ),
        key="practical_validation_profile_id",
    )
    answers: dict[str, str] = {}
    question_items = list(VALIDATION_PROFILE_QUESTIONS.items())
    for start in range(0, len(question_items), 2):
        cols = st.columns(2, gap="small")
        for offset, col in enumerate(cols):
            if start + offset >= len(question_items):
                continue
            question_key, question = question_items[start + offset]
            options = list(dict(question.get("options") or {}).keys())
            labels = dict(question.get("options") or {})
            with col:
                answers[question_key] = st.selectbox(
                    str(question.get("label") or question_key),
                    options=options,
                    format_func=lambda option, labels=labels: labels.get(option, option),
                    index=options.index(question.get("default")) if question.get("default") in options else 0,
                    key=f"practical_validation_profile_answer_{question_key}",
                )
    profile = build_validation_profile(profile_id, answers)
    render_badge_strip(
        [
            {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
            {"label": "Rolling", "value": f"{dict(profile.get('thresholds') or {}).get('rolling_window_months')}M", "tone": "neutral"},
            {"label": "Cost", "value": f"{dict(profile.get('thresholds') or {}).get('one_way_cost_bps')} bps", "tone": "neutral"},
            {"label": "MDD Line", "value": dict(profile.get("thresholds") or {}).get("mdd_review_line"), "tone": "neutral"},
        ]
    )
    return {"profile_id": profile_id, "answers": answers}


def _replay_state_key(source: dict[str, Any], mode: str) -> str:
    return f"practical_validation_recheck_{source.get('selection_source_id') or 'source'}_{mode}"


def _render_actual_replay_panel(source: dict[str, Any]) -> dict[str, Any] | None:
    source_id = source.get("selection_source_id") or "source"
    mode = st.radio(
        "재검증 방식",
        options=list(RECHECK_MODE_LABELS.keys()),
        format_func=lambda value: RECHECK_MODE_LABELS.get(value, value),
        horizontal=True,
        key=f"practical_validation_recheck_mode_{source_id}",
    )
    recheck_plan = build_practical_validation_recheck_plan(source, mode=mode)
    replay_key = _replay_state_key(source, mode)
    replay_result = st.session_state.get(replay_key)
    render_badge_strip(
        [
            {"label": "Mode", "value": recheck_plan.get("mode_label") or "-", "tone": "neutral"},
            {"label": "Stored End", "value": dict(recheck_plan.get("stored_period") or {}).get("end") or "-", "tone": "neutral"},
            {"label": "Recheck End", "value": dict(recheck_plan.get("requested_period") or {}).get("end") or "-", "tone": "neutral"},
            {
                "label": "Extension",
                "value": f"{recheck_plan.get('extension_days', 0)} days",
                "tone": "neutral",
            },
        ]
    )
    if recheck_plan.get("latest_market_date_error"):
        st.warning(f"최신 DB 시장일 조회 실패: {recheck_plan.get('latest_market_date_error')}")
    elif mode == RECHECK_MODE_EXTEND_TO_LATEST:
        st.caption(
            f"DB 최신 시장일 `{recheck_plan.get('latest_market_date') or '-'}` 기준입니다. "
            f"{recheck_plan.get('status_reason') or ''}"
        )
    else:
        st.caption(str(recheck_plan.get("status_reason") or ""))
    st.caption(
        "이 버튼은 새 전략을 만들지 않고 기존 Backtest runtime으로 source를 재검증합니다. "
        "실패해도 저장 snapshot / DB price proxy 기반 진단은 계속 볼 수 있습니다."
    )
    if st.button("전략 재검증 실행", key=f"{replay_key}_run", width="stretch"):
        with st.spinner("기존 strategy runtime으로 Practical Validation source를 재검증 중입니다..."):
            replay_result = run_practical_validation_actual_replay(source, mode=mode)
        st.session_state[replay_key] = replay_result
        if replay_result.get("status") == "PASS":
            st.success("전략 재검증이 완료되었습니다.")
        elif replay_result.get("status") == "REVIEW":
            st.warning("전략 재검증은 완료되었지만 기간 coverage 또는 일부 component 확인이 필요합니다.")
        else:
            st.warning("전략 재검증이 일부 실패했습니다. 세부 결과를 확인하세요.")
    replay_result = st.session_state.get(replay_key)
    if isinstance(replay_result, dict) and replay_result:
        summary = dict(replay_result.get("summary") or {})
        period_coverage = dict(replay_result.get("period_coverage") or {})
        actual_period = dict(period_coverage.get("actual_period") or replay_result.get("actual_period") or {})
        render_badge_strip(
            [
                {
                    "label": "Recheck",
                    "value": replay_result.get("status") or "NOT_RUN",
                    "tone": _status_tone(replay_result.get("status")),
                },
                {"label": "Recheck ID", "value": replay_result.get("replay_id") or "-", "tone": "neutral"},
                {"label": "Elapsed", "value": f"{replay_result.get('elapsed_ms', 0)} ms", "tone": "neutral"},
                {"label": "CAGR", "value": summary.get("cagr") if summary else "-", "tone": "neutral"},
                {"label": "MDD", "value": summary.get("mdd") if summary else "-", "tone": "neutral"},
            ]
        )
        render_badge_strip(
            [
                {
                    "label": "Coverage",
                    "value": period_coverage.get("status") or "NOT_RUN",
                    "tone": _status_tone(period_coverage.get("status")),
                },
                {"label": "Actual End", "value": actual_period.get("end") or "-", "tone": "neutral"},
                {"label": "End Gap", "value": f"{period_coverage.get('end_gap_days', '-')} days", "tone": "neutral"},
                {"label": "Latest DB", "value": replay_result.get("latest_market_date") or "-", "tone": "neutral"},
            ]
        )
        if period_coverage.get("summary"):
            st.caption(str(period_coverage.get("summary")))
        component_rows = list(replay_result.get("component_results") or [])
        if component_rows:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Component": row.get("title"),
                            "Strategy": row.get("strategy_key"),
                            "Weight": row.get("target_weight"),
                            "Status": row.get("status"),
                            "Rows": row.get("result_rows"),
                            "Requested Start": row.get("requested_start"),
                            "Requested End": row.get("requested_end"),
                            "Start": row.get("actual_start"),
                            "End": row.get("actual_end"),
                            "Error": row.get("error"),
                        }
                        for row in component_rows
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        coverage_rows = list(period_coverage.get("component_rows") or [])
        if coverage_rows:
            st.dataframe(pd.DataFrame(coverage_rows), width="stretch", hide_index=True)
    return dict(replay_result) if isinstance(replay_result, dict) else None


def _status_tone(status: Any) -> str:
    status_text = str(status or "").upper()
    if status_text == "PASS":
        return "positive"
    if status_text == "BLOCKED":
        return "danger"
    if status_text == "REVIEW":
        return "warning"
    return "neutral"


def _upper_symbol_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        raw_values = values.replace("\n", ",").split(",")
    else:
        raw_values = list(values or [])
    return {str(value or "").strip().upper() for value in raw_values if str(value or "").strip()}


def _provider_gap_state_key(validation_result: dict[str, Any]) -> str:
    source_id = str(validation_result.get("selection_source_id") or "source").strip() or "source"
    return f"{PROVIDER_GAP_STATE_PREFIX}_{source_id}"


def _verified_provider_source_maps(symbols: set[str]) -> dict[str, dict[str, dict[str, Any]]]:
    """Read verified ETF source mappings so the UI can distinguish collectable gaps from unmapped gaps."""
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


def _provider_gap_rows(validation_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Build ETF-level provider coverage rows so operators can see exactly what is missing."""
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


def _provider_gap_collection_plan(validation_result: dict[str, Any]) -> dict[str, Any]:
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


def _run_provider_gap_collection(validation_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Run only the provider collectors that can improve the current validation source."""
    source_id = str(validation_result.get("selection_source_id") or "-")
    plan = _provider_gap_collection_plan(validation_result)
    results: list[dict[str, Any]] = []

    if plan["source_map_discovery"]:
        result = run_discover_etf_provider_source_map(
            plan["source_symbols"] or plan["source_map_discovery"],
            verify=True,
        )
        results.append(_record_provider_gap_result(result, source_id=source_id, area="etf_provider_source_map"))
        plan = _provider_gap_collection_plan(validation_result)

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


def _render_provider_gap_collection_results(results: list[dict[str, Any]]) -> None:
    if not results:
        return
    st.markdown("###### 최근 Provider 데이터 수집 결과")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Job": result.get("job_name"),
                    "Status": result.get("status"),
                    "Rows Written": result.get("rows_written"),
                    "Symbols": result.get("symbols_requested"),
                    "Failed": len(result.get("failed_symbols") or []),
                    "Message": result.get("message"),
                }
                for result in results
            ]
        ),
        width="stretch",
        hide_index=True,
    )


def _render_provider_gap_section(validation_result: dict[str, Any]) -> None:
    gap_rows = _provider_gap_rows(validation_result)
    if not gap_rows:
        return

    st.markdown("##### Provider Data Gaps")
    st.caption(
        "현재 source에 필요한 ETF별 provider 데이터가 어디까지 채워졌는지 보여줍니다. "
        "부족 데이터는 이 화면에서 바로 수집할 수 있고, source mapping이 없는 ETF는 connector 보강이 필요합니다."
    )
    st.dataframe(pd.DataFrame(gap_rows), width="stretch", hide_index=True)
    if not any(str(row.get("Action") or "") != "조치 없음" for row in gap_rows):
        st.success("현재 ETF provider gap은 없습니다.")
        return

    plan = _provider_gap_collection_plan(validation_result)
    if plan["operability_bridge"] or plan["operability_official"]:
        st.warning(
            "운용성 데이터 보강 필요: "
            + ", ".join(sorted(set(plan["operability_official"]) | set(plan["operability_bridge"])))
        )
    if plan["holdings_exposure"]:
        st.warning("Holdings / Exposure 수집 가능: " + ", ".join(plan["holdings_exposure"]))
    if plan["source_map_discovery"]:
        st.info(
            "Holdings / Exposure source map 자동 탐색 필요: "
            + ", ".join(plan["source_map_discovery"])
        )
    if plan["mapping_needed"]:
        st.info(
            "Holdings / Exposure connector mapping 필요: "
            + ", ".join(plan["mapping_needed"])
        )
    action_rows = [
        {
            "Area": "ETF Provider Source Map",
            "Symbols": ", ".join(plan["source_map_discovery"]) or "-",
            "Meaning": "`nyse_etf`와 asset profile을 기준으로 운용사 공식 URL / parser mapping을 찾아 `finance_meta.etf_provider_source_map`에 저장합니다.",
        },
        {
            "Area": "ETF Operability official",
            "Symbols": ", ".join(plan["operability_official"]) or "-",
            "Meaning": "공식 운용사 page에서 비용 / 상품 metadata를 수집합니다.",
        },
        {
            "Area": "ETF Operability DB bridge",
            "Symbols": ", ".join(plan["operability_bridge"]) or "-",
            "Meaning": "공식 source map이 없거나 부족한 ETF를 DB price / asset profile 기반으로 보강합니다.",
        },
        {
            "Area": "ETF Holdings / Exposure",
            "Symbols": ", ".join(plan["holdings_exposure"]) or "-",
            "Meaning": "공식 holdings를 수집하고 자산군 / 섹터 exposure를 재집계합니다.",
        },
        {
            "Area": "Connector mapping needed",
            "Symbols": ", ".join(plan["mapping_needed"]) or "-",
            "Meaning": "자동 탐색 후에도 검증된 issuer URL / parser mapping이 없으면 수동 connector 보강이 필요합니다.",
        },
    ]
    if plan["macro"]:
        action_rows.append(
            {
                "Area": "Macro Context",
                "Symbols": "VIXCLS, T10Y3M, BAA10Y",
                "Meaning": "FRED market context series를 다시 수집합니다.",
            }
        )
    st.dataframe(pd.DataFrame(action_rows), width="stretch", hide_index=True)

    result_key = _provider_gap_state_key(validation_result)
    latest_results = st.session_state.get(result_key)
    if isinstance(latest_results, list):
        _render_provider_gap_collection_results(latest_results)

    has_collectable = any(
        [
            plan["operability_official"],
            plan["operability_bridge"],
            plan["holdings_exposure"],
            plan["source_map_discovery"],
            plan["macro"],
        ]
    )
    if not has_collectable:
        st.info("현재 버튼으로 수집 가능한 provider gap은 없습니다. 남은 부족 ETF는 connector source mapping 추가가 필요합니다.")
        return

    if st.button("부족한 Provider 데이터 일괄 수집 / 보강", key=f"{result_key}_run", width="stretch"):
        with st.spinner("현재 source에 필요한 provider snapshot을 수집 / 보강 중입니다..."):
            results = _run_provider_gap_collection(validation_result)
        st.session_state[result_key] = results
        st.rerun()


def _render_validation_result(validation_result: dict[str, Any]) -> None:
    profile = dict(validation_result.get("validation_profile") or {})
    status_counts = dict(dict(validation_result.get("diagnostic_summary") or {}).get("status_counts") or {})
    render_readiness_route_panel(
        route_label=str(validation_result.get("validation_route") or "-"),
        score=float(validation_result.get("validation_score") or 0.0),
        blockers_count=len(validation_result.get("hard_blockers") or []),
        verdict=str(validation_result.get("verdict") or "-"),
        next_action=str(validation_result.get("next_action") or "-"),
        route_title="Practical Validation",
        score_title="Validation Score",
    )
    render_badge_strip(
        [
            {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
            {"label": "PASS", "value": status_counts.get("PASS", 0), "tone": "positive"},
            {"label": "REVIEW", "value": status_counts.get("REVIEW", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": status_counts.get("BLOCKED", 0), "tone": "danger"},
            {"label": "NOT_RUN", "value": status_counts.get("NOT_RUN", 0), "tone": "neutral"},
        ]
    )
    st.markdown("##### Input Evidence")
    st.dataframe(pd.DataFrame(validation_result.get("checks") or []), width="stretch", hide_index=True)
    st.markdown("##### Practical Diagnostics")
    diagnostic_rows = list(validation_result.get("diagnostic_display_rows") or [])
    if diagnostic_rows:
        st.dataframe(pd.DataFrame(diagnostic_rows), width="stretch", hide_index=True)
    else:
        st.info("표시할 diagnostic row가 없습니다.")

    provider_rows = list(validation_result.get("provider_coverage_display_rows") or [])
    if provider_rows:
        st.markdown("##### Provider Coverage")
        st.caption(
            "Ingestion에서 저장한 ETF provider / FRED snapshot이 Practical Diagnostics에 어떻게 연결됐는지 보여줍니다."
        )
        st.dataframe(pd.DataFrame(provider_rows), width="stretch", hide_index=True)
        _render_provider_gap_section(validation_result)

    mismatch_warnings = list(validation_result.get("intent_mismatch_warnings") or [])
    if mismatch_warnings:
        st.warning("사용자 프로필과 후보 특성이 충돌할 수 있습니다.")
        for warning in mismatch_warnings:
            st.caption(f"- {warning}")
    if validation_result.get("hard_blockers"):
        for blocker in list(validation_result.get("hard_blockers") or []):
            st.error(str(blocker))
    if validation_result.get("review_gaps"):
        for gap in list(validation_result.get("review_gaps") or []):
            st.warning(str(gap))
    not_run_critical = list(validation_result.get("not_run_critical_domains") or [])
    if not_run_critical:
        st.info("아래 NOT_RUN 항목은 Final Review에서 선택/보류/재검토 판단 근거로 확인해야 합니다.")
        st.dataframe(pd.DataFrame(not_run_critical), width="stretch", hide_index=True)
    curve_evidence = dict(validation_result.get("curve_evidence") or {})
    if curve_evidence:
        st.markdown("##### Curve / Recheck Evidence")
        render_badge_strip(
            [
                {"label": "Portfolio Curve", "value": curve_evidence.get("portfolio_curve_source") or "-", "tone": "positive" if curve_evidence.get("portfolio_curve_rows") else "warning"},
                {"label": "Rows", "value": curve_evidence.get("portfolio_curve_rows", 0), "tone": "neutral"},
                {"label": "Benchmark", "value": curve_evidence.get("benchmark_ticker") or "-", "tone": "neutral"},
                {"label": "Benchmark Rows", "value": curve_evidence.get("benchmark_curve_rows", 0), "tone": "neutral"},
            ]
        )
        component_curve_rows = list(curve_evidence.get("component_curve_rows") or [])
        if component_curve_rows:
            st.dataframe(pd.DataFrame(component_curve_rows), width="stretch", hide_index=True)
        benchmark_parity = dict(curve_evidence.get("benchmark_parity") or {})
        if benchmark_parity:
            render_badge_strip(
                [
                    {
                        "label": "Benchmark Parity",
                        "value": benchmark_parity.get("status") or "-",
                        "tone": _status_tone(benchmark_parity.get("status")),
                    },
                    {
                        "label": "Coverage",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("coverage_ratio", "-"),
                        "tone": "neutral",
                    },
                    {
                        "label": "Same Period",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("same_period", "-"),
                        "tone": "neutral",
                    },
                    {
                        "label": "Same Frequency",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("same_frequency", "-"),
                        "tone": "neutral",
                    },
                ]
            )
            parity_rows = list(benchmark_parity.get("rows") or [])
            if parity_rows:
                st.dataframe(pd.DataFrame(parity_rows), width="stretch", hide_index=True)
        curve_provenance = dict(curve_evidence.get("curve_provenance") or {})
        if curve_provenance:
            with st.expander("Curve provenance", expanded=False):
                st.json(curve_provenance)

    with st.expander("진단 세부 근거", expanded=False):
        for diagnostic in list(validation_result.get("diagnostic_results") or []):
            st.markdown(f"**{diagnostic.get('title')}**")
            render_badge_strip(
                [
                    {"label": "Status", "value": diagnostic.get("status") or "-", "tone": _status_tone(diagnostic.get("status"))},
                    {"label": "Metric", "value": diagnostic.get("key_metric") or "-", "tone": "neutral"},
                    {"label": "Origin", "value": diagnostic.get("origin") or "-", "tone": "neutral"},
                ]
            )
            st.caption(str(diagnostic.get("summary") or "-"))
            evidence_rows = list(diagnostic.get("evidence_rows") or [])
            if evidence_rows:
                st.dataframe(pd.DataFrame(evidence_rows), width="stretch", hide_index=True)
            limitations = list(diagnostic.get("limitations") or [])
            if limitations:
                st.caption("Limitations: " + " / ".join(str(item) for item in limitations))
    profile_score_rows = list(validation_result.get("profile_score_rows") or [])
    if profile_score_rows:
        with st.expander("Profile-aware score breakdown", expanded=False):
            st.dataframe(pd.DataFrame(profile_score_rows), width="stretch", hide_index=True)


def render_practical_validation_workspace() -> None:
    st.markdown("### Practical Validation")
    st.caption(
        "Backtest Analysis에서 선택한 후보를 실전 투입 전 관점으로 검증합니다. "
        "최종 사용자 메모와 최종 판단은 Final Review에서만 남깁니다."
    )

    sources = load_portfolio_selection_sources(limit=100)
    validation_rows = load_practical_validation_results(limit=100)
    session_source = st.session_state.get("backtest_practical_validation_source")
    notice = st.session_state.pop("backtest_practical_validation_notice", None)
    if notice:
        st.success(str(notice))

    render_status_card_grid(
        [
            {"title": "Selection Sources", "value": len(sources), "tone": "positive" if sources else "neutral"},
            {"title": "Validation Results", "value": len(validation_rows), "tone": "positive" if validation_rows else "neutral"},
            {"title": "Final Memo", "value": "Final Review Only", "tone": "neutral"},
            {"title": "Live Approval", "value": "Disabled", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        render_stage_brief(
            purpose="선택된 단일 전략, Compare 후보, 저장 Mix를 같은 Clean V2 source로 읽습니다.",
            result="Practical Validation result",
        )
        st.caption(f"Sources: `{PORTFOLIO_SELECTION_SOURCE_FILE}`")
        st.caption(f"Validation: `{PRACTICAL_VALIDATION_RESULT_FILE}`")

    selectable_sources: list[dict[str, Any]] = []
    if isinstance(session_source, dict) and session_source:
        selectable_sources.append(dict(session_source))
    existing_ids = {str(row.get("selection_source_id") or "") for row in selectable_sources}
    for row in sources:
        source_id = str(row.get("selection_source_id") or "")
        if source_id in existing_ids:
            continue
        selectable_sources.append(dict(row))

    if not selectable_sources:
        st.info("아직 Practical Validation으로 보낸 Clean V2 source가 없습니다.")
        st.caption("Backtest Analysis에서 Single / Compare / Saved Mix 결과를 선택하면 여기에 표시됩니다.")
        return

    labels = [_source_label(row) for row in selectable_sources]
    selected_label = st.selectbox("검증할 후보 source", options=labels, key="practical_validation_source_selected")
    source = selectable_sources[labels.index(selected_label)]

    st.markdown("#### 1. 선택 후보 확인")
    with st.container(border=True):
        _render_source_summary(source)

    st.markdown("#### 2. 검증 프로필")
    with st.container(border=True):
        validation_profile = _render_validation_profile_form()

    st.markdown("#### 3. 최신 데이터 기준 전략 재검증")
    with st.container(border=True):
        replay_result = _render_actual_replay_panel(source)

    validation_result = build_practical_validation_result(
        source,
        validation_profile=validation_profile,
        replay_result=replay_result,
    )
    st.markdown("#### 4. 실전 진단 보드")
    with st.container(border=True):
        _render_validation_result(validation_result)

    st.markdown("#### 5. 다음 단계")
    with st.container(border=True):
        st.info(
            "이 단계는 구조화된 검증 자료를 저장합니다. "
            "선정 / 보류 / 거절 / 재검토 판단과 최종 메모는 Final Review에서 기록합니다."
        )
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button("검증 결과 저장", key="practical_validation_save_result", width="stretch"):
                save_practical_validation_result(validation_result)
                st.success(f"검증 결과 `{validation_result['validation_id']}`를 저장했습니다.")
        with action_cols[1]:
            is_blocked = validation_result.get("validation_route") == "BLOCKED"
            if st.button(
                "Final Review로 이동",
                key="practical_validation_send_final_review",
                width="stretch",
                disabled=is_blocked,
            ):
                queue_final_review_source_from_validation(
                    source=source,
                    validation_result=validation_result,
                    persist_validation=True,
                )
                st.rerun()
            if is_blocked:
                st.caption("BLOCKED 상태는 Backtest Analysis에서 source를 보강한 뒤 Final Review로 보낼 수 있습니다.")

    with st.expander("Clean V2 Source JSON", expanded=False):
        st.json(source)
    with st.expander("Practical Validation Result JSON", expanded=False):
        st.json(validation_result)
