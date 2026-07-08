# DB Schema Map

Status: Active
Last Verified: 2026-07-08

## 목적

이 문서는 finance 프로젝트에서 현재 사용하는 DB와 주요 table을 빠르게 확인하기 위한 지도다.
실제 schema definition은 `finance/data/db/schema.py`가 기준이다.

## DB 목록

| DB | 역할 |
|---|---|
| `finance_meta` | universe, listing, asset profile 같은 meta data |
| `finance_price` | price history |
| `finance_fundamental` | fundamentals, factors, detailed financial statements |

## Table 목록

### `finance_meta`

| Table | 역할 |
|---|---|
| `nyse_stock` | NYSE stock listing master |
| `nyse_etf` | NYSE ETF listing master |
| `nyse_symbol_lifecycle` | symbol lifecycle / historical universe / delisting evidence. current listing snapshot은 partial `listing_observed` event이고 computed snapshot row도 partial observed-window 요약이며, SEC Form 25 같은 delisting source는 actual `delisting` event지만 complete membership proof는 아니다 |
| `nyse_asset_profile` | stock / ETF profile, universe filter, current ETF operability metadata |
| `equity_universe_snapshot` | Quality / Value strict family용 prebuilt monthly PIT-like equity universe snapshot header. V1은 DB price와 latest-known statement shares 기반 근사 market-cap universe다 |
| `equity_universe_member` | `equity_universe_snapshot`별 included / excluded member, rank, approximate market cap, liquidity / exclusion reason evidence |
| `market_universe_member` | Overview market intelligence용 current universe membership. 초기 구현은 S&P 500 current constituents |
| `market_liquidity_universe_member` | Market Movers Top1000 / Top2000용 current liquidity universe membership. listing source 후보 중 `nyse_price_history` 최신 거래일 row가 있는 종목을 최근 20거래일 평균 거래대금으로 ranking해 저장 |
| `market_symbol_alias` | Market Movers ticker-change repair alias store. Quote-missing old ticker와 replacement ticker 후보 / 적용 상태를 저장해 future intraday quote lookup에서 사용 |
| `market_event_calendar` | Overview Events calendar용 event snapshot. FOMC / macro / earnings 등 공통 event row와 earnings source validation / lifecycle status를 저장 |
| `market_data_issue` | Overview Market Movers quote gap 같은 반복 데이터 이슈를 symbol / universe 단위로 누적 추적 |
| `futures_instrument` | Overview futures용 watchlist preset / display metadata. 1차 source는 yfinance provider symbol이다 |
| `futures_market_monitor_run` | Futures OHLCV 수집 run diagnostics. 최근 run status, failed symbols, latest candle time을 저장 |
| `etf_provider_source_map` | ETF별 issuer 공식 endpoint / parser mapping cache. verified row를 provider snapshot collector가 사용 |
| `etf_operability_snapshot` | ETF 비용 / 규모 / 유동성 / spread / NAV 관련 provider snapshot. DB bridge/proxy row와 일부 issuer official actual/partial row를 source별로 저장 |
| `etf_holdings_snapshot` | ETF 내부 holdings row provider snapshot. official issuer download/API row를 저장 |
| `etf_exposure_snapshot` | ETF holdings 또는 provider aggregate에서 만든 asset class / sector / country / currency exposure summary |
| `macro_series_observation` | FRED macro context plus CNN Fear & Greed / AAII sentiment context series observation. VIX / yield curve / credit spread, CNN score / component score, AAII bullish / neutral / bearish / bull-bear spread를 long-form으로 저장 |

### `finance_price`

| Table | 역할 |
|---|---|
| `nyse_price_history` | stock / ETF 공용 OHLCV, dividend, split price ledger |
| `market_intraday_snapshot` | Overview daily movers용 intraday latest price / previous close snapshot. S&P 500 / Top1000 / Top2000 coverage별 최신 refresh row를 저장 |
| `futures_ohlcv` | Overview futures OHLCV candle ledger. 1m row는 stored-candle chart / diagnostics에, 1d row는 Futures Macro current score와 historical validation에 사용 |

### `finance_fundamental`

| Table | 역할 |
|---|---|
| `nyse_fundamentals` | legacy broad yfinance compatibility fundamentals summary |
| `nyse_fundamentals_statement` | EDGAR statement ledger 기반 canonical fundamentals shadow |
| `nyse_factors` | legacy broad fundamentals + price 기반 compatibility factor table |
| `nyse_factors_statement` | EDGAR statement fundamentals shadow + price 기반 canonical strict annual factor shadow |
| `nyse_financial_statement_filings` | filing-level metadata ledger |
| `nyse_financial_statement_values` | filing / concept / period 단위 long-format raw fact ledger |
| `nyse_financial_statement_labels` | concept summary / UI helper layer |

Phase 8 source migration closeout 기준으로 production financial statement source는 EDGAR raw ledger와 statement shadow tables다. `nyse_fundamentals` / `nyse_factors`는 saved/history replay 또는 explicit broad comparison용 legacy compatibility layer다. Phase 3 기준 quarterly 10-K/FY 혼입 방지는 table drop이나 schema 확장이 아니라 policy layer에서 처리한다. `nyse_fundamentals_statement` write path는 unsafe quarterly flow metrics를 비우고, `nyse_fundamentals_statement` / `nyse_factors_statement` loaders는 quarterly 소비 경로에서 `10-Q` / `10-Q/A` row만 반환한다.

## Schema 관리 기준

- 실제 table definition은 `finance/data/db/schema.py`를 기준으로 한다.
- schema sync는 현재 누락 column을 추가하는 방향에 가깝다.
- 정식 migration system처럼 column rename / delete / index redesign까지 안전하게 관리하는 체계는 아니다.
- 새 column을 추가하면 이 문서와 `TABLE_SEMANTICS.md`에 의미가 필요한지 확인한다.

## Table 성격 구분

| 성격 | 의미 | 대표 table |
|---|---|---|
| master | universe / symbol master | `nyse_stock`, `nyse_etf` |
| lifecycle evidence | symbol lifecycle / delisting / historical membership evidence | `nyse_symbol_lifecycle` |
| profile | 현재 snapshot 성격의 profile metadata | `nyse_asset_profile` |
| derived PIT universe snapshot | DB price와 statement shadow 기반으로 만든 monthly equity universe snapshot | `equity_universe_snapshot`, `equity_universe_member` |
| materialized universe | UI / refresh job이 반복해서 읽는 계산된 current membership snapshot | `market_universe_member`, `market_liquidity_universe_member` |
| alias mapping | provider quote ticker drift를 명시적으로 복구하기 위한 current alias state | `market_symbol_alias` |
| connector metadata | provider endpoint / parser mapping cache | `etf_provider_source_map` |
| provider snapshot | provider / DB bridge에서 온 검증용 snapshot | `etf_operability_snapshot`, `etf_holdings_snapshot`, `macro_series_observation`, `market_intraday_snapshot`, `market_event_calendar`, `futures_ohlcv`, `futures_market_monitor_run` |
| issue tracking | 반복되는 수집 / coverage 이슈를 운영 판단용으로 누적 | `market_data_issue` |
| raw ledger | raw source에 가까운 fact ledger | `nyse_price_history`, `nyse_financial_statement_values` |
| filing ledger | filing 단위 metadata | `nyse_financial_statement_filings` |
| broad summary | provider-normalized legacy compatibility summary | `nyse_fundamentals` |
| derived | 계산된 factor table 또는 holdings aggregate. `nyse_factors`는 legacy compatibility, `etf_exposure_snapshot`은 provider/holdings aggregate | `nyse_factors`, `etf_exposure_snapshot` |
| shadow | statement raw ledger에서 재구성한 canonical 재무제표 / strict annual factor layer | `nyse_fundamentals_statement`, `nyse_factors_statement` |
| convenience | UI / 해석 보조 layer | `nyse_financial_statement_labels` |
