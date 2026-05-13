---
name: finance-integration-review
description: Review and integrate quant-data-pipeline finance work across branches, worktrees, sub-results, or conflict resolutions. Use this for merge conflicts, master/rebase integration, preserving both sides of conflicting finance changes, reviewing sub-agent or parallel work outputs, checking staged diffs before commit, or defining final verification criteria after multi-file finance changes.
---

# Finance Integration Review

Use this skill when the problem is integration quality rather than new implementation.

This skill owns merge/worktree review, conflict-resolution reasoning, sub-result integration, and final verification planning. It does not replace the domain implementation skills.

## First Reads

- `AGENTS.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- the active task or phase docs related to the integration
- affected architecture / flow / data docs only when touched files imply those domains

For detailed checks, read `references/integration-review-checklist.md`.

## Use When

- Merge conflict resolution must preserve both branches' intent.
- A master merge or rebase changed finance docs, UI, DB, loader, strategy, or registry behavior.
- Parallel work from another worktree or sub-agent needs review before integration.
- A broad diff needs final verification criteria before commit.
- The user asks whether a merge, QA, or closeout state is safe.

## Workflow

1. Inspect `git status --short` and identify unrelated local artifacts.
2. Identify affected ownership areas from `PROJECT_MAP.md`.
3. For conflicts, read both sides and preserve distinct behavior unless the user asks to discard one side.
4. Check for stale paths, broken source boundaries, generated artifacts, and registry/run-history mistakes.
5. Run focused validation for the affected domains.
6. Record only durable integration decisions in task docs or root handoff logs.
7. Commit only coherent integration units and leave unrelated local artifacts unstaged.

## Boundary

- Do not make product redesign decisions during conflict resolution unless required to preserve behavior.
- Do not stage `.aiworkspace/note/finance/run_history/*.jsonl`, temp CSV, `.DS_Store`, or generated artifacts unless explicitly requested.
- Route follow-up implementation to the matching domain skill.
