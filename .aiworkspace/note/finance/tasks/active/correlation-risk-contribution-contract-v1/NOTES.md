# Correlation / Risk Contribution Contract V1 Notes

Status: Active
Created: 2026-05-29

## Notes

- Existing `correlation_diversification_risk_contribution` diagnostic already contains average / max correlation, max risk contribution proxy, and monthly return rows.
- Existing `sensitivity_interpretation` already contains a `Component dependency` row from drop-one scenarios.
- V1 labels risk contribution as a proxy because it uses weight times monthly volatility, not full marginal covariance contribution.
- DB price proxy or mixed component curve sources are visible as source strength and remain `REVIEW`, not ready.
- No raw return matrix, covariance matrix, new JSONL registry, user memo, preset, approval, order, or auto rebalance path was added.
