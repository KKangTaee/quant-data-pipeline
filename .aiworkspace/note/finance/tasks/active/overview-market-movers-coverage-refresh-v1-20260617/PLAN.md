# Overview Market Movers Coverage Refresh V1

## Goal

`Workspace > Overview > Market Movers`의 coverage universe를 최신화하고, Nasdaq-listed current snapshot coverage를 추가하며, 반복 갱신과 Coverage Diagnostics의 원인 설명력을 보강한다.

## 이걸 하는 이유?

Market Movers는 현재 S&P 500 / Top1000 / Top2000 중심이라 Nasdaq-listed coverage를 직접 볼 수 없다. 또한 Top universe는 asset profile freshness와 가격 이력 coverage 차이 때문에 missing row가 반복되지만, 화면은 주로 `가격 이력 갱신`만 안내해 왜 계속 빠지는지 이해하기 어렵다. 사용자가 coverage 선택, 갱신, 원인 확인을 한 화면에서 덜 헷갈리게 끝낼 수 있게 한다.

## Roadmap

1. Nasdaq coverage 추가
   - `nyse_symbol_lifecycle`의 최신 `nasdaq_symdir_nasdaqlisted` current snapshot row를 DB-backed universe로 읽는다.
   - Nasdaq Composite / Nasdaq-100으로 표현하지 않고 `Nasdaq-listed current snapshot`으로 라벨링한다.
   - source / event date / collected_at / current snapshot caveat를 coverage metadata에 남긴다.

2. 반복 갱신 연결
   - Overview action facade에 Nasdaq Symbol Directory refresh와 Nasdaq intraday refresh를 연결한다.
   - `overview_automation` dry-run plan에 daily Symbol Directory refresh와 `nasdaq_intraday` job을 노출한다.
   - OS scheduler 등록이나 대량 provider 수집 실행은 하지 않는다.

3. Coverage Diagnostics 보강
   - missing row에 latest price, profile freshness, lifecycle/listing evidence, market data issue evidence를 compact하게 덧붙인다.
   - 법적/상폐/거래정지 확정 표현은 피하고 source-backed evidence와 `current listing observation only` caveat를 유지한다.

## Scope

- `finance/data/market_intelligence.py`
- `app/services/overview_market_intelligence.py`
- `app/jobs/overview_actions.py`
- `app/jobs/overview_automation.py`
- `app/jobs/ingestion_jobs.py` if wrapper contract needs minor exposure only
- `app/web/overview_dashboard.py`
- `tests/test_service_contracts.py`
- Overview Market Intelligence runbook and root handoff logs

## Non-Goals

- Nasdaq Composite, Nasdaq-100, trade signal, recommendation, buy/sell wording.
- New paid provider, API key, DB table, registry / saved JSONL write.
- Backtest Analysis, Practical Validation, Final Review, Operations monitoring logic changes.
- OS launchd / cron registration.
- Browser QA에서 대량 provider collection 강제 실행.

## Stop Condition

- Focused failing tests are added and verified red before implementation.
- Required py_compile, pytest, automation dry-run checks pass.
- Browser QA confirms the coverage dropdown, existing coverages, Nasdaq empty/data state, and diagnostics evidence.
- Durable runbook/doc alignment is updated where behavior changed.
- Coherent commit is created without generated artifacts.
