# Phase 12 Strict Annual Broader Benchmark Contract Later Pass

## 목적

strict annual family의 benchmark 비교를
단순 `SPY` 같은 단일 ticker 비교에서 한 단계 더 넓혀,
같은 후보 universe를 기준으로도 읽을 수 있게 만든다.

## 쉽게 말하면

이전까지는:

- benchmark를 `SPY` 같은 ticker 하나로만 잡았다.

이번에는 여기에 아래 contract를 추가했다.

- `Ticker Benchmark`
- `Candidate Universe Equal-Weight`

즉 이제는
"이 전략이 SPY보다 어땠는가?"뿐 아니라
"같은 후보 universe를 그냥 단순 균등 보유했을 때보다도 나았는가?"
를 같이 볼 수 있다.

## 추가된 입력

strict annual 3종에 아래 입력이 추가되었다.

- `Benchmark Contract`
  - `Ticker Benchmark`
  - `Candidate Universe Equal-Weight`
- `Benchmark Ticker`
  - ticker benchmark 또는 guardrail 기준 ticker

대상 전략:

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

## 용어 설명

### `Ticker Benchmark`

- 기본 설명:
  - `SPY` 같은 ETF 1개를 기준선으로 두는 방식이다.
- 왜 사용되는지:
  - 가장 익숙하고 해석이 쉬운 benchmark 비교다.
- 예시 / 필요 상황:
  - 전략이 S&P 500 ETF보다 나은지 직접 보고 싶을 때 사용한다.

### `Candidate Universe Equal-Weight`

- 기본 설명:
  - 전략이 보는 같은 후보 universe를 단순히 균등 보유했을 때의 기준선이다.
- 왜 사용되는지:
  - benchmark를 broad index 하나로만 보면,
    전략 자체의 선별 효과보다 시장 스타일 차이만 크게 보일 수 있다.
  - 같은 후보군을 기준으로 두면
    "그냥 후보군을 들고 있는 것"보다 전략 선별이 실제로 도움이 되는지 더 직접 볼 수 있다.
- 예시 / 필요 상황:
  - annual strict universe 안에서 quality/value ranking이
    정말 alpha를 만드는지 보고 싶을 때 적합하다.

## 구현 내용

runtime은 now 아래 값을 meta에 남긴다.

- `benchmark_contract`
- `benchmark_label`
- `benchmark_symbol_count`
- `benchmark_eligible_symbol_count`

그리고 benchmark overlay는 contract에 따라 달라진다.

### 1. `Ticker Benchmark`

- 기존처럼 단일 ticker의 DB price history를 기준으로 benchmark 곡선을 만든다.

### 2. `Candidate Universe Equal-Weight`

- 현재 strict annual candidate universe의 DB price history를 불러온다.
- 첫 aligned date에서 가격이 있는 종목만 골라
  단순 equal-weight buy-and-hold benchmark를 만든다.
- 이 first pass는
  dynamic monthly membership까지 반영하는 완전한 PIT benchmark는 아니다.
  대신 "같은 후보군을 단순 보유했을 때"라는 실용적 기준선을 추가한다.

## UI / History 반영 범위

single / compare / history 모두 같은 contract를 따른다.

- single `Real-Money`
  - `Benchmark Contract`
  - `Benchmark Universe`
  - `Benchmark Eligible`
- single `Execution Context`
  - benchmark contract / counts
- compare `Strategy Highlights`
  - `Benchmark Contract`
- history / `Load Into Form`
  - benchmark contract 복원

## 현재 한계

- underperformance guardrail actual-rule은 여전히 `Benchmark Ticker` 기준이다.
  - 이번 pass는 validation / promotion / benchmark surface를 넓힌 작업이다.
- `Candidate Universe Equal-Weight`는 first pass라서,
  candidate universe를 월별로 다시 구성하는 완전한 dynamic constituent benchmark는 아니다.
- 그래도 실전 해석에서는
  single ticker benchmark만 보던 것보다 한 단계 더 납득 가능한 비교축이 된다.

## 의미

이번 작업으로 strict annual family는

- broad ETF 1개와 비교하는 관점
- 같은 후보 universe를 단순 보유하는 관점

두 가지 benchmark contract로 읽을 수 있게 되었다.

즉 실전 승격 판단에서
"그냥 SPY보다 어땠다" 수준을 넘어서
"같은 investable menu 안에서도 selection이 의미 있었나"
를 같이 볼 수 있게 된 것이다.
