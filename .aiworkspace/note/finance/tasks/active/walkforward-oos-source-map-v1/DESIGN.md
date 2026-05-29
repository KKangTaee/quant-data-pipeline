# Walk-forward / OOS Source Map V1 Design

Status: Complete
Created: 2026-05-29

## Design Decision

Phase 10 구현은 새 저장 체인을 만들기보다, 기존 curve / benchmark / replay / macro evidence를 읽는 compact temporal validation read model부터 만든다.

다음 구현은 `walkforward-split-contract-v1`로 진행한다.
첫 구현 slice는 OOS / regime까지 한 번에 넣지 않고, 재사용 가능한 temporal split helper와 walk-forward evidence row를 먼저 만든다.

## Recommended Implementation Boundary

1. Add a service-level temporal validation helper.
   - Candidate location: `app/services/backtest_temporal_validation.py` or a focused helper beside Practical Validation services.
   - Inputs: normalized portfolio curve, benchmark curve, curve provenance, threshold profile.
   - Output: compact rows with `PASS / REVIEW / NEEDS_INPUT / BLOCKED`, metrics, limitations, and storage boundary.

2. Wire walk-forward evidence into Practical Validation.
   - Candidate caller: `app/services/backtest_practical_validation_diagnostics.py`.
   - Store only compact evidence in the existing validation result payload.

3. Extend Validation Efficacy Audit after the walk-forward row exists.
   - Candidate file: `app/services/backtest_validation_efficacy.py`.
   - `NOT_RUN` / insufficient period / benchmark parity missing should not become pass.

4. Extend Final Review gate policy only after the audit row exists.
   - Candidate file: `app/services/backtest_evidence_read_model.py`.
   - Prefer merging the row through Validation Efficacy first, then decide if a separate `temporal_validation` gate group is necessary.

## Why 10-2 First?

Current runtime already has rolling and OOS metadata, but Practical Validation gate semantics need a reusable, explicit contract before OOS and regime split are added.
Walk-forward is the safest first slice because it can reuse existing normalized curves and does not require new macro source work.

## Storage Boundary

- No new JSONL registry.
- No raw split curve artifact in workflow registry.
- No user memo / preset storage.
- No live approval / broker order / auto rebalance behavior.
- If future regime data needs collection, use DB-backed ingestion and loader path only.
