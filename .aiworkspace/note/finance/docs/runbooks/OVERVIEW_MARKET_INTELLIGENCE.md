# Overview Market Intelligence Runbook

Status: Active
Last Verified: 2026-07-05

## Purpose

이 runbook은 `Workspace > Overview`의 Market Movers, Sector / Industry, Futures Monitor, Sentiment, Events 데이터를 수동, browser-session auto refresh, 또는 scheduled refresh로 갱신하고 정상 여부를 확인하는 절차를 정리한다.

## When To Use

- 장 시작 후 또는 장중에 daily movers snapshot을 새로 보고 싶을 때
- FOMC calendar row를 갱신해야 할 때
- CPI / PPI / Employment Situation / GDP 같은 macro release calendar row를 갱신해야 할 때
- latest S&P 500 movers 또는 수동 ticker의 upcoming earnings event를 갱신해야 할 때
- 선물장 OHLCV와 개장 전 급변 상태를 Overview Futures Monitor에서 확인하고 싶을 때
- CNN Fear & Greed / AAII bearish sentiment context를 갱신하거나 freshness를 확인해야 할 때
- Overview Events / Market Movers 화면이 비어 있거나 오래된 것으로 보일 때
- 브라우저를 켜지 않고 scheduled refresh runner를 cron / launchd / 외부 automation으로 호출하고 싶을 때

## App Startup

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8501
```

브라우저에서 확인한다.

```text
http://localhost:8501
```

이미 포트가 사용 중이면 다른 포트를 지정한다.

## Refresh Order

1. `Workspace > Ingestion > Overview Market Snapshot`
   - `Collect S&P 500 Universe`를 먼저 실행해 current S&P 500 membership을 갱신한다.
   - Nasdaq coverage가 필요하면 `Workspace > Ingestion > 상장 / 상폐 근거 > Nasdaq Symbol Directory current snapshot` 또는 Overview Market Movers의 `유니버스 기준 갱신`을 실행해 latest `nasdaq_symdir_nasdaqlisted` row를 `finance_meta.nyse_symbol_lifecycle`에 저장한다.
   - Top1000 / Top2000 coverage가 필요하면 먼저 listing source를 최신화하고, EOD 1d price / volume row를 확보한 다음, Overview Market Movers의 `유니버스 기준 갱신`으로 `market_liquidity_universe_member`를 다시 materialize한다.
   - `Collect Market Intraday Snapshot`으로 `SP500`, 필요하면 `TOP1000`, `TOP2000` snapshot을 갱신한다. Top coverage의 intraday snapshot은 저장된 liquidity universe membership을 읽는다.
   - Nasdaq-listed daily movers가 필요하면 `NASDAQ` intraday snapshot을 갱신한다. 이 coverage는 Nasdaq Symbol Directory current listing observation 기준이며 Nasdaq Composite / Nasdaq-100 membership proof가 아니다.
   - daily movers는 `finance_price.market_intraday_snapshot`의 latest snapshot을 읽는다.

2. `Workspace > Overview > Market Movers`
   - `Coverage`, `Period`, `Sector`, `Top N`을 선택한다.
   - daily period의 `데이터 갱신` 패널에서 `수동 갱신` 또는 `자동 갱신`을 선택한다.
   - `수동 갱신`에서는 `일중 스냅샷 갱신`을 눌러 새 snapshot을 저장하고, `화면 새로고침`으로 stored DB state를 다시 읽는다.
   - `유니버스 기준 갱신`은 선택 coverage의 membership 기준을 다시 저장한다. `SP500`은 S&P 500 구성 목록, `NASDAQ`은 Nasdaq Symbol Directory current snapshot, `TOP1000` / `TOP2000`은 최근 20거래일 평균 거래대금 ranking membership을 갱신한다.
   - Coverage에서 `Nasdaq-listed current snapshot`을 선택했는데 universe가 비어 있으면 `유니버스 기준 갱신` 또는 Ingestion의 Nasdaq Symbol Directory 수집을 먼저 실행한다.
   - Top1000 / Top2000에서 universe 수가 1000 / 2000보다 작으면 listing source 후보 수, 최신 EOD 가격 row coverage, provider price 누락을 순서대로 확인한다. 최신 거래일 price row가 없는 ticker는 ranking 가능한 후보에서 제외된다.
   - Weekly / Monthly / Yearly 결과는 저장된 EOD 가격 기준이다. Market Movers 기본 화면에서는 별도 `가격 이력 갱신` 버튼을 노출하지 않고, 먼저 `유니버스 기준 갱신`과 `화면 새로고침`으로 membership 기준과 stored DB state를 명확히 분리한다.
   - `자동 갱신`은 현재 선택한 daily coverage 하나만 확인한다. S&P 500은 `browser_safe` / `sp500_intraday`, Top1000은 `intraday` / `top1000_intraday`, Top2000은 `intraday` / `top2000_intraday` job filter를 사용한다.
   - CLI / scheduler dry-run에서는 Nasdaq-listed snapshot도 `standard` profile plan에 표시되며, 단일 job 확인은 `--profile intraday --job nasdaq_intraday --dry-run`으로 한다. 실제 자동 실행은 미국 장중 guard와 cadence를 따른다.
   - 자동 cadence는 S&P 500 5분, Top1000 15분, Top2000 30분 기준이며 Overview가 열려 있는 브라우저 세션에서만 heartbeat가 돈다.
   - `데이터 갱신` 상태 / 액션 바에서 현재 상태, 범위, 가격 모드, 커버리지 %, 다음 확인을 먼저 확인하고, 자동 실행 상세는 `자동 갱신 세부 정보`를 펼쳐 본다.
   - `Return Rank` 탭에서 symbol-level return ranking과 직전 동일 기간 return / momentum delta를 확인한다.
   - `Volume Rank` 탭에서 daily는 당일 거래량 / 거래대금을, weekly / monthly / yearly는 평균 일거래량 / 평균 일거래대금과 기간 합계를 함께 확인한다.
   - `Sector Pulse` 탭에서 선택한 mover set 안에서 평균 return이 강한 sector를 확인한다.
   - `Why It Moved`에서 Return Rank 또는 Volume Rank ticker를 선택하면 먼저 선택 ticker의 movement summary header를 확인한다. Header는 종목 / 회사명 / 섹터 / 산업 / 시가총액, 기간 / 범위 / 순위 기준 / 순위, 수익률 / 직전 수익률 / 모멘텀 변화 / 거래량 / 거래대금을 묶어서 보여준다.
   - Movement header 아래 metadata status strip에서 `조회 상태`, 뉴스 row count 또는 failure, 한국어 뉴스 row count 또는 failure, SEC row count 또는 failure, `조회 시각`, `세션 전용` boundary를 확인한다. `PARTIAL`은 warning 상태이며 complete success가 아니다.
   - `Why It Moved`는 manual catalyst investigation panel이다. 자동 원인 판정기, AI 요약, 감성 분석, article / filing body collector가 아니다.
   - Ticker selectbox 변경은 외부 조회를 실행하지 않는다. `간단 메타데이터 조회` 버튼을 눌렀을 때만 현재 선택 ticker 1개에 대해 bounded news / SEC metadata lookup을 실행한다.
   - `조사 단서`에서 `뉴스 메타데이터`, `한국어 뉴스`, `SEC 공시`, `외부 검색`을 확인한다. Compact news metadata는 제목, 출처 / publisher, 게시 시각, URL만 표시한다. `한국어 뉴스`는 keyless Google News KR RSS metadata/snippet을 `제목 / 출처 / 게시 시각 / 단서 / 열기`로 표시한다. API key나 Naver credential은 필요하지 않으며, RSS failure는 다른 provider row가 있으면 `부분 완료`, 모두 없으면 `실패` / `메타데이터 없음` 상태로 표시한다. Compact SEC metadata는 양식, 공시일, 제목 / description, URL만 표시하고, SEC table은 양식 / 공시일 / 제목 / `열기` 중심으로 표시한다. metadata table의 URL은 클릭 가능한 `열기` link로 표시한다. 조회 상태는 `조회 전`, `완료`, `부분 완료`, `메타데이터 없음`, `실패`를 구분한다. `부분 완료`는 한 provider가 실패했지만 다른 provider row가 있는 상태이며 complete lookup으로 해석하지 않는다.
   - `SEC 공시`는 현재 metadata table-only 상태다. 앱 안에서 filing 원문을 fetch / parse / preview하지 않으며, 공시 원문이나 재무제표 표 확인은 각 row의 official SEC `열기` link로 이동해 확인한다.
   - Yahoo Finance / Google News / SEC company search / IR earnings / Google News KR / Naver News outbound search는 `조사 단서 > 외부 검색` expander의 클릭 가능한 `열기` link table에서 확인한다. 이 링크들은 앱 내부 조회나 저장을 실행하지 않는 보조 research start point이며, 기본 상태는 collapsed다.
   - 조회 결과는 Streamlit session state에만 남는다. DB schema, workflow registry JSONL, saved setup JSONL, run history에는 쓰지 않는다. DB-backed compact metadata는 retention / freshness / replay semantics가 승인된 후속 V2 조건으로만 검토한다.
   - `Returnable Coverage`에서 missing / failed count를 확인한다.
   - `Coverage Diagnostics`에서 missing symbol, reason, recommended action을 확인한다.
   - daily intraday missing row는 `Diagnose Missing Quotes`로 원인 후보를 확인한다. 결과는 `finance_meta.market_data_issue`에 반복 issue로 누적된다.

3. `Workspace > Overview > Sector / Industry`
   - `Coverage`, `Group`, `Period`, `Top N`, `Min Symbols`를 선택한다.
   - `Latest Ranking`에서 equal-weight / cap-weighted return, 구성 종목 수, 대표 symbol, breadth / concentration summary를 확인한다.
   - `Trend`에서 Daily 1M, Weekly 3M, Monthly 12M window의 group 흐름을 보고, `Trend Groups`로 표시할 group을 좁힌다.
   - 같은 `Group` mode 안에서는 `Coverage`, `Period`, `Top N`, `Min Symbols`를 바꿔도 유효한 `Trend Groups` 선택을 유지한다. `Sector`와 `Industry` 선택 기억은 분리된다.
   - Trend chart는 `Heatmap`, `Line`, `Latest Delta` 하위 탭으로 본다. Heatmap은 구간별 양/음 흐름, Line은 경로, Latest Delta는 latest window와 previous window의 변화폭을 빠르게 확인하는 용도다.
   - daily period는 저장된 `market_intraday_snapshot`이 있으면 `Previous Close -> latest quote` 기준을 사용한다.
   - weekly / monthly period는 EOD DB 기준이다. 최신 raw EOD row가 sparse하면 `Effective EOD Date`와 fallback reason이 status에 표시된다.
   - positive return group을 선택하면 해당 group 안의 ticker leaders와 return-share donut을 확인한다. Ticker leader bar는 양수일 때 sector color, 음수일 때 danger red를 사용하고, 직전 동일 기간 return은 얇은 marker로 표시한다.

4. `Workspace > Overview > Futures Monitor`
   - 기본 `관찰 그룹`은 `개장 전 핵심`이다. 기본 후보는 `NQ=F`(지수), `ZN=F`(금리), `CL=F`(원유), `6E=F`(FX), `GC=F`(금), `6J=F`(엔)를 보여준다.
   - `관찰 그룹`은 1차 선택지를 `개장 전 핵심`, `주가지수`, `금리`, `원자재`, `환율`, `전체 보기`로 단순화했다. optional micro / crypto 그룹은 기본 사용 흐름에서 노출하지 않는다.
   - `선물 선택`, `시간 범위`, `차트 봉`, `차트 범위`를 먼저 정한다. `차트 봉`은 저장된 1분봉 row를 표시용으로 `1분 / 5분 / 15분 / 60분` 집계한다.
   - `데이터 갱신` popover에서 `수동` 또는 `60초 자동 확인`을 고른다. `선택 선물 1분봉 갱신`은 현재 선택한 선물만 수집하고, `화면만 다시 읽기`는 DB state를 다시 읽는다.
   - 60초 자동 확인은 브라우저 세션이 열려 있을 때만 동작하며 provider를 매초 호출하지 않는다. 20초 fast mode는 이 화면의 기본 선택지로 노출하지 않는다.
   - 상단 `선물 워크스페이스`, `단기 움직임`, `데이터 상태`를 먼저 본다. 최신 candle이 오래됐으면 차트는 latest stored data를 보여주되 `오래됨`과 갱신 안내를 표시한다.
   - `매크로 컨텍스트`는 core 16개 선물의 저장된 1D OHLCV를 읽어 오늘 기준 시장 해석, 근거 강도, 과거 일관성 점검, 유사 구간, score chip을 보여준다. Futures Macro tab의 React workbench는 command strip, 현재 브리프, score chip, 1W / 1M 흐름, validation state, 근거 drawer를 렌더링한다.
   - Futures Macro tab 첫 진입은 `include_validation=False` snapshot으로 빠르게 렌더링한다. Historical validation은 `과거 점검 불러오기`를 눌렀을 때만 계산되며, `일봉 갱신` / `다시 읽기`는 session validation state를 clear한다.
   - `1W / 1M 흐름`은 저장된 1D 선물의 최근 5거래일 / 20거래일 변화율로 위험선호, 금리 부담, 달러 압력, 안전자산, 원자재 / 물가 흐름을 요약한다. 이 값은 render 중 provider fetch를 실행하지 않는다.
   - `근거 해석 / 원본 데이터`를 열면 `강하게 말하는 근거`, `약한 근거`, `충돌 근거`, `자료 부족`을 먼저 읽고, 그 다음 historical validation / 원본 점수표 / 구성 선물별 기여 / 선물별 일봉 변화 원본을 확인한다.
   - 매크로 일봉이 비어 있거나 근거가 부족하면 `일봉 매크로 데이터 갱신`을 눌러 core 16개 `5y / 1d` backfill을 실행하거나, `Workspace > Ingestion > 선물 OHLCV 수집`에서 `Period=5y`, `Interval=1d`로 수동 실행한다.
   - Historical Validation은 저장된 daily futures row를 point-in-time으로 재계산한 과거 일관성 평가다. 현재 시나리오의 directional sample / hit rate, score threshold sensitivity, score-forward-return relationship을 보되 예측 보장으로 해석하지 않는다. 혼재 시나리오는 억지로 risk-on / risk-off directional hit rule에 넣지 않으며 occurrence count와 hit-rate N/A로 본다.
   - `실시간 선물 차트`에서 선택 symbol을 포함한 최대 6개 미니 캔들 차트를 본다. 더 넓게 보려면 `차트 범위`를 `데이터 있는 전체`로 바꾼다.
   - `진단 / Provider 근거`는 보조 disclosure다. 최신 run status, rows, processed / requested, latest candle time은 여기서 확인한다.
   - Futures Monitor는 시장 컨텍스트 화면이며 live approval, order, broker/account sync, auto rebalance를 만들지 않는다.

5. `Workspace > Overview > Sentiment`
   - `시장 심리 갱신`을 누르면 `collect_market_sentiment` job이 CNN Fear & Greed와 AAII Sentiment Survey를 수집해 `finance_meta.macro_series_observation`에 저장한다.
   - 같은 수집은 `Workspace > Ingestion > 시장 심리 수집`에서도 실행할 수 있으며, CNN / AAII source를 개별 checkbox로 켜고 끌 수 있다.
   - 상단 카드에서 `Sentiment Status`, CNN score / rating, AAII bearish %, AAII bull-bear spread를 먼저 확인한다.
   - `Trend` 탭은 stored CNN score / AAII bearish / bull-bear spread history를 보여주고, `CNN Components`는 CNN component score를 보여준다.
   - `Table` 탭은 source, observation date, staleness, status를 함께 보여준다.
   - 이 화면은 시장 심리 context이며 trade signal, Practical Validation PASS, live approval, order, broker/account sync, auto rebalance로 해석하지 않는다.
   - AAII official page가 automated backend request를 차단하면 job result와 Overview status에 failed / missing state를 남기고 값을 임의 생성하지 않는다.

6. `Workspace > Ingestion > Overview Market Event Calendar > FOMC`
   - 기본은 current year와 next year를 수집한다.
   - 결과는 `finance_meta.market_event_calendar`에 `event_type=FOMC_MEETING`으로 저장된다.

7. `Workspace > Ingestion > Overview Market Event Calendar > Macro`
   - 기본은 current year와 next year를 수집한다.
   - BLS source는 CPI / PPI / Employment Situation release schedule을 읽어 각각 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`로 저장한다.
   - BEA source는 national GDP release schedule을 읽어 `MACRO_GDP`로 저장한다.
   - 결과는 모두 `source_type=official`, `validation_status=official`로 저장된다.
   - BLS가 HTTP 403 등으로 차단되면 BEA가 성공하더라도 job은 `partial_success`가 될 수 있다.
   - BLS 자동 요청이 막히면 BLS 공식 release schedule `.ics` 파일을 브라우저로 내려받아 `BLS Calendar .ics File`에 업로드하고 `Import BLS .ics Calendar`를 실행한다.
   - `.ics` import도 같은 `market_event_calendar` table에 저장되며, Data Health의 Macro Calendar coverage에 포함된다.

8. `Workspace > Ingestion > Overview Market Event Calendar > Earnings`
   - 기본은 `Latest S&P 500 Movers` source를 사용한다.
   - broader coverage는 `S&P 500 Universe Batch`, `Top1000 Batch`, `Top2000 Batch`를 사용한다.
   - broader mode는 `Max Symbols`, `Batch Offset`, `Ticker Cooldown Sec`을 작게 잡아 저빈도로 실행한다.
   - `Nasdaq cross-check`를 켜면 yfinance estimate를 Nasdaq의 무료 earnings calendar endpoint와 날짜 단위로 비교한다.
   - latest movers mode는 stored S&P 500 intraday snapshot이 먼저 있어야 한다.
   - 특정 ticker 확인이 필요하면 `Manual Symbols`를 사용한다.
   - 결과는 `finance_meta.market_event_calendar`에 `event_type=EARNINGS`, `source=yfinance_calendar`, `source_type=provider_estimate`로 저장된다.
   - yfinance-only estimate는 `validation_status=estimate_only`, Nasdaq 확인 row는 `validation_status=cross_checked`, Nasdaq에서 확인하지 못한 row는 `validation_status=not_confirmed`가 된다.
   - 같은 symbol/source의 이전 active estimate는 새 수집 결과가 있으면 `event_status=superseded`로 정리된다.
   - 수집 결과에는 `symbol_diagnostics`가 포함되며 `no_provider_earnings_date`, `outside_window`, `provider_error` 같은 missing / failure reason을 확인할 수 있다.
   - Ingestion 실행 결과와 Overview refresh 결과의 `Earnings Diagnostics` expander에서 issue count, reason count, symbol-level detail을 확인한다.

9. `Workspace > Overview > Events`
   - `All`, `FOMC`, `Earnings`, `Macro` filter를 바꿔 저장 row를 확인한다.
   - `Window`, `Source Type`, `Validation`, `Importance` filter로 캘린더 범위와 source quality를 좁힌다.
   - 상단 summary strip에서 next event, this week, next 30D, needs review counts를 먼저 확인한다.
   - source lane의 FOMC / Earnings / Macro mini card에서 row count, latest collection, review count를 확인한다.
   - `Refresh` popover에서 FOMC / Earnings / Macro refresh button을 실행한다.
   - `Agenda` 탭에서 upcoming / needs review / high impact row를 먼저 확인한다.
   - `Calendar` 탭에서 월별 calendar grid와 event type별 marker를 확인한다.
   - `Quality` 탭에서 source / validation issue와 next action을 확인한다.
   - `Raw` 탭에서 DB row-level detail을 확인한다.
   - `Source Type`에서 FOMC official row와 earnings provider estimate row를 구분한다.
   - `Importance`, `Validation`, `Freshness`, `Quality Action`, `Age Days`, `Event Status`에서 high impact 일정, cross-check 여부, 오래된 earnings estimate, 다음 조치가 필요한 row를 확인한다.
   - Overview의 refresh buttons는 `app/jobs/overview_actions.py` facade를 통해 ingestion job wrapper를 호출한다. UI render 중 직접 외부 source를 scraping하지 않는다.

10. Data Health ownership
   - `Data Health`는 V22부터 `Workspace > Overview` top-level tab이 아니다.
   - Market Context의 `근거: 자료 기준 / 출처 상태`와 `필요 자료 보강`이 현재 brief에 필요한 direct source / refresh 판단을 보여준다. 이 보강은 S&P 500 movers, sentiment, event calendars만 대상으로 하며 Top1000 / Top2000 / Futures refresh는 Market Movers, Futures Macro, 또는 Ingestion 전용 화면에서 실행한다.
   - 상세 run health, 실패 artifact, log, system snapshot은 `Operations > System / Data Health`와 `Workspace > Ingestion`에서 확인한다.
   - local run history와 DB freshness read model은 유지되지만, Overview 첫 화면의 시장 context 흐름을 대신하지 않는다.
   - 이 탭은 DB와 local JSONL만 읽고 외부 provider를 fetch하지 않는다.

11. `Workspace > Overview > Market Movers > 데이터 갱신 > 자동 갱신`
   - `Market Movers > 데이터 갱신`의 `자동 갱신` 모드는 브라우저 세션이 살아 있을 때만 현재 선택한 daily coverage의 due 여부를 확인한다.
   - S&P 500은 `browser_safe` profile을 사용하고, Top1000 / Top2000은 `intraday` profile에 선택 job_id를 넘겨 한 coverage만 실행한다.
   - 브라우저를 닫거나 Overview 페이지 연결이 끊기면 이 자동 check도 멈춘다.
   - 실제 실행 여부는 `overview_automation`의 cadence, US market-hours guard, lock file이 판단한다.
   - 자동 check 중에는 전체 화면을 blocking하지 않고, 같은 `데이터 갱신` 영역에서 다음 갱신까지 남은 시간과 5분 cadence 진행 bar를 표시한다.
   - 남은 시간과 progress bar는 브라우저 JS가 초 단위로 갱신한다. provider collection은 매초 실행되지 않는다.

## CLI Smoke Checks

Overview scheduled refresh dry-run:

```bash
uv run python -m app.jobs.overview_automation --profile standard --dry-run
```

Nasdaq-listed intraday job dry-run:

```bash
uv run python -m app.jobs.overview_automation --profile intraday --job nasdaq_intraday --dry-run
```

브라우저 없이 due job만 실제 실행:

```bash
uv run python -m app.jobs.overview_automation --profile standard
```

Overview를 열어둔 동안만 호출할 1차 browser-safe profile:

```bash
uv run python -m app.jobs.overview_automation --profile browser_safe
```

무료 provider 압력을 낮춘 안전 profile:

```bash
uv run python -m app.jobs.overview_automation --profile safe
```

캘린더만 갱신:

```bash
uv run python -m app.jobs.overview_automation --profile events
```

운영 scheduler에 연결할 때는 5분마다 위 명령을 호출하도록 두고, 실제 실행 여부는 CLI가 run history cadence와 US market-hours guard로 판단한다. 중복 실행은 `.aiworkspace/note/finance/run_artifacts/locks/overview_automation.lock`으로 막는다. `browser_safe` profile은 OS scheduler가 아니라 Overview 브라우저 세션이 열려 있을 때 호출하는 용도이며, 단독 CLI profile로는 S&P 500 daily snapshot만 선택한다. Overview UI에서 Top1000 / Top2000 자동 갱신을 켜면 `intraday` profile에 선택 coverage job_id를 넘겨 단일 job만 실행한다.

작은 수동 earnings smoke:

```bash
uv run python - <<'PY'
from app.jobs.ingestion_jobs import run_collect_earnings_calendar
print(run_collect_earnings_calendar(symbols=["AAPL", "MSFT", "NVDA"], symbol_source="manual", lookahead_days=180, max_symbols=10))
PY
```

latest movers source 확인:

```bash
uv run python - <<'PY'
from finance.data.market_intelligence import load_latest_intraday_mover_symbols
print(load_latest_intraday_mover_symbols(universe_code="SP500", top_n=5))
PY
```

Top1000 / Top2000 liquidity universe 저장 상태 확인:

```bash
uv run python - <<'PY'
from finance.data.market_intelligence import load_market_liquidity_universe_members
for code in ("TOP1000", "TOP2000"):
    rows = load_market_liquidity_universe_members(code)
    latest = rows[0]["as_of_date"] if rows else None
    print(code, len(rows), latest, [row["symbol"] for row in rows[:5]])
PY
```

BEA GDP macro calendar smoke:

```bash
uv run python - <<'PY'
from app.jobs.ingestion_jobs import run_collect_macro_calendar
print(run_collect_macro_calendar(years=(2026,), include_bls=False, include_bea=True))
PY
```

BLS `.ics` file import smoke:

```bash
uv run python - <<'PY'
from pathlib import Path
from app.jobs.ingestion_jobs import run_import_bls_macro_calendar_ics

ics_text = Path("/path/to/bls.ics").read_text(encoding="utf-8-sig")
print(run_import_bls_macro_calendar_ics(ics_text=ics_text, years=(2026,), source_name="bls.ics"))
PY
```

## Expected Results

- Market Movers Coverage includes `S&P 500`, `Top 1000`, `Top 2000`, and `Nasdaq-listed current snapshot`.
- Nasdaq-listed coverage shows `coverage_basis=Nasdaq-listed current snapshot`, `universe_source=nasdaq_symdir_nasdaqlisted`, current snapshot caveat, and Symbol Directory refresh guidance when no lifecycle rows exist.
- Top1000 / Top2000 coverage shows a 20D average dollar volume basis, not market-cap basis. The materialized membership is stored in `finance_meta.market_liquidity_universe_member` and reused by Overview read model and intraday snapshot refresh.
- New listing tickers appear in Top1000 / Top2000 only after the listing source contains the symbol and `finance_price.nyse_price_history` has latest EOD close / volume rows for ranking.
- Market Movers daily snapshot shows `price_mode=Intraday Snapshot` and a recent `snapshot_time_utc`.
- Market Movers daily refresh state shows `Fresh`, `Update due`, `Stale`, `Partial`, or `Failed`.
- Market Movers daily `데이터 갱신` status / action bar shows coverage ratio / percent, next check time, refresh mode, and the recommended next action for SP500 / TOP1000 / TOP2000.
- Market Movers snapshot metadata is shown as a compact strip rather than a separate card grid, so the ranking chart and table stay closer to the controls.
- Market Movers `자동 갱신` follows the selected daily coverage: S&P 500 uses 5-minute `browser_safe`, Top1000 uses 15-minute selected `intraday`, and Top2000 uses 30-minute selected `intraday`.
- Market Movers refresh results expose `Snapshot Diagnostics` with snapshot time, rows written, failed count, method, and provider diagnostics when available.
- Market Movers displays `Return Rank`, `Volume Rank`, and `Sector Pulse` chart tabs.
- Market Movers builds a separate `volume_rows` ranking. Daily ranks the latest stored snapshot / EOD day by dollar volume with raw volume beside it; weekly / monthly / yearly rank average daily dollar volume and expose average / total volume metrics in the Volume table.
- Market Movers return rows include `Volume`, `Dollar Volume`, `Previous Return %`, and `Momentum Delta pp`; positive return bars use sector colors and negative bars use the danger red.
- Market Movers `Why It Moved` renders a ticker selector sourced from Return Rank and Volume Rank rows, then shows a movement summary header with selected ticker identity, rank / coverage / period context, return / previous return / momentum delta, volume, and dollar volume. The visible labels are Korean except the main `Why It Moved` title and source/product names.
- Market Movers `Why It Moved` shows a metadata status strip before the fetch button: `조회 상태`, 뉴스 rows / failure, 한국어 뉴스 rows / failure, SEC rows / failure, `조회 시각`, and `세션 전용` storage boundary. `PARTIAL` / `부분 완료` is warning-level evidence, not a complete lookup.
- Market Movers `Why It Moved` uses `조사 단서` sections for `뉴스 메타데이터`, `한국어 뉴스`, `SEC 공시`, and collapsed `외부 검색`. The `한국어 뉴스` lane is powered by keyless Google News KR RSS and displays metadata/snippet only; no Naver API key, article scraping, or article body storage is required. Yahoo Finance, Google News, SEC company search, IR / earnings, Google News KR, and Naver News stay as collapsed external rows with clickable `열기` URLs instead of primary action buttons.
- Futures Monitor shows the latest stored candle window for each selected symbol even when provider freshness is stale; stale latest candles should appear as `Stale`, not as missing chart data.
- Market Movers `Why It Moved > SEC 공시` preserves the compact SEC table as `양식 / 공시일 / 제목 / 열기`. V1.7 / V1.8 selected-filing preview and `공시 Digest` were rolled back after user review, so this lane currently does not fetch, parse, preview, or store filing bodies; users open official SEC documents through the clickable `열기` links.
- `Why It Moved` remains a manual investigation panel. It does not summarize, crawl, collect article bodies, collect filing bodies, run sentiment analysis, auto-classify catalysts, mutate DB schema, or write workflow JSONL / saved setup rows.
- `간단 메타데이터 조회` is button-only and selected-ticker-only. The not-yet-run state is visible before lookup; `OK`, `PARTIAL`, no metadata, and failed lookup states are separate. Metadata URL columns render as clickable `열기` links. SEC filings are displayed as 양식 / 공시일 / 제목 / 열기 and sorted by date with form-priority tie-breaks.
- Compact metadata is session-only. DB-backed metadata persistence is not part of V1.6 and requires a later V2 storage / freshness / retention decision.
- Sector / Industry displays `Latest Breadth Heatmap`, `Latest Ranking`, trend detail, positive group ticker leaders, and raw tables behind `상세 표`.
- Sector / Industry daily mode uses the stored intraday previous-close snapshot when available; weekly / monthly remain EOD DB based.
- Sector / Industry status distinguishes `Effective Quote Time` from `Effective EOD Date` and explains sparse raw-date fallback.
- Sector / Industry shows `Best Breadth`, `Cap vs Equal`, `Concentration`, and `Improving` insight cards above the latest ranking chart.
- Sector / Industry Trend has `Heatmap`, `Line`, and `Latest Delta` chart tabs, and valid `Trend Groups` selections persist across controls inside the same group mode.
- Sector / Industry Positive Group Detail ticker bars use sector colors for positive returns, danger red for negative returns, and high-contrast previous-period return markers.
- Missing diagnostics are visible with recommended action when provider rows are absent or incomplete.
- Coverage Diagnostics keeps `Reason` / `Recommended Action` and adds compact `Likely Cause`, `Evidence Summary`, `Next Check`, `Listing Evidence`, `Profile Freshness`, and `Market Data Issue` evidence. These are DB-backed hints, not legal status, trading signal, validation gate, or monitoring signal.
- Quote gap diagnostics persist repeated issue history to `finance_meta.market_data_issue` and display occurrence count / latest evidence in Coverage Diagnostics.
- Futures Macro Thermometer shows six standardized daily score cards, scenario summary, mixed-scenario subtype / reason when the top-level scenario is `혼재된 매크로 흐름`, Interpretation Confidence, current scenario directional sample / hit rate or mixed-scenario occurrence count, strong / weak / conflicting evidence groups, score components, symbol-level 1D / 3D / 5D / 20D / 60D returns, 60D volatility standardized move, 252D position, historical validation summary, score threshold sensitivity, false-positive rates, score-forward-return relationships, and caution copy. The `Futures Macro` tab owns explicit `일봉 매크로 갱신` and `최신 데이터 다시 읽기` controls; newly collected daily futures rows invalidate the macro snapshot cache through the latest stored 1D candle marker. Historical validation is lazy-loaded by the `과거 점검 불러오기` button instead of tab entry, and `일봉 갱신` / `다시 읽기` clears the session validation state so the next validation uses the current snapshot.
- FOMC rows have `source=federal_reserve_fomc_calendar`, `confidence=1.0`, and `Source Type=Official`.
- Macro rows have `Type=MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`, or `MACRO_GDP`, `Source Type=Official`, and `Validation=Official`.
- BLS `.ics` import rows keep `source=bureau_labor_statistics_release_schedule` and `raw_payload_json.import_method=official_ics_file`.
- Earnings rows have `source=yfinance_calendar`, `Source Type=Provider Estimate`, and a validation label.
- Nasdaq cross-checked earnings rows have `Validation=Cross-checked` and higher confidence.
- Earnings rows collected more than 14 days ago show `Freshness=Stale estimate` and a warning.
- Earnings job results show `Earnings Diagnostics` when requested symbols are missing, outside the selected lookahead window, or fail at the provider layer.
- Earnings event rows include `Quality Action`; `Estimate only` rows recommend cross-check or closer refresh, stale rows recommend refresh, and cross-checked rows show no action.
- Overview Events displays summary cards, source mini cards, refresh popover, and `Agenda`, `Calendar`, `Quality`, `Raw` tabs with Window / Source Type / Validation / Importance filters.
- Overview Events read model includes `Days Until`, `Importance`, quality / validation fields, and source status summaries; FOMC / macro rows are `High`, earnings rows are `Medium`, and rows with source / validation action show `Needs Review`.
- Overview Events calendar is a month grid with event type markers; agenda and quality views stay available for list/detail inspection.
- Overview Events has a `Macro` filter and `Refresh Macro Calendar` button.
- Overview Events `Latest Collection` updates after a successful collector run.
- Overview Sentiment starts with `시장 심리 컨텍스트`: phase / headline / data confidence, then `시장 심리 읽기 - 6단계` covering current conclusion, why it reads that way, strong signals, weak signals, combined interpretation, and next checks.
- Overview Sentiment then displays CNN Fear & Greed, AAII Bearish, AAII Bull-Bear Spread, CNN component scores, driver groups, CNN component learning notes, next-check links, trend evidence, component detail, and stored row table from `macro_series_observation`.
- Overview no longer renders Data Health as a primary tab. Use Market Context source / refresh evidence for current brief issues and `Operations > System / Data Health` for detailed operational diagnostics.
- Overview refresh buttons route through `app/jobs/overview_actions.py` and append their result to local web app run history; the JSONL file itself remains a generated local artifact and is not committed. Market Context refresh is intentionally scoped to the current Market Context surface and does not run Top1000 / Top2000 / Futures refresh actions.
- Overview scheduled refresh CLI can run without Streamlit and appends scheduled job results to the same local web app run history.

## Failure Handling

| Symptom | Likely Cause | Action |
|---|---|---|
| Earnings latest movers mode writes no rows | No latest S&P 500 intraday snapshot | Run S&P 500 market snapshot first or switch to manual symbols |
| Some earnings symbols are missing | yfinance calendar has no upcoming date, date is outside the selected window, or provider request failed | Open `Earnings Diagnostics`; retry with wider lookahead for `outside_window`, retry later for `provider_error`, or inspect ticker manually for `no_provider_earnings_date` |
| Earnings row is not confirmed | Nasdaq cross-check did not find the same symbol on that event date | Treat as provider estimate only; refresh later or inspect company IR manually |
| Old earnings date remains in DB | Estimate date changed | Overview hides superseded rows by default; inspect DB if an audit trail is needed |
| Market Movers missing count is high | Provider quote rows missing or DB previous close missing | Open `Coverage Diagnostics`, then refresh OHLCV / snapshot source if needed |
| Nasdaq coverage is empty | No latest `nasdaq_symdir_nasdaqlisted` lifecycle rows exist locally | Run `Nasdaq 목록 갱신` in Market Movers or the Ingestion Nasdaq Symbol Directory current snapshot collector |
| Nasdaq coverage is confused with an index | Symbol Directory rows are listing observations, not index constituents | Treat the coverage as Nasdaq-listed current snapshot only; do not describe it as Nasdaq Composite or Nasdaq-100 |
| Quote gap occurrence count keeps increasing | The same symbol repeatedly misses the quote endpoint or supporting evidence | Treat it as an operating issue; inspect `market_data_issue`, refresh profile / OHLCV, or keep the symbol under manual review |
| Events tab is empty | Matching collector has not been run or filter is too narrow | Run FOMC / Earnings refresh and select `All` |
| Macro Calendar shows `Due` with covered `1/4` | Only BEA GDP rows are stored; BLS CPI / PPI / Jobs rows are missing or blocked | Import the official BLS `.ics` file, retry BLS later, or treat current Macro view as GDP-only until BLS rows are available |
| Macro collection is partial | BLS schedule page rejected automated access, but BEA or another enabled source succeeded | Inspect failed source message, then use the BLS `.ics` import fallback if CPI / PPI / Jobs rows are needed |
| Market Sentiment collection is partial | CNN or AAII official source changed, blocked the request, or returned an interstitial | Inspect `collect_market_sentiment` job details; refresh later or use Browser check to confirm whether the official public page still shows the table |
| Sentiment tab still shows only raw cards after deployment | Streamlit served an old imported module or cache schema | Restart the Streamlit process and clear the Overview cache via normal app reload; confirm the top `시장 심리 컨텍스트` band and `분석 체크` section are visible |
| Market Context source evidence shows stale S&P 500 daily snapshot | Stored 5m S&P 500 snapshot is older than the intraday freshness threshold | Run Market Context `현재 이슈만 보강` or Market Movers S&P 500 refresh |
| Operations / Ingestion shows blank latest success / issue | No Overview refresh button has written local run history yet | Use the relevant Overview refresh button or inspect Ingestion output directly |
| Scheduled refresh exits as locked | A previous automation run is still active, or a stale lock file remains | Wait for the run to finish; if the process is gone and the lock is older than the stale threshold, rerun after the CLI clears it |
| Overview app looks stale after code change | Old Streamlit process still running | Restart the Streamlit server and confirm Runtime / Build metadata in Ingestion |

## Verification Commands

```bash
uv run python -m py_compile app/web/overview_dashboard.py app/web/overview/page.py app/web/overview/market_context.py app/web/overview/market_movers.py app/web/overview/futures_macro.py app/web/overview/sentiment.py app/web/overview/events.py app/web/overview/components/common.py app/web/overview/components/layout.py app/web/overview/components/market_context.py app/web/overview/components/market_movers.py app/web/overview/components/events.py app/web/overview/components/data_health.py app/web/overview_ui_components.py app/web/streamlit_app.py app/jobs/overview_actions.py app/jobs/ingestion_jobs.py app/jobs/overview_automation.py finance/data/db/schema.py finance/data/market_intelligence.py finance/data/sentiment.py finance/loaders/sentiment.py
uv run python -m unittest tests.test_service_contracts
uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
git diff --check
```

Expected result:

- service contract tests pass
- UI-engine boundary reports `Result: PASS`
- `git diff --check` has no output
