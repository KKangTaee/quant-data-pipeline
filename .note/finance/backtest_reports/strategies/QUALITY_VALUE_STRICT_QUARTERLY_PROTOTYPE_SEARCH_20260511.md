# Quality / Value Strict Quarterly Prototype Candidate Search - 2026-05-11

## 목적

Quality, Value, Quality + Value 계열에서 `SPY`보다 성과가 좋고, 리밸런싱 주기가 3개월 이내이며, 포지션 수가 10개 내외인 실전 후보 탐색 대상을 찾는다.

이 문서는 투자 추천이나 live approval이 아니라, 기존 DB-backed runtime으로 확인한 후보 탐색 / 검증 자료다.

## 기간 / Universe

- 실행일: `2026-05-11`
- 기간: `2016-01-01 ~ 2026-05-05`
- 비교 정렬 기간: 월별 공통 정렬 기준 `2016-01-29 ~ 2026-05-01`
- Runtime:
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
- Universe:
  - 1차: `US Statement Coverage 100`
  - 민감도 확인: `US Statement Coverage 300`
  - `Historical Dynamic PIT Universe`
- 공통 조건:
  - `option = month_end`
  - `top_n = 10` 중심, 보조로 `top_n = 8 / 12`
  - `rebalance_interval = 1 / 3`
  - `weighting_mode = equal_weight` 중심, 일부 `rank_tapered` 확인
  - trend filter / market regime overlay는 보조 변형으로만 확인

## Factor Set

### Quality

- `q_default`: `roe`, `roa`, `net_margin`, `asset_turnover`, `current_ratio`
- `q_profit`: `roe`, `roa`, `operating_margin`, `asset_turnover`, `current_ratio`
- `q_def`: `roe`, `roa`, `cash_ratio`, `debt_to_assets`

### Value

- `v_default`: `book_to_market`, `earnings_yield`, `sales_yield`, `ocf_yield`, `operating_income_yield`
- `v_expanded`: `book_to_market`, `earnings_yield`, `sales_yield`, `ocf_yield`, `operating_income_yield`, `psr`
- `v_price`: `book_to_market`, `earnings_yield`, `sales_yield`, `pcr`, `por`, `per`

## Summary

### Focused Sweep - Coverage 100 / Top 10 / 3개월 리밸런싱

| Family | Factor Set | CAGR | SPY CAGR | Excess | MDD | SPY MDD | Sharpe | 36M Rolling Win vs SPY | 해석 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Value | `v_price` | `15.08%` | `13.67%` | `+1.41%` | `-38.83%` | `-24.90%` | `0.59` | `55%` | SPY 초과지만 drawdown 과다 |
| Quality + Value | `q_profit + v_price` | `14.40%` | `13.67%` | `+0.73%` | `-37.73%` | `-24.90%` | `0.59` | `47%` | 초과 성과가 약하고 rolling 우위가 약함 |
| Quality + Value | `q_def + v_default` | `13.09%` | `13.67%` | `-0.58%` | `-37.06%` | `-24.90%` | `0.57` | `40%` | 탈락 |
| Quality | `q_def` | `12.06%` | `13.67%` | `-1.61%` | `-30.75%` | `-24.90%` | `0.53` | `43%` | 탈락 |
| Value | `v_default` | `11.32%` | `13.67%` | `-2.35%` | `-35.93%` | `-24.90%` | `0.51` | `52%` | 탈락 |

3개월 리밸런싱만 보면 `v_price`가 유일하게 SPY CAGR을 넘었지만, MDD가 `-38.83%`로 너무 깊어서 바로 실전 후보로 보기는 어렵다.

### 월별 리밸런싱 후보

| Candidate | Universe | CAGR | SPY CAGR | QQQ CAGR | MDD | SPY MDD | QQQ MDD | 36M Win vs SPY | Last Selected |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Value `v_price`, top 10, monthly | Coverage 100 | `36.12%` | `13.67%` | `19.97%` | `-39.09%` | `-24.90%` | `-33.06%` | `100%` | `CMCSA`, `TMUS`, `MCD`, `GILD`, `UNP`, `CRM`, `LMT`, `UBER`, `MO`, `INTC` |
| Value `v_price`, top 10, monthly | Coverage 300 | `29.79%` | `13.67%` | `19.97%` | `-24.26%` | `-24.90%` | `-33.06%` | `100%` | `CMCSA`, `DAL`, `PCG`, `UAL`, `CI`, `MPC`, `TGT`, `OKE`, `EOG`, `EXC` |
| Q+V `q_profit + v_price`, top 10, monthly | Coverage 300 | `30.15%` | `13.67%` | `19.97%` | `-30.11%` | `-24.90%` | `-33.06%` | `100%` | `EOG`, `LNG`, `MPC`, `CTSH`, `PYPL`, `UPS`, `CMCSA`, `TGT`, `FCX`, `GILD` |
| Q+V `q_def + v_default`, top 10, monthly | Coverage 300 | `23.83%` | `13.67%` | `19.97%` | `-33.17%` | `-24.90%` | `-33.06%` | `96%` | `EOG`, `UAL`, `DAL`, `FCX`, `LNG`, `UPS`, `OKE`, `CMI`, `EBAY`, `TGT` |

가장 의미 있는 후보는 `Value v_price / Coverage 300 / top 10 / monthly`다. Coverage 100보다 CAGR은 낮지만 MDD가 `-24.26%`로 SPY와 거의 같고, QQQ보다 CAGR이 높으며 MDD는 더 낮다. 즉 현재 탐색 기준에서는 Coverage 300 쪽이 더 현실적인 후보다.

### Subperiod Check - 월별 상위 후보

| Candidate | 2016-2019 Excess vs SPY | 2020-2021 Excess vs SPY | 2022 Excess vs SPY | 2023-2026 Excess vs SPY | 해석 |
|---|---:|---:|---:|---:|---|
| Value `v_price`, Coverage 100 | `+29.87%` | `+30.21%` | `-8.75%` | `+22.08%` | 2022 금리 충격에서 취약 |
| Q+V `q_profit + v_price`, Coverage 100 | `+23.69%` | `+36.41%` | `-9.82%` | `+22.64%` | 강한 수익, 2022 방어 약함 |
| Q+V `q_def + v_default`, Coverage 100 | `+8.93%` | `+26.41%` | `-5.94%` | `+11.93%` | 상대적으로 균형형이지만 Coverage 300에서는 MDD가 커짐 |

## Turnover / Cost Sanity Check

Runtime 자체에는 quarterly prototype용 transaction cost hardening이 충분히 붙어 있지 않아서, 결과 curve에 비용이 반영된 것은 아니다. 대신 선택 종목 변경 기준으로 equal-weight one-way turnover를 사후 추정했다.

| Candidate | Rebalance Events | Avg One-Way Turnover | Annualized One-Way Turnover | 10 bps Cost Drag | 25 bps Cost Drag |
|---|---:|---:|---:|---:|---:|
| Value `v_price`, Coverage 100, monthly | `125` | `15.48%` | `1.87x` | `0.19%/yr` | `0.47%/yr` |
| Value `v_price`, Coverage 300, monthly | `125` | `18.95%` | `2.29x` | `0.23%/yr` | `0.57%/yr` |
| Q+V `q_profit + v_price`, Coverage 300, monthly | `125` | `25.97%` | `3.14x` | `0.31%/yr` | `0.78%/yr` |
| Q+V `q_def + v_default`, Coverage 300, monthly | `125` | `25.73%` | `3.11x` | `0.31%/yr` | `0.78%/yr` |

비용 추정만으로 월별 후보의 초과 CAGR이 사라지지는 않는다. 다만 실제 체결 슬리피지, 세금, liquidity capacity, 월별 재계산 시점의 factor availability lag를 별도로 검증해야 한다.

## Interpretation

1. 순수 Quality quarterly prototype은 이번 조건에서 SPY를 넘지 못했다.
2. 기본 Value factor도 SPY를 넘지 못했고, `pcr / por / per`를 포함한 price-ratio value set이 성과를 만들었다.
3. 월별 리밸런싱에서는 `Value v_price`와 `Q+V q_profit + v_price`가 강하게 보이지만, 너무 강한 성과는 오히려 검증 우선순위를 높여야 한다.
4. Coverage 100의 `Value v_price monthly`는 CAGR이 가장 높지만 MDD가 `-39.09%`라서 단독 실전 후보로는 공격적이다.
5. Coverage 300의 `Value v_price monthly`는 CAGR `29.79%`, MDD `-24.26%`로 이번 탐색에서 가장 균형이 좋다.
6. Coverage 300의 Q+V 후보들은 CAGR은 높지만 MDD가 SPY보다 크고, 최근 편입 종목이 에너지 / 운송 / 경기민감 성격으로 몰릴 수 있어 exposure 검증이 필요하다.

## Program / Validation Gaps Found

이번 탐색에서 좋은 후보를 찾는 과정에서 드러난 부족한 부분은 아래와 같다.

1. `Strict Quarterly Prototype`은 아직 full Real-Money hardening이 약하다.
   - annual strict 계열과 달리 min price, min history, avg dollar volume, transaction cost, benchmark contract, underperformance / drawdown guardrail이 완전한 promotion gate로 붙어 있지 않다.
2. 월별 리밸런싱 후보의 비용은 runtime curve에 직접 반영되지 않는다.
   - turnover / cost는 사후 추정만 했고, net CAGR / net MDD gate가 필요하다.
3. quarterly shadow factor의 PIT 검증이 더 필요하다.
   - monthly rebalance에서 quarterly statement factor를 사용할 때 `latest_available_at`, filing acceptance, price-based ratio 계산 시점이 정확히 과거 시점만 쓰는지 별도 audit view가 필요하다.
4. universe sensitivity가 자동화되어 있지 않다.
   - Coverage 100과 Coverage 300 결과가 크게 달라진다. candidate search 단계에서 universe size perturbation을 자동으로 보여줘야 한다.
5. factor 전략용 benchmark set이 부족하다.
   - 이번에는 수동으로 `SPY`, `QQQ`, `VTV`, `QUAL`을 비교했다. UI/runtime에서 factor strategy benchmark pack으로 제공하는 것이 좋다.
6. sector / industry exposure 검증이 부족하다.
   - Coverage 300 후보의 최근 종목은 에너지, 항공, 통신, 경기민감 종목 비중이 높다. sector concentration / macro exposure를 Practical Validation에서 실제 데이터로 확인해야 한다.
7. stress / regime 해석이 부족하다.
   - 2022 inflation / rate shock 구간에서 월별 상위 후보가 SPY보다 크게 밀렸다. stress window, rate-sensitive exposure, VIX / credit spread / yield curve connector가 후속으로 필요하다.
8. overfit audit이 부족하다.
   - factor set, top_n, universe, rebalance interval을 여러 번 바꾸며 찾은 후보이므로, trial count와 sensitivity perturbation을 validation row에 남겨야 한다.
9. 기존 GTAA / Equal Weight mix와의 결합 검증이 아직 없다.
   - Quality/Value 후보가 독립적으로 좋아 보여도, 기존 GTAA + EW 조합에 붙였을 때 correlation, risk contribution, drawdown contribution이 개선되는지 봐야 한다.

## Candidate Status

| Candidate | Candidate Search | Validation | Real-Money | Deployment | 판단 |
|---|---|---|---|---|---|
| Value `v_price`, Coverage 300, top 10, monthly | `PASS` | `REVIEW_REQUIRED` | `NOT_EVALUATED` | `NOT_APPROVED` | 다음 Practical Validation 우선 후보 |
| Q+V `q_profit + v_price`, Coverage 300, top 10, monthly | `PASS` | `REVIEW_REQUIRED` | `NOT_EVALUATED` | `NOT_APPROVED` | 공격형 대안 후보 |
| Q+V `q_def + v_default`, Coverage 300, top 10, monthly | `WATCH` | `REVIEW_REQUIRED` | `NOT_EVALUATED` | `NOT_APPROVED` | 균형형 보조 후보 |
| Value `v_price`, Coverage 100, top 10, monthly | `WATCH` | `REVIEW_REQUIRED` | `NOT_EVALUATED` | `NOT_APPROVED` | raw 성과는 강하지만 MDD 과다 |
| 3개월 리밸런싱 후보군 | `WEAK_PASS / WATCH` | `REVIEW_REQUIRED` | `NOT_EVALUATED` | `NOT_APPROVED` | SPY 초과가 약하고 drawdown이 큼 |

## Next Action

1. 우선 후보는 `Value v_price / Coverage 300 / top 10 / monthly`로 둔다.
2. 다음 검증은 후보 등록이 아니라 Practical Validation 성격의 follow-up으로 진행한다.
3. follow-up에서 반드시 볼 항목:
   - quarterly shadow factor PIT audit
   - net-of-cost backtest
   - Coverage 100 / 300 / 500 universe sensitivity
   - `top_n = 8 / 10 / 12 / 14` sensitivity
   - monthly vs 2-month vs quarterly rebalance sensitivity
   - 2022 inflation / rate shock stress
   - sector / industry concentration
   - 기존 GTAA + Equal Weight mix에 10~30% sleeve로 붙였을 때 portfolio-level MDD / Sharpe / rolling excess 변화

