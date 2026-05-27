# UI Engine Boundary Cleanup Audit Notes

Status: Complete
Created: 2026-05-27

## Baseline

Current package split:

- `app/web`: Streamlit UI, form, routing, session state, render feedback
- `app/services`: Streamlit-free use-case service and evidence/result orchestration
- `app/runtime`: Streamlit-free runtime / repository / registry helper boundary
- `finance/*`: data, loader, strategy, transform, performance engine

## Boundary Lint Findings

Hard violations: none.

Advisories:

- `app/services/backtest_practical_validation_diagnostics.py:13` imports `app.web.backtest_practical_validation_curve`
- `app/services/backtest_practical_validation_diagnostics.py:18` imports `app.web.backtest_practical_validation_connectors`
- `app/services/backtest_practical_validation_replay.py:10` imports `app.web.backtest_practical_validation_curve`

Interpretation:

- The current architecture is already separated enough to pass the hard Streamlit boundary.
- The remaining issue is reverse package dependency: service modules depend on helper modules located under `app/web`.
- Because those helper modules are Streamlit-free, this is not an immediate runtime bug, but it weakens future multi-agent ownership.

## Large File Candidates

| File | Lines | Interpretation |
| --- | ---: | --- |
| `app/services/backtest_practical_validation_diagnostics.py` | 2956 | diagnostics orchestration and multiple evidence helper families live together |
| `app/runtime/backtest.py` | 5191 | runtime wrapper, policy surfaces, preflight, strategy-family dispatch are bundled |
| `app/runtime/final_selected_portfolios.py` | 1064 | selected dashboard runtime read model and performance recheck logic are together |
| `app/runtime/candidate_library.py` | 800 | candidate library read model and replay dispatch helper are together |

## Recommended Task Order

1. Task 6 removes the remaining service/runtime -> web helper dependency.
2. Task 7 splits diagnostics helpers after the dependency direction is clean.
3. Task 8 maps runtime wrapper responsibilities before applying low-risk extraction.
4. Task 9 hardens lint/test/docs once the advisory debt is gone.

## Important Constraint

Task 6~9 should keep calculation semantics stable unless a task explicitly says otherwise.
This cleanup phase is about ownership, import direction, and maintainability.
