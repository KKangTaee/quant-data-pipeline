# Current Project Audit

Status: Active
Last Updated: 2026-06-29 KST

## Summary

현재 Backtest Analysis는 핵심 기능 자체는 풍부하다.
문제는 기능 부재보다 정보 배치와 판단 무게다.

- 상단 `Backtest 사용 안내`는 접혀 있어도 첫 화면의 제품 인상을 "읽어야 하는 매뉴얼"로 만든다.
- `Reference help - Backtest > Backtest Analysis`는 Backtest Analysis 기본 작업과 직접 관련 없는 Reference entrypoint다. 화면 내 안내로 두기보다 제거하고 Reference 영역으로 돌려야 한다.
- `전략 개발 참고`는 4C 이후 숨겨졌지만 여전히 화면 하단에 섹션 / checkbox / 숨김 보드 구조가 남아 있어 패널 확장 방향을 다시 부를 수 있다.
- `Latest Backtest Run`은 Data Trust와 handoff 정보를 담지만, A/B/C/D 안내 카드, badge, Data Trust cards, warning box, handoff card가 비슷한 의미를 반복한다.
- 현재 `Practical Validation`으로 보내기 조건은 `promotion_decision != hold`, 실행 blocker 없음, 검증 blocker 없음에 의존한다. 이 조건은 "검증을 받으러 가는 단계"에 대해 지나치게 선별적일 수 있다.

제품 방향은 유지한다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
```

다만 Backtest Analysis가 모든 검증을 미리 끝내는 화면처럼 보이면 안 된다.

## Current Product Promise

Backtest Analysis는 전략을 실행 / 비교하고 후보 source를 만드는 화면이다.
Practical Validation은 후보를 실전 검토 근거로 구조화한다.
Final Review는 gate를 통과한 후보만 selected-route decision으로 저장한다.

따라서 Backtest Analysis의 첫 화면이 해야 할 일은 다음 네 가지다.

1. 어떤 전략 / mix를 실행할지 빠르게 정한다.
2. 실행 결과의 성과와 데이터 상태를 한눈에 본다.
3. 결과가 다음 단계로 갈 수 있는지 확인한다.
4. 갈 수 없다면 무엇을 다시 해야 하는지 짧게 알려준다.

## Implemented Capabilities

| Area | Implemented Facts | Main Files |
|---|---|---|
| Workflow shell | `Backtest Analysis`, `Practical Validation`, `Final Review` 3단계 panel selector | `app/web/pages/backtest.py`, `app/web/backtest_workflow_routes.py` |
| Single Strategy | 전략 선택, strategy-specific form, DB-backed execution, latest result display | `app/web/backtest_single_strategy.py`, `app/web/backtest_single_forms.py`, `app/web/backtest_single_runner.py`, `app/services/backtest_execution.py` |
| Portfolio Mix Builder | 여러 전략 실행, component result 비교, weighted mix, saved replay, Practical Validation source handoff | `app/web/backtest_compare.py`, `app/services/backtest_compare_execution.py`, `app/services/backtest_weighted_portfolio.py`, `app/services/backtest_saved_portfolio_replay.py` |
| Result display | summary metrics, equity curve, data trust, policy signal, selection history, result/meta tabs | `app/web/backtest_result_display.py`, `app/services/backtest_result_read_model.py` |
| Research/reference panels | strategy inventory, strict annual / ETF bridge, Risk-On governance, ETF evidence/current anchor/rerun matrix | `app/web/backtest_analysis.py`, `app/services/backtest_analysis_research_board.py` |
| Candidate source handoff | latest run 또는 weighted mix를 Practical Validation source로 등록 | `app/web/backtest_result_display.py`, `app/web/backtest_compare.py`, `app/services/backtest_practical_validation.py` |

## Strategy Function Map

| Strategy Group | How It Works | Current Product Interpretation |
|---|---|---|
| Equal Weight | 지정 ETF / ticker를 균등 보유하고 rebalance interval마다 비중을 재조정한다. | baseline / exposure sleeve. 단독 alpha claim보다 비교 기준으로 유용하다. |
| GTAA | 평균 수익률 score 상위 ETF를 고르고 MA trend filter를 통과하지 못한 자산은 현금 또는 defensive sleeve로 처리한다. | tactical ETF candidate / sleeve. 조건과 risk-off overlay가 핵심이다. |
| Global Relative Strength | 여러 lookback return score로 상위 ETF를 고르고 trend filter 실패 slot은 cash proxy로 둔다. 5A 이후 cadence, cash, benchmark, concentration metadata가 강화됐다. | runtime-hardened ETF strategy. evidence expansion은 필요하지만 result contract 방향은 좋다. |
| Risk Parity Trend | trend/min-price eligible ETF에 대해 최근 변동성 inverse weight를 계산하고, 조건 불충분 / guardrail 상태에서는 cash-only가 된다. 5B 이후 inverse-vol / cash-only / low-vol overweight metadata가 강화됐다. | runtime-hardened defensive ETF strategy. default panel 추가가 아니라 result interpretation 강화가 맞다. |
| Dual Momentum | lookback return 상위 ETF를 고르되 trend rejected slot은 surviving ticker로 재가중하지 않고 cash proxy로 둔다. 5B 이후 trend rejection / concentration / whipsaw metadata가 강화됐다. | runtime-hardened ETF strategy. concentration / whipsaw 설명이 중요하다. |
| Strict Annual Quality / Value / Quality+Value | annual statement shadow factor 기반으로 월별 선택 / 보유를 시뮬레이션하고 selection history를 남긴다. | 가장 후보 source에 가까운 factor group. 그래도 Practical Validation gate는 필요하다. |
| Strict Quarterly Prototype | quarterly statement shadow factor 기반 prototype. annual strict와 같은 maturity가 아니다. | research-only / prototype label 유지. 기본 추천 candidate처럼 보이면 안 된다. |
| Risk-On Momentum 5D | daily OHLCV, D+1 open execution, futures macro mean-z filter, scanner/trade log, comparison/sensitivity/stability artifacts를 만든다. | Daily swing research lane. Practical Validation / Final Review / Monitoring 연결은 별도 governance 필요. |

## UX / Workflow Friction

### 1. Top guidance is the wrong artifact

`Backtest 사용 안내`는 기능을 설명하지만, 사용자의 다음 행동을 줄이지 않는다.
상용 제품의 상단은 보통 "지금 무엇을 만들거나 확인할 수 있는가"를 보여준다.
현재 안내는 운영 경계, history, dashboard, prototype 주의까지 한 번에 담아 초반 인지부하가 크다.

Recommended change:

- 제거하거나, 한 줄짜리 workflow stepper / active task bar로 대체한다.
- 자세한 설명은 `Reference > Guides`로 이동한다.
- 상단은 "후보 만들기 / 검증으로 보내기 / 최종 검토"의 현재 단계와 바로 할 일만 보여준다.

### 2. Reference help should not live in Backtest Analysis

`Reference help - Backtest > Backtest Analysis`는 Reference page의 역할이다.
Backtest Analysis에서 사용자가 이미 실행 / 비교 / 후보 생성 중이라면 이 블록은 거의 읽히지 않거나, 읽혀도 실행을 늦춘다.

Recommended change:

- Backtest Analysis render path에서 제거한다.
- Reference link가 필요하면 화면 우상단 small text link 또는 Reference page에만 둔다.
- "개선" 명목으로 새로운 guide expander를 추가하지 않는 원칙을 task acceptance criteria에 넣는다.

### 3. Strategy development reference panels should move out of the default product gravity

4C가 숨긴 것은 좋은 방향이지만, `전략 개발 참고` section 자체가 여전히 Backtest Analysis의 일부다.
이 자료는 가치가 있지만 사용자-facing 기본 workflow가 아니라 strategy research / reference / report material이다.

Recommended change:

- 1차에서는 Reference help 제거와 함께 `전략 개발 참고` 섹션을 기본 Backtest Analysis에서 제거하거나 더 낮은 developer-only/debug route로 이동한다.
- strategy inventory / ETF rerun matrix / current anchor는 필요하면 research/report에서 보게 한다.
- Backtest Analysis에는 strategy maturity label을 큰 표가 아니라 결과 옆 compact badge로만 남긴다.

### 4. Latest Run has useful checks but repeats itself

Current repeated layers:

- A/B/C/D checkpoint strip
- availability badges
- Data Trust Summary cards
- Data Trust badge strip
- warning block
- handoff card
- handoff button panel
- Candidate Readiness checkpoint / score area

Recommended change:

- result top을 `Run Summary` 하나로 압축한다.
- 첫 줄은 strategy, period, actual end, return/CAGR/MDD, data state, next action만 보여준다.
- Data Trust는 "정상 / 확인 필요 / 차단" 1개 status와 detail disclosure로 낮춘다.
- Candidate Readiness 점수는 제거하거나 debug disclosure로 낮추고, 사용자는 `다음 행동`만 먼저 보게 한다.

### 5. Handoff gate is probably too strict for the source-creation stage

현재 `can_submit`은 promotion signal과 execution / validation blockers가 모두 양호해야 한다.
하지만 Practical Validation은 원래 provider / coverage / realism / robustness를 확인하는 다음 단계다.

Recommended policy split:

| Decision | Should Hard Block? | Reason |
|---|---:|---|
| result bundle missing / empty result rows | Yes | source 자체가 없음 |
| unsupported downstream strategy, e.g. Risk-On research lane or quarterly prototype if not approved | Yes | downstream contract 없음 |
| no replayable payload / source identity | Yes | Practical Validation이 source를 재구성할 수 없음 |
| price freshness warning | No, review | 검증에서 확인할 수 있는 데이터 상태 |
| promotion_decision = hold | Usually no, but mark not recommended | hold를 검증으로 보내 원인을 확인할 수 있어야 할 때가 있음 |
| provider / liquidity / benchmark warning | No, review | Practical Validation의 본업 |
| live approval / broker readiness missing | Never relevant here | current product boundary 밖 |

This means the next implementation should replace "Candidate Readiness score" with "Validation handoff eligibility":

- `보낼 수 있음`: source contract exists, result rows exist, supported strategy.
- `보낼 수 있지만 주의`: Data Trust / promotion / provider warning exists.
- `보낼 수 없음`: source contract missing, unsupported research/prototype lane, empty result.

## Data And Validation Risks

- Data Trust warning should remain visible. Removing guide text must not hide point-in-time, stale price, survivorship, provider coverage risks.
- Quarterly prototype must not lose its `research-only` interpretation through UI simplification.
- Risk-On Momentum must not become Practical Validation-ready without daily swing governance.
- Backtest Analysis must not directly fetch provider / FRED data.
- Practical Validation `NOT_RUN` is still not pass.

## Audit Conclusion

The product should not add another guide or evidence panel.
The next development should remove guide-like surfaces from Backtest Analysis, replace the top with a compact action-focused workbench header, and simplify Latest Run into a summary-first result with a clearer handoff policy.
