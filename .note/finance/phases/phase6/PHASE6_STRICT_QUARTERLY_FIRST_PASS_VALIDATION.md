# Phase 6 Strict Quarterly First Pass Validation

## target

- strategy:
  - `Quality Snapshot (Strict Quarterly Prototype)`
- status:
  - research-only single strategy candidate

## implementation summary

- runtime wrapper:
  - `run_quality_snapshot_strict_quarterly_prototype_backtest_from_db(...)`
- sample path:
  - quarterly statement shadow factor history 기반
- UI:
  - single strategy only
  - trend filter overlay 지원
  - market regime overlay 지원
  - selection history / interpretation 지원

## smoke result

- universe:
  - `AAPL`, `MSFT`, `GOOG`
- period:
  - `2024-01-01 -> 2026-03-28`
- regime:
  - `SPY < MA200 => cash`
- result:
  - `End Balance = 14066.3`
  - `CAGR = 0.1718`
  - `Sharpe = 1.0931`
  - `MDD = -0.1232`
  - `Regime Blocked = 2`
  - `Selected Events = 18`

## validation interpretation

- quarterly prototype path는 DB-backed strict shadow factor history 기준으로 실제 결과를 반환했다.
- result row에 annual strict family와 같은 overlay / interpretation 컬럼이 남는다.
- single strategy surface에서 research prototype을 열기 위한 최소 contract는 충족한 상태다.

## current decision

- quarterly strict family first candidate는
  **implemented + smoke validated**
  상태다.
- 다만 current chapter에서는
  - wider universe coverage audit
  - compare public exposure
  - public default 승격
  까지 진행하지 않는다.

즉 현재 위치는:

- `research-only prototype`
- `manual UI testing ready`

로 보는 것이 가장 정확하다.
