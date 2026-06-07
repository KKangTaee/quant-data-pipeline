# Risks

Status: Completed
Last Verified: 2026-06-07

## Residual Risks

- Browser QA confirmed the Portfolio Mix Builder screen renders after moving visual CSS / card helpers.
- `_render_strategy_compare_workspace` remains a very large form orchestration function and is intentionally not split in this task.
- Saved portfolio replay and weighted result panels still live in `app/web/backtest_compare.py`.

## Do Not Infer

- This task does not change strategy math, compare execution, saved portfolio schema, registry policy, or Practical Validation handoff behavior.
