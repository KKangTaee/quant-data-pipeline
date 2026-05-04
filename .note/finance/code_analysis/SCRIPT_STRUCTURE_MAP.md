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
| `app/web/overview_dashboard.py` | `Workspace > Overview`의 후보 Top 3, funnel chart, next actions, recent activity, system snapshot dashboard render |
| `app/web/overview_dashboard_helpers.py` | Overview dashboard용 current candidate / Pre-Live / proposal / history / saved portfolio 집계, 후보 우선순위 scoring, funnel / activity table helper |
| `app/web/backtest_strategy_catalog.py` | Strategy display name, strategy key, family variant 선택 매핑 |
| `app/web/backtest_common.py` | Backtest 공용 preset / session state / panel routing / ticker universe input / real-money contract / guardrail input / label 변환 helper |
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
| `app/web/backtest_candidate_review.py` | `Backtest > Candidate Review`의 Candidate Packaging 화면 render, Review Note / current candidate registry 저장, Pre-Live 운영 기록 저장, Portfolio Proposal 이동 판단 |
| `app/web/backtest_candidate_review_helpers.py` | Candidate Review readiness 평가, Review Note 생성, current candidate registry row 변환, Pre-Live status 추천 / draft 생성 / Proposal readiness 평가, display table helper |
| `app/web/backtest_portfolio_proposal.py` | `Backtest > Portfolio Proposal`의 단일 후보 직행 평가, 다중 후보 proposal 후보 선택, 목적 / 역할 / 비중 설계, proposal draft 저장, 저장 proposal monitoring / feedback 화면 render |
| `app/web/backtest_portfolio_proposal_helpers.py` | Portfolio Proposal row 생성, 단일 후보 direct readiness / proposal save readiness 평가, 공유 validation / robustness 계산 helper, saved proposal monitoring / Pre-Live feedback / paper feedback table helper |
| `app/web/backtest_final_review.py` | `Backtest > Final Review`의 단일 후보 / 저장 proposal 선택, Validation / Robustness / Paper Observation 기준 확인, 최종 선정 / 보류 / 거절 / 재검토 결과 기록, Phase35 handoff review 화면 render |
| `app/web/backtest_final_review_helpers.py` | Final Review source 선택, validation 재사용, inline paper observation snapshot, final review evidence / save readiness / decision row 생성, saved final decision display helper |
| `app/web/backtest_post_selection_guide.py` | `Backtest > Post-Selection Guide`의 selected final decision 선택, 최종 투자 가능성 확인, 운영 전 기준 preview 화면 render |
| `app/web/backtest_post_selection_guide_helpers.py` | Post-Selection Guide input selector, 최종 판단 문구 변환, readiness route, final guide preview helper |
| `app/web/pages/backtest.py` | Backtest page shell, workflow navigation, panel dispatch entry. Single / Compare / Candidate Review / Portfolio Proposal / Final Review / Post-Selection Guide 본문은 별도 module이 관리 |

## App / Runtime

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/web/runtime/backtest.py` | UI payload를 DB-backed backtest 실행으로 변환하는 runtime wrapper, Real-Money / guardrail / benchmark 계약 처리 |
| `app/web/runtime/candidate_registry.py` | current candidate, candidate review note, pre-live registry JSONL path / load / append helper |
| `app/web/runtime/history.py` | Backtest run history persistence helper |
| `app/web/runtime/portfolio_proposal.py` | Portfolio proposal draft registry JSONL path / load / append helper |
| `app/web/runtime/paper_portfolio_ledger.py` | Paper Portfolio Tracking Ledger JSONL path / load / append helper |
| `app/web/runtime/final_selection_decisions.py` | Final Portfolio Selection Decision JSONL path / load / append helper |
| `app/web/runtime/portfolio_store.py` | Saved portfolio persistence helper |

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
| `finance/loaders/price.py` | DB price history read path |
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
| `finance/data/asset_profile.py` | Asset profile / ETF operability metadata 수집 |
| `finance/data/fundamentals.py` | Fundamentals 수집 |
| `finance/data/financial_statements.py` | Financial statement 수집 |
| `finance/data/factors.py` | Factor 생성 / 저장 pipeline |

## Repo-Local Automation

| 스크립트 | 관리하는 기능 |
|---|---|
| `plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py` | 새 finance phase 문서 bundle 생성 |
| `plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | finance diff의 docs / logs / generated artifact hygiene 점검 |
| `plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py` | Current Candidate Registry list / show / validate / append helper |
| `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py` | Pre-Live Candidate Registry template / draft / list / show / validate / append helper |

## 같이 볼 상세 문서

| 작업 종류 | 상세 문서 |
|---|---|
| Backtest UI / Candidate Review / History / Proposal | `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md` |
| UI payload -> runtime -> result bundle | `.note/finance/code_analysis/BACKTEST_RUNTIME_FLOW.md` |
| Data / DB / loader | `.note/finance/code_analysis/DATA_DB_PIPELINE_FLOW.md` |
| Strategy family 추가 / 연결 | `.note/finance/code_analysis/STRATEGY_IMPLEMENTATION_FLOW.md` |
| Repo-local helper script | `.note/finance/code_analysis/AUTOMATION_SCRIPTS_GUIDE.md` |
