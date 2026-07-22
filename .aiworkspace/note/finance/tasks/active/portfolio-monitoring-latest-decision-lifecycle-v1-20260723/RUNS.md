# Portfolio Monitoring Latest Decision Lifecycle V1 Runs

- 2026-07-23: current registry 6 rows가 모두 `SELECT_FOR_PRACTICAL_PORTFOLIO`, `monitoring_candidate=true`임을 read-only로 확인했다.
- 2026-07-23: 과거 selected와 최신 hold가 같은 source에 있어도 기존 catalog가 과거 selected를 반환하는 최소 재현을 확인했다.
- 2026-07-23: Portfolio Monitoring catalog/selected-strategy focused tests 11개가 현재 baseline에서 통과했다.
- registry, saved setup, run history는 변경하지 않았다.
