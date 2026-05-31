# Phase 13 Gate Validation QA Matrix V1 Design

Status: Complete
Created: 2026-05-30
Completed: 2026-05-30

## QA Layers

| Layer | QA Question | Primary Code Surface |
| --- | --- | --- |
| Practical Validation | Evidence row status가 `PASS / REVIEW / NEEDS_INPUT / BLOCKED / NOT_RUN`로 보이는가? | `app/web/backtest_practical_validation.py`, audit service read models |
| Final Review | non-PASS audit row가 investability packet과 selected-route gate에 반영되는가? | `app/services/backtest_evidence_read_model.py`, `app/web/backtest_final_review_helpers.py` |
| Selected Dashboard | 선정 이후 stale / missing / breached / source mismatch가 정상처럼 보이지 않는가? | `app/runtime/final_selected_portfolios.py`, `app/web/final_selected_portfolio_dashboard.py` |
| Service contracts | 위 route가 regression test로 고정되어 있는가? | `tests/test_service_contracts.py` |

## Severity Interpretation

| Input State | Final Review Gate Interpretation | Selected Dashboard Interpretation |
| --- | --- | --- |
| `PASS` | Gate row ready | Ready / clear only if all required evidence rows pass |
| `REVIEW`, stale, partial, watch | `REVIEW_REQUIRED` for critical groups; selected route disallowed | Review / watch route; user must inspect |
| `NEEDS_INPUT`, missing, `NOT_RUN` critical evidence | `BLOCK` for critical groups; selected route disallowed | Needs data / needs input route |
| `BLOCKED`, error, source mismatch | `BLOCK`; selected route disallowed | Blocked route |
| breached recheck / allocation drift | Not a new Final Review approval; post-selection review signal | Breached / rebalance review signal only, no order |

## Result Classification

- `QA_PASS`: existing implementation and service contracts support the intended severity.
- `FOLLOW_UP`: not a code defect, but should be documented or triaged in later Phase 13 tasks.
- `DEFECT`: code behavior contradicts the intended gate / severity contract and needs a scoped implementation task.
