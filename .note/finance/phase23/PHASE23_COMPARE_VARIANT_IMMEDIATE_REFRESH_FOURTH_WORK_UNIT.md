# Phase 23 Compare Variant Immediate Refresh Fourth Work Unit

## 이 문서는 무엇인가

`Phase 23`의 네 번째 작업 단위 문서다.

이번 작업은 `Compare & Portfolio Builder`에서 `Quality / Value / Quality + Value`의
Annual / Quarterly variant를 바꿨을 때,
아래 strategy-specific 입력 UI가 즉시 따라 바뀌도록 정리한 기록이다.

## 쉽게 말하면

기존 화면에서는 `Variant` 선택이 compare 실행 form 안에 있었다.

Streamlit form 안의 widget은 사용자가 값을 바꿔도 바로 앱을 다시 그리지 않고,
submit 버튼을 누를 때 한꺼번에 반영되는 성격이 있다.

그래서 사용자가 `Annual -> Quarterly`로 바꿔도,
일부 설명은 바뀐 것처럼 보이는데 아래 advanced option 박스는 아직 annual처럼 남아 있는 어색한 상태가 생겼다.

이번 작업은 버튼을 추가하지 않고,
variant 선택만 form 밖으로 빼서 선택 즉시 아래 입력 UI가 바뀌게 만든 것이다.

## 왜 필요한가

Phase 23 QA의 핵심은 quarterly가 제품 안에서 annual과 구분되어 재현되는지 확인하는 것이다.

그런데 Compare 화면에서 variant를 바꿨는데 UI가 바로 바뀌지 않으면,
사용자는 지금 annual을 테스트하는지 quarterly를 테스트하는지 확신하기 어렵다.

이 문제는 계산 오류는 아니지만 QA UX를 크게 흔든다.

## 실제로 변경한 것

### 1. Variant 선택을 form 밖으로 이동

`Compare & Portfolio Builder`에서 family 전략이 선택되어 있으면
`Strategy Variants` 섹션이 먼저 보인다.

여기서 아래 variant를 고른다.

- `Quality Variant`
- `Value Variant`
- `Quality + Value Variant`

이 섹션은 `st.form()` 밖에 있으므로,
Annual / Quarterly를 바꾸면 Streamlit이 즉시 rerun되고 아래 입력 UI도 같이 바뀐다.

### 2. Advanced Inputs 안쪽은 현재 variant의 세부 입력만 표시

`Advanced Inputs > Strategy-Specific Advanced Inputs` 안에서는
더 이상 variant를 고르지 않는다.

대신 위에서 선택한 variant 이름을 보여주고,
그 variant에 맞는 상세 옵션만 표시한다.

### 3. 버튼 방식은 사용하지 않음

이전처럼 `Apply`나 `Refresh` 버튼을 두지 않았다.

이유는 명확하다.
variant 선택은 “어떤 입력 UI를 보여줄지”를 결정하는 상위 선택이므로,
별도 버튼 없이 즉시 반영되는 것이 더 자연스럽다.

## UI에서 기대되는 동작

1. `Backtest > Compare & Portfolio Builder`로 간다.
2. `Strategies`에서 `Quality`, `Value`, `Quality + Value` 중 하나 이상을 선택한다.
3. `Strategy Variants` 섹션에서 Annual / Quarterly를 바꾼다.
4. 아래 `Advanced Inputs > Strategy-Specific Advanced Inputs`를 보면 해당 variant에 맞는 입력 섹션이 즉시 바뀐다.

예상 차이:

- Annual strict는 `Real-Money Contract`, `Guardrails`까지 보인다.
- Quarterly prototype은 현재 `Overlay`, `Portfolio Handling & Defensive Rules` 중심으로 보이고,
  real-money promotion / annual guardrail UI는 아직 붙이지 않는다.

## 체크리스트 문구 수정

이번 QA 피드백에서 `annual strict와 다른 입력 또는 제한`,
`factor timing / PIT / coverage 관련 경고`라는 표현이 너무 추상적이라는 점도 확인했다.

따라서 `PHASE23_TEST_CHECKLIST.md`를 화면 위치 기준으로 다시 정리했다.

- quarterly single strategy의 `Data Requirements`
- `Statement Shadow Coverage Preview`
- `Universe Contract`와 `Historical Dynamic PIT Universe` 설명
- compare 화면의 `Strategy Variants`

위 위치를 기준으로 사용자가 무엇을 확인하면 되는지 더 직접적으로 적었다.

## 한 줄 정리

Compare 화면의 Annual / Quarterly variant 선택은 이제 버튼 없이 즉시 아래 입력 UI를 갱신하며,
Phase 23 checklist도 실제 화면 위치 기준으로 다시 읽을 수 있게 정리했다.
