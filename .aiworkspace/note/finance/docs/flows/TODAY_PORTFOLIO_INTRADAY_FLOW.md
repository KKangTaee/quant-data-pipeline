# Today Portfolio Intraday Flow

Status: Active
Last Verified: 2026-07-23

## 목적

Today를 보고 있는 동안 미국 정규장에 한해 대표 포트폴리오의 direct stock·ETF 현재가를 5분마다 DB에 저장하고, 확정 종가 기반 이력을 훼손하지 않으면서 평가액·수익률·기여도와 그래프를 자연스럽게 갱신한다.

## Runtime Flow

```text
Today 15초 fragment heartbeat
  -> official calendar quality와 regular-session phase 확인
  -> OPEN + default group direct stock·ETF 최대 10개
     -> group DB latest attempt가 300초 이상인지 확인
     -> process single-worker + MySQL advisory lock
     -> quote-fast 수집
     -> market_intraday_snapshot TODAY_<group hash> UPSERT
     -> DB latest quote 재조회
     -> position ledger + EOD close + fresh quote로 portfolio.live 계산
     -> stable React component에 live metric/contributor/dashed point 전달
  -> CLOSED
     -> intraday quote 제출 중단
     -> scheduled close +5분부터 EOD freshness 확인
     -> 부족하면 기존 portfolio daily-price refresh를 5분 간격 최대 6회 제출
     -> 당일 direct-security 일봉이 모두 확인되면 live overlay 제거
```

## 의미 계약

- 15초는 화면 heartbeat이지 provider 수집 주기가 아니다. provider attempt는 group별 300초보다 자주 실행되지 않는다.
- `quote_time_utc` age가 600초를 넘거나 price/status가 유효하지 않으면 fresh로 세지 않는다.
- 일부 quote만 fresh하면 나머지 direct item은 마지막 EOD value를 유지하고 `LIVE_PARTIAL` coverage를 표시한다. 모두 실패하면 live point를 만들지 않는다.
- selected strategy는 quote coverage 분모에서 제외하고 마지막 확정 EOD value를 group total에 유지한다.
- live value는 current shares와 EOD market value의 차이인 retained cash를 보존한다. group return은 기존 Modified Dietz 0.5 flow policy를 사용한다.
- historical curve, observation count, MDD, CAGR과 `nyse_price_history`는 intraday overlay 때문에 바뀌지 않는다.

## 장 마감 전환

- scheduled regular close 또는 official early close부터 intraday 수집을 즉시 중단한다.
- close 직후 장중 point를 종가로 이름만 바꾸지 않는다. 당일 일봉이 없으면 `종가 반영 대기`다.
- close +300초부터 existing EOD refresh를 300초 간격 최대 6회 실행한다.
- 당일 direct-security daily date가 모두 확인된 heartbeat에서 workspace를 다시 읽고 `확정 종가`와 EOD curve로 전환한다.
- 프리마켓·애프터마켓, WebSocket/SSE, broker/order, selected-strategy 가상 실시간 가격은 범위 밖이다.

## Failure Recovery

- calendar가 LIMITED/STALE면 자동 quote/EOD job을 제출하지 않는다.
- provider batch exception도 symbol별 error snapshot으로 저장해 15초 retry storm을 막는다.
- partial/missing quote는 EOD fallback이며 최신화된 것처럼 표현하지 않는다.
- process restart 후에도 intraday cadence는 DB snapshot time, EOD 완료 여부는 daily freshness에서 복구한다.
