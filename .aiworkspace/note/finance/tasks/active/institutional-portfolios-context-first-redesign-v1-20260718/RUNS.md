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
