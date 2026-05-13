# Integration Review Checklist

## Conflict Resolution

- Identify the owning files and feature surfaces before editing.
- Preserve both sides when they add distinct behavior.
- Prefer manual reconciliation over choosing `ours` or `theirs`.
- Re-run focused validation for every ownership area touched.

## Worktree / Branch Integration

- Check whether the incoming work changed docs, scripts, runtime paths, registry assumptions, or DB schema.
- Keep generated artifacts and local run history unstaged.
- Update task `RUNS.md` with important validation outcomes.
- Update root handoff logs only with high-signal milestone summaries.

## Diff Review

- Confirm changed files match the stated task scope.
- Check stale path references after migrations.
- Check registry JSONL and saved setup files are intentionally changed before staging.
- Run `git diff --check` before commit.

## Validation Menu

- Skill changes: `quick_validate.py` for each changed skill.
- Plugin changes: JSON parse manifest and marketplace files.
- Python code changes: focused `py_compile` or targeted tests.
- Web UI changes: Browser/Playwright only when layout or interaction behavior changed.
