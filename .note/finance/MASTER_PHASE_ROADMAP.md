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
- `implementation_completed`
- `manual_validation_deferred`

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
- 사용자 manual validation은 Phase 8 검수와 함께 later batch review로 진행하기로 결정되었다

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
- `in_progress`

### 현재 상태 요약
- Phase 7에서 quarterly data foundation은 복구되었고
  `Quality Snapshot (Strict Quarterly Prototype)`는 longer-history에서 실제로 열리게 되었다
- 이제 남은 핵심은
  single prototype 하나에 머무는 quarterly path를
  strategy family 수준으로 확장하는 일이다

### 주요 문서
- `.note/finance/phase8/PHASE8_QUARTERLY_STRATEGY_FAMILY_EXPANSION_PLAN.md`
- `.note/finance/phase8/PHASE8_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phase7/PHASE7_QUARTERLY_RERUN_VALIDATION.md`
- `.note/finance/phase7/PHASE7_TEST_CHECKLIST.md`

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
- `Phase 7` implementation completed, manual validation deferred
- `Phase 8` in progress

현재 바로 이어지는 핵심 포인트:
- Phase 7에서 quarterly foundation과 PIT timing을 복구했다
- 이제 Phase 8에서는
  - quarterly value / quality+value family 확장
  - compare / history parity
  - promotion readiness 기준 정리
  를 다루는 단계다

즉 지금은
“quarterly strict family를 quality-only prototype에서
research strategy family 수준으로 확장하는 단계”
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
