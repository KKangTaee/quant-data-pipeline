# Overview Market Context US Stock Turnaround Analysis V1 Status

Last Updated: 2026-07-15

## Current Stage

- 전체 roadmap: 1차~5차
- 현재: 5차 Actual QA · Docs · Final Verification 완료
- 구현 완료 차수: 5/5

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
- 4차: 선택 종목에만 `PER 상대가치 | 전환 분석` selector를 추가하고 symbol별 로컬 선택과 service 추천 기본값을 연결했다.
- 4차: milestone rail, shared 8/12/20분기 Graph 1/2, 결측 단절, 0축, inspector, runway/debt/dilution, valuation reason card를 구현했다.
- 4차: 420px risk/selector/card one-column responsive CSS와 새 `component_static` production bundle을 생성했다.
- 4차 S&P/PER/turnaround 회귀 95 tests와 Vite production build를 통과했다.
- 5차: actual DB에서 RIVN `17/18`, LCID `23/24`, PLTR `21/22` quarter slot을 확인했고 각각 `OPERATING_IMPROVEMENT`, `LOSS_BASELINE`, `CASH_FLOW_TURN`으로 전환 분석 READY를 표시했다.
- 5차: AMD/AAPL은 기존 PER payload를 바꾸지 않고 `recommended_analysis=per`, Graph 1 READY, current P/E `169.2164x` / `39.3241x`를 유지했다.
- 5차: SEC CIK가 비어 있어 수집을 실행할 수 없는 경우 collection plan을 `BLOCKED/CIK_MISSING`으로 두되 이미 READY인 분석을 ERROR로 덮지 않도록 TDD 회귀를 추가했다.
- 5차: focused 96 tests를 통과했고, 24개 test module 격리 전체 회귀는 1,073/1,077 통과했다. 실패 4건은 이전부터 존재한 Practical Validation 2건, Market Movers 1건, Sentiment 1건이다.
- 5차: actual Streamlit desktop에서 RIVN/LCID/PLTR 전환 분석, AMD/AAPL PER handoff와 selector 전환을 확인했다. 420px iframe/body/outer overflow는 모두 0px, browser console error는 0건이다.
- 5차: external collection, DB/schema 변경, registry/saved write는 실행하지 않았다.

## Next Action

- V1의 필수 후속은 없다. 다음 확장은 별도 승인 범위로 all-stock turnaround discovery/ranking, peer-relative valuation, historical enterprise-value snapshot 중 하나를 선택한다.
- 실제 원자료 보강이 필요하면 먼저 symbol lifecycle에 SEC CIK를 연결한 뒤 선택 종목의 명시 수집 action으로만 실행한다.

## Remaining Boundaries

- 전환 단계는 독립 evidence 요약이며 매수/매도 신호가 아니다.
- read-time latency는 actual DB 기준 약 `1.7s~7.2s`였고, universe-wide discovery에는 별도 materialization/performance 설계가 필요하다.
- 저장소 전체 회귀의 기존 unrelated 4 failures는 이 task 범위에서 수정하지 않았다.
