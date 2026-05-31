# Validation Efficacy Gate Policy Refinement V2 Plan

Status: Complete
Created: 2026-05-29

## 이걸 하는 이유?

Phase 10에서 추가한 walk-forward / OOS / regime split evidence가 Practical Validation의 audit row에만 머물면 Final Review selected-route 판단에서 사용자가 어떤 검증 공백 때문에 선정이 막혔는지 알기 어렵다.
이번 task는 새 저장 기능을 만들지 않고 기존 investability packet / selected-route gate policy 안에서 temporal evidence gap을 blocker 또는 review-required 근거로 드러내는 작업이다.

## Scope

- Validation Efficacy Audit의 failing row를 profile-aware gate policy evidence에 병합한다.
- `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker, `REVIEW`는 hold / re-review 요구로 유지한다.
- walk-forward / OOS / regime row가 `policy_rows`, `blockers`, `review_required`에 포함되는지 service contract로 고정한다.

## Out Of Scope

- 새 JSONL registry
- user memo / preset persistence
- raw validation artifact persistence
- broker order / live approval / auto rebalance
- waiver UI / persistence
