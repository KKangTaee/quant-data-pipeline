# Reference Center React V1 Risks

## Open Validation Gap

- The repository does not have one isolated automated test that boots Streamlit multipage navigation and asserts browser history. Pure route/event tests plus actual Browser QA cover the current contract; future navigation-shell changes should repeat that Browser QA.

## Ongoing Maintenance Risk

- The catalog is intentionally curated rather than generated from `GLOSSARY.md`. A newly renamed product surface can drift unless its Reference item, contextual help ID, and current-surface guard are updated together.

## Closed Risks

- Invalid destinations are rejected before `st.switch_page`.
- Legacy Guides/Glossary paths are removed only after the new page and contextual links passed tests.
- Modal-open iframe height fills the parent viewport's available height without an arbitrary upper cap, recomputes on resize, stays aligned below navigation, and keeps the persistent footer independent of body scroll position.
- Internal durable `GLOSSARY.md`, registries, saved setups, and generated/user artifacts were not rewritten or deleted.
