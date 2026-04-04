# Phase 12 GTAA vs SPY Dominance Search

## 목적

- `GTAA`를 여러 방식으로 변형했을 때,
  **SPY보다 CAGR은 높고 MDD는 더 낮은**
  조합이 실제로 나오는지 확인한다.
- 여기서 말하는 `dominance`는:
  - 수익은 `SPY`보다 더 높고
  - 낙폭은 `SPY`보다 더 덜 큰
  상태를 뜻한다.

쉬운 뜻:

- 이번 실험은 단순히 “좋아 보이는 GTAA 조합”을 찾는 게 아니다.
- **실전 기준에서 SPY를 두 가지 축(CAGR, MDD)으로 동시에 이길 수 있는지**
  보는 실험이다.

## 비교 기준

### SPY baseline

- strategy: `Equal Weight`
- ticker: `SPY`
- start: `2016-08-31`
- end: `2026-04-02`
- timeframe: `1d`
- option: `month_end`
- rebalance interval: `1`

baseline 결과:

- `CAGR`: `12.21%`
- `MDD`: `-24.80%`
- `End Balance`: `30,169.70`

## GTAA 탐색 범위

이번 탐색은 두 단계로 나눠 진행했다.

### 1. 기본 dominance search

- tested runs: `48`
- 공통 시작점: `2016-08-31`
- universe:
  - `GTAA Universe`
  - `GTAA Universe (No Commodity + QUAL + USMV)`
  - `GTAA Universe (QQQ + XLE + IAU + TIP)`
  - `GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)`
  - `GTAA Universe (QQQ + XLE + IAU)`
  - `GTAA Universe (COMT + QUAL + USMV)`
- score horizon:
  - `1/3/6/12`
  - `1/3/6`
  - `3/6/12`
  - `1/3`
- risk-off:
  - `Cash Only`
  - `Defensive Bond Preference`

artifact:

- `.note/finance/phase12/_tmp_gtaa_vs_spy_search.csv`

### 2. overlay 확장 dominance search

- tested runs: `96`
- 공통 시작점: `2016-08-31`
- universe:
  - `GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)`
  - `GTAA Universe (QQQ + XLE + IAU + TIP)`
  - `GTAA Universe (No Commodity + QUAL + USMV)`
  - `GTAA Universe (QQQ + XLE + IAU)`
- score horizon:
  - `1/3/6/12`
  - `1/3/6`
  - `3/6/12`
- risk-off:
  - `Cash Only`
  - `Defensive Bond Preference`
- overlay:
  - `None`
  - `Regime`
  - `Crash`
  - `Regime + Crash`

artifact:

- `.note/finance/phase12/_tmp_gtaa_vs_spy_overlay_search.csv`

## 결론

- 이번에 테스트한 `GTAA` 조합 중에는
  **SPY보다 CAGR이 더 높고, 동시에 MDD도 더 낮은 조합은 없었다.**
- 즉 current Phase 12 search range 안에서는
  **SPY를 두 축에서 동시에 지배(dominance)하는 GTAA 조합을 찾지 못했다.**

쉬운 뜻:

- `GTAA`는 drawdown을 줄이는 데는 꽤 성공했지만,
  그 대신 상승률이 SPY보다 약간 부족한 경우가 많았다.
- 반대로 공격성을 높이면 CAGR은 SPY에 가까워지지만,
  그 경우에도 SPY보다 확실히 높은 수준까지는 못 올라갔다.

## 가장 가까웠던 후보

### 1. CAGR 쪽에서 가장 가까웠던 후보

- `GTAA Universe (QQQ + XLE + IAU + TIP)`
- `GTAA Universe (QQQ + XLE + IAU)`
- `Score Horizons = 1/3/6`
- `Risk-Off = Cash Only` 또는 `Defensive Bond Preference`

결과:

- `CAGR`: `11.90%`
- `MDD`: `-20.03%`
- `Sharpe`: `0.859`

해석:

- 이 조합은 **SPY보다 낙폭은 확실히 낮았다.**
- 하지만 CAGR이 `12.21%`인 SPY를 아주 조금 못 넘었다.
- 즉 이번 실험에서는
  **“가장 비슷하게 따라간 공격형 GTAA”**
  로 보는 게 맞다.

### 2. MDD 개선 쪽에서 가장 강했던 후보

- `GTAA Universe (No Commodity + QUAL + USMV)`
- `Score Horizons = 1/3/6/12`
- `Risk-Off = Defensive Bond Preference`

결과:

- `CAGR`: `8.96%`
- `MDD`: `-16.17%`

해석:

- 이 조합은 **낙폭 관리 성격이 매우 강했다.**
- 대신 수익률은 SPY보다 꽤 낮아졌다.
- 즉 실전형 “defensive variant”로는 의미가 있지만,
  **SPY를 수익/낙폭 두 축에서 동시에 이기는 후보는 아니었다.**

## overlay는 도움이 되었는가

- `Regime`
- `Crash`
- `Regime + Crash`

까지 포함해서 다시 돌렸지만,
**winner는 여전히 `0`개**였다.

해석:

- overlay가 drawdown을 줄이는 방향으로는 일부 도움을 줄 수 있지만,
  이번 탐색 범위에서는 그 대가로 CAGR이 같이 줄어드는 경우가 많았다.
- 즉 current GTAA contract에서는
  **overlay만 얹는다고 SPY dominance가 바로 생기지는 않았다.**

## 왜 이런 결과가 나왔는가

가능성 높은 해석은 세 가지다.

### 1. GTAA는 원래 drawdown 개선형 성격이 더 강하다

- `top-3 rotation`
- `trend filter`
- `risk-off fallback`

이 구조는 대체로
**강한 폭락을 덜 맞는 대신,
계속 우상향하는 강한 주식장에선 SPY보다 덜 공격적일 수 있다.**

### 2. 현재 탐색에서 가장 강한 공격축은 이미 `QQQ + XLE + IAU` 쪽이다

- 이번 범위에서는 이 축이 가장 좋은 CAGR을 만들었다.
- 그럼에도 SPY를 아주 조금 못 넘었다는 건,
  **현재 contract 안에서는 이미 꽤 상단까지 온 상태**
  일 가능성이 높다.

### 3. GTAA 성능은 universe뿐 아니라 contract에도 크게 의존한다

- score horizon
- top N
- rebalance cadence
- risk-off rule

이런 contract를 더 넓게 바꾸지 않으면
SPY dominance를 찾기 어렵다는 신호로 읽을 수 있다.

## 현재 실무적 해석

- **“SPY보다 무조건 더 좋은 GTAA를 이미 찾았다”라고 말할 단계는 아니다.**
- 하지만 다음 두 방향은 분명하다.

1. `QQQ + XLE + IAU (+TIP)` 계열
   - 가장 공격적인 GTAA 개선 방향
   - SPY에 가장 가까운 CAGR을 만들었음
2. `No Commodity + QUAL + USMV`
   - 가장 안정적인 GTAA 개선 방향
   - MDD를 강하게 줄였음

즉 현재 GTAA는
- **공격형 candidate**
- **방어형 candidate**
로는 방향이 보이지만,
- **SPY dominance candidate**
는 아직 확보되지 않았다.

## 다음 탐색이 의미 있는 축

SPY dominance를 계속 찾고 싶다면,
다음 레버가 가장 자연스럽다.

1. `top N` 변경
   - `top=2`
   - `top=4`
2. score horizon 재탐색
   - `1/3`
   - `1/3/6`
   - `3/6/12`
3. risk-off contract 재설계
   - defensive bond preference 강화
   - regime/crash threshold 조정
4. ETF universe 추가 확장
   - current Phase 12 search보다 더 넓은 공격/방어 ETF 후보군

## Phase 12 기준 결론

- 이번 검색으로 확인된 durable result는:
  **현재 Phase 12에서 테스트한 GTAA 조합 중,
  SPY보다 CAGR이 높고 MDD가 낮은 조합은 없었다.**
- 따라서 current GTAA는
  - drawdown 개선형 실전 후보
  - 공격형 대안 후보
  로는 의미가 있지만,
  **SPY를 두 축에서 동시에 이기는 확정 승격 후보는 아직 아니다.**
