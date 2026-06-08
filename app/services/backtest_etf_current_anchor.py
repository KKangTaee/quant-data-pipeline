from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable

from app.services.backtest_etf_evidence_expansion import ETF_EVIDENCE_EXPANSION_TARGET_KEYS
from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME


_COMMON_ROUTE_BOUNDARY = (
    "Backtest Analysis current-anchor workbench only; Practical Validation owns evidence results, "
    "Final Review owns selected-route decisions, and Portfolio Monitoring remains read-only."
)

_RUN_TIMESTAMP_KEYS = ("recorded_at", "updated_at", "created_at")
_SOURCE_TIMESTAMP_KEYS = ("updated_at", "created_at", "recorded_at")


def _normalize_key(value: Any) -> str:
    return str(value or "").strip().lower()


def _timestamp_text(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    return next((str(row.get(key) or "") for key in keys if row.get(key)), "")


def _strategy_key_from_run(row: dict[str, Any]) -> str:
    meta = dict(row.get("meta") or {})
    return _normalize_key(row.get("strategy_key") or meta.get("strategy_key"))


def _strategy_keys_from_source(row: dict[str, Any]) -> set[str]:
    keys = {_normalize_key(row.get("strategy_key"))}
    for component in row.get("components") or []:
        if isinstance(component, dict):
            keys.add(_normalize_key(component.get("strategy_key")))
            keys.add(_normalize_key(component.get("strategy_family")))
    return {key for key in keys if key}


def _latest_by_strategy(
    rows: Iterable[dict[str, Any]],
    *,
    strategy_key: str,
    row_key_getter: Any,
    timestamp_keys: tuple[str, ...],
) -> dict[str, Any] | None:
    matched: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_keys = row_key_getter(row)
        candidate_keys = row_keys if isinstance(row_keys, set) else {row_keys}
        if strategy_key in candidate_keys:
            matched.append(dict(row))
    if not matched:
        return None
    return sorted(matched, key=lambda row: _timestamp_text(row, timestamp_keys), reverse=True)[0]


def _nested_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if row.get(key) not in (None, ""):
            return row.get(key)
    gate_snapshot = dict(row.get("gate_snapshot") or {})
    for key in keys:
        if gate_snapshot.get(key) not in (None, ""):
            return gate_snapshot.get(key)
    return None


def _price_freshness_status(row: dict[str, Any]) -> str | None:
    freshness = dict(row.get("price_freshness") or {})
    value = (
        freshness.get("status")
        or _nested_value(row, "price_freshness_status")
        or _nested_value(row, "data_trust_status")
    )
    return str(value) if value not in (None, "") else None


def _has_any_value(row: dict[str, Any], fields: tuple[str, ...]) -> bool:
    return any(_nested_value(row, field) not in (None, "", [], {}) for field in fields)


def _summarize_latest_run(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    summary = dict(row.get("summary") or {})
    return {
        "recorded_at": row.get("recorded_at") or row.get("updated_at") or row.get("created_at"),
        "actual_result_start": row.get("actual_result_start") or summary.get("start_date"),
        "actual_result_end": row.get("actual_result_end") or summary.get("end_date"),
        "result_rows": row.get("result_rows"),
        "cagr": summary.get("cagr"),
        "maximum_drawdown": summary.get("maximum_drawdown") or summary.get("mdd"),
        "sharpe_ratio": summary.get("sharpe_ratio") or summary.get("sharpe"),
        "price_freshness_status": _price_freshness_status(row),
        "promotion_decision": _nested_value(row, "promotion_decision"),
        "cost_application_status": _nested_value(row, "cost_application_status"),
        "net_cost_curve_status": _nested_value(row, "net_cost_curve_status"),
        "benchmark_policy_status": _nested_value(row, "benchmark_policy_status"),
        "liquidity_policy_status": _nested_value(row, "liquidity_policy_status"),
        "etf_operability_status": _nested_value(row, "etf_operability_status"),
        "warning_count": len(row.get("warnings") or []),
    }


def _summarize_latest_source(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "selection_source_id": row.get("selection_source_id"),
        "source_kind": row.get("source_kind"),
        "source_title": row.get("source_title"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "source_status": row.get("source_status"),
    }


def _missing_evidence(*, latest_run: dict[str, Any] | None, latest_source: dict[str, Any] | None) -> list[str]:
    gaps: list[str] = []
    if latest_run is None:
        gaps.append("latest DB-backed backtest run")
        gaps.append("Backtest Analysis selection source")
        return gaps

    if latest_source is None:
        gaps.append("Backtest Analysis selection source")
    if not _price_freshness_status(latest_run):
        gaps.append("price freshness evidence")
    if not _has_any_value(
        latest_run,
        (
            "cost_application_status",
            "cost_model_source",
            "transaction_cost_bps",
            "net_cost_curve_status",
        ),
    ):
        gaps.append("cost application / net-cost curve evidence")
    if not _has_any_value(latest_run, ("benchmark_policy_status", "benchmark_contract", "benchmark_ticker")):
        gaps.append("benchmark / comparator policy evidence")
    if not _has_any_value(latest_run, ("etf_operability_status", "liquidity_policy_status")):
        gaps.append("ETF provider / liquidity evidence")
    return gaps


def _anchor_status(*, latest_run: dict[str, Any] | None, latest_source: dict[str, Any] | None, gaps: list[str]) -> str:
    if latest_run is None:
        return "RERUN_REQUIRED"
    if latest_source is None:
        return "SOURCE_HANDOFF_REQUIRED"
    if gaps:
        return "ANCHOR_EVIDENCE_REVIEW_REQUIRED"
    return "ANCHOR_READY_FOR_REVIEW"


def _recommended_next_action(*, display_name: str, status: str) -> str:
    if status == "RERUN_REQUIRED":
        return (
            f"Run latest DB-backed {display_name} backtest and review Data Trust Summary before creating a current-anchor source."
        )
    if status == "SOURCE_HANDOFF_REQUIRED":
        return (
            f"Create a Backtest Analysis selection source for {display_name} after reviewing the latest run evidence."
        )
    if status == "ANCHOR_EVIDENCE_REVIEW_REQUIRED":
        return (
            f"Review missing ETF provider / cost / benchmark evidence for {display_name} before current candidate promotion."
        )
    return (
        f"Use {display_name} as current anchor review input; keep registry promotion for an approved follow-up task."
    )


def _load_default_run_history_rows() -> list[dict[str, Any]]:
    from app.runtime.history import load_backtest_run_history

    return load_backtest_run_history(limit=200)


def _load_default_selection_source_rows() -> list[dict[str, Any]]:
    from app.runtime.portfolio_selection_v2 import load_portfolio_selection_sources

    return load_portfolio_selection_sources(limit=200)


def build_etf_current_anchor_workbench(
    *,
    run_history_rows: Iterable[dict[str, Any]] | None = None,
    selection_source_rows: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a read-only ETF current-anchor workbench from existing local workflow artifacts."""

    runs = list(run_history_rows) if run_history_rows is not None else _load_default_run_history_rows()
    sources = (
        list(selection_source_rows)
        if selection_source_rows is not None
        else _load_default_selection_source_rows()
    )

    rows: list[dict[str, Any]] = []
    for strategy_key in ETF_EVIDENCE_EXPANSION_TARGET_KEYS:
        display_name = STRATEGY_KEY_TO_DISPLAY_NAME[strategy_key]
        latest_run = _latest_by_strategy(
            runs,
            strategy_key=strategy_key,
            row_key_getter=_strategy_key_from_run,
            timestamp_keys=_RUN_TIMESTAMP_KEYS,
        )
        latest_source = _latest_by_strategy(
            sources,
            strategy_key=strategy_key,
            row_key_getter=_strategy_keys_from_source,
            timestamp_keys=_SOURCE_TIMESTAMP_KEYS,
        )
        gaps = _missing_evidence(latest_run=latest_run, latest_source=latest_source)
        status = _anchor_status(latest_run=latest_run, latest_source=latest_source, gaps=gaps)
        rows.append(
            {
                "strategy_key": strategy_key,
                "display_name": display_name,
                "anchor_status": status,
                "latest_run": _summarize_latest_run(latest_run),
                "latest_source": _summarize_latest_source(latest_source),
                "missing_evidence": gaps,
                "recommended_next_action": _recommended_next_action(display_name=display_name, status=status),
                "route_boundary": _COMMON_ROUTE_BOUNDARY,
            }
        )

    ready_count = sum(1 for row in rows if row["anchor_status"] == "ANCHOR_READY_FOR_REVIEW")
    latest_run_count = sum(1 for row in rows if row["latest_run"])
    source_count = sum(1 for row in rows if row["latest_source"])
    return deepcopy(
        {
            "workbench_id": "etf_current_anchor_workbench_v1",
            "title": "ETF Current Anchor Workbench",
            "status": "Read-only current-anchor workbench",
            "target_strategy_keys": list(ETF_EVIDENCE_EXPANSION_TARGET_KEYS),
            "summary": (
                "Reads existing run history and Practical Validation source handoff rows to show which ETF strategies "
                "have enough local evidence to become current-anchor review inputs."
            ),
            "rows": rows,
            "latest_run_count": latest_run_count,
            "source_count": source_count,
            "ready_count": ready_count,
            "gap_count": len(rows) - ready_count,
            "creates_current_candidate": False,
            "runs_backtests": False,
            "writes_validation_results": False,
            "storage_boundary": (
                "Read-only current-anchor workbench; does not write the Current candidate registry, saved setups, "
                "run history, validation results, final decisions, monitoring logs, provider snapshots, or rerun matrix artifacts."
            ),
            "route_boundary": _COMMON_ROUTE_BOUNDARY,
        }
    )
