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
- `completed`

### 현재 상태 요약
- current active priority는
  `portfolio workflow polish`보다
  **실전 전략 승격**
  쪽이다
- 현재 전략군은 다음처럼 읽는 것이 맞다
  - ETF 전략군: first hardening 우선 후보
  - strict annual family: next promotion 대상
  - quarterly strict prototype family: research-only hold
- Phase 12에서는
  - strategy audit
  - promotion contract 정의
  - ETF 전략군 first-pass hardening
  - strict annual family promotion surface 보강
  - strategy surface consolidation
  까지 practical closeout 가능한 수준으로 완료되었다
- remaining ETF second-pass guardrail / PIT operability later pass는
  다음 phase backlog로 넘기는 것이 맞다

### 권고 방향
- fixed ETF 전략군부터 investability / cost / turnover / benchmark contract를 얹고,
  current-operability AUM / spread policy까지 붙이는 방향은 완료되었다
- strict annual family도 dynamic PIT contract 위에서
  validation / guardrail / promotion surface를 practical 수준으로 갖췄다
- quarterly strict prototype family는 여전히 무리하게 promotion하지 않는 것이 맞다
- 다음 active phase는
  second-pass deployment-readiness / probation / monitoring 쪽으로 여는 것이 자연스럽다

### 주요 문서
- `.note/finance/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
- `.note/finance/phase12/PHASE12_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase12/PHASE12_STRATEGY_PRODUCTION_AUDIT_MATRIX.md`
- `.note/finance/phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
- `.note/finance/phase12/PHASE12_COMPLETION_SUMMARY.md`
- `.note/finance/phase12/PHASE12_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase12/PHASE12_TEST_CHECKLIST.md`

---

## Phase 13. Deployment Readiness And Probation

### 목적
- Phase 12에서 `real-money candidate` 수준까지 정리한 전략들을,
  실제 운용 후보 shortlist로 다시 좁히고
  **배치 전 검증 / probation / monitoring 계약**
  으로 연결한다
- 이제 중요한 것은 전략을 더 많이 늘리는 일이 아니라,
  이미 승격된 후보를 어떤 기준으로 실제 투입 후보로 볼지 정하는 일이다

### 핵심 내용
- candidate shortlist contract
- ETF second-pass hardening
- probation / monitoring workflow
- out-of-sample / rolling validation workflow
- deployment-readiness checklist

### 상태
- `completed`

### 현재 상태 요약
- Phase 12는 practical closeout 되었지만,
  user-side manual validation은 아직 pending이다
- 따라서 현재 운영 기준은:
  - `Phase 12`: implementation closed / manual_validation_pending
  - `Phase 13`: practical closeout / manual_validation_pending
- 이번 phase에서는
  - shortlisted candidate 상태 language 고정
  - ETF second-pass backlog 재정리
  - paper / small-capital probation workflow 초안
  - rolling / out-of-sample review contract
  - deployment-readiness checklist
  까지를 practical 기준으로 정리했다

### 권고 방향
- 백테스트 winner를 바로 실제 투자 전략으로 해석하지 말고,
  `watchlist -> paper_probation -> small_capital_trial -> hold`
  같은 shortlist 상태로 관리하는 운영 계약이 먼저 필요하다
- ETF 전략군은 Phase 12 first-pass hardening 위에
  second-pass guardrail / operability review를 추가하는 것이 자연스럽다
- strict annual family는 promotion surface를 확보했으므로,
  이제는 추가 기능보다 probation / monitoring 관점에서 재해석하는 쪽이 우선이다

### 주요 문서
- `.note/finance/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md`
- `.note/finance/phase13/PHASE13_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase13/PHASE13_COMPLETION_SUMMARY.md`
- `.note/finance/phase13/PHASE13_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase13/PHASE13_TEST_CHECKLIST.md`

---

## Phase 14. Real-Money Gate Calibration And Deployment Workflow Bridge

### 목적
- Phase 13까지 열린 `promotion / shortlist / probation / deployment-readiness` surface를
  실제 운영 판단에 더 쓸 수 있게 calibration한다
- repeated `hold / watchlist_only / blocked` 결과가
  전략 문제인지, gate threshold 문제인지, 데이터/contract 문제인지 분리해서 본다
- shortlist 후보를 실제 paper probation / small-capital trial 해석으로 이어주는
  operator workflow bridge를 더 분명히 만든다

### 핵심 내용
- gate blocker distribution audit
- promotion / shortlist calibration review
- deployment workflow bridge
- ETF PIT operability later-pass planning

### 상태
- `practical_closeout / manual_validation_pending`

### 현재 상태 요약
- Phase 13 checklist QA를 통해
  UI 설명 surface와 glossary는 많이 보강되었다
- 하지만 사용자 보류 항목이었던
  `real-money gate calibration`
  논의는 이제 representative rerun evidence와 calibration review 문서 기준으로 정식 수행되었다
- Phase 14 first-pass에서는
  representative candidate와 current code gate logic을 기준으로
  blocker audit을 먼저 수행했고,
  strict annual repeated hold의 핵심이
  `validation / validation_policy` 쪽에 있음을 문서화했다
- 동시에 이후 aggregate audit를 위해
  backtest history schema에 `gate_snapshot` persistence를 추가했다
- 이어서 calibration review를 통해
  - factor 부족이 repeated hold의 1차 원인이 아님을 분리했고
  - strict annual repeated hold는 internal `validation_status`,
  - ETF repeated hold는 `partial data coverage` interpretation이 더 직접적인 blocker임을 좁혔다
- 이후 Phase 14 후반부에서는
  - family-specific threshold experiment design
  - deployment workflow bridge definition
  - PIT operability later-pass decision
  까지 정리되어,
  현재는 next implementation phase를 bounded하게 열 수 있는 상태다

### 주요 문서
- `.note/finance/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md`
- `.note/finance/phase14/PHASE14_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase14/PHASE14_GATE_BLOCKER_DISTRIBUTION_AUDIT_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_PROMOTION_SHORTLIST_CALIBRATION_REVIEW_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_NEAR_MISS_CANDIDATE_CASE_STUDY_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_POLICY_SENSITIVITY_REVIEW_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_ETF_OPERABILITY_SENSITIVITY_REVIEW_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_STATUS_FIXED_THRESHOLD_REVIEW_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_ETF_OPERABILITY_DATA_COVERAGE_INTERPRETATION_REVIEW_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_FAMILY_SPECIFIC_THRESHOLD_EXPERIMENT_DESIGN_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_DEPLOYMENT_WORKFLOW_BRIDGE_FIRST_PASS.md`
- `.note/finance/phase14/PHASE14_PIT_OPERABILITY_LATER_PASS_DECISION.md`
- `.note/finance/phase14/PHASE14_COMPLETION_SUMMARY.md`
- `.note/finance/phase14/PHASE14_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase14/PHASE14_TEST_CHECKLIST.md`

---

## Phase 15. Candidate Quality Improvement

### 목적
- Phase 14에서 gate를 설명 가능하게 만든 뒤,
  이제는 실제 후보 전략의 품질을 더 좋게 만드는 방향으로 탐색한다
- blanket threshold relaxation보다
  stronger baseline / downside-improved candidate / strategy-specific cumulative logging을 우선한다

### 핵심 내용
- `Value` downside-improvement search
- `Quality`, `Quality + Value` candidate-improvement search
- 전략별 backtest log 누적
- strongest baseline 대비 tradeoff 정리

### 상태
- `practical closeout / manual_validation_pending`

### 현재 상태 요약
- strongest `Value > Strict Annual` baseline은
  여전히 `real_money_candidate / paper_probation / review_required` exact candidate다
- Phase 15 first pass에서는
  overlay / cadence / top-N 조합을 먼저 보았고,
  overlay보다 `Top N diversification`이
  downside 개선에 더 유효한 레버라는 점을 확인했다
- 현재 대표 downside-improved candidate는
  `Top N = 14` 조합이며,
  strongest baseline 대비
  `CAGR 29.89% -> 27.48%`,
  `MDD -29.15% -> -24.55%`
  개선/희생 tradeoff를 보여준다
- Phase 15 second pass에서는
  `Top N = 14 + psr` 조합이 current best addition candidate로 확인되었고,
  같은 `MDD -24.55%` 수준에서 `CAGR 28.13%`까지 끌어올렸다
- `Quality` family는 같은 bounded addition pass를 current literal preset semantics 기준으로 다시 돌렸을 때
  single-factor addition만으로는 non-hold candidate를 회복하지 못했다
- `Quality + Value` family는 value-side controlled addition까지 넓혀 보니
  `per` addition이
  `real_money_candidate / small_capital_trial / review_required`
  current strongest practical candidate로 확인됐다
- 이후 pass를 거치며
  - `Quality`는
    rescued candidate와 downside-improved candidate까지 확보했다
  - `Quality + Value`는
    `ocf_yield -> pcr`,
    `net_margin -> operating_margin`
    replacement를 거쳐
    `CAGR = 31.25% / MDD = -26.63% / real_money_candidate / small_capital_trial / review_required`
    current strongest practical point를 고정했다
- sixth-pass `Top N` follow-up까지 다시 본 결과,
  `Top N = 10`이 strongest practical point로 유지됐다
- 따라서 Phase 15는
  family별 strongest/current candidate를 확보하고
  strategy hub / one-pager / backtest log 운영 체계를 정리한 상태로
  practical closeout까지 왔다

### 주요 문서
- `.note/finance/phase15/PHASE15_CANDIDATE_QUALITY_IMPROVEMENT_PLAN.md`
- `.note/finance/phase15/PHASE15_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase15/PHASE15_COMPLETION_SUMMARY.md`
- `.note/finance/phase15/PHASE15_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase15/PHASE15_TEST_CHECKLIST.md`
- `.note/finance/backtest_reports/phase15/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
- `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`

---

## Phase 17. Structural Downside Improvement

### 목적
- Phase 16에서 bounded refinement가 practical 기준으로 닫힌 뒤,
  strict annual family의 lower-MDD practical candidate를 만들기 위한
  구조 레버를 current code 기준으로 좁힌다
- 동시에 weighted portfolio / saved portfolio가
  immediate practical-candidate work의 메인 트랙인지,
  operator bridge 보조 트랙인지 분리한다

### 핵심 내용
- strict annual structural lever inventory first pass
- candidate consolidation fit review first pass
- `Value`와 `Quality + Value`에 공통으로 적용 가능한 first implementation slice 결정
- phase17 current board / code-flow / skill sync

### 상태
- `completed`

### 현재 상태 요약
- `Value`와 `Quality + Value` 모두에서 bounded `Top N` / one-factor / minimal overlay tweak은 충분히 소진되었다
- current code 기준으로 가장 먼저 볼 구조 레버는:
  - partial cash retention
  - defensive sleeve risk-off
  - concentration-aware weighting
- Phase 17 current pass 기준으로
  - `partial cash retention`
  - `defensive sleeve risk-off`
  - `concentration-aware weighting`
  first three slices는 모두 구현 완료 상태다
- representative rerun 기준으로는
  세 레버 모두 구현/검증 가치는 있었지만
  current `Value` / `Quality + Value` anchor를 대체하는
  same-gate lower-MDD exact rescue는 만들지 못했다
- 다음 active question은
  current 3개 structural lever 결과를 묶어
  next phase에서
  `larger structural redesign`
  또는
  `candidate consolidation / operator bridge`
  를 어떻게 열지 다시 정리하는 것이다
- weighted portfolio / saved portfolio는 지금도 유용하지만,
  즉시 `promotion / shortlist / deployment`를 대체하는 계층은 아니므로
  Phase 17에서는 operator bridge 보조 트랙으로 둔다

### 주요 문서
- `.note/finance/phase17/README.md`
- `.note/finance/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md`
- `.note/finance/phase17/PHASE17_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase17/PHASE17_STRUCTURAL_LEVER_INVENTORY_FIRST_PASS.md`
- `.note/finance/phase17/PHASE17_CANDIDATE_CONSOLIDATION_FIT_REVIEW_FIRST_PASS.md`
- `.note/finance/phase17/PHASE17_PARTIAL_CASH_RETENTION_IMPLEMENTATION_FIRST_SLICE.md`
- `.note/finance/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_IMPLEMENTATION_SECOND_SLICE.md`
- `.note/finance/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_IMPLEMENTATION_THIRD_SLICE.md`
- `.note/finance/phase17/PHASE17_COMPLETION_SUMMARY.md`
- `.note/finance/phase17/PHASE17_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase17/PHASE17_TEST_CHECKLIST.md`

---

## Phase 18. Larger Structural Redesign

### 목적
- Phase 17 first three structural levers 이후에도
  current `Value` / `Quality + Value` anchor를 교체하는
  same-gate lower-MDD exact rescue가 없었기 때문에,
  더 큰 selection-structure redesign을 실제 코드에 연결한다
- 기존 strongest family를 유지한 채
  실전형 gate와 downside를 같이 개선할 수 있는지 본다

### 핵심 내용
- strict annual `next-ranked eligible fill` first slice
- single / compare / history / rerun surface 연결
- `Value` / `Quality + Value` representative rerun first pass
- anchor replacement와 meaningful rescue를 분리해서 기록
- implementation-first reprioritization
- remaining structural/operator backlog 정리 후 deeper rerun 재개

### 상태
- `in_progress`

### 현재 상태 요약
- user confirmation 기준 next direction은 `larger structural redesign`로 고정되었다
- first slice는
  `Fill Rejected Slots With Next Ranked Names`
  contract를 strict annual family 3종에 연결하는 것으로 좁혔다
- current first-pass result:
  - `Value`
    - trend-on probe와 anchor-near second pass 모두
      still `hold / blocked`
    - meaningful redesign reference이지만
      current practical anchor replacement는 아니다
  - `Quality + Value`
    - `CAGR`, `MDD`, cash share는 개선되었지만
      still `hold / blocked`였다
- 즉 이 redesign은 meaningful new lane이지만,
  current practical anchor replacement는 아니다
- 또한 현재 운영 모드는
  deeper rerun expansion보다
  **implementation-first reprioritization**
  으로 전환된 상태다
- remaining structural/operator backlog를 더 구현한 뒤
  integrated deep rerun을 다시 여는 것이 current phase 원칙이다

### 주요 문서
- `.note/finance/phase18/PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md`
- `.note/finance/phase18/PHASE18_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase18/PHASE18_IMPLEMENTATION_FIRST_REPRIORITIZATION.md`
- `.note/finance/phase18/PHASE18_NEXT_RANKED_FILL_IMPLEMENTATION_FIRST_SLICE.md`
- `.note/finance/backtest_reports/phase18/README.md`
- `.note/finance/backtest_reports/phase18/PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md`

---

## Phase 19. Structural Contract Expansion And Interpretation Cleanup

### 목적
- `Phase 18`에서 열린 larger structural redesign lane을
  실제 usable contract 수준으로 더 넓힌다
- strict annual family의 rejection / risk-off / weighting semantics를
  operator가 읽기 쉬운 형태로 정리한다

### 쉽게 말하면
- 구조 옵션이 늘어난 지금,
  그 옵션을 “계속 써도 헷갈리지 않는 기능”으로 다듬는 단계다

### 왜 필요한가
- 지금 deep backtest를 더 넓히는 것보다
  contract와 interpretation을 먼저 정리해야
  이후 검증 결과도 덜 흔들린다

### 예상 핵심 내용
- second / third structural slice implementation
- interpretation / history / meta cleanup
- minimal validation 기준으로 contract behavior 고정
- first active slice:
  - `Rejected Slot Handling Contract`
    - strict annual single / compare / history / runtime에서
      trend rejection 처리 semantics를 explicit mode로 정리
    - legacy boolean payload도 계속 복원 가능하게 유지

### 상태
- `practical closeout / manual_validation_pending`

### 현재 상태 요약
- strict annual 구조 옵션 3축이 operator-facing contract 언어로 정리되었다.
  - rejected-slot handling
  - weighting
  - risk-off
- history / compare / prefill / interpretation이 같은 contract 언어를 더 많이 공유하게 되었다.
- `Phase 19`는 deep rerun phase가 아니라
  **구조 옵션의 뜻과 기록 방식을 안정화하는 phase**로 practical closeout 상태다.

---

## Phase 20. Candidate Consolidation And Operator Workflow Hardening

### 목적
- strongest / near-miss candidate를
  compare -> weighted -> saved portfolio 흐름과 더 자연스럽게 연결한다
- portfolio bridge를 operator workflow 관점에서 더 실용적으로 만든다

### 쉽게 말하면
- 좋은 후보를 찾는 것뿐 아니라
  그 후보를 다시 꺼내 보고 비교하고 저장하는 흐름을 정리하는 단계다

### 왜 필요한가
- 후보가 늘수록 연구보다 관리가 더 어려워지기 때문에,
  operator workflow를 먼저 단단하게 만들 필요가 있다

### 예상 핵심 내용
- candidate summary / bundle organization
- compare-to-portfolio bridge polish
- saved portfolio usability hardening

### 상태
- `in_progress`

### 현재 상태 요약
- `Phase 19`에서 strict annual contract language를 읽기 쉽게 정리한 뒤,
  이제는 strongest / near-miss candidate를 다시 보고 비교하고 저장하는 흐름을 다듬는 단계로 넘어왔다.
- `Phase 20`은 deep rerun phase가 아니라,
  current candidate와 portfolio bridge를 operator workflow 관점에서 더 실용적으로 만드는 phase로 시작되었다.

---

## Phase 21. Research Automation And Experiment Persistence

### 목적
- 반복되는 refinement / rerun / documentation 흐름을 더 자동화한다
- repo-local plugin / skill / checklist workflow를 practical 수준으로 끌어올린다

### 쉽게 말하면
- 반복 연구를 손작업 중심에서
  더 재현 가능하고 자동화된 흐름으로 바꾸는 단계다

### 왜 필요한가
- 구현과 검증이 커질수록
  실험 관리 비용도 커지기 때문에,
  deep validation 전에 자동화를 먼저 붙이는 것이 효율적이다

### 예상 핵심 내용
- experiment preset / scenario persistence
- documentation/checklist automation
- repo-local plugin / skill practical upgrade

### 상태
- `practical closeout / manual_validation_pending`

### 현재 상태 요약
- `Phase 21`에서는 반복적인 phase 문서 작업을 줄이기 위한
  phase bundle bootstrap script를 추가했다.
- current candidate를 machine-readable하게 남기는
  `CURRENT_CANDIDATE_REGISTRY.jsonl` baseline도 열었다.
- hygiene / plugin / skill 문서도 이 새 workflow를 알도록 같이 정리했다.

---

## Phase 22. Integrated Deep Backtest Validation

### 목적
- `Phase 19 ~ 21`에서 구현을 더 쌓은 뒤
  integrated deep backtest를 다시 연다
- strongest / near-miss / redesigned contract를
  같은 validation frame에서 다시 검증한다

### 쉽게 말하면
- 구현을 더 쌓아둔 뒤,
  strongest candidate를 다시 진짜 크게 검증하는 단계다

### 왜 필요한가
- 현재는 구현이 먼저지만,
  결국 strongest / rescue / replacement를 다시 확정하는 큰 검증은 반드시 필요하다

### 예상 핵심 내용
- integrated rerun matrix
- family별 comparative validation
- anchor replacement / rescue 여부 재판단

### 상태
- `proposed`

---

## Phase 23. Portfolio-Level Candidate Construction

### 목적
- single-strategy candidate를 넘어
  portfolio-level candidate construction을 본격적으로 다룬다
- weighted bundle가 portfolio candidate로 해석될 수 있는지 검토한다

### 쉽게 말하면
- 전략 하나가 아니라
  전략 묶음이 더 좋은 후보가 되는지 보는 단계다

### 왜 필요한가
- 실제 운용은 single-strategy만이 아니라
  portfolio-level construction도 중요하기 때문이다

### 예상 핵심 내용
- multi-strategy bundle validation
- portfolio-level interpretation / promotion draft
- strongest portfolio candidate search

### 상태
- `proposed`

---

## Phase 24. New Strategy Expansion

### 목적
- 기존 strongest family 고도화 이후
  다시 새로운 전략 family를 연다
- `quant-research`와 implementation bridge를 더 명시적으로 연결한다

### 쉽게 말하면
- 기존 핵심 전략을 충분히 다듬은 뒤,
  새로운 전략을 다시 늘리는 단계다

### 왜 필요한가
- 너무 일찍 새 전략을 열면 범위만 넓어지고,
  지금까지 만든 strongest family 정리가 흐려질 수 있기 때문이다

### 예상 핵심 내용
- new strategy shortlist
- research-to-implementation bridge
- first new family implementation

### 상태
- `proposed`

---

## Phase 25. Pre-Live Operating System And Deployment Readiness

### 목적
- current candidate / portfolio candidate를
  paper / small-capital trial 관점의 운영 체계로 연결한다
- 지금까지 만든 promotion / shortlist / probation / deployment surface를
  실제 operator workflow로 묶는다

### 쉽게 말하면
- 좋은 후보를 실제로 어떻게 paper / trial 단계까지 가져갈지
  운영 루틴을 정리하는 단계다

### 왜 필요한가
- 좋은 전략이 있어도
  review / probation / deployment workflow가 없으면
  실전 준비가 완성됐다고 보기 어렵기 때문이다

### 예상 핵심 내용
- operator review workflow
- probation / monitoring persistence
- deployment readiness playbook

### 상태
- `proposed`

---

## Phase 18~25 Draft Big Picture

- 구현 우선:
  - `Phase 18`
  - `Phase 19`
  - `Phase 20`
  - `Phase 21`
- 그 뒤 deep validation:
  - `Phase 22`
- 그 다음 확장:
  - `Phase 23`
  - `Phase 24`
  - `Phase 25`

- 현재 권고 reading:
  - 지금은 deep backtest를 더 넓히기보다
    structural / operator / automation backlog를 먼저 쌓는 것이 맞다
  - 그래서 future roadmap은
    `implement first -> validate deeply later -> expand after validation`
    순서로 읽는 것이 가장 자연스럽다

### 참고 문서
- `.note/finance/ROADMAP_REBASE_PHASE18_TO_PHASE25_20260414.md`

---

## Phase 16. Downside-Focused Practical Refinement

### 목적
- Phase 15에서 확보한 `Value`와 `Quality + Value` current practical anchor를 유지하면서
  `MDD`를 더 낮추거나, 같은 gate tier를 유지한 채 더 좋은 practical point를 찾는 bounded refinement를 수행한다
- blanket gate relaxation보다
  `Top N` narrow band, one-factor addition/replacement, minimal overlay sensitivity를 우선한다

### 핵심 내용
- `Value > Strict Annual` downside refinement first pass
- `Quality + Value > Strict Annual` downside refinement first pass
- `Value` current practical anchor `Top N = 14 + psr` rescue second pass
- `Quality + Value` current strongest practical anchor downside follow-up second pass
- strategy log / hub snapshot / one-pager 운영 체계 유지

### 상태
- `completed`

### 현재 상태 요약
- `Value > Strict Annual`의 current practical anchor는
  여전히 `real_money_candidate / paper_probation / review_required` exact candidate다
- lower-MDD rescue second pass에서도 `Top N = 14 + psr`가 current best practical point로 유지됐다
- `Value`에서는 strongest lower-MDD near-miss가 `+ pfcr`였지만
  `production_candidate / watchlist`에서 멈췄고,
  `Top N = 15 + psr + pfcr`는 gate를 회복했지만 downside edge를 잃었다
- `Quality + Value`에서는 `ocf_yield -> pcr` 위에 `operating_income_yield -> por` replacement가 더해진 조합이
  `CAGR = 31.82% / MDD = -26.63% / real_money_candidate / small_capital_trial / review_required`로 current strongest practical point가 됐다
- `Quality + Value` second pass에서도 lower-MDD 대안은 있었지만
  practical gate를 그대로 유지한 채 `MDD`만 더 낮추는 exact hit는 없었다
- 따라서 Phase 16 결론은
  bounded refinement closeout 후 structural downside improvement로 넘어가는 것이다

### 주요 문서
- `.note/finance/phase16/README.md`
- `.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase16/PHASE16_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
- `.note/finance/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
- `.note/finance/phase16/PHASE16_COMPLETION_SUMMARY.md`
- `.note/finance/phase16/PHASE16_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phase16/PHASE16_TEST_CHECKLIST.md`
- `.note/finance/backtest_reports/phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md`
- `.note/finance/backtest_reports/phase16/PHASE16_QUALITY_VALUE_STRONGEST_POINT_DOWNSIDE_FOLLOWUP_SECOND_PASS.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md`

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
- `Phase 12` practical closeout 완료
- `Phase 13` practical closeout 완료 / manual validation pending
- `Phase 14` practical closeout 완료 / manual validation pending
- `Phase 15` practical closeout 완료 / manual validation pending
- `Phase 16` practical closeout 완료 / manual validation pending
- `Phase 17` practical closeout 완료 / manual validation pending
- `Phase 18` larger structural redesign / implementation-first reprioritization 진행 중
- `Phase 19 ~ 25`는 draft roadmap으로 재정렬 완료

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
- Phase 12에서는
  - ETF 전략군 first-pass hardening
  - strict annual family promotion surface
  - strategy surface consolidation
  까지 practical closeout 되었다
- 현재는
  `Phase 15`에서 family별 current strongest candidate를 practical closeout 수준까지 정리했고,
  `Phase 16`에서 bounded downside refinement를 닫았고,
  `Phase 17`에서 first three structural levers를 구현/검증했고,
  `Phase 18`에서 larger structural redesign first slice를 구현했고,
  지금은 implementation-first 모드로 remaining backlog를 정리 중이다
- 지금 가장 자연스러운 immediate next step은
  broader rerun을 더 미는 것이 아니라
  `Phase 18` second slice 후보를 구현 관점에서 먼저 좁히는 것이다
- 그리고 그 뒤의 큰 흐름은:
  - `Phase 19~21`
    implementation / operator / automation 확대
  - `Phase 22`
    integrated deep validation 재개
  - `Phase 23~25`
    portfolio / new strategy / pre-live workflow 확장

즉 지금은
“실전형 validation contract, workflow first pass, strategy promotion first pass,
deployment-readiness / probation / monitoring 계약과 gate calibration 설명까지 확보했고,
이제는 actual candidate quality를 더 좋게 만드는 larger structural redesign을
구현 우선 모드로 밀어야 하는 단계이며,
그 이후에는 Phase 19~25 draft roadmap 순서로
구현 -> deep validation -> 확장으로 넘어가는 단계”
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
