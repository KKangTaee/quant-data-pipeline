# Phase 25 Next Phase Preparation

## 목적

이 문서는 `Phase 25` 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리하기 위한 draft다.

현재는 Phase 25 kickoff 직후 문서다.
Phase 25가 완료되면 실제 결과에 맞춰 다시 갱신한다.

## 현재 handoff 상태

- Phase 25는 방금 시작되었다.
- 현재 고정된 것은 `Real-Money 검증 신호`와 `Pre-Live 운영 점검`의 역할 분리다.
- Pre-Live 후보 저장소는 `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`로 정했다.
- `manage_pre_live_candidate_registry.py` helper로 template / draft-from-current / list / show / append / validate를 지원한다.
- current candidate에서 Pre-Live 기록 초안을 만드는 report/helper workflow는 추가했다.
- 아직 Backtest UI에서 바로 Pre-Live 기록으로 넘기는 dashboard나 버튼은 완성되지 않았다.

## 다음 phase에서 더 중요한 질문

Phase 25가 끝난 뒤에는 다음 질문을 보게 될 가능성이 크다.

1. Pre-Live 운영 기록을 기반으로 deployment readiness를 판단할 수 있는가
2. paper tracking에서 나온 결과를 후보 promotion / demotion에 어떻게 연결할 것인가
3. 실제 투자 분석 요청과 제품 개발 phase를 어떻게 계속 분리해서 관리할 것인가

## 추천 다음 방향

Phase 25가 계획대로 끝나면,
다음 phase는 `Deployment Readiness Review` 또는 `Pre-Live Monitoring Hardening` 성격이 자연스럽다.

다만 이 방향은 Phase 25에서 실제로 무엇을 구현했는지에 따라 달라진다.
현재는 Phase 26을 미리 고정하지 않는다.

## handoff 메모

- Phase 25는 live trading 기능이 아니다.
- Phase 25 결과가 곧바로 투자 승인으로 해석되면 안 된다.
- Phase 25에서 만들 기록은 이후 사용자가 명시적으로 투자 후보 분석을 요청할 때 판단 자료로 쓸 수 있다.
