# Sources

Access date: 2026-06-08

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `AGENTS.md` | Documented | Worktree scope, documentation rules, product-boundary rules, research bundle handling, verification expectations. |
| `.aiworkspace/note/finance/docs/INDEX.md` | Documented | Current docs map and active / completed state. |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Product pillars: DB-backed runtime, evidence-first, context-not-approval, no live trading. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | Current Overview / Market Context, Ingestion, Operations, and next decision candidates. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Ownership map for Overview, Ingestion, Futures, Sentiment, Data Health, Operations. |
| `.aiworkspace/note/finance/docs/architecture/SYSTEM_BOUNDARIES.md` | Documented | Layer ownership and product-surface boundaries. |
| `.aiworkspace/note/finance/docs/data/README.md` | Documented | DB tables, JSONL boundaries, data integrity rules. |
| `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` | Documented | Current Overview operation flow and expected results. |
| `app/web/overview_dashboard.py` | Observed | Overview tab layout and current UI surface shape. |
| `app/web/overview_dashboard_helpers.py` | Observed | DB-backed Overview helper read paths. |
| `app/jobs/overview_actions.py` | Observed | Approved Overview action facade for refresh / run-history boundary. |
| `app/web/ingestion_console.py` | Observed | Ingestion console for futures, sentiment, events, macro, provider, and diagnostics. |
| `app/web/operations_overview.py` | Observed | Operations Console portfolio / system data health model. |
| `.aiworkspace/note/finance/researches/active/2026-05-overview-market-intelligence/RECOMMENDATION.md` | Documented | Prior Overview market intelligence recommendation. |
| `.aiworkspace/note/finance/researches/active/2026-06-futures-market-monitoring/RECOMMENDATION.md` | Documented | Prior futures monitor recommendation. |
| `.aiworkspace/note/finance/researches/active/2026-06-operations-workspace-restructure/RECOMMENDATION.md` | Documented | Prior Operations restructure recommendation. |
| `.aiworkspace/note/finance/researches/active/2026-06-why-it-moved-benchmark/RECOMMENDATION.md` | Documented | Prior Why It Moved UX / boundary recommendation. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| Koyfin Market Dashboards: https://www.koyfin.com/features/market-dashboards/ | Claimed | Curated market / economics / yields / commodities / credit dashboard pattern. |
| Koyfin Data Overview: https://www.koyfin.com/help/data-overview/ | Documented | Data source coverage and live / delayed / EOD distinctions. |
| Koyfin My Dashboards: https://www.koyfin.com/help/mydashboards-myd/ | Documented | Custom dashboard widgets, watchlists, charts, tables, news, linked dashboard groups. |
| TradingView Features: https://www.tradingview.com/features/ | Claimed / Documented | Economic calendar, corporate events, macro maps / heatmap-style macro coverage. |
| TradingView Economic Calendar: https://www.tradingview.com/support/solutions/43000759911-economic-calendar-track-all-major-market-events/ | Documented | Date / region / category event filtering and embeddable calendar pattern. |
| TradingView Macro Maps: https://www.tradingview.com/support/solutions/43000764925-macro-maps-on-tradingview-explore-compare-track/ | Documented | Macro maps as global economic indicator visualization. |
| FRED API Overview: https://fred.stlouisfed.org/docs/api/fred/overview.html | Documented | API access to FRED / ALFRED by source, release, category, and series. |
| FRED Series Observations: https://fred.stlouisfed.org/docs/api/fred/series_observations.html | Documented | Series observations API, file formats, observation parameters, real-time / vintage-related fields. |
| FRED Dashboard Help: https://fredhelp.stlouisfed.org/fred/account/dashboard-features/add-a-graph-to-a-dashboard/ | Documented | Saved graph / dashboard pattern. |
| OpenBB Dashboard Docs: https://docs.openbb.co/workspace/analysts/dashboards | Documented | Dashboard widgets, layout, folders, refresh actions, sharing. |
| OpenBB Workspace Product: https://www.openbb.co/products/workspace | Claimed | Data visualization, multi-source dashboards, macro scenario planning, analyst workflows. |

## Source Notes

- Product pages are used as pattern evidence, not proof that this project should match their full feature scope.
- External service details can change; any implementation that depends on pricing, terms, or provider capability needs a fresh source check.
- No live trading or brokerage pattern from external products is adopted into this recommendation.
