# Phase 17 Structural Downside Improvement Plan

## 목적

- Phase 16에서 bounded `Top N` / one-factor / minimal overlay refinement가 practical 기준으로 닫힌 뒤,
  다음 질문을 **구조적인 downside improvement**로 올린다.
- 이번 phase의 핵심은
  `Value`와 `Quality + Value`의 strongest practical point를 유지하거나 크게 해치지 않으면서
  더 낮은 `MDD`를 만들 수 있는 구조 레버를 찾는 것이다.

## 왜 지금 이 phase가 필요한가

Phase 16까지 확인한 결론은 분명했다.

- `Value`
  - current best practical point:
    - `Top N = 14 + psr`
    - `28.13% / -24.55%`
    - `real_money_candidate / paper_probation / review_required`
  - lower-MDD near-miss:
    - `Top N = 14 + psr + pfcr`
    - `27.22% / -21.16%`
    - 하지만 `production_candidate / watchlist`
- `Quality + Value`
  - current strongest practical point:
    - `operating_margin + pcr + por + per`
    - `Top N = 10`
    - `31.82% / -26.63%`
    - `real_money_candidate / small_capital_trial / review_required`
  - lower-MDD near-miss:
    - `Top N = 9`
    - `32.21% / -25.61%`
    - 하지만 `production_candidate / watchlist`

즉 지금은:

- bounded tweak을 더 반복하는 문제보다
- **구조를 바꾸면 same gate lower-MDD candidate를 만들 수 있나**

를 보는 단계다.

## 이번 phase의 핵심 질문

### 1. strict annual 구조에서 실제로 열려 있는 downside 레버는 무엇인가

- partial overlay rejection을 `survivor reweighting`으로 볼 것인가
- 일부 rejection을 `cash retention`으로 볼 수 있는가
- strict annual risk-off를 `cash only` 대신 defensive sleeve로 바꿀 수 있는가
- equal-weight top-N 구조를 concentration-aware하게 바꿀 가치가 있는가

### 2. 어떤 레버가 gate tier에 직접 영향을 주는가

- `validation_status`
- `benchmark_policy_status`
- `validation_policy_status`
- `guardrail_policy_status`

이 상태를 해치지 않으면서 `MDD`를 낮출 수 있는 구조만 실제로 의미가 있다.

### 3. weighted portfolio / saved portfolio는 지금 메인 트랙인가

- 이미 살아 있는 strongest candidates를 묶어서 더 낮은 `MDD`를 만드는 것이
  실전형 다음 단계일 수 있다.
- 하지만 현재 weighted portfolio가
  `promotion / shortlist / deployment`
  surface까지 같이 가져오는지 먼저 확인해야 한다.

## 이번 phase에서 먼저 하지 않는 것

- blanket gate relaxation
- 큰 폭의 factor expansion
- 새로운 대형 전략 family 추가

이유:

- 지금 문제는 문턱이 아니라
  **전략 구조가 same gate lower-MDD practical point를 만들 수 있느냐**
  이기 때문이다.

## 추천 실행 순서

1. strict annual 구조 레버 inventory first pass
2. weighted portfolio / saved portfolio fit review first pass
3. 첫 구현 slice 하나 결정
   - partial cash retention
   - defensive sleeve risk-off
   - concentration-aware weighting
4. Value first implementation
5. Quality + Value follow-up

## 이번 phase의 성공 기준

- 단순히 문서를 더 쓰는 것이 아니라,
  **첫 구현 slice를 하나로 좁힐 수 있어야 한다**
- 그 slice가:
  - current code와 맞고
  - `MDD` 개선 논리가 분명하며
  - real-money gate를 너무 쉽게 무너뜨리지 않는 방향이어야 한다

## 관련 문서

- [PHASE16_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_NEXT_PHASE_PREPARATION.md)
- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- [BACKTEST_REFINEMENT_CODE_FLOW_GUIDE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/code_analysis/BACKTEST_REFINEMENT_CODE_FLOW_GUIDE.md)
