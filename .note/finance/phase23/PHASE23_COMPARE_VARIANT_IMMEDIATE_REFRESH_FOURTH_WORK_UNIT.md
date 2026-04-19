# Phase 23 Compare Strategy Box Layout And Variant Refresh Fourth Work Unit

## 이 문서는 무엇인가

`Phase 23`의 네 번째 작업 단위 문서다.

이번 작업은 `Compare & Portfolio Builder`에서
Annual / Quarterly variant를 바꿨을 때,
각 전략 박스 안의 입력 UI가 즉시 따라 바뀌도록 만들고,
compare 입력 화면의 구조를 더 자연스럽게 정리한 기록이다.

## 쉽게 말하면

처음에는 Annual / Quarterly variant 선택을 별도 `Strategy Variants` 섹션으로 밖에 빼서
즉시 갱신 문제를 해결했다.

하지만 사용자가 보기에는 variant 선택과 실제 전략 입력이 떨어져 있어
화면이 분산되어 보였다.

그래서 최종 구조는 아래처럼 바꿨다.

- `Start Date`, `End Date`, `Timeframe`, `Option`은 한 곳에 모았다.
- 그 영역 이름은 `Compare Period & Shared Inputs`다.
- `Strategy Variants`라는 별도 상단 섹션은 없앴다.
- `Quality`, `Value`, `Quality + Value` variant 선택은 각 전략 박스 안에 넣었다.
- 전략별 최상위 접기/펼치기는 없애고, 각 전략을 border box로 구분했다.
- `Overlay`, `Portfolio Handling & Defensive Rules`, `Real-Money Contract`, `Guardrails` 같은 하위 세부 그룹은 기존처럼 접기/펼치기로 유지했다.
- `Run Strategy Comparison`만 실제 실행 버튼으로 남겼다.

## 왜 필요한가

Phase 23 QA의 핵심은 quarterly가 제품 안에서 annual과 구분되어 재현되는지 확인하는 것이다.

Compare 화면에서 Annual / Quarterly를 바꿨는데 하단 UI가 바로 바뀌지 않거나,
variant 선택과 실제 전략 설정이 서로 떨어져 있으면,
사용자는 지금 무엇을 테스트하고 있는지 확신하기 어렵다.

이 문제는 계산 오류는 아니지만 QA UX를 흔든다.
따라서 버튼을 하나 더 추가하는 방식이 아니라,
전략 단위 박스 안에서 “variant 선택 -> 해당 variant 세부 입력”이 바로 이어지는 구조가 더 맞다.

## 실제로 변경한 것

### 1. 공용 실행 입력을 `Compare Period & Shared Inputs`로 이동

아래 네 가지는 특정 전략 전용 설정이 아니다.
모든 compare 전략이 공유하는 실행 입력이다.

- `Start Date`
- `End Date`
- `Timeframe`
- `Option`

그래서 `Advanced Inputs` 안쪽이 아니라
날짜 입력과 같은 공용 입력 영역에서 관리한다.

### 2. 전략별 최상위 expander를 box로 변경

아래 전략들은 선택되면 각각 border box로 표시된다.

- `Equal Weight`
- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`
- `Quality`
- `Value`
- `Quality + Value`

전략 자체를 접어 숨기는 구조가 아니라,
화면에서 바로 보이는 박스로 구분한다.

### 3. Annual / Quarterly variant 선택을 각 family box 안으로 이동

`Quality`, `Value`, `Quality + Value`는 각 박스 안에서 variant를 고른다.

예시:

- `Quality` 박스 안에서 `Quality Variant` 선택
- 선택된 variant가 `Quality Snapshot (Strict Annual)`이면 annual strict 입력 표시
- 선택된 variant가 `Quality Snapshot (Strict Quarterly Prototype)`이면 quarterly prototype 입력 표시

이 구조에서는 variant 선택과 실제 입력이 한 박스 안에 있으므로,
사용자가 “내가 지금 어떤 전략 variant를 설정하고 있는지”를 더 쉽게 따라갈 수 있다.

### 4. 하위 세부 그룹은 기존 접기/펼치기 유지

전략 안의 세부 그룹은 그대로 접기/펼치기로 둔다.

예시:

- `Overlay`
- `Portfolio Handling & Defensive Rules`
- `Real-Money Contract`
- `Guardrails`
- `Risk-Off Overlay`
- `ETF Guardrails`

즉 최상위 전략 구분은 box,
전략 안의 세부 설정 묶음은 기존 expander 구조다.

### 5. Apply / Refresh 버튼은 만들지 않음

이번 구조에서도 별도 `Apply`나 `Refresh` 버튼을 두지 않았다.

variant 선택은 “어떤 입력 UI를 보여줄지”를 결정하는 상위 선택이므로,
버튼을 눌러 적용하는 방식보다 선택 즉시 반영되는 방식이 더 자연스럽다.

## UI에서 기대되는 동작

1. `Backtest > Compare & Portfolio Builder`로 간다.
2. `Strategies`에서 원하는 전략을 선택한다.
3. `Compare Period & Shared Inputs`에서 기간, `Timeframe`, `Option`을 확인한다.
4. `Strategy-Specific Advanced Inputs` 아래에서 각 전략이 box로 구분되어 보이는지 확인한다.
5. `Quality`, `Value`, `Quality + Value` 박스 안에서 Annual / Quarterly variant를 바꾼다.
6. 같은 박스 안의 세부 입력이 선택한 variant에 맞게 즉시 바뀌는지 본다.
7. 값이 맞으면 `Run Strategy Comparison`을 눌러 실제 compare를 실행한다.

## 체크리스트 문구 수정

이번 QA 피드백에 따라 `PHASE23_TEST_CHECKLIST.md`도 실제 화면 위치 기준으로 다시 정리했다.

- `Compare Period & Shared Inputs`
- `Strategy-Specific Advanced Inputs`
- 각 전략별 border box
- 각 family box 안의 Annual / Quarterly variant selector
- 하위 `Overlay`, `Portfolio Handling & Defensive Rules`, `Real-Money Contract`, `Guardrails`

## 한 줄 정리

Compare 화면은 이제 공용 실행 입력과 전략별 박스가 분리되어 있으며,
Annual / Quarterly variant 선택은 각 전략 박스 안에서 즉시 해당 세부 입력을 갱신한다.
