from __future__ import annotations

from typing import Any

import streamlit as st

from app.services.backtest_practical_validation import prepare_practical_validation_source_handoff
from app.services.backtest_practical_validation_source import (
    build_selection_source_from_history_record,
    build_selection_source_from_result_bundle,
)


def apply_practical_validation_source_handoff(source: dict[str, Any]):
    """Queue a current selection source for the Practical Validation workspace."""

    handoff = prepare_practical_validation_source_handoff(source, persist=True)
    st.session_state.backtest_practical_validation_source = handoff.source_payload
    st.session_state.backtest_practical_validation_notice = handoff.notice
    st.session_state.backtest_practical_validation_mode = handoff.mode
    st.session_state.backtest_requested_panel = handoff.requested_panel
    return handoff


def queue_practical_validation_handoff_from_result_bundle(
    bundle: dict[str, Any],
    *,
    source_kind: str = "latest_backtest_run",
    extra_fields: dict[str, Any] | None = None,
):
    source = build_selection_source_from_result_bundle(
        bundle,
        source_kind=source_kind,
        extra_fields=extra_fields,
    )
    return apply_practical_validation_source_handoff(source)


def queue_practical_validation_handoff_from_history_record(record: dict[str, Any]):
    source = build_selection_source_from_history_record(record)
    return apply_practical_validation_source_handoff(source)
