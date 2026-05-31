# Notes

- User clarified that the next redesign needs at least one portfolio already selected through Final Review stage 3.
- GTAA-only or GTAA-heavy candidates from the previous task are excluded from the first search pass.
- Selection safety remains unchanged: no live approval, broker/account, orders, or auto rebalance.

## Fresh Non-GTAA Search Result

- Changing the strategy family alone did not produce a current-gate selected candidate.
- Fresh non-GTAA candidates can reach Practical Validation and Final Review evidence readiness, but current selected-route policy treats critical `REVIEW` rows as selection blockers.
- Strongest practical fresh candidate by balanced drawdown/performance was `EW GrowthSectorGold 50 + RiskParity 25 + GRS 25`: replay CAGR 13.01%, MDD -13.66%, Sharpe 1.21, Practical Validation score 9.1.
- Strongest high-return fresh candidates used `SOXX / SPY / IEF / TLT` lifecycle-supported ETF mixes, but drawdowns were materially higher and Final Review still blocked selection.

## Main Blockers

- `Backtest Realism`: weighted mix sources do not yet carry complete net cost curve proof, turnover, explicit cost/slippage sensitivity, net performance policy, and tax/account scope evidence.
- `Component Role / Weight`: weighted mix prefill has component rationale, but the current source builder does not preserve `weight_reason`, so weight rationale coverage is 0.0%.
- `Risk Contribution`: single-strategy candidates and several mixed/proxy component curves produce review-required concentration or correlation findings.
- `Data Coverage / Provider / Construction / Validation Efficacy`: many candidates remain in `REVIEW`, which is enough to block selected-route under the current strict evidence profile.

## Legacy Candidate

- Existing V1 registry contains a non-GTAA Quality selected candidate: `Quality Coverage 100 Top-10 AOR MA250 paper-only candidate`.
- It is already a historical Final Review `SELECT_FOR_PRACTICAL_PORTFOLIO` record with no live approval or order instruction.
- Dashboard handoff dry-run is ready if the row is migrated or seeded into the V2 registry, but this would be a controlled legacy migration seed rather than a fresh current-gate revalidation.
