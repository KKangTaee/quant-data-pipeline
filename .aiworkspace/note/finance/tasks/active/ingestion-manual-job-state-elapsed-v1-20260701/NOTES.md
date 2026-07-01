# Notes

## Behavior

- Native `st.tabs` was replaced because tab selection is not a stable product state when the page reruns for job scheduling.
- The selector now stores the selected section in `st.session_state.ingestion_collection_section_choice`.
- `_schedule_job` infers whether the job belongs to the operational or manual collection section, stores that section on the job, stores it in `run_metadata`, records `ui_started_at`, and requests a rerun.
- During rerun, the selector can force the section from pending/running job state before rendering the controls.

## QA Boundary

- The real financial statement ingestion button was not clicked during Browser QA because that would fetch/store EDGAR statement data.
- Browser QA verified the no-data-side-effect flow: select `수동 복구 / 진단`, confirm the manual card list appears, confirm no Traceback, and capture a screenshot.
- Elapsed time rendering is covered by focused source contract tests and py_compile; a live elapsed progress run would require starting a real ingestion job.
