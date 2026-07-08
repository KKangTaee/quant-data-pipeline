# Current Project Audit

## 요약 결론

현재 프로젝트는 이미 두 계층을 가지고 있다.

1. `yfinance` broad fundamentals 계층
   - 수집: `finance/data/fundamentals.py::upsert_fundamentals`
   - 저장: `finance_fundamental.nyse_fundamentals`
   - factor: `finance/data/factors.py::upsert_factors` -> `nyse_factors`
   - loader: `finance/loaders/fundamentals.py::load_fundamental_snapshot`, `finance/loaders/factors.py::load_factor_snapshot`

2. EDGAR statement ledger / shadow 계층
   - raw 수집: `finance/data/financial_statements.py::upsert_financial_statements`
   - 저장: `nyse_financial_statement_filings`, `nyse_financial_statement_values`, `nyse_financial_statement_labels`
   - shadow: `upsert_statement_fundamentals_shadow` -> `nyse_fundamentals_statement`
   - factor shadow: `upsert_statement_factors_shadow` -> `nyse_factors_statement`
   - loader: `load_statement_fundamentals_shadow`, `load_statement_factor_snapshot_shadow`, `load_statement_snapshot_strict`

따라서 문제는 "EDGAR path가 없어서 못 한다"가 아니다. 문제는 broad yfinance와 EDGAR shadow가 기능별로 섞여 있고, 어떤 화면/백테스트가 어느 source를 쓰는지 사용자가 즉시 알기 어렵다는 점이다.

## 설치된 provider/library 상태

- `edgartools 5.15.0`
- `yfinance 1.1.0`
- `sec-edgar-api`는 설치되어 있지 않다.
- `pyproject.toml`은 `edgartools>=5.15.0`, `yfinance>=0.2.65`를 명시한다.

## DB coverage snapshot

2026-06-30 현재 local MySQL 기준 확인값:

| Table | Freq | Rows | Symbols | Min period_end | Max period_end | Max collected |
| --- | --- | ---: | ---: | --- | --- | --- |
| `nyse_fundamentals` | annual | 23,094 | 5,528 | 2021-02-28 | 2025-12-31 | 2026-03-24 |
| `nyse_fundamentals` | quarterly | 31,495 | 5,554 | 2024-05-31 | 2026-02-28 | 2026-03-24 |
| `nyse_fundamentals_statement` | annual | 10,317 | 989 | 2010-12-31 | 2026-02-01 | 2026-03-26 |
| `nyse_fundamentals_statement` | quarterly | 58,318 | 988 | 1997-06-30 | 2026-02-28 | 2026-03-29 |
| `nyse_financial_statement_values` | annual | 2,088,537 | 989 | 1989-12-31 | 2026-04-30 | 2026-03-29 |
| `nyse_financial_statement_values` | quarterly | 7,209,821 | 988 | 1989-12-31 | 2026-04-30 | 2026-03-29 |

Interpretation:

- yfinance broad fundamentals는 symbol coverage가 넓지만 기간이 짧고 provider-normalized layer다.
- EDGAR statement shadow는 current universe 중심 coverage가 작지만 기간이 길고 `available_at`, `accession_no`, `form_type`를 가진다.
- 실전 백테스트 canonical로는 EDGAR shadow가 맞고, broad yfinance는 compatibility / bridge로만 남겨야 한다.

## Broad annual freshness

`nyse_fundamentals` annual latest year distribution:

| Latest year | Symbols |
| ---: | ---: |
| 2025 | 1,561 |
| 2024 | 3,945 |
| 2023 | 22 |

`nyse_fundamentals_statement` annual latest year distribution:

| Latest year | Symbols |
| ---: | ---: |
| 2026 | 51 |
| 2025 | 935 |
| 2024 | 3 |

Interpretation:

- Market Movers detail에서 annual 2024가 노출되는 문제는 source가 broad yfinance table이면 자연스럽게 발생한다.
- EDGAR annual shadow는 Top universe 기준으로 훨씬 더 최신 annual data를 가지고 있다.

## 현재 기능 의존성

### Ingestion

- `app/jobs/ingestion_jobs.py::run_collect_fundamentals`
  - broad yfinance `upsert_fundamentals`를 호출한다.
  - row count 중심 result를 반환하므로 symbol별 coverage failure가 가려질 수 있다.

- `run_weekly_fundamental_refresh`
  - broad fundamentals와 broad factors를 같이 갱신한다.

- `run_extended_statement_refresh`
  - EDGAR raw statement 수집 -> statement fundamentals shadow -> statement factor shadow 순서로 실행한다.

- `run_rebuild_statement_shadow`
  - 이미 저장된 EDGAR raw ledger에서 shadow만 재구성한다.

- `run_strict_annual_shadow_refresh`
  - annual EDGAR refresh와 shadow rebuild를 묶은 helper다.

### Backtest

- Legacy broad strategy:
  - `app/runtime/backtest_strict.py::run_quality_snapshot_backtest_from_db`
  - `finance/sample.py::get_quality_snapshot_from_db`
  - source: `nyse_factors`

- Strict annual strategies:
  - `quality_snapshot_strict_annual`
  - `value_snapshot_strict_annual`
  - `quality_value_snapshot_strict_annual`
  - source: `nyse_factors_statement` 또는 strict statement snapshot path

- Quarterly prototype:
  - `quality_snapshot_strict_quarterly_prototype`
  - source: statement quarterly shadow
  - 현재는 production-grade로 보기 어렵다.

### Overview / Market Movers

- `app/services/overview/why_it_moved.py::build_market_mover_research_snapshot`
  - default `fundamental_loader = load_fundamental_snapshot`
  - 즉 Market Movers detail의 annual / quarterly financial card는 broad yfinance fundamentals를 우선 읽는다.
  - 사용자가 본 VSAT annual 2024 / quarterly 2025-12-31 같은 불일치도 이 source 선택의 결과다.

## 중요한 data-quality 발견

### EDGAR quarterly shadow는 아직 canonical로 승격하면 안 된다

`finance/data/financial_statements.py`는 quarterly 수집에서 `10-Q`, `10-Q/A`뿐 아니라 `10-K`, `10-K/A`도 허용한다.

의도:

- 10-K에 들어오는 year-end quarter / Q4-like coverage를 놓치지 않기 위함.

문제:

- EDGAR 10-K의 FY flow item은 "Q4"가 아니라 "연간 누적값"이다.
- 현재 shadow build는 `(symbol, period_end)` 중심으로 묶기 때문에, full-year 10-K 값이 quarterly row처럼 들어갈 수 있다.
- local DB에서 quarterly shadow `latest_form_type=10-K` rows가 14,538개 / 987 symbols로 확인됐다.

따라서 migration 순서는 다음을 지켜야 한다.

1. Annual EDGAR shadow는 canonical 후보로 승격 가능.
2. Quarterly EDGAR shadow는 10-K/FY 혼입 문제를 먼저 분리해야 함.
3. Q4를 쓰려면 flow item은 `FY - Q1 - Q2 - Q3` synthetic Q4로 만들고, balance sheet instant item은 year-end 10-K 값을 허용하는 별도 규칙이 필요하다.

## yfinance를 바로 삭제하면 깨지는 곳

- broad `quality_snapshot` legacy backtest
- Ingestion Console의 `collect_fundamentals` / weekly broad refresh UX
- Market Movers 선택 종목 조사 financial snapshot
- statement shadow의 `shares_outstanding` fallback 일부
- docs / tests에서 broad yfinance source를 명시한 contract

즉 yfinance financial statements 수집은 canonical에서 제외할 수 있지만, 코드를 즉시 삭제하면 regression 위험이 크다.

## 현재 audit 기준 판정

| 질문 | 판정 |
| --- | --- |
| yfinance financial statements를 없애도 되는가? | 즉시 삭제는 불가. canonical에서는 제외하고 freeze/deprecate 후 단계적으로 제거해야 한다. |
| EDGAR path는 쓸 수 있는가? | annual strict path는 이미 충분히 준비되어 있다. quarterly는 보정 전까지 제한해야 한다. |
| 모든 yfinance 기반 backtest를 마이그레이션 가능한가? | 가능하지만 legacy compatibility 기간이 필요하다. |
| UI 최신 표시 원천은? | annual은 statement shadow 우선, quarterly는 10-Q only 또는 보정 완료 후 사용. |
| 최우선 코드 정리 지점은? | Market Movers detail loader, broad quality_snapshot deprecation, quarterly shadow form/period policy. |
