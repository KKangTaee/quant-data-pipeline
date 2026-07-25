# Phase Closeout QA Runbook

Status: Active
Last Verified: 2026-05-30

## Purpose

Use this runbook to close a finance phase or phase-slice after implementation, QA, or documentation alignment.
The goal is to make sure the phase state, durable docs, storage boundary, generated artifacts, and verification commands agree before committing.

## When To Use

- A phase가 여러 active task의 결과를 통합하고 종료 상태를 판정한다.
- A phase closeout summarizes multiple implementation tasks.
- A storage, gate, validation, or selected monitoring boundary was reviewed.
- A future agent needs a repeatable checklist instead of reconstructing commands from task notes.

## Inputs Or Prerequisites

- Active phase folder under `.aiworkspace/note/finance/phases/active/<phase>/`.
- Active task folder under `.aiworkspace/note/finance/tasks/active/<task>/`.
- `AGENTS.md`의 canonical document ownership/update trigger와 상태 우선순위.
- 변경 영역에 해당하는 focused durable doc.
- Relevant source maps or QA artifacts for the task.

## Commands

Start by checking local state:

```bash
git status --short
git log -1 --oneline
```

For documentation and phase-task changes:

```bash
git diff --check
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
```

When the task changes service contracts, gate interpretation, selected monitoring boundaries, or storage / execution boundary language:

```bash
.venv/bin/python -m unittest tests.test_service_contracts
```

When `app/services` or `app/runtime` changed:

```bash
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
```

Confirm generated / local artifacts were not accidentally changed or staged:

```bash
git status --short -- \
  .aiworkspace/note/finance/registries \
  .aiworkspace/note/finance/saved \
  .aiworkspace/note/finance/run_history \
  .aiworkspace/note/finance/run_artifacts \
  .playwright-mcp \
  finance/.DS_Store
```

## Expected Result

- Phase `PLAN.md`, `DESIGN.md`, `TASKS.md`, `STATUS.md`, `RISKS.md`, `INTEGRATION.md`가 완료/다음 task와 통합 상태에 대해 일치한다.
- Phase `STATUS.md`는 정규화된 `State: active | paused | verification_only | complete | blocked`를 사용한다.
- Task `RUNS.md` records the commands that were actually run and the result.
- `docs/ROADMAP.md`는 baseline, 상태, 우선순위가 실제로 바뀐 경우에만 갱신한다.
- `docs/INDEX.md`는 문서 탐색 구조나 읽기 순서가 바뀐 경우에만 갱신한다.
- root log는 다음 작업자가 반드시 알아야 할 고신호 handoff가 있을 때만 3~5줄로 남긴다.
- canonical 문서 변경이 없었다면 task/phase closeout에 “canonical doc change 없음”을 정상 결과로 남긴다.
- `registries/*.jsonl`, `saved/*.jsonl`, `run_history/*.jsonl`, `run_artifacts/`, `.playwright-mcp/`, and `.DS_Store` remain unstaged unless the user explicitly asked otherwise.

## Failure Handling

- If a service contract fails, do not mark the phase slice complete. Create or reopen a scoped implementation task with the matching finance domain skill.
- If generated artifacts appear in `git status`, leave them unstaged and record the reason in `RUNS.md`.
- If docs disagree about current source-of-truth, use the state priority in `AGENTS.md`, fix the owning durable doc, and cite the task artifact that supports the interpretation.
- If the task needs a new persistence path, stop and apply the storage checklist in `docs/data/STORAGE_GOVERNANCE.md` before editing code.

## Related Docs

- [Runbook README](./README.md)
- [Storage Governance](../data/STORAGE_GOVERNANCE.md)
- [Portfolio Selection Flow](../flows/PORTFOLIO_SELECTION_FLOW.md)
- [Finance Roadmap](../ROADMAP.md)
- [Finance Documentation Index](../INDEX.md)
