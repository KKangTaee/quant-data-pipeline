# Today Portfolio Intraday Auto Refresh V1 Design

Status: Written Spec Approved
Last Updated: 2026-07-22

## Problem

Today의 대표 포트폴리오는 `nyse_price_history`의 확정 일봉으로 계산한 공통 기준일, 평가액, 현금흐름 조정 수익률, 기여도와 일별 가치곡선을 읽는다. 이 계약은 EOD 분석에는 정확하지만 미국 정규장 진행 중에는 현재 포트폴리오 변화를 보여 주지 못한다.

사용자는 Today 화면을 보고 있는 동안에만 자동으로 가격을 최신화하고, 수집 중 로딩 화면 없이 5분마다 장중 평가액·수익률·그래프가 자연스럽게 바뀌기를 원한다. 모든 provider 결과는 화면 표시 전에 DB에 저장되어야 한다.

## Chosen Approach

`Streamlit fragment heartbeat + process-level background executor + DB snapshot + React live overlay`를 사용한다.

다른 접근은 채택하지 않는다.

- fragment 안에서 provider 수집을 동기 실행하면 구현은 단순하지만 Streamlit running state와 잠깐의 화면 정지가 보일 수 있다.
- 별도 WebSocket/SSE API는 가장 push-like하지만 서버·인증·배포 경계가 새로 생겨 현재 범위에 과하다.
- React의 provider 직접 호출은 `Ingestion -> DB -> Loader -> UI` 경계를 깨고 CORS·credentials·DB persistence를 우회하므로 금지한다.

## Activation And Cadence

- 자동 갱신은 별도 toggle 없이 Today 화면이 열린 동안 활성화한다.
- Python이 제공한 market-session payload가 `calendar_quality=CONFIRMED`이고 resolved phase가 `OPEN`일 때만 intraday collection을 허용한다.
- lightweight heartbeat는 `st.fragment(run_every=15)`로 DB 최신 snapshot, due state와 background future 완료 여부만 확인한다.
- provider collection cadence는 group별 300초다. 15초 heartbeat가 반복되어도 DB의 마지막 attempt snapshot 시각에서 300초 전에는 새 job을 만들지 않는다.
- Today를 벗어나면 fragment heartbeat가 멈춘다. 별도 상시 daemon은 만들지 않는다.
- PRE_OPEN, CLOSED, HOLIDAY, WEEKEND, STALE/LIMITED에서는 intraday job을 제출하지 않는다.

## Ownership And Components

### Collection And Persistence

- 기존 `finance/data/market_intelligence.py` quote-fast normalization과 `upsert_intraday_snapshot_rows`를 재사용한다.
- collector는 explicit symbol list와 group-scoped universe code를 받을 수 있는 좁은 경계를 추가한다.
- universe code는 `TODAY_`와 `portfolio_group_id` SHA-256 앞 16자를 결합한 값으로 고정한다. `VARCHAR(32)` 범위 안에서 group별 snapshot을 분리하고 broad `SP500/TOP1000/TOP2000/NASDAQ` snapshot을 오염시키지 않는다.
- `source_ref`에는 compact `portfolio_group_id=<id>`와 quote source를 남긴다.
- business key는 기존 `(universe_code, symbol, interval_code, snapshot_time_utc)`를 유지한다. snapshot timestamp는 UTC minute로 정규화되어 동일 실행 replay가 UPSERT된다.
- 기본 source는 기존 Yahoo quote-fast path이고, provider timestamp, previous close, latest price, volume, provider status와 error를 보존한다.
- batch-level provider exception도 requested symbol별 `provider_status=error` row로 정규화해 같은 snapshot minute에 저장한다. 따라서 실패한 attempt도 durable cadence 기준이 되고 15초마다 재시도되지 않는다.

### Background Coordinator

- Today 전용 coordinator는 `ThreadPoolExecutor(max_workers=1)`를 process-level cached resource로 소유한다.
- fragment는 job을 기다리지 않고, due하며 실행 중 future가 없을 때만 제출한다.
- 여러 browser session·worker의 중복을 막기 위해 group hash 기반 MySQL advisory lock을 획득한 job만 provider를 호출한다.
- DB latest attempt snapshot이 300초 이내면 lock을 얻어도 skip한다. process restart로 in-memory future가 사라져도 DB due-check가 복구 기준이다.
- 5분마다 생성되는 job result를 JSONL run history에 append하지 않는다. per-symbol outcome과 attempt time은 snapshot table이 소유하고, compact aggregate status는 현재 Streamlit session state와 operational log에만 남긴다. raw quote payload는 어느 쪽에도 저장하지 않는다.

### Loader And Today Read Model

- loader는 현재 default portfolio group의 expected direct-security symbol과 group-scoped latest snapshot을 함께 읽는다.
- quote freshness는 provider `quote_time_utc` 기준으로 계산하고 10분을 넘으면 `STALE`로 처리한다.
- Today payload는 historical EOD portfolio와 분리된 `portfolio.live` projection을 가진다.
- React는 provider나 DB를 직접 읽지 않고 Python payload만 표시한다.

## Live Valuation Semantics

- 대상은 status가 `active` 또는 `data_review`인 direct stock·ETF다.
- selected strategy와 ended item은 intraday quote 대상이 아니다. selected strategy는 마지막 EOD 가치로 group live total에 유지한다.
- Python은 기존 position ledger, entry-price, cashflow와 direct-security value-lane 계약을 재사용하고 terminal observation만 fresh quote로 평가한다. React가 shares나 수익률을 재계산하지 않는다.
- 오늘 추가매수·일부매도 등 external flow가 있으면 기존 Modified Dietz weight 0.5 정책을 적용한다.
- live group value는 fresh direct-security live value, EOD-held selected-strategy value와 기존 cash component의 합이다.
- `live_daily_return`은 직전 confirmed EOD group unit value에서 live unit value까지의 flow-adjusted 변화다.
- `live_total_return`은 기존 누적 unit value에 live daily return을 연결한 임시 값이다.
- 종목별 live return과 contribution도 Python이 동일 terminal quote로 계산한다.

## Partial Coverage

- 모든 direct security가 fresh하면 `LIVE_READY`다.
- 일부 quote가 missing/error/stale이면 해당 item은 마지막 confirmed EOD value를 유지하고 group status는 `LIVE_PARTIAL`이다.
- UI는 `직접 종목 9/10개 장중 반영`처럼 분모·분자를 표시한다. fallback item을 최신화된 것처럼 표현하지 않는다.
- 모든 quote가 실패하면 historical EOD payload를 그대로 표시하고 live chart point를 만들지 않는다.
- selected strategy는 direct quote coverage 분모에 포함하지 않는다.

## React Presentation

- stable Streamlit component key를 유지해 fragment rerun 때 iframe을 교체하지 않고 새 render payload를 전달한다.
- 값 변화는 짧은 numeric/color transition으로 바꾸고 full-screen spinner, skeleton reset, loading overlay를 사용하지 않는다.
- 현재 평가액, 오늘 장중 수익률, 누적 수익률, contributor card에 `장중 임시` label과 quote time을 표시한다.
- historical chart는 confirmed daily-close rows를 그대로 유지한다.
- fresh live projection이 있으면 마지막 confirmed EOD point에서 quote timestamp의 한 개 live point로 dashed segment를 추가하고 hollow marker와 `장중 임시` label을 사용한다.
- live point는 historical daily observation count, MDD, CAGR 또는 EOD curve에 합산하지 않는다.

## Close Handoff

- scheduled close boundary를 지나면 intraday collection을 즉시 중단하고 live point를 종가로 재명명하지 않는다.
- confirmed trading day의 scheduled close 5분 후부터 default portfolio direct stock·ETF가 당일 `nyse_price_history`에 없는 경우 기존 `run_portfolio_price_refresh` EOD 경로를 background로 한 번 제출한다.
- provider delay에 대비해 화면이 열린 동안 5분 간격, 최대 6회까지 bounded retry한다. 이후에도 부족하면 `종가 반영 대기`와 missing symbol count를 유지한다.
- Today를 장 마감 후 처음 열었을 때 EOD가 stale하면 같은 bounded catch-up을 시작한다.
- 모든 direct-security EOD row가 당일 session date에 도달하면 historical read model을 다시 계산하고 live overlay를 제거한다.
- early close는 official schedule의 actual close boundary를 사용한다. 프리마켓·애프터마켓 quote는 수집하거나 handoff 근거로 사용하지 않는다.

## Failure And Recovery

- calendar LIMITED/STALE: 자동 job 없음, 기존 EOD 화면 유지.
- repository/default group 없음: 자동 job 없음, 기존 Today empty/unavailable 계약 유지.
- background exception: requested symbol별 error snapshot을 저장하고 기존 화면을 유지한다. 현재 session에는 compact failure status와 다음 due 시각만 두며, 300초 뒤 다시 시도할 수 있다.
- lock contention: 정상 skip이며 사용자 오류로 표시하지 않는다.
- provider partial: DB에 per-symbol provider status를 저장하고 partial coverage로 표시.
- process restart: in-memory future는 잃어도 DB snapshot time, EOD freshness와 advisory lock으로 다음 heartbeat가 복구한다.

## Expected File Boundaries

- `finance/data/market_intelligence.py`: explicit bounded portfolio symbol collection과 기존 snapshot UPSERT reuse
- `app/services/portfolio_monitoring/intraday_refresh.py`: eligibility, group scope, due/lock, live valuation과 close handoff service
- `app/services/today.py`: EOD와 live projection composition
- `app/web/today_page.py`: fragment heartbeat, background submission, DB-only reload
- `app/web/streamlit_components/today_workbench/src/`: typed live payload, transitions, chart live point와 freshness copy
- `tests/test_today_home.py`와 focused new service tests: Python contracts
- Today React Vitest: phase/cadence-independent presentation contracts
- task docs와 durable data/flow docs: closeout sync

## Verification

- pure tests: eligible items, group hash, 300초 due boundary, confirmed OPEN gate, stale quote, partial/all-failed coverage, selected-strategy exclusion, Modified Dietz live result, exact close handoff와 bounded retry
- collector tests: explicit symbol batch, alias, per-symbol status, group-scoped UPSERT, broad universe isolation
- coordinator tests: non-blocking submit, single in-flight future, DB lock contention, process-restart recovery contract
- React tests: live labels, transition payload, dashed point, partial coverage, no live point after close
- regression: Today market session, EOD curve, contributor semantics, Portfolio Monitoring EOD price refresh, Market Movers broad intraday snapshots
- actual Browser QA: regular-session desktop·760px·420px, no page-level loading/reset, value/graph update after new DB snapshot, console error 0
- close fixture/controlled-clock QA: live point removal, `종가 반영 대기`, confirmed EOD replacement

## Approved Roadmap

1. `1/4차` collection, group-scoped DB persistence and deduplication
2. `2/4차` non-blocking fragment coordinator and five-minute cadence
3. `3/4차` live valuation/read model/React graph and return overlay
4. `4/4차` close handoff, regression, actual responsive Browser QA and docs closeout
