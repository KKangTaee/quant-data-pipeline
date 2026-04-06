# PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH

## 목적

사용자가 `GTAA` 전략만 대상으로, 아래 조건을 만족하는 포트폴리오를 찾아달라고 요청했다.

- `Promotion != hold`
- `Deployment != blocked`
- `SPY`보다 `CAGR`가 높을 것
- `SPY`보다 `MDD`가 더 좋을 것
- 시작일: `2016-01-01`
- 종료일: 현재 DB 기준 최신 구간
- 현재 고정 preset 외에도 DB에 데이터가 존재하는 ETF를 섞어볼 수 있음

이번 탐색은 서브 에이전트 병렬 검색과 메인 환경 재검증을 함께 사용했다.

## 후보 ETF 풀

DB에서 다음 조건을 먼저 확인했다.

- ETF asset profile 존재
- price history가 `2016-01`부터 이어짐
- 최근 데이터가 현재 구간까지 연결됨

실제 탐색에 사용한 후보군은 아래 40개 ETF였다.

`SPY, QQQ, GLD, IEF, TLT, BIL, LQD, DBC, EFA, IWD, IWM, IWN, SOXX, VNQ, MTUM, AGG, EWJ, HYG, IAU, RSP, SHY, TIP, VEA, VEU, VGK, VIG, VTV, VUG, VWO, XLE, XLP, XLU, XLV, ACWV, SCHD, USMV, QUAL, DGRO, COMT, PDBC`

## 최종 선정 후보

### 선택 이유

서브 에이전트 탐색에서는 더 높은 `CAGR`를 가진 공격형 후보도 나왔지만, 일부는 `ETF operability` 조건을 사실상 꺼야만 `hold`를 벗어났다.

이번 문서에서는:

- `SPY` benchmark 유지
- UI에서 그대로 재현 가능
- `Promotion != hold`
- `Deployment != blocked`
- `SPY` 대비 `CAGR / MDD` 우위

를 동시에 만족하는 **실용적인 후보**를 최종값으로 남긴다.

### 포트폴리오 설정

- 전략: `GTAA`
- tickers:
  - `SPY, QQQ, GLD, LQD`
- 시작일: `2016-01-01`
- 종료일: `2026-04-02`
- 리밸런싱 기준: `month_end`
- `Top Assets = 2`
- `Signal Interval = 3`
- `Score Horizons = 1M, 3M`
- `Risk-Off Mode = cash_only`
- `Benchmark Ticker = SPY`
- `Minimum Price = 5.0`
- `Transaction Cost = 10 bps`
- `Min ETF AUM ($B) = 0.0`
- `Max Bid-Ask Spread (%) = 100.0`
- `Market Regime = off`

## 메인 환경 재검증 결과

### GTAA 후보

- effective window: `2016-01-29 ~ 2026-04-02`
- `CAGR = 14.7671%`
- `MDD = -11.5626%`
- `Promotion = production_candidate`
- `Shortlist = watchlist`
- `Deployment = watchlist_only`
- `Validation = watch`
- `Rolling Review = normal`
- `Out-Of-Sample Review = normal`
- `ETF Operability = normal`
- `ETF Operability Clean Coverage = 100%`

### SPY benchmark 동일 구간

- effective window: `2016-01-29 ~ 2026-04-02`
- `CAGR = 12.7345%`
- `MDD = -15.9042%`

## 조건 충족 여부

- `Promotion != hold`: 충족
- `Deployment != blocked`: 충족
- `CAGR > SPY`: 충족
- `MDD better than SPY`: 충족

## 해석

이 후보는 현재 Phase 13 운영 해석 기준으로:

- 아직 `real_money_candidate`는 아님
- 하지만 `hold`는 벗어났고
- `blocked`도 아님
- 즉 **관찰 가능한 운용 후보(`watchlist_only`)**로 볼 수 있다

쉽게 말하면:

- 바로 실전 투입 확정 전략은 아니지만
- 현재 GTAA family 안에서는
- `SPY`보다 나은 위험/수익 구조와
- non-hold 상태를 동시에 보여준 practical reference다

## 더 공격적인 near-miss

서브 에이전트 탐색에서 아래 공격형 후보는 더 강한 수익률을 보였다.

- tickers:
  - `SPY, QQQ, SOXX, VUG, VTV, RSP, IAU, XLE, TIP, TLT, IEF, LQD, VNQ, EFA, GLD`
- `Top = 2`
- `Interval = 3`
- `Score Horizons = 1M, 3M, 6M`
- `Benchmark = SPY`
- `CAGR = 16.7189%`
- `MDD = -13.0870%`

다만 이 후보는 `ETF operability` current-data gap 때문에, 실전형 상태를 유지하려면 해당 정책을 사실상 꺼야 했다. 그래서 이번 문서의 최종 practical candidate로는 채택하지 않았다.

## 한 줄 결론

현재 GTAA에서 가장 실용적인 non-hold reference는:

- `SPY, QQQ, GLD, LQD`
- `top = 2`
- `interval = 3`
- `score horizons = 1M / 3M`
- `benchmark = SPY`

조합이다.
