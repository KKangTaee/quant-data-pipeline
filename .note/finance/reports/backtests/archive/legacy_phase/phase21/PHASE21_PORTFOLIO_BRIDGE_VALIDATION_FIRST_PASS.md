# Phase 21 Portfolio Bridge Validation Report

## 이 문서는 무엇인가

이 문서는 `Phase 21`에서 확인한 **portfolio bridge 검증 결과**를 정리한 문서다.

쉽게 말하면, 이번 문서는 "이 3개 전략을 섞은 포트폴리오가 최종 투자 후보로 가장 좋다"를 주장하는 문서가 아니다.

목적은 더 좁고 실무적이다.

- `Compare & Portfolio Builder`에서 current candidate를 불러올 수 있는지
- 불러온 전략들을 weighted portfolio로 만들 수 있는지
- 그 weighted portfolio를 저장할 수 있는지
- 저장한 portfolio를 나중에 다시 replay했을 때 같은 결과가 나오는지
- 이 흐름을 `Phase 22`의 portfolio-level candidate construction으로 확장해도 되는지

파일명에는 `FIRST_PASS`가 남아 있지만, 여기서 뜻하는 바는 **첫 검증**이다.
즉 최종 결론판이 아니라, "이 workflow를 다음 phase의 정식 작업 대상으로 삼아도 되는가"를 먼저 확인한 문서다.

## 결론 먼저

- `Load Recommended Candidates -> Weighted Portfolio Builder -> Save Portfolio -> Replay Saved Portfolio` 흐름은 정상 작동했다.
- 저장된 portfolio를 replay했을 때 `CAGR`, `MDD`, `End Balance`가 모두 정확히 재현됐다.
- representative weighted portfolio 결과는 `CAGR 28.66%`, `MDD -25.42%`, `Sharpe 1.51`이었다.
- 다만 이번 3개 전략은 모두 annual strict factor family라 서로 완전히 다른 전략군은 아니다.
- 따라서 이번 결과를 최종 분산 포트폴리오 후보로 읽기보다는, **portfolio workflow가 재현 가능하게 작동한다는 검증 결과**로 읽는 것이 맞다.
- 진짜 portfolio-level 후보 구성은 `Phase 22`에서 별도 기준으로 열어야 한다.

## 용어 정리

- `Portfolio Bridge`
  - single strategy 결과를 compare에 올리고, 여러 전략을 weighted portfolio로 묶고, 저장 / replay까지 이어가는 연결 흐름이다.
- `Weighted Portfolio`
  - 여러 전략 결과를 정해진 비중으로 섞어 하나의 portfolio처럼 보는 결과다.
  - 이번 검증에서는 `33 / 33 / 34` 비중을 사용했다.
- `Saved Portfolio Replay`
  - 저장해 둔 compare 설정과 portfolio weight를 다시 실행해서 같은 결과가 나오는지 확인하는 기능이다.
- `First Pass`
  - 이 문서에서는 "첫 검증"이라는 뜻이다.
  - 최종 투자 후보 확정이 아니라, 다음 단계로 넘어갈 만큼 기능과 결과 해석이 성립하는지 확인하는 단계다.

## 왜 이 3개 전략을 묶었나

이번에 묶은 전략은 아래 3개다.

- `Value Snapshot (Strict Annual)`
- `Quality Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

이 3개를 선택한 이유는 다음과 같다.

- `Phase 21`에서 이미 각각 current anchor가 다시 검증된 상태였다.
- 같은 기간, 같은 universe, 같은 annual strict validation frame에서 비교할 수 있었다.
- `Load Recommended Candidates`가 이 3개를 대표 후보로 불러오는 흐름과 자연스럽게 연결됐다.
- portfolio bridge 기능이 current candidate workflow와 이어지는지 확인하기 좋았다.

하지만 한계도 분명하다.

- 세 전략 모두 재무 factor 기반 annual strict family다.
- universe와 rebalance cadence도 비슷하다.
- 그래서 서로 완전히 독립적인 전략 조합이라고 보기는 어렵다.
- 이번 검증은 "분산이 완벽한 포트폴리오를 찾았다"가 아니라,
  "portfolio construction workflow를 실제 후보들로 돌려도 재현 가능하다"를 확인한 것이다.

## 검증 흐름

이번 검증은 아래 순서로 진행했다.

1. `Compare & Portfolio Builder`에서 `Load Recommended Candidates`를 사용한다.
2. `Value`, `Quality`, `Quality + Value` current anchor 3개를 compare 대상으로 불러온다.
3. `Weighted Portfolio Builder`에서 `33 / 33 / 34` 비중을 적용한다.
4. `Date Alignment = intersection` 기준으로 weighted portfolio를 만든다.
5. 그 결과를 saved portfolio로 저장한다.
6. 저장된 portfolio를 `Replay Saved Portfolio`로 다시 실행한다.
7. 최초 weighted result와 replay result의 `CAGR`, `MDD`, `End Balance`가 같은지 확인한다.

## 이번 검증 설정

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
- saved portfolio name:
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

이 결과는 다음처럼 읽는 것이 좋다.

- `Value`보다 CAGR은 조금 높지만 MDD는 더 깊다.
- `Quality + Value`보다 CAGR은 낮지만 MDD는 조금 낮고 Sharpe는 더 높다.
- `Quality`보다 CAGR과 Sharpe는 높다.
- 하지만 이 결과 하나만으로 single-strategy anchor를 대체한다고 보기는 이르다.

## saved portfolio replay 검증

같은 saved portfolio context로 다시 replay했을 때 결과 차이는 아래와 같았다.

| 항목 | 차이 |
|---|---:|
| `CAGR` | `0.0` |
| `MDD` | `0.0` |
| `End Balance` | `0.0` |
| result rows | initial `124` / replay `124` |

해석:

- saved portfolio replay는 이번 representative context에서 weighted result를 정확히 재현했다.
- `Load Saved Setup Into Compare`와 `Replay Saved Portfolio` 흐름은 Phase 21 validation frame에서도 사용할 수 있는 상태로 읽힌다.
- 이 점이 이번 문서에서 가장 중요한 확인 결과다.

## contribution share

마지막 월 기준 contribution share는 아래와 같다.

| component | ending contribution share |
|---|---:|
| `Value Snapshot (Strict Annual)` | `31.05%` |
| `Quality Snapshot (Strict Annual)` | `26.22%` |
| `Quality + Value Snapshot (Strict Annual)` | `42.73%` |

입력 비중은 `33 / 33 / 34`였지만, 마지막 시점 contribution은 `Quality + Value`가 더 커졌다.
이는 blended family의 성장률이 더 높았기 때문이며, weighted portfolio가 시간이 지나며 component 성과 차이를 반영한다는 점을 보여준다.

## 이 결과가 의미하는 것

이번 검증으로 확인된 것은 다음이다.

- current candidate 3개를 compare로 불러오는 흐름은 작동한다.
- compare 결과를 weighted portfolio로 묶는 흐름은 작동한다.
- weighted portfolio 결과를 저장하고 replay하는 흐름은 작동한다.
- replay 결과는 최초 결과와 정확히 일치한다.
- 따라서 portfolio bridge는 단순 UI 부가 기능이 아니라, 다음 phase에서 portfolio-level candidate construction으로 확장할 수 있는 작업 흐름이다.

이번 검증으로 아직 확인하지 않은 것은 다음이다.

- 이 3개 조합이 최종 portfolio winner인지
- 서로 낮은 상관을 가진 진짜 분산 포트폴리오인지
- portfolio-level promotion / shortlist / deployment 기준을 어떻게 줄지
- GTAA, defensive, momentum, treasury, ETF 전략까지 섞었을 때 더 나은 portfolio가 나오는지

## Phase 22로 넘길 질문

`Phase 22`에서는 아래 질문을 별도로 다루는 것이 맞다.

- portfolio-level candidate를 어떤 기준으로 promotion할 것인가
- 단일 전략의 `Promotion / Shortlist / Deployment`를 portfolio에는 어떻게 적용할 것인가
- annual strict factor 전략끼리만 섞을 것인가, 아니면 GTAA / defensive / momentum / treasury 계열까지 섞을 것인가
- 단순 equal-weight가 아니라 risk parity, volatility target, drawdown-aware weighting 같은 weighting rule을 볼 것인가
- portfolio 자체의 benchmark와 guardrail을 어떻게 정할 것인가

## 한 줄 결론

이번 검증은 최종 portfolio winner를 고른 것이 아니라,
**current candidate를 compare에 불러오고, weighted portfolio로 묶고, 저장 / replay까지 재현하는 workflow가 실제로 쓸 수 있는 수준인지 확인한 첫 검증**이다.

결과적으로 이 workflow는 정상 작동했고, `Phase 22`에서 portfolio-level candidate construction을 열 근거는 충분하다.

## 같이 보면 좋은 문서

- [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md)
- [PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
- [PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
- [PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
