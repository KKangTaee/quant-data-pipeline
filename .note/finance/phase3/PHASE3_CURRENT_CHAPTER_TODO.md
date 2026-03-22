# Phase 3 Current Chapter TODO

## 목적
이 문서는 Phase 3의 첫 챕터를
실행 가능한 큰 TODO와 세부 체크 항목으로 관리하기 위한 작업 보드다.

상위 계획 문서:
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`

---

## 현재 챕터 범위

현재 챕터의 목표:

1. loader 구현 범위를 확정한다
2. strict vs broad loader 정책을 고정한다
3. 첫 구현 대상 loader 묶음을 결정한다

---

## 큰 TODO 보드

### A. Loader Scope Finalization
상태:
- `completed`

세부 작업:
- `[completed]` 1차 loader 구현 목록 확정
  - 어떤 loader를 지금 구현하고 어떤 loader를 다음으로 미룰지 결정
- `[completed]` loader 모듈 경로 확정
  - `finance/loaders/*` 구조로 갈지 최종 확정
- `[completed]` helper 분리 범위 확정
  - symbol resolution / date normalization / strict PIT helper 범위 정리

완료 기준:
- 구현 시작 전에 파일 구조와 우선 loader 목록이 확정되어 있어야 함

---

### B. Strict vs Broad Loader Policy
상태:
- `completed`

세부 작업:
- `[completed]` naming 규칙 확정
  - strict PIT loader와 broad research loader 이름을 어떻게 구분할지 결정
- `[completed]` strict statement loader 범위 확정
  - accession-bearing rows만 읽는 strict statement snapshot 규칙 고정
- `[completed]` broad loader 허용 범위 확정
  - broad research loader가 legacy/mixed-state를 어디까지 허용할지 결정

완료 기준:
- strict / broad loader 차이가 이름과 정책에서 명확해야 함

---

### C. Implementation Entry Set
상태:
- `completed`

세부 작업:
- `[completed]` 첫 구현 loader 순서 확정
  - universe / price / fundamentals / factors / statements 중 어떤 순서로 구현할지 정리
- `[completed]` first DB-backed strategy 후보 결정
  - 가장 먼저 loader와 연결해 볼 전략 1개 후보 선택
- `[completed]` 최소 검증 경로 정의
  - 어떤 입력과 어떤 결과로 성공 여부를 판별할지 정의

완료 기준:
- 바로 다음 코드 구현 작업을 시작할 수 있을 정도로 entry set이 정리되어 있어야 함

---

## 현재 추천 다음 작업 순서

1. B-1 naming 규칙 확정
2. B-2 strict statement loader 범위 확정
3. B-3 broad loader 허용 범위 확정
4. A-1 1차 loader 구현 목록 확정
5. C-1 첫 구현 loader 순서 확정

---

## 현재 작업 중 항목

현재 `in_progress`:
- `없음`

바로 다음 체크 대상:
- `Phase 3 첫 코드 구현 시작`

---

## 현재 진척도

- Phase 3 현재 챕터:
  - 약 `65%`

판단 근거:
- Phase 3는 개시되었고
- strict / broad policy, loader scope, implementation entry set이 정리된 상태
