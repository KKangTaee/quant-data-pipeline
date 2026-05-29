# Validation Efficacy Gate Policy Refinement V2 Design

Status: Complete
Created: 2026-05-29

## Boundary

이 task는 Final Review read model 변경이다.
Practical Validation의 기존 `validation_efficacy_audit` payload와 investability packet의 기존 gate policy snapshot을 재사용한다.

## Implemented Contract

- `build_investability_gate_policy()`가 Validation Efficacy Audit의 non-PASS row를 `validation_efficacy` group으로 병합한다.
- generated `validation_efficacy_audit`도 gate policy build에 전달해, 저장된 audit이 없어도 packet 내부에서 만든 compact audit row가 selected-route policy에 반영된다.
- `Walk-forward temporal validation`, `OOS holdout validation`, `Regime split validation` row는 다른 Validation Efficacy row와 같은 severity rule을 따른다.

## Severity Rule

| Audit row status | Gate result |
| --- | --- |
| `PASS` | policy finding 없음 |
| `REVIEW` | `REVIEW_REQUIRED`; selected route는 hold / re-review 필요 |
| `NEEDS_INPUT` | `BLOCK`; selected route 차단 |
| `BLOCKED` | `BLOCK`; selected route 차단 |

## Storage Boundary

이 변경은 read-only evidence 정렬이다.
새 DB table, JSONL registry, saved setup, memo field, report artifact, order, approval, auto rebalance path를 추가하지 않는다.
