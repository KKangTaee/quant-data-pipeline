# Risks

- limited-history issue는 provider가 반환한 실제 row만 설명하며 신규 상장/분할 원인을 단정하지 않는다.
- symbol의 row count가 이후 threshold를 충족하면 preflight는 issue row가 남아 있어도 정상 계산 경로를 우선해야 한다.
- provider full-window 실행 전 단순 DB partial 상태를 limited-history로 오인하지 않도록 issue 생성은 refresh 후 재검증에서만 수행한다.
- 현재 열린 blocker는 없다. `market_data_issue`에 자동 resolve lifecycle은 없지만, preflight가 현재 row count를 먼저 평가하므로 stale issue가 수집 가능 종목을 막지 않는다.
