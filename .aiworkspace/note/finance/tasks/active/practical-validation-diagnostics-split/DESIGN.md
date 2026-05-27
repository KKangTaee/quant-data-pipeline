# Practical Validation Diagnostics Split Design

Status: Active
Created: 2026-05-27

## Split Order

The split order follows dependency risk.

1. `7-01`: source/profile builder
2. `7-02`: curve context helper
3. `7-03`: stress/sensitivity helper
4. `7-04`: orchestration cleanup

## 7-01 Module Boundary

New module:

```text
app/services/backtest_practical_validation_source.py
```

Responsibilities:

- validation profile options / questions / domain weights
- user answer normalization into threshold/domain-weight contract
- candidate draft / saved mix / weighted mix to Clean V2 selection source conversion
- tiny shared scalar helpers required by the source/profile contract

The existing diagnostics module keeps importing these public builders so existing callers can migrate gradually.

## Browser Decision

`7-01` changes service module ownership and imports only.
It does not change Streamlit layout, user controls, session state keys, or displayed data shape.
Browser QA is not required unless tests reveal a runtime import break.
