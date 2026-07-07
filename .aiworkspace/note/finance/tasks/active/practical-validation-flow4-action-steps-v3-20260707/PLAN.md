# Practical Validation Flow4 Action Steps V3 Plan

Status: Completed
Date: 2026-07-07

## 이걸 하는 이유?

Flow 4 `검증 기준 상세`의 `해결 방법`이 row별 Next Action을 한 문장에 이어 붙인 형태로 보이면, 사용자는 무엇을 먼저 처리하고 어떤 후속 확인을 해야 하는지 다시 해석해야 한다.

목표는 `해결 방법`을 단일 문단이 아니라 번호형 실행 단계로 보여주어, 부족 항목 확인 -> 보강 위치 / 실행 -> 재검증 확인 흐름을 카드 안에서 바로 읽게 하는 것이다.

## Scope

- `resolution_guide`에 UI용 `action_steps` list를 추가한다.
- Flow 4 criteria card는 `action_steps`가 있으면 번호 목록으로 렌더링한다.
- Data Coverage, Validation Efficacy, Latest Replay 등 주요 기준의 action guide를 구체 단계로 정리한다.
- 기존 gate policy, replay execution, provider ingestion, registry / saved JSONL persistence는 변경하지 않는다.

## Completion Criteria

- Flow 4 `해결 방법`이 긴 slash-joined 문단 대신 단계 목록으로 보인다.
- audit row의 non-PASS `Next Action`은 구체 action step으로 우선 반영된다.
- 서비스 계약 테스트와 py_compile을 통과한다.
- Browser QA에서 Flow 4 카드의 단계형 해결 방법이 보인다.
