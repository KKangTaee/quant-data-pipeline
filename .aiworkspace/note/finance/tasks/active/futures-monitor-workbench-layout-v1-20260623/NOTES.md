# Futures Monitor Workbench Layout V1 Notes

## Decisions

- Use current DB-backed read models only.
- Keep existing control semantics and session keys.
- Use helper models to make TDD possible without full Streamlit rendering.
- Do not add diagnostic/job panels as the product improvement.
- Browser QA showed the remaining prototype-like element was the large symbol multiselect. V1 therefore keeps the same selection capability but moves it behind `관찰 대상 편집` and renders the selected symbols as a read-only watch strip.
- The watch strip intentionally shows symbol state, 15m/60m move, and age only. Provider run rows and job success/row counts stay in diagnostics.
