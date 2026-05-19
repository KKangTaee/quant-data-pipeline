# Evidence Read Model Boundary Design

Status: Complete

Created: 2026-05-20

## Current Coupling

| Area | Current State | Boundary Issue |
|---|---|---|
| Final Review saved decisions | `app/web/backtest_final_review_helpers.py` flattens final decision rows and status display | final decision read model lives under `app/web` |
| Selected Dashboard evidence | `app/web/final_selected_portfolio_dashboard_helpers.py` expands the same final decision evidence checks | evidence row interpretation is duplicated in a UI helper |
| Dashboard runtime | `app/web/runtime/final_selected_portfolios.py` builds selected dashboard rows read-only | acceptable for now, but shared final decision evidence rows should move first |

## Target Slice

```text
Final Review / Selected Dashboard UI helpers
  -> app.services.backtest_evidence_read_model
    -> final decision row dictionaries
```

Service owns:

- final review decision labels and status display copy
- saved final decision table row list
- final decision evidence check row list

UI helpers own:

- `pd.DataFrame` conversion
- Streamlit render
- selectbox labels / filters / layout-specific formatting

## Migration Rule

- Return plain dictionaries / lists from service.
- Do not import Streamlit from service.
- Do not read or write registry files in this service slice.
- Do not change final decision row schema.

## Implemented Slice

- `app/services/backtest_evidence_read_model.py` added.
- Final Review saved decision status / table row read models moved to the service.
- Selected Dashboard evidence check rows moved to the same service.
- UI helpers still convert read-model rows into DataFrames and render them.
