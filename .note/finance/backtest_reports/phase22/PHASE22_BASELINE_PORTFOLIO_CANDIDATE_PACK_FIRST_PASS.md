# Phase 22 Baseline Portfolio Candidate Pack First Pass

## 이 문서는 무엇인가

이 문서는 `Phase 22`의 첫 portfolio-level candidate report다.

쉽게 말하면, `Phase 21`에서 workflow 검증용으로 확인했던
`Value / Quality / Quality + Value` 조합을
`Phase 22`의 **개발 검증용 baseline portfolio candidate pack**으로 다시 읽어도 되는지 정리한다.

여기서 중요한 점은 하나다.

- 이 문서는 최종 portfolio winner 확정 문서가 아니다.
- 이 문서는 실전 투자 승인 문서도 아니다.
- 대신 프로그램이 portfolio 구성 / 저장 / replay / 비교 workflow를 제대로 다루는지 확인하기 위한
  **개발 검증용 baseline 후보 pack**을 고정하는 문서다.

## 결론 먼저

- `Value / Quality / Quality + Value` current anchor 3개는 `Phase 22` baseline portfolio candidate pack의 출발점으로 적합하다.
- 다만 이 조합은 모두 annual strict factor family라서, 완성된 분산 포트폴리오라고 보기는 이르다.
- 따라서 이 baseline은 "투자 기준"이 아니라 "포트폴리오 기능 검증 기준"이다.
- 따라서 현재 상태는:
  - `Portfolio Status`: `baseline_candidate`
  - `Shortlist`: `portfolio_watchlist`
  - `Deployment`: `not_deployment_ready`
  - `Next Action`: weight alternative와 diversified component 추가 가능성 검토
- 즉 이 조합은 "계속 볼 기준점"이지, "바로 실전 투입할 최종 포트폴리오"가 아니다.

## 왜 이 3개 전략을 썼나

`Value / Quality / Quality + Value` 3개를 쓴 이유는
이 조합이 최종 투자 후보라서가 아니다.

이 3개는 Phase 21에서 이미 같은 validation frame으로 다시 검증된 대표 strict annual strategy들이었다.
그래서 포트폴리오 기능을 테스트하기 위한 fixture로 쓰기 좋았다.

이번 phase의 질문은:

- "이 3개를 실전 투자 포트폴리오로 확정할 것인가?"

가 아니라:

- "이 프로그램이 검증된 단일 전략 결과들을 묶어 portfolio로 만들고,
  그 결과를 저장 / replay / 비교할 수 있는가?"

이다.

## 왜 이 report를 따로 만들었나

`Phase 21` report는 portfolio bridge가 작동하는지 확인한 문서였다.

확인한 것은 아래 흐름이다.

1. `Load Recommended Candidates`
2. `Weighted Portfolio Builder`
3. `Save Portfolio`
4. `Replay Saved Portfolio`

반면 `Phase 22`에서는 질문이 달라진다.

- 이 조합을 portfolio 후보로 부를 수 있는가
- 후보로 부른다면 개발 검증상 어떤 status를 줄 것인가
- 앞으로 같은 fixture 기반 weight 조합과 비교할 기준점으로 둘 수 있는가

그래서 같은 결과를 그대로 반복하지 않고,
candidate pack 관점으로 다시 정리한다.

## baseline pack 정의

| 항목 | 값 |
|---|---|
| pack name | `phase22_annual_strict_equal_third_baseline_v1` |
| source | `Phase 21 portfolio bridge validation` |
| saved portfolio id | `portfolio_a516b0a9f117` |
| saved portfolio name | `Value current anchor, Quality current anchor, Quality + Value strongest practical point` |
| saved at | `2026-04-16T08:34:51` |
| validation period | `2016-01-01 ~ 2026-04-01` |
| universe frame | `US Statement Coverage 100`, `Historical Dynamic PIT Universe` |
| date alignment | `intersection` |
| weight policy | `equal-third baseline` |
| saved weights | `[33.33, 33.33, 33.33]` |
| normalized weights | `[1/3, 1/3, 1/3]` |

## `33 / 33 / 34`와 `33.33 / 33.33 / 33.33` 정리

`Phase 21` 문서에서는 사람이 읽기 쉽게 `33 / 33 / 34`라고 표현했다.

하지만 저장된 portfolio definition은:

- `weights_percent = [33.33, 33.33, 33.33]`
- `normalized_weights = [0.3333333333, 0.3333333333, 0.3333333333]`

이다.

따라서 `Phase 22`에서는 이 baseline을
`33 / 33 / 34`가 아니라 **equal-third baseline**으로 부른다.
이 표현이 더 정확하고, 나중에 weight alternative와 비교할 때 덜 헷갈린다.

## component strategies

| component | role in pack | current status |
|---|---|---|
| `Value Snapshot (Strict Annual)` | high-return value anchor | `real_money_candidate / paper_probation / review_required` |
| `Quality Snapshot (Strict Annual)` | quality-only practical anchor | `real_money_candidate / paper_probation / review_required` |
| `Quality + Value Snapshot (Strict Annual)` | blended strongest anchor | `real_money_candidate / small_capital_trial / review_required` |

## component result summary

| component | CAGR | MDD | Sharpe | 해석 |
|---|---:|---:|---:|---|
| `Value Snapshot (Strict Annual)` | `28.13%` | `-24.55%` | `1.43` | current value anchor 유지 |
| `Quality Snapshot (Strict Annual)` | `26.02%` | `-25.57%` | `1.37` | quality-only practical anchor 유지 |
| `Quality + Value Snapshot (Strict Annual)` | `31.82%` | `-26.63%` | `1.48` | blended strongest point 유지 |

## portfolio result summary

| portfolio | CAGR | MDD | Sharpe | End Balance | Rows |
|---|---:|---:|---:|---:|---:|
| `phase22_annual_strict_equal_third_baseline_v1` | `28.63%` | `-25.41%` | `1.51` | `$131,721.23` | `124` |

## metric note

`Phase 21` portfolio bridge report의 `$132,063.56` 결과는
사람이 입력한 `33 / 33 / 34` near-equal weight 결과다.

`Phase 22`에서 공식 baseline으로 고정한 saved portfolio definition은
`[33.33, 33.33, 33.33]`이므로,
Phase 22의 weight alternative 비교에서는 `$131,721.23` 결과를 기준으로 쓴다.

두 결과의 방향성은 거의 같지만, weight 정의가 다르기 때문에
Phase 22 문서에서는 섞어 쓰지 않는다.

## saved replay evidence

`Phase 21` saved replay 검증에서 아래 값이 exact match로 확인됐다.

| 항목 | 차이 |
|---|---:|
| `CAGR` | `0.0` |
| `MDD` | `0.0` |
| `End Balance` | `0.0` |
| result rows | initial `124` / replay `124` |

이 때문에 이 조합은 단순 화면 결과가 아니라
재현 가능한 baseline candidate pack으로 다시 볼 수 있다.

## candidate minimum-record checklist

| 최소 기록 항목 | 상태 | 메모 |
|---|---|---|
| component strategy 목록 | `ok` | 3개 annual strict current anchor |
| source document / candidate source | `ok` | Phase 21 bridge report와 saved portfolio id |
| validation period | `ok` | `2016-01-01 ~ 2026-04-01` |
| universe frame | `ok` | `US Statement Coverage 100`, `Historical Dynamic PIT Universe` |
| weight | `ok` | equal-third baseline |
| date alignment | `ok` | `intersection` |
| benchmark / guardrail interpretation | `ok` | Phase 22 second work unit에서 baseline portfolio benchmark / report-level guardrail 기준 정의 |
| key metrics | `ok` | CAGR / MDD / Sharpe / End Balance |
| saved replay result | `ok` | exact match |
| interpretation / next action | `ok` | baseline 유지, deployment 보류 |

## 유지 / 교체 / 보류 판단

여기서 `유지`는 실전 투자 유지가 아니다.

뜻은:

- 개발 검증용 기준 포트폴리오로 계속 사용한다
- 다음 weight alternative나 diversified component 테스트의 비교 기준으로 쓴다
- 아직 live deployment 후보로 승격하지 않는다

이다.

### 유지하는 이유

- component 3개가 모두 `Phase 21`에서 current anchor로 유지됐다.
- weighted result가 단일 전략 대비 극단적으로 나쁘지 않다.
- saved replay가 exact match로 재현됐다.
- `Sharpe 1.51`로 component 단일 결과보다 risk-adjusted surface가 나아졌다.
- 앞으로 weight alternative나 diversified component를 비교할 기준점으로 쓰기 좋다.

### 바로 최종 후보로 승격하지 않는 이유

- 세 component가 모두 annual strict factor family라 전략 독립성이 충분히 검증되지 않았다.
- portfolio-level benchmark / guardrail policy와 first-pass weight alternative 검증은 끝났지만,
  아직 annual strict family 밖의 diversified component 검증은 남아 있다.
- portfolio-level promotion / shortlist / deployment 기준이 아직 초안 단계다.
- `Quality + Value` contribution이 시간이 지나며 커지는 구조라,
  최종적으로는 blended anchor 편중 여부를 따로 봐야 한다.

### 현재 판단

| 판단 항목 | 결정 |
|---|---|
| baseline 유지 여부 | `maintain_as_baseline` |
| current portfolio candidate status | `baseline_candidate` |
| shortlist status | `portfolio_watchlist` |
| deployment status | `not_deployment_ready` |
| next action | `weight_and_diversification_followup` |

## 다음에 비교할 후보

후속 rerun에서는 아래 후보를 넓게가 아니라 좁게 비교했다.

| 후보 | 왜 보는가 |
|---|---|
| equal-third baseline 유지 | 현재 기준점 |
| `Quality + Value` tilt | strongest component의 기여를 의도적으로 더 키울 때 tradeoff 확인 |
| `Value / Quality` defensive tilt | blended anchor 편중을 줄이고 drawdown tradeoff 확인 |
| future diversified component 추가 | annual strict family끼리만 묶는 한계를 줄일 가능성 확인 |

rerun 결과는 [PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase22/PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md)에 따로 정리했다.

## Phase 22 다음 작업으로 넘길 질문

- first-pass weight alternative 기준으로는 equal-third baseline을 유지해도 되는가
- portfolio-level benchmark를 equal-third baseline으로 두는 현재 해석이 충분히 명확한가
- component strategy의 promotion status를 portfolio status에 어떻게 반영할 것인가
- annual strict family끼리만 묶은 후보를 어디까지 portfolio candidate로 인정할 것인가
- GTAA, treasury, defensive, momentum 계열을 언제 추가 비교할 것인가
- portfolio-level candidate도 `CURRENT_CANDIDATE_REGISTRY.jsonl`에 저장할 것인가,
  아니면 별도 portfolio registry를 둘 것인가

## 한 줄 결론

`phase22_annual_strict_equal_third_baseline_v1`은 최종 포트폴리오 후보가 아니라,
**portfolio 구성 기능을 검증하고 이후 후보를 비교하기 위한 첫 개발 검증용 baseline 후보 pack**으로 유지한다.

## 같이 보면 좋은 문서

- [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_CONSTRUCTION_PLAN.md)
- [PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase22/PHASE22_PORTFOLIO_LEVEL_CANDIDATE_SEMANTICS_FIRST_WORK_UNIT.md)
- [PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md)
- [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
