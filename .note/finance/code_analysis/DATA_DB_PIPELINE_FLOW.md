# Data / DB Pipeline Flow

## 목적

이 문서는 finance data collection, DB persistence, loader read path가 어떻게 연결되는지 설명한다.
새 table, collector, UPSERT, loader를 추가할 때 먼저 확인한다.

## 현재 큰 흐름

```text
external source
  -> finance/data/*
  -> finance/data/db/schema.py
  -> MySQL tables
  -> finance/loaders/*
  -> app/web/runtime/backtest.py or finance/sample.py
  -> strategy runtime
```

## 주요 데이터 소스

| 소스 | 주로 쓰는 영역 |
|---|---|
| yfinance | price, profile, 일부 fundamentals |
| NYSE listing source | stock / ETF universe |
| EDGAR | detailed financial statements |
| local DB | backtest runtime read path |

## Persistence 계층

| 파일 | 역할 |
|---|---|
| `finance/data/db/schema.py` | DB table definition과 schema migration 성격의 column 보강 |
| `finance/data/db/mysql.py` | MySQL connection / execution helper |
| `finance/data/nyse_db.py` | NYSE CSV를 DB universe table로 적재 |
| `finance/data/asset_profile.py` | asset profile 수집과 저장 |
| `finance/data/data.py` | price 수집 / DB read helper |
| `finance/data/fundamentals.py` | fundamentals와 statement fundamentals shadow 적재 |
| `finance/data/factors.py` | factor 생성과 statement factor shadow 적재 |
| `finance/data/financial_statements.py` | EDGAR detailed statement filing/value/label 적재 |

## Loader 계층

| 파일 | 역할 |
|---|---|
| `finance/loaders/universe.py` | universe와 asset profile status 조회 |
| `finance/loaders/price.py` | price history, price matrix, freshness 조회 |
| `finance/loaders/fundamentals.py` | broad fundamentals와 statement shadow fundamentals 조회 |
| `finance/loaders/factors.py` | broad factors와 statement factor snapshot 조회 |
| `finance/loaders/financial_statements.py` | statement values / labels / strict snapshot / timing audit 조회 |
| `finance/loaders/runtime_adapter.py` | runtime에서 쓰는 price strategy dict 생성 |

## 현재 중요한 구분

- broad `nyse_factors` / `nyse_fundamentals` 계층은 research convenience layer로 본다.
- strict annual / quarterly factor strategy는 statement shadow / PIT snapshot 계층을 더 중요하게 본다.
- 가격 기반 ETF 전략은 price loader와 `BacktestEngine` warmup / slice 경로가 중심이다.
- factor / fundamental 전략은 rebalance date 기준 snapshot payload가 핵심 계약이다.

## 데이터 무결성 체크포인트

새 data / DB 변경 시 반드시 확인한다.

- point-in-time 기준이 `period_end`인지 filing/acceptance timing인지
- look-ahead bias 위험이 있는지
- survivorship bias 위험이 커지는지
- UPSERT가 idempotent한지
- provider field 누락이나 ticker별 coverage 차이를 warning으로 남기는지
- schema 변경 시 `FINANCE_COMPREHENSIVE_ANALYSIS.md`와 이 문서가 필요한 만큼 갱신됐는지

## 갱신해야 하는 경우

- 새 DB table / column이 추가될 때
- 새 collector나 refresh script가 추가될 때
- loader 함수가 추가되거나 반환 계약이 바뀔 때
- PIT / filing timing / coverage 기준이 바뀔 때
- backtest runtime이 새 loader 계층을 읽기 시작할 때
