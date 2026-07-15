# Institutional Portfolios Source Extension Sources

Status: Active
Access date: 2026-07-12

| Source | Evidence |
|---|---|
| SEC Form 13F Data Sets, https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets | Official quarterly data source; flattened as-filed XML-derived 13F data; quarterly update and data-quality caveats |
| SEC EDGAR APIs, https://www.sec.gov/search-filings/edgar-application-programming-interfaces | Official API context for submissions history and data.sec.gov JSON APIs |
| SEC Developer Resources, https://www.sec.gov/about/developer-resources | Fair access guidance, efficient scripting, and request moderation |
| Dataroma Terms, https://www.dataroma.com/m/inc/tos.php | Reference-only terms; no republishing/reproducing/redistributing/selling content |
| Dataroma Home, https://www.dataroma.com/m/home.php | Curated superinvestor list and UX benchmark |
| WhaleWisdom API, https://whalewisdom.com/help/api | Account/API-key based 13F API, subscriber restrictions, rate limit |
| WhaleWisdom Subscription Info, https://whalewisdom.com/info/subscription_info | Subscription tiers and API/bulk access signals |
| WhaleWisdom FAQ, https://whalewisdom.com/info/faq | 13F filing timing and data caveats |
| Fintel Terms, https://fintel.io/terms | Explicit prohibition on bots/screen scraping/downloading/harvesting data |
| Fintel Latest 13F Filings, https://fintel.io/latest-13f-filings | UX benchmark and 13F delay caveat |
| OpenFIGI API docs, https://www.openfigi.com/api/documentation | Candidate identifier mapping API, request format and rate limits |

## Local Evidence

- `finance/loaders/price.py`
- `finance/data/data.py`
- `app/services/institutional_portfolios.py`
- `app/web/institutional_portfolios.py`
- `finance/loaders/institutional_13f.py`
- `finance/data/db/schema.py`
- Local MySQL checks on 2026-07-12 for `finance_price.nyse_price_history` and `finance_meta.institutional_13f_*`.
