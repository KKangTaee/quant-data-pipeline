# Risks

- Browser QA did not execute the real EDGAR financial statement ingestion job to avoid writing data during UI verification.
- Elapsed time display is verified by focused code-path tests and compile checks, not by a live long-running ingestion run.
- Streamlit direct navigation to `/ingestion` still shows the app fallback dialog before rendering the page. This was pre-existing route behavior and outside this task.
