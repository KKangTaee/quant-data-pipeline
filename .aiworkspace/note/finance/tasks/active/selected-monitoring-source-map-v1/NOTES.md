# Selected Monitoring Source Map V1 Notes

Status: Complete
Created: 2026-05-29

## Notes

- `load_final_selected_portfolio_dashboard()` uses `FINAL_SELECTION_DECISION_V2_FILE` through `load_final_selection_decisions_v2()`.
- Selected Dashboard active filter is `decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO` or `selected_practical_portfolio == true`.
- Performance Recheck currently rebuilds selected component payloads through Current Candidate Registry rows keyed by component `registry_id`.
- Symbol Freshness uses the same replay contract source to resolve portfolio and benchmark symbols, then reads DB price freshness metadata.
- Provider Evidence resolves selected provider symbol weights from candidate replay contract first, then component fallback fields; fallback stays `REVIEW`.
- Timeline, latest recheck result, drift check, and alert preview are session-state evidence, not durable monitoring records.
- `append_selected_portfolio_monitoring_log()` exists for explicit optional records, but the active Selected Dashboard path does not call it.
- Review Signals and Recheck Comparison should not remain two independent policy owners for the same CAGR / MDD / benchmark spread thresholds.

## Immediate Question For 12-2

Should recheck readiness be able to use an embedded selected component contract from the Final Review V2 decision row before falling back to Current Candidate Registry?
