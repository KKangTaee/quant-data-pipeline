# Quant Data Pipeline

DB-backed market data ingestion, factor generation, and strategy backtesting workspace for quant research and operator review.

이 저장소의 현재 중심은 `finance` 패키지입니다.  
주요 목표는 아래 두 가지입니다.

- 데이터 수집과 정규화
- 전략 백테스트와 실전형 해석

`financial_advisor` 디렉터리는 저장소 안에 남아 있지만, 현재 활성 개발 범위의 중심은 아닙니다.

## 현재 제품 표면

현재 메인 진입점은 Streamlit 기반 `Finance Console`입니다.

- `Overview`
  - 후보 Top 3, candidate funnel, next actions, recent activity, system snapshot dashboard
- `Ingestion`
  - 일별 업데이트, statement refresh, 진단 작업
- `Backtest`
  - `Backtest Analysis -> Practical Validation -> Final Review` 3단계로 후보 source 생성, 실전 검증, 최종 판단 기록을 처리
- `Ops Review`
  - Operations Dashboard 형태의 triage flow, run health, action inbox, failure artifact, logs, system snapshot 점검
- `Selected Portfolio Dashboard`
  - Final Review에서 선정된 포트폴리오를 최신 날짜 범위로 다시 계산하고, 가상 투자금 기준 성과 / benchmark spread / component contribution / Allocation drift를 read-only 운영 화면으로 확인
- `Backtest Run History`
  - 저장된 백테스트 실행 기록 검토, form 복원, 재실행, candidate review 초안 전달
- `Guides`
  - 현재 phase 문서, 체크리스트, 승격 해석 가이드, 단계형 운영 흐름 안내
- `Glossary`
  - 퀀트/백테스트/real-money 관련 용어를 검색하며 확인하는 reference 페이지

## 현재 구현 범위

### Data / Ingestion

- OHLCV 수집 및 DB 적재
- fundamentals / financial statements 수집
- asset profile / ETF 운용 가능성 관련 메타데이터 수집
- factor 계산 파이프라인
- 진단 작업
  - stale price
  - statement coverage
  - source payload inspection

### Backtest / Research

- ETF 전략
  - `Equal Weight`
  - `GTAA`
  - `Global Relative Strength`
  - `Risk Parity Trend`
  - `Dual Momentum`
- Strict annual factor family
  - `Quality`
  - `Value`
  - `Quality + Value`
  - strict annual trend overlay는 now optional `partial cash retention`을 받아,
    일부 추세 탈락 슬롯을 survivor reweighting 대신 현금으로 남기는 구조 실험이 가능
  - strict annual full risk-off는 now optional `defensive sleeve risk-off`를 받아,
    `BIL / SHY / LQD` 같은 방어 sleeve로 회전하는 구조 실험이 가능
  - strict annual weighting은 now optional `concentration-aware weighting`을 받아,
    pure equal-weight 대신 mild `rank-tapered` top-N 배분을 실험할 수 있음
- 실전형 해석 surface
  - `Promotion`
  - `Shortlist`
  - `Probation`
  - `Monitoring`
  - `Deployment Readiness`
  - `Validation / Rolling / Out-of-Sample Review`
- persistent backtest history
  - 실행 입력/요약뿐 아니라 `gate snapshot`도 함께 저장하는 history v2
  - 이후 blocker audit, candidate review, rerun drilldown에 활용
  - `Operations > Backtest Run History`에서 운영 기록처럼 확인하고, 필요 시 Backtest 흐름으로 다시 보냄
- Clean V2 portfolio selection workflow
  - `Backtest > Backtest Analysis`에서 Single Strategy / Compare / 저장 Mix replay를 실행하고 실전 검증 후보 source를 선택하는 흐름
  - `.note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl`에 선택한 후보 source를 append-only로 저장하는 흐름
  - `Backtest > Practical Validation`에서 선택 source의 component, weight, Data Trust, Real-Money signal, paper observation 기준을 구조화하는 흐름
  - `.note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl`에 검증 결과를 저장하되, 사용자 최종 메모는 Final Review에만 남기는 흐름
  - `Backtest > Final Review`에서 Practical Validation 결과를 기준으로 최종 선정 / 보류 / 거절 / 재검토 판단을 한 번만 기록하는 흐름
  - `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`이 새 selected dashboard의 source-of-truth가 되는 흐름
  - 기존 Candidate Review / Portfolio Proposal / Pre-Live JSONL은 legacy / archive compatibility 경로로 유지하고 새 workflow의 필수 join 조건으로 쓰지 않는 흐름
- selected portfolio operations dashboard
  - `Operations > Selected Portfolio Dashboard`에서 Final Review의 `SELECT_FOR_PRACTICAL_PORTFOLIO` row만 운영 대상으로 확인하는 흐름
  - `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`을 read-only로 읽는 흐름
  - selected component의 저장 contract를 사용자가 지정한 시작일 / 종료일 / 가상 투자금으로 다시 실행해 최신 기간 성과를 확인하는 흐름
  - portfolio value, total return, CAGR, MDD, benchmark spread, component contribution, strongest / weakest periods를 확인하는 흐름
  - target allocation, benchmark, evidence, operator next action, current weight / current value / shares x price 기반 Allocation Check, disabled live approval / order boundary를 확인하는 흐름
  - shares x price 입력에서는 DB latest close를 보조로 불러올 수 있지만, 실제 account holding 연결이나 주문 생성은 하지 않는 흐름

## 프로젝트 구조

```text
app/
  jobs/                  # ingestion jobs, diagnostics, run history
  web/
    streamlit_app.py     # Finance Console entry point
    overview_dashboard.py # Workspace > Overview dashboard UI
    overview_dashboard_helpers.py # Overview 후보/Pre-Live/Proposal/History 집계 helper
    backtest_analysis.py # Backtest Analysis 3단계 wrapper
    backtest_practical_validation.py # Practical Validation UI
    backtest_practical_validation_helpers.py # Clean V2 source / validation helper
    backtest_workflow_routes.py # Backtest 3단계 route mapping
    backtest_history.py  # Operations > Backtest Run History UI
    backtest_candidate_library.py # Operations > Candidate Library UI
    backtest_candidate_library_helpers.py # 저장 후보 목록 / replay payload / 후보 replay helper
    final_selected_portfolio_dashboard.py # Operations > Selected Portfolio Dashboard UI
    final_selected_portfolio_dashboard_helpers.py # 선정 포트폴리오 table / evidence / allocation input helper
    backtest_ui_components.py # Backtest 공용 status/route UI component
    backtest_candidate_review.py # Candidate Review / Candidate Packaging / Pre-Live 운영 기록 UI
    backtest_candidate_review_helpers.py # Candidate Review 판단/변환/Pre-Live 운영 기록 helper
    backtest_portfolio_proposal.py # Portfolio Proposal 작성 / 저장 / proposal feedback UI
    backtest_portfolio_proposal_helpers.py # Portfolio Proposal 저장/검증/feedback helper
    backtest_final_review.py # Final Review / 검증 근거 / 최종 판단 기록 UI
    backtest_final_review_helpers.py # Final Review source/evidence/decision helper
    pages/backtest.py    # Backtest shell, workflow navigation
    runtime/             # UI-facing runtime wrappers
      candidate_registry.py
      portfolio_proposal.py
      paper_portfolio_ledger.py
      final_selection_decisions.py
      portfolio_selection_v2.py
      final_selected_portfolios.py
finance/
  data/                  # ingestion, DB schema, loaders, factors
  strategy.py            # strategy simulation logic
  transform.py           # reusable preprocessing
  engine.py              # orchestration
  performance.py         # performance summaries
.note/finance/
  FINANCE_COMPREHENSIVE_ANALYSIS.md
  MASTER_PHASE_ROADMAP.md
  WORK_PROGRESS.md
  QUESTION_AND_ANALYSIS_LOG.md
  FINANCE_TERM_GLOSSARY.md
  backtest_reports/
```

## 빠른 시작

### 1. 환경 준비

이 프로젝트는 Python `3.12+` 기준입니다.

```bash
uv sync
```

또는 기존 가상환경이 이미 있다면 그대로 사용해도 됩니다.

### 2. 콘솔 실행

```bash
.venv/bin/streamlit run app/web/streamlit_app.py
```

앱이 열리면 상단 navigation에서 `Overview`, `Ingestion`, `Backtest`, `Ops Review`, `Selected Portfolio Dashboard`, `Backtest Run History`, `Candidate Library`, `Guides`, `Glossary`를 이동하며 사용합니다.

## 참고 문서

가장 먼저 보면 좋은 문서는 아래입니다.

- `.note/finance/FINANCE_COMPREHENSIVE_ANALYSIS.md`
  - 현재 finance 구조와 runtime/data/strategy 흐름 종합 문서
- `.note/finance/MASTER_PHASE_ROADMAP.md`
  - 전체 phase 흐름과 현재 위치
- `.note/finance/FINANCE_DOC_INDEX.md`
  - finance 문서 인덱스
- `.note/finance/FINANCE_TERM_GLOSSARY.md`
  - 반복 용어 사전
- `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`
  - 결과 중심 백테스트 리포트 인덱스

## 개발 원칙

- Point-in-time correctness를 항상 우선합니다.
- Look-ahead bias와 survivorship bias를 명시적으로 경계합니다.
- 전략 추가 시에는 가능하면:
  - `finance/transform.py`에 전처리
  - `finance/strategy.py`에 시뮬레이션
  - `finance/engine.py`에 orchestration
  구조를 유지합니다.
- generated artifact, run history, temp CSV, notebook scratch 파일은 기본적으로 커밋하지 않습니다.

## 현재 상태에 대한 메모

이 저장소는 “백테스트가 되는 연구 코드”를 넘어서,  
실전형 승격과 운영 준비도를 함께 읽는 쪽으로 계속 발전 중입니다.

즉 지금의 핵심은:

- 좋은 전략을 찾는 것
- 그 전략이 실전형 후보인지 구분하는 것
- operator가 그 상태를 UI에서 바로 해석할 수 있게 만드는 것

입니다.
