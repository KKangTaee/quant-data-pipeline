# Overview Market Context S&P 500 Valuation V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This workspace does not authorize sub-agent dispatch for this task.

**Goal:** 기존 Market Context visible UI를 제거하고, DB-backed 공개 데이터와 FOMC SEP vintage를 이용한 두 개의 React S&P 500 가치평가 그래프로 교체한다.

**Architecture:** 외부 자료 수집과 persistence는 `finance/data/sp500_valuation.py`, DB read는 `finance/loaders/sp500_valuation.py`, 모든 재무 계산과 판정은 `app/services/overview/sp500_valuation.py`가 소유한다. Streamlit entrypoint는 직렬화된 read model만 React component에 전달하며, React는 계산식이나 원격 fetch를 수행하지 않는다.

**Tech Stack:** Python 3.12, pandas, BeautifulSoup, xlrd/openpyxl, MySQL, Streamlit, React 18, TypeScript 5.7, Vite 6, SVG, unittest/pytest.

## Global Constraints

- 기존 시장 세션/브리프/Top Mover/Breadth/섹터 압력/이벤트/sentiment/자료 보강 visible UI를 Market Context에서 제거한다.
- 신규 Market Context visible UI는 React Streamlit component를 사용한다.
- UI에서 provider, Shiller, S&P, Federal Reserve를 직접 fetch하지 않는다.
- EPS 기준은 `As-Reported`로 통일한다.
- `TTM actual EPS`는 완료된 최근 4개 분기의 actual index EPS 합계다. mixed/estimate row를 actual로 취급하지 않는다.
- 5년/60개월이 공식 멀티플 판정 window이며 3년/36개월은 기간 민감도 evidence다.
- 표준편차 band는 descriptive relative zone이며 confidence interval이 아니다.
- FOMC SEP GDP/PCE endpoint 조합은 sensitivity scenario이며 participant joint distribution이 아니다.
- 가치평가 계산은 SPX로 하고 SPY는 동일 기준일 proportional conversion으로만 표시한다.
- trailing multiple과 macro-implied NTM EPS 결합 결과는 `예상 실적 기반 지수 시나리오`로 부르고 공식 적정가나 투자 signal로 표현하지 않는다.
- 새 SEP release는 release-date vintage로 보존하고 이전 release를 덮어쓰지 않는다.
- registry/saved JSONL, run history, 기존 Market Movers research/QA artifact를 수정하거나 stage하지 않는다.

---

## File Responsibility Map

| File | Responsibility |
|---|---|
| `pyproject.toml`, `uv.lock` | `.xls`/`.xlsx` source parser dependencies |
| `finance/data/db/schema.py` | valuation/earnings/SEP table DDL |
| `finance/data/sp500_valuation.py` | source fetch/parse/normalize/upsert and vintage identity |
| `finance/loaders/sp500_valuation.py` | DB-backed monthly valuation, TTM actual EPS, SEP, SPX/SPY reads |
| `finance/loaders/__init__.py` | public loader exports |
| `app/services/overview/sp500_valuation.py` | 60m/36m multiple distribution, FOMC EPS, SPX/SPY scenario read model |
| `app/jobs/ingestion_jobs.py` | valuation source collection JobResult wrapper |
| `app/jobs/overview_automation.py` | monthly/quarterly source refresh scheduling |
| `app/web/overview/market_context.py` | new Market Context entrypoint only |
| `app/web/overview/market_context_helpers.py` | cached read-model load and Streamlit fallback |
| `app/web/overview/market_context_react_component.py` | compiled React component declaration |
| `app/web/streamlit_components/market_context_valuation/*` | React/TypeScript/SVG/CSS source and build output |
| `tests/test_sp500_valuation.py` | data normalization, calculation, read-model tests |
| `tests/test_service_contracts.py` | entrypoint/component/removal/automation contract tests |
| finance docs/task docs | canonical data/UI flow and implementation evidence |

---

### Task 1: 1차 — Source Contract And Persistence

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `finance/data/db/schema.py`
- Create: `finance/data/sp500_valuation.py`
- Create: `tests/test_sp500_valuation.py`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-market-context-sp500-valuation-v1-20260712/{STATUS,NOTES,RUNS,RISKS}.md`

**Interfaces:**
- Produces: `VALUATION_SCHEMAS`, `normalize_shiller_monthly_frame`, `normalize_index_earnings_frame`, `discover_latest_fomc_sep_url`, `parse_fomc_sep_html`, `collect_and_store_shiller_monthly_valuation`, `import_and_store_sp500_index_earnings`, `collect_and_store_fomc_sep`.
- Storage: `finance_meta.sp500_monthly_valuation`, `finance_meta.sp500_index_earnings`, `finance_meta.fomc_sep_projection`.

- [ ] **Step 1: Add failing schema contract tests**

```python
def test_valuation_schema_preserves_monthly_earnings_and_sep_vintages(self) -> None:
    from finance.data.db.schema import VALUATION_SCHEMAS

    monthly = VALUATION_SCHEMAS["sp500_monthly_valuation"]
    earnings = VALUATION_SCHEMAS["sp500_index_earnings"]
    sep = VALUATION_SCHEMAS["fomc_sep_projection"]
    self.assertIn("UNIQUE KEY uk_sp500_month_source", monthly)
    self.assertIn("value_status ENUM('actual','estimate','mixed')", earnings)
    self.assertIn("UNIQUE KEY uk_sep_release_year_variable_stat", sep)
```

- [ ] **Step 2: Run the schema test and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py::Sp500ValuationDataTests::test_valuation_schema_preserves_monthly_earnings_and_sep_vintages -q
```

Expected: FAIL because `VALUATION_SCHEMAS` does not exist.

- [ ] **Step 3: Add parser dependency declarations and table DDL**

Add `xlrd>=2.0.2` and `openpyxl>=3.1.5` to `pyproject.toml`, regenerate `uv.lock`, and define the exact table keys:

```python
VALUATION_SCHEMAS = {
    "sp500_monthly_valuation": """
        CREATE TABLE IF NOT EXISTS sp500_monthly_valuation (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          observation_month DATE NOT NULL,
          spx_level DOUBLE NULL,
          trailing_eps DOUBLE NULL,
          trailing_pe DOUBLE NULL,
          cape DOUBLE NULL,
          data_quality ENUM('actual','interpolated','estimate','missing','error') NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          source_version VARCHAR(128) NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uk_sp500_month_source (observation_month, source),
          KEY ix_sp500_month (observation_month)
        );
    """,
    "sp500_index_earnings": """
        CREATE TABLE IF NOT EXISTS sp500_index_earnings (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          period_end DATE NOT NULL,
          period_type ENUM('quarterly','annual','ttm') NOT NULL,
          earnings_basis ENUM('as_reported','operating') NOT NULL,
          value_status ENUM('actual','estimate','mixed') NOT NULL,
          eps DOUBLE NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          source_release_date DATE NOT NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uk_sp500_eps_period_basis_status_source
            (period_end, period_type, earnings_basis, value_status, source, source_release_date),
          KEY ix_sp500_eps_period (period_end, period_type)
        );
    """,
    "fomc_sep_projection": """
        CREATE TABLE IF NOT EXISTS fomc_sep_projection (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          release_date DATE NOT NULL,
          target_year SMALLINT NOT NULL,
          variable_name ENUM('real_gdp','pce_inflation') NOT NULL,
          statistic_name ENUM('median','central_tendency_lower','central_tendency_upper','range_lower','range_upper') NOT NULL,
          value_pct DOUBLE NOT NULL,
          source VARCHAR(64) NOT NULL DEFAULT 'federal_reserve_sep',
          source_ref VARCHAR(1024) NOT NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          UNIQUE KEY uk_sep_release_year_variable_stat
            (release_date, target_year, variable_name, statistic_name),
          KEY ix_sep_latest (release_date, target_year)
        );
    """,
}
```

Required typed columns are those in `DESIGN.md`: source/reference, actual/estimate/mixed, As-Reported/Operating, release/vintage date, value, quality, collected time, error.

- [ ] **Step 4: Verify schema GREEN**

Run the Step 2 command. Expected: PASS.

- [ ] **Step 5: Add failing source normalizer/parser tests**

```python
def test_shiller_normalizer_emits_positive_monthly_per(self) -> None:
    frame = pd.DataFrame({"Date": [2026.03], "P": [6654.4191], "E": [261.723], "CAPE": [37.03]})
    rows = normalize_shiller_monthly_frame(frame, collected_at="2026-07-12 00:00:00")
    self.assertEqual(rows[0]["observation_month"], "2026-03-01")
    self.assertAlmostEqual(rows[0]["trailing_pe"], 25.4254, places=4)

def test_index_earnings_normalizer_keeps_actual_as_reported_quarters(self) -> None:
    frame = pd.DataFrame({"period_end": ["2026-03-31"], "as_reported_eps": [70.0], "status": ["actual"]})
    rows = normalize_index_earnings_frame(frame, source_release_date="2026-05-15")
    self.assertEqual(rows[0]["earnings_basis"], "as_reported")
    self.assertEqual(rows[0]["value_status"], "actual")

def test_sep_parser_preserves_release_vintage_and_central_tendency(self) -> None:
    rows = parse_fomc_sep_html(SEP_HTML_FIXTURE, source_url="https://www.federalreserve.gov/example")
    keyed = {(row["variable_name"], row["statistic_name"]): row["value_pct"] for row in rows if row["target_year"] == 2026}
    self.assertEqual(keyed[("real_gdp", "median")], 2.2)
    self.assertEqual(keyed[("pce_inflation", "central_tendency_upper")], 3.7)
```

- [ ] **Step 6: Run parser tests and verify RED**

Run:

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py -q
```

Expected: FAIL because the source module/functions are missing.

- [ ] **Step 7: Implement minimal source normalization, fetch, parsing, and UPSERT**

Implement the exact public functions named in the Task 1 Interfaces block. `normalize_shiller_monthly_frame` converts decimal dates to the first day of each month, coerces `P/E/CAPE` numerics, calculates `P / E`, and emits `data_quality='interpolated'`. `normalize_index_earnings_frame` accepts only positive quarterly EPS rows with explicit `actual/estimate/mixed` status and emits both As-Reported and Operating rows only when their source columns exist. `discover_latest_fomc_sep_url` selects the maximum dated official accessible-material link matching `fomcprojtablYYYYMMDD.htm`; `parse_fomc_sep_html` emits separate median/lower/upper rows for GDP and PCE by target year.

The three persistence functions create/sync their table, run parameterized `executemany` UPSERT, and return a dictionary containing `rows_written`, `source`, `source_ref`, `release_date` where applicable, and `warnings`. Fetchers and DB connection arguments remain injectable so tests never require network or MySQL.

All collectors use `MySQLClient`, `VALUATION_SCHEMAS`, `sync_table_schema`, parameterized UPSERT, and injected fetchers in tests. Do not add Streamlit imports.

- [ ] **Step 8: Verify Task 1 GREEN and compile**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py -q
.venv/bin/python -m py_compile finance/data/sp500_valuation.py finance/data/db/schema.py
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 9: Update task evidence and commit 1차**

```bash
git add pyproject.toml uv.lock finance/data/db/schema.py finance/data/sp500_valuation.py tests/test_sp500_valuation.py .aiworkspace/note/finance/tasks/active/overview-market-context-sp500-valuation-v1-20260712
git commit -m "S&P 500 가치평가 원천과 저장 구조 추가"
```

---

### Task 2: 2차 — Five-Year Multiple Loader And Engine

**Files:**
- Create: `finance/loaders/sp500_valuation.py`
- Modify: `finance/loaders/__init__.py`
- Create: `app/services/overview/sp500_valuation.py`
- Modify: `tests/test_sp500_valuation.py`
- Modify: task docs

**Interfaces:**
- Consumes: Task 1 tables.
- Produces: `load_sp500_monthly_valuation`, `load_latest_sp500_ttm_actual_eps`, `load_latest_fomc_sep_projection`, `calculate_multiple_regime`.

- [ ] **Step 1: Add failing loader and 60m/36m regime tests**

```python
def test_multiple_regime_uses_60_months_and_36_month_sensitivity(self) -> None:
    frame = monthly_pe_frame(72, start="2020-01-01")
    result = calculate_multiple_regime(frame, current_spx=7200.0, current_ttm_eps=280.0)
    self.assertEqual(result["window_months"], 60)
    self.assertEqual(result["sensitivity"]["window_months"], 36)
    self.assertAlmostEqual(result["current_pe"], 25.7142857)
    self.assertIn(result["bucket"], {"LOW", "NEUTRAL", "HIGH", "EXTREME_HIGH"})

def test_ttm_loader_sums_latest_four_completed_actual_quarters(self) -> None:
    row = load_latest_sp500_ttm_actual_eps(query_fn=fake_eps_query)
    self.assertEqual(row["quarter_count"], 4)
    self.assertEqual(row["ttm_eps"], 270.0)
    self.assertEqual(row["value_status"], "actual")
```

- [ ] **Step 2: Verify RED**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py -q
```

Expected: FAIL because loader/service functions are missing.

- [ ] **Step 3: Implement DB loaders with injectable queries**

Implement `load_sp500_monthly_valuation(months=72, query_fn=None)`, `load_latest_sp500_ttm_actual_eps(query_fn=None)`, and `load_latest_fomc_sep_projection(query_fn=None)` with the return types declared in the Interfaces block. Each default query opens `finance_meta` through `MySQLClient`; an injected `query_fn(sql, params)` returns dictionaries for deterministic tests.

`load_latest_sp500_ttm_actual_eps` filters `period_type='quarterly'`, `earnings_basis='as_reported'`, `value_status='actual'`, orders by completed period descending, requires exactly four distinct quarters, and returns source/release evidence.

- [ ] **Step 4: Implement the multiple regime calculator**

Implement `calculate_multiple_regime(monthly_rows, current_spx, current_ttm_eps, official_window=60, sensitivity_window=36) -> dict[str, Any]` as a pure function. It sorts and deduplicates months, filters positive values, takes the last 60 and 36 rows, calculates sample standard deviation on log(PER), and maps Z-score thresholds to `LOW/NEUTRAL/HIGH/EXTREME_HIGH`.

The result contains `series`, `mean_multiple`, `minus_1sigma`, `plus_1sigma`, `plus_2sigma`, `current_pe`, `current_z`, `bucket`, `sensitivity`, `period_sensitive`, `basis_start`, `basis_end`, and limitation copy keys. Use `statistics.stdev`/pandas sample std with `ddof=1` on `log(PER)`.

- [ ] **Step 5: Verify GREEN and commit 2차**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py -q
.venv/bin/python -m py_compile finance/loaders/sp500_valuation.py app/services/overview/sp500_valuation.py
git diff --check
git add finance/loaders/sp500_valuation.py finance/loaders/__init__.py app/services/overview/sp500_valuation.py tests/test_sp500_valuation.py .aiworkspace/note/finance/tasks/active/overview-market-context-sp500-valuation-v1-20260712
git commit -m "최근 5년 S&P 500 멀티플 구간 계산 추가"
```

---

### Task 3: 3차 — FOMC EPS And SPX/SPY Scenario Read Model

**Files:**
- Modify: `app/services/overview/sp500_valuation.py`
- Modify: `finance/loaders/sp500_valuation.py`
- Modify: `tests/test_sp500_valuation.py`
- Modify: task docs

**Interfaces:**
- Consumes: Task 2 multiple regime, current actual TTM EPS, latest SEP, SPX/SPY same-date EOD.
- Produces: `calculate_fomc_eps_scenarios`, `calculate_index_scenario`, `build_sp500_valuation_read_model`.

- [ ] **Step 1: Add failing FOMC compounding and SPY alignment tests**

```python
def test_fomc_eps_scenario_compounds_real_gdp_and_pce(self) -> None:
    result = calculate_fomc_eps_scenarios(270.0, sep_projection_frame())
    self.assertAlmostEqual(result["baseline"]["growth_pct"], 5.8792, places=4)
    self.assertAlmostEqual(result["baseline"]["projected_eps"], 285.87384, places=5)

def test_index_scenario_blocks_spy_conversion_when_dates_differ(self) -> None:
    result = calculate_index_scenario(
        multiple_regime=multiple_regime_fixture(),
        eps_scenarios=eps_scenario_fixture(),
        current_spx={"date": "2026-07-10", "price": 7200.0},
        current_spy={"date": "2026-07-09", "price": 720.0},
    )
    self.assertIsNone(result["spy_equivalent"])
    self.assertEqual(result["spy_status"], "DATE_MISMATCH")
```

- [ ] **Step 2: Verify RED**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py -q
```

Expected: FAIL because scenario/read-model functions are missing.

- [ ] **Step 3: Implement scenario calculators and loader price bridge**

Implement `calculate_fomc_eps_scenarios(current_ttm_eps, sep_rows)`, `calculate_index_scenario(multiple_regime, eps_scenarios, current_spx, current_spy)`, and `build_sp500_valuation_read_model(monthly_rows=None, ttm_evidence=None, sep_rows=None, current_prices=None)` with the JSON-safe return contract in the Task 3 Interfaces block.

Use `finance.loaders.price.load_latest_prices` for `^GSPC` and `SPY`. The read model is JSON-safe and has top-level keys `schema_version`, `status`, `basis`, `multiple_regime`, `earnings_scenario`, `index_scenario`, `sources`, `limitations`.

- [ ] **Step 4: Add failing insufficiency/stale/mixed tests and implement guards**

```python
def test_read_model_blocks_actual_scenario_for_mixed_eps(self) -> None:
    model = build_sp500_valuation_read_model(
        monthly_rows=monthly_pe_frame(60),
        ttm_evidence={"value_status": "mixed", "ttm_eps": 280.0},
        sep_rows=sep_projection_frame(),
        current_prices=pd.DataFrame(
            [
                {"symbol": "^GSPC", "latest_date": "2026-07-10", "price": 7200.0},
                {"symbol": "SPY", "latest_date": "2026-07-10", "price": 720.0},
            ]
        ),
    )
    self.assertEqual(model["earnings_scenario"]["status"], "BLOCKED")
    self.assertIn("실제 EPS", model["earnings_scenario"]["reason"])
```

Implement explicit `INSUFFICIENT_HISTORY`, `NON_POSITIVE_EPS`, `MIXED_EPS`, `STALE_SEP`, `DATE_MISMATCH`, and `READY` states. Never silently substitute an estimate for actual EPS.

- [ ] **Step 5: Verify GREEN and commit 3차**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py -q
.venv/bin/python -m py_compile app/services/overview/sp500_valuation.py finance/loaders/sp500_valuation.py
git diff --check
git add app/services/overview/sp500_valuation.py finance/loaders/sp500_valuation.py tests/test_sp500_valuation.py .aiworkspace/note/finance/tasks/active/overview-market-context-sp500-valuation-v1-20260712
git commit -m "FOMC 예상 EPS와 S&P 500 지수 시나리오 추가"
```

---

### Task 4: 4차 — React Market Context Replacement

**Files:**
- Create: `app/web/overview/market_context_react_component.py`
- Create: `app/web/streamlit_components/market_context_valuation/package.json`
- Create: `app/web/streamlit_components/market_context_valuation/package-lock.json`
- Create: `app/web/streamlit_components/market_context_valuation/index.html`
- Create: `app/web/streamlit_components/market_context_valuation/tsconfig.json`
- Create: `app/web/streamlit_components/market_context_valuation/vite.config.ts`
- Create: `app/web/streamlit_components/market_context_valuation/src/main.tsx`
- Create: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Create: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Generate: `app/web/streamlit_components/market_context_valuation/component_static/*`
- Modify: `app/web/overview/market_context.py`
- Replace focused content in: `app/web/overview/market_context_helpers.py`
- Modify: `tests/test_service_contracts.py`
- Modify: task docs

**Interfaces:**
- Consumes: `build_sp500_valuation_read_model`.
- Produces: `render_market_context_valuation_component(payload, key="market_context_valuation") -> dict | None` and Streamlit fallback.

- [ ] **Step 1: Add failing entrypoint/component contract tests**

```python
def test_market_context_entrypoint_uses_only_valuation_surface(self) -> None:
    source = Path("app/web/overview/market_context.py").read_text(encoding="utf-8")
    self.assertIn("render_market_context_valuation", source)
    self.assertNotIn("render_macro_context_cockpit", source)
    self.assertNotIn("render_market_context_refresh_bar", source)

def test_market_context_valuation_react_scaffold_exists(self) -> None:
    root = Path("app/web/streamlit_components/market_context_valuation")
    self.assertTrue((root / "src" / "MarketContextValuation.tsx").exists())
    self.assertIn("최근 5년 멀티플 구간", (root / "src" / "MarketContextValuation.tsx").read_text(encoding="utf-8"))
    self.assertIn("FOMC 예상 실적 기반", (root / "src" / "MarketContextValuation.tsx").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Verify RED**

```bash
.venv/bin/python -m pytest tests/test_service_contracts.py -k "market_context and valuation" -q
```

Expected: FAIL because the component/entrypoint does not exist.

- [ ] **Step 3: Implement Python component wrapper and simplified helpers**

Define `MARKET_CONTEXT_VALUATION_COMPONENT_NAME = "market_context_valuation"` and implement the five functions named in the Task 4 Interfaces block: build availability check, component declaration/render, cached service-model load, React-first render, and compact Streamlit fallback. Follow the existing `sentiment_react_component.py` declaration pattern exactly and pass `default={"event": None}`.

`app/web/overview/market_context.py` becomes a thin entrypoint calling `render_market_context_header()` and `render_market_context_valuation()`. Delete its old cockpit/refresh imports and calls.

- [ ] **Step 4: Scaffold React and verify source contract RED-to-GREEN**

Use the existing Vite/Streamlit component versions. The payload types and top-level render are:

```tsx
type ValuationPayload = {
  schema_version: "sp500_valuation_v1";
  status: string;
  basis: BasisPayload;
  multiple_regime: MultipleRegimePayload;
  earnings_scenario: EarningsScenarioPayload;
  index_scenario: IndexScenarioPayload;
  sources: SourcePayload[];
  limitations: string[];
};

function MarketContextValuation({ args }: ComponentProps) {
  const payload = (args.payload || {}) as Partial<ValuationPayload>;
  useEffect(() => { Streamlit.setFrameHeight(); }, [payload]);
  return (
    <main className="valuation-workbench">
      <ValuationHeader basis={payload.basis} status={payload.status} />
      <MultipleRegimeSection model={payload.multiple_regime} />
      <EarningsScenarioSection earnings={payload.earnings_scenario} index={payload.index_scenario} />
      <EvidenceDisclosure sources={payload.sources} limitations={payload.limitations} />
    </main>
  );
}
```

Build charts with responsive SVG, not a new chart dependency:

- chart 1: 60m PER polyline, sigma zone rectangles/lines, current marker
- chart 2: lower/center/upper SPX band and current SPX marker
- summary grids collapse 4→2→1 columns
- source/limitation disclosure is secondary
- no action buttons, job rows, trade colors, PASS/BLOCKER, buy/sell language

- [ ] **Step 5: Build React and verify GREEN**

```bash
cd app/web/streamlit_components/market_context_valuation
npm install
npm run build
cd -
.venv/bin/python -m pytest tests/test_service_contracts.py -k "market_context and valuation" -q
git diff --check
```

Expected: Vite build exits 0, targeted tests pass.

- [ ] **Step 6: Run old-UI removal checks and commit 4차**

```bash
rg -n "render_macro_context_cockpit|render_market_context_refresh_bar|render_market_context_refresh_reflection" app/web/overview/market_context.py
```

Expected: no matches.

```bash
git add app/web/overview/market_context.py app/web/overview/market_context_helpers.py app/web/overview/market_context_react_component.py app/web/streamlit_components/market_context_valuation tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/overview-market-context-sp500-valuation-v1-20260712
git commit -m "시장 맥락을 React S&P 500 가치평가 화면으로 교체"
```

---

### Task 5: 5차 — Refresh Automation, PIT Hardening, Browser QA, Documentation

**Files:**
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/jobs/overview_automation.py`
- Modify: `app/web/ingestion/registry.py`
- Modify: `app/web/ingestion/dispatcher.py`
- Modify: `tests/test_sp500_valuation.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `.aiworkspace/note/finance/docs/{INDEX,ROADMAP,PROJECT_MAP,PRODUCT_DIRECTION}.md`
- Modify: `.aiworkspace/note/finance/docs/{architecture/README,flows/README,data/README,data/DB_SCHEMA_MAP,data/DATA_FLOW_MAP,data/TABLE_SEMANTICS}.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task docs
- Generate but do not commit: `market-context-sp500-valuation-qa.png`

**Interfaces:**
- Produces: `run_collect_sp500_valuation_context` JobResult and scheduled source refresh specs.
- Final outcome: five stages verified, documented, committed.

- [ ] **Step 1: Add failing job/automation tests**

```python
def test_valuation_collection_job_reports_source_results(self) -> None:
    with patch(
        "app.jobs.ingestion_jobs.collect_and_store_shiller_monthly_valuation",
        return_value={"rows_written": 60},
    ), patch(
        "app.jobs.ingestion_jobs.collect_and_store_fomc_sep",
        return_value={"rows_written": 10},
    ), patch(
        "app.jobs.ingestion_jobs.import_and_store_sp500_index_earnings",
        return_value={"rows_written": 4},
    ), patch(
        "app.jobs.ingestion_jobs.run_collect_ohlcv",
        return_value={"status": "success", "rows_written": 500},
    ):
        result = run_collect_sp500_valuation_context(index_earnings_path="fixture.xlsx", source_release_date="2026-07-01")
    self.assertEqual(result["status"], "success")
    self.assertEqual(result["details"]["pipeline_type"], "sp500_valuation_context")

def test_overview_automation_includes_monthly_shiller_and_quarterly_sep_refresh(self) -> None:
    plan = build_overview_automation_plan(profile="standard", now=datetime(2026, 9, 16, 18, 0))
    job_ids = {row["job_id"] for row in plan}
    self.assertIn("sp500_valuation_context", job_ids)
```

- [ ] **Step 2: Verify RED**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py tests/test_service_contracts.py -k "valuation" -q
```

Expected: FAIL because job/registry/automation paths are missing.

- [ ] **Step 3: Implement job, registry, dispatcher, and schedule**

Implement `run_collect_sp500_valuation_context(index_earnings_path=None, source_release_date=None, refresh_prices=True, progress_callback=None) -> JobResult` with the behavior below.

The job runs Shiller and SEP every invocation, imports S&P earnings only when a path/release date is supplied, and refreshes `^GSPC`/`SPY` through the existing OHLCV job boundary. It reports compact source results in JobResult but the Market Context page never renders job diagnostics.

Add one `ScheduledJobSpec` whose due policy refreshes monthly data when stale and checks official SEP on the standard calendar cadence. The collector remains safe when no new SEP exists because the vintage key is idempotent.

- [ ] **Step 4: Verify automated tests GREEN**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py tests/test_service_contracts.py -k "valuation" -q
.venv/bin/python -m pytest tests/test_service_contracts.py -k "overview and market_context" -q
```

Expected: all targeted tests pass.

- [ ] **Step 5: Run source collection smoke and DB-backed read-model smoke**

```bash
.venv/bin/python -c "from app.jobs.ingestion_jobs import run_collect_sp500_valuation_context; print(run_collect_sp500_valuation_context(refresh_prices=True))"
.venv/bin/python -c "from app.services.overview.sp500_valuation import build_sp500_valuation_read_model; print(build_sp500_valuation_read_model()['status'])"
```

Expected: collection returns structured success/partial evidence; read model returns `READY` or an explicit evidence-backed blocked state, never an exception.

- [ ] **Step 6: Run full relevant verification**

```bash
.venv/bin/python -m pytest tests/test_sp500_valuation.py -q
.venv/bin/python -m pytest tests/test_service_contracts.py -k "market_context or valuation or overview_automation" -q
.venv/bin/python -m py_compile finance/data/sp500_valuation.py finance/loaders/sp500_valuation.py app/services/overview/sp500_valuation.py app/jobs/ingestion_jobs.py app/jobs/overview_automation.py app/web/overview/market_context.py app/web/overview/market_context_helpers.py app/web/overview/market_context_react_component.py
npm --prefix app/web/streamlit_components/market_context_valuation run build
git diff --check
```

Expected: all commands exit 0.

- [ ] **Step 7: Perform Browser QA**

Start the existing Streamlit app using the project runbook, open `Workspace > Overview > 시장 맥락`, and verify:

1. old brief/sector/event/refresh UI is absent
2. both React valuation graphs render
3. current PER and 5y band labels match service payload
4. expected EPS and SPX band match service payload
5. SPY conversion appears only for same-date prices
6. source dates and limitations are visible but secondary
7. desktop and narrow viewport have no horizontal overflow

Capture `market-context-sp500-valuation-qa.png` and keep it untracked.

- [ ] **Step 8: Synchronize durable docs and task evidence**

Update canonical docs with the new Market Context promise, code ownership, DB tables, source cadence, data semantics, and removal of the old cockpit. Keep root logs to 3–5 lines with pointers to this task folder. Record commands/results in `RUNS.md`, remaining evidence gaps in `RISKS.md`, and set `STATUS.md` to complete only after verification.

- [ ] **Step 9: Verify documentation alignment and commit 5차**

```bash
find .aiworkspace/note/finance -maxdepth 4 -type f | sort
git diff --check
git status --short
```

Stage only owned implementation/docs files; exclude generated screenshots and unrelated untracked files.

```bash
git commit -m "S&P 500 가치평가 자동화와 QA 문서 정렬"
```

---

## V1.1 Data Activation Implementation Plan — 2026-07-12

### Task 6: 1차 — Graph 1 Shiller Independence

**Files:**
- Modify: `tests/test_sp500_valuation.py`
- Modify: `app/services/overview/sp500_valuation.py`

**Produces:** `calculate_multiple_regime(monthly_rows, official_window=60, sensitivity_window=36)` whose current marker is the latest Shiller trailing PER.

- [x] Add `test_multiple_regime_uses_latest_shiller_per_as_current_marker` and `test_read_model_keeps_graph_one_ready_without_official_eps`.
- [x] Run both tests and confirm RED because the current API requires current SPX/EPS and the read model shares the official-EPS gate.
- [x] Remove the graph-1 dependency on current SPX/current EPS, derive `current_pe` and `current_basis_date` from the latest valid monthly row, and calculate graph 1 before resolving graph 2 inputs.
- [x] Run the focused tests and the full valuation test module; expect GREEN.

### Task 7: 2차 — EPS Source Resolver

**Files:**
- Modify: `tests/test_sp500_valuation.py`
- Modify: `finance/loaders/sp500_valuation.py`
- Modify: `finance/loaders/__init__.py`

**Produces:** `load_latest_shiller_ttm_eps()` and `resolve_sp500_ttm_eps()` returning `current_ttm_eps`, `eps_source`, `eps_source_quality`, `eps_basis_date`, and `fallback_reason`.

- [x] Add tests for latest positive Shiller EPS, official-first selection, and Shiller fallback when official history is empty.
- [x] Run the tests and confirm RED because the loader/resolver functions do not exist.
- [x] Implement the two functions with injectable query/evidence inputs and no persistence or provider call.
- [x] Run the focused loader tests and the full valuation test module; expect GREEN.

### Task 8: 3차 — SEP EPS And Fair SPX Band

**Files:**
- Modify: `tests/test_sp500_valuation.py`
- Modify: `app/services/overview/sp500_valuation.py`

**Produces:** median GDP+PCE expected growth, one baseline expected EPS, `-1σ/mean/+1σ` SPX band, `current_vs_baseline_gap_pct`, and date-mismatch evidence.

- [x] Change the SEP formula test to expect `2.2 + 3.6 = 5.8%` and `270 × 1.058 = 285.66`.
- [x] Add a read-model test asserting source fields, SEP inputs, SPX band, and positive/negative current-vs-baseline interpretation.
- [x] Run the tests and confirm RED against the compounded-growth and mixed EPS/multiple implementation.
- [x] Implement the additive median formula and apply the same baseline projected EPS to the three PER anchors.
- [x] Run focused calculation/read-model tests and the full valuation module; expect GREEN.

### Task 9: 4차 — React Source And Decision UI

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/market_context_helpers.py`
- Modify: `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx`
- Modify: `app/web/streamlit_components/market_context_valuation/src/style.css`
- Generate: `app/web/streamlit_components/market_context_valuation/component_static/*`

**Produces:** two independent graph states plus visible EPS source/basis, SEP inputs, expected growth, fallback reason, and current valuation gap.

- [x] Add source-string/read-model contract assertions for `Robert Shiller TTM EPS`, `eps_source_quality`, `fallback_reason`, `real_gdp_pct`, `pce_inflation_pct`, and `current_vs_baseline_gap_pct`.
- [x] Run the Market Context contracts and confirm RED.
- [x] Update React types and rendering; keep source/fallback explanation visible and keep job/status/uploader controls absent.
- [x] Update the Streamlit fallback with the same essential decision fields.
- [x] Run Market Context contracts, `tsc --noEmit`, and Vite build; expect GREEN.

### Task 10: 5차 — Refresh Verification, Browser QA, Docs, Commit

**Files:**
- Verify: `finance/data/sp500_valuation.py`, `app/jobs/ingestion_jobs.py`, `app/jobs/overview_automation.py`
- Modify: task docs and affected canonical finance docs
- Generate but do not stage: `market-context-sp500-valuation-v1-1-qa.png`

- [x] Verify the existing Shiller and SEP automation remains `Ingestion -> DB -> Loader -> Service -> React` and does not require S&P workbook configuration.
- [x] Run full valuation tests, focused Market Context/service contracts, Python compile, TypeScript check, Vite build, DB-backed read-model smoke, and `git diff --check`.
- [x] Run Streamlit Browser QA, verify both charts and source/date copy against the service payload, and capture one untracked screenshot.
- [x] Synchronize task `STATUS/NOTES/RUNS/RISKS`, durable finance docs, and 3–5 line root handoff logs.
- [x] Review the owned diff, stage only owned files, and create a coherent Korean commit.

## Final Self-Review Checklist

- [ ] Every production function was introduced after a failing test.
- [ ] Current TTM actual EPS uses four completed actual As-Reported quarters.
- [ ] Five-year official classification and three-year sensitivity are distinct.
- [ ] SEP vintage refresh is idempotent and latest-success fallback is explicit.
- [ ] SPX/SPY date alignment guard is tested.
- [ ] Market Context entrypoint contains no old cockpit/refresh render calls.
- [ ] React owns presentation only; Python owns formulas.
- [ ] No provider fetch occurs in Market Context UI.
- [ ] No raw job/rows/status panel appears in the new surface.
- [ ] Generated artifacts and unrelated user files are not committed.
- [ ] Browser QA screenshot exists and is not staged.
- [ ] All relevant tests/build/compile/diff checks have fresh passing output before completion claims.
