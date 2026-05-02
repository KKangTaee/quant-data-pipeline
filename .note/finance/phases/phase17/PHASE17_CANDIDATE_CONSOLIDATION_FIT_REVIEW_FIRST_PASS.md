# Phase 17 Candidate Consolidation Fit Review First Pass

## 목적

이미 확보한 strongest practical candidates를
weighted portfolio / saved portfolio로 묶는 흐름이
지금 immediate practical-candidate work의 메인 트랙이 맞는지 본다.

쉽게 말하면:

- 후보를 섞어서 `MDD`를 낮추는 연구가 지금 바로 맞는가
- 아니면 먼저 single-strategy structural lever를 구현하는 편이 맞는가

를 정리하는 문서다.

## 현재 코드에서 이미 가능한 것

### 1. weighted portfolio builder

compare 결과를 바탕으로
전략별 비중을 입력해 monthly weighted portfolio를 만들 수 있다.

근거:
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/pages/backtest.py#L4461)
- [performance.py](/Users/taeho/Project/quant-data-pipeline/finance/performance.py#L70)

### 2. date alignment policy

weighted portfolio는:

- `intersection`
- `union`

두 가지 날짜 정렬 방식으로 만들 수 있다.

즉 candidate combination 실험 자체는
이미 꽤 실용적으로 가능하다.

### 3. saved portfolio workflow

현재 compare 결과와 weighted portfolio 구성을 저장하고,
나중에 다시 compare로 불러오거나 rerun할 수 있다.

근거:
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/pages/backtest.py#L4526)

## 하지만 immediate practical-candidate 메인 트랙이 아닌 이유

### 1. weighted bundle에는 single-strategy real-money surface가 직접 붙지 않는다

현재 `promotion / shortlist / deployment` 계산은
strategy bundle meta를 기준으로 만들어져 있다.

weighted portfolio builder는
월별 가중 결합 결과를 만드는 데는 좋지만,
strict annual 단일 전략과 같은 방식의
`promotion_decision`, `shortlist_status`, `deployment_readiness_status`
를 immediate replacement로 계산해주지는 않는다.

즉:

- 수익률/낙폭 연구에는 바로 쓸 수 있다
- 그러나 실전형 후보 판정 메인 경로로는 아직 얇다

관련 코드:
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py#L844)
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py#L936)
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/pages/backtest.py#L4515)

### 2. current strongest candidate 문제를 직접 해결하지는 않는다

지금 핵심 질문은:

- `Value`의 lower-MDD near-miss를 same gate로 rescue할 수 있나
- `Quality + Value` strongest point를 same gate로 더 방어적으로 만들 수 있나

이다.

weighted portfolio는 이 질문을 우회할 수는 있지만,
single-strategy strongest point의 구조 문제를 직접 고치진 않는다.

## 그래서 지금의 위치는

### 메인 트랙 아님

- Phase 17 immediate practical-candidate work의 메인 트랙은 아니다

### 하지만 강한 보조 트랙

- strongest candidate와 near-miss를
  operator 관점에서 같이 관리하는 데 매우 유용하다
- 나중에:
  - family 간 blend research
  - saved portfolio operator workflow
  - shortlist 후보 묶음 관리

로 이어질 가능성이 높다

## Phase 17 문서에 남길 권고

1. structural downside improvement를 메인 트랙으로 둔다
2. candidate consolidation은 보조 트랙으로 둔다
3. weighted portfolio / saved portfolio는
   - operator organization
   - multi-candidate research
   - later portfolio-level downside study
   용도로 설명한다

## 한 줄 결론

weighted portfolio / saved portfolio는
**지금 당장 single-strategy practical-candidate work를 대체하는 메인 트랙은 아니고,
Phase 17에서는 보조 트랙으로 유지하는 것이 맞다.**
