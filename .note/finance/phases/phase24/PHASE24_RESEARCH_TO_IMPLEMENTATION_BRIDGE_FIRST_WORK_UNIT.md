# Phase 24 Research-To-Implementation Bridge First Work Unit

## 목적

이 문서는 Phase 24의 첫 작업 단위다.

목표는 `quant-research`에 있는 전략 문서 중에서
지금 finance 백테스트 제품에 가장 안전하게 붙일 수 있는 첫 신규 전략 후보를 고르는 것이다.

## 쉽게 말하면

새 전략을 추가할 수는 있지만,
모든 전략을 지금 바로 구현할 수 있는 것은 아니다.

옵션, M&A, 선물, 회사 이벤트, analyst estimate처럼 별도 데이터가 필요한 전략은 매력적이어도 첫 구현 후보로는 부담이 크다.
반대로 ETF 가격 데이터만으로 구현 가능한 월간 전략은 현재 DB loader와 compare/history 구조에 바로 붙이기 좋다.

## 첫 후보 선정 기준

Phase 24 첫 구현 후보는 아래 기준을 만족해야 한다.

- 현재 MySQL price history loader로 필요한 데이터를 읽을 수 있어야 한다.
- daily 또는 month-end ETF 가격만으로 신호를 만들 수 있어야 한다.
- single strategy와 compare에 넣었을 때 결과 schema가 기존 `Total Balance`, `Total Return` 구조와 맞아야 한다.
- history / load-into-form / saved replay payload가 과하게 복잡하지 않아야 한다.
- 투자 분석이 아니라 제품 기능 검증으로 대표 smoke run을 만들 수 있어야 한다.

## 검토한 후보군

### 1. Global Relative-Strength Allocation With Trend Safety Net

- 문서 위치:
  - `/Users/taeho/Project/quant-research/.note/research/strategies/2026-04-15-global-relative-strength-allocation-with-trend-safety-net.md`
- 장점:
  - ETF 가격 데이터만으로 구현 가능하다.
  - 월말 리밸런싱이라 현재 compare / history 구조와 잘 맞는다.
  - 상대강도 score, trend filter, cash fallback 구조가 이미 구현된 GTAA / Dual Momentum 계열과 개념적으로 가깝다.
  - 새 전략 family로 분리하되 기존 price-only strategy infrastructure를 재사용할 수 있다.
- 주의점:
  - GTAA와 비슷해 보일 수 있으므로, UI와 문서에서 차이를 설명해야 한다.
  - 성과 분석이 아니라 new family integration 검증으로 다뤄야 한다.

### 2. Treasury Roll-Down With Curve-Steepness Filter

- 장점:
  - 공식 데이터 근거가 좋고 전략 아이디어가 명확하다.
- 보류 이유:
  - yield curve / duration / roll-down 계산이 필요해 price-only 첫 구현보다 데이터/모델 부담이 크다.

### 3. US Buyback Achievers / Quality Dividend Growth

- 장점:
  - 실제 ETF proxy와 공식 방법론 근거가 있다.
- 보류 이유:
  - direct replication은 buyback, dividend, share, filing timing 데이터가 필요해 Phase 24 첫 구현 후보로는 무겁다.

### 4. Options / Event-Driven / Market-Neutral 전략군

- 장점:
  - 전략 다양성은 크다.
- 보류 이유:
  - 옵션 chain, M&A event, short borrow, global classification 등 별도 데이터가 필요하다.
  - Phase 24의 첫 목표인 “새 전략 추가 표준 경로 검증”보다 범위가 커진다.

## 첫 구현 후보

첫 구현 후보는 `Global Relative-Strength Allocation With Trend Safety Net`으로 둔다.

이 전략은 현재 codebase에 가장 자연스럽게 붙는다.

- 입력: ETF ticker basket, top N, score lookback, trend MA, cash ticker
- cadence: monthly
- fallback: trend를 통과하지 못한 슬롯은 cash proxy 또는 현금
- output: 기존 price-only strategy result schema와 호환 가능
- UI 연결: `Backtest > Single Strategy`, compare, history, saved replay에 붙이기 쉬움

## GTAA와의 차이

겉으로는 GTAA와 비슷하지만 역할이 다르다.

- GTAA:
  - 현재 코드에서는 broader tactical allocation 엔진으로 쓰이고,
    score weight, risk-off, defensive bond preference, crash guardrail 등 실전 후보 검토 surface가 이미 붙어 있다.
- Global Relative Strength:
  - `quant-research`의 별도 전략 문서에서 온 신규 family다.
  - Phase 24에서는 “새 research note를 제품 전략으로 옮기는 첫 사례”로 쓴다.
  - 처음부터 real-money promotion까지 확장하지 않고, price-only monthly allocation의 최소 제품 경로를 검증한다.

## 다음 구현 단위

다음 작업은 첫 신규 family의 최소 구현이다.

필요한 연결은 다음과 같다.

- `finance.strategy`: relative-strength allocation simulation 또는 기존 GTAA engine 재사용 wrapper
- `finance.sample`: DB-backed helper와 default universe
- `app.web.runtime.backtest`: result bundle / meta / history payload에 필요한 runtime wrapper
- `app.web.backtest_strategy_catalog`: strategy option 등록
- `app.web.pages.backtest`: single / compare / history / saved replay UI 연결
- `.note/finance/backtest_reports/phase24/`: representative smoke validation report

## 한 줄 정리

Phase 24 첫 구현 후보는 성과가 가장 좋아서가 아니라,
현재 제품 구조에 가장 안전하게 붙여서 신규 전략 추가 경로를 검증하기 좋기 때문에 선택한다.
