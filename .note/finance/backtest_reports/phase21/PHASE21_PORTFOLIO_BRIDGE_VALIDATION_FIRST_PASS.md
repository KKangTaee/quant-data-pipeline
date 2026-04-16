# Phase 21 Portfolio Bridge Validation First Pass

## 목적

- `Phase 21`에서 family별 current anchor를 모두 다시 확인한 뒤,
  그 후보들이 `Compare -> Weighted Portfolio -> Saved Portfolio Replay`
  흐름에서도 재현 가능한지 확인한다.
- 이번 검증은 weighted portfolio를 최적화하는 것이 아니라,
  **portfolio bridge가 다음 phase의 candidate lane으로 넘어갈 만큼 의미 있는지**
  보는 first pass다.

## 이번 validation에서 사용한 bridge frame

- source:
  - `Compare & Portfolio Builder`
  - `Load Recommended Candidates`
- component strategies:
  - `Value Snapshot (Strict Annual)`
  - `Quality Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- period:
  - `2016-01-01 ~ 2026-04-01`
- universe:
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- weighted portfolio:
  - `33 / 33 / 34`
  - `Date Alignment = intersection`
- representative saved portfolio name:
  - `phase21_validation_recommended_equal_weight_v1`

## component 결과

| component | CAGR | MDD | Sharpe | Promotion | Shortlist | Deployment |
|---|---:|---:|---:|---|---|---|
| `Value Snapshot (Strict Annual)` | `28.13%` | `-24.55%` | `1.43` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Quality Snapshot (Strict Annual)` | `26.02%` | `-25.57%` | `1.37` | `real_money_candidate` | `paper_probation` | `review_required` |
| `Quality + Value Snapshot (Strict Annual)` | `31.82%` | `-26.63%` | `1.48` | `real_money_candidate` | `small_capital_trial` | `review_required` |

## weighted portfolio 결과

| label | CAGR | MDD | Sharpe | End Balance | Rows |
|---|---:|---:|---:|---:|---:|
| `phase21_validation_recommended_equal_weight_v1` | `28.66%` | `-25.42%` | `1.51` | `$132,063.56` | `124` |

## saved portfolio replay 검증

같은 saved portfolio context로 다시 replay했을 때:

- `CAGR` 차이:
  - `0.0`
- `MDD` 차이:
  - `0.0`
- `End Balance` 차이:
  - `0.0`
- result rows:
  - initial weighted result: `124`
  - replay result: `124`

즉:

- saved portfolio replay는 이번 representative context에서
  weighted result를 정확히 재현했다.
- `Load Saved Setup Into Compare` / `Replay Saved Portfolio` 흐름은
  Phase 20에서 정리한 operator bridge를
  Phase 21 validation frame에서도 사용할 수 있는 상태로 읽힌다.

## ending contribution share

마지막 월 기준 contribution share는 아래와 같다.

| component | ending contribution share |
|---|---:|
| `Value Snapshot (Strict Annual)` | `31.05%` |
| `Quality Snapshot (Strict Annual)` | `26.22%` |
| `Quality + Value Snapshot (Strict Annual)` | `42.73%` |

해석:

- 입력 weight는 `33 / 33 / 34`였지만,
  끝 시점 contribution은 `Quality + Value`가 더 커졌다.
- 이는 blended family의 성장률이 높았기 때문이며,
  weighted portfolio가 시간이 지나며 component 성과 차이를 자연스럽게 반영한다는 점을 보여준다.

## 실무 해석

이번 representative weighted portfolio는:

- `CAGR = 28.66%`
- `MDD = -25.42%`
- `Sharpe = 1.51`

로 나왔다.

이 결과는 단일 family anchor를 모두 대체하는 새 winner로 읽기보다는,
다음과 같이 읽는 편이 맞다.

1. `Value`보다 CAGR은 조금 높지만 MDD는 더 깊다
2. `Quality + Value`보다 CAGR은 낮지만 MDD는 조금 낮고 Sharpe는 더 높다
3. `Quality`보다 CAGR과 Sharpe가 더 높다
4. saved replay가 정확히 재현되어 operator workflow 신뢰성은 확인됐다

즉:

- 이 bridge는 단순 UI artifact가 아니다.
- 다만 portfolio-level promotion / shortlist semantics가 아직 별도로 정의되어 있지 않으므로,
  지금 당장 single-strategy anchor를 대체하는 production candidate로 보긴 이르다.
- 대신 `Phase 22`에서
  portfolio-level candidate construction을 본격적으로 열 근거는 충분하다.

## 이번 first pass 결론

1. representative compare -> weighted portfolio bridge는 정상 작동했다
2. saved portfolio replay는 동일 summary를 정확히 재현했다
3. weighted result는 Sharpe 개선과 재현성 측면에서 의미가 있다
4. 하지만 portfolio-level promotion semantics는 아직 없으므로,
   `Phase 22`의 메인 설계 대상으로 넘기는 것이 맞다

## 다음 액션

- `Phase 21`을 practical closeout으로 정리한다
- `Phase 22`를 열 때는
  portfolio-level candidate construction / promotion semantics를 우선 질문으로 둔다

## 같이 보면 좋은 문서

- [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md)
- [PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
- [PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
- [PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
