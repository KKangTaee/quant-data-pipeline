# Data Flow Map

## 목적

이 문서는 finance 프로젝트의 주요 데이터가 어디서 와서 어떤 DB table과 loader를 거쳐 strategy runtime과 app surface로 들어가는지 설명한다.
Layer ownership과 storage class 판정은 [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md)를 함께 본다.

## 전체 흐름

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

## Universe 흐름

```text
NYSE 웹페이지
  -> finance.data.nyse.load_nyse_listings()
  -> csv/nyse_stock.csv / csv/nyse_etf.csv
  -> finance.data.nyse_db.load_nyse_csv_to_mysql()
  -> finance_meta.nyse_stock / finance_meta.nyse_etf
  -> finance.data.asset_profile.collect_and_store_asset_profiles()
  -> finance_meta.nyse_asset_profile
  -> finance.loaders.universe.load_universe()
```

의미:

- universe는 listing 수집 후 asset profile로 정제된다.
- `nyse_asset_profile`은 stock / ETF 필터링과 current-operability 판단의 핵심 메타 table이다.
- 완전한 point-in-time universe history는 아직 아니다.

## Symbol lifecycle / delisting evidence 흐름

```text
NYSE listing CSV
  -> finance.data.nyse_db.load_nyse_csv_to_mysql()
  -> finance_meta.nyse_symbol_lifecycle (current_listing_snapshot / listing_observed / partial)

Nasdaq public Symbol Directory
  -> finance.data.symbol_directory.collect_and_store_symbol_directory_snapshots()
  -> finance_meta.nyse_symbol_lifecycle (current_listing_snapshot / listing_observed / partial)

SEC company_tickers_exchange.json
  -> finance.data.sec_company_tickers.collect_and_store_sec_company_ticker_crosscheck()
  -> finance_meta.nyse_symbol_lifecycle (current_listing_snapshot / listing_observed / partial / CIK cross-check)

SEC company_tickers.json
SEC submissions API Form 25 / 25-NSE metadata
  -> finance.data.sec_delisting.collect_and_store_sec_form25_delistings()
  -> finance_meta.nyse_symbol_lifecycle (delisting_feed / delisting / actual)

Existing current snapshot lifecycle rows
  -> finance.data.computed_lifecycle.collect_and_store_computed_snapshot_lifecycle()
  -> finance_meta.nyse_symbol_lifecycle (computed_from_snapshots / historical_membership / partial)
  -> finance.loaders.universe.load_symbol_lifecycle_coverage_summary()
  -> Data Coverage Audit / Validation Efficacy Audit
```

의미:

- current listing snapshot은 현재 NYSE listing 관찰치이며 historical survivorship PASS 근거가 아니다.
- Nasdaq Symbol Directory snapshot도 current listing 관찰치이며 historical survivorship PASS 근거가 아니다.
- SEC CIK / ticker / exchange association도 current identity cross-check이며 historical survivorship PASS 근거가 아니다.
- SEC Form 25 row는 official delisting / withdrawal evidence다.
- computed snapshot lifecycle row는 repeated observation window 요약이며, `coverage_status=partial`이면 historical survivorship PASS 근거가 아니다.
- Form 25가 없다는 사실은 active listing proof가 아니다.
- complete historical universe membership은 여전히 별도 historical listing source가 필요하다.
- Phase 8부터 lifecycle row는 `event_type`, `event_date`, `related_symbol`, `related_cik`를 받을 수 있다.
  이 필드는 future ticker change / merger / historical membership source를 같은 table에 넣기 위한 DB row contract다.

## Price 흐름

```text
yfinance
  -> finance.data.data.get_ohlcv()
  -> direct research path

yfinance
  -> finance.data.data.store_ohlcv_to_mysql()
  -> finance_price.nyse_price_history
  -> finance.loaders.price.load_price_history() / load_price_matrix()
  -> runtime price dict
```

의미:

- price는 direct-fetch 경로와 DB-backed 경로가 함께 존재한다.
- 제품 runtime은 점점 DB-backed path를 더 중요하게 본다.
- ETF 전략에서는 moving average / trailing return warmup과 date alignment가 결과 기간을 줄일 수 있다.

## Overview market intelligence 흐름

```text
Wikipedia S&P 500 constituents
  -> finance.data.market_intelligence.collect_and_store_sp500_universe()
  -> finance_meta.market_universe_member

Nasdaq public Symbol Directory nasdaqlisted.txt current file
  -> finance.data.symbol_directory.collect_and_store_symbol_directory_snapshots()
  -> finance_meta.nyse_symbol_lifecycle (source=nasdaq_symdir_nasdaqlisted)
  -> app.services.overview.market_movers.build_market_movers_snapshot(universe_code=NASDAQ)
  -> Workspace > Overview > Market Movers

yahoo quote batch via yfinance cookie / crumb session
  -> finance.data.market_intelligence.collect_and_store_market_intraday_snapshot()
  -> finance_price.market_intraday_snapshot

yfinance 5m OHLCV fallback
  -> finance.data.market_intelligence.collect_and_store_market_intraday_snapshot()
  -> finance_price.market_intraday_snapshot
  -> app.services.overview.market_movers.build_market_movers_snapshot()
  -> Workspace > Overview > Market Movers

finance_price.market_intraday_snapshot or finance_price.nyse_price_history
  -> app.services.overview.market_movers.build_group_leadership_snapshot()
  -> Workspace > Overview > Sector / Industry

missing quote rows
  -> finance.data.market_intelligence.diagnose_market_quote_gaps()
  -> app.jobs.overview_actions.run_overview_quote_gap_diagnostics()
  -> app.jobs.ingestion_jobs.run_diagnose_market_quote_gaps()
  -> finance_meta.market_data_issue
  -> Workspace > Overview > Market Movers > Coverage Trust / Raw diagnostics
```

의미:

- `market_universe_member`의 S&P 500은 current constituents snapshot이며 historical PIT membership이 아니다.
- Market Movers의 Nasdaq coverage는 `nyse_symbol_lifecycle`의 latest `nasdaq_symdir_nasdaqlisted` current snapshot을 직접 읽는다. 이는 Nasdaq-listed current observation이며 Nasdaq Composite / Nasdaq-100 또는 historical membership proof가 아니다.
- `market_intraday_snapshot`은 daily movers에서 전일 종가 대비 최신 quote / intraday 가격을 빠르게 읽기 위한 coverage별 snapshot이다.
- 기본 refresh path는 Yahoo quote batch이며, S&P 500은 quote path 실패 시 기존 yfinance 5m OHLCV download로 fallback할 수 있다.
- Top1000 / Top2000 / Nasdaq-listed daily movers도 저장된 quote snapshot을 우선 읽는다. Top universe는 `nyse_asset_profile.market_cap` current snapshot 기준이고 Nasdaq-listed universe는 Symbol Directory current snapshot 기준이며, UI refresh에서는 오래 걸리는 yfinance OHLCV fallback을 자동 실행하지 않는다.
- Missing quote diagnostics는 Yahoo single-symbol quote, 5D history, DB EOD price, asset profile, 필요 시 yfinance `fast_info` evidence를 비교해 `provider_quote_gap` 같은 원인 후보를 job result로 표시한다.
- 진단 결과는 `market_data_issue`에 `issue_type=quote_gap`으로 누적 저장한다. 이는 반복 발생 횟수와 최신 evidence를 추적하기 위한 운영 table이며, 상장폐지 / 거래정지 확정 판정은 아니다.
- Sector / Industry daily leadership은 저장된 intraday snapshot이 있으면 `Previous Close -> latest quote` 기준을 사용한다. Weekly / Monthly leadership은 EOD DB의 최신 usable date를 사용하며, 최신 raw row가 sparse하면 prior eligible date로 fallback한다.

## Overview market event calendar 흐름

```text
Federal Reserve official FOMC calendar HTML
  -> finance.data.market_intelligence.collect_and_store_fomc_calendar()
  -> finance_meta.market_event_calendar
  -> app.services.overview.events.build_market_events_snapshot()
  -> Workspace > Overview > Events

Yahoo / yfinance ticker calendar, bounded symbols
  -> finance.data.market_intelligence.collect_and_store_earnings_calendar()
  -> finance.data.market_intelligence.upsert_market_event_rows()
  -> finance_meta.market_event_calendar
  -> Workspace > Overview > Events

BLS / BEA official release schedules or BLS .ics import
  -> finance.data.market_intelligence.collect_and_store_macro_calendar()
  -> finance_meta.market_event_calendar
  -> Workspace > Overview > Events
```

의미:

- `market_event_calendar`는 event collector별 normalized output을 저장하는 공통 table이다.
- 반복 수집은 `event_key` 기준 UPSERT로 같은 event row를 갱신한다.
- FOMC collector는 Fed 공식 `.gov` calendar page를 파싱한다. meeting range의 마지막 날을 `event_date`로 저장하고, 원본 month/date text와 link evidence는 `raw_payload_json`에 남긴다.
- Earnings collector는 yfinance ticker `calendar` field에서 upcoming `Earnings Date`를 읽고 `event_type=EARNINGS`, `source=yfinance_calendar`, `source_type=provider_estimate`로 저장한다.
- 선택적으로 Nasdaq earnings calendar web endpoint로 같은 symbol/date를 cross-check하고, 결과를 `validation_status`와 `raw_payload_json.source_validation`에 남긴다.
- 날짜가 바뀐 같은 symbol/source의 이전 active estimate는 `event_status=superseded`로 남겨 audit trail을 유지한다.
- Earnings 수집 대상은 manual symbol list 또는 최신 S&P 500 movers snapshot 일부로 제한한다. Coverage 1000/2000 전체 earnings scan은 rate-limit 위험 때문에 production화 전까지 기본 path가 아니다.
- Overview Events 탭과 refresh 버튼은 UI에서 직접 외부 페이지를 파싱하지 않고, `app/jobs/overview_actions.py` facade를 거쳐 ingestion job wrapper로 DB에 저장한 뒤 service read model로 읽는다.
- Macro calendar collector는 official BLS / BEA schedules를 사용한다. BLS 자동 요청이 차단되면 사용자가 받은 공식 `.ics` 파일을 import해 같은 table에 저장한다.

## Overview futures monitor 흐름

```text
yfinance futures OHLCV
  -> finance.data.futures_market.collect_and_store_futures_ohlcv()
  -> finance_meta.futures_instrument
  -> finance_price.futures_ohlcv
  -> finance_meta.futures_market_monitor_run
  -> app.services.futures_market_monitoring.build_futures_monitor_snapshot()
  -> app.services.futures_macro_thermometer.build_futures_macro_thermometer_snapshot()
  -> app.services.futures_macro_validation.build_futures_macro_validation_snapshot()
  -> Workspace > Overview > Futures Monitor
  -> Market Context source / refresh evidence
  -> Operations > System / Data Health / Workspace > Ingestion for detailed diagnostics

finance_price.futures_ohlcv daily rows
  -> finance.loaders.futures.load_futures_ohlcv(symbols=["ZN=F", "ZB=F"], interval_code="1d", end=selected_as_of)
  -> app.services.overview_market_context_analog.build_historical_analog_snapshot()
  -> Workspace > Overview > Market Context > Macro 조건 포함 pilot
```

의미:

- 1차 source는 Yahoo/yfinance provider symbol 기반의 pilot feed다.
- 기본 watchlist는 주가지수, 금리, 원자재, FX futures이며 optional micro / crypto futures는 별도 그룹으로 둔다.
- 정상 화면 render는 DB row를 읽고, 수집은 Overview refresh button이 `app/jobs/overview_actions.py` facade를 호출하거나 Ingestion job wrapper가 실행한다.
- yfinance가 `period=1d`, `interval=1m`에서 일부 futures symbol을 빈 응답 또는 지나치게 희소한 응답으로 돌려주면 collector는 해당 symbol만 `period=2d`, `interval=1m`으로 한 번 보강 수집한다. 성공 / 실패, 초기 row 수, 회복 symbol은 `futures_market_monitor_run.diagnostics_json.fallback_retries`에 남긴다.
- `futures_market_monitor_run`과 Overview local run history가 Data Health의 latest success / failed symbols / stale 판단에 사용된다.
- Macro Thermometer historical validation은 `futures_ohlcv` 1d row를 point-in-time으로 재계산하고, target futures가 부족할 때만 `nyse_price_history` ETF proxy를 labeled fallback으로 읽는다.
- Market Context 3차-B의 Macro 조건 포함 pilot은 저장된 `ZN=F` / `ZB=F` daily rows만 읽어 Rate Pressure futures proxy bucket을 계산한다. selected as-of 이후 row와 anchor 이후 futures 움직임은 조건 계산에 쓰지 않는다.

주의:

- 무료 provider source이므로 exchange-grade realtime feed로 설명하지 않는다.
- yfinance continuous futures는 실제 roll / 만기 구조와 다를 수 있다.
- historical validation은 과거 일관성 평가이며 예측 보장이 아니다.
- 매초 provider fetch는 하지 않는다. MVP는 60초 기본 refresh와 제한된 fast mode를 기준으로 한다.
- futures shock state는 시장 컨텍스트이며 투자 추천이나 자동 매매 신호가 아니다.

## ETF operability provider snapshot 흐름

```text
finance_meta.nyse_etf
finance_meta.nyse_asset_profile
issuer official product list / endpoint verification
  -> finance.data.etf_provider.discover_and_store_etf_provider_source_map()
  -> finance_meta.etf_provider_source_map

finance_price.nyse_price_history
  -> ADV / dollar volume / market price proxy

finance_meta.nyse_asset_profile
  -> total assets / bid / ask bridge

iShares / SSGA / Invesco official ETF pages
  -> expense ratio / AUM / NAV / premium-discount / spread / volume actual or partial snapshot

finance.data.etf_provider.collect_and_store_etf_operability()
  -> finance_meta.etf_operability_snapshot
  -> finance.loaders.provider.load_etf_operability_snapshot()
  -> app.services.backtest_practical_validation_provider_context.build_provider_context()
  -> Practical Validation provider context
```

의미:

- `coverage_status=bridge` 또는 `proxy`는 실제 provider 검증 완료가 아니라, 기존 DB로 확인 가능한 보조 근거라는 뜻이다.
- `coverage_status=actual` 또는 `partial`인 official row는 issuer page에서 직접 확인한 field를 normalize한 것이다.
- `etf_provider_source_map` verified row가 있으면 official 수집은 그 mapping을 static map보다 먼저 사용한다.
- source map discovery는 iShares product list, SSGA holdings XLSX endpoint pattern, Invesco endpoint pattern, 금 현물 ETF `commodity_gold` rule을 사용한다.
- QQQ는 현재 공식 QQQ page에서 expense ratio / inception만 확보되어 `partial`로 저장한다.
- P2-5A부터 이 수집은 `Workspace > Ingestion > Practical Validation Provider Snapshots > ETF Operability`에서 실행할 수 있다.
- P2-5B부터 Practical Validation 9번 / 10번 진단은 이 snapshot을 우선 읽는다. 공식 provider row가 부족하고 bridge / proxy만 있으면 `PASS`가 아니라 `REVIEW` 출처로 남긴다.
- `data-provenance-coverage-v1`부터 provider context는 operability snapshot의 source mix, coverage status weight, as-of range, collected range, freshness를 compact provenance로 함께 저장한다. coverage가 충분해도 snapshot이 오래됐으면 diagnostic status는 `REVIEW`로 낮춘다.

## ETF holdings / exposure provider snapshot 흐름

```text
iShares / SSGA / Invesco source map discovery
  -> finance_meta.etf_provider_source_map

iShares official holdings CSV
SSGA / SPDR official daily holdings XLSX
Invesco official holdings / weighted sector API
  -> finance.data.etf_provider.collect_and_store_etf_holdings()
  -> finance_meta.etf_holdings_snapshot
  -> finance.data.etf_provider.aggregate_and_store_etf_exposures()
  -> finance_meta.etf_exposure_snapshot
  -> finance.loaders.provider.load_etf_holdings_snapshot()
  -> finance.loaders.provider.load_etf_exposure_snapshot()
  -> app.services.backtest_practical_validation_provider_context.build_provider_context()
  -> Practical Validation provider context
```

의미:

- `etf_holdings_snapshot`은 ETF 내부 구성 row의 source-of-truth snapshot이다.
- `etf_exposure_snapshot`은 holdings row 또는 provider aggregate에서 만든 derived summary다.
- P2-5C부터 source map discovery가 verified endpoint를 DB에 저장한다. 현재 smoke 기준 `MTUM`, `QUAL`, `SOXX`, `USMV`, `XLE`, `XLU`도 자동 수집 가능한 mapping으로 검증됐다.
- `GLD`, `IAU`는 금 현물 ETF 특성상 row-level stock holdings가 아니라 synthetic `commodity_gold` 100% gold exposure row로 저장한다.
- `AOR`은 현재 1차 ETF holdings만 저장하고, iShares Aggregate Underlying 구간은 2차 look-through expansion 후속으로 둔다.
- P2-5A부터 이 수집과 exposure 재집계는 `Workspace > Ingestion > Practical Validation Provider Snapshots > ETF Holdings / Exposure`에서 실행할 수 있다.
- P2-5B부터 Practical Validation 2번 / 3번 진단은 이 holdings / exposure snapshot을 우선 읽고, JSONL에는 full row가 아니라 compact provider coverage와 top evidence만 저장한다.
- `data-provenance-coverage-v1`부터 holdings / exposure context도 source mix, coverage status weight, freshness, stale symbols를 compact provenance로 제공한다. Full holdings / exposure row는 계속 DB에만 둔다.
- `look-through-exposure-board-v1`부터 provider context는 holdings / exposure snapshot을 compact board로 요약한다. Board에는 asset bucket rows, top holding rows, ETF별 holdings / exposure coverage, exposure detail top rows만 남기며 full holdings row는 저장하지 않는다.

## Macro / sentiment market-context 흐름

```text
FRED API or FRED official CSV download
  -> finance.data.macro.collect_and_store_macro_series()
  -> finance_meta.macro_series_observation
  -> finance.loaders.macro.load_macro_series_observations()
  -> finance.loaders.macro.load_macro_snapshot()
  -> app.services.backtest_practical_validation_provider_context.build_provider_context()
  -> Practical Validation market-context provider context

CNN Fear & Greed JSON / AAII official historical HTML
  -> finance.data.sentiment.collect_and_store_market_sentiment()
  -> finance_meta.macro_series_observation
  -> finance.loaders.sentiment.load_market_sentiment_snapshot()
  -> finance.loaders.sentiment.load_market_sentiment_history()
  -> app.services.overview.sentiment.build_market_sentiment_snapshot()
  -> app.services.backtest_practical_validation.build_market_sentiment_context_overlay()
  -> Workspace > Overview > Sentiment / Data Health
  -> Backtest > Practical Validation / Final Review context overlay
  -> Operations > Portfolio Monitoring context overlay
```

의미:

- P2-4 초기 series는 `VIXCLS`, `T10Y3M`, `BAA10Y`다.
- API key가 있으면 FRED API를 쓰고, 없으면 official `fredgraph.csv` download를 사용한다.
- Overview sentiment는 `CNN_FEAR_GREED`, CNN component score, `AAII_BULLISH`, `AAII_NEUTRAL`, `AAII_BEARISH`, `AAII_BULL_BEAR_SPREAD`를 같은 long-form table에 저장한다.
- AAII official page는 backend default HTTP client가 interstitial을 받을 수 있어 browser-like document request / TLS impersonation path를 사용한다. 실패하면 값을 꾸미지 않고 job result와 Overview status에 failed / missing state를 남긴다.
- `load_macro_snapshot()`은 기준일 이전 최신 관측값과 `staleness_days`를 함께 반환한다.
- `load_market_sentiment_snapshot()`은 Overview Sentiment tab에서 latest CNN / AAII context를 읽고, surface-specific overlay는 Practical Validation / Final Review / Portfolio Monitoring에서도 같은 context를 읽는다. 이 context는 trade signal, PASS / BLOCKER, selected-route gate, monitoring signal, live approval, order, auto rebalance가 아니다.
- P2-5A부터 이 수집은 `Workspace > Ingestion > Practical Validation Provider Snapshots > Macro Context`에서 실행할 수 있다.
- P2-5B부터 Practical Validation 5번 / 6번 진단은 FRED snapshot을 우선 읽고, 없으면 기존 market proxy를 `REVIEW` fallback으로 표시한다.
- `data-provenance-coverage-v1`부터 macro context는 FRED source mode, observation range, collected range, stale series를 compact provenance로 제공한다.
- `regime-split-validation-v1`부터 Practical Validation은 stored FRED history를 read-only로 읽어 `neutral` / `caution` / `risk_off` bucket별 portfolio / benchmark 성과를 compact evidence로 계산한다.
- Market Context 3차-C부터 `app.services.overview_market_context_analog.build_historical_analog_snapshot()`은 stored FRED `T10Y3M` / `VIXCLS` / `BAA10Y`와 CNN / AAII sentiment history를 loader로 읽어 `Macro 조건 포함 pilot`의 `맥락 차원 상태`에 availability / bucket preview / deferred reason을 표시한다. 이 read model은 기준일 이후 row를 쓰지 않고, FRED / events / sentiment를 historical anchor hard filter로 적용하지 않는다.

## Broad fundamentals / factors 흐름

```text
yfinance financial statements (legacy compatibility only)
  -> finance.data.fundamentals.upsert_fundamentals()
  -> finance_fundamental.nyse_fundamentals
  -> finance.data.factors.upsert_factors()
  -> finance_fundamental.nyse_factors
```

의미:

- `nyse_fundamentals`는 provider-normalized broad summary layer다.
- `nyse_factors`는 fundamentals와 price as-of matching으로 만든 derived research layer다.
- 이 경로는 `legacy_broad_yfinance` source contract로 표시한다.
- 이 경로는 편리하지만 canonical financial statement source나 strict filing-time PIT source로 보지 않는다.
- Phase 7 source migration부터 Ingestion UI의 active broad yfinance fundamentals / factors collection cards는 제거했다. action handlers와 tables는 saved/history replay 또는 explicit compatibility comparison을 위해서만 남긴다.
- loader read model은 `financial_source`, `financial_source_mode`, `source_table`, `available_at`, `form_type`, `accession_no` 공통 source contract alias를 노출한다. broad yfinance row는 filing metadata가 없으므로 `available_at`, `form_type`, `accession_no`가 비어 있을 수 있다.

## Statement-driven shadow 흐름

```text
finance_fundamental.nyse_financial_statement_values
  -> finance.data.fundamentals.upsert_statement_fundamentals_shadow()
  -> finance_fundamental.nyse_fundamentals_statement
  -> finance.data.factors.upsert_statement_factors_shadow()
  -> finance_fundamental.nyse_factors_statement
```

의미:

- broad public path와 statement-driven rebuild path를 분리한다.
- strict annual / quarterly factor strategy는 이 shadow path를 더 중요하게 본다.
- raw truth는 여전히 `nyse_financial_statement_values`다.
- 이 경로는 `sec_edgar_statement_shadow` source contract로 표시한다.
- statement shadow loader는 `latest_available_at`, `latest_form_type`, `latest_accession_no`를 공통 alias인 `available_at`, `form_type`, `accession_no`로도 노출한다.
- annual shadow는 canonical 승격 대상이지만, quarterly shadow는 10-K/FY full-year flow-value 혼입 정책이 고정되기 전까지 production source로 승격하지 않는다.
- Phase 3 source migration부터 quarterly shadow write path는 `10-K` / `10-K/A` filing에서 온 flow metrics를 분기값으로 저장하지 않도록 해당 flow column을 비운다. balance sheet instant 항목은 별도 policy로 남을 수 있다.
- Phase 3 source migration부터 quarterly shadow loaders는 `10-Q` / `10-Q/A` row만 소비 경로에 반환한다. 기존 DB에 남아 있는 quarterly `10-K` / `10-K/A` row는 audit 대상일 수 있지만 Market Movers / backtest factor 소비 경로의 usable row가 아니다.
- `nyse_factors_statement` 자체에는 form type column이 없으므로 factor shadow loader는 `nyse_fundamentals_statement`와 `symbol/freq/period_end/accession` 기준으로 join해 `form_type` source contract alias를 회수한 뒤 같은 quarterly gate를 적용한다.

## Detailed financial statements 흐름

```text
EDGAR
  -> finance.data.financial_statements.get_fundamental()
  -> filing / label / value rows
  -> finance.data.financial_statements.upsert_financial_statements()
  -> finance_fundamental.nyse_financial_statement_filings
  -> finance_fundamental.nyse_financial_statement_labels
  -> finance_fundamental.nyse_financial_statement_values
```

의미:

- detailed statement 계층은 filing-level metadata와 raw long-format values를 보존한다.
- `values` table은 향후 PIT-friendly custom factor engine의 원재료다.
- `labels`는 UI / 해석 보조용 convenience layer로 본다.
- Phase 5 source migration부터 `Workspace > Ingestion`의 기본 재무제표 갱신 흐름은 `EDGAR annual 재무제표 갱신` card에서 시작한다. 같은 화면의 broad yfinance fundamentals / factors refresh는 legacy compatibility / explicit comparison path이며 canonical financial statement refresh가 아니다.
- Phase 6 source migration부터 `Workspace > Ingestion > 수동 복구 / 진단`은 DB-backed `Statement Universe Coverage QA`를 제공한다. 이 QA는 `SP500` / `TOP1000` / `TOP2000` / `NASDAQ` universe를 raw statement / shadow / profile rows로 요약하고, live EDGAR source probe는 소수 symbol용 `Statement Coverage Diagnosis`에만 남긴다.

## Runtime read path

```text
MySQL tables
  -> finance/loaders/*
  -> app/runtime/backtest.py
  -> app/services/* read models
  -> app/web/* render surfaces
  -> result bundle / metadata / warnings
```

중요 기준:

- table 의미는 이 폴더에서 확인한다.
- loader / runtime code flow는 `docs/architecture/DATA_DB_PIPELINE_FLOW.md`와 `docs/architecture/BACKTEST_RUNTIME_FLOW.md`에서 확인한다.
- layer ownership과 JSONL / saved / report 저장 경계는 `docs/architecture/SYSTEM_BOUNDARIES.md`와 `docs/data/STORAGE_GOVERNANCE.md`에서 확인한다.
