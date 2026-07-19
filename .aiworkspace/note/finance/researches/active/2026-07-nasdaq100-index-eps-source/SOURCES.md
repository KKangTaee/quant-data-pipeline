# Sources

Status: Complete
Access date: 2026-07-14

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
   - Supports: Free 월 100 requests, Economic Data가 base plan 제외 add-on임을 보여주는 feature table/endpoint explorer, `+$90/month`, PAYG `$0.10/request`, 초기 `$100` top-up
   - Type: official pricing page
   - Evidence: Observed + Documented
   - Limitation: 동적 icon cell은 text-only crawler에서 누락될 수 있어 2026-07-14 실제 DOM을 교차확인함
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

## Public Chart Automation Review

26. [World PE Ratio Nasdaq-100](https://worldperatio.com/index/nasdaq-100/)
    - Supports: account-free monthly QQQ-based P/E chart history embedded in public HTML
    - Type: public chart page
    - Evidence: Observed
    - Limitation: underlying provider, aggregate earnings method, revision/PIT contract and automated reuse rights are not identified
27. [Trendonify Nasdaq-100 P/E](https://trendonify.com/united-states/stock-market/nasdaq-100/pe-ratio)
    - Supports: public monthly Nasdaq-100 P/E table from 1990
    - Type: public chart/data page
    - Evidence: Observed
    - Limitation: data source is generic and latest observation was stale at review time
28. [Trendonify Terms](https://trendonify.com/terms)
    - Supports: scraping, crawling and automated extraction require prior written permission
    - Type: official site terms
    - Evidence: Documented
29. [VCP Scanner Nasdaq-100 Valuation](https://vcpscanner.com/market-valuation/nasdaq-100)
    - Supports: daily constituent-financial-based P/E history and current aggregate
    - Type: public product page
    - Evidence: Observed
    - Limitation: current value materially differs from other sources and exact index aggregate contract needs validation
30. [VCP Scanner Methodology](https://vcpscanner.com/methodology)
    - Supports: SEC EDGAR statements, exchange price feeds and constituent-level metric computation
    - Type: official methodology page
    - Evidence: Documented
31. [VCP Scanner Terms](https://vcpscanner.com/terms)
    - Supports: bulk scraping/harvesting and systematic API extraction are prohibited without permission
    - Type: official site terms
    - Evidence: Documented
32. [Invesco QQQ Fact Sheet](https://www.invesco.com/content/dam/invesco/us/en/product-documents/etf/fact-sheet/qqq-invesco-qqq-etf-fact-sheet.pdf)
    - Supports: official current-quarter QQQ weighted harmonic trailing P/E and calculation description
    - Type: issuer fact sheet
    - Evidence: Documented
    - Limitation: stable five-year machine-readable archive/API was not found; suitable for current calibration, not primary history

## 2026-07-14 Free Alternative Verification

33. [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/)
   - Supports: free-key NDX historical price OHLC endpoint
   - Type: official API docs
   - Evidence: Documented
   - Limitation: historical Nasdaq-100 P/E/EPS endpoint는 확인되지 않음
34. [FRED NASDAQ-100](https://fred.stlouisfed.org/series/NASDAQ100)
   - Supports: official-source daily NDX closing level
   - Type: official public data page
   - Evidence: Documented
   - Limitation: P/E/EPS가 없고 Nasdaq copyright/pre-approval note가 있음
35. [nfin API](https://nfin.dev/)
   - Supports: anonymous Nasdaq quotes, index snapshots and historical price rows
   - Type: public API documentation
   - Evidence: Documented
   - Limitation: index fundamental P/E/EPS route가 없고 upstream redistribution contract가 공개 문서에서 명확하지 않음
36. [Business Quant Financial Statements API](https://businessquant.com/docs/api/financial-statements)
   - Supports: free-key SEC-derived annual/quarterly/TTM statements including foreign issuer filings
   - Type: official API docs
   - Evidence: Documented
   - Limitation: direct NDX aggregate가 아니며 pricing table상 Free financial statement history는 3년
37. [Business Quant Pricing](https://businessquant.com/pricing)
   - Supports: Free `$0`, no credit card, 30 API calls/day, 0.1GB/month, Free financial statements 3 years, Enterprise commercial-use signal
   - Type: official pricing page
   - Evidence: Documented
38. [Business Quant Terms of Use](https://businessquant.com/terms-of-use)
   - Supports: website/data accuracy disclaimer, credential sharing restriction, no general data IP license grant
   - Type: official terms
   - Evidence: Documented
   - Limitation: API-specific retention/derived-output grant가 명확하지 않음
39. [MacroMicro Nasdaq-100 Forward P/E](https://en.macromicro.me/series/23955/nasdaq-100-pe)
   - Supports: monthly forward P/E surface
   - Type: public chart page
   - Evidence: Observed
   - Limitation: trailing P/E가 아니며 automated API/download는 free production contract가 아님
40. [MacroMicro Enterprise/API](https://en.macromicro.me/subscribe-enterprise)
   - Supports: Business AI data download, API Essential historical integration, Custom exclusive-indicator/commercial licensing
   - Type: official pricing/FAQ page
   - Evidence: Documented
   - Limitation: series `23955`의 개별 entitlement는 로그인된 dataset list 또는 provider 확인이 필요함
41. [MacroMicro Help - Can I download data after subscribing?](https://support.macromicro.me/en/faq/152)
   - Supports: Prime/Max individual plans do not include raw CSV; raw download/API belongs to Enterprise
   - Type: official Help Center
   - Evidence: Documented
42. [MacroMicro Help - Free member benefits](https://support.macromicro.me/en/faq/131)
   - Supports: free member has limited chart views/save limits; Business adds data download
   - Type: official Help Center
   - Evidence: Documented
43. [MacroMicro Terms of Service](https://en.macromicro.me/terms)
   - Supports: prior written consent requirement for data download/citation/reposting; restrictions on database reconstruction, redistribution and derivative works
   - Type: official terms
   - Evidence: Documented
44. [Nasdaq NDX Extended Presentation](https://indexes.nasdaq.com/docs/NDX%20Extended%20Presentation.pdf)
   - Supports: long-run NDX trailing P/E/earnings chart through 2025
   - Type: official research PDF
   - Evidence: Documented
   - Limitation: chart-only, underlying source Bloomberg, no monthly machine-readable value contract
45. [World PE Ratio Nasdaq-100](https://worldperatio.com/index/nasdaq-100/)
   - Supports: account-free QQQ-based historical P/E chart and period statistics
   - Type: public chart page
   - Evidence: Observed
   - Limitation: documented API, raw source, automated extraction and reuse license were not found

## 2026-07-14 Implementation Feasibility Sources

46. [Tiingo End-of-Day Product](https://www.tiingo.com/products/end-of-day-stock-price-data)
   - Supports: 60+ years, raw/adjusted prices, split/dividend fields, REST, free 50 requests/hour and 1,000/day
   - Type: official product/pricing page
   - Evidence: Documented
   - Limitation: free license is internal use only
47. [Tiingo EOD API Documentation](https://www.tiingo.com/documentation/end-of-day)
   - Supports: historical date-range/monthly resample endpoint, token requirement, adjusted fields, daily supported ticker catalog
   - Type: official API docs
   - Evidence: Documented
48. [Tiingo API Pricing](https://www.tiingo.com/about/pricing)
   - Supports: Starter `$0`, 500 unique symbols/month, 50 requests/hour, 1,000/day, 1GB/month, internal-only definition
   - Type: official pricing page
   - Evidence: Documented
49. [Tiingo Symbology](https://www.tiingo.com/documentation/appendix/symbology)
   - Supports: share-class symbol rules and delisted coverage caveat
   - Type: official API docs
   - Evidence: Documented
50. [Tiingo Supported Tickers Catalog](https://apimedia.tiingo.com/docs/tiingo/daily/supported_tickers.zip)
   - Supports: 22/23 exact historical EOD gap symbols plus `GEN` successor candidate for `SYMC`
   - Type: official daily catalog
   - Evidence: Observed local catalog smoke
   - Limitation: actual price payload requires free account token; recycled tickers require identity validation
51. [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
   - Supports: no-auth companyfacts/submissions and official ticker-to-CIK mapping
   - Type: official API docs
   - Evidence: Documented + payload smoke
52. [SEC Form N-PORT Data Sets](https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets)
   - Supports: public structured holdings data, quarterly data-set publication and archive from 2019
   - Type: official SEC data page
   - Evidence: Documented
53. [SEC N-PORT Compliance Delay](https://www.sec.gov/rules-regulations/2025/04/s7-26-22)
   - Supports: monthly public-reporting amendment compliance delayed to 2027/2028
   - Type: official final-rule page
   - Evidence: Documented
54. [Alpha Vantage API Documentation](https://www.alphavantage.co/documentation/)
   - Supports: listing-status active/delisted catalog; full daily history boundary
   - Type: official API docs
   - Evidence: Documented
55. [Alpha Vantage Premium / Limits](https://www.alphavantage.co/premium/)
   - Supports: standard free limit 25 requests/day and premium feature boundary
   - Type: official pricing page
   - Evidence: Documented
56. [SimFin Pricing](https://www.simfin.com/en/prices/)
   - Supports: free account, API/bulk download, five-year chart and fundamentals history
   - Type: official pricing page
   - Evidence: Documented
   - Limitation: five years is shorter than the 119-month input window
