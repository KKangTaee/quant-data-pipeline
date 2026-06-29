# Benchmarks

Status: Draft
Last Updated: 2026-06-23

## Research Question

Futures Monitor를 “한글화된 Streamlit 화면”이 아니라 “읽는 순서가 분명한 금융 모니터링 워크스페이스”로 만들기 위해 어떤 UI 패턴을 참고해야 하는가?

## Selection Criteria

- Watchlist / chart workspace를 잘 다루는 제품.
- Data freshness / dashboard state / drilldown을 잘 다루는 제품.
- 사용자 행동을 한 화면에서 줄이는 command/action surface를 가진 제품.
- 한국 사용자에게 친숙한 쉽고 직관적인 투자 UI 사례.

## Benchmark Matrix

| Product Or Class | Category | Target User | Relevant Workflow | Evidence Label | Applicability |
|---|---|---|---|---|---|
| TradingView / Koyfin | Market monitor / chart workspace | Active investor, analyst | Watchlist -> chart -> metrics/news/detail | Documented / Claimed | High |
| IBKR TWS Mosaic / professional WTS | Professional trading workspace | Active trader | Linked watchlists, scanners, charts, news in one workspace | Documented | Medium |
| Datadog / Grafana | Observability dashboard | Operator / engineer | Status overview -> anomaly -> correlated panel/event | Documented | High for data freshness |
| Stripe / Linear | B2B SaaS dashboard / command workflow | Operator / team user | Overview, important notifications, filters, command menu | Documented | Medium |
| Toss Securities | Retail investing UX | Retail investor | Easy exploration, watchlist, plain-language context, simplified MTS | Documented / Claimed | High for Korean UX language |

## Product Notes

### TradingView / Koyfin

- Category: Market monitor and chart analysis workspace.
- Main workflow: watchlist and chart are close together. Users track a focused symbol set, switch symbols, customize visible metrics, and read related details without leaving the workspace.
- UI/workflow patterns:
  - Watchlist as a persistent context rail, not a large multi-select blob.
  - Symbols can be grouped into sections by market / sector / mood.
  - Table/row view and metric customization support dense scanning.
  - Dashboards allow multiple watchlists and custom views across asset classes.
- Strong ideas for this project:
  - Replace the large selected-symbol chip block with a compact watchlist rail/table.
  - Let selected group drive linked macro brief and chart grid.
  - Make chart controls compact and persistent, not scattered.
- Ideas to avoid:
  - Full professional charting overload.
  - Too many customizable columns in V1.
- Evidence label: Documented / Claimed.

### IBKR TWS Mosaic / Professional Trading Workspace

- Category: Professional trading workspace.
- Main workflow: monitor panel, watchlists, scanners, charts, quote details, news, and order widgets are arranged in a customizable workspace.
- UI/workflow patterns:
  - Dense but structured workbench.
  - Linked windows / color grouping synchronize symbol context.
  - Scanners use gradients, lines, bars to make trends visible at a glance.
  - Multiple panes preserve context while reducing navigation.
- Strong ideas for this project:
  - Borrow “linked context” without borrowing trading/order semantics.
  - Use a left watch rail and right chart/evidence panes that react to the same selected group.
  - Use compact bars/heat lanes instead of repeated cards for macro scores.
- Ideas to avoid:
  - Order entry, order monitor, trade execution.
  - Highly customizable window layout; too much complexity for Streamlit V1.
- Evidence label: Documented.

### Datadog / Grafana

- Category: Observability dashboard.
- Main workflow: dashboard widgets summarize health, anomalies, logs/statuses, then users drill into panels and annotations.
- UI/workflow patterns:
  - Widgets are building blocks with clear ownership.
  - Template variables / filters change the whole dashboard context.
  - Annotations explain why a time-series moved at a point in time.
  - Dashboard state focuses on “is this usable / stale / anomalous?” before raw data.
- Strong ideas for this project:
  - Treat data freshness as a small status strip, not a large popover.
  - Add event/refresh annotations on charts for latest collection and stale ranges.
  - Separate overview status, chart panels, and raw evidence disclosures.
- Ideas to avoid:
  - Ops-only run/job panels as a main product surface.
  - Generic dashboard widgets without market interpretation.
- Evidence label: Documented.

### Stripe / Linear

- Category: B2B SaaS dashboard and command workflow.
- Main workflow: home overview surfaces analytics plus important notifications; filters/exports/actions are discoverable but do not dominate the page. Linear-style command surfaces prioritize quick navigation/actions.
- UI/workflow patterns:
  - Overview first, detail and actions second.
  - Important notifications sit near the top but stay compact.
  - Configurable widgets are useful when they preserve user workflow.
  - Command/action menus should be small, predictable, and not obscure primary content.
- Strong ideas for this project:
  - Replace refresh popover with compact split action + inline status.
  - Use a right-side or inline action tray only when the user asks for refresh settings.
  - Keep raw diagnostics behind disclosure.
- Ideas to avoid:
  - Over-generic SaaS cards that feel disconnected from market analysis.
- Evidence label: Documented.

### Toss Securities

- Category: Korean retail investing UX.
- Main workflow: lower investment complexity by removing unnecessary indicators, using plain language, watchlist and discovery surfaces, and content at the moment users need explanation.
- UI/workflow patterns:
  - Simplify aggressively: ask whether each visible element helps the user decide.
  - Plain-language explanation sits near the moment of need.
  - Watchlist is not assumed; the product teaches why it matters.
  - Retail research content is rewritten for easy reading and distributed at relevant paths.
  - Recent PC updates show multi-chart and customized info tabs as a way to reduce movement between screens.
- Strong ideas for this project:
  - Make macro interpretation sound like a short market brief, not a data dump.
  - Explain score chips in plain Korean and avoid financial jargon unless needed.
  - Build one clear primary action per state: `갱신 필요`, `차트 확인`, `근거 보기`.
- Ideas to avoid:
  - Oversimplifying away useful quant evidence.
  - Any wording that implies recommendation, signal, or investment advice.
- Evidence label: Documented / Claimed.

## Cross-Product Patterns

1. **Persistent context beats large selectors.**
   - Watchlist/workspace products keep the selected universe visible but compact.

2. **Overview owns status; details own evidence.**
   - Dashboards show compact health/status first, then drilldowns.

3. **Charts need context linking.**
   - A chart grid should know what group, timeframe, and macro question it answers.

4. **Plain language is not just translation.**
   - Toss-style UX reframes technical information around user questions.

5. **Actions should not cover the main reading path.**
   - Refresh/settings popovers should be narrow and contextual or move into an inline tray.

## Architecture / Platform Implications

- Keep DB-backed read model and Streamlit-free service boundaries unchanged.
- Most immediate changes are in `app/web/overview_dashboard.py` and `app/web/overview_ui_components.py`.
- If future implementation needs richer chart layout / interaction, consider frontend platform research separately; not required for the next Streamlit slice.

## Open Questions

- Should Futures Monitor prioritize macro brief above chart grid on desktop, or use a two-column brief/chart split?
- Should the watch rail replace multi-select chips entirely, or should chips remain as the edit mode only?
- Should score chips become a compact heat lane with explanations, or stay as badges for continuity?

