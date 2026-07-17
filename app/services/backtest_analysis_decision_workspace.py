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
from app.services.backtest_handoff_readiness import (
    build_handoff_gate_summary,
    build_next_step_readiness_evaluation,
)


BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION = (
    "backtest_analysis_decision_workspace_v1"
)


def _json_ready(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


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
) -> dict[str, Any]:
    """Project existing handoff truth together with result freshness and handlers."""

    result_available = bool(result_bundle)
    if not result_available:
        freshness = "none"
    elif current_configuration_fingerprint == result_configuration_fingerprint:
        freshness = "current"
    else:
        freshness = "stale"

    maturity = (
        level1_strategy_maturity(strategy_choice)
        if workspace_kind == "single_strategy"
        else "production"
    )
    meta = dict((result_bundle or {}).get("meta") or {})
    evaluation = (
        build_next_step_readiness_evaluation(meta) if result_available else {}
    )
    can_enter = bool(evaluation.get("can_enter_practical_validation"))
    handoff_state = (
        "ready"
        if (
            result_available
            and freshness == "current"
            and maturity == "production"
            and can_enter
        )
        else "blocked"
    )

    actions: dict[str, dict[str, Any]] = {}
    if handoff_state == "ready" and callable(action_handlers.get("save_and_move")):
        actions["save_and_move"] = {
            "id": "save_and_move",
            "label": "후보로 저장하고 Level2로 이동",
            "enabled": True,
        }

    return {
        "result_available": result_available,
        "result_freshness": freshness,
        "strategy_maturity": maturity,
        "handoff_state": handoff_state,
        "actions": actions,
        "evaluation": evaluation,
        "gate_summary": (
            build_handoff_gate_summary(meta) if result_available else {}
        ),
    }


__all__ = [
    "BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION",
    "build_level1_configuration_fingerprint",
    "build_level1_readiness_projection",
    "build_level1_strategy_catalog",
    "level1_strategy_maturity",
]
