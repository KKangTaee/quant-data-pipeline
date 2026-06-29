# Plan

Status: Completed
Last Verified: 2026-06-08

## Goal

Backtest 3차 3C로 Risk-On Momentum 5D의 governance readiness를 Backtest Analysis에서 read-only로 확인하게 한다.

## 이걸 하는 이유?

Risk-On Momentum 5D는 Daily Swing research evidence가 강하지만 기존 monthly / annual candidate workflow와 다르다.
따라서 사용자가 이 전략을 바로 Practical Validation 후보, Final Review selected-route 후보, 또는 Portfolio Monitoring daily signal로 오해하지 않도록
필요한 validation module / review rule / monitoring cadence / artifact boundary를 먼저 제품 화면에서 명확하게 보여준다.

## Scope

- Streamlit-free Risk-On Momentum governance read model을 추가한다.
- Backtest Analysis에 read-only `Risk-On Momentum 5D Governance` panel을 추가한다.
- Daily Swing Practical Validation module, Final Review route, Portfolio Monitoring signal policy의 readiness / blocker / next action을 표시한다.
- storage / route boundary를 명시한다.
- focused tests와 Browser QA를 수행한다.
- 관련 durable docs와 root handoff logs를 sync한다.

## Out Of Scope

- Risk-On Momentum runtime behavior 변경.
- Practical Validation module 실행 구현.
- Final Review selected-route gate 연결.
- Portfolio Monitoring daily signal / 자동 signal write 구현.
- registry / saved JSONL / run history rewrite.
- DB schema 변경.
- provider / FRED direct fetch.
- ETF current-candidate rerun.
- live trading / broker order / auto rebalance 설계.

## Completion Criteria

- Risk-On Momentum governance read model이 Streamlit-free이며, governance 상태가 deferred로 고정된다.
- panel이 research evidence와 missing governance modules를 구분한다.
- panel이 monitoring signal이 아니라 review evidence로 시작한다는 정책을 명시한다.
- tests, py_compile, UI-engine boundary checker, diff check, Browser QA가 완료된다.
- docs / task records / root logs가 현재 3C 상태와 맞는다.
