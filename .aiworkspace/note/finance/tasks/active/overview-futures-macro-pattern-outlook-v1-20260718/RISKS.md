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

A polished probability path can look more certain than the evidence. The first ellipse design made one median location look like the forecast and the 60-point observed polyline hid time order; the intermediate fixed categorical branches also did not change geometry by horizon.
The corrected map uses only three observed anchors, the selected horizon's historical-analog median path, and one terminal middle-50% arrival range. Fixed-size direction markers sit on inset mid-line segments rather than endpoint circles. Probability rows remain in the horizon cards, while path status, sample, provisional label, and unavailable-path suppression remain visible beside the map.

### Runtime Cost

Actual multi-window replay initially took 21.791s. Vectorized as-of path statistics reduced it to 4.963s uncached and 0.031s for a same-marker cached reload, so V1 remains process-cached without a DB schema.

### Calibration Gap

The actual 5D Brier score is slightly worse than its unconditional baseline, while 20D has only 42 independent episodes. Both horizons correctly remain `PROVISIONAL`; improving this requires more independent history or a separately approved model/source revision, not lower gates.

### Conditional Path Overconfidence

A median analog path can be mistaken for a precise forecast even when its regime probabilities remain provisional.
The path must inherit the more conservative of probability and path-validation status,
show the middle 50% historical range, and disappear below 30 independent episodes.
The UI must not label the line as an actual future path or price target.

### Two-Dimensional Coordinate Semantics

The observed point uses current 5D standardized family state while the forecast is a standardized cumulative movement from the origin.
The published endpoint therefore means `current location + conditional analog movement`, not a re-estimated absolute economic state.
Axis copy, method disclosure, and tests must preserve this distinction.

## Escalation Conditions

- Fewer than 30 independent episodes for the selected horizon.
- Required history cannot be collected safely through the existing source boundary.
- Verified outlook requires a new provider, contract curve, or DB schema.
- Actual QA shows the probability presentation is misleading or indistinguishable from a trading signal.
