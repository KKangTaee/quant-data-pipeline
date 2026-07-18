# Institutional Portfolios Context-First Redesign V1 Risks

## Closed Risks

- React no longer hides rows after 80. Bridgewater actual `993` rows equal explorer `993` rows and render in fixed 50-row pages.
- Count coverage, mapped reported-value weight, and performance coverage are separate v2 fields and UI metrics.
- Previous-quarter absence is an explicit comparison-unavailable state; synthetic fixture covers the available branch and actual DB covers the unavailable branch.

## Open Risks

- V1 still serializes the full holdings payload into the component; 50-row pagination limits rendered DOM size but does not introduce server-side pagination.
- Current `app/services/institutional_portfolios.py`, React TSX, CSS, and focused test file are already large. Implementation should avoid unrelated refactors while keeping new pure helpers isolated.
- Streamlit component iframe interaction automation must keep the target visible; Browser QA confirmed actual event delivery after using visible DOM / pointer coordinates.

## Deferred Dependencies

- Historical SEC 13F quarter backfill for real quarter-over-quarter comparison.
- Verified security master / OpenFIGI / licensed identifier mapping.
- Multi-manager comparison surface.
- Dedicated TradingView-class chart library.
