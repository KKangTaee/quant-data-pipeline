---
name: finance-runbook-maintainer
description: Maintain durable runbooks for repeated quant-data-pipeline finance operations. Use this when a repeated command, QA procedure, ingestion process, registry helper, app startup flow, provider snapshot refresh, merge routine, or operational checklist should be documented under .aiworkspace/note/finance/docs/runbooks instead of being left only in chat or task notes.
---

# Finance Runbook Maintainer

Use this skill when a repeated finance procedure needs a durable operating guide.

This skill writes and maintains `docs/runbooks/` content. It does not own code implementation or final cross-doc sync.

## First Reads

- `AGENTS.md`
- `.aiworkspace/note/finance/docs/runbooks/README.md`
- `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md` when helper scripts are involved
- the relevant active task docs if the procedure came from current work

For runbook writing rules, read `references/runbook-rules.md`.

## Use When

- A command sequence is repeated across turns or worktrees.
- An ingestion, provider refresh, registry helper, QA, app startup, or merge routine needs clear operating steps.
- A task uncovered a recurring failure mode that future agents should avoid.
- A helper script is added or its usage changes.

## Workflow

1. Decide whether the content belongs in an existing runbook or a new one.
2. Keep runbooks procedural: purpose, when to use, commands, expected result, failure handling.
3. Link to architecture/data/flow docs instead of copying large explanations.
4. Update `docs/runbooks/README.md` or `AUTOMATION_SCRIPTS.md` when discoverability changes.
5. Route final cross-doc alignment to `finance-doc-sync` if roadmap/index/root logs also changed.

## Boundary

- Do not put one-off experiment notes in runbooks.
- Do not turn runbooks into implementation logs.
- Do not document commands that were not run or verified unless clearly marked as planned.
