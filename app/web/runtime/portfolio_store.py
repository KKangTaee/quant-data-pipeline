from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAVED_PORTFOLIO_FILE = PROJECT_ROOT / ".note" / "finance" / "SAVED_PORTFOLIOS.jsonl"
SAVED_PORTFOLIO_SCHEMA_VERSION = 1


def _load_saved_portfolios_unbounded() -> list[dict[str, Any]]:
    if not SAVED_PORTFOLIO_FILE.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in SAVED_PORTFOLIO_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def load_saved_portfolios(limit: int | None = 50) -> list[dict[str, Any]]:
    rows = _load_saved_portfolios_unbounded()
    rows = sorted(rows, key=lambda row: str(row.get("updated_at") or row.get("saved_at") or ""), reverse=True)
    if limit is None:
        return rows
    return rows[:limit]


def save_saved_portfolio(
    *,
    name: str,
    description: str | None,
    compare_context: dict[str, Any],
    portfolio_context: dict[str, Any],
    source_context: dict[str, Any] | None = None,
    portfolio_id: str | None = None,
) -> dict[str, Any]:
    name = (name or "").strip()
    if not name:
        raise ValueError("Saved portfolio name is required.")

    saved_at = datetime.now().isoformat(timespec="seconds")
    existing_rows = _load_saved_portfolios_unbounded()

    existing = None
    if portfolio_id:
        for row in existing_rows:
            if row.get("portfolio_id") == portfolio_id:
                existing = row
                break

    record = {
        "schema_version": SAVED_PORTFOLIO_SCHEMA_VERSION,
        "portfolio_id": portfolio_id or f"portfolio_{uuid4().hex[:12]}",
        "saved_at": existing.get("saved_at") if existing else saved_at,
        "updated_at": saved_at,
        "name": name,
        "description": (description or "").strip(),
        "compare_context": compare_context,
        "portfolio_context": portfolio_context,
        "source_context": source_context or {},
    }

    replaced = False
    for idx, row in enumerate(existing_rows):
        if row.get("portfolio_id") == record["portfolio_id"]:
            existing_rows[idx] = record
            replaced = True
            break
    if not replaced:
        existing_rows.append(record)

    SAVED_PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SAVED_PORTFOLIO_FILE.open("w", encoding="utf-8") as f:
        for row in existing_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return record


def delete_saved_portfolio(portfolio_id: str) -> bool:
    existing_rows = _load_saved_portfolios_unbounded()
    filtered_rows = [row for row in existing_rows if row.get("portfolio_id") != portfolio_id]
    if len(filtered_rows) == len(existing_rows):
        return False

    SAVED_PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SAVED_PORTFOLIO_FILE.open("w", encoding="utf-8") as f:
        for row in filtered_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return True
