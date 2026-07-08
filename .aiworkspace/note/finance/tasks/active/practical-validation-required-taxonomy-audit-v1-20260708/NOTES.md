# Practical Validation Required Taxonomy Audit Notes

## Main Finding

The current Flow 4 categories are directionally useful, but service ownership is not clean enough. The user-facing confusion comes from repeated evidence rows and repeated gate meaning, not only from labels.

## Important Observations

- `latest_replay` is necessary and should remain a required module.
- `benchmark_parity` is necessary and should remain required, but it should be named around comparison basis rather than only benchmark.
- `validation_efficacy` is currently too broad. It should be narrowed to validation method strength.
- `data_coverage` should own PIT, lifecycle, survivorship, price window, and provider freshness.
- `stress_robustness` should own stress / rolling / sensitivity / overfit evidence.
- `portfolio_construction` should absorb construction risk, risk contribution, and component role/weight as sub-checks for applicable sources.
- `tax_account_scope` and `monitoring_baseline` should remain downstream reference items.

## Proposed Naming

| Current | Proposed visible label |
|---|---|
| Source Integrity | 후보 계약 |
| Latest Runtime Replay | 최신 재검증 |
| Benchmark / Comparator Parity | 비교 기준 동등성 |
| Data Coverage | 데이터 품질 / 편향 통제 |
| Validation Efficacy | 검증 방법론 강도 |
| Backtest Realism | 실전 운용 현실성 |
| Stress / Robustness | 강건성 |
| Construction Risk / Risk Contribution / Component Role Weight | 포트폴리오 구성 근거 |

## Implementation Constraint

Existing JSONL rows and Final Review evidence may still use old module ids. The code refactor should prefer backward-compatible ids internally and only change visible labels / ownership mapping where safe.
