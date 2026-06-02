# Notes

## High

- Final Review selected-route gate currently behaves like a live/deployment readiness audit.
- Practical Validation allows `REVIEW` rows to move forward, but Final Review treats most `REVIEW` rows as selection blockers.
- Single-component candidates can still be blocked by audits that Practical Validation module planning marks not applicable.

## Medium

- Weighted mix source conversion drops `weight_reason`, causing component role / weight rationale coverage failures.
- Weighted mix evidence does not reliably surface aggregate cost / turnover / net-cost curve snapshots to Backtest Realism.
- Provider / lifecycle / cost sensitivity gaps are real, but many are follow-up items rather than selection blockers.

## Low

- Existing labels such as "실전 검토 통과 후보" can still be confused with live approval if open review / live-readiness boundary is not visible enough.
- Selected Dashboard needs a compact way to carry open review items forward.

## Implementation Notes

- `selection_gate_policy_snapshot` is the policy that controls `SELECT_FOR_PRACTICAL_PORTFOLIO` save readiness.
- `deployment_readiness_policy_snapshot` preserves the previous stricter interpretation so a future Live / Deployment Readiness screen can remain strict without forcing Final Review to behave like live approval.
- `gate_policy_snapshot` intentionally points to the selection policy for backward-compatible read paths.
- Default `REVIEW` findings become `WATCH` in the selection policy and are emitted through `open_review_items`.
- `REVIEW_REQUIRED` is still possible for selection when the issue is benchmark parity or explicit backtest realism selection evidence such as transaction cost / net cost curve / net performance / gross-only gaps.
- Single-component sources treat weighted-mix-only risk contribution / component role-weight audits as not applicable for selection.
