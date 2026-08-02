# Inflation Policy Equity Stress Runs

## 2026-08-03 Baseline

- focused Python: 81 passed, third-party EDGAR deprecation warning 3건.
- React: 8 passed.
- linked worktree `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`,
  branch `codex/sub-dev`를 재확인했다.

## 2026-08-03 PIT Panel

- RED: equity loader와 pure panel module 부재로 5건 실패.
- GREEN: official EPS cutoff, 월말 index, vintage yield, 차년도 4분기 EPS,
  year-end identity를 구현했다.
- equity/loaders/S&P valuation focused 66건 통과.

## 2026-08-03 Conditional Model

- RED: fit/validation interface 부재로 모델 테스트 4건 실패.
- expanding rolling-origin ridge, constant EPS·multiple baseline, paired residual,
  insufficient-origin gate를 구현했다.
- adverse fixture가 baseline을 실제로 이기고 있던 원인을 metric으로 확인한 뒤 평가
  시작부터 regime이 뒤집히도록 fixture만 교정했다.
- equity/model/loader focused 20건 통과.
