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

## 2026-07-18 Reviewer Follow-Up: 420px Interaction QA

- Separate Streamlit server: port `8519`; stopped after QA. Browser viewport override was reset and the QA tab was finalized.
- Requested viewport `420 × 900`에서 primary `종목 분석` 탭과 secondary `종목 상세` / `기관 보유 랭킹` 탭을 실제 클릭해 전환했다. 랭킹 화면의 `기관 보유 랭킹 불러오기` action도 노출됨을 확인했다.
- `포트폴리오 > 전체 보유`로 돌아와 mapping filter `ticker 미연결 / mapping 확인 필요`를 선택했다. Berkshire 결과는 `1–10 / 10`이며 10개 row 모두 `ticker 연결 전`으로 표시됐다.
- 미연결 `CONSTELLATION BRANDS INC` row를 선택해 `CUSIP 21036P108 · Unmapped` identity notice와 `ticker가 안전하게 연결되기 전에는 종목 차트나 가격 수집을 열지 않습니다.` 안내를 확인했다. `.ip-price-action`과 `.ip-security-detail`은 모두 `0`개였다.
- mapping filter를 `ticker 연결됨`으로 전환하고 holdings search에 `AAPL`을 입력해 `1–1 / 1`을 확인했다. AAPL row 선택 후 종목 상세, CUSIP `037833100`, 포트폴리오 비중 `22.0%`, 보고 평가액 `57.8B`, 보유 기관 `100`, interactive chart가 노출됐다.
- Mobile interaction screenshot: `.playwright-mcp/institutional-portfolios-context-first-v2-mobile-interaction.png` (not staged).

## 2026-07-18 Final Review Fix Wave

- Root-cause RED: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py -k 'outside_selected_portfolio or outside_portfolio or preserves_curated_live_context_when_search_has_no_results'` -> 3 expected failures: builder returned `empty`, loader made no price call, zero-result resolver returned `None`.
- Python GREEN: the same focused command -> `3 passed`; final required command `uv run --with pytest pytest -q tests/test_institutional_portfolios.py` -> `51 passed`, `2 subtests passed`, 3 dependency deprecation warnings.
- Frontend RED: initial `npm test -- --reporter=verbose` failed because the new helper module was absent; after adding explicit stubs it produced 4 expected `not implemented` failures. The cleared-query case separately failed `expected false to be true`.
- Frontend GREEN: `npm test -- --reporter=verbose` -> `5 passed`; `npm run typecheck` -> PASS; `npm run build` -> PASS, 171 modules transformed; `npm audit --json` -> 0 vulnerabilities after Vitest 4 alignment.
- Runtime contract: tracked `component_static` bundle rebuilt; source and runtime scans found no `slice(0,80)` / `slice(0, 80)`.
- Browser QA on port `8524`: lowercase `nvda` outside Berkshire resolved to NVIDIA / CUSIP `67066G104`, DB chart, 100 holders, unavailable selected-manager position and an enabled search action after response. `zzzz-no-manager-qa` showed an explicit 0-result state while retaining the live Berkshire hero. Bridgewater unresolved top holding activation opened `전체 보유`, `1–50 / 993`, CUSIP `78462F103`, and the no-price-action notice.
- QA screenshot: `.playwright-mcp/institutional-portfolios-final-review-fixes.png` (generated, ignored, not staged). Browser tab finalized and port `8524` server stopped.
- Earlier `git diff --check` records in this file were working-tree checks only. After commit `3b64f77f`, the exact requested range `git diff --check 229422290f5e33638b21932e72cd4dee8f7b7b85..HEAD` passed with no output after removing the plan EOF blank line.

## 2026-07-18 Final Re-review Hardening

- Focused RED: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py -k 'ambiguous_interest_identities or exact_symbol_or_cusip_resolves or generic_live_context_when_search_has_no_results'` -> 4 failures reproduced arbitrary identity promotion, ambiguous price loading, wrong exact-CUSIP resolution, and loss of a non-watchlist selected CIK; one subtest passed.
- Focused GREEN: the same command -> `4 passed`, `51 deselected`, `2 subtests passed`, 3 dependency deprecation warnings.
- Full Python verification: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py` -> `55 passed`, `4 subtests passed`, 3 dependency deprecation warnings; `.venv/bin/python -m py_compile app/services/institutional_portfolios.py app/web/institutional_portfolios.py` -> PASS.
- Full frontend verification: `npm test -- --reporter=verbose` -> `5 passed`; `npm run typecheck` -> PASS; `npm run build` -> PASS, 171 modules transformed; `npm audit --json` -> 0 vulnerabilities.
- The frontend source was unchanged in this follow-up; rebuilding produced no tracked `component_static` diff. Source and tracked runtime scans still contain no `slice(0,80)` / `slice(0, 80)` limit.

## 2026-07-18 Hero Layout Alignment Follow-Up

- Focused RED: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py::InstitutionalPortfoliosNavigationTests::test_context_hero_basis_and_controls_share_alignment_contract` -> expected failure because `ip-context-basis__snapshot` was absent.
- Focused GREEN: the same command -> `1 passed`.
- Full Python: `uv run --with pytest pytest -q tests/test_institutional_portfolios.py` -> `56 passed`, `4 subtests passed`, 3 existing Edgar dependency deprecation warnings.
- Frontend: `npm test -- --reporter=verbose` -> `5 passed`; `npm run typecheck` -> PASS; `npm run build` -> PASS, 171 modules transformed.
- Tracked runtime: `component_static/index.html` points to `index-DHuSgLHe.js` and `index-Dcz2GNfw.css`; built assets contain `--ip-context-columns`, `ip-freshness-block`, and no `slice(0,80)` / `slice(0, 80)` path.
- Browser QA used actual Berkshire hero data and the actual Appaloosa manager rail entry on a separate Streamlit server at port `8526`; the server was stopped, the viewport override reset, and the QA tab finalized. Browser error / warning log was empty.
- Desktop component width `1139px`: hero and controls both computed `703.452px 363.864px`; context copy / manager switcher left was `26.889px`; basis / freshness block was `748.338px..1112.202px`; search input / freshness panel top was `273.707px`; snapshot computed `grid-column: 1 / -1`; collected-time `clientWidth == scrollWidth == 342px`.
- Exact `420 × 900` viewport: page `clientWidth == scrollWidth == 420px`; iframe and component document `clientWidth == scrollWidth == 378px`; hero and controls each computed one `332.415px` column; freshness action / period / time each had `clientWidth == scrollWidth == 311px`.
- Final ignored PNG screenshot: `.playwright-mcp/institutional-portfolios-hero-layout-alignment-final.png`.
- `git diff --check` -> PASS.

## 2026-07-18 Hero Layout Contract Review Fix

- Strengthened the focused regression to bind shared columns / 18px gap to both exact desktop selectors, `align-items: start` to controls, the full-width basis selectors to `grid-column: 1 / -1`, the complete shared label typography / bottom-gap declarations to both labels, and freshness grid areas to desktop and `<=720px` scopes.
- Extended the same contract to resolve the CSS / JS paths referenced by tracked `component_static/index.html`, inspect those exact assets for layout / label markers, and reject `slice(0,80)` / `slice(0, 80)` in referenced JS.
- Mutation RED: temporarily changed only `.ip-context-controls` from `gap: 18px` to `gap: 12px`; the focused test failed at the selector-specific `gap: 18px` assertion with the controls rule body in the failure output.
- Restored the exact CSS with `apply_patch`; focused GREEN -> `1 passed`. Production source and tracked assets matched `HEAD` immediately after restore and again after Vite build.
- Full checks: Python `56 passed`, `4 subtests passed`, 3 existing Edgar dependency deprecation warnings; Vitest `5 passed`; typecheck PASS; Vite build PASS with 171 modules; `git diff --check` PASS.
- Browser QA was not rerun because no production or tracked runtime byte changed. Source / index / JS / CSS SHA-256 remained `462c858a...`, `2b31c53f...`, `62976028...`, `28998f7a...`, and `94e839cf...` respectively.

## 2026-07-18 Freshness Binding Contract Final Review

- Added exact source assertions for `.ip-freshness__action { grid-area: action; }`, `.ip-freshness strong { grid-area: period; }`, and `.ip-freshness em { grid-area: time; white-space: normal; }`.
- Referenced minified runtime CSS is now parsed by exact selector. The regression protects the shared token declaration / use, both 18px grid gaps, basis full-span, action / period / time bindings, desktop freshness areas, and `<=720px` mobile ordering.
- Mutation RED: temporarily changed only `.ip-freshness em` from `grid-area: time` to `grid-area: auto`; focused test failed at the source selector assertion and printed the mutated rule body. Restored with `apply_patch`; focused GREEN -> `1 passed`.
- Marked all eight steps complete in `LAYOUT_ALIGNMENT_IMPLEMENTATION_PLAN.md`; automated count confirmed `8/8` checked and no unchecked Task 1 step remains.
- Final checks: Python `56 passed`, `4 subtests passed`, 3 existing Edgar dependency warnings; Vitest `5 passed`; typecheck PASS; Vite build PASS with 171 modules; `git diff --check` and focused source/runtime contract PASS.
- Browser QA was not rerun because production TSX / CSS and tracked index / JS / CSS remained byte-identical after build with the previously recorded five SHA-256 values.

## 2026-07-18 Manager Rail Visibility Follow-Up

- Root-cause RED: the new `test_manager_rail_shows_complete_cards_and_wraps_labels` failed because `.ip-manager-rail` still used `display: flex`; the first draft also exposed that the tablet media rule was absent. The test order was tightened before production edits so the direct flex failure appeared first.
- Source CSS GREEN changed only the manager rail presentation contract: desktop `4`, tablet `3`, mobile `1` complete-card grid columns; mandatory horizontal snap; natural alias / filer-name wrapping; effective `12px` bottom margin and `10px` scrollbar spacing. React markup, manager payload, CIK events, DB, provider, and ingestion were unchanged.
- Intermediate verification failed only on the intentionally stale tracked runtime after the source CSS passed. Vite rebuilt `component_static` with 171 modules, then the focused source/runtime test passed.
- Automated verification: full Python `57 passed`, `4 subtests passed`, 3 existing Edgar dependency warnings; Vitest `5 passed`; TypeScript typecheck PASS; Vite build PASS; `git diff --check` PASS.
- Actual Browser QA used dedicated Streamlit port `8527`, then stopped the server, reset the viewport, and finalized the in-app Browser tab. Browser error / warning log was empty.
- Desktop `2048 × 1000`: component document `1877px`, rail `1190px`, four cards `291.406px` plus three `8px` gaps, fifth-card visible width `0px`; `white-space: normal`, `text-overflow: clip`, and content `scrollWidth == clientWidth` were confirmed.
- Tablet `900 × 1000`: component document `729px`, rail `675px`, three cards `219.656px` plus two `8px` gaps, fourth-card visible width `0px`; page / component horizontal overflow was `0px`.
- Mobile `420 × 900`: component document `377px`, rail / card `331px`, second-card visible width `0px`; page / component horizontal overflow was `0px` and long filer metadata wrapped without inner overflow.
- Horizontal scroll settled at `299px` for a `299.406px` card step, a `0.406px` rounding error. The visible Stanley Druckenmiller card selected CIK `0001536411`, updated the hero to `Duquesne Family Office LLC`, and preserved the snapped rail position.
- Final ignored screenshot: `.playwright-mcp/institutional-portfolios-manager-rail-visibility-final.png`.
