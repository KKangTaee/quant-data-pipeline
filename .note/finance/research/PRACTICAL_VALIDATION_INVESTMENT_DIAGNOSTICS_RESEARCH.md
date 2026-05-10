# Practical Validation Investment Diagnostics Research

## 목적

이 문서는 `Backtest > Practical Validation`을 단순한 evidence 정리 화면이 아니라
실전 투자 진단 엔진으로 확장하기 위한 조사 / 설계 기준이다.

여기서 말하는 실전 투자 진단은 투자 추천, live approval, 주문 지시가 아니다.
Backtest Analysis에서 선택된 단일 전략, Compare 후보, weighted mix, saved mix가
Final Review로 올라가기 전에 아래 질문에 답하도록 돕는 검증 layer다.

```text
이 포트폴리오 후보는 백테스트 성과가 좋아 보이는 것 이상으로,
실제로 운용 후보로 검토할 만한 구조와 근거를 갖고 있는가?
```

## 핵심 결론

- Practical Validation은 앞 단계 검증 결과를 단순히 나열하는 단계가 아니다.
- 앞 단계의 Data Trust, Compare, Real-Money, Mix replay 결과는 입력 evidence로 상속한다.
- Practical Validation의 핵심은 그 evidence 위에서 portfolio-level 실전 진단을 새로 수행하는 것이다.
- 단일 전략도 1개 component 포트폴리오로 보고 동일한 진단을 실행한다.
- Mix는 component 성과 합성뿐 아니라 자산군 / 섹터 / 상관 / 위험기여 / regime 적합성을 함께 봐야 한다.
- sentiment, macro, yield curve, VIX, CNN Fear & Greed 같은 지표는 매수 / 매도 신호가 아니라 risk context overlay로 사용한다.
- leveraged / inverse ETF는 별도 suitability 경고와 보유 기간 / 리밸런싱 cadence 확인이 필요하다.
- Final Review는 Practical Validation의 진단 결과를 읽어 최종 선정 / 보류 / 거절 / 재검토 판단을 저장한다.

## 단계 정의

권장 사용자 흐름은 아래와 같다.

```text
1. Backtest Analysis
   - Single Strategy 또는 Compare / Weighted Mix로 후보를 만든다.
   - 1차 성과, Data Trust, benchmark, Compare 근거를 확인한다.
   - 통과 후보를 Practical Validation source로 보낸다.

2. Practical Validation
   - 앞 단계 evidence를 입력으로 읽는다.
   - 포트폴리오 구조, 집중도, 상관, 위험기여, macro / sentiment context,
     stress, ETF 운용 가능성, leveraged / inverse suitability, robustness를 진단한다.
   - 부족한 domain은 `NOT_RUN` 또는 `REVIEW`로 표시한다.
   - 투자 추천이 아니라 Final Review에 올릴 수 있는 검증 evidence를 만든다.

3. Final Review
   - Practical Validation 결과와 사용자의 최종 판단을 함께 읽는다.
   - `select / hold / reject / re-review` 판단과 최종 메모를 저장한다.

4. Selected Portfolio Dashboard
   - Final Review에서 선택된 후보를 사후 monitoring / recheck 대상으로 읽는다.
   - baseline 대비 성과, benchmark, drawdown, allocation drift 등을 추적한다.
```

## 앞 단계와의 중복 방지

Practical Validation은 아래 evidence를 다시 계산하지 않고 먼저 입력으로 받는다.

| Evidence | 1차 소유 단계 | Practical Validation 역할 |
|---|---|---|
| source id / settings / period | Backtest Analysis | candidate identity로 상속 |
| Data Trust / result warning | Single runtime / Compare / Mix board | hard blocker 또는 review gap으로 전파 |
| Real-Money gate / deployment blocker | runtime meta | 실전 후보 판단의 inherited warning으로 표시 |
| Compare 상대 순위 / 선택 근거 | Compare 5단계 보드 | selection rationale로 표시 |
| saved mix replay 가능 여부 | Saved Mix 검증 보드 | source freshness / replay parity의 입력으로 사용 |
| benchmark snapshot | runtime / Compare | 같은 기간 benchmark parity 계산의 입력으로 사용 |
| 기존 rolling / OOS status | runtime meta | 같은 원인을 이중 감점하지 않고 inherited evidence로 표시 |

Practical Validation에서 새로 계산하거나 새로 해석해야 하는 부분은 아래다.

| Practical Validation 신규 책임 | 이유 |
|---|---|
| portfolio-level asset allocation fit | 단일 run 성과만으로 주식 / 채권 / 현금 / 금 / 원자재 비중의 적합성을 알 수 없음 |
| concentration / overlap / exposure | ETF 여러 개를 섞으면 같은 섹터나 index에 중복 노출될 수 있음 |
| correlation / diversification / risk contribution | 비중 50:50이어도 실제 위험은 한쪽 asset이 대부분 차지할 수 있음 |
| regime / macro suitability | 과거 평균 성과가 좋아도 금리 / 인플레이션 / 경기 regime에 취약할 수 있음 |
| sentiment / risk-on-off overlay | 현재 시장이 극단적 risk-on 또는 risk-off인지 context로 확인해야 함 |
| stress / scenario diagnostics | 2020 crash, 2022 rate shock 같은 구간에서 구조적으로 무너지는지 확인 |
| alternative portfolio challenge | 더 단순한 benchmark나 60/40, All Weather류 대비 복잡성이 보상되는지 확인 |
| leveraged / inverse ETF suitability | daily objective, compounding, holding period mismatch가 실전 리스크가 될 수 있음 |
| cost / liquidity / ETF operability | bid-ask spread, expense, volume, premium / discount는 실전 성과에 직접 영향 |
| robustness / sensitivity / overfit audit | best-only 백테스트가 아니라 주변 설정에서도 견고한지 확인 |

## 조사 자료 요약

아래 자료는 설계 방향을 잡기 위한 reference다. 제품은 이 자료를 기계적으로 투자 규칙으로
고정하지 않고, 검증 domain과 disclosure 기준으로 사용한다.

| 자료 | 설계에 반영할 점 |
|---|---|
| [Investor.gov - Beginners' Guide to Asset Allocation, Diversification, and Rebalancing](https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset) | asset allocation은 투자 기간과 위험 감내도에 연결되고, diversification은 asset category 사이와 category 내부를 모두 봐야 한다. rebalancing은 원래 risk level로 되돌리는 수단이다. |
| [CFA Institute - Portfolio Risk and Return Part I](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/portfolio-risk-return-part-1) | portfolio risk는 개별 asset의 risk / return뿐 아니라 asset 간 correlation에 의해 결정된다. 저상관 asset 결합은 위험을 줄일 수 있다. |
| [CFA Institute - Measuring and Managing Market Risk](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/measuring-managing-market-risk) | stress test, scenario analysis, sensitivity measure, risk budget, position limit, scenario limit는 시장 위험 관리에서 실무적으로 쓰이는 framework다. |
| [CFA Institute RPC - Allocating Assets in Climates of Extreme Risk](https://rpc.cfainstitute.org/research/financial-analysts-journal/2012/allocating-assets-in-climates-of-extreme-risk-a-new-paradigm-for-stress-testing-portfolios) | stress testing은 historical / hypothetical covariance와 scenario construction에 민감하며, scenario 결과를 investment decision process에 연결할 수 있다. |
| [Federal Reserve SR 11-7 Model Risk Management](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm) | 모델 검증은 목적, 입력, 처리, reporting, validation, monitoring, documentation을 분리해야 한다. Practical Validation도 model output의 한계와 intended use를 명확히 해야 한다. |
| [Investor.gov - Updated Investor Bulletin: ETFs](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-24) | ETF는 NAV, market price, premium / discount, holdings, median bid-ask spread, fee / expense, 투자 목적과 risk profile 적합성을 확인해야 한다. |
| [Investor.gov - Fees and Expenses](https://www.investor.gov/index.php/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/updated) | 작은 비용도 장기 수익률에 큰 영향을 줄 수 있으므로 expense ratio, transaction fee, brokerage cost를 disclosure해야 한다. |
| [FINRA - Leveraged and Inverse ETPs](https://www.finra.org/investors/insights/lowdown-leveraged-and-inverse-exchange-traded-products) | leveraged / inverse ETP는 보통 일간 목표를 추구하고, 중장기 성과는 underlying index와 크게 달라질 수 있다. |
| [Cboe - Volatility Trading / VIX](https://www.cboe.com/tradable-products/volatility-trading/) | VIX는 미국 주식시장 기대 변동성의 대표 지표지만, VIX product는 buy-and-hold 투자로 쓰기 어렵다. Practical Validation에서는 sentiment / volatility context로 제한해 해석한다. |
| [CNN Fear & Greed Index](https://www.cnn.com/markets/fear-and-greed) | market momentum, price strength, breadth, put/call, junk bond demand, volatility, safe haven demand를 묶은 sentiment dashboard다. 독립 매매 신호가 아니라 context overlay로 둔다. |
| [FRED - 10Y minus 3M Treasury Spread](https://fred.stlouisfed.org/series/T10Y3M) | yield curve spread는 recession / macro risk context를 보는 대표 지표다. portfolio regime context에 사용하되 timing signal로 단정하지 않는다. |
| [NBER - US Business Cycle Expansions and Contractions](https://www.nber.org/research/data/us-business-cycle-expansions-and-contractions) | historical recession / expansion window를 stress window와 regime tagging에 사용할 수 있다. |
| [AQR - Risk Parity, Risk Management and the Real World](https://www.aqr.com/insights/research/white-papers/risk-parity-risk-management-and-the-real-world) | risk parity 관점은 "모든 asset이 matter하지만 어느 하나도 너무 많이 matter하지 않게" 하는 위험 분산 개념을 제공한다. |
| [Bridgewater - The All Weather Story](https://www.bridgewater.com/research-and-insights/the-all-weather-story) | growth / inflation surprise에 대한 asset class balance framework는 macro regime fit을 설명하는 reference로 쓸 수 있다. |

## Practical Diagnostics Module 설계

### 1. Input Evidence Layer

목적:

- Backtest Analysis가 만든 source와 upstream validation evidence를 한곳에 묶는다.
- 이 layer는 새 검증이 아니라 provenance / inherited evidence다.

입력:

- `selection_source_id`
- `source_kind`
- source settings / period / universe
- component list and target weights
- Data Trust status
- Real-Money / deployment status
- benchmark snapshot
- Compare rationale
- saved mix replay status

출력:

- `input_evidence_summary`
- `inherited_blockers`
- `inherited_review_gaps`
- `missing_source_fields`

### 2. Asset Allocation Fit

질문:

```text
이 후보는 주식, 채권, 현금, 금, 원자재, 대체자산 비중이 의도와 맞는가?
```

진단:

- component ticker를 asset class로 분류한다.
- equity / bond / cash / gold / commodity / real asset / inverse / leveraged 비중을 계산한다.
- 사용자 validation profile과 비교한다.
- 60/40, cash-aware, All Weather-like baseline과 노출 차이를 표시한다.

MVP 데이터:

- ticker category mapping
- target weight
- ETF category fallback

상태 예시:

| 상태 | 예시 |
|---|---|
| `PASS` | profile 대비 asset class 편중이 낮고 의도된 role이 명확함 |
| `REVIEW` | equity 90% 이상, bond / cash hedge 없음, 특정 theme ETF가 핵심 비중 |
| `BLOCKED` | asset class 분류 불가 component가 대부분이고 Final Review selected route를 만들려 함 |
| `NOT_RUN` | ticker category mapping이 아직 없음 |

### 3. Concentration / Overlap / Exposure

질문:

```text
겉으로는 여러 ETF지만 실제로는 같은 섹터, 같은 index, 같은 theme에 몰려 있지 않은가?
```

진단:

- max component weight
- top 2 / top 3 component cumulative weight
- sector / theme / geography / currency concentration
- ETF holdings overlap, 가능하면 top holding overlap
- benchmark와의 active exposure

MVP 데이터:

- ticker category
- ETF sector proxy
- component weights

후속 데이터:

- ETF holdings
- issuer / index provider
- look-through sector and top holding data

상태 예시:

| 상태 | 예시 |
|---|---|
| `PASS` | component 수와 exposure가 분산되어 있고 max weight가 profile 기준 안쪽 |
| `REVIEW` | QQQ, XLK, SMH처럼 technology / growth가 중복되어 포트폴리오 대부분을 차지 |
| `BLOCKED` | operator가 diversified mix로 저장했는데 실제 active component가 1개뿐임 |
| `NOT_RUN` | holdings / sector data가 없음 |

### 4. Correlation / Diversification / Risk Contribution

질문:

```text
비중은 분산되어 있어도 실제 위험도 분산되어 있는가?
```

진단:

- component return correlation matrix
- rolling correlation
- portfolio volatility contribution
- marginal risk contribution
- effective number of bets
- equity beta / benchmark beta

MVP 데이터:

- daily or monthly price history
- component target weights

상태 예시:

| 상태 | 예시 |
|---|---|
| `PASS` | component 간 correlation이 낮고 risk contribution이 한쪽에 과도하게 몰리지 않음 |
| `REVIEW` | capital weight는 50:50이지만 risk contribution의 80% 이상이 equity ETF에서 발생 |
| `BLOCKED` | 가격 곡선이 없어 risk calculation 자체가 불가능하고 투자 가능 판단을 요구함 |
| `NOT_RUN` | return history 부족 |

### 5. Regime / Macro Suitability

질문:

```text
이 후보는 현재와 과거의 경기 / 금리 / 인플레이션 regime에서 어떤 취약점을 가지는가?
```

진단:

- NBER recession window tagging
- yield curve spread context
- high yield spread context
- inflation / rate shock window
- growth / inflation 4-quadrant exposure narrative
- strategy cadence와 macro indicator refresh cadence 정합성

MVP 지표:

- FRED `T10Y3M` 또는 `T10Y2Y`
- NBER recession dates
- CPI / Fed Funds / 10Y yield, 필요 시 후속

상태 예시:

| 상태 | 예시 |
|---|---|
| `PASS` | 여러 stress / regime window에서 목적에 맞는 방어 또는 회복 evidence가 있음 |
| `REVIEW` | rising-rate / inflation shock window에서 benchmark보다 크게 악화 |
| `BLOCKED` | 후보 목적이 macro defensive인데 해당 stress window evidence가 전혀 없음 |
| `NOT_RUN` | macro data connector 미구현 |

### 6. Sentiment / Risk-On-Off Overlay

질문:

```text
현재 시장 risk context가 후보 포트폴리오의 진입 / 관찰 판단에 중요한 경고를 주는가?
```

진단:

- VIX level and change
- CNN Fear & Greed bucket
- put/call proxy, 가능하면 후속
- junk bond demand / credit spread proxy
- safe haven demand proxy
- market breadth or momentum context

주의:

- sentiment overlay는 trade trigger가 아니다.
- `Extreme Fear`가 자동 매수 신호가 아니고, `Extreme Greed`가 자동 매도 신호도 아니다.
- Final Review에서 "현재 시장 context상 추가 관찰 필요"라는 evidence로만 사용한다.

상태 예시:

| 상태 | 예시 |
|---|---|
| `PASS` | sentiment가 극단적이지 않거나 strategy 목적과 충돌하지 않음 |
| `REVIEW` | high equity / high beta portfolio인데 greed / low-vol complacency context가 강함 |
| `BLOCKED` | sentiment 단독으로 blocker 처리하지 않는 것을 기본값으로 함 |
| `NOT_RUN` | 외부 sentiment data connector 미구현 |

### 7. Stress / Scenario Diagnostics

질문:

```text
역사적 또는 가상 충격에서 포트폴리오가 감당 가능한 수준으로 작동하는가?
```

진단:

- COVID crash
- 2022 inflation / rate shock
- 2023 banking stress
- custom stress window
- hypothetical equity -20%, bond yield +100 bps, credit spread +300 bps, USD shock
- scenario별 return, MDD, recovery, benchmark spread

MVP:

- historical stress window table
- candidate vs benchmark return / MDD
- 기간이 겹치지 않으면 `NOT_RUN`, 실패가 아님

후속:

- factor-based hypothetical shock
- covariance scenario
- reverse stress test

### 8. Alternative Portfolio Challenge

질문:

```text
이 후보는 더 단순한 포트폴리오보다 복잡성을 감수할 만큼 나은가?
```

비교 후보:

- SPY 또는 broad equity benchmark
- 60/40 proxy
- equal weight simple mix
- cash-aware defensive baseline
- All Weather-like proxy
- minimum volatility or risk-parity-like proxy, 후속

출력:

- candidate vs baseline CAGR
- MDD improvement
- Sharpe / Sortino improvement
- turnover / complexity cost
- "복잡성이 보상되는가" review note

이 module은 후보를 자동 탈락시키는 용도가 아니라,
Final Review에서 "왜 이 후보여야 하는가"를 묻는 장치다.

### 9. Leveraged / Inverse ETF Suitability

질문:

```text
leveraged / inverse ETF가 포함되어 있다면, 보유 기간과 리밸런싱 방식이 상품 구조와 맞는가?
```

진단:

- leveraged / inverse ticker detection
- daily objective disclosure
- medium / long-term holding warning
- volatility compounding risk
- strategy rebalance cadence mismatch
- explicit operator acknowledgement requirement

상태 예시:

| 상태 | 예시 |
|---|---|
| `PASS` | leveraged / inverse 없음 |
| `REVIEW` | inverse hedge가 작고 명시적 역할이 있음. 그래도 확인 필요 |
| `BLOCKED` | leveraged / inverse component가 큰 비중인데 목적 / holding period / acknowledgement 없음 |
| `NOT_RUN` | ticker classification 미구현 |

### 10. Operability / Cost / Liquidity

질문:

```text
실제로 거래하고 유지할 수 있는 ETF / 비용 구조인가?
```

진단:

- latest price availability
- 20d average dollar volume proxy
- expense ratio
- bid-ask spread, 후속
- premium / discount, 후속
- turnover-based cost drag
- rebalance frequency and estimated annual trades

MVP:

- 가격 존재
- average dollar volume proxy
- user-entered one-way cost bps
- expense ratio 있으면 반영, 없으면 `NOT_RUN`

### 11. Robustness / Sensitivity / Overfit

질문:

```text
이 후보는 특정 설정 하나에서만 우연히 좋아 보이는가?
```

진단:

- nearby parameter perturbation
- mix weight +/- 5%p
- drop-one component test
- selected source rank in compare set
- local run_history trial count, commit 대상 아님
- Deflated Sharpe Ratio / PBO는 후속 advanced module

상태 예시:

| 상태 | 예시 |
|---|---|
| `PASS` | 주변 설정 / drop-one 결과가 급격히 무너지지 않음 |
| `REVIEW` | original setting만 유난히 좋고 주변 설정은 약함 |
| `BLOCKED` | 대규모 best-only search인데 OOS / sensitivity evidence가 전혀 없음 |
| `NOT_RUN` | perturbation runner 미구현 |

### 12. Monitoring Baseline Seed

질문:

```text
Final Review 이후 Selected Portfolio Dashboard가 무엇을 기준으로 재검토할 것인가?
```

진단:

- baseline CAGR / MDD / volatility
- benchmark ticker / period
- review cadence
- recheck trigger
- allocation drift threshold
- data freshness trigger

주의:

- 이 module은 Pre-Live record를 새로 만드는 단계가 아니다.
- Final Review selected row와 Selected Portfolio Dashboard가 읽을 baseline seed만 만든다.

## 단일 포트폴리오와 Mix 처리

단일 전략:

- 1개 component, weight 100%인 포트폴리오로 본다.
- asset allocation / concentration은 "단일 전략으로 의도된 집중인가"를 해석한다.
- ETF 하나로 구성되어도 ETF 내부 holdings / sector concentration은 가능하면 look-through로 본다.
- benchmark challenge와 stress / sentiment / operability는 mix와 동일하게 실행한다.

Mix:

- component별 upstream evidence를 상속한다.
- target weight를 기준으로 asset class / sector / correlation / risk contribution을 합산한다.
- component period가 다르면 same-period alignment를 강하게 표시한다.
- mix-level stress, alternative portfolio challenge, drop-one sensitivity를 실행한다.

## 저장 구조 제안

기존 Clean V2의 `PRACTICAL_VALIDATION_RESULTS.jsonl`을 확장하는 것이 우선이다.
새 registry를 계속 늘리는 것보다 하나의 Practical Validation result row 안에
domain별 evidence를 넣는 방식이 낫다.

권장 row shape:

```json
{
  "schema_version": "practical_validation_diagnostics_v1",
  "validation_id": "pv_...",
  "selection_source_id": "selection_...",
  "source_kind": "single_strategy | compare_candidate | weighted_mix | saved_mix",
  "created_at": "...",
  "validation_profile": "balanced",
  "route": "READY_FOR_FINAL_REVIEW | NEEDS_REVIEW | BLOCKED",
  "input_evidence": {
    "data_trust": {},
    "real_money_gate": {},
    "compare_rationale": {},
    "mix_replay": {}
  },
  "diagnostics": [
    {
      "domain": "asset_allocation_fit",
      "status": "PASS | REVIEW | BLOCKED | NOT_RUN",
      "origin": "pv_computed",
      "summary": "...",
      "metrics": {},
      "limitations": []
    }
  ],
  "hard_blockers": [],
  "review_gaps": [],
  "not_run_critical_domains": [],
  "final_review_handoff": {
    "allowed": true,
    "required_confirmations": []
  },
  "execution_boundary": {
    "investment_recommendation": false,
    "live_approval": false,
    "order_instruction": false
  }
}
```

## MVP 개발 우선순위

### MVP 1. Evidence intake와 diagnostic board

- 현재 v1 check를 domain board로 감싼다.
- input evidence와 신규 diagnostic domain을 UI에서 분리한다.
- 아직 구현되지 않은 domain은 `NOT_RUN`으로 표시한다.

### MVP 2. Asset allocation / concentration / ticker classification

- ticker -> asset class / broad category mapping을 만든다.
- component weight 기반 exposure table을 표시한다.
- leveraged / inverse detection을 먼저 넣는다.

### MVP 3. Portfolio curve 기반 diagnostics

- replay 또는 source curve에서 monthly returns를 만든다.
- rolling, drawdown, stress window, benchmark same-period 비교를 계산한다.
- 단일과 mix를 같은 portfolio curve interface로 처리한다.

### MVP 4. Correlation / risk contribution / drop-one

- component monthly return matrix를 만든다.
- correlation, volatility contribution, drop-one sensitivity를 표시한다.
- data가 부족하면 `NOT_RUN`을 명확히 표시한다.

### MVP 5. Macro / sentiment context overlay

- FRED yield curve / NBER recession window부터 붙인다.
- VIX와 CNN Fear & Greed는 optional connector로 둔다.
- output은 trade signal이 아니라 context warning이다.

### MVP 6. ETF operability / cost expansion

- price availability, ADV proxy, expense ratio부터 시작한다.
- bid-ask spread, premium / discount, holdings look-through는 데이터 수집 확장으로 분리한다.

## UI 설계 원칙

- `Input Evidence`와 `Practical Diagnostics`를 화면에서 분리한다.
- 맨 위에는 route와 blocker / review gap / not-run critical domain 요약을 보여준다.
- 각 module은 `왜 보는가`, `결과`, `한계`, `Final Review에서 확인할 점`을 짧게 표시한다.
- sentiment / macro는 버튼 이름이나 status에서 투자 지시처럼 보이면 안 된다.
- `Run Practical Diagnostics` 이후에는 `Final Review로 보내기`가 가능하되,
  required confirmation이 있으면 Final Review에서 확인하도록 넘긴다.

## 구현하지 않을 것

- 새 전략 구현
- broker 연결
- 주문 생성
- 자동 매수 / 매도 시그널
- 사용자 개인 재무상황에 대한 적합성 판단
- sentiment 기반 자동 allocation 변경
- live approval

## 남은 설계 질문

| 질문 | 기본 제안 |
|---|---|
| sentiment overlay를 hard blocker로 쓸 것인가? | 기본적으로 쓰지 않는다. context review gap으로만 둔다. |
| asset allocation profile을 어떻게 고를 것인가? | conservative / balanced / growth / custom profile을 둔다. |
| sector / holdings look-through data가 없으면 어떻게 할 것인가? | proxy classification으로 시작하고 missing coverage를 `NOT_RUN`으로 표시한다. |
| leveraged / inverse ETF는 언제 blocker인가? | 큰 비중, medium-long cadence, 목적 불명, acknowledgement 없음이면 blocker 후보로 둔다. |
| Final Review selected route에서 `NOT_RUN`을 허용할 것인가? | 허용하되 critical domain이면 Final Review에서 명시 확인을 요구한다. |
| 기존 Phase 31 / 32 검증과 충돌하지 않는가? | Clean V2에서는 Practical Validation 안의 module로 흡수하고, 기존 문서는 legacy / prior implementation reference로 둔다. |
