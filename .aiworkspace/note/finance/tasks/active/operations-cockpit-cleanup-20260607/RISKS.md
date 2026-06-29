# Risks

- Browser QA may show existing Streamlit static resource 404 messages; treat as residual only if the page renders and navigation content is correct.
- This 1차 cleanup intentionally does not implement portfolio-first summary counters, scenario freshness, next review date, or evidence health mini strip.
- Browser QA observed Streamlit static resource 404s for `/operations/_stcore/health` and `/operations/_stcore/host-config`; page title, DOM checks, and screenshot rendered correctly, so this remains a residual Streamlit routing artifact rather than a blocker for this cleanup.
