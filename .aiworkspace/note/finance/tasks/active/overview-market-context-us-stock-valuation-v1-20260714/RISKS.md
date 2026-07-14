# Overview Market Context US Stock Valuation V1 Risks

Last Updated: 2026-07-14

## Open Risks

1. **Comparative FY facts can create false Q4 EPS.**
   - Fix the shared resolver before implementing the stock service; add real-like filing fixtures.
2. **Stock splits can distort price/EPS identity.**
   - Separate raw per-share valuation identity from split-neutral historical comparison and test known split symbols.
3. **Negative or near-zero EPS makes P/E undefined or explosive.**
   - Return NOT_APPLICABLE; do not cap an invalid P/E into a valid-looking signal.
4. **Recent IPOs cannot satisfy 60/119-month history.**
   - Explain structural history insufficiency and do not expose a collection button that cannot fix time.
5. **FOMC GDP+PCE is not company earnings growth.**
   - Label it as a macro proxy and keep company excess EPS growth separately visible.
6. **Historical excess growth can be dominated by one-off events.**
   - Use distinct quarterly YoY TTM observations and deterministic Tukey clipping.
7. **Foreign issuers/ADRs can have EPS unit and ADR-ratio mismatch.**
   - Require verified USD/share trading-unit identity or return NOT_APPLICABLE.
8. **Read-time calculation may be slow for 119 months.**
   - Keep the query one-symbol/bounded, measure in actual QA, and add caching only if evidence requires it.
9. **Generalizing the React component could regress S&P.**
   - Preserve S&P service contract and add focused service/Browser regression coverage.
10. **Nasdaq cleanup could become destructive scope creep.**
    - Remove only the user-facing selector/action path in V1; retain raw data and collectors.
11. **Search can include non-operating securities.**
    - Filter lifecycle/search results to active common stocks and test ETF/preferred/warrant exclusion.
12. **Scenario values can be mistaken for target prices.**
    - Use relative-scenario language and keep evidence/limitations adjacent to the chart.

## Deferred Risks

- REIT P/FFO and sector-specific valuation metrics are separate follow-up work.
- Analyst consensus availability/license is outside free·accountless V1.
- Delisted historical-company search remains outside current user workflow.

## Closed In 1차

- Comparative FY false-Q4 regression is covered by an AMZN-like later-filing fixture.
- True non-calendar fiscal-year Q4 derivation is covered by an AAPL-like fixture.
- Split-unit drift is covered by an NVDA-like 10-for-1 monthly P/E fixture with a future-split no-look-ahead assertion.
