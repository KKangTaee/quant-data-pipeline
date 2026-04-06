# Quality Strict Annual Backtest Hub

## 전략

- family: `Quality`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`

## 한 줄 요약

`Quality` 단독 family는 Phase 13 탐색에서 `SPY` dominance와 non-hold exact-hit를 동시에 만족시키는 대표 후보를 만들지는 못했다.

즉:

- 품질 factor 조합 실험의 reference로는 의미가 있지만
- 현재 strict annual family 중 최강 후보는 아니었다

## 지금 어떻게 읽으면 되는가

- `SPY` 대비 우위가 가능한지 먼저 확인
- non-hold로 올라갈 수 있는지 확인
- 안 되면 `Value` 또는 `Quality + Value`와 비교

## 대표 결과

- strongest search theme:
  - `SPY` dominance 탐색
- current takeaway:
  - exact-hit 없음
  - family 단독으로는 `Value`보다 약했다

## 관련 결과 문서

- [PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md)
  - `Quality`만으로 `SPY`를 동시에 이길 수 있는지 본 핵심 문서
- [PHASE13_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md)
  - strict annual family 전체를 `SPY` 기준으로 비교한 문서
- [PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md)
  - `CAGR 15% / MDD 20%` 조건까지 넣었을 때 family 비교 결과
- [PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md)
  - `real_money_candidate + SPY 초과 + MDD 25% 이내` 조건 탐색
- [PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md)
  - coverage 확대가 `Quality` family에도 의미가 있었는지 확인하는 공통 문서
- [PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md)
  - family 전체를 한 장으로 요약한 summary 문서

## 실무 해석

지금 시점의 `Quality Strict Annual`은:

- 단독 운영 후보보다는
- factor 비교 기준점
- `Value`와 `Quality + Value`를 해석할 때의 reference family

로 읽는 편이 맞다.
