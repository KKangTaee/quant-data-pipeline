# Finance Documentation Index

## 목적
이 문서는 `.note/finance/` 아래의 핵심 문서들을
역할과 Phase 기준으로 빠르게 찾기 위한 인덱스다.

---

## 1. 상위 기준 문서

- `AGENTS.md`
  - 앞으로 phase plan 문서를 만들 때 포함해야 하는 설명 섹션과 finance 작업 운영 규칙을 담은 저장소 기준 문서
- `.note/finance/PHASE_PLAN_TEMPLATE.md`
  - 앞으로 `finance` phase plan 문서를 만들 때 기본으로 따를 설명형 템플릿 문서
  - `slice` 같은 내부 표현보다 `작업 단위`, `첫 번째 작업`, `다음 작업`처럼 바로 이해되는 문장을 기본으로 쓰는 출발점이다
- `.note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md`
  - 앞으로 `finance` phase test checklist 문서를 만들 때 기본으로 따를 checkbox 중심 템플릿 문서
- `.note/finance/MASTER_PHASE_ROADMAP.md`
  - 전체 Phase 구조와 상위 진행 방향
- `.note/finance/ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md`
  - `Phase 18` 진행 중 시점에서 `Phase 19~25` 큰 그림을 다시 정리한 논의용 상위 로드맵 초안
- `.note/finance/phase19/PHASE19_STRUCTURAL_CONTRACT_EXPANSION_PLAN.md`
  - `Phase 19`가 무엇을 하는 phase인지, 왜 지금 필요한지, 어려운 용어가 무엇을 뜻하는지까지 쉽게 풀어쓴 kickoff 문서
- `.note/finance/phase19/PHASE19_CURRENT_CHAPTER_TODO.md`
  - `Phase 19` 현재 챕터 TODO 보드
- `.note/finance/phase19/PHASE19_REJECTED_SLOT_HANDLING_CONTRACT_FIRST_SLICE.md`
  - strict annual rejected-slot handling semantics를 explicit contract로 정리한 첫 번째 작업 문서
- `.note/finance/phase19/PHASE19_HISTORY_AND_INTERPRETATION_CLEANUP_SECOND_SLICE.md`
  - strict annual selection history와 interpretation summary를 explicit handling contract 언어로 다시 정리한 두 번째 작업 문서
- `.note/finance/phase19/PHASE19_RISK_OFF_AND_WEIGHTING_INTERPRETATION_CLEANUP_THIRD_SLICE.md`
  - strict annual history / interpretation surface에서 risk-off contract와 weighting contract까지 같은 operator-facing 언어로 정리한 세 번째 작업 문서
- `.note/finance/phase19/PHASE19_COMPLETION_SUMMARY.md`
  - `Phase 19`가 실제로 무엇을 정리했고 왜 검수 완료 기준으로 닫을 수 있는지 요약한 closeout 문서
- `.note/finance/phase19/PHASE19_NEXT_PHASE_PREPARATION.md`
  - `Phase 19` 이후 다음 phase 방향을 어떤 질문으로 이어가면 좋은지 정리한 handoff 문서
- `.note/finance/phase19/PHASE19_TEST_CHECKLIST.md`
  - `Phase 19` contract language 정리가 UI / history / interpretation / 문서에서 일관되게 읽히는지,
    그리고 `Advanced Inputs > Overlay`, `Advanced Inputs > Portfolio Handling & Defensive Rules` 안에서 각 contract 위치, 뜻, tooltip 가독성, always-on 처리 규칙을 다시 이해할 수 있는지 확인하기 위한 manual checklist
- `.note/finance/phase20/PHASE20_CANDIDATE_CONSOLIDATION_AND_OPERATOR_WORKFLOW_HARDENING_PLAN.md`
  - `Phase 20`가 무엇을 하는 phase인지, 왜 지금 필요한지, 현재 후보 관리 흐름을 왜 정리해야 하는지 설명하는 kickoff 문서
- `.note/finance/phase20/PHASE20_CURRENT_CHAPTER_TODO.md`
  - `Phase 20` 현재 챕터 TODO 보드
- `.note/finance/phase20/PHASE20_OPERATOR_WORKFLOW_INVENTORY_FIRST_PASS.md`
  - strongest candidate, compare, weighted portfolio, saved portfolio 흐름에서 실제로 어디가 불편한지 first-pass로 정리한 workflow inventory 문서
- `.note/finance/phase20/PHASE20_CURRENT_CANDIDATE_COMPARE_REENTRY_FIRST_WORK_UNIT.md`
  - current candidate registry를 `Compare & Portfolio Builder`로 다시 연결해,
    strongest candidate와 near-miss를 UI에서 바로 compare로 보내는 첫 실제 구현 단위를 정리한 문서
- `.note/finance/phase20/PHASE20_COMPARE_WEIGHTED_AND_SAVED_REENTRY_HARDENING_SECOND_WORK_UNIT.md`
  - compare source context를 weighted portfolio와 saved portfolio까지 이어서,
    compare 결과의 출처와 다음 행동이 더 직접적으로 보이게 만든 두 번째 구현 문서
- `.note/finance/phase20/PHASE20_CURRENT_CHAPTER_TODO.md`
  - current candidate re-entry QA 중 발견된 설명/재진입 UX 보강, strict annual compare regression bugfix,
    weighted builder 상단 context summary UX 정리, saved portfolio replay legacy-key bugfix,
    save / load / replay 의미 보강과 manual validation 완료까지 반영된 현재 execution board
- `.note/finance/phase20/PHASE20_COMPLETION_SUMMARY.md`
  - `Phase 20`이 실제로 무엇을 더 쉽게 만들었는지와 왜 검수 완료 기준으로 닫을 수 있는지 정리한 closeout 문서
- `.note/finance/phase20/PHASE20_NEXT_PHASE_PREPARATION.md`
  - `Phase 20` 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리한 handoff 문서
- `.note/finance/phase20/PHASE20_TEST_CHECKLIST.md`
  - current candidate 재진입, compare -> weighted 흐름, saved portfolio 재진입,
    `Save This Weighted Portfolio`, `Load Saved Setup Into Compare`, `Replay Saved Portfolio`가 현재 UI 이름과 실제 동작 기준으로 자연스럽게 읽히는지 확인하는 manual checklist
- `.note/finance/CURRENT_CANDIDATE_REGISTRY_GUIDE.md`
  - `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`가 무엇인지, 왜 필요한지, script로 어떻게 읽고 검증하는지 정리한 안내 문서
- `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl`
  - current strongest candidate와 near-miss를 machine-readable하게 남기는 append-only registry 파일
- `.note/finance/phase21/PHASE21_RESEARCH_AUTOMATION_AND_EXPERIMENT_PERSISTENCE_PLAN.md`
  - `Phase 21`가 무엇을 하는 phase인지, 왜 지금 automation과 persistence baseline이 필요한지 설명하는 kickoff 문서
- `.note/finance/phase21/PHASE21_CURRENT_CHAPTER_TODO.md`
  - `Phase 21` 현재 챕터 TODO 보드
- `.note/finance/phase21/PHASE21_PHASE_BUNDLE_AUTOMATION_FIRST_WORK_UNIT.md`
  - phase 문서 묶음을 자동 생성하는 script를 추가한 첫 번째 작업 문서
- `.note/finance/phase21/PHASE21_CURRENT_CANDIDATE_REGISTRY_AND_WORKFLOW_AUTOMATION_SECOND_WORK_UNIT.md`
  - current candidate registry와 hygiene/script integration을 정리한 두 번째 작업 문서
- `.note/finance/phase21/PHASE21_COMPLETION_SUMMARY.md`
  - `Phase 21`이 실제로 무엇을 자동화했고 왜 practical closeout으로 볼 수 있는지 요약한 문서
- `.note/finance/phase21/PHASE21_NEXT_PHASE_PREPARATION.md`
  - `Phase 21` 이후 어떤 질문으로 다음 phase를 여는 것이 자연스러운지 정리한 handoff 문서
- `.note/finance/phase21/PHASE21_TEST_CHECKLIST.md`
  - `Phase 21` automation/persistence baseline을 script와 문서 기준으로 확인하기 위한 manual checklist
- `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - `finance` 패키지 전체 구조와 DB/기능 종합 분석
- `.note/finance/WORK_PROGRESS.md`
  - 현재 active workstream만 남긴 concise 구현 진행 로그
- `.note/finance/FINANCE_WORK_PROGRESS_POLICY.md`
  - root `WORK_PROGRESS.md`를 유지하되, 로그가 커질 때는 월별이 아니라 phase별 worklog/archive로 분리하는 운영 기준 문서
- `.note/finance/QUESTION_AND_ANALYSIS_LOG.md`
  - 현재 active 설계 판단만 남긴 concise 질의/설계/분석 로그
- `.note/finance/archive/README.md`
  - root 로그를 압축한 뒤, full archive를 어디서 봐야 하는지 정리한 안내 문서
- `.note/finance/archive/WORK_PROGRESS_ARCHIVE_20260413.md`
  - 2026-04-13 시점까지의 full work progress archive
- `.note/finance/archive/QUESTION_AND_ANALYSIS_LOG_ARCHIVE_20260413.md`
  - 2026-04-13 시점까지의 full question/analysis archive
- `.note/finance/FINANCE_TERM_GLOSSARY.md`
  - 퀀트 / 백테스트 / 실전형 전략 관련 반복 용어를 `기본 설명 / 왜 사용되는지 / 예시 / 필요 상황` 구조로 정리하는 공통 용어 사전
  - 최근 strict annual UI QA에서 자주 물었던 `Benchmark Contract`, `Candidate Universe Equal-Weight` 같은 operator-facing 용어도 여기에서 다시 확인할 수 있다
  - `Candidate Universe Equal-Weight / SPY`처럼 contract와 reference ticker가 같이 보일 때의 의미도 이 glossary 기준으로 다시 읽을 수 있다
  - equal-weight contract에서 왜 입력 필드명이 `Guardrail / Reference Ticker`로 보일 수 있는지도 여기 용어 기준으로 다시 이해할 수 있다
  - 현재는 submit-form 특성 때문에 ticker 입력 필드 이름을 중립적으로 `Benchmark / Guardrail / Reference Ticker`로 두고, contract별 의미를 캡션으로 설명하는 이유도 여기 문맥으로 이어서 이해할 수 있다
  - 앱에서는 `Reference > Glossary`에서 검색형 UI로 바로 다시 볼 수 있다
- `.note/finance/BACKTEST_REFINEMENT_CODE_FLOW_GUIDE.md`
  - Streamlit UI, runtime adapter, finance engine, strategy 문서 흐름까지 backtest refinement code path를 한 장으로 정리한 안내 문서
- `.note/finance/RUNTIME_ARTIFACT_HYGIENE.md`
  - run history, artifacts, temp csv, scratch notebook 같은 runtime 산출물을 어떻게 해석하고 관리해야 하는지 정리한 운영 문서
- `.note/finance/CODEX_PLUGIN_AND_SKILL_APPLICATION_REVIEW_20260413.md`
  - Codex plugin/skill을 현재 프로젝트 workflow에 적용할 가치가 있는지와 repo-local draft 구성 판단을 정리한 문서
- `plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - current git diff를 기준으로 phase 문서, strategy hub / one-pager / backtest log, root concise logs, generated artifacts 상태를 한 번에 점검하는 repo-local checklist script
- `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py`
  - 새 phase plan / TODO / completion / next-phase / checklist 문서 묶음을 한 번에 생성하는 repo-local automation script
- `plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py`
  - current candidate registry를 seed, list, show, append, validate 하는 repo-local persistence helper
- `.note/finance/backtest_reports/README.md`
  - phase 문서와 분리해서, 결과 중심 backtest Markdown 문서를 어디에 두고 어떻게 관리할지 정리한 운영 안내 문서
- `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`
  - durable backtest 결과 리포트 전용 인덱스로, 앞으로 결과 중심 Markdown 문서를 따로 모아 관리하기 위한 문서
- `.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
  - 현재 `Value / Quality / Quality + Value` family에서 다시 볼 practical candidate를 한 장으로 요약한 문서
- `.note/finance/backtest_reports/strategies/BACKTEST_LOG_TEMPLATE.md`
  - 전략별 backtest log를 같은 형식으로 append하기 위한 공통 템플릿 문서
- `.note/finance/backtest_reports/strategies/GTAA_BACKTEST_LOG.md`
  - `GTAA` 전략 run 기록을 전략 기준으로 누적 관리하는 backtest log 문서
- `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Quality > Strict Annual` 전략 run 기록을 전략 기준으로 누적 관리하는 backtest log 문서
- `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md`
  - `Quality > Strict Annual` structural rescue search에서 current rescued candidate를 전략 구성 중심으로 정리한 one-pager
- `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
  - rescued `Quality > Strict Annual` anchor보다 `MDD`를 크게 낮춘 downside-improved current candidate를 전략 구성 중심으로 정리한 one-pager
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_ALTERNATE_CONTRACT_SEARCH_THIRD_PASS.md`
  - rescued `Quality > Strict Annual` downside-improved anchor 위에서 `benchmark / overlay` alternate contract를 다시 보고,
    strongest practical point와 cleaner alternative를 같이 고정한 문서
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Value > Strict Annual` 전략 run 기록을 전략 기준으로 누적 관리하는 backtest log 문서
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Quality + Value > Strict Annual` 전략 run 기록을 전략 기준으로 누적 관리하는 backtest log 문서
- `.note/finance/OVERLAY_CASH_POLICY_RESEARCH.md`
  - strict factor overlay의 partial rejection을 survivor reweighting으로 볼지, cash retention으로 볼지에 대한 실무 관행 조사와 현재 프로젝트 권고 문서
- `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_ANALYSIS_20260328.md`
  - `Daily Market Update`의 yfinance rate-limit 재현 결과와 first-pass 최적화 방향 분석 문서
- `.note/finance/DAILY_MARKET_UPDATE_RATE_LIMIT_IMPLEMENTATION_20260328.md`
  - `Daily Market Update` rate-limit 완화를 위한 1차/2차/3차 구현 요약과 검증 문서
- `.note/finance/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_PLAN_20260328.md`
  - 안정화 이후 속도 최적화 2차 계획 문서
- `.note/finance/DAILY_MARKET_UPDATE_SPEED_OPTIMIZATION_IMPLEMENTATION_20260328.md`
  - execution breakdown, managed-fast profile, source별 profile 분리 구현 요약 문서
- `.note/finance/DAILY_MARKET_UPDATE_SHORT_WINDOW_ACCELERATION_20260404.md`
  - `1d`/짧은 daily refresh가 `20y`와 비슷하게 느린 이유를 fetch 병목 기준으로 분석하고, short-window 전용 `managed_refresh_short` profile을 도입한 구현/검증 문서
- `.note/finance/PLAYWRIGHT_MARKET_RESEARCH_PLAYBOOK_20260331.md`
  - Playwright를 활용한 공개정보 기반 시장/기업 조사 프레임으로, 기관형 키워드별 3단계 리서치와 반복 운용용 5단계 보강안을 함께 정리한 플레이북
- `.note/finance/US_PUBLIC_PORTFOLIO_AND_STRATEGY_SOURCE_MAP_20260404.md`
  - 미국 유명 기관/펀드/투자자들의 포트폴리오와 공개 전략을 어디서 봐야 하는지 공식 소스 중심으로 정리한 source map
- `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
  - Phase 7 전체 계획 문서
- `.note/finance/phase7/PHASE7_CURRENT_CHAPTER_TODO.md`
  - Phase 7 현재 챕터 TODO 보드
- `.note/finance/phase7/PHASE7_STATEMENT_SOURCE_PAYLOAD_INSPECTION.md`
  - EDGAR statement source가 실제로 돌려주는 fact/filing/timing field reality check 문서
- `.note/finance/phase7/PHASE7_RAW_STATEMENT_LEDGER_REVIEW_AND_DECISION.md`
  - raw statement ledger의 역할 점검과 유지/수정 결정 문서
- `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_HARDENING_FIRST_PASS.md`
  - quarterly late-start를 줄이기 위한 first-pass 코드 변경과 coverage 회복 결과 문서
- `.note/finance/phase7/PHASE7_QUARTERLY_RERUN_VALIDATION.md`
  - quarterly strict prototype rerun validation 결과 문서
- `.note/finance/phase7/PHASE7_SUPPLEMENTARY_POLISH_PASS.md`
  - weekend/holiday-aware preflight와 quarterly shadow coverage preview를 정리한 실사용성 보강 문서
- `.note/finance/phase7/PHASE7_COMPLETION_SUMMARY.md`
  - Phase 7 implementation closeout 요약 문서
- `.note/finance/phase7/PHASE7_NEXT_PHASE_PREPARATION.md`
  - Phase 8 kickoff 전 다음 방향 정리 문서
- `.note/finance/phase7/PHASE7_TEST_CHECKLIST.md`
  - Phase 7 manual validation checklist
- `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
  - Phase 8 전체 계획 문서
- `.note/finance/phase8/PHASE8_CURRENT_CHAPTER_TODO.md`
  - Phase 8 현재 챕터 TODO 보드
- `.note/finance/phase8/PHASE8_QUARTERLY_FAMILY_SCOPE_AND_COMPARE_DECISION.md`
  - quarterly strict family 3종의 naming / research-only 역할 / compare exposure 정책 문서
- `.note/finance/phase8/PHASE8_QUARTERLY_VALUE_AND_MULTI_FACTOR_FIRST_PASS.md`
  - quarterly value / quality+value prototype first-pass 구현 기록 문서
- `.note/finance/phase8/PHASE8_QUARTERLY_VALIDATION_FIRST_PASS.md`
  - quarterly family first-pass smoke / preset / compare 검증 문서
- `.note/finance/phase8/PHASE8_PROMOTION_READINESS_CRITERIA_DRAFT.md`
  - quarterly strict family의 research-only 유지 기준과 향후 promotion 판단 기준 초안
- `.note/finance/phase8/PHASE8_PRICE_STALE_DIAGNOSIS_FIRST_PASS.md`
  - stale price symbol을 DB gap / provider gap / likely delisted 쪽으로 좁히는 read-only diagnosis 카드 구현 문서
- `.note/finance/phase8/PHASE8_STATEMENT_SHADOW_COVERAGE_GAP_DIAGNOSTICS.md`
  - quarterly prototype의 `Statement Shadow Coverage Preview`에서 missing symbol drilldown과 targeted statement refresh payload를 제공하는 진단 보강 문서
- `.note/finance/phase8/PHASE8_INGESTION_UI_POLISH_AND_REVIEW.md`
  - Ingestion 화면의 Write Targets 제거, run-job expander 전환, Recent Logs / Failure CSV Preview 검토 결과와 후속 권고 문서
- `.note/finance/phase8/PHASE8_OPERATOR_RUNTIME_AND_SHADOW_REBUILD_TOOLING.md`
  - Runtime / Build indicator, Statement Shadow Rebuild Only helper, coverage-gap action bridge, Run Inspector, standardized run artifacts 문서
- `.note/finance/phase8/PHASE8_STATEMENT_COVERAGE_DIAGNOSIS_GUIDANCE.md`
  - coverage-missing symbol을 raw recollection / shadow rebuild / source-structure / symbol-source issue로 분류하고 단계별 가이드를 제공하는 operator 문서
- `.note/finance/phase8/PHASE8_TEST_CHECKLIST.md`
  - Phase 8 manual validation checklist
- `.note/finance/phase8/PHASE8_CHECKLIST_PREVALIDATION.md`
  - assistant가 Phase 8 checklist를 먼저 자동 점검한 결과 문서
- `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md`
  - strict coverage exception policy, foreign-form handling, public promotion gate를 다음 단계에서 어떻게 정리할지에 대한 Phase 9 guidance 문서
- `.note/finance/phase9/PHASE9_CURRENT_CHAPTER_TODO.md`
  - Phase 9의 현재 실행 보드로, strict coverage exception inventory / foreign-form policy / promotion gate 작업 상태를 관리하는 문서
- `.note/finance/phase9/PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md`
  - current strict preset을 어디까지 실전 투자 판단 근거로 볼 수 있는지와, policy 고정 이후 `historical dynamic PIT universe`를 다음 우선 구현으로 둘지에 대한 권고 문서
- `.note/finance/phase9/PHASE9_STRICT_COVERAGE_EXCEPTION_INVENTORY.md`
  - current preset에서 실제로 관찰되는 strict coverage gap bucket, 대표 심볼, diagnosis 분포를 정리한 inventory 문서
- `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_DECISION.md`
  - diagnostics bucket을 `eligible / review_needed / excluded` 정책으로 연결하고 canonical preset 유지 원칙을 고정한 문서
- `.note/finance/phase9/PHASE9_STRICT_FAMILY_PROMOTION_GATE.md`
  - strict annual / quarterly family의 public-candidate / research-only 경계를 정리한 승격 기준 문서
- `.note/finance/phase9/PHASE9_OPERATOR_DECISION_TREE.md`
  - preflight / diagnosis / rebuild / recollection / exclusion을 어떤 순서로 해석할지 정리한 운영 decision tree 문서
- `.note/finance/phase9/PHASE9_TEST_CHECKLIST.md`
  - Phase 9 policy / governance / promotion 문구를 현재 구현과 함께 검수하기 위한 checklist 문서
- `.note/finance/phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md`
  - current static preset과 분리된 rebalance-date historical dynamic PIT universe mode를 다음 실제 구현 workstream으로 여는 계획 문서
- `.note/finance/phase10/PHASE10_CURRENT_CHAPTER_TODO.md`
  - Phase 10 dynamic PIT universe 실행 보드 초안으로, contract / source inventory / annual strict first pass / validation 항목을 관리하는 문서
- `.note/finance/phase10/PHASE10_PIT_SOURCE_AND_SCHEMA_GAP_ANALYSIS.md`
  - current DB/schema 기준으로 dynamic PIT universe 구현에 바로 활용 가능한 데이터와 부족한 데이터를 구분한 gap analysis 문서
- `.note/finance/phase10/PHASE10_DYNAMIC_PIT_FIRST_PASS_IMPLEMENTATION_ORDER.md`
  - annual strict family + rebalance-date approximate PIT market-cap universe를 기준으로 한 first-pass 구현 순서 문서
- `.note/finance/phase10/PHASE10_ANNUAL_STRICT_DYNAMIC_PIT_FIRST_PASS.md`
  - annual strict single-strategy form에 `Historical Dynamic PIT Universe`를 first pass로 연결하고, candidate-pool / target-size / universe-debug contract를 정리한 구현 요약 문서
- `.note/finance/phase10/PHASE10_DYNAMIC_PIT_SECOND_PASS_HARDENING.md`
  - continuity / delisting diagnostics, history artifact persistence, quarterly dynamic PIT first pass 확장, approximate PIT contract 한계를 함께 정리한 second-pass hardening 문서
- `.note/finance/phase10/PHASE10_COMPLETION_SUMMARY.md`
  - Phase 10 dynamic PIT universe workstream의 practical closeout 요약 문서
- `.note/finance/phase10/PHASE10_NEXT_PHASE_PREPARATION.md`
  - Phase 10 종료 이후 Phase 11 productization/workflow 방향으로 어떻게 이어갈지 정리한 handoff 문서
- `.note/finance/phase10/PHASE10_TEST_CHECKLIST.md`
  - dynamic PIT universe mode가 current static mode와 구분되는 실전형 validation contract로 동작하는지 확인하는 checklist 문서
- `.note/finance/phase11/PHASE11_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md`
  - 전략 조합, 저장 가능한 포트폴리오, compare-to-portfolio bridge를 제품형 workflow로 확장하기 위한 Phase 11 guidance 문서
- `.note/finance/phase11/PHASE11_CURRENT_CHAPTER_TODO.md`
  - Phase 11 현재 실행 보드로, saved portfolio first pass 진행 상태와 남은 productization backlog를 관리하는 문서
- `.note/finance/phase11/PHASE11_EXECUTION_PREPARATION.md`
  - Phase 11을 바로 열어도 흔들리지 않도록 chapter별 구현 순서와 선행 확인 사항을 정리한 준비 문서
- `.note/finance/phase11/PHASE11_SAVED_PORTFOLIO_FIRST_PASS.md`
  - saved portfolio store, load-into-compare bridge, saved portfolio rerun, weighted result meta 보강까지 포함한 Phase 11 first-pass 구현 요약 문서
- `.note/finance/phase11/PHASE11_COMPLETION_SUMMARY.md`
  - saved portfolio workflow first pass를 practical closeout으로 정리한 Phase 11 종료 요약 문서
- `.note/finance/phase11/PHASE11_NEXT_PHASE_PREPARATION.md`
  - Phase 11 이후 real-money strategy promotion phase로 어떻게 handoff할지 정리한 문서
- `.note/finance/phase11/PHASE11_TEST_CHECKLIST.md`
  - Phase 11 구현 이후 later batch review에서 사용할 productization checklist 문서
- `.note/finance/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
  - 현재 전략군을 실전형 계약으로 승격하기 위한 Phase 12 상위 계획 문서
- `.note/finance/phase12/PHASE12_CURRENT_CHAPTER_TODO.md`
  - Phase 12 현재 실행 보드로, strategy audit / promotion contract / ETF-first hardening 순서를 관리하는 문서
- `.note/finance/phase12/PHASE12_STRATEGY_PRODUCTION_AUDIT_MATRIX.md`
  - current strategy family를 production-priority / baseline / research-only로 재분류한 audit 문서
- `.note/finance/phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
  - 실전 전략 승격에 필요한 공통 contract를 정리한 문서
- `.note/finance/phase12/PHASE12_COMPLETION_SUMMARY.md`
  - Phase 12 real-money strategy promotion workstream을 practical closeout 기준으로 정리한 요약 문서
- `.note/finance/phase12/PHASE12_NEXT_PHASE_PREPARATION.md`
  - Phase 12 이후 어떤 deployment-readiness / probation 방향으로 이어가는 것이 자연스러운지 정리한 handoff 문서
- `.note/finance/phase12/PHASE12_ETF_REAL_MONEY_HARDENING_FIRST_PASS.md`
  - ETF 전략 3종에 `Minimum Price`, `Transaction Cost`, benchmark overlay, gross-vs-net result surface, history/prefill contract를 first pass로 연결한 구현 요약 문서
- `.note/finance/phase12/PHASE12_ETF_AUM_AND_SPREAD_POLICY_FIRST_PASS.md`
  - ETF 전략 3종에 `Min ETF AUM ($B)`, `Max Bid-Ask Spread (%)` current-operability policy를 추가하고, asset profile schema 확장과 promotion/readout 연동까지 정리한 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_REAL_MONEY_HARDENING_FIRST_PASS.md`
  - strict annual family 3종에 `Minimum Price`, `Transaction Cost`, benchmark overlay, real-money result surface, single/compare/history contract를 first pass로 연결한 구현 요약 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_VALIDATION_SURFACE_SECOND_PASS.md`
  - strict annual family의 benchmark-relative drawdown / rolling underperformance 진단과 `validation_status`, `promotion_decision` surface를 second pass로 보강한 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_UNDERPERFORMANCE_GUARDRAIL_FIRST_PASS.md`
  - strict annual family에 optional benchmark-relative trailing excess return guardrail을 실제 전략 규칙으로 연결하고, single / compare / history / real-money surface까지 같이 연결한 first-pass 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_INVESTABILITY_AND_BENCHMARK_REINFORCEMENT_FIRST_PASS.md`
  - strict annual family에 `Minimum History (Months)` investability proxy와 `Benchmark CAGR` / `Net CAGR Spread` / `Benchmark Coverage`를 first pass로 추가한 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_LIQUIDITY_PROXY_FIRST_PASS.md`
  - strict annual family에 `Min Avg Dollar Volume 20D ($M)` later-pass liquidity proxy를 추가하고, single / compare / history / meta surface까지 연결한 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_BENCHMARK_POLICY_AND_PROMOTION_REINFORCEMENT_LATER_PASS.md`
  - strict annual family에 `Min Benchmark Coverage (%)`, `Min Net CAGR Spread (%)`, `benchmark_policy_status`를 추가하고 promotion decision이 그 상태를 함께 반영하도록 보강한 later-pass 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_LIQUIDITY_POLICY_AND_PROMOTION_REINFORCEMENT_LATER_PASS.md`
  - strict annual family에 `Min Liquidity Clean Coverage (%)`, `liquidity_clean_coverage`, `liquidity_policy_status`를 추가하고 promotion decision이 그 상태를 함께 반영하도록 보강한 later-pass 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_VALIDATION_POLICY_AND_PROMOTION_REINFORCEMENT_LATER_PASS.md`
  - strict annual family에 `Max Underperformance Share (%)`, `Min Worst Rolling Excess (%)`, `validation_policy_status`를 추가하고 promotion decision이 그 상태를 함께 반영하도록 보강한 later-pass 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_BROADER_BENCHMARK_CONTRACT_LATER_PASS.md`
  - strict annual family에 `Benchmark Contract`를 추가하고 `Ticker Benchmark`와 `Candidate Universe Equal-Weight` 두 기준선으로 validation / promotion / history surface를 읽을 수 있게 넓힌 later-pass 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_PORTFOLIO_GUARDRAIL_POLICY_AND_PROMOTION_REINFORCEMENT_LATER_PASS.md`
  - strict annual family에 `Max Strategy Drawdown (%)`, `Max Drawdown Gap vs Benchmark (%)`, `guardrail_policy_status`를 추가하고 promotion decision이 그 상태를 함께 반영하도록 보강한 later-pass 문서
- `.note/finance/phase12/PHASE12_STRICT_ANNUAL_DRAWDOWN_GUARDRAIL_ACTUAL_RULE_FIRST_PASS.md`
  - strict annual family에 trailing 전략 drawdown / benchmark 대비 drawdown gap 기반 optional actual guardrail을 추가하고, risk-off 시 해당 rebalance를 cash로 유지하도록 연결한 first-pass 문서
- `.note/finance/phase12/PHASE12_BACKTEST_STRATEGY_SURFACE_CONSOLIDATION_FIRST_PASS.md`
  - `backtest.py`의 strategy surface를 family 중심으로 정리하고, quality/value 계열을 `Quality` / `Value` / `Quality + Value`로 통합한 first-pass UI/orchestration 리팩터링 문서
- `.note/finance/phase12/PHASE12_GTAA_DBC_PDBC_NO_COMMODITY_ANALYSIS.md`
  - `GTAA`에서 `DBC`, `PDBC`, `No Commodity Sleeve`를 비교하고, ETF 자체 유사성과 전략 결과 차이가 왜 증폭되는지, 대안 ETF 후보까지 정리한 분석 문서
- `.note/finance/phase12/PHASE12_GTAA_COMMODITY_ALTERNATIVE_CANDIDATE_ANALYSIS.md`
  - `GTAA`에서 `CMDY`, `BCI`, `COMT` 대안 후보를 custom backfill 후 실제 백테스트에 넣어 `DBC`, `PDBC`, `No Commodity Sleeve`와 함께 비교한 분석 문서
- `.note/finance/phase12/PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md`
  - `Signal Interval = 1` 고정 조건에서 GTAA universe를 10개 변형해 `CAGR`와 `MDD`가 더 좋은 조합을 찾고, 어떤 수정이 실전형 개선으로 이어지는지 정리한 분석 문서
- `.note/finance/phase12/PHASE12_GTAA_NO_DBC_INTERVAL1_VARIATION_SEARCH.md`
  - `DBC`를 완전히 제외한 GTAA 10개 변형을 `Signal Interval = 1` 계약으로 비교하고, no-DBC 환경에서 더 나은 `CAGR`/`MDD` 조합과 개선 방향을 정리한 분석 문서
- `.note/finance/phase12/PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md`
  - 현재 GTAA 기본 계약(`top=3`, `interval=2`, `month_end`, `10 bps`)을 유지한 채 DB-backed ETF 그룹 18개를 비교하고, `QQQ + IAU + XLE` 중심의 개선 방향을 도출한 분석 문서
- `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md`
  - Phase 17 전체 structural downside-improvement 상위 계획 문서
- `.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md`
  - Phase 17 현재 실행 보드로, structural lever inventory / implementation slice / representative rerun 다음 단계를 관리하는 문서
- `.note/finance/phase17/PHASE17_STRUCTURAL_LEVER_INVENTORY_FIRST_PASS.md`
  - strict annual current code 기준 구조 레버를 inventory 형태로 정리한 first-pass 문서
- `.note/finance/phase17/PHASE17_CANDIDATE_CONSOLIDATION_FIT_REVIEW_FIRST_PASS.md`
  - compare / weighted portfolio / saved portfolio가 immediate practical-candidate work의 메인 트랙인지 보조 트랙인지 판단한 문서
- `.note/finance/phase17/PHASE17_PARTIAL_CASH_RETENTION_IMPLEMENTATION_FIRST_SLICE.md`
  - strict annual family에 partial cash retention contract를 실제 코드로 연결한 first implementation slice 문서
- `.note/finance/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_IMPLEMENTATION_SECOND_SLICE.md`
  - strict annual family에 defensive sleeve risk-off contract를 실제 코드로 연결한 second implementation slice 문서
- `.note/finance/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_IMPLEMENTATION_THIRD_SLICE.md`
  - strict annual family에 concentration-aware weighting contract를 실제 코드로 연결한 third implementation slice 문서
- `.note/finance/phase17/PHASE17_COMPLETION_SUMMARY.md`
  - Phase 17 structural downside-improvement closeout을 practical 기준으로 정리한 요약 문서
- `.note/finance/phase17/PHASE17_NEXT_PHASE_PREPARATION.md`
  - Phase 17 이후 next phase 방향을 larger structural redesign / candidate consolidation 기준으로 정리한 handoff 문서
- `.note/finance/phase17/PHASE17_TEST_CHECKLIST.md`
  - Phase 17 manual validation checklist
- `.note/finance/backtest_reports/phase17/README.md`
  - Phase 17 결과 중심 backtest report archive 안내 문서
- `.note/finance/backtest_reports/phase17/PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual `partial cash retention`이 실제 `Value` / `Quality + Value` anchor에서
    same-gate lower-MDD rescue를 만들 수 있는지 representative rerun으로 확인한 문서
- `.note/finance/backtest_reports/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual `defensive sleeve risk-off`가 같은 anchor에서
    same-gate lower-MDD rescue를 만들 수 있는지 representative rerun으로 확인한 문서
- `.note/finance/backtest_reports/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual `concentration-aware weighting`이 같은 anchor에서
    same-gate lower-MDD rescue를 만들 수 있는지 representative rerun으로 확인한 문서
- `.note/finance/phase18/PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md`
  - Phase 18 larger structural redesign 상위 계획 문서
- `.note/finance/phase18/PHASE18_CURRENT_CHAPTER_TODO.md`
  - Phase 18 current execution board
- `.note/finance/phase18/PHASE18_IMPLEMENTATION_FIRST_REPRIORITIZATION.md`
  - Phase 18을 deep-backtest-first가 아니라 implementation-first로 재정렬한 운영 기준 문서
- `.note/finance/phase18/PHASE18_NEXT_RANKED_FILL_IMPLEMENTATION_FIRST_SLICE.md`
  - strict annual family에 `Fill Rejected Slots With Next Ranked Names` contract를 연결한 first implementation slice 문서
- `.note/finance/backtest_reports/phase18/README.md`
  - Phase 18 larger structural redesign archive 안내 문서
- `.note/finance/backtest_reports/phase18/PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - next-ranked eligible fill이 current `Value` / `Quality + Value` structural probe에서
    meaningful rescue 또는 anchor replacement로 이어지는지 representative rerun으로 확인한 문서
- `.note/finance/backtest_reports/phase18/PHASE18_VALUE_FILL_ANCHOR_NEAR_FOLLOWUP_SECOND_PASS.md`
  - `Value` current practical anchor 근처에서
    fill contract를 좁게 다시 보고
    same-gate lower-MDD rescue가 실제로 있는지 확인한 문서
- `.note/finance/phase12/PHASE12_GTAA_INTERVAL1_DEFAULT_REBASE_ANALYSIS.md`
  - GTAA 기본 `Signal Interval`을 `1`로 rebased 한 뒤, 주요 preset과 상위 후보군을 공통 시작점에서 다시 비교해 현재 default cadence 기준의 우선순위를 정리한 문서
- `.note/finance/phase12/PHASE12_GTAA_SCORE_WEIGHT_AND_RISK_OFF_FIRST_PASS.md`
  - GTAA의 고정 `1/3/6/12` score blend를 UI에서 조절 가능하게 만들고, `Fallback Mode`, `Defensive Tickers`, `Market Regime`, `Crash Guardrail`을 포함한 risk-off contract를 first pass로 연결한 구현 문서
- `.note/finance/phase12/PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md`
  - current Phase 12 GTAA 후보군을 `SPY` benchmark와 직접 비교해, `CAGR`는 더 높고 `MDD`는 더 낮은 dominance candidate가 존재하는지 탐색하고 그 결과가 없었음을 정리한 분석 문서
- `.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md`
  - GTAA manual universe를 더 넓게 확장하고 `top / interval / score horizon`을 재조정해, `CAGR >= 9%`와 `MDD >= -16%`를 동시에 만족하는 실전형 candidate를 찾은 분석 문서
- `.note/finance/phase12/PHASE12_TEST_CHECKLIST.md`
  - Phase 12 real-money hardening 결과를 later batch review로 검수하기 위한 checklist 문서
- `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md`
  - Phase 12 이후 후보 전략을 shortlist / probation / monitoring 계약으로 다시 좁히기 위한 Phase 13 상위 계획 문서
- `.note/finance/phase13/PHASE13_CURRENT_CHAPTER_TODO.md`
  - Phase 13 현재 실행 보드로, candidate shortlist / ETF second-pass / monitoring / rolling validation 작업 상태를 관리하는 문서
- `.note/finance/phase13/PHASE13_CANDIDATE_SHORTLIST_CONTRACT_FIRST_PASS.md`
  - Phase 12의 `promotion_decision`을 `watchlist / paper_probation / small_capital_trial / hold` shortlist language로 다시 읽고, single / compare / execution context surface까지 연결한 Phase 13 first-pass 문서
- `.note/finance/phase13/PHASE13_ETF_GUARDRAIL_SECOND_PASS_FIRST_PASS.md`
  - ETF 전략군(`GTAA`, `Risk Parity Trend`, `Dual Momentum`)에 underperformance / drawdown guardrail actual rule을 second pass로 연결하고, single / compare / history round-trip까지 확장한 문서
- `.note/finance/phase13/PHASE13_PROBATION_AND_MONITORING_WORKFLOW_FIRST_PASS.md`
  - shortlist 결과를 `probation_status / monitoring_status / monthly review` 언어로 다시 읽고, single / compare / execution context surface까지 연결한 Phase 13 first-pass 문서
- `.note/finance/phase13/PHASE13_ROLLING_AND_OUT_OF_SAMPLE_VALIDATION_WORKFLOW_FIRST_PASS.md`
  - 최근 validation window와 split-period consistency를 따로 읽는 rolling / out-of-sample review layer를 추가하고, monitoring surface와 review checklist 초안까지 정리한 Phase 13 first-pass 문서
- `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_CHECKLIST_FIRST_PASS.md`
  - shortlist / probation / monitoring / rolling review / policy status를 한 장의 checklist로 묶고 deployment status를 `blocked / paper_only / small_capital_ready` 언어로 다시 읽는 Phase 13 first-pass 문서
- `.note/finance/phase13/PHASE13_COMPLETION_SUMMARY.md`
  - Phase 13 deployment-readiness / probation work를 practical closeout 기준으로 정리하고, 완료 범위와 다음 phase backlog를 명확히 남긴 문서
- `.note/finance/phase13/PHASE13_NEXT_PHASE_PREPARATION.md`
  - Phase 13 이후 다음 phase를 live deployment workflow 또는 PIT execution-readiness 방향으로 어떻게 열지 정리한 handoff 문서
- `.note/finance/phase13/PHASE13_TEST_CHECKLIST.md`
  - Phase 13 manual validation checklist로, shortlist / probation / rolling review / deployment checklist surface를 현재 UI에서 검수하기 위한 문서
- `.note/finance/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md`
  - Phase 14 상위 계획 문서로, Phase 13 QA 이후 다시 보기로 했던 real-money gate calibration 논의와 deployment workflow bridge 방향을 정리한 문서
- `.note/finance/phase14/PHASE14_CURRENT_CHAPTER_TODO.md`
  - Phase 14 현재 실행 보드로, gate blocker audit / calibration review / deployment workflow bridge 진행 상태를 관리하는 문서
- `.note/finance/phase14/PHASE14_GATE_BLOCKER_DISTRIBUTION_AUDIT_FIRST_PASS.md`
  - representative candidate와 current code gate logic을 기준으로 repeated `hold / blocked` blocker를 first-pass로 분류하고, backtest history `gate_snapshot` persistence 필요성을 함께 정리한 문서
- `.note/finance/phase14/PHASE14_PROMOTION_SHORTLIST_CALIBRATION_REVIEW_FIRST_PASS.md`
  - current promotion threshold inventory를 정리하고, repeated hold의 1차 원인이 factor 부족인지 gate calibration인지 분리해 본 Phase 14 calibration review first-pass 문서
- `.note/finance/phase14/PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md`
  - strict annual UI에 현재 안 열려 있는 stored factor 후보 중 sign 해석과 operator 설명이 비교적 명확한 small-set만 먼저 추려서 Phase 14 controlled expansion 대상으로 정리한 문서
- `.note/finance/phase14/PHASE14_NEAR_MISS_CANDIDATE_CASE_STUDY_FIRST_PASS.md`
  - representative strict annual / ETF near-miss candidate를 케이스 단위로 다시 읽고, family별 calibration 질문을 좁힌 Phase 14 case-study 문서
- `.note/finance/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_POLICY_SENSITIVITY_REVIEW_FIRST_PASS.md`
  - strict annual exact-hit hold와 quality near-miss를 current runtime으로 다시 돌려, `validation_policy` 완화만으로는 `hold`가 잘 풀리지 않고 fixed internal `validation_status` threshold가 더 직접적인 gate임을 정리한 Phase 14 sensitivity review 문서
- `.note/finance/phase14/PHASE14_ETF_OPERABILITY_SENSITIVITY_REVIEW_FIRST_PASS.md`
  - practical GTAA와 aggressive GTAA near-miss를 AUM / spread threshold sweep으로 다시 돌려, ETF operability blocker가 threshold 자체보다 partial data coverage 해석에 더 가깝다는 점을 정리한 Phase 14 sensitivity review 문서
- `.note/finance/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_STATUS_FIXED_THRESHOLD_REVIEW_FIRST_PASS.md`
  - strict annual repeated hold에서 `validation_policy`보다 internal `validation_status` fixed threshold가 더 직접적인 blocker임을, severe / caution 규칙 중심으로 다시 읽은 Phase 14 문서
- `.note/finance/phase14/PHASE14_ETF_OPERABILITY_DATA_COVERAGE_INTERPRETATION_REVIEW_FIRST_PASS.md`
  - ETF repeated hold에서 AUM / spread threshold보다 partial data coverage 해석이 더 직접적인 blocker임을, coverage boundary와 missing-data semantics 중심으로 다시 읽은 Phase 14 문서
- `.note/finance/phase14/PHASE14_FAMILY_SPECIFIC_THRESHOLD_EXPERIMENT_DESIGN_FIRST_PASS.md`
  - strict annual과 ETF를 같은 blanket 완화 대상으로 보지 않고, 다음 phase에서 실제로 실행할 threshold experiment를 family별로 좁혀 설계한 Phase 14 문서
- `.note/finance/phase14/PHASE14_DEPLOYMENT_WORKFLOW_BRIDGE_FIRST_PASS.md`
  - shortlist / probation / monitoring / deployment surface가 현재 어디까지 operator workflow를 설명하고, 어디서부터 operator log / action persistence가 비는지 정리한 Phase 14 bridge 문서
- `.note/finance/phase14/PHASE14_PIT_OPERABILITY_LATER_PASS_DECISION.md`
  - ETF operability가 왜 아직 current snapshot diagnostic으로만 읽혀야 하고, PIT/history 없이는 actual block rule로 승격하기 이르다는 점을 정리한 Phase 14 문서
- `.note/finance/phase14/PHASE14_TEST_CHECKLIST.md`
  - Phase 14 manual validation checklist로, gate calibration 설명 surface / tooltip / glossary / history gate snapshot을 현재 UI에서 검수하기 위한 문서
- `.note/finance/phase14/PHASE14_COMPLETION_SUMMARY.md`
  - Phase 14 real-money gate calibration work를 practical closeout 기준으로 정리하고, 완료 범위와 다음 phase backlog를 분명히 남긴 문서
- `.note/finance/phase14/PHASE14_NEXT_PHASE_PREPARATION.md`
  - Phase 14 이후 다음 phase를 threshold execution / operator workflow persistence / PIT operability 방향으로 어떻게 여는 것이 자연스러운지 정리한 handoff 문서
- `.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md`
  - Phase 14 calibration 이후 `Quality / Value / Quality + Value` strict annual family를 current practical contract로 다시 돌려,
    family별 strongest non-hold candidate와 현재 승격 근접도를 고정한 refresh 문서
- `.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md`
  - Phase 13 동안 진행한 `Quality / Value / Quality + Value` strict annual family 백테스트 결과를 family별로 한 장에 요약하고, 가장 강한 후보와 반복된 hold 원인을 빠르게 다시 보기 위한 정리 문서
- `.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md`
  - `Coverage 100`에서 못 찾은 exact-hit를 `US Statement Coverage 300 / 500 / 1000`까지 넓혀 다시 탐색하고, wider coverage가 실제로도 strict annual family의 hold-free target을 해결해주는지 점검한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md`
  - `Quality / Value / Quality + Value` strict annual family를 대상으로 `promotion = real_money_candidate`, `SPY` 초과 CAGR, `MDD 25% 이내` 조건을 동시에 만족하는 포트폴리오가 존재하는지 서브 에이전트 병렬 탐색으로 다시 확인한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md`
  - `Value > Strict Annual` raw winner(`CAGR 29.89% / MDD -29.15% / promotion = real_money_candidate`)를 backtest UI에서 다시 재현하기 위한 입력값 중심 가이드 문서
- `.note/finance/backtest_reports/phase13/PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md`
  - `Quality + Value > Strict Annual`를 `Historical Dynamic PIT Universe`와 `2016-01-01` 시작 조건으로 고정한 뒤, factor 조합과 benchmark / cadence를 바꿔 `hold 아님 + MDD 15% 이내` 가능성을 다시 탐색한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_VALUE_STRICT_CAGR15_MDD20_SEARCH.md`
  - 서브 에이전트 병렬 탐색 후 메인 환경 재검증으로, `Value > Strict Annual`에서 `CAGR 15% 이상 + MDD 20% 이내`를 만족한 exact-hit 조합을 정리한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_CAGR20_MDD25_HOLD_FREE_SEARCH.md`
  - `hold 아님 + CAGR 20% 이상 + MDD 25% 이내`를 strict annual family 전체에서 다시 탐색했지만 exact hit가 없었고, `Value > Strict Annual`의 near-miss 조합이 가장 가까웠음을 정리한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_HOLD_DIAGNOSTIC_AND_NONHOLD_NEAR_MISS_SEARCH.md`
  - `Value` exact-hit 후보의 `hold` 원인을 `validation` 계층에서 진단하고, `Quality` 및 `Quality + Value` strict annual family에서 non-hold exact hit가 가능한지 다시 탐색한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_VALUE_STRICT_HOLD_FREE_SEARCH.md`
  - `Value Strict Annual` exact-hit 후보의 `hold` 원인을 유지한 채, benchmark / factor / cadence / trend / regime를 바꿔 `hold`가 풀리면서도 `CAGR >= 15%`와 `MDD >= -20%`를 동시에 만족하는 후보가 존재하는지 다시 탐색한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_VALUE_STRICT_SPY_TARGET_SEARCH.md`
  - `Value Strict Annual`을 중심으로 `SPY`보다 `CAGR`와 `MDD`가 동시에 나은 후보를 찾기 위해 `2016-01-01` 시작, `Historical Dynamic PIT Universe`, `top_n <= 10` 조건에서 수행한 탐색 문서
- `.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md`
  - `Quality / Value / Quality + Value` strict annual family를 대상으로 `SPY` 대비 CAGR/MDD 우위와 `CAGR >= 15%`, `MDD >= -20%` 교집합 후보를 다시 탐색한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md`
  - `Quality Snapshot (Strict Annual)`만으로 `SPY` baseline을 동시에 이기는 raw candidate를 찾는 탐색 문서로, factor set / cadence / top_n를 바꿔 실전형 UI 설정에서의 dominance 여부를 정리한 분석 문서
- `.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md`
  - `Quality`, `Value`, `Quality + Value` strict annual family를 `SPY` 기준선과 직접 비교해, `2016-01-01` 시작 / `Historical Dynamic PIT Universe` / `top_n <= 10` 조건에서 `SPY`보다 CAGR과 MDD가 모두 나은 후보를 찾은 분석 문서
- `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md`
  - `Quality > Strict Annual` family의 Phase 13 결과를 전략 기준으로 다시 읽기 위한 허브 문서로, 관련 raw report와 현재 해석을 한 곳에 모아둔 문서
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md`
  - `Value > Strict Annual` family의 strongest raw winner, balanced near-miss, hold 병목을 전략 기준으로 다시 읽기 위한 허브 문서
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - `Value > Strict Annual` strongest current candidate 하나를 링크 모음이 아니라 실제 전략 구성, 입력값, factor, overlay, 기대 결과 중심으로 바로 읽기 위한 one-pager 문서
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md`
  - `Quality + Value > Strict Annual` family의 low-drawdown 탐색과 family positioning을 전략 기준으로 다시 읽기 위한 허브 문서
- `.note/finance/backtest_reports/strategies/GTAA.md`
  - `GTAA` family의 current practical candidate와 관련 탐색 문서를 전략 기준으로 다시 읽기 위한 허브 문서
- `.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md`
  - DB에 가격이 존재하는 ETF 후보군을 기반으로 GTAA를 다시 탐색해, `Promotion != hold`, `Deployment != blocked`, `SPY` 대비 `CAGR / MDD` 우위를 동시에 만족하는 practical candidate를 찾은 분석 문서

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
  - Phase 5 first chapter TODO 보드
- `.note/finance/phase5/PHASE5_COMPLETION_SUMMARY.md`
  - Phase 5 first chapter 종료 요약 문서
- `.note/finance/phase5/PHASE5_NEXT_PHASE_PREPARATION.md`
  - Phase 5 이후 next-phase 후보와 kickoff 기준 정리 문서
- `.note/finance/phase5/PHASE5_STRICT_FAMILY_TEST_CHECKLIST.md`
  - Phase 5 결과물을 수동 검증하기 위한 테스트 체크리스트

---

## 7. Phase 6 상위 문서

- `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md`
  - second overlay와 quarterly strict family entry/validation을 이번 chapter의 공식 방향으로 고정한 문서
- `.note/finance/phase6/PHASE6_CURRENT_CHAPTER_TODO.md`
  - Phase 6 current chapter TODO 보드
- `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_REQUIREMENTS.md`
  - second overlay로 선택된 `Market Regime Overlay`의 first-pass rule을 고정한 문서
- `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_FIRST_PASS.md`
  - strict family와 quarterly prototype에 market regime overlay를 연결한 first-pass 구현 문서
- `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_VALIDATION.md`
  - annual strict family small-smoke 기준 on/off validation 결과 문서
- `.note/finance/phase6/PHASE6_STRICT_QUARTERLY_ENTRY_CRITERIA.md`
  - strict quarterly family first candidate와 research-only semantics를 고정한 문서
- `.note/finance/phase6/PHASE6_STRICT_QUARTERLY_FIRST_PASS_VALIDATION.md`
  - `Quality Snapshot (Strict Quarterly Prototype)` first-pass 검증 문서
- `.note/finance/phase6/PHASE6_TEST_CHECKLIST.md`
  - Phase 6 market regime overlay / quarterly prototype 수동 테스트 체크리스트
- `.note/finance/phase6/PHASE6_COMPLETION_SUMMARY.md`
  - Phase 6 종료 요약 문서
- `.note/finance/phase6/PHASE6_NEXT_PHASE_PREPARATION.md`
  - Phase 7 kickoff 전 준비 문서

---

## 8. Phase 7 상위 문서

- `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
  - quarterly strict family late-start 문제와 statement PIT hardening을 다음 major phase 방향으로 고정한 문서
- `.note/finance/phase7/PHASE7_CURRENT_CHAPTER_TODO.md`
  - Phase 7 current chapter TODO 보드
- `.note/finance/phase7/PHASE7_SUPPLEMENTARY_POLISH_PASS.md`
  - Phase 7 first pass 이후 practical UX/runtime 보강 사항 정리 문서
- `.note/finance/phase7/PHASE7_COMPLETION_SUMMARY.md`
  - Phase 7 implementation closeout 요약 문서
- `.note/finance/phase7/PHASE7_NEXT_PHASE_PREPARATION.md`
  - Phase 8 kickoff 전 다음 방향 정리 문서

---

## 9. Phase 8 상위 문서

- `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
  - quarterly strict strategy family를 quality/value/quality+value research library로 확장하기 위한 계획 문서
- `.note/finance/phase8/PHASE8_CURRENT_CHAPTER_TODO.md`
  - Phase 8 current chapter TODO 보드

---

## 10. Phase 5 세부 구현 문서

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
- `.note/finance/phase5/PHASE5_COMPLETION_SUMMARY.md`
  - Phase 5 첫 챕터 완료 범위와 남겨둔 후속 후보를 정리한 종료 요약 문서
- `.note/finance/phase5/PHASE5_NEXT_PHASE_PREPARATION.md`
  - Phase 5 종료 이후 다음 chapter/phase 후보와 추천 순서를 정리한 문서

---

## 10. Phase 2 / Phase 3 - Backtest / Loader 관련 문서

- `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
  - loader 함수 초안
- `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
  - loader 입력 계약
- `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`
  - point-in-time 원칙
- `.note/finance/phase2/STRICT_PIT_LOADER_QUERY_DRAFT.md`
  - strict PIT loader query 초안

---

## 11. Phase 2 - Point-In-Time / 재무제표 정리 문서

- `.note/finance/phase2/POINT_IN_TIME_SCHEMA_REVIEW_AND_PATCH_PLAN.md`
  - point-in-time 스키마 리뷰와 패치 계획
- `.note/finance/phase2/POINT_IN_TIME_BACKFILL_AND_CONSTRAINT_STRATEGY.md`
  - backfill 및 stricter constraint 전략

---

## 12. 운영 / 설정 / 수집 전략 문서

- `.note/finance/DATA_COLLECTION_UI_STRATEGY.md`
  - 내부 운영 수집 UI 전략
- `.note/finance/CONFIG_EXTERNALIZATION_INVENTORY.md`
  - 설정 외부화 후보와 우선순위
- `.note/finance/OHLCV_AND_FINANCIAL_INGESTION_REVIEW.md`
  - OHLCV / 재무 적재 기능 점검 문서

---

## 13. 문서 사용 순서 권장

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

---

## Latest Additions

- `.note/finance/phase17/README.md`
  - Phase 17 structural downside improvement current chapter 안내 문서
- `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md`
  - Phase 17 structural downside improvement kickoff plan 문서
- `.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md`
  - Phase 17 current board 문서
- `.note/finance/phase17/PHASE17_STRUCTURAL_LEVER_INVENTORY_FIRST_PASS.md`
  - strict annual 구조 레버를 current code 기준으로 inventory한 first-pass 문서
- `.note/finance/phase17/PHASE17_CANDIDATE_CONSOLIDATION_FIT_REVIEW_FIRST_PASS.md`
  - weighted portfolio / saved portfolio를 operator bridge로 읽어야 하는지 정리한 first-pass 문서
- `.note/finance/phase17/PHASE17_PARTIAL_CASH_RETENTION_IMPLEMENTATION_FIRST_SLICE.md`
  - strict annual partial cash retention contract를 실제 코드에 연결한 first implementation slice 문서
- `.note/finance/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_IMPLEMENTATION_SECOND_SLICE.md`
  - strict annual defensive sleeve risk-off contract를 실제 코드에 연결한 second implementation slice 문서
- `.note/finance/backtest_reports/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual defensive sleeve risk-off rerun 결과를 current anchor 기준으로 정리한 문서
- `.note/finance/phase15/PHASE15_CANDIDATE_QUALITY_IMPROVEMENT_PLAN.md`
  - Phase 15 candidate quality improvement 상위 계획 문서
- `.note/finance/phase15/PHASE15_CURRENT_CHAPTER_TODO.md`
  - Phase 15 현재 실행 보드
- `.note/finance/phase15/PHASE15_COMPLETION_SUMMARY.md`
  - Phase 15 candidate quality improvement를 practical closeout 기준으로 정리한 요약 문서
- `.note/finance/phase15/PHASE15_NEXT_PHASE_PREPARATION.md`
  - Phase 15 이후 다음 phase를 candidate consolidation / downside follow-up / operator workflow persistence 관점에서 정리한 handoff 문서
- `.note/finance/phase15/PHASE15_TEST_CHECKLIST.md`
  - Phase 15 strongest/current candidate 문서와 전략 로그를 수동으로 검수하기 위한 checklist 문서
- `.note/finance/phase16/README.md`
  - Phase 16 downside-focused practical refinement current chapter 안내 문서
- `.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md`
  - Phase 16 current board이자 closeout 상태 요약 문서
- `.note/finance/phase16/PHASE16_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
  - `Value > Strict Annual` current practical anchor를 기준으로 bounded downside refinement를 다시 본 first-pass 문서
- `.note/finance/phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md`
  - 결과 중심 report는 backtest archive를 canonical로 사용하고,
    phase 폴더에서는 `Value` rescue second pass 결론을 pointer로 남긴 문서
- `.note/finance/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
  - `Quality + Value > Strict Annual` strongest practical anchor를 기준으로 bounded downside refinement를 다시 본 first-pass 문서
- `.note/finance/phase16/PHASE16_COMPLETION_SUMMARY.md`
  - Phase 16 downside-focused practical refinement를 practical closeout 기준으로 정리한 요약 문서
- `.note/finance/phase16/PHASE16_NEXT_PHASE_PREPARATION.md`
  - Phase 16 이후 structural downside improvement 방향으로 handoff하기 위한 준비 문서
- `.note/finance/phase16/PHASE16_TEST_CHECKLIST.md`
  - Phase 16 strongest point / lower-MDD near-miss / closeout 문서를 수동으로 검수하기 위한 checklist 문서
- `.note/finance/backtest_reports/phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md`
  - `Value > Strict Annual` lower-MDD near-miss rescue second pass canonical backtest report
- `.note/finance/backtest_reports/phase16/PHASE16_QUALITY_VALUE_STRONGEST_POINT_DOWNSIDE_FOLLOWUP_SECOND_PASS.md`
  - `Quality + Value > Strict Annual` strongest practical point를 current code 기준으로 다시 확인한 second-pass backtest report
- `.note/finance/phase17/README.md`
  - Phase 17 structural downside improvement current chapter 안내 문서
- `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md`
  - Phase 17 structural downside improvement kickoff plan 문서
- `.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md`
  - Phase 17 current board 문서
- `.note/finance/phase17/PHASE17_STRUCTURAL_LEVER_INVENTORY_FIRST_PASS.md`
  - strict annual 구조 레버를 current code 기준으로 inventory한 first-pass 문서
- `.note/finance/phase17/PHASE17_CANDIDATE_CONSOLIDATION_FIT_REVIEW_FIRST_PASS.md`
  - weighted portfolio / saved portfolio를 operator bridge로 읽어야 하는지 정리한 first-pass 문서
- `.note/finance/backtest_reports/phase15/README.md`
  - Phase 15 backtest archive 안내 문서
- `.note/finance/backtest_reports/phase15/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
  - strongest `Value` baseline에서 `MDD`를 낮추는 방향으로 practical candidate quality를 개선할 수 있는지 본 first-pass backtest report
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
  - strongest `Value` baseline보다 `MDD`를 낮춘 downside-improved current candidate one-pager
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
  - `Quality` family에서 controlled addition이 current literal preset semantics 기준으로 왜 non-hold를 회복하지 못했는지 정리한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md`
  - `Quality` family에서 `benchmark / overlay` 구조를 조정해 current rescued candidate를 다시 확보한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md`
  - rescued `Quality` anchor 기준 `Top N / Rebalance Interval` downside search를 다시 돌려, recommended downside-improved candidate와 conservative clean candidate를 함께 고정한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md`
  - rescued `Quality` anchor 위 bounded factor addition / replacement를 다시 붙였지만 baseline을 넘는 practical candidate가 없었다는 점을 정리한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
  - `Quality + Value` family baseline blend에 controlled addition을 붙여 best raw addition candidate를 정리한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md`
  - `Quality + Value + per` strongest candidate를 anchor로 `Top N` downside search를 다시 본 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md`
  - `Quality + Value + per` strongest candidate를 anchor로 benchmark sensitivity와 quality-side pruning을 다시 봤고, baseline candidate-equal-weight contract가 여전히 strongest practical point임을 고정한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md`
  - `Quality + Value + per` strongest candidate에서 value-side removal / replacement를 다시 봤고, `ocf_yield -> pcr`가 same gate / same MDD로 `CAGR`를 더 높인 current strongest practical candidate가 되었음을 정리한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md`
  - `Quality + Value > Strict Annual` current strongest practical point(`ocf_yield -> pcr`) 위에서
    `Top N / benchmark` follow-up을 다시 보고 strongest practical point가 유지되는지 정리한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md`
  - `Quality + Value > Strict Annual` replacement anchor 위 quality-side bounded replacement를 다시 보고,
    `net_margin -> operating_margin`가 strongest practical point를 갱신했는지 정리한 report
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md`
  - `Quality + Value > Strict Annual` new strongest practical point 위에서 `Top N` follow-up을 다시 보고,
    `Top N = 10`이 strongest practical point로 유지되는지 정리한 report
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md`
  - `per` addition 기반 current best raw addition candidate one-pager
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - quality/value replacement를 함께 반영한 current strongest practical blended candidate one-pager
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md`
  - `operating_income_yield -> por` replacement를 더한 Phase 16 strongest practical blended candidate one-pager
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md`
  - `ocf_yield -> pcr` replacement를 적용한 current strongest practical blended candidate one-pager
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Value > Strict Annual` 전략 run 기록 누적 문서
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - `Value > Strict Annual` strongest current candidate one-pager
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
  - `Value > Strict Annual` downside-improved current candidate one-pager
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md`
  - `Value > Strict Annual` one-factor addition best current candidate one-pager
