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
| Backtest Analysis | `app/runtime/backtest/`, `finance/loaders/*`, `finance/*` runtime | 후보 source와 result bundle 생성. Final approval / monitoring policy는 소유하지 않는다 |
| Practical Validation / Final Review | `app/services/backtest_*`, `finance/loaders/provider.py`, `finance/loaders/macro.py`, `finance/loaders/sentiment.py` | compact evidence와 gate / selected-route read model 생성. Full provider / macro / holdings row는 DB에 둔다 |
| Workspace > Overview | `app/services/overview/*`, futures / sentiment services | market context / data health only. Trade signal이나 validation PASS / BLOCKER가 아니다 |
| Workspace > Institutional Portfolios | `app/services/institutional_portfolios.py`, `finance/loaders/institutional_13f.py` | delayed 13F portfolio research only. 추천 / 매수매도 신호 / monitoring signal이 아니다 |
| Operations > Portfolio Monitoring | `app/runtime/backtest/read_models/final_selected_portfolios.py`, `app/services/backtest_practical_validation.py` sentiment overlay | read-only monitoring / explicit scenario update. No broker order, live approval, auto rebalance |

## 주요 데이터 소스

| 소스 | 주로 쓰는 영역 |
|---|---|
| yfinance | price, profile, 일부 fundamentals |
| NYSE / Nasdaq listing sources | stock / ETF universe, current listing lifecycle evidence, Market Movers Top liquidity universe candidate set |
| EDGAR | detailed financial statements |
| SEC Form 13F official data sets | institutional investment manager holdings filings. Quarterly official ZIP data sets are stored as manager / filing / holding rows and shown with delay / coverage caveats |
| SEC EDGAR submissions / Form 25 | symbol lifecycle delisting evidence |
| local DB | backtest runtime read path |
| local DB bridge | ETF operability snapshot의 1차 bridge / proxy source. `nyse_price_history`, `nyse_asset_profile`에서 계산 |
| ETF provider source map | `nyse_etf` / `nyse_asset_profile`와 issuer 공식 URL 검증을 이용해 ETF별 수집 endpoint / parser mapping을 저장 |
| ETF issuer official pages | ETF operability actual / partial source. 초기 구현은 iShares, SSGA / SPDR, Invesco 일부 ticker |
| ETF issuer holdings downloads / APIs | ETF holdings / exposure source. 초기 구현은 iShares CSV, SSGA XLSX, Invesco holdings / sector API |
| FRED official API / CSV download | Practical Validation market-context source. 초기 구현은 `VIXCLS`, `T10Y3M`, `BAA10Y` |
| FRED/ALFRED `series/vintagedates` + observations API `output_type=1` | Overview 경제 사이클 17-series long-form revision interval source. `FRED_API_KEY`가 필수이며 revised CSV fallback은 금지한다 |
| Federal Reserve official FOMC calendar HTML | Overview Events FOMC meeting calendar source. `.gov` page를 파싱해 `market_event_calendar`에 저장 |
| Robert Shiller `ie_data.xls` | Market Context 월별 SPX 가격·보간 EPS·CAPE source. 공식 Shiller 페이지에서 현재 XLS 링크를 발견하며 EPS 미발표 최신 월도 price-only row로 `sp500_monthly_valuation`에 저장 |
| SEC QQQ N-PORT / N-30B-2 | Market Context Nasdaq-100 QQQ proxy holdings source. CUSIP/ISIN/LEI, filing/accession, annual/quarterly anchor를 `etf_holdings_snapshot`에 저장하며 공식 Nasdaq aggregate로 취급하지 않는다 |
| S&P Index Earnings workbook | Market Context index EPS source. explicit period/status/EPS columns와 release date가 있는 operator-supplied workbook만 import하며 actual/estimate를 위치나 색상으로 추론하지 않음 |
| Federal Reserve SEP accessible HTML | Market Context GDP/PCE projection source. 2025-06 이후 공식 history 중 missing vintage를 backfill하고 FOMC calendar의 최신 material을 매일 확인해 `fomc_sep_projection`에 release별 저장 |
| BLS official release schedule HTML / `.ics` file | Overview Events macro calendar source. CPI / PPI / Employment Situation release dates를 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT` row로 저장. 네트워크 정책상 자동 요청이 차단되면 사용자가 내려받은 공식 `.ics` 파일을 Ingestion에서 import할 수 있다 |
| BEA official release schedule HTML | Overview Events macro calendar source. national GDP release dates를 `MACRO_GDP` row로 저장 |
| Yahoo / yfinance ticker calendar | Overview Events earnings primary free provider estimate source. bounded symbol set만 조회해 `market_event_calendar`에 `EARNINGS` row로 저장하고, row가 없는 ticker는 job result의 `symbol_diagnostics`에 missing / failure reason을 남긴다 |
| yfinance futures OHLCV | Overview futures data source. 주요 선물 1m / daily OHLCV를 `futures_ohlcv`에 저장하되 exchange-grade realtime feed로 보지 않는다. 1d / 1m 요청에서 일부 futures symbol이 빈 응답이거나 지나치게 희소한 응답이면 해당 symbol만 2d / 1m으로 한 번 보강 수집하고 run diagnostics에 남긴다. 1m rows are retained for stored-candle chart / diagnostic context; daily rows are used by `Futures Macro` scoring/validation and Economic Cycle의 `GC=F` / `DX-Y.NYB` 가격 확인. Freshness is based on stored latest candle versus current time, not hidden as missing data |
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
| `finance/data/symbol_resolver.py` | 사용자가 Factor Readiness에서 승인한 ticker-change repair를 `nyse_symbol_lifecycle`에 `resolution_status=active` row로 UPSERT |
| `finance/data/asset_profile.py` | asset profile 수집과 저장 |
| `finance/data/market_intelligence.py` | Overview market intelligence 수집 / 저장 경계. S&P 500 current constituents, Nasdaq-listed Symbol Directory current snapshot read helper, Market Movers Top1000 / Top2000 최근 20거래일 평균 거래대금 universe materialize/read helper, S&P 500 / Top1000 / Top2000 / Nasdaq-listed intraday previous-close snapshot, ticker-change alias candidate / active alias persistence, missing quote gap diagnostics와 반복 issue persistence, full-window 뒤에도 짧은 EOD 이력의 compact issue evidence, FOMC calendar collector, macro release calendar collector, earnings estimate collector, earnings symbol diagnostics, Nasdaq cross-check, earnings lifecycle cleanup, market event UPSERT/read helper를 제공한다. Intraday snapshot은 Market Movers daily와 Market Context / Market Movers sector-group leadership read path가 공유한다 |
| `finance/data/futures_market.py` | Overview futures OHLCV 수집 / 저장 경계. yfinance futures provider symbol preset, 1m / daily OHLCV UPSERT, 1d / 1m empty / sparse symbol fallback, 수집 run diagnostics를 `futures_instrument`, `futures_ohlcv`, `futures_market_monitor_run`에 저장한다. Core preset은 Economic Cycle 달러 가격 확인용 `DX-Y.NYB`를 포함한다. `app/services/futures_market_monitoring.py`는 stored 1m candle chart / diagnostic context를 최신 저장 candle 기준으로 읽고 stale 여부를 별도 계산한다. `Futures Macro`는 stored daily futures rows를 읽어 current scoring과 lazy historical validation을 만들며, validation은 read-only이고 새 materialized table을 만들지 않는다 |
| `finance/loaders/economic_cycle_assets.py` | Economic Cycle 금·달러 가격 확인용 DB-only reader. `futures_ohlcv`에서 `GC=F` / `DX-Y.NYB` daily row를 종목당 최근 80개로 제한해 읽으며 provider 호출이나 저장을 수행하지 않는다 |
| `finance/data/etf_provider.py` | ETF provider source map discovery와 provider snapshot 수집 / 저장 경계. `nyse_etf` / asset profile 기반으로 공식 endpoint map을 `etf_provider_source_map`에 저장하고, 기존 DB 기반 bridge/proxy row와 issuer official row를 `etf_operability_snapshot`, `etf_holdings_snapshot`, `etf_exposure_snapshot`에 저장한다 |
| `finance/data/macro.py` | FRED macro context series 수집 / 저장 경계. API key가 있으면 FRED API, 없으면 official CSV download를 사용해 `macro_series_observation`에 저장한다 |
| `finance/data/economic_cycle_vintages.py` | 경제 사이클 catalog를 FRED/ALFRED vintage mode로 수집·정규화하고 `(series_id, observation_date, realtime_start, source)` key로 `macro_series_vintage_observation`에 UPSERT한다. API key 부재와 missing value를 명시적으로 보존한다 |
| `finance/data/economic_cycle_results.py` | validation artifact와 current/historical replay compact snapshot의 serialize/UPSERT 경계. 계산 가능한 LIMITED 확률과 publication reason을 함께 보존한다 |
| `finance/economic_cycle_features.py` / `economic_cycle_labels.py` / `economic_cycle_model.py` / `economic_cycle_validation.py` / `economic_cycle_pipeline.py` | strict origin input을 월별 factor/real-economy label로 변환하고 h0/h1/h2 direct model, rolling-origin calibration/publication gate, artifact/current/replay materialization을 수행한다. Pipeline의 explicit provisional scoring만 LIMITED artifact를 계산하며 artifact validation status 자체는 바꾸지 않는다 |
| `finance/data/sp500_valuation.py` | S&P 500 valuation source 경계. Shiller workbook discovery/read와 price-only 최신 월, explicit S&P index earnings import, Federal Reserve calendar 기반 latest/missing-history SEP discovery/parse, 3-table schema bootstrap, parameterized UPSERT를 소유한다 |
| `finance/loaders/sp500_valuation.py` | rolling warmup을 포함한 최근 120개월 price/EPS/PER, 최근 4개 actual As-Reported quarter TTM, 최신 Shiller interpolated TTM EPS, latest/all SEP vintage DB read 경계. graph 2 resolver는 official actual을 우선하고 준비되지 않으면 Shiller proxy를 source/quality/basis/fallback evidence와 함께 반환한다 |
| `app/services/overview/sp500_valuation.py` | 완결 Shiller-only 60m official/36m sensitivity log(PER)와 대칭 2σ anchor, 최신 EPS를 유지한 price-only/current EOD 잠정 PER display series, SEP median GDP+PCE current scenario, 다음 달 vintage activation과 calendar-year target을 적용한 12/36/60개월 rolling SPX reconstruction을 계산하는 Streamlit-free read model 경계 |
| `finance/data/nasdaq100_valuation.py` / `finance/loaders/nasdaq100_valuation.py` | SEC QQQ holdings discovery/parser, identity, filing-aware TTM EPS, weight drift, 95% coverage gate, 60개월 부족 EPS/EOD repair plan, holdings/monthly UPSERT와 DB read 경계. shared resolver는 Q/FY 모두 primary filing period만 받아 later comparative duration fact의 quarter/Q4 오귀속을 막는다. blocked month도 evidence로 보존한다 |
| `finance/data/us_stock_valuation.py` / `finance/loaders/us_stock_valuation.py` | filing available-at TTM, split-neutral monthly price/EPS identity, selected-symbol bounded DB read, active common-stock 검색과 exact missing-range preflight 경계. split-year는 raw Q/FY를 월말 share basis로 먼저 정규화한 뒤 FY-derived Q4를 계산하며 future split/filing을 소급하지 않는다 |
| `finance/data/us_stock_turnaround.py` / `finance/loaders/us_stock_turnaround.py` | selected-symbol 최대 7 fiscal year duration/instant fact read, primary-period direct/cumulative discrete quarter, explicit equivalent-concept family의 guarded missing-Q4 fallback, per-metric/TTM provenance, gap-preserving TTM operating/cash series, split-neutral dilution, milestone/risk/valuation pure contract와 exact profile/price/SEC collection preflight 경계. direct/exact Q4가 family fallback보다 우선하고, duration EPS reader는 canonical `USD per share`와 retained compatibility unit을 함께 허용한다. coverage는 profile/price basis, statement period end/available-at, core raw gap을 분리해 노출한다 |
| `app/services/nyse_calendar.py` | 미국 동부시간 regular/early close, 주말, NYSE 휴일을 반영한 마지막 완료 session 공용 계약. 개별주 freshness와 Backtest price refresh가 같은 기준을 사용한다 |
| `app/services/overview/us_stock_valuation.py` / `us_stock_turnaround.py` / `us_stock_freshness.py` / `market_context_valuation.py` | 개별주 60m/36m log(PER), FOMC+기업 초과 EPS 성장 시나리오, quarterly turnaround analysis와 S&P/PER/turnaround failure isolation 경계. unified freshness는 마지막 완료 NYSE price, profile/price 7일 정렬, 실제 statement raw gap을 결합하며 repairable scope가 있을 때만 `refresh_us_stock_data`를 만든다. positive Graph 1 READY PER만 기본 추천하며, 다른 경우 전환 분석을 추천하되 기존 PER status/value를 바꾸지 않는다. 화면 진입과 내부 selector 전환은 read-only다 |
| `app/services/overview/nasdaq100_valuation.py` | QQQ 단위 Nasdaq retained backend read model. current Market Context user-facing selector에는 연결되지 않지만 data/materialization/collector 계약은 보존한다 |
| `finance/data/sentiment.py` | CNN Fear & Greed / AAII Sentiment Survey 수집 / 저장 경계. 별도 table을 만들지 않고 `macro_series_observation`에 sentiment series를 idempotent UPSERT한다 |
| `finance/data/data.py` | price 수집 / DB read helper |
| `finance/data/fundamentals.py` | fundamentals와 statement fundamentals shadow 적재 |
| `finance/data/factors.py` | factor 생성과 statement factor shadow 적재 |
| `finance/data/pit_universe.py` | Quality / Value strict family용 monthly equity universe snapshot build / UPSERT helper. DB price, statement shadow shares evidence, asset profile filter를 읽어 `equity_universe_snapshot` / `equity_universe_member`에 idempotent하게 저장한다 |
| `finance/data/financial_statements.py` | EDGAR detailed statement filing/value/label 적재 |
| `finance/data/institutional_13f.py` | SEC Form 13F official quarterly data set ZIP 파서 / 수집 경계. manager / filing / holding / CUSIP-symbol map row를 `finance_meta.institutional_13f_*`에 idempotent UPSERT한다 |
| `app/jobs/ingestion_jobs.py` / `app/jobs/ingestion/common.py` | Streamlit Ingestion 또는 approved action facade에서 실행되는 수집 job wrapper. `ingestion_jobs.py`는 provider / macro / lifecycle evidence / market intelligence collector 결과를 표준 `JobResult`로 변환하고, 경제 사이클 explicit vintage collection과 DB-only current materialization wrapper를 제공하며 unattended schedule에는 등록하지 않는다. selected-stock unified collector는 profile/완료-session inclusive price를 CIK 없이 실행한 뒤 SEC scope에만 identity equality를 요구한다. `common.py`는 symbol parsing, result normalization, progress event, execution profile, pipeline status helper를 소유한다 |
| `app/services/overview/economic_cycle.py` | `economic_cycle_snapshot`과 최근 최대 60개월 replay history를 JSON-safe compact read model로 변환한다. DB의 더 긴 replay는 보존한다. 유효 확률과 publication status를 조합해 `VERIFIED/PROVISIONAL/UNAVAILABLE`를 만들며 provider fetch, fit, materialization, DB write를 하지 않는다 |
| `app/jobs/overview_actions.py` | `Workspace > Overview`의 bounded refresh action facade. Overview UI 대신 승인된 market intelligence / futures / events / sentiment / quote-gap diagnostics job 호출과 run-history 기록을 맡는다. Market Context 개별주는 명시 `refresh_us_stock_data` action에서 profile/price를 먼저 canonical ingestion으로 보강하고, SEC statement scope가 있을 때만 selected-symbol/CIK identity를 확인한 뒤 재판정한다. partial success는 저장하고 다음 retry scope를 줄이며, missing CIK는 기존 분석을 ERROR로 덮지 않고 SEC collection gap으로만 둔다. Retained Nasdaq valuation repair facade도 보존한다. Market Movers `유니버스 기준 갱신`은 S&P 500 구성 목록, Nasdaq Symbol Directory, 또는 Top1000 / Top2000 liquidity universe materialize action으로 분기한다. 비-Daily EOD full-window 갱신 뒤에도 가격 row가 period threshold보다 짧으면 `limited_price_history` evidence를 저장하며, 다음 preflight는 현재 row 수가 부족한 동안 같은 full-window 수집을 반복 제안하지 않는다. Market Movers ticker-change repair action은 화면의 후보 alias를 `market_symbol_alias.status=active`로 저장하고, 다음 `일중 스냅샷 갱신`이 active alias를 quote lookup에 사용하게 한다. Market Context historical analog coverage gap은 같은 facade에서 기존 OHLCV collection job을 managed-safe profile로 호출해 `finance_price.nyse_price_history`를 보강한다. Market Movers SEC filing tab의 selected-symbol 재무제표 보강도 같은 facade에서 기존 Ingestion EDGAR statement refresh job으로 위임한다 |
| `app/jobs/overview_automation.py` | Overview market intelligence job wrapper를 반복 호출하는 run-once orchestrator. cron / launchd / 외부 runner용 `standard` / `safe` / `events` profile과, Overview 브라우저 세션용 `browser_safe` profile의 cadence, US market-hours guard, lock, run history metadata를 처리한다. S&P와 Nasdaq valuation은 daily-safe, non-market-hours-only spec으로 분리된다 |
| `app/services/ingestion_diagnostics.py` | `Workspace > Ingestion`의 read-only diagnostic facade. price window preflight, stale price diagnosis, statement coverage diagnosis, statement PIT inspection을 Streamlit 없이 실행하고 UI가 읽을 payload를 반환한다 |
| `app/web/ingestion_console.py` / `app/web/ingestion/*` | `Workspace > Ingestion`의 provider / evidence / market intelligence snapshot 실행 화면. `ingestion_console.py`는 compatibility facade이고 active implementation은 `app/web/ingestion/page.py`, `registry.py`, `guides.py`, `styles.py`, `results.py`, `dispatcher.py`, `sections.py`로 나뉜다. Korean purpose-first job guide, action registry, common recent-run summary, result next-action guidance, three-section workbench, scheduled read-only diagnostics, running progress / elapsed-time display, execution records section, ETF/provider/macro/lifecycle/event collection cards and diagnostic panel render를 제공한다. Broad yfinance fundamentals / factors는 active UI가 아니라 old replay / explicit comparison compatibility로만 남긴다 |

## Loader 계층

| 파일 | 역할 |
|---|---|
| `finance/loaders/universe.py` | universe, asset profile status, symbol lifecycle coverage summary, prebuilt PIT monthly equity universe membership 조회 |
| `finance/loaders/symbol_resolver.py` | `nyse_symbol_lifecycle`의 ticker-change evidence와 price freshness를 결합해 symbol identity 후보 / active repair map을 읽는다 |
| `finance/loaders/price.py` | price history, price matrix, freshness, symbol별 latest price, validation window coverage summary 조회 |
| `finance/loaders/provider.py` | provider snapshot read path. ETF operability / holdings / exposure snapshot을 읽는다 |
| `finance/loaders/macro.py` | market-context read path. macro observation range와 기준일 snapshot / staleness를 읽는다 |
| `finance/loaders/economic_cycle.py` | `realtime_start <= as_of_date <= realtime_end`를 적용해 origin별 eligible revision 하나를 선택하고 coverage, approved artifact, compact snapshot/history를 읽는다. provider 호출과 UI import가 없다 |
| `finance/loaders/sentiment.py` | Overview sentiment read path. `macro_series_observation`에서 CNN / AAII latest snapshot과 history를 읽는다 |
| `finance/loaders/fundamentals.py` | broad fundamentals와 statement shadow fundamentals 조회 |
| `finance/loaders/factors.py` | broad factors와 statement factor snapshot 조회 |
| `finance/loaders/financial_statements.py` | statement filing metadata / values / labels / strict snapshot / timing audit 조회 |
| `finance/loaders/institutional_13f.py` | institutional manager search, latest / previous filing, holdings, symbol / CUSIP reverse lookup, and report-period holder-count ranking read path. External fetch나 DB write를 하지 않는다 |
| `finance/loaders/runtime_adapter.py` | runtime에서 쓰는 price strategy dict 생성 |

## 현재 중요한 구분

- broad `nyse_factors` / `nyse_fundamentals` 계층은 research convenience layer로 본다.
- strict annual / quarterly factor strategy는 statement shadow / PIT snapshot 계층을 더 중요하게 본다.
- Quality / Value strict family의 `PIT Monthly Snapshot Universe` 계약은 `equity_universe_snapshot` / `equity_universe_member`를 loader로 읽고, 각 rebalance date를 가장 가까운 이전 월말 snapshot membership에 매핑한다. 이는 현재 Top-N 고정보다 낫지만 official historical index membership은 아니다.
- 가격 기반 ETF 전략은 price loader와 `BacktestEngine` warmup / slice 경로가 중심이다.
- factor / fundamental 전략은 rebalance date 기준 snapshot payload가 핵심 계약이다.
- Institutional 13F는 `period_of_report`와 `filing_date` / SEC acceptance timing을 구분해야 한다. 화면의 신규 / 증가 / 감소 / 전량 매도 후보는 보고된 두 분기 filing 비교이며 실시간 매수 / 매도나 trading intent가 아니다. CUSIP-symbol mapping은 best-effort 보조 mapping으로 남긴다.
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
  `backtest-symbol-resolver-v1`부터 Backtest strict Factor Readiness는 stale/missing price ticker를 `event_type=ticker_change` lifecycle row와 대조해 symbol identity 후보를 보여준다.
  후보 confidence는 same CIK, lifecycle coverage, source reference, resolved ticker price freshness 같은 source evidence factor로 설명하며, LOW confidence 후보는 자동 반영 대상에서 제외한다.
  사용자가 repair action을 승인하면 `finance/data/symbol_resolver.py`가 같은 table에 `resolution_status=active`와 compact evidence payload를 저장하고, price refresh는 source ticker를 유지한 채 collection ticker만 `related_symbol`로 바꾼다.
  Active repair의 `effective_date`는 price refresh plan/details에서 `source_range` / `resolved_range` / `split_status` metadata-only split contract로 노출된다. 이는 future PIT stitching 입력 계약이며 실제 price series 합성이나 official corporate-action ingestion은 별도 후속 범위다.
  `symbol-directory-snapshot-ingestion-v1`부터 `finance/data/symbol_directory.py`는 Nasdaq public Symbol Directory current files를 읽어
  `source=nasdaq_symdir_nasdaqlisted` / `nasdaq_symdir_otherlisted`, `source_type=current_listing_snapshot`, `coverage_status=partial`, `event_type=listing_observed` row를 저장한다.
  이 row는 current snapshot evidence이며 historical membership PASS 근거가 아니다.
  `market-movers-liquidity-universe-v1`부터 Market Movers Top1000 / Top2000은 `nyse_asset_profile.market_cap` snapshot이 아니라
  `market_liquidity_universe_member`에 materialize된 최근 20거래일 평균 거래대금 membership을 읽는다.
  후보 ticker는 current listing source에서 오고, ranking에는 `nyse_price_history` 최신 거래일 EOD row가 필요하다.
  listing source가 비어 있으면 legacy profile fallback으로 UI를 채우지 않고 `유니버스 기준 갱신` 결과에서 listing source 갱신 필요를 드러낸다.
  `market-movers-ticker-change-repair-v1`부터 quote-fast intraday snapshot은 `market_symbol_alias.status=active` alias를 읽어 provider lookup ticker만 바꿀 수 있다.
  후보 탐지는 quote-missing row에 대해서만 candidate로 저장하며, 사용자가 Overview Market Movers에서 `티커 변경 복구 적용`을 누른 뒤 다시 `일중 스냅샷 갱신`해야 missing row가 제거된다.
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
- 경제 사이클은 `collector -> raw vintage DB -> strict as-of loader -> feature/label/model/validation -> approved artifact/snapshot -> Overview service -> React` 순서다. Overview render는 마지막 두 read-only 단계만 사용한다. 금·달러 가격 확인은 별도의 `futures collector -> futures_ohlcv -> economic_cycle_assets loader -> Overview service -> React` DB-only 보조 경로이며 모델 확률이나 publication gate를 바꾸지 않는다.
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
