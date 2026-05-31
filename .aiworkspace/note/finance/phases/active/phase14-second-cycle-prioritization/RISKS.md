# Phase 14 Second-Cycle Prioritization Risks

Status: Active
Created: 2026-05-30

## Risks

- Phase 14 could become another broad documentation phase without selecting a concrete implementation slice.
- The first second-cycle task could be chosen because it is easy, not because it improves investability the most.
- Data-source dependent candidates could be implemented before source availability is understood.
- Broker-grade execution or production monitoring language could overstate the system's actual scope.
- Storage boundary drift could reintroduce user memo / preset / monitoring log sprawl.

## Mitigation

- Rank candidates with explicit impact / effort / dependency / source uncertainty / QA criteria.
- Separate immediately implementable workflow hardening from source-review and product-research work.
- Keep broker/account/order/auto rebalance out of scope unless a future phase explicitly approves design-only work.
- Preserve DB-backed full evidence and compact workflow JSONL boundaries.
- Require `git diff --check` and artifact boundary checks for this phase.

## Current Risk Posture

Phase 14 has only opened the board.
Main risk now is prioritization drift: 14-1 must produce a concrete first implementation recommendation rather than another open-ended list.
