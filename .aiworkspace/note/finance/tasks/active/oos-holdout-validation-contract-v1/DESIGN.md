# OOS Holdout Validation Contract V1 Design

Status: Complete
Created: 2026-05-29

## Contract

`app/services/backtest_temporal_validation.py`에 `build_oos_holdout_validation()`을 추가한다.

입력은 기존 Practical Validation에서 이미 보유한 normalized portfolio curve, benchmark curve, curve source, benchmark parity evidence를 재사용한다.
출력은 workflow registry나 memo 저장이 아니라 Practical Validation result에 포함되는 compact evidence dict다.

## Rows

OOS evidence는 아래 row를 만든다.

- `OOS split sample`: 공통 월 데이터가 in-sample / out-sample 최소기간을 만족하는지 확인한다.
- `Out-sample excess return`: 뒤쪽 holdout 구간의 benchmark 대비 초과성과를 확인한다.
- `Split deterioration`: in-sample excess 대비 out-sample excess가 급격히 악화됐는지 확인한다.
- `Out-sample drawdown gap`: 뒤쪽 구간의 strategy drawdown이 benchmark보다 과도하게 깊은지 확인한다.
- `OOS source strength`: runtime / embedded / proxy source strength와 benchmark parity를 확인한다.

## Status Semantics

- `PASS`: benchmark-aligned split이 충분하고 OOS 성과 / 낙폭 기준과 source strength를 만족한다.
- `REVIEW`: OOS evidence는 있으나 성과 악화, drawdown gap, benchmark parity, proxy source 문제가 남아 있다.
- `NEEDS_INPUT`: portfolio curve, benchmark curve, 공통 월 데이터, split metric 계산에 필요한 evidence가 부족하다.
- `BLOCKED`: 현재 구현에서는 OOS helper가 직접 차단하지 않지만 상위 Validation Efficacy Audit은 다른 row와 함께 차단 route를 계산할 수 있다.

## Storage Boundary

- `db_write=False`
- `registry_write=False`
- `memo_persistence=False`
- live approval / order / auto rebalance 없음

필요한 raw data는 향후 regime task에서 DB / loader backed evidence로 검토하고, OOS task는 기존 curve를 해석하는 read-only contract로 제한한다.
