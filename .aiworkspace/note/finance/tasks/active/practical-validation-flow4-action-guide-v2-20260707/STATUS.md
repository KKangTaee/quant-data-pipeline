# Practical Validation Flow4 Action Guide V2

Status: Completed
Date: 2026-07-07

## Purpose

Flow 4 criteria card의 `부족한 것 / 해야 할 일 / 보강 위치`가 각각 분리되어 있어 사용자가 실제로 무엇을 실행하면 통과되는지 한 번에 판단하기 어려웠다.

## Completed

- Flow 4 `resolution_guide`에 `통과 기준`을 추가했다.
- Criteria card guide를 `검증한 것 / 해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치`로 재구성했다.
- Audit row의 non-PASS `Criteria`와 `Next Action`은 계속 우선 사용하되, 위치는 해결 방법의 보조 정보로 낮췄다.
- Data Coverage 같은 provider 보강 항목은 실행 위치와 통과 기준을 함께 보여준다.

## Out Of Scope

- validation threshold 변경
- replay 실행 로직 변경
- provider ingestion orchestration 변경
- registry / saved JSONL rewrite
- Final Review selected-route policy 변경
- live approval / broker order / auto rebalance 의미 추가
