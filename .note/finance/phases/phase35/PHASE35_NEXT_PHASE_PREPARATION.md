# Phase 35 Next Phase Preparation

## 목적

이 문서는 Phase 35 이후 어떤 방향으로 넘어갈 수 있는지 미리 기록하는 초안이다.

현재 Phase 35는 active / not_ready_for_qa 상태이므로,
이 문서는 구현 중 바뀔 수 있다.

## 현재 handoff 상태

- Phase 34는 complete / manual_qa_completed 상태다.
- Phase 35는 Phase34 final review record 중 selected record를 읽어 운영 가이드를 만드는 phase로 시작했다.
- 아직 Phase35 operating guide 구현은 시작하지 않았다.

## 다음 phase에서 더 중요한 질문

1. Phase35에서 운영 기준이 만들어진 뒤, 실제 live approval / broker order와 어디까지 연결할 것인가?
2. live approval 전에 paper/live monitoring 성과를 자동 계산하거나 추적해야 하는가?
3. 운영 가이드가 깨졌을 때 Candidate Review / Final Review로 되돌리는 route를 어떻게 만들 것인가?

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase36 후보는 Phase35 결과에 따라 달라진다.
- 운영 가이드만으로 충분하면 live approval 경계를 더 자세히 정리할 수 있고,
  자동 성과 추적이 필요하다고 판단되면 paper/live monitoring engine을 먼저 만들 수 있다.

주요 후보:

1. Live Approval Boundary / Execution Readiness
   - 실제 주문 전 승인 절차, operator confirmation, broker/order boundary를 정리한다.
2. Paper / Live Monitoring Result Tracker
   - 운영 가이드 기준으로 실제 추적 성과, 리밸런싱 이벤트, stop / reduce trigger를 기록한다.

## 추천 다음 방향

Phase35가 끝나기 전에는 Phase36 방향을 확정하지 않는다.

왜냐하면 운영 guide를 만들고 나서야
다음 병목이 live approval 계약인지, monitoring tracker인지, 리스크/비용 엔진인지 분명해지기 때문이다.

## handoff 메모

- Phase35 구현 후 이 문서를 다시 갱신한다.
- Phase36을 열기 전에는 Phase35 checklist 완료와 사용자의 방향 승인이 필요하다.
