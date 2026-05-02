# Phase 4 Visualization And Portfolio Builder Options

## 목적
이 문서는 Phase 4 Backtest 탭에서

- 시각화 강화
- 전략 비중 결합 포트폴리오
- 다중 전략 비교 그래프

를 어떤 순서와 방식으로 열지 정리하기 위한 선택 문서다.

이 영역은 UI 구조와 사용 흐름에 직접 영향을 주므로
구현 전에 사용자와 선택지를 먼저 합의하는 것이 맞다.

## 현재 코드 기준 가능한 것

- 단일 전략 DB-backed 실행:
  - `Equal Weight`
  - `GTAA`
  - `Risk Parity Trend`
  - `Dual Momentum`
- 공통 성과 요약:
  - `portfolio_performance_summary(...)`
- 여러 전략 결합 포트폴리오:
  - `make_monthly_weighted_portfolio(...)`
- 여러 전략 비교 그래프의 기초:
  - `plot_equity_curves(...)`
  - `plot_drawdowns(...)`

즉, 기능의 씨앗은 이미 있고
Phase 4에서는 이것을 UI와 runtime wrapper 기준으로 다시 묶는 작업이 핵심이다.

---

## 사용자 요청을 기능 단위로 나누면

### 1. 시각화 강화

예시:

- 누적 수익 곡선 강화
- drawdown 차트
- top 3 best / worst period 표시
- 고점 / 저점 annotation
- summary KPI 강화

### 2. 전략 비중 결합 포트폴리오

예시:

- `Dual Momentum 50 + GTAA 50`
- `Equal Weight 40 + GTAA 30 + Risk Parity 30`

핵심은 여러 전략 결과를 월별 기준으로 정렬해서
가중 결합 포트폴리오를 만드는 것이다.

### 3. 여러 전략 비교 그래프

예시:

- 최대 `n`개 전략을 한 화면에 overlay
- equity curve 비교
- drawdown 비교
- summary table 비교

---

## 추천 구현 순서

### 추천 순서 A

1. 다중 전략 비교 그래프
2. 전략 비중 결합 포트폴리오
3. 단일/결합 포트폴리오 시각화 강화

이 순서를 추천하는 이유:

- 현재 공개 전략 4개가 이미 있어서 비교 기능 체감이 바로 큼
- 비교 기능을 만들면 그 결과를 그대로 비중 결합 입력으로 재사용하기 쉬움
- 결합 포트폴리오가 생긴 뒤에 시각화를 강화하면
  단일 전략과 조합 전략을 같은 화면 규칙으로 보여주기 좋음

---

## 화면 구조 선택지

### 옵션 1. Backtest 탭 안에 단계적으로 확장

- 현재 화면 유지
- 아래쪽에
  - compare section
  - portfolio builder section
  를 추가

장점:

- 현재 구조를 거의 유지
- 빠르게 붙일 수 있음

단점:

- 한 탭 안에서 길어질 수 있음

### 옵션 2. Backtest 탭 내부를 2단 구조로 분리

- `Single Strategy`
- `Compare / Portfolio Builder`

장점:

- 사용 흐름이 더 명확함
- 비교/결합 기능이 커져도 정리가 쉬움

단점:

- 현재보다 구조 변경이 조금 있음

### 옵션 3. Backtest 탭 내부를 3단 구조로 분리

- `Single Strategy`
- `Compare`
- `Portfolio Builder`

장점:

- 가장 명확함

단점:

- 지금 단계에서는 다소 과할 수 있음

---

## 시각화 강화 후보

### 후보 A. 즉시 추가 가치가 큰 것

- Equity Curve overlay
- Drawdown overlay
- Summary comparison table

### 후보 B. 단일 전략 강조용

- 최고점/최저점 marker
- top 3 best / worst monthly return table
- rolling return / rolling drawdown

### 후보 C. 나중 단계

- rebalance event marker
- 포지션 비중 변화 시각화
- strategy contribution breakdown

---

## 현재 기준 추천안

현재 기준 추천은 아래 조합이다.

- 화면 구조: `옵션 2`
- 구현 순서:
  1. Compare / Portfolio Builder 진입 섹션 추가
  2. 최대 `n`개 전략 overlay equity / drawdown
  3. `make_monthly_weighted_portfolio(...)`를 UI에서 호출
  4. 결합 포트폴리오 결과를 기존 result bundle 스타일로 표시
  5. 단일/결합 전략 공통으로 top 3 best / worst period 표 추가

이 조합은 사용자 요청 3개를 모두 커버하면서도
현재 Phase 4 구조를 무리하게 깨지 않는다.

---

## 결정이 필요한 항목

다음 구현 전에는 아래를 사용자와 확정하는 것이 맞다.

1. 화면 구조:
   - Backtest 탭 내부를 계속 단일 화면으로 확장할지
   - `Single Strategy` / `Compare+Builder` 2단으로 나눌지

2. 우선 기능:
   - 비교 그래프 먼저
   - 비중 결합 먼저
   - 단일 전략 시각화 강화 먼저

3. 비교 전략 수:
   - 최대 2개
   - 최대 4개
   - 사용자 임의 선택 + 상한만 둘지
