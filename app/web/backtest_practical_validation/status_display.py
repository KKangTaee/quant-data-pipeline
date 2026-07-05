from __future__ import annotations

from typing import Any


def validation_status_label(status: Any) -> str:
    status_text = str(status or "").strip().upper()
    if not status_text:
        return "-"
    if status_text in {"PASS", "READY", "READY_FOR_FINAL_REVIEW"}:
        return "PASS"
    if "BLOCKED" in status_text:
        return "BLOCKED"
    if status_text in {"REVIEW", "NEEDS_INPUT", "NOT_RUN", "NOT_APPLICABLE"}:
        return status_text
    if status_text in {"READY_WITH_REVIEW", "REVIEW_REQUIRED"}:
        return "REVIEW"
    return status_text


def validation_status_tone(status: Any) -> str:
    label = validation_status_label(status)
    if label == "PASS":
        return "positive"
    if label == "BLOCKED":
        return "danger"
    if label in {"REVIEW", "NEEDS_INPUT"}:
        return "warning"
    return "neutral"
