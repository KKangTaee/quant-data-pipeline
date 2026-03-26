# Phase 4 Completion Summary

## 목적

- Phase 4에서 구현된 UI / runtime / strict annual family 결과를 마감 관점에서 정리한다.
- 다음 phase를 열기 전에,
  현재 상태가 어디까지 구현되었는지 한 번에 확인할 수 있게 한다.

## Phase 4에서 완료된 것

### 1. unified Streamlit app 기반 Backtest UI

- 메인 앱은 `app/web/streamlit_app.py` 하나로 유지된다.
- `Ingestion` / `Backtest` 탭 구조가 확정되었다.
- 내부 코드는 탭별 모듈로 분리되어 있다.

### 2. public runtime wrapper set

현재 public runtime family:
- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`
- `Quality Snapshot`
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

즉 Phase 4 종료 시점 기준으로
price-only 4개 + factor/fundamental 계열 4개가 UI에 올라와 있다.

### 3. result / compare / weighted portfolio UX

- single strategy result bundle
- KPI / chart / result table / meta
- compare overlay
- weighted portfolio builder
- contribution chart
- backtest history
- rerun / prefill
- elapsed-time display

까지 first usable product 수준으로 열려 있다.

### 4. factor / fundamental entry

- broad research quality path:
  - `Quality Snapshot`
- strict annual statement path:
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`

strict annual path는 이제:
- statement shadow factor fast runtime
- selection-history interpretation
- operator preset
- preflight / stale-symbol operator UX
- strict multi-factor public candidate
- large-universe union-calendar fix

까지 반영된 상태다.

## Phase 4의 핵심 결과

### broad vs strict 공존 구조가 생겼다

- `Quality Snapshot`
  - broad research path
  - 빠르고 가벼운 public research 전략
- `Quality Snapshot (Strict Annual)`
  - statement shadow strict annual path
  - 더 엄격한 public candidate
- `Value Snapshot (Strict Annual)`
  - strict annual second family / secondary candidate

### strict annual은 sample-universe smoke path를 넘었다

- `US Statement Coverage 100`
- `US Statement Coverage 300`

annual coverage preset과 operator preset이 실제로 연결되었고,
large-universe sparse issue도 해결되었다.

따라서 strict annual family는 이제
sample smoke가 아니라
실제 public candidate family로 볼 수 있는 상태다.

## 아직 남아 있는 제약

- strict annual family는 price-only family보다 still heavier 하다
  - `Coverage 100`: 대략 `3초대`
  - `Coverage 300`: 대략 `9초대`
- `US Statement Coverage 1000`은 real staged preset으로 usable하지만,
  아직 stale symbol `4`개와 `49d` freshness spread가 남아 있어
  public default로 승격하지 않는다
- `Value Snapshot (Strict Annual)`은 now `2016-01-29`부터 active하게 동작하지만,
  valuation/shares/freshness 의존성이 quality strict보다 더 크기 때문에
  current product position에서는 secondary candidate로 두는 편이 맞다
- broad와 strict의 제품 역할은 생겼지만,
  이후에는 더 분명한 guide / preset / defaults polish가 가능하다

## Phase 4 종료 판단

현재 기준으로는:
- Phase 4 major implementation scope:
  - `completed`
- Phase 4 closeout verification:
  - `completed`
- 남은 것은:
  - next phase 연결 준비

즉 Phase 4는 이제
**새 기능을 계속 덧붙이는 단계보다, closeout 후 다음 phase를 여는 단계**
로 보는 것이 맞다.

## 다음 phase 준비 포인트

- strict family comparative research
- strict multi-factor 후보
- strategy library 확장
- broader comparative research workflow

다만 새 major phase 개설은 사용자 확인 후 진행하는 것이 맞다.
