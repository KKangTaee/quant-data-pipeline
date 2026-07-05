# Backtest Data Trust Price Refresh V1

## 이걸 하는 이유?

Backtest Analysis의 `데이터 기준 요약`은 현재 백테스트가 어떤 DB 가격 기준일로 계산됐는지 알려준다. 사용자가 요청 종료일을 최신으로 넣었는데 DB의 OHLCV가 직전 거래일까지 채워져 있지 않으면, 사용자는 별도 Ingestion 화면으로 이동해 ticker와 기간을 다시 맞춰야 한다. 이 작업은 현재 backtest 결과 화면 안에서 해당 후보의 ticker만 안전하게 갱신할 수 있는 명시적 action을 추가한다.

## Scope

- Backtest 결과의 Data Trust summary에 조건부 `가격 데이터 업데이트` action을 추가한다.
- 주말 / NYSE 휴장일은 최신 필요 기준에서 제외하고, 직전 완료 거래일까지만 갱신 대상으로 본다.
- 실행은 기존 `run_collect_ohlcv` job wrapper를 통과한다.
- 실행 후에는 자동 재백테스트를 하지 않고, 사용자가 `Run Backtest`를 다시 눌러 최신 DB 기준으로 재계산하게 안내한다.

## Non-Goals

- 새 provider / schema / table 추가 없음.
- render path에서 외부 provider 직접 fetch 없음.
- 후보 등록, 2차 검증 전송, Practical Validation / Final Review gate 변경 없음.
- live approval, broker order, auto rebalance 의미 없음.

## Steps

1. 서비스 계약 테스트로 refresh eligibility와 job wrapper 호출 계약을 고정한다.
2. Backtest 전용 price refresh service를 추가한다.
3. Data Trust summary에 조건부 버튼과 실행 결과 표시를 붙인다.
4. 문서 / 실행 로그를 갱신하고 focused QA를 수행한다.
