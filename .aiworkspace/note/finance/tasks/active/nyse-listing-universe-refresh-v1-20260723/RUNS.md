# Runs

## 2026-07-23 Read-only inspection

- `git status --short`, `git log -6 --oneline`
  - unrelated registry/run-history/QA artifacts가 존재하므로 작업 파일만 선별한다.
- finance docs, NYSE collector/writer, symbol source, Ingestion registry/dispatcher/section을 확인했다.
- MySQL current master summary:
  - stock: 6,738 rows, lifecycle last snapshot 2026-05-31
  - ETF: 5,232 rows, lifecycle last snapshot 2026-05-31
- NYSE official current listing API read-only diff:
  - stock: current 6,770, DB missing 158, DB-only 126
  - ETF: current 5,537, DB missing 372, DB-only 67
- 이 inspection 단계에서는 DB write를 수행하지 않았다.

## 2026-07-23 TDD and focused verification

- source/core RED
  - snapshot fetcher와 atomic writer가 없어 expected import/test failure를 확인했다.
- job/dispatch RED
  - refresh action과 job wrapper가 없어 registry/dispatch contract failure를 확인했다.
- UI RED
  - Ingestion 첫 action과 compact result summary가 없어 placement/result contract failure를 확인했다.
- GREEN
  - `tests.test_nyse_listing_universe_refresh`: 10 tests OK
  - `tests.test_nyse_listing_universe_refresh tests.test_ingestion_module_split_contracts`:
    19 tests OK
  - 기존 lifecycle contract: OK
  - 관련 Python module compile 및 `git diff --check`: pass

## 2026-07-23 Actual refresh

- Ingestion job wrapper로 `refresh_nyse_listing_universe`를 실행했다.
- result: success
- before/after:
  - basis `2026-05-31 → 2026-07-23`
  - stock `6,738 → 6,770(+158/-126)`
  - ETF `5,232 → 5,537(+372/-67)`
- `nyse_price_history`: 실행 전후 모두 20,341,708 rows
- closeout read:
  - stock source 6,770, ETF source 5,537, combined unique 12,307
  - 이후 별도 동시 수집으로 price history가 20,341,710 rows가 되었지만,
    listing refresh 실행 전후 비교에서는 20,341,708 rows로 동일했고 이 job에는 price write 경로가 없다.

## 2026-07-23 Browser QA

- desktop:
  - `주식·ETF 종목 목록 최신화`가 `일별 가격 업데이트`보다 먼저 노출됨
  - basis 2026-07-23, stock 6,770, ETF 5,537과 실행 button 확인
- mobile 420x900:
  - horizontal overflow 없음
  - action button visible/enabled
- browser console errors: 0
- screenshot: `nyse-listing-universe-refresh-v1-qa.png` (generated, uncommitted)
