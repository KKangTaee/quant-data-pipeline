# Current Project Audit

Status: Active
Last Verified: 2026-06-08

## Snapshot

현재 `finance` Backtest 제품은 단순 backtest runner가 아니라 아래 흐름을 가진 quant research workspace다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Portfolio Monitoring
```

Backtest Analysis는 후보 source를 만들고, Practical Validation / Final Review가 investability evidence와 selected-route gate를 담당한다.
Operations > Portfolio Monitoring은 read-only monitoring surface이며 live approval, broker order, account sync, auto rebalance를 만들지 않는다.

이번 audit의 결론:

- 전략 실행 기능은 넓다.
- 전략별 제품 성숙도는 다르다.
- 다음 개발은 새 전략 추가보다 `후보 evidence / validation / monitoring 연결성`을 고정하는 쪽이 더 중요하다.

## Local Evidence

| Area | Local source | What it proves |
| --- | --- | --- |
| Product direction | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Backtest 결과를 바로 투자 판단으로 쓰지 않고 evidence-first workflow로 검증하는 것이 제품 중심이다. |
| Roadmap | `.aiworkspace/note/finance/docs/ROADMAP.md` | Risk-On Momentum 5D는 research lane complete지만 governance 연결은 deferred decision이다. |
| Project map | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Strategy / runtime / service / UI ownership boundary가 분리되어 있다. |
| Strategy catalog | `app/web/backtest_strategy_catalog.py` | Single / Compare에 노출되는 전략 목록과 family variant를 확인할 수 있다. |
| Single dispatch | `app/services/backtest_execution.py` | 실제 사용자-facing runtime dispatch가 어떤 strategy key를 지원하는지 확인할 수 있다. |
| Candidate replay | `app/runtime/candidate_library.py` | Candidate Library replay는 ETF 5종과 strict annual 3종 중심이다. |
| Strategy reports | `.aiworkspace/note/finance/reports/backtests/strategies/` | strict annual / GTAA / Equal Weight의 기존 후보, gate, tradeoff가 문서화되어 있다. |

## Surface Classification

| Surface | User-facing / internal / mixed | Notes |
| --- | --- | --- |
| Backtest > Backtest Analysis | User-facing product surface | Single Strategy / Portfolio Mix Builder / saved mix replay / Practical Validation handoff를 소유한다. |
| Risk-On Momentum 5D Swing Detail | Mixed research surface | trade log, scanner, comparison, sensitivity, quality warning을 보여주지만 Final Review / Monitoring governance는 아직 없다. |
| Backtest > Practical Validation | User-facing gate / evidence surface | `NOT_RUN`은 pass가 아니며, compact investability evidence를 만든다. |
| Backtest > Final Review | User-facing decision support surface | selected-route gate 통과 후보만 monitoring candidate로 저장한다. |
| Operations > Portfolio Monitoring | User-facing monitoring surface | read-only explicit scenario update 기반이다. |
| Candidate Library | Support / compatibility surface | 현재 replay 지원 범위는 price-only ETF 후보와 strict annual equity 후보 중심이다. |
| Strategy reports | Human-readable research artifact | registry source-of-truth가 아니라 전략 판단 근거와 handoff를 읽는 곳이다. |

## Strengths

- Strategy catalog가 넓다: Equal Weight, GTAA, Global Relative Strength, Risk Parity Trend, Dual Momentum, Risk-On Momentum 5D, Quality / Value / Quality+Value annual and quarterly variants.
- Strict annual family는 기존 탐색 report와 current candidate one-pager가 풍부하다.
- GTAA / Equal Weight는 ETF sleeve와 mix 관점의 후보 근거가 이미 있다.
- Result bundle / Data Trust / Real-Money first-pass / guardrail scope 같은 metadata가 UI와 replay 흐름에 연결되어 있다.
- Practical Validation / Final Review / Portfolio Monitoring workflow는 이미 evidence-first product boundary를 갖췄다.
- UI / service / runtime / finance layer ownership이 최근 refactor round로 정리되어 있다.

## Weaknesses

- 전략 수는 많지만, 전략별 성숙도가 균등하지 않다.
- Strict annual과 GTAA / Equal Weight 외에는 current anchor와 전략 hub가 부족하다.
- Risk-On Momentum 5D는 연구 증거가 강하지만 validation / final selection / daily monitoring policy가 비어 있다.
- Quarterly prototype은 runtime contract smoke를 통과했지만 investment candidate로 읽을 evidence가 부족하다.
- Global Relative Strength는 UI / replay 연결은 되었지만 GTAA 수준의 후보 탐색과 weakness follow-up이 부족하다.
- Risk Parity Trend와 Dual Momentum은 product surface에 있지만 durable strategy report / current candidate guide가 거의 없다.
- Candidate Library replay 지원 범위가 annual strict 중심이라 quarterly / Risk-On Momentum candidate lifecycle은 아직 약하다.
- 기존 report 링크 중 일부는 과거 worktree 경로를 가리킨다. 현재 worktree 기준으로 읽을 때 path drift를 주의해야 한다.

## Product Boundaries

- Keep Final Review and Selected Portfolio Dashboard as decision support, not live approval.
- Do not turn research output into roadmap commitment without user approval.
- Do not treat high CAGR or low MDD as sufficient investability evidence.
- Do not make Risk-On Momentum 5D a monitoring signal without an approved Daily Swing governance design.
- Do not rewrite registry / saved JSONL or generated run history during direction research.
- Do not add provider or FRED direct fetches in UI.

## Audit Conclusion

3차 구현은 새 strategy idea 추가보다 `기존 전략군의 evidence maturity를 정렬하는 일`이 먼저다.

가장 안정적인 첫 구현 scope는 strict annual 대표 후보와 GTAA / Equal Weight bridge를 중심으로, strategy direction dashboard 또는 report/handoff가 Practical Validation / Final Review / Portfolio Monitoring에서 무엇을 더 확인해야 하는지 명확히 보여주는 것이다.

Risk-On Momentum 5D는 두 번째 큰 scope로 분리하는 편이 낫다.
이 전략은 단기 swing이라는 성격상 기존 monthly / annual candidate workflow와 다르므로, 바로 Final Review나 Portfolio Monitoring에 붙이면 gate 의미가 흐려질 수 있다.
