from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKTEST_HISTORY_FILE = PROJECT_ROOT / ".note" / "finance" / "BACKTEST_RUN_HISTORY.jsonl"
BACKTEST_HISTORY_SCHEMA_VERSION = 1


def _extract_primary_summary(bundle: dict[str, Any]) -> dict[str, Any]:
    summary_df = bundle.get("summary_df")
    if summary_df is None or summary_df.empty:
        return {}

    row = summary_df.iloc[0]
    return {
        "strategy_name": row.get("Name"),
        "start_date": str(row.get("Start Date")),
        "end_date": str(row.get("End Date")),
        "start_balance": float(row.get("Start Balance")),
        "end_balance": float(row.get("End Balance")),
        "cagr": float(row.get("CAGR")),
        "standard_deviation": float(row.get("Standard Deviation")),
        "sharpe_ratio": float(row.get("Sharpe Ratio")),
        "maximum_drawdown": float(row.get("Maximum Drawdown")),
    }


def append_backtest_run_history(
    *,
    bundle: dict[str, Any],
    run_kind: str,
    context: dict[str, Any] | None = None,
) -> None:
    meta = dict(bundle.get("meta") or {})
    record = {
        "schema_version": BACKTEST_HISTORY_SCHEMA_VERSION,
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "run_kind": run_kind,
        "strategy_key": meta.get("strategy_key"),
        "execution_mode": meta.get("execution_mode"),
        "data_mode": meta.get("data_mode"),
        "tickers": meta.get("tickers", []),
        "input_start": meta.get("start"),
        "input_end": meta.get("end"),
        "timeframe": meta.get("timeframe"),
        "option": meta.get("option"),
        "rebalance_interval": meta.get("rebalance_interval"),
        "top": meta.get("top"),
        "vol_window": meta.get("vol_window"),
        "factor_freq": meta.get("factor_freq"),
        "rebalance_freq": meta.get("rebalance_freq"),
        "snapshot_mode": meta.get("snapshot_mode"),
        "quality_factors": meta.get("quality_factors"),
        "universe_mode": meta.get("universe_mode"),
        "preset_name": meta.get("preset_name"),
        "warnings": meta.get("warnings", []),
        "summary": _extract_primary_summary(bundle),
        "context": context or {},
    }

    BACKTEST_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with BACKTEST_HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_backtest_run_history(limit: int = 30) -> list[dict[str, Any]]:
    if not BACKTEST_HISTORY_FILE.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in BACKTEST_HISTORY_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return rows[-limit:][::-1]
