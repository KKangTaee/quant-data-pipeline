# Design

## Current Finding

- `app/web/overview_dashboard.py`는 기준 시점 / 기준일 / 패턴 기간 control을 렌더링하고, selected mode에서 `as_of_date`를 loader에 전달한다.
- `app/web/overview_dashboard_helpers.py`는 `load_overview_market_context_historical_analog(as_of_date, pattern_window)`로 historical analog snapshot을 만든다.
- `app/services/overview_market_context_analog.py`는 `load_price_history(..., end=as_of_date)`로 DB-backed daily prices를 읽고, sector ETF / SPY / comparison symbols pivot matrix를 만든다.
- 실제 계산 기준일은 `analysis_matrix.index.max()`다. 일부 comparison asset의 daily price가 오래되어 공통 matrix가 더 이른 날짜에서 끊기면 `requested_as_of`와 `current_as_of`가 달라질 수 있다.
- 현재 UI는 이를 `계산 기준일`로만 표시해 선택일이 무시된 것처럼 보인다.

## Implementation Direction

1. Service contract
   - `requested_as_of`, `current_as_of`는 유지한다.
   - `as_of_alignment` payload를 추가한다.
     - `requested_as_of`
     - `effective_as_of`
     - `is_aligned`
     - `reason`
     - `limiting_symbols`
     - `latest_by_symbol`
   - 선택일과 실제 계산 기준일이 다르면 `basis_warnings`를 추가한다.

2. Historical analog UI
   - `기준 시점` / `계산 기준일`의 의미를 나눠 표시한다.
   - 요청일이 낮춰진 경우 warning strip으로 `선택일 -> 실제 계산일`을 먼저 보여준다.
   - 기준 ledger label을 `요청 기준`, `실제 계산`, `리더십`, `유사 조건`, `표본` 중심으로 바꾼다.

3. Macro comparison UI
   - `Broad sample`, `Macro 조건 sample`, `추가 조건` 같은 개발자 표현을 줄인다.
   - funnel을 `1. 섹터 상대강도`, `2. GLD 배경`, `3. 금리선물 압력`으로 보여준다.
   - `사용한 조건`은 `표본을 실제로 줄인 조건`, `조건 부족`은 `자료 부족으로 적용 못 한 조건`, `이번 차수 제외`는 `참고만 하는 정보`로 바꾼다.

4. Tests
   - Service test: requested selected date later than common matrix date produces explicit misalignment payload.
   - HTML test: misalignment warning and renamed macro condition groups render.
   - Existing as-of replay tests remain green.
