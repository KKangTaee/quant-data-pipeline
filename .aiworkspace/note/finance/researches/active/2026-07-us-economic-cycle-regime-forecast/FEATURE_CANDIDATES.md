# Feature Candidates

Status: Complete
Last Updated: 2026-07-16

Scoring: 1 low, 5 high.

## Priority Matrix

| Bucket | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Now | Vintage-aware macro evidence contract | 5 | 4 | 4 | 5 | 5 | Required foundation |
| Now | Four-phase current-state engine | 5 | 4 | 4 | 4 | 5 | Build after vintage contract |
| Now | Calibrated +1M / +2M transition forecast | 5 | 4 | 5 | 4 | 5 | Build with rolling-origin evaluation |
| Now | Market Context economic-cycle surface | 5 | 4 | 3 | 5 | Build only on validated read model |
| Next | Forecast replay and revision comparison | 4 | 3 | 3 | 4 | 4 | Add after first production cycle |
| Later | Fiscal-policy impulse module | 3 | 4 | 5 | 2 | 3 | Research source/cadence separately |
| Parking Lot | Phase-based portfolio recommendation | 3 | 4 | 5 | 2 | 1 | Outside current product boundary |

## Now. Vintage-Aware Macro Evidence Contract

Goal:

- Preserve what was known on each historical forecast date for a focused U.S. macro series catalog.

Evidence:

- Audit: current macro UPSERT overwrites revisions.
- Benchmark: ALFRED, ADS vintages, and Chauvet-Hamilton require real-time information sets.

Dependencies:

- Series catalog with frequency, transformation, polarity, release lag, vintage source, and freshness rule.
- Schema decision: extend the current table or add a dedicated vintage table without breaking existing readers.

Success criteria:

- A forecast-origin loader returns only observations released by that date.
- First-release and latest-revised values can be compared.
- Existing Practical Validation macro readers remain compatible.

## Now. Four-Phase Current-State Engine

Goal:

- Separate real activity from market-implied conditions and estimate `회복`, `확장`, `둔화`, `침체` probabilities.

Proposed semantics:

- `회복`: activity below trend but momentum and breadth improving; contraction probability falling.
- `확장`: activity near/above trend with positive or stable momentum and broad participation.
- `둔화`: activity not yet broadly contracting, but momentum/leading breadth deteriorating.
- `침체`: significant, broad, persistent contraction probability is dominant.

Dependencies:

- Coincident dynamic factor or equivalent composite.
- Leading, inflation/policy, and financial-condition features.
- Explicit mapping to final NBER recession chronology for evaluation, not live declaration.

Success criteria:

- No future release enters a historical current-state estimate.
- Probabilities sum to 100% and alternative phases stay visible.
- Historical turning-point delay and false alarms are reported.

## Now. Calibrated +1M / +2M Forecast

Goal:

- Produce separate phase distributions one and two months ahead from the current information set.

Recommended method:

- Hybrid factor + constrained transition model.
- Direct horizon-specific probability calibration rather than extrapolating one point estimate twice.
- Compare against naive baselines: current phase persists, fixed historical transition matrix, and OECD CLI quadrant.

Success criteria:

- Rolling-origin backtest uses vintages.
- Report Brier score, log loss, calibration error, phase confusion, and turning-point lead/lag.
- Forecast is withheld or marked limited when input coverage or calibration is inadequate.

## Now. Market Context Economic-Cycle Surface

Goal:

- Add `경제 사이클` alongside S&P 500 and U.S. stock analysis without mixing cycle logic into valuation code.

Workflow change:

- User opens Market Context, selects `경제 사이클`, and sees current probabilities, path, history, forecast, and evidence without visiting Ingestion.
- S&P 500 and U.S. stock flows retain existing behavior.

Success criteria:

- Cycle clock + regime ribbon + probability horizon strip render on desktop and 420px mobile.
- The component consumes one JSON-safe service read model.
- No provider call occurs during rendering.
- Forecast/history/source semantics are visually distinct.

## Parking Lot

- Automatic asset allocation, buy/sell, or risk-budget changes by phase.
- Gold / dollar / rates-only phase engine.
- LLM-generated cycle calls without deterministic data provenance.
- Full global multi-country cycle comparison before the U.S. model is validated.
- Fiscal impulse as a numeric core pillar before a durable official real-time source contract exists.
