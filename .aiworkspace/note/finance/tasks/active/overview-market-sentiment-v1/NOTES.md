# Overview Market Sentiment V1 Notes

- CNN endpoint test: `https://production.dataviz.cnn.io/index/fearandgreed/graphdata` returns bot text without headers, but returns JSON with CNN referer and browser-like user agent.
- AAII official historical HTML table is parseable with rows like `Jun 3 / 36.3% / 26.7% / 37.0%`.
- The existing finance docs already classify Fear & Greed as optional sentiment context, not a trading signal.
- AAII official page is visible in Browser, but Python `urllib` can receive `Pardon Our Interruption`; `curl_cffi` browser impersonation with document headers returns the official table and was used for the collector.
- Altair v6 accepts `cornerRadiusEnd`, not `cornerRadiusRight`; Browser QA caught this in the hidden CNN Components chart render path.
