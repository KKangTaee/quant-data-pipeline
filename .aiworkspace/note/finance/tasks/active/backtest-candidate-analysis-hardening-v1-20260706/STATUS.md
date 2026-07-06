# Backtest Candidate Analysis Hardening V1 Status

Status: Complete
Started: 2026-07-06

## 이걸 하는 이유?

후보분석에서 선택 전략과 백테스트 결과, 데이터 기준, 2차 검증 진입 판단이 서로 다른 기준으로 보이면 사용자가 stale 결과를 현재 결과로 오해할 수 있다. 이번 작업은 진단값을 더 늘리는 것이 아니라 잘못된 다음 행동을 막고, 실제로 다시 실행해야 하는 순간을 명확하게 만든다.

## Roadmap

1. 1차: 전략 변경 / Data Trust gate 안전장치.
2. 2차: Quality / Value preset 기준과 최신화 가능성 표시.
3. 3차: Price Freshness Preflight React surface.
4. 4차: 가격 데이터 업데이트 후 rerun-required UX.

## Progress

- 2026-07-06: 코드 원인 파악 완료. `backtest_last_bundle` stale 렌더링, missing `price_freshness.status` gate pass, strict preset basis, price refresh DB-only behavior를 확인했다.
- 2026-07-06: Baseline focused test 실행: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestPresetCatalogContractTests -v` 통과.
- 2026-07-06: 1차 구현 완료. 전략 / family variant 선택이 바뀌면 이전 `backtest_last_bundle`을 숨기고 재실행 안내를 표시한다.
- 2026-07-06: 1차 구현 완료. `price_freshness.status`가 missing / warning / error / 자료제한 상태이거나 제외 / malformed 가격 row가 있으면 Practical Validation 진입을 차단한다.
- 2026-07-06: 1차 QA 완료. focused tests, `py_compile`, `git diff --check`, `tests.test_service_contracts` 전체 483개 통과.
- 2026-07-06: 2차 구현 완료. strict Quality / Value preset 기준을 `nyse_asset_profile` 기반 US stock market-cap order로 명시하고, S&P 최신 구성원 기준이 아님을 화면 note로 노출했다.
- 2026-07-06: 2차 구현 완료. preset target count와 실제 loaded count mismatch, staged 500/1000 preset, static fallback 가능성을 읽기 모델과 UI note로 표시했다.
- 2026-07-06: 2차 QA 완료. focused tests, `py_compile`, `git diff --check`, `tests.test_service_contracts` 전체 486개 통과.
- 2026-07-06: 3차 구현 완료. `Price Freshness Preflight`를 display-only React component로 추가하고, strict preflight report를 React payload로 변환하는 읽기 모델을 붙였다.
- 2026-07-06: 3차 QA 완료. React build, focused tests, `py_compile`, `git diff --check`, `tests.test_service_contracts` 전체 488개 통과.
- 2026-07-06: 4차 구현 완료. 가격 업데이트가 OHLCV DB row를 저장하면 이전 백테스트 결과를 stale로 표시하고, 재실행 전까지 결과 / 2차 진입 판단 / tabs 렌더링을 숨긴다.
- 2026-07-06: 4차 구현 완료. 가격 업데이트 실행 경로는 기존 `run_collect_ohlcv` ingestion job을 사용하며, 목표 테이블은 `finance_price.nyse_price_history`다.
- 2026-07-06: 4차 QA 완료. focused tests, `py_compile`, `git diff --check`, `tests.test_service_contracts` 전체 490개 통과.
