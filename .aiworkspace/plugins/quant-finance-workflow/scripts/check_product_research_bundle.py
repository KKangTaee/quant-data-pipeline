#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# scripts live under .aiworkspace/plugins/quant-finance-workflow/scripts.
REPO_ROOT = Path(__file__).resolve().parents[4]
FINANCE_NOTE_DIR = REPO_ROOT / ".aiworkspace" / "note" / "finance"
RESEARCHES_DIR = FINANCE_NOTE_DIR / "researches"
ACTIVE_RESEARCH_DIR = RESEARCHES_DIR / "active"
README_PATH = RESEARCHES_DIR / "README.md"

REQUIRED_FILES = [
    "RESEARCH_PLAN.md",
    "CURRENT_PROJECT_AUDIT.md",
    "BENCHMARKS.md",
    "UI_PATTERNS.md",
    "FEATURE_CANDIDATES.md",
    "RECOMMENDATION.md",
    "SOURCES.md",
    "RISKS.md",
]

SECTION_HINTS = {
    "RESEARCH_PLAN.md": ["Scope", "Method", "Outputs"],
    "CURRENT_PROJECT_AUDIT.md": ["Snapshot", "Weaknesses"],
    "BENCHMARKS.md": ["Benchmarks"],
    "UI_PATTERNS.md": ["Pattern"],
    "FEATURE_CANDIDATES.md": ["Feature", "Priority"],
    "RECOMMENDATION.md": ["One-Line Recommendation", "Final Recommendation"],
    "SOURCES.md": ["Access date"],
    "RISKS.md": ["Risks"],
}

EVIDENCE_LABELS = {"Observed", "Documented", "Claimed", "Inferred", "Unknown"}


@dataclass
class BundleCheck:
    research_id: str
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _active_bundle_dirs() -> list[Path]:
    if not ACTIVE_RESEARCH_DIR.exists():
        return []
    return sorted(path for path in ACTIVE_RESEARCH_DIR.iterdir() if path.is_dir())


def _resolve_bundle(research_id: str) -> Path:
    return ACTIVE_RESEARCH_DIR / research_id


def _contains_evidence_label(text: str) -> bool:
    return any(re.search(rf"\b{re.escape(label)}\b", text) for label in EVIDENCE_LABELS)


def _check_sections(check: BundleCheck, bundle_dir: Path, filename: str, text: str) -> None:
    for hint in SECTION_HINTS.get(filename, []):
        if hint not in text:
            check.warnings.append(f"{filename}: expected section/content hint missing: {hint}")

    if filename == "SOURCES.md":
        if not re.search(r"Access date:\s*\d{4}-\d{2}-\d{2}", text):
            check.errors.append("SOURCES.md: missing 'Access date: YYYY-MM-DD'")
        if not _contains_evidence_label(text):
            check.warnings.append("SOURCES.md: no standard evidence labels detected")

    if filename == "BENCHMARKS.md" and not _contains_evidence_label(text):
        check.warnings.append("BENCHMARKS.md: no standard evidence labels detected")

    if filename == "FEATURE_CANDIDATES.md" and "Parking" not in text:
        check.warnings.append("FEATURE_CANDIDATES.md: parking-lot section not detected")

    if filename == "RECOMMENDATION.md":
        lower = text.lower()
        if "not to do" not in lower and "avoid" not in lower and "하지" not in text:
            check.warnings.append("RECOMMENDATION.md: no explicit deferred/avoid scope detected")

    if "TBD" in text:
        check.warnings.append(f"{filename}: contains TBD placeholders")


def _check_readme_listing(check: BundleCheck) -> None:
    if not README_PATH.exists():
        check.warnings.append("researches/README.md is missing")
        return
    readme = _read(README_PATH)
    needle = f"active/{check.research_id}/"
    if needle not in readme:
        check.warnings.append(f"researches/README.md does not list `{needle}`")


def check_bundle(bundle_dir: Path) -> BundleCheck:
    check = BundleCheck(research_id=bundle_dir.name, path=str(bundle_dir.relative_to(REPO_ROOT)))

    if not bundle_dir.exists():
        check.errors.append(f"bundle directory not found: {bundle_dir}")
        return check
    if not bundle_dir.is_dir():
        check.errors.append(f"bundle path is not a directory: {bundle_dir}")
        return check

    for filename in REQUIRED_FILES:
        path = bundle_dir / filename
        if not path.exists():
            check.errors.append(f"missing required file: {filename}")
            continue
        text = _read(path)
        if not text.strip():
            check.errors.append(f"empty required file: {filename}")
            continue
        _check_sections(check, bundle_dir, filename, text)

    extra_md = sorted(
        path.name
        for path in bundle_dir.glob("*.md")
        if path.name not in REQUIRED_FILES
    )
    if extra_md:
        check.warnings.append(f"extra markdown files found: {', '.join(extra_md)}")

    _check_readme_listing(check)
    return check


def _render_text(results: list[BundleCheck], *, strict: bool) -> str:
    lines: list[str] = []
    lines.append("Finance Product Research Bundle Check")
    lines.append(f"repo: {REPO_ROOT}")
    lines.append(f"strict: {str(strict).lower()}")
    lines.append("")

    for result in results:
        marker = "PASS" if result.ok and (not strict or not result.warnings) else "WARN" if result.ok else "FAIL"
        lines.append(f"[{marker}] {result.research_id}")
        lines.append(f"  path: {result.path}")
        for error in result.errors:
            lines.append(f"  error: {error}")
        for warning in result.warnings:
            lines.append(f"  warning: {warning}")
        if not result.errors and not result.warnings:
            lines.append("  no issues detected")
        lines.append("")

    failed = [result for result in results if result.errors or (strict and result.warnings)]
    if failed:
        lines.append("Result: attention needed")
    else:
        lines.append("Result: all checked bundles satisfy the enforced contract")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check finance product research bundle structure.")
    parser.add_argument("--research-id", help="Check one active research bundle by folder name.")
    parser.add_argument("--all-active", action="store_true", help="Check every active research bundle.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    if args.research_id and args.all_active:
        parser.error("use either --research-id or --all-active, not both")

    if args.research_id:
        bundle_dirs = [_resolve_bundle(args.research_id)]
    else:
        bundle_dirs = _active_bundle_dirs()

    results = [check_bundle(path) for path in bundle_dirs]
    payload = {
        "repo_root": str(REPO_ROOT),
        "strict": args.strict,
        "checked_count": len(results),
        "results": [
            {
                "research_id": result.research_id,
                "path": result.path,
                "ok": result.ok,
                "errors": result.errors,
                "warnings": result.warnings,
            }
            for result in results
        ],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(_render_text(results, strict=args.strict))

    failed = [result for result in results if result.errors or (args.strict and result.warnings)]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
