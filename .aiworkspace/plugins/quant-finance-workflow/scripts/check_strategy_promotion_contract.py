#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_SECTION_HEADINGS = [
    "Metadata",
    "Handoff Summary",
    "Strategy Identity",
    "Universe And Membership Contract",
    "Data And PIT Contract",
    "Parameter And Optimization Contract",
    "IS OOS And Walk Forward Evidence",
    "Cost Slippage Turnover And Liquidity",
    "Benchmark And Comparator Policy",
    "Replay Contract",
    "Generated Artifacts And Storage Boundary",
    "Known Failures And Evidence State",
    "Practical Validation Source Payload Conditions",
    "Final Review Selected Route Blockers",
    "Portfolio Monitoring Review Triggers",
    "Promotion Review Decision",
    "Verification",
]

REQUIRED_STATE_TOKENS = [
    "PROMOTE_READY",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "NOT_RUN",
]

HEADING_RE = re.compile(r"^\s*##\s+(.+?)\s*$")


def _normalize_heading(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip().rstrip("#").strip())


def extract_section_headings(markdown_text: str) -> list[str]:
    headings: list[str] = []
    for line in markdown_text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            headings.append(_normalize_heading(match.group(1)))
    return headings


def build_report(contract_path: str | Path) -> dict[str, Any]:
    path = Path(contract_path)
    text = path.read_text(encoding="utf-8")
    headings = extract_section_headings(text)
    heading_set = set(headings)
    missing_required_sections = [
        heading for heading in REQUIRED_SECTION_HEADINGS if heading not in heading_set
    ]
    missing_state_tokens = [token for token in REQUIRED_STATE_TOKENS if token not in text]

    return {
        "path": str(path),
        "required_sections": REQUIRED_SECTION_HEADINGS,
        "found_sections": headings,
        "missing_required_sections": missing_required_sections,
        "required_state_tokens": REQUIRED_STATE_TOKENS,
        "missing_state_tokens": missing_state_tokens,
        "ok": not missing_required_sections and not missing_state_tokens,
    }


def _render_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("Strategy Promotion Contract Check")
    lines.append(f"path: {report['path']}")
    lines.append(f"required sections: {len(report['required_sections'])}")
    lines.append(f"found sections: {len(report['found_sections'])}")
    lines.append("")

    missing_sections = report["missing_required_sections"]
    if missing_sections:
        lines.append("Missing required sections:")
        for heading in missing_sections:
            lines.append(f"  [fail] {heading}")
    else:
        lines.append("Missing required sections: none")
    lines.append("")

    missing_tokens = report["missing_state_tokens"]
    if missing_tokens:
        lines.append("Missing decision state tokens:")
        for token in missing_tokens:
            lines.append(f"  [fail] {token}")
    else:
        lines.append("Missing decision state tokens: none")
    lines.append("")

    lines.append(
        "Scope: structure check only; this does not approve strategy performance or rewrite registries."
    )
    lines.append("Result: PASS" if report["ok"] else "Result: FAIL")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check required sections for a Strategy Promotion Contract markdown file.",
    )
    parser.add_argument("contract_path", help="Path to a strategy promotion contract markdown file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON report.")
    args = parser.parse_args(argv)

    report = build_report(args.contract_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_render_text(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
