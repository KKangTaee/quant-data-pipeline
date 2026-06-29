# Overview Futures Macro Mixed Substates V1 Notes

## Initial Notes

- Current production snapshot often returns `혼재된 매크로 흐름`.
- Recent inspection showed mixed has many historical occurrences but no directional hit rule, so this change should explain mixed context rather than force a prediction.
- Keep top-level scenario stable for historical validation compatibility.

## Implementation Notes

- Mixed subtype is calculated only in the final fallback branch of `generate_market_interpretation`.
- Existing directional scenarios such as `금리 상승 부담`, `좋은 risk-on`, and `경기침체 우려 / risk-off` keep their prior rule order and labels.
- The UI shows subtype / hint / reason as supporting copy below the main scenario. It is not a status table, job diagnostic, trade signal, validation gate, or monitoring signal.
- 2차 전문성 보강 후보 remains independent macro source integration such as yield curve, volatility, credit spread, real yield, and breakeven inflation.
