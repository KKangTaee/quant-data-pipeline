# Phase 4 First Screen Scope

## 목적
이 문서는 Phase 4 첫 백테스트 화면의 범위를
너무 넓어지지 않게 고정하기 위해 만든다.

현재 범위:
- single strategy
- DB-backed
- `Equal Weight`
- form-first

---

## 현재 결정

첫 백테스트 화면은
`Equal Weight` 단일 전략 실행 form부터 시작한다.

현재 단계에서 먼저 구현하는 것:
- strategy 제목/설명
- universe 입력
- 기간 입력
- 최소 advanced input
- runtime payload preview

현재 단계에서 아직 구현하지 않는 것:
- 결과 summary 카드
- equity curve
- result table
- multi-strategy selector
- 비교 화면

---

## 사용자 입력 범위

first pass form은 아래 입력만 직접 노출한다.

필수 입력:
- `universe_mode`
- `preset_name` 또는 `tickers`
- `start_date`
- `end_date`

advanced 입력:
- `timeframe`
- `option`
- `rebalance_interval`

현재 판단:
- first pass에서 전략 선택기는 아직 필요 없다
- 첫 공개 전략이 `Equal Weight` 하나로 고정되어 있기 때문이다

---

## 왜 form-first가 적절한가

현재 Phase 4는
runtime public boundary를 막 고정한 상태다.

이 시점에서 바로:
- 실행
- 결과 레이아웃
- 차트
- 에러 처리

를 한 번에 넣으면
초기 UI 범위가 빠르게 커질 수 있다.

따라서 먼저:
- 어떤 입력을 받을지
- 어떤 payload가 wrapper로 갈지

를 UI에서 명확히 드러내는 것이 더 안전하다.

---

## 현재 화면의 의미

현재 `Backtest` 탭의 first-pass form은
아직 최종 실행 화면이 아니다.

의미는 아래와 같다.

1. UI 입력 계약 시각화
2. wrapper payload shape 확인
3. 다음 단계 실행 연결을 위한 안정적 출발점 확보

---

## 다음 단계

이 문서 기준 다음 단계는 아래 순서다.

1. form submit -> `run_equal_weight_backtest_from_db(...)` 연결
2. result bundle 수신
3. summary / chart / table 표시
4. 빈 결과 / 에러 규칙 추가

---

## 결론

Phase 4 첫 화면 범위는 현재 아래처럼 고정한다.

- `Equal Weight`
- DB-backed
- single-screen form first
- 결과 화면은 다음 단계에서 연결
