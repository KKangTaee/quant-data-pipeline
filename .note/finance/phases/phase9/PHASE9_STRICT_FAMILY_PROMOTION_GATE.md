# Phase 9 Strict Family Promotion Gate

## 목적

- strict annual / quarterly family를
  어떤 기준에서 public candidate 또는 research-only로 볼지 문서로 고정한다.

## 현재 family 상태

### strict annual family

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

현재 해석:

- current managed static preset 기준으로는
  가장 앞선 public-candidate family

### strict quarterly family

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

현재 해석:

- `research-only`

## annual strict family gate

strict annual family는
다음 의미에서 public-candidate 지위를 유지할 수 있다.

1. managed static preset 기준 coverage/operator tooling이 정리되어 있다
2. UI single / compare / history / interpretation surface가 연결되어 있다
3. diagnostics/operator workflow가 실사용 가능한 수준으로 정리되어 있다

다만 제한:

- 이 family도 아직
  `historical dynamic PIT universe` contract를 통과한 것은 아니다

따라서:

- public-candidate = 가능
- real-money final validation passed = 아님

으로 구분한다.

## quarterly strict family gate

Phase 9 전체 기간 동안
quarterly family는 `research-only`를 유지한다.

이유:

1. quarterly coverage/operator path는 많이 정리되었지만
   아직 policy와 semantics를 막 고정하는 단계다
2. foreign/non-standard form policy가 current preset coverage에 직접 영향을 준다
3. batch QA가 누적되어야 하고
   annual과의 comparative role도 더 정리되어야 한다

## quarterly family의 future promotion trigger

quarterly family는 아래를 만족할 때만
public-candidate 재검토를 연다.

### 1. coverage policy stability

- strict coverage policy가 확정되어 있고
- exclusion/review bucket이 반복적으로 흔들리지 않는다

### 2. runtime / UX repeatability

- single strategy
- compare
- history rerun / prefill
- interpretation / shadow coverage preview

위 surface가 반복 실행에서 안정적이다.

### 3. default no-misleading rule

- default preset / default dates 기준 실행이
  “사실상 대부분 cash-only” 또는
  “활성 구간이 너무 늦어서 오해를 부르는 path”
가 되지 않는다

### 4. research value clarity

- annual strict family와 비교했을 때
  quarterly family가 단순 duplicate가 아니라
  의미 있는 다른 연구 surface를 제공한다

### 5. next validation contract readiness

- 이후 `historical dynamic PIT universe` mode가 생기면
  quarterly family도 거기서 별도 validation candidate로 다시 평가한다

## practical interpretation

지금 시점에서의 가장 안전한 해석은 이렇다.

- annual strict family:
  - current public-facing research candidate
- quarterly strict family:
  - current research-only prototype family

즉 annual은 “지금 연구 UI에서 가장 앞선 family”이고,
quarterly는 “정책과 coverage가 더 안정화된 뒤 승격을 다시 논의할 family”다.

## recommendation

Phase 9에서는 승격을 서두르지 않는다.

이번 phase의 목적은:

1. policy를 고정하고
2. diagnostics를 governance에 연결하고
3. next validation contract를 정하는 것

이지, quarterly family를 public candidate로 바로 올리는 것이 아니다.

## 한 줄 결론

- `strict annual family` = public-candidate 유지 가능
- `strict quarterly family` = Phase 9 동안 research-only 유지
- final real-money validation은 future `historical dynamic PIT universe`에서 다시 본다
