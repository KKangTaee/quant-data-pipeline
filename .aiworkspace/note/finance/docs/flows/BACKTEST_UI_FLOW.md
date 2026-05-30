# Web Backtest UI Flow

Status: Active
Last Verified: 2026-05-30

## 목적

이 문서는 Streamlit Backtest 화면의 single strategy, Portfolio Mix Builder, candidate review, Pre-Live 운영 기록, portfolio proposal, final review, Operations-owned backtest history, Candidate Library, saved weighted portfolio 흐름을 설명한다.
UI form, payload 복원, candidate review, history replay, candidate replay, saved weighted portfolio replay를 수정할 때 먼저 확인한다.

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `app/web/streamlit_app.py` | top navigation과 page entry |
| `app/web/reference_guides.py` | `Reference > Guides`의 제품형 workflow guide, portfolio flowchart, decision gates, reference drawer |
| `app/web/ops_review.py` | `Operations > Ops Review`의 triage flow, 웹앱 run health, action inbox, failure artifact, log, system snapshot dashboard |
| `app/web/overview_dashboard.py` | `Workspace > Overview`에서 Market Movers, Sector / Industry, Events, Data Health, Candidate Ops dashboard render. Market session banner, daily snapshot refresh action bar, browser-session auto refresh heartbeat, Sector / Industry ranking/trend, Events agenda/calendar/quality/raw views를 조정한다 |
| `app/web/overview_dashboard_helpers.py` | Overview dashboard용 current candidate / Pre-Live / proposal / history / saved portfolio 집계, candidate priority scoring, cached market intelligence service wrapper |
| `app/web/overview_ui_components.py` | Overview 전용 visual token, Market Movers refresh surface / metadata strip, Events summary/source/agenda/calendar/quality components, market session banner render |
| `app/services/overview_market_intelligence.py` | Streamlit-free Overview market intelligence service. S&P 500 / Top1000 / Top2000 movers, yearly period, Sector / Industry leadership ranking/trend/ticker leaders, intraday snapshot read path, missing diagnostics, event calendar snapshot, collection ops snapshot을 만든다 |
| `app/web/backtest_common.py` | Backtest 공용 preset, session state, 3단계 stage routing compatibility, universe / real-money / guardrail input, status label helper |
| `app/web/backtest_workflow_routes.py` | `Backtest Analysis`, `Practical Validation`, `Final Review` visible stage와 legacy panel route mapping |
| `app/web/backtest_analysis.py` | `Backtest Analysis` stage wrapper. Single Strategy와 Portfolio Mix Builder를 submode로 렌더링 |
| `app/web/backtest_single_strategy.py` | `Single Strategy` 화면 orchestration. strategy 선택, prefill notice, form dispatch, latest result 연결 |
| `app/web/backtest_single_forms.py` | Single Strategy strategy-specific form render. Equal Weight, GTAA, GRS, Risk Parity, Dual Momentum, Quality / Value 계열 |
| `app/web/backtest_single_runner.py` | Single Strategy payload 표시, execution service 호출, latest bundle state 저장, run history append |
| `app/services/backtest_execution.py` | Streamlit-free Single Strategy execution service. DB-backed runtime dispatch와 input/data/system error normalization 담당 |
| `app/services/backtest_compare_execution.py` | Streamlit-free manual Compare execution service. 여러 전략 실행 loop와 input/data/system error normalization 담당 |
| `app/services/backtest_compare_catalog.py` | Streamlit-free Compare runner catalog service. 전략별 default / universe resolution / runtime dispatch 담당 |
| `app/services/backtest_result_read_model.py` | Streamlit-free Backtest result read model helper. data trust row와 weighted component contribution view 담당 |
| `app/services/backtest_weighted_portfolio.py` | Streamlit-free weighted portfolio builder service. component 실행 결과 bundle을 weighted portfolio result bundle로 합성 |
| `app/services/backtest_saved_portfolio_replay.py` | Streamlit-free saved portfolio replay service. 저장된 mix의 strategy rerun / weighted bundle / replay context 조립 담당 |
| `app/web/backtest_compare.py` | `Portfolio Mix Builder` 화면 render, component portfolio 실행 / weighted portfolio / saved replay service 호출, saved portfolio load, mix candidate handoff |
| `app/web/backtest_result_display.py` | Backtest 결과 공용 display. summary, chart, data trust, real-money detail, selection history, compare result helper |
| `app/web/backtest_history.py` | `Operations > Backtest Run History` 화면 render, selected record inspect, run again / load into form / candidate draft handoff |
| `app/web/backtest_history_helpers.py` | History table row, replay payload, replay parity, Real-Money / Guardrail scope helper |
| `app/web/backtest_candidate_library.py` | `Operations > Candidate Library` 화면 render. 저장된 current / Pre-Live 후보 inspect와 저장 contract 기반 result curve rebuild |
| `app/runtime/candidate_library.py` | Candidate Library registry join, table row, replay payload 생성, ETF / strict annual equity 후보 replay runtime dispatch helper |
| `app/web/pages/backtest.py` | Backtest page entry, workflow navigation, panel dispatch shell. 주요 panel 본문은 `app/web/backtest_*.py` module이 담당 |
| `app/web/backtest_ui_components.py` | Backtest UI 공용 status card, artifact pipeline, compact badge strip, stage brief strip, route/readiness panel, legacy product card / stepper render helper |
| `app/web/backtest_practical_validation_components.py` | Practical Validation 전용 workbench visual shell. Command Center, section header, card grid, step rail, alert panel helper를 제공하며 검증 로직과 저장 계약은 갖지 않는다 |
| `app/services/backtest_practical_validation.py` | Streamlit-free Practical Validation service. source/result 저장, Practical Validation / Final Review handoff contract, Provider Data Gaps row / collection plan / ingestion job orchestration을 만든다 |
| `app/services/backtest_practical_validation_source.py` | Streamlit-free validation profile / selection source builder / source component table helper. Candidate draft, saved mix, weighted mix를 Clean V2 source로 변환한다 |
| `app/services/backtest_practical_validation_curve_context.py` | Streamlit-free curve context helper. compact curve snapshot, curve normalize, DB price proxy, component curve combination, window perturbation / monthly returns 계산을 맡는다 |
| `app/services/backtest_practical_validation_stress_sensitivity.py` | Streamlit-free stress / sensitivity helper. rolling validation, stress window, baseline challenge, sensitivity 해석, correlation risk, market context, overfit audit를 맡는다 |
| `app/services/backtest_temporal_validation.py` | Streamlit-free temporal validation helper. benchmark-aligned walk-forward rolling excess return, OOS holdout excess / deterioration, macro regime split excess / drawdown gap, source strength, compact storage boundary evidence를 만든다 |
| `app/services/backtest_practical_validation_diagnostics.py` | Streamlit-free Practical Validation diagnostics service. component context assembly, 12개 Practical Diagnostics result, validation module plan, board map, final review gate, compatibility export를 만든다 |
| `app/services/backtest_practical_validation_modules.py` | Streamlit-free Practical Validation module planner. source traits와 profile / input checks / diagnostic / audit rows를 읽어 필수 / 조건부 / 후속 참고 module, gate effect, gate reason, evidence board 연결, Final Review 이동 gate를 만든다 |
| `app/services/backtest_practical_validation_board_registry.py` | Streamlit-free Practical Validation board registry. 화면 보드가 어떤 validation module의 evidence인지, 현재 후보에 적용되는지, 어떤 gate effect를 갖는지 매핑한다 |
| `app/services/backtest_practical_validation_replay.py` | Streamlit-free Practical Validation replay service. 기존 strategy runtime 재검증 계획과 actual replay result를 만든다 |
| `app/services/backtest_practical_validation_curve.py` | Streamlit-free Practical Validation curve normalize, compact curve records, curve provenance, benchmark parity helper |
| `app/services/backtest_practical_validation_provider_context.py` | Streamlit-free P2 provider context adapter. DB에 저장된 ETF operability / holdings / exposure / FRED macro snapshot을 compact coverage / provenance / freshness evidence와 look-through board로 바꿔 Practical Diagnostics에 연결 |
| `app/services/backtest_construction_risk_audit.py` | Streamlit-free Construction Risk Audit. Practical Validation metrics와 provider look-through board를 읽어 component concentration, provider coverage, top holding, holdings overlap, asset bucket exposure를 compact audit row로 표시 |
| `app/services/backtest_risk_contribution_audit.py` | Streamlit-free Risk Contribution Audit. Practical Validation component curve / correlation diagnostic과 Robustness Lab drop-one dependency를 읽어 component return matrix coverage, pairwise correlation, max risk contribution proxy, source strength, storage boundary를 compact audit row로 표시 |
| `app/services/backtest_component_role_weight_audit.py` | Streamlit-free Component Role / Weight Audit. Practical Validation selection source의 proposal role, target weight, validation profile, profile intent, weight reason을 읽어 role / weight discipline을 compact audit row로 표시 |
| `app/services/backtest_validation_efficacy.py` | Streamlit-free Validation Efficacy audit read model. Practical Validation의 기존 compact evidence를 읽어 runtime replay, period coverage, benchmark parity, walk-forward temporal validation, OOS holdout validation, regime split validation, provider freshness, robustness, PIT / look-ahead, survivorship / universe, execution / storage boundary gap을 분리한다 |
| `app/services/backtest_data_coverage_audit.py` | Streamlit-free Data Coverage audit read model. DB price window, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 compact row로 분리한다 |
| `app/services/backtest_realism_audit.py` | Streamlit-free Backtest Realism audit read model. Practical Validation의 기존 result metadata와 compact evidence를 읽어 거래비용, net cost curve, turnover, cost / slippage sensitivity, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary gap을 분리한다 |
| `app/web/backtest_practical_validation.py` | `Practical Validation` stage render. Clean V2 source 확인, 검증 프로필 입력, 최신 DB 데이터 기준 runtime 재검증 실행 버튼, 전용 workbench shell 기반 Control Center, Fix Queue, summary-first `검증 근거 보드`, Provider Action Center, 저장 / Final Review 이동, service handoff 결과의 session state 반영을 담당 |
| `app/web/backtest_candidate_review.py` | Candidate Review / Candidate Packaging / Pre-Live 운영 기록 화면 render logic |
| `app/web/backtest_candidate_review_helpers.py` | Candidate Review 판단, Review Note / registry 변환, Pre-Live status 추천 / draft 변환 / Portfolio Proposal 진입 readiness score helper |
| `app/web/backtest_portfolio_proposal.py` | 단일 후보 직행 평가, 다중 후보 Portfolio Proposal 후보 선택 / 목적 / 역할 / 비중 설계, proposal draft 저장, 저장된 proposal monitoring / feedback section render logic |
| `app/web/backtest_portfolio_proposal_helpers.py` | Portfolio Proposal row 생성, 단일 후보 direct readiness / proposal save readiness 평가, 공유 validation / robustness 계산 helper, monitoring / Pre-Live / paper feedback table helper |
| `app/services/backtest_evidence_read_model.py` | Streamlit-free final decision evidence read model. Final Review investability evidence packet / selected-route gate / saved decision status / table row, Selected Dashboard evidence check row, Decision Dossier markdown read model과 selected decision source contract를 공통으로 만든다 |
| `app/web/backtest_final_review.py` | Final Review 화면 render. 단일 후보 / 저장 proposal 선택, Validation / Robustness / Paper Observation / Investability Evidence Packet 기준 확인, 최종 판단 기록, saved final decision review, Decision Dossier download |
| `app/web/backtest_final_review_helpers.py` | Final Review source 선택, validation 재사용, inline paper observation snapshot, investability packet 연결, final evidence / save readiness / decision row helper |
| `app/web/final_selected_portfolio_dashboard.py` | `Operations > Selected Portfolio Dashboard` 화면 render. Final Review에서 선정된 포트폴리오를 운영 대상으로 읽고 compact selected portfolio picker / Snapshot / tabbed Performance Recheck / recheck operations preflight / recheck readiness / symbol freshness / provider evidence / Final Review -> dashboard continuity check / source contract / Portfolio Monitoring Timeline / Review Signals / recheck comparison / optional Actual Allocation / allocation evidence boundary / Decision Dossier / Audit을 보여준다 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | Selected Portfolio Dashboard의 table / component / continuity / source contract / recheck preflight / recheck readiness / symbol freshness / provider evidence / recheck comparison / value / holding input / drift / alert preview / allocation boundary / filter helper. Evidence table은 service read model을 표시한다 |
| `app/runtime/backtest.py` | UI payload를 실행 가능한 runtime call로 변환 |
| `app/runtime/backtest_result_bundle.py` | Backtest runtime 결과를 UI가 읽는 summary / chart / metadata bundle로 변환 |
| `app/runtime/candidate_registry.py` | current candidate / review note / pre-live registry JSONL read / append helper |
| `app/runtime/portfolio_proposal.py` | portfolio proposal draft JSONL read / append helper |
| `app/runtime/paper_portfolio_ledger.py` | paper portfolio tracking ledger JSONL read / append helper |
| `app/runtime/final_selection_decisions.py` | final portfolio selection decision JSONL read / append helper |
| `app/runtime/portfolio_selection_v2.py` | Clean V2 selection source, practical validation result, Final Decision V2, selected monitoring log, saved mix JSONL helper |
| `app/runtime/final_selected_portfolios.py` | final selection decision registry를 read-only dashboard row, continuity check, selected component replay recheck, component contribution, optional Allocation Check / drift preview / allocation drift evidence boundary로 변환하는 Phase36 helper |
| `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl` | local run history. 보통 commit하지 않음 |
| `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl` | saved portfolio persistence |
| `.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | proposal draft persistence. 첫 proposal 저장 시 생성 |
| `.aiworkspace/note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | paper tracking ledger persistence. 첫 paper ledger 저장 시 생성 |
| `.aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl` | Clean V2 Backtest Analysis source persistence. 첫 후보 source 선택 시 생성 |
| `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` | Clean V2 Practical Validation result persistence. 첫 검증 결과 저장 시 생성 |
| `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | Clean V2 final selection decision persistence. 첫 final decision 저장 시 생성 |
| `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | 선정 이후 optional monitoring check record. 자동 생성하지 않고 명시 저장이 필요할 때만 사용 |

## 화면 흐름

Backtest page는 후보 선정 주 흐름만 보여준다.

Backtest 주 흐름:

- `Backtest Analysis`: Single Strategy 또는 Portfolio Mix Builder로 1차 후보 source를 만들고 `PORTFOLIO_SELECTION_SOURCES.jsonl`에 Clean V2 source로 저장한다. Portfolio Mix Builder는 여러 component portfolio를 실행하고 weight를 정해 하나의 mix 후보로 만든다. 화면은 `Component 실행 -> Weight 구성 -> Mix 후보 판단 -> Practical Validation` 순서로 읽히며, component 실행 결과는 compact card와 `요약 / 차트 / 진단 / 상세` 탭으로 먼저 보여주고 원본 summary / criteria / meta는 접힘 상세로 낮춘다.
- `Practical Validation`: 선택된 단일 전략 후보 / Portfolio Mix 후보 source를 실전 투입 전 조건으로 검증한다. 사용자는 방어형 / 균형형 / 성장 / 공격형 / 전술·헤지형 / 사용자 지정 profile과 5개 답변을 고른다. 화면은 전용 workbench shell에서 후보 / profile / latest replay / gate를 먼저 요약하고, `4. Final Review Gate / 검증 모듈`의 Fix Queue로 이동 차단 항목을 카드형으로 보여준다. `5. 검증 근거 보드`는 summary-first Evidence Workspace로, Input Evidence, audit board, Practical Diagnostics, Provider Coverage, Look-through Exposure Board, Robustness Lab, Curve evidence를 탭과 접힘 상세로 나눠 보여준다. `6. 보강 액션`은 Provider Action Center로 Provider Data Gaps, 수집 가능 항목, connector 보강 필요 항목, 수집 / 보강 버튼을 분리해서 보여주며, `7. 저장 & Final Review 이동`에서 저장과 이동을 수행한다. 각 화면 보드는 board registry를 통해 Required / Conditional / Reference module과 연결되며, 단일 component 후보의 mix 전용 board처럼 적용되지 않는 보드는 비적용으로 분리한다. 결과는 `PRACTICAL_VALIDATION_RESULTS.jsonl`에 저장하며 사용자 최종 메모는 받지 않는다.
- `Final Review`: Practical Validation result와 diagnostics 요약, Construction Risk, Risk Contribution, Component Role / Weight, Validation Efficacy, Data Coverage, Backtest Realism, Robustness / Paper Observation / Investability Evidence Packet을 한 화면에서 확인하고, profile-aware `Validation Gate Policy`로 selected-route 가능 여부를 판정한 뒤 최종 선정 / 보류 / 거절 / 재검토 판단을 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 저장한다. critical gap, Construction Risk / Risk Contribution / Component Role / Weight `NEEDS_INPUT` / `BLOCKED`, Validation Efficacy `NEEDS_INPUT` / `BLOCKED`, walk-forward / OOS / regime row-level `NEEDS_INPUT` / `BLOCKED`, Data Coverage `NEEDS_INPUT` / `BLOCKED`, Backtest Realism `NEEDS_INPUT` / `BLOCKED`, selected-route policy blocker가 남아 있으면 `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장은 차단하지만, 보류 / 거절 / 재검토 판단은 기록할 수 있다. Construction risk 계열과 Validation Efficacy row-level `REVIEW`는 선정 전 hold / re-review 요구로 표시한다. Structured waiver는 현재 UI / persistence가 없고, future policy도 `BLOCK` waiver를 허용하지 않는다. 저장된 최종 판단은 read-only Decision Dossier markdown으로 다운로드할 수 있지만 report 파일을 자동 생성하지 않는다.

Backtest Analysis 1단계 closeout 기준은 [BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md](./BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md)에 둔다. 이 문서는 이번 세션에서 정리한 Real-Money 1차 readiness, Practical Validation handoff gate, Portfolio Mix Builder 재정의, Mix 후보 판단 UI, 저장 경계를 요약한다.

Practical Validation V2의 현재 구현은 최소 contract를 Input Evidence로 읽고, profile-aware practical diagnostics board를 만든다.
`practical-validation-module-gate-v1`부터 Practical Validation result에는 `source_traits`, `validation_modules`, `validation_module_summary`, `final_review_gate`가 붙는다. module planner는 source kind, component count, target weights, strategy key, universe symbols, replay contract, profile, input checks, diagnostic rows, audit rows를 읽어 필수 검증 / 조건부 검증 / 후속 참고를 분리한다. 필수 module의 `BLOCKED` / `NEEDS_INPUT` / `NOT_RUN`은 `저장하고 Final Review로 이동`을 막고, `REVIEW`는 `READY_WITH_REVIEW`로 Final Review에서 확인할 근거로 넘긴다. module row는 `Gate Effect`와 `Gate Reason`으로 이동 차단 / Final Review 확인 / 후속 참고 여부를 명시한다. 조건부 module은 source traits에 맞을 때만 적용하며, 단일 ETF-like 후보에는 weighted-mix 전용 risk contribution / component role module을 `NOT_APPLICABLE`로 낮춘다.

`practical-validation-board-map-v1`부터 Practical Validation result에는 `validation_board_map`, `validation_board_display_rows`, `applied_validation_board_display_rows`, `not_applicable_validation_board_display_rows`가 붙는다. 이 map은 검증 module taxonomy와 화면 board taxonomy를 분리한다. module은 검증 의미와 gate owner이고, board는 사용자에게 보이는 evidence 묶음이다. UI는 `4. Final Review Gate / 검증 모듈`에서 module list와 Fix Queue를 먼저 보여주고, Applied Validation Map은 보조 `검증-근거 연결 지도`로 접어 둔다. 각 evidence / action board title 아래에는 `Board Type`, `Applies`, `Feeds`, `Gate` badge를 표시한다.
Final Review Gate의 blocker / review module table은 내부 module id 대신 `Module`, `Status`, `Fix Location`, `Fix Action`, `Gate Effect`, `Gate Reason`을 먼저 보여준다. 예를 들어 `latest_replay` blocker는 `3. 최신 데이터 기준 전략 재검증`에서 `전략 재검증 실행` 후 Recheck / Coverage를 확인하라고 안내한다.
`practical-validation-required-module-polish-v1`부터 사용자-facing benchmark module label은 `Benchmark / Comparator Parity`다. 내부 input check key는 backward compatibility를 위해 `Benchmark parity`를 유지하지만, 해석은 benchmark, cash, simple baseline, custom comparator 같은 비교 기준의 기간 / coverage / frequency 동등성으로 확장한다.
현재 board는 compact curve snapshot 또는 DB price proxy curve를 사용해 rolling validation, stress window 구간 성과, simple baseline challenge, component correlation / risk contribution proxy, window / drop-one / weight perturbation sensitivity를 계산한다.
Stress / Sensitivity Interpretation은 계산된 숫자를 그대로 두지 않고, covered stress 중 daily replay가 필요한 구간, worst MDD / benchmark spread, rolling / window / component dependency / weight tilt / strategy runtime follow-up을 별도 해석 row로 요약한다.
P2-5B부터 ETF asset allocation / concentration / leveraged-inverse / operability와 macro / sentiment 진단은 DB에 저장된 provider snapshot을 우선 사용하고, 없으면 proxy origin을 `REVIEW`로 남긴다.
provider snapshot 조회 기준일은 저장된 backtest 종료일이 아니라 Practical Validation 실행일이다. 저장된 mix의 backtest 기간이 과거에 끝나도, 실전 투입 전 검증은 현재 수집된 ETF 운용성 / holdings / macro context로 확인한다.
`data-provenance-coverage-v1`부터 Provider Coverage 표는 coverage status뿐 아니라 source mix, freshness, as-of range를 함께 보여준다. ETF provider snapshot이 오래됐으면 충분한 coverage라도 `PASS`가 아니라 `REVIEW`로 남긴다.
`look-through-exposure-board-v1`부터 Provider Coverage 아래에 Look-through Exposure Board를 표시한다. 이 board는 holdings / exposure snapshot을 portfolio weight 기준으로 접어 asset bucket, top holdings, overlap, ETF별 coverage를 보여주며, full holdings row는 DB에만 둔다.
`robustness-lab-v1`부터 Stress / Sensitivity Interpretation은 Robustness Lab board로 표시한다. 이 board는 stress coverage, worst stress, sensitivity coverage, worst sensitivity delta, rolling validation, local overfit audit를 compact summary로 묶고, Final Review와 final decision evidence read model이 같은 summary row를 읽는다. Raw run history와 strategy-specific perturbation artifact는 workflow JSONL에 저장하지 않는다.
`validation-efficacy-hardening-v1`부터 Practical Validation result에는 compact `validation_efficacy_audit`가 붙는다. 이 audit은 기존 compact evidence만 읽고, runtime replay, period coverage, benchmark parity, walk-forward temporal validation, OOS holdout validation, regime split validation, provider freshness, robustness, PIT / look-ahead, survivorship / universe, execution / storage boundary를 별도 row로 표시한다. 새 DB write, 새 JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않는다.
`validation-efficacy-gate-policy-link-v1`부터 Final Review gate policy는 Validation Efficacy Audit route를 selected-route 조건으로 읽는다. `VALIDATION_EFFICACY_NEEDS_INPUT`과 `VALIDATION_EFFICACY_BLOCKED`는 selected-route blocker이며, `VALIDATION_EFFICACY_REVIEW`는 선정 전 review-required로 남긴다.
`validation-efficacy-gate-policy-refinement-v2`부터 Final Review gate policy는 Validation Efficacy Audit의 non-PASS row도 evidence로 병합한다. Phase 10 temporal / OOS / regime row가 `REVIEW`이면 hold / re-review 요구로, `NEEDS_INPUT` 또는 `BLOCKED`이면 selected-route blocker로 표시된다.
`data-coverage-hardening-v1`부터 Practical Validation result에는 compact `data_coverage_audit`가 붙는다. 이 audit은 DB price window summary, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 별도 row로 표시한다. 현재 listing / asset profile row는 current listing evidence이므로 historical universe나 delisting coverage가 없으면 survivorship PASS로 보지 않는다. 새 JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않는다.
`data-coverage-gate-policy-link-v1`부터 Final Review gate policy는 Data Coverage Audit route를 selected-route 조건으로 읽는다. `DATA_COVERAGE_NEEDS_INPUT`과 `DATA_COVERAGE_BLOCKED`는 selected-route blocker이며, `DATA_COVERAGE_REVIEW`는 선정 전 review-required로 남긴다.
`lifecycle-audit-scoring-v1`부터 Data Coverage Audit은 lifecycle evidence를 current snapshot, SEC identity cross-check, computed partial, actual coverage, delisting actual로 분리해 metrics와 evidence string에 표시한다. 이 표시 강화는 read-only이며 partial evidence를 PASS로 승격하지 않는다.
`concentration-overlap-exposure-contract-v1`부터 Practical Validation result에는 compact `construction_risk_audit`가 붙는다. 이 audit은 component max weight, provider look-through coverage, top holding, holdings overlap, dominant asset bucket, unknown exposure를 분리해 표시한다. provider holdings / exposure가 없거나 partial이면 ready로 올리지 않는다. 새 JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않는다.
`correlation-risk-contribution-contract-v1`부터 Practical Validation result에는 compact `risk_contribution_audit`가 붙는다. 이 audit은 component return matrix coverage, average / max correlation, max risk contribution proxy, drop-one dependency, source strength, storage boundary를 분리해 표시한다. component matrix나 drop-one evidence가 없으면 ready로 올리지 않고, DB price proxy / mixed source matrix는 `REVIEW`로 남긴다. raw return matrix나 covariance artifact를 workflow 저장물로 만들지 않는다.
`component-role-weight-discipline-v1`부터 Practical Validation result에는 compact `component_role_weight_audit`가 붙는다. 이 audit은 explicit role source coverage, profile-aware max weight, role concentration, profile intent fit, weight rationale coverage, storage boundary를 분리해 표시한다. role source가 없거나 partial이면 ready로 올리지 않고, 단일 / inferred-only role evidence는 `REVIEW` 또는 `NEEDS_INPUT`으로 남긴다. role preset, user memo, saved setup 저장을 만들지 않는다.
`construction-risk-gate-policy-v1`부터 Final Review gate policy는 Construction Risk / Risk Contribution / Component Role / Weight audit route와 non-PASS row criteria를 selected-route 조건으로 읽는다. `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다.
`backtest-realism-hardening-v1`부터 Practical Validation result에는 compact `backtest_realism_audit`가 붙는다. 이 audit은 기존 result metadata와 compact validation evidence만 읽고, transaction cost, turnover, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary를 별도 row로 표시한다. 새 DB write, 새 JSONL registry, user memo, preset, approval, order, auto rebalance는 추가하지 않는다.
`cost-model-source-contract-review-v1`부터 Backtest Realism Audit은 compact `cost_model_contract`를 함께 읽는다. `transaction_cost_bps`만 있는 경우는 assumption-only `REVIEW`이며, runtime이 `cost_application_status=applied_to_result_curve`와 비용 적용 source를 전달한 경우에만 cost model PASS 후보가 된다.
`turnover-rebalance-evidence-v1`부터 Backtest Realism Audit은 compact `turnover_evidence_contract`도 함께 읽는다. holdings-derived turnover estimate는 PASS 후보지만, rebalance cadence만 있거나 legacy turnover metadata만 있으면 `REVIEW`, turnover와 cadence가 모두 없으면 `NEEDS_INPUT`으로 남긴다.
`net-cost-curve-application-v1`부터 Backtest Realism Audit은 compact `net_cost_curve_contract`와 `Net cost curve proof` row도 함께 읽는다. measurable gross-net cost impact가 있으면 PASS 후보지만, zero-cost, turnover 미추정, legacy application flag only, missing proof는 각각 `REVIEW` 또는 `NEEDS_INPUT`으로 남긴다.
`liquidity-capacity-evidence-v1`부터 Backtest Realism Audit은 compact `liquidity_capacity_contract`도 함께 읽는다. fresh official actual provider evidence와 capacity metrics는 PASS 후보지만, stale / unknown freshness, partial coverage, bridge / proxy-only evidence, legacy `PASS` flag only는 `REVIEW` 또는 `NEEDS_INPUT`으로 남긴다.
`cost-slippage-sensitivity-audit-v1`부터 Backtest Realism Audit은 compact `cost_slippage_sensitivity_contract`와 `Cost / slippage sensitivity evidence` row도 함께 읽는다. explicit cost / slippage sensitivity는 PASS 후보지만, 일반 robustness sensitivity만 있거나 sensitivity가 없으면 `REVIEW`, 비용 / net curve baseline 자체가 없으면 `NEEDS_INPUT`으로 남긴다.
`backtest-realism-gate-policy-link-v1`부터 Final Review gate policy는 Backtest Realism Audit route를 selected-route 조건으로 읽는다. `BACKTEST_REALISM_NEEDS_INPUT`과 `BACKTEST_REALISM_BLOCKED`는 selected-route blocker이며, `BACKTEST_REALISM_REVIEW`는 선정 전 review-required로 남긴다.
`backtest-realism-gate-policy-refinement-v1`부터 gate policy는 failing Backtest Realism row criteria도 `backtest_realism` policy evidence에 병합한다. 따라서 cost / slippage sensitivity gap이나 liquidity gap은 generic route label 뒤에 숨지 않고 selected-route gate에서 직접 확인된다.
`6. 보강 액션`에는 Provider Action Center를 표시한다. 사용자는 ETF별 Provider Data Gaps 표를 바로 보기 전에 actionable gap 수, 현재 수집 / 보강 가능한 항목, connector mapping 필요 항목을 카드로 먼저 본다. 상세 table과 action plan은 접힘 영역에 두고, 수집 가능한 부족 데이터는 같은 화면에서 일괄 수집 / 보강할 수 있다. 이때 화면은 버튼과 결과 표시만 맡고, 수집 계획과 ingestion job orchestration은 Practical Validation service가 맡는다. 공식 source mapping이 없는 holdings / exposure는 먼저 `etf_provider_source_map` discovery를 실행해 verified endpoint를 찾고, 자동 탐색 후에도 없을 때만 수동 connector mapping 필요로 남긴다.
사용자가 명시적으로 `전략 재검증 실행`을 누르면 Practical Validation replay service가 기존 strategy runtime으로 source를 다시 실행하고, 기본값은 DB의 최신 시장일까지 종료일을 확장한 재검증이다. 최신 runtime replay와 period coverage는 Practical Validation의 필수 module이므로 미실행 `NOT_RUN` 상태에서는 Final Review 이동이 차단된다.
보조 모드로 `저장 기간 그대로 재현`을 선택할 수 있으며, 화면은 저장 종료일, 재검증 종료일, 확장 일수, curve provenance와 benchmark / comparator parity를 표시해 결과가 최신 runtime 재검증인지, 저장 기간 재현인지, embedded snapshot인지, DB price proxy인지 구분한다.
full holdings row와 full macro series는 DB에만 두고, Practical Validation result에는 compact provider coverage / top evidence만 저장한다.

Legacy / compatibility 흐름:

- `Candidate Review`, `Portfolio Proposal`, 기존 Pre-Live registry, 기존 proposal registry는 바로 삭제하지 않는다. 다만 새 주 흐름의 필수 join 조건이 아니라 legacy inspector / archive compatibility로 낮춘다.
- 기존 `Single Strategy`, `Compare & Portfolio Builder`, `Candidate Review`, `Portfolio Proposal` route request는 `backtest_workflow_routes.py`에서 3단계 stage로 매핑한다.

Operations 보조 화면:

- `Operations > Ops Review`: 웹앱 ingestion / refresh / factor job의 run health를 점검한다. triage flow, 최근 실행 상태, action inbox, failure CSV, run artifact, related logs, runtime snapshot을 보여주며, job 실행은 `Ingestion`, backtest replay는 `Backtest Run History`, 후보 replay는 `Candidate Library`로 분리한다.
- `Operations > Backtest Run History`: 저장된 실행 기록을 inspect하고, 가능한 경우 run again, load into form, candidate draft handoff를 수행한다. 후보 검토 흐름의 주 단계가 아니라 과거 실행을 다시 열기 위한 운영 / 재현 도구로 둔다.
- `Operations > Candidate Library`: `CURRENT_CANDIDATE_REGISTRY.jsonl`과 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 읽어 저장된 후보를 다시 열어 본다. registry에는 compact snapshot만 남으므로, 그래프 / result table이 필요할 때 저장 contract로 DB-backed result curve를 재생성한다. 후보 등록 단계가 아니라 보관함 / 재검토 도구다.
- `Operations > Selected Portfolio Dashboard`: `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 row만 읽어 최종 선정 포트폴리오의 compact 선택, Snapshot, 기간 확장 Performance Recheck tabs, Recheck Operations Preflight, Recheck Readiness, Symbol Freshness, Provider Evidence, Final Review -> dashboard continuity check, source contract, Portfolio Monitoring의 Timeline / Review Signals / recheck comparison / Why Selected / optional Actual Allocation / allocation evidence boundary / Decision Dossier / Audit을 보여준다. Preflight / Readiness / Symbol Freshness / Provider Evidence / Continuity / Timeline / Recheck Comparison / Allocation Boundary / Dossier는 read-only이며, live approval / broker order / auto rebalance는 disabled로 둔다.

## 현재 Reference Guide 제품 흐름

`Reference > Guides`의 사용자-facing 흐름은 아래 순서로 읽는다.

```text
Ingestion / Data Trust
  -> Single Strategy Backtest
  -> Real-Money Signal
  -> Hold / Blocker Resolution
  -> Portfolio Mix Builder
  -> Candidate Packaging
     -> Draft 확인 / Review Note 저장 / Registry 저장 / Pre-Live 운영 기록 / Portfolio Proposal 이동 판단
  -> Portfolio Mix Builder 재검토 또는 Portfolio Proposal
  -> Portfolio Proposal
     -> 후보 선택 / 목적 / 역할 / 비중 설계 / Proposal 저장 / Final Review 입력 준비
  -> Final Review
     -> Portfolio Risk / Validation Pack
     -> Robustness / Stress Validation Preview
     -> Stress / Sensitivity Summary
     -> Paper Observation 기준 확인
     -> 최종 선정 / 보류 / 거절 / 재검토 결과 기록
     -> 최종 판단 완료
```

구분:

- `Candidate Packaging`은 Draft 확인, Review Note 저장, Registry 저장, Pre-Live 운영 기록, Portfolio Proposal 이동 판단을 하나로 묶은 사용자-facing 6단계다.
- `Candidate Draft`는 latest run 또는 `Operations > Backtest Run History`에서 보낸 history run을 후보처럼 읽는 저장 전 초안이며, Candidate Packaging 안에서 쓰인다.
- `Registry 저장`은 저장된 판단 기록을 Current Candidate / Near Miss / Scenario / Stop 중 어디까지 남길지 정하고, 통과한 row만 Current Candidate Registry에 append하는 Candidate Packaging 내부 작업이다.
- `Pre-Live 운영 기록`은 저장된 후보를 실제 돈 없이 paper / watchlist / hold / re-review 중 어떻게 관찰할지 기록하는 Candidate Packaging 내부 작업이다.
- `Portfolio Proposal 이동 판단`은 Pre-Live 운영 record를 저장하기 전에 저장 가능 여부와 저장 후 Proposal 이동 가능 여부를 같이 보여주는 Candidate Packaging의 최종 route 확인이다.
- `Portfolio Proposal`은 후보 묶음 제안이며, live trading approval이 아니다. 단일 후보는 별도 proposal 저장 없이 Final Review 입력 후보로 읽고, 여러 후보를 묶을 때는 역할 / 비중을 명시한다. 내부 route label에 `Live Readiness`라는 legacy 표현이 남아 있어도 현재 사용자-facing 해석은 Final Review 입력 준비다.
- `Final Review`는 Proposal 탭 밖에서 검증과 최종 판단을 담당한다. 별도 Paper Ledger 저장 버튼을 주요 흐름으로 노출하지 않고, paper observation 기준을 최종 검토 기록 안에 포함하며 현재 사용자-facing workflow의 마지막 active panel이다.
- `Portfolio Risk / Live Readiness Validation Pack`은 Phase 31에서 추가된 읽기 전용 검증 surface다. 단일 후보, 작성 중 proposal, 저장된 proposal을 route / score / blocker / component risk / 다음 단계 안내로 읽는다.
- `Robustness / Stress Validation Pack`은 Phase 32에서 추가된 surface다. 현재 주 흐름에서는 Practical Validation의 Robustness Lab board가 stress / rolling / sensitivity / overfit 근거를 compact하게 요약하고 Final Review가 같은 board를 읽는다. Strategy-specific parameter perturbation이 아직 없는 항목은 follow-up으로 남기며 PASS로 간주하지 않는다.
- `Paper Tracking Ledger`는 Phase 33에서 추가된 append-only 기록 흐름이지만, 현재 주 사용자 흐름에서는 Final Review의 inline paper observation 기준으로 흡수한다. 기존 ledger row는 backward compatibility / 과거 QA 기록으로 읽을 수 있다.
- Phase 35에서 별도 `Post-Selection Guide` panel은 과한 단계로 판단해 active workflow에서 제거했다. 최종 판단과 투자 가능 / 투자하면 안 됨 / 내용 부족 / 재검토 필요 해석은 `Backtest > Final Review`의 saved final decision review에서 확인한다.
- Phase 36에서 선정 이후 운영 확인은 `Backtest` 주 workflow가 아니라 `Operations > Selected Portfolio Dashboard`로 분리했다. 이 화면은 Final Review selected row를 read-only로 읽고, 사용자가 지정한 시작일 / 종료일 / 가상 투자금으로 selected component contract를 다시 replay해 최신 기간 성과를 확인한다. `Recheck Operations Preflight`는 Final Review embedded replay contract, Current Candidate Registry fallback, DB latest market date, replay period, symbol freshness를 하나의 route로 묶는다. `Recheck Readiness`는 실행 전에 DB latest market date, selected component replay contract, 기본 기간, 실행 / 저장 경계를 읽는다. `Symbol Freshness`는 replay portfolio ticker와 benchmark ticker의 DB latest date / row count / lag를 읽어 missing / stale 상태를 표시한다. `Provider Evidence`는 selected component ticker weight로 기존 DB provider / holdings / exposure context를 읽고 `NOT_RUN`, stale freshness, partial / bridge / proxy coverage, missing operability / holdings / exposure를 pass로 숨기지 않는다. `Continuity` check는 selected route, source contract, investability packet, component target, review trigger, monitoring timeline, Performance Recheck input, execution / storage boundary를 읽는다. `Timeline`은 Final Review selection, evidence gate, Performance Recheck, Actual Allocation drift, Review trigger preview를 시간순으로 보여주며 monitoring log를 자동 저장하지 않는다. `Review Signals`는 Recheck Comparison을 performance threshold policy owner로 삼아 CAGR / MDD / benchmark spread / component coverage / period coverage rows를 읽고, preflight / provider / drift 상태를 `Clear / Watch / Breached / Needs Input / Optional`로 번역한다. `Decision Dossier`는 Final Decision V2 row와 optional session timeline의 source contract consistency를 markdown에 표시한다. current value 기반 Actual Allocation을 기본 입력으로 두고, shares x price / current weight 입력은 advanced 입력으로 둔다. `Allocation evidence boundary`는 입력 / alert 저장, monitoring log auto-write, account / broker 연결, 주문, 자동 리밸런싱이 모두 꺼져 있음을 표시한다.
- Practical Validation P2 provider data는 `Workspace > Ingestion > Practical Validation Provider Snapshots`에서 먼저 수집할 수 있다. `Provider Source Map` tab은 `nyse_etf` / `nyse_asset_profile` 기반으로 ETF별 공식 endpoint와 parser mapping을 검증해 저장한다. `Delisting Evidence` tab은 SEC Form 25 / 25-NSE filing metadata를 `nyse_symbol_lifecycle` delisting evidence로 저장해 Data Coverage Audit의 survivorship / delisting control 근거를 보강한다. 이후 Practical Validation 화면은 loader / provider context / lifecycle summary를 읽어 12개 진단과 audit의 actual / proxy / `NOT_RUN` 상태와 Look-through Exposure Board를 표시한다. 화면 안의 Provider Data Gaps에서도 현재 source에 부족한 provider snapshot을 ETF별로 확인하고, source map discovery와 수집 가능한 항목은 일괄 보강할 수 있다.

현재 Guides 화면은 제품형 의사결정 guide로 정리한다.

| 묶음 | 내용 |
|---|---|
| `Portfolio Selection Guide` hero | 제품 안내 첫 화면으로, 현재 workflow와 runtime / git 상태를 compact badge로 보여준다. 개발용 `Runtime / Build`는 하단 접힘 `System status`로 낮춘다 |
| `현재 진행 상황 선택` | 단일 후보, 여러 후보 묶음, 저장된 Mix, 보류 / 재검토 중 사용자의 현재 상황을 먼저 고른다 |
| `전체 1~10 단계에서 현재 위치` | 선택 버튼 바로 아래에 제품형 compact timeline을 둔다. 선택 경로에 따라 `필수`, `반복`, `직행`, `선행`, `생략`, `보류` 같은 상태 라벨을 붙여 현재 위치와 생략되는 단계를 먼저 해석하게 한다 |
| `선택한 경로 요약` | `선택한 목표`, `진행 순서`, `건너뛰거나 조심할 단계`, `생성 / 참조 기록`으로 선택 경로의 화면 순서와 기록 경계를 짧게 보여준다 |
| `Portfolio Flow` | 선택 경로를 GraphViz flowchart로 보여주고, 환경상 GraphViz 렌더링이 실패하면 compact visual fallback으로 표시한다. chart node는 큰 흐름을 맡고, 긴 설명은 아래 checkpoint 패널로 넘긴다 |
| `선택한 경로의 핵심 체크포인트` | 선택 경로에서 실제로 놓치면 안 되는 checkpoint를 카드로 보여준다. 단일 후보, 여러 후보 묶음, 저장된 Mix, 보류 / 재검토마다 같은 workflow를 다르게 해석한다 |
| `Decision Gates` | 단계 번호 대신 `Portfolio Mix Builder로 조합해도 되는가`, `Candidate로 남겨도 되는가`, `Proposal로 묶어도 되는가`, `Final Review를 기록해도 되는가` 같은 사용자 질문 기준으로 Go / Review / Stop을 보여준다 |
| `Reference Drawer` | 핵심 개념, 상세 단계, 기록 저장소, 운영 경계를 탭으로 낮춰 필요할 때만 확인하게 한다 |

사용자는 먼저 현재 진행 상황을 고르고,
1~10 단계 timeline에서 전체 workflow상 위치를 본 뒤,
선택한 경로 요약과 flowchart로 실제 화면 순서와 기록 경계를 확인한다.
그 다음 경로별 checkpoint에서 놓치면 안 되는 판단을 보고
실제로 지나가는 화면, 반복되는 단계, 생략되는 단계, 생성되거나 읽는 기록을 본다.
그 다음 Decision Gates와 Reference Drawer를 이어서 읽는다.

경로별 핵심 차이는 아래와 같다.

| 경로 | 핵심 차이 |
|---|---|
| `단일 후보 경로` | Candidate Review와 Pre-Live 기록 후 Portfolio Proposal에서 단일 후보 직행 평가를 사용하며, proposal draft 저장을 반복하지 않는다 |
| `여러 후보 묶음 경로` | 후보별 실행 / 비교와 Candidate Review 저장이 선행이고, Portfolio Proposal은 이미 저장된 후보들을 역할 / 비중 / 목적이 있는 proposal draft로 묶은 뒤 Final Review에서 읽는다 |
| `저장된 Mix 경로` | saved weighted portfolio setup은 후보 registry가 아니라 재사용 weight setup이므로 replay / mix 검증 후 Practical Validation source로 연결한다 |
| `보류 / 재검토 경로` | hold / blocked / insufficient evidence / re-review 상태에서는 Final Review 직행이 아니라 원인 화면으로 되돌아간다 |

## Phase 36 Selected Portfolio Dashboard

Phase36은 Final Review 이후 새 판단 저장 단계를 추가하지 않는다.
Backtest workflow는 Final Review에서 끝나고,
선정 이후 확인은 Operations 화면에서 한다.

```text
Backtest > Final Review
  -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl
  -> Operations > Selected Portfolio Dashboard
```

구현 책임:

| 파일 | 역할 |
|---|---|
| `app/runtime/final_selected_portfolios.py` | Final Review final decision row를 읽고 selected dashboard row / status summary / continuity check / selected component performance recheck operations preflight / readiness / symbol freshness / selected provider evidence / performance recheck / recheck comparison / current weight 또는 value / holding input 기반 drift check / drift alert preview / allocation drift evidence boundary / monitoring timeline으로 변환 |
| `app/services/backtest_evidence_read_model.py` | Final Review final decision row의 status / evidence checks / decision dossier를 Streamlit-free read model로 변환 |
| `app/web/final_selected_portfolio_dashboard.py` | Operations dashboard 화면 render, compact selected portfolio picker, Snapshot, Performance Recheck readiness + symbol freshness + provider evidence + setup + result tabs, Continuity check, Portfolio Monitoring Timeline / Review Signals / Recheck Comparison / Why Selected / optional Actual Allocation / allocation evidence boundary / Decision Dossier / Audit 표시 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | dashboard table, component table, timeline table, recheck preflight table, recheck readiness table, symbol freshness table, provider evidence table, recheck comparison table, value / holding input table, drift table, alert preview table, allocation boundary table, filter helper |
| `app/web/streamlit_app.py` | Operations navigation에 `Selected Portfolio Dashboard` page 등록 |

데이터 기준:

- source-of-truth: `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`
- selected filter:
  - `decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO`
  - 또는 `selected_practical_portfolio == true`
- dashboard write policy:
  - read-only
  - 새 final decision row를 저장하지 않음
  - proposal / candidate registry를 덮어쓰지 않음
  - monitoring timeline을 자동 저장하지 않음
- performance recheck:
  - 실행 전 Recheck Operations Preflight가 replay contract readiness와 DB symbol freshness를 하나의 route로 확인
  - Recheck Readiness가 DB latest market date, selected component replay contract, 기본 기간을 확인
  - Symbol Freshness가 replay portfolio ticker와 benchmark ticker의 DB latest date / row count / stale 상태를 확인
  - Provider Evidence가 selected provider ticker weight로 DB provider / holdings / exposure context와 look-through summary를 read-only로 확인
  - selected component의 `registry_id`로 Current Candidate Registry의 replay contract를 찾음
  - 사용자가 지정한 recheck start / end / virtual capital로 DB-backed strategy replay 실행
  - portfolio value, total return, CAGR, MDD, benchmark spread, component contribution, strongest / weakest periods 표시
  - 새 registry row를 저장하지 않음
- recheck comparison:
  - 최신 Performance Recheck result를 Final Review baseline과 비교
  - CAGR delta, MDD delta, benchmark spread, component coverage, period coverage를 `PASS / WATCH / BREACHED / NEEDS_INPUT`으로 분류
  - Performance Recheck 미실행이나 오류는 pass가 아니라 입력 필요 상태로 표시
  - monitoring log, memo, preset, report 파일을 자동 저장하지 않음

first-pass status:

| status | 의미 |
|---|---|
| `normal` | selected row, active component, target weight 100%, blocker 없음 |
| `watch` | selected row지만 evidence / validation / robustness / paper route가 보수적으로 읽힘 |
| `rebalance_needed` | dashboard row 상태 enum으로 유지하며, 상세 `Current Weight / Drift Check`에서는 threshold 초과 시 `REBALANCE_NEEDED`로 표시 |
| `re_review_needed` | evidence 또는 paper observation blocker가 남아 있음 |
| `blocked` | component / target weight / selected route 기준이 운영 대상으로 불충분함 |

경계:

- `Operations > Selected Portfolio Dashboard`는 live approval, broker order, auto rebalance가 아니다.
- Recheck Operations Preflight는 현재 decision row, Current Candidate Registry fallback, DB latest market date, price freshness metadata를 읽는 사전 점검이며 데이터 수집이나 저장을 실행하지 않는다.
- Recheck Readiness는 현재 decision row, embedded replay contract, Current Candidate Registry fallback, DB latest market date를 읽는 사전 점검이며 데이터 수집이나 저장을 실행하지 않는다.
- Symbol Freshness는 price DB metadata를 읽는 사전 점검이며 OHLCV 수집이나 저장을 실행하지 않는다.
- Provider Evidence는 기존 provider snapshot DB를 읽는 사전 점검이며 provider 수집, JSONL 저장, monitoring log 자동 저장을 실행하지 않는다.
- Performance Recheck는 latest result 확인 도구이며 live approval이나 수익 보장 표현이 아니다.
- current value 기반 Actual Allocation을 기본 입력으로 두고, current weight 직접 입력과 shares x price 입력 기반 drift check는 advanced 입력으로 둔다.
- DB latest close 조회는 shares x price 입력을 돕는 보조 기능이다.
- Drift Alert / Review Trigger Preview는 read-only 해석이며 alert registry를 저장하지 않는다.
- Allocation evidence boundary는 Actual Allocation 결과가 수동 / session-only 증거이며 raw input persistence, alert persistence, monitoring log auto-write, account / broker 연결, 주문, 자동 리밸런싱을 만들지 않음을 표시한다.
- Timeline은 현재 decision row와 session-state recheck / drift / alert preview를 읽는 read model이며 monitoring log를 append하지 않는다.
- Continuity check는 현재 decision row와 timeline source contract를 읽는 read model이며 mismatch를 blocked issue로 표시하고 monitoring log를 append하지 않는다.
- Recheck Comparison은 현재 decision row와 session-state recheck result를 읽는 read model이며 monitoring log를 append하지 않는다.
- Decision Dossier는 현재 final decision evidence와 optional session-state timeline을 markdown으로 export하는 read model이며 source contract consistency를 표시하고 report 파일을 자동 저장하지 않는다.
- account holding 자동 연결, broker order, auto rebalance는 후속 phase에서 별도 계약을 정한 뒤 구현한다.

## Portfolio Proposal 계약

Portfolio Proposal은 단순 weighted portfolio 저장값이 아니라,
후보 묶음의 목적과 검토 근거를 함께 담는 제안 초안으로 본다.

현재 상세 계약은 아래 문서를 기준으로 한다.

- [PORTFOLIO_SELECTION_FLOW.md](./PORTFOLIO_SELECTION_FLOW.md)
- [Finance Registries](../../registries/README.md)

기본 저장 위치는
`.aiworkspace/note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이다.
첫 proposal draft를 저장할 때 파일이 생성되며,
append / load helper는 `app/runtime/portfolio_proposal.py`가 담당한다.

Proposal UI가 최소 표시해야 하는 묶음:

- proposal objective
- component candidates and proposal roles
- target weights and weight reasons
- construction method and date alignment
- risk constraints
- evidence snapshot
- open blockers
- operator decision

Portfolio Proposal은 `SAVED_PORTFOLIOS.jsonl`의 replay 계약을 대체하지 않는다.
Saved Portfolio는 재현 가능한 weight setup이고,
Portfolio Proposal은 그 setup이나 candidate set을 왜 제안 후보로 보는지 설명하는 검토 단위다.

## `backtest.py` 리팩토링 경계

2026-04-30 리팩토링 이후 `app/web/pages/backtest.py`는 약 100 lines의 page shell이다.
Backtest workflow의 실제 body는 `app/web/backtest_*.py` module로 분리한다.

| 우선순위 | 분리 후보 | 대표 책임 | 이유 |
|---|---|---|---|
| 1 | Candidate Review module | Candidate Packaging flow, review note save, registry draft UI, Pre-Live 운영 기록, Portfolio Proposal 이동 판단 | 완료: render flow는 `app/web/backtest_candidate_review.py`, 판단 / 변환 / Pre-Live helper는 `app/web/backtest_candidate_review_helpers.py`로 분리. Streamlit auto page discovery를 피하려고 `pages/` 밖에 둔다 |
| 2 | Pre-Live Review tab/module | 별도 Pre-Live tab | 제거: Pre-Live 운영 기록은 Candidate Review 3번 구간으로 통합했고, 별도 `backtest_pre_live_review*.py` 파일은 삭제했다 |
| 3 | Registry runtime helpers | current candidate / review note / pre-live / proposal registry I/O, compare prefill conversion | Candidate Review / Compare / Pre-Live / Proposal이 공통 persistence pattern을 쓴다 |
| 4 | History module | run history display, selected record, run again, load into form | 완료: render flow는 `app/web/backtest_history.py`, replay / parity helper는 `app/web/backtest_history_helpers.py`로 분리. `Operations > Backtest Run History`에서 사용한다 |
| 5 | Portfolio Proposal module | proposal 후보 선택, 목적 / 역할 / 비중 설계, Live Readiness 진입 평가, saved proposal feedback | 완료: render flow는 `app/web/backtest_portfolio_proposal.py`, proposal row / readiness / feedback helper는 `app/web/backtest_portfolio_proposal_helpers.py`로 분리 |
| 6 | Single Strategy module split | strategy-specific forms, runtime dispatch, latest result 연결 | 완료: `backtest_single_strategy.py`, `backtest_single_forms.py`, `backtest_single_runner.py`로 분리 |
| 7 | Portfolio Mix Builder module split | component form / 실행 / weighted portfolio / saved portfolio replay | 완료: `backtest_compare.py`로 분리. 향후 더 세분화할 경우 weighted / saved portfolio를 별도 module로 뺄 수 있다 |
| 8 | Result display helpers | latest result, charts, data trust, real-money details | 완료: 공용 display는 `backtest_result_display.py`로 분리 |
| 9 | Backtest common helper | preset, session state, 입력 컴포넌트, status label | 완료: `backtest_common.py`가 transitional shared module로 관리한다. 향후 규모가 다시 커지면 `backtest_state.py`, `backtest_strategy_inputs.py`, `backtest_presets.py`로 추가 분리한다 |

분리 원칙:

- 먼저 함수 이동만 하고 behavior를 바꾸지 않는다.
- module split 후에는 `python3 -m py_compile app/web/pages/backtest.py app/web/backtest_*.py app/web/streamlit_app.py`를 기본 확인한다.
- Streamlit session state key는 이름을 바꾸지 않는 것을 기본으로 한다.
- registry file path와 append-only semantics는 helper 이동 후에도 유지한다.
- 한 번에 여러 workflow를 옮기지 않는다.

Phase 30 third work unit status:

- `app/runtime/candidate_registry.py`로 registry JSONL read / append helper를 먼저 분리했다.
- 분리된 대상은 current candidate registry, candidate review notes, pre-live candidate registry의 file path constant와 I/O helper다.
- `app/runtime/portfolio_proposal.py`로 proposal draft registry read / append helper도 추가했다.
- Candidate Review는 `app/web/backtest_candidate_review.py`와 `app/web/backtest_candidate_review_helpers.py`로 분리되어, `backtest.py`에는 panel wrapper와 cross-panel handoff call만 남아 있다.
- 긴 route/status 문자열은 공용 화면에서는 `app/web/backtest_ui_components.py`의 wrapping card / route panel을 사용하고, Practical Validation은 `app/web/backtest_practical_validation_components.py`의 전용 workbench shell을 사용해 `st.metric` 말줄임과 기본 container 의존을 피한다.
- Backtest shell은 `Backtest Analysis -> Practical Validation -> Final Review`를 주 workflow navigation으로 보여준다. Backtest Analysis 안에서 `Single Strategy`와 `Portfolio Mix Builder`를 선택한다. `History`는 메인 흐름에서 제외하고 `Operations > Backtest Run History` page로 연다.
- Backtest Run History는 `app/web/backtest_history.py`와 `app/web/backtest_history_helpers.py`로 분리되어, `backtest.py`에는 History 화면 render / replay helper 본문이 남아 있지 않다.
- Portfolio Proposal은 `app/web/backtest_portfolio_proposal.py`와 `app/web/backtest_portfolio_proposal_helpers.py`로 분리되어, `backtest.py`에는 panel wrapper만 남아 있다.
- Final Review는 `app/web/backtest_final_review.py`와 `app/web/backtest_final_review_helpers.py`로 분리되어, `backtest.py`에는 panel dispatch만 남아 있다.
- Phase35 보정 이후 Post-Selection Guide module과 panel dispatch는 제거했다. Final Review가 현재 workflow의 마지막 active panel이다.
- Single Strategy는 `app/web/backtest_single_strategy.py`, `app/web/backtest_single_forms.py`, `app/web/backtest_single_runner.py`로 분리되어, form render와 runtime dispatch를 page shell에서 제거했다.
- Portfolio Mix Builder는 `app/web/backtest_compare.py`로 분리되어, component 실행 / weighted portfolio service 호출, saved portfolio replay / load, current-candidate prefill을 page shell에서 제거했다.
- Latest result / compare result / Real-Money detail / selection history display는 `app/web/backtest_result_display.py`가 담당한다.
- 공용 preset, session state, 입력 컴포넌트, status label은 `app/web/backtest_common.py`가 담당한다. 이 파일은 다음 리팩토링에서 더 잘게 나눌 수 있는 transitional shared module이다.
- 따라서 `app/web/pages/backtest.py`는 Backtest page shell과 workflow navigation만 유지한다.

## Single Strategy 흐름

```text
strategy 선택
  -> strategy-specific form 입력
  -> _handle_backtest_run(...)
  -> app/runtime/backtest.py run_*_backtest_from_db(...)
  -> latest result bundle 저장
  -> result table / summary / selection history / real-money surface 표시
  -> history record 저장
```

주의:

- `Load Into Form`은 입력값만 복원한다.
- 복원 후 결과를 갱신하려면 사용자가 다시 실행해야 한다.
- selection history가 있는 전략은 latest result의 `Selection History Table` / `Interpretation Summary`에서 상세를 본다.

## Stage / Checkpoint 용어 기준

Backtest 제품 흐름의 `Stage`와 화면 안의 검증 기준은 분리해 부른다.

Stage:

- `Backtest Analysis`: 후보 생성
- `Practical Validation`: 실전 투입 전 검증
- `Final Review`: 최종 선택 / 보류 / 거절 / 재검토
- `Operations > Selected Portfolio Dashboard`: 선정 이후 모니터링 / 재확인

검증 체크포인트:

- `Result Integrity`: Data Trust, 기간, 가격 최신성, excluded ticker
- `Performance Shape`: Summary, Equity Curve, extremes
- `Candidate Readiness`: Real-Money signal, Promotion, execution source checks, validation source checks
- `Practical Evidence`: provider / data coverage / realism / robustness / construction evidence
- `Final Decision Gate`: selected-route blocker와 최종 판단
- `Monitoring Check`: 선정 이후 recheck readiness, freshness, provider evidence, review signal

## Real-Money Candidate Readiness 흐름

`Real-Money > 현재 판단`에는 `Candidate Readiness Checkpoint` 박스를 둔다.

목적:

- `Promotion`, execution source checks, validation source checks를 10점 척도로 요약한다.
- 사용자가 이 결과를 Portfolio Mix Builder 또는 Practical Validation 후보로 넘겨도 되는지 먼저 판단하게 한다.
- 이 평가는 live trading approval이나 주문 지시가 아니라 후보 검토 보조 신호다.
- `Shortlist`는 독립 검증 단계로 보지 않고, `Promotion` 안의 `Suggested Route`로 표시한다.
- Backtest Analysis에서는 `Probation`, `Monitoring`, `Deployment`를 시작한 것처럼 표시하지 않고, `Next Validation Focus`와 `Execution Preview`로 낮춰 보여준다.

기준:

- `Promotion Decision != hold`
- 실행 원천 blocker 없음
- 검증 원천 blocker 없음

점수 해석:

- `8.0 / 10` 이상이면 깔끔하게 후보 검토가 가능한 상태다.
- `8.0 / 10` 미만이어도 위 핵심 기준을 만족하면 조건부 후보 검토가 가능하지만, 개선 항목을 같이 확인한다.
- 위 핵심 기준을 만족하지 못하면 점수와 무관하게 blocker를 먼저 해결한다.

표시:

- `Candidate Readiness`: 10점 만점의 후보 검토 점수
- `판정`: `후보 검토 진행 가능`, `후보 검토 가능, 개선 항목 동시 확인`, `후보 보류: blocker 먼저 해결`
- `다음 행동`: Portfolio Mix Builder / Practical Validation으로 넘길지, blocker를 먼저 해결할지 설명
- `Promotion Suggested Route`: `Hold / Review`, `Watchlist Review`, `Paper Observation Candidate`, `Small-Capital Review Candidate` 같은 추천 경로
- `Next Validation Focus`: 다음 단계에서 확인할 benchmark, drawdown, liquidity, price freshness, regime / split-period 항목
- `Execution Preview`: 비용, 유동성, ETF 운용 가능성 같은 실행 부담 미리보기이며 배치 승인 아님
- `점수 계산 기준 보기`: Promotion / Execution Source Checks / Validation Source Checks별 점수 근거

## Portfolio Mix Builder 흐름

```text
strategy multi-select
  -> Component Period & Shared Inputs
  -> strategy별 box에서 variant / advanced inputs 설정
  -> 구성 포트폴리오 실행
  -> component별 result bundle 실행
  -> component summary / data trust / real-money evidence 확인
  -> Mix Weight 구성
  -> Mix 후보 1차 판단
  -> 실전성 검증으로 보내기
```

현재 UX 기준:

- common date / timeframe / option은 공유 입력으로 둔다.
- strategy-specific advanced inputs는 strategy별 box 안에서 보이게 한다.
- variant 변경은 버튼 없이 즉시 아래 옵션이 바뀌는 방향이 선호된다.
- 최대 component 전략 수는 operator가 읽을 수 있는 범위로 유지한다.

Portfolio Mix Builder는 더 이상 "개별 후보를 서로 비교해서 하나를 보내는 화면"이 아니다.
이 화면의 주 목적은 여러 component portfolio를 실행하고 weight를 정해 하나의 mix 후보를 만드는 것이다.
component별 상세 결과는 weight를 정하기 위한 근거로 남기고, Practical Validation handoff는 mix 전체에만 둔다.

목적:

- 여러 전략을 같은 기간 / 같은 공통 입력으로 실행해 mix의 재료를 만든다.
- weight 합계와 positive component 수를 확인해 실제 mix 후보인지 본다.
- component별 Promotion / 실행 원천 / 검증 원천 blocker와 Data Trust를 모아 mix handoff 가능 여부를 판단한다.
- 이 평가는 saved setup 저장, Pre-Live 승인, live trading approval이 아니라 Backtest 1차 후보를 Practical Validation으로 넘길 수 있는지 보는 신호다.

기준:

- `Mix Result`: weighted mix result가 실제로 생성됐는지
- `Weight Discipline`: target weight 합계가 100%이고 positive component가 2개 이상인지
- `Component Data Trust`: component별 결과 기간, 가격 최신성, excluded / malformed ticker가 해석 가능한지
- `Component 1차 후보 판단`: 각 component의 `Promotion != hold`, 실행 원천 blocker 없음, 검증 원천 blocker 없음인지

점수 해석:

- `8.0 / 10` 이상이면 `PASS`로 보고 Practical Validation으로 진행 가능하다.
- `6.5 / 10` 이상이면 `CONDITIONAL`로 보고 조건부 진행 가능하되 Practical Validation에서 확인할 약점과 gap을 같이 남긴다.
- 짧은 실제 종료일 불일치, warning, excluded / malformed ticker 같은 Data Trust 이슈는 score를 cap하지 않고 warning으로 표시한다.
- GTAA처럼 `interval > 1`, `option=month_end`인 cadence 전략은 요청 종료일이 다음 정상 cadence close 전이면 `Data Trust blocked`가 아니라 cadence-aligned review로 표시한다.
- 가격 최신성 error 또는 결과 기간이 크게 비는 Data Trust blocked 상태, component Promotion hold, 실행 / 검증 원천 blocker, weight discipline 실패는 `HOLD`로 보고 mix를 먼저 보강한다.

실행:

- `Mix 후보 1차 판단`이 통과 또는 조건부 통과 상태일 때만 `실전성 검증으로 보내기` 버튼으로 mix Clean V2 source를 만들 수 있다.
- 이 버튼은 1차 Backtest 후보 판단을 통과한 mix를 2차 `Practical Validation` 입력 source로 넘기는 handoff다.
- `Promotion Decision = hold`, 실행 원천 blocker, 검증 원천 blocker, weight blocker가 남아 있으면 버튼은 비활성화되고, 화면에 막는 이유를 짧게 표시한다.
- 이 버튼은 live approval, 투자 추천, 주문 지시, 자동 리밸런싱이 아니다.

저장된 Mix replay:

- `Mix 재실행 및 검증`은 저장된 weighted portfolio mix 자체와 그 구성 전략 compare를 함께 복원한다.
- UI에서는 `저장된 Mix` 화면 안에서 `저장 Mix Replay 결과`와 `Portfolio Mix 검증 보드`를 바로 보여준다.
- `Portfolio Mix 검증 보드`는 saved mix 자체의 replay 가능 여부, mix data trust, 구성 전략 Real-Money gate, Clean V2 검증 기록 여부를 분리해서 보여준다.
- 저장 mix는 reusable setup이므로, replay 성과가 좋아도 자동으로 최종 판단 기록이 되지 않는다. `Workflow Registry`가 `NOT RECORDED`이면 Practical Validation / Final Review 쪽 기록이 아직 없다는 뜻이다.
- 이 경우 사용자는 `Practical Validation으로 보내기`로 mix 전체를 Clean V2 source로 저장한다. Saved mix는 이미 비중이 정해진 포트폴리오 조합이므로, 단일 전략 후보 handoff와 분리한다.
- 개별 전략 후보 간 비교 / 벤치마킹 도구는 추후 별도 Candidate Comparison 성격의 read-only 도구로 분리할 수 있다.

## Strategy Capability Snapshot 흐름

Phase 28 이후 `Single Strategy`와 `Portfolio Mix Builder`의 strategy box에는
`Strategy Capability Snapshot` 접힘 영역을 둔다.

목적:

- annual strict, quarterly strict, price-only ETF 전략이 서로 다른 이유를 UI에서 먼저 설명한다.
- cadence, data trust, selection history, Real-Money/Guardrail, history/replay 지원 범위를 표로 보여준다.
- 기능이 없는 것처럼 보이는 부분이 버그인지, 아직 annual 중심으로 남긴 의도적 차이인지 구분하게 한다.

현재 기준:

- strict annual은 가장 성숙한 Real-Money / Guardrail surface로 설명한다.
- strict quarterly prototype은 Data Trust와 Portfolio Handling은 지원하지만, Real-Money promotion / Guardrail 판단은 아직 annual strict 중심으로 설명한다.
- Equal Weight는 static ETF basket baseline이지만, Single / Portfolio Mix Builder 실행에서는 ETF Real-Money first pass를 붙여 promotion / suggested route / deployment gate를 읽는다.
- Global Relative Strength는 재무제표 selection history 대상이 아니라 price-only ETF relative strength strategy로 설명한다.

## Data Trust Summary 흐름

Phase 27 이후 `Latest Backtest Run` 상단에는 `Data Trust Summary`를 둔다.

목적:

- 요청 종료일과 실제 결과 종료일을 먼저 비교한다.
- price freshness, common latest price, latest-date spread를 결과 해석 전에 보여준다.
- excluded ticker와 malformed price row가 있으면 `Data Quality Details`에서 확인하게 한다.

첫 적용 대상:

- `Global Relative Strength` single strategy 실행 전 `Price Freshness Preflight`
- `Latest Backtest Run`의 공통 `Data Trust Summary`

## Candidate Library 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  + PRE_LIVE_CANDIDATE_REGISTRY.jsonl
  -> Operations > Candidate Library
  -> 후보 선택
  -> Stored Snapshot / Replay Contract / Pre-Live Record 확인
  -> Rebuild Result Curve
  -> Single Strategy와 같은 Summary / Equity Curve / Extremes / Result Table 확인
```

Candidate Library는 workflow 단계가 아니다.
Candidate Review에서 저장한 후보를 나중에 다시 열어보고,
registry snapshot과 실제 재실행 결과가 같은 설정으로 복원되는지 확인하는 보조 화면이다.

현재 replay 지원 범위는 price-only ETF 후보 family와 strict annual equity 후보 family다.

- Equal Weight
- GTAA
- Global Relative Strength
- Risk Parity Trend
- Dual Momentum
- Quality Snapshot (Strict Annual)
- Value Snapshot (Strict Annual)
- Quality + Value Snapshot (Strict Annual)

## Weighted Portfolio / Saved Portfolio Mix 흐름

```text
Backtest > Portfolio Mix Builder
  -> 새 Mix 만들기
  -> 구성 포트폴리오 실행
  -> component result bundles
  -> weight 입력
  -> optional GTAA 70 / Equal Weight 30 quick mix
  -> make_monthly_weighted_portfolio(...)
  -> weighted result
  -> Mix 후보 1차 판단
  -> 실전성 검증으로 보내기
  -> Save Portfolio Mix

Backtest > Portfolio Mix Builder
  -> 저장된 Mix
  -> Mix 재실행 및 검증 or 새 Mix 만들기에서 수정하기
  -> Mix 재실행 및 검증은 같은 화면에서 replay result / Portfolio Mix 검증 보드 / weighted result 확인
  -> workflow 기록이 없으면 Practical Validation으로 보내기
  -> 새 Mix 만들기에서 수정하기는 기존 결과를 숨기고 component 실행 form을 form-first 상태로 다시 채움
```

구분:

- `새 Mix 만들기`: component portfolio를 실행하고 weight를 입력해 하나의 mix 후보를 만든다. 개별 전략 handoff는 주 action이 아니며, mix 후보 판단만 Practical Validation handoff를 가진다.
- `저장된 Mix`: `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`에 저장한 reusable setup을 다시 실행하고 mix-level 검증으로 읽는다.
- `새 Mix 만들기에서 수정하기`: 저장된 component 구성과 weight를 form에 다시 채운다. 검증 버튼이 아니라 편집 / 재구성 진입이며, 기존 stale compare / weighted 결과는 숨기고 사용자가 먼저 설정을 수정하게 한다.
- `Mix 재실행 및 검증`: 저장 당시 context로 component 실행과 weighted portfolio를 다시 실행하고, `저장된 Mix` 화면 아래에 replay 결과와 mix 검증 보드를 바로 렌더링한다.

2026-05-30 이후 Portfolio Mix workspace의 `새 Mix 만들기` / `저장된 Mix` 전환은 `st.tabs`가 아니라 상태를 가진 선택 UI로 관리한다.
이는 saved mix replay 후에도 결과가 숨은 탭 안에 남지 않게 하기 위한 것이다.
최근 component 실행 결과는 `새 Mix 만들기` 화면 상단의 `구성 포트폴리오 실행 결과` 박스에 먼저 표시하고,
그 아래에 입력 form과 weighted portfolio builder를 둔다.
다만 saved mix edit mode에서는 stale 결과를 숨기고 저장된 설정이 반영된 form을 먼저 보여준다.

2026-05-07 후속 UX 정리:

- saved mix replay는 더 이상 `새 Mix 만들기` 화면으로 강제 이동하지 않는다.
- `저장된 Mix` 안에서 `Portfolio Mix 검증 보드`를 보여준다.
- 이 보드는 `Mix Replay`, `Mix Data Trust`, `Component Real-Money`, `Workflow Registry`를 따로 판단한다.
- mix data trust는 GTAA cadence-aligned result-date gap을 hard blocker와 분리해 `CADENCE ALIGNED` / review 성격으로 보여준다.
- `Workflow Registry`가 `NOT RECORDED`이면 저장 mix가 성과 replay는 가능하지만 Practical Validation / Final Review registry에는 아직 기록되지 않은 상태다.
- `NOT RECORDED` 상태의 saved mix는 `Practical Validation으로 보내기`로 보낸다. 이 경로는 legacy Candidate / Proposal을 필수로 요구하지 않고, 비중이 정해진 mix를 Clean V2 source로 남겨 이후 Final Review에서 읽게 하는 경로다.
- 따라서 saved mix replay 결과와 개별 전략 handoff 판단이 한 화면에서 섞이지 않는다.

저장된 weighted portfolio는 live trading 승인 기록이 아니다.
후보 조합을 다시 재현하고 검증하기 위한 operator workflow artifact다.
저장된 후보 자체의 그래프 재검토는 `Operations > Candidate Library`에서 처리한다.

## Candidate Review 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Candidate Review
  -> 3. 운영 기록 저장 및 Portfolio Proposal 이동에서 선택 후보 확인
  -> Save Pre-Live Record 또는 Open Portfolio Mix Builder
  -> 저장된 Pre-Live record가 PORTFOLIO_PROPOSAL_READY이면 Open Portfolio Proposal
```

Latest / Operations history result handoff:

```text
Latest Backtest Run 또는 Operations > Backtest Run History selected record
  -> Review As Candidate Draft
  -> Backtest > Candidate Review > 1. Draft 확인 / Review Note 저장
  -> result snapshot / Real-Money signal / data trust snapshot 확인
  -> Candidate Packaging 저장 준비 확인
  -> Save Candidate Review Note
  -> CANDIDATE_REVIEW_NOTES.jsonl
  -> 2. Registry 저장에서 registry 후보 범위 판단
  -> Prepare Current Candidate Registry Row
  -> explicit Append To Current Candidate Registry
  -> 3. 운영 기록 저장 및 Portfolio Proposal 이동에서 선택 후보 확인
  -> PRE_LIVE_READY면 같은 화면에서 운영 기록 저장 및 다음 단계 판단
  -> Save Pre-Live Record
  -> PRE_LIVE_CANDIDATE_REGISTRY.jsonl append
  -> 저장된 record가 PORTFOLIO_PROPOSAL_READY이면 Portfolio Proposal로 이동
```

구분:

- Candidate Review는 후보를 투자 추천으로 확정하는 화면이 아니다.
- Candidate Review는 Candidate Packaging 작업 공간이며 한 화면 안에서 Draft 확인, Registry 저장, Pre-Live 운영 기록, Portfolio Proposal 이동 판단을 순서대로 처리한다.
- 상단의 `Candidate Packaging 산출물 흐름`은 Draft, Review Note, Current Candidate, Pre-Live Record, Proposal Ready를 카드로 보여준다.
- 각 큰 단계는 긴 설명문이나 card grid 대신 얇은 `왜 / 결과` brief strip으로 목적과 산출물을 먼저 보여준다.
- `Send To Portfolio Mix Builder`는 후보 row의 `compare_prefill`을 우선 사용하고,
  기존 strict annual seed 후보는 registry id 기반 기본값을 사용한다.
- GTAA seed 후보처럼 `compare_prefill`은 없지만 전략 `contract`가 남아 있는 경우에는
  해당 `contract`를 compare override로 변환해 form에 채운다.
- 후보 row에 `compare_prefill`도 없고 변환 가능한 `contract`도 없으면,
  사용자가 해결할 수 있는 설정 문제가 아니라 해당 후보 row의 compare 재진입 정보가 부족한 상태다.
- `1. Draft 확인`은 registry에 저장된 후보가 아니라 Candidate Packaging의 검토 초안을 다룬다.
- Candidate Review Note는 초안을 보고 남기는 operator decision 기록이며,
  현재 UI에서는 Draft 수신 정보와 operator reason / next action이 준비되어야 저장 버튼이 활성화된다.
- Candidate Review Note를 저장해도 current candidate registry에 자동 등록되지 않는다.
- `2. Registry 저장`은 `저장 범위 판단`으로 Current Candidate / Near Miss / Scenario / Stop 범위를 먼저 보여준다.
- `저장 범위 판단`은 route/readiness panel을 사용해 Scope, Scope Score, Blockers, 판정, 다음 행동을 표시한다.
- Registry scope의 추천 type, 허용 type, Review Decision은 compact badge strip으로 보여주고, 판단 기준 표와 기존 저장 기록은 기본 접힘 영역에 둔다.
- Registry row 저장값은 기본적으로 `Registry ID`, `Record Type`, `Candidate Title`, `Registry Notes`, 다음 단계에서 찾을 label만 펼쳐 보여주고, strategy family / name / role 같은 고급 식별값은 접힘 영역에 둔다.
- 범위 판단과 맞지 않는 record type은 append를 막는다.
- Review Note를 registry row로 남기려면 `2. Registry 저장`에서 row preview를 확인한 뒤
  같은 Candidate Packaging 안에서 `Append To Current Candidate Registry`를 명시적으로 눌러야 한다.
- 같은 Review Note가 이미 append된 경우에는 중복 append를 기본 차단하고, 의도적 revision 저장 체크박스를 켠 경우에만 다시 저장한다.
- append 성공 직후에는 새 registry row의 `registry_id` / `revision_id`를 session state에 남기고, `3. 운영 기록 저장 및 Portfolio Proposal 이동`에서 해당 후보를 자동 선택한다.
- Candidate selection label은 `Strategy Family | Role | Title | id=<registry_id>` 형식이다. 같은 family와 title이 반복되어도 `registry_id`로 방금 저장한 row를 찾을 수 있게 한다.
- `3. 운영 기록 저장 및 Portfolio Proposal 이동`은 먼저 선택 후보가 운영 기록으로 갈 current candidate인지, Portfolio Mix Builder로 돌아갈 후보인지 확인한다.
- `PRE_LIVE_READY`는 같은 화면에서 Pre-Live 운영 record를 저장할 수 있다는 뜻이고, `COMPARE_REVIEW_READY`는 실패가 아니라 Portfolio Mix Builder 재검토 경로다.
- `운영 기록 저장 및 다음 단계 판단`은 System Suggested Status를 기본값으로 보여주고, 사용자가 필요할 때만 `운영 상태 확인`과 접힌 운영 메모 / 다음 확인일을 수정하게 한다. 이 판정 박스는 입력 영역보다 위에 렌더링해, 저장 가능 여부를 먼저 읽고 아래에서 최소한의 운영 기록을 확인하는 흐름으로 보이게 한다.
- 공통 route/readiness panel은 긴 enum route를 underscore 기준으로 줄바꿈하고, 좁은 화면에서는 verdict 영역을 아래로 내려 가로 넘침 없이 읽히게 한다.
- Save / Open 버튼은 판단 기준과 JSON보다 먼저 보이게 하고, 상세 기준 / Pre-Live JSON / 선택 후보 raw detail은 하나의 `상세 보기` expander 안에 둔다.
- Pre-Live 운영 상태 영역은 Candidate Review 관점에서 필요한 promotion / suggested route / deployment / suggested status만 badge strip으로 보여주고, 추천 근거, 저장 후보 식별값, 판단 기준 표는 접힘 영역에 둔다.
- `Suggested Next Step`은 다음 검토 행동 제안이지 live trading 승인이나 최종 투자 판단이 아니다.
- `Save Pre-Live Record`는 live trading 승인이 아니라 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 paper / watchlist / hold 같은 운영 상태를 남기는 append-only 기록이다.
- `Open Portfolio Proposal`은 같은 후보의 현재 선택 상태가 저장된 Pre-Live record와 맞고 route가 `PORTFOLIO_PROPOSAL_READY`일 때 활성화된다.

Phase 28 이후 `저장된 Mix` 영역에는
`저장된 Mix Replay / 편집 Parity Snapshot`을 둔다.
이 표는 저장 포트폴리오를 다시 열거나 재실행하기 전에 아래 값이 남아 있는지 보여준다.

- compare 공용 입력: start / end / timeframe / option
- selected strategy list
- weights percent / date alignment
- strategy override map
- strategy별 핵심 override: cadence, universe, factor, overlay, handling, benchmark, guardrail, score 설정

## Portfolio Mix / Weighted Data Trust 흐름

Phase 28 이후 compare와 weighted portfolio 결과도 component별 data trust를 표시한다.

표시 위치:

- `Portfolio Mix Builder > 구성 포트폴리오 실행 상세 > Data Trust`
- `Weighted Portfolio Result > Component Data Trust`
- `Operations > Backtest Run History > Selected History Run > Saved Input & Context`

보는 값:

- 요청 종료일과 실제 결과 종료일
- result row 수
- price freshness status
- common latest price / newest latest price / latest-date spread
- excluded ticker 수
- malformed ticker 수
- warnings 수
- 간단한 interpretation

의미:

- component 실행 결과가 서로 같은 데이터 조건에서 나온 것인지 먼저 확인한다.
- weighted portfolio는 composite 결과이므로, 구성 전략별 데이터 상태를 먼저 확인한다.
- 이 표는 성과 비교표가 아니라 데이터 조건 확인표다.

## Real-Money / Guardrail Scope 흐름

Phase 28 이후 compare, history, saved portfolio에는
전략별 Real-Money / Guardrail 지원 범위를 같은 언어로 보여주는 표를 둔다.

표시 위치:

- `Portfolio Mix Builder > 구성 포트폴리오 실행 상세 > Real-Money / Guardrail`
- `Operations > Backtest Run History > Selected History Run > History Real-Money / Guardrail Scope`
- `저장된 Mix > Saved Portfolio Real-Money / Guardrail Scope`

현재 기준:

- annual strict는 full strict equity Real-Money / Guardrail 기준 surface다.
- strict quarterly prototype은 cadence / replay / portfolio handling 검증 단계이며, annual strict 수준의 promotion surface로 보지 않는다.
- Global Relative Strength는 ETF operability + cost / benchmark first pass이며, dedicated ETF underperformance / drawdown guardrail은 아직 없다.
- GTAA, Risk Parity Trend, Dual Momentum은 ETF Real-Money + ETF guardrail first pass로 본다.
- Equal Weight는 baseline 성격의 static ETF basket이지만, Phase35 이후 ETF operability, cost, benchmark 기반 Real-Money first pass와 saved replay 입력 보존을 지원한다.

의미:

- 모든 전략에 같은 실전 검증 UI를 강제로 붙였다는 뜻이 아니다.
- 전략별 성격에 맞는 검증 범위를 보여줘서 사용자가 annual / quarterly / ETF first-pass를 혼동하지 않게 한다.

## Backtest Run History 흐름

`Operations > Backtest Run History`는 compact summary 중심이다.
모든 selection history row를 그대로 저장하지 않는다.

대표 action:

- `Inspect`: 저장된 record를 읽는다.
- `Run Again`: 저장된 payload로 다시 실행한다.
- `Load Into Form`: 저장된 입력값을 single strategy form에 복원한다.

Phase 28 이후 Backtest Run History의 selected record 영역에는
`History Replay / Load Parity Snapshot`을 둔다.
이 표는 선택한 record에 재실행 / form 복원에 필요한 핵심 값이 남아 있는지 보여준다.

주요 확인 항목:

- strategy key, 입력 기간, timeframe, option
- universe / ticker / preset
- actual result start / end, result row count
- price freshness, excluded ticker, malformed price row
- strict family factor cadence, universe contract, overlay, portfolio handling
- annual strict real-money / guardrail / promotion settings
- GRS score, cash ticker, trend window, ETF operability inputs
- strategy별 Real-Money / Guardrail scope

## Candidate Review 안의 Pre-Live 운영 기록 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Candidate Review > 3. 운영 기록 저장 및 Portfolio Proposal 이동
  -> Packaging 확인 후보 선택
     -> 2. Registry 저장에서 방금 append한 후보 자동 선택
     -> 또는 current candidate 직접 선택
  -> 선택 후보 확인
  -> 운영 기록 저장 및 다음 단계 판단
     -> PORTFOLIO_PROPOSAL_READY / WATCHLIST_ONLY / PRE_LIVE_HOLD / REJECTED / SCHEDULED_REVIEW
  -> Save Pre-Live Record
  -> PRE_LIVE_CANDIDATE_REGISTRY.jsonl append
  -> 저장된 record와 현재 선택 상태가 맞으면 Portfolio Proposal로 이동
  -> 하단 보조 도구에서 active Pre-Live record 확인
```

구분:

- current candidate registry는 후보 자체를 정의한다.
- pre-live registry는 그 후보를 실전 전 어떻게 관찰하거나 보류할지 기록한다.
- Pre-Live 운영 기록은 별도 탭이 아니라 Candidate Review 3번 구간 안의 `선택 후보 확인 -> 운영 기록 저장 및 다음 단계 판단 -> 저장 및 이동` 순서형 화면으로 본다.
- Candidate Packaging에서 방금 저장한 후보는 자동 선택되지만, 사용자가 Candidate Review에서 다른 current candidate를 직접 고르는 것도 허용한다.
- `System Suggested Status`는 선택한 current candidate의 Real-Money 신호와 blocker에서 계산한 추천값이고, `운영 상태 확인` 값이 실제 Pre-Live registry에 저장되는 운영 상태다. 이 값은 최종 투자 판단이 아니라 실전 전 관찰 / 보류 상태다.
- 운영자가 추천값과 다른 status를 선택하면 UI는 경고를 보여주며, 의도적 override 근거를 `Operator Reason`에 남기도록 안내한다.
- `운영 기록 저장 및 다음 단계 판단`은 전략 성과 점수가 아니라 Pre-Live record가 다음 단계에서 읽을 수 있을 만큼 identity, result snapshot, Real-Money signal, status, reason, next action, review date, tracking plan을 갖췄는지 보는 route 확인이다.
- 이 route 확인은 `저장 범위 판단`과 같은 공통 판정 패턴을 사용하되, 독립된 큰 단계가 아니라 저장 버튼 위의 최종 확인으로 배치한다.
- `Save Pre-Live Record`는 live trading 승인 버튼이 아니다.
- `paper_tracking`도 실제 돈을 넣는다는 뜻이 아니라 paper 관찰 상태다.

## Portfolio Proposal 흐름

```text
CURRENT_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Portfolio Proposal
  -> 1. Proposal 후보 확인
  -> 후보 1개 선택
     -> 단일 후보 직행 평가
     -> Live Readiness 직행 route/readiness panel 확인
     -> proposal draft 저장 없이 Final Review 입력 후보로 사용
  -> 후보 2개 이상 선택
     -> 2. 목적 / 역할 / 비중 설계
     -> 3. Proposal 저장 및 다음 단계 판단
     -> Live Readiness 진입 평가 route/readiness panel 확인
     -> Portfolio Proposal JSON Preview 확인
     -> Save Portfolio Proposal Draft
     -> PORTFOLIO_PROPOSAL_REGISTRY.jsonl append
     -> 4. 저장된 Portfolio Proposal 확인에서 monitoring / Pre-Live / paper feedback / raw JSON inspect
     -> Final Review 탭으로 이동
```

구분:

- Portfolio Proposal은 current candidate 하나를 다시 저장하는 단계가 아니다.
- 단일 후보는 `LIVE_READINESS_DIRECT_READY` / `LIVE_READINESS_DIRECT_REVIEW_REQUIRED` / `LIVE_READINESS_DIRECT_BLOCKED` route로 기존 current candidate와 Pre-Live record가 Final Review 입력으로 충분한지 본다.
- 여러 후보는 `LIVE_READINESS_CANDIDATE_READY` / `PROPOSAL_DRAFT_READY` / `PROPOSAL_BLOCKED` route로 proposal draft 저장 가능성과 Final Review 입력 후보성을 본다. route label의 `Live Readiness`는 Phase31 legacy naming이며, 현재 active workflow에서는 Final Review 전 검증 준비로 읽는다.
- `Proposal Components`는 비교 기능이 아니라 포트폴리오에 넣을 구성 후보 선택이다. 여러 전략을 하나의 후보로 섞는 작업은 `Portfolio Mix Builder`에서 수행하고, 후보 간 read-only 비교 도구는 별도 기능으로 분리할 수 있다.
- `2. 목적 / 역할 / 비중 설계`에서는 active weight가 있는 proposal에 최소 1개 `core_anchor`가 필요하다. `return_driver`, `diversifier`, `defensive_sleeve`, `satellite`은 중심 후보를 보완하는 역할이고, `watch_only`는 보통 0% 관찰 후보로 둔다.
- target weight 합계가 100%가 아니거나 core anchor가 없으면 `PROPOSAL_BLOCKED`가 정상적으로 뜬다. UI는 이때 criteria 이름만 보여주지 않고, 비중 합계 조정 / core anchor 지정 같은 수정 안내를 함께 보여준다.
- `Proposal 저장 상태`는 proposal draft 저장 상태를 확인하는 가벼운 field다. 역할 / 비중 / blocker가 핵심이고, 구성 메모와 다음 확인일은 기본값을 둔 접힘 영역에서 필요할 때만 수정한다.
- saved portfolio는 재현 가능한 weight setup이고, proposal은 그 후보 묶음의 목적과 검토 이유를 남긴다.
- `Save Portfolio Proposal Draft`는 live trading 승인 버튼이 아니다.
- proposal 저장은 current candidate registry나 pre-live registry를 자동 변경하지 않는다.
- 현재 proposal UI는 optimizer가 아니며, target weight는 manual / equal-weight 초안 기준이다.
- 단일 후보 직행 평가는 role `core_anchor`, weight `100%`, capital scope `paper_only`를 자동 전제로 둔다.
- `Save Portfolio Proposal Draft`는 여러 후보를 묶는 포트폴리오 초안 작성 흐름에서만 노출한다. 단일 후보 direct path에는 proposal 저장 목록을 붙이지 않는다.
- saved proposal의 monitoring / Pre-Live feedback / paper feedback은 다중 후보 작성 흐름의 `4. 저장된 Portfolio Proposal 확인` 안에서 읽는다.
- 현재 `Paper Tracking Feedback`은 실제 paper PnL 시계열 자동 계산이 아니라 Pre-Live record에 저장된 최신 snapshot 비교다.

## Final Review 흐름

```text
Current Candidate 또는 Saved Portfolio Proposal
  -> Backtest > Final Review
  -> 1. 최종 검토 대상 선택
  -> 2. Validation 근거 확인
  -> 3. Robustness / Stress 질문 확인
  -> 4. Paper Observation 기준 확인
     -> 별도 Save Paper Tracking Ledger 없이 최종 검토 기록 안에 포함
  -> 5. 최종 판단 및 테스트 검증
     -> 최종 검토 결과 기록
     -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl append
  -> 6. 기록된 최종 검토 결과 확인
     -> Phase35 handoff inspect
```

구분:

- Final Review는 Portfolio Proposal 탭이 아니라 별도 workflow panel이다.
- Phase 31 이후 `Validation Pack`은 Final Review 안에서 단일 후보와 저장 proposal을 같은 검증 언어로 읽는다.
- validation route는 `READY_FOR_ROBUSTNESS_REVIEW`, `PAPER_TRACKING_REQUIRED`, `NEEDS_PORTFOLIO_RISK_REVIEW`, `BLOCKED_FOR_LIVE_READINESS`로 구분한다.
- Phase 32의 `Robustness / Stress Validation Preview`와 `Stress / Sensitivity Summary`도 Final Review 안에서 읽는다.
- `Result Status = NOT_RUN`은 아직 실제 stress runner가 실행되지 않았다는 뜻이다.
- Paper Observation은 별도 ledger 저장 버튼으로 노출하지 않고, benchmark / review cadence / trigger / baseline을 최종 검토 기록 안에 포함한다.
- Candidate Review와 Portfolio Proposal의 판단 field는 준비 기록이고, Final Review의 `최종 판단`만 실전 후보 선정 / 보류 / 거절 / 재검토를 명시하는 주 decision surface다.
- `최종 검토 결과 기록`은 `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 `SELECT_FOR_PRACTICAL_PORTFOLIO`, `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, `RE_REVIEW_REQUIRED` 중 하나를 append-only로 저장한다.
- Final Review 기록은 `최종 판단 완료` 기록이지 live approval, broker order, 자동매매 지시가 아니다.

## Final Review 완료 흐름

```text
Backtest > Final Review
  -> 검토 대상 선택
  -> Validation / Robustness / Paper Observation 확인
  -> 최종 판단 선택
     -> SELECT_FOR_PRACTICAL_PORTFOLIO / HOLD_FOR_MORE_PAPER_TRACKING
     -> REJECT_FOR_PRACTICAL_USE / RE_REVIEW_REQUIRED
  -> 최종 검토 결과 기록
  -> 기록된 최종 검토 결과 확인
     -> 투자 가능 후보 / 내용 부족 / 투자하면 안 됨 / 재검토 필요 확인
     -> Live Approval = Disabled / Order = Disabled 확인
```

구분:

- Final Review는 현재 active workflow의 마지막 panel이다.
- final decision registry가 최종 판단 원본이다.
- `decision_route`는 사용자-facing으로 `투자 가능 후보`, `내용 부족 / 관찰 필요`, `투자하면 안 됨`, `재검토 필요`로 읽는다.
- `phase35_handoff` 필드는 과거 row 호환을 위해 남아 있을 수 있지만, UI에서는 `Final Review Status` 또는 `Final Status`로 읽는다.
- 별도 Post-Selection registry나 Post-Selection panel은 만들지 않는다.
- Final Review도 live approval, broker order, 자동매매 지시가 아니다.

## Streamlit form 주의

Streamlit `st.form()` 내부 widget은 submit 전까지 app state가 즉시 rerun되지 않는다.
따라서 variant 선택처럼 아래 UI를 즉시 바꿔야 하는 값은 form 밖에 두는 것이 낫다.
반대로 한 번에 제출되어야 하는 detailed contract 입력은 form 내부에 유지할 수 있다.

## 갱신해야 하는 경우

- Backtest panel 구조가 바뀔 때
- strategy-specific form 위치나 payload key가 바뀔 때
- compare / weighted / saved portfolio 계약이 바뀔 때
- history record schema나 replay 가능 범위가 바뀔 때
- `Load Into Form`, `Run Again`, `Replay Saved Portfolio` semantics가 바뀔 때
