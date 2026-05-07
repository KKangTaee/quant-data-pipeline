from __future__ import annotations

import re
from typing import Any

import pandas as pd

from app.web.runtime.final_selected_portfolios import FINAL_SELECTED_PORTFOLIO_STATUS_LABELS


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


def _append_check_rows(
    display_rows: list[dict[str, Any]],
    *,
    area: str,
    checks: list[dict[str, Any]],
) -> None:
    for check in checks:
        check_row = dict(check or {})
        display_rows.append(
            {
                "Area": area,
                "Criteria": check_row.get("Criteria") or check_row.get("criteria") or "-",
                "Ready": check_row.get("Ready") if "Ready" in check_row else check_row.get("ready"),
                "Current": check_row.get("Current")
                or check_row.get("current")
                or check_row.get("current_value")
                or "-",
                "Meaning": check_row.get("Meaning") or check_row.get("meaning") or "-",
                "Score": check_row.get("Score") or check_row.get("score") or "-",
            }
        )


def build_selected_portfolio_evidence_table(row: dict[str, Any]) -> pd.DataFrame:
    raw_decision = dict(row.get("raw_decision") or {})
    evidence = dict(raw_decision.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    display_rows: list[dict[str, Any]] = []
    _append_check_rows(display_rows, area="Final Review Evidence", checks=list(evidence.get("checks") or []))
    _append_check_rows(display_rows, area="Validation", checks=list(risk_snapshot.get("validation_checks") or []))
    _append_check_rows(display_rows, area="Robustness", checks=list(robustness.get("checks") or []))
    _append_check_rows(display_rows, area="Paper Observation", checks=list(paper_snapshot.get("checks") or []))
    return pd.DataFrame(display_rows)


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
