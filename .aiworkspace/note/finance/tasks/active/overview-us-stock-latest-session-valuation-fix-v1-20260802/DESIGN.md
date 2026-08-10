# Overview US Stock Latest Session Valuation Fix V1 Design

## 이걸 하는 이유?

미국 개별종목 Graph 2는 예상 EPS와 세 시나리오 가격이 모두 준비되어도 새 달의
첫 거래가 아직 없으면 빈 안내를 표시한다. 달력상 현재 월보다 사용자가 실제로
확인할 수 있는 가장 최근 완료 거래일을 현재 가격 기준으로 사용해야 한다.

## Approved Behavior

- 정상 기본 기준일은 `latest_completed_nyse_session()`이다.
- 주말, 휴장일, 장 시작 전에는 직전 완료 NYSE 거래일까지만 읽는다.
- 최신 완료 세션 가격이 아직 DB에 없으면 저장된 가장 최근 양수 가격 행을 사용한다.
- 가격이 뒤처졌다는 사실은 기존 `data_freshness`가 계속 표시한다.
- Graph 2는 `READY`이면서 `current_price=None`인 모순 상태를 만들지 않는다.
- Graph 1의 60개월 complete-only 분포, EPS/SEP 계산식, React 구조와 copy는 바꾸지 않는다.

## Approaches

1. 완료 거래일 cutoff만 적용: 월초 정상화에는 충분하지만 DB가 월경계를 넘어
   지연되면 Graph 2가 다시 빈다.
2. 최신 가격 행만 선택: 화면은 복구되지만 미완료 달력 월을 계산하는 기준일 의미가
   남는다.
3. 완료 거래일 cutoff와 최신 가격 행 fallback을 함께 적용: 정상 기준일과 stale
   fallback을 모두 보장하므로 이 방식을 사용한다.

## Data Flow

```text
latest_completed_nyse_session
  -> load_us_stock_valuation_inputs(as_of_date=completed session)
  -> monthly PIT rows
  -> latest price-bearing row
  -> current TTM EPS / scenario current price / basis.price
  -> existing freshness comparison and React chart
```

## Error And PIT Handling

- 가격 행은 `price > 0`과 `price_basis_date`가 모두 있는 최신 월만 선택한다.
- 가격 행이 하나도 없으면 기존 BLOCKED/COLLECTABLE 계약을 유지한다.
- latest completed session 뒤의 가격이나 filing을 읽지 않는다.
- stale fallback에서는 가격과 TTM EPS를 같은 월 행에서 가져와 분모·가격 기준을
  어긋나게 만들지 않는다.

## Verification Contract

- 2026-08-01 주말 cutoff가 2026-07-31로 loader에 전달된다.
- 2026-08 결측 가격 행이 payload 끝에 있어도 Graph 2는 2026-07-31 가격을 쓴다.
- AMD 실제 DB payload가 Graph 2 `READY`와 양수 `current_price`를 함께 제공한다.
- 기존 U.S. stock valuation, freshness, Market Context 회귀 테스트가 통과한다.
