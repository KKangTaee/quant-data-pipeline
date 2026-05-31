# Cost Model Source Contract Review V1

Status: Active
Created: 2026-05-29
Phase: Phase 9 Cost / Slippage / Liquidity Realism

## 이걸 하는 이유?

Backtest Realism Audit은 거래비용 bps가 있는지 확인하지만, 그 값이 단순 입력 가정인지 실제 result curve에 반영된 비용인지 더 분명히 구분해야 한다.
이 task는 새 저장소나 사용자 메모 기능을 만들지 않고, 기존 runtime metadata와 Practical Validation source snapshot 안에서 cost source contract를 compact하게 전달하도록 보강한다.

## Scope

- 현재 cost 값의 생성 / 전달 / 판정 경로 확인
- runtime result metadata에 비용 적용 증거를 명시하는 compact contract 추가
- Practical Validation source snapshot이 cost contract를 잃지 않도록 보강
- Backtest Realism Audit이 assumption-only와 applied-net-curve를 구분하도록 보강
- service contract test와 compile 검증

## Out Of Scope

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- full execution simulator
- 세금 최적화 또는 market microstructure simulator

## Expected Output

- `Transaction cost model` row가 missing / zero-cost / assumption-only / applied-to-result-curve를 구분한다.
- future source snapshot은 cost contract를 compact evidence로 보존한다.
- 기존 저장 경계는 유지한다.
