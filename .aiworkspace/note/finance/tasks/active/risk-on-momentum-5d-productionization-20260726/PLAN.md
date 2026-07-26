# Risk-On Momentum 5D Productionization Plan

State: active
Last Updated: 2026-07-26

## Goal

`Risk-On Momentum 5D`를 계산 정확성, 2년 실행 성능, Daily Swing 검증 계약,
Level2 / Final Review / Portfolio Monitoring 경계까지 단계적으로 마무리해
Backtest catalog의 `개발 중` 상태를 근거 있게 종료한다.

## 이걸 하는 이유?

현재 전략 V1/V2의 scanner, D+1 execution, exit, macro mode, comparison, history와
Swing Detail은 구현되어 있다. 그러나 기본 Top1000 2년 실행은 같은 전체 시뮬레이션을
최대 57회 반복하고, 각 실행이 전체 일별 universe row를 Python 객체로 다시 변환해
실사용이 어렵다. 또한 Daily Swing 전용 validation, selected-route, monitoring
governance가 deferred라 catalog가 Level2 인계를 차단한다.

## 전체 Roadmap

### 1차 — Core runtime productionization

- 목적: 결과 의미를 보존하면서 2년 실행을 실사용 가능한 시간으로 줄인다.
- 주요 범위:
  - `finance/swing.py`
  - `finance/swing_analysis.py`
  - `app/runtime/backtest/runners/risk_on_momentum.py`
  - Single Strategy settings schema와 focused tests
- 완료 조건:
  - 기존 synthetic 거래 / 잔고 결과 parity
  - full-universe per-day `iterrows()` 제거
  - prepared date/index data 재사용
  - 중복 variant 실행 제거
  - 빠른 / 표준 / 정밀 검증 강도와 실제 실행 횟수 계약
  - 같은 장비 Top1000 2년 기본 실행 60초 이내

### 2차 — Daily Swing validation handoff

- 목적: raw artifact를 그대로 승격하지 않고 Level2가 읽을 compact evidence를 만든다.
- 주요 범위:
  - Daily Swing validation service/read model
  - Backtest result metadata와 candidate source handoff
  - Practical Validation module / focused tests
- 완료 조건:
  - trade count, holding period, turnover, cost/slippage, macro mode,
    failed-trade quality, benchmark/random comparison을 compact evidence로 전달
  - current-universe / PIT membership / delisting 한계를 명시적으로 판정
  - insufficient evidence는 fail-closed
  - 사용자의 명시적 action 전에는 registry를 쓰지 않음

### 3차 — Maturity and downstream governance closeout

- 목적: Daily Swing에 맞는 수동 검토 정책을 연결한 뒤 `개발 중`을 종료한다.
- 주요 범위:
  - strategy catalog maturity
  - Final Review selected-route policy
  - Portfolio Monitoring daily review / stale signal policy
  - durable docs와 Browser QA
- 완료 조건:
  - Level2 / Final Review 경로가 Daily Swing evidence를 해석
  - monitoring은 수동 review, expiry/stale, no-auto-order 경계를 유지
  - production 분류와 visible copy가 실제 gate 상태와 일치
  - focused/full feasible tests, browser interaction QA, docs sync, coherent commit

## Global Constraints

- 현재 사용자 요청은 위 1차~3차 전체다. 1차만 끝내고 전체 완료로 말하지 않는다.
- point-in-time correctness, look-ahead bias, survivorship bias를 숨기지 않는다.
- current-universe historical result는 PIT membership 근거와 같은 것으로 취급하지 않는다.
- UI에서 provider를 직접 조회하지 않는다.
- raw trade/scanner artifact를 registry payload로 복제하지 않는다.
- Final Review와 Portfolio Monitoring은 live approval, broker order, auto rebalance가 아니다.
- 기존 registry / saved / run history / generated QA artifact는 명시 요청 없이 stage하지 않는다.
- 사용자가 만든 dirty worktree 파일은 수정하거나 되돌리지 않는다.

## Stop Condition

- 1차~3차 완료 조건을 모두 충족하고 검증 결과를 task 문서에 기록한다.
- 외부 데이터 또는 승인 정책 때문에 production 승격이 불가능하면 구현 가능한 범위를
  완료한 뒤 정확한 blocker와 재개 조건을 `RISKS.md` / `STATUS.md`에 남긴다.
