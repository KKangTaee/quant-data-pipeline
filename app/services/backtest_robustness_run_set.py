from __future__ import annotations

from typing import Any


ROBUSTNESS_RUN_SET_SCHEMA_VERSION = "robustness_run_set_v1"

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}

_PARAMETER_TERMS = (
    "parameter",
    "perturb",
    "lookback",
    "ma window",
    "ma_window",
    "interval",
    "rebalance",
    "momentum",
)

_COST_SLIPPAGE_TERMS = (
    "cost",
    "slippage",
    "spread",
    "bps",
    "transaction",
)


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _status(value: Any, *, default: str = "NEEDS_INPUT") -> str:
    text = str(value or "").strip().upper()
    if not text or text in {"-", "NONE", "NULL", "N/A", "UNKNOWN"}:
        return default
    if text in {"BLOCKED", "BLOCK", "ERROR", "FAILED", "FAIL"} or "ERROR" in text:
        return "BLOCKED"
    if text in {"NOT_RUN", "MISSING", "NO_DATA", "UNAVAILABLE", "NEEDS_INPUT"}:
        return "NEEDS_INPUT"
    if text in {"PASS", "OK", "READY", "SUCCESS", "COMPLETE", "COMPLETED"}:
        return "PASS"
    if text.startswith("READY_"):
        return "PASS"
    if text in {"REVIEW", "STALE", "PARTIAL", "WARNING", "WARN", "WATCH"} or "REVIEW" in text:
        return "REVIEW"
    return default


def _display_status(value: Any, *, default: str = "NEEDS_INPUT") -> str:
    text = str(value or "").strip().upper()
    if text == "NOT_RUN":
        return "NOT_RUN"
    return _status(text, default=default)


def _combine_statuses(values: list[Any]) -> str:
    statuses = [_status(value) for value in values if str(value or "").strip()]
    if not statuses:
        return "NEEDS_INPUT"
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "NEEDS_INPUT" in statuses:
        return "NEEDS_INPUT"
    if "REVIEW" in statuses:
        return "REVIEW"
    if set(statuses) == {"PASS"}:
        return "PASS"
    return "REVIEW"


def _slug(value: Any, fallback: str = "unknown") -> str:
    text = _safe_text(value, fallback).lower()
    chars = [char if char.isalnum() else "_" for char in text]
    slug = "_".join("".join(chars).split("_"))
    return slug or fallback


def _plain_mapping(value: Any, *, limit: int = 40) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    for key, raw in value.items():
        if len(result) >= limit:
            break
        if isinstance(raw, (str, int, float, bool)) or raw is None:
            result[str(key)] = raw
        elif isinstance(raw, (list, tuple)):
            primitives = [item for item in raw if isinstance(item, (str, int, float, bool))]
            if primitives:
                result[str(key)] = primitives[:20]
    return result


def _source_snapshot(validation: dict[str, Any]) -> dict[str, Any]:
    return dict(validation.get("selection_source_snapshot") or validation.get("source_snapshot") or {})


def _source_settings(source: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(source.get("source_snapshot") or {})
    settings = dict(snapshot.get("settings_snapshot") or {})
    settings.update(dict(source.get("settings_snapshot") or {}))
    return settings


def _components(source: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(item or {}) for item in _as_list(source.get("components")) if isinstance(item, dict)]


def _strategy_identity(validation: dict[str, Any], source: dict[str, Any]) -> tuple[str, str]:
    settings = _source_settings(source)
    components = _components(source)
    first_component = components[0] if components else {}
    strategy_key = (
        settings.get("strategy_key")
        or first_component.get("strategy_key")
        or validation.get("strategy_key")
        or source.get("strategy_key")
        or source.get("source_kind")
    )
    strategy_family = (
        settings.get("strategy_family")
        or first_component.get("strategy_family")
        or first_component.get("strategy_name")
        or validation.get("strategy_family")
        or source.get("strategy_family")
        or source.get("source_kind")
    )
    return _safe_text(strategy_family), _safe_text(strategy_key)


def _frozen_parameter_set(source: dict[str, Any]) -> dict[str, Any]:
    settings = _plain_mapping(_source_settings(source))
    components = _components(source)
    component_rows: list[dict[str, Any]] = []
    for component in components[:12]:
        replay_contract = dict(component.get("replay_contract") or {})
        component_settings = _plain_mapping(dict(replay_contract.get("settings_snapshot") or {}), limit=20)
        component_rows.append(
            {
                "component": component.get("title")
                or component.get("strategy_name")
                or component.get("component_id")
                or "-",
                "strategy_key": component.get("strategy_key") or component_settings.get("strategy_key"),
                "target_weight": component.get("target_weight"),
                "settings": component_settings,
            }
        )
    return {
        "settings_snapshot": settings,
        "components": component_rows,
    }


def _evidence_summary(evidence: dict[str, Any], *, label: str) -> dict[str, Any]:
    metrics = dict(evidence.get("metrics") or {})
    status = _display_status(evidence.get("status"))
    return {
        "label": label,
        "status": status,
        "summary": evidence.get("summary") or "-",
        "metrics": metrics,
        "next_action": evidence.get("next_action") or ("추가 조치 없음" if status == "PASS" else "evidence를 보강합니다."),
    }


def _row_status(row: dict[str, Any]) -> str:
    return _display_status(
        row.get("Status")
        or row.get("Result Status")
        or row.get("Judgment")
        or row.get("Current")
        or row.get("status")
    )


def _row_text(row: dict[str, Any]) -> str:
    parts = [
        row.get("Criteria"),
        row.get("Check"),
        row.get("Scenario"),
        row.get("Scope"),
        row.get("Evidence"),
        row.get("Meaning"),
    ]
    return " ".join(str(item or "") for item in parts).lower()


def _compact_evidence_row(area: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Area": area,
        "Criteria": row.get("Criteria") or row.get("Check") or row.get("Scenario") or row.get("Metric") or area,
        "Status": _row_status(row),
        "Evidence": row.get("Evidence") or row.get("Finding") or row.get("Current") or row.get("Scope") or "-",
        "Next Action": row.get("Next Action") or row.get("Next Check") or row.get("Required Action") or "-",
    }


def _non_pass_rows(area: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for row in rows:
        status = _row_status(row)
        if _status(status) != "PASS" or status == "NOT_RUN":
            compact.append(_compact_evidence_row(area, row))
    return compact


def _artifact_references(source: dict[str, Any]) -> list[dict[str, Any]]:
    raw_refs: list[Any] = []
    for key in (
        "generated_artifacts",
        "generated_artifact_references",
        "artifact_references",
        "related_generated_artifacts",
    ):
        raw_refs.extend(_as_list(source.get(key)))
    refs: list[dict[str, Any]] = []
    for item in raw_refs[:12]:
        if isinstance(item, dict):
            row = {
                key: value
                for key, value in item.items()
                if key in {"type", "path", "label", "reference", "description"} and value not in (None, "")
            }
            if row:
                refs.append(row)
        elif item not in (None, ""):
            refs.append({"reference": str(item)})
    return refs


def _cost_slippage_summary(validation: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    audit = dict(validation.get("backtest_realism_audit") or {})
    rows = [
        dict(row or {})
        for row in _as_list(audit.get("rows"))
        if isinstance(row, dict) and any(term in _row_text(dict(row or {})) for term in _COST_SLIPPAGE_TERMS)
    ]
    if not rows:
        robustness = dict(validation.get("robustness_validation") or {})
        rows = [
            dict(row or {})
            for row in _as_list(robustness.get("sensitivity_rows") or validation.get("sensitivity_rows"))
            if isinstance(row, dict) and any(term in _row_text(dict(row or {})) for term in _COST_SLIPPAGE_TERMS)
        ]
    status = _combine_statuses([_row_status(row) for row in rows]) if rows else "NEEDS_INPUT"
    evidence = _safe_text(rows[0].get("Evidence") or rows[0].get("Finding") if rows else None, "cost / slippage sensitivity evidence missing")
    return (
        {
            "status": status,
            "summary": evidence,
            "row_count": len(rows),
        },
        _non_pass_rows("Cost / Slippage Sensitivity", rows),
    )


def _parameter_perturbation_summary(validation: dict[str, Any], board: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    robustness = dict(validation.get("robustness_validation") or {})
    rows = [
        dict(row or {})
        for row in _as_list(robustness.get("sensitivity_rows") or validation.get("sensitivity_rows"))
        if isinstance(row, dict) and any(term in _row_text(dict(row or {})) for term in _PARAMETER_TERMS)
    ]
    metrics = dict(board.get("metrics") or {})
    runtime_followup_count = int(metrics.get("runtime_followup_count") or 0)
    statuses = [_row_status(row) for row in rows]
    if runtime_followup_count:
        statuses.append("REVIEW")
    status = _combine_statuses(statuses) if statuses else "NEEDS_INPUT"
    return (
        {
            "status": status,
            "summary": (
                f"{len(rows)} parameter rows / runtime follow-up {runtime_followup_count}"
                if rows or runtime_followup_count
                else "strategy-specific parameter perturbation evidence missing"
            ),
            "row_count": len(rows),
            "runtime_followup_count": runtime_followup_count,
        },
        _non_pass_rows("Parameter Perturbation", rows),
    )


def _experiment_types(
    *,
    board: dict[str, Any],
    validation: dict[str, Any],
    cost_summary: dict[str, Any],
    parameter_summary: dict[str, Any],
) -> list[str]:
    metrics = dict(board.get("metrics") or {})
    types: set[str] = set()
    if board or metrics.get("covered_stress_windows") is not None:
        types.add("stress")
    if metrics.get("rolling_window_count"):
        types.add("rolling")
    if metrics.get("computed_sensitivity_checks") is not None or validation.get("sensitivity_rows"):
        types.add("sensitivity")
    if parameter_summary.get("row_count") or parameter_summary.get("runtime_followup_count"):
        types.add("parameter_perturbation")
    if validation.get("temporal_validation") or validation.get("walkforward_validation"):
        types.add("walk_forward")
    if validation.get("oos_holdout_validation"):
        types.add("oos_holdout")
    if validation.get("regime_split_validation"):
        types.add("regime_split")
    if cost_summary.get("row_count"):
        types.add("cost_slippage_sensitivity")
    if metrics.get("local_trial_count"):
        types.add("local_overfit")
    return sorted(types)


def _status_evidence_from_summary(area: str, summary: dict[str, Any]) -> list[dict[str, Any]]:
    status = _display_status(summary.get("status"))
    if _status(status) == "PASS" and status != "NOT_RUN":
        return []
    return [
        {
            "Area": area,
            "Criteria": summary.get("label") or area,
            "Status": status,
            "Evidence": summary.get("summary") or "-",
            "Next Action": summary.get("next_action") or "-",
        }
    ]


def build_robustness_run_set_summary(validation: dict[str, Any]) -> dict[str, Any]:
    """Build compact run-set provenance from existing Practical Validation evidence."""

    validation = dict(validation or {})
    source = _source_snapshot(validation)
    source_id = _safe_text(source.get("source_id") or validation.get("selection_source_id"))
    validation_id = _safe_text(validation.get("validation_id"), source_id)
    strategy_family, strategy_key = _strategy_identity(validation, source)
    robustness = dict(validation.get("robustness_validation") or {})
    board = dict(robustness.get("robustness_lab_board") or validation.get("robustness_lab_board") or {})
    board_summary = _evidence_summary(board, label="Robustness Lab")
    walk_forward = _evidence_summary(
        dict(validation.get("temporal_validation") or validation.get("walkforward_validation") or {}),
        label="Walk-forward temporal validation",
    )
    oos = _evidence_summary(dict(validation.get("oos_holdout_validation") or {}), label="OOS holdout validation")
    regime = _evidence_summary(dict(validation.get("regime_split_validation") or {}), label="Regime split validation")
    cost_summary, cost_non_pass = _cost_slippage_summary(validation)
    parameter_summary, parameter_non_pass = _parameter_perturbation_summary(validation, board)
    experiment_types = _experiment_types(
        board=board,
        validation=validation,
        cost_summary=cost_summary,
        parameter_summary=parameter_summary,
    )
    evidence_rows: list[dict[str, Any]] = []
    evidence_rows.extend(_non_pass_rows("Robustness Lab", [dict(row or {}) for row in _as_list(board.get("follow_up_rows")) if isinstance(row, dict)]))
    evidence_rows.extend(_status_evidence_from_summary("Walk-forward", walk_forward))
    evidence_rows.extend(_status_evidence_from_summary("OOS Holdout", oos))
    evidence_rows.extend(_status_evidence_from_summary("Regime Split", regime))
    evidence_rows.extend(cost_non_pass)
    evidence_rows.extend(parameter_non_pass)
    statuses = [
        board_summary.get("status"),
        walk_forward.get("status"),
        oos.get("status"),
        regime.get("status"),
        cost_summary.get("status"),
        parameter_summary.get("status"),
    ]
    overall_status = _combine_statuses(statuses)
    if overall_status == "PASS" and evidence_rows:
        overall_status = "REVIEW"
    decision_effect = {
        "practical_validation": overall_status,
        "final_review": overall_status,
        "treat_as_pass": overall_status == "PASS",
        "reason": (
            "run-set evidence is ready"
            if overall_status == "PASS"
            else "run-set has non-pass robustness evidence that must remain visible"
        ),
    }
    return {
        "schema_version": ROBUSTNESS_RUN_SET_SCHEMA_VERSION,
        "robustness_run_set_id": f"robustness_run_set_{_slug(validation_id)}",
        "overall_status": overall_status,
        "strategy_family": strategy_family,
        "strategy_key": strategy_key,
        "source_id": source_id,
        "selection_source_id": validation.get("selection_source_id") or source_id,
        "source_title": source.get("source_title") or source_id,
        "source_kind": source.get("source_kind") or validation.get("source_kind"),
        "promotion_contract_reference": source.get("promotion_contract_reference")
        or source.get("promotion_contract")
        or source.get("related_promotion_contract"),
        "frozen_parameter_set": _frozen_parameter_set(source),
        "experiment_types": experiment_types,
        "is_oos_window": {
            "status": oos.get("status"),
            "summary": oos.get("summary"),
            "in_sample_months": dict(oos.get("metrics") or {}).get("in_sample_months"),
            "out_sample_months": dict(oos.get("metrics") or {}).get("out_sample_months"),
        },
        "walk_forward_summary": walk_forward,
        "regime_split_summary": regime,
        "cost_slippage_sensitivity_summary": cost_summary,
        "parameter_perturbation_summary": parameter_summary,
        "not_run_review_blocked_evidence": evidence_rows[:24],
        "generated_artifact_references": _artifact_references(source),
        "decision_effect": decision_effect,
        "storage_boundary": {
            "write_policy": "compact_read_model_only",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "full_artifact_persistence": False,
            "full_trade_log_persistence": False,
            "full_holdings_persistence": False,
            "raw_provider_response_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "ROBUSTNESS_RUN_SET_SCHEMA_VERSION",
    "build_robustness_run_set_summary",
]
