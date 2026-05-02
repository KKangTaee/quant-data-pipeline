# Phase 14 Family-Specific Threshold Experiment Design First Pass

## 목적

- Phase 14 calibration review를 closeout 가능한 수준으로 묶기 위해,
  **다음 phase에서 실제로 손댈 threshold 실험 후보를 family별로 좁혀서** 남긴다.
- 이번 문서는 threshold를 바로 바꾸는 문서가 아니라,
  **어떤 실험을 어떤 순서로 해야 의미가 있는지**를 고정하는 문서다.

## 이번 문서의 한 줄 결론

- strict annual과 ETF는 같은 방식으로 threshold를 풀면 안 된다.
- 다음 phase 실험은 blanket relaxation이 아니라
  **strict annual은 internal validation core,
  ETF는 operability coverage interpretation**
  으로 따로 나눠서 진행하는 것이 맞다.

## 1. 왜 지금은 설계까지만 하고 멈추는가

현재 evidence는 충분히 쌓였다.

- repeated `hold`의 위치는 이미 family별로 좁혀졌다.
- representative rerun set도 이미 고정했다.
- operator-facing policy threshold와
  internal fixed threshold가 서로 다르다는 점도 분리됐다.

하지만 지금 여기서 바로 값을 바꾸면,

- calibration review
- actual product semantics 변경
- next phase validation

이 한 번에 섞인다.

따라서 Phase 14에서는
**실험 설계까지를 practical closeout 범위**로 보고,
실제 threshold 변경과 rerun execution은 다음 phase workstream으로 넘기는 것이 더 안전하다.

## 2. Strict Annual 실험 설계

### 2-1. 현재 직접 blocker

현재 strict annual repeated `hold`의 1차 blocker는 다음 둘이다.

- `worst rolling excess <= -15%` severe boundary
- `single severe signal -> validation = caution` 규칙

대표 근거:

- `Value` exact-hit hold
- `Quality` capital-discipline near miss

두 케이스 모두
`validation_policy`보다 internal `validation_status`가 먼저 `hold`를 고정한다.

### 2-2. 추천 실험 순서

#### 실험 A. worst-excess severe boundary review

- current:
  - severe `<= -15%`
- 질문:
  - strict annual family에서 severe를 `-20%` 또는 `-25%`까지 내리는 것이 더 현실적인가?

실험 이유:

- 가장 직접적인 current blocker다.
- 이 값을 건드리지 않으면 `validation_policy` 완화 효과가 거의 안 보인다.

#### 실험 B. single-severe escalation rule review

- current:
  - severe signal 하나만 있어도 `validation = caution`
- 질문:
  - strict annual에서는
    `severe 1개 + watch 1개 이상`일 때만 `caution`으로 올리는 것이 더 맞는가?

실험 이유:

- current rule은 quality/value defensive near miss까지 너무 빨리 `hold`로 묶을 가능성이 있다.

#### 실험 C. drawdown-gap fixed threshold review

- current:
  - watch `5%p`
  - severe `10%p`
- 질문:
  - benchmark-relative downside 해석이 strict annual family에 과도하게 불리한가?

실험 이유:

- 1차 blocker는 아니지만, A/B를 건드린 뒤 secondary pressure가 될 수 있다.

### 2-3. 이번 phase에서 아직 하지 않는 것

- `validation_policy`와 `validation_status`를 동시에 완화
- benchmark / liquidity / drawdown policy를 한 번에 모두 변경
- strict annual과 ETF를 같은 severe / caution semantics로 재정렬

## 3. ETF 실험 설계

### 3-1. 현재 직접 blocker

현재 ETF repeated `hold`의 1차 blocker는 다음 셋이다.

- `data_coverage < 0.75 -> caution`
- partial data coverage missing-data semantics
- full candidate pool 기준 coverage denominator

대표 근거:

- practical GTAA는 default contract를 clean하게 통과한다.
- aggressive GTAA는 AUM / spread threshold를 사실상 꺼도
  `partial data coverage` 때문에 계속 `hold`다.

즉 current 핵심은
`Min ETF AUM`이나 `Max Spread`보다
**coverage interpretation**이다.

### 3-2. 추천 실험 순서

#### 실험 A. data-coverage caution boundary review

- current:
  - `< 1.0 -> watch`
  - `< 0.75 -> caution`
- 질문:
  - current ETF family에서 `0.75`가 너무 높은가?
  - `0.50` 또는 `selected asset 기준` 해석이 더 실무적인가?

#### 실험 B. missing-data semantics review

- current:
  - current-date asset profile missing도 operability signal로 바로 올라간다.
- 질문:
  - missing data는 informational watch로 두고,
    actual block은 confirmed fail row에서만 읽는 것이 더 적절한가?

#### 실험 C. denominator review

- current:
  - full candidate ETF 기준 mean
- 질문:
  - 실제 selection top asset만 분모에 넣는 것이 더 실무적인가?

### 3-3. 이번 phase에서 아직 하지 않는 것

- default AUM / spread threshold 즉시 변경
- current snapshot operability를 PIT actual block처럼 재해석
- missing-data 의미를 현재 code에서 바로 완화

## 4. 실험 실행 규칙

다음 phase에서 threshold 실험을 실제로 열 때는 아래 규칙을 유지하는 것이 맞다.

1. representative canonical case를 고정한다.
   - strict annual:
     - `Value` exact-hit hold
     - `Quality` near miss
   - ETF:
     - practical GTAA
     - aggressive GTAA near miss
2. 한 번에 한 축만 바꾼다.
   - policy threshold
   - fixed internal threshold
   - interpretation rule
   중 하나만 바꾼다.
3. rerun 결과는 반드시
   - `promotion`
   - `shortlist`
   - `deployment`
   - relevant policy status
   - representative performance
   를 같이 기록한다.
4. 사용자-facing default 변경은
   별도 sign-off 전에는 하지 않는다.

## 5. closeout 판단

Phase 14 기준으로는

- blocker audit
- calibration review
- family별 실험 후보 분리

까지면 충분히 practical closeout으로 볼 수 있다.

즉 다음 phase에서 할 일은
**threshold를 막연히 풀어보는 것**이 아니라,
이번 문서에 정리된 family-specific experiment를 실제로 실행하는 것이다.

