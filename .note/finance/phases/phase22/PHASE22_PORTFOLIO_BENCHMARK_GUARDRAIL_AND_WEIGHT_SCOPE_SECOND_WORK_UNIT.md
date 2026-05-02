# Phase 22 Portfolio Benchmark, Guardrail, And Weight Scope Second Work Unit

## 이 문서는 무엇인가

- 이 문서는 `Phase 22`의 두 번째 작업 단위다.
- 첫 번째 작업에서 portfolio-level candidate의 의미를 정했고,
  두 번째 작업에서는 그 후보를 **무엇과 비교하고, 어떤 위험 기준으로 보수적으로 볼지** 정한다.

## 쉽게 말하면

- 포트폴리오 후보도 benchmark와 guardrail이 필요하다.
- 그런데 단일 전략의 benchmark를 그대로 섞으면 해석이 꼬인다.
- 그래서 `Phase 22`에서는 먼저 아래처럼 단순하고 안전하게 간다.
  - portfolio 후보끼리는 baseline portfolio와 먼저 비교한다.
  - component strategy의 benchmark는 component 해석으로만 유지한다.
  - portfolio-level guardrail은 아직 실제 매매 규칙이 아니라 report-level 경고 기준으로 둔다.

## 왜 지금 필요한가

- `Phase 22` baseline 후보 pack은 만들어졌다.
- 하지만 다음 weight alternative를 돌리기 전에 비교 기준이 있어야 한다.
- 기준 없이 `25/25/50`, `40/40/20` 같은 weight를 돌리면
  어느 조합이 좋아진 것인지, 단순히 다른 결과인 것인지 판단하기 어렵다.

## 핵심 결정

| 영역 | Phase 22 결정 |
|---|---|
| primary portfolio benchmark | `phase22_annual_strict_equal_third_baseline_v1` |
| external reference | `SPY`는 문맥 참고용으로만 둔다 |
| component benchmark | 각 component strategy 내부 해석으로만 유지한다 |
| blended benchmark | 이번 phase에서는 만들지 않는다 |
| portfolio guardrail | 실제 trading rule이 아니라 report-level warning 기준으로 둔다 |
| weight search | broad search가 아니라 해석 가능한 소수 후보만 본다 |

## Benchmark Policy

### 1. Portfolio 후보의 1차 benchmark는 baseline portfolio다

`Phase 22`에서 weight alternative를 볼 때 가장 먼저 비교할 대상은
`SPY`가 아니라 현재 baseline portfolio다.

기준점:

- `phase22_annual_strict_equal_third_baseline_v1`
- component:
  - `Value Snapshot (Strict Annual)`
  - `Quality Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- weight:
  - `[33.33, 33.33, 33.33]`
  - normalized equal-third
- date alignment:
  - `intersection`

이렇게 하는 이유는 간단하다.

- 지금 질문은 "이 포트폴리오가 SPY보다 나은가"가 아니다.
- 지금 질문은 "equal-third baseline보다 더 나은 portfolio construction이 있는가"다.

### 2. SPY는 참고 지표이지, Phase 22의 primary gate가 아니다

`SPY`는 broad market reference로 계속 의미가 있다.

하지만 `Phase 22`에서 바로 primary gate로 쓰면 애매해진다.

- component마다 benchmark contract가 다르다.
- `Quality`는 `LQD`를 benchmark ticker로 쓴다.
- `Quality + Value`는 `Candidate Universe Equal-Weight` contract를 쓴다.
- weighted portfolio는 component 결과를 섞은 composite라서 단일 전략의 benchmark contract와 1:1로 맞지 않는다.

따라서 이번 phase에서는 `SPY`를 참고용 market context로만 둔다.

### 3. Component benchmark는 component 안에서만 해석한다

각 component strategy의 benchmark / guardrail 상태는 버리지 않는다.

다만 portfolio-level report에서는 이렇게 읽는다.

- `Value`의 `SPY` benchmark:
  - Value component가 자체 기준에서 의미 있는지 확인하는 정보
- `Quality`의 `LQD` benchmark:
  - Quality component가 현재 practical anchor인지 확인하는 정보
- `Quality + Value`의 `Candidate Universe Equal-Weight`:
  - blended component가 같은 후보군 equal-weight보다 의미 있는 selection인지 확인하는 정보

즉 component benchmark는 portfolio 후보의 재료 품질을 보는 정보이지,
portfolio-level benchmark 자체는 아니다.

### 4. Blended benchmark는 이번 phase에서 만들지 않는다

나중에는 아래 같은 blended benchmark가 필요할 수 있다.

- component benchmark를 component weight대로 섞은 blended benchmark
- portfolio component universe 전체를 equal-weight한 synthetic benchmark
- SPY / BIL / AGG 같은 외부 reference basket

하지만 이번 phase에서 이것까지 만들면 범위가 커진다.

따라서 `Phase 22`에서는:

- primary benchmark:
  - equal-third baseline portfolio
- context benchmark:
  - SPY
- later option:
  - blended portfolio benchmark

로 정리한다.

## Guardrail Policy

### 1. Phase 22 guardrail은 report-level warning이다

이번 phase에서 portfolio-level guardrail은 실제 trading rule이 아니다.

즉:

- 특정 조건이 나오면 자동으로 현금화하는 규칙이 아니다.
- 특정 조건이 나오면 report에서 `watch`, `caution`, `not_deployment_ready`로 보수적으로 읽는 기준이다.

### 2. Hard blocker

아래 중 하나라도 있으면 portfolio-level candidate로 보지 않는다.

| 조건 | 해석 |
|---|---|
| saved replay가 재현되지 않음 | 후보가 아니라 일회성 결과 |
| component source가 불명확함 | 후보 출처 추적 불가 |
| date alignment가 baseline과 다름 | 같은 frame 비교가 아님 |
| component 중 current anchor가 아닌 weaker-gate 후보가 섞였는데 설명이 없음 | portfolio가 약한 후보를 숨기는 구조일 수 있음 |

### 3. Watch / Caution 기준

아래는 바로 탈락은 아니지만 보수적으로 읽는다.

| 조건 | 해석 |
|---|---|
| MDD가 baseline보다 2~3%p 이상 깊어짐 | 수익 개선이 있어도 downside tradeoff 확인 필요 |
| Sharpe가 baseline보다 낮아짐 | risk-adjusted surface 약화 |
| 한 component contribution이 장기적으로 50%를 넘음 | 사실상 특정 component tilt가 될 수 있음 |
| CAGR만 좋아지고 MDD / Sharpe / replay 근거가 약함 | raw return chase 위험 |
| annual strict family끼리만 섞음 | 분산 효과가 제한적일 수 있음 |

### 4. Maintain 기준

아래 조건을 만족하면 portfolio baseline 또는 alternative를 유지 후보로 볼 수 있다.

- saved replay가 재현된다.
- 같은 validation frame에서 비교된다.
- baseline보다 tradeoff가 설명 가능하다.
- component status가 약해지지 않는다.
- report에서 왜 유지하는지와 다음 action이 분명하다.

## Weight Alternative Scope

### 이번 phase에서 볼 후보

`Phase 22`에서는 weight를 넓게 탐색하지 않는다.

다음 두 가지 대안만 먼저 본다.

| 후보 | weight | 왜 보는가 | 기대 효과 | 주요 위험 |
|---|---:|---|---|---|
| `quality_value_tilt` | `25 / 25 / 50` | strongest blended anchor의 기여를 의도적으로 키운다 | CAGR 또는 Sharpe 개선 가능성 | `Quality + Value` 편중 |
| `value_quality_defensive_tilt` | `40 / 40 / 20` | blended anchor 편중을 줄이고 Value / Quality를 더 크게 둔다 | MDD 또는 contribution 균형 개선 가능성 | CAGR 저하 가능성 |

### 이번 phase에서 아직 보지 않는 후보

아래는 나중 option으로 둔다.

- broad brute-force weight search
- volatility targeting
- risk parity
- monthly dynamic allocation
- GTAA / treasury / defensive strategy 추가
- portfolio-level blended benchmark 구현

이것들은 의미가 있지만,
지금 다 열면 Phase 22가 너무 커진다.

## 다음 validation report 기준

다음 report는 아래 3개를 같은 표에서 비교한다.

1. `phase22_annual_strict_equal_third_baseline_v1`
2. `phase22_annual_strict_quality_value_tilt_v1`
3. `phase22_annual_strict_value_quality_defensive_tilt_v1`

각 후보 report에는 최소한 아래 항목을 남긴다.

- component strategy 목록
- source / saved portfolio or run source
- validation period
- universe frame
- weight
- date alignment
- CAGR / MDD / Sharpe / End Balance
- baseline 대비 차이
- contribution concentration
- saved replay 가능 여부
- maintain / replace / defer 판단

## TODO 반영

- `portfolio-level benchmark / guardrail interpretation`은 이 문서 기준으로 완료 처리한다.
- 다음 실제 작업은 두 weight alternative를 같은 frame에서 rerun하고,
  baseline 대비 유지 / 교체 / 보류 판단을 report로 남기는 것이다.

## 한 줄 정리

- `Phase 22` portfolio 후보의 1차 benchmark는 `SPY`가 아니라 equal-third baseline이고,
  guardrail은 아직 trading rule이 아니라 report-level warning이며,
  다음 weight alternative는 `25/25/50`과 `40/40/20` 두 개로 좁혀 본다.
