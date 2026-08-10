# Inflation Policy Yield Path Tasks

| Order | Task | State | Gate |
| ---: | --- | --- | --- |
| 1 | inflation-policy-data-pipeline | complete | PIT schema, loaders, official-source smoke |
| 2 | inflation-policy-core-engines | complete | Core PCE Q4/Q4, policy와 joint rate path actual chronological validation 완료 |
| 3 | inflation-policy-workbench | complete | component gate, exact reverse target와 actual Browser command QA 완료 |
| 4 | inflation-policy-equity-stress | complete | verified FactSet EPS vintage, actual joint paths, OOS coverage와 Browser command 통과 |
| 5 | recession-risk-engine | complete | 138 origins/86 OOS folds, no cycle reuse, DB/Browser READY |
| R | inflation-policy-functional-recovery-20260803 | complete | actual DB 기준 1~5차 기능 복구·통합 완료 |
