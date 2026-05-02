# Phase 12 GTAA DB ETF Group Search

## 목적

- 현재 `GTAA` 기본 universe를 그대로 두고,
  DB에 이미 존재하는 일반 ETF를 추가하거나 일부 sleeve를 바꿔서
  **CAGR는 높이고 MDD는 낮출 가능성이 있는 조합**을 찾는다.
- 이번 실험은 이전 `Signal Interval = 1` 탐색과 다르게,
  **현재 GTAA 기본 계약** 위에서 수행한다.

## 이번 실험 계약

- strategy: `GTAA`
- data path: DB-backed runtime
- start: `2016-01-01`
- end: `2026-04-02`
- timeframe: `1d`
- option: `month_end`
- top assets: `3`
- signal interval: `2`
- minimum price filter: `5.0`
- transaction cost: `10 bps`
- benchmark: `SPY`

쉬운 뜻:

- 이번 비교는 universe만 바꿨다.
- 즉,
  `top=3`, `2개월 cadence`, `월말 signal`, `실전형 first-pass cost contract`
  는 그대로 유지했다.
- 그래서 결과 차이는 대부분
  **어떤 ETF를 후보군에 넣었는가**
  에서 온다고 볼 수 있다.

## 후보 ETF를 어떻게 골랐는가

기본 core:

- `SPY`
- `IWD`
- `IWM`
- `IWN`
- `MTUM`
- `EFA`
- `TLT`
- `IEF`
- `LQD`
- `PDBC`
- `VNQ`
- `GLD`

추가 후보는 DB 기준으로:

- active ETF
- 2016 이후 장기 테스트가 가능한 가격 이력
- 레버리지/인버스가 아닌 일반 ETF
- GTAA에 의미 있는 축을 만들 수 있는 ETF

를 우선했다.

실제로 backfill한 ETF:

- `XLP`
- `XLU`
- `XLV`
- `XLE`
- `SHY`
- `AGG`
- `HYG`
- `IAU`
- `VEU`
- `VWO`
- `EWJ`
- `VUG`
- `VTV`
- `RSP`
- `ACWV`
- `VGK`

## 제외 판단

이번 실험에서는
**개인 투자자가 굳이 피하고 싶은 구조일 가능성이 큰 obvious LP/PTP형 후보는 우선 제외**
했다.

예:

- `USO`
  - DB metadata상 `United States Oil Fund, LP`

또한 이번 라운드는
이미 별도 비교를 했던 `DBC` 중심이 아니라,
**`PDBC` core를 유지한 채 다른 일반 ETF를 섞는 방향**을 먼저 봤다.

## 그룹 설계 방식

이번 그룹은 랜덤으로 만들지 않았다.

다음 다섯 축으로 나눠 설계했다.

1. 공격 성장 강화
   - `QQQ`, `VUG`
2. 품질 / 저변동성 보강
   - `QUAL`, `USMV`, `ACWV`
3. 방어 섹터 보강
   - `XLP`, `XLU`, `XLV`
4. 단기 / 채권 안전판 보강
   - `SHY`, `AGG`, `HYG`, `TIP`
5. 대체자산 / 인플레이션 / 경기민감 보강
   - `IAU`, `COMT`, `XLE`

쉬운 뜻:

- `QQQ`는 강한 상승장 leadership을 주는지 보려는 카드
- `QUAL`, `USMV`는 quality / lower-volatility 보완 카드
- `XLP`, `XLU`, `XLV`는 방어 섹터 카드
- `SHY`, `AGG`, `HYG`, `TIP`은 “채권 메뉴를 더 넓히면 도움이 되는가”를 보는 카드
- `IAU`, `COMT`, `XLE`는 금 / 원자재 / 에너지 축을 넣어
  인플레이션이나 경기순환 구간에서 도움이 되는지 보는 카드다

## 전체 실험 결과

| Rank | Group | CAGR | MDD | Sharpe |
| --- | --- | --- | --- | --- |
| 1 | Base + QQQ + QUAL + USMV + XLE + IAU | 11.50% | -16.69% | 1.184 |
| 2 | Base + QQQ + XLE + IAU + TIP | 11.02% | -16.69% | 1.137 |
| 3 | Base + QQQ + XLE + COMT + IAU + TIP | 10.67% | -21.52% | 1.060 |
| 4 | Base + QQQ + QUAL + USMV | 9.42% | -23.42% | 1.067 |
| 5 | Base + XLE + COMT + IAU + TIP | 8.12% | -21.52% | 0.875 |
| 6 | Base + VUG + VTV + RSP | 7.70% | -24.49% | 0.918 |
| 7 | Base + IAU + COMT + TIP + SHY | 7.34% | -26.41% | 0.790 |
| 8 | COMT Core + QUAL + USMV + XLP + XLU | 6.86% | -22.60% | 0.810 |
| 9 | Base + QUAL + USMV | 6.85% | -25.70% | 0.802 |
| 10 | Base + QUAL + USMV + SHY + TIP | 6.85% | -25.70% | 0.802 |
| 11 | Base PDBC Core | 6.73% | -23.10% | 0.811 |
| 12 | Base + AGG + HYG + SHY + TIP | 6.73% | -23.10% | 0.811 |
| 13 | Base + ACWV + QUAL + USMV + VEU | 6.39% | -27.43% | 0.740 |
| 14 | Base + QUAL + USMV + XLP + XLU | 5.82% | -28.68% | 0.688 |
| 15 | Base + QUAL + USMV + XLP + XLU + SHY + TIP | 5.82% | -28.68% | 0.688 |
| 16 | No Commodity + QUAL + USMV + XLP + XLU | 5.55% | -21.87% | 0.774 |
| 17 | Base + XLP + XLU + XLV + SHY | 5.45% | -30.01% | 0.665 |
| 18 | Base + VEU + VWO + EWJ + VGK | 5.41% | -23.13% | 0.672 |

## 핵심 해석

### 1. 이번 계약에서는 `QQQ`가 가장 강한 개선 축이었다

상위권 조합의 공통점:

- `QQQ` 포함

대표 결과:

- `Base + QQQ + QUAL + USMV + XLE + IAU`
  - CAGR `11.50%`
  - MDD `-16.69%`
- `Base + QQQ + XLE + IAU + TIP`
  - CAGR `11.02%`
  - MDD `-16.69%`
- `Base + QQQ + QUAL + USMV`
  - CAGR `9.42%`
  - MDD `-23.42%`

selection count:

- best group에서 `QQQ`는 `28`회 선택

해석:

- 현재 GTAA score 구조에서는
  강한 성장 리더십 ETF를 universe에 추가하면
  `MTUM`, `IWM/IWN`과 함께 offensive bucket이 더 강해졌다.
- `QQQ`는 “항상 사는 ETF”가 아니라,
  **강한 상승장 구간에서 top-3에 실제로 자주 들어오는 공격축**으로 작동했다.

### 2. `IAU`와 `XLE` 조합이 MDD 개선에 크게 기여했다

대표 결과:

- `Base + XLE + COMT + IAU + TIP`
  - CAGR `8.12%`
  - MDD `-21.52%`
- `Base + QQQ + XLE + IAU + TIP`
  - CAGR `11.02%`
  - MDD `-16.69%`

selection count:

- `IAU`: `25~28`회 수준
- `XLE`: `17`회 수준

해석:

- `IAU`는 기존 `GLD`와 유사하지만,
  현재 GTAA 안에서는 **금 노출이 더 자주 top-3에 살아남는 보조 축**으로 작동했다.
- `XLE`는 경기순환 / 인플레이션 압력 구간에서
  기존 core에 부족했던 에너지 leadership을 보강했다.
- 즉 이번 실험에선
  **성장축은 `QQQ`, 대체/경기민감 방어축은 `IAU + XLE`**
  조합이 가장 잘 먹혔다.

### 3. `QUAL`, `USMV`는 단독 주연보다 보조 카드에 가까웠다

대표 결과:

- `Base + QUAL + USMV`
  - CAGR `6.85%`
  - MDD `-25.70%`
- `Base + QQQ + QUAL + USMV`
  - CAGR `9.42%`
  - MDD `-23.42%`
- `Base + QQQ + QUAL + USMV + XLE + IAU`
  - CAGR `11.50%`
  - MDD `-16.69%`

selection count:

- `QUAL`: best group에서 `9`회
- `USMV`: best group에서 `4`회

해석:

- `QUAL`과 `USMV`는 universe를 나쁘게 만들지는 않았지만,
  이번 계약에서는 **주된 엔진이 아니라 보완재**였다.
- 이 둘만 추가하면 성과 개선은 제한적이었다.
- 하지만 `QQQ`, `IAU`, `XLE` 같은 강한 축과 함께 넣으면
  일부 구간에서 안정화 보조 역할을 했다.

### 4. 추가 채권 메뉴는 거의 효과가 없었다

대표 결과:

- `Base + AGG + HYG + SHY + TIP`
  - `Base PDBC Core`와 사실상 동일
- `Base + QUAL + USMV + SHY + TIP`
  - `Base + QUAL + USMV`와 사실상 동일

해석:

- 기존 core에 이미:
  - `TLT`
  - `IEF`
  - `LQD`
  가 있다.
- 그래서 `AGG`, `HYG`, `SHY`, `TIP`을 더 넣어도
  top-3 momentum + MA filter 구조에서는
  **실제로 선택되지 않거나, 선택되어도 차이를 만들지 못했다.**

즉:

- “채권 메뉴를 더 늘리면 더 좋아질 것”이라는 가설은
  이번 GTAA 계약에서는 지지되지 않았다.

### 5. 방어 섹터만 추가하는 방식은 생각보다 약했다

대표 결과:

- `Base + XLP + XLU + XLV + SHY`
  - CAGR `5.45%`
  - MDD `-30.01%`
- `Base + QUAL + USMV + XLP + XLU`
  - CAGR `5.82%`
  - MDD `-28.68%`

해석:

- `XLP`, `XLU`, `XLV`는 방어적 성격이 있지만,
  이 전략 구조에서는
  **공격 구간의 수익 엔진을 대체할 정도로 강하지 않았다.**
- 일부 시점에서는 top-3에 올라왔지만,
  전체 CAGR과 MDD를 동시에 개선하는 데는 실패했다.

## 최종 권고

### 1순위 권고

`Base + QQQ + QUAL + USMV + XLE + IAU`

이유:

- 전체 실험 중 최고 CAGR
- 동시에 MDD도 가장 낮은 축에 속함
- Sharpe도 최고
- added ETF 중 실제 selection도 충분히 발생

즉:

- 단순 “ETF를 많이 넣어서 운 좋게 좋아진 조합”이 아니라
- **추가한 ETF들이 실제로 전략 안에서 반복적으로 쓰인 조합**
이다.

### 2순위 권고

`Base + QQQ + XLE + IAU + TIP`

이유:

- 1순위보다 약간 단순함
- CAGR과 MDD가 매우 좋음
- 다만 이번 결과에선 `TIP`이 실제 selection 기여가 거의 없어서,
  실무적으로는 `TIP` 없이 더 단순화해도 다시 볼 가치가 있다

### 3순위 권고

`Base + QQQ + QUAL + USMV`

이유:

- 구조가 이해하기 쉽고
- baseline 대비 CAGR 개선이 뚜렷함
- 다만 MDD 개선은 top 2보다 약함

## 실무적으로 무엇을 GTAA에서 수정하면 좋겠는가

현재 기준 권고:

1. `QQQ`를 추가해서 공격 성장축을 보강
2. `IAU`를 추가해서 금 축을 `GLD` 단일에서 넓힘
3. `XLE`를 추가해서 인플레이션 / 경기민감 leadership을 보강
4. `QUAL`, `USMV`는 단독 주연보다 보조 카드로 유지
5. 채권 ETF를 더 많이 넣는 방식은 우선순위를 낮춤

한 줄 권고:

- 지금 GTAA를 더 좋게 바꾸려면,
  **채권을 더 늘리기보다 `QQQ + IAU + XLE` 축을 우선 검토**하는 편이 맞다.

## 참고한 공식 ETF 자료

- QQQ official:
  - https://www.invesco.com/content/invesco/us/en/financial-products/etfs/invesco-qqq-trust-series-1.html
  - https://www.invesco.com/content/dam/invesco/us/en/product-documents/etf/fact-sheet/qqq-invesco-qqq-etf-fact-sheet.pdf
- QUAL official:
  - https://www.blackrock.com/us/individual/products/256101/ishares-msci-usa-quality-factor-etf
  - https://www.blackrock.com/us/individual/literature/fact-sheet/qual-ishares-msci-usa-quality-factor-etf-fund-fact-sheet-en-us.pdf
- USMV official:
  - https://www.blackrock.com/us/individual/products/239695/ishares-msci-usa-minimum-volatility-etf
- XLE official:
  - https://www.ssga.com/us/en/intermediary/etfs/funds/energy-select-sector-spdr-fund-xle/
- IAU official:
  - https://www.blackrock.com/us/partner/products/239561/ishares-gold-trust-fund

## 다음 액션 제안

1. UI preset으로 올릴 필요가 있으면 먼저:
   - `GTAA Universe (QQQ + XLE + IAU + QUAL + USMV)`
   를 추가
2. 그 다음:
   - `QQQ + IAU + XLE`를 중심으로 더 단순한 2차 탐색
3. 마지막으로:
   - out-of-sample 구간 분리
   - interval `1` vs `2` 재검증

