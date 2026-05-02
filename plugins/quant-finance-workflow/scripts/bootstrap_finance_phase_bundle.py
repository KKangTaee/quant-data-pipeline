#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[3]
FINANCE_NOTE_DIR = REPO_ROOT / ".note" / "finance"
PHASES_DIR = FINANCE_NOTE_DIR / "phases"
PHASE_PLAN_TEMPLATE = FINANCE_NOTE_DIR / "PHASE_PLAN_TEMPLATE.md"
PHASE_CHECKLIST_TEMPLATE = FINANCE_NOTE_DIR / "PHASE_TEST_CHECKLIST_TEMPLATE.md"


def _slugify(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_")
    return token.upper() or "NEW_PHASE"


def _phase_dir(phase_number: int) -> Path:
    # Return the canonical location for phase-specific planning bundles.
    return PHASES_DIR / f"phase{phase_number}"


def _prefixed_template(header: str, template_path: Path) -> str:
    body = template_path.read_text(encoding="utf-8").strip()
    return f"{header}\n\n{body}\n"


def _todo_skeleton(phase_number: int, title: str) -> str:
    return dedent(
        f"""\
        # Phase {phase_number} Current Chapter TODO

        ## 상태
        - `kickoff / first_work_unit_in_progress`

        ## 1. 핵심 작업

        - `in_progress` 첫 번째 작업 단위
          - {title} phase를 실제로 시작하기 위한 첫 작업을 적는다
        - `pending` 두 번째 작업 단위
          - 첫 번째 작업 이후 바로 이어질 구현/정리 항목을 적는다

        ## 2. Validation

        - `pending` `py_compile`
        - `pending` `.venv` import smoke
        - `pending` targeted manual validation

        ## 3. Documentation Sync

        - `completed` phase kickoff plan 문서 생성
        - `completed` current chapter TODO 문서 생성
        - `pending` first work-unit 문서 생성
        - `pending` roadmap / doc index / work log / question log sync
        """
    )


def _completion_skeleton(phase_number: int, title: str) -> str:
    return dedent(
        f"""\
        # Phase {phase_number} Completion Summary

        ## 목적

        - Phase {phase_number} `{title}`를 closeout 기준으로 정리한다.

        ## 이번 phase에서 실제로 완료된 것

        ### 1. 첫 번째 큰 정리 항목

        - 이 phase에서 실제로 끝낸 구현/정리 내용을 적는다.

        쉽게 말하면:

        - 사용자가 무엇을 더 쉽게 하게 되었는지 적는다.

        ## 아직 남아 있지만 closeout blocker는 아닌 것

        - 후속 polish 또는 다음 phase로 넘길 항목을 적는다.

        쉽게 말하면:

        - 지금 남아 있는 일은 무엇이고, 왜 이번 phase blocker가 아닌지 적는다.

        ## closeout 판단

        - 현재 기준 상태를 적는다.
        """
    )


def _next_phase_skeleton(phase_number: int) -> str:
    return dedent(
        f"""\
        # Phase {phase_number} Next Phase Preparation

        ## 목적

        - Phase {phase_number} 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리한다.

        ## 현재 handoff 상태

        - 이번 phase를 통해 무엇이 고정되었는지 적는다.

        ## 다음 phase에서 더 중요한 질문

        1. 다음에 먼저 다뤄야 할 질문
        2. 그 다음 질문

        ## 다음 phase에서 실제로 할 작업

        쉽게 말하면:

        - 다음 phase에서 무엇을 실제로 만들거나 정리하는지 적는다.
        - "왜 다음 phase인가"와 별개로 "무슨 작업을 하는가"가 바로 보이게 적는다.

        주요 작업:

        1. 첫 번째 작업
           - 무엇을 바꾸거나 확인하는지 적는다.
        2. 두 번째 작업
           - 무엇을 바꾸거나 확인하는지 적는다.

        ## 추천 다음 방향

        - 왜 그 방향이 자연스러운지 적는다.

        ## handoff 메모

        - 다음 턴에서 바로 읽어야 할 문서나 주의점을 적는다.
        """
    )


def _build_paths(phase_number: int, title: str) -> dict[str, Path]:
    phase_dir = _phase_dir(phase_number)
    slug = _slugify(title)
    return {
        "phase_dir": phase_dir,
        "plan": phase_dir / f"PHASE{phase_number}_{slug}_PLAN.md",
        "todo": phase_dir / f"PHASE{phase_number}_CURRENT_CHAPTER_TODO.md",
        "completion": phase_dir / f"PHASE{phase_number}_COMPLETION_SUMMARY.md",
        "next_phase": phase_dir / f"PHASE{phase_number}_NEXT_PHASE_PREPARATION.md",
        "checklist": phase_dir / f"PHASE{phase_number}_TEST_CHECKLIST.md",
    }


def _write(path: Path, content: str, *, force: bool) -> str:
    if path.exists() and not force:
        return f"skip: {path} already exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"write: {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a finance phase document bundle from the repo templates.")
    parser.add_argument("--phase", type=int, required=True, help="Phase number, for example 21.")
    parser.add_argument("--title", required=True, help="Phase title, for example 'Research Automation And Experiment Persistence'.")
    parser.add_argument("--force", action="store_true", help="Overwrite files if they already exist.")
    parser.add_argument("--dry-run", action="store_true", help="Print the file plan without writing files.")
    args = parser.parse_args()

    paths = _build_paths(args.phase, args.title)
    operations = {
        paths["plan"]: _prefixed_template(
            f"# Phase {args.phase} {args.title} Plan",
            PHASE_PLAN_TEMPLATE,
        ),
        paths["todo"]: _todo_skeleton(args.phase, args.title),
        paths["completion"]: _completion_skeleton(args.phase, args.title),
        paths["next_phase"]: _next_phase_skeleton(args.phase),
        paths["checklist"]: _prefixed_template(
            f"# Phase {args.phase} Test Checklist",
            PHASE_CHECKLIST_TEMPLATE,
        ),
    }

    if args.dry_run:
        for path in operations:
            print(path)
        return 0

    for path, content in operations.items():
        print(_write(path, content, force=args.force))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
