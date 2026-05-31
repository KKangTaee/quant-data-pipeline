# Backtest Realism Gate Policy Refinement V1 Risks

| Risk | Mitigation |
| --- | --- |
| Row-level audit evidence changes selected-route semantics unexpectedly | Keep existing route semantics and add tests around expected severity |
| `NEEDS_INPUT` row status is treated as PASS when merged directly | Explicitly map `NEEDS_INPUT` to blocker severity |
| Gate policy becomes a persistence layer | Keep change in read model only; do not write JSONL or DB |
| Specific Phase 9 gaps remain hidden behind generic route labels | Assert policy evidence contains the failing Backtest Realism row criteria |

## Residual Risk

- This task refines Final Review gate evidence and severity. It does not add a new sensitivity execution engine or liquidity simulator.
- Phase 9-7 should run integrated QA across Backtest Realism Audit, investability packet, selected-route gate, and docs.
