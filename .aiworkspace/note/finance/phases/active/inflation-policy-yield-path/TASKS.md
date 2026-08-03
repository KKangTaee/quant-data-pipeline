# Inflation Policy Yield Path Tasks

| Order | Task | State | Gate |
| ---: | --- | --- | --- |
| 1 | inflation-policy-data-pipeline | complete | PIT schema, loaders, official-source smoke |
| 2 | inflation-policy-core-engines | partial complete | Core PCE Q4/Q4 actual validation 완료, policy·joint path production validation 필요 |
| 3 | inflation-policy-workbench | reopened | reverse JSON/component gate와 Core PCE actual Browser QA 완료, policy/reverse result QA 필요 |
| 4 | inflation-policy-equity-stress | reopened | PIT forward EPS vintage와 actual joint path materialization 필요 |
| 5 | recession-risk-engine | pending | independent validation; no cycle reuse |
| R | inflation-policy-functional-recovery-20260803 | active | actual DB 기준 2차 물가 완료, 3~4차 근본 복구와 상태 정렬 |
