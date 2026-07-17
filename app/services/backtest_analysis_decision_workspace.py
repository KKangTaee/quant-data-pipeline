from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    LEVEL1_STRATEGY_PURPOSE_GROUPS,
    STRATEGY_FAMILY_VARIANTS,
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


__all__ = [
    "BACKTEST_ANALYSIS_DECISION_WORKSPACE_SCHEMA_VERSION",
    "build_level1_configuration_fingerprint",
    "build_level1_strategy_catalog",
    "level1_strategy_maturity",
]
