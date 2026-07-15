# Overview Market Context US Stock Turnaround Analysis V1 Status

Last Updated: 2026-07-15

## Current Stage

- 전체 roadmap: 1차~5차
- 현재: 3차 Loader · Service · Collection 완료, 4차 내부 selector와 UI 착수 전
- 구현 완료 차수: 3/5

## Completed

- 기존 미국 개별주 PER task와 Market Context service/React 경계를 재검토했다.
- 내부 `PER 상대가치 | 전환 분석` selector 방향과 negative-EPS default routing을 승인받았다.
- RIVN/LCID/PLTR/AMD/AAPL raw SEC concept coverage를 actual DB에서 read-only로 확인했다.
- operating milestone과 survival risk를 분리하고, cumulative SEC duration fact resolver와 EV freshness gate를 authoritative design에 고정했다.
- 기존 calculator/loader/service/job/Streamlit/React/test 소유 경계와 설계 커밋 이후 코드 차이 없음(HEAD=`067cc954`)을 확인했다.
- `PLAN.md`를 파일·interface·RED/GREEN·검증·커밋 단위의 1차~5차 상세 계획으로 확장했다.
- 1차: direct Q, H1-Q1, 9M-H1, FY-Q1-Q2-Q3 resolver와 primary comparative non-overwrite, derived available-at provenance를 구현했다.
- 1차: instant/duration 분리와 as-of 이후 split을 소급하지 않는 split-neutral diluted-share series를 구현했다.
- 1차 focused/regression 48 tests, target py_compile, `git diff --check`를 통과했다.
- 2차: canonical SEC concept family, gap-preserving quarter timeline, TTM/YoY/margin/FCF series와 instant balance를 구현했다.
- 2차: operating/cash/earnings/PER milestone과 runway/interest/net-debt/dilution risk를 서로 독립된 근거로 분류했다.
- 2차: P/E handoff, P/FCF, P/OCF, EV/EBITDA, EV/Gross Profit, EV/Sales valuation routing과 stale/unit/alignment/sector 차단 경계를 구현했다.
- 2차 focused/regression 67 tests, target py_compile, `git diff --check`를 통과했다.
- 3차: 한 ticker·최대 7 fiscal years·as-of cutoff로 duration/instant/profile/price 조회를 제한하는 DB-only loader와 exact gap preflight를 구현했다.
- 3차: JSON-safe turnaround service와 S&P/PER/turnaround 독립 격리, positive READY PER 기준 `recommended_analysis`를 구현했다.
- 3차: selected profile/price/SEC 동기 수집, CIK 선검증, partial-success 보존, retry scope 축소, explicit Streamlit event를 구현했다.
- 3차 turnaround/PER/Market Context 회귀 92 tests와 target py_compile을 통과했다.

## Next Action

- 4차 React source/contract RED부터 시작한다.
- 이어서 symbol-keyed 내부 selector, milestone/charts/risk/valuation UI와 420px responsive layout을 구현한다.

## Not Started

- external collection
- DB/schema changes
- Browser QA
