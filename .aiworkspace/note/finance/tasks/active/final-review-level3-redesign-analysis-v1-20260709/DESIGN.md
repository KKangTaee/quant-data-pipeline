# Design Direction Draft

## Working Interpretation

`Final Review / Level3` should be the last Backtest decision stage before Operations monitoring. It should not rerun Practical Validation or repair data. It should translate saved evidence into a final investment review: recommendation, reason, strengths, weaknesses, scenario fit, expected risk/result range, benchmark or alternative rationale, open review disposition, and monitoring handoff conditions.

## Current Boundary

- React / UI components may present cards, boards, controls, and click intent only.
- Python services own read-model synthesis, scoring, REVIEW role interpretation, save readiness, and final decision row construction.
- Runtime stores append Final Review decision records. Only records explicitly marked as Monitoring candidates should feed Portfolio Monitoring.
- Portfolio Monitoring reads selected decisions and saved dashboard setup separately.

## Proposed First Development Slice

Separate Final Review judgment persistence from Monitoring handoff.

- Final Review decision records can store `SELECT_FOR_PRACTICAL_PORTFOLIO`, `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, and `RE_REVIEW_REQUIRED`.
- Monitoring handoff remains narrower: only selected-route records that pass the selection gate become Monitoring candidates.
- The change is additive. Existing registry JSONL rows are not rewritten; new rows carry explicit handoff flags for read models.
- Streamlit should expose route choice and operator reasoning, but save/readiness logic remains in Python helper/service code.

## Deferred Slices

- Weakness improvement proposal and current-vs-improved comparison.
- Scenario-specific stress enhancement.
- Alternative strategy ranking workspace.
- Narrative investment-review scoring, if not required to unblock the persistence boundary.
