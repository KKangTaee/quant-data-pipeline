# Streamlit Ingestion Console Split Risks

## Remaining Risks

- 7A is a physical Streamlit module split, not a full service/job diagnostic boundary extraction.
- `app/web/ingestion_console.py` is still large because the first step preserved behavior and avoided mixing extraction with redesign.
- Importing the Ingestion module in tests still loads Streamlit and ingestion dependencies; future 7B can move read-only diagnostic orchestration to Streamlit-free helpers.
- Browser QA initially showed a stale Page not found modal on the reused tab after server restart, but a fresh direct `/ingestion` tab loaded cleanly and the modal disappeared after closing.

## Mitigations

- Contract tests now prevent the top-level shell from silently taking Ingestion console ownership back.
- Runtime context is passed explicitly from the shell into the Ingestion entrypoint.
- Final verification includes boundary checker and Browser QA.
