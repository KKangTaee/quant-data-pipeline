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
