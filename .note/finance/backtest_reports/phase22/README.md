# Phase 22 Portfolio-Level Candidate Construction Archive

## 이 archive는 무엇인가

- 이 폴더는 `Phase 22`에서 만든 portfolio-level candidate 관련 report를 모아두는 위치다.
- `Phase 21`의 portfolio bridge 검증을 이어받아,
  weighted portfolio를 재현 가능한 후보 기록으로 관리할 수 있는지 확인한다.

## 현재 report

| 문서 | 역할 |
|---|---|
| [PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md) | `Value / Quality / Quality + Value` current anchor 3개를 equal-third baseline portfolio candidate pack으로 다시 정의한 첫 report |
| [PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md) | equal-third baseline과 `25/25/50`, `40/40/20` weight alternative를 같은 frame에서 비교한 rerun report |

## 읽는 순서

1. [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md)
2. [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md)
3. [PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md)
4. [PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md)
5. [PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md)

## 운영 메모

- `Phase 22` report는 최종 투자 후보를 바로 확정하기보다,
  portfolio-level candidate를 어떤 기준으로 유지 / 교체 / 보류할지 기록하는 데 초점을 둔다.
- saved replay가 재현되지 않은 portfolio는 candidate로 보지 않는다.
