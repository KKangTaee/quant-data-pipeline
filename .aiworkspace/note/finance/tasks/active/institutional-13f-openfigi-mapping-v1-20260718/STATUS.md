# Institutional 13F OpenFIGI Mapping V1 Status

- Status: Complete
- Roadmap: `4/4`

- 2026-07-18: User approved researching a free verified CUSIP-ticker source and proceeding if free.
- 2026-07-18: Official OpenFIGI v3 docs confirmed free anonymous access and a free optional API key with higher limits.
- 2026-07-18: Actual anonymous API probe mapped all 68 distinct Duquesne latest CUSIP/CINS values to one US Equity ticker after filters.
- 2026-07-18: User approved the 1차~4차 design: provider adapter, persistence/source precedence, curated-manager backfill, actual DB/UI QA.
- 2026-07-18: User approved the written spec. Detailed TDD implementation plan now covers resolver, canonical resolution persistence, loader precedence, explicit ingestion action, actual backfill/Browser QA/docs.
- 2026-07-18: Implemented the OpenFIGI v3 resolver, current-state schema, error-preserving UPSERT, and safe loader precedence with RED/GREEN tests.
- 2026-07-18: Added the explicit `13F ticker 연결 보강` action inside the existing SEC 13F Ingestion expander without an API-key input or new diagnostics panel.
- 2026-07-18: Anonymous curated-manager backfill completed in 272.417 seconds: 1,244 written, 1,195 mapped, 49 unmapped, 0 ambiguous, 0 errors, no API key.
- 2026-07-18: Actual public-service coverage improved: Berkshire 19→29/29, Bridgewater 86→985/993, Duquesne 5→70/70; Duquesne mapped weight 6.6579%→99.9999%.
- 2026-07-18: Browser QA confirmed Duquesne 70/70 mapping, representative rows, NTRA saved-price detail, no page/frame horizontal overflow, and no console errors.
- Current: implementation, actual backfill, QA, and durable documentation complete.
- Deferred: all-latest-manager ~31k expansion, 49 current no-match review, historical PIT identity lifecycle, and licensed security-master comparison.
