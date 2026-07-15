# Institutional Portfolios Source Extension Benchmarks

Status: Active
Last checked: 2026-07-12

## SEC Official 13F

- Primary implementation source should remain SEC official Form 13F data sets plus EDGAR access.
- SEC Form 13F data sets are quarterly, flattened from XML portions of EDGAR Form 13F submissions, and presented as-filed.
- SEC explicitly cautions that the data sets are derived from filer-submitted information and are not a substitute for reviewing the full filings.
- SEC `data.sec.gov` APIs can support filer submission history and accession-level discovery, but the bulk official 13F data set remains the practical primary source for local full-quarter ingestion.

## Dataroma

- Useful benchmark for curated "superinvestor" UX and seed list discovery.
- Dataroma publicly lists 84 superinvestors and shows manager/investor friendly names.
- Terms allow small reference portions with citation but prohibit republishing, reproducing, redistributing, or selling site content.
- Current recommendation: do not build Dataroma scraping as a data source unless written permission / explicit allowed API path is confirmed.

## WhaleWisdom

- Useful benchmark and potential licensed provider.
- WhaleWisdom documents an API for 13F database access with account/API keys, authentication, subscriber tiers, and rate limits.
- Non-subscribers are restricted, while subscribers/enterprise plans unlock broader history or API/bulk access.
- Current recommendation: optional provider adapter only when account, subscription, quota, and terms are available.

## Fintel

- Useful benchmark for institutional ownership pages, recent filers, top holders, and premium packaging.
- Fintel terms explicitly prohibit bots or automated processes for screen scraping, downloading, or harvesting data.
- Current recommendation: benchmark only. Do not scrape.

## Optional Mapping Provider

- OpenFIGI is a candidate for CUSIP-to-FIGI/ticker mapping enrichment because its API supports mapping third-party identifiers to FIGI/ticker metadata.
- It has explicit rate limits and optional API key support.
- Current recommendation: evaluate as a controlled ingestion adapter for mapping quality, with CUSIP licensing/redistribution constraints treated carefully.
