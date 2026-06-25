# Overview Tab Helper Extraction V11-V16 Risks

- `legacy_dashboard.py` still contains shared constants and lower-level helpers used by multiple tab helper groups. Do not delete broad helper clusters without direct usage checks.
- Streamlit UI helpers can be moved into tab helper modules, but service/data calculations must stay Streamlit-free and outside `app/web`.
- Browser QA screenshots are generated artifacts and should not be committed unless explicitly requested.

