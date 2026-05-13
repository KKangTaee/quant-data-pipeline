#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

GENERATED_PATTERNS = [
    ".note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl",
    ".note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl",
    ".note/finance/saved/SAVED_PORTFOLIOS.jsonl",
    ".note/finance/backtest_artifacts/*",
    ".note/finance/run_artifacts/*",
    ".note/finance/phases/active/phase12/_tmp_gtaa_*.csv",
    "csv/*daily_market_update_failures.csv",
    "*.ipynb",
    "*.DS_Store",
]

ROOT_LOGS = {
    ".note/finance/WORK_PROGRESS.md",
    ".note/finance/QUESTION_AND_ANALYSIS_LOG.md",
}

INDEX_DOCS = {
    ".note/finance/docs/INDEX.md",
    ".note/finance/reports/backtests/INDEX.md",
}

REGISTRY_DOCS = {
    ".note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl",
    ".note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl",
    ".note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl",
    ".note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl",
    ".note/finance/registries/EXPERIMENT_REGISTRY.jsonl",
}


def _git_status() -> list[dict[str, str]]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    rows: list[dict[str, str]] = []
    for raw in proc.stdout.splitlines():
        if not raw.strip():
            continue
        status = raw[:2]
        path_text = raw[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        rows.append({"status": status, "path": path_text})
    return rows


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _classify(paths: list[str]) -> dict[str, list[str]]:
    out = {
        "generated": [],
        "phase_docs": [],
        "strategy_hubs": [],
        "backtest_logs": [],
        "one_pagers": [],
        "root_logs": [],
        "indexes": [],
        "registries": [],
        "other_docs": [],
        "other_files": [],
    }
    for path in paths:
        if _matches_any(path, GENERATED_PATTERNS):
            out["generated"].append(path)
        elif path in ROOT_LOGS:
            out["root_logs"].append(path)
        elif path in INDEX_DOCS:
            out["indexes"].append(path)
        elif path in REGISTRY_DOCS:
            out["registries"].append(path)
        elif path.startswith(".note/finance/phases/active/phase") and path.endswith(".md"):
            out["phase_docs"].append(path)
        elif path.startswith(".note/finance/reports/backtests/strategies/") and path.endswith("_BACKTEST_LOG.md"):
            out["backtest_logs"].append(path)
        elif path.startswith(".note/finance/reports/backtests/strategies/") and path.endswith(".md"):
            name = Path(path).name
            if name in {
                "VALUE_STRICT_ANNUAL.md",
                "QUALITY_STRICT_ANNUAL.md",
                "QUALITY_VALUE_STRICT_ANNUAL.md",
                "GTAA.md",
            }:
                out["strategy_hubs"].append(path)
            elif name == "CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md":
                out["other_docs"].append(path)
            else:
                out["one_pagers"].append(path)
        elif path.endswith(".md"):
            out["other_docs"].append(path)
        else:
            out["other_files"].append(path)
    return out


def _family_token(path: str) -> str | None:
    name = Path(path).name
    if name.startswith("VALUE_STRICT_ANNUAL"):
        return "value"
    if name.startswith("QUALITY_STRICT_ANNUAL"):
        return "quality"
    if name.startswith("QUALITY_VALUE_STRICT_ANNUAL"):
        return "quality_value"
    if name.startswith("GTAA"):
        return "gtaa"
    return None


def _build_checks(groups: dict[str, list[str]]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    phase_docs = groups["phase_docs"]
    strategy_hubs = groups["strategy_hubs"]
    backtest_logs = groups["backtest_logs"]
    one_pagers = groups["one_pagers"]
    root_logs = groups["root_logs"]
    generated = groups["generated"]
    other_docs = groups["other_docs"]
    indexes = groups["indexes"]
    registries = groups["registries"]

    if phase_docs:
        has_todo = any("CURRENT_CHAPTER_TODO" in path for path in phase_docs)
        checks.append(
            {
                "name": "active phase TODO synced",
                "ok": "yes" if has_todo else "no",
                "detail": "phase docs changed and CURRENT_CHAPTER_TODO is present" if has_todo else "phase docs changed but CURRENT_CHAPTER_TODO was not touched",
            }
        )

    changed_strategy_families = {
        token
        for path in strategy_hubs + one_pagers + backtest_logs
        if (token := _family_token(path)) is not None
    }
    logged_strategy_families = {
        token for path in backtest_logs if (token := _family_token(path)) is not None
    }
    missing_log_families = sorted(changed_strategy_families - logged_strategy_families)
    if changed_strategy_families:
        checks.append(
            {
                "name": "strategy backtest logs synced",
                "ok": "yes" if not missing_log_families else "no",
                "detail": "all changed strategy families touched their backtest log"
                if not missing_log_families
                else f"missing backtest log update for: {', '.join(missing_log_families)}",
            }
        )

    if phase_docs or strategy_hubs or one_pagers or other_docs:
        checks.append(
            {
                "name": "root concise logs reviewed",
                "ok": "yes" if root_logs else "no",
                "detail": "WORK_PROGRESS or QUESTION_AND_ANALYSIS_LOG touched"
                if root_logs
                else "durable docs changed but root concise logs were not touched",
            }
        )

    if one_pagers or any("CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md" in path for path in other_docs):
        touched_summary = any("CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md" in path for path in other_docs)
        checks.append(
            {
                "name": "current candidate summary reviewed",
                "ok": "yes" if touched_summary else "no",
                "detail": "summary updated" if touched_summary else "candidate docs changed but CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md was not touched",
            }
        )

    if changed_strategy_families or any("CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md" in path for path in other_docs):
        has_candidate_registry = ".note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl" in registries
        checks.append(
            {
                "name": "current candidate registry reviewed",
                "ok": "yes" if has_candidate_registry else "no",
                "detail": "machine-readable current candidate registry touched"
                if has_candidate_registry
                else "candidate-facing docs changed but CURRENT_CANDIDATE_REGISTRY.jsonl was not touched",
            }
        )

    if phase_docs or strategy_hubs or one_pagers:
        checks.append(
            {
                "name": "index docs reviewed",
                "ok": "yes" if indexes else "no",
                "detail": "docs/INDEX or reports/backtests/INDEX touched"
                if indexes
                else "durable docs changed but index docs were not touched",
            }
        )

    checks.append(
        {
            "name": "generated artifacts remain unstaged",
            "ok": "yes" if generated else "n/a",
            "detail": "generated artifacts are present and should usually stay uncommitted"
            if generated
            else "no generated artifacts detected in git status",
        }
    )

    return checks


def _render_text(status_rows: list[dict[str, str]], groups: dict[str, list[str]], checks: list[dict[str, str]]) -> str:
    lines: list[str] = []
    lines.append("Finance Refinement Hygiene Check")
    lines.append(f"repo: {REPO_ROOT}")
    lines.append(f"changed paths: {len(status_rows)}")
    lines.append("")

    order = [
        ("phase_docs", "Phase docs"),
        ("strategy_hubs", "Strategy hubs"),
        ("one_pagers", "One-pagers"),
        ("backtest_logs", "Backtest logs"),
        ("root_logs", "Root concise logs"),
        ("indexes", "Index docs"),
        ("registries", "Registries"),
        ("other_docs", "Other docs"),
        ("generated", "Generated artifacts"),
        ("other_files", "Other files"),
    ]
    for key, title in order:
        values = groups[key]
        lines.append(f"{title}: {len(values)}")
        for value in values[:12]:
            lines.append(f"  - {value}")
        if len(values) > 12:
            lines.append(f"  - ... (+{len(values) - 12} more)")
        lines.append("")

    lines.append("Checklist:")
    for check in checks:
        marker = "[x]" if check["ok"] == "yes" else "[ ]" if check["ok"] == "no" else "[-]"
        lines.append(f"{marker} {check['name']}: {check['detail']}")
    lines.append("")

    warnings = [check for check in checks if check["ok"] == "no"]
    if warnings:
        lines.append("Recommended next actions:")
        for check in warnings:
            lines.append(f"  - {check['name']}")
    else:
        lines.append("No missing checklist items detected from the current git diff.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check finance backtest-refinement document and artifact hygiene.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of text.")
    args = parser.parse_args()

    status_rows = _git_status()
    paths = [row["path"] for row in status_rows]
    groups = _classify(paths)
    checks = _build_checks(groups)

    payload = {
        "repo_root": str(REPO_ROOT),
        "changed_count": len(status_rows),
        "groups": groups,
        "checks": checks,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(_render_text(status_rows, groups, checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
