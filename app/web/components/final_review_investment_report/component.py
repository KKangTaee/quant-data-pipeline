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


def is_final_review_decision_workspace_available() -> bool:
    return _component is not None


def render_final_review_decision_workspace(
    *,
    decision_brief: dict[str, Any],
    candidate_selector: dict[str, Any],
    key: str | None = None,
) -> dict[str, Any] | None:
    """Render one candidate-to-decision workspace and return presentation intent.

    React displays Python-owned projections and emits candidate or route/reason
    intent only. Python keeps eligibility, calculations, validation, and writes.
    """
    if _component is None:
        return None
    value = _component(
        decision_brief=decision_brief,
        candidate_selector=candidate_selector,
        key=key,
        default=None,
    )
    return value if isinstance(value, dict) else None
