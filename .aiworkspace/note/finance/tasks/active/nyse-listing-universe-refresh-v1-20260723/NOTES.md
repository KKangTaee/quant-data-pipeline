# Notes

## 2026-07-23 Findings

- `app/jobs/symbol_sources.py`
  - `NYSE Stocks` → `SELECT symbol FROM nyse_stock`
  - `NYSE ETFs` → `SELECT symbol FROM nyse_etf`
  - `NYSE Stocks + ETFs` → 두 table merge
- `finance/loaders/_common.py`도 같은 master를 loader universe source로 사용한다.
- `finance/data/nyse.py`의 `load_nyse_listings`는 NYSE API를 통해 current listing을 읽는다.
- `finance/data/nyse_db.py`의 `load_nyse_csv_to_mysql`은 canonical replace와 lifecycle UPSERT를
  지원하지만 CSV 중간 파일과 종류별 독립 실행에 묶여 있다.
- master의 `created_at`은 UPSERT update 시 바뀌지 않으므로 refresh freshness 기준으로 부적합하다.
- UI의 최근 기준은 `nyse_symbol_lifecycle`의 `last_seen_date` / `collected_at`을 사용한다.

## Decisions

- 사용자는 stock과 ETF를 한 action으로 갱신한다.
- 둘을 모두 fetch/validate한 후 atomic DB write한다.
- stale current-master row는 제거하지만 historical price와 lifecycle evidence는 보존한다.
- universe refresh는 daily price update와 자동 결합하지 않는다.
- 새 diagnostic dashboard는 만들지 않는다.

## Implementation

- `finance/data/nyse.py`
  - stock/ETF current listing snapshot과 source 통계를 반환하는 fetch boundary를 추가했다.
- `finance/data/nyse_db.py`
  - 두 snapshot의 필수 컬럼, 중복, empty, retention ratio를 write 전에 검증한다.
  - 두 current master의 UPSERT/canonical delete와 lifecycle UPSERT를 한 transaction으로 묶었다.
  - 화면에서 사용할 공통 기준일과 stock/ETF 현재 건수를 lifecycle에서 읽는다.
- `app/jobs/ingestion_jobs.py`
  - stock과 ETF를 모두 fetch한 뒤에만 writer를 호출하는 job wrapper를 추가했다.
- `app/web/ingestion/`
  - registry/dispatcher/guide에 action을 등록했다.
  - Data Operations 첫 action에 마지막 기준과 현재 건수를 표시한다.
  - 성공 결과는 raw job table 대신 기준일·현재·추가·제외·다음 행동으로 요약한다.

## Actual Result

- 기준일: `2026-05-31 → 2026-07-23`
- stock: `6,738 → 6,770`, added 158, removed 126
- ETF: `5,232 → 5,537`, added 372, removed 67
- price history: `20,341,708 → 20,341,708`
- source totals before canonical symbol dedupe:
  - stock 6,771 → 6,770
  - ETF 5,604 → 5,537
