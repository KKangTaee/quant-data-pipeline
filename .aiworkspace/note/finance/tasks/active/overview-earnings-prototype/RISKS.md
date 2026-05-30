# Risks

- yfinance / Yahoo calendar fields can be missing, delayed, or inconsistent with company IR pages.
- Broad coverage scans can be slow and rate-limited; keep the prototype bounded to manual symbols or latest movers.
- Some provider dates may represent after-close timing differently than official release timestamps.
- Because `event_key` includes date/title/source, provider date changes can leave older estimate rows unless a later cleanup/expiry policy is added.
