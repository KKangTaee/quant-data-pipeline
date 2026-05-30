# Practical Validation Required Module Polish V1 Plan

Status: Implementation complete
Created: 2026-05-30

## 이걸 하는 이유?

Practical Validation의 필수검증 8개는 방향이 맞지만, 화면에서 어떤 검증이 Final Review 이동을 막고 어떤 검증은 Final Review 판단 근거로 넘어가는지 더 분명해야 한다.
이번 작업은 검증 범위를 크게 늘리지 않고, 필수검증 이름 / 설명 / gate effect를 정리해 사용자가 차단 사유와 review 사유를 바로 읽게 만드는 것이다.

## Scope

- `Benchmark Parity` 표시를 `Benchmark / Comparator Parity`로 확장한다.
- 필수검증 row에 `Gate Effect`와 `Gate Reason`을 표시한다.
- Source Integrity와 Data Coverage 설명을 source 자격 vs evidence coverage로 분리한다.
- Stress / Robustness는 최소 실전 stress 근거를 보는 필수검증으로 설명한다.
- Backtest Realism과 Latest Runtime Replay의 next action을 더 직접적으로 만든다.
- 관련 docs와 focused tests를 갱신한다.

## Out Of Scope

- 새 validation module 추가
- 새 provider connector / DB schema 추가
- Final Review 최종 판단 정책 변경
- JSONL registry rewrite 또는 generated artifact commit
