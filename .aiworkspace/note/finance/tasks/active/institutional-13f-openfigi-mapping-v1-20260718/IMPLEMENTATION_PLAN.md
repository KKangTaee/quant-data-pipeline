# Institutional 13F OpenFIGI Mapping V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 무료 OpenFIGI v3로 current curated-manager 13F CUSIP/CINS를 안전한 미국 Equity ticker identity로 보강하고 기존 Institutional Portfolios가 그 결과를 자동 사용하게 한다.

**Architecture:** 새 `finance/data/institutional_13f_mapping.py`가 provider 요청, 응답 정규화, current resolution persistence, selected-CIK backfill을 소유한다. 새 resolution table은 `(identifier_value, source)`당 current provider 상태를 저장하며 legacy `institutional_13f_cusip_symbol_map`과 분리된다. Loader는 OpenFIGI mapped/ambiguous gate를 먼저 읽고, provider가 unmapped/error-only일 때만 legacy exact issuer-name mapping과 service curated seed로 fallback한다.

**Tech Stack:** Python 3.12, standard-library `urllib`, PyMySQL/MySQL, pandas loader frames, unittest/pytest, Streamlit ingestion action, existing React Institutional Portfolios workbench.

## Global Constraints

- OpenFIGI endpoint는 `https://api.openfigi.com/v3/mapping`만 사용한다.
- 숫자로 시작하는 9자 식별자는 `ID_CUSIP`, 문자로 시작하는 9자 식별자는 `ID_CINS`로 요청한다.
- 모든 mapping job은 `exchCode=US`, `marketSecDes=Equity`를 포함한다.
- distinct `(ticker, compositeFIGI)`가 하나일 때만 `mapped`; 0개는 `unmapped`; 2개 이상은 `ambiguous`다.
- API key는 `OPENFIGI_API_KEY` 환경변수 또는 explicit argument로만 받으며 저장하거나 출력하지 않는다.
- key 없음은 10 jobs/request, key 있음은 100 jobs/request를 넘지 않는다.
- 429/500/503만 bounded retry하고 400/401/schema error는 재시도하지 않는다.
- provider/transport error는 마지막 정상 resolution을 지우지 않는다.
- OpenFIGI fetch는 explicit ingestion/backfill에서만 수행하며 normal UI render에서는 호출하지 않는다.
- legacy mapping row를 삭제하거나 CUSIP-only 후보로 자동 승격하지 않는다.
- run/job/row diagnostic panel, 추천, 매수/매도 신호, broker action을 추가하지 않는다.
- initial actual backfill은 current curated 12 managers의 latest holdings로 제한한다.

---

## Execution Preflight

- [ ] **Step 1: Verify this checkout is already an isolated linked worktree**

Run:

```bash
git_dir=$(cd "$(git rev-parse --git-dir)" && pwd -P)
git_common=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
branch=$(git branch --show-current)
superproject=$(git rev-parse --show-superproject-working-tree 2>/dev/null || true)
printf '%s\n' "$git_dir" "$git_common" "$branch" "$superproject"
```

Expected: `git_dir != git_common`, branch `codex/main-dev`, empty superproject. Do not create another worktree.

- [ ] **Step 2: Run the focused baseline before changing code**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_portfolios.py
```

Expected: current Institutional Portfolios tests pass. If they do not, record the exact pre-existing failure in task `RUNS.md` before implementation.

---

### Task 1: Pure OpenFIGI V3 Resolver

**Files:**
- Create: `finance/data/institutional_13f_mapping.py`
- Create: `tests/test_institutional_13f_mapping.py`

**Interfaces:**
- Produces: `normalize_13f_identifier(value: Any) -> str | None`
- Produces: `build_openfigi_mapping_job(identifier: str) -> dict[str, str]`
- Produces: `normalize_openfigi_mapping_result(identifier: str, payload: dict[str, Any], *, attempted_at: str) -> dict[str, Any]`
- Produces: `collect_openfigi_resolutions(identifier_rows: Iterable[Mapping[str, Any]], *, api_key: str | None = None, opener: Any = urlopen, sleep_fn: Any = time.sleep, timeout: float = 30.0, max_retries: int = 2) -> list[dict[str, Any]]`
- Consumers: Task 2 persistence and Task 4 ingestion job.

- [ ] **Step 1: Write failing normalization and classification tests**

Create tests that assert the wished-for API:

```python
from finance.data.institutional_13f_mapping import (
    build_openfigi_mapping_job,
    normalize_13f_identifier,
    normalize_openfigi_mapping_result,
)


def test_identifier_type_and_us_equity_filters() -> None:
    assert normalize_13f_identifier(" 632307104 ") == "632307104"
    assert normalize_13f_identifier("n62509109") == "N62509109"
    assert normalize_13f_identifier("bad") is None
    assert build_openfigi_mapping_job("632307104") == {
        "idType": "ID_CUSIP",
        "idValue": "632307104",
        "exchCode": "US",
        "marketSecDes": "Equity",
    }
    assert build_openfigi_mapping_job("N62509109")["idType"] == "ID_CINS"


def test_result_normalization_dedupes_one_identity_and_blocks_multiple() -> None:
    mapped = normalize_openfigi_mapping_result(
        "632307104",
        {"data": [
            {"ticker": "NTRA", "name": "NATERA INC", "figi": "BBG1", "compositeFIGI": "BBG1"},
            {"ticker": "NTRA", "name": "NATERA INC", "figi": "BBG1", "compositeFIGI": "BBG1"},
        ]},
        attempted_at="2026-07-18 12:00:00",
    )
    assert mapped["resolution_status"] == "mapped"
    assert mapped["symbol"] == "NTRA"
    assert mapped["figi"] == "BBG1"
    assert mapped["candidate_count"] == 1

    ambiguous = normalize_openfigi_mapping_result(
        "000000001",
        {"data": [
            {"ticker": "AAA", "compositeFIGI": "BBGA"},
            {"ticker": "BBB", "compositeFIGI": "BBGB"},
        ]},
        attempted_at="2026-07-18 12:00:00",
    )
    assert ambiguous["resolution_status"] == "ambiguous"
    assert ambiguous["symbol"] is None
    assert ambiguous["candidate_count"] == 2

    missing = normalize_openfigi_mapping_result(
        "000000002",
        {"warning": "No identifier found."},
        attempted_at="2026-07-18 12:00:00",
    )
    assert missing["resolution_status"] == "unmapped"
    assert missing["last_attempt_status"] == "success"
```

- [ ] **Step 2: Run RED and confirm the module is missing**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py -k 'identifier_type or result_normalization'
```

Expected: FAIL with `ModuleNotFoundError: finance.data.institutional_13f_mapping`.

- [ ] **Step 3: Implement identifier and response pure functions**

Create the module with these constants and exact output contract:

```python
OPENFIGI_MAPPING_URL = "https://api.openfigi.com/v3/mapping"
OPENFIGI_SOURCE = "openfigi_v3"
OPENFIGI_SOURCE_REF = "https://www.openfigi.com/api/documentation"


def normalize_13f_identifier(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    return text if len(text) == 9 and text.isalnum() else None


def build_openfigi_mapping_job(identifier: str) -> dict[str, str]:
    clean = normalize_13f_identifier(identifier)
    if not clean:
        raise ValueError(f"Invalid 13F identifier: {identifier!r}")
    return {
        "idType": "ID_CINS" if clean[0].isalpha() else "ID_CUSIP",
        "idValue": clean,
        "exchCode": "US",
        "marketSecDes": "Equity",
    }
```

`normalize_openfigi_mapping_result` must:

1. Normalize ticker/name/`compositeFIGI or figi`.
2. Dedupe by `(ticker, composite_figi)`.
3. Return the shared fields `identifier_value`, `identifier_type`, `source`, `source_ref`, `resolution_status`, `symbol`, `provider_name`, `figi`, `candidate_count`, `candidates_json`, `warning_text`, `error_text`, `last_attempt_status`, `attempted_at`, `resolved_at`.
4. Serialize only compact candidate fields with `json.dumps(..., ensure_ascii=False, sort_keys=True)`.
5. Use `mapped` only for one candidate, `ambiguous` for two or more, and `unmapped` for zero including a v3 `warning`.
6. `_error_resolution` uses neutral `resolution_status="unmapped"`, null accepted identity, `last_attempt_status="error"`, and null `resolved_at`; on an existing row Task 2's conditional UPSERT preserves the prior normal resolution.

- [ ] **Step 4: Add RED tests for batching, optional key, and bounded retry**

Use a fake context-manager response and an injected opener:

```python
import json
from urllib.error import HTTPError


class FakeResponse:
    def __init__(self, payload: object, headers: dict[str, str] | None = None) -> None:
        self.payload = payload
        self.headers = headers or {}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_collect_batches_10_without_key_and_100_with_key() -> None:
    calls: list[tuple[object, float]] = []

    def opener(request: object, timeout: float):
        calls.append((request, timeout))
        jobs = json.loads(request.data.decode("utf-8"))
        return FakeResponse([{"data": [{"ticker": job["idValue"], "compositeFIGI": f"FIGI-{job['idValue']}"}]} for job in jobs])

    rows = [{"identifier_value": f"{index:09d}"} for index in range(25)]
    assert len(collect_openfigi_resolutions(rows, opener=opener, sleep_fn=lambda _: None)) == 25
    assert [len(json.loads(call[0].data)) for call in calls] == [10, 10, 5]

    calls.clear()
    collect_openfigi_resolutions(rows, api_key="free-key", opener=opener, sleep_fn=lambda _: None)
    assert [len(json.loads(call[0].data)) for call in calls] == [25]
    assert calls[0][0].headers["X-openfigi-apikey"] == "free-key"


def test_retryable_http_error_retries_but_401_does_not() -> None:
    retry_calls = 0

    def retry_opener(request: object, timeout: float):
        nonlocal retry_calls
        retry_calls += 1
        if retry_calls == 1:
            raise HTTPError(request.full_url, 429, "Too Many", {"ratelimit-reset": "0"}, None)
        return FakeResponse([{"warning": "No identifier found."}])

    rows = collect_openfigi_resolutions(
        [{"identifier_value": "632307104"}], opener=retry_opener, sleep_fn=lambda _: None
    )
    assert retry_calls == 2
    assert rows[0]["resolution_status"] == "unmapped"

    def unauthorized(request: object, timeout: float):
        raise HTTPError(request.full_url, 401, "Unauthorized", {}, None)

    rows = collect_openfigi_resolutions(
        [{"identifier_value": "632307104"}], opener=unauthorized, sleep_fn=lambda _: None
    )
    assert rows[0]["last_attempt_status"] == "error"
```

Add one success-response test whose headers contain `ratelimit-remaining: 0` and `ratelimit-reset: 2`; assert the injected `sleep_fn` receives `2.0` before the next batch. This prevents anonymous backfill from repeatedly discovering the limit through 429 responses.

- [ ] **Step 5: Run RED for the collector**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py -k 'collect or retryable'
```

Expected: FAIL because `collect_openfigi_resolutions`/HTTP behavior is not implemented.

- [ ] **Step 6: Implement the minimal HTTP collector**

Implementation requirements:

```python
def collect_openfigi_resolutions(
    identifier_rows: Iterable[Mapping[str, Any]],
    *,
    api_key: str | None = None,
    opener: Any = urlopen,
    sleep_fn: Any = time.sleep,
    timeout: float = 30.0,
    max_retries: int = 2,
) -> list[dict[str, Any]]:
    clean_rows = _dedupe_identifier_rows(identifier_rows)
    batch_size = 100 if str(api_key or "").strip() else 10
    output: list[dict[str, Any]] = []
    batches = list(_chunks(clean_rows, batch_size))
    for batch_index, batch in enumerate(batches):
        jobs = [build_openfigi_mapping_job(row["identifier_value"]) for row in batch]
        payload, error_text, rate = _request_openfigi_batch(
            jobs,
            api_key=api_key,
            opener=opener,
            sleep_fn=sleep_fn,
            timeout=timeout,
            max_retries=max_retries,
        )
        attempted_at = _now_utc_text()
        if error_text is not None:
            output.extend(_error_resolution(row, error_text, attempted_at=attempted_at) for row in batch)
            continue
        if len(payload) != len(batch):
            message = f"OpenFIGI response length mismatch: expected {len(batch)}, got {len(payload)}"
            output.extend(_error_resolution(row, message, attempted_at=attempted_at) for row in batch)
            continue
        output.extend(
            normalize_openfigi_mapping_result(
                row["identifier_value"], result, attempted_at=attempted_at
            )
            for row, result in zip(batch, payload)
        )
        if batch_index < len(batches) - 1 and rate.get("remaining") == 0:
            sleep_fn(max(0.0, float(rate.get("reset") or 0.0)))
    return output
```

`_request_openfigi_batch` must build `urllib.request.Request`, set `Content-Type: application/json`, add `X-OPENFIGI-APIKEY` only when non-empty, parse JSON arrays, retry only status 429/500/503, and cap attempts at `max_retries + 1`. It must return compact rate state from `ratelimit-remaining`/`ratelimit-reset`; when a successful non-final batch reports remaining `0`, the collector sleeps for the reported reset seconds before issuing the next batch.

Use this request helper shape so tests can inject `opener`/`sleep_fn` without network:

```python
def _float_header(headers: Mapping[str, Any], name: str, default: float) -> float:
    try:
        return float(headers.get(name, default))
    except (TypeError, ValueError):
        return default


def _chunks(rows: list[dict[str, Any]], size: int) -> Iterable[list[dict[str, Any]]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def _dedupe_identifier_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        identifier = normalize_13f_identifier(row.get("identifier_value") or row.get("cusip"))
        if identifier and identifier not in seen:
            output.append({**dict(row), "identifier_value": identifier})
            seen.add(identifier)
    return output


def _request_openfigi_batch(
    jobs: list[dict[str, str]],
    *,
    api_key: str | None,
    opener: Any,
    sleep_fn: Any,
    timeout: float,
    max_retries: int,
) -> tuple[list[dict[str, Any]], str | None, dict[str, float]]:
    headers = {"Content-Type": "application/json", "User-Agent": "quant-data-pipeline/13f-identity"}
    if str(api_key or "").strip():
        headers["X-OPENFIGI-APIKEY"] = str(api_key).strip()
    request = Request(
        OPENFIGI_MAPPING_URL,
        data=json.dumps(jobs).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    for attempt in range(max_retries + 1):
        try:
            with opener(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, list):
                    return [], "OpenFIGI response must be a JSON array.", {}
                rate = {
                    "remaining": _float_header(response.headers, "ratelimit-remaining", -1.0),
                    "reset": _float_header(response.headers, "ratelimit-reset", 0.0),
                }
                return payload, None, rate
        except HTTPError as exc:
            if exc.code not in {429, 500, 503} or attempt >= max_retries:
                return [], f"OpenFIGI HTTP {exc.code}: {exc.reason}", {}
            reset = _float_header(exc.headers or {}, "ratelimit-reset", 0.0)
            sleep_fn(max(reset, 0.5 * (2**attempt)))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            return [], f"OpenFIGI request failed: {exc}", {}
    return [], "OpenFIGI request failed after bounded retries.", {}
```

- [ ] **Step 7: Verify Task 1 GREEN and commit**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py
.venv/bin/python -m py_compile finance/data/institutional_13f_mapping.py
git diff --check
git add finance/data/institutional_13f_mapping.py tests/test_institutional_13f_mapping.py
git commit -m "OpenFIGI 13F 식별자 변환기 추가"
```

Expected: focused tests PASS and one coherent resolver commit.

---

### Task 2: Canonical Resolution Schema And Idempotent Backfill Writer

**Files:**
- Modify: `finance/data/db/schema.py`
- Modify: `finance/data/institutional_13f_mapping.py`
- Modify: `tests/test_institutional_13f_mapping.py`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**
- Produces table: `finance_meta.institutional_13f_identifier_resolution`
- Produces: `load_latest_13f_identifier_rows(db: MySQLClient, ciks: Iterable[str], *, refresh_existing: bool = False) -> list[dict[str, Any]]`
- Produces: `upsert_13f_identifier_resolutions(db: MySQLClient, rows: list[dict[str, Any]]) -> int`
- Produces: `collect_and_store_openfigi_13f_mappings(*, ciks: Iterable[str], api_key: str | None = None, refresh_existing: bool = False, ...) -> dict[str, Any]`
- Consumers: Task 3 loaders and Task 4 job wrapper.

- [ ] **Step 1: Write RED schema and writer tests**

Add assertions for the new table and FakeDB behavior:

```python
class FakeDB:
    def __init__(self) -> None:
        self.executemany_calls: list[tuple[str, list[dict[str, object]]]] = []

    def executemany(self, sql: str, rows: list[dict[str, object]]) -> None:
        self.executemany_calls.append((sql, rows))


def test_schema_defines_identifier_resolution_current_state() -> None:
    from finance.data.db.schema import INSTITUTIONAL_13F_SCHEMAS

    sql = INSTITUTIONAL_13F_SCHEMAS["institutional_13f_identifier_resolution"]
    assert "UNIQUE KEY uk_identifier_source (identifier_value, source)" in sql
    assert "resolution_status" in sql
    assert "last_attempt_status" in sql
    assert "candidates_json JSON" in sql


def test_resolution_upsert_preserves_normal_state_on_error_attempt() -> None:
    fake_db = FakeDB()
    error_row = {
        "identifier_value": "632307104",
        "identifier_type": "ID_CUSIP",
        "source": "openfigi_v3",
        "resolution_status": "unmapped",
        "symbol": None,
        "provider_name": None,
        "figi": None,
        "candidate_count": 0,
        "candidates_json": "[]",
        "source_ref": "https://www.openfigi.com/api/documentation",
        "warning_text": None,
        "error_text": "OpenFIGI HTTP 503: unavailable",
        "last_attempt_status": "error",
        "attempted_at": "2026-07-18 12:00:00",
        "resolved_at": None,
    }
    count = upsert_13f_identifier_resolutions(fake_db, [error_row])
    sql, params = fake_db.executemany_calls[0]
    assert count == 1
    assert "IF(VALUES(last_attempt_status) = 'error', resolution_status" in sql
    assert "IF(VALUES(last_attempt_status) = 'error', symbol" in sql
    assert params[0]["last_attempt_status"] == "error"
```

Add a test that captures the selection SQL and verifies latest accession, CIK placeholders, dedupe by identifier, and the default `missing or last error` refresh scope.

- [ ] **Step 2: Run RED for schema/writer**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py -k 'identifier_resolution or resolution_upsert or latest_13f_identifier'
```

Expected: FAIL because the schema and writer do not exist.

- [ ] **Step 3: Add the canonical resolution table**

Add this table to `INSTITUTIONAL_13F_SCHEMAS`:

```sql
CREATE TABLE IF NOT EXISTS institutional_13f_identifier_resolution (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  identifier_value CHAR(9) NOT NULL,
  identifier_type VARCHAR(16) NOT NULL,
  source VARCHAR(64) NOT NULL,
  resolution_status VARCHAR(16) NOT NULL,
  symbol VARCHAR(20) NULL,
  provider_name VARCHAR(255) NULL,
  figi VARCHAR(16) NULL,
  candidate_count INT NOT NULL DEFAULT 0,
  candidates_json JSON NULL,
  source_ref VARCHAR(1024) NULL,
  warning_text TEXT NULL,
  error_text TEXT NULL,
  last_attempt_status VARCHAR(16) NOT NULL,
  attempted_at TIMESTAMP NULL,
  resolved_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_identifier_source (identifier_value, source),
  KEY ix_resolution_status (resolution_status),
  KEY ix_resolution_symbol (symbol),
  KEY ix_last_attempt_status (last_attempt_status)
);
```

- [ ] **Step 4: Implement selected-CIK query and conditional UPSERT**

`load_latest_13f_identifier_rows` must normalize CIKs to ten digits and query `manager.latest_accession_number -> holding`, returning one row per CUSIP. With `refresh_existing=False`, include only rows with no OpenFIGI resolution or `last_attempt_status='error'`; with `True`, include all selected identifiers.

`upsert_13f_identifier_resolutions` must use `INSERT ... ON DUPLICATE KEY UPDATE`. For rows whose incoming `last_attempt_status='error'`, preserve `resolution_status`, `symbol`, `provider_name`, `figi`, `candidate_count`, `candidates_json`, `warning_text`, and `resolved_at`, while updating `error_text`, `last_attempt_status`, and `attempted_at`. For normal responses, replace the current resolution fields and clear `error_text`.

- [ ] **Step 5: Implement the DB orchestration entry point**

```python
def collect_and_store_openfigi_13f_mappings(
    *,
    ciks: Iterable[str],
    api_key: str | None = None,
    refresh_existing: bool = False,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    opener: Any = urlopen,
    sleep_fn: Any = time.sleep,
    timeout: float = 30.0,
    max_retries: int = 2,
) -> dict[str, Any]:
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db("finance_meta")
        sync_table_schema(
            db,
            "institutional_13f_identifier_resolution",
            INSTITUTIONAL_13F_SCHEMAS["institutional_13f_identifier_resolution"],
            "finance_meta",
        )
        identifiers = load_latest_13f_identifier_rows(db, ciks, refresh_existing=refresh_existing)
        resolutions = collect_openfigi_resolutions(
            identifiers,
            api_key=api_key or os.getenv("OPENFIGI_API_KEY"),
            opener=opener,
            sleep_fn=sleep_fn,
            timeout=timeout,
            max_retries=max_retries,
        )
        rows_written = upsert_13f_identifier_resolutions(db, resolutions)
    finally:
        db.close()
    counts = Counter(row["resolution_status"] if row["last_attempt_status"] != "error" else "error" for row in resolutions)
    return {
        "source": OPENFIGI_SOURCE,
        "source_ref": OPENFIGI_SOURCE_REF,
        "identifiers_requested": len(identifiers),
        "rows_written": rows_written,
        "mapped": counts["mapped"],
        "ambiguous": counts["ambiguous"],
        "unmapped": counts["unmapped"],
        "errors": counts["error"],
        "api_key_used": bool(api_key or os.getenv("OPENFIGI_API_KEY")),
        "target_table": "finance_meta.institutional_13f_identifier_resolution",
    }
```

Do not return the API key or full provider response.

- [ ] **Step 6: Verify Task 2 GREEN and commit**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py -k 'schema or resolution or openfigi'
.venv/bin/python -m py_compile finance/data/db/schema.py finance/data/institutional_13f_mapping.py
git diff --check
git add finance/data/db/schema.py finance/data/institutional_13f_mapping.py tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py
git commit -m "13F 식별자 해석 상태 저장"
```

Expected: schema/writer tests PASS and error attempts preserve prior normal state by SQL contract.

---

### Task 3: Safe Loader Source Precedence And Reverse Lookup

**Files:**
- Modify: `finance/loaders/institutional_13f.py`
- Modify: `tests/test_institutional_13f_mapping.py`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**
- Consumes: `institutional_13f_identifier_resolution` current OpenFIGI row.
- Produces loader fields: `holding_symbol`, `symbol_source`, `mapping_status`, `figi`, `sector`, `industry`.
- Preserves: `load_institutional_13f_holdings`, `load_institutional_13f_interest`, `load_institutional_13f_popularity_ranking` public signatures.

- [ ] **Step 1: Write RED loader precedence tests with captured SQL and service fixtures**

Add tests that require:

```python
assert "institutional_13f_identifier_resolution" in captured_sql
assert "ir.resolution_status = 'mapped'" in captured_sql
assert "ir.resolution_status = 'ambiguous'" in captured_sql
assert "lm.issuer_key = UPPER(h.issuer_name)" in captured_sql
assert "nyse_asset_profile" in captured_sql
```

Add a service fixture row with `mapping_status="ambiguous"`, `holding_symbol=None`, `symbol_source="openfigi_v3_ambiguous"` and assert the existing price action remains `mapping_ambiguous`. Add a mapped fixture with provider canonical name different from SEC issuer text and assert the service exposes the OpenFIGI ticker.

- [ ] **Step 2: Run RED for loader precedence**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py -k 'loader_precedence or canonical_name or ambiguous_interest'
```

Expected: FAIL because loaders do not read the new resolution table.

- [ ] **Step 3: Add shared identity SQL fragments**

Define fixed-alias helpers in the loader so every holding query uses the same rules:

```python
_IDENTITY_JOIN_SQL = """
LEFT JOIN institutional_13f_identifier_resolution ir
  ON h.cusip = ir.identifier_value
 AND ir.source = 'openfigi_v3'
LEFT JOIN (
  SELECT
    cusip,
    UPPER(issuer_name) AS issuer_key,
    COUNT(DISTINCT symbol) AS symbol_count,
    CASE WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(symbol) END AS symbol,
    CASE WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(source) ELSE 'legacy_mapping_ambiguous' END AS source,
    CASE WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(sector) END AS sector,
    CASE WHEN COUNT(DISTINCT symbol) = 1 THEN MAX(industry) END AS industry
  FROM institutional_13f_cusip_symbol_map
  GROUP BY cusip, UPPER(issuer_name)
) lm
  ON h.cusip = lm.cusip
 AND lm.issuer_key = UPPER(h.issuer_name)
LEFT JOIN nyse_asset_profile ap
  ON ap.symbol = CASE
      WHEN ir.resolution_status = 'mapped' THEN ir.symbol
      ELSE COALESCE(h.holding_symbol, lm.symbol)
    END
"""
```

The shared select expressions must implement:

```sql
CASE
  WHEN ir.resolution_status = 'ambiguous' THEN NULL
  WHEN ir.resolution_status = 'mapped' THEN ir.symbol
  WHEN lm.symbol_count > 1 THEN NULL
  ELSE COALESCE(h.holding_symbol, lm.symbol)
END AS holding_symbol,
CASE
  WHEN ir.resolution_status = 'ambiguous' THEN 'openfigi_v3_ambiguous'
  WHEN ir.resolution_status = 'mapped' THEN 'openfigi_v3'
  WHEN lm.symbol_count > 1 THEN 'legacy_mapping_ambiguous'
  ELSE COALESCE(h.symbol_source, lm.source)
END AS symbol_source,
CASE
  WHEN ir.resolution_status = 'ambiguous' THEN 'ambiguous'
  WHEN ir.resolution_status = 'mapped' AND ir.symbol IS NOT NULL THEN 'mapped'
  WHEN lm.symbol_count > 1 THEN 'ambiguous'
  WHEN COALESCE(h.holding_symbol, lm.symbol) IS NOT NULL THEN 'mapped'
  ELSE 'unmapped'
END AS mapping_status
```

Use `COALESCE(h.figi, ir.figi)` for FIGI and `COALESCE(h.sector, ap.sector, lm.sector)` / industry equivalent. The grouped legacy subquery guarantees one output row per holding and explicitly marks multiple exact-name symbols ambiguous. Keep legacy issuer exact-match; never use legacy CUSIP-only symbol in a holding row.

- [ ] **Step 4: Apply the same precedence to all reader paths**

Update:

- filing holdings.
- CUSIP interest lookup.
- holding-symbol interest lookup.
- issuer-text interest lookup.
- popularity ranking symbol aggregation.
- `_load_mapped_cusips_for_symbol` and `_load_mapped_cusips_for_issuer` so current OpenFIGI `mapped` rows are searched before the legacy table.

For reverse lookup, union current provider mappings with legacy mappings, dedupe CUSIPs in Python, and retain the current limit.

- [ ] **Step 5: Verify loader/service GREEN and commit**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py
.venv/bin/python -m py_compile finance/loaders/institutional_13f.py app/services/institutional_portfolios.py
git diff --check
git add finance/loaders/institutional_13f.py tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py
git commit -m "OpenFIGI 13F 매핑을 조회 경로에 연결"
```

Expected: full Institutional Portfolios focused suite PASS; ambiguous rows still do not expose price actions.

---

### Task 4: Explicit Ingestion Action For Repeatable Mapping Backfill

**Files:**
- Modify: `app/jobs/ingestion_jobs.py`
- Modify: `app/web/ingestion/dispatcher.py`
- Modify: `app/web/ingestion/registry.py`
- Modify: `app/web/ingestion/guides.py`
- Modify: `app/web/ingestion/sections.py`
- Modify: `tests/test_institutional_13f_mapping.py`
- Modify: `tests/test_institutional_portfolios.py`

**Interfaces:**
- Produces job: `run_collect_sec_13f_identifier_mappings(...) -> JobResult`
- Produces action id: `collect_sec_13f_identifier_mappings`
- Consumes: service `INSTITUTIONAL_MANAGER_WATCHLIST` only inside the app job default-scope resolver; finance collector itself receives explicit CIKs.

- [ ] **Step 1: Write RED job/registry/dispatcher tests**

Test the job with a patched collector summary and explicit CIKs:

```python
def test_mapping_job_reports_provider_summary_without_secret(monkeypatch) -> None:
    monkeypatch.setattr(
        ingestion_jobs,
        "collect_and_store_openfigi_13f_mappings",
        lambda **kwargs: {
            "rows_written": 68,
            "identifiers_requested": 68,
            "mapped": 68,
            "ambiguous": 0,
            "unmapped": 0,
            "errors": 0,
            "api_key_used": True,
            "target_table": "finance_meta.institutional_13f_identifier_resolution",
        },
    )
    result = ingestion_jobs.run_collect_sec_13f_identifier_mappings(ciks=["0001536411"])
    assert result["status"] == "success"
    assert result["rows_written"] == 68
    assert "api_key" not in json.dumps(result).lower().replace("api_key_used", "")
```

Add registry/guide assertions and a dispatcher test that action parameters reach the new runner. Add a source-contract assertion that the existing SEC 13F expander contains a `13F ticker 연결 보강` button but no API-key text input and no new result diagnostics panel.

- [ ] **Step 2: Run RED for the action**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py -k 'mapping_job or identifier_mapping_action or ingestion_registry'
```

Expected: FAIL because action/job definitions are missing.

- [ ] **Step 3: Implement the job wrapper**

Add the collector import and runner:

```python
def run_collect_sec_13f_identifier_mappings(
    ciks: str | Iterable[str] | None = None,
    *,
    refresh_existing: bool = False,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_sec_13f_identifier_mappings"
    started_at = _now_str()
    t0 = perf_counter()
    if ciks is None:
        from app.services.institutional_portfolios import INSTITUTIONAL_MANAGER_WATCHLIST
        selected_ciks = [str(row["cik"]) for row in INSTITUTIONAL_MANAGER_WATCHLIST]
    else:
        selected_ciks = [str(value).strip() for value in ([ciks] if isinstance(ciks, str) else ciks) if str(value).strip()]
    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="sec_13f_identifier_mapping")
        summary = collect_and_store_openfigi_13f_mappings(
            ciks=selected_ciks,
            refresh_existing=refresh_existing,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="sec_13f_identifier_mapping")
        status = "failed" if int(summary.get("errors") or 0) and not int(summary.get("mapped") or 0) else (
            "partial_success" if int(summary.get("errors") or 0) or int(summary.get("ambiguous") or 0) else "success"
        )
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=perf_counter() - t0,
            rows_written=int(summary.get("rows_written") or 0),
            symbols_requested=int(summary.get("identifiers_requested") or 0),
            symbols_processed=int(summary.get("mapped") or 0),
            failed_symbols=[],
            message="SEC 13F ticker identity enrichment completed.",
            details=summary,
        )
    except Exception as exc:
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(selected_ciks),
            symbols_processed=0,
            failed_symbols=[],
            message=f"SEC 13F ticker identity enrichment failed: {exc}",
            details={"target_table": "finance_meta.institutional_13f_identifier_resolution"},
        )
```

- [ ] **Step 4: Register and expose one action inside the existing SEC 13F expander**

Add registry/guide/dispatcher entries for `collect_sec_13f_identifier_mappings`. In `sections.py`, under the existing dataset collection result, add a caption explaining that it maps stored latest holdings and a button labeled `13F ticker 연결 보강`. Schedule the new action with `refresh_existing=False`; use the same existing inline completed-result component. Do not add an API-key input—the environment variable is the only UI-runtime key path.

- [ ] **Step 5: Verify Task 4 GREEN and commit**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py
.venv/bin/python -m py_compile app/jobs/ingestion_jobs.py app/web/ingestion/dispatcher.py app/web/ingestion/registry.py app/web/ingestion/guides.py app/web/ingestion/sections.py
git diff --check
git add app/jobs/ingestion_jobs.py app/web/ingestion/dispatcher.py app/web/ingestion/registry.py app/web/ingestion/guides.py app/web/ingestion/sections.py tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py
git commit -m "13F 티커 연결 보강 작업 추가"
```

Expected: action contracts PASS and no secret field is rendered.

---

### Task 5: Actual Backfill, Browser QA, Durable Documentation And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/data/README.md`
- Modify: `.aiworkspace/note/finance/docs/data/TABLE_SEMANTICS.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/DATA_DB_PIPELINE_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Generate only: `institutional-13f-openfigi-mapping-qa.png`

**Interfaces:**
- Consumes all prior tasks.
- Produces actual DB resolution rows and final documented roadmap state.

- [ ] **Step 1: Capture actual before-state**

Run read-only SQL for Berkshire, Bridgewater, and Duquesne through the existing loader/service path and append total/mapped/unmapped/mapped-weight to task `RUNS.md`. Duquesne expected baseline is 70 total, 5 mapped, 65 unmapped, 6.6579% mapped weight.

- [ ] **Step 2: Run schema sync and curated-manager backfill without exposing credentials**

Run the job in an exec session that can be polled because anonymous pacing may take several minutes:

```bash
.venv/bin/python - <<'PY'
from app.jobs.ingestion_jobs import run_collect_sec_13f_identifier_mappings
print(run_collect_sec_13f_identifier_mappings())
PY
```

Expected: nonzero `identifiers_requested`, `rows_written`, and `mapped`; target table `finance_meta.institutional_13f_identifier_resolution`. Never print `OPENFIGI_API_KEY`.

- [ ] **Step 3: Verify actual DB safety and coverage**

Run assertions through the public loader/service path:

```python
assert duquesne_payload["coverage"]["holding_count_total"] == 70
assert duquesne_payload["coverage"]["holding_count_mapped"] > 5
assert duquesne_payload["coverage"]["mapped_weight_pct"] > 6.6579
assert by_cusip["632307104"]["symbol"] == "NTRA"
assert by_cusip["457669307"]["symbol"] == "INSM"
assert by_cusip["874039100"]["symbol"] == "TSM"
assert by_cusip["N62509109"]["symbol"] == "NAMS"
```

Also query the three known unsafe legacy examples and assert the current provider resolution, not legacy `AUR`/`AWI`/`AVGO`, owns the read model.

- [ ] **Step 4: Run complete verification**

Run:

```bash
.venv/bin/python -m pytest -q tests/test_institutional_13f_mapping.py tests/test_institutional_portfolios.py
.venv/bin/python -m py_compile finance/data/institutional_13f_mapping.py finance/loaders/institutional_13f.py finance/data/institutional_13f.py app/jobs/ingestion_jobs.py
git diff --check
git status --short
```

Then run the broader relevant service contract suite if the focused suite passes. Record any pre-existing unrelated failure separately; do not call it fixed.

- [ ] **Step 5: Perform Browser QA and save one generated screenshot**

Open the actual local Streamlit Institutional Portfolios page, select Stanley Druckenmiller/Duquesne, and verify:

- coverage metrics reflect the new DB mapping.
- Natera, Insmed, TSM, EWZ/RSP, YPF, Sea, STM, and Teva rows show `ticker 연결됨`.
- clicking a mapped row opens security detail; price action is available or clearly `price_missing`, not `symbol_missing`.
- any true ambiguous/unmapped row still shows issuer/CUSIP notice and no price action.
- no page-level horizontal overflow or console error.

Save `institutional-13f-openfigi-mapping-qa.png` as generated/local artifact and do not stage it.

- [ ] **Step 6: Synchronize durable docs**

Use `finance-doc-sync` and document:

- new canonical resolution table semantics.
- OpenFIGI v3 source, free optional-key boundary, and current-state—not PIT-history—meaning.
- loader precedence and legacy exact-name fallback.
- explicit ingestion action and UI render no-fetch boundary.
- actual before/after coverage.
- roadmap completion `4/4` and deferred all-latest-manager 31k expansion.

- [ ] **Step 7: Final verification and closeout commit**

Run:

```bash
rg -n "TBD|TODO|implement later|fill in details" .aiworkspace/note/finance/tasks/active/institutional-13f-openfigi-mapping-v1-20260718 || true
git diff --check
git status --short
git add .aiworkspace/note/finance/docs .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md .aiworkspace/note/finance/tasks/active/institutional-13f-openfigi-mapping-v1-20260718
git commit -m "기관 13F 티커 매핑 문서 정렬"
```

Expected: generated screenshot remains untracked, task status reports `4/4`, tests and Browser QA evidence are recorded, and the branch contains coherent implementation commits.
