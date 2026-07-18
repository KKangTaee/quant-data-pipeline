# Institutional 13F OpenFIGI Mapping V1 Risks

## Open Risks

- OpenFIGI descriptions are provided without an accuracy guarantee; accepted source must still preserve lineage and ambiguity guards.
- US Equity filters may return no result for valid non-US-only securities; V1 must keep them unresolved rather than broaden automatically.
- ticker reuse/change over time can make ticker alone unstable; composite FIGI must be stored with the result.
- current legacy mapping table contains unsafe CUSIP-only collisions; loader precedence must be tested before actual backfill.
- OpenFIGI rate limits can change or return 429; pacing must use response headers and bounded retry.
- anonymous full-universe backfill would be slow; V1 initial run stays on current curated managers.
- successful ticker mapping does not guarantee local sector metadata or stored price history.

## Guardrails

- no first-result promotion when multiple identities remain.
- no hardcoded API key.
- no full raw provider-response persistence.
- no destructive cleanup of legacy mapping rows in V1.
- no provider fetch during normal UI render.
- no mapping status is presented as investment advice or current manager intent.

## Deferred

- full 31k latest-manager identifier backfill after curated-manager validation.
- licensed commercial security master comparison if OpenFIGI later proves insufficient.
- historical point-in-time ticker/FIGI lifecycle handling beyond the latest-filing research surface.
