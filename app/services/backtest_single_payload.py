from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _json_ready_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready_value(item) for item in value]
    if isinstance(value, list):
        return [_json_ready_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready_value(item) for key, item in value.items()}
    return value


def normalize_single_strategy_payload(payload: Mapping[str, Any], *, strategy_name: str) -> dict[str, Any]:
    """Build the service-facing Single Strategy payload from a UI form payload."""

    normalized = {key: _json_ready_value(value) for key, value in dict(payload or {}).items()}
    normalized["strategy_name"] = strategy_name
    return normalized
