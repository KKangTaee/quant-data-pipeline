# Notes

Status: Active
Last Verified: 2026-06-08

## Intake Result

- Request type: focused multi-step Backtest UI / workflow implementation.
- Primary skill: `finance-backtest-web-workflow`.
- Closeout skill: `finance-doc-sync`.
- Task docs required because this touches read model, UI, tests, Browser QA, and durable docs.

## Research Bundle Takeaways

- Start with 3A Strategy Evidence Inventory / Direction Panel.
- Strict annual 3종 and GTAA / Equal Weight are the first evidence-mature candidate group.
- Risk-On Momentum 5D remains a Backtest Analysis research lane; governance is deferred.
- Strict quarterly prototypes must stay prototype / contract-smoke.
- GRS / Risk Parity / Dual Momentum need evidence expansion later, not current-candidate reruns in this task.

## Boundaries

- Read-only display only.
- No registry / saved JSONL / run history rewrite.
- No strategy runtime behavior changes.
- No DB schema or provider/FRED fetch.
- No live approval, broker order, account sync, or auto rebalance.

## Implementation Decisions

- Strategy catalog ownership moved to `app/services/backtest_strategy_catalog.py` so the inventory service can read catalog rows without importing `app.web`.
- `app/web/backtest_strategy_catalog.py` remains as an explicit compatibility wrapper for existing UI callers.
- The inventory intentionally separates `runtime_support`, `compare_support`, and `workflow readiness`; supported runtime does not imply Practical Validation / Final Review / Monitoring maturity.
- `Risk-On Momentum 5D` remains `Backtest Analysis research lane` with `governance_status=Deferred`.
- Strict quarterly variants remain `Prototype / contract-smoke`.
