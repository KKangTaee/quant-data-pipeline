from __future__ import annotations

from contextlib import contextmanager
from html import escape
from datetime import date
from typing import Any, Callable, Iterator, Mapping, Sequence

import streamlit as st

from app.services.backtest_single_settings_workspace import (
    SettingsValidationError,
    build_single_settings_workspace,
    project_single_settings_payload,
)
from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    LEVEL1_STRATEGY_PURPOSE_GROUPS,
    SINGLE_STRATEGY_OPTIONS,
    family_variant_options,
    resolve_concrete_strategy_display_name,
)


_SETTINGS_ACTIONS = frozenset({"select_strategy_variant", "run_single_strategy"})
_UI_TO_SCHEMA_VARIANT = {
    "Strict Annual": "Annual",
    "Strict Quarterly": "Quarterly",
    "Annual": "Annual",
    "Quarterly": "Quarterly",
    "Snapshot": "Snapshot",
}
_SCHEMA_TO_UI_VARIANT = {
    "Annual": "Strict Annual",
    "Quarterly": "Strict Quarterly",
    "Snapshot": "Snapshot",
}
_CONSUMED_INTENTS_KEY = "backtest_single_settings_consumed_intent_ids"
_DRAFTS_KEY = "backtest_single_settings_drafts"
_ERRORS_KEY = "backtest_single_settings_validation_errors"


_STRATEGY_DESCRIPTIONS = {
    "Quality + Value": "기업의 품질과 가치평가를 함께 비교해 보유 후보를 고릅니다.",
    "Quality": "수익성과 재무 건전성이 상대적으로 좋은 기업을 고릅니다.",
    "Value": "기초가치 대비 가격 부담이 낮은 기업을 고릅니다.",
    "GTAA": "자산군의 상대강도와 추세를 비교해 공격·방어 자산을 선택합니다.",
    "Global Relative Strength": "글로벌 자산군의 상대강도를 비교해 상위 자산을 보유합니다.",
    "Dual Momentum": "상대·절대 모멘텀을 함께 확인해 공격·방어 자산을 선택합니다.",
    "Risk Parity Trend": "변동성과 추세를 함께 사용해 자산별 위험 기여를 조정합니다.",
    "Equal Weight": "선택한 자산을 같은 비중으로 보유하고 정해진 주기로 조정합니다.",
    "Risk-On Momentum 5D": "단기 위험선호 종목을 탐색하는 개발 중 전략입니다.",
}


def _strategy_purpose_label(strategy_choice: str) -> str:
    return next(
        (
            str(group["label"])
            for group in LEVEL1_STRATEGY_PURPOSE_GROUPS.values()
            if strategy_choice in group["items"]
        ),
        "기타 전략",
    )


def build_single_strategy_settings_summary(
    strategy_choice: str,
    selected_variant: str | None,
) -> dict[str, str | None]:
    """Project the selected strategy into a user-facing Step 2 summary."""

    maturity = LEVEL1_STRATEGY_MATURITY.get(strategy_choice, "development")
    return {
        "strategy_choice": strategy_choice,
        "display_name": resolve_concrete_strategy_display_name(
            strategy_choice,
            selected_variant,
        ),
        "variant": selected_variant,
        "purpose": _strategy_purpose_label(strategy_choice),
        "maturity": maturity,
        "maturity_label": "운영 전략" if maturity == "production" else "개발 중",
        "description": _STRATEGY_DESCRIPTIONS.get(
            strategy_choice,
            "선택한 전략의 실행 조건을 확인합니다.",
        ),
    }


def build_compact_ticker_summary(
    tickers: Sequence[str],
    *,
    preview_count: int = 5,
) -> dict[str, str | int]:
    """Keep the first-read universe compact while preserving complete evidence."""

    normalized = [str(ticker).strip().upper() for ticker in tickers if str(ticker).strip()]
    preview = ", ".join(normalized[: max(1, preview_count)]) or "없음"
    return {
        "count": len(normalized),
        "headline": f"선택 종목 {len(normalized)}개 · 대표 {preview}",
        "full_text": ", ".join(normalized),
    }


def _render_single_settings_style() -> None:
    st.markdown(
        """
        <style>
        .bt1-settings-summary {
          color-scheme: light;
          background: linear-gradient(135deg, #f6faff 0%, #eef6f7 100%);
          border: 1px solid #d8e4ee;
          border-radius: 20px;
          padding: 1.1rem 1.2rem;
          margin: 0.25rem 0 1rem;
          color: #152033;
        }
        .bt1-settings-summary__eyebrow {
          color: #557086;
          font-size: 0.78rem;
          font-weight: 800;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .bt1-settings-summary__title {
          font-size: 1.35rem;
          font-weight: 800;
          margin: 0.3rem 0 0.45rem;
        }
        .bt1-settings-summary__meta {
          display: flex;
          flex-wrap: wrap;
          gap: 0.45rem;
          margin-bottom: 0.55rem;
        }
        .bt1-settings-summary__meta span {
          background: #ffffff;
          border: 1px solid #d8e4ee;
          border-radius: 999px;
          color: #38536a;
          font-size: 0.78rem;
          font-weight: 700;
          padding: 0.28rem 0.58rem;
        }
        .bt1-settings-summary__description {
          color: #52677a;
          font-size: 0.92rem;
          line-height: 1.55;
          margin: 0;
        }
        @media (max-width: 760px) {
          .bt1-settings-summary { border-radius: 16px; padding: 1rem; }
          .bt1-settings-summary__title { font-size: 1.16rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_single_strategy_settings_header(
    *,
    strategy_choice: str,
    selected_variant: str | None,
    variant_key: str | None = None,
    variant_options: Sequence[str] = (),
) -> str | None:
    """Render the only Step 2 strategy summary and compact family variant control."""

    if variant_key and variant_options:
        options = list(variant_options)
        current_variant = selected_variant if selected_variant in options else options[0]
        if st.session_state.get(variant_key) not in options:
            st.session_state[variant_key] = current_variant
        selected_variant = st.segmented_control(
            "실행 기준",
            options=options,
            key=variant_key,
            help="연간 또는 분기 재무제표 기준을 선택합니다.",
            width="stretch",
        )
        selected_variant = str(selected_variant or current_variant)

    summary = build_single_strategy_settings_summary(strategy_choice, selected_variant)
    _render_single_settings_style()
    variant_badge = (
        f"<span>{escape(str(summary['variant']))}</span>"
        if summary.get("variant")
        else ""
    )
    st.markdown(
        f"""
        <section class="bt1-settings-summary">
          <div class="bt1-settings-summary__eyebrow">현재 설정 대상</div>
          <div class="bt1-settings-summary__title">{escape(str(summary['display_name']))}</div>
          <div class="bt1-settings-summary__meta">
            <span>{escape(str(summary['purpose']))}</span>
            {variant_badge}
            <span>{escape(str(summary['maturity_label']))}</span>
          </div>
          <p class="bt1-settings-summary__description">{escape(str(summary['description']))}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    return selected_variant


@contextmanager
def single_settings_section(title: str, description: str) -> Iterator[None]:
    """Render one consistent settings card without owning its strategy widgets."""

    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.caption(description)
        yield


def render_compact_ticker_summary(
    tickers: Sequence[str],
    *,
    preview_count: int = 5,
) -> None:
    summary = build_compact_ticker_summary(tickers, preview_count=preview_count)
    st.caption(str(summary["headline"]))
    with st.expander("전체 종목 보기", expanded=False):
        st.code(str(summary["full_text"]) or "선택된 종목이 없습니다.")


def _variant_session_key(strategy_choice: str) -> str | None:
    """Resolve the existing family session key without creating an import cycle."""

    from app.web.backtest_common import _single_family_variant_session_key

    return _single_family_variant_session_key(strategy_choice)


def _schema_variant(value: object) -> str | None:
    if value is None:
        return None
    return _UI_TO_SCHEMA_VARIANT.get(str(value), str(value))


def _ui_variant(value: object) -> str | None:
    if value is None:
        return None
    return _SCHEMA_TO_UI_VARIANT.get(str(value), str(value))


def build_single_settings_runtime_options() -> dict[str, object]:
    """Adapt Python-owned catalogs/defaults into the pure settings service input."""

    from app.web import backtest_common as common

    presets: dict[str, Mapping[str, Sequence[str]]] = {
        "Equal Weight": common.EQUAL_WEIGHT_PRESETS,
        "GTAA": common.GTAA_PRESETS,
        "Global Relative Strength": common.GLOBAL_RELATIVE_STRENGTH_PRESETS,
        "Risk Parity Trend": common.RISK_PARITY_PRESETS,
        "Dual Momentum": common.DUAL_MOMENTUM_PRESETS,
    }
    strict_presets = common.QUALITY_STRICT_PRESETS
    presets_by_strategy_key = {
        "quality_snapshot": common.QUALITY_BROAD_PRESETS,
        "quality_snapshot_strict_annual": strict_presets,
        "quality_snapshot_strict_quarterly_prototype": strict_presets,
        "value_snapshot_strict_annual": common.VALUE_STRICT_PRESETS,
        "value_snapshot_strict_quarterly_prototype": common.VALUE_STRICT_PRESETS,
        "quality_value_snapshot_strict_annual": strict_presets,
        "quality_value_snapshot_strict_quarterly_prototype": strict_presets,
    }
    ticker_values: list[str] = []
    for catalog in [*presets.values(), *presets_by_strategy_key.values()]:
        for members in catalog.values():
            ticker_values.extend(str(item).strip().upper() for item in members)
    ticker_values.extend(str(item).strip().upper() for item in common.GTAA_DEFAULT_DEFENSIVE_TICKERS)
    ticker_values.extend(str(item).strip().upper() for item in common.STRICT_DEFAULT_DEFENSIVE_TICKERS)

    return {
        "presets": {key: dict(value) for key, value in presets.items()},
        "presets_by_strategy_key": {
            key: dict(value) for key, value in presets_by_strategy_key.items()
        },
        "preset_target_sizes": dict(common.STRICT_ANNUAL_MANAGED_PRESET_SPECS),
        "tickers": list(dict.fromkeys(item for item in ticker_values if item)),
        "benchmarks": ["SPY", "ACWI", "QQQ", "VTI", "IWM"],
        "score_horizons": list(common.GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
        "market_regime_benchmarks": list(common.STRICT_MARKET_REGIME_BENCHMARK_OPTIONS),
        "policy_defaults": dict(common._dynamic_etf_promotion_policy_defaults()),
        "quality_factor_options": list(common.QUALITY_STRICT_FACTOR_OPTIONS),
        "value_factor_options": list(common.VALUE_STRICT_FACTOR_OPTIONS),
    }


def _current_strategy_and_variant(
    selected_variant: str | None = None,
) -> tuple[str, str | None]:
    strategy_choice = str(
        st.session_state.get("backtest_strategy_choice") or "Quality + Value"
    )
    if strategy_choice not in SINGLE_STRATEGY_OPTIONS:
        strategy_choice = "Quality + Value"
    if family_variant_options(strategy_choice):
        variant_key = _variant_session_key(strategy_choice)
        ui_value = selected_variant
        if ui_value is None and variant_key:
            ui_value = st.session_state.get(variant_key)
        options = family_variant_options(strategy_choice)
        if ui_value not in options:
            ui_value = options[0]
        return strategy_choice, _schema_variant(ui_value)
    return strategy_choice, None


def _workspace_fields(workspace: Mapping[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for section in workspace.get("sections", []):
        if not isinstance(section, Mapping):
            continue
        for field in section.get("fields", []):
            if isinstance(field, Mapping):
                result.append(dict(field))
    return result


def _prefill_values(
    workspace: Mapping[str, object],
    payload: object,
) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        return {}
    if payload.get("strategy_key") != workspace.get("concrete_strategy_key"):
        return {}
    projected: dict[str, object] = {}
    for field in _workspace_fields(workspace):
        field_id = str(field.get("field_id") or "")
        payload_key = str(field.get("payload_key") or "")
        if not field_id or payload_key not in payload:
            continue
        value = payload[payload_key]
        scale = field.get("payload_scale")
        if isinstance(scale, (int, float)) and scale and isinstance(value, (int, float)):
            value = float(value) / float(scale)
        if field_id == "min_avg_dollar_volume_20d_m" and isinstance(value, (int, float)):
            value = float(value) / 1_000_000.0
        projected[field_id] = value
    return projected


def build_current_single_settings_workspace(
    *,
    selected_variant: str | None = None,
    runtime_options: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build the editor model for the current catalog selection and replay draft."""

    strategy_choice, variant = _current_strategy_and_variant(selected_variant)
    runtime = dict(runtime_options or build_single_settings_runtime_options())
    empty = build_single_settings_workspace(strategy_choice, variant, {}, runtime)
    draft_key = str(empty["draft_key"])
    drafts = st.session_state.get(_DRAFTS_KEY)
    stored = dict(drafts.get(draft_key, {})) if isinstance(drafts, Mapping) else {}
    values = {
        **_prefill_values(empty, st.session_state.get("backtest_prefill_payload")),
        **stored,
    }
    workspace = build_single_settings_workspace(strategy_choice, variant, values, runtime)
    primary_variants = {
        _schema_variant(item) for item in family_variant_options(strategy_choice)
    }
    if primary_variants and isinstance(workspace.get("variant"), Mapping):
        workspace["variant"]["options"] = [
            option
            for option in workspace["variant"].get("options", [])
            if isinstance(option, Mapping) and option.get("value") in primary_variants
        ]
    errors = st.session_state.get(_ERRORS_KEY)
    if isinstance(errors, Mapping):
        workspace["validation_errors"] = dict(errors.get(draft_key, {}))
    return workspace


def _remember_consumed_intent(intent_id: str) -> None:
    consumed = list(st.session_state.get(_CONSUMED_INTENTS_KEY) or [])
    if intent_id not in consumed:
        consumed.append(intent_id)
    st.session_state[_CONSUMED_INTENTS_KEY] = consumed[-100:]


def _store_draft_result(
    draft_key: str,
    values: Mapping[str, object],
    errors: Mapping[str, str],
) -> None:
    drafts = dict(st.session_state.get(_DRAFTS_KEY) or {})
    drafts[draft_key] = dict(values)
    st.session_state[_DRAFTS_KEY] = drafts
    all_errors = dict(st.session_state.get(_ERRORS_KEY) or {})
    all_errors[draft_key] = dict(errors)
    st.session_state[_ERRORS_KEY] = all_errors


def consume_single_settings_intent(
    intent: object,
    *,
    run_handler: Callable[[dict[str, object], str], object] | None,
    runtime_options: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Validate one React/fallback intent before crossing the execution boundary."""

    if not isinstance(intent, Mapping):
        return {"ok": False, "reason": "invalid_intent"}
    action = str(intent.get("action") or "")
    intent_id = str(intent.get("intent_id") or "")
    if action not in _SETTINGS_ACTIONS or not intent_id:
        return {"ok": False, "reason": "invalid_intent"}
    consumed = list(st.session_state.get(_CONSUMED_INTENTS_KEY) or [])
    if intent_id in consumed:
        return {"ok": False, "duplicate": True}

    current_choice, current_variant = _current_strategy_and_variant()
    requested_choice = str(intent.get("strategy_choice") or "")
    requested_variant = _schema_variant(intent.get("variant"))
    if requested_choice != current_choice:
        return {"ok": False, "reason": "selection_mismatch"}

    if action == "select_strategy_variant":
        allowed = {_schema_variant(item) for item in family_variant_options(current_choice)}
        if requested_variant not in allowed:
            return {"ok": False, "reason": "variant_not_allowed"}
        variant_key = _variant_session_key(current_choice)
        if not variant_key:
            return {"ok": False, "reason": "variant_not_allowed"}
        st.session_state[variant_key] = _ui_variant(requested_variant)
        _remember_consumed_intent(intent_id)
        return {"ok": True, "variant": requested_variant}

    if requested_variant != current_variant:
        return {"ok": False, "reason": "selection_mismatch"}
    if not callable(run_handler):
        return {"ok": False, "reason": "handler_unavailable"}
    values = intent.get("values")
    submitted = dict(values) if isinstance(values, Mapping) else {}
    runtime = dict(runtime_options or build_single_settings_runtime_options())
    workspace = build_single_settings_workspace(
        current_choice,
        current_variant,
        submitted,
        runtime,
    )
    draft_key = str(workspace["draft_key"])
    try:
        payload = project_single_settings_payload(workspace, submitted)
    except SettingsValidationError as exc:
        _store_draft_result(draft_key, submitted, exc.errors)
        _remember_consumed_intent(intent_id)
        return {"ok": False, "errors": dict(exc.errors)}

    _store_draft_result(draft_key, submitted, {})
    _remember_consumed_intent(intent_id)
    strategy_name = resolve_concrete_strategy_display_name(
        current_choice,
        _ui_variant(current_variant),
    )
    result = run_handler(payload, strategy_name)
    return {"ok": True, "payload": payload, "handler_result": result}


def _option_pairs(field: Mapping[str, object]) -> tuple[list[object], dict[object, str]]:
    values: list[object] = []
    labels: dict[object, str] = {}
    for option in field.get("options", []):
        if isinstance(option, Mapping):
            value = option.get("value")
            label = str(option.get("label") or value)
        else:
            value = option
            label = str(option)
        values.append(value)
        labels[value] = label
    return values, labels


def _render_fallback_field(
    field: Mapping[str, object],
    *,
    key_prefix: str,
) -> object:
    field_id = str(field["field_id"])
    label = str(field.get("label") or field_id)
    value = field.get("value")
    help_text = str(field.get("help") or "") or None
    key = f"{key_prefix}:{field_id}"
    control = str(field.get("control") or "")
    if control == "date":
        initial = date.fromisoformat(str(value)) if value else date.today()
        return st.date_input(label, value=initial, key=key, help=help_text).isoformat()
    if control == "number":
        kwargs: dict[str, object] = {"value": value, "key": key, "help": help_text}
        if isinstance(field.get("min"), (int, float)):
            kwargs["min_value"] = field["min"]
        if isinstance(field.get("max"), (int, float)):
            kwargs["max_value"] = field["max"]
        if isinstance(field.get("step"), (int, float)):
            kwargs["step"] = field["step"]
        return st.number_input(label, **kwargs)
    if control == "text":
        return st.text_input(label, value=str(value or ""), key=key, help=help_text)
    if control in {"single_select", "segmented", "multi_select"}:
        options, labels = _option_pairs(field)
        formatter = lambda item: labels.get(item, str(item))
        if control == "multi_select":
            return st.multiselect(label, options, default=list(value or []), format_func=formatter, key=key, help=help_text)
        if control == "segmented":
            return st.segmented_control(label, options, default=value, format_func=formatter, key=key, help=help_text)
        index = options.index(value) if value in options else 0
        return st.selectbox(label, options, index=index, format_func=formatter, key=key, help=help_text)
    if control == "toggle":
        return st.toggle(label, value=bool(value), key=key, help=help_text)
    return value


def render_single_settings_fallback(
    workspace: Mapping[str, object],
    *,
    on_submit: Callable[[dict[str, object]], object] | None = None,
) -> dict[str, object] | None:
    """Render the same read model with native controls when React is unavailable."""

    draft_key = str(workspace.get("draft_key") or "single-settings")
    values = {str(field["field_id"]): field.get("value") for field in _workspace_fields(workspace)}
    with st.form(f"single_settings_fallback:{draft_key}", clear_on_submit=False):
        for section in workspace.get("sections", []):
            if not isinstance(section, Mapping):
                continue
            st.markdown(f"#### {section.get('title') or ''}")
            st.caption(str(section.get("description") or ""))
            for field in section.get("fields", []):
                if not isinstance(field, Mapping):
                    continue
                visible_when = field.get("visible_when")
                if isinstance(visible_when, Mapping) and not all(
                    values.get(str(name)) == expected
                    for name, expected in visible_when.items()
                ):
                    continue
                values[str(field["field_id"])] = _render_fallback_field(
                    field,
                    key_prefix=draft_key,
                )
                error = dict(workspace.get("validation_errors") or {}).get(str(field["field_id"]))
                if error:
                    st.error(str(error))
        submitted = st.form_submit_button(
            str(dict(workspace.get("action") or {}).get("label") or "실행"),
            use_container_width=True,
        )
    if not submitted:
        return None
    if callable(on_submit):
        on_submit(values)
    return {
        "action": "run_single_strategy",
        "strategy_choice": workspace.get("strategy_choice"),
        "variant": dict(workspace.get("variant") or {}).get("value"),
        "values": values,
    }


__all__ = [
    "build_compact_ticker_summary",
    "build_current_single_settings_workspace",
    "build_single_settings_runtime_options",
    "build_single_strategy_settings_summary",
    "consume_single_settings_intent",
    "render_compact_ticker_summary",
    "render_single_settings_fallback",
    "render_single_strategy_settings_header",
    "single_settings_section",
]
