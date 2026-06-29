# Risk Parity / Dual Momentum 5B Notes

## Initial Findings

- 5A pattern: `finance/strategy.py` creates row diagnostics and `app/runtime/backtest.py` attaches compact meta summaries.
- Risk Parity currently computes inverse-vol weights but does not expose eligible universe / vol window / inverse-vol interpretation as a stable row contract.
- Dual Momentum currently selects top-N and handles cash proxy, but does not expose raw top-N, trend rejection, cash proxy retention, or whipsaw/turnover interpretation as a stable row contract.
- `SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS` currently includes GRS but not Risk Parity Trend or Dual Momentum.

## Implementation Notes

- Risk Parity Trend keeps its inverse-vol allocation math and now records the diagnostic inputs used to create those weights.
- Dual Momentum now retains rejected top-N slots as cash proxy instead of silently reweighting all surviving selections to 100%.
- Runtime meta summaries are compact read-only interpretations of `result_df` columns; they do not fetch provider/FRED data or write workflow JSONL.
- Selection History support is an allow-list and renderer extension only; it does not add a new analysis panel.
