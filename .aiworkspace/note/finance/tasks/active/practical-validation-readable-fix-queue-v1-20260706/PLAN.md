# Practical Validation Readable Fix Queue V1 Plan

## 이걸 하는 이유?

Flow 3 / Flow 4 구조는 좋아졌지만 `NEEDS_INPUT row`, `Validation Efficacy Audit`, `walk-forward / OOS / regime` 같은 내부 용어가 먼저 보여 사용자가 무엇을 검증했고 무엇을 해야 하는지 파악하기 어렵다.
이번 작업은 gate 계산을 바꾸지 않고, 같은 evidence를 사용자 언어로 번역해 행동 가능한 카드로 보여준다.

## Scope

- Flow 3 `먼저 해결할 일`을 `무엇을 검증했나 / 부족한 점 / 해야 할 일 / 왜 중요한가` 구조로 바꾼다.
- `NEEDS_INPUT`은 메인 문구가 아니라 `근거 보강 필요`의 기술 상태 tag로 낮춘다.
- Flow 3 / Flow 4의 `Final Review 이동 기준` 표현을 `Final Review로 넘기기 전 확인 기준` 중심으로 바꾼다.
- validation threshold, replay execution, provider collection, registry / saved JSONL, Final Review persistence는 변경하지 않는다.

## Steps

1. RED tests for user-language fix queue / criteria cards.
2. Add user-facing explanation fields to Practical Validation workspace read model.
3. Update Flow 3 React Fix Queue display.
4. Update Flow 4 criteria board copy and rows.
5. Rebuild React bundle, run focused tests, Browser QA, docs sync, commit.
