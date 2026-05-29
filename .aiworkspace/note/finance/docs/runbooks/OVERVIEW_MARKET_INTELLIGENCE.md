# Overview Market Intelligence Runbook

Status: Active
Last Verified: 2026-05-28

## Purpose

이 runbook은 `Workspace > Overview`의 Market Movers, Sector / Industry, Events 데이터를 수동 또는 scheduled refresh로 갱신하고 정상 여부를 확인하는 절차를 정리한다.

## When To Use

- 장 시작 후 또는 장중에 daily movers snapshot을 새로 보고 싶을 때
- FOMC calendar row를 갱신해야 할 때
- CPI / PPI / Employment Situation / GDP 같은 macro release calendar row를 갱신해야 할 때
- latest S&P 500 movers 또는 수동 ticker의 upcoming earnings event를 갱신해야 할 때
- Overview Events / Market Movers 화면이 비어 있거나 오래된 것으로 보일 때
- 브라우저를 켜지 않고 scheduled refresh runner를 cron / launchd / 외부 automation으로 호출하고 싶을 때

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
   - daily period의 `Status Check`는 SP500 / TOP1000 / TOP2000 모두에서 stored DB snapshot 상태를 주기적으로 다시 읽는다. provider quote 수집은 자동 실행하지 않는다.
   - daily period에서 refresh state가 `Update due`, `Stale`, `Failed`이면 `Update Daily Snapshot`을 눌러 새 snapshot을 저장한다.
   - refresh bar에서 Universe, Mode, Coverage %, Next Check, recommended action을 확인한다.
   - `Rank` 탭에서 symbol-level return ranking을 확인한다.
   - `Sector Pulse` 탭에서 선택한 mover set 안에서 평균 return이 강한 sector를 확인한다.
   - `Returnable Coverage`에서 missing / failed count를 확인한다.
   - `Coverage Diagnostics`에서 missing symbol, reason, recommended action을 확인한다.
   - daily intraday missing row는 `Diagnose Missing Quotes`로 원인 후보를 확인한다. 결과는 `finance_meta.market_data_issue`에 반복 issue로 누적된다.

3. `Workspace > Overview > Sector / Industry`
   - `Coverage`, `Group`, `Top N`, `Min Symbols`를 선택한다.
   - `Heatmap` 탭에서 Equal Weight, Cap Weighted, Top Symbol return을 함께 비교한다.
   - `Table` 탭에서 구성 종목 수, 대표 symbol, raw return column을 확인한다.

4. `Workspace > Ingestion > Overview Market Event Calendar > FOMC`
   - 기본은 current year와 next year를 수집한다.
   - 결과는 `finance_meta.market_event_calendar`에 `event_type=FOMC_MEETING`으로 저장된다.

5. `Workspace > Ingestion > Overview Market Event Calendar > Macro`
   - 기본은 current year와 next year를 수집한다.
   - BLS source는 CPI / PPI / Employment Situation release schedule을 읽어 각각 `MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`로 저장한다.
   - BEA source는 national GDP release schedule을 읽어 `MACRO_GDP`로 저장한다.
   - 결과는 모두 `source_type=official`, `validation_status=official`로 저장된다.
   - BLS가 HTTP 403 등으로 차단되면 BEA가 성공하더라도 job은 `partial_success`가 될 수 있다.
   - BLS 자동 요청이 막히면 BLS 공식 release schedule `.ics` 파일을 브라우저로 내려받아 `BLS Calendar .ics File`에 업로드하고 `Import BLS .ics Calendar`를 실행한다.
   - `.ics` import도 같은 `market_event_calendar` table에 저장되며, Data Health의 Macro Calendar coverage에 포함된다.

6. `Workspace > Ingestion > Overview Market Event Calendar > Earnings`
   - 기본은 `Latest S&P 500 Movers` source를 사용한다.
   - broader coverage는 `S&P 500 Universe Batch`, `Top1000 Batch`, `Top2000 Batch`를 사용한다.
   - broader mode는 `Max Symbols`, `Batch Offset`, `Ticker Cooldown Sec`을 작게 잡아 저빈도로 실행한다.
   - `Nasdaq cross-check`를 켜면 yfinance estimate를 Nasdaq의 무료 earnings calendar endpoint와 날짜 단위로 비교한다.
   - latest movers mode는 stored S&P 500 intraday snapshot이 먼저 있어야 한다.
   - 특정 ticker 확인이 필요하면 `Manual Symbols`를 사용한다.
   - 결과는 `finance_meta.market_event_calendar`에 `event_type=EARNINGS`, `source=yfinance_calendar`, `source_type=provider_estimate`로 저장된다.
   - yfinance-only estimate는 `validation_status=estimate_only`, Nasdaq 확인 row는 `validation_status=cross_checked`, Nasdaq에서 확인하지 못한 row는 `validation_status=not_confirmed`가 된다.
   - 같은 symbol/source의 이전 active estimate는 새 수집 결과가 있으면 `event_status=superseded`로 정리된다.
   - 수집 결과에는 `symbol_diagnostics`가 포함되며 `no_provider_earnings_date`, `outside_window`, `provider_error` 같은 missing / failure reason을 확인할 수 있다.
   - Ingestion 실행 결과와 Overview refresh 결과의 `Earnings Diagnostics` expander에서 issue count, reason count, symbol-level detail을 확인한다.

7. `Workspace > Overview > Events`
   - `All`, `FOMC`, `Earnings`, `Macro` filter를 바꿔 저장 row를 확인한다.
   - `Window`, `Source Type`, `Validation`, `Importance` filter로 캘린더 범위와 source quality를 좁힌다.
   - `Focus` 탭에서 upcoming, needs review, high impact row를 먼저 확인한다.
   - `Calendar` 탭에서 event type별 stacked event count와 날짜별 grouped cards를 확인한다.
   - `Table` 탭에서 DB row-level detail을 확인한다.
   - `Source Type`에서 FOMC official row와 earnings provider estimate row를 구분한다.
   - `Importance`, `Focus`, `Validation`, `Freshness`, `Quality Action`, `Age Days`, `Event Status`에서 high impact 일정, cross-check 여부, 오래된 earnings estimate, 다음 조치가 필요한 row를 확인한다.
   - Overview의 refresh buttons도 ingestion job wrapper를 호출한다. UI render 중 직접 외부 source를 scraping하지 않는다.

8. `Workspace > Overview > Data Health`
   - Market Intelligence 운영 대상 7개를 한 화면에서 확인한다.
   - 대상은 S&P 500 universe, S&P 500 / Top1000 / Top2000 daily snapshot, FOMC calendar, Macro calendar, Earnings calendar다.
   - 상태는 `OK`, `Due`, `Stale`, `Missing`, `Failed`, `Partial`로 표시된다.
   - `Latest Success`, `Latest Issue`, `Rows`, `Processed`, `Failed`, `Duration Sec`은 Overview refresh button이 남긴 `.aiworkspace/note/finance/run_history/WEB_APP_RUN_HISTORY.jsonl`의 local run history를 읽는다.
   - `Last Auto Run`, `Auto Source`, `Next Auto Due`, `Last Manual Run`, `Failure Streak`은 scheduled automation, browser-session auto refresh, 수동 refresh가 섞여 있을 때 실행 경로를 구분하기 위한 운영 지표다.
   - local run history가 비어 있어도 DB freshness만으로 상태와 next action은 표시돼야 한다.
   - 이 탭은 DB와 local JSONL만 읽고 외부 provider를 fetch하지 않는다.

9. `Workspace > Overview > Browser Auto Refresh`
   - Overview 상단의 `Auto refresh while Overview is open` 토글은 브라우저 세션이 살아 있을 때만 `browser_safe` profile을 5분마다 호출한다.
   - 1차 browser-safe mode는 S&P 500 daily snapshot만 수집 대상으로 둔다.
   - 브라우저를 닫거나 Overview 페이지 연결이 끊기면 이 자동 check도 멈춘다.
   - 실제 실행 여부는 `overview_automation`의 cadence, US market-hours guard, lock file이 판단한다.
   - 자동 check 중에는 상단 패널 안에서 한국어 checking / collecting 상태와 progress indicator만 표시하며, 전체 화면을 blocking하지 않는다.

## CLI Smoke Checks

Overview scheduled refresh dry-run:

```bash
uv run python -m app.jobs.overview_automation --profile standard --dry-run
```

브라우저 없이 due job만 실제 실행:

```bash
uv run python -m app.jobs.overview_automation --profile standard
```

Overview를 열어둔 동안만 호출할 1차 browser-safe profile:

```bash
uv run python -m app.jobs.overview_automation --profile browser_safe
```

무료 provider 압력을 낮춘 안전 profile:

```bash
uv run python -m app.jobs.overview_automation --profile safe
```

캘린더만 갱신:

```bash
uv run python -m app.jobs.overview_automation --profile events
```

운영 scheduler에 연결할 때는 5분마다 위 명령을 호출하도록 두고, 실제 실행 여부는 CLI가 run history cadence와 US market-hours guard로 판단한다. 중복 실행은 `.aiworkspace/note/finance/run_artifacts/locks/overview_automation.lock`으로 막는다. `browser_safe` profile은 OS scheduler가 아니라 Overview 브라우저 세션이 열려 있을 때 호출하는 용도이며, S&P 500 daily snapshot만 선택한다.

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

BEA GDP macro calendar smoke:

```bash
uv run python - <<'PY'
from app.jobs.ingestion_jobs import run_collect_macro_calendar
print(run_collect_macro_calendar(years=(2026,), include_bls=False, include_bea=True))
PY
```

BLS `.ics` file import smoke:

```bash
uv run python - <<'PY'
from pathlib import Path
from app.jobs.ingestion_jobs import run_import_bls_macro_calendar_ics

ics_text = Path("/path/to/bls.ics").read_text(encoding="utf-8-sig")
print(run_import_bls_macro_calendar_ics(ics_text=ics_text, years=(2026,), source_name="bls.ics"))
PY
```

## Expected Results

- Market Movers daily snapshot shows `price_mode=Intraday Snapshot` and a recent `snapshot_time_utc`.
- Market Movers daily refresh state shows `Fresh`, `Update due`, `Stale`, `Partial`, or `Failed`.
- Market Movers daily refresh bar shows coverage ratio / percent, next DB status check time, and the recommended next action for SP500 / TOP1000 / TOP2000.
- Market Movers `Status Check` reloads the DB read model and refresh bar on the selected interval; it does not collect provider quotes automatically.
- Market Movers refresh results expose `Snapshot Diagnostics` with snapshot time, rows written, failed count, method, and provider diagnostics when available.
- Market Movers displays both `Rank` and `Sector Pulse` chart tabs.
- Sector / Industry displays both `Heatmap` and `Table` tabs.
- Missing diagnostics are visible with recommended action when provider rows are absent or incomplete.
- Quote gap diagnostics persist repeated issue history to `finance_meta.market_data_issue` and display occurrence count / latest evidence in Coverage Diagnostics.
- FOMC rows have `source=federal_reserve_fomc_calendar`, `confidence=1.0`, and `Source Type=Official`.
- Macro rows have `Type=MACRO_CPI`, `MACRO_PPI`, `MACRO_EMPLOYMENT`, or `MACRO_GDP`, `Source Type=Official`, and `Validation=Official`.
- BLS `.ics` import rows keep `source=bureau_labor_statistics_release_schedule` and `raw_payload_json.import_method=official_ics_file`.
- Earnings rows have `source=yfinance_calendar`, `Source Type=Provider Estimate`, and a validation label.
- Nasdaq cross-checked earnings rows have `Validation=Cross-checked` and higher confidence.
- Earnings rows collected more than 14 days ago show `Freshness=Stale estimate` and a warning.
- Earnings job results show `Earnings Diagnostics` when requested symbols are missing, outside the selected lookahead window, or fail at the provider layer.
- Earnings event rows include `Quality Action`; `Estimate only` rows recommend cross-check or closer refresh, stale rows recommend refresh, and cross-checked rows show no action.
- Overview Events displays `Focus`, `Calendar`, and `Table` tabs with Window / Source Type / Validation / Importance filters.
- Overview Events read model includes `Days Until`, `Importance`, and `Focus`; FOMC / macro rows are `High`, earnings rows are `Medium`, and rows with source / validation action show `Needs Review`.
- Overview Events calendar chart is stacked by event type, not a single aggregate line.
- Overview Events has a `Macro` filter and `Refresh Macro Calendar` button.
- Overview Events `Latest Collection` updates after a successful collector run.
- Overview Data Health displays 7 collection targets with ops status cards, warning banner, status badges, auto/manual run columns, failure streak, and next-action table.
- Overview refresh buttons append their result to local web app run history; the JSONL file itself remains a generated local artifact and is not committed.
- Overview scheduled refresh CLI can run without Streamlit and appends scheduled job results to the same local web app run history.

## Failure Handling

| Symptom | Likely Cause | Action |
|---|---|---|
| Earnings latest movers mode writes no rows | No latest S&P 500 intraday snapshot | Run S&P 500 market snapshot first or switch to manual symbols |
| Some earnings symbols are missing | yfinance calendar has no upcoming date, date is outside the selected window, or provider request failed | Open `Earnings Diagnostics`; retry with wider lookahead for `outside_window`, retry later for `provider_error`, or inspect ticker manually for `no_provider_earnings_date` |
| Earnings row is not confirmed | Nasdaq cross-check did not find the same symbol on that event date | Treat as provider estimate only; refresh later or inspect company IR manually |
| Old earnings date remains in DB | Estimate date changed | Overview hides superseded rows by default; inspect DB if an audit trail is needed |
| Market Movers missing count is high | Provider quote rows missing or DB previous close missing | Open `Coverage Diagnostics`, then refresh OHLCV / snapshot source if needed |
| Quote gap occurrence count keeps increasing | The same symbol repeatedly misses the quote endpoint or supporting evidence | Treat it as an operating issue; inspect `market_data_issue`, refresh profile / OHLCV, or keep the symbol under manual review |
| Events tab is empty | Matching collector has not been run or filter is too narrow | Run FOMC / Earnings refresh and select `All` |
| Macro Calendar shows `Due` with covered `1/4` | Only BEA GDP rows are stored; BLS CPI / PPI / Jobs rows are missing or blocked | Import the official BLS `.ics` file, retry BLS later, or treat current Macro view as GDP-only until BLS rows are available |
| Macro collection is partial | BLS schedule page rejected automated access, but BEA or another enabled source succeeded | Inspect failed source message, then use the BLS `.ics` import fallback if CPI / PPI / Jobs rows are needed |
| Data Health shows stale daily snapshots | Stored 5m snapshot is older than the intraday freshness threshold | Run `Update Daily Snapshot` for the affected coverage |
| Data Health shows blank latest success / issue | No Overview refresh button has written local run history yet | Use the relevant Overview refresh button or inspect Ingestion output directly |
| Scheduled refresh exits as locked | A previous automation run is still active, or a stale lock file remains | Wait for the run to finish; if the process is gone and the lock is older than the stale threshold, rerun after the CLI clears it |
| Overview app looks stale after code change | Old Streamlit process still running | Restart the Streamlit server and confirm Runtime / Build metadata in Ingestion |

## Verification Commands

```bash
uv run python -m py_compile app/web/overview_dashboard.py app/web/streamlit_app.py app/jobs/ingestion_jobs.py app/jobs/overview_automation.py finance/data/db/schema.py finance/data/market_intelligence.py
uv run python -m unittest tests.test_service_contracts
uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
git diff --check
```

Expected result:

- service contract tests pass
- UI-engine boundary reports `Result: PASS`
- `git diff --check` has no output
