# Phase 17 Structural Lever Inventory First Pass

## 목적

현재 strict annual family에서
`MDD`를 더 낮추면서도 실전형 gate를 지키기 위해
어떤 구조 레버를 실제로 사용할 수 있는지
current code 기준으로 정리한다.

이번 문서는
새 전략 아이디어를 넓게 브레인스토밍하는 문서가 아니라,
**지금 코드에 맞는 다음 구현 후보를 고르는 문서**다.

## current code에서 이미 구현된 구조

### 1. top-N equal-weight holding

strict annual family는 현재:

- rebalance 시점 snapshot에서 상위 `N` 종목을 고르고
- 최종 생존 종목에 대해
  `base_balance / len(held_tickers)`로 다시 100% 균등배분한다

즉 현재 기본 구조는
**equal-weight top-N stock basket**이다.

근거:
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L1375)
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L1381)

### 2. overlay / guardrail risk-off는 full cash

현재 strict annual family는:

- market regime `risk_off`
- underperformance guardrail `risk_off`
- drawdown guardrail `risk_off`

가 걸리면 selection 결과를 비워서
다음 구간을 현금으로 보낸다.

즉:
- 전체가 막히면 `cash`
- 일부만 탈락하면 survivor reweighting

구조다.

근거:
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L1363)
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L1367)
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L1371)

### 3. partial overlay rejection은 survivor reweighting

trend filter가 일부 종목만 탈락시켜도,
현재 strict annual은 남은 종목을 다시 균등배분한다.

즉 현재는
**partial rejection -> partial cash retention**이 아니라
**partial rejection -> survivor reweighting**
이다.

관련 해석 문서:
- [OVERLAY_CASH_POLICY_RESEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/OVERLAY_CASH_POLICY_RESEARCH.md)

### 4. benchmark contract는 gate에 큰 영향을 주지만, 수익률 구조 레버는 아니다

runtime의 `promotion / shortlist`는
`validation_status`, `benchmark_policy_status`, `validation_policy_status`,
`guardrail_policy_status` 등으로 결정된다.

즉 `Candidate Universe Equal-Weight` 같은 benchmark contract는
shortlist tier에는 큰 영향을 주지만,
그 자체가 전략 return path를 방어적으로 바꾸는 구조 레버는 아니다.

근거:
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py#L844)
- [backtest.py](/Users/taeho/Project/quant-data-pipeline/app/web/runtime/backtest.py#L936)

## 지금 코드에서 보이는 한계

### 1. strict annual에는 defensive sleeve risk-off가 없다

ETF 쪽은 `risk_off_mode`와 defensive bond 선호 구조가 있지만,
strict annual family는 risk-off 시
사실상 `cash only`다.

즉 strict annual에서
`cash drag`를 줄이는 방어 구조는 아직 얇다.

근거:
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L129)
- [strategy.py](/Users/taeho/Project/quant-data-pipeline/finance/strategy.py#L172)

### 2. concentration을 조절하는 방법이 사실상 Top N밖에 없다

지금 strict annual은:

- `Top N`
- factor set
- overlay on/off

정도로 concentration을 바꾼다.

하지만:

- tiered weight
- capped equal-weight
- rank-based tapering

같은 concentration-aware 구조는 없다.

즉 more defensive concentration control을 보려면
구조 추가가 필요하다.

### 3. lower-MDD near-miss가 gate에서 미끄러질 때 구출 수단이 제한적이다

현재 lower-MDD near-miss는 보통:

- `validation = watch`
- `rolling = watch/caution`

으로 내려가면서
`production_candidate / watchlist`에 머문다.

즉 단순히 방어적으로 만들기만 하면
gate가 함께 내려갈 가능성이 높고,
이를 상쇄할 구조 레버가 현재는 많지 않다.

## Phase 17에서 가장 유력한 구조 레버

### 1. partial cash retention contract

아이디어:

- partial overlay rejection이 생길 때
  남은 종목에 100% 재배분하지 않고
  탈락한 slot만큼 현금을 남기는 구조

왜 유력한가:

- current strict annual architecture와 가장 가깝다
- `MDD`를 직접적으로 낮출 가능성이 있다
- 완전한 새 전략 family를 만들지 않고도 실험할 수 있다

주의:

- 수익률 희생 가능성
- factor basket의 full-investment 성격이 약해질 수 있음

### 2. defensive sleeve risk-off contract

아이디어:

- strict annual risk-off를 `cash only` 대신
  `BIL`, `SHY`, `LQD` 같은 defensive sleeve로 돌리는 구조

왜 유력한가:

- current `cash drag`를 줄일 수 있다
- 실전형 해석에서도 더 operator-friendly할 수 있다

주의:

- strict annual family에 새 자산 sleeve가 들어오므로
  철학과 문서 설명이 더 복잡해진다

### 3. concentration-aware weighting

아이디어:

- equal-weight top-N을 유지하되
  상위 rank tapering이나 capped weight 구조를 붙인다

왜 유력한가:

- `Top N`만 바꾸는 것보다 부드럽게 concentration을 조절할 수 있다

주의:

- 현재 strict annual family에 없는 weighting 체계라
  구현/설명/검증 범위가 더 커진다

## family별 추천 우선순위

### Value

1. partial cash retention
2. defensive sleeve risk-off
3. concentration-aware weighting

이유:

- `+ pfcr` near-miss는 이미 `MDD`가 크게 개선된 상태라
  cash-retention 계열 구조가 제일 직접적으로 맞닿아 있다

### Quality + Value

1. partial cash retention
2. concentration-aware weighting
3. defensive sleeve risk-off

이유:

- strongest point가 이미 강해서,
  먼저 partial rejection과 concentration 조절로 `MDD`를 조금씩 줄이는 쪽이 자연스럽다

## first implementation slice 추천

현재 추천은:

- **strict annual partial cash retention contract**

이유:

- current architecture와 가장 가깝다
- `Value`와 `Quality + Value` 둘 다에 공통으로 적용 가능하다
- lower-MDD same-gate rescue를 볼 때
  가장 직접적인 first slice다

## 한 줄 결론

Phase 17에서 가장 먼저 구현 후보로 볼 것은:

- `partial cash retention`

그 다음은:

- `defensive sleeve risk-off`

이고,
candidate consolidation은 별도 보조 트랙으로 두는 것이 자연스럽다.
