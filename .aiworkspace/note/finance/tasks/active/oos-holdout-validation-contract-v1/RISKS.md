# OOS Holdout Validation Contract V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

- OOS holdout still depends on the quality of the available portfolio / benchmark curve.
- A clean numeric OOS result is not enough if the evidence came only from proxy curves.
- Historical market regime sensitivity is still not covered; next task should add regime bucket evidence using DB / macro loader sources.
- Final Review gate policy still needs a later refinement pass to decide how OOS / regime gaps influence selected-route eligibility.
