# Design

## User Flow

The Overview first screen reads in this order:

1. Market session banner.
2. Macro Context Cockpit with Source Confidence.
3. Overview Map showing where to drill next.
4. Deep tabs.

## Model

`load_overview_ia_closeout_model()` returns static, Streamlit-free metadata:

- market-context tabs: Market Movers, Futures Monitor, Sentiment, Sector / Industry, Events
- data-repair tab: Data Health
- transitional tab: Candidate Ops
- boundary note: context-only, no validation / monitoring / trading / persistence semantics

## Rendering

`render_overview_ia_closeout_guide()` renders a compact full-width band with small cards.
The component is intentionally simple and does not fetch data.

## Tradeoff

This avoids a disruptive navigation change while making the candidate/backtest boundary clear.
A future approved IA task can remove, relocate, or rename Candidate Ops after the user confirms the workflow impact.
