# Runs

## 2026-07-25 Diagnosis

- official XLS recent spread dates: 2026-06-04, 06-11, 06-18, 06-25, 07-02, 07-09, 07-16, 07-23
- gaps: `7, 7, 7, 7, 7, 7, 7` days
- canonical DB and React payload: legacy HTML Wednesday + XLS Thursday pairs reproduced

## 2026-07-25 TDD

- baseline: `.venv/bin/python -m unittest tests.test_sentiment_pit -q` → `21 tests OK`
- RED: XLS reconciliation test expected `canonical_window` before UPSERT and failed because current event sequence omitted it
- GREEN: reconciliation / HTML non-authoritative / rollback tests → `3 tests OK`
- focused full suite: `.venv/bin/python -m unittest tests.test_sentiment_pit -q` → `24 tests OK`
- review RED: 중간 주차 누락과 outer source/partial/non-official/workbook provenance 반례 5건에서 기존 helper가 cleanup을 실행해 실패
- review GREEN: success official workbook + four-series alignment + ISO 7일 cadence gate를 추가하고 final PIT suite `26 tests OK`

## 2026-07-25 Actual Cleanup

- before: canonical `2,054주 / 8,216행`, immutable `1,104행`, batch `11건`
- command: `backfill_aaii_sentiment_history(timeout=20, retries=2)`
- result: official workbook `1987-07-24~2026-07-23`, `2,033주 / 8,132행`
- after: immutable `1,104행`, batch `11건` unchanged
- recent canonical / React payload: 2026-06-18, 06-25, 07-02, 07-09, 07-16 only

## 2026-07-25 Browser QA

- route: `http://localhost:8501/overview?overview_tab=sentiment`
- actual UI: AAII coverage `1987-07-24~2026-07-23 · 2033개`
- current evidence: latest `2026-07-23`, previous `2026-07-16`
- AAII Spread tab: `-12.8pp`, weekly chart rendered
- console errors: `0`
- screenshot: `overview-sentiment-aaii-canonical-dedup-qa.png` generated, not staged

## 2026-07-25 Final Verification

- `.venv/bin/python -m unittest tests.test_sentiment_pit -v` → `26 tests OK`
- sentiment service / React static focused contracts → `14 tests OK`
- `py_compile` for sentiment collector/store/loader → exit `0`
- `git diff --check` → exit `0`
- actual DB recheck: canonical `8,132행 / 2,033주`, immutable `1,104행`, AAII batch `11건`
- downstream React `history_rows`: `2026-06-18, 06-25, 07-02, 07-09, 07-16`
- repository-wide `unittest discover`: `1,816 tests`, `272 errors / 12 failures`; failures span Backtest/Overview/Portfolio files not touched by this task, so this task does not claim a green repository-wide suite
