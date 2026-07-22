# Market Research Editorial Navigation V2 Risks

Status: Complete
Last Updated: 2026-07-23

## Resolved Risks

1. family button은 44px 높이와 focus-visible outline을 유지하며 actual keyboard QA를 통과했다.
2. 420px에서 `지수 가치평가` full label과 동일 너비 3-column이 clipping 없이 표시된다.
3. navigation은 module과 같은 full-width 축을 사용하고 desktop overflow가 없다.
4. active family underline과 active view fill은 light/dark theme variable 계약을 유지한다.
5. 7-view URL/active-state 전환과 Python 회귀로 V1 state/fallback 계약을 확인했다.

## Deferred

- command bar, left rail, drawer, sticky navigation
- recent/saved research
- module body redesign

## Verification Gap Outside Scope

- broad service contracts에는 기존 baseline과 같은 18 failures가 남는다: Practical Validation/Backtest 13, Futures Macro 3, Sentiment/AAII 2. Market Research Editorial 변경 파일과 겹치지 않으며 이 task에서 수정하지 않았다.
