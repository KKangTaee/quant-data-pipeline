# Overview Market Intelligence S&P500 Intraday

Status: Active
Started: 2026-05-28

## 이걸 하는 이유?

Market Movers의 1차 구현은 DB에 이미 저장된 daily close 기반이었다.
사용자는 daily movers를 장중에도 전일 종가 대비로 빠르게 보고 싶어 하므로, 무료 소스 범위 안에서 먼저 S&P 500 universe만 준실시간 snapshot으로 검증한다.

## Scope

- S&P 500 universe를 별도 DB snapshot으로 저장
- S&P 500 daily intraday snapshot을 전일 종가 대비 수익률로 저장
- S&P 500 fast path 검증 후 Top 1000 / Top 2000 daily intraday snapshot을 같은 저장 구조로 확장
- Overview Market Movers coverage를 `S&P 500`, `Top 1000`, `Top 2000`로 정리
- daily coverage는 저장된 intraday snapshot을 우선 표시하고, 없으면 EOD DB로 fallback
- yearly period 추가
- Market Movers sector filter 추가
- returnable coverage missing ticker diagnostics 추가

## Out Of Scope

- paid realtime market data
- broker / exchange direct feed
- fully unattended background scheduler
- FOMC / earnings calendar

## Verification

- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
- `uv run python -m unittest tests.test_service_contracts`
- `uv run python -m py_compile finance/data/market_intelligence.py app/jobs/ingestion_jobs.py app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py tests/test_service_contracts.py`
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `git diff --check`
- Browser smoke for Overview Market Movers
