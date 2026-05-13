# Weighted Portfolio Replay Validation

Status: Historical smoke evidence
Last Verified: 2026-05-12

## 이 문서는 무엇인가

이 문서는 여러 단일 전략 결과를 비중 포트폴리오로 묶고, 저장한 뒤, 다시 불러와 같은 결과가 재현되는지 확인했던 검증 내용을 현재 문서 구조에 맞춰 다시 정리한 것이다.

현재 후보 source-of-truth는 이 문서가 아니다.

- 현재 후보: `.aiworkspace/note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl`
- 최종 선정 판단: `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS*.jsonl`
- 저장된 weight setup: `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl`
- 현재 화면 흐름: `Backtest Analysis -> Practical Validation -> Final Review -> Operations > Selected Portfolio Dashboard`

따라서 이 문서는 “지금 이 포트폴리오를 최종 후보로 보라”는 문서가 아니라, weighted portfolio / saved replay 기능이 어떤 기준으로 검증됐는지 이해하기 위한 runtime smoke 기록이다.

## 이걸 하는 이유?

여러 전략을 하나의 포트폴리오로 묶는 기능은 숫자만 계산된다고 끝나지 않는다.

사용자는 나중에 같은 비중 조합을 다시 열었을 때 같은 결과가 나와야 하고, 비중 입력값과 기간 정렬 방식도 사라지면 안 된다. 이 검증은 과거 annual strict 전략 3개를 fixture로 사용해 아래 흐름이 성립하는지 확인했다.

1. current candidate 성격의 전략 결과를 compare에 올린다.
2. 전략별 weight를 입력해 weighted portfolio를 만든다.
3. weighted portfolio setup을 저장한다.
4. 저장된 setup을 다시 replay한다.
5. 최초 계산과 replay 결과의 주요 metric이 같은지 확인한다.

이 기록이 남아 있으면, 나중에 Saved Portfolio replay나 Practical Validation handoff가 흔들릴 때 어떤 기능 경계를 다시 확인해야 하는지 빠르게 알 수 있다.

## 검증에 사용한 fixture

당시 fixture는 annual strict factor family 3개였다.

| Component | 역할 | 당시 해석 |
|---|---|---|
| Value Snapshot (Strict Annual) | high-return value anchor | practical anchor |
| Quality Snapshot (Strict Annual) | quality-only anchor | practical anchor |
| Quality + Value Snapshot (Strict Annual) | blended anchor | strongest practical point |

중요한 한계:

- 세 component는 모두 annual strict factor family라 완전한 분산 포트폴리오라고 볼 수 없다.
- 이 조합은 최종 투자 후보가 아니라 portfolio 기능 검증 fixture였다.
- 당시 saved portfolio id는 현재 `SAVED_PORTFOLIOS.jsonl`의 active row로 남아 있지 않으므로, 현재 화면에서 그대로 재사용할 대상으로 보지 않는다.

## 확인한 workflow

| Step | 확인 내용 |
|---|---|
| Compare source | 여러 전략 결과를 같은 비교 화면에 올릴 수 있는지 확인 |
| Weighted builder | strategy별 weight를 넣어 composite result를 만들 수 있는지 확인 |
| Date alignment | `intersection` 기준으로 공통 월 구간을 맞출 수 있는지 확인 |
| Save setup | weight setup과 compare context를 저장할 수 있는지 확인 |
| Replay setup | 저장된 setup으로 다시 실행했을 때 metric이 재현되는지 확인 |

## 주요 결과

### Near-equal 입력 검증

| Weight | CAGR | MDD | Sharpe | End Balance | Rows |
|---|---:|---:|---:|---:|---:|
| `33 / 33 / 34` | `28.66%` | `-25.42%` | `1.51` | `$132,063.56` | `124` |

Replay 검증:

| 항목 | 차이 |
|---|---:|
| `CAGR` | `0.0` |
| `MDD` | `0.0` |
| `End Balance` | `0.0` |
| result rows | initial `124` / replay `124` |

### Equal-third baseline 정리

사람이 보기 쉬운 `33 / 33 / 34`와 저장된 normalized equal-third definition은 다르다.

| Definition | CAGR | MDD | Sharpe | End Balance | 해석 |
|---|---:|---:|---:|---:|---|
| `33 / 33 / 34` | `28.66%` | `-25.42%` | `1.51` | `$132,063.56` | near-equal manual input |
| `33.33 / 33.33 / 33.33` | `28.63%` | `-25.41%` | `1.51` | `$131,721.23` | normalized equal-third baseline |

나중에 재검증할 때는 이 두 값을 섞어 쓰지 않는다.

## Weight alternative에서 확인한 점

| Mix | Weight | CAGR | MDD | Sharpe | End Balance | 당시 판단 |
|---|---|---:|---:|---:|---:|---|
| Equal-third baseline | `33.33 / 33.33 / 33.33` | `28.63%` | `-25.41%` | `1.511` | `$131,721.23` | 기준점 |
| Quality + Value tilt | `25 / 25 / 50` | `29.42%` | `-25.74%` | `1.507` | `$140,279.42` | raw return은 좋지만 blended component 의존도 증가 |
| Value / Quality defensive tilt | `40 / 40 / 20` | `27.96%` | `-25.13%` | `1.509` | `$124,874.68` | drawdown은 소폭 낮지만 return 포기 큼 |

당시 결론은 “equal-third baseline을 최종 투자 후보로 선정한다”가 아니었다.

정확한 결론은:

- weighted portfolio builder와 saved replay는 재현 가능했다.
- annual strict 3개 조합은 기능 검증 기준점으로는 유용했다.
- 하지만 실전 포트폴리오 후보로 보려면 GTAA, ETF sleeve, defensive/momentum 계열 등 더 독립적인 component 검증이 필요했다.

## 현재 기준에서 읽는 법

| 질문 | 답 |
|---|---|
| 현재 후보 source-of-truth인가? | 아니다 |
| 현재 saved portfolio 목록에 그대로 남아 있는가? | 아니다 |
| 삭제해도 되는 원본 결과인가? | 핵심 내용은 이 문서와 strategy logs에 흡수했으므로 원래 phase report는 제거 가능 |
| 나중에 쓸 수 있는가? | saved replay, weighted builder, portfolio mix 재검증 기준으로 참고 가능 |

## 같이 봐야 하는 현재 문서

- [Backtest Report Index](../../INDEX.md)
- [Value Strict Annual Backtest Log](../../strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [Quality Strict Annual Backtest Log](../../strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [Quality + Value Strict Annual Backtest Log](../../strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
