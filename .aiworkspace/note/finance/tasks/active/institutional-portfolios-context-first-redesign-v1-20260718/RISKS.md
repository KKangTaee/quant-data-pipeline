# Institutional Portfolios Context-First Redesign V1 Risks

## Open Risks

- Current payload already carries the full 993 logical Bridgewater rows while React hides rows after 80. Pagination reduces DOM cost but not existing serialization cost, so implementation must measure rerun latency and avoid duplicating the row payload.
- Mapping count coverage can be low even when mapped value coverage is high. One percentage cannot represent both states.
- Current local DB has no previous comparable filing for the checked curated managers, so change-board visual QA needs a synthetic previous-quarter fixture unless historical quarters are separately loaded.
- Current `app/services/institutional_portfolios.py`, React TSX, CSS, and focused test file are already large. Implementation should avoid unrelated refactors while keeping new pure helpers isolated.
- Streamlit component iframe scroll preservation has had past Browser automation limitations; QA should verify user-visible flow and use DOM evidence when page capture is incomplete.

## Deferred Dependencies

- Historical SEC 13F quarter backfill for real quarter-over-quarter comparison.
- Verified security master / OpenFIGI / licensed identifier mapping.
- Multi-manager comparison surface.
- Dedicated TradingView-class chart library.
