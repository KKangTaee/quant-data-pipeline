# Status

- 2026-07-05: `codex/sub-dev`에서 작업을 다시 시작했다. 잘못 생성한 `codex/market-movers-volume-universe` 브랜치는 삭제했고, 이 task가 현재 실행 기록이다.
- 1차 완료: `market_liquidity_universe_member` schema, writer, reader, sync path를 추가했다.
- 2차 완료: listing lifecycle 후보 조회, 최근 20거래일 평균 거래대금 계산, materialize 함수, Overview action facade를 추가했다.
- 3차 완료: Top1000 / Top2000 daily UI에서 `유니버스 기준 갱신` action을 활성화하고 React/fallback dispatch를 action facade에 연결했다.
- 4차 완료: Market Movers read model과 intraday snapshot 기본 loader를 materialized liquidity universe로 전환했다.
- 5차 완료: Market Movers 기본/React UI에서 `가격 이력 갱신` primary action을 숨기고, coverage별 `유니버스 기준 갱신` action으로 통일했다.
- 현재 차수: 6차 대기.
