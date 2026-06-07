# Reference Drift Guard / QA Polish V5 Risks

Status: Active
Date: 2026-06-08

## Risks

- Browser QA showed existing Streamlit `_stcore` console noise when direct route paths were opened, but content rendering and contextual help text were verified.
- In-app browser screenshot capture timed out; the QA image was captured through the fallback Playwright QA session after the DOM checks passed.
- Drift report only guards curated contextual help catalog alignment; it does not verify every markdown section in `GLOSSARY.md`.
