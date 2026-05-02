# Phase 12 ETF AUM And Spread Policy First Pass

## 목적

- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`

이 3개 ETF 전략에 "현재 시점 기준으로 봤을 때, 너무 작은 ETF이거나 현재 호가 스프레드가 너무 넓은 ETF는 아닌지"를 읽을 수 있는 운용 가능성 정책을 first pass로 붙인다.

쉬운 뜻:
- 이전에는 ETF 전략에서
  - 최소 가격
  - 거래 비용
  - benchmark
  중심으로만 실전성을 읽었다.
- 이번에는 여기에
  - ETF 규모(`AUM`)
  - 현재 bid/ask spread
  기준까지 더해서
  "이 ETF를 지금 실제로 쓰기 부담스러운지"를 추가로 읽게 만든 것이다.

## 이번에 추가된 것

### 1. `nyse_asset_profile` 스키마 확장

ETF 운용 가능성 정책을 위해 asset profile 계층이 아래 필드를 저장한다.

- `exchange`
- `fund_family`
- `total_assets`
- `bid`
- `ask`
- `bid_size`
- `ask_size`

의미:
- `total_assets`
  - ETF 현재 운용자산 규모
- `bid` / `ask`
  - 현재 호가
- `fund_family`
  - ETF 운용사/패밀리 정보

현재 역할:
- 이 필드들은 strict annual stock 전략용이 아니라,
  ETF 전략군의 current-operability 판단에 사용된다.

### 2. 새 실전형 입력값

ETF 전략 3종의 single / compare form에 아래 입력이 추가되었다.

- `Min ETF AUM ($B)`
- `Max Bid-Ask Spread (%)`

쉬운 뜻:
- `Min ETF AUM ($B)`
  - 이 값보다 너무 작은 ETF는 실전형 관점에서 주의 신호로 본다.
- `Max Bid-Ask Spread (%)`
  - 현재 bid/ask 차이가 이 값보다 너무 넓으면 실전형 관점에서 주의 신호로 본다.

기본값:
- `Min ETF AUM ($B) = 1.0`
- `Max Bid-Ask Spread (%) = 0.50%`

### 3. ETF Operability Policy surface

runtime은 현재 선택한 ETF universe에 대해
asset profile current snapshot을 읽고 아래를 계산한다.

- `etf_symbol_count`
- `etf_profile_symbol_count`
- `etf_aum_available_count`
- `etf_spread_available_count`
- `etf_aum_pass_count`
- `etf_spread_pass_count`
- `etf_operability_clean_pass_count`
- `etf_operability_clean_coverage`
- `etf_operability_data_coverage`
- `etf_aum_failed_symbols`
- `etf_spread_failed_symbols`
- `etf_operability_missing_data_symbols`
- `etf_operability_status`

상태값:
- `normal`
  - 데이터와 기준이 충분히 무난함
- `watch`
  - 일부 ETF가 정책에 걸리거나, coverage가 조금 부족함
- `caution`
  - 정책 위반 또는 data gap이 커서 승격 보류가 맞음
- `unavailable`
  - ETF profile/current quote 정보가 부족해서 판단 근거가 약함

### 4. 승격 판단과 연결

이 operability status는 `promotion_decision`에도 반영된다.

현재 규칙:
- `etf_operability_status = normal`
  - 다른 조건도 괜찮으면 `real_money_candidate` 가능
- `watch`
  - 결과는 보되 추가 검토 필요
- `caution` / `unavailable`
  - 현재는 `hold` 쪽으로 읽는다

## 노출 위치

- single form / compare override
  - `Min ETF AUM ($B)`
  - `Max Bid-Ask Spread (%)`
- `Real-Money`
  - `ETF Operability Policy`
  - `Policy Status`
  - `Clean Coverage`
  - `AUM/Spread failed symbols`
  - missing-data preview
- `Execution Context`
  - `Min ETF AUM`
  - `Max Bid-Ask Spread`
  - `ETF Operability Status`
- `Compare > Strategy Highlights`
  - `Min ETF AUM ($B)`
  - `Max Spread (%)`
  - `ETF Operability`
- history / `Load Into Form`
  - contract 값 복원

## 현재 경계

- 이건 `current-operability first pass`다.
- 아직 하지 않은 것:
  - point-in-time AUM / spread history
  - ETF strategy actual-trade blocking rule
  - AUM과 spread를 직접 turnover/cost 모델에 합치는 것
  - intraday liquidity / creation-redemption 구조 해석

즉 현재 의미는:
- "이 전략이 지금 쓰는 ETF 묶음이 현재 시점 기준으로 너무 작거나 너무 비효율적으로 보이지는 않는가"를
  promotion/readout 관점에서 먼저 읽는 것이다.
- 아직 "그 ETF는 과거 그 시점에도 같은 operability였다"까지 보장하는 것은 아니다.
