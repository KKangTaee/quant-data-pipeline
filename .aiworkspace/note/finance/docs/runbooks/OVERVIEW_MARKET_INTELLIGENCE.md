# Overview Market Intelligence Runbook

Status: Active
Last Verified: 2026-05-28

## Purpose

이 runbook은 `Workspace > Overview`의 Market Movers, Sector / Industry, Events 데이터를 운영자가 수동으로 refresh하고 정상 여부를 확인하는 절차를 정리한다.

## When To Use

- 장 시작 후 또는 장중에 daily movers snapshot을 새로 보고 싶을 때
- FOMC calendar row를 갱신해야 할 때
- latest S&P 500 movers 또는 수동 ticker의 upcoming earnings event를 갱신해야 할 때
- Overview Events / Market Movers 화면이 비어 있거나 오래된 것으로 보일 때

## App Startup

```bash
uv run streamlit run app/web/streamlit_app.py --server.port 8501
```

브라우저에서 확인한다.

```text
http://localhost:8501
```

이미 포트가 사용 중이면 다른 포트를 지정한다.

## Refresh Order

1. `Workspace > Ingestion > Overview Market Snapshot`
   - `Collect S&P 500 Universe`를 먼저 실행해 current S&P 500 membership을 갱신한다.
   - `Collect Market Intraday Snapshot`으로 `SP500`, 필요하면 `TOP1000`, `TOP2000` snapshot을 갱신한다.
   - daily movers는 `finance_price.market_intraday_snapshot`의 latest snapshot을 읽는다.

2. `Workspace > Overview > Market Movers`
   - `Coverage`, `Period`, `Sector`, `Top N`을 선택한다.
   - daily period에서 refresh state가 `Update due`, `Stale`, `Failed`이면 `Update Daily Snapshot`을 눌러 새 snapshot을 저장한다.
   - `Rank` 탭에서 symbol-level return ranking을 확인한다.
   - `Sector Pulse` 탭에서 선택한 mover set 안에서 평균 return이 강한 sector를 확인한다.
   - `Returnable Coverage`에서 missing / failed count를 확인한다.
   - `Coverage Diagnostics`에서 missing symbol, reason, recommended action을 확인한다.

3. `Workspace > Overview > Sector / Industry`
   - `Coverage`, `Group`, `Top N`, `Min Symbols`를 선택한다.
   - `Heatmap` 탭에서 Equal Weight, Cap Weighted, Top Symbol return을 함께 비교한다.
   - `Table` 탭에서 구성 종목 수, 대표 symbol, raw return column을 확인한다.

4. `Workspace > Ingestion > Overview Market Event Calendar > FOMC`
   - 기본은 current year와 next year를 수집한다.
   - 결과는 `finance_meta.market_event_calendar`에 `event_type=FOMC_MEETING`으로 저장된다.

5. `Workspace > Ingestion > Overview Market Event Calendar > Earnings`
   - 기본은 `Latest S&P 500 Movers` source를 사용한다.
   - broader coverage는 `S&P 500 Universe Batch`, `Top1000 Batch`, `Top2000 Batch`를 사용한다.
   - broader mode는 `Max Symbols`, `Batch Offset`, `Ticker Cooldown Sec`을 작게 잡아 저빈도로 실행한다.
   - `Nasdaq cross-check`를 켜면 yfinance estimate를 Nasdaq의 무료 earnings calendar endpoint와 날짜 단위로 비교한다.
   - latest movers mode는 stored S&P 500 intraday snapshot이 먼저 있어야 한다.
   - 특정 ticker 확인이 필요하면 `Manual Symbols`를 사용한다.
   - 결과는 `finance_meta.market_event_calendar`에 `event_type=EARNINGS`, `source=yfinance_calendar`, `source_type=provider_estimate`로 저장된다.
   - yfinance-only estimate는 `validation_status=estimate_only`, Nasdaq 확인 row는 `validation_status=cross_checked`, Nasdaq에서 확인하지 못한 row는 `validation_status=not_confirmed`가 된다.
   - 같은 symbol/source의 이전 active estimate는 새 수집 결과가 있으면 `event_status=superseded`로 정리된다.

6. `Workspace > Overview > Events`
   - `All`, `FOMC`, `Earnings` filter를 바꿔 저장 row를 확인한다.
   - `Window`, `Source Type`, `Validation` filter로 캘린더 범위와 source quality를 좁힌다.
   - `Calendar` 탭에서 event count timeline과 날짜별 grouped cards를 확인한다.
   - `Table` 탭에서 DB row-level detail을 확인한다.
   - `Source Type`에서 FOMC official row와 earnings provider estimate row를 구분한다.
   - `Validation`, `Freshness`, `Age Days`, `Event Status`에서 cross-check 여부와 오래된 earnings estimate인지 확인한다.
   - Overview의 refresh buttons도 ingestion job wrapper를 호출한다. UI render 중 직접 외부 source를 scraping하지 않는다.

## CLI Smoke Checks

작은 수동 earnings smoke:

```bash
uv run python - <<'PY'
from app.jobs.ingestion_jobs import run_collect_earnings_calendar
print(run_collect_earnings_calendar(symbols=["AAPL", "MSFT", "NVDA"], symbol_source="manual", lookahead_days=180, max_symbols=10))
PY
```

latest movers source 확인:

```bash
uv run python - <<'PY'
from finance.data.market_intelligence import load_latest_intraday_mover_symbols
print(load_latest_intraday_mover_symbols(universe_code="SP500", top_n=5))
PY
```

## Expected Results

- Market Movers daily snapshot shows `price_mode=Intraday Snapshot` and a recent `snapshot_time_utc`.
- Market Movers daily refresh state shows `Fresh`, `Update due`, `Stale`, `Partial`, or `Failed`.
- Market Movers displays both `Rank` and `Sector Pulse` chart tabs.
- Sector / Industry displays both `Heatmap` and `Table` tabs.
- Missing diagnostics are visible with recommended action when provider rows are absent or incomplete.
- FOMC rows have `source=federal_reserve_fomc_calendar`, `confidence=1.0`, and `Source Type=Official`.
- Earnings rows have `source=yfinance_calendar`, `Source Type=Provider Estimate`, and a validation label.
- Nasdaq cross-checked earnings rows have `Validation=Cross-checked` and higher confidence.
- Earnings rows collected more than 14 days ago show `Freshness=Stale estimate` and a warning.
- Overview Events displays `Calendar` and `Table` tabs with Window / Source Type / Validation filters.
- Overview Events `Latest Collection` updates after a successful collector run.

## Failure Handling

| Symptom | Likely Cause | Action |
|---|---|---|
| Earnings latest movers mode writes no rows | No latest S&P 500 intraday snapshot | Run S&P 500 market snapshot first or switch to manual symbols |
| Some earnings symbols are missing | yfinance calendar has no upcoming date in the selected window | Check `failed_symbols` / `missing_symbols`; retry with wider lookahead or manual source |
| Earnings row is not confirmed | Nasdaq cross-check did not find the same symbol on that event date | Treat as provider estimate only; refresh later or inspect company IR manually |
| Old earnings date remains in DB | Estimate date changed | Overview hides superseded rows by default; inspect DB if an audit trail is needed |
| Market Movers missing count is high | Provider quote rows missing or DB previous close missing | Open `Coverage Diagnostics`, then refresh OHLCV / snapshot source if needed |
| Events tab is empty | Matching collector has not been run or filter is too narrow | Run FOMC / Earnings refresh and select `All` |
| Overview app looks stale after code change | Old Streamlit process still running | Restart the Streamlit server and confirm Runtime / Build metadata in Ingestion |

## Verification Commands

```bash
uv run python -m py_compile app/web/overview_dashboard.py app/web/streamlit_app.py app/jobs/ingestion_jobs.py finance/data/market_intelligence.py
uv run python -m unittest tests.test_service_contracts
uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
git diff --check
```

Expected result:

- service contract tests pass
- UI-engine boundary reports `Result: PASS`
- `git diff --check` has no output
