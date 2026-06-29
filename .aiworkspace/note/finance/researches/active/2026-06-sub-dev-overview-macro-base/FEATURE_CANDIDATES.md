# Feature Candidates

Status: Active
Last Updated: 2026-06-08

Scoring: 1 low, 5 high.

Priority formula reference: `impact + fit + confidence - effort - risk`, adjusted for dependency and boundary clarity.

## Candidate Matrix

| Bucket | Candidate | Impact | Effort | Risk | Confidence | Fit | Score | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Now | Overview Macro Context Cockpit V1 | 5 | 3 | 2 | 4 | 5 | 9 | First implementation candidate |
| Now | Data Health -> Ingestion Action Queue | 4 | 3 | 2 | 4 | 5 | 8 | Second implementation candidate |
| Now | Macro Indicator / Source Confidence Catalog | 4 | 2 | 1 | 4 | 5 | 10 | Can run in parallel with UI planning |
| Next | Market Breadth / Heatmap Visualization | 4 | 3 | 2 | 4 | 4 | 7 | Build after cockpit clarifies hierarchy |
| Next | Events Quality / Macro Week View | 3 | 2 | 2 | 4 | 4 | 7 | Good follow-up if event data is stale-visible |
| Next | Candidate Ops Demotion / Overview IA Cleanup | 3 | 2 | 2 | 4 | 4 | 7 | Needs user approval because IA changes workflow |
| Later | Why It Moved V2 Compact Metadata Storage Policy | 4 | 4 | 4 | 3 | 4 | 3 | Research / policy first, then build |
| Later | Futures Provider Hardening Decision | 4 | 4 | 4 | 3 | 4 | 3 | Needs provider / cost / source-quality decision |
| Later | Custom Overview Dashboard Presets | 3 | 4 | 3 | 3 | 3 | -1 | Wait until surface taxonomy stabilizes |

## Now. Overview Macro Context Cockpit V1

Problem:

- Overview has useful tabs, but the market story is fragmented across futures, sentiment, movers, events, and data health.

Expected workflow change:

- User opens Overview and first sees a compact market context cockpit: market pressure, breadth, sentiment, upcoming event risk, freshness / data confidence, and next action.
- Deep tabs remain available; no new data source or provider is introduced.

Evidence:

- Audit: Overview currently renders seven top-level tabs and has DB-backed read models for each major surface.
- Benchmark: Koyfin / OpenBB patterns favor curated summary dashboards before deep exploration.

Likely owner area:

- `app/web/overview_dashboard.py`
- `app/web/overview_dashboard_helpers.py`
- `app/services/overview_market_intelligence.py`
- `app/services/futures_macro_thermometer.py`
- `app/web/overview_ui_components.py`

Data / storage boundary:

- Read-only from existing DB-backed service models.
- No registry / saved JSONL writes.
- No provider fetch during render.

Success criteria:

- Overview first screen can answer: "시장 압력은 어떤가?", "데이터는 믿을 만큼 fresh한가?", "이번 주 이벤트 risk는 무엇인가?", "어느 deep tab을 봐야 하나?"
- Sentiment / futures / events remain context-only.
- Existing tabs still work.

## Now. Data Health -> Ingestion Action Queue

Problem:

- Data Health shows statuses, but the user still has to know which Ingestion job fixes each stale / missing / failed target.

Expected workflow change:

- Data Health rows are priority-ranked by freshness / failure / downstream impact.
- Each row has an explicit next action and target Ingestion area.
- Optional future work can add session prefill, but first pass can be read-only guidance.

Evidence:

- Audit: `build_collection_ops_snapshot` already has status vocabulary and run-history context.
- Benchmark: OpenBB dashboard docs emphasize refresh actions; Koyfin distinguishes data coverage / timing by source.

Likely owner area:

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `app/web/ingestion_console.py`
- `app/jobs/overview_actions.py`

Data / storage boundary:

- Use existing run history and DB freshness.
- Ingestion remains the owner of collection execution.

Success criteria:

- User can identify top 3 stale / missing data targets and the exact collection surface to run.
- Partial / failed results remain visibly different from success.

## Now. Macro Indicator / Source Confidence Catalog

Problem:

- Macro / sentiment / futures indicators are useful but can be over-interpreted if source, cadence, coverage, and non-signal boundaries are not explained close to the product.

Expected workflow change:

- A durable catalog or Reference companion explains each Overview macro indicator: source, table, collector, loader, freshness threshold, UI surfaces, caveats, and downstream use.

Evidence:

- Audit: Overview has futures, sentiment, events, and macro evidence spread across UI and services.
- Benchmark: FRED's series-first model reinforces source / series / observation semantics.

Likely owner area:

- `.aiworkspace/note/finance/docs/`
- `Reference > Guides` if implemented as UI companion
- Possible `app/services/reference_contextual_help.py` alignment later

Data / storage boundary:

- Documentation / reference only unless a future UI companion is approved.

Success criteria:

- Future developers can add or modify macro indicators without guessing source semantics.
- Users can see that context is not approval or signal.

## Next. Market Breadth / Heatmap Visualization

Problem:

- Market Movers and Sector / Industry rankings show leaders, but not enough distribution / breadth at a glance.

Expected workflow change:

- User can distinguish broad market participation from a few concentrated leaders.

Likely owner area:

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `app/web/overview_ui_components.py`

Success criteria:

- Heatmap / breadth view is derived from existing DB-backed rows.
- Negative, positive, concentration, and missing-data states are readable.

## Next. Events Quality / Macro Week View

Problem:

- Events already has agenda / calendar / quality / raw tabs, but macro weeks can be summarized more directly.

Expected workflow change:

- User sees upcoming FOMC / CPI / PPI / Employment / GDP / earnings estimate clusters with source quality and freshness.

Likely owner area:

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `app/jobs/overview_actions.py`

Success criteria:

- Official macro releases and provider-estimated earnings are visually distinct.
- No event is treated as a prediction or trading instruction.

## Next. Candidate Ops Demotion / Overview IA Cleanup

Problem:

- `Candidate Ops` inside Overview keeps candidate/backtest operational content in a market context workspace.

Expected workflow change:

- Overview becomes cleaner as a market context / data health surface.
- Candidate-oriented content moves, demotes, or is renamed only after user approval.

Likely owner area:

- `app/web/overview_dashboard.py`
- Navigation / flow docs after approval

Success criteria:

- Overview identity is clearer without losing access to useful legacy context.

## Later. Why It Moved V2 Compact Metadata Storage Policy

Problem:

- Session-only metadata is safe but not replayable.

Needed decision before build:

- Define DB schema, retention, freshness, provider throttling, replay semantics, and source terms.

Parking risk:

- Body collection, AI summary, and automatic cause classification remain out of scope until explicitly approved.

## Later. Futures Provider Hardening Decision

Problem:

- yfinance futures are useful for pilot context but not official exchange-grade data.

Needed decision before build:

- Decide whether CME / paid provider / KRX source quality is worth cost and complexity.

Parking risk:

- Do not promise real-time futures reliability from free provider data.

## Parking Lot

- Broker/account integration.
- Auto rebalance or order generation.
- Persistent push alerts that imply investment action.
- AI catalyst classifier from article / filing bodies.
- Full widgetized dashboard builder before product taxonomy stabilizes.
- Frontend migration only for Overview polish before the broader UI platform decision is approved.
