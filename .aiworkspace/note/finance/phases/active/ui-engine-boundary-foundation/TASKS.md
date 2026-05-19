# UI Engine Boundary Foundation Tasks

Status: Active
Created: 2026-05-19

## Task Board

| Task | Owner Scope | Status | Notes |
| --- | --- | --- | --- |
| `ui-engine-boundary-audit` | docs + code flow audit | Complete | first implementation target selected: `backtest-execution-service-boundary` |
| `backtest-execution-service-boundary` | Single Strategy execution service | Complete | `app/services/backtest_execution.py` added; UI runner delegates execution |
| `compare-service-boundary` | Compare / weighted portfolio execution service | In progress | manual compare execution loop moved to `app/services/backtest_compare_execution.py`; runner catalog moved to `app/services/backtest_compare_catalog.py`; weighted builder / saved replay remain |
| `practical-validation-service-boundary` | Practical Validation calculation/save/handoff split | Pending | coordinate with active Practical Validation V2 |
| `evidence-read-model-boundary` | Final Review / Selected Dashboard read model | Pending | no frontend migration |

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

- In progress on 2026-05-19.
- Task record: `.aiworkspace/note/finance/tasks/active/compare-service-boundary/`
- Manual compare execution loop and error normalization moved to `app/services/backtest_compare_execution.py`.
- Strategy runner catalog and compare defaults moved to `app/services/backtest_compare_catalog.py`.
- Weighted portfolio builder and saved portfolio replay remain follow-up slices.

## Task 4. Practical Validation Service Boundary

Goals:

- split pure diagnostic computation from Streamlit handoff
- keep provider / macro loader path intact
- preserve `NOT_RUN` semantics
- avoid interfering with active Practical Validation V2 work

## Task 5. Evidence Read Model Boundary

Goals:

- define common evidence/read model for Final Review and Selected Dashboard
- keep selected dashboard read-only
- avoid new frontend/API implementation

## Parking Lot

- FastAPI endpoint
- React / Next.js pilot
- auth / multi-user workflow
- job queue implementation
- live trading / order workflow
