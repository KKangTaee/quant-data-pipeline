# Economic Cycle Next-Transition Forecast Feasibility Design

Status: User-approved target; feasibility `NO_GO_DATA`
Last Updated: 2026-08-12

## 목적

이 연구는 `몇 개월 뒤 어느 국면인가`를 맞히는 고정시점 분류가 아니다. 현재까지
알려진 정보로 현재 국면이 얼마나 불안정해졌는지와 **다음으로 확인될 국면이 무엇일
가능성이 높은지**를 과거 전환 사건으로 검증할 수 있는지 판정한다.

제품이 답해야 하는 질문은 세 가지다.

1. 현재 상대 성장순환 국면은 무엇인가?
2. 현재 국면에서 다른 국면으로 전환할 신호는 얼마나 강한가?
3. 전환된다면 네 국면 중 어디가 가장 유력하며, 어떤 조건이 주경로와 대안 경로를
   강화하거나 약화하는가?

feasibility와 publication gate를 통과하기 전에는 forecast DB serving schema,
Overview 확률 payload 또는 React 확률 UI를 만들지 않는다.

## 승인된 제품 의도

- 현재 국면은 기존 PIT observed-state의 level / momentum / breadth 근거로 별도
  진단한다.
- 고정 순환 순서는 시각적 참고일 뿐 destination 후보를 제한하지 않는다.
- 다음 전환 후보는 `recovery / expansion / slowdown / contraction`을 모두 비교한다.
- 정확한 전환 월을 약속하지 않는다.
- `전환 임박도`와 `다음 국면별 확률`을 분리한다.
- 기본 전망과 금리·신용·고용·물가·생산 조건 변화에 따른 확률 변화를 함께 제시한다.
- 확률과 모델 신뢰도를 분리한다.
- feasibility가 실패하면 확률 UI를 만들지 않고 필요한 추가 데이터 또는 구조적
  한계를 명시한다.
- `자산별 확인 포인트` 계산, payload, 카드 디자인과 순서는 변경하지 않는다.

## 기존 명세 반려

2026-08-11 초안의 아래 target은 사용자가 원한 기능이 아니므로 폐기한다.

```text
P(phase at t+3 months)
P(phase at t+6 months)
```

과거 1·3·6개월은 입력 변화량을 만드는 관찰 창으로 사용할 수 있지만, 출력의 예측
시점으로 고정하지 않는다.

## 예측 계약

### 다음 국면 목적지

확률 target은 다음과 같다.

```text
P(next confirmed phase = destination | information known at origin)
```

- `next confirmed phase`는 현재 확인 국면과 다른 국면이 연속 두 번의 정식 월말
  관측에서 유지된 첫 사건이다.
- 후보는 현재 국면을 포함한 네 phase vocabulary를 사용하되, destination은 현재
  확인 국면과 달라야 한다.
- 비인접 전환도 허용한다.
- 네 destination 확률은 유한하고 음수가 아니며 합이 1이어야 한다.
- 같은 전환 사건 전의 여러 월을 독립 전환 사례로 세지 않는다.

두 번 연속 확인은 월별 경계 잡음을 줄이기 위한 사건 정의다. 기존 fixed adjacent
monitor의 `회복→확장→둔화→위축→회복` 순서나 세 조건을 재사용하지 않는다.

### 전환 임박도

다음 국면 목적지만으로는 전환이 가까운지 알 수 없다. 따라서 별도 event probability를
둔다.

```text
P(any confirmed phase transition within the next 3 official monthly releases
  | information known at origin)
```

이 3회 창은 `3개월 뒤 국면`을 예측하는 horizon이 아니다. 전환 사건이 가까운지를
검증 가능한 binary event로 정의하기 위한 짧은 관찰 창이다. 제품에서는 calibrated
probability를 그대로 과장하지 않고 사전 고정 threshold로 `낮음 / 중간 / 높음`을
표시한다.

- 낮음: 현재 국면 유지 근거가 우세하고 3회 내 전환 사건 근거가 약함
- 중간: 일부 전환 신호가 있으나 지표·지속성이 엇갈림
- 높음: 여러 독립 signal family가 같은 방향을 지지해 3회 내 전환 위험이 상승

`낮음`은 달력상 전환이 멀다는 확정 예측이 아니다.

### 조건부 시나리오

시나리오는 generic 문구가 아니라 동일 모델 입력에 사전 정의한 충격을 적용했을 때
확률이 얼마나 변하는지 계산한다.

- rates / curve
- credit / financial conditions
- activity
- labor / income
- inflation / policy

각 시나리오는 `변경한 변수`, `현재값`, `충격 규칙`, `destination probability delta`,
`imminence delta`를 남긴다. 모델 밖에서 임의로 “금리가 오르면 위축” 같은 문장을
만들지 않는다.

## Information-Date 계약

각 origin의 input은 그 시점까지 실제로 알 수 있었던 값만 사용한다.

```text
official vintage / realtime interval / released-at evidence
  -> origin-specific transform
  -> expanding normalization fitted through origin only
  -> current-state and leading feature row
```

- revised macro history를 과거 origin의 predictor로 소급하지 않는다.
- revision이 없는 market series도 origin 이후 관측을 사용하지 않는다.
- target outcome은 이후 두 번 연속 확인된 phase 사건으로 정하되, predictor와
  normalization에는 target 이후 정보를 쓰지 않는다.
- source, observation date, known-at date, transform version을 추적한다.

## 사건 추출 규칙

1. 첫 usable phase를 초기 anchor로 둔다.
2. anchor와 다른 phase가 나타나면 candidate를 시작한다.
3. 같은 candidate가 두 번 연속 usable 월말 관측에서 유지되면 전환 사건을 확정한다.
4. candidate가 anchor로 되돌아오거나 다른 candidate로 바뀌면 streak를 초기화한다.
5. unavailable 월은 candidate streak를 끊는다.
6. 확정 destination은 새 anchor가 되며 이후 사건을 독립적으로 센다.

각 사건에는 `from_phase`, `to_phase`, `candidate_started_at`, `confirmed_at`,
`releases_to_confirmation`을 저장한다.

## 1차 표본 Gate

이 gate는 모델 공개 기준이 아니라 **모델 실험을 시작할 최소 조건**이다. 아래를 모두
충족하지 못하면 candidate model fitting 전에 `NO_GO_DATA`로 중단한다.

- usable PIT monthly origins: 180개 이상
- independent confirmed transitions: 48개 이상
- destination phase별 event: 8개 이상
- origin phase별 event: 8개 이상
- 마지막 25% chronological holdout event: 12개 이상
- holdout destination phase별 event: 2개 이상

월별 origin을 반복 표본으로 세어 사건 부족을 숨기지 않는다.

## 모델 후보와 Baseline

표본 gate를 통과한 뒤에만 아래를 비교한다.

### Destination model

- L2 regularized multinomial logistic model
- current phase, level, momentum, breadth, duration, recent 1·3·6-release deltas
- rates/curve, credit/financial conditions, activity, labor, inflation/policy family

### Imminence model

- L2 regularized binary logistic model
- target: 다음 3회 정식 월말 발표 안의 confirmed transition event

### Baselines

- expanding unconditional destination frequency
- current phase별 expanding destination frequency
- no-transition base rate for imminence

historical analog은 설명 근거로만 사용하며 확률 authority가 아니다.

## 검증 계약

- chronological expanding-origin validation
- 같은 transition episode에 속한 origin을 train과 validation에 나누지 않는 episode block
- candidate/hyperparameter/calibration 고정 후 마지막 holdout 1회 평가
- destination: log loss, multiclass Brier, classwise calibration, top-1 accuracy
- imminence: log loss, Brier, calibration slope/intercept, precision/recall
- 모든 candidate는 strongest baseline보다 proper score가 우수해야 한다.
- COVID 포함/제외, revision sensitivity, feature-family ablation을 stress test한다.

확률 합과 calibration만 통과해도 공개하지 않는다. baseline skill과 episode support를
함께 통과해야 한다.

## UI 공개 계약

publication gate를 통과한 뒤 별도 UI 설계를 승인받는다. 예상 정보 구조는 아래다.

```text
현재 국면
  -> 전환 임박도: 낮음 / 중간 / 높음
  -> 가장 유력한 다음 국면과 대안 국면 확률
  -> 주경로를 강화하는 조건
  -> 대안 경로를 강화하는 조건
  -> 확률 근거와 모델 신뢰도
```

고정 순환 지도는 phase vocabulary 설명용이며, 강조 화살표는 분석된 primary destination을
사용한다. 검증 실패·stale source·모델 unavailable을 같은 `자료 부족` 문구로 합치지
않는다.

## 중단 조건

다음 중 하나면 제품 확률 개발을 중단한다.

- 1차 표본 gate 미달
- strict PIT input 역사가 짧아 holdout class support를 만들 수 없음
- strongest baseline을 proper score에서 이기지 못함
- 확률 calibration 실패
- 결과가 한 번의 shock episode에 의존
- current runtime에서 같은 feature contract를 materialize할 수 없음

중단 시 `현재 국면 + 관측 근거`는 유지한다. 검증되지 않은 수치를 감추기 위해
fallback probability나 hardcoded scenario 문구를 만들지 않는다.

## 현재 범위

이번 단계는 target·event·표본 gate를 코드로 고정하고 실제 PIT 데이터에 적용하는
feasibility audit까지만 수행한다. production DB schema, refresh job, service payload,
React UI와 자산별 확인 포인트는 변경하지 않는다.
