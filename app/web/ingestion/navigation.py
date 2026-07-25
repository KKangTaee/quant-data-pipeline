"""Navigation and focus state for the Data Operations page."""

from __future__ import annotations

from collections.abc import MutableMapping

import streamlit as st

from app.web.ingestion.workflows import (
    DATA_OPERATIONS_SECTION_ADVANCED,
    DATA_OPERATIONS_SECTION_PREPARATION,
    DATA_OPERATIONS_SECTIONS,
    action_definition,
    workflow_for_id,
)


SECTION_STATE_KEY = "data_operations_section_choice"
WORKFLOW_STATE_KEY = "data_operations_workflow_choice"
FOCUSED_ACTION_STATE_KEY = "data_operations_focused_action"


def apply_action_focus(
    state: MutableMapping[str, object],
    action: str,
) -> None:
    """Move navigation to Advanced only after validating an active action."""

    action_definition(action)
    state[SECTION_STATE_KEY] = DATA_OPERATIONS_SECTION_ADVANCED
    state[FOCUSED_ACTION_STATE_KEY] = action


def select_data_operations_section() -> str:
    """Render and persist the five-section Data Operations selector."""

    selected = st.pills(
        "Data Operations 구분",
        options=list(DATA_OPERATIONS_SECTIONS),
        default=DATA_OPERATIONS_SECTION_PREPARATION,
        key=SECTION_STATE_KEY,
        label_visibility="collapsed",
    )
    if selected not in DATA_OPERATIONS_SECTIONS:
        selected = DATA_OPERATIONS_SECTION_PREPARATION
        st.session_state[SECTION_STATE_KEY] = selected
    return str(selected)


def select_data_operations_workflow(workflow_id: str) -> None:
    """Persist one known consumer workflow selection."""

    workflow_for_id(workflow_id)
    st.session_state[WORKFLOW_STATE_KEY] = workflow_id


def clear_data_operations_workflow() -> None:
    st.session_state[WORKFLOW_STATE_KEY] = None


def selected_data_operations_workflow() -> str | None:
    value = st.session_state.get(WORKFLOW_STATE_KEY)
    if not value:
        return None
    try:
        workflow_for_id(str(value))
    except KeyError:
        st.session_state[WORKFLOW_STATE_KEY] = None
        return None
    return str(value)


def focus_data_operations_action(action: str) -> None:
    """Focus an action in Advanced and rerun from the top-level selector."""

    apply_action_focus(st.session_state, action)
    st.rerun()


def consume_focused_data_operations_action() -> str | None:
    """Return the current focus while clearing invalid or inactive values."""

    value = st.session_state.get(FOCUSED_ACTION_STATE_KEY)
    if not value:
        return None
    try:
        action_definition(str(value))
    except KeyError:
        st.session_state[FOCUSED_ACTION_STATE_KEY] = None
        return None
    return str(value)


__all__ = [
    "FOCUSED_ACTION_STATE_KEY",
    "SECTION_STATE_KEY",
    "WORKFLOW_STATE_KEY",
    "apply_action_focus",
    "clear_data_operations_workflow",
    "consume_focused_data_operations_action",
    "focus_data_operations_action",
    "select_data_operations_section",
    "select_data_operations_workflow",
    "selected_data_operations_workflow",
]
