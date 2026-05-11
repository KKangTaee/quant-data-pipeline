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
  -> app/web/runtime/backtest.py or finance/sample.py
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

## ETF operability provider snapshot 흐름

```text
finance_price.nyse_price_history
  -> ADV / dollar volume / market price proxy

finance_meta.nyse_asset_profile
  -> total assets / bid / ask bridge

iShares / SSGA / Invesco official ETF pages
  -> expense ratio / AUM / NAV / premium-discount / spread / volume actual or partial snapshot

finance.data.etf_provider.collect_and_store_etf_operability()
  -> finance_meta.etf_operability_snapshot
  -> finance.loaders.provider.load_etf_operability_snapshot()
  -> Practical Validation provider context
```

의미:

- `coverage_status=bridge` 또는 `proxy`는 실제 provider 검증 완료가 아니라, 기존 DB로 확인 가능한 보조 근거라는 뜻이다.
- `coverage_status=actual` 또는 `partial`인 official row는 issuer page에서 직접 확인한 field를 normalize한 것이다.
- P2-2B 초기 source map은 iShares `AOR/IEF/TLT`, SSGA `SPY/BIL/GLD`, Invesco `QQQ`다.
- QQQ는 현재 공식 QQQ page에서 expense ratio / inception만 확보되어 `partial`로 저장한다.

## ETF holdings / exposure provider snapshot 흐름

```text
iShares official holdings CSV
SSGA / SPDR official daily holdings XLSX
Invesco official holdings / weighted sector API
  -> finance.data.etf_provider.collect_and_store_etf_holdings()
  -> finance_meta.etf_holdings_snapshot
  -> finance.data.etf_provider.aggregate_and_store_etf_exposures()
  -> finance_meta.etf_exposure_snapshot
  -> finance.loaders.provider.load_etf_holdings_snapshot()
  -> finance.loaders.provider.load_etf_exposure_snapshot()
  -> Practical Validation provider context
```

의미:

- `etf_holdings_snapshot`은 ETF 내부 구성 row의 source-of-truth snapshot이다.
- `etf_exposure_snapshot`은 holdings row 또는 provider aggregate에서 만든 derived summary다.
- P2-3 초기 source map은 iShares `AOR/IEF/TLT`, SSGA `SPY/BIL`, Invesco `QQQ`다.
- `GLD`는 row-level holdings source가 bar list PDF 성격이라 synthetic 100% commodity row를 만들지 않고 missing으로 둔다.
- `AOR`은 현재 1차 ETF holdings만 저장하고, iShares Aggregate Underlying 구간은 2차 look-through expansion 후속으로 둔다.

## Macro / sentiment market-context 흐름

```text
FRED API or FRED official CSV download
  -> finance.data.macro.collect_and_store_macro_series()
  -> finance_meta.macro_series_observation
  -> finance.loaders.macro.load_macro_series_observations()
  -> finance.loaders.macro.load_macro_snapshot()
  -> Practical Validation market-context provider context
```

의미:

- P2-4 초기 series는 `VIXCLS`, `T10Y3M`, `BAA10Y`다.
- API key가 있으면 FRED API를 쓰고, 없으면 official `fredgraph.csv` download를 사용한다.
- sentiment는 별도 composite index crawling이 아니라 VIX / credit spread / yield curve 기반 market-context proxy로 시작한다.
- `load_macro_snapshot()`은 기준일 이전 최신 관측값과 `staleness_days`를 함께 반환한다.

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
  -> app/web/runtime/backtest.py
  -> result bundle / metadata / warnings
```

중요 기준:

- table 의미는 이 폴더에서 확인한다.
- loader / runtime code flow는 `code_analysis/DATA_DB_PIPELINE_FLOW.md`와 `code_analysis/BACKTEST_RUNTIME_FLOW.md`에서 확인한다.
