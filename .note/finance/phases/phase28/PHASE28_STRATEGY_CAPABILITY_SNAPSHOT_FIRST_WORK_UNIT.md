# Phase 28 Strategy Capability Snapshot First Work Unit

## 이 문서는 무엇인가

이 문서는 Phase 28의 첫 번째 작업 단위 기록이다.

목표는 `Backtest` 화면에서 strategy별 지원 범위를 사용자가 바로 확인할 수 있게 만드는 것이다.

## 쉽게 말하면

같은 Backtest 화면에 있어도 전략마다 성격이 다르다.

- annual strict는 Real-Money / Guardrail surface가 가장 성숙하다.
- quarterly strict는 아직 prototype 성격이 남아 있다.
- Global Relative Strength는 재무제표 전략이 아니라 price-only ETF 전략이다.

이번 작업은 이 차이를 화면 안에서 먼저 보여주는 `Strategy Capability Snapshot`을 붙인다.

## 왜 먼저 하는가

Phase 28의 핵심은 전략 family별 차이를 줄이거나, 최소한 헷갈리지 않게 설명하는 것이다.

무턱대고 quarterly나 GRS에 annual strict와 같은 옵션을 복사하면,
사용자는 "이 전략도 annual strict와 같은 수준으로 실전 검증이 끝난 건가?"라고 오해할 수 있다.

그래서 첫 작업은 기능을 더 붙이기 전에,
현재 지원 범위를 명확하게 보여주는 것이다.

## 이번 작업에서 바꾸는 것

### 1. Single Strategy capability snapshot

- `Backtest > Single Strategy`에서 strategy를 선택하면 `Strategy Capability Snapshot` 접힘 영역을 볼 수 있다.
- 이 표는 cadence, data trust, 선택 기록, Real-Money/Guardrail, 저장 / 재실행 지원 범위를 설명한다.

### 2. Compare strategy box capability snapshot

- `Backtest > Compare & Portfolio Builder`에서 선택한 각 전략 박스 안에도 같은 snapshot을 추가했다.
- Quality / Value / Quality + Value는 Annual / Quarterly variant 선택에 따라 다른 설명이 나온다.

### 3. annual / quarterly / ETF 전략 차이 고정

- Strict Annual:
  - annual statement shadow factor 기반
  - Data Trust Summary / price freshness 지원
  - Selection History / Interpretation 지원
  - Real-Money / Guardrail surface가 가장 성숙
- Strict Quarterly Prototype:
  - quarterly statement shadow factor 기반
  - Data Trust Summary / price freshness 지원
  - Portfolio Handling contract는 지원
  - Real-Money promotion / Guardrail 판단은 아직 annual strict 중심
- Global Relative Strength:
  - price-only ETF relative strength 전략
  - Phase 27의 price freshness / Data Trust Summary 지원
  - ETF operability / Real-Money first pass 지원
  - annual strict와 같은 재무제표 selection history 대상은 아님

## 이번 작업에서 하지 않는 것

- quarterly를 annual strict와 동일한 실전 검증 단계로 승격하지 않는다.
- 모든 전략에 같은 Guardrail UI를 억지로 붙이지 않는다.
- 새 전략을 추가하지 않는다.
- 성과가 좋은 후보를 찾는 분석은 하지 않는다.

## 확인할 것

- Single Strategy에서 strategy를 바꾸면 `Strategy Capability Snapshot`이 보이는지
- Compare에서 선택한 각 전략 박스 안에 snapshot이 보이는지
- quarterly prototype이 annual strict와 같은 수준으로 오해되지 않는지
- GRS가 재무제표 selection history 대상이 아니라 price-only ETF 전략으로 읽히는지

## 한 줄 정리

첫 작업은 전략 기능을 더 붙이는 것이 아니라,
전략별 현재 지원 범위를 화면 안에서 먼저 보여주는 작업이다.
