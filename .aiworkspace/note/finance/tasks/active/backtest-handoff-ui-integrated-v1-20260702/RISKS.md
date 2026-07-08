# Backtest Handoff UI Integrated V1 Risks

## Remaining Follow-Up

- Gate semantics are still duplicated conceptually: `promotion_decision` already aggregates some policy checks, while handoff readiness also displays execution / validation source checks. V1 did not change this to avoid changing stage behavior during UI polish.
- `_build_next_step_readiness_evaluation` still lives in `app/web/backtest_result_display.py` and is imported by compare UI. V2 should move this to a Streamlit-free service/read model before deeper policy cleanup.
- `Policy Signal Meta` still repeats lower-level policy metadata. V2/V3 should decide whether it is debug evidence, source provenance, or user-facing gate detail.
