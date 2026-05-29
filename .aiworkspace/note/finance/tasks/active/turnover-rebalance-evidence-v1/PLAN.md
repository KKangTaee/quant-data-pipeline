# Turnover Rebalance Evidence V1

Status: Active
Created: 2026-05-29
Phase: Phase 9 Cost / Slippage / Liquidity Realism

## 이걸 하는 이유?

거래비용은 turnover 추정치에 크게 의존한다.
현재 runtime은 `avg_turnover` / `max_turnover`를 metadata로 남기지만, 그 값이 실제 holdings delta에서 나온 것인지, 단순 rebalance cadence만 있는 것인지, 또는 추정 입력이 부족한지를 audit에서 충분히 분리하지 못한다.

이 task는 새 저장 기능을 만들지 않고, 기존 runtime metadata와 Practical Validation source snapshot 안에서 turnover evidence의 강도를 분리한다.

## Scope

- turnover estimate 입력 column과 추정 가능 여부 확인
- runtime metadata에 compact turnover evidence contract 추가
- Practical Validation source snapshot / history record에 turnover evidence 유지
- Backtest Realism Audit이 actual estimate / cadence-only / missing을 구분하도록 보강
- focused service contract와 compile 검증

## Out Of Scope

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- full execution simulator
- slippage / market-impact simulator

## Expected Output

- Backtest Realism Audit의 `Turnover evidence` row가 `estimated_from_holdings`, `cadence_only`, `missing`을 분리한다.
- turnover estimate가 없으면 cost sensitivity 후속 확인이 필요하다고 표시한다.
- Phase 9-3 net-cost curve proof와 Phase 9-5 cost/slippage sensitivity audit이 읽을 수 있는 compact field가 생긴다.
