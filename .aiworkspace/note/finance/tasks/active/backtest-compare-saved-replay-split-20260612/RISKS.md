# Backtest Compare Saved Replay Split 6A Risks

## Open Risks

- Full `tests.test_service_contracts` still has an unrelated macro thermometer baseline failure: `FuturesMacroThermometerContractTests.test_macro_thermometer_inverts_rates_and_fx_pressure` expects `OK` while current output is `REVIEW`. Track separately before treating the whole suite as green.
- Streamlit emits `use_container_width` deprecation warnings during Browser QA. This is broader UI debt and not introduced by 6A.
- `app/web/backtest_compare.py` still owns weighted-result and strategy-specific form bodies, so file size remains high until 6B / 6C.

## Follow-Up

- 6B should split weighted result / Practical Validation handoff panel after 6A.
- 6C should split the strategy-specific form body after the weighted result boundary is stable.
