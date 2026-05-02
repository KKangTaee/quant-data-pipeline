# Phase 4 Backtest History Enhancement Second Pass

## 목적
이 문서는 Phase 4 Backtest 탭의
`Persistent Backtest History`를
first-pass filter/search/drilldown에서 한 단계 더 확장한 내용을 기록한다.

이번 단계의 초점:

- 날짜 기준으로 다시 좁혀보기
- metric 기준으로 정렬하기
- 저장된 단일 전략 실행을 다시 실행하기

## 추가된 기능

### 1. Recorded Date Range

history는 이제 `recorded_at` 기준으로 날짜 범위를 걸러볼 수 있다.

의미:

- 특정 작업 세션이나 최근 며칠간의 실험만 빠르게 다시 볼 수 있다

### 2. Sort

지원되는 정렬 기준:

- `Recorded At (Newest)`
- `Recorded At (Oldest)`
- `End Balance (High)`
- `CAGR (High)`
- `Sharpe Ratio (High)`
- `Drawdown (Best)`

의미:

- 단순 최신순 조회를 넘어서
  성과가 좋았던 실행이나
  drawdown이 덜 나빴던 실행을 바로 찾을 수 있다

### 3. Run Again

selected record 하단에 `Run Again` action이 추가되었다.

현재 지원 범위:

- `single_strategy` 계열 중
  - `equal_weight`
  - `gtaa`
  - `risk_parity_trend`
  - `dual_momentum`

현재 미지원:

- `strategy_compare`
- `weighted_portfolio`

이유:

- compare / weighted history는 현재 저장 구조상
  각 전략의 모든 override와 composite build context를
  완전히 되살릴 만큼 충분히 세밀하게 남기지 않기 때문이다

즉 현재 `Run Again`은
“안전하게 동일 경로를 다시 탈 수 있는 단일 전략 실행”
만 대상으로 연다.

## 구현 파일

- `app/web/pages/backtest.py`

## 검증

확인한 것:

- history table builder가 정렬 보조 컬럼을 포함해 정상 동작
- rerun payload 복원이 가능한 single-strategy record에서 정상 생성
- `equal_weight` record 기준:
  - `rebalance_interval=12`
  복원 확인

## 현재 한계

- compare / weighted `Run Again`은 아직 미지원
- 결과를 현재 form 입력값에 역주입하는 기능은 아직 없음
- `recorded_at` 기준 필터만 있고,
  input period 기준 필터는 아직 없음

## 다음 자연스러운 확장

- compare / weighted rerun에 필요한 저장 스키마 보강 여부 검토
- selected history -> current form prefill
- metric threshold filter
