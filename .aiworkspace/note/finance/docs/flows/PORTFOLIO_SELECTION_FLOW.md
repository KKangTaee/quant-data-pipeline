# Portfolio Selection Flow

Status: Active
Last Verified: 2026-06-09

## Purpose

이 문서는 Backtest에서 후보를 만들고, Practical Validation에서 검증 근거를 만들고, Final Review에서 Portfolio Monitoring 후보 여부를 판단한 뒤 Operations > Portfolio Monitoring에서 사후 확인하는 현재 사용자 흐름을 설명한다.

파일 / helper 이름은 여전히 legacy `Selected Portfolio Dashboard`를 포함할 수 있지만, 현재 사용자-facing route와 stage 이름은 `Operations > Portfolio Monitoring`이다.

예전의 긴 workflow redesign 문서는 구현 전 분석과 migration 계획이 섞여 있었다. 이 문서는 현재 제품에서 사용자가 실제로 따라야 하는 흐름만 남긴다.

## Current Flow

`backtest-dev`에서 온 새 전략 또는 의미 있는 전략 개선을 이 흐름에 올리려면, 먼저 [Strategy Promotion Contract](../../reports/backtests/STRATEGY_PROMOTION_CONTRACT.md)를 채워 universe, survivorship, PIT, optimization, OOS / walk-forward, cost / liquidity, replay, generated artifact, `NOT_RUN` evidence, monitoring trigger를 확인한다. 이 contract는 source 생성 전 precondition이며, 기존 Practical Validation / Final Review gate를 대체하지 않는다.

```text
Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Portfolio Monitoring
```

| Step | Screen | What It Does | Durable Record |
|---|---|---|---|
| 1 | Backtest Analysis | 단일 전략 실행 또는 Portfolio Mix Builder로 weighted mix 후보를 만들고 검증 후보 source를 만든다 | `PORTFOLIO_SELECTION_SOURCES.jsonl` |
| 2 | Practical Validation | 선택된 source를 source traits 기반 module gate, selected-route preflight, practical diagnostic으로 검증한다 | `PRACTICAL_VALIDATION_RESULTS.jsonl` |
| 3 | Final Review | Decision Desk command center로 오늘의 판단 상태를 먼저 보고, CNN / AAII market sentiment context overlay를 시장 배경으로만 확인한다. Candidate Board의 review priority / first-review candidate와 Decision Cockpit으로 selection-readiness 상태를 확인한다. `selection_gate_policy_snapshot`이 통과한 후보만 Portfolio Monitoring 후보로 저장하며, 보류 / 거절 / 재검토는 저장 action이 아니라 상태 안내로 표시한다. `REVIEW` 항목은 기본적으로 `open_review_items`로 이어서 추적하고, 더 엄격한 live 투입 감사 성격의 판정은 `deployment_readiness_policy_snapshot`으로 보존한다. 저장된 선정 기록은 Saved Decision Review ledger와 Portfolio Monitoring handoff로 다시 읽고 상세 Practical Validation evidence는 Appendix에서 read-only로 확인한다 | `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` |
| 4 | Operations > Portfolio Monitoring | legacy file/helper name은 Selected Portfolio Dashboard를 유지하지만 사용자-facing route는 Portfolio Monitoring이다. 화면 진입 시 CNN / AAII market sentiment context overlay와 Active Portfolio Monitoring Scenario가 먼저 보이며, active portfolio의 실행 상태, 설정 투자금, 평가 금액, 손익, 총 수익률, CAGR / MDD, 기준일, 마지막 session update, value curve, 전략별 성과, target snapshot / next review schedule을 확인한다. Portfolio가 없거나 strategy가 없거나 scenario가 아직 실행되지 않았으면 각각 생성 / 전략 추가 / 업데이트 실행 안내를 보여준다. Scenario 결과가 있으면 latest / previous saved Monitoring Snapshot과 current scenario의 return / CAGR / drawdown / benchmark delta / drift 차이를 비교한다. 사용자가 `Save Monitoring Snapshot` 또는 `Record Review`를 명시적으로 누르면 compact benchmark delta, return / drawdown, drift, provider freshness, review signal, open issue, operator note, next review date가 monitoring log에 append된다. 그 아래 나의 포트폴리오 card shelf에서 active portfolio를 바꾸고, portfolio name / description edit와 compact strategy board에서 Final Review selected 후보 slot의 start / latest-end mode / balance / memo를 관리한다. `포트폴리오 시나리오 업데이트`는 strategy board 아래에서 pending / stale strategy만 기본 실행하고, 필요 시 `전체 재실행`으로 full refresh한다. Strategy별 recheck readiness / provider / open issue / deployment evidence는 하단 상세 점검에서 사용자가 선택한 1개 전략만 연다. Sentiment context, target snapshot, monitoring snapshot은 주문 지시나 자동 리밸런싱이 아니다 | `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` for dashboard portfolio setup; scenario result는 session state; 사용자가 명시적으로 저장할 때만 `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` |

## Stage Ownership

| Stage | Owns | Does Not Own |
|---|---|---|
| Backtest Analysis | 단일 후보 생성, Portfolio Mix 후보 생성, saved mix replay, 1차 후보 readiness, Practical Validation handoff gate | 최종 판단, 별도 후보 간 read-only 비교, 후속 monitoring / deployment 판단 |
| Practical Validation | Final Review로 넘길 검증 근거 생성, source strategy / construction 확인, CNN / AAII market sentiment context overlay, source traits 기반 module gate, selected-route preflight, provider data gap, stress / sensitivity evidence, validation efficacy / data coverage / backtest realism evidence | 투자 승인, 최종 사용자 메모, full holdings 원장 저장, sentiment 기반 자동 통과 / 차단 |
| Final Review | Gate-passed 후보 비교, Decision Desk command center / flow rail, CNN / AAII market sentiment context overlay, Candidate Board review priority / queue, Decision Cockpit에서 모니터링 후보 가능 / 보류 / 재검토 / 거절 상태 안내, Decision Record Checklist와 선정 문안으로 모니터링 후보 저장 가능 여부 확인, Saved Decision Review ledger로 저장된 선정 기록 재확인, Portfolio Monitoring handoff로 dashboard 대상 row / monitorable / blocked 상태 확인, Evidence Appendix에서 investability evidence packet / construction risk / risk contribution / component role weight / validation efficacy / data coverage / backtest realism 근거 read-only 확인, selection-readiness gate, open review item handoff, deployment readiness policy snapshot 보존, saved decision dossier export | 새 비중 실험, provider data 수집, sentiment 기반 selection gate 변경, 사용자 메모용 반복 저장, 비선정 판단 저장, 실제 자금 투입 승인, broker order, account sync, 자동 report 파일 생성, dashboard monitoring 자동 저장 |
| Operations > Portfolio Monitoring | CNN / AAII market sentiment context overlay, 사용자 dashboard portfolio 생성 / 선택 / soft delete, Final Review selected 후보 pool에서 strategy slot 추가 / 설정 적용 / 제거, 명시적 scenario update와 portfolio-level 성과 재확인, explicit Monitoring Snapshot / Review 저장, latest / previous / current scenario comparison, strategy별 target snapshot / next review schedule 표시, 선택한 1개 전략의 lazy detail에서 Final Review -> dashboard continuity check / read-only recheck readiness / symbol freshness / provider evidence / monitoring timeline / signal / recheck comparison / optional allocation check / allocation evidence boundary, 같은 portfolio 안 전략 간 전환 비교 | sentiment 기반 monitoring signal, 자동 monitoring log 저장, broker order, live approval, account / broker sync, auto rebalance |

Live / Deployment Readiness는 현재 별도 화면으로 구현되지 않았다. Final Review는 향후 그 단계가 사용할 수 있도록 엄격한 `deployment_readiness_policy_snapshot`을 남기지만, 그 snapshot이 곧 live approval이나 주문 가능 상태를 뜻하지 않는다.

## Verification Checkpoints

검증 기준은 제품 `Stage` 번호로 부르지 않는다.
화면 흐름과 검증 기준이 섞이면 Backtest Analysis 안의 promotion policy signal / Portfolio Mix 보조 신호가 별도 단계처럼 보이기 때문이다.

| Checkpoint | Primary Surface | Meaning |
|---|---|---|
| Strategy Promotion Handoff | Backtest Reports > Strategy Promotion Contract | `backtest-dev` result가 product workflow source로 올라가기 전 universe, PIT / survivorship, optimization, OOS, cost / liquidity, replay, artifact, blocker, monitoring trigger를 갖췄는지 확인 |
| Result Integrity | Backtest Analysis > Data Trust Summary | 결과 기간, 가격 최신성, excluded ticker를 먼저 확인 |
| Performance Shape | Backtest Analysis > Summary / Equity Curve | 성과와 낙폭의 기본 모양 확인 |
| Candidate Readiness | Backtest Analysis > Promotion Policy Signal / Mix 후보 1차 판단 | 단일 후보 또는 mix 후보를 Practical Validation으로 넘겨도 되는지 확인 |
| Practical Evidence | Practical Validation | source traits, 필수 / 조건부 module gate, selected-route preflight, provider, data coverage, realism, robustness, construction risk 검증 |
| Final Decision Gate | Final Review | selection hard blocker와 open review item을 분리해 최종 관찰 후보로 저장 가능한지 판단 |
| Monitoring Check | Operations > Portfolio Monitoring | 모니터링 이후 recheck readiness, freshness, provider evidence, review signal 확인 |

## Source Contract

Portfolio Selection current의 기준 id는 `selection_source_id`다.

`backtest-dev` 전략 promotion의 경우 source chain 앞에 사람이 읽는 contract precondition이 붙는다.

```text
Strategy Promotion Contract
  -> PORTFOLIO_SELECTION_SOURCES
    -> PRACTICAL_VALIDATION_RESULTS
      -> FINAL_PORTFOLIO_SELECTION_DECISIONS
        -> Operations > Portfolio Monitoring read-only monitoring
```

일반 current source chain은 아래와 같다.

```text
PORTFOLIO_SELECTION_SOURCES
  -> PRACTICAL_VALIDATION_RESULTS
    -> FINAL_PORTFOLIO_SELECTION_DECISIONS
      -> Operations > Portfolio Monitoring read-only monitoring
```

기존 `registry_id`, Review Note, Pre-Live registry, Portfolio Proposal registry는 legacy compatibility로 남을 수 있지만, 현재 주 흐름의 필수 저장 단계는 아니다.
Portfolio Monitoring의 Timeline / Continuity / Review Signals / Decision Dossier는 `FINAL_PORTFOLIO_SELECTION_DECISIONS` row를 같은 durable source로 표시하고, session-state recheck / drift / alert evidence는 저장된 monitoring history가 아니라 read-only context로 표시한다.
Portfolio Monitoring handoff review도 같은 Final Decision row를 읽으며, selected route / dashboard row build / monitorable 여부를 표시한다. 사용자가 만든 dashboard portfolio setup은 별도 saved state인 `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`에만 저장되며 Final Decision row를 수정하지 않는다.
Final Decision row는 backward compatibility용 `gate_policy_snapshot`을 selection policy로 유지하고, `selection_gate_policy_snapshot`, `deployment_readiness_policy_snapshot`, `open_review_items`를 함께 저장해 선정 판단과 live 투입 감사 후보 항목을 분리한다.
ETF 동적 전략 source contract는 Backtest Analysis fresh 실행 단계에서 strict promotion default와 일관된 `promotion_min_benchmark_coverage`, `promotion_min_net_cagr_spread`, `promotion_min_liquidity_clean_coverage`, rolling underperformance, drawdown policy threshold를 함께 싣는다. Practical Validation이나 Final Review가 missing policy를 후처리로 채우지 않으며, net cost / turnover proof가 부족한 후보는 selected-route gate에서 계속 막힌다.

## User-Facing Rules

- 사용자는 Backtest Analysis에서 후보를 만들고 Practical Validation으로 보낸다.
- `Operations > Operations Overview`는 선정 후 monitoring / system health / archive recovery의 Operations Console 입구이며, Backtest 후보 생성 단계가 아니다. Today action queue는 검토 우선순위만 안내하고 주문 / 자동 리밸런싱을 만들지 않는다.
- Backtest Analysis의 Promotion Policy Signal은 1차 후보 readiness만 보며, probation / monitoring / deployment를 시작하거나 확정하지 않는다.
- Backtest Analysis의 Portfolio Mix Builder는 여러 component를 비교해 하나를 고르는 화면이 아니라, weight를 정해 하나의 mix 후보를 만드는 화면이다.
- `검증 후보로 보내기`는 사용자 메모나 preset 저장이 아니라 1차 후보 판단을 통과한 source를 Practical Validation으로 넘기는 workflow handoff다.
- Practical Validation은 후보가 Final Review에 충분한 검증 근거를 갖는지 보여준다.
- Practical Validation은 source traits와 validation profile을 함께 읽어 필수 검증, 조건부 / 전략별 검증, 후속 참고 검증을 분리한다.
- Practical Validation의 `1. 선택 후보 확인`은 Backtest Analysis가 넘긴 summary, equity curve, result table snapshot, strategy / construction brief, monthly selection / holdings history를 먼저 보여줘 후보의 원래 백테스트 근거와 구성 방식을 빠르게 확인하게 한다.
- 기존 source처럼 selection history snapshot이 없는 기록은 `3. 최신 데이터 기준 전략 재검증`을 실행하면 가능한 범위에서 runtime replay selection history를 확인한다. 이 fallback은 기존 registry row를 재작성하지 않는다.
- Practical Validation은 전용 workbench shell의 Control Center에서 후보 / profile / latest replay / gate를 먼저 요약한다.
- Practical Validation의 `시장 심리 Context Overlay`는 저장된 CNN Fear & Greed / AAII sentiment를 risk-on / neutral / risk-off 참고 맥락으로 보여준다. 이 overlay는 `context_only`이며 Final Review Gate, selected-route preflight, PASS / BLOCKER, registry 저장, saved setup, live approval / broker order / auto rebalance에 영향을 주지 않는다.
- Practical Validation의 각 step은 bordered surface로 분리해 step 경계를 명확히 보여준다.
- Practical Validation의 `4. Final Review Gate / 검증 모듈`은 통과 / 차단 여부와 적용 module을 먼저 보여주고, blocker는 Fix Queue 카드로 해결 위치와 액션을 같이 보여준다. 화면 board는 검증 module과 1:1 개념이 아니므로 `5. 검증 근거 보드`와 `6. 보강 액션`으로 분리한다.
- `Applied Validation Map`은 각 board가 어떤 module의 evidence인지, 현재 후보에 적용되는지, 적용되지 않으면 왜 빠졌는지를 보여주는 보조 `검증-근거 연결 지도`이며 기본 상세 영역으로 낮춘다.
- Practical Validation의 `Latest Runtime Replay`는 별도 audit board가 아니라 `3. 최신 데이터 기준 전략 재검증` 섹션에서 재검증을 실행해 해소한다. 이 결과는 브라우저 세션에서 사용자가 직접 실행한 뒤에만 보이며, Practical Validation 탭에 새로 들어오거나 source를 바꾸면 이전 replay 표시 state를 지운다.
- Final Review 이동은 필수 검증 module의 `BLOCKED` / `NEEDS_INPUT` / `NOT_RUN`이 해소됐을 때만 가능하다. `REVIEW`는 원칙적으로 Final Review에서 선택 / 보류 / 재검토 판단 근거로 확인하지만, Final Review selected-route policy가 저장 차단으로 해석하는 selection-critical `REVIEW_REQUIRED` gap은 Practical Validation의 `Selected-route Preflight`에서 `NEEDS_INPUT`으로 승격되어 이동을 막는다. Practical Validation module board는 `Gate Effect`와 `Gate Reason`으로 이동 차단, Final Review 확인, 후속 참고를 구분한다. `검증 결과 저장(기록용)`은 audit trail만 남기는 기능이며, Gate 미통과 row는 Final Review 후보 목록에 나타나지 않는다.
- `Benchmark / Comparator Parity`는 benchmark뿐 아니라 cash, simple baseline, equal-weight baseline, custom comparator 같은 비교 기준과 후보의 기간 / coverage / frequency가 동등한지 보는 필수 검증이다.
- `NOT_RUN`은 pass가 아니다. 데이터나 구현이 부족해 검증하지 못했다는 뜻이다.
- Final Review가 최종 판단 위치다. 중간 단계에서 최종 메모를 반복해서 저장하지 않는다.
- Final Review source picker는 Practical Validation Gate와 selected-route preflight를 통과한 result만 표시한다. 저장만 된 blocked / needs input / not run validation row와 selected-route preflight 미통과 row는 기록으로 남지만 최종 검토 후보에서는 숨긴다.
- Final Review 상단은 Decision Desk command center와 flow rail로 오늘의 판단 상태, 후보 수, 숨겨진 Gate 미통과 기록, 저장된 모니터링 후보 선정 기록, Portfolio Monitoring 연결 후보를 먼저 보여준다. 이 shell은 UI 표시 계층이며 gate / persistence logic을 바꾸지 않는다.
- Final Review의 `시장 심리 Context Overlay`는 같은 저장된 CNN / AAII sentiment를 Decision Desk 아래에서 market backdrop으로 보여준다. 이 overlay는 Candidate Board priority, selected-route gate, Final Decision save readiness, registry 저장, live approval / broker order / auto rebalance에 영향을 주지 않는다.
- Final Review는 후보 선택 전에 Candidate Board로 Gate 통과 후보의 decision state, suggested decision, blocker / open review 수, 주요 audit route를 비교한다.
- Candidate Board는 후보를 select-ready, hold / re-review, blocked 순서로 정렬하고, first-review candidate, primary reason, next action을 표시한다. 이 priority는 새 투자 점수가 아니라 기존 evidence를 보기 쉽게 정렬하는 read-only 표시다.
- Final Review는 상세 evidence table보다 Decision Cockpit을 먼저 보여준다. 이 cockpit은 selection-readiness state, suggested decision, Must Fix, open review items, monitoring seed를 같은 evidence packet에서 읽는다.
- Final Review의 주 action은 Decision Cockpit 다음에 나오는 `모니터링 후보 선정 저장`이다. 이 구간은 Decision Record Checklist, selected-route gate, 선정 사유 / 운영 전 조건 / 다음 행동 문안을 보여주며, 상세 Practical Validation / Robustness / Paper Observation / Investability Packet 표는 중복 검증이 아니라 이전 검증 결과를 추적하는 Evidence Appendix다.
- 저장된 Final Review row는 Saved Decision Review ledger에서 selected count, latest selection, detail tabs, Portfolio Monitoring handoff, Decision Dossier export로 다시 확인한다. 기존 hold / reject / re-review row는 과거 호환용으로 읽을 수 있지만 새 UI의 정식 저장 action은 아니다. 이 review는 과거 판단을 읽는 화면이며 새 report 파일, approval, order를 만들지 않는다.
- Saved Decision Review의 Portfolio Monitoring handoff는 selected rows, dashboard rows, monitorable / blocked counts, checklist, destination을 보여준다. 이는 기존 selected-route gate나 Portfolio Monitoring continuity check를 다시 계산하는 중복 검증이 아니라, 저장된 모니터링 후보 선정 기록이 다음 operations 화면으로 연결 가능한지 보여주는 read-only 연결 상태다.
- Final Review의 investability packet은 새 저장 단계를 만들지 않고 기존 validation evidence를 compact하게 읽는다.
- Final Review의 profile-aware selection gate policy가 data trust, benchmark, provider / look-through, stress / robustness, leveraged / inverse, paper observation, construction risk, risk contribution, component role / weight, validation efficacy, data coverage, backtest realism group을 판정한다. 같은 입력에서 만든 deployment readiness policy는 더 엄격한 live-readiness 감사 snapshot으로 보존한다.
- Decision Dossier는 Final Review row와 Portfolio Monitoring timeline을 사람이 읽는 markdown으로 묶는 read-only export다. source contract consistency를 표시하지만 자동 report 저장이나 새 판단 row를 만들지 않는다.
- selection hard blocker, critical `NOT_RUN` / `NEEDS_INPUT`, benchmark / comparator parity blocker, gross-only 또는 net/cost 적용 부재, weighted mix component role / weight rationale 부재, Final Review evidence 미준비가 남아 있으면 최종 관찰 후보 선정 저장은 차단된다. 기본 `REVIEW` 항목은 저장을 막기보다 `open_review_items`로 Portfolio Monitoring과 향후 Live / Deployment Readiness에서 이어서 본다. 보류 / 거절 / 재검토는 화면 상태 안내로 표시하되 새 정식 저장 row를 만들지 않는다.
- Structured waiver는 현재 구현하지 않는다. 향후 구현해도 `BLOCK` severity는 waiver 불가이고, 일부 `REVIEW_REQUIRED` gap만 expiry / review trigger / scope를 가진 구조화 waiver로 검토할 수 있다.
- Provider / look-through evidence는 source mix, freshness, as-of range를 함께 본다. stale provider snapshot은 pass가 아니라 review evidence다.
- Look-through Exposure Board는 holdings / exposure snapshot을 asset bucket, top holding, overlap, ETF별 coverage로 요약한다. Full holdings row는 DB 영역에 남고 workflow JSONL에는 compact summary만 남긴다.
- Construction Risk Audit은 component max weight, provider look-through coverage, top holding, holdings overlap, dominant asset bucket, unknown exposure를 별도 row로 본다. provider holdings / exposure가 없거나 partial이면 ready로 보지 않는다.
- Risk Contribution Audit은 component return matrix coverage, pairwise correlation, max risk contribution proxy, drop-one dependency, source strength를 별도 row로 본다. component matrix나 drop-one evidence가 없으면 ready로 보지 않고, DB price proxy / mixed source evidence는 `REVIEW`로 남긴다.
- Component Role / Weight Audit은 explicit role source coverage, profile-aware weight discipline, role concentration, profile intent fit, weight rationale coverage를 별도 row로 본다. role source가 없거나 partial이면 ready로 보지 않고, role preset이나 user memo 저장을 만들지 않는다.
- Construction Risk / Risk Contribution / Component Role / Weight Audit의 `BLOCKED`는 selected-route blocker다. weighted mix에서 component role / weight rationale의 핵심 `NEEDS_INPUT`은 selection blocker이며, 일반 `REVIEW`는 `open_review_items`로 남긴다. 단일 component 후보에는 mix 전용 risk contribution / component role weight audit을 selection gate에서 비적용으로 낮춘다. Final Review gate policy는 non-PASS row criteria를 evidence에 표시한다.
- Robustness Lab은 stress / rolling / sensitivity / overfit evidence를 compact summary로 묶어 Practical Validation과 Final Review가 같은 근거를 읽게 한다. Robustness Experiment run-set은 이 board를 대체하지 않고 `robustness_run_set_id`가 있는 provenance / grouping layer로 유지한다. Final Review investability packet과 saved decision evidence는 run-set id, strategy/source, frozen parameter summary, OOS / walk-forward / regime / cost / parameter perturbation summary, non-PASS evidence, generated artifact reference를 compact하게 읽는다. Strategy-specific perturbation follow-up이나 `NOT_RUN` row는 pass가 아니다.
- Validation Efficacy Audit은 runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT / look-ahead, survivorship / universe, storage boundary를 분리해 본다. 핵심 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 기본적으로 `open_review_items`로 남긴다.
- Data Coverage Audit은 DB price window, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 분리해 본다. 핵심 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 기본적으로 `open_review_items`로 남긴다. 현재 listing / asset profile row는 current listing evidence일 뿐이므로 historical universe나 delisting coverage가 없으면 survivorship PASS로 보지 않는다.
- Data Coverage Audit의 lifecycle metrics는 current snapshot, SEC identity cross-check, computed partial, actual coverage, delisting actual을 분리한다. 표시가 구체화돼도 partial evidence는 selected-route PASS 근거가 아니다.
- Data Provenance / PIT Evidence Contract는 Provider / Macro / Price Window / Universe Lifecycle / Robustness run-set evidence를 같은 row schema로 보여준다. 사용자는 `source_date`, `collected_at`, `snapshot_kind`, `freshness_status`, `proxy_status`, PIT / look-ahead / survivorship risk, `decision_effect.treat_as_pass`를 확인할 수 있다. current snapshot, stale, proxy, non-PIT-safe row는 pass처럼 숨기지 않고 `REVIEW` 또는 `NEEDS_INPUT`으로 남긴다.
- Backtest Realism Audit은 transaction cost, net cost curve, turnover, cost / slippage sensitivity, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary를 분리해 본다. 핵심 `NEEDS_INPUT` / `BLOCKED`와 명시적 transaction cost / net cost curve / net performance / gross-only selection gap은 selected-route blocker이며, 일반 `REVIEW`는 `open_review_items`로 남긴다. Final Review gate policy는 failing Backtest Realism row criteria도 policy evidence로 보여주므로 cost / slippage sensitivity나 liquidity gap이 generic route label 뒤에 숨지 않는다. 이 연결은 core strategy runtime이나 새 저장소를 만들지 않는다.
- Integrated Investability Gate QA는 construction risk 계열 audit, validation / coverage / realism audit, provider / robustness / paper observation / final evidence gate가 함께 작동할 때 ready는 selected-route를 허용하고, 기본 `REVIEW`는 selection을 막지 않는 open review item으로 넘기며, hard blocker는 selected-route를 차단하는 service contract를 유지한다. 동시에 `deployment_readiness_policy_snapshot`은 같은 `REVIEW`를 hold / re-review 수준으로 보존한다.
- Operations > Portfolio Monitoring은 모니터링 후보 선정 후 상태 확인 화면이며, legacy 구현 파일은 Selected Portfolio Dashboard 이름을 유지한다. 이제 화면 진입 시 Active Portfolio Monitoring Scenario를 먼저 보여준다. 사용자는 먼저 active portfolio의 현재 모니터링 상태와 portfolio-level 현재 가치, 손익, 총 수익률, CAGR, MDD, 계산 기준일, session update timestamp, daily badges, value curve, 전략별 성과, 리밸런싱 target table을 본다. Portfolio가 없으면 생성 안내, portfolio는 있지만 strategy가 없으면 strategy board 안내, strategy는 있지만 scenario가 없으면 update 실행 안내를 보여준다. Scenario 결과가 있으면 Monitoring Snapshot / Review 영역에서 saved latest snapshot, previous snapshot, current scenario의 return / CAGR / drawdown / benchmark delta / max drift 변화를 비교한다. `Save Monitoring Snapshot` 또는 `Record Review`는 사용자가 눌렀을 때만 append-only monitoring log를 남기며, provider freshness와 preflight evidence는 이 명시 저장 action에서 compact snapshot으로 포함한다. 그 아래 `나의 포트폴리오` fixed-height card shelf에서 monitoring portfolio를 만들거나 선택하고, delete / raw setup management는 접힌 관리 영역에서만 다룬다. 선택된 portfolio는 portfolio name / description edit와 compact strategy slot board로 관리하며, Final Review selected 후보 pool에서 selected decision을 추가한다. 이 dashboard portfolio는 backtest 전략 정의가 아니라 사용자 모니터링 컨테이너이며, 같은 포트폴리오 안 중복 selected decision은 추가하지 않는다. 각 slot은 selected decision, 시작일, 종료일 latest mode, balance, optional memo를 저장하며 `전략 적용`과 scenario update는 분리된다. Portfolio Monitoring Scenario는 strategy board 아래의 `포트폴리오 시나리오 업데이트`를 누를 때만 slot 기준 selected component contract를 다시 실행하고, 종료일이 latest mode이면 DB 최신 시장일을 사용한다. 기본 업데이트는 아직 실행되지 않았거나 현재 slot signature와 맞지 않는 stale strategy만 실행하며, `전체 재실행`을 켜야 기존 최신 결과까지 다시 replay한다. Strategy별 Recheck Operations Preflight / Recheck Readiness / Symbol Freshness / Provider Evidence / Monitoring Signals는 Streamlit eager tab 비용을 피하기 위해 사용자가 선택한 1개 전략 상세를 열 때만 렌더링한다. Preflight는 selected replay contract readiness와 DB symbol freshness를 하나의 read-only route로 묶고, Final Review embedded replay contract를 먼저 보며 Current Candidate Registry는 fallback으로 사용한다. Provider Evidence는 selected component ticker weight로 기존 DB provider / holdings / exposure context를 read-only로 읽고 `NOT_RUN`, stale freshness, partial / bridge / proxy coverage, missing operability / holdings / exposure를 pass로 처리하지 않는다. Continuity check는 Final Review selected row가 source contract / evidence packet / component target / review trigger / timeline / recheck input 경계를 갖췄는지 읽고, timeline source mismatch는 blocked issue로 표시한다. Timeline은 selection / evidence gate / recheck / drift / trigger preview를 read-only로 읽고 monitoring log를 자동 저장하지 않는다. Review Signals는 Recheck Comparison을 CAGR / MDD / benchmark spread threshold의 policy owner로 사용하며 preflight / provider / comparison route를 계속 관찰 / 보강 필요 / 대체 검토 성격의 read-only signal board로 번역한다. 같은 dashboard portfolio 안 selected 전략이 2개 이상이면 최신 scenario 결과를 전환 비교 표로 볼 수 있다. Recheck Comparison은 최신 Monitoring Scenario가 기존 Final Review baseline을 계속 지지하는지 read-only로 비교하며, 미실행이나 오류를 pass로 처리하지 않는다. Allocation evidence boundary는 optional Actual Allocation이 수동 / session-only 증거이며 raw input / alert 저장, account / broker 연결, 주문, 자동 리밸런싱을 만들지 않음을 표시한다. Live / Deployment Readiness는 마지막 optional preflight로만 남긴다.
- Portfolio Monitoring의 `시장 심리 Context Overlay`는 화면 진입부에서 현재 시장 배경을 보여줄 뿐이다. Monitoring Scenario, Review Signals, saved dashboard setup, monitoring log, broker order, auto rebalance와 연결하지 않는다.

## Storage Boundary

- Portfolio Selection current의 main durable chain은 `PORTFOLIO_SELECTION_SOURCES.jsonl -> PRACTICAL_VALIDATION_RESULTS.jsonl -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`은 Operations > Portfolio Monitoring 전용 saved setup이다. File name은 legacy dashboard term을 유지한다. Final Review 판단, monitoring evidence, approval record가 아니며 user-created portfolio 이름, 설명, selected decision strategy slot, start / latest-end mode / balance / memo만 보존한다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 사용자가 명시적으로 남기는 optional monitoring snapshot / review record이며 자동 저장 대상이 아니다. full holdings / full macro series / raw provider response 없이 compact scenario, drift, provider freshness, review signal, open issue, operator note, next review date만 저장한다.
- runtime registry path는 runtime-defined라 첫 write 전에는 로컬 파일이 없을 수 있다. 파일 부재는 저장 경계 drift가 아니다.
- Waiver persistence는 현재 없다. future implementation이 필요하면 새 JSONL registry가 아니라 compact final decision snapshot을 먼저 검토한다.
- legacy candidate / proposal / paper registry는 보존하지만, 현재 main flow의 필수 단계로 확장하지 않는다.
- raw provider / holdings / macro evidence는 DB에 두고, workflow JSONL에는 compact evidence와 blocker summary만 저장한다.
- 자세한 저장 기준은 `docs/data/STORAGE_GOVERNANCE.md`를 따른다.

## Main Files

| Area | Files |
|---|---|
| Backtest stage routing | `app/web/backtest_common.py`, `app/web/backtest_workflow_routes.py`, `app/web/pages/backtest.py` |
| Strategy promotion handoff | `.aiworkspace/note/finance/reports/backtests/STRATEGY_PROMOTION_CONTRACT.md`, `.aiworkspace/note/finance/reports/backtests/templates/STRATEGY_PROMOTION_CONTRACT_TEMPLATE.md` |
| Backtest Analysis | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare.py` |
| Practical Validation | `app/web/backtest_practical_validation*.py`, `app/services/backtest_practical_validation_modules.py`, `app/services/backtest_practical_validation_board_registry.py`, `app/services/backtest_selected_route_preflight.py`, `app/services/backtest_construction_risk_audit.py`, `app/services/backtest_risk_contribution_audit.py`, `app/services/backtest_component_role_weight_audit.py`, `app/services/backtest_temporal_validation.py`, `app/services/backtest_validation_efficacy.py`, `app/services/backtest_data_coverage_audit.py`, `app/services/backtest_realism_audit.py` |
| Final Review | `app/web/backtest_final_review*.py`, `app/services/backtest_evidence_read_model.py` |
| Operations > Portfolio Monitoring | `app/web/final_selected_portfolio_dashboard*.py`, `app/runtime/final_selected_portfolios.py` |
| Selection persistence | `app/runtime/portfolio_selection_v2.py` |

## Update Rules

이 문서는 아래가 바뀌면 갱신한다.

- Backtest 상단 stage가 바뀔 때
- selection source / validation result / final decision record 관계가 바뀔 때
- Practical Validation과 Final Review의 stage ownership이 바뀔 때
- Operations > Portfolio Monitoring이 read-only monitoring 경계를 넘어서거나 저장 경계가 바뀔 때
