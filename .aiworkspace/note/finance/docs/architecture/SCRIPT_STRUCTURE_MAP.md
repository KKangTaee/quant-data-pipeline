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
| `app/workspace_paths.py` | active worktree root 탐색과 canonical `.aiworkspace/note/finance`의 registries / saved / run_history / docs / artifact path 상수 |
| `app/web/streamlit_app.py` | Finance Console top navigation, page entry, page-level routing |
| `app/web/ingestion_console.py` | `Workspace > Ingestion` render / session-state boundary. Korean purpose-first job guide, symbol preset/source controls, explicit ingestion job scheduling, runtime metadata handoff, result/history/log/failure artifact display, and price / statement / PIT diagnostic panel rendering. Read-only diagnostic orchestration is delegated to `app/services/ingestion_diagnostics.py` |
| `app/web/operations_overview.py` | `Operations > Operations Overview` / `Operations Console` render와 Streamlit-free Operations read model. Portfolio Monitoring Status summary, Today action queue, Portfolio Monitoring / System Data Health primary lane, no-live approval / order / auto rebalance boundary를 표시 |
| `app/web/reference_guides.py` | `Reference > Guides`의 제품형 portfolio workflow guide, flowchart, decision gate, reference drawer render |
| `app/web/ops_review.py` | `Operations > System / Data Health`의 triage flow, 웹앱 run health, action inbox, failure artifact, log, system snapshot dashboard render |
| `app/web/overview_dashboard.py` | `Workspace > Overview`의 Market Movers, Why It Moved, Sector / Industry, Sentiment, Events, Data Health, Candidate Ops tab render. Market session banner, daily snapshot refresh action bar, browser-session auto refresh heartbeat, Market Movers manual investigation panel, Sector / Industry ranking/trend, Sentiment context, Events view routing을 조정. 수집 action은 `app/jobs/overview_actions.py` facade를 호출한다 |
| `app/web/overview_dashboard_helpers.py` | Overview dashboard용 current candidate / Pre-Live / proposal / history / saved portfolio 집계, 후보 우선순위 scoring, cached market intelligence service wrapper |
| `app/web/overview_ui_components.py` | Overview 전용 visual token, Market Movers refresh surface / metadata strip, Events summary/source/agenda/calendar/quality components, market session banner render |
| `app/web/backtest_strategy_catalog.py` | Strategy display name, strategy key, family variant 선택 매핑 |
| `app/web/backtest_common.py` | Backtest 공용 preset / session state / 3단계 stage routing compatibility / ticker universe input / real-money contract / guardrail input / label 변환 helper |
| `app/web/backtest_workflow_routes.py` | Backtest visible stage 3개와 legacy panel route를 매핑하는 route helper |
| `app/web/backtest_analysis.py` | `Backtest > Backtest Analysis`에서 Single Strategy / Portfolio Mix Builder를 submode로 렌더링하는 wrapper |
| `app/web/backtest_single_strategy.py` | `Backtest > Single Strategy` 화면 orchestration, strategy 선택 / prefill notice / form dispatch / latest result 연결 |
| `app/web/backtest_single_forms.py` | Single Strategy의 Equal Weight, GTAA, GRS, Risk Parity, Dual Momentum, Quality / Value 계열 strategy-specific form render |
| `app/web/backtest_single_runner.py` | Single Strategy payload 표시, execution service 호출, latest bundle state 저장, run history append |
| `app/web/backtest_compare.py` | `Backtest > Portfolio Mix Builder` 화면 orchestration, component portfolio 실행 / weighted portfolio / saved replay service 호출, saved portfolio load, mix candidate handoff, preset catalog assembly |
| `app/web/backtest_compare_components.py` | `Backtest > Portfolio Mix Builder` visual shell. CSS, flow stepper, section heading, component result card render를 담당하며 compare 실행 / 저장 / handoff 로직은 포함하지 않는다 |
| `app/web/backtest_result_display.py` | Backtest 결과 공용 display, summary / chart / data trust / real-money detail / selection history / compare result render wrapper |
| `app/web/backtest_history.py` | Hidden compatibility archive render for historical backtest run inspect / replay / form load / candidate draft handoff, Real-Money / Guardrail parity table render. Not exposed in current Operations top navigation |
| `app/web/backtest_history_helpers.py` | Backtest history row 변환, replay payload 복원, History replay parity / Real-Money scope table helper |
| `app/web/backtest_candidate_library.py` | Hidden compatibility archive render for saved current / Pre-Live 후보 inspect and stored-contract result curve rebuild. Not exposed in current Operations top navigation |
| `app/web/backtest_ui_components.py` | Backtest UI 공용 wrapping status card, artifact pipeline, compact badge strip, stage brief strip, route/readiness 판정 panel, legacy product card / stepper helper |
| `app/web/backtest_practical_validation_components.py` | Practical Validation 전용 visual shell. Command Center, section header, card grid, step rail, alert panel CSS / HTML helper를 제공하며 service/gate 로직은 포함하지 않는다 |
| `app/web/backtest_practical_validation.py` | `Backtest > Practical Validation`에서 current selection source의 strategy / construction / selection history 확인, 검증 프로필 입력, CNN / AAII market sentiment context overlay, 최신 DB 데이터 기준 runtime 재검증 실행 버튼, 전용 workbench shell 기반 Control Center, Fix Queue, summary-first evidence workspace, Applied Validation Map, Provider Action Center, Look-through Board / Robustness Lab 표시, provider gap / replay service 실행 버튼, service 결과를 session state에 반영하는 화면 render |
| `app/web/backtest_candidate_review.py` | `Backtest > Candidate Review`의 Candidate Packaging 화면 render, Review Note / current candidate registry 저장, Pre-Live 운영 기록 저장, Portfolio Proposal 이동 판단 |
| `app/web/backtest_candidate_review_helpers.py` | Candidate Review readiness 평가, Review Note 생성, current candidate registry row 변환, Pre-Live status 추천 / draft 생성 / Proposal readiness 평가, display table helper |
| `app/web/backtest_portfolio_proposal.py` | `Backtest > Portfolio Proposal`의 단일 후보 직행 평가, 다중 후보 proposal 후보 선택, 목적 / 역할 / 비중 설계, proposal draft 저장, 저장 proposal monitoring / feedback 화면 render |
| `app/web/backtest_portfolio_proposal_helpers.py` | Portfolio Proposal row 생성, 단일 후보 direct readiness / proposal save readiness 평가, 공유 validation / robustness 계산 helper, saved proposal monitoring / Pre-Live feedback / paper feedback table helper |
| `app/web/backtest_final_review.py` | `Backtest > Final Review`의 Decision Desk command center / flow, CNN / AAII market sentiment context overlay, Practical Validation Gate 통과 후보 Candidate Board priority / review queue, 선택 후보 Decision Cockpit, selected-route gate 통과 후보의 최종 선정 저장 checklist / route guide, 보류 / 거절 / 재검토 상태 안내, Evidence Appendix의 Practical Diagnostics / Look-through / Robustness Lab / Paper Observation / Investability Evidence Packet read-only 확인, 저장된 최종 선정 review ledger / Selected Dashboard handoff / Decision Dossier 화면 render |
| `app/web/backtest_final_review_components.py` | Final Review 전용 visual shell. Command Center, flow rail, section header, lane grid, action panel CSS / HTML helper를 제공하며 service/gate/persistence 로직은 포함하지 않는다 |
| `app/web/backtest_final_review_helpers.py` | Final Review source 선택, validation 재사용, Practical Diagnostics snapshot 포함, inline paper observation snapshot, investability packet 연결, final review evidence / save readiness / decision row 생성 helper |
| `app/web/final_selected_portfolio_dashboard.py` | `Operations > Portfolio Monitoring` 화면 render. Legacy file name은 Selected Portfolio Dashboard를 유지한다. CNN / AAII market sentiment context overlay, 사용자 monitoring portfolio 생성 / 선택 / soft delete, Final Review selected strategy 추가 / 제거, strategy별 Snapshot / Monitoring Scenario / recheck readiness / symbol freshness / provider evidence / continuity check / source contract / Monitoring Timeline / Review Signal Policy / Open Issues / optional preflight / recheck comparison / optional Actual Allocation / allocation evidence boundary / Decision Dossier / Audit / 전환 비교 표시 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | Selected Portfolio Dashboard용 dashboard portfolio row, selected strategy pool row, strategy comparison row, handoff row, component row, continuity row, source contract row, timeline row, recheck readiness row, symbol freshness row, provider evidence row, review signal policy row, open issue follow-up row, deployment readiness row, recheck comparison row, value / holding input row, drift row, alert preview row, allocation boundary row, filter option helper. Evidence row는 service read model을 사용 |
| `app/web/pages/backtest.py` | Backtest page shell, `Backtest Analysis -> Practical Validation -> Final Review` workflow navigation, stage dispatch entry. 본문은 별도 module이 관리 |

## App / Services

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/services/backtest_execution.py` | Streamlit-free Single Strategy execution service. runtime dispatch, elapsed timing, input/data/system error normalization, result bundle metadata update를 담당 |
| `app/services/ingestion_diagnostics.py` | Streamlit-free Ingestion read-only diagnostics facade. Price window preflight, Price Stale Diagnosis, Statement Coverage Diagnosis, Statement PIT Inspection의 loader/job/source inspection calls를 UI 대신 담당 |
| `app/services/backtest_compare_execution.py` | Streamlit-free manual Compare execution service. multi-strategy execution loop, elapsed timing, input/data/system error normalization을 담당 |
| `app/services/backtest_compare_catalog.py` | Streamlit-free Compare runner catalog service. strategy별 default parameter, preset/manual universe resolution, runtime dispatch, runner signature filtering을 담당 |
| `app/services/backtest_result_read_model.py` | Streamlit-free Backtest result read model helper. strategy data trust row와 weighted component contribution view를 담당 |
| `app/services/backtest_weighted_portfolio.py` | Streamlit-free weighted portfolio builder service. compared strategy result bundle을 월별 weighted result bundle로 합성 |
| `app/services/backtest_saved_portfolio_replay.py` | Streamlit-free saved portfolio replay service. 저장된 mix의 strategy rerun, weighted bundle 생성, replay source / history context 조립을 담당 |
| `app/services/backtest_practical_validation.py` | Streamlit-free Practical Validation service. result 생성 wrapper, selection source / validation result append, Practical Validation / Final Review handoff contract, provider gap row / collection plan / ingestion job orchestration, Practical Validation / Final Review / Portfolio Monitoring의 surface-aware CNN / AAII market sentiment context overlay를 담당 |
| `app/services/backtest_practical_validation_source.py` | Streamlit-free Practical Validation validation profile / selection source builder / source component table / compact selection history helper. Candidate draft, saved mix, weighted mix를 current selection source contract로 변환 |
| `app/services/backtest_practical_validation_curve_context.py` | Streamlit-free Practical Validation curve context helper. compact curve snapshot, result curve normalize, DB price proxy curve, component curve combination, window perturbation / monthly returns 계산을 담당 |
| `app/services/backtest_practical_validation_stress_sensitivity.py` | Streamlit-free Practical Validation stress / sensitivity helper. rolling validation, stress window, baseline challenge, sensitivity interpretation, correlation risk, market context, overfit audit, Robustness Lab board를 담당 |
| `app/services/backtest_temporal_validation.py` | Streamlit-free temporal validation helper. benchmark-aligned walk-forward rolling excess return, OOS holdout excess / deterioration, macro regime split excess / drawdown gap, source strength, compact storage boundary evidence를 담당 |
| `app/services/backtest_practical_validation_diagnostics.py` | Streamlit-free Practical Validation diagnostics service. component context assembly, 12개 Practical Diagnostics result 생성, validation module / board map 결과 병합, legacy compatibility export를 담당 |
| `app/services/backtest_practical_validation_replay.py` | Streamlit-free Practical Validation replay service. 기존 strategy runtime으로 최신 DB 데이터 기준 재검증하거나 저장 기간 그대로 재현해 component / portfolio curve evidence와 replay selection history snapshot을 만든다 |
| `app/services/backtest_practical_validation_curve.py` | Streamlit-free Practical Validation curve normalize / compact records / curve provenance / benchmark parity helper |
| `app/services/backtest_practical_validation_provider_context.py` | Streamlit-free Practical Validation provider context adapter. ETF operability / holdings / exposure / FRED macro loader 결과를 compact coverage, provenance, freshness, diagnostic evidence, look-through board로 변환 |
| `app/services/backtest_practical_validation_modules.py` | Streamlit-free Practical Validation module planner. source traits와 profile / input checks / diagnostics / audit rows를 읽어 필수 / 조건부 / 후속 참고 module, gate effect, gate reason, Final Review 이동 gate, evidence board 연결을 만든다 |
| `app/services/backtest_practical_validation_board_registry.py` | Streamlit-free Practical Validation board registry. 화면 보드가 어떤 validation module을 설명하는지, 현재 후보에 적용되는지, 어떤 gate effect를 갖는지 board map으로 변환 |
| `app/services/backtest_construction_risk_audit.py` | Streamlit-free construction risk audit read model. Practical Validation metrics와 provider look-through board를 읽어 component concentration, provider coverage, top holding, holdings overlap, asset bucket exposure를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 변환 |
| `app/services/backtest_risk_contribution_audit.py` | Streamlit-free risk contribution audit read model. Practical Validation의 component return matrix, correlation, max risk contribution proxy, drop-one dependency, storage boundary evidence를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 변환 |
| `app/services/backtest_component_role_weight_audit.py` | Streamlit-free component role / weight audit read model. Practical Validation의 proposal role, target weight, validation profile, role concentration, profile intent, weight reason evidence를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 변환 |
| `app/services/backtest_evidence_read_model.py` | Streamlit-free evidence read model service. Final Review candidate board priority / decision cockpit / decision record guide / saved decision review / final decision status / investability evidence packet / profile-aware gate policy snapshot / selected-route gate / saved decision table row / Selected Dashboard evidence check row / Decision Dossier markdown read model과 selected decision source consistency contract를 담당. Validation Efficacy Audit의 walk-forward / OOS / regime non-PASS row를 gate policy evidence에 병합한다 |
| `app/services/overview_market_intelligence.py` | Streamlit-free Overview market intelligence service. S&P 500 / Top1000 / Top2000 movers, yearly period, sector filter, intraday snapshot read path, missing diagnostics, Why It Moved manual investigation read model / session-only compact metadata helper, Sector / Industry ranking/trend/ticker leaders, market event calendar payload, collection ops snapshot을 담당 |

## App / Runtime

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/runtime/backtest.py` | UI payload를 DB-backed backtest 실행으로 변환하는 public runtime compatibility facade와 price-only ETF family runtime wrappers. Result bundle, Risk-On Momentum, Real-Money helper, Strict quality / value family 구현은 전용 module로 위임하고 기존 import path를 re-export한다 |
| `app/runtime/backtest_risk_on_momentum.py` | Risk-On Momentum 5D runtime slice. managed universe resolution, DB price / statement / futures macro load, swing execution, comparison / sensitivity / stability wiring, generated swing artifact writer를 담당하며 `app.runtime.backtest`가 compatibility export한다 |
| `app/runtime/backtest_real_money.py` | Backtest real-money / guardrail / benchmark / deployment readiness helper slice. constants, ticker normalization compatibility helper, cost / turnover postprocess, benchmark overlay, validation / promotion / shortlist / probation / monitoring / deployment readiness contracts, ETF operability policy, `_apply_real_money_hardening`을 담당하며 `app.runtime.backtest`가 compatibility export한다 |
| `app/runtime/backtest_strict.py` | Strict quality / value / quality-value annual and quarterly runtime slice. strict price freshness, factor / statement snapshot preflight, dynamic universe handling, rejected slot handling, strict result metadata assembly를 담당하며 `app.runtime.backtest`가 compatibility export한다 |
| `app/runtime/backtest_result_bundle.py` | Backtest runtime result bundle contract helper. `result_df`를 정렬하고 summary / chart / metadata bundle을 생성하며 `app.runtime.backtest` public export와 호환된다 |
| `app/runtime/candidate_library.py` | Candidate Library용 registry join, 후보 table row, replay payload 생성, ETF / strict annual equity 후보 replay runtime dispatch helper |
| `app/runtime/candidate_registry.py` | current candidate, candidate review note, pre-live registry JSONL path / load / append helper |
| `app/runtime/history.py` | Backtest run history persistence helper |
| `app/runtime/portfolio_proposal.py` | Portfolio proposal draft registry JSONL path / load / append helper |
| `app/runtime/paper_portfolio_ledger.py` | Paper Portfolio Tracking Ledger JSONL path / load / append helper |
| `app/runtime/final_selection_decisions.py` | Final Portfolio Selection Decision JSONL path / load / append helper |
| `app/runtime/portfolio_selection_v2.py` | current workflow portfolio selection source / Practical Validation result / Final Decision / selected monitoring log / saved mix JSONL helper와 legacy archive copy helper |
| `app/runtime/final_selected_portfolios.py` | Final Selection Decision registry를 read-only로 읽어 최종 선정 포트폴리오 운영 대시보드 row / status summary / dashboard portfolio saved state / Final Review -> Selected Dashboard handoff review / continuity check / 기간 확장 replay readiness / symbol freshness / selected provider evidence / review signal policy / replay recheck / recheck comparison / current weight 또는 value / holding input 기반 drift check / drift alert preview / allocation drift evidence boundary / monitoring timeline으로 변환 |
| `app/runtime/portfolio_store.py` | Saved portfolio persistence helper |

## App / Jobs

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/jobs/ingestion_jobs.py` | `Workspace > Ingestion`과 승인된 action facade에서 사용하는 수집 / refresh job wrapper. OHLCV, fundamentals, statement refresh, asset profile, Practical Validation provider snapshot, SEC Form 25 delisting evidence, S&P 500 universe / intraday snapshot, quote gap diagnostics, FOMC / macro / earnings calendar job을 표준 `JobResult`로 감싼다 |
| `app/jobs/overview_actions.py` | `Workspace > Overview`의 bounded refresh action facade. Overview UI 대신 market intraday snapshot, futures OHLCV, events, sentiment, quote-gap diagnostics, browser-session auto refresh, run-history append 호출을 모은다 |
| `app/jobs/overview_automation.py` | Overview market intelligence run-once automation orchestrator. `standard`, `safe`, `events`, `browser_safe` profile의 cadence, US market-hours guard, lock, run history metadata를 처리 |

## Finance Core

| 스크립트 | 관리하는 기능 |
|---|---|
| `finance/sample.py` | DB-backed strategy example / smoke 실행 함수, UI runtime이 호출하는 sample-level strategy entry |
| `finance/engine.py` | Strategy orchestration, input alignment, engine-level execution |
| `finance/strategy.py` | 실제 portfolio simulation / rebalancing logic |
| `finance/transform.py` | Strategy 공용 전처리, signal / factor / ranking transform helper |
| `finance/performance.py` | 성과 요약, portfolio performance metric, weighted portfolio 계산 helper |
| `finance/indicators.py` | Reusable indicator helper. Risk-On Momentum 5D V2 uses simple rolling True Range / ATR here instead of embedding ATR math in the strategy loop |
| `finance/swing_macro.py` | Risk-On Momentum 5D macro evaluation helper. Hard filter and ranking penalty mode share this Streamlit-free logic |
| `finance/swing_analysis.py` | Risk-On Momentum 5D V2 repeated-run analysis helper. Exit / macro / holding comparison, sensitivity, stability, trade-cause, and quality warning rows are built here |
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
| `finance/loaders/universe.py` | Universe / investability 관련 read path. asset profile status와 symbol lifecycle coverage summary를 제공 |
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
| `finance/data/nyse_db.py` | NYSE universe DB persistence. current listing master와 `nyse_symbol_lifecycle` bridge row UPSERT를 담당 |
| `finance/data/sec_delisting.py` | SEC EDGAR Form 25 / 25-NSE filing metadata를 읽어 `nyse_symbol_lifecycle` delisting_feed evidence row로 UPSERT |
| `finance/data/asset_profile.py` | Asset profile 수집. ETF operability snapshot의 bridge source로 일부 field를 제공 |
| `finance/data/market_intelligence.py` | S&P 500 current constituent parsing / 저장, S&P 500 / Top1000 / Top2000 intraday previous-close snapshot 수집 / 저장, quote gap diagnostics / issue persistence, Fed 공식 FOMC calendar parsing / 저장, BLS / BEA macro calendar 수집 및 BLS `.ics` import, yfinance earnings estimate 수집, Nasdaq earnings cross-check, earnings lifecycle cleanup, Overview market event calendar persistence helper |
| `finance/data/etf_provider.py` | ETF provider source map discovery, ETF operability / holdings / exposure snapshot schema sync, 기존 price/profile DB 기반 bridge/proxy 수집, iShares / SSGA / Invesco official row normalize, commodity gold exposure row 생성, holdings canonical refresh, exposure aggregation, UPSERT 저장 |
| `finance/data/macro.py` | FRED macro context series 수집. VIX / yield curve / credit spread series를 `macro_series_observation`에 UPSERT 저장 |
| `finance/data/fundamentals.py` | Fundamentals 수집 |
| `finance/data/financial_statements.py` | Financial statement 수집 |
| `finance/data/factors.py` | Factor 생성 / 저장 pipeline |

## Repo-Local Automation

| 스크립트 | 관리하는 기능 |
|---|---|
| `.aiworkspace/plugins/quant-finance-workflow/scripts/bootstrap_finance_phase_bundle.py` | 새 finance phase 문서 bundle 생성 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | finance diff의 docs / logs / generated artifact hygiene 점검 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | `app/services` / `app/runtime` Streamlit-free boundary, `app.web` import 금지, staged artifact guard 점검 |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py` | Current Candidate Registry list / show / validate / append helper |
| `.aiworkspace/plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py` | Pre-Live Candidate Registry template / draft / list / show / validate / append helper |

## Tests

| 스크립트 | 관리하는 기능 |
|---|---|
| `tests/test_service_contracts.py` | `app/services` / `app/runtime` contract, Practical Validation handoff, Final Review evidence read model, boundary checker behavior를 DB / Streamlit runtime 없이 검증 |

## 같이 볼 상세 문서

| 작업 종류 | 상세 문서 |
|---|---|
| Backtest UI / Candidate Review / History / Proposal | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` |
| UI payload -> runtime -> result bundle | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` |
| Data / DB / loader | `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` |
| Strategy family 추가 / 연결 | `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` |
| Repo-local helper script | `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md` |
