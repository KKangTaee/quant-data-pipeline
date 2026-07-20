# Runs

- Repository docs, active V1 task, sentiment ingestion/loader/service, macro schema, automation registry, Ingestion registry, and focused tests were inspected read-only.
- Production DB coverage and continuity were queried read-only for CNN headline, seven CNN components, and four AAII series.
- Current CNN and AAII provider rows were fetched without storage and compared to canonical DB overlap after normalizing observation dates.
- Overlap comparison result: 332 overlapping rows, zero current value differences; previous revision values remain unrecoverable because canonical rows were updated in place.
- Run-history JSONL was read without modification to measure distinct collection days and missing execution-mode provenance.
- No production DB, registry JSONL, app code, or generated QA artifact was changed during discovery and design.
- The approved design was decomposed into an eight-task RED→GREEN implementation plan covering schema, source transactions, collection, known-at loading, automation, service/payload, React periods, and Browser QA.
- Plan self-review confirmed balanced code fences, no placeholder markers, correct test-class ownership, and a clean `git diff --check`; implementation has not started.
- Added `market_sentiment_collection_batch` and `market_sentiment_observation_snapshot`, source-scoped atomic dual persistence, source-isolated collection, UTC known-at loading, daily automation, and Ingestion registry coverage.
- Live schema sync and first capture succeeded: collection `c1a46319-e525-4663-9fd1-92459ef0849e`, CNN batch `bf7c1be4-314f-4500-a87b-6116275e33c8`, AAII batch `3920ad51-174a-4349-b88a-fadea7725279`, snapshot/canonical rows `340/340`, failed/missing sources `0/0`.
- Live known-at read returned 340 rows. PIT capture coverage begins at CNN `2026-07-20 09:17:44 UTC` and AAII `2026-07-20 09:17:45 UTC`; one chronological capture per source is not a forecast-validation sample.
- Focused Python verification passed: sentiment PIT `12` tests and Overview/automation/ingestion/service `344` tests. React Vite production build, target Python compile, and `git diff --check` also passed.
- Browser QA passed at `http://localhost:49190/`: shared 6M/1Y/전체 periods, full-history CNN start `2025-06-04`, stacked CNN + AAII graphs, AAII response/spread click and keyboard switching, first/latest CNN hover, 420px no-overflow layout, and zero console errors.
- QA screenshot: `overview-sentiment-history-pit-v2-qa.png` (generated artifact, intentionally unstaged).
- Final closeout rerun passed 373 focused Python tests, React production build, target py_compile, finance refinement hygiene, DB as-known read (340 rows), and `git diff --check`.
