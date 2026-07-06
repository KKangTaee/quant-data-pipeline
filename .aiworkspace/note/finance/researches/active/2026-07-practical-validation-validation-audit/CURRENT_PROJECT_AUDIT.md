# Current Project Audit

Status: Active
Date: 2026-07-06
Subject: Practical Validation 검증 체계와 Flow 4 정보 구조

## Executive Summary

현재 Practical Validation의 검증 항목은 방향 자체는 대체로 맞다. source contract, 최신 runtime replay, benchmark parity, PIT / survivorship, price coverage, cost / slippage, liquidity, net performance 같은 기준은 실전검증에서 꼭 필요하다.

문제는 세 가지다.

1. Flow 4의 첫 메시지가 `Final Review로 넘기기 전 확인 기준`이라서, 사용자가 "검증 결과"보다 "다음 단계 이동 조건"을 먼저 읽는다.
2. core validation, conditional evidence, downstream reference, selected-route preflight가 같은 기준 그룹 안에 섞여 있다.
3. 일부 검증은 신빙성은 있지만 모든 후보에 hard blocker로 쓰기엔 과하다. 특히 stress / robustness, construction risk, provider freshness, walk-forward / OOS / regime, sentiment context는 후보 특성과 증거 수준에 따라 severity를 달리해야 한다.

따라서 다음 구현 방향은 다음과 같다.

- Flow 4 메인: `카테고리별 검증 결과`
- Flow 4 보조: Final Review 이동 가능성 compact summary
- Gate policy: core blocker / review / conditional / reference 분리
- UI copy: `NEEDS_INPUT`은 사용자에게 `근거 보강 필요`로 읽히게 하고, 기술 tag로만 남긴다.

## Current Product Promise

Practical Validation은 Backtest Analysis에서 넘어온 후보가 Final Review에서 검토될 만큼 실전 근거를 갖췄는지 확인하는 2차 검증 화면이다.

현재 문서와 코드 기준으로 화면은 5-flow다.

1. 후보 / 검증 프로필 확인
2. 실전 검증 실행
3. 2차 검증 결론 / Fix Queue
4. 근거 Workbench
5. 저장 / Final Review 이동

이 흐름에서 Flow 3은 결론과 먼저 해결할 일을 보여주고, Flow 4는 그 결론을 만든 검증 근거를 카테고리별로 보여줘야 한다.

## Current Implementation Inventory

### Gate Status Policy

`BLOCKED`, `NEEDS_INPUT`, `NOT_RUN`은 block status다. `REVIEW`는 pass가 아니지만 Final Review에서 판단 근거로 확인할 상태다. `PASS`와 `READY`만 통과 상태다.

### Required Modules

현재 required module은 다음이다.

| Module | Current Role | Audit Decision |
| --- | --- | --- |
| `source_integrity` | source id, active components, weight total, Data Trust, execution boundary, curve evidence 확인 | 유지. Core blocker가 맞다. |
| `latest_replay` | 최신 DB 기준 runtime replay와 period coverage 확인 | 유지. Core blocker가 맞다. |
| `benchmark_parity` | 후보와 benchmark / comparator가 같은 기간 / frequency / coverage인지 확인 | 유지. Core blocker가 맞다. |
| `validation_efficacy` | source contract, data trust, replay, benchmark, walk-forward, OOS, regime, provider, robustness, PIT, survivorship, boundary를 한 번 더 감사 | 유지하되 재분류 필요. 너무 많은 중복 기준을 한 module에 포함한다. |
| `data_coverage` | price window, provider freshness, PIT window, universe / listing, survivorship, storage boundary 확인 | 유지하되 provider row는 후보 특성별 조건부로 낮춰야 한다. |
| `construction_risk` | component weight, provider look-through, top holdings, overlap, exposure 확인 | 조건부 / review로 낮춘다. ETF-like 또는 weighted mix에는 중요하지만 모든 후보 hard blocker는 과하다. |
| `backtest_realism` | transaction cost, net cost curve, sensitivity, turnover, liquidity, net performance, rebalance timing, tax/account, boundary 확인 | 유지. 단, tax/account는 이미 reference 성격이므로 Flow 4 core failure에서 제외한다. |
| `stress_robustness` | stress scenario, rolling, sensitivity, overfit warning 확인 | 유지하되 기본 hard blocker에서 review 중심으로 낮춘다. |
| `selected_route_preflight` | Final Review 저장 전에 막힐 deterministic gap 확인 | category에서 제외. Handoff summary로만 보여준다. |

### Conditional Modules

| Module | Applies When | Audit Decision |
| --- | --- | --- |
| `provider_investability` | ETF-like source | 유지. ETF / holdings / exposure가 있는 후보에만 핵심이다. |
| `leverage_inverse` | leveraged / inverse ticker 포함 | 유지. 조건부 경고 / review가 맞다. |
| `risk_contribution` | weighted mix | 유지. weighted mix에만 필요하다. |
| `component_role_weight` | weighted mix | 유지. weighted mix에만 필요하다. |
| `macro_regime` | tactical source 또는 hedged tactical profile | 축소. macro regime은 조건부 검증으로 유지하고 sentiment risk-on/off overlay는 context로 낮춘다. |

### Reference / Downstream Modules

| Module | Current Role | Audit Decision |
| --- | --- | --- |
| `monitoring_baseline` | Selected Dashboard recheck / monitoring seed | Flow 4 main에서 제외. downstream reference다. |
| `tax_account_scope` | 세금, 계좌, 최소 주문 단위 | Flow 4 main에서 제외. Final Review memo / account planning 영역이다. |

## Evidence Credibility Review

### Strong Core Validations

이 기준들은 Practical Validation에서 계속 핵심으로 유지해야 한다.

| Category | Why Credible | User-Facing Question |
| --- | --- | --- |
| Source contract | 후보 id, 구성, 비중, curve가 같은 source로 묶이지 않으면 이후 검토가 재현되지 않는다. | 같은 후보를 검증하고 있는가? |
| Latest runtime replay | 저장된 과거 snapshot이 아니라 최신 DB 기준으로 다시 실행됐는지 확인한다. | 지금 데이터로도 다시 재현되는가? |
| Benchmark parity | 후보와 비교 기준이 같은 기간 / frequency / coverage여야 성과 비교가 공정하다. | 비교가 공정한가? |
| Price / PIT coverage | 가격 row, replay period, point-in-time boundary가 없으면 look-ahead 위험이 생긴다. | 미래 데이터를 섞지 않았는가? |
| Survivorship / listing | 현재 살아있는 종목만으로 과거를 재구성하면 성과가 과대평가된다. | 사라진 종목을 무시하지 않았는가? |
| Cost / slippage / turnover / liquidity | 실전 운용에서는 비용과 거래 가능성이 성과를 크게 바꾼다. | 백테스트 수익이 실전 비용 후에도 의미 있는가? |
| Execution boundary | Practical Validation이 승인 / 주문 / 자동 리밸런싱을 만들지 않는지 보장한다. | 검증 화면이 실거래 기능으로 오해되지 않는가? |

### Credible But Too Broad As Hard Blockers

이 기준들은 중요하지만 모든 후보를 막는 기준으로 쓰면 과하다.

| Category | Current Issue | Recommended Severity |
| --- | --- | --- |
| Walk-forward / OOS / regime | 있으면 강한 검증이지만 모든 전략과 모든 후보가 항상 준비할 수 있는 최소 조건은 아니다. | 핵심 기간 검증은 review, 명시적으로 요구된 profile만 blocker |
| Stress / robustness | overfit과 충격 구간 확인에 유용하지만 daily replay / stress window가 없다는 이유만으로 모든 후보를 막으면 과하다. | 기본 review, 심각한 missing replay만 blocker |
| Construction risk | ETF look-through / weighted mix에는 중요하지만 단일 factor strategy에는 같은 의미로 적용되지 않는다. | ETF-like / weighted mix 조건부 core, 그 외 review |
| Provider freshness | ETF provider snapshot에는 중요하지만 factor equity나 순수 price strategy에는 과할 수 있다. | ETF-like 조건부 core, 그 외 hidden 또는 reference |
| Macro / regime | tactical strategy에는 의미 있지만 core validation은 아니다. | tactical / hedged profile 조건부 review |
| Sentiment risk-on/off overlay | 시장 배경 설명에는 유용하지만 검증 자체의 pass/fail 근거로는 약하다. | context-only, gate 제외 |

### Duplicated Or Mixed Responsibilities

`validation_efficacy`는 현재 source contract, data trust, runtime replay, benchmark parity, provider freshness, robustness, PIT, survivorship을 한 번 더 읽는다. 이 때문에 같은 문제가 여러 곳에서 blocker처럼 반복될 수 있다.

추천:

- `validation_efficacy`를 `Validation Strength` 성격으로 좁힌다.
- 중복된 source / replay / benchmark / provider / robustness blocker는 해당 원래 category에서만 count한다.
- `Validation Strength`는 walk-forward, OOS, regime, PIT / survivorship guard의 해석 강도를 보여준다.
- PIT / survivorship처럼 bias control에 가까운 항목은 `Data Quality / Bias Control` category에서도 직접 보여준다.

## Flow 4 Information Architecture Finding

현재 Flow 4는 다음처럼 읽힌다.

```text
검증 기준 상세
Final Review로 넘기기 전 확인 기준
먼저 해결 / 통과 / Final Review 확인 / 기술 근거
Source Readiness
Validation Readiness
Final Review Readiness Preview
Conditional Evidence
```

이 구조는 사용자의 질문과 다르다.

사용자는 Flow 4에서 다음을 확인하고 싶다.

- 무엇을 검증했는가?
- 카테고리별로 몇 개가 통과했고 몇 개가 실패했는가?
- 실패한 항목은 무엇인가?
- 그 실패가 왜 중요한가?
- 무엇을 보강해야 하는가?
- Final Review로 넘길 수 있는지는 최종 요약으로만 보면 된다.

따라서 Flow 4는 다음 구조가 맞다.

```text
카테고리별 검증 결과
전체: 통과 N / 보강 필요 N / Final Review 확인 N / 미실행 N

1. Source & Replay
2. Data Quality / Bias Control
3. Comparison Validity
4. Realism / Tradability
5. Validation Strength / Robustness
6. Portfolio Construction
7. Conditional Evidence

Final Review 이동 요약
```

## Recommended Category Model

| Category | Include | Failure Copy Should Say |
| --- | --- | --- |
| Source & Replay | source_integrity, latest_replay | 후보 source 계약과 최신 재검증이 준비됐는지 |
| Data Quality / Bias Control | data coverage price/PIT/universe/survivorship rows | 가격, 기간, 생존편향, look-ahead 근거 중 무엇이 부족한지 |
| Comparison Validity | benchmark_parity | benchmark / comparator가 같은 조건인지 |
| Realism / Tradability | backtest_realism cost/net/turnover/liquidity/rebalance rows | 비용과 거래 현실성이 반영됐는지 |
| Validation Strength / Robustness | walk-forward, OOS, regime, stress, overfit | 검증 강도가 충분한지, 또는 Final Review에서 확인할 부분인지 |
| Portfolio Construction | construction, risk contribution, component role / weight | mix / ETF 구성 위험을 설명할 수 있는지 |
| Conditional Evidence | provider, leverage/inverse, macro | 후보 특성상 추가로 봐야 하는 근거가 있는지 |
| Handoff Summary | selected_route_preflight | 검증 category가 아니라 Final Review 저장 전 막힐 gap 요약 |

## What To Remove Or Demote From Main Flow

제거 또는 기본 숨김:

- Practical Validation 첫 화면의 market sentiment overlay: 이미 제거됨. 유지해야 한다.
- Flow 4 main category 안의 `monitoring_baseline`: Selected Dashboard 참고로 낮춘다.
- Flow 4 main category 안의 `tax_account_scope`: Final Review 판단 메모로 낮춘다.
- Flow 4 main category 안의 `selected_route_preflight`: 검증 category가 아니라 handoff summary다.

조건부 또는 review로 강등:

- sentiment risk-on/off overlay: tactical profile context일 때만 보조 표시, gate 제외
- provider snapshot freshness: ETF-like 후보에만 core
- construction risk: ETF-like / weighted mix에만 core, 단일 후보는 review
- stress / robustness: 기본 review, hard blocker는 replay 자체가 없거나 profile이 명시적으로 요구할 때만
- walk-forward / OOS / regime: 검증 강도 증거로 표시, 기본 hard blocker에서 제외

유지:

- source contract
- latest runtime replay
- benchmark parity
- price DB window
- PIT / look-ahead guard
- survivorship / listing control
- transaction cost / net cost curve
- turnover / liquidity / rebalance timing
- execution / storage boundary

## Decision

Flow 4는 `Final Review로 넘기기 전 확인 기준`을 메인으로 노출하지 않는 것이 맞다.

Flow 4의 메인은 `카테고리별 검증 결과`여야 한다. Final Review 이동 가능성은 Flow 3에서 결론으로 보여주고, Flow 4에서는 하단 또는 우측의 `Final Review 이동 요약`으로만 보조 노출한다.

Practical Validation의 검증 기준은 완전히 갈아엎을 필요는 없다. 다만 gate severity와 화면 정보 구조를 정리해야 한다.

가장 중요한 제품 원칙:

- 검증 category는 사용자의 질문에 답해야 한다.
- gate는 category 결과에서 파생된 route 판단이어야 한다.
- context-only 정보는 검증 실패처럼 보이면 안 된다.
- `NEEDS_INPUT`은 "사용자가 값을 입력하라"가 아니라 "근거가 부족하다"는 의미로 표시해야 한다.
