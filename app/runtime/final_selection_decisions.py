from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FINANCE_NOTE_DIR = PROJECT_ROOT / ".note" / "finance"
REGISTRIES_DIR = FINANCE_NOTE_DIR / "registries"
FINAL_SELECTION_DECISION_REGISTRY_FILE = REGISTRIES_DIR / "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl"
FINAL_SELECTION_DECISION_SCHEMA_VERSION = 1


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


def append_final_selection_decision(row: dict[str, Any]) -> None:
    """Append one explicit final selection decision without mutating source registries."""
    FINAL_SELECTION_DECISION_REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with FINAL_SELECTION_DECISION_REGISTRY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_final_selection_decisions(limit: int | None = 100) -> list[dict[str, Any]]:
    """Load saved final selection decisions in recent-first order for UI review."""
    rows = _read_jsonl_rows(FINAL_SELECTION_DECISION_REGISTRY_FILE)
    rows = sorted(
        rows,
        key=lambda row: str(row.get("updated_at") or row.get("created_at") or ""),
        reverse=True,
    )
    if limit is None:
        return rows
    return rows[:limit]
