from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from app.services.backtest_strategy_catalog import LEVEL1_STRATEGY_MATURITY


BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION = (
    "backtest_analysis_result_workspace_v1"
)


def _strategy_maturity(strategy_choice: str | None) -> str:
    return LEVEL1_STRATEGY_MATURITY.get(str(strategy_choice or ""), "development")


def build_result_lifecycle(
    *,
    result_bundle: Mapping[str, Any] | None,
    current_configuration_fingerprint: str,
    result_configuration_fingerprint: str | None,
    result_requires_rerun: bool,
    is_running: bool,
    last_error: str | None,
    last_error_kind: str | None,
) -> dict[str, Any]:
    """Project run state without discarding the last successful result."""

    result_available = bool(result_bundle)
    fingerprint_matches = bool(
        result_available
        and result_configuration_fingerprint
        and current_configuration_fingerprint == result_configuration_fingerprint
    )
    reference_only = bool(
        result_available
        and (result_requires_rerun or not fingerprint_matches or last_error)
    )

    if is_running:
        state = "running_with_reference" if result_available else "running"
    elif last_error:
        state = "error_with_reference" if result_available else "error"
    elif not result_available:
        state = "hidden"
    elif reference_only:
        state = "stale"
    else:
        state = "fresh"

    display_labels = {
        "hidden": "",
        "running": "첫 결과를 만드는 중",
        "running_with_reference": "새 설정으로 실행 중",
        "error": "실행 결과를 만들지 못했습니다",
        "error_with_reference": "이전 설정 결과 · 참고용",
        "stale": "이전 설정 결과 · 참고용",
        "fresh": "현재 설정 결과",
    }
    return {
        "state": state,
        "display_label": display_labels[state],
        "show_workspace": result_available,
        "result_available": result_available,
        "fingerprint_matches": fingerprint_matches,
        "reference_only": reference_only or state == "running_with_reference",
        "is_running": is_running,
        "error": (
            {
                "kind": str(last_error_kind or "execution_failed"),
                "message": str(last_error),
            }
            if last_error
            else None
        ),
    }


def _core_result_reasons(
    result_bundle: Mapping[str, Any] | None,
) -> list[dict[str, str]]:
    bundle = dict(result_bundle or {})
    meta = dict(bundle.get("meta") or {})
    reasons: list[dict[str, str]] = []
    if not str(meta.get("run_id") or ""):
        reasons.append(
            {
                "root_issue_id": "run_identity",
                "message": "실행 결과 식별자가 없습니다.",
            }
        )
    for key, label in (
        ("summary_df", "성과 요약"),
        ("result_df", "결과 표"),
        ("chart_df", "성과 곡선"),
    ):
        value = bundle.get(key)
        if value is None or bool(getattr(value, "empty", False)):
            reasons.append(
                {
                    "root_issue_id": f"core:{key}",
                    "message": f"{label} 계약이 비어 있습니다.",
                }
            )
    return reasons


def build_level1_technical_handoff_readiness(
    *,
    workspace_kind: str,
    strategy_choice: str | None,
    result_bundle: Mapping[str, Any] | None,
    lifecycle: Mapping[str, Any],
    action_handlers: Mapping[str, Callable[..., Any] | None],
) -> dict[str, Any]:
    """Decide Level2 handoff from Level1-owned technical contracts only."""

    if not lifecycle.get("result_available"):
        return {
            "state": "result_required",
            "label": "결과 준비 필요",
            "can_handoff": False,
            "reasons": [],
            "action": None,
        }
    if (
        workspace_kind == "single_strategy"
        and _strategy_maturity(strategy_choice) != "production"
    ):
        return {
            "state": "unsupported",
            "label": "인계 기능 미지원",
            "can_handoff": False,
            "reasons": [],
            "action": None,
        }
    if not callable(action_handlers.get("save_and_move")):
        return {
            "state": "unsupported",
            "label": "인계 기능 미지원",
            "can_handoff": False,
            "reasons": [],
            "action": None,
        }

    reasons = _core_result_reasons(result_bundle)
    if lifecycle.get("state") != "fresh":
        return {
            "state": "rerun_required",
            "label": "재실행 필요",
            "can_handoff": False,
            "reasons": reasons,
            "action": None,
        }
    if reasons:
        return {
            "state": "result_required",
            "label": "결과 준비 필요",
            "can_handoff": False,
            "reasons": reasons,
            "action": None,
        }
    return {
        "state": "ready",
        "label": "Level2 인계 가능",
        "can_handoff": True,
        "reasons": [],
        "action": {
            "id": "save_and_move",
            "label": "후보로 저장하고 Level2로 이동",
            "enabled": True,
        },
    }


_LEVEL2_QUESTION_SPECS = (
    (
        "benchmark_comparison",
        "benchmark",
        "benchmark_available",
        {False, None, ""},
        "기준지수와 손익·낙폭 비교",
        "동일 기간 기준지수와의 차이를 Practical Validation에서 확인합니다.",
    ),
    (
        "rolling_oos_validation",
        "temporal_validation",
        "rolling_review_status",
        {"review", "not_run", "unavailable", ""},
        "구간별 성과 지속성",
        "rolling/OOS 구간에서 결과가 유지되는지 확인합니다.",
    ),
    (
        "split_oos_validation",
        "temporal_validation",
        "out_of_sample_review_status",
        {"review", "not_run", "unavailable", ""},
        "분할·홀드아웃 재검증",
        "학습 외 구간의 재현성을 확인합니다.",
    ),
    (
        "cost_turnover_realism",
        "execution_realism",
        "net_cost_curve_status",
        {"not_run", "unavailable", "applied_without_turnover_estimate", ""},
        "비용·교체 현실성",
        "turnover와 거래비용 반영 수준을 확인합니다.",
    ),
    (
        "liquidity_realism",
        "execution_realism",
        "liquidity_policy_status",
        {"caution", "review", "unavailable", ""},
        "유동성 적합성",
        "보유 후보의 거래 가능 규모를 확인합니다.",
    ),
    (
        "etf_operability",
        "execution_realism",
        "etf_operability_status",
        {"caution", "review", "unavailable", ""},
        "ETF 운용 가능성",
        "AUM·spread·holdings 근거를 확인합니다.",
    ),
    (
        "regime_validation",
        "temporal_validation",
        "regime_split_validation_status",
        {"review", "not_run", "unavailable", ""},
        "시장 국면별 재현성",
        "상승·하락·중립 국면에서 결과가 유지되는지 확인합니다.",
    ),
    (
        "construction_overlap",
        "execution_realism",
        "construction_risk_status",
        {"review", "not_run", "unavailable", ""},
        "집중도·중복 구성",
        "상위 보유 집중도와 구성 간 중복을 확인합니다.",
    ),
    (
        "latest_data_replay",
        "temporal_validation",
        "latest_data_replay_status",
        {"review", "not_run", "unavailable", ""},
        "최신 데이터 재검증",
        "현재 DB 기준으로 같은 설정을 다시 실행해 차이를 확인합니다.",
    ),
    (
        "evidence_development",
        "execution_realism",
        "evidence_adapter_status",
        {"review", "not_run", "unavailable", ""},
        "추가 검증 근거 필요 여부",
        "현재 근거로 확인할 수 없는 항목은 Level2에서 adapter 개발 필요성을 판단합니다.",
    ),
)


def build_level2_validation_questions(
    *,
    meta: Mapping[str, Any],
    workspace_kind: str,
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    """Project unresolved practical checks without affecting Level1 readiness."""

    del workspace_kind, component_bundles
    lane_labels = {
        "benchmark": "성과·위험 검증",
        "temporal_validation": "기간·재현성 검증",
        "execution_realism": "실행 현실성 검증",
    }
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for question_id, lane, field, unresolved, title, summary in _LEVEL2_QUESTION_SPECS:
        raw = meta.get(field)
        normalized = (
            raw
            if raw is None or isinstance(raw, bool)
            else str(raw).strip().lower()
        )
        if normalized not in unresolved:
            continue
        root = f"level2:{lane}:{question_id}"
        if root in seen:
            continue
        seen.add(root)
        rows.append(
            {
                "question_id": question_id,
                "root_issue_id": root,
                "lane": lane,
                "lane_label": lane_labels[lane],
                "status": "needs_validation",
                "title": title,
                "summary": summary,
            }
        )
    return rows


__all__ = [
    "BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION",
    "build_level1_technical_handoff_readiness",
    "build_level2_validation_questions",
    "build_result_lifecycle",
]
