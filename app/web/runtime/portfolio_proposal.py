from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PORTFOLIO_PROPOSAL_REGISTRY_FILE = PROJECT_ROOT / ".note" / "finance" / "PORTFOLIO_PROPOSAL_REGISTRY.jsonl"
PORTFOLIO_PROPOSAL_SCHEMA_VERSION = 1


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


def append_portfolio_proposal(row: dict[str, Any]) -> None:
    PORTFOLIO_PROPOSAL_REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PORTFOLIO_PROPOSAL_REGISTRY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_portfolio_proposals(limit: int | None = 50) -> list[dict[str, Any]]:
    rows = _read_jsonl_rows(PORTFOLIO_PROPOSAL_REGISTRY_FILE)
    rows = sorted(
        rows,
        key=lambda row: str(row.get("updated_at") or row.get("created_at") or ""),
        reverse=True,
    )
    if limit is None:
        return rows
    return rows[:limit]
