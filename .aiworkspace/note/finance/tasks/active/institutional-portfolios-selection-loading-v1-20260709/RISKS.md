# Institutional Portfolios Selection Loading V1 Risks

- Streamlit custom component values can persist across reruns; event handling must be idempotent.
- Browser QA through direct route can show a Streamlit route fallback modal; final QA should navigate through the app page route or close the modal before interacting.
- Reverse lookup optimization must preserve delayed 13F caveats and avoid turning holder lookup into a recommendation signal.

## Closed In This Task

- Custom component manager-select events now carry nonce keys and are consumed once, so replayed component values do not trigger repeated reruns.
- Watchlist managers are included in selected-manager resolution, so clicking Berkshire / Pershing / Appaloosa / Baupost no longer falls back to an unrelated first DB row.
- Manager change no longer reloads reverse lookup unless the user explicitly opens a stock drilldown.

## Follow-Up

- The local CUSIP-symbol map can still contain imperfect display mappings because official 13F rows do not provide reliable tickers. This remains a data-quality follow-up, not a selection/loading blocker.
