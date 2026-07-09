# Notes

- Existing scorecard is `final_review_scorecard_v1` and uses three categories: `Selection Gate`, `Evidence Packet`, `Review Burden`.
- Current non-block Level2 REVIEW mostly affects `Review Burden`; this is too weak for final portfolio selection.
- New scoring should keep backward-compatible top-level fields where possible.
- Completed read model keeps backward-compatible top-level scorecard fields while adding weighted dimensions, REVIEW impacts, score limits, cap state, selection rationale, and required decision notes.
- Level2 REVIEW is consumed as final judgment evidence and Monitoring handoff context. It is not rerun by Final Review.
- React remains presentation-only: it renders Python-owned report props and does not calculate gates, fetch providers / DB, or write registry / saved JSONL.
