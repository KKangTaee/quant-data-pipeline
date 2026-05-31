# Backtest Real-Money Readiness Efficacy V1 Plan

Status: Complete
Created: 2026-05-30

## 이걸 하는 이유?

Backtest Real-Money는 1차 후보 검증으로 유효하지만, 일부 계산과 표현이 후속 단계인 probation / monitoring 개념을 다시 끌어와 중복 해석될 수 있다.
이번 작업은 새 저장 기능이나 새 검증 축을 추가하지 않고, 이미 있는 1차 지표가 실제 원천 증거만 기준으로 읽히도록 정리한다.

## Scope

- `Execution Preview`가 `Probation` / `Monitoring` 파생값을 평가하지 않고, benchmark / liquidity / validation / guardrail / ETF / freshness / rolling / split-period 원천 지표만 보게 한다.
- `Candidate Readiness` 점수에서 `Execution Preview`를 별도 stage처럼 중복 가중하지 않고, Promotion / execution burden / validation burden / blocker로 나눠 계산한다.
- Turnover / cost 표시에서 holdings 기반 추정 상태를 함께 보여주고, 추정 불가 상태를 0처럼 오해하지 않게 한다.
- `Out-of-Sample Review` 표현을 Backtest 1차의 간이 전후반 구간 점검으로 낮춘다.

## Out Of Scope

- 새 DB schema, 새 JSONL registry, 사용자 memo / preset 저장 기능
- Practical Validation / Final Review의 gate policy 재설계
- broker approval, order, account sync, auto rebalance
- 저장된 과거 run metadata migration
