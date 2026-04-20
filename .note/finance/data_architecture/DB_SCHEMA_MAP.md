# DB Schema Map

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
| `nyse_asset_profile` | stock / ETF profile, universe filter, current ETF operability metadata |

### `finance_price`

| Table | 역할 |
|---|---|
| `nyse_price_history` | stock / ETF 공용 OHLCV, dividend, split price ledger |

### `finance_fundamental`

| Table | 역할 |
|---|---|
| `nyse_fundamentals` | provider-normalized broad fundamentals summary |
| `nyse_fundamentals_statement` | statement ledger 기반 fundamentals shadow |
| `nyse_factors` | broad fundamentals + price 기반 derived factor table |
| `nyse_factors_statement` | statement fundamentals shadow + price 기반 derived factor shadow |
| `nyse_financial_statement_filings` | filing-level metadata ledger |
| `nyse_financial_statement_values` | filing / concept / period 단위 long-format raw fact ledger |
| `nyse_financial_statement_labels` | concept summary / UI helper layer |

## Schema 관리 기준

- 실제 table definition은 `finance/data/db/schema.py`를 기준으로 한다.
- schema sync는 현재 누락 column을 추가하는 방향에 가깝다.
- 정식 migration system처럼 column rename / delete / index redesign까지 안전하게 관리하는 체계는 아니다.
- 새 column을 추가하면 이 문서와 `TABLE_SEMANTICS.md`에 의미가 필요한지 확인한다.

## Table 성격 구분

| 성격 | 의미 | 대표 table |
|---|---|---|
| master | universe / symbol master | `nyse_stock`, `nyse_etf` |
| profile | 현재 snapshot 성격의 profile metadata | `nyse_asset_profile` |
| raw ledger | raw source에 가까운 fact ledger | `nyse_price_history`, `nyse_financial_statement_values` |
| filing ledger | filing 단위 metadata | `nyse_financial_statement_filings` |
| broad summary | provider-normalized convenience summary | `nyse_fundamentals` |
| derived | 계산된 factor table | `nyse_factors` |
| shadow | statement raw ledger에서 재구성한 검증/전략용 layer | `nyse_fundamentals_statement`, `nyse_factors_statement` |
| convenience | UI / 해석 보조 layer | `nyse_financial_statement_labels` |
