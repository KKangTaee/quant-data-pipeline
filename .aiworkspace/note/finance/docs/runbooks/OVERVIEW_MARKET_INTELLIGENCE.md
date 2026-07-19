# Overview Market Intelligence Runbook

Status: Active
Last Verified: 2026-07-19

## Purpose

이 runbook은 `Workspace > Overview`의 Market Context, Market Movers, Futures Macro, Sentiment, Events 데이터를 수동, browser-session auto refresh, 또는 scheduled refresh로 갱신하고 정상 여부를 확인하는 절차를 정리한다.

## When To Use

- 장 시작 후 또는 장중에 daily movers snapshot을 새로 보고 싶을 때
- FOMC calendar row를 갱신해야 할 때
- CPI / PPI / Employment Situation / GDP 같은 macro release calendar row를 갱신해야 할 때
- latest S&P 500 movers 또는 수동 ticker의 upcoming earnings event를 갱신해야 할 때
- 저장된 선물 OHLCV와 일봉 매크로 상태를 Overview Futures Macro에서 확인하고 싶을 때
- CNN Fear & Greed / AAII bearish sentiment context를 갱신하거나 freshness를 확인해야 할 때
- Overview Events / Market Movers 화면이 비어 있거나 오래된 것으로 보일 때
- Market Context의 S&P/Nasdaq valuation source와 coverage gate를 갱신할 때
- Market Context 경제 사이클 vintage를 수집하고 학습·검증·current/10년 replay snapshot을 명시적으로 materialize할 때
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

## Economic Cycle Vintage / Model Refresh

이 작업은 화면 render나 unattended Overview scheduler가 실행하지 않는다. 운영자가 `FRED_API_KEY`를 설정하고 backend에서 명시적으로 실행한 뒤, `Workspace > Overview > Market Context > 경제 사이클`은 저장된 compact snapshot만 읽는다.

### 1. Prerequisite와 schema

```bash
export FRED_API_KEY='<local secret>'
uv run python -c "from finance.data.economic_cycle_vintages import ensure_economic_cycle_vintage_schema; from finance.data.economic_cycle_results import ensure_economic_cycle_result_schemas; ensure_economic_cycle_vintage_schema(); ensure_economic_cycle_result_schemas(); print('economic-cycle schemas ready')"
```

- credential과 raw provider payload를 문서, run history, commit에 남기지 않는다.
- 생성 대상은 `macro_series_vintage_observation`, `economic_cycle_model_artifact`, `economic_cycle_snapshot` 세 table이다.
- `FRED_API_KEY`가 없으면 vintage collection은 `failed`여야 한다. revised FRED CSV로 대체하지 않는다.

### 2. Locked 17-series vintage collection

```bash
uv run python -c "from app.jobs.ingestion_jobs import run_collect_economic_cycle_vintages; print(run_collect_economic_cycle_vintages())"
```

확인할 내용:

- `source_mode=fred_output_type_1_realtime_intervals`와 series별 row/date coverage
- large-series default는 observation page 50,000행, timeout 60초다. 현재 catalog의 full bootstrap 기대치는 17 series / 1,232,856 rows이며 ANFCI가 1,014,042 rows를 차지한다.
- raw unique key `(series_id, observation_date, realtime_start, source)`
- 동일 범위 재실행 뒤 business row 수가 증가하지 않는지
- `.`/non-finite value가 0이 아니라 `coverage_status=missing` row로 남는지

### 3. Train, validate, current materialization

아래 날짜는 latest fully available month에 맞게 운영자가 지정한다.

```bash
uv run python -c "from finance.economic_cycle_pipeline import train_validate_economic_cycle_model, materialize_economic_cycle_snapshot; trained_through='YYYY-MM-DD'; as_of_date='YYYY-MM-DD'; result=train_validate_economic_cycle_model(trained_through=trained_through); print(result['model_version'], result['publication_status']); print(materialize_economic_cycle_snapshot(as_of_date=as_of_date, model_version=result['model_version'], artifact_row=result['artifact_row']))"
```

- h0/h1/h2별 origin count, phase support, recession episode, complete-feature ratio, Brier, log loss, ECE, persistence/historical-transition baseline, reason code를 확인한다.
- horizon별 gate는 `READY/LIMITED` publication status를 결정한다. 완전한 artifact와 입력으로 계산 가능한 LIMITED horizon은 숫자 확률을 snapshot에 보존하고 UI에서 `잠정 모델 추정`으로 표시한다. READY는 `검증된 모델 추정`, phase support·parameter·입력이 불완전하면 `판단 불가`다.
- validation metadata 누락이나 실행 오류가 있으면 latest approved artifact/snapshot을 ERROR row로 덮지 않는다.

### 4. Ten-year month-end replay와 idempotence

```bash
uv run python -c "from finance.economic_cycle_pipeline import replay_economic_cycle_history; print(replay_economic_cycle_history(start_date='YYYY-MM-DD', end_date='YYYY-MM-DD'))"
```

- 각 origin은 직전 month-end까지 학습한 origin-specific artifact와 그 origin 당시 eligible vintage를 사용한다.
- 같은 날짜 범위를 한 번 더 실행하고 `(as_of_date, model_version, run_kind)` business key가 중복되지 않는지 확인한다.
- payroll series 한 origin과 recession-era 한 origin을 표본으로 골라 stored eligible `realtime_start/realtime_end`가 official FRED/ALFRED response metadata와 일치하는지 확인한다.

### 5. Failure / recovery

- `FRED_API_KEY` 부재: 수집을 중단하고 UI의 `NOT_MATERIALIZED` 또는 latest-good LIMITED/READY snapshot을 유지한다.
- sparse coverage/calibration/origin/baseline 성능 미달: 해당 horizon을 `LIMITED`로 두고 계산 가능하면 잠정 추정으로 공개한다. threshold를 낮추거나 artifact status를 손으로 바꾸지 않는다.
- missing phase support 또는 불완전 parameter/input: 해당 horizon은 `UNAVAILABLE`로 materialize하고 다른 horizon·origin 처리는 계속한다.
- stale/vintage gap: missing series/date/revision interval을 공식 API에서 보강한 뒤 collection부터 재실행한다.
- 화면은 run/job/row 진단 panel이 아니다. 운영 근거는 backend 결과와 DB audit에서 확인하고 사용자는 국면 확률, evidence, source date, 제한 사유를 읽는다.

## Valuation Refresh

Nasdaq-100 QQQ proxy job의 due/skip 계획과 강제 실행은 아래처럼 확인한다.

```bash
.venv/bin/python -m app.jobs.overview_automation --profile safe --job nasdaq100_valuation --dry-run
.venv/bin/python -m app.jobs.overview_automation --profile safe --job nasdaq100_valuation --force --json
```

이 job은 SEC QQQ holdings, QQQ EOD, stored DB 기반 monthly materialization을 순서대로 실행한다. `success`는 파이프라인 실행 성공이지 valuation coverage 통과를 뜻하지 않는다. `finance_meta.nasdaq100_monthly_valuation.data_quality=blocked`와 `coverage_weight_pct < 95`이면 UI는 그래프 대신 coverage blocker를 표시한다.

blocker가 표시되면 같은 카드의 `60개월 가치평가 자료 보강`을 누른다. 화면은 최근 60개월 historical holdings universe에서 부족한 분기 EPS와 EOD만 계획하고, canonical ingestion job으로 종목별 UPSERT한 뒤 60개월을 다시 materialize한다. 실행 중에는 같은 화면에서 단계별 진행 상태를 표시하며 완료까지 기다린다. React는 action intent만 전달하고 SEC/가격 수집, DB write, cache clear와 재계산은 Python job 경계가 맡는다.

Expected result:

- job result의 `details.steps`에 `SEC QQQ holdings`, `QQQ EOD`, `Nasdaq-100 monthly proxy`가 각각 남는다.
- 동일 source/business key 재실행은 새 중복 row를 만들지 않는다.
- 95% 미만 monthly row는 `blocked`와 error reason을 유지한다.
- 보강 뒤 60개월 모두 95% gate를 통과하면 blocker 대신 Nasdaq-100 QQQ proxy 그래프가 표시된다.
- `EarningsPerShareBasicAndDiluted`는 기본/희석 EPS가 동일하다고 공시한 US-GAAP actual이므로 diluted EPS fallback으로 허용한다. 별도 basic EPS나 FY-only proxy는 허용하지 않는다.

Failure handling:

- 한 source step이 실패하면 `partial_success`와 step message를 확인하고 latest-good DB row로 materialization/read가 가능한지 분리해 본다.
- schema bootstrap failure는 전체 `failed`다. `finance_meta` 연결과 `schema.py` sync 결과를 먼저 확인한다.
- `부분 완료` 뒤에도 blocker가 남으면 `남은 자료 다시 보강`으로 transient 실패만 재시도한다. 무료 원천에서 확보할 수 없는 acquired/delisted EOD, foreign/FY-only, unresolved identity는 합성하거나 95% gate를 낮추지 않는다.
- 화면 action이 실패하면 기존 latest-good cache를 유지한다. 로그의 failed symbol과 `market_data_issue.limited_price_history` evidence를 확인한 뒤 재시도한다.

Related docs: [Data Flow Map](../data/DATA_FLOW_MAP.md), [Table Semantics](../data/TABLE_SEMANTICS.md), [coverage repair task status](../../tasks/active/overview-market-context-nasdaq100-coverage-repair-action-v1-20260713/STATUS.md).

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
   - `Coverage trust detail` 또는 상단 action bar에 `티커 변경 복구 적용`이 보이면 old ticker가 Yahoo quote row를 반환하지 않고 replacement ticker 후보가 탐지된 상태다.
   - `티커 변경 복구 적용`을 누르면 candidate alias가 `finance_meta.market_symbol_alias`에 active로 저장된다. 이 버튼은 가격 row를 즉시 다시 쓰지 않는다.
   - 복구 적용 후 `일중 스냅샷 갱신`을 다시 실행한다. 새 snapshot은 universe symbol은 유지하고 quote lookup만 active alias ticker를 사용해 `finance_price.market_intraday_snapshot.quote_symbol`에 남긴다.
   - 복구 후에도 missing이 남으면 `Diagnose Missing Quotes`로 provider coverage, listing evidence, previous-close coverage를 다시 확인한다.
   - daily intraday missing row는 `Diagnose Missing Quotes`로 원인 후보를 확인한다. 결과는 `finance_meta.market_data_issue`에 반복 issue로 누적된다.

3. `Workspace > Overview` sector evidence
   - `Sector / Industry`는 current primary tab이 아니다. Sector 흐름은 `Market Context`의 sector pressure / breadth evidence와 `Market Movers`의 `Sector Pulse` / group leadership에서 확인한다.
   - `Market Movers`에서는 `Coverage`, `Period`, `Sector`, `Top N`을 바꿔 선택 mover set 안의 평균 return, breadth, concentration, leading symbols를 확인한다.
   - daily period는 저장된 `market_intraday_snapshot`이 있으면 `Previous Close -> latest quote` 기준을 사용한다.
   - weekly / monthly / yearly period는 EOD DB 기준이다. 최신 raw EOD row가 sparse하면 effective date와 fallback reason을 먼저 확인한다.
   - Market Context의 sector pressure map은 provider sector alias를 canonical sector로 normalize해 동일 크기 tile로 보여준다. tile 크기가 아니라 색상 / 값 / breadth를 읽는다.

4. `Workspace > Overview > Futures Macro`
   - 이 tab은 저장된 주요 선물 1D OHLCV로 만든 compact macro snapshot을 읽는 current primary surface다. 화면 진입 중 provider fetch나 5D / 20D 전망 계산을 실행하지 않는다.
   - `일봉 갱신`은 주요 선물 `5y / 1d`를 수집한 뒤 current macro와 5D / 20D 조건부 전망을 `finance_meta.futures_macro_snapshot`의 `overview_current` row로 materialize한다. 1m 수집은 이 snapshot을 갱신하지 않는다.
   - `다시 읽기`는 provider 수집이나 전망 계산 없이 저장된 compatible snapshot만 다시 읽는다. snapshot이 없거나 schema/algorithm version이 맞지 않으면 `일봉 갱신 필요` 상태를 표시한다.
   - 첫 화면은 현재 체제, 현재/다음 1주/다음 1개월, `20D 전 → 5D 전 → 현재` 관측과 선택 horizon 예상 순이동·말일 도착 범위, 근거, 60D ribbon, 자산별 확인 포인트 순으로 읽는다.
   - 5D / 20D 확률과 예상 위치는 과거 유사 episode의 조건부 빈도·중앙 이동이며 미래 보장이나 가격 목표가 아니다. 방향 우위가 검증 gate를 넘지 못하면 `PROVISIONAL`과 `방향 우위 미확인`을 유지한다.
   - 현재 관측은 `관측 완료 / 일부 관측 / 관측 불가`, 미래 분포는 `VERIFIED / PROVISIONAL / UNAVAILABLE`로 분리한다. 미래 전망이 잠정이어도 현재 저장 자료가 완전하면 현재 관측을 잠정으로 낮추지 않는다.
   - `방법론과 품질`은 원천, 독립 표본, Brier, baseline, calibration, 제한을 보여준다. 펼침 높이는 React component가 Streamlit iframe과 동기화한다.
   - React `원본 데이터 / 계산 추적`은 snapshot 기준일/저장 시각/source marker와 compact `현재 점수 원본`, `점수 구성 기여`, `선물 일봉 변화`, 해석 주의점을 보여준다. 전체 10년 OHLCV 원본은 이 disclosure가 아니라 `finance_price.futures_ohlcv`에 남는다.
   - 일봉 수집 성공 뒤 materialization만 실패하면 job은 `partial_success`다. 이전 latest-good snapshot은 지우지 말고 attached materialization result를 확인한 뒤 일봉 갱신을 재시도한다.
   - Futures Macro는 시장 컨텍스트 화면이며 live approval, order, broker/account sync, auto rebalance를 만들지 않는다.

5. `Workspace > Overview > Sentiment`
   - `시장 심리 갱신`을 누르면 `collect_market_sentiment` job이 CNN Fear & Greed와 AAII Sentiment Survey를 수집해 `finance_meta.macro_series_observation`에 저장한다.
   - 같은 수집은 `Workspace > Ingestion > 시장 심리 수집`에서도 실행할 수 있으며, CNN / AAII source를 개별 checkbox로 켜고 끌 수 있다.
   - React workbench가 available이면 첫 화면에서 service-owned phase / headline / summary, CNN Fear & Greed, AAII Bearish, Bull-Bear Spread, Data Confidence, data freshness, `시장 심리 갱신` / `화면 다시 읽기` action을 함께 확인한다. React build가 없으면 기존 Streamlit controls / overview / detail sections로 fallback한다.
   - `CNN / AAII 같이 보기`는 `analysis_steps`, core metrics, 최근 범위 percentile / min-max, CNN headline / component / AAII divergence를 표시한다. 프론트엔드는 AAII / CNN divergence나 추천 문구를 새로 만들지 않고 `app/services/overview/sentiment.py`가 제공한 해석만 보여준다.
   - `무엇이 이 심리를 만들었나`에서 CNN 7개 구성요소를 탐욕 / 공포 / 중립 driver lane으로 읽고, `CNN 구성요소 상세`에서 각 component가 무엇을 보는지와 현재 읽기를 확인한다. `CNN 구성요소 변화`는 latest vs previous 관측값, 날짜, 변화폭, service-owned change detail을 보여준다.
   - `그래프로 보는 근거`는 stored CNN score / AAII bearish / bull-bear spread history line chart와 CNN component bar chart를 보여준다. History line chart는 y축 눈금과 hover tooltip으로 날짜 / 시리즈 / 값 / source를 확인한다.
   - `원본 / 상세 근거`는 source, observation date, staleness, status, component rows, history rows를 하단 근거 table로 보여준다.
   - 이 화면은 시장 심리 context이며 trade signal, Practical Validation PASS, live approval, order, broker/account sync, auto rebalance로 해석하지 않는다.
   - AAII official page가 automated backend request를 차단하면 job result와 Overview status에 failed / missing state를 남기고 값을 임의 생성하지 않는다.

6. `Workspace > Ingestion > Overview Market Event Calendar > FOMC`
   - 기본은 current year와 next year를 수집한다.
   - 결과는 `finance_meta.market_event_calendar`에 `event_type=FOMC_MEETING`으로 저장된다.
   - Events read model은 legacy row라도 `event_family=central_bank`, `universe_scope=official_macro`, `source_authority=official`로 읽을 수 있게 추론한다.

7. `Workspace > Ingestion > Overview Market Event Calendar > Macro`
   - 기본은 current year와 next year를 수집한다.
   - BLS source는 CPI / PPI / Employment Situation / JOLTS / ECI release schedule을 읽어 official macro row로 저장한다.
   - BEA source는 national GDP와 Personal Income and Outlays / PCE release schedule을 official macro row로 저장한다.
   - Census source는 retail sales, durable goods, housing, construction, trade 관련 economic indicator release row를 저장한다.
   - ISM source는 Manufacturing / Services PMI release row를 저장한다.
   - TreasuryDirect source는 Treasury auction calendar row를 `event_family=fixed_income`, `event_type=TREASURY_AUCTION`으로 저장한다.
   - 결과는 모두 `source_type=official`, `validation_status=official`, `source_authority=official`로 저장된다.
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
   - S&P 500 / Nasdaq-100 / portfolio / watchlist / major-cap earnings coverage는 후속 확장 대상이며, 저장 row는 `universe_scope`로 구분한다.
   - yfinance-only estimate는 `validation_status=estimate_only`, Nasdaq 확인 row는 `validation_status=cross_checked`, Nasdaq에서 확인하지 못한 row는 `validation_status=not_confirmed`가 된다.
   - `source_authority=provider_estimate` 또는 `cross_checked`는 공식 실적 일정 확인이 아니다. 회사 IR / SEC / issuer-confirmed source가 붙은 경우만 official/issuer-confirmed로 올린다.
   - 같은 symbol/source의 이전 active estimate는 새 수집 결과가 있으면 `event_status=superseded`로 정리된다.
   - 수집 결과에는 `symbol_diagnostics`가 포함되며 `no_provider_earnings_date`, `outside_window`, `provider_error` 같은 missing / failure reason을 확인할 수 있다.
   - Ingestion 실행 결과와 Overview refresh 결과의 `Earnings Diagnostics` expander에서 issue count, reason count, symbol-level detail을 확인한다.

9. `Workspace > Overview > Events`
   - React `다가오는 시장 이벤트 브리프` workbench가 available이면 next event, today / this week / next 30D counts, official vs provider-estimate counts, stale estimate count, and context-only boundary를 먼저 확인한다.
   - `화면 / 수집 갱신` command band에서 `화면 새로고침`은 stored DB rows를 다시 읽고, `전체 일정 갱신`은 FOMC / Macro / Market Structure / Earnings collectors를 `app/jobs/overview_actions.py` facade에서 순차 실행한다. 개별 refresh도 같은 Python facade를 통과한다.
   - `실적 예상 일정 갱신`은 최근 S&P 500 movers snapshot 상위 최대 20개 후보를 기준으로 하며 provider 호출은 최대 50개 symbol / 120일 lookahead로 제한한다. 이 일정은 issuer-confirmed source가 붙기 전까지 provider estimate다.
   - React `일정 타입` filter는 `전체`, `FOMC`, `매크로`, `실적`, `시장 구조`를 display-only로 좁힌다. `자료 상태` filter는 `전체`, `확인 필요`, `공식 / 확인됨`, `추정 / 미확정`을 display-only로 좁힌다.
   - Event rails는 row 5개를 한 번에 펼치지 않고 `최근 중요`, `오늘 / 이번 주`, `30일 내`, `나중` 탭으로 읽는다. Badge는 공식 일정 / 제공사 추정 / 교차 확인 / 오래된 추정 / 미확정 같은 source-state를 구분한다.
   - `일정 확정성 / 추정 일정 점검`에서 오래된 추정 일정, 미확정 일정, 추정만 있음, 일정 충돌 sections를 확인한다. 이 섹션의 신뢰는 예측 신뢰가 아니라 source authority / freshness / confirmation 상태다.
   - `캘린더로 보는 일정 근거`는 월간 7열 calendar grid와 weekly density bars를 보여준다. 오늘과 이번 주는 별도 색으로 표시되며, hover tooltip은 날짜별 event count, major title, stale/review count, family mix를 보여준다. 이 정보는 일정 밀도와 자료 상태 근거이며 예측/신호가 아니다.
   - `원본 / 상세 근거`는 collapsed appendix다. 펼치면 Source URL, Source Authority, Collected At 등 service-provided evidence rows를 확인한다.
   - React build가 없으면 기존 Streamlit summary/source lane과 `Agenda`, `Calendar`, `Quality`, `Raw` tabs가 fallback으로 남는다.
   - 하단 Streamlit detail filters인 `Window`, `Source Type`, `Validation`, `Importance`로 캘린더 범위와 source quality를 더 좁힐 수 있다.
   - Overview Events는 UI render 중 직접 외부 source를 scraping하지 않는다. External source fetch는 ingestion job wrapper가 DB에 저장한 뒤 service read model이 읽는다.

10. Data Health ownership
   - `Data Health`는 V22부터 `Workspace > Overview` top-level tab이 아니다.
   - Market Context의 `근거: 자료 기준 / 출처 상태`와 `필요 자료 보강`이 현재 brief에 필요한 direct source / refresh 판단을 보여준다. 이 보강은 S&P 500 movers, sentiment, event calendars만 대상으로 하며 Top1000 / Top2000 / Futures refresh는 Market Movers, Futures Macro, 또는 Ingestion 전용 화면에서 실행한다.
   - 상세 run history, 실패 artifact, log는 `Workspace > Ingestion > 실행 기록 / 결과`에서 확인한다.
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
- Futures Macro lower chart / diagnostics show the latest stored candle window for each selected symbol even when provider freshness is stale; stale latest candles should appear as `Stale`, not as missing chart data.
- Market Movers `Why It Moved > SEC 공시` preserves the compact SEC table as `양식 / 공시일 / 제목 / 열기`. V1.7 / V1.8 selected-filing preview and `공시 Digest` were rolled back after user review, so this lane currently does not fetch, parse, preview, or store filing bodies; users open official SEC documents through the clickable `열기` links.
- `Why It Moved` remains a manual investigation panel. It does not summarize, crawl, collect article bodies, collect filing bodies, run sentiment analysis, auto-classify catalysts, mutate DB schema, or write workflow JSONL / saved setup rows.
- `간단 메타데이터 조회` is button-only and selected-ticker-only. The not-yet-run state is visible before lookup; `OK`, `PARTIAL`, no metadata, and failed lookup states are separate. Metadata URL columns render as clickable `열기` links. SEC filings are displayed as 양식 / 공시일 / 제목 / 열기 and sorted by date with form-priority tie-breaks.
- Compact metadata is session-only. DB-backed metadata persistence is not part of V1.6 and requires a later V2 storage / freshness / retention decision.
- Market Movers / Market Context sector evidence displays breadth, group leadership, trend context, positive group ticker leaders, and raw tables as supporting detail rather than a standalone primary tab.
- Sector/group daily mode uses the stored intraday previous-close snapshot when available; weekly / monthly remain EOD DB based.
- Sector/group status distinguishes `Effective Quote Time` from `Effective EOD Date` and explains sparse raw-date fallback.
- Sector/group evidence shows breadth, cap-vs-equal, concentration, and improving context before raw ranking detail.
- Sector/group trend evidence can use heatmap, line, and latest-delta style views when surfaced inside the current Market Movers / Market Context flows.
- Positive group detail ticker bars use sector colors for positive returns, danger red for negative returns, and high-contrast previous-period return markers.
- Missing diagnostics are visible with recommended action when provider rows are absent or incomplete.
- Coverage Diagnostics keeps `Reason` / `Recommended Action` and adds compact `Likely Cause`, `Evidence Summary`, `Next Check`, `Listing Evidence`, `Profile Freshness`, and `Market Data Issue` evidence. These are DB-backed hints, not legal status, trading signal, validation gate, or monitoring signal.
- Quote gap diagnostics persist repeated issue history to `finance_meta.market_data_issue` and display occurrence count / latest evidence in Coverage Diagnostics.
- Futures Macro requests ten years of daily candles and stores the current 1D/5D/20D score state, 5D/20D independent-episode probabilities, empirical net movement, validation metrics, and bounded calculation trace in one compatible compact snapshot after `일봉 갱신`. The React workbench reads this row without render-time replay; `다시 읽기` is storage-only. Its conclusion and path stay metric-backed, keep current observation status separate from future publication gates, and must not create uncomputed recommendation prose.
- FOMC rows have `source=federal_reserve_fomc_calendar`, `confidence=1.0`, and `Source Type=Official`.
- Macro rows have `Type=MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`, or `MACRO_GDP`, `Source Type=Official`, and `Validation=Official`.
- BLS `.ics` import rows keep `source=bureau_labor_statistics_release_schedule` and `raw_payload_json.import_method=official_ics_file`.
- Earnings rows have `source=yfinance_calendar`, `Source Type=Provider Estimate`, and a validation label.
- Nasdaq cross-checked earnings rows have `Validation=Cross-checked` and higher confidence.
- Earnings rows collected more than 14 days ago show `Freshness=Stale estimate` and a warning.
- Earnings job results show `Earnings Diagnostics` when requested symbols are missing, outside the selected lookahead window, or fail at the provider layer.
- Earnings event rows include `Quality Action`; `Estimate only` rows recommend cross-check or closer refresh, stale rows recommend refresh, and cross-checked rows show no action.
- Overview Events starts with the React workbench when the component build exists: brief, command boundary with last refresh results, local display filters, tabbed event rails, schedule-confirmation review, monthly calendar grid, weekly density, and collapsed raw evidence appendix.
- Overview Events read model includes `Days Until`, `Importance`, taxonomy, quality / validation fields, source status summaries, and workbench payload sections; FOMC / macro / fixed-income rows are high-context official rows, earnings rows remain estimates until confirmed, and rows with source / validation action show `Needs Review`.
- Overview Events calendar/density visuals show schedule clustering and stale/review evidence only. Today and the current week can be highlighted in the month grid, but they do not create validation gates, trade signals, monitoring signals, or automated actions.
- Overview Events keeps existing Streamlit `Agenda`, `Calendar`, `Quality`, `Raw` tabs with Window / Source Type / Validation / Importance filters as fallback and lower evidence sections.
- Overview Events `Latest Collection` / freshness updates after a successful collector run.
- Overview Sentiment starts with the React `시장 심리 컨텍스트` workbench when the component build exists: phase / headline / summary, freshness, CNN Fear & Greed, AAII Bearish, Bull-Bear Spread, Data Confidence, refresh / reload actions, context-only boundary, CNN / AAII cross-read, recent range percentile / min-max, divergence axes, service-owned analysis steps, driver lanes, component explanations, CNN component latest-vs-previous changes, hover-readable history line chart, component bar chart, and stored row evidence.
- Overview Sentiment keeps Python services as owner of DB reads, refresh actions, and interpretation text. React only displays and dispatches the existing refresh / reload events, and the fallback Streamlit detail sections remain available when the React build is missing.
- Overview no longer renders Data Health as a primary tab. Use Market Context source / refresh evidence for current brief issues and `Workspace > Ingestion > 실행 기록 / 결과` for detailed operational diagnostics.
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
