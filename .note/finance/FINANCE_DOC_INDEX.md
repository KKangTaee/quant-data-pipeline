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
- `.note/finance/phase3/PHASE3_FIRST_LOADER_IMPLEMENTATION_ORDER.md`
  - Phase 3 첫 loader 구현 순서
- `.note/finance/phase3/PHASE3_FIRST_DB_BACKED_STRATEGY_CANDIDATE.md`
  - Phase 3 첫 DB-backed 전략 후보
- `.note/finance/phase3/PHASE3_MINIMAL_VALIDATION_PATH.md`
  - Phase 3 첫 최소 검증 경로
- `.note/finance/phase3/PHASE3_LOADER_IMPLEMENTATION_TODO.md`
  - Phase 3 실제 loader 코드 구현 챕터 보드
- `.note/finance/phase3/PHASE3_CHAPTER1_COMPLETION_SUMMARY.md`
  - Phase 3 첫 구현 챕터 종료 요약
- `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`
  - Phase 3 다음 실행 챕터 TODO 보드
- `.note/finance/phase3/PHASE3_RUNTIME_ADAPTER_PATH.md`
  - Phase 3 첫 runtime adapter 연결 방식
- `.note/finance/phase3/PHASE3_FIRST_DB_BACKED_RUNTIME_VALIDATION.md`
  - Phase 3 첫 DB-backed 전략 실행 검증 결과
- `.note/finance/phase3/PHASE3_DB_SAMPLE_ENTRYPOINTS.md`
  - Phase 3 DB 기반 전략 샘플 함수 정리
- `.note/finance/phase3/PHASE3_OHLCV_INGESTION_HARDENING_TODO.md`
  - stock + ETF 공통 OHLCV 수집 hardening 작업 보드
- `.note/finance/phase3/PHASE3_OHLCV_STORAGE_DECISION.md`
  - stock + ETF OHLCV 단일 price table 유지 결정
- `.note/finance/phase3/PHASE3_OHLCV_INGESTION_VALIDATION.md`
  - OHLCV hardening 후 실제 적재/전략 검증 결과
- `.note/finance/phase3/PHASE3_STATEMENT_LOADER_VALIDATION.md`
  - broad / strict statement loader 기본 검증 결과
- `.note/finance/phase3/PHASE3_DB_SAMPLE_ALIGNMENT_VALIDATION.md`
  - DB-backed sample warmup 정렬과 direct-vs-DB 차이 분석 결과
- `.note/finance/phase3/PHASE3_PORTFOLIO_SAMPLE_PARITY_POSTMORTEM.md`
  - `portfolio_sample` vs `portfolio_sample_from_db` 불일치 원인과 해결 회고
- `.note/finance/phase3/PHASE3_RUNTIME_PATH_ROLE_SPLIT.md`
  - legacy direct-fetch path와 DB-backed runtime path 역할 분리 문서
- `.note/finance/phase3/PHASE3_PRICE_ONLY_RUNTIME_PATTERN.md`
  - price-only 전략 sample의 공통 runtime 시작 패턴 정리
- `.note/finance/phase3/PHASE3_FACTOR_FUNDAMENTAL_RUNTIME_CONNECTIONS.md`
  - factor / fundamental 전략의 loader-to-runtime 연결 포인트 정리
- `.note/finance/phase3/PHASE3_RUNTIME_STRATEGY_INPUT_CONTRACT.md`
  - Phase 3 기준 strategy runtime 입력 계약 정리
- `.note/finance/phase3/PHASE3_REPEATABLE_DB_BACKED_SMOKE_SCENARIOS.md`
  - DB-backed runtime 반복 smoke scenario 세트
- `.note/finance/phase3/PHASE3_LOADER_RUNTIME_VALIDATION_EXAMPLES.md`
  - loader/runtime 검증용 실행 예시 모음
- `.note/finance/phase3/PHASE3_RUNTIME_CLEANUP_BACKLOG.md`
  - runtime generalization 이후 남겨둔 warning / cleanup / optimization backlog
- `.note/finance/phase3/PHASE3_UI_RUNTIME_FUNCTION_CANDIDATES.md`
  - Phase 4 UI가 직접 호출할 최소 runtime function 후보 정리
- `.note/finance/phase3/PHASE3_UI_USER_INPUT_SET_DRAFT.md`
  - Phase 4 전략 실행 UI의 최소 user-facing 입력 세트 초안
- `.note/finance/phase3/PHASE3_UI_RESULT_BUNDLE_DRAFT.md`
  - Phase 4 전략 실행 UI가 받게 될 최소 결과 bundle 초안
- `.note/finance/phase3/PHASE3_FUNDAMENTALS_FACTORS_HARDENING_TODO.md`
  - `nyse_fundamentals` / `nyse_factors` hardening 실행 보드
- `.note/finance/phase3/PHASE3_FUNDAMENTALS_FACTORS_REVIEW_AND_DIRECTION.md`
  - `nyse_fundamentals` / `nyse_factors` 역할, 수정 내용, 장기 방향 정리

---

## 5. Phase 4 상위 문서

- `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md`
  - Phase 4 전체 계획 문서
- `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md`
  - Phase 4 첫 실행 챕터 TODO 보드
- `.note/finance/phase4/PHASE4_UI_STRUCTURE_DECISION.md`
  - 단일 메인 앱 + `Ingestion` / `Backtest` 탭 구조 결정 문서
- `.note/finance/phase4/PHASE4_RUNTIME_WRAPPER_SIGNATURES.md`
  - Phase 4 first public runtime wrapper와 공통 result bundle builder 시그니처 문서
- `.note/finance/phase4/PHASE4_FIRST_SCREEN_SCOPE.md`
  - Phase 4 첫 백테스트 화면 범위와 form-first 결정 문서
- `.note/finance/phase4/PHASE4_FIRST_RESULT_LAYOUT_DRAFT.md`
  - Phase 4 첫 결과 레이아웃 초안과 현재 탭 구조 정리
- `.note/finance/phase4/PHASE4_ERROR_AND_EMPTY_RESULT_RULES.md`
  - Phase 4 첫 오류/빈 결과 처리 규칙 문서
- `.note/finance/phase4/PHASE4_SECOND_STRATEGY_GTAA_ADDITION.md`
  - Phase 4 두 번째 공개 전략으로 GTAA를 추가한 기록 문서
- `.note/finance/phase4/PHASE4_THIRD_STRATEGY_RISK_PARITY_ADDITION.md`
  - Phase 4 세 번째 공개 전략으로 Risk Parity Trend를 추가한 기록 문서
- `.note/finance/phase4/PHASE4_FOURTH_STRATEGY_DUAL_MOMENTUM_ADDITION.md`
  - Phase 4 네 번째 공개 전략으로 Dual Momentum을 추가한 기록 문서
- `.note/finance/phase4/PHASE4_FOURTH_STRATEGY_DUAL_MOMENTUM_NEXT.md`
  - Dual Momentum 추가 직전 후보 상태를 남긴 기록 문서
- `.note/finance/phase4/PHASE4_VISUALIZATION_AND_PORTFOLIO_BUILDER_OPTIONS.md`
  - 시각화 강화, 전략 비중 결합, 다중 전략 비교 UI 선택지 정리 문서
- `.note/finance/phase4/PHASE4_COMPARE_AND_WEIGHTED_PORTFOLIO_FIRST_PASS.md`
  - 다중 전략 비교와 weighted portfolio builder first-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_WEIGHTED_PORTFOLIO_CONTRIBUTION_FIRST_PASS.md`
  - weighted portfolio 기여도 시각화 first-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_FIRST_PASS.md`
  - Backtest 탭 실행 이력 저장 first-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_ENHANCEMENT_FIRST_PASS.md`
  - Backtest history의 filter / search / drilldown first-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_ENHANCEMENT_SECOND_PASS.md`
  - Backtest history의 date filter / metric sort / single-strategy rerun second-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_BACKTEST_HISTORY_ENHANCEMENT_THIRD_PASS.md`
  - Backtest history의 metric threshold filter / form prefill / single-strategy form reload third-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_VISUALIZATION_ENHANCEMENT_FIRST_PASS.md`
  - Backtest 탭 시각화 강화 first-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_VISUALIZATION_ENHANCEMENT_SECOND_PASS.md`
  - compare overlay end marker와 strategy highlight table을 추가한 second-pass 시각화 기록 문서

---

## 6. Phase 2 / Phase 3 - Backtest / Loader 관련 문서

- `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
  - loader 함수 초안
- `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
  - loader 입력 계약
- `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`
  - point-in-time 원칙
- `.note/finance/phase2/STRICT_PIT_LOADER_QUERY_DRAFT.md`
  - strict PIT loader query 초안

---

## 7. Phase 2 - Point-In-Time / 재무제표 정리 문서

- `.note/finance/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`
  - point-in-time 스키마 리뷰와 패치 계획
- `.note/finance/phase2/POINT_IN_TIME_BACKFILL_AND_CONSTRAINT_STRATEGY.md`
  - backfill 및 stricter constraint 전략

---

## 8. 운영 / 설정 / 수집 전략 문서

- `.note/finance/DATA_COLLECTION_UI_STRATEGY.md`
  - 내부 운영 수집 UI 전략
- `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - 설정 외부화 후보와 우선순위
- `.note/finance/OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md`
  - OHLCV / 재무 적재 기능 점검 문서

---

## 9. 문서 사용 순서 권장

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
10. `PHASE3_FIRST_LOADER_IMPLEMENTATION_ORDER.md`
11. `PHASE3_FIRST_DB_BACKED_STRATEGY_CANDIDATE.md`
12. `PHASE3_MINIMAL_VALIDATION_PATH.md`

Phase 3 현재 위치를 볼 때:
1. `PHASE3_CHAPTER1_COMPLETION_SUMMARY.md`
2. `PHASE3_RUNTIME_GENERALIZATION_TODO.md`
3. `PHASE3_RUNTIME_CLEANUP_BACKLOG.md`
4. `PHASE3_UI_RUNTIME_FUNCTION_CANDIDATES.md`
5. `PHASE3_UI_USER_INPUT_SET_DRAFT.md`
6. `PHASE3_UI_RESULT_BUNDLE_DRAFT.md`
7. `WORK_PROGRESS.md`
8. `QUESTION_AND_ANALYSIS_LOG.md`

Phase 4 시작 시:
1. `MASTER_PHASE_ROADMAP.md`
2. `PHASE3_RUNTIME_GENERALIZATION_TODO.md`
3. `PHASE3_UI_RUNTIME_FUNCTION_CANDIDATES.md`
4. `PHASE3_UI_USER_INPUT_SET_DRAFT.md`
5. `PHASE3_UI_RESULT_BUNDLE_DRAFT.md`
6. `PHASE4_UI_AND_BACKTEST_PLAN.md`
7. `PHASE4_UI_STRUCTURE_DECISION.md`
8. `PHASE4_RUNTIME_WRAPPER_SIGNATURES.md`
9. `PHASE4_CURRENT_CHAPTER_TODO.md`
