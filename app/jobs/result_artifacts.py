from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_ARTIFACT_DIR = PROJECT_ROOT / ".note" / "finance" / "run_artifacts"
CSV_DIR = PROJECT_ROOT / "csv"
_SAFE_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")


def _safe_token(value: str | None, *, fallback: str) -> str:
    token = _SAFE_CHARS.sub("_", (value or "").strip())
    token = token.strip("._")
    return token or fallback


def _artifact_stamp(result: dict[str, Any]) -> str:
    raw = (
        result.get("started_at")
        or result.get("finished_at")
        or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return _safe_token(str(raw).replace(" ", "T").replace(":", "-"), fallback="run")


def _artifact_base_name(result: dict[str, Any]) -> str:
    return f"{_artifact_stamp(result)}_{_safe_token(str(result.get('job_name')), fallback='job')}"


def _dedupe_failure_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = (
            str(row.get("symbol") or ""),
            str(row.get("kind") or ""),
            str(row.get("detail") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _extract_failure_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    details = dict(result.get("details") or {})
    run_metadata = dict(result.get("run_metadata") or {})
    base = {
        "job_name": result.get("job_name"),
        "status": result.get("status"),
        "started_at": result.get("started_at"),
        "finished_at": result.get("finished_at"),
        "pipeline_type": run_metadata.get("pipeline_type"),
        "execution_mode": run_metadata.get("execution_mode"),
        "symbol_source": run_metadata.get("symbol_source"),
    }
    rows: list[dict[str, Any]] = []

    for symbol in result.get("failed_symbols") or []:
        rows.append(
            {
                **base,
                "symbol": symbol,
                "kind": "failed_symbol",
                "detail": result.get("message"),
            }
        )

    issue_mappings = {
        "missing_symbols": "provider_missing",
        "provider_no_data_symbols": "provider_no_data",
        "rate_limited_symbols": "rate_limited",
        "refresh_symbols_all": "preflight_refresh_candidate",
    }
    for key, kind in issue_mappings.items():
        for symbol in details.get(key) or []:
            rows.append(
                {
                    **base,
                    "symbol": symbol,
                    "kind": kind,
                    "detail": key,
                }
            )

    for row in details.get("rows") or []:
        symbol = row.get("symbol")
        diagnosis = row.get("diagnosis")
        if not symbol or not diagnosis:
            continue
        rows.append(
            {
                **base,
                "symbol": symbol,
                "kind": "price_stale_diagnosis",
                "detail": diagnosis,
            }
        )

    if not rows and result.get("status") != "success":
        rows.append(
            {
                **base,
                "symbol": "",
                "kind": "job_status",
                "detail": result.get("message"),
            }
        )

    return _dedupe_failure_rows(rows)


def write_run_artifacts(result: dict[str, Any]) -> dict[str, Any]:
    RUN_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    base_name = _artifact_base_name(result)
    artifact_dir = RUN_ARTIFACT_DIR / base_name
    counter = 2
    while artifact_dir.exists():
        artifact_dir = RUN_ARTIFACT_DIR / f"{base_name}_{counter}"
        counter += 1
    artifact_dir.mkdir(parents=True, exist_ok=False)

    result_json_path = artifact_dir / "result.json"
    result_json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    failure_rows = _extract_failure_rows(result)
    failure_csv_path: Path | None = None
    if failure_rows:
        failure_csv_path = CSV_DIR / f"{artifact_dir.name}_failures.csv"
        pd.DataFrame(failure_rows).to_csv(failure_csv_path, index=False)

    artifact_info = {
        "artifact_key": artifact_dir.name,
        "artifact_dir": str(artifact_dir),
        "result_json": str(result_json_path),
        "failure_csv": str(failure_csv_path) if failure_csv_path else None,
        "failure_row_count": len(failure_rows),
    }

    manifest_path = artifact_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(artifact_info, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    artifact_info["manifest_json"] = str(manifest_path)
    return artifact_info
