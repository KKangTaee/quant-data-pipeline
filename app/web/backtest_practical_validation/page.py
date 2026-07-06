from __future__ import annotations

from html import escape
from typing import Any

import altair as alt
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
from app.web.backtest_practical_validation.components import (
    render_pv_alert_panel,
    render_pv_card_grid,
    render_pv_command_center,
    render_pv_section_header,
    render_pv_step_rail,
    render_pv_styles,
)
from app.web.backtest_practical_validation.workspace_panel import (
    gate_module_display_rows,
    render_fix_queue,
    render_practical_validation_workspace_overview,
)
from app.web.backtest_practical_validation.status_display import (
    validation_status_label,
    validation_status_tone as _status_tone,
)
from app.web.backtest_ui_components import render_badge_strip
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
    "monitoring_baseline_seed": "모니터링에서 추적할 benchmark, component, review trigger의 기본 seed가 충분한지 확인합니다.",
}


FLOW4_CRITERIA_GROUP_HINTS = (
    "Source & Replay",
    "Data Quality / Bias Control",
    "Comparison Validity",
    "Realism / Tradability",
    "Validation Strength / Robustness",
    "Portfolio Construction",
    "Conditional Evidence",
)


def _diagnostic_explanation(diagnostic: dict[str, Any]) -> str:
    domain = str(diagnostic.get("domain") or "").strip()
    return DIAGNOSTIC_EXPLANATIONS.get(domain, "")


def _source_label(row: dict[str, Any]) -> str:
    return (
        f"{row.get('created_at') or '-'} | "
        f"{row.get('source_kind') or '-'} | "
        f"{row.get('source_title') or row.get('selection_source_id') or '-'}"
    )


def _format_date_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime("%Y-%m-%d")


def _format_percent_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(numeric) <= 2.0:
        return f"{numeric:.2%}"
    return f"{numeric:.2f}%"


def _format_component_summary_df(component_df: pd.DataFrame) -> pd.DataFrame:
    if component_df.empty:
        return component_df
    display_df = component_df.copy()
    if "Weight" in display_df.columns:
        display_df["Weight"] = display_df["Weight"].map(
            lambda value: f"{float(value):.2f}%" if value not in (None, "") else "-"
        )
    for column in ["CAGR", "MDD"]:
        if column in display_df.columns:
            display_df[column] = display_df[column].map(_format_percent_value)
    return display_df


def _format_weight_percent_value(value: Any) -> str:
    numeric = _optional_float_for_display(value)
    if numeric is None:
        return "-"
    if abs(numeric) <= 2.0:
        return f"{numeric:.2%}"
    return f"{numeric:.2f}%"


def _optional_float_for_display(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _list_value(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    if isinstance(value, (list, tuple, set)):
        return [item for item in value if item not in (None, "")]
    text = str(value or "").strip()
    if not text:
        return []
    return [part.strip().strip("'").strip('"') for part in text.strip("[]").split(",") if part.strip()]


def _format_list_value(value: Any, *, max_items: int = 8) -> str:
    items = [str(item).strip() for item in _list_value(value) if str(item).strip()]
    if not items:
        return "-"
    shown = items[:max_items]
    suffix = f" +{len(items) - max_items}" if len(items) > max_items else ""
    return ", ".join(shown) + suffix


def _format_weight_list(value: Any) -> str:
    weights = []
    for item in _list_value(value):
        numeric = _optional_float_for_display(item)
        if numeric is not None:
            weights.append(_format_weight_percent_value(numeric))
    return ", ".join(weights) if weights else "-"


def _format_display_scalar(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, str) and not value.strip():
        return "-"
    if isinstance(value, float) and pd.isna(value):
        return "-"
    if isinstance(value, (list, tuple, set)):
        return _format_list_value(value)
    if isinstance(value, dict):
        return ", ".join(f"{key}: {item}" for key, item in value.items()) or "-"
    return str(value)


def _arrow_safe_display_dataframe(data: Any) -> pd.DataFrame:
    display_df = data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    if display_df.empty:
        return display_df
    for column in display_df.columns:
        if display_df[column].dtype == "object":
            display_df[column] = display_df[column].map(_format_display_scalar)
    return display_df


def _render_display_dataframe(data: Any, **kwargs: Any) -> None:
    st.dataframe(_arrow_safe_display_dataframe(data), **kwargs)


def _component_settings(source: dict[str, Any], component: dict[str, Any]) -> dict[str, Any]:
    source_settings = dict(dict(source.get("source_snapshot") or {}).get("settings_snapshot") or {})
    replay_contract = dict(component.get("replay_contract") or {})
    settings = dict(source_settings)
    settings.update(dict(replay_contract.get("settings_snapshot") or {}))
    settings.update(dict(replay_contract.get("contract") or {}))
    settings.update(dict(component.get("contract") or {}))
    return settings


def _settings_label(settings: dict[str, Any], key: str, default: str = "-") -> str:
    value = settings.get(key)
    if value in (None, "", []):
        return default
    if isinstance(value, dict):
        return ", ".join(f"{k}:{v}" for k, v in value.items()) or default
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value) or default
    return str(value)


def _component_strategy_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for component in list(source.get("components") or []):
        component_row = dict(component or {})
        settings = _component_settings(source, component_row)
        score_horizons = settings.get("score_lookback_months") or settings.get("score_return_columns")
        rows.append(
            {
                "Component": (
                    component_row.get("title")
                    or component_row.get("strategy_name")
                    or component_row.get("component_id")
                    or "-"
                ),
                "Strategy": (
                    component_row.get("strategy_name")
                    or component_row.get("strategy_key")
                    or component_row.get("strategy_family")
                    or "-"
                ),
                "Role": component_row.get("proposal_role") or component_row.get("candidate_role") or "-",
                "Target Weight": _format_weight_percent_value(component_row.get("target_weight")),
                "Benchmark": component_row.get("benchmark") or settings.get("benchmark_ticker") or "-",
                "Universe": _format_list_value(component_row.get("universe") or settings.get("tickers")),
                "Top": _settings_label(settings, "top", "-"),
                "Score Horizons": _format_list_value(score_horizons, max_items=6),
                "Rebalance": _settings_label(settings, "rebalance_freq", None)
                or _settings_label(settings, "factor_freq", None)
                or _settings_label(settings, "rebalance_interval", "-"),
                "Trend / Risk-Off": (
                    f"MA{settings.get('trend_filter_window')} / {settings.get('risk_off_mode')}"
                    if settings.get("trend_filter_window") or settings.get("risk_off_mode")
                    else "-"
                ),
                "Data Trust": component_row.get("data_trust_status") or "-",
            }
        )
    return rows


def _render_source_strategy_brief(source: dict[str, Any]) -> None:
    construction = dict(source.get("construction") or {})
    component_rows = _component_strategy_rows(source)
    component_count = len(component_rows)
    source_type = str(construction.get("source") or source.get("source_kind") or "-")
    selection_rows = _selection_history_rows(source)
    target_weight_total = _optional_float_for_display(construction.get("target_weight_total"))
    render_pv_card_grid(
        [
            {
                "kicker": "Source Strategy",
                "title": source.get("source_title") or source.get("selection_source_id") or "-",
                "status": "Single Strategy" if component_count <= 1 else "Portfolio Mix",
                "detail": f"{source_type} / {component_count} component(s)",
                "tone": "neutral",
            },
            {
                "kicker": "Construction",
                "title": "Target Weight",
                "status": _format_weight_percent_value(construction.get("target_weight_total")),
                "detail": (
                    f"Date policy {construction.get('date_policy') or '-'}, "
                    f"rebalance {construction.get('rebalance_cadence') or '-'}"
                ),
                "tone": (
                    "positive"
                    if target_weight_total is not None and abs(target_weight_total - 100.0) < 0.01
                    else "warning"
                ),
            },
            {
                "kicker": "Selection Evidence",
                "title": "Monthly holdings",
                "status": "Available" if selection_rows else "Not captured",
                "detail": (
                    "Stored source snapshot"
                    if selection_rows
                    else "Run Step 3 replay for legacy sources"
                ),
                "tone": "positive" if selection_rows else "warning",
            },
        ],
        min_width=230,
    )
    if component_rows:
        _render_display_dataframe(pd.DataFrame(component_rows), width="stretch", hide_index=True)


def _format_number_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _source_curve_dataframe(source: dict[str, Any], key: str, label: str) -> pd.DataFrame:
    records = list(source.get(key) or [])
    if not records:
        return pd.DataFrame()
    curve_df = pd.DataFrame(records)
    if curve_df.empty or "Date" not in curve_df.columns or "Total Balance" not in curve_df.columns:
        return pd.DataFrame()
    curve_df = curve_df.copy()
    curve_df["Date"] = pd.to_datetime(curve_df["Date"], errors="coerce")
    curve_df["Total Balance"] = pd.to_numeric(curve_df["Total Balance"], errors="coerce")
    if "Total Return" in curve_df.columns:
        curve_df["Total Return"] = pd.to_numeric(curve_df["Total Return"], errors="coerce")
    else:
        curve_df["Total Return"] = None
    curve_df = curve_df.dropna(subset=["Date", "Total Balance"]).sort_values("Date")
    if curve_df.empty:
        return pd.DataFrame()
    curve_df["Series"] = label
    return curve_df


def _source_backtest_summary_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    summary = dict(source.get("summary") or {})
    period = dict(source.get("period") or {})
    construction = dict(source.get("construction") or {})
    data_trust = dict(source.get("data_trust") or {})
    settings = dict(dict(source.get("source_snapshot") or {}).get("settings_snapshot") or {})
    return [
        {
            "Area": "Performance",
            "Metric": "CAGR",
            "Value": _format_percent_value(summary.get("cagr")),
        },
        {
            "Area": "Performance",
            "Metric": "MDD",
            "Value": _format_percent_value(summary.get("mdd")),
        },
        {
            "Area": "Performance",
            "Metric": "Sharpe",
            "Value": _format_number_value(summary.get("sharpe")),
        },
        {
            "Area": "Performance",
            "Metric": "End Balance",
            "Value": _format_number_value(summary.get("end_balance")),
        },
        {
            "Area": "Period",
            "Metric": "Actual Period",
            "Value": (
                f"{_format_date_value(period.get('actual_start') or period.get('start'))} -> "
                f"{_format_date_value(period.get('actual_end') or period.get('end'))}"
            ),
        },
        {
            "Area": "Contract",
            "Metric": "Benchmark",
            "Value": _format_display_scalar(
                settings.get("benchmark_ticker")
                or next(
                    (
                        str(component.get("benchmark"))
                        for component in list(source.get("components") or [])
                        if component.get("benchmark")
                    ),
                    "-",
                )
            ),
        },
        {
            "Area": "Data",
            "Metric": "Result Rows",
            "Value": _format_display_scalar(
                data_trust.get("result_rows") or len(source.get("result_curve") or [])
            ),
        },
        {
            "Area": "Construction",
            "Metric": "Weight Total",
            "Value": f"{construction.get('target_weight_total', 0)}%",
        },
    ]


def _format_source_result_table(curve_df: pd.DataFrame) -> pd.DataFrame:
    if curve_df.empty:
        return curve_df
    display_df = curve_df.copy()
    display_df["Date"] = display_df["Date"].map(_format_date_value)
    if "Total Balance" in display_df.columns:
        display_df["Total Balance"] = display_df["Total Balance"].map(_format_number_value)
    if "Total Return" in display_df.columns:
        display_df["Total Return"] = display_df["Total Return"].map(_format_percent_value)
    ordered_columns = [
        column
        for column in ["Date", "Total Balance", "Total Return"]
        if column in display_df.columns
    ]
    return display_df[ordered_columns]


def _selection_history_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    root_rows = list(source.get("selection_history") or [])
    if root_rows:
        return [dict(row or {}) for row in root_rows]
    rows: list[dict[str, Any]] = []
    for component in list(source.get("components") or []):
        component_row = dict(component or {})
        title = component_row.get("title") or component_row.get("strategy_name") or component_row.get("component_id")
        component_weight = component_row.get("target_weight")
        for raw_row in list(component_row.get("selection_history") or []):
            row = dict(raw_row or {})
            row.setdefault("component", title)
            row.setdefault("component_weight", component_weight)
            rows.append(row)
    return rows


def _format_selection_history_table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        row_dict = dict(row or {})
        display_rows.append(
            {
                "Date": _format_date_value(row_dict.get("date") or row_dict.get("Date")),
                "Component": row_dict.get("component") or row_dict.get("Component") or "-",
                "Component Weight": _format_weight_percent_value(row_dict.get("component_weight")),
                "Selected Tickers": _format_list_value(
                    row_dict.get("selected_tickers") or row_dict.get("Selected Tickers"),
                    max_items=12,
                ),
                "Target Weights": _format_weight_list(row_dict.get("target_weights") or row_dict.get("Target Weights")),
                "Selected Count": _format_display_scalar(row_dict.get("selected_count")),
                "Raw Selected": _format_list_value(row_dict.get("raw_selected_tickers"), max_items=12),
                "Overlay Rejected": _format_list_value(row_dict.get("overlay_rejected_tickers"), max_items=12),
                "Cash Share": _format_weight_percent_value(row_dict.get("cash_share")),
                "Total Balance": _format_number_value(row_dict.get("total_balance")),
                "Total Return": _format_percent_value(row_dict.get("total_return")),
                "Interpretation": row_dict.get("interpretation") or "-",
            }
        )
    return pd.DataFrame(display_rows)


def _render_source_equity_curve(source: dict[str, Any]) -> None:
    portfolio_df = _source_curve_dataframe(source, "result_curve", "Candidate")
    benchmark_df = _source_curve_dataframe(source, "benchmark_curve", "Benchmark")
    curve_frames = [frame for frame in [portfolio_df, benchmark_df] if not frame.empty]
    if not curve_frames:
        st.info("저장된 backtest equity curve snapshot이 없습니다.")
        return
    chart_df = pd.concat(curve_frames, ignore_index=True)
    chart = (
        alt.Chart(chart_df)
        .mark_line(point=False, strokeWidth=2)
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Total Balance:Q", title="Total Balance", scale=alt.Scale(zero=False)),
            color=alt.Color("Series:N", title=None, legend=alt.Legend(orient="top")),
            tooltip=[
                alt.Tooltip("Date:T", title="Date", format="%Y-%m-%d"),
                alt.Tooltip("Series:N", title="Series"),
                alt.Tooltip("Total Balance:Q", title="Balance", format=",.2f"),
                alt.Tooltip("Total Return:Q", title="Return", format=".2%"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")
    if benchmark_df.empty:
        st.caption("Benchmark curve snapshot이 없어 후보 equity curve만 표시합니다.")


def _render_source_backtest_snapshot(source: dict[str, Any]) -> None:
    summary = dict(source.get("summary") or {})
    data_trust = dict(source.get("data_trust") or {})
    result_curve_df = _source_curve_dataframe(source, "result_curve", "Candidate")
    component_df = source_components_dataframe(source)
    selection_rows = _selection_history_rows(source)
    summary_tab, curve_tab, table_tab, component_tab, selection_tab = st.tabs(
        ["Summary", "Equity Curve", "Result Table", "Components", "Selection History"]
    )
    with summary_tab:
        render_pv_card_grid(
            [
                {
                    "kicker": "Backtest Result",
                    "title": "성과 요약",
                    "status": f"CAGR {_format_percent_value(summary.get('cagr'))}",
                    "detail": (
                        f"MDD {_format_percent_value(summary.get('mdd'))}, "
                        f"Sharpe {_format_number_value(summary.get('sharpe'))}, "
                        f"End {_format_number_value(summary.get('end_balance'))}"
                    ),
                    "tone": "positive",
                },
                {
                    "kicker": "Equity Snapshot",
                    "title": "저장된 curve",
                    "status": f"{len(result_curve_df)} rows",
                    "detail": "Backtest Analysis에서 Practical Validation으로 넘긴 compact result curve입니다.",
                    "tone": "positive" if not result_curve_df.empty else "warning",
                },
                {
                    "kicker": "Data Trust",
                    "title": data_trust.get("status") or "snapshot",
                    "status": f"Warnings {data_trust.get('warning_count', 0)}",
                    "detail": (
                        f"Actual end {_format_date_value(data_trust.get('actual_result_end'))}, "
                        f"excluded {len(data_trust.get('excluded_tickers') or [])}"
                    ),
                    "tone": "warning" if data_trust.get("warning_count") else "neutral",
                },
            ],
            min_width=220,
        )
        _render_display_dataframe(pd.DataFrame(_source_backtest_summary_rows(source)), width="stretch", hide_index=True)
    with curve_tab:
        _render_source_equity_curve(source)
    with table_tab:
        if result_curve_df.empty:
            st.info("표시할 saved result table snapshot이 없습니다.")
        else:
            st.markdown("##### Performance Result")
            _render_display_dataframe(_format_source_result_table(result_curve_df), width="stretch", hide_index=True)
        if selection_rows:
            st.markdown("##### Monthly Selection / Holdings")
            _render_display_dataframe(_format_selection_history_table(selection_rows), width="stretch", hide_index=True)
        else:
            st.info("이 source에는 월별 선택 종목 snapshot이 저장되어 있지 않습니다. 기존 source라면 Step 3 replay 실행 후 재검증 결과에서 확인하세요.")
    with component_tab:
        if component_df.empty:
            st.info("선택된 source에 component snapshot이 없습니다.")
        else:
            _render_display_dataframe(_format_component_summary_df(component_df), width="stretch", hide_index=True)
    with selection_tab:
        if not selection_rows:
            st.info("표시할 selection history snapshot이 없습니다.")
        else:
            _render_display_dataframe(_format_selection_history_table(selection_rows), width="stretch", hide_index=True)


def _render_source_summary(source: dict[str, Any]) -> None:
    summary = dict(source.get("summary") or {})
    period = dict(source.get("period") or {})
    construction = dict(source.get("construction") or {})
    render_badge_strip(
        [
            {"label": "Source", "value": source.get("source_kind") or "-", "tone": "neutral"},
            {
                "label": "Period",
                "value": (
                    f"{_format_date_value(period.get('actual_start') or period.get('start'))} -> "
                    f"{_format_date_value(period.get('actual_end') or period.get('end'))}"
                ),
                "tone": "neutral",
            },
            {"label": "CAGR", "value": _format_percent_value(summary.get("cagr")), "tone": "neutral"},
            {"label": "MDD", "value": _format_percent_value(summary.get("mdd")), "tone": "neutral"},
            {"label": "Weight Total", "value": f"{construction.get('target_weight_total', 0)}%", "tone": "neutral"},
        ]
    )
    _render_source_strategy_brief(source)
    _render_source_backtest_snapshot(source)


def _render_validation_profile_form() -> dict[str, Any]:
    st.caption(
        "검증 프로필은 전략을 다시 만드는 설정이 아니라, 재검증 결과를 어떤 위험 기준으로 판정할지 정합니다."
    )
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
    with st.expander("세부 기준 조정", expanded=False):
        st.caption("목적, 허용 손실, 운용 기간, 상품 복잡도, 비교 기준을 조정하면 같은 replay 결과도 다른 엄격도로 판정합니다.")
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
    thresholds = dict(profile.get("thresholds") or {})
    profile_option = dict(VALIDATION_PROFILE_OPTIONS.get(profile_id) or {})
    render_badge_strip(
        [
            {"label": "Profile", "value": profile.get("profile_label") or "-", "tone": "neutral"},
            {"label": "Rolling", "value": f"{thresholds.get('rolling_window_months')}M", "tone": "neutral"},
            {"label": "Cost", "value": f"{thresholds.get('one_way_cost_bps')} bps", "tone": "neutral"},
            {
                "label": "MDD Line",
                "value": _format_percent_value((thresholds.get("mdd_review_line") or 0.0) / 100.0),
                "tone": "neutral",
            },
        ]
    )
    st.caption(
        f"{profile_option.get('label') or profile.get('profile_label') or '선택한 프로필'} 기준은 "
        f"{profile_option.get('description') or '선택한 위험 기준'}에 맞춰 결과를 판정합니다. "
        f"MDD 약화 신호는 {_format_percent_value((thresholds.get('mdd_review_line') or 0.0) / 100.0)}부터 보며, "
        "최신 재검증, 데이터 커버리지, 비용 / 유동성 근거는 어떤 프로필에서도 생략하지 않습니다."
    )
    return {"profile_id": profile_id, "answers": answers}


def _replay_state_key(source: dict[str, Any], mode: str) -> str:
    return f"practical_validation_recheck_{source.get('selection_source_id') or 'source'}_{mode}"


def _clear_practical_validation_replay_state(source_id: str | None = None) -> None:
    """Clear replay outputs so old validation evidence is not shown as current-session proof."""

    prefix = "practical_validation_recheck_"
    source_prefix = f"{prefix}{source_id}_" if source_id else prefix
    for key in list(st.session_state.keys()):
        key_text = str(key)
        if key_text.startswith("practical_validation_recheck_mode_"):
            continue
        if key_text.startswith(source_prefix):
            del st.session_state[key]


def _render_actual_replay_panel(source: dict[str, Any]) -> dict[str, Any] | None:
    source_id = source.get("selection_source_id") or "source"
    mode = st.radio(
        "재검증 방식",
        options=list(RECHECK_MODE_LABELS.keys()),
        format_func=lambda value: RECHECK_MODE_LABELS.get(value, value),
        horizontal=True,
        key=f"practical_validation_recheck_mode_{source_id}",
    )
    mode_state_key = f"practical_validation_active_recheck_mode_{source_id}"
    if st.session_state.get(mode_state_key) != mode:
        _clear_practical_validation_replay_state(str(source_id))
        st.session_state[mode_state_key] = mode
    recheck_plan = build_practical_validation_recheck_plan(source, mode=mode)
    replay_key = _replay_state_key(source, mode)
    replay_result = st.session_state.get(replay_key)
    render_badge_strip(
        [
            {"label": "Mode", "value": recheck_plan.get("mode_label") or "-", "tone": "neutral"},
            {
                "label": "Stored End",
                "value": _format_date_value(dict(recheck_plan.get("stored_period") or {}).get("end")),
                "tone": "neutral",
            },
            {
                "label": "Recheck End",
                "value": _format_date_value(dict(recheck_plan.get("requested_period") or {}).get("end")),
                "tone": "neutral",
            },
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
        with st.spinner("기존 strategy runtime으로 Practical Validation source를 재검증 중입니다...", show_time=True):
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
                {"label": "CAGR", "value": _format_percent_value(summary.get("cagr")) if summary else "-", "tone": "neutral"},
                {"label": "MDD", "value": _format_percent_value(summary.get("mdd")) if summary else "-", "tone": "neutral"},
            ]
        )
        render_badge_strip(
            [
                {
                    "label": "Coverage",
                    "value": period_coverage.get("status") or "NOT_RUN",
                    "tone": _status_tone(period_coverage.get("status")),
                },
                {"label": "Actual End", "value": _format_date_value(actual_period.get("end")), "tone": "neutral"},
                {"label": "End Gap", "value": f"{period_coverage.get('end_gap_days', '-')} days", "tone": "neutral"},
                {"label": "Latest DB", "value": _format_date_value(replay_result.get("latest_market_date")), "tone": "neutral"},
            ]
        )
        if period_coverage.get("summary"):
            st.caption(str(period_coverage.get("summary")))
        component_rows = list(replay_result.get("component_results") or [])
        if component_rows:
            _render_display_dataframe(
                pd.DataFrame(
                    [
                        {
                            "Component": row.get("title"),
                            "Strategy": row.get("strategy_key"),
                            "Weight": row.get("target_weight"),
                            "Status": row.get("status"),
                            "Rows": row.get("result_rows"),
                            "Requested Start": _format_date_value(row.get("requested_start")),
                            "Requested End": _format_date_value(row.get("requested_end")),
                            "Start": _format_date_value(row.get("actual_start")),
                            "End": _format_date_value(row.get("actual_end")),
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
            _render_display_dataframe(pd.DataFrame(coverage_rows), width="stretch", hide_index=True)
        replay_selection_rows: list[dict[str, Any]] = []
        for row in component_rows:
            component_title = row.get("title") or row.get("component_id")
            component_weight = row.get("target_weight")
            for raw_selection_row in list(row.get("selection_history") or []):
                selection_row = dict(raw_selection_row or {})
                selection_row.setdefault("component", component_title)
                selection_row.setdefault("component_weight", component_weight)
                replay_selection_rows.append(selection_row)
        if replay_selection_rows:
            with st.expander("Runtime replay monthly selection / holdings", expanded=False):
                _render_display_dataframe(_format_selection_history_table(replay_selection_rows), width="stretch", hide_index=True)
    else:
        st.info("이 탭의 현재 세션에서는 아직 최신 runtime 재검증을 실행하지 않았습니다. 버튼을 눌러야 결과가 표시됩니다.")
    return dict(replay_result) if isinstance(replay_result, dict) else None


def _entry_gate_effect_label(effect: Any) -> str:
    mapping = {
        "block": "먼저 해결",
        "review": "2차 확인",
        "pass": "통과",
        "context": "참고",
    }
    effect_text = str(effect or "").strip().lower()
    return mapping.get(effect_text, str(effect or "-"))


def _entry_gate_effect_tone(effect: Any) -> str:
    effect_text = str(effect or "").strip().lower()
    if effect_text == "block":
        return "danger"
    if effect_text == "review":
        return "warning"
    if effect_text == "pass":
        return "positive"
    return "neutral"


def _entry_gate_display_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def text(value: Any, fallback: str = "-") -> str:
        value_text = str(value or "").strip()
        return value_text or fallback

    return [
        {
            "구분": text(row.get("group")),
            "신호": text(row.get("signal")),
            "상태": text(row.get("status")),
            "판정": _entry_gate_effect_label(row.get("effect")),
            "확인 위치": text(row.get("next_surface"), "Practical Validation"),
            "확인할 것": text(row.get("checked_evidence")),
            "표시 근거": text(row.get("display_detail") or row.get("meaning")),
            "의미": text(row.get("meaning")),
        }
        for row in rows
    ]


def _entry_gate_card_detail(row: dict[str, Any]) -> str:
    checked = str(row.get("checked_evidence") or "").strip() or "Practical Validation에서 확인할 근거"
    detail = str(row.get("display_detail") or row.get("meaning") or "").strip() or "2차에서 확인할 review 신호입니다."
    return f"확인할 것: {checked}. {detail}"


def _render_backtest_entry_gate_review_queue(source: dict[str, Any]) -> None:
    entry_gate = dict(source.get("entry_gate") or {})
    if not entry_gate:
        return

    review_rows = [dict(row or {}) for row in list(entry_gate.get("review_focus_rows") or [])]
    blocker_rows = [dict(row or {}) for row in list(entry_gate.get("blocker_rows") or [])]
    can_enter = bool(entry_gate.get("can_enter_practical_validation"))
    review_count = int(entry_gate.get("review_focus_count") or len(review_rows))
    blocker_count = int(entry_gate.get("blocker_count") or len(blocker_rows))
    tone = "danger" if blocker_count or not can_enter else "warning" if review_count else "positive"

    render_pv_alert_panel(
        title="Backtest에서 넘어온 2차 확인 항목",
        detail=(
            "1차 화면에서는 source 등록을 막는 항목만 확인했고, "
            "실전성 판단에 필요한 review 신호는 이 화면에서 이어서 확인합니다."
        ),
        tone=tone,
    )
    render_pv_card_grid(
        [
            {
                "kicker": "Entry Gate",
                "title": "2차 진입",
                "status": "가능" if can_enter and not blocker_count else "보류",
                "detail": entry_gate.get("verdict") or entry_gate.get("route_label") or "-",
                "tone": "positive" if can_enter and not blocker_count else "danger",
            },
            {
                "kicker": "먼저 해결",
                "title": f"{blocker_count}개",
                "status": "없음" if not blocker_count else "확인 필요",
                "detail": "source 등록을 막는 hard blocker입니다.",
                "tone": "positive" if not blocker_count else "danger",
            },
            {
                "kicker": "2차 확인",
                "title": f"{review_count}개",
                "status": "검증 큐" if review_count else "없음",
                "detail": "Promotion hold, 운용성, 검증 근거, 비용 / 기간 확인 항목입니다.",
                "tone": "warning" if review_count else "positive",
            },
            {
                "kicker": "Compare Gate",
                "title": "가능" if entry_gate.get("can_move_to_compare") else "보류",
                "status": "Portfolio Mix strict gate",
                "detail": "Portfolio Mix 비교 가능성은 Practical Validation 진입 기준보다 보수적으로 봅니다.",
                "tone": "positive" if entry_gate.get("can_move_to_compare") else "neutral",
            },
        ],
        min_width=190,
    )

    if blocker_rows:
        render_pv_card_grid(
            [
                {
                    "kicker": row.get("group") or "Blocker",
                    "title": row.get("signal") or "-",
                    "status": row.get("status") or "-",
                    "detail": row.get("meaning") or "source 등록 전 먼저 해결해야 하는 항목입니다.",
                    "meta": row.get("next_surface") or "Backtest Analysis",
                    "tone": "danger",
                }
                for row in blocker_rows
            ],
            min_width=250,
        )

    if review_rows:
        render_pv_card_grid(
            [
                {
                    "kicker": row.get("group") or "Review",
                    "title": row.get("signal") or "-",
                    "status": row.get("status") or "-",
                    "detail": _entry_gate_card_detail(row),
                    "meta": row.get("next_surface") or "Practical Validation",
                    "tone": _entry_gate_effect_tone(row.get("effect")),
                }
                for row in review_rows
            ],
            min_width=250,
        )
        with st.expander("2차 확인 항목 상세 테이블", expanded=False):
            _render_display_dataframe(pd.DataFrame(_entry_gate_display_rows(review_rows)), width="stretch", hide_index=True)
    elif not blocker_rows:
        st.success("Backtest에서 넘어온 2차 확인 항목이 없습니다. 아래 source snapshot과 최신 재검증을 이어서 확인하세요.")


def _table_status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("Status") or row.get("status") or "-").upper()
        counts[status] = counts.get(status, 0) + 1
    return counts


def _audit_status_summary(rows: list[dict[str, Any]]) -> str:
    counts = _table_status_counts(rows)
    if not counts:
        return "No rows"
    order = ["BLOCKED", "NEEDS_INPUT", "NOT_RUN", "REVIEW", "PASS"]
    parts = [f"{key} {counts[key]}" for key in order if counts.get(key)]
    return " / ".join(parts) if parts else f"{len(rows)} rows"


def _board_summary_cards(validation_result: dict[str, Any], board_ids: list[str]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for board_id in board_ids:
        row = _validation_board_row(validation_result, board_id)
        if not row:
            continue
        applies = str(row.get("Applies") or "").lower() == "yes"
        status = row.get("Status") if applies else "NOT_APPLICABLE"
        cards.append(
            {
                "kicker": row.get("Board Type") or "Evidence Board",
                "title": row.get("Board") or board_id,
                "status": status,
                "detail": row.get("Why It Appears") or row.get("Applicability") or "",
                "meta": f"Feeds: {row.get('Feeds Modules') or '-'}",
                "tone": _status_tone(status) if applies else "neutral",
            }
        )
    return cards


def _validation_board_row(validation_result: dict[str, Any], board_id: str) -> dict[str, Any]:
    target = str(board_id or "").strip()
    for row in list(validation_result.get("validation_board_display_rows") or []):
        row_dict = dict(row or {})
        if str(row_dict.get("Board ID") or "").strip() == target:
            return row_dict
    return {}


def _board_applies(validation_result: dict[str, Any], board_id: str) -> bool:
    row = _validation_board_row(validation_result, board_id)
    if not row:
        return True
    return str(row.get("Applies") or "").lower() == "yes"


def _board_feed_count(row: dict[str, Any]) -> int:
    feeds = str(row.get("Feeds Modules") or "").strip()
    if not feeds or feeds == "-":
        return 0
    return len([item for item in feeds.split(" / ") if item.strip()])


def _board_gate_badge_value(row: dict[str, Any]) -> str:
    gate_effects = str(row.get("Gate Effects") or "").strip()
    if not gate_effects or gate_effects == "-":
        return "Not applicable"
    effects = [item.strip() for item in gate_effects.split(" / ") if item.strip()]
    if len(dict.fromkeys(effects)) > 1:
        return "Mixed"
    return effects[0]


def _render_board_context_badges(validation_result: dict[str, Any], board_id: str) -> None:
    row = _validation_board_row(validation_result, board_id)
    if not row:
        return
    applies = str(row.get("Applies") or "").lower() == "yes"
    render_badge_strip(
        [
            {"label": "Board Type", "value": row.get("Board Type") or "-", "tone": "neutral"},
            {
                "label": "Applies",
                "value": "Yes" if applies else "No",
                "tone": "positive" if applies else "neutral",
            },
            {"label": "Feeds", "value": _board_feed_count(row), "tone": "neutral"},
            {
                "label": "Gate",
                "value": _board_gate_badge_value(row),
                "tone": _status_tone(row.get("Status")),
            },
        ]
    )
    if row.get("Why It Appears"):
        st.caption(str(row.get("Why It Appears")))


def _render_not_applicable_board(
    validation_result: dict[str, Any],
    board_id: str,
    title: str,
) -> bool:
    row = _validation_board_row(validation_result, board_id)
    if not row or _board_applies(validation_result, board_id):
        return False
    with st.expander(f"{title} - Not applicable", expanded=False):
        _render_board_context_badges(validation_result, board_id)
        st.caption(str(row.get("Applicability") or "현재 후보 특성상 이 보드는 적용하지 않습니다."))
    return True


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
    _render_display_dataframe(
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


def _render_provider_gap_section(validation_result: dict[str, Any]) -> bool:
    gap_rows = build_provider_gap_rows(validation_result)
    if not gap_rows:
        return False

    plan = build_provider_gap_collection_plan(validation_result)
    actionable_rows = [row for row in gap_rows if str(row.get("Action") or "") != "조치 없음"]
    collectable_count = sum(
        len(plan[key])
        for key in [
            "operability_official",
            "operability_bridge",
            "holdings_exposure",
            "source_map_discovery",
        ]
        if isinstance(plan.get(key), list)
    ) + (1 if plan.get("macro") else 0)
    render_pv_section_header(
        eyebrow="Action center",
        title="Provider 보강 액션",
        detail="ETF provider snapshot 부족분을 요약하고, 수집 가능한 항목과 connector 보강이 필요한 항목을 분리합니다.",
        tone="warning" if actionable_rows else "positive",
    )
    render_pv_card_grid(
        [
            {
                "kicker": "Gap Status",
                "title": "Provider data gaps",
                "status": f"{len(actionable_rows)} actionable",
                "detail": f"전체 {len(gap_rows)}개 row 중 보강 액션이 필요한 항목입니다.",
                "tone": "warning" if actionable_rows else "positive",
            },
            {
                "kicker": "Collectable Now",
                "title": "수집 / 보강 가능",
                "status": collectable_count,
                "detail": "source map discovery, official operability, DB bridge, holdings / exposure, macro context 기준입니다.",
                "tone": "positive" if collectable_count else "neutral",
            },
            {
                "kicker": "Connector Work",
                "title": "Mapping needed",
                "status": len(plan["mapping_needed"]),
                "detail": "검증된 issuer URL / parser mapping이 없으면 수동 connector 보강이 필요합니다.",
                "tone": "warning" if plan["mapping_needed"] else "neutral",
            },
        ],
        min_width=220,
    )

    st.markdown("##### Provider Data Gaps")
    with st.expander("Provider Data Gaps 상세", expanded=bool(actionable_rows)):
        _render_board_context_badges(validation_result, "provider_data_gaps")
        st.caption(
            "현재 source에 필요한 ETF별 provider 데이터가 어디까지 채워졌는지 보여줍니다. "
            "부족 데이터는 이 화면에서 바로 수집할 수 있고, source mapping이 없는 ETF는 connector 보강이 필요합니다."
        )
        _render_display_dataframe(pd.DataFrame(gap_rows), width="stretch", hide_index=True)
    if not any(str(row.get("Action") or "") != "조치 없음" for row in gap_rows):
        st.success("현재 ETF provider gap은 없습니다.")
        return True

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
    render_pv_card_grid(
        [
            {
                "kicker": row["Area"],
                "title": row["Symbols"],
                "status": "No immediate action" if row["Symbols"] == "-" else "Action available",
                "detail": row["Meaning"],
                "tone": "neutral" if row["Symbols"] == "-" else "warning",
            }
            for row in action_rows
        ],
        min_width=250,
    )
    with st.expander("보강 작업 상세 테이블", expanded=False):
        _render_display_dataframe(pd.DataFrame(action_rows), width="stretch", hide_index=True)

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
        return True

    if st.button("부족한 Provider 데이터 일괄 수집 / 보강", key=f"{result_key}_run", width="stretch"):
        with st.spinner("현재 source에 필요한 provider snapshot을 수집 / 보강 중입니다...", show_time=True):
            results = run_provider_gap_collection(validation_result)
        st.session_state[result_key] = results
        st.rerun()
    return True


def _provider_look_through_board(validation_result: dict[str, Any]) -> dict[str, Any]:
    board = dict(validation_result.get("provider_look_through_board") or {})
    if board:
        return board
    provider_context = dict(validation_result.get("provider_coverage") or {})
    return dict(provider_context.get("look_through_board") or {})


def _render_provider_look_through_board(validation_result: dict[str, Any]) -> None:
    if _render_not_applicable_board(validation_result, "look_through_exposure", "Look-through Exposure Board"):
        return
    board = _provider_look_through_board(validation_result)
    if not board:
        return

    st.markdown("##### Look-through Exposure Board")
    _render_board_context_badges(validation_result, "look_through_exposure")
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
        _render_display_dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)

    tabs = st.tabs(["Asset Buckets", "Top Holdings", "Fund Coverage", "Exposure Detail"])
    with tabs[0]:
        asset_rows = list(board.get("asset_bucket_rows") or [])
        if asset_rows:
            _render_display_dataframe(pd.DataFrame(asset_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 asset bucket exposure가 없습니다.")
    with tabs[1]:
        holding_rows = list(board.get("top_holding_rows") or [])
        if holding_rows:
            _render_display_dataframe(pd.DataFrame(holding_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 top holdings row가 없습니다.")
    with tabs[2]:
        fund_rows = list(board.get("fund_coverage_rows") or [])
        if fund_rows:
            _render_display_dataframe(pd.DataFrame(fund_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 ETF별 coverage row가 없습니다.")
    with tabs[3]:
        exposure_rows = list(board.get("exposure_detail_rows") or [])
        if exposure_rows:
            _render_display_dataframe(pd.DataFrame(exposure_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 exposure detail row가 없습니다.")

    limitations = list(board.get("limitations") or [])
    if limitations:
        st.caption("Limitations: " + " / ".join(str(item) for item in limitations))


def _robustness_lab_board(validation_result: dict[str, Any]) -> dict[str, Any]:
    robustness = dict(validation_result.get("robustness_validation") or {})
    board = dict(robustness.get("robustness_lab_board") or validation_result.get("robustness_lab_board") or {})
    return board


def _render_robustness_lab_board(
    board: dict[str, Any],
    validation_result: dict[str, Any] | None = None,
) -> None:
    metrics = dict(board.get("metrics") or {})
    st.markdown("##### Robustness Lab")
    if validation_result is not None:
        _render_board_context_badges(validation_result, "robustness_lab")
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
            _render_display_dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 robustness summary row가 없습니다.")
    with stress_tab:
        stress_rows = list(board.get("stress_rows") or [])
        if stress_rows:
            _render_display_dataframe(pd.DataFrame(stress_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 stress detail row가 없습니다.")
    with sensitivity_tab:
        sensitivity_rows = list(board.get("sensitivity_rows") or [])
        if sensitivity_rows:
            _render_display_dataframe(pd.DataFrame(sensitivity_rows), width="stretch", hide_index=True)
        else:
            st.info("표시할 sensitivity detail row가 없습니다.")
    with follow_up_tab:
        follow_up_rows = list(board.get("follow_up_rows") or [])
        if follow_up_rows:
            _render_display_dataframe(pd.DataFrame(follow_up_rows), width="stretch", hide_index=True)
        else:
            st.success("즉시 follow-up으로 남은 robustness row가 없습니다.")

    limitations = list(board.get("limitations") or [])
    if limitations:
        st.caption("Limitations: " + " / ".join(str(item) for item in limitations))


def _render_stress_sensitivity_interpretation(validation_result: dict[str, Any]) -> None:
    board = _robustness_lab_board(validation_result)
    if board:
        _render_robustness_lab_board(board, validation_result)
        return

    stress = dict(validation_result.get("stress_interpretation") or {})
    sensitivity = dict(validation_result.get("sensitivity_interpretation") or {})
    if not stress and not sensitivity:
        return

    st.markdown("##### Stress / Sensitivity Interpretation")
    _render_board_context_badges(validation_result, "robustness_lab")
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
            _render_display_dataframe(pd.DataFrame(stress_rows), width="stretch", hide_index=True)
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
            _render_display_dataframe(pd.DataFrame(sensitivity_rows), width="stretch", hide_index=True)


def _render_applied_validation_map(validation_result: dict[str, Any]) -> None:
    applied_rows = list(validation_result.get("applied_validation_board_display_rows") or [])
    skipped_rows = list(validation_result.get("not_applicable_validation_board_display_rows") or [])
    module_rows = list(validation_result.get("validation_module_display_rows") or [])
    summary = dict(validation_result.get("validation_board_summary") or {})
    if not applied_rows and not skipped_rows:
        return

    with st.expander("검증-근거 연결 지도", expanded=False):
        st.caption(
            "이 표는 화면 보드가 어떤 검증 모듈의 근거인지 보여주는 보조 지도입니다. "
            "Final Review 이동 판단은 검증 결론과 Gate 상태를 함께 봅니다."
        )
        render_badge_strip(
            [
                {"label": "Applied Boards", "value": summary.get("applied", len(applied_rows)), "tone": "positive"},
                {
                    "label": "Skipped Boards",
                    "value": summary.get("not_applicable", len(skipped_rows)),
                    "tone": "neutral",
                },
                {"label": "Required Links", "value": summary.get("required_boards", 0), "tone": "neutral"},
                {
                    "label": "Conditional Links",
                    "value": summary.get("conditional_boards", 0),
                    "tone": "neutral",
                },
            ]
        )
        map_tab, skipped_tab, module_tab = st.tabs(["적용 보드", "비적용 보드", "모듈 연결"])
        with map_tab:
            if applied_rows:
                _render_display_dataframe(
                    pd.DataFrame(applied_rows)[
                        [
                            "Board",
                            "Board Type",
                            "Module Types",
                            "Feeds Modules",
                            "Gate Effects",
                            "Why It Appears",
                        ]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.info("현재 후보에 적용되는 보드가 없습니다.")
        with skipped_tab:
            if skipped_rows:
                _render_display_dataframe(
                    pd.DataFrame(skipped_rows)[
                        [
                            "Board",
                            "Board Type",
                            "Applicability",
                            "Primary Modules",
                            "Why It Appears",
                        ]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.success("현재 후보에서 제외되는 조건부 보드가 없습니다.")
        with module_tab:
            if module_rows:
                _render_display_dataframe(
                    pd.DataFrame(module_rows)[
                        [
                            "Module",
                            "Module Type",
                            "Applies",
                            "Status",
                            "Gate Effect",
                            "Evidence Boards",
                        ]
                    ],
                    width="stretch",
                    hide_index=True,
                )


def _render_validation_module_board(validation_result: dict[str, Any]) -> None:
    gate = dict(validation_result.get("final_review_gate") or {})
    summary = dict(validation_result.get("validation_module_summary") or {})
    status_counts = dict(summary.get("status_counts") or {})
    traits = dict(validation_result.get("source_traits") or {})
    module_rows = list(validation_result.get("validation_module_display_rows") or [])

    st.markdown("##### Final Review 이동 요약")
    _render_board_context_badges(validation_result, "final_review_gate")
    render_badge_strip(
        [
            {
                "label": "Gate",
                "value": validation_status_label(gate.get("route")),
                "tone": _status_tone(gate.get("route")),
            },
            {
                "label": "Move",
                "value": "Enabled" if gate.get("can_save_and_move") else "Blocked",
                "tone": "positive" if gate.get("can_save_and_move") else "danger",
            },
            {"label": "Required", "value": summary.get("required", 0), "tone": "neutral"},
            {
                "label": "Blocking",
                "value": len(gate.get("blocking_modules") or []),
                "tone": "danger" if gate.get("blocking_modules") else "positive",
            },
            {
                "label": "Review",
                "value": len(gate.get("review_modules") or []),
                "tone": "warning" if gate.get("review_modules") else "neutral",
            },
        ]
    )
    st.caption(str(gate.get("verdict") or ""))
    st.caption(
        "Gate Effect는 Final Review 이동 영향입니다. `Blocks Final Review`는 먼저 보강하고, "
        "`Final Review review`는 이동 후 최종 판단 근거로 확인합니다."
    )
    render_badge_strip(
        [
            {
                "label": "Traits",
                "value": " / ".join(
                    label
                    for label, enabled in [
                        ("ETF-like", traits.get("is_etf_like")),
                        ("Tactical", traits.get("is_tactical")),
                        ("Weighted Mix", traits.get("is_weighted_mix")),
                        ("Factor", traits.get("is_factor_equity")),
                    ]
                    if enabled
                )
                or "Basic",
                "tone": "neutral",
            },
            {"label": "Components", "value": traits.get("active_component_count", 0), "tone": "neutral"},
            {"label": "Symbols", "value": traits.get("symbol_count", 0), "tone": "neutral"},
            {"label": "PASS", "value": status_counts.get("PASS", 0), "tone": "positive"},
            {"label": "NEEDS_INPUT", "value": status_counts.get("NEEDS_INPUT", 0), "tone": "warning"},
        ]
    )

    _render_applied_validation_map(validation_result)

    blocking_modules = list(gate.get("blocking_modules") or [])
    render_fix_queue(blocking_modules)
    if blocking_modules:
        with st.expander("이동 보류 모듈 상세 테이블", expanded=False):
            _render_display_dataframe(pd.DataFrame(gate_module_display_rows(blocking_modules)), width="stretch", hide_index=True)
    review_modules = list(gate.get("review_modules") or [])
    if review_modules:
        with st.expander("Final Review에서 확인할 REVIEW 모듈", expanded=False):
            _render_display_dataframe(pd.DataFrame(gate_module_display_rows(review_modules)), width="stretch", hide_index=True)

    if module_rows:
        required_rows = [row for row in module_rows if row.get("Group") == "Required for Final Review"]
        conditional_rows = [row for row in module_rows if row.get("Group") == "Conditional / Strategy-specific"]
        reference_rows = [row for row in module_rows if row.get("Group") == "Downstream Reference"]
        render_pv_card_grid(
            [
                {
                    "kicker": "Required",
                    "title": "필수 검증",
                    "status": _audit_status_summary(required_rows),
                    "detail": "Final Review 이동을 직접 막는 모듈입니다.",
                    "tone": "danger" if blocking_modules else "positive",
                },
                {
                    "kicker": "Conditional",
                    "title": "조건부 / 전략별 검증",
                    "status": _audit_status_summary(conditional_rows),
                    "detail": "ETF-like, tactical, weighted mix 같은 후보 특성에 따라 적용됩니다.",
                    "tone": "warning" if conditional_rows else "neutral",
                },
                {
                    "kicker": "Reference",
                    "title": "후속 참고",
                    "status": _audit_status_summary(reference_rows),
                    "detail": "Final Review 또는 Selected Dashboard에서 이어서 읽는 참고 근거입니다.",
                    "tone": "neutral",
                },
            ],
            min_width=220,
        )
        with st.expander("검증 모듈 상세", expanded=False):
            required_tab, conditional_tab, reference_tab = st.tabs(["필수 검증", "조건부 검증", "후속 참고"])
            with required_tab:
                _render_display_dataframe(pd.DataFrame(required_rows), width="stretch", hide_index=True)
            with conditional_tab:
                _render_display_dataframe(pd.DataFrame(conditional_rows), width="stretch", hide_index=True)
            with reference_tab:
                _render_display_dataframe(pd.DataFrame(reference_rows), width="stretch", hide_index=True)

    with st.expander("Source traits", expanded=False):
        st.json(traits)


def _render_validation_gate_section(validation_result: dict[str, Any]) -> None:
    profile = dict(validation_result.get("validation_profile") or {})
    gate = dict(validation_result.get("final_review_gate") or {})
    status_counts = dict(dict(validation_result.get("diagnostic_summary") or {}).get("status_counts") or {})
    route_status = gate.get("route") or validation_result.get("validation_route")
    route_label = validation_status_label(route_status)
    blocker_count = len(gate.get("blocking_modules") or validation_result.get("hard_blockers") or [])
    render_pv_alert_panel(
        title=f"Gate: {route_label}",
        detail=(
            f"Validation score {float(validation_result.get('validation_score') or 0.0):.2f}. "
            f"Blocking modules {blocker_count}. "
            f"{gate.get('verdict') or validation_result.get('verdict') or ''} "
            f"{gate.get('next_action') or validation_result.get('next_action') or ''}"
        ).strip(),
        tone=_status_tone(route_label),
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
    _render_validation_module_board(validation_result)


def _render_validation_alerts(validation_result: dict[str, Any]) -> None:
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
        _render_display_dataframe(pd.DataFrame(not_run_critical), width="stretch", hide_index=True)


def _render_curve_evidence(validation_result: dict[str, Any]) -> None:
    curve_evidence = dict(validation_result.get("curve_evidence") or {})
    if not curve_evidence:
        st.info("표시할 curve / recheck evidence가 없습니다.")
        return
    st.markdown("##### Curve / Recheck Evidence")
    render_badge_strip(
        [
            {
                "label": "Portfolio Curve",
                "value": curve_evidence.get("portfolio_curve_source") or "-",
                "tone": "positive" if curve_evidence.get("portfolio_curve_rows") else "warning",
            },
            {"label": "Rows", "value": curve_evidence.get("portfolio_curve_rows", 0), "tone": "neutral"},
            {"label": "Benchmark", "value": curve_evidence.get("benchmark_ticker") or "-", "tone": "neutral"},
            {"label": "Benchmark Rows", "value": curve_evidence.get("benchmark_curve_rows", 0), "tone": "neutral"},
        ]
    )
    component_curve_rows = list(curve_evidence.get("component_curve_rows") or [])
    if component_curve_rows:
        _render_display_dataframe(pd.DataFrame(component_curve_rows), width="stretch", hide_index=True)
    benchmark_parity = dict(curve_evidence.get("benchmark_parity") or {})
    if benchmark_parity:
        render_badge_strip(
            [
                {
                    "label": "Benchmark / Comparator Parity",
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
            _render_display_dataframe(pd.DataFrame(parity_rows), width="stretch", hide_index=True)
    curve_provenance = dict(curve_evidence.get("curve_provenance") or {})
    if curve_provenance:
        with st.expander("Curve provenance", expanded=False):
            st.json(curve_provenance)


def _render_diagnostic_detail_expanders(validation_result: dict[str, Any]) -> None:
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
                _render_display_dataframe(pd.DataFrame(evidence_rows), width="stretch", hide_index=True)
            limitations = list(diagnostic.get("limitations") or [])
            if limitations:
                st.caption("Limitations: " + " / ".join(str(item) for item in limitations))
    profile_score_rows = list(validation_result.get("profile_score_rows") or [])
    if profile_score_rows:
        with st.expander("Profile-aware score breakdown", expanded=False):
            _render_display_dataframe(pd.DataFrame(profile_score_rows), width="stretch", hide_index=True)


def _render_practical_diagnostics_summary(validation_result: dict[str, Any]) -> None:
    st.markdown("##### Practical Diagnostics")
    _render_board_context_badges(validation_result, "practical_diagnostics")
    diagnostic_rows = list(validation_result.get("diagnostic_display_rows") or [])
    if diagnostic_rows:
        render_pv_card_grid(
            [
                {
                    "kicker": "Diagnostics",
                    "title": "Practical diagnostics rows",
                    "status": _audit_status_summary(diagnostic_rows),
                    "detail": "프로필과 source traits에 따라 실전성 진단 row를 compact하게 요약합니다.",
                    "tone": "warning" if any(str(row.get("Status") or "").upper() != "PASS" for row in diagnostic_rows) else "positive",
                }
            ],
            min_width=240,
        )
        with st.expander("Practical Diagnostics 상세", expanded=False):
            _render_display_dataframe(pd.DataFrame(diagnostic_rows), width="stretch", hide_index=True)
    else:
        st.info("표시할 diagnostic row가 없습니다.")


def _render_validation_evidence_boards(validation_result: dict[str, Any]) -> None:
    render_pv_section_header(
        eyebrow="Evidence workspace",
        title="검증 근거 보드",
        detail="요약 카드로 먼저 판단하고, 상세 테이블과 raw evidence는 필요한 탭에서 펼쳐 확인합니다.",
        tone="neutral",
    )
    render_pv_card_grid(
        _board_summary_cards(
            validation_result,
            [
                "input_evidence",
                "validation_efficacy_audit",
                "data_coverage_audit",
                "construction_risk_audit",
                "backtest_realism_audit",
                "robustness_lab",
            ],
        ),
        min_width=230,
    )
    summary_tab, data_tab, construction_tab, realism_tab, robustness_tab, raw_tab = st.tabs(
        ["핵심 근거", "데이터", "구성 / 리스크", "실전성", "강건성", "Raw Evidence"]
    )
    with summary_tab:
        st.markdown("##### Input Evidence")
        _render_board_context_badges(validation_result, "input_evidence")
        checks = list(validation_result.get("checks") or [])
        render_pv_card_grid(
            [
                {
                    "kicker": "Input",
                    "title": "Source / Replay / Comparator",
                    "status": _audit_status_summary(checks),
                    "detail": "source 자격, 최신 재검증, 비교 기준 동등성의 기본 입력 근거입니다.",
                    "tone": "warning" if any(not bool(row.get("Ready")) for row in checks) else "positive",
                }
            ],
            min_width=240,
        )
        with st.expander("Input Evidence 상세", expanded=False):
            _render_display_dataframe(pd.DataFrame(checks), width="stretch", hide_index=True)
        with st.expander("Curve / Recheck Evidence", expanded=False):
            _render_curve_evidence(validation_result)
        _render_validation_alerts(validation_result)
    with data_tab:
        with st.expander("Data Coverage Audit 상세", expanded=False):
            _render_data_coverage_audit(validation_result)
        provider_rows = list(validation_result.get("provider_coverage_display_rows") or [])
        if provider_rows:
            st.markdown("##### Provider Coverage")
            _render_board_context_badges(validation_result, "provider_coverage")
            st.caption(
                "Ingestion에서 저장한 ETF provider / FRED snapshot이 Practical Diagnostics에 어떻게 연결됐는지 보여줍니다."
            )
            render_pv_card_grid(
                [
                    {
                        "kicker": "Provider Coverage",
                        "title": "ETF / macro evidence",
                        "status": _audit_status_summary(provider_rows),
                        "detail": "provider freshness, operability, holdings / exposure coverage를 compact하게 확인합니다.",
                        "tone": "warning"
                        if any(str(row.get("Status") or "").upper() != "PASS" for row in provider_rows)
                        else "positive",
                    }
                ],
                min_width=240,
            )
            with st.expander("Provider Coverage 상세", expanded=False):
                _render_display_dataframe(pd.DataFrame(provider_rows), width="stretch", hide_index=True)
            _render_provider_look_through_board(validation_result)
    with construction_tab:
        with st.expander("Construction Risk Audit 상세", expanded=False):
            _render_construction_risk_audit(validation_result)
        with st.expander("Risk Contribution Audit 상세", expanded=False):
            _render_risk_contribution_audit(validation_result)
        with st.expander("Component Role / Weight Audit 상세", expanded=False):
            _render_component_role_weight_audit(validation_result)
    with realism_tab:
        with st.expander("Validation Efficacy Audit 상세", expanded=False):
            _render_validation_efficacy_audit(validation_result)
        with st.expander("Backtest Realism Audit 상세", expanded=False):
            _render_backtest_realism_audit(validation_result)
        _render_practical_diagnostics_summary(validation_result)
    with robustness_tab:
        with st.expander("Robustness Lab 상세", expanded=False):
            _render_stress_sensitivity_interpretation(validation_result)
    with raw_tab:
        _render_diagnostic_detail_expanders(validation_result)


def _render_validation_action_boards(validation_result: dict[str, Any]) -> None:
    provider_rows = list(validation_result.get("provider_coverage_display_rows") or [])
    rendered = _render_provider_gap_section(validation_result) if provider_rows else False
    if not rendered:
        st.info("현재 후보에서 실행할 provider 보강 액션이 없습니다.")


def _render_validation_criteria_detail_board(validation_result: dict[str, Any]) -> None:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    summary = dict(workspace.get("summary") or {})
    gate_summary = dict(workspace.get("gate_summary") or validation_result.get("final_review_gate") or {})
    groups = [dict(group or {}) for group in list(workspace.get("criteria_detail_groups") or [])]
    handoff_groups = [dict(group or {}) for group in list(workspace.get("handoff_summary_groups") or [])]
    if not groups:
        return
    group_order = {label: index for index, label in enumerate(FLOW4_CRITERIA_GROUP_HINTS)}
    groups.sort(key=lambda group: group_order.get(str(group.get("label") or ""), len(group_order)))

    blocker_count = int(summary.get("criteria_blocker_count") or summary.get("fix_item_count") or 0)
    review_count = int(summary.get("criteria_review_count") or gate_summary.get("review_count") or 0)
    pass_count = int(summary.get("criteria_pass_count") or 0)
    evidence_count = int(summary.get("criteria_card_count") or 0)
    tone = _status_tone(gate_summary.get("route") or validation_result.get("validation_route"))
    if blocker_count:
        headline = f"보강이 필요한 검증 항목 {blocker_count}개가 남아 있습니다."
    elif review_count:
        headline = f"Final Review에서 확인할 기준 {review_count}개가 남아 있습니다."
    else:
        headline = "카테고리별 검증 결과가 모두 통과 상태입니다."

    metric_rows = [
        ("보강 필요", str(blocker_count), "검증 항목"),
        ("통과", str(pass_count), "PASS 기준"),
        ("Final Review 확인", str(review_count), "REVIEW 기준"),
        ("검증 항목", str(evidence_count), "criteria cards"),
    ]
    metric_html = "".join(
        '<div class="pv-criteria-metric">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<span>{escape(detail)}</span>"
        "</div>"
        for label, value, detail in metric_rows
    )

    group_html: list[str] = []
    for group in groups:
        cards = [dict(card or {}) for card in list(group.get("criteria_cards") or [])]
        passed = [str(item) for item in list(group.get("passed_criteria") or []) if str(item).strip()]
        remaining = [str(item) for item in list(group.get("remaining_issues") or []) if str(item).strip()]
        decision = str(group.get("decision_summary") or "-")
        passed_text = " / ".join(passed) if passed else "없음"
        remaining_text = " / ".join(remaining) if remaining else "없음"
        card_html: list[str] = []
        for card in cards:
            card_tone = _status_tone(card.get("status"))
            card_html.append(
                f'<article class="pv-criteria-card pv-criteria-card-{card_tone}">'
                '<div class="pv-criteria-card-head">'
                f"<h5>{escape(str(card.get('issue_title') or card.get('display_label') or card.get('label') or '-'))}</h5>"
                f'<div class="pv-criteria-card-status">{escape(str(card.get("status_label") or card.get("status") or "-"))}</div>'
                "</div>"
                '<div class="pv-criteria-row">'
                "<span>현재 문제</span>"
                f"<p>{escape(str(card.get('current_problem') or card.get('evidence') or '-'))}</p>"
                "</div>"
                '<div class="pv-criteria-row">'
                "<span>완료 기준</span>"
                f"<p>{escape(str(card.get('completion_criteria') or card.get('resolution_action') or '-'))}</p>"
                "</div>"
                '<div class="pv-criteria-row">'
                "<span>보강 위치</span>"
                f"<p>{escape(str(card.get('fix_location') or card.get('resolution_surface') or '-'))}</p>"
                "</div>"
                '<div class="pv-criteria-row">'
                "<span>영향</span>"
                f"<p>{escape(str(card.get('impact_summary') or '-'))}</p>"
                "</div>"
                "<footer>"
                f"<span>기술 기준: {escape(str(card.get('technical_label') or card.get('module_type') or '-'))}</span>"
                f"<span>{escape(str(card.get('resolution_surface') or '-'))}</span>"
                "</footer>"
                "</article>"
            )
        group_html.append(
            '<section class="pv-criteria-group">'
            '<header class="pv-criteria-group-head">'
            "<div>"
            f"<strong>{escape(str(group.get('display_label') or group.get('label') or '-'))}</strong>"
            f"<span>{escape(str(group.get('purpose') or '-'))}</span>"
            "</div>"
            f"<b>{escape(str(group.get('module_count') or len(cards)))}개</b>"
            "</header>"
            '<div class="pv-criteria-status-grid">'
            '<div class="pv-criteria-status-cell">'
            "<span>상태</span>"
            f"<strong>{escape(str(group.get('status') or '-'))}</strong>"
            "</div>"
            '<div class="pv-criteria-status-cell">'
            "<span>통과한 기준</span>"
            f"<p>{escape(passed_text)}</p>"
            "</div>"
            '<div class="pv-criteria-status-cell">'
            "<span>남은 문제</span>"
            f"<p>{escape(remaining_text)}</p>"
            "</div>"
            '<div class="pv-criteria-status-cell pv-criteria-status-cell-wide">'
            "<span>판정</span>"
            f"<p>{escape(decision)}</p>"
            "</div>"
            "</div>"
            '<details class="pv-criteria-technical-detail">'
            "<summary>기술 기준 상세</summary>"
            f'<div class="pv-criteria-cards">{"".join(card_html)}</div>'
            "</details>"
            "</section>"
        )

    handoff_html = ""
    if handoff_groups:
        handoff_cards: list[str] = []
        for group in handoff_groups:
            modules = [dict(module or {}) for module in list(group.get("modules") or [])]
            status_text = " / ".join(
                str(module.get("status_label") or module.get("status") or "-")
                for module in modules
                if module
            ) or "-"
            issue_text = " / ".join(
                str(module.get("current_problem") or module.get("gate_reason") or module.get("resolution_action") or "-")
                for module in modules
                if module
            ) or "Final Review 저장 전에 막힐 별도 gap이 없습니다."
            action_text = " / ".join(
                str(module.get("completion_criteria") or module.get("resolution_action") or "-")
                for module in modules
                if module
            ) or "-"
            handoff_cards.append(
                '<article class="pv-criteria-status-cell pv-criteria-status-cell-wide">'
                "<span>Final Review 이동 요약</span>"
                f"<strong>{escape(status_text)}</strong>"
                f"<p>{escape(issue_text)}</p>"
                f"<p>{escape(action_text)}</p>"
                "</article>"
            )
        handoff_html = (
            '<section class="pv-criteria-group pv-criteria-group-handoff">'
            '<header class="pv-criteria-group-head">'
            "<div>"
            "<strong>Final Review 이동 요약</strong>"
            "<span>검증 category가 아니라 Final Review 저장 전에 막힐 gap을 따로 요약합니다.</span>"
            "</div>"
            "</header>"
            f'<div class="pv-criteria-status-grid">{"".join(handoff_cards)}</div>'
            "</section>"
        )

    st.markdown(
        '<div class="pv-shell">'
        f'<section class="pv-criteria-board pv-criteria-board-{tone}">'
        '<div class="pv-criteria-kicker">검증 기준 상세</div>'
        f'<div class="pv-criteria-title">카테고리별 검증 결과</div>'
        f'<div class="pv-criteria-detail">{escape(headline)} 검증한 category별 통과 상태와 보강 상태를 요약합니다. Final Review 이동 가능성은 아래 이동 요약으로 분리해서 확인합니다.</div>'
        f'<div class="pv-criteria-metrics">{metric_html}</div>'
        f'<div class="pv-criteria-groups">{"".join(group_html)}{handoff_html}</div>'
        "</section></div>",
        unsafe_allow_html=True,
    )


def _render_validation_efficacy_audit(validation_result: dict[str, Any]) -> None:
    audit = dict(validation_result.get("validation_efficacy_audit") or {})
    rows = list(validation_result.get("validation_efficacy_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    boundary = dict(audit.get("execution_boundary") or {})
    st.markdown("##### Validation Efficacy Audit")
    _render_board_context_badges(validation_result, "validation_efficacy_audit")
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
    _render_display_dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    if audit.get("conclusion"):
        st.caption(str(audit.get("conclusion")))


def _render_backtest_realism_audit(validation_result: dict[str, Any]) -> None:
    audit = dict(validation_result.get("backtest_realism_audit") or {})
    rows = list(validation_result.get("backtest_realism_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    boundary = dict(audit.get("execution_boundary") or {})
    st.markdown("##### Backtest Realism Audit")
    _render_board_context_badges(validation_result, "backtest_realism_audit")
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
    _render_display_dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    if audit.get("conclusion"):
        st.caption(str(audit.get("conclusion")))


def _render_construction_risk_audit(validation_result: dict[str, Any]) -> None:
    audit = dict(validation_result.get("construction_risk_audit") or {})
    rows = list(validation_result.get("construction_risk_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    boundary = dict(audit.get("execution_boundary") or {})
    st.markdown("##### Construction Risk Audit")
    _render_board_context_badges(validation_result, "construction_risk_audit")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "Source", "value": audit.get("source_strength") or "-", "tone": "neutral"},
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {
                "label": "Writes",
                "value": "Disabled" if not boundary.get("db_write") and not boundary.get("registry_write") else "Review",
                "tone": "neutral",
            },
        ]
    )
    _render_display_dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    if audit.get("conclusion"):
        st.caption(str(audit.get("conclusion")))


def _render_risk_contribution_audit(validation_result: dict[str, Any]) -> None:
    if _render_not_applicable_board(validation_result, "risk_contribution_audit", "Risk Contribution Audit"):
        return
    audit = dict(validation_result.get("risk_contribution_audit") or {})
    rows = list(validation_result.get("risk_contribution_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    boundary = dict(audit.get("execution_boundary") or {})
    st.markdown("##### Risk Contribution Audit")
    _render_board_context_badges(validation_result, "risk_contribution_audit")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "Source", "value": audit.get("source_strength") or "-", "tone": "neutral"},
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {
                "label": "Writes",
                "value": "Disabled"
                if not boundary.get("db_write")
                and not boundary.get("registry_write")
                and not boundary.get("raw_matrix_persistence")
                else "Review",
                "tone": "neutral",
            },
        ]
    )
    _render_display_dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    component_rows = list(audit.get("component_rows") or [])
    if component_rows:
        with st.expander("Risk contribution component rows", expanded=False):
            _render_display_dataframe(pd.DataFrame(component_rows), width="stretch", hide_index=True)
    if audit.get("conclusion"):
        st.caption(str(audit.get("conclusion")))


def _render_component_role_weight_audit(validation_result: dict[str, Any]) -> None:
    if _render_not_applicable_board(validation_result, "component_role_weight_audit", "Component Role / Weight Audit"):
        return
    audit = dict(validation_result.get("component_role_weight_audit") or {})
    rows = list(validation_result.get("component_role_weight_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    boundary = dict(audit.get("execution_boundary") or {})
    st.markdown("##### Component Role / Weight Audit")
    _render_board_context_badges(validation_result, "component_role_weight_audit")
    render_badge_strip(
        [
            {
                "label": "Route",
                "value": audit.get("route_label") or audit.get("route") or "-",
                "tone": _status_tone(audit.get("overall_status")),
            },
            {"label": "Source", "value": audit.get("source_strength") or "-", "tone": "neutral"},
            {"label": "PASS", "value": metrics.get("pass", 0), "tone": "positive"},
            {"label": "REVIEW", "value": metrics.get("review", 0), "tone": "warning"},
            {"label": "NEEDS_INPUT", "value": metrics.get("needs_input", 0), "tone": "warning"},
            {
                "label": "Writes",
                "value": "Disabled"
                if not boundary.get("db_write")
                and not boundary.get("registry_write")
                and not boundary.get("memo_persistence")
                and not boundary.get("role_preset_persistence")
                else "Review",
                "tone": "neutral",
            },
        ]
    )
    _render_display_dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    component_rows = list(audit.get("component_rows") or [])
    if component_rows:
        with st.expander("Component role / weight rows", expanded=False):
            _render_display_dataframe(pd.DataFrame(component_rows), width="stretch", hide_index=True)
    if audit.get("conclusion"):
        st.caption(str(audit.get("conclusion")))


def _render_data_coverage_audit(validation_result: dict[str, Any]) -> None:
    audit = dict(validation_result.get("data_coverage_audit") or {})
    rows = list(validation_result.get("data_coverage_display_rows") or audit.get("rows") or [])
    if not rows:
        return
    metrics = dict(audit.get("metrics") or {})
    boundary = dict(audit.get("execution_boundary") or {})
    st.markdown("##### Data Coverage Audit")
    _render_board_context_badges(validation_result, "data_coverage_audit")
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
            {"label": "Symbols", "value": metrics.get("symbol_count", 0), "tone": "neutral"},
            {
                "label": "Writes",
                "value": "Disabled" if not boundary.get("db_write") and not boundary.get("registry_write") else "Review",
                "tone": "neutral",
            },
        ]
    )
    _render_display_dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    if audit.get("conclusion"):
        st.caption(str(audit.get("conclusion")))


def render_practical_validation_workspace() -> None:
    render_pv_styles()
    st.markdown("### Practical Validation")
    st.caption(
        "Backtest Analysis에서 선택한 후보를 Final Review로 넘기기 전 검증 근거로 구조화합니다. "
        "최종 사용자 메모와 최종 판단은 Final Review에서만 남깁니다."
    )

    sources = load_portfolio_selection_sources(limit=100)
    validation_rows = load_practical_validation_results(limit=100)
    session_source = st.session_state.get("backtest_practical_validation_source")
    notice = st.session_state.pop("backtest_practical_validation_notice", None)
    if st.session_state.pop("practical_validation_reset_replay_on_entry", False):
        _clear_practical_validation_replay_state()
        st.session_state.pop("practical_validation_active_source_id", None)
    if notice:
        st.success(str(notice))

    render_pv_command_center(
        eyebrow="Practical Validation Workbench",
        title="Final Review 이동 전 검증 상태",
        detail=(
            "이 후보가 Final Review로 넘어갈 수 있는지, 막힌 항목과 필요한 보강을 먼저 확인합니다. "
            "최종 선택 판단과 사용자 메모는 Final Review에서만 남깁니다."
        ),
        route_label="Workflow Boundary",
        route_value="Final Review Only",
        route_detail=(
            f"Sources registry: {PORTFOLIO_SELECTION_SOURCE_FILE.name}. "
            f"Validation registry: {PRACTICAL_VALIDATION_RESULT_FILE.name}. "
            "Live approval and final memo are disabled here."
        ),
        route_tone="neutral",
        kpis=[
            {"label": "Selection Sources", "value": len(sources), "detail": "current input"},
            {"label": "Validation Results", "value": len(validation_rows), "detail": "Saved records"},
            {"label": "Final Memo", "value": "Final Review", "detail": "Not stored here"},
            {"label": "Live Approval", "value": "Disabled", "detail": "Read-only evidence"},
        ],
    )

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
        st.info("아직 Practical Validation으로 보낸 current selection source가 없습니다.")
        st.caption("Backtest Analysis에서 Single / Portfolio Mix / Saved Mix 결과를 선택하면 여기에 표시됩니다.")
        return

    labels = [_source_label(row) for row in selectable_sources]
    selected_label = st.selectbox("검증할 후보 source", options=labels, key="practical_validation_source_selected")
    source = selectable_sources[labels.index(selected_label)]
    selected_source_id = str(source.get("selection_source_id") or "source")
    if st.session_state.get("practical_validation_active_source_id") != selected_source_id:
        _clear_practical_validation_replay_state()
        st.session_state.practical_validation_active_source_id = selected_source_id

    render_pv_step_rail(
        [
            {"marker": "1", "title": "후보 Source 확인", "detail": "Source snapshot", "tone": "neutral"},
            {"marker": "2", "title": "검증 기준 / 재검증 실행", "detail": "Profile + runtime replay", "tone": "warning"},
            {"marker": "3", "title": "검증 결론", "detail": "Conclusion summary", "tone": "neutral"},
            {"marker": "4", "title": "근거 Workbench", "detail": "Evidence + provider actions", "tone": "neutral"},
            {"marker": "5", "title": "저장 / Final Review 이동", "detail": "Handoff", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        render_pv_section_header(
            eyebrow="Flow 1",
            title="후보 Source 확인",
            detail="Backtest Analysis에서 넘어온 current selection source와 저장된 백테스트 근거를 확인합니다.",
            tone="neutral",
        )
        _render_backtest_entry_gate_review_queue(source)
        _render_source_summary(source)

    with st.container(border=True):
        render_pv_section_header(
            eyebrow="Flow 2",
            title="검증 기준 설정 / 실전 재검증 실행",
            detail="Final Review 이동 전 적용할 판정 기준을 고르고 Latest Runtime Replay를 해소합니다.",
            tone="warning",
        )
        st.markdown("##### 검증 기준")
        validation_profile = _render_validation_profile_form()
        st.divider()
        st.markdown("##### 실전 재검증 실행")
        replay_result = _render_actual_replay_panel(source)

    validation_result = build_practical_validation_result(
        source,
        validation_profile=validation_profile,
        replay_result=replay_result,
    )

    with st.container(border=True):
        render_pv_section_header(
            eyebrow="Flow 3",
            title="검증 결론",
            detail="카테고리별 통과 / 실패만 요약합니다. 자세한 원인과 보강 기준은 Flow 4에서 확인합니다.",
            tone=_status_tone(dict(validation_result.get("final_review_gate") or {}).get("route")),
        )
        render_practical_validation_workspace_overview(validation_result)

    with st.container(border=True):
        render_pv_section_header(
            eyebrow="Flow 4",
            title="근거 Workbench",
            detail="검증 근거 보드와 사용자가 바로 실행할 provider 보강 액션을 함께 확인합니다.",
            tone="neutral",
        )
        _render_validation_criteria_detail_board(validation_result)
        _render_validation_evidence_boards(validation_result)
        with st.expander("검증 모듈 / 기술 상세", expanded=False):
            _render_validation_gate_section(validation_result)
        st.markdown("##### Provider / Data 보강 액션")
        _render_validation_action_boards(validation_result)

    with st.container(border=True):
        render_pv_section_header(
            eyebrow="Flow 5",
            title="저장 / Final Review 이동",
            detail="구조화된 검증 자료를 저장하고, 필수 blocker가 없을 때만 Final Review로 보냅니다.",
            tone="neutral",
        )
        gate = dict(validation_result.get("final_review_gate") or {})
        can_save_and_move = bool(gate.get("can_save_and_move"))
        render_pv_alert_panel(
            title="Save & Move Control",
            detail=(
                "검증 결과 저장은 감사용 기록을 남기는 기능입니다. Final Review 이동과 후보 노출은 필수 검증 모듈의 "
                "BLOCKED / NEEDS_INPUT / NOT_RUN 상태가 해소됐을 때만 가능합니다. "
                "Final Review의 정식 저장은 Final Review 준비 상태와 Selected Dashboard 모니터링 후보 선정 기준을 통과할 때만 허용합니다."
            ),
            tone="positive" if can_save_and_move else "danger",
        )
        render_badge_strip(
            [
                {
                    "label": "Gate",
                    "value": validation_status_label(gate.get("route") or validation_result.get("validation_route")),
                    "tone": _status_tone(gate.get("route") or validation_result.get("validation_route")),
                },
                {
                    "label": "Save & Move",
                    "value": "Enabled" if can_save_and_move else "Blocked",
                    "tone": "positive" if can_save_and_move else "danger",
                },
                {
                    "label": "Blocking Modules",
                    "value": len(gate.get("blocking_modules") or []),
                    "tone": "danger" if gate.get("blocking_modules") else "positive",
                },
            ]
        )
        if gate.get("next_action"):
            st.caption(str(gate.get("next_action")))
        if not can_save_and_move:
            st.caption("준비 상태 통과 전 저장 기록은 audit trail로만 남고 Final Review 후보 목록에는 노출되지 않습니다.")
        blocking_modules = list(gate.get("blocking_modules") or [])
        if blocking_modules:
            with st.expander("Save blocker 상세", expanded=False):
                _render_display_dataframe(pd.DataFrame(gate_module_display_rows(blocking_modules)), width="stretch", hide_index=True)
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button("검증 결과 저장(기록용)", key="practical_validation_save_result", width="stretch"):
                save_practical_validation_result(validation_result)
                st.success(f"검증 결과 `{validation_result['validation_id']}`를 저장했습니다.")
                if not can_save_and_move:
                    st.warning("이 기록은 Final Review 준비 상태를 통과하지 않아 Final Review 후보 목록에는 표시되지 않습니다.")
        with action_cols[1]:
            if st.button(
                "저장하고 Final Review로 이동",
                key="practical_validation_send_final_review",
                width="stretch",
                disabled=not can_save_and_move,
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
            if not can_save_and_move:
                st.caption("필수 검증 모듈을 보강한 뒤 저장하고 Final Review로 이동할 수 있습니다.")

    with st.expander("Selection Source JSON", expanded=False):
        st.json(source)
    with st.expander("Practical Validation Result JSON", expanded=False):
        st.json(validation_result)
