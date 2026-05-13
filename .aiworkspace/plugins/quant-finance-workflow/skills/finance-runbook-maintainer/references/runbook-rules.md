# Runbook Rules

## Shape

Use this structure when creating or rewriting a runbook:

1. Purpose
2. When to use
3. Inputs or prerequisites
4. Commands or UI path
5. Expected result
6. Failure handling
7. Related docs

## Keep It Durable

- Prefer stable commands over one-off shell history.
- Mention which artifacts should remain unstaged.
- Link to task docs for historical detail instead of copying the whole investigation.
- Keep root logs short; runbooks should carry repeatable procedure detail.

## Update Points

- Update `docs/runbooks/README.md` when adding a new runbook.
- Update `AUTOMATION_SCRIPTS.md` when adding or changing helper scripts.
- Update `agent/GOTCHAS.md` when the runbook exists mainly to prevent repeated mistakes.
