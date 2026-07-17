# Risks

- EIA weekly dates and daily market dates must not be presented as the same horizon.
- `^GSPC` may be absent from local price history; `SPY` fallback must remain explicit.
- Eight actual S&P EPS quarters may be unavailable; the earnings path must fail independently.
- Copper remains partial until an approved global activity series is connected.
- Continuous futures include contract-roll effects.
- 2026-07-17 actual DB에는 공식 actual/as-reported S&P EPS 완료 분기가 없어 earnings path가 `UNAVAILABLE`이다. Shiller/estimate로 대체하지 않는다.
- 달러의 국가 간 상대금리와 구리의 글로벌 활동지표는 아직 연결하지 않아 각각의 관련 coverage는 `PARTIAL`이다.
- 경제사이클 자체 publication status `LIMITED`와 자산 경로 coverage는 별도 계약이다. 자산 경로가 `SUFFICIENT`여도 국면 확률이 검증 완료가 되는 것은 아니다.
- Streamlit이 `runOnSave=false`, `fileWatcherType=none`이면 Python 변경 뒤 프로세스 재시작이 필요하다.
