# Portfolio Monitoring ETF Position Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `direct_security + stock/etf + fixed_shares` 항목이 같은 append-only 보유 수량 원장과 정정·매수·매도 계약을 사용하도록 만든다.

**Architecture:** `position_events.is_position_ledger_item()`을 수량 원장 shape의 단일 판정기로 두고 command validation, valuation, read model이 공유한다. React는 원장 데이터가 실제로 있는 항목만 수량·입출금 숫자 카드를 보여주며 command eligibility는 기존 `position.eligible`로 따로 제어한다.

**Tech Stack:** Python 3, dataclass/Decimal, pandas, unittest, React 18, TypeScript, Vitest, Streamlit custom component, Vite.

## Global Constraints

- ETF `fixed_shares`만 새 position ledger 대상에 포함한다.
- ETF/stock `fixed_notional`, selected strategy, quant backtest는 position ledger 대상이 아니다.
- 기존 `monitoring_security_position_event` append-only revision과 DB schema를 변경하지 않는다.
- 일부매도 후 최소 1주, 전량매도는 tracking end, exact-date DB close 기본값과 manual override를 유지한다.
- 저장 command를 실행하지 않는 read-only actual Browser QA만 수행한다.
- registry JSONL, run history, 기존 generated QA 파일을 stage하지 않는다.

---

### Task 1: 공통 ETF/주식 수량 원장 eligibility

**Files:**
- Modify: `tests/test_portfolio_monitoring_position_events.py`
- Modify: `app/services/portfolio_monitoring/position_events.py`

**Interfaces:**
- Consumes: `MonitoringItemRecord`의 `source_type`, `instrument_kind`, `funding_mode`, `status`.
- Produces: `is_position_ledger_item(item: MonitoringItemRecord) -> bool`; `assert_position_item_eligible()`이 이 helper를 사용한다.

- [ ] **Step 1: ETF fixed-shares가 eligibility를 통과하는 실패 테스트 작성**

```python
def test_etf_fixed_shares_is_position_eligible(self) -> None:
    from app.services.portfolio_monitoring.position_events import (
        assert_position_item_eligible,
        is_position_ledger_item,
    )

    item = _stock_item(instrument_kind="etf", source_ref="QQQ")
    self.assertTrue(is_position_ledger_item(item))
    assert_position_item_eligible(item)
```

ETF `fixed_notional`과 selected strategy는 `False`이고 validation error를 유지하는 별도 assertion을 추가한다.

- [ ] **Step 2: 실패 원인이 기존 stock-only 검사인지 확인**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_position_events
```

Expected: ETF가 `개별주식` validation error를 발생시켜 FAIL.

- [ ] **Step 3: 최소 공통 helper 구현**

```python
def is_position_ledger_item(item: MonitoringItemRecord) -> bool:
    return (
        item.source_type == "direct_security"
        and item.instrument_kind in {"stock", "etf"}
        and item.funding_mode == "fixed_shares"
    )
```

`_assert_position_item_shape()`은 helper가 `False`일 때 `주식·ETF의 보유 수량 방식에서만 사용할 수 있습니다.`를 발생시킨다.

- [ ] **Step 4: focused test green 확인**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_position_events
```

Expected: PASS.

### Task 2: ETF valuation과 selected position projection

**Files:**
- Modify: `tests/test_portfolio_monitoring_valuation.py`
- Modify: `tests/test_portfolio_monitoring_read_model.py`
- Modify: `app/services/portfolio_monitoring/valuation.py`
- Modify: `app/services/portfolio_monitoring/read_model.py`

**Interfaces:**
- Consumes: Task 1의 `is_position_ledger_item()`.
- Produces: ETF fixed-shares `ItemValueLane.position: PositionLedgerSummary`; workspace `selected_position`/`item_details`의 ETF 수량·가치·event rows.

- [ ] **Step 1: ETF split/dividend/buy/sell valuation 실패 테스트 작성**

`tests/test_portfolio_monitoring_valuation.py`의 `_item()`에 `instrument_kind`와 `source_ref` 인자를 추가하고 아래 계약을 검사한다.

```python
frame = _history(
    [
        {"date": "2026-07-01", "close": 100, "adj_close": 50, "stock_splits": 0, "dividends": 0},
        {"date": "2026-07-02", "close": 50, "adj_close": 50, "stock_splits": 2, "dividends": 0},
        {"date": "2026-07-03", "close": 51, "adj_close": 51, "stock_splits": 0, "dividends": 1},
    ]
)
item = self._item(
    instrument_kind="etf", source_ref="QQQ", input_shares=4,
    entry_close=Decimal("100"), initial_capital=Decimal("400"),
)
lane = valuation.build_direct_security_value_lane(
    item,
    frame,
    position_events=[
        self._event(
            event_id="buy-v1", root_id="buy-root", order=1,
            effect="buy", day="2026-07-02", quantity=1,
            price="50", fee="1",
        ),
        self._event(
            event_id="sell-v1", root_id="sell-root", order=2,
            effect="sell", day="2026-07-03", quantity=2,
            price="51", fee="1",
        ),
    ],
)
self.assertEqual(lane.position.effective_initial_shares, Decimal("4"))
self.assertEqual(lane.position.current_shares, Decimal("7"))
self.assertEqual(Decimal(str(lane.curve.iloc[-1]["dividend_cash"])), Decimal("7.0"))

fixed_notional = self._item(
    instrument_kind="etf", source_ref="QQQ",
    funding_mode="fixed_notional", input_notional=Decimal("400"),
    input_shares=None, initial_capital=Decimal("400"),
)
self.assertIsNone(
    valuation.build_direct_security_value_lane(fixed_notional, frame).position
)
```

ETF `fixed_notional` lane의 `position`은 계속 `None`인지 검사한다.

- [ ] **Step 2: ETF read-model projection 실패 테스트 작성**

`tests/test_portfolio_monitoring_read_model.py`의 `_item()`에 `instrument_kind`를 추가하고 아래 ETF + `_position_lane()` projection을 검사한다.

```python
etf = _item(
    "item-qqq",
    requested=date(2026, 7, 1),
    effective=date(2026, 7, 1),
    capital="1000",
    funding_mode="fixed_shares",
    input_shares=10,
    instrument_kind="etf",
)
workspace = read_model.build_portfolio_monitoring_workspace(
    FakeRepository([PortfolioGroupRecord("group-core", "Core", True)], [etf]),
    active_group_id="group-core",
    selected_item_id=etf.monitoring_item_id,
    lane_loader=_position_lane,
)
self.assertTrue(workspace["selected_position"]["eligible"])
self.assertEqual(workspace["selected_position"]["effective_initial_shares"], Decimal("10"))
self.assertEqual(workspace["selected_position"]["current_shares"], Decimal("12"))
self.assertEqual(workspace["selected_position"]["current_value"], Decimal("1200.0"))
```

- [ ] **Step 3: 두 테스트가 기존 stock-only 조건 때문에 실패하는지 확인**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_valuation tests.test_portfolio_monitoring_read_model
```

Expected: ETF lane `position is None`, selected position `eligible is False`로 FAIL.

- [ ] **Step 4: valuation과 read model을 공통 helper로 전환**

`valuation.build_direct_security_value_lane()`의 `position_eligible` 중복 조건과
`read_model._project_selected_position()`의 stock-only 조건을 `is_position_ledger_item(item)` 호출로 교체한다. 지원 문구는 `주식·ETF의 보유 수량 방식`으로 맞춘다.

- [ ] **Step 5: valuation/read-model green과 기존 stock 회귀 확인**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_position_events tests.test_portfolio_monitoring_valuation tests.test_portfolio_monitoring_read_model
```

Expected: PASS.

### Task 3: 비원장 항목의 빈 숫자 카드 제거와 사용자 문구 정렬

**Files:**
- Modify: `tests/test_portfolio_monitoring_component.py`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx`
- Modify: `app/services/portfolio_monitoring/position_events.py`
- Modify: `app/services/portfolio_monitoring/read_model.py`

**Interfaces:**
- Consumes: `SelectedPositionProjection.current_shares`, `effective_initial_shares`, `eligible`, `reason`.
- Produces: `hasLedger` presentation guard; ended stock/ETF 원장은 read-only로 유지하고 fixed-notional/strategy는 boundary message만 표시한다.

- [ ] **Step 1: source-contract 실패 테스트 작성**

```python
source = Path(
    "app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx"
).read_text(encoding="utf-8")
backend_source = Path(
    "app/services/portfolio_monitoring/position_events.py"
).read_text(encoding="utf-8")
self.assertIn(
    "const hasLedger = position.current_shares != null",
    source,
)
self.assertIn("{hasLedger && (", source)
self.assertIn("주식·ETF", backend_source)
```

- [ ] **Step 2: 실패 확인**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_component
```

Expected: `hasLedger` guard와 새 범위 문구 부재로 FAIL.

- [ ] **Step 3: React presentation 최소 구현**

```tsx
const hasLedger = position.current_shares != null
  && position.effective_initial_shares != null;
```

`hasLedger`일 때만 summary/history를 렌더링한다. action은 계속 `position.eligible`일 때만 보인다. 원장이 없는 항목은 `position.reason`만 표시한다.

- [ ] **Step 4: component와 React tests green 확인**

Run:

```bash
.venv/bin/python -m unittest tests.test_portfolio_monitoring_component
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test -- --run
npm run typecheck
```

Expected: Python component contract, React 36 tests, TypeScript PASS.

### Task 4: production build, actual QA, durable docs와 commit

**Files:**
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/index.html`
- Delete: `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/assets/index-CvNDQ7z3.js`
- Create: Vite가 `component_static/index.html`에 기록한 content-hash JS entry under `app/web/streamlit_components/portfolio_monitoring_workbench/component_static/assets/`
- Modify: `.aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Consumes: Tasks 1-3의 green implementation.
- Produces: 배포 가능한 Vite static asset, QQQ/SOXX actual QA evidence, 현재 계약과 일치하는 durable docs.

- [ ] **Step 1: 전체 관련 자동 검증과 production build**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_position_events \
  tests.test_portfolio_monitoring_valuation \
  tests.test_portfolio_monitoring_read_model \
  tests.test_portfolio_monitoring_component \
  tests.test_portfolio_monitoring_page
.venv/bin/python -m py_compile \
  app/services/portfolio_monitoring/position_events.py \
  app/services/portfolio_monitoring/valuation.py \
  app/services/portfolio_monitoring/read_model.py
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test -- --run
npm run typecheck
npm run build
```

Expected: 모든 command exit 0.

- [ ] **Step 2: actual Browser QA**

`/selected-portfolio-dashboard`에서 QQQ와 SOXX를 차례로 선택해 다음을 확인한다.

- QQQ 현재/최초 수량 4주와 action 두 개 노출.
- SOXX 현재/최초 수량 6주와 action 두 개 노출.
- 현재 평가금액이 상단 개별 가치와 일치.
- fixed-notional/strategy 원장은 빈 숫자 카드 대신 지원 경계만 표시.
- Streamlit Running 0, browser console warning/error 0.

- [ ] **Step 3: 문서와 task closeout 동기화**

초기 `개별주식 전용` 문구를 `주식·ETF fixed-shares`로 바꾸고 DB/schema/브로커 경계가 그대로임을 기록한다.

- [ ] **Step 4: diff 검증과 coherent commit**

Run:

```bash
git diff --check
git status --short
```

Stage only implementation, tests, static asset, task/durable docs. Commit message:

```text
기능: ETF 보유 수량 원장 지원
```
