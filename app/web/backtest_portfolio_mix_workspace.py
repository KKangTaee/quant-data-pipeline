"""Streamlit adapter for the Python-owned Portfolio Mix one-shell workspace."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from functools import partial
from typing import Any, Mapping, MutableMapping

import streamlit as st

from app.services.backtest_portfolio_mix_workspace import (
    MIX_ROLE_OPTIONS,
    build_portfolio_mix_workspace,
    normalize_portfolio_mix_draft,
)
from app.services.backtest_single_settings_workspace import (
    apply_single_settings_preset,
    build_single_settings_workspace,
)
from app.services.backtest_strategy_catalog import (
    SINGLE_STRATEGY_OPTIONS,
    STRATEGY_FAMILY_VARIANTS,
)
from app.web.backtest_single_settings_workspace import (
    build_single_settings_runtime_options,
)
from app.web.components.backtest_portfolio_mix_workspace import (
    is_backtest_portfolio_mix_workspace_available,
    render_backtest_portfolio_mix_workspace_component,
)


MIX_SESSION_KEYS = {
    "draft": "backtest_portfolio_mix_draft",
    "mode": "backtest_portfolio_mix_mode",
    "component_states": "backtest_portfolio_mix_component_states",
    "current_result": "backtest_portfolio_mix_current_result",
    "last_result": "backtest_portfolio_mix_last_result",
    "last_intent_id": "backtest_portfolio_mix_last_intent_id",
}
_COMPONENT_KEY = "backtest-portfolio-mix-workspace"
_EDIT_ACTIONS = frozenset(
    {
        "set_mode",
        "add_component",
        "remove_component",
        "set_strategy",
        "set_variant",
        "apply_preset",
        "set_component_field",
        "set_shared_field",
        "set_role",
        "set_weight",
    }
)
_DEFERRED_ACTIONS = frozenset(
    {"restore_saved_mix", "run_saved_mix", "run_mix", "save_mix", "handoff_level2"}
)
_SHARED_FIELDS = frozenset({"start", "end", "timeframe", "option", "date_policy"})


def build_initial_portfolio_mix_session_draft(
    *, today: date | None = None
) -> dict[str, Any]:
    """Create a valid two-component starting point without running a backtest."""

    return normalize_portfolio_mix_draft(
        {
            "draft_id": "mix-draft-new",
            "source_saved_portfolio_id": None,
            "shared": {
                "start": "2016-01-01",
                "end": (today or date.today()).isoformat(),
                "timeframe": "1d",
                "option": "month_end",
                "date_policy": "intersection",
            },
            "components": [
                {
                    "component_id": "component-gtaa",
                    "strategy_choice": "GTAA",
                    "variant": None,
                    "settings_values": {},
                    "role": "core",
                    "weight_percent": 50.0,
                },
                {
                    "component_id": "component-equal-weight",
                    "strategy_choice": "Equal Weight",
                    "variant": None,
                    "settings_values": {},
                    "role": "defense",
                    "weight_percent": 50.0,
                },
            ],
        },
        today=today,
    )


def _event(intent: object) -> dict[str, Any]:
    if not isinstance(intent, Mapping):
        return {}
    event = intent.get("event")
    return dict(event) if isinstance(event, Mapping) else {}


def _component_index(draft: Mapping[str, Any], component_id: str) -> int | None:
    for index, component in enumerate(list(draft.get("components") or [])):
        if isinstance(component, Mapping) and str(component.get("component_id")) == component_id:
            return index
    return None


def _variant_allowed(strategy_choice: str, variant: object) -> bool:
    variants = STRATEGY_FAMILY_VARIANTS.get(strategy_choice)
    if not variants:
        return variant in (None, "")
    allowed = {
        "Annual" if name == "Strict Annual" else "Quarterly"
        if name == "Strict Quarterly"
        else name
        for name in variants
    }
    return str(variant or "") in allowed


def _component_settings_workspace(
    component: Mapping[str, Any],
    *,
    shared: Mapping[str, Any],
    runtime_options: Mapping[str, Any],
) -> dict[str, Any]:
    values = {
        **dict(component.get("settings_values") or {}),
        "start": shared.get("start"),
        "end": shared.get("end"),
    }
    return build_single_settings_workspace(
        str(component.get("strategy_choice") or ""),
        str(component.get("variant")) if component.get("variant") else None,
        values,
        runtime_options,
    )


def _allowed_component_field_ids(workspace: Mapping[str, Any]) -> set[str]:
    return {
        str(field.get("field_id"))
        for section in list(workspace.get("sections") or [])
        if isinstance(section, Mapping)
        for field in list(section.get("fields") or [])
        if isinstance(field, Mapping)
        and str(field.get("field_id") or "") not in {"start", "end"}
    }


def apply_portfolio_mix_intent(
    intent: object,
    *,
    session_state: MutableMapping[str, Any],
    runtime_options: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate one presentation intent and mutate only the addressed draft region."""

    event = _event(intent)
    action = str(event.get("id") or "")
    intent_id = str(event.get("intent_id") or "")
    payload = dict(event.get("payload") or {}) if isinstance(event.get("payload"), Mapping) else {}
    if action not in _EDIT_ACTIONS | _DEFERRED_ACTIONS:
        return {"accepted": False, "reason": "unknown_action"}
    if not intent_id:
        return {"accepted": False, "reason": "missing_intent_id"}
    if intent_id == str(session_state.get(MIX_SESSION_KEYS["last_intent_id"]) or ""):
        return {"accepted": False, "reason": "duplicate_intent"}
    if action in _DEFERRED_ACTIONS:
        return {"accepted": False, "reason": "handler_unavailable"}

    runtime = dict(runtime_options or build_single_settings_runtime_options())
    draft = normalize_portfolio_mix_draft(
        session_state.get(MIX_SESSION_KEYS["draft"])
        if isinstance(session_state.get(MIX_SESSION_KEYS["draft"]), Mapping)
        else build_initial_portfolio_mix_session_draft(),
        runtime_options=runtime,
    )
    components = list(draft["components"])

    if action == "set_mode":
        mode = str(payload.get("value") or "")
        if mode not in {"new", "saved"}:
            return {"accepted": False, "reason": "invalid_mode"}
        session_state[MIX_SESSION_KEYS["mode"]] = mode
    elif action == "set_shared_field":
        field_id = str(payload.get("field_id") or "")
        if field_id not in _SHARED_FIELDS:
            return {"accepted": False, "reason": "invalid_shared_field"}
        draft["shared"] = {**dict(draft["shared"]), field_id: payload.get("value")}
    elif action == "add_component":
        if len(components) >= 4:
            return {"accepted": False, "reason": "component_limit"}
        strategy_choice = str(payload.get("strategy_choice") or "")
        variant = payload.get("variant")
        if strategy_choice not in SINGLE_STRATEGY_OPTIONS or not _variant_allowed(
            strategy_choice, variant
        ):
            return {"accepted": False, "reason": "invalid_strategy"}
        component_id = f"component-{intent_id}"
        components.append(
            {
                "component_id": component_id,
                "strategy_choice": strategy_choice,
                "variant": variant,
                "settings_values": {},
                "role": "satellite",
                "weight_percent": 0.0,
            }
        )
        draft["components"] = components
    else:
        component_id = str(payload.get("component_id") or "")
        index = _component_index(draft, component_id)
        if index is None:
            return {"accepted": False, "reason": "unknown_component"}
        component = deepcopy(components[index])
        if action == "remove_component":
            if len(components) <= 2:
                return {"accepted": False, "reason": "component_minimum"}
            components.pop(index)
        elif action == "set_strategy":
            strategy_choice = str(payload.get("value") or "")
            if strategy_choice not in SINGLE_STRATEGY_OPTIONS:
                return {"accepted": False, "reason": "invalid_strategy"}
            variants = list(STRATEGY_FAMILY_VARIANTS.get(strategy_choice, {}))
            component["strategy_choice"] = strategy_choice
            component["variant"] = (
                "Annual" if variants and variants[0] == "Strict Annual" else None
            )
            component["settings_values"] = {}
            components[index] = component
        elif action == "set_variant":
            variant = payload.get("value")
            if not _variant_allowed(str(component["strategy_choice"]), variant):
                return {"accepted": False, "reason": "invalid_variant"}
            component["variant"] = variant
            component["settings_values"] = {}
            components[index] = component
        elif action == "set_role":
            role = str(payload.get("value") or "")
            if role not in MIX_ROLE_OPTIONS:
                return {"accepted": False, "reason": "invalid_role"}
            component["role"] = role
            components[index] = component
        elif action == "set_weight":
            try:
                component["weight_percent"] = float(payload.get("value"))
            except (TypeError, ValueError):
                return {"accepted": False, "reason": "invalid_weight"}
            components[index] = component
        else:
            workspace = _component_settings_workspace(
                component,
                shared=draft["shared"],
                runtime_options=runtime,
            )
            values = dict(component.get("settings_values") or {})
            if action == "apply_preset":
                preset_name = str(payload.get("preset_name") or "")
                try:
                    applied = apply_single_settings_preset(
                        workspace,
                        values,
                        preset_name,
                    )
                except ValueError:
                    return {"accepted": False, "reason": "invalid_preset"}
                component["settings_values"] = dict(applied["values"])
            elif action == "set_component_field":
                field_id = str(payload.get("field_id") or "")
                if field_id not in _allowed_component_field_ids(workspace):
                    return {"accepted": False, "reason": "invalid_component_field"}
                values[field_id] = payload.get("value")
                component["settings_values"] = values
            components[index] = component
        draft["components"] = components

    session_state[MIX_SESSION_KEYS["draft"]] = normalize_portfolio_mix_draft(
        draft,
        runtime_options=runtime,
    )
    session_state[MIX_SESSION_KEYS["last_intent_id"]] = intent_id
    response: dict[str, Any] = {"accepted": True, "action": action}
    if action == "add_component":
        response["component_id"] = component_id
    return response


def build_portfolio_mix_fallback_model(
    workspace: Mapping[str, Any],
) -> dict[str, Any]:
    """Project the same four steps for the Python fallback renderer."""

    return {
        "steps": [
            {"id": "configuration", "title": "구성 전략과 공통 기준"},
            {"id": "allocation", "title": "역할과 목표 비중"},
            {"id": "execution", "title": "Mix 실행과 해석"},
            {"id": "handoff", "title": "저장하고 Level2로 이동"},
        ],
        "mode": str(workspace.get("mode") or "new"),
        "draft": deepcopy(dict(workspace.get("draft") or {})),
        "component_cards": deepcopy(list(workspace.get("component_cards") or [])),
        "saved_mix": deepcopy(dict(workspace.get("saved_mix") or {})),
        "validation": deepcopy(dict(workspace.get("validation") or {})),
        "allocation": deepcopy(dict(workspace.get("allocation") or {})),
        "result": deepcopy(dict(workspace.get("result") or {})),
        "execution_action": deepcopy(workspace.get("execution_action")),
        "actions": deepcopy(list(workspace.get("actions") or [])),
    }


def render_backtest_portfolio_mix_workspace_fallback(
    workspace: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Render a compact Streamlit fallback from the same Python read model."""

    model = build_portfolio_mix_fallback_model(workspace)
    st.markdown("### Portfolio Mix Decision Workspace")
    for index, step in enumerate(model["steps"], start=1):
        with st.container(border=True):
            st.markdown(f"#### {index}. {step['title']}")
            if step["id"] == "configuration":
                for component in model["component_cards"]:
                    st.markdown(f"**{component.get('strategy_name') or '-'}**")
                    st.caption(
                        f"{component.get('purpose_label') or '-'} · "
                        f"{component.get('weight_percent') or 0:g}%"
                    )
            elif step["id"] == "allocation":
                st.metric(
                    "목표 비중 합계",
                    f"{float(model['allocation'].get('total_weight_percent') or 0):g}%",
                )
                for issue in list(model["validation"].get("issues") or []):
                    st.warning(str(issue.get("message") or "설정을 확인해 주세요."))
            elif step["id"] == "execution":
                action = dict(model.get("execution_action") or {})
                if action.get("enabled") and st.button(
                    str(action.get("label") or "Mix 실행"),
                    key="portfolio_mix_fallback_run",
                    use_container_width=True,
                ):
                    return {
                        "event": {
                            "id": "run_mix",
                            "intent_id": f"fallback-run-{date.today().isoformat()}",
                            "payload": {},
                        }
                    }
                if model["result"].get("status") == "stale":
                    st.info("이전 결과는 참고용이며 현재 설정으로 다시 실행해야 합니다.")
            else:
                for action in model["actions"]:
                    if action.get("enabled") and st.button(
                        str(action.get("label") or action.get("id")),
                        key=f"portfolio_mix_fallback_{action.get('id')}",
                        use_container_width=True,
                    ):
                        return {
                            "event": {
                                "id": action.get("id"),
                                "intent_id": f"fallback-{action.get('id')}-{date.today().isoformat()}",
                                "payload": {},
                            }
                        }
    return None


def build_portfolio_mix_workspace_from_session(
    *,
    session_state: MutableMapping[str, Any],
    runtime_options: Mapping[str, Any],
    saved_records: list[Mapping[str, Any]] | None = None,
    action_capabilities: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Build one rerun-stable workspace from an explicit session mapping."""

    if not isinstance(session_state.get(MIX_SESSION_KEYS["draft"]), Mapping):
        session_state[MIX_SESSION_KEYS["draft"]] = (
            build_initial_portfolio_mix_session_draft()
        )
    mode = str(session_state.get(MIX_SESSION_KEYS["mode"]) or "new")
    if mode not in {"new", "saved"}:
        mode = "new"
    workspace = build_portfolio_mix_workspace(
        draft=session_state[MIX_SESSION_KEYS["draft"]],
        saved_records=list(saved_records or []),
        component_states=session_state.get(MIX_SESSION_KEYS["component_states"]),
        current_result=session_state.get(MIX_SESSION_KEYS["current_result"]),
        last_result=session_state.get(MIX_SESSION_KEYS["last_result"]),
        action_capabilities=action_capabilities or {},
        runtime_options=runtime_options,
    )
    return {**workspace, "mode": mode}


def build_current_portfolio_mix_workspace() -> dict[str, Any]:
    """Adapt current Streamlit state into the pure Mix workspace."""

    return build_portfolio_mix_workspace_from_session(
        session_state=st.session_state,
        runtime_options=build_single_settings_runtime_options(),
    )


def _consume_component_change(*, component_key: str) -> None:
    value = st.session_state.get(component_key)
    apply_portfolio_mix_intent(
        value,
        session_state=st.session_state,
        runtime_options=build_single_settings_runtime_options(),
    )


def render_backtest_portfolio_mix_workspace() -> None:
    """Render and consume the current Portfolio Mix one-shell workspace."""

    workspace = build_current_portfolio_mix_workspace()
    if is_backtest_portfolio_mix_workspace_available():
        intent = render_backtest_portfolio_mix_workspace_component(
            workspace=workspace,
            key=_COMPONENT_KEY,
            on_change=partial(_consume_component_change, component_key=_COMPONENT_KEY),
        )
    else:
        intent = render_backtest_portfolio_mix_workspace_fallback(workspace)
    apply_portfolio_mix_intent(
        intent,
        session_state=st.session_state,
        runtime_options=build_single_settings_runtime_options(),
    )


__all__ = [
    "MIX_SESSION_KEYS",
    "apply_portfolio_mix_intent",
    "build_current_portfolio_mix_workspace",
    "build_initial_portfolio_mix_session_draft",
    "build_portfolio_mix_fallback_model",
    "build_portfolio_mix_workspace_from_session",
    "render_backtest_portfolio_mix_workspace",
    "render_backtest_portfolio_mix_workspace_fallback",
]
