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
- `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_ANALYSIS_20260328.md`
  - `Daily Market Update`의 yfinance rate-limit 재현 결과와 first-pass 최적화 방향 분석 문서

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
- `.note/finance/phase4/PHASE4_UI_CHAPTER1_COMPLETION_SUMMARY.md`
  - Phase 4 첫 UI 실행 챕터 완료 요약 문서
- `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_ENTRY_TODO.md`
  - Phase 4 다음 챕터인 factor / fundamental 전략 진입 준비 보드
- `.note/finance/phase4/PHASE4_FACTOR_FUNDAMENTAL_FIRST_STRATEGY_OPTIONS.md`
  - 첫 factor / fundamental 전략 후보 선택지 문서
- `.note/finance/phase4/PHASE4_QUALITY_SNAPSHOT_STRATEGY_SCOPE.md`
  - 첫 factor / fundamental 전략으로 선택된 Quality Snapshot Strategy의 범위 문서
- `.note/finance/phase4/PHASE4_QUALITY_RUNTIME_WRAPPER_DRAFT.md`
  - Quality Snapshot Strategy용 first public runtime wrapper 초안
- `.note/finance/phase4/PHASE4_QUALITY_BROAD_RESEARCH_DECISION.md`
  - Quality Snapshot Strategy의 first public mode를 broad_research로 정한 결정 문서
- `.note/finance/phase4/PHASE4_QUALITY_SNAPSHOT_IMPLEMENTATION_FIRST_PASS.md`
  - Quality Snapshot Strategy broad-research first-pass 구현 기록 문서
- `.note/finance/phase4/PHASE4_QUALITY_UI_INPUT_DRAFT.md`
  - Quality Snapshot Strategy의 기본 / advanced / hidden UI 입력 정리 문서
- `.note/finance/phase4/PHASE4_FIFTH_STRATEGY_QUALITY_ADDITION.md`
  - Quality Snapshot Strategy를 Backtest UI의 다섯 번째 전략으로 연결한 기록 문서
- `.note/finance/phase4/PHASE4_STATEMENT_DRIVEN_QUALITY_BLOCKER_AND_NEXT_STEPS.md`
  - statement-driven quality path로 바로 넘어갈 때의 현재 blocker와 다음 현실적 선택지 정리 문서
- `.note/finance/phase4/PHASE4_STATEMENT_LEDGER_FEASIBILITY_AND_TARGETED_BACKFILL.md`
  - statement-driven quality로 가기 전 수행한 sample-universe feasibility test와 targeted backfill 결과 문서
- `.note/finance/phase4/PHASE4_STATEMENT_DRIVEN_QUALITY_PROTOTYPE_FIRST_PASS.md`
  - strict statement snapshot 기반 sample-universe quality prototype first-pass 구현 및 검증 문서
- `.note/finance/phase4/PHASE4_STATEMENT_TO_FUNDAMENTALS_FACTORS_MAPPING_FIRST_PASS.md`
  - strict statement snapshot에서 normalized fundamentals와 quality factor snapshot으로 가는 reusable mapping 정리 문서
- `.note/finance/phase4/PHASE4_STATEMENT_QUALITY_LOADER_FIRST_PASS.md`
  - strict statement 기반 quality snapshot을 loader 계층으로 올린 first-pass 정리 문서
- `.note/finance/phase4/PHASE4_STATEMENT_DRIVEN_BACKFILL_PLAN_FIRST_PASS.md`
  - statement-driven fundamentals/factors backfill을 시작하기 전 필요한 저장 전략과 rollout 순서를 정리한 문서
- `.note/finance/phase4/PHASE4_STATEMENT_SHADOW_TABLES_FIRST_PASS.md`
  - statement-driven fundamentals/factors를 shadow table에 first-pass로 write/read 검증한 구현 기록 문서
- `.note/finance/phase4/PHASE4_STATEMENT_SHADOW_SHARES_ENHANCEMENT_FIRST_PASS.md`
  - statement-driven shadow path에서 broad fundamentals fallback으로 shares/valuation 계열을 보강한 기록 문서
- `.note/finance/phase4/PHASE4_EXTENDED_STATEMENT_REFRESH_VERIFICATION_AND_SHADOW_REBUILD.md`
  - 사용자가 실행한 extended statement refresh 이후 annual/quarterly coverage와 shadow rebuild 결과를 검증한 문서
- `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_PERIOD_LIMIT_FIX_AND_COVERAGE_EXPANSION.md`
  - annual statement collector의 period-limit semantics를 reported-period 기준으로 고치고 sample-universe annual strict coverage를 확장한 기록 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_QUALITY_PUBLIC_CANDIDATE_FIRST_PASS.md`
  - strict annual statement-driven quality path를 Backtest UI의 public candidate 전략으로 노출한 기록 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_QUALITY_PUBLIC_ROLE_AND_DEFAULT_UNIVERSE.md`
  - strict annual quality의 public 역할과 wider stock-universe 기본 preset을 재정의한 문서
- `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_COVERAGE_OPERATOR_SUPPORT_FIRST_PASS.md`
  - wider-universe annual statement coverage 실행 전에 extended statement refresh/operator progress를 보강한 기록 문서
- `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_COVERAGE_STAGE1_TOP100_RUN.md`
  - 시가총액 상위 100개 profile-filtered stocks를 대상으로 annual statement coverage stage 1 run을 수행하고 결과를 정리한 문서
- `.note/finance/phase4/PHASE4_ANNUAL_STATEMENT_COVERAGE_STAGE2_US_TOP300_RUN.md`
  - United States issuer top-300 profile-filtered stocks를 대상으로 annual statement coverage stage 2 run을 수행하고 strict annual path 확장성을 검증한 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_SHADOW_FACTOR_OPTIMIZATION_FIRST_PASS.md`
  - strict annual public 경로를 statement shadow factors 기반 fast path로 최적화하고 prototype parity를 확인한 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_INTERPRETATION_AND_VALUE_STRICT_FIRST_PASS.md`
  - strict annual 전략의 selection history 해석 UI와 Value Snapshot (Strict Annual) public candidate 추가를 정리한 문서
- `.note/finance/phase4/PHASE4_ANNUAL_COVERAGE_OPERATORIZATION_PRESETS_FIRST_PASS.md`
  - strict annual annual coverage preset을 ingestion/operator 흐름에 재사용 가능하게 만든 기록 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_LARGE_UNIVERSE_CALENDAR_FIX_FIRST_PASS.md`
  - strict annual large stock universe에서 full date intersection 대신 union calendar를 사용하도록 바꾸고 sparse issue를 해결한 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_FINAL_MONTH_PRICE_REFRESH_VERIFICATION.md`
  - strict annual coverage 300의 duplicated final-month row가 uneven daily price freshness 때문이었음을 확인하고 targeted refresh로 해소한 검증 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_PRICE_FRESHNESS_PREFLIGHT_FIRST_PASS.md`
  - strict annual single-strategy UI와 runtime meta에 price freshness preflight를 추가한 기록 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_PRICE_FRESHNESS_PREFLIGHT_SECOND_PASS.md`
  - strict annual preflight가 stale/missing symbol 대응 payload와 preset status note까지 보여주도록 확장한 문서
- `.note/finance/phase4/PHASE4_STRICT_FAMILY_COMPARISON_EVALUATION.md`
  - strict annual family에서 quality/value public candidate를 같은 조건으로 비교 평가한 문서
- `.note/finance/phase4/PHASE4_COMPLETION_SUMMARY.md`
  - unified Backtest UI와 strict annual family까지 포함한 Phase 4 종료 요약 문서
- `.note/finance/phase4/PHASE4_NEXT_PHASE_PREPARATION.md`
  - Phase 4 이후 next-phase 후보와 kickoff 전 확인 포인트를 정리한 문서
- `.note/finance/phase4/PHASE4_QUALITY_FACTOR_EXPANSION_OPTIONS.md`
  - strict annual wider-universe 기준 quality factor 확장 후보의 coverage와 추천안을 정리한 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_QUALITY_FACTOR_SET_REFRESH_FIRST_PASS.md`
  - strict annual quality 기본 factor set을 coverage-first 방향으로 재정렬하고 current public default를 재검증한 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_WIDER_UNIVERSE_STAGE3_CURRENT_DB_AUDIT.md`
  - current DB 기준으로 `US Statement Coverage 500/1000`을 audit하고 wider-universe stage 3 readiness를 평가한 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_PUBLIC_UNIVERSE_DECISION_CURRENT_DB.md`
  - current DB audit 기준 strict annual public default universe를 `300`으로 유지한 결정 문서
- `.note/finance/phase4/PHASE4_STRICT_MULTIFACTOR_PUBLIC_CANDIDATE_FIRST_PASS.md`
  - `Quality + Value Snapshot (Strict Annual)` first public multi-factor candidate를 추가하고 first-pass 성능을 정리한 문서
- `.note/finance/phase4/PHASE4_STRICT_ANNUAL_OPERATOR_AUTOMATION_FIRST_PASS.md`
  - strict annual operator helper `run_strict_annual_shadow_refresh(...)`를 추가하고 반복 maintenance path를 정리한 문서
- `.note/finance/phase4/PHASE4_COVERAGE1000_AND_VALUE_STRICT_CLOSEOUT.md`
  - `Coverage 1000` closeout 판단과 `Value Snapshot (Strict Annual)`의 2016-start recovery를 함께 정리한 문서

---

## 6. Phase 5 상위 문서

- `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md`
  - strict factor strategy library 확장과 risk overlay를 다음 major phase의 공식 방향으로 정리한 문서
- `.note/finance/phase5/PHASE5_CURRENT_CHAPTER_TODO.md`
  - Phase 5 첫 챕터 TODO 보드
- `.note/finance/phase5/PHASE5_BASELINE_STRICT_FAMILY_COMPARATIVE_RESEARCH.md`
  - strict annual family의 canonical compare/single baseline을 고정한 문서
- `.note/finance/phase5/PHASE5_COMPARE_ADVANCED_INPUT_PARITY_FIRST_PASS.md`
  - compare 화면에서 strict factor 전략별 preset/factor/overlay 입력을 조절할 수 있게 한 first-pass 구현 문서
- `.note/finance/phase5/PHASE5_FIRST_OVERLAY_REQUIREMENTS_AND_SELECTION.md`
  - first overlay 요구사항과 선정 결과를 고정한 문서
- `.note/finance/phase5/PHASE5_OVERLAY_RUNTIME_FIRST_PASS.md`
  - strict family의 month-end trend filter overlay first-pass 구현 문서
- `.note/finance/phase5/PHASE5_FIRST_OVERLAY_ON_OFF_VALIDATION.md`
  - strict family first overlay의 on/off 비교 결과를 canonical preset 기준으로 정리한 문서
- `.note/finance/phase5/PHASE5_STALE_REASON_CLASSIFICATION_FIRST_PASS.md`
  - strict preflight stale / missing symbol에 heuristic reason을 붙인 first-pass 진단 문서
- `.note/finance/phase5/PHASE5_STRICT_FAMILY_TEST_CHECKLIST.md`
  - strict family single / compare / overlay / preflight / history 테스트 체크리스트 문서
- `.note/finance/phase5/PHASE5_PRACTICAL_INVESTMENT_READINESS_POLICY.md`
  - strict managed universe를 historical-backtest 우선 기준으로 운영하기 위한 freshness / transparency 정책 문서
- `.note/finance/phase5/PHASE5_MANAGED_UNIVERSE_FRESHNESS_BACKFILL_FIRST_PASS.md`
  - freshness-aware backfill 실험과 이후 historical-only 방향으로의 롤백 결정을 기록한 문서
- `.note/finance/phase5/PHASE5_QUARTERLY_STRICT_FAMILY_REVIEW.md`
  - quarterly strict family를 언제 여는 것이 맞는지 review한 문서
- `.note/finance/phase5/PHASE5_SECOND_OVERLAY_CANDIDATE_REVIEW.md`
  - first overlay 다음 후보 overlay 우선순위를 정리한 문서

---

## 7. Phase 2 / Phase 3 - Backtest / Loader 관련 문서

- `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
  - loader 함수 초안
- `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
  - loader 입력 계약
- `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`
  - point-in-time 원칙
- `.note/finance/phase2/STRICT_PIT_LOADER_QUERY_DRAFT.md`
  - strict PIT loader query 초안

---

## 8. Phase 2 - Point-In-Time / 재무제표 정리 문서

- `.note/finance/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`
  - point-in-time 스키마 리뷰와 패치 계획
- `.note/finance/phase2/POINT_IN_TIME_BACKFILL_AND_CONSTRAINT_STRATEGY.md`
  - backfill 및 stricter constraint 전략

---

## 9. 운영 / 설정 / 수집 전략 문서

- `.note/finance/DATA_COLLECTION_UI_STRATEGY.md`
  - 내부 운영 수집 UI 전략
- `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - 설정 외부화 후보와 우선순위
- `.note/finance/OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md`
  - OHLCV / 재무 적재 기능 점검 문서

---

## 10. 문서 사용 순서 권장

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
