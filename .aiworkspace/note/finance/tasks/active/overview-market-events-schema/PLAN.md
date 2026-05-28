# Overview Market Events Schema

Status: Active
Started: 2026-05-28

## 이걸 하는 이유?

Overview Events 탭에 FOMC와 earnings calendar를 붙이려면 먼저 무료 수집 source별 결과를 같은 DB table에 저장하는 공통 event contract가 필요하다.
UI는 provider를 직접 파싱하지 않고 `ingestion -> DB -> service/UI read` 흐름을 유지해야 한다.

## Scope

- `finance_meta.market_event_calendar` schema 추가
- FOMC / earnings / future event collector가 공통으로 쓸 persistence helper 추가
- event date range read helper 추가
- Task 5 FOMC collector가 바로 재사용할 수 있는 idempotent UPSERT contract 추가
- data / DB docs와 phase task 상태 갱신

## Out Of Scope

- Fed 공식 페이지 파싱
- earnings source 선택 / 파싱
- Overview Events UI 실데이터 표시
- Events 탭 refresh button

## Verification

- `uv run python -m py_compile finance/data/db/schema.py finance/data/market_intelligence.py tests/test_service_contracts.py`
- `uv run python -m unittest tests.test_service_contracts.MarketIntelligenceEventCalendarContractTests`
- `uv run python -m unittest tests.test_service_contracts`
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `git diff --check`
