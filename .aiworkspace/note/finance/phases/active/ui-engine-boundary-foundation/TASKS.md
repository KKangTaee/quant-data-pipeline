# UI Engine Boundary Foundation Tasks

Status: Active
Created: 2026-05-19

## Task Board

| Task | Owner Scope | Status | Notes |
| --- | --- | --- | --- |
| `ui-engine-boundary-audit` | docs + code flow audit | Complete | first implementation target selected: `backtest-execution-service-boundary` |
| `backtest-execution-service-boundary` | Single Strategy execution service | Complete | `app/services/backtest_execution.py` added; UI runner delegates execution |
| `compare-service-boundary` | Compare / weighted portfolio execution service | Complete | manual compare, runner catalog, weighted builder, result read model, saved replay data assembly moved to `app/services` |
| `practical-validation-service-boundary` | Practical Validation calculation/save/handoff split | Complete | first service slice added for source/result append and Final Review handoff contract |
| `evidence-read-model-boundary` | Final Review / Selected Dashboard read model | Complete | shared final decision evidence read model moved to `app/services` |

## Task 1. UI Engine Boundary Audit

Goals:

- map current UI / runtime / engine ownership
- identify direct Streamlit dependencies in helper/runtime-adjacent files
- identify first safe extraction target
- record no-go files for early work

Deliverables:

- `.aiworkspace/note/finance/tasks/active/ui-engine-boundary-audit/`
- findings in `NOTES.md`
- run log in `RUNS.md`
- risk list in `RISKS.md`

## Task 2. Backtest Execution Service Boundary

Goals:

- create `app/services/backtest_execution.py`
- move single-run strategy dispatch and error normalization out of `backtest_single_runner.py`
- keep UI behavior and history append stable

Candidate checks:

- `.venv/bin/python -m py_compile app/services/backtest_execution.py app/web/backtest_single_runner.py`
- import smoke for `app.services.backtest_execution`
- `rg "streamlit|st\\." app/services/backtest_execution.py` should return no hits

Result:

- Complete on 2026-05-19.
- Task record: `.aiworkspace/note/finance/tasks/active/backtest-execution-service-boundary/`

## Task 3. Compare Service Boundary

Goals:

- identify compare execution functions currently embedded in `backtest_compare.py`
- extract compare run dispatch after Task 2 pattern is stable
- defer chart/render/session state cleanup

Current slice:

- Complete on 2026-05-20.
- Task record: `.aiworkspace/note/finance/tasks/active/compare-service-boundary/`
- Manual compare execution loop and error normalization moved to `app/services/backtest_compare_execution.py`.
- Strategy runner catalog and compare defaults moved to `app/services/backtest_compare_catalog.py`.
- Weighted portfolio bundle construction moved to `app/services/backtest_weighted_portfolio.py`.
- Result data trust / component contribution read model moved to `app/services/backtest_result_read_model.py`.
- Saved portfolio replay execution / data assembly moved to `app/services/backtest_saved_portfolio_replay.py`.
- UI still owns session state, history append calls, notices, and rendering.

## Task 4. Practical Validation Service Boundary

Goals:

- split pure diagnostic computation from Streamlit handoff
- keep provider / macro loader path intact
- preserve `NOT_RUN` semantics
- avoid interfering with active Practical Validation V2 work

Result:

- Complete on 2026-05-20.
- Task record: `.aiworkspace/note/finance/tasks/active/practical-validation-service-boundary/`
- Added `app/services/backtest_practical_validation.py` as a Streamlit-free source/result save and handoff contract boundary.
- Removed direct Streamlit session-state writes from `app/web/backtest_practical_validation_helpers.py`.
- UI modules still own buttons, session state, rendering, provider gap collection UI, and rerun behavior.

## Task 5. Evidence Read Model Boundary

Goals:

- define common evidence/read model for Final Review and Selected Dashboard
- keep selected dashboard read-only
- avoid new frontend/API implementation

Result:

- Complete on 2026-05-20.
- Task record: `.aiworkspace/note/finance/tasks/active/evidence-read-model-boundary/`
- Added `app/services/backtest_evidence_read_model.py` for Final Review status / saved decision table rows / Selected Dashboard evidence checks.
- Final Review and Selected Dashboard helpers now consume the same Streamlit-free read model.
- Selected Dashboard remains read-only and no registry schema changed.

## Parking Lot

- FastAPI endpoint
- React / Next.js pilot
- auth / multi-user workflow
- job queue implementation
- live trading / order workflow
