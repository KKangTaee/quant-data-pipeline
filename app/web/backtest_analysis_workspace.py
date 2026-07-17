from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from app.runtime import load_saved_portfolios
from app.services.backtest_analysis_decision_workspace import (
    build_backtest_analysis_decision_workspace,
    build_level1_configuration_fingerprint,
)
from app.services.backtest_single_payload import normalize_single_strategy_payload
from app.web.backtest_strategy_catalog import (
    DEFAULT_SINGLE_STRATEGY_OPTION,
    SINGLE_STRATEGY_OPTIONS,
)
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_ANALYSIS_MODE_SINGLE,
)


_CONTEXT_ACTIONS = {"select_workspace_kind", "select_strategy"}
_DECISION_ACTIONS = {"save_and_move"}


def _workspace_kind_from_mode(mode: str | None) -> str:
    if mode == BACKTEST_ANALYSIS_MODE_COMPARE:
        return "portfolio_mix"
    return "single_strategy"


def record_single_strategy_draft(payload: dict, *, strategy_name: str) -> str:
    """Normalize and identify the latest Python-owned Single Strategy draft."""

    normalized = normalize_single_strategy_payload(
        payload,
        strategy_name=strategy_name,
    )
    selection = {
        "strategy_choice": st.session_state.get("backtest_strategy_choice"),
        "strategy_name": strategy_name,
    }
    fingerprint = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection=selection,
        configuration=normalized,
    )
    st.session_state.backtest_current_draft_payload = normalized
    st.session_state.backtest_current_configuration_fingerprint = fingerprint
    return fingerprint


def _saved_mix_summaries() -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for row in load_saved_portfolios(limit=20):
        portfolio_context = dict(row.get("portfolio_context") or {})
        summaries.append(
            {
                "portfolio_id": row.get("portfolio_id"),
                "name": row.get("name"),
                "description": row.get("description"),
                "updated_at": row.get("updated_at") or row.get("saved_at"),
                "strategy_names": list(
                    portfolio_context.get("strategy_names") or []
                ),
                "weights_percent": list(
                    portfolio_context.get("weights_percent") or []
                ),
                "component_roles": list(
                    portfolio_context.get("component_roles") or []
                ),
            }
        )
    return summaries


def build_current_backtest_analysis_workspace() -> dict[str, Any]:
    """Adapt current Streamlit state to the pure Level1 read model."""

    mode = str(
        st.session_state.get(
            "backtest_analysis_mode",
            BACKTEST_ANALYSIS_MODE_SINGLE,
        )
    )
    workspace_kind = _workspace_kind_from_mode(mode)
    if workspace_kind == "single_strategy":
        strategy_choice = str(
            st.session_state.get(
                "backtest_strategy_choice",
                DEFAULT_SINGLE_STRATEGY_OPTION,
            )
        )
        selection = {"strategy_choice": strategy_choice}
        configuration = dict(
            st.session_state.get("backtest_current_draft_payload") or {}
        )
        result_bundle = st.session_state.get("backtest_last_bundle")
        result_fingerprint = st.session_state.get(
            "backtest_last_configuration_fingerprint"
        ) or dict((result_bundle or {}).get("meta") or {}).get(
            "level1_configuration_fingerprint"
        )
        last_error = st.session_state.get("backtest_last_error")
        last_error_kind = st.session_state.get("backtest_last_error_kind")
        component_bundles: list[dict[str, Any]] = []
    else:
        weighted_bundle = st.session_state.get("backtest_weighted_bundle")
        bundles = list(st.session_state.get("backtest_compare_bundles") or [])
        selection = {
            "mix_name": dict(weighted_bundle or {}).get("strategy_name")
            or "Portfolio Mix",
            "mix_mode": st.session_state.get(
                "backtest_compare_workspace_mode",
                "전략 비교",
            ),
        }
        configuration = dict(
            st.session_state.get("backtest_current_mix_configuration") or {}
        )
        result_bundle = weighted_bundle
        result_fingerprint = st.session_state.get(
            "backtest_last_mix_configuration_fingerprint"
        ) or dict((weighted_bundle or {}).get("meta") or {}).get(
            "level1_configuration_fingerprint"
        )
        last_error = st.session_state.get("backtest_weighted_error") or st.session_state.get(
            "backtest_compare_error"
        )
        last_error_kind = st.session_state.get("backtest_compare_error_kind")
        component_bundles = bundles

    return build_backtest_analysis_decision_workspace(
        workspace_kind=workspace_kind,
        selection=selection,
        configuration=configuration,
        result_bundle=result_bundle,
        result_configuration_fingerprint=(
            str(result_fingerprint) if result_fingerprint else None
        ),
        saved_mixes=_saved_mix_summaries(),
        last_error=str(last_error) if last_error else None,
        last_error_kind=str(last_error_kind) if last_error_kind else None,
        action_handlers={},
        component_bundles=component_bundles,
    )


def _new_component_intent(
    intent: dict[str, Any] | None,
    *,
    consumed_nonce: str | None,
) -> bool:
    nonce = str(dict(intent or {}).get("nonce") or "")
    return bool(nonce and nonce != consumed_nonce)


def consume_backtest_analysis_intent(
    intent: dict[str, Any] | None,
    *,
    allowed_actions: set[str] | None = None,
) -> None:
    """Validate a presentation intent before changing Python-owned state."""

    consumed_nonce = st.session_state.get("backtest_analysis_consumed_nonce")
    if not _new_component_intent(intent, consumed_nonce=consumed_nonce):
        return
    payload = dict(intent or {})
    action = str(payload.get("action") or "")
    if allowed_actions is not None and action not in allowed_actions:
        return
    nonce = str(payload.get("nonce") or "")
    action_payload = dict(payload.get("payload") or {})

    if action == "select_workspace_kind":
        workspace_kind = str(action_payload.get("workspace_kind") or "")
        if workspace_kind == "portfolio_mix":
            st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_COMPARE
        elif workspace_kind == "single_strategy":
            st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE
        else:
            return
    elif action == "select_strategy":
        strategy_choice = str(action_payload.get("strategy_choice") or "")
        if strategy_choice not in SINGLE_STRATEGY_OPTIONS:
            return
        st.session_state.backtest_strategy_choice = strategy_choice
    else:
        return

    st.session_state.backtest_analysis_consumed_nonce = nonce
    st.rerun(scope="app")


def consume_backtest_analysis_component_change(
    *,
    component_key: str,
    allowed_actions: set[str],
) -> None:
    intent = st.session_state.get(component_key)
    consume_backtest_analysis_intent(
        intent if isinstance(intent, dict) else None,
        allowed_actions=allowed_actions,
    )


__all__ = [
    "_CONTEXT_ACTIONS",
    "_DECISION_ACTIONS",
    "build_current_backtest_analysis_workspace",
    "consume_backtest_analysis_component_change",
    "consume_backtest_analysis_intent",
    "record_single_strategy_draft",
]
