# Status

Status: Done
Started: 2026-07-07

## Current

- Single Strategy / Portfolio Mix Builder strict annual factor form에서 `Universe 기준`을 Preset 하단으로 올렸다.
- Run 전 Factor Readiness는 실제 검증이 아니라 `Run 이후 실제 사용 데이터 기준으로 확인` preview로 낮췄다.
- 결과 화면은 strict factor bundle의 actual `price_freshness`, `History Excluded Ticker`, `Liquidity Excluded Ticker`를 읽어 post-run Factor Readiness panel을 표시한다.
- 가격 보강 action은 post-run model의 refresh 가능한 티커만 `run_backtest_price_refresh`로 전달한다. provider/source gap은 반복 refresh가 아니라 수동 확인 action으로 남긴다.

## Completed

- 1차: Universe 기준 visible placement / pre-run preview 전환.
- 2차: post-run readiness read model 추가.
- 3차: 결과 화면에서 Data Trust Summary 이후, Practical Validation handoff 이전에 post-run panel 연결.
- 4차: 실제 문제 티커 기준 가격 refresh meta filtering과 provider gap retry-block 유지.
- QA: py_compile, service contract 전체 unittest, Browser QA.
