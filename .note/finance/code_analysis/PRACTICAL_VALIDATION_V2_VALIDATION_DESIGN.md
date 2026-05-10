# Practical Validation V2 Validation Design

## 목적

이 문서는 `Backtest > Practical Validation`을 단순한 source sanity gate에서
실전 투자 진단 엔진으로 확장하기 위한 조사 / 분석 / 개발 설계 문서다.

현재 목표는 코드를 바로 수정하는 것이 아니라, 사용자가 궁금해한
"이 전략을 실전 전략으로 사용할 수 있나?"라는 질문에 대해
무엇을 어떤 기준으로 검증해야 하는지 정리하는 것이다.

실전 투자 진단 module의 research 기준은
[`PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md`](../research/PRACTICAL_VALIDATION_INVESTMENT_DIAGNOSTICS_RESEARCH.md)에 정리한다.
이 문서는 그 research를 실제 Backtest UI / JSON contract / 구현 slice로 옮기는 개발 가이드다.

이 문서의 결론은 다음과 같다.

- Practical Validation은 투자 추천, live approval, 주문 지시가 아니다.
- Practical Validation은 `Backtest Analysis`에서 선택된 단일 전략, Compare 후보, weighted mix, saved mix를 같은 검증 단위로 읽어야 한다.
- Practical Validation은 앞 단계 evidence를 단순히 다시 보여주는 화면이 아니라, 그 evidence 위에서 portfolio-level 실전 진단을 실행하는 단계다.
- 검증 결과는 `PASS / REVIEW / BLOCKED / NOT_RUN`을 domain별로 분리해서 보여줘야 한다.
- `NOT_RUN`은 통과가 아니다. 아직 데이터나 구현이 없어 확인하지 못했다는 별도 상태다.
- 단일 전략도 1개 component, weight 100% 포트폴리오로 보고 asset allocation, concentration, stress, operability, macro / sentiment context를 진단해야 한다.
- Mix는 component score 합산보다 asset class / exposure / correlation / risk contribution / drop-one sensitivity를 우선 봐야 한다.
- Final Review는 Practical Validation 결과를 바탕으로 최종 선정 / 보류 / 거절 / 재검토를 판단한다.
- Selected Portfolio Dashboard는 Final Review에서 선정된 후보의 사후 monitoring / recheck를 담당한다.

## 현재 구현 기준

현재 Clean V2 구현은 아래 흐름이다.

```text
Backtest Analysis
  -> PORTFOLIO_SELECTION_SOURCES.jsonl
  -> Practical Validation
  -> PRACTICAL_VALIDATION_RESULTS.jsonl
  -> Final Review
  -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl
  -> Operations > Selected Portfolio Dashboard
```

현재 `build_practical_validation_result()`는 다음을 확인한다.

| 현재 체크 | 의미 |
|---|---|
| `selection_source_id` 존재 | Backtest Analysis에서 선택된 Clean V2 source가 있는지 확인 |
| active component 존재 | 검증할 component가 있는지 확인 |
| target weight 합계 100% | 포트폴리오 비중이 완성됐는지 확인 |
| Data Trust blocked 여부 | 원본 실행 결과가 명시적으로 blocked / error인지 확인 |
| Real-Money deployment blocked 여부 | 기존 real-money signal이 blocked인지 확인 |
| benchmark snapshot 존재 | 비교 기준이 아예 없는지 확인 |
| execution boundary | live approval / order instruction disabled 문구 확인 |

즉, 현재 Practical Validation은 깊은 실전 검증이라기보다
`Final Review로 넘길 수 있는 최소 source contract가 있는가`를 보는 단계다.

현재 구현의 공백은 다음이다.

| 공백 | 왜 문제인가 |
|---|---|
| full result curve 재현 검증 없음 | CAGR / MDD snapshot만 보고 rolling, drawdown duration, tail risk를 계산할 수 없다 |
| benchmark 동일 기간 비교 검증 약함 | 같은 기간 / 같은 방법론으로 benchmark와 비교했는지 강하게 보장하지 않는다 |
| 거래 비용 / turnover 검증 없음 | 실전 성과는 비용 차감 후 달라질 수 있다 |
| rolling / walk-forward 안정성 없음 | 전체 기간 평균은 좋아도 특정 구간에서 계속 실패할 수 있다 |
| stress / regime 검증 없음 | 2020, 2022 같은 구조적 시장 구간에서 어떤지 알 수 없다 |
| overfit / sensitivity 검증 없음 | 많은 설정을 돌려 고른 best-only 결과인지 알 수 없다 |
| ETF investability 검증 없음 | bid-ask spread, volume, premium/discount, 비용 구조를 확인하지 않는다 |
| paper observation은 trigger baseline만 있음 | 실제 out-of-sample 관찰 결과가 아니라 향후 볼 기준만 만든다 |

## 앞 단계 검증과의 중복 위험

Practical Validation v2에서 가장 조심해야 할 부분은
이미 앞 단계에서 수행한 검증을 다른 이름으로 다시 수행하는 것이다.

현재 앞 단계에도 검증은 이미 존재한다.

| 위치 | 현재 검증 | 실제 책임 |
|---|---|---|
| Single Strategy runtime | Data Trust, 거래비용 postprocess, benchmark overlay, rolling underperformance, out-of-sample split review, ETF operability, liquidity policy, validation policy, guardrail policy, promotion / deployment readiness | 단일 run의 실행 결과와 실전 해석 meta 생성 |
| Single Strategy result 화면 | Data Trust Summary, Real-Money tab, Summary / Equity / extremes / Meta | 단일 run 결과를 사람이 해석할 수 있게 표시 |
| Compare 5단계 보드 | Compare run 완성도, selected strategy Data Trust, Real-Money gate, 상대 순위 / 상대 근거 | 여러 전략 중 단일 후보를 Practical Validation으로 보낼 수 있는지 판단 |
| Weighted Portfolio Builder | component result를 weight로 합성하고 weighted result curve / summary 생성 | mix 성과 산출 |
| Saved Mix 검증 보드 | saved mix replay 가능 여부, component Data Trust, component Real-Money blocker, Practical Validation / Final Review V2 기록 존재 여부 | 저장된 mix setup이 다시 열리고 검증 flow로 연결될 수 있는지 판단 |
| Practical Validation 현재 v1 | source id, active component, weight total, Data Trust blocked, Real-Money deployment blocked, benchmark snapshot | Final Review로 넘길 최소 Clean V2 source contract 확인 |

따라서 Practical Validation v2는 아래 방식으로 설계해야 한다.

```text
앞 단계 검증 = 원본 실행 / 선택 / replay 검증의 source-of-truth
Practical Validation = 그 증거를 입력으로 받고, portfolio-level 실전 진단을 실행하는 Practical Investment Diagnostics layer
Final Review = 사용자 최종 판단과 최종 메모 저장
```

즉, Practical Validation에서 evidence 통합은 core가 아니라 `Input Evidence Layer`다.
핵심은 아래 같은 질문을 새로 진단하는 것이다.

- 현재 후보가 주식 / 채권 / 현금 / 금 / 원자재 비중 측면에서 목적에 맞는가?
- 여러 ETF를 섞었지만 실제로는 같은 sector / theme / index에 몰려 있지 않은가?
- 50:50 비중처럼 보여도 실제 risk contribution은 한쪽 asset에 과도하게 몰려 있지 않은가?
- rising-rate, inflation shock, recession, crisis window에서 구조적으로 취약하지 않은가?
- VIX, yield curve, credit spread, Fear & Greed 같은 risk context가 추가 관찰을 요구하지 않는가?
- leveraged / inverse ETF가 있으면 보유 기간과 리밸런싱 cadence가 상품 구조와 맞는가?
- 더 단순한 benchmark / 60:40 / cash-aware / All Weather-like baseline 대비 복잡성이 보상되는가?

### 중복이 되는 경우

아래처럼 구현하면 중복 검증 문제가 생긴다.

| 잘못된 구현 | 문제 |
|---|---|
| Single Strategy runtime이 이미 만든 `validation_status`, `rolling_review_status`, `out_of_sample_review_status`를 무시하고 Practical Validation에서 같은 rolling 계산을 별도 기준으로 다시 FAIL 처리 | 사용자는 같은 rolling 검증이 두 번 다른 이름으로 실패한 것으로 본다 |
| Compare 5단계가 이미 Data Trust / Real-Money / 상대 근거를 보고 후보를 보냈는데 Practical Validation이 같은 비교 순위를 다시 점수화 | Compare의 역할과 Practical Validation의 역할이 다시 섞인다 |
| Saved Mix 검증 보드가 replay 가능성을 확인했는데 Practical Validation이 다시 replay 여부만 보고 별도 성공 / 실패 판정을 반복 | Mix 검증 보드와 Practical Validation이 같은 gate처럼 보인다 |
| ETF operability가 runtime meta에 있는데 Practical Validation에서 같은 AUM / spread 기준을 다른 threshold로 다시 계산 | threshold 충돌과 이중 fail이 생긴다 |
| 거래비용이 이미 `transaction_cost_bps`로 반영된 net result인데 Practical Validation이 같은 비용을 다시 차감 | 성과를 이중 차감할 위험이 있다 |

### 중복이 아닌 경우

반대로 아래는 의도적으로 Practical Validation에서 다시 봐야 한다.

| Practical Validation에서 다시 보는 항목 | 중복이 아닌 이유 |
|---|---|
| upstream Data Trust blocker 전파 | 새 검증이 아니라 hard blocker 상속이다 |
| source replay parity | 저장된 source가 지금도 같은 결과로 재현되는지 확인하는 freshness / reproducibility 검증이다 |
| mix-level weight total / concentration | 앞 단계 단일 전략 검증에는 없는 포트폴리오 구성 검증이다 |
| component evidence aggregation | component별 upstream 검증을 입력 evidence로 묶는 작업이다. 최종 판정은 별도 portfolio-level 진단과 섞어서 읽는다 |
| 같은 기간 benchmark alignment 확인 | 여러 component / mix가 서로 다른 actual period를 가질 수 있어 portfolio-level 정렬 확인이 필요하다 |
| `NOT_RUN` domain 표시 | 앞 단계가 확인하지 않은 항목을 통과로 오해하지 않게 하는 표시다 |
| asset allocation / exposure 진단 | 앞 단계 성과 검증만으로 실전 포트폴리오 구성이 적절한지 알 수 없다 |
| correlation / risk contribution 진단 | 자본 비중과 실제 위험 기여가 다를 수 있어 portfolio-level 계산이 필요하다 |
| macro / sentiment context | 현재 시장 환경이 후보의 목적과 충돌하는지 context로 확인하는 새 domain이다 |
| alternative portfolio challenge | 더 단순한 대안 대비 복잡성이 보상되는지 Final Review evidence를 만든다 |
| sensitivity / overfit audit | 현재 앞 단계에는 공식 domain으로 거의 없다 |
| monitoring baseline seed 생성 | Pre-Live record를 만드는 것이 아니라 Final Review와 Selected Portfolio Dashboard가 이어서 쓸 기준값을 만드는 작업이다 |

## Stage Ownership Matrix

Practical Validation v2의 중복을 막으려면 각 검증 domain의 소유권을 명확히 해야 한다.

| Domain | 1차 소유 단계 | Practical Validation v2 역할 | 중복 방지 규칙 |
|---|---|---|---|
| Data freshness / result period | Single Strategy runtime, Compare Data Trust, Saved Mix 검증 보드 | upstream status를 상속하고 portfolio-level로 요약 | 같은 raw warning을 새 fail로 재계산하지 않는다. cadence-aware 해석을 유지한다 |
| Transaction cost / net result | runtime Real-Money hardening | 비용이 이미 반영됐는지 표시하고 mix-level weighted net effect만 보강 | `transaction_cost_bps`가 이미 반영된 result에 같은 비용을 다시 차감하지 않는다 |
| Benchmark overlay / policy | runtime Real-Money hardening | benchmark가 같은 기간 / 같은 방법론인지 확인하고 mix-level benchmark 필요 여부를 표시 | 단일 전략 benchmark policy를 Practical Validation에서 다른 threshold로 재판정하지 않는다 |
| Rolling / OOS review | runtime Real-Money hardening | upstream rolling/OOS status를 domain board에 상속하고, mix result curve가 있을 때만 mix-level rolling을 추가 | upstream status와 PV-computed status를 같은 점수에 이중 반영하지 않는다 |
| ETF operability / liquidity | runtime ETF / liquidity policy | component별 status를 통합하고 누락 데이터를 `NOT_RUN`으로 표시 | 같은 AUM / spread rule을 다른 기준으로 재계산하지 않는다 |
| Compare relative ranking | Compare 5단계 보드 | selection rationale로 보관 | Practical Validation에서 다시 전략 순위를 매겨 후보 선택을 반복하지 않는다 |
| Saved mix replay | Saved Mix 검증 보드 / Weighted Portfolio Builder | source replay parity와 Final Review handoff readiness 확인 | replay 가능 여부만 반복 점수화하지 않고, replay 결과의 freshness / parity를 본다 |
| Weight / construction | Practical Validation | active components, target weight total, concentration, component role 확인 | 앞 단계가 component 성과를 만들었어도 portfolio 구성 검증은 여기서 한다 |
| Asset allocation / exposure | Practical Validation | equity / bond / cash / gold / commodity / sector / theme exposure를 portfolio-level로 계산 | 단일 전략도 100% component 포트폴리오로 보고 같은 진단을 적용한다 |
| Correlation / risk contribution | Practical Validation | component return correlation, volatility contribution, drop-one impact 계산 | Compare 순위나 component CAGR을 다시 고르는 데 쓰지 않고 portfolio risk 구조를 해석한다 |
| Macro / sentiment context | Practical Validation | yield curve, recession window, VIX, Fear & Greed 같은 context overlay 표시 | 매수 / 매도 signal이나 live timing rule로 해석하지 않는다 |
| Alternative portfolio challenge | Practical Validation | SPY, 60:40, cash-aware, All Weather-like baseline 대비 복잡성 보상 여부 표시 | 후보를 자동 탈락시키는 최적화 engine으로 만들지 않는다 |
| Leveraged / inverse suitability | Practical Validation | daily objective, holding period, cadence mismatch, explicit acknowledgement 확인 | ticker 포함 여부만 보고 무조건 실패시키지 않고 비중 / 목적 / 보유 기간을 함께 본다 |
| Sensitivity / overfit | Practical Validation 또는 후속 robustness runner | parameter / weight perturbation, trial-count audit | 앞 단계에 공식 검증이 없으므로 새 domain으로 둔다 |
| Final decision / memo | Final Review | Practical Validation은 판단 근거만 제공 | 사용자 최종 메모를 여기서 받지 않는다 |
| Post-selection monitoring | Selected Portfolio Dashboard | monitoring baseline / trigger seed 제공 | 사후 성과 recheck 자체는 dashboard가 맡는다 |

## Practical Validation V2 구현 규칙

V2 row에는 각 domain의 출처를 남기는 것이 좋다.

```json
{
  "domain": "rolling_walk_forward",
  "status": "REVIEW",
  "origin": "upstream_runtime",
  "source_ref": {
    "selection_source_id": "selection_...",
    "component_id": "..."
  },
  "upstream_status": "watch",
  "pv_status": null,
  "summary": "Runtime Real-Money rolling review를 상속했습니다.",
  "metrics": {}
}
```

권장 `origin` 값:

| origin | 의미 |
|---|---|
| `upstream_runtime` | Single Strategy runtime / Real-Money meta에서 가져온 검증 |
| `upstream_compare` | Compare 5단계 보드에서 가져온 선택 근거 |
| `upstream_saved_mix` | Saved Mix 검증 보드에서 가져온 replay / mix gate 근거 |
| `pv_source_contract` | Practical Validation이 직접 확인한 source / weight / component contract |
| `pv_replay` | Practical Validation에서 source replay를 실행해 확인한 근거 |
| `pv_computed` | Practical Validation에서 새로 계산한 portfolio-level metric |
| `not_run` | 아직 데이터나 구현이 없어 실행하지 못한 domain |

점수도 단순 합산하면 안 된다.
예를 들어 `rolling_review_status=watch`와 `validation_policy_status=watch`가 같은 원인에서 나온 것이라면
두 번 감점하지 말고 하나의 inherited review gap으로 묶어야 한다.

권장 scoring 원칙:

1. hard blocker는 중복되어도 한 번만 카운트한다.
2. 같은 upstream source에서 나온 warning은 하나의 review gap 그룹으로 묶는다.
3. PV가 새로 계산한 domain만 별도 점수로 반영한다.
4. `NOT_RUN`은 감점보다 disclosure로 시작하되, critical domain이면 Final Review에서 확인을 요구한다.
5. Final Review는 score만 보지 않고 blocker / review gap / not-run critical domain을 같이 읽는다.

## 조사 기준

아래 기준을 설계에 반영한다.

| 출처 | 설계에 반영할 점 |
|---|---|
| [Investor.gov - Asset Allocation, Diversification, and Rebalancing](https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset) | asset allocation은 time horizon / risk tolerance와 연결되고, diversification은 자산군 사이와 자산군 내부를 모두 봐야 한다. |
| [CFA Institute - Portfolio Risk and Return Part I](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/portfolio-risk-return-part-1) | portfolio risk는 asset별 risk / return뿐 아니라 correlation에 크게 좌우된다. Practical Validation에서 correlation / risk contribution을 별도 domain으로 둔다. |
| [CFA Institute - Measuring and Managing Market Risk](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/measuring-managing-market-risk) | stress test, scenario analysis, sensitivity, risk budget, position limit는 실전 risk management framework로 쓸 수 있다. |
| [CFA Institute RPC - Extreme Risk Stress Testing](https://rpc.cfainstitute.org/research/financial-analysts-journal/2012/allocating-assets-in-climates-of-extreme-risk-a-new-paradigm-for-stress-testing-portfolios) | stress testing은 historical / hypothetical scenario와 covariance assumption에 민감하므로 결과와 한계를 같이 표시해야 한다. |
| [FINRA - Leveraged and Inverse ETPs](https://www.finra.org/investors/insights/lowdown-leveraged-and-inverse-exchange-traded-products) | leveraged / inverse ETP는 보통 daily objective를 가지므로 중장기 보유, volatility compounding, cadence mismatch를 별도 suitability domain으로 봐야 한다. |
| [Cboe - VIX / Volatility Trading](https://www.cboe.com/tradable-products/volatility-trading/) | VIX는 volatility context로 쓰되, VIX product를 장기 buy-and-hold 투자처럼 해석하지 않도록 boundary를 둔다. |
| [CNN Fear & Greed Index](https://www.cnn.com/markets/fear-and-greed) | market momentum, breadth, put/call, junk bond demand, volatility, safe haven demand를 묶은 sentiment context다. 자동 trading signal이 아니라 review gap context로만 사용한다. |
| [FRED - 10Y minus 3M Treasury Spread](https://fred.stlouisfed.org/series/T10Y3M) | yield curve spread는 macro / recession context overlay에 사용할 수 있다. 타이밍 확정 신호로 단정하지 않는다. |
| [NBER - US Business Cycle Expansions and Contractions](https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions) | recession / expansion date를 historical stress window와 regime tagging에 사용한다. |
| [AQR - Risk Parity, Risk Management and the Real World](https://www.aqr.com/insights/research/white-papers/risk-parity-risk-management-and-the-real-world) | risk parity의 핵심인 risk exposure balance 개념을 portfolio risk contribution 진단에 참고한다. |
| [Bridgewater - The All Weather Story](https://www.bridgewater.com/research-and-insights/the-all-weather-story) | growth / inflation surprise에 대한 asset class balance framework를 macro regime fit 설명에 참고한다. |
| [CFA Institute - Backtesting & Simulation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation) | rolling-window / walk-forward, scenario analysis, simulation, sensitivity analysis, survivorship bias, look-ahead bias, fat-tail / structural break 점검이 backtest 해석의 핵심이다. |
| [SEC - Investment Adviser Marketing Rule Guide](https://www.sec.gov/resources-small-businesses/small-business-compliance-guides/investment-adviser-marketing) | performance 정보는 오해를 만들지 않도록 기간, net/gross, 가정, 한계가 명확해야 한다. 내부 검증 문서도 hypothetical performance를 실제 성과처럼 표현하지 않아야 한다. |
| [SEC Marketing FAQ](https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/marketing-compliance-frequently-asked-questions) | gross / net performance나 특성치가 같은 기간과 비교 가능한 형식으로 표시되어야 한다는 원칙을 benchmark / cost 표시 설계에 반영한다. |
| [CFA Institute - GIPS Overview](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/overview-of-the-global-investment-performance-standards) | 성과 표현은 정확하고 일관된 데이터, transaction cost 차감, benchmark annual returns, simulated/model 성과와 actual 성과의 분리가 중요하다. |
| [CFA Institute - Standard III(D) Performance Presentation](https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-iii-d) | 성과 주장은 fair, accurate, complete해야 하며 simulated result, gross/net, record source, supporting data를 명확히 보관해야 한다. |
| [Federal Reserve SR 11-7 Model Risk Management](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm) | 모델 검증은 conceptual soundness, ongoing monitoring, outcomes analysis / back-testing, benchmarking, documentation으로 나뉜다. Practical Validation도 이 구조를 빌려야 한다. |
| [Bailey and Lopez de Prado - The Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551) | 여러 전략 / 파라미터를 많이 시험한 뒤 최고 성과만 고르면 selection bias와 overfitting이 생긴다. Sharpe는 sample length, non-normality, multiple testing을 고려해야 한다. |
| [Bailey et al. - Statistical Overfitting and Backtest Performance](https://sdm.lbl.gov/oapapers/ssrn-id2507040-bailey.pdf) | in-sample 최적 전략이 out-of-sample에서 무너질 수 있으므로 검증은 best snapshot만 보지 말고 out-of-sample / robustness evidence를 봐야 한다. |
| [Frazzini, Israel, Moskowitz - Trading Costs of Asset Pricing Anomalies](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2294498) | 거래 비용과 capacity는 anomaly / style strategy의 실전 가능성에 직접 영향을 준다. |
| [Novy-Marx and Velikov - A Taxonomy of Anomalies and Their Trading Costs](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2535173) | turnover가 높은 전략은 거래 비용 후 통계적 유의성이 크게 약화될 수 있으므로 turnover / cost check가 필요하다. |
| [Investor.gov - ETF Investor Bulletin](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-24) | ETF는 market price와 NAV 차이, bid-ask spread, brokerage commission, premium/discount, fund website disclosure를 확인해야 한다. |
| [SEC - ETF Rule Compliance Guide](https://www.sec.gov/investment/exchange-traded-funds-small-entity-compliance-guide) | ETF에는 holdings, NAV, market price, premium/discount, median bid-ask spread 같은 trading cost / transparency disclosure가 중요하다. |

## 설계 원칙

### 1. Practical Diagnostics이지 approval이 아니다

Practical Validation은 다음 질문에 답한다.

```text
이 후보가 Final Review에서 실전 후보로 판단될 만큼 구조, 위험, 운용 가능성, context 근거를 갖췄는가?
```

답하지 않는 질문은 다음이다.

```text
지금 실제 돈으로 사도 되는가?
얼마를 사야 하는가?
자동 리밸런싱을 해도 되는가?
```

따라서 UI와 JSON에는 계속 아래 boundary가 남아야 한다.

- investment recommendation 아님
- live approval 아님
- order instruction 아님
- future return guarantee 아님

Evidence pack은 Practical Diagnostics의 입력과 출력 형식이다.
제품 가치의 중심은 "이미 통과한 검증을 다시 보여주기"가 아니라,
포트폴리오 후보가 실전 운용 후보로서 어떤 구조적 약점과 검토 근거를 갖는지 새로 진단하는 데 있다.

### 2. Domain별 판정을 분리한다

전체 결과를 하나의 `READY / FAIL`로 압축하면 사용자가 무엇이 부족한지 알 수 없다.
다음 domain별로 판정을 분리한다.

| 상태 | 의미 |
|---|---|
| `PASS` | 현재 데이터와 구현 기준에서 통과 |
| `REVIEW` | hard blocker는 아니지만 Final Review 전에 사용자가 확인해야 함 |
| `BLOCKED` | 이 상태에서는 Final Review selected route로 보내면 안 됨 |
| `NOT_RUN` | 아직 필요한 데이터나 검증 구현이 없어 실행하지 못함 |

최종 route는 domain 결과를 조합한다.

| route | 조건 |
|---|---|
| `READY_FOR_FINAL_REVIEW` | blocker 없음, critical domain이 PASS 또는 허용 가능한 REVIEW |
| `NEEDS_REVIEW` | blocker는 없지만 review gap 또는 NOT_RUN domain이 있음 |
| `BLOCKED` | 재현성, 데이터, 비중, benchmark, execution boundary 같은 hard blocker 존재 |

### 3. Validation Profile이 threshold / weight / blocker 해석을 조정한다

Practical Validation은 진단 전에 3~5개 질문으로 `Validation Profile`을 만든다.
이 profile은 어떤 진단을 실행할지 고르는 필터가 아니다.
12개 diagnostic domain은 가능한 한 모두 실행하고, profile은 아래를 조정한다.

- domain별 threshold
- domain별 중요도 weight
- `REVIEW`와 `BLOCKED`의 경계
- Final Review에서 확인해야 하는 required confirmation
- 사용자 의도와 후보 성격 mismatch warning

권장 질문:

| 질문 | 선택지 예시 | 반영 domain |
|---|---|---|
| 주된 목적 | 방어형 / 균형형 / 성장형 / 공격형 / 헤지형 | asset allocation, benchmark challenge, stress |
| 감내 가능한 손실 | -10% / -20% / -35% / 그 이상 | drawdown, tail, rolling |
| 예상 운용 기간 | 3개월 미만 / 6~12개월 / 1~3년 / 3년 이상 | leveraged / inverse, cost, rolling window |
| 상품 / 회전율 허용 | 단순 ETF만 / sector ETF 가능 / leveraged·inverse 제한 허용 | ETF operability, cost, suitability |
| 단순 대안 대비 기대 | MDD 감소 / CAGR 증가 / Sharpe 개선 / 하락 방어 / theme 노출 | alternative challenge |

기본 profile:

| profile | 의미 |
|---|---|
| `conservative_defensive` | 손실 방어와 안정성 우선. MDD, concentration, liquidity, cost에 엄격 |
| `balanced_core` | 수익과 위험 균형. CAGR / MDD / diversification을 균형 있게 봄 |
| `growth_aggressive` | 성장과 upside 우선. 높은 equity exposure는 허용하되 overfit / tail risk는 계속 확인 |
| `hedged_tactical` | hedge 또는 tactical exposure. inverse / cash / bond role과 cadence mismatch를 더 강하게 봄 |
| `custom` | 사용자가 답변으로 threshold / weight를 직접 구성 |

profile로 무력화하면 안 되는 invariant hard blocker:

- Data Trust hard blocker 또는 result 없음
- active weight 합계 오류
- 핵심 ticker 가격 부재
- replay 불가능한데 snapshot-only로 selected judgment를 요구하는 경우
- 거래 불가 또는 심각한 liquidity issue
- 큰 leveraged / inverse exposure인데 목적 / 보유 기간 / acknowledgement가 없는 경우
- live approval / order instruction boundary 위반

### 4. 사용자 의도와 후보 성격 mismatch를 표시한다

Practical Validation은 사용자가 원한 포트폴리오 성격과 실제 후보 성격이 어긋날 때
이를 별도 warning으로 표시해야 한다.

예시:

| 사용자 의도 | 후보 진단 결과 | warning |
|---|---|---|
| 공격형 성장 | SPY / QQQ와 성과와 노출 차이가 작음 | 복잡한 후보를 유지할 근거가 약하고 공격형 목표와 차별성이 낮음 |
| 방어형 | equity / growth / sector concentration이 높음 | 선택한 profile 대비 손실 방어 구조가 부족함 |
| 헤지형 | inverse ETF 비중과 리밸런싱 cadence가 불명확 | hedge 목적과 상품 구조 mismatch를 확인해야 함 |
| 저비용 장기 운용 | turnover / expense / spread 부담이 큼 | 장기 비용 부담이 후보 목적과 충돌할 수 있음 |

이 warning은 투자 추천이 아니다.
예를 들어 `차라리 SPY를 사세요`가 아니라,
`단순 benchmark 후보와 함께 Final Review에서 비교하는 것이 좋습니다`처럼
검토 방향을 제시해야 한다.

### 5. 같은 기간 / 같은 방법론 / 비용 차감을 우선한다

성과 비교는 다음을 명시해야 한다.

- strategy period
- benchmark period
- requested period
- actual result period
- rebalance / signal cadence
- gross / net 구분
- cost assumption
- benchmark ticker / benchmark calculation method

특히 mix는 component별 actual end가 다를 수 있으므로
cadence-aware date alignment가 필요하다.

### 6. Snapshot보다 replay를 우선한다

Practical Validation v2는 snapshot만 믿지 말고 replay contract를 우선해야 한다.

권장 순서:

1. `selection_source_snapshot`에서 원본 설정 / component / weight를 읽는다.
2. replay contract가 있으면 동일 설정으로 result curve를 재계산한다.
3. 재계산 summary가 snapshot summary와 크게 다르면 `REVIEW` 또는 `BLOCKED`로 표시한다.
4. replay가 불가능하면 snapshot-only validation으로 낮추고 해당 domain을 `NOT_RUN` 또는 `REVIEW`로 둔다.

### 7. Overfit 위험은 "성공한 결과"보다 "선택 과정"을 봐야 한다

Practical Validation에서 필요한 것은 최고 성과의 크기만이 아니다.

- 같은 전략을 몇 번 시험했는가
- 어떤 파라미터 후보군에서 골랐는가
- 유사 파라미터도 비슷하게 작동하는가
- benchmark와 비교한 우위가 특정 한 구간에만 몰려 있는가
- Sharpe가 비정상적일 정도로 높지만 표본이 짧거나 fat-tail이 큰가

초기 구현에서는 완전한 DSR / PBO를 바로 구현하지 않아도 된다.
대신 trial count, nearby parameter sensitivity, rolling result dispersion을 먼저 기록하고
후속 단계에서 Deflated Sharpe Ratio를 추가한다.

## 검증 Domain 설계

### A. Source Contract / Identity

| 항목 | 내용 |
|---|---|
| 검증 질문 | 이 후보가 어디서 왔고, 어떤 설정으로 만들어졌는가? |
| 필요한 데이터 | `selection_source_id`, `source_kind`, `source_title`, `components`, `construction`, `source_snapshot` |
| 현재 가능 여부 | 가능 |
| 판정 기준 | id / component / construction 존재, source kind가 허용 목록인지 확인 |
| blocker | id 없음, active component 없음, source kind 알 수 없음 |
| 출력 예 | `PASS: saved_mix source with 2 active components` |

### B. Weight / Construction Integrity

| 항목 | 내용 |
|---|---|
| 검증 질문 | 실전 후보로 볼 포트폴리오 비중이 완성됐는가? |
| 필요한 데이터 | component target weight, active component count, max weight, component role |
| 현재 가능 여부 | 부분 가능 |
| 판정 기준 | active weight 합계 100%, 음수 / null weight 없음, max weight와 component 수 표시 |
| blocker | active weight 합계가 100%가 아님 |
| review gap | 특정 component 80% 이상 집중, component role 없음, benchmark 누락 |

초기에는 concentration을 blocker로 두지 말고 review gap으로 둔다.
사용자의 투자 목적에 따라 100% 단일 후보도 의도한 구성이 될 수 있기 때문이다.

### B2. Asset Allocation / Exposure Fit

| 항목 | 내용 |
|---|---|
| 검증 질문 | 이 후보는 주식 / 채권 / 현금 / 금 / 원자재 / inverse / leveraged 노출이 목적에 맞는가? |
| 필요한 데이터 | component ticker category, target weight, ETF category / holdings proxy, validation profile |
| 현재 가능 여부 | 새 classification helper 필요 |
| 판정 기준 | asset class exposure, equity concentration, hedge asset 존재 여부, profile 대비 편차 |
| blocker | 대부분의 component를 분류할 수 없는데 실전 후보로 판단하려는 경우 |
| review gap | equity 90% 이상, bond / cash / gold hedge 없음, theme / sector ETF가 포트폴리오 대부분 |

단일 전략도 이 domain을 통과해야 한다.
단일 ETF 100% 포트폴리오라면 "의도된 집중인지", "benchmark와 다를 바가 있는지",
"ETF 내부 sector / holding concentration을 봐야 하는지"를 표시한다.

Mix의 경우 component를 단순 합산하지 말고 asset class / sector / theme exposure를
target weight 기준으로 합산한다.

### B3. Correlation / Diversification / Risk Contribution

| 항목 | 내용 |
|---|---|
| 검증 질문 | 자본 비중이 아니라 실제 위험도 분산되어 있는가? |
| 필요한 데이터 | component price / return history, target weights, benchmark curve |
| 현재 가능 여부 | 새 계산 필요 |
| 판정 기준 | pairwise correlation, rolling correlation, volatility contribution, benchmark beta, drop-one impact |
| blocker | 실전 후보 판단에 필요한 return history가 없고 snapshot-only로 risk 구조를 설명하려는 경우 |
| review gap | 50:50 mix지만 portfolio volatility contribution의 대부분이 한 component에서 발생 |

이 domain은 "어느 전략이 더 좋은지"를 다시 고르는 Compare 검증이 아니다.
이미 선택된 후보가 실제로 분산된 포트폴리오인지 설명하는 portfolio risk 진단이다.

### C. Data Integrity / Data Trust

| 항목 | 내용 |
|---|---|
| 검증 질문 | 백테스트 결과가 요청 기간과 데이터 상태를 신뢰할 수 있는가? |
| 필요한 데이터 | requested start/end, actual start/end, result rows, warning count, excluded tickers, data freshness status |
| 현재 가능 여부 | 부분 가능 |
| 판정 기준 | Data Trust blocked / error 확인, actual period gap, excluded ticker, warning count |
| blocker | data trust `blocked` / `error`, result row 없음, 핵심 ticker 전부 제외 |
| review gap | cadence 때문에 actual end가 짧음, 일부 ticker 제외, warning 존재 |

중요한 세부 기준:

- GTAA처럼 `interval > 1`, `month_end` cadence를 쓰는 경우 actual end가 요청 end보다 짧은 것은 항상 DB 부족이 아니다.
- 이 경우 `requested_end - actual_end`를 calendar day만으로 blocker 처리하지 말고
  strategy cadence와 next rebalance date 기준으로 해석해야 한다.
- cadence-aware 허용 범위를 넘어서는 gap만 blocker 또는 review gap으로 본다.

### D. Reproducibility / Replay

| 항목 | 내용 |
|---|---|
| 검증 질문 | 같은 설정으로 결과를 다시 만들 수 있는가? |
| 필요한 데이터 | replay contract, settings snapshot, tickers, benchmark, period, strategy key, result curve |
| 현재 가능 여부 | 부분 가능. source마다 replay contract 품질이 다름 |
| 판정 기준 | replay success, summary delta, row count, start/end parity |
| blocker | replay contract 없음 + snapshot만으로 Final Review selected route를 만들 수 없음 |
| review gap | replay summary와 snapshot summary 차이가 임계값 이상 |

권장 first-pass metric:

- `replay_available`
- `replay_success`
- `snapshot_cagr`
- `replay_cagr`
- `cagr_delta`
- `snapshot_mdd`
- `replay_mdd`
- `mdd_delta`
- `result_row_delta`

### E. Benchmark / Relative Performance

| 항목 | 내용 |
|---|---|
| 검증 질문 | 무엇과 비교했을 때 실전 후보로 볼 수 있는가? |
| 필요한 데이터 | benchmark ticker, benchmark curve, same period strategy curve, summary metrics |
| 현재 가능 여부 | 부분 가능. benchmark snapshot은 있으나 curve 재계산은 source별 확인 필요 |
| 판정 기준 | benchmark 존재, same period comparison, CAGR spread, MDD difference, Sharpe difference |
| blocker | benchmark 없음, benchmark result curve 없음, 비교 기간 불일치가 큰데 표시 없음 |
| review gap | benchmark 대비 초과수익이 약함, benchmark보다 MDD 악화, benchmark와 correlation 과도 |

최소 표시는 아래를 포함한다.

- strategy CAGR / MDD / Sharpe
- benchmark CAGR / MDD / Sharpe
- strategy - benchmark CAGR spread
- MDD improvement / deterioration
- same-period flag
- gross/net flag

### F. Rolling / Walk-Forward Stability

| 항목 | 내용 |
|---|---|
| 검증 질문 | 전체 평균이 아니라 여러 구간에서도 성과가 유지되는가? |
| 필요한 데이터 | daily or monthly result curve, benchmark curve |
| 현재 가능 여부 | 새 계산 필요 |
| 판정 기준 | rolling 12m / 36m return, rolling MDD, rolling benchmark spread, pass ratio |
| blocker | result curve가 없어 rolling 계산 불가이고 snapshot-only로 selected route를 만들려는 경우 |
| review gap | rolling window 대부분에서 benchmark 하회, 특정 한 구간에 성과 집중 |

권장 MVP:

- monthly return으로 12개월 / 36개월 rolling return 계산
- strategy rolling return과 benchmark rolling return 비교
- rolling window 중 strategy가 benchmark를 이긴 비율 표시
- worst rolling return / worst rolling drawdown 표시

권장 상태:

| 상태 | 조건 예시 |
|---|---|
| `PASS` | 충분한 window가 있고 극단적 집중이 없음 |
| `REVIEW` | window 수가 적거나 benchmark win rate가 낮음 |
| `NOT_RUN` | result curve 없음 |

### G. Drawdown / Tail / Recovery

| 항목 | 내용 |
|---|---|
| 검증 질문 | 손실 구간의 크기, 길이, 회복 가능성을 감당할 수 있는가? |
| 필요한 데이터 | result curve, peak/trough, monthly returns |
| 현재 가능 여부 | 새 계산 필요 |
| 판정 기준 | max drawdown, drawdown duration, recovery months, worst monthly return, historical VaR / CVaR |
| blocker | 사용자가 지정한 max drawdown tolerance를 크게 초과 |
| review gap | 회복 기간이 길거나 tail loss가 benchmark보다 나쁨 |

MVP에서는 다음만 먼저 계산해도 충분하다.

- max drawdown
- max drawdown start / trough / recovery date
- recovery months
- worst monthly return
- negative month ratio

VaR / CVaR는 monthly return 기반으로 후속 추가한다.

### H. Regime / Stress Windows

| 항목 | 내용 |
|---|---|
| 검증 질문 | 특정 시장 regime에서 무너지는가? |
| 필요한 데이터 | result curve, benchmark curve, known stress window calendar |
| 현재 가능 여부 | 새 계산 필요 |
| 판정 기준 | stress window별 return, MDD, benchmark spread |
| blocker | strategy 목적상 반드시 봐야 하는 stress window가 기간 내 있는데 결과가 없음 |
| review gap | 특정 stress window에서 benchmark 대비 크게 열위 |

초기 stress window 후보:

| Window | 의미 |
|---|---|
| 2020-02 to 2020-04 | COVID crash |
| 2022-01 to 2022-10 | inflation / rate shock |
| 2023-03 | banking stress |
| custom | 사용자가 직접 지정한 검증 기간 |

기간이 겹치지 않으면 `NOT_RUN: period does not cover stress window`로 표시한다.
겹치지 않는 것을 실패로 처리하지 않는다.

### H2. Macro / Sentiment Context Overlay

| 항목 | 내용 |
|---|---|
| 검증 질문 | 현재 macro / sentiment 환경이 후보 포트폴리오의 목적과 충돌하거나 추가 관찰을 요구하는가? |
| 필요한 데이터 | yield curve spread, recession window, VIX, credit spread, Fear & Greed, market breadth / momentum proxy |
| 현재 가능 여부 | 새 connector / optional data 필요 |
| 판정 기준 | risk-on / risk-off context, recession / rate shock context, high volatility context, signal freshness |
| blocker | 기본값은 blocker로 쓰지 않음. 단, 후보 설명이 macro defense인데 macro evidence가 전혀 없으면 review 또는 blocked 후보 |
| review gap | high-beta / high-equity 후보인데 sentiment가 극단적 greed 또는 volatility complacency로 표시됨 |

이 domain은 매수 / 매도 signal이 아니다.
CNN Fear & Greed, VIX, yield curve 같은 지표는 Final Review에서
"현재 시장 context상 바로 선정할지, 추가 관찰할지"를 판단할 때 보는 context evidence다.

### I. Cost / Turnover / Slippage

| 항목 | 내용 |
|---|---|
| 검증 질문 | 비용 차감 후에도 전략이 의미가 있는가? |
| 필요한 데이터 | rebalance dates, holdings/weights by rebalance, turnover, ETF expense ratio, bid-ask spread, commission/slippage assumptions |
| 현재 가능 여부 | 대부분 새 계산 / 데이터 필요 |
| 판정 기준 | gross vs net CAGR, annual turnover, cost drag, rebalance count |
| blocker | turnover 계산이 필수인 고회전 전략인데 turnover 데이터 없음 |
| review gap | 비용 차감 후 benchmark 대비 우위 소멸 |

MVP 비용 모델:

```text
one_way_cost_bps = user_input or default profile
annual_expense_ratio_bps = component ETF expense ratio if available else user_input
turnover_cost = one_way_cost_bps * annual_turnover
net_return = gross_return - turnover_cost - expense_ratio
```

초기에는 정확한 주문장 시뮬레이션을 하지 않는다.
대신 보수적 cost assumption을 명시하고 net summary를 함께 표시한다.

### J. ETF Investability / Liquidity

| 항목 | 내용 |
|---|---|
| 검증 질문 | 구성 ETF가 실제로 거래 가능한가? |
| 필요한 데이터 | ticker type, latest price, average dollar volume, bid-ask spread, AUM, expense ratio, premium/discount, fund status |
| 현재 가능 여부 | asset_profile / price metadata 확장 필요 |
| 판정 기준 | ticker alive, price available, liquidity proxy, cost proxy |
| blocker | 가격 없음, 상장폐지 / 거래불가로 보임, leveraged/inverse ETF인데 명시 승인 없음 |
| review gap | low volume, high spread, high expense ratio, premium/discount 정보 없음 |

초기 구현 우선순위:

1. price available / latest date
2. ticker profile exists
3. 20d average dollar volume proxy
4. expense ratio if available
5. bid-ask / premium-discount는 데이터 수집 확장 후 추가

### J2. Leveraged / Inverse ETF Suitability

| 항목 | 내용 |
|---|---|
| 검증 질문 | leveraged / inverse ETF가 포함되어 있다면 보유 기간, 리밸런싱 cadence, 목적이 상품 구조와 맞는가? |
| 필요한 데이터 | ticker classification, leverage / inverse flag, target weight, rebalance cadence, component role |
| 현재 가능 여부 | ticker classification helper 필요 |
| 판정 기준 | daily objective disclosure, weight size, hedge role, holding period mismatch, operator acknowledgement |
| blocker | leveraged / inverse 비중이 크고 목적 / holding period / acknowledgement가 없음 |
| review gap | 작은 hedge 목적이라도 volatility compounding과 daily reset risk를 Final Review에서 확인해야 함 |

FINRA / SEC 계열 자료는 leveraged / inverse ETP가 일반 ETF와 다르게 작동하며
중장기 보유 성과가 underlying index와 크게 달라질 수 있음을 강조한다.
따라서 이 domain은 단순히 ticker를 금지하는 장치가 아니라,
상품 구조와 포트폴리오 사용 목적의 mismatch를 명시하는 장치다.

### K. Parameter / Weight Sensitivity

| 항목 | 내용 |
|---|---|
| 검증 질문 | 설정을 조금만 바꿔도 결과가 무너지는가? |
| 필요한 데이터 | strategy settings, perturbation grid, weighted mix weights |
| 현재 가능 여부 | 새 runner 필요 |
| 판정 기준 | nearby settings의 CAGR / MDD / Sharpe dispersion, original percentile |
| blocker | best-only 최적화 결과인데 trial log / sensitivity가 전혀 없음 |
| review gap | 원본 설정만 유난히 좋고 주변 설정은 대부분 실패 |

초기에는 모든 전략에 같은 sensitivity를 강제하지 않는다.

권장:

- GTAA: interval, moving average window, top/bottom selection, rebalance day perturbation
- Equal Weight: rebalance frequency, ticker subset / sector grouping perturbation
- GRS / Relative Strength: lookback window, top_n, skip period perturbation
- Mix: target weight +/- 5%p 또는 component drop-one sensitivity

### L. Overfit / Selection Process Audit

| 항목 | 내용 |
|---|---|
| 검증 질문 | 이 후보가 많은 실험 중 우연히 좋아 보인 결과인가? |
| 필요한 데이터 | run history count, compare set, strategy family, parameter grid, selected reason |
| 현재 가능 여부 | 부분 가능. run_history는 generated라 commit 대상은 아니지만 local audit에는 사용 가능 |
| 판정 기준 | number of trials, selected rank, family-level repeated attempts, DSR/PBO later |
| blocker | 명백한 대규모 parameter search best-only인데 validation evidence 없음 |
| review gap | trial count 불명, selected reason 없음, near-miss 기록 없음 |

MVP:

- 같은 source title / strategy family의 recent local run count 표시
- compare universe에서 selected rank 표시
- selected source가 best-only인지, mix construction인지 표시

후속:

- Deflated Sharpe Ratio
- Probability of Backtest Overfitting
- minimum track record length

### M. Conceptual Soundness / Strategy Rationale

| 항목 | 내용 |
|---|---|
| 검증 질문 | 이 전략의 논리와 사용 목적이 설명 가능한가? |
| 필요한 데이터 | strategy family, universe, rebalance rule, factor/ticker set, intended role |
| 현재 가능 여부 | 부분 가능 |
| 판정 기준 | strategy type이 known catalog에 있고, universe와 목적이 모순되지 않음 |
| blocker | strategy key / rule 불명, source snapshot이 결과만 있고 규칙 없음 |
| review gap | mix component role 없음, safe asset / benchmark 목적 불명 |

이 domain은 자동 점수보다 설명 가능성 표시가 중요하다.

### M2. Alternative Portfolio Challenge

| 항목 | 내용 |
|---|---|
| 검증 질문 | 이 후보는 더 단순한 대안 포트폴리오보다 복잡성을 감수할 만큼 나은가? |
| 필요한 데이터 | candidate curve, benchmark curve, simple baseline curves, cost / turnover summary |
| 현재 가능 여부 | benchmark / replay helper 확장 필요 |
| 판정 기준 | SPY, 60:40 proxy, cash-aware baseline, All Weather-like proxy 대비 CAGR / MDD / Sharpe / recovery / cost drag |
| blocker | 기본값은 blocker가 아님 |
| review gap | 후보가 복잡하지만 단순 baseline 대비 성과 / 위험 개선이 거의 없음 |

이 domain은 자동 최적화 engine이 아니다.
Final Review에서 "왜 이 후보여야 하는가"를 묻기 위한 challenge evidence다.

### N. Paper Observation / Ongoing Monitoring Plan

| 항목 | 내용 |
|---|---|
| 검증 질문 | 선정 후 무엇을 보고 재검토할 것인가? |
| 필요한 데이터 | baseline CAGR/MDD, benchmark, review cadence, triggers, dashboard recheck contract |
| 현재 가능 여부 | 부분 가능 |
| 판정 기준 | benchmark, cadence, trigger, selected dashboard replay path 존재 |
| blocker | 선정 후 비교 기준이 전혀 없음 |
| review gap | trigger가 너무 일반적이거나 threshold가 없음 |

MVP trigger:

- CAGR deterioration vs baseline
- MDD expansion vs baseline
- benchmark-relative underperformance
- Data Trust refresh issue
- actual allocation drift, if user enters allocation

이 domain은 별도의 Pre-Live record를 만들거나 사용자 메모를 추가로 저장하는 단계가 아니다.
Final Review selected row와 Selected Portfolio Dashboard가 이어서 읽을 monitoring baseline seed를 만드는 것이 목적이다.

## 권장 Practical Validation V2 JSON Schema

현재 schema version 1은 단순 `checks / hard_blockers / review_gaps` 중심이다.
v2에서는 `input_evidence`와 `diagnostic_results`를 분리한다.

```json
{
  "schema_version": 2,
  "validation_id": "validation_...",
  "selection_source_id": "selection_...",
  "created_at": "...",
  "source_kind": "weighted_portfolio_mix",
  "source_title": "...",
  "validation_profile": {
    "profile_id": "balanced_core",
    "answers": {
      "primary_goal": "balanced",
      "drawdown_tolerance": "-20%",
      "holding_period": "1-3y",
      "complexity_allowance": "sector_etf_allowed",
      "alternative_success_metric": "mdd_reduction"
    },
    "thresholds": {
      "max_drawdown_review": -0.25,
      "equity_exposure_review": 0.85,
      "benchmark_win_rate_review": 0.5
    },
    "domain_weights": {
      "asset_allocation_fit": 1.0,
      "drawdown_tail": 1.0,
      "alternative_portfolio_challenge": 0.8
    }
  },
  "validation_route": "NEEDS_REVIEW",
  "overall_score": 7.4,
  "hard_blockers": [],
  "review_gaps": [],
  "not_run_domains": [],
  "intent_mismatch_warnings": [],
  "invariant_hard_blockers": [],
  "input_evidence": {
    "data_trust": {},
    "real_money_gate": {},
    "compare_rationale": {},
    "mix_replay": {}
  },
  "diagnostic_results": [
    {
      "domain": "asset_allocation_fit",
      "status": "REVIEW",
      "score": 6.5,
      "origin": "pv_computed",
      "profile_effect": {
        "profile_id": "balanced_core",
        "threshold_used": 0.85,
        "status_without_profile": "PASS"
      },
      "summary": "Equity exposure is above the balanced profile review line.",
      "metrics": {
        "equity_weight": 0.86,
        "bond_weight": 0.0,
        "cash_like_weight": 0.0
      },
      "blockers": [],
      "review_gaps": ["high equity exposure"],
      "limitations": ["ticker category mapping is proxy-based"]
    },
    {
      "domain": "rolling_walk_forward",
      "status": "REVIEW",
      "score": 6.0,
      "origin": "pv_computed",
      "summary": "36m rolling benchmark win rate is 48%.",
      "metrics": {
        "window_months": 36,
        "window_count": 84,
        "benchmark_win_rate": 0.48,
        "worst_rolling_return": -0.18
      },
      "blockers": [],
      "review_gaps": ["benchmark win rate below target profile"],
      "limitations": [],
      "evidence_rows": []
    }
  ],
  "replay": {
    "status": "PASS",
    "replay_available": true,
    "snapshot_delta": {
      "cagr_delta": 0.001,
      "mdd_delta": 0.002
    }
  },
  "benchmark_relative": {},
  "rolling_validation": {},
  "drawdown_tail": {},
  "asset_allocation_fit": {},
  "concentration_overlap": {},
  "correlation_risk_contribution": {},
  "stress_windows": {},
  "macro_sentiment_context": {},
  "alternative_portfolio_challenge": {},
  "cost_turnover": {},
  "investability": {},
  "leveraged_inverse_suitability": {},
  "sensitivity": {},
  "overfit_audit": {},
  "monitoring_plan": {},
  "final_review_confirmations": [],
  "selection_source_snapshot": {}
}
```

v1 compatibility:

- Final Review는 v1 row도 계속 읽어야 한다.
- v2 row가 있으면 `diagnostic_results`를 우선 표시한다.
- 과도기에는 기존 `domain_results` key를 읽되 새 저장은 `diagnostic_results`로 한다.
- v1 row는 `legacy_minimum_contract` domain으로 변환해서 표시할 수 있다.

## 권장 UI 구조

현재 UI:

```text
1. 선택 후보 확인
2. 실전 검증 결과
3. 다음 단계
```

권장 V2 UI:

```text
1. Validation Profile
   - 목적 / 손실 감내도 / 운용 기간 / 상품 허용 범위 / 단순 대안 대비 기대
   - profile id, 주요 threshold, invariant blocker 안내
2. 후보 Source / Input Evidence
   - Source / settings / component
   - Data Trust / Real-Money / Compare / Mix replay inherited evidence
3. Practical Diagnostics Board
   - Asset Allocation / Exposure
   - Concentration / Overlap
   - Correlation / Risk Contribution
   - Performance / Benchmark / Rolling / Drawdown
   - Stress / Scenario
   - Macro / Sentiment Context
   - Alternative Portfolio Challenge
   - Cost / ETF Operability / Leveraged-Inverse Suitability
   - Sensitivity / Overfit
   - Monitoring Baseline Seed
4. Blockers / Review Gaps / Not Run / Intent Mismatch
5. 저장 및 Final Review 이동
```

검증 보드 card에는 아래가 필요하다.

| 필드 | 설명 |
|---|---|
| Domain | 검증 영역 |
| Status | `PASS / REVIEW / BLOCKED / NOT_RUN` |
| Key Metric | 핵심 숫자 하나 |
| Reason | 왜 이 상태인지 한 줄 |
| Evidence | 상세 table / chart expander |
| Profile Effect | 어떤 profile threshold 때문에 status가 바뀌었는지 |

버튼 구조:

| 버튼 | 동작 |
|---|---|
| `Validation Profile 만들기 / 수정` | 3~5개 질문으로 profile과 threshold를 생성 / 갱신 |
| `실전 진단 실행 / 갱신` | replay / exposure / correlation / rolling / stress / macro context / cost 계산 실행 |
| `검증 결과 저장` | `PRACTICAL_VALIDATION_RESULTS.jsonl` append |
| `Final Review로 이동` | blocker가 없을 때 가능. review gap은 남긴 채 이동 가능 |

중요한 UX:

- `NOT_RUN`을 초록색 통과처럼 보이면 안 된다.
- `BLOCKED`가 있어도 사용자가 raw source와 blocker reason은 볼 수 있어야 한다.
- profile 때문에 기준이 완화되거나 강화된 domain은 `Profile Effect`를 표시해야 한다.
- 사용자 의도와 후보 성격 mismatch는 route summary에서 먼저 보여주고, 관련 domain에도 연결해야 한다.
- Final Review 이동은 blocked 상태에서는 막거나, 최소한 selected decision route를 제한해야 한다.
- review gap이 있는 상태에서는 Final Review에서 `HOLD` 또는 `RE_REVIEW`가 자연스러운 선택지로 보이게 해야 한다.

## 구현 우선순위

### Slice 1. Validation Profile intake와 Practical Diagnostics board

목표:

- Practical Validation 진입 시 3~5개 질문으로 `Validation Profile`을 만든다.
- profile에서 threshold / domain weight / invariant blocker set을 생성한다.
- 기존 v1 check를 `Input Evidence Layer`로 감싼다.
- UI에서 `Input Evidence`와 `Practical Diagnostics`를 분리해서 표시한다.
- 아직 계산하지 못하는 domain은 `NOT_RUN`으로 명확히 표시한다.

주요 파일:

| 파일 | 변경 방향 |
|---|---|
| `app/web/backtest_practical_validation_helpers.py` | profile builder, threshold resolver, input evidence builder, diagnostic domain result builder 추가 |
| `app/web/backtest_practical_validation.py` | profile form, evidence board, diagnostics board UI 분리 |
| `app/web/backtest_final_review_helpers.py` | diagnostic result를 Final Review evidence로 읽기 |
| `app/web/runtime/portfolio_selection_v2.py` | schema version 확장 / loader compatibility |

### Slice 2. Asset allocation / exposure classification

목표:

- ticker를 broad asset class / ETF category / inverse / leveraged flag로 분류한다.
- 단일 전략은 100% component 포트폴리오로 보고 같은 exposure table을 만든다.
- mix는 target weight 기준으로 asset class / sector / theme proxy를 합산한다.
- profile 목표와 실제 exposure가 충돌하면 intent mismatch warning을 만든다.

주의:

- holdings look-through가 없으면 proxy classification으로 시작한다.
- 분류가 없으면 `NOT_RUN`이지 pass가 아니다.

### Slice 3. Replay / benchmark / portfolio curve parity

목표:

- selection source의 replay contract로 결과 curve를 재생성한다.
- snapshot summary와 replay summary delta를 표시한다.
- benchmark를 같은 기간으로 계산한다.

주의:

- 새 전략을 구현하지 않는다.
- 기존 runtime으로 가능한 전략만 replay한다.
- replay contract가 부족하면 `NOT_RUN` 또는 `REVIEW`로 둔다.

### Slice 4. Rolling / drawdown / stress / scenario

목표:

- result curve에서 monthly return을 만든다.
- rolling 12m / 36m, drawdown duration, stress window 결과를 계산한다.
- COVID crash, 2022 rate shock, banking stress, custom window를 table 중심으로 표시한다.

후속:

- hypothetical shock과 reverse stress test는 별도 advanced module로 둔다.

### Slice 5. Correlation / risk contribution / alternative challenge

목표:

- component monthly return matrix로 correlation과 rolling correlation을 계산한다.
- target weight 기준 volatility contribution과 drop-one impact를 표시한다.
- SPY, 60:40 proxy, cash-aware, All Weather-like baseline 대비 복잡성이 보상되는지 challenge table을 만든다.
- 사용자가 선택한 `alternative_success_metric`에 따라 challenge의 주요 metric을 바꾼다.

주의:

- 이 slice는 Compare 순위를 다시 고르는 기능이 아니다.
- baseline challenge는 자동 탈락 기준이 아니라 Final Review 근거다.

### Slice 6. Macro / sentiment context overlay

목표:

- NBER recession window와 FRED yield curve spread부터 붙인다.
- VIX와 CNN Fear & Greed는 optional connector로 둔다.
- status는 trade signal이 아니라 context review gap으로만 표시한다.

주의:

- sentiment overlay만으로 `BLOCKED`를 만들지 않는 것이 기본값이다.
- 외부 데이터 freshness와 source URL을 result row에 남긴다.

### Slice 7. Cost / turnover / ETF operability / leveraged-inverse suitability

목표:

- turnover가 runtime result에 있으면 사용하고, 없으면 rebalance weight history 필요 여부를 표시한다.
- 사용자가 cost bps를 입력할 수 있게 하고 gross/net summary를 나란히 보여준다.
- ETF investability는 price availability와 average dollar volume proxy부터 시작한다.
- leveraged / inverse ticker는 별도 suitability warning과 acknowledgement requirement로 분리한다.
- liquidity / price availability / 큰 leveraged-inverse mismatch는 profile과 무관한 invariant blocker 후보로 둔다.

주의:

- bid-ask spread / premium-discount는 데이터 수집 확장이 필요할 수 있다.
- 데이터가 없으면 `NOT_RUN`이지 pass가 아니다.

### Slice 8. Sensitivity / overfit audit

목표:

- strategy별 작은 perturbation set을 정의한다.
- mix는 weight +/- 5%p, component drop-one부터 시작한다.
- run_history 기반 trial count는 local audit로만 쓰고 commit 대상 registry로 만들지 않는다.

주의:

- 대규모 parameter search engine은 별도 설계가 필요하다.
- DSR / PBO는 후속 고급 검증으로 둔다.

### Slice 9. Final Review / Selected Dashboard 연결

목표:

- Final Review가 diagnostic result를 그대로 읽어 최종 판단 evidence로 보여준다.
- Selected Portfolio Dashboard의 review signal이 Practical Validation baseline seed를 읽을 수 있게 한다.

## 구현하지 않을 것

이번 설계는 아래를 만들지 않는다.

- 새 투자 전략 구현
- `finance/strategy.py`, `finance/engine.py`의 전략 로직 변경
- broker 연결
- 주문 초안
- 자동 리밸런싱
- live approval
- 투자 추천 문구
- 수익 보장 문구
- 기존 legacy JSONL 삭제

## 개발 시 주의할 파일 경계

예상 변경 파일:

| 파일 | 이유 |
|---|---|
| `app/web/backtest_practical_validation_helpers.py` | Practical Validation v2 domain result 생성 |
| `app/web/backtest_practical_validation.py` | 검증 보드 UI |
| `app/web/backtest_final_review_helpers.py` | Final Review diagnostic evidence 호환 |
| `app/web/backtest_final_review.py` | v2 evidence 표시 |
| `app/web/runtime/portfolio_selection_v2.py` | schema version / persistence helper |
| `app/web/final_selected_portfolio_dashboard_helpers.py` | 선정 후 monitoring signal이 v2 baseline을 읽게 할 경우 |
| `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md` | flow 문서 갱신 |
| `Reference > Guides` 관련 문서 / UI | 사용자-facing 단계 설명 갱신 |

명시 요청 전에는 아래를 건드리지 않는다.

- `finance/strategy.py`
- `finance/engine.py`
- `finance/data/*`
- `app/web/*` 중 설계 범위를 벗어난 페이지

## Threshold 설계

threshold는 처음부터 하나의 절대값으로 고정하지 않는다.
전략 목적과 사용자 risk tolerance가 다르기 때문이다.

권장 방식:

```text
Validation Profile
  - conservative_defensive
  - balanced_core
  - growth_aggressive
  - hedged_tactical
  - custom
```

초기 default 예시:

| 항목 | conservative_defensive | balanced_core | growth_aggressive |
|---|---:|---:|---:|
| minimum history | 60 months | 36 months | 24 months |
| rolling window | 36 months | 24 months | 12 months |
| benchmark win rate review line | 55% | 50% | 45% |
| cost shock | 20 bps one-way | 10 bps one-way | 5 bps one-way |
| concentration review | max weight > 60% | max weight > 75% | max weight > 90% |
| equity exposure review | > 70% | > 85% | > 95% |
| MDD review line | < -15% | < -25% | < -35% |

이 값은 hard-coded investment rule이 아니라 검증 board의 starting profile이다.
사용자가 Final Review에서 최종 판단해야 한다.

profile로도 바뀌지 않는 invariant blocker는 별도 목록으로 관리한다.
예를 들어 Data Trust hard blocker, active weight 합계 오류, 핵심 가격 부재,
거래 불가, execution boundary 위반, 큰 leveraged / inverse exposure의 목적 부재는
aggressive profile에서도 자동 pass로 바꾸지 않는다.

## Data Needs

| 데이터 | 현재 위치 / 가능성 | 필요 작업 |
|---|---|---|
| selection source snapshot | `PORTFOLIO_SELECTION_SOURCES.jsonl` | 이미 있음 |
| practical validation result | `PRACTICAL_VALIDATION_RESULTS.jsonl` | v2 schema 확장 |
| validation profile answers | Practical Validation UI 입력 | profile builder / persistence 필요 |
| profile threshold config | code constant 또는 config helper | profile별 threshold / weight / invariant blocker 관리 |
| result curve | runtime replay 또는 source snapshot | replay helper 필요 |
| benchmark curve | runtime replay / price loader | same-period 비교 helper 필요 |
| ticker category / asset class | 새 mapping 또는 ETF profile | asset allocation / exposure 진단 필요 |
| ETF leveraged / inverse flag | 새 mapping 또는 ETF profile | suitability warning 필요 |
| sector / theme / holdings | 현재 불확실 | MVP는 proxy, 후속 holdings look-through |
| component return matrix | price history에서 계산 가능 | correlation / risk contribution 계산 |
| rebalance dates / weights | 전략 runtime output 확인 필요 | turnover 계산용 output contract 검토 |
| ETF profile | `finance/data/asset_profile.py` 가능성 | expense / AUM / spread 데이터 coverage 확인 |
| average dollar volume | price history에서 계산 가능 | loader helper 필요 |
| bid-ask spread / premium-discount | 현재 불확실 | 데이터 수집 확장 필요 |
| macro regime data | FRED / NBER source | yield curve / recession window context |
| sentiment data | Cboe / CNN / optional provider | VIX / Fear & Greed context. trade signal 아님 |
| simple baseline curves | price loader / replay helper | SPY, 60:40, cash-aware, All Weather-like challenge |
| run trial count | local run_history | commit하지 않고 local audit로 사용 |

## Final Review와의 연결

Practical Validation v2가 끝난 뒤 Final Review는 아래를 보여줘야 한다.

| Final Review section | Practical Validation source |
|---|---|
| 최종 검증 요약 | diagnostic status summary |
| 사용자 검증 profile | profile id, answers, 주요 threshold, invariant blockers |
| 투자 가능 후보 / 보류 / 거절 / 재검토 판단 | route + hard blockers + review gaps |
| 사용자 의도와 후보 성격 mismatch | intent_mismatch_warnings |
| 최종 메모 | Final Review에서만 입력 |
| paper observation 기준 | monitoring_plan domain |
| Selected Dashboard baseline | replay / benchmark / drawdown / monitoring baseline seed |

Final Review selected decision은 다음 조건을 강하게 봐야 한다.

- `hard_blockers` 없음
- source replay 또는 snapshot-only limitation이 명확히 표시됨
- benchmark 기준이 있음
- monitoring plan이 있음
- `NOT_RUN` critical domain이 selected 판단을 방해하는지 사용자가 확인함

## Open Questions

구현 전에 결정할 질문:

| 질문 | 기본 제안 |
|---|---|
| selected route에서 `NOT_RUN` domain을 허용할 것인가? | 허용하되 Final Review에서 명시 확인 필요 |
| rolling window 최소 길이는? | balanced profile 36개월 시작 |
| cost assumption 기본값은? | balanced profile one-way 10 bps, expense ratio 있으면 추가 |
| ETF investability 데이터가 없으면 blocker인가? | 처음에는 `NOT_RUN`; leveraged/inverse 또는 price missing만 blocker |
| asset allocation profile은 어떻게 고를 것인가? | `conservative_defensive`, `balanced_core`, `growth_aggressive`, `hedged_tactical`, `custom`으로 시작 |
| profile 질문은 몇 개로 시작할 것인가? | 3~5개. 길어지면 Practical Validation 진입 장벽이 높아진다 |
| profile에 따라 12개 domain 중 일부를 생략할 것인가? | 생략하지 않는다. 가능한 domain은 모두 시도하고 threshold / weight / blocker 해석만 조정한다 |
| profile별 기준이 바뀌었음을 어떻게 설명할 것인가? | domain row에 `profile_effect`를 남기고 UI에 threshold used / reason을 표시한다 |
| profile로 무력화하면 안 되는 blocker는? | Data Trust, weight 합계, 핵심 가격 부재, 거래 불가, execution boundary, 큰 leveraged / inverse exposure의 목적 부재 |
| 사용자 의도와 후보 mismatch는 자동 탈락인가? | 기본은 `REVIEW`. Final Review에서 hold / re-review / reject 판단 근거로 쓴다 |
| sentiment overlay를 hard blocker로 쓸 것인가? | 기본적으로 쓰지 않는다. context review gap으로만 둔다 |
| sector / holdings look-through 데이터가 없으면 어떻게 할 것인가? | proxy classification으로 시작하고 missing coverage를 명시 |
| leveraged / inverse ETF는 언제 blocker인가? | 큰 비중, medium-long cadence, 목적 불명, acknowledgement 없음이면 blocker 후보 |
| simple baseline challenge에서 어떤 baseline을 우선할 것인가? | SPY, 60:40 proxy, cash-aware baseline부터 시작 |
| sensitivity는 모든 전략에 필수인가? | MVP에서는 `REVIEW / NOT_RUN`, 최종 selected hard blocker로는 두지 않음 |
| run_history trial count를 저장소에 남길 것인가? | 남기지 않음. local audit summary만 validation row에 넣을지 별도 결정 |
| stress window를 고정할 것인가? | 기본 window + custom window 입력을 같이 둠 |

## 추천 다음 작업

1. 먼저 Slice 1을 구현해 `Validation Profile`, `Input Evidence`, `Practical Diagnostics`를 분리해서 보여주게 한다.
2. Slice 2에서 asset allocation / exposure classification을 붙여 profile 목표와 후보 노출 mismatch를 표시한다.
3. Slice 3에서 replay / benchmark parity를 붙여 snapshot-only 한계를 줄인다.
4. Slice 4에서 rolling / drawdown / stress 계산을 profile threshold로 해석한다.
5. Slice 5 이후는 correlation / risk contribution, macro / sentiment, turnover / ETF data coverage를 확인한 뒤 진행한다.

이 순서가 좋은 이유는 사용자가 지금 가장 혼란스러워하는 부분이
"Practical Validation이 무엇을 검증하는지 보이지 않는다"는 점이기 때문이다.
먼저 domain board와 `NOT_RUN` 상태를 보이게 만들면,
아직 구현되지 않은 검증과 실제 통과한 검증이 UI에서 분리된다.
