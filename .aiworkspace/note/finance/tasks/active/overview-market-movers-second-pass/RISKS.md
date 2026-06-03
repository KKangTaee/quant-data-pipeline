# Risks

- Provider quote timeout can turn a normally short snapshot into a multi-minute run.
- Daily intraday return and previous daily return use different end points, so UI text must avoid implying perfect apples-to-apples comparison.
- Raw volume favors high-share-count / low-price names; dollar volume is a useful companion but not a substitute for relative volume.
- Browser QA used the existing local Streamlit server on port 8501; it verified render stability but did not trigger provider collection because US market hours were closed.
- Top2000 yearly Market Movers can still take about 20 seconds locally because eligible-date resolution scans daily price history. A later storage/index pass could add a date-window cache or composite `(timeframe, date)` index if yearly usage becomes frequent.
- Catalyst Links use generic Yahoo / Google / SEC search URLs and company-name queries. They can miss the true cause, surface stale results, or require manual ticker / company disambiguation; this is intentional for the no-crawl V1.
