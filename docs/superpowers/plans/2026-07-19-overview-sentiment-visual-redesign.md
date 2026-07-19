# Overview 시장 심리 시각 개편 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 CNN·AAII 두 축 판정을 유지하면서 Overview 시장 심리를 서사형 Hero, 균형 current evidence, CNN 고정 + AAII 전환의 두 graph, 검증 상태가 명확한 1W·1M card로 개편한다.

**Architecture:** `app/services/overview/sentiment.py`가 교차 판정과 전망 publication 상태를 소유하고 `app/web/overview/sentiment_helpers.py`가 직렬화 가능한 `sentiment_react_workbench_v2` payload로 변환한다. React root는 section 순서와 Python action dispatch만 담당하고 Hero, current evidence, history, outlook, watch, disclosure를 독립 component로 분리한다. 시각 상태인 AAII tab과 graph hover는 React 안에서만 처리하며 DB·ingestion·판정 임계값은 변경하지 않는다.

**Tech Stack:** Python 3, pandas, unittest service contracts, React 18, TypeScript 5, Vite 6, Streamlit custom component, SVG polyline, CSS, in-app Browser QA.

## Global Constraints

- CNN은 `시장 행동`, AAII는 `개인투자자 설문`이며 하나의 숫자형 합성점수를 만들지 않는다.
- AAII 방향은 Bull-Bear Spread `>= +10pp` 낙관, `<= -10pp` 비관, 그 사이는 중립으로 유지한다.
- CNN 구성요소는 CNN headline의 내부 근거이며 별도 심리 축으로 다시 합산하지 않는다.
- 화면 순서는 Hero → current evidence → history → 1W·1M outlook → watch conditions → method/raw disclosure다.
- Hero에서 교차 판정을 한 번만 설명하며 별도의 cross-read card를 만들지 않는다.
- CNN source color는 warm brown, AAII source color는 teal로 고정하고 상태색과 분리한다.
- source box 상단의 갈색·녹청색 rounded rail을 렌더링하지 않는다.
- 화면에는 CNN graph와 AAII graph 두 panel만 동시에 표시한다.
- AAII graph 기본 tab은 `AAII 응답`이고 `AAII Spread`로 전환한다.
- 모든 graph는 실제 관측일 x좌표 사이를 SVG `polyline` 직선으로 연결하며 spline, bezier, curve smoothing을 사용하지 않는다.
- 검증된 estimator와 validation evidence가 없으면 1W·1M은 모두 `UNAVAILABLE`이고 probability를 렌더링하지 않는다.
- 신규 provider, DB schema, ingestion job, 가상 중간 관측, 매수·매도 신호를 추가하지 않는다.
- 기존 refresh/reload action id와 `python_dispatch_only` 경계를 유지한다.
- 420px viewport에서 document와 component의 horizontal overflow가 없어야 한다.

## File Structure

- `app/services/overview/sentiment.py`: CNN·AAII 판정, server-owned history 상태 문구, confirm/reverse/persist 관찰 경로, 전망 publication gate의 source of truth.
- `app/web/overview/sentiment_helpers.py`: service snapshot을 JSON-safe v2 payload로 변환하고 검증되지 않은 확률을 제거한다.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`: shared payload types, formatting helpers, action dispatch, 최종 section ordering만 소유한다.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentHero.tsx`: 교차 판정 서사와 refresh/reload action을 한 번만 표시한다.
- `app/web/streamlit_components/sentiment_workbench/src/CurrentEvidenceSection.tsx`: 같은 밀도의 CNN·AAII 현재 근거 두 box를 표시한다.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`: raw-date scale, straight polyline, hover, CNN 고정 panel, AAII tab을 소유한다.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentOutlookSection.tsx`: 1W·1M publication status와 guarded probabilities를 표시한다.
- `app/web/streamlit_components/sentiment_workbench/src/WatchConditionsSection.tsx`: confirm/reverse/persist 세 관찰 경로를 표시한다.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentEvidenceDisclosure.tsx`: 방법·상세 evidence·raw tables를 기본 접힘 상태로 제공한다.
- `app/web/streamlit_components/sentiment_workbench/src/style.css`: approved source colors, neutral surfaces, two-column desktop/one-column mobile layout을 소유한다.
- `tests/test_service_contracts.py`: service/payload semantics와 React source contract를 회귀 검증한다.

---

### Task 1: 전망 publication gate와 graph 의미 payload

**Files:**
- Modify: `app/services/overview/sentiment.py:715-890`
- Modify: `app/web/overview/sentiment_helpers.py:471-617`
- Modify: `tests/test_service_contracts.py:22020-22320`
- Modify: `tests/test_service_contracts.py:22620-22905`

**Interfaces:**
- Consumes: existing `_build_sentiment_axes(...)`, `_build_sentiment_cross_read(...)`, stored `history_rows`.
- Produces: `_build_sentiment_outlook() -> dict[str, Any]`, `analysis["outlook"]`, confirm/reverse/persist `analysis["watch_conditions"]`, server-owned history `State`, `_sentiment_outlook_payload(value: Any) -> dict[str, Any]`, `payload["outlook"]`.
- `payload["outlook"]["horizons"]` contains exactly `1W` and `1M`; each unavailable horizon has `probabilities == []`, `episode_count == 0`, and no numeric baseline.

- [ ] **Step 1: Write failing service tests for the unavailable outlook contract**

Add to `OverviewMarketIntelligenceServiceContractTests`:

```python
def test_market_sentiment_outlook_stays_unavailable_without_validated_estimator(self) -> None:
    from app.services.overview.sentiment import _build_market_sentiment_analysis

    analysis = _build_market_sentiment_analysis(
        coverage={
            "cnn_score": 37.1,
            "aaii_bullish": 44.9,
            "aaii_neutral": 22.2,
            "aaii_bearish": 32.9,
            "aaii_bull_bear_spread": 12.0,
            "source_count": 2,
            "missing_count": 0,
            "stale_count": 0,
        },
        component_rows=[],
        history_rows=pd.DataFrame(),
    )

    self.assertEqual(analysis["outlook"]["status"], "UNAVAILABLE")
    self.assertEqual([row["key"] for row in analysis["outlook"]["horizons"]], ["1W", "1M"])
    for row in analysis["outlook"]["horizons"]:
        self.assertEqual(row["status"], "UNAVAILABLE")
        self.assertEqual(row["probabilities"], [])
        self.assertEqual(row["episode_count"], 0)
        self.assertIsNone(row["baseline"])
        self.assertIn("point-in-time", row["status_reason"])

def test_market_sentiment_watch_conditions_publish_three_relationship_paths(self) -> None:
    from app.services.overview.sentiment import _build_market_sentiment_analysis

    analysis = _build_market_sentiment_analysis(
        coverage={
            "cnn_score": 37.1,
            "aaii_bullish": 44.9,
            "aaii_neutral": 22.2,
            "aaii_bearish": 32.9,
            "aaii_bull_bear_spread": 12.0,
            "source_count": 2,
            "missing_count": 0,
            "stale_count": 0,
        },
        component_rows=[],
        history_rows=pd.DataFrame(),
    )

    self.assertEqual(
        [row["key"] for row in analysis["watch_conditions"]],
        ["confirm", "reverse", "persist"],
    )
    self.assertTrue(all(row["condition"] for row in analysis["watch_conditions"]))
```

- [ ] **Step 2: Run the service test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_outlook_stays_unavailable_without_validated_estimator \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_watch_conditions_publish_three_relationship_paths \
  -v
```

Expected: `ERROR` or `FAIL` because `analysis["outlook"]` does not exist.

- [ ] **Step 3: Add the deterministic unavailable outlook builder**

Add above `_build_market_sentiment_analysis`:

```python
def _build_sentiment_outlook() -> dict[str, Any]:
    """Publish horizon slots without inventing probabilities before PIT validation."""
    status_reason = (
        "장기 이력과 point-in-time 분리 검증을 통과한 estimator가 없어 "
        "확률을 공개하지 않습니다."
    )
    horizons = [
        {
            "key": "1W",
            "label": "1주",
            "period_label": "다음 5거래일",
            "trading_days": 5,
            "status": "UNAVAILABLE",
            "status_label": "통계적 판단 불가",
            "dominant_path": None,
            "probabilities": [],
            "baseline": None,
            "episode_count": 0,
            "validation_evidence": [],
            "status_reason": status_reason,
        },
        {
            "key": "1M",
            "label": "1개월",
            "period_label": "다음 20거래일",
            "trading_days": 20,
            "status": "UNAVAILABLE",
            "status_label": "통계적 판단 불가",
            "dominant_path": None,
            "probabilities": [],
            "baseline": None,
            "episode_count": 0,
            "validation_evidence": [],
            "status_reason": status_reason,
        },
    ]
    return {
        "status": "UNAVAILABLE",
        "summary": "현재는 확률 전망 대신 다음 CNN·AAII 관측 조건을 확인합니다.",
        "horizons": horizons,
    }
```

Add `"outlook": _build_sentiment_outlook(),` to the return value of `_build_market_sentiment_analysis` immediately after `"watch_conditions"`.

Replace `_build_sentiment_watch_conditions` with a relationship-path contract and pass `cross_read` from `_build_market_sentiment_analysis`:

```python
def _build_sentiment_watch_conditions(
    axes: dict[str, dict[str, Any]],
    cross_read: dict[str, Any],
) -> list[dict[str, str]]:
    market = axes["market_behavior"]
    survey = axes["investor_survey"]
    return [
        {
            "key": "confirm",
            "label": "정렬 확인",
            "condition": (
                f"CNN {market['direction_label']}와 AAII {survey['direction_label']}가 "
                "같은 방향으로 모이는지 확인합니다."
            ),
            "basis": "두 source의 다음 유효 관측",
            "tone": "positive",
        },
        {
            "key": "reverse",
            "label": "설문 반전",
            "condition": (
                f"AAII {survey['direction_label']} 우위가 ±10pp 경계를 넘어 "
                "반대 방향으로 전환되는지 확인합니다."
            ),
            "basis": "AAII 주간 Bull-Bear Spread",
            "tone": "warning",
        },
        {
            "key": "persist",
            "label": "관계 지속",
            "condition": f"현재 `{cross_read['status']}` 관계가 다음 CNN·AAII 관측에서도 이어지는지 확인합니다.",
            "basis": "CNN 일간 × AAII 주간",
            "tone": cross_read.get("tone") or "neutral",
        },
    ]
```

Change the caller to `_build_sentiment_watch_conditions(axes, cross_read)`.

Add `"State"` to `SENTIMENT_HISTORY_COLUMNS`, then keep historical status semantics in the service:

```python
def _sentiment_history_state_label(series_id: Any, value: Any) -> str:
    normalized = str(series_id or "").upper()
    numeric = _safe_float(value)
    if normalized == "CNN_FEAR_GREED":
        return _sentiment_score_bucket(numeric)["label_ko"] if numeric is not None else "판정 보류"
    if normalized == "AAII_BULL_BEAR_SPREAD":
        return _aaii_direction_label(_aaii_direction(spread=numeric))
    return ""
```

When building `visible_history`, assign:

```python
visible_history["State"] = visible_history.apply(
    lambda row: _sentiment_history_state_label(row.get("series_id"), row.get("value")),
    axis=1,
)
```

- [ ] **Step 4: Run the service test and confirm GREEN**

Run the Step 2 command. Expected: `OK`, 2 tests passed.

- [ ] **Step 5: Write a failing payload guard test**

Extend `test_market_sentiment_react_payload_uses_existing_snapshot_fields` by putting `_build_sentiment_outlook()` output in `snapshot["analysis"]["outlook"]`, then add:

Replace that fixture's two legacy source checks with three relationship paths:

```python
"watch_conditions": [
    {"key": "confirm", "label": "정렬 확인", "condition": "두 축이 같은 방향으로 모이는지 확인합니다.", "basis": "다음 유효 관측", "tone": "positive"},
    {"key": "reverse", "label": "설문 반전", "condition": "AAII 방향 반전을 확인합니다.", "basis": "AAII 주간", "tone": "warning"},
    {"key": "persist", "label": "관계 지속", "condition": "현재 엇갈림이 이어지는지 확인합니다.", "basis": "CNN 일간 × AAII 주간", "tone": "warning"},
],
```

Then add:

```python
self.assertEqual(payload["outlook"]["status"], "UNAVAILABLE")
self.assertEqual([row["key"] for row in payload["outlook"]["horizons"]], ["1W", "1M"])
for row in payload["outlook"]["horizons"]:
    self.assertEqual(row["status"], "UNAVAILABLE")
    self.assertEqual(row["probabilities"], [])
    self.assertIsNone(row["baseline"])
    self.assertEqual(row["episode_count"], 0)
self.assertEqual([row["key"] for row in payload["watch_conditions"]], ["confirm", "reverse", "persist"])
```

Add `"State": "공포"` to the latest CNN history fixture and assert:

```python
self.assertEqual(payload["charts"]["cnn"]["series"][-1]["status_label"], "공포")
self.assertEqual(payload["charts"]["cnn"]["latest"]["label"], "공포")
```

Add a separate malicious-demo case:

```python
def test_market_sentiment_payload_drops_unvalidated_demo_probabilities(self) -> None:
    from app.web.overview.sentiment_helpers import _sentiment_outlook_payload

    payload = _sentiment_outlook_payload({
        "status": "UNAVAILABLE",
        "horizons": [{
            "key": "1W",
            "status": "UNAVAILABLE",
            "probabilities": [{"label": "엇갈림 유지", "value": 0.71}],
            "baseline": 0.44,
            "episode_count": 88,
        }],
    })

    self.assertEqual(payload["horizons"][0]["probabilities"], [])
    self.assertIsNone(payload["horizons"][0]["baseline"])
    self.assertEqual(payload["horizons"][0]["episode_count"], 0)
```

- [ ] **Step 6: Run the payload tests and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_payload_drops_unvalidated_demo_probabilities \
  -v
```

Expected: the new assertions fail because `_sentiment_outlook_payload` and `payload["outlook"]` do not exist.

- [ ] **Step 7: Implement the payload adapter with an explicit publication guard**

Add before `build_sentiment_react_workbench_payload`:

```python
def _sentiment_probability_rows(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in list(value or []):
        if not isinstance(item, dict):
            continue
        probability = _safe_float(item.get("value"))
        if probability is None or probability < 0 or probability > 1:
            continue
        rows.append({
            "key": _display_text(item.get("key") or item.get("label")),
            "label": _display_text(item.get("label")),
            "value": probability,
            "baseline": _safe_float(item.get("baseline")),
            "difference_pp": _safe_float(item.get("difference_pp")),
        })
    return rows


def _sentiment_outlook_payload(value: Any) -> dict[str, Any]:
    source = dict(value) if isinstance(value, dict) else {}
    source_by_key = {
        str(item.get("key") or ""): dict(item)
        for item in list(source.get("horizons") or [])
        if isinstance(item, dict)
    }
    horizons: list[dict[str, Any]] = []
    for key, label, period_label, trading_days in (
        ("1W", "1주", "다음 5거래일", 5),
        ("1M", "1개월", "다음 20거래일", 20),
    ):
        item = source_by_key.get(key, {})
        status = str(item.get("status") or "UNAVAILABLE").upper()
        if status not in {"VERIFIED", "PROVISIONAL", "UNAVAILABLE"}:
            status = "UNAVAILABLE"
        can_publish = status in {"VERIFIED", "PROVISIONAL"} and bool(item.get("validation_evidence"))
        horizons.append({
            "key": key,
            "label": label,
            "period_label": period_label,
            "trading_days": trading_days,
            "status": status if can_publish else "UNAVAILABLE",
            "status_label": _display_text(
                item.get("status_label") if can_publish else "통계적 판단 불가"
            ),
            "dominant_path": _display_text(item.get("dominant_path"), "") if can_publish else "",
            "probabilities": _sentiment_probability_rows(item.get("probabilities")) if can_publish else [],
            "baseline": _json_safe_value(item.get("baseline")) if can_publish else None,
            "episode_count": int(item.get("episode_count") or 0) if can_publish else 0,
            "validation_evidence": list(item.get("validation_evidence") or []) if can_publish else [],
            "status_reason": _display_text(
                item.get("status_reason"),
                "장기 이력과 point-in-time 검증이 부족해 확률을 공개하지 않습니다.",
            ),
        })
    return {
        "status": "UNAVAILABLE" if all(row["status"] == "UNAVAILABLE" for row in horizons) else "AVAILABLE",
        "summary": _display_text(
            source.get("summary"),
            "현재는 확률 전망 대신 다음 CNN·AAII 관측 조건을 확인합니다.",
        ),
        "horizons": horizons,
    }
```

Add `"outlook": _sentiment_outlook_payload(analysis.get("outlook")),` immediately before `"watch_conditions"` in the v2 payload.

Preserve `key` while adapting watch conditions:

```python
"key": _display_text(item.get("key"), "persist"),
```

Extend `_sentiment_chart_points` with server-owned semantics:

```python
"status_label": _display_text(row.get("State"), ""),
```

Add `latest` metadata to all three chart panels. CNN uses `market_behavior`; Spread uses `investor_survey`; AAII responses use the three response values. The CNN shape is:

```python
"latest": {
    "date": market_behavior.get("latest_date") or "-",
    "value": market_behavior.get("current"),
    "label": market_behavior.get("direction_label") or "판정 보류",
},
```

The AAII panel shapes are:

```python
"latest": {
    "date": investor_survey.get("latest_date") or "-",
    "value": None,
    "label": (
        f"Bullish {_format_sentiment_percent(dict(investor_survey.get('responses') or {}).get('bullish'))} · "
        f"Neutral {_format_sentiment_percent(dict(investor_survey.get('responses') or {}).get('neutral'))} · "
        f"Bearish {_format_sentiment_percent(dict(investor_survey.get('responses') or {}).get('bearish'))}"
    ),
},
```

```python
"latest": {
    "date": investor_survey.get("latest_date") or "-",
    "value": investor_survey.get("spread"),
    "label": investor_survey.get("direction_label") or "판정 보류",
},
```

- [ ] **Step 8: Run focused sentiment service and payload tests**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_aaii_direction_uses_spread_without_bearish_gate \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_two_axis_cross_read_marks_cnn_fear_aaii_optimistic_as_divergent \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_cross_read_matrix_handles_alignment_neutral_and_missing \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_outlook_stays_unavailable_without_validated_estimator \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_watch_conditions_publish_three_relationship_paths \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_payload_drops_unvalidated_demo_probabilities \
  -v
```

Expected: `OK`, 7 tests passed.

- [ ] **Step 9: Commit the outlook contract**

```bash
git add app/services/overview/sentiment.py app/web/overview/sentiment_helpers.py tests/test_service_contracts.py
git commit -m "Overview 심리 전망 공개 경계 추가"
```

---

### Task 2: Hero와 균형 current evidence 구조

**Files:**
- Create: `app/web/streamlit_components/sentiment_workbench/src/SentimentHero.tsx`
- Create: `app/web/streamlit_components/sentiment_workbench/src/CurrentEvidenceSection.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx:1-584`
- Modify: `tests/test_service_contracts.py:8498-8767`

**Interfaces:**
- Consumes: existing `SentimentWorkbenchPayload`, `SentimentAction`, `SentimentAxis`, format helpers.
- Produces: `SentimentHero`, `CurrentEvidenceSection`; root order starts with these two components and contains no separate cross-read section.
- `SentimentHero` receives `payload`, `pendingActionLabel`, and `onAction(action)`; `CurrentEvidenceSection` receives `axes` and `aaiiComparison`.

- [ ] **Step 1: Write a failing hierarchy contract test**

Add to `OverviewAutomationContractTests`:

```python
def test_sentiment_react_visual_hierarchy_uses_hero_and_balanced_current_evidence(self) -> None:
    source_root = Path("app/web/streamlit_components/sentiment_workbench/src")
    root_source = (source_root / "SentimentWorkbench.tsx").read_text(encoding="utf-8")
    all_source = "\n".join(path.read_text(encoding="utf-8") for path in source_root.glob("*.tsx"))

    self.assertTrue((source_root / "SentimentHero.tsx").exists())
    self.assertTrue((source_root / "CurrentEvidenceSection.tsx").exists())
    self.assertIn("<SentimentHero", root_source)
    self.assertIn("<CurrentEvidenceSection", root_source)
    self.assertLess(root_source.index("<SentimentHero"), root_source.index("<CurrentEvidenceSection"))
    self.assertNotIn('<section className="sentiment-workbench__cross-read"', root_source)
    self.assertEqual(all_source.count("payload.cross_read.meaning"), 1)
    self.assertIn('kind="cnn"', all_source)
    self.assertIn('kind="aaii"', all_source)
    self.assertIn("axis.available", all_source)
    self.assertIn("관측값 없음 · 판정 보류", all_source)
```

- [ ] **Step 2: Run the hierarchy test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_visual_hierarchy_uses_hero_and_balanced_current_evidence -v
```

Expected: `FAIL` because the section files do not exist and the old root renders a separate cross-read card.

- [ ] **Step 3: Export the shared component types and format helpers**

In `SentimentWorkbench.tsx`, add `export` to `SentimentAction`, `SentimentAxis`, `AaiiComparison`, `SentimentWorkbenchPayload`, `displayValue`, `signedValue`, and `toneColor`. Keep `payload.schema_version === "sentiment_react_workbench_v2"` and the existing event dispatch unchanged. Update existing sentiment source-contract tests to concatenate all `src/*.tsx` files for section markup assertions; keep schema validation and event dispatch assertions against `SentimentWorkbench.tsx` itself.

The exported outlook types must be:

```tsx
export type OutlookStatus = "VERIFIED" | "PROVISIONAL" | "UNAVAILABLE";

export type OutlookProbability = {
  key?: string;
  label: string;
  value: number;
  baseline?: number | null;
  difference_pp?: number | null;
};

export type OutlookHorizon = {
  key: "1W" | "1M";
  label: string;
  period_label: string;
  trading_days: 5 | 20;
  status: OutlookStatus;
  status_label: string;
  dominant_path?: string;
  probabilities: OutlookProbability[];
  baseline?: number | null;
  episode_count: number;
  validation_evidence: string[];
  status_reason: string;
};
```

Extend the existing chart types so historical interpretation remains server-owned:

```tsx
export type ChartPoint = {
  date: string;
  series: string;
  value?: NumericValue;
  source?: string;
  status_label?: string;
};

export type ChartPanel = {
  title: string;
  basis: string;
  unit: "score_0_100" | "percent" | "percentage_point";
  latest?: {
    date: string;
    value?: NumericValue;
    label: string;
  };
  series: ChartPoint[];
};
```

Export the watch condition type with its stable relationship keys:

```tsx
export type WatchCondition = {
  key: "confirm" | "reverse" | "persist";
  label: string;
  condition: string;
  basis: string;
  tone?: string;
};
```

Extend `SentimentWorkbenchPayload` with:

```tsx
outlook: {
  status: "AVAILABLE" | "UNAVAILABLE";
  summary: string;
  horizons: OutlookHorizon[];
};
```

- [ ] **Step 4: Create `SentimentHero` and place the cross-read narrative once**

Create `SentimentHero.tsx`:

```tsx
import type { SentimentAction, SentimentWorkbenchPayload } from "./SentimentWorkbench";

type Props = {
  payload: SentimentWorkbenchPayload;
  pendingActionLabel: string;
  onAction: (action: SentimentAction) => void;
};

function SentimentHero({ payload, pendingActionLabel, onAction }: Props) {
  return (
    <section className="sentiment-workbench__hero" aria-labelledby="sentiment-hero-title">
      <div className="sentiment-workbench__command-row">
        <div>
          <span className="sentiment-workbench__eyebrow">Market psychology · cross read</span>
          <small>CNN 시장 행동 × AAII 개인투자자 설문</small>
        </div>
        <div className="sentiment-workbench__actions" aria-label="시장 심리 자료 동작">
          {payload.command.actions.map((action) => (
            <button
              className={`sentiment-workbench__action sentiment-workbench__action--${action.kind}`}
              key={action.id}
              onClick={() => onAction(action)}
              title={action.detail}
              type="button"
            >
              {action.label}
            </button>
          ))}
          {pendingActionLabel ? <span className="sentiment-workbench__action-feedback">요청 전송 · {pendingActionLabel}</span> : null}
        </div>
      </div>
      <div className="sentiment-workbench__hero-grid">
        <div className="sentiment-workbench__hero-copy">
          <span className="sentiment-workbench__kicker">{payload.cross_read.status}</span>
          <h2 id="sentiment-hero-title">{payload.summary.headline}</h2>
          <div className="sentiment-workbench__transition">{payload.summary.phase_label}</div>
          <p>{payload.cross_read.meaning}</p>
          {payload.cross_read.confidence_note ? <small>{payload.cross_read.confidence_note}</small> : null}
        </div>
        <aside className="sentiment-workbench__hero-side">
          <div><span>CNN 시장 행동</span><strong>{payload.axes.market_behavior.direction_label}</strong></div>
          <div><span>AAII 투자자 설문</span><strong>{payload.axes.investor_survey.direction_label}</strong></div>
        </aside>
      </div>
      <div className="sentiment-workbench__hero-meta">
        <span>CNN {payload.axes.market_behavior.latest_date || "-"}</span>
        <span>AAII {payload.axes.investor_survey.latest_date || "-"}</span>
        <span>합성점수 없음</span>
        <span>매수·매도 신호 아님</span>
        {payload.freshness.stale_count > 0 ? <span>stale {payload.freshness.stale_count} · 상세 근거 확인</span> : null}
      </div>
    </section>
  );
}

export default SentimentHero;
```

- [ ] **Step 5: Create equal-density current evidence boxes**

Create `CurrentEvidenceSection.tsx`. Reuse the existing score/change/date/breakdown/range markup, but render only the compact evidence required by the approved design:

```tsx
import { displayValue, signedValue } from "./SentimentWorkbench";
import type { AaiiComparison, SentimentAxis } from "./SentimentWorkbench";

function SourceEvidenceBox({ axis, kind, aaiiComparison }: { axis: SentimentAxis; kind: "cnn" | "aaii"; aaiiComparison: AaiiComparison[] }) {
  const balance = axis.component_balance;
  const responses = axis.responses;
  const bullishComparison = aaiiComparison.find((item) => item.key === "bullish");
  return (
    <article className={`sentiment-workbench__source-box sentiment-workbench__source-box--${kind}`}>
      <header>
        <div><span>{kind === "cnn" ? "CNN 시장 행동" : "AAII 투자자 설문"}</span><small>{axis.source}</small></div>
        <b>{axis.direction_label}</b>
      </header>
      {axis.available ? <>
        <div className="sentiment-workbench__source-value">
          <strong>{displayValue(axis.current, kind === "aaii" ? "pp" : "")}</strong>
          <span>직전 대비 {signedValue(axis.change, kind === "aaii" ? "pp" : "p")}</span>
        </div>
        <small>기준 {axis.latest_date || "-"} · 직전 {axis.previous_date || "-"}</small>
      </> : <div className="sentiment-workbench__source-empty">관측값 없음 · 판정 보류</div>}
      <div className="sentiment-workbench__source-breakdown">
        {kind === "cnn" ? (
          <><span>탐욕 <b>{balance?.greed_count ?? 0}</b></span><span>중립 <b>{balance?.neutral_count ?? 0}</b></span><span>공포 <b>{balance?.fear_count ?? 0}</b></span></>
        ) : (
          <><span>Bullish <b>{displayValue(responses?.bullish, "%")}</b></span><span>Neutral <b>{displayValue(responses?.neutral, "%")}</b></span><span>Bearish <b>{displayValue(responses?.bearish, "%")}</b></span></>
        )}
      </div>
      <p>{kind === "cnn" ? axis.components_support : `Bullish 장기평균 대비 ${signedValue(bullishComparison?.difference_pp, "pp")} · ${axis.detail || ""}`}</p>
      <small>{axis.range?.sample_count ?? 0}개 관측 · {axis.range?.position_label || "자료 부족"}</small>
    </article>
  );
}

function CurrentEvidenceSection({ axes, aaiiComparison }: { axes: { market_behavior: SentimentAxis; investor_survey: SentimentAxis }; aaiiComparison: AaiiComparison[] }) {
  return (
    <section className="sentiment-workbench__current-section" aria-labelledby="sentiment-current-title">
      <div className="sentiment-workbench__section-heading"><div><span>Current evidence</span><h3 id="sentiment-current-title">두 축의 현재 근거</h3></div><small>행동과 인식을 같은 깊이로 비교</small></div>
      <div className="sentiment-workbench__source-grid">
        <SourceEvidenceBox aaiiComparison={aaiiComparison} axis={axes.market_behavior} kind="cnn" />
        <SourceEvidenceBox aaiiComparison={aaiiComparison} axis={axes.investor_survey} kind="aaii" />
      </div>
    </section>
  );
}

export default CurrentEvidenceSection;
```

- [ ] **Step 6: Reduce the root to orchestration and section order**

Import the new components and replace the old Hero, freshness strip, axis grid, and cross-read card with:

```tsx
<SentimentHero payload={payload} pendingActionLabel={pendingActionLabel} onAction={emitAction} />
<CurrentEvidenceSection aaiiComparison={payload.evidence.aaii_comparison} axes={payload.axes} />
```

Keep the existing detailed evidence, chart, watch, and disclosure temporarily below them until Tasks 3 and 4 replace those blocks. Do not render `payload.cross_read` anywhere else.

In the pre-existing sentiment source-contract tests, replace assertions for `sentiment-workbench__freshness-strip`, `sentiment-workbench__axis-grid`, and `sentiment-workbench__cross-read` with assertions for `SentimentHero`, `CurrentEvidenceSection`, `sentiment-workbench__hero-meta`, and `sentiment-workbench__source-grid`. This keeps the regression suite aligned at the end of Task 2 rather than leaving tests red between commits.

- [ ] **Step 7: Run the hierarchy contract and TypeScript check**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_visual_hierarchy_uses_hero_and_balanced_current_evidence -v
cd app/web/streamlit_components/sentiment_workbench && ./node_modules/.bin/tsc --noEmit
```

Expected: unittest `OK`; TypeScript exits 0 with no output.

- [ ] **Step 8: Commit Hero and current evidence**

```bash
git add app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx app/web/streamlit_components/sentiment_workbench/src/SentimentHero.tsx app/web/streamlit_components/sentiment_workbench/src/CurrentEvidenceSection.tsx tests/test_service_contracts.py
git commit -m "Overview 심리 Hero와 현재 근거 재구성"
```

---

### Task 3: CNN 고정 + AAII 전환의 직선 graph

**Files:**
- Create: `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css:300-520`
- Modify: `tests/test_service_contracts.py:8769-8822`

**Interfaces:**
- Consumes: `payload.charts.cnn`, `payload.charts.aaii_responses`, `payload.charts.aaii_spread`.
- Produces: `SentimentHistorySection({ charts })`, local `AaiiHistoryTab = "aaii_responses" | "aaii_spread"`, two simultaneous `.sentiment-workbench__history-panel` nodes.
- Graphs use `Date.parse(point.date)` for x-position, `<polyline>` for raw-point connections, and no `path` `C/S/Q` commands.

- [ ] **Step 1: Replace the old graph source contract with a failing two-panel contract**

Update `test_sentiment_react_evidence_surface_improves_graphs_and_raw_detail`:

```python
source_root = Path("app/web/streamlit_components/sentiment_workbench/src")
root_source = (source_root / "SentimentWorkbench.tsx").read_text(encoding="utf-8")
history_source = (source_root / "SentimentHistorySection.tsx").read_text(encoding="utf-8")

self.assertIn("<SentimentHistorySection", root_source)
self.assertIn('type AaiiHistoryTab = "aaii_responses" | "aaii_spread"', history_source)
self.assertIn('useState<AaiiHistoryTab>("aaii_responses")', history_source)
self.assertIn("charts.cnn", history_source)
self.assertIn("charts[aaiiTab]", history_source)
self.assertEqual(history_source.count("<SentimentLineChart"), 2)
self.assertIn("<polyline", history_source)
self.assertNotIn("<path", history_source)
self.assertNotIn("bezier", history_source.lower())
self.assertNotIn("spline", history_source.lower())
self.assertIn("Date.parse", history_source)
self.assertIn('role="tablist"', history_source)
self.assertIn('aria-controls="sentiment-aaii-history-panel"', history_source)
self.assertIn("onKeyDown={handleTabKeyDown}", history_source)
self.assertIn('event.key === "ArrowRight"', history_source)
self.assertIn('event.key === "ArrowLeft"', history_source)
self.assertIn("point.status_label", history_source)
self.assertIn("panel.latest?.label", history_source)
```

- [ ] **Step 2: Run the graph contract and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_evidence_surface_improves_graphs_and_raw_detail -v
```

Expected: `ERROR` because `SentimentHistorySection.tsx` does not exist.

- [ ] **Step 3: Move chart math and hover handling into `SentimentHistorySection`**

Import `ChartPanel`, `SentimentWorkbenchPayload`, and `displayValue` from `SentimentWorkbench`. Move the existing raw-date helpers `parsedChartPoints`, `chartExtent`, `chartDomain`, `xForTimestamp`, `yForValue`, `buildDateTicks`, `formatChartDate`, and nearest-date hover logic into the new file without changing their formulas. Set the source/style mapping exactly as follows:

```tsx
type AaiiHistoryTab = "aaii_responses" | "aaii_spread";
type ChartKind = "cnn" | AaiiHistoryTab;

function chartSeriesStyle(series: string) {
  if (series === "CNN Fear & Greed") return { color: "#9a6a44", dash: undefined };
  if (series === "AAII Bullish") return { color: "#0f766e", dash: undefined };
  if (series === "AAII Neutral") return { color: "#64748b", dash: "8 6" };
  if (series === "AAII Bearish") return { color: "#a14f61", dash: "3 6" };
  return { color: "#0f766e", dash: undefined };
}
```

Render each grouped raw series with a straight SVG polyline:

```tsx
{Object.entries(grouped).map(([series, seriesPoints]) => {
  const style = chartSeriesStyle(series);
  return (
    <polyline
      className="sentiment-workbench__chart-line"
      fill="none"
      key={series}
      points={seriesPoints.map((point) => `${xForTimestamp(point.timestamp, extent)},${yForValue(point.numericValue, domain)}`).join(" ")}
      stroke={style.color}
      strokeDasharray={style.dash}
    />
  );
})}
```

Keep the existing y domains: CNN and AAII response `0..100`, AAII Spread symmetric pp domain with `-10`, `0`, `+10` guides. Keep hover selection on the nearest actual timestamp and show all values observed on that timestamp.

In each tooltip row, append the service-owned status only when present:

```tsx
<span key={`${point.series}-tooltip`}>
  <i style={{ background: chartSeriesStyle(point.series).color }} />
  {point.series}
  <b>{displayValue(point.numericValue, chartValueSuffix(panel))}</b>
  {point.status_label ? <em>{point.status_label}</em> : null}
</span>
```

For the CNN panel, render the latest raw point and label without requiring hover:

```tsx
const lastSeriesPoint = grouped["CNN Fear & Greed"]?.at(-1);

{chartKind === "cnn" && panel.latest && lastSeriesPoint ? (
  <g className="sentiment-workbench__chart-latest">
    <circle cx={xForTimestamp(lastSeriesPoint.timestamp, extent)} cy={yForValue(lastSeriesPoint.numericValue, domain)} r={5} />
    <text x={xForTimestamp(lastSeriesPoint.timestamp, extent) - 8} y={yForValue(lastSeriesPoint.numericValue, domain) - 11} textAnchor="end">
      {displayValue(panel.latest.value)} · {panel.latest?.label}
    </text>
  </g>
) : null}
```

Add `<title>{panel.title} · 실제 관측값 직선 연결</title>` as the first child of each SVG.

- [ ] **Step 4: Build the fixed CNN panel and AAII tab panel**

Add the section shell:

```tsx
function SentimentHistorySection({ charts }: { charts: SentimentWorkbenchPayload["charts"] }) {
  const [aaiiTab, setAaiiTab] = useState<AaiiHistoryTab>("aaii_responses");
  const tabs: AaiiHistoryTab[] = ["aaii_responses", "aaii_spread"];
  const handleTabKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    setAaiiTab((current) => {
      const currentIndex = tabs.indexOf(current);
      const delta = event.key === "ArrowRight" ? 1 : -1;
      return tabs[(currentIndex + delta + tabs.length) % tabs.length];
    });
  };
  return (
    <section className="sentiment-workbench__history-section" aria-labelledby="sentiment-history-title">
      <div className="sentiment-workbench__section-heading"><div><span>History</span><h3 id="sentiment-history-title">과거 심리 흐름</h3></div><small>실제 관측점 사이를 직선 연결</small></div>
      <div className="sentiment-workbench__history-grid">
        <article className="sentiment-workbench__history-panel sentiment-workbench__history-panel--cnn">
          <SentimentLineChart chartKind="cnn" panel={charts.cnn} />
        </article>
        <article className="sentiment-workbench__history-panel sentiment-workbench__history-panel--aaii">
          <div className="sentiment-workbench__aaii-tabs" role="tablist" aria-label="AAII 그래프 보기">
            {tabs.map((tab) => (
              <button aria-controls="sentiment-aaii-history-panel" aria-selected={aaiiTab === tab} id={`sentiment-aaii-tab-${tab}`} key={tab} onClick={() => setAaiiTab(tab)} onKeyDown={handleTabKeyDown} role="tab" type="button">
                {tab === "aaii_responses" ? "AAII 응답" : "AAII Spread"}
              </button>
            ))}
          </div>
          <div aria-labelledby={`sentiment-aaii-tab-${aaiiTab}`} id="sentiment-aaii-history-panel" role="tabpanel">
            <SentimentLineChart chartKind={aaiiTab} panel={charts[aaiiTab]} />
          </div>
        </article>
      </div>
    </section>
  );
}
```

- [ ] **Step 5: Replace the old one-of-three tab block in the root**

Remove `ChartTab`, root `chartTab` state, `activeChart`, and the old `chart-tabs/chart-panel` JSX. Import and render:

```tsx
<SentimentHistorySection charts={payload.charts} />
```

Place it immediately after `<CurrentEvidenceSection ... />`.

- [ ] **Step 6: Set stable medium graph dimensions**

In the new history file use:

```tsx
const chartWidth = 960;
const chartHeight = 360;
const chartMargin = { top: 28, right: 38, bottom: 42, left: 54 };
```

In CSS set desktop plot height to `clamp(280px, 30vw, 360px)` and mobile plot height to `250px`. Do not set either graph to viewport height.

- [ ] **Step 7: Run graph contract and TypeScript check**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_evidence_surface_improves_graphs_and_raw_detail -v
cd app/web/streamlit_components/sentiment_workbench && ./node_modules/.bin/tsc --noEmit
```

Expected: unittest `OK`; TypeScript exits 0.

- [ ] **Step 8: Commit the two-panel graph**

```bash
git add app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx app/web/streamlit_components/sentiment_workbench/src/style.css tests/test_service_contracts.py
git commit -m "Overview 심리 두 패널 직선 그래프 적용"
```

---

### Task 4: 1W·1M card, watch conditions, method/raw disclosure

**Files:**
- Create: `app/web/streamlit_components/sentiment_workbench/src/SentimentOutlookSection.tsx`
- Create: `app/web/streamlit_components/sentiment_workbench/src/WatchConditionsSection.tsx`
- Create: `app/web/streamlit_components/sentiment_workbench/src/SentimentEvidenceDisclosure.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Modify: `tests/test_service_contracts.py:8663-8822`

**Interfaces:**
- Consumes: `payload.outlook`, `payload.watch_conditions`, `payload.evidence`, `payload.raw_evidence`, `payload.freshness`, `payload.boundary_note`.
- Produces: guarded probability rendering, three watch paths, one default-closed details disclosure.
- `SentimentOutlookSection` renders probability rows only when `status !== "UNAVAILABLE"` and `validation_evidence.length > 0`.

- [ ] **Step 1: Write failing section and probability guard tests**

Add to `OverviewAutomationContractTests`:

```python
def test_sentiment_react_outlook_and_disclosure_keep_unvalidated_probability_hidden(self) -> None:
    source_root = Path("app/web/streamlit_components/sentiment_workbench/src")
    root_source = (source_root / "SentimentWorkbench.tsx").read_text(encoding="utf-8")
    outlook_source = (source_root / "SentimentOutlookSection.tsx").read_text(encoding="utf-8")
    watch_source = (source_root / "WatchConditionsSection.tsx").read_text(encoding="utf-8")
    disclosure_source = (source_root / "SentimentEvidenceDisclosure.tsx").read_text(encoding="utf-8")

    self.assertIn("<SentimentOutlookSection", root_source)
    self.assertIn("<WatchConditionsSection", root_source)
    self.assertIn("<SentimentEvidenceDisclosure", root_source)
    self.assertLess(root_source.index("<SentimentOutlookSection"), root_source.index("<WatchConditionsSection"))
    self.assertLess(root_source.index("<WatchConditionsSection"), root_source.index("<SentimentEvidenceDisclosure"))
    self.assertIn('horizon.status !== "UNAVAILABLE"', outlook_source)
    self.assertIn("horizon.validation_evidence.length > 0", outlook_source)
    self.assertIn("통계적 판단 불가", outlook_source)
    self.assertIn("data-path={item.key}", watch_source)
    self.assertIn("key={item.key}", watch_source)
    self.assertIn("payload.raw_evidence.sentiment_rows", disclosure_source)
    self.assertIn("payload.raw_evidence.component_rows", disclosure_source)
    self.assertIn("payload.raw_evidence.history_rows", disclosure_source)
    self.assertIn("<details", disclosure_source)
```

- [ ] **Step 2: Run the section test and confirm RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_outlook_and_disclosure_keep_unvalidated_probability_hidden -v
```

Expected: `ERROR` because the new files do not exist.

- [ ] **Step 3: Create the guarded 1W·1M outlook cards**

Create `SentimentOutlookSection.tsx`:

```tsx
import type { OutlookHorizon, SentimentWorkbenchPayload } from "./SentimentWorkbench";

function HorizonCard({ horizon }: { horizon: OutlookHorizon }) {
  const canShowProbability = horizon.status !== "UNAVAILABLE" && horizon.validation_evidence.length > 0;
  return (
    <article className={`sentiment-workbench__outlook-card is-${horizon.status.toLowerCase()}`}>
      <header><div><span>{horizon.label}</span><strong>{horizon.period_label}</strong></div><b>{horizon.status_label}</b></header>
      {canShowProbability ? (
        <div className="sentiment-workbench__probabilities">
          {horizon.probabilities.map((row) => (
            <div className="sentiment-workbench__probability-row" key={row.key || row.label}>
              <span>{row.label}</span><div><i style={{ width: `${Math.max(0, Math.min(100, row.value * 100))}%` }} /></div><strong>{Math.round(row.value * 100)}%</strong>
            </div>
          ))}
        </div>
      ) : <div className="sentiment-workbench__outlook-unavailable">통계적 판단 불가</div>}
      <p>{canShowProbability ? horizon.dominant_path : horizon.status_reason}</p>
      <footer>{canShowProbability ? `독립 표본 ${horizon.episode_count}개` : "다음 관측 조건을 확인하세요."}</footer>
    </article>
  );
}

function SentimentOutlookSection({ outlook }: { outlook: SentimentWorkbenchPayload["outlook"] }) {
  return (
    <section className="sentiment-workbench__outlook-section" aria-labelledby="sentiment-outlook-title">
      <div className="sentiment-workbench__section-heading"><div><span>Conditional outlook</span><h3 id="sentiment-outlook-title">다음 1주·1개월</h3></div><small>{outlook.summary}</small></div>
      <div className="sentiment-workbench__outlook-grid">{outlook.horizons.map((horizon) => <HorizonCard horizon={horizon} key={horizon.key} />)}</div>
    </section>
  );
}

export default SentimentOutlookSection;
```

- [ ] **Step 4: Create watch and disclosure components**

Create `WatchConditionsSection.tsx` with the existing `payload.watch_conditions.map` markup and these fixed section labels:

```tsx
import type { WatchCondition } from "./SentimentWorkbench";

function WatchConditionsSection({ items }: { items: WatchCondition[] }) {
  return (
    <section className="sentiment-workbench__watch-section" aria-labelledby="sentiment-watch-title">
      <div className="sentiment-workbench__section-heading"><div><span>Watch</span><h3 id="sentiment-watch-title">다음 관찰 조건</h3></div><small>확률을 대신하는 확인 경로</small></div>
      <div className="sentiment-workbench__watch-grid">
        {items.map((item) => (
          <article data-path={item.key} key={item.key}>
            <span>{item.label}</span>
            <p>{item.condition}</p>
            <small>{item.basis}</small>
          </article>
        ))}
      </div>
    </section>
  );
}

export default WatchConditionsSection;
```

Map each item to `<article data-path={item.key} key={item.key}>` with `item.label`, `item.condition`, and `item.basis`. Do not add run count, saved rows, or refresh status.

Create `SentimentEvidenceDisclosure.tsx` by moving `EvidenceTable` and the existing raw table markup out of the root. Its summary and content must be:

```tsx
type EvidenceCell = number | string | null | undefined;
type EvidenceRow = Record<string, EvidenceCell>;

function toEvidenceRows(rows: object[]): EvidenceRow[] {
  return rows.map((row) => Object.fromEntries(
    Object.entries(row).filter(([, value]) => (
      value === null || value === undefined || typeof value === "string" || typeof value === "number"
    )),
  ) as EvidenceRow);
}
```

Use `toEvidenceRows` for the two structured evidence arrays so nested properties never render as `[object Object]`.

```tsx
<details className="sentiment-workbench__raw-disclosure">
  <summary>방법 · 상세 근거 · 원본 관측 보기</summary>
  <div className="sentiment-workbench__method-note">
    <strong>해석 기준</strong>
    <p>{payload.boundary_note}</p>
    <small>{payload.freshness.detail}</small>
  </div>
  <div className="sentiment-workbench__evidence-columns">
    <EvidenceTable rows={toEvidenceRows(payload.evidence.cnn_components)} title="CNN 구성요소" />
    <EvidenceTable rows={toEvidenceRows(payload.evidence.aaii_comparison)} title="AAII 장기평균 비교" />
  </div>
  <div className="sentiment-workbench__raw-grid">
    <EvidenceTable rows={payload.raw_evidence.sentiment_rows} title="Sentiment rows" />
    <EvidenceTable rows={payload.raw_evidence.component_rows} title="Component rows" />
    <EvidenceTable rows={payload.raw_evidence.history_rows} title="History rows" />
  </div>
</details>
```

Warnings remain inside the disclosure immediately before `.sentiment-workbench__raw-grid`.

- [ ] **Step 5: Complete the root section order**

Replace the old watch and disclosure JSX with:

```tsx
<SentimentOutlookSection outlook={payload.outlook} />
<WatchConditionsSection items={payload.watch_conditions} />
<SentimentEvidenceDisclosure payload={payload} />
```

The complete root order must be Hero → CurrentEvidenceSection → SentimentHistorySection → SentimentOutlookSection → WatchConditionsSection → SentimentEvidenceDisclosure.

- [ ] **Step 6: Run section contract and TypeScript check**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_outlook_and_disclosure_keep_unvalidated_probability_hidden -v
cd app/web/streamlit_components/sentiment_workbench && ./node_modules/.bin/tsc --noEmit
```

Expected: unittest `OK`; TypeScript exits 0.

- [ ] **Step 7: Commit the outlook and disclosure sections**

```bash
git add app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx app/web/streamlit_components/sentiment_workbench/src/SentimentOutlookSection.tsx app/web/streamlit_components/sentiment_workbench/src/WatchConditionsSection.tsx app/web/streamlit_components/sentiment_workbench/src/SentimentEvidenceDisclosure.tsx tests/test_service_contracts.py
git commit -m "Overview 심리 기간 카드와 상세 근거 분리"
```

---

### Task 5: 승인된 surface styling, production build, actual Browser QA와 문서 마감

**Files:**
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css:1-680`
- Rebuild: `app/web/streamlit_components/sentiment_workbench/component_static/index.html`
- Rebuild: `app/web/streamlit_components/sentiment_workbench/component_static/assets/index-*.css`
- Rebuild: `app/web/streamlit_components/sentiment_workbench/component_static/assets/index-*.js`
- Modify: `tests/test_service_contracts.py:8498-8822`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Consumes: all components and contracts from Tasks 1-4.
- Produces: Market Context·Futures Macro-aligned responsive surface, rebuilt production component, desktop/420px QA screenshot.

- [ ] **Step 1: Add failing CSS contracts for the approved visual rules**

Extend the sentiment React style tests:

```python
self.assertIn(".sentiment-workbench__hero", react_style)
self.assertIn("linear-gradient", react_style)
self.assertIn(".sentiment-workbench__source-grid", react_style)
self.assertIn(".sentiment-workbench__history-grid", react_style)
self.assertIn(".sentiment-workbench__outlook-grid", react_style)
self.assertIn("--cnn-source: #9a6a44;", react_style)
self.assertIn("--aaii-source: #0f766e;", react_style)
self.assertNotIn(".sentiment-workbench__axis-card {", react_style)
self.assertNotIn("border-top: 4px solid var(--metric-tone", react_style)
self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr));", react_style)
self.assertIn("@media (max-width: 760px)", react_style)
self.assertIn("@media (max-width: 460px)", react_style)
```

- [ ] **Step 2: Run the CSS contract and confirm RED**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_summary_surface_prioritizes_state_and_freshness \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_driver_surface_groups_cnn_and_aaii_without_next_checks \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_evidence_surface_improves_graphs_and_raw_detail \
  -v
```

Expected: at least one assertion fails against the old compact surface CSS.

- [ ] **Step 3: Apply the approved design tokens and neutral source boxes**

Start the stylesheet with:

```css
:root {
  --ink: #172033;
  --muted: #64748b;
  --line: #dce4ec;
  --surface: #ffffff;
  --soft: #f5f8fa;
  --cnn-source: #9a6a44;
  --aaii-source: #0f766e;
  --berry: #a14f61;
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.sentiment-workbench {
  background: #f7f9fb;
  border: 1px solid var(--line);
  border-radius: 18px;
  color: var(--ink);
  display: grid;
  gap: 18px;
  padding: 18px;
}

.sentiment-workbench__hero {
  background: linear-gradient(135deg, #ffffff 0%, #f3f7f8 58%, #edf4f2 100%);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 24px;
}

.sentiment-workbench__source-grid,
.sentiment-workbench__history-grid,
.sentiment-workbench__outlook-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.sentiment-workbench__source-box {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  min-width: 0;
  padding: 18px;
}
```

Do not add `border-top`, top pseudo-elements, or colored absolute rails to `.sentiment-workbench__source-box`. Use `.source-box--cnn header > b { color: var(--cnn-source); }` and `.source-box--aaii header > b { color: var(--aaii-source); }` for fixed source identity.

- [ ] **Step 4: Add stable history, outlook, disclosure, and responsive layout**

Use these layout constraints:

```css
.sentiment-workbench__history-panel,
.sentiment-workbench__outlook-card,
.sentiment-workbench__raw-disclosure {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  min-width: 0;
}

.sentiment-workbench__line-chart svg {
  display: block;
  height: clamp(280px, 30vw, 360px);
  overflow: visible;
  width: 100%;
}

.sentiment-workbench__outlook-card {
  display: grid;
  gap: 12px;
  min-height: 190px;
  padding: 16px;
}

.sentiment-workbench__outlook-card > header > b {
  background: #eef2f5;
  border-radius: 999px;
  color: var(--muted);
  padding: 5px 8px;
}

@media (max-width: 760px) {
  .sentiment-workbench__hero-grid,
  .sentiment-workbench__source-grid,
  .sentiment-workbench__history-grid,
  .sentiment-workbench__outlook-grid,
  .sentiment-workbench__watch-grid,
  .sentiment-workbench__evidence-columns,
  .sentiment-workbench__raw-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 460px) {
  .sentiment-workbench { border-radius: 12px; padding: 10px; }
  .sentiment-workbench__hero { border-radius: 12px; padding: 18px 14px; }
  .sentiment-workbench__headline { font-size: 1.65rem; }
  .sentiment-workbench__line-chart svg { height: 250px; }
  .sentiment-workbench__aaii-tabs { width: 100%; }
}
```

The AAII tab active state uses `var(--aaii-source)`. CNN chart color remains `#9a6a44`; Bullish teal, Neutral gray dashed, Bearish berry dotted.

- [ ] **Step 5: Run focused Python and source-contract regression**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_component_scaffold_keeps_streamlit_fallback \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_visual_hierarchy_uses_hero_and_balanced_current_evidence \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_evidence_surface_improves_graphs_and_raw_detail \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_outlook_and_disclosure_keep_unvalidated_probability_hidden \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_aaii_direction_uses_spread_without_bearish_gate \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_two_axis_cross_read_marks_cnn_fear_aaii_optimistic_as_divergent \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_cross_read_matrix_handles_alignment_neutral_and_missing \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_axes_include_aaii_long_term_comparison_and_history \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_outlook_stays_unavailable_without_validated_estimator \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_watch_conditions_publish_three_relationship_paths \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_payload_drops_unvalidated_demo_probabilities \
  -v
```

Expected: `OK`, 12 tests passed.

- [ ] **Step 6: Type-check and rebuild the production component**

Run:

```bash
cd app/web/streamlit_components/sentiment_workbench
./node_modules/.bin/tsc --noEmit
npm run build
```

Expected: TypeScript exits 0; Vite reports a successful production build and rewrites `component_static/index.html` plus hashed JS/CSS assets.

- [ ] **Step 7: Run Python compile and diff hygiene checks**

Run from repository root:

```bash
.venv/bin/python -m py_compile app/services/overview/sentiment.py app/web/overview/sentiment_helpers.py app/web/overview/sentiment.py
git diff --check
git status --short
```

Expected: compile and diff check exit 0. Only this task's files plus pre-existing untracked research, `.superpowers/`, and QA images are present.

- [ ] **Step 8: Perform actual desktop Browser QA**

Open `http://localhost:49190/`, enter Overview → 시장 심리, and verify:

1. Hero contains the only cross-read narrative.
2. CNN and AAII current evidence boxes have equal width and no colored rounded top rail.
3. Exactly two graph panels are visible: CNN and AAII.
4. AAII 응답 is selected by default; click AAII Spread and verify only the AAII panel changes.
5. ArrowLeft/ArrowRight changes the focused AAII tab.
6. Each graph line connects visible raw turns with straight segments.
7. CNN hover shows exact date/value; AAII response hover shows Bullish/Neutral/Bearish together; Spread hover shows exact pp.
8. Both 1W and 1M cards show `통계적 판단 불가` and no percentage values.
9. Method/raw disclosure is closed by default and opens without layout breakage.
10. browser console error count is 0 and `document.documentElement.scrollWidth === document.documentElement.clientWidth`.

- [ ] **Step 9: Perform 420px Browser QA and save one generated screenshot**

Set viewport width to 420px and verify Hero, source boxes, graph panels, outlook cards, watch cards, and disclosure stack into one column with no horizontal overflow. Save the screenshot as `overview-sentiment-visual-redesign-qa.png` at repository root and leave it untracked.

- [ ] **Step 10: Align active task and root handoff docs**

Record in task docs:

- implementation status and exact commit sequence in `STATUS.md`;
- two-panel graph, removed rail, and unavailable forecast decision in `NOTES.md`;
- exact unittest/typecheck/build/Browser QA results in `RUNS.md`;
- remaining long-history/PIT estimator dependency in `RISKS.md`.

Add only a 3-5 line milestone to each root handoff log. State that roadmap 1/4 visual polish is complete, roadmap 2/4 long-history quality remains, and 1W/1M probability publication remains gated.

- [ ] **Step 11: Commit production assets and closeout docs**

```bash
git add app/web/streamlit_components/sentiment_workbench/src app/web/streamlit_components/sentiment_workbench/component_static tests/test_service_contracts.py .aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719 .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "Overview 심리 시각 개편 완료"
```

Do not stage `overview-sentiment-visual-redesign-qa.png`, `.superpowers/`, the market-interest research bundle, or older QA PNG files.

- [ ] **Step 12: Final verification before completion claim**

Run:

```bash
git diff HEAD^ --check
git status --short
git log --oneline -6
```

Expected: diff check exits 0; status contains only the preserved untracked artifacts; log shows the task commits in order. Report the focused test count, TypeScript/build result, desktop/420px QA, screenshot path, current roadmap position, and remaining long-history/PIT work.
