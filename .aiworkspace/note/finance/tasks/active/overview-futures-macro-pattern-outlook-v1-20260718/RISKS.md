# Futures Macro Pattern Outlook V1 Risks

## Open Risks

### Independent Sample Size

Five years of daily rows can look large while 20D forward outcomes and adjacent pattern windows are highly overlapping.
The publication gate must use effective independent episodes, not raw daily counts.

### Overfitting

Similarity weights, thresholds, and state labels can be tuned to historical anecdotes.
Weights must be fixed before actual outcome review and evaluated with chronological walk-forward tests.

### Continuous Futures Semantics

yfinance continuous futures may differ from specific contract roll and maturity behavior.
V1 cannot present its probabilities as exchange-contract forecasts.

### Causal Language

Cross-asset futures can show what repriced together but cannot prove why an event caused the movement.
UI copy must say `근거`, `일치`, `압력`, or `해석` rather than confirmed cause.

### UI Overconfidence

A polished probability path can look more certain than the evidence.
Baseline comparison, estimate status, sample, and unavailable states must remain visible.

### Runtime Cost

Actual multi-window replay initially took 21.791s. Vectorized as-of path statistics reduced it to 4.963s uncached and 0.031s for a same-marker cached reload, so V1 remains process-cached without a DB schema.

### Calibration Gap

The actual 5D Brier score is slightly worse than its unconditional baseline, while 20D has only 42 independent episodes. Both horizons correctly remain `PROVISIONAL`; improving this requires more independent history or a separately approved model/source revision, not lower gates.

## Escalation Conditions

- Fewer than 30 independent episodes for the selected horizon.
- Required history cannot be collected safely through the existing source boundary.
- Verified outlook requires a new provider, contract curve, or DB schema.
- Actual QA shows the probability presentation is misleading or indistinguishable from a trading signal.
