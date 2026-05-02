# Phase 14 Test Checklist

## 목적

- Phase 14에서 추가된 calibration / reference / history surface가
  현재 UI에서 자연스럽게 읽히는지 수동으로 확인한다.
- 이번 checklist는
  threshold를 실제로 바꾸는 것이 아니라,
  **왜 전략이 hold가 되는지 product가 더 설명 가능해졌는지**
  를 검수하는 데 초점을 둔다.

## 추천 실행 순서

1. `Overview` 현재 상태 확인
2. `Reference > Guides` 확인
3. `Reference > Glossary` 확인
4. strict annual `Advanced Inputs > Real-Money Contract` 도움말 확인
5. strict annual factor 확장 옵션 확인
6. `History` gate snapshot 확인
7. representative strict annual / ETF run 1개씩 다시 읽기

## 1. Overview 상태

- 앱 상단 `Overview`
- 확인:
  - `현재 상태` metric이 `Phase 14 Practical Closeout`로 보이는지
  - 현재 phase가 kickoff가 아니라 closeout 상태로 읽히는지

## 2. Guides - Real-Money Contract 해설

- `Reference > Guides`
- `Real-Money Contract 값 해설`
- 확인:
  - 공통 입력 / strict annual 전용 / ETF 전용 구간이 나뉘어 있는지
  - 각 항목이 무엇을 뜻하는지와 왜 필요한지가 한국어로 보이는지
  - 결과에서 어디에 영향을 주는지도 같이 읽히는지

## 3. Guides - 단계형 사용 흐름

- `Reference > Guides`
- `테스트에서 상용화 후보 검토까지 사용하는 흐름`
- 확인:
  - `1단계 ~ 8단계`가 순서대로 보이는지
  - `Backtest -> Real-Money -> Hold 해결 -> Compare -> History` 흐름이 자연스러운지

## 4. Glossary 검색

- `Reference > Glossary`
- 확인:
  - `Gate Calibration`
  - `Rolling Window`
  - `Real-Money Contract`
  - `Deployment Readiness`
  - `ETF Operability`
  검색 시 설명이 걸리는지
  - 제목 검색과 본문 검색이 모두 되는지

## 5. Strict Annual 툴팁 / help box

- `Backtest > Single Strategy`
- `Quality / Value / Quality + Value > Strict Annual`
- `Advanced Inputs > Real-Money Contract`
- 확인:
  - `Min Avg Dollar Volume 20D ($M)` 툴팁에
    `close × volume` 기반 20일 평균 거래대금 설명이 보이는지
  - `Min Liquidity Clean Coverage (%)` 툴팁에
    종목-level 필터와 strategy-level `Liquidity Policy` 연결 설명이 보이는지
  - 아래 항목 툴팁에 “왜 필요한지” 설명이 보이는지
    - `Max Underperformance Share (%)`
    - `Min Worst Rolling Excess (%)`
    - `Max Strategy Drawdown (%)`
    - `Max Drawdown Gap vs Benchmark (%)`
  - `rolling 구간`이 moving comparison window라는 설명이 field 주변에서 읽히는지

## 6. Strict Annual factor 확장 옵션

- `Backtest > Single Strategy`
- `Quality > Strict Annual`
- factor selector 확인
- 기대:
  - 아래 quality factor가 추가 옵션으로 보이는지
    - `interest_coverage`
    - `ocf_margin`
    - `fcf_margin`
    - `net_debt_to_equity`
- `Value > Strict Annual`
- 기대:
  - `liquidation_value`가 추가 옵션으로 보이는지
- 확인:
  - default factor가 강제로 바뀌지 않고
    선택 가능한 옵션만 넓어진 형태인지

## 7. History gate snapshot

- strict annual 또는 ETF 한 번 실행
- `History > Detail`
- `Context` 영역 확인
- 기대:
  - `gate_snapshot` 표가 보이는지
  - 아래 항목 중 실행 결과에 해당하는 값이 들어오는지
    - `Promotion`
    - `Shortlist`
    - `Probation`
    - `Monitoring`
    - `Deployment`
    - `Validation`
    - `Benchmark Policy`
    - `Liquidity Policy`
    - `Validation Policy`
    - `Guardrail Policy`
    - `ETF Operability`
    - `Rolling Review`
    - `Out-Of-Sample Review`
    - `Price Freshness`
  - schema v2 history record가 gate snapshot을 남긴다는 설명 문구가 보이는지

## 8. Strict Annual repeated hold 해석

- representative strict annual run 1개 실행
- `Real-Money` 확인
- 기대:
  - `Validation`
  - `Validation Policy`
  - `Rolling Review`
  - `Hold 해결 가이드`
  가 서로 연결되어 읽히는지
  - `Hold 해결 가이드`가 현재 판단 탭에 있고,
    blocker 위치와 바로 해볼 일을 안내하는지

## 9. ETF repeated hold 해석

- ETF 전략 1개 실행
- `Real-Money > 실행 부담`
- 기대:
  - `ETF Operability`
  - `data coverage / clean coverage`
  - missing-data 성격의 경고가 읽히는지
  - AUM / spread 숫자를 바꾸는 것과 coverage 해석이 다른 문제라는 점이 surface에서 이해 가능한지

## 10. Phase 14 한 줄 판단 기준

- 이번 checklist는
  “threshold를 지금 당장 바꿨는가”
  를 보는 것이 아니라,
  **hold / watch / blocked가 왜 나오는지 product가 더 설명 가능해졌는지**
  를 보는 checklist다.

