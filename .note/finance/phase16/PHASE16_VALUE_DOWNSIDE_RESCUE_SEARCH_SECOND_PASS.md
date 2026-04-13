# Phase 16 Value Downside Rescue Search Second Pass

이 문서는 결과 중심 backtest report로 재분류되어
아래 경로를 canonical 문서로 사용한다.

- [PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md)

## 핵심 결론

- current best practical point는 여전히 `Top N = 14 + psr`다
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `real_money_candidate / paper_probation / review_required`
- lower-MDD rescue near-miss는
  - `Top N = 14 + psr + pfcr`
  - `CAGR = 27.22%`
  - `MDD = -21.16%`
  - 하지만 `production_candidate / watchlist`로 내려간다
- `Top N = 15 + psr + pfcr`는
  - `real_money_candidate / paper_probation`을 회복하지만
  - `MDD = -27.59%`로 downside edge를 잃는다
- 즉 이번 second pass에서도
  same gate를 유지하면서 `MDD`를 더 낮춘 exact rescue는 없었다
