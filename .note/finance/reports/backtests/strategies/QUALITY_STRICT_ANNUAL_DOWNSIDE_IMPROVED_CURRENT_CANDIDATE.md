# Quality Strict Annual Downside Improved Current Candidate

## 한 줄 요약

`Quality > Strict Annual` rescued anchor에서
가장 실무적으로 매력적인 downside-improved current candidate는
`Top N = 12`였다.

이 조합은 rescued baseline 대비

- `CAGR`를 높이고
- `MDD`를 크게 낮추면서
- `real_money_candidate / paper_probation / review_required`
를 그대로 유지했다.

## 전략

- family: `Quality`
- variant: `Strict Annual`
- role:
  - rescued-anchor downside-improved current candidate
  - `Quality` family의 practical follow-up reference

## 전략 구성

### 기간 / universe

- `2016-01-01 ~ 2026-04-01`
- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`

### 핵심 설정

- `Option = month_end`
- `Top N = 12`
- `Rebalance Interval = 1`
- `Benchmark = LQD`
- `Trend Filter = on`
- `Market Regime = off`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`

### factor 조합

- `roe`
- `roa`
- `cash_ratio`
- `debt_to_assets`

### real-money / guardrail

- practical strict annual contract defaults 유지
- underperformance guardrail `on`
- drawdown guardrail `on`

## 결과

- `CAGR = 26.02%`
- `MDD = -25.57%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation = normal`
- `Rolling Review = watch`
- `Out-of-Sample Review = normal`

## 왜 다시 볼 가치가 있나

- rescued baseline(`Top N = 10`) 대비
  - `CAGR`:
    - `24.28% -> 26.02%`
  - `MDD`:
    - `-31.48% -> -25.57%`
  로 동시에 개선됐다.
- gate도 그대로 유지됐다.
- 즉 `Quality` family 안에서
  actual candidate quality를 더 좋게 만들 수 있다는 첫 clear proof다.

## 주의점

- `Rolling Review = watch`가 붙는다.
- 즉 stronger downside / return tradeoff이긴 하지만
  consistency surface는 rescued baseline보다 아주 조금 더 보수적으로 읽어야 한다.
- more conservative alternative가 필요하면
  `Top N = 16`
  (`CAGR = 20.23%`, `MDD = -25.73%`, `Rolling = normal`)
  도 같이 참고할 수 있다.

## 관련 문서

- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md)
- [PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md)
