# Phase 28 History Replay / Load Parity Second Work Unit

## 어떤 문서인가

Phase 28의 두 번째 작업 단위 기록이다.
첫 작업이 전략별 지원 범위를 화면에 보여주는 것이었다면,
이번 작업은 저장된 history 기록을 다시 열 때 어떤 설정이 유지되는지 확인하기 쉽게 만드는 작업이다.

## 쉽게 말하면

백테스트를 한 번 실행하면 history에 기록이 남는다.
그 기록에서 `Load Into Form`이나 `Run Again`을 누르면 예전 설정을 다시 불러오거나 재실행할 수 있다.

이번 작업은 사용자가 history 기록을 고른 뒤,
“이 기록에는 기간, ticker, cadence, factor, overlay, portfolio handling, real-money 설정이 제대로 남아 있나?”
를 표로 먼저 확인할 수 있게 만든다.

## 왜 필요한가

Phase 28의 핵심은 전략 family별 차이를 헷갈리지 않게 만드는 것이다.
Single Strategy와 Compare에서 차이를 보여줘도,
history에서 다시 불러올 때 quarterly가 annual처럼 보이거나,
GRS의 score 설정이 빠지거나,
annual strict의 guardrail reference 값이 사라지면 실제 사용 흐름은 흔들린다.

그래서 history 화면에서도 재진입에 필요한 값이 남아 있는지 보여주는 장치가 필요하다.

## 이번 작업에서 한 일

- `Backtest > History > Selected History Run` 아래에 `History Replay / Load Parity Snapshot` 표를 추가했다.
- 표는 선택한 저장 기록에서 아래 항목의 저장 상태를 보여준다.
  - 전략과 실행 기간
  - Universe / Ticker
  - 결과 데이터 범위
  - Data Trust
  - strict family cadence / factor / contract / overlay
  - annual strict Real-Money / Guardrail / Promotion 기준
  - quarterly prototype의 Real-Money / Guardrail 범위 구분
  - GRS score / cash / trend / ETF real-money 입력
  - GTAA와 기타 ETF 전략의 주요 재실행 입력
- 새로 저장되는 history record에는 아래 값을 추가로 보존한다.
  - `result_rows`
  - `actual_result_start`
  - `actual_result_end`
  - `guardrail_reference_ticker`
  - `requested_tickers`
  - `excluded_tickers`
  - `malformed_price_rows`
  - `price_freshness`

## 기대 효과

- 사용자가 `Load Into Form`을 누르기 전에 어떤 값이 복원될지 먼저 볼 수 있다.
- `Run Again`을 눌렀을 때 같은 설정으로 다시 실행되는지 QA하기 쉬워진다.
- annual strict와 quarterly prototype이 history에서 같은 실전 검증 상태처럼 보이는 위험을 줄인다.
- GRS 같은 price-only ETF 전략도 score, cash, trend 관련 설정이 history에 남아 있는지 확인할 수 있다.

## 주의할 점

- 기존 history record는 새 필드가 없을 수 있다.
- 그런 경우 표에 `누락 가능` 또는 `없음 또는 미사용`이 보일 수 있다.
- 새 필드는 이번 작업 이후 새로 실행한 백테스트 기록부터 더 잘 채워진다.
- 이 표는 투자 판단표가 아니라 재실행 / 복원 QA용 표다.

## 확인 위치

- UI:
  - `Backtest > History > Selected History Run`
  - `History Replay / Load Parity Snapshot`
- 코드:
  - `app/web/pages/backtest.py`
  - `app/web/runtime/history.py`

## 한 줄 정리

Phase 28 두 번째 작업은 history 기록을 다시 열 때
“무엇이 저장됐고 무엇이 복원될 수 있는지”를 먼저 보이게 만든 작업이다.
