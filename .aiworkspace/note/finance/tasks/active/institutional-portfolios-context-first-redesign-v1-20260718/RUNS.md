# Institutional Portfolios Context-First Redesign V1 Runs

## 2026-07-18 Audit

- Read canonical finance docs, Institutional Portfolios flow, recent task records, source-extension research, product audit checklist, and relevant code ownership.
- Inspected current `main-dev` Overview and Institutional Portfolios in a local Streamlit app.
- Compared Overview context-first header / navigation / evidence flow with the Institutional Portfolios manager rail / hero / panel flow.
- Inspected `app/web/institutional_portfolios.py`, `app/services/institutional_portfolios.py`, the React workbench, CSS, loader, and focused tests.
- Queried actual DB through existing read-only loaders for major curated managers.
- Confirmed current list limits and Bridgewater `993` logical holding case.

## 2026-07-18 Design Self-Review

- Reviewed the written spec for incomplete items, scope contradictions, ambiguous data ownership, and silent truncation.
- Chose the existing full holdings payload plus client-side fixed 50-row pagination for V1; no alternate server-side pagination contract remains ambiguous.
- Defined the context summary as deterministic formatting of concentration / sector / coverage / comparison fields.
- Confirmed the active task manifest and root handoff pointers refer to the new task.
- Confirmed the required six task documents are present.
- `git diff --check` and trailing-whitespace checks passed before final verification.

## 2026-07-18 Implementation Verification

- `uv run --with pytest pytest -q tests/test_institutional_portfolios.py` -> `46 passed`, `2 subtests passed`, 3 dependency deprecation warnings.
- `.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py` -> PASS.
- `npm run build --prefix app/web/streamlit_components/institutional_portfolios_workbench` -> PASS, 170 modules transformed.
- `git diff --check` -> PASS.

## 2026-07-18 Actual DB Smoke

- Existing `load_institutional_portfolio_model -> build_institutional_workbench_payload` path used for Berkshire, Bridgewater, and Duquesne.
- For every manager, `coverage.holding_count_total == len(holdings_explorer.rows)` and `default_page_size == 50`.
- Bridgewater: total `993`, explorer `993`, mapped `86`, mapped weight `21.0227%`, performance coverage `21.0228%`.
- All three actual snapshots have no previous comparable filing; `comparison_available=false` and change group count `0`.

## 2026-07-18 Browser QA

- Separate Streamlit server: port `8518`, stopped after QA.
- Desktop: context hero, compact manager search / rail, Bridgewater `1–50 / 993` and `51–100 / 993`, 20 pages, NVDA search, mapped/unmapped filter, unresolved identity notice, NVDA chart / 100 holders verified.
- 420px: hero and controls use one grid column; four holdings controls each use full available width; page and iframe document report no horizontal overflow.
- Final generated screenshot: `.playwright-mcp/institutional-portfolios-context-first-v2-final.png` (not staged).
