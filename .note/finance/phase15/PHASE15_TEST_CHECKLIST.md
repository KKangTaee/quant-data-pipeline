# Phase 15 Test Checklist

## 목적

- Phase 15에서 정리한 strongest/current candidate 문서와 전략 로그가
  실제로 다시 읽히고 재현 가능한지 수동으로 확인한다.
- 이번 checklist는
  threshold를 바꾸는 것이 아니라,
  **후보 전략 품질 개선 결과가 문서와 UI에서 일관되게 다시 읽히는지**
  를 검수하는 데 초점을 둔다.

## 추천 실행 순서

1. 전략 허브 문서 확인
2. `Value` strongest / balanced candidate 확인
3. `Quality` downside-improved candidate 확인
4. `Quality + Value` strongest candidate 확인
5. 전략별 backtest log 확인
6. Phase 15 report index / archive 확인

## 1. 전략 허브 landing 확인

- `.note/finance/backtest_reports/strategies/`
- 확인 문서:
  - [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
  - [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- 확인:
  - 최근 strongest/current candidate snapshot이 바로 보이는지
  - hub에서 one-pager와 backtest log로 자연스럽게 이동되는지

## 2. Value strongest / balanced candidate 확인

- one-pager:
  - [VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
  - [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
  - [VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md)
- 기대:
  - strongest baseline:
    - `CAGR ≈ 29.89%`
    - `MDD ≈ -29.15%`
    - `real_money_candidate / paper_probation / review_required`
  - downside-improved:
    - `CAGR ≈ 27.48%`
    - `MDD ≈ -24.55%`
  - best addition:
    - `CAGR ≈ 28.13%`
    - `MDD ≈ -24.55%`
- 확인:
  - strongest / balanced / addition 후보가 서로 다른 역할로 읽히는지

## 3. Quality downside-improved candidate 확인

- one-pager:
  - [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
- 기대:
  - `CAGR ≈ 26.02%`
  - `MDD ≈ -25.57%`
  - `real_money_candidate / paper_probation / review_required`
- 확인:
  - `Quality`가 단순 rescue 상태가 아니라,
    actual current candidate까지 확보된 것으로 읽히는지
  - `Rolling Review = watch` 주의점이 문서에 보이는지

## 4. Quality + Value strongest candidate 확인

- one-pager:
  - [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- 기대:
  - quality-side:
    - `net_margin -> operating_margin`
  - value-side:
    - `ocf_yield -> pcr`
  - `Top N = 10`
  - `CAGR ≈ 31.25%`
  - `MDD ≈ -26.63%`
  - `real_money_candidate / small_capital_trial / review_required`
- 확인:
  - sixth-pass follow-up 이후에도 `Top N = 10`이 strongest point로 정리돼 있는지
  - lower-drawdown but weaker-gate 대안 설명이 같이 보이는지

## 5. 전략별 backtest log append 상태 확인

- 확인 문서:
  - [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
  - [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- 확인:
  - 최근 meaningful run이 append되어 있는지
  - 각 entry에
    - goal
    - 기간 / universe
    - key settings
    - result summary
    - interpretation / next action
    가 들어가는지

## 6. Phase 15 archive / index 확인

- 확인 문서:
  - [README.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/README.md)
  - [BACKTEST_REPORT_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
- 확인:
  - Phase 15 fifth / sixth pass report가 index에서 바로 찾히는지
  - completion summary / next phase preparation / test checklist가 finance index에 등록돼 있는지

## 7. Phase 15 한 줄 판단 기준

- 이번 checklist는
  “새 gate를 만들었는가”
  가 아니라,
  **family별 strongest/current candidate가 실제로 문서와 로그 체계 안에 정리됐는지**
  를 보는 checklist다.
