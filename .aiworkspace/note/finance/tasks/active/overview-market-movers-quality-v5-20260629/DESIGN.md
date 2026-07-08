# Overview Market Movers Quality V5 Design

## Boundaries

- Service: `app/services/overview/market_movers.py`
- UI glue: `app/web/overview/market_movers_helpers.py`
- Visual component/CSS: `app/web/overview/components/market_movers.py`, `app/web/overview/components/common.py`
- Contract tests: `tests/test_service_contracts.py`

## Read Model Direction

`build_market_movers_coverage_trust_model(snapshot)` summarizes the existing Market Movers snapshot into a context-only trust model:

- `state`: Good / Stale / Partial / Needs Refresh / No Universe / Missing Quotes
- compact metrics: coverage, freshness timestamp, universe, returnable, missing
- grouped missing rows: missing reason group, likely cause, suggested next action, affected count, sample tickers
- suggested action metadata for existing UI refresh surfaces
- raw missing rows remain available but are not the primary UX

## UI Direction

The Market Movers tab renders a compact `자료 신뢰 상태` strip after the command strip and refresh bar. A `Coverage trust detail` expander shows grouped missing diagnostics first. Raw symbol-level diagnostics and quote-gap diagnosis stay in a separate collapsed `Raw diagnostics` expander.

Nasdaq no-universe uses the existing `run_overview_nasdaq_symbol_directory()` action facade and result key. The UI does not add provider fetches or write new data outside the existing action/ingestion boundary.

## Context-Only Boundary

Coverage trust is data-quality context for the current Market Movers view. It is not a recommendation, trade signal, validation PASS/BLOCKER, Final Review decision, or Operations monitoring signal.
