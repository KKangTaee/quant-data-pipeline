# Institutional Portfolios Holding Chart Refresh V1 Plan

Status: Active
Started: 2026-07-12

## 이걸 하는 이유?

보유 기관 조회에서 선택 종목 차트가 비어 보이는 원인을 실제 DB 기준으로 분리하고, 가격 DB에 이미 있는 row는 바로 차트로 연결하며, 가격 row가 없을 때만 사용자가 명시 버튼으로 OHLCV 수집을 실행하게 한다.

## Scope

- `app/services/institutional_portfolios.py`: safe CUSIP-symbol resolver, selected-security price action, curated symbol reverse lookup fallback.
- `app/web/institutional_portfolios.py`: React event -> Python `run_collect_ohlcv` action boundary.
- `app/web/streamlit_components/institutional_portfolios_workbench/`: chart-empty price collection button, pending state, result notice.
- `tests/test_institutional_portfolios.py`: resolver / selected-security / event-boundary regression tests.

## Non-goals

- DB schema 변경.
- external site scraping.
- React에서 직접 yfinance / SEC fetch.
- 추천 / 매매 신호 / live trading / auto rebalance 연결.
