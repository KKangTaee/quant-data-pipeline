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


def estimate_duration_from_history(job_name: str, symbol_count: int) -> dict[str, Any]:
    history = load_run_history(limit=200)
    relevant = [
        item for item in history
        if item.get("job_name") == job_name
        and (item.get("symbols_requested") or 0) > 0
        and (item.get("duration_sec") or 0) > 0
    ]

    if not relevant or symbol_count <= 0:
        return {
            "available": False,
            "message": "No estimate available yet.",
        }

    per_symbol = [
        float(item["duration_sec"]) / float(item["symbols_requested"])
        for item in relevant
        if item.get("symbols_requested")
    ]
    if not per_symbol:
        return {
            "available": False,
            "message": "No estimate available yet.",
        }

    avg = sum(per_symbol) / len(per_symbol)
    estimate_sec = avg * symbol_count
    low = max(1, int(estimate_sec * 0.7))
    high = max(low, int(estimate_sec * 1.3))

    return {
        "available": True,
        "seconds_low": low,
        "seconds_high": high,
        "message": f"Estimated runtime: {low // 60}m {low % 60}s - {high // 60}m {high % 60}s",
    }
