# Futures Macro Pattern Outlook V1 Risks

## 2026-07-19 Ten-Year Re-evaluation Residual Risks

- Sample quantity is no longer the principal blocker: 5D has 120 independent episodes and 20D has 88.
- 5D remaining failures are terminal path median error (`0.735945` vs baseline `0.735919`) and middle-50% coverage (`0.267692`).
- 20D remaining failures are Brier baseline improvement (`0.719307` vs `0.718834`), chronological fold improvement ratio (`0.48`), and middle-50% coverage (`0.282828`).
- Both horizons still have `방향 우위 미확인`; no statistically distinct edge may be claimed.
- Any 5차 model work must target these measured failures with chronological out-of-sample comparison. Gate lowering, in-sample-only tuning, and hard-coded promotion remain prohibited.
- RTY begins `2017-07-10`, about one year later than the other core symbols. Feature construction must continue using actual available family inputs without fabricated history.

## 2026-07-19 Materialized Snapshot Residual Risks

- The first entry is intentionally latest-good and DB-only. If the stored schema/algorithm version is incompatible, the screen asks for `일봉 갱신` instead of silently rebuilding.
- Ten-year collection plus materialization is CPU-bound; the actual provider collection job reported 10.59s and snapshot calculation completed behind the same approved daily-ingestion boundary. It never runs after 1m ingestion or display-only reload.
- A daily collection may succeed while snapshot materialization fails; the result is `partial_success`, and operators should inspect the attached materialization result before retrying.
- Compact trace tables are capped at 80 rows and are not a replacement for full OHLCV audit. Full candles remain in the canonical futures OHLCV table.

## Open Risks

### Independent Sample Size

Ten years of daily rows can look large while 20D forward outcomes and adjacent pattern windows are highly overlapping.
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
The corrected map uses only three observed anchors, one direct current-to-terminal expected-net-movement line, and one terminal middle-50% arrival range. Fixed-size direction markers sit on inset mid-line segments rather than endpoint circles. Probability rows remain in the horizon cards, while path status, sample, provisional label, and unavailable-path suppression remain visible beside the map.

### Runtime Cost

Actual multi-window replay initially took 21.791s. Vectorized as-of path statistics reduced it to 4.963s uncached and 0.031s for a same-marker cached reload, so V1 remains process-cached without a DB schema.

### Calibration Gap

The ten-year actual 5D probability gate passes, but path error and interval coverage fail. The 20D sample reached 88, while Brier improvement, fold stability, and interval coverage fail. Both horizons correctly remain `PROVISIONAL`; improving this requires a separately approved model revision, not lower gates.

### Conditional Path Overconfidence

A connected sequence of stepwise medians can be mistaken for a coherent daily forecast even when each step was aggregated independently and regime probabilities remain provisional.
The path must inherit the more conservative of probability and path-validation status,
show the middle 50% historical range, and disappear below 30 independent episodes.
The UI renders only current-to-terminal expected net movement and must not label the line as an actual daily route, future path, or price target.

### Two-Dimensional Coordinate Semantics

The observed point uses current 5D standardized family state while the forecast is a standardized cumulative movement from the origin.
The published endpoint therefore means `current location + conditional analog movement`, not a re-estimated absolute economic state.
Axis copy, method disclosure, and tests must preserve this distinction.

### Horizon Scale Drift

If the selected or hidden forecast geometry owns the SVG scale, horizon switching can move the observed anchors and imply that history changed. The map therefore derives one common bound from both terminal/ranges and excludes hidden intermediate medians; a source contract and actual browser coordinate-equality check guard this comparison rule.

### Shared-Worktree Snapshot Overwrite

`finance_meta.futures_macro_snapshot` currently identifies the compact row by `snapshot_key` only. A concurrently running older worktree can therefore overwrite the compatible V4 row with an older algorithm payload even though sub-dev code and the daily data are correct.
This follow-up restored `pattern_outlook_v4_conservative_status_10y` but did not change the DB schema or cross-worktree runtime contract. Preventing recurrence requires a separately approved versioned-key or writer-compatibility design.

## Escalation Conditions

- Fewer than 30 independent episodes for the selected horizon.
- Required history cannot be collected safely through the existing source boundary.
- Verified outlook requires a new provider, contract curve, or DB schema.
- Actual QA shows the probability presentation is misleading or indistinguishable from a trading signal.
