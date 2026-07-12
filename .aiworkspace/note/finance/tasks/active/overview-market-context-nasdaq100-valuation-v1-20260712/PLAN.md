# Overview Market Context Nasdaq-100 Valuation V1 Plan

Status: Approved — Detailed Execution Plan
Last Updated: 2026-07-13

## 이걸 하는 이유?

현재 Market Context의 가치평가 화면은 S&P 500만 지원한다. 사용자는 계정, API token, 유료 데이터 계약 없이 같은 판단 흐름을 Nasdaq-100에도 적용하고 싶다. 무료 공개자료에는 완성된 Nasdaq 공식 index-level EPS/PER history가 없지만, SEC의 QQQ holdings와 기업 actual을 결합하면 출처와 한계를 숨기지 않는 QQQ proxy 가치평가를 만들 수 있다.

## Goal

- `Nasdaq-100 (QQQ proxy)`를 S&P 500 가치평가 화면의 두 번째 index option으로 제공한다.
- Graph 1은 공개 공시로 재구성한 월별 trailing P/E의 최근 60개월 분포를 표시한다.
- Graph 2는 현재 QQQ EPS proxy에 기존 FOMC SEP GDP+PCE 성장률을 적용해 예상 QQQ 가격 구간을 표시한다.
- Graph 2 history는 1년·3년·5년을 제공하되 과거 holdings anchor 품질을 명시한다.
- 모든 원격 수집은 ingestion에서 수행하고 UI는 DB-backed read model만 렌더링한다.

## Five-Stage Roadmap

### 1차 — Public Source Coverage Spike

- SEC N-PORT/N-30B-2 discovery와 parser fixture
- historical holding identity mapping
- diluted EPS/price/weight coverage와 known Nasdaq P/E calibration
- 완료 조건: 60개월 current multiple history와 1/3/5년 rolling warmup에 필요한 월 중 최소 95% weighted coverage

### 2차 — Ingestion / DB / Loader

- SEC holdings backfill과 idempotent UPSERT
- holding identifier columns와 Nasdaq monthly valuation table
- filing-aware TTM EPS와 monthly reconstructed P/E materialization
- 완료 조건: DB에 raw holdings와 derived monthly rows가 저장되고 재실행 결과가 안정적임

### 3차 — Service / FOMC Scenario

- current QQQ EPS proxy resolver
- 60m/36m multiple regime
- latest SEP GDP+PCE expected EPS와 QQQ price band
- 1/3/5년 reconstructed history
- 완료 조건: JSON-safe Nasdaq read model이 S&P와 동일한 핵심 contract를 제공함

### 4차 — React Index Selector

- `S&P 500 / Nasdaq-100 · QQQ proxy` selector
- SPX/QQQ copy와 단위 generic rendering
- public filing reconstruction badge, coverage, basis date, limitation
- 완료 조건: 두 index를 전환해도 각 그래프와 hover/기간 selector가 정상 동작함

### 5차 — Automation / QA / Docs / Commit

- existing Overview automation에 Nasdaq refresh 연결
- focused unit/service contract/DB smoke/Browser QA
- active task와 canonical finance docs 동기화
- generated screenshot은 커밋하지 않음
- 완료 조건: 실제 DB 데이터로 두 graph가 렌더링되고 검증 근거와 남은 위험이 기록됨

## Scope

### In Scope

- QQQ SEC holdings와 SEC company actual 기반 reconstructed P/E/EPS
- existing QQQ EOD, FOMC SEP, S&P React valuation surface 재사용
- 1/3/5년 history와 source-quality 표시

### Out Of Scope

- Nasdaq 공식 index-level P/E라고 표시
- NDX price licensing 또는 Nasdaq GIW/GIFFD 계약
- GuruFocus/FactSet/LSEG/Bloomberg 구매
- analyst consensus EPS
- UI에서 SEC/Invesco/Yahoo 직접 호출
- scraping, login gate 우회, current constituents의 무근거 과거 소급

## Stop Conditions

- weighted EPS/price coverage가 95% 미만이면 production-ready graph로 표시하지 않는다.
- 공개 Nasdaq trailing P/E 관측점 대비 median absolute percentage error가 5%를 넘거나 단일 관측 오차가 10%를 넘으면 `BLOCKED` read model과 원인을 제공하고 공식값처럼 렌더링하지 않는다.
- ADR/복수 클래스 mapping이 설명되지 않은 상태에서 해당 weight를 actual coverage로 세지 않는다.

## Approved Architecture And File Map

승인된 구현은 기존 S&P 500 흐름을 덮어쓰지 않고 Nasdaq read model을 독립적으로 추가한 뒤 Market Context 조합 service에서 두 instrument를 묶는다.

| 책임 | 파일 | 변경 계약 |
|---|---|---|
| SEC holdings discovery/parser, identity, PIT EPS, monthly materialization | `finance/data/nasdaq100_valuation.py` | 원격 source와 계산을 소유하고 UI를 import하지 않음 |
| additive schema | `finance/data/db/schema.py` | `etf_holdings_snapshot` optional identity/timing column과 `nasdaq100_monthly_valuation` 추가 |
| DB read path | `finance/loaders/nasdaq100_valuation.py` | 120개월 valuation, latest complete proxy EPS, coverage/calibration evidence를 읽음 |
| Nasdaq service | `app/services/overview/nasdaq100_valuation.py` | S&P pure 계산을 재사용해 QQQ 단위 JSON-safe read model 생성 |
| instrument composition | `app/services/overview/market_context_valuation.py` | S&P 실패와 Nasdaq 실패를 서로 전파하지 않고 nested instrument payload 생성 |
| ingestion/automation | `app/jobs/ingestion_jobs.py`, `app/jobs/overview_automation.py` | holdings backfill/materialization job과 daily-safe cadence 연결 |
| Python UI bridge | `app/web/overview/market_context_helpers.py` | combined payload만 React/fallback에 전달 |
| React surface | `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`, `style.css` | selector, 동적 단위/copy, coverage/basis/limitation 표시 |
| tests | `tests/test_nasdaq100_valuation.py`, `tests/test_sp500_valuation.py` | 새 계약과 S&P 회귀를 각각 소유 |
| durable docs | `docs/PROJECT_MAP.md`, `docs/ROADMAP.md`, `docs/INDEX.md`, `docs/architecture/DATA_DB_PIPELINE_FLOW.md`, `docs/data/*`, task/root logs | source/table/PIT/UX/QA 결과 동기화 |

## Detailed TDD Execution Plan

### 1차 — Public Source Coverage Spike

**목적:** DB write 전에 2015-09 이후 holdings anchor, filing-aware diluted EPS, month-end price를 결합할 수 있는지 수치로 차단/통과시킨다.

**Interfaces**

```python
discover_qqq_sec_filings(payload: dict[str, Any]) -> list[dict[str, Any]]
parse_qqq_nport_xml(xml_text: str, *, filing: dict[str, Any]) -> list[dict[str, Any]]
parse_qqq_n30b2_html(html_text: str, *, filing: dict[str, Any]) -> list[dict[str, Any]]
resolve_holding_identities(holdings, identity_rows, *, overrides=None) -> list[dict[str, Any]]
derive_filing_aware_ttm_eps(statement_rows, *, as_of_date: str) -> dict[str, dict[str, Any]]
drift_holding_weights(holdings, prices, *, snapshot_date: str, observation_month: str) -> list[dict[str, Any]]
reconstruct_monthly_valuation(holdings, eps_by_symbol, prices, *, minimum_coverage_pct=95.0) -> dict[str, Any]
evaluate_pe_calibration(reconstructed_rows, fixtures, *, median_limit_pct=5.0, max_limit_pct=10.0) -> dict[str, Any]
```

- [ ] `tests/test_nasdaq100_valuation.py`에 작은 N-PORT XML, 2018 N-30B-2 HTML, identity, Q1/Q2/Q3/FY EPS, negative EPS, weight drift, 95% gate, calibration fixture를 작성한다.
- [ ] `.venv/bin/python -m unittest tests.test_nasdaq100_valuation -v`를 실행해 module 부재와 함수 부재로 RED가 나는지 확인한다.
- [ ] `finance/data/nasdaq100_valuation.py`에 위 pure interface만 최소 구현하고 SEC namespace, annual schedule numeric row, USD/share duration row만 허용한다.
- [ ] 같은 테스트를 다시 실행해 pure coverage contract를 GREEN으로 만든다.
- [ ] SEC QQQ submissions/N-PORT/N-30B-2와 local DB를 읽는 read-only `run_nasdaq100_coverage_spike(start_month="2016-09-01")`를 추가한다. 이 함수는 DB write를 하지 않고 월별 `coverage_weight_pct`, `unmapped_weight_pct`, `data_quality`, calibration 결과를 반환한다.
- [ ] 실제 spike를 실행해 120개월 input 중 complete row 수, 최근 60개월 complete 여부, 1/3/5년 warmup 가능 여부, unresolved holdings를 `RUNS.md`/`NOTES.md`에 기록한다.
- [ ] 최근 60개월 중 한 달이라도 95% gate를 통과하지 못하거나 public fixture 오차가 threshold를 넘으면 2차로 진행하지 않고 `RISKS.md`에 blocker를 남긴다.

**1차 완료 조건:** 최근 60개 observation month가 모두 complete이며, 현재 공개 P/E fixture의 median/max 오차가 각각 5%/10% 이하다.

### 2차 — Ingestion / DB / Loader

**목적:** spike에서 검증한 source를 repeat-safe DB pipeline으로 승격한다.

**Schema contract**

```text
etf_holdings_snapshot optional columns:
  cusip, isin, lei, issuer_cik, filing_date

nasdaq100_monthly_valuation business key:
  (observation_month, proxy_symbol, source)
```

- [ ] schema SQL 문자열, schema sync, holdings/monthly UPSERT, loader query 기대값을 먼저 테스트에 추가하고 RED를 확인한다.
- [ ] `finance/data/db/schema.py`에 additive columns와 `nasdaq100_monthly_valuation`을 추가한다. 기존 provider row는 null 호환을 유지한다.
- [ ] `finance/data/nasdaq100_valuation.py`에 `ensure_nasdaq100_valuation_schemas`, holdings UPSERT, derived monthly UPSERT를 구현한다. stable source/accession/holding id를 유지하고 repeat run은 row 수를 늘리지 않는다.
- [ ] `collect_and_store_qqq_sec_holdings()`는 SEC filings만 수집하고, `materialize_nasdaq100_monthly_valuation()`은 저장된 holdings/statements/prices만 읽는다. 두 단계의 실패를 섞지 않는다.
- [ ] `finance/loaders/nasdaq100_valuation.py`에 `load_nasdaq100_monthly_valuation(months=120)`과 `load_latest_nasdaq100_ttm_proxy()`를 구현한다.
- [ ] mocked DB로 schema/UPSERT/loader focused tests를 GREEN으로 만든다.
- [ ] 실제 DB schema sync, historical holdings backfill, monthly materialization을 순서대로 실행하고 동일 명령을 한 번 더 실행해 unique key/idempotency를 확인한다.

**2차 완료 조건:** raw holdings와 derived monthly rows가 DB에 저장되고, 2회 실행 후 동일 business key row count와 동일 valuation 결과를 유지한다.

### 3차 — Service / FOMC Scenario

**목적:** DB row를 React가 계산 없이 읽을 수 있는 instrument-specific JSON payload로 변환한다.

**Read-model contract**

```python
{
  "schema_version": "nasdaq100_qqq_valuation_v1",
  "instrument": {
    "key": "nasdaq100_qqq_proxy",
    "index_name": "Nasdaq-100",
    "price_symbol": "QQQ",
    "price_label": "QQQ",
    "source_quality": "public_filing_reconstructed_proxy",
    "official_index_aggregate": False,
  },
  "multiple_regime": {...},
  "earnings_scenario": {...},
  "index_scenario": {"qqq_scenarios": {...}, "history_options": {...}},
  "coverage": {...},
  "calibration": {...},
}
```

- [ ] 60m/36m multiple, QQQ scenario, 1/3/5년 history, coverage/calibration block, JSON-safe/instrument metadata 테스트를 RED로 작성한다.
- [ ] `app/services/overview/nasdaq100_valuation.py`에서 S&P의 index-neutral `calculate_multiple_regime`과 `calculate_fomc_eps_scenarios`를 재사용하고, QQQ price field adapter와 history output만 새로 구현한다.
- [ ] `app/services/overview/market_context_valuation.py`에 `build_market_context_valuation_read_model()`을 추가해 `default_instrument="sp500"`, `instruments={"sp500": ..., "nasdaq100_qqq_proxy": ...}`를 반환한다.
- [ ] Nasdaq가 BLOCKED여도 S&P model은 그대로 READY/렌더 가능하다는 독립성 테스트를 GREEN으로 만든다.
- [ ] actual DB read model smoke에서 60/36개월, current QQQ EPS proxy, 1/3/5년 12/36/60 points, coverage/calibration evidence를 확인한다.

**3차 완료 조건:** service payload가 instrument/source/basis/quality를 모두 포함하고 React가 별도 계산 없이 두 그래프를 그릴 수 있다.

### 4차 — React Index Selector

**목적:** 사용자가 같은 Market Context 판단 흐름에서 S&P와 QQQ proxy를 명확히 전환한다.

- [ ] React source contract test에 selector label, dynamic `price_label`, proxy limitation, coverage/basis copy를 먼저 추가해 RED를 확인한다.
- [ ] `market_context_helpers.py`의 cached loader를 combined service로 바꾸고 fallback도 instrument metadata로 단위/문구를 렌더링한다.
- [ ] `MarketContextValuation.tsx`에 `S&P 500 / Nasdaq-100 · QQQ proxy` selector state를 추가하고 선택한 nested model만 차트에 넘긴다.
- [ ] `actual_spx/lower_spx/...` hard-coded history field는 service가 공통 `actual_price/lower_price/...` alias도 제공하게 하여 React를 generic하게 바꾼다. S&P legacy aliases는 Python contract에 유지한다.
- [ ] Nasdaq 선택 시 source/quality/coverage/holdings basis/`공식 Nasdaq index-level P/E/EPS가 아님`을 첫 화면 보조 근거로 표시하고 job/status/row-count 패널은 만들지 않는다.
- [ ] `npm run build`와 Python source contract tests를 GREEN으로 만든다. build output의 hash 변경 파일만 stage 후보로 둔다.

**4차 완료 조건:** 두 instrument 전환, 그래프 hover, 1/3/5년 selector, narrow layout이 동작하고 공식 aggregate로 오인할 문구가 없다.

### 5차 — Automation / QA / Docs / Commit

**목적:** 실데이터 refresh와 사용자 화면을 검증하고 다음 작업자가 재현할 수 있게 닫는다.

- [ ] `app/jobs/ingestion_jobs.py`에 Nasdaq context job을 추가하고 source 단계별 partial failure evidence를 표준 `JobResult`로 반환한다.
- [ ] `app/jobs/overview_automation.py`에 daily-safe `nasdaq100_valuation` spec을 연결한다. holdings discovery는 새 filing만 UPSERT하고 materialization은 저장된 DB만 사용한다.
- [ ] `.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_sp500_valuation -v`, focused service contracts, `py_compile`, TypeScript, Vite build, `git diff --check`를 fresh 실행한다.
- [ ] 실제 DB에서 holdings snapshot date/quality, 120개월/최근 60개월 complete row, coverage min/median, calibration median/max, 1/3/5 history count를 조회한다.
- [ ] in-app Browser에서 desktop과 420px viewport로 S&P/Nasdaq selector, 두 그래프 hover, 1/3/5년, horizontal overflow/console error를 확인하고 screenshot 1장을 generated artifact로 남기되 stage하지 않는다.
- [ ] task `STATUS/NOTES/RUNS/RISKS`, canonical data/architecture/project map, `ROADMAP/INDEX`, root handoff logs를 실제 결과만으로 동기화한다.
- [ ] `git status --short`, scoped diff, generated/registry/saved/run-history 제외, staged diff review를 수행한다.
- [ ] coherent 변경만 stage하고 Korean commit `나스닥100 QQQ 공개 공시 가치평가 구현`을 만든다. unrelated untracked research 폴더는 끝까지 unstaged로 둔다.

**5차 완료 조건:** focused tests/DB smoke/React build/Browser QA/docs sync가 fresh evidence로 통과하고 coherent commit이 생성된다.

## Verification Commands

```bash
.venv/bin/python -m unittest tests.test_nasdaq100_valuation tests.test_sp500_valuation -v
.venv/bin/python -m py_compile \
  finance/data/nasdaq100_valuation.py \
  finance/loaders/nasdaq100_valuation.py \
  app/services/overview/nasdaq100_valuation.py \
  app/services/overview/market_context_valuation.py \
  app/jobs/ingestion_jobs.py app/jobs/overview_automation.py
npm run build --prefix app/web/streamlit_components/market_context_valuation
git diff --check
git status --short
```
