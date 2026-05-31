# Final Review Evidence Appendix V1 Design

## Current Problem

After Decision Cockpit V1, Final Review already has the right read model boundary: it reads the selected Practical Validation result, selected-route gate policy, suggested decision, blockers, review-required rows, and monitoring seed.

The remaining UX issue is ordering. The old prototype order still puts these detailed sections before the final record form:

- validation summary
- robustness / stress details
- paper observation criteria
- investability evidence packet

That makes the screen look like it is rerunning or redoing Practical Validation, even though the code only reads stored evidence.

## Implementation Direction

- Keep the existing helper functions and service read models unchanged.
- Move the final decision form directly after Decision Cockpit.
- Add a new "Evidence Appendix / 이전 검증 결과 부록" section after the decision form.
- Render the existing detailed evidence helpers inside collapsed expanders.
- Add short copy that the appendix is read-only evidence reuse, not a validation rerun.

## User Flow After Change

```text
Candidate Board
  -> Decision Cockpit
  -> Final Decision Record
  -> Evidence Appendix
  -> Saved Final Review Decisions
```

## Non-Goals

- No new validation module.
- No new scoring or selected-route policy.
- No JSONL registry schema change.
- No structured waiver UI.
- No live approval, order, broker connection, account sync, or auto rebalance behavior.
