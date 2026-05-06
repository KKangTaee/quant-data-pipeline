# Equal Weight Backtest Log

## 최근 판단 요약표

| 날짜 | 목표 | 대표 후보 | 상태 | 판단 |
|---|---|---|---|---|
| 2026-05-05 | `GTAA SPY Low-MDD Style Top-3`와 함께 쓸 Equal Weight sleeve 탐색 | `QQQ / SOXX / XLE / XLU / GLD`, annual rebalance | 10단계 gate 통과, 단독 MDD 조건은 초과 | GTAA mix용 실사용 후보로 가장 균형적 |

## 로그

### 2026-05-05 - GTAA SPY Low-MDD 후보와 함께 쓸 Equal Weight sleeve 탐색

- 목표:
  - `GTAA SPY Low-MDD Style Top-3`와 60:40 또는 70:30으로 섞었을 때 시너지가 나는 Equal Weight 후보를 찾는다.
  - 조건은 symbol 3~5개, interval 6~12개월, benchmark `SPY`, 10단계 이상 통과 가능 상태, 가능하면 MDD 15% 이하이다.
- 기준 GTAA:
  - `GTAA SPY Low-MDD Style Top-3`
  - universe: `QQQ, SOXX, MTUM, QUAL, USMV, IAU, IEF, TLT`
  - `top=3`, `interval=3`, `1M/6M`, `MA250`, `cash_only`, `Benchmark=SPY`
  - `CAGR=19.35%`, `MDD=-11.03%`, `Sharpe=2.42`
- 탐색 결론:
  - 모든 조건을 동시에 만족하는 Equal Weight 단독 후보는 찾지 못했다.
  - MDD 15% 이하 방어형 후보는 `hold / blocked`로 떨어졌다. 대표 예시는 `DGRW / XLU / GLD`, annual rebalance이며 `CAGR=11.74%`, `MDD=-13.71%`지만 `Promotion=hold`, `Deployment=blocked`, `Validation=caution`이다.
  - 이유는 SPY 강세 구간에서 rolling excess가 크게 나빠져 `worst rolling excess=-30.90%`, `underperformance share=57.52%`가 되었기 때문이다.
- 대표 실사용 후보:
  - 전략 이름 후보: `Equal Weight Growth / Sector / Gold 5`
  - universe: `QQQ, SOXX, XLE, XLU, GLD`
  - `Interval = 12`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
- 단독 Equal Weight 결과:
  - `CAGR = 17.55%`
  - `MDD = -18.98%`
  - `Sharpe = 1.21`
  - `SPY CAGR = 13.67%`
  - `SPY MDD = -24.80%`
  - `SPY 대비 CAGR spread = +3.88%p`
  - `Rolling underperformance share = 45.13%`
  - `Worst rolling excess = -8.06%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `Validation = normal`
  - `Monitoring = routine_review`
  - `ETF Operability = normal`
- GTAA mix 결과:
  - `GTAA 70 / Equal Weight 30`: `CAGR=18.74%`, `MDD=-10.30%`, `Sharpe=2.51`
  - `GTAA 60 / Equal Weight 40`: `CAGR=18.52%`, `MDD=-10.04%`, `Sharpe=2.54`
- 비교 후보:
  - `QQQ / SOXX / XLE / XLV / GLD`, annual rebalance:
    - 단독 `CAGR=17.58%`, `MDD=-18.40%`, `Promotion=real_money_candidate`, `Deployment=paper_only`
    - `GTAA 70 / EW 30`: `CAGR=18.78%`, `MDD=-10.08%`, `Sharpe=2.47`
    - MDD는 조금 낮지만, utility sleeve가 빠져 mix Sharpe는 대표 후보보다 약하다.
  - `DGRW / XLU / GLD`, annual rebalance:
    - 단독 `CAGR=11.74%`, `MDD=-13.71%`
    - MDD 조건은 좋지만 `Promotion=hold`, `Deployment=blocked`라 10단계 실습 후보로는 부적합하다.
- 해석:
  - `MDD <= 15%`를 Equal Weight 단독 조건으로 엄격히 적용하면 현재 SPY benchmark gate를 통과하는 후보가 없다.
  - `GTAA와 섞은 전체 포트폴리오 MDD <= 15%`로 보면 `QQQ / SOXX / XLE / XLU / GLD`가 가장 균형적이다.
  - 특히 60:40은 70:30보다 CAGR은 조금 낮지만 Sharpe와 MDD가 더 좋아, 방어 목적의 보완 sleeve로 더 자연스럽다.

