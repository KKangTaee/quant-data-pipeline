# Final Review Candidate Board V1 Notes

## Decisions

- Candidate Board remains read-only and uses existing Practical Validation / investability packet / Decision Cockpit evidence.
- Board priority is a display priority for review usefulness, not a new investment score.
- Gate-failed Practical Validation rows remain hidden from Final Review source options by existing eligibility policy.
- Board sorting is `SELECT_READY`, then `HOLD_OR_RE_REVIEW`, then `SELECT_BLOCKED`; blockers, review-required rows, critical gaps, NOT_RUN, packet score, and original order are tie-breakers.

## Boundary

- Practical Validation owns validation execution and Final Review move eligibility.
- Candidate Board owns comparison and review priority among eligible candidates.
- Decision Cockpit owns the selected candidate's detailed selected-route state.

## QA Evidence

- Browser QA confirmed Candidate Board count cards, first-review candidate, Review Queue, Candidate Board detail, and source picker render in Final Review.
- Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/final-review-candidate-board-v1-qa.png`
