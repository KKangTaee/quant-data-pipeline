# Web Backtest UI Flow

## 목적

이 문서는 Streamlit Backtest 화면의 single strategy, compare, candidate review, Pre-Live 운영 기록, portfolio proposal, final review, Operations-owned backtest history, Candidate Library, saved weighted portfolio 흐름을 설명한다.
UI form, payload 복원, candidate review, history replay, candidate replay, saved weighted portfolio replay를 수정할 때 먼저 확인한다.

## 핵심 파일

| 파일 | 역할 |
|---|---|
| `app/web/streamlit_app.py` | top navigation과 page entry |
| `app/web/reference_guides.py` | `Reference > Guides`의 제품형 workflow guide, portfolio flowchart, decision gates, reference drawer |
| `app/web/ops_review.py` | `Operations > Ops Review`의 triage flow, 웹앱 run health, action inbox, failure artifact, log, system snapshot dashboard |
| `app/web/overview_dashboard.py` | `Workspace > Overview`에서 Backtest registry 기반 후보 Top 3, candidate funnel, next actions, recent activity dashboard render |
| `app/web/overview_dashboard_helpers.py` | Overview dashboard용 current candidate / Pre-Live / proposal / history / saved portfolio 집계와 candidate priority scoring helper |
| `app/web/backtest_common.py` | Backtest 공용 preset, session state, 3단계 stage routing compatibility, universe / real-money / guardrail input, status label helper |
| `app/web/backtest_workflow_routes.py` | `Backtest Analysis`, `Practical Validation`, `Final Review` visible stage와 legacy panel route mapping |
| `app/web/backtest_analysis.py` | `Backtest Analysis` stage wrapper. Single Strategy와 Compare & Portfolio Builder를 submode로 렌더링 |
| `app/web/backtest_single_strategy.py` | `Single Strategy` 화면 orchestration. strategy 선택, prefill notice, form dispatch, latest result 연결 |
| `app/web/backtest_single_forms.py` | Single Strategy strategy-specific form render. Equal Weight, GTAA, GRS, Risk Parity, Dual Momentum, Quality / Value 계열 |
| `app/web/backtest_single_runner.py` | Single Strategy payload 실행 dispatch, DB-backed runtime 호출, latest bundle state 저장, run history append |
| `app/web/backtest_compare.py` | `Compare & Portfolio Builder` 화면 render, compare 실행, weighted portfolio builder, saved portfolio replay / load, candidate handoff |
| `app/web/backtest_result_display.py` | Backtest 결과 공용 display. summary, chart, data trust, real-money detail, selection history, compare result helper |
| `app/web/backtest_history.py` | `Operations > Backtest Run History` 화면 render, selected record inspect, run again / load into form / candidate draft handoff |
| `app/web/backtest_history_helpers.py` | History table row, replay payload, replay parity, Real-Money / Guardrail scope helper |
| `app/web/backtest_candidate_library.py` | `Operations > Candidate Library` 화면 render. 저장된 current / Pre-Live 후보 inspect와 저장 contract 기반 result curve rebuild |
| `app/web/backtest_candidate_library_helpers.py` | Candidate Library registry join, table row, replay payload 생성, ETF / strict annual equity 후보 replay runtime dispatch helper |
| `app/web/pages/backtest.py` | Backtest page entry, workflow navigation, panel dispatch shell. 주요 panel 본문은 `app/web/backtest_*.py` module이 담당 |
| `app/web/backtest_ui_components.py` | Backtest UI 공용 status card, artifact pipeline, compact badge strip, stage brief strip, route/readiness panel render helper |
| `app/web/backtest_practical_validation.py` | `Practical Validation` stage render. Clean V2 source 확인, 검증 프로필 입력, actual runtime replay 실행 버튼, V2 practical diagnostics board, Final Review handoff를 담당 |
| `app/web/backtest_practical_validation_helpers.py` | Clean V2 selection source / validation profile / 12개 Practical Diagnostics result 생성, 저장, Final Review handoff helper |
| `app/web/backtest_practical_validation_curve.py` | Practical Validation curve normalize, compact curve records, curve provenance, benchmark parity helper |
| `app/web/backtest_practical_validation_replay.py` | Practical Validation source를 기존 strategy runtime으로 명시 replay하고 actual component / portfolio curve evidence를 만드는 helper |
| `app/web/backtest_candidate_review.py` | Candidate Review / Candidate Packaging / Pre-Live 운영 기록 화면 render logic |
| `app/web/backtest_candidate_review_helpers.py` | Candidate Review 판단, Review Note / registry 변환, Pre-Live status 추천 / draft 변환 / Portfolio Proposal 진입 readiness score helper |
| `app/web/backtest_portfolio_proposal.py` | 단일 후보 직행 평가, 다중 후보 Portfolio Proposal 후보 선택 / 목적 / 역할 / 비중 설계, proposal draft 저장, 저장된 proposal monitoring / feedback section render logic |
| `app/web/backtest_portfolio_proposal_helpers.py` | Portfolio Proposal row 생성, 단일 후보 direct readiness / proposal save readiness 평가, 공유 validation / robustness 계산 helper, monitoring / Pre-Live / paper feedback table helper |
| `app/web/backtest_final_review.py` | Final Review 화면 render. 단일 후보 / 저장 proposal 선택, Validation / Robustness / Paper Observation 기준 확인, 최종 판단 기록, saved final decision review |
| `app/web/backtest_final_review_helpers.py` | Final Review source 선택, validation 재사용, inline paper observation snapshot, final evidence / save readiness / decision row / display helper |
| `app/web/final_selected_portfolio_dashboard.py` | `Operations > Selected Portfolio Dashboard` 화면 render. Final Review에서 선정된 포트폴리오를 운영 대상으로 읽고 compact selected portfolio picker / Snapshot / tabbed Performance Recheck / Portfolio Monitoring Review Signals / optional Actual Allocation / Audit을 보여준다 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | Selected Portfolio Dashboard의 table / component / evidence / value / holding input / drift / alert preview / filter helper |
| `app/web/runtime/backtest.py` | UI payload를 실행 가능한 runtime call로 변환 |
| `app/web/runtime/candidate_registry.py` | current candidate / review note / pre-live registry JSONL read / append helper |
| `app/web/runtime/portfolio_proposal.py` | portfolio proposal draft JSONL read / append helper |
| `app/web/runtime/paper_portfolio_ledger.py` | paper portfolio tracking ledger JSONL read / append helper |
| `app/web/runtime/final_selection_decisions.py` | final portfolio selection decision JSONL read / append helper |
| `app/web/runtime/portfolio_selection_v2.py` | Clean V2 selection source, practical validation result, Final Decision V2, selected monitoring log, saved mix JSONL helper |
| `app/web/runtime/final_selected_portfolios.py` | final selection decision registry를 read-only dashboard row, selected component replay recheck, component contribution, optional Allocation Check / drift preview로 변환하는 Phase36 helper |
| `.note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl` | local run history. 보통 commit하지 않음 |
| `.note/finance/saved/SAVED_PORTFOLIOS.jsonl` | saved portfolio persistence |
| `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | proposal draft persistence. 첫 proposal 저장 시 생성 |
| `.note/finance/registries/PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | paper tracking ledger persistence. 첫 paper ledger 저장 시 생성 |
| `.note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl` | Clean V2 Backtest Analysis source persistence. 첫 후보 source 선택 시 생성 |
| `.note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` | Clean V2 Practical Validation result persistence. 첫 검증 결과 저장 시 생성 |
| `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | Clean V2 final selection decision persistence. 첫 final decision 저장 시 생성 |
| `.note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | 선정 이후 monitoring snapshot persistence. 사용자가 명시 저장할 때 생성 |

## 화면 흐름

Backtest page는 후보 선정 주 흐름만 보여준다.

Backtest 주 흐름:

- `Backtest Analysis`: Single Strategy 실행, Compare, weighted portfolio builder, 저장된 비중 조합 replay를 통해 후보 source를 만들고 `PORTFOLIO_SELECTION_SOURCES.jsonl`에 Clean V2 source로 저장한다.
- `Practical Validation`: 선택된 단일 전략 / Compare 후보 / Saved Mix source를 실전 투입 전 조건으로 검증한다. 사용자는 방어형 / 균형형 / 성장형 / 전술·헤지형 / 사용자 지정 profile과 5개 답변을 고르고, 화면은 Input Evidence와 12개 Practical Diagnostics를 `PASS / REVIEW / BLOCKED / NOT_RUN`으로 분리해 보여준다. 결과는 `PRACTICAL_VALIDATION_RESULTS.jsonl`에 저장하며 사용자 최종 메모는 받지 않는다.
- `Final Review`: Practical Validation result와 diagnostics 요약, Robustness / Paper Observation 기준을 한 화면에서 확인하고, 최종 선정 / 보류 / 거절 / 재검토 판단과 최종 메모를 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에 저장한다.

Practical Validation V2의 현재 구현은 최소 contract를 Input Evidence로 읽고, profile-aware practical diagnostics board를 만든다.
현재 board는 compact curve snapshot 또는 DB price proxy curve를 사용해 rolling validation, stress window 구간 성과, simple baseline challenge, component correlation / risk contribution proxy, drop-one / weight perturbation sensitivity, ETF price / volume operability proxy를 계산한다.
사용자가 명시적으로 `실제 전략 replay 실행`을 누르면 기존 strategy runtime으로 source를 다시 실행하고, replay curve를 diagnostics의 우선 evidence로 사용한다.
화면은 curve provenance와 benchmark parity를 표시해 결과가 actual runtime replay인지, embedded snapshot인지, DB price proxy인지 구분한다.
아직 ETF holdings-level look-through, expense ratio / bid-ask spread / AUM connector, FRED 기반 VIX / credit spread / yield curve connector는 후속 계산이며 `NOT_RUN` 또는 `REVIEW`로 명시한다.

Legacy / compatibility 흐름:

- `Candidate Review`, `Portfolio Proposal`, 기존 Pre-Live registry, 기존 proposal registry는 바로 삭제하지 않는다. 다만 새 주 흐름의 필수 join 조건이 아니라 legacy inspector / archive compatibility로 낮춘다.
- 기존 `Single Strategy`, `Compare & Portfolio Builder`, `Candidate Review`, `Portfolio Proposal` route request는 `backtest_workflow_routes.py`에서 3단계 stage로 매핑한다.

Operations 보조 화면:

- `Operations > Ops Review`: 웹앱 ingestion / refresh / factor job의 run health를 점검한다. triage flow, 최근 실행 상태, action inbox, failure CSV, run artifact, related logs, runtime snapshot을 보여주며, job 실행은 `Ingestion`, backtest replay는 `Backtest Run History`, 후보 replay는 `Candidate Library`로 분리한다.
- `Operations > Backtest Run History`: 저장된 실행 기록을 inspect하고, 가능한 경우 run again, load into form, candidate draft handoff를 수행한다. 후보 검토 흐름의 주 단계가 아니라 과거 실행을 다시 열기 위한 운영 / 재현 도구로 둔다.
- `Operations > Candidate Library`: `CURRENT_CANDIDATE_REGISTRY.jsonl`과 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 읽어 저장된 후보를 다시 열어 본다. registry에는 compact snapshot만 남으므로, 그래프 / result table이 필요할 때 저장 contract로 DB-backed result curve를 재생성한다. 후보 등록 단계가 아니라 보관함 / 재검토 도구다.
- `Operations > Selected Portfolio Dashboard`: `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`에서 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 row만 읽어 최종 선정 포트폴리오의 compact 선택, Snapshot, 기간 확장 Performance Recheck tabs, Portfolio Monitoring의 Review Signals / Why Selected / optional Actual Allocation / Audit을 보여준다. live approval / broker order / auto rebalance는 disabled로 둔다.

## 현재 Reference Guide 제품 흐름

`Reference > Guides`의 사용자-facing 흐름은 아래 순서로 읽는다.

```text
Ingestion / Data Trust
  -> Single Strategy Backtest
  -> Real-Money Signal
  -> Hold / Blocker Resolution
  -> Compare
  -> Candidate Packaging
     -> Draft 확인 / Review Note 저장 / Registry 저장 / Pre-Live 운영 기록 / Portfolio Proposal 이동 판단
  -> Compare 재검토 또는 Portfolio Proposal
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
- `Robustness / Stress Validation Pack`은 Phase 32에서 추가된 surface다. stress 검증 실행 전 period / contract / benchmark / CAGR / MDD / compare evidence가 충분한지 확인하고, stress / sensitivity summary row와 Phase33 paper ledger handoff를 보여준다. 아직 실제 stress sweep을 실행했다는 뜻은 아니다.
- `Paper Tracking Ledger`는 Phase 33에서 추가된 append-only 기록 흐름이지만, 현재 주 사용자 흐름에서는 Final Review의 inline paper observation 기준으로 흡수한다. 기존 ledger row는 backward compatibility / 과거 QA 기록으로 읽을 수 있다.
- Phase 35에서 별도 `Post-Selection Guide` panel은 과한 단계로 판단해 active workflow에서 제거했다. 최종 판단과 투자 가능 / 투자하면 안 됨 / 내용 부족 / 재검토 필요 해석은 `Backtest > Final Review`의 saved final decision review에서 확인한다.
- Phase 36에서 선정 이후 운영 확인은 `Backtest` 주 workflow가 아니라 `Operations > Selected Portfolio Dashboard`로 분리했다. 이 화면은 Final Review selected row를 read-only로 읽고, 사용자가 지정한 시작일 / 종료일 / 가상 투자금으로 selected component contract를 다시 replay해 최신 기간 성과를 확인한다. `Review Signals`는 최신 Performance Recheck와 사용자가 명시적으로 반영한 Actual Allocation 상태를 `Clear / Watch / Breached / Needs Input / Optional`로 번역한다. current value 기반 Actual Allocation을 기본 입력으로 두고, shares x price / current weight 입력은 advanced 입력으로 둔다. shares x price 입력에서는 DB latest close를 보조로 불러올 수 있지만, account holding 자동 연결이나 주문 초안은 만들지 않는다.

현재 Guides 화면은 제품형 의사결정 guide로 정리한다.

| 묶음 | 내용 |
|---|---|
| `Portfolio Selection Guide` hero | 제품 안내 첫 화면으로, 현재 workflow와 runtime / git 상태를 compact badge로 보여준다. 개발용 `Runtime / Build`는 하단 접힘 `System status`로 낮춘다 |
| `현재 진행 상황 선택` | 단일 후보, 여러 후보 묶음, 저장된 비중 조합, 보류 / 재검토 중 사용자의 현재 상황을 먼저 고른다 |
| `전체 1~10 단계에서 현재 위치` | 선택 버튼 바로 아래에 제품형 compact timeline을 둔다. 선택 경로에 따라 `필수`, `반복`, `직행`, `선행`, `생략`, `보류` 같은 상태 라벨을 붙여 현재 위치와 생략되는 단계를 먼저 해석하게 한다 |
| `선택한 경로 요약` | `선택한 목표`, `진행 순서`, `건너뛰거나 조심할 단계`, `생성 / 참조 기록`으로 선택 경로의 화면 순서와 기록 경계를 짧게 보여준다 |
| `Portfolio Flow` | 선택 경로를 GraphViz flowchart로 보여주고, 환경상 GraphViz 렌더링이 실패하면 compact visual fallback으로 표시한다. chart node는 큰 흐름을 맡고, 긴 설명은 아래 checkpoint 패널로 넘긴다 |
| `선택한 경로의 핵심 체크포인트` | 선택 경로에서 실제로 놓치면 안 되는 checkpoint를 카드로 보여준다. 단일 후보, 여러 후보 묶음, 저장된 비중 조합, 보류 / 재검토마다 같은 workflow를 다르게 해석한다 |
| `Decision Gates` | 단계 번호 대신 `Compare로 가도 되는가`, `Candidate로 남겨도 되는가`, `Proposal로 묶어도 되는가`, `Final Review를 기록해도 되는가` 같은 사용자 질문 기준으로 Go / Review / Stop을 보여준다 |
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
| `저장된 비중 조합 경로` | saved weighted portfolio setup은 후보 registry가 아니라 재사용 weight setup이므로 Candidate Review가 아니라 `포트폴리오 후보 초안으로 보내기`로 proposal registry에 연결한다 |
| `보류 / 재검토 경로` | hold / blocked / insufficient evidence / re-review 상태에서는 Final Review 직행이 아니라 원인 화면으로 되돌아간다 |

## Phase 36 Selected Portfolio Dashboard

Phase36은 Final Review 이후 새 판단 저장 단계를 추가하지 않는다.
Backtest workflow는 Final Review에서 끝나고,
선정 이후 확인은 Operations 화면에서 한다.

```text
Backtest > Final Review
  -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl
  -> Operations > Selected Portfolio Dashboard
```

구현 책임:

| 파일 | 역할 |
|---|---|
| `app/web/runtime/final_selected_portfolios.py` | Final Review final decision row를 읽고 selected dashboard row / status summary / selected component performance recheck / current weight 또는 value / holding input 기반 drift check / drift alert preview로 변환 |
| `app/web/final_selected_portfolio_dashboard.py` | Operations dashboard 화면 render, compact selected portfolio picker, Snapshot, Performance Recheck setup + result tabs, Portfolio Monitoring Review Signals / Why Selected / optional Actual Allocation / Audit 표시 |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | dashboard table, component table, evidence table, value / holding input table, drift table, alert preview table, filter helper |
| `app/web/streamlit_app.py` | Operations navigation에 `Selected Portfolio Dashboard` page 등록 |

데이터 기준:

- source-of-truth: `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`
- selected filter:
  - `decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO`
  - 또는 `selected_practical_portfolio == true`
- dashboard write policy:
  - read-only
  - 새 final decision row를 저장하지 않음
  - proposal / candidate registry를 덮어쓰지 않음
- performance recheck:
  - selected component의 `registry_id`로 Current Candidate Registry의 replay contract를 찾음
  - 사용자가 지정한 recheck start / end / virtual capital로 DB-backed strategy replay 실행
  - portfolio value, total return, CAGR, MDD, benchmark spread, component contribution, strongest / weakest periods 표시
  - 새 registry row를 저장하지 않음

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
- Performance Recheck는 latest result 확인 도구이며 live approval이나 수익 보장 표현이 아니다.
- current value 기반 Actual Allocation을 기본 입력으로 두고, current weight 직접 입력과 shares x price 입력 기반 drift check는 advanced 입력으로 둔다.
- DB latest close 조회는 shares x price 입력을 돕는 보조 기능이다.
- Drift Alert / Review Trigger Preview는 read-only 해석이며 alert registry를 저장하지 않는다.
- account holding 자동 연결, broker order, auto rebalance는 후속 phase에서 별도 계약을 정한 뒤 구현한다.

## Phase 30 Portfolio Proposal 계약

Phase 30 두 번째 작업 이후 Portfolio Proposal은 단순 weighted portfolio 저장값이 아니라,
후보 묶음의 목적과 검토 근거를 함께 담는 제안 초안으로 본다.

상세 계약은 아래 문서를 기준으로 한다.

- `.note/finance/phases/phase30/PHASE30_PORTFOLIO_PROPOSAL_CONTRACT_SECOND_WORK_UNIT.md`

Phase 30 네 번째 작업 이후 기본 저장 위치는
`.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이다.
첫 proposal draft를 저장할 때 파일이 생성되며,
append / load helper는 `app/web/runtime/portfolio_proposal.py`가 담당한다.

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
| 7 | Compare / Portfolio Builder module split | compare form / 실행 / weighted portfolio / saved portfolio replay | 완료: `backtest_compare.py`로 분리. 향후 더 세분화할 경우 weighted / saved portfolio를 별도 module로 뺄 수 있다 |
| 8 | Result display helpers | latest result, charts, data trust, real-money details | 완료: 공용 display는 `backtest_result_display.py`로 분리 |
| 9 | Backtest common helper | preset, session state, 입력 컴포넌트, status label | 완료: `backtest_common.py`가 transitional shared module로 관리한다. 향후 규모가 다시 커지면 `backtest_state.py`, `backtest_strategy_inputs.py`, `backtest_presets.py`로 추가 분리한다 |

분리 원칙:

- 먼저 함수 이동만 하고 behavior를 바꾸지 않는다.
- module split 후에는 `python3 -m py_compile app/web/pages/backtest.py app/web/backtest_*.py app/web/streamlit_app.py`를 기본 확인한다.
- Streamlit session state key는 이름을 바꾸지 않는 것을 기본으로 한다.
- registry file path와 append-only semantics는 helper 이동 후에도 유지한다.
- 한 번에 여러 workflow를 옮기지 않는다.

Phase 30 third work unit status:

- `app/web/runtime/candidate_registry.py`로 registry JSONL read / append helper를 먼저 분리했다.
- 분리된 대상은 current candidate registry, candidate review notes, pre-live candidate registry의 file path constant와 I/O helper다.
- `app/web/runtime/portfolio_proposal.py`로 proposal draft registry read / append helper도 추가했다.
- Candidate Review는 `app/web/backtest_candidate_review.py`와 `app/web/backtest_candidate_review_helpers.py`로 분리되어, `backtest.py`에는 panel wrapper와 cross-panel handoff call만 남아 있다.
- 긴 route/status 문자열은 `app/web/backtest_ui_components.py`의 wrapping card / route panel을 사용해 `st.metric` 말줄임을 피한다.
- Backtest shell은 중복 제목을 제거하고, `Single Strategy -> Compare & Portfolio Builder -> Candidate Review -> Portfolio Proposal -> Final Review`를 주 workflow navigation으로 보여준다. `History`는 메인 흐름에서 제외하고 `Operations > Backtest Run History` page로 연다.
- Backtest Run History는 `app/web/backtest_history.py`와 `app/web/backtest_history_helpers.py`로 분리되어, `backtest.py`에는 History 화면 render / replay helper 본문이 남아 있지 않다.
- Portfolio Proposal은 `app/web/backtest_portfolio_proposal.py`와 `app/web/backtest_portfolio_proposal_helpers.py`로 분리되어, `backtest.py`에는 panel wrapper만 남아 있다.
- Final Review는 `app/web/backtest_final_review.py`와 `app/web/backtest_final_review_helpers.py`로 분리되어, `backtest.py`에는 panel dispatch만 남아 있다.
- Phase35 보정 이후 Post-Selection Guide module과 panel dispatch는 제거했다. Final Review가 현재 workflow의 마지막 active panel이다.
- Single Strategy는 `app/web/backtest_single_strategy.py`, `app/web/backtest_single_forms.py`, `app/web/backtest_single_runner.py`로 분리되어, form render와 runtime dispatch를 page shell에서 제거했다.
- Compare / Portfolio Builder는 `app/web/backtest_compare.py`로 분리되어, compare 실행, weighted portfolio builder, saved portfolio replay / load, current-candidate compare prefill을 page shell에서 제거했다.
- Latest result / compare result / Real-Money detail / selection history display는 `app/web/backtest_result_display.py`가 담당한다.
- 공용 preset, session state, 입력 컴포넌트, status label은 `app/web/backtest_common.py`가 담당한다. 이 파일은 다음 리팩토링에서 더 잘게 나눌 수 있는 transitional shared module이다.
- 따라서 `app/web/pages/backtest.py`는 Backtest page shell과 workflow navigation만 유지한다.

## Single Strategy 흐름

```text
strategy 선택
  -> strategy-specific form 입력
  -> _handle_backtest_run(...)
  -> app/web/runtime/backtest.py run_*_backtest_from_db(...)
  -> latest result bundle 저장
  -> result table / summary / selection history / real-money surface 표시
  -> history record 저장
```

주의:

- `Load Into Form`은 입력값만 복원한다.
- 복원 후 결과를 갱신하려면 사용자가 다시 실행해야 한다.
- selection history가 있는 전략은 latest result의 `Selection History Table` / `Interpretation Summary`에서 상세를 본다.

## Real-Money Compare 진입 평가 흐름

`Real-Money > 현재 판단`에는 `5단계 Compare 진입 평가` 박스를 둔다.

목적:

- `Promotion`, `Deployment`, blocker 정보를 10점 척도로 요약한다.
- 사용자가 4단계 Hold 해결을 마치고 5단계 Compare로 넘어갈 수 있는지 먼저 판단하게 한다.
- 이 평가는 live trading approval이나 주문 지시가 아니라 Compare 진입 보조 신호다.

기준:

- `Promotion Decision != hold`
- `Deployment Readiness / Deployment Status != blocked`
- 핵심 blocker 없음

점수 해석:

- `8.0 / 10` 이상이면 깔끔하게 5단계 Compare로 진행 가능한 상태다.
- `8.0 / 10` 미만이어도 위 핵심 기준을 만족하면 Compare로는 넘길 수 있지만, 개선 항목을 같이 확인한다.
- 위 핵심 기준을 만족하지 못하면 점수와 무관하게 4단계에서 blocker를 먼저 해결한다.

표시:

- `Readiness Score`: 10점 만점의 Compare 진입 점수
- `판정`: `5단계 Compare 진행 가능`, `5단계 Compare 진행 가능, 개선 항목 동시 확인`, `4단계에서 먼저 blocker 해결`
- `다음 행동`: Compare로 넘길지, blocker를 먼저 해결할지 설명
- `점수 계산 기준 보기`: Promotion / Deployment / Core Blocker별 점수 근거

## Compare 흐름

```text
strategy multi-select
  -> Compare Period & Shared Inputs
  -> strategy별 box에서 variant / advanced inputs 설정
  -> Run Strategy Comparison
  -> strategy별 result bundle 실행
  -> 5단계 Compare 검증 보드
  -> comparison table / overlay / focused strategy 표시
  -> Weighted Portfolio Builder로 전달
```

현재 UX 기준:

- common date / timeframe / option은 공유 입력으로 둔다.
- strategy-specific advanced inputs는 strategy별 box 안에서 보이게 한다.
- variant 변경은 버튼 없이 즉시 아래 옵션이 바뀌는 방향이 선호된다.
- 최대 compare 전략 수는 operator가 읽을 수 있는 범위로 유지한다.

Compare 결과 상단에는 개별 전략용 `Compare 검증 보드`를 둔다.

목적:

- Compare 결과 중 어떤 단일 전략을 `Practical Validation`으로 넘길지 명시적으로 선택하게 한다.
- Compare 실행 정상 여부, 선택 후보의 Data Trust, Real-Money gate, 상대 비교 근거를 10점으로 요약한다.
- Data Trust는 Readiness를 강제로 `6.4` 같은 값으로 누르는 cap이 아니라, 별도 `OK / WARNING / BLOCKED` gate로 같이 표시한다.
- 이 평가는 current candidate registry 저장, Pre-Live 승인, live trading approval이 아니라 후보 검토 초안으로 넘길 수 있는지 보는 신호다.

기준:

- `Compare Run`: 2개 이상 전략이 정상 비교됐는지
- `Data Trust`: 선택 후보의 결과 기간, 가격 최신성, excluded / malformed ticker가 해석 가능한지
- `Real-Money Gate`: `Promotion != hold`, `Deployment != blocked`, 핵심 blocker 없음인지
- `Relative Evidence`: CAGR, End Balance, Maximum Drawdown, Sharpe 중 설명 가능한 상대 근거가 있는지

점수 해석:

- `8.0 / 10` 이상이면 `PASS`로 보고 Practical Validation으로 진행 가능하다.
- `6.5 / 10` 이상이면 `CONDITIONAL`로 보고 조건부 진행 가능하되 Practical Validation에서 확인할 약점과 gap을 같이 남긴다.
- 짧은 실제 종료일 불일치, warning, excluded / malformed ticker 같은 Data Trust 이슈는 score를 cap하지 않고 warning으로 표시한다.
- GTAA처럼 `interval > 1`, `option=month_end`인 cadence 전략은 요청 종료일이 다음 정상 cadence close 전이면 `Data Trust blocked`가 아니라 cadence-aligned review로 표시한다.
- 가격 최신성 error 또는 결과 기간이 크게 비는 Data Trust blocked 상태, Real-Money blocker, 비교 실패, 상대 근거 없음은 `FAIL`로 보고 Compare에서 먼저 재확인한다.

실행:

- 통과 또는 조건부 통과 상태에서는 `Practical Validation으로 보내기` 버튼으로 단일 전략 Clean V2 source를 만들 수 있다.
- 이 버튼은 registry 저장이나 live approval이 아니라 Practical Validation 입력 source를 저장하는 동작이다.

저장된 비중 조합 replay:

- `Mix 재실행 및 검증`은 저장된 weighted portfolio mix 자체와 그 구성 전략 compare를 함께 복원한다.
- UI에서는 `저장된 비중 조합` 화면 안에서 `저장 Mix Replay 결과`와 `Portfolio Mix 검증 보드`를 바로 보여준다.
- `Portfolio Mix 검증 보드`는 saved mix 자체의 replay 가능 여부, mix data trust, 구성 전략 Real-Money gate, Clean V2 검증 기록 여부를 분리해서 보여준다.
- 저장 mix는 reusable setup이므로, replay 성과가 좋아도 자동으로 최종 판단 기록이 되지 않는다. `Workflow Registry`가 `NOT RECORDED`이면 Practical Validation / Final Review 쪽 기록이 아직 없다는 뜻이다.
- 이 경우 사용자는 `Practical Validation으로 보내기`로 mix 전체를 Clean V2 source로 저장한다. Saved mix는 이미 비중이 정해진 포트폴리오 조합이므로, 단일 전략 후보 handoff와 분리한다.
- 개별 전략을 Practical Validation으로 보낼 때만 `개별 전략 비교` 화면의 `Compare 검증 보드`를 사용한다. mix는 current weighted mix handoff 또는 saved mix validation board를 사용한다.

## Strategy Capability Snapshot 흐름

Phase 28 이후 `Single Strategy`와 `Compare & Portfolio Builder`의 strategy box에는
`Strategy Capability Snapshot` 접힘 영역을 둔다.

목적:

- annual strict, quarterly strict, price-only ETF 전략이 서로 다른 이유를 UI에서 먼저 설명한다.
- cadence, data trust, selection history, Real-Money/Guardrail, history/replay 지원 범위를 표로 보여준다.
- 기능이 없는 것처럼 보이는 부분이 버그인지, 아직 annual 중심으로 남긴 의도적 차이인지 구분하게 한다.

현재 기준:

- strict annual은 가장 성숙한 Real-Money / Guardrail surface로 설명한다.
- strict quarterly prototype은 Data Trust와 Portfolio Handling은 지원하지만, Real-Money promotion / Guardrail 판단은 아직 annual strict 중심으로 설명한다.
- Equal Weight는 static ETF basket baseline이지만, Single / Compare 실행에서는 ETF Real-Money first pass를 붙여 promotion / shortlist / deployment gate를 읽는다.
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
Backtest > Compare & Portfolio Builder
  -> 개별 전략 비교 화면
  -> 개별 전략 5단계 Compare 결과
  -> compare result bundles
  -> weight 입력
  -> optional GTAA 70 / Equal Weight 30 quick mix
  -> make_monthly_weighted_portfolio(...)
  -> weighted result
  -> 현재 Mix를 Practical Validation으로 보내기
  -> Save Portfolio Mix

Backtest > Compare & Portfolio Builder
  -> 저장된 비중 조합 화면
  -> Mix 재실행 및 검증 or 전략 비교에서 수정하기
  -> Mix 재실행 및 검증은 같은 화면에서 replay result / Portfolio Mix 검증 보드 / weighted result 확인
  -> workflow 기록이 없으면 Practical Validation으로 보내기
  -> 전략 비교에서 수정하기는 기존 결과를 숨기고 개별 전략 비교 form을 form-first 상태로 다시 채움
```

구분:

- `개별 전략 비교`: 새 compare를 실행하고, 개별 전략 후보를 Practical Validation으로 보낼 수 있는지 Compare 검증 보드로 판단한다. 이어서 weighted portfolio mix를 만들고, 저장 여부와 무관하게 mix 전체를 Practical Validation으로 보낼 수 있다.
- `저장된 비중 조합`: `.note/finance/saved/SAVED_PORTFOLIOS.jsonl`에 저장한 reusable setup을 다시 실행하고 mix-level 검증으로 읽는다.
- `전략 비교에서 수정하기`: 저장된 compare 구성과 weight를 form에 다시 채운다. 검증 버튼이 아니라 편집 / 재구성 진입이며, 기존 stale compare / weighted 결과는 숨기고 사용자가 먼저 설정을 수정하게 한다.
- `Mix 재실행 및 검증`: 저장 당시 context로 compare와 weighted portfolio를 다시 실행하고, `저장된 비중 조합` 화면 아래에 replay 결과와 mix 검증 보드를 바로 렌더링한다.

2026-05-06 이후 Compare workspace의 `개별 전략 비교` / `저장된 비중 조합` 전환은 `st.tabs`가 아니라 상태를 가진 선택 UI로 관리한다.
이는 saved mix replay 후에도 결과가 숨은 탭 안에 남지 않게 하기 위한 것이다.
최근 compare 결과는 `개별 전략 비교` 화면 상단의 `개별 전략 Compare 결과` 박스에 먼저 표시하고,
그 아래에 입력 form과 weighted portfolio builder를 둔다.
다만 `전략 비교에서 수정하기`로 들어온 saved mix edit mode에서는 stale 결과를 숨기고 저장된 설정이 반영된 form을 먼저 보여준다.

2026-05-07 후속 UX 정리:

- saved mix replay는 더 이상 `개별 전략 비교` 화면으로 강제 이동하지 않는다.
- `저장된 비중 조합` 안에서 `Portfolio Mix 검증 보드`를 보여준다.
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
  -> Save Pre-Live Record 또는 Open Compare Picker
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
- `Send To Compare`는 후보 row의 `compare_prefill`을 우선 사용하고,
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
- `3. 운영 기록 저장 및 Portfolio Proposal 이동`은 먼저 선택 후보가 운영 기록으로 갈 current candidate인지, Compare로 돌아갈 후보인지 확인한다.
- `PRE_LIVE_READY`는 같은 화면에서 Pre-Live 운영 record를 저장할 수 있다는 뜻이고, `COMPARE_REVIEW_READY`는 실패가 아니라 Compare 재검토 경로다.
- `운영 기록 저장 및 다음 단계 판단`은 System Suggested Status를 기본값으로 보여주고, 사용자가 필요할 때만 `운영 상태 확인`과 접힌 운영 메모 / 다음 확인일을 수정하게 한다. 이 판정 박스는 입력 영역보다 위에 렌더링해, 저장 가능 여부를 먼저 읽고 아래에서 최소한의 운영 기록을 확인하는 흐름으로 보이게 한다.
- 공통 route/readiness panel은 긴 enum route를 underscore 기준으로 줄바꿈하고, 좁은 화면에서는 verdict 영역을 아래로 내려 가로 넘침 없이 읽히게 한다.
- Save / Open 버튼은 판단 기준과 JSON보다 먼저 보이게 하고, 상세 기준 / Pre-Live JSON / 선택 후보 raw detail은 하나의 `상세 보기` expander 안에 둔다.
- Pre-Live 운영 상태 영역은 Candidate Review 관점에서 필요한 promotion / shortlist / deployment / suggested status만 badge strip으로 보여주고, 추천 근거, 저장 후보 식별값, 판단 기준 표는 접힘 영역에 둔다.
- `Suggested Next Step`은 다음 검토 행동 제안이지 live trading 승인이나 최종 투자 판단이 아니다.
- `Save Pre-Live Record`는 live trading 승인이 아니라 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 paper / watchlist / hold 같은 운영 상태를 남기는 append-only 기록이다.
- `Open Portfolio Proposal`은 같은 후보의 현재 선택 상태가 저장된 Pre-Live record와 맞고 route가 `PORTFOLIO_PROPOSAL_READY`일 때 활성화된다.

Phase 28 이후 `저장된 비중 조합` 영역에는
`저장된 비중 조합 Replay / 편집 Parity Snapshot`을 둔다.
이 표는 저장 포트폴리오를 다시 열거나 재실행하기 전에 아래 값이 남아 있는지 보여준다.

- compare 공용 입력: start / end / timeframe / option
- selected strategy list
- weights percent / date alignment
- strategy override map
- strategy별 핵심 override: cadence, universe, factor, overlay, handling, benchmark, guardrail, score 설정

## Compare / Weighted Data Trust 흐름

Phase 28 이후 compare와 weighted portfolio 결과도 component별 data trust를 표시한다.

표시 위치:

- `Strategy Comparison > Data Trust`
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

- compare 결과가 서로 같은 데이터 조건에서 나온 것인지 먼저 확인한다.
- weighted portfolio는 composite 결과이므로, 구성 전략별 데이터 상태를 먼저 확인한다.
- 이 표는 성과 비교표가 아니라 데이터 조건 확인표다.

## Real-Money / Guardrail Scope 흐름

Phase 28 이후 compare, history, saved portfolio에는
전략별 Real-Money / Guardrail 지원 범위를 같은 언어로 보여주는 표를 둔다.

표시 위치:

- `Strategy Comparison > Real-Money / Guardrail`
- `Operations > Backtest Run History > Selected History Run > History Real-Money / Guardrail Scope`
- `저장된 비중 조합 > Saved Portfolio Real-Money / Guardrail Scope`

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
- `Proposal Components`는 비교 기능이 아니라 포트폴리오에 넣을 구성 후보 선택이다. 비교는 `Compare & Portfolio Builder`에서 수행한다.
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
     -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl append
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
- `최종 검토 결과 기록`은 `.note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`에 `SELECT_FOR_PRACTICAL_PORTFOLIO`, `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, `RE_REVIEW_REQUIRED` 중 하나를 append-only로 저장한다.
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
