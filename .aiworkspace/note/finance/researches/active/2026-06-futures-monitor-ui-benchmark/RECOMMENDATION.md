# Recommendation

Status: Draft
Last Updated: 2026-06-23

## Recommended Direction

Proceed with **Futures Workbench Layout V1** as the next approved implementation slice, not another copy/text polish pass.

The goal is to redesign Futures Monitor around this reading flow:

```text
Compact context bar
  -> Market brief hero
  -> Weekly flow and evidence lane
  -> Linked watchlist / chart workspace
  -> Evidence and diagnostics disclosures
```

## Decision Scope

- Immediate next build:
  - Streamlit/CSS layout redesign using existing read models only.
  - Refresh status strip and market brief hero.
  - Weekly flow lane using existing `weekly_context`.
- Needs human approval before execution:
  - Replacing the current multiselect chip block with a watch rail as default.
  - Any mobile-specific layout pass beyond basic responsive checks.
- Longer roadmap option:
  - Rich linked chart workspace or non-Streamlit frontend.
- Not approved / parking lot:
  - Live trading, broker order, recommendation signal, auto refresh daemon changes, provider/schema changes.

## Why This Direction

The current page problem is not missing data. It is a weak visual hierarchy:

- Controls look like form inputs.
- Refresh settings cover the content.
- Macro context does not yet look like a market brief.
- Weekly flow and chart grid do not form a single monitoring workflow.

The benchmarks point to a common answer: keep context persistent, make status compact, make the primary interpretation prominent, and push raw evidence into drilldown.

## What To Build First

### 1. Context Bar

- One row: watch group, symbol count, timeframe, candle interval, chart scope.
- Right edge: data state pill + primary refresh action.
- Expanded refresh settings: small inline tray below the bar, not a large overlay.

### 2. Market Brief Hero

- Large statement: `혼재된 매크로 흐름`.
- One sentence: why.
- Compact support row: confidence, validation, similar episodes, data basis.
- Evidence chips: show support/opposition, not just raw scores.

### 3. Weekly Flow Lane

- Top line: dominant 1-week driver.
- Two columns: supports today's interpretation / conflicts or tempers it.
- Small bar or strength lane instead of repeated equal cards.

### 4. Linked Chart Workspace

- Chart section begins with `이 차트에서 확인할 것`.
- Optional left watch rail if feasible in V1.
- Chart cards keep symbol-level state only.

## Pilot Scope

- Keep all computation unchanged.
- Keep existing controls semantically unchanged.
- Keep diagnostics and raw data disclosures.
- Use Browser QA screenshot as primary visual acceptance.
- Add helper tests for new market brief / weekly lane display contracts.

## What To Defer

- Full custom chart interactions.
- Drag-and-drop dashboard.
- Advanced symbol grouping customization.
- AI narrative beyond existing deterministic summary.
- Any trade/order semantics.

## Decision Checkpoint

Before implementation, approve one of these approaches:

1. **Recommended: Workbench redesign in current Streamlit page.**
   - Fastest useful improvement, lowest data risk.
2. **Conservative: only refresh strip + Macro hero redesign.**
   - Lower effort, but chart/watchlist still feels prototype-like.
3. **Strategic: plan a React/Next.js frontend for Overview.**
   - Better long-term UI potential, but too large for this immediate complaint.

## Required Decisions

- Should the next implementation include the watch rail in V1, or defer it to V2?
- Should the weekly lane be visually compact or remain card-based with improved ranking?
- Should refresh auto/manual controls be inline tray or right-side drawer?

## Proposed Next Handoff

If approved, open a task:

```text
.aiworkspace/note/finance/tasks/active/futures-monitor-workbench-layout-v1-20260623/
```

Suggested stages:

1. Contract tests for context bar / brief / weekly lane.
2. Context bar and refresh strip.
3. Market brief hero.
4. Weekly flow lane.
5. Chart workspace alignment and Browser QA.

## Evidence Summary

- TradingView/Koyfin support persistent watchlist + customizable dashboard/workspace patterns.
- IBKR Mosaic supports dense linked workspace patterns, but order/trading semantics are out of scope.
- Datadog/Grafana support compact status widgets and annotation/drilldown patterns.
- Stripe/Linear support overview-first and compact action/menu discipline.
- Toss Securities supports plain-language, simplified, investor-facing explanation and aggressive removal of non-essential complexity.

## Risks And Unknowns

- Streamlit can limit precise layout; some visual polish may need CSS compromises.
- Too much simplification can hide quantitative evidence; disclosures must remain available.
- If the next pass still only rearranges existing cards, it will not solve the user's complaint.

