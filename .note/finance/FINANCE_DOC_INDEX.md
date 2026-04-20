# Finance Documentation Index

## 목적

이 문서는 `.note/finance/` 아래 문서를 빠르게 찾기 위한 지도다.

읽는 순서는 보통 아래처럼 잡는다.

1. 지금 진행 중인 phase를 확인한다.
2. 해당 phase의 `Plan`, `TODO`, `Test Checklist`를 본다.
3. 구현 구조가 궁금하면 `FINANCE_COMPREHENSIVE_ANALYSIS.md`를 본다.
4. 용어가 헷갈리면 `FINANCE_TERM_GLOSSARY.md`를 본다.
5. 백테스트 결과 문서는 `backtest_reports/BACKTEST_REPORT_INDEX.md`에서 찾는다.

---

## 1. 지금 먼저 볼 문서

| 목적 | 문서 |
|---|---|
| 전체 phase 현재 위치 | `.note/finance/MASTER_PHASE_ROADMAP.md` |
| 현재 active phase TODO | `.note/finance/phase25/PHASE25_CURRENT_CHAPTER_TODO.md` |
| Phase 25 계획 | `.note/finance/phase25/PHASE25_PRE_LIVE_OPERATING_SYSTEM_AND_DEPLOYMENT_READINESS_PLAN.md` |
| Phase 25 첫 작업 단위 | `.note/finance/phase25/PHASE25_PRE_LIVE_BOUNDARY_AND_OPERATING_FRAME_FIRST_WORK_UNIT.md` |
| Phase 25 QA 초안 | `.note/finance/phase25/PHASE25_TEST_CHECKLIST.md` |
| 최근 작업 로그 | `.note/finance/WORK_PROGRESS.md` |
| 최근 질문 / 설계 판단 | `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` |

현재 상태:

- `Phase 24`: `phase complete / manual_validation_completed`
- `Phase 25`: `active / first_work_unit_completed`

현재 한 줄 요약:

- Phase 25는 live trading이 아니라,
  `Real-Money 검증 신호`를 보고 `paper tracking / watchlist / hold / reject / re-review` 같은
  Pre-Live 운영 상태를 기록하는 체계를 만드는 단계다.

---

## 2. 상위 기준 문서

| 문서 | 역할 |
|---|---|
| `AGENTS.md` | 저장소 전체 작업 규칙, finance phase 운영 규칙, 문서화 규칙 |
| `.note/finance/MASTER_PHASE_ROADMAP.md` | 전체 phase 방향, 현재 위치, 다음 phase 흐름 |
| `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` | finance 시스템 구조와 구현 상태를 설명하는 큰 기술 문서 |
| `.note/finance/FINANCE_DOC_INDEX.md` | 지금 보고 있는 문서. finance 문서 지도 |
| `.note/finance/FINANCE_TERM_GLOSSARY.md` | 반복 용어 사전. `Real-Money`, `Pre-Live`, `Validation Frame` 같은 용어 확인 |
| `.note/finance/WORK_PROGRESS.md` | 최근 구현/문서 작업 로그 |
| `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` | 최근 질문, 설계 판단, 방향성 결정 로그 |
| `.note/finance/PHASE_PLAN_TEMPLATE.md` | phase plan 작성 템플릿 |
| `.note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md` | phase QA checklist 작성 템플릿 |
| `.note/finance/FINANCE_WORK_PROGRESS_POLICY.md` | work log를 어떻게 유지/아카이브할지 정한 정책 |

읽는 기준:

- 프로젝트 전체 방향은 `MASTER_PHASE_ROADMAP.md`
- 코드/시스템 구조는 `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- 문서 위치는 `FINANCE_DOC_INDEX.md`
- 용어는 `FINANCE_TERM_GLOSSARY.md`
- 현재 작업 상태는 `WORK_PROGRESS.md`

---

## 3. 현재 운영 / 저장 파일

| 문서 또는 파일 | 역할 |
|---|---|
| `.note/finance/CURRENT_CANDIDATE_REGISTRY_GUIDE.md` | current candidate registry 사용법 |
| `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` | current strongest candidate / near-miss append-only registry |
| `.note/finance/SAVED_PORTFOLIOS.jsonl` | saved portfolio 정의 저장 파일 |
| `.note/finance/BACKTEST_RUN_HISTORY.jsonl` | local backtest run history. 보통 commit하지 않음 |
| `.note/finance/WEB_APP_RUN_HISTORY.jsonl` | local web app run history. 보통 commit하지 않음 |
| `.note/finance/RUNTIME_ARTIFACT_HYGIENE.md` | runtime artifact를 어떻게 다룰지 정리한 문서 |

주의:

- `BACKTEST_RUN_HISTORY.jsonl`, `WEB_APP_RUN_HISTORY.jsonl`는 local/generated 성격이 강하다.
- 특별한 요청이 없으면 보통 commit 대상이 아니다.

---

## 4. Backtest Report 문서

| 문서 | 역할 |
|---|---|
| `.note/finance/backtest_reports/README.md` | backtest report 저장 위치 안내 |
| `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md` | durable backtest report 전용 index |
| `.note/finance/backtest_reports/strategies/README.md` | strategy별 hub / backtest log 안내 |
| `.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md` | 현재 실용 후보 요약 |
| `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md` | Value strict annual strategy hub |
| `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md` | Value strict annual 반복 실험 log |
| `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md` | Quality strict annual strategy hub |
| `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md` | Quality strict annual 반복 실험 log |
| `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md` | Quality + Value strict annual strategy hub |
| `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md` | Quality + Value strict annual 반복 실험 log |
| `.note/finance/backtest_reports/strategies/GTAA.md` | GTAA strategy hub |
| `.note/finance/backtest_reports/strategies/GTAA_BACKTEST_LOG.md` | GTAA 반복 실험 log |

대표 phase report 위치:

| Phase | 위치 |
|---|---|
| Phase 13 | `.note/finance/backtest_reports/phase13/` |
| Phase 14 | `.note/finance/backtest_reports/phase14/` |
| Phase 15 | `.note/finance/backtest_reports/phase15/` |
| Phase 16 | `.note/finance/backtest_reports/phase16/` |
| Phase 17 | `.note/finance/backtest_reports/phase17/` |
| Phase 18 | `.note/finance/backtest_reports/phase18/` |
| Phase 21 | `.note/finance/backtest_reports/phase21/` |
| Phase 22 | `.note/finance/backtest_reports/phase22/` |
| Phase 23 | `.note/finance/backtest_reports/phase23/` |
| Phase 24 | `.note/finance/backtest_reports/phase24/` |

backtest 결과를 찾을 때는 이 문서보다
`.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`를 먼저 본다.

---

## 5. Phase별 빠른 지도

| Phase | 상태 | 핵심 목적 | 먼저 볼 문서 |
|---|---|---|---|
| Phase 1 | completed | internal web app scope | `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md` |
| Phase 2 | completed | backtest loader / PIT guideline | `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md` |
| Phase 3 | completed | DB-backed loader/runtime foundation | `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md` |
| Phase 4 | completed | Backtest UI / first strategy library expansion | `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md` |
| Phase 5 | first chapter completed | strategy library / risk overlay | `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md` |
| Phase 6 | completed | market regime overlay / quarterly entry | `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md` |
| Phase 7 | completed | quarterly coverage / statement PIT hardening | `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md` |
| Phase 8 | implementation completed / manual validation pending | quarterly family expansion / operator polish | `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md` |
| Phase 9 | completed / manual validation pending | strict coverage policy / promotion gate | `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md` |
| Phase 10 | completed | historical dynamic PIT universe | `.note/finance/phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md` |
| Phase 11 | completed | portfolio productization / research workflow | `.note/finance/phase11/PHASE11_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md` |
| Phase 12 | completed | strategy surface consolidation / real-money hardening | `.note/finance/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md` |
| Phase 13 | completed / manual validation pending | deployment readiness / probation | `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md` |
| Phase 14 | practical closeout / manual validation pending | gate calibration / deployment workflow bridge | `.note/finance/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md` |
| Phase 15 | practical closeout / manual validation pending | candidate quality improvement | `.note/finance/phase15/PHASE15_CANDIDATE_QUALITY_IMPROVEMENT_PLAN.md` |
| Phase 16 | completed | downside refinement | `.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md` |
| Phase 17 | completed | structural downside improvement | `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md` |
| Phase 18 | practical closeout / manual validation pending | larger structural redesign | `.note/finance/phase18/PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md` |
| Phase 19 | phase complete / manual validation completed | structural contract expansion | `.note/finance/phase19/PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md` |
| Phase 20 | phase complete / manual validation completed | candidate workflow hardening | `.note/finance/phase20/PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md` |
| Phase 21 | phase complete / manual validation completed | integrated deep validation | `.note/finance/phase21/PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md` |
| Phase 22 | phase complete / manual validation completed | portfolio workflow development validation | `.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md` |
| Phase 23 | phase complete / manual validation completed | quarterly / alternate cadence productionization | `.note/finance/phase23/PHASE23_QUARTERLY_AND_ALTERNATE_CADENCE_PRODUCTIONIZATION_PLAN.md` |
| Phase 24 | phase complete / manual validation completed | new strategy expansion bridge | `.note/finance/phase24/PHASE24_NEW_STRATEGY_EXPANSION_AND_RESEARCH_IMPLEMENTATION_BRIDGE_PLAN.md` |
| Phase 25 | active / first work unit completed | pre-live operating system | `.note/finance/phase25/PHASE25_PRE_LIVE_OPERATING_SYSTEM_AND_DEPLOYMENT_READINESS_PLAN.md` |

---

## 6. Recent Phase Detail

최근 phase는 사용자가 자주 다시 확인하므로, 핵심 문서를 바로 찾을 수 있게 따로 둔다.

### Phase 25. Pre-Live Operating System And Deployment Readiness

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase25/PHASE25_PRE_LIVE_OPERATING_SYSTEM_AND_DEPLOYMENT_READINESS_PLAN.md` |
| TODO | `.note/finance/phase25/PHASE25_CURRENT_CHAPTER_TODO.md` |
| First work unit | `.note/finance/phase25/PHASE25_PRE_LIVE_BOUNDARY_AND_OPERATING_FRAME_FIRST_WORK_UNIT.md` |
| Test checklist | `.note/finance/phase25/PHASE25_TEST_CHECKLIST.md` |
| Completion draft | `.note/finance/phase25/PHASE25_COMPLETION_SUMMARY.md` |
| Next phase draft | `.note/finance/phase25/PHASE25_NEXT_PHASE_PREPARATION.md` |

한 줄 설명:

- Real-Money 검증 신호를 보고 후보를 `paper tracking / watchlist / hold / reject / re-review`로 관리하는 운영 체계를 만든다.

### Phase 24. New Strategy Expansion

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase24/PHASE24_NEW_STRATEGY_EXPANSION_AND_RESEARCH_IMPLEMENTATION_BRIDGE_PLAN.md` |
| TODO | `.note/finance/phase24/PHASE24_CURRENT_CHAPTER_TODO.md` |
| Work unit 1 | `.note/finance/phase24/PHASE24_RESEARCH_TO_IMPLEMENTATION_BRIDGE_FIRST_WORK_UNIT.md` |
| Work unit 2 | `.note/finance/phase24/PHASE24_UI_AND_REPLAY_INTEGRATION_SECOND_WORK_UNIT.md` |
| Test checklist | `.note/finance/phase24/PHASE24_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase24/PHASE24_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase24/PHASE24_NEXT_PHASE_PREPARATION.md` |
| Core/runtime report | `.note/finance/backtest_reports/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md` |
| UI/replay report | `.note/finance/backtest_reports/phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md` |

한 줄 설명:

- `Global Relative Strength`를 첫 신규 전략으로 구현하고 single / compare / history / saved replay까지 연결했다.

### Phase 23. Quarterly And Alternate Cadence Productionization

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase23/PHASE23_QUARTERLY_AND_ALTERNATE_CADENCE_PRODUCTIONIZATION_PLAN.md` |
| TODO | `.note/finance/phase23/PHASE23_CURRENT_CHAPTER_TODO.md` |
| Work unit 1 | `.note/finance/phase23/PHASE23_QUARTERLY_PRODUCTIONIZATION_FRAME_FIRST_WORK_UNIT.md` |
| Work unit 2 | `.note/finance/phase23/PHASE23_QUARTERLY_PORTFOLIO_HANDLING_CONTRACT_PARITY_SECOND_WORK_UNIT.md` |
| Work unit 3 | `.note/finance/phase23/PHASE23_HISTORY_AND_SAVED_REPLAY_CONTRACT_ROUNDTRIP_THIRD_WORK_UNIT.md` |
| Work unit 4 | `.note/finance/phase23/PHASE23_COMPARE_VARIANT_IMMEDIATE_REFRESH_FOURTH_WORK_UNIT.md` |
| Test checklist | `.note/finance/phase23/PHASE23_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase23/PHASE23_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase23/PHASE23_NEXT_PHASE_PREPARATION.md` |
| Smoke report | `.note/finance/backtest_reports/phase23/PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md` |

한 줄 설명:

- quarterly strict 계열을 prototype에서 제품 기능 수준으로 끌어올렸다.

### Phase 22. Portfolio Workflow Development Validation

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md` |
| TODO | `.note/finance/phase22/PHASE22_CURRENT_CHAPTER_TODO.md` |
| Work unit 1 | `.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md` |
| Work unit 2 | `.note/finance/phase22/PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md` |
| Test checklist | `.note/finance/phase22/PHASE22_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase22/PHASE22_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase22/PHASE22_NEXT_PHASE_PREPARATION.md` |
| Baseline report | `.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md` |
| Weight alternative report | `.note/finance/backtest_reports/phase22/PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md` |

한 줄 설명:

- weighted / saved portfolio workflow가 재현 가능한지 개발 검증했다. 투자 포트폴리오 승인이 아니다.

### Phase 21. Integrated Deep Backtest Validation

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase21/PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md` |
| TODO | `.note/finance/phase21/PHASE21_CURRENT_CHAPTER_TODO.md` |
| Work unit | `.note/finance/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md` |
| Test checklist | `.note/finance/phase21/PHASE21_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase21/PHASE21_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase21/PHASE21_NEXT_PHASE_PREPARATION.md` |
| Value report | `.note/finance/backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md` |
| Quality report | `.note/finance/backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md` |
| Quality + Value report | `.note/finance/backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md` |
| Portfolio bridge report | `.note/finance/backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md` |

한 줄 설명:

- annual strict family와 portfolio bridge를 같은 frame에서 다시 검증했다.

### Phase 20. Candidate Consolidation And Operator Workflow Hardening

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase20/PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md` |
| TODO | `.note/finance/phase20/PHASE20_CURRENT_CHAPTER_TODO.md` |
| Inventory | `.note/finance/phase20/PHASE20_OPERATOR_WORKFLOW_INVENTORY_FIRST_PASS.md` |
| Work unit 1 | `.note/finance/phase20/PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md` |
| Work unit 2 | `.note/finance/phase20/PHASE20_COMPARE_WEIGHTED_AND_SAVED_REENTRY_HARDENING_SECOND_WORK_UNIT.md` |
| Test checklist | `.note/finance/phase20/PHASE20_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase20/PHASE20_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase20/PHASE20_NEXT_PHASE_PREPARATION.md` |

한 줄 설명:

- current candidate를 compare / weighted / saved portfolio workflow로 다시 불러오는 흐름을 정리했다.

### Phase 19. Structural Contract Expansion

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase19/PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md` |
| TODO | `.note/finance/phase19/PHASE19_CURRENT_CHAPTER_TODO.md` |
| Work unit 1 | `.note/finance/phase19/PHASE19_REJECTED_SLOT_HANDLING_CONTRACT_FIRST_SLICE.md` |
| Work unit 2 | `.note/finance/phase19/PHASE19_HISTORY_AND_INTERPRETATION_CLEANUP_SECOND_SLICE.md` |
| Work unit 3 | `.note/finance/phase19/PHASE19_RISK_OFF_AND_WEIGHTING_INTERPRETATION_CLEANUP_THIRD_SLICE.md` |
| Test checklist | `.note/finance/phase19/PHASE19_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase19/PHASE19_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase19/PHASE19_NEXT_PHASE_PREPARATION.md` |

한 줄 설명:

- rejected-slot handling, weighting, risk-off 같은 처리 규칙을 사용자가 읽을 수 있는 contract 언어로 정리했다.

---

## 7. Earlier Phase Detail

오래된 phase는 문서 수가 많으므로 대표 문서만 둔다.
상세 파일은 각 phase 폴더에서 확인한다.

| Phase | 대표 문서 |
|---|---|
| Phase 1 | `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md` |
| Phase 1 | `.note/finance/phase1/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md` |
| Phase 2 | `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md` |
| Phase 2 | `.note/finance/phase2/PHASE2_COMPLETION_SUMMARY.md` |
| Phase 2 | `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md` |
| Phase 3 | `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md` |
| Phase 3 | `.note/finance/phase3/PHASE3_CHAPTER1_COMPLETION_SUMMARY.md` |
| Phase 3 | `.note/finance/phase3/PHASE3_DB_SAMPLE_ENTRYPOINTS.md` |
| Phase 3 | `.note/finance/phase3/PHASE3_RUNTIME_ADAPTER_PATH.md` |
| Phase 4 | `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md` |
| Phase 4 | `.note/finance/phase4/PHASE4_COMPLETION_SUMMARY.md` |
| Phase 4 | `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md` |
| Phase 4 | `.note/finance/phase4/PHASE4_STRICT_FAMILY_COMPARISON_EVALUATION.md` |
| Phase 5 | `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md` |
| Phase 5 | `.note/finance/phase5/PHASE5_CURRENT_CHAPTER_TODO.md` |
| Phase 5 | `.note/finance/phase5/PHASE5_COMPLETION_SUMMARY.md` |
| Phase 5 | `.note/finance/phase5/PHASE5_STRICT_FAMILY_TEST_CHECKLIST.md` |
| Phase 6 | `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md` |
| Phase 6 | `.note/finance/phase6/PHASE6_CURRENT_CHAPTER_TODO.md` |
| Phase 6 | `.note/finance/phase6/PHASE6_COMPLETION_SUMMARY.md` |
| Phase 6 | `.note/finance/phase6/PHASE6_TEST_CHECKLIST.md` |
| Phase 7 | `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md` |
| Phase 7 | `.note/finance/phase7/PHASE7_CURRENT_CHAPTER_TODO.md` |
| Phase 7 | `.note/finance/phase7/PHASE7_COMPLETION_SUMMARY.md` |
| Phase 7 | `.note/finance/phase7/PHASE7_TEST_CHECKLIST.md` |
| Phase 8 | `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md` |
| Phase 8 | `.note/finance/phase8/PHASE8_CURRENT_CHAPTER_TODO.md` |
| Phase 8 | `.note/finance/phase8/PHASE8_TEST_CHECKLIST.md` |
| Phase 9 | `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md` |
| Phase 9 | `.note/finance/phase9/PHASE9_CURRENT_CHAPTER_TODO.md` |
| Phase 9 | `.note/finance/phase9/PHASE9_TEST_CHECKLIST.md` |
| Phase 10 | `.note/finance/phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md` |
| Phase 10 | `.note/finance/phase10/PHASE10_CURRENT_CHAPTER_TODO.md` |
| Phase 10 | `.note/finance/phase10/PHASE10_COMPLETION_SUMMARY.md` |
| Phase 10 | `.note/finance/phase10/PHASE10_TEST_CHECKLIST.md` |
| Phase 11 | `.note/finance/phase11/PHASE11_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md` |
| Phase 11 | `.note/finance/phase11/PHASE11_CURRENT_CHAPTER_TODO.md` |
| Phase 11 | `.note/finance/phase11/PHASE11_COMPLETION_SUMMARY.md` |
| Phase 11 | `.note/finance/phase11/PHASE11_TEST_CHECKLIST.md` |
| Phase 12 | `.note/finance/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md` |
| Phase 12 | `.note/finance/phase12/PHASE12_CURRENT_CHAPTER_TODO.md` |
| Phase 12 | `.note/finance/phase12/PHASE12_COMPLETION_SUMMARY.md` |
| Phase 12 | `.note/finance/phase12/PHASE12_TEST_CHECKLIST.md` |
| Phase 13 | `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md` |
| Phase 13 | `.note/finance/phase13/PHASE13_CURRENT_CHAPTER_TODO.md` |
| Phase 13 | `.note/finance/phase13/PHASE13_COMPLETION_SUMMARY.md` |
| Phase 13 | `.note/finance/phase13/PHASE13_TEST_CHECKLIST.md` |
| Phase 14 | `.note/finance/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md` |
| Phase 14 | `.note/finance/phase14/PHASE14_CURRENT_CHAPTER_TODO.md` |
| Phase 14 | `.note/finance/phase14/PHASE14_COMPLETION_SUMMARY.md` |
| Phase 14 | `.note/finance/phase14/PHASE14_TEST_CHECKLIST.md` |
| Phase 15 | `.note/finance/phase15/PHASE15_CANDIDATE_QUALITY_IMPROVEMENT_PLAN.md` |
| Phase 15 | `.note/finance/phase15/PHASE15_CURRENT_CHAPTER_TODO.md` |
| Phase 15 | `.note/finance/phase15/PHASE15_COMPLETION_SUMMARY.md` |
| Phase 15 | `.note/finance/phase15/PHASE15_TEST_CHECKLIST.md` |
| Phase 16 | `.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md` |
| Phase 16 | `.note/finance/phase16/PHASE16_COMPLETION_SUMMARY.md` |
| Phase 16 | `.note/finance/phase16/PHASE16_TEST_CHECKLIST.md` |
| Phase 17 | `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md` |
| Phase 17 | `.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md` |
| Phase 17 | `.note/finance/phase17/PHASE17_COMPLETION_SUMMARY.md` |
| Phase 17 | `.note/finance/phase17/PHASE17_TEST_CHECKLIST.md` |
| Phase 18 | `.note/finance/phase18/PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md` |
| Phase 18 | `.note/finance/phase18/PHASE18_CURRENT_CHAPTER_TODO.md` |
| Phase 18 | `.note/finance/phase18/PHASE18_COMPLETION_SUMMARY.md` |
| Phase 18 | `.note/finance/phase18/PHASE18_TEST_CHECKLIST.md` |

---

## 8. Support Track

Support Track은 main finance feature phase가 아니라,
작업을 돕는 자동화 / plugin / registry / workflow tooling 관리 트랙이다.

| 문서 | 역할 |
|---|---|
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_AND_EXPERIMENT_PERSISTENCE_SUPPORT_TRACK_20260416.md` | support track 설명 |
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_AND_EXPERIMENT_PERSISTENCE_SUPPORT_PLAN_20260416.md` | support track 계획 |
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_PHASE_BUNDLE_AUTOMATION_FIRST_WORK_UNIT_20260416.md` | phase bundle bootstrap 작업 |
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_CURRENT_CANDIDATE_REGISTRY_AND_WORKFLOW_AUTOMATION_SECOND_WORK_UNIT_20260416.md` | current candidate registry / workflow 자동화 작업 |

---

## 9. Data Collection / Runtime / 운영 참고 문서

| 문서 | 역할 |
|---|---|
| `.note/finance/BACKTEST_REFINEMENT_CODE_FLOW_GUIDE.md` | Streamlit UI -> runtime -> finance strategy 흐름 안내 |
| `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md` | 설정값 외부화 inventory |
| `.note/finance/DATA_COLLECTION_UI_STRATEGY.md` | 데이터 수집 UI 방향 |
| `.note/finance/OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md` | OHLCV / 재무 데이터 수집 리뷰 |
| `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_ANALYSIS_20260328.md` | daily market update rate limit 분석 |
| `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_IMPLEMENTATION_20260328.md` | daily market update rate limit 대응 구현 |
| `.note/finance/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_PLAN_20260328.md` | daily market update 속도 개선 계획 |
| `.note/finance/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_IMPLEMENTATION_20260328.md` | daily market update 속도 개선 구현 |
| `.note/finance/DAILY_MARKET_UPDATE_SHORT_WINDOW_ACCELERATION_20260404.md` | short-window update 가속화 |

---

## 10. Research / 참고 자료

| 문서 | 역할 |
|---|---|
| `.note/finance/OVERLAY_CASH_POLICY_RESEARCH.md` | overlay cash policy research |
| `.note/finance/US_PUBLIC_PORTFOLIO_AND_STRATEGY_SOURCE_MAP_20260404.md` | 미국 공개 포트폴리오 / 전략 source map |
| `.note/finance/PLAYWRIGHT_MARKET_RESEARCH_PLAYBOOK_20260331.md` | Playwright 기반 market research playbook |
| `.note/finance/CODEX_PLUGIN_AND_SKILL_APPLICATION_REVIEW_20260413.md` | Codex plugin / skill 적용 리뷰 |
| `.note/finance/ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md` | Phase 18~25 roadmap rebase 논의용 문서 |

---

## 11. Archive

| 문서 | 역할 |
|---|---|
| `.note/finance/archive/README.md` | archive 안내 |
| `.note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md` | 2026-04-13 이전 work progress full archive |
| `.note/finance/archive/QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md` | 2026-04-13 이전 question / analysis full archive |

---

## 12. 새 문서를 추가할 때

새 phase 문서가 생기면 이 index에는 아래만 추가한다.

1. `Phase별 빠른 지도`에 phase 한 줄 추가
2. 최근 phase라면 `Recent Phase Detail`에 plan / TODO / work unit / checklist / completion 링크 추가
3. backtest result 문서라면 이 문서가 아니라 `backtest_reports/BACKTEST_REPORT_INDEX.md`를 우선 갱신
4. 반복 용어가 늘면 `FINANCE_TERM_GLOSSARY.md` 갱신

원칙:

- 이 문서는 상세 설명을 길게 담지 않는다.
- 상세 내용은 각 phase plan, completion summary, report index로 보낸다.
- 사용자가 “어디를 봐야 하는지”를 찾는 데 집중한다.
