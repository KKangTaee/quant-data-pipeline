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

## 제품 개발 방향성

### 이 섹션은 무엇인가

이 프로젝트의 최종 목표는
**사용자가 전략을 만들고 백테스트하고 검증한 뒤, 투자 후보와 포트폴리오 구성안을 제안받을 수 있는 퀀트 프로그램**을 개발하는 것이다.

다만 현재 phase 진행은 투자 결론을 먼저 내리는 단계가 아니라,
그 최종 목표에 필요한 데이터 수집, 백테스트, 전략 구현, 검증, 운영 기록 체계를 만드는 개발 단계다.

따라서 phase의 기본 진행은 아래 순서를 우선한다.

1. 데이터가 준비되어 있는가
2. 백테스트 엔진이 올바르게 계산하는가
3. 전략을 추가하거나 고도화할 수 있는가
4. 사용자가 UI에서 실행 / 비교 / 저장 / 재실행할 수 있는가
5. 결과를 읽고 검증할 수 있는가
6. 충분히 성숙한 뒤 paper / pre-live 운영 체계로 갈 수 있는가

### 기본 원칙

- 기본 phase 진행은 `개발 중심`이다.
- phase 문서에서 별도로 명시하지 않는 한,
  개별 백테스트 결과는 최종 투자 추천이나 실전 운용 승인으로 자동 해석하지 않는다.
- 개발 중 쓰는 baseline, fixture, representative portfolio는
  기능을 검증하기 위한 기준일 수 있으며,
  그 자체가 투자 기준점이라는 뜻은 아니다.
- 사용자가 QA나 테스트 과정에서 특정 전략 분석,
  백테스트 비교, 투자 가능성 검토를 명시적으로 요청하면
  그때는 분석과 백테스트를 수행한다.
- 단, 그렇게 수행한 분석은
  `사용자 요청 분석`으로 기록하고,
  기본 phase 방향이 투자 분석으로 바뀐 것으로 해석하지 않는다.

### 제품 레이어

| 레이어 | 무엇을 만드는가 | 현재 로드맵에서의 의미 |
|---|---|---|
| Data Layer | 가격, 재무제표, factor, profile 데이터를 수집하고 저장한다 | Phase 1~3의 핵심 기반 |
| Backtest Engine Layer | DB 데이터를 읽어 전략을 계산하고 성과를 만든다 | Phase 3~4에서 기본 연결 완료, 이후 계속 보강 |
| Strategy Library Layer | Value, Quality, GTAA, ETF, 신규 전략 등을 구현한다 | Phase 4~18에서 확장, Phase 23~24에서 다시 중요 |
| Backtest UX Layer | 사용자가 UI에서 실행, 비교, history, load/replay를 할 수 있게 한다 | Phase 4, 19, 20의 핵심 |
| Portfolio Workflow Layer | 여러 전략 결과를 묶고 저장하고 다시 재현한다 | Phase 20~22에서 기능 검증 |
| Validation / Review Layer | 결과가 신뢰 가능한지, 유지 / 교체 / 보류 판단을 남긴다 | Phase 12~22에서 일부 구현 |
| Paper / Pre-Live Layer | paper run, watchlist, hold, re-review 같은 운영 루틴을 준비한다 | Phase 25에서 시작 |
| Live Trading Layer | 실제 주문 / 브로커 연동 / 운용 자동화 | 현재 로드맵의 직접 범위 밖 |

### 지금 중요한 경계

`Phase 22`에서 portfolio workflow를 본 이유는
투자 포트폴리오를 고르기 위해서가 아니라,
프로그램이 여러 전략 결과를 섞고 저장하고 replay할 수 있는지 확인하기 위해서였다.

따라서 `Phase 22` 이후 기본 방향은
portfolio weight 분석을 계속 넓히는 것이 아니라,
아직 덜 구현된 핵심 제품 기능으로 돌아가는 것이다.

우선순위는 아래 순서가 더 자연스럽다.

1. `Phase 22` closeout 완료
2. `Phase 23` quarterly / alternate cadence productionization 완료
3. `Phase 24` new strategy expansion과 research-to-implementation bridge 완료
4. `Phase 25` validation / review / paper-readiness 운영 체계 시작

---

## 전체 상위 Phase 구조

### 빠른 읽기

- `Phase 1 ~ 5`
  - 데이터 수집 콘솔, loader/runtime, Backtest UI, 초기 전략 라이브러리와 overlay 기반을 만든 구간
- `Phase 6 ~ 12`
  - quarterly / strict family / dynamic PIT / portfolio workflow / real-money promotion surface를 확장한 구간
- `Phase 13 ~ 20`
  - 후보 품질 개선, downside refinement, structural redesign, contract cleanup, operator workflow hardening을 진행한 구간
- `Support Track`
  - plugin / registry / phase bootstrap 같은 repo-local 지원 tooling을 별도 관리하는 보조 트랙
- `Phase 21 ~ 25`
  - integrated validation과 portfolio workflow 개발 검증을 닫고,
    다시 quarterly / alternate cadence, new strategy, validation / pre-live scaffolding으로 돌아가는 개발 중심 구간

## Phase 1. Internal Data Collection Console

### 목적
- 내부 운영용 데이터 수집 웹앱 구축
- 수집 작업을 버튼 기반으로 실행 가능하게 만들기

### 핵심 내용
- Streamlit 기반 운영 UI
- OHLCV / fundamentals / factors / asset profile / financial statements 수집
- 실행 결과, 로그, 실패 확인
- 기본적인 운영 UX 확보

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

### 주요 문서
- `.note/finance/phases/phase1/INTERNAL_WEB_APP_DEVELOPMENT_GUIDE.md`
- `.note/finance/phases/phase1/PHASE1_WEB_APP_SCOPE.md`
- `.note/finance/phases/phase1/PHASE1_JOB_WRAPPER_INTERFACE.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

### 현재 하위 작업 묶음
- 일반 운영 고도화 작업 묶음
- point-in-time hardening 작업 묶음
- 종료 요약 문서

### 주요 문서
- `.note/finance/phases/phase2/PHASE2_WEB_APP_AND_BACKTEST_PLAN.md`
- `.note/finance/phases/phase2/PHASE2_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase2/PHASE2_POINT_IN_TIME_HARDENING_TODO.md`
- `.note/finance/phases/phase2/PHASE2_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase2/BACKTEST_LOADER_FUNCTION_DRAFT.md`
- `.note/finance/phases/phase2/BACKTEST_LOADER_INPUT_CONTRACT.md`
- `.note/finance/phases/phase2/BACKTEST_POINT_IN_TIME_GUIDELINES.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

### 주요 하위 작업 묶음
- loader/runtime groundwork 작업 묶음
- runtime generalization 작업 묶음
- UI structure decision 작업 묶음
- runtime public boundary 구체화 작업 묶음

### 현재 상태 요약
- 첫 loader 구현 작업 묶음 완료
- broad / strict statement loader까지 포함한 loader read-path 구현 완료
- DB-backed sample path 확보 완료
- 다음 포커스는 runtime 일반화와 Phase 4 handoff 준비

### 주요 문서
- `.note/finance/phases/phase3/PHASE3_LOADER_AND_RUNTIME_PLAN.md`
- `.note/finance/phases/phase3/PHASE3_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase3/PHASE3_CHAPTER1_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase3/PHASE3_RUNTIME_GENERALIZATION_TODO.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

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

### 진행 상태
- `partial_complete`

### 검증 상태
- `legacy_unknown`

### 현재 작업 묶음
- strategy library baseline + risk overlay design 작업 묶음

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
  Phase 5의 당시 작업 묶음은 여기서 closeout 되었다
- 즉:
  - 정식 `second chapter`가 따로 이어진 것이 아니라
  - 후속 주요 workstream은 `Phase 6`으로 분리되어 이어졌다

### 주요 문서
- `.note/finance/phases/phase5/PHASE5_STRATEGY_LIBRARY_AND_RISK_OVERLAY_PLAN.md`
- `.note/finance/phases/phase5/PHASE5_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase5/PHASE5_BASELINE_STRICT_FAMILY_COMPARATIVE_RESEARCH.md`
- `.note/finance/phases/phase5/PHASE5_COMPARE_ADVANCED_INPUT_PARITY_FIRST_PASS.md`
- `.note/finance/phases/phase5/PHASE5_FIRST_OVERLAY_REQUIREMENTS_AND_SELECTION.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

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
- `.note/finance/phases/phase6/PHASE6_OVERLAY_AND_QUARTERLY_EXPANSION_PLAN.md`
- `.note/finance/phases/phase6/PHASE6_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase6/PHASE6_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase6/PHASE6_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase6/PHASE6_MARKET_REGIME_OVERLAY_REQUIREMENTS.md`
- `.note/finance/phases/phase6/PHASE6_MARKET_REGIME_OVERLAY_FIRST_PASS.md`
- `.note/finance/phases/phase6/PHASE6_MARKET_REGIME_OVERLAY_VALIDATION.md`
- `.note/finance/phases/phase6/PHASE6_STRICT_QUARTERLY_ENTRY_CRITERIA.md`
- `.note/finance/phases/phase6/PHASE6_STRICT_QUARTERLY_FIRST_PASS_VALIDATION.md`
- `.note/finance/phases/phase6/PHASE6_TEST_CHECKLIST.md`
- `.note/finance/phases/phase5/PHASE5_OVERLAY_RUNTIME_FIRST_PASS.md`
- `.note/finance/phases/phase5/PHASE5_QUARTERLY_STRICT_FAMILY_REVIEW.md`
- `.note/finance/phases/phase5/PHASE5_SECOND_OVERLAY_CANDIDATE_REVIEW.md`
- `.note/finance/phases/phase5/PHASE5_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase5/PHASE5_NEXT_PHASE_PREPARATION.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

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
- `.note/finance/phases/phase7/PHASE7_QUARTERLY_COVERAGE_AND_STATEMENT_PIT_HARDENING_PLAN.md`
- `.note/finance/phases/phase7/PHASE7_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase7/PHASE7_STATEMENT_SOURCE_PAYLOAD_INSPECTION.md`
- `.note/finance/phases/phase7/PHASE7_RAW_STATEMENT_LEDGER_REVIEW_AND_DECISION.md`
- `.note/finance/phases/phase7/PHASE7_QUARTERLY_COVERAGE_HARDENING_FIRST_PASS.md`
- `.note/finance/phases/phase7/PHASE7_SUPPLEMENTARY_POLISH_PASS.md`
- `.note/finance/phases/phase7/PHASE7_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase7/PHASE7_NEXT_PHASE_PREPARATION.md`

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

### 진행 상태
- `implementation_complete`

### 검증 상태
- `manual_qa_pending`

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
- `.note/finance/phases/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
- `.note/finance/phases/phase8/PHASE8_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase8/PHASE8_QUARTERLY_FAMILY_SCOPE_AND_COMPARE_DECISION.md`
- `.note/finance/phases/phase8/PHASE8_QUARTERLY_VALUE_AND_MULTI_FACTOR_FIRST_PASS.md`
- `.note/finance/phases/phase8/PHASE8_QUARTERLY_VALIDATION_FIRST_PASS.md`
- `.note/finance/phases/phase8/PHASE8_PRICE_STALE_DIAGNOSIS_FIRST_PASS.md`
- `.note/finance/phases/phase8/PHASE8_STATEMENT_SHADOW_COVERAGE_GAP_DIAGNOSTICS.md`
- `.note/finance/phases/phase8/PHASE8_OPERATOR_RUNTIME_AND_SHADOW_REBUILD_TOOLING.md`
- `.note/finance/phases/phase8/PHASE8_STATEMENT_COVERAGE_DIAGNOSIS_GUIDANCE.md`
- `.note/finance/phases/phase8/PHASE8_TEST_CHECKLIST.md`

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

### 진행 상태
- `implementation_complete`

### 검증 상태
- `manual_qa_pending`

### 현재 상태 요약
- Phase 8까지 구현된 diagnostics / operator tooling을 이제 policy 레벨로 고정해야 하는 단계다
- `MRSH`, `AU` 같은 exception case가 단순 operator 이슈가 아니라 strict coverage 정책의 입력으로 다뤄지기 시작했다
- 현재 작업 묶음은
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
- `.note/finance/phases/phase9/PHASE9_STRICT_COVERAGE_POLICY_AND_PROMOTION_PLAN.md`
- `.note/finance/phases/phase9/PHASE9_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase9/PHASE9_REAL_MONEY_VALIDATION_DIRECTION.md`
- `.note/finance/phases/phase9/PHASE9_STRICT_COVERAGE_EXCEPTION_INVENTORY.md`
- `.note/finance/phases/phase9/PHASE9_STRICT_COVERAGE_POLICY_DECISION.md`
- `.note/finance/phases/phase9/PHASE9_STRICT_FAMILY_PROMOTION_GATE.md`
- `.note/finance/phases/phase9/PHASE9_OPERATOR_DECISION_TREE.md`
- `.note/finance/phases/phase9/PHASE9_TEST_CHECKLIST.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

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
- `.note/finance/phases/phase10/PHASE10_HISTORICAL_DYNAMIC_PIT_UNIVERSE_PLAN.md`
- `.note/finance/phases/phase10/PHASE10_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase10/PHASE10_PIT_SOURCE_AND_SCHEMA_GAP_ANALYSIS.md`
- `.note/finance/phases/phase10/PHASE10_DYNAMIC_PIT_FIRST_PASS_IMPLEMENTATION_ORDER.md`
- `.note/finance/phases/phase10/PHASE10_ANNUAL_STRICT_DYNAMIC_PIT_FIRST_PASS.md`
- `.note/finance/phases/phase10/PHASE10_DYNAMIC_PIT_SECOND_PASS_HARDENING.md`
- `.note/finance/phases/phase10/PHASE10_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase10/PHASE10_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase10/PHASE10_TEST_CHECKLIST.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

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
- `.note/finance/phases/phase11/PHASE11_PORTFOLIO_PRODUCTIZATION_AND_RESEARCH_WORKFLOW_PLAN.md`
- `.note/finance/phases/phase11/PHASE11_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase11/PHASE11_EXECUTION_PREPARATION.md`
- `.note/finance/phases/phase11/PHASE11_SAVED_PORTFOLIO_FIRST_PASS.md`
- `.note/finance/phases/phase11/PHASE11_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase11/PHASE11_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase11/PHASE11_TEST_CHECKLIST.md`

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

### 진행 상태
- `practical_closeout`

### 검증 상태
- `manual_qa_pending`

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
- `.note/finance/phases/phase12/PHASE12_REAL_MONEY_STRATEGY_PROMOTION_PLAN.md`
- `.note/finance/phases/phase12/PHASE12_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase12/PHASE12_STRATEGY_PRODUCTION_AUDIT_MATRIX.md`
- `.note/finance/phases/phase12/PHASE12_REAL_MONEY_PROMOTION_CONTRACT.md`
- `.note/finance/phases/phase12/PHASE12_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase12/PHASE12_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase12/PHASE12_TEST_CHECKLIST.md`

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

### 진행 상태
- `implementation_complete`

### 검증 상태
- `manual_qa_pending`

### 현재 상태 요약
- Phase 12는 practical closeout 되었지만,
  user-side manual validation은 아직 pending이다
- 따라서 현재 운영 기준은:
  - `Phase 12`: `practical_closeout` / `manual_qa_pending`
  - `Phase 13`: `implementation_complete` / `manual_qa_pending`
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
- `.note/finance/phases/phase13/PHASE13_DEPLOYMENT_READINESS_AND_PROBATION_PLAN.md`
- `.note/finance/phases/phase13/PHASE13_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase13/PHASE13_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase13/PHASE13_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase13/PHASE13_TEST_CHECKLIST.md`

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

### 진행 상태
- `practical_closeout`

### 검증 상태
- `manual_qa_pending`

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
- `.note/finance/phases/phase14/PHASE14_REAL_MONEY_GATE_CALIBRATION_AND_DEPLOYMENT_WORKFLOW_PLAN.md`
- `.note/finance/phases/phase14/PHASE14_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase14/PHASE14_GATE_BLOCKER_DISTRIBUTION_AUDIT_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_PROMOTION_SHORTLIST_CALIBRATION_REVIEW_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_CONTROLLED_FACTOR_EXPANSION_SHORTLIST_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_NEAR_MISS_CANDIDATE_CASE_STUDY_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_POLICY_SENSITIVITY_REVIEW_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_ETF_OPERABILITY_SENSITIVITY_REVIEW_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_STRICT_ANNUAL_VALIDATION_STATUS_FIXED_THRESHOLD_REVIEW_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_ETF_OPERABILITY_DATA_COVERAGE_INTERPRETATION_REVIEW_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_FAMILY_SPECIFIC_THRESHOLD_EXPERIMENT_DESIGN_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_DEPLOYMENT_WORKFLOW_BRIDGE_FIRST_PASS.md`
- `.note/finance/phases/phase14/PHASE14_PIT_OPERABILITY_LATER_PASS_DECISION.md`
- `.note/finance/phases/phase14/PHASE14_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase14/PHASE14_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase14/PHASE14_TEST_CHECKLIST.md`

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

### 진행 상태
- `practical_closeout`

### 검증 상태
- `manual_qa_pending`

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
- `.note/finance/phases/phase15/PHASE15_CANDIDATE_QUALITY_IMPROVEMENT_PLAN.md`
- `.note/finance/phases/phase15/PHASE15_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase15/PHASE15_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase15/PHASE15_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase15/PHASE15_TEST_CHECKLIST.md`
- `.note/finance/backtest_reports/phase15/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
- `.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

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
- `.note/finance/phases/phase16/README.md`
- `.note/finance/phases/phase16/PHASE16_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase16/PHASE16_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
- `.note/finance/phases/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
- `.note/finance/phases/phase16/PHASE16_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase16/PHASE16_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase16/PHASE16_TEST_CHECKLIST.md`
- `.note/finance/backtest_reports/phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md`
- `.note/finance/backtest_reports/phase16/PHASE16_QUALITY_VALUE_STRONGEST_POINT_DOWNSIDE_FOLLOWUP_SECOND_PASS.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
- `.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md`

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

### 진행 상태
- `complete`

### 검증 상태
- `legacy_unknown`

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
- `.note/finance/phases/phase17/README.md`
- `.note/finance/phases/phase17/PHASE17_STRUCTURAL_DOWNSIDE_IMPROVEMENT_PLAN.md`
- `.note/finance/phases/phase17/PHASE17_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase17/PHASE17_STRUCTURAL_LEVER_INVENTORY_FIRST_PASS.md`
- `.note/finance/phases/phase17/PHASE17_CANDIDATE_CONSOLIDATION_FIT_REVIEW_FIRST_PASS.md`
- `.note/finance/phases/phase17/PHASE17_PARTIAL_CASH_RETENTION_IMPLEMENTATION_FIRST_SLICE.md`
- `.note/finance/phases/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_IMPLEMENTATION_SECOND_SLICE.md`
- `.note/finance/phases/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_IMPLEMENTATION_THIRD_SLICE.md`
- `.note/finance/phases/phase17/PHASE17_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase17/PHASE17_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase17/PHASE17_TEST_CHECKLIST.md`

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

### 진행 상태
- `practical_closeout`

### 검증 상태
- `manual_qa_pending`

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
- `.note/finance/phases/phase18/PHASE18_LARGER_STRUCTURAL_REDESIGN_PLAN.md`
- `.note/finance/phases/phase18/PHASE18_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase18/PHASE18_IMPLEMENTATION_FIRST_REPRIORITIZATION.md`
- `.note/finance/phases/phase18/PHASE18_NEXT_RANKED_FILL_IMPLEMENTATION_FIRST_SLICE.md`
- `.note/finance/phases/phase18/PHASE18_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase18/PHASE18_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase18/PHASE18_TEST_CHECKLIST.md`
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

### 진행 상태
- `complete`

### 검증 상태
- `manual_qa_completed`

### 현재 상태 요약
- strict annual 구조 옵션 3축이 operator-facing contract 언어로 정리되었다.
  - rejected-slot handling
  - weighting
  - risk-off
- history / compare / prefill / interpretation이 같은 contract 언어를 더 많이 공유하게 되었다.
- `Phase 19`는 deep rerun phase가 아니라
  **구조 옵션의 뜻과 기록 방식을 안정화하는 phase**로 manual checklist까지 완료된 상태다.

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

### 진행 상태
- `complete`

### 검증 상태
- `manual_qa_completed`

### 현재 상태 요약
- `Phase 19`에서 strict annual contract language를 읽기 쉽게 정리한 뒤,
  이제는 strongest / near-miss candidate를 다시 보고 비교하고 저장하는 흐름을 다듬는 단계로 넘어왔다.
- `Phase 20`은 deep rerun phase가 아니라,
  current candidate와 portfolio bridge를 operator workflow 관점에서 더 실용적으로 만드는 phase로 시작되었다.
- 첫 실제 구현 단위로는
  `Compare & Portfolio Builder` 안에 current candidate re-entry surface를 붙여,
  current anchor / near-miss를 바로 compare로 다시 보내는 동선을 열었다.
- 이어서 compare source context를 weighted portfolio와 saved portfolio까지 이어,
  지금 보고 있는 compare bundle의 출처와 다음 행동을 더 직접적으로 보이게 만들었다.
- 현재는
  current candidate -> compare -> weighted portfolio -> saved portfolio
  흐름이 실제 operator workflow 기준으로 더 자연스럽게 읽히는 상태까지 정리되었고,
  manual checklist 기준 검수도 완료되었다.

## Support Track. Research Automation And Experiment Persistence

### 목적
- repo-local script / registry / plugin / skill 같은 지원 tooling을 유지한다
- 다만 이것은 main finance product phase가 아니라
  **support track**으로 관리한다

### 쉽게 말하면
- 현재 desktop agent 환경과 repo-local tooling을 더 편하게 쓰기 위한 작업이다
- 유용하지만,
  전략 / 백테스트 / 후보 검증 자체를 한 단계 진전시키는 main phase로 세지는 않는다

### 왜 필요한가
- support tooling은 계속 도움이 되지만,
  이걸 main phase로 세면 실제 quant project roadmap과 agent 환경 정리가 섞여 버린다

### 진행 상태
- `complete`

### 검증 상태
- `not_applicable`

### 현재 상태 요약
- phase bundle bootstrap
- current candidate registry
- hygiene / plugin / skill sync
  는 이미 support tooling으로 usable한 상태다

---

## Phase 21. Integrated Deep Backtest Validation

### 목적
- `Value`, `Quality`, `Quality + Value` current candidate를
  같은 validation frame에서 다시 크게 검증한다
- strongest / lower-MDD alternative / portfolio bridge를
  유지 / 교체 / 보류 기준으로 다시 판단한다

### 쉽게 말하면
- 지금까지 만든 후보를
  이제 한 판에서 다시 크게 검증해보는 단계다

### 왜 필요한가
- `Phase 15 ~ 20` 동안 후보와 workflow는 충분히 쌓였지만,
  아직 current anchor를 한 기준에서 다시 확인하는 deep validation은 남아 있다

### 예상 핵심 내용
- integrated rerun matrix
- family별 comparative validation
- anchor replacement / rescue / defer 여부 재판단
- weighted / saved portfolio bridge validation

### 진행 상태
- `complete`

### 검증 상태
- `manual_qa_completed`

### 현재 상태 요약
- `Phase 18` closeout 이후 immediate next main phase로 실제 진행했다
- first work unit에서
  - 공통 validation period
  - 공통 universe frame
  - family별 current anchor / alternative rerun pack
  - representative portfolio bridge frame
  - rerun report / strategy log naming rule
  을 먼저 고정했다
- 그 뒤 actual rerun pack에서:
  - `Value` current anchor 유지
  - `Quality` current anchor 유지
  - `Quality + Value` current strongest point 유지
  를 확인했다
- 마지막 portfolio bridge validation에서는
  `33 / 33 / 34` weighted bundle이
  `28.66% / -25.42% / Sharpe 1.51`로 나왔고,
  saved portfolio replay도 exact match로 재현됐다
- Phase 21 checklist QA도 완료되어,
  이제 다음 main phase는 `Phase 22` portfolio-level candidate construction이다

### 주요 문서
- `.note/finance/phases/phase21/PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md`
- `.note/finance/phases/phase21/PHASE21_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md`
- `.note/finance/phases/phase21/PHASE21_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase21/PHASE21_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase21/PHASE21_TEST_CHECKLIST.md`

---

## Phase 22. Portfolio-Level Candidate Construction

### 목적
- single-strategy result를 넘어
  여러 전략 결과를 portfolio로 묶는 workflow가 제대로 작동하는지 검증한다
- weighted bundle이 단순 화면 결과가 아니라 재현 가능한 기록으로 남을 수 있는지 검토한다
- portfolio 후보를 후보라고 부를 기준과 최소 기록 항목을 먼저 고정하되,
  live investment approval로 해석하지 않는다

### 쉽게 말하면
- 전략 묶음이 더 좋은 투자 후보인지 고르는 단계가 아니라,
  프로그램이 전략 묶음을 portfolio로 만들고 저장 / replay / 비교할 수 있는지 확인하는 단계다
- 여기서 쓰는 equal-third baseline은 투자 benchmark가 아니라 개발 검증용 fixture baseline이다

### 왜 필요한가
- 장기적으로 실제 운용에는 portfolio-level construction도 필요하지만,
  지금은 그 전에 프로그램 기능이 신뢰 가능하게 작동하는지 확인해야 하기 때문이다
- `Phase 21`에서 `33 / 33 / 34` portfolio bridge가 재현 가능하다는 점은 확인했지만,
  아직 실전 portfolio winner나 deployment 기준을 정하는 단계는 아니기 때문이다

### 예상 핵심 내용
- portfolio-level candidate semantics definition
- multi-strategy bundle validation
- portfolio-level interpretation / promotion draft
- development-validation baseline and weight alternative check
- saved portfolio replay validation

### 진행 상태
- `complete`

### 검증 상태
- `manual_qa_completed`

### 현재 상태 요약
- `Phase 22` phase bundle을 생성했다
- kickoff plan에서 `Phase 22` 목적을
  "weighted portfolio를 재현 가능한 portfolio-level candidate로 다룰 기준을 세우는 단계"로 정리했다
- 첫 번째 작업 단위에서:
  - `Portfolio-Level Candidate`
  - `Portfolio Bridge`
  - `Component Strategy`
  - `Date Alignment`
  - `Saved Portfolio Replay`
  의미를 정리했다
- `Phase 21`의 `33 / 33 / 34` bridge는 저장 정의 기준
  `[33.33, 33.33, 33.33]` equal-third baseline으로 다시 정리했다
- 첫 portfolio-level report에서
  `phase22_annual_strict_equal_third_baseline_v1`을
  `baseline_candidate / portfolio_watchlist / not_deployment_ready`로 고정했다
- 두 번째 작업 단위에서 portfolio-level benchmark / guardrail interpretation과
  weight alternative 비교 범위를 정했다
- Phase 22 primary portfolio benchmark는 equal-third baseline이고,
  next weight alternatives는 `25 / 25 / 50`, `40 / 40 / 20`으로 좁혔다
- 이 baseline은 투자 benchmark가 아니라 같은 fixture 조합을 검증하기 위한 개발 기준이다
- weight alternative rerun에서:
  - `25 / 25 / 50`은 CAGR은 좋아졌지만 `Quality + Value` 편중이 커져 watch alternative로 보류했다
  - `40 / 40 / 20`은 MDD는 조금 낮아졌지만 CAGR을 포기해 comparison-only 후보로 보류했다
  - 따라서 equal-third baseline을 primary portfolio benchmark로 유지한다
- Phase 22 checklist QA까지 완료되었으므로,
  Phase 22는 `complete` / `manual_qa_completed` 상태로 닫는다
- 다음 기본 작업은
  `Phase 23 Quarterly And Alternate Cadence Productionization`을 열어
  quarterly / alternate cadence를 제품 기능 수준으로 끌어올리는 것이다
- 단, 사용자가 명시적으로 portfolio 분석을 요청하면
  추가 백테스트 / 분석을 수행할 수 있다.
  이 경우에도 그것은 기본 phase 방향 변경이 아니라
  `사용자 요청 분석`으로 기록한다

### 주요 문서
- `.note/finance/phases/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md`
- `.note/finance/phases/phase22/PHASE22_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md`
- `.note/finance/phases/phase22/PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md`
- `.note/finance/phases/phase22/PHASE22_COMPLETION_SUMMARY.md`
- `.note/finance/phases/phase22/PHASE22_NEXT_PHASE_PREPARATION.md`
- `.note/finance/phases/phase22/PHASE22_TEST_CHECKLIST.md`
- `.note/finance/backtest_reports/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`
- `.note/finance/backtest_reports/phase22/PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md`

---

## Phase 23. Quarterly And Alternate Cadence Productionization

### 목적
- 현재 prototype 성격이 강한 quarterly strict family와
  alternate cadence 실행 경로를 실제 제품 기능으로 끌어올린다
- 목표는 투자 후보를 바로 고르는 것이 아니라,
  annual strict family처럼 입력, 실행, compare, report, history가
  일관되게 작동하는 cadence lane을 만드는 것이다

### 쉽게 말하면
- 지금은 annual 쪽은 비교적 잘 돌아가지만,
  quarterly 쪽은 아직 prototype 성격이 남아 있다.
- Phase 23은 quarterly / alternate cadence를
  "실제로 백테스트 기능으로 쓸 수 있는 수준"까지 올리는 단계다

### 왜 필요한가
- 여러 전략을 제대로 탐색하려면
  annual만으로는 부족하고 quarterly / alternate cadence도 같은 품질의 실행 경로가 필요하다
- 아직 이 lane이 prototype이면,
  이후 새로운 전략을 붙이거나 deep validation을 할 때 비교 기준이 흔들린다

### 예상 핵심 내용
- quarterly strict prototype의 runtime / UI / report / history 경로 점검
- quarterly factor timing과 point-in-time 해석 보강
- annual / quarterly / alternate cadence 입력 contract 정리
- compare / saved replay에서 cadence별 설정 복원 확인
- compare 화면에서 공용 실행 입력과 strategy-specific 입력 분리
- 최소 representative smoke rerun과 manual checklist 작성

### 진행 상태
- `complete`

### 검증 상태
- `manual_qa_completed`

---

## Phase 24. New Strategy Expansion

### 목적
- core cadence와 backtest UX가 안정된 뒤,
  새로운 전략 family를 다시 추가한다
- `quant-research`의 전략 문서가
  실제 finance strategy implementation으로 이어지는 bridge를 정리한다

### 쉽게 말하면
- 프로그램이 어느 정도 안정되면,
  이제 Value / Quality 중심에서 벗어나
  다른 전략도 구현해 볼 수 있어야 한다
- Phase 24는 "전략 분석"보다
  "새 전략을 이 프로그램에 추가하는 표준 경로"를 만드는 단계다

### 왜 필요한가
- 전략을 계속 수동으로 붙이면
  매번 입력, report, history, compare 연결이 달라져 유지보수가 어려워진다
- research note에서 implementation까지 이어지는 기준이 있어야
  이후 전략 라이브러리를 안정적으로 넓힐 수 있다

### 예상 핵심 내용
- new strategy shortlist
- research-to-implementation bridge
- first new family implementation
- strategy template / report template alignment
- compare / history / saved replay 연결 기준

### 진행 상태
- `complete`

### 검증 상태
- `manual_qa_completed`

### 현재 메모
- 첫 구현 후보는 `Global Relative Strength`로 고정했다.
- core strategy, DB-backed sample helper, web runtime wrapper, compile / import / DB-backed smoke validation은 완료했다.
- `Backtest` UI, compare, history, saved replay 연결까지 완료했다.
- 기본 preset QA 중 확인된 `EEM` 이력 부족과 `IWM` 결측 가격 행은
  `excluded_tickers`, `malformed_price_rows`, 한국어 주의사항으로 드러내는 방향으로 정리했다.
- 사용자 manual checklist QA까지 완료했다.

---

## Phase 25. Pre-Live Operating System And Deployment Readiness

### 목적
- 충분히 구현된 전략과 백테스트 workflow를
  paper / watchlist / review 중심 운영 체계로 묶는다
- 이 phase도 실제 주문 / live trading을 바로 여는 단계가 아니라,
  pre-live 판단과 운영 기록을 정리하는 단계다

### 쉽게 말하면
- 전략을 "좋아 보인다"에서 끝내지 않고,
  paper run으로 관찰하고,
  어떤 조건에서 보류하거나 다시 볼지 정하는 운영판을 만드는 단계다

### 왜 필요한가
- 백테스트 결과만으로는 실전 준비가 끝났다고 볼 수 없다
- 최소한 paper / review / monitoring 기준이 있어야
  사용자가 실전 투입 여부를 별도 판단할 수 있다

### 예상 핵심 내용
- operator review workflow
- probation / monitoring persistence
- deployment readiness playbook
- promotion / shortlist language cleanup
- paper-run checklist
- pre-live dashboard or report draft

### 진행 상태
- `complete`

### 검증 상태
- `manual_qa_completed`

### 현재 메모
- Phase 25는 live trading이나 투자 승인 단계가 아니다.
- 현재 첫 작업으로 `Real-Money 검증 신호`와 `Pre-Live 운영 점검`의 경계를 고정했다.
- 두 번째 작업으로 Pre-Live 후보 기록 포맷과 `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` 저장 위치를 고정했다.
- 세 번째 작업으로 current candidate에서 Pre-Live 기록 초안을 만드는 `draft-from-current` helper workflow를 추가했다.
- 네 번째 작업으로 `Backtest > Pre-Live Review` 패널을 추가했다.
- Phase 25 manual QA까지 완료했다.

---

## 현재 위치

상태값은 `.note/finance/FINANCE_DOC_INDEX.md`의 `Phase 상태값 읽는 법`을 따른다.
이 프로젝트는 별도 chapter 체계를 도입하지 않고,
phase의 `진행 상태`와 `검증 상태`를 분리해서 관리한다.

주의:
- 이 문서의 위쪽 phase별 상세 기록에는 당시 기준의 legacy 상태 표현이 남아 있을 수 있다.
- 현재 gate 판단은 아래 `현재 위치` 표와
  `.note/finance/phases/phase26/PHASE26_BACKLOG_REBASE_AND_FOUNDATION_GAP_MAP.md`를 우선한다.

| Phase | 진행 상태 | 검증 상태 | 현재 해석 |
|---|---|---|---|
| Phase 1 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 2 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 3 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 4 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 5 | `partial_complete` | `legacy_unknown` | legacy `first_chapter_completed` 표현을 `partial_complete`로 읽음 |
| Phase 6 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 7 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 8 | `complete` | `superseded_by_later_phase` | Phase 23 quarterly productionization에 흡수 |
| Phase 9 | `complete` | `superseded_by_later_phase` | Phase 10/12/23/25 흐름에 흡수 |
| Phase 10 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 11 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 12 | `complete` | `superseded_by_later_phase` | Real-Money first pass가 Phase 13~15/25에 흡수 |
| Phase 13 | `complete` | `superseded_by_later_phase` | probation language가 Phase 25 Pre-Live로 재정의 |
| Phase 14 | `complete` | `superseded_by_later_phase` | calibration 설계가 Phase 27~29에서 다룰 주제로 정리 |
| Phase 15 | `complete` | `superseded_by_later_phase` | candidate workflow가 registry/report 흐름으로 흡수 |
| Phase 16 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 17 | `complete` | `legacy_unknown` | 과거 완료 phase. 필요 시 과거 문서 확인 |
| Phase 18 | `complete` | `superseded_by_later_phase` | 남은 구조 작업은 future structural option |
| Phase 19 | `complete` | `manual_qa_completed` | 완료 |
| Phase 20 | `complete` | `manual_qa_completed` | 완료 |
| Support Track | `complete` | `not_applicable` | phase가 아닌 지원 도구 흐름 |
| Phase 21 | `complete` | `manual_qa_completed` | 완료 |
| Phase 22 | `complete` | `manual_qa_completed` | 완료 |
| Phase 23 | `complete` | `manual_qa_completed` | 완료 |
| Phase 24 | `complete` | `manual_qa_completed` | 완료 |
| Phase 25 | `complete` | `manual_qa_completed` | 완료 |
| Phase 26 | `complete` | `manual_qa_completed` | 완료 |
| Phase 27 | `complete` | `manual_qa_completed` | 완료 |
| Phase 28 | `complete` | `manual_qa_completed` | Capability + Replay + Data Trust + Real-Money/Guardrail parity QA 완료 |
| Phase 29 | `complete` | `manual_qa_completed` | Candidate Review Board + Result Handoff + Review Notes + Registry Draft QA 완료 |
| Phase 30 | `implementation_complete` | `manual_qa_pending` | product-flow 재정렬, Portfolio Proposal 계약 정의, registry I/O helper 분리, Proposal Draft UI, Monitoring Review, Pre-Live Feedback, Paper Tracking Feedback 구현 |

한 줄 현재 판단:
- current annual strict candidate와 portfolio bridge를 같은 frame에서 다시 본 `Phase 21`은 manual validation까지 완료되었고,
  `Phase 22`도 portfolio workflow 개발 검증과 manual QA까지 완료되었다.
  `Phase 23` quarterly / alternate cadence productionization도 manual QA까지 완료되었다.
  `Phase 24`는 `Global Relative Strength`를 첫 신규 전략 후보로 구현하고
  core/runtime smoke, `Backtest` UI, compare, history, saved replay, 사용자 QA까지 끝낸 상태다.
  `Phase 25`는 Real-Money 검증 신호와 Pre-Live 운영 점검의 경계를 고정했고,
  Pre-Live 후보 기록 포맷, 저장 위치, helper 기반 operator review workflow, `Backtest > Pre-Live Review` UI까지 구현했다.
  사용자 manual QA까지 완료했다.
  `Phase 26`은 과거 pending 상태와 foundation gap을 재분류했고, 사용자 checklist QA까지 완료했다.
  `Phase 27`은 데이터 신뢰성과 백테스트 결과 해석 표면을 강화했고, 사용자 checklist QA까지 완료했다.
  `Phase 28`도 사용자 QA까지 완료되어 전략 family별 지원 범위와 cadence 차이,
  history / saved portfolio 재실행과 form 복원 가능성,
  compare / weighted data trust, Real-Money / Guardrail scope가 closeout 기준으로 정리되었다.
  `Phase 29`는 `Backtest > Candidate Review`에서 current candidate를 검토 보드로 읽고
  compare 또는 Pre-Live Review로 넘기는 workflow와, Latest / History 결과를 후보 검토 초안으로 보내는 handoff,
  초안을 별도 Candidate Review Note로 저장하는 흐름,
  그리고 review note를 current candidate registry row 초안으로 변환해 명시적으로 append하는 흐름을 구현하고
  사용자 QA까지 완료한 상태다.
  `Phase 30`은 implementation_complete / manual_qa_pending 상태다.
  첫 작업은 Phase 29 이후 기준으로 사용 흐름을 다시 정렬하고,
  16k lines 이상으로 커진 `app/web/pages/backtest.py`의 점진 리팩토링 경계를 정리하는 것이었다.
  두 번째 작업으로 Portfolio Proposal row의 목적, 후보 역할, 비중 근거, risk constraints,
  evidence snapshot, blocker, operator decision 계약을 정의했다.
  세 번째 작업으로 current candidate / review note / pre-live registry JSONL I/O helper를
  `app/web/runtime/candidate_registry.py`로 분리했다.
  네 번째 작업으로 `Backtest > Portfolio Proposal`에서 current candidate 여러 개를 proposal draft로 묶고
  `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`에 append-only로 저장하는 UI / helper를 추가했다.
  다섯 번째 작업으로 저장된 proposal draft를 blocker / review gap / 후보 구성 관점에서 다시 보는
  `Monitoring Review` tab을 추가했다.
  여섯 번째 작업으로 proposal snapshot과 현재 Pre-Live registry 상태를 비교하는
  `Pre-Live Feedback` tab을 추가했다.
  일곱 번째 작업으로 proposal evidence snapshot과 현재 Pre-Live result snapshot의 CAGR / MDD를 비교하는
  `Paper Tracking Feedback` tab을 추가했다.

---

## Phase 26~30 개발 로드맵

### 이 섹션은 무엇인가
- `현재 위치`가 지금 상태를 보여주는 상태판이라면,
  이 섹션은 Phase 25 이후 어떤 순서로 제품 기반을 강화할지 보여주는 다음 구간 안내판이다.
- 이 구간의 목적은 Live Readiness / Final Approval로 바로 가는 것이 아니라,
  그 전에 필요한 데이터 신뢰성, 전략 parity, 후보 검토, 포트폴리오 제안 기반을 만드는 것이다.

### 핵심 원칙
- 기본 흐름은 개발 / 검증 / 운영 workflow 구축이다.
- 사용자가 명시적으로 요청할 때만 투자 분석, 후보 비교, 실전 적합성 분석을 한다.
- 강한 백테스트 결과가 자동으로 투자 추천이나 live trading 승인으로 이어지지 않는다.
- Live Readiness / Final Approval은 Phase 30 이후 별도 phase로 다룬다.

### Phase 26~30 요약

| Phase | 이름 | 진행 상태 | 검증 상태 | 쉽게 말하면 |
|---|---|---|---|---|
| Phase 26 | Foundation Stabilization And Backlog Rebase | `complete` | `manual_qa_completed` | 과거 backlog와 pending 상태를 현재 제품 기준으로 다시 정리했고 QA까지 완료했다 |
| Phase 27 | Data Integrity And Backtest Trust Layer | `complete` | `manual_qa_completed` | 백테스트 전에 데이터가 믿을 만한지, 어디까지 계산 가능한지 보여주고 QA까지 완료했다 |
| Phase 28 | Strategy Family Parity And Cadence Completion | `complete` | `manual_qa_completed` | annual / quarterly / 신규 전략의 지원 범위, 재진입 상태, compare data trust, Real-Money / Guardrail scope를 화면에서 구분하고 QA까지 완료했다 |
| Phase 29 | Candidate Review And Recommendation Workflow | `complete` | `manual_qa_completed` | current candidate를 검토 보드로 읽고, Latest / History 결과를 후보 검토 초안, review note, registry draft로 넘기는 workflow를 구현하고 QA까지 완료했다 |
| Phase 30 | Portfolio Proposal And Pre-Live Monitoring Surface | `implementation_complete` | `manual_qa_pending` | 후보들을 포트폴리오 제안으로 묶는 draft UI / persistence와 저장 proposal monitoring review, Pre-Live feedback, Paper Tracking feedback 비교를 구현했고 사용자 QA가 남아 있다 |

### Phase 26. Foundation Stabilization And Backlog Rebase

### 목적
- 오래된 `manual_qa_pending`, `practical_closeout`, remaining backlog 표현을 현재 제품 기준으로 다시 읽는다.
- immediate blocker, next-phase input, future option, legacy note를 구분한다.

### 왜 먼저 하는가
- Phase 27 이후로 바로 기능을 늘리면 과거 phase 상태와 새 roadmap이 충돌할 수 있다.
- 특히 Phase 18 structural backlog와 Phase 8/9/12~15의 pending 상태가 현재도 blocker인지 먼저 봐야 한다.

### 현재 메모
- Phase 26 implementation과 사용자 checklist QA는 완료되었다.
- 과거 pending 상태는 immediate blocker가 아니라 Phase 27~30에서 다룰 주제 또는 future option으로 재분류했다.
- 새 전략 구현이나 deep backtest는 이번 phase에서 하지 않았다.

### Phase 27. Data Integrity And Backtest Trust Layer

### 목적
- 백테스트 실행 전에 데이터 가능 범위와 신뢰성 문제를 더 명확히 보여준다.
- missing ticker, stale price, malformed row, common-date truncation 같은 이슈를 사용자가 놓치지 않게 만든다.

### 현재 메모
- Phase 27은 complete / manual_qa_completed 상태다.
- `Backtest Data Trust Summary`와 `Global Relative Strength price freshness preflight`를 구현했다.
- 사용자가 `Price Freshness Preflight`, `Data Trust Summary`, `Data Quality Details`, Meta/history 연결을 QA했다.
- 새 전략 발굴이나 투자 후보 판정은 이번 phase의 목적이 아니었다.

### 왜 필요한가
- Phase 24 QA에서 `EEM`, `IWM`, 공통 날짜 문제처럼 데이터 때문에 결과 범위가 달라지는 사례가 이미 드러났다.
- 전략 성과를 판단하기 전에 결과가 어떤 데이터 조건에서 나온 것인지 알아야 한다.

### Phase 28. Strategy Family Parity And Cadence Completion

### 목적
- annual strict, quarterly strict, price-only 신규 전략이 UI / payload / history / saved replay / Real-Money / Guardrail에서 어느 정도 같은 사용성을 갖게 만든다.

### 왜 필요한가
- 지금 annual strict는 가장 성숙하지만 quarterly와 신규 전략은 아직 일부 검증 surface가 다르다.
- 전략을 더 늘리기 전에 family별 차이를 의도된 차이와 미완성 차이로 나눠야 한다.

### 현재 메모
- Phase 28은 complete / manual_qa_completed phase다.
- 첫 작업은 `Strategy Capability Snapshot`이었다.
- Single Strategy와 Compare 전략 박스에서 cadence, data trust, Real-Money/Guardrail, history/replay 지원 범위를 표로 보여준다.
- 두 번째 작업으로 `History Replay / Load Parity Snapshot`을 추가해 selected history record의 재실행 / form 복원 관련 저장 상태를 볼 수 있게 했다.
- 세 번째 작업으로 `Saved Portfolio Replay / Load Parity Snapshot`을 추가해 저장 포트폴리오의 전략 목록, weight/date alignment, strategy override 저장 상태를 볼 수 있게 했다.
- 네 번째 작업으로 compare / weighted / saved replay에서도 component별 data trust를 볼 수 있게 했다.
- 다섯 번째 작업으로 compare / history / saved portfolio에 Real-Money / Guardrail scope 표를 추가했다.
- Phase 29 `Candidate Review And Recommendation Workflow`는 사용자 QA까지 완료됐다.

### Phase 29. Candidate Review And Recommendation Workflow

### 목적
- 백테스트 결과를 current candidate, near miss, watchlist, pre-live 후보로 넘기는 흐름을 표준화한다.

### 왜 필요한가
- 최종 목표는 투자 후보와 포트폴리오 구성안을 제안하는 프로그램이다.
- 그러려면 좋은 결과를 볼 때마다 임시 문서로 판단하지 않고, 반복 가능한 후보 검토 절차가 필요하다.

### 현재 메모
- Phase 29는 complete / manual_qa_completed 상태다.
- 첫 작업으로 `Backtest > Candidate Review` panel을 추가했다.
- 이 panel은 current candidate registry의 active 후보를 review board로 보여주고,
  후보별 review stage, 존재 이유, 다음 행동 제안을 표시한다.
- 선택한 후보는 Pre-Live Review로 넘길 수 있고, 후보 묶음은 기존 compare re-entry로 보낼 수 있다.
- 두 번째 작업으로 Latest Backtest Run 또는 History 결과를 candidate review 초안으로 넘기는 handoff를 추가했다.
- 세 번째 작업으로 candidate review 초안을 별도 review note로 저장하는 흐름을 추가했다.
- 네 번째 작업으로 review note를 current candidate registry row 초안으로 변환하고, 명시적 append 버튼으로만 후보 registry에 기록하는 흐름을 추가했다.
- 다음 작업 후보는 Phase 30을 바로 구현하기 전,
  Phase 29 이후 기준의 사용 흐름 재정렬과 `backtest.py` 리팩토링 경계 검토다.

### Phase 30. Portfolio Proposal And Pre-Live Monitoring Surface

### 목적
- 후보들을 사용자 정의 포트폴리오, 제안 포트폴리오, paper tracking, pre-live monitoring 관점에서 볼 수 있게 만든다.

### 왜 필요한가
- 단일 전략 후보만으로는 최종 product goal인 포트폴리오 구성 제안까지 가기 어렵다.
- 다만 이 phase도 live trading 승인이 아니라 proposal / monitoring surface까지를 목표로 한다.

### 현재 메모
- Phase 30은 implementation_complete / manual_qa_pending 상태다.
- 첫 작업 단위는 portfolio proposal 기능 구현이 아니라,
  `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 Phase 29 이후 기준으로 다시 정렬하는 것이었다.
- 기준 흐름은 `Ingestion / Data Trust -> Single Strategy Backtest -> Real-Money Signal -> Hold / Blocker Resolution -> Compare -> Candidate Packaging -> Compare 재검토 또는 Pre-Live Review -> Portfolio Proposal -> Live Readiness / Final Approval`이다.
- `backtest.py`가 16k lines 이상으로 커졌으므로, Candidate Review / Pre-Live / registry helper / History / Saved Portfolio / result display / strategy forms를 어떤 순서로 점진 분리할지 먼저 문서화했다.
- 두 번째 작업으로 Portfolio Proposal row 계약을 정의했다.
  이 계약은 proposal objective, component candidates, target weights, risk constraints, evidence snapshot, open blockers, operator decision을 포함한다.
- 세 번째 작업으로 `app/web/runtime/candidate_registry.py`를 추가해 current candidate / candidate review note / pre-live registry JSONL read / append helper를 분리했다.
- 네 번째 작업으로 `app/web/runtime/portfolio_proposal.py`와 `Backtest > Portfolio Proposal` panel을 추가했다.
  current candidate 여러 개를 proposal draft로 묶고, 목적 / 역할 / target weight / weight reason / operator decision을 확인한 뒤
  `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`에 append-only로 저장할 수 있다.
- 다섯 번째 작업으로 `Backtest > Portfolio Proposal > Monitoring Review` tab을 추가했다.
  저장된 proposal draft의 monitoring state, component table, blocker, review gap, operator decision을 확인할 수 있다.
- 여섯 번째 작업으로 `Backtest > Portfolio Proposal > Pre-Live Feedback` tab을 추가했다.
  저장된 proposal snapshot과 현재 Pre-Live registry active record를 비교할 수 있다.
- 일곱 번째 작업으로 `Backtest > Portfolio Proposal > Paper Tracking Feedback` tab을 추가했다.
  저장된 proposal evidence snapshot과 현재 Pre-Live result snapshot의 CAGR / MDD, performance signal, tracking plan을 비교할 수 있다.
- 추가 코드 분리는 Candidate Review / Pre-Live / History / Saved Portfolio 같은 별도 special refactor task에서 점진 진행한다.

### Phase 30 이후
- Live Readiness / Final Approval은 Phase 30 이후 별도 phase로 연다.
- 이 단계에서는 실제 돈을 넣어도 되는지 최종 판단 기준, paper tracking 근거, blocker 해소 여부, 승인 / 보류 / 거절 기록을 다룬다.

### 한 줄 흐름
- `정리 -> 데이터 신뢰성 -> 전략 parity -> 후보 검토 -> 포트폴리오 제안 -> 이후 live readiness`

---

## 앞으로의 운영 방식

앞으로는 새 작업을 시작할 때 아래 순서를 기본으로 한다.

1. 이 작업이 어느 Phase에 속하는지 먼저 결정한다
2. 그 Phase 문서 또는 TODO 보드에서 현재 위치를 먼저 확인한다
3. 필요하면 Phase 문서와 roadmap을 먼저 갱신한 뒤 구현이나 검증으로 들어간다
4. 작업 중 변경사항이 생기면
   - 해당 Phase 문서
   - TODO 보드
   - `WORK_PROGRESS.md`
   - `QUESTION_AND_ANALYSIS_LOG.md`
   를 함께 갱신한다
5. support tooling처럼 main product phase가 아닌 작업은
   - phase 번호에 억지로 넣지 않고
   - support track 문서로 별도 관리한다
6. 새로운 큰 묶음으로 넘어갈 때는 사용자와 phase 개설 여부를 먼저 확인한다
7. phase 진행 중 백테스트 분석이 필요하면 수행하되,
   - 사용자가 명시적으로 요청한 분석인지
   - 제품 기능 검증을 위한 fixture인지
   - 투자 후보 판단인지
   를 문서에서 구분한다
