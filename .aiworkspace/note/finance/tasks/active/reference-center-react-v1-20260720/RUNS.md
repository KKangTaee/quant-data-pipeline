# Reference Center React V1 Runs

## 2026-07-20 Design Run

- Read current finance docs, Reference research bundle, implementation, catalog, glossary parser, contextual help, tests, and representative React component patterns.
- Verified focused existing Reference tests: 14 passed.
- Inspected current HEAD Reference / Glossary at desktop and narrow viewport without changing product code.
- Compared three layout options in Visual Companion; user selected Search-first Hybrid A.
- Recorded user approvals for information architecture, component/data boundary, error handling, drift guard, and QA contract.

## 2026-07-20 Implementation Planning Run

- User approved the written `DESIGN.md` specification.
- Read the actual Streamlit page registration, contextual help routing, Backtest panel routing, and existing React component bridge/build conventions.
- Verified the installed Streamlit signatures support `query_params` for `st.page_link` and `st.switch_page`.
- Expanded `PLAN.md` into nine file-specific TDD tasks with RED/GREEN commands, commit boundaries, responsive Browser QA, and documentation closeout.
- The first verification exposed unavailable `pytest`; all plan commands were corrected to the repository's installed `unittest` runner, then the current 14 Reference tests passed.
- Product implementation remains `0/4차`; no app code or navigation changed in this run.
