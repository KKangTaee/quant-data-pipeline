# Futures Monitor UI V2 Plan

## 이걸 하는 이유?

현재 `Overview > Futures Monitor`는 수집 / 검증 기능은 갖췄지만 Macro Thermometer, Candles, Shock Board, Provider Run을 동급 탭으로 분리해 시장 해석과 실제 가격 움직임을 동시에 읽기 어렵다. 수집 control도 prototype 버튼처럼 보여 사용자가 데이터 상태를 먼저 이해하기보다 수동 작업을 떠올리게 만든다.

이번 V2 skeleton은 Futures Monitor를 시장 모니터링 workspace처럼 재배치한다.

## Scope

- Futures Monitor 상단 command center / data feed 상태 표현 개선.
- Macro Thermometer와 Candles를 같은 화면에 동시 노출.
- Shock Board와 Provider Run은 하단 diagnostics로 강등.
- 자동 수집 fragment가 전체 body를 다시 그리는 느낌을 줄이고 chart workspace 중심으로 갱신.
- 새 chart dependency 없이 기존 Streamlit / Altair / CSS로 1차 개선.

## Non-goals

- live trading, order, broker/account 연결, auto rebalance 없음.
- yfinance provider 특성 변경 없음.
- Macro Thermometer scoring / validation logic 변경 없음.
- 새 DB table 없음.

## Acceptance

- Futures Monitor 첫 화면에서 Macro Thermometer summary와 4개 mini candle chart를 동시에 볼 수 있다.
- Data feed 상태가 상단에서 Fresh / Review / Stale 계열로 읽힌다.
- Shock Board / Provider Run은 하단 diagnostics expander로 이동한다.
- 수동 refresh 후 불필요한 explicit `st.rerun()`을 줄인다.
- Browser QA screenshot으로 desktop 화면을 확인한다.
