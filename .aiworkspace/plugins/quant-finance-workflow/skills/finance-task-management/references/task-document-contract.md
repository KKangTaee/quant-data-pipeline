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

## Root Log Rules

Use root logs as handoff summaries, not transcripts:

- `.aiworkspace/note/finance/WORK_PROGRESS.md`: 3-5 concise lines per meaningful milestone
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`: durable analysis result and decision, not every exchange

When a discussion becomes long, move details into active task `NOTES.md`, `STATUS.md`, or `DESIGN.md`, then leave a pointer in the root log.

## Phase Handling

Use active tasks for most non-trivial work. Do not recreate old numbered phase-folder structures unless the user explicitly asks for phase-managed execution.

If a phase is needed, keep it as a higher-level integration layer under `.aiworkspace/note/finance/phases/active/<phase-name>/` and keep execution details inside active task docs.
