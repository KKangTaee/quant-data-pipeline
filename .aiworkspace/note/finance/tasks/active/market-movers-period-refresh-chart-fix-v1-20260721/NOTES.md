# Notes

## Root Cause

- 비-Daily refresh 목표일이 coverage-qualified 랭킹 기준일에 묶여 최신 완료 시장일까지 전진하지 못했다.
- 과거 limited-history 분류는 선택 기간 경계보다 lifetime row count를 우선해 stale 신규 종목의 재수집을 막았다.
- 수집 호출은 필요한 기간보다 넓었고, component tooltip은 항상 위로 펼쳐져 고점에서 잘렸다.
- 가격 차트는 시작/종료 두 날짜만 표시해 중간 위치를 판독하기 어려웠다.

## Decisions

- refresh target은 `latest_completed_nyse_session()`이며 랭킹 기준일과 분리한다.
- Weekly fetch window는 `[as_of-2주, as_of]`, required return window는 `[as_of-1주, as_of]`다.
- Monthly fetch window는 calendar-safe `[as_of-2개월, as_of]`, required return window는 `[as_of-1개월, as_of]`다.
- provider adapter가 inclusive end 보정을 소유하므로 Overview job은 `as_of`를 한 번만 넘긴다.
- 첫 가격일이 required start 뒤인 현재 종목은 기간 전체 수익률로 합성하지 않는다.
- tooltip은 plot y가 92보다 작으면 point 아래로 펼치고, 긴 재무 차트에서는 현재 scroll viewport 좌우 72px 안에 고정한다.

## Actual Observation

- bounded window는 provider payload 기간을 줄였지만 503개 symbol fetch 자체는 유지되어 실제 주간 보강에 138.11초가 걸렸다.
- 수집 후 주간 coverage 503/503, 랭킹 기준일 2026-07-20, 다음 preflight는 503개 전부 current skip 상태였다.
