# Institutional 13F OpenFIGI Mapping V1 Runs

## 2026-07-18 Design Investigation

- Read finance task intake, DB pipeline, brainstorming, systematic debugging, TDD, and planning instructions.
- Read canonical finance docs and completed Institutional Portfolios context/mapping task records.
- Inspected current mapper, schema, loader joins, service guardrails, and React mapping badges.
- Queried actual DB mapping-source counts and Duquesne coverage with read-only SQL.
- Compared exact issuer joins, CUSIP-only unique candidates, ambiguous candidates, and no-candidate rows.
- Verified legacy mapping table contains CUSIP-only collisions/stale candidates that must not be promoted.
- Read official OpenFIGI API/pricing/terms and SEC ticker association documentation.
- Called OpenFIGI v3 anonymously for visible Duquesne examples, then all 68 distinct latest identifiers.
- Confirmed `ID_CUSIP`/`ID_CINS`, US Equity filtering, and one-ticker results for the actual Duquesne sample.

No implementation code or DB writes were performed during design investigation.
