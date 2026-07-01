from __future__ import annotations

"""Append/load helpers for portfolio selection workflow JSONL records."""

import json
import shutil
from datetime import date, datetime
from decimal import Decimal
from math import isfinite
from pathlib import Path
from typing import Any

from app.workspace_paths import FINANCE_NOTE_DIR, REGISTRIES_DIR, SAVED_DIR

ARCHIVE_DIR = FINANCE_NOTE_DIR / "archive" / "legacy_portfolio_workflow_v1"

PORTFOLIO_SELECTION_SOURCE_FILE = REGISTRIES_DIR / "PORTFOLIO_SELECTION_SOURCES.jsonl"
PRACTICAL_VALIDATION_RESULT_FILE = REGISTRIES_DIR / "PRACTICAL_VALIDATION_RESULTS.jsonl"
FINAL_SELECTION_DECISION_FILE = REGISTRIES_DIR / "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl"
SELECTED_PORTFOLIO_MONITORING_LOG_FILE = REGISTRIES_DIR / "SELECTED_PORTFOLIO_MONITORING_LOG.jsonl"
SAVED_PORTFOLIO_MIXES_FILE = SAVED_DIR / "SAVED_PORTFOLIO_MIXES.jsonl"

PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION = 1
PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION = 5
FINAL_SELECTION_DECISION_CURRENT_SCHEMA_VERSION = 2
SELECTED_PORTFOLIO_MONITORING_LOG_SCHEMA_VERSION = 1
SAVED_PORTFOLIO_MIX_SCHEMA_VERSION = 1

LEGACY_PORTFOLIO_WORKFLOW_FILES = [
    REGISTRIES_DIR / "CANDIDATE_REVIEW_NOTES.jsonl",
    REGISTRIES_DIR / "CURRENT_CANDIDATE_REGISTRY.jsonl",
    REGISTRIES_DIR / "PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
    REGISTRIES_DIR / "PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
    REGISTRIES_DIR / "PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl",
    REGISTRIES_DIR / "FINAL_PORTFOLIO_SELECTION_DECISIONS_V1.jsonl",
]


def _read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _append_jsonl_row(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_ready(row), ensure_ascii=False) + "\n")


def _json_ready(value: Any) -> Any:
    """Normalize DB/UI scalar payloads before writing workflow JSONL rows."""

    if isinstance(value, dict):
        return {str(key): _json_ready(child) for key, child in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_ready(child) for child in value]
    if isinstance(value, Decimal):
        if not value.is_finite():
            return None
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float):
        return value if isfinite(value) else None
    if hasattr(value, "item"):
        try:
            return _json_ready(value.item())
        except Exception:
            pass
    if value.__class__.__name__ == "DataFrame" and hasattr(value, "to_dict"):
        try:
            return _json_ready(value.to_dict(orient="records"))
        except Exception:
            return str(value)
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        return str(value)


def _load_recent(path: Path, *, limit: int | None, timestamp_keys: tuple[str, ...]) -> list[dict[str, Any]]:
    rows = _read_jsonl_rows(path)
    rows = sorted(
        rows,
        key=lambda row: next((str(row.get(key) or "") for key in timestamp_keys if row.get(key)), ""),
        reverse=True,
    )
    if limit is None:
        return rows
    return rows[:limit]


def append_portfolio_selection_source(row: dict[str, Any]) -> None:
    """Persist one Backtest Analysis source selected for practical validation."""
    _append_jsonl_row(PORTFOLIO_SELECTION_SOURCE_FILE, row)


def load_portfolio_selection_sources(limit: int | None = 100) -> list[dict[str, Any]]:
    return _load_recent(PORTFOLIO_SELECTION_SOURCE_FILE, limit=limit, timestamp_keys=("updated_at", "created_at"))


def append_practical_validation_result(row: dict[str, Any]) -> None:
    """Persist one structured Practical Validation result without final operator memo."""
    _append_jsonl_row(PRACTICAL_VALIDATION_RESULT_FILE, row)


def load_practical_validation_results(limit: int | None = 100) -> list[dict[str, Any]]:
    return _load_recent(PRACTICAL_VALIDATION_RESULT_FILE, limit=limit, timestamp_keys=("updated_at", "created_at"))


def append_current_final_selection_decision(row: dict[str, Any]) -> None:
    """Persist one Final Review decision row used by the selected dashboard."""
    _append_jsonl_row(FINAL_SELECTION_DECISION_FILE, row)


def load_current_final_selection_decisions(limit: int | None = 100) -> list[dict[str, Any]]:
    return _load_recent(FINAL_SELECTION_DECISION_FILE, limit=limit, timestamp_keys=("updated_at", "created_at"))


def append_final_selection_decision_v2(row: dict[str, Any]) -> None:
    """Backward-compatible alias for older imports."""
    append_current_final_selection_decision(row)


def load_final_selection_decisions_v2(limit: int | None = 100) -> list[dict[str, Any]]:
    """Backward-compatible alias for older imports."""
    return load_current_final_selection_decisions(limit=limit)


def append_selected_portfolio_monitoring_log(row: dict[str, Any]) -> None:
    """Persist an explicit selected-portfolio monitoring snapshot."""
    _append_jsonl_row(SELECTED_PORTFOLIO_MONITORING_LOG_FILE, row)


def load_selected_portfolio_monitoring_logs(limit: int | None = 100) -> list[dict[str, Any]]:
    return _load_recent(SELECTED_PORTFOLIO_MONITORING_LOG_FILE, limit=limit, timestamp_keys=("updated_at", "created_at"))


def append_saved_portfolio_mix(row: dict[str, Any]) -> None:
    """Persist one reusable saved mix setup; this is not a validation result."""
    _append_jsonl_row(SAVED_PORTFOLIO_MIXES_FILE, row)


def load_saved_portfolio_mixes(limit: int | None = 100) -> list[dict[str, Any]]:
    return _load_recent(SAVED_PORTFOLIO_MIXES_FILE, limit=limit, timestamp_keys=("updated_at", "created_at"))


def archive_legacy_portfolio_workflow_files(*, archive_date: str | None = None) -> dict[str, Any]:
    """Copy legacy portfolio workflow JSONL files into archive without deleting originals."""
    archive_key = archive_date or datetime.now().strftime("%Y%m%d")
    target_dir = ARCHIVE_DIR / archive_key / "registries"
    copied: list[str] = []
    missing: list[str] = []
    target_dir.mkdir(parents=True, exist_ok=True)
    for source in LEGACY_PORTFOLIO_WORKFLOW_FILES:
        if not source.exists():
            missing.append(str(source))
            continue
        target = target_dir / source.name
        shutil.copy2(source, target)
        copied.append(str(target))
    return {
        "archive_dir": str(target_dir),
        "copied": copied,
        "missing": missing,
    }
