from __future__ import annotations

from typing import Any

from app.services.backtest_execution import execute_single_backtest
from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_ui_components import render_badge_strip


def _payload_badges(payload: dict[str, Any], *, strategy_name: str) -> list[dict[str, Any]]:
    tickers = payload.get("tickers") or payload.get("dynamic_candidate_tickers") or []
    ticker_count = len(tickers) if isinstance(tickers, list) else None
    period = f"{payload.get('start') or '-'} -> {payload.get('end') or '-'}"
    cadence = payload.get("option") or payload.get("timeframe") or "-"
    top = payload.get("top")
    asset_label = str(ticker_count) if ticker_count is not None else "-"
    if top is not None:
        asset_label = f"{asset_label} / top {top}"
    return [
        {"label": "Strategy", "value": strategy_name, "tone": "neutral"},
        {"label": "Period", "value": period, "tone": "neutral"},
        {"label": "Assets", "value": asset_label, "tone": "positive" if ticker_count else "warning"},
        {"label": "Cadence", "value": cadence, "tone": "neutral"},
        {"label": "Preset", "value": payload.get("preset_name") or payload.get("universe_mode") or "-", "tone": "neutral"},
    ]


def _handle_backtest_run(payload: dict, *, strategy_name: str) -> bool:
    st.markdown("#### Execution Summary")
    render_badge_strip(_payload_badges(payload, strategy_name=strategy_name))
    with st.expander("Developer Payload", expanded=False):
        st.caption("실행 service에 전달되는 원본 payload입니다. 일반 결과 확인 중에는 접어두어도 됩니다.")
        st.json(payload)

    spinner_text = f"Running {strategy_name} backtest from DB..."
    with st.spinner(spinner_text):
        result = execute_single_backtest(payload, strategy_name=strategy_name)

    if not result.ok:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = result.error_kind
        st.session_state.backtest_last_error = result.error_message
        return False

    if result.bundle is None:
        st.session_state.backtest_last_bundle = None
        st.session_state.backtest_last_error_kind = "system"
        st.session_state.backtest_last_error = "Backtest execution failed: missing result bundle."
        return False

    bundle = result.bundle
    st.session_state.backtest_last_bundle = bundle
    st.session_state.backtest_last_error = None
    st.session_state.backtest_last_error_kind = None
    append_backtest_run_history(bundle=bundle, run_kind="single_strategy")
    st.success(f"{strategy_name} backtest execution completed in {result.elapsed_seconds:.3f}s.")
    return True


__all__ = ["_handle_backtest_run"]
