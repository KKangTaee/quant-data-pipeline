# Portfolio Selection Flow

Status: Active
Last Verified: 2026-05-28

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
| 1 | Backtest Analysis | 단일 전략 실행, compare, saved mix replay, 비중 조합을 수행하고 검증 후보 source를 만든다 | `PORTFOLIO_SELECTION_SOURCES.jsonl` |
| 2 | Practical Validation | 선택된 source를 12개 practical diagnostic으로 검증한다 | `PRACTICAL_VALIDATION_RESULTS.jsonl` |
| 3 | Final Review | Practical Validation evidence를 investability packet으로 확인하고 최종 select / hold / reject / re-review 판단을 남기며, 저장된 판단을 read-only dossier로 다시 읽는다 | `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` |
| 4 | Selected Portfolio Dashboard | 선정된 포트폴리오를 최신 기간, recheck readiness, symbol freshness, provider evidence, timeline, review signal, recheck comparison, 가상 투자금 기준으로 다시 확인한다 | 사용자가 명시적으로 저장할 때만 monitoring log |

## Stage Ownership

| Stage | Owns | Does Not Own |
|---|---|---|
| Backtest Analysis | 후보 생성, 전략 비교, saved mix replay, 비중 조합 | 최종 판단 |
| Practical Validation | 실전 투입 전 검증, provider data gap, stress / sensitivity evidence, validation efficacy / data coverage / backtest realism evidence | 투자 승인, 최종 사용자 메모 |
| Final Review | 최종 후보 판단, investability evidence packet 확인, validation efficacy / data coverage / backtest realism 근거 확인, critical gap 기반 selected-route gate, saved decision dossier export | 새 비중 실험, provider data 수집, 사용자 메모용 반복 저장, 자동 report 파일 생성 |
| Selected Portfolio Dashboard | 선정 이후 성과 재확인, Final Review -> dashboard continuity check, read-only recheck readiness / symbol freshness / provider evidence / monitoring timeline / signal / recheck comparison, optional allocation check | broker order, live approval, auto rebalance |

## Source Contract

Portfolio Selection V2의 기준 id는 `selection_source_id`다.

```text
PORTFOLIO_SELECTION_SOURCES
  -> PRACTICAL_VALIDATION_RESULTS
    -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2
      -> Selected Portfolio Dashboard read-only monitoring
```

기존 `registry_id`, Review Note, Pre-Live registry, Portfolio Proposal registry는 legacy compatibility로 남을 수 있지만, 현재 주 흐름의 필수 저장 단계는 아니다.

## User-Facing Rules

- 사용자는 Backtest Analysis에서 후보를 만들고 Practical Validation으로 보낸다.
- Practical Validation은 후보가 실전 검토에 충분한 근거를 갖는지 보여준다.
- `NOT_RUN`은 pass가 아니다. 데이터나 구현이 부족해 검증하지 못했다는 뜻이다.
- Final Review가 최종 판단 위치다. 중간 단계에서 최종 메모를 반복해서 저장하지 않는다.
- Final Review의 investability packet은 새 저장 단계를 만들지 않고 기존 validation evidence를 compact하게 읽는다.
- Final Review의 profile-aware gate policy가 data trust, benchmark, provider / look-through, stress / robustness, leveraged / inverse, paper observation, validation efficacy, data coverage, backtest realism group을 판정한다.
- Decision Dossier는 Final Review row와 Selected Dashboard timeline을 사람이 읽는 markdown으로 묶는 read-only export다. 자동 report 저장이나 새 판단 row를 만들지 않는다.
- critical `NOT_RUN`, hard blocker, evidence blocker, selected-route policy blocker가 남아 있으면 실전 검토 통과 후보 선정은 차단하고, 보류 / 거절 / 재검토 판단으로 기록할 수 있다.
- Structured waiver는 현재 구현하지 않는다. 향후 구현해도 `BLOCK` severity는 waiver 불가이고, 일부 `REVIEW_REQUIRED` gap만 expiry / review trigger / scope를 가진 구조화 waiver로 검토할 수 있다.
- Provider / look-through evidence는 source mix, freshness, as-of range를 함께 본다. stale provider snapshot은 pass가 아니라 review evidence다.
- Look-through Exposure Board는 holdings / exposure snapshot을 asset bucket, top holding, overlap, ETF별 coverage로 요약한다. Full holdings row는 DB 영역에 남고 workflow JSONL에는 compact summary만 남긴다.
- Construction Risk Audit은 component max weight, provider look-through coverage, top holding, holdings overlap, dominant asset bucket, unknown exposure를 별도 row로 본다. provider holdings / exposure가 없거나 partial이면 ready로 보지 않는다.
- Robustness Lab은 stress / rolling / sensitivity / overfit evidence를 compact summary로 묶어 Practical Validation과 Final Review가 같은 근거를 읽게 한다. Strategy-specific perturbation follow-up이나 `NOT_RUN` row는 pass가 아니다.
- Validation Efficacy Audit은 runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT / look-ahead, survivorship / universe, storage boundary를 분리해 본다. `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다.
- Data Coverage Audit은 DB price window, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 분리해 본다. `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다. 현재 listing / asset profile row는 current listing evidence일 뿐이므로 historical universe나 delisting coverage가 없으면 survivorship PASS로 보지 않는다.
- Data Coverage Audit의 lifecycle metrics는 current snapshot, SEC identity cross-check, computed partial, actual coverage, delisting actual을 분리한다. 표시가 구체화돼도 partial evidence는 selected-route PASS 근거가 아니다.
- Backtest Realism Audit은 transaction cost, net cost curve, turnover, cost / slippage sensitivity, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary를 분리해 본다. `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 선정 전 review-required다. Final Review gate policy는 failing Backtest Realism row criteria도 policy evidence로 보여주므로 cost / slippage sensitivity나 liquidity gap이 generic route label 뒤에 숨지 않는다. 이 연결은 core strategy runtime이나 새 저장소를 만들지 않는다.
- Integrated Investability Gate QA는 세 audit과 provider / robustness / paper observation / final evidence gate가 함께 작동할 때 ready는 selected-route를 허용하고, 다중 `REVIEW`는 hold / re-review로 보내며, 다중 blocker는 selected-route를 차단하는 service contract를 유지한다.
- Selected Portfolio Dashboard는 선정 이후 상태 확인 화면이다. Recheck Readiness는 Performance Recheck 실행 전 DB latest market date와 selected component replay contract를 read-only로 확인한다. Symbol Freshness는 replay portfolio ticker와 benchmark ticker의 DB price latest date / row count / lag를 read-only로 확인한다. Provider Evidence는 selected component ticker weight로 기존 DB provider / holdings / exposure context를 read-only로 읽고 `NOT_RUN`, partial coverage, stale evidence를 pass로 처리하지 않는다. Continuity check는 Final Review selected row가 evidence packet / component target / review trigger / timeline / recheck input 경계를 갖췄는지 읽는다. Timeline은 selection / evidence gate / recheck / drift / trigger preview를 read-only로 읽고 monitoring log를 자동 저장하지 않는다. Recheck Comparison은 최신 Performance Recheck가 기존 Final Review baseline을 계속 지지하는지 read-only로 비교하며, 미실행이나 오류를 pass로 처리하지 않는다. 주문이나 자동 리밸런싱을 만들지 않는다.

## Storage Boundary

- Portfolio Selection V2의 main durable chain은 `PORTFOLIO_SELECTION_SOURCES.jsonl -> PRACTICAL_VALIDATION_RESULTS.jsonl -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`이다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 사용자가 명시적으로 남기는 optional monitoring check record이며 자동 저장 대상이 아니다.
- Waiver persistence는 현재 없다. future implementation이 필요하면 새 JSONL registry가 아니라 compact final decision snapshot을 먼저 검토한다.
- legacy candidate / proposal / paper registry는 보존하지만, 현재 main flow의 필수 단계로 확장하지 않는다.
- raw provider / holdings / macro evidence는 DB에 두고, workflow JSONL에는 compact evidence와 blocker summary만 저장한다.
- 자세한 저장 기준은 `docs/data/STORAGE_GOVERNANCE.md`를 따른다.

## Main Files

| Area | Files |
|---|---|
| Backtest stage routing | `app/web/backtest_common.py`, `app/web/backtest_workflow_routes.py`, `app/web/pages/backtest.py` |
| Backtest Analysis | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare.py` |
| Practical Validation | `app/web/backtest_practical_validation*.py`, `app/services/backtest_temporal_validation.py`, `app/services/backtest_validation_efficacy.py`, `app/services/backtest_data_coverage_audit.py`, `app/services/backtest_realism_audit.py` |
| Final Review | `app/web/backtest_final_review*.py`, `app/services/backtest_evidence_read_model.py` |
| Selected Dashboard | `app/web/final_selected_portfolio_dashboard*.py`, `app/runtime/final_selected_portfolios.py` |
| Selection V2 persistence | `app/runtime/portfolio_selection_v2.py` |

## Update Rules

이 문서는 아래가 바뀌면 갱신한다.

- Backtest 상단 stage가 바뀔 때
- selection source / validation result / final decision record 관계가 바뀔 때
- Practical Validation과 Final Review의 stage ownership이 바뀔 때
- Selected Portfolio Dashboard가 read-only monitoring 경계를 넘어서거나 저장 경계가 바뀔 때
