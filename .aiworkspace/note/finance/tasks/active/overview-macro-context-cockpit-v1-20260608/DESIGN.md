# Overview Macro Context Cockpit V1 Design

Status: Active
Created: 2026-06-08

## Design Summary

Cockpit V1 is a summary band at the top of `Workspace > Overview`.
It synthesizes existing Overview snapshots into six compact context cards plus a suggested deep-tab lane.
The model is read-only and context-only.

## Data Flow

```text
Existing DB-backed read models
  -> build_overview_macro_context_cockpit(...)
  -> load_overview_macro_context_cockpit()
  -> render_macro_context_cockpit(...)
  -> Workspace > Overview top band
```

The service builder accepts snapshot dictionaries so focused tests can cover behavior without DB access.
The default loader may call existing snapshot builders, but it does not add a provider fetch, schema change, registry write, or saved setup write.

## Cockpit Sections

| Section | Source | Purpose |
| --- | --- | --- |
| Market Movement | Market Movers snapshot | Show top mover and whether movement data is available / stale. |
| Breadth / Concentration | Sector leadership snapshot | Distinguish broad participation from concentrated sector leadership. |
| Futures Background | Futures macro thermometer snapshot | Summarize risk-on / risk-off / rate pressure / safe-haven context. |
| Sentiment Backdrop | CNN Fear & Greed / AAII sentiment snapshot | Show market mood as context only. |
| Near Events | Event calendar snapshot | Surface nearby FOMC / macro / earnings events. |
| Data Confidence | Collection ops snapshot | Show fresh / due / stale / partial / missing / failed counts. |

## Rendering

The Streamlit page renders the cockpit before the existing tabs.
Deep tabs remain unchanged.
The cockpit uses compact cards, status chips, and short next-check items rather than large marketing-style hero content.

## Boundary Guardrails

- No direct provider / FRED / crawler imports in `app/web/overview_dashboard.py`.
- No DB schema or JSONL persistence changes.
- No validation gate, final review decision, monitoring signal, live approval, broker order, account sync, or auto rebalance semantics.
- Missing, stale, failed, and partial states remain visible.
