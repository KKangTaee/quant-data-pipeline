# Backtest Runs

Status: Active
Last Verified: 2026-05-12

이 폴더는 새 분석 세션에서 생성된 원본성 backtest report를 연도별로 받는 위치다.

새 report가 들어오면 먼저 `runs/YYYY/`에 저장하고, 이후 장기적으로 의미가 있으면 `strategies/` log나 `candidates/point_in_time/`로 요약을 승격한다.

## Current Locations

| 위치 | 용도 |
|---|---|
| `2026/strategy_search/` | legacy phase13~phase18에서 나온 전략 탐색 / 개선 raw report |
