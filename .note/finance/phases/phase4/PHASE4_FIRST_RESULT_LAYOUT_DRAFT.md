# Phase 4 First Result Layout Draft

## 목적
이 문서는 Phase 4 첫 백테스트 화면의
결과 레이아웃 초안을 현재 구현 기준으로 고정한다.

현재 범위:
- single strategy
- `Equal Weight`
- DB-backed
- first-pass result display

---

## 현재 레이아웃

현재 `Backtest` 탭의 결과 영역은 아래 순서로 표시된다.

1. 전략명
2. 핵심 KPI metric row
3. 탭 기반 상세 결과

세부 구성:

### 1. KPI metric row

현재 바로 보이는 핵심 값:
- `End Balance`
- `CAGR`
- `Sharpe Ratio`
- `Maximum Drawdown`

의도:
- 사용자가 결과 요약을 가장 먼저 읽게 한다
- summary table 전체를 먼저 읽지 않아도 핵심 지표를 확인하게 한다

### 2. 탭 기반 결과 영역

현재 탭 구성:
- `Summary`
- `Equity Curve`
- `Result Table`
- `Meta`

의도:
- first pass에서 화면을 너무 길게 늘이지 않는다
- 결과/원본/메타를 명확히 분리한다

---

## 각 탭의 역할

### Summary
- `summary_df` 전체 표시
- KPI card 아래의 canonical 요약 테이블

### Equity Curve
- `Total Balance` 단일 line chart
- first pass에서는 시각 노이즈를 줄이기 위해 한 축만 사용

### Result Table
- `result_df` 전체 표시
- strategy raw result preview 성격

### Meta
- 실행 맥락과 runtime metadata 분리 표시
- strategy wrapper 입력과 실행 모드를 확인하는 용도

---

## 현재 의도적으로 하지 않은 것

아래 항목은 아직 first pass 범위에서 제외했다.

- multiple charts
- comparison view
- separate drawdown chart
- download button
- trade log / position table
- debug payload tab

이유:
- 지금 단계는 single-strategy first-pass UI를 안정적으로 여는 것이 우선이다
- 결과 레이아웃은 “가볍지만 product-like” 수준까지만 먼저 맞춘다

---

## 다음 개선 후보

현재 레이아웃 이후 자연스러운 개선 방향:

1. 빈 결과 / 에러 화면 정교화
2. drawdown or return chart 추가
3. second strategy 추가
4. preset 설명/validation 강화

---

## 결론

Phase 4 first-pass 결과 레이아웃은 현재 아래 원칙으로 고정한다.

- 핵심 지표는 바로 위에서 읽는다
- 상세 결과는 탭으로 분리한다
- 메타데이터는 별도 탭으로 분리한다
- first pass는 단순성과 읽기 쉬움을 우선한다
