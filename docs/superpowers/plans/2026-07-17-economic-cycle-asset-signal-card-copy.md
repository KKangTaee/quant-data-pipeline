# Economic Cycle Asset Signal Card Copy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 경제사이클 자산 카드가 미국 경기 신호, 실제 가격, 두 신호 관계를 자산별 문장과 명확한 기간 표기로 보여주게 한다.

**Architecture:** `finance/economic_cycle_interpretation.py`가 기존 계산 상태를 변경하지 않고 사용자 언어 label과 동적 설명 문장을 생성한다. React component는 이 read-model 값을 세 칸 비교 UI와 자산별 현재 환경 제목으로 표시하며, 가격 계산과 provider 경계는 그대로 유지한다.

**Tech Stack:** Python 3.12, pytest, React 18, TypeScript, CSS, Vite, Streamlit custom component

## Global Constraints

- 경제사이클 확률, publication gate, factor score, 5/21/63거래일 가격 계산은 변경하지 않는다.
- 미국 경제 전체 국면을 자산별 현재 상태처럼 반복하지 않는다.
- 확인되지 않은 가격 원인을 추정하거나 자산 가격 전망·목표가격·매매 신호를 만들지 않는다.
- 가격이 없거나 64개 미만이거나 7일 이상 오래되면 비교 대기 상태를 유지한다.
- 기존 `assessment`, `price_context.status`, `alignment` machine state는 유지한다.
- UI/provider 직접 호출을 추가하지 않는다.

---

### Task 1: Asset Signal Labels And Dynamic Summary

**Files:**
- Modify: `finance/economic_cycle_interpretation.py`
- Modify: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: existing `assessment`, complete canonical `drivers`, `price_context.status`, `alignment`
- Produces per row: `current_environment_label`, `macro_signal_label`; price-aware rows also produce `price_direction_label`, `relationship_label`
- Produces: `summary` and `context` as the same dynamic user sentence

- [ ] **Step 1: Write failing user-language contract tests**

```python
def test_price_aware_implications_explain_macro_price_relationship() -> None:
    rows = interpretation.build_market_implications(
        _horizons(), _evidence(), _gold_and_dollar_prices(),
        price_reference_date="2026-07-17",
    )
    gold = next(row for row in rows if row["asset_group"] == "gold")
    dollar = next(row for row in rows if row["asset_group"] == "dollar")

    assert gold["macro_signal_label"] == "금을 지지"
    assert gold["price_direction_label"] == "하락"
    assert gold["relationship_label"] == "서로 다른 방향"
    assert "미국 경기지표에서는" in gold["summary"]
    assert "실제 가격은 최근 1개월과 3개월 모두 하락" in gold["summary"]
    assert dollar["macro_signal_label"] == "달러에 부담"
    assert dollar["price_direction_label"] == "상승"
    assert dollar["relationship_label"] == "서로 다른 방향"
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_service.py -k 'price_aware_implications_explain' -q
```

Expected: FAIL because the four user-language fields and dynamic summary do not exist.

- [ ] **Step 3: Add minimal label maps and summary helpers**

```python
PRICE_DIRECTION_LABELS = {
    "RISING": "상승",
    "FALLING": "하락",
    "MIXED": "방향 혼재",
    "UNAVAILABLE": "확인 대기",
}

RELATIONSHIP_LABELS = {
    "ALIGNED": "같은 방향",
    "DIVERGENCE": "서로 다른 방향",
    "MIXED": "판단 유보",
    "PRICE_PENDING": "비교 대기",
}

CURRENT_ENVIRONMENT_LABELS = {
    "FAVORABLE": "지지 요인 우세",
    "BURDEN": "부담 요인 우세",
    "MIXED": "신호 혼재",
    "INSUFFICIENT": "자료 부족",
}
```

Add per-asset signal labels to `ASSET_CONTEXT`:

```python
"gold": {
    ...,
    "macro_signal_labels": {
        "FAVORABLE": "금을 지지",
        "BURDEN": "금에 부담",
        "MIXED": "금 신호 혼재",
        "INSUFFICIENT": "판단 자료 부족",
    },
},
"dollar": {
    ...,
    "macro_signal_labels": {
        "FAVORABLE": "달러를 지지",
        "BURDEN": "달러에 부담",
        "MIXED": "달러 신호 혼재",
        "INSUFFICIENT": "판단 자료 부족",
    },
},
```

Build price-aware summaries from the complete driver list before reducing the displayed driver list:

```python
summary = _asset_signal_summary(
    asset_group=asset_group,
    assessment=assessment,
    drivers=drivers,
    price_context=price_context,
    alignment=alignment,
)
```

The helper must return these endings:

```python
if price_status == "RISING":
    price_phrase = "실제 가격은 최근 1개월과 3개월 모두 상승"
elif price_status == "FALLING":
    price_phrase = "실제 가격은 최근 1개월과 3개월 모두 하락"
elif price_status == "MIXED":
    price_phrase = "실제 가격은 기간별 방향이 엇갈려"
else:
    price_phrase = "실제 가격 자료가 부족해"
```

- [ ] **Step 4: Add mixed and price-pending edge tests**

```python
def test_signal_labels_keep_mixed_and_price_pending_conservative() -> None:
    assert mixed["current_environment_label"] == "신호 혼재"
    assert mixed["relationship_label"] == "판단 유보"
    assert pending["price_direction_label"] == "확인 대기"
    assert pending["relationship_label"] == "비교 대기"
    assert "상승" not in pending["summary"]
    assert "하락" not in pending["summary"]
```

- [ ] **Step 5: Run service tests and verify GREEN**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest tests/test_economic_cycle_asset_prices.py tests/test_economic_cycle_service.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit interpretation unit**

```bash
git add finance/economic_cycle_interpretation.py tests/test_economic_cycle_service.py
git commit -m "자산별 경기 신호 설명 개선"
```

### Task 2: React Signal Comparison Card

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `tests/test_market_context_economic_cycle.py`
- Rebuild: `app/web/streamlit_components/economic_cycle_workbench/component_static/`

**Interfaces:**
- Consumes: `current_environment_label`, `macro_signal_label`, `price_direction_label`, `relationship_label`, dynamic `summary`
- Produces: three-column price-aware comparison and current-environment title for non-price cards

- [ ] **Step 1: Replace the old source-contract tokens with failing new tokens**

```python
for token in (
    "미국 경기 신호와 시장 가격 비교",
    "현재 환경:",
    "미국 경기 신호",
    "실제 가격",
    "두 신호 관계",
    "향후 확인 조건",
    "1주(5거래일)",
    "1개월(21거래일)",
    "3개월(63거래일)",
):
    assert token in source
assert "경제 국면:" not in source
assert "바뀌는 조건" not in source
```

- [ ] **Step 2: Run the source-contract test and verify RED**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest tests/test_market_context_economic_cycle.py -k full_reading_flow -q
```

Expected: FAIL on the new labels and old-label absence assertions.

- [ ] **Step 3: Extend TypeScript payload types**

```tsx
type MarketImplication = {
  // existing fields
  current_environment_label: string;
  macro_signal_label?: string;
  price_direction_label?: string;
  relationship_label?: string;
};
```

- [ ] **Step 4: Replace price confirmation header with three-column comparison**

```tsx
<div className="signal-comparison-grid">
  <div><span>미국 경기 신호</span><strong>{item.macro_signal_label}</strong></div>
  <div><span>실제 가격</span><strong>{item.price_direction_label}</strong></div>
  <div><span>두 신호 관계</span><strong>{item.relationship_label}</strong></div>
</div>
```

Use the exact price window labels:

```tsx
const windows = [
  ["1주(5거래일)", price.returns.one_week],
  ["1개월(21거래일)", price.returns.one_month],
  ["3개월(63거래일)", price.returns.three_months],
] as const;
```

- [ ] **Step 5: Replace card headings and future-check copy**

```tsx
<strong>
  {priceAware
    ? "미국 경기 신호와 시장 가격 비교"
    : `현재 환경: ${item.current_environment_label}`}
</strong>
```

```tsx
<span>향후 확인 조건</span>
```

The overall price-aware badge must render `item.relationship_label`; non-price cards keep `item.current_environment_label`.

- [ ] **Step 6: Add responsive three-column CSS**

```css
.signal-comparison-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

@media (max-width: 760px) {
  .signal-comparison-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 7: Run React contract tests and build**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest tests/test_market_context_economic_cycle.py -q
cd app/web/streamlit_components/economic_cycle_workbench && npm run build
```

Expected: tests and Vite build PASS.

- [ ] **Step 8: Commit UI unit**

```bash
git add app/web/streamlit_components/economic_cycle_workbench tests/test_market_context_economic_cycle.py
git commit -m "자산 신호 비교 카드 가독성 개선"
```

### Task 3: Actual Verification And Documentation Closeout

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-asset-signal-copy-v1-20260717/PLAN.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-asset-signal-copy-v1-20260717/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-asset-signal-copy-v1-20260717/RUNS.md`
- Create: `.aiworkspace/note/finance/tasks/active/overview-economic-cycle-asset-signal-copy-v1-20260717/RISKS.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

**Interfaces:**
- Verifies: actual DB read model, running Streamlit HTTP surface, desktop/mobile card layout
- Documents: the copy contract without changing price/model semantics

- [ ] **Step 1: Verify actual read-model labels and summaries**

Run:

```bash
PYTHONPATH=. .venv/bin/python - <<'PY'
from app.services.overview.economic_cycle import build_economic_cycle_read_model
m = build_economic_cycle_read_model()
rows = {row["asset_group"]: row for row in m["market_implications"]}
assert rows["gold"]["macro_signal_label"] == "금을 지지"
assert rows["gold"]["price_direction_label"] == "하락"
assert rows["gold"]["relationship_label"] == "서로 다른 방향"
assert rows["dollar"]["macro_signal_label"] == "달러에 부담"
assert rows["dollar"]["price_direction_label"] == "상승"
print(rows["gold"]["summary"])
print(rows["dollar"]["summary"])
PY
```

Expected: assertions PASS and both summaries connect macro conditions to actual price without inventing a cause.

- [ ] **Step 2: Run full focused verification**

Run:

```bash
PYTHONPATH=. uv run --with pytest pytest \
  tests/test_economic_cycle_asset_prices.py \
  tests/test_economic_cycle_service.py \
  tests/test_market_context_economic_cycle.py -q
.venv/bin/python -m py_compile \
  finance/economic_cycle_interpretation.py \
  app/services/overview/economic_cycle.py
git diff --check
curl -sS -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:8502/
```

Expected: all tests PASS, compile/diff check exit 0, HTTP 200.

- [ ] **Step 3: Browser QA**

At desktop and 420px confirm:

- five cards have no horizontal overflow;
- gold/dollar comparison has three readable rows/columns;
- dynamic summary remains under three lines at desktop and wraps without clipping on mobile;
- exact 5/21/63-trading-day labels are visible;
- no new page or console errors.

Capture one screenshot when the configured Browser runtime is available. If unavailable, record the gap in `RISKS.md` and do not claim visual Browser QA passed.

- [ ] **Step 4: Sync task and durable docs**

Record the implemented copy contract, actual gold/dollar labels, verification commands, and remaining visual QA gap. Keep root logs to 3–5 high-signal lines.

- [ ] **Step 5: Commit closeout**

```bash
git add .aiworkspace/note/finance
git commit -m "자산 신호 카드 문구 개선 완료"
```
