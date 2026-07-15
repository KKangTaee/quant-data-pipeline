# Portfolio Selection Flow

Status: Active
Last Verified: 2026-07-12

## Purpose

이 문서는 Backtest에서 후보를 만들고, Practical Validation에서 검증 근거를 만들고, Final Review에서 Portfolio Monitoring 후보 여부를 판단한 뒤 Operations > Portfolio Monitoring에서 사후 확인하는 현재 사용자 흐름을 설명한다.

파일 / helper 이름은 여전히 legacy `Selected Portfolio Dashboard`를 포함할 수 있지만, 현재 사용자-facing route와 stage 이름은 `Operations > Portfolio Monitoring`이다.

예전의 긴 workflow redesign 문서는 구현 전 분석과 migration 계획이 섞여 있었다. 이 문서는 현재 제품에서 사용자가 실제로 따라야 하는 흐름만 남긴다.

## Current Flow

```text
Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Portfolio Monitoring
```

| Step | Screen | What It Does | Durable Record |
|---|---|---|---|
| 1 | Backtest Analysis | 단일 전략 실행 또는 Portfolio Mix Builder로 weighted mix 후보를 만들고 검증 후보 source를 만든다 | `PORTFOLIO_SELECTION_SOURCES.jsonl` |
| 2 | Practical Validation | 선택된 source를 source traits 기반 module gate, selected-route preflight, practical diagnostic으로 검증한다. REVIEW는 `데이터 주의`, `2단계 실용성 주의`, `최종 판단 참고`, `Monitoring 추적` role로 분리해 현재 단계에서 볼 항목과 후속 참고를 구분한다 | `PRACTICAL_VALIDATION_RESULTS.jsonl` |
| 3 | Final Review | primary question 아래 latest eligible 후보를 고르고 one-shell Decision Workspace에서 결론, cumulative / Benchmark, Underwater, 실행 관측, 실제 강점 / 약점, measured trait, structured Monitoring 조건, canonical route / 판단 사유, disclosure를 순서대로 읽는다. overall / headline score는 없고 evidence confidence만 보조 metadata다. React는 candidate / route / reason intent와 SVG만 소유하며 Python이 eligibility, 계산, dedup, save evaluation, 자동 Decision ID, append, Monitoring handoff를 소유한다. 같은 active brief의 compact snapshot을 row에 저장하고 기존 row는 재작성하지 않는다. Final Review는 live approval, broker order, auto rebalance가 아니다 | `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` |
| 4 | Operations > Portfolio Monitoring | 기존 Selected Portfolio Dashboard route다. 화면 진입 시 CNN / AAII market sentiment context overlay와 Active Portfolio Monitoring Scenario가 먼저 보이며, active portfolio의 실행 상태, 설정 투자금, 평가 금액, 손익, 총 수익률, CAGR / MDD, 기준일, 마지막 session update, value curve, 전략별 성과, target snapshot / next review schedule을 확인한다. Portfolio가 없거나 strategy가 없거나 scenario가 아직 실행되지 않았으면 각각 생성 / 전략 추가 / 업데이트 실행 안내를 보여준다. 그 아래 나의 포트폴리오 card shelf에서 active portfolio를 바꾸고, portfolio name / description edit와 compact strategy board에서 Final Review selected 후보 slot의 start / latest-end mode / balance / memo를 관리한다. `포트폴리오 시나리오 업데이트`는 strategy board 아래에서 pending / stale strategy만 기본 실행하고, 필요 시 `전체 재실행`으로 full refresh한다. Strategy별 recheck readiness / provider / open issue / deployment evidence는 하단 상세 점검에서 사용자가 선택한 1개 전략만 연다. Sentiment context와 target snapshot은 주문 지시나 자동 리밸런싱이 아니다 | `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` for dashboard portfolio setup; scenario result는 session state; 사용자가 명시적으로 저장할 때만 monitoring log |

## Stage Ownership

| Stage | Owns | Does Not Own |
|---|---|---|
| Backtest Analysis | 단일 후보 생성, Portfolio Mix 후보 생성, saved mix replay, 1차 후보 readiness, Practical Validation handoff gate | 최종 판단, 별도 후보 간 read-only 비교, 후속 monitoring / deployment 판단 |
| Practical Validation | Final Review로 넘길 검증 근거 생성, source strategy / construction 확인, source traits 기반 module gate, selected-route preflight, ETF 운용사 / 공식 외부 데이터 gap, stress / sensitivity evidence, validation method strength / data coverage / backtest realism evidence, 데이터 / 실용성 REVIEW role 표시 | 투자 승인, 최종 사용자 메모, full holdings 원장 저장, sentiment 기반 자동 통과 / 차단, 수익성 최종 랭킹 |
| Final Review | latest eligible 후보 선택, Decision Brief 결론 / 행동 근거 / 실제 강점·약점 / measured trait / structured Monitoring 조건, canonical route·사유·CTA, compact snapshot, selected-route Gate 기반 Portfolio Monitoring 후보 handoff | Decision Desk / visible Review Queue / confirmed-report 단계, composite score, Level2 remediation / pattern guide, React domain 계산·저장, Decision ID / storage path / 운영 조건 사용자 편집, Evidence Appendix, Saved Decisions ledger, provider data 수집, Practical Validation 재실행, 실제 자금 투입 승인, broker order, account sync, auto rebalance |
| Operations > Portfolio Monitoring | CNN / AAII market sentiment context overlay, 사용자 dashboard portfolio 생성 / 선택 / soft delete, Final Review selected 후보 pool에서 strategy slot 추가 / 설정 적용 / 제거, 명시적 scenario update와 portfolio-level 성과 재확인, strategy별 target snapshot / next review schedule 표시, 선택한 1개 전략의 lazy detail에서 Final Review -> dashboard continuity check / read-only recheck readiness / symbol freshness / provider evidence / monitoring timeline / signal / recheck comparison / optional allocation check / allocation evidence boundary, 같은 portfolio 안 전략 간 전환 비교 | sentiment 기반 monitoring signal, broker order, live approval, account / broker sync, auto rebalance |

Live / Deployment Readiness는 현재 별도 화면으로 구현되지 않았다. Final Review는 향후 그 단계가 사용할 수 있도록 엄격한 `deployment_readiness_policy_snapshot`을 남기지만, 그 snapshot이 곧 live approval이나 주문 가능 상태를 뜻하지 않는다.

## Verification Checkpoints

검증 기준은 제품 `Stage` 번호로 부르지 않는다.
화면 흐름과 검증 기준이 섞이면 Backtest Analysis 안의 promotion policy signal / Portfolio Mix 보조 신호가 별도 단계처럼 보이기 때문이다.

| Checkpoint | Primary Surface | Meaning |
|---|---|---|
| Result Integrity | Backtest Analysis > Data Trust Summary | 결과 기간, 가격 최신성, excluded ticker를 먼저 확인 |
| Performance Shape | Backtest Analysis > Summary / Equity Curve | 성과와 낙폭의 기본 모양 확인 |
| Candidate Readiness | Backtest Analysis > Promotion Policy Signal / Mix 후보 1차 판단 | 단일 후보 또는 mix 후보를 Practical Validation source로 넘겨도 되는지 확인한다. `promotion_decision=hold`는 2차 진입 blocker가 아니라 review focus이며, Backtest Analysis에서는 상세 review row와 count / handoff notice를 표시하지 않는다. Data Trust도 `meta["warnings"]` review focus를 1차 데이터 기준 요약에 표시하지 않는다. Portfolio Mix strict compare gate는 별도로 더 보수적으로 읽는다 |
| Practical Evidence | Practical Validation | source traits, 필수 / 조건부 module gate, selected-route preflight, provider, data coverage, realism, robustness, construction risk 검증 |
| Final Decision Gate | Final Review | selection hard blocker와 open review item을 분리해 최종 관찰 후보로 저장 가능한지 판단 |
| Monitoring Check | Operations > Portfolio Monitoring | 모니터링 이후 recheck readiness, freshness, provider evidence, review signal 확인 |

## Source Contract

Portfolio Selection current의 기준 id는 `selection_source_id`다.

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
- `Operations > Operations Overview`는 선정 후 monitoring / system health의 Operations Console 입구이며, Backtest 후보 생성 단계가 아니다. Today action queue는 검토 우선순위만 안내하고 주문 / 자동 리밸런싱을 만들지 않는다. Backtest Run History와 Candidate Library archive 화면은 현재 Operations 상단 탭에 노출하지 않는다.
- Backtest Analysis의 Promotion Policy Signal은 1차 후보 readiness만 보며, probation / monitoring / deployment를 시작하거나 확정하지 않는다. hard blocker는 1차 source 등록을 막고, `2차 확인` review focus는 source의 `entry_gate.review_focus_rows`로 Practical Validation에 전달한다.
- Backtest Analysis의 Data Trust Summary는 DB 가격 기준일이 최신 완료 거래일보다 오래된 경우, 현재 후보 ticker만 대상으로 OHLCV 가격 이력 업데이트 action을 제공한다. 보이는 action card와 버튼은 React custom component 안에서 통합 렌더링되며, Python은 submit event를 받아 데이터 보강만 수행한다. 결과 재계산 / source 등록 / 2차 검증 전송은 사용자가 별도로 실행한다.
- Backtest Analysis의 Handoff panel이 source 등록 action과 entry judgment를 소유한다. Handoff는 `1차 진입 기준`, `먼저 해결`, `다음 단계`를 보여주며 readiness score나 promotion hold review를 1차 blocker처럼 표시하지 않는다. Policy Signals owns evidence detail and does not repeat the same entry-readiness hero. React custom component owns the visible Handoff card and button, and a separate React custom component owns the `검증 기준 상세` first-stage evidence board, while Python keeps source registration write / rerun, policy classification, and persistence. `검증 기준 상세`은 `Data Trust`, `Execution Source`, `Validation Source` 중심으로 1차 기준을 묶고, 각 기준의 `?` help는 `plain_explanation` / `checked_items`로 무엇을 검증했는지 설명한다. 2차 review focus 상세 목록과 count / notice는 Backtest Analysis에서 반복하지 않고 source contract로 Practical Validation에 전달한다.
- Backtest Analysis의 Portfolio Mix Builder는 여러 component를 비교해 하나를 고르는 화면이 아니라, weight를 정해 하나의 mix 후보를 만드는 화면이다.
- `검증 후보로 보내기`는 사용자 메모나 preset 저장이 아니라 1차 후보 판단을 통과한 source를 Practical Validation으로 넘기는 workflow handoff다.
- Practical Validation은 후보가 Final Review에 충분한 검증 근거를 갖는지 보여준다.
- Practical Validation은 source traits와 validation profile을 함께 읽어 필수 검증, 조건부 / 전략별 검증, 후속 참고 검증을 분리하고, 이 결과를 `practical_validation_workspace` read model로 묶어 화면이 바로 읽을 수 있게 한다.
- Practical Validation은 4개 user-facing flow로 읽는다: `후보 Source 확인`, `검증 기준 설정 / 실전 재검증 실행`, `검증 결론 / 다음 행동`, `검증 기준 상세`.
- Flow 1은 Backtest Analysis가 넘긴 `entry_gate.review_focus_rows`를 `Backtest에서 넘어온 2차 확인 항목`으로 보여주고, summary, equity curve, result table snapshot, strategy / construction brief, monthly selection / holdings history로 원래 백테스트 근거와 구성 방식을 확인하게 한다.
- Flow 2는 검증 프로필을 먼저 고른 뒤 최신 runtime replay를 실행하는 지점이다. 기존 source처럼 selection history snapshot이 없는 기록은 Flow 2에서 최신 runtime replay를 실행하면 가능한 범위에서 replay selection history를 확인한다. 이 fallback은 기존 registry row를 재작성하지 않는다. 현재 브라우저 세션에서 `전략 재검증 실행`을 누르기 전에는 Flow 3 / Flow 4와 Practical Validation Result JSON을 렌더링하지 않고 Flow 1 / Flow 2만 보여준다. 자료 보강이 끝나도 validation은 갱신되지 않으므로 collection completion은 해당 source의 replay state를 반드시 지우고 `Flow 2 재검증 필요`로 되돌린다.
- Flow 3 `검증 결론 / 다음 행동`은 Final Review 이동 가능 / 보류와 카테고리별 `통과 / 실패 / 확인 필요`, `검증 결과 저장(기록용)`, `저장하고 Final Review로 이동` CTA를 compact하게 보여주는 first-read surface다. 실행 가능한 pre-final enrichment gap이 있으면 category pass와 별개로 `필수 데이터 보강 후 재검증 필요`를 우선 표시하고 이동 CTA를 비활성화한다. 이 surface는 `workspace_panel.py`가 소유하고, `practical_validation_fix_queue` React component는 compatibility path를 유지하되 visible copy는 `검증 결론` / `카테고리별 검증 요약` / next-stage CTA로 렌더링한다. React는 button click intent만 Python으로 전달하고, 저장 / Final Review handoff / rerun은 page + service boundary가 처리한다. `검증한 것 / 해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치`, 검증 모듈 table, raw status 상세는 Flow 4에서 확인한다.
- Flow 3 summary band는 Python이 root issue 기준으로 계산한 `Final Review 판단에 반영할 한계` 개수와 즉시 해결·개발 blocker 유무를 함께 보여준다. React는 전달된 개수만 표시하며 closure 분류, Gate, 저장은 계산하지 않는다.
- Practical Validation 기본 진입 화면은 저장된 CNN Fear & Greed / AAII sentiment overlay를 렌더링하지 않는다. 이 sentiment context는 검증 요소가 아니며, Final Review / Monitoring의 market backdrop으로만 읽는다.
- Practical Validation의 각 step은 bordered surface로 분리해 step 경계를 명확히 보여준다.
- Flow 4는 독립적인 `근거 종결 경로` 카드 묶음을 반복하지 않는다. category criteria와 action board는 Practical Validation에서 해결할 일을 설명하고, accepted-limit 상세와 terminal decision은 Final Review에서 종결한다.
- Flow 4 `검증 기준 상세`는 먼저 `카테고리별 검증 결과` 보드로 Source & Replay, Data Quality / Bias Control, Comparison Validity, Realism / Tradability, Validation Method Strength, Stress / Robustness, Portfolio Construction, Conditional Evidence의 `상태 / 통과한 기준 / 남은 문제 / 판정`을 요약한다. REVIEW-only라도 Practical Validation이 소유한 applied category는 숨기지 않고 `데이터 주의` 또는 `2단계 실용성 주의`로 표시한다. `selected_route_preflight`는 검증 category가 아니라 `Final Review 이동 요약`으로 분리해 저장 전 막힐 gap만 보조로 보여준다. 각 criteria card는 단순 위치 문자열이 아니라 `검증한 것 / 해결해야 할 항목 / 해결 방법 / 통과 기준 / 위치` guide로 보여주며, 가능하면 audit row의 non-PASS `Criteria`와 `Next Action`을 끌어와 실제 부족 항목과 실행 방법을 노출한다. `해결 방법`은 한 줄 조합 문장이 아니라 `resolution_guide.action_steps` 번호 목록으로 보여주며, row별 action이 있으면 가장 구체적인 단계로 우선 반영한다. `통과 기준`은 사용자가 보강 후 무엇이 되어야 해결된 것인지 판단하는 기준이고, 위치는 `Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세`, `Flow4 > 데이터 보강 / 수집 실행`처럼 실제 화면 경로로 표시한다. Flow 4 visible order는 `카테고리별 검증 결과 -> 데이터 보강 / 수집 실행 -> 상세 근거 / 원자료`다. `단계별 검증 소유권`은 내부 read model inventory로만 유지하고 visible expander로 렌더링하지 않는다. 수집 가능한 ETF 운용사 / holdings / exposure / macro gap만 criteria card의 `수집하기` CTA로 같은 action center의 기존 Python 수집 버튼에 연결하며, React board는 category / ticker / reason / next action / availability 표시만 담당한다. 버튼 설명은 수집하는 것과 하지 않는 것, 실행 후 Flow 2 재검증 필요를 함께 보여준다. 상세 evidence tabs, Look-through Board, Robustness Lab, detailed diagnostics와 보강 작업 상세 / 수집 원자료는 Flow 4 하단의 접힌 `상세 근거 / 원자료`에서 필요한 경우만 확인한다.
- Practical Validation의 `Latest Runtime Replay`는 별도 audit board가 아니라 Flow 2에서 재검증을 실행해 해소한다. 이 결과는 브라우저 세션에서 사용자가 직접 실행한 뒤에만 보이며, Practical Validation 탭에 새로 들어오거나 source를 바꾸면 이전 replay 표시 state를 지운다. Final Review recovery 또는 Flow 4 보강 뒤에는 `자료 보강 -> Flow 2 재검증 -> 새 결과 저장 -> Final Review 확인` 진행 상태를 보여주며, current replay가 없으면 `저장하고 Final Review로 이동` Python handler도 요청을 거부한다.
- First-read status는 `PASS / REVIEW / NEEDS_INPUT / BLOCKED / NOT_RUN / NOT_APPLICABLE`로 정규화해 보여주고, `BLOCKED_FOR_FINAL_REVIEW` 같은 raw route id는 technical detail / JSON context에 남긴다. `REVIEW`는 `pv_data_caution`, `pv_practical_caution`, `final_decision_input`, `monitoring_followup`, `final_readiness_blocker` role로 분리한다.
- Final Review 이동은 필수 core 검증 module의 `BLOCKED` / `NEEDS_INPUT` / `NOT_RUN`과 실행 가능한 pre-final enrichment blocker가 해소됐을 때 가능하다. 현재 Python plan에서 verified source로 실행 가능한 operability, holdings / exposure, required macro gap은 Flow 4에서 보강하고 Flow 2 재검증과 새 validation 저장을 끝내야 한다. source 탐색만 가능한 항목, 기간 밖 stress, 미구현 검증, historical survivorship source, 세금·계좌 판단은 자동 수집 blocker로 승격하지 않는다. `REVIEW`는 pass가 아니지만 하나의 Final Review 숙제가 아니다. 데이터 / 실용성 REVIEW는 Practical Validation에서 role label로 읽고, 최종 선택 메모와 monitoring 추적 항목만 Final Review / Monitoring handoff로 이어진다. Stress / robustness 미실행은 pass가 아니지만 기본적으로 `REVIEW`로 낮춰 과도한 universal blocker가 되지 않게 한다. Construction risk는 ETF-like 또는 weighted mix 후보에만 적용하고, sentiment risk-on/off overlay는 macro gate가 아니라 context로만 남긴다. Final Review selected-route policy가 저장 차단으로 해석하는 selection-critical `REVIEW_REQUIRED` gap은 Practical Validation의 `Selected-route Preflight`에서 `NEEDS_INPUT`으로 승격되어 이동을 막는다. `검증 결과 저장(기록용)`은 audit trail만 남기는 기능이며, Gate 미통과 row는 Final Review 후보 목록에 나타나지 않는다.
- `Benchmark / Comparator Parity`는 benchmark뿐 아니라 cash, simple baseline, equal-weight baseline, custom comparator 같은 비교 기준과 후보의 기간 / coverage / frequency가 동등한지 보는 필수 검증이다.
- `NOT_RUN`은 pass가 아니다. 데이터나 구현이 부족해 검증하지 못했다는 뜻이다.
- Final Review가 최종 판단 위치다. 중간 단계에서 최종 메모를 반복해서 저장하지 않는다.
- Final Review source picker는 source별 최신 Practical Validation row를 먼저 고른 뒤 Gate eligibility를 적용한다. 최신 row가 blocking이면 저장 기록으로 남아도 후보에서 숨기며 과거 eligible row로 fallback하지 않는다. current page는 legacy source를 후보로 포함하지 않는다. Practical Validation의 명시적인 save-and-move가 성공하면 새 stable key를 session handoff로 전달한다.
- Final Review 상단은 primary question과 React Decision Workspace의 candidate selector를 먼저 보여준다. candidate switch는 Python session state를 바꾸는 presentation intent이며 registry를 쓰지 않는다.
- Final Review first-read에서는 CNN / AAII 시장심리 패널을 렌더링하지 않는다. 자세한 심리 해석은 `Workspace > Overview > Sentiment`에서 확인하며, 시장심리는 후보 우선순위, selected-route gate, Final Decision save readiness, registry 저장, live approval / broker order / auto rebalance에 영향을 주지 않는다.
- 시장심리 timing / rebalance 활용은 별도 리서치와 look-ahead-safe 검증 전까지 Final Review gate나 Portfolio Monitoring signal로 쓰지 않는다.
- current Final Review는 별도 Decision Desk / Review Queue / confirmed-report 단계 없이 candidate selector와 판단 근거를 one-shell로 연결한다.
- Decision Workspace는 후보 선택 → 결론 → 행동 근거 → 실제 강점/약점 → trait map → Monitoring 변화 조건 → 최종 판단 → disclosure 순서다. overall / headline score는 제거하고 evidence confidence만 보조 metadata로 남긴다. Python service가 stored curve exact-common alignment, underwater, execution observation, measured comparator 기반 finding/trait, structured trigger, primary-role dedup을 소유하며 React는 계산하지 않는다.
- Level2 REVIEW는 Final Review에서 모두 다시 검증하지 않는다. `final_readiness_blocker`와 selected-route blocking status는 blocker, `pv_data_caution` / `pv_practical_caution`은 근거 신뢰도, `final_decision_input`은 자동 감점 없는 저장 전 확인, `monitoring_followup`은 Monitoring 준비도와 추적 조건으로 분리한다. `남은 판단 근거`는 raw audit id 대신 사용자 언어의 검증명 / 설명 / 현재 확인 내용 / 판단 이유 / 개선 행동을 표시하고 source / 기준일은 접힌 상세 근거로 남긴다. 정상 current flow에서는 실행 가능한 provider gap이 2단계 승격 전에 해소되므로 Final Review 데이터 보강 card가 나타나지 않는다. 이 card는 계약 도입 전 legacy 또는 이후 stale 검토서의 복구 navigation으로만 남고 Final Review에서 provider를 호출하지 않는다. 기간 밖 검증, 미구현 검증, lifecycle source 탐색, 세금·계좌 판단은 일괄 수집으로 보내지 않는다. open REVIEW 개수만으로 투자 매력도를 감점하거나 cap하지 않는다.
- 약점 개선안은 현재 read-only proposal이다. 개선 portfolio 생성, 신규 backtest 실행, registry / saved write는 하지 않으며, 실제 개선 효과는 별도 후속 task에서 Python strategy / engine / service boundary로 검증해야 한다.
- Python selection-readiness model은 state, suggested decision, Must Fix, open review items, monitoring seed를 같은 evidence packet에서 읽지만 standalone Decision Cockpit으로 렌더링하지 않는다.
- Final Review의 주 action은 one-shell 하단의 `최종 판단과 사유`다. canonical route는 `SELECT_FOR_PRACTICAL_PORTFOLIO`, `HOLD_FOR_MORE_PAPER_TRACKING`, `REJECT_FOR_PRACTICAL_USE`, `RE_REVIEW_REQUIRED` 그대로 저장하며 사용자 label만 `계속 추적`, `관찰 후 재검토`, `추적 대상에서 제외`, `Level2로 돌려보내기`로 표시한다. 사유를 직접 작성해야 CTA가 활성화되고 Decision ID / constraints / next action은 Python이 자동 생성한다.
- Final Review는 Evidence Appendix를 렌더링하지 않는다. Practical Validation / Robustness / Paper Observation / Investability raw detail은 이전 stage와 `남은 판단 근거`의 stored audit trace가 소유하며, source / 기준일은 카드의 접힌 상세에서 확인한다.
- Final Review는 Saved Decisions ledger, Dossier, Evidence Packet, Raw JSON을 렌더링하지 않는다. selected row의 운영 확인은 Operations > Portfolio Monitoring이 맡고, hold / reject / re-review row는 append-only audit data로 보존한다.
- Final Review의 investability packet은 새 저장 단계를 만들지 않고 기존 validation evidence를 compact하게 읽는다.
- Final Review의 profile-aware selection gate policy가 data trust, benchmark, provider / look-through, stress / robustness, leveraged / inverse, paper observation, construction risk, risk contribution, component role / weight, validation method strength, data coverage, backtest realism group을 판정한다. 같은 입력에서 만든 deployment readiness policy는 더 엄격한 live-readiness 감사 snapshot으로 보존한다.
- Decision Dossier는 Final Review row와 Selected Dashboard timeline을 사람이 읽는 markdown으로 묶는 read-only export다. source contract consistency를 표시하지만 자동 report 저장이나 새 판단 row를 만들지 않는다.
- selection hard blocker, critical `NOT_RUN` / `NEEDS_INPUT`, benchmark / comparator parity blocker, gross-only 또는 net/cost 적용 부재, weighted mix component role / weight rationale 부재, Final Review evidence 미준비가 남아 있으면 Monitoring 후보 handoff는 차단된다. 기본 `REVIEW` 항목은 Final Review 판단 record 저장을 막기보다 `open_review_items`로 남기고, Selected Dashboard와 향후 Live / Deployment Readiness에서 이어서 본다. 보류 / 거절 / 재검토는 Monitoring 후보로 올리지 않는 판단 기록이며, live approval / broker order / auto rebalance를 만들지 않는다.
- Structured waiver는 현재 구현하지 않는다. 향후 구현해도 `BLOCK` severity는 waiver 불가이고, 일부 `REVIEW_REQUIRED` gap만 expiry / review trigger / scope를 가진 구조화 waiver로 검토할 수 있다.
- Provider / look-through evidence는 source mix, freshness, as-of range를 함께 본다. stale provider snapshot은 pass가 아니라 review evidence다.
- Look-through Exposure Board는 holdings / exposure snapshot을 asset bucket, top holding, overlap, ETF별 coverage로 요약한다. Full holdings row는 DB 영역에 남고 workflow JSONL에는 compact summary만 남긴다.
- Construction Risk Audit은 component max weight, provider look-through coverage, top holding, holdings overlap, dominant asset bucket, unknown exposure를 별도 row로 본다. provider holdings / exposure가 없거나 partial이면 ready로 보지 않는다.
- Risk Contribution Audit은 component return matrix coverage, pairwise correlation, max risk contribution proxy, drop-one dependency, source strength를 별도 row로 본다. component matrix나 drop-one evidence가 없으면 ready로 보지 않고, DB price proxy / mixed source evidence는 `REVIEW`로 남긴다.
- Component Role / Weight Audit은 explicit role source coverage, profile-aware weight discipline, role concentration, profile intent fit, weight rationale coverage를 별도 row로 본다. role source가 없거나 partial이면 ready로 보지 않고, role preset이나 user memo 저장을 만들지 않는다.
- Construction Risk / Risk Contribution / Component Role / Weight Audit의 `BLOCKED`는 selected-route blocker다. weighted mix에서 component role / weight rationale의 핵심 `NEEDS_INPUT`은 selection blocker이며, 일반 `REVIEW`는 `open_review_items`로 남긴다. 단일 component 후보에는 mix 전용 risk contribution / component role weight audit을 selection gate에서 비적용으로 낮춘다. Final Review gate policy는 non-PASS row criteria를 evidence에 표시한다.
- Robustness Lab은 stress / rolling / sensitivity / overfit evidence를 compact summary로 묶어 Practical Validation과 Final Review가 같은 근거를 읽게 한다. Strategy-specific perturbation follow-up이나 `NOT_RUN` row는 pass가 아니다.
- Validation Method Strength는 walk-forward temporal validation, OOS holdout validation, regime split validation이 현재 후보의 검증 방법론을 충분히 뒷받침하는지 본다. 핵심 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 기본적으로 `open_review_items`로 남긴다. runtime replay, benchmark parity, provider freshness, robustness, PIT / survivorship은 각각 별도 owner 검증에서 본다.
- Data Coverage Audit은 DB price window, provider freshness, PIT replay / period coverage, universe listing, survivorship evidence를 분리해 본다. 핵심 `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker이며, `REVIEW`는 기본적으로 `open_review_items`로 남긴다. 현재 listing / asset profile row는 current listing evidence일 뿐이므로 historical universe나 delisting coverage가 없으면 survivorship PASS로 보지 않는다.
- Data Coverage Audit의 lifecycle metrics는 current snapshot, SEC identity cross-check, computed partial, actual coverage, delisting actual을 분리한다. 표시가 구체화돼도 partial evidence는 selected-route PASS 근거가 아니다.
- Evidence closure는 replay/PIT와 universe/survivorship derived check를 root issue 단위로 합친다. static manual universe의 historical selection 한계는 Final Review에서 인수할 수 있지만, dynamic historical universe의 PIT membership / delisting 근거 부재는 `engineering_required + critical` blocker다.
- Practical Validation은 root issue를 `지금 해결 가능 / 개발 필요 / 한계 인수 가능`으로 나누고, current Final Review eligible 후보는 unresolved actionable / critical engineering / missing contract가 모두 0이어야 한다.
- Final Review는 current 후보의 `선정 전 미해결 항목 0`을 확인한 뒤 accepted limit / final decision / Monitoring transfer를 기존 route와 판단 사유로 종결한다. final decision row에는 기존 `evidence_closure_snapshot`과 함께 chart point를 제외한 verdict, finding ids, structured Monitoring conditions, accepted root ids, source gaps를 `decision_brief_snapshot_v1`으로 저장한다. selected route는 기존 Gate와 closed closure를 모두 통과해야 `monitoring_candidate=True`가 되며 snapshot만으로 우회할 수 없다.
- Backtest Realism Audit은 transaction cost, net cost curve, turnover, cost / slippage sensitivity, liquidity / operability, net performance policy, rebalance timing, tax / account scope, execution boundary를 분리해 본다. 핵심 `NEEDS_INPUT` / `BLOCKED`와 명시적 transaction cost / net cost curve / net performance / gross-only selection gap은 selected-route blocker이며, 일반 `REVIEW`는 `open_review_items`로 남긴다. Final Review gate policy는 failing Backtest Realism row criteria도 policy evidence로 보여주므로 cost / slippage sensitivity나 liquidity gap이 generic route label 뒤에 숨지 않는다. 이 연결은 core strategy runtime이나 새 저장소를 만들지 않는다.
- Integrated Investability Gate QA는 construction risk 계열 audit, validation / coverage / realism audit, provider / robustness / paper observation / final evidence gate가 함께 작동할 때 ready는 selected-route를 허용하고, 기본 `REVIEW`는 selection을 막지 않는 open review item으로 넘기며, hard blocker는 selected-route를 차단하는 service contract를 유지한다. 동시에 `deployment_readiness_policy_snapshot`은 같은 `REVIEW`를 hold / re-review 수준으로 보존한다.
- Operations > Portfolio Monitoring은 모니터링 후보 선정 후 상태 확인 화면이며, legacy 구현 파일은 Selected Portfolio Dashboard 이름을 유지한다. 이제 화면 진입 시 Active Portfolio Monitoring Scenario를 먼저 보여준다. 사용자는 먼저 active portfolio의 현재 모니터링 상태와 portfolio-level 현재 가치, 손익, 총 수익률, CAGR, MDD, 계산 기준일, session update timestamp, daily badges, value curve, 전략별 성과, 리밸런싱 target table을 본다. Portfolio가 없으면 생성 안내, portfolio는 있지만 strategy가 없으면 strategy board 안내, strategy는 있지만 scenario가 없으면 update 실행 안내를 보여준다. 그 아래 `나의 포트폴리오` fixed-height card shelf에서 monitoring portfolio를 만들거나 선택하고, delete / raw setup management는 접힌 관리 영역에서만 다룬다. 선택된 portfolio는 portfolio name / description edit와 compact strategy slot board로 관리하며, Final Review selected 후보 pool에서 selected decision을 추가한다. 이 dashboard portfolio는 backtest 전략 정의가 아니라 사용자 모니터링 컨테이너이며, 같은 포트폴리오 안 중복 selected decision은 추가하지 않는다. 각 slot은 selected decision, 시작일, 종료일 latest mode, balance, optional memo를 저장하며 `전략 적용`과 scenario update는 분리된다. Portfolio Monitoring Scenario는 strategy board 아래의 `포트폴리오 시나리오 업데이트`를 누를 때만 slot 기준 selected component contract를 다시 실행하고, 종료일이 latest mode이면 DB 최신 시장일을 사용한다. 기본 업데이트는 아직 실행되지 않았거나 현재 slot signature와 맞지 않는 stale strategy만 실행하며, `전체 재실행`을 켜야 기존 최신 결과까지 다시 replay한다. Strategy별 Recheck Operations Preflight / Recheck Readiness / Symbol Freshness / Provider Evidence / Monitoring Signals는 Streamlit eager tab 비용을 피하기 위해 사용자가 선택한 1개 전략 상세를 열 때만 렌더링한다. Preflight는 selected replay contract readiness와 DB symbol freshness를 하나의 read-only route로 묶고, Final Review embedded replay contract를 먼저 보며 Current Candidate Registry는 fallback으로 사용한다. Provider Evidence는 selected component ticker weight로 기존 DB provider / holdings / exposure context를 read-only로 읽고 `NOT_RUN`, stale freshness, partial / bridge / proxy coverage, missing operability / holdings / exposure를 pass로 처리하지 않는다. Continuity check는 Final Review selected row가 source contract / evidence packet / component target / review trigger / timeline / recheck input 경계를 갖췄는지 읽고, timeline source mismatch는 blocked issue로 표시한다. Timeline은 selection / evidence gate / recheck / drift / trigger preview를 read-only로 읽고 monitoring log를 자동 저장하지 않는다. Review Signals는 Recheck Comparison을 CAGR / MDD / benchmark spread threshold의 policy owner로 사용하며 preflight / provider / comparison route를 계속 관찰 / 보강 필요 / 대체 검토 성격의 read-only signal board로 번역한다. 같은 dashboard portfolio 안 selected 전략이 2개 이상이면 최신 scenario 결과를 전환 비교 표로 볼 수 있다. Recheck Comparison은 최신 Monitoring Scenario가 기존 Final Review baseline을 계속 지지하는지 read-only로 비교하며, 미실행이나 오류를 pass로 처리하지 않는다. Allocation evidence boundary는 optional Actual Allocation이 수동 / session-only evidence이며 raw input / alert 저장, account / broker 연결, 주문, 자동 리밸런싱을 만들지 않음을 표시한다. Live / Deployment Readiness는 마지막 optional preflight로만 남긴다.
- Portfolio Monitoring의 `시장 심리 Context Overlay`는 화면 진입부에서 현재 시장 배경을 보여줄 뿐이다. Monitoring Scenario, Review Signals, saved dashboard setup, monitoring log, broker order, auto rebalance와 연결하지 않는다.

## Storage Boundary

- Portfolio Selection current의 main durable chain은 `PORTFOLIO_SELECTION_SOURCES.jsonl -> PRACTICAL_VALIDATION_RESULTS.jsonl -> FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`은 Final Review 판단 record를 append-only로 담는다. 새 row는 `monitoring_candidate` / `monitoring_handoff_state`, `evidence_closure_snapshot`, compact `decision_brief_snapshot`을 포함한다. Portfolio Monitoring은 selected row의 structured `decision_brief_snapshot.monitoring_conditions`를 우선 읽고, snapshot 없는 legacy row는 `paper_tracking_snapshot.review_triggers`를 fallback으로 읽는다. 기존 row는 재작성하지 않는다.
- `SELECTED_DASHBOARD_PORTFOLIOS.jsonl`은 Operations > Portfolio Monitoring 전용 saved setup이다. File name은 legacy dashboard term을 유지한다. Final Review 판단, monitoring evidence, approval record가 아니며 user-created portfolio 이름, 설명, selected decision strategy slot, start / latest-end mode / balance / memo만 보존한다.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`는 사용자가 명시적으로 남기는 optional monitoring check record이며 자동 저장 대상이 아니다.
- runtime registry path는 runtime-defined라 첫 write 전에는 로컬 파일이 없을 수 있다. 파일 부재는 저장 경계 drift가 아니다.
- Waiver persistence는 현재 없다. future implementation이 필요하면 새 JSONL registry가 아니라 compact final decision snapshot을 먼저 검토한다.
- legacy candidate / proposal / paper registry는 보존하지만, 현재 main flow의 필수 단계로 확장하지 않는다.
- raw provider / holdings / macro evidence는 DB에 두고, workflow JSONL에는 compact evidence와 blocker summary만 저장한다.
- 자세한 저장 기준은 `docs/data/STORAGE_GOVERNANCE.md`를 따른다.

## Main Files

| Area | Files |
|---|---|
| Backtest stage routing | `app/web/backtest_common.py`, `app/web/backtest_workflow_routes.py`, `app/web/backtest_page.py` |
| Backtest Analysis | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare/` |
| Practical Validation | `app/web/backtest_practical_validation/`, `app/services/backtest_practical_validation_modules.py`, `app/services/backtest_practical_validation_board_registry.py`, `app/services/backtest_selected_route_preflight.py`, `app/services/backtest_construction_risk_audit.py`, `app/services/backtest_risk_contribution_audit.py`, `app/services/backtest_component_role_weight_audit.py`, `app/services/backtest_temporal_validation.py`, `app/services/backtest_validation_efficacy.py`, `app/services/backtest_data_coverage_audit.py`, `app/services/backtest_realism_audit.py` |
| Final Review | `app/web/backtest_final_review/`, `app/services/backtest_final_review_decision_brief.py`, `app/services/backtest_evidence_read_model.py` compatibility |
| Evidence closure contract | `app/services/backtest_evidence_closure.py`, `app/services/backtest_practical_validation_replay.py` |
| Operations > Portfolio Monitoring | `app/web/final_selected_portfolio_dashboard*.py`, `app/runtime/backtest/read_models/final_selected_portfolios.py` |
| Selection persistence | `app/runtime/backtest/stores/portfolio_selection.py` |

## Update Rules

이 문서는 아래가 바뀌면 갱신한다.

- Backtest 상단 stage가 바뀔 때
- selection source / validation result / final decision record 관계가 바뀔 때
- Practical Validation과 Final Review의 stage ownership이 바뀔 때
- Operations > Portfolio Monitoring이 read-only monitoring 경계를 넘어서거나 저장 경계가 바뀔 때
