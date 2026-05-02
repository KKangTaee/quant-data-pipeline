# Phase 4 Backtest History First Pass

## 목적
이 문서는 Phase 4 Backtest 탭에
백테스트 실행 이력 저장을 first-pass 수준으로 추가한 결과를 기록한다.

## 구현 내용

추가된 파일:

- `app/web/runtime/history.py`

역할:

- 백테스트 실행 이력을 JSONL로 append
- 최근 이력을 다시 읽어 UI에서 표시

저장 경로:

- `.note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`

## 현재 저장되는 실행 종류

- `single_strategy`
- `strategy_compare`
- `weighted_portfolio`

## 현재 저장되는 핵심 정보

- `recorded_at`
- `run_kind`
- `strategy_key`
- `execution_mode`
- `data_mode`
- `tickers`
- `start / end`
- `timeframe`
- `option`
- `rebalance_interval`
- `top`
- `vol_window`
- summary metric
  - `end_balance`
  - `cagr`
  - `sharpe_ratio`
  - `maximum_drawdown`
- compare / weighted context
  - `selected_strategies`
  - `date_policy`

## UI 반영

`Compare & Portfolio Builder` 섹션 하단에
`Persistent Backtest History` 테이블이 추가되었다.

현재는 다음을 빠르게 읽는 용도다.

- 언제 실행했는지
- 어떤 실행 종류였는지
- 어떤 전략/조합이었는지
- 주요 성과값이 무엇인지
- 어떤 파라미터로 실행했는지

## 검증

검증 방식:

- single strategy run append
- compare run append
- weighted portfolio append
- load 후 각 row가 구분되는지 확인

확인 결과:

- 세 종류 모두 별도 `run_kind`로 적재됨
- compare는 summary보다 selected strategies 중심으로 읽힘
- weighted portfolio는 summary metric과 함께 정상 적재됨

## 현재 한계

- first-pass라서 history filter/search는 아직 없음
- single tab 하단이 아니라 compare 섹션 하단에만 노출
- 실패 실행 이력은 아직 별도 저장하지 않음
