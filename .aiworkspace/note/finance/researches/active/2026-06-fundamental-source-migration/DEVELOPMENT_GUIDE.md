# Fundamental Source Migration Development Guide

## 최종 목표

재무제표 source를 다음 구조로 정리한다.

```text
SEC EDGAR official filing/facts
  -> local raw ledger
  -> validated statement shadow
  -> source-aware factors/read models
  -> Backtest / Market Movers / UI

yfinance financial statements
  -> legacy compatibility / explicit fallback only
```

최종 상태에서는 새 기능이 `yfinance` financial statements를 primary source로 사용하지 않는다. 단, `yfinance` price, futures, event estimate 등 이미 별도 caveat가 있는 비재무제표 usage는 이번 migration 범위 밖이다.

## 공통 개발 원칙

- UI에서 SEC, yfinance, provider를 직접 fetch하지 않는다.
- raw SEC facts는 `nyse_financial_statement_values` / `nyse_financial_statement_filings`에 보존한다.
- backtest는 `available_at <= rebalance_date` 기준을 유지한다.
- annual부터 canonical로 승격한다.
- quarterly는 10-K/FY 혼입 문제를 고치기 전까지 production path로 승격하지 않는다.
- `nyse_fundamentals` / `nyse_factors`는 한동안 legacy compatibility로 보존한다.
- generated artifact, run history, registry/saved JSONL은 stage하지 않는다.

## 다른 세션 시작 시 먼저 읽을 문서

1. `AGENTS.md`
2. `.aiworkspace/note/finance/docs/INDEX.md`
3. `.aiworkspace/note/finance/docs/ROADMAP.md`
4. `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
5. `.aiworkspace/note/finance/docs/data/README.md`
6. `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md`
7. `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
8. `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
9. `.aiworkspace/note/finance/researches/active/2026-06-fundamental-source-migration/RECOMMENDATION.md`
10. `.aiworkspace/note/finance/researches/active/2026-06-fundamental-source-migration/CURRENT_PROJECT_AUDIT.md`
11. `.aiworkspace/note/finance/researches/active/2026-06-fundamental-source-migration/RISKS.md`
12. 이 문서

## 권장 실행 단위

각 phase는 별도 task로 진행한다.

```text
.aiworkspace/note/finance/tasks/active/fundamental-source-migration-p<N>-<slug>/
  PLAN.md
  STATUS.md
  NOTES.md
  RUNS.md
  RISKS.md
```

각 phase는 구현 -> focused tests -> 필요한 UI/Browser QA -> coherent commit까지 하고 멈춘다.

---

## Phase 0. Current-State Recheck

### 목적

실제 개발 시작 전에 현재 branch와 DB 상태가 research 시점과 크게 달라지지 않았는지 확인한다.

### 확인할 것

- current branch / dirty files
- `nyse_fundamentals`, `nyse_factors`, `nyse_fundamentals_statement`, `nyse_factors_statement`, `nyse_financial_statement_values` coverage
- Market Movers detail이 아직 broad `load_fundamental_snapshot`을 쓰는지
- quarterly shadow에 `latest_form_type=10-K` row가 남아 있는지

### 주요 명령

```bash
git status --short
rg -n "load_fundamental_snapshot|load_statement_fundamentals_shadow|nyse_factors|nyse_factors_statement|quality_snapshot_strict_quarterly" app finance tests
uv run python - <<'PY'
from finance.data.db.mysql import MySQLClient
db = MySQLClient("localhost", "root", "1234", 3306)
try:
    db.use_db("finance_fundamental")
    for table in ["nyse_fundamentals", "nyse_fundamentals_statement", "nyse_financial_statement_values", "nyse_factors", "nyse_factors_statement"]:
        print("\\n", table)
        for row in db.query(f"SELECT freq, COUNT(*) rows_count, COUNT(DISTINCT symbol) symbols, MAX(period_end) max_period_end FROM {table} GROUP BY freq ORDER BY freq"):
            print(row)
finally:
    db.close()
PY
```

### 완료 조건

- 현재 상태가 research 결론과 다르면 `NOTES.md`에 차이를 기록한다.
- 차이가 migration 순서를 바꿀 정도면 사용자에게 먼저 알린다.

---

## Phase 1. Source Contract Freeze

### 목적

동작을 크게 바꾸기 전에 financial statement source contract를 코드와 문서에 명시한다.

### 바꿀 가능성이 큰 파일

- `finance/loaders/fundamentals.py`
- `finance/loaders/factors.py`
- `app/services/overview/why_it_moved.py`
- `app/services/backtest_strategy_evidence_inventory.py`
- `app/services/backtest_strategy_catalog.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`

### 구현 방향

- broad tables를 `legacy_broad_yfinance`로 명명/표시한다.
- statement tables를 `statement_shadow` / `sec_edgar_statement`로 명명/표시한다.
- financial read model output에 가능한 경우 `source`, `source_mode`, `period_end`, `available_at`, `form_type`, `accession_no`를 노출한다.
- 테스트에서 legacy와 statement source label이 섞이지 않도록 고정한다.

### 하지 말 것

- 아직 yfinance collector 삭제 금지.
- DB schema 대개편 금지.
- quarterly 계산 변경 금지.

### 완료 조건

- source label이 없는 새 financial metric path가 생기지 않는다.
- docs에서 `nyse_fundamentals` / `nyse_factors`가 canonical처럼 보이지 않는다.

### 검증

```bash
git diff --check
uv run python -m py_compile finance/loaders/fundamentals.py finance/loaders/factors.py app/services/overview/why_it_moved.py
uv run python -m pytest tests/test_service_contracts.py -q -k "fundamental or fundamentals or factor or statement or why_it_moved or strategy_evidence"
```

### 권장 커밋 메시지

`재무제표 source contract 정리`

---

## Phase 2. Market Movers Annual EDGAR-First Migration

### 목적

선택 종목 조사 패널의 annual financial summary가 EDGAR annual statement shadow를 우선 사용하게 한다.

### 바꿀 가능성이 큰 파일

- `app/services/overview/why_it_moved.py`
- `app/web/overview/components/market_movers.py`
- `app/web/overview/market_movers_helpers.py`
- `tests/test_service_contracts.py`

### 구현 방향

- `build_market_mover_research_snapshot`에서 annual은 `load_statement_fundamentals_shadow`를 먼저 읽는다.
- EDGAR annual row가 있으면 PER/EPS/net income/source strip은 statement shadow 기준으로 만든다.
- EDGAR annual row가 없을 때만 broad `load_fundamental_snapshot`으로 fallback하고, UI에 `legacy yfinance fallback`을 표시한다.
- quarterly는 Phase 3 전까지 `10-Q only`가 가능하면 제한적으로 쓰고, 아니면 `수집/보정 필요`로 둔다.

### 하지 말 것

- UI에서 SEC/yfinance 직접 fetch 금지.
- quarterly 10-K/FY 값을 분기 지표처럼 보여주지 말 것.
- AI 요약/원인 판정/투자 신호 추가 금지.

### 완료 조건

- VSAT 같은 케이스에서 annual source가 silent yfinance로 노출되지 않는다.
- financial card는 source, period_end, available_at/form을 compact하게 보여준다.
- fallback일 때 사용자가 fallback임을 알 수 있다.

### 검증

```bash
git diff --check
uv run python -m py_compile app/services/overview/why_it_moved.py app/web/overview/components/market_movers.py app/web/overview/market_movers_helpers.py
uv run python -m pytest tests/test_service_contracts.py -q -k "market_mover or why_it_moved or fundamental"
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Browser QA:

- Overview > Market Movers > 선택 종목 조사
- EDGAR annual available symbol 1개
- EDGAR annual missing/fallback symbol 1개
- 좁은 화면에서 source strip 깨짐 여부

### 권장 커밋 메시지

`Market Movers 재무요약 EDGAR annual 우선 전환`

---

## Phase 3. Quarterly Correctness Gate

### 목적

quarterly statement shadow에서 10-K/FY full-year flow value가 quarterly row처럼 쓰이는 문제를 막는다.

### 바꿀 가능성이 큰 파일

- `finance/data/financial_statements.py`
- `finance/data/fundamentals.py`
- `finance/data/factors.py`
- `finance/loaders/financial_statements.py`
- `finance/loaders/fundamentals.py`
- `finance/loaders/factors.py`
- `tests/test_service_contracts.py`

### 구현 방향

- Q1-Q3 flow values는 `10-Q` / `10-Q/A`만 허용한다.
- `10-K` / `10-K/A`의 FY flow values는 quarterly shadow에 그대로 넣지 않는다.
- Q4 flow를 지원하려면 `FY - Q1 - Q2 - Q3` synthetic row로 만들고 `source_mode=synthetic_q4_from_fy_minus_quarters`처럼 표시한다.
- balance sheet instant items은 year-end `10-K` 값을 사용할 수 있지만, flow item과 별도 policy로 처리한다.
- synthetic Q4를 당장 구현하지 않는다면 quarterly UI/backtest는 `Q4 보정 미지원`으로 명확히 막는다.

### 하지 말 것

- full-year FY value를 Q4로 이름만 바꿔 저장하지 말 것.
- quarterly prototype strategy를 production처럼 보이게 하지 말 것.
- 기존 annual strict path를 깨지 말 것.

### 완료 조건

- quarterly shadow에서 flow metrics가 full-year 10-K 값으로 생성되지 않는다.
- tests가 `latest_form_type=10-K` quarterly flow row 혼입을 잡는다.
- quarterly strategy/UI는 안전한 데이터만 사용하거나 명확히 blocked 상태를 표시한다.

### 검증

```bash
git diff --check
uv run python -m py_compile finance/data/financial_statements.py finance/data/fundamentals.py finance/data/factors.py finance/loaders/financial_statements.py finance/loaders/fundamentals.py finance/loaders/factors.py
uv run python -m pytest tests/test_service_contracts.py -q -k "financial_statement or statement_shadow or quarterly or factor"
```

DB audit query:

```sql
SELECT latest_form_type, COUNT(*) rows_count, COUNT(DISTINCT symbol) symbols
FROM finance_fundamental.nyse_fundamentals_statement
WHERE freq='quarterly'
GROUP BY latest_form_type;
```

### 권장 커밋 메시지

`분기 재무제표 10-K FY 혼입 방지`

---

## Phase 4. Backtest Strategy Migration

### 목적

새 backtest 기본 흐름을 broad yfinance factors가 아니라 statement shadow factors로 전환한다.

### 바꿀 가능성이 큰 파일

- `app/runtime/backtest_strict.py`
- `app/runtime/backtest.py`
- `app/runtime/candidate_library.py`
- `app/services/backtest_strategy_catalog.py`
- `app/services/backtest_strategy_evidence_inventory.py`
- `app/services/backtest_execution.py`
- `app/services/backtest_compare_catalog.py`
- `app/web/backtest_common.py`
- `app/web/backtest_single_forms.py`
- `app/web/backtest_history_helpers.py`
- `tests/test_service_contracts.py`

### 구현 방향

- `quality_snapshot_strict_annual`, `value_snapshot_strict_annual`, `quality_value_snapshot_strict_annual`을 primary로 둔다.
- legacy `quality_snapshot`은 숨기거나 `legacy yfinance broad`로 강하게 표시한다.
- saved/history replay는 기존 run reproducibility 때문에 깨지지 않게 둔다.
- strategy evidence inventory에 source/freshness/availability 설명을 정리한다.

### 하지 말 것

- 기존 saved run을 삭제하지 말 것.
- broad `quality_snapshot` 함수를 바로 삭제하지 말 것.
- quarterly prototype을 primary catalog에 올리지 말 것.

### 완료 조건

- 새 사용자가 기본적으로 strict annual statement strategy를 선택하게 된다.
- broad yfinance factor strategy는 명시적 legacy 선택일 때만 보인다.
- tests가 strategy catalog source label을 검증한다.

### 검증

```bash
git diff --check
uv run python -m py_compile app/runtime/backtest_strict.py app/runtime/backtest.py app/runtime/candidate_library.py app/services/backtest_strategy_catalog.py app/services/backtest_strategy_evidence_inventory.py app/services/backtest_execution.py app/services/backtest_compare_catalog.py app/web/backtest_common.py app/web/backtest_single_forms.py app/web/backtest_history_helpers.py
uv run python -m pytest tests/test_service_contracts.py -q -k "backtest or strategy_catalog or strategy_evidence or candidate_library or strict_annual"
```

Browser QA:

- Backtest single / compare에서 strict annual path가 primary인지 확인
- legacy quality snapshot이 있다면 legacy label 확인

### 권장 커밋 메시지

`백테스트 기본 재무 source를 statement annual로 전환`

---

## Phase 5. Ingestion Workflow Cleanup

### 목적

사용자가 재무제표를 갱신하려고 할 때 EDGAR annual statement refresh가 자연스러운 기본 경로가 되게 한다.

### 바꿀 가능성이 큰 파일

- `app/jobs/ingestion_jobs.py`
- `app/web/ingestion_console.py`
- `app/jobs/diagnostics.py`
- `app/jobs/run_history.py`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/runbooks/` 관련 runbook

### 구현 방향

- EDGAR annual refresh / shadow rebuild를 primary financial statement refresh로 배치한다.
- broad yfinance fundamentals refresh는 legacy/advanced section으로 낮춘다.
- result UI는 run/job/raw row 숫자 중심이 아니라 `coverage`, `freshness`, `failed symbols summary`, `next action` 중심으로 compact하게 보여준다.
- SEC fair access / User-Agent / pacing 관련 runbook을 정리한다.

### 하지 말 것

- 새 provider 추가 금지.
- run dashboard를 메인 UX로 만들지 말 것.
- registry/saved JSONL rewrite 금지.

### 완료 조건

- 사용자가 재무제표 갱신을 누르면 EDGAR annual path를 먼저 쓰게 된다.
- broad yfinance refresh는 실수로 primary처럼 보이지 않는다.
- 실패/부분 성공은 actionable summary로 보인다.

### 검증

```bash
git diff --check
uv run python -m py_compile app/jobs/ingestion_jobs.py app/web/ingestion_console.py app/jobs/diagnostics.py app/jobs/run_history.py
uv run python -m pytest tests/test_service_contracts.py -q -k "ingestion or financial_statement or statement_shadow or run_history"
uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true
```

Browser QA:

- Ingestion Console 재무제표 갱신 위치
- broad yfinance legacy 위치
- partial/failure summary 표시

### 권장 커밋 메시지

`재무제표 수집 UX를 EDGAR 중심으로 정리`

---

## Phase 6. Coverage Expansion And Source QA

### 목적

EDGAR annual primary 전환 후 Top1000/Top2000/Nasdaq workflows에 필요한 coverage를 넓힌다.

### 바꿀 가능성이 큰 파일

- `app/jobs/ingestion_jobs.py`
- `app/jobs/diagnostics.py`
- `finance/loaders/universe.py`
- `finance/data/financial_statements.py`
- `finance/data/fundamentals.py`
- `finance/data/factors.py`
- `tests/test_service_contracts.py`
- 관련 runbook/docs

### 구현 방향

- S&P 500 -> Top1000 -> Top2000 -> Nasdaq-listed 순서로 coverage target을 넓힌다.
- coverage summary는 missing reason group으로 보여준다.
- EDGAR unavailable / non-US issuer / CIK mapping issue / no recent 10-K 같은 원인 후보를 분리한다.
- paid provider나 direct SEC adapter는 이 phase에서 바로 붙이지 않고, 필요하면 별도 decision으로 남긴다.

### 하지 말 것

- coverage를 맞추려고 yfinance financial statements를 primary fallback으로 되돌리지 말 것.
- 불명확한 missing reason을 상장폐지/거래정지로 단정하지 말 것.

### 완료 조건

- primary universe별 EDGAR annual coverage와 missing reason을 설명할 수 있다.
- Market Movers/Backtest에서 coverage 부족이 source trust UI로 자연스럽게 이어진다.

### 검증

```bash
git diff --check
uv run python -m pytest tests/test_service_contracts.py -q -k "coverage or financial_statement or statement_shadow or universe"
```

### 권장 커밋 메시지

`EDGAR 재무제표 coverage 진단 확장`

---

## Phase 7. Legacy yfinance Decommission

### 목적

모든 primary consumer가 EDGAR statement path로 이동한 뒤 broad yfinance financial statement path를 제거하거나 archive한다.

### 바꿀 가능성이 큰 파일

- `finance/data/fundamentals.py`
- `finance/data/factors.py`
- `finance/loaders/fundamentals.py`
- `finance/loaders/factors.py`
- `app/jobs/ingestion_jobs.py`
- `app/web/ingestion_console.py`
- `app/runtime/backtest_strict.py`
- `app/runtime/candidate_library.py`
- `app/services/backtest_*`
- `tests/test_service_contracts.py`
- `.aiworkspace/note/finance/docs/data/*`

### 구현 방향

- 먼저 import audit로 non-legacy path가 broad loaders를 쓰지 않는지 확인한다.
- legacy history replay가 필요한 경우 table/code를 read-only compatibility로 남긴다.
- 더 이상 사용하지 않는 broad collection action은 UI에서 제거한다.
- 삭제 전후로 saved run/history replay contract를 검증한다.

### 하지 말 것

- old backtest reproducibility를 깨지 말 것.
- `yfinance` package 자체를 제거하지 말 것. 가격/선물/이벤트 estimate 등 별도 사용이 남아 있다.
- DB table drop 금지. table drop은 별도 승인 필요.

### 완료 조건

- current workflows는 `nyse_fundamentals` / `nyse_factors`에 의존하지 않는다.
- legacy path는 명시적으로만 접근 가능하거나 제거되어 있다.
- docs에서 financial statement canonical source가 EDGAR로 일관된다.

### 검증

```bash
git diff --check
rg -n "load_fundamental_snapshot|load_factor_snapshot|nyse_fundamentals|nyse_factors|upsert_fundamentals|upsert_factors" app finance tests .aiworkspace/note/finance/docs
uv run python -m pytest tests/test_service_contracts.py -q -k "fundamental or factor or backtest or market_mover or ingestion"
```

### 권장 커밋 메시지

`legacy yfinance 재무제표 경로 정리`

---

## Phase 8. Final Docs / Runbook Alignment

### 목적

개발 결과를 durable docs와 runbook에 반영하고, 다음 세션이 더 이상 예전 source 구조로 돌아가지 않게 한다.

### 바꿀 가능성이 큰 파일

- `.aiworkspace/note/finance/docs/data/README.md`
- `.aiworkspace/note/finance/docs/data/DB_SCHEMA_MAP.md`
- `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- `.aiworkspace/note/finance/docs/data/DATA_QUALITY_AND_PIT_NOTES.md`
- `.aiworkspace/note/finance/docs/ROADMAP.md`
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- `.aiworkspace/note/finance/docs/runbooks/*`
- `.aiworkspace/note/finance/WORK_PROGRESS.md`
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

### 구현 방향

- canonical source map을 EDGAR 중심으로 정리한다.
- yfinance financial statements의 legacy status를 명시한다.
- quarterly policy와 remaining risk를 별도 notes에 남긴다.
- 실행 runbook에는 EDGAR annual refresh, shadow rebuild, coverage audit 절차를 남긴다.

### 완료 조건

- docs에서 `nyse_fundamentals`가 더 이상 production financial statement source처럼 읽히지 않는다.
- 다른 세션이 source 선택을 다시 추측하지 않아도 된다.

### 검증

```bash
git diff --check
find .aiworkspace/note/finance/docs -maxdepth 3 -type f | sort
```

### 권장 커밋 메시지

`재무제표 source 문서와 runbook 정렬`

---

## 권장 진행 순서 요약

1. Phase 0: 현재 상태 재확인
2. Phase 1: source contract freeze
3. Phase 2: Market Movers annual EDGAR-first
4. Phase 3: quarterly correctness gate
5. Phase 4: backtest strategy migration
6. Phase 5: ingestion workflow cleanup
7. Phase 6: EDGAR coverage expansion
8. Phase 7: legacy yfinance decommission
9. Phase 8: final docs/runbook alignment

## 중요한 의사결정 포인트

- Phase 3에서 synthetic Q4를 구현할지, 아니면 quarterly를 당분간 blocked로 둘지 결정해야 한다.
- Phase 6에서 Top2000/Nasdaq coverage 확장 목표를 어디까지 잡을지 결정해야 한다.
- paid normalized provider는 이번 migration의 전제가 아니다. 필요하면 Phase 6 이후 별도 research/approval로 다룬다.
- table drop은 이 plan 범위가 아니다. broad table은 archive/read-only compatibility로 먼저 둔다.
