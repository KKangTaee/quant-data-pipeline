# Recommendation

## Short answer

yfinance financial statements should not remain the canonical source. However, removing them immediately is too risky because legacy backtests, ingestion jobs, Market Movers detail, and some fallback logic still depend on broad fundamentals/factors.

The recommended target is:

```text
Canonical financial statements:
SEC EDGAR raw facts / filings
  -> local raw ledger
  -> validated statement shadow
  -> source-aware factor/read models

Compatibility / fallback:
yfinance broad fundamentals
  -> frozen legacy tables
  -> explicit fallback labels only
```

## Direct answers to the user questions

### 1. yfinance를 없애도 되는가?

Financial statement canonical source에서는 없애는 것이 맞다. 하지만 지금 당장 code/table을 삭제하면 안 된다.

Reason:

- broad `quality_snapshot` backtest는 `nyse_factors`에 의존한다.
- Market Movers 선택 종목 조사 financial snapshot은 broad `load_fundamental_snapshot`을 기본으로 쓴다.
- Ingestion Console에는 broad fundamentals refresh path가 노출되어 있다.
- statement shadow의 shares fallback 일부가 broad fundamentals를 참조한다.

Decision:

- New development: yfinance financial statements 사용 금지.
- Existing features: deprecate -> migrate -> compatibility hide -> delete 순서.
- Price / futures / event estimate 같은 다른 yfinance usage는 별도 provider strategy로 분리해서 다룬다.

### 2. `edgartools`를 신뢰할 수 있는가?

`edgartools` 자체를 최종 truth로 믿으면 안 되고, SEC EDGAR source와 local raw ledger를 믿는 구조로 써야 한다.

Good:

- SEC filing / facts에 접근하기 편하다.
- 이 프로젝트는 이미 accession, form, accepted time, unit, concept를 DB에 저장한다.
- wrapper를 교체해도 raw ledger schema를 유지할 수 있다.

Guardrails:

- ingestion에는 SEC User-Agent / fair access 준수가 필요하다.
- raw facts sample을 SEC official API response와 주기적으로 cross-check한다.
- library-normalized statement view만 저장하지 않는다.
- `available_at`, `accession_no`, `form_type`, `fiscal_period`, `unit` 없는 row는 strict path에서 제외한다.

### 3. yfinance 기반 backtest와 data collection을 EDGAR로 마이그레이션 가능한가?

가능하다. 단, annual부터 먼저 해야 한다.

Already ready:

- `quality_snapshot_strict_annual`
- `value_snapshot_strict_annual`
- `quality_value_snapshot_strict_annual`
- statement factor shadow path

Needs migration:

- legacy `quality_snapshot`
- Market Movers detail financial summary
- Ingestion Console primary refresh copy/actions
- broad `nyse_factors` dependency in strategy catalog/history copy

Blocked until fixed:

- strict quarterly prototype. Current quarterly shadow allows `10-K/FY` rows, so full-year values can look like quarterly values.

### 4. 실전 프로그램을 만들기 위한 최선

Best architecture:

1. SEC EDGAR raw facts as canonical source.
2. Store raw filing/value ledger unchanged enough for audit.
3. Build derived statement shadow by explicit concept mapping.
4. Build factors/read models from statement shadow only.
5. Use `available_at <= rebalance_date` for PIT backtests.
6. UI reads local DB only and shows source/freshness evidence compactly.
7. yfinance financial statements become legacy fallback, not primary source.

### 5. 수집 / 백테스트 / UX 최신 표시에 어떤 정보를 써야 하는가?

| Use case | Recommended data |
| --- | --- |
| Raw collection | SEC EDGAR filings / company facts via `edgartools` or direct SEC adapter |
| Annual backtest | `nyse_factors_statement` annual, with `fundamental_available_at` |
| Value / quality factors | statement shadow factors, not `nyse_factors` |
| Quarterly backtest | after Q4/FY correction only; Q1-Q3 from 10-Q, Q4 synthetic or clearly annual |
| Market Movers financial summary | annual statement shadow first, quarterly 10-Q-only if available, explicit fallback otherwise |
| Market cap / price return | price history / asset profile / quote snapshot, not financial statements |
| UI freshness | period_end + available_at + form_type + source badge |

### 6. 다른 대안은?

Alternatives exist, but none should replace the local SEC raw ledger without a deliberate license/provider decision.

- Direct SEC API: best wrapper-risk reduction.
- Financial Modeling Prep / Polygon / Alpha Vantage: useful normalized paid/free API alternatives or cross-check sources.
- OpenBB-style aggregator: useful developer convenience, but still needs source contract.
- Commercial data vendors: best if the project later needs survivorship-safe universes, restated fundamentals, point-in-time vendor history, or institutional coverage.

## Migration plan

### Phase 1. Source contract freeze

Purpose:

- Make the source boundary explicit without changing behavior.

Actions:

- Add a finance source contract note to docs.
- Mark `nyse_fundamentals` / `nyse_factors` as `legacy_broad_yfinance`.
- Mark `nyse_fundamentals_statement` / `nyse_factors_statement` as `canonical_candidate_statement_shadow`.
- Add tests that Market Movers and backtest services can expose source labels.

Done when:

- Any financial metric read model can say `source`, `period_end`, `available_at`, `form_type`.

### Phase 2. Market Movers annual migration

Purpose:

- Stop showing yfinance annual financials in the selected-symbol detail panel when EDGAR annual shadow exists.

Actions:

- Change Market Movers research snapshot to prefer annual `load_statement_fundamentals_shadow`.
- Keep yfinance only as labeled fallback.
- Show fiscal year-end / accepted date / form in compact source strip.
- Keep quarterly as 10-Q-only or fallback until Phase 3.

Done when:

- VSAT-like cards no longer silently mix broad yfinance annual and quarterly facts.

### Phase 3. Quarterly correctness

Purpose:

- Make quarterly statement data safe enough for UI and later backtests.

Actions:

- Split quarterly raw/shadow policy:
  - Q1-Q3: 10-Q / 10-Q/A only.
  - Q4 flow items: synthetic `FY - Q1 - Q2 - Q3`, marked `synthetic_q4`.
  - Balance sheet instant items: year-end 10-K value may be used, marked separately.
- Add anomaly tests for `latest_form_type=10-K` quarterly rows.
- Disable or clearly block quarterly prototype strategy until fixed.

Done when:

- quarterly rows cannot silently contain full-year flow values.

### Phase 4. Backtest migration

Purpose:

- Move official strategy catalog away from broad yfinance factors.

Actions:

- Default quality/value strategies to strict annual statement factors.
- Demote `quality_snapshot` to legacy compatibility.
- Update candidate library/history labels.
- Add migration notes for old saved runs.

Done when:

- New backtests do not depend on `nyse_factors` unless explicitly choosing legacy.

### Phase 5. Ingestion UX cleanup

Purpose:

- Make EDGAR refresh the normal fundamentals workflow.

Actions:

- In Ingestion Console, make annual EDGAR statement refresh/shadow rebuild the primary path.
- Move broad yfinance fundamentals refresh into legacy/advanced expander.
- Replace row-count-heavy result UI with concise action results and coverage trust.

Done when:

- A user updating financial statements naturally runs EDGAR refresh, not yfinance broad refresh.

### Phase 6. Decommission broad yfinance financial statements

Purpose:

- Remove duplicate patterns after consumers are migrated.

Actions:

- Stop scheduled/manual primary broad fundamentals collection.
- Keep archived table or migration snapshot if needed for old run reproducibility.
- Remove broad financial statement UI from primary navigation.
- Delete code only after tests prove no non-legacy path imports broad loaders.

Done when:

- `nyse_fundamentals` / `nyse_factors` are no longer active dependencies of current workflows.

## Final recommendation

Do not delete yfinance today. Freeze it as legacy. Promote EDGAR annual statement shadow to primary. Fix quarterly before trusting it. Then migrate Market Movers, backtests, and ingestion UI in that order.
