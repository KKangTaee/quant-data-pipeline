# Notes

- Runtime already has partial real-money hardening metadata for some strategies: transaction cost bps, turnover estimates, net spread policy, provider operability.
- The immediate gap is evidence visibility and final-review handoff, not another registry.
- Missing cost / turnover / liquidity evidence should be `NEEDS_INPUT` or `REVIEW`, not pass.
- The first slice does not gate selected-route. It exposes realism gaps in the packet so a later task can decide whether specific statuses should become policy blockers.
- `Tax / account scope` remains `REVIEW` unless an explicit tax/account scope or operator acknowledgment is attached.
