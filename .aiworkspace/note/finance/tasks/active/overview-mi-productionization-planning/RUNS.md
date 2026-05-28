# Runs

- `find .aiworkspace/note/finance/phases/active/overview-market-intelligence-productionization -maxdepth 1 -type f | sort`
  - Result: phase bundle files present: `PLAN.md`, `DESIGN.md`, `TASKS.md`, `STATUS.md`, `RISKS.md`, `INTEGRATION.md`.
- `find .aiworkspace/note/finance/tasks/active/overview-mi-productionization-planning -maxdepth 1 -type f | sort`
  - Result: task bundle files present: `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`.
- `git diff --check`
  - Result: pass.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - Result: no missing checklist items; no generated artifacts detected.
