# Status

Status: Implementation complete

## 2026-05-29

- Active task opened for Phase 9-2.
- Initial finding: runtime `_estimate_turnover_series(...)` uses `End Ticker` / `End Balance` and `Next Ticker` / `Next Balance`, but Backtest Realism Audit currently only checks whether `avg_turnover` or `max_turnover` exists.
- Gap: audit cannot distinguish actual holdings-derived turnover evidence from cadence-only evidence.
- Runtime now marks turnover evidence with `turnover_evidence_contract_v1`.
- Missing holdings columns now produce `not_estimated_missing_holdings` instead of a fake turnover estimate.
- Practical Validation source snapshots preserve `turnover_evidence_snapshot`.
- Backtest Realism Audit exposes `turnover_evidence_contract`; actual holdings-derived estimates can PASS, legacy or cadence-only evidence stays REVIEW, missing evidence is NEEDS_INPUT.
