from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.services.backtest_practical_validation import (
    VALIDATION_PROFILE_OPTIONS,
    VALIDATION_PROFILE_QUESTIONS,
    build_provider_gap_collection_plan,
    build_provider_gap_rows,
    build_practical_validation_result,
    build_validation_profile,
    prepare_final_review_handoff_from_validation,
    provider_gap_state_key,
    run_provider_gap_collection,
    save_practical_validation_result,
    source_components_dataframe,
)
from app.services.backtest_practical_validation_replay import (
    RECHECK_MODE_EXTEND_TO_LATEST,
    RECHECK_MODE_LABELS,
    build_practical_validation_recheck_plan,
    run_practical_validation_actual_replay,
)
from app.web.backtest_ui_components import (
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.runtime import (
    PORTFOLIO_SELECTION_SOURCE_FILE,
    PRACTICAL_VALIDATION_RESULT_FILE,
    load_portfolio_selection_sources,
    load_practical_validation_results,
)


DIAGNOSTIC_EXPLANATIONS = {
    "input_evidence_layer": "원본 source, 비중 합계, Data Trust, 실행 경계가 검증 가능한 상태인지 확인합니다.",
    "asset_allocation_fit": "ETF 내부 exposure 또는 proxy 기준으로 자산군 구성이 검증 프로필과 맞는지 확인합니다.",
    "concentration_overlap_exposure": "보유 ETF와 내부 노출이 특정 자산, 섹터, 종목에 과도하게 몰려 있는지 확인합니다.",
    "correlation_diversification_risk_contribution": "component 간 수익률 움직임과 위험 기여가 한쪽으로 쏠리지 않는지 확인합니다.",
    "regime_macro_suitability": "현재 금리, 신용스프레드, 변동성 환경이 후보 전략의 약점과 충돌하는지 확인합니다.",
    "sentiment_risk_on_off_overlay": "VIX, 금리곡선, credit spread로 현재 시장이 risk-on인지 caution 구간인지 확인합니다.",
    "stress_scenario_diagnostics": "과거 위기 구간에서 후보가 얼마나 버텼고, 아직 계산되지 않은 stress window가 있는지 확인합니다.",
    "alternative_portfolio_challenge": "SPY, QQQ, 60/40 같은 단순 대안보다 이 후보를 선택할 이유가 있는지 확인합니다.",
    "leveraged_inverse_etf_suitability": "레버리지, 인버스, 일간 목표 상품이 포함되어 운용 목적과 충돌하지 않는지 확인합니다.",
    "operability_cost_liquidity": "ETF 비용, 규모, 거래대금, 스프레드, premium/discount가 실전 운용에 충분한지 확인합니다.",
    "robustness_sensitivity_overfit": "기간, 구성요소, 비중 변화에 결과가 과도하게 흔들리거나 과최적화된 흔적이 있는지 확인합니다.",
    "monitoring_baseline_seed": "선정 이후 추적할 benchmark, component, review trigger의 기본 seed가 충분한지 확인합니다.",
}


def _diagnostic_explanation(diagnostic: dict[str, Any]) -> str:
    domain = str(diagnostic.get("domain") or "").strip()
    return DIAGNOSTIC_EXPLANATIONS.get(domain, "")


def _source_label(row: dict[str, Any]) -> str:
    return (
        f"{row.get('created_at') or '-'} | "
        f"{row.get('source_kind') or '-'} | "
        f"{row.get('source_title') or row.get('selection_source_id') or '-'}"
    )


def _render_source_summary(source: dict[str, Any]) -> None:
    summary = dict(source.get("summary") or {})
    period = dict(source.get("period") or {})
    construction = dict(source.get("construction") or {})
    render_badge_strip(
        [
            {"label": "Source", "value": source.get("source_kind") or "-", "tone": "neutral"},
            {"label": "Period", "value": f"{period.get('actual_start') or period.get('start') or '-'} -> {period.get('actual_end') or period.get('end') or '-'}", "tone": "neutral"},
            {"label": "CAGR", "value": summary.get("cagr") if summary.get("cagr") is not None else "-", "tone": "neutral"},
            {"label": "MDD", "value": summary.get("mdd") if summary.get("mdd") is not None else "-", "tone": "neutral"},
            {"label": "Weight Total", "value": f"{construction.get('target_weight_total', 0)}%", "tone": "neutral"},
        ]
    )
    component_df = source_components_dataframe(source)
    if component_df.empty:
        st.info("선택된 source에 component snapshot이 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)


def _render_validation_profile_form() -> dict[str, Any]:
    profile_options = list(VALIDATION_PROFILE_OPTIONS.keys())
    profile_id = st.selectbox(
        "검증 프로필",
        options=profile_options,
        format_func=lambda key: (
            f"{VALIDATION_PROFILE_OPTIONS[key]['label']} - "
            f"{VALIDATION_PROFILE_OPTIONS[key]['description']}"
        ),
        key="practical_validation_profile_id",
    )
    answers: dict[str, str] = {}
    question_items = list(VALIDATION_PROFILE_QUESTIONS.items())
    for start in range(0, len(question_items), 2):
        cols = st.columns(2, gap="small")
        for offset, col in enumerate(cols):
            if start + offset >= len(question_items):
                continue
            question_key, question = question_items[start + offset]
            options = list(dict(question.get("options") or {}).keys())
            labels = dict(question.get("options") or {})
            with col:
                answers[question_key] = st.selectbox(
                    str(question.get("label") or question_key),
                    options=options,
                    format_func=lambda option, labels=labels: labels.get(option, option),
                    index=options.index(question.get("default")) if question.get("default") in options else 0,
                    key=f"practical_validation_profile_answer_{question_key}",
                )
    profile = build_validation_profile(profile_id, answers)
    render_badge_strip(
        [
            {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
            {"label": "Rolling", "value": f"{dict(profile.get('thresholds') or {}).get('rolling_window_months')}M", "tone": "neutral"},
            {"label": "Cost", "value": f"{dict(profile.get('thresholds') or {}).get('one_way_cost_bps')} bps", "tone": "neutral"},
            {"label": "MDD Line", "value": dict(profile.get("thresholds") or {}).get("mdd_review_line"), "tone": "neutral"},
        ]
    )
    return {"profile_id": profile_id, "answers": answers}


def _replay_state_key(source: dict[str, Any], mode: str) -> str:
    return f"practical_validation_recheck_{source.get('selection_source_id') or 'source'}_{mode}"


def _render_actual_replay_panel(source: dict[str, Any]) -> dict[str, Any] | None:
    source_id = source.get("selection_source_id") or "source"
    mode = st.radio(
        "재검증 방식",
        options=list(RECHECK_MODE_LABELS.keys()),
        format_func=lambda value: RECHECK_MODE_LABELS.get(value, value),
        horizontal=True,
        key=f"practical_validation_recheck_mode_{source_id}",
    )
    recheck_plan = build_practical_validation_recheck_plan(source, mode=mode)
    replay_key = _replay_state_key(source, mode)
    replay_result = st.session_state.get(replay_key)
    render_badge_strip(
        [
            {"label": "Mode", "value": recheck_plan.get("mode_label") or "-", "tone": "neutral"},
            {"label": "Stored End", "value": dict(recheck_plan.get("stored_period") or {}).get("end") or "-", "tone": "neutral"},
            {"label": "Recheck End", "value": dict(recheck_plan.get("requested_period") or {}).get("end") or "-", "tone": "neutral"},
            {
                "label": "Extension",
                "value": f"{recheck_plan.get('extension_days', 0)} days",
                "tone": "neutral",
            },
        ]
    )
    if recheck_plan.get("latest_market_date_error"):
        st.warning(f"최신 DB 시장일 조회 실패: {recheck_plan.get('latest_market_date_error')}")
    elif mode == RECHECK_MODE_EXTEND_TO_LATEST:
        st.caption(
            f"DB 최신 시장일 `{recheck_plan.get('latest_market_date') or '-'}` 기준입니다. "
            f"{recheck_plan.get('status_reason') or ''}"
        )
    else:
        st.caption(str(recheck_plan.get("status_reason") or ""))
    st.caption(
        "이 버튼은 새 전략을 만들지 않고 기존 Backtest runtime으로 source를 재검증합니다. "
        "실패해도 저장 snapshot / DB price proxy 기반 진단은 계속 볼 수 있습니다."
    )
    if st.button("전략 재검증 실행", key=f"{replay_key}_run", width="stretch"):
        with st.spinner("기존 strategy runtime으로 Practical Validation source를 재검증 중입니다..."):
            replay_result = run_practical_validation_actual_replay(source, mode=mode)
        st.session_state[replay_key] = replay_result
        if replay_result.get("status") == "PASS":
            st.success("전략 재검증이 완료되었습니다.")
        elif replay_result.get("status") == "REVIEW":
            st.warning("전략 재검증은 완료되었지만 기간 coverage 또는 일부 component 확인이 필요합니다.")
        else:
            st.warning("전략 재검증이 일부 실패했습니다. 세부 결과를 확인하세요.")
    replay_result = st.session_state.get(replay_key)
    if isinstance(replay_result, dict) and replay_result:
        summary = dict(replay_result.get("summary") or {})
        period_coverage = dict(replay_result.get("period_coverage") or {})
        actual_period = dict(period_coverage.get("actual_period") or replay_result.get("actual_period") or {})
        render_badge_strip(
            [
                {
                    "label": "Recheck",
                    "value": replay_result.get("status") or "NOT_RUN",
                    "tone": _status_tone(replay_result.get("status")),
                },
                {"label": "Recheck ID", "value": replay_result.get("replay_id") or "-", "tone": "neutral"},
                {"label": "Elapsed", "value": f"{replay_result.get('elapsed_ms', 0)} ms", "tone": "neutral"},
                {"label": "CAGR", "value": summary.get("cagr") if summary else "-", "tone": "neutral"},
                {"label": "MDD", "value": summary.get("mdd") if summary else "-", "tone": "neutral"},
            ]
        )
        render_badge_strip(
            [
                {
                    "label": "Coverage",
                    "value": period_coverage.get("status") or "NOT_RUN",
                    "tone": _status_tone(period_coverage.get("status")),
                },
                {"label": "Actual End", "value": actual_period.get("end") or "-", "tone": "neutral"},
                {"label": "End Gap", "value": f"{period_coverage.get('end_gap_days', '-')} days", "tone": "neutral"},
                {"label": "Latest DB", "value": replay_result.get("latest_market_date") or "-", "tone": "neutral"},
            ]
        )
        if period_coverage.get("summary"):
            st.caption(str(period_coverage.get("summary")))
        component_rows = list(replay_result.get("component_results") or [])
        if component_rows:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Component": row.get("title"),
                            "Strategy": row.get("strategy_key"),
                            "Weight": row.get("target_weight"),
                            "Status": row.get("status"),
                            "Rows": row.get("result_rows"),
                            "Requested Start": row.get("requested_start"),
                            "Requested End": row.get("requested_end"),
                            "Start": row.get("actual_start"),
                            "End": row.get("actual_end"),
                            "Error": row.get("error"),
                        }
                        for row in component_rows
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
        coverage_rows = list(period_coverage.get("component_rows") or [])
        if coverage_rows:
            st.dataframe(pd.DataFrame(coverage_rows), width="stretch", hide_index=True)
    return dict(replay_result) if isinstance(replay_result, dict) else None


def _status_tone(status: Any) -> str:
    status_text = str(status or "").upper()
    if status_text == "PASS":
        return "positive"
    if status_text == "BLOCKED":
        return "danger"
    if status_text in {"REVIEW", "NEEDS_INPUT"}:
        return "warning"
    return "neutral"


def _pct_badge_value(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return "-"


def _render_provider_gap_collection_results(results: list[dict[str, Any]]) -> None:
    if not results:
        return
    st.markdown("###### 최근 Provider 데이터 수집 결과")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Job": result.get("job_name"),
                    "Status": result.get("status"),
                    "Rows Written": result.get("rows_written"),
                    "Symbols": result.get("symbols_requested"),
                    "Failed": len(result.get("failed_symbols") or []),
                    "Message": result.get("message"),
                }
                for result in results
            ]
        ),
        width="stretch",
        hide_index=True,
    )


def _render_provider_gap_section(validation_result: dict[str, Any]) -> None:
    gap_rows = build_provider_gap_rows(validation_result)
    if not gap_rows:
        return

    st.markdown("##### Provider Data Gaps")
    st.caption(
        "현재 source에 필요한 ETF별 provider 데이터가 어디까지 채워졌는지 보여줍니다. "
        "부족 데이터는 이 화면에서 바로 수집할 수 있고, source mapping이 없는 ETF는 connector 보강이 필요합니다."
    )
    st.dataframe(pd.DataFrame(gap_rows), width="stretch", hide_index=True)
    if not any(str(row.get("Action") or "") != "조치 없음" for row in gap_rows):
        st.success("현재 ETF provider gap은 없습니다.")
        return

    plan = build_provider_gap_collection_plan(validation_result)
    if plan["operability_bridge"] or plan["operability_official"]:
        st.warning(
            "운용성 데이터 보강 필요: "
            + ", ".join(sorted(set(plan["operability_official"]) | set(plan["operability_bridge"])))
        )
    if plan["holdings_exposure"]:
        st.warning("Holdings / Exposure 수집 가능: " + ", ".join(plan["holdings_exposure"]))
    if plan["source_map_discovery"]:
        st.info(
            "Holdings / Exposure source map 자동 탐색 필요: "
            + ", ".join(plan["source_map_discovery"])
        )
    if plan["mapping_needed"]:
        st.info(
            "Holdings / Exposure connector mapping 필요: "
            + ", ".join(plan["mapping_needed"])
        )
    action_rows = [
        {
            "Area": "ETF Provider Source Map",
            "Symbols": ", ".join(plan["source_map_discovery"]) or "-",
            "Meaning": "`nyse_etf`와 asset profile을 기준으로 운용사 공식 URL / parser mapping을 찾아 `finance_meta.etf_provider_source_map`에 저장합니다.",
        },
        {
            "Area": "ETF Operability official",
            "Symbols": ", ".join(plan["operability_official"]) or "-",
            "Meaning": "공식 운용사 page에서 비용 / 상품 metadata를 수집합니다.",
        },
        {
            "Area": "ETF Operability DB bridge",
            "Symbols": ", ".join(plan["operability_bridge"]) or "-",
            "Meaning": "공식 source map이 없거나 부족한 ETF를 DB price / asset profile 기반으로 보강합니다.",
        },
        {
            "Area": "ETF Holdings / Exposure",
            "Symbols": ", ".join(plan["holdings_exposure"]) or "-",
            "Meaning": "공식 holdings를 수집하고 자산군 / 섹터 exposure를 재집계합니다.",
        },
        {
            "Area": "Connector mapping needed",
            "Symbols": ", ".join(plan["mapping_needed"]) or "-",
            "Meaning": "자동 탐색 후에도 검증된 issuer URL / parser mapping이 없으면 수동 connector 보강이 필요합니다.",
        },
    ]
    if plan["macro"]:
        action_rows.append(
            {
                "Area": "Macro Context",
                "Symbols": "VIXCLS, T10Y3M, BAA10Y",
                "Meaning": "FRED market context series를 다시 수집합니다.",
            }
        )
    st.dataframe(pd.DataFrame(action_rows), width="stretch", hide_index=True)

    result_key = provider_gap_state_key(validation_result)
    latest_results = st.session_state.get(result_key)
    if isinstance(latest_results, list):
        _render_provider_gap_collection_results(latest_results)

    has_collectable = any(
        [
            plan["operability_official"],
            plan["operability_bridge"],
            plan["holdings_exposure"],
            plan["source_map_discovery"],
            plan["macro"],
        ]
    )
    if not has_collectable:
        st.info("현재 버튼으로 수집 가능한 provider gap은 없습니다. 남은 부족 ETF는 connector source mapping 추가가 필요합니다.")
        return

    if st.button("부족한 Provider 데이터 일괄 수집 / 보강", key=f"{result_key}_run", width="stretch"):
        with st.spinner("현재 source에 필요한 provider snapshot을 수집 / 보강 중입니다..."):
            results = run_provider_gap_collection(validation_result)
        st.session_state[result_key] = results
        st.rerun()


def _provider_look_through_board(validation_result: dict[str, Any]) -> dict[str, Any]:
    board = dict(validation_result.get("provider_look_through_board") or {})
    if board:
        return board
    provider_context = dict(validation_result.get("provider_coverage") or {})
    return dict(provider_context.get("look_through_board") or {})


def _render_provider_look_through_board(validation_result: dict[str, Any]) -> None:
    board = _provider_look_through_board(validation_result)
    if not board:
        return

    st.markdown("##### Look-through Exposure Board")
    st.caption(
        "ETF holdings / exposure snapshot을 portfolio weight 기준으로 접어 본 compact board입니다. "
        "full holdings row는 DB에만 있고, 여기에는 판단에 필요한 요약만 표시합니다."
    )
    render_badge_strip(
        [
            {"label": "Board", "value": board.get("status") or "-", "tone": _status_tone(board.get("status"))},
            {"label": "Holdings", "value": f"{board.get('holdings_coverage_weight', 0)}%", "tone": _status_tone(board.get("holdings_status"))},
            {"label": "Exposure", "value": f"{board.get('exposure_coverage_weight', 0)}%", "tone": _status_tone(board.get("exposure_status"))},
            {"label": "Top Holding", "value": f"{board.get('top_holding_weight', 0)}%", "tone": "warning" if (board.get("top_holding_weight") or 0) > 25 else "neutral"},
            {"label": "Dominant", "value": f"{board.get('dominant_asset_bucket') or '-'} {board.get('dominant_asset_weight', 0)}%", "tone": "neutral"},
            {"label": "Unknown", "value": f"{board.get('unknown_exposure_weight', 0)}%", "tone": "warning" if (board.get("unknown_exposure_weight") or 0) else "neutral"},
        ]
    )
    st.caption(str(board.get("summary") or "-"))
    summary_rows = list(board.get("summary_rows") or [])
    if summary_rows:
        st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)

    tabs = st.tabs(["Asset Buckets", "Top Holdings", "Fund Coverage", "Exposure Detail"])
    with tabs[0]:
        asset_rows = list(board.get("asset_bucket_rows") or [])
        if asset_rows:
            st.dataframe(pd.DataFrame(asset_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 asset bucket exposure가 없습니다.")
    with tabs[1]:
        holding_rows = list(board.get("top_holding_rows") or [])
        if holding_rows:
            st.dataframe(pd.DataFrame(holding_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 top holdings row가 없습니다.")
    with tabs[2]:
        fund_rows = list(board.get("fund_coverage_rows") or [])
        if fund_rows:
            st.dataframe(pd.DataFrame(fund_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 ETF별 coverage row가 없습니다.")
    with tabs[3]:
        exposure_rows = list(board.get("exposure_detail_rows") or [])
        if exposure_rows:
            st.dataframe(pd.DataFrame(exposure_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 exposure detail row가 없습니다.")

    limitations = list(board.get("limitations") or [])
    if limitations:
        st.caption("Limitations: " + " / ".join(str(item) for item in limitations))


def _robustness_lab_board(validation_result: dict[str, Any]) -> dict[str, Any]:
    robustness = dict(validation_result.get("robustness_validation") or {})
    board = dict(robustness.get("robustness_lab_board") or validation_result.get("robustness_lab_board") or {})
    return board


def _render_robustness_lab_board(board: dict[str, Any]) -> None:
    metrics = dict(board.get("metrics") or {})
    st.markdown("##### Robustness Lab")
    st.caption(
        "Stress, rolling, sensitivity, overfit 근거를 Final Review에서 바로 읽을 수 있는 compact board로 요약합니다."
    )
    render_badge_strip(
        [
            {"label": "Board", "value": board.get("status") or "-", "tone": _status_tone(board.get("status"))},
            {
                "label": "Stress",
                "value": f"{metrics.get('computed_stress_windows', 0)}/{metrics.get('covered_stress_windows', 0)}",
                "tone": _status_tone(metrics.get("stress_status")),
            },
            {
                "label": "Sensitivity",
                "value": metrics.get("computed_sensitivity_checks", 0),
                "tone": _status_tone(metrics.get("sensitivity_status")),
            },
            {
                "label": "Follow-up",
                "value": metrics.get("runtime_followup_count", 0),
                "tone": "warning" if metrics.get("runtime_followup_count") else "neutral",
            },
            {"label": "Rolling", "value": metrics.get("rolling_window_count") or "-", "tone": _status_tone(metrics.get("rolling_status"))},
            {"label": "Trials", "value": metrics.get("local_trial_count", 0), "tone": _status_tone(metrics.get("overfit_status"))},
        ]
    )
    st.caption(str(board.get("summary") or "-"))
    summary_tab, stress_tab, sensitivity_tab, follow_up_tab = st.tabs(["Summary", "Stress", "Sensitivity", "Follow-up"])
    with summary_tab:
        summary_rows = list(board.get("summary_rows") or [])
        if summary_rows:
            st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 robustness summary row가 없습니다.")
    with stress_tab:
        stress_rows = list(board.get("stress_rows") or [])
        if stress_rows:
            st.dataframe(pd.DataFrame(stress_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 stress detail row가 없습니다.")
    with sensitivity_tab:
        sensitivity_rows = list(board.get("sensitivity_rows") or [])
        if sensitivity_rows:
            st.dataframe(pd.DataFrame(sensitivity_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 sensitivity detail row가 없습니다.")
    with follow_up_tab:
        follow_up_rows = list(board.get("follow_up_rows") or [])
        if follow_up_rows:
            st.dataframe(pd.DataFrame(follow_up_rows), width="stretch", hide_index=True)
        else:
            st.success("즉시 follow-up으로 남은 robustness row가 없습니다.")

    limitations = list(board.get("limitations") or [])
    if limitations:
        st.caption("Limitations: " + " / ".join(str(item) for item in limitations))


def _render_stress_sensitivity_interpretation(validation_result: dict[str, Any]) -> None:
    board = _robustness_lab_board(validation_result)
    if board:
        _render_robustness_lab_board(board)
        return

    stress = dict(validation_result.get("stress_interpretation") or {})
    sensitivity = dict(validation_result.get("sensitivity_interpretation") or {})
    if not stress and not sensitivity:
        return

    st.markdown("##### Stress / Sensitivity Interpretation")
    st.caption(
        "Stress와 sensitivity 숫자를 Final Review에서 바로 읽을 수 있도록 원인, trigger, 다음 확인 항목으로 요약합니다."
    )
    stress_tab, sensitivity_tab = st.tabs(["Stress", "Sensitivity"])
    with stress_tab:
        render_badge_strip(
            [
                {"label": "Status", "value": stress.get("status") or "-", "tone": _status_tone(stress.get("status"))},
                {"label": "Computed", "value": f"{stress.get('computed_count', 0)}/{stress.get('covered_count', 0)}", "tone": "neutral"},
                {"label": "Uncomputed", "value": stress.get("uncomputed_count", 0), "tone": "warning" if stress.get("uncomputed_count") else "neutral"},
                {"label": "Worst MDD", "value": _pct_badge_value(stress.get("worst_mdd")), "tone": "neutral"},
            ]
        )
        st.caption(str(stress.get("summary") or "-"))
        stress_rows = list(stress.get("rows") or [])
        if stress_rows:
            st.dataframe(pd.DataFrame(stress_rows), width="stretch", hide_index=True)
    with sensitivity_tab:
        render_badge_strip(
            [
                {"label": "Status", "value": sensitivity.get("status") or "-", "tone": _status_tone(sensitivity.get("status"))},
                {"label": "Computed", "value": sensitivity.get("computed_count", 0), "tone": "neutral"},
                {"label": "Review", "value": sensitivity.get("review_count", 0), "tone": "warning" if sensitivity.get("review_count") else "neutral"},
                {"label": "Runtime Follow-up", "value": sensitivity.get("runtime_followup_count", 0), "tone": "warning" if sensitivity.get("runtime_followup_count") else "neutral"},
            ]
        )
        st.caption(str(sensitivity.get("summary") or "-"))
        sensitivity_rows = list(sensitivity.get("rows") or [])
        if sensitivity_rows:
            st.dataframe(pd.DataFrame(sensitivity_rows), width="stretch", hide_index=True)


def _render_validation_result(validation_result: dict[str, Any]) -> None:
    profile = dict(validation_result.get("validation_profile") or {})
    status_counts = dict(dict(validation_result.get("diagnostic_summary") or {}).get("status_counts") or {})
    render_readiness_route_panel(
        route_label=str(validation_result.get("validation_route") or "-"),
        score=float(validation_result.get("validation_score") or 0.0),
        blockers_count=len(validation_result.get("hard_blockers") or []),
        verdict=str(validation_result.get("verdict") or "-"),
        next_action=str(validation_result.get("next_action") or "-"),
        route_title="Practical Validation",
        score_title="Validation Score",
    )
    render_badge_strip(
        [
            {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
            {"label": "PASS", "value": status_counts.get("PASS", 0), "tone": "positive"},
            {"label": "REVIEW", "value": status_counts.get("REVIEW", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": status_counts.get("BLOCKED", 0), "tone": "danger"},
            {"label": "NOT_RUN", "value": status_counts.get("NOT_RUN", 0), "tone": "neutral"},
        ]
    )
    st.markdown("##### Input Evidence")
    st.dataframe(pd.DataFrame(validation_result.get("checks") or []), width="stretch", hide_index=True)
    _render_validation_efficacy_audit(validation_result)
    st.markdown("##### Practical Diagnostics")
    diagnostic_rows = list(validation_result.get("diagnostic_display_rows") or [])
    if diagnostic_rows:
        st.dataframe(pd.DataFrame(diagnostic_rows), width="stretch", hide_index=True)
    else:
        st.info("표시할 diagnostic row가 없습니다.")

    provider_rows = list(validation_result.get("provider_coverage_display_rows") or [])
    if provider_rows:
        st.markdown("##### Provider Coverage")
        st.caption(
            "Ingestion에서 저장한 ETF provider / FRED snapshot이 Practical Diagnostics에 어떻게 연결됐는지 보여줍니다."
        )
        st.dataframe(pd.DataFrame(provider_rows), width="stretch", hide_index=True)
        _render_provider_look_through_board(validation_result)
        _render_provider_gap_section(validation_result)

    _render_stress_sensitivity_interpretation(validation_result)

    mismatch_warnings = list(validation_result.get("intent_mismatch_warnings") or [])
    if mismatch_warnings:
        st.warning("사용자 프로필과 후보 특성이 충돌할 수 있습니다.")
        for warning in mismatch_warnings:
            st.caption(f"- {warning}")
    if validation_result.get("hard_blockers"):
        for blocker in list(validation_result.get("hard_blockers") or []):
            st.error(str(blocker))
    if validation_result.get("review_gaps"):
        for gap in list(validation_result.get("review_gaps") or []):
            st.warning(str(gap))
    not_run_critical = list(validation_result.get("not_run_critical_domains") or [])
    if not_run_critical:
        st.info("아래 NOT_RUN 항목은 Final Review에서 선택/보류/재검토 판단 근거로 확인해야 합니다.")
        st.dataframe(pd.DataFrame(not_run_critical), width="stretch", hide_index=True)
    curve_evidence = dict(validation_result.get("curve_evidence") or {})
    if curve_evidence:
        st.markdown("##### Curve / Recheck Evidence")
        render_badge_strip(
            [
                {"label": "Portfolio Curve", "value": curve_evidence.get("portfolio_curve_source") or "-", "tone": "positive" if curve_evidence.get("portfolio_curve_rows") else "warning"},
                {"label": "Rows", "value": curve_evidence.get("portfolio_curve_rows", 0), "tone": "neutral"},
                {"label": "Benchmark", "value": curve_evidence.get("benchmark_ticker") or "-", "tone": "neutral"},
                {"label": "Benchmark Rows", "value": curve_evidence.get("benchmark_curve_rows", 0), "tone": "neutral"},
            ]
        )
        component_curve_rows = list(curve_evidence.get("component_curve_rows") or [])
        if component_curve_rows:
            st.dataframe(pd.DataFrame(component_curve_rows), width="stretch", hide_index=True)
        benchmark_parity = dict(curve_evidence.get("benchmark_parity") or {})
        if benchmark_parity:
            render_badge_strip(
                [
                    {
                        "label": "Benchmark Parity",
                        "value": benchmark_parity.get("status") or "-",
                        "tone": _status_tone(benchmark_parity.get("status")),
                    },
                    {
                        "label": "Coverage",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("coverage_ratio", "-"),
                        "tone": "neutral",
                    },
                    {
                        "label": "Same Period",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("same_period", "-"),
                        "tone": "neutral",
                    },
                    {
                        "label": "Same Frequency",
                        "value": dict(benchmark_parity.get("metrics") or {}).get("same_frequency", "-"),
                        "tone": "neutral",
                    },
                ]
            )
            parity_rows = list(benchmark_parity.get("rows") or [])
            if parity_rows:
                st.dataframe(pd.DataFrame(parity_rows), width="stretch", hide_index=True)
        curve_provenance = dict(curve_evidence.get("curve_provenance") or {})
        if curve_provenance:
            with st.expander("Curve provenance", expanded=False):
                st.json(curve_provenance)

    with st.expander("진단 세부 근거", expanded=False):
        for diagnostic in list(validation_result.get("diagnostic_results") or []):
            st.markdown(f"**{diagnostic.get('title')}**")
            explanation = _diagnostic_explanation(diagnostic)
            if explanation:
                st.caption(explanation)
            render_badge_strip(
                [
                    {"label": "Status", "value": diagnostic.get("status") or "-", "tone": _status_tone(diagnostic.get("status"))},
                    {"label": "Metric", "value": diagnostic.get("key_metric") or "-", "tone": "neutral"},
                    {"label": "Origin", "value": diagnostic.get("origin") or "-", "tone": "neutral"},
                ]
            )
            st.caption(str(diagnostic.get("summary") or "-"))
            evidence_rows = list(diagnostic.get("evidence_rows") or [])
            if evidence_rows:
                st.dataframe(pd.DataFrame(evidence_rows), width="stretch", hide_index=True)
            limitations = list(diagnostic.get("limitations") or [])
            if limitations:
                st.caption("Limitations: " + " / ".join(str(item) for item in limitations))
    profile_score_rows = list(validation_result.get("profile_score_rows") or [])
    if profile_score_rows:
        with st.expander("Profile-aware score breakdown", expanded=False):
            st.dataframe(pd.DataFrame(profile_score_rows), width="stretch", hide_index=True)


def _render_validation_efficacy_audit(validation_result: dict[str, Any]) -> None:
    audit = dict(validation_result.get("validation_efficacy_audit") or {})
    rows = list(validation_result.get("validation_efficacy_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    boundary = dict(audit.get("execution_boundary") or {})
    st.markdown("##### Validation Efficacy Audit")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {"label": "BLOCKED", "value": metrics.get("blocked", 0), "tone": "danger"},
            {
                "label": "Writes",
                "value": "Disabled" if not boundary.get("db_write") and not boundary.get("registry_write") else "Review",
                "tone": "neutral",
            },
        ]
    )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    if audit.get("conclusion"):
        st.caption(str(audit.get("conclusion")))


def render_practical_validation_workspace() -> None:
    st.markdown("### Practical Validation")
    st.caption(
        "Backtest Analysis에서 선택한 후보를 실전 투입 전 관점으로 검증합니다. "
        "최종 사용자 메모와 최종 판단은 Final Review에서만 남깁니다."
    )

    sources = load_portfolio_selection_sources(limit=100)
    validation_rows = load_practical_validation_results(limit=100)
    session_source = st.session_state.get("backtest_practical_validation_source")
    notice = st.session_state.pop("backtest_practical_validation_notice", None)
    if notice:
        st.success(str(notice))

    render_status_card_grid(
        [
            {"title": "Selection Sources", "value": len(sources), "tone": "positive" if sources else "neutral"},
            {"title": "Validation Results", "value": len(validation_rows), "tone": "positive" if validation_rows else "neutral"},
            {"title": "Final Memo", "value": "Final Review Only", "tone": "neutral"},
            {"title": "Live Approval", "value": "Disabled", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        render_stage_brief(
            purpose="선택된 단일 전략, Compare 후보, 저장 Mix를 같은 Clean V2 source로 읽습니다.",
            result="Practical Validation result",
        )
        st.caption(f"Sources: `{PORTFOLIO_SELECTION_SOURCE_FILE}`")
        st.caption(f"Validation: `{PRACTICAL_VALIDATION_RESULT_FILE}`")

    selectable_sources: list[dict[str, Any]] = []
    if isinstance(session_source, dict) and session_source:
        selectable_sources.append(dict(session_source))
    existing_ids = {str(row.get("selection_source_id") or "") for row in selectable_sources}
    for row in sources:
        source_id = str(row.get("selection_source_id") or "")
        if source_id in existing_ids:
            continue
        selectable_sources.append(dict(row))

    if not selectable_sources:
        st.info("아직 Practical Validation으로 보낸 Clean V2 source가 없습니다.")
        st.caption("Backtest Analysis에서 Single / Compare / Saved Mix 결과를 선택하면 여기에 표시됩니다.")
        return

    labels = [_source_label(row) for row in selectable_sources]
    selected_label = st.selectbox("검증할 후보 source", options=labels, key="practical_validation_source_selected")
    source = selectable_sources[labels.index(selected_label)]

    st.markdown("#### 1. 선택 후보 확인")
    with st.container(border=True):
        _render_source_summary(source)

    st.markdown("#### 2. 검증 프로필")
    with st.container(border=True):
        validation_profile = _render_validation_profile_form()

    st.markdown("#### 3. 최신 데이터 기준 전략 재검증")
    with st.container(border=True):
        replay_result = _render_actual_replay_panel(source)

    validation_result = build_practical_validation_result(
        source,
        validation_profile=validation_profile,
        replay_result=replay_result,
    )
    st.markdown("#### 4. 실전 진단 보드")
    with st.container(border=True):
        _render_validation_result(validation_result)

    st.markdown("#### 5. 다음 단계")
    with st.container(border=True):
        st.info(
            "이 단계는 구조화된 검증 자료를 저장합니다. "
            "선정 / 보류 / 거절 / 재검토 판단과 최종 메모는 Final Review에서 기록합니다."
        )
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button("검증 결과 저장", key="practical_validation_save_result", width="stretch"):
                save_practical_validation_result(validation_result)
                st.success(f"검증 결과 `{validation_result['validation_id']}`를 저장했습니다.")
        with action_cols[1]:
            is_blocked = validation_result.get("validation_route") == "BLOCKED"
            if st.button(
                "Final Review로 이동",
                key="practical_validation_send_final_review",
                width="stretch",
                disabled=is_blocked,
            ):
                handoff = prepare_final_review_handoff_from_validation(
                    source=source,
                    validation_result=validation_result,
                    persist_validation=True,
                )
                st.session_state.final_review_practical_validation_source = handoff.session_payload
                st.session_state.final_review_practical_validation_notice = handoff.notice
                st.session_state.backtest_requested_panel = handoff.requested_panel
                st.rerun()
            if is_blocked:
                st.caption("BLOCKED 상태는 Backtest Analysis에서 source를 보강한 뒤 Final Review로 보낼 수 있습니다.")

    with st.expander("Clean V2 Source JSON", expanded=False):
        st.json(source)
    with st.expander("Practical Validation Result JSON", expanded=False):
        st.json(validation_result)
