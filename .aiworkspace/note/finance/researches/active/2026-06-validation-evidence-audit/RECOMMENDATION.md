# Recommendation

Status: Draft recommendation
Last Updated: 2026-06-01

## Recommended Direction

Start with evidence-label and selected-route severity hardening. This reduces the risk that prototype, proxy, heuristic, or watch evidence appears like an investment approval while keeping existing storage and workflow boundaries intact.

## Decision Scope

- Immediate next build: relabel user-facing policy / selected / dashboard states and make WATCH / REVIEW semantics explicit in selected-route evidence tables.
- Needs human approval before execution: replay snapshot hash, historical survivorship data expansion, and cost / slippage scenario model.
- Longer roadmap option: sealed OOS / WFO provenance and full covariance risk contribution artifact.
- Not approved / parking lot: live approval, broker/account connection, order instruction, automatic rebalancing, and account-specific tax modeling.

## Why This Direction

The audit found that the strongest current gates are technical: source contract, Data Trust, replay, period coverage, benchmark parity, module blockers, selected-route blockers, and net-cost proof. The largest immediate product risk is not missing another metric; it is overstating current evidence. A narrow label / gate-hardening slice fixes that without touching registries, saved setup, DB schema, or provider ingestion.

## What To Build First

1. Backtest Analysis should present Real-Money output as a first-pass promotion / policy signal, not approval.
2. Practical Validation `READY_WITH_REVIEW` should clearly read as movement with unresolved review evidence, not pass.
3. Final Review selected route should read as monitoring-candidate selection.
4. Selected-route policy rows should display WATCH as allowed with watch, not plain allowed.
5. Selected Dashboard `normal` should read as monitoring baseline clear, not operational approval.

## Pilot Scope

- Code scope: UI / read-model labels and focused contract tests only.
- Storage scope: no route constant rename and no JSONL rewrite.
- Data scope: no DB schema or collector changes.
- Trading boundary: no live approval, broker/account, order, or auto rebalance.

## What To Defer

- replay input snapshot / hash
- historical universe / delisting source expansion
- liquidity-dependent cost and slippage scenarios
- sealed OOS / WFO provenance
- covariance risk contribution artifact

## Decision Checkpoint

After the pilot, the product should no longer imply that WATCH / REVIEW / Deployment preflight / Selected Dashboard means investable approval. If that is true and tests pass, the next approved build can start with replay reproducibility or survivorship evidence.

## Required Decisions

- Whether to make any selected-route `WATCH` category a blocker in the next slice.
- Which P0 data-hardening track comes next: replay snapshot hash, survivorship data, or cost/slippage scenario model.
- Whether to keep the term `Real-Money` in legacy sections or progressively replace it with `Promotion Policy Signal`.

## Proposed Next Handoff

Use `finance-backtest-web-workflow` for the immediate label / gate-hardening build. Use `finance-db-pipeline` only after the user approves historical universe / survivorship data expansion.

## Evidence Summary

- `CURRENT_PROJECT_AUDIT.md` identifies Real-Money / promotion, deployment readiness, liquidity, WFO/OOS/regime, risk contribution, component role, and Selected Dashboard normal state as prototype / proxy / heuristic unless stronger evidence is present.
- `BENCHMARKS.md` shows external products generally label backtests as hypothetical and disclose cost, slippage, data, and live-vs-simulation assumptions.
- Local DB spot checks show useful recent covered-symbol data, but broad survivorship proof is not yet strong enough.

## Risks And Unknowns

- Label hardening may make existing Korean UI strings longer.
- Some tests assert current labels and must be updated intentionally.
- Deeper evidence improvements require data / runtime contracts and should not be mixed into this narrow pilot.
