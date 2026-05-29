# Net Cost Curve Application V1

Status: Active
Created: 2026-05-29
Phase: Phase 9 Cost / Slippage / Liquidity Realism

## 이걸 하는 이유?

Phase 9-1은 cost bps가 단순 assumption인지 result curve에 적용됐는지 구분했고, Phase 9-2는 turnover evidence의 강도를 분리했다.
이 task는 그 다음 단계로, gross / net / estimated cost curve가 실제로 연결되어 있는지 Backtest Realism Audit이 더 직접적으로 확인하게 한다.

## Scope

- runtime net cost curve metadata contract 추가
- gross end balance, net end balance, estimated cost total, positive cost row count를 compact evidence로 전달
- Practical Validation source snapshot이 net cost curve proof를 잃지 않도록 보강
- Backtest Realism Audit에 net cost curve proof row 추가
- cost application flag만 있고 measurable cost impact가 없는 legacy / incomplete source는 PASS로 과대평가하지 않음

## Out Of Scope

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- full execution simulator
- slippage / market-impact sensitivity sweep

## Expected Output

- `Net cost curve proof` row가 measurable cost impact, zero-cost, missing turnover estimate, missing proof를 분리한다.
- result curve가 net 값이라는 증거가 compact metadata로 남는다.
- 기존 저장 경계는 유지한다.
