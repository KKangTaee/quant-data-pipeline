# Risks

- Provider quote timeout can turn a normally short snapshot into a multi-minute run.
- Daily intraday return and previous daily return use different end points, so UI text must avoid implying perfect apples-to-apples comparison.
- Raw volume favors high-share-count / low-price names; dollar volume is a useful companion but not a substitute for relative volume.
- Browser QA used the existing local Streamlit server on port 8501; it verified render stability but did not trigger provider collection because US market hours were closed.
- Top2000 yearly Market Movers can still take about 20 seconds locally because eligible-date resolution scans daily price history. A later storage/index pass could add a date-window cache or composite `(timeframe, date)` index if yearly usage becomes frequent.
- Catalyst Links use generic Yahoo / Google / SEC search URLs and company-name queries. They can miss the true cause, surface stale results, or require manual ticker / company disambiguation; this is intentional for the no-crawl V1.
- Why It Moved compact metadata still depends on free yfinance news metadata and SEC current ticker / submissions metadata. Provider timeout, schema drift, rate limiting, current ticker mapping gaps, or stale / irrelevant headlines can produce `FAILED` or `NO_METADATA` states; these are investigation states, not pass / fail catalyst evidence.
- The V1.5 Browser QA verified render, outbound links, and the not-yet-run metadata state. It did not press the live metadata button to avoid turning UI QA into a provider-network test; injected service contracts cover OK / no metadata / failure result rendering inputs.
- Durable DB-backed compact metadata is intentionally deferred. V2 would need explicit source retention policy, freshness semantics, replay behavior, provider throttling, and schema / registry approval before any metadata can be stored.
- `PARTIAL` status prevents false complete-success messaging, but it still does not prove the returned provider rows explain the price move. It only means at least one compact metadata source returned bounded rows while another failed.
- Why It Moved remains a prototype-level investigation panel. The next UX pass should improve information hierarchy and source-state guidance before adding any new provider, classifier, persistence, or summary behavior.
