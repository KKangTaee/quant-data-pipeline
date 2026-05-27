# Recommendation

## One-Line Recommendation

Build the Overview redesign in two slices: first DB-backed market movers and sector / industry leadership, then a read-only event calendar with FOMC first and earnings only after provider ingestion is chosen.

## Why This Direction

The first two requested features are already supported by local price/profile data. The third feature is feasible, but not all event types have the same source quality. FOMC has an official source and low risk. Earnings dates are vendor data and need a provider, API key, persistence, and source-confidence labels.

Important date note: on the 2026-05-28 workspace check, the raw latest daily price date was 2026-05-19, but that date had only one null price row. The effective usable market date was 2026-05-18.

## Feasibility Verdict

| Requested feature | Verdict | Reason |
| --- | --- | --- |
| Daily / weekly / monthly top movers from Coverage 1000/2000 | Feasible now | Existing US active stock profile and daily price DB are enough. Weekly/monthly can be derived from daily prices. |
| Monthly sector / industry Top N | Feasible now | Existing `sector`, `industry`, `market_cap`, and daily price rows support group return aggregation. |
| Market event calendar | Partially feasible | FOMC is feasible immediately. Earnings requires provider selection, API key handling, ingestion, persistence, and source labeling. |

## Recommended 1st Build Scope

### Step 1. Add service contract

```text
app/services/overview_market_intelligence.py
  build_market_movers_snapshot(universe_limit, period, top_n)
  build_group_leadership_snapshot(universe_limit, group_by, top_n)
  resolve_effective_market_dates(min_price_rows)
```

### Step 2. Wire Overview helper and UI

```text
app/web/overview_dashboard_helpers.py
app/web/overview_dashboard.py
```

Recommended tabs:

- `Market Movers`
- `Sector / Industry`
- `Events`
- `Candidate Ops`

The current candidate Top 3, funnel, next actions, and recent activity should move under `Candidate Ops`.

### Step 3. Test and verify

- Effective date selection ignores sparse/null latest dates.
- Daily, weekly, and monthly returns use daily price rows.
- Coverage gaps are displayed, not hidden.
- Sector / industry ranking tolerates missing profile fields.

## Recommended Next Phase After 1st Build

| Phase | Output | Why |
| --- | --- | --- |
| FOMC Events | Read-only FOMC rows in Events tab | Official source, low risk, useful market context. |
| Earnings Provider Decision | Provider/API choice note | Avoid building against an unstable or unlicensed source. |
| Earnings Ingestion | DB table, collector, loader, ingestion job | Keeps Overview aligned with architecture rules. |

## What Not To Do Yet

- Do not fetch earnings or Fed pages directly during Streamlit render.
- Do not remove existing candidate Overview content.
- Do not treat top movers as candidate recommendations.
- Do not add broker action, live approval, or rebalance behavior.

## Decision Rules

Proceed when:

- User approves the Overview tab structure.
- First implementation is scoped to DB-backed movers and sector/industry leadership.
- Event calendar is treated as next slice unless the user explicitly prioritizes it first.

## Final Recommendation

Start with `Market Movers` and `Sector / Industry` inside Overview. This gives the user immediate value with existing data and reveals freshness/coverage gaps clearly. Add `Events` as a placeholder tab with source requirements documented, then implement FOMC and earnings in separate follow-up slices.
