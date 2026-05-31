# Practical Validation V2 P3 Continuity Check Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

P2는 Practical Validation evidence를 provider / macro / robustness 기준으로 정상화했다.
P3의 첫 문제는 Final Review에서 선정된 row가 Selected Portfolio Dashboard에서 사후 점검 가능한 상태인지 한눈에 확인하기 어렵다는 점이다.

이번 작업은 새 저장소나 자동 monitoring log를 만들지 않고, 기존 final decision row와 session timeline을 읽어 continuity QA를 보여준다.

## Scope

- Final Review selected row가 Selected Dashboard monitoring에 필요한 필드를 갖췄는지 read-only check를 만든다.
- selected route, evidence packet, component target, review trigger, monitoring timeline, performance recheck input 상태, execution / storage boundary를 확인한다.
- Selected Dashboard에 continuity check table과 summary badge를 표시한다.
- service contract test로 read-only boundary와 needs-input 상태를 고정한다.

## Non-Goals

- monitoring log 자동 저장
- broker approval / order / auto rebalance
- account holding 자동 연결
- strategy-specific sensitivity runtime sweep
- 새 JSONL registry 추가

## Verification Plan

- `.venv/bin/python -m unittest tests/test_service_contracts.py`
- `.venv/bin/python -m py_compile app/runtime/final_selected_portfolios.py app/web/final_selected_portfolio_dashboard.py app/web/final_selected_portfolio_dashboard_helpers.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `git diff --check`
