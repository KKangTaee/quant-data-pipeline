# Phase 14 Second-Cycle Prioritization Design

Status: Active
Created: 2026-05-30

## Design Principle

Phase 14 is a decision and handoff phase.
It should prevent the second cycle from becoming a grab bag of unrelated improvements.

The work should rank carry-forward candidates by:

- investability impact
- dependency readiness
- implementation effort
- source uncertainty
- storage boundary risk
- QA / service contract testability
- fit with current Backtest -> Practical Validation -> Final Review -> Selected Dashboard flow

## Candidate Groups

| Group | Candidate examples | Likely handling |
| --- | --- | --- |
| Immediately implementable workflow hardening | selected replay contract, weighted mix cost / turnover, profile thresholds | prioritize and open implementation task |
| Data-source dependent hardening | historical membership coverage, lifecycle actual coverage scoring v2 | run source review / DB pipeline design first |
| Research-before-build topics | broker-grade execution realism, production monitoring design | product research or design task before implementation |
| Lower-priority policy implementation | structured waiver implementation | defer unless user asks for review workflow |

## Expected Output

- `phase14-candidate-prioritization-v1` task with a ranked matrix.
- First implementation slice design with owner skill and verification criteria.
- Roadmap / index / root log updates showing the selected next step.

## Boundaries

- Phase 14 does not implement runtime logic.
- Phase 14 does not create new user memo, preset, closeout comment, or monitoring-log auto-write persistence.
- DB-backed data collection is allowed only after a later scoped DB pipeline task.
- Trading automation remains out of scope.
