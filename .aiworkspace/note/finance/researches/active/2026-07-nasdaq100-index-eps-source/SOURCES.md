# Sources

Status: Complete
Access date: 2026-07-12

## GuruFocus

1. [Nasdaq 100 PE Ratio](https://www.gurufocus.com/economic_indicators/6778/nasdaq-100-pe-ratio)
   - Supports: daily NDX P/E, 5Y/20Y historical chart availability, current value
   - Type: provider product page
   - Evidence: Documented
   - Limitation: aggregate methodology and release vintage not disclosed
2. [Nasdaq 100 Earnings per Share](https://www.gurufocus.com/economic_indicators/5870/nasdaq-100-earnings-per-share)
   - Supports: quarterly index EPS series and indicator ID
   - Type: provider product page
   - Evidence: Documented
   - Limitation: page does not explicitly call the EPS TTM
3. [Economic Indicator Historical Data API](https://www.gurufocus.com/data-api/economic/data)
   - Supports: `GET /economic/{nameOrId}` historical date/value response
   - Type: official API docs
   - Evidence: Documented
4. [GuruFocus Data API Pricing](https://www.gurufocus.com/data-api/pricing)
   - Supports: Economic Data add-on/PAYG and commercial packaging signals
   - Type: official pricing page
   - Evidence: Documented
   - Limitation: pricing and rights can change; agreement controls actual use

## Nasdaq

5. [Nasdaq Index Data](https://www.nasdaq.com/solutions/global-indexes/data)
   - Supports: GIDS/GIW/GIFFD roles, licensing requirement
   - Type: official product page
   - Evidence: Documented
6. [Global Index Watch](https://www.nasdaq.com/solutions/global-indexes/data/giw)
   - Supports: historical/current composition, weights, corporate actions for subscribers
   - Type: official product page
   - Evidence: Documented
7. [GIW Web Service Specification](https://www.nasdaq.com/docs/GIW_WebService_Spec.pdf)
   - Supports: weights/history/divisor service fields
   - Type: official specification
   - Evidence: Documented
8. [GIDS 2.0 Specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/globalindex2-0.pdf)
   - Supports: index value/summary and ETP valuation message fields; no public EPS/P-E field found
   - Type: official specification
   - Evidence: Observed
9. [NDX Overview](https://indexes.nasdaq.com/Index/Overview/NDX)
   - Supports: official index level, divisor and research links
   - Type: official index page
   - Evidence: Observed
10. [NDX Q4 2025 Earnings Update](https://indexes.nasdaq.com/docs/NDX_Earnings_Update_-_Q4_2025.pdf)
    - Supports: Nasdaq research uses FactSet for index-weighted earnings analysis
    - Type: official research PDF
    - Evidence: Documented

## Enterprise Providers

11. [FactSet Benchmarks API](https://developer.factset.com/api-catalog/factset-benchmarks-api)
    - Supports: index ratios endpoint and rolling constituent aggregate method
    - Type: official API catalog
    - Evidence: Documented
12. [LSEG I/B/E/S Estimates and Global Aggregates](https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates)
    - Supports: index/country/sector aggregate earnings, weekly/monthly delivery, deep history
    - Type: official product page
    - Evidence: Documented
13. [LSEG Nasdaq Indices](https://www.lseg.com/en/data-analytics/financial-data/indices/equity-indices/third-party/nasdaq-indices)
    - Supports: Nasdaq-100 coverage and delivery channels
    - Type: official product page
    - Evidence: Documented
14. [Bloomberg Data License](https://professional.bloomberg.com/products/data/data-management/data-license/)
    - Supports: historical pricing/fundamentals/estimates and REST/SFTP/cloud delivery
    - Type: official product page
    - Evidence: Claimed
    - Limitation: exact NDX P/E/EPS field not publicly verified

## Public Filing Source

15. [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
    - Supports: filing metadata and XBRL company facts without API key
    - Type: official API docs
    - Evidence: Documented
    - Limitation: does not provide NDX historical weights or index aggregate EPS
