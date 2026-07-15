# Overview Market Context US Stock Valuation V1 Risks

Last Updated: 2026-07-15

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

## Closed In 2차

- Loader window widening is prevented by exact one-symbol price/statement/SEP query assertions.
- Graph 2 refuses fewer than eight positive-to-positive quarterly observations and keeps applicable SEP release dates in evidence.
- Negative EPS, structural short listing, raw data gaps, and unverified ADR units have distinct readiness regression cases.
- The selected-stock service returns JSON-safe stable shapes for READY, COLLECTABLE, NOT_APPLICABLE, ERROR, and NOT_SELECTED.

## Closed In 3차

- Search cannot trigger remote fetches and excludes stored non-common/inactive rows with regression coverage.
- Collection rejects ticker/CIK mismatch before price or SEC runners are called.
- Exact price range, SEC scope, partial-success recheck, narrowed retry, and READY no-op behavior are covered.
- The 119-month loader window no longer incorrectly turns a valid 60-month main valuation into COLLECTABLE.

## Closed In 4차

- Combined-service regression preserves the S&P payload while isolating selected-stock failures.
- UI events cannot run the former Nasdaq repair path and cannot collect a ticker different from the current selected ticker.
- The React branch exposes collection only for COLLECTABLE and keeps explicit relative-value/non-target-price language next to Graph 2.
- Nasdaq data and collector preservation is covered by the retained backend/facade/automation regression tests.

## Closed In 5차 Actual Audit

- A missing current SEC lifecycle snapshot no longer blanks read-only valuation when current listing/profile plus stored raw evidence exist.
- External selected-symbol collection still requires an exact CIK link; the same explicit action obtains selected-symbol SEC identity first and re-plans before provider calls.
- Recent lifecycle refresh dates no longer create false short-listing classifications because stored price history participates in the listing-duration boundary.
- Non-U.S. issuer profiles without verified share-unit evidence are NOT_APPLICABLE instead of COLLECTABLE.

## Remaining After V1

- Some older 3/5-year points remain unavailable even when raw positive-P/E months exceed the rolling warmup because complete historical filing+SEP evidence is not present at every visible month. The UI reports the exact complete-point count and does not synthesize the missing months.
- The repository-wide isolated full run has four unrelated existing contract failures recorded in `RUNS.md`. All Market Context/U.S. stock/S&P/Nasdaq backend scope tests pass.

## Closed In 2026-07-15 Correctness Follow-up

- Comparative quarterly facts can no longer overwrite the primary reported period or change an already derived Q4 when a later filing repeats prior-year figures.
- Split-year FY/Q operands are normalized to one as-of share basis before Q4 derivation; the NVDA-like 10:1 regression proves `FY 2.94 - Q1 0.598 - Q2 0.67 - Q3 0.78 = Q4 0.892`.
- Graph 2's minimum growth-history gate no longer turns an otherwise valid 60-month Graph 1 into whole-screen NOT_APPLICABLE.
- Actual AMD resolver runtime was reduced from about 5.9 seconds to about 2.5 seconds by prefiltering bounded split events; this changes execution cost only, not valuation values.
