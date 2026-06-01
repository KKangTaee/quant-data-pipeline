# Risks

- Scenario execution may still depend on local DB/candidate replay availability; failed scenario rows should be explicit errors, not pass states.
- Existing user-created portfolio setup must remain readable.
- Rebalance "next target" is a planned recompute, not a known future holding signal.
- Browser QA used the current local DB / registry state, including the existing dirty saved portfolio file. The implementation preserves that file but does not normalize or rewrite it as part of this task.
- Scenario summary remains empty until per-strategy Monitoring Scenario runs in the current session. This is intentional and should not be read as a stored monitoring result.
