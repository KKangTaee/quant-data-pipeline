# Why It Moved UI Patterns

Status: Active
Last Updated: 2026-06-04

## Pattern 1: Movement Summary First

Benchmark basis:

- Yahoo Finance and TradingView put ticker identity, price / movement windows, key facts, and stats before deeper source material.

Apply:

- Replace the current two raw fact grids with a tighter movement header:
  - left: Symbol, Name, Sector / Industry, Market Cap
  - middle: Period, Coverage, Rank Type, Rank
  - right: Return %, Previous Return %, Momentum Delta, Volume / Dollar Volume
- The header should be scan-first and not look like a generic table.

Do not:

- Add price prediction, buy/sell wording, or automatic cause labels.

## Pattern 2: Source Status Strip

Benchmark basis:

- Professional tools expose whether news / documents / filings are current, searchable, filtered, or alertable.
- Current implementation already has `NOT_REQUESTED`, `OK`, `PARTIAL`, `FAILED`, and `NO_METADATA`.

Apply:

- Add a compact status strip above source sections:
  - `Lookup`: Not requested / Complete / Partial / Failed / No metadata
  - `News`: rows count or failure
  - `SEC`: rows count or failure
  - `Fetched`: timestamp if available
  - `Storage`: Session-only
- Use warning tone for `PARTIAL` and `NO_METADATA`.

Do not:

- Treat provider rows as cause evidence. They are investigation leads.

## Pattern 3: Evidence Lanes Instead Of Raw Metadata Dump

Benchmark basis:

- Yahoo / Seeking Alpha / Koyfin separate news, transcripts, SEC filings, earnings, ratings, and financials.
- SEC EDGAR is official filing metadata and should not be visually mixed with general news.

Apply:

- Rename `Compact Metadata` to `Investigation Leads`.
- Use three lanes:
  - `News Metadata`
  - `SEC Filings`
  - `External Searches`
- Within each lane, show empty / partial / failed states locally.
- Use clickable `Open` URL cells in every lane.

Do not:

- Add article body, filing body, AI summary, sentiment score, or catalyst class.

## Pattern 4: Prioritized SEC Filing Display

Benchmark basis:

- Filing-focused pages surface form type, filing date, description, and source link; users filter by form type / date.

Apply:

- Keep SEC metadata columns compact: `Form`, `Filing Date`, `Title`, `Open`.
- Sort important form types first when dates tie or when presenting compact top rows:
  - `8-K`, `10-Q`, `10-K`, `S-1`, `S-3`, `S-8`, `4`, then others.
- Add short form hints only in UI copy or optional small helper text:
  - `8-K`: material event
  - `10-Q`: quarterly report
  - `10-K`: annual report
  - `4`: insider transaction

Do not:

- Parse filing content or infer whether the filing caused the move.

## Pattern 5: External Searches As Secondary Tools

Benchmark basis:

- Professional products separate first-party collected evidence from search / tool launch points.

Apply:

- Keep `External searches` collapsed by default.
- Keep rows for:
  - Yahoo Finance
  - Google News
  - SEC Company Search
  - Investor Relations / Earnings Search
  - Google News KR
  - Naver News
- Place `Open` near `Source` so users can click without horizontal scrolling.

Do not:

- Turn these into primary buttons again.

## Pattern 6: Korean Source Boundary

Benchmark basis:

- Koyfin / Bloomberg-like source breadth is valuable, but provider licensing and source policy matter.

Apply:

- V1.6: keep Korean sources outbound-only.
- V1.7/V1.8: define provider policy before metadata fetch:
  - source terms
  - API credentials
  - quota / throttling
  - metadata fields only
  - no article body
  - session-only or storage policy

Do not:

- Scrape Korean news sites or store article text.

## Proposed V1.6 Screen Structure

```text
Why It Moved
Manual investigation panel. No automatic cause judgement.

[Symbol selector]

[Movement Summary Header]
Symbol / Name / Sector / Industry / Market Cap
Period / Coverage / Rank Type / Rank
Return / Previous Return / Momentum Delta / Volume / Dollar Volume

[Metadata Status Strip]
Lookup status | News rows | SEC rows | Fetched at | Session-only

[Fetch compact metadata]

[Investigation Leads]
Tabs or stacked sections:
  News Metadata
  SEC Filings
  External Searches
```

## Implementation Priority

1. V1.6: UI hierarchy only, no provider changes.
2. V1.7: metadata display quality, status counts, SEC form priority.
3. V1.8: Korean source provider policy decision.
4. V2: DB-backed compact metadata only after retention / freshness / replay policy.
