from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import streamlit as st

from app.services.backtest_analysis_result_workspace import (
    build_backtest_analysis_result_workspace,
)
from app.services.backtest_level1_price_freshness import (
    build_level1_price_freshness_action,
    build_level1_price_refresh_meta,
)
from app.services.backtest_price_refresh import (
    build_backtest_price_refresh_plan,
    price_refresh_result_requires_backtest_rerun,
    run_backtest_price_refresh,
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
_SUPPORTED_ACTIONS = frozenset(
    {"save_and_move", "refresh_prices", "rerun_same_configuration"}
)


def _workspace_kind_from_state() -> str:
    mode = str(
        st.session_state.get(
            "backtest_analysis_mode",
            BACKTEST_ANALYSIS_MODE_SINGLE,
        )
    )
    return "portfolio_mix" if mode == BACKTEST_ANALYSIS_MODE_COMPARE else "single_strategy"


def _current_single_price_refresh_context() -> dict[str, Any] | None:
    """Rebuild the current refresh input and plan from Python-owned session state."""

    result_bundle = st.session_state.get("backtest_last_bundle")
    if not isinstance(result_bundle, Mapping):
        return None
    configuration = st.session_state.get("backtest_current_draft_payload")
    refresh_meta = build_level1_price_refresh_meta(
        result_bundle=result_bundle,
        configuration=(
            configuration if isinstance(configuration, Mapping) else None
        ),
    )
    raw_plan = build_backtest_price_refresh_plan(refresh_meta)
    plan = {
        **raw_plan,
        "requested_end": refresh_meta.get("end"),
    }
    return {"meta": refresh_meta, "plan": plan}


def _run_current_single_price_refresh(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Run only the eligible OHLCV refresh and keep the old result as reference."""

    del payload
    context = _current_single_price_refresh_context()
    if not context or not dict(context.get("plan") or {}).get("eligible"):
        return {"accepted": False, "reason": "refresh_unavailable"}
    result = dict(run_backtest_price_refresh(dict(context["meta"])))
    st.session_state["backtest_last_result_refresh_result"] = result
    if price_refresh_result_requires_backtest_rerun(result):
        st.session_state["backtest_last_result_requires_rerun"] = True
    return {"accepted": True, "result": result}


def _queue_current_single_rerun(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Queue the current Python-owned draft without collecting or auto-running here."""

    del payload
    draft = st.session_state.get("backtest_current_draft_payload")
    if not isinstance(draft, Mapping):
        return {"accepted": False, "reason": "draft_unavailable"}
    strategy_name = str(
        st.session_state.get(
            "backtest_strategy_choice",
            DEFAULT_SINGLE_STRATEGY_OPTION,
        )
    )
    st.session_state["backtest_pending_single_run"] = {
        "payload": dict(draft),
        "strategy_name": strategy_name,
    }
    return {"accepted": True, "action": "rerun_same_configuration"}


def _build_result_workspace_action_handlers(
    *, workspace_kind: str
) -> dict[str, Any]:
    handlers = dict(
        build_backtest_analysis_action_handlers(workspace_kind=workspace_kind)
    )
    if workspace_kind == "single_strategy":
        handlers.update(
            {
                "refresh_prices": _run_current_single_price_refresh,
                "rerun_same_configuration": _queue_current_single_rerun,
            }
        )
    return handlers


def build_current_backtest_analysis_result_workspace(
    *,
    is_running: bool = False,
) -> dict[str, Any]:
    """Adapt current Streamlit state to the pure Level1 result read model."""

    workspace_kind = _workspace_kind_from_state()
    price_freshness_action: dict[str, Any] | None = None
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
        refresh_result = st.session_state.get(
            "backtest_last_result_refresh_result"
        )
        reference_reason = (
            "price_refresh"
            if result_requires_rerun and isinstance(refresh_result, Mapping)
            else None
        )
        last_error = st.session_state.get("backtest_last_error")
        last_error_kind = st.session_state.get("backtest_last_error_kind")
        component_bundles: list[dict[str, Any]] = []
        pending = st.session_state.get("backtest_pending_single_run")
        refresh_context = _current_single_price_refresh_context()
        if refresh_context:
            price_freshness_action = build_level1_price_freshness_action(
                plan=dict(refresh_context["plan"]),
                refresh_result=(
                    refresh_result if isinstance(refresh_result, Mapping) else None
                ),
                result_requires_rerun=result_requires_rerun,
            )
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
        reference_reason = None

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
        price_freshness_action=price_freshness_action,
        component_bundles=component_bundles,
        reference_reason=reference_reason,
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
    if action not in _SUPPORTED_ACTIONS or not nonce:
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
    handlers = _build_result_workspace_action_handlers(workspace_kind=workspace_kind)
    handler = handlers.get(str(validation["action"]))
    if not callable(handler):
        return {"ok": False, "reason": "handler_unavailable"}
    result = handler(dict(validation["payload"]))
    if isinstance(result, Mapping) and result.get("accepted") is False:
        return {
            "ok": False,
            "reason": str(result.get("reason") or "action_rejected"),
        }
    st.session_state[_CONSUMED_NONCE_KEY] = nonce
    return {"ok": True, "handler_result": result}


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
