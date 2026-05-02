# Phase 12 GTAA Interval-1 Default Rebase Analysis

## 목적

- `GTAA`의 기본 `Signal Interval`을 `2`에서 `1`로 바꾼다.
- 그리고 interval default가 바뀐 상태에서,
  현재 주요 GTAA preset과 최근에 찾은 상위 후보군을 다시 같은 계약으로 비교한다.

쉬운 뜻:

- 예전에는 GTAA가 기본적으로 `격월` 신호였다.
- 이제는 기본을 `매월` 신호로 바꾸고,
  그 기준에서 어떤 universe가 더 좋아 보이는지 다시 보는 작업이다.

## 이번에 바뀐 점

- GTAA `Single Strategy` 기본 `Signal Interval` = `1`
- GTAA `Compare` 기본 `Signal Interval` = `1`
- `History -> Load Into Form`
- `Saved Portfolio -> Load Into Compare`
- sample/runtime fallback

도 모두 같은 기본값으로 맞췄다.

즉:

- 화면에서 새로 GTAA를 열면 기본이 `1`
- 예전 history record를 불러와도 값이 있으면 그 값을 존중
- 값이 없을 때의 fallback은 이제 `1`

## 비교 계약

- strategy: `GTAA`
- option: `month_end`
- top assets: `3`
- signal interval: `1`
- minimum price: `5.0`
- transaction cost: `10 bps`
- benchmark: `SPY`
- normalized comparison start: `2016-08-31`
- end: `2026-04-02`

왜 `2016-08-31`로 맞췄는가:

- `PDBC`를 포함한 universe는 usable history 시작이 더 늦다.
- `DBC` 또는 `No Commodity` universe는 더 이른 구간부터 실행 가능하다.
- 그대로 비교하면 일부 조합이 시작일에서 유리해질 수 있어서,
  이번 표는 **공통 시작점**으로 다시 맞춘 비교를 메인으로 사용했다.

## 비교 대상

1. `GTAA Universe`
2. `GTAA Universe (DBC)`
3. `GTAA Universe (No Commodity Sleeve)`
4. `GTAA Universe (COMT + QUAL + USMV)`
5. `GTAA Universe (No Commodity + QUAL + USMV)`
6. `Base + QQQ + QUAL + USMV`
7. `Base + QQQ + XLE + IAU + TIP`
8. `Base + QQQ + QUAL + USMV + XLE + IAU`

## 결과

| Rank | Universe | CAGR | MDD | Sharpe | End Balance | Estimated Cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Base + QQQ + QUAL + USMV + XLE + IAU | 11.41% | -21.96% | 0.877 | 28,150.50 | 559.91 |
| 2 | Base + QQQ + XLE + IAU + TIP | 10.08% | -21.60% | 0.786 | 25,086.34 | 524.70 |
| 3 | GTAA Universe (No Commodity + QUAL + USMV) | 8.87% | -16.17% | 0.796 | 22,557.07 | 513.75 |
| 4 | GTAA Universe (DBC) | 8.75% | -15.09% | 0.795 | 22,328.16 | 534.80 |
| 5 | Base + QQQ + QUAL + USMV | 8.74% | -27.91% | 0.748 | 22,297.94 | 485.69 |
| 6 | GTAA Universe (COMT + QUAL + USMV) | 8.58% | -16.98% | 0.767 | 21,993.66 | 522.13 |
| 7 | GTAA Universe (No Commodity Sleeve) | 8.06% | -16.71% | 0.731 | 21,010.84 | 493.41 |
| 8 | GTAA Universe | 6.36% | -26.20% | 0.585 | 18,041.30 | 478.90 |

## 핵심 해석

### 1. interval = 1 기준에서도 `QQQ + IAU + XLE` 축이 가장 강했다

상위 2개 결과의 공통점:

- `QQQ`
- `IAU`
- `XLE`

해석:

- `QQQ`는 공격 성장축
- `IAU`는 금 / 대체자산 보조축
- `XLE`는 경기민감 / 에너지 축

이 셋이 같이 들어가면,
현재 GTAA score 구조에서 offensive 구간과 inflation/cycle 구간을 동시에 더 잘 받쳐주는 것으로 보인다.

### 2. `QUAL`, `USMV`는 여전히 보조 broadener로 읽는 편이 맞다

- `Base + QQQ + QUAL + USMV`
  만으로도 개선은 있다.
- 하지만 최상위 조합은
  `QUAL`, `USMV`만이 아니라 `XLE`, `IAU`까지 함께 들어간 경우였다.

즉:

- `QUAL`, `USMV`는 나쁘지 않다.
- 하지만 이번 계약에서는 주연이 아니라 보조 카드에 가깝다.

### 3. 현재 기본 `PDBC` preset은 interval = 1에서도 약하다

- `GTAA Universe`
  - CAGR `6.36%`
  - MDD `-26.20%`

이 결과는 같은 interval = 1 기준에서도
다른 주요 조합보다 확실히 약했다.

의미:

- 단순히 interval을 `2 -> 1`로 바꾼다고 해서
  현재 `PDBC` 기본 universe의 약점이 사라지지는 않았다.

### 4. preset만 놓고 보면 가장 강한 쪽은 여전히 `No Commodity + QUAL + USMV` 또는 `DBC`

현재 UI에 이미 있는 preset만 기준으로 보면:

- 더 높은 CAGR: `GTAA Universe (No Commodity + QUAL + USMV)`
- 더 낮은 MDD: `GTAA Universe (DBC)`

즉:

- 수익 우선이면 `No Commodity + QUAL + USMV`
- 낙폭 우선이면 `DBC`

로 읽는 게 자연스럽다.

### 5. `COMT + QUAL + USMV`는 중간권 대안이다

- `GTAA Universe (COMT + QUAL + USMV)`
  - CAGR `8.58%`
  - MDD `-16.98%`

해석:

- `PDBC` 기본보다는 낫다.
- 하지만 이번 기준에서는
  `No Commodity + QUAL + USMV`
  또는 `DBC`
  를 넘는 대안으로 보이진 않았다.

## 실무적 결론

### 현재 default contract 기준 최우선 후보

- `Base + QQQ + QUAL + USMV + XLE + IAU`

왜:

- 현재 interval = 1 기준 전체 비교에서 CAGR이 가장 높고
- MDD도 과도하게 나쁘지 않다
- 이번 GTAA 계약에서 가장 설득력 있는 offensive + alternative + cyclicality 조합이다

### UI에 이미 있는 preset 중에서는

1. `GTAA Universe (No Commodity + QUAL + USMV)`
2. `GTAA Universe (DBC)`

를 먼저 계속 비교해보는 것이 좋다.

### 현재 기본 `GTAA Universe (PDBC)`는

- default로 남아 있더라도
- 현재 성과 기준으로는 우선순위가 낮다

즉:

- "기본값"과 "가장 좋은 preset"은 현재 다르다.
- 이 부분은 다음 pass에서 preset 기본값까지 바꿀지 다시 검토할 수 있다.

## 다음 액션 제안

1. 현 상태 그대로 `Signal Interval = 1`을 GTAA 기본값으로 유지
2. 다음 비교는 아래 중 하나로 좁히기
   - `GTAA Universe (No Commodity + QUAL + USMV)`
   - `GTAA Universe (DBC)`
   - `Base + QQQ + QUAL + USMV + XLE + IAU`
3. 다음 pass에서 필요하면
   - 이 상위 manual universe를 preset으로 노출
   - 현재 기본 `PDBC` preset을 유지할지 재검토
