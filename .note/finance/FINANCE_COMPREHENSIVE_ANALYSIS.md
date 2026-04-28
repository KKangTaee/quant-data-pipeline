# Finance Comprehensive Analysis

## 문서 목적
이 문서는 `finance` 패키지의 구현 히스토리, 구조 정보,
DB / strategy / runtime / UI 연결을 한 번에 확인하기 위한 상세 분석 문서다.

단순한 사용자 매뉴얼은 아니다.
다만 사용자가 프로젝트의 현재 구조를 따라올 수 있도록,
이제는 아래 세 가지 역할을 함께 갖는다.

1. 사람도 읽을 수 있는 현재 시스템 구조 지도
2. agent가 깊게 분석할 때 쓰는 상세 기술 reference
3. 과거 구현 판단과 현재 구현 상태를 함께 추적하는 durable context

- `finance/docs/FINANCE_PACKAGE_ANALYSIS.md`
- `finance/docs/FINANCE_DB_DATA_AUDIT.md`
- 현재 워크스페이스의 실제 코드

이 문서는 이후 대화에서 `finance` 패키지의 현재 상태를 이해하는 기준 문서로 사용하기 위한 것이다.

- 범위 포함: `finance` 패키지 전체
- 범위 제외: `financial_advisor`
- 최초 기준 시점: 2026-03-11
- 최근 동기화 기준: 2026-04-28 / Phase 30 paper tracking feedback implementation complete

---

## 빠른 읽기

처음 이 문서를 읽는다면 처음부터 끝까지 정독하지 않아도 된다.
목적에 따라 아래 순서로 읽는 것이 좋다.

| 목적 | 먼저 볼 섹션 |
|---|---|
| 현재 finance 시스템이 무엇인지 빠르게 알고 싶을 때 | `현재 시스템 한 장 요약`, `1. 전체 요약`, `3-1. 현재 시스템 구조` |
| 데이터 수집 / DB 구조를 보고 싶을 때 | `5. 현재 데이터 흐름`, `6. DB 구조 요약`, `7. 테이블별 역할과 데이터 성격` |
| 백테스트 / 전략 구조를 보고 싶을 때 | `3-1. 현재 시스템 구조`, `8. 현재 제품 / 전략 레이어의 성격`, `12. 핵심 코드 진입점과 상세 문서 위치` |
| Streamlit UI / runtime 연결을 보고 싶을 때 | `3-1. 현재 시스템 구조`, `4-1. 핵심 실행 계층`, `12. 핵심 코드 진입점과 상세 문서 위치` |
| 현재 한계와 다음 우선순위를 보고 싶을 때 | `10. 현재 남은 한계와 주의 경계`, `14. 다음 개발 우선순위` |
| agent가 작업 전 깊은 맥락을 확인할 때 | 전체 문서 + `FINANCE_DOC_INDEX.md`, `WORK_PROGRESS.md`, `QUESTION_AND_ANALYSIS_LOG.md` |

이 문서는 의도적으로 많은 정보를 보존한다.
대신 자세한 phase 문서나 backtest report를 찾을 때는 이 문서가 아니라
`.note/finance/FINANCE_DOC_INDEX.md`와
`.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`를 먼저 본다.

---

## 현재 시스템 한 장 요약

현재 `finance`는 크게 여섯 개 층으로 읽는 것이 가장 쉽다.

| 층 | 역할 | 대표 위치 |
|---|---|---|
| Data Collection | 가격, ETF/주식 universe, profile, fundamentals, statements를 수집한다 | `finance/data/*` |
| Persistence | 수집한 데이터를 MySQL 테이블에 저장한다 | `finance/data/db/*` |
| Loader / Runtime Read Path | DB 데이터를 백테스트용 입력으로 꺼낸다 | `finance/loaders/*`, `finance/sample.py` |
| Strategy / Backtest Engine | 전략을 계산하고 result dataframe을 만든다 | `finance/strategy.py`, `finance/engine.py`, `finance/transform.py` |
| Web Runtime / UI | Streamlit에서 single / compare / candidate review / history / saved replay / Pre-Live Review / Portfolio Proposal을 실행한다 | `app/web/runtime/*`, `app/web/pages/backtest.py` |
| Review / Proposal / Pre-Live | 결과를 진단하고 candidate note / registry / proposal draft / paper / watchlist / hold / re-review로 관리한다 | Real-Money surface, Phase 25 / Phase 29 / Phase 30 문서 |

중요한 경계:

- 이 프로젝트의 최종 목표는 `데이터 수집 + 백테스트 제품 개발`을 기반으로 투자 후보와 포트폴리오 구성을 제안하는 프로그램을 만드는 것이다.
- 다만 현재 phase에서 나온 강한 백테스트 결과가 곧바로 최종 투자 추천이나 live trading 승인을 뜻하지는 않는다.
- `Real-Money 검증 신호`는 개별 백테스트 결과에 붙는 진단표다.
- `Pre-Live 운영 점검`은 그 진단표를 보고 다음 행동을 기록하는 운영 절차다.
- 실제 투자 분석은 사용자가 명시적으로 요청했을 때 별도 분석으로 수행한다.

---

## 이 문서의 읽기 기준

본문에는 초기 구조 분석, 중간 phase에서 추가된 구현 기록,
최근 Phase 25 기준의 운영 개념이 함께 들어 있다.

따라서 아래 기준으로 읽는다.

- 이 문서는 `finance` 시스템의 high-level current-state map이다.
- 모든 구현 기록을 계속 쌓는 문서가 아니라, 현재 큰 구조를 이해하기 위한 지도다.
- 현재 상태를 확인할 때는 최신 roadmap / work log와 함께 본다.
- 구체적인 phase 문서는 `FINANCE_DOC_INDEX.md`에서 찾는다.
- 반복 용어는 `FINANCE_TERM_GLOSSARY.md`에서 확인한다.
- 자동 생성 실행 기록은 이 문서가 아니라 run history JSONL 또는 Backtest UI history에서 확인한다.
- 일회성 backtest 결과, phase 진행 상태, 상세 call flow, table별 상세 의미는 이 문서에 길게 추가하지 않는다.
- 현재 시스템의 큰 그림이 바뀌었을 때만 관련 섹션을 짧게 갱신한다.

---

## 1. 전체 요약

현재 `finance` 패키지는 하나의 단일 라이브러리라기보다
아래 두 축이 함께 들어 있는 확장형 퀀트 리서치 / 백테스트 시스템에 가깝다.

1. 데이터 인프라 축
   - NYSE 유니버스 수집
   - 자산 메타데이터 수집
   - 가격/재무/팩터 DB 적재
   - 상세 재무제표 라벨/값 수집
2. 전략 리서치 축
   - 시계열 전처리
   - 전략 시뮬레이션
   - 성과 분석 및 시각화

즉, 이 패키지는 "데이터 수집기"와 "백테스트 프레임워크"가 같은 패키지 안에 공존하는 구조다.

---

## 2. 기존 문서와 이번 종합 문서의 관계

### `FINANCE_PACKAGE_ANALYSIS.md`가 다루는 것
- 패키지 레이어 구조
- 각 스크립트의 역할
- 전략/엔진/변환 흐름

### `FINANCE_DB_DATA_AUDIT.md`가 다루는 것
- 어떤 DB와 테이블이 생성되는지
- 어떤 데이터가 실제로 수집/적재되는지
- 퀀트 관점에서 어떤 데이터가 추가로 필요한지

### 이번 문서가 추가로 다루는 것
- 코드 기준으로 재검증한 실제 구조
- 패키지의 중심 인터페이스와 실행 순서
- 데이터 흐름과 DB 흐름의 연결 구조
- 현재 설계의 강점, 리스크, 구조적 갭
- 현재 남은 한계와 다음 개발 우선순위

---

## 3. 현재 시스템 구조와 phase별 구현 히스토리

이 섹션은 두 가지를 분리해서 읽는다.

1. 현재 시스템 구조
   - 지금 코드가 어떤 층으로 나뉘어 작동하는지 설명한다.
2. phase별 구현 히스토리
   - 그 구조가 어떤 phase를 거치며 만들어졌는지 설명한다.

기존에는 이 둘이 한 흐름에 섞여 있어,
현재 UI 구조를 설명하다가 Phase 14, Phase 24, Phase 25 이야기가 갑자기 이어지는 문제가 있었다.
이제는 먼저 현재 구조를 보고, 그 다음 phase별 히스토리를 보는 방식으로 읽는다.

### 3-1. 현재 시스템 구조

현재 구조를 가장 자연스럽게 표현하면 아래와 같다.

```text
외부 데이터 소스
  - yfinance
  - NYSE 웹페이지
  - EDGAR

      |
      v

Data Collection / Persistence
  - finance/data/*
  - finance/data/db/*
  - MySQL

      |
      v

Loader / Runtime Read Path
  - finance/loaders/*
  - finance/sample.py
  - app/web/runtime/*

      |
      v

Research / Backtest Processing
  - finance/transform.py
  - finance/engine.py
  - finance/strategy.py

      |
      v

Web Product Surface
  - app/web/pages/backtest.py
  - single strategy
  - compare
  - history
  - saved portfolio replay
  - candidate review
  - pre-live review
  - portfolio proposal

      |
      v

Analysis / Review / Proposal / Pre-Live
  - finance/performance.py
  - result bundle / summary
  - Real-Money 검증 신호
  - Portfolio Proposal 초안
  - Pre-Live 운영 점검
```

현재 시스템은 단순히 `finance.strategy`만 호출하는 구조가 아니다.
DB에 쌓인 데이터를 runtime wrapper가 읽고,
web UI가 그 wrapper의 result bundle을 받아 single / compare / history / saved replay에 연결하는 구조다.

핵심 경계는 아래와 같다.

| 영역 | 현재 역할 |
|---|---|
| Data Collection | 외부 데이터 수집과 원천 데이터 보강 |
| Persistence | MySQL 기반 저장과 재사용 가능한 DB table 유지 |
| Loader / Runtime | DB 데이터를 백테스트 입력으로 변환하고 web runtime에 전달 |
| Strategy / Engine | 전략 계산, 리밸런싱, 포트폴리오 시뮬레이션 |
| Web Product Surface | 사용자가 전략 실행, 비교, 저장, 재실행, 후보 검토, proposal 초안 작성을 수행하는 UI |
| Review / Proposal / Pre-Live | 결과 해석, Real-Money 진단, proposal draft, paper / watchlist / hold 운영 준비 |

현재 구현을 읽을 때 가장 중요한 점은:

- DB 적재 경로와 백테스트 실행 경로는 이제 연결되어 있지만, 모든 데이터/전략이 같은 완성도는 아니다.
- annual strict 계열은 가장 성숙한 경로다.
- quarterly 계열은 Phase 23에서 제품 실행 경로가 크게 보강되었지만, real-money / guardrail parity는 아직 후속 과제다.
- `Global Relative Strength`는 Phase 24에서 새 전략 추가 경로를 검증하기 위해 붙인 첫 신규 전략이다.
- Phase 25는 live trading이 아니라, Real-Money 진단 이후의 Pre-Live 운영 기록을 준비하고 저장하는 단계를 완성했다.

### 3-2. Phase별 구현 히스토리

아래는 현재 구조가 생긴 큰 흐름이다.
세부 문서는 `.note/finance/FINANCE_DOC_INDEX.md`에서 phase별로 찾는다.

| Phase 구간 | 무엇이 만들어졌나 | 현재 의미 |
|---|---|---|
| Phase 1~3 | 내부 web app 범위, PIT guideline, DB-backed loader/runtime foundation | 데이터 수집과 DB-backed 백테스트의 기반 |
| Phase 4~5 | Backtest UI, 초기 strategy library, compare / weighted portfolio, risk overlay | 사용자가 화면에서 전략을 실행하고 비교하는 초기 제품 surface |
| Phase 6~8 | market regime overlay, quarterly strict family, statement coverage / shadow rebuild tooling | annual 중심에서 quarterly / statement-driven 경로로 확장 |
| Phase 9~12 | strict coverage policy, dynamic PIT universe, saved portfolio, real-money promotion surface | 후보 검증과 실전형 진단 surface의 초석 |
| Phase 13~15 | deployment readiness, probation, gate calibration, candidate quality improvement | 후보를 유지 / 보류 / 재검토하는 정책과 분석 흐름 |
| Phase 16~18 | downside refinement, partial cash retention, defensive sleeve, concentration-aware weighting, next-ranked fill | strict annual downside와 구조적 처리 규칙 개선 |
| Phase 19~20 | structural contract language, current candidate re-entry, compare / weighted / saved workflow hardening | operator가 UI에서 설정과 후보를 다시 이해하고 재사용하는 흐름 |
| Phase 21~22 | integrated deep validation, portfolio bridge / portfolio workflow development validation | 후보와 portfolio workflow를 같은 frame에서 재검증 |
| Phase 23 | quarterly / alternate cadence productionization | quarterly prototype을 UI / payload / history / saved replay까지 제품 기능으로 보강 |
| Phase 24 | new strategy expansion bridge, `Global Relative Strength` 추가 | research note에서 finance strategy implementation으로 이어지는 첫 신규 전략 경로 |
| Phase 25 | Pre-Live operating system closeout | Real-Money 진단 이후 paper / watchlist / hold / re-review 운영 기록 체계를 구현하고 사용자 QA 완료 |
| Phase 26 | Foundation stabilization / backlog rebase | 과거 pending phase와 foundation gap을 현재 제품 기준으로 재분류하고 사용자 QA 완료 |
| Phase 27 | Data integrity / backtest trust layer | 백테스트 결과의 데이터 가능 범위, stale / missing / malformed price, common-date truncation을 먼저 보이게 만들고 사용자 QA 완료 |
| Phase 28 | Strategy family parity / cadence completion | 전략 family별 지원 범위, history / saved replay, compare data trust, Real-Money / Guardrail scope를 화면에서 구분하고 사용자 QA 완료 |
| Phase 29 | Candidate review / recommendation workflow | Candidate Review board, result-to-draft handoff, review note, registry draft workflow를 구현하고 사용자 QA 완료 |
| Phase 30 | Product-flow / proposal draft / monitoring review / pre-live feedback / paper tracking feedback / helper split | Phase 29 이후 사용 흐름, `backtest.py` 점진 리팩토링 경계, proposal row 계약, registry I/O helper 경계, Portfolio Proposal Draft UI / persistence, Monitoring Review, Pre-Live Feedback, Paper Tracking Feedback을 구현하고 manual QA 대기 중 |

이 히스토리는 투자 성과 순위표가 아니다.
각 phase가 제품 기능, 검증 흐름, operator workflow를 어떤 방향으로 확장했는지 보는 지도다.

### 3-3. Legacy 상세 구현 메모 보관 위치

예전에는 이 문서 안에 긴 `3-3. 상세 구현 메모`가 직접 들어 있었다.
하지만 `FINANCE_COMPREHENSIVE_ANALYSIS.md`를 high-level current-state map으로 관리하기로 했기 때문에,
긴 legacy 구현 메모는 아래 archive 문서로 분리했다.

- Archive: `.note/finance/archive/FINANCE_COMPREHENSIVE_ANALYSIS_LEGACY_IMPLEMENTATION_NOTES_20260420.md`

앞으로 기록 위치는 다음 기준을 따른다.

- 현재 시스템의 큰 구조가 바뀌면 이 문서의 관련 섹션을 짧게 갱신한다.
- phase 진행 상황은 해당 `phase*/` 문서와 `WORK_PROGRESS.md`에 남긴다.
- 설계 판단과 사용자 질문의 durable conclusion은 `QUESTION_AND_ANALYSIS_LOG.md`에 남긴다.
- 상세 code flow는 `code_analysis/`에 남긴다.
- DB / data / PIT / stale data 의미는 `data_architecture/`에 남긴다.
- backtest 결과와 후보 비교는 `backtest_reports/`와 strategy별 backtest log에 남긴다.

## 4. 상위 디렉터리 기준 파일 역할

이 섹션은 `finance` 패키지의 큰 파일 역할을 설명하는 요약이다.
실제 코드 수정 순서, runtime 연결, UI replay, 새 전략 추가 절차처럼
개발자가 따라야 하는 상세 흐름은 `.note/finance/code_analysis/`에서 관리한다.

현재 코드 분석 문서는 다음을 우선해서 본다.

- `.note/finance/code_analysis/BACKTEST_RUNTIME_FLOW.md`
- `.note/finance/code_analysis/DATA_DB_PIPELINE_FLOW.md`
- `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
- `.note/finance/code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md`
- `.note/finance/code_analysis/AUTOMATION_SCRIPTS_GUIDE.md`

## 4-1. 핵심 코드 계층 요약

| 계층 | 대표 파일 | 한 줄 역할 |
|---|---|---|
| Web entry | `app/web/streamlit_app.py` | Finance Console navigation entry |
| Backtest UI | `app/web/pages/backtest.py` | Single / Compare / Candidate Review / History / Saved Portfolio / Pre-Live Review / Portfolio Proposal 화면 |
| Web runtime | `app/web/runtime/backtest.py` | UI payload를 DB-backed backtest 실행으로 변환 |
| Candidate registry runtime | `app/web/runtime/candidate_registry.py` | current candidate / candidate review note / pre-live registry JSONL read / append helper |
| Portfolio proposal runtime | `app/web/runtime/portfolio_proposal.py` | portfolio proposal draft JSONL read / append helper |
| Loader | `finance/loaders/*` | DB read path와 PIT snapshot 조회 |
| Engine / transform | `finance/engine.py`, `finance/transform.py` | price strategy orchestration과 전처리 |
| Strategy | `finance/strategy.py` | 실제 strategy simulation |
| Performance | `finance/performance.py` | 성과 요약과 weighted portfolio 계산 |
| Data collection | `finance/data/*` | 가격, 유니버스, 프로파일, 재무, 팩터 수집 / 저장 |
| DB schema | `finance/data/db/schema.py` | finance DB table schema 기준 |

## 4-2. 여기서 남기는 기준

이 문서에는 각 파일의 큰 역할만 남긴다.
다음과 같은 상세 흐름은 `code_analysis/`를 우선한다.

- backtest runtime call flow: `.note/finance/code_analysis/BACKTEST_RUNTIME_FLOW.md`
- data / DB / loader flow: `.note/finance/code_analysis/DATA_DB_PIPELINE_FLOW.md`
- Backtest UI / history / replay flow: `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
- strategy 추가 / 변경 flow: `.note/finance/code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md`
- automation script 기준: `.note/finance/code_analysis/AUTOMATION_SCRIPTS_GUIDE.md`

## 4-3. 현재 구조를 읽을 때의 핵심

- `FINANCE_COMPREHENSIVE_ANALYSIS.md`는 전체 구조를 이해하는 지도다.
- 실제 코드 수정 순서와 상세 계약은 `code_analysis/`에서 관리한다.
- data source / DB table 의미는 이 문서의 `5~7` 섹션을 같이 본다.
- 전략 구현 세부와 UI replay 계약은 code analysis 문서와 phase 문서를 같이 본다.

---

## 5. 현재 데이터 흐름

이 섹션은 데이터 흐름의 큰 그림만 남긴다.
상세한 source -> table -> loader -> runtime 흐름은
`.note/finance/data_architecture/DATA_FLOW_MAP.md`에서 관리한다.

핵심 흐름은 네 가지다.

| 흐름 | 요약 | 상세 문서 |
|---|---|---|
| Universe | NYSE listing -> CSV -> `nyse_stock` / `nyse_etf` -> asset profile | `data_architecture/DATA_FLOW_MAP.md` |
| Price | yfinance -> direct research path 또는 `nyse_price_history` DB path | `data_architecture/DATA_FLOW_MAP.md` |
| Broad fundamentals / factors | yfinance statements -> `nyse_fundamentals` -> `nyse_factors` | `data_architecture/DATA_FLOW_MAP.md` |
| Statement-driven path | EDGAR / statement values -> fundamentals shadow -> factors shadow | `data_architecture/DATA_FLOW_MAP.md` |

현재 중요한 구분은 아래다.

- price는 direct-fetch 경로와 DB-backed 경로가 함께 존재한다.
- broad fundamentals / factors는 빠른 research convenience layer다.
- statement-driven shadow path는 strict annual / quarterly factor strategy에서 더 중요하다.
- detailed financial statements의 raw truth는 `nyse_financial_statement_values`를 중심으로 본다.

---

## 6. DB 구조 요약

이 섹션은 DB와 주요 table의 큰 목록만 남긴다.
상세 schema map과 table 성격은 아래 문서에서 관리한다.

- `.note/finance/data_architecture/DB_SCHEMA_MAP.md`
- `.note/finance/data_architecture/TABLE_SEMANTICS.md`

| DB | 주요 table | 역할 |
|---|---|---|
| `finance_meta` | `nyse_stock`, `nyse_etf`, `nyse_asset_profile` | universe / listing / profile metadata |
| `finance_price` | `nyse_price_history` | stock / ETF 공용 price ledger |
| `finance_fundamental` | `nyse_fundamentals`, `nyse_factors`, `nyse_fundamentals_statement`, `nyse_factors_statement`, statement filings / values / labels | fundamentals, factors, detailed statement data |

실제 schema definition은 `finance/data/db/schema.py`가 기준이다.
이 문서는 schema SQL을 복제하지 않고, 사람이 읽는 구조 요약만 유지한다.

---

## 7. 테이블별 역할과 데이터 성격

테이블별 상세 의미는 `.note/finance/data_architecture/TABLE_SEMANTICS.md`에서 관리한다.
여기서는 현재 시스템을 읽을 때 필요한 성격 구분만 남긴다.

| 성격 | 의미 | 대표 table |
|---|---|---|
| master | universe / symbol master | `nyse_stock`, `nyse_etf` |
| profile | current profile snapshot | `nyse_asset_profile` |
| raw ledger | raw source에 가까운 fact ledger | `nyse_price_history`, `nyse_financial_statement_values` |
| filing ledger | filing 단위 metadata | `nyse_financial_statement_filings` |
| broad summary | provider-normalized convenience summary | `nyse_fundamentals` |
| derived | 계산된 factor table | `nyse_factors` |
| shadow | statement raw ledger에서 재구성한 검증 / 전략용 layer | `nyse_fundamentals_statement`, `nyse_factors_statement` |
| convenience | UI / 해석 보조 layer | `nyse_financial_statement_labels` |

데이터 품질, PIT, survivorship, stale data 주의사항은
`.note/finance/data_architecture/DATA_QUALITY_AND_PIT_NOTES.md`를 우선한다.

---

## 8. 현재 제품 / 전략 레이어의 성격

현재 `finance`는 단순한 예제 전략 모음이 아니라,
DB-backed 데이터, 전략 실행, UI 실행, compare/history/replay, 후보 검토 문서가 연결된
퀀트 백테스트 제품으로 확장 중이다.

전략 레이어는 크게 네 축으로 본다.

| 축 | 현재 의미 | 상세 기준 |
|---|---|---|
| Price-only ETF family | `GTAA`, `Risk Parity Trend`, `Dual Momentum`, `Global Relative Strength` 같은 ETF / 자산배분 전략 | `code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md` |
| Factor / fundamental family | `Quality`, `Value`, `Quality + Value` strict annual / quarterly 계열 | `backtest_reports/strategies/` |
| Portfolio workflow | compare 결과를 weighted portfolio로 묶고 saved replay로 재현하는 workflow | `code_analysis/WEB_BACKTEST_UI_FLOW.md` |
| Review / Proposal / Pre-Live layer | Real-Money 진단 이후 candidate note / registry / proposal draft / paper / watchlist / hold / re-review를 기록하는 운영 준비 계층 | `phase25/`, `phase29/`, `phase30/` |

중요한 경계:

- 이 프로젝트의 장기 목표는 데이터와 백테스트 근거를 바탕으로 투자 후보와 포트폴리오 구성을 제안하는 프로그램을 만드는 것이다.
- 현재 phase 진행은 그 목표를 위한 개발 / 검증 단계이며, 강한 백테스트 결과를 최종 투자 추천으로 자동 해석하지 않는다.
- 사용자가 명시적으로 분석을 요청하면 분석을 수행하되, phase roadmap 자체가 투자 분석 중심으로 바뀐 것은 아니다.
- live trading / broker order automation은 현재 직접 범위 밖이다.

---

## 9. 현재 시스템의 강점

현재 강점은 개별 함수가 잘 나뉘어 있다는 수준을 넘어,
반복 가능한 research / backtest workflow가 점점 제품 형태로 연결되고 있다는 점이다.

| 강점 | 현재 의미 |
|---|---|
| DB-backed runtime | 가격, 재무, factor, statement data를 DB / loader / runtime으로 연결하는 기준 경로가 생겼다. |
| Backtest UI surface | Single Strategy, Compare, History, Saved Portfolio replay, Candidate Review, Pre-Live Review, Portfolio Proposal 흐름이 제품 화면에서 이어진다. |
| Result metadata | result table뿐 아니라 warnings, contract, coverage, selection history, interpretation, real-money signal을 같이 남긴다. |
| Strategy expansion path | `Global Relative Strength`를 통해 research note -> core strategy -> runtime -> UI / replay 연결 경로가 확인됐다. |
| Data architecture split | DB/table 의미와 PIT/data-quality 기준이 `data_architecture/`로 분리됐다. |
| Code flow split | 실제 코드 수정 흐름은 `code_analysis/`에서 따로 관리한다. |
| Phase / report 운영 | phase docs, backtest reports, strategy logs, candidate registry, hygiene helper가 반복 연구의 기록 체계를 만든다. |

즉 현재 프로젝트의 강점은
**데이터 수집, 전략 실행, UI 재현, 결과 해석, 문서 관리가 같은 workflow 안에서 이어진다**는 점이다.

---

## 10. 현재 남은 한계와 주의 경계

현재 한계는 “기본 제품 경로가 없다”가 아니라,
더 엄격한 데이터 검증과 운영 준비 단계로 가기 전에 남아 있는 경계다.

| 영역 | 현재 남은 한계 | 우선 참고 문서 |
|---|---|---|
| PIT / survivorship | filing-time point-in-time과 historical universe survivorship 제어는 아직 완전하지 않다. | `data_architecture/DATA_QUALITY_AND_PIT_NOTES.md` |
| Broad factor layer | `nyse_fundamentals`, `nyse_factors`는 broad research convenience layer이지 strict filing-time source가 아니다. | `data_architecture/TABLE_SEMANTICS.md` |
| Quarterly parity | quarterly strict lane은 제품 실행 경로가 보강됐지만 annual strict와 같은 real-money / guardrail parity는 아직 후속 과제다. | `phase23/` |
| Pre-Live persistence | Phase 25에서 후보 운영 기록소가 `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`로 분리되었고, `draft-from-current` helper와 `Backtest > Pre-Live Review` UI로 current candidate를 Pre-Live 운영 기록으로 저장할 수 있다. | `phase25/`, `operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md` |
| Portfolio proposal persistence / monitoring | Phase 30에서 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` 저장소와 `Backtest > Portfolio Proposal` UI가 추가되어 current candidate 여러 개를 proposal draft로 저장하고 Monitoring Review / Pre-Live Feedback / Paper Tracking Feedback에서 blocker, review gap, component table, 최신 Pre-Live 상태 차이, 최신 Pre-Live result snapshot의 CAGR / MDD 변화를 다시 볼 수 있다. 아직 optimizer, correlation / turnover / capacity 평가, live readiness approval은 아니다. | `phase30/`, `operations/PORTFOLIO_PROPOSAL_REGISTRY_GUIDE.md` |
| Live trading | broker order, live execution, 자동 매매는 현재 scope 밖이다. | `MASTER_PHASE_ROADMAP.md` |
| Config / migration | DB 설정 외부화, 정식 migration, 환경 분리는 아직 더 정리할 여지가 있다. | `AGENTS.md`, `code_analysis/` |
| Trading cost / liquidity | 일부 real-money surface는 있지만 완전한 체결비용, 슬리피지, 유동성 모델은 아니다. | `code_analysis/BACKTEST_RUNTIME_FLOW.md` |

즉 현재 제품은 “못 돌아가는 상태”가 아니라,
**개발 검증에서 더 엄격한 운영 검증으로 넘어가기 위한 경계를 정리하는 단계**다.

---

## 11. 데이터 품질 / PIT 해석 요약

데이터 품질과 DB table 의미의 상세 기준은 `.note/finance/data_architecture/`를 우선한다.
여기서는 현재 시스템을 읽을 때 반드시 기억할 위험만 요약한다.

| 데이터 영역 | 핵심 주의사항 | 상세 문서 |
|---|---|---|
| Price | stale / missing row는 결과 기간, excluded ticker, warning에 직접 영향을 준다. | `data_architecture/DATA_QUALITY_AND_PIT_NOTES.md` |
| Profile / universe | `status`, `is_spac`, sector, country는 유용하지만 historical truth는 아니다. | `data_architecture/TABLE_SEMANTICS.md` |
| Broad fundamentals | provider-normalized summary라 filing-time PIT source로 바로 쓰면 위험하다. | `data_architecture/TABLE_SEMANTICS.md` |
| Detailed statements | raw ledger는 강력하지만 concept/unit/period 해석과 filing timing 검증이 필요하다. | `data_architecture/DATA_QUALITY_AND_PIT_NOTES.md` |
| Factors | broad factors와 statement shadow factors의 성격을 구분해야 한다. | `data_architecture/TABLE_SEMANTICS.md` |

데이터 품질 문제는 숨기지 않고
warnings, metadata, report blocker, pre-live review reason으로 남기는 방향이 맞다.

---

## 12. 핵심 코드 진입점과 상세 문서 위치

이 섹션은 최소 진입점만 남긴다.
함수별 call flow, strategy contract, UI replay, 신규 전략 추가 절차는
`.note/finance/code_analysis/`를 우선한다.

| 알고 싶은 것 | 먼저 볼 문서 |
|---|---|
| data ingestion / DB write path를 어떻게 고칠지 | `code_analysis/DATA_DB_PIPELINE_FLOW.md` |
| DB table 의미와 데이터 품질 경계를 어떻게 볼지 | `data_architecture/README.md` |
| backtest runtime wrapper와 result bundle을 어떻게 볼지 | `code_analysis/BACKTEST_RUNTIME_FLOW.md` |
| Backtest UI, compare, history, saved replay 흐름을 어떻게 볼지 | `code_analysis/WEB_BACKTEST_UI_FLOW.md` |
| 신규 전략을 어떻게 추가할지 | `code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md` |
| phase bootstrap, registry, hygiene helper를 어떻게 쓸지 | `code_analysis/AUTOMATION_SCRIPTS_GUIDE.md` |

대표 코드 진입점은 아래처럼 본다.

| 영역 | 대표 위치 | 역할 |
|---|---|---|
| DB schema / persistence | `finance/data/db/schema.py`, `finance/data/db/*` | table 생성, UPSERT, DB 저장 규칙 |
| Data collection | `finance/data/*` | 가격, profile, fundamentals, statements 수집 |
| Loader read path | `finance/loaders/*` | DB 데이터를 백테스트 입력으로 변환 |
| Core strategy | `finance/strategy.py`, `finance/engine.py`, `finance/transform.py` | 전략 계산과 rebalancing / alignment |
| Performance | `finance/performance.py` | 성과 지표와 weighted portfolio summary |
| Web runtime | `app/web/runtime/backtest.py` | UI에서 호출하는 DB-backed runtime wrapper |
| Candidate registry runtime | `app/web/runtime/candidate_registry.py` | candidate / review note / pre-live registry JSONL I/O helper |
| Portfolio proposal runtime | `app/web/runtime/portfolio_proposal.py` | proposal draft registry JSONL I/O helper |
| Web UI | `app/web/pages/backtest.py` | Single / Compare / Candidate Review / History / Saved Portfolio / Pre-Live Review / Portfolio Proposal 화면 |

현재 구현을 읽는 핵심 구분:

- price-only ETF family는 price history, warmup, date alignment, cash fallback이 핵심이다.
- factor / fundamental family는 rebalance date, statement snapshot, PIT handling, selection history가 핵심이다.
- strict annual family의 real-money, guardrail, rejected-slot, weighting, risk-off contract는 strategy implementation flow에서 관리한다.
- single / compare / history / saved replay의 payload 복원 흐름은 web UI flow에서 관리한다.

---

## 13. 지금 당장 이해해야 하는 핵심 사실

1. 이 프로젝트의 최종 목표는 데이터 수집과 백테스트를 기반으로 투자 후보와 포트폴리오 구성안을 제안하는 프로그램을 만드는 것이다.
2. 현재 개발의 중심은 그 목표를 위한 데이터 수집, 백테스트 엔진, 전략 구현, UI 실행 / 비교 / 저장 / 재실행 workflow를 완성하는 것이다.
3. 현재 제품 경로는 DB-backed runtime, Backtest UI, compare, Candidate Review, history, saved replay, Pre-Live Review, Portfolio Proposal draft까지 확장됐다.
4. 강한 백테스트 결과가 최종 투자 추천이나 live trading 승인으로 자동 연결되지는 않는다.
5. Real-Money 검증 신호는 개별 백테스트 결과에 붙는 진단표이고, Pre-Live 운영 점검은 그 이후의 후보 상태 기록 절차다.
6. Phase 25는 live trading이 아니라 paper / watchlist / hold / re-review 운영 기록 체계를 준비하고 저장하는 단계를 완성했다.
7. Phase 26은 Phase 27~30을 시작하기 전에 과거 backlog와 현재 foundation gap을 다시 정렬했고, 사용자 checklist QA까지 완료했다.
8. Phase 27은 백테스트 결과 상단에서 데이터 가능 범위, 실제 결과 기간, stale / missing / malformed price 문제를 더 먼저 보이게 만들었고, 사용자 checklist QA까지 완료했다.
9. Phase 28은 annual strict, quarterly strict, price-only ETF 전략의 지원 범위와 cadence 차이를 `Strategy Capability Snapshot`으로 보이게 만들고, history / saved portfolio 재진입 가능성, compare / weighted data trust, Real-Money / Guardrail scope까지 확인하게 만든 뒤 사용자 checklist QA까지 완료했다.
10. Phase 29는 current candidate registry를 `Backtest > Candidate Review`에서 검토 보드로 읽고, 후보를 compare 또는 Pre-Live Review로 넘기며, Latest / History 결과를 후보 검토 초안, Candidate Review Note, registry draft로 보내는 workflow를 추가했고 사용자 QA까지 완료했다.
11. Phase 30은 implementation_complete / manual_qa_pending 상태다. Phase 29 이후의 사용 흐름, `backtest.py` 리팩토링 경계, Portfolio Proposal row 계약을 정리했고, registry JSONL I/O helper 분리와 `Backtest > Portfolio Proposal` draft UI / persistence / Monitoring Review / Pre-Live Feedback / Paper Tracking Feedback을 추가했다. 아직 live approval이나 자동 portfolio optimizer는 아니다.
12. 자세한 코드 흐름은 `code_analysis/`, DB와 데이터 품질은 `data_architecture/`, 결과 기록은 `backtest_reports/`에서 관리한다.

---

## 14. 다음 개발 우선순위

향후 우선순위는 “성과가 좋은 조합을 찾는 일”보다
제품이 안전하게 반복 실행되고, 후보를 재현 가능하게 검토할 수 있는 구조를 만드는 쪽에 둔다.

| 우선순위 | 왜 필요한가 | 기준 문서 |
|---|---|---|
| Phase 26 Foundation stabilization | 과거 pending / backlog를 현재 제품 기준으로 다시 정렬했고, Phase 27~30에서 다룰 주제를 분리했다. | `phase26/` |
| Phase 27 Data integrity / backtest trust | missing data, stale data, common-date truncation, excluded ticker를 사용자가 놓치지 않게 하는 첫 surface를 구현했고 QA까지 완료했다. | `data_architecture/DATA_QUALITY_AND_PIT_NOTES.md`, `code_analysis/BACKTEST_RUNTIME_FLOW.md`, `phase27/` |
| Phase 28 Strategy family parity | annual / quarterly / 신규 전략이 UI, payload, history, saved replay, Real-Money, Guardrail에서 의도된 수준으로 구분되도록 capability snapshot, history / saved portfolio replay/load parity snapshot, compare / weighted data trust, Real-Money / Guardrail scope surface를 추가했고 사용자 QA까지 완료했다. | `code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md`, `code_analysis/WEB_BACKTEST_UI_FLOW.md`, `phase28/` |
| Phase 29 Candidate review workflow | current candidate를 검토 보드로 읽고 compare / Pre-Live Review로 넘기는 surface와, Latest / History 결과를 후보 검토 초안, Candidate Review Note, registry draft로 보내는 workflow를 추가했고 QA까지 완료했다. | `operations/`, `backtest_reports/strategies/`, `phase29/` |
| Phase 30 Portfolio proposal / pre-live monitoring | 최종 목표인 포트폴리오 구성 제안으로 가기 위해 후보 묶음과 paper/pre-live tracking surface가 필요하다. 현재는 Phase 29 이후의 사용 흐름, `backtest.py` 리팩토링 경계, proposal row 계약, registry I/O helper 경계, Proposal Draft UI / persistence, Monitoring Review, Pre-Live Feedback, Paper Tracking Feedback을 구현하고 manual QA 대기 중이다. | `phase30/`, `code_analysis/WEB_BACKTEST_UI_FLOW.md` |

새 phase는 이 우선순위 안에서 사용자와 방향을 확인한 뒤 연다.

---

## 15. 퀀트 관점에서 추가되면 좋은 데이터

추가 데이터는 “있으면 좋아 보이는 것”이 아니라,
현재 제품의 검증 품질을 실제로 올리는 순서로 본다.

| 우선순위 | 데이터 | 왜 필요한가 |
|---|---|---|
| 높음 | listing / delisting / symbol change history | historical universe와 survivorship bias를 더 정확히 제어하기 위해 필요하다. |
| 높음 | risk-free rate / benchmark 시계열 | Sharpe, excess return, benchmark guardrail 해석을 더 엄격하게 만들기 위해 필요하다. |
| 높음 | ADV, volume quality, bid/ask spread proxy | turnover, capacity, liquidity risk를 추정하기 위해 필요하다. |
| 높음 | transaction cost / slippage assumption table | frictionless backtest와 실제 운용 가능성의 차이를 줄이기 위해 필요하다. |
| 중간 | sector / industry classification history | factor / sector bias 분석을 historical 기준으로 하기 위해 필요하다. |
| 중간 | index membership history | benchmark-relative universe와 membership bias를 검토하기 위해 필요하다. |
| 중간 | ETF metadata history | ETF 전략에서 asset class, inception, expense, closure risk를 더 잘 설명하기 위해 필요하다. |
| 고급 | analyst estimates / surprise | earnings surprise, revision factor research로 확장할 때 필요하다. |
| 고급 | short interest / borrow fee | crowded short, squeeze, short constraint 분석이 필요할 때 유용하다. |
| 고급 | option implied volatility | volatility regime, tail risk, option-aware strategy 연구에 필요하다. |

---

## 16. 현재 패키지를 한 문장으로 정의하면

현재 `finance` 패키지는:

> NYSE / ETF 데이터 수집, MySQL 기반 loader, DB-backed strategy runtime, Backtest UI compare/history/saved replay/Candidate Review/Pre-Live Review/Portfolio Proposal, strategy report, Pre-Live 운영 준비를 연결하는 퀀트 백테스트 워크벤치

라고 정의하는 것이 가장 정확하다.

---

## 17. 이후 이 문서를 어떻게 사용할지

이 문서는 상세 사양서가 아니라 top-level orientation 문서다.
처음 방향을 잡을 때 이 문서를 보고, 세부 작업은 아래 문서로 내려간다.

| 상황 | 우선 볼 문서 |
|---|---|
| 현재 phase 방향을 확인할 때 | `MASTER_PHASE_ROADMAP.md`, 해당 `phase*/` 문서 |
| finance 문서 전체 위치를 찾을 때 | `FINANCE_DOC_INDEX.md` |
| backtest 결과 / candidate report를 찾을 때 | `backtest_reports/BACKTEST_REPORT_INDEX.md` |
| strategy별 run log를 볼 때 | `backtest_reports/strategies/` |
| code flow를 따라갈 때 | `code_analysis/README.md` |
| DB / data quality를 확인할 때 | `data_architecture/README.md` |
| recurring term을 확인할 때 | `FINANCE_TERM_GLOSSARY.md` |
| 작업 진행 상태를 확인할 때 | `WORK_PROGRESS.md` |
| 사용자 질문과 설계 판단을 확인할 때 | `QUESTION_AND_ANALYSIS_LOG.md` |

문서 관리 원칙:

- 이 문서는 현재 구조의 큰 지도만 유지한다.
- 제품 목적, major layer, data flow, strategy family, runtime / UI workflow, Real-Money / Pre-Live 경계처럼 현재 시스템 이해를 바꾸는 변화가 있을 때만 갱신한다.
- 긴 코드 분석은 `code_analysis/`에 둔다.
- DB와 data flow 분석은 `data_architecture/`에 둔다.
- phase별 계획 / QA / closeout은 각 `phase*/` 폴더에 둔다.
- 의미 있는 backtest 결과는 `backtest_reports/`에 둔다.
- 작은 UI 문구, 일회성 결과, phase checklist 상태, minor bug-fix 기록은 이 문서에 누적하지 않는다.

---

## 18. 현재 반복 연구를 돕는 automation / persistence baseline

이 섹션은 automation / persistence의 큰 기준만 요약한다.
각 script의 사용 시점과 갱신 기준은
`.note/finance/code_analysis/AUTOMATION_SCRIPTS_GUIDE.md`를 우선한다.

| 구분 | 기준 파일 / script | 역할 |
|---|---|---|
| phase 문서 bootstrap | `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py` | 새 phase 기본 문서 bundle 생성 |
| phase checklist template | `.note/finance/PHASE_TEST_CHECKLIST_TEMPLATE.md` | 사용자가 직접 체크할 QA 문서의 기본 형태 |
| phase plan template | `.note/finance/PHASE_PLAN_TEMPLATE.md` | phase plan이 쉬운 설명, 필요성, 완료 후 장점을 포함하도록 하는 기본 형태 |
| current candidate registry | `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` | strongest / near-miss 후보의 machine-readable persistence |
| candidate review notes | `.note/finance/CANDIDATE_REVIEW_NOTES.jsonl` | 후보 검토 초안을 본 뒤 남기는 operator decision persistence |
| pre-live candidate registry | `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 후보의 watchlist / paper tracking / hold / reject / re-review 운영 상태 persistence |
| backtest report index | `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md` | durable backtest report 위치를 찾는 전용 index |
| strategy run logs | `.note/finance/backtest_reports/strategies/*_BACKTEST_LOG.md` | 반복 strategy 실험 결과를 strategy별로 누적 |
| refinement hygiene helper | `plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | 문서 / index / root log / generated artifact 상태 점검 |
| code analysis docs | `.note/finance/code_analysis/` | 코드 흐름, UI 흐름, strategy 추가 절차, automation script 사용법 관리 |
| data architecture docs | `.note/finance/data_architecture/` | DB schema, table semantics, data flow, PIT/data-quality 기준 관리 |
| pre-live registry helper | `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py` | Pre-Live 후보 운영 기록 template / draft-from-current / list / show / append / validate |

주의:

- `.note/finance/BACKTEST_RUN_HISTORY.jsonl`, `.note/finance/WEB_APP_RUN_HISTORY.jsonl` 같은 실행 기록은 유용하지만 보통 commit 대상이 아니다.
- 자동화 script는 작업을 돕는 support tool이지, 사람이 판단해야 할 phase gate를 대체하지 않는다.
- phase closeout 때는 roadmap, doc index, report index, glossary, skill guidance가 stale해졌는지 함께 확인한다.
