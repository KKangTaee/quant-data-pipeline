# Construction Risk Gate Policy V1 Plan

Status: Complete
Created: 2026-05-29

## Goal

Phase 11의 11-5로 Construction Risk / Risk Contribution / Component Role Weight audit 결과를 Final Review selected-route gate policy에 연결한다.

이걸 하는 이유?

- Practical Validation에서 construction risk gap을 보여줘도 Final Review selected-route가 이를 무시하면 실전 후보 선정 기준이 약해진다.
- `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker로, `REVIEW`는 선정 전 hold / re-review 근거로 고정해야 한다.
- route label만 보여주면 어떤 row가 문제인지 숨겨지므로 non-PASS row criteria를 gate evidence에 병합해야 한다.

## Scope

- `app/services/backtest_evidence_read_model.py` gate policy read model 업데이트
- Construction Risk / Risk Contribution / Component Role / Weight를 first-class gate policy group으로 추가
- investability packet checks에 세 audit route를 추가
- non-PASS audit row criteria를 gate policy evidence에 병합
- focused service contract tests 추가

## Out Of Scope

- 새 JSONL registry
- user memo / preset persistence
- raw holdings / return matrix artifact 저장
- broker order / live approval / auto rebalance
- waiver persistence
- optimizer replacement

## Completion Criteria

- 세 audit이 모두 ready면 selected-route는 기존 조건과 함께 열릴 수 있다.
- 세 audit 중 `NEEDS_INPUT` 또는 `BLOCKED`가 있으면 selected-route는 blocked가 된다.
- 세 audit 중 `REVIEW`가 있으면 selected-route는 hold / re-review가 필요하다.
- gate policy evidence가 generic route가 아니라 failing criteria 이름을 포함한다.
