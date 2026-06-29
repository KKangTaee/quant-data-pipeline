# GTAA Result Cadence Monthly Valuation Plan

## 이걸 하는 이유?

GTAA의 `interval`은 리밸런싱 주기여야 하지만, 현재 DB-backed 경로에서는 입력 row 자체를 interval로 줄여 결과 종료일이 마지막 리밸런싱월에 멈춘다. 사용자는 리밸런싱 월이 아니어도 요청 종료일 기준 마지막 사용 가능 거래일까지 평가 곡선을 보고 싶어 한다.

## Scope

- `finance/strategy.py`: GTAA strategy가 `rebalance_interval`을 직접 소유하게 한다.
- `finance/transform.py`: period-filtered row에 최신 공통 거래일 row를 덧붙이는 순수 helper를 추가한다.
- `finance/sample.py`: GTAA DB/direct sample 경로에서 `.interval(interval)` row thinning을 제거하고, 월말 필터 뒤 최신 공통 거래일 row를 보강한다.
- `tests/`: GTAA cadence contract 테스트를 추가한다.
- 문서: runtime / strategy docs와 root handoff log에 변경 의미만 짧게 남긴다.

## Done

- GTAA `interval=4` 실행 결과가 마지막 리밸런싱월이 아니라 요청 종료 범위의 최신 공통 거래일 row까지 이어진다.
- 비리밸런싱 row에서도 `Raw Selected Ticker`와 `Signal Investable Ticker`는 매월 계산된다.
- 비리밸런싱 row의 `Next Ticker`는 실제 보유 포지션을 유지한다.
- 관련 테스트와 실제 DB-backed smoke가 통과한다.
