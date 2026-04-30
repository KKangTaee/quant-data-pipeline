from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from app.web.runtime import PORTFOLIO_PROPOSAL_SCHEMA_VERSION

PORTFOLIO_PROPOSAL_STATUS_OPTIONS = [
    "draft",
    "review_ready",
    "paper_tracking",
    "hold",
    "rejected",
    "superseded",
    "live_readiness_candidate",
]
PORTFOLIO_PROPOSAL_TYPE_OPTIONS = [
    "balanced_core",
    "lower_drawdown_core",
    "defensive_blend",
    "satellite_pack",
]
PORTFOLIO_PROPOSAL_ROLE_OPTIONS = [
    "core_anchor",
    "return_driver",
    "diversifier",
    "defensive_sleeve",
    "satellite",
    "watch_only",
]
PORTFOLIO_PROPOSAL_WEIGHTING_OPTIONS = ["manual_weight", "equal_weight"]
PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD = -2.0
PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD = -5.0


# Parse a proposal component target weight into a safe float.
def _component_target_weight(component_input: dict[str, Any]) -> float:
    try:
        return float(component_input.get("target_weight") or 0.0)
    except (TypeError, ValueError):
        return 0.0


# Convert latest Pre-Live rows into a registry_id -> status lookup for proposal component cards.
def _portfolio_proposal_pre_live_status_by_registry_id(pre_live_rows: list[dict[str, Any]]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for row in pre_live_rows:
        registry_id = str(row.get("source_candidate_registry_id") or "").strip()
        if registry_id:
            statuses[registry_id] = str(row.get("pre_live_status") or "not_started")
    return statuses


# Build the append-only Portfolio Proposal registry row from selected candidates and operator inputs.
def _build_portfolio_proposal_row(
    *,
    proposal_id: str,
    proposal_status: str,
    proposal_type: str,
    primary_goal: str,
    secondary_goal: str,
    target_holding_style: str,
    capital_scope: str,
    weighting_method: str,
    benchmark_policy: str,
    selected_rows: list[dict[str, Any]],
    component_inputs: dict[str, dict[str, Any]],
    open_blockers: list[str],
    operator_decision: str,
    operator_reason: str,
    next_action: str,
    review_date_value: date | None,
) -> dict[str, Any]:
    now = datetime.now().isoformat(timespec="seconds")
    candidate_refs: list[dict[str, Any]] = []
    evidence_components: list[dict[str, Any]] = []
    for row in selected_rows:
        registry_id = str(row.get("registry_id") or "")
        component_input = dict(component_inputs.get(registry_id) or {})
        result = dict(row.get("result") or {})
        candidate_ref = {
            "registry_id": registry_id,
            "strategy_family": row.get("strategy_family"),
            "strategy_name": row.get("strategy_name"),
            "candidate_role": row.get("candidate_role"),
            "proposal_role": component_input.get("proposal_role"),
            "target_weight": component_input.get("target_weight"),
            "weight_reason": component_input.get("weight_reason"),
            "data_trust_status": component_input.get("data_trust_status") or "not_attached",
            "real_money_status": {
                "promotion": result.get("promotion"),
                "shortlist": result.get("shortlist"),
                "deployment": result.get("deployment"),
            },
            "pre_live_status": component_input.get("pre_live_status") or "not_started",
            "open_candidate_blockers": component_input.get("open_candidate_blockers") or [],
        }
        candidate_refs.append(candidate_ref)
        evidence_components.append(
            {
                "registry_id": registry_id,
                "title": row.get("title"),
                "cagr": result.get("cagr"),
                "mdd": result.get("mdd"),
                "promotion": result.get("promotion"),
                "shortlist": result.get("shortlist"),
                "deployment": result.get("deployment"),
                "period": row.get("period") or {},
            }
        )

    return {
        "schema_version": PORTFOLIO_PROPOSAL_SCHEMA_VERSION,
        "proposal_id": proposal_id.strip(),
        "created_at": now,
        "updated_at": now,
        "proposal_status": proposal_status,
        "proposal_type": proposal_type,
        "objective": {
            "primary_goal": primary_goal.strip(),
            "secondary_goal": secondary_goal.strip(),
            "target_holding_style": target_holding_style.strip(),
            "capital_scope": capital_scope,
        },
        "candidate_refs": candidate_refs,
        "construction": {
            "weighting_method": weighting_method,
            "benchmark_policy": benchmark_policy.strip(),
            "date_alignment": "compare_or_saved_portfolio_context_required",
        },
        "risk_constraints": {
            "max_component_weight": max(
                [float(ref.get("target_weight") or 0.0) for ref in candidate_refs],
                default=0.0,
            ),
            "requires_component_data_trust_review": True,
            "requires_real_money_review": True,
            "requires_pre_live_review": True,
        },
        "evidence_snapshot": {
            "component_count": len(candidate_refs),
            "components": evidence_components,
        },
        "open_blockers": open_blockers,
        "operator_decision": {
            "decision": operator_decision.strip(),
            "reason": operator_reason.strip(),
            "next_action": next_action.strip(),
            "review_date": review_date_value.isoformat() if review_date_value else None,
        },
        "notes": (
            "Created from Backtest > Portfolio Proposal. This is a proposal draft, "
            "not live trading approval and not an order instruction."
        ),
    }


# Summarize saved proposal rows for the compact saved-proposals table.
def _build_portfolio_proposal_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        objective = dict(row.get("objective") or {})
        construction = dict(row.get("construction") or {})
        operator_decision = dict(row.get("operator_decision") or {})
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Type": row.get("proposal_type"),
                "Primary Goal": objective.get("primary_goal"),
                "Components": len(row.get("candidate_refs") or []),
                "Weighting": construction.get("weighting_method"),
                "Next Action": operator_decision.get("next_action"),
            }
        )
    return pd.DataFrame(display_rows)


# Add all component target weights in a saved proposal row.
def _portfolio_proposal_weight_total(row: dict[str, Any]) -> float:
    total = 0.0
    for ref in list(row.get("candidate_refs") or []):
        try:
            total += float(ref.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            continue
    return round(total, 4)


# Find non-blocking review gaps that should be visible before later approval stages.
def _portfolio_proposal_review_gaps(row: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    operator_decision = dict(row.get("operator_decision") or {})
    if not operator_decision.get("review_date"):
        gaps.append("Review date is not set.")

    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "-")
        data_trust_status = str(ref.get("data_trust_status") or "not_attached")
        pre_live_status = str(ref.get("pre_live_status") or "not_started")
        if data_trust_status in {"not_attached", "unknown", "missing"}:
            gaps.append(f"{registry_id}: data trust status needs review.")
        if pre_live_status == "not_started":
            gaps.append(f"{registry_id}: pre-live status is not started.")
    return gaps


# Find hard proposal blockers that should stop an active proposal weight.
def _portfolio_proposal_monitoring_blockers(row: dict[str, Any]) -> list[str]:
    blockers = [str(value) for value in list(row.get("open_blockers") or []) if str(value).strip()]
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "-")
        real_money_status = dict(ref.get("real_money_status") or {})
        try:
            target_weight = float(ref.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            target_weight = 0.0
        pre_live_status = str(ref.get("pre_live_status") or "not_started")
        proposal_role = str(ref.get("proposal_role") or "")
        deployment_status = str(real_money_status.get("deployment") or "").lower()
        component_blockers = [str(value) for value in list(ref.get("open_candidate_blockers") or []) if str(value).strip()]
        for blocker in component_blockers:
            blockers.append(f"{registry_id}: {blocker}")
        if pre_live_status == "reject" and target_weight > 0:
            blockers.append(f"{registry_id}: rejected pre-live candidate has active weight.")
        if deployment_status == "blocked" and proposal_role == "core_anchor":
            blockers.append(f"{registry_id}: blocked candidate is marked as core anchor.")
    return blockers


# Convert saved proposal blockers and gaps into a compact monitoring state label.
def _portfolio_proposal_monitoring_state(row: dict[str, Any]) -> str:
    if _portfolio_proposal_monitoring_blockers(row):
        return "blocked"
    if _portfolio_proposal_review_gaps(row):
        return "needs_review"
    return "review_ready"


# Build the saved proposal monitoring summary table.
def _build_portfolio_proposal_monitoring_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        operator_decision = dict(row.get("operator_decision") or {})
        blockers = _portfolio_proposal_monitoring_blockers(row)
        review_gaps = _portfolio_proposal_review_gaps(row)
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Monitoring State": _portfolio_proposal_monitoring_state(row),
                "Components": len(row.get("candidate_refs") or []),
                "Weight Total": _portfolio_proposal_weight_total(row),
                "Blockers": len(blockers),
                "Review Gaps": len(review_gaps),
                "Review Date": operator_decision.get("review_date"),
                "Next Action": operator_decision.get("next_action"),
            }
        )
    return pd.DataFrame(display_rows)


# Build the saved proposal component table for inspection.
def _build_portfolio_proposal_component_rows(row: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for ref in list(row.get("candidate_refs") or []):
        real_money_status = dict(ref.get("real_money_status") or {})
        blockers = [str(value) for value in list(ref.get("open_candidate_blockers") or []) if str(value).strip()]
        display_rows.append(
            {
                "Registry ID": ref.get("registry_id"),
                "Family": ref.get("strategy_family"),
                "Strategy": ref.get("strategy_name"),
                "Candidate Role": ref.get("candidate_role"),
                "Proposal Role": ref.get("proposal_role"),
                "Target Weight": ref.get("target_weight"),
                "Data Trust": ref.get("data_trust_status"),
                "Pre-Live": ref.get("pre_live_status"),
                "Promotion": real_money_status.get("promotion"),
                "Shortlist": real_money_status.get("shortlist"),
                "Deployment": real_money_status.get("deployment"),
                "Weight Reason": ref.get("weight_reason"),
                "Candidate Blockers": "; ".join(blockers) if blockers else "-",
            }
        )
    return pd.DataFrame(display_rows)


# Create a stable, human-readable label for selecting a saved proposal row.
def _portfolio_proposal_selection_label(row: dict[str, Any]) -> str:
    return f"{row.get('updated_at') or row.get('created_at')} | {row.get('proposal_status')} | {row.get('proposal_id')}"


# Convert latest Pre-Live rows into a registry_id -> row lookup for feedback comparisons.
def _portfolio_proposal_pre_live_record_by_registry_id(pre_live_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for row in pre_live_rows:
        registry_id = str(row.get("source_candidate_registry_id") or "").strip()
        if registry_id:
            records[registry_id] = dict(row)
    return records


# Parse ISO-like review date values from saved JSONL records.
def _portfolio_proposal_parse_review_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


# Parse optional numeric values from JSONL snapshots and table cells.
def _portfolio_proposal_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return float(value)
    value_text = str(value).strip()
    if not value_text or value_text.lower() in {"none", "nan", "null"} or value_text == "-":
        return None
    value_text = value_text.replace("%", "").replace(",", "")
    try:
        return float(value_text)
    except ValueError:
        return None


# Calculate current-minus-saved metric deltas for paper tracking feedback.
def _portfolio_proposal_metric_delta(current_value: Any, saved_value: Any) -> float | None:
    current_float = _portfolio_proposal_optional_float(current_value)
    saved_float = _portfolio_proposal_optional_float(saved_value)
    if current_float is None or saved_float is None:
        return None
    return round(current_float - saved_float, 4)


# Convert a saved proposal evidence snapshot into a registry_id -> evidence lookup.
def _portfolio_proposal_evidence_by_registry_id(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    evidence = dict(row.get("evidence_snapshot") or {})
    records: dict[str, dict[str, Any]] = {}
    for component in list(evidence.get("components") or []):
        registry_id = str(dict(component).get("registry_id") or "").strip()
        if registry_id:
            records[registry_id] = dict(component)
    return records


# Classify whether current paper tracking performance is stable, missing, or worsened.
def _portfolio_proposal_paper_tracking_signal(
    *,
    current_status: str,
    saved_cagr: Any,
    current_cagr: Any,
    saved_mdd: Any,
    current_mdd: Any,
) -> str:
    if current_status != "paper_tracking":
        return "needs_paper_tracking"
    if current_cagr is None or current_mdd is None:
        return "missing_current_result"
    if saved_cagr is None or saved_mdd is None:
        return "missing_saved_snapshot"
    cagr_delta = _portfolio_proposal_metric_delta(current_cagr, saved_cagr)
    mdd_delta = _portfolio_proposal_metric_delta(current_mdd, saved_mdd)
    if cagr_delta is None or mdd_delta is None:
        return "missing_current_result"
    if (
        cagr_delta <= PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD
        or mdd_delta <= PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD
    ):
        return "worsened"
    return "stable_or_better"


# Build row-level comparison between saved proposal Pre-Live snapshot and current Pre-Live state.
def _portfolio_proposal_pre_live_feedback_rows(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        saved_status = str(ref.get("pre_live_status") or "not_started")
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        tracking_plan = dict(pre_live_record.get("tracking_plan") or {})
        review_date = pre_live_record.get("review_date")
        review_date_value = _portfolio_proposal_parse_review_date(review_date)
        display_rows.append(
            {
                "Registry ID": registry_id or "-",
                "Proposal Role": ref.get("proposal_role"),
                "Target Weight": ref.get("target_weight"),
                "Saved Pre-Live": saved_status,
                "Current Pre-Live": current_status,
                "Status Drift": "changed" if saved_status != current_status else "same",
                "Current Review Date": review_date,
                "Review Overdue": bool(review_date_value and review_date_value < date.today()),
                "Tracking Cadence": tracking_plan.get("cadence"),
                "Current Next Action": pre_live_record.get("next_action"),
            }
        )
    return pd.DataFrame(display_rows)


# Find gaps between a saved proposal and the latest Pre-Live registry rows.
def _portfolio_proposal_pre_live_feedback_gaps(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> list[str]:
    gaps: list[str] = []
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        if not registry_id:
            continue
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        saved_status = str(ref.get("pre_live_status") or "not_started")
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        try:
            target_weight = float(ref.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            target_weight = 0.0
        if not pre_live_record:
            gaps.append(f"{registry_id}: no active Pre-Live record is linked.")
        if saved_status != current_status:
            gaps.append(f"{registry_id}: proposal snapshot `{saved_status}` differs from current Pre-Live `{current_status}`.")
        if current_status in {"hold", "reject", "re_review"} and target_weight > 0:
            gaps.append(f"{registry_id}: current Pre-Live status `{current_status}` needs review for active weight.")
        review_date_value = _portfolio_proposal_parse_review_date(pre_live_record.get("review_date"))
        if review_date_value and review_date_value < date.today():
            gaps.append(f"{registry_id}: Pre-Live review date `{review_date_value.isoformat()}` is overdue.")
    return gaps


# Build a saved proposal summary table for current Pre-Live feedback.
def _build_portfolio_proposal_pre_live_feedback_summary_rows(
    rows: list[dict[str, Any]],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        feedback_df = _portfolio_proposal_pre_live_feedback_rows(row, pre_live_by_registry_id)
        gaps = _portfolio_proposal_pre_live_feedback_gaps(row, pre_live_by_registry_id)
        if feedback_df.empty:
            linked_count = 0
            paper_tracking_count = 0
            drift_count = 0
            overdue_count = 0
        else:
            linked_count = int((feedback_df["Current Pre-Live"] != "not_started").sum())
            paper_tracking_count = int((feedback_df["Current Pre-Live"] == "paper_tracking").sum())
            drift_count = int((feedback_df["Status Drift"] == "changed").sum())
            overdue_count = int(feedback_df["Review Overdue"].sum())
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Components": len(row.get("candidate_refs") or []),
                "Linked Pre-Live": linked_count,
                "Paper Tracking": paper_tracking_count,
                "Status Drift": drift_count,
                "Overdue Reviews": overdue_count,
                "Feedback Gaps": len(gaps),
            }
        )
    return pd.DataFrame(display_rows)


# Build component-level paper tracking metric feedback rows.
def _portfolio_proposal_paper_tracking_feedback_rows(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    evidence_by_registry_id = _portfolio_proposal_evidence_by_registry_id(row)
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        evidence = evidence_by_registry_id.get(registry_id) or {}
        result_snapshot = dict(pre_live_record.get("result_snapshot") or {})
        tracking_plan = dict(pre_live_record.get("tracking_plan") or {})
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        saved_cagr = _portfolio_proposal_optional_float(evidence.get("cagr"))
        saved_mdd = _portfolio_proposal_optional_float(evidence.get("mdd"))
        current_cagr = _portfolio_proposal_optional_float(result_snapshot.get("cagr"))
        current_mdd = _portfolio_proposal_optional_float(result_snapshot.get("mdd"))
        display_rows.append(
            {
                "Registry ID": registry_id or "-",
                "Proposal Role": ref.get("proposal_role"),
                "Target Weight": ref.get("target_weight"),
                "Current Pre-Live": current_status,
                "Saved CAGR": saved_cagr,
                "Current CAGR": current_cagr,
                "CAGR Delta": _portfolio_proposal_metric_delta(current_cagr, saved_cagr),
                "Saved MDD": saved_mdd,
                "Current MDD": current_mdd,
                "MDD Delta": _portfolio_proposal_metric_delta(current_mdd, saved_mdd),
                "Performance Signal": _portfolio_proposal_paper_tracking_signal(
                    current_status=current_status,
                    saved_cagr=saved_cagr,
                    current_cagr=current_cagr,
                    saved_mdd=saved_mdd,
                    current_mdd=current_mdd,
                ),
                "Tracking Cadence": tracking_plan.get("cadence"),
                "Stop Condition": tracking_plan.get("stop_condition"),
                "Success Condition": tracking_plan.get("success_condition"),
            }
        )
    return pd.DataFrame(display_rows)


# Find paper tracking feedback gaps between a proposal snapshot and the latest Pre-Live snapshots.
def _portfolio_proposal_paper_tracking_feedback_gaps(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> list[str]:
    gaps: list[str] = []
    evidence_by_registry_id = _portfolio_proposal_evidence_by_registry_id(row)
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        if not registry_id:
            continue
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        evidence = evidence_by_registry_id.get(registry_id) or {}
        result_snapshot = dict(pre_live_record.get("result_snapshot") or {})
        tracking_plan = dict(pre_live_record.get("tracking_plan") or {})
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        saved_cagr = _portfolio_proposal_optional_float(evidence.get("cagr"))
        saved_mdd = _portfolio_proposal_optional_float(evidence.get("mdd"))
        current_cagr = _portfolio_proposal_optional_float(result_snapshot.get("cagr"))
        current_mdd = _portfolio_proposal_optional_float(result_snapshot.get("mdd"))
        cagr_delta = _portfolio_proposal_metric_delta(current_cagr, saved_cagr)
        mdd_delta = _portfolio_proposal_metric_delta(current_mdd, saved_mdd)
        if not pre_live_record:
            gaps.append(f"{registry_id}: no active Pre-Live record is linked for paper tracking feedback.")
            continue
        if current_status != "paper_tracking":
            gaps.append(f"{registry_id}: current Pre-Live status is `{current_status}`, not `paper_tracking`.")
        if saved_cagr is None or saved_mdd is None:
            gaps.append(f"{registry_id}: proposal evidence snapshot is missing CAGR or MDD.")
        if current_cagr is None or current_mdd is None:
            gaps.append(f"{registry_id}: current Pre-Live result snapshot is missing CAGR or MDD.")
        if cagr_delta is not None and cagr_delta <= PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD:
            gaps.append(f"{registry_id}: CAGR delta `{cagr_delta}` is below the paper tracking threshold.")
        if mdd_delta is not None and mdd_delta <= PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD:
            gaps.append(f"{registry_id}: MDD delta `{mdd_delta}` is below the paper tracking threshold.")
        if current_status == "paper_tracking" and not tracking_plan.get("cadence"):
            gaps.append(f"{registry_id}: paper tracking cadence is not set.")
    return gaps


# Build a saved proposal summary table for paper tracking performance feedback.
def _build_portfolio_proposal_paper_tracking_feedback_summary_rows(
    rows: list[dict[str, Any]],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        feedback_df = _portfolio_proposal_paper_tracking_feedback_rows(row, pre_live_by_registry_id)
        gaps = _portfolio_proposal_paper_tracking_feedback_gaps(row, pre_live_by_registry_id)
        if feedback_df.empty:
            paper_tracking_count = 0
            missing_current_result_count = 0
            worsened_count = 0
            stable_or_better_count = 0
        else:
            paper_tracking_count = int((feedback_df["Current Pre-Live"] == "paper_tracking").sum())
            missing_current_result_count = int((feedback_df["Performance Signal"] == "missing_current_result").sum())
            worsened_count = int((feedback_df["Performance Signal"] == "worsened").sum())
            stable_or_better_count = int((feedback_df["Performance Signal"] == "stable_or_better").sum())
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Components": len(row.get("candidate_refs") or []),
                "Paper Tracking": paper_tracking_count,
                "Missing Current Result": missing_current_result_count,
                "Worsened": worsened_count,
                "Stable / Better": stable_or_better_count,
                "Feedback Gaps": len(gaps),
            }
        )
    return pd.DataFrame(display_rows)


# Build save blockers from selected proposal components and their target roles/weights.
def _portfolio_proposal_open_blockers(
    *,
    selected_rows: list[dict[str, Any]],
    component_inputs: dict[str, dict[str, Any]],
    proposal_id: str,
    total_weight: float,
) -> list[str]:
    blockers: list[str] = []
    if not proposal_id.strip():
        blockers.append("Proposal ID is required.")
    if not selected_rows:
        blockers.append("No current candidate selected.")
    if selected_rows and abs(total_weight - 100.0) > 0.01:
        blockers.append("Target weights must sum to 100%.")
    for row in selected_rows:
        registry_id = str(row.get("registry_id") or "")
        component_input = component_inputs.get(registry_id) or {}
        try:
            target_weight = float(component_input.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            target_weight = 0.0
        if component_input.get("pre_live_status") == "reject" and target_weight > 0:
            blockers.append(f"{registry_id}: rejected pre-live candidate cannot have active weight.")
        if component_input.get("proposal_role") == "core_anchor":
            result = dict(row.get("result") or {})
            if str(result.get("deployment") or "").lower() == "blocked":
                blockers.append(f"{registry_id}: blocked candidate cannot be core anchor without review.")
    return blockers


# Score whether the proposal draft is only saveable or ready for a later Live Readiness step.
def _build_portfolio_proposal_readiness_evaluation(
    *,
    selected_rows: list[dict[str, Any]],
    component_inputs: dict[str, dict[str, Any]],
    proposal_id: str,
    total_weight: float,
    operator_reason: str,
    next_action: str,
    review_date_value: date | None,
    open_blockers: list[str],
) -> dict[str, Any]:
    active_components = [
        (row, component_inputs.get(str(row.get("registry_id") or ""), {}))
        for row in selected_rows
        if _component_target_weight(component_inputs.get(str(row.get("registry_id") or ""), {}) or {}) > 0
    ]
    has_core_anchor = any(str(component.get("proposal_role") or "") == "core_anchor" for _, component in active_components)
    pre_live_ready = bool(active_components) and all(
        str(component.get("pre_live_status") or "") == "paper_tracking"
        for _, component in active_components
    )
    reason_ready = bool(operator_reason.strip())
    next_action_ready = bool(next_action.strip())
    review_date_ready = bool(review_date_value)
    identity_ready = bool(proposal_id.strip()) and bool(selected_rows)
    construction_ready = bool(selected_rows) and abs(total_weight - 100.0) <= 0.01
    blocker_ready = not open_blockers

    checks = [
        {
            "criteria": "Proposal Identity",
            "ready": identity_ready,
            "current_value": f"id={proposal_id or '-'}, components={len(selected_rows)}",
            "judgment": "proposal 초안 식별 가능" if identity_ready else "proposal id 또는 후보 선택 필요",
            "score": 1.2,
        },
        {
            "criteria": "Portfolio Construction",
            "ready": construction_ready,
            "current_value": f"weight_total={total_weight}%",
            "judgment": "비중 합계 100%" if construction_ready else "target weight 합계 확인 필요",
            "score": 1.8,
        },
        {
            "criteria": "Component Role",
            "ready": has_core_anchor,
            "current_value": "core_anchor 있음" if has_core_anchor else "core_anchor 없음",
            "judgment": "포트폴리오 중심 후보 있음" if has_core_anchor else "최소 1개 core anchor 필요",
            "score": 1.2,
        },
        {
            "criteria": "Pre-Live State",
            "ready": pre_live_ready,
            "current_value": ", ".join(
                sorted({str(component.get("pre_live_status") or "not_started") for _, component in active_components})
            )
            or "no active component",
            "judgment": "active 후보가 paper_tracking 상태" if pre_live_ready else "active 후보는 paper_tracking 상태가 필요",
            "score": 1.6,
        },
        {
            "criteria": "Operator Context",
            "ready": reason_ready and next_action_ready and review_date_ready,
            "current_value": (
                f"reason={'ok' if reason_ready else 'missing'}, "
                f"next_action={'ok' if next_action_ready else 'missing'}, "
                f"review_date={review_date_value.isoformat() if review_date_value else 'missing'}"
            ),
            "judgment": "판단 이유 / 다음 행동 / 날짜 있음"
            if reason_ready and next_action_ready and review_date_ready
            else "판단 이유, 다음 행동, review date 보강 필요",
            "score": 1.4,
        },
        {
            "criteria": "Blocking Scope",
            "ready": blocker_ready,
            "current_value": f"blockers={len(open_blockers)}",
            "judgment": "저장 blocker 없음" if blocker_ready else "저장 blocker 해결 필요",
            "score": 2.8,
        },
    ]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    score = min(score, 10.0)
    live_readiness_blockers = [str(check["criteria"]) for check in checks if not check["ready"]]
    can_save_proposal = bool(identity_ready and construction_ready and blocker_ready)
    can_move_to_live_readiness = bool(can_save_proposal and not live_readiness_blockers)

    if can_move_to_live_readiness:
        route_label = "LIVE_READINESS_CANDIDATE_READY"
        verdict = "Proposal 통과: 저장 후 Live Readiness 후보로 이동 가능"
        next_step = "Save Portfolio Proposal Draft로 포트폴리오 초안을 남긴 뒤 이후 Live Readiness 단계에서 실전 전 검토를 진행합니다."
    elif can_save_proposal:
        route_label = "PROPOSAL_DRAFT_READY"
        verdict = "Proposal 저장 가능: Live Readiness 전 보강 항목 있음"
        next_step = "Proposal draft는 저장할 수 있습니다. 남은 보강 항목을 해결한 뒤 Live Readiness 후보 여부를 다시 판단합니다."
    else:
        route_label = "PROPOSAL_BLOCKED"
        verdict = "Proposal 저장 전 blocker 해결 필요"
        next_step = "후보 선택, weight 합계, rejected/blocked 후보 비중 같은 저장 blocker를 먼저 해결합니다."

    return {
        "score": score,
        "checks": checks,
        "route_label": route_label,
        "verdict": verdict,
        "next_action": next_step,
        "blocking_reasons": live_readiness_blockers,
        "open_blockers": open_blockers,
        "can_save_proposal": can_save_proposal,
        "can_move_to_live_readiness": can_move_to_live_readiness,
    }
