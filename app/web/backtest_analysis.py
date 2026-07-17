from __future__ import annotations

from functools import partial

import pandas as pd
import streamlit as st

from app.services.backtest_analysis_research_board import build_backtest_analysis_research_board
from app.services.backtest_etf_current_anchor import build_etf_current_anchor_workbench
from app.services.backtest_etf_evidence_expansion import build_etf_evidence_expansion
from app.services.backtest_etf_rerun_matrix import (
    build_etf_rerun_matrix_plan,
    run_etf_rerun_matrix,
)
from app.services.backtest_risk_on_governance import build_risk_on_momentum_governance
from app.services.backtest_strategy_bridge import build_strict_annual_etf_bridge
from app.services.backtest_strategy_evidence_inventory import (
    build_strategy_evidence_inventory,
    build_strategy_evidence_inventory_summary,
)
from app.web.reference_contextual_help import render_reference_contextual_help
from app.web.backtest_compare import render_compare_portfolio_workspace
from app.web.backtest_analysis_workspace import (
    _CONTEXT_ACTIONS,
    build_current_backtest_analysis_workspace,
    consume_backtest_analysis_component_change,
    consume_backtest_analysis_intent,
    render_backtest_analysis_decision_surface,
)
from app.web.backtest_analysis_workspace_panel import (
    render_backtest_analysis_workspace_fallback,
)
from app.web.backtest_single_strategy import render_single_strategy_workspace
from app.web.components.backtest_analysis_decision_workspace import (
    is_backtest_analysis_decision_workspace_available,
    render_backtest_analysis_decision_workspace,
)
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_ANALYSIS_MODE_OPTIONS,
    BACKTEST_ANALYSIS_MODE_SINGLE,
    BACKTEST_LEGACY_ANALYSIS_MODE_COMPARE,
)


def _bridge_rows_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "전략": row.get("display_name") or "-",
                "연결 역할": row.get("bridge_role") or "-",
                "목표 용도": row.get("target_use") or "-",
                "필요 검증 근거": "; ".join(row.get("required_practical_validation_evidence") or []),
                "알려진 약점": row.get("known_weakness") or "-",
                "다음 작업": row.get("recommended_next_workflow") or "-",
            }
            for row in rows
        ]
    )


def _etf_expansion_rows_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "전략": row.get("display_name") or "-",
                "우선순위": row.get("priority") or "-",
                "현재 근거": row.get("current_anchor") or "-",
                "근접 후보": row.get("near_miss") or "-",
                "미성숙 이유": row.get("not_ready_reason") or "-",
                "필요 근거": "; ".join(row.get("required_evidence") or []),
                "다음 작업": row.get("next_workflow") or "-",
            }
            for row in rows
        ]
    )


def _etf_current_anchor_rows_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    table_rows: list[dict[str, object]] = []
    for row in rows:
        latest_run = dict(row.get("latest_run") or {})
        latest_source = dict(row.get("latest_source") or {})
        run_label = "-"
        if latest_run:
            run_label = (
                f"{latest_run.get('recorded_at') or '-'} / "
                f"end {latest_run.get('actual_result_end') or '-'} / "
                f"rows {latest_run.get('result_rows') or '-'}"
            )
        table_rows.append(
            {
                "전략": row.get("display_name") or "-",
                "현재 근거 상태": row.get("anchor_status") or "-",
                "최근 실행": run_label,
                "선택 source": latest_source.get("selection_source_id") or "-",
                "부족한 근거": "; ".join(row.get("missing_evidence") or []) or "-",
                "다음 액션": row.get("recommended_next_action") or "-",
            }
        )
    return pd.DataFrame(table_rows)


def _format_params(params: dict[str, object]) -> str:
    if not params:
        return "-"
    return ", ".join(f"{key}={value}" for key, value in params.items() if value not in (None, "", [], {})) or "-"


def _etf_rerun_plan_rows_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    table_rows: list[dict[str, object]] = []
    for row in rows:
        for scenario in row.get("scenarios") or []:
            scenario_row = dict(scenario)
            table_rows.append(
                {
                    "전략": row.get("display_name") or "-",
                    "시나리오": scenario_row.get("scenario_name") or scenario_row.get("scenario_id") or "-",
                    "확인할 근거": scenario_row.get("evidence_focus") or "-",
                    "파라미터": _format_params(dict(scenario_row.get("params") or {})),
                }
            )
    return pd.DataFrame(table_rows)


def _etf_rerun_result_rows_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "시나리오": row.get("scenario_name") or row.get("scenario_id") or "-",
                "상태": row.get("status") or "-",
                "실제 종료일": row.get("actual_result_end") or "-",
                "행 수": row.get("result_rows") or "-",
                "CAGR": row.get("cagr") if row.get("cagr") is not None else "-",
                "MDD": row.get("maximum_drawdown") if row.get("maximum_drawdown") is not None else "-",
                "Sharpe": row.get("sharpe_ratio") if row.get("sharpe_ratio") is not None else "-",
                "가격 최신성": row.get("price_freshness_status") or "-",
                "승격 판단": row.get("promotion_decision") or "-",
                "경고 수": row.get("warning_count") if row.get("warning_count") is not None else "-",
                "오류": row.get("error") or "-",
            }
            for row in rows
        ]
    )


def _governance_evidence_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "근거": row.get("evidence") or "-",
                "상태": row.get("status") or "-",
                "해석": row.get("interpretation") or "-",
            }
            for row in rows
        ]
    )


def _governance_modules_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "모듈": row.get("module") or "-",
                "담당 화면": row.get("owner_surface") or "-",
                "준비도": row.get("readiness") or "-",
                "차단 사유": row.get("blocker") or "-",
                "다음 액션": row.get("next_action") or "-",
            }
            for row in rows
        ]
    )


def _simple_rows(items: list[str], column_name: str) -> pd.DataFrame:
    return pd.DataFrame([{column_name: item} for item in items])


def _strategy_inventory_table(rows: list[dict[str, object]], *, compact: bool = False) -> pd.DataFrame:
    columns = [
        ("display_name", "전략"),
        ("family", "계열"),
        ("maturity_label", "성숙도"),
        ("intended_role", "역할"),
        ("current_anchor", "현재 근거"),
        ("main_weakness", "핵심 약점"),
        ("next_action", "다음 액션"),
    ]
    if not compact:
        columns.insert(3, ("product_lane", "제품 경로"))
        columns.insert(4, ("governance_status", "governance"))
        columns.insert(5, ("validation_readiness", "검증 준비도"))
        columns.insert(6, ("monitoring_readiness", "모니터링 준비도"))
    return pd.DataFrame(
        [
            {label: row.get(key) or "-" for key, label in columns}
            for row in rows
        ]
    )


def _research_board_rows_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "항목": row.get("korean_label") or row.get("title") or "-",
                "성격": row.get("classification") or "-",
                "백테스트 실행 필수": "예" if row.get("required_for_backtest_execution") else "아니오",
                "전략 연구용": "예" if row.get("strategy_development_useful") else "아니오",
                "기본 표시": row.get("default_display") or "-",
                "권장 위치": row.get("recommended_location") or "-",
                "이유": row.get("reason") or "-",
            }
            for row in rows
        ]
    )


def _render_strategy_evidence_direction_panel() -> None:
    rows = build_strategy_evidence_inventory()
    summary = build_strategy_evidence_inventory_summary()
    first_group_rows = [
        row
        for row in rows
        if row["candidate_group"] == "First evidence-mature candidate group"
    ]

    with st.expander("전략 성숙도 / 다음 액션 (Strategy Evidence Inventory)", expanded=False):
        st.caption(
            "전략 catalog의 성숙도와 다음 작업을 확인하는 참고 보드입니다. "
            "전략을 실행하거나 registry / saved setup / run history를 쓰지 않습니다."
        )
        metric_cols = st.columns(4)
        metric_cols[0].metric("Catalog 전략", summary["strategy_count"])
        metric_cols[1].metric("근거 성숙 후보", summary["first_evidence_mature_count"])
        metric_cols[2].metric("Quarterly formal", summary["quarterly_formal_count"])
        metric_cols[3].metric("Risk-On governance", summary["risk_on_governance_status"])

        st.markdown("**첫 근거 성숙 후보군**")
        st.dataframe(
            _strategy_inventory_table(first_group_rows, compact=True),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**전체 catalog 전략 성숙도 / 다음 액션**")
        st.dataframe(
            _strategy_inventory_table(rows),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**다음 구현 후보 범위**")
        st.write(" / ".join(summary["next_scope_options"]))


def _render_strict_annual_etf_bridge_panel() -> None:
    bridge = build_strict_annual_etf_bridge()
    rows = bridge["rows"]

    with st.expander("Strict Annual + GTAA / Equal Weight 연결 기준", expanded=False):
        st.caption(bridge["candidate_intent"])
        metric_cols = st.columns(3)
        metric_cols[0].metric("연결 전략", len(rows))
        metric_cols[1].metric("검증 체크", len(bridge["validation_checklist"]))
        metric_cols[2].metric("보류 전략", len(bridge["deferred_exclusions"]))

        st.markdown("**연결 역할 / 검증 handoff**")
        st.dataframe(
            _bridge_rows_table(rows),
            hide_index=True,
            width="stretch",
        )

        checklist_col, workflow_col = st.columns(2)
        with checklist_col:
            st.markdown("**Practical Validation 체크리스트**")
            st.dataframe(
                _simple_rows(bridge["validation_checklist"], "체크"),
                hide_index=True,
                width="stretch",
            )
        with workflow_col:
            st.markdown("**다음 작업**")
            st.dataframe(
                _simple_rows(bridge["next_workflow_steps"], "단계"),
                hide_index=True,
                width="stretch",
            )

        st.caption(bridge["storage_boundary"])
        st.caption(bridge["route_boundary"])


def _render_risk_on_governance_panel() -> None:
    governance = build_risk_on_momentum_governance()

    with st.expander("Risk-On Momentum 5D 승격 조건", expanded=False):
        st.caption(governance["summary"])
        metric_cols = st.columns(4)
        metric_cols[0].metric("Governance", str(governance["status"]).replace("Governance ", "").title())
        metric_cols[1].metric(
            "Practical Validation",
            "Disabled" if not governance["promoted_to_practical_validation"] else "Enabled",
        )
        metric_cols[2].metric(
            "Final Review",
            "Disabled" if not governance["promoted_to_final_review"] else "Enabled",
        )
        metric_cols[3].metric(
            "Monitoring Signal",
            "Disabled" if not governance["monitoring_signal_enabled"] else "Enabled",
        )

        st.markdown("**현재 확인 가능한 연구 근거**")
        st.dataframe(
            _governance_evidence_table(governance["research_evidence"]),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**승격 전 필요한 governance module**")
        st.dataframe(
            _governance_modules_table(governance["required_modules"]),
            hide_index=True,
            width="stretch",
        )

        rules_col, workflow_col = st.columns(2)
        with rules_col:
            st.markdown("**Governance 규칙**")
            st.dataframe(
                _simple_rows(governance["governance_rules"], "규칙"),
                hide_index=True,
                width="stretch",
            )
        with workflow_col:
            st.markdown("**다음 작업**")
            st.dataframe(
                _simple_rows(governance["next_workflow_steps"], "단계"),
                hide_index=True,
                width="stretch",
            )

        st.caption(governance["storage_boundary"])
        st.caption(governance["route_boundary"])


def _render_etf_evidence_expansion_panel() -> None:
    expansion = build_etf_evidence_expansion()
    rows = expansion["rows"]

    with st.expander("ETF 전략 보강 필요 근거 (ETF Evidence Expansion)", expanded=False):
        st.caption(expansion["summary"])
        metric_cols = st.columns(4)
        metric_cols[0].metric("대상 전략", len(rows))
        metric_cols[1].metric("기준 참고 전략", len(expansion["baseline_reference_keys"]))
        metric_cols[2].metric(
            "후보 저장",
            "Disabled" if not expansion["creates_current_candidate"] else "Enabled",
        )
        metric_cols[3].metric(
            "Backtest 재실행",
            "Disabled" if not expansion["runs_backtests"] else "Enabled",
        )

        st.markdown("**ETF evidence 대상**")
        st.dataframe(
            _etf_expansion_rows_table(rows),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**전략별 상세**")
        for row in rows:
            display_name = row.get("display_name") or row.get("strategy_key") or "Strategy"
            with st.expander(f"{display_name} - {row.get('priority') or 'Evidence target'}", expanded=False):
                detail_cols = st.columns(2)
                detail_cols[0].markdown("**현재 근거**")
                detail_cols[0].write(row.get("current_anchor") or "-")
                detail_cols[0].markdown("**근접 후보**")
                detail_cols[0].write(row.get("near_miss") or "-")
                detail_cols[1].markdown("**미성숙 이유**")
                detail_cols[1].write(row.get("not_ready_reason") or "-")
                detail_cols[1].markdown("**근거 gap**")
                detail_cols[1].write(row.get("evidence_gap") or "-")
                st.markdown("**필요 근거**")
                for evidence in row.get("required_evidence") or []:
                    st.markdown(f"- {evidence}")
                st.markdown("**다음 작업**")
                st.write(row.get("next_workflow") or "-")

        st.markdown("**다음 작업**")
        st.dataframe(
            _simple_rows(expansion["next_workflow_steps"], "단계"),
            hide_index=True,
            width="stretch",
        )

        st.caption(expansion["storage_boundary"])
        st.caption(expansion["route_boundary"])


def _render_etf_current_anchor_workbench_panel() -> None:
    workbench = build_etf_current_anchor_workbench()
    rows = workbench["rows"]

    with st.expander("ETF 현재 근거 확인 (Current Anchor)", expanded=False):
        st.caption(workbench["summary"])
        metric_cols = st.columns(4)
        metric_cols[0].metric("최근 실행", workbench["latest_run_count"])
        metric_cols[1].metric("선택 source", workbench["source_count"])
        metric_cols[2].metric("검토 가능", workbench["ready_count"])
        metric_cols[3].metric("근거 gap", workbench["gap_count"])

        st.markdown("**현재 근거 readiness**")
        st.dataframe(
            _etf_current_anchor_rows_table(rows),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**전략별 근거 상세**")
        for row in rows:
            display_name = row.get("display_name") or row.get("strategy_key") or "Strategy"
            with st.expander(f"{display_name} - {row.get('anchor_status') or 'Anchor status'}", expanded=False):
                latest_run = dict(row.get("latest_run") or {})
                latest_source = dict(row.get("latest_source") or {})
                run_col, source_col = st.columns(2)
                with run_col:
                    st.markdown("**최근 실행 근거**")
                    if latest_run:
                        st.dataframe(
                            pd.DataFrame(
                                [
                                    {"항목": key.replace("_", " ").title(), "값": value}
                                    for key, value in latest_run.items()
                                    if value not in (None, "", [], {})
                                ]
                            ),
                            hide_index=True,
                            width="stretch",
                        )
                    else:
                        st.info("이 ETF 전략의 local run history row를 찾지 못했습니다.")
                with source_col:
                    st.markdown("**선택 source 근거**")
                    if latest_source:
                        st.dataframe(
                            pd.DataFrame(
                                [
                                    {"항목": key.replace("_", " ").title(), "값": value}
                                    for key, value in latest_source.items()
                                    if value not in (None, "", [], {})
                                ]
                            ),
                            hide_index=True,
                            width="stretch",
                        )
                    else:
                        st.info("이 ETF 전략의 Backtest Analysis selection source row를 찾지 못했습니다.")

                st.markdown("**부족한 근거**")
                missing = list(row.get("missing_evidence") or [])
                if missing:
                    for item in missing:
                        st.markdown(f"- {item}")
                else:
                    st.success("로드된 artifact row에서 현재 근거 gap을 찾지 못했습니다.")

                st.markdown("**권장 다음 액션**")
                st.write(row.get("recommended_next_action") or "-")

        st.caption(workbench["storage_boundary"])
        st.caption(workbench["route_boundary"])


def _render_etf_rerun_matrix_workbench_panel() -> None:
    plan = build_etf_rerun_matrix_plan()
    rows = plan["rows"]
    display_names = {row["strategy_key"]: row["display_name"] for row in rows}

    with st.expander("ETF 재실행 매트릭스 (Rerun Matrix)", expanded=False):
        st.caption(plan["summary"])
        metric_cols = st.columns(4)
        metric_cols[0].metric("전략", plan["strategy_count"])
        metric_cols[1].metric("시나리오", plan["scenario_count"])
        metric_cols[2].metric(
            "화면 로드시 실행",
            "Disabled" if not plan["runs_backtests_on_render"] else "Enabled",
        )
        metric_cols[3].metric(
            "Artifact 쓰기",
            "Disabled" if not plan["writes_run_history"] else "Enabled",
        )

        st.markdown("**Session-only 재실행 시나리오**")
        st.dataframe(
            _etf_rerun_plan_rows_table(rows),
            hide_index=True,
            width="stretch",
        )

        selected_strategy_key = st.selectbox(
            "ETF 재실행 매트릭스 대상",
            options=list(plan["target_strategy_keys"]),
            format_func=lambda key: display_names.get(key, key),
            key="backtest_etf_rerun_matrix_target",
        )
        if st.button(
            "선택한 ETF 재실행 매트릭스 실행",
            key="backtest_etf_rerun_matrix_run_button",
            type="secondary",
        ):
            with st.spinner("선택한 ETF 재실행 매트릭스를 현재 세션에서만 실행합니다..."):
                st.session_state["backtest_etf_rerun_matrix_result"] = run_etf_rerun_matrix(
                    selected_strategy_key
                )

        result = st.session_state.get("backtest_etf_rerun_matrix_result")
        if result and result.get("strategy_key") == selected_strategy_key:
            st.markdown("**최근 세션 결과**")
            result_metric_cols = st.columns(4)
            result_metric_cols[0].metric("상태", result["status"])
            result_metric_cols[1].metric("통과", result["pass_count"])
            result_metric_cols[2].metric("오류", result["error_count"])
            result_metric_cols[3].metric("시나리오", result["scenario_count"])
            st.dataframe(
                _etf_rerun_result_rows_table(result["rows"]),
                hide_index=True,
                width="stretch",
            )
        else:
            st.info("선택한 전략에 대해 현재 세션에서 실행된 ETF 재실행 매트릭스가 없습니다.")

        st.caption(plan["storage_boundary"])
        st.caption(plan["route_boundary"])


def _render_backtest_analysis_research_reference_board() -> None:
    board = build_backtest_analysis_research_board()

    st.divider()
    st.markdown("#### 전략 연구 보조")
    st.caption(board["summary"])
    with st.expander("기본 화면에서 숨긴 참고 항목", expanded=False):
        st.dataframe(
            _research_board_rows_table(board["rows"]),
            hide_index=True,
            width="stretch",
        )
        st.caption(board["storage_boundary"])

    show_reference_panels = st.checkbox(
        "전략 연구 보조 패널 열기",
        value=False,
        key="backtest_analysis_show_research_auxiliary_panels",
        help="전략 성숙도, governance, ETF evidence / rerun matrix 같은 보조 패널을 아래에 표시합니다.",
    )
    if not show_reference_panels:
        st.caption("기본 작업 흐름에서는 위 참고 패널을 숨기고 전략 실행 / 비교 / 후보 생성에 집중합니다.")
        return

    st.info(
        "아래 패널은 전략 연구 보조용입니다. 기본 백테스트 실행, registry, saved setup, run history, "
        "Practical Validation 결과, Final Review 결정, Monitoring log를 자동으로 만들지 않습니다."
    )
    render_reference_contextual_help("backtest_analysis", expanded=False)
    _render_strategy_evidence_direction_panel()
    _render_strict_annual_etf_bridge_panel()
    _render_risk_on_governance_panel()
    _render_etf_evidence_expansion_panel()
    _render_etf_current_anchor_workbench_panel()
    _render_etf_rerun_matrix_workbench_panel()


def render_backtest_analysis_workspace() -> None:
    current_mode = st.session_state.get("backtest_analysis_mode")
    if current_mode == BACKTEST_LEGACY_ANALYSIS_MODE_COMPARE:
        st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_COMPARE
    elif current_mode not in BACKTEST_ANALYSIS_MODE_OPTIONS:
        st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE

    workspace = build_current_backtest_analysis_workspace()
    component_key = "backtest-analysis-decision-workspace-context"
    if is_backtest_analysis_decision_workspace_available():
        intent = render_backtest_analysis_decision_workspace(
            workspace=workspace,
            surface="context",
            key=component_key,
            on_change=partial(
                consume_backtest_analysis_component_change,
                component_key=component_key,
                allowed_actions=_CONTEXT_ACTIONS,
            ),
        )
    else:
        intent = render_backtest_analysis_workspace_fallback(
            workspace,
            surface="context",
        )
    consume_backtest_analysis_intent(
        intent,
        allowed_actions=_CONTEXT_ACTIONS,
    )
    _render_backtest_analysis_work_fragment()


@st.fragment
def _render_backtest_analysis_work_fragment() -> None:
    if st.session_state.backtest_analysis_mode == BACKTEST_ANALYSIS_MODE_COMPARE:
        render_compare_portfolio_workspace()
    else:
        if st.session_state.backtest_analysis_mode != BACKTEST_ANALYSIS_MODE_SINGLE:
            st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE
        render_single_strategy_workspace()

    if st.session_state.backtest_analysis_mode == BACKTEST_ANALYSIS_MODE_COMPARE:
        render_backtest_analysis_decision_surface()
