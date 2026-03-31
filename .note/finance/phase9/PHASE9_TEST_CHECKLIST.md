# Phase 9 Test Checklist

## 목적

- Phase 9에서 고정한 policy / governance / promotion 문구가
  현재 구현과 실제 diagnostics 결과에 맞는지 확인한다.
- 이번 checklist는 성격상
  “UI 기능 QA”보다 “정책 해석 검수”에 가깝다.

## 1. strict preset semantics 확인

- `Backtest`에서 `Coverage 100/300/500/1000` preset을 확인한다
- 관련 문서:
  - `PHASE9_STRICT_COVERAGE_POLICY_DECISION.md`
  - `PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md`
- 확인:
  - current preset이 historical monthly top-N이 아니라
    `managed static research universe`로 설명되어 있는지
  - future real-money validation은 별도 `historical dynamic PIT universe`가 필요하다는 방향이 문서에 있는지

## 2. active coverage gap inventory 확인

- `Quality Snapshot (Strict Quarterly Prototype)`
- `US Statement Coverage 300`, `500`, `1000`
- `Statement Shadow Coverage Preview` 확인
- 기대:
  - `300` preset: missing `2`
  - `500` preset: missing `3`
  - `1000` preset: missing `12`
  - 모두 `raw_present_shadow_missing`보다 `no_raw_statement_coverage` 중심인지

## 3. Coverage Gap Drilldown coarse 분류 확인

- `Coverage Gap Drilldown` 열기
- 확인:
  - `Coverage Gap Status` 컬럼이 coarse 상태만 보여주는지
  - 세부 diagnosis는 `Statement Coverage Diagnosis`에서 보라고 안내하는지

## 4. Statement Coverage Diagnosis fine 분류 확인

- `Ingestion > Manual Jobs / Inspection > Statement Coverage Diagnosis`
- symbols:
  - `MRSH,AU,GFS`
- freq:
  - `quarterly`
- 기대:
  - `MRSH` -> `source_empty_or_symbol_issue`
  - `AU` -> `foreign_or_nonstandard_form_structure`
  - `GFS` -> `foreign_or_nonstandard_form_structure`

## 5. operator guidance 확인

- 같은 결과 표에서 아래 컬럼 확인:
  - `Recommended Action`
  - `Note`
  - `Stepwise Guidance`
- 기대:
  - 컬럼명은 영어
  - 값은 한국어
  - `MRSH`는 symbol/source validity review 방향
  - `AU`, `GFS`는 form support vs exclusion 방향

## 6. policy mapping 문서 확인

- 문서:
  - `PHASE9_STRICT_COVERAGE_EXCEPTION_INVENTORY.md`
  - `PHASE9_STRICT_COVERAGE_POLICY_DECISION.md`
- 확인:
  - `source_empty_or_symbol_issue` = default `excluded`
  - `foreign_or_nonstandard_form_structure` = default `excluded`
  - `raw_present_shadow_missing` = `eligible`
  - `source_present_raw_missing` = `review_needed`

## 7. promotion gate 문서 확인

- 문서:
  - `PHASE9_STRICT_FAMILY_PROMOTION_GATE.md`
- 확인:
  - `strict annual family`는 public-candidate 유지
  - `strict quarterly family`는 Phase 9 동안 `research-only`
  - final real-money validation은 future `historical dynamic PIT universe`를 거친다는 문구가 있는지

## 8. operator decision tree 확인

- 문서:
  - `PHASE9_OPERATOR_DECISION_TREE.md`
- 확인:
  - price diagnosis와 statement coverage diagnosis가 섞이지 않게 분리돼 있는지
  - coverage gap -> diagnosis -> action -> governance 흐름이 단계별로 정리돼 있는지

## 9. roadmap / index / logs sync 확인

- 문서:
  - `MASTER_PHASE_ROADMAP.md`
  - `FINANCE_DOC_INDEX.md`
  - `WORK_PROGRESS.md`
  - `QUESTION_AND_ANALYSIS_LOG.md`
- 확인:
  - Phase 9 active 상태가 반영돼 있는지
  - 새 Phase 9 문서들이 index에 등록돼 있는지
  - 실전 투자 기준 권고가 로그에 남아 있는지

## closeout 판단 기준

아래가 모두 만족되면
Phase 9는 “policy first pass complete”로 볼 수 있다.

1. current preset semantics가 문서상 흔들리지 않는다
2. diagnostics bucket과 policy mapping이 정리되어 있다
3. annual / quarterly promotion gate가 문서로 고정되어 있다
4. next engineering priority가 `historical dynamic PIT universe`로 정리되어 있다
