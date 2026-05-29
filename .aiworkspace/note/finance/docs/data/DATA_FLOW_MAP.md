# Data Flow Map

## 목적

이 문서는 finance 프로젝트의 주요 데이터가 어디서 와서 어떤 DB table과 loader를 거쳐 strategy runtime으로 들어가는지 설명한다.

## 전체 흐름

```text
external source
  -> finance/data/*
  -> finance/data/db/schema.py
  -> MySQL tables
  -> finance/loaders/*
  -> app/runtime/backtest.py or finance/sample.py
  -> finance/strategy.py
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

yahoo quote batch via yfinance cookie / crumb session
  -> finance.data.market_intelligence.collect_and_store_market_intraday_snapshot()
  -> finance_price.market_intraday_snapshot

yfinance 5m OHLCV fallback
  -> finance.data.market_intelligence.collect_and_store_market_intraday_snapshot()
  -> finance_price.market_intraday_snapshot
  -> app.services.overview_market_intelligence.build_market_movers_snapshot()
  -> Workspace > Overview > Market Movers

missing quote rows
  -> finance.data.market_intelligence.diagnose_market_quote_gaps()
  -> app.jobs.ingestion_jobs.run_diagnose_market_quote_gaps()
  -> Workspace > Overview > Market Movers > Coverage Diagnostics
```

의미:

- `market_universe_member`의 S&P 500은 current constituents snapshot이며 historical PIT membership이 아니다.
- `market_intraday_snapshot`은 daily movers에서 전일 종가 대비 최신 quote / intraday 가격을 빠르게 읽기 위한 coverage별 snapshot이다.
- 기본 refresh path는 Yahoo quote batch이며, S&P 500은 quote path 실패 시 기존 yfinance 5m OHLCV download로 fallback할 수 있다.
- Top1000 / Top2000 daily movers도 저장된 quote snapshot을 우선 읽는다. 해당 universe는 `nyse_asset_profile.market_cap` current snapshot 기준이며, UI refresh에서는 오래 걸리는 yfinance OHLCV fallback을 자동 실행하지 않는다.
- Missing quote diagnostics는 별도 fact table을 만들지 않는 1차 운영 진단이다. Yahoo single-symbol quote, 5D history, DB EOD price, asset profile, 필요 시 yfinance `fast_info` evidence를 비교해 `provider_quote_gap` 같은 원인 후보를 job result로 표시한다.

## Overview market event calendar 흐름

```text
Federal Reserve official FOMC calendar HTML
  -> finance.data.market_intelligence.collect_and_store_fomc_calendar()
  -> finance_meta.market_event_calendar
  -> app.services.overview_market_intelligence.build_market_events_snapshot()
  -> Workspace > Overview > Events

Yahoo / yfinance ticker calendar, bounded symbols
  -> finance.data.market_intelligence.collect_and_store_earnings_calendar()
  -> finance.data.market_intelligence.upsert_market_event_rows()
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
- Overview Events 탭과 refresh 버튼은 UI에서 직접 외부 페이지를 파싱하지 않고, ingestion job wrapper를 통해 DB에 저장한 뒤 service read model로 읽는다.

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

## Macro / sentiment market-context 흐름

```text
FRED API or FRED official CSV download
  -> finance.data.macro.collect_and_store_macro_series()
  -> finance_meta.macro_series_observation
  -> finance.loaders.macro.load_macro_series_observations()
  -> finance.loaders.macro.load_macro_snapshot()
  -> app.services.backtest_practical_validation_provider_context.build_provider_context()
  -> Practical Validation market-context provider context
```

의미:

- P2-4 초기 series는 `VIXCLS`, `T10Y3M`, `BAA10Y`다.
- API key가 있으면 FRED API를 쓰고, 없으면 official `fredgraph.csv` download를 사용한다.
- sentiment는 별도 composite index crawling이 아니라 VIX / credit spread / yield curve 기반 market-context proxy로 시작한다.
- `load_macro_snapshot()`은 기준일 이전 최신 관측값과 `staleness_days`를 함께 반환한다.
- P2-5A부터 이 수집은 `Workspace > Ingestion > Practical Validation Provider Snapshots > Macro Context`에서 실행할 수 있다.
- P2-5B부터 Practical Validation 5번 / 6번 진단은 FRED snapshot을 우선 읽고, 없으면 기존 market proxy를 `REVIEW` fallback으로 표시한다.

## Broad fundamentals / factors 흐름

```text
yfinance statements
  -> finance.data.fundamentals.upsert_fundamentals()
  -> finance_fundamental.nyse_fundamentals
  -> finance.data.factors.upsert_factors()
  -> finance_fundamental.nyse_factors
```

의미:

- `nyse_fundamentals`는 provider-normalized broad summary layer다.
- `nyse_factors`는 fundamentals와 price as-of matching으로 만든 derived research layer다.
- 이 경로는 편리하지만 strict filing-time PIT source로 보지는 않는다.

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

## Runtime read path

```text
MySQL tables
  -> finance/loaders/*
  -> app/runtime/backtest.py
  -> result bundle / metadata / warnings
```

중요 기준:

- table 의미는 이 폴더에서 확인한다.
- loader / runtime code flow는 `docs/architecture/DATA_DB_PIPELINE_FLOW.md`와 `docs/architecture/BACKTEST_RUNTIME_FLOW.md`에서 확인한다.
