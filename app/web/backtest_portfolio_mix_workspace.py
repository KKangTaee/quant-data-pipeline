"""Streamlit adapter for the Python-owned Portfolio Mix one-shell workspace."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from functools import partial
from typing import Any, Callable, Mapping, MutableMapping
from uuid import uuid4

import streamlit as st

from app.services.backtest_portfolio_mix_workspace import (
    MIX_ROLE_OPTIONS,
    PORTFOLIO_MIX_SAVED_SCHEMA_VERSION,
    PortfolioMixValidationError,
    build_portfolio_mix_fingerprint,
    build_portfolio_mix_result_evidence,
    build_portfolio_mix_workspace,
    extract_saved_portfolio_mix_draft,
    normalize_portfolio_mix_draft,
    project_portfolio_mix_component_payloads,
)
from app.services.backtest_compare_catalog import (
    ComparePresetCatalog,
    run_compare_strategy,
)
from app.services.backtest_practical_validation import (
    prepare_practical_validation_source_handoff,
)
from app.services.backtest_practical_validation_curve_context import (
    compact_curve_snapshot_from_bundle,
)
from app.services.backtest_practical_validation_source import (
    build_selection_source_from_weighted_mix_prefill,
    compact_selection_history_from_bundle,
)
from app.services.backtest_weighted_portfolio import build_weighted_portfolio_bundle
from app.runtime.backtest.stores.portfolio_store import (
    load_saved_portfolios,
    save_saved_portfolio,
)
from app.runtime.backtest.stores.run_history import append_backtest_run_history
from app.services.backtest_single_settings_workspace import (
    apply_single_settings_preset,
    build_single_settings_workspace,
)
from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    SINGLE_STRATEGY_OPTIONS,
    STRATEGY_FAMILY_VARIANTS,
)
from app.web.backtest_single_settings_workspace import (
    build_single_settings_runtime_options,
)
from app.web.backtest_common import (
    EQUAL_WEIGHT_PRESETS,
    GLOBAL_RELATIVE_STRENGTH_PRESETS,
    GTAA_PRESETS,
    QUALITY_STRICT_PRESETS,
    STRICT_ANNUAL_COMPARE_DEFAULT_PRESET,
    STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET,
    VALUE_STRICT_PRESETS,
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
    "component_bundles": "backtest_portfolio_mix_component_bundles",
    "weighted_bundle": "backtest_portfolio_mix_weighted_bundle",
    "error": "backtest_portfolio_mix_error",
    "notice": "backtest_portfolio_mix_notice",
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


def _compare_preset_catalog() -> ComparePresetCatalog:
    return ComparePresetCatalog(
        equal_weight_presets=EQUAL_WEIGHT_PRESETS,
        gtaa_presets=GTAA_PRESETS,
        global_relative_strength_presets=GLOBAL_RELATIVE_STRENGTH_PRESETS,
        quality_strict_presets=QUALITY_STRICT_PRESETS,
        value_strict_presets=VALUE_STRICT_PRESETS,
        strict_annual_compare_default_preset=STRICT_ANNUAL_COMPARE_DEFAULT_PRESET,
        strict_quarterly_prototype_default_preset=(
            STRICT_QUARTERLY_PROTOTYPE_DEFAULT_PRESET
        ),
    )


def _run_component_with_current_catalog(**kwargs: Any) -> dict[str, Any]:
    return run_compare_strategy(
        str(kwargs["strategy_name"]),
        start=str(kwargs["start"]),
        end=str(kwargs["end"]),
        timeframe=str(kwargs["timeframe"]),
        option=str(kwargs["option"]),
        overrides=dict(kwargs.get("overrides") or {}),
        preset_catalog=_compare_preset_catalog(),
    )


def _json_value(value: object) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return item()
        except (TypeError, ValueError):
            pass
    return str(value)


def _compact_bundle_summary(bundle: Mapping[str, Any]) -> dict[str, Any]:
    summary_df = bundle.get("summary_df")
    if summary_df is None or getattr(summary_df, "empty", True):
        return {}
    try:
        row = dict(summary_df.iloc[0].to_dict())
    except (AttributeError, IndexError, TypeError):
        return {}
    return {
        "annualized_return": _json_value(row.get("CAGR")),
        "maximum_drawdown": _json_value(row.get("Maximum Drawdown")),
        "sharpe_ratio": _json_value(row.get("Sharpe Ratio")),
        "end_balance": _json_value(row.get("End Balance")),
    }


def _compact_bundle_period(bundle: Mapping[str, Any]) -> dict[str, str | None]:
    meta = dict(bundle.get("meta") or {})
    result_df = bundle.get("result_df")
    if result_df is not None and not getattr(result_df, "empty", True):
        try:
            dates = result_df["Date"]
            start = str(dates.min())[:10]
            end = str(dates.max())[:10]
            return {"start": start, "end": end}
        except (KeyError, TypeError, AttributeError):
            pass
    return {
        "start": str(meta.get("start")) if meta.get("start") else None,
        "end": str(meta.get("actual_result_end") or meta.get("end"))
        if meta.get("actual_result_end") or meta.get("end")
        else None,
    }


def _execution_error(exc: Exception) -> tuple[str, str]:
    class_name = exc.__class__.__name__
    if class_name == "BacktestInputError":
        return "input", f"구성 전략 입력값을 확인해 주세요: {exc}"
    if class_name == "BacktestDataError":
        return "data", f"구성 전략에 필요한 데이터를 확인해 주세요: {exc}"
    return "system", f"구성 전략 실행 중 오류가 발생했습니다: {exc}"


def execute_portfolio_mix_draft(
    draft: Mapping[str, Any],
    *,
    runtime_options: Mapping[str, Any],
    run_component: Callable[..., dict[str, Any]],
    weighted_builder: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Run a validated Mix atomically while exposing component-local states."""

    normalized = normalize_portfolio_mix_draft(
        draft,
        runtime_options=runtime_options,
    )
    try:
        projections = project_portfolio_mix_component_payloads(
            normalized,
            runtime_options=runtime_options,
        )
    except PortfolioMixValidationError as exc:
        return {
            "ok": False,
            "error_kind": "validation",
            "error_message": "Mix 설정값을 확인해 주세요.",
            "validation_errors": dict(exc.errors),
            "component_states": {},
        }

    shared = dict(normalized["shared"])
    fingerprint = build_portfolio_mix_fingerprint(
        normalized,
        runtime_options=runtime_options,
    )
    component_states: dict[str, dict[str, Any]] = {
        str(item["component_id"]): {
            "status": "pending",
            "message": "실행 대기 중",
        }
        for item in projections
    }
    bundles: list[dict[str, Any]] = []
    for projection in projections:
        component_id = str(projection["component_id"])
        component_states[component_id] = {
            "status": "running",
            "message": "전략을 계산하고 있습니다.",
        }
        try:
            bundle = run_component(
                strategy_name=projection["strategy_name"],
                start=shared["start"],
                end=shared["end"],
                timeframe=shared["timeframe"],
                option=shared["option"],
                overrides=dict(projection["overrides"]),
            )
        except Exception as exc:  # execution boundary normalizes domain failures
            error_kind, error_message = _execution_error(exc)
            component_states[component_id] = {
                "status": "error",
                "message": error_message,
            }
            return {
                "ok": False,
                "error_kind": error_kind,
                "error_message": error_message,
                "failed_component_id": component_id,
                "component_states": component_states,
            }
        bundles.append(dict(bundle))
        component_states[component_id] = {
            "status": "completed",
            "message": "계산을 완료했습니다.",
        }

    try:
        weighted_bundle = weighted_builder(
            bundles=bundles,
            weights_percent=[float(item["weight_percent"]) for item in projections],
            date_policy=str(shared["date_policy"]),
            source_kind="backtest_portfolio_mix_workspace",
            compare_source_context={
                "configuration_fingerprint": fingerprint,
                "draft_id": normalized["draft_id"],
            },
            component_roles=[str(item["role"]) for item in projections],
        )
    except Exception as exc:  # weighted construction is a distinct boundary
        error_kind, error_message = _execution_error(exc)
        return {
            "ok": False,
            "error_kind": error_kind,
            "error_message": error_message,
            "failed_component_id": "weighted_portfolio",
            "component_states": component_states,
        }

    meta = dict(weighted_bundle.get("meta") or {})
    run_result_id = str(meta.get("run_id") or f"portfolio_mix_{uuid4().hex[:12]}")
    current_result = {
        "run_result_id": run_result_id,
        "configuration_fingerprint": fingerprint,
        "summary": _compact_bundle_summary(weighted_bundle),
        "period": _compact_bundle_period(weighted_bundle),
        "component_count": len(projections),
        "component_strategy_names": [
            str(item["strategy_name"]) for item in projections
        ],
        "component_roles": [str(item["role"]) for item in projections],
        "weights_percent": [float(item["weight_percent"]) for item in projections],
        "evidence": build_portfolio_mix_result_evidence(weighted_bundle),
    }
    return {
        "ok": True,
        "draft": normalized,
        "configuration_fingerprint": fingerprint,
        "component_states": component_states,
        "component_bundles": bundles,
        "weighted_bundle": weighted_bundle,
        "current_result": current_result,
    }


def run_current_portfolio_mix(
    *,
    session_state: MutableMapping[str, Any],
    runtime_options: Mapping[str, Any],
    run_component: Callable[..., dict[str, Any]] = _run_component_with_current_catalog,
    weighted_builder: Callable[..., dict[str, Any]] = build_weighted_portfolio_bundle,
    history_appender: Callable[..., None] = append_backtest_run_history,
) -> dict[str, Any]:
    """Execute the current draft and commit session state only after full success."""

    draft = session_state.get(MIX_SESSION_KEYS["draft"])
    result = execute_portfolio_mix_draft(
        draft if isinstance(draft, Mapping) else {},
        runtime_options=runtime_options,
        run_component=run_component,
        weighted_builder=weighted_builder,
    )
    session_state[MIX_SESSION_KEYS["component_states"]] = deepcopy(
        result.get("component_states") or {}
    )
    if not result.get("ok"):
        session_state[MIX_SESSION_KEYS["error"]] = {
            "kind": result.get("error_kind"),
            "message": result.get("error_message"),
            "failed_component_id": result.get("failed_component_id"),
        }
        return {
            "accepted": False,
            "reason": (
                "validation_failed"
                if result.get("error_kind") == "validation"
                else "component_execution_failed"
            ),
            "result": result,
        }

    previous = session_state.get(MIX_SESSION_KEYS["current_result"])
    if isinstance(previous, Mapping):
        session_state[MIX_SESSION_KEYS["last_result"]] = deepcopy(dict(previous))
    session_state[MIX_SESSION_KEYS["draft"]] = deepcopy(result["draft"])
    session_state[MIX_SESSION_KEYS["current_result"]] = deepcopy(
        result["current_result"]
    )
    session_state[MIX_SESSION_KEYS["component_bundles"]] = list(
        result["component_bundles"]
    )
    session_state[MIX_SESSION_KEYS["weighted_bundle"]] = result["weighted_bundle"]
    session_state[MIX_SESSION_KEYS["error"]] = None
    session_state[MIX_SESSION_KEYS["notice"]] = (
        "현재 구성으로 Portfolio Mix 계산을 완료했습니다."
    )
    try:
        history_appender(
            bundle=result["weighted_bundle"],
            run_kind="portfolio_mix",
            context={
                "configuration_fingerprint": result["configuration_fingerprint"],
                "component_count": len(result["component_bundles"]),
            },
        )
    except Exception as exc:  # history is audit support, not the calculation result
        session_state[MIX_SESSION_KEYS["notice"]] = (
            "Mix 계산은 완료했지만 실행 기록 저장을 확인해 주세요: " f"{exc}"
        )
    return {"accepted": True, "action": "run_mix", "result": result}


def apply_portfolio_mix_intent(
    intent: object,
    *,
    session_state: MutableMapping[str, Any],
    runtime_options: Mapping[str, Any] | None = None,
    action_handlers: Mapping[
        str, Callable[[Mapping[str, Any]], Mapping[str, Any] | None]
    ]
    | None = None,
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
        handler = dict(action_handlers or {}).get(action)
        if not callable(handler):
            return {"accepted": False, "reason": "handler_unavailable"}
        session_state[MIX_SESSION_KEYS["last_intent_id"]] = intent_id
        try:
            handled = handler(payload)
        except Exception as exc:
            session_state[MIX_SESSION_KEYS["error"]] = {
                "kind": "action",
                "message": str(exc),
            }
            return {"accepted": False, "reason": "action_failed"}
        response = dict(handled or {})
        response.setdefault("accepted", True)
        response.setdefault("action", action)
        return response

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


def _current_result_matches_draft(
    *,
    session_state: Mapping[str, Any],
    runtime_options: Mapping[str, Any],
) -> bool:
    draft = session_state.get(MIX_SESSION_KEYS["draft"])
    result = session_state.get(MIX_SESSION_KEYS["current_result"])
    if not isinstance(draft, Mapping) or not isinstance(result, Mapping):
        return False
    return str(result.get("configuration_fingerprint") or "") == (
        build_portfolio_mix_fingerprint(draft, runtime_options=runtime_options)
    )


def _suggest_mix_name(draft: Mapping[str, Any]) -> str:
    parts = [
        f"{component.get('strategy_choice')} {float(component.get('weight_percent') or 0):g}%"
        for component in list(draft.get("components") or [])
        if isinstance(component, Mapping)
    ]
    return " + ".join(parts) or "Portfolio Mix"


def _saved_contexts(
    *,
    draft: Mapping[str, Any],
    runtime_options: Mapping[str, Any],
    current_result: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    normalized = normalize_portfolio_mix_draft(
        draft,
        runtime_options=runtime_options,
    )
    projections = project_portfolio_mix_component_payloads(
        normalized,
        runtime_options=runtime_options,
    )
    shared = dict(normalized["shared"])
    compare_context = {
        "selected_strategies": [item["strategy_name"] for item in projections],
        "start": shared["start"],
        "end": shared["end"],
        "timeframe": shared["timeframe"],
        "option": shared["option"],
        "strategy_overrides": {
            str(item["strategy_name"]): deepcopy(dict(item["overrides"]))
            for item in projections
        },
    }
    portfolio_context = {
        "strategy_names": [item["strategy_name"] for item in projections],
        "weights_percent": [float(item["weight_percent"]) for item in projections],
        "normalized_weights": [
            float(item["weight_percent"]) / 100.0 for item in projections
        ],
        "component_roles": [str(item["role"]) for item in projections],
        "date_policy": shared["date_policy"],
    }
    source_context = {
        "created_from": "backtest_portfolio_mix_workspace",
        "mix_schema_version": PORTFOLIO_MIX_SAVED_SCHEMA_VERSION,
        "mix_draft": normalized,
        "configuration_fingerprint": str(
            current_result.get("configuration_fingerprint") or ""
        ),
        "run_result_id": current_result.get("run_result_id"),
    }
    return compare_context, portfolio_context, source_context


def save_current_portfolio_mix(
    payload: Mapping[str, Any],
    *,
    session_state: MutableMapping[str, Any],
    runtime_options: Mapping[str, Any],
    save_handler: Callable[..., dict[str, Any]] = save_saved_portfolio,
) -> dict[str, Any]:
    """Persist only the new Mix setup schema after a matching successful run."""

    if not _current_result_matches_draft(
        session_state=session_state,
        runtime_options=runtime_options,
    ):
        return {"accepted": False, "reason": "current_result_required"}
    draft = dict(session_state[MIX_SESSION_KEYS["draft"]])
    current_result = dict(session_state[MIX_SESSION_KEYS["current_result"]])
    if not isinstance(session_state.get(MIX_SESSION_KEYS["weighted_bundle"]), Mapping):
        return {"accepted": False, "reason": "weighted_bundle_required"}
    compare_context, portfolio_context, source_context = _saved_contexts(
        draft=draft,
        runtime_options=runtime_options,
        current_result=current_result,
    )
    name = str(payload.get("name") or "").strip() or _suggest_mix_name(draft)
    record = save_handler(
        name=name,
        description=str(payload.get("description") or "").strip(),
        compare_context=compare_context,
        portfolio_context=portfolio_context,
        source_context=source_context,
        portfolio_id=(
            str(payload.get("portfolio_id"))
            if payload.get("portfolio_id") not in (None, "")
            else None
        ),
    )
    session_state[MIX_SESSION_KEYS["notice"]] = (
        f"`{record.get('name') or name}` Mix 설정을 저장했습니다."
    )
    return {"accepted": True, "action": "save_mix", "record": record}


def restore_saved_portfolio_mix(
    payload: Mapping[str, Any],
    *,
    session_state: MutableMapping[str, Any],
    saved_records: list[Mapping[str, Any]],
    runtime_options: Mapping[str, Any],
) -> dict[str, Any]:
    """Restore an approved setup as a draft without fabricating a run result."""

    saved_mix_id = str(payload.get("saved_mix_id") or "")
    record = next(
        (
            dict(item)
            for item in saved_records
            if str(item.get("portfolio_id") or item.get("id") or "") == saved_mix_id
        ),
        None,
    )
    draft_source = extract_saved_portfolio_mix_draft(record)
    if record is None or draft_source is None:
        return {"accepted": False, "reason": "saved_mix_not_found"}
    previous = session_state.get(MIX_SESSION_KEYS["current_result"])
    if isinstance(previous, Mapping):
        session_state[MIX_SESSION_KEYS["last_result"]] = deepcopy(dict(previous))
    restored = normalize_portfolio_mix_draft(
        draft_source,
        runtime_options=runtime_options,
    )
    restored["source_saved_portfolio_id"] = saved_mix_id
    session_state[MIX_SESSION_KEYS["draft"]] = restored
    session_state[MIX_SESSION_KEYS["mode"]] = "new"
    session_state[MIX_SESSION_KEYS["current_result"]] = None
    session_state[MIX_SESSION_KEYS["component_bundles"]] = None
    session_state[MIX_SESSION_KEYS["weighted_bundle"]] = None
    session_state[MIX_SESSION_KEYS["component_states"]] = {}
    session_state[MIX_SESSION_KEYS["error"]] = None
    session_state[MIX_SESSION_KEYS["notice"]] = (
        f"`{record.get('name') or '저장된 Mix'}` 설정을 불러왔습니다. "
        "현재 데이터로 실행하면 새 결과가 만들어집니다."
    )
    return {"accepted": True, "action": "restore_saved_mix", "record": record}


def run_saved_portfolio_mix(
    payload: Mapping[str, Any],
    *,
    session_state: MutableMapping[str, Any],
    saved_records: list[Mapping[str, Any]],
    runtime_options: Mapping[str, Any],
) -> dict[str, Any]:
    restored = restore_saved_portfolio_mix(
        payload,
        session_state=session_state,
        saved_records=saved_records,
        runtime_options=runtime_options,
    )
    if not restored.get("accepted"):
        return restored
    return run_current_portfolio_mix(
        session_state=session_state,
        runtime_options=runtime_options,
    )


def _build_level2_prefill(
    *,
    draft: Mapping[str, Any],
    current_result: Mapping[str, Any],
    component_bundles: list[Mapping[str, Any]],
    weighted_bundle: Mapping[str, Any],
    runtime_options: Mapping[str, Any],
    name: str,
) -> dict[str, Any]:
    normalized = normalize_portfolio_mix_draft(
        draft,
        runtime_options=runtime_options,
    )
    projections = project_portfolio_mix_component_payloads(
        normalized,
        runtime_options=runtime_options,
    )
    components: list[dict[str, Any]] = []
    for projection, bundle in zip(projections, component_bundles):
        bundle_row = dict(bundle)
        meta = dict(bundle_row.get("meta") or {})
        summary = _compact_bundle_summary(bundle_row)
        contract = {
            "start": normalized["shared"]["start"],
            "end": normalized["shared"]["end"],
            "timeframe": normalized["shared"]["timeframe"],
            "option": normalized["shared"]["option"],
            **deepcopy(dict(projection["overrides"])),
        }
        components.append(
            {
                "registry_id": (
                    f"portfolio_mix_{current_result.get('run_result_id')}_"
                    f"{projection['component_id']}"
                ),
                "title": projection["strategy_name"],
                "strategy_family": projection["concrete_strategy_key"],
                "strategy_key": projection["concrete_strategy_key"],
                "strategy_name": projection["strategy_name"],
                "candidate_role": projection["role"],
                "proposal_role": projection["role"],
                "target_weight": float(projection["weight_percent"]),
                "weight_reason": "Portfolio Mix에서 사용자가 지정한 목표 비중",
                "data_trust_status": str(meta.get("data_trust_status") or "snapshot"),
                "cagr": summary.get("annualized_return"),
                "mdd": summary.get("maximum_drawdown"),
                "period": _compact_bundle_period(bundle_row),
                "result_curve": compact_curve_snapshot_from_bundle(bundle_row),
                "selection_history": compact_selection_history_from_bundle(
                    bundle_row,
                    component_weight=float(projection["weight_percent"]),
                ),
                "contract": contract,
                "benchmark": meta.get("benchmark_ticker") or contract.get("benchmark_ticker") or "-",
                "universe": contract.get("tickers") or [],
                "compare_evidence": {
                    "source_kind": "backtest_portfolio_mix_workspace",
                    "configuration_fingerprint": current_result.get(
                        "configuration_fingerprint"
                    ),
                },
                "open_candidate_blockers": [],
            }
        )
    return {
        "source_kind": "weighted_portfolio_mix",
        "run_result_id": current_result.get("run_result_id"),
        "weighted_portfolio_id": (
            normalized.get("source_saved_portfolio_id")
            or f"current_mix_{str(current_result.get('run_result_id') or uuid4().hex)}"
        ),
        "weighted_portfolio_name": name,
        "description": "Portfolio Mix Decision Workspace에서 계산한 현재 비중 조합",
        "compare_context": _saved_contexts(
            draft=normalized,
            runtime_options=runtime_options,
            current_result=current_result,
        )[0],
        "portfolio_context": _saved_contexts(
            draft=normalized,
            runtime_options=runtime_options,
            current_result=current_result,
        )[1],
        "source_context": {
            "created_from": "backtest_portfolio_mix_workspace",
            "configuration_fingerprint": current_result.get(
                "configuration_fingerprint"
            ),
        },
        "weighted_summary": _compact_bundle_summary(weighted_bundle),
        "weighted_period": _compact_bundle_period(weighted_bundle),
        "weighted_curve_snapshot": compact_curve_snapshot_from_bundle(
            dict(weighted_bundle)
        ),
        "selection_history_snapshot": compact_selection_history_from_bundle(
            dict(weighted_bundle)
        ),
        "data_trust_status": "weighted_mix_snapshot",
        "components": components,
    }


def handoff_current_portfolio_mix(
    payload: Mapping[str, Any],
    *,
    session_state: MutableMapping[str, Any],
    runtime_options: Mapping[str, Any],
    source_builder: Callable[[dict[str, Any]], dict[str, Any]] = (
        build_selection_source_from_weighted_mix_prefill
    ),
    handoff_handler: Callable[..., Any] = prepare_practical_validation_source_handoff,
) -> dict[str, Any]:
    """Register the current Mix as one Level2 source through the callable handoff."""

    if not _current_result_matches_draft(
        session_state=session_state,
        runtime_options=runtime_options,
    ):
        return {"accepted": False, "reason": "current_result_required"}
    draft_value = session_state.get(MIX_SESSION_KEYS["draft"])
    if not isinstance(draft_value, Mapping):
        return {"accepted": False, "reason": "current_result_required"}
    if any(
        LEVEL1_STRATEGY_MATURITY.get(str(component.get("strategy_choice") or ""))
        == "development"
        for component in list(draft_value.get("components") or [])
        if isinstance(component, Mapping)
    ):
        return {"accepted": False, "reason": "development_component_blocked"}
    component_bundles = session_state.get(MIX_SESSION_KEYS["component_bundles"])
    weighted_bundle = session_state.get(MIX_SESSION_KEYS["weighted_bundle"])
    if not isinstance(component_bundles, list) or not isinstance(
        weighted_bundle, Mapping
    ):
        return {"accepted": False, "reason": "weighted_bundle_required"}
    draft = dict(draft_value)
    current_result = dict(session_state[MIX_SESSION_KEYS["current_result"]])
    name = str(payload.get("name") or "").strip() or _suggest_mix_name(draft)
    prefill = _build_level2_prefill(
        draft=draft,
        current_result=current_result,
        component_bundles=[dict(item) for item in component_bundles],
        weighted_bundle=dict(weighted_bundle),
        runtime_options=runtime_options,
        name=name,
    )
    source = source_builder(prefill)
    handoff = handoff_handler(source, persist=True)
    source_payload = getattr(handoff, "source_payload", None)
    notice = getattr(handoff, "notice", None)
    mode = getattr(handoff, "mode", None)
    requested_panel = getattr(handoff, "requested_panel", None)
    if isinstance(handoff, Mapping):
        source_payload = handoff.get("source_payload", source_payload)
        notice = handoff.get("notice", notice)
        mode = handoff.get("mode", mode)
        requested_panel = handoff.get("requested_panel", requested_panel)
    session_state["backtest_practical_validation_source"] = source_payload or source
    session_state["backtest_practical_validation_notice"] = notice or (
        f"`{name}`를 Practical Validation으로 보냈습니다."
    )
    session_state["backtest_practical_validation_mode"] = mode or "Selected Source"
    session_state["backtest_requested_panel"] = requested_panel or (
        "Practical Validation"
    )
    return {"accepted": True, "action": "handoff_level2", "source": source}


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
    return {
        **workspace,
        "mode": mode,
        "feedback": {
            "notice": str(session_state.get(MIX_SESSION_KEYS["notice"]) or ""),
            "error": deepcopy(session_state.get(MIX_SESSION_KEYS["error"])),
        },
    }


def build_current_portfolio_mix_workspace() -> dict[str, Any]:
    """Adapt current Streamlit state into the pure Mix workspace."""

    return build_portfolio_mix_workspace_from_session(
        session_state=st.session_state,
        runtime_options=build_single_settings_runtime_options(),
        saved_records=load_saved_portfolios(limit=100),
        action_capabilities={
            "run_mix": True,
            "save_mix": True,
            "handoff_level2": True,
        },
    )


def _current_action_handlers(
    *,
    runtime_options: Mapping[str, Any],
    saved_records: list[Mapping[str, Any]],
) -> dict[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]]:
    return {
        "run_mix": lambda payload: run_current_portfolio_mix(
            session_state=st.session_state,
            runtime_options=runtime_options,
        ),
        "save_mix": lambda payload: save_current_portfolio_mix(
            payload,
            session_state=st.session_state,
            runtime_options=runtime_options,
        ),
        "handoff_level2": lambda payload: handoff_current_portfolio_mix(
            payload,
            session_state=st.session_state,
            runtime_options=runtime_options,
        ),
        "restore_saved_mix": lambda payload: restore_saved_portfolio_mix(
            payload,
            session_state=st.session_state,
            saved_records=saved_records,
            runtime_options=runtime_options,
        ),
        "run_saved_mix": lambda payload: run_saved_portfolio_mix(
            payload,
            session_state=st.session_state,
            saved_records=saved_records,
            runtime_options=runtime_options,
        ),
    }


def _consume_component_change(*, component_key: str) -> None:
    value = st.session_state.get(component_key)
    runtime_options = build_single_settings_runtime_options()
    saved_records = load_saved_portfolios(limit=100)
    apply_portfolio_mix_intent(
        value,
        session_state=st.session_state,
        runtime_options=runtime_options,
        action_handlers=_current_action_handlers(
            runtime_options=runtime_options,
            saved_records=saved_records,
        ),
    )


def render_backtest_portfolio_mix_workspace() -> None:
    """Render and consume the current Portfolio Mix one-shell workspace."""

    runtime_options = build_single_settings_runtime_options()
    saved_records = load_saved_portfolios(limit=100)
    workspace = build_portfolio_mix_workspace_from_session(
        session_state=st.session_state,
        runtime_options=runtime_options,
        saved_records=saved_records,
        action_capabilities={
            "run_mix": True,
            "save_mix": True,
            "handoff_level2": True,
        },
    )
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
        runtime_options=runtime_options,
        action_handlers=_current_action_handlers(
            runtime_options=runtime_options,
            saved_records=saved_records,
        ),
    )


__all__ = [
    "MIX_SESSION_KEYS",
    "apply_portfolio_mix_intent",
    "build_current_portfolio_mix_workspace",
    "build_initial_portfolio_mix_session_draft",
    "build_portfolio_mix_fallback_model",
    "build_portfolio_mix_workspace_from_session",
    "execute_portfolio_mix_draft",
    "handoff_current_portfolio_mix",
    "restore_saved_portfolio_mix",
    "run_current_portfolio_mix",
    "run_saved_portfolio_mix",
    "save_current_portfolio_mix",
    "render_backtest_portfolio_mix_workspace",
    "render_backtest_portfolio_mix_workspace_fallback",
]
