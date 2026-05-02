# Phase 26 Foundation Stabilization And Backlog Rebase Plan

## 이 문서는 무엇인가

이 문서는 Phase 26에서 무엇을 정리하고, 왜 지금 이 정리가 필요한지 설명하는 kickoff 문서다.

Phase 26은 새 전략을 만드는 phase가 아니다.
과거 phase의 pending 상태, 남은 backlog, 현재 제품 foundation의 빈 구간을 다시 정렬해서
Phase 27~30을 흔들리지 않게 진행하기 위한 정리 phase다.

## 목적

1. Phase 25까지 만든 기능과 문서 상태를 기준으로, 과거 phase의 남은 pending / backlog를 다시 분류한다.
2. `지금 꼭 막는 문제`, `후속 phase로 넘길 문제`, `legacy 상태로만 남길 문제`를 구분한다.
3. Phase 27~30의 개발 순서가 데이터 신뢰성, 전략 parity, 후보 검토, 포트폴리오 제안으로 자연스럽게 이어지도록 만든다.

## 쉽게 말하면

지금은 기능이 많이 생겼다.
그런데 예전 phase의 QA pending, practical closeout, backlog 표현이 함께 남아 있어
"지금 무엇이 진짜 다음 blocker인지" 헷갈릴 수 있다.

Phase 26은 새 기능을 크게 붙이기 전에 책상을 한번 정리하는 단계다.
어떤 일은 지금 닫고, 어떤 일은 다음 phase로 넘기고,
어떤 일은 더 이상 중요한 blocker가 아니라고 표시한다.

## 왜 필요한가

- Phase 8, 9, 12~15, 18에는 아직 `manual_qa_pending` 또는 `practical_closeout` 상태가 남아 있다.
- Phase 23~25에서 quarterly, 신규 전략, Pre-Live workflow가 추가되면서 제품 surface가 커졌다.
- 이제부터는 Live Readiness / Final Approval로 바로 가는 것이 아니라,
  그 전에 데이터 신뢰성, 전략 parity, 후보 검토 workflow, 포트폴리오 제안 surface를 순서대로 강화해야 한다.
- 과거 backlog를 먼저 정리하지 않으면 Phase 27 이후 작업이 예전 문서와 충돌하거나, 같은 문제를 반복해서 다시 논의하게 된다.

## 이 phase가 끝나면 좋은 점

- 현재 roadmap에서 "진짜 다음에 해야 할 일"이 더 선명해진다.
- 오래된 pending 상태를 보고 불필요하게 과거 phase로 돌아가는 일이 줄어든다.
- Phase 27의 Data Integrity 작업을 시작할 때, 어떤 데이터 / 백테스트 신뢰성 문제가 우선인지 알 수 있다.
- Live Readiness / Final Approval은 Phase 30 이후 과제로 명확히 미뤄져, 지금 단계에서 투자 승인 흐름과 개발 흐름이 섞이지 않는다.

## 이 phase에서 다루는 대상

- `.note/finance/MASTER_PHASE_ROADMAP.md`
- `.note/finance/FINANCE_DOC_INDEX.md`
- 과거 phase 상태값과 pending QA 표기
- Phase 18 remaining structural backlog
- quarterly / annual / 신규 전략 간 남은 parity gap
- 데이터 신뢰성, 백테스트 preflight, candidate review, portfolio proposal로 이어지는 Phase 27~30 방향

이번 phase에서 직접 다루지 않는 것:

- 새 전략 구현
- deep backtest 후보 탐색
- live trading
- Live Readiness / Final Approval
- 실제 투자 추천 또는 최종 투자 승인

## 현재 구현 우선순위

1. Phase 상태와 backlog inventory 정리
   - 쉽게 말하면: 과거 phase에 남은 "아직 해야 하는 것처럼 보이는 항목"을 다시 확인한다.
   - 왜 먼저 하는가: 이 정리가 없으면 Phase 27 이후 작업이 예전 pending 상태에 계속 끌려간다.
   - 기대 효과: 지금 남은 일이 blocker인지, future option인지, legacy note인지 구분된다.
2. Foundation gap map 작성
   - 쉽게 말하면: 데이터, 백테스트, 전략 family, 후보 검토, portfolio workflow 중 어디가 약한지 표로 본다.
   - 왜 필요한가: Phase 27~30의 순서를 감이 아니라 제품 foundation의 빈틈 기준으로 정해야 한다.
   - 기대 효과: Phase 27 Data Integrity 작업의 우선순위가 명확해진다.
3. Phase 27~30 roadmap 확정
   - 쉽게 말하면: 지금 합의한 큰 그림을 문서에 고정한다.
   - 왜 필요한가: Live Readiness / Final Approval을 성급히 당기지 않고, 먼저 필요한 기반 작업을 끝내기 위해서다.
   - 기대 효과: 다음 phase마다 "왜 이걸 지금 하는지"가 더 분명해진다.

## 이 문서에서 자주 쓰는 용어

- Backlog Rebase:
  - 예전에 남은 할 일을 현재 제품 상태 기준으로 다시 분류하는 일이다.
- Foundation:
  - 데이터 수집, 백테스트 신뢰성, 전략 실행, 결과 저장, 후보 검토 같은 제품의 바닥 구조다.
- Blocker:
  - 다음 phase로 넘어가기 전에 반드시 해결해야 하는 문제다.
- Future Option:
  - 지금 당장 막지는 않지만 나중에 다시 선택할 수 있는 개선 후보를 뜻한다.
- Live Readiness / Final Approval:
  - 실제 돈을 넣어도 되는지 마지막으로 판단하는 단계다.
  - Phase 26~30 이후에 별도 phase로 다룬다.

## 이번 phase의 운영 원칙

- 새 기능 추가보다 정리와 분류를 우선한다.
- 과거 phase를 전부 다시 QA하려고 하지 않는다.
- 사용자가 명시적으로 요청하지 않는 한 deep backtest나 투자 후보 분석을 하지 않는다.
- `manual_qa_pending`이 남아 있어도 현재 제품 흐름의 blocker가 아니면 future / legacy 상태로 분리한다.
- Phase 27~30은 제품 기반을 강화하는 개발 phase로 본다.

## 이번 phase의 주요 작업 단위

### 첫 번째 작업: phase 상태와 backlog 재분류

- 무엇을 바꾸는가:
  - roadmap과 doc index에 남아 있는 과거 phase 상태를 현재 기준으로 다시 읽는다.
- 왜 필요한가:
  - 오래된 pending 상태가 실제 blocker인지 아닌지 판단해야 한다.
- 끝나면 좋은 점:
  - 다음 phase가 과거 문서 혼선 없이 시작된다.

### 두 번째 작업: foundation gap map 작성

- 무엇을 바꾸는가:
  - 데이터 신뢰성, 백테스트 preflight, 전략 family parity, 후보 검토, portfolio workflow의 빈틈을 정리한다.
- 왜 필요한가:
  - Phase 27~30의 실제 개발 우선순위를 정해야 한다.
- 끝나면 좋은 점:
  - Phase 27이 바로 Data Integrity 작업으로 들어갈 수 있다.

### 세 번째 작업: Phase 27~30 handoff 고정

- 무엇을 바꾸는가:
  - Phase 27~30의 큰 그림을 roadmap과 index에 고정한다.
- 왜 필요한가:
  - 사용자가 다음 phase의 목적을 읽고 바로 이해할 수 있어야 한다.
- 끝나면 좋은 점:
  - Phase 30 이후 Live Readiness / Final Approval을 열 때까지 개발 흐름이 흔들리지 않는다.

## 다음에 확인할 것

- 재분류 결과는 `.note/finance/phases/phase26/PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`에서 확인한다.
- Phase 8, 9, 12~15, 18의 pending 상태는 현재 immediate blocker가 아니라 `superseded_by_later_phase`로 재분류했다.
- Phase 18 remaining structural backlog는 Phase 28의 future structural option으로 유지한다.
- Phase 27에서 먼저 잡아야 할 데이터 신뢰성 이슈는 common-date truncation, stale/missing ticker, malformed price row, statement coverage semantics다.

## 한 줄 정리

Phase 26은 새 기능을 늘리는 phase가 아니라, Phase 27~30을 안전하게 진행하기 위해 과거 backlog와 현재 foundation gap을 다시 정렬하는 phase다.
