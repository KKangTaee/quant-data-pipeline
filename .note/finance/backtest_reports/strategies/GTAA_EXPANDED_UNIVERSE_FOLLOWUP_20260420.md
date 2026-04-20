# GTAA Expanded Universe Follow-Up - 2026-04-20

## 목적

이 문서는 2026-04-20 사용자 요청에 따라 기존 `GTAA` 후보의 약점인
작은 ticker universe를 보강해 다시 백테스트한 결과를 정리한다.

기존 추천 후보는 `SPY / QQQ / GLD / IEF` 4개 중 `Top = 2`를 고르는 방식이었다.
성과와 validation은 좋았지만, universe가 너무 compact해서 다음 약점이 있었다.

- 주식 축이 사실상 미국 대형주와 Nasdaq 성장주 중심이다.
- 채권 축이 `IEF` 또는 `LQD` 중심이라 duration 분산이 충분하지 않다.
- ETF 수가 적어 한두 개 asset의 최근 momentum에 allocation이 크게 흔들린다.
- broad style / international / sector ETF를 넣고 싶어도 current ETF profile snapshot에서 AUM / spread coverage가 부족한 ticker가 많다.

이번 follow-up의 목표는 preset에 묶이지 않고 ticker를 늘리되,
`Promotion = hold`가 아닌 실제 후보가 나오는지 확인하는 것이다.

## 결론 요약

| 판단 | Universe | Top | Interval | Score | CAGR | MDD | Sharpe | Promotion | Shortlist | Deployment |
|---|---|---:|---:|---|---:|---:|---:|---|---|---|
| 기존 기본 후보 유지 | `SPY, QQQ, GLD, IEF` | `2` | `4` | `1M / 3M` | `18.09%` | `-8.39%` | `3.31` | `real_money_candidate` | `paper_probation` | `paper_only` |
| 기존 낮은 MDD 대안 유지 | `SPY, QQQ, GLD, IEF, LQD` | `2` | `6` | `1M / 3M` | `16.59%` | `-4.50%` | `3.94` | `real_money_candidate` | `paper_probation` | `paper_only` |
| 신규 확장 real-money 후보 | `SPY, QQQ, GLD, IEF, LQD, TLT` | `1` | `8` | `1M / 3M / 6M` | `21.50%` | `-6.49%` | `3.66` | `real_money_candidate` | `paper_probation` | `paper_only` |
| 신규 확장 Top-2 후보 | `SPY, QQQ, GLD, IEF, LQD, TLT` | `2` | `4` | `1M / 3M / 6M` | `16.79%` | `-8.39%` | `3.01` | `production_candidate` | `watchlist` | `watchlist_only` |

핵심 결론은 다음과 같다.

- `TLT`를 추가한 6개 clean ETF universe는 보강 방향으로 타당하다.
- 다만 `Top = 2`를 유지하면 current runtime 기준 `real_money_candidate`까지는 못 올라가고 `production_candidate / watchlist_only`에 머문다.
- `real_money_candidate`를 엄격하게 요구하면 신규 확장 후보는 `Top = 1`, `Interval = 8`, `Score = 1M / 3M / 6M` 조합이다.
- 따라서 지금 당장 기본 후보를 교체하기보다는:
  - 기본 추천은 기존 `SPY / QQQ / GLD / IEF`, `Top = 2`를 유지한다.
  - 확장 universe 실험 후보는 `SPY / QQQ / GLD / IEF / LQD / TLT`, `Top = 1`을 paper probation 후보로 추가한다.
  - 확장 `Top = 2`는 투자 후보가 아니라 watchlist-only 개선 대상으로 둔다.

## 백테스트 계약

| 항목 | 값 |
|---|---|
| Runtime | `app.web.runtime.backtest.run_gtaa_backtest_from_db` |
| Data Source | repo DB-backed adjusted daily price runtime |
| Start Input | `2016-01-01` |
| Effective Result Window | `2016-01-29 ~ 2026-04-17` |
| Timeframe | `1d` |
| Option | `month_end` |
| Benchmark | `SPY` sampled benchmark |
| Minimum Price | `5.0` |
| Transaction Cost | `10 bps` |
| Min ETF AUM Gate | `$1.0B` |
| Max Bid-Ask Spread Gate | `0.50%` |
| Market Regime | `off` |
| Crash Guardrail | `off` |
| Risk-Off Defensive Tickers | `TLT, IEF, LQD, BIL` |

주의할 점:

- `SPY Benchmark`는 raw daily buy-and-hold가 아니라, GTAA 결과와 같은 sampled frequency surface에서 비교된다.
- ETF operability gate는 current profile snapshot 기준이다. point-in-time AUM / spread history가 아니다.
- 이 문서는 투자 조언이 아니라 repo runtime 기준 후보 검토 기록이다. deployment는 모두 live가 아닌 `paper_only` 또는 `watchlist_only`다.

## 기존 후보의 부족한 부분

### 1. Universe가 너무 작다

기존 기본 후보는 `SPY / QQQ / GLD / IEF` 네 개만 사용한다.
성과는 좋지만, 전략이 실제로 선택할 수 있는 asset class가 좁다.

특히 주식 쪽은:

- 미국 대형주 broad market: `SPY`
- 미국 대형 성장 / Nasdaq: `QQQ`

로 거의 고정된다.

방어 자산도:

- 금: `GLD`
- 중기 국채: `IEF`

정도로 단순하다.

### 2. 금리 duration 축이 부족하다

기존 후보의 채권 축은 `IEF`가 핵심이다.
하지만 GTAA에서는 금리 하락 또는 경기 stress 국면에서 long-duration Treasury가 별도 역할을 할 수 있다.

그래서 이번 follow-up에서는 current ETF profile과 price coverage가 깨끗한 `TLT`를 추가했다.

### 3. `Top = 2`가 항상 확장 효과를 살리지는 못한다

6개 universe로 넓혀도 `Top = 2`를 고정하면 validation gate가 `watch`로 내려갔다.
즉 ticker 수를 늘리는 것만으로 자동 개선되지는 않았다.

반대로 `Top = 1`, `Interval = 8`에서는 확장 universe가 강하게 작동했다.
이 조합은 asset을 더 많이 들고 가는 후보가 아니라, 더 넓은 후보군에서 하나를 고르는 concentrated momentum 후보에 가깝다.

## 확장 universe 설계

### Clean core로 유지한 ticker

| Ticker | 역할 |
|---|---|
| `SPY` | 미국 대형주 broad market |
| `QQQ` | 미국 대형 성장 / Nasdaq |
| `GLD` | 금 |
| `IEF` | 중기 미국 국채 |
| `LQD` | 투자등급 회사채 |
| `TLT` | 장기 미국 국채 |

`TLT`를 추가한 이유는 다음과 같다.

- current DB profile snapshot에서 AUM / spread coverage가 정상이다.
- 기존 `IEF`보다 duration이 길어 금리 하락 국면 반응이 다르다.
- ETF universe를 늘리면서도 current operability gate를 깨지 않는다.

### Watch로만 본 ticker

| Ticker / Group | 보류 이유 |
|---|---|
| `BIL` | current DB snapshot에서 bid/ask spread data가 `0 / 0` 형태로 들어와 operability가 `watch`로 내려간다. |
| `IWD, IWM, VUG` | style / size 확장으로 의미는 있지만 current ETF profile data coverage가 부족하다. |
| `EFA, VNQ, XLE` | international / REIT / sector 확장 후보지만 current profile gap 때문에 `hold`로 밀린다. |

따라서 이번 추천은 `SPY / QQQ / GLD / IEF / LQD / TLT` 6개를 clean expanded core로 제한한다.

## 상세 결과

### A. 기존 기본 후보 재확인

| 항목 | 값 |
|---|---|
| Universe | `SPY, QQQ, GLD, IEF` |
| Top | `2` |
| Interval | `4` |
| Score | `1M / 3M` |
| Risk-Off | `defensive_bond_preference` |
| End Balance | `54,631.16` |
| CAGR | `18.09%` |
| MDD | `-8.39%` |
| Sharpe | `3.31` |
| Benchmark CAGR | `13.56%` |
| Net CAGR Spread | `+4.53%p` |
| Promotion | `real_money_candidate` |
| Shortlist | `paper_probation` |
| Deployment | `paper_only` |
| Validation / Rolling / OOS | `normal / normal / normal` |
| ETF Operability | `normal` |

최근 allocation tail:

| Date | End Ticker | Next Ticker | Total Balance | Period Return |
|---|---|---|---:|---:|
| `2025-09-30` | `GLD, QQQ` | `GLD, QQQ` | `47,142.31` | `16.40%` |
| `2026-01-30` | `GLD, QQQ` | `GLD, SPY` | `53,903.83` | `14.34%` |
| `2026-04-17` | `GLD, SPY` | `QQQ, SPY` | `54,631.16` | `1.35%` |

해석:

- 기존 기본 후보는 최신 DB end date까지 다시 돌려도 `real_money_candidate`를 유지한다.
- 사용자가 원한 "2개를 선택하는 GTAA" 형태를 유지한다면 아직 이 후보가 가장 자연스러운 기본값이다.

### B. 기존 낮은 MDD 대안 재확인

| 항목 | 값 |
|---|---|
| Universe | `SPY, QQQ, GLD, IEF, LQD` |
| Top | `2` |
| Interval | `6` |
| Score | `1M / 3M` |
| Risk-Off | `defensive_bond_preference` |
| End Balance | `47,960.46` |
| CAGR | `16.59%` |
| MDD | `-4.50%` |
| Sharpe | `3.94` |
| Benchmark CAGR | `13.56%` |
| Net CAGR Spread | `+3.03%p` |
| Promotion | `real_money_candidate` |
| Shortlist | `paper_probation` |
| Deployment | `paper_only` |
| Validation / Rolling / OOS | `normal / normal / normal` |
| ETF Operability | `normal` |

최근 allocation tail:

| Date | End Ticker | Next Ticker | Total Balance | Period Return |
|---|---|---|---:|---:|
| `2025-07-31` | `QQQ, GLD` | `QQQ, SPY` | `43,119.93` | `12.64%` |
| `2026-01-30` | `QQQ, SPY` | `GLD, SPY` | `47,321.95` | `9.75%` |
| `2026-04-17` | `GLD, SPY` | `QQQ, SPY` | `47,960.46` | `1.35%` |

해석:

- risk-first 관점에서는 여전히 가장 깨끗하다.
- 다만 ticker 수를 충분히 늘렸다고 보기는 어렵고, CAGR도 신규 expanded `Top = 1`보다 낮다.

### C. 신규 확장 real-money 후보

| 항목 | 값 |
|---|---|
| Universe | `SPY, QQQ, GLD, IEF, LQD, TLT` |
| Top | `1` |
| Interval | `8` |
| Score | `1M / 3M / 6M` |
| Risk-Off | `cash_only` 또는 `defensive_bond_preference` 모두 동일 |
| End Balance | `73,002.03` |
| CAGR | `21.50%` |
| MDD | `-6.49%` |
| Sharpe | `3.66` |
| Benchmark CAGR | `13.56%` |
| Net CAGR Spread | `+7.93%p` |
| Promotion | `real_money_candidate` |
| Shortlist | `paper_probation` |
| Deployment | `paper_only` |
| Validation / Rolling / OOS | `normal / normal / normal` |
| ETF Operability | `normal` |

최근 allocation tail:

| Date | End Ticker | Next Ticker | Total Balance | Period Return |
|---|---|---|---:|---:|
| `2025-05-30` | `GLD` | `GLD` | `49,697.35` | `24.90%` |
| `2026-01-30` | `GLD` | `GLD` | `72,856.32` | `46.60%` |
| `2026-04-17` | `GLD` | `GLD` | `73,002.03` | `0.20%` |

해석:

- 이번 follow-up에서 새로 추가할 수 있는 가장 강한 확장 후보다.
- `TLT`까지 포함한 6개 universe이며, ETF operability와 validation이 모두 `normal`이다.
- 단점은 분명하다. 매 리밸런싱마다 1개 ETF만 들고 가므로 single-asset concentration이 크다.
- 최근 tail도 계속 `GLD`를 선택하고 있어 금 노출 집중을 별도 운영 리스크로 봐야 한다.

따라서 이 후보는 "기존 기본 후보 replacement"가 아니라
"확장 universe 공격형 paper probation 후보"로 등록한다.

### D. 신규 확장 Top-2 watchlist 후보

| 항목 | 값 |
|---|---|
| Universe | `SPY, QQQ, GLD, IEF, LQD, TLT` |
| Top | `2` |
| Interval | `4` |
| Score | `1M / 3M / 6M` |
| Risk-Off | `cash_only` 또는 `defensive_bond_preference` 모두 동일 |
| End Balance | `48,784.25` |
| CAGR | `16.79%` |
| MDD | `-8.39%` |
| Sharpe | `3.01` |
| Benchmark CAGR | `13.56%` |
| Net CAGR Spread | `+3.23%p` |
| Promotion | `production_candidate` |
| Shortlist | `watchlist` |
| Deployment | `watchlist_only` |
| Validation / Rolling / OOS | `watch / normal / normal` |
| ETF Operability | `normal` |

최근 allocation tail:

| Date | End Ticker | Next Ticker | Total Balance | Period Return |
|---|---|---|---:|---:|
| `2025-09-30` | `GLD, QQQ` | `GLD, QQQ` | `42,097.14` | `16.40%` |
| `2026-01-30` | `GLD, QQQ` | `GLD, SPY` | `48,135.05` | `14.34%` |
| `2026-04-17` | `GLD, SPY` | `GLD, QQQ` | `48,784.25` | `1.35%` |

해석:

- 사용자가 지적한 "ticker가 부족하다"는 문제에는 가장 직접적으로 답한다.
- 하지만 current promotion surface에서는 `validation_status = watch` 때문에 `real_money_candidate`가 아니다.
- 그래서 실전 후보로 추천하지 않고 watchlist-only 개선 대상으로 둔다.

## 제외된 확장 probe

| Probe | Universe | Top / Interval / Score | CAGR | MDD | Promotion | 제외 이유 |
|---|---|---|---:|---:|---|---|
| `BIL` 포함 7개 | `SPY, QQQ, GLD, IEF, LQD, TLT, BIL` | `Top 2 / Interval 6 / 1M, 3M` | `13.62%` | `-4.50%` | `hold` | `BIL` profile snapshot에서 spread data가 비정상적으로 들어와 ETF operability가 `watch`다. |
| Style 9 probe | `SPY, QQQ, GLD, IEF, LQD, TLT, IWD, IWM, VUG` | `Top 3 / Interval 4 / 1M, 3M` | `15.52%` | `-9.05%` | `hold` | `IWD / IWM / VUG` ETF profile coverage gap 때문에 operability가 `caution`이다. |
| Broad 11 probe | `SPY, QQQ, GLD, IEF, LQD, TLT, IWD, IWM, EFA, VNQ, XLE` | `Top 2 / Interval 4 / 1M, 3M` | `16.21%` | `-10.11%` | `hold` | `EFA / IWD / IWM / VNQ / XLE` profile gap과 rolling caution이 같이 있다. |

## 추천 운영안

### 1. 기본 추천은 기존 Top-2 후보 유지

실제 paper tracking의 기본값은 아래로 유지한다.

- Universe: `SPY, QQQ, GLD, IEF`
- Top: `2`
- Interval: `4`
- Score: `1M / 3M`
- Risk-Off: `defensive_bond_preference`
- Status: `real_money_candidate / paper_probation / paper_only`

이 조합은 여전히 다음 이유로 가장 균형이 좋다.

- 2개 ETF를 보유한다.
- ETF operability가 `normal`이다.
- validation / rolling / out-of-sample이 모두 `normal`이다.
- current sampled benchmark 대비 CAGR과 MDD가 모두 우위다.

### 2. 신규 확장 후보는 공격형 paper candidate로 추가

확장 universe를 반영하고 싶다면 아래 후보를 새로 tracking한다.

- Universe: `SPY, QQQ, GLD, IEF, LQD, TLT`
- Top: `1`
- Interval: `8`
- Score: `1M / 3M / 6M`
- Status: `real_money_candidate / paper_probation / paper_only`

이 후보는 숫자가 강하지만, `Top = 1` concentration이 있으므로
기본 후보를 대체하기보다는 별도 공격형 sleeve 후보로 본다.

### 3. 확장 Top-2는 다음 개선 대상

아래 조합은 직관적으로 더 마음에 들지만 아직 gate가 부족하다.

- Universe: `SPY, QQQ, GLD, IEF, LQD, TLT`
- Top: `2`
- Interval: `4`
- Score: `1M / 3M / 6M`
- Status: `production_candidate / watchlist / watchlist_only`

다음 작업에서 볼 만한 개선 방향은:

- `Top = 2`를 유지하되 interval을 `5 / 6 / 8` 주변에서 더 세밀하게 탐색
- `TLT` 외에 clean profile이 확보된 defensive ETF만 추가
- style / international / sector ETF는 먼저 profile refresh 이후 다시 테스트
- 최근 GLD 집중을 완화하는 allocation cap 또는 diversity penalty 검토

## 현재 ETF 상품 확인

이번 clean expanded core에 쓰인 ETF는 아래 공식 상품 페이지를 현재 시점 확인용 reference로 둔다.

- `SPY`: State Street SPDR S&P 500 ETF Trust
  - https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy
- `QQQ`: Invesco QQQ
  - https://www.invesco.com/qqq-etf/en/home.html
- `GLD`: SPDR Gold Shares
  - https://www.spdrgoldshares.com/usa/gld/
- `IEF`: iShares 7-10 Year Treasury Bond ETF
  - https://www.ishares.com/us/products/239456/ishares-710-year-treasury-bond-etf
- `LQD`: iShares iBoxx $ Investment Grade Corporate Bond ETF
  - https://www.ishares.com/us/products/239566/ishares-iboxx-investment-grade-corporate-bond-etf
- `TLT`: iShares 20+ Year Treasury Bond ETF
  - https://www.ishares.com/us/products/239454/ishares-20-year-treasury-bond-etf
- `BIL`: State Street SPDR Bloomberg 1-3 Month T-Bill ETF
  - https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-bloomberg-1-3-month-t-bill-etf-bil

## 실행 재현 스니펫

신규 확장 real-money 후보:

```python
from app.web.runtime.backtest import run_gtaa_backtest_from_db

bundle = run_gtaa_backtest_from_db(
    tickers=["SPY", "QQQ", "GLD", "IEF", "LQD", "TLT"],
    start="2016-01-01",
    end=None,
    timeframe="1d",
    option="month_end",
    top=1,
    interval=8,
    min_price_filter=5.0,
    transaction_cost_bps=10.0,
    benchmark_ticker="SPY",
    score_lookback_months=[1, 3, 6],
    risk_off_mode="cash_only",
    defensive_tickers=["TLT", "IEF", "LQD", "BIL"],
    market_regime_enabled=False,
    crash_guardrail_enabled=False,
    promotion_min_etf_aum_b=1.0,
    promotion_max_bid_ask_spread_pct=0.005,
    universe_mode="manual_tickers",
    preset_name="gtaa_expanded_core6_top1_20260420",
)
```

확장 Top-2 watchlist 후보:

```python
from app.web.runtime.backtest import run_gtaa_backtest_from_db

bundle = run_gtaa_backtest_from_db(
    tickers=["SPY", "QQQ", "GLD", "IEF", "LQD", "TLT"],
    start="2016-01-01",
    end=None,
    timeframe="1d",
    option="month_end",
    top=2,
    interval=4,
    min_price_filter=5.0,
    transaction_cost_bps=10.0,
    benchmark_ticker="SPY",
    score_lookback_months=[1, 3, 6],
    risk_off_mode="cash_only",
    defensive_tickers=["TLT", "IEF", "LQD", "BIL"],
    market_regime_enabled=False,
    crash_guardrail_enabled=False,
    promotion_min_etf_aum_b=1.0,
    promotion_max_bid_ask_spread_pct=0.005,
    universe_mode="manual_tickers",
    preset_name="gtaa_expanded_core6_top2_watchlist_20260420",
)
```

## 한 줄 결론

`GTAA` 안에서 ticker 부족 문제를 보강한 새 후보는
`SPY / QQQ / GLD / IEF / LQD / TLT`, `Top = 1`, `Interval = 8`, `Score = 1M / 3M / 6M`이다.

다만 2개 보유를 유지하는 실전 기본값은 아직 기존
`SPY / QQQ / GLD / IEF`, `Top = 2`, `Interval = 4`, `Score = 1M / 3M`
후보가 더 안정적인 대표 후보로 남는다.
