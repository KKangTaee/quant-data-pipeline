# Institutional Portfolios Context-First Redesign V1 Risks

## Closed Risks

- React no longer hides rows after 80. Bridgewater actual `993` rows equal explorer `993` rows and render in fixed 50-row pages.
- Count coverage, mapped reported-value weight, and performance coverage are separate v2 fields and UI metrics.
- Previous-quarter absence is an explicit comparison-unavailable state; synthetic fixture covers the available branch and actual DB covers the unavailable branch.
- A mapped security found by direct Institutional Interest search no longer depends on the selected manager holding it; selected-manager position absence is explicit and DB price / holder evidence remains available.
- Direct Institutional Interest search promotes an identity only for an exact ticker / CUSIP or one unique `(ticker, CUSIP)` pair. Multiple identities return an explicit ambiguous state without loading price data.
- Manager search 0건 preserves any selected normalized CIK's live portfolio context, including managers outside the curated watchlist, and overview unresolved top holdings open their CUSIP notice in the full holdings explorer.

## Open Risks

- V1 still serializes the full holdings payload into the component; 50-row pagination limits rendered DOM size but does not introduce server-side pagination.
- Current `app/services/institutional_portfolios.py`, React TSX, CSS, and focused test file are already large. Implementation should avoid unrelated refactors while keeping new pure helpers isolated.
- Streamlit component iframe interaction automation must keep the target visible; Browser QA confirmed actual event delivery after using visible DOM / pointer coordinates.

## Deferred Dependencies

- Historical SEC 13F quarter backfill for real quarter-over-quarter comparison.
- Verified security master / OpenFIGI / licensed identifier mapping.
- Multi-manager comparison surface.
- Dedicated TradingView-class chart library.
