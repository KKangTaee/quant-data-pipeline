# PHASE13 Value Strict Hold-Free Search

## Goal
Find a `Value Strict Annual` configuration that satisfies all three:
- `promotion != hold`
- `CAGR >= 15%`
- `MDD >= -20%`

The user asked for a practical, UI-exposed search first:
- keep `Universe Contract = Historical Dynamic PIT Universe`
- start from `2016-01-01`
- keep `top_n <= 10`
- vary benchmark contract / ticker
- vary factor combinations
- vary cadence with `month_end`, `rebalance_interval = 1 / 3`
- toggle `trend_filter` and `market_regime`

## Search Result
No configuration in the tested practical grid satisfied all three conditions at once.

### Best exact-hit numeric candidate
- family: `Value > Strict Annual`
- factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `month_end`
- `rebalance_interval = 1`
- `top_n = 9`
- `benchmark = SPY`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`
- result:
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
  - `promotion = hold`
  - `reason = validation_caution + validation_policy_caution`

### Structural findings
- Changing benchmark contract / ticker:
  - `SPY`, `LQD`, `IEF`, `TLT`, `candidate_universe_equal_weight`
  - did not produce a non-hold exact hit within the target envelope
- Changing cadence:
  - `rebalance_interval = 1` and `3`
  - did not clear `hold` while keeping both numeric constraints
- Changing trend / regime switches:
  - turning them off could clear `hold`
  - but drawdown worsened sharply and broke the target
- The exact-hit candidate is blocked by the validation layer, not the raw return profile.

## Practical Conclusion
If the user wants:
- `hold` cleared
- `CAGR >= 15%`
- `MDD >= -20%`

then the next lever is not more raw return tuning alone.
The likely next step is to relax or retune the validation / promotion policy thresholds.
