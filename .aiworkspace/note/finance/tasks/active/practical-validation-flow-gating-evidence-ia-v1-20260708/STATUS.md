# Practical Validation Flow Gating / Evidence IA V1 Status

Status: Active
Date: 2026-07-08

## Current

- User approved 1차부터 4차까지 `개발 -> QA -> 커밋` 순서로 단계별 진행.

## Milestones

- 1차: Completed. Flow 2 replay attempt가 없으면 Flow 3 / Flow 4 / Flow 5와 Practical Validation Result JSON을 렌더링하지 않고 Flow 1 / Flow 2만 보여준다.
- 2차: Completed. Data Coverage / Construction Risk / Provider Investability 중 provider snapshot, holdings / exposure, macro context처럼 기존 Provider / Data 보강 액션으로 수집 가능한 gap만 criteria card에 `수집하기` CTA를 붙이고, Flow 4 순서를 `기준 상세 -> Provider / Data 보강 액션 -> 근거 부록`으로 조정했다.
- 3차: Completed. Workspace read model에 stage ownership inventory를 추가하고 Flow 4에서 접힌 `단계별 검증 소유권`으로 Backtest Analysis / Practical Validation / Final Review / Portfolio Monitoring 소유 기준을 확인할 수 있게 했다.
- 4차: Pending.
