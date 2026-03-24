# Phase 4 UI And Backtest Plan

## 목적
이 문서는 `finance` 프로젝트의 Phase 4 계획 문서다.

Phase 4의 정식 이름:
- `Portfolio Construction And Backtest UI`

이 단계의 목적은
Phase 3에서 정리한 DB-backed runtime 경로를 바탕으로,
사용자가 웹 UI에서 전략을 선택하고 백테스트를 실행할 수 있게 만드는 것이다.

---

## Phase 4의 핵심 목표

Phase 4 종료 시점에 확보하고 싶은 상태:

1. 사용자가 UI에서 전략을 선택할 수 있다
2. 사용자가 최소 입력으로 DB-backed 백테스트를 실행할 수 있다
3. 결과를 표/요약/차트 형태로 바로 확인할 수 있다
4. 기존 수집 UI와 백테스트 UI의 역할이 명확히 분리된다
5. 이후 factor / fundamental 전략 UI 확장을 위한 입력/출력 경계가 유지된다

---

## 사용자 협업 원칙

Phase 4는 UI/UX와 공개 실행 경계가 직접 결정되는 단계다.

따라서 아래 항목은 Codex가 단독으로 확정하지 않는다.

반드시 사용자에게:
- 선택지별 장단점
- 구현 영향
- 이후 확장성 차이

를 설명한 뒤,
사용자가 선택한 방향으로만 진행한다.

적용 대상 예시:
- 기존 Streamlit 앱에 통합할지, 별도 앱으로 분리할지
- single-page vs multi-page 구성
- 전략 선택 방식
- preset 중심 UI vs 자유 입력 중심 UI
- 결과 화면 레이아웃

즉 Phase 4의 핵심 원칙은:
**구현은 빠르게 하되, 선택은 반드시 사용자와 합의 후 진행한다.**

---

## Phase 4의 큰 작업 축

1. UI 구조 결정
2. runtime wrapper 구현
3. result bundle builder 구현
4. 전략 실행 화면 구현
5. 결과 표시 화면 구현
6. 향후 factor / fundamental 전략 확장 여지 정리

---

## Phase 4-1. UI Structure Decision

### 목표
- 백테스트 UI를 어디에 어떻게 붙일지 결정한다

### 대표 선택지
- 기존 `app/web/streamlit_app.py`에 통합
- 별도 backtest Streamlit app 분리
- multipage 구조로 재편

### 산출물
- 구조 결정 문서
- 선택 근거
- 첫 UI 골격 방향

현재 결정:
- 메인 앱은 `app/web/streamlit_app.py`로 유지
- 수집/백테스트는 탭으로 분리
- 내부 코드는 탭별/속성별 모듈로 분리하는 방향으로 진행

---

## Phase 4-2. Runtime Wrapper Implementation

### 목표
- UI가 직접 호출할 DB-backed runtime wrapper 구현

### 초기 대상
- `run_equal_weight_backtest_from_db(...)`
- `run_gtaa_backtest_from_db(...)`
- `run_risk_parity_trend_backtest_from_db(...)`
- `run_dual_momentum_backtest_from_db(...)`

### 산출물
- wrapper 코드
- 최소 실행 검증

현재 상태:
- `run_equal_weight_backtest_from_db(...)` first public wrapper 구현 완료
- 공통 `build_backtest_result_bundle(...)` 초안 구현 완료
- `run_gtaa_backtest_from_db(...)` second public wrapper 구현 완료
- `run_risk_parity_trend_backtest_from_db(...)` third public wrapper 구현 완료
- `run_dual_momentum_backtest_from_db(...)` fourth public wrapper 구현 완료

---

## Phase 4-3. Result Bundle Builder

### 목표
- UI가 공통으로 사용할 결과 bundle 생성기 구현

### 기준 구조
- `strategy_name`
- `result_df`
- `summary_df`
- `chart_df`
- `meta`

### 산출물
- bundle helper 코드
- 전략 wrapper와 연결

---

## Phase 4-4. First Strategy Execution UI

### 목표
- 사용자가 최소 입력으로 price-only 전략을 실행하게 한다

### 최소 입력 기준
- strategy
- universe mode
- tickers or preset
- start date
- end date

### 산출물
- 실행 form
- 실행 버튼
- 에러/빈 결과 처리

현재 상태:
- `Equal Weight` first-pass form 구현 완료
- 현재 form은 실제 `run_equal_weight_backtest_from_db(...)` 실행까지 연결됨
- first-pass 결과 표시는 summary + line chart + result preview 수준으로 열려 있음
- 입력 오류 / 데이터 부재 / 일반 실행 오류도 first-pass 수준으로 구분된다
- `GTAA` 전략 선택과 실행 form도 추가되어, 현재는 두 개의 공개 price-only 전략을 UI에서 전환 실행할 수 있다
- GTAA form의 `Signal Interval (months)`도 advanced input으로 노출되어,
  기존 고정 `2개월` cadence를 사용자 입력으로 조정할 수 있다
- `Risk Parity Trend` 전략 선택과 실행 form도 추가되어, 현재는 세 개의 공개 price-only 전략을 UI에서 전환 실행할 수 있다
- `Dual Momentum` 전략 선택과 실행 form도 추가되어, 현재는 네 개의 공개 price-only 전략을 UI에서 전환 실행할 수 있다
- 다음 단계는 history / visualization / execution history 강화 중에서 사용자 선택 후 진행하는 것이 맞다

---

## Phase 4-5. Result Presentation UI

### 목표
- 단일 전략 결과를 바로 읽기 좋게 보여준다

### 최소 표시 항목
- 성과 요약 표
- equity curve
- 상세 결과 표
- 실행 메타데이터

### 산출물
- 결과 레이아웃
- chart / table 연결

현재 상태:
- KPI metric row 연결 완료
- `Summary / Equity Curve / Result Table / Meta` 탭 구성 완료
- first-pass 결과 레이아웃은 product-like read path를 확보한 상태
- `Compare & Portfolio Builder` first-pass가 추가되어,
  - 최대 4개 전략 summary comparison
  - equity overlay
  - drawdown overlay
  - weighted portfolio builder
  까지 열린 상태
- compare mode에서도 전략별 advanced override가 열려 있어,
  첫 price-only 4개 전략의 핵심 cadence/selection 파라미터를 비교 실행 중 조정할 수 있다
- 백테스트 실행 이력도 `.note/finance/BACKTEST_RUN_HISTORY.jsonl` 기준으로
  first-pass 수준에서 영속 저장되며,
  `Compare & Portfolio Builder` 하단에서 최근 이력을 다시 확인할 수 있다
- 이어서 history는 한 단계 더 강화되어,
  - run kind filter
  - 검색
  - selected record drilldown
  까지 지원하게 되었다
- 그리고 다음 단계에서
  - recorded date range filter
  - metric sort
  - single-strategy `Run Again`
  까지 지원하게 되었다
- 이어서 history는 third-pass 수준으로 더 강화되어,
  - metric threshold filter
  - single-strategy `Load Into Form`
  - stored input의 current form prefill
  까지 지원하게 되었다
- compare / weighted rerun은 replay fidelity를 보장하기 전까지 intentionally deferred 상태로 유지한다
- 시각화도 한 단계 더 강화되어,
  - single strategy: `High / Low / End` marker, `Best / Worst Period` marker, top/bottom period table
  - compare: `Total Return` overlay + focused strategy drilldown
    + overlay end marker
    + strategy highlight table
  - weighted portfolio: single-strategy와 같은 marker / balance-extremes / period-extremes read path
    + strategy contribution amount/share view
  까지 확인할 수 있는 상태가 되었다

---

## Phase 4-6. Future Expansion Boundary

### 목표
- factor / fundamental 전략 UI 확장 경계를 정리한다

### 핵심 확인 항목
- strict PIT snapshot mode
- rebalance frequency
- factor selection / ranking inputs
- multi-strategy comparison path

### 산출물
- 후속 확장 메모
- Phase 5와의 연결 정리

현재 다음 활성 챕터:
- `factor / fundamental 전략 진입 준비`

현재 권장 순서:
1. 첫 factor / fundamental 전략 후보 선택
2. snapshot-first runtime wrapper 경계 정리
3. `snapshot_mode` 기본값 결정
4. 첫 UI 입력 세트 초안
5. 선택된 전략 기준 구현 범위 확정

현재 상태 업데이트:
- 첫 factor / fundamental 전략 방향은 `Quality Snapshot Strategy`
- first public mode는 `broad_research`
- broad-research first-pass runtime wrapper와 DB-backed sample entrypoint까지 구현 완료
- Quality Snapshot Strategy는 이제 Backtest UI의 다섯 번째 공개 전략으로 연결되었고,
  history / form prefill / compare first-pass 경로에도 반영되었다
- 추가로 sample-universe 기준 strict annual statement snapshot을 직접 사용하는
  `statement-driven quality prototype`도 backend/runtime 수준에서 first-pass 구현 및 검증되었다
- 이어서 이 prototype의 preprocessing은
  `strict statement snapshot -> normalized fundamentals -> quality factor snapshot`
  형태의 reusable data-layer mapping으로 정리되었다
- 그리고 broad public tables를 보존하기 위해
  `nyse_fundamentals_statement`, `nyse_factors_statement`
  shadow table first-pass도 실제 code path와 sample-universe validation까지 열렸다
- 이후 annual period-limit semantics fix와 canonical refresh를 통해
  sample-universe annual strict coverage가 `2011~2025` 수준까지 확장되었고,
  strict annual quality path는 이제 `Quality Snapshot (Strict Annual)` 이름으로
  Backtest UI의 public candidate 전략까지 올라왔다
- 그리고 wider-universe annual coverage 실행을 준비하기 위해,
  `Extended Statement Refresh`와 manual statement ingestion은
  large run에서 live statement-ingestion progress를 보여주도록 보강되었다
- 또한 first staged annual coverage run으로
  `Profile Filtered Stocks` top-100 market-cap seed를 실제 실행했고,
  annual strict coverage가 `80/100` symbols 수준으로 확인되었다
- 이후 stage 2에서는
  `United States` issuer top-300 annual run까지 진행했고,
  strict annual coverage가 `297/300` symbols 수준으로 확인되었다
- 그 결과 strict annual quality의 public 역할도 다시 정리되었다.
  - single-strategy 기본 preset:
    - `US Statement Coverage 300`
  - compare default preset:
    - `US Statement Coverage 100`
  - broad quality의 `Big Tech Quality Trial`과는 별도 역할로 분리
- 다음 선택은
  broad quality와 strict annual quality의 공존 원칙을 더 정리할지,
  shadow coverage를 더 넓힐지, valuation 보강을 할지,
  아니면 strict statement quality를 public 후보로 더 키울지
  쪽으로 넘어가는 것이 자연스럽다

---

## Phase 4 진입 전 이미 준비된 것

Phase 3에서 이미 고정된 것:

- UI가 직접 호출할 최소 runtime function 방향
- first-pass user-facing input set
- first-pass result bundle 구조
- DB-backed price-only 전략 검증 경로

즉 Phase 4는 완전한 탐색 단계가 아니라,
이미 정리된 handoff 규칙 위에서 UI를 구현하는 단계다.

---

## 결론

Phase 4는
“백테스트가 가능한가?”를 넘어서
“사용자가 실제로 그 경로를 UI에서 사용할 수 있는가?”를 만드는 단계다.

따라서 이 단계에서는
속도만큼이나
선택의 합의와 문서화가 중요하다.
