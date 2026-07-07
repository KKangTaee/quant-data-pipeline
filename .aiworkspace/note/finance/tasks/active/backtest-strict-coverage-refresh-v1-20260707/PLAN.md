# Backtest Strict Coverage Refresh V1 Plan

## 이걸 하는 이유?

Quality / Value strict preset의 `Coverage 100 / 300 / 500` 표현이 실제로는 `finance_meta.nyse_asset_profile` market-cap 후보군인데, 사용자는 이를 백테스트 가능한 종목 coverage로 읽고 있다. CUK / BK처럼 가격 최신성이나 provider 상태가 맞지 않는 종목이 후보군에 들어오면 가격 업데이트 버튼을 눌러도 실행 가능 universe가 재구성되지 않아 같은 경고가 반복된다.

이번 작업은 coverage를 `Base Universe`와 `Runnable Coverage`로 분리하고, 가격 / statement shadow / liquidity를 단계적으로 붙여 실제 백테스트 가능한 후보군으로 읽히게 만든다.

## 단계

1. 현재 strict preset을 `Base Universe`로 명확히 표시한다.
   - 화면: Single Strategy strict Quality / Value, Portfolio Mix Builder strict form
   - 완료조건: 현재 100 / 300 / 500 / 1000이 market-cap 기반 후보군이며 runnable coverage가 아님을 표시한다.

2. Data Trust 1차 데이터 확인에 price freshness / statement coverage 이슈를 실제 리스트로 노출한다.
   - 화면: 백테스트 결과 `데이터 기준 요약`
   - 완료조건: summary가 `확인 필요`이면 하단 issue queue에도 stale / missing 원인이 보인다.

3. `가격 데이터 업데이트`를 `Coverage 최신화` 흐름으로 정리한다.
   - 화면: Data Trust action card
   - 완료조건: refresh 대상은 stale / missing symbols를 우선하고, 실행 후에는 backtest rerun 필요 상태와 미해결 종목을 분리해 안내한다.

4. Runnable coverage backfill 로직을 추가한다.
   - 범위: strict Quality / Value annual candidate pool read path
   - 완료조건: target coverage를 만족하지 못하는 stale / missing 후보는 다음 market-cap rank 후보로 대체 가능한 계약을 만든다.

5. 20일 평균 거래대금 필터를 optional liquidity layer로 추가한다.
   - 범위: strict promotion / investability input, result meta
   - 완료조건: liquidity는 coverage 본체가 아니라 investable coverage 필터로 표시한다.

## 이번 작업에서 하지 않는 일

- Strategy selector 자체를 React로 옮기지 않는다.
- Practical Validation / Final Review gate policy 의미를 임의로 바꾸지 않는다.
- Provider DB schema를 먼저 바꾸지 않는다.
- live approval, broker order, auto rebalance 의미를 추가하지 않는다.
