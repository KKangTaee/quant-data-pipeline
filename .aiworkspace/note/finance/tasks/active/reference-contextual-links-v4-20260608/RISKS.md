# Risks

- Too many help boxes can make dense work screens noisy; keep each helper collapsed and concise.
- URL-only links may not preserve active Backtest sub-stage state. The 4차 scope is entry-point linking, not deep-link routing.
- Direct Streamlit page URLs can emit `_stcore` 404 console noise for the path-prefixed health / host-config endpoints. QA treated this as existing direct-path fallback noise because page content and helper rendered correctly.
