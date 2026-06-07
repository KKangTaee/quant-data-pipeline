# Overview Market Sentiment V1 Notes

- CNN endpoint test: `https://production.dataviz.cnn.io/index/fearandgreed/graphdata` returns bot text without headers, but returns JSON with CNN referer and browser-like user agent.
- AAII official historical HTML table is parseable with rows like `Jun 3 / 36.3% / 26.7% / 37.0%`.
- The existing finance docs already classify Fear & Greed as optional sentiment context, not a trading signal.
- AAII official page is visible in Browser, but Python `urllib` can receive `Pardon Our Interruption`; `curl_cffi` browser impersonation with document headers returns the official table and was used for the collector.
- Altair v6 accepts `cornerRadiusEnd`, not `cornerRadiusRight`; Browser QA caught this in the hidden CNN Components chart render path.
- The Sentiment tab should start with the interpretation path, not the raw cards: data confidence first, then fear/greed, CNN internal split, AAII pessimism, combined phase, and next checks.
- Streamlit can keep old imported modules alive when an earlier server process remains on the same port. After changing the read model schema, restart the local Streamlit process before Browser QA.
- User-facing component names need Korean market-language labels. For example `Safe Haven Demand` should read as `주식 vs 안전자산` in driver summaries, otherwise Korean particles can make the sentence ambiguous.
