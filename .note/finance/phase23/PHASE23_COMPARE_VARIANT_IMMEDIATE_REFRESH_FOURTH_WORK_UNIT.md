# Phase 23 Compare Input Layout And Variant Refresh Fourth Work Unit

## 이 문서는 무엇인가

`Phase 23`의 네 번째 작업 단위 문서다.

이번 작업은 `Compare & Portfolio Builder`에서
Annual / Quarterly variant를 바꿨을 때,
아래 전략별 입력 UI가 즉시 따라 바뀌도록 만들고,
동시에 compare 입력 화면의 구조를 더 자연스럽게 정리한 기록이다.

## 쉽게 말하면

기존 화면은 `Strategy Variants`를 먼저 form 밖으로 빼서
Annual / Quarterly 변경이 즉시 반영되게 만들었다.

하지만 공용 입력인 `Timeframe`, `Option`이 여전히
`Advanced Inputs` 안에 들어 있었고,
전략별 옵션도 form 안쪽에 묶여 있어 화면이 조금 흩어진 느낌이 남아 있었다.

이번 추가 정리는 아래처럼 바꿨다.

- `Start Date`, `End Date`, `Timeframe`, `Option`은 한 곳에 모았다.
- 그 영역 이름은 `Compare Period & Shared Inputs`다.
- `Advanced Inputs` expander / form wrapper는 Compare 화면에서 제거했다.
- 전략별 세부 옵션은 `Strategy-Specific Advanced Inputs`라는 별도 섹션으로 밖에 꺼냈다.
- `Run Strategy Comparison`만 실제 실행 버튼으로 남겼다.

## 왜 필요한가

Phase 23 QA의 핵심은 quarterly가 제품 안에서 annual과 구분되어 재현되는지 확인하는 것이다.

Compare 화면에서 Annual / Quarterly를 바꿨는데 하단 UI가 바로 바뀌지 않거나,
공용 입력과 전략별 입력이 애매하게 섞여 있으면,
사용자는 지금 무엇을 테스트하고 있는지 확신하기 어렵다.

이 문제는 계산 오류는 아니지만 QA UX를 흔든다.
따라서 버튼을 하나 더 추가하는 방식이 아니라,
화면 구조 자체를 자연스럽게 바꾸는 것이 더 맞다.

## 실제로 변경한 것

### 1. Variant 선택은 계속 form 밖에서 즉시 갱신

`Compare & Portfolio Builder`에서 family 전략이 선택되어 있으면
`Strategy Variants` 섹션이 먼저 보인다.

여기서 아래 variant를 고른다.

- `Quality Variant`
- `Value Variant`
- `Quality + Value Variant`

이 섹션은 form 안에 있지 않으므로,
Annual / Quarterly를 바꾸면 Streamlit이 즉시 rerun되고
아래 전략별 입력 UI도 같이 바뀐다.

### 2. 공용 실행 입력을 `Compare Period & Shared Inputs`로 이동

아래 네 가지는 특정 전략 전용 설정이 아니다.
모든 compare 전략이 공유하는 실행 입력이다.

- `Start Date`
- `End Date`
- `Timeframe`
- `Option`

그래서 이제 `Advanced Inputs` 안쪽이 아니라
날짜 입력과 같은 줄의 공용 입력 영역에서 관리한다.

### 3. `Strategy-Specific Advanced Inputs`를 밖으로 분리

전략별 세부 옵션은 별도 섹션으로 보여준다.

예상 차이:

- Annual strict는 `Real-Money Contract`, `Guardrails`까지 보인다.
- Quarterly prototype은 현재 `Overlay`, `Portfolio Handling & Defensive Rules` 중심으로 보인다.
- Quarterly에는 아직 annual-only인 real-money promotion / guardrail UI를 억지로 붙이지 않는다.

### 4. Apply / Refresh 버튼은 만들지 않음

이번 구조에서도 별도 `Apply`나 `Refresh` 버튼을 두지 않았다.

이유는 명확하다.
variant 선택은 “어떤 입력 UI를 보여줄지”를 결정하는 상위 선택이므로,
버튼을 눌러 적용하는 방식보다 선택 즉시 반영되는 방식이 더 자연스럽다.

## UI에서 기대되는 동작

1. `Backtest > Compare & Portfolio Builder`로 간다.
2. `Strategies`에서 `Quality`, `Value`, `Quality + Value` 중 하나 이상을 선택한다.
3. `Strategy Variants`에서 Annual / Quarterly를 바꾼다.
4. `Compare Period & Shared Inputs`에서 기간, `Timeframe`, `Option`을 확인한다.
5. `Strategy-Specific Advanced Inputs`에서 선택된 variant에 맞는 세부 옵션이 즉시 바뀌는지 본다.
6. 값이 맞으면 `Run Strategy Comparison`을 눌러 실제 compare를 실행한다.

## 체크리스트 문구 수정

이번 QA 피드백에서 `Advanced Inputs > Strategy-Specific Advanced Inputs`라는 표현이
새 UI와 맞지 않게 되었다.

따라서 `PHASE23_TEST_CHECKLIST.md`도 실제 화면 위치 기준으로 다시 정리했다.

- `Strategy Variants`
- `Compare Period & Shared Inputs`
- `Strategy-Specific Advanced Inputs`
- quarterly single strategy의 `Data Requirements`
- `Statement Shadow Coverage Preview`
- `Universe Contract`와 `Historical Dynamic PIT Universe` 설명

## 한 줄 정리

Compare 화면은 이제 공용 실행 입력과 전략별 세부 입력이 분리되어 있으며,
Annual / Quarterly variant 변경은 별도 버튼 없이 즉시 하단 UI를 갱신한다.
