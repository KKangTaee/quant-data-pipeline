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
