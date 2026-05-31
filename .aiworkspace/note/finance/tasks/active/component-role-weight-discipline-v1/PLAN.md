# Component Role / Weight Discipline V1 Plan

Status: Complete
Created: 2026-05-29

## Goal

Phase 11의 11-4로 existing component role / target weight / validation profile evidence를 read-only audit contract로 분리한다.

이걸 하는 이유?

- component 비중 합계가 맞아도 각 component가 어떤 역할인지 불분명하면 실전 포트폴리오 구성 근거가 약하다.
- hedge / diversifier / growth / core 역할이 profile 목적과 맞는지 Final Review에서 같은 의미로 읽게 한다.
- role source나 weight discipline 근거가 없으면 `PASS`처럼 보이지 않게 한다.

## Scope

- `app/services/backtest_component_role_weight_audit.py` 추가
- Practical Validation result에 `component_role_weight_audit`와 display rows 연결
- Practical Validation / Final Review 화면에서 audit summary 표시
- Final Review decision snapshot / evidence rows에 audit payload 보존
- focused service contract tests 추가

## Out Of Scope

- 새 role registry / preset / memo persistence
- portfolio optimizer replacement
- selected-route gate policy enforcement
- broker order / live approval / auto rebalance

## Completion Criteria

- explicit role metadata가 있으면 role / weight discipline rows를 표시한다.
- role source가 없거나 partial이면 `PASS`가 아니라 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- profile-aware max weight와 role concentration review line을 적용한다.
- 새 JSONL registry나 user memo 저장을 만들지 않는다.

## Completion Result

- `component_role_weight_audit_v1` is implemented as a read-only service contract.
- Practical Validation and Final Review show the same compact role / weight rows.
- Final Review snapshots and evidence rows preserve the audit without adding role preset, user memo, or saved setup persistence.
