# Data / DB Pipeline Flow

## 목적

이 문서는 finance data collection, DB persistence, loader read path가 어떻게 연결되는지 설명한다.
새 table, collector, UPSERT, loader를 추가할 때 먼저 확인한다.

Layer ownership과 product surface boundary는 [SYSTEM_BOUNDARIES.md](./SYSTEM_BOUNDARIES.md)를 기준으로 한다.

## 현재 큰 흐름

```text
external source
  -> finance/data/*
  -> finance/data/db/schema.py
  -> MySQL tables
  -> finance/loaders/*
  -> finance/* strategy / analysis runtime
  -> app/runtime/*
  -> app/services/*
  -> app/web/* surfaces
```

대표 소비 경로:

| Consumer | Reads Through | Boundary |
|---|---|---|
| Backtest Analysis | `app/runtime/backtest.py`, `finance/loaders/*`, `finance/*` runtime | 후보 source와 result bundle 생성. Final approval / monitoring policy는 소유하지 않는다 |
| Practical Validation / Final Review | `app/services/backtest_*`, `finance/loaders/provider.py`, `finance/loaders/macro.py`, `finance/loaders/sentiment.py` | compact evidence와 gate / selected-route read model 생성. Full provider / macro / holdings row는 DB에 둔다 |
| Workspace > Overview | `app/services/overview/*`, futures / sentiment services | market context / data health only. Trade signal이나 validation PASS / BLOCKER가 아니다 |
| Operations > Portfolio Monitoring | `app/runtime/final_selected_portfolios.py`, `app/services/backtest_practical_validation.py` sentiment overlay | read-only monitoring / explicit scenario update. No broker order, live approval, auto rebalance |

## 주요 데이터 소스

| 소스 | 주로 쓰는 영역 |
|---|---|
| yfinance | price, profile, 일부 fundamentals |
| NYSE listing source | stock / ETF universe |
| EDGAR | detailed financial statements |
| SEC EDGAR submissions / Form 25 | symbol lifecycle delisting evidence |
| local DB | backtest runtime read path |
| local DB bridge | ETF operability snapshot의 1차 bridge / proxy source. `nyse_price_history`, `nyse_asset_profile`에서 계산 |
| ETF provider source map | `nyse_etf` / `nyse_asset_profile`와 issuer 공식 URL 검증을 이용해 ETF별 수집 endpoint / parser mapping을 저장 |
| ETF issuer official pages | ETF operability actual / partial source. 초기 구현은 iShares, SSGA / SPDR, Invesco 일부 ticker |
| ETF issuer holdings downloads / APIs | ETF holdings / exposure source. 초기 구현은 iShares CSV, SSGA XLSX, Invesco holdings / sector API |
| FRED official API / CSV download | Practical Validation market-context source. 초기 구현은 `VIXCLS`, `T10Y3M`, `BAA10Y` |
| Federal Reserve official FOMC calendar HTML | Overview Events FOMC meeting calendar source. `.gov` page를 파싱해 `market_event_calendar`에 저장 |
| BLS official release schedule HTML / `.ics` file | Overview Events macro calendar source. CPI / PPI / Employment Situation release dates를 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT` row로 저장. 네트워크 정책상 자동 요청이 차단되면 사용자가 내려받은 공식 `.ics` 파일을 Ingestion에서 import할 수 있다 |
| BEA official release schedule HTML | Overview Events macro calendar source. national GDP release dates를 `MACRO_GDP` row로 저장 |
| Yahoo / yfinance ticker calendar | Overview Events earnings primary free provider estimate source. bounded symbol set만 조회해 `market_event_calendar`에 `EARNINGS` row로 저장하고, row가 없는 ticker는 job result의 `symbol_diagnostics`에 missing / failure reason을 남긴다 |
| yfinance futures OHLCV | Overview Futures Monitor pilot source. 주요 선물 1m / daily OHLCV를 `futures_ohlcv`에 저장하되 exchange-grade realtime feed로 보지 않는다. 1d / 1m 요청에서 일부 futures symbol이 빈 응답이거나 지나치게 희소한 응답이면 해당 symbol만 2d / 1m으로 한 번 보강 수집하고 run diagnostics에 남긴다. Futures Monitor chart/read model은 현재 UTC가 아니라 각 symbol의 최신 저장 candle을 기준으로 window를 읽고, freshness는 실제 현재 시각 대비 `Stale`로 표시한다. Daily rows also feed Macro Thermometer current scoring and historical validation |
| CNN Fear & Greed official page JSON | Overview Sentiment context source. CNN page referer와 browser-like request를 사용해 overall score / rating / component score를 `macro_series_observation`에 저장한다 |
| AAII Sentiment Survey official historical HTML | Overview Sentiment context source. official historical table의 bullish / neutral / bearish weekly survey row와 bull-bear spread를 `macro_series_observation`에 저장한다 |

## Persistence 계층

| 파일 | 역할 |
|---|---|
| `finance/data/db/schema.py` | DB table definition과 schema migration 성격의 column 보강 |
| `finance/data/db/mysql.py` | MySQL connection / execution helper |
| `finance/data/nyse_db.py` | NYSE CSV를 DB universe table로 적재하고 current listing lifecycle bridge row를 UPSERT |
| `finance/data/sec_delisting.py` | SEC `company_tickers.json`와 submissions API에서 Form 25 / 25-NSE filing metadata를 읽어 `nyse_symbol_lifecycle` delisting_feed row로 UPSERT |
| `finance/data/sec_company_tickers.py` | SEC `company_tickers_exchange.json` current CIK / ticker / exchange association을 `nyse_symbol_lifecycle` listing_observed row로 UPSERT |
| `finance/data/symbol_directory.py` | Nasdaq public Symbol Directory `nasdaqlisted.txt` / `otherlisted.txt` current snapshot을 `nyse_symbol_lifecycle` listing_observed row로 UPSERT |
| `finance/data/computed_lifecycle.py` | 기존 current snapshot lifecycle rows를 읽어 repeated observation window를 `computed_from_snapshots` partial row로 요약 |
| `finance/data/asset_profile.py` | asset profile 수집과 저장 |
| `finance/data/market_intelligence.py` | Overview market intelligence 수집 / 저장 경계. S&P 500 current constituents, Nasdaq-listed Symbol Directory current snapshot read helper, S&P 500 / Top1000 / Top2000 / Nasdaq-listed intraday previous-close snapshot, missing quote gap diagnostics와 반복 issue persistence, FOMC calendar collector, macro release calendar collector, earnings estimate collector, earnings symbol diagnostics, Nasdaq cross-check, earnings lifecycle cleanup, market event UPSERT/read helper를 제공한다. Intraday snapshot은 Market Movers daily와 Sector / Industry daily leadership의 최신 previous-close return read path가 공유한다 |
| `finance/data/futures_market.py` | Overview Futures Monitor 수집 / 저장 경계. yfinance futures provider symbol preset, 1m / daily OHLCV UPSERT, 1d / 1m empty / sparse symbol fallback, 수집 run diagnostics를 `futures_instrument`, `futures_ohlcv`, `futures_market_monitor_run`에 저장한다. `app/services/futures_market_monitoring.py`는 저장된 최신 candle 기준으로 표시 window를 읽고 stale 여부를 별도 계산한다. Macro Thermometer validation is read-only and does not create a new table |
| `finance/data/etf_provider.py` | ETF provider source map discovery와 provider snapshot 수집 / 저장 경계. `nyse_etf` / asset profile 기반으로 공식 endpoint map을 `etf_provider_source_map`에 저장하고, 기존 DB 기반 bridge/proxy row와 issuer official row를 `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot`에 저장한다 |
| `finance/data/macro.py` | FRED macro context series 수집 / 저장 경계. API key가 있으면 FRED API, 없으면 official CSV download를 사용해 `macro_series_observation`에 저장한다 |
| `finance/data/sentiment.py` | CNN Fear & Greed / AAII Sentiment Survey 수집 / 저장 경계. 별도 table을 만들지 않고 `macro_series_observation`에 sentiment series를 idempotent UPSERT한다 |
| `finance/data/data.py` | price 수집 / DB read helper |
| `finance/data/fundamentals.py` | fundamentals와 statement fundamentals shadow 적재 |
| `finance/data/factors.py` | factor 생성과 statement factor shadow 적재 |
| `finance/data/financial_statements.py` | EDGAR detailed statement filing/value/label 적재 |
| `app/jobs/ingestion_jobs.py` / `app/jobs/ingestion/common.py` | Streamlit Ingestion 또는 approved action facade에서 실행되는 수집 job wrapper. `ingestion_jobs.py`는 provider / macro / lifecycle evidence / market intelligence collector 결과를 표준 `JobResult`로 변환하고, `common.py`는 symbol parsing, result normalization, progress event, execution profile, pipeline status helper를 소유한다 |
| `app/jobs/overview_actions.py` | `Workspace > Overview`의 bounded refresh action facade. Overview UI 대신 승인된 market intelligence / futures / events / sentiment / quote-gap diagnostics job 호출과 run-history 기록을 맡는다. Market Context historical analog coverage gap은 같은 facade에서 기존 OHLCV collection job을 managed-safe profile로 호출해 `finance_price.nyse_price_history`를 보강한다 |
| `app/jobs/overview_automation.py` | Overview market intelligence job wrapper를 반복 호출하는 run-once orchestrator. cron / launchd / 외부 runner용 `standard` / `safe` / `events` profile과, Overview 브라우저 세션용 `browser_safe` profile의 cadence, US market-hours guard, lock, run history metadata를 처리한다 |
| `app/services/ingestion_diagnostics.py` | `Workspace > Ingestion`의 read-only diagnostic facade. price window preflight, stale price diagnosis, statement coverage diagnosis, statement PIT inspection을 Streamlit 없이 실행하고 UI가 읽을 payload를 반환한다 |
| `app/web/ingestion_console.py` / `app/web/ingestion/*` | `Workspace > Ingestion`의 provider / evidence / market intelligence snapshot 실행 화면. `ingestion_console.py`는 compatibility facade이고 active implementation은 `app/web/ingestion/page.py`, `registry.py`, `guides.py`, `styles.py`, `results.py`, `dispatcher.py`, `sections.py`로 나뉜다. Korean purpose-first job guide, action registry, common recent-run summary, result next-action guidance, three-section workbench, scheduled read-only diagnostics, running progress / elapsed-time display, execution records section, ETF/provider/macro/lifecycle/event collection cards and diagnostic panel render를 제공한다. Broad yfinance fundamentals / factors는 active UI가 아니라 old replay / explicit comparison compatibility로만 남긴다 |

## Loader 계층

| 파일 | 역할 |
|---|---|
| `finance/loaders/universe.py` | universe, asset profile status, symbol lifecycle coverage summary 조회 |
| `finance/loaders/price.py` | price history, price matrix, freshness, symbol별 latest price, validation window coverage summary 조회 |
| `finance/loaders/provider.py` | provider snapshot read path. ETF operability / holdings / exposure snapshot을 읽는다 |
| `finance/loaders/macro.py` | market-context read path. macro observation range와 기준일 snapshot / staleness를 읽는다 |
| `finance/loaders/sentiment.py` | Overview sentiment read path. `macro_series_observation`에서 CNN / AAII latest snapshot과 history를 읽는다 |
| `finance/loaders/fundamentals.py` | broad fundamentals와 statement shadow fundamentals 조회 |
| `finance/loaders/factors.py` | broad factors와 statement factor snapshot 조회 |
| `finance/loaders/financial_statements.py` | statement filing metadata / values / labels / strict snapshot / timing audit 조회 |
| `finance/loaders/runtime_adapter.py` | runtime에서 쓰는 price strategy dict 생성 |

## 현재 중요한 구분

- broad `nyse_factors` / `nyse_fundamentals` 계층은 research convenience layer로 본다.
- strict annual / quarterly factor strategy는 statement shadow / PIT snapshot 계층을 더 중요하게 본다.
- 가격 기반 ETF 전략은 price loader와 `BacktestEngine` warmup / slice 경로가 중심이다.
- factor / fundamental 전략은 rebalance date 기준 snapshot payload가 핵심 계약이다.
- Practical Validation provider connector는 UI에서 외부 provider를 직접 호출하지 않고,
  `finance/data/*` ingestion이 저장한 snapshot을 `finance/loaders/provider.py`로 읽는다.
  P2-5A부터 `Workspace > Ingestion > Practical Validation 검증 데이터 보강`에서
  해당 ingestion을 수동 실행할 수 있다.
  `Provider Source Map` tab은 `nyse_etf`와 `nyse_asset_profile`을 기준으로 iShares / SSGA / Invesco 공식 endpoint 후보를 검증해
  `etf_provider_source_map`에 저장한다. 이후 snapshot collector는 이 verified source map을 static map보다 먼저 사용한다.
  P2-5B부터 `app/services/backtest_practical_validation_provider_context.py`가 loader 결과를 compact provider context로 바꾸고,
  Practical Validation diagnostics가 이 context를 proxy보다 우선 사용한다.
  `etf_operability_snapshot`은 기존 DB의 price/profile 기반 bridge/proxy snapshot과
  iShares / SSGA / Invesco official page 기반 actual/partial snapshot을 source별로 함께 제공한다.
  `etf_holdings_snapshot`은 official holdings download/API row를 저장하고,
  `etf_exposure_snapshot`은 holdings aggregate와 일부 provider aggregate sector exposure를 저장한다.
  `macro_series_observation`은 FRED market-context observation과 CNN / AAII sentiment observation을 long-form으로 저장하고,
  `finance/loaders/macro.py`가 validation 기준일 근처 FRED snapshot과 staleness를 읽으며 `finance/loaders/sentiment.py`가 Overview Sentiment latest/history를 읽는다.
  `regime-split-validation-v1`부터 Practical Validation은 같은 loader의 historical observation read path를 사용해
  VIX / yield curve / credit spread 월별 regime bucket evidence를 read-only로 계산한다.
  `data-provenance-coverage-v1`부터 Practical Validation provider context는 loader 결과를 source mix / coverage status weight / as-of range / collected range / freshness로 요약하고,
  stale ETF provider snapshot은 `PASS`가 아니라 `REVIEW`로 남긴다.
  `liquidity-capacity-evidence-v1`부터 provider operability context는 min net assets, min average daily dollar volume, max bid-ask spread, max expense, max premium/discount, review symbols 같은 compact capacity metrics도 제공한다.
  Bridge / proxy liquidity evidence는 coverage가 높아도 official actual provider evidence처럼 PASS 처리하지 않고 REVIEW로 남긴다.
  `look-through-exposure-board-v1`부터 같은 provider context가 holdings / exposure snapshot을 compact board로 접어 asset bucket, top holding, overlap, ETF별 coverage를 보여준다.
  이 board도 full holdings row를 JSONL에 저장하지 않고 DB-backed loader 결과에서 만든 summary / top rows만 저장한다.
  `data-coverage-hardening-v1`부터 `finance/loaders/price.py`는 requested validation window의 symbol별 first / latest / row count summary를 제공한다.
  Practical Validation은 이 summary와 asset profile status, provider freshness, runtime replay / period coverage를 `Data Coverage Audit`으로 묶어 보여주며, full OHLCV row나 full listing row를 workflow JSONL에 저장하지 않는다.
  `historical-universe-survivorship-v1`부터 `nyse_symbol_lifecycle`은 current listing snapshot, historical listing, delisting feed, computed snapshot evidence를 저장할 수 있는 lifecycle table이다.
  `finance/loaders/universe.py`는 requested period 기준 compact lifecycle summary를 제공하고, Data Coverage Audit은 requested period를 덮는 historical / delisting evidence가 있을 때만 survivorship control을 PASS로 본다.
  current listing snapshot이나 asset profile row만 있으면 REVIEW로 남긴다.
  `sec-form25-delisting-backfill-v1`부터 `finance/data/sec_delisting.py`는 SEC EDGAR submissions API와 Form 25 / 25-NSE metadata를 official/free delisting source로 사용해
  `source_type=delisting_feed`, `coverage_status=actual`, `listing_status=delisted` lifecycle row를 저장한다.
  Form 25 row는 delisting evidence이며, Form 25 부재를 active proof로 해석하지 않는다.
  `symbol-lifecycle-event-fields-v1`부터 lifecycle row는 `event_type`, `event_date`, `related_symbol`, `related_cik`를 받을 수 있다.
  NYSE current listing row는 `event_type=listing_observed`, SEC Form 25 row는 `event_type=delisting`으로 저장해 future ticker change / merger source와 같은 row contract를 쓴다.
  `symbol-directory-snapshot-ingestion-v1`부터 `finance/data/symbol_directory.py`는 Nasdaq public Symbol Directory current files를 읽어
  `source=nasdaq_symdir_nasdaqlisted` / `nasdaq_symdir_otherlisted`, `source_type=current_listing_snapshot`, `coverage_status=partial`, `event_type=listing_observed` row를 저장한다.
  이 row는 current snapshot evidence이며 historical membership PASS 근거가 아니다.
  `sec-cik-exchange-crosscheck-v1`부터 `finance/data/sec_company_tickers.py`는 SEC `company_tickers_exchange.json` current association을 읽어
  `source=sec_company_tickers_exchange`, `source_type=current_listing_snapshot`, `coverage_status=partial`, `event_type=listing_observed` row를 저장하고 CIK를 `related_cik`에 둔다.
  이 row는 identity cross-check evidence이며 historical membership / delisting / ticker action proof가 아니다.
  `computed-snapshot-lifecycle-v1`부터 `finance/data/computed_lifecycle.py`는 기존 current snapshot rows의 repeated observation window를
  `source=computed_snapshot_lifecycle`, `source_type=computed_from_snapshots`, `coverage_status=partial`, `event_type=historical_membership` row로 요약한다.
  이 row도 absence를 delisting proof로 해석하지 않으며, Data Coverage Audit은 `coverage_status=actual` row만 survivorship PASS 후보로 본다.
  `ingestion-console-ux-data-quality-v1`부터 Streamlit Ingestion UI는 이 lifecycle collector들을 `상장 / 상폐 근거` 탭 아래에 노출한다.
  UI는 current snapshot / identity cross-check / computed partial evidence가 historical membership PASS나 active listing proof가 아니라는 caveat를 함께 보여준다.

## Boundary Summary

- External provider / FRED / crawler calls belong in `finance/data/*` or job wrappers, not normal render paths.
- Loaders read DB state and shape it for runtime / service use; they do not persist new rows.
- `app/services/*` can interpret compact evidence and normalize errors, but should remain Streamlit-free.
- `app/web/*` renders forms, session state, and explicit actions. It should not become a collector, schema owner, or strategy engine.
- Context-only data such as sentiment, futures thermometer, and Why It Moved metadata can inform the user, but it does not become a validation gate or monitoring signal without a separate approved task.

## 데이터 무결성 체크포인트

새 data / DB 변경 시 반드시 확인한다.

- point-in-time 기준이 `period_end`인지 filing/acceptance timing인지
- look-ahead bias 위험이 있는지
- survivorship bias 위험이 커지는지
- UPSERT가 idempotent한지
- provider field 누락이나 ticker별 coverage 차이를 warning으로 남기는지
- schema 변경 시 `docs/PROJECT_MAP.md`, `docs/data/`, 이 문서가 필요한 만큼 갱신됐는지

## 갱신해야 하는 경우

- 새 DB table / column이 추가될 때
- 새 collector나 refresh script가 추가될 때
- loader 함수가 추가되거나 반환 계약이 바뀔 때
- PIT / filing timing / coverage 기준이 바뀔 때
- backtest runtime이 새 loader 계층을 읽기 시작할 때
