# Why It Moved Benchmark Notes

Status: Active
Last Updated: 2026-06-04

## Research Question

`Overview > Market Movers > Why It Moved`를 prototype-level link / metadata panel에서 더 product-like manual investigation panel로 개선하려면, comparable finance research products의 stock detail / news / filings / catalyst investigation patterns 중 무엇을 차용하고 무엇을 제외해야 하는가?

Current project boundary:

- Manual investigation only.
- No automatic catalyst judgement.
- No AI summary.
- No article body or filing body collection.
- No DB schema change or workflow JSONL write for compact metadata.
- Fetch only selected ticker, button-triggered, session-only.

## Benchmark Set

| Product / Source | Category | Why Included |
|---|---|---|
| Yahoo Finance quote page | Retail quote / news detail | Public stock page pattern combining price move, company facts, latest news, earnings / SEC filters, and basic financial context |
| TradingView symbol page | Chart-first market research | Strong pattern for symbol header, performance windows, key facts, latest earnings, stats, and tabbed source categories |
| Koyfin company snapshots + News / Transcripts | Professional research dashboard | Pattern for top-down company snapshot, estimates, earnings surprises, ETF exposure, news / filings / transcripts grouping |
| Seeking Alpha Premium feature surface | Investor research / rating workflow | Pattern for ratings / factor grades, transcripts, financials, side-by-side compare, alerts, and symbol-page research hierarchy |
| Bloomberg Terminal News + SEC EDGAR | Institutional news / official filings | Pattern for integrated market-moving news / alerts / source breadth and official filing search / metadata separation |

## Product Notes

### Yahoo Finance

Evidence label: observed from publicly indexed HPE quote page.

Relevant patterns:

- Stock page starts with ticker / company identity, price, chart range, quote metrics, company overview, recent news, performance overview, earnings trends, statistics, analyst insights, and research reports.
- Recent News includes source filtering such as news, earnings calls, press releases, and SEC filings.
- The quote page puts latest market data and movement context before deeper research sections.

Applicability:

- Keep Why It Moved header focused on identity + movement metrics before news / filings.
- Add source lanes or tabs for `News`, `SEC`, and `External searches`.
- Do not copy Yahoo Scout-like automated narrative because this project explicitly excludes AI summary / automatic cause judgement.

### TradingView

Evidence label: observed from public HPE symbol page and support / product docs.

Relevant patterns:

- Symbol page exposes high-level tabs such as Overview, Financials, News, Documents, Community, Technicals, Forecasts, Seasonals, Options, Bonds, and ETFs.
- The public HPE page shows short/medium/long performance windows, `Key facts today`, latest earnings metadata, key stats, and company identity in a compact vertical flow.
- TradingView keeps chart / movement context close to symbol identity while separating documents and news into dedicated navigation surfaces.

Applicability:

- Add a compact movement header with current return, previous return, momentum delta, rank source, and period.
- Use source sections rather than dumping all metadata into one table.
- Consider `Movement`, `News`, `SEC`, `External` section labels rather than generic `Compact Metadata`.

Out of scope:

- Broker connection / trading actions must not be copied.
- `Analyze the impact` style automated interpretation is out of V1.6 scope.

### Koyfin

Evidence label: documented product feature pages and release notes.

Relevant patterns:

- Company snapshots are positioned as top-down company information, including company overview, price target, financial / valuation metrics, ETF exposure, analyst estimates, and earnings history / surprises.
- Corporate transcripts live under News & Filings and are grouped by years, with participant lists.
- News / transcript search supports date range, event type, company, watchlist / index, sector, and keyword filtering, and results appear chronologically with snippets.

Applicability:

- Why It Moved should read as a compact investigation workspace: company / movement snapshot first, source evidence second, deeper external research third.
- SEC forms should be grouped and labeled by likely investigation relevance, not just raw filing order.
- Korean source expansion should be treated as a source lane / policy decision, not mixed silently into generic news.

Out of scope:

- Transcript body ingestion, keyword snippets, saved / printed transcripts, and sentiment trend extraction are out of current boundary.

### Seeking Alpha

Evidence label: documented Premium feature list and public symbol-page search result.

Relevant patterns:

- Symbol pages combine ratings, factor grades, news, transcripts, financials, earnings, and SEC filings.
- Seeking Alpha explicitly uses ratings / grades as quick scanning aids, but also provides access to transcripts and financial statements for deeper research.
- Alerts and broker linking exist, but are outside this project boundary.

Applicability:

- Use compact badges for source status and investigation readiness, not investment ratings.
- A manual `Research state` badge such as `Not requested`, `Complete`, `Partial`, `No metadata`, `Failed` is aligned with the quick-scan pattern without implying recommendation.
- Do not introduce buy/sell / factor-grade style judgement.

### Bloomberg Terminal News + SEC EDGAR

Evidence label: documented Bloomberg News product page and SEC official search page.

Relevant patterns:

- Bloomberg positions news as timely, tailored, analytical, and integrated across charts / visualizations. It emphasizes alerts, source breadth, and market-moving event coverage.
- SEC EDGAR provides official filing search by company / ticker, full-text search, latest filings, daily filings by form type, and APIs / RSS feeds for public filing data.

Applicability:

- Source state and freshness should be visible: when fetched, which sources returned rows, which failed.
- Official SEC metadata deserves its own lane because it has different reliability / meaning from news.
- `External searches` should stay secondary because those links are launch points, not evidence already collected by the app.

Out of scope:

- Real-time news alerts, news volume / sentiment analytics, body search, EDGAR full-text ingestion, APIs / RSS persistence, and durable filing database expansion are V2+ only.

## Cross-Benchmark Takeaways

1. A stock investigation surface usually begins with identity + movement context, not a link list.
2. Source categories are separated: news, filings / documents, financials / earnings, analysts / ratings, and external tools.
3. Professional tools make source state visible: timeliness, provider/source, filters, and result types.
4. News and filings are not equivalent evidence. Filing metadata should be visually distinct from news metadata.
5. Automated summaries / ratings are common in commercial tools, but they conflict with this project's V1.6 boundary.
6. The most useful near-term improvement is information hierarchy, not more providers.

## Recommendation

Proceed with `Why It Moved V1.6 UX Pass` before adding new data providers.

V1.6 should:

- Keep no-classifier / no-summary / no-body / session-only boundary.
- Reframe the panel as an investigation board.
- Add a movement summary header and metadata status strip.
- Split evidence into `News Metadata`, `SEC Filings`, and `External Searches`.
- Keep Korean sources as external search rows unless a Korean metadata provider policy is approved.
- Treat `PARTIAL` as warning-level evidence, not success.
