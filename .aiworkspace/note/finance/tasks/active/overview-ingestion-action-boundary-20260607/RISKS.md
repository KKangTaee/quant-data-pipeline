# Risks

Status: Complete
Last Updated: 2026-06-07

## Residual Risks

- This task changes the call boundary, not the collector internals.
- Browser route smoke should still be checked because Overview is a large Streamlit module.
- Ingestion diagnostic facade and Ingestion Console split remain follow-up work.
- Existing local run-history JSONL is generated state and should not be staged.
- `app/jobs/overview_automation.py` remains the scheduler / cadence owner; this task does not configure OS-level scheduling.
