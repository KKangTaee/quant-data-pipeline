# Phase 23 Next Phase Preparation

## 목적

이 문서는 `Phase 23` 이후 `Phase 24`로 넘어갈 때 바로 읽기 위한 handoff 문서다.

## 현재 handoff 상태

Phase 23에서 다음이 고정되었다.

- quarterly strict family는 실행 / compare / history / saved replay 재현성을 제품 기능 수준으로 끌어올렸다.
- Compare 화면은 공용 실행 입력과 strategy-specific 입력을 나누는 구조로 정리되었다.
- Annual / Quarterly variant 선택은 각 strategy box 안에서 즉시 하단 입력 UI를 바꾸는 구조가 되었다.
- quarterly portfolio handling contract는 result bundle, history record, history payload, saved portfolio override까지 보존된다.
- quarterly real-money contract / guardrails parity는 future backlog로 분리했다.

## 다음 phase에서 더 중요한 질문

1. `quant-research` 전략 문서를 finance 구현 후보로 가져올 때 어떤 기준으로 고를 것인가
2. 새 전략을 추가할 때 single / compare / history / saved replay까지 최소 어디까지 붙일 것인가
3. 첫 신규 전략은 가격 데이터만으로 구현 가능한 ETF 전략부터 열 것인가, 아니면 더 어려운 event / option / accounting 전략을 바로 열 것인가

## 추천 다음 방향

기본 다음 방향은 `Phase 24 New Strategy Expansion And Research Implementation Bridge`다.

이유는 단순하다.
cadence와 compare 구조가 어느 정도 정리되었으므로,
이제 Value / Quality 중심에서 벗어나 새 전략 family를 추가하는 표준 경로를 만들 수 있다.

## handoff 메모

- Phase 24도 기본은 개발 phase다.
- 새 전략의 성과가 좋아 보여도 자동으로 투자 후보로 승격하지 않는다.
- 사용자가 특정 전략 분석을 명시적으로 요청하면 그때는 `사용자 요청 분석`으로 분리한다.
- 첫 구현 후보는 데이터 요구가 단순하고 현재 DB 가격 loader로 검증 가능한 전략이 우선이다.
