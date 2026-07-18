from __future__ import annotations

from uuid import uuid4

from app.services.backtest_execution import execute_single_backtest
from app.services.backtest_single_payload import normalize_single_strategy_payload
from app.web.backtest_analysis_workspace import record_single_strategy_draft
from app.web.backtest_common import *  # noqa: F401,F403


def _handle_backtest_run(payload: dict, *, strategy_name: str) -> bool:
    execution_payload = normalize_single_strategy_payload(payload, strategy_name=strategy_name)
    fingerprint = record_single_strategy_draft(
        execution_payload,
        strategy_name=strategy_name,
    )

    spinner_text = f"Running {strategy_name} backtest from DB..."
    with st.spinner(spinner_text, show_time=True):
        result = execute_single_backtest(execution_payload, strategy_name=strategy_name)

    if not result.ok:
        st.session_state.backtest_last_error_kind = result.error_kind
        st.session_state.backtest_last_error = result.error_message
        return False

    if result.bundle is None:
        st.session_state.backtest_last_error_kind = "system"
        st.session_state.backtest_last_error = "Backtest execution failed: missing result bundle."
        return False

    bundle = dict(result.bundle)
    bundle["meta"] = dict(bundle.get("meta") or {})
    bundle["meta"].setdefault("run_id", f"level1-{uuid4().hex}")
    bundle["meta"]["level1_configuration_fingerprint"] = fingerprint
    st.session_state.backtest_last_configuration_fingerprint = fingerprint
    st.session_state.backtest_last_bundle = bundle
    st.session_state.backtest_last_error = None
    st.session_state.backtest_last_error_kind = None
    st.session_state.backtest_last_result_requires_rerun = False
    st.session_state.backtest_last_result_refresh_result = None
    append_backtest_run_history(
        bundle=bundle,
        run_kind="single_strategy",
        context={"level1_configuration_fingerprint": fingerprint},
    )
    st.success(f"{strategy_name} backtest execution completed in {result.elapsed_seconds:.3f}s.")
    return True


__all__ = ["_handle_backtest_run"]
