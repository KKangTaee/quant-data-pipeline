# Finance Script Structure Map

## 목적

이 문서는 코드 수정자가 먼저 보는 빠른 스크립트 책임 지도다.
상세 실행 흐름은 같은 폴더의 개별 flow 문서에 두고,
여기에는 "어느 파일이 어떤 종류의 기능을 관리하는지"만 간략히 남긴다.

코드 수정 전에 이 문서를 먼저 훑고, 실제 수정은 해당 영역의 상세 문서를 이어서 확인한다.

## 갱신 기준

아래 변경이 있으면 같은 작업 단위에서 이 문서를 갱신한다.

- 새 Python 스크립트가 추가되거나 기존 스크립트가 삭제될 때
- 스크립트 이름이 바뀌거나 위치가 이동할 때
- 큰 모듈이 render / helper / runtime처럼 책임 단위로 분리될 때
- 특정 스크립트가 관리하는 기능 범위가 눈에 띄게 바뀔 때

작은 함수 내부 구현 변경, copy 변경, 일회성 실험 결과는 이 문서에 올리지 않는다.

## App / Web

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/web/streamlit_app.py` | Finance Console top navigation, page entry, page-level routing |
| `app/web/reference_guides.py` | `Reference > Guides`의 제품형 portfolio workflow guide, flowchart, decision gate, reference drawer render |
| `app/web/ops_review.py` | `Operations > Ops Review`의 triage flow, 웹앱 run health, action inbox, failure artifact, log, system snapshot dashboard render |
| `app/web/overview_dashboard.py` | `Workspace > Overview`의 후보 Top 3, funnel chart, next actions, recent activity, system snapshot dashboard render |
| `app/web/overview_dashboard_helpers.py` | Overview dashboard용 current candidate / Pre-Live / proposal / history / saved portfolio 집계, 후보 우선순위 scoring, funnel / activity table helper |
| `app/web/backtest_strategy_catalog.py` | Strategy display name, strategy key, family variant 선택 매핑 |
| `app/web/backtest_common.py` | Backtest 공용 preset / session state / 3단계 stage routing compatibility / ticker universe input / real-money contract / guardrail input / label 변환 helper |
| `app/web/backtest_workflow_routes.py` | Backtest visible stage 3개와 legacy panel route를 매핑하는 route helper |
| `app/web/backtest_analysis.py` | `Backtest > Backtest Analysis`에서 Single Strategy / Compare & Portfolio Builder를 submode로 렌더링하는 wrapper |
| `app/web/backtest_single_strategy.py` | `Backtest > Single Strategy` 화면 orchestration, strategy 선택 / prefill notice / form dispatch / latest result 연결 |
| `app/web/backtest_single_forms.py` | Single Strategy의 Equal Weight, GTAA, GRS, Risk Parity, Dual Momentum, Quality / Value 계열 strategy-specific form render |
| `app/web/backtest_single_runner.py` | Single Strategy payload 실행 dispatch, DB-backed runtime 호출, latest bundle state 저장, run history append |
| `app/web/backtest_compare.py` | `Backtest > Compare & Portfolio Builder` 화면 render, compare 실행, weighted portfolio builder, saved portfolio replay / load, candidate handoff |
| `app/web/backtest_result_display.py` | Backtest 결과 공용 display, summary / chart / data trust / real-money detail / selection history / compare result helper |
| `app/web/backtest_history.py` | `Operations > Backtest Run History` 화면 render, history inspect / replay / form load / candidate draft handoff, Real-Money / Guardrail parity table render |
| `app/web/backtest_history_helpers.py` | Backtest history row 변환, replay payload 복원, History replay parity / Real-Money scope table helper |
| `app/web/backtest_candidate_library.py` | `Operations > Candidate Library` 화면 render, 저장된 current / Pre-Live 후보 inspect, 저장 contract 기반 result curve rebuild |
| `app/web/backtest_candidate_library_helpers.py` | Candidate Library용 registry join, 후보 table row, replay payload 생성, ETF 후보 replay runtime dispatch helper |
| `app/web/backtest_ui_components.py` | Backtest UI 공용 wrapping status card, artifact pipeline, compact badge strip, stage brief strip, route/readiness 판정 panel |
| `app/web/backtest_practical_validation.py` | `Backtest > Practical Validation`에서 Clean V2 selection source 확인, 검증 프로필 입력, 최신 DB 데이터 기준 runtime 재검증 실행 버튼, V2 practical diagnostics board / Provider Data Gaps 표시, 부족 provider snapshot 일괄 수집 / 보강 버튼, Final Review handoff를 담당하는 화면 render |
| `app/web/backtest_practical_validation_helpers.py` | Clean V2 portfolio selection source 생성, validation profile threshold / score 해석, 12개 Practical Diagnostics result 생성 / 저장 / Final Review handoff helper |
| `app/web/backtest_practical_validation_connectors.py` | Practical Validation P2 provider context adapter. ETF operability / holdings / exposure / FRED macro loader 결과를 compact coverage와 diagnostic evidence로 변환 |
| `app/web/backtest_practical_validation_curve.py` | Practical Validation의 curve normalize / compact records / curve provenance / benchmark parity helper |
| `app/web/backtest_practical_validation_replay.py` | Practical Validation source를 기존 strategy runtime으로 최신 DB 데이터 기준 재검증하거나 저장 기간 그대로 재현해 component / portfolio curve evidence를 만드는 helper |
| `app/web/backtest_candidate_review.py` | `Backtest > Candidate Review`의 Candidate Packaging 화면 render, Review Note / current candidate registry 저장, Pre-Live 운영 기록 저장, Portfolio Proposal 이동 판단 |
| `app/web/backtest_candidate_review_helpers.py` | Candidate Review readiness 평가, Review Note 생성, current candidate registry row 변환, Pre-Live status 추천 / draft 생성 / Proposal readiness 평가, display table helper |
| `app/web/backtest_portfolio_proposal.py` | `Backtest > Portfolio Proposal`의 단일 후보 직행 평가, 다중 후보 proposal 후보 선택, 목적 / 역할 / 비중 설계, proposal draft 저장, 저장 proposal monitoring / feedback 화면 render |
| `app/web/backtest_portfolio_proposal_helpers.py` | Portfolio Proposal row 생성, 단일 후보 direct readiness / proposal save readiness 평가, 공유 validation / robustness 계산 helper, saved proposal monitoring / Pre-Live feedback / paper feedback table helper |
| `app/web/backtest_final_review.py` | `Backtest > Final Review`의 단일 후보 / 저장 proposal 선택, Practical Diagnostics 요약, Validation / Robustness / Paper Observation 기준 확인, 최종 선정 / 보류 / 거절 / 재검토 결과 기록, 최종 판단 완료 review 화면 render |
| `app/web/backtest_final_review_helpers.py` | Final Review source 선택, validation 재사용, Practical Diagnostics snapshot 포함, inline paper observation snapshot, final review evidence / save readiness / decision row 생성, saved final decision display helper |
| `app/web/final_selected_portfolio_dashboard.py` | `Operations > Selected Portfolio Dashboard` 화면 render, Final Review에서 선정된 포트폴리오 summary / compact selected portfolio picker / Snapshot / tabbed Performance Recheck / Portfolio Monitoring Review Signals / optional Actual Allocation / Audit 표시 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | Selected Portfolio Dashboard용 table row, component row, evidence row, value / holding input row, drift row, alert preview row, filter option helper |
| `app/web/pages/backtest.py` | Backtest page shell, `Backtest Analysis -> Practical Validation -> Final Review` workflow navigation, stage dispatch entry. 본문은 별도 module이 관리 |

## App / Runtime

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/web/runtime/backtest.py` | UI payload를 DB-backed backtest 실행으로 변환하는 runtime wrapper, Real-Money / guardrail / benchmark 계약 처리 |
| `app/web/runtime/candidate_registry.py` | current candidate, candidate review note, pre-live registry JSONL path / load / append helper |
| `app/web/runtime/history.py` | Backtest run history persistence helper |
| `app/web/runtime/portfolio_proposal.py` | Portfolio proposal draft registry JSONL path / load / append helper |
| `app/web/runtime/paper_portfolio_ledger.py` | Paper Portfolio Tracking Ledger JSONL path / load / append helper |
| `app/web/runtime/final_selection_decisions.py` | Final Portfolio Selection Decision JSONL path / load / append helper |
| `app/web/runtime/portfolio_selection_v2.py` | Clean V2 portfolio selection source / Practical Validation result / Final Decision V2 / selected monitoring log / saved mix JSONL helper와 legacy archive copy helper |
| `app/web/runtime/final_selected_portfolios.py` | Final Selection Decision V2 registry를 read-only로 읽어 최종 선정 포트폴리오 운영 대시보드 row / status summary / 기간 확장 replay recheck / current weight 또는 value / holding input 기반 drift check / drift alert preview로 변환 |
| `app/web/runtime/portfolio_store.py` | Saved portfolio persistence helper |

## App / Jobs

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/jobs/ingestion_jobs.py` | `Workspace > Ingestion`에서 실행하는 수집 / refresh job wrapper. OHLCV, fundamentals, statement refresh, asset profile, Practical Validation provider snapshot job을 표준 `JobResult`로 감싼다 |

## Finance Core

| 스크립트 | 관리하는 기능 |
|---|---|
| `finance/sample.py` | DB-backed strategy example / smoke 실행 함수, UI runtime이 호출하는 sample-level strategy entry |
| `finance/engine.py` | Strategy orchestration, input alignment, engine-level execution |
| `finance/strategy.py` | 실제 portfolio simulation / rebalancing logic |
| `finance/transform.py` | Strategy 공용 전처리, signal / factor / ranking transform helper |
| `finance/performance.py` | 성과 요약, portfolio performance metric, weighted portfolio 계산 helper |
| `finance/display.py` | CLI / notebook 성격의 display helper |
| `finance/visualize.py` | 백테스트 결과 시각화 helper |

## Finance Loaders

| 스크립트 | 관리하는 기능 |
|---|---|
| `finance/loaders/price.py` | DB price history / price matrix / freshness / latest per-symbol price read path |
| `finance/loaders/provider.py` | Practical Validation provider snapshot read path. ETF operability, ETF holdings, ETF exposure snapshot loader를 제공 |
| `finance/loaders/macro.py` | Practical Validation market-context read path. FRED macro series observation과 기준일 snapshot / staleness loader를 제공 |
| `finance/loaders/factors.py` | Factor snapshot read path |
| `finance/loaders/fundamentals.py` | Fundamentals read path |
| `finance/loaders/financial_statements.py` | Statement snapshot read path |
| `finance/loaders/universe.py` | Universe / investability 관련 read path |
| `finance/loaders/runtime_adapter.py` | loader output을 runtime / strategy 입력으로 맞추는 adapter |
| `finance/loaders/_common.py` | loader 공통 DB / dataframe helper |

## Finance Data / DB

| 스크립트 | 관리하는 기능 |
|---|---|
| `finance/data/db/schema.py` | Finance DB table schema 기준 |
| `finance/data/db/mysql.py` | MySQL connection / execution helper |
| `finance/data/data.py` | 가격 데이터 수집 entry / orchestration |
| `finance/data/data_format.py` | 수집 데이터 정규화 helper |
| `finance/data/nyse.py` | NYSE universe source 수집 |
| `finance/data/nyse_db.py` | NYSE universe DB persistence |
| `finance/data/asset_profile.py` | Asset profile 수집. ETF operability snapshot의 bridge source로 일부 field를 제공 |
| `finance/data/etf_provider.py` | ETF provider source map discovery, ETF operability / holdings / exposure snapshot schema sync, 기존 price/profile DB 기반 bridge/proxy 수집, iShares / SSGA / Invesco official row normalize, commodity gold exposure row 생성, holdings canonical refresh, exposure aggregation, UPSERT 저장 |
| `finance/data/macro.py` | FRED market-context series 수집. VIX / yield curve / credit spread series를 `macro_series_observation`에 UPSERT 저장 |
| `finance/data/fundamentals.py` | Fundamentals 수집 |
| `finance/data/financial_statements.py` | Financial statement 수집 |
| `finance/data/factors.py` | Factor 생성 / 저장 pipeline |

## Repo-Local Automation

| 스크립트 | 관리하는 기능 |
|---|---|
| `.aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py` | 새 finance phase 문서 bundle 생성 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | finance diff의 docs / logs / generated artifact hygiene 점검 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py` | Current Candidate Registry list / show / validate / append helper |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py` | Pre-Live Candidate Registry template / draft / list / show / validate / append helper |

## 같이 볼 상세 문서

| 작업 종류 | 상세 문서 |
|---|---|
| Backtest UI / Candidate Review / History / Proposal | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` |
| UI payload -> runtime -> result bundle | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` |
| Data / DB / loader | `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` |
| Strategy family 추가 / 연결 | `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` |
| Repo-local helper script | `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md` |
