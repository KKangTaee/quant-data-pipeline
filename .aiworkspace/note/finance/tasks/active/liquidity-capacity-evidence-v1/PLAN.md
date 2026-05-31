# Liquidity Capacity Evidence V1

Status: Active
Created: 2026-05-29
Phase: Phase 9 Cost / Slippage / Liquidity Realism

## 이걸 하는 이유?

Phase 9-1~9-3은 거래비용 가정, turnover evidence, net cost curve 적용 증거를 분리했다.
이 task는 다음 단계로, Backtest Realism Audit이 ETF liquidity / capacity evidence를 단순 `PASS` 문자열이 아니라 DB-backed provider snapshot의 coverage, freshness, source strength, compact capacity metrics로 판단하게 한다.

## Scope

- provider operability context에 compact capacity metrics 추가
- Backtest Realism Audit에 `liquidity_capacity_contract_v1` read model 추가
- fresh official provider evidence와 stale / partial / bridge / missing evidence를 분리
- 기존 Practical Validation provider context / Backtest Realism Audit 경계 안에서만 반영
- focused service contract test 추가

## Out Of Scope

- 새 JSONL registry
- user memo / preset persistence
- UI direct provider fetch
- broker order / live approval / auto rebalance
- market impact simulator
- 새 DB table 또는 schema 변경

## Expected Output

- `Liquidity / operability evidence` row가 fresh official capacity evidence만 PASS 후보로 본다.
- stale / unknown freshness, partial coverage, bridge/proxy-only, legacy PASS flag는 REVIEW 또는 NEEDS_INPUT으로 남긴다.
- compact capacity metrics는 Practical Validation result / Backtest Realism Audit에서 읽을 수 있지만 raw provider row는 DB에만 남는다.
