#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from textwrap import dedent


# scripts live under .aiworkspace/plugins/quant-finance-workflow/scripts.
REPO_ROOT = Path(__file__).resolve().parents[4]
FINANCE_NOTE_DIR = REPO_ROOT / ".aiworkspace" / "note" / "finance"
PHASES_DIR = FINANCE_NOTE_DIR / "phases"


def _validate_phase_id(value: str) -> str:
    phase_id = value.strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", phase_id):
        raise ValueError("phase id must be a lowercase kebab-case identifier")
    if re.fullmatch(r"phase\d+", phase_id):
        raise ValueError("number-only legacy phase ids are not allowed; use a semantic phase id")
    return phase_id


def _phase_dir(phase_id: str) -> Path:
    # Return the canonical location for phase-specific planning bundles.
    return PHASES_DIR / "active" / _validate_phase_id(phase_id)


def _plan_skeleton(title: str) -> str:
    return dedent(
        f"""\
        # {title} Plan

        ## Goal

        - 이 phase에서 달성할 상위 목표를 적는다.

        ## 이걸 하는 이유?

        - 지금 이 phase가 필요한 이유와 완료 후 좋아지는 점을 적는다.

        ## Scope

        - 포함할 task와 소유 경계를 적는다.

        ## Exit Criteria

        - phase 종료 조건을 적는다.
        """
    )


def _design_skeleton(title: str) -> str:
    return dedent(
        f"""\
        # {title} Design

        ## Current State

        - 현재 구조와 제약을 적는다.

        ## Direction

        - phase 수준의 설계 방향과 task 경계를 적는다.

        ## Tradeoffs

        - 선택한 방향의 장단점과 제외 범위를 적는다.
        """
    )


def _tasks_skeleton(title: str) -> str:
    return dedent(
        f"""\
        # {title} Tasks

        ## Task Board

        | Task | State | Owner | Dependency | Active task |
        |---|---|---|---|---|
        | 첫 작업 단위 | pending | TBD | none | TBD |
        """
    )


def _status_skeleton(title: str) -> str:
    return dedent(
        f"""\
        # {title} Status

        State: active

        ## Current

        - phase kickoff

        ## Next

        - 첫 active task를 확정한다.
        """
    )


def _risks_skeleton(title: str) -> str:
    return dedent(
        f"""\
        # {title} Risks

        ## Open Risks

        - 현재 risk와 영향 범위를 적는다.

        ## Mitigations

        - 완화 방법과 확인 시점을 적는다.
        """
    )


def _integration_skeleton(title: str) -> str:
    return dedent(
        f"""\
        # {title} Integration

        ## Integration Order

        - task 간 통합 순서와 dependency를 적는다.

        ## Conflict Surface

        - 충돌 가능 파일과 소유 경계를 적는다.

        ## Verification

        - phase 통합 완료 전 실행할 검증을 적는다.
        """
    )


def _build_operations(phase_id: str, title: str) -> dict[Path, str]:
    phase_dir = _phase_dir(phase_id)
    return {
        phase_dir / "PLAN.md": _plan_skeleton(title),
        phase_dir / "DESIGN.md": _design_skeleton(title),
        phase_dir / "TASKS.md": _tasks_skeleton(title),
        phase_dir / "STATUS.md": _status_skeleton(title),
        phase_dir / "RISKS.md": _risks_skeleton(title),
        phase_dir / "INTEGRATION.md": _integration_skeleton(title),
    }


def _write(path: Path, content: str, *, force: bool) -> str:
    if path.exists() and not force:
        return f"skip: {path} already exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"write: {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a finance phase document bundle from the repo templates.")
    parser.add_argument(
        "--phase-id",
        required=True,
        help="Semantic lowercase kebab-case id, for example 'research-automation'.",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Human-readable phase title, for example 'Research Automation'.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite files if they already exist.")
    parser.add_argument("--dry-run", action="store_true", help="Print the file plan without writing files.")
    args = parser.parse_args()

    try:
        operations = _build_operations(args.phase_id, args.title)
    except ValueError as exc:
        parser.error(str(exc))

    if args.dry_run:
        for path in operations:
            print(path)
        return 0

    for path, content in operations.items():
        print(_write(path, content, force=args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
