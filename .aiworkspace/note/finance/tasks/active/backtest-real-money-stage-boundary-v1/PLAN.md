# Backtest Real-Money Stage Boundary V1 Plan

Status: Implementation complete
Created: 2026-05-30

## 이걸 하는 이유?

Backtest Analysis는 후보를 만들고 Practical Validation으로 넘길 수 있는지 1차로 보는 단계다.
현재 Real-Money 화면은 `Probation`, `Monitoring`, `Deployment` 같은 후속 운영 표현을 너무 강하게 보여줘 Practical Validation / Final Review / Selected Dashboard 역할과 겹쳐 보인다.
따라서 Backtest 화면에서는 후속 검증을 실행한 것처럼 보이는 표현을 제거하고, 다음 단계에서 확인할 validation focus와 execution preview만 남긴다.

## Scope

- Backtest Real-Money 상단 카드에서 `Probation` / `Deployment`를 후속 운영 상태처럼 보이지 않게 정리한다.
- `Probation / Monitoring` 섹션을 `Next Validation Focus` 성격으로 낮춘다.
- `Deployment Readiness`를 `Execution Preview` 성격으로 낮추고 live deployment 가능성처럼 보이는 copy를 제거한다.
- Runtime metadata / history compatibility field는 유지하되, 사용자-facing 문구는 stage boundary에 맞춘다.
- Compare / History / durable docs에서 같은 용어가 다시 후속 단계처럼 보이지 않도록 정리한다.

## Out Of Scope

- 새 JSONL registry 또는 사용자 메모 / preset 저장 기능
- Practical Validation / Final Review gate 계산 정책 변경
- Selected Dashboard monitoring log 자동 저장
- broker order, live approval, account sync, auto rebalance
- 저장된 과거 run metadata migration
