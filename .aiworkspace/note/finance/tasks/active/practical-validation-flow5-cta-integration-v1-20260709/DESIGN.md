# Design

## 현재 구조 진단

- Flow3는 `canSaveAndMove`를 받아 결론과 다음 단계 copy를 보여주지만 버튼은 없다.
- Flow5는 별도 container에서 `검증 결과 저장(기록용)`과 `저장하고 Final Review로 이동` 버튼을 렌더링한다.
- 이 분리는 구현 경계는 안전하지만 사용 흐름상 결론과 행동이 분리되어 보인다.

## 개선 방향

Flow3를 `검증 결론 + 다음 행동` surface로 확장한다.

- Primary action: `저장하고 Final Review로 이동`
- Secondary action: `검증 결과 저장(기록용)`
- Blocked state: primary disabled, Flow4 보강 안내와 blocker count 표시
- Boundary copy: Final Review는 최종 승인 / 주문이 아니라 수익성, 벤치마크, 후보 비교, 모니터링 후보 선정 판단 단계

## UI / Engine Boundary

- React component는 props를 렌더링하고 button click intent만 `Streamlit.setComponentValue`로 전달한다.
- Python은 nonce 중복 소비를 막고 기존 `save_practical_validation_result` / `prepare_final_review_handoff_from_validation`을 호출한다.
- `build_practical_validation_workspace`는 CTA read model만 만든다. gate 계산은 기존 module planner를 그대로 읽는다.

## Tradeoff

Flow3에 버튼이 올라오면 사용 흐름은 명확해진다.
다만 Flow3가 최종 투자 승인처럼 보일 위험이 있으므로 copy에서 `Final Review 이동`과 `audit-only 저장`을 명확히 구분한다.
