# Phase 4 Factor / Fundamental First Strategy Options

## 목적
이 문서는 Phase 4에서
첫 factor / fundamental 전략을 어떤 유형으로 열지 고르기 위한 기준 문서다.

현재 전제:
- price-only 전략 UI는 이미 열려 있다
- 다음 단계는 snapshot-first 입력을 쓰는 전략군이다
- 첫 전략은 복잡도를 통제하면서도 확장성이 있어야 한다

---

## 옵션 1. Value Snapshot Strategy

예시 신호:
- `per`
- `pbr`
- `psr`
- `book_to_market`
- `earnings_yield`

장점:
- factor 의미가 직관적이다
- 현재 `nyse_factors`에서 바로 가져오기 쉽다
- ranking/selection UI로 연결하기 쉽다

단점:
- valuation factor는 price attachment와 시점 해석이 중요하다
- naive하게 열면 broad research 값과 strict PIT 기대가 쉽게 섞일 수 있다

적합도:
- 높음

---

## 옵션 2. Quality Snapshot Strategy

예시 신호:
- `roe`
- `roa`
- `gross_margin`
- `operating_margin`
- `debt_ratio`

장점:
- price dependency가 valuation보다 약하다
- accounting quality 중심 전략으로 설명하기 쉽다
- first-pass에서 missingness handling 규칙을 드러내기 좋다

단점:
- 단일 factor만으로는 전략 설명력이 약해 보일 수 있다
- value 대비 직관적인 성과 비교가 어려울 수 있다

적합도:
- 높음

---

## 옵션 3. Simple Multi-Factor Strategy

예시 신호:
- value + quality 혼합 score
- 예: `book_to_market`, `earnings_yield`, `roe`, `gross_margin`

장점:
- 장기적으로 가장 실전적인 방향에 가깝다
- snapshot 연결, ranking, weighting, selection을 모두 보여줄 수 있다

단점:
- 첫 구현으로는 결정할 것이 많다
- score 조합 방식, 결측 처리, 표준화 규칙까지 같이 정해야 한다

적합도:
- 중간

---

## 권장 시작점

현재 기준 권장은:
- `Quality Snapshot Strategy` 또는 `Value Snapshot Strategy`

더 구체적으로는:
- strict PIT 경계 설명을 먼저 강조하고 싶다면 `Quality`
- factor ranking UI의 직관성을 먼저 강조하고 싶다면 `Value`

현재 단계에서 `Simple Multi-Factor`를 첫 전략으로 여는 것은
조금 이른 편으로 본다.

---

## 첫 전략이 가져야 할 공통 조건

어떤 옵션을 고르든 첫 전략은 아래를 만족하는 것이 좋다.

1. 월말 rebalance 기준으로 설명 가능해야 한다
2. snapshot 입력 컬럼 수가 과하지 않아야 한다
3. broad research / strict PIT 차이를 문서로 설명할 수 있어야 한다
4. UI 입력이 너무 많아지지 않아야 한다

---

## 결론

첫 factor / fundamental 전략 후보는 아래 둘 중 하나가 현실적이다.

1. `Value Snapshot Strategy`
2. `Quality Snapshot Strategy`

이 둘 중 하나를 먼저 고르고,
그 다음에 필요한 snapshot 컬럼 계약과 runtime wrapper 시그니처를 고정하는 순서가 맞다.
