# Phase 7 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 7 방향 고정
  - quarterly coverage + statement PIT hardening을 이번 chapter의 메인 축으로 확정
- `completed` Phase 7 계획 문서 작성
  - `PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
- `completed` roadmap / doc index / 로그 동기화 검토

## 2. Statement Source Reality Check

- `completed` source API payload inspection
  - 다양한 symbol과 annual/quarterly 케이스에서 실제 반환 필드 확인
- `completed` timing field inventory
  - filing / acceptance / available-at에 준하는 필드 존재 여부 정리
- `completed` payload-to-raw-table mapping 초안
  - 현재 raw ledger가 담는 정보와 누락 정보를 정리

## 3. Raw Statement Ledger Review

- `completed` current schema audit
  - `nyse_financial_statement_*` 계열 table 구조와 business meaning 점검
- `completed` redesign decision
  - 유지 / 수정 / 재생성 방향 중 하나를 문서로 고정
- `completed` human-readable inspection path 설계
  - raw response와 DB row를 비교 확인할 수 있는 조회 방식 정리

## 4. Quarterly Coverage Hardening

- `completed` quarterly shadow path audit
  - fundamentals / factors / strict snapshot availability late-start 원인 측정
- `completed` schema / loader / rebuild implementation
  - 필요한 경우 raw statement schema와 shadow rebuild 경로 수정
- `completed` quarterly prototype rerun validation
  - first active date / coverage / runtime 재측정

## 5. Documentation And Handoff

- `completed` phase-specific reference docs 작성
- `completed` comprehensive analysis sync
- `completed` manual test checklist 작성
- `completed` supplementary polish pass
  - weekend/holiday-aware price freshness preflight
  - quarterly statement shadow coverage preview
  - statement PIT inspection UI card
  - quarterly UI guidance wording refresh
- `completed` completion summary / next-phase prep
  - implementation closeout 문서 작성
  - next-phase direction을 quarterly strategy family expansion으로 고정

## 6. Validation State

- `completed` assistant pre-validation
  - checklist 핵심 항목을 코드/runtime 기준으로 먼저 점검
- `completed` closeout confirmation
  - later operator 보강과 checklist 확인을 거쳐 Phase 7은 closeout-ready가 아니라 closeout-complete 상태로 전환
