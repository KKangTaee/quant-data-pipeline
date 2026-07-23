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
