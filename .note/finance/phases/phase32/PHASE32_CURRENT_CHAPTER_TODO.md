# Phase 32 Current Chapter TODO

## 진행 상태

- `complete`

## 검증 상태

- `manual_qa_completed`

## 현재 목표

Phase 32의 목표는 Phase 31에서 읽은 후보 또는 Portfolio Proposal을 바로 승인하는 것이 아니다.
저장된 기간 / 설정 / benchmark / 성과 snapshot을 바탕으로 robustness / stress 검증을 실행할 준비가 되었는지 먼저 확인하고,
이후 실제 stress summary를 붙일 수 있는 입력 계약을 고정하는 것이다.

## 작업 단위 진행 순서

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Phase 32 전체 목표 | Robustness / Stress Validation Pack을 만든다 | `complete` |
| 첫 번째 작업 | Robustness 입력 preview와 stress 실행 후보 판정 | `completed` |
| 두 번째 작업 | Stress / sensitivity result contract 정의 | `completed` |
| 세 번째 작업 | 후보 / proposal별 stress summary surface 추가 | `completed` |
| 네 번째 작업 | Phase 33 paper ledger handoff 정리 | `completed` |

## 1. Phase kickoff

- `completed` Phase 32 문서 bundle 생성
  - 문서 위치는 `.note/finance/phases/phase32/`이다.
- `completed` Phase 31 next phase preparation 확인
  - Phase 31 QA 완료 후 Phase 32 `Robustness And Stress Validation Pack`으로 진행하는 방향을 확인했다.
- `completed` 첫 번째 작업 단위 구현
  - `Backtest > Portfolio Proposal` Validation Pack 안에 `Robustness / Stress Validation Preview`를 붙인다.

## 2. 첫 번째 작업 구현 항목

- `completed` Phase 31 validation input에 robustness가 읽을 snapshot 추가
  - period, contract, compare evidence를 component row에 포함한다.
- `completed` robustness route / score / blocker / input gap / suggested sweep 계산
  - route는 `READY_FOR_STRESS_SWEEP`, `NEEDS_ROBUSTNESS_INPUT_REVIEW`, `BLOCKED_FOR_ROBUSTNESS`로 나눈다.
- `completed` UI preview 추가
  - Validation Pack 아래에서 component별 기간 / CAGR / MDD / benchmark / contract / compare evidence를 확인한다.
- `completed` 문서 sync
  - roadmap / doc index / code flow / work log를 Phase 32 complete 상태로 맞춘다.

## 3. Validation

- `completed` `.venv/bin/python -m py_compile app/web/backtest_portfolio_proposal.py app/web/backtest_portfolio_proposal_helpers.py`
- `completed` saved proposal robustness helper smoke
  - 저장된 proposal에서 robustness route와 suggested sweep row가 생성되는지 확인했다.
- `completed` saved proposal stress summary / Phase33 handoff helper smoke
  - 저장된 proposal에서 stress summary row 6개와 Phase33 handoff route가 생성되는지 확인했다.
- `completed` Streamlit server health smoke
  - 기존 local Streamlit server가 `http://localhost:8520`에서 응답하는지 확인했다.
- `completed` targeted manual validation
  - 사용자가 Phase32 checklist 기준으로 QA 완료를 확인했다.

## 4. Documentation Sync

- `completed` phase kickoff plan 문서 생성
- `completed` current chapter TODO 문서 생성
- `completed` first work-unit 문서 생성
- `completed` second / third / fourth work-unit 문서 생성
- `completed` final checklist 정리
- `completed` roadmap / doc index / work log / question log sync
- `completed` Backtest UI flow sync

## 현재 판단

Phase 32는 complete / manual_qa_completed 상태다.
2번째부터 4번째 작업까지 구현과 helper smoke를 통과했고, 사용자 checklist QA까지 완료했다.
