# Market Research IA Redesign V1 Risks

Status: Complete
Last Updated: 2026-07-22

## Resolved Risks

1. structural contract는 새 page-global banner 부재와 direct renderer ownership으로 migration했다.
2. legacy `market-context`와 Today CTA는 `economic-cycle` canonical view로 수용한다.
3. Market Movers handoff는 현재 selected symbol과 event symbol을 대조한 뒤 session/query를 변경한다.
4. page title과 module body heading 계층을 유지하고 중복 module title만 선택적으로 숨긴다.
5. 420px에서 primary 3등분과 secondary 2열 wrap, overflow 0을 actual Browser QA로 확인했다.
6. registry, run history, research bundle, 기존 QA image와 이번 generated screenshot을 stage하지 않았다.

## Residual Validation Gap

- broader service suite의 sentiment overlay 2개와 AAII parser 1개 실패는 이 task 이전부터 재현되며, 이 task diff가 해당 service/parser를 변경하지 않는다. 별도 sentiment task에서 다룬다.

## Deferred

- separate Stock Research page
- sticky research navigation
- global research search
- new data source or scoring model
