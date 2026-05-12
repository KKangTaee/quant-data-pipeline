# Phase 22 Weight Alternative Rerun First Pass

## 이 문서는 무엇인가

이 문서는 `Phase 22`에서 정한 두 가지 portfolio weight alternative를
같은 validation frame에서 다시 계산한 report다.

쉽게 말하면, 이미 정한 baseline portfolio에서 비중만 바꿨을 때
결과가 실제로 좋아지는지 확인한 문서다.

이번에 본 후보는 세 개다.

1. `equal-third baseline`
2. `Quality + Value tilt`
3. `Value / Quality defensive tilt`

## 결론 먼저

- `equal-third baseline`을 Phase 22의 primary portfolio benchmark로 계속 유지한다.
- `25 / 25 / 50` Quality + Value tilt는 CAGR과 End Balance가 좋아졌지만,
  Sharpe가 아주 조금 낮아지고 `Quality + Value` contribution이 50%를 넘는다.
  그래서 baseline을 바로 교체하지 않고 `watch alternative`로 둔다.
- `40 / 40 / 20` Value / Quality defensive tilt는 MDD가 조금 낮아졌지만,
  CAGR과 End Balance를 꽤 포기한다.
  그래서 baseline 교체 후보가 아니라 `comparison-only defensive alternative`로 둔다.
- 이번 rerun 기준으로는 **baseline 교체 없음**이 결론이다.

## 왜 이 검증을 했나

`Phase 22`의 질문은 "아무 weight나 넓게 뒤져서 최고 숫자를 찾자"가 아니다.

지금 질문은 더 좁다.

- strongest component인 `Quality + Value`를 더 키우면 좋아지는가
- blended component 편중을 줄이면 위험이 낮아지는가
- 둘 중 어느 쪽이 baseline을 교체할 만큼 명확한가

따라서 이번에는 broad brute-force search가 아니라,
해석 가능한 두 weight만 먼저 봤다.

## validation frame

| 항목 | 값 |
|---|---|
| source | saved portfolio `portfolio_a516b0a9f117`의 compare context |
| component strategies | `Value`, `Quality`, `Quality + Value` strict annual current anchors |
| input period | `2016-01-01 ~ 2026-04-01` |
| result month range | `2016-01-31 ~ 2026-04-30` |
| universe frame | `US Statement Coverage 100`, `Historical Dynamic PIT Universe` |
| date alignment | `intersection` |
| weighted portfolio function | `make_monthly_weighted_portfolio` |
| run method | saved compare context를 code runner로 재실행한 scripted rerun |

## baseline metric 정정

`Phase 21` portfolio bridge report의 `$132,063.56` 결과는
사람이 입력한 `33 / 33 / 34` near-equal weight 결과다.

반면 `Phase 22`에서 공식 baseline으로 부르기로 한 saved definition은
`[33.33, 33.33, 33.33]`이다.

두 결과는 거의 같은 방향이지만 완전히 같은 weight는 아니다.

| weight | CAGR | MDD | Sharpe | End Balance | 해석 |
|---|---:|---:|---:|---:|---|
| `33 / 33 / 34` | `28.66%` | `-25.42%` | `1.51` | `$132,063.56` | Phase 21 bridge 검증에서 쓴 near-equal 입력 |
| `33.33 / 33.33 / 33.33` | `28.63%` | `-25.41%` | `1.51` | `$131,721.23` | Phase 22 공식 equal-third baseline |

따라서 이 문서부터 Phase 22의 baseline 비교 기준은
`33.33 / 33.33 / 33.33` scripted rerun 값으로 고정한다.

## component rerun summary

| component | CAGR | MDD | Sharpe | End Balance | Rows |
|---|---:|---:|---:|---:|---:|
| `Value Snapshot (Strict Annual)` | `28.13%` | `-24.55%` | `1.43` | `$124,260.12` | `124` |
| `Quality Snapshot (Strict Annual)` | `26.02%` | `-25.57%` | `1.37` | `$104,949.60` | `124` |
| `Quality + Value Snapshot (Strict Annual)` | `31.82%` | `-26.63%` | `1.48` | `$165,953.98` | `124` |

## weight alternative result

| portfolio id | weight | CAGR | MDD | Sharpe | End Balance | Rows |
|---|---:|---:|---:|---:|---:|---:|
| `phase22_annual_strict_equal_third_baseline_v1` | `33.33 / 33.33 / 33.33` | `28.63%` | `-25.41%` | `1.511` | `$131,721.23` | `124` |
| `phase22_annual_strict_quality_value_tilt_v1` | `25 / 25 / 50` | `29.42%` | `-25.74%` | `1.507` | `$140,279.42` | `124` |
| `phase22_annual_strict_value_quality_defensive_tilt_v1` | `40 / 40 / 20` | `27.96%` | `-25.13%` | `1.509` | `$124,874.68` | `124` |

## baseline 대비 차이

| 후보 | CAGR 차이 | MDD 차이 | Sharpe 차이 | End Balance 차이 | 1차 해석 |
|---|---:|---:|---:|---:|---|
| `Quality + Value tilt` | `+0.79%p` | `-0.33%p` | `-0.004` | `+$8,558.19` | 수익은 개선, 위험/편중 watch |
| `Value / Quality defensive tilt` | `-0.67%p` | `+0.28%p` | `-0.002` | `-$6,846.55` | 낙폭은 조금 개선, 수익 포기 큼 |

MDD 차이에서 `+`는 baseline보다 덜 깊다는 뜻이고,
`-`는 baseline보다 더 깊다는 뜻이다.

## contribution concentration

| 후보 | final dominant component | final share | max share | 해석 |
|---|---|---:|---:|---|
| `equal-third baseline` | `Quality + Value` | `42.00%` | `43.14%` | 시간이 지나며 strongest component가 자연스럽게 커짐 |
| `Quality + Value tilt` | `Quality + Value` | `59.15%` | `60.28%` | 사실상 blended anchor tilt에 가까움 |
| `Value / Quality defensive tilt` | `Value` | `39.80%` | `49.07%` | contribution은 가장 균형적 |

`Quality + Value tilt`는 숫자상 CAGR이 좋아졌지만,
장기 contribution이 50%를 넘기 때문에 portfolio-level guardrail상 watch로 본다.

## 후보별 판단

### 1. `equal-third baseline`

판단:

- `maintain_as_primary_baseline`

이유:

- Sharpe가 세 후보 중 가장 높다.
- CAGR, MDD, concentration의 균형이 가장 무난하다.
- saved definition과 해석이 단순하다.
- 앞으로 다른 diversified component를 붙일 때 기준점으로 쓰기 좋다.

### 2. `Quality + Value tilt`

판단:

- `watch_alternative`
- `do_not_replace_baseline_yet`

이유:

- CAGR과 End Balance는 가장 좋다.
- 하지만 Sharpe가 baseline보다 소폭 낮다.
- MDD도 baseline보다 조금 깊어진다.
- 무엇보다 `Quality + Value` contribution이 60% 수준까지 올라가서,
  "세 전략 portfolio"라기보다 "Quality + Value 중심 portfolio"에 가까워진다.

따라서 성과 후보로는 남기되,
portfolio baseline을 교체할 만큼 균형이 좋아졌다고 보지는 않는다.

### 3. `Value / Quality defensive tilt`

판단:

- `comparison_only_defensive_alternative`
- `do_not_replace_baseline`

이유:

- MDD는 baseline보다 약간 낮다.
- contribution 균형도 가장 좋다.
- 하지만 CAGR과 End Balance 하락이 더 크다.
- Sharpe도 baseline보다 소폭 낮다.

따라서 drawdown을 아주 조금 낮추기 위해 baseline을 교체할 이유는 약하다.

## Phase 22 판단

| 항목 | 결정 |
|---|---|
| baseline 교체 여부 | `no_replace` |
| primary portfolio benchmark | `phase22_annual_strict_equal_third_baseline_v1` 유지 |
| `25 / 25 / 50` 후보 | `watch_alternative` |
| `40 / 40 / 20` 후보 | `comparison_only` |
| next action | Phase 22 closeout 준비 또는 diversified component 추가 여부 논의 |

## 아직 확인하지 않은 것

- 이번 rerun은 saved compare context를 code runner로 재실행한 것이다.
- 두 weight alternative를 별도 saved portfolio로 저장하고 replay하는 UI 검증은 아직 하지 않았다.
- 세 component는 모두 annual strict factor family라 분산 효과가 제한적일 수 있다.
- GTAA, treasury, defensive, momentum 같은 다른 전략군을 붙였을 때의 portfolio-level 개선 가능성은 아직 열어두었다.

## 한 줄 결론

`25 / 25 / 50`은 수익은 좋아지지만 `Quality + Value` 편중이 커지고,
`40 / 40 / 20`은 균형은 좋아지지만 수익을 너무 포기한다.

따라서 `Phase 22`의 현재 결론은
**equal-third baseline 유지, 두 alternative는 참고 후보로 보류**다.

## 같이 보면 좋은 문서

- [PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md)
- [PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase22/PHASE22_PORTFOLIO_BENCHMARK_GUARDRAIL_AND_WEIGHT_SCOPE_SECOND_WORK_UNIT.md)
- [PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md)
