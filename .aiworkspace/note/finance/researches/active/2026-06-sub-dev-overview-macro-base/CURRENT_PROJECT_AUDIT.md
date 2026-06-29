# Current Project Audit

Status: Active
Last Updated: 2026-06-08

## Summary

`sub-dev` should be treated as the product-direction and implementation branch for `Workspace > Overview`, `Workspace > Ingestion`, and the supporting `Operations` data / status surfaces. Its current best use is not core backtest validation or future monitoring governance. It should audit market context, macro indicators, source freshness, collection workflows, and visualization gaps, then hand approved build scopes to separate implementation sessions.

The current product is already strong as a DB-backed market context workspace. The next weakness is not lack of panels; it is that macro context, market movement, event risk, sentiment, and data freshness are split across tabs without one summary-first "what should I look at now?" cockpit.

## Snapshot

Current state: Overview has broad market context coverage and clear collection boundaries, but needs a summary-first cockpit and stronger Overview -> Ingestion handoff before adding more data sources.

## Current Product Promise

The durable product direction says this project is a quant research workspace where data collection, market context, backtest candidates, investability validation, final selection, and read-only monitoring are connected. `Overview` is explicitly context / investigation, not a trade signal or approval stage. Macro / sentiment / futures evidence must stay source-visible and freshness-visible.

## Implemented Overview / Ingestion / Operations Capabilities

| Area | Implemented capability | Evidence |
| --- | --- | --- |
| Overview top-level tabs | `Market Movers`, `Futures Monitor`, `Sentiment`, `Sector / Industry`, `Events`, `Data Health`, `Candidate Ops` are rendered in one Streamlit surface. | `app/web/overview_dashboard.py:5517` |
| DB-backed read models | Market movers, sector / industry, event calendar, sentiment, and data health are loaded through helpers that call service read models. | `app/web/overview_dashboard_helpers.py:365` |
| Bounded Overview refresh | Overview refresh actions go through `app/jobs/overview_actions.py`, which wraps ingestion jobs and run history. | `app/jobs/overview_actions.py:23` |
| Futures context | Futures Monitor reads stored futures OHLCV and supports manual / auto refresh through bounded yfinance pilot collection. | `app/jobs/overview_actions.py:92`, `app/web/ingestion_console.py:2790` |
| Sentiment context | CNN Fear & Greed / AAII rows are collected into `finance_meta.macro_series_observation` and displayed as context. | `app/web/ingestion_console.py:2882` |
| Event context | FOMC, macro release, and earnings calendar collection are available through Ingestion and Overview refresh paths. | `app/web/ingestion_console.py:3130` |
| Operations entry | Operations Console summarizes Portfolio Monitoring and System / Data Health as the primary Operations lanes. | `app/web/operations_overview.py:580`, `app/web/operations_overview.py:868` |

## Surface Role Classification

| Surface | Role | Notes |
| --- | --- | --- |
| `Workspace > Overview > Market Movers` | User-facing product surface | Good scan surface for returns, volume, sector pulse, and manual `Why It Moved` investigation. |
| `Workspace > Overview > Futures Monitor` | User-facing market context surface | Useful pre-open / macro shock monitor, but provider caveat is important because yfinance futures are a pilot source. |
| `Workspace > Overview > Sentiment` | User-facing context surface | Shows market mood and data confidence, but should remain explicitly non-signal. |
| `Workspace > Overview > Sector / Industry` | User-facing analysis surface | Good breadth / leadership view; could become a heatmap / breadth dashboard. |
| `Workspace > Overview > Events` | Mixed product and ops surface | Event agenda is user-facing; raw / quality tabs are closer to ops diagnostics. |
| `Workspace > Overview > Data Health` | Mixed ops diagnostic | Valuable but should become more action-prioritized and connected to Ingestion. |
| `Workspace > Overview > Candidate Ops` | Transitional / mixed | It keeps legacy candidate-oriented dashboard content inside Overview; this weakens the market-context identity. |
| `Workspace > Ingestion` | Internal / ops console | Correctly owns external source collection and DB writes. It is intentionally control-heavy. |
| `Operations > Operations Console` | User-facing operations summary | Portfolio-first status and evidence health are aligned with the current product boundary. |
| `Operations > System / Data Health` | Internal / ops console | Best kept as diagnostics / repair / run-health surface. |

## Strengths

- The architecture boundary is healthy: UI reads DB-backed service models, and Overview refresh actions use an explicit facade instead of direct provider fetches.
- The product already covers the core market context stack: movers, sector / industry leadership, futures, sentiment, calendar events, and collection health.
- Source and freshness are not hidden. Partial / stale / missing states are part of the visible product language.
- The system preserves context-only boundaries: sentiment, futures thermometer, and `Why It Moved` are not treated as PASS / BLOCKER / trading signals.
- Ingestion and Overview are connected through shared data targets and run history, which gives a good base for action-prioritized data health.
- Operations has been narrowed to Portfolio Monitoring and System / Data Health, which reduces workflow confusion compared with older archive-heavy operations screens.

## Weaknesses

- Overview lacks a summary-first macro cockpit. The user must visit separate tabs to connect futures pressure, sentiment, upcoming macro events, market breadth, and stale data.
- Overview top caption still reads like a broad `Finance Console`, and `Candidate Ops` keeps candidate/backtest-oriented content inside the market context workspace.
- Data Health is status-rich but not yet priority-rich. It shows missing / stale / failed states, but the next refresh action is not yet a strong guided workflow.
- Ingestion is accurate but dense. It is useful for an operator, yet the handoff from an Overview problem to the exact Ingestion job can be made more ergonomic.
- Macro indicators do not yet have a durable in-product catalog explaining source, cadence, interpretation, freshness threshold, downstream surfaces, and "not a signal" limits.
- Existing visualizations are functional, but market breadth / heatmap / linked macro-event context is not yet as scan-first as comparable market dashboards.
- `overview_dashboard.py` is a very large file. Future changes risk UI complexity unless new summary panels and chart helpers are kept small and service-backed.
- `Why It Moved` is currently session-only by design. That is safe, but it means repeated investigation cannot be replayed unless a later storage policy is approved.

## Data And Validation Risks

- yfinance futures can be delayed, sparse, unavailable for some symbols, and not exchange-grade. It must stay labeled as pilot context.
- FRED / official macro series are good source candidates, but real-time / vintage / release-date semantics matter if they are ever used beyond context.
- Earnings estimates are provider estimates even when cross-checked; they should not be presented like official macro releases.
- Current listing snapshots, lifecycle observations, sentiment rows, and futures shock states are context or partial evidence, not survivorship or investment approval proof.
- `NOT_RUN`, `Missing`, `Partial`, `Stale`, and `Failed` states should remain visually distinct from successful evidence.

## Benchmark Questions

- How can Overview become a one-screen market pulse without becoming an investment-signal dashboard?
- Which market context views should be summary-first, and which should remain deep-dive tabs?
- Can Data Health become an action queue that points into Ingestion without letting Overview own data collection?
- What source catalog / glossary would prevent users from over-trusting macro context?
- Which visual patterns are worth building in Streamlit, and which should wait for a future API + richer frontend decision?

## Audit Conclusion

The strongest first development candidate is an `Overview Macro Context Cockpit V1`: a summary-first panel that synthesizes existing DB-backed futures, sentiment, events, breadth, movers, and data health into a market context read model. It should not add new providers, new registry writes, or trade signals. The second candidate is an Overview Data Health -> Ingestion handoff pass that turns stale / missing / failed status into a clear next collection action.
