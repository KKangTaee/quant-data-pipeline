# Today Portfolio Intraday Auto Refresh V1 Plan

Status: 3/4 Complete
Roadmap: 3/4 implementation stages complete
Last Updated: 2026-07-23

## 이걸 하는 이유?

Today의 대표 포트폴리오는 현재 확정 종가 기반 가치와 수익률만 표시한다. 사용자가 미국 정규장 진행 중 Today를 보고 있을 때는 별도 수동 조작과 화면 로딩 없이 현재 시장가를 5분마다 DB에 저장하고, 장중 평가액·수익률·기여도·그래프가 자연스럽게 바뀌어야 한다.

## Goal

Today 화면이 열려 있고 official calendar가 확인된 미국 정규장 `OPEN` 상태일 때, 대표 포트폴리오의 활성 direct stock·ETF 가격을 5분 주기로 비동기 수집·DB 저장하고 live portfolio overlay를 표시한다. 장 마감 후에는 장중 값을 종가로 간주하지 않고 당일 확정 일봉으로 전환한다.

## Scope

- 화면-open + confirmed regular session `OPEN`에서만 자동 수집
- provider cadence 5분, lightweight DB/future check 15초
- 대표 포트폴리오의 활성 direct stock·ETF 최대 10개
- 기존 `market_intraday_snapshot`의 group-scoped universe code와 idempotent UPSERT 재사용
- process-level background executor와 DB advisory lock / due-check
- DB snapshot 기반 장중 평가액, 당일·누적 수익률, 종목별 기여도, chart live point
- selected strategy는 마지막 확정 EOD 값 유지
- 장 마감 후 bounded EOD refresh와 `nyse_price_history` 확정 종가 handoff
- Today React stable-key update와 값·점 전환 animation

## Out Of Scope

- 프리마켓·애프터마켓
- 1분 이하 실시간 시세 또는 tick stream
- React/browser의 provider 직접 호출
- WebSocket/SSE용 별도 API 서버
- 장중 snapshot을 `nyse_price_history.close`로 복사
- broker order, account sync, auto rebalance
- selected strategy의 가상 실시간 가격 생성

## Tentative Roadmap

1. `1/4차` — 포트폴리오 전용 장중 수집·DB 저장·중복 방지
2. `2/4차` — 화면-open 비동기 coordinator와 5분 cadence
3. `3/4차` — live 평가액·수익률·기여도·graph overlay
4. `4/4차` — 장 마감 EOD handoff, 회귀, actual responsive Browser QA

## Stop Condition

대표 포트폴리오 direct stock·ETF의 장중 quote가 5분보다 자주 provider에 요청되지 않고 DB에 group scope로 저장되며, Today가 spinner나 전체-page rerun 없이 새 snapshot을 표시한다. partial/missing quote는 명시되고, confirmed EOD가 저장되기 전에는 live point를 종가로 취급하지 않으며, 장 마감 후 확정 일봉으로 안전하게 전환되어야 한다.

## Implementation Plan

- 승인된 설계를 TDD 단위로 분해한 실행 계획: `IMPLEMENTATION_PLAN.md`
- 구현 시작 방식은 subagent-driven 또는 inline execution 중 하나를 선택한다.
