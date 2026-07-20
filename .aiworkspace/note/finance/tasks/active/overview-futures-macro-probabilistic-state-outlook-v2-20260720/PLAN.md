# Overview Futures Macro Probabilistic State Outlook V2 Plan

Status: Design approved; implementation plan ready
Started: 2026-07-20

## 이걸 하는 이유?

현재 `최근 시장 위치와 조건부 다음 경로`는 최근 5일 표준화 상태를 `20D 전 / 5D 전 / 현재` 세 점으로만 연결한다.
하루 갱신 때 세 anchor의 실제 날짜가 함께 이동하고 진행 중 일봉까지 들어갈 수 있어, 사용자가 과거 경로가 다시 쓰인 것으로 오해할 수 있다.

더 중요한 문제는 관측점과 전망점의 의미가 다르다는 점이다.
관측점은 같은 날짜의 5D rolling state지만, 전망점은 현재 위치에 과거 유사 episode의 forward cumulative return을 더한 좌표다.
사용자가 원하는 것은 같은 상태 정의의 `S(t+5)`와 `S(t+20)` 확률분포다.

V2는 예측 위치를 반드시 만드는 작업이 아니다.
모멘텀-only와 macro-conditioned hybrid를 시간순 검증으로 비교하고, baseline을 이기지 못한 horizon은 `예측 우위 없음`으로 남기는 것이 목적이다.

## Goal

1. 완료된 선물 session만 current state에 사용한다.
2. 최근 실제 일별 상태 경로를 생략 없이 보여준다.
3. 5D / 20D target을 동일 정의의 future state로 바꾼다.
4. momentum-only를 기준모델로 두고 macro/event conditioning의 incremental value를 검증한다.
5. 확률과 위치/경로 검증을 분리하고 검증되지 않은 예상 위치를 공개하지 않는다.
6. 날짜별 input identity, model version, forecast를 재현 가능한 history로 남긴다.

## Tentative Roadmap

### 1차 — Data / Target Contract

- 목적: 완료 session, canonical session date, same-state future target을 확정한다.
- 주요 범위: futures candle normalization, pattern feature/state builder, forecast history storage contract.
- 완료 조건:
  - 진행 중 daily candle이 final state를 덮어쓰지 않는다.
  - 같은 as-of cutoff를 다시 계산하면 feature와 target이 동일하다.
  - `S(t+h)`가 `S(t)`와 같은 feature/state 정의를 사용한다.
- 다음 연결: 2차의 모델 후보가 모두 같은 target으로 경쟁한다.

### 2차 — Momentum Baseline / Macro Hybrid Validation

- 목적: macro를 강제로 채택하지 않고 horizon별 incremental edge를 측정한다.
- 주요 범위: reduced momentum feature set, PIT macro context, event-risk context, rolling-origin comparison.
- 완료 조건:
  - unconditional / persistence / momentum-only / hybrid 결과를 동일 fold에서 비교한다.
  - 선택 모델과 선택 이유가 horizon별로 기록된다.
  - 어떤 모델도 baseline을 못 이기면 `NO_EDGE`다.
- 다음 연결: 3차 UI가 검증 결과에 따라 확률, density, suppression을 선택한다.

### 3차 — Observed Trail / Probabilistic Outlook UI / QA

- 목적: 실제 경로와 조건부 분포를 결정론적 선으로 오해하지 않게 한다.
- 주요 범위: Futures Macro payload, React pattern map, method disclosure, daily forecast comparison.
- 완료 조건:
  - 최근 20~30 completed session이 실제 날짜 순서로 표시된다.
  - 5D / 20D는 terminal density와 regime probability를 분리해 보여준다.
  - path gate 미통과 시 예상 이동선/위치가 없다.
  - desktop / 420px Browser QA와 고정 as-of 재현 QA를 통과한다.

## In Scope

- Overview > Futures Macro의 pattern/outlook service와 React surface
- daily futures session finality / canonical date boundary
- same-state 5D / 20D target
- momentum-only versus PIT macro-conditioned comparison
- official stored macro event schedule의 horizon risk context
- compact immutable forecast history
- focused tests, Browser QA, finance docs alignment

## Out Of Scope

- 매수/매도 신호, 목표가격, 주문, broker 연동
- CPI / payroll consensus surprise 신규 유료 provider 도입
- 검증 전 supervised black-box model 자동 채택
- Economic Cycle publication logic 변경
- Futures Monitor intraday chart 재설계
- macro data가 없을 때 현재값이나 수정 최신값으로 과거를 채우기

## Stop Conditions

- 1차에서 provider daily timestamp를 안전한 completed session으로 매핑할 수 없으면 UI 구현 전에 중단하고 data contract를 재협의한다.
- macro PIT history가 horizon 검증에 부족하면 hybrid는 `UNAVAILABLE`로 두고 momentum baseline만 검증한다.
- hybrid가 momentum-only를 시간순 검증에서 개선하지 못하면 macro를 production forecast에 사용하지 않는다.
- terminal/path 분포가 baseline 또는 coverage gate를 통과하지 못하면 예상 위치를 공개하지 않는다.

## Approval Gate

- 2026-07-20: 사용자가 written design을 명시적으로 승인했다.
- 상세 TDD 실행 계획은 `IMPLEMENTATION_PLAN.md`에 보존한다.
- 실행 방식을 선택한 뒤 1차 Data / Target Contract부터 시작한다.
