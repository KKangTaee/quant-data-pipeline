# Finance Documentation Index

## 목적
이 문서는 `.note/finance/` 아래의 핵심 문서들을
역할과 Phase 기준으로 빠르게 찾기 위한 인덱스다.

---

## 1. 상위 기준 문서

- `.note/finance/MASTER_PHASE_ROADMAP.md`
  - 전체 Phase 구조와 상위 진행 방향
- `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `finance` 패키지 전체 구조와 DB/기능 종합 분석
- `.note/finance/WORK_PROGRESS.md`
  - 구현 진행 로그
- `.note/finance/QUESTION_AND_ANALYSIS_LOG.md`
  - 질의/설계/분석 결과 로그

---

## 2. Phase 1 문서

- `.note/finance/phase1/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md`
  - 1차 내부 웹앱 개발 순서 가이드
- `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md`
  - 1차 범위 정의
- `.note/finance/phase1/PHASE1_JOB_WRAPPER_INTERFACE.md`
  - job wrapper 인터페이스 계획

---

## 3. Phase 2 상위 문서

- `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`
  - PHASE2 전체 계획 문서
- `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`
  - PHASE2 일반 운영 고도화 챕터 보드
- `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`
  - PHASE2 point-in-time hardening 챕터 보드
- `.note/finance/phase2/PHASE2_COMPLETION_SUMMARY.md`
  - PHASE2 종료 요약 문서

---

## 4. Phase 3 상위 문서

- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
  - PHASE3 전체 계획 문서
- `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
  - PHASE3 첫 챕터 TODO 보드
- `.note/finance/phase3/PHASE3_LOADER_NAMING_POLICY.md`
  - Phase 3 loader naming 규칙
- `.note/finance/phase3/PHASE3_STRICT_STATEMENT_LOADER_SCOPE.md`
  - strict statement snapshot loader 범위 정책
- `.note/finance/phase3/PHASE3_BROAD_STATEMENT_LOADER_POLICY.md`
  - broad statement research loader 허용 범위 정책
- `.note/finance/phase3/PHASE3_INITIAL_LOADER_IMPLEMENTATION_SET.md`
  - Phase 3 1차 loader 구현 세트 정의
- `.note/finance/phase3/PHASE3_LOADER_MODULE_PATH.md`
  - Phase 3 loader 패키지 경로와 모듈 경계
- `.note/finance/phase3/PHASE3_LOADER_HELPER_SCOPE.md`
  - Phase 3 `_common.py` helper 범위 정의

---

## 5. Phase 2 / Phase 3 - Backtest / Loader 관련 문서

- `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
  - loader 함수 초안
- `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
  - loader 입력 계약
- `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`
  - point-in-time 원칙
- `.note/finance/phase2/STRICT_PIT_LOADER_QUERY_DRAFT.md`
  - strict PIT loader query 초안

---

## 6. Phase 2 - Point-In-Time / 재무제표 정리 문서

- `.note/finance/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`
  - point-in-time 스키마 리뷰와 패치 계획
- `.note/finance/phase2/POINT_IN_TIME_BACKFILL_AND_CONSTRAINT_STRATEGY.md`
  - backfill 및 stricter constraint 전략

---

## 7. 운영 / 설정 / 수집 전략 문서

- `.note/finance/DATA_COLLECTION_UI_STRATEGY.md`
  - 내부 운영 수집 UI 전략
- `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - 설정 외부화 후보와 우선순위
- `.note/finance/OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md`
  - OHLCV / 재무 적재 기능 점검 문서

---

## 8. 문서 사용 순서 권장

처음 프로젝트 전체를 볼 때:
1. `MASTER_PHASE_ROADMAP.md`
2. `FINANCE_COMPREHENSIVE_ANALYSIS.md`
3. 현재 활성 TODO 보드

현재 작업 위치를 볼 때:
1. 현재 활성 Phase TODO 문서
2. `WORK_PROGRESS.md`
3. `QUESTION_AND_ANALYSIS_LOG.md`

백테스트 준비를 볼 때:
1. `PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`
2. `BACKTEST_LOADER_FUNCTION_DRAFT.md`
3. `BACKTEST_LOADER_INPUT_CONTRACT.md`
4. `BACKTEST_POINT_IN_TIME_GUIDELINES.md`

Phase 3 시작 시:
1. `MASTER_PHASE_ROADMAP.md`
2. `PHASE2_COMPLETION_SUMMARY.md`
3. `PHASE3_LOADER_AND_RUNTIME_PLAN.md`
4. `PHASE3_CURRENT_CHAPTER_TODO.md`
5. `PHASE3_STRICT_STATEMENT_LOADER_SCOPE.md`
6. `PHASE3_BROAD_STATEMENT_LOADER_POLICY.md`
7. `PHASE3_INITIAL_LOADER_IMPLEMENTATION_SET.md`
8. `PHASE3_LOADER_MODULE_PATH.md`
9. `PHASE3_LOADER_HELPER_SCOPE.md`
