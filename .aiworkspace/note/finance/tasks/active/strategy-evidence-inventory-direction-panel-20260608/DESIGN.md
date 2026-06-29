# Design

Status: Completed
Last Verified: 2026-06-08

## Source Context

- 2차 research bundle: `.aiworkspace/note/finance/researches/active/2026-06-backtest-strategy-direction/`
- Required docs checked: `PROJECT_MAP.md`, `BACKTEST_RUNTIME_FLOW.md`, `BACKTEST_UI_FLOW.md`
- Owner skill: `finance-backtest-web-workflow`

## Implementation Direction

### Read Model

Create a Streamlit-free service under `app/services/` that builds a static interpretation model from the current strategy catalog.
The read model should expose rows with:

- strategy key / display name / family
- intended role
- maturity
- runtime / compare / replay support
- evidence anchor
- main weakness
- next action
- product lane / governance note
- recommended group marker

The service must not import Streamlit, mutate registries, call strategy runtimes, fetch providers, or read DB state.
The canonical strategy catalog now lives in `app/services/backtest_strategy_catalog.py`; `app/web/backtest_strategy_catalog.py` remains a compatibility wrapper so services do not import `app.web`.

### UI Surface

Render a read-only `Strategy Evidence Inventory / Direction Panel` in `Backtest > Backtest Analysis`.
The panel should sit near the stage entry before Single Strategy / Portfolio Mix Builder choices, because it explains how to interpret available strategies before running or packaging them.

### Test Strategy

Add focused Streamlit-free tests before implementation.
Tests should verify:

- every `app/web/backtest_strategy_catalog.py` catalog key appears in the evidence inventory
- Risk-On Momentum 5D lane is research / governance deferred
- quarterly strict prototypes are prototype / contract-smoke
- strict annual 3종 + GTAA / Equal Weight are first evidence-mature candidates
- rows expose next-action text and do not require Streamlit

## Boundary Decisions

- Treat the inventory as a product interpretation layer, not a candidate registry or source-of-truth rewrite.
- Keep Risk-On Momentum governance deferred even though runtime and research artifacts exist.
- Keep quarterly strict family below annual strict readiness.
- Do not convert maturity labels into validation pass / fail status.
- Keep Backtest strategy catalog ownership Streamlit-free so service read models pass the UI / engine boundary checker.
