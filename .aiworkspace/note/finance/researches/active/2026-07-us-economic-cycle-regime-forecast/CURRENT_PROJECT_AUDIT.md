# Current Project Audit

Status: Complete
Last Updated: 2026-07-16

## Summary

`Workspace > Overview > Market Context` is a user-facing, DB-backed analysis surface. It currently renders one React valuation workbench with an internal `S&P 500 | 미국 개별주식` selector. The project already has a generic FRED collector and macro loader, but its default macro scope is limited to VIX, the 10Y–3M curve, and a Baa spread. It has no economic-cycle state model, one-/two-month transition forecast, or real-time vintage history.

The feature is feasible inside the existing architecture, but the correct first dependency is not a new chart. The current macro table overwrites revisions because its unique key is `(series_id, observation_date, source)`. A reliable historical simulation therefore requires a vintage-aware macro store or equivalent point-in-time snapshot contract before probabilities can be calibrated.

## Snapshot

- Surface: `Workspace > Overview > Market Context`
- Requested scope: U.S. economy, four phases, probabilistic now/+1M/+2M view
- Existing reusable base: FRED collector, macro loader, ingestion job, React Market Context component pattern
- Primary blocker: no revision-preserving macro vintage contract
- Research recommendation: hybrid factor + constrained transition model, cycle clock + regime ribbon

## Current Product Promise

- Overview is for market context and investigation, not trade approval or automated allocation.
- UI reads DB-backed service models; it does not fetch FRED or another provider during render.
- Source, freshness, partial coverage, and methodology limits stay visible.
- A cycle estimate may be called a model estimate, but not an official NBER determination.

## Current Workflow

1. `app/web/overview/page.py` routes the top-level `Market Context` tab.
2. `app/web/overview/market_context.py` renders the header and valuation surface.
3. `app/web/overview/market_context_helpers.py` loads a combined valuation read model.
4. `app/web/streamlit_components/market_context_valuation/` renders the `S&P 500 | 미국 개별주식` selector and analysis UI.
5. `finance/data/macro.py` can collect arbitrary FRED series, but defaults to `VIXCLS`, `T10Y3M`, and `BAA10Y`.
6. `finance/loaders/macro.py` exposes historical observations and latest-as-of snapshots from MySQL.

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Overview owns context and investigation, not a trade signal. |
| Roadmap | `.aiworkspace/note/finance/docs/ROADMAP.md` | Market Context is an active product surface and no new phase is committed without approval. |
| Project map | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Overview follows thin entrypoint, helper/read-model, component, and ingestion boundaries. |
| UI routing | `app/web/overview/page.py`, `app/web/overview/market_context.py` | Market Context currently has one valuation-oriented child surface. |
| Existing selector | `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx` | S&P 500 and U.S. stock selection currently lives inside the valuation component. |
| Macro collector | `finance/data/macro.py` | FRED collection and DB UPSERT infrastructure already exists and accepts arbitrary series IDs. |
| Macro loader | `finance/loaders/macro.py` | DB-backed historical and as-of snapshot reads already exist. |
| Macro schema | `finance/data/db/schema.py` | Revisions overwrite prior values; no vintage date is part of the unique key. |
| Ingestion job | `app/jobs/ingestion_jobs.py` | Collection already has an explicit job boundary suitable for extension. |

## Surface Classification

| Surface | User-facing / internal / mixed | Notes |
| --- | --- | --- |
| `Overview > Market Context` | User-facing | Correct destination for a readable cycle estimate, forecast, history, and evidence. |
| `Ingestion > FRED 시장환경` | Internal / ops | Correct owner for collection, refresh, source failures, and row-level diagnostics. |
| Economic-cycle method / backtest | Internal research engine | Must validate probabilities and vintages before the UI consumes them. |
| Data freshness / source details | Mixed | Compact cutoff and confidence belong in the product; raw jobs and row counts remain ops-only. |

## Strengths

- DB-only UI and bounded ingestion job boundaries already match the required architecture.
- The generic macro collector means most selected FRED series can be added without a provider rewrite.
- The macro loader already supports date-bounded history and as-of reads.
- Market Context already uses a responsive React component and explicit source/methodology copy.
- Existing project rules explicitly guard point-in-time correctness and non-signal semantics.

## Weaknesses

- The current macro table cannot reproduce what data were known at a past forecast date.
- Only three default risk-context series are configured; real activity, labor, demand, inflation, and leading breadth are absent.
- No phase taxonomy or probability calibration contract exists.
- The user study note mixes real-economy phases with asset-price regimes; gold, dollar, and rates can support interpretation but cannot define the economic cycle alone.
- The existing React package is named and structured around valuation; directly adding a large cycle model to it would blur domain ownership.
- Current macro freshness uses a single day threshold even though daily, weekly, monthly, and quarterly releases have different expected lags.

## Relevant Ownership Map

| Responsibility | Current / likely owner |
| --- | --- |
| Vintage-aware macro ingestion and schema | `finance/data/macro.py`, `finance/data/db/schema.py`, `app/jobs/ingestion_jobs.py` |
| Point-in-time macro loading | `finance/loaders/macro.py` or a dedicated economic-cycle loader |
| Phase and forecast engine | New focused service under `app/services/overview/` or a finance domain module with a thin overview read model |
| Market Context routing | `app/web/overview/market_context.py`, `app/web/overview/market_context_helpers.py` |
| Cycle visualization | New isolated Streamlit React component instead of adding cycle logic to `MarketContextValuation.tsx` |
| Existing valuation | Preserve current valuation service and component behavior |

## Data And Validation Risks

- Final revised macro history creates look-ahead bias unless ALFRED or stored collection vintages are used.
- Release calendars are ragged: a July screen may combine June labor data, May income/output data, and daily July financial data.
- U.S. recessions are rare, so a complex four-class model can look accurate while learning very few transition episodes.
- NBER labels are retrospective and two-state; recovery/expansion/slowdown need an explicit operational definition.
- OECD CLI levels and directions can be revised because the trend/filter uses the full series.
- A forecast probability needs rolling-origin calibration metrics, not only in-sample classification accuracy.

## Product Boundaries

- Keep Final Review and Selected Portfolio Dashboard as decision support, not live approval.
- Keep the cycle feature as macro context; do not output buy/sell or portfolio weights.
- Keep asset prices, gold, dollar, and rates as market-implied overlays rather than the primary phase label.
- Never call a real-time model state an official NBER recession declaration.
- Do not turn research output into roadmap commitment without user approval.

## Audit Conclusion

The product should add an isolated `경제 사이클` Market Context child surface, backed by a vintage-aware data and model pipeline. The first implementation slice must establish phase semantics, source cadence, and point-in-time evaluation. UI-only delivery would be visually impressive but methodologically invalid.
