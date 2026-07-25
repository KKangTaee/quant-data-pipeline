# Task Document Contract

## Active Task Shape

For new substantial tasks, keep the task folder compact:

- `PLAN.md`: goal, scope, stop condition, and `이걸 하는 이유?`
- `DESIGN.md`: code/doc structure analysis and implementation direction
- `STATUS.md`: current progress and next action
- `NOTES.md`: decisions, discoveries, and durable context
- `RUNS.md`: commands run and important outcomes
- `RISKS.md`: open risks, blocked items, and follow-up constraints

Do not create extra planning files unless the task truly needs a separate durable artifact. Put long details in task docs, not root logs.

## Normalized State

For a new task, or when materially updating an existing task `STATUS.md`, include exactly one:

```text
State: active
State: paused
State: verification_only
State: complete
State: blocked
```

Use `active` only while implementation or analysis is actually in progress.
Use `verification_only` when implementation is complete and only explicit user/browser/operational verification remains.
Legacy `Status:` fields may be read as fallback; do not mass-migrate untouched historical tasks.

Resolve state conflicts in this order:

1. explicit user decision
2. normalized task/phase `STATUS.md`
3. compact manifest
4. Roadmap summary
5. root log

## Root Log Rules

Use root logs as handoff summaries, not transcripts:

- `.aiworkspace/note/finance/WORK_PROGRESS.md`: 3-5 concise lines per meaningful milestone
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`: durable analysis result and decision, not every exchange

When a discussion becomes long, move details into active task `NOTES.md`, `STATUS.md`, or `DESIGN.md`, then leave a pointer in the root log.
Do not update root logs for every closeout. Add a pointer only when the next worker needs a high-signal milestone or decision.

## Phase Handling

Use active tasks for most non-trivial work. Open a phase only when the user explicitly asks for phase-managed execution.

If a phase is needed, keep it as a higher-level integration layer under
`.aiworkspace/note/finance/phases/active/<semantic-phase-id>/` with
`PLAN.md`, `DESIGN.md`, `TASKS.md`, `STATUS.md`, `RISKS.md`, and `INTEGRATION.md`.
Keep execution details inside active task docs and do not recreate old numbered phase-folder structures.
