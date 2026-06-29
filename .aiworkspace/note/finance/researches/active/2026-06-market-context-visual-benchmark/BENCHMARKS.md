# Benchmarks

Status: Draft
Last Updated: 2026-06-15

## Research Question

How should `Overview > Market Context` become more visual without becoming another card stack?

## Selection Criteria

This benchmark compares finance products that expose market context through dashboards, heatmaps, calendars, linked widgets, and professional terminal-style monitoring surfaces.

## Benchmark Matrix

| Product Or Framework | Category | Target User | Relevant Workflow | Evidence Label | Applicability |
|---|---|---|---|---|---|
| Koyfin Market / Custom Dashboards | Market dashboard | Investor / analyst | curated all-market screen, custom watchlists, tables, charts, news | Documented / Claimed | High for compact market brief + linked rows |
| TradingView Heatmaps + Economic Calendar | Visual market tools | Trader / investor | heatmap leaders/laggards, event calendar, drill-in | Documented / Observed | High for heatmap/timeline option |
| OpenBB Workspace | Analyst workspace | Analyst / developer | drag-drop widgets, parameter-linked tables/charts | Documented | Medium-high for linked evidence panel model |
| Bloomberg Terminal Launchpad | Professional terminal workspace | Institutional professional | customized monitors, alerts, charts, news | Claimed / Documented | Medium for dense monitor/tape inspiration |

## Product Notes

### Koyfin

- Category: Market dashboards and custom dashboard workspace.
- Target user: Investor / analyst who wants multi-asset market context.
- Main workflow: curated dashboards for broad market view; custom dashboards with watchlists, charts, news, and data tables.
- Relevant UI/workflow pattern: dense comparative dashboard, bespoke data table, saved asset-class views.
- Strong idea for this project: use a `market brief tape` rather than nested cards; keep many facts on one screen with row hierarchy.
- Ideas to avoid: fully user-customizable dashboard presets before the Overview taxonomy stabilizes.
- Evidence label: Documented / Claimed.
- Evidence limits: official marketing/help pages show capabilities, not a full interactive inspection.
- Sources: Koyfin custom dashboards, Koyfin market dashboards, Koyfin dashboard grouping.

### TradingView

- Category: Visual market tools.
- Target user: Trader / investor scanning leaders, laggards, events.
- Main workflow: market summary, heatmaps, economic calendar, charts.
- Relevant UI/workflow pattern: heatmap uses cell size for relative importance and color for performance; economic calendar provides event time, country, importance, event, actual / forecast / prior, and drill-in actions.
- Strong idea for this project: heatmap + timeline can make market context genuinely visual without card stacks.
- Ideas to avoid: visual intensity that implies signals or forecast confidence beyond local data coverage.
- Evidence label: Documented / Observed.
- Evidence limits: source evidence is official docs/home page; exact current app UI may vary by logged-in state.
- Sources: TradingView heatmap docs, economic calendar docs, homepage market summary.

### OpenBB Workspace

- Category: Analyst dashboard workspace.
- Target user: Analyst / developer who assembles internal and external data views.
- Main workflow: arrange widgets into workflow-specific dashboards; link parameters across widgets; tables can sort/filter and show sparklines/hover cards.
- Relevant UI/workflow pattern: widgets are linked by context, not merely grouped visually.
- Strong idea for this project: if a Market Context item is selected, related evidence rows / event / sentiment / data state can synchronize without being visually nested in one card.
- Ideas to avoid: full drag-drop customization before Streamlit view hierarchy is cleaner.
- Evidence label: Documented.
- Evidence limits: docs describe product behavior; not all widget visuals map directly to Streamlit.
- Sources: OpenBB dashboard docs, interacting with data docs.

### Bloomberg Terminal Launchpad

- Category: Professional terminal workspace.
- Target user: Institutional finance professional.
- Main workflow: customized workspace with security monitors, alerts, charts, news.
- Relevant UI/workflow pattern: dense monitors and linked terminal panels; not card-first.
- Strong idea for this project: status strips and monitor rows can be more finance-native than large cards.
- Ideas to avoid: real-time alerting or trade-action affordances.
- Evidence label: Claimed / Documented.
- Evidence limits: public product page is high-level and not a full UI spec.
- Sources: Bloomberg Terminal product page.

## Cross-Product Patterns

- Card grids are not the default finance-native answer. Dense monitors, tables, heatmaps, timelines, chart-adjacent context, and linked panels are more common.
- Visual hierarchy usually comes from spatial grouping, row density, color encoding, and drill-in, not from wrapping every concept in a separate card.
- Provenance and freshness should be visible, but often as small status tags, side rails, hover/detail rows, or collapsed evidence panes.
- Customization exists in mature products, but only after the core workflow taxonomy is stable.

## Architecture / Platform Implications

- A first pass can stay in Streamlit if we choose row/tape or narrative/rail.
- Heatmap/timeline is possible in Streamlit but will need stricter responsive QA and possibly charting helper boundaries.
- Full widget linking / customization points toward future API + frontend research, not this immediate task.

## Open Questions

- Should the next implementation optimize for fastest reading, most visual scanning, or research-note clarity?
- Should heatmap become the primary first impression, or remain a secondary deep visual under a textual brief?
