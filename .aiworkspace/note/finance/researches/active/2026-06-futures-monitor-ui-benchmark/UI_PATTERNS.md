# UI Patterns

Status: Draft
Last Updated: 2026-06-23

## Summary

Futures Monitor should become a compact market workbench:

```text
Context bar
  -> Market brief
  -> Weekly flow / evidence lane
  -> Linked watchlist + chart grid
  -> Evidence and diagnostics disclosures
```

The goal is not to add more cards. The goal is to make the first screen answer the user's market-context questions in order.

## Pattern Catalog

### 1. Persistent Watch Rail

- Seen in: TradingView, Koyfin, IBKR.
- User problem: large multi-select chips consume space and look like form input, not market monitoring.
- Interaction shape: left or top rail with group label, selected symbols, last state, small returns, one add/edit affordance.
- Data required: current selected symbols, state, 15m/60m moves, age.
- Fit for this project: High.
- Guideline: default mode shows compact rows; edit mode opens the existing multi-select.

### 2. Compact Context Bar

- Seen in: TradingView/Koyfin controls, Stripe dashboard action surfaces.
- User problem: controls currently appear as unrelated form blocks.
- Interaction shape: one horizontal bar with grouped segments: watch group, timeframe, candle, chart scope, refresh status/action.
- Data required: existing session controls and freshness state.
- Fit for this project: High.
- Guideline: control labels should be visible but compact; the refresh action should not open a large overlay by default.

### 3. Refresh Status Strip Instead Of Large Popover

- Seen in: Datadog/Grafana dashboard health patterns, Stripe important notifications.
- User problem: current refresh popover covers the market brief and feels like a modal.
- Interaction shape: small status pill plus split button. Expanded settings become a narrow inline tray below the bar.
- Data required: refresh mode, latest age, latest run status, manual/auto state.
- Fit for this project: High.
- Guideline: show `오래됨 · 591분 · 갱신 필요`; only expose manual/auto choice when the user opens settings.

### 4. Market Brief Hero

- Seen in: Toss Securities content-first UX, Stripe overview, Koyfin dashboard summaries.
- User problem: Macro Context reads as support cards plus paragraph.
- Interaction shape: headline, 1-2 sentence interpretation, confidence/source row, supporting/opposing evidence chips.
- Data required: macro scenario, summary sentence, evidence reading, score groups, validation/confidence.
- Fit for this project: High.
- Guideline: hero should answer `지금 시장은 어떤 상태인가?` before showing any cards.

### 5. Weekly Flow Comparison

- Seen in: market dashboards and observability trend panels.
- User problem: recent 1-week flow is currently repeated cards with no ranking.
- Interaction shape: primary driver lane + supporting/opposing columns + mini bars.
- Data required: existing `weekly_context` and score values.
- Fit for this project: High.
- Guideline: show `1주 흐름: 원자재/물가 하락이 가장 큼` then `오늘 해석과 같은 방향 / 다른 방향`.

### 6. Evidence Trail Before Raw Tables

- Seen in: Toss content insertion, Grafana annotations, observability drilldowns.
- User problem: raw evidence tables are hard to interpret.
- Interaction shape: first a readable evidence trail; raw tables live behind nested disclosure.
- Data required: existing evidence_reading, components, scores, symbols.
- Fit for this project: High.
- Guideline: evidence row must say `무엇`, `방향`, `왜 중요`, `현재 결론에 기여`.

### 7. Linked Chart Grid

- Seen in: TradingView/Koyfin/IBKR and Toss PC multi-chart updates.
- User problem: chart grid is detached from the market brief.
- Interaction shape: chart grid reads from selected group and common timeframe; optional selected-symbol focus.
- Data required: existing candles and symbol metrics.
- Fit for this project: Medium-high.
- Guideline: chart section header should say what question the chart answers, not repeat provider state.

### 8. Annotations For Refresh / Stale Periods

- Seen in: Grafana annotations.
- User problem: stale warnings are separated from charts.
- Interaction shape: a small marker or note near chart panel header showing latest collection / stale.
- Data required: latest candle time / age from existing snapshot.
- Fit for this project: Medium.
- Guideline: do not create an ops panel; annotate chart usability.

## Patterns That Conflict With Current Boundaries

- Order entry, chart trading, broker execution, live approval.
- AI stock recommendation or automatic trading signal wording.
- Full custom dashboard builder in the next slice.
- Any render-time provider fetch from UI.

## Patterns That Should Remain Internal/Ops Only

- Provider row counts and latest run payloads.
- Full failed job logs.
- Raw OHLCV table previews.
- Cache/session diagnostics.

## Candidate Questions For Feature Opportunity

- Can V1 be completed as a pure Streamlit/CSS rearrangement?
- Should watch rail and chart grid be a two-column layout or stacked sections?
- Can weekly context become a ranked lane without service changes?
- How much of the refresh menu should stay visible by default?

