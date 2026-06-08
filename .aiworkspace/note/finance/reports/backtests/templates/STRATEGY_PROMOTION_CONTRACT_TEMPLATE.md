# Strategy Promotion Contract Template

Status: Template
Last Verified: 2026-06-08

## Metadata

| Field | Value |
|---|---|
| Contract ID | |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Source Worktree / Session | `backtest-dev` / other |
| Strategy Family | |
| Strategy Owner | |
| Target Use Case | |
| Requested Promotion State | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |
| Related Backtest Reports | |
| Related Strategy Hub / Log | |
| Related Generated Artifacts | |
| Related Registry IDs | optional |

## Handoff Summary

| Item | Value |
|---|---|
| What changed | |
| Why this strategy should be reviewed for product workflow | |
| What must not be inferred from this contract | Not live approval, not broker order, not account sync, not auto rebalance |
| Recommended next owner | `main-dev` / `backtest-dev` / other |
| Recommended next action | Practical Validation source build / more research / block / review |

## Strategy Identity

| Field | Value |
|---|---|
| Strategy family | |
| Strategy key / runner | |
| Owner | |
| Target use case | |
| Product surface requested | Backtest Analysis / Practical Validation / Final Review / Portfolio Monitoring |

## Universe And Membership Contract

| Field | Value |
|---|---|
| Universe definition | |
| Membership source | |
| Historical membership policy | |
| Survivorship assumption | |
| Excluded ticker policy | |
| Coverage gaps | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## Data And PIT Contract

| Field | Value |
|---|---|
| Price data source | |
| Factor / statement source | |
| Macro / provider source | |
| Point-in-time assumption | |
| Available-at assumption | |
| Current snapshot caveats | |
| Look-ahead risk notes | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## Parameter And Optimization Contract

| Field | Value |
|---|---|
| Frozen promotion parameter set | |
| Parameter search space | |
| Optimization history | |
| Parameter selection reason | |
| Sensitivity results | |
| Overfit warning | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## IS OOS And Walk Forward Evidence

| Field | Value |
|---|---|
| In-sample period | |
| Out-of-sample period | |
| Holdout policy | |
| Walk-forward method | |
| Walk-forward result | |
| Regime split result | |
| Stress windows | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## Cost Slippage Turnover And Liquidity

| Field | Value |
|---|---|
| Transaction cost assumption | |
| Slippage assumption | |
| Cost application to result curve | |
| Turnover evidence | |
| Liquidity / capacity assumption | |
| Net performance policy | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## Benchmark And Comparator Policy

| Field | Value |
|---|---|
| Primary benchmark | |
| Secondary comparator | |
| Comparator period parity | |
| Comparator frequency parity | |
| Comparator coverage parity | |
| Benchmark spread interpretation | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## Replay Contract

| Field | Value |
|---|---|
| Runtime owner | |
| Replay command / service | |
| Replay input payload | |
| Latest DB replay policy | |
| Selection / holdings history replay | |
| Expected output fields | |
| Replay blockers | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## Generated Artifacts And Storage Boundary

| Field | Value |
|---|---|
| Generated artifact location | |
| Artifact contents | |
| Artifact retention policy | Generated/local artifact unless explicitly approved |
| Workflow JSONL payload boundary | Compact evidence only |
| DB-only evidence | |
| Evidence state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |

## Known Failures And Evidence State

| Failure / Gap | State | Owner | Next Action | Product Effect |
|---|---|---|---|---|
| | `NOT_RUN` / `REVIEW_REQUIRED` / `BLOCKED` | | | |

## Practical Validation Source Payload Conditions

| Required Payload Item | Provided? | Source / Notes |
|---|---|---|
| strategy family / key | | |
| frozen parameters | | |
| universe label and membership rule | | |
| period start / end | | |
| benchmark / comparator policy | | |
| result summary | | |
| equity curve boundary | | |
| selection / holdings history | | |
| cost / turnover / liquidity compact evidence | | |
| data trust warnings | | |
| generated artifact pointer | | |
| missing payload fields and reason | | |

## Final Review Selected Route Blockers

| Potential Blocker | State | Reason | Required Fix |
|---|---|---|---|
| replay contract missing | | | |
| PIT / look-ahead ambiguity | | | |
| survivorship ambiguity | | | |
| benchmark / comparator parity missing | | | |
| hidden optimization | | | |
| OOS / walk-forward missing | | | |
| net cost / slippage proof missing | | | |
| liquidity / capacity unknown | | | |
| generated artifact missing | | | |
| critical `NOT_RUN` evidence | | | |

## Portfolio Monitoring Review Triggers

| Trigger | Threshold / Condition | Review Owner | Monitoring Effect |
|---|---|---|---|
| benchmark underperformance | | | |
| drawdown deterioration | | | |
| replay failure | | | |
| stale source / provider / macro evidence | | | |
| liquidity / capacity coverage drop | | | |
| universe membership refresh gap | | | |
| strategy-specific trigger | | | |

## Promotion Review Decision

| Field | Value |
|---|---|
| Main-dev reviewer | |
| Review date | YYYY-MM-DD |
| Decision state | `PROMOTE_READY` / `REVIEW_REQUIRED` / `BLOCKED` / `NOT_RUN` |
| Decision reason | |
| Practical Validation handoff allowed? | yes / no |
| Final Review selected-route allowed? | yes / no |
| Portfolio Monitoring trigger defined? | yes / no |
| Required follow-up | |

## Verification

| Check | Command / Evidence | Result |
|---|---|---|
| Contract structure check | `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_strategy_promotion_contract.py <this-file>` | |
| Related backtest report read | | |
| Generated artifact path exists | | |
| Replay command smoke | | |
| Practical Validation payload review | | |

## Notes

- This contract does not approve the strategy for live trading.
- This contract does not rewrite registry / saved JSONL.
- `NOT_RUN` means the evidence was not executed or is unavailable. It is not pass.
- Generated artifacts should not be staged or committed unless explicitly approved.
