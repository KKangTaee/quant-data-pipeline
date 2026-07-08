# Backtest Handoff / Policy Signal Action V1-V4 Plan

## 이걸 하는 이유?

Backtest Analysis 결과 화면에서 `2차 실전성 검증 Handoff`와 `검증 신호 · Policy Signals`가 같은 진입 가능 여부와 review count를 반복해서 보여준다. 사용자는 Handoff에서 다음 행동을 결정하고, Policy Signals에서는 그 결정의 근거만 확인해야 한다.

## Scope

- V1: Policy Signals를 evidence-only surface로 낮춘다.
- V2: Streamlit-only 방식으로 Handoff action block을 더 자연스럽게 통합한다.
- V3: React custom component POC를 production path와 분리해서 추가한다.
- V4: React 적용 판단과 durable docs를 정리한다.

## Non-goals

- Streamlit 앱 전체를 React/Next.js로 전환하지 않는다.
- Backtest runtime, strategy math, registry schema, Practical Validation gate semantics를 바꾸지 않는다.
- React POC는 V3/V4에서 production source 등록 버튼을 대체하지 않는다.
