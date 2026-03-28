# Phase 6 Market Regime Overlay First Pass

## 구현 범위

- `finance/strategy.py`
  - `quality_snapshot_equal_weight(...)`에 market regime overlay를 추가했다.
- `finance/sample.py`
  - DB-backed strict family sample path에서 benchmark MA data를 구성해 strategy에 전달한다.
- `app/web/runtime/backtest.py`
  - strict annual family runtime wrapper와 quarterly prototype wrapper에 regime 입력을 연결했다.
- `app/web/pages/backtest.py`
  - single / compare / history / interpretation UI에 market regime overlay를 노출했다.
- `app/web/runtime/history.py`
  - market regime meta를 history에 저장하도록 확장했다.

## 구현된 동작

### strategy layer

- strict factor ranking 이후,
  benchmark `Close < MA(window)`이면 final selection을 비우고 현금으로 이동한다.
- 결과 row에는 regime 상태와 blocked ticker 정보를 함께 저장한다.

### sample/runtime layer

- `SPY`, `QQQ`, `VTI`, `IWM` 중 선택한 benchmark의 DB price history를 읽는다.
- snapshot price builder와 동일한 monthly canonical date shaping을 사용한다.
- benchmark row는 `Close`와 `MA(window)`를 포함한 DataFrame으로 strategy에 전달된다.

### UI layer

- strict annual family 3종과 quarterly prototype single form에 아래 입력이 추가되었다.
  - `Enable Market Regime Overlay`
  - `Market Regime Window`
  - `Market Regime Benchmark`
- compare strict annual family 3종도 전략별 advanced input override에서 같은 입력을 가진다.
- `Selection History -> Interpretation`에는
  - `Regime Blocked Events`
  - `Regime Cash Rebalances`
  - `Market Regime Events`
  가 추가되었다.

## 연구용 quarterly prototype

- 새 single-only strategy:
  - `Quality Snapshot (Strict Quarterly Prototype)`
- 의도:
  - strict quarterly quality path를 public default가 아니라
    **research-only prototype**으로 열어두기
- 현재는
  - quality factor
  - trend filter
  - market regime overlay
  까지 single strategy 기준으로 검증 가능하다.

## current semantics

- regime overlay는 rebalance-date only다.
- benchmark가 `risk_off`면 strict factor 후보 전체가 현금으로 이동한다.
- preset universe semantics는 historical mode를 그대로 유지한다.
  - run-level preset universe는 고정
  - stale symbol은 rebalance date availability에 따라 자연스럽게 빠진다.

## known limits

- `Market Regime Overlay`는 아직 annual strict family compare focused validation의 second layer일 뿐,
  독립 전략군은 아니다.
- quarterly prototype은 compare public set에 포함되지 않았다.
- regime signal은 first pass에서 단일 benchmark + 단일 MA rule만 사용한다.
