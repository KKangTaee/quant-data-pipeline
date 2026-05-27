# Recommendation

Status: Draft
Last Updated: 2026-05-28

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

If this direction is approved, the next implementation task should be:

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
