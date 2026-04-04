# Phase 12 GTAA CAGR 9 / MDD 16 Target Search

## 목적

- `GTAA` 변형을 더 넓게 탐색해서,
  `CAGR >= 9%`이면서 `MDD >= -16%`인 조합을 찾는다.
- 여기서 `MDD >= -16%`는 최대 낙폭이 `-16%`보다 더 나쁘지 않다는 뜻이다.

쉬운 뜻:

- 이번 실험은 단순히 좋아 보이는 GTAA 조합을 찾는 게 아니라,
  **실전형으로 쓸 수 있는 최소 성능 기준**을 만족하는 후보를 찾는 것이다.

## 비교 기준

- benchmark reference: `SPY`
- common date range: `2016-08-31 ~ 2026-04-02`

SPY baseline:

- `CAGR`: `12.21%`
- `MDD`: `-24.80%`

## 탐색 방식

탐색은 두 단계로 진행했다.

### 1. broad universe sweep

- current GTAA core에 더 많은 ETF를 섞은 large manual universes를 탐색
- `top`: `2 / 3 / 4`
- `rebalance interval`: `1 / 2`
- score horizons:
  - `1/3`
  - `1/3/6`
  - `3/6`
- risk-off:
- `cash_only`
- `defensive_bond_preference`

대표 universe:

- `SPY|QQQ|VUG|MTUM|QUAL|USMV|XLE|IAU|TIP|TLT|LQD|VNQ|ACWV`
- `QQQ|VUG|RSP|VTV|QUAL|USMV|XLE|IAU|TIP|TLT|LQD|ACWV|SPY`
- `QQQ|QUAL|USMV|XLE|IAU|TIP|TLT|LQD|SHY|AGG|VNQ|ACWV`

### 2. focused refinement

- first pass에서 target을 만족한 universe 주변만 다시 좁혀서 재검증
- 같은 `top / interval / horizon / risk-off` 축을 유지하면서 더 나은 candidate를 찾았다.

### 3. cadence follow-up

- first pass에서 강했던 universe만 골라
  `rebalance interval = 2 / 3`를 추가로 탐색했다.
- 이 단계에서 `interval` 변화가 target 충족 여부와 성능을 크게 바꿀 수 있다는 점을 확인했다.

## 핵심 결과

### Target Met

목표를 만족한 조합은 여러 개였고, 그중 상위 후보는 다음과 같다.

#### Best offensive candidate

- universe:
  - `SPY|QQQ|XLE|COMT|IAU|GLD|QUAL|USMV|TIP|TLT|IEF|LQD|VNQ|EFA|MTUM`
- `top = 2`
- `rebalance interval = 3`
- `Score Horizons = 1/3/6`
- `risk-off = cash_only` 또는 `defensive_bond_preference`

결과:

- `CAGR`: `16.66%`
- `MDD`: `-11.29%`
- `Sharpe`: `1.708`

#### Best balanced candidate

- universe:
  - `SPY|QQQ|MTUM|QUAL|USMV|VUG|VTV|RSP|IAU|XLE|TIP|TLT|IEF|LQD|VNQ|EFA`
- `top = 2`
- `rebalance interval = 3`
- `Score Horizons = 1/3/6/12`
- `risk-off = cash_only` 또는 `defensive_bond_preference`

결과:

- `CAGR`: `16.25%`
- `MDD`: `-10.59%`
- `Sharpe`: `2.171`

#### Best defensive candidate

- universe:
  - `SPY|QQQ|IWM|IWN|IWD|MTUM|QUAL|USMV|EFA|VNQ|TLT|IEF|LQD|IAU|XLE|TIP`
- `top = 3`
- `rebalance interval = 3`
- `Score Horizons = 1/3/6/12`
- `risk-off = cash_only`

결과:

- `CAGR`: `12.04%`
- `MDD`: `-9.79%`
- `Sharpe`: `1.833`

쉬운 뜻:

- 이번엔 단순히 한 조합이 target을 넘은 게 아니라,
  **공격형 / 균형형 / 방어형 세 갈래 모두에서 실전 기준을 넘는 후보가 나왔다.**
- 그 중에서도 `interval=3`이 생각보다 강했다.
- 즉 GTAA는 universe 구성만이 아니라 cadence 선택도 실전 성능에 매우 중요하다.

### GTAA 실전 후보 판정표

| Candidate | 역할 | 권장 Contract | CAGR | MDD | 강점 | 주의점 | 현재 판정 |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `U3 Commodity Candidate Base` | 공격형 | `month_end`, `top=2`, `interval=3`, `1/3/6` | `16.66%` | `-11.29%` | commodity / inflation 축이 강할 때 가장 높은 복리 기대 | commodity 민감도가 높아 regime 변동에 더 흔들릴 수 있음 | `real-money candidate` |
| `U1 Offensive Candidate Base` | 균형형 | `month_end`, `top=2`, `interval=3`, `1/3/6/12` | `16.25%` | `-10.59%` | growth + quality + style diversification이 함께 살아 있고 Sharpe가 가장 좋음 | offensive 성격이 남아 있어 cadence 민감도는 추가 점검 필요 | `real-money candidate` |
| `U5 Smallcap Value Candidate Base` | 방어형 | `month_end`, `top=3`, `interval=3`, `1/3/6/12` | `12.04%` | `-9.79%` | 낙폭이 가장 안정적이고 defensive baseline으로 읽기 좋음 | CAGR은 offensive / balanced 후보보다 낮음 | `real-money candidate` |

쉬운 뜻:

- `U3`는 가장 공격적으로 복리를 밀어보는 후보다.
- `U1`은 수익과 안정성의 균형이 가장 좋아서,
  지금 기준으로는 **가장 먼저 기본 후보로 검토할 만한 조합**이다.
- `U5`는 수익을 조금 덜 가져가더라도,
  낙폭을 가장 안정적으로 관리하는 방어형 기준점으로 쓰기 좋다.

## Near Misses

### 가장 공격적인 조합

- universe:
  - `SPY|QQQ|VUG|MTUM|QUAL|USMV|XLE|IAU|TIP|TLT|LQD|VNQ|ACWV`
- `top = 2`
- `rebalance interval = 1`
- `Score Horizons = 1/3`

결과:

- `CAGR`: `14.56%`
- `MDD`: `-19.86%`

해석:

- CAGR은 매우 강했지만,
  MDD가 목표인 `-16%`를 넘지 못했다.

### 가장 방어적인 조합

- `top = 4`
- `rebalance interval = 2`
- `Score Horizons = 1/3`

결과:

- `CAGR`: `8.98%`
- `MDD`: `-9.47%`

해석:

- 낙폭은 매우 좋았지만,
  CAGR이 `9%`에 아주 조금 못 미쳤다.

## 실무적 해석

이번 결과는 GTAA가 다음 두 가지 성격을 동시에 가질 수 있음을 보여준다.

1. 공격형
   - `top=2`
   - `interval=3`
   - `1/3/6` horizon
   - commodity / inflation 축을 강하게 쓰는 편이 가장 높은 CAGR을 만들었다
2. 균형형
   - `top=2`
   - `interval=3`
   - `1/3/6/12` horizon
   - growth + quality + style diversification 조합이 Sharpe까지 가장 좋았다
3. 방어형
   - `top=3`
   - `interval=3`
   - `1/3/6/12` horizon
   - smallcap/value 축을 유지하면서도 MDD를 -10% 안쪽으로 관리할 수 있었다

즉 실전 기준으로는
**`month_end`, `interval=3`, `top=2~3`**
가 가장 유망한 contract 패턴으로 보인다.

## Phase 12 결론

- 이번 탐색의 최종 결론은:
  **GTAA에서 `CAGR >= 9%`와 `MDD >= -16%`를 동시에 만족하는 후보를 다수 찾았다.**
- 가장 좋은 offensive candidate는:
  - `SPY|QQQ|XLE|COMT|IAU|GLD|QUAL|USMV|TIP|TLT|IEF|LQD|VNQ|EFA|MTUM`
  - `top=2`
  - `interval=3`
  - `Score Horizons = 1/3/6`
- 가장 좋은 balanced candidate는:
  - `SPY|QQQ|MTUM|QUAL|USMV|VUG|VTV|RSP|IAU|XLE|TIP|TLT|IEF|LQD|VNQ|EFA`
  - `top=2`
  - `interval=3`
  - `Score Horizons = 1/3/6/12`
- 가장 좋은 defensive candidate는:
  - `SPY|QQQ|IWM|IWN|IWD|MTUM|QUAL|USMV|EFA|VNQ|TLT|IEF|LQD|IAU|XLE|TIP`
  - `top=3`
  - `interval=3`
  - `Score Horizons = 1/3/6/12`
- 이번 메인 환경 재검증 기준 defensive candidate 성과는:
  - `CAGR 12.04%`
  - `MDD -9.79%`
  - `Sharpe 1.833`
- 이 결과는 current Phase 12 기준에서
  **실전형 GTAA candidate가 이미 존재한다**는 뜻이다.
