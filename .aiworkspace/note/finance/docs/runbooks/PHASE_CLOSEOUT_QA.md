# Phase Closeout QA Runbook

Status: Active
Last Verified: 2026-05-30

## Purpose

Use this runbook to close a finance phase or phase-slice after implementation, QA, or documentation alignment.
The goal is to make sure the phase state, durable docs, storage boundary, generated artifacts, and verification commands agree before committing.

## When To Use

- A phase task changes docs / runbooks / roadmap / root logs.
- A phase closeout summarizes multiple implementation tasks.
- A storage, gate, validation, or selected monitoring boundary was reviewed.
- A future agent needs a repeatable checklist instead of reconstructing commands from task notes.

## Inputs Or Prerequisites

- Active phase folder under `.aiworkspace/note/finance/phases/active/<phase>/`.
- Active task folder under `.aiworkspace/note/finance/tasks/active/<task>/`.
- Current docs index and roadmap:
  - `.aiworkspace/note/finance/docs/INDEX.md`
  - `.aiworkspace/note/finance/docs/ROADMAP.md`
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

- Phase `PLAN.md`, `TASKS.md`, `STATUS.md`, `CURRENT_CHAPTER_TODO.md`, `DESIGN.md`, `INTEGRATION.md`, and `RISKS.md` agree on completed / next task.
- Task `RUNS.md` records the commands that were actually run and the result.
- `docs/INDEX.md` and `docs/ROADMAP.md` point to the current active phase and next task.
- `WORK_PROGRESS.md` and `QUESTION_AND_ANALYSIS_LOG.md` contain only concise handoff entries.
- `registries/*.jsonl`, `saved/*.jsonl`, `run_history/*.jsonl`, `run_artifacts/`, `.playwright-mcp/`, and `.DS_Store` remain unstaged unless the user explicitly asked otherwise.

## Failure Handling

- If a service contract fails, do not mark the phase slice complete. Create or reopen a scoped implementation task with the matching finance domain skill.
- If generated artifacts appear in `git status`, leave them unstaged and record the reason in `RUNS.md`.
- If docs disagree about current source-of-truth, fix the durable doc first and cite the task artifact that supports the interpretation.
- If the task needs a new persistence path, stop and apply the storage checklist in `docs/data/STORAGE_GOVERNANCE.md` before editing code.

## Related Docs

- [Runbook README](./README.md)
- [Storage Governance](../data/STORAGE_GOVERNANCE.md)
- [Portfolio Selection Flow](../flows/PORTFOLIO_SELECTION_FLOW.md)
- [Finance Roadmap](../ROADMAP.md)
- [Finance Documentation Index](../INDEX.md)
