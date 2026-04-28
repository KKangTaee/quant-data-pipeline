# Phase 30 Test Checklist

## 목적

이 checklist는 Phase 30에서 만드는 product-flow 재정렬,
리팩토링 경계 검토, 이후 Portfolio Proposal / Pre-Live Monitoring surface가
사용자가 이해할 수 있는 흐름으로 연결되는지 확인하기 위한 문서다.

현재는 Phase 30 첫 작업 단위 QA checklist 초안이다.
첫 작업은 기능 구현이 아니라 사용 흐름과 코드 경계 정리다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 완료된 뒤 다음 작업 단위로 넘어간다.
- checklist에는 별도 `용어 기준` 섹션을 만들지 않는다.
- 용어 설명이 필요하면 각 체크 항목 안에 `어디서 무엇을 어떻게 확인하는지`를 직접 적는다.

## 1. Guide 흐름 확인

- 확인 위치:
  - `Guides > 테스트에서 상용화 후보 검토까지 사용하는 흐름`
- 체크 항목:
  - [ ] 1~5단계가 데이터 최신화, Single Strategy, Real-Money, Hold 해결, Compare로 이어지는 테스트 / 검증 구간으로 읽히는지
  - [ ] 6~10단계가 Phase 29 기능 나열이 아니라 후보 초안, 판단 기록, 후보 저장, 운영 관찰로 이어지는 후보 검토 / 운영 기록 구간으로 읽히는지
  - [ ] `Candidate Draft`가 좋은 백테스트 결과를 바로 후보 registry에 넣는 것이 아니라 저장 전 초안으로 설명되는지
  - [ ] `Candidate Review Note`가 사람의 판단과 다음 행동을 남기는 기록으로 설명되는지
  - [ ] `Current Candidate Registry`가 후보 저장소이지 투자 승인 저장소가 아니라고 읽히는지
  - [ ] `Pre-Live Review`가 live trading 승인 전 paper / watchlist / hold 운영 기록으로 설명되는지
  - [ ] `Portfolio Proposal`이 Phase 30 이후 후보 묶음 제안이며 투자 승인과 구분되는지

## 2. 리팩토링 경계 확인

- 확인 위치:
  - `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
  - `.note/finance/phase30/PHASE30_PRODUCT_FLOW_REORIENTATION_AND_BACKTEST_REFACTOR_BOUNDARY_FIRST_WORK_UNIT.md`
- 체크 항목:
  - [ ] `backtest.py`가 왜 커졌는지 주요 책임 묶음이 이해되는지
  - [ ] Candidate Review / Pre-Live / registry helper가 먼저 분리 후보로 잡힌 이유가 이해되는지
  - [ ] Strategy forms를 가장 나중에 분리하자는 판단이 안전하게 느껴지는지
  - [ ] 실제 리팩토링이 아직 시작되지 않았고, 이번 작업은 경계 검토라는 점이 분명한지

## 3. Phase 30 문서 확인

- 확인 문서:
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_AND_PRE_LIVE_MONITORING_SURFACE_PLAN.md`
  - `.note/finance/phase30/PHASE30_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 30이 active 상태지만 아직 portfolio proposal 기능 구현 단계는 아니라고 읽히는지
  - [ ] 첫 작업이 사용 흐름 재정렬과 리팩토링 경계 검토로 설명되는지
  - [ ] 다음 작업 후보가 실제 모듈 분리 또는 Portfolio Proposal 계약 정의로 이어지는지

## 4. Portfolio Proposal 계약 확인

- 확인 문서:
  - `.note/finance/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`
- 체크 항목:
  - [ ] Portfolio Proposal이 단순 saved portfolio나 weighted result가 아니라 후보 묶음 제안으로 설명되는지
  - [ ] proposal row에 목적, 후보 역할, 비중 근거, risk constraints, evidence snapshot, blocker, operator decision이 필요하다는 점이 이해되는지
  - [ ] `core_anchor`, `diversifier`, `defensive_sleeve`, `satellite`, `watch_only` 같은 후보 역할이 포트폴리오 안에서 왜 필요한지 이해되는지
  - [ ] `manual_weight` 또는 `equal_weight`로 먼저 시작하고 optimizer는 당장 제외한다는 판단이 안전하게 느껴지는지
  - [ ] `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`는 향후 저장소 후보일 뿐, 이번 작업에서 파일 생성이나 저장 구현이 된 것은 아니라고 읽히는지
  - [ ] Proposal lifecycle이 draft / review_ready / paper_tracking / hold / rejected / superseded / live_readiness_candidate로 구분되고, live approval과 분리되는지

## 한 줄 판단 기준

이번 Phase 30 중간 QA는
**새 기능이 생겼는가**가 아니라,
**Phase 29 이후 흐름과 Portfolio Proposal 계약을 사용자가 이해하고, 다음 리팩토링 / UI 구현 경계를 납득할 수 있는가**
를 확인한다.
