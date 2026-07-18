from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from typing import Any

from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    LEVEL1_STRATEGY_PURPOSE_GROUPS,
    STRATEGY_FAMILY_VARIANTS,
)
from app.services.backtest_analysis_result_workspace import (
    build_level1_technical_handoff_readiness,
    build_level2_validation_questions,
    build_result_lifecycle,
)
from app.services.backtest_portfolio_mix_readiness import (
    build_mix_role_weight_rows,
)


BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION = (
    "backtest_analysis_decision_workspace_v1"
)
_ERROR_KIND_MAP = {
    "input": "configuration_required",
    "data": "data_required",
    "system": "execution_failed",
}


def _json_ready(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    scalar_item = getattr(value, "item", None)
    if callable(scalar_item):
        try:
            return _json_ready(scalar_item())
        except (TypeError, ValueError):
            pass
    return str(value)


def build_level1_configuration_fingerprint(
    *,
    workspace_kind: str,
    selection: Mapping[str, Any],
    configuration: Mapping[str, Any],
) -> str:
    """Create a stable identity for the current Level1 candidate configuration."""

    payload = {
        "workspace_kind": workspace_kind,
        "selection": _json_ready(dict(selection)),
        "configuration": _json_ready(dict(configuration)),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def level1_strategy_maturity(strategy_choice: str | None) -> str:
    """Return the Level1 handoff maturity for a strategy choice."""

    return LEVEL1_STRATEGY_MATURITY.get(str(strategy_choice or ""), "development")


def build_level1_strategy_catalog() -> list[dict[str, Any]]:
    """Project the strategy catalog into purpose groups for the Level1 selector."""

    groups: list[dict[str, Any]] = []
    for group_id, config in LEVEL1_STRATEGY_PURPOSE_GROUPS.items():
        items = [
            {
                "strategy_choice": choice,
                "maturity": level1_strategy_maturity(choice),
                "variants": list(STRATEGY_FAMILY_VARIANTS.get(choice, {}).keys()),
                "level2_handoff_supported": (
                    level1_strategy_maturity(choice) == "production"
                ),
            }
            for choice in config["items"]
        ]
        groups.append(
            {
                "group_id": group_id,
                "label": config["label"],
                "items": items,
            }
        )
    return groups


def _deduplicate_reasons(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Keep one user-facing row for each underlying Level1 issue."""

    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        root = str(row.get("root_issue_id") or row.get("message") or "").strip()
        if not root or root in seen:
            continue
        seen.add(root)
        result.append(
            {
                "root_issue_id": root,
                "message": str(row.get("message") or ""),
            }
        )
    return result


def build_level1_readiness_projection(
    *,
    workspace_kind: str,
    strategy_choice: str | None,
    result_bundle: dict[str, Any] | None,
    current_configuration_fingerprint: str,
    result_configuration_fingerprint: str | None,
    action_handlers: Mapping[str, Callable[..., Any] | None],
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Keep compatibility keys while delegating handoff to technical truth."""

    lifecycle = build_result_lifecycle(
        result_bundle=result_bundle,
        current_configuration_fingerprint=current_configuration_fingerprint,
        result_configuration_fingerprint=result_configuration_fingerprint,
        result_requires_rerun=bool(
            result_bundle
            and current_configuration_fingerprint
            != result_configuration_fingerprint
        ),
        is_running=False,
        last_error=None,
        last_error_kind=None,
    )
    result_available = bool(lifecycle["result_available"])
    freshness = (
        "none"
        if not result_available
        else "current"
        if lifecycle["state"] == "fresh"
        else "stale"
    )

    maturity = (
        level1_strategy_maturity(strategy_choice)
        if workspace_kind == "single_strategy"
        else "production"
    )
    meta = dict((result_bundle or {}).get("meta") or {})
    technical = build_level1_technical_handoff_readiness(
        workspace_kind=workspace_kind,
        strategy_choice=strategy_choice,
        result_bundle=result_bundle,
        lifecycle=lifecycle,
        action_handlers=action_handlers,
    )
    level2_questions = build_level2_validation_questions(
        meta=meta,
        workspace_kind=workspace_kind,
        component_bundles=component_bundles,
    )
    handoff_state = "ready" if technical["can_handoff"] else "blocked"
    evaluation = {
        "technical_handoff_readiness": technical,
        "level2_validation_questions": level2_questions,
    }

    actions: dict[str, dict[str, Any]] = {}
    if (
        workspace_kind == "portfolio_mix"
        and result_available
        and freshness == "current"
        and callable(action_handlers.get("save_mix"))
    ):
        actions["save_mix"] = {
            "id": "save_mix",
            "label": "Mix 저장",
            "enabled": True,
        }
    if technical.get("action"):
        actions["save_and_move"] = dict(technical["action"])

    gate_summary = {
        "can_submit": technical["can_handoff"],
        "action_items": [
            str(reason.get("message") or "")
            for reason in list(technical.get("reasons") or [])
        ],
        "evaluation": evaluation,
    }

    return {
        "result_available": result_available,
        "result_freshness": freshness,
        "strategy_maturity": maturity,
        "handoff_state": handoff_state,
        "actions": actions,
        "evaluation": evaluation,
        "gate_summary": gate_summary,
    }


def _configuration_summary(
    workspace_kind: str,
    configuration: Mapping[str, Any],
) -> dict[str, Any]:
    """Keep previous run payloads out of the current Single Strategy selector."""

    if workspace_kind == "single_strategy":
        return {}
    strategy_names = [
        str(name) for name in list(configuration.get("strategy_names") or [])
    ]
    weights = [
        float(weight)
        for weight in list(configuration.get("weights_percent") or [])
    ]
    return {
        "구성 전략": ", ".join(strategy_names) or "구성 전",
        "목표 비중": ", ".join(f"{weight:g}%" for weight in weights)
        or "설정 전",
        "구성 수": len(strategy_names),
    }


def _metric_items(summary_df: Any) -> list[dict[str, Any]]:
    if summary_df is None or getattr(summary_df, "empty", True):
        return []
    row = summary_df.iloc[0]
    definitions = [
        ("cagr", "연환산 수익률", "CAGR"),
        ("maximum_drawdown", "최대 낙폭", "Maximum Drawdown"),
        ("sharpe_ratio", "위험 대비 수익", "Sharpe Ratio"),
        ("volatility", "변동성", "Standard Deviation"),
    ]
    return [
        {
            "metric_id": key,
            "label": label,
            "value": _json_ready(row.get(column)),
        }
        for key, label, column in definitions
        if column in row.index
    ]


def _plain_reasons(readiness: Mapping[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    gate_summary = dict(readiness.get("gate_summary") or {})
    for index, message in enumerate(list(gate_summary.get("action_items") or [])):
        text = str(message)
        if "app." in text or "result_df." in text:
            text = "실행 계약의 기술 근거를 상세 근거에서 확인해야 합니다."
        rows.append(
            {
                "root_issue_id": f"gate:{index}:{text}",
                "message": text,
            }
        )
    return _deduplicate_reasons(rows)[:3]


def build_backtest_analysis_decision_workspace(
    *,
    workspace_kind: str,
    selection: Mapping[str, Any],
    configuration: Mapping[str, Any],
    result_bundle: dict[str, Any] | None,
    result_configuration_fingerprint: str | None,
    saved_mixes: Sequence[Mapping[str, Any]],
    last_error: str | None,
    last_error_kind: str | None,
    action_handlers: Mapping[str, Callable[..., Any] | None],
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Build the Python-owned Level1 read model consumed by all UI surfaces."""

    fingerprint = build_level1_configuration_fingerprint(
        workspace_kind=workspace_kind,
        selection=selection,
        configuration=configuration,
    )
    strategy_choice = str(selection.get("strategy_choice") or "") or None
    readiness = build_level1_readiness_projection(
        workspace_kind=workspace_kind,
        strategy_choice=strategy_choice,
        result_bundle=result_bundle,
        current_configuration_fingerprint=fingerprint,
        result_configuration_fingerprint=result_configuration_fingerprint,
        action_handlers=action_handlers,
        component_bundles=component_bundles,
    )
    meta = dict((result_bundle or {}).get("meta") or {})
    phase = (
        "error"
        if last_error
        else "result"
        if result_bundle
        else "configuring"
        if selection
        else "selecting"
    )
    maturity = readiness["strategy_maturity"]
    if maturity == "development":
        headline = "개발 중이므로 현재 Level2로 보낼 수 없습니다"
    elif readiness["handoff_state"] == "ready":
        headline = "Level2 검증 후보로 보낼 수 있습니다"
    else:
        headline = "Level1에서 먼저 해결할 항목이 있습니다"

    error = None
    if last_error:
        error = {
            "kind": _ERROR_KIND_MAP.get(
                str(last_error_kind or ""), "execution_failed"
            ),
            "message": str(last_error),
        }
    current_work = {
        "title": strategy_choice
        or str(selection.get("mix_name") or "Portfolio Mix"),
        "workspace_kind": workspace_kind,
    }
    decision = {
        "headline": headline,
        "summary": (
            "성과만으로 판단하지 않고 실행·데이터·인계 준비 상태를 함께 확인합니다."
        ),
        "reasons": _plain_reasons(readiness),
        "metrics": _metric_items((result_bundle or {}).get("summary_df")),
        "result_available": readiness["result_available"],
    }
    workspace = {
        "schema_version": BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION,
        "workspace_id": fingerprint[:16],
        "workspace_kind": workspace_kind,
        "configuration_fingerprint": fingerprint,
        "run_result_id": meta.get("run_id"),
        "candidate_source_id": meta.get("selection_source_id"),
        "workspace_phase": phase,
        "result_freshness": readiness["result_freshness"],
        "handoff_state": readiness["handoff_state"],
        "strategy_maturity": maturity,
        "header": {
            "question": "이 전략 또는 조합을 Level2 검증 후보로 만들 수 있는가?"
        },
        "current_work": current_work,
        "strategy_catalog": build_level1_strategy_catalog(),
        "configuration_summary": _configuration_summary(
            workspace_kind,
            configuration,
        ),
        "saved_mixes": [_json_ready(dict(row)) for row in saved_mixes],
        "component_bundle_count": len(component_bundles),
        "decision": decision,
        "evaluation": readiness["evaluation"],
        "error": error,
        "actions": readiness["actions"],
        "details": {"technical_evidence": {"meta": _json_ready(meta)}},
        "boundaries": {
            "react_executes_backtest": False,
            "react_writes_history": False,
            "react_writes_saved_mix": False,
            "react_writes_candidate_source": False,
            "python_validates_intent": True,
        },
    }
    if workspace_kind == "portfolio_mix":
        strategy_names = [
            str(name) for name in list(configuration.get("strategy_names") or [])
        ]
        weights_percent = [
            float(weight)
            for weight in list(configuration.get("weights_percent") or [])
        ]
        component_roles = [
            str(role)
            for role in list(configuration.get("component_roles") or [])
        ]
        workspace["mix"] = {
            "role_weight_rows": build_mix_role_weight_rows(
                strategy_names=strategy_names,
                weights_percent=weights_percent,
                component_roles=component_roles,
            ),
            "total_weight_percent": round(sum(weights_percent), 4),
            "saved_entry_mode": str(selection.get("mix_mode") or "new"),
        }
    return workspace


__all__ = [
    "BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION",
    "build_backtest_analysis_decision_workspace",
    "build_level1_configuration_fingerprint",
    "build_level1_readiness_projection",
    "build_level1_strategy_catalog",
    "level1_strategy_maturity",
]
