# Phase 4 Backtest History Enhancement Third Pass

## 목적
이 문서는 Phase 4 Backtest 탭의 persistent history를
단순 조회 화면에서
재실행 준비와 성과 기준 필터링까지 가능한 수준으로 올린
third-pass 구현 기록이다.

## 이번 단계에서 추가한 것

### 1. Metric Threshold Filters
- `Persistent Backtest History`에 metric threshold filter expander를 추가했다.
- 현재 지원 항목:
  - `Min End Balance`
  - `Min CAGR`
  - `Min Sharpe Ratio`
  - `Max Drawdown`

의미:
- 사용자는 저장된 이력 중에서
  일정 성과 기준을 만족한 실행만 빠르게 좁혀볼 수 있다.

### 2. Load Into Form
- single-strategy history record에 대해 `Load Into Form` 액션을 추가했다.
- 지원 전략:
  - `Equal Weight`
  - `GTAA`
  - `Risk Parity Trend`
  - `Dual Momentum`

동작:
- history record를 현재 single-strategy form에 prefill한다.
- 사용자는 값을 미세 조정한 뒤 다시 실행할 수 있다.

### 3. Single-Strategy Prefill Wiring
- strategy별 form에 history payload prefill을 연결했다.
- prefill 대상:
  - universe mode
  - preset / manual tickers
  - start / end
  - timeframe
  - option
  - strategy-specific advanced inputs

### 4. Compare / Weighted Replay Policy 유지
- compare / weighted record는 여전히 `Run Again` / `Load Into Form`을 열지 않았다.
- 이유:
  - 현재 저장되는 context만으로는
    selected strategies별 advanced override를 완전하게 복원하기 어렵기 때문이다.

현재 판단:
- compare / weighted rerun은 기능 부족이 아니라
  replay fidelity를 보장하기 전까지 의도적으로 닫아두는 것이 맞다.

## 사용자 경험 변화

이제 Backtest history는 아래 3단 흐름을 지원한다.

1. filter / sort로 원하는 실행을 찾는다
2. drilldown으로 결과와 입력을 확인한다
3. single-strategy record는 form에 다시 불러와 수정 후 재실행한다

즉 history가 단순 보관소가 아니라
repeatable experiment surface에 가까워졌다.

## 검증
- `python3 -m py_compile app/web/pages/backtest.py app/web/streamlit_app.py`
- single-strategy prefill session-state wiring 점검
- metric threshold filter 렌더링 및 필터 경로 점검

## 관련 코드
- `app/web/pages/backtest.py`
