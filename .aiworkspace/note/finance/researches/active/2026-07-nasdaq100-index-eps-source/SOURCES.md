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
   - Supports: Free 월 100 requests 표시, Economic Data add-on/PAYG, commercial packaging signals
   - Type: official pricing page
   - Evidence: Documented
   - Limitation: Free API 표와 Economic Data add-on 표가 함께 있어 실제 free endpoint entitlement는 authenticated smoke가 필요함
5. [GuruFocus Terms of Use](https://www.gurufocus.com/term-of-use)
   - Supports: personal/professional internal research boundary, external end-user/redistribution restriction, public-site automated monitoring restriction
   - Type: official terms
   - Evidence: Documented
   - Limitation: accepted Data API Agreement and account plan terms take precedence for API storage/retention details
6. [GuruFocus Sample License Agreement](https://userupload.gurufocus.com/1803094042721021952.pdf)
   - Supports: one negotiated agreement permits internal development/testing/use while prohibiting external redistribution of provider data and derived results
   - Type: official-hosted customer-specific agreement example
   - Evidence: Observed
   - Limitation: customer-specific Exhibit A; not a universal Data API contract

## Nasdaq

7. [Nasdaq Index Data](https://www.nasdaq.com/solutions/global-indexes/data)
   - Supports: GIDS/GIW/GIFFD roles, licensing requirement
   - Type: official product page
   - Evidence: Documented
8. [Global Index Watch](https://www.nasdaq.com/solutions/global-indexes/data/giw)
   - Supports: historical/current composition, weights, corporate actions for subscribers
   - Type: official product page
   - Evidence: Documented
9. [GIW Web Service Specification](https://www.nasdaq.com/docs/GIW_WebService_Spec.pdf)
   - Supports: weights/history/divisor service fields
   - Type: official specification
   - Evidence: Documented
10. [GIDS 2.0 Specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/globalindex2-0.pdf)
   - Supports: index value/summary and ETP valuation message fields; no public EPS/P-E field found
   - Type: official specification
   - Evidence: Observed
11. [NDX Overview](https://indexes.nasdaq.com/Index/Overview/NDX)
   - Supports: official index level, divisor and research links
   - Type: official index page
   - Evidence: Observed
12. [NDX Q4 2025 Earnings Update](https://indexes.nasdaq.com/docs/NDX_Earnings_Update_-_Q4_2025.pdf)
    - Supports: Nasdaq research uses FactSet for index-weighted earnings analysis
    - Type: official research PDF
    - Evidence: Documented

## Enterprise Providers

13. [FactSet Benchmarks API](https://developer.factset.com/api-catalog/factset-benchmarks-api)
    - Supports: index ratios endpoint and rolling constituent aggregate method
    - Type: official API catalog
    - Evidence: Documented
14. [LSEG I/B/E/S Estimates and Global Aggregates](https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates)
    - Supports: index/country/sector aggregate earnings, weekly/monthly delivery, deep history
    - Type: official product page
    - Evidence: Documented
15. [LSEG Nasdaq Indices](https://www.lseg.com/en/data-analytics/financial-data/indices/equity-indices/third-party/nasdaq-indices)
    - Supports: Nasdaq-100 coverage and delivery channels
    - Type: official product page
    - Evidence: Documented
16. [Bloomberg Data License](https://professional.bloomberg.com/products/data/data-management/data-license/)
    - Supports: historical pricing/fundamentals/estimates and REST/SFTP/cloud delivery
    - Type: official product page
    - Evidence: Claimed
    - Limitation: exact NDX P/E/EPS field not publicly verified

## Public Filing Source

17. [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
    - Supports: filing metadata and XBRL company facts without authentication or API key
    - Type: official API docs
    - Evidence: Documented
    - Limitation: does not provide NDX historical weights or index aggregate EPS
18. [QQQ September 2024 Annual Filing](https://www.sec.gov/Archives/edgar/data/1067839/000119312524285734/d876223dn30b2.htm)
    - Supports: complete QQQ schedule of investments and statement that first/third-quarter complete holdings are filed on Form N-PORT
    - Type: SEC issuer filing
    - Evidence: Documented
19. [QQQ March 2026 Semi-Annual Filing](https://www.sec.gov/Archives/edgar/data/1067839/000119312526250483/8deb6f921189c0e.htm)
    - Supports: full QQQ holdings schedule and 102-holding fund summary
    - Type: SEC issuer filing
    - Evidence: Documented
20. [Nasdaq Global Index Policies](https://www.nasdaq.com/solutions/global-indexes/policies)
    - Supports: public current/rebalance constituent weight publication for selected licensed UCITS indexes, including NDX
    - Type: official policy page
    - Evidence: Documented
    - Limitation: public page is not a documented five-year historical weight API
21. [Current Public NDX Weight File](https://www.nasdaq.com/docs/2026/05/04/NDX.pdf)
    - Supports: current full NDX constituent/weight snapshot without login
    - Type: official public PDF
    - Evidence: Documented
22. [Nasdaq NDX Weighting Page](https://indexes.nasdaq.com/Index/Weighting/NDX)
    - Supports: current weighting surface and confirms full/historical access is login-gated
    - Type: official index page
    - Evidence: Observed
23. [Nasdaq-100 Methodology](https://indexes.nasdaq.com/docs/Methodology_NDX.pdf)
    - Supports: quarterly rebalance schedule and modified capitalization weighting rules
    - Type: official methodology
    - Evidence: Documented
24. [Nasdaq-100 2023 Special Rebalance](https://www.nasdaq.com/press-release/the-nasdaq-100-index-special-rebalance-to-be-effective-july-24-2023-2023-07-07)
    - Supports: known mid-quarter special rebalance that must be handled in a five-year reconstruction
    - Type: official press release
    - Evidence: Documented
25. [FRED NASDAQ-100 Series](https://fred.stlouisfed.org/series/NASDAQ100)
    - Supports: daily NDX close history sourced from Nasdaq
    - Type: official Federal Reserve data page
    - Evidence: Documented
    - Limitation: series notes mark Nasdaq copyright/pre-approval; QQQ EOD is the safer no-license V1 price proxy
