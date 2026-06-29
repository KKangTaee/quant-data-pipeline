# Notes

Status: Active
Last Verified: 2026-06-08

## Intake Result

- Request type: focused Backtest UI / workflow implementation, 3B continuation.
- Primary skill: `finance-backtest-web-workflow`.
- Closeout skill: `finance-doc-sync`.
- Task docs required because this touches service read model, UI, tests, Browser QA, docs, and commit.

## Scope Interpretation

- User flagged that 3A looks like guidance rather than functional improvement.
- 3B should move from maturity guidance to actionable bridge/handoff structure for the first evidence-mature candidate group.
- The change still remains read-only; it should not mutate registries or execute strategy runtimes.

## Boundaries

- No registry / saved JSONL / run history rewrite.
- Do not stage `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`.
- No provider / FRED direct fetch.
- No Risk-On Momentum governance or quarterly maturation.
- No live trading / broker order / auto rebalance design.

## Implementation Decisions

- 3B uses `app/services/backtest_strategy_bridge.py` as the Streamlit-free read model owner.
- Bridge membership is exactly `quality_value_snapshot_strict_annual`, `value_snapshot_strict_annual`, `quality_snapshot_strict_annual`, `gtaa`, and `equal_weight`.
- Deferred exclusions intentionally include Risk-On Momentum 5D, strict quarterly prototypes, and lower-evidence ETF strategies.
- The UI exposes bridge role / target use / required Practical Validation evidence / recommended workflow, but does not save or run anything.
