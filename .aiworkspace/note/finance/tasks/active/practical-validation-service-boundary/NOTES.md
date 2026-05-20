# Practical Validation Service Boundary Notes

## Observations

- `app/web/backtest_practical_validation.py` owns screen rendering and interactive buttons.
- `app/web/backtest_practical_validation_helpers.py` owns diagnostic result construction, result save helper, and Final Review queue helper.
- The Final Review queue helper currently writes `st.session_state` from the helper module, which makes a non-render helper depend on Streamlit.
- Provider / macro evidence is read through loader-backed connector helpers and should not become a direct provider fetch from UI.

## Decisions

- The first slice should not move the 12-diagnostic builder wholesale.
- Source append and validation result append are service responsibilities.
- Handoff notices / payloads are service contracts; Streamlit session-state writes stay in UI modules.
- At this task's first slice, `app/web/backtest_practical_validation_helpers.py` could remain the calculation helper as long as it stayed Streamlit-free.
- Follow-up `practical-validation-diagnostics-service-boundary` later moved that helper to `app/services/backtest_practical_validation_diagnostics.py`.
