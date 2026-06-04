# Why It Moved Benchmark Sources

Status: Active
Access Date: 2026-06-05

## Sources

### Yahoo Finance HPE quote page

- URL: https://finance.yahoo.com/quote/HPE/
- Evidence label: observed from publicly indexed page text.
- Supports:
  - quote page combines price / chart, quote metrics, company overview, recent news, earnings / SEC filters, performance overview, earnings trends, statistics, analyst insights, and reports.
- Limits:
  - Page is dynamic and may vary by locale, subscription state, and market time.
  - Yahoo Scout-style automated narrative is out of project scope.

### TradingView HPE symbol page

- URL: https://www.tradingview.com/symbols/NYSE-HPE/
- Evidence label: observed from public page.
- Supports:
  - symbol page tabs: Overview, Financials, News, Documents, Community, Technicals, Forecasts, Seasonals, Options, Bonds, ETFs.
  - compact key facts, performance windows, latest earnings, and key stats patterns.
- Limits:
  - Some features may require login or paid plans.
  - Trading / broker actions are out of project scope.

### Koyfin company snapshots

- URL: https://www.koyfin.com/features/company-snapshots/
- Evidence label: documented product feature page.
- Supports:
  - top-down company snapshot, company overview, valuation / financial metrics, ETF exposure, analyst estimates, earnings history / surprises.
- Limits:
  - Marketing page, not full logged-in workflow.

### Koyfin corporate transcripts

- URL: https://www.koyfin.com/help/release-notes/release-v3-2/
- Evidence label: documented release note.
- Supports:
  - transcripts are grouped under News & Filings and cover earnings calls, shareholder / analyst calls, conferences, M&A calls, investor days.
- Limits:
  - Transcript body collection is explicitly out of current project scope.

### Koyfin transcripts & news search

- URL: https://www.koyfin.com/help/release-notes/release-v3-11/
- Evidence label: documented release note.
- Supports:
  - search / filter patterns by date range, event type, companies, lists, sectors, keywords, and chronological results.
- Limits:
  - Advanced search and article snippets are not directly adoptable without provider / licensing decisions.

### Seeking Alpha Premium feature list

- URL: https://help.seekingalpha.com/premium/seeking-alpha-premium-feature-list
- Evidence label: documented help page.
- Supports:
  - symbol pages with ratings, factor-grade snapshots, transcripts, stock financials, comparisons, alerts, and portfolio features.
- Limits:
  - Ratings / factor grades and broker linking conflict with this project's current no-recommendation / no-broker boundary.

### Bloomberg Terminal News

- URL: https://professional.bloomberg.com/products/bloomberg-terminal/news/
- Evidence label: documented product page.
- Supports:
  - timely / tailored / integrated news, alerts, source breadth, news integrated with charts / visualizations, news volume / sentiment concepts.
- Limits:
  - Institutional / paid terminal functionality and alerting are out of V1.6 scope.

### SEC Search Filings

- URL: https://www.sec.gov/search-filings
- Evidence label: official source.
- Supports:
  - official EDGAR company search, full-text search, latest filings, daily filing by form type, APIs, RSS feeds.
- Limits:
  - Full-text filing search / API ingestion / RSS persistence require separate V2 storage and source policy.

### SEC EDGAR Full Text Search

- URL: https://www.sec.gov/edgar/search/
- Evidence label: official source, rechecked 2026-06-05 with Browser.
- Supports:
  - result filtering by entity, form / filing type, and filed date.
  - result table separates form/file metadata from `Open document` and `Open filing` actions.
- Limits:
  - This source supports official-link preservation and selected-document reading, not automatic cause judgement.

### BamSEC Key Exhibits / Document Search

- URL: https://help.bamsec.com/docs/key-exhibits
- URL: https://help.bamsec.com/hc/en-us/articles/45646409684755-Document-Search
- Evidence label: documented help pages, rechecked 2026-06-05.
- Supports:
  - filing/exhibit navigation, chronological exhibit lists, and document search within filings / transcripts.
- Limits:
  - Product details may require account access; this project only borrows bounded exhibit / document navigation patterns.

### Quartr Filings Search

- URL: https://quartr.com/features/filings-search
- Evidence label: documented feature page, rechecked 2026-06-05.
- Supports:
  - filing search results with company, filing type, date, text snippet, and jump-to-location behavior.
- Limits:
  - Global search and snippets are product capabilities; current implementation stays limited to selected SEC filing preview.

### AlphaSense SEC Filings / Company Documents

- URL: https://help.alpha-sense.com/hc/en-us/articles/41887692936083-SEC-Filings-Overview
- URL: https://help.alpha-sense.com/en/articles/5578740-search-library-identifying-the-right-sources-for-my-search
- Evidence label: documented help pages, rechecked 2026-06-05.
- Supports:
  - company documents / SEC filings as auditable source sets inside a broader research search workflow.
- Limits:
  - AI / summary / broad document-search patterns remain out of current Why It Moved boundary.
