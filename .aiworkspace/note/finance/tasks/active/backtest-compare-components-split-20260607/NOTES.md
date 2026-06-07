# Notes

Status: Completed
Last Verified: 2026-06-07

## Findings

- `app/web/backtest_compare.py` had about 6,220 lines before this task.
- The safest first split was the visual shell block near the top of the file because it does not own runtime calls, registry writes, or saved replay orchestration.
- `_render_strategy_compare_workspace` remains the largest body and should be split later only after a smaller visual boundary lands cleanly.

## Decisions

- Keep component result row calculation in `app/web/backtest_compare.py`.
- Move only card rendering for those rows to `app/web/backtest_compare_components.py`.
- Do not move `render_compare_portfolio_workspace`; it remains the page-level entrypoint.
- Keep the next split small enough to preserve Compare workflow behavior; saved replay and weighted result panels are better follow-up candidates than moving the entire workspace body at once.
