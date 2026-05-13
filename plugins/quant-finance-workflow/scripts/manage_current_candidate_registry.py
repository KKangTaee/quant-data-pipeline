#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[3]
FINANCE_NOTE_DIR = REPO_ROOT / ".note" / "finance"
REGISTRIES_DIR = FINANCE_NOTE_DIR / "registries"
REGISTRY_FILE = REGISTRIES_DIR / "CURRENT_CANDIDATE_REGISTRY.jsonl"
SCHEMA_VERSION = 1


def _iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_rows() -> list[dict[str, Any]]:
    if not REGISTRY_FILE.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in REGISTRY_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _append_row(row: dict[str, Any]) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REGISTRY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _seed_rows() -> list[dict[str, Any]]:
    recorded_at = _iso_now()
    common = {
        "schema_version": SCHEMA_VERSION,
        "recorded_at": recorded_at,
        "status": "active",
        "source_kind": "manual_seed_from_current_practical_candidates_summary",
    }
    return [
        {
            **common,
            "registry_id": "value_current_anchor_top14_psr",
            "revision_id": f"rev_{uuid4().hex[:12]}",
            "record_type": "current_candidate",
            "strategy_family": "value",
            "strategy_name": "Value Snapshot (Strict Annual)",
            "candidate_role": "current_anchor",
            "title": "Value current anchor",
            "source_ref": "CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
            "period": {"start": None, "end": None},
            "contract": {
                "top_n": 14,
                "factor_adjustment": "psr",
            },
            "result": {
                "cagr": 28.13,
                "mdd": -24.55,
                "promotion": "real_money_candidate",
                "shortlist": "paper_probation",
                "deployment": "review_required",
            },
            "docs": {
                "summary": ".note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
                "strategy_hub": ".note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md",
                "one_pager": ".note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md",
                "backtest_log": ".note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md",
            },
            "notes": "Current practical anchor for Value strict annual family.",
        },
        {
            **common,
            "registry_id": "value_lower_mdd_near_miss_pfcr",
            "revision_id": f"rev_{uuid4().hex[:12]}",
            "record_type": "near_miss",
            "strategy_family": "value",
            "strategy_name": "Value Snapshot (Strict Annual)",
            "candidate_role": "lower_mdd_weaker_gate",
            "title": "Value lower-MDD near miss",
            "source_ref": "CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
            "period": {"start": None, "end": None},
            "contract": {
                "top_n": 14,
                "factor_adjustment": "psr + pfcr",
            },
            "result": {
                "cagr": 27.22,
                "mdd": -21.16,
                "promotion": "production_candidate",
                "shortlist": "watchlist",
                "deployment": "review_required",
            },
            "docs": {
                "summary": ".note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
                "strategy_hub": ".note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md",
                "one_pager": ".note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md",
                "backtest_log": ".note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md",
            },
            "notes": "Lower-MDD near miss for Value that loses one gate tier.",
        },
        {
            **common,
            "registry_id": "quality_current_anchor_top12_lqd",
            "revision_id": f"rev_{uuid4().hex[:12]}",
            "record_type": "current_candidate",
            "strategy_family": "quality",
            "strategy_name": "Quality Snapshot (Strict Annual)",
            "candidate_role": "current_anchor",
            "title": "Quality current anchor",
            "source_ref": "CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
            "period": {"start": None, "end": None},
            "contract": {
                "top_n": 12,
                "benchmark_ticker": "LQD",
                "trend_filter_enabled": True,
                "market_regime_enabled": False,
                "factor_adjustment": "capital_discipline",
            },
            "result": {
                "cagr": 26.02,
                "mdd": -25.57,
                "promotion": "real_money_candidate",
                "shortlist": "paper_probation",
                "deployment": "review_required",
            },
            "docs": {
                "summary": ".note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
                "strategy_hub": ".note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md",
                "one_pager": ".note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md",
                "backtest_log": ".note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md",
            },
            "notes": "Current practical anchor for Quality strict annual family.",
        },
        {
            **common,
            "registry_id": "quality_cleaner_alternative_top12_spy",
            "revision_id": f"rev_{uuid4().hex[:12]}",
            "record_type": "scenario",
            "strategy_family": "quality",
            "strategy_name": "Quality Snapshot (Strict Annual)",
            "candidate_role": "cleaner_alternative",
            "title": "Quality cleaner alternative",
            "source_ref": "CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
            "period": {"start": None, "end": None},
            "contract": {
                "top_n": 12,
                "benchmark_ticker": "SPY",
                "trend_filter_enabled": True,
                "market_regime_enabled": False,
            },
            "result": {
                "cagr": 25.18,
                "mdd": -25.57,
                "promotion": "real_money_candidate",
                "shortlist": "paper_probation",
                "deployment": "paper_only",
            },
            "docs": {
                "summary": ".note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
                "strategy_hub": ".note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md",
                "backtest_log": ".note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md",
            },
            "notes": "Cleaner benchmark alternative for Quality family.",
        },
        {
            **common,
            "registry_id": "quality_value_current_anchor_top10_por",
            "revision_id": f"rev_{uuid4().hex[:12]}",
            "record_type": "current_candidate",
            "strategy_family": "quality_value",
            "strategy_name": "Quality + Value Snapshot (Strict Annual)",
            "candidate_role": "current_anchor",
            "title": "Quality + Value strongest practical point",
            "source_ref": "CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
            "period": {"start": None, "end": None},
            "contract": {
                "top_n": 10,
                "benchmark_contract": "Candidate Universe Equal-Weight",
                "quality_adjustment": "operating_margin",
                "value_adjustment": "pcr + por + per",
            },
            "result": {
                "cagr": 31.82,
                "mdd": -26.63,
                "promotion": "real_money_candidate",
                "shortlist": "small_capital_trial",
                "deployment": "review_required",
            },
            "docs": {
                "summary": ".note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
                "strategy_hub": ".note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md",
                "one_pager": ".note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md",
                "backtest_log": ".note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md",
            },
            "notes": "Current strongest practical point for blended strict annual family.",
        },
        {
            **common,
            "registry_id": "quality_value_lower_mdd_near_miss_top9",
            "revision_id": f"rev_{uuid4().hex[:12]}",
            "record_type": "near_miss",
            "strategy_family": "quality_value",
            "strategy_name": "Quality + Value Snapshot (Strict Annual)",
            "candidate_role": "lower_mdd_weaker_gate",
            "title": "Quality + Value lower-MDD near miss",
            "source_ref": "CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
            "period": {"start": None, "end": None},
            "contract": {
                "top_n": 9,
                "benchmark_contract": "Candidate Universe Equal-Weight",
            },
            "result": {
                "cagr": 31.08,
                "mdd": -25.61,
                "promotion": "production_candidate",
                "shortlist": "watchlist",
                "deployment": "review_required",
            },
            "docs": {
                "summary": ".note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md",
                "strategy_hub": ".note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md",
                "one_pager": ".note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md",
                "backtest_log": ".note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md",
            },
            "notes": "Lower-MDD near miss for Quality + Value that drops one gate tier.",
        },
    ]


def _latest_by_registry_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("registry_id") or "").strip()
        if not key:
            continue
        previous = latest.get(key)
        if previous is None or str(row.get("recorded_at") or "") >= str(previous.get("recorded_at") or ""):
            latest[key] = row
    return latest


def _validate_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required = [
        "registry_id",
        "recorded_at",
        "record_type",
        "strategy_family",
        "strategy_name",
        "candidate_role",
        "status",
        "result",
    ]
    for key in required:
        if key not in row or row.get(key) in (None, ""):
            issues.append(f"missing `{key}`")
    result = row.get("result") or {}
    for key in ["cagr", "mdd", "promotion", "shortlist", "deployment"]:
        if key not in result:
            issues.append(f"missing result.`{key}`")
    docs = row.get("docs") or {}
    for path in docs.values():
        if path and not (REPO_ROOT / str(path)).exists():
            issues.append(f"missing doc path `{path}`")
    return issues


def _cmd_seed(args: argparse.Namespace) -> int:
    existing = _load_rows()
    if existing and not args.force:
        raise SystemExit("Registry already contains rows. Use --force to append a fresh seed snapshot.")
    for row in _seed_rows():
        _append_row(row)
    print(f"seeded {len(_seed_rows())} rows into {REGISTRY_FILE}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    latest_rows = list(_latest_by_registry_id(_load_rows()).values())
    if args.family:
        latest_rows = [row for row in latest_rows if row.get("strategy_family") == args.family]
    latest_rows = sorted(latest_rows, key=lambda row: (str(row.get("strategy_family")), str(row.get("title"))))
    for row in latest_rows:
        result = row.get("result") or {}
        print(
            f"{row.get('registry_id')}: "
            f"{row.get('strategy_family')} / {row.get('candidate_role')} / "
            f"CAGR {result.get('cagr')} / MDD {result.get('mdd')} / "
            f"{result.get('promotion')} / {result.get('shortlist')}"
        )
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    latest = _latest_by_registry_id(_load_rows())
    row = latest.get(args.registry_id)
    if row is None:
        raise SystemExit(f"Unknown registry_id: {args.registry_id}")
    print(json.dumps(row, ensure_ascii=False, indent=2))
    return 0


def _cmd_append(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("recorded_at", _iso_now())
    payload.setdefault("revision_id", f"rev_{uuid4().hex[:12]}")
    issues = _validate_row(payload)
    if issues:
        raise SystemExit("Invalid registry payload:\n- " + "\n- ".join(issues))
    _append_row(payload)
    print(f"appended {payload['registry_id']} to {REGISTRY_FILE}")
    return 0


def _cmd_validate(_: argparse.Namespace) -> int:
    rows = _load_rows()
    if not rows:
        print("registry is empty")
        return 0
    had_issue = False
    for row in rows:
        issues = _validate_row(row)
        if issues:
            had_issue = True
            print(f"{row.get('registry_id') or '[missing id]'}:")
            for issue in issues:
                print(f"  - {issue}")
    if not had_issue:
        print(f"validated {len(rows)} registry row(s) with no missing required fields")
    return 1 if had_issue else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the machine-readable current candidate registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed-current-practical", help="Append a first-pass seed snapshot of the current practical candidates.")
    seed_parser.add_argument("--force", action="store_true", help="Allow seeding even if the registry already has rows.")
    seed_parser.set_defaults(func=_cmd_seed)

    list_parser = subparsers.add_parser("list", help="List the latest active view of the registry.")
    list_parser.add_argument("--family", choices=["value", "quality", "quality_value"], help="Filter by strategy family.")
    list_parser.set_defaults(func=_cmd_list)

    show_parser = subparsers.add_parser("show", help="Show the latest record for one registry id.")
    show_parser.add_argument("registry_id")
    show_parser.set_defaults(func=_cmd_show)

    append_parser = subparsers.add_parser("append", help="Append one registry row from a JSON file.")
    append_parser.add_argument("--json-file", required=True)
    append_parser.set_defaults(func=_cmd_append)

    validate_parser = subparsers.add_parser("validate", help="Validate registry rows and referenced docs.")
    validate_parser.set_defaults(func=_cmd_validate)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
