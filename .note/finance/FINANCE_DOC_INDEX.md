# Finance Documentation Index

## 목적

이 문서는 `.note/finance/` 아래 문서를 빠르게 찾기 위한 지도다.

읽는 순서는 보통 아래처럼 잡는다.

1. 지금 진행 중인 phase를 확인한다.
2. 해당 phase의 `Plan`, `TODO`, `Test Checklist`를 본다.
3. 구현 구조가 궁금하면 `FINANCE_COMPREHENSIVE_ANALYSIS.md`를 본다.
4. 실제 코드 수정 흐름이 궁금하면 `code_analysis/README.md`를 본다.
5. 데이터 / DB 의미가 궁금하면 `data_architecture/README.md`를 본다.
6. 용어가 헷갈리면 `FINANCE_TERM_GLOSSARY.md`를 본다.
7. 백테스트 결과 문서는 `backtest_reports/BACKTEST_REPORT_INDEX.md`에서 찾는다.

---

## 1. 지금 먼저 볼 문서

| 목적 | 문서 |
|---|---|
| 전체 phase 현재 위치 | `.note/finance/MASTER_PHASE_ROADMAP.md` |
| 현재 active phase TODO | `.note/finance/phase26/PHASE26_CURRENT_CHAPTER_TODO.md` |
| Phase 26 계획 | `.note/finance/phase26/PHASE26_FOUNDATION_STABILIZATION_AND_BACKLOG_REBASE_PLAN.md` |
| Phase 26 첫 작업 단위 | `.note/finance/phase26/PHASE26_PHASE_STATUS_AND_BACKLOG_REBASE_FIRST_WORK_UNIT.md` |
| Phase 26 QA checklist draft | `.note/finance/phase26/PHASE26_TEST_CHECKLIST.md` |
| Phase 26 이후 roadmap | `.note/finance/MASTER_PHASE_ROADMAP.md` |
| 최근 작업 로그 | `.note/finance/WORK_PROGRESS.md` |
| 최근 질문 / 설계 판단 | `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` |

현재 상태:

| Phase | 진행 상태 | 검증 상태 | 메모 |
|---|---|---|---|
| Phase 25 | `complete` | `manual_qa_completed` | Pre-Live Review UI QA 완료 |
| Phase 26 | `active` | `not_ready_for_qa` | foundation backlog rebase 시작 |

현재 한 줄 요약:

- Phase 26은 새 전략 구현이나 투자 분석이 아니라,
  Phase 27~30을 안정적으로 진행하기 위해 과거 backlog와 현재 foundation gap을 다시 정렬하는 단계다.

---

## 2. 상위 기준 문서

| 문서 | 역할 |
|---|---|
| `AGENTS.md` | 저장소 전체 작업 규칙, finance phase 운영 규칙, 문서화 규칙 |
| `.note/finance/MASTER_PHASE_ROADMAP.md` | 전체 phase 방향, 현재 위치, 다음 phase 흐름 |
| `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md` | finance 시스템의 큰 구조와 현재 상태를 설명하는 high-level map |
| `.note/finance/code_analysis/README.md` | 코드 수정자가 보는 개발자용 flow 문서 index |
| `.note/finance/data_architecture/README.md` | 데이터 흐름, DB 구조, table 의미를 보는 data architecture index |
| `.note/finance/FINANCE_DOC_INDEX.md` | 지금 보고 있는 문서. finance 문서 지도 |
| `.note/finance/FINANCE_TERM_GLOSSARY.md` | 반복 용어 사전. `Real-Money`, `Pre-Live`, `Validation Frame` 같은 용어 확인 |
| `.note/finance/WORK_PROGRESS.md` | 최근 구현/문서 작업 로그 |
| `.note/finance/QUESTION_AND_ANALYSIS_LOG.md` | 최근 질문, 설계 판단, 방향성 결정 로그 |
| `.note/finance/PHASE_PLAN_TEMPLATE.md` | phase plan 작성 템플릿 |
| `.note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md` | phase QA checklist 작성 템플릿 |
| `.note/finance/operations/FINANCE_WORK_PROGRESS_POLICY.md` | work log를 어떻게 유지/아카이브할지 정한 정책 |

읽는 기준:

- 프로젝트 전체 방향은 `MASTER_PHASE_ROADMAP.md`
- 코드/시스템 구조는 `FINANCE_COMPREHENSIVE_ANALYSIS.md`
- 실제 코드 수정 흐름은 `code_analysis/README.md`
- 데이터 / DB 의미는 `data_architecture/README.md`
- 문서 위치는 `FINANCE_DOC_INDEX.md`
- 용어는 `FINANCE_TERM_GLOSSARY.md`
- 현재 작업 상태는 `WORK_PROGRESS.md`

---

## 3. 현재 운영 / 저장 파일

| 문서 또는 파일 | 역할 |
|---|---|
| `.note/finance/operations/README.md` | 운영성 문서 묶음 안내 |
| `.note/finance/operations/CURRENT_CANDIDATE_REGISTRY_GUIDE.md` | current candidate registry 사용법 |
| `.note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md` | pre-live candidate registry 사용법 |
| `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` | current strongest candidate / near-miss append-only registry |
| `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | pre-live 운영 상태 append-only registry. QA 과정에서 첫 active record가 생성됨 |
| `.note/finance/SAVED_PORTFOLIOS.jsonl` | saved portfolio 정의 저장 파일 |
| `.note/finance/BACKTEST_RUN_HISTORY.jsonl` | local backtest run history. 보통 commit하지 않음 |
| `.note/finance/WEB_APP_RUN_HISTORY.jsonl` | local web app run history. 보통 commit하지 않음 |
| `.note/finance/operations/RUNTIME_ARTIFACT_HYGIENE.md` | runtime artifact를 어떻게 다룰지 정리한 문서 |

주의:

- `BACKTEST_RUN_HISTORY.jsonl`, `WEB_APP_RUN_HISTORY.jsonl`는 local/generated 성격이 강하다.
- 특별한 요청이 없으면 보통 commit 대상이 아니다.

---

## 4. Code Analysis / Developer Flow 문서

| 문서 | 역할 |
|---|---|
| `.note/finance/code_analysis/README.md` | 코드 분석 문서의 기준, 갱신 조건, 읽는 순서 |
| `.note/finance/code_analysis/BACKTEST_RUNTIME_FLOW.md` | UI payload에서 runtime, loader, strategy, result bundle까지의 실행 흐름 |
| `.note/finance/code_analysis/DATA_DB_PIPELINE_FLOW.md` | data collection, DB persistence, loader read path 흐름 |
| `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md` | Backtest UI, Single Strategy, Compare, History, Saved Portfolio 흐름 |
| `.note/finance/code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md` | 새 strategy family를 제품에 추가할 때 따라야 하는 구현 흐름 |
| `.note/finance/code_analysis/AUTOMATION_SCRIPTS_GUIDE.md` | phase bootstrap, hygiene, candidate registry helper script 사용 기준 |
| `.note/finance/code_analysis/BACKTEST_REFINEMENT_CODE_FLOW_GUIDE.md` | 기존 backtest refinement 중심 code flow guide |

관리 기준:

- `FINANCE_COMPREHENSIVE_ANALYSIS.md`에는 큰 구조와 핵심 파일 역할만 유지한다.
- 현재 시스템의 큰 그림이 바뀌지 않은 작은 수정, 일회성 결과, phase 진행 상태는 `FINANCE_COMPREHENSIVE_ANALYSIS.md`에 누적하지 않는다.
- 실제 코드 수정 순서와 flow-level 상세는 `code_analysis/`에 기록한다.
- 작은 문구 수정, 일회성 실험 결과, phase 진행 내역은 code analysis 문서에 기록하지 않는다.

---

## 5. Data Architecture / DB 문서

| 문서 | 역할 |
|---|---|
| `.note/finance/data_architecture/README.md` | data architecture 문서의 읽는 순서와 갱신 기준 |
| `.note/finance/data_architecture/DATA_FLOW_MAP.md` | external source -> finance/data -> DB -> loader -> runtime 흐름 |
| `.note/finance/data_architecture/DB_SCHEMA_MAP.md` | DB와 주요 table 목록, table 성격 구분 |
| `.note/finance/data_architecture/TABLE_SEMANTICS.md` | table별 source / derived / shadow / convenience 의미 |
| `.note/finance/data_architecture/DATA_QUALITY_AND_PIT_NOTES.md` | PIT, look-ahead, survivorship, stale data 주의사항 |
| `.note/finance/code_analysis/DATA_DB_PIPELINE_FLOW.md` | data / DB 관련 코드를 수정할 때 보는 developer flow |

관리 기준:

- `data_architecture/`는 데이터와 DB의 의미를 관리한다.
- `code_analysis/DATA_DB_PIPELINE_FLOW.md`는 관련 코드를 어떻게 따라가고 수정할지 관리한다.
- `FINANCE_COMPREHENSIVE_ANALYSIS.md`에는 데이터 흐름과 DB 구조의 상위 요약만 남긴다.
- table별 상세 의미, PIT 세부 규칙, stale data 해석은 `data_architecture/`에서 관리한다.

---

## 6. Backtest Report 문서

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

## 7. Phase별 빠른 지도

### Phase 상태값 읽는 법

Phase 상태는 하나의 긴 문장으로 합치지 않고, 아래 두 축으로 나눠 읽는다.

- `진행 상태`: phase 작업 자체가 어디까지 왔는지
- `검증 상태`: 사용자 QA, checklist 확인, 또는 추가 확인이 필요한지

진행 상태 표준값:

| 진행 상태 | 쉬운 뜻 |
|---|---|
| `planned` | 계획만 있고 아직 본격 작업 전이다. |
| `active` | 지금 진행 중이다. |
| `partial_complete` | 일부 작업 단위만 끝났다. phase 전체 완료는 아니다. |
| `implementation_complete` | 구현과 문서 1차 작업은 끝났다. |
| `practical_closeout` | 현재 범위는 다음 단계로 넘길 수 있을 만큼 정리되었다. |
| `complete` | phase 자체가 종료되었다. |

검증 상태 표준값:

| 검증 상태 | 쉬운 뜻 |
|---|---|
| `not_ready_for_qa` | 아직 사용자 QA를 할 단계가 아니다. |
| `manual_qa_pending` | 사용자 checklist 확인이 남아 있다. |
| `manual_qa_completed` | 사용자 checklist 확인까지 끝났다. |
| `smoke_checked` | 최소 자동/스모크 검증은 됐다. 사용자 QA와는 별개다. |
| `legacy_unknown` | 예전 phase라 검증 상태가 명확히 분리되어 남아 있지 않다. |
| `not_applicable` | phase 검증 대상이 아닌 지원 트랙이나 참고 문서다. |

`first_chapter_completed`는 정식 chapter 체계가 아니다.
예전 문서에서 "첫 번째 큰 작업 묶음이 끝났다"는 뜻으로 남은 legacy 표현이며,
앞으로 새 phase 상태값으로는 사용하지 않는다.
일부 파일명에 남아 있는 `CURRENT_CHAPTER_TODO`도 과거 명명 관례이며,
현재 운영 단위는 chapter가 아니라 phase다.

| Phase | 진행 상태 | 검증 상태 | 다음 확인 | 핵심 목적 | 먼저 볼 문서 |
|---|---|---|---|---|---|
| Phase 1 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | internal web app scope | `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md` |
| Phase 2 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | backtest loader / PIT guideline | `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md` |
| Phase 3 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | DB-backed loader/runtime foundation | `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md` |
| Phase 4 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | Backtest UI / first strategy library expansion | `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md` |
| Phase 5 | `partial_complete` | `legacy_unknown` | legacy `first_chapter_completed` 의미만 유지 | strategy library / risk overlay | `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md` |
| Phase 6 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | market regime overlay / quarterly entry | `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md` |
| Phase 7 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | quarterly coverage / statement PIT hardening | `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md` |
| Phase 8 | `implementation_complete` | `manual_qa_pending` | 사용자 QA 필요 | quarterly family expansion / operator polish | `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md` |
| Phase 9 | `implementation_complete` | `manual_qa_pending` | 사용자 QA 필요 | strict coverage policy / promotion gate | `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md` |
| Phase 10 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | historical dynamic PIT universe | `.note/finance/phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md` |
| Phase 11 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | portfolio productization / research workflow | `.note/finance/phase11/PHASE11_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md` |
| Phase 12 | `practical_closeout` | `manual_qa_pending` | 사용자 QA 필요 | strategy surface consolidation / real-money hardening | `.note/finance/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md` |
| Phase 13 | `implementation_complete` | `manual_qa_pending` | 사용자 QA 필요 | deployment readiness / probation | `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md` |
| Phase 14 | `practical_closeout` | `manual_qa_pending` | 사용자 QA 필요 | gate calibration / deployment workflow bridge | `.note/finance/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md` |
| Phase 15 | `practical_closeout` | `manual_qa_pending` | 사용자 QA 필요 | candidate quality improvement | `.note/finance/phase15/PHASE15_CANDIDATE_QUALITY_IMPROVEMENT_PLAN.md` |
| Phase 16 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | downside refinement | `.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md` |
| Phase 17 | `complete` | `legacy_unknown` | 필요 시 과거 문서 확인 | structural downside improvement | `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md` |
| Phase 18 | `practical_closeout` | `manual_qa_pending` | 사용자 QA 필요 | larger structural redesign | `.note/finance/phase18/PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md` |
| Phase 19 | `complete` | `manual_qa_completed` | 없음 | structural contract expansion | `.note/finance/phase19/PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md` |
| Phase 20 | `complete` | `manual_qa_completed` | 없음 | candidate workflow hardening | `.note/finance/phase20/PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md` |
| Phase 21 | `complete` | `manual_qa_completed` | 없음 | integrated deep validation | `.note/finance/phase21/PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md` |
| Phase 22 | `complete` | `manual_qa_completed` | 없음 | portfolio workflow development validation | `.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md` |
| Phase 23 | `complete` | `manual_qa_completed` | 없음 | quarterly / alternate cadence productionization | `.note/finance/phase23/PHASE23_QUARTERLY_AND_ALTERNATE_CADENCE_PRODUCTIONIZATION_PLAN.md` |
| Phase 24 | `complete` | `manual_qa_completed` | 없음 | new strategy expansion bridge | `.note/finance/phase24/PHASE24_NEW_STRATEGY_EXPANSION_AND_RESEARCH_IMPLEMENTATION_BRIDGE_PLAN.md` |
| Phase 25 | `complete` | `manual_qa_completed` | 없음 | pre-live operating system | `.note/finance/phase25/PHASE25_PRE_LIVE_OPERATING_SYSTEM_AND_DEPLOYMENT_READINESS_PLAN.md` |
| Phase 26 | `active` | `not_ready_for_qa` | backlog rebase 진행 | foundation stabilization / backlog rebase | `.note/finance/phase26/PHASE26_FOUNDATION_STABILIZATION_AND_BACKLOG_REBASE_PLAN.md` |
| Phase 27 | `planned` | `not_ready_for_qa` | Phase 26 이후 | data integrity / backtest trust | `.note/finance/MASTER_PHASE_ROADMAP.md` |
| Phase 28 | `planned` | `not_ready_for_qa` | Phase 27 이후 | strategy family parity / cadence completion | `.note/finance/MASTER_PHASE_ROADMAP.md` |
| Phase 29 | `planned` | `not_ready_for_qa` | Phase 28 이후 | candidate review / recommendation workflow | `.note/finance/MASTER_PHASE_ROADMAP.md` |
| Phase 30 | `planned` | `not_ready_for_qa` | Phase 29 이후 | portfolio proposal / pre-live monitoring | `.note/finance/MASTER_PHASE_ROADMAP.md` |

---

## 8. Recent Phase Detail

최근 phase는 사용자가 자주 다시 확인하므로, 핵심 문서를 바로 찾을 수 있게 따로 둔다.

### Phase 26. Foundation Stabilization And Backlog Rebase

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase26/PHASE26_FOUNDATION_STABILIZATION_AND_BACKLOG_REBASE_PLAN.md` |
| TODO | `.note/finance/phase26/PHASE26_CURRENT_CHAPTER_TODO.md` |
| First work unit | `.note/finance/phase26/PHASE26_PHASE_STATUS_AND_BACKLOG_REBASE_FIRST_WORK_UNIT.md` |
| Test checklist draft | `.note/finance/phase26/PHASE26_TEST_CHECKLIST.md` |
| Completion draft | `.note/finance/phase26/PHASE26_COMPLETION_SUMMARY.md` |
| Next phase preparation | `.note/finance/phase26/PHASE26_NEXT_PHASE_PREPARATION.md` |

한 줄 설명:

- Phase 26은 새 전략 구현이나 투자 분석이 아니라, Phase 27~30을 진행하기 전에 과거 phase backlog와 현재 foundation gap을 다시 정리하는 phase다.
- Live Readiness / Final Approval은 Phase 30 이후 별도 phase로 둔다.

### Phase 25. Pre-Live Operating System And Deployment Readiness

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase25/PHASE25_PRE_LIVE_OPERATING_SYSTEM_AND_DEPLOYMENT_READINESS_PLAN.md` |
| TODO | `.note/finance/phase25/PHASE25_CURRENT_CHAPTER_TODO.md` |
| First work unit | `.note/finance/phase25/PHASE25_PRE_LIVE_BOUNDARY_AND_OPERATING_FRAME_FIRST_WORK_UNIT.md` |
| Second work unit | `.note/finance/phase25/PHASE25_PRE_LIVE_CANDIDATE_RECORD_CONTRACT_SECOND_WORK_UNIT.md` |
| Third work unit | `.note/finance/phase25/PHASE25_OPERATOR_REVIEW_WORKFLOW_THIRD_WORK_UNIT.md` |
| Fourth work unit | `.note/finance/phase25/PHASE25_PRE_LIVE_REVIEW_UI_FOURTH_WORK_UNIT.md` |
| Test checklist | `.note/finance/phase25/PHASE25_TEST_CHECKLIST.md` |
| Completion summary | `.note/finance/phase25/PHASE25_COMPLETION_SUMMARY.md` |
| Next phase preparation | `.note/finance/phase25/PHASE25_NEXT_PHASE_PREPARATION.md` |

한 줄 설명:

- Real-Money 검증 신호를 보고 후보를 `paper tracking / watchlist / hold / reject / re-review`로 관리하는 운영 체계를 만든다.
- 단순 상태값만 저장하는 것이 아니라, `operator_reason`, `next_action`, `review_date`, `tracking_plan`을 함께 남기는 다음 행동 기록이 핵심이다.
- Pre-Live 후보 운영 기록은 `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 저장하고,
  current candidate registry와는 pointer로 연결한다.
- `draft-from-current` helper로 current candidate에서 Pre-Live 기록 초안을 만들 수 있다.
- `Backtest > Pre-Live Review`에서 current candidate를 선택해 Pre-Live record를 저장하고 확인할 수 있다.

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

## 9. Earlier Phase Detail

오래된 phase도 phase별로 찾을 수 있게 나눈다.
다만 모든 파일을 다 넣으면 index가 다시 길어지므로,
각 phase에서 계속 관리할 대표 문서와 핵심 참고 문서만 둔다.

### Phase 18. Larger Structural Redesign

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase18/PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md` |
| TODO | `.note/finance/phase18/PHASE18_CURRENT_CHAPTER_TODO.md` |
| Work unit | `.note/finance/phase18/PHASE18_NEXT_RANKED_FILL_IMPLEMENTATION_FIRST_SLICE.md` |
| Test checklist | `.note/finance/phase18/PHASE18_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase18/PHASE18_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase18/PHASE18_NEXT_PHASE_PREPARATION.md` |

### Phase 17. Structural Downside Improvement

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md` |
| TODO | `.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md` |
| Work unit 1 | `.note/finance/phase17/PHASE17_PARTIAL_CASH_RETENTION_IMPLEMENTATION_FIRST_SLICE.md` |
| Work unit 2 | `.note/finance/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_IMPLEMENTATION_SECOND_SLICE.md` |
| Work unit 3 | `.note/finance/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_IMPLEMENTATION_THIRD_SLICE.md` |
| Test checklist | `.note/finance/phase17/PHASE17_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase17/PHASE17_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase17/PHASE17_NEXT_PHASE_PREPARATION.md` |

### Phase 16. Downside Refinement

| 종류 | 문서 |
|---|---|
| TODO | `.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md` |
| Work unit | `.note/finance/phase16/PHASE16_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md` |
| Work unit | `.note/finance/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md` |
| Work unit | `.note/finance/phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md` |
| Test checklist | `.note/finance/phase16/PHASE16_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase16/PHASE16_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase16/PHASE16_NEXT_PHASE_PREPARATION.md` |

### Phase 15. Candidate Quality Improvement

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase15/PHASE15_CANDIDATE_QUALITY_IMPROVEMENT_PLAN.md` |
| TODO | `.note/finance/phase15/PHASE15_CURRENT_CHAPTER_TODO.md` |
| Test checklist | `.note/finance/phase15/PHASE15_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase15/PHASE15_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase15/PHASE15_NEXT_PHASE_PREPARATION.md` |

### Phase 14. Real-Money Gate Calibration

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md` |
| TODO | `.note/finance/phase14/PHASE14_CURRENT_CHAPTER_TODO.md` |
| Key review | `.note/finance/phase14/PHASE14_PROMOTION_SHORTLIST_CALIBRATION_REVIEW_FIRST_PASS.md` |
| Key review | `.note/finance/phase14/PHASE14_DEPLOYMENT_WORKFLOW_BRIDGE_FIRST_PASS.md` |
| Test checklist | `.note/finance/phase14/PHASE14_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase14/PHASE14_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase14/PHASE14_NEXT_PHASE_PREPARATION.md` |

### Phase 13. Deployment Readiness And Probation

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md` |
| TODO | `.note/finance/phase13/PHASE13_CURRENT_CHAPTER_TODO.md` |
| Key workflow | `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_CHECKLIST_FIRST_PASS.md` |
| Key workflow | `.note/finance/phase13/PHASE13_PROBATION_AND_MONITORING_WORKFLOW_FIRST_PASS.md` |
| Test checklist | `.note/finance/phase13/PHASE13_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase13/PHASE13_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase13/PHASE13_NEXT_PHASE_PREPARATION.md` |

### Phase 12. Real-Money Strategy Promotion

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md` |
| TODO | `.note/finance/phase12/PHASE12_CURRENT_CHAPTER_TODO.md` |
| Contract | `.note/finance/phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md` |
| Audit matrix | `.note/finance/phase12/PHASE12_STRATEGY_PRODUCTION_AUDIT_MATRIX.md` |
| Test checklist | `.note/finance/phase12/PHASE12_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase12/PHASE12_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase12/PHASE12_NEXT_PHASE_PREPARATION.md` |

### Phase 11. Portfolio Productization And Research Workflow

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase11/PHASE11_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md` |
| TODO | `.note/finance/phase11/PHASE11_CURRENT_CHAPTER_TODO.md` |
| Work unit | `.note/finance/phase11/PHASE11_SAVED_PORTFOLIO_FIRST_PASS.md` |
| Execution prep | `.note/finance/phase11/PHASE11_EXECUTION_PREPARATION.md` |
| Test checklist | `.note/finance/phase11/PHASE11_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase11/PHASE11_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase11/PHASE11_NEXT_PHASE_PREPARATION.md` |

### Phase 10. Historical Dynamic PIT Universe

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md` |
| TODO | `.note/finance/phase10/PHASE10_CURRENT_CHAPTER_TODO.md` |
| Work unit 1 | `.note/finance/phase10/PHASE10_ANNUAL_STRICT_DYNAMIC_PIT_FIRST_PASS.md` |
| Work unit 2 | `.note/finance/phase10/PHASE10_DYNAMIC_PIT_SECOND_PASS_HARDENING.md` |
| Test checklist | `.note/finance/phase10/PHASE10_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase10/PHASE10_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase10/PHASE10_NEXT_PHASE_PREPARATION.md` |

### Phase 9. Strict Coverage Policy And Promotion Gate

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md` |
| TODO | `.note/finance/phase9/PHASE9_CURRENT_CHAPTER_TODO.md` |
| Decision | `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_DECISION.md` |
| Gate | `.note/finance/phase9/PHASE9_STRICT_FAMILY_PROMOTION_GATE.md` |
| Operator guide | `.note/finance/phase9/PHASE9_OPERATOR_DECISION_TREE.md` |
| Test checklist | `.note/finance/phase9/PHASE9_TEST_CHECKLIST.md` |

### Phase 8. Quarterly Strategy Family Expansion

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md` |
| TODO | `.note/finance/phase8/PHASE8_CURRENT_CHAPTER_TODO.md` |
| Key decision | `.note/finance/phase8/PHASE8_QUARTERLY_FAMILY_SCOPE_AND_COMPARE_DECISION.md` |
| Validation | `.note/finance/phase8/PHASE8_QUARTERLY_VALIDATION_FIRST_PASS.md` |
| Operator tooling | `.note/finance/phase8/PHASE8_OPERATOR_RUNTIME_AND_SHADOW_REBUILD_TOOLING.md` |
| Test checklist | `.note/finance/phase8/PHASE8_TEST_CHECKLIST.md` |

### Phase 7. Quarterly Coverage And Statement PIT Hardening

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md` |
| TODO | `.note/finance/phase7/PHASE7_CURRENT_CHAPTER_TODO.md` |
| Work unit | `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_HARDENING_FIRST_PASS.md` |
| Validation | `.note/finance/phase7/PHASE7_QUARTERLY_RERUN_VALIDATION.md` |
| Test checklist | `.note/finance/phase7/PHASE7_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase7/PHASE7_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase7/PHASE7_NEXT_PHASE_PREPARATION.md` |

### Phase 6. Overlay And Quarterly Expansion

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md` |
| TODO | `.note/finance/phase6/PHASE6_CURRENT_CHAPTER_TODO.md` |
| Requirement | `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_REQUIREMENTS.md` |
| Work unit | `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_FIRST_PASS.md` |
| Validation | `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_VALIDATION.md` |
| Test checklist | `.note/finance/phase6/PHASE6_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase6/PHASE6_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase6/PHASE6_NEXT_PHASE_PREPARATION.md` |

### Phase 5. Strategy Library And Risk Overlay

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md` |
| TODO | `.note/finance/phase5/PHASE5_CURRENT_CHAPTER_TODO.md` |
| Requirement | `.note/finance/phase5/PHASE5_FIRST_OVERLAY_REQUIREMENTS_AND_SELECTION.md` |
| Work unit | `.note/finance/phase5/PHASE5_OVERLAY_RUNTIME_FIRST_PASS.md` |
| Test checklist | `.note/finance/phase5/PHASE5_STRICT_FAMILY_TEST_CHECKLIST.md` |
| Completion | `.note/finance/phase5/PHASE5_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase5/PHASE5_NEXT_PHASE_PREPARATION.md` |

### Phase 4. Backtest UI And Strategy Library Expansion

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase4/PHASE4_UI_AND_BACKTEST_PLAN.md` |
| TODO | `.note/finance/phase4/PHASE4_CURRENT_CHAPTER_TODO.md` |
| UI scope | `.note/finance/phase4/PHASE4_FIRST_SCREEN_SCOPE.md` |
| Strategy comparison | `.note/finance/phase4/PHASE4_STRICT_FAMILY_COMPARISON_EVALUATION.md` |
| Weighted portfolio | `.note/finance/phase4/PHASE4_COMPARE_AND_WEIGHTED_PORTFOLIO_FIRST_PASS.md` |
| Completion | `.note/finance/phase4/PHASE4_COMPLETION_SUMMARY.md` |
| Next phase prep | `.note/finance/phase4/PHASE4_NEXT_PHASE_PREPARATION.md` |

### Phase 3. DB-Backed Runtime Foundation

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md` |
| TODO | `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md` |
| Runtime adapter | `.note/finance/phase3/PHASE3_RUNTIME_ADAPTER_PATH.md` |
| DB sample entrypoints | `.note/finance/phase3/PHASE3_DB_SAMPLE_ENTRYPOINTS.md` |
| PIT / loader policy | `.note/finance/phase3/PHASE3_STRICT_STATEMENT_LOADER_SCOPE.md` |
| Completion | `.note/finance/phase3/PHASE3_CHAPTER1_COMPLETION_SUMMARY.md` |

### Phase 2. Backtest Loader And PIT Guidelines

| 종류 | 문서 |
|---|---|
| Plan | `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md` |
| TODO | `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md` |
| PIT guideline | `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md` |
| Loader contract | `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md` |
| Schema review | `.note/finance/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md` |
| Completion | `.note/finance/phase2/PHASE2_COMPLETION_SUMMARY.md` |

### Phase 1. Internal Web App Scope

| 종류 | 문서 |
|---|---|
| Scope | `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md` |
| Development guide | `.note/finance/phase1/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md` |
| Job wrapper interface | `.note/finance/phase1/PHASE1_JOB_WRAPPER_INTERFACE.md` |

---

## 10. Support Track

Support Track은 main finance feature phase가 아니라,
작업을 돕는 자동화 / plugin / registry / workflow tooling 관리 트랙이다.

| 문서 | 역할 |
|---|---|
| `.note/finance/support_tracks/README.md` | support track 문서 묶음 안내 |
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_AND_EXPERIMENT_PERSISTENCE_SUPPORT_TRACK_20260416.md` | support track 설명 |
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_AND_EXPERIMENT_PERSISTENCE_SUPPORT_PLAN_20260416.md` | support track 계획 |
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_PHASE_BUNDLE_AUTOMATION_FIRST_WORK_UNIT_20260416.md` | phase bundle bootstrap 작업 |
| `.note/finance/support_tracks/RESEARCH_AUTOMATION_CURRENT_CANDIDATE_REGISTRY_AND_WORKFLOW_AUTOMATION_SECOND_WORK_UNIT_20260416.md` | current candidate registry / workflow 자동화 작업 |
| `.note/finance/support_tracks/CODEX_PLUGIN_AND_SKILL_APPLICATION_REVIEW_20260413.md` | Codex plugin / skill 적용 리뷰 |
| `.note/finance/support_tracks/ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md` | Phase 18~25 roadmap rebase 논의용 문서 |

---

## 11. Data Collection / Runtime / 운영 참고 문서

| 문서 | 역할 |
|---|---|
| `.note/finance/operations/README.md` | 운영성 문서 묶음 안내 |
| `.note/finance/code_analysis/BACKTEST_REFINEMENT_CODE_FLOW_GUIDE.md` | Streamlit UI -> runtime -> finance strategy 흐름 안내 |
| `.note/finance/operations/CONFIG_EXTERNALIZATION_INVENTORY.md` | 설정값 외부화 inventory |
| `.note/finance/operations/DATA_COLLECTION_UI_STRATEGY.md` | 데이터 수집 UI 방향 |
| `.note/finance/operations/OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md` | OHLCV / 재무 데이터 수집 리뷰 |
| `.note/finance/operations/daily_market_update/DAILY_MARKET_UPDATE_RATE_LIMIT_ANALYSIS_20260328.md` | daily market update rate limit 분석 |
| `.note/finance/operations/daily_market_update/DAILY_MARKET_UPDATE_RATE_LIMIT_IMPLEMENTATION_20260328.md` | daily market update rate limit 대응 구현 |
| `.note/finance/operations/daily_market_update/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_PLAN_20260328.md` | daily market update 속도 개선 계획 |
| `.note/finance/operations/daily_market_update/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_IMPLEMENTATION_20260328.md` | daily market update 속도 개선 구현 |
| `.note/finance/operations/daily_market_update/DAILY_MARKET_UPDATE_SHORT_WINDOW_ACCELERATION_20260404.md` | short-window update 가속화 |

---

## 12. Research / 참고 자료

| 문서 | 역할 |
|---|---|
| `.note/finance/research/README.md` | research note 묶음 안내 |
| `.note/finance/research/OVERLAY_CASH_POLICY_RESEARCH.md` | overlay cash policy research |
| `.note/finance/research/US_PUBLIC_PORTFOLIO_AND_STRATEGY_SOURCE_MAP_20260404.md` | 미국 공개 포트폴리오 / 전략 source map |
| `.note/finance/research/PLAYWRIGHT_MARKET_RESEARCH_PLAYBOOK_20260331.md` | Playwright 기반 market research playbook |

---

## 13. Archive

| 문서 | 역할 |
|---|---|
| `.note/finance/archive/README.md` | archive 안내 |
| `.note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md` | 2026-04-13 이전 work progress full archive |
| `.note/finance/archive/QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md` | 2026-04-13 이전 question / analysis full archive |
| `.note/finance/archive/FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md` | 예전 종합 분석 문서의 긴 legacy 구현 메모 원문 archive |

---

## 14. 새 문서를 추가할 때

새 phase 문서가 생기면 이 index에는 아래만 추가한다.

1. `Phase별 빠른 지도`에 phase 한 줄 추가
2. 최근 phase라면 `Recent Phase Detail`에 plan / TODO / work unit / checklist / completion 링크 추가
3. backtest result 문서라면 이 문서가 아니라 `backtest_reports/BACKTEST_REPORT_INDEX.md`를 우선 갱신
4. 반복 용어가 늘면 `FINANCE_TERM_GLOSSARY.md` 갱신

원칙:

- 이 문서는 상세 설명을 길게 담지 않는다.
- 상세 내용은 각 phase plan, completion summary, report index로 보낸다.
- 사용자가 “어디를 봐야 하는지”를 찾는 데 집중한다.
