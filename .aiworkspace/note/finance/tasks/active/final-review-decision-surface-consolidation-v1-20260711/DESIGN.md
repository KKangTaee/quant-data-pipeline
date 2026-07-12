# Design

## Detail tabs

- tab rail과 panel은 하나의 border shell을 공유한다.
- panel 내부의 중복 tab title은 제거한다.
- score first-read는 종합 판정, 5개 dimension, 핵심 영향과 route 제한만 남긴다.

## REVIEW trace

- 저장된 workspace summary card를 module별 audit row와 연결한다.
- 숫자 기준을 만들지 않고 payload에 존재하는 Current / Target / Evidence / as-of만 정규화한다.
- trace type은 measured / derived / qualitative / missing_contract로 구분한다.

## Experiments

- 현재 점수 개선 예측이 아니라 별도 counterfactual backtest 가설임을 유지한다.
- 적용 가능하거나 조건부인 패턴을 우선하고 사용자 질문을 실험 목적에 연결한다.
- 자동 실행, strategy variant 저장, registry write는 하지 않는다.

## Final decision

- Decision Cockpit read model과 gate policy는 유지한다.
- 독립 cockpit visible surface만 제거하고 현재 상태, blocker 수, 권장 route를 최종 판단 영역에 흡수한다.
- 판단 route, 사유, 저장 CTA는 Python / Streamlit이 계속 소유한다.
- live approval, broker order, auto rebalance 의미를 추가하지 않는다.
