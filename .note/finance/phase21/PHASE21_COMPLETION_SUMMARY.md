# Phase 21 Completion Summary

## 이 문서는 무엇인가
- 이 문서는 `Phase 21`이 실제로 끝난 뒤,
  무엇을 검증했고 어떤 candidate decision이 남았는지 정리하는 closeout 문서다.

## 현재 상태
- `practical_closeout / manual_validation_pending`

## 쉽게 말하면

- `Phase 21`에서는 새 기능을 더 붙이기보다,
  지금까지 모아 둔 annual strict 후보를 같은 기준으로 다시 돌렸다.
- 그리고 마지막에는
  `Compare -> Weighted Portfolio -> Saved Portfolio Replay`
  흐름까지 확인했다.
- 결과적으로 current anchor들은 모두 유지됐고,
  portfolio bridge는 다음 phase에서 더 본격적으로 다룰 가치가 있다는 판단이 남았다.

## 무엇을 검증했나

- `Value`:
  - current anchor `Top N = 14 + psr`
  - lower-MDD alternative `+ pfcr`
- `Quality`:
  - current anchor `LQD + trend on + Top N 12`
  - cleaner alternative `SPY + trend on + Top N 12`
- `Quality + Value`:
  - current strongest point `Top N 10`
  - lower-MDD alternative `Top N 9`
- portfolio bridge:
  - `Load Recommended Candidates`
  - `33 / 33 / 34` weighted portfolio
  - saved portfolio replay

## 핵심 결과

| 대상 | 결론 |
|---|---|
| `Value` | current anchor 유지. `+ pfcr`는 lower-MDD지만 weaker-gate |
| `Quality` | current anchor 유지. `SPY` alternative는 comparison-only |
| `Quality + Value` | current strongest point 유지. `Top N 9`는 숫자는 좋지만 weaker-gate |
| portfolio bridge | weighted result와 saved replay 재현성 확인. Phase 22 설계 대상으로 적합 |

## portfolio bridge 결과

- representative weighted portfolio:
  - `33 / 33 / 34`
  - `Date Alignment = intersection`
  - `CAGR = 28.66%`
  - `MDD = -25.42%`
  - `Sharpe = 1.51`
- saved portfolio replay:
  - `CAGR`, `MDD`, `End Balance` 모두 exact match

## 왜 중요한가

- 단일 family anchor는 이미 각자 의미가 있지만,
  실제 운용에서는 후보들을 묶어 portfolio-level로 볼 가능성이 크다.
- 이번 결과는 weighted portfolio가 단순 UI 기능이 아니라,
  재현 가능한 candidate bridge로 읽을 수 있음을 보여준다.
- 다만 아직 portfolio-level promotion / shortlist 기준은 따로 없기 때문에,
  다음 phase에서 그 기준을 설계해야 한다.

## 다음 방향

- `Phase 22`는 portfolio-level candidate construction이 가장 자연스럽다.
- 핵심 질문은:
  - weighted portfolio를 어떤 기준으로 후보화할지
  - portfolio-level promotion / shortlist / deployment semantics를 어떻게 만들지
  - single-strategy anchor와 portfolio-level candidate를 어떻게 비교할지
  가 된다.

## 한 줄 정리
- `Phase 21`은 annual strict family anchor를 다시 고정하고,
  portfolio bridge를 다음 phase의 메인 설계 대상으로 넘길 만큼의 근거를 만든 phase다.
