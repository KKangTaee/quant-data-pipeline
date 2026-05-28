# Overview Market Intelligence Acceptance Checklist

Status: Active
Last Updated: 2026-05-28

## 2차 Production Baseline Gate

2차는 prototype을 정식 feature로 굳히기 전의 운영 기준선이다. 목표는 모든 데이터 source를 완성하는 것이 아니라, 현재 제공되는 Market Movers / Sector Leadership / Events를 사용자가 최신성, 부분 실패, source 신뢰도와 함께 판단할 수 있게 만드는 것이다.

## Market Movers

- Daily `Market Movers`는 refresh state를 `fresh / due / stale / partial / failed` 중 하나로 보여준다.
- 5분 이상 지난 daily snapshot은 버튼 근처에서 refresh 필요 상태가 보인다.
- snapshot이 없으면 EOD fallback임을 warning과 status card에서 확인할 수 있다.
- `Returnable Coverage`는 returnable / universe count와 missing / failed count를 보여준다.
- `Coverage Diagnostics`는 missing symbol, reason, recommended action을 보여준다.
- S&P 500, Top1000, Top2000 daily snapshot refresh는 Overview button이 ingestion job wrapper를 호출한다.

## Sector / Industry

- Sector / Industry leadership은 DB에 저장된 price/profile 기반으로 월별 ranking을 보여준다.
- Equal-weight return과 market-cap-weighted return이 함께 보인다.
- 최소 구성 종목 수 기준 때문에 제외된 symbol은 missing diagnostics에서 확인한다.
- 2차에서는 chart polish를 하지 않는다. Visual heatmap/treemap은 4차로 넘긴다.

## Events

- Events tab은 `market_event_calendar` 저장 row만 읽는다.
- `FOMC_MEETING` row는 `Official` source type으로 보인다.
- `EARNINGS` prototype row는 `Provider Estimate` source type으로 보인다.
- earnings estimate가 14일 초과로 오래됐으면 `Stale estimate`와 warning이 보인다.
- All / FOMC / Earnings filter가 유지된다.
- FOMC / Earnings refresh button은 Overview에서 직접 scraping하지 않고 ingestion job wrapper를 호출한다.

## Manual Browser QA

1. Streamlit을 실행한다.

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8501
```

2. `http://localhost:8501`에서 `Workspace > Overview`를 연다.
3. `Market Movers`에서 S&P 500 daily를 선택하고 refresh state, returnable coverage, warning, diagnostics expander를 확인한다.
4. `Sector / Industry`에서 sector와 industry ranking이 비어 있지 않거나, 비어 있으면 DB missing 안내가 보이는지 확인한다.
5. `Events`에서 All / FOMC / Earnings filter를 바꾸고 source type / freshness / age days column을 확인한다.
6. Browser console에 신규 error가 없는지 확인한다.

## Command Gate

```bash
uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard.py app/jobs/ingestion_jobs.py finance/data/market_intelligence.py tests/test_service_contracts.py
uv run python -m unittest tests.test_service_contracts
uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
git diff --check
```

## Remaining After 2차

- Earnings source validation is still 3차 work.
- Earnings lifecycle cleanup for changed estimate dates is still 3차 work.
- Wider low-frequency event collection beyond latest movers is still 3차 work.
- Heatmap / calendar-like visual polish is still 4차 work.
