# Phase 31 Next Phase Preparation

## 목적

이 문서는 Phase 31 이후 어떤 질문으로 Phase 32를 여는 것이 자연스러운지 정리하는 handoff 초안이다.

현재 Phase 31은 implementation_complete / manual_qa_pending 상태다.
사용자 QA가 완료되면 이 문서를 기준으로 Phase 32 방향을 확정한다.

## 현재 handoff 상태

- Phase 30은 Portfolio Proposal / Monitoring Review / Pre-Live Feedback / Paper Tracking Feedback을 구현했고 manual QA pending 상태다.
- Phase 31은 Portfolio Proposal 이후 같은 판단 기록을 중복 저장하지 않고, portfolio risk / live readiness validation pack을 구현했다.
- 단일 후보 또는 proposal draft는 `READY_FOR_ROBUSTNESS_REVIEW`, `PAPER_TRACKING_REQUIRED`, `NEEDS_PORTFOLIO_RISK_REVIEW`, `BLOCKED_FOR_LIVE_READINESS` 중 하나로 읽힌다.
- Phase 31 validation pack은 live approval이 아니라, Phase 32 robustness 검증에 넘길 수 있는지 판단하는 입력 정리다.

## 다음 phase에서 더 중요한 질문

1. Phase 31 validation을 통과한 후보나 proposal이 특정 기간 / benchmark / parameter에만 의존한 결과인지 어떻게 검증할 것인가
2. stress window, 최근 구간, benchmark 변경, guardrail 민감도 같은 robustness 결과를 어떤 summary로 보여줄 것인가
3. robustness 결과가 paper tracking 또는 final selection으로 넘어갈 때 어떤 blocker와 next action을 남겨야 하는가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase 32는 Phase 31에서 구조적으로 괜찮다고 본 후보가 정말 버티는 후보인지 확인하는 단계다.
- 좋은 CAGR/MDD 하나만 보는 것이 아니라, 기간과 조건이 조금 달라져도 후보가 완전히 무너지지 않는지 본다.

주요 작업:

1. Robustness input 정의
   - Phase 31 validation pack이 넘겨주는 candidate/proposal과 설정 snapshot을 읽는다.
2. Stress / sensitivity summary
   - 기간 분할, benchmark 변경, parameter sensitivity, 최근 구간, guardrail trigger 안정성을 요약한다.
3. Robustness blocker / next action
   - paper tracking으로 넘길 수 있는지, 보강 검증이 필요한지, 차단해야 하는지 표시한다.

## 추천 다음 방향

Phase 32는 `Robustness And Stress Validation Pack`으로 여는 것이 자연스럽다.
Phase 31이 포트폴리오 구조 위험을 보는 단계라면,
Phase 32는 그 구조가 다른 조건에서도 버틸 수 있는지 보는 단계다.

## handoff 메모

- Phase 31은 live approval이 아니다.
- Phase 32도 live approval이 아니라 robustness 검증이다.
- 실제 paper ledger는 Phase 33에서 다룬다.
- 최종 선정 decision pack은 Phase 34에서 다룬다.
- Phase 31 QA가 완료되기 전에는 Phase 32를 바로 열지 않는다.
