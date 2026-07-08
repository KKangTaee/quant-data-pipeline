# Status

Status: Completed
Last Updated: 2026-07-09

## Current

- 1차~2차 implementation unit completed: selected-symbol yfinance analyst metadata, analyst read-model integration, and UI rendering are in place.

## Completed

- Source boundary decision: yfinance structured session metadata first; Nasdaq / WSJ / MarketWatch stay source-attributed cross-check links in this implementation unit.
- Added `fetch_yfinance_analyst_interest_metadata()` with injectable ticker factory for tests.
- Market interest read model now shows `애널리스트 N건` when yfinance action rows are available.
- `애널리스트 관심` now renders recent analyst action rows, target summary, opinion distribution, and public cross-check links.
- `시장 관심 근거 확인` fetches news, Korean news, SEC metadata, and analyst metadata for the selected ticker only.
- Browser QA confirmed AKAM selected-symbol panel renders analyst summary, news list, SEC filing list, 13F caveats, and source disclosure.

## Not Done

- Nasdaq / WSJ / MarketWatch HTML scraping is intentionally not implemented because this task keeps those pages as original cross-check links.
- No DB schema, ingestion, durable cache, paid API key, login, paywall, or broker/trading integration was added.
