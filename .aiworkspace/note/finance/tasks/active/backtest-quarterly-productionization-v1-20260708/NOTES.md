# Notes

## Baseline Findings

- Quarterly strict strategies were intentionally marked `Prototype / contract-smoke` in `app/services/backtest_strategy_evidence_inventory.py`; this task promotes them to formal `Strict Quarterly` labels.
- Historical work raised quarterly to runtime / compare / history contract smoke parity, not annual-level promotion readiness.
- Strict annual Quality runner exposes investability, benchmark, promotion, and guardrail contracts. Quarterly wrappers currently expose a narrower portfolio-handling oriented contract.
- Quarterly statement path must handle 10-Q plus 10-K/FY rows for Q4-like coverage, so filing timing and coverage need stronger evidence than annual before promotion.

## Implementation Notes

- Formal promotion keeps strategy keys such as `quality_snapshot_strict_quarterly_prototype` for saved payload compatibility; only user-facing labels and evidence maturity changed.
- Runtime bundles now carry `meta.statement_shadow_coverage` for strict statement-shadow factor paths, so post-run readiness can identify actual missing statement/shadow symbols after a run.
- Post-run Factor Readiness can call `run_extended_statement_refresh()` for missing statement/shadow symbols and marks the displayed result as requiring a new run after successful repair.
- Quarterly Value and Quality+Value wrappers now pass investability filters, benchmark/guardrail settings, and promotion thresholds to the DB-backed sample layer and real-money hardening.
