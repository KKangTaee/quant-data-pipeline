# Portfolio Monitoring Initial Setting Correction V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** `개별 추적 결과 > 보유내역`에서 최초 요청 시작일과 최초 수량을 함께 append-only로 정정하고, 새 적용 시장일·종가부터 개별/그룹 성과를 일관되게 다시 계산한다.

**Architecture:** 기존 `correct_initial_quantity` command와 `initial_quantity_correction` effect identity는 legacy 저장 호환을 위해 유지한다. Position-event revision에 optional requested/effective start를 추가하고 terminal initial correction에서 유효 초기 계약을 투영한다. Python이 DB-only entry resolution, 거래 선후관계, 가치곡선과 group timeline을 소유하고 React는 입력·resolution request·비교 preview·명시적 save intent만 소유한다.

**Tech Stack:** Python 3, dataclasses, Decimal, pandas, MySQL, Streamlit Python↔React bridge, React 18, TypeScript, Vitest, unittest.

## Global Constraints

- 사용자-facing action과 dialog 명칭은 `최초 설정 정정`이다.
- 적용 대상은 active/data-review `direct_security + stock + fixed_shares`뿐이다.
- `requested_start_date`는 사용자 선택일, `effective_start_date`는 요청일 이후 첫 DB 시장일, `entry_close`는 적용일 저장 종가다.
- UI와 command는 provider를 호출하지 않고 `Ingestion -> DB -> Loader -> Service -> Streamlit bridge -> React`를 유지한다.
- 원본 `monitoring_portfolio_item`, 과거 position revision, registry/saved JSONL은 재작성하지 않는다.
- 기존 `correct_initial_quantity` / `initial_quantity_correction` identity, 추가매수·일부매도, split-first, event order, Modified Dietz `0.5` 계약을 유지한다.
- 새 적용일보다 이른 유효 buy/sell 또는 새 수량으로 invalid해지는 sell이 있으면 전체 command를 rollback한다.
- ETF, fixed notional, selected strategy, quant backtest, full sell, tax lot, broker/account sync는 변경하지 않는다.
- generated Browser QA artifact는 stage하지 않는다.

---

## File Structure

### Modify

- `finance/data/db/schema.py` — position-event optional requested/effective date columns.
- `app/services/portfolio_monitoring/schemas.py` — initial correction requested-date input validation.
- `app/services/portfolio_monitoring/persistence.py` — scoped idempotent column upgrade, row parser, insert binding.
- `app/services/portfolio_monitoring/position_events.py` — effective initial contract projection and trade-date validation.
- `app/services/portfolio_monitoring/commands.py` — server-owned initial entry resolver and revision append.
- `app/services/portfolio_monitoring/valuation.py` — corrected start/close/capital lane and position summary.
- `app/services/portfolio_monitoring/read_model.py` — corrected group timeline and selected-position projection.
- `app/web/final_selected_portfolio_dashboard.py` — DB-only initial-entry resolution, editor recovery, dispatch.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts` — initial-entry/current-initial contracts.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.ts` — date-aware correction draft, validation, payload/recovery.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx` — `최초 설정 정정` form and before/after preview; its source contract remains covered by the existing Python component test because this package has no DOM test runtime.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css` — correction comparison layout.
- Python/Vitest contract tests and durable finance docs listed in Tasks 1-4.

### New Interfaces

```python
@dataclass(frozen=True)
class InitialPositionContract:
    requested_start_date: date
    effective_start_date: date
    entry_close: Decimal
    initial_shares: int
    initial_capital: Decimal


InitialEntryResolver = Callable[
    [MonitoringItemRecord, date, int],
    EntryResolution,
]
```

```ts
export type InitialPositionEntryProjection = {
  status: "IDLE" | "READY" | "MISSING" | string;
  monitoring_item_id: string | null;
  requested_start_date: string | null;
  effective_start_date: string | null;
  entry_close: number | null;
  initial_capital: number | null;
  reason: string | null;
};
```

---

### Task 1: Additive initial-contract persistence and projection

**Files:**
- Modify: `tests/test_portfolio_monitoring_schema.py`
- Modify: `tests/test_portfolio_monitoring_position_events.py`
- Modify: `finance/data/db/schema.py:1210-1237`
- Modify: `app/services/portfolio_monitoring/schemas.py:98-112,209-225`
- Modify: `app/services/portfolio_monitoring/persistence.py:74-94,232-263,303-307,522-556`
- Modify: `app/services/portfolio_monitoring/position_events.py:20-61,113-229`

**Interfaces:**
- Consumes: existing `MonitoringItemRecord`, `PositionEventRecord`, append-only root/revision chain.
- Produces: `InitialPositionContract`, `PositionEventProjection.initial_contract`, optional event requested/effective dates, legacy fallback.

- [x] **Step 1: Write schema/input RED tests**

Add these assertions to `tests/test_portfolio_monitoring_schema.py`:

```python
def test_position_event_schema_carries_optional_initial_contract_dates(self) -> None:
    sql = _load_database_schemas()["monitoring_security_position_event"]
    self.assertIn("requested_start_date DATE NULL", sql)
    self.assertIn("effective_start_date DATE NULL", sql)


def test_initial_correction_accepts_a_requested_start_date(self) -> None:
    schemas = _load_schema_module()
    value = schemas.validate_initial_quantity_correction_input(
        schemas.InitialQuantityCorrectionInput(
            monitoring_item_id="item-amd",
            quantity=42,
            requested_start_date=date(2026, 7, 4),
            note="최초 입력 수정",
        )
    )
    self.assertEqual(value.requested_start_date, date(2026, 7, 4))
```

Add one source/repository contract test that calls `ensure_schema()` with a fake DB containing the old event columns and asserts these exact statements are issued once:

```text
ALTER TABLE `monitoring_security_position_event` ADD COLUMN `requested_start_date` DATE NULL
ALTER TABLE `monitoring_security_position_event` ADD COLUMN `effective_start_date` DATE NULL
```

- [x] **Step 2: Write effective-initial-contract RED tests**

In `tests/test_portfolio_monitoring_position_events.py`, add:

```python
def test_projection_uses_corrected_date_close_and_quantity() -> None:
    item = _stock_item(input_shares=30)
    correction = _event(
        "correct-v1", "correct-root", None, 1, "create",
        "initial_quantity_correction", date(2026, 6, 29), 40, None,
    )
    correction = replace(
        correction,
        requested_start_date=date(2026, 6, 28),
        effective_start_date=date(2026, 6, 29),
        reference_close=Decimal("95"),
    )

    projection = project_position_events(item, [correction])

    self.assertEqual(projection.initial_contract.requested_start_date, date(2026, 6, 28))
    self.assertEqual(projection.initial_contract.effective_start_date, date(2026, 6, 29))
    self.assertEqual(projection.initial_contract.entry_close, Decimal("95"))
    self.assertEqual(projection.initial_contract.initial_shares, 40)
    self.assertEqual(projection.initial_contract.initial_capital, Decimal("3800"))


def test_legacy_quantity_correction_falls_back_to_item_start_contract() -> None:
    item = _stock_item(input_shares=30)
    legacy = _event(
        "correct-v1", "correct-root", None, 1, "create",
        "initial_quantity_correction", date(2026, 7, 1), 20, None,
    )

    projection = project_position_events(item, [legacy])

    self.assertEqual(projection.initial_contract.requested_start_date, item.requested_start_date)
    self.assertEqual(projection.initial_contract.effective_start_date, item.effective_start_date)
    self.assertEqual(projection.initial_contract.entry_close, item.entry_close)
    self.assertEqual(projection.initial_contract.initial_capital, Decimal("2000"))
```

- [x] **Step 3: Run RED and verify the missing contracts**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_schema \
  tests.test_portfolio_monitoring_position_events -v
```

Expected: FAIL because `InitialQuantityCorrectionInput` and `PositionEventRecord` do not accept the dates, DDL lacks both columns, and `PositionEventProjection` has no `initial_contract`.

- [x] **Step 4: Implement schema, parser and idempotent upgrade**

Add to the event DDL immediately after `trade_date`:

```sql
requested_start_date DATE NULL,
effective_start_date DATE NULL,
```

Extend the records without changing existing required constructor arguments:

```python
@dataclass(frozen=True)
class PositionEventRecord:
    # existing required fields unchanged
    created_at: datetime | None = None
    requested_start_date: date | None = None
    effective_start_date: date | None = None
```

Update `_position_event_from_row()` and `insert_position_event()` to read/write both fields. Add a scoped upgrade helper rather than changing the global schema synchronizer:

```python
_POSITION_EVENT_OPTIONAL_COLUMNS = {
    "requested_start_date": "DATE NULL",
    "effective_start_date": "DATE NULL",
}


def _ensure_position_event_optional_columns(db: Any) -> None:
    rows = db.query(
        """
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """,
        [FINANCE_META_DB, "monitoring_security_position_event"],
    )
    existing = {str(row["COLUMN_NAME"]).casefold() for row in rows}
    for name, definition in _POSITION_EVENT_OPTIONAL_COLUMNS.items():
        if name.casefold() not in existing:
            db.execute(
                f"ALTER TABLE `monitoring_security_position_event` "
                f"ADD COLUMN `{name}` {definition}"
            )
```

Call it at the end of `MySQLMonitoringRepository.ensure_schema()`. Do not catch and suppress the ALTER failure.

- [x] **Step 5: Implement initial input and projection**

Extend the input compatibly:

```python
@dataclass(frozen=True)
class InitialQuantityCorrectionInput:
    monitoring_item_id: str
    quantity: int
    note: str = ""
    requested_start_date: date | None = None
```

Reject non-date, non-None values in `validate_initial_quantity_correction_input()`.

Add the projection type and fields:

```python
@dataclass(frozen=True)
class InitialPositionContract:
    requested_start_date: date
    effective_start_date: date
    entry_close: Decimal
    initial_shares: int
    initial_capital: Decimal


@dataclass(frozen=True)
class PositionEventProjection:
    eligible: bool
    eligibility_reason: str | None
    initial_contract: InitialPositionContract
    effective_initial_shares: int | None
    initial_correction: EffectivePositionEvent | None
    trades: tuple[EffectivePositionEvent, ...]
    audit_rows: tuple[PositionAuditRow, ...]
```

`EffectivePositionEvent` must expose optional `requested_start_date` and `effective_start_date`. In `project_position_events()` resolve the contract exactly once:

```python
correction = corrections[0] if corrections else None
initial_shares = correction.quantity if correction else item.input_shares
requested_start = (
    correction.requested_start_date
    if correction and correction.requested_start_date is not None
    else item.requested_start_date
)
effective_start = (
    correction.effective_start_date
    if correction and correction.effective_start_date is not None
    else item.effective_start_date
)
entry_close = (
    correction.reference_close
    if correction and correction.reference_close is not None
    else item.entry_close
)
if effective_start < requested_start or entry_close <= 0:
    raise PositionEventIntegrityError("The effective initial contract is invalid.")
initial_contract = InitialPositionContract(
    requested_start_date=requested_start,
    effective_start_date=effective_start,
    entry_close=entry_close,
    initial_shares=int(initial_shares or 0),
    initial_capital=Decimal(initial_shares or 0) * entry_close,
)
```

- [x] **Step 6: Run GREEN and full Task 1 regression**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_schema \
  tests.test_portfolio_monitoring_position_events -v
.venv/bin/python -m py_compile \
  finance/data/db/schema.py \
  app/services/portfolio_monitoring/schemas.py \
  app/services/portfolio_monitoring/persistence.py \
  app/services/portfolio_monitoring/position_events.py
git diff --check
```

Expected: all focused tests pass; legacy event fixtures remain constructible; compile and diff check exit 0.

- [x] **Step 7: Review and commit Task 1**

```bash
git add \
  finance/data/db/schema.py \
  app/services/portfolio_monitoring/schemas.py \
  app/services/portfolio_monitoring/persistence.py \
  app/services/portfolio_monitoring/position_events.py \
  tests/test_portfolio_monitoring_schema.py \
  tests/test_portfolio_monitoring_position_events.py
git commit -m "기능: 포트폴리오 최초 설정 정정 계약 확장"
```

---

### Task 2: Command validation and corrected valuation/group timeline

**Files:**
- Modify: `tests/test_portfolio_monitoring_commands.py`
- Modify: `tests/test_portfolio_monitoring_valuation.py`
- Modify: `tests/test_portfolio_monitoring_read_model.py`
- Modify: `app/services/portfolio_monitoring/commands.py:20-50,493-582,686-727`
- Modify: `app/services/portfolio_monitoring/position_events.py:230-275`
- Modify: `app/services/portfolio_monitoring/valuation.py:35-66,252-530`
- Modify: `app/services/portfolio_monitoring/read_model.py:204-390,500-590`

**Interfaces:**
- Consumes: Task 1 `InitialPositionContract` and optional event dates.
- Produces: `InitialEntryResolver`, correction revision resolution, corrected `ItemValueLane`, selected-position initial fields, group timeline alignment.

- [x] **Step 1: Write command RED tests**

Add tests that use a resolver returning Monday for a Sunday request:

```python
def resolve_initial(item, requested, quantity):
    self.assertEqual(requested, date(2026, 6, 28))
    self.assertEqual(quantity, 40)
    return commands.EntryResolution(
        effective_start_date=date(2026, 6, 29),
        entry_close=Decimal("95"),
        initial_capital=Decimal("3800"),
    )
```

Assert `execute_correct_initial_quantity()` stores one revision with:

```python
self.assertEqual(saved.requested_start_date, date(2026, 6, 28))
self.assertEqual(saved.effective_start_date, date(2026, 6, 29))
self.assertEqual(saved.trade_date, date(2026, 6, 29))
self.assertEqual(saved.reference_close, Decimal("95"))
self.assertEqual(saved.quantity, 40)
```

Add separate tests for:

- replacing the same initial-correction root preserves `event_order` and audit history;
- same command/date/quantity replays, same command with a different date conflicts;
- corrected effective start `2026-07-10` is rejected when an active buy exists on `2026-07-09`;
- corrected quantity is rejected when a later sell leaves fewer than one share.

- [x] **Step 2: Write valuation/read-model RED tests**

Add a lane test with an original item start of `2026-07-01`, corrected request/effective dates `2026-06-28/29`, entry close `95`, 40 shares and history beginning on `2026-06-29`. Assert:

```python
self.assertEqual(lane.effective_start_date, date(2026, 6, 29))
self.assertEqual(lane.initial_capital, Decimal("3800"))
self.assertEqual(lane.position.requested_start_date, date(2026, 6, 28))
self.assertEqual(lane.position.effective_start_date, date(2026, 6, 29))
self.assertEqual(lane.position.entry_close, Decimal("95"))
```

Add a group test with this corrected lane and a second item starting `2026-07-01`. Assert the first group curve date is `2026-06-28`, the corrected capital is held as pre-market cash until `2026-06-29`, and group invested capital/current P&L use `3800`, not the original item capital.

- [x] **Step 3: Run RED**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_commands \
  tests.test_portfolio_monitoring_valuation \
  tests.test_portfolio_monitoring_read_model -v
```

Expected: FAIL because correction has no resolver, lane still filters on the item start/close, and group timeline still reads item dates.

- [x] **Step 4: Implement server-owned correction resolution**

Add:

```python
InitialEntryResolver = Callable[
    [MonitoringItemRecord, date, int],
    EntryResolution,
]
```

Extend `_append_position_revision()` with optional `requested_start_date` and `resolve_initial_entry`. For `INITIAL_QUANTITY_CORRECTION`, resolve under the locked-item transaction:

```python
if position_effect == PositionEffect.INITIAL_QUANTITY_CORRECTION:
    requested = requested_start_date or item.requested_start_date
    if quantity is None:
        raise CommandValidationError("최초 수량이 필요합니다.")
    if resolve_initial_entry is None:
        resolution = EntryResolution(
            effective_start_date=item.effective_start_date,
            entry_close=item.entry_close,
            initial_capital=Decimal(quantity) * item.entry_close,
        )
    else:
        resolution = resolve_initial_entry(item, requested, quantity)
    event_trade_date = resolution.effective_start_date
    event_requested_start = requested
    event_effective_start = resolution.effective_start_date
    reference_close = resolution.entry_close
else:
    event_trade_date = trade_date
    event_requested_start = None
    event_effective_start = None
```

Only buy/sell uses the old `trade_date < item.effective_start_date` gate. The candidate event receives both initial dates. `execute_correct_initial_quantity()` passes `validated.requested_start_date` and the resolver, and the fingerprint remains `asdict(validated)`.

- [x] **Step 5: Validate trades against the projected start**

Before applying splits in `validate_position_sequence()` add:

```python
for trade in projection.trades:
    if trade.trade_date < projection.initial_contract.effective_start_date:
        raise PositionEventValidationError(
            f"{trade.trade_date.isoformat()} 거래가 새 추적 시작일보다 빠릅니다. "
            "해당 거래를 먼저 수정하거나 취소해 주세요."
        )
```

Keep split and sell validation unchanged after this gate.

- [x] **Step 6: Use the corrected contract in valuation**

Resolve projection before filtering the frame. Use:

```python
projection = project_position_events(item, event_records) if position_eligible else None
initial_contract = projection.initial_contract if projection is not None else None
effective_start = (
    initial_contract.effective_start_date
    if initial_contract is not None
    else item.effective_start_date
)
entry_close = initial_contract.entry_close if initial_contract is not None else item.entry_close
frame = frame.loc[frame["date"] >= pd.Timestamp(effective_start)].copy()
units = (
    Decimal(initial_contract.initial_shares)
    if initial_contract is not None
    else _initial_units(item)
)
initial_capital = (
    initial_contract.initial_capital
    if initial_contract is not None
    else item.initial_capital
)
```

Extend `PositionLedgerSummary` with `requested_start_date`, `effective_start_date`, `entry_close`, `initial_capital`, and return the corrected `effective_start_date` from `ItemValueLane`.

- [x] **Step 7: Align group and selected-position projections**

Add read-model helpers:

```python
def _requested_start(item: MonitoringItemRecord, lane: ItemValueLane | None) -> date:
    if lane is not None and lane.position is not None:
        return lane.position.requested_start_date
    return item.requested_start_date


def _effective_start(item: MonitoringItemRecord, lane: ItemValueLane | None) -> date:
    return lane.effective_start_date if lane is not None else item.effective_start_date
```

Use them in `align_group_value_lanes()` for `start_date`, each timeline start and fallback basis. Add these keys to `_project_selected_position()`:

```python
"requested_start_date": lane.position.requested_start_date.isoformat(),
"effective_start_date": lane.position.effective_start_date.isoformat(),
"entry_close": lane.position.entry_close,
"initial_capital": lane.position.initial_capital,
```

- [x] **Step 8: Run GREEN and regression**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_commands \
  tests.test_portfolio_monitoring_position_events \
  tests.test_portfolio_monitoring_valuation \
  tests.test_portfolio_monitoring_read_model -v
.venv/bin/python -m py_compile \
  app/services/portfolio_monitoring/commands.py \
  app/services/portfolio_monitoring/position_events.py \
  app/services/portfolio_monitoring/valuation.py \
  app/services/portfolio_monitoring/read_model.py
git diff --check
```

Expected: all Task 2 and Task 1 regressions pass; legacy no-event and quantity-only correction tests remain green.

- [x] **Step 9: Review and commit Task 2**

```bash
git add \
  app/services/portfolio_monitoring/commands.py \
  app/services/portfolio_monitoring/position_events.py \
  app/services/portfolio_monitoring/valuation.py \
  app/services/portfolio_monitoring/read_model.py \
  tests/test_portfolio_monitoring_commands.py \
  tests/test_portfolio_monitoring_position_events.py \
  tests/test_portfolio_monitoring_valuation.py \
  tests/test_portfolio_monitoring_read_model.py
git commit -m "기능: 정정 시작일 기준 포트폴리오 성과 재계산"
```

---

### Task 3: Streamlit bridge and React `최초 설정 정정` workflow

**Files:**
- Modify: `tests/test_portfolio_monitoring_page.py`
- Modify: `tests/test_portfolio_monitoring_component.py`
- Modify: `app/web/final_selected_portfolio_dashboard.py:330-350,488-735,852-884,4200-4310`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts:20-90,230-275`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.test.ts`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`

**Interfaces:**
- Consumes: Task 2 corrected selected-position fields and `execute_correct_initial_quantity(..., resolve_initial_entry=...)`.
- Produces: `lookup_initial_position_entry` intent, `initial_position_entry` projection, recovery-safe date editor and final correction command payload.

- [x] **Step 1: Write page RED tests**

Add tests for a Sunday request resolving to Monday without provider fetch:

```python
def test_initial_entry_lookup_resolves_requested_to_effective_market_date(self) -> None:
    frame = pd.DataFrame([
        {"date": "2026-06-29", "close": 95},
        {"date": "2026-06-30", "close": 97},
    ])
    item = SimpleNamespace(source_ref="AMD")
    with patch.object(page, "load_price_history", return_value=frame):
        result = page._resolve_initial_position_entry(
            item, date(2026, 6, 28), 40
        )
    self.assertEqual(result.effective_start_date, date(2026, 6, 29))
    self.assertEqual(result.entry_close, Decimal("95"))
    self.assertEqual(result.initial_capital, Decimal("3800"))
```

Add dispatch/recovery tests asserting `lookup_initial_position_entry` stores selected item, requested date and whitelisted correction state, while `correct_initial_quantity` forwards `requested_start_date` to the service exactly once.

- [x] **Step 2: Write React state RED tests**

Extend `positionEditorState.test.ts`:

```ts
it("builds a date-aware initial-setting correction", () => {
  const correction = {
    ...createPositionEditorDraft("correct_initial", "buy", "correct-1"),
    tradeDate: "2026-06-28",
    quantity: "40",
  };
  expect(buildPositionCommandEvent(correction, "item-amd")).toMatchObject({
    id: "correct_initial_quantity",
    requested_start_date: "2026-06-28",
    quantity: 40,
  });
  expect(validatePositionEditorDraft(correction, {
    currentShares: 40,
    initialEntryReady: true,
  })).toBeNull();
});
```

Add cases for missing date, unresolved/mismatched resolution, and recovery-key change when the correction date changes.

- [x] **Step 3: Write the existing component source-contract RED test**

Extend `tests/test_portfolio_monitoring_component.py` instead of introducing a DOM test dependency that the component package does not currently carry:

```python
def test_initial_setting_correction_exposes_date_lookup_and_comparison(self) -> None:
    component_root = Path(
        "app/web/streamlit_components/portfolio_monitoring_workbench/src"
    )
    source = (component_root / "PositionLedgerPanel.tsx").read_text(
        encoding="utf-8"
    )
    contracts = (component_root / "contracts.ts").read_text(encoding="utf-8")

    self.assertIn("최초 설정 정정", source)
    self.assertIn("새 추적 시작일", source)
    self.assertIn("lookup_initial_position_entry", source)
    self.assertIn("변경 전", source)
    self.assertIn("변경 후", source)
    self.assertIn("requested_start_date", contracts)
    self.assertIn("initial_position_entry", contracts)
```

The reducer test from Step 2 owns the final command payload. The actual click/rerender/preview interaction is verified in Task 4 Browser QA, where a DOM and Streamlit rerun loop are available.

- [x] **Step 4: Run RED**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_page \
  tests.test_portfolio_monitoring_component -v
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench \
  test -- --run src/positionEditorState.test.ts
```

Expected: FAIL because lookup/projection fields, date-aware correction payload and UI do not exist.

- [x] **Step 5: Implement DB-only initial entry resolution and lane loading**

Add:

```python
def _resolve_initial_position_entry(
    item: Any,
    requested_start_date: date,
    quantity: int,
) -> EntryResolution:
    history = load_price_history(
        symbols=[item.source_ref],
        start=requested_start_date.isoformat(),
        timeframe="1d",
    )
    return resolve_direct_security_entry(
        history,
        requested_start_date,
        FundingMode.FIXED_SHARES,
        quantity,
    )
```

In `lane_loader()` load events first, call `project_position_events()` for eligible direct stocks, and load history from `projection.initial_contract.effective_start_date`. Do the same in `validate_position_candidate()` using the candidate records.

Parse correction input as:

```python
value = InitialQuantityCorrectionInput(
    monitoring_item_id=item_id,
    quantity=int(event.get("quantity") or 0),
    note=str(event.get("note") or ""),
    requested_start_date=date.fromisoformat(
        str(event.get("requested_start_date") or "")
    ),
)
```

Pass `resolve_initial_entry=_resolve_initial_position_entry` to the command.

- [x] **Step 6: Implement initial-entry projection and dispatch**

Add separate workspace state rather than overloading trade-close price semantics:

```python
workspace["initial_position_entry"] = {
    "status": "IDLE",
    "monitoring_item_id": selected_item_id,
    "requested_start_date": initial_requested_date_text,
    "effective_start_date": None,
    "entry_close": None,
    "initial_capital": None,
    "reason": None,
}
```

When a requested date exists, resolve it for the selected item and current effective initial shares. On exception return `MISSING` with the concrete message. Add dispatch:

```python
if event_id == "lookup_initial_position_entry":
    services.session_state["portfolio_monitoring_selected_item_id"] = str(
        event.get("monitoring_item_id") or ""
    )
    services.session_state["portfolio_monitoring_initial_requested_start_date"] = str(
        event.get("requested_start_date") or ""
    )
    editor_state = _sanitize_position_editor_state(
        event.get("position_editor_state")
    )
    if editor_state is not None:
        services.session_state["portfolio_monitoring_position_editor_state"] = editor_state
    return None
```

- [x] **Step 7: Implement TypeScript contracts and editor state**

Add `InitialPositionEntryProjection`, the four selected-position initial fields, workspace `initial_position_entry`, and event contracts:

```ts
| {
    id: "lookup_initial_position_entry";
    monitoring_item_id: string;
    requested_start_date: string;
    position_editor_state: PositionEditorRecoveryState;
    nonce: string;
  }
| {
    id: "correct_initial_quantity";
    command_id: string;
    monitoring_item_id: string;
    requested_start_date: string;
    quantity: number;
    note: string;
    nonce: string;
  }
```

For correction mode, require `draft.tradeDate`, include it as `requested_start_date`, and include `initialEntryReady` in validation context. `buildPositionEditorRecovery()` continues using `trade_date` as the transient correction requested date, preserving the existing recovery schema.

- [x] **Step 8: Implement `최초 설정 정정` form and preview**

Change the action/title and prefill:

```ts
setDraft({
  ...next,
  tradeDate: position.requested_start_date ?? "",
  quantity: String(position.effective_initial_shares ?? ""),
});
```

For correction date changes emit `lookup_initial_position_entry`; leave buy/sell using `lookup_position_trade_close`. Render:

```tsx
<label>
  새 추적 시작일
  <input
    type="date"
    value={draft.tradeDate}
    onChange={(event) => requestInitialEntry(
      changeTradeDate(draft, event.target.value)
    )}
  />
</label>
```

The preview must show two columns with these exact labels: `변경 전`, `변경 후`, `요청일`, `적용일`, `시작 종가`, `최초 투자금`. Disable save unless the READY projection belongs to the selected item and requested date. Use the note `새 적용일부터 전체 거래 이력과 성과를 다시 계산합니다.`

- [x] **Step 9: Run GREEN, typecheck and build**

```bash
.venv/bin/python -m unittest \
  tests.test_portfolio_monitoring_page \
  tests.test_portfolio_monitoring_component -v
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench test -- --run
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run typecheck
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run build
.venv/bin/python -m py_compile app/web/final_selected_portfolio_dashboard.py
git diff --check
```

Expected: Python page/component contracts and all React tests pass; typecheck/build and compile exit 0.

- [x] **Step 10: Review and commit Task 3**

```bash
git add \
  app/web/final_selected_portfolio_dashboard.py \
  app/web/streamlit_components/portfolio_monitoring_workbench/src \
  app/web/streamlit_components/portfolio_monitoring_workbench/component_static \
  tests/test_portfolio_monitoring_page.py \
  tests/test_portfolio_monitoring_component.py
git commit -m "개선: 개별종목 최초 시작일과 수량 정정 지원"
```

---

### Task 4: Migration, full QA and durable documentation closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/PORTFOLIO_MONITORING_DATA_CONTRACT.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/PORTFOLIO_MONITORING_MIGRATION_AND_QA.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: task `DESIGN.md`, `PLAN.md`, `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Generate only: `portfolio-monitoring-initial-setting-correction-qa.png`

**Interfaces:**
- Verifies: Tasks 1-3 full behavior, schema upgrade, no user-data rewrite, responsive correction flow.
- Produces: deployed current-state contract, QA evidence, docs/task closeout.

- [x] **Step 1: Run full Portfolio Monitoring automation**

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -q
.venv/bin/python -m py_compile \
  finance/data/db/schema.py \
  app/services/portfolio_monitoring/*.py \
  app/web/final_selected_portfolio_dashboard.py
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench test -- --run
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run typecheck
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run build
git diff --check
```

Record exact Python/React counts in `RUNS.md`.

- [x] **Step 2: Verify and apply the additive schema upgrade**

Before mutation, read and record the event table row count and current column list. Run `MySQLMonitoringRepository.ensure_schema()` once, then repeat it. Verify:

- the original row count is unchanged;
- both date columns exist as nullable DATE;
- the second call emits no additional ALTER;
- no group/item/command/event row was updated or deleted;
- registry/saved JSONL checksums are unchanged.

If DB configuration is unavailable, do not claim migration completion; record the exact gap in `RISKS.md` and keep automated fake-DB idempotency evidence.

- [x] **Step 3: Run actual and isolated Browser QA**

Use the in-app Browser according to the repository rule.

Actual route read-only checks at desktop and 420px:

- `최초 설정 정정` action is visible for eligible direct-stock fixed-shares;
- dialog opens with current requested date and quantity;
- date input is visible and layout has no horizontal overflow;
- ETF/strategy/fixed-notional boundaries remain unchanged;
- console error count is zero.

Use the isolated component/Streamlit harness for a mutation interaction:

- change request from `2026-07-01` to Sunday `2026-06-28`;
- READY preview shows applied Monday `2026-06-29`, `$95`, `$3,800` for 40 shares;
- save event contains requested date and quantity;
- a fixture with a `2026-06-27` request and an active `2026-06-26` trade shows the blocking reason;
- same selected item context remains after rerun.

Save one screenshot as `portfolio-monitoring-initial-setting-correction-qa.png`; do not stage it. Reset the temporary viewport and close QA tabs after verification.

- [x] **Step 4: Synchronize durable docs**

Update the smallest current-state set:

- data contract: optional event dates, legacy fallback, projected initial contract, no row rewrite;
- architecture/UI flow: `최초 설정 정정` and DB-only resolution/recalculation path;
- runbook: additive-column pre/post counts, idempotent repeat and Browser checks;
- Project Map/Roadmap/Index: task completion and direct-stock-only boundary;
- task docs: exact RED/GREEN runs, migration status, Browser assertions, residual gaps;
- root logs: 3-5 line milestone and durable decision.

- [x] **Step 5: Run final fresh verification**

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_portfolio_monitoring_*.py' -q
.venv/bin/python -m unittest tests.test_portfolio_monitoring_docs -q
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench test -- --run
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run typecheck
npm --prefix app/web/streamlit_components/portfolio_monitoring_workbench run build
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
git diff --check
git status --short
```

Expected: all tests/builds pass; only intended code/docs/static assets are tracked; QA PNG and pre-existing local artifacts remain untracked.

- [x] **Step 6: Commit closeout**

```bash
git add \
  .aiworkspace/note/finance/docs/INDEX.md \
  .aiworkspace/note/finance/docs/PROJECT_MAP.md \
  .aiworkspace/note/finance/docs/ROADMAP.md \
  .aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md \
  .aiworkspace/note/finance/docs/data/PORTFOLIO_MONITORING_DATA_CONTRACT.md \
  .aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md \
  .aiworkspace/note/finance/docs/runbooks/PORTFOLIO_MONITORING_MIGRATION_AND_QA.md \
  .aiworkspace/note/finance/tasks/active/portfolio-monitoring-initial-setting-correction-v1-20260721 \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git commit -m "문서: 포트폴리오 최초 설정 정정 계약과 QA 정리"
```

## Plan Self-Review

- Spec coverage: requested/effective date semantics, entry close, append-only audit, legacy fallback, group recalculation, trade conflict, responsive UI, schema migration and docs closeout are mapped to Tasks 1-4.
- Isolation: each task ends with focused tests and a coherent commit; no unrelated portfolio/backtest behavior is introduced.
- Type consistency: Python uses `requested_start_date`, `effective_start_date`, `entry_close`, `initial_capital`; React uses the same snake-case JSON fields. The transient correction date remains `trade_date` only inside `PositionEditorRecoveryState` for backward-compatible rerun recovery.
- Placeholder scan: no TBD/TODO/“similar to” steps remain; every code step names exact signatures, fields, commands and expected outcomes.
