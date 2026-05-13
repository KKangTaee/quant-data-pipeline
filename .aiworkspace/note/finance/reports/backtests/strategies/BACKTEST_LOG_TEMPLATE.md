# Strategy Backtest Log Template

## 목적

이 문서는 전략별 backtest log를 작성할 때 공통으로 복사해서 쓰는 템플릿이다.

핵심은 매번 같은 형식으로 남겨서,

- 어떤 설정으로 돌렸는지
- 결과가 어땠는지
- 왜 의미가 있었는지

를 나중에 다시 빠르게 읽을 수 있게 만드는 것이다.

## 작성 규칙

- 의미 있는 백테스트를 하나 완료할 때마다 **append** 한다
- 기존 기록은 지우지 않고 누적하되, 날짜는 최신 run이 위에 오도록 정리한다
- 너무 사소한 trial-and-error는 생략하고, 다시 볼 가치가 있는 run만 남긴다
- 가능하면 아래 항목을 같이 남긴다
  - 목표
  - 기간 / universe / benchmark
  - 핵심 설정
  - factor 또는 ticker
  - 결과
  - 해석
  - 다음 액션
- 문서 마지막에는 최근 핵심 run을 한눈에 보는 `최근 판단 요약표`를 유지한다

## 기록 템플릿

### YYYY-MM-DD - run title

- 목표:
  - 이 run에서 확인하려던 질문
- 전략:
  - family / variant
- 기간 / universe:
  - start / end
  - preset / universe contract
- 핵심 설정:
  - option
  - top_n
  - rebalance interval
  - benchmark
  - overlay / regime / trend
  - real-money contract 핵심값
- factor / ticker:
  - 사용한 factor 또는 ticker
- 결과:
  - CAGR
  - MDD
  - Promotion
  - Shortlist
  - Deployment
- 해석:
  - 왜 의미가 있었는지
  - 어떤 tradeoff가 있었는지
- 다음 액션:
  - 다시 돌릴 것인지
  - 비교 후보가 있는지
- 관련 문서:
  - 연결할 report / phase 문서

## 최근 판단 요약표

| 날짜 | run | 핵심 결과 | 판단 |
| --- | --- | --- | --- |
| YYYY-MM-DD | run title | `CAGR / MDD`, 핵심 gate 상태 | 유지 / 교체 / 보류 판단 |
