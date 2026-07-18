from __future__ import annotations

from functools import partial
from uuid import uuid4

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_result_display import _render_last_run
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.components.backtest_analysis_decision_workspace import (
    is_backtest_analysis_decision_workspace_available,
    render_backtest_analysis_decision_workspace,
)
from app.web.backtest_single_settings_workspace import (
    build_current_single_settings_workspace,
    build_single_settings_runtime_options,
    consume_single_settings_intent,
    render_single_settings_fallback,
)


def _last_run_matches_strategy_selection(
    bundle: dict | None,
    strategy_choice: str | None,
    selected_variant: str | None = None,
) -> bool:
    """Return whether the last result bundle belongs to the currently selected strategy."""
    if not bundle:
        return True
    meta = dict(bundle.get("meta") or {})
    bundle_choice, bundle_variant = strategy_key_to_selection(meta.get("strategy_key"))
    if not bundle_choice:
        bundle_choice, bundle_variant = display_name_to_selection(
            bundle.get("strategy_name") or meta.get("strategy_name")
        )
    if bundle_choice != strategy_choice:
        return False
    if selected_variant is not None:
        return bundle_variant == selected_variant
    return True


def _selected_strategy_variant(strategy_choice: str | None) -> str | None:
    variant_key = _single_family_variant_session_key(strategy_choice)
    if not variant_key:
        return None
    value = st.session_state.get(variant_key)
    return str(value) if value else None


def _selection_signature(strategy_choice: str | None, selected_variant: str | None) -> str:
    return f"{strategy_choice or '-'}::{selected_variant or '-'}"


def _mark_last_run_stale_if_strategy_selection_changed(
    strategy_choice: str | None,
    selected_variant: str | None = None,
) -> None:
    bundle = st.session_state.get("backtest_last_bundle")
    current_signature = _selection_signature(strategy_choice, selected_variant)
    previous_signature = st.session_state.get("backtest_last_strategy_selection_signature")
    should_mark_stale = bool(bundle) and (
        not _last_run_matches_strategy_selection(bundle, strategy_choice, selected_variant)
        or (previous_signature is not None and previous_signature != current_signature)
    )
    if should_mark_stale:
        st.session_state.backtest_last_error = None
        st.session_state.backtest_last_error_kind = None
        st.session_state.backtest_last_result_requires_rerun = True
        st.session_state.backtest_last_result_refresh_result = None
        st.session_state.backtest_last_result_reset_notice = (
            "현재 선택이 이전 실행과 달라 기존 결과를 참고용으로 유지합니다. "
            "현재 설정으로 다시 실행해야 Level2 전송이 열립니다."
        )
    st.session_state.backtest_last_strategy_selection_signature = current_signature


def _run_single_settings_payload(payload: dict, strategy_name: str) -> bool:
    st.session_state.backtest_pending_single_run = {
        "payload": dict(payload),
        "strategy_name": str(strategy_name),
    }
    return True


def _consume_single_settings_component_change(
    *,
    component_key: str,
    runtime_options: dict[str, object],
) -> None:
    intent = st.session_state.get(component_key)
    consume_single_settings_intent(
        intent if isinstance(intent, dict) else None,
        run_handler=_run_single_settings_payload,
        runtime_options=runtime_options,
    )


def _render_single_settings_surface(
    *,
    selected_variant: str | None,
) -> None:
    runtime_options = build_single_settings_runtime_options()
    workspace = build_current_single_settings_workspace(
        selected_variant=selected_variant,
        runtime_options=runtime_options,
    )
    component_key = (
        "backtest-analysis-single-settings-"
        f"{str(workspace.get('draft_key') or 'current')}"
    )
    intent = None
    if is_backtest_analysis_decision_workspace_available():
        try:
            intent = render_backtest_analysis_decision_workspace(
                workspace=workspace,
                surface="settings",
                key=component_key,
                on_change=partial(
                    _consume_single_settings_component_change,
                    component_key=component_key,
                    runtime_options=runtime_options,
                ),
            )
        except Exception as exc:  # component availability must not block execution
            st.warning(
                "React 설정 화면을 열지 못해 같은 설정 계약의 기본 화면으로 전환했습니다. "
                f"({exc})"
            )
            render_single_settings_fallback(
                workspace,
                on_submit=lambda values: consume_single_settings_intent(
                    {
                        "action": "run_single_strategy",
                        "intent_id": f"fallback-{uuid4()}",
                        "strategy_choice": workspace["strategy_choice"],
                        "variant": dict(workspace.get("variant") or {}).get("value"),
                        "values": values,
                    },
                    run_handler=_run_single_settings_payload,
                    runtime_options=runtime_options,
                ),
            )
    else:
        render_single_settings_fallback(
            workspace,
            on_submit=lambda values: consume_single_settings_intent(
                {
                    "action": "run_single_strategy",
                    "intent_id": f"fallback-{uuid4()}",
                    "strategy_choice": workspace["strategy_choice"],
                    "variant": dict(workspace.get("variant") or {}).get("value"),
                    "values": values,
                },
                run_handler=_run_single_settings_payload,
                runtime_options=runtime_options,
            ),
        )
    consume_single_settings_intent(
        intent,
        run_handler=_run_single_settings_payload,
        runtime_options=runtime_options,
    )


# Render and operate the Single Strategy workspace.
def render_single_strategy_workspace() -> None:
    prefill_notice = st.session_state.get("backtest_prefill_notice")
    if prefill_notice:
        st.info(prefill_notice)
        prefill_lines = _build_prefill_summary_lines(st.session_state.get("backtest_prefill_payload"))
        if prefill_lines:
            st.caption("이번에 불러온 입력값 요약")
            st.markdown("\n".join(f"- {line}" for line in prefill_lines))
        st.caption(
            "참고: `Load Into Form`은 입력값만 불러옵니다. "
            "아래 form에서 다시 실행해야 `Latest Backtest Run`과 `Selection History Table`이 이 입력값 기준으로 갱신됩니다."
        )
        prefill_action_cols = st.columns([0.22, 0.78], gap="small")
        with prefill_action_cols[0]:
            st.caption("History는 `Operations > Backtest Run History`에서 다시 열 수 있습니다.")
        st.session_state.backtest_prefill_notice = None
    pending_strategy_choice = st.session_state.get("backtest_prefill_strategy_choice")
    pending_strategy_variant = st.session_state.get("backtest_prefill_strategy_variant")
    if pending_strategy_choice not in SINGLE_STRATEGY_OPTIONS:
        remapped_choice, remapped_variant = display_name_to_selection(pending_strategy_choice)
        if remapped_choice in SINGLE_STRATEGY_OPTIONS:
            pending_strategy_choice = remapped_choice
            pending_strategy_variant = pending_strategy_variant or remapped_variant
    if pending_strategy_choice in SINGLE_STRATEGY_OPTIONS:
        st.session_state.backtest_strategy_choice = pending_strategy_choice
        variant_key = _single_family_variant_session_key(pending_strategy_choice)
        if variant_key and pending_strategy_variant in family_variant_options(pending_strategy_choice):
            st.session_state[variant_key] = pending_strategy_variant
        st.session_state.backtest_prefill_strategy_choice = None
        st.session_state.backtest_prefill_strategy_variant = None
    current_strategy_choice = st.session_state.get("backtest_strategy_choice")
    if current_strategy_choice not in SINGLE_STRATEGY_OPTIONS:
        remapped_choice, remapped_variant = display_name_to_selection(current_strategy_choice)
        if remapped_choice in SINGLE_STRATEGY_OPTIONS:
            st.session_state.backtest_strategy_choice = remapped_choice
            variant_key = _single_family_variant_session_key(remapped_choice)
            if variant_key and remapped_variant in family_variant_options(remapped_choice):
                st.session_state[variant_key] = remapped_variant
    strategy_choice = str(
        st.session_state.get(
            "backtest_strategy_choice",
            DEFAULT_SINGLE_STRATEGY_OPTION,
        )
    )
    if strategy_choice not in SINGLE_STRATEGY_OPTIONS:
        strategy_choice = DEFAULT_SINGLE_STRATEGY_OPTION
        st.session_state.backtest_strategy_choice = strategy_choice

    selected_variant = _selected_strategy_variant(strategy_choice)
    variant_key = _single_family_variant_session_key(strategy_choice)
    variant_options = family_variant_options(strategy_choice)
    if variant_key and selected_variant not in variant_options:
        selected_variant = variant_options[0]
        st.session_state[variant_key] = selected_variant
    _render_single_settings_surface(selected_variant=selected_variant)
    st.session_state.backtest_prefill_pending = False
    st.divider()
    selected_variant = selected_variant or _selected_strategy_variant(strategy_choice)
    _mark_last_run_stale_if_strategy_selection_changed(strategy_choice, selected_variant)
    reset_notice = st.session_state.get("backtest_last_result_reset_notice")
    if reset_notice:
        st.info(str(reset_notice))
        st.session_state.backtest_last_result_reset_notice = None
    pending = st.session_state.get("backtest_pending_single_run")
    _render_last_run(is_running=bool(pending))
    if isinstance(pending, dict):
        try:
            _handle_backtest_run(
                dict(pending["payload"]),
                strategy_name=str(pending["strategy_name"]),
            )
        finally:
            st.session_state.pop("backtest_pending_single_run", None)
        st.rerun(scope="fragment")

__all__ = ["render_single_strategy_workspace"]
