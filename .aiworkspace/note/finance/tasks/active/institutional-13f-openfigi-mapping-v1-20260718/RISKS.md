# Institutional 13F OpenFIGI Mapping V1 Risks

## Remaining Risks

- OpenFIGI descriptions are provided without an accuracy guarantee; accepted source must still preserve lineage and ambiguity guards.
- US Equity filters may return no result for valid non-US-only securities; V1 must keep them unresolved rather than broaden automatically.
- ticker reuse/change over time can make ticker alone unstable; composite FIGI must be stored with the result.
- current legacy mapping table still contains unsafe CUSIP-only collisions, but the loader no longer promotes them and actual provider precedence assertions passed.
- OpenFIGI rate limits can change or return 429; implemented pacing uses response headers and bounded retry, while anonymous full-universe expansion remains deferred.
- anonymous full-universe backfill would be slow; V1 initial run stays on current curated managers.
- successful ticker mapping does not guarantee local sector metadata or stored price history.
- 49 curated-scope identifiers remain no-match and must stay issuer/CUSIP-only until a verified source resolves them.

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

## Closed In V1

- provider errors do not erase prior good resolution state.
- legacy exact-name collisions are marked ambiguous and do not multiply holding rows.
- actual curated backfill completed without API key, ambiguity, or transport errors.
- actual UI preserved 70 Duquesne rows, exposed mapped ticker detail, and showed no horizontal overflow or console error.
