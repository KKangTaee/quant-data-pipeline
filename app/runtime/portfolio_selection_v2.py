from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FINANCE_NOTE_DIR = PROJECT_ROOT / ".note" / "finance"
REGISTRIES_DIR = FINANCE_NOTE_DIR / "registries"
SAVED_DIR = FINANCE_NOTE_DIR / "saved"
ARCHIVE_DIR = FINANCE_NOTE_DIR / "archive" / "legacy_portfolio_workflow_v1"

PORTFOLIO_SELECTION_SOURCE_FILE = REGISTRIES_DIR / "PORTFOLIO_SELECTION_SOURCES.jsonl"
PRACTICAL_VALIDATION_RESULT_FILE = REGISTRIES_DIR / "PRACTICAL_VALIDATION_RESULTS.jsonl"
FINAL_SELECTION_DECISION_V2_FILE = REGISTRIES_DIR / "FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl"
SELECTED_PORTFOLIO_MONITORING_LOG_FILE = REGISTRIES_DIR / "SELECTED_PORTFOLIO_MONITORING_LOG.jsonl"
SAVED_PORTFOLIO_MIXES_FILE = SAVED_DIR / "SAVED_PORTFOLIO_MIXES.jsonl"

PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION = 1
PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION = 5
FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION = 2
SELECTED_PORTFOLIO_MONITORING_LOG_SCHEMA_VERSION = 1
SAVED_PORTFOLIO_MIX_SCHEMA_VERSION = 1

LEGACY_PORTFOLIO_WORKFLOW_FILES = [
    REGISTRIES_DIR / "CANDIDATE_REVIEW_NOTES.jsonl",
    REGISTRIES_DIR / "CURRENT_CANDIDATE_REGISTRY.jsonl",
    REGISTRIES_DIR / "PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
    REGISTRIES_DIR / "PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
    REGISTRIES_DIR / "PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl",
    REGISTRIES_DIR / "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
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
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


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


def append_final_selection_decision_v2(row: dict[str, Any]) -> None:
    """Persist one Final Review V2 decision row used by the selected dashboard."""
    _append_jsonl_row(FINAL_SELECTION_DECISION_V2_FILE, row)


def load_final_selection_decisions_v2(limit: int | None = 100) -> list[dict[str, Any]]:
    return _load_recent(FINAL_SELECTION_DECISION_V2_FILE, limit=limit, timestamp_keys=("updated_at", "created_at"))


def append_selected_portfolio_monitoring_log(row: dict[str, Any]) -> None:
    """Persist an explicit selected-portfolio monitoring snapshot."""
    _append_jsonl_row(SELECTED_PORTFOLIO_MONITORING_LOG_FILE, row)


def load_selected_portfolio_monitoring_logs(limit: int | None = 100) -> list[dict[str, Any]]:
    return _load_recent(SELECTED_PORTFOLIO_MONITORING_LOG_FILE, limit=limit, timestamp_keys=("updated_at", "created_at"))


def append_saved_portfolio_mix(row: dict[str, Any]) -> None:
    """Persist one reusable V2 saved mix setup; this is not a validation result."""
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
