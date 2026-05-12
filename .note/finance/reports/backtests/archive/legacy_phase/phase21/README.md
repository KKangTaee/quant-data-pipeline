# Phase 21 Raw Archive

## 목적

- 이 폴더는 `Phase 21` integrated deep validation에서 나온
  family별 rerun report와 portfolio bridge validation report를 모아 두는 archive다.

## 어떻게 읽으면 되는가

1. family별 current anchor / alternative rerun 결과를 먼저 본다
2. representative portfolio bridge validation 결과를 본다
3. 그 뒤 strategy hub / backtest log / current candidate summary에서
   durable interpretation이 어떻게 반영됐는지 같이 본다

## 현재 포함 문서

- [PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
  - `Value` current anchor와 lower-MDD alternative를 같은 validation frame에서 다시 돌린 first-pass 문서
- [PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
  - `Quality` current anchor와 cleaner alternative를 같은 validation frame에서 다시 돌려,
    current anchor 유지와 cleaner alternative의 comparison-only status를 다시 확인한 first-pass 문서
- [PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
  - `Quality + Value` current strongest point와 lower-MDD alternative를 같은 validation frame에서 다시 돌려,
    current anchor 유지와 `Top N 9` alternative의 weaker-gate status를 다시 확인한 first-pass 문서
- [PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md)
  - `Load Recommended Candidates -> near-equal weighted bundle -> saved portfolio replay` 흐름을 대표 frame으로 검증한 문서
  - 최종 포트폴리오 후보를 고른 문서가 아니라, weighted / saved portfolio workflow가 재현 가능하게 작동하는지 확인한 첫 검증 보고서
