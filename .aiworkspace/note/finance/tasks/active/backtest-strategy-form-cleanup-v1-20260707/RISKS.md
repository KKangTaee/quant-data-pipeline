# Risks

- Removing the overbuilt panel must not regress the existing strategy-change result clearing behavior.
- Strict preset helper copy is shared by Single Strategy and Portfolio Mix Builder; wording changes should stay generic enough for both.
- Browser QA should verify that the strict Price Freshness Preflight still renders after the panel removal.
- Remaining risk: future UX polish could accidentally reintroduce a broad strategy detail surface. Keep Strategy dropdown / form switching in Streamlit unless a later task explicitly approves a deeper migration.
