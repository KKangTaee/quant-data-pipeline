# GTAA Real-Money Candidate Search 2026-04-18

## 이 문서는 무엇인가

사용자가 요청한 `GTAA` 전략 기반 투자 가능 포트폴리오 탐색 기록이다.

요청의 핵심은 아래였다.

- `promotion`이 `hold`가 아닌 후보
- 기존 preset에 갇히지 않은 다양한 ETF 조합 탐색
- 실제 백테스트를 통해 추천 후보와 전략을 Markdown으로 저장
- 백테스트 탐색에 서브에이전트 적극 활용

이번 문서의 결론은 **current DB/runtime 기준으로 `Promotion = real_money_candidate`까지 올라간 GTAA 후보를 확보했다**는 것이다.

다만 이 repo의 deployment contract에서 ETF 전략의 `real_money_candidate`는 곧바로 실전 주문을 뜻하지 않는다.
현재 추천 후보의 `Deployment = paper_only`이므로, 운영 해석은 **실거래 전 paper probation 후보**다.

## 결론 먼저

현재 가장 추천할 만한 기본 후보는 아래 `Balanced Top-2`다.

| 역할 | Tickers | Top | Interval | Score Horizons | Risk-Off | CAGR | MDD | Sharpe | Promotion | Shortlist | Deployment |
|---|---|---:|---:|---|---|---:|---:|---:|---|---|---|
| 추천 기본 후보 | `SPY, QQQ, GLD, IEF` | `2` | `4` | `1M / 3M` | `defensive_bond_preference` | `17.46%` | `-8.39%` | `3.07` | `real_money_candidate` | `paper_probation` | `paper_only` |
| 공격형 대안 | `SPY, QQQ, GLD, LQD` | `1` | `4` | `1M / 3M / 6M` | `cash_only` | `20.62%` | `-10.67%` | `2.94` | `real_money_candidate` | `paper_probation` | `paper_only` |
| 낮은 MDD 대안 | `SPY, QQQ, GLD, IEF, LQD` | `2` | `6` | `1M / 3M` | `defensive_bond_preference` | `15.97%` | `-4.75%` | `3.59` | `real_money_candidate` | `paper_probation` | `paper_only` |
| 기존 Phase 13 reference | `SPY, QQQ, GLD, LQD` | `2` | `3` | `1M / 3M` | `cash_only` | `14.74%` | `-11.56%` | `2.07` | `production_candidate` | `watchlist` | `watchlist_only` |

추천 기본 후보를 `Balanced Top-2`로 둔 이유는:

- `Promotion = real_money_candidate`
- `ETF Operability = normal`
- `Validation = normal`
- `Rolling Review = normal`
- `Out-Of-Sample Review = normal`
- `Top = 2`라서 `Top = 1` 공격형보다 한 종목 집중도가 낮음
- 기존 Phase 13 reference보다 gate가 한 단계 좋아짐

공격형 대안은 CAGR이 가장 높지만, `Top = 1`이라 매 리밸런싱 때 한 ETF에 집중된다.
낮은 MDD 대안은 수익률을 일부 포기하고 최대 낙폭을 크게 줄이는 관찰 후보로 둔다.

## 공통 백테스트 계약

| 항목 | 값 |
|---|---|
| Runtime | `app.web.runtime.backtest.run_gtaa_backtest_from_db` |
| Interpreter | `./.venv/bin/python` |
| Strategy | `GTAA` |
| Universe Mode | `manual_tickers` |
| Start Input | `2016-01-01` |
| Effective Start | `2016-01-29` |
| End Input | `None` |
| Effective End | `2026-03-31` |
| Timeframe | `1d` |
| Sampling | `month_end` |
| Benchmark | `SPY` |
| Min Price | `$5.0` |
| Transaction Cost | `10 bps` |
| Min ETF AUM | `$1.0B` default |
| Max Bid-Ask Spread | `0.50%` default |
| Market Regime / Crash Guardrail | off |

주의할 점:

- DB의 일간 가격 freshness는 일부 ETF에서 `2026-04-16`까지 있었지만,
  `month_end` 샘플링 결과의 마지막 유효 row는 `2026-03-31`이다.
- `SPY` benchmark는 raw daily buy-and-hold가 아니라,
  GTAA 결과와 같은 month-end sampled surface에 맞춘 비교다.

## 서브에이전트 활용

이번 탐색은 메인 환경 재검증과 서브에이전트 탐색을 같이 사용했다.

| Agent | 역할 | 핵심 결과 |
|---|---|---|
| `Confucius` | GTAA 코드 경로 / 실행 경로 조사 | `run_gtaa_backtest_from_db`가 promotion/readiness metadata를 포함하는 canonical DB runtime임을 확인 |
| `Mencius` | 보수형 ETF universe 탐색 | `SPY, QQQ, GLD, LQD` compact sleeve가 current operability normal인 practical candidate임을 재확인 |
| `Socrates` | 공격형 ETF universe 탐색 | sector / style 확장 universe는 raw CAGR이 높아도 ETF operability/profile coverage 때문에 `hold`로 막히는 패턴 확인 |

메인 재검증에서는 위 결과를 받아서 `ETF profile / AUM / spread coverage`가 완전한 ETF 중심으로 다시 좁혔다.
그 결과 기존 `production_candidate` reference를 넘어서는 `real_money_candidate` 변형을 찾았다.

## 왜 broad universe를 그대로 추천하지 않았나

기존 preset 밖으로 넓게 테스트한 universe 중에는 raw 성과가 더 높은 후보도 있었다.
예를 들면 `XLE`, `MTUM`, `EFA`, `VWO`, `TIP`, `USMV`, `VNQ` 등을 섞은 후보들은 일부 구간에서 더 높은 CAGR을 보였다.

하지만 current runtime promotion gate에서는 아래 이유로 보수적으로 제외했다.

- ETF profile / AUM / spread coverage가 부분적으로 비어 있음
- `ETF Operability = caution`으로 내려감
- 일부 broader mix는 `Validation = caution`도 같이 발생
- 결과적으로 `Promotion = hold`, `Deployment = blocked`가 반복됨

따라서 이번 추천은 “가장 화려한 raw CAGR”이 아니라,
**현재 repo의 promotion/readiness gate를 완전히 통과한 후보**를 우선했다.

## 후보 상세

### 1. 추천 기본 후보: Balanced Top-2

| 항목 | 값 |
|---|---|
| Tickers | `SPY, QQQ, GLD, IEF` |
| Top | `2` |
| Interval | `4` |
| Score Horizons | `1M / 3M` |
| Risk-Off Mode | `defensive_bond_preference` |
| Defensive Tickers | `TLT, IEF, LQD, BIL` |
| End Balance | `$51,344.67` |
| CAGR | `17.46%` |
| Standard Deviation | `21.90%` |
| Sharpe | `3.07` |
| MDD | `-8.39%` |
| Benchmark CAGR | `12.65%` |
| Net CAGR Spread | `+4.81%p` |
| Strategy Max Drawdown | `-8.39%` |
| Benchmark Max Drawdown | `-20.61%` |
| Promotion | `real_money_candidate` |
| Shortlist | `paper_probation` |
| Probation | `paper_tracking` |
| Monitoring | `routine_review` |
| Deployment | `paper_only` |
| ETF Operability | `normal` |
| ETF Operability Clean Coverage | `100%` |
| Validation | `normal` |
| Rolling Review | `normal` |
| Out-Of-Sample Review | `normal` |

최신 월말 상태:

- `2026-03-31`
- `End Ticker = [GLD, SPY]`
- `Next Ticker = [GLD]`
- 한 슬롯은 trend filter로 채워지지 않아 cash로 남음
- `Cash = 25,906`

해석:

- 기본 추천 후보로 둔다.
- 공격형 후보보다 CAGR은 낮지만, `Top = 2`라서 한 ETF에만 전액 배분하는 구조보다 실전 설명이 쉽다.
- 최근 상태가 `GLD + cash`에 가까우므로, 현재 시장 국면에서는 위험자산보다 금/현금 쪽으로 기울어진 해석이 필요하다.

### 2. 공격형 대안: High-CAGR Top-1

| 항목 | 값 |
|---|---|
| Tickers | `SPY, QQQ, GLD, LQD` |
| Top | `1` |
| Interval | `4` |
| Score Horizons | `1M / 3M / 6M` |
| Risk-Off Mode | `cash_only` |
| End Balance | `$67,260.28` |
| CAGR | `20.62%` |
| Standard Deviation | `26.96%` |
| Sharpe | `2.94` |
| MDD | `-10.67%` |
| Benchmark CAGR | `12.65%` |
| Net CAGR Spread | `+7.97%p` |
| Strategy Max Drawdown | `-10.67%` |
| Benchmark Max Drawdown | `-20.61%` |
| Promotion | `real_money_candidate` |
| Shortlist | `paper_probation` |
| Deployment | `paper_only` |
| ETF Operability | `normal` |
| Validation | `normal` |
| Rolling Review | `normal` |
| Out-Of-Sample Review | `normal` |

최신 월말 상태:

- `2026-03-31`
- `End Ticker = [GLD]`
- `Next Ticker = [GLD]`
- `Cash = 0`

해석:

- 이번 탐색에서 가장 높은 CAGR을 낸 clean 후보다.
- 다만 `Top = 1`이라 실제로는 “4개 ETF 중 하나만 보유하는 tactical rotation”에 가깝다.
- 투자 후보로는 가능하지만, 사용자 성향이 집중 포지션을 감당할 수 있는지 별도 확인이 필요하다.

### 3. 낮은 MDD 대안: Low-MDD Top-2

| 항목 | 값 |
|---|---|
| Tickers | `SPY, QQQ, GLD, IEF, LQD` |
| Top | `2` |
| Interval | `6` |
| Score Horizons | `1M / 3M` |
| Risk-Off Mode | `defensive_bond_preference` |
| End Balance | `$45,075.27` |
| CAGR | `15.97%` |
| Standard Deviation | `25.66%` |
| Sharpe | `3.59` |
| MDD | `-4.75%` |
| Benchmark CAGR | `12.65%` |
| Net CAGR Spread | `+3.32%p` |
| Strategy Max Drawdown | `-4.75%` |
| Benchmark Max Drawdown | `-9.65%` |
| Promotion | `real_money_candidate` |
| Shortlist | `paper_probation` |
| Deployment | `paper_only` |
| ETF Operability | `normal` |
| Validation | `normal` |
| Rolling Review | `normal` |
| Out-Of-Sample Review | `normal` |

최신 월말 상태:

- `2026-03-31`
- `End Ticker = [GLD, SPY]`
- `Next Ticker = [GLD]`
- 한 슬롯은 cash로 남음
- `Cash = 22,731`

해석:

- 최대 낙폭을 더 줄이고 싶을 때 보는 대안이다.
- 단, `interval = 6`이라 리밸런싱이 더 느리고, 비교 benchmark drawdown도 같은 interval surface 기준으로 낮아진다.
- 실전 전에는 cadence 민감도 검토를 한 번 더 하는 편이 좋다.

## 기존 Phase 13 reference와의 차이

기존 reference는 아래였다.

- `SPY, QQQ, GLD, LQD`
- `Top = 2`
- `Interval = 3`
- `Score Horizons = 1M / 3M`
- `Promotion = production_candidate`
- `Shortlist = watchlist`
- `Deployment = watchlist_only`
- `Validation = watch`

이번 후보들은 같은 compact ETF idea에서 출발했지만,
`top / interval / horizon`을 다시 조정해 `Validation = normal`을 회복했다.
그래서 현재 기준으로는 기존 Phase 13 reference보다 이번 `Balanced Top-2`가 더 좋은 운영 후보다.

## 현재 ETF 상품 확인

이번 추천 후보에 쓰인 ETF는 아래 공식 상품 페이지를 현재 시점 확인용 reference로 둔다.

- `SPY`: State Street SPDR S&P 500 ETF Trust 공식 상품 페이지
  - https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy
- `QQQ`: Invesco QQQ Trust 공식 상품 페이지
  - https://www.invesco.com/qqq-etf/en/home.html
- `GLD`: SPDR Gold Shares 공식 상품 페이지
  - https://www.spdrgoldshares.com/
- `IEF`: iShares 7-10 Year Treasury Bond ETF 공식 상품 페이지
  - https://www.ishares.com/us/products/239456/ishares-710-year-treasury-bond-etf
- `LQD`: iShares iBoxx $ Investment Grade Corporate Bond ETF 공식 상품 페이지
  - https://www.ishares.com/us/products/239566/ishares-iboxx-investment-grade-corporate-bond-etf

repo DB의 current ETF operability snapshot에서는 추천 후보의 ETF들이 모두 `normal`로 통과했다.
단, 이 snapshot은 point-in-time AUM/spread history가 아니라 current profile 기반 first-pass operability다.

## 실행 재현 스니펫

```python
from app.web.runtime.backtest import run_gtaa_backtest_from_db

bundle = run_gtaa_backtest_from_db(
    tickers=["SPY", "QQQ", "GLD", "IEF"],
    start="2016-01-01",
    end=None,
    timeframe="1d",
    option="month_end",
    top=2,
    interval=4,
    min_price_filter=5.0,
    transaction_cost_bps=10.0,
    benchmark_ticker="SPY",
    score_lookback_months=[1, 3],
    risk_off_mode="defensive_bond_preference",
    defensive_tickers=["TLT", "IEF", "LQD", "BIL"],
    universe_mode="manual_tickers",
    preset_name="gtaa_real_money_balanced_top2_20260418",
)

summary = bundle["summary_df"]
meta = bundle["meta"]
```

## 운영 해석

이번 후보는 `Promotion = real_money_candidate`지만, `Deployment = paper_only`다.

즉 결론은:

- 백테스트와 current operability gate 기준으로는 `hold`를 벗어난다
- current runtime은 실제 투자 후보로 읽을 수 있는 단계까지 올린다
- 하지만 곧바로 큰 자금을 넣는 후보가 아니라, paper tracking을 먼저 시작하는 후보로 해석한다

실전 전 최소 확인 사항:

- 다음 월말 리밸런싱에서 동일 후보가 계속 `real_money_candidate`인지 재확인
- GLD 집중 상태와 세금/상품 구조 확인
- 실제 주문 단위, 계좌 통화, ETF 거래 가능 여부 확인
- spread / quote snapshot refresh
- monthly paper tracking 기록 시작

## 한 줄 결론

현재 repo 기준 GTAA에서 추천할 수 있는 투자 가능 후보는:

`SPY / QQQ / GLD / IEF`, `Top = 2`, `Interval = 4`, `Score = 1M / 3M`, `Risk-Off = defensive_bond_preference`

이다.

이 후보는 `real_money_candidate / paper_probation / paper_only`로, **hold가 아닌 실제 후보지만 첫 운영 단계는 paper probation**으로 남긴다.
