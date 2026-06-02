# Status

- 2026-06-01: Task opened after user approval. Scope is Final Review selection-readiness gate separation plus first evidence mapping fixes.
- 2026-06-01: Implemented weighted mix source evidence preservation for role / weight reason / cost / turnover / net-cost snapshots.
- 2026-06-01: Split Final Review gate policy into `selection_gate_policy_snapshot` and `deployment_readiness_policy_snapshot`; `gate_policy_snapshot` remains a selection-policy compatibility alias.
- 2026-06-01: Added `open_review_items` to investability packet, cockpit summary, and saved final decision row. Default `REVIEW` findings now carry forward without blocking selection, while hard blockers and critical missing evidence still block.
- 2026-06-01: Durable docs and root handoff logs aligned.
