# Institutional Holdings React Parity V1 Runs

## 2026-07-25 Diagnosis

- Reviewed finance docs, current Institutional Holdings tasks, Today / Market Research task records, Python page wrappers and React component sources.
- Started a dedicated local Streamlit server on port `8528`.
- Inspected actual Institutional Holdings, Today and Market Research at desktop and 420px.
- Confirmed Holdings functionality and data flow are healthy; the identified gap is page ownership, hierarchy, visual tokens and responsive first-read.
- Institutional and Market Research console review returned no error / warning. A temporary `/today` route probe produced the expected Streamlit page-not-found fallback before the valid root Today route was used; it is not a Today product regression.
- Browser tabs were finalized, viewport override reset and the dedicated server stopped.

## 2026-07-25 Design

- Created the active task shell and written React parity design.
- Visual Companion rendered three one-shot directions using the same Berkshire manager context and existing feature set.
- Terminal feedback is the primary selection record: the user replaced B with `C · Modular Research Studio`.
- Updated the written design for desktop research rail / main canvas and tablet/mobile studio switcher / drawer.
- No implementation code, registry, saved setup or generated artifact was changed.

## 2026-07-25 Implementation

- Added `InstitutionalStudioShell.tsx`, canonical studio destination state and focused React navigation tests.
- Reworked the workbench into a desktop research rail / main canvas and a 980px 이하 top switcher / drawer while preserving allocation, holdings, security chart, popularity and caveats.
- Moved SEC refresh inputs/result into React and added the explicit Python `collect_sec_13f_dataset` event handler.
- Limited the legacy Streamlit title/help/refresh/table surface to React-unavailable fallback.
- Rebuilt the tracked `component_static` bundle.

## 2026-07-25 Verification

- `npm test -- --run`: 7 passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `.venv/bin/python -m unittest tests.test_institutional_portfolios`: 58 passed.
- `.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py`: passed.
- `git diff --check`: passed.
- Browser actual DB QA: Berkshire desktop, Bridgewater manager search, AAPL selected-security chart, Bridgewater unresolved CUSIP guardrail, 1280/760/420 rendering and mobile drawer passed; console error/warning 0.
- QA screenshot: `institutional-holdings-research-studio-desktop-qa.png` (generated artifact, not staged).
