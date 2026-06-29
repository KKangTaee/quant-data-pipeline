# GTAA Result Cadence Monthly Valuation Status

## 2026-06-29

- User request: GTAA `interval=4` 결과가 마지막 리밸런싱일 `2026-02-27`에서 멈추지 않고, 현재 탐색 종료일 기준 마지막 거래 가능 row까지 이어지게 수정.
- Interpretation: 리밸런싱 cadence와 결과 valuation cadence를 분리한다.
- User-approved design: 매월 후보 신호는 보여주되, 실제 `Next Ticker` / `Next Balance`는 리밸런싱월에만 변경한다.
- Implementation: GTAA runtime은 period row를 `.interval(...)`로 줄이지 않고, `GTAA3Strategy(rebalance_interval=...)`가 실제 holdings 변경 cadence를 소유한다.
- Implementation: `append_latest_common_row(...)`로 월말 row 뒤에 요청 종료일 이하 최신 공통 거래일 row를 보강한다.
- DB smoke: 요청 종료일 `2026-06-29` 실행은 현재 DB coverage상 `SOXX/MTUM/QUAL/USMV`가 `2026-03-16`에서 멈춰, 결과 종료일이 최신 공통 거래일 `2026-03-16`이 됐다.
- Verification: focused / broader unit tests, py_compile, DB-backed smoke, `git diff --check` 통과.
