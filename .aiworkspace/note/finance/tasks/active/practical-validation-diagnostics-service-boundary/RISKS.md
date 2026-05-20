# Practical Validation Diagnostics Service Boundary Risks

## Open Risks

- The moved diagnostics service still uses some `app.web` runtime / connector helpers as transitional dependencies.
- Full diagnostic builder remains large; this task changes ownership boundary, not internal formula decomposition.

## Closed In This Task

- Service layer no longer imports Practical Validation diagnostics from `app.web.backtest_practical_validation_helpers`.
