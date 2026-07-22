# Market Research IA Redesign V1 Risks

Status: Active
Last Updated: 2026-07-22

## Open Risks

1. 기존 tests가 `Market Context` label과 helper 이름을 structural contract로 검사하므로 compatibility adapter 또는 focused test migration이 필요하다.
2. Today CTA는 legacy `overview_tab=market-context`를 사용하므로 canonical view 확장 뒤에도 반드시 수용해야 한다.
3. Market Movers와 U.S. Stock의 universe/profile 범위가 다를 수 있어 symbol handoff validation을 UI 문자열 복사만으로 처리하면 안 된다.
4. module heading 제거 시 Streamlit fallback의 접근 가능한 heading hierarchy를 잃지 않아야 한다.
5. 420px에서 native Streamlit pills의 실제 wrap/overflow 동작을 Browser QA로 확인해야 한다.
6. actual app render가 registry/run-history local artifact를 갱신할 수 있으므로 commit selection을 path allow-list로 제한한다.

## Deferred

- separate Stock Research page
- sticky research navigation
- global research search
- new data source or scoring model
