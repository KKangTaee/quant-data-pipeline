from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORY_FILE = PROJECT_ROOT / ".note" / "finance" / "WEB_APP_RUN_HISTORY.jsonl"


def append_run_history(result: dict[str, Any]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


def load_run_history(limit: int = 50) -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in HISTORY_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return rows[-limit:][::-1]
