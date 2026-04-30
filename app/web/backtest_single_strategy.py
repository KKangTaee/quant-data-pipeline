from __future__ import annotations

from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_result_display import _render_last_run
from app.web.backtest_single_forms import (
    _render_dual_momentum_form,
    _render_equal_weight_form,
    _render_global_relative_strength_form,
    _render_gtaa_form,
    _render_risk_parity_form,
    _render_single_strategy_family_form,
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
    strategy_choice = st.selectbox(
        "Strategy",
        options=SINGLE_STRATEGY_OPTIONS,
        index=0,
        help="The first Phase 4 UI keeps one strategy form visible at a time.",
        key="backtest_strategy_choice",
    )
    if not family_variant_options(strategy_choice):
        _render_strategy_capability_snapshot(strategy_choice)
    st.divider()
    if strategy_choice == "Equal Weight":
        _render_equal_weight_form()
    elif strategy_choice == "GTAA":
        _render_gtaa_form()
    elif strategy_choice == "Global Relative Strength":
        _render_global_relative_strength_form()
    elif strategy_choice == "Risk Parity Trend":
        _render_risk_parity_form()
    elif strategy_choice == "Dual Momentum":
        _render_dual_momentum_form()
    else:
        _render_single_strategy_family_form(strategy_choice)
    st.divider()
    _render_last_run()

__all__ = ["render_single_strategy_workspace"]
