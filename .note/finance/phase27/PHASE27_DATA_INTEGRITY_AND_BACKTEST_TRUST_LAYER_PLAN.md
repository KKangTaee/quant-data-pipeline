# Phase 27 Data Integrity And Backtest Trust Layer Plan

## 이 문서는 무엇인가

이 문서는 Phase 27에서 데이터 신뢰성과 백테스트 결과 해석을 어떻게 강화할지 정리하는 계획 문서다.

Phase 27은 새 투자 전략을 찾는 phase가 아니다.
백테스트를 실행하거나 결과를 읽을 때, 사용자가 "이 결과가 어떤 데이터 조건에서 나온 것인지"를 놓치지 않게 만드는 phase다.

## 목적

- 백테스트 실행 전후에 데이터 가능 범위와 신뢰성 문제를 더 분명하게 보여준다.
- stale ticker, missing ticker, malformed price row, common-date truncation을 사용자가 이해할 수 있는 경고로 만든다.
- 결과가 이상할 때 전략 문제와 데이터 문제를 분리해서 볼 수 있게 한다.

## 쉽게 말하면

좋은 수익률이 나와도 데이터가 깨져 있거나 특정 ticker 때문에 결과 기간이 짧아졌다면,
그 결과는 그대로 믿기 어렵다.

Phase 27은 백테스트 결과를 보기 전에
"이번 데이터로 어디까지 계산했고, 어떤 ticker가 결과를 줄였고, 무엇을 조심해야 하는지"
먼저 알려주는 안전장치를 만드는 단계다.

## 왜 필요한가

- Phase 24 QA에서 `EEM`, `IWM`, common-date truncation 문제가 실제로 드러났다.
- 일부 전략은 가격 이력 부족 ticker를 제외하거나, 공통 날짜가 짧아져 결과가 예상보다 짧게 나올 수 있다.
- 이런 정보가 결과 상단에 명확히 보이지 않으면 사용자는 전략 성과 문제와 데이터 품질 문제를 혼동할 수 있다.
- 앞으로 후보 추천 / 포트폴리오 제안으로 가려면, 먼저 "백테스트 결과가 어떤 데이터 조건에서 나온 것인가"를 설명할 수 있어야 한다.

## 이 phase가 끝나면 좋은 점

- 사용자는 백테스트 결과를 보기 전에 데이터 문제 여부를 먼저 확인할 수 있다.
- 특정 ticker 때문에 결과 기간이 짧아졌는지 더 쉽게 알 수 있다.
- missing / stale / malformed price 문제가 조용히 묻히지 않는다.
- Phase 28 이후 전략 family parity를 맞출 때, 데이터 신뢰성 표면이 공통 기준으로 쓰일 수 있다.

## 이 phase에서 다루는 대상

- `Backtest > Single Strategy` 실행 전 preflight 표시
- `Latest Backtest Run` 결과 상단의 데이터 신뢰성 요약
- runtime metadata의 result window / price freshness / excluded ticker / malformed row
- Global Relative Strength를 첫 적용 대상으로 한 price-only ETF 전략 경로
- 이후 strict annual / quarterly / compare / saved replay로 확장할 수 있는 공통 표시 방식

## 현재 구현 우선순위

1. Backtest Data Trust Summary 첫 구현
   - 쉽게 말하면: 결과 상단에 "요청 기간 vs 실제 결과 기간, 가격 최신성, 제외 ticker"를 바로 보이게 만든다.
   - 왜 먼저 하는가: 사용자가 가장 먼저 헷갈리는 지점이 "왜 이 기간까지만 계산됐는가"이기 때문이다.
   - 기대 효과: 결과 숫자를 보기 전에 데이터 조건을 먼저 확인할 수 있다.
2. Global Relative Strength price freshness preflight 연결
   - 쉽게 말하면: GRS 실행 전에 ETF universe의 최신 가격 날짜가 서로 맞는지 보여준다.
   - 왜 필요한가: Phase 24에서 GRS가 실제 missing/stale ticker 문제를 드러냈기 때문이다.
   - 기대 효과: 실행 전에 데이터 문제를 발견하고, 실행 후에도 같은 정보를 meta에서 확인할 수 있다.
3. 데이터 문제 문구 한글화 / 해석 정리
   - 쉽게 말하면: 기술적인 warning을 사용자가 이해할 수 있는 문장으로 바꾼다.
   - 왜 필요한가: "stale", "malformed", "common-date" 같은 말만으로는 실제 영향이 잘 보이지 않는다.
   - 기대 효과: 사용자가 데이터 문제를 보고 다음 행동을 판단하기 쉬워진다.
4. compare / history / saved replay까지 확장
   - 쉽게 말하면: 단일 실행뿐 아니라 저장된 실행과 compare 결과에서도 데이터 조건을 잃지 않게 한다.
   - 왜 필요한가: 후보 검토는 단일 실행보다 재실행 / 비교 / 저장 흐름에서 더 많이 흔들린다.
   - 기대 효과: Phase 29 후보 검토 workflow의 신뢰도가 높아진다.

## 이 문서에서 자주 쓰는 용어

- `Data Trust Summary`: 백테스트 결과가 어떤 데이터 조건에서 계산됐는지 보여주는 요약 영역이다.
- `Price Freshness`: ticker별 최신 가격 날짜가 요청 종료일 또는 실제 거래 종료일에 얼마나 가까운지 보는 점검이다.
- `Common Latest Price`: 선택된 ticker들 중 가장 늦게 따라온 최신 가격 날짜다. 이 날짜가 너무 과거면 결과 기간이 짧아질 수 있다.
- `Malformed Price Row`: 가격 컬럼이 비어 있거나 깨져 있어 계산에 영향을 줄 수 있는 행이다.
- `Excluded Ticker`: 이번 실행에서 필요한 가격 이력이나 파생 지표가 부족해 제외된 ticker다.

## 이번 phase의 운영 원칙

- 새 전략 발굴보다 데이터 신뢰성 표시를 우선한다.
- 데이터 문제를 조용히 보정하지 않는다.
- 값을 임의로 채우기보다, 어떤 데이터 때문에 결과가 짧아졌는지 먼저 보여준다.
- 사용자가 명시적으로 분석을 요청하지 않는 한 투자 후보 판정으로 넘어가지 않는다.

## 이번 phase의 주요 작업 단위

1. Backtest Data Trust Summary
   - 결과 bundle metadata에 실제 결과 기간과 row 수를 남긴다.
   - 최신 실행 결과 상단에 데이터 신뢰성 요약을 보여준다.
2. GRS price preflight 연결
   - Global Relative Strength 실행 전 price freshness preflight를 보여준다.
   - 실행 결과 meta에도 price freshness 결과를 남긴다.
3. 공통 warning 문구 정리
   - warning 문구를 사용자 관점의 한글 설명으로 다듬는다.
   - stale / missing / malformed / excluded가 각각 무엇을 의미하는지 결과 화면에서 설명한다.
4. 확장 범위 검토
   - strict annual / quarterly, compare, history, saved replay에서 같은 정보를 어떻게 보일지 정리한다.

## 다음에 확인할 것

- Global Relative Strength 실행 화면에서 Price Freshness Preflight가 보이는지
- 실행 후 Latest Backtest Run 상단에 Data Trust Summary가 보이는지
- excluded ticker와 malformed price row가 숨겨지지 않는지
- Phase 27의 다음 작업을 compare / history 쪽으로 확장할지 결정

## 한 줄 정리

Phase 27은 백테스트 결과를 더 좋게 만드는 phase가 아니라,
그 결과를 믿어도 되는 데이터 조건을 먼저 보여주는 phase다.
