from __future__ import annotations

from collections.abc import Callable, MutableMapping
from functools import partial
from typing import Any

import streamlit as st

from app.services.backtest_workflow_shell import (
    build_backtest_workflow_shell,
    resolve_backtest_workflow_shell_intent,
)
from app.web.backtest_state import request_backtest_panel
from app.web.backtest_workflow_shell_panel import (
    render_backtest_workflow_shell_fallback,
)
from app.web.components.backtest_workflow_shell import (
    is_backtest_workflow_shell_available,
    render_backtest_workflow_shell_component,
)


_COMPONENT_KEY = "backtest-workflow-shell"


def apply_backtest_workflow_shell_intent(
    intent: dict[str, Any] | None,
    *,
    session_state: MutableMapping[str, Any],
    request_handler: Callable[[str], None],
) -> bool:
    """Validate one presentation intent before requesting a Python-owned route."""

    resolution = resolve_backtest_workflow_shell_intent(
        intent,
        active_stage=str(session_state.get("backtest_active_panel") or ""),
        consumed_nonce=(
            str(session_state.get("backtest_workflow_shell_consumed_nonce") or "")
            or None
        ),
    )
    if not resolution.get("accepted"):
        return False
    request_handler(str(resolution["stage_key"]))
    session_state["backtest_workflow_shell_consumed_nonce"] = str(
        resolution["nonce"]
    )
    return True


def build_current_backtest_workflow_shell() -> dict[str, Any]:
    """Adapt the active Streamlit stage to the pure shell read model."""

    return build_backtest_workflow_shell(
        str(st.session_state.get("backtest_active_panel") or "")
    )


def consume_backtest_workflow_shell_intent(
    intent: dict[str, Any] | None,
    *,
    rerun_scope: str = "app",
) -> bool:
    accepted = apply_backtest_workflow_shell_intent(
        intent,
        session_state=st.session_state,
        request_handler=request_backtest_panel,
    )
    if accepted and rerun_scope != "none":
        st.rerun(scope="app")
    return accepted


def _consume_backtest_workflow_shell_component_change(
    *,
    component_key: str,
) -> None:
    value = st.session_state.get(component_key)
    consume_backtest_workflow_shell_intent(
        value if isinstance(value, dict) else None,
        rerun_scope="none",
    )


def render_backtest_workflow_shell() -> str:
    """Render the common page shell and return the normalized active stage."""

    shell = build_current_backtest_workflow_shell()
    if is_backtest_workflow_shell_available():
        intent = render_backtest_workflow_shell_component(
            shell=shell,
            key=_COMPONENT_KEY,
            on_change=partial(
                _consume_backtest_workflow_shell_component_change,
                component_key=_COMPONENT_KEY,
            ),
        )
    else:
        intent = render_backtest_workflow_shell_fallback(shell)
    consume_backtest_workflow_shell_intent(intent)
    return str(shell["active_stage"])


__all__ = [
    "apply_backtest_workflow_shell_intent",
    "build_current_backtest_workflow_shell",
    "consume_backtest_workflow_shell_intent",
    "render_backtest_workflow_shell",
]
