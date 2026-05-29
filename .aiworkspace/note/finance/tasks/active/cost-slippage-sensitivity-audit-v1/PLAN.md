# Cost / Slippage Sensitivity Audit V1 Plan

Status: Active
Created: 2026-05-29

## 이걸 하는 이유?

Phase 9는 백테스트가 실제 투자로 이어질 수 있는지 판단할 때 비용, turnover, liquidity, capacity를 더 엄격하게 보려는 hardening 작업이다.
현재 Backtest Realism Audit은 transaction cost 적용, net cost curve, turnover, liquidity evidence를 읽지만, 단일 비용 bps 가정만으로는 비용 / slippage 변화에 얼마나 취약한지 알 수 없다.

이 task는 새 저장 기능을 만들지 않고 기존 Practical Validation evidence를 읽어 cost / slippage sensitivity 실행 여부와 공백을 Backtest Realism Audit에 명확히 노출한다.

## Goal

- Backtest Realism Audit에 read-only `cost_slippage_sensitivity_contract_v1`을 추가한다.
- explicit cost / slippage sensitivity evidence가 있을 때만 PASS로 본다.
- 일반 robustness sensitivity만 있고 비용 / slippage 축이 없으면 REVIEW로 남긴다.
- 비용 input이나 net cost curve proof 자체가 없으면 NEEDS_INPUT으로 남긴다.
- 새 JSONL registry, memo, preset, raw run artifact, DB schema는 추가하지 않는다.

## Scope

Included:

- `app/services/backtest_realism_audit.py` read model 보강
- focused service contract tests
- Phase 9 task / status / integration docs sync
- durable flow / runtime docs minimal sync

Excluded:

- 새 sensitivity 실행 엔진
- full market impact simulator
- broker order, live approval, auto rebalance
- user memo / preset persistence
- 새 workflow JSONL registry
