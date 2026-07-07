# Backtest Symbol Resolver V1 Plan

## Goal

Backtest Quality / Value Factor Readiness에서 stale/missing price ticker가 단순 가격 누락인지, ticker change 가능성인지 공용으로 진단하고 사용자가 명시적으로 repair를 적용할 수 있게 한다.

## 이걸 하는 이유?

기존 흐름은 `BK` 같은 과거 ticker가 최신 가격을 반환하지 않을 때 같은 ticker로 가격 수집을 반복한다. 실제 사용자는 가격이 빠진 것인지 ticker가 바뀐 것인지 판단해야 하므로, Factor Readiness가 먼저 identity issue 후보를 보여주고 버튼으로 `후보 적용 -> resolved ticker 가격 수집 -> readiness 재검사` 경로를 제공해야 한다.

## Scope

- `codex/sub-dev`의 `4b698eb6` 커밋은 그대로 병합하지 않고, alias 후보/active 적용 아이디어만 재사용한다.
- `market_symbol_alias` 새 테이블 대신 기존 `finance_meta.nyse_symbol_lifecycle`의 `event_type=ticker_change`, `related_symbol`, `related_cik`를 중심으로 구현한다.
- BK -> BNY는 fixture / QA 케이스로만 사용한다.
- 1차는 current 기준 Factor Readiness / price refresh에 집중한다. PIT effective-date split 자동화는 후속 차수로 남긴다.

## Stop Condition

- Factor Readiness model이 ticker change 후보를 가격 refresh보다 우선 표시한다.
- apply action이 lifecycle row를 active repair로 저장할 수 있다.
- Backtest price refresh가 active resolver를 읽으면 old ticker 대신 resolved ticker를 수집 대상으로 사용한다.
- 관련 focused tests, py_compile, diff check를 실행하고 commit한다.
