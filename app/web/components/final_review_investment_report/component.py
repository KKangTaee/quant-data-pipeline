from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_NAME = "final_review_investment_report"
_FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

_component = (
    components.declare_component(_COMPONENT_NAME, path=str(_FRONTEND_BUILD_DIR))
    if _FRONTEND_BUILD_DIR.exists()
    else None
)


def is_final_review_investment_report_available() -> bool:
    return _component is not None


def render_final_review_investment_report(
    *,
    report: dict[str, Any],
    decision_action: dict[str, Any] | None = None,
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render the optional Final Review report and return decision intent.

    React displays the report and collects route / reason intent only. Python
    keeps ownership of scoring, save validation, persistence, and Monitoring
    handoff boundaries.
    """
    if _component is None:
        return None
    value = _component(
        report=report,
        decision_action=dict(decision_action or {}),
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
