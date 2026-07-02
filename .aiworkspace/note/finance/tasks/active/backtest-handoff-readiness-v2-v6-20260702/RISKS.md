# Backtest Handoff Readiness V2-V6 Risks

## Remaining Risks

- V2 is a location/refactor change only. It intentionally preserves current readiness semantics, including conceptual duplication between `promotion_decision` and source checks.
- V3 must reduce duplicated display without weakening blocker behavior.
- V5 must store compact handoff evidence only; raw provider / run history payloads should stay out of workflow JSONL.
