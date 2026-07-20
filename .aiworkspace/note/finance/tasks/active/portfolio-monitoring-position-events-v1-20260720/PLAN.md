# Portfolio Monitoring Position Events V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 직접 등록한 미국 개별주식의 최초 수량 정정과 실제 추가매수·일부매도를 audit-preserving 원장으로 저장하고, DB 종가 기본값·수동 체결가 override·현금흐름 조정 성과를 Portfolio Monitoring에서 관리한다.

**Architecture:** 기존 `monitoring_portfolio_item`은 최초 입력 provenance로 유지하고 새 `monitoring_security_position_event` append-only revision chain이 유효 포지션을 투영한다. Python service가 event validity, exact-date close, split-first 수량, Modified Dietz 가치곡선과 read model을 소유하고 React는 입력·preview·ledger 표현만 소유한다. 이벤트 없는 기존 stock/ETF/strategy는 현재 결과를 유지한다.

**Tech Stack:** Python 3, dataclasses, Decimal, pandas, MySQL, Streamlit Python↔React component bridge, React 18, TypeScript, Vitest, pytest.

## Global Constraints

- 적용 대상은 `source_type=direct_security`, `instrument_kind=stock`, `funding_mode=fixed_shares`, status `active|data_review`뿐이다.
- ETF, fixed-notional, Final Review selected strategy, quant backtest, full sell, tax lot, group cash account, broker/order/auto-rebalance는 범위 밖이다.
- 거래일 DB close를 execution price 기본값으로 자동 입력하고 사용자가 수정할 수 있다.
- 서버는 exact-date DB close와 최종 execution price의 Decimal equality로 `db_close_default|manual_override`를 판정한다.
- buy는 외부 입금, partial sell은 외부 출금이고 sell 뒤 최소 1주를 유지한다.
- 같은 날 거래는 root-stable `event_order`, split은 거래보다 먼저 적용한다.
- 거래 시각이 없으므로 일별 Modified Dietz cash-flow weight는 `0.5`다.
- UI/provider 직접 fetch는 금지하고 `Ingestion -> DB -> Loader -> Service -> Streamlit bridge -> React`를 유지한다.
- registry/saved JSONL, legacy command, generated QA artifact와 기존 사용자 데이터를 재작성하지 않는다.
- 각 task는 RED 확인, 최소 구현, focused GREEN, regression, coherent Korean commit 순서로 끝낸다.

---

## File Structure

### Create

- `app/services/portfolio_monitoring/position_events.py` — revision chain 해석, effective event projection, eligibility와 수량 sequence 검증.
- `tests/test_portfolio_monitoring_position_events.py` — append-only projection, same-day order, replace/void, eligibility tests.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.ts` — 거래 editor draft, close default recovery, validation, command payload.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.test.ts` — close default/manual override/date reset/partial sell payload tests.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx` — 보유내역 summary, 최초 수량 정정, trade editor, chronological ledger.

### Modify

- `finance/data/db/schema.py` — additive `monitoring_security_position_event` DDL.
- `app/services/portfolio_monitoring/schemas.py` — event/action/effect/price-source enums와 command input validators.
- `app/services/portfolio_monitoring/persistence.py` — event record parser와 MySQL list/get/insert/next-order methods.
- `app/services/portfolio_monitoring/commands.py` — 네 개 idempotent position command와 transactional revalidation.
- `app/services/portfolio_monitoring/valuation.py` — event-aware direct stock lane, cashflow columns, Modified Dietz unit index.
- `app/services/portfolio_monitoring/read_model.py` — flow-aware group KPI, selected position projection, workspace schema v2.
- `app/services/portfolio_monitoring/__init__.py` — public command/domain exports.
- `app/web/final_selected_portfolio_dashboard.py` — event loading, exact close lookup, editor recovery, command bridge/dispatch.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts` — position summary/event/close projection contracts.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx` — selected detail에 `PositionLedgerPanel` 연결.
- `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css` — desktop/mobile action/editor/ledger layout.
- `tests/test_portfolio_monitoring_schema.py` — DDL contract.
- `tests/test_portfolio_monitoring_commands.py` — idempotency, conflict, unsupported target, later-sell invalidation.
- `tests/test_portfolio_monitoring_valuation.py` — quantity/cashflow/split/dividend/Modified Dietz/no-event regression.
- `tests/test_portfolio_monitoring_read_model.py` — group cashflow KPI와 selected position JSON.
- `tests/test_portfolio_monitoring_page.py` — close lookup recovery와 four-command dispatch.
- `tests/test_portfolio_monitoring_component.py` — action-first UI/source contract.
- Durable/task/root docs listed in Task 8.

## Test Fixture Contracts

`tests/test_portfolio_monitoring_position_events.py` creates the following concrete helpers once and reuses them in Tasks 1-3:

```python
def stock_item(*, input_shares: int = 30) -> MonitoringItemRecord:
    return MonitoringItemRecord(
        monitoring_item_id="item-amd",
        portfolio_group_id="group-core",
        source_type="direct_security",
        source_ref="AMD",
        instrument_kind="stock",
        requested_start_date=date(2026, 7, 1),
        effective_start_date=date(2026, 7, 1),
        funding_mode="fixed_shares",
        input_notional=None,
        input_shares=input_shares,
        entry_close=Decimal("100"),
        initial_capital=Decimal(input_shares) * Decimal("100"),
    )


def etf_item() -> MonitoringItemRecord:
    return replace(stock_item(), instrument_kind="etf", source_ref="SPY")


def event(
    event_id: str,
    root_id: str,
    supersedes: str | None,
    order: int,
    action: str,
    effect: str,
    day: str,
    quantity: int | None,
    price: str | None,
) -> PositionEventRecord:
    return PositionEventRecord(
        position_event_id=event_id,
        root_event_id=root_id,
        supersedes_event_id=supersedes,
        monitoring_item_id="item-amd",
        event_order=order,
        event_action=action,
        position_effect=effect,
        trade_date=date.fromisoformat(day),
        quantity=quantity,
        execution_price=Decimal(price) if price is not None else None,
        reference_close=Decimal(price) if price is not None else None,
        execution_price_source="db_close_default" if price is not None else None,
        fee_usd=Decimal("0"),
        note="",
        command_id=f"command-{event_id}",
    )


def effective_trade(
    effect: str,
    day: str,
    *,
    quantity: int,
    order: int,
) -> EffectivePositionEvent:
    return EffectivePositionEvent(
        root_event_id=f"{effect}-{order}",
        current_event_id=f"{effect}-{order}-v1",
        event_order=order,
        position_effect=effect,
        trade_date=date.fromisoformat(day),
        quantity=quantity,
        execution_price=Decimal("100"),
        reference_close=Decimal("100"),
        execution_price_source="db_close_default",
        fee_usd=Decimal("0"),
        note="",
    )


def projection_with_trades(
    *,
    initial_shares: int,
    trades: list[EffectivePositionEvent],
) -> PositionEventProjection:
    return PositionEventProjection(
        eligible=True,
        eligibility_reason=None,
        effective_initial_shares=initial_shares,
        initial_correction=None,
        trades=tuple(trades),
        audit_rows=(),
    )


def projection_with_sell(*, quantity: int) -> PositionEventProjection:
    return projection_with_trades(
        initial_shares=30,
        trades=[effective_trade("sell", "2026-07-10", quantity=quantity, order=1)],
    )
```

`tests/test_portfolio_monitoring_commands.py` extends its existing `FakeRepository` with event state and rollback coverage:

```python
self.position_events = []
snapshot = copy.deepcopy((self.groups, self.items, self.commands, self.position_events))

def list_position_events(self, monitoring_item_id, *, for_update=False):
    return [row for row in self.position_events if row.monitoring_item_id == monitoring_item_id]

def get_position_event(self, position_event_id, *, for_update=False):
    return next((row for row in self.position_events if row.position_event_id == position_event_id), None)

def next_position_event_order(self, monitoring_item_id):
    orders = [row.event_order for row in self.position_events if row.monitoring_item_id == monitoring_item_id]
    return max(orders, default=0) + 1

def insert_position_event(self, record):
    self.position_events.append(record)
    return record
```

Import the validation error and add the candidate validator used by rollback tests:

```python
from app.services.portfolio_monitoring.position_events import (
    PositionEventValidationError,
    project_position_events,
    validate_position_sequence,
)


def validate_candidate_sequence(item, records):
    projection = project_position_events(item, records)
    validate_position_sequence(item, projection, split_factors={})
```

Add this concrete builder to the existing command test class:

```python
def _stored_direct_item(self, persistence, *, shares=30):
    return persistence.MonitoringItemRecord(
        monitoring_item_id="item-direct",
        portfolio_group_id="group-core",
        source_type="direct_security",
        source_ref="AMD",
        instrument_kind="stock",
        requested_start_date=date(2026, 7, 1),
        effective_start_date=date(2026, 7, 1),
        funding_mode="fixed_shares",
        input_notional=None,
        input_shares=shares,
        entry_close=Decimal("100"),
        initial_capital=Decimal(shares) * Decimal("100"),
    )


def _position_event(
    self,
    persistence,
    *,
    event_id,
    root_id,
    supersedes=None,
    order=1,
    action="create",
    effect="buy",
    quantity=5,
    price="100",
    command_id=None,
):
    return persistence.PositionEventRecord(
        position_event_id=event_id,
        root_event_id=root_id,
        supersedes_event_id=supersedes,
        monitoring_item_id="item-direct",
        event_order=order,
        event_action=action,
        position_effect=effect,
        trade_date=date(2026, 7, 10),
        quantity=quantity,
        execution_price=Decimal(price) if price is not None else None,
        reference_close=Decimal(price) if price is not None else None,
        execution_price_source="db_close_default" if price is not None else None,
        fee_usd=Decimal("0"),
        note="",
        command_id=command_id or f"command-{event_id}",
    )
```

The rollback branch restores all four snapshots. Valuation tests reuse existing `self._item()` and `_history()` and add this local helper:

```python
def _event(
    self,
    *,
    event_id,
    root_id,
    order,
    effect,
    day,
    quantity,
    price=None,
    fee="0",
):
    return PositionEventRecord(
        position_event_id=event_id,
        root_event_id=root_id,
        supersedes_event_id=None,
        monitoring_item_id="item-aapl",
        event_order=order,
        event_action="create",
        position_effect=effect,
        trade_date=date.fromisoformat(day),
        quantity=quantity,
        execution_price=Decimal(price) if price is not None else None,
        reference_close=Decimal(price) if price is not None else None,
        execution_price_source="db_close_default" if price is not None else None,
        fee_usd=Decimal(fee),
        note="",
        command_id=f"command-{event_id}",
    )
```

Read-model tests add `from dataclasses import replace`, import `PositionLedgerSummary`, and replace the existing `_item()` signature with the following backward-compatible parameters while preserving all existing callers:

```python
def _item(
    item_id: str,
    *,
    requested: date,
    effective: date,
    capital: str = "100",
    status: str = "active",
    end: date | None = None,
    exit_value: str | None = None,
    funding_mode: str = "fixed_notional",
    input_shares: int | None = None,
) -> MonitoringItemRecord:
    initial_capital = Decimal(capital)
    return MonitoringItemRecord(
        monitoring_item_id=item_id,
        portfolio_group_id="group-core",
        source_type="direct_security",
        source_ref=item_id.upper(),
        instrument_kind="stock",
        requested_start_date=requested,
        effective_start_date=effective,
        funding_mode=funding_mode,
        input_notional=initial_capital if funding_mode == "fixed_notional" else None,
        input_shares=input_shares,
        entry_close=Decimal("10"),
        initial_capital=initial_capital,
        tracking_end_requested_date=end,
        tracking_end_effective_date=end,
        exit_value=Decimal(exit_value) if exit_value is not None else None,
        status=status,
    )
```

Then add:

```python
def _position_lane(item: MonitoringItemRecord) -> ItemValueLane:
    frame = pd.DataFrame({
        "date": pd.to_datetime(["2026-07-01", "2026-07-02", "2026-07-03"]),
        "total_value": [1000.0, 1500.0, 1200.0],
        "external_flow": [0.0, 501.0, -299.0],
        "flow_adjusted_index": [1.0, 0.9992, 0.9984],
        "data_status": ["active", "active", "active"],
    })
    return ItemValueLane(
        monitoring_item_id=item.monitoring_item_id,
        source_ref=item.source_ref,
        effective_start_date=date(2026, 7, 1),
        latest_usable_date=date(2026, 7, 3),
        initial_capital=Decimal("1000"),
        status="active",
        curve=frame,
        review=CorporateActionReview("READY", Decimal("0"), Decimal("0"), ()),
        position=PositionLedgerSummary(
            eligible=True,
            effective_initial_shares=Decimal("10"),
            current_shares=Decimal("12"),
            cumulative_contributions=Decimal("1501"),
            cumulative_withdrawals=Decimal("299"),
            pnl=Decimal("-2"),
            event_rows=({
                "root_event_id": "buy-root",
                "current_event_id": "buy-v1",
                "status": "active",
                "position_effect": "buy",
                "trade_date": "2026-07-02",
                "event_order": 1,
                "quantity": 5,
                "execution_price": Decimal("100"),
                "reference_close": Decimal("100"),
                "execution_price_source": "db_close_default",
                "fee_usd": Decimal("1"),
                "note": "",
                "shares_after": Decimal("15"),
            },),
        ),
    )
```

Page tests reuse `_services()` and add the four service callables to the returned `SimpleNamespace`.

---

### Task 1: Additive Event Schema And Repository

**Files:**
- Modify: `finance/data/db/schema.py:1179-1227`
- Modify: `app/services/portfolio_monitoring/schemas.py:17-65`
- Modify: `app/services/portfolio_monitoring/persistence.py:23-183,300-448`
- Modify: `tests/test_portfolio_monitoring_schema.py`
- Create: `tests/test_portfolio_monitoring_position_events.py`

**Interfaces:**
- Produces: `PositionEventAction`, `PositionEffect`, `ExecutionPriceSource` enums.
- Produces: `PositionEventRecord` and repository methods `list_position_events()`, `get_position_event()`, `next_position_event_order()`, `insert_position_event()`.
- Consumes: existing `MonitoringRepository.transaction()` and MySQL connection reuse.

- [ ] **Step 1: Write the failing DDL and repository contract tests**

```python
def test_position_event_schema_is_append_only_and_queryable(self) -> None:
    sql = PORTFOLIO_MONITORING_SCHEMAS["monitoring_security_position_event"]
    self.assertIn("CREATE TABLE IF NOT EXISTS monitoring_security_position_event", sql)
    self.assertIn("position_event_id VARCHAR(64) PRIMARY KEY", sql)
    self.assertIn("root_event_id VARCHAR(64) NOT NULL", sql)
    self.assertIn("event_order BIGINT NOT NULL", sql)
    self.assertIn("reference_close DECIMAL(24,8) NULL", sql)
    self.assertIn("execution_price_source ENUM('db_close_default','manual_override') NULL", sql)
    self.assertIn("UNIQUE KEY uk_monitoring_position_event_command (command_id)", sql)
    self.assertIn("KEY ix_monitoring_position_event_item_date", sql)
```

```python
def test_repository_protocol_exposes_position_event_operations(self) -> None:
    required = {
        "list_position_events",
        "get_position_event",
        "next_position_event_order",
        "insert_position_event",
    }
    self.assertTrue(required.issubset(MonitoringRepository.__dict__))
```

- [ ] **Step 2: Run RED tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_schema.py tests/test_portfolio_monitoring_position_events.py -q
```

Expected: FAIL because the DDL key, enums, record and repository methods do not exist.

- [ ] **Step 3: Add the exact enums and immutable persistence record**

```python
class PositionEventAction(str, Enum):
    CREATE = "create"
    REPLACE = "replace"
    VOID = "void"


class PositionEffect(str, Enum):
    INITIAL_QUANTITY_CORRECTION = "initial_quantity_correction"
    BUY = "buy"
    SELL = "sell"


class ExecutionPriceSource(str, Enum):
    DB_CLOSE_DEFAULT = "db_close_default"
    MANUAL_OVERRIDE = "manual_override"
```

```python
@dataclass(frozen=True)
class PositionEventRecord:
    position_event_id: str
    root_event_id: str
    supersedes_event_id: str | None
    monitoring_item_id: str
    event_order: int
    event_action: str
    position_effect: str
    trade_date: date
    quantity: int | None
    execution_price: Decimal | None
    reference_close: Decimal | None
    execution_price_source: str | None
    fee_usd: Decimal
    note: str
    command_id: str
    created_at: datetime | None = None
```

- [ ] **Step 4: Add the additive MySQL table**

```sql
CREATE TABLE IF NOT EXISTS monitoring_security_position_event (
  position_event_id VARCHAR(64) PRIMARY KEY,
  root_event_id VARCHAR(64) NOT NULL,
  supersedes_event_id VARCHAR(64) NULL,
  monitoring_item_id VARCHAR(64) NOT NULL,
  event_order BIGINT NOT NULL,
  event_action ENUM('create','replace','void') NOT NULL,
  position_effect ENUM('initial_quantity_correction','buy','sell') NOT NULL,
  trade_date DATE NOT NULL,
  quantity BIGINT NULL,
  execution_price DECIMAL(24,8) NULL,
  reference_close DECIMAL(24,8) NULL,
  execution_price_source ENUM('db_close_default','manual_override') NULL,
  fee_usd DECIMAL(24,8) NOT NULL DEFAULT 0,
  note VARCHAR(500) NOT NULL DEFAULT '',
  command_id VARCHAR(64) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_monitoring_position_event_command (command_id),
  KEY ix_monitoring_position_event_item_date (monitoring_item_id, trade_date, event_order),
  KEY ix_monitoring_position_event_root (root_event_id, created_at),
  KEY ix_monitoring_position_event_supersedes (supersedes_event_id)
);
```

- [ ] **Step 5: Implement parser and transaction-reusing repository methods**

```python
def list_position_events(
    self,
    monitoring_item_id: str,
    *,
    for_update: bool = False,
) -> list[PositionEventRecord]:
    suffix = " FOR UPDATE" if for_update else ""
    with self._connection() as db:
        rows = db.query(
            "SELECT * FROM monitoring_security_position_event "
            "WHERE monitoring_item_id = %s "
            f"ORDER BY trade_date, event_order, created_at, position_event_id{suffix}",
            [monitoring_item_id],
        )
    return [record for row in rows if (record := _position_event_from_row(row)) is not None]


def next_position_event_order(self, monitoring_item_id: str) -> int:
    with self._connection() as db:
        rows = db.query(
            "SELECT COALESCE(MAX(event_order), 0) AS max_order "
            "FROM monitoring_security_position_event WHERE monitoring_item_id = %s FOR UPDATE",
            [monitoring_item_id],
        )
    return int(rows[0]["max_order"] or 0) + 1
```

- [ ] **Step 6: Run focused GREEN tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_schema.py tests/test_portfolio_monitoring_position_events.py -q
```

Expected: PASS.

- [ ] **Step 7: Run existing persistence regressions**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_legacy_import.py tests/test_portfolio_monitoring_commands.py -q
```

Expected: PASS with no existing item/group/legacy behavior changes.

- [ ] **Step 8: Commit Task 1**

```bash
git add finance/data/db/schema.py app/services/portfolio_monitoring/schemas.py app/services/portfolio_monitoring/persistence.py tests/test_portfolio_monitoring_schema.py tests/test_portfolio_monitoring_position_events.py
git commit -m "기능: 포트폴리오 종목 거래 원장 스키마 추가"
```

---

### Task 2: Effective Revision Projection And Sequence Validation

**Files:**
- Create: `app/services/portfolio_monitoring/position_events.py`
- Modify: `tests/test_portfolio_monitoring_position_events.py`
- Modify: `app/services/portfolio_monitoring/__init__.py`

**Interfaces:**
- Consumes: `MonitoringItemRecord`, `PositionEventRecord`.
- Produces: `EffectivePositionEvent`, `PositionEventProjection`.
- Produces: `project_position_events(item, records) -> PositionEventProjection`.
- Produces: `assert_position_item_eligible(item) -> None` and `validate_position_sequence(item, projection, split_factors) -> None`.

- [ ] **Step 1: Write failing projection tests for correction, replace, void and stable same-day order**

```python
def test_projection_uses_terminal_revision_without_reordering_the_root(self) -> None:
    records = [
        event("buy-v1", "buy-root", None, 1, "create", "buy", "2026-07-10", 5, "100"),
        event("sell-v1", "sell-root", None, 2, "create", "sell", "2026-07-10", 3, "110"),
        event("buy-v2", "buy-root", "buy-v1", 1, "replace", "buy", "2026-07-10", 7, "99"),
    ]

    projection = project_position_events(stock_item(input_shares=30), records)

    self.assertEqual(projection.effective_initial_shares, 30)
    self.assertEqual([row.root_event_id for row in projection.trades], ["buy-root", "sell-root"])
    self.assertEqual([row.quantity for row in projection.trades], [7, 3])
```

```python
def test_void_removes_business_effect_but_retains_audit_row(self) -> None:
    records = [
        event("buy-v1", "buy-root", None, 1, "create", "buy", "2026-07-10", 5, "100"),
        event("buy-void", "buy-root", "buy-v1", 1, "void", "buy", "2026-07-10", None, None),
    ]
    projection = project_position_events(stock_item(input_shares=30), records)
    self.assertEqual(projection.trades, ())
    self.assertEqual(projection.audit_rows[-1].status, "voided")
```

- [ ] **Step 2: Run RED projection tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_position_events.py -q
```

Expected: FAIL because `position_events.py` and projection types do not exist.

- [ ] **Step 3: Implement immutable terminal-revision resolution**

```python
@dataclass(frozen=True)
class EffectivePositionEvent:
    root_event_id: str
    current_event_id: str
    event_order: int
    position_effect: str
    trade_date: date
    quantity: int
    execution_price: Decimal | None
    reference_close: Decimal | None
    execution_price_source: str | None
    fee_usd: Decimal
    note: str


class PositionEventIntegrityError(RuntimeError):
    """Raised when an append-only revision chain is internally inconsistent."""


class PositionEventValidationError(ValueError):
    """Raised when an otherwise valid event would create an invalid position."""


@dataclass(frozen=True)
class PositionAuditRow:
    position_event_id: str
    root_event_id: str
    status: str
    position_effect: str
    trade_date: date
    event_order: int


@dataclass(frozen=True)
class PositionQuantitySnapshot:
    root_event_id: str
    shares_before: Decimal
    shares_after: Decimal


@dataclass(frozen=True)
class PositionEventProjection:
    eligible: bool
    eligibility_reason: str | None
    effective_initial_shares: int | None
    initial_correction: EffectivePositionEvent | None
    trades: tuple[EffectivePositionEvent, ...]
    audit_rows: tuple[PositionAuditRow, ...]


def project_position_events(
    item: MonitoringItemRecord,
    records: Sequence[PositionEventRecord],
) -> PositionEventProjection:
    assert_position_item_eligible(item)
    terminal_by_root = _terminal_revisions(records)
    effective = [row for row in terminal_by_root.values() if row.event_action != "void"]
    corrections = [row for row in effective if row.position_effect == "initial_quantity_correction"]
    if len(corrections) > 1:
        raise PositionEventIntegrityError("Only one initial quantity correction root is allowed.")
    initial_shares = corrections[0].quantity if corrections else item.input_shares
    trades = tuple(
        _effective_event(row)
        for row in sorted(
            (row for row in effective if row.position_effect in {"buy", "sell"}),
            key=lambda value: (value.trade_date, value.event_order, value.root_event_id),
        )
    )
    return PositionEventProjection(
        eligible=True,
        eligibility_reason=None,
        effective_initial_shares=initial_shares,
        initial_correction=_effective_event(corrections[0]) if corrections else None,
        trades=trades,
        audit_rows=_audit_rows(records, terminal_by_root),
    )
```

- [ ] **Step 4: Add failing eligibility and split-first quantity sequence tests**

```python
def test_sequence_applies_split_before_same_day_sell(self) -> None:
    projection = projection_with_trades(
        initial_shares=30,
        trades=[effective_trade("sell", "2026-07-15", quantity=50, order=1)],
    )
    snapshots = validate_position_sequence(
        stock_item(input_shares=30),
        projection,
        split_factors={date(2026, 7, 15): Decimal("2")},
    )
    self.assertEqual(snapshots[-1].shares_after, Decimal("10"))
```

```python
def test_sequence_rejects_full_or_oversell_and_non_stock_targets(self) -> None:
    with self.assertRaisesRegex(PositionEventValidationError, "최소 1주"):
        validate_position_sequence(
            stock_item(input_shares=30),
            projection_with_sell(quantity=30),
            split_factors={},
        )
    with self.assertRaisesRegex(PositionEventValidationError, "개별주식"):
        assert_position_item_eligible(etf_item())
```

- [ ] **Step 5: Implement eligibility and deterministic quantity snapshots**

```python
def assert_position_item_eligible(item: MonitoringItemRecord) -> None:
    if not (
        item.source_type == "direct_security"
        and item.instrument_kind == "stock"
        and item.funding_mode == "fixed_shares"
        and item.status in {"active", "data_review"}
    ):
        raise PositionEventValidationError("활성 개별주식의 보유 수량 방식에서만 사용할 수 있습니다.")


def validate_position_sequence(
    item: MonitoringItemRecord,
    projection: PositionEventProjection,
    split_factors: Mapping[date, Decimal],
) -> tuple[PositionQuantitySnapshot, ...]:
    shares = Decimal(projection.effective_initial_shares or 0)
    snapshots: list[PositionQuantitySnapshot] = []
    applied_split_dates: set[date] = set()
    for trade in projection.trades:
        for split_date in sorted(split_factors):
            if split_date in applied_split_dates or split_date > trade.trade_date:
                continue
            shares *= split_factors[split_date]
            applied_split_dates.add(split_date)
        before = shares
        shares += Decimal(trade.quantity) if trade.position_effect == "buy" else -Decimal(trade.quantity)
        if shares < 1:
            raise PositionEventValidationError("일부매도 후 최소 1주를 유지해야 합니다.")
        snapshots.append(PositionQuantitySnapshot(trade.root_event_id, before, shares))
    return tuple(snapshots)
```

- [ ] **Step 6: Run focused GREEN tests and public export check**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_position_events.py -q
.venv/bin/python -m py_compile app/services/portfolio_monitoring/position_events.py
```

Expected: PASS.

- [ ] **Step 7: Commit Task 2**

```bash
git add app/services/portfolio_monitoring/position_events.py app/services/portfolio_monitoring/__init__.py tests/test_portfolio_monitoring_position_events.py
git commit -m "기능: 종목 거래 이벤트 투영과 수량 검증 추가"
```

---

### Task 3: Idempotent Correction, Trade, Replace And Void Commands

**Files:**
- Modify: `app/services/portfolio_monitoring/schemas.py`
- Modify: `app/services/portfolio_monitoring/commands.py`
- Modify: `app/services/portfolio_monitoring/__init__.py`
- Modify: `tests/test_portfolio_monitoring_commands.py`
- Modify: `tests/test_portfolio_monitoring_position_events.py`

**Interfaces:**
- Produces: `InitialQuantityCorrectionInput`, `PositionTradeInput`, `ReplacePositionTradeInput`, `VoidPositionTradeInput`.
- Produces: `execute_correct_initial_quantity()`, `execute_record_position_trade()`, `execute_replace_position_trade()`, `execute_void_position_trade()`.
- Consumes callbacks `resolve_reference_close(item, trade_date) -> Decimal` and `validate_candidate(item, records) -> None`.

- [ ] **Step 1: Write failing command tests for price provenance and replay**

```python
def test_record_trade_uses_close_default_and_replays_same_command(self) -> None:
    commands, persistence, schemas = _load_modules()
    repository = FakeRepository()
    item = self._stored_direct_item(persistence)
    repository.items[item.monitoring_item_id] = item
    value = schemas.PositionTradeInput(
        monitoring_item_id=item.monitoring_item_id,
        position_effect=schemas.PositionEffect.BUY,
        trade_date=date(2026, 7, 10),
        quantity=5,
        execution_price=Decimal("160"),
        fee_usd=Decimal("0"),
        note="추가매수",
    )
    command = self._command(
        schemas,
        "trade-1",
        schemas.CommandType.RECORD_POSITION_TRADE,
        target_id=item.monitoring_item_id,
        payload={"trade_date": "2026-07-10", "quantity": 5, "execution_price": "160"},
    )

    first = commands.execute_record_position_trade(
        repository,
        command,
        value,
        resolve_reference_close=lambda item, day: Decimal("160"),
        validate_candidate=lambda item, records: None,
    )
    replay = commands.execute_record_position_trade(
        repository,
        command,
        value,
        resolve_reference_close=lambda item, day: Decimal("160"),
        validate_candidate=lambda item, records: None,
    )

    self.assertFalse(first.replayed)
    self.assertTrue(replay.replayed)
    self.assertEqual(repository.position_events[0].execution_price_source, "db_close_default")
```

```python
def test_manual_price_is_preserved_with_reference_close(self) -> None:
    commands, persistence, schemas = _load_modules()
    repository = FakeRepository()
    item = self._stored_direct_item(persistence)
    repository.items[item.monitoring_item_id] = item
    commands.execute_record_position_trade(
        repository,
        self._command(
            schemas,
            "trade-manual",
            schemas.CommandType.RECORD_POSITION_TRADE,
            target_id=item.monitoring_item_id,
            payload={"trade_date": "2026-07-10", "quantity": 5, "execution_price": "159.25"},
        ),
        schemas.PositionTradeInput(
            monitoring_item_id=item.monitoring_item_id,
            position_effect=schemas.PositionEffect.BUY,
            trade_date=date(2026, 7, 10),
            quantity=5,
            execution_price=Decimal("159.25"),
        ),
        resolve_reference_close=lambda current, day: Decimal("160"),
        validate_candidate=lambda current, records: None,
    )
    row = repository.position_events[0]
    self.assertEqual(row.execution_price, Decimal("159.25"))
    self.assertEqual(row.reference_close, Decimal("160"))
    self.assertEqual(row.execution_price_source, "manual_override")
```

- [ ] **Step 2: Run RED command tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_commands.py tests/test_portfolio_monitoring_position_events.py -q
```

Expected: FAIL because command types, inputs and handlers are missing.

- [ ] **Step 3: Add command types and strict input validators**

```python
class CommandType(str, Enum):
    CREATE_GROUP = "create_group"
    RENAME_GROUP = "rename_group"
    ADD_ITEM = "add_item"
    END_ITEM = "end_item"
    REOPEN_ITEM = "reopen_item"
    CORRECT_INITIAL_QUANTITY = "correct_initial_quantity"
    RECORD_POSITION_TRADE = "record_position_trade"
    REPLACE_POSITION_TRADE = "replace_position_trade"
    VOID_POSITION_TRADE = "void_position_trade"
    IMPORT_LEGACY = "import_legacy"
```

```python
@dataclass(frozen=True)
class PositionTradeInput:
    monitoring_item_id: str
    position_effect: PositionEffect
    trade_date: date
    quantity: int
    execution_price: Decimal
    fee_usd: Decimal = Decimal("0")
    note: str = ""


@dataclass(frozen=True)
class InitialQuantityCorrectionInput:
    monitoring_item_id: str
    quantity: int
    note: str = ""


@dataclass(frozen=True)
class ReplacePositionTradeInput:
    monitoring_item_id: str
    root_event_id: str
    expected_event_id: str
    position_effect: PositionEffect
    trade_date: date
    quantity: int
    execution_price: Decimal
    fee_usd: Decimal = Decimal("0")
    note: str = ""


@dataclass(frozen=True)
class VoidPositionTradeInput:
    monitoring_item_id: str
    root_event_id: str
    expected_event_id: str
```

Validation must reject bool/non-integer/`<1` quantity, non-buy/sell effect, nonpositive execution price, negative fee, sell `quantity*price-fee <= 0`, note over 500 chars, missing IDs and non-date values.

```python
def validate_position_trade_input(value: PositionTradeInput) -> PositionTradeInput:
    item_id = str(value.monitoring_item_id or "").strip()
    note = str(value.note or "").strip()
    if not item_id:
        raise ValueError("monitoring item id is required.")
    if value.position_effect not in {PositionEffect.BUY, PositionEffect.SELL}:
        raise ValueError("position trade must be buy or sell.")
    if not isinstance(value.trade_date, date):
        raise ValueError("trade date is required.")
    if isinstance(value.quantity, bool) or not isinstance(value.quantity, int) or value.quantity < 1:
        raise ValueError("quantity must be an integer of at least 1.")
    price = _positive_decimal(value.execution_price)
    if price is None:
        raise ValueError("execution price must be positive.")
    fee = _nonnegative_decimal(value.fee_usd)
    if fee is None:
        raise ValueError("fee must be nonnegative.")
    if value.position_effect == PositionEffect.SELL and Decimal(value.quantity) * price - fee <= 0:
        raise ValueError("sell withdrawal must be positive after fees.")
    if len(note) > 500:
        raise ValueError("note must contain at most 500 characters.")
    return replace(value, monitoring_item_id=item_id, execution_price=price, fee_usd=fee, note=note)
```

- [ ] **Step 4: Implement one transactional append helper used by all four commands**

```python
def _append_position_revision(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
    *,
    event_action: PositionEventAction,
    position_effect: PositionEffect,
    trade_date: date,
    quantity: int | None,
    execution_price: Decimal | None,
    fee_usd: Decimal,
    note: str,
    root_event_id: str | None,
    expected_event_id: str | None,
    resolve_reference_close: ReferenceCloseResolver | None,
    validate_candidate: CandidateValidator,
) -> CommandResult:
    def mutate() -> CommandResult:
        item = repository.get_item(str(command.target_id or ""), for_update=True)
        if item is None:
            raise CommandValidationError("Monitoring item not found.")
        assert_position_item_eligible(item)
        current = repository.list_position_events(item.monitoring_item_id, for_update=True)
        order, root_id, supersedes = _resolve_revision_identity(
            repository,
            item,
            current,
            event_action,
            root_event_id,
            expected_event_id,
        )
        reference_close = (
            resolve_reference_close(item, trade_date)
            if resolve_reference_close is not None and position_effect in {PositionEffect.BUY, PositionEffect.SELL}
            else None
        )
        price_source = (
            ExecutionPriceSource.DB_CLOSE_DEFAULT.value
            if execution_price == reference_close
            else ExecutionPriceSource.MANUAL_OVERRIDE.value
        ) if reference_close is not None else None
        candidate = PositionEventRecord(
            position_event_id=f"position_event_{uuid4().hex[:16]}",
            root_event_id=root_id,
            supersedes_event_id=supersedes,
            monitoring_item_id=item.monitoring_item_id,
            event_order=order,
            event_action=event_action.value,
            position_effect=position_effect.value,
            trade_date=trade_date,
            quantity=quantity,
            execution_price=execution_price,
            reference_close=reference_close,
            execution_price_source=price_source,
            fee_usd=fee_usd,
            note=note,
            command_id=command.command_id,
        )
        validate_candidate(item, [*current, candidate])
        repository.insert_position_event(candidate)
        return CommandResult(CommandStatus.SUCCEEDED, command.command_id, root_id, False, "보유내역을 저장했습니다.")
    return _execute(repository, command, _command_fingerprint(command, dict(command.payload)), mutate)
```

- [ ] **Step 5: Write failing replace/void stale-revision and later-sell invalidation tests**

```python
def test_replace_rejects_stale_terminal_revision(self) -> None:
    commands, persistence, schemas = _load_modules()
    repository = FakeRepository()
    item = self._stored_direct_item(persistence)
    repository.items[item.monitoring_item_id] = item
    repository.position_events = [
        self._position_event(persistence, event_id="buy-v1", root_id="buy-root"),
        self._position_event(
            persistence,
            event_id="buy-v2",
            root_id="buy-root",
            supersedes="buy-v1",
            action="replace",
            quantity=6,
        ),
    ]
    with self.assertRaisesRegex(commands.CommandConflictError, "최신 거래 기록"):
        commands.execute_replace_position_trade(
            repository,
            self._command(
                schemas,
                "replace-stale",
                schemas.CommandType.REPLACE_POSITION_TRADE,
                target_id=item.monitoring_item_id,
                payload={"root_event_id": "buy-root", "expected_event_id": "buy-v1"},
            ),
            schemas.ReplacePositionTradeInput(
                monitoring_item_id=item.monitoring_item_id,
                root_event_id="buy-root",
                expected_event_id="buy-v1",
                position_effect=schemas.PositionEffect.BUY,
                trade_date=date(2026, 7, 10),
                quantity=7,
                execution_price=Decimal("100"),
            ),
            resolve_reference_close=lambda item, day: Decimal("100"),
            validate_candidate=lambda item, records: None,
        )
```

```python
def test_initial_correction_rolls_back_when_later_sell_becomes_invalid(self) -> None:
    commands, persistence, schemas = _load_modules()
    repository = FakeRepository()
    item = self._stored_direct_item(persistence, shares=30)
    repository.items[item.monitoring_item_id] = item
    repository.position_events = [
        self._position_event(
            persistence,
            event_id="sell-v1",
            root_id="sell-root",
            effect="sell",
            quantity=25,
        )
    ]
    with self.assertRaisesRegex(PositionEventValidationError, "최소 1주"):
        commands.execute_correct_initial_quantity(
            repository,
            self._command(
                schemas,
                "correct-invalid",
                schemas.CommandType.CORRECT_INITIAL_QUANTITY,
                target_id=item.monitoring_item_id,
                payload={"quantity": 20},
            ),
            schemas.InitialQuantityCorrectionInput(item.monitoring_item_id, 20, "입력 오류 수정"),
            validate_candidate=validate_candidate_sequence,
        )
    self.assertEqual(len(repository.position_events), 1)
```

- [ ] **Step 6: Implement replace/void terminal checks and candidate revalidation**

The replace and void handlers must require both `root_event_id` and `expected_event_id`, preserve `event_order`, set `supersedes_event_id=expected_event_id`, and call `validate_candidate()` before insert. Initial correction must create one root once and replace that root on later corrections.

- [ ] **Step 7: Run command GREEN and existing lifecycle regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_commands.py tests/test_portfolio_monitoring_position_events.py -q
```

Expected: PASS including existing add/end/reopen tests.

- [ ] **Step 8: Commit Task 3**

```bash
git add app/services/portfolio_monitoring/schemas.py app/services/portfolio_monitoring/commands.py app/services/portfolio_monitoring/__init__.py tests/test_portfolio_monitoring_commands.py tests/test_portfolio_monitoring_position_events.py
git commit -m "기능: 개별종목 수량 정정과 거래 명령 추가"
```

---

### Task 4: Transaction-Aware Direct Stock Valuation

**Files:**
- Modify: `app/services/portfolio_monitoring/valuation.py:32-51,214-320`
- Modify: `tests/test_portfolio_monitoring_valuation.py`

**Interfaces:**
- Consumes: `PositionEventRecord`, `project_position_events()`.
- Modifies: `build_direct_security_value_lane(item, history, position_events=())` while preserving the two-argument call.
- Produces: lane curve columns `external_flow`, `cumulative_contributions`, `cumulative_withdrawals`, `flow_adjusted_index`.
- Produces: `PositionLedgerSummary` on `ItemValueLane.position`.

- [ ] **Step 1: Write failing no-event and initial-correction regression tests**

```python
def test_no_event_lane_is_identical_to_existing_fixed_share_result(self) -> None:
    valuation = _load_valuation()
    item = self._item(input_shares=30, entry_close=Decimal("100"), initial_capital=Decimal("3000"))
    frame = _history([
        {"date": "2026-07-01", "close": 100, "adj_close": 100},
        {"date": "2026-07-02", "close": 110, "adj_close": 110},
    ])
    legacy = valuation.build_direct_security_value_lane(item, frame)
    explicit = valuation.build_direct_security_value_lane(item, frame, position_events=[])
    pd.testing.assert_frame_equal(legacy.curve, explicit.curve)
    self.assertEqual(legacy.initial_capital, explicit.initial_capital)
```

```python
def test_initial_quantity_correction_recomputes_from_original_entry_close(self) -> None:
    valuation = _load_valuation()
    item = self._item(input_shares=30, entry_close=Decimal("100"), initial_capital=Decimal("3000"))
    frame = _history([
        {"date": "2026-07-01", "close": 100, "adj_close": 100},
        {"date": "2026-07-02", "close": 110, "adj_close": 110},
    ])
    lane = valuation.build_direct_security_value_lane(
        item,
        frame,
        position_events=[self._event(
            event_id="correct-v1", root_id="correct-root", order=1,
            effect="initial_quantity_correction", day="2026-07-01", quantity=20,
        )],
    )
    self.assertEqual(lane.initial_capital, Decimal("2000"))
    self.assertEqual(lane.position.current_shares, Decimal("20"))
    self.assertEqual(Decimal(str(lane.curve.iloc[-1]["total_value"])), Decimal("2200"))
```

- [ ] **Step 2: Run RED valuation tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_valuation.py -q
```

Expected: FAIL because the third argument, position summary and cashflow columns do not exist.

- [ ] **Step 3: Extend the lane contract without changing existing no-event column values**

```python
@dataclass(frozen=True)
class PositionLedgerSummary:
    eligible: bool
    effective_initial_shares: Decimal | None
    current_shares: Decimal | None
    cumulative_contributions: Decimal
    cumulative_withdrawals: Decimal
    pnl: Decimal | None
    event_rows: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ItemValueLane:
    monitoring_item_id: str
    source_ref: str
    effective_start_date: date
    latest_usable_date: date
    initial_capital: Decimal
    status: str
    curve: pd.DataFrame
    review: CorporateActionReview
    readiness: Any | None = None
    position: PositionLedgerSummary | None = None
```

- [ ] **Step 4: Write failing buy/sell/fee/Modified Dietz tests**

```python
def test_buy_and_partial_sell_adjust_cashflow_without_counting_flows_as_profit(self) -> None:
    valuation = _load_valuation()
    item = self._item(input_shares=10, entry_close=Decimal("100"), initial_capital=Decimal("1000"))
    frame = _history([
        {"date": "2026-07-01", "close": 100, "adj_close": 100},
        {"date": "2026-07-02", "close": 100, "adj_close": 100},
        {"date": "2026-07-03", "close": 100, "adj_close": 100},
    ])
    lane = valuation.build_direct_security_value_lane(
        item,
        frame,
        position_events=[
            self._event(event_id="buy-v1", root_id="buy-root", order=1, effect="buy", day="2026-07-02", quantity=5, price="100", fee="1"),
            self._event(event_id="sell-v1", root_id="sell-root", order=2, effect="sell", day="2026-07-03", quantity=3, price="100", fee="1"),
        ],
    )
    self.assertEqual(lane.position.current_shares, Decimal("12"))
    self.assertEqual(lane.position.cumulative_contributions, Decimal("1501"))
    self.assertEqual(lane.position.cumulative_withdrawals, Decimal("299"))
    self.assertEqual(lane.position.pnl, Decimal("-2"))
    self.assertLess(Decimal(str(lane.curve.iloc[-1]["flow_adjusted_index"])), Decimal("1"))
```

```python
def test_daily_modified_dietz_uses_half_day_flow_weight(self) -> None:
    valuation = _load_valuation()
    result = valuation.modified_dietz_return(
        begin_value=Decimal("3000"),
        end_value=Decimal("4100"),
        net_external_flow=Decimal("1000"),
    )
    self.assertEqual(result.quantize(Decimal("0.000001")), Decimal("0.028571"))
```

- [ ] **Step 5: Implement split-first event application and flow-adjusted index**

```python
def modified_dietz_return(
    begin_value: Decimal,
    end_value: Decimal,
    net_external_flow: Decimal,
) -> Decimal | None:
    denominator = begin_value + Decimal("0.5") * net_external_flow
    if denominator <= 0:
        return None
    return (end_value - begin_value - net_external_flow) / denominator
```

For each date: apply the stored split factor, apply effective trades by `event_order`, accrue existing dividend cash, calculate close market value, record positive buy/negative sell `external_flow`, and chain `flow_adjusted_index *= 1 + daily_return`. If a return denominator is invalid, set lane status `data_review` and leave that day/index unavailable rather than fabricating a return.

- [ ] **Step 6: Add split-day, dividend and sell-sequence tests**

```python
def test_split_precedes_same_day_trade_and_dividend_uses_effective_units(self) -> None:
    valuation = _load_valuation()
    item = self._item(input_shares=30, entry_close=Decimal("50"), initial_capital=Decimal("1500"))
    frame = _history([
        {"date": "2026-07-14", "close": 50, "adj_close": 25, "stock_splits": 0, "dividends": 0},
        {"date": "2026-07-15", "close": 25, "adj_close": 25, "stock_splits": 2, "dividends": 1},
    ])
    lane = valuation.build_direct_security_value_lane(
        item,
        frame,
        position_events=[self._event(event_id="sell-v1", root_id="sell-root", order=1, effect="sell", day="2026-07-15", quantity=50, price="25")],
    )
    self.assertEqual(lane.position.current_shares, Decimal("10"))
    self.assertGreaterEqual(Decimal(str(lane.curve.iloc[-1]["dividend_cash"])), Decimal("10"))
```

- [ ] **Step 7: Run valuation GREEN and selected-strategy regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_valuation.py tests/test_portfolio_monitoring_selected_strategy.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit Task 4**

```bash
git add app/services/portfolio_monitoring/valuation.py tests/test_portfolio_monitoring_valuation.py
git commit -m "기능: 거래 현금흐름 기반 종목 가치곡선 계산"
```

---

### Task 5: Flow-Aware Group Metrics And Selected Position Read Model

**Files:**
- Modify: `app/services/portfolio_monitoring/read_model.py:18-290,358-533`
- Modify: `tests/test_portfolio_monitoring_read_model.py`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts`

**Interfaces:**
- Consumes: enriched `ItemValueLane.position` and curve cashflow/index columns.
- Produces: `portfolio_monitoring_workspace_v2`.
- Produces: group metrics `gross_contributions`, `gross_withdrawals`, `net_contributions` and exact flow-aware P&L/return/MDD/CAGR.
- Produces: top-level `selected_position` projection.

- [ ] **Step 1: Write failing group KPI tests**

```python
def test_group_metrics_exclude_external_flows_from_return_and_profit(self) -> None:
    read_model = _load_read_model()
    item = _item(
        "amd",
        requested=date(2026, 7, 1),
        effective=date(2026, 7, 1),
        capital="1000",
        funding_mode="fixed_shares",
        input_shares=10,
    )
    result = read_model.align_group_value_lanes(
        [item],
        {"amd": _position_lane(item)},
    )
    self.assertEqual(result.metrics.gross_contributions, Decimal("1501"))
    self.assertEqual(result.metrics.gross_withdrawals, Decimal("299"))
    self.assertEqual(result.metrics.net_contributions, Decimal("1202"))
    self.assertEqual(result.metrics.pnl, Decimal("-2"))
    self.assertNotEqual(result.metrics.total_return, result.metrics.pnl / result.metrics.gross_contributions)
```

```python
def test_eventless_group_metrics_match_v1_values(self) -> None:
    read_model = _load_read_model()
    first = _item("a", requested=date(2026, 7, 1), effective=date(2026, 7, 1), capital="10000")
    second = _item("b", requested=date(2026, 7, 1), effective=date(2026, 7, 1), capital="10000")
    result = read_model.align_group_value_lanes(
        [first, second],
        {
            "a": _lane(first, [("2026-07-01", 10000), ("2026-07-18", 10500)]),
            "b": _lane(second, [("2026-07-01", 10000), ("2026-07-18", 10500)]),
        },
    )
    self.assertEqual(result.metrics.invested_capital, Decimal("20000"))
    self.assertEqual(result.metrics.current_value, Decimal("21000"))
    self.assertEqual(result.metrics.pnl, Decimal("1000"))
    self.assertEqual(result.metrics.total_return, Decimal("0.05"))
```

- [ ] **Step 2: Run RED read-model tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_read_model.py -q
```

Expected: FAIL because flow-aware metrics and selected projection do not exist.

- [ ] **Step 3: Extend group curve and metrics**

```python
@dataclass(frozen=True)
class GroupMetrics:
    invested_capital: Decimal
    gross_contributions: Decimal
    gross_withdrawals: Decimal
    net_contributions: Decimal
    current_value: Decimal
    pnl: Decimal
    total_return: Decimal | None
    mdd: Decimal | None
    cagr: Decimal | None
    observation_days: int
    short_window: bool
    total_contribution: Decimal
    downside_contribution: Decimal
    contribution_by_item: dict[str, Decimal]
```

Build group rows with additive `external_flow` and `unit_value` columns while preserving every existing no-event column value. Compute dollar P&L as `current_value + gross_withdrawals - gross_contributions`; compute total return/MDD/CAGR from group `unit_value`; use lane position P&L for `contribution_by_item`. Keep `invested_capital` equal to gross contributions so the existing metric remains meaningful and unchanged when no events exist. `_value_at()` and the invested-capital sum must use `lane.initial_capital` when a corrected eligible lane exists, otherwise `item.initial_capital`.

- [ ] **Step 4: Write failing selected-position projection and schema-version tests**

```python
def test_workspace_projects_only_selected_eligible_position(self) -> None:
    read_model = _load_read_model()
    group = PortfolioGroupRecord("group-core", "Core", True)
    stock = _item(
        "item-amd",
        requested=date(2026, 7, 1),
        effective=date(2026, 7, 1),
        capital="1000",
        funding_mode="fixed_shares",
        input_shares=10,
    )
    strategy = replace(
        _item("item-strategy", requested=date(2026, 7, 1), effective=date(2026, 7, 1)),
        source_type="selected_strategy",
        instrument_kind="strategy",
    )
    repository = FakeRepository([group], [stock, strategy])
    workspace = read_model.build_portfolio_monitoring_workspace(
        repository,
        active_group_id="group-core",
        selected_item_id="item-amd",
        lane_loader=lambda item: _position_lane(item) if item.monitoring_item_id == "item-amd" else _lane(item, [("2026-07-01", 100)]),
    )
    self.assertEqual(workspace["schema_version"], "portfolio_monitoring_workspace_v2")
    self.assertTrue(workspace["selected_position"]["eligible"])
    self.assertEqual(workspace["selected_position"]["current_shares"], Decimal("12"))
    self.assertEqual(workspace["selected_position"]["event_rows"][0]["position_effect"], "buy")
```

- [ ] **Step 5: Implement workspace v2 and selected item projection**

```python
WORKSPACE_SCHEMA_VERSION = "portfolio_monitoring_workspace_v2"
MONITORING_VALUE_METHOD = {
    "basis": "oldest_latest_usable_date_among_active_lanes",
    "alignment": "as_of_step_without_interpolation",
    "pre_start": "planned_capital_as_cash",
    "post_end": "exit_value_as_cash",
    "cashflow_return": "daily_modified_dietz_weight_0_5",
}
```

`selected_position` must contain item identity, eligibility/reason, effective initial/current shares, contributions, withdrawals, P&L, flow-adjusted return and chronological event/audit rows. Unsupported ETF/strategy/fixed-notional selections return `{eligible: false, reason: ...}` without action data.

- [ ] **Step 6: Update TypeScript contracts to the exact v2 shape**

```typescript
export type PositionEventRow = {
  root_event_id: string;
  current_event_id: string;
  status: "active" | "superseded" | "voided";
  position_effect: "initial_quantity_correction" | "buy" | "sell";
  trade_date: string;
  event_order: number;
  quantity: number | null;
  execution_price: number | null;
  reference_close: number | null;
  execution_price_source: "db_close_default" | "manual_override" | null;
  fee_usd: number;
  note: string;
  shares_after: number | null;
};

export type SelectedPositionProjection = {
  monitoring_item_id: string | null;
  eligible: boolean;
  reason: string | null;
  effective_initial_shares: number | null;
  current_shares: number | null;
  gross_contributions: number;
  gross_withdrawals: number;
  pnl: number | null;
  total_return: number | null;
  event_rows: PositionEventRow[];
};
```

- [ ] **Step 7: Run read-model and TypeScript type GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_read_model.py tests/test_portfolio_monitoring_component.py -q
cd app/web/streamlit_components/portfolio_monitoring_workbench && npm run typecheck
```

Expected: PASS.

- [ ] **Step 8: Commit Task 5**

```bash
git add app/services/portfolio_monitoring/read_model.py tests/test_portfolio_monitoring_read_model.py app/web/streamlit_components/portfolio_monitoring_workbench/src/contracts.ts
git commit -m "기능: 거래 반영 포트폴리오 성과 모델 연결"
```

---

### Task 6: DB Close Default And Streamlit Command Bridge

**Files:**
- Modify: `app/web/final_selected_portfolio_dashboard.py:323-334,438-764,3991-4040`
- Modify: `tests/test_portfolio_monitoring_page.py`

**Interfaces:**
- Consumes: four position command handlers and `build_direct_security_value_lane(..., position_events=...)`.
- Produces view event: `lookup_position_trade_close`.
- Produces command events: `correct_initial_quantity`, `record_position_trade`, `replace_position_trade`, `void_position_trade`.
- Produces workspace fields `position_editor_state` and `position_trade_close`.

- [ ] **Step 1: Write failing exact-close lookup and recovery tests**

```python
def test_trade_date_lookup_preserves_editor_and_requests_exact_close(self) -> None:
    from app.web import final_selected_portfolio_dashboard as page
    services = self._services()
    event = {
        "id": "lookup_position_trade_close",
        "monitoring_item_id": "item-amd",
        "trade_date": "2026-07-17",
        "position_editor_state": {
            "open": True,
            "mode": "record",
            "position_effect": "buy",
            "quantity": "5",
            "execution_price": "",
            "fee_usd": "0",
            "note": "",
        },
    }
    page._dispatch_portfolio_monitoring_event(event, services)
    self.assertEqual(services.session_state["portfolio_monitoring_trade_date"], "2026-07-17")
    self.assertEqual(services.session_state["portfolio_monitoring_position_editor_state"]["quantity"], "5")
```

```python
def test_exact_close_projection_never_shifts_to_next_market_day(self) -> None:
    from app.web import final_selected_portfolio_dashboard as page
    frame = pd.DataFrame([{"date": "2026-07-18", "close": 160}])
    item = SimpleNamespace(source_ref="AMD")
    with patch.object(page, "load_price_history", return_value=frame):
        with self.assertRaisesRegex(ValueError, "해당 거래일"):
            page._load_exact_position_trade_close(item, date(2026, 7, 17))
```

- [ ] **Step 2: Run RED page tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_page.py -q
```

Expected: FAIL because the lookup event, sanitizer, exact-close helper and services are missing.

- [ ] **Step 3: Add exact DB close loader and one-shot editor recovery projection**

```python
def _load_exact_position_trade_close(item: MonitoringItemRecord, trade_date: date) -> Decimal:
    frame = load_price_history(
        symbols=[item.source_ref],
        start=trade_date.isoformat(),
        end=trade_date.isoformat(),
        timeframe="1d",
    )
    normalized = frame.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce").dt.date
    rows = normalized.loc[normalized["date"] == trade_date]
    if rows.empty:
        raise ValueError("해당 거래일의 저장 종가가 없습니다.")
    close = Decimal(str(rows.iloc[-1]["close"]))
    if close <= 0:
        raise ValueError("해당 거래일의 저장 종가가 없습니다.")
    return close
```

The build path must pop sanitized editor recovery once, resolve only the selected eligible item/date, and return `{status, monitoring_item_id, trade_date, reference_close, reason}`. No provider call or automatic next-session shift is allowed.

- [ ] **Step 4: Write failing four-command dispatch tests**

```python
def test_dispatches_all_position_commands_once(self) -> None:
    from app.web import final_selected_portfolio_dashboard as page
    services = self._services()
    for event_id, call_name in (
        ("correct_initial_quantity", "correct_initial_quantity"),
        ("record_position_trade", "record_position_trade"),
        ("replace_position_trade", "replace_position_trade"),
        ("void_position_trade", "void_position_trade"),
    ):
        event = {"id": event_id, "command_id": f"command-{event_id}", "monitoring_item_id": "item-amd"}
        page._dispatch_portfolio_monitoring_event(event, services)
        self.assertIn((call_name, event), services.calls)
```

- [ ] **Step 5: Wire repository events into lane loading and candidate validation**

```python
def lane_loader(item: MonitoringItemRecord) -> ItemValueLane:
    if item.source_type == SourceType.SELECTED_STRATEGY.value:
        return selected_adapter.build_value_lane(item, end_date=item.tracking_end_effective_date)
    history = load_price_history(
        symbols=[item.source_ref],
        start=item.effective_start_date.isoformat(),
        end=item.tracking_end_effective_date.isoformat() if item.tracking_end_effective_date else None,
        timeframe="1d",
    )
    events = repository.list_position_events(item.monitoring_item_id)
    return build_direct_security_value_lane(item, history, position_events=events)
```

The same DB-only history path must be used by `validate_candidate(item, records)` so a correction/replace/void is rejected before insert when later sells become invalid.

- [ ] **Step 6: Add page service methods and dispatch branches**

Extend `PortfolioMonitoringPageServices` with four callables. Parse date/Decimal/int payloads into the Task 3 input dataclasses, call the handlers with `_load_exact_position_trade_close` and candidate validator, keep selected item/editor context in session, and route all four IDs exactly once.

```python
if event_id == "correct_initial_quantity":
    return services.correct_initial_quantity(event)
if event_id == "record_position_trade":
    return services.record_position_trade(event)
if event_id == "replace_position_trade":
    return services.replace_position_trade(event)
if event_id == "void_position_trade":
    return services.void_position_trade(event)
```

- [ ] **Step 7: Run page, command and valuation integration GREEN**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_page.py tests/test_portfolio_monitoring_commands.py tests/test_portfolio_monitoring_valuation.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit Task 6**

```bash
git add app/web/final_selected_portfolio_dashboard.py tests/test_portfolio_monitoring_page.py
git commit -m "기능: 거래 종가 기본값과 포지션 명령 연결"
```

---

### Task 7: React Position Summary, Correction And Trade Ledger

**Files:**
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.ts`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/positionEditorState.test.ts`
- Create: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/PortfolioMonitoringWorkbench.tsx:571-845`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/style.css`
- Modify: `app/web/streamlit_components/portfolio_monitoring_workbench/src/workbenchState.test.ts`
- Modify: `tests/test_portfolio_monitoring_component.py`

**Interfaces:**
- Consumes: `SelectedPositionProjection`, `PositionTradeCloseProjection`, `CommandProjection`, `emit(event)`.
- Produces: pure helpers `createPositionEditorDraft()`, `applyCloseDefault()`, `validatePositionEditorDraft()`, `buildPositionCommandEvent()`.
- Produces: action-first `PositionLedgerPanel` shown only for eligible selected stock.

- [ ] **Step 1: Write failing close-default and manual-override state tests**

```typescript
it("fills the exact close by default and resets it when the trade date changes", () => {
  const draft = createPositionEditorDraft("record", "buy", "command-1");
  const first = applyCloseDefault({ ...draft, tradeDate: "2026-07-17" }, {
    status: "READY", monitoring_item_id: "item-amd", trade_date: "2026-07-17", reference_close: 160, reason: null,
  });
  expect(first.executionPrice).toBe("160");
  expect(first.priceMode).toBe("db_close_default");

  const manual = markManualExecutionPrice(first, "159.25");
  expect(manual.priceMode).toBe("manual_override");

  const changed = changeTradeDate(manual, "2026-07-18");
  expect(changed.executionPrice).toBe("");
  expect(changed.priceMode).toBe("awaiting_close");
});
```

- [ ] **Step 2: Write failing validation and payload tests**

```typescript
it("blocks full sell and emits the final execution price", () => {
  const draft = {
    ...createPositionEditorDraft("record", "sell", "command-2"),
    tradeDate: "2026-07-17",
    quantity: "5",
    executionPrice: "159.25",
    feeUsd: "1",
    priceMode: "manual_override" as const,
  };
  expect(validatePositionEditorDraft(draft, { currentShares: 5 })).toContain("최소 1주");
  expect(buildPositionCommandEvent({ ...draft, quantity: "4" }, "item-amd")).toMatchObject({
    id: "record_position_trade",
    monitoring_item_id: "item-amd",
    position_effect: "sell",
    trade_date: "2026-07-17",
    quantity: 4,
    execution_price: 159.25,
    fee_usd: 1,
  });
});
```

- [ ] **Step 3: Run React RED tests**

Run:

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test -- positionEditorState.test.ts
```

Expected: FAIL because the editor state module does not exist.

- [ ] **Step 4: Implement pure editor state and recovery helpers**

```typescript
export type PositionEditorDraft = {
  commandId: string;
  mode: "correct_initial" | "record" | "replace";
  rootEventId: string | null;
  expectedEventId: string | null;
  positionEffect: "buy" | "sell";
  tradeDate: string;
  quantity: string;
  executionPrice: string;
  feeUsd: string;
  note: string;
  priceMode: "awaiting_close" | "db_close_default" | "manual_override";
};

export function applyCloseDefault(
  draft: PositionEditorDraft,
  close: PositionTradeCloseProjection,
): PositionEditorDraft {
  if (close.status !== "READY" || close.trade_date !== draft.tradeDate || close.reference_close == null) return draft;
  return {
    ...draft,
    executionPrice: String(close.reference_close),
    priceMode: "db_close_default",
  };
}
```

The lookup payload must include the full sanitized editor state; trade-date changes clear the old price before emitting lookup; correction payload does not request a close; replace preserves `root_event_id` and `expected_event_id`; void emits a fresh command ID and both revision identities.

- [ ] **Step 5: Write failing component source-contract test**

```python
def test_selected_stock_exposes_position_actions_and_ledger_without_strategy_controls(self) -> None:
    source = Path("app/web/streamlit_components/portfolio_monitoring_workbench/src/PositionLedgerPanel.tsx").read_text(encoding="utf-8")
    self.assertIn("현재 보유수량", source)
    self.assertIn("최초 수량 정정", source)
    self.assertIn("매수·매도 기록", source)
    self.assertIn("거래 내역", source)
    self.assertIn('id: "lookup_position_trade_close"', source)
    self.assertIn("종가 기본값", source)
    self.assertIn("수동 체결가", source)
```

- [ ] **Step 6: Implement `PositionLedgerPanel` and connect it below selected summary**

The panel must render current/initial shares, gross buy contributions, sell withdrawals, current value, P&L and flow-adjusted return first. It must expose two actions, use a focused dialog/sheet for correction/trade entry, show before/after shares for sell, require confirmation for void, and keep chronological active/superseded/voided rows. Unsupported selections render a compact boundary sentence and no disabled trade form.

```tsx
{workspace.selected_position && (
  <PositionLedgerPanel
    position={workspace.selected_position}
    closeProjection={workspace.position_trade_close ?? null}
    recoveryState={workspace.position_editor_state}
    latestCommand={latestCommand ?? null}
    emit={emit}
  />
)}
```

- [ ] **Step 7: Add responsive styles**

Desktop summary uses a compact responsive metric grid; the ledger remains one readable column; the editor uses the existing drawer visual language. At `max-width: 900px` the summary becomes two columns, and at `max-width: 420px` it becomes one column with full-width actions and no horizontal overflow.

- [ ] **Step 8: Run React unit, typecheck and production build GREEN**

Run:

```bash
cd app/web/streamlit_components/portfolio_monitoring_workbench
npm test
npm run typecheck
npm run build
```

Expected: all Vitest tests PASS, TypeScript exits 0, Vite writes `component_static/index.html` and hashed assets.

- [ ] **Step 9: Run Python component contracts**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_component.py tests/test_portfolio_monitoring_page.py -q
```

Expected: PASS.

- [ ] **Step 10: Commit Task 7 including canonical static distribution**

```bash
git add app/web/streamlit_components/portfolio_monitoring_workbench/src app/web/streamlit_components/portfolio_monitoring_workbench/component_static tests/test_portfolio_monitoring_component.py
git commit -m "기능: 개별종목 보유내역과 매매 기록 화면 추가"
```

---

### Task 8: Additive Migration, Full Regression, Browser QA And Documentation Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/data/PORTFOLIO_MONITORING_DATA_CONTRACT.md`
- Modify: `.aiworkspace/note/finance/docs/architecture/PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-position-events-v1-20260720/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-position-events-v1-20260720/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-position-events-v1-20260720/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/portfolio-monitoring-position-events-v1-20260720/RISKS.md`
- Generated, do not commit: `portfolio-monitoring-position-events-v1-qa.png`

**Interfaces:**
- Consumes: complete Tasks 1-7 feature.
- Produces: actual empty additive table, verified existing data preservation, responsive QA evidence, durable contract alignment and `3/3차` closeout.

- [ ] **Step 1: Run the full focused Python suite before touching production schema**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_portfolio_monitoring_schema.py \
  tests/test_portfolio_monitoring_position_events.py \
  tests/test_portfolio_monitoring_commands.py \
  tests/test_portfolio_monitoring_valuation.py \
  tests/test_portfolio_monitoring_read_model.py \
  tests/test_portfolio_monitoring_page.py \
  tests/test_portfolio_monitoring_component.py \
  tests/test_portfolio_monitoring_catalog.py \
  tests/test_portfolio_monitoring_selected_strategy.py \
  -q
```

Expected: PASS with zero failures.

- [ ] **Step 2: Verify the additive DDL target and create only the new empty table**

Run a read-only precheck against `finance_meta` for table existence and existing monitoring item/command counts. Then call `MySQLMonitoringRepository.ensure_schema()` once. Re-run the counts and assert:

- existing group/item/command counts are unchanged;
- `monitoring_security_position_event` exists;
- its row count is `0` before Browser QA;
- no registry/saved JSONL checksum changes.

Record commands and counts in task `RUNS.md`; do not print credentials into logs.

- [ ] **Step 3: Run all linked automated regressions and static checks**

Run:

```bash
.venv/bin/python -m pytest tests/test_portfolio_monitoring_*.py -q
.venv/bin/python -m py_compile \
  app/services/portfolio_monitoring/position_events.py \
  app/services/portfolio_monitoring/commands.py \
  app/services/portfolio_monitoring/valuation.py \
  app/services/portfolio_monitoring/read_model.py \
  app/web/final_selected_portfolio_dashboard.py
cd app/web/streamlit_components/portfolio_monitoring_workbench && npm test && npm run typecheck && npm run build
cd /Users/taeho/Project/quant-data-pipeline-worktrees/main-dev && git diff --check
```

Expected: every command exits 0.

- [ ] **Step 4: Start the local Finance app for a read-only route smoke test**

Use the repository’s current Finance Streamlit startup command from the Portfolio Monitoring runbook. Open `Operations > Portfolio Monitoring`, confirm workspace v2 loads without storage error, existing portfolios/items render, and unsupported items keep their current behavior. Do not create, edit, end or reopen production user items.

- [ ] **Step 5: Perform interactive Browser QA with an isolated fixture harness**

Create a temporary directory with `mktemp -d` and a non-committed Streamlit harness that imports the canonical React component, supplies a representative `portfolio_monitoring_workspace_v2` fixture, and updates session fixture state from component events. The harness must not connect to production MySQL or write registry/saved JSONL. In the browser:

1. Open `Operations > Portfolio Monitoring`.
2. Confirm `현재 보유수량`, `최초 수량 정정`, `매수·매도 기록` appear for the eligible fixture.
3. Select a fixture market date and confirm its close auto-fills.
4. Override the price and confirm `수동 체결가` appears.
5. Submit buy/sell/replace/void UI events and confirm the harness projects the corresponding fixture response.
6. Confirm ETF/strategy/fixed-notional fixture selections have no trade actions.

- [ ] **Step 6: Perform responsive QA and save one generated screenshot**

Verify desktop, `900px`, and `420px` widths for dialog/sheet layout, summary readability, ledger wrapping, button reachability and horizontal overflow `0`. Save one representative screenshot as `portfolio-monitoring-position-events-v1-qa.png`; do not stage it.

- [ ] **Step 7: Synchronize durable and task documentation**

Document:

- the new table and append-only revision contract;
- direct-stock fixed-shares eligibility;
- DB close default/manual override provenance;
- buy contribution/sell withdrawal and Modified Dietz 0.5 method;
- full-sell/trading/broker boundaries;
- exact test counts, production migration counts and Browser QA result;
- overall roadmap `3/3차` only after all required checks pass.

Update root handoff logs in 3-5 concise milestone lines and keep full commands in task `RUNS.md`.

- [ ] **Step 8: Review the final diff and exclude generated/user artifacts**

Run:

```bash
git status --short
git diff --check
git diff --stat
git diff -- .aiworkspace/note/finance/registries .aiworkspace/note/finance/saved
```

Expected: no registry/saved diff; QA screenshot and pre-existing untracked artifacts remain unstaged.

- [ ] **Step 9: Commit Task 8**

```bash
git add \
  .aiworkspace/note/finance/docs \
  .aiworkspace/note/finance/WORK_PROGRESS.md \
  .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md \
  .aiworkspace/note/finance/tasks/active/portfolio-monitoring-position-events-v1-20260720
git commit -m "문서: 개별종목 거래 원장 구현과 QA 정리"
```

- [ ] **Step 10: Run final post-commit verification**

Run:

```bash
git show --stat --oneline --summary HEAD
git status --short
```

Expected: the documentation commit contains only intended closeout files; generated and pre-existing untracked artifacts are not committed.

---

## Execution Checkpoints

- Checkpoint A — Task 1-2: additive storage and pure projection are independently reviewable; no UI or production mutation.
- Checkpoint B — Task 3-4: commands and cashflow valuation are independently testable; no React work yet.
- Checkpoint C — Task 5-7: workspace v2, page bridge and action-first React workflow are complete with automated regression.
- Checkpoint D — Task 8: additive production table, actual Browser QA, durable documentation and final verification close the roadmap.

## Completion State

- Current: overall roadmap `1/3차`; approved design and this implementation plan.
- After Tasks 1-4: `2차` backend/domain portion complete, UI still incomplete.
- After Tasks 5-7: `2차` DB/service/UI implementation complete.
- After Task 8: `3차` migration/regression/Browser QA/docs complete; overall `3/3차`.

## Plan Self-Review

- Spec coverage: initial correction is Tasks 2-4/6-7; buy/sell is Tasks 2-7; replace/void is Tasks 2-3/6-7.
- Price behavior: Task 3 stores `reference_close` and server-derived source; Tasks 6-7 implement exact-date close auto-fill, manual override and date-change reset.
- Calculation coverage: Task 4 owns split-first item cashflows and Modified Dietz; Task 5 owns group aggregation and no-event parity.
- Scope coverage: eligibility is server-owned in Task 2 and action visibility is React-owned in Task 7; ETF/strategy/fixed-notional/full-sell remain excluded.
- Persistence coverage: Task 1 is additive only; Task 8 verifies existing counts/checksums and keeps production event rows empty before interactive fixture QA.
- Error coverage: Tasks 2-3 validate sequence/revision/concurrency; Task 6 validates exact DB dates; Task 7 previews the same constraints without replacing server authority.
- QA coverage: every task has RED/GREEN commands and a coherent commit; Task 8 includes full Python/React/build checks, read-only production smoke and isolated responsive Browser QA.
- Type consistency: `PositionEventRecord`, `PositionEventProjection`, `PositionLedgerSummary`, `SelectedPositionProjection` and command IDs/names are introduced before consumers and use the same field names across Python and TypeScript.
- Placeholder scan: no unresolved placeholder, unspecified error step or deferred implementation requirement remains in this plan.
