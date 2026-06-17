# Design

## Operating Contract

Use the existing product workflow as-is:

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Portfolio Monitoring
```

The final candidate must satisfy both numeric exploration criteria and workflow gate criteria:

- CAGR greater than SPY over the same available period.
- MDD lower than SPY over the same available period.
- MDD below 15%.
- Practical Validation final review gate allows handoff.
- Final Review selected-route gate allows `SELECT_FOR_PRACTICAL_PORTFOLIO`.
- Portfolio Monitoring saved setup contains a complete strategy slot.
