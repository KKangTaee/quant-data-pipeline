# Master Phase Roadmap

## 목적
이 문서는 `finance` 프로젝트를
Phase 기반으로 어떻게 진행할지 큰 틀을 정리하는 상위 로드맵이다.

이 프로젝트의 핵심 목적은 두 가지다.

1. 데이터 수집
2. 백테스트

최종 목표:
- 사용자가 가상의 포트폴리오를 구성할 수 있어야 한다
- 다양한 전략을 선택하거나 직접 구성할 수 있어야 한다
- DB에 저장된 데이터 기반으로 백테스트를 실행할 수 있어야 한다
- 결과 수익률, 포트폴리오 변화, 전략 특성을 시각적으로 확인할 수 있어야 한다

즉 이 프로젝트는
“데이터를 모으는 도구”에서 끝나는 것이 아니라,
최종적으로는 **퀀트 전략 실행 및 백테스트 플랫폼**으로 가는 것을 목표로 한다.

---

## Phase 운영 원칙

앞으로는 아래 원칙으로 진행한다.

1. 큰 기능은 항상 Phase 기준으로 먼저 정리한다
2. 각 Phase는 별도 문서로 범위, 목표, 산출물, 검증 기준을 가진다
3. 실제 진행은 각 Phase의 TODO 보드 문서로 관리한다
4. 추가 요청이나 방향 변경이 생기면
   - 기존 Phase 문서를 업데이트하거나
   - 필요한 경우 새 Phase를 개설한다
5. 새로운 Phase를 열기 전에는
   - 왜 필요한지
   - 이전 Phase와 어떻게 연결되는지
   - 어떤 결과물이 나와야 하는지
   를 먼저 사용자와 확인한다

---

## 전체 상위 Phase 구조

## Phase 1. Internal Data Collection Console

### 목적
- 내부 운영용 데이터 수집 웹앱 구축
- 수집 작업을 버튼 기반으로 실행 가능하게 만들기

### 핵심 내용
- Streamlit 기반 운영 UI
- OHLCV / fundamentals / factors / asset profile / financial statements 수집
- 실행 결과, 로그, 실패 확인
- 기본적인 운영 UX 확보

### 상태
- `completed`

### 주요 문서
- `.note/finance/phase1/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md`
- `.note/finance/phase1/PHASE1_WEB_APP_SCOPE.md`
- `.note/finance/phase1/PHASE1_JOB_WRAPPER_INTERFACE.md`

---

## Phase 2. Operational Hardening And Backtest Preparation

### 목적
- 수집 운영을 안정화
- 백테스트 진입을 위한 데이터/loader/point-in-time 기반 정리

### 핵심 내용
- 운영 파이프라인 분리
- 실행 이력 고도화
- 설정 외부화 준비
- backtest loader 설계
- point-in-time 보강
- 상세 재무제표 raw ledger 정리

### 상태
- `completed`

### 현재 하위 챕터
- 일반 운영 고도화 챕터
- point-in-time hardening 챕터
- 종료 요약 문서

### 주요 문서
- `.note/finance/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`
- `.note/finance/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`
- `.note/finance/phase2/PHASE2_COMPLETION_SUMMARY.md`
- `.note/finance/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
- `.note/finance/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
- `.note/finance/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`

---

## Phase 3. Backtest Loader Implementation And Strategy Runtime

### 목적
- 설계된 loader를 실제 코드로 구현
- 전략 실행 엔진과 DB loader를 연결

### 예상 핵심 내용
- price / fundamentals / factors / detailed statements loader 구현
- strict PIT loader와 broad research loader 구분
- universe resolution 표준화
- strategy input contract 정리
- 최소 1개 전략의 DB 기반 실행 경로 확보

### 상태
- `completed`

### 현재 하위 챕터
- UI structure decision 챕터
- runtime public boundary 구체화 챕터

### 현재 하위 챕터
- loader/runtime groundwork 챕터
- runtime generalization 챕터

### 현재 상태 요약
- 첫 loader 구현 챕터 완료
- broad / strict statement loader까지 포함한 loader read-path 구현 완료
- DB-backed sample path 확보 완료
- 다음 포커스는 runtime 일반화와 Phase 4 handoff 준비

### 주요 문서
- `.note/finance/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
- `.note/finance/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase3/PHASE3_CHAPTER1_COMPLETION_SUMMARY.md`
- `.note/finance/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

---

## Phase 4. Portfolio Construction And Backtest UI

### 목적
- 사용자가 웹 UI에서 포트폴리오와 전략을 구성하고 백테스트를 실행할 수 있게 만들기

### 예상 핵심 내용
- 전략 선택 UI
- 포트폴리오 구성 UI
- 기간 / 유니버스 / 리밸런싱 규칙 입력
- 백테스트 실행 버튼
- 결과 차트 및 요약 지표 표시

### 상태
- `completed`

### 중요 전제
- loader 계층과 strategy runtime이 먼저 안정화되어야 함

### 현재 상태 요약
- unified Backtest UI와 public runtime wrapper family가 구현되었다
- price-only public 전략 4종과 factor/fundamental public 전략 4종이 UI에 연결되었다
- strict annual family는
  - fast runtime
  - selection-history interpretation
  - annual coverage preset/operator flow
  - large-universe calendar fix
  - stale-symbol preflight refresh payload
  - staged wider-universe preset (`500/1000`)
  - first strict multi-factor public candidate
  까지 갖춘 상태다
- strict annual public default는 현재도
  - single: `US Statement Coverage 300`
  - compare: `US Statement Coverage 100`
  으로 유지된다
- `US Statement Coverage 1000`은 staged preset으로 usable하지만,
  closeout 기준으로 stale symbol `4`개와 `49d` freshness spread가 남아 있어
  public default로는 승격하지 않았다
- `Value Snapshot (Strict Annual)`은 closeout 보강 이후
  `2016-01-29`부터 active하게 동작하는 real strict-value path가 되었다
- 따라서 Phase 4는
  closeout verification까지 마치고 다음 phase 준비 단계로 넘어간 상태다

---

## Phase 5. Strategy Library, Comparative Research, And Risk Overlay

### 목적
- 다양한 전략을 축적하고 비교 가능한 연구 환경을 구축하며,
  strict factor 전략군에 risk overlay를 추가할 준비와 first implementation을 진행한다

### 예상 핵심 내용
- 전략 템플릿
- factor / momentum / allocation / custom strategy 라이브러리
- 전략 간 비교 리포트
- 전략별 결과 저장 및 재실행
- strict factor risk overlay 설계
- first overlay candidate 구현
- overlay-aware compare / interpretation

### 상태
- `completed`  # first chapter

### 현재 하위 챕터
- strategy library baseline + risk overlay design 챕터

### 현재 상태 요약
- Phase 4 closeout 후 사용자 확인을 거쳐
  next-phase 방향이 risk overlay 확장까지 포함하는 형태로 고정되었다
- 현재는
  - strict family baseline comparative research 정리
  - compare advanced-input parity first pass
  - `month-end MA200 trend filter` overlay first pass
  - historical managed-universe semantics 정리
  - quarterly strict family review
  - second overlay candidate review
  까지 진행되었고,
  Phase 5 first chapter는 closeout 상태다

### 주요 문서
- `.note/finance/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md`
- `.note/finance/phase5/PHASE5_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase5/PHASE5_BASELINE_STRICT_FAMILY_COMPARATIVE_RESEARCH.md`
- `.note/finance/phase5/PHASE5_COMPARE_ADVANCED_INPUT_PARITY_FIRST_PASS.md`
- `.note/finance/phase5/PHASE5_FIRST_OVERLAY_REQUIREMENTS_AND_SELECTION.md`

---

## Phase 7. Quarterly Coverage And Statement PIT Hardening

### 목적
- quarterly strict prototype가 late-start 되는 원인을 source/schema/loader/shadow 관점에서 바로잡는다
- raw statement timing semantics를 다시 점검하고 quarterly longer-history를 회복한다

### 핵심 내용
- statement source payload inspection
- raw statement ledger review
- PIT timing semantics 점검
- quarterly ingestion depth 확대
- quarterly shadow fundamentals / factors rebuild
- quarterly strict prototype rerun validation

### 상태
- `completed`

### 현재 상태 요약
- source inspection 결과, EDGAR source 자체는 long-history와 timing field를 충분히 제공하고 있음이 확인되었다
- Phase 7 first pass에서 quarterly late-start의 직접 원인을
  - `10-K/FY` exclusion
  - short period limit
  - report-date anchor filter
  로 고정했다
- 코드 기준으로는
  - quarterly path가 `10-K/FY`를 포함하도록 바뀌었고
  - `periods=0 = all available`가 공식 입력으로 열렸으며
  - quarterly shadow builder가 valid rows를 버리지 않도록 수정되었다
- `US Statement Coverage 100` quarterly shadow까지 다시 채운 뒤 prototype이 다시 `2016-01-29`부터 active하게 열리는 것을 확인했다
- supplementary polish 기준으로는
  - weekend/holiday-aware freshness preflight
  - quarterly shadow coverage preview
  - statement PIT inspection UI
  도 함께 정리되었다
- 이후 operator 보강과 checklist 확인을 거치며,
  Phase 7 핵심 목표였던 quarterly coverage hardening / PIT inspection / longer-history recovery는 closeout 가능한 수준으로 정리되었다

### 주요 문서
- `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
- `.note/finance/phase7/PHASE7_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase7/PHASE7_STATEMENT_SOURCE_PAYLOAD_INSPECTION.md`
- `.note/finance/phase7/PHASE7_RAW_STATEMENT_LEDGER_REVIEW_AND_DECISION.md`
- `.note/finance/phase7/PHASE7_QUARTERLY_COVERAGE_HARDENING_FIRST_PASS.md`
- `.note/finance/phase7/PHASE7_SUPPLEMENTARY_POLISH_PASS.md`
- `.note/finance/phase7/PHASE7_COMPLETION_SUMMARY.md`
- `.note/finance/phase7/PHASE7_NEXT_PHASE_PREPARATION.md`

---

## Phase 8. Quarterly Strategy Family Expansion And Promotion Readiness

### 목적
- repaired quarterly foundation 위에 quarterly strict strategy family를 실제 research strategy library로 확장한다
- annual strict family와 비교 가능한 quarterly quality / value / quality+value 경로를 만든다
- quarterly family의 research-only 유지 vs promotion readiness를 판단할 기준을 정리한다

### 핵심 내용
- quarterly family scope / naming / role decision
- `Value Snapshot (Strict Quarterly Prototype)` first pass
- `Quality + Value Snapshot (Strict Quarterly Prototype)` first pass
- quarterly interpretation / history parity
- quarterly compare integration 검토
- quarterly promotion readiness criteria draft

### 상태
- `implementation_completed`
- `manual_validation_pending`

### 현재 상태 요약
- Phase 7에서 quarterly data foundation은 복구되었고
  `Quality Snapshot (Strict Quarterly Prototype)`는 longer-history에서 실제로 열리게 되었다
- 이제 남은 핵심은
  single prototype 하나에 머무는 quarterly path를
  strategy family 수준으로 확장하는 일이다
- Phase 8 진행 중 추가된 operator tooling 기준으로는
  - stale price diagnosis
  - statement shadow coverage gap drilldown
  - statement coverage diagnosis
  - runtime/build indicator
  - statement shadow rebuild only
  까지 정리되어 later batch validation에 유리한 상태다

### 주요 문서
- `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
- `.note/finance/phase8/PHASE8_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase8/PHASE8_QUARTERLY_FAMILY_SCOPE_AND_COMPARE_DECISION.md`
- `.note/finance/phase8/PHASE8_QUARTERLY_VALUE_AND_MULTI_FACTOR_FIRST_PASS.md`
- `.note/finance/phase8/PHASE8_QUARTERLY_VALIDATION_FIRST_PASS.md`
- `.note/finance/phase8/PHASE8_PRICE_STALE_DIAGNOSIS_FIRST_PASS.md`
- `.note/finance/phase8/PHASE8_STATEMENT_SHADOW_COVERAGE_GAP_DIAGNOSTICS.md`
- `.note/finance/phase8/PHASE8_OPERATOR_RUNTIME_AND_SHADOW_REBUILD_TOOLING.md`
- `.note/finance/phase8/PHASE8_STATEMENT_COVERAGE_DIAGNOSIS_GUIDANCE.md`
- `.note/finance/phase8/PHASE8_TEST_CHECKLIST.md`

---

## Phase 9. Strict Coverage Policy And Promotion Gate

### 목적
- annual / quarterly strict family를 어떤 universe / filing structure / operator rule 위에서 공식 지원할지 고정한다
- `MRSH`, `AU` 같은 coverage-exception 사례를 ad hoc 대응이 아니라 정책으로 처리한다
- research-only 경로와 public-candidate 경로 사이의 승격 기준을 명시한다

### 핵심 내용
- strict coverage eligibility policy
- unsupported form / foreign issuer handling policy
- source-empty / symbol-mapping issue handling rule
- canonical strict preset governance
- annual / quarterly promotion gate 정의

### 상태
- `completed`

### 현재 상태 요약
- Phase 8까지 구현된 diagnostics / operator tooling을 이제 policy 레벨로 고정해야 하는 단계다
- `MRSH`, `AU` 같은 exception case가 단순 operator 이슈가 아니라 strict coverage 정책의 입력으로 다뤄지기 시작했다
- 현재 chapter는
  - exception inventory
  - foreign-form handling
  - public promotion gate
  를 문서와 운영 rule로 고정하는 방향으로 열려 있다
- current strict preset semantics는
  historical monthly top-N universe가 아니라
  `managed static research universe`로 해석하는 것이 맞다는 점이 정리되었다
- 실전 투자 기준 다음 우선순위는
  productization(현재 Phase 11)보다
  Phase 10 `historical dynamic PIT universe` 쪽이 더 높다는 권고가 추가되었다

### 권고 방향
- Phase 8 결과를 바로 public으로 승격하기보다,
  Phase 9에서 먼저 coverage 정책과 승격 기준을 고정하는 것이 맞다

### 주요 문서
- `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md`
- `.note/finance/phase9/PHASE9_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase9/PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md`
- `.note/finance/phase9/PHASE9_STRICT_COVERAGE_EXCEPTION_INVENTORY.md`
- `.note/finance/phase9/PHASE9_STRICT_COVERAGE_POLICY_DECISION.md`
- `.note/finance/phase9/PHASE9_STRICT_FAMILY_PROMOTION_GATE.md`
- `.note/finance/phase9/PHASE9_OPERATOR_DECISION_TREE.md`
- `.note/finance/phase9/PHASE9_TEST_CHECKLIST.md`

---

## Phase 10. Historical Dynamic PIT Universe

### 목적
- current strict preset의 managed static research universe를 넘어서
  rebalance-date 기준 historical dynamic PIT universe mode를 구현한다
- 실전 투자용 final validation에 더 가까운 universe contract를 만든다

### 핵심 내용
- rebalance-date membership contract 정의
- historical market-cap / listing / delisting source inventory
- annual strict family dynamic mode first pass
- static vs dynamic comparison readout
- PIT mode caution / help / interpretation 정리

### 상태
- `completed`

### 현재 상태 요약
- dynamic PIT universe contract가 current code/UI/history surface에 반영되었다
- annual strict family는 dynamic PIT single / compare / history first pass를 갖춘 상태다
- quarterly strict prototype family도 dynamic PIT single / compare / history first pass를 갖춘 상태다
- result surface에는
  - `Universe Membership Count`
  - `Universe Contract`
  - `Dynamic Universe` 상세 탭
  - history artifact persistence
  가 들어가 있다
- continuity / delisting / profile diagnostics도 함께 남기므로,
  current implementation은 `approximate PIT + diagnostics` contract로 읽는 것이 맞다
- perfect constituent-history reinforcement는 future backlog로 남기되,
  Phase 10 current scope 기준으로는 practical closeout 가능한 상태다

### 권고 방향
- 실전 투자 목표 기준에서는
  productization보다 먼저 Phase 10을 구현하는 것이 더 합리적이다

### 주요 문서
- `.note/finance/phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md`
- `.note/finance/phase10/PHASE10_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase10/PHASE10_PIT_SOURCE_AND_SCHEMA_GAP_ANALYSIS.md`
- `.note/finance/phase10/PHASE10_DYNAMIC_PIT_FIRST_PASS_IMPLEMENTATION_ORDER.md`
- `.note/finance/phase10/PHASE10_ANNUAL_STRICT_DYNAMIC_PIT_FIRST_PASS.md`
- `.note/finance/phase10/PHASE10_DYNAMIC_PIT_SECOND_PASS_HARDENING.md`
- `.note/finance/phase10/PHASE10_COMPLETION_SUMMARY.md`
- `.note/finance/phase10/PHASE10_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase10/PHASE10_TEST_CHECKLIST.md`

---

## Phase 11. Portfolio Productization And Research Workflow

### 목적
- 여러 전략과 포트폴리오 구성을 실제 사용자 중심 워크플로우로 끌어올린다
- 단일 전략 실행을 넘어서, 저장 가능한 포트폴리오 / 비교 / 재실행 / 분석 surface를 제품 수준으로 정리한다

### 핵심 내용
- weighted multi-strategy portfolio UX 정리
- saved portfolio / run preset workflow
- compare-to-portfolio bridge 강화
- contribution / exposure / attribution readout 확장
- user-defined research workflow 정리

### 상태
- `completed`

### 권고 방향
- Phase 11 first pass는 practical closeout 처리하고,
  next priority는 portfolio surface polish보다
  Phase 12 real-money strategy promotion으로 옮기는 것이 맞다

### 현재 상태 요약
- Phase 11 first pass에서는
  - saved portfolio persistence contract
  - compare -> weighted portfolio -> saved portfolio 저장 흐름
  - saved portfolio -> compare prefill
  - saved portfolio end-to-end rerun
  까지 구현되었다
- 현재 저장 파일은
  - `.note/finance/SAVED_PORTFOLIOS.jsonl`
  이고,
  저장 단위는
  - `compare_context`
  - `portfolio_context`
  - `source_context`
  로 나뉜다
- 아직 남은 큰 항목은
  - in-place edit / overwrite UX
  - richer portfolio readouts
  - workflow wording polish
  쪽이지만,
  이는 later backlog로 남기고 first-pass practical closeout 처리한다

### 주요 문서
- `.note/finance/phase11/PHASE11_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md`
- `.note/finance/phase11/PHASE11_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase11/PHASE11_EXECUTION_PREPARATION.md`
- `.note/finance/phase11/PHASE11_SAVED_PORTFOLIO_FIRST_PASS.md`
- `.note/finance/phase11/PHASE11_COMPLETION_SUMMARY.md`
- `.note/finance/phase11/PHASE11_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase11/PHASE11_TEST_CHECKLIST.md`

---

## Phase 12. Real-Money Strategy Promotion

### 목적
- 현재 구현된 전략군을
  “실행 가능” 수준에서
  **실전 투자 판단에 쓸 수 있는 계약**
  수준으로 끌어올린다
- prototype / baseline / production-candidate 전략을 다시 분류하고,
  어떤 전략부터 먼저 hardening할지 고정한다

### 핵심 내용
- strategy production audit matrix
- real-money promotion contract
- ETF 전략군 hardening
- strict annual family promotion
- quarterly prototype hold rule
- real-money strategy checklist 준비

### 상태
- `in_progress`

### 현재 상태 요약
- current active priority는
  `portfolio workflow polish`보다
  **실전 전략 승격**
  쪽이다
- 현재 전략군은 다음처럼 읽는 것이 맞다
  - ETF 전략군: first hardening 우선 후보
  - strict annual family: next promotion 대상
  - quarterly strict prototype family: research-only hold
- Phase 12 current first pass에서는
  - strategy audit
  - promotion contract 정의
  - 구현 우선순위 고정
  까지 먼저 정리한다

### 권고 방향
- fixed ETF 전략군부터 investability / cost / turnover / benchmark contract를 얹는다
- 그 다음 strict annual family를 dynamic PIT contract 위에서 승격한다
- quarterly strict prototype family는 무리하게 promotion하지 않는다

### 주요 문서
- `.note/finance/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
- `.note/finance/phase12/PHASE12_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase12/PHASE12_STRATEGY_PRODUCTION_AUDIT_MATRIX.md`
- `.note/finance/phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
- `.note/finance/phase12/PHASE12_TEST_CHECKLIST.md`

---

## Phase 6. Second Overlay And Quarterly Strict Expansion

### 목적
- strict annual family 위에 second overlay를 추가하고
  quarterly strict family의 실제 진입 경로와 validation 기준을 정리한다

### 핵심 내용
- `Market Regime Overlay` 계열 second overlay first pass
- strict family single / compare / history overlay 확장
- quarterly strict family entry criteria와 data-path audit
- quarterly strict candidate first validation
- interpretation / checklist / closeout 문서화

### 상태
- `completed`

### 현재 상태 요약
- Phase 6에서는
  - `Market Regime Overlay` first pass를 strict annual family에 연결했고
  - `Quality Snapshot (Strict Quarterly Prototype)` research-only entry path를 열었다
- manual validation과 follow-up UX/history fixes까지 마쳤고,
  현재 Phase 6는 closeout 완료 상태다
- 주요 결론:
  - annual strict family는 second overlay까지 연구 가능한 상태
  - quarterly strict family는 구현 가능성은 열렸지만 여전히 research-only이며,
    coverage가 늦게 시작되는 구조가 다음 major blocker로 남아 있다

### 주요 문서
- `.note/finance/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md`
- `.note/finance/phase6/PHASE6_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase6/PHASE6_COMPLETION_SUMMARY.md`
- `.note/finance/phase6/PHASE6_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_REQUIREMENTS.md`
- `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_FIRST_PASS.md`
- `.note/finance/phase6/PHASE6_MARKET_REGIME_OVERLAY_VALIDATION.md`
- `.note/finance/phase6/PHASE6_STRICT_QUARTERLY_ENTRY_CRITERIA.md`
- `.note/finance/phase6/PHASE6_STRICT_QUARTERLY_FIRST_PASS_VALIDATION.md`
- `.note/finance/phase6/PHASE6_TEST_CHECKLIST.md`
- `.note/finance/phase5/PHASE5_OVERLAY_RUNTIME_FIRST_PASS.md`
- `.note/finance/phase5/PHASE5_QUARTERLY_STRICT_FAMILY_REVIEW.md`
- `.note/finance/phase5/PHASE5_SECOND_OVERLAY_CANDIDATE_REVIEW.md`
- `.note/finance/phase5/PHASE5_COMPLETION_SUMMARY.md`
- `.note/finance/phase5/PHASE5_NEXT_PHASE_PREPARATION.md`

---

## 현재 위치

현재 프로젝트는:
- `Phase 1` 완료
- `Phase 2` 완료
- `Phase 3` 완료
- `Phase 4` 완료
- `Phase 5` first chapter 완료
- `Phase 6` 완료
- `Phase 7` 완료
- `Phase 8` 구현 완료 / manual validation pending
- `Phase 9` policy closeout 완료 / manual validation pending
- `Phase 10` practical closeout 완료
- `Phase 11` first-pass practical closeout 완료
- `Phase 12` in progress

현재 바로 이어지는 핵심 포인트:
- Phase 7에서 quarterly foundation과 PIT timing을 복구했다
- Phase 8과 Phase 9를 거치며
  - quarterly family/operator tooling/policy가 정리되었고
  - 다음 real-money priority는 dynamic PIT universe로 좁혀졌다
- Phase 10에서
  - dynamic PIT validation contract first/second pass가 실제 code/UI/history surface까지 연결되었다
  - 이제 static research mode를 넘는 실전형 validation contract는 확보된 상태다
- Phase 11에서는
  - saved portfolio first pass가 열려
  - compare / weighted portfolio / rerun을 반복 가능한 workflow object로 묶기 시작했다
- 이제 다음 active priority는
  - workflow polish가 아니라
  - 어떤 전략을 실제 투자 판단에 더 가깝게 승격할지 정리하는
    Phase 12다

즉 지금은
“실전형 validation contract와 workflow first pass는 확보했고,
이제 전략 자체를 real-money candidate 수준으로 hardening하는 단계”
라고 보는 것이 가장 정확하다.

---

## 앞으로의 운영 방식

앞으로는 새 작업을 시작할 때 아래 순서를 기본으로 한다.

1. 이 작업이 어느 Phase에 속하는지 먼저 결정
2. 그 Phase 문서 또는 챕터 TODO 보드에서 현재 위치 확인
3. 필요하면 문서 업데이트 후 작업 시작
4. 작업 중 변경사항이 생기면
   - 해당 Phase 문서
   - TODO 보드
   - WORK_PROGRESS
   - QUESTION_AND_ANALYSIS_LOG
   를 함께 갱신
5. 새로운 큰 묶음으로 넘어갈 때는 사용자와 Phase 개설 여부를 먼저 확인
