# Design

- React owner: `app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx`, `style.css`
- Streamlit render boundary: `app/web/overview/market_movers_helpers.py`
- HTML fallback: `app/web/overview/components/market_movers.py`, `common.py`
- Contract tests: `tests/test_service_contracts.py`

React와 fallback에 동일한 `section kicker / section title / section description / status / result headline` 의미를 둔다. 데이터 tone은 status, rail, lane에만 쓰고 제목 계층은 고정한다.
