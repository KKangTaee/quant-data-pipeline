# Runs

## TDD

- 신규 3개 핵심 계약 테스트가 기존 구현에서 실패함을 확인했다.
- 구현 후 decision UI 26 tests 통과.
- Market Movers EOD/action focused service contracts 5 tests 통과.
- NYSE calendar 4 tests 통과.
- closeout 확대 검증: decision UI/NYSE 30 tests와 전체 Market Movers service contract 84 tests, 합계 114 tests 통과.

## Build And Smoke

- `py_compile app/jobs/overview_actions.py app/web/overview/market_movers_helpers.py` 통과.
- `market_movers_workbench npm run build` 통과.
- 실제 DB read-only preflight: latest completed NYSE `2026-07-20`; Weekly 502 / Monthly 501 due, range `2026-07-08~2026-07-21`.
- in-app Browser는 localhost:8530 URL policy로 차단되어 actual screenshot을 생성하지 못했다.
