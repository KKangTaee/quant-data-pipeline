# Reference Center React V1 Runs

## 2026-07-20 Design And Planning

- Re-audited finance docs, legacy Reference/Glossary implementation, contextual help, current product surfaces, and existing React component conventions.
- Verified the existing 14 Reference tests before implementation.
- Compared three information architecture options; user approved Search-first Hybrid A and the nine-task TDD plan.

## 2026-07-20 TDD Implementation

- Task 1 RED: missing `app.services.reference_center`; GREEN: catalog schema, lookup, drift, relation, destination tests passed.
- Task 2 RED: missing navigation helpers; GREEN: deep-link/event/page-target routing tests passed.
- Task 3-5: ranked local search, React workbench, production build, JSON-safe bridge, and Streamlit page shell completed.
- Task 6-8: single Reference navigation, seven-surface contextual help, and legacy renderer/catalog deletion completed.
- Browser-discovered frame regression RED: `setFrameHeight(760)` expectation failed with two auto-height calls. GREEN: component test 6 passed; modal-open frame cap and internal drawer scroll verified in browser.

## 2026-07-20 Automated Verification

From repository root:

```bash
git diff --check
.venv/bin/python -m unittest tests/test_reference_center.py tests/test_reference_center_component.py tests/test_reference_contextual_help.py
.venv/bin/python -m compileall -q app/services app/web
```

- Result: focused Python `28 passed`; compileall and diff check passed.

From `app/web/streamlit_components/reference_center_workbench`:

```bash
npm test
npm run typecheck
npm run build
```

- Result: Vitest `2 files / 11 tests passed`; TypeScript and Vite production build passed.

Combined Reference and navigation-owner regression:

```bash
.venv/bin/python -m unittest \
  tests/test_reference_center.py \
  tests/test_reference_center_component.py \
  tests/test_reference_contextual_help.py \
  tests/test_portfolio_monitoring_page.py \
  tests/test_ingestion_module_split_contracts.py \
  tests/test_institutional_portfolios.py
```

- Initial combined run exposed test isolation drift: two Streamlit-free import-contract tests removed the already loaded `streamlit` module without restoring it, so later UI tests hit Streamlit's singleton re-import guard.
- After restoring the prior module in each test's `finally` block, the combined run passed: `102 tests passed`; bare-Streamlit context warnings only, no failures.

## 2026-07-20 Browser QA

- The `.venv/bin/streamlit` entrypoint had a stale worktree shebang, so the verified server command was:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.headless true --server.port 8517
```

- Desktop: one Reference navigation entry, search-first order, six journey cards, `NOT_RUN` search/detail, local filter and related-item navigation, explicit close, valid/invalid deep links, and drawer internal scroll passed.
- Product navigation: `NOT_RUN` destination opened `/backtest` at Practical Validation. Overview contextual help opened `feature.market_context`; browser back returned to Overview.
- 900px: journey grid computed as two columns and drawer had no horizontal overflow.
- 420px: journey grid computed as one column; detail rendered as full-width 88vh sheet with no horizontal overflow and explicit close worked.
- Browser console: no new error/warning entries.
- Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/reference-center-react-v1-qa.png` (generated, unstaged).

## 2026-07-20 Integration Review

- Independent code review found no critical product defect and confirmed focused Python, React, typecheck, and diff-check results.
- The review found two stale canonical documents that still described deleted Guides / Glossary modules and routes.
- `docs/architecture/SCRIPT_STRUCTURE_MAP.md` and `docs/flows/BACKTEST_UI_FLOW.md` were aligned to the curated catalog, React workbench, single `/reference` route, seven contextual surfaces, read-only boundary, and legacy-removal decision.

## 2026-07-20 PC Detail Footer Follow-up

- Reproduced at `1400×768`: the fixed `760px` iframe ignored the Streamlit navigation/viewport boundary, and the destination action remained below the scroll fold.
- TDD RED: expected viewport-derived `672px` frame and persistent `.reference-detail__footer`; existing code returned `760px` and had no footer. A second RED reproduced retained parent scroll (`140`) instead of navigation-aligned scroll (`64`).
- GREEN: frame height now uses parent viewport minus 80px navigation clearance and 16px bottom gap, bounded to 520~760px. The component aligns under navigation and separates fixed header/footer from the scrollable body.
- React result: `2 files / 13 tests passed`; TypeScript typecheck and Vite production build passed.
- Browser result: `1400×900` frame `top=80, bottom=840, height=760`; `1400×768` frame `top=80, bottom=752, height=672`; footer visible in both. `420×844` remained full-width with `scrollWidth == clientWidth == 377` and visible footer.
- Browser console: no error/warning entries.
- Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/reference-center-pc-bottom-fix-qa.png` (generated, unstaged).
