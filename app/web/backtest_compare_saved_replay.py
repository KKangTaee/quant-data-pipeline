from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from app.runtime import (
    SAVED_PORTFOLIO_FILE,
    append_backtest_run_history,
    delete_saved_portfolio,
    load_saved_portfolios,
)
from app.services.backtest_practical_validation_curve_context import (
    compact_curve_snapshot_from_bundle,
)
from app.services.backtest_practical_validation_source import (
    build_selection_source_from_saved_mix_prefill,
    compact_selection_history_from_bundle,
)
from app.services.backtest_result_read_model import build_strategy_data_trust_rows
from app.services.backtest_saved_portfolio_replay import replay_saved_portfolio_record
from app.web.backtest_common import _render_summary_metrics
from app.web.backtest_history import (
    render_real_money_guardrail_parity_snapshot as _render_real_money_guardrail_parity_snapshot,
)
from app.web.backtest_practical_validation_handoff import (
    apply_practical_validation_source_handoff,
)
from app.web.backtest_strategy_catalog import display_name_to_selection
from app.workspace_paths import REGISTRIES_DIR


@dataclass(frozen=True)
class SavedReplayRenderContext:
    run_compare_strategy: Callable[..., dict[str, Any]]
    resolve_dynamic_inputs: Callable[..., dict[str, Any]]
    build_compare_data_trust_assessment: Callable[[dict[str, Any]], dict[str, Any]]
    render_weighted_portfolio_result: Callable[[dict[str, Any]], None]
    build_compare_strategy_overview_rows: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]
    compare_source_kind_label: Callable[[str | None], str]
    compare_mode_strategy: str


def _safe_int_value(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _weighted_bundle_actual_end(bundle: dict[str, Any]) -> str | None:
    result_df = bundle.get("result_df")
    if not isinstance(result_df, pd.DataFrame) or result_df.empty or "Date" not in result_df.columns:
        return None
    actual_end = pd.to_datetime(result_df["Date"], errors="coerce").max()
    if pd.isna(actual_end):
        return None
    return str(actual_end.date())


def _bundle_result_period(bundle: dict[str, Any]) -> dict[str, str | None]:
    result_df = bundle.get("result_df")
    if not isinstance(result_df, pd.DataFrame) or result_df.empty or "Date" not in result_df.columns:
        meta = dict(bundle.get("meta") or {})
        return {"start": meta.get("start"), "end": meta.get("actual_result_end") or meta.get("end")}
    dates = pd.to_datetime(result_df["Date"], errors="coerce").dropna()
    if dates.empty:
        return {"start": None, "end": None}
    return {"start": str(dates.min().date()), "end": str(dates.max().date())}


def _bundle_summary_snapshot(bundle: dict[str, Any]) -> dict[str, Any]:
    summary_df = bundle.get("summary_df")
    if not isinstance(summary_df, pd.DataFrame) or summary_df.empty:
        return {}
    row = dict(summary_df.iloc[0].to_dict())
    return {
        "name": row.get("Name"),
        "cagr": row.get("CAGR"),
        "mdd": row.get("Maximum Drawdown"),
        "sharpe": row.get("Sharpe Ratio"),
        "end_balance": row.get("End Balance"),
    }


def _saved_mix_slug(value: Any) -> str:
    raw = str(value or "").strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw)
    return "_".join(part for part in cleaned.split("_") if part) or "saved_mix"


def _saved_mix_component_role(strategy_name: str, weight: float, max_weight: float) -> str:
    if weight == max_weight:
        return "core_anchor"
    if "risk" in strategy_name.lower() or "bond" in strategy_name.lower():
        return "defensive_sleeve"
    return "diversifier"


# Read current workflow and legacy append-only records to see whether a saved mix
# has moved beyond reusable setup storage into validation / final-review records.
def _find_saved_mix_workflow_references(record: dict[str, Any]) -> list[dict[str, str]]:
    portfolio_id = str(record.get("portfolio_id") or "").strip()
    portfolio_name = str(record.get("name") or "").strip()
    search_terms = [term for term in {portfolio_id, portfolio_name} if term]
    if not search_terms:
        return []

    registry_paths = [
        REGISTRIES_DIR / "PORTFOLIO_SELECTION_SOURCES.jsonl",
        REGISTRIES_DIR / "PRACTICAL_VALIDATION_RESULTS.jsonl",
        REGISTRIES_DIR / "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        REGISTRIES_DIR / "SELECTED_PORTFOLIO_MONITORING_LOG.jsonl",
        REGISTRIES_DIR / "CURRENT_CANDIDATE_REGISTRY.jsonl",
        REGISTRIES_DIR / "PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
        REGISTRIES_DIR / "PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
        REGISTRIES_DIR / "FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl",
    ]
    references: list[dict[str, str]] = []
    for path in registry_paths:
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if any(term in line for term in search_terms):
                references.append(
                    {
                        "Registry": path.name,
                        "Line": str(line_number),
                        "Matched": ", ".join(term for term in search_terms if term in line),
                    }
                )
    return references


# Evaluate a saved weighted mix as a reusable portfolio setup, separate from the
# single-strategy Compare handoff gate.
def _build_saved_mix_validation_evaluation(
    *,
    record: dict[str, Any],
    weighted_bundle: dict[str, Any] | None,
    bundles: list[dict[str, Any]] | None,
    context: SavedReplayRenderContext,
) -> dict[str, Any]:
    replay_ready = (
        isinstance(weighted_bundle, dict)
        and isinstance(weighted_bundle.get("summary_df"), pd.DataFrame)
        and not weighted_bundle["summary_df"].empty
        and isinstance(weighted_bundle.get("result_df"), pd.DataFrame)
        and not weighted_bundle["result_df"].empty
    )
    compare_context = dict(record.get("compare_context") or {})
    requested_end = compare_context.get("end")
    actual_end = _weighted_bundle_actual_end(weighted_bundle or {}) if replay_ready else None
    requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
    actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
    shortened_days = (
        (requested_end_ts.date() - actual_end_ts.date()).days
        if pd.notna(requested_end_ts)
        and pd.notna(actual_end_ts)
        and actual_end_ts.date() < requested_end_ts.date()
        else 0
    )

    component_bundles = list(bundles or [])
    component_data_assessments = [
        context.build_compare_data_trust_assessment(bundle)
        for bundle in component_bundles
    ]
    cadence_alignments = [
        dict(assessment.get("cadence_alignment") or {})
        for assessment in component_data_assessments
        if assessment.get("cadence_alignment")
    ]
    data_rows = list((weighted_bundle or {}).get("component_data_trust_rows") or [])
    has_component_error = any(str(row.get("Price Freshness") or "").strip().lower() == "error" for row in data_rows)
    has_cadence_aligned_gap = bool(shortened_days > 31 and cadence_alignments)
    has_component_review = shortened_days > 0 or any(
        str(row.get("Interpretation") or "").strip() not in {"", "-", "눈에 띄는 데이터 이슈 없음"}
        or _safe_int_value(row.get("Warnings")) > 0
        or _safe_int_value(row.get("Excluded Tickers")) > 0
        or _safe_int_value(row.get("Malformed Tickers")) > 0
        for row in data_rows
    )
    if not replay_ready:
        data_status = "FAIL"
        data_score = 0.0
        data_judgment = "replay 결과 없음"
    elif has_component_error:
        data_status = "FAIL"
        data_score = 0.0
        data_judgment = "구성 전략 데이터에 error가 있음"
    elif has_cadence_aligned_gap:
        data_status = "CADENCE ALIGNED"
        data_score = 1.5
        data_judgment = "구성 전략 결과 종료일 차이는 정상 cadence 범위로 보임"
    elif has_component_review:
        data_status = "REVIEW"
        data_score = 1.0
        data_judgment = "구성 전략 기간 / warning 확인 필요"
    else:
        data_status = "PASS"
        data_score = 2.0
        data_judgment = "구성 전략 데이터 조건이 깨끗함"

    real_money_missing: list[str] = []
    real_money_blocked: list[str] = []
    for bundle in component_bundles:
        meta = dict(bundle.get("meta") or {})
        strategy_name = str(bundle.get("strategy_name") or meta.get("strategy_name") or "-")
        promotion = str(meta.get("promotion_decision") or "").strip().lower()
        deployment = str(meta.get("deployment_readiness_status") or "").strip().lower()
        if not meta.get("real_money_hardening"):
            real_money_missing.append(strategy_name)
        if promotion == "hold" or deployment == "blocked":
            real_money_blocked.append(strategy_name)
    if real_money_blocked:
        real_money_status = "FAIL"
        real_money_score = 0.0
        real_money_judgment = "Real-Money blocker가 있는 구성 전략 포함"
    elif real_money_missing:
        real_money_status = "REVIEW"
        real_money_score = 1.0
        real_money_judgment = "Real-Money 정보가 없는 구성 전략 포함"
    elif component_bundles:
        real_money_status = "PASS"
        real_money_score = 2.0
        real_money_judgment = "구성 전략 Real-Money gate가 막지 않음"
    else:
        real_money_status = "REVIEW"
        real_money_score = 1.0
        real_money_judgment = "구성 전략 replay 정보 확인 필요"

    workflow_references = _find_saved_mix_workflow_references(record)
    workflow_status = "PASS" if workflow_references else "NOT RECORDED"
    workflow_score = 3.0 if workflow_references else 0.0
    workflow_judgment = (
        "Practical Validation / Final Review 기록 있음"
        if workflow_references
        else "saved mix setup만 있고 Practical Validation / Final Review 기록은 아직 없음"
    )

    replay_score = 3.0 if replay_ready else 0.0
    score = round(replay_score + data_score + real_money_score + workflow_score, 1)
    if not replay_ready or data_status == "FAIL" or real_money_status == "FAIL":
        stage_status = "BLOCKED"
        verdict = "Replay 또는 구성 전략 gate를 먼저 해결해야 합니다."
        tone = "error"
    elif workflow_status == "PASS":
        stage_status = "WORKFLOW RECORDED"
        verdict = "저장 mix가 Practical Validation / Final Review 기록에서도 확인됩니다."
        tone = "success"
    else:
        stage_status = "REPLAY OK"
        verdict = "성과 replay는 가능하지만, Practical Validation / Final Review 기록은 아직 없습니다."
        tone = "warning"

    criteria_rows = [
        {
            "기준": "Mix Replay",
            "상태": "PASS" if replay_ready else "FAIL",
            "현재 값": "weighted result 생성됨" if replay_ready else "weighted result 없음",
            "점수": f"{replay_score:g} / 3",
            "판단": "저장된 compare context와 weights로 다시 실행 가능" if replay_ready else "Mix 재실행 및 검증을 다시 실행해야 함",
        },
        {
            "기준": "Mix Data Trust",
            "상태": data_status,
            "현재 값": f"actual_end={actual_end or '-'}, requested_end={requested_end or '-'}",
            "점수": f"{data_score:g} / 2",
            "판단": (
                "; ".join(str(item.get("judgment")) for item in cadence_alignments if item.get("judgment"))
                if cadence_alignments
                else
                f"{data_judgment}, {shortened_days}일 짧음"
                if shortened_days
                else data_judgment
            ),
        },
        {
            "기준": "Component Real-Money",
            "상태": real_money_status,
            "현재 값": real_money_judgment,
            "점수": f"{real_money_score:g} / 2",
            "판단": ", ".join(real_money_blocked or real_money_missing) or "특이사항 없음",
        },
        {
            "기준": "Workflow Records",
            "상태": workflow_status,
            "현재 값": f"{len(workflow_references)}개 참조",
            "점수": f"{workflow_score:g} / 3",
            "판단": workflow_judgment,
        },
    ]

    return {
        "score": score,
        "stage_status": stage_status,
        "verdict": verdict,
        "tone": tone,
        "can_send_to_practical_validation": not (
            not replay_ready or data_status == "FAIL" or real_money_status == "FAIL"
        ),
        "criteria_rows": criteria_rows,
        "workflow_references": workflow_references,
        "data_rows": data_rows,
        "actual_end": actual_end,
        "requested_end": requested_end,
        "shortened_days": shortened_days,
        "cadence_alignments": cadence_alignments,
    }


# Build the cross-panel payload that turns a replayed saved mix into a current
# workflow validation source rather than a single-strategy handoff.
def _build_saved_mix_validation_prefill_payload(
    record: dict[str, Any],
    *,
    context: SavedReplayRenderContext,
) -> dict[str, Any]:
    weighted_bundle = dict(st.session_state.get("backtest_weighted_bundle") or {})
    bundles = list(st.session_state.get("backtest_compare_bundles") or [])
    compare_context = dict(record.get("compare_context") or {})
    portfolio_context = dict(record.get("portfolio_context") or {})
    source_context = dict(record.get("source_context") or {})
    upstream_context = dict(source_context.get("compare_source_context") or {})
    registry_ids = list(upstream_context.get("registry_ids") or [])
    candidate_titles = list(upstream_context.get("candidate_titles") or [])
    weights_percent = [float(weight) for weight in list(portfolio_context.get("weights_percent") or [])]
    strategy_names = list(portfolio_context.get("strategy_names") or compare_context.get("selected_strategies") or [])
    max_weight = max(weights_percent, default=0.0)
    override_map = dict(compare_context.get("strategy_overrides") or {})

    components: list[dict[str, Any]] = []
    for idx, strategy_name in enumerate(strategy_names):
        bundle = next((item for item in bundles if str(item.get("strategy_name") or "") == str(strategy_name)), {})
        meta = dict(bundle.get("meta") or {})
        summary = _bundle_summary_snapshot(bundle)
        data_assessment = context.build_compare_data_trust_assessment(bundle) if bundle else {}
        weight = weights_percent[idx] if idx < len(weights_percent) else 0.0
        registry_id = str(registry_ids[idx]) if idx < len(registry_ids) else ""
        if not registry_id:
            registry_id = f"saved_mix_component_{_saved_mix_slug(record.get('portfolio_id'))}_{_saved_mix_slug(strategy_name)}"
        contract = {
            "start": compare_context.get("start"),
            "end": compare_context.get("end"),
            "timeframe": compare_context.get("timeframe"),
            "option": compare_context.get("option"),
            **dict(override_map.get(strategy_name) or {}),
        }
        title = str(candidate_titles[idx]) if idx < len(candidate_titles) else str(strategy_name)
        components.append(
            {
                "registry_id": registry_id,
                "title": title,
                "strategy_family": _saved_mix_slug(strategy_name),
                "strategy_name": strategy_name,
                "candidate_role": "saved_mix_component",
                "proposal_role": _saved_mix_component_role(str(strategy_name), weight, max_weight),
                "target_weight": weight,
                "weight_reason": "Saved Mix에서 재생성한 목표 비중",
                "data_trust_status": str(data_assessment.get("gate_status") or "warning"),
                "pre_live_status": "saved_mix_replay",
                "promotion": meta.get("promotion_decision"),
                "shortlist": meta.get("shortlist_status"),
                "deployment": meta.get("deployment_readiness_status"),
                "cagr": summary.get("cagr"),
                "mdd": summary.get("mdd"),
                "period": _bundle_result_period(bundle),
                "result_curve": compact_curve_snapshot_from_bundle(bundle),
                "selection_history": compact_selection_history_from_bundle(bundle, component_weight=weight),
                "contract": contract,
                "benchmark": meta.get("benchmark_ticker") or contract.get("benchmark_ticker") or "-",
                "universe": ",".join(str(ticker) for ticker in list(contract.get("tickers") or [])) or str(contract.get("preset_name") or "-"),
                "compare_evidence": {
                    "source_kind": "saved_mix_replay",
                    "saved_portfolio_id": record.get("portfolio_id"),
                    "saved_portfolio_name": record.get("name"),
                    "date_policy": portfolio_context.get("date_policy"),
                },
                "open_candidate_blockers": [],
            }
        )

    return {
        "source_kind": "saved_portfolio_mix",
        "saved_portfolio_id": record.get("portfolio_id"),
        "saved_portfolio_name": record.get("name"),
        "description": record.get("description"),
        "compare_context": compare_context,
        "portfolio_context": portfolio_context,
        "source_context": source_context,
        "weighted_summary": _bundle_summary_snapshot(weighted_bundle),
        "weighted_period": _bundle_result_period(weighted_bundle),
        "weighted_curve_snapshot": compact_curve_snapshot_from_bundle(weighted_bundle),
        "selection_history_snapshot": compact_selection_history_from_bundle(weighted_bundle),
        "components": components,
    }


# Render the saved-mix stop/go board in the saved portfolio workspace.
def _render_saved_mix_validation_board(
    record: dict[str, Any],
    *,
    context: SavedReplayRenderContext,
) -> None:
    weighted_bundle = st.session_state.get("backtest_weighted_bundle")
    bundles = st.session_state.get("backtest_compare_bundles") or []
    evaluation = _build_saved_mix_validation_evaluation(
        record=record,
        weighted_bundle=weighted_bundle,
        bundles=bundles,
        context=context,
    )
    with st.container(border=True):
        st.markdown("### Portfolio Mix 검증 보드")
        st.caption(
            "이 보드는 저장 mix 자체를 다시 열었을 때 보는 검증입니다. "
            "component 개별 handoff와 분리해서, mix replay 가능 여부와 Practical Validation 연결 가능성을 봅니다."
        )
        metric_cols = st.columns([0.2, 0.18, 0.18, 0.44], gap="small")
        metric_cols[0].metric("Mix 상태", str(evaluation["stage_status"]))
        metric_cols[1].metric("Readiness", f"{float(evaluation['score']):.1f} / 10")
        metric_cols[2].metric("Blockers", sum(1 for row in evaluation["criteria_rows"] if row["상태"] == "FAIL"))
        with metric_cols[3]:
            st.caption("판정")
            st.markdown(f"**{evaluation['verdict']}**")
            st.caption("다음 행동")
            if evaluation["stage_status"] == "WORKFLOW RECORDED":
                st.markdown("Practical Validation / Final Review 쪽 기록을 열어 실제 통과 판단을 이어서 확인합니다.")
            elif evaluation["tone"] == "warning":
                st.markdown("이 mix를 실전 검증 후보로 쓰려면 Practical Validation source로 저장해야 합니다.")
            else:
                st.markdown("Replay result, Data Trust, Real-Money blocker를 먼저 다시 확인합니다.")
        st.progress(max(0.0, min(float(evaluation["score"]) / 10.0, 1.0)))
        message = (
            f"{evaluation['verdict']} "
            "Saved mix는 reusable setup이므로, 이 보드에서 현재 검증 기록 유무를 따로 확인합니다."
        )
        if evaluation["tone"] == "success":
            st.success(message)
        elif evaluation["tone"] == "warning":
            st.warning(message)
        else:
            st.error(message)
        if evaluation["tone"] != "error":
            st.info(
                "이 saved mix는 이미 비중이 정해진 포트폴리오 조합입니다. "
                "따라서 단일 전략 후보로 보내지 않고, mix 전체를 Practical Validation source로 기록합니다."
            )
            if st.button(
                "Practical Validation으로 보내기",
                key=f"use_saved_mix_in_practical_validation_{record.get('portfolio_id')}",
                disabled=not bool(evaluation.get("can_send_to_practical_validation")),
                use_container_width=True,
            ):
                prefill = _build_saved_mix_validation_prefill_payload(record, context=context)
                source = build_selection_source_from_saved_mix_prefill(prefill)
                apply_practical_validation_source_handoff(source)
                st.session_state.backtest_practical_validation_saved_mix_prefill = prefill
                st.session_state.backtest_practical_validation_saved_mix_notice = (
                    f"Saved Mix `{record.get('name')}`를 Practical Validation source로 저장했습니다. "
                    "이 경로는 legacy Candidate / Proposal 저장을 필수로 요구하지 않습니다."
                )
                st.rerun()
        st.dataframe(pd.DataFrame(evaluation["criteria_rows"]), use_container_width=True, hide_index=True)
        if evaluation["workflow_references"]:
            with st.expander("Workflow Registry References", expanded=False):
                st.dataframe(pd.DataFrame(evaluation["workflow_references"]), use_container_width=True, hide_index=True)
        if evaluation.get("cadence_alignments"):
            with st.expander("Cadence-Aligned Data Trust Notes", expanded=False):
                st.dataframe(pd.DataFrame(evaluation["cadence_alignments"]), use_container_width=True, hide_index=True)
        if evaluation["data_rows"]:
            with st.expander("Component Data Trust Snapshot", expanded=False):
                st.dataframe(pd.DataFrame(evaluation["data_rows"]), use_container_width=True, hide_index=True)


def _build_saved_portfolio_display_rows(
    saved_portfolios: list[dict[str, Any]],
    *,
    context: SavedReplayRenderContext,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in saved_portfolios:
        compare_context = item.get("compare_context") or {}
        portfolio_context = item.get("portfolio_context") or {}
        source_context = item.get("source_context") or {}
        strategy_names = list(portfolio_context.get("strategy_names") or compare_context.get("selected_strategies") or [])
        weights_percent = list(portfolio_context.get("weights_percent") or [])
        weight_pairs = [
            f"{strategy_name} {float(weight):.1f}%"
            for strategy_name, weight in zip(strategy_names, weights_percent)
        ]
        rows.append(
            {
                "Name": item.get("name"),
                "Updated At": item.get("updated_at") or item.get("saved_at"),
                "Strategies": ", ".join(strategy_names),
                "Weights": " | ".join(weight_pairs),
                "Date Policy": portfolio_context.get("date_policy"),
                "Period": f"{compare_context.get('start')} -> {compare_context.get('end')}",
                "Source": source_context.get("source_label") or context.compare_source_kind_label(source_context.get("source_kind")),
                "Description": item.get("description"),
            }
        )
    return pd.DataFrame(rows)


def _saved_portfolio_value_is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (float, np.floating)) and pd.isna(value):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _format_saved_portfolio_value(value: Any) -> str:
    if not _saved_portfolio_value_is_present(value):
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        items = [str(item) for item in list(value)]
        preview = ", ".join(items[:8])
        if len(items) > 8:
            preview += f" 외 {len(items) - 8}개"
        return preview
    if isinstance(value, dict):
        text = json.dumps(value, ensure_ascii=False, default=str)
    else:
        text = str(value)
    if len(text) > 140:
        return text[:137] + "..."
    return text


def _saved_portfolio_field_summary(source: dict[str, Any], fields: list[str]) -> str:
    pairs = [
        f"{field}={_format_saved_portfolio_value(source.get(field))}"
        for field in fields
        if _saved_portfolio_value_is_present(source.get(field))
    ]
    return " / ".join(pairs) if pairs else "-"


def _saved_portfolio_present_count(source: dict[str, Any], fields: list[str]) -> int:
    return sum(1 for field in fields if _saved_portfolio_value_is_present(source.get(field)))


def _saved_portfolio_strategy_expected_fields(strategy_name: str) -> tuple[list[str], str]:
    if strategy_name.endswith("(Strict Annual)") or strategy_name.endswith("(Strict Quarterly Prototype)"):
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "top_n",
            "rebalance_interval",
            "factor_freq",
            "snapshot_mode",
            "quality_factors",
            "value_factors",
            "universe_contract",
            "dynamic_target_size",
            "trend_filter_enabled",
            "trend_filter_window",
            "weighting_mode",
            "rejected_slot_handling_mode",
            "risk_off_mode",
            "defensive_tickers",
            "market_regime_enabled",
            "benchmark_contract",
            "benchmark_ticker",
            "guardrail_reference_ticker",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
        return fields, "strict factor 전략은 cadence, factor, universe, overlay, portfolio handling, guardrail 설정이 replay 의미를 결정합니다."

    if strategy_name == "Global Relative Strength":
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "cash_ticker",
            "top",
            "interval",
            "score_lookback_months",
            "score_return_columns",
            "score_weights",
            "trend_filter_window",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
        ]
        return fields, "GRS는 score horizon / weight, cash ticker, trend window가 replay 의미를 결정합니다."

    if strategy_name == "GTAA":
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "top",
            "interval",
            "score_lookback_months",
            "score_return_columns",
            "score_weights",
            "trend_filter_window",
            "risk_off_mode",
            "defensive_tickers",
            "market_regime_enabled",
            "crash_guardrail_enabled",
            "benchmark_ticker",
        ]
        return fields, "GTAA는 score, risk-off, defensive sleeve, crash guardrail 설정이 replay 의미를 결정합니다."

    if strategy_name == "Risk Parity Trend":
        fields = [
            "rebalance_interval",
            "vol_window",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
        return fields, "Risk Parity Trend는 vol window와 ETF operability / guardrail 입력을 같이 확인합니다."

    if strategy_name == "Dual Momentum":
        fields = [
            "top",
            "rebalance_interval",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
            "underperformance_guardrail_enabled",
            "drawdown_guardrail_enabled",
        ]
        return fields, "Dual Momentum은 top, cadence, ETF operability / guardrail 입력을 같이 확인합니다."

    if strategy_name == "Equal Weight":
        fields = [
            "universe_mode",
            "preset_name",
            "tickers",
            "rebalance_interval",
            "min_price_filter",
            "transaction_cost_bps",
            "benchmark_ticker",
            "promotion_min_etf_aum_b",
            "promotion_max_bid_ask_spread_pct",
        ]
        return fields, "Equal Weight는 ticker universe, cadence, ETF operability / benchmark 입력을 같이 확인합니다."

    return ["universe_mode", "preset_name", "tickers", "top", "rebalance_interval"], "전략별 핵심 override가 저장됐는지 확인합니다."


def _build_saved_portfolio_replay_parity_rows(record: dict[str, Any]) -> pd.DataFrame:
    compare_context = dict(record.get("compare_context") or {})
    portfolio_context = dict(record.get("portfolio_context") or {})
    strategy_overrides = dict(compare_context.get("strategy_overrides") or {})
    selected_strategies = list(compare_context.get("selected_strategies") or [])
    strategy_names = list(portfolio_context.get("strategy_names") or [])
    weights_percent = list(portfolio_context.get("weights_percent") or [])

    rows: list[dict[str, str]] = []
    rows.append(
        {
            "확인 영역": "Component 공용 입력",
            "저장 상태": "저장됨" if _saved_portfolio_present_count(compare_context, ["start", "end", "timeframe", "option"]) == 4 else "일부 누락",
            "저장된 값": _saved_portfolio_field_summary(compare_context, ["start", "end", "timeframe", "option"]),
            "왜 중요한가": "Replay는 이 기간과 timeframe / option으로 component 실행을 다시 수행합니다.",
        }
    )
    rows.append(
        {
            "확인 영역": "전략 목록",
            "저장 상태": "저장됨" if selected_strategies else "누락 가능",
            "저장된 값": _format_saved_portfolio_value(selected_strategies),
            "왜 중요한가": "어떤 전략들을 다시 compare하고 weighted portfolio로 섞을지 결정합니다.",
        }
    )
    rows.append(
        {
            "확인 영역": "Weight / Date Alignment",
            "저장 상태": "저장됨" if len(weights_percent) == len(selected_strategies) and weights_percent else "일부 누락",
            "저장된 값": (
                f"strategy_names={_format_saved_portfolio_value(strategy_names)} / "
                f"weights_percent={_format_saved_portfolio_value(weights_percent)} / "
                f"date_policy={_format_saved_portfolio_value(portfolio_context.get('date_policy'))}"
            ),
            "왜 중요한가": "`전략 비교에서 수정하기`와 `Mix 재실행 및 검증`이 같은 weight와 date alignment로 이어지는지 확인합니다.",
        }
    )
    rows.append(
        {
            "확인 영역": "Strategy Override Map",
            "저장 상태": "저장됨" if all(strategy in strategy_overrides for strategy in selected_strategies) else "일부 누락",
            "저장된 값": f"{sum(1 for strategy in selected_strategies if strategy in strategy_overrides)} / {len(selected_strategies)} strategies",
            "왜 중요한가": "전략별 세부 옵션이 없으면 replay가 기본값으로 돌아가 다른 결과가 될 수 있습니다.",
        }
    )

    for strategy_name in selected_strategies:
        override = dict(strategy_overrides.get(strategy_name) or {})
        fields, reason = _saved_portfolio_strategy_expected_fields(strategy_name)
        present = _saved_portfolio_present_count(override, fields)
        status = "저장됨" if present >= max(1, min(4, len(fields))) else "누락 가능"
        if not override:
            status = "누락 가능"
        rows.append(
            {
                "확인 영역": strategy_name,
                "저장 상태": status,
                "저장된 값": _saved_portfolio_field_summary(override, fields),
                "왜 중요한가": reason,
            }
        )

    return pd.DataFrame(rows)


def _build_saved_portfolio_override_summary_rows(record: dict[str, Any]) -> pd.DataFrame:
    compare_context = dict(record.get("compare_context") or {})
    strategy_overrides = dict(compare_context.get("strategy_overrides") or {})
    rows: list[dict[str, Any]] = []
    for strategy_name in list(compare_context.get("selected_strategies") or []):
        override = dict(strategy_overrides.get(strategy_name) or {})
        _, strategy_variant = display_name_to_selection(strategy_name)
        rows.append(
            {
                "Strategy": strategy_name,
                "Variant": strategy_variant or "-",
                "Top / Interval": (
                    f"{override.get('top_n') or override.get('top') or '-'} / "
                    f"{override.get('rebalance_interval') or override.get('interval') or '-'}"
                ),
                "Universe": _format_saved_portfolio_value(
                    override.get("universe_contract") or override.get("preset_name") or override.get("universe_mode")
                ),
                "Cadence / Snapshot": _format_saved_portfolio_value(
                    override.get("factor_freq") or override.get("snapshot_mode") or override.get("score_lookback_months")
                ),
                "Overlay / Handling": _format_saved_portfolio_value(
                    {
                        key: override.get(key)
                        for key in [
                            "trend_filter_enabled",
                            "trend_filter_window",
                            "weighting_mode",
                            "rejected_slot_handling_mode",
                            "risk_off_mode",
                            "market_regime_enabled",
                        ]
                        if key in override
                    }
                ),
                "Benchmark / Guardrail": _format_saved_portfolio_value(
                    {
                        key: override.get(key)
                        for key in [
                            "benchmark_contract",
                            "benchmark_ticker",
                            "guardrail_reference_ticker",
                            "underperformance_guardrail_enabled",
                            "drawdown_guardrail_enabled",
                        ]
                        if key in override
                    }
                ),
            }
        )
    return pd.DataFrame(rows)


def _render_saved_portfolio_replay_parity_snapshot(record: dict[str, Any]) -> None:
    parity_df = _build_saved_portfolio_replay_parity_rows(record)
    if parity_df.empty:
        return

    compare_context = dict(record.get("compare_context") or {})
    portfolio_context = dict(record.get("portfolio_context") or {})
    selected_strategies = list(compare_context.get("selected_strategies") or [])
    weights_percent = list(portfolio_context.get("weights_percent") or [])

    st.markdown("#### 저장된 Mix Replay / 편집 Parity Snapshot")
    st.caption(
        "이 표는 저장된 portfolio mix를 `전략 비교에서 수정하기` 또는 `Mix 재실행 및 검증`으로 다시 열 때 "
        "전략 목록, 공용 기간, strategy-specific override, weight/date alignment가 충분히 남아 있는지 확인하는 표입니다."
    )
    metric_cols = st.columns(4, gap="small")
    metric_cols[0].metric("Strategies", len(selected_strategies))
    metric_cols[1].metric("Weights", len(weights_percent))
    metric_cols[2].metric("Overrides", len(dict(compare_context.get("strategy_overrides") or {})))
    metric_cols[3].metric("Date Policy", portfolio_context.get("date_policy") or "-")
    st.dataframe(parity_df, use_container_width=True, hide_index=True)

    override_df = _build_saved_portfolio_override_summary_rows(record)
    if not override_df.empty:
        with st.expander("Strategy Override Summary", expanded=False):
            st.caption(
                "전략별 저장 override를 사람이 읽기 쉬운 형태로 줄여서 보여줍니다. "
                "정확한 전체 payload는 `Mix Context` 또는 `Raw Record` 탭에서 확인합니다."
            )
            st.dataframe(override_df, use_container_width=True, hide_index=True)
    _render_real_money_guardrail_parity_snapshot(
        [
            {
                "strategy_name": strategy_name,
                "strategy_key": None,
                "data": dict((compare_context.get("strategy_overrides") or {}).get(strategy_name) or {}),
            }
            for strategy_name in selected_strategies
        ],
        title="Saved Portfolio Real-Money / Guardrail Scope",
        caption=(
            "저장 포트폴리오 안의 각 전략이 어떤 Real-Money / Guardrail 범위로 다시 열리는지 확인합니다. "
            "quarterly prototype과 ETF first-pass를 annual strict full surface로 오해하지 않기 위한 표입니다."
        ),
    )


def _run_saved_portfolio_record(
    record: dict[str, Any],
    *,
    context: SavedReplayRenderContext,
) -> None:
    replay_result = replay_saved_portfolio_record(
        record,
        run_strategy=context.run_compare_strategy,
        resolve_dynamic_inputs=context.resolve_dynamic_inputs,
    )

    st.session_state.backtest_compare_bundles = replay_result.bundles
    st.session_state.backtest_compare_error = None
    st.session_state.backtest_compare_error_kind = None
    st.session_state.backtest_weighted_bundle = replay_result.weighted_bundle
    st.session_state.backtest_weighted_error = None
    st.session_state.backtest_compare_source_context = replay_result.replay_source_context
    st.session_state.backtest_saved_portfolio_replay_id = str(record.get("portfolio_id") or "")
    st.session_state.backtest_compare_result_notice = None
    st.session_state.backtest_requested_panel = "Portfolio Mix Builder"

    append_backtest_run_history(
        bundle=replay_result.compare_history_bundle,
        run_kind="strategy_compare",
        context=replay_result.compare_history_context,
    )
    append_backtest_run_history(
        bundle=replay_result.weighted_bundle,
        run_kind="weighted_portfolio",
        context=replay_result.weighted_history_context,
    )


def _queue_saved_portfolio_compare_prefill(
    saved_portfolio: dict[str, Any],
    *,
    context: SavedReplayRenderContext,
) -> None:
    compare_context = dict(saved_portfolio.get("compare_context") or {})
    portfolio_context = dict(saved_portfolio.get("portfolio_context") or {})
    source_context = dict(saved_portfolio.get("source_context") or {})
    st.session_state.backtest_compare_prefill_payload = compare_context
    st.session_state.backtest_compare_prefill_pending = True
    st.session_state.backtest_saved_portfolio_replay_id = None
    st.session_state.backtest_compare_bundles = []
    st.session_state.backtest_compare_error = None
    st.session_state.backtest_compare_error_kind = None
    st.session_state.backtest_compare_result_notice = None
    st.session_state.backtest_weighted_bundle = None
    st.session_state.backtest_weighted_error = None
    st.session_state.backtest_compare_workspace_mode_request = context.compare_mode_strategy
    st.session_state.backtest_compare_prefill_notice = (
        f"저장된 Mix `{saved_portfolio.get('name')}`의 전략/기간/세부 설정과 "
        "weight/date alignment를 새 Mix 만들기 form에 다시 채웠습니다. "
        "이전 결과는 숨기고, 저장된 설정을 수정할 수 있는 form-first 상태로 전환했습니다."
    )
    st.session_state.backtest_compare_source_context = {
        "source_kind": "saved_portfolio",
        "source_label": saved_portfolio.get("name"),
        "saved_portfolio_id": saved_portfolio.get("portfolio_id"),
        "saved_portfolio_name": saved_portfolio.get("name"),
        "selected_strategies": list(compare_context.get("selected_strategies") or []),
        "weights_percent": list(portfolio_context.get("weights_percent") or []),
        "upstream_source_context": source_context,
    }
    st.session_state.backtest_weighted_portfolio_prefill = {
        "strategy_names": list(portfolio_context.get("strategy_names") or []),
        "weights_percent": list(portfolio_context.get("weights_percent") or []),
        "date_policy": portfolio_context.get("date_policy") or "intersection",
    }
    st.session_state.backtest_requested_panel = "Portfolio Mix Builder"


def is_saved_mix_replay_context() -> bool:
    source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    saved_portfolio_id = str(source_context.get("saved_portfolio_id") or "")
    replay_id = str(st.session_state.get("backtest_saved_portfolio_replay_id") or "")
    return (
        str(source_context.get("source_kind") or "").strip() == "saved_portfolio"
        and bool(replay_id)
        and replay_id == saved_portfolio_id
    )


# Keep replay details attached to the saved mix the user is currently inspecting.
def _saved_portfolio_replay_matches_selected_record(record: dict[str, Any]) -> bool:
    source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    replay_id = str(st.session_state.get("backtest_saved_portfolio_replay_id") or "")
    selected_id = str(record.get("portfolio_id") or "")
    return (
        bool(replay_id)
        and replay_id == selected_id
        and str(source_context.get("source_kind") or "").strip() == "saved_portfolio"
        and str(source_context.get("saved_portfolio_id") or "") == selected_id
        and isinstance(st.session_state.get("backtest_weighted_bundle"), dict)
    )


def _render_saved_mix_replay_result_card() -> None:
    source_context = dict(st.session_state.get("backtest_compare_source_context") or {})
    weighted_bundle = st.session_state.get("backtest_weighted_bundle")
    strategy_names = list(source_context.get("selected_strategies") or [])
    weights_percent = list(source_context.get("weights_percent") or [])
    source_label = str(source_context.get("source_label") or "Saved Portfolio Mix")
    saved_portfolio_id = str(source_context.get("saved_portfolio_id") or "-")

    with st.container(border=True):
        st.markdown("### 저장 Mix Replay 결과")
        st.caption(
            "이 영역은 저장된 비중 포트폴리오 mix 자체를 다시 연 결과입니다. "
            "아래 `Portfolio Mix 검증 보드`에서 mix replay와 workflow 기록 여부를 분리해서 확인합니다."
        )
        summary_cols = st.columns(4, gap="small")
        with summary_cols[0]:
            st.markdown(f"**Mix 이름**  \n{source_label}")
        with summary_cols[1]:
            st.markdown(f"**Portfolio ID**  \n`{saved_portfolio_id}`")
        with summary_cols[2]:
            st.markdown(f"**구성 전략**  \n{len(strategy_names)}개")
        with summary_cols[3]:
            st.markdown(
                "**비중**  \n"
                + (
                    " / ".join(f"{float(weight):.0f}%" for weight in weights_percent)
                    if weights_percent
                    else "-"
                )
            )
        if weighted_bundle and isinstance(weighted_bundle.get("summary_df"), pd.DataFrame):
            _render_summary_metrics(weighted_bundle["summary_df"])
            st.caption("상세 equity curve, contribution, result table은 아래 `3. 비중 포트폴리오 결과 확인`에서 확인합니다.")


def render_saved_portfolio_workspace(context: SavedReplayRenderContext) -> None:
    st.markdown("### 저장된 Mix")
    st.caption(
        "저장한 weighted portfolio mix를 다시 실행하고 mix-level 검증으로 읽습니다. "
        "개별 후보 검증이 아니라 Practical Validation으로 이어지는 비중 조합 작업 공간입니다."
    )

    saved_portfolios = load_saved_portfolios(limit=100)
    if not saved_portfolios:
        st.info("저장된 portfolio mix가 아직 없습니다. `새 Mix 만들기`에서 mix 후보 결과를 만든 뒤 저장할 수 있습니다.")
        st.caption(f"저장 위치: `{SAVED_PORTFOLIO_FILE}`")
        return

    st.caption(f"저장 위치: `{SAVED_PORTFOLIO_FILE}`")
    st.dataframe(_build_saved_portfolio_display_rows(saved_portfolios, context=context), use_container_width=True, hide_index=True)

    record_labels = [
        f"{item.get('updated_at') or item.get('saved_at')} | {item.get('name')}"
        for item in saved_portfolios
    ]
    selected_label = st.selectbox(
        "저장된 Mix 선택",
        options=record_labels,
        index=0,
        key="saved_portfolio_selected_record",
    )
    selected_record = saved_portfolios[record_labels.index(selected_label)]

    compare_context = selected_record.get("compare_context") or {}
    portfolio_context = selected_record.get("portfolio_context") or {}
    source_context = selected_record.get("source_context") or {}

    _render_saved_portfolio_replay_parity_snapshot(selected_record)

    detail_tabs = st.tabs(["Summary", "Source & Actions", "Mix Context", "Raw Record"])
    with detail_tabs[0]:
        st.json(
            {
                "portfolio_id": selected_record.get("portfolio_id"),
                "name": selected_record.get("name"),
                "description": selected_record.get("description"),
                "saved_at": selected_record.get("saved_at"),
                "updated_at": selected_record.get("updated_at"),
                "selected_strategies": compare_context.get("selected_strategies"),
                "weights_percent": portfolio_context.get("weights_percent"),
                "date_policy": portfolio_context.get("date_policy"),
                "period": f"{compare_context.get('start')} -> {compare_context.get('end')}",
            }
        )
    with detail_tabs[1]:
        st.markdown("##### Source")
        st.json(
            {
                "source_kind": source_context.get("compare_source_context", {}).get("source_kind") or source_context.get("created_from"),
                "source_label": source_context.get("compare_source_context", {}).get("source_label"),
                "source_strategy_names": source_context.get("source_strategy_names"),
            }
        )
        st.markdown("##### Next Action")
        st.markdown(
            "- `Mix 재실행 및 검증`: 저장 당시 compare context와 weighted portfolio 구성을 그대로 다시 실행하고 mix 검증 보드를 확인합니다."
        )
        st.markdown(
            "- `전략 비교에서 수정하기`: 저장된 전략 조합, compare 기간, strategy-specific 설정, weight/date alignment를 form에 다시 채워 수정합니다."
        )
        st.markdown("- `조합 삭제`: 더 이상 쓰지 않는 저장 mix를 정리합니다.")
    with detail_tabs[2]:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Mix Context")
            st.json(compare_context)
        with right:
            st.markdown("##### Portfolio Context")
            st.json(portfolio_context)
    with detail_tabs[3]:
        st.json(selected_record)

    action_cols = st.columns([0.24, 0.24, 0.20, 0.32], gap="small")
    with action_cols[0]:
        if st.button("Mix 재실행 및 검증", key="saved_portfolio_run", use_container_width=True):
            try:
                with st.spinner("Running saved mix from stored compare context...", show_time=True):
                    _run_saved_portfolio_record(selected_record, context=context)
                st.session_state.backtest_saved_portfolio_notice = (
                    f"저장된 portfolio mix `{selected_record.get('name')}`를 다시 실행했습니다."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Saved mix run failed: {exc}")
    with action_cols[1]:
        if st.button("전략 비교에서 수정하기", key="saved_portfolio_load_into_compare", use_container_width=True):
            _queue_saved_portfolio_compare_prefill(selected_record, context=context)
            st.rerun()
    with action_cols[2]:
        if st.button("조합 삭제", key="saved_portfolio_delete", use_container_width=True):
            if delete_saved_portfolio(str(selected_record.get("portfolio_id") or "")):
                st.session_state.backtest_saved_portfolio_notice = (
                    f"저장된 portfolio mix `{selected_record.get('name')}`를 삭제했습니다."
                )
                st.rerun()
            else:
                st.error("Saved mix delete failed.")
    with action_cols[3]:
        st.caption(
            "`Mix 재실행 및 검증`은 저장된 Mix 자체를 평가합니다. "
            "`전략 비교에서 수정하기`는 검증이 아니라 form 편집 / 재구성 진입입니다."
        )

    if _saved_portfolio_replay_matches_selected_record(selected_record):
        st.divider()
        _render_saved_mix_replay_result_card()
        _render_saved_mix_validation_board(selected_record, context=context)
        with st.expander("Weighted Portfolio Result 상세", expanded=True):
            weighted_bundle = st.session_state.get("backtest_weighted_bundle")
            if weighted_bundle:
                context.render_weighted_portfolio_result(weighted_bundle)
            else:
                st.info("Replay 결과가 아직 없습니다. `Mix 재실행 및 검증`을 다시 실행해 주세요.")
        bundles = st.session_state.get("backtest_compare_bundles") or []
        if bundles:
            with st.expander("구성 전략 참고 Summary", expanded=False):
                overview_rows = context.build_compare_strategy_overview_rows(list(bundles))
                if overview_rows:
                    st.dataframe(pd.DataFrame(overview_rows), use_container_width=True, hide_index=True)
                data_rows = build_strategy_data_trust_rows(list(bundles))
                if data_rows:
                    st.markdown("##### Component Data Trust")
                    st.dataframe(pd.DataFrame(data_rows), use_container_width=True, hide_index=True)


__all__ = [name for name in globals() if not name.startswith("__")]
