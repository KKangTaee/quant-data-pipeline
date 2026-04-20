# Phase 24 Next Phase Preparation

## 목적

이 문서는 `Phase 24` 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리하기 위한 handoff 문서다.

현재는 Phase 24 practical closeout 단계의 handoff로 읽는다.

## 현재 handoff 상태

- 아직 Phase 24는 manual validation completed 상태가 아니다.
- 첫 신규 전략 `Global Relative Strength`는 core/runtime smoke와
  UI catalog, single strategy, compare, history, saved replay 연결까지 완료했다.
- 따라서 지금은 Phase 25로 넘어가기 전에 `PHASE24_TEST_CHECKLIST.md`로 사용자 QA를 먼저 진행하는 것이 맞다.

## 다음 phase에서 더 중요한 질문

1. 새 전략 확장 경로가 충분히 안정되었는가
2. 추가 전략을 더 붙일 것인가, 아니면 pre-live readiness로 넘어갈 것인가
3. quarterly real-money / guardrail parity를 Phase 25 전후에 열어야 하는가

## 추천 다음 방향

현재 roadmap 기준으로 Phase 24 이후 기본 방향은 `Phase 25 Pre-Live Operating System And Deployment Readiness`다.

다만 Phase 24에서 신규 전략 구현 경로가 충분히 검증되지 않으면,
Phase 25로 바로 넘어가기보다 Phase 24 안에서 한 번 더 implementation hardening을 진행한다.

현재 판단:

- `Global Relative Strength`는 제품 UI와 재진입 흐름까지 연결된 상태다.
- 다음 작업은 사용자가 single / compare / history / saved replay 체크리스트를 실제 화면에서 확인하는 것이다.
- 그 manual QA가 끝난 뒤에 Phase 25 진입 여부를 판단한다.

## handoff 메모

- Phase 25는 live trading이 아니라 paper / review / pre-live readiness 운영 체계다.
- Phase 24 결과가 투자 추천으로 자동 변환되지 않게 유지한다.
