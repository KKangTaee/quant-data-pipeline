# Phase 9 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 9 방향 확정
  - strict coverage policy + promotion gate를 이번 chapter의 메인 축으로 고정
- `completed` Phase 9 계획 문서 작성
  - `PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md`
- `completed` 실전 투자 기준 상위 방향 문서 작성
  - `PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md`
- `completed` roadmap / doc index / 로그 동기화 시작

## 2. Strict Coverage Exception Inventory

- `completed` exception bucket inventory 작성
  - `source_empty_or_symbol_issue`
  - `foreign_or_nonstandard_form_structure`
  - `source_present_raw_missing`
  - `raw_present_shadow_missing`
  를 현재 preset / diagnostics 기준으로 어떻게 해석할지 정리
- `completed` representative symbol set 정리
  - `MRSH`, `AU` 같은 known exception case를 policy anchor로 고정
- `completed` strict universe exception table 초안
  - eligible / review-needed / excluded 3단 분류 초안 작성

## 3. Unsupported Form Policy

- `completed` foreign / non-standard filing policy 초안
  - `20-F`, `6-K`, `40-F` 등 form의 기본 처리 정책 정의
- `completed` support vs exclusion decision
  - quarterly strict family에서 지원 확대가 맞는지, 제외가 맞는지 결정

## 4. Promotion Gate Definition

- `completed` annual strict family public role 재확인
  - 이미 public candidate인 annual strict family의 유지 조건 정리
- `completed` quarterly strict family promotion gate 초안
  - research-only 유지 조건과 public candidate 진입 조건 문서화
- `completed` universe semantics decision
  - current strict preset을 `managed static research universe`로 공식 고정할지
  - historical monthly top-N universe는 future separate mode로 둘지 결정
- `completed` next-phase engineering priority 고정
  - portfolio productization보다 `historical dynamic PIT universe`를 먼저 둘지 결정

## 5. Operator Decision Policy

- `completed` diagnostics-to-action decision tree 초안
  - recollection / rebuild / exclusion / review로 이어지는 operator rule 정리
- `completed` preset governance rule 초안
  - canonical strict preset에 어떤 심볼이 남고 빠지는지 유지 규칙 정의

## 6. Documentation And Handoff

- `completed` phase-specific reference docs 추가
- `completed` comprehensive analysis sync
- `completed` manual policy checklist 작성

## 7. Validation State

- `completed` assistant-side policy precheck
- `pending` user review / confirmation
- `pending` batch QA with Phase 8 / 9 / 10
  - 사용자 확인은 Phase 10 구현 이후 `Phase 8 + Phase 9 + Phase 10` checklist를 묶어 진행 가능

## 현재 메모

- `Phase 8`은 구현 완료, manual validation pending 상태로 유지한다.
- `Phase 9`는 기능 추가보다 policy / governance / promotion 기준을 고정하는 chapter로 진행한다.
- 현재 임시 기본안:
  - `source_empty_or_symbol_issue` = 기본 제외
  - `foreign_or_nonstandard_form_structure` = 기본 제외
  - `raw_present_shadow_missing` = eligible + rebuild path
  - `source_present_raw_missing` = review-needed + targeted recollection
  - quarterly family = research-only 유지
  - current strict coverage preset = `run-level static managed universe`
- 실전 투자 기준 권고:
  - Phase 9는 policy / governance 고정
  - 다음 major engineering priority는 `historical dynamic PIT universe`
  - portfolio productization은 그 이후 단계로 두는 편이 맞다
- validation 운영 권고:
  - Phase 8과 Phase 9는 지금처럼 implementation-complete / policy-first 상태로 유지하고
  - 사용자 manual QA는 Phase 10 이후 batch review로 함께 돌려도 된다
