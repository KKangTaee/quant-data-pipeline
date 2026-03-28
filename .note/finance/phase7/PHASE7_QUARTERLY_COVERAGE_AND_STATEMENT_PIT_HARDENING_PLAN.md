# Phase 7 Quarterly Coverage And Statement PIT Hardening Plan

## 목적

- quarterly strict family가 현재 research-only / late-start 상태에 머무는 근본 원인을 해결한다.
- statement raw layer와 timing semantics를 다시 점검해,
  quarterly strict family가 더 긴 history에서 연구 가능하도록 기반을 만든다.

## 왜 이 phase가 필요한가

Phase 6에서 `Quality Snapshot (Strict Quarterly Prototype)`는 실제 코드 경로로 열렸지만,
manual validation 기준으로 active period가 주로 `2025` 부근부터 시작했다.

이 현상은 전략 로직 문제라기보다,
아래 upstream/data 문제와 더 직접적으로 연결된다.

- quarterly statement raw coverage 부족
- quarterly shadow fundamentals/factors depth 부족
- filing / acceptance / available timing semantics 불명확
- current raw statement tables의 정보 표현력 부족 가능성

즉 Phase 7의 핵심은
**quarterly strict strategy를 더 똑똑하게 만드는 것**보다
**quarterly strict strategy가 제대로 돌아갈 수 있는 PIT data foundation을 만드는 것**
이다.

## 이번 phase의 핵심 질문

1. 현재 statement source API는 실제로 어떤 timing field를 돌려주는가
2. 현 `nyse_financial_statement_*` 계열 raw schema가 그 정보를 충분히 담고 있는가
3. quarterly shadow fundamentals / factors가 왜 late-start 되는가
4. 어떤 schema / loader / backfill 조합이 quarterly longer-history를 가장 빠르게 회복시키는가

## 범위 안

### A. statement source payload 재확인

- API raw response 직접 점검
- 다양한 symbol case 비교
- annual / quarterly / filing / acceptance / available timing field 확인

### B. raw statement ledger 재정비

- 현 raw table 구조 리뷰
- column meaning 재정의
- 필요시 schema 변경 또는 대대적 재생성
- 사람 눈으로 검증하기 쉬운 inspection path도 함께 설계

### C. quarterly shadow path hardening

- quarterly fundamentals/factors shadow 생성 경로 재검토
- PIT timing과 snapshot availability semantics 재정리
- longer-history quarterly coverage 복구 시도

### D. quarterly strict validation rerun

- prototype 재실행
- first active date / coverage / freshness / runtime 재측정
- research-only 유지 vs promotion 가능성 판단

## 범위 밖

- 새 overlay 추가
- intramonth event engine
- quarterly strict public default 승격 확정
- broad strategy-library 대규모 추가

## 추천 구현 순서

1. statement source payload inspection
2. current raw statement schema review
3. PIT timing column / table redesign decision
4. schema / loader patch
5. quarterly shadow rebuild
6. quarterly coverage audit
7. quarterly prototype rerun validation
8. docs / checklist / next-step sync

## 완료 기준

Phase 7 current chapter는 최소 아래가 충족되면 closeout-ready로 본다.

- statement source payload와 timing field가 문서화되어 있음
- raw statement ledger schema의 역할이 현재 코드 기준으로 정리되어 있음
- quarterly shadow path가 재정비되었거나, 최소한 blocker가 정확히 고정되어 있음
- quarterly strict prototype의 rerun validation 결과가 문서화되어 있음
- phase-specific manual test checklist가 작성되어 있음

## 현재 상태

- phase direction:
  - `opened`
- current chapter focus:
  - `statement payload + PIT timing reality check first`
  - `quarterly coverage hardening second`
- current implementation state:
  - `first_pass_completed`
  - `supplementary_polish_completed`
