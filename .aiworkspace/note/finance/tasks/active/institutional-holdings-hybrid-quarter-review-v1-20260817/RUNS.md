# Institutional Holdings Hybrid Quarter Review V1 Runs

## 2026-08-17 — Discovery and design

- Read finance documentation index, roadmap, project map, Institutional Portfolios flow and 13F
  dataset runbook.
- Inspected bulk collector, refresh status, DB schema, loader, service, Streamlit command boundary,
  React workbench and focused tests.
- Queried the actual local DB through the service read path:
  - refresh dataset `2026-march-april-may`
  - latest stored report period `2026-03-31`
  - watchlist sample filings dated `2026-05-15`
- Checked SEC official Form 13F dataset page and filing deadline FAQ.
- Checked SEC submissions data for Berkshire, Bridgewater and Duquesne; each exposed a
  `2026-06-30` report filed `2026-08-14`.
- Inspected recent commits and completed Institutional Holdings task records before defining the
  new ownership boundary.

## 2026-08-17 — Implementation planning

- Converted the approved written spec into nine TDD execution tasks covering all five roadmap
  stages.
- Self-reviewed function signatures, payload ownership, no-auto-network boundary, amendment and
  missing-price fail-closed rules, React calculation boundary and actual QA closeout gate.
- Selected inline execution because this session is not authorized to delegate implementation to
  subagents.

## 2026-08-17 — Task 1 local due decision

- RED: `tests/test_institutional_13f_refresh.py` failed with three missing-module failures.
- GREEN: 2026 quarter deadlines, partial/current watchlist action and injected workbench action all
  passed (`4 passed`).
- Regression: `tests/test_institutional_portfolios.py` passed (`58 passed`, three pre-existing
  edgar deprecation warnings and four subtests).

## 2026-08-17 — Task 2 SEC bulk discovery

- RED: listing parser/select imports failed; discovery tests then failed on the missing network
  boundary after correcting the test module import.
- GREEN: standard-library anchor parsing accepted only filename-encoded ZIP windows, selected the
  filing-deadline window and preserved SEC HTTP 429 details (`8 passed`).
- Reused the shared pure deadline function from `finance/data` so the data layer does not import
  the app service. The app service continues to expose the approved public helper.
- The no-auto-network boundary remains covered by the injected local action composition test; no
  page render path imports or calls discovery at this stage.

## 2026-08-17 — Task 3 EDGAR watchlist ingestion

- RED: missing EDGAR module, missing shared persistence helper and missing watchlist collector each
  failed before implementation. A separate identity mutation exposed that a requested manager
  could otherwise accept another CIK's XML.
- GREEN: exact report-period submissions filtering, namespace-insensitive primary/information XML,
  `13F-NT` no-holdings behavior, shared UPSERT counts, per-manager commit/rollback, replay skip and
  requested-CIK validation passed (`13 passed`).
- Regression: the existing Institutional Portfolios suite passed (`58 passed`, existing edgar
  deprecation warnings only).

## 2026-08-17 — Task 4 amendment-aware effective history

- RED: the pure resolver, single-connection history loader and effective-bundle compatibility keys
  each failed before implementation.
- GREEN: restatement replacement, additive extension, additive-without-base rejection, unknown
  amendment last-good preservation, two-quarter DB composition and legacy bundle keys passed
  (`17 passed`).
- Regression: Institutional Portfolios remained `58 passed`; the loader opens one connection per
  history request and performs no external request or write.

## 2026-08-17 — Task 5 hybrid manual refresh

- RED: bulk/fallback/error orchestration, local page action and manual event tests failed on the
  missing job and event boundary.
- GREEN: official bulk wins when published; otherwise curated EDGAR runs once. Partial manager
  counts remain in the JobResult, discovery failure runs neither collector, and the React event
  ignores supplied source URLs (`22 passed`).
- Regression: Institutional Portfolios passed (`58 passed`). Normal page composition calls only
  the local calendar helper and stored manager rows; SEC discovery remains behind the explicit
  event.

## 2026-08-17 — Task 6 historical quarter review

- RED: change/proxy module, two-window composer and DB-backed review loader each failed before
  implementation.
- GREEN: share/principal labels ignore market-value-only movement; put/call and amount type stay
  separate; missing price/identifier weight is excluded rather than zero-filled; READY/LIMITED/
  NOT_AVAILABLE thresholds and first/last boundary closes are deterministic (`7 passed`).
- Both quarter-end and filing-to-filing proxies use prior reported-value weights. Focused combined
  regression passed (`80 passed`, existing edgar deprecation warnings only).

## 2026-08-17 — Task 7 Python v3 contract

- RED: workbench rejected the new `quarter_review` argument and still emitted v2.
- GREEN: v3 carries the Python-owned review unchanged, uses the conditional local refresh action,
  and preview emits invisible `not_ready` plus a two-quarter unavailable explanation.
- The page loads review once after the selected portfolio succeeds; a review-only failure preserves
  the latest portfolio and emits a bounded unavailable model. Institutional tests passed (`58 passed`).

## 2026-08-17 — Task 8 React v3 product flow

- RED: navigation tests failed until `quarter_review` became a first-class destination; legacy
  Python source-contract tests also failed while they still required the v2 schema and editable
  SEC ZIP/User-Agent form.
- GREEN: React state/filter tests passed (`10 passed`), TypeScript typecheck passed, and Vite rebuilt
  the tracked v3 bundle with the conditional `refresh_institutional_13f` action.
- The `분기 리뷰` screen renders both server-owned proxy windows, coverage state, change filters,
  contribution evidence and a responsive holdings-change table without recalculating finance
  results in the browser.
- Focused Python regression passed (`88 passed`, three pre-existing edgar deprecation warnings and
  four subtests).

## 2026-08-17 — Task 9 actual SEC / MySQL / Browser QA

- Automated baseline: Python focused suites, py_compile, React Vitest/typecheck/build and
  `git diff --check` passed before live execution.
- Live SEC: Q2 official bulk candidate was `None` (0.241s). Berkshire accession
  `0001193125-26-352200`, filed 2026-08-14 for 2026-06-30, normalized 89 holding rows from
  `https://www.sec.gov/Archives/edgar/data/1067983/000119312526352200/` in 4.932s.
- Live SEC exposed that submissions `primaryDocument` may include an XSL path while archive
  `index.json` flattens filenames and reports XML types as `text.gif`. Added a failing actual-shape
  regression, then basename/single-remaining-XML selection; focused live parsing passed.
- Actual MySQL: watchlist Q2 ledger contains 12 unique accessions and 1,640 holdings. Berkshire 89,
  Bridgewater 997 and Duquesne 95 holdings resolved to Q2; the same refresh replay kept 12 unique
  accessions. Pershing Square and Icahn Q2 rows are notice-only `13F-NT` with no fabricated holdings.
- Actual loader/review: Berkshire, Bridgewater and Duquesne each load Q2/Q1 effective quarters.
  Berkshire changes are NEW 1 / ADD 7 / KEEP 15 / REDUCE 6 / DROP 1. 최초 raw-close proxy는
  +8.01% / +6.13%였고 final review에서 corporate-action-safe 기준으로 교체했다.
- Notice-only filings initially left the button at 10/12 because local due logic read the holdings
  manager pointer. Added RED tests and a filing-ledger latest-period loader; actual local action is
  now current 12/12 without promoting notice portfolios.
- Browser QA: 1280/760/420 viewports showed v3 `분기 리뷰`, both proxy cards, coverage, filters,
  table and mobile drawer. Host and component scroll widths equaled client widths at 760/420;
  console error/warning count was zero. Final desktop screenshot remains untracked at
  `institutional-holdings-hybrid-quarter-review-v1-qa.png`.

## 2026-08-17 — Independent review fixes and final re-verification

- Independent review reported no Critical findings and identified bulk portfolio promotion,
  non-common/raw-close proxy coverage, startup-time due clock, bulk replay, transition selection,
  raw error text and request pacing gaps.
- Added fail-closed bulk pointer regressions for notice-only, empty holdings and unknown amendment;
  the manager pointer now accepts only a complete base or unambiguous restatement. Hybrid refresh
  checks the recorded source/report period before downloading the same bulk ZIP again.
- Performance now requires `amount_type=SH`, rejects debt/preferred/convertible class tokens and
  uses stored `adj_close`; raw-close-only positions are missing coverage. Actual Berkshire results
  are quarter +8.4177% and public-follow +6.4840%, both READY with 99.9924% coverage.
- The due decision uses the live clock, every SEC request is paced, technical exception text stays
  in details, and all saved adjacent effective-quarter transitions are returned from one combined
  DB price window for local React selection.
- Final focused Python regression: `103 passed`, three dependency deprecation warnings and four
  subtests. React: `10 passed`; TypeScript typecheck and Vite build passed.
- Repository-wide `pytest -q --tb=short` is not green: `2465 passed, 362 failed, 4 warnings,
  158 subtests` in 145.32s. Failures are broad pre-existing Streamlit singleton and unrelated
  Overview/Backtest/Today contract drift; this task's focused suites are green.
- Final Browser QA after restart showed freshness `2026-06-30`, adjusted proxy +8.42%/+6.48%,
  no refresh action in current 12/12 state, zero console errors and 420px host/component overflow 0.
  Final screenshot remains untracked at
  `institutional-holdings-hybrid-quarter-review-v1-qa-final.png`.
- Second review found three remaining boundaries. Manager UPSERT pointer/source metadata is now
  monotonic by report period and filing date, bulk/EDGAR accepts a portfolio only when parsed rows
  exactly equal `tableEntryTotal`, and incomplete EDGAR filings persist as filing-only evidence but
  remain ineligible for submission freshness/replay completion. Due/partial freshness keeps the
  actual reflected period while the action separately carries the target period; React resets a
  historical transition selection when manager/latest payload identity changes.
- Final independent re-review confirmed the full period/date/accession tie-break and rebuilt
  `index-BFkGfQ8h.js`; no Critical/Important findings remain and the change is ready to integrate.
