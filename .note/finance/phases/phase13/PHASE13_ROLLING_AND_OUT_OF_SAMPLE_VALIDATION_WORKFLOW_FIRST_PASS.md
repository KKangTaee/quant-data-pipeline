# Phase 13 Rolling And Out-Of-Sample Validation Workflow First Pass

## 목적

- Phase 13 shortlist / probation 상태 위에,
  최근 시장 구간에서 전략이 여전히 버티는지와
  split-period 기준으로 후반부 성과가 무너졌는지를 같이 읽는
  review layer를 추가한다.

쉬운 뜻:

- 전체 백테스트 결과만 좋다고 바로 믿지 않고,
  최근 구간과 후반부 구간도 따로 본다.
- 이번 pass는 전략 규칙을 더 바꾸는 것이 아니라,
  **현재 전략을 더 보수적으로 해석하기 위한 review surface**다.

## 이번에 추가된 meta

- `rolling_review_status`
- `rolling_review_window_label`
- `rolling_review_recent_excess_return`
- `rolling_review_previous_excess_return`
- `rolling_review_recent_drawdown_gap`
- `rolling_review_rationale`
- `out_of_sample_review_status`
- `out_of_sample_in_sample_excess_return`
- `out_of_sample_out_sample_excess_return`
- `out_of_sample_excess_change`
- `out_of_sample_review_rationale`

## rolling review 의미

- benchmark와 정렬된 결과를 기준으로 최근 `12M` 또는 `252D` window를 본다.
- 최근 window에서 전략이 benchmark보다 약하면
  `watch` 또는 `caution`으로 읽는다.
- 이전 window가 있을 경우, 최근 window가 직전 window보다 크게 약해졌는지도 같이 본다.

### rolling review 상태

- `normal`
  - 최근 구간이 큰 문제 없이 유지된다
- `watch`
  - 최근 구간 약세나 최근 drawdown gap이 보여서 보수적 해석이 필요하다
- `caution`
  - 최근 구간 underperformance나 drawdown 악화가 꽤 크다
- `unavailable`
  - 최근 review window를 볼 수 있을 만큼 데이터가 충분하지 않다

## out-of-sample review 의미

- benchmark와 정렬된 전체 기간을 앞/뒤 절반으로 나눠서 본다.
- 후반부(out-of-sample로 읽는 구간)가
  앞 절반보다 너무 약해졌는지 확인한다.

### out-of-sample review 상태

- `normal`
  - 후반부가 크게 무너지지 않았다
- `watch`
  - 후반부가 약해졌지만 아직 즉시 제외 수준은 아니다
- `caution`
  - 후반부 underperformance 또는 drawdown gap 악화가 꽤 크다
- `unavailable`
  - split-period review를 보기엔 데이터가 부족하다

## monitoring과의 관계

- 이번 pass는 `promotion_decision`을 직접 다시 계산하지 않는다.
- 대신 `probation / monitoring` contract가
  `rolling_review_status`, `out_of_sample_review_status`를 같이 읽어서
  `heightened_review` 또는 `breach_watch` 쪽으로 더 보수적으로 해석할 수 있게 한다.

## UI surface

- single strategy `Real-Money`
- `Execution Context`
- compare `Strategy Highlights`
- compare meta table

## out-of-sample review checklist 초안

1. 전체 기간 숫자만 보지 말고 `Rolling Review`와 `OOS Review`를 같이 본다
2. `Rolling Review = caution`이면 current regime robustness가 약한 것으로 본다
3. `OOS Review = caution`이면 후반부 구간 일관성이 약한 것으로 본다
4. `watch`가 여러 개 겹치면 paper probation에서는 유지하되 비중 확대는 보류한다
5. `unavailable`이면 short sample이라는 뜻이므로 실전 해석을 더 보수적으로 한다

## 현재 경계

- 이번 pass는 read-only review layer다.
- rolling / out-of-sample 결과를 아직 actual rebalance rule로 쓰지는 않는다.
- 별도 monthly review note 저장이나 rolling window batch runner는 아직 later pass다.

## 검증

- `py_compile`
- page/runtime import smoke
- helper-level smoke for:
  - recent window review
  - split-period review
- DB-backed smoke:
  - strict annual
  - ETF strategy

## 해석

- Phase 13은 이제 shortlist / probation / monitoring뿐 아니라,
  **recent regime와 split-period consistency까지 같이 읽는 deployment-readiness workflow**를 갖게 되었다.
- 다만 실제 전략 규칙을 더 강화하는 단계는 아직 아니고,
  현재는 "비중 확대 전에 한 번 더 확인해야 하는 review layer"로 읽는 것이 맞다.
