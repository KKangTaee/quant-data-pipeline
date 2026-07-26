# Risk-On Momentum 5D Productionization Notes

## Decisions

- Label-only promotion is unsafe because maturity currently gates Level2 handoff.
- Core strategy behavior is treated as an existing contract; optimization must prove parity.
- Standard execution should be a useful candidate review, while 50-random plus sensitivity
  belongs to an explicit deep-research mode.
- Full trade/scanner rows stay generated; downstream uses compact evidence only.
- Current universe membership must not be presented as historical PIT membership.

## Existing Dirty Worktree

The following pre-existing user/runtime files are out of scope and must not be staged:

- `.aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl`
- `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`
- `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`
- `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`
- existing generated QA images and `.superpowers/`

## Baseline Test Gap

The broader evidence-inventory suite currently has one pre-existing drift failure:
`test_backtest_ui_uses_catalog_defaults_for_primary_strategy_surfaces` searches the current
Single Strategy source for the old literal `statement annual`. Risk-On core and governance
tests are green. This drift should be handled only if the owning contract is touched.
