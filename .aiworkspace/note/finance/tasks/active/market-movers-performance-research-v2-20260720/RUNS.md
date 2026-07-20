# Runs

## 2026-07-20

- group snapshot DB timing: sector daily 0.660s, weekly 1.991s, monthly 8.474s; industry daily 0.467s, weekly 1.726s, monthly 8.674s.
- actual Browser cold entry: 약 46초까지 재현.
- selected research DB timing: TER 0.862s, COHR 0.855s.
- monthly sector query profiling: total 8.206s / 9 queries; market-date aggregation 8.062s.
- 사용자 승인: 이전 권장안 전체 + 현재/갱신 시각 + manual refresh + semantic return color.
- Task 1 RED: lazy breadth/reuse와 request event 테스트 `2 failed` 확인.
- Task 1 GREEN: focused event tests `3 passed`; 전체 decision UI tests `12 passed`.
- Python compile 통과; Vite production build `170 modules transformed`.
- Task 2 RED: timing/action payload와 grouped breadth/return tone source contract `2 failed` 확인.
- Task 2 GREEN: focused tests `2 passed`; 전체 decision UI tests `14 passed`.
- Task 2 Vite production build `170 modules transformed`.
- Task 3 RED: 10년 financial history와 hover/chart-mode/resize source contract `2 failed` 확인.
- Task 3 GREEN: research + decision UI tests `21 passed`.
- Task 3 Vite production build `170 modules transformed`.
- Task 4 RED: DB filing evidence, explicit news/SEC action, selected-symbol session 테스트 `3 failed` 확인.
- Task 4 GREEN: focused tests `3 passed`; research + decision UI tests `24 passed`.
- Task 4 Vite production build `170 modules transformed`.
- DB filing ledger는 한 번만 조회해 collection status와 compact evidence가 함께 재사용하도록 구성.
- 통합 검증: research/decision UI `24 passed`; Market Movers service contracts `126 passed`; `py_compile`, `git diff --check`, Vite production build 통과.
- stale QA server는 `runOnSave=false`로 이전 코드를 유지하고 있어 8530 QA instance만 현재 코드로 재시작했다.
- actual Browser cold entry `1.593s`; Top Rank 선택은 click return `0.272s`, selected state 확인 `0.995s`; industry daily 전환 `1.270s`.
- price hover `2026-05-12 / +72.77% / $358.31`, quarterly financial 39 points, bar/line toggle, DB filing 5 rows, explicit news/SEC actions를 actual data로 확인.
- desktop/760px responsive, nested iframe detail interaction, browser console error 0건 확인. QA screenshot `market-movers-performance-research-v2-desktop-qa.png`는 generated artifact로 commit 제외.
- independent review: Critical 0, Important 4, Minor 2. PIT future-filing filter, cached DB read invalidation, stored effective market date, filing error/source rendering, breadth semantic color, reload timestamp 의미를 모두 보정했다.
- review follow-up GREEN: research/decision `27 passed`; Market Movers service contracts `126 passed`; Vite production build `170 modules transformed`; fresh Browser session entry/market date/error log 0건 확인.
