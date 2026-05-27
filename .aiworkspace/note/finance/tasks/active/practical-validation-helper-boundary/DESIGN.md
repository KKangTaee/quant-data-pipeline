# Practical Validation Helper Boundary Design

Status: Complete
Created: 2026-05-27

## Target Module Placement

| Before | After | Reason |
| --- | --- | --- |
| `app/web/backtest_practical_validation_curve.py` | `app/services/backtest_practical_validation_curve.py` | curve normalize / provenance / parity는 render가 아니라 service evidence helper |
| `app/web/backtest_practical_validation_connectors.py` | `app/services/backtest_practical_validation_provider_context.py` | provider / macro loader output을 diagnostic context로 바꾸는 service adapter |

## Import Direction

After this task:

```text
app/web -> app/services
app/services -> app/runtime / finance
app/runtime -> finance
```

`app/services` and `app/runtime` should not import `app/web`.

## Behavior Rule

This task is an ownership move.
Return dictionaries, public function names, diagnostic statuses, and compact evidence shapes must stay the same.

## Browser Rule

If the implementation only changes Python module locations/imports, browser QA is not required because no visible Streamlit flow or displayed data shape changes.
If import cleanup exposes a visible Practical Validation page error, open the browser and inspect the Backtest / Practical Validation screen.
