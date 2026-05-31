# Backtest Realism Gate Policy Refinement V1 Plan

Status: Active
Created: 2026-05-29

## 이걸 하는 이유?

Phase 9는 Backtest Realism Audit이 비용, turnover, net cost curve, liquidity, cost / slippage sensitivity gap을 더 엄격히 드러내도록 보강했다.
이제 Final Review selected-route gate가 새 audit row들을 의도한 severity로 읽는지 고정해야 한다.

이 task는 새 저장 기능을 만들지 않고, 기존 investability gate policy가 Backtest Realism row-level evidence를 더 명확히 보여주도록 보강한다.

## Goal

- Backtest Realism Audit의 failing row가 gate policy evidence에도 보이게 한다.
- `BACKTEST_REALISM_NEEDS_INPUT` / `BLOCKED`는 selected-route blocker로 유지한다.
- `BACKTEST_REALISM_REVIEW`는 selected-route review-required로 유지한다.
- cost / slippage sensitivity gap과 liquidity gap이 generic route label 뒤에 묻히지 않게 한다.

## Scope

Included:

- `app/services/backtest_evidence_read_model.py` gate policy read model refinement
- Focused service contract tests
- Phase 9 docs and root handoff sync

Excluded:

- 새 JSONL registry
- user memo / preset persistence
- live approval, broker order, auto rebalance
- waiver persistence
- new validation execution engine
