# Risks

- If selection gate is too permissive, users may confuse a tracked candidate with live readiness.
- If old strict policy is removed instead of preserved, Live / Deployment Readiness cannot reuse the audit evidence later.
- Tests must assert both paths: selection can pass with open review items, while deployment readiness remains stricter.

## Mitigations

- Saved decision rows carry both selection and deployment policy snapshots.
- `open_review_items` keeps allowed `REVIEW` findings visible instead of silently passing them.
- Live approval, broker order, account sync, auto rebalance, provider fetch, DB schema change, and registry rewrite stayed out of scope.
- Service contracts now cover selection pass with review items, hard blocker failure, and stricter deployment policy preservation.
