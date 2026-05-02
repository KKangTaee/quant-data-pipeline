from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FINANCE_NOTE_DIR = PROJECT_ROOT / ".note" / "finance"
REGISTRIES_DIR = FINANCE_NOTE_DIR / "registries"
CURRENT_CANDIDATE_REGISTRY_FILE = REGISTRIES_DIR / "CURRENT_CANDIDATE_REGISTRY.jsonl"
PRE_LIVE_CANDIDATE_REGISTRY_FILE = REGISTRIES_DIR / "PRE_LIVE_CANDIDATE_REGISTRY.jsonl"
CANDIDATE_REVIEW_NOTES_FILE = REGISTRIES_DIR / "CANDIDATE_REVIEW_NOTES.jsonl"


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


def load_current_candidate_registry_latest() -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl_rows(CURRENT_CANDIDATE_REGISTRY_FILE):
        registry_id = str(row.get("registry_id") or "").strip()
        if not registry_id:
            continue
        previous = latest.get(registry_id)
        if previous is None or str(row.get("recorded_at") or "") >= str(previous.get("recorded_at") or ""):
            latest[registry_id] = row

    family_order = {"value": 0, "quality": 1, "quality_value": 2}
    role_order = {"current_candidate": 0, "near_miss": 1, "scenario": 2}
    return sorted(
        [
            row
            for row in latest.values()
            if str(row.get("status") or "active").strip().lower() == "active"
        ],
        key=lambda row: (
            family_order.get(str(row.get("strategy_family") or ""), 99),
            role_order.get(str(row.get("record_type") or ""), 99),
            str(row.get("title") or ""),
        ),
    )


def append_current_candidate_registry_row(row: dict[str, Any]) -> None:
    _append_jsonl_row(CURRENT_CANDIDATE_REGISTRY_FILE, row)


def append_candidate_review_note(row: dict[str, Any]) -> None:
    _append_jsonl_row(CANDIDATE_REVIEW_NOTES_FILE, row)


def load_candidate_review_notes() -> list[dict[str, Any]]:
    rows = [
        row
        for row in _read_jsonl_rows(CANDIDATE_REVIEW_NOTES_FILE)
        if str(row.get("record_status") or "active").strip().lower() == "active"
    ]
    return sorted(rows, key=lambda row: str(row.get("recorded_at") or ""), reverse=True)


def load_pre_live_candidate_registry_latest() -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl_rows(PRE_LIVE_CANDIDATE_REGISTRY_FILE):
        pre_live_id = str(row.get("pre_live_id") or "").strip()
        if not pre_live_id:
            continue
        previous = latest.get(pre_live_id)
        if previous is None or str(row.get("recorded_at") or "") >= str(previous.get("recorded_at") or ""):
            latest[pre_live_id] = row

    return sorted(
        [
            row
            for row in latest.values()
            if str(row.get("record_status") or "active").strip().lower() == "active"
        ],
        key=lambda row: (
            str(row.get("pre_live_status") or ""),
            str(row.get("title") or ""),
        ),
    )


def append_pre_live_candidate_registry_row(row: dict[str, Any]) -> None:
    _append_jsonl_row(PRE_LIVE_CANDIDATE_REGISTRY_FILE, row)
