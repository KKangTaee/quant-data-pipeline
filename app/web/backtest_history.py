from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from app.web.runtime import BACKTEST_HISTORY_FILE, load_backtest_run_history
from app.web.backtest_common import _set_single_strategy_target_from_strategy_key
from app.web.backtest_single_runner import _handle_backtest_run
from app.web.backtest_candidate_review_helpers import (
    _candidate_review_draft_from_history_record,
    _queue_candidate_review_draft,
)
from app.web.backtest_history_helpers import (
    _build_backtest_history_rows,
    _build_history_payload,
    _build_history_replay_parity_rows,
    _build_real_money_guardrail_parity_rows,
    _format_history_record_label,
    _history_strategy_display_name,
    _normalize_recorded_date_range,
    _strategy_key_to_display_name,
)
from app.web.backtest_strategy_catalog import strategy_key_to_selection

SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS = {
    "quality_snapshot",
    "quality_snapshot_strict_annual",
    "quality_snapshot_strict_quarterly_prototype",
    "value_snapshot_strict_annual",
    "value_snapshot_strict_quarterly_prototype",
    "quality_value_snapshot_strict_annual",
    "quality_value_snapshot_strict_quarterly_prototype",
}


# Build a compact family / variant label for History -> Single Strategy prefill notices.
def _family_strategy_summary_label(strategy_key: str | None) -> str | None:
    family_name, variant_name = strategy_key_to_selection(strategy_key)
    if family_name is None:
        return None
    if variant_name:
        return f"{family_name} / {variant_name}"
    return family_name


# Render the shared Real-Money / Guardrail scope table inside History-owned surfaces.
def _render_real_money_guardrail_parity_snapshot(
    items: list[dict[str, Any]],
    *,
    title: str = "Real-Money / Guardrail Scope Snapshot",
    caption: str | None = None,
) -> None:
    df = _build_real_money_guardrail_parity_rows(items)
    if df.empty:
        return

    st.markdown(f"#### {title}")
    st.caption(
        caption
        or "이 표는 전략별 Real-Money와 Guardrail 지원 범위를 같은 언어로 보여줍니다. 모든 전략에 같은 실전 검증을 강제로 붙였다는 뜻은 아닙니다."
    )
    st.dataframe(df, use_container_width=True, hide_index=True)


# Show which History fields are sufficient for load / replay parity.
def _render_history_replay_parity_snapshot(record: dict[str, Any]) -> None:
    payload = _build_history_payload(record)
    if payload is None:
        return

    rows = _build_history_replay_parity_rows(record)
    if not rows:
        return

    st.markdown("#### History Replay / Load Parity Snapshot")
    st.caption(
        "이 표는 선택한 저장 기록을 `Load Into Form` 또는 `Run Again`으로 다시 열 때 "
        "어떤 핵심 설정이 history에 남아 있는지 확인하는 표입니다. "
        "`누락 가능`이 보이면 그 항목은 기본값으로 돌아갈 수 있으므로 Raw Record나 form 복원 결과를 같이 봅니다."
    )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    _render_real_money_guardrail_parity_snapshot(
        [
            {
                "strategy_name": _strategy_key_to_display_name(record.get("strategy_key")),
                "strategy_key": record.get("strategy_key"),
                "data": record,
            }
        ],
        title="History Real-Money / Guardrail Scope",
        caption=(
            "이 저장 기록이 annual strict 실전 검증 기록인지, quarterly prototype 기록인지, "
            "또는 ETF first-pass 기록인지 구분합니다."
        ),
    )


# Queue a persisted History record as a Single Strategy form prefill.
def _load_history_into_form(record: dict[str, Any]) -> bool:
    payload = _build_history_payload(record)
    strategy_key = record.get("strategy_key")
    strategy_name = _strategy_key_to_display_name(strategy_key)
    strategy_choice, strategy_variant = strategy_key_to_selection(strategy_key)
    if payload is None or strategy_name is None or strategy_choice is None:
        return False

    st.session_state.backtest_prefill_payload = payload
    st.session_state.backtest_prefill_pending = True
    st.session_state.backtest_prefill_notice = (
        f"히스토리에서 `{_family_strategy_summary_label(strategy_key) or strategy_name}` 입력값을 불러왔습니다."
    )
    st.session_state.backtest_prefill_strategy_choice = strategy_choice
    st.session_state.backtest_prefill_strategy_variant = strategy_variant
    st.session_state.backtest_requested_panel = "Single Strategy"
    return True


# Render the persisted Backtest history inspector and replay actions.
def _render_persistent_backtest_history(*, open_backtest_page=None) -> None:
    st.markdown("### Persistent Backtest History")
    st.info(
        "여기서 말하는 `history run`은 예전에 저장된 백테스트 실행 기록 1건입니다. "
        "먼저 아래 목록에서 기록 1개를 고른 뒤, `Saved Run Summary`와 `Saved Input & Context`를 보고, "
        "필요하면 `Run Again` 또는 `Load Into Form`으로 다시 열어 확인합니다."
    )
    history = load_backtest_run_history(limit=100)
    if not history:
        st.info("No persisted backtest history found yet.")
        return

    st.caption(f"Path: {BACKTEST_HISTORY_FILE}")
    history_df, history_records = _build_backtest_history_rows(history)

    filter_col, search_col = st.columns([1.1, 1.4], gap="large")
    with filter_col:
        selected_run_kinds = st.multiselect(
            "Run Kind Filter",
            options=sorted(history_df["run_kind"].dropna().unique().tolist()),
            default=sorted(history_df["run_kind"].dropna().unique().tolist()),
            key="backtest_history_run_kind_filter",
        )
    with search_col:
        search_text = st.text_input(
            "Search",
            value="",
            placeholder="strategy, ticker, preset, selected strategies",
            key="backtest_history_search_text",
        ).strip().lower()

    date_filter_col, sort_filter_col = st.columns([1.2, 1.0], gap="large")
    recorded_dates = pd.to_datetime(history_df["recorded_at"], errors="coerce")
    min_recorded_date = recorded_dates.min().date() if not recorded_dates.isna().all() else date.today()
    max_recorded_date = recorded_dates.max().date() if not recorded_dates.isna().all() else date.today()
    with date_filter_col:
        recorded_range = st.date_input(
            "Recorded Date Range",
            value=(min_recorded_date, max_recorded_date),
            min_value=min_recorded_date,
            max_value=max_recorded_date,
            key="backtest_history_recorded_range",
        )
    with sort_filter_col:
        sort_by = st.selectbox(
            "Sort",
            options=[
                "Recorded At (Newest)",
                "Recorded At (Oldest)",
                "End Balance (High)",
                "CAGR (High)",
                "Sharpe Ratio (High)",
                "Drawdown (Best)",
            ],
            index=0,
            key="backtest_history_sort_by",
        )

    with st.expander("Metric Threshold Filters", expanded=False):
        threshold_cols = st.columns(4, gap="large")
        with threshold_cols[0]:
            use_min_end_balance = st.checkbox("Min End Balance", value=False, key="history_filter_use_end_balance")
            min_end_balance = st.number_input(
                "Threshold",
                min_value=0.0,
                value=10000.0,
                step=1000.0,
                key="history_filter_min_end_balance",
                disabled=not use_min_end_balance,
            )
        with threshold_cols[1]:
            use_min_cagr = st.checkbox("Min CAGR", value=False, key="history_filter_use_cagr")
            min_cagr = st.number_input(
                "Threshold ",
                value=0.0,
                step=0.01,
                format="%.4f",
                key="history_filter_min_cagr",
                disabled=not use_min_cagr,
            )
        with threshold_cols[2]:
            use_min_sharpe = st.checkbox("Min Sharpe Ratio", value=False, key="history_filter_use_sharpe")
            min_sharpe = st.number_input(
                "Threshold  ",
                value=0.0,
                step=0.1,
                format="%.4f",
                key="history_filter_min_sharpe",
                disabled=not use_min_sharpe,
            )
        with threshold_cols[3]:
            use_max_drawdown = st.checkbox("Max Drawdown", value=False, key="history_filter_use_drawdown")
            max_drawdown = st.number_input(
                "Threshold   ",
                value=-0.20,
                step=0.01,
                format="%.4f",
                key="history_filter_max_drawdown",
                disabled=not use_max_drawdown,
            )

    recorded_start, recorded_end = _normalize_recorded_date_range(
        recorded_range,
        fallback_start=min_recorded_date,
        fallback_end=max_recorded_date,
    )

    filtered_indices = []
    for idx, row in history_df.iterrows():
        if selected_run_kinds and row["run_kind"] not in selected_run_kinds:
            continue
        if search_text and search_text not in str(row["_search_text"]):
            continue
        row_recorded_at = pd.to_datetime(row["recorded_at"], errors="coerce")
        if pd.notna(row_recorded_at):
            row_date = row_recorded_at.date()
            if row_date < recorded_start or row_date > recorded_end:
                continue
        if use_min_end_balance and (
            pd.isna(row["end_balance"]) or float(row["end_balance"]) < float(min_end_balance)
        ):
            continue
        if use_min_cagr and (
            pd.isna(row["cagr"]) or float(row["cagr"]) < float(min_cagr)
        ):
            continue
        if use_min_sharpe and (
            pd.isna(row["sharpe_ratio"]) or float(row["sharpe_ratio"]) < float(min_sharpe)
        ):
            continue
        if use_max_drawdown and (
            pd.isna(row["drawdown"]) or float(row["drawdown"]) < float(max_drawdown)
        ):
            continue
        filtered_indices.append(idx)

    filtered_df = history_df.loc[filtered_indices].copy()
    filtered_records = [history_records[idx] for idx in filtered_indices]

    if filtered_df.empty:
        st.info("No history records matched the current filter.")
        return

    sort_column = "_recorded_at_dt"
    ascending = False
    na_position = "last"
    if sort_by == "Recorded At (Oldest)":
        ascending = True
    elif sort_by == "End Balance (High)":
        sort_column = "end_balance"
    elif sort_by == "CAGR (High)":
        sort_column = "cagr"
    elif sort_by == "Sharpe Ratio (High)":
        sort_column = "sharpe_ratio"
    elif sort_by == "Drawdown (Best)":
        sort_column = "drawdown"
        ascending = False

    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending, na_position=na_position).reset_index(drop=True)
    filtered_records = [history_records[int(idx)] for idx in filtered_df["_record_index"].tolist()]

    display_df = filtered_df.drop(columns=["_search_text", "_record_index", "_recorded_at_dt"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("#### Selected History Run")
    selected_label = st.selectbox(
        "Inspect Record",
        options=[_format_history_record_label(record) for record in filtered_records],
        index=0,
        key="backtest_history_selected_record",
    )
    selected_record = filtered_records[
        [_format_history_record_label(record) for record in filtered_records].index(selected_label)
    ]

    summary = selected_record.get("summary") or {}
    context = selected_record.get("context") or {}
    if selected_record.get("strategy_key") in SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS:
        st.caption(
            "이 저장 기록은 compact summary 중심이라 `Selection History Table`과 `Interpretation Summary` 전체 표를 그대로 담고 있지는 않습니다. "
            "이 전략의 행별 선택 기록과 해석을 다시 보려면 아래 `Run Again` 또는 `Load Into Form`을 사용한 뒤, "
            "새로 열린 결과의 `Selection History Table` 탭을 확인하면 됩니다."
        )

    detail_tabs = st.tabs(["Saved Run Summary", "Saved Input & Context", "Raw Record"])

    with detail_tabs[0]:
        if summary:
            st.dataframe(pd.DataFrame([summary]), use_container_width=True, hide_index=True)
        elif selected_record.get("run_kind") == "strategy_compare":
            compare_summary_rows = context.get("strategy_summaries") or []
            if compare_summary_rows:
                st.caption("Compare records keep per-strategy summary rows instead of one primary summary row.")
                st.dataframe(pd.DataFrame(compare_summary_rows), use_container_width=True, hide_index=True)
            else:
                st.info("This compare history record does not include stored per-strategy summary rows. Older compare records may only keep the selected strategy list.")
        else:
            st.info("This history record does not include a primary summary row.")

    with detail_tabs[1]:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("##### Input")
            st.json(
                {
                    "run_kind": selected_record.get("run_kind"),
                    "strategy_key": selected_record.get("strategy_key"),
                    "tickers": selected_record.get("tickers", []),
                    "start": selected_record.get("input_start"),
                    "end": selected_record.get("input_end"),
                    "timeframe": selected_record.get("timeframe"),
                    "option": selected_record.get("option"),
                    "rebalance_interval": selected_record.get("rebalance_interval"),
                    "top": selected_record.get("top"),
                    "cash_ticker": selected_record.get("cash_ticker"),
                    "vol_window": selected_record.get("vol_window"),
                    "result_rows": selected_record.get("result_rows"),
                    "actual_result_start": selected_record.get("actual_result_start"),
                    "actual_result_end": selected_record.get("actual_result_end"),
                    "factor_freq": selected_record.get("factor_freq"),
                    "rebalance_freq": selected_record.get("rebalance_freq"),
                    "snapshot_mode": selected_record.get("snapshot_mode"),
                    "quality_factors": selected_record.get("quality_factors"),
                    "value_factors": selected_record.get("value_factors"),
                    "score_lookback_months": selected_record.get("score_lookback_months"),
                    "score_return_columns": selected_record.get("score_return_columns"),
                    "score_weights": selected_record.get("score_weights"),
                    "trend_filter_enabled": selected_record.get("trend_filter_enabled"),
                    "trend_filter_window": selected_record.get("trend_filter_window"),
                    "weighting_mode": selected_record.get("weighting_mode"),
                    "rejected_slot_handling_mode": selected_record.get("rejected_slot_handling_mode"),
                    "rejected_slot_fill_enabled": selected_record.get("rejected_slot_fill_enabled"),
                    "partial_cash_retention_enabled": selected_record.get("partial_cash_retention_enabled"),
                    "risk_off_mode": selected_record.get("risk_off_mode"),
                    "defensive_tickers": selected_record.get("defensive_tickers"),
                    "market_regime_enabled": selected_record.get("market_regime_enabled"),
                    "market_regime_window": selected_record.get("market_regime_window"),
                    "market_regime_benchmark": selected_record.get("market_regime_benchmark"),
                    "crash_guardrail_enabled": selected_record.get("crash_guardrail_enabled"),
                    "crash_guardrail_drawdown_threshold": selected_record.get("crash_guardrail_drawdown_threshold"),
                    "crash_guardrail_lookback_months": selected_record.get("crash_guardrail_lookback_months"),
                    "underperformance_guardrail_enabled": selected_record.get("underperformance_guardrail_enabled"),
                    "underperformance_guardrail_window_months": selected_record.get("underperformance_guardrail_window_months"),
                    "underperformance_guardrail_threshold": selected_record.get("underperformance_guardrail_threshold"),
                    "drawdown_guardrail_enabled": selected_record.get("drawdown_guardrail_enabled"),
                    "drawdown_guardrail_window_months": selected_record.get("drawdown_guardrail_window_months"),
                    "drawdown_guardrail_strategy_threshold": selected_record.get("drawdown_guardrail_strategy_threshold"),
                    "drawdown_guardrail_gap_threshold": selected_record.get("drawdown_guardrail_gap_threshold"),
                    "benchmark_contract": selected_record.get("benchmark_contract"),
                    "benchmark_ticker": selected_record.get("benchmark_ticker"),
                    "guardrail_reference_ticker": selected_record.get("guardrail_reference_ticker"),
                    "min_price_filter": selected_record.get("min_price_filter"),
                    "min_history_months_filter": selected_record.get("min_history_months_filter"),
                    "min_avg_dollar_volume_20d_m_filter": selected_record.get("min_avg_dollar_volume_20d_m_filter"),
                    "transaction_cost_bps": selected_record.get("transaction_cost_bps"),
                    "snapshot_source": selected_record.get("snapshot_source"),
                    "universe_contract": selected_record.get("universe_contract"),
                    "dynamic_target_size": selected_record.get("dynamic_target_size"),
                    "requested_tickers": selected_record.get("requested_tickers"),
                    "excluded_tickers": selected_record.get("excluded_tickers"),
                    "malformed_price_rows": selected_record.get("malformed_price_rows"),
                    "price_freshness": selected_record.get("price_freshness"),
                    "ui_elapsed_seconds": selected_record.get("ui_elapsed_seconds"),
                    "universe_mode": selected_record.get("universe_mode"),
                    "preset_name": selected_record.get("preset_name"),
                }
            )
        with right:
            st.markdown("##### Context")
            gate_snapshot = selected_record.get("gate_snapshot") or {}
            if gate_snapshot:
                st.caption(
                    "Schema v2 history record는 실행 시점의 real-money gate snapshot을 같이 남깁니다. "
                    "이 값으로 이후 blocker audit이나 candidate review를 더 빠르게 다시 읽을 수 있습니다."
                )
                gate_rows = [
                    {"항목": "Promotion", "상태": gate_snapshot.get("promotion_decision"), "다음 단계": gate_snapshot.get("promotion_next_step")},
                    {"항목": "Shortlist", "상태": gate_snapshot.get("shortlist_status"), "다음 단계": gate_snapshot.get("shortlist_next_step")},
                    {"항목": "Probation", "상태": gate_snapshot.get("probation_status"), "다음 단계": gate_snapshot.get("probation_next_step")},
                    {"항목": "Monitoring", "상태": gate_snapshot.get("monitoring_status"), "다음 단계": gate_snapshot.get("monitoring_next_step")},
                    {
                        "항목": "Deployment",
                        "상태": gate_snapshot.get("deployment_readiness_status"),
                        "다음 단계": gate_snapshot.get("deployment_readiness_next_step"),
                    },
                    {"항목": "Validation", "상태": gate_snapshot.get("validation_status"), "다음 단계": None},
                    {"항목": "Benchmark Policy", "상태": gate_snapshot.get("benchmark_policy_status"), "다음 단계": None},
                    {"항목": "Liquidity Policy", "상태": gate_snapshot.get("liquidity_policy_status"), "다음 단계": None},
                    {"항목": "Validation Policy", "상태": gate_snapshot.get("validation_policy_status"), "다음 단계": None},
                    {"항목": "Guardrail Policy", "상태": gate_snapshot.get("guardrail_policy_status"), "다음 단계": None},
                    {"항목": "ETF Operability", "상태": gate_snapshot.get("etf_operability_status"), "다음 단계": None},
                    {"항목": "Rolling Review", "상태": gate_snapshot.get("rolling_review_status"), "다음 단계": None},
                    {"항목": "Out-Of-Sample Review", "상태": gate_snapshot.get("out_of_sample_review_status"), "다음 단계": None},
                    {"항목": "Price Freshness", "상태": gate_snapshot.get("price_freshness_status"), "다음 단계": None},
                ]
                gate_df = pd.DataFrame(gate_rows).dropna(how="all")
                gate_df = gate_df[gate_df["상태"].notna() | gate_df["다음 단계"].notna()]
                if not gate_df.empty:
                    st.dataframe(gate_df, use_container_width=True, hide_index=True)
            if selected_record.get("run_kind") == "strategy_compare":
                compare_overrides = context.get("strategy_overrides") or {}
                if compare_overrides:
                    override_rows = []
                    for strategy_name, overrides in compare_overrides.items():
                        override_rows.append(
                            {
                                "Strategy": strategy_name,
                                "Preset": overrides.get("preset_name"),
                                "Top N": overrides.get("top_n"),
                                "Rebalance Interval": overrides.get("rebalance_interval"),
                                "Trend Filter": overrides.get("trend_filter_enabled"),
                                "Trend Window": overrides.get("trend_filter_window"),
                                "Weighting": overrides.get("weighting_mode"),
                                "Rejected Slot Handling": overrides.get("rejected_slot_handling_mode"),
                                "Slot Fill": overrides.get("rejected_slot_fill_enabled"),
                                "Cash Retention": overrides.get("partial_cash_retention_enabled"),
                                "Market Regime": overrides.get("market_regime_enabled"),
                                "Regime Window": overrides.get("market_regime_window"),
                                "Regime Benchmark": overrides.get("market_regime_benchmark"),
                            }
                        )
                    st.caption(
                        "Compare 기록은 전략별 override가 context에 저장됩니다. "
                        "아래 표에서 trend/regime과 portfolio handling contract 설정을 바로 확인할 수 있습니다."
                    )
                    st.dataframe(pd.DataFrame(override_rows), use_container_width=True, hide_index=True)
                strategy_data_trust_rows = context.get("strategy_data_trust_rows") or []
                if strategy_data_trust_rows:
                    st.caption(
                        "Compare 기록에는 전략별 Data Trust Snapshot도 저장됩니다. "
                        "요청 종료일, 실제 결과 종료일, 가격 최신성, excluded/malformed ticker를 다시 확인할 수 있습니다."
                    )
                    st.dataframe(pd.DataFrame(strategy_data_trust_rows), use_container_width=True, hide_index=True)
            component_data_trust_rows = context.get("component_data_trust_rows") or []
            if component_data_trust_rows:
                st.caption(
                    "Weighted portfolio 기록에는 구성 전략별 Data Trust Snapshot이 같이 저장됩니다. "
                    "포트폴리오 조합 결과를 해석하기 전에 각 component의 데이터 상태를 다시 봅니다."
                )
                st.dataframe(pd.DataFrame(component_data_trust_rows), use_container_width=True, hide_index=True)
            dynamic_universe_preview_rows = context.get("dynamic_universe_preview_rows") or []
            if dynamic_universe_preview_rows:
                st.caption(
                    "`dynamic_universe_preview_rows`는 history에 같이 저장되는 날짜별 모집군 미리보기입니다. "
                    "각 행은 리밸런싱 날짜 1개이며, membership / continuity / profile 관련 count를 빠르게 다시 확인할 때 씁니다."
                )
                st.dataframe(pd.DataFrame(dynamic_universe_preview_rows), use_container_width=True, hide_index=True)
            dynamic_universe_artifact = context.get("dynamic_universe_artifact") or {}
            if dynamic_universe_artifact:
                st.caption(
                    "`dynamic_universe_artifact`는 dynamic universe 상세를 별도 JSON 파일로 저장한 산출물입니다. "
                    "`artifact_dir`는 저장 폴더, `snapshot_json`은 실제 JSON 파일 경로입니다."
                )
                artifact_cols = st.columns(2)
                with artifact_cols[0]:
                    st.markdown(f"- `artifact_dir`: `{dynamic_universe_artifact.get('artifact_dir', '-')}`")
                    st.markdown(f"- `snapshot_json`: `{dynamic_universe_artifact.get('snapshot_json', '-')}`")
                with artifact_cols[1]:
                    st.markdown(f"- `snapshot_row_count`: `{dynamic_universe_artifact.get('snapshot_row_count', '-')}`")
                    st.markdown(f"- `candidate_status_row_count`: `{dynamic_universe_artifact.get('candidate_status_row_count', '-')}`")
                st.json(dynamic_universe_artifact)
            if context.get("saved_portfolio_name") or context.get("saved_portfolio_id"):
                st.caption(
                    "이 run은 저장된 포트폴리오에서 다시 실행된 결과입니다. "
                    "아래 값으로 history run과 saved portfolio definition을 연결할 수 있습니다."
                )
                st.json(
                    {
                        "saved_portfolio_name": context.get("saved_portfolio_name"),
                        "saved_portfolio_id": context.get("saved_portfolio_id"),
                    }
                )
            st.json(context or {"context": None})

    with detail_tabs[2]:
        st.json(selected_record)

    _render_history_replay_parity_snapshot(selected_record)

    st.markdown("#### Actions For This History Run")
    payload = _build_history_payload(selected_record)
    if payload is None:
        st.caption("This record type is not rerunnable yet. `Run Again` and `Load Into Form` are currently supported for single-strategy records only.")
        return

    action_cols = st.columns([0.18, 0.18, 0.24, 0.40], gap="small")
    with action_cols[0]:
        if st.button("Load Into Form", key="backtest_history_load_into_form", width="stretch"):
            if _load_history_into_form(selected_record):
                if open_backtest_page is not None:
                    open_backtest_page()
                st.rerun()
    with action_cols[1]:
        if st.button("Run Again", key="backtest_history_run_again", width="stretch"):
            rerun_ok = _handle_backtest_run(payload, strategy_name=_history_strategy_display_name(selected_record))
            if rerun_ok:
                _set_single_strategy_target_from_strategy_key(selected_record.get("strategy_key"))
                st.session_state.backtest_requested_panel = "Single Strategy"
                if open_backtest_page is not None:
                    open_backtest_page()
                st.rerun()
    with action_cols[2]:
        if st.button("Review As Candidate Draft", key="backtest_history_candidate_review_draft", width="stretch"):
            _queue_candidate_review_draft(_candidate_review_draft_from_history_record(selected_record))
            if open_backtest_page is not None:
                open_backtest_page()
            st.rerun()
    with action_cols[3]:
        st.caption(
            "`Load Into Form`은 저장된 입력값만 `Single Strategy` 화면으로 불러옵니다. "
            "이후 form에서 다시 실행해야 최신 결과가 갱신됩니다. "
            "`Run Again`은 저장된 payload를 즉시 다시 실행하고, 최신 결과 화면으로 자동 이동합니다. "
            "`Review As Candidate Draft`는 저장된 결과를 후보 검토 초안으로만 보냅니다."
        )


# Public renderer used by Compare and saved portfolio replay surfaces.
def render_real_money_guardrail_parity_snapshot(
    items: list[dict[str, Any]],
    *,
    title: str = "Real-Money / Guardrail Scope Snapshot",
    caption: str | None = None,
) -> None:
    _render_real_money_guardrail_parity_snapshot(items, title=title, caption=caption)


# Render the Operations-owned Backtest run history surface.
def render_backtest_run_history_page(*, open_backtest_page: Callable[[], None] | None = None) -> None:
    st.title("Backtest Run History")
    st.caption(
        "저장된 백테스트 실행 기록을 운영 관점에서 다시 열고, form 복원, 재실행, Candidate Review 초안 전달을 처리합니다."
    )
    st.info(
        "이 화면은 후보 검토의 본 단계가 아니라 과거 실행을 재현하고 감사하는 운영 도구입니다. "
        "`Load Into Form`, `Run Again`, `Review As Candidate Draft`를 사용하면 Backtest 작업 흐름으로 이동합니다."
    )

    _render_persistent_backtest_history(open_backtest_page=open_backtest_page)
