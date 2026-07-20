from __future__ import annotations

from app.services.reference_center import (
    get_reference_item,
    validate_reference_destination,
)


BACKTEST_DESTINATION_PANELS = {
    "backtest_analysis": "Backtest Analysis",
    "practical_validation": "Practical Validation",
    "final_review": "Final Review",
}

REFERENCE_PAGE_TARGET_KEYS = {
    "overview",
    "institutional_portfolios",
    "ingestion",
    "backtest",
    "portfolio_monitoring",
}

_REFERENCE_PAGE_TARGETS: dict[str, object] = {}


def normalize_reference_event(value: object) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    event = value.get("event")
    if not isinstance(event, dict) or event.get("id") != "navigate_to_surface":
        return None

    destination = validate_reference_destination(event.get("destination"))
    item_id = str(event.get("item_id") or "").strip()
    if destination is None or get_reference_item(item_id) is None:
        return None

    return {
        "id": "navigate_to_surface",
        "destination": destination,
        "item_id": item_id,
        "nonce": str(event.get("nonce") or "").strip(),
    }


def resolve_reference_navigation(destination: object) -> dict[str, str] | None:
    normalized_destination = validate_reference_destination(destination)
    if normalized_destination is None:
        return None
    panel = BACKTEST_DESTINATION_PANELS.get(normalized_destination)
    if panel is not None:
        return {"page_target_key": "backtest", "panel": panel}
    return {"page_target_key": normalized_destination, "panel": ""}


def configure_reference_center_page_targets(page_targets: dict[str, object]) -> None:
    _REFERENCE_PAGE_TARGETS.clear()
    _REFERENCE_PAGE_TARGETS.update(
        {
            key: value
            for key, value in dict(page_targets or {}).items()
            if key in REFERENCE_PAGE_TARGET_KEYS and value is not None
        }
    )
