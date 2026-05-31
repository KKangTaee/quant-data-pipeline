# Portfolio Selection Flow

Status: Active
Last Verified: 2026-05-31

## Purpose

이 문서는 Backtest에서 후보를 만들고, Practical Validation에서 검증하고, Final Review에서 최종 판단한 뒤 Selected Portfolio Dashboard에서 사후 확인하는 현재 사용자 흐름을 설명한다.

예전의 긴 workflow redesign 문서는 구현 전 분석과 migration 계획이 섞여 있었다. 이 문서는 현재 제품에서 사용자가 실제로 따라야 하는 흐름만 남긴다.

## Current Flow

```text
Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Selected Portfolio Dashboard
```

| Step | Screen | What It Does | Durable Record |
|---|---|---|---|
| 1 | Backtest Analysis | 단일 전략 실행 또는 Portfolio Mix Builder로 weighted mix 후보를 만들고 검증 후보 source를 만든다 | `PORTFOLIO_SELECTION_SOURCES.jsonl` |
| 2 | Practical Validation | 선택된 source를 source traits 기반 module gate와 practical diagnostic으로 검증한다 | `PRACTICAL_VALIDATION_RESULTS.jsonl` |
| 3 | Final Review | Candidate Board의 review priority / first-review candidate와 Decision Cockpit으로 selected-route 상태를 보고 최종 select / hold / reject / re-review 판단을 남기며, 상세 Practical Validation evidence는 Appendix에서 read-only로 확인한다 | `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` |
| 4 | Selected Portfolio Dashboard | 선정된 포트폴리오를 최신 기간, recheck readiness, symbol freshness, provider evidence, timeline, review signal, recheck comparison, 가상 투자금 / optional actual allocation boundary 기준으로 다시 확인한다 | 사용자가 명시적으로 저장할 때만 monitoring log |

## Stage Ownership

| Stage | Owns | Does Not Own |
|---|---|---|
| Backtest Analysis | 단일 후보 생성, Portfolio Mix 후보 생성, saved mix replay, 1차 후보 readiness, Practical Validation handoff gate | 최종 판단, 별도 후보 간 read-only 비교, 후속 monitoring / deployment 판단 |
| Practical Validation | 실전 투입 전 검증, source traits 기반 module gate, provider data gap, stress / sensitivity evidence, validation efficacy / data coverage / backtest realism evidence | 투자 승인, 최종 사용자 메모 |
| Final Review | Gate-passed 후보 비교, Candidate Board review priority / queue, Decision Cockpit에서 선정 가능 / 보류 / 재검토 / 거절 판단, 최종 판단 기록, Evidence Appendix에서 investability evidence packet / construction risk / risk contribution / component role weight / validation efficacy / data coverage / backtest realism 근거 read-only 확인, critical gap 기반 selected-route gate, saved decision dossier export | 새 비중 실험, provider data 수집, 사용자 메모용 반복 저장, 자동 report 파일 생성 |
| Selected Portfolio Dashboard | 선정 이후 성과 재확인, Final Review -> dashboard continuity check, read-only recheck readiness / symbol freshness / provider evidence / monitoring timeline / signal / recheck comparison, optional allocation check / allocation evidence boundary | broker order, live approval, auto rebalance |

## Verification Checkpoints

검증 기준은 제품 `Stage` 번호로 부르지 않는다.
화면 흐름과 검증 기준이 섞이면 Backtest Analysis 안의 Real-Money / Portfolio Mix 보조 신호가 별도 단계처럼 보이기 때문이다.

| Checkpoint | Primary Surface | Meaning |
|---|---|---|
| Result Integrity | Backtest Analysis > Data Trust Summary | 결과 기간, 가격 최신성, excluded ticker를 먼저 확인 |
| Performance Shape | Backtest Analysis > Summary / Equity Curve | 성과와 낙폭의 기본 모양 확인 |
| Candidate Readiness | Backtest Analysis > Real-Money / Mix 후보 1차 판단 | 단일 후보 또는 mix 후보를 Practical Validation으로 넘겨도 되는지 확인 |
| Practical Evidence | Practical Validation | source traits, 필수 / 조건부 module gate, provider, data coverage, realism, robustness, construction risk 검증 |
| Final Decision Gate | Final Review | selected-route blocker와 최종 선택 가능 여부 판단 |
| Monitoring Check | Selected Portfolio Dashboard | 선정 이후 recheck readiness, freshness, provider evidence, review signal 확인 |

## Source Contract

Portfolio Selection V2의 기준 id는 `selection_source_id`다.

```text
PORTFOLIO_SELECTION_SOURCES
  -> PRACTICAL_VALIDATION_RESULTS
    -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2
      -> Selected Portfolio Dashboard read-only monitoring
```

기존 `registry_id`, Review Note, Pre-Live registry, Portfolio Proposal registry는 legacy compatibility로 남을 수 있지만, 현재 주 흐름의 필수 저장 단계는 아니다.
Selected Dashboard의 Timeline / Continuity / Review Signals / Decision Dossier는 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2` row를 같은 durable source로 표시하고, session-state recheck / drift / alert evidence는 저장된 monitoring history가 아니라 read-only context로 표시한다.

## User-Facing Rules

- 사용자는 Backtest Analysis에서 후보를 만들고 Practical Validation으로 보낸다.
- Backtest Analysis의 Real-Money는 1차 후보 readiness만 보며, probation / monitoring / deployment를 시작하거나 확정하지 않는다.
- Backtest Analysis의 Portfolio Mix Builder는 여러 component를 비교해 하나를 고르는 화면이 아니라, weight를 정해 하나의 mix 후보를 만드는 화면이다.
- `검증 후보로 보내기` / `실전성 검증으로 보내기`는 사용자 메모나 preset 저장이 아니라 1차 후보 판단을 통과한 source를 Practical Validation으로 넘기는 workflow handoff다.
- Practical Validation은 후보가 실전 검토에 충분한 근거를 갖는지 보여준다.
- Practical Validation은 source traits와 validation profile을 함께 읽어 필수 검증, 조건부 / 전략별 검증, 후속 참고 검증을 분리한다.
- Practical Validation의 `1. 선택 후보 확인`은 Backtest Analysis가 넘긴 summary, equity curve, result table snapshot을 먼저 보여줘 후보의 원래 백테스트 근거를 빠르게 확인하게 한다.
- Practical Validation은 전용 workbench shell의 Control Center에서 후보 / profile / latest replay / gate를 먼저 요약한다.
- Practical Validation의 각 step은 bordered surface로 분리해 step 경계를 명확히 보여준다.
- Practical Validation의 `4. Final Review Gate / 검증 모듈`은 통과 / 차단 여부와 적용 module을 먼저 보여주고, blocker는 Fix Queue 카드로 해결 위치와 액션을 같이 보여준다. 화면 board는 검증 module과 1:1 개념이 아니므로 `5. 검증 근거 보드`와 `6. 보강 액션`으로 분리한다.
- `Applied Validation Map`은 각 board가 어떤 module의 evidence인지, 현재 후보에 적용되는지, 적용되지 않으면 왜 빠졌는지를 보여주는 보조 `검증-근거 연결 지도`이며 기본 상세 영역으로 낮춘다.
- Practical Validation의 `Latest Runtime Replay`는 별도 audit board가 아니라 `3. 최신 데이터 기준 전략 재검증` 섹션에서 재검증을 실행해 해소한다. 이 결과는 브라우저 세션에서 사용자가 직접 실행한 뒤에만 보이며, Practical Validation 탭에 새로 들어오거나 source를 바꾸면 이전 replay 표시 state를 지운다.
- Final Review 이동은 필수 검증 module의 `BLOCKED` / `NEEDS_INPUT` / `NOT_RUN`이 해소됐을 때만 가능하다. `REVIEW`는 이동을 막지 않지만 Final Review에서 선택 / 보류 / 재검토 판단 근거로 확인해야 한다. Practical Validation module board는 `Gate Effect`와 `Gate Reason`으로 이동 차단, Final Review 확인, 후속 참고를 구분한다. `검증 결과 저장(기록용)`은 audit trail만 남기는 기능이며, Gate 미통과 row는 Final Review 후보 목록에 나타나지 않는다.
- `Benchmark / Comparator Parity`는 benchmark뿐 아니라 cash, simple baseline, equal-weight baseline, custom comparator 같은 비교 기준과 후보의 기간 / coverage / frequency가 동등한지 보는 필수 검증이다.
- `NOT_RUN`은 pass가 아니다. 데이터나 구현이 부족해 검증하지 못했다는 뜻이다.
- Final Review가 최종 판단 위치다. 중간 단계에서 최종 메모를 반복해서 저장하지 않는다.
- Final Review source picker는 Practical Validation Gate를 통과한 result만 표시한다. 저장만 된 blocked / needs input / not run validation row는 기록으로 남지만 최종 검토 후보에서는 숨긴다.
- Final Review는 후보 선택 전에 Candidate Board로 Gate 통과 후보의 decision state, suggested decision, blocker / review-required 수, 주요 audit route를 비교한다.
- Candidate Board는 후보를 select-ready, hold / re-review, blocked 순서로 정렬하고, first-review candidate, primary reason, next action을 표시한다. 이 priority는 새 투자 점수가 아니라 기존 evidence를 보기 쉽게 정렬하는 read-only 표시다.
- Final Review는 상세 evidence table보다 Decision Cockpit을 먼저 보여준다. 이 cockpit은 selected-route state, suggested decision, Must Fix, Must Review, monitoring seed를 같은 gate policy에서 읽는다.
- Final Review의 주 action은 Decision Cockpit 다음에 나오는 `최종 판단 기록`이다. 상세 Practical Validation / Robustness / Paper Observation / Investability Packet 표는 중복 검증이 아니라 이전 검증 결과를 추적하는 Evidence Appendix다.
- Final Review의 investability packet은 새 저장 단계를 만들지 않고 기존 validation evidence를 compact하게 읽는다.
- Final Review의 profile-aware gate policy가 data trust, benchmark, provider / look-through, stress / robustness, leveraged / inverse, paper observation, construction risk, risk contribution, component role / weight, validation efficacy, data coverage, backtest realism group을 판정한다.
- Decision Dossier는 Final Review row와 Selected Dashboard timeline을 사람이 읽는 markdown으로 묶는 read-only export다. source contract consistency를 표시하지만 자동 report 저장이나 새 판단 row를 만들지 않는다.
- critical `NOT_RUN`, hard blocker, evidence blocker, selected-route policy blocker가 남아 있으면 실전 검토 통과 후보 선정은 차단하고, 보류 / 거절 / 재검토 판단으로 기록할 수 있다.
- Structured waiver는 현재 구현하지 않는다. 향후 구현해도 `BLOCK` severity는 waiver 불가이고, 일부 `REVIEW_REQUIRED` gap만 expiry / review trigger / scope를 가진 구조화 waiver로 검토할 수 있다.
- Provider / look-through evidence는 source mix, freshness, as-of range를 함께 본다. stale provider snapshot은 pass가 아니라 review evidence다.
- Look-through Exposure Board는 holdings / exposure snapshot을 asset bucket, top holding, overlap, ETF별 coverage로 요약한다. Full holdings row는 DB 영역에 남고 workflow JSONL에는 compact summary만 남긴다.
- Construction Risk Audit은 component max weight, provider look-through coverage, top holding, holdings overlap, dominant asset bucket, unknown exposure를 별도 row로 본다. provider holdings / exposure가 없거나 partial이면 ready로 보지 않는다.
- Risk Contribution Audit은 component return matrix coverage, pairwise correlation, max risk contribution proxy, drop-one dependency, source strength를 별도 row로 본다. component matrix나 drop-one evidence가 없으면 ready로 보지 않고, DB price proxy / mixed source evidence는 `REVIEW`로 남긴다.
- Component Role / Weight Audit은 explicit role source coverage, profile-aware weight discipline, role concentration, profile intent fit, weight rationale coverage를 별도 row로 본다. role source가 없거나 partial이면 ready로 보지 않고, role preset이나 user memo 저장을 만들지 않는다.
- Construction Risk / Risk Contribution / Component Role / Weight Audit의 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다. Final Review gate policy는 failing row criteria를 evidence에 표시한다.
- Robustness Lab은 stress / rolling / sensitivity / overfit evidence를 compact summary로 묶어 Practical Validation과 Final Review가 같은 근거를 읽게 한다. Strategy-specific perturbation follow-up이나 `NOT_RUN` row는 pass가 아니다.
- Validation Efficacy Audit은 runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT / look-ahead, survivorship / universe, storage boundary를 분리해 본다. `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다.
- Data Coverage Audit은 DB price window, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 분리해 본다. `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다. 현재 listing / asset profile row는 current listing evidence일 뿐이므로 historical universe나 delisting coverage가 없으면 survivorship PASS로 보지 않는다.
- Data Coverage Audit의 lifecycle metrics는 current snapshot, SEC identity cross-check, computed partial, actual coverage, delisting actual을 분리한다. 표시가 구체화돼도 partial evidence는 selected-route PASS 근거가 아니다.
- Backtest Realism Audit은 transaction cost, net cost curve, turnover, cost / slippage sensitivity, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary를 분리해 본다. `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다. Final Review gate policy는 failing Backtest Realism row criteria도 policy evidence로 보여주므로 cost / slippage sensitivity나 liquidity gap이 generic route label 뒤에 숨지 않는다. 이 연결은 core strategy runtime이나 새 저장소를 만들지 않는다.
- Integrated Investability Gate QA는 construction risk 계열 audit, validation / coverage / realism audit, provider / robustness / paper observation / final evidence gate가 함께 작동할 때 ready는 selected-route를 허용하고, 다중 `REVIEW`는 hold / re-review로 보내며, 다중 blocker는 selected-route를 차단하는 service contract를 유지한다.
- Selected Portfolio Dashboard는 선정 이후 상태 확인 화면이다. Recheck Operations Preflight는 Performance Recheck 실행 전 selected replay contract readiness와 DB symbol freshness를 하나의 read-only route로 묶는다. Final Review embedded replay contract를 먼저 보고 Current Candidate Registry는 fallback으로 사용한다. Recheck Readiness는 DB latest market date와 selected component replay contract를 read-only로 확인한다. Symbol Freshness는 replay portfolio ticker와 benchmark ticker의 DB price latest date / row count / lag를 read-only로 확인한다. Provider Evidence는 selected component ticker weight로 기존 DB provider / holdings / exposure context를 read-only로 읽고 `NOT_RUN`, stale freshness, partial / bridge / proxy coverage, missing operability / holdings / exposure를 pass로 처리하지 않는다. Continuity check는 Final Review selected row가 source contract / evidence packet / component target / review trigger / timeline / recheck input 경계를 갖췄는지 읽고, timeline source mismatch는 blocked issue로 표시한다. Timeline은 selection / evidence gate / recheck / drift / trigger preview를 read-only로 읽고 monitoring log를 자동 저장하지 않는다. Review Signals는 Recheck Comparison을 CAGR / MDD / benchmark spread threshold의 policy owner로 사용하며 preflight / provider / comparison route를 하나의 read-only signal board로 번역한다. Recheck Comparison은 최신 Performance Recheck가 기존 Final Review baseline을 계속 지지하는지 read-only로 비교하며, 미실행이나 오류를 pass로 처리하지 않는다. Allocation evidence boundary는 optional Actual Allocation이 수동 / session-only evidence이며 raw input / alert 저장, account / broker 연결, 주문, 자동 리밸런싱을 만들지 않음을 표시한다.

## Storage Boundary

- Portfolio Selection V2의 main durable chain은 `PORTFOLIO_SELECTION_SOURCES.jsonl -> PRACTICAL_VALIDATION_RESULTS.jsonl -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`이다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 사용자가 명시적으로 남기는 optional monitoring check record이며 자동 저장 대상이 아니다.
- V2 registry path는 runtime-defined라 첫 write 전에는 로컬 파일이 없을 수 있다. 파일 부재는 저장 경계 drift가 아니다.
- Waiver persistence는 현재 없다. future implementation이 필요하면 새 JSONL registry가 아니라 compact final decision snapshot을 먼저 검토한다.
- legacy candidate / proposal / paper registry는 보존하지만, 현재 main flow의 필수 단계로 확장하지 않는다.
- raw provider / holdings / macro evidence는 DB에 두고, workflow JSONL에는 compact evidence와 blocker summary만 저장한다.
- 자세한 저장 기준은 `docs/data/STORAGE_GOVERNANCE.md`를 따른다.

## Main Files

| Area | Files |
|---|---|
| Backtest stage routing | `app/web/backtest_common.py`, `app/web/backtest_workflow_routes.py`, `app/web/pages/backtest.py` |
| Backtest Analysis | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare.py` |
| Practical Validation | `app/web/backtest_practical_validation*.py`, `app/services/backtest_practical_validation_modules.py`, `app/services/backtest_practical_validation_board_registry.py`, `app/services/backtest_construction_risk_audit.py`, `app/services/backtest_risk_contribution_audit.py`, `app/services/backtest_component_role_weight_audit.py`, `app/services/backtest_temporal_validation.py`, `app/services/backtest_validation_efficacy.py`, `app/services/backtest_data_coverage_audit.py`, `app/services/backtest_realism_audit.py` |
| Final Review | `app/web/backtest_final_review*.py`, `app/services/backtest_evidence_read_model.py` |
| Selected Dashboard | `app/web/final_selected_portfolio_dashboard*.py`, `app/runtime/final_selected_portfolios.py` |
| Selection V2 persistence | `app/runtime/portfolio_selection_v2.py` |

## Update Rules

이 문서는 아래가 바뀌면 갱신한다.

- Backtest 상단 stage가 바뀔 때
- selection source / validation result / final decision record 관계가 바뀔 때
- Practical Validation과 Final Review의 stage ownership이 바뀔 때
- Selected Portfolio Dashboard가 read-only monitoring 경계를 넘어서거나 저장 경계가 바뀔 때
