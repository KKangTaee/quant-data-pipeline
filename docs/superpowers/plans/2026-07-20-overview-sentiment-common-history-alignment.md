# Overview Sentiment Common History Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AAII 공식 workbook 장기 이력을 canonical DB에 보강하고, Overview 심리의 CNN·AAII 두 그래프가 `6M / 1Y / 공통 전체`마다 두 source 이력의 교집합만 같은 x축으로 보여주게 한다.

**Architecture:** AAII ingestion은 공식 `sentiment.xls`를 primary source로 정규화하되 일상 PIT capture에는 최신 26주만 넣고, 전체 backfill은 별도 함수가 canonical table만 transaction으로 교체한다. 서비스는 CNN과 AAII canonical coverage의 교집합을 `history_coverage.common`으로 계산하고, React는 이 범위에서 선택 기간을 계산해 두 그래프와 AAII 두 탭에 동일한 `TimeExtent`를 전달한다.

**Tech Stack:** Python 3, pandas, BeautifulSoup, PyMySQL, unittest, Streamlit, React, TypeScript, SVG, npm/Vite

## Global Constraints

- 3차 독립 데이터 후보 검토와 1W/1M 예측은 시작하지 않는다.
- CNN / AAII 외 새 심리 지표를 추가하지 않는다.
- AAII `observation_date`는 workbook 공식 `Reported Date`를 사용한다.
- 일상 AAII PIT capture에는 workbook 최신 26주만 저장한다.
- historical backfill은 canonical history만 갱신하며 immutable PIT를 소급 생성하지 않는다.
- workbook 최신일 이후 prospective AAII canonical row는 삭제하지 않는다.
- common start는 `max(CNN start, AAII start)`, common end는 `min(CNN end, AAII end)`다.
- CNN이 더 오래된 값을 제공하지 못하면 AAII 단독 과거 구간은 비교 그래프에 노출하지 않는다.
- 선, tooltip, 상단 최신값·날짜 모두 공통 범위 밖 값을 노출하지 않는다.
- AAII 빈 일간 날짜를 보간하거나 한쪽 선을 coverage 밖으로 연장하지 않는다.
- AAII 응답과 Spread 탭은 같은 common domain을 공유한다.
- desktop/420px Browser QA와 untracked screenshot 1장을 남긴다.

---

## File Map

- `finance/data/sentiment.py`: workbook parser/fetcher, 최신 26주 daily view, HTML fallback 날짜 정규화, explicit backfill entry point.
- `finance/data/sentiment_store.py`: 네 AAII canonical series 날짜 집합 검증과 원자적 교체.
- `tests/test_sentiment_pit.py`: parser, bounded fetch, fallback, transaction, rollback tests.
- `app/services/overview/sentiment.py`: source별 coverage에서 common intersection 계산.
- `app/web/overview/sentiment_helpers.py`: `history_coverage.common` 직렬화.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`: common coverage와 `TimeExtent` type.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`: shared period/domain, filtering, latest header, copy.
- `app/web/streamlit_components/sentiment_workbench/src/style.css`: 420px coverage wrapping.
- `tests/test_service_contracts.py`: service/payload/React source contracts.
- `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1/{STATUS,RUNS,RISKS}.md`: 2차 보정 근거.
- `.aiworkspace/note/finance/{WORK_PROGRESS,QUESTION_AND_ANALYSIS_LOG}.md`: compact root handoff.

---

### Task 1: AAII 공식 workbook 정규화와 bounded daily fetch

**Files:**
- Modify: `finance/data/sentiment.py`
- Test: `tests/test_sentiment_pit.py`

**Interfaces:**
- Consumes: `_sentiment_row(...)`, `_fetch_bytes(...)`, `AAII_SERIES`, 기존 HTML parser.
- Produces: `AAII_SENTIMENT_HISTORY_URL`, `parse_aaii_sentiment_frame(...)`, `parse_aaii_sentiment_rows_from_workbook(...)`, `fetch_aaii_sentiment_history_rows(...)`, 최신 26주 `fetch_aaii_sentiment_rows(...)`.

- [ ] **Step 1: workbook fraction/spread/provenance failing test를 작성한다**

```python
from datetime import date, timedelta
import pandas as pd

class SentimentAaiiWorkbookTests(unittest.TestCase):
    def test_workbook_frame_normalizes_four_series_per_complete_week(self) -> None:
        from finance.data.sentiment import parse_aaii_sentiment_frame
        frame = pd.DataFrame({
            "Reported Date": [pd.Timestamp("1987-07-24"), pd.Timestamp("2026-07-16")],
            "Bullish": [0.35, 0.449074],
            "Neutral": [0.30, 0.222222],
            "Bearish": [0.35, 0.328704],
        })
        rows = parse_aaii_sentiment_frame(
            frame, collected_at="2026-07-20 09:00:00",
            source_mode="xls", source_ref="https://www.aaii.com/files/surveys/sentiment.xls",
        )
        self.assertEqual(len(rows), 8)
        latest = {row["series_id"]: row for row in rows if row["observation_date"] == "2026-07-16"}
        self.assertAlmostEqual(latest["AAII_BULLISH"]["value"], 44.9074, places=4)
        self.assertAlmostEqual(latest["AAII_BULL_BEAR_SPREAD"]["value"], 12.037, places=3)
        self.assertIn('"reported_date": "2026-07-16"', latest["AAII_BULLISH"]["missing_fields_json"])

    def test_workbook_frame_skips_incomplete_week(self) -> None:
        from finance.data.sentiment import parse_aaii_sentiment_frame
        frame = pd.DataFrame({
            "Reported Date": [pd.Timestamp("2026-07-09"), pd.Timestamp("2026-07-16")],
            "Bullish": [0.40, 0.44], "Neutral": [0.25, None], "Bearish": [0.35, 0.33],
        })
        rows = parse_aaii_sentiment_frame(
            frame, collected_at="2026-07-20 09:00:00", source_mode="xls", source_ref="xls",
        )
        self.assertEqual({row["observation_date"] for row in rows}, {"2026-07-09"})
        self.assertEqual(len(rows), 4)
```

- [ ] **Step 2: parser test가 `ImportError`로 실패하는지 확인한다**

Run: `.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentAaiiWorkbookTests -v`

Expected: `parse_aaii_sentiment_frame` 부재로 FAIL.

- [ ] **Step 3: DataFrame parser와 workbook wrapper를 구현한다**

```python
from io import BytesIO
from datetime import date, datetime, timedelta, timezone

AAII_SENTIMENT_HISTORY_URL = "https://www.aaii.com/files/surveys/sentiment.xls"
AAII_DAILY_CAPTURE_WEEKS = 26

def parse_aaii_sentiment_frame(
    frame: pd.DataFrame, *, collected_at: str, source_mode: str, source_ref: str,
) -> list[dict[str, Any]]:
    required = ["Reported Date", "Bullish", "Neutral", "Bearish"]
    if not set(required).issubset(frame.columns):
        raise RuntimeError(f"AAII workbook is missing required columns: {required}")
    normalized = frame[required].copy()
    normalized["Reported Date"] = pd.to_datetime(normalized["Reported Date"], errors="coerce")
    for column in required[1:]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    normalized = normalized.dropna(subset=required).sort_values("Reported Date")
    rows: list[dict[str, Any]] = []
    for item in normalized.to_dict("records"):
        observed = pd.Timestamp(item["Reported Date"]).strftime("%Y-%m-%d")
        bullish, neutral, bearish = (
            round(float(item[name]) * 100.0, 4) for name in required[1:]
        )
        values = {"bullish": bullish, "neutral": neutral, "bearish": bearish,
                  "spread": round(bullish - bearish, 4)}
        metadata = {"reported_date": observed,
                    "bullish_fraction": float(item["Bullish"]),
                    "neutral_fraction": float(item["Neutral"]),
                    "bearish_fraction": float(item["Bearish"])}
        for key, value in values.items():
            series_id, series_name, units = AAII_SERIES[key]
            rows.append(_sentiment_row(
                series_id, observation_date=observed, source="aaii_sentiment_survey",
                source_mode=source_mode, source_ref=source_ref, series_name=series_name,
                category="sentiment_survey", units=units, value=value,
                collected_at=collected_at, metadata=metadata,
            ))
    return rows

def parse_aaii_sentiment_rows_from_workbook(
    data: bytes, *, collected_at: str | None = None,
) -> list[dict[str, Any]]:
    frame = pd.read_excel(BytesIO(data), sheet_name="SENTIMENT", header=3)
    return parse_aaii_sentiment_frame(
        frame, collected_at=collected_at or _utc_now_string(),
        source_mode="xls", source_ref=AAII_SENTIMENT_HISTORY_URL,
    )
```

- [ ] **Step 4: parser tests를 통과시킨다**

Run: Step 2 command. Expected: 2 tests `OK`.

- [ ] **Step 5: bounded primary와 HTML fallback date failing tests를 추가한다**

```python
    def test_daily_fetch_keeps_latest_26_complete_weeks(self) -> None:
        from finance.data import sentiment
        rows = []
        for offset in range(30):
            observed = date(2026, 1, 1) + timedelta(days=7 * offset)
            for series_id in ("AAII_BULLISH", "AAII_NEUTRAL", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD"):
                rows.append({"series_id": series_id, "observation_date": observed.isoformat()})
        with patch.object(sentiment, "fetch_aaii_sentiment_history_rows", return_value=rows):
            recent = sentiment.fetch_aaii_sentiment_rows()
        self.assertEqual(len(recent), 104)
        self.assertEqual(min(row["observation_date"] for row in recent), "2026-01-29")

    def test_daily_fetch_falls_back_to_html_and_anchors_wednesday_on_thursday(self) -> None:
        from finance.data import sentiment
        html = b"""<table><tr><th>Reported Date</th><th>Bullish</th><th>Neutral</th><th>Bearish</th></tr>
        <tr><td>Jul 15</td><td>44.9%</td><td>22.2%</td><td>32.9%</td></tr></table>"""
        with (patch.object(sentiment, "fetch_aaii_sentiment_history_rows", side_effect=RuntimeError("blocked")),
              patch.object(sentiment, "_fetch_bytes", return_value=html)):
            rows = sentiment.fetch_aaii_sentiment_rows(today=date(2026, 7, 20))
        self.assertEqual({row["observation_date"] for row in rows}, {"2026-07-16"})
        self.assertTrue(all('"reported_date_raw": "Jul 15"' in row["missing_fields_json"] for row in rows))
```

- [ ] **Step 6: 새 fetch tests가 함수/동작 차이로 실패하는지 확인한다**

Run: Step 2 command. Expected: history fetcher 부재 또는 date/count assertion으로 FAIL.

- [ ] **Step 7: full fetcher, limiter, fallback을 구현한다**

HTML parser에서 parsed Wednesday에 `timedelta(days=1)`을 적용하고 metadata에 `reported_date_raw`를 둔다. fetch 함수는 아래 경계를 따른다.

```python
def fetch_aaii_sentiment_history_rows(*, timeout=DEFAULT_TIMEOUT, retries=DEFAULT_RETRIES, fetcher=None):
    data = _fetch_bytes(
        AAII_SENTIMENT_HISTORY_URL,
        headers={"User-Agent": DEFAULT_USER_AGENT,
                 "Accept": "application/vnd.ms-excel,application/octet-stream,*/*",
                 "Referer": AAII_SENTIMENT_URL},
        timeout=timeout, retries=retries, fetcher=fetcher,
    )
    rows = parse_aaii_sentiment_rows_from_workbook(data)
    if not rows:
        raise RuntimeError("AAII official workbook contained no complete observations")
    return rows

def _latest_aaii_weeks(rows: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    dates = sorted({str(row["observation_date"]) for row in rows if row.get("observation_date")})
    allowed = set(dates[-max(int(count), 1):])
    return [row for row in rows if str(row.get("observation_date")) in allowed]
```

`fetch_aaii_sentiment_rows`는 먼저 `fetch_aaii_sentiment_history_rows`를 호출해 `_latest_aaii_weeks(..., 26)`을 반환한다. workbook exception을 log한 뒤에만 기존 HTML `_fetch_bytes`와 parser를 호출하고 동일 limiter를 적용한다. HTML도 없거나 anti-bot이면 기존 RuntimeError 계약을 유지한다.

- [ ] **Step 8: parser/collector regression을 통과시킨다**

Run:

```bash
.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentAaiiWorkbookTests -v
.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentPitCollectorTests -v
```

Expected: 모두 `OK`.

- [ ] **Step 9: Task 1을 commit한다**

```bash
git add finance/data/sentiment.py tests/test_sentiment_pit.py
git commit -m "AAII 공식 장기 이력 수집 경로 추가"
```

---

### Task 2: AAII canonical full-history 원자적 backfill

**Files:**
- Modify: `finance/data/sentiment_store.py`
- Modify: `finance/data/sentiment.py`
- Test: `tests/test_sentiment_pit.py`

**Interfaces:**
- Consumes: Task 1의 `fetch_aaii_sentiment_history_rows(...)`, `deduplicate_sentiment_rows(...)`, `_upsert_canonical_rows(...)`.
- Produces: `replace_aaii_canonical_history(db, rows) -> dict[str, Any]`, `backfill_aaii_sentiment_history(...) -> dict[str, Any]`.

- [ ] **Step 1: aligned series, scoped delete, rollback failing tests를 작성한다**

`FakeTransactionDb.execute`에서 `DELETE FROM macro_series_observation`을 `delete` event로 기록하고 params를 `deleted_params`에 보존한다. `executemany`에는 `fail_canonical`일 때 `RuntimeError("canonical write failed")`를 내는 hook을 추가한다.

```python
def aaii_week_rows(observation_date: str) -> list[dict]:
    values = {"AAII_BULLISH": 44.9, "AAII_NEUTRAL": 22.2,
              "AAII_BEARISH": 32.9, "AAII_BULL_BEAR_SPREAD": 12.0}
    return [{**sentiment_row(value), "series_id": series_id,
             "observation_date": observation_date, "source": "aaii_sentiment_survey",
             "source_mode": "xls"} for series_id, value in values.items()]

class SentimentAaiiBackfillTests(unittest.TestCase):
    def test_canonical_backfill_deletes_only_through_workbook_latest_then_upserts(self) -> None:
        from finance.data.sentiment_store import replace_aaii_canonical_history
        db = FakeTransactionDb()
        result = replace_aaii_canonical_history(
            db, aaii_week_rows("1987-07-24") + aaii_week_rows("2026-07-16"))
        self.assertEqual(db.events, ["begin", "delete", "canonical", "commit"])
        self.assertEqual(db.deleted_params["latest_date"], "2026-07-16")
        self.assertEqual(result["week_count"], 2)
        self.assertEqual(result["canonical_rows_written"], 8)

    def test_canonical_backfill_rejects_misaligned_series_before_transaction(self) -> None:
        from finance.data.sentiment_store import replace_aaii_canonical_history
        db = FakeTransactionDb()
        with self.assertRaisesRegex(RuntimeError, "aligned dates"):
            replace_aaii_canonical_history(db, aaii_week_rows("2026-07-16")[:-1])
        self.assertEqual(db.events, [])

    def test_canonical_backfill_rolls_back_when_upsert_fails(self) -> None:
        from finance.data.sentiment_store import replace_aaii_canonical_history
        db = FakeTransactionDb()
        db.fail_canonical = True
        with self.assertRaisesRegex(RuntimeError, "canonical write failed"):
            replace_aaii_canonical_history(db, aaii_week_rows("2026-07-16"))
        self.assertEqual(db.events, ["begin", "delete", "rollback"])
```

- [ ] **Step 2: transaction tests가 import failure인지 확인한다**

Run: `.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentAaiiBackfillTests -v`

Expected: `replace_aaii_canonical_history` 부재로 FAIL.

- [ ] **Step 3: validation-first canonical replacement를 구현한다**

```python
AAII_CANONICAL_SERIES = {
    "AAII_BULLISH", "AAII_NEUTRAL", "AAII_BEARISH", "AAII_BULL_BEAR_SPREAD",
}

def replace_aaii_canonical_history(db: MySQLClient, rows: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = deduplicate_sentiment_rows(rows)
    dates_by_series = {series_id: set() for series_id in AAII_CANONICAL_SERIES}
    for row in normalized:
        series_id = str(row.get("series_id") or "").upper()
        if row.get("source") != "aaii_sentiment_survey" or series_id not in AAII_CANONICAL_SERIES:
            raise RuntimeError("AAII canonical backfill contains an unexpected source or series")
        dates_by_series[series_id].add(str(row.get("observation_date") or ""))
    date_sets = list(dates_by_series.values())
    if not date_sets[0] or any(item != date_sets[0] for item in date_sets[1:]):
        raise RuntimeError("AAII canonical backfill requires four series with aligned dates")
    dates = sorted(date_sets[0])
    db.begin()
    try:
        db.execute(f"""
            DELETE FROM {MACRO_TABLE}
            WHERE source = %(source)s
              AND series_id IN ('AAII_BULLISH', 'AAII_NEUTRAL', 'AAII_BEARISH', 'AAII_BULL_BEAR_SPREAD')
              AND observation_date <= %(latest_date)s
        """, {"source": "aaii_sentiment_survey", "latest_date": dates[-1]})
        _upsert_canonical_rows(db, normalized)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"canonical_rows_written": len(normalized), "observation_start": dates[0],
            "observation_end": dates[-1], "week_count": len(dates)}
```

- [ ] **Step 4: transaction tests를 통과시킨다**

Run: Step 2 command. Expected: 3 tests `OK`.

- [ ] **Step 5: explicit orchestration failing test를 추가한다**

```python
    def test_backfill_fetches_before_db_and_never_writes_snapshot(self) -> None:
        from finance.data import sentiment
        rows, db = aaii_week_rows("2026-07-16"), MagicMock()
        with (patch.object(sentiment, "fetch_aaii_sentiment_history_rows", return_value=rows) as fetch,
              patch.object(sentiment, "MySQLClient", return_value=db),
              patch.object(sentiment, "ensure_market_sentiment_schema") as ensure,
              patch.object(sentiment, "replace_aaii_canonical_history",
                           return_value={"canonical_rows_written": 4}) as replace):
            result = sentiment.backfill_aaii_sentiment_history()
        fetch.assert_called_once()
        ensure.assert_called_once_with(db)
        replace.assert_called_once_with(db, rows)
        db.close.assert_called_once_with()
        self.assertNotIn("snapshot_rows_written", result)
```

- [ ] **Step 6: orchestration test가 함수 부재로 실패하는지 확인한다**

Run: `.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentAaiiBackfillTests.test_backfill_fetches_before_db_and_never_writes_snapshot -v`

Expected: `backfill_aaii_sentiment_history` 부재로 FAIL.

- [ ] **Step 7: fetch 완료 후 DB를 열어 canonical만 교체하는 entry point를 구현한다**

```python
def backfill_aaii_sentiment_history(
    *, timeout=DEFAULT_TIMEOUT, retries=DEFAULT_RETRIES,
    host="localhost", user="root", password="1234", port=3306,
) -> dict[str, Any]:
    rows = fetch_aaii_sentiment_history_rows(timeout=timeout, retries=retries)
    db = MySQLClient(host, user, password, port)
    try:
        ensure_market_sentiment_schema(db)
        return replace_aaii_canonical_history(db, rows)
    finally:
        db.close()
```

- [ ] **Step 8: persistence/backfill regression을 통과시킨다**

Run:

```bash
.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentPitPersistenceTests -v
.venv/bin/python -m unittest tests.test_sentiment_pit.SentimentAaiiBackfillTests -v
```

Expected: 모두 `OK`; immutable snapshot write 호출 없음.

- [ ] **Step 9: Task 2를 commit한다**

```bash
git add finance/data/sentiment.py finance/data/sentiment_store.py tests/test_sentiment_pit.py
git commit -m "AAII canonical 장기 이력 원자적 보강 추가"
```

---

### Task 3: 서비스와 payload에 canonical 교집합 명시

**Files:**
- Modify: `app/services/overview/sentiment.py`
- Modify: `app/web/overview/sentiment_helpers.py`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: `_history_source_coverage(...)`의 `canonical_start`, `canonical_end`.
- Produces: `_common_history_coverage(cnn, aaii)`, `history_coverage.common`.

- [ ] **Step 1: intersection/no-overlap failing test를 작성한다**

```python
def test_sentiment_common_history_coverage_uses_only_source_intersection(self) -> None:
    from app.services.overview.sentiment import _common_history_coverage
    self.assertEqual(_common_history_coverage(
        {"canonical_start": "2025-06-04", "canonical_end": "2026-07-20"},
        {"canonical_start": "1987-07-24", "canonical_end": "2026-07-16"},
    ), {"canonical_start": "2025-06-04", "canonical_end": "2026-07-16", "available": True})
    self.assertEqual(_common_history_coverage(
        {"canonical_start": "2026-08-01", "canonical_end": "2026-08-02"},
        {"canonical_start": "2026-07-01", "canonical_end": "2026-07-16"},
    ), {"canonical_start": None, "canonical_end": None, "available": False})
```

- [ ] **Step 2: helper import failure를 확인한다**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_sentiment_common_history_coverage_uses_only_source_intersection -v`

Expected: `ImportError`로 FAIL.

- [ ] **Step 3: service helper와 snapshot common field를 구현한다**

```python
def _common_history_coverage(cnn: dict[str, Any], aaii: dict[str, Any]) -> dict[str, Any]:
    starts = [pd.to_datetime(item.get("canonical_start"), errors="coerce") for item in (cnn, aaii)]
    ends = [pd.to_datetime(item.get("canonical_end"), errors="coerce") for item in (cnn, aaii)]
    if any(pd.isna(value) for value in [*starts, *ends]):
        return {"canonical_start": None, "canonical_end": None, "available": False}
    common_start, common_end = max(starts), min(ends)
    if common_start > common_end:
        return {"canonical_start": None, "canonical_end": None, "available": False}
    return {"canonical_start": common_start.strftime("%Y-%m-%d"),
            "canonical_end": common_end.strftime("%Y-%m-%d"), "available": True}
```

`build_market_sentiment_snapshot`에서 `cnn_history_coverage`와 `aaii_history_coverage`를 한 번씩 계산한 뒤 다음을 반환한다.

```python
"history_coverage": {
    "common": _common_history_coverage(cnn_history_coverage, aaii_history_coverage),
    "cnn": cnn_history_coverage,
    "aaii": aaii_history_coverage,
    "cnn_components_note": "수집 시작 이후 현재값을 축적 중",
},
```

- [ ] **Step 4: service unit test를 통과시킨다**

Run: Step 2 command. Expected: test `OK`.

- [ ] **Step 5: snapshot/payload common assertion을 추가해 직렬화 부재를 확인한다**

기존 full-history service test fixture에 `AAII_BULL_BEAR_SPREAD`의 `1987-07-24`, `2026-07-16` 두 row를 넣고 다음을 assert한다.

```python
self.assertEqual(snapshot["history_coverage"]["common"], {
    "canonical_start": "2025-06-04", "canonical_end": "2026-07-16", "available": True,
})
self.assertEqual(payload["history_coverage"]["common"], {
    "canonical_start": "2025-06-04", "canonical_end": "2026-07-16", "available": True,
})
```

Run: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields -v`

Expected: payload의 `common` 부재 assertion으로 FAIL.

- [ ] **Step 6: helper payload에 common coverage를 직렬화한다**

```python
common_source = dict(coverage_source.get("common") or {})
common_history_coverage = {
    "canonical_start": _display_text(common_source.get("canonical_start"), ""),
    "canonical_end": _display_text(common_source.get("canonical_end"), ""),
    "available": bool(common_source.get("available")),
}
```

기존 payload `history_coverage`에 `"common": common_history_coverage`를 추가하고 `periods`는 `['6M', '1Y', 'ALL']` 그대로 둔다.

- [ ] **Step 7: service/helper regression을 통과시킨다**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests -v
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields -v
```

Expected: 모두 `OK`; 1W/1M outlook assertions는 계속 `UNAVAILABLE`.

- [ ] **Step 8: Task 3을 commit한다**

```bash
git add app/services/overview/sentiment.py app/web/overview/sentiment_helpers.py tests/test_service_contracts.py
git commit -m "심리 그래프 공통 이력 교집합 계약 추가"
```

---

### Task 4: React 두 그래프에 동일한 교집합 x-domain 적용

**Files:**
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css`
- Test: `tests/test_service_contracts.py`

**Interfaces:**
- Consumes: Task 3의 `coverage.common.{canonical_start,canonical_end,available}`.
- Produces: `TimeExtent`, `buildCommonPeriodExtent(...)`, `filterChartPanel(panel, extent)`, shared-extent `SentimentLineChart`.

- [ ] **Step 1: shared extent source-contract failing test로 기존 shared-period test를 교체한다**

```python
def test_sentiment_history_uses_one_shared_intersection_domain_for_both_panels(self) -> None:
    root = Path("app/web/streamlit_components/sentiment_workbench/src")
    types = (root / "SentimentWorkbench.tsx").read_text(encoding="utf-8")
    history = (root / "SentimentHistorySection.tsx").read_text(encoding="utf-8")
    style = (root / "style.css").read_text(encoding="utf-8")
    self.assertIn("export type TimeExtent", types)
    self.assertIn("common: CommonHistoryCoverage", types)
    self.assertIn("export function buildCommonPeriodExtent", history)
    self.assertIn("const selectedExtent = buildCommonPeriodExtent(coverage, period)", history)
    for key in ("cnn", "aaii_responses", "aaii_spread"):
        self.assertIn(f"filterChartPanel(charts.{key}, selectedExtent)", history)
    self.assertEqual(history.count("extent={selectedExtent}"), 2)
    self.assertIn('key === "ALL" ? "공통 전체" : key', history)
    self.assertIn("비교 구간", history)
    self.assertNotIn("anchorTimestamp", history)
    self.assertIn("sentiment-workbench__history-coverage", style)
```

- [ ] **Step 2: existing independent-domain source가 test를 실패시키는지 확인한다**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_history_uses_one_shared_intersection_domain_for_both_panels -v`

Expected: `TimeExtent`, `common`, `extent={selectedExtent}` assertions로 FAIL.

- [ ] **Step 3: TypeScript payload type을 확장한다**

```typescript
export type TimeExtent = { min: number; max: number };
export type CommonHistoryCoverage = {
  canonical_start: string;
  canonical_end: string;
  available: boolean;
};
export type HistoryCoverage = {
  default_period: HistoryPeriod;
  periods: HistoryPeriod[];
  common: CommonHistoryCoverage;
  cnn: SourceHistoryCoverage;
  aaii: SourceHistoryCoverage;
  cnn_components_note: string;
};
```

- [ ] **Step 4: common period extent와 range filter를 구현한다**

```typescript
function subtractUtcMonths(timestamp: number, months: number) {
  const value = new Date(timestamp);
  const day = value.getUTCDate();
  value.setUTCHours(0, 0, 0, 0);
  value.setUTCDate(1);
  value.setUTCMonth(value.getUTCMonth() - months);
  const lastDay = new Date(Date.UTC(value.getUTCFullYear(), value.getUTCMonth() + 1, 0)).getUTCDate();
  value.setUTCDate(Math.min(day, lastDay));
  return value.getTime();
}

export function buildCommonPeriodExtent(
  coverage: HistoryCoverage, period: HistoryPeriod,
): TimeExtent | null {
  if (!coverage.common.available) return null;
  const commonStart = Date.parse(coverage.common.canonical_start);
  const commonEnd = Date.parse(coverage.common.canonical_end);
  if (!Number.isFinite(commonStart) || !Number.isFinite(commonEnd) || commonStart > commonEnd) return null;
  const requested = period === "ALL" ? commonStart
    : subtractUtcMonths(commonEnd, period === "6M" ? 6 : 12);
  return { min: Math.max(commonStart, requested), max: commonEnd };
}

function pointWithinExtent(point: ChartPoint, extent: TimeExtent) {
  const timestamp = Date.parse(point.date);
  return Number.isFinite(timestamp) && timestamp >= extent.min && timestamp <= extent.max;
}

function latestWithinExtent(panel: ChartPanel, series: ChartPoint[], extent: TimeExtent) {
  const timestamp = Date.parse(panel.latest?.date || "");
  if (Number.isFinite(timestamp) && timestamp >= extent.min && timestamp <= extent.max) return panel.latest;
  if (new Set(series.map((point) => point.series)).size !== 1 || !series.length) return undefined;
  const point = [...series].sort((a, b) => Date.parse(a.date) - Date.parse(b.date)).at(-1);
  return point ? {date: point.date, value: point.value,
                  label: point.status_label || "공통 구간 최신"} : undefined;
}

export function filterChartPanel(panel: ChartPanel, extent: TimeExtent | null): ChartPanel {
  if (!extent) return {...panel, latest: undefined, series: []};
  const series = panel.series.filter((point) => pointWithinExtent(point, extent));
  return {...panel, latest: latestWithinExtent(panel, series, extent), series};
}
```

이 latest 규칙으로 CNN current가 AAII common end보다 늦어도 chart header에서 공통 구간 마지막 CNN 관측만 보인다. 다중 series인 AAII 응답은 원래 latest가 범위 밖이면 header를 숨긴다.

- [ ] **Step 5: chart 내부의 independent `chartExtent(points)`를 prop extent로 교체한다**

```typescript
function SentimentLineChart({panel, mode, extent}: {
  panel: ChartPanel; mode: ChartMode; extent: TimeExtent | null;
}) {
  const points = parsedChartPoints(panel);
  const chartTimeExtent = extent || {min: 0, max: 1};
  const dateTicks = buildDateTicks(chartTimeExtent);
```

hover target, tick, polyline, latest dot의 모든 `xForTimestamp(..., extent)`를 `chartTimeExtent`로 바꾼다. `targetTimestamp`도 `chartTimeExtent.min/max`로 계산한다. y-domain은 panel 값 기준 기존 동작을 유지한다.

- [ ] **Step 6: section에서 independent anchor를 제거하고 동일 extent를 두 chart에 준다**

```typescript
const selectedExtent = buildCommonPeriodExtent(coverage, period);
const visibleCharts = {
  cnn: filterChartPanel(charts.cnn, selectedExtent),
  aaii_responses: filterChartPanel(charts.aaii_responses, selectedExtent),
  aaii_spread: filterChartPanel(charts.aaii_spread, selectedExtent),
};
```

```tsx
{key === "ALL" ? "공통 전체" : key}
<strong>비교 구간 · {selectedExtent
  ? `${new Date(selectedExtent.min).toISOString().slice(0, 10)}~${new Date(selectedExtent.max).toISOString().slice(0, 10)}`
  : "공통 이력 없음"}</strong>
<span>{coverageLine("CNN 보유 이력", coverage.cnn)}</span>
<span>{coverageLine("AAII 보유 이력", coverage.aaii)}</span>
<SentimentLineChart extent={selectedExtent} mode="cnn" panel={visibleCharts.cnn} />
<SentimentLineChart extent={selectedExtent} mode={activeAaiiMode} panel={activeAaiiChart} />
```

- [ ] **Step 7: no-overlap/short-range empty state를 명확히 한다**

```tsx
{!extent ? (
  <p className="sentiment-workbench__empty">CNN과 AAII가 함께 존재하는 비교 기간이 없습니다.</p>
) : hasTrend ? (
  <div className="sentiment-workbench__line-chart-plot">{/* existing SVG and tooltip */}</div>
) : (
  <p className="sentiment-workbench__empty">공통 기간에 서로 다른 두 시점 이상의 관측이 필요합니다.</p>
)}
```

기존 source-contract의 empty copy assertion도 새 문구로 갱신한다.

- [ ] **Step 8: 420px coverage wrapping CSS를 추가한다**

```css
.sentiment-workbench__history-coverage strong,
.sentiment-workbench__history-coverage span,
.sentiment-workbench__history-coverage small {
  overflow-wrap: anywhere;
}
.sentiment-workbench__history-coverage strong {
  color: var(--sentiment-ink);
  font-weight: 750;
}
```

- [ ] **Step 9: source-contract와 frontend build를 통과시킨다**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests -v
npm run build --prefix app/web/streamlit_components/sentiment_workbench
```

Expected: tests `OK`, TypeScript/Vite build exit 0, 두 `SentimentLineChart` 호출의 extent가 동일.

- [ ] **Step 10: Task 4를 commit한다**

```bash
git status --short
git add app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx
git add app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx
git add app/web/streamlit_components/sentiment_workbench/src/style.css
git add app/web/streamlit_components/sentiment_workbench/frontend tests/test_service_contracts.py
git commit -m "심리 그래프를 공통기간 축으로 정렬"
```

`git status`에서 실제 generated bundle 경로를 확인해 그 경로만 stage하고 기존 screenshot, `.superpowers/`, research bundle은 stage하지 않는다.

---

### Task 5: 실제 AAII backfill, 교집합 QA, 문서 closeout

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated/untracked: `overview-sentiment-common-history-alignment-qa.png`

**Interfaces:**
- Consumes: `backfill_aaii_sentiment_history()`, common payload, shared domain UI.
- Produces: 실제 canonical history, 유지된 PIT 시작일 근거, desktop/420 QA, 2차 보정 기록.

- [ ] **Step 1: data mutation 전 focused verification을 통과시킨다**

```bash
.venv/bin/python -m unittest tests.test_sentiment_pit -v
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests -v
.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields -v
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests -v
.venv/bin/python -m py_compile finance/data/sentiment.py finance/data/sentiment_store.py
.venv/bin/python -m py_compile app/services/overview/sentiment.py app/web/overview/sentiment_helpers.py
npm run build --prefix app/web/streamlit_components/sentiment_workbench
git diff --check
```

Expected: tests/build PASS, `git diff --check` output 없음.

- [ ] **Step 2: backfill 전 canonical/PIT baseline을 읽는다**

```python
from finance.data.db.mysql import MySQLClient
db = MySQLClient("localhost", "root", "1234", 3306)
try:
    db.use_db("finance_meta")
    print(db.query("""SELECT source, series_id, MIN(observation_date) start_date,
      MAX(observation_date) end_date, COUNT(*) row_count
      FROM macro_series_observation
      WHERE source IN ('cnn_fear_greed','aaii_sentiment_survey')
      AND series_id IN ('CNN_FEAR_GREED','AAII_BULLISH','AAII_NEUTRAL','AAII_BEARISH','AAII_BULL_BEAR_SPREAD')
      GROUP BY source, series_id ORDER BY source, series_id"""))
    print(db.query("""SELECT source, MIN(observed_at) pit_start_at,
      MAX(observed_at) latest_capture_at, COUNT(DISTINCT batch_id) capture_count
      FROM market_sentiment_observation_snapshot GROUP BY source ORDER BY source"""))
finally:
    db.close()
```

Run the snippet with `.venv/bin/python - <<'PY' ... PY`. Expected: existing AAII PIT start begins `2026-07-20`.

- [ ] **Step 3: explicit canonical backfill을 한 번 실행한다**

```bash
.venv/bin/python - <<'PY'
from finance.data.sentiment import backfill_aaii_sentiment_history
print(backfill_aaii_sentiment_history())
PY
```

Expected: start `1987-07-24` 부근, latest official Reported Date, 약 2,032 weeks/8,128 rows. workbook 갱신 시 정확한 date/count는 실제 응답을 따른다.

- [ ] **Step 4: 네 series 정렬과 PIT 비소급을 검증한다**

```python
rows = db.query("""SELECT series_id, MIN(observation_date) start_date,
  MAX(observation_date) end_date, COUNT(*) row_count
  FROM macro_series_observation WHERE source='aaii_sentiment_survey'
  AND series_id IN ('AAII_BULLISH','AAII_NEUTRAL','AAII_BEARISH','AAII_BULL_BEAR_SPREAD')
  GROUP BY series_id ORDER BY series_id""")
pit = db.query("""SELECT MIN(observed_at) pit_start_at
  FROM market_sentiment_observation_snapshot WHERE source='aaii_sentiment_survey'""")
assert len(rows) == 4
assert len({(row['start_date'], row['end_date'], row['row_count']) for row in rows}) == 1
assert str(pit[0]['pit_start_at']).startswith('2026-07-20')
```

Expected: 네 series 동일 start/end/count, PIT start 유지.

- [ ] **Step 5: desktop Browser QA를 수행한다**

```text
1. 6M의 CNN/AAII 첫/마지막 x tick이 동일하다.
2. 1Y의 CNN/AAII 첫/마지막 x tick이 동일하다.
3. 공통 전체 시작/끝이 max(start)/min(end)다.
4. common end 이후 CNN 선/tooltip/header 값이 없다.
5. 비교 구간과 source별 보유 이력이 구분된다.
6. AAII 응답/Spread 전환 후 x tick이 유지된다.
7. 양 끝 hover tooltip이 card 밖으로 잘리지 않는다.
8. 1W/1M은 UNAVAILABLE이다.
9. console error가 0개다.
```

- [ ] **Step 6: 420px QA와 untracked screenshot을 남긴다**

420px에서 기간 버튼, coverage wrapping, 두 행 chart, AAII tab, hover overflow를 확인하고 repository root에 `overview-sentiment-common-history-alignment-qa.png`를 저장한다. 이 파일은 commit하지 않는다.

- [ ] **Step 7: finance-doc-sync 지침으로 task/root 문서를 갱신한다**

```markdown
- 2차 보정 완료: AAII 공식 workbook canonical backfill + CNN/AAII common intersection x-domain.
- 6M / 1Y / 공통 전체는 교집합만 표시하고 source별 보유 이력은 coverage로 분리.
- historical canonical backfill을 immutable snapshot으로 소급 복제하지 않아 AAII PIT start 2026-07-20 유지.
- focused tests, TypeScript build, DB series alignment, desktop/420 Browser QA 완료.
- 전체 roadmap 2/4 유지. 3차 독립 데이터/예측 검증은 사용자 요청대로 보류.
```

`RUNS.md`에는 실제 command/count/date를, root logs에는 위 결론을 3~5줄로만 남긴다.

- [ ] **Step 8: final verification을 실행한다**

```bash
git status --short
git diff --check
.venv/bin/python -m unittest tests.test_sentiment_pit -v
npm run build --prefix app/web/streamlit_components/sentiment_workbench
```

Expected: PASS; untracked에는 QA screenshot과 기존 사용자 artifact만 보임.

- [ ] **Step 9: closeout docs를 commit한다**

```bash
git add .aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1/STATUS.md
git add .aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1/RUNS.md
git add .aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1/RISKS.md
git add .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "Overview 심리 공통기간 보정 완료 기록"
```

Do not stage the QA screenshot, `.superpowers/`, registries, saved JSONL, unrelated research bundle, or previous screenshots.

---

## Completion Gate

- workbook parser가 official date/fractions를 네 기존 series로 변환한다.
- daily PIT는 AAII 최신 26주만 저장한다.
- full backfill은 fetch/parse 성공 후 canonical transaction만 연다.
- 네 AAII canonical series가 같은 date set/count이며 workbook latest 이하만 교체된다.
- immutable AAII PIT start가 2026-07-20에서 소급 이동하지 않는다.
- service/payload common range가 source coverage 교집합이다.
- CNN/AAII가 6M, 1Y, 공통 전체에서 같은 x-domain을 사용한다.
- 공통 범위 밖 값이 line, tooltip, latest header에 없다.
- AAII 응답/Spread가 같은 domain을 유지한다.
- desktop/420px QA, zero console error, screenshot이 확인된다.
- 1W/1M은 `UNAVAILABLE`, 전체 roadmap은 2/4, 3차는 보류다.
