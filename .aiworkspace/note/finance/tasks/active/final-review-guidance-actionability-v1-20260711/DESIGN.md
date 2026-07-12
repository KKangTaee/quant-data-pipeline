# Design

## Boundary

- Python service가 패턴 적용 여부, evidence 정규화, 상태, 사용자 문장과 stage ownership을 결정한다.
- React는 전달된 read model을 순서와 시각 계층에 맞게 표시한다.
- Final Review는 저장된 Practical Validation evidence를 재해석하며 provider fetch나 검증 재실행을 하지 않는다.

## Pattern contract

- 상태: `actionable`, `conditional`, `needs_validation`, `not_applicable`
- 첫 화면: 후보 구성에 적용되며 저장 evidence가 있는 패턴만 표시한다.
- 카드: 현재 진단, 의미, 변화 조건, 다음 행동을 제공한다.
- 기술 trace: 사용자 source label과 내부 technical path를 분리해 접힌 상세 정보에서 표시한다.

## Stage ownership

- Final Review 직접 판단: 최종 판단 참고, Monitoring 추적, blocker
- Level2 인수 제한사항: 데이터 주의, 2단계 실용성 주의는 점수/신뢰도에 반영된 제한사항으로 요약한다.
- Level2의 Flow4 보강/수집 문구는 Final Review 행동으로 전달하지 않는다.

## Interpretation

- 총평 바로 다음에 성과 해석, 위험 해석, 근거 신뢰도, Monitoring 적합성 네 행을 배치한다.
- 내부 route/module id 대신 사용자가 판단에 사용할 수 있는 한국어 문장을 제공한다.
