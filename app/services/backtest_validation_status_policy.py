from __future__ import annotations

from typing import Any


BLOCKING_STATUSES = {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}
REVIEW_STATUSES = {"REVIEW"}
PASS_STATUSES = {"PASS", "READY"}
STATUS_RANK = {
    "BLOCKED": 60,
    "NEEDS_INPUT": 50,
    "NOT_RUN": 40,
    "REVIEW": 30,
    "PASS": 20,
    "READY": 20,
    "INFO": 10,
    "NOT_APPLICABLE": 0,
}


def normalize_validation_status(value: Any) -> str:
    normalized = str(value or "NOT_RUN").strip().upper()
    if normalized in {"TRUE"}:
        return "PASS"
    if normalized in {"FALSE"}:
        return "NEEDS_INPUT"
    return normalized if normalized in STATUS_RANK else "NOT_RUN"


def worst_validation_status(values: list[Any], *, default: str = "NOT_RUN") -> str:
    statuses = [normalize_validation_status(value) for value in values if value is not None]
    if not statuses:
        return default
    return max(statuses, key=lambda item: STATUS_RANK.get(item, STATUS_RANK["NOT_RUN"]))
