# Overview Market Context Nasdaq-100 Scenario History Warmup V1 Risks

Last Updated: 2026-07-13

## Open Risks

1. Older acquired/delisted QQQ constituents may lack free historical EOD prices.
   - Keep affected months blocked and report partial readiness; do not synthesize values.
2. Foreign issuers may lack four discrete SEC diluted-EPS quarters.
   - Preserve unsupported-source evidence and the 95% monthly gate.
3. A 119-month synchronous repair may take materially longer than the completed 60-month run.
   - Reuse target-only planning, bounded batches, progress callbacks, per-symbol persistence, and resume semantics.
4. Shared historical scenario diagnostics could regress S&P output.
   - Add S&P 12/36/60 READY regression coverage before changing the shared function.
5. A successful collection can still leave fewer than 119 READY months.
   - Treat actual 12/36/60 graph points as the success evidence; otherwise retain accurate partial UI and retry action.

## Actual Residual Risk

- The 119-month run stopped at 66 READY / 53 BLOCKED months. The remaining 50 planner targets are concentrated in historical acquired/delisted constituents and foreign/non-standard issuer coverage.
- Repeating the same free-source action is resumable and idempotent, but may not improve coverage until those upstream sources expose more history.
- The UI therefore keeps all three options in an actionable partial state; it does not render the existing 7 points as a complete 1/3/5-year graph.
