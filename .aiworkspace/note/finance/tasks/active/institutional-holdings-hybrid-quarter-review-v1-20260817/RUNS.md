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

Implementation and verification commands will be appended after written-spec approval.
