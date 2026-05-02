# Phase 4 Statement-Driven Quality Blocker And Next Steps

## 목적
이 문서는 `Quality Snapshot`을
현재 `broad_research` 요약 팩터 경로가 아니라
`nyse_financial_statement_values` 기반의 더 긴 역사 / 더 나은 timing 의미를 가진 경로로
옮기려 할 때, 현재 즉시 구현을 막는 실제 제약을 정리한다.

## 확인한 현재 상태

직접 확인한 결과:

- `Weekly Fundamental Refresh`는 정상 동작한다
- 하지만 현재 `nyse_fundamentals` / `nyse_factors`의 history depth는 짧다
  - `AAPL/MSFT/GOOG` annual factor coverage는 대체로 `2021~2022` 이후부터
- 그래서 public `Quality Snapshot`은 2016 시작 backtest에서 초반 구간이 현금 상태가 된다

그리고 더 중요한 점:

- 현재 `nyse_financial_statement_values` coverage도 아직 충분히 길지 않다
- 실제 확인 기준:
  - `AAPL annual`: `period_end 2024-09-28 ~ 2025-09-27`
  - `MSFT annual`: `period_end 2025-05-01 ~ 2025-06-30`
  - `GOOG`: 현재 확인 row 없음
- 즉 현재 detailed statement ledger도
  `2016`부터 quality factor를 재구성할 수준의 history depth를 제공하지 못한다

## 의미

이 상태에서는
`statement-driven quality path`를 바로 구현하더라도
원하는 장기 backtest 범위를 열 수 없다.

즉 지금의 blocker는:

1. 설계 미정이 아니라
2. **raw statement coverage 부족**

이다.

## 현실적인 다음 선택지

### 1. Statement ledger backfill 먼저

의미:
- `Extended Statement Refresh` 또는 별도 backfill 경로로
  필요한 universe에 대해 longer-history statement 데이터를 먼저 채운다
- 그 다음 quality factor rebuild로 들어간다

장점:
- 원래 원하던 `option 2` 방향과 가장 일치한다
- 장기적으로 가장 일관된 architecture다

단점:
- 운영 작업량이 크다
- source/provider가 실제로 얼마나 긴 history를 줄 수 있는지 먼저 검증해야 한다

### 2. Public quality 전략은 당분간 broad_research 유지

의미:
- 현재 UI 공개 전략은 그대로 둔다
- statement-driven path는 backfill 이후 second public mode로 연다

장점:
- 지금 제품은 안정적으로 유지된다
- 무리한 구현을 피할 수 있다

단점:
- 2016 quality backtest 문제는 바로 해결되지 않는다

### 3. Universe를 아주 작게 잡고 statement path feasibility test 먼저

의미:
- 예: `AAPL/MSFT/GOOG` 대신
  실제 statement source가 잘 나오는 심볼 1~2개로 먼저 깊이 테스트
- source가 충분한지 확인한 뒤 full path로 확장

장점:
- 가장 빠르게 feasibility를 검증할 수 있다

단점:
- product 기능보다는 조사 단계에 가깝다

## 현재 판단

현재 바로 full statement-driven quality strategy 구현으로 들어가는 것은
실익이 작다.

가장 자연스러운 순서는:

1. `statement history depth`를 먼저 확보할 수 있는지 확인
2. 가능하면 targeted backfill 실행
3. 그 다음 quality factor rebuild / runtime path 구현

## 결론

`option 2`는 방향 자체는 맞다.

다만 지금 즉시 필요한 첫 작업은
새 strategy code를 더 쓰는 것이 아니라
**statement ledger history를 먼저 확보할 수 있는지 검증하고 backfill 범위를 정하는 것**이다.
