# Structured Waiver Policy V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

Investability gate가 엄격해지면서 좋은 후보가 provider coverage, benchmark parity, paper observation 같은 보강 가능 gap 때문에 selected route로 가지 못하는 경우가 생길 수 있다.
하지만 waiver를 너무 쉽게 허용하면 `NOT_RUN`이나 proxy evidence가 통과처럼 보이는 문제가 다시 생긴다.

이번 작업은 waiver를 구현하지 않고, 허용 가능한 범위와 저장 경계를 먼저 정한다.

## Scope

- `BLOCK`과 `REVIEW_REQUIRED`의 waiver 가능 여부를 구분한다.
- future waiver가 필요할 때 필요한 구조화 field를 정의한다.
- waiver가 사용자 free-form memo나 자동 승인으로 변질되지 않도록 storage / UI boundary를 문서화한다.
- Roadmap / flow / storage governance / root handoff를 정렬한다.

## Non-Goals

- waiver UI 구현
- selected-route gate 코드 변경
- 새 JSONL registry 생성
- final decision row schema 변경
- broker approval / order / auto rebalance

## Verification Plan

- `git diff --check`
- `find .aiworkspace/note/finance/tasks/active/structured-waiver-policy-v1 -maxdepth 1 -type f | sort`
- no Python compile required unless code changes are introduced
