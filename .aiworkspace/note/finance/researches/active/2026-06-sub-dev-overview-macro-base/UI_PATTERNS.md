# UI Patterns

Status: Active
Last Updated: 2026-06-08

## Summary

The best fit for this project is a summary-first, evidence-labeled market context workflow. Overview should not become a recommendation engine. It should help the user see current market pressure, breadth, upcoming event risk, sentiment backdrop, and whether the data is fresh enough to trust as context.

## Pattern Catalog

### 1. Market Pulse Cockpit

- Seen in: Koyfin curated dashboards, OpenBB dashboards.
- User problem: the user needs one place to understand the current market backdrop before moving into deep tabs.
- Interaction shape: top summary lane with compact cards for futures pressure, sentiment, breadth, event risk, data health, and latest mover context.
- Data required: existing futures macro thermometer, market movers / sector leadership snapshot, sentiment snapshot, events snapshot, collection ops snapshot.
- Fit for this project: high. It uses existing DB-backed read models and improves workflow without adding providers.
- Risks: must avoid turning context into a trade signal.

### 2. Evidence Health Strip

- Seen in: current Operations Console, OpenBB refresh actions, Koyfin data coverage distinctions.
- User problem: users need to know whether context is fresh, stale, partial, or missing before trusting the view.
- Interaction shape: a compact strip above analysis tabs showing `OK / Due / Stale / Missing / Failed / Partial` counts and the next refresh action.
- Data required: existing `build_collection_ops_snapshot` plus current tab-specific coverage.
- Fit for this project: high. The project already has the vocabulary and run-history path.
- Risks: must link to Ingestion without making Overview own collection execution.

### 3. Calendar Quality Lane

- Seen in: TradingView Economic Calendar, current Overview Events.
- User problem: event rows have different reliability and urgency.
- Interaction shape: next event card, this-week count, source lane, validation lane, quality action lane, raw rows as fallback.
- Data required: `market_event_calendar`, source type, validation status, freshness, event status.
- Fit for this project: high. Current Events is already close; the improvement is visual hierarchy.
- Risks: earnings estimates must not look like official macro releases.

### 4. Breadth / Heatmap View

- Seen in: TradingView heatmaps and macro maps.
- User problem: top movers alone do not reveal whether the market move is broad or concentrated.
- Interaction shape: sector / industry heatmap, breadth summary, concentration summary, positive / negative participation.
- Data required: existing market movers, sector / industry leadership, market cap, return / volume metrics.
- Fit for this project: medium-high. Useful after cockpit and handoff improvements.
- Risks: Streamlit / Altair can do a first pass, but richer heatmaps may eventually need a frontend decision.

### 5. Linked Investigation Board

- Seen in: Koyfin dashboard widget linking, TradingView chart-adjacent event / macro context, current `Why It Moved`.
- User problem: selecting a mover should carry identity, movement, news / SEC / external clues, and source state together.
- Interaction shape: selected ticker drives compact identity header, movement context, metadata status, investigation lanes, and external links.
- Data required: existing session-only compact metadata; optional future DB retention only after policy approval.
- Fit for this project: medium. V1 is implemented; V2 depends on storage policy.
- Risks: automatic cause classification, AI summary, article body storage, and filing body parsing are out of current scope.

### 6. Source Catalog / Indicator Reference

- Seen in: FRED series-first model, Koyfin data overview.
- User problem: users need to know what each macro indicator means, where it comes from, how fresh it should be, and what it does not prove.
- Interaction shape: searchable reference / catalog with source, table, collector, loader, cadence, confidence, downstream surfaces, caveats.
- Data required: docs / source map; no new data source required.
- Fit for this project: high as documentation / Reference companion.
- Risks: if maintained poorly, it can drift from actual collectors and DB schema.

### 7. Custom Dashboard Presets

- Seen in: Koyfin My Dashboards, OpenBB Workspace dashboards.
- User problem: different research workflows want different layouts.
- Interaction shape: reusable preset layouts for pre-open, macro event week, sector rotation, data repair, or selected portfolio context.
- Data required: stable read models and possibly saved user preferences.
- Fit for this project: later. Current workflow clarity should come first.
- Risks: layout customization can create maintenance burden before the product taxonomy is stable.

## Patterns That Conflict With Current Boundaries

- Live broker trading, order tickets, account sync, or auto rebalance.
- Persistent push alerts that imply trading action.
- Automatic catalyst classification from news / filings.
- AI summaries that read article or filing bodies without a storage / source / retention policy.
- Direct provider / FRED fetch during Streamlit render.
- Treating sentiment, futures shock state, or macro thermometer as Practical Validation PASS / BLOCKER evidence.

## Patterns That Should Remain Internal / Ops Only

- Raw run-history tables.
- Provider failure artifacts and diagnostics.
- Manual bulk collection controls.
- DB schema / table repair details.
- Full raw provider responses.
- Historical debug outputs.

## Candidate Questions For Feature Opportunity

- Can `Overview Macro Context Cockpit V1` be built from existing read models only?
- Should `Data Health` become a priority-ranked action queue before adding new visualizations?
- Which macro indicators need a source catalog entry before being shown more prominently?
- Should `Candidate Ops` be removed, renamed, or demoted from Overview after the market context cockpit exists?
- Which future heatmap can be built safely in Streamlit, and which should wait for platform research?
