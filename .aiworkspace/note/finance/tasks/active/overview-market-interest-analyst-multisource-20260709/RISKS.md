# Risks

## Source Policy

- Yahoo/yfinance is used only for explicit selected-symbol, session-only personal research metadata. No durable DB storage or analyst report body collection is added.
- Nasdaq.com, WSJ Markets, and MarketWatch expose useful analyst pages but have provider / terms constraints. This task does not add automatic HTML scraping for those sites.
- The UI labels those sources as public cross-check links, not as automatically parsed evidence.

## Product Interpretation

- Analyst ratings and target changes can be misread as investment advice. UI copy must keep this as `조사 보조 정보`, not recommendation, score, or buy/sell signal.
- The table may contain source-provided rating words such as `Buy` or `Sell`; surrounding copy frames them as source values only, not app output.
