# Practical Validation Service Boundary Risks

## Open Risks

- Practical Validation diagnostic builder is large and still lives under `app/web`; moving it wholesale requires a separate slice with broader compile and app QA.
- Provider gap collection still mixes UI, job execution, and run-history append. This task does not change that yet.
- DB-backed replay and provider loader QA may depend on local DB state; first slice should use compile / import smoke and no-Streamlit boundary checks.

## Closed In This Slice

- The Practical Validation helper no longer imports Streamlit.
- Source/result append and handoff contracts no longer live in the helper module.
