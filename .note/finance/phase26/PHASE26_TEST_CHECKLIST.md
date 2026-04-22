# Phase 26 Test Checklist

## 목적

이 checklist는 Phase 26에서 정리한 roadmap / backlog / foundation gap이
사용자가 읽고 다음 phase로 넘어갈 수 있을 만큼 명확한지 확인하기 위한 문서다.

현재는 Phase 26 implementation 완료 후 사용자 QA를 위한 checklist다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- checklist에는 별도 `용어 기준` 섹션을 만들지 않는다.
- 용어 설명이 필요하면 각 체크 항목 안에 `어디서 무엇을 어떻게 확인하는지`를 직접 적는다.

## 1. Phase 26 방향 확인

- 확인 위치:
  - `.note/finance/phase26/PHASE26_FOUNDATION_STABILIZATION_AND_BACKLOG_REBASE_PLAN.md`
  - `.note/finance/phase26/PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
- 체크 항목:
  - [x] Phase 26이 새 전략 구현이나 투자 분석이 아니라 backlog / foundation 정리 phase라는 점이 이해되는지
  - [x] Live Readiness / Final Approval이 Phase 26~30 이후 과제로 분리되어 있는지
  - [x] Phase 27~30의 큰 순서가 데이터 신뢰성 -> 전략 parity -> 후보 검토 -> 포트폴리오 제안으로 읽히는지

## 2. Backlog rebase 확인

- 확인 위치:
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
  - `.note/finance/phase26/PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
- 체크 항목:
  - [x] Phase 8, 9, 12~15, 18이 왜 우선 재분류 대상이었는지 이해되는지
  - [x] 과거 phase의 pending 상태가 현재 blocker인지 future option인지 구분되어 있는지
  - [x] `superseded_by_later_phase`가 "무시"가 아니라 "이후 phase에 흡수됨"이라는 뜻으로 읽히는지
  - [x] Phase 18 remaining structural backlog가 다음 개발 흐름에서 어떻게 다뤄질지 이해되는지

## 3. Foundation gap 확인

- 확인 위치:
  - `.note/finance/phase26/PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`
- 체크 항목:
  - [x] 데이터 / 백테스트 신뢰성 gap이 Phase 27에서 다룰 주제로 정리되어 있는지
  - [x] annual / quarterly / 신규 전략 parity gap이 Phase 28에서 다룰 주제로 정리되어 있는지
  - [x] 후보 검토 workflow gap이 Phase 29에서 다룰 주제로 정리되어 있는지
  - [x] portfolio proposal / pre-live monitoring gap이 Phase 30에서 다룰 주제로 정리되어 있는지

## 4. 문서와 closeout 확인

- 확인 문서:
  - `.note/finance/phase26/PHASE26_CURRENT_CHAPTER_TODO.md`
  - `.note/finance/phase26/PHASE26_COMPLETION_SUMMARY.md`
  - `.note/finance/phase26/PHASE26_NEXT_PHASE_PREPARATION.md`
  - `.note/finance/MASTER_PHASE_ROADMAP.md`
  - `.note/finance/FINANCE_DOC_INDEX.md`
- 체크 항목:
  - [ ] Phase 26 상태가 현재 구현 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] Phase 27로 넘어가기 위한 설명이 충분한지

## 한 줄 판단 기준

이번 checklist는
**새 기능이 많이 생겼는가**가 아니라,
**다음 5개 phase를 흔들리지 않게 진행할 정도로 현재 상태와 backlog가 정리되었는가**
를 확인하는 문서다.
