# Design

Status: Approved
Date: 2026-07-19

## User Problem

`고급 설정과 원본 근거`가 판정 설정, replay 기간 선택, 후보 근거, raw JSON을 한데 묶어 각 요소의 역할과 사용 시점을 알기 어렵다. 결과에 영향을 주는 설정이 Level2의 마지막에 숨어 있고 `상세 검증 근거`와 원본 감사 데이터의 차이도 흐리다.

## Considered Options

1. 이름만 변경: 변경량은 작지만 설정/근거 혼합과 행동 순서 문제를 남긴다.
2. 설정을 해당 단계로 이동하고 원본만 하단에 유지: 기존 Python 경계와 one-shell을 보존하면서 사용자 흐름을 바로잡는다. **채택.**
3. 설정과 raw evidence를 모두 React로 이관: 시각적 일관성은 높지만 Streamlit raw renderer까지 다시 만들 필요가 있어 과도하다.

## Approved Information Architecture

### Step 1 — 후보와 검증 기준

- 기존 5개 profile preset을 유지한다.
- 그 아래 `판정 기준 세부 조정` disclosure를 둔다.
- 목적, 손실 허용, 운용 기간, 상품 복잡도, 대안 성공 기준을 조정한다.
- 적용 중인 rolling window, MDD review line, 거래비용을 compact summary로 표시한다.
- answer 변경은 replay 계산값을 버리지 않고 validation result만 다시 판정한다.

### Step 2 — 최신 데이터 기준 재검증

- 실행 카드 위에 `재검증 범위`를 둔다.
- `최신 DB 데이터까지 확장 검증`을 기본 권장으로 표시한다.
- `저장 기간 그대로 재현`은 과거 결과 재현 용도로 설명한다.
- mode 변경은 현재 source의 replay/result를 초기화하고 명시적 재실행을 요구한다.

### Step 3 — 상세 검증 근거

- 현재 React category disclosure를 유지한다.
- 사람이 판정 이유를 이해하는 영역이며 raw JSON 영역과 합치지 않는다.

### Bottom Audit Disclosure

- 제목은 `원본 데이터·감사 정보`다.
- `후보 원본`, `재검증 원본`, `판정 원본`으로 나눈다.
- 설정 widget과 write action을 두지 않는다.
- 기본 닫힘 상태이며 판정 재현/오류 확인 목적임을 설명한다.

## State And Safety Contract

- React intent는 canonical option을 다시 보내는 역할만 한다.
- Python은 question id, answer, recheck mode, current source id를 검증한다.
- profile answer 변경은 app rerun으로 context/decision read model을 함께 갱신한다.
- recheck mode 변경은 fragment rerun을 사용하되 해당 source replay/result state를 제거한다.
- source/validation/result registry write는 기존 Step 4 action에서만 가능하다.
- Final Review gate, audit taxonomy, provider action, DB schema는 변경하지 않는다.

## Error Handling

- 알 수 없는 question/answer/mode intent는 state를 변경하지 않고 사용자 notice를 표시한다.
- source가 바뀐 stale intent는 기존 guard로 거부한다.
- replay/result가 없으면 각 원본 tab은 명확한 empty message를 표시한다.

## Acceptance Criteria

1. `고급 설정과 원본 근거` 문구가 current path에서 사라진다.
2. Step 1에 판정 기준 질문과 적용 기준 요약이 있다.
3. Step 2에 재검증 범위 두 옵션과 용도 설명이 있다.
4. profile answer 변경 뒤 read model이 새 answer/threshold를 표시한다.
5. recheck mode 변경 뒤 이전 mode 결과가 current result로 남지 않는다.
6. 하단 disclosure에는 select/radio/button이 없고 세 원본 tab만 있다.
7. React unavailable fallback도 Step 1/2 순서를 유지한다.
8. desktop/760px에서 overflow와 component error가 없다.
9. registry/saved JSONL schema와 validation gate semantics가 바뀌지 않는다.

## Self-Review

- Placeholder: 없음.
- Internal consistency: 설정은 Step 1/2, 해석 근거는 Step 3, raw audit는 하단으로 일관되게 분리했다.
- Scope: Practical Validation UI/state contract에 한정했다.
- Ambiguity: profile answer는 replay를 보존하고 mode 변경은 replay를 무효화하는 것으로 명시했다.
