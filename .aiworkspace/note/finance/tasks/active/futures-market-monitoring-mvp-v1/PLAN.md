# Futures Market Monitoring MVP V1 Plan

## 이걸 하는 이유?

미국장과 한국장 현물 개장 전 선물 시장에서 급격한 움직임을 먼저 확인할 수 있도록 `Workspace > Overview`에 read-only futures monitor를 추가한다.

## Scope

- `yfinance` 기반 주요 선물 1분봉 OHLCV 수집
- MySQL 저장과 idempotent UPSERT
- Streamlit-free service read model
- `Workspace > Overview > Futures Monitor` 탭
- Overview Data Health futures 상태
- runbook / durable docs sync

## Non Goals

- broker order, live approval, auto rebalance
- exchange-grade real-time 보장
- public chart site scraping
- persistent push notification
- KRX futures integration

## Proposed File Areas

| Area | Files |
| --- | --- |
| DB schema | `finance/data/db/schema.py` |
| Collector | `finance/data/futures_market.py` |
| Job wrapper | `app/jobs/ingestion_jobs.py`, `app/jobs/run_history.py` |
| Service | `app/services/futures_market_monitoring.py` |
| Overview UI | `app/web/overview_dashboard.py`, `app/web/overview_ui_components.py` |
| Tests | `tests/test_service_contracts.py` or focused test file |
| Docs | `.aiworkspace/note/finance/docs/data/`, `.aiworkspace/note/finance/docs/architecture/`, `.aiworkspace/note/finance/docs/runbooks/` |

## Done Criteria

- Futures collector writes normalized 1m OHLCV and run diagnostics.
- Overview tab renders without provider fetch during normal read.
- Stale / missing / failed source states are visible.
- Tests / compile / diff checks pass.
- Browser QA screenshot is captured if the app can run.
