# Overview Market Movers Liquidity Universe V1

## 이걸 하는 이유?

Market Movers의 Top1000 / Top2000 기준을 stale할 수 있는 `nyse_asset_profile.market_cap` live ranking에서 최근 20거래일 평균 거래대금 기준으로 바꾼다. 사용자는 coverage 전환, 일중 스냅샷 갱신, 유니버스 기준 갱신을 헷갈리지 않고 실행해야 한다.

## Roadmap

1. 1차: `market_liquidity_universe_member` 저장 기반 추가.
   - 범위: schema, writer/reader, table sync.
   - 완료 조건: materialized Top universe rows를 rank 순서로 저장/조회하고 이전 rows를 inactive 처리한다.
2. 2차: Top1000 / Top2000 materialize job 추가.
   - 범위: listing 후보 조회, EOD 1d 보강, 20D 평균 거래대금 재계산/저장 action.
   - 완료 조건: action 하나가 price history refresh와 universe membership refresh를 함께 수행한다.
3. 3차: Market Movers UI의 `유니버스 기준 갱신` 활성화.
   - 범위: React/fallback action dispatch.
   - 완료 조건: Top coverage에서 disabled 버튼 대신 갱신 action이 실행된다.
4. 4차: Market Movers read path와 intraday snapshot이 materialized universe를 사용하도록 전환.
   - 범위: service read model, intraday snapshot loader.
   - 완료 조건: coverage 탭 전환 시 live 20D ranking query를 반복하지 않는다.
5. 5차: 가격 이력 갱신 노출 정리와 copy 정렬.
   - 범위: refresh action UX, basis labels, user-facing wording.
   - 완료 조건: primary user flow는 `일중 스냅샷 갱신`, `유니버스 기준 갱신`, `화면 새로고침`으로 읽힌다.
6. 6차: durable docs, smoke, Browser QA, final verification.
   - 범위: docs/data, docs/flows 또는 runbook, root handoff, QA.
   - 완료 조건: 테스트/py_compile/diff check/가능한 DB smoke/UI screenshot 결과를 남긴다.

## Tradeoff

Top1000 / Top2000은 이제 "가장 큰 기업"이 아니라 "최근 거래대금이 큰 종목" 기준이다. 신규 상장 종목은 listing source와 EOD price history에 들어온 뒤에만 포함될 수 있다.
