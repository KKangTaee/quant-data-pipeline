from __future__ import annotations

import re
from typing import Any

import pandas as pd

from app.services.backtest_evidence_read_model import build_final_decision_evidence_rows
from app.runtime.final_selected_portfolios import FINAL_SELECTED_PORTFOLIO_STATUS_LABELS


def _display_value(value: Any) -> str:
    if value is None:
        return "-"
    text = str(value).strip()
    return text or "-"


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def final_selected_portfolio_label(row: dict[str, Any]) -> str:
    """Build a stable selectbox label for one selected portfolio dashboard row."""
    title = _display_value(row.get("source_title"))
    if len(title) > 72:
        title = f"{title[:69]}..."
    return f"{_display_value(row.get('operation_status_label'))} | {title} | {_display_value(row.get('updated_at'))}"


def build_selected_portfolio_dashboard_table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        display_rows.append(
            {
                "Updated At": row.get("updated_at"),
                "Status": row.get("operation_status_label"),
                "Portfolio": row.get("source_title"),
                "Source Type": row.get("source_type"),
                "Components": row.get("component_count"),
                "Target": f"{_optional_float(row.get('target_weight_total')) or 0.0:.1f}%",
                "Benchmark": row.get("benchmark_label"),
                "Original Period": f"{_display_value(row.get('baseline_start'))} -> {_display_value(row.get('baseline_end'))}",
                "Baseline CAGR": (
                    f"{(_optional_float(row.get('baseline_cagr')) or 0.0):.2%}"
                    if _optional_float(row.get("baseline_cagr")) is not None
                    else "-"
                ),
                "Baseline MDD": (
                    f"{(_optional_float(row.get('baseline_mdd')) or 0.0):.2%}"
                    if _optional_float(row.get("baseline_mdd")) is not None
                    else "-"
                ),
            }
        )
    return pd.DataFrame(display_rows)


def selected_dashboard_portfolio_label(row: dict[str, Any]) -> str:
    name = _display_value(row.get("name"))
    if len(name) > 72:
        name = f"{name[:69]}..."
    count = int(row.get("strategy_count") or len(list(row.get("selected_decision_ids") or [])) or 0)
    return f"{name} | {count} strategies | {_display_value(row.get('updated_at'))}"


def build_selected_dashboard_portfolio_table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        display_rows.append(
            {
                "Name": row.get("name"),
                "Strategies": row.get("strategy_count", len(list(row.get("selected_decision_ids") or []))),
                "Missing": row.get("missing_strategy_count", 0),
                "Updated At": row.get("updated_at"),
                "Created At": row.get("created_at"),
                "Description": row.get("description"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_dashboard_portfolio_strategy_table(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        display_rows.append(
            {
                "Decision ID": row.get("decision_id"),
                "Strategy": row.get("source_title"),
                "Status": row.get("operation_status_label"),
                "Components": row.get("component_count"),
                "Target": f"{_optional_float(row.get('target_weight_total')) or 0.0:.1f}%",
                "Benchmark": row.get("benchmark_label"),
                "Original Period": f"{_display_value(row.get('baseline_start'))} -> {_display_value(row.get('baseline_end'))}",
                "Baseline CAGR": (
                    f"{(_optional_float(row.get('baseline_cagr')) or 0.0):.2%}"
                    if _optional_float(row.get("baseline_cagr")) is not None
                    else "-"
                ),
                "Baseline MDD": (
                    f"{(_optional_float(row.get('baseline_mdd')) or 0.0):.2%}"
                    if _optional_float(row.get("baseline_mdd")) is not None
                    else "-"
                ),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_dashboard_strategy_pool_table(
    rows: list[dict[str, Any]],
    *,
    selected_decision_ids: list[str] | None = None,
) -> pd.DataFrame:
    selected_ids = {str(item) for item in list(selected_decision_ids or [])}
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        decision_id = str(row.get("decision_id") or "")
        display_rows.append(
            {
                "Decision ID": decision_id,
                "Strategy": row.get("source_title"),
                "Add State": "Already added" if decision_id in selected_ids else "Available",
                "Status": row.get("operation_status_label"),
                "Benchmark": row.get("benchmark_label"),
                "Baseline CAGR": (
                    f"{(_optional_float(row.get('baseline_cagr')) or 0.0):.2%}"
                    if _optional_float(row.get("baseline_cagr")) is not None
                    else "-"
                ),
                "Baseline MDD": (
                    f"{(_optional_float(row.get('baseline_mdd')) or 0.0):.2%}"
                    if _optional_float(row.get("baseline_mdd")) is not None
                    else "-"
                ),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_dashboard_portfolio_strategy_comparison_table(
    rows: list[dict[str, Any]],
    *,
    recheck_results_by_decision_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        decision_id = str(row.get("decision_id") or "")
        result = dict(recheck_results_by_decision_id.get(decision_id) or {})
        portfolio_summary = dict(result.get("portfolio_summary") or {})
        benchmark_summary = dict(result.get("benchmark_summary") or {})
        change_summary = dict(result.get("change_summary") or {})
        period = dict(result.get("period") or {})
        display_rows.append(
            {
                "Strategy": row.get("source_title"),
                "Scenario Status": result.get("status") or "not run",
                "Verdict": result.get("verdict_route") or "-",
                "Start": period.get("start") or "-",
                "End": period.get("end") or "-",
                "Current Value": portfolio_summary.get("end_balance"),
                "Cumulative Return": portfolio_summary.get("total_return"),
                "CAGR": portfolio_summary.get("cagr"),
                "MDD": portfolio_summary.get("mdd"),
                "Benchmark CAGR": benchmark_summary.get("cagr"),
                "Benchmark Spread": change_summary.get("net_cagr_spread"),
            }
        )
    frame = pd.DataFrame(display_rows)
    for column in ["Cumulative Return", "CAGR", "MDD", "Benchmark CAGR", "Benchmark Spread"]:
        if column in frame.columns:
            frame[column] = frame[column].map(lambda value: f"{float(value):.2%}" if value is not None and not pd.isna(value) else "-")
    if "Current Value" in frame.columns:
        frame["Current Value"] = frame["Current Value"].map(lambda value: f"{float(value):,.0f}" if value is not None and not pd.isna(value) else "-")
    return frame


def build_selected_portfolio_open_issue_followup_table(followup: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(followup.get("rows") or []):
        display_rows.append(
            {
                "Area": row.get("Area"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
                "Source": row.get("Source"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_deployment_readiness_table(preflight: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(preflight.get("rows") or []):
        display_rows.append(
            {
                "Area": row.get("Area"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
                "Source": row.get("Source"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_dashboard_handoff_table(handoff: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(handoff.get("rows") or []):
        display_rows.append(
            {
                "Updated At": row.get("Updated At"),
                "Decision ID": row.get("Decision ID"),
                "Portfolio": row.get("Portfolio"),
                "Dashboard Status": row.get("Dashboard Status"),
                "Status Reason": row.get("Status Reason"),
                "Components": row.get("Components"),
                "Target Weight": row.get("Target Weight"),
                "Benchmark": row.get("Benchmark"),
                "Evidence Route": row.get("Evidence Route"),
                "Review Cadence": row.get("Review Cadence"),
                "Review Triggers": row.get("Review Triggers"),
                "Handoff Destination": row.get("Handoff Destination"),
                "Handoff Action": row.get("Handoff Action"),
                "Live Approval": row.get("Live Approval"),
                "Order": row.get("Order"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_dashboard_handoff_checklist_table(handoff: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(handoff.get("checklist") or []):
        display_rows.append(
            {
                "Check": row.get("Check"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_component_table(row: dict[str, Any]) -> pd.DataFrame:
    raw_decision = dict(row.get("raw_decision") or {})
    display_rows: list[dict[str, Any]] = []
    for component in list(raw_decision.get("selected_components") or []):
        component_row = dict(component or {})
        weight = _optional_float(component_row.get("target_weight")) or 0.0
        if weight <= 0.0:
            continue
        display_rows.append(
            {
                "Registry ID": component_row.get("registry_id"),
                "Title": component_row.get("title"),
                "Role": component_row.get("proposal_role"),
                "Target Weight": weight,
                "Family": component_row.get("strategy_family"),
                "Benchmark": component_row.get("benchmark"),
                "Universe": component_row.get("universe"),
                "Data Trust": component_row.get("data_trust_status"),
                "Promotion": component_row.get("promotion"),
                "Deployment": component_row.get("deployment"),
                "Baseline CAGR": component_row.get("baseline_cagr"),
                "Baseline MDD": component_row.get("baseline_mdd"),
            }
        )
    return pd.DataFrame(display_rows)


def selected_portfolio_active_components(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw_decision = dict(row.get("raw_decision") or {})
    active: list[dict[str, Any]] = []
    for index, component in enumerate(list(raw_decision.get("selected_components") or [])):
        component_row = dict(component or {})
        weight = _optional_float(component_row.get("target_weight")) or 0.0
        if weight <= 0.0:
            continue
        component_id = _display_value(component_row.get("registry_id"))
        if component_id == "-":
            component_id = _display_value(component_row.get("title"))
        if component_id == "-":
            component_id = f"component_{index + 1}"
        component_row["component_id"] = component_id
        component_row["target_weight"] = weight
        active.append(component_row)
    return active


def _clean_symbol_candidate(value: Any) -> str:
    text = str(value or "").strip().upper()
    if not text or text in {"-", "N/A", "NONE"}:
        return ""
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,14}", text):
        return ""
    return text


def selected_portfolio_component_default_symbol(component: dict[str, Any]) -> str:
    """Infer a safe single-symbol default for optional price assistance."""
    for field in ("holding_symbol", "asset_symbol", "symbol", "ticker"):
        candidate = _clean_symbol_candidate(component.get(field))
        if candidate:
            return candidate

    universe = str(component.get("universe") or "").strip()
    if universe:
        tokens = [token.strip() for token in re.split(r"[,/\s]+", universe) if token.strip()]
        if len(tokens) == 1:
            candidate = _clean_symbol_candidate(tokens[0])
            if candidate:
                return candidate
    return ""


def build_selected_portfolio_current_weight_input_table(weight_inputs: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(weight_inputs.get("rows") or []):
        display_rows.append(
            {
                "Component": row.get("title"),
                "Input Mode": row.get("input_mode_label"),
                "Symbol": row.get("symbol") or "-",
                "Shares": row.get("shares"),
                "Price": row.get("price"),
                "Price Date": row.get("price_date") or "-",
                "Price Source": row.get("price_source") or "-",
                "Current Value": row.get("current_value"),
                "Current Weight": row.get("current_weight"),
                "Complete": bool(row.get("input_complete")),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_drift_table(drift_check: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(drift_check.get("rows") or []):
        drift = _optional_float(row.get("drift")) or 0.0
        direction = "Overweight" if drift > 0 else "Underweight" if drift < 0 else "Aligned"
        display_rows.append(
            {
                "Component": row.get("title"),
                "Target Weight": row.get("target_weight"),
                "Current Weight": row.get("current_weight"),
                "Drift": row.get("drift"),
                "Abs Drift": row.get("abs_drift"),
                "Direction": direction,
                "Rebalance": bool(row.get("threshold_breached")),
                "Watch": bool(row.get("watch_breached")),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_drift_alert_table(alert_preview: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(alert_preview.get("rows") or []):
        display_rows.append(
            {
                "Area": row.get("area"),
                "Trigger": row.get("trigger"),
                "Status": row.get("status"),
                "Current": row.get("current"),
                "Next Action": row.get("next_action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_allocation_drift_boundary_table(boundary: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(boundary.get("rows") or []):
        display_rows.append(
            {
                "Check": row.get("Check"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
                "Source": row.get("Source"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_evidence_table(row: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame(build_final_decision_evidence_rows(row))


def build_selected_portfolio_monitoring_timeline_table(timeline: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(timeline.get("rows") or []):
        display_rows.append(
            {
                "Order": row.get("order"),
                "Event": row.get("event"),
                "When": row.get("timestamp"),
                "Status": row.get("status_label") or row.get("status"),
                "Signal": row.get("signal"),
                "Evidence": row.get("evidence"),
                "Next Action": row.get("next_action"),
                "Source": row.get("source"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_continuity_table(continuity: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(continuity.get("checks") or []):
        display_rows.append(
            {
                "Check": row.get("Check"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_source_contract_table(contract: dict[str, Any]) -> pd.DataFrame:
    boundary = dict(contract.get("execution_boundary") or {})
    rows = [
        {"Field": "Schema", "Value": contract.get("schema_version")},
        {"Field": "Surface", "Value": contract.get("surface")},
        {"Field": "Decision ID", "Value": contract.get("decision_id")},
        {"Field": "Decision Route", "Value": contract.get("decision_route")},
        {"Field": "Durable Source", "Value": contract.get("durable_source")},
        {"Field": "Source Identity", "Value": contract.get("source_identity")},
        {"Field": "Selection Source ID", "Value": contract.get("selection_source_id")},
        {"Field": "Validation ID", "Value": contract.get("validation_id")},
        {
            "Field": "Session Evidence",
            "Value": ", ".join(list(contract.get("session_evidence_sources") or [])) or "-",
        },
        {"Field": "Registry Write", "Value": boundary.get("registry_write")},
        {"Field": "Monitoring Log Auto Write", "Value": boundary.get("monitoring_log_auto_write")},
        {"Field": "Report Auto Write", "Value": boundary.get("report_auto_write")},
        {"Field": "Order Instruction", "Value": boundary.get("order_instruction")},
        {"Field": "Auto Rebalance", "Value": boundary.get("auto_rebalance")},
    ]
    return pd.DataFrame(rows)


def build_selected_portfolio_recheck_comparison_table(comparison: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(comparison.get("rows") or []):
        display_rows.append(
            {
                "Check": row.get("Check"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Threshold": row.get("Threshold"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_review_signal_policy_table(policy: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(policy.get("rows") or []):
        display_rows.append(
            {
                "Trigger": row.get("Trigger"),
                "Status": row.get("Status Label") or row.get("Status"),
                "Current Signal": row.get("Current Signal"),
                "Policy Owner": row.get("Policy Owner"),
                "Why It Matters": row.get("Why It Matters"),
                "Suggested Action": row.get("Suggested Action"),
                "Source": row.get("Source"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_recheck_readiness_table(readiness: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(readiness.get("rows") or []):
        display_rows.append(
            {
                "Check": row.get("Check"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_recheck_preflight_table(preflight: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(preflight.get("rows") or []):
        display_rows.append(
            {
                "Area": row.get("Area"),
                "Status": row.get("Status"),
                "Ready": bool(row.get("Ready")),
                "Current": row.get("Current"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_symbol_freshness_table(freshness: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(freshness.get("rows") or []):
        display_rows.append(
            {
                "Symbol": row.get("Symbol"),
                "Role": row.get("Role"),
                "Components": row.get("Components"),
                "Status": row.get("Status"),
                "Latest Date": row.get("Latest Date"),
                "Market Date": row.get("Market Date"),
                "Days Lag": row.get("Days Lag"),
                "Row Count": row.get("Row Count"),
                "Evidence": row.get("Evidence"),
                "Next Action": row.get("Next Action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_provider_evidence_table(evidence: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in list(evidence.get("rows") or []):
        display_rows.append(
            {
                "Area": row.get("Area"),
                "Status": row.get("Status"),
                "Coverage": row.get("Coverage"),
                "Coverage Weight": row.get("Coverage Weight"),
                "Freshness": row.get("Freshness"),
                "As Of Range": row.get("As Of Range"),
                "Source Mix": row.get("Source Mix"),
                "Policy Reason": row.get("Policy Reason"),
                "Summary": row.get("Summary"),
                "Next Action": row.get("Next Action"),
            }
        )
    return pd.DataFrame(display_rows)


def build_selected_portfolio_provider_symbol_weight_table(evidence: dict[str, Any]) -> pd.DataFrame:
    symbol_weights = dict(evidence.get("symbol_weights") or {})
    return pd.DataFrame(
        [
            {
                "Symbol": symbol,
                "Provider Weight": weight,
            }
            for symbol, weight in sorted(symbol_weights.items())
        ]
    )


def filter_selected_portfolio_rows(
    rows: list[dict[str, Any]],
    *,
    statuses: list[str],
    source_types: list[str],
    benchmark: str,
) -> list[dict[str, Any]]:
    benchmark_clean = str(benchmark or "").strip()
    filtered: list[dict[str, Any]] = []
    for row in rows:
        if statuses and str(row.get("operation_status") or "") not in statuses:
            continue
        if source_types and str(row.get("source_type") or "") not in source_types:
            continue
        if benchmark_clean and benchmark_clean != "All":
            benchmarks = {str(item) for item in list(row.get("benchmarks") or [])}
            if benchmark_clean not in benchmarks:
                continue
        filtered.append(row)
    return filtered


def selected_portfolio_status_options(rows: list[dict[str, Any]]) -> list[str]:
    seen = {str(row.get("operation_status") or "blocked") for row in rows}
    ordered = [status for status in FINAL_SELECTED_PORTFOLIO_STATUS_LABELS if status in seen]
    return ordered or list(FINAL_SELECTED_PORTFOLIO_STATUS_LABELS)


def selected_portfolio_source_type_options(rows: list[dict[str, Any]]) -> list[str]:
    return sorted({str(row.get("source_type") or "-") for row in rows if str(row.get("source_type") or "-")})


def selected_portfolio_benchmark_options(rows: list[dict[str, Any]]) -> list[str]:
    benchmarks = sorted(
        {
            str(benchmark)
            for row in rows
            for benchmark in list(row.get("benchmarks") or [])
            if str(benchmark).strip()
        }
    )
    return ["All"] + benchmarks
