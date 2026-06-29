# Design

Status: Completed
Last Verified: 2026-06-08

## Source Context

- Parent research bundle: `.aiworkspace/note/finance/researches/active/2026-06-backtest-strategy-direction/`
- Preceding task: `.aiworkspace/note/finance/tasks/active/strategy-evidence-inventory-direction-panel-20260608/`
- Owner skill: `finance-backtest-web-workflow`

## Implementation Direction

### Read Model

Add a Streamlit-free bridge read model under `app/services/`.
It should depend only on existing Streamlit-free services/catalogs.

Rows should include:

- strategy key / display name / bridge role
- target use
- current anchor
- known weakness
- required Practical Validation evidence
- recommended next workflow
- route boundary

The read model should also expose bridge-level summary / checklist items:

- bridge group membership
- candidate intent
- validation checklist
- deferred exclusions
- storage / governance boundary

### UI Surface

Render a read-only `Strict Annual + GTAA / Equal Weight Bridge` section in `Backtest > Backtest Analysis`.
It should appear after the 3A inventory because it uses the inventory's first evidence-mature group as input.

### Test Strategy

Add focused Streamlit-free tests before implementation.
Tests should verify:

- bridge group is exactly strict annual 3종 + GTAA + Equal Weight
- no Risk-On Momentum / quarterly prototype / low-evidence ETF strategy is included
- each row has role / target use / required validation / recommended workflow
- Practical Validation and Final Review boundaries are visible
- rows are returned as copies

## Boundary Decisions

- This task improves decision workflow clarity, not strategy execution.
- Bridge rows do not create selected candidates or validation results.
- Practical Validation remains the owner of PASS / BLOCKER / selected-route evidence.
- Final Review and Portfolio Monitoring remain read-only decision support, not live trading.
