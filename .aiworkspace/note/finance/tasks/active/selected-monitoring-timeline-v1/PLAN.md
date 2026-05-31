# Selected Monitoring Timeline V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Selected Portfolio Dashboard는 Final Review에서 선정된 포트폴리오를 다시 확인할 수 있지만, 사용자가 현재 상태를 시간 흐름으로 읽기 어렵다.

이번 작업은 새 자동 저장이나 사용자 메모 기능을 추가하지 않고, 기존 Final Review selection, Performance Recheck, Actual Allocation drift, review trigger 신호를 하나의 read-only timeline으로 묶어 "지금 무엇을 다시 봐야 하는지"를 더 선명하게 만드는 것이다.

## Scope

- Selected Dashboard용 monitoring timeline read model 추가.
- Timeline은 Final Review decision row, latest recheck session result, latest drift session result를 읽는다.
- 새 registry write, 자동 monitoring log append, alert 저장은 추가하지 않는다.
- Selected Dashboard UI에 Timeline tab을 추가한다.
- Streamlit-free runtime contract test를 추가한다.

## Non-Goals

- broker order, live approval, auto rebalance
- 자동 알림 / automation / background monitor
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` 자동 append
- 사용자 free-form memo 저장
- 새 DB schema 또는 ingestion 구현

## Verification Plan

- relevant Python compile
- `tests/test_service_contracts.py`
- UI-engine boundary check
- `git diff --check`
- Browser smoke for Operations > Selected Portfolio Dashboard
