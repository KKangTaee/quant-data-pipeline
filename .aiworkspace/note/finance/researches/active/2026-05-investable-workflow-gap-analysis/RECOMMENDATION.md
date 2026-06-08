# Recommendation

Status: Accepted for Phase 0; refreshed for 2026-06-08 baseline
Last Updated: 2026-06-08

## Recommended Direction

현재 프로젝트는 "더 많은 백테스트 기능"보다 "백테스트를 실전 후보로 승격하는 검증 효력"을 먼저 강화해야 한다.

## One-Line Recommendation

추천 방향은 다음 한 줄이다.

> Backtest 결과를 Final Review로 바로 밀어 올리는 흐름을 유지하되, 중간에 `Investability Evidence Packet`과 stricter validation gate를 만들어 `선택 가능`, `보류`, `재검토`, `폐기` 이유를 더 엄격하게 기록한다.

## Decision Scope

- Immediate next build: `Investability Evidence Packet + Validation Gate Hardening + Assumption Disclosure + Source Breadcrumb`
- Needs human approval before execution: critical `NOT_RUN` 차단 정책, waiver 허용 여부, mandatory paper observation 기준
- Longer roadmap option: Robustness Lab V1, Look-Through Exposure Board, Persistent Monitoring Timeline, report export
- Not approved / parking lot: broker 연결, 자동 주문, auto rebalance, account aggregation

## Why This Direction

1. 현재 흐름은 맞다.
   Backtest -> Practical Validation -> Final Review -> Selected Dashboard의 stage ownership은 제품의 좋은 중심축이다. 이걸 갈아엎기보다 각 gate의 효력을 강화하는 편이 낫다.

2. 사용자가 느끼는 약점은 구조의 부재보다 기준의 약함에 가깝다.
   데이터 저장 기준, validation 효력, backtest robustness, monitoring 기록이 아직 "실전 투자 판단"이라고 부르기에는 느슨하다.

3. 상용 / 실서비스 패턴도 같은 방향을 가리킨다.
   QuantConnect는 재현 가능한 research/backtest/deploy 경계를, Bloomberg PORT는 data validation/risk/reporting 통합을, Morningstar X-Ray는 holdings look-through를, IBKR PortfolioAnalyst는 monitoring/benchmark/attribution을, Portfolio Lab은 historical backtest와 forward-looking simulation의 병행을 보여준다.

4. current product boundary와 충돌하지 않는다.
   broker order나 live approval 없이도 실전 투자 전 판단 효력을 크게 높일 수 있다.

## What To Build First

### 1. Investability Evidence Packet

Final Review에서 선택 전에 아래 항목을 하나의 read model로 보여준다.

| Packet section | Meaning |
| --- | --- |
| Source Chain | `selection_source_id -> validation_id -> decision_id` |
| Backtest Contract | strategy, universe, period, rebalance, benchmark, costs, data trust |
| Data Validation | price freshness, excluded ticker, malformed rows, PIT / current snapshot limitations |
| Provider / Look-through | holdings / exposure / operability / macro coverage and missing symbols |
| Benchmark Parity | same period / frequency / coverage |
| Robustness Summary | rolling, stress, baseline, sensitivity, overfit warnings |
| Critical Gaps | critical `NOT_RUN`, proxy-only evidence, stale provider, unsupported replay |
| Assumptions & Limits | hypothetical backtest, no investment advice, no live approval, current snapshot caveats |
| Operator Decision | selected / hold / reject / re-review reason and constraints |

### 2. Validation Gate Hardening

기본 정책 제안:

| Condition | Default handling |
| --- | --- |
| Hard blocker | Final selection blocked |
| Critical `NOT_RUN` in stress / robustness / benchmark parity / provider look-through | Final selection blocked unless explicit waiver is allowed |
| Proxy-only provider evidence for major allocation | Default `HOLD_FOR_MORE_PAPER_TRACKING` or `RE_REVIEW_REQUIRED` |
| Leveraged / inverse ETF without objective / holding-period evidence | Selection blocked |
| Stale macro / provider snapshot | Review required; selection requires acknowledgement |
| No benchmark | Selection blocked for most profile types |

Open decision: waiver를 허용할지 정해야 한다.

- Conservative option: critical `NOT_RUN` is always blocking.
- Flexible option: critical `NOT_RUN` can be waived only with reason, expiry / re-review date, and monitoring trigger.

추천은 Flexible option이다. 지금 provider coverage가 partial이므로 항상 blocking으로 두면 workflow가 지나치게 막힐 수 있다. 대신 waiver는 "선택 사유"가 아니라 "남은 위험을 알고 보류하지 않는 이유"로 저장해야 한다.

### 3. Assumption & Limitation Disclosure

Final Review 저장 전 자동 생성 checklist:

- 이 결과는 hypothetical backtest이며 미래 수익을 보장하지 않는다.
- provider / holdings / macro data는 coverage와 staleness 한계가 있다.
- current ETF snapshot은 과거 특정 시점의 truth가 아닐 수 있다.
- FRED macro vintage / ALFRED 계층은 아직 구현되지 않았다.
- live approval, broker order, auto rebalance가 아니다.
- 비용, slippage, tax, account-specific constraints는 제한적으로만 반영됐다.

### 4. Source-Of-Truth Breadcrumb

주요 화면에서 항상 현재 record chain을 보여준다.

```text
Backtest source -> Practical Validation result -> Final Review decision -> Monitoring snapshots
```

이렇게 하면 legacy registry와 V2 registry가 섞여도 사용자가 현재 판단의 원본을 잃지 않는다.

## Pilot Scope

첫 build는 코드 변경 범위를 좁혀야 한다.

| Slice | Include | Exclude |
| --- | --- | --- |
| Read model | packet summary builder, gate evaluation builder, assumption list builder | new DB schema |
| UI | Final Review packet panel, critical gap panel, breadcrumb | large UX redesign |
| Persistence | final decision row에 packet snapshot / waiver fields 추가 | registry rewrite |
| Tests | service contract tests for gate / selected route / waiver | full Streamlit E2E |
| Docs | Portfolio Selection Flow update | Roadmap promotion before user approval |

## What To Defer

- Full Robustness Lab: first define packet / gate contract, then add walk-forward / Monte Carlo / parameter sweep.
- Look-Through Board: provider foundation exists, but strict board should follow gate policy.
- Monitoring Timeline: selected decision packet should exist before monitoring snapshots reference it.
- React / API product surface migration: product contract should stabilize first.
- Broker linkage / live trading: remain out of scope.

## Decision Checkpoint

Before development, decide these with the user:

1. Should critical `NOT_RUN` block final selection, or allow explicit waiver?
2. Which diagnostics are critical for `SELECT_FOR_PRACTICAL_PORTFOLIO`?
3. Is paper observation mandatory before selection, or can selection mean "candidate selected for practical portfolio tracking" rather than "capital deployment ready"?
4. Should current ETF provider snapshot be enough, or should each final decision require an as-of snapshot id?
5. What wording should replace or clarify "투자 가능 후보" to avoid sounding like live approval?

## Proposed Next Handoff

This direction has been accepted into the active phase:

```text
phase: investability-decision-foundation
location: .aiworkspace/note/finance/phases/active/investability-decision-foundation/
```

The first narrow implementation task was:

```text
task: investability-evidence-packet-v1
owner skill: finance-backtest-web-workflow
scope:
  - Final Review evidence packet read model
  - critical gap / waiver save policy
  - source chain breadcrumb
  - assumption disclosure
  - focused service contract tests
```

Expected follow-up tasks:

1. `validation-gate-hardening-v1`
2. `data-provenance-and-governance-v1`
3. `look-through-exposure-board-v1`
4. `robustness-lab-v1`
5. `selected-monitoring-timeline-v1`

## Evidence Summary

- Local audit shows strong stage boundaries but weak critical-missing-data handling.
- Local data docs already identify PIT, survivorship, current snapshot, stale data, provider coverage limits.
- Benchmarks consistently use reproducible experiment contracts, look-through exposure, scenario / simulation, reporting, benchmarked monitoring, and assumption disclosure.
- Regulatory / professional sources warn that backtesting needs simulation / sensitivity support and that automated investment tools must disclose assumptions and limitations.

## Risks And Unknowns

- If gate hardening is too strict, the product may feel blocked before provider coverage is mature.
- If waiver is too easy, it will recreate the current validation weakness in a different UI.
- If packet output is too verbose, users will ignore it.
- If "투자 가능 후보" wording remains too strong, the no-live boundary may be misunderstood.
- If data governance is deferred too long, new evidence features may increase storage confusion.

## Final Recommendation

Approve a narrow first phase around `Investability Evidence Packet` and `Validation Gate Hardening`. Do not start with new strategy research, UI platform migration, or live trading features. The first successful outcome should be: when a candidate reaches Final Review, the system can explain in one place exactly what was tested, what was not tested, what was proxy/current snapshot, what blocks selection, what was waived, and what monitoring obligation remains.

## 2026-06-08 Revised Recommendation

### One-Line Recommendation

현재 제품 구조는 유지한다. 다음 방향은 `Backtest -> Practical Validation -> Final Review -> Portfolio Monitoring`을 더 많은 화면으로 늘리는 것이 아니라, `전략 연구 결과를 제품 후보로 승격하는 계약`과 `선정 이후 monitoring snapshot / review loop`를 강화하는 것이다.

### Session Usage Model

이 세션의 기본 역할은 아래처럼 둔다.

| Worktree / session | Role |
| --- | --- |
| `backtest-dev` / `codex/backtest-dev` | 전략 심층 분석, 약점 파악, 개선, 추가 전략 개발 |
| `main-dev` current session | 현재 제품 흐름 감사, 상용 benchmark, 개발 후보 우선순위, 향후 phase / task handoff |
| Future implementation sessions | 승인된 단위별 실제 개발. Backtest UI / monitoring / data / strategy 구현 owner를 별도로 선택 |

이 세션은 아직 AGENTS 지침을 바꾸는 세션이 아니다. 다만 향후 넓은 방향 요청을 처리할 때는 product research bundle을 기준으로 1차 / 2차 / 3차 흐름을 먼저 공유한다.

### Tentative Roadmap

| 차수 | 목적 | 바뀔 화면 / 파일 범위 | 완료 조건 | 다음 차수 연결 |
| --- | --- | --- | --- | --- |
| 1차: Product Flow Baseline | 현재 Backtest -> Validation -> Final Review -> Monitoring 흐름, 장점 / 약점 / legacy 경계를 정리 | research bundle 중심, 코드 변경 없음 | 현재 장점, 단점, 삭제/보존 후보, 세션 역할이 명확해짐 | 2차 benchmark와 gap 비교 |
| 2차: Benchmark Gap Synthesis | 상용 quant / portfolio analytics 제품 패턴을 비교해 부족한 기능을 분류 | research bundle 중심, 외부 source 기록 | 재사용할 패턴과 현재 boundary와 충돌하는 패턴 구분 | 3차 feature candidates |
| 3차: Development Candidate Selection | Now / Next / Later / Parking Lot으로 후보를 나누고 승인 받을 build 단위를 정함 | `FEATURE_CANDIDATES.md`, `RECOMMENDATION.md` | 다음에 열 development session의 후보 1~2개가 명확해짐 | 별도 task / phase 생성 |
| 4차: Approved Build Handoff | 승인된 후보만 별도 세션에서 task / phase로 전환 | future task / phase docs and code | owner skill, scope, verification, out-of-scope 확정 | 구현 세션 시작 |

이번 refresh는 1차~3차의 baseline을 만든 것이다. 4차 구현 handoff는 아직 승인 전이다.

### Revised Priority

| Priority | Candidate | Why now |
| --- | --- | --- |
| 1 | `Monitoring Snapshot / Review Loop V2` | 선정 이후 관리가 현재 가장 제품적인 빈칸이다. 상용 portfolio tools는 drift, benchmark, risk, report를 반복 snapshot으로 다룬다. |
| 2 | `Strategy Promotion Contract For Backtest-Dev Handoff` | backtest-dev에서 개선한 전략을 main 제품 흐름으로 안전하게 받아들이려면 promotion 기준이 필요하다. |
| 3 | `Robustness Experiment Registry` | 이미 validation rows는 있으나 run-set / parameter / OOS / walk-forward evidence를 하나의 실험 단위로 묶는 계약이 약하다. |
| 4 | `Data Provenance / PIT Evidence Contract` | current snapshot과 historical truth가 섞이지 않게 evidence row의 source-date / available-at / snapshot-kind를 통일해야 한다. |
| 5 | `Legacy Archive Demotion Matrix` | 삭제보다 먼저 archive / recovery 의미를 고정해 사용자 혼란을 줄인다. |
| 6 | `Large Surface Refactor Round 2` | 큰 기능 추가 전 `backtest_compare`와 Portfolio Monitoring UI/runtime을 feature boundary별로 나눌 필요가 있다. |

### What To Improve

- Portfolio Monitoring: session scenario 결과를 명시적 monitoring snapshot으로 저장하고, review trigger / benchmark delta / drift / provider freshness / open issue를 누적한다.
- Strategy governance: Risk-On Momentum 5D 같은 research lane이 Practical Validation / Final Review / Monitoring policy로 올라가기 위한 handoff checklist를 만든다.
- Robustness: 단일 equity curve보다 walk-forward, OOS, parameter perturbation, cost/slippage, regime, Monte Carlo/bootstrap run-set을 기준으로 본다.
- Data provenance: provider / macro / lifecycle / factor evidence가 current snapshot인지, decision-time available evidence인지, proxy인지 항상 보이게 한다.
- UX: evidence detail보다 "Ready / Must Fix / Open Review / Missing / Next Owner" 요약을 앞세운다.

### What To Remove Or Demote

삭제는 아직 최우선이 아니다. 먼저 demotion matrix를 만든다.

| Keep / demote | Direction |
| --- | --- |
| Candidate Review | legacy compatibility / archive route로 낮춤 |
| Portfolio Proposal | 기존 proposal evidence는 보존, 신규 primary path에서는 강조하지 않음 |
| Backtest Run History | archive / recovery로 보존 |
| Candidate Library | archive / recovery로 보존 |
| `Selected Portfolio Dashboard` wording | 사용자-facing에서는 `Portfolio Monitoring`; 파일명 rename은 별도 refactor |
| run history / generated artifacts | generated/local artifact로 유지, 명시 승인 없이는 커밋하지 않음 |

### What Not To Do Yet

- 새 전략 추가 자체를 `main-dev`에서 진행하지 않는다.
- broker account 연결, order, auto rebalance, live approval을 추가하지 않는다.
- Streamlit -> React/API 대형 이전을 첫 개선으로 잡지 않는다.
- legacy registry / saved setup / run history를 정리 명목으로 재작성하지 않는다.
- Candidate Library나 Run History를 즉시 삭제하지 않는다.

### Recommended Next Decision

다음 개발 세션을 연다면 첫 후보는 `Monitoring Snapshot / Review Loop V2`가 가장 좋다.

이유:

- 현재 제품 흐름의 끝단을 강화한다.
- backtest-dev 전략 연구와 독립적으로 진행 가능하다.
- no-live boundary를 유지하면서도 "상용 제품처럼 관리한다"는 느낌을 가장 빨리 준다.
- 이후 Strategy Promotion Contract와 Robustness Registry가 붙을 안정적인 대상이 생긴다.

두 번째 후보는 `Strategy Promotion Contract For Backtest-Dev Handoff`다. 이 후보는 backtest-dev 결과가 나오는 즉시 main product workflow로 안전하게 흡수하기 위한 기준점이 된다.

### Handoff Rule

추천은 아직 승인된 roadmap이 아니다. 사용자가 특정 후보를 승인하면 그때:

1. `finance-task-intake`로 scope를 분류한다.
2. 관련 domain skill을 선택한다.
3. active task 또는 phase를 연다.
4. 구현 범위와 하지 않을 일을 먼저 공유한다.
5. 코드 / QA / docs sync를 별도 개발 세션에서 진행한다.
