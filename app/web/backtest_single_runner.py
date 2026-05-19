from __future__ import annotations

from app.services.backtest_execution import execute_single_backtest
from app.web.backtest_common import *  # noqa: F401,F403


def _handle_backtest_run(payload: dict, *, strategy_name: str) -> bool:
    st.markdown("#### Runtime Payload")
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
