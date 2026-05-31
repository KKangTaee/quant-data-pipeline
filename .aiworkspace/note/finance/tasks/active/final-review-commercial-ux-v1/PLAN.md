# Final Review Commercial UX V1

Status: Active
Started: 2026-05-31

## 이걸 하는 이유?

Final Review는 Candidate Board, Decision Cockpit, Decision Record, Saved Decision Review, Selected Dashboard Handoff까지 갖췄지만 화면 경험은 아직 개발자용에 가깝다.
사용자는 긴 table과 내부 route label보다 "오늘 어떤 후보를 보고, 어떤 결정을 내려야 하는지"를 먼저 이해해야 한다.

이 작업은 판단 로직을 바꾸지 않고, Final Review를 사용자용 decision desk처럼 읽히도록 화면 위계와 시각 컴포넌트를 개편한다.

## Scope

- Final Review 전용 visual component module 추가
- Final Review 상단 command center / workflow rail 추가
- Candidate Board를 lane / card 중심으로 보강
- Decision Cockpit을 Must Fix / Must Review / Monitoring Seed 중심의 판단 카드로 보강
- Final Decision Record를 action panel로 강조
- Evidence Appendix / Saved Decision / Handoff는 상세 확인 영역으로 낮추되 기존 기능 유지
- 관련 docs / task logs 업데이트

## Out Of Scope

- selected-route gate, validation score, candidate priority 로직 변경
- Practical Validation / Selected Dashboard 저장 schema 변경
- provider / FRED fetch 추가
- live approval, broker order, account sync, auto rebalance
- 새 외부 dependency 추가

## Done Criteria

- Final Review 진입 시 현재 후보 상태와 다음 행동을 command center에서 바로 읽을 수 있다.
- Candidate Board와 Decision Cockpit이 table보다 먼저 decision-oriented card/lane으로 보인다.
- 최종 판단 기록 영역이 명확한 primary action panel로 보인다.
- 기존 save / dossier / appendix / handoff 기능이 유지된다.
- py_compile, service contracts, diff check, Browser QA를 통과하고 commit된다.
