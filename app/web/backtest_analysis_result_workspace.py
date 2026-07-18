from __future__ import annotations

from collections.abc import Mapping
from functools import partial
from typing import Any

import streamlit as st

from app.services.backtest_analysis_result_workspace import (
    build_backtest_analysis_result_workspace,
)
from app.web.backtest_analysis_result_workspace_panel import (
    render_backtest_analysis_result_workspace_fallback,
)
from app.web.backtest_analysis_workspace import (
    build_backtest_analysis_action_handlers,
)
from app.web.backtest_strategy_catalog import DEFAULT_SINGLE_STRATEGY_OPTION
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_ANALYSIS_MODE_SINGLE,
)
from app.web.components.backtest_analysis_result_workspace import (
    is_backtest_analysis_result_workspace_available,
    render_backtest_analysis_result_workspace_component,
)


_CONSUMED_NONCE_KEY = "backtest_analysis_result_consumed_nonce"


def _workspace_kind_from_state() -> str:
    mode = str(
        st.session_state.get(
            "backtest_analysis_mode",
            BACKTEST_ANALYSIS_MODE_SINGLE,
        )
    )
    return "portfolio_mix" if mode == BACKTEST_ANALYSIS_MODE_COMPARE else "single_strategy"


def build_current_backtest_analysis_result_workspace(
    *,
    is_running: bool = False,
) -> dict[str, Any]:
    """Adapt current Streamlit state to the pure Level1 result read model."""

    workspace_kind = _workspace_kind_from_state()
    if workspace_kind == "single_strategy":
        strategy_choice: str | None = str(
            st.session_state.get(
                "backtest_strategy_choice",
                DEFAULT_SINGLE_STRATEGY_OPTION,
            )
        )
        result_bundle = st.session_state.get("backtest_last_bundle")
        result_meta = dict((result_bundle or {}).get("meta") or {})
        result_fingerprint = st.session_state.get(
            "backtest_last_configuration_fingerprint"
        ) or result_meta.get("level1_configuration_fingerprint")
        current_fingerprint = st.session_state.get(
            "backtest_current_configuration_fingerprint"
        ) or result_fingerprint
        result_requires_rerun = bool(
            st.session_state.get("backtest_last_result_requires_rerun")
        )
        last_error = st.session_state.get("backtest_last_error")
        last_error_kind = st.session_state.get("backtest_last_error_kind")
        component_bundles: list[dict[str, Any]] = []
        pending = st.session_state.get("backtest_pending_single_run")
    else:
        strategy_choice = None
        result_bundle = st.session_state.get("backtest_weighted_bundle")
        result_meta = dict((result_bundle or {}).get("meta") or {})
        result_fingerprint = st.session_state.get(
            "backtest_last_mix_configuration_fingerprint"
        ) or result_meta.get("level1_configuration_fingerprint")
        current_fingerprint = st.session_state.get(
            "backtest_current_mix_configuration_fingerprint"
        ) or result_fingerprint
        result_requires_rerun = bool(
            result_bundle
            and current_fingerprint
            and result_fingerprint
            and str(current_fingerprint) != str(result_fingerprint)
        )
        last_error = st.session_state.get("backtest_weighted_error") or st.session_state.get(
            "backtest_compare_error"
        )
        last_error_kind = st.session_state.get("backtest_compare_error_kind")
        component_bundles = list(
            st.session_state.get("backtest_compare_bundles") or []
        )
        pending = st.session_state.get("backtest_pending_weighted_run")

    action_handlers = build_backtest_analysis_action_handlers(
        workspace_kind=workspace_kind,
    )
    return build_backtest_analysis_result_workspace(
        workspace_kind=workspace_kind,
        strategy_choice=strategy_choice,
        result_bundle=result_bundle if isinstance(result_bundle, Mapping) else None,
        current_configuration_fingerprint=str(current_fingerprint or ""),
        result_configuration_fingerprint=(
            str(result_fingerprint) if result_fingerprint else None
        ),
        result_requires_rerun=result_requires_rerun,
        is_running=bool(is_running or pending),
        last_error=str(last_error) if last_error else None,
        last_error_kind=str(last_error_kind) if last_error_kind else None,
        action_handlers=action_handlers,
        component_bundles=component_bundles,
    )


def validate_result_workspace_intent(
    intent: object,
    *,
    workspace: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate identity and action state without trusting component flags."""

    if not isinstance(intent, Mapping):
        return {"ok": False, "reason": "invalid_intent"}
    action = str(intent.get("action") or "")
    nonce = str(intent.get("nonce") or "")
    if action != "save_and_move" or not nonce:
        return {"ok": False, "reason": "invalid_intent"}
    action_state = dict(dict(workspace.get("actions") or {}).get(action) or {})
    if not action_state.get("enabled"):
        return {"ok": False, "reason": "action_unavailable"}
    payload = intent.get("payload")
    if not isinstance(payload, Mapping):
        return {"ok": False, "reason": "invalid_payload"}
    identity = dict(workspace.get("identity") or {})
    expected_run_id = str(identity.get("run_result_id") or "")
    requested_run_id = str(payload.get("run_result_id") or "")
    if not expected_run_id or requested_run_id != expected_run_id:
        return {"ok": False, "reason": "run_identity_mismatch"}
    expected_fingerprint = str(
        workspace.get("configuration_fingerprint") or ""
    )
    requested_fingerprint = str(
        payload.get("current_configuration_fingerprint") or ""
    )
    if not expected_fingerprint or requested_fingerprint != expected_fingerprint:
        return {"ok": False, "reason": "configuration_mismatch"}
    return {
        "ok": True,
        "action": action,
        "nonce": nonce,
        "payload": dict(payload),
    }


def consume_result_workspace_intent(
    intent: object,
    *,
    workspace: Mapping[str, Any],
) -> dict[str, Any]:
    """Revalidate one current-result intent and dispatch a Python handler."""

    validation = validate_result_workspace_intent(intent, workspace=workspace)
    if not validation.get("ok"):
        return validation
    nonce = str(validation["nonce"])
    if nonce == str(st.session_state.get(_CONSUMED_NONCE_KEY) or ""):
        return {"ok": False, "reason": "duplicate_intent"}
    workspace_kind = _workspace_kind_from_state()
    handlers = build_backtest_analysis_action_handlers(
        workspace_kind=workspace_kind,
    )
    handler = handlers.get(str(validation["action"]))
    if not callable(handler):
        return {"ok": False, "reason": "handler_unavailable"}
    result = handler(dict(validation["payload"]))
    st.session_state[_CONSUMED_NONCE_KEY] = nonce
    return {"ok": True, "handler_result": result}


def _consume_result_workspace_component_change(
    *,
    component_key: str,
    is_running: bool,
) -> None:
    intent = st.session_state.get(component_key)
    workspace = build_current_backtest_analysis_result_workspace(
        is_running=is_running,
    )
    consumed = consume_result_workspace_intent(intent, workspace=workspace)
    if consumed.get("ok"):
        st.rerun(scope="app")


def render_backtest_analysis_result_workspace(
    *,
    is_running: bool = False,
) -> None:
    """Render the result component or the same-read-model Python fallback."""

    workspace = build_current_backtest_analysis_result_workspace(
        is_running=is_running,
    )
    if not workspace.get("visible"):
        if is_running:
            st.info("첫 백테스트 결과를 만드는 중입니다.")
        return

    identity = dict(workspace.get("identity") or {})
    component_key = (
        "backtest-analysis-result-workspace-"
        f"{identity.get('run_result_id') or str(workspace.get('configuration_fingerprint') or '')[:16] or 'current'}"
    )
    intent: dict[str, Any] | None = None
    if is_backtest_analysis_result_workspace_available():
        try:
            intent = render_backtest_analysis_result_workspace_component(
                workspace=workspace,
                key=component_key,
                on_change=partial(
                    _consume_result_workspace_component_change,
                    component_key=component_key,
                    is_running=is_running,
                ),
            )
        except Exception as exc:  # component availability must not hide results
            st.warning(
                "React 결과 화면을 열지 못해 같은 결과 계약의 기본 화면으로 전환했습니다. "
                f"({exc})"
            )
            intent = render_backtest_analysis_result_workspace_fallback(workspace)
    else:
        intent = render_backtest_analysis_result_workspace_fallback(workspace)

    consumed = consume_result_workspace_intent(intent, workspace=workspace)
    if consumed.get("ok"):
        st.rerun(scope="app")


__all__ = [
    "build_current_backtest_analysis_result_workspace",
    "consume_result_workspace_intent",
    "render_backtest_analysis_result_workspace",
    "validate_result_workspace_intent",
]
