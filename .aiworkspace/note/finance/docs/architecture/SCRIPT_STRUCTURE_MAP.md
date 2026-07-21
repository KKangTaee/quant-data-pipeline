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
| `app/web/streamlit_app.py` | Finance Console top navigation, page entry, page-level routing. Reference는 단일 `/reference` entry만 등록한다 |
| `app/web/ingestion_console.py` + `app/web/ingestion/*` | `Workspace > Ingestion` render path. `ingestion_console.py` is a compatibility facade. `app/web/ingestion/page.py` owns the shell / session-state boundary, `registry.py` owns active vs legacy compatibility action metadata, `guides.py` owns Korean purpose-first job guide metadata, `styles.py` owns responsive CSS, `results.py` owns pure result-summary helpers, `dispatcher.py` owns UI action dispatch and read-only diagnostic job wrapping, and `sections.py` owns selected collection workbench renderers for `일상 운영 / 검증 데이터`, `수동 복구 / 진단`, `실행 기록 / 결과`. Run history/detail/log/failure artifact display remains in the records section; price / statement / PIT diagnostics still run through the shared scheduled job path and Streamlit-free diagnostic service |
| `app/services/reference_center.py` | 단일 Reference Center가 사용하는 Streamlit-free curated catalog. 6개 사용자 흐름, 상태·용어·기능 개념, 문제 해결 playbook, 검색 문자열, 관련 항목, owner 화면 destination과 drift guard를 제공한다 |
| `app/web/reference_center.py` | `/reference` page payload, 안정적인 `?item=<reference-id>` deep link, React event와 allowlisted owner 화면 navigation intent를 처리한다 |
| `app/web/reference_center_react_component.py` + `app/web/streamlit_components/reference_center_workbench/` | 검색 우선 Reference React workbench bridge와 UI. 검색·종류 filter·관련 항목·상세 drawer/sheet는 React local state가 소유하고 Python은 catalog와 navigation boundary를 소유한다 |
| `app/web/reference_contextual_help.py` | Overview, Institutional Portfolios, Ingestion, Backtest Analysis, Practical Validation, Final Review에 붙는 read-only Reference help expander와 exact item deep link render |
| `app/services/reference_contextual_help.py` | Overview부터 Final Review까지 6개 주요 workflow 화면의 contextual help catalog, surface lookup helper, Reference item / target / duplicate surface drift report |
| `app/web/overview_dashboard.py` | `Workspace > Overview`의 explicit compatibility wrapper. 현재는 기존 import path 호환을 위해 `render_overview_dashboard`만 re-export하고 active body는 `app/web/overview/page.py`로 위임한다 |
| `app/web/overview/page.py` | `Workspace > Overview` active page shell. title, market session banner, selected-tab lazy dispatch를 관리하고 primary tab entry modules로 위임한다 |
| `app/web/overview/navigation.py` | Overview primary navigation constants, query-param slug mapping, `st.pills` selector render, selected-tab dispatch helper |
| `app/web/overview/market_context.py` / `market_movers.py` / `futures_macro.py` / `sentiment.py` / `events.py` | Overview primary tab entrypoint modules. Active path는 선택된 tab의 user flow order만 소유하고, tab-local Streamlit glue는 각 `*_helpers.py`로 위임한다 |
| `app/web/overview/market_context_helpers.py` / `market_movers_helpers.py` / `futures_macro_helpers.py` / `sentiment_helpers.py` / `events_helpers.py` | Overview primary tab helper modules. Header/control/refresh branch/snapshot detail/tabpanel glue를 tab별로 소유하며, action 실행은 `app/jobs/overview_actions.py`, read-model loading은 service/helper boundary를 통해 수행한다 |
| `app/web/overview/components/*` | Overview active page / tab이 쓰는 domain visual component implementation. `common.py`는 visual token / CSS / shared strip, `layout.py`는 session banner, `market_context.py`는 cockpit / analog / source confidence / IA closeout, `market_movers.py`는 breadth / refresh status, `events.py`는 macro week / event agenda, `data_health.py`는 ingestion handoff renderer를 소유한다 |
| `app/web/overview/legacy_dashboard.py` | 삭제됨. V17-V24에서 남은 helper body를 tab-local helper modules로 옮기고 compatibility wrapper를 explicit export로 바꾼 뒤 파일을 제거했다 |
| `app/web/overview_dashboard_helpers.py` | Overview dashboard용 cached market intelligence service wrapper. Market Context, Market Movers, Events, Sentiment, Data Health, IA read model service imports를 제공한다. Candidate Ops overview snapshot helpers는 V9에서 제거했고 Candidate Ops는 Overview tab이 아니다 |
| `app/web/overview_ui_components.py` | 과거 Overview component import path 호환용 thin facade. 실제 renderer body는 `app/web/overview/components/*`에 있다 |
| `app/web/backtest_strategy_catalog.py` | Strategy display name, strategy key, family variant 선택 매핑 |
| `app/web/backtest_page.py` | Backtest page shell. React workflow top shell을 먼저 조합하고 `Backtest Analysis -> Practical Validation -> Final Review` 기존 stage dispatcher를 유지한다. 초기 Streamlit title/caption/native pills는 렌더링하지 않으며, native `pages/` auto-discovery를 피하려고 `app/web/pages/` 밖에 둔다 |
| `app/web/backtest_common.py` | Backtest 공용 preset / strategy input / real-money contract / guardrail input / strict preset basis display / Price Freshness Preflight model / legacy compatibility helper. 신규 호출은 가능한 경우 더 좁은 `backtest_state.py`, `backtest_formatters.py`, service boundary를 먼저 사용한다 |
| `app/web/backtest_state.py` | Backtest page shell이 쓰는 workflow state boundary. 기존 `backtest_common.py`의 session state / stage request helper를 compatibility wrapper로 제공해 page entry가 common module을 직접 확장하지 않게 한다 |
| `app/web/backtest_formatters.py` | Streamlit-free Backtest formatting / manual ticker parsing helper |
| `app/web/backtest_workflow_routes.py` | Backtest visible stage 3개와 legacy panel route를 매핑하는 route helper |
| `app/services/backtest_workflow_shell.py` | Streamlit-free page-level workflow shell read model. Level1~3 고정 순서, active-stage normalization, 단계별 사용자 책임과 신규·비현재 `select_stage` intent truth를 제공하며 Level 내부 Gate/count를 계산하지 않는다 |
| `app/web/backtest_workflow_shell.py` | current session을 workflow shell read model로 바꾸고 중복/invalid/current intent를 거부한 뒤 accepted stage만 기존 `request_backtest_panel()` 경계로 전달한다 |
| `app/web/backtest_workflow_shell_panel.py` | React build가 없을 때 같은 read model로 current context와 3단계 이동 button을 렌더링하는 Streamlit fallback |
| `app/web/components/backtest_workflow_shell/` | Backtest page-level React/Vite presentation bundle. headline, 현재 단계에서 끝낼 일, 3단계 rail, keyboard button / `aria-current`, desktop·760·520 responsive contract와 ResizeObserver만 소유한다 |
| `app/web/components/*/frontend/component_static/` | Backtest Analysis, Portfolio Mix, Practical Validation, Final Review 계열 13개 Streamlit React component의 canonical Vite 배포 산출물. `index.html`과 relative JS/CSS assets를 Git에 포함하므로 clean checkout은 별도 npm build 없이 로드한다. 각 `component.py`는 `component_static/index.html` 존재를 availability 기준으로 사용하며 과거 `frontend/build/`은 사용하지 않는다 |
| `app/web/backtest_analysis.py` | `Backtest > Backtest Analysis` Level1 one-shell orchestration. React `context` surface는 work fragment 밖에 고정하고 Single form/result 또는 전용 Portfolio Mix workspace만 fragment 안에서 갱신한다. Mix branch는 duplicate generic decision surface를 mount하지 않는다 |
| `app/web/backtest_analysis_workspace.py` | current session을 pure Level1 read model로 변환하고 component intent allow-list, normalized configuration fingerprint, distinct `save_mix` / `save_and_move` Python handler를 검증한다. component callback은 현재 rerun을 재사용해 중첩 app rerun 경고를 만들지 않는다 |
| `app/web/backtest_analysis_workspace_panel.py` | `backtest_analysis_decision_workspace_v1`을 소비하는 Python fallback. React가 없을 때도 같은 Single / Mix entry, decision, explicit action contract를 유지한다 |
| `app/web/components/backtest_analysis_decision_workspace/` | Level1 React/Vite presentation bundle. 고정 질문, Single / Mix entry, 목적별 strategy catalog, schema-driven Single settings, decision-first KPI / 이유 / 저장·인계 intent, 760px one-column layout와 ResizeObserver height sync만 소유한다. settings surface는 분류·validation·payload·실행을 계산하지 않는다 |
| `app/web/backtest_single_settings_workspace.py` | Python-owned Single settings runtime adapter. 현재 catalog / preset을 pure schema에 주입하고 prefill·draft를 투영하며, current selection / variant allow-list / 중복 intent / visible branch / callable handler를 검증한 뒤 기존 runner를 호출한다. React 미가용 시 같은 schema를 쓰는 generic fallback도 소유한다 |
| `app/web/backtest_single_strategy.py` | `Backtest > Single Strategy` orchestration. React catalog가 고른 strategy를 schema-driven settings surface에 연결하고 validated intent를 shared runner로 전달하며 latest result를 보존한다. strategy-specific native form dispatch, 별도 Strategy dropdown과 Strategy Detail panel은 active flow가 아니다 |
| `app/web/backtest_single_forms/` | history/replay와 compatibility 검증을 위해 남긴 legacy strategy-specific renderer. current Single primary route에서는 호출하지 않으며 신규 설정 UI 계약의 owner가 아니다 |
| `app/web/backtest_single_runner.py` | Single Strategy service-facing payload 표시, execution service 호출, normalized Level1 configuration fingerprint stamp, latest bundle state 저장, run history append. 실행 성공 자체는 Level2 handoff를 수행하지 않는다 |
| `app/web/backtest_portfolio_mix_workspace.py` | current Portfolio Mix Python adapter/runtime. intent allow-list와 nonce dedup, same Single settings payload projection, compare runner 순차 실행, weighted result atomic 교체, new-schema save/restore/rerun, distinct Level2 handoff와 fallback을 소유한다 |
| `app/web/components/backtest_portfolio_mix_workspace/` | current Portfolio Mix React/Vite presentation. `구성/공통 기준 -> 역할/비중 -> 실행/해석 -> 저장/Level2` 네 단계, saved shelf, Python 표시값 기반 KPI·누적 성과·월별 수익률·상세 근거, hover/focus intent, responsive/ResizeObserver와 접근성만 소유한다 |
| `app/web/backtest_compare/page.py` / `components.py` | legacy compare/replay compatibility surface. 기존 execution/preset/replay helper는 current adapter가 재사용할 수 있지만 primary Mix renderer는 이 Streamlit form/visual shell을 호출하지 않는다 |
| `app/web/backtest_result_display.py` | Backtest 결과 공용 display. Level1 decision / KPI / data-action 이유를 먼저 두고 chart / table / raw technical path는 접힌 `상세 근거`로 낮춘다. 설정이 바뀐 이전 성공 결과는 삭제하지 않고 참고용 stale 결과로 보존하며 Level2 인계만 차단한다. legacy Streamlit reset notice와 refresh job DataFrame은 active result route에서 렌더링하지 않는다 |
| `app/web/backtest_analysis_result_workspace.py` | `backtest_analysis_result_workspace_v1`의 current session adapter, validated intent dispatch, React / Python fallback mount를 소유한다. 실행 전에는 result surface를 만들지 않고 stale result는 참고용으로 보존한다. 가격 갱신 여부는 raw job row가 아니라 Python-owned `reference_reason`으로만 read model에 투영한다 |
| `app/web/components/backtest_analysis_result_workspace/` | Level1 결과용 React/Vite presentation bundle. KPI, 실제 날짜 tick과 pointer tooltip/crosshair가 있는 strategy/benchmark SVG, current/target holdings 일정, Level1 technical handoff, Level2 questions, evidence, user tables, 사용자용 계산·데이터 기준과 secondary raw disclosure, 760px/ResizeObserver contract만 소유한다. normalized return, Benchmark 의미, next window는 계산하지 않는다 |
| `app/web/backtest_history.py` | Hidden compatibility archive render for historical backtest run inspect / replay / form load / candidate draft handoff, Real-Money / Guardrail parity table render. Not exposed in current Operations top navigation |
| `app/web/backtest_history_helpers.py` | Backtest history row 변환, replay payload 복원, History replay parity / Real-Money scope table helper |
| `app/web/backtest_candidate_library.py` | Hidden compatibility archive render for saved current / Pre-Live 후보 inspect and stored-contract result curve rebuild. Not exposed in current Operations top navigation |
| `app/web/backtest_ui_components.py` | Backtest UI 공용 wrapping status card, artifact pipeline, compact badge strip, stage brief strip, route/readiness 판정 panel, legacy product card / stepper helper |
| `app/web/components/backtest_price_refresh_action/` | Backtest Data Trust 가격 업데이트용 React action card. 보이는 `가격 데이터 업데이트` 카드 / 버튼 / submit event만 담당하고, OHLCV 수집 실행과 session feedback은 Python path가 소유한다 |
| `app/web/components/backtest_price_freshness_preflight/` | Strict Quality / Value 계열 form-level 가격 최신성 preflight React panel. 보이는 price freshness 요약만 담당하며, Vite build asset은 Streamlit component iframe 안에서 동작하도록 relative path를 사용해야 한다 |
| `app/web/backtest_practical_validation/components.py` | Practical Validation 전용 visual shell. White square Command Center, section header, card grid, step rail, alert panel CSS / HTML helper를 제공하며 service/gate 로직은 포함하지 않는다 |
| `app/web/backtest_practical_validation/page.py` | `Backtest > Practical Validation` current visual one-shell orchestration. 후보/검증 기준 `context` surface는 replay fragment 밖에 고정하고, 최신 replay·결과/해결·저장 `decision` surface만 `@st.fragment` 안에서 갱신한다. surface별 intent allow-list와 Python validation / execution / persistence를 소유하며 Final Review route 이동만 app rerun을 사용한다 |
| `app/web/backtest_practical_validation/workspace_panel.py` | `practical_validation_decision_workspace_v1` 기반 `context / decision` two-surface Streamlit fallback과 legacy Flow 3 compatibility renderer를 소유한다. fallback Step 1도 현재 후보/판정 기준 summary 뒤에 접힌 `1A. 후보 변경`을 둔다 |
| `app/web/backtest_practical_validation/status_display.py` | Practical Validation UI status display helper. Raw route-like status를 first-read `PASS / REVIEW / NEEDS_INPUT / BLOCKED / NOT_RUN / NOT_APPLICABLE` labels / tones로 정규화한다 |
| `app/web/components/practical_validation_decision_workspace/` | current Level2 React visual one-shell bundle. 같은 read model을 `context / decision` surface로 나눠 별도 iframe mount 경계를 만들고, 고정 hero, Step 1 후보/판정 기준 summary, 접힌 후보 목록, 데스크톱 5열·760px 2열 검증 관점, Step 2 pending, non-empty lane, 5개 category 중 하나를 여는 Step 3 disclosure, ResizeObserver height sync를 담당하며 intent만 반환한다 |
| `app/web/components/practical_validation_fix_queue/`, `app/web/components/practical_validation_data_action_board/` | compatibility-only legacy React components. active first-read에서는 렌더링하지 않는다 |
| `app/web/backtest_candidate_review.py` | `Backtest > Candidate Review`의 Candidate Packaging 화면 render, Review Note / current candidate registry 저장, Pre-Live 운영 기록 저장, Portfolio Proposal 이동 판단 |
| `app/web/backtest_candidate_review_helpers.py` | Candidate Review readiness 평가, Review Note 생성, current candidate registry row 변환, Latest / History result draft 생성, Practical Validation entry gate와 strict compare gate를 분리한 handoff readiness snapshot 보존, Pre-Live status 추천 / Proposal readiness 평가, display table helper |
| `app/web/backtest_portfolio_proposal.py` | `Backtest > Portfolio Proposal`의 단일 후보 직행 평가, 다중 후보 proposal 후보 선택, 목적 / 역할 / 비중 설계, proposal draft 저장, 저장 proposal monitoring / feedback 화면 render |
| `app/web/backtest_portfolio_proposal_helpers.py` | Portfolio Proposal row 생성, 단일 후보 direct readiness / proposal save readiness 평가, 공유 validation / robustness 계산 helper, saved proposal monitoring / Pre-Live feedback / paper feedback table helper |
| `app/web/backtest_final_review/page.py` | `Backtest > Final Review`의 primary question, latest eligible candidate context, `decision_brief_v1` / candidate selector orchestration, Level2 handoff Python fallback, React candidate / observation refresh / route / reason intent 소비, 자동 Decision ID, save evaluation / append와 Monitoring handoff를 소유한다. refresh success는 새 validation stable key를 선택하고 rerun한다. current first-read는 Decision Workspace one-shell만 렌더하며 별도 Decision Desk / confirmed-report gate / Review Queue / Decision Cockpit / Evidence Appendix / Saved Decisions / 시장심리 패널을 렌더링하지 않는다 |
| `app/web/backtest_final_review/components.py` | Final Review 전용 visual shell. Command Center, flow rail, section header, lane grid, action panel CSS / HTML helper를 제공하며 service/gate/persistence 로직은 포함하지 않는다 |
| `app/web/backtest_final_review_helpers.py` | Final Review source 선택, validation 재사용, paper observation / investability packet 연결, save readiness, append row 생성 helper. 같은 active Decision Brief의 compact `decision_brief_snapshot_v1`을 row에 저장하고 기존 selected-route Gate / closure handoff를 유지한다 |
| `app/web/final_selected_portfolio_dashboard.py` | `Operations > Portfolio Monitoring` 화면 render. Legacy file name은 Selected Portfolio Dashboard를 유지한다. CNN / AAII market sentiment context overlay, 사용자 monitoring portfolio 생성 / 선택 / soft delete, Final Review selected strategy 추가 / 제거, strategy별 Snapshot / Monitoring Scenario / recheck readiness / symbol freshness / provider evidence / continuity check / source contract / Monitoring Timeline / Review Signal Policy / Open Issues / optional preflight / recheck comparison / optional Actual Allocation / allocation evidence boundary / Decision Dossier / Audit / 전환 비교 표시 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | Selected Portfolio Dashboard용 dashboard portfolio row, selected strategy pool row, strategy comparison row, handoff row, component row, continuity row, source contract row, timeline row, recheck readiness row, symbol freshness row, provider evidence row, review signal policy row, open issue follow-up row, deployment readiness row, recheck comparison row, value / holding input row, drift row, alert preview row, allocation boundary row, filter option helper. Evidence row는 service read model을 사용 |

## App / Services

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/services/backtest_single_payload.py` | Streamlit-free Single Strategy payload normalization helper. UI form payload를 execution service-facing payload로 복사 / JSON-ready 변환한다 |
| `app/services/backtest_execution.py` | Streamlit-free Single Strategy execution service. runtime dispatch, elapsed timing, input/data/system error normalization, runtime runner catalog metadata update를 담당 |
| `app/services/backtest_strategy_catalog.py` | Streamlit-free Level1 purpose group / maturity catalog. production 전략과 미완성 `Risk-On Momentum 5D` development 상태를 UI 밖에서 한 번만 분류한다 |
| `app/services/backtest_analysis_decision_workspace.py` | Streamlit-free Level1 truth / readiness / complete read model. Single / Mix 공통 configuration fingerprint, fresh / stale result, error projection, root reason dedup, handler-aware action, KPI / technical evidence 순서를 계산한다. Single current context에는 이전 실행 raw configuration을 투영하지 않고, Mix만 사용자용 구성 전략·목표 비중 요약을 제공한다 |
| `app/services/backtest_analysis_result_workspace.py` | Streamlit-free Level1 result evidence read model. `run_result_id`, lifecycle, technical handoff gate, deduplicated Level2 questions, union timeline/normalized return/Benchmark identity, 현재 평가일·최신 신호·마지막 리밸런싱·cadence·다음 월말 window, evidence/user table와 calculation/data/result-trace projection을 계산한다. 설정 변경·가격 갱신·재실행 실패를 `reference_reason` / `reference_message`로 분류하며 cadence가 없으면 exact next date를 만들지 않는다 |
| `app/services/backtest_single_settings_workspace.py` | Streamlit-free Single settings schema / validation / payload projector. 9개 user choice와 12개 primary concrete variant(legacy Quality Snapshot은 replay compatibility only)의 profile, 4개 section, field type/range/option/visibility, exact runner payload를 Python에서 한 번만 정의한다. 팩터 option은 계산용 raw `value`와 한국어 의미·표준 약어를 포함한 사용자 `label`을 분리한다 |
| `app/services/backtest_portfolio_mix_workspace.py` | Streamlit-free Portfolio Mix draft/read model. 2~4개 component, concrete strategy uniqueness, shared period, role/weight/100% validation, effective payload fingerprint, fresh/stale lifecycle, `backtest_portfolio_mix_saved_v1` shelf와 callable action projection을 소유한다. weighted result의 KPI·base-100 누적 성과·월별 수익률·기여도·계산/data trust를 사용자용 JSON-safe evidence로 포맷하며 존재하지 않는 benchmark나 holdings는 만들지 않는다 |
| `app/services/ingestion_diagnostics.py` | Streamlit-free Ingestion read-only diagnostics facade. Price window preflight, Price Stale Diagnosis, Statement Coverage Diagnosis, Statement PIT Inspection의 loader/job/source inspection calls를 UI 대신 담당 |
| `app/services/backtest_compare_execution.py` | Streamlit-free manual Compare execution service. multi-strategy execution loop, elapsed timing, input/data/system error normalization을 담당 |
| `app/services/backtest_compare_catalog.py` | Streamlit-free Compare runner catalog service. strategy별 default parameter, preset/manual universe resolution, runtime dispatch, runner signature filtering, runtime runner catalog metadata update를 담당 |
| `app/services/backtest_portfolio_mix_readiness.py` | Streamlit-free Portfolio Mix readiness helper. component role option / legacy role inference / role·weight row와 Mix Gate를 UI 밖에서 판정한다 |
| `app/services/backtest_result_read_model.py` | Streamlit-free Backtest result read model helper. strategy data trust row와 weighted component contribution view를 담당 |
| `app/services/backtest_handoff_readiness.py` | Streamlit-free Backtest Analysis -> Practical Validation handoff readiness read model. promotion signal, execution source checks, validation source checks를 policy signal inventory로 분류하고, Practical Validation entry gate와 Portfolio Mix strict compare gate의 score / blocker / review / next-action contract와 grouped gate summary를 만든다 |
| `app/services/backtest_price_refresh.py` | Streamlit-free Backtest Data Trust price refresh action model. 현재 백테스트 ticker, requested end, DB common latest date, 주말 / NYSE 휴장일 제외 최신 완료 거래일을 비교해 OHLCV 갱신 가능 여부와 수집 기간을 만들고, 실행 시 기존 `run_collect_ohlcv` job wrapper를 호출한다. Active ticker-change repair가 있으면 source ticker는 보존하고 collection ticker만 resolved symbol로 바꾸며, old/new ticker `source_range` / `resolved_range` split metadata를 plan/details에 남긴다 |
| `app/services/backtest_final_review_refresh.py` | Streamlit-free Final Review observation freshness / refresh orchestration owner. stored curve end, latest completed NYSE session, source-specific DB common date, stale / missing / provider-gap / limiting symbol을 분리하고 `up_to_date / replay_available / price_refresh_available / partial_refresh / blocked`를 만든다. refresh intent에서는 기존 price refresh와 Practical Validation replay/builder/writer를 호출해 새 validation만 append한다 |
| `app/services/backtest_weighted_portfolio.py` | Streamlit-free weighted portfolio builder service. compared strategy result bundle을 월별 weighted result bundle로 합성 |
| `app/services/backtest_saved_portfolio_replay.py` | Streamlit-free saved portfolio replay service. 저장된 mix의 strategy rerun, weighted bundle 생성, replay source / history context 조립을 담당 |
| `app/services/backtest_practical_validation.py` | Streamlit-free Practical Validation service. result 생성 wrapper, selection source / validation result append, Practical Validation / Final Review handoff contract, provider gap row / collection plan / ingestion job orchestration, downstream surface가 읽을 수 있는 read-only CNN / AAII market sentiment context overlay를 담당한다. Final Review first-read에서는 이 overlay를 렌더링하지 않는다 |
| `app/services/backtest_practical_validation_source.py` | Streamlit-free Practical Validation validation profile / selection source builder / source component table / compact selection history helper. Candidate draft, saved mix, weighted mix를 current selection source contract로 변환하고 cost / turnover / net-cost / handoff readiness snapshot / entry gate 요약을 보존 |
| `app/services/backtest_practical_validation_curve_context.py` | Streamlit-free Practical Validation curve context helper. compact curve snapshot, result curve normalize, DB price proxy curve, component curve combination, window perturbation / monthly returns 계산을 담당 |
| `app/services/backtest_practical_validation_stress_sensitivity.py` | Streamlit-free Practical Validation stress / sensitivity helper. rolling validation, stress window, baseline challenge, sensitivity interpretation, correlation risk, market context, overfit audit, Robustness Lab board를 담당 |
| `app/services/backtest_temporal_validation.py` | Streamlit-free temporal validation helper. benchmark-aligned walk-forward rolling excess return, OOS holdout excess / deterioration, macro regime split excess / drawdown gap, source strength, compact storage boundary evidence를 담당 |
| `app/services/backtest_practical_validation_diagnostics.py` | Streamlit-free Practical Validation diagnostics service. component context assembly, 12개 Practical Diagnostics result 생성, validation module / board map 결과 병합, legacy compatibility export를 담당 |
| `app/services/backtest_practical_validation_replay.py` | Streamlit-free Practical Validation replay service. 기존 strategy runtime으로 최신 DB 데이터 기준 재검증하거나 저장 기간 그대로 재현해 component / portfolio curve evidence와 replay selection history snapshot을 만든다 |
| `app/services/backtest_practical_validation_curve.py` | Streamlit-free Practical Validation curve normalize / compact records / curve provenance / benchmark parity helper |
| `app/services/backtest_practical_validation_provider_context.py` | Streamlit-free Practical Validation provider context adapter. ETF operability / holdings / exposure / FRED macro loader 결과를 compact coverage, provenance, freshness, diagnostic evidence, look-through board로 변환 |
| `app/services/backtest_practical_validation_workspace.py` | Streamlit-free Practical Validation workspace read model. result에서 gate summary, category-first criteria groups, Flow 4 `resolution_guide` action guide, display-only `data_action_board`, handoff summary, core / conditional / downstream evidence groups, technical details를 묶어 Flow 3 / Flow 4가 같은 screen-oriented contract를 읽게 한다. Flow 4 guide는 해결해야 할 항목, 번호형 `action_steps`, 통과 기준, 위치를 함께 제공한다 |
| `app/services/backtest_practical_validation_decision_workspace.py` | current Level2 pure projection. root issue dedup, verified / measured caution / validated caution / resolve-now / engineering-required / Final Review handoff 분리, top-level `validation_result_id`, state machine과 summary counts를 소유한다. measured caution은 validated caution에만 적용하며 accepted limit / final decision / monitoring transfer는 측정값이 있어도 handoff class를 유지한다 |
| `app/services/backtest_practical_validation_explanation.py` | Practical Validation audit row를 사용자 언어의 검증명 / 상태 / 확인 내용 / 결과 / 의미 / 다음 행동으로 변환하는 pure service. data/bias, validation method, portfolio structure, realism/cost, stress/robustness 5개 category mapping과 secondary `technical_trace`를 소유한다 |
| `app/services/backtest_validation_status_policy.py` | Streamlit-free validation status policy. `PASS / READY / REVIEW / NOT_RUN / NEEDS_INPUT / BLOCKED` normalization과 rank를 소유한다 |
| `app/services/backtest_practical_validation_modules.py` | Streamlit-free Practical Validation module planner. source traits와 profile / input checks / diagnostics / audit rows를 읽어 필수 / 조건부 / 후속 참고 module, gate effect, gate reason, Final Review 이동 gate, evidence board 연결과 `verified / computed / missing / not_applicable` evidence state를 만든다. Status normalization은 `backtest_validation_status_policy.py`를 사용한다 |
| `app/services/backtest_practical_validation_board_registry.py` | Streamlit-free Practical Validation board registry. 화면 보드가 어떤 validation module을 설명하는지, 현재 후보에 적용되는지, 어떤 gate effect를 갖는지 board map으로 변환 |
| `app/services/backtest_construction_risk_audit.py` | Streamlit-free construction risk audit read model. Practical Validation metrics와 provider look-through board를 읽어 component concentration, provider coverage, top holding, holdings overlap, asset bucket exposure를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 변환 |
| `app/services/backtest_risk_contribution_audit.py` | Streamlit-free risk contribution audit read model. Practical Validation의 component return matrix, correlation, max risk contribution proxy, drop-one dependency, storage boundary evidence를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 변환 |
| `app/services/backtest_component_role_weight_audit.py` | Streamlit-free component role / weight audit read model. Practical Validation의 proposal role, target weight, validation profile, role concentration, profile intent, weight reason evidence를 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` row로 변환 |
| `app/services/backtest_evidence_read_model.py` | Streamlit-free evidence read model service. investability packet / gate policy / decision guide / saved review / decision dossier와 legacy candidate board / scorecard / investment report compatibility payload를 유지한다. current Decision Workspace projection owner는 아니다 |
| `app/services/backtest_final_review_decision_brief.py` | Streamlit-free current Final Review projection owner. stored curve → exact-common behavior, measured-only observation / finding / trait, structured Monitoring condition, canonical route capability와 Level2 `final_decision / accepted_limit / monitoring_transfer` root-dedup handoff를 `decision_brief_v1`으로 만들고 chart bulk를 제외한 `decision_brief_snapshot_v1`을 제공한다 |
| `app/services/backtest_final_review_policy.py` | Streamlit-free Final Review selected-route policy boundary. investability evidence packet을 selected-route preflight contract로 변환한다 |
| `app/services/overview/*` | Overview UI-facing domain service implementation modules. `economic_cycle.py` owns compact DB month-end snapshot/history, exact-baseline intramonth comparison, and stable LIMITED/ERROR contract, `market_context.py` owns retained cockpit / source confidence composition, `market_movers.py` owns movers / group leadership / breadth / date windows, `events.py` owns market event calendar / macro week lane, `sentiment.py` owns CNN / AAII sentiment, `data_health.py` owns collection ops / ingestion handoff, `why_it_moved.py` owns catalyst links / compact metadata, and `ia.py` owns the closeout guide |
| `app/services/overview_market_intelligence.py` | 삭제됨. Overview service 구현과 내부 import는 `app/services/overview/*` domain modules를 직접 사용한다 |

## App / Runtime

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/runtime/backtest/__init__.py` / `facade.py` | UI payload를 DB-backed backtest 실행으로 변환하는 public runtime compatibility facade와 price-only ETF family runtime wrappers. Result bundle, Risk-On Momentum, Real-Money helper, Strict quality / value family 구현은 전용 module로 위임하고 기존 `app.runtime.backtest` import path를 re-export한다 |
| `app/runtime/backtest/runners/risk_on_momentum.py` | Risk-On Momentum 5D runtime slice. managed universe resolution, DB price / statement / futures macro load, swing execution, comparison / sensitivity / stability wiring, generated swing artifact writer를 담당하며 `app.runtime.backtest`가 compatibility export한다 |
| `app/runtime/backtest/real_money.py` | Backtest real-money / guardrail / benchmark / deployment readiness helper slice. constants, ticker normalization compatibility helper, cost / turnover postprocess, benchmark overlay, validation / promotion / shortlist / probation / monitoring / deployment readiness contracts, ETF operability policy, `_apply_real_money_hardening`을 담당하며 `app.runtime.backtest`가 compatibility export한다 |
| `app/runtime/backtest/runners/strict_factor.py` | Strict quality / value / quality-value annual and quarterly runtime slice. strict price freshness, factor / statement snapshot preflight, dynamic universe handling, rejected slot handling, strict result metadata assembly를 담당하며 `app.runtime.backtest`가 compatibility export한다 |
| `app/runtime/backtest/result_bundle.py` | Backtest runtime result bundle contract helper. `result_df`를 정렬하고 summary / chart / metadata bundle을 생성하며 `app.runtime.backtest` public export와 호환된다 |
| `app/runtime/backtest/runner_catalog.py` | Runtime strategy runner ownership catalog. strategy key / display name / runtime module / runtime family metadata를 제공하며 execution / compare service가 result bundle meta에 소유권 정보를 붙인다 |
| `app/runtime/backtest/read_models/candidate_library.py` | Candidate Library용 registry join, 후보 table row, replay payload 생성, ETF / strict annual equity 후보 replay runtime dispatch helper |
| `app/runtime/backtest/stores/candidate_registry.py` | current candidate, candidate review note, pre-live registry JSONL path / load / append helper |
| `app/runtime/backtest/stores/run_history.py` | Backtest run history persistence helper |
| `app/runtime/backtest/stores/portfolio_proposal.py` | Portfolio proposal draft registry JSONL path / load / append helper |
| `app/runtime/backtest/stores/paper_portfolio_ledger.py` | Paper Portfolio Tracking Ledger JSONL path / load / append helper |
| `app/runtime/backtest/stores/final_selection_decisions.py` | Final Portfolio Selection Decision JSONL path / load / append helper |
| `app/runtime/backtest/stores/portfolio_selection.py` | current workflow portfolio selection source / Practical Validation result / Final Decision / selected monitoring log / saved mix JSONL helper와 legacy archive copy helper |
| `app/runtime/backtest/read_models/final_selected_portfolios.py` | Final Selection Decision registry를 read-only로 읽어 운영 대시보드 / handoff / continuity / recheck / drift / timeline으로 변환한다. Monitoring trigger는 compact Decision Brief structured condition을 우선 표시하고 snapshot 없는 legacy row만 paper trigger string으로 fallback한다 |
| `app/runtime/backtest/stores/portfolio_store.py` | Saved portfolio persistence helper |

## App / Jobs

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/jobs/ingestion_jobs.py` + `app/jobs/ingestion/common.py` | `Workspace > Ingestion`과 승인된 action facade에서 사용하는 수집 / refresh job wrapper. `ingestion_jobs.py` wraps OHLCV, legacy fundamentals compatibility, EDGAR statement refresh, asset profile, Practical Validation provider snapshot, SEC Form 25 delisting evidence, S&P 500 universe / intraday snapshot, S&P 500 valuation context, quote gap diagnostics, FOMC / macro / earnings calendar jobs as standard `JobResult`; 경제 사이클은 explicit vintage collection과 DB-only current materialization entry를 제공하되 scheduler/UI 진단 panel에는 등록하지 않는다. `app/jobs/ingestion/common.py` owns symbol parsing, normalized result creation, progress event helpers, execution profile resolution, and pipeline status helpers |
| `app/jobs/overview_actions.py` | `Workspace > Overview`의 bounded refresh action facade. Overview UI 대신 market intraday snapshot, futures OHLCV, events, sentiment, quote-gap diagnostics, browser-session auto refresh, run-history append 호출을 모은다. Market Context refresh bundle은 S&P 500 movers, sentiment, event calendars만 소유하며 Top1000 / Top2000 / Futures refresh는 전용 Market Movers / Futures Macro / Ingestion 흐름에 둔다 |
| `app/jobs/economic_cycle_refresh.py` | 경제사이클 평일 fail-closed refresh. 17-series overlap 증분 수집이 모두 성공한 뒤 누락 직전 월말 append-only rollover와 당일 `intramonth_nowcast` materialization을 실행하며 실패 시 last-good를 유지한다 |
| `app/jobs/overview_automation.py` | Overview market intelligence run-once automation orchestrator. `standard`, `safe`, `events`, `browser_safe` profile의 cadence, weekday / US market-hours guard, lock, run history metadata를 처리한다. 경제사이클 월중 job은 `safe/standard/broad`에만 등록하고 `browser_safe`에서는 실행하지 않는다 |

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
| `finance/economic_cycle_catalog.py` / `economic_cycle_features.py` / `economic_cycle_labels.py` | 17-series 역할/변환 계약, leakage-safe 월별 factor, activity/labor+eligible USREC retrospective label |
| `finance/economic_cycle_model.py` / `economic_cycle_validation.py` / `economic_cycle_pipeline.py` / `economic_cycle_interpretation.py` | horizon별 확률 모델·transition prior·temperature calibration·rolling-origin publication gate·artifact/snapshot orchestration·시장 맥락 해석. Pipeline은 계산 가능한 LIMITED artifact를 잠정 확률로 materialize하되 validation status를 변경하지 않으며, exact artifact 기반 월중 partial-origin materialization과 closed-month append-only rollover를 제공한다 |

## Finance Loaders

| 스크립트 | 관리하는 기능 |
|---|---|
| `finance/loaders/price.py` | DB price history / price matrix / freshness / latest per-symbol price read path |
| `finance/loaders/provider.py` | Practical Validation provider snapshot read path. ETF operability, ETF holdings, ETF exposure snapshot loader를 제공 |
| `finance/loaders/macro.py` | Practical Validation market-context read path. FRED macro series observation과 기준일 snapshot / staleness loader를 제공 |
| `finance/loaders/economic_cycle.py` | FRED/ALFRED revision interval의 strict as-of selection, coverage, approved artifact, compact current/history snapshot DB read path |
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
| `finance/data/economic_cycle_vintages.py` / `finance/data/economic_cycle_results.py` | 경제 사이클 raw vintage full/overlap 증분 수집·revision UPSERT와 model artifact/current·replay·intramonth compact snapshot persistence |
| `finance/data/sp500_valuation.py` / `finance/loaders/sp500_valuation.py` | Shiller monthly valuation(price-only 최신 월 포함), optional S&P index earnings release vintage, Federal Reserve SEP latest/calendar-discovered history vintage 수집·UPSERT와 DB read. loader는 5년 display+60개월 rolling warmup용 120개월 rows, 최신 actual As-Reported 네 분기 TTM 또는 Shiller interpolated TTM EPS, 1/3/5년 reconstruction용 전체 SEP vintage를 제공한다 |
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
| `tests/test_service_contracts.py` | `app/services` / `app/runtime` contract, Practical Validation handoff, Final Review evidence read model, Overview structure / boundary guard, boundary checker behavior를 DB / Streamlit runtime 없이 검증 |
| `tests/test_backtest_evidence_closure.py` | root issue dedup, action handler, eligibility, GRS market-date contract, survivorship applicability, terminal-state finalization, measured-only score 계약 검증 |
| `tests/test_backtest_practical_validation_decision_workspace.py` | Level2 truth/applicability, closure class counts, action handler, state/read-model dedup, measured caution, stable validation id 계약 검증 |
| `tests/test_practical_validation_market_context_visual_contract.py` | four-step order, Level3-compatible visual token, zero-action lane omission, 760px layout, ResizeObserver 계약 검증 |

## Backtest Evidence Closure

| 스크립트 | 관리하는 기능 |
|---|---|
| `app/services/backtest_evidence_closure.py` | stored validation을 root issue로 정규화하고 actionability, criticality, Gate, terminal state, Final Review closure snapshot을 계산하는 pure service |
| `app/services/backtest_practical_validation_replay.py` | whole-DB requested date와 source common date를 분리하고 기존 Python runtime replay를 실행 |
| `finance/transform.py`, `finance/sample.py`, `finance/strategy.py` | GRS month-end signal과 latest-common valuation row를 분리해 가짜 rebalance를 방지 |
| `app/services/backtest_evidence_read_model.py` | root closure issue를 Final Review report, measured-only score impact, unresolved/accepted section으로 변환 |

## 같이 볼 상세 문서

| 작업 종류 | 상세 문서 |
|---|---|
| Backtest UI / Candidate Review / History / Proposal | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` |
| UI payload -> runtime -> result bundle | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` |
| Data / DB / loader | `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md` |
| Strategy family 추가 / 연결 | `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` |
| Repo-local helper script | `.aiworkspace/note/finance/docs/runbooks/AUTOMATION_SCRIPTS.md` |
