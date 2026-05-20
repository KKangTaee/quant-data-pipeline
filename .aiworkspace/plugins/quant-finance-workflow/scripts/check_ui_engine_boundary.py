#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


# scripts live under .aiworkspace/plugins/quant-finance-workflow/scripts.
REPO_ROOT = Path(__file__).resolve().parents[4]
SERVICE_DIR = REPO_ROOT / "app" / "services"
RUNTIME_DIR = REPO_ROOT / "app" / "runtime"
BOUNDARY_DIRS = [SERVICE_DIR, RUNTIME_DIR]

STREAMLIT_IMPORT_RE = re.compile(r"^\s*(?:import\s+streamlit\b|from\s+streamlit\s+import\b)")
STREAMLIT_ACCESS_RE = re.compile(r"(?<![A-Za-z0-9_])st\.")
APP_WEB_IMPORT_RE = re.compile(r"^\s*(?:from\s+app\.web\b|import\s+app\.web\b)")

FORBIDDEN_STAGED_PATTERNS = [
    ".aiworkspace/note/finance/registries/*.jsonl",
    ".aiworkspace/note/finance/saved/*.jsonl",
    ".aiworkspace/note/finance/run_history/*.jsonl",
    ".aiworkspace/note/finance/run_artifacts/*",
    ".aiworkspace/note/finance/backtest_artifacts/*",
    ".playwright-mcp/*",
    "*.DS_Store",
    "_tmp_*.csv",
    "csv/*daily_market_update_failures.csv",
]


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _boundary_files() -> list[Path]:
    files: list[Path] = []
    for directory in BOUNDARY_DIRS:
        if directory.exists():
            files.extend(path for path in directory.glob("*.py") if path.is_file())
    return sorted(files)


def _scan_boundary_files() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    violations: list[dict[str, Any]] = []
    advisories: list[dict[str, Any]] = []
    for path in _boundary_files():
        rel_path = _relative(path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if STREAMLIT_IMPORT_RE.search(line):
                violations.append(
                    {
                        "kind": "streamlit_import",
                        "path": rel_path,
                        "line": lineno,
                        "detail": line.strip(),
                    }
                )
            if STREAMLIT_ACCESS_RE.search(line):
                violations.append(
                    {
                        "kind": "streamlit_access",
                        "path": rel_path,
                        "line": lineno,
                        "detail": line.strip(),
                    }
                )
            if APP_WEB_IMPORT_RE.search(line):
                advisories.append(
                    {
                        "kind": "transitional_app_web_import",
                        "path": rel_path,
                        "line": lineno,
                        "detail": line.strip(),
                    }
                )
    return violations, advisories


def _git_staged_paths() -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _staged_artifact_violations() -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for path in _git_staged_paths():
        if _matches_any(path, FORBIDDEN_STAGED_PATTERNS):
            violations.append(
                {
                    "kind": "forbidden_staged_artifact",
                    "path": path,
                    "line": None,
                    "detail": "generated, registry, saved, run-history, or local artifact is staged",
                }
            )
    return violations


def _build_report() -> dict[str, Any]:
    boundary_violations, boundary_advisories = _scan_boundary_files()
    staged_violations = _staged_artifact_violations()
    violations = boundary_violations + staged_violations
    return {
        "repo": str(REPO_ROOT),
        "boundary_files": [_relative(path) for path in _boundary_files()],
        "service_files": [
            _relative(path)
            for path in _boundary_files()
            if path.is_relative_to(SERVICE_DIR)
        ],
        "runtime_files": [
            _relative(path)
            for path in _boundary_files()
            if path.is_relative_to(RUNTIME_DIR)
        ],
        "staged_paths": _git_staged_paths(),
        "violations": violations,
        "advisories": boundary_advisories,
        "ok": not violations,
    }


def _render_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("UI / Engine Boundary Check")
    lines.append(f"repo: {report['repo']}")
    lines.append(f"boundary files: {len(report['boundary_files'])}")
    lines.append(f"service files: {len(report['service_files'])}")
    lines.append(f"runtime files: {len(report['runtime_files'])}")
    lines.append(f"staged paths: {len(report['staged_paths'])}")
    lines.append("")

    violations = list(report["violations"])
    if violations:
        lines.append("Hard violations:")
        for item in violations:
            location = item["path"]
            if item.get("line"):
                location = f"{location}:{item['line']}"
            lines.append(f"  [fail] {item['kind']} {location} - {item['detail']}")
    else:
        lines.append("Hard violations: none")
    lines.append("")

    advisories = list(report["advisories"])
    if advisories:
        lines.append("Advisories:")
        for item in advisories:
            lines.append(
                f"  [warn] {item['kind']} {item['path']}:{item['line']} - {item['detail']}"
            )
        lines.append("")
        lines.append(
            "Note: app.services/app.runtime -> app.web imports are advisory during the current "
            "transition. They should trend down as Streamlit-free helpers move out of app.web."
        )
    else:
        lines.append("Advisories: none")
    lines.append("")
    lines.append("Result: PASS" if report["ok"] else "Result: FAIL")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check UI/engine boundary hygiene for finance service/runtime modules.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON report.")
    args = parser.parse_args(argv)

    report = _build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_render_text(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
