#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4


# scripts live under .aiworkspace/plugins/quant-finance-workflow/scripts.
REPO_ROOT = Path(__file__).resolve().parents[4]
FINANCE_NOTE_DIR = REPO_ROOT / ".aiworkspace" / "note" / "finance"
REGISTRIES_DIR = FINANCE_NOTE_DIR / "registries"
REGISTRY_FILE = REGISTRIES_DIR / "PRE_LIVE_CANDIDATE_REGISTRY.jsonl"
CURRENT_CANDIDATE_REGISTRY_FILE = REGISTRIES_DIR / "CURRENT_CANDIDATE_REGISTRY.jsonl"
SCHEMA_VERSION = 1

VALID_RECORD_STATUSES = {"active", "superseded", "archived"}
VALID_SOURCE_KINDS = {
    "current_candidate_registry",
    "backtest_run",
    "saved_portfolio",
    "backtest_report",
    "manual_review",
}
VALID_PRE_LIVE_STATUSES = {"watchlist", "paper_tracking", "hold", "reject", "re_review"}


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
            rows.append({"_decode_error": line[:120]})
    return rows


def _load_current_candidate_rows() -> list[dict[str, Any]]:
    if not CURRENT_CANDIDATE_REGISTRY_FILE.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in CURRENT_CANDIDATE_REGISTRY_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
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


def _latest_by_pre_live_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("pre_live_id") or "").strip()
        if not key:
            continue
        previous = latest.get(key)
        if previous is None or str(row.get("recorded_at") or "") >= str(previous.get("recorded_at") or ""):
            latest[key] = row
    return latest


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


def _is_iso_date(value: Any) -> bool:
    if value in (None, ""):
        return False
    try:
        date.fromisoformat(str(value))
    except ValueError:
        return False
    return True


def _validate_doc_paths(row: dict[str, Any], issues: list[str]) -> None:
    docs = row.get("docs") or {}
    if not isinstance(docs, dict):
        issues.append("docs must be an object when present")
        return
    for key, path in docs.items():
        if not path:
            continue
        if not (REPO_ROOT / str(path)).exists():
            issues.append(f"missing docs.`{key}` path `{path}`")


def _validate_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if "_decode_error" in row:
        return [f"invalid JSON line starts with `{row['_decode_error']}`"]

    required = [
        "pre_live_id",
        "recorded_at",
        "record_status",
        "source_kind",
        "title",
        "strategy_or_bundle",
        "result_snapshot",
        "real_money_signal",
        "pre_live_status",
        "operator_reason",
        "next_action",
    ]
    for key in required:
        if key not in row or row.get(key) in (None, ""):
            issues.append(f"missing `{key}`")

    if row.get("schema_version") != SCHEMA_VERSION:
        issues.append(f"schema_version must be {SCHEMA_VERSION}")

    if row.get("record_status") not in VALID_RECORD_STATUSES:
        issues.append(f"record_status must be one of {sorted(VALID_RECORD_STATUSES)}")
    if row.get("source_kind") not in VALID_SOURCE_KINDS:
        issues.append(f"source_kind must be one of {sorted(VALID_SOURCE_KINDS)}")
    if row.get("pre_live_status") not in VALID_PRE_LIVE_STATUSES:
        issues.append(f"pre_live_status must be one of {sorted(VALID_PRE_LIVE_STATUSES)}")

    strategy_or_bundle = row.get("strategy_or_bundle")
    if not isinstance(strategy_or_bundle, dict):
        issues.append("strategy_or_bundle must be an object")
    else:
        for key in ["kind", "name"]:
            if not strategy_or_bundle.get(key):
                issues.append(f"missing strategy_or_bundle.`{key}`")

    result_snapshot = row.get("result_snapshot")
    if not isinstance(result_snapshot, dict):
        issues.append("result_snapshot must be an object")
    else:
        for key in ["cagr", "mdd"]:
            if key not in result_snapshot:
                issues.append(f"missing result_snapshot.`{key}`")

    real_money_signal = row.get("real_money_signal")
    if not isinstance(real_money_signal, dict):
        issues.append("real_money_signal must be an object")
    else:
        for key in ["promotion", "shortlist", "deployment"]:
            if key not in real_money_signal:
                issues.append(f"missing real_money_signal.`{key}`")
        blockers = real_money_signal.get("blockers", [])
        if blockers is not None and not isinstance(blockers, list):
            issues.append("real_money_signal.`blockers` must be a list")

    if row.get("pre_live_status") == "re_review" and not _is_iso_date(row.get("review_date")):
        issues.append("review_date must be YYYY-MM-DD when pre_live_status is re_review")

    if row.get("pre_live_status") == "paper_tracking":
        tracking = row.get("tracking_plan") or {}
        if not isinstance(tracking, dict):
            issues.append("tracking_plan must be an object when present")
        elif not tracking.get("cadence"):
            issues.append("tracking_plan.`cadence` is recommended for paper_tracking records")

    _validate_doc_paths(row, issues)
    return issues


def _default_tracking_plan(pre_live_status: str) -> dict[str, str | None]:
    if pre_live_status == "paper_tracking":
        return {
            "cadence": "monthly",
            "stop_condition": "Real-Money blocker가 새로 생기거나 drawdown / benchmark gap이 크게 악화되면 중단한다.",
            "success_condition": "정해진 관찰 기간 동안 핵심 Real-Money blocker 없이 후보 성격이 유지되면 재검토한다.",
        }
    if pre_live_status == "watchlist":
        return {
            "cadence": "next_strategy_review",
            "stop_condition": "동일 family에서 더 나은 후보가 나오거나 핵심 지표가 훼손되면 watchlist에서 내린다.",
            "success_condition": "다음 비교에서 여전히 후보 가치가 있으면 paper tracking 전환을 검토한다.",
        }
    if pre_live_status == "re_review":
        return {
            "cadence": "scheduled_review",
            "stop_condition": "재검토 시점에도 blocker가 유지되면 hold 또는 reject로 바꾼다.",
            "success_condition": "재검토 시점에 blocker가 해소되면 watchlist 또는 paper tracking으로 전환한다.",
        }
    return {
        "cadence": None,
        "stop_condition": None,
        "success_condition": None,
    }


def _recommended_pre_live_status(real_money_signal: dict[str, Any]) -> str:
    promotion = str(real_money_signal.get("promotion") or "").lower()
    shortlist = str(real_money_signal.get("shortlist") or "").lower()
    deployment = str(real_money_signal.get("deployment") or "").lower()
    blockers = real_money_signal.get("blockers") or []

    if any(term in promotion for term in ["reject", "fail"]) or any(term in deployment for term in ["reject", "blocked"]):
        return "reject"
    if blockers:
        return "hold"
    if shortlist in {"paper_probation", "small_capital_trial"} or deployment == "paper_only":
        return "paper_tracking"
    if shortlist == "watchlist":
        return "watchlist"
    if deployment == "review_required":
        return "watchlist"
    return "re_review"


def _default_operator_reason(row: dict[str, Any], status: str) -> str:
    result = row.get("result") or {}
    promotion = result.get("promotion") or "unknown"
    shortlist = result.get("shortlist") or "unknown"
    deployment = result.get("deployment") or "unknown"
    title = row.get("title") or row.get("registry_id") or "candidate"

    if status == "paper_tracking":
        return (
            f"{title}는 Real-Money 신호가 paper 관찰 후보에 가깝다 "
            f"(promotion={promotion}, shortlist={shortlist}, deployment={deployment}). "
            "아직 실전 투입이 아니라 실제 돈 없이 추적할 후보로 기록한다."
        )
    if status == "watchlist":
        return (
            f"{title}는 다시 볼 가치는 있지만 즉시 paper tracking으로 올리기 전 추가 비교가 필요하다 "
            f"(promotion={promotion}, shortlist={shortlist}, deployment={deployment})."
        )
    if status == "hold":
        return (
            f"{title}는 Real-Money blocker 또는 운영상 미확인 요소가 남아 있어 보류한다 "
            f"(promotion={promotion}, shortlist={shortlist}, deployment={deployment})."
        )
    if status == "reject":
        return (
            f"{title}는 현재 기준에서 Pre-Live 추적 대상으로 유지하기 어렵다 "
            f"(promotion={promotion}, shortlist={shortlist}, deployment={deployment})."
        )
    return (
        f"{title}는 지금 즉시 분류하기보다 정해진 시점에 다시 확인한다 "
        f"(promotion={promotion}, shortlist={shortlist}, deployment={deployment})."
    )


def _default_next_action(pre_live_status: str) -> str:
    if pre_live_status == "paper_tracking":
        return "실제 돈을 넣지 않고 월 1회 기준으로 성과, MDD, benchmark gap, Real-Money blocker 변화를 기록한다."
    if pre_live_status == "watchlist":
        return "다음 후보 비교 또는 데이터 업데이트 후 paper tracking 전환 여부를 다시 판단한다."
    if pre_live_status == "hold":
        return "보류 사유를 해소할 수 있는 데이터, 설정, 검증 조건을 먼저 확인한다."
    if pre_live_status == "reject":
        return "현재 기준에서는 추적을 종료하고, 같은 후보를 다시 쓰려면 새 근거가 생겼을 때 새 기록으로 검토한다."
    return "review_date에 후보 상태와 Real-Money 신호를 다시 확인한다."


def _build_pre_live_row_from_current_candidate(
    current_row: dict[str, Any],
    *,
    pre_live_status: str | None = None,
    pre_live_id: str | None = None,
    operator_reason: str | None = None,
    next_action: str | None = None,
    review_date: str | None = None,
) -> dict[str, Any]:
    result = current_row.get("result") or {}
    real_money_signal = {
        "promotion": result.get("promotion") or "unknown",
        "shortlist": result.get("shortlist") or "unknown",
        "deployment": result.get("deployment") or "unknown",
        "validation_status": result.get("validation_status") or "unknown",
        "liquidity_status": result.get("liquidity_status") or "unknown",
        "blockers": result.get("blockers") if isinstance(result.get("blockers"), list) else [],
    }
    status = pre_live_status or _recommended_pre_live_status(real_money_signal)
    if status == "re_review" and not review_date:
        review_date = (date.today() + timedelta(days=30)).isoformat()

    registry_id = str(current_row.get("registry_id") or "unknown_current_candidate")
    return {
        "schema_version": SCHEMA_VERSION,
        "pre_live_id": pre_live_id or f"pre_live_{registry_id}",
        "revision_id": f"rev_{uuid4().hex[:12]}",
        "recorded_at": _iso_now(),
        "record_status": "active",
        "source_kind": "current_candidate_registry",
        "source_ref": ".aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl",
        "source_candidate_registry_id": registry_id,
        "title": f"{current_row.get('title') or registry_id} - Pre-Live review",
        "strategy_or_bundle": {
            "kind": "single_strategy",
            "family": current_row.get("strategy_family"),
            "name": current_row.get("strategy_name"),
            "candidate_role": current_row.get("candidate_role"),
        },
        "settings_snapshot": {
            "period": current_row.get("period"),
            "contract": current_row.get("contract"),
            "source_ref": current_row.get("source_ref"),
        },
        "result_snapshot": {
            "cagr": result.get("cagr"),
            "mdd": result.get("mdd"),
            "sharpe": result.get("sharpe"),
            "end_balance": result.get("end_balance"),
        },
        "real_money_signal": real_money_signal,
        "pre_live_status": status,
        "operator_reason": operator_reason or _default_operator_reason(current_row, status),
        "next_action": next_action or _default_next_action(status),
        "review_date": review_date,
        "tracking_plan": _default_tracking_plan(status),
        "docs": current_row.get("docs") or {},
        "notes": "Drafted from CURRENT_CANDIDATE_REGISTRY. Operator may override status, reason, next_action, and review_date before append.",
    }


def _template_row() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "pre_live_id": "example_pre_live_candidate_id",
        "revision_id": f"rev_{uuid4().hex[:12]}",
        "recorded_at": _iso_now(),
        "record_status": "active",
        "source_kind": "current_candidate_registry",
        "source_ref": ".aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl",
        "source_candidate_registry_id": "example_current_candidate_id",
        "title": "Example pre-live candidate",
        "strategy_or_bundle": {
            "kind": "single_strategy",
            "family": "gtaa",
            "name": "GTAA",
        },
        "settings_snapshot": {
            "summary": "Human-readable settings needed to find or rerun the candidate.",
        },
        "result_snapshot": {
            "cagr": 0.0,
            "mdd": 0.0,
            "sharpe": None,
            "end_balance": None,
        },
        "real_money_signal": {
            "promotion": "real_money_candidate",
            "shortlist": "paper_probation",
            "deployment": "paper_only",
            "validation_status": "normal",
            "liquidity_status": "normal",
            "blockers": [],
        },
        "pre_live_status": "watchlist",
        "operator_reason": "Why this candidate is being tracked before live use.",
        "next_action": "What to do next.",
        "review_date": None,
        "tracking_plan": {
            "cadence": None,
            "stop_condition": None,
            "success_condition": None,
        },
        "docs": {
            "source_report": ".aiworkspace/note/finance/reports/backtests/strategies/GTAA.md",
        },
        "notes": "Optional extra context.",
    }


def _cmd_template(_: argparse.Namespace) -> int:
    print(json.dumps(_template_row(), ensure_ascii=False, indent=2))
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    rows = list(_latest_by_pre_live_id(_load_rows()).values())
    if not args.all:
        rows = [row for row in rows if row.get("record_status") == "active"]
    if args.pre_live_status:
        rows = [row for row in rows if row.get("pre_live_status") == args.pre_live_status]
    rows = sorted(rows, key=lambda row: (str(row.get("pre_live_status")), str(row.get("title"))))
    for row in rows:
        result = row.get("result_snapshot") or {}
        signal = row.get("real_money_signal") or {}
        print(
            f"{row.get('pre_live_id')}: "
            f"{row.get('pre_live_status')} / {row.get('record_status')} / "
            f"CAGR {result.get('cagr')} / MDD {result.get('mdd')} / "
            f"{signal.get('promotion')} / {signal.get('shortlist')} / {signal.get('deployment')}"
        )
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    latest = _latest_by_pre_live_id(_load_rows())
    row = latest.get(args.pre_live_id)
    if row is None:
        raise SystemExit(f"Unknown pre_live_id: {args.pre_live_id}")
    print(json.dumps(row, ensure_ascii=False, indent=2))
    return 0


def _cmd_append(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("recorded_at", _iso_now())
    payload.setdefault("revision_id", f"rev_{uuid4().hex[:12]}")
    payload.setdefault("record_status", "active")
    issues = _validate_row(payload)
    if issues:
        raise SystemExit("Invalid pre-live registry payload:\n- " + "\n- ".join(issues))
    _append_row(payload)
    print(f"appended {payload['pre_live_id']} to {REGISTRY_FILE}")
    return 0


def _cmd_draft_from_current(args: argparse.Namespace) -> int:
    latest = _latest_by_registry_id(_load_current_candidate_rows())
    current_row = latest.get(args.registry_id)
    if current_row is None:
        raise SystemExit(f"Unknown current candidate registry_id: {args.registry_id}")

    row = _build_pre_live_row_from_current_candidate(
        current_row,
        pre_live_status=args.pre_live_status,
        pre_live_id=args.pre_live_id,
        operator_reason=args.operator_reason,
        next_action=args.next_action,
        review_date=args.review_date,
    )
    issues = _validate_row(row)
    if issues:
        raise SystemExit("Invalid drafted pre-live registry payload:\n- " + "\n- ".join(issues))

    if args.append:
        _append_row(row)
        print(f"appended {row['pre_live_id']} to {REGISTRY_FILE}")
        return 0

    print(json.dumps(row, ensure_ascii=False, indent=2))
    return 0


def _cmd_validate(_: argparse.Namespace) -> int:
    rows = _load_rows()
    if not rows:
        print("pre-live registry is empty")
        return 0
    had_issue = False
    for row in rows:
        issues = _validate_row(row)
        if issues:
            had_issue = True
            print(f"{row.get('pre_live_id') or '[missing id]'}:")
            for issue in issues:
                print(f"  - {issue}")
    if not had_issue:
        print(f"validated {len(rows)} pre-live registry row(s) with no missing required fields")
    return 1 if had_issue else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the machine-readable pre-live candidate registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    template_parser = subparsers.add_parser("template", help="Print a JSON template for one pre-live registry row.")
    template_parser.set_defaults(func=_cmd_template)

    list_parser = subparsers.add_parser("list", help="List the latest active pre-live records.")
    list_parser.add_argument("--all", action="store_true", help="Include archived and superseded records.")
    list_parser.add_argument("--pre-live-status", choices=sorted(VALID_PRE_LIVE_STATUSES))
    list_parser.set_defaults(func=_cmd_list)

    show_parser = subparsers.add_parser("show", help="Show the latest record for one pre_live_id.")
    show_parser.add_argument("pre_live_id")
    show_parser.set_defaults(func=_cmd_show)

    append_parser = subparsers.add_parser("append", help="Append one pre-live registry row from a JSON file.")
    append_parser.add_argument("--json-file", required=True)
    append_parser.set_defaults(func=_cmd_append)

    draft_parser = subparsers.add_parser(
        "draft-from-current",
        help="Draft a pre-live row from CURRENT_CANDIDATE_REGISTRY without appending unless --append is set.",
    )
    draft_parser.add_argument("registry_id", help="CURRENT_CANDIDATE_REGISTRY registry_id to convert into a pre-live draft.")
    draft_parser.add_argument("--pre-live-status", choices=sorted(VALID_PRE_LIVE_STATUSES))
    draft_parser.add_argument("--pre-live-id")
    draft_parser.add_argument("--operator-reason")
    draft_parser.add_argument("--next-action")
    draft_parser.add_argument("--review-date", help="YYYY-MM-DD. Required when overriding status to re_review.")
    draft_parser.add_argument("--append", action="store_true", help="Append the drafted row to PRE_LIVE_CANDIDATE_REGISTRY.jsonl.")
    draft_parser.set_defaults(func=_cmd_draft_from_current)

    validate_parser = subparsers.add_parser("validate", help="Validate pre-live registry rows and referenced docs.")
    validate_parser.set_defaults(func=_cmd_validate)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
