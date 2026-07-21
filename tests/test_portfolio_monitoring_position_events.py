from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal


def _stock_item(**changes):
    from app.services.portfolio_monitoring.persistence import MonitoringItemRecord

    values = {
        "monitoring_item_id": "item-amd",
        "portfolio_group_id": "group-core",
        "source_type": "direct_security",
        "source_ref": "AMD",
        "instrument_kind": "stock",
        "requested_start_date": date(2026, 7, 1),
        "effective_start_date": date(2026, 7, 1),
        "funding_mode": "fixed_shares",
        "input_notional": None,
        "input_shares": 30,
        "entry_close": Decimal("100"),
        "initial_capital": Decimal("3000"),
    }
    values.update(changes)
    return MonitoringItemRecord(**values)


def _event(
    event_id: str,
    root_id: str,
    supersedes_id: str | None,
    order: int,
    action: str,
    effect: str,
    trade_date: date,
    quantity: int | None,
    execution_price: str | None,
):
    from app.services.portfolio_monitoring.persistence import PositionEventRecord

    return PositionEventRecord(
        position_event_id=event_id,
        root_event_id=root_id,
        supersedes_event_id=supersedes_id,
        monitoring_item_id="item-amd",
        event_order=order,
        event_action=action,
        position_effect=effect,
        trade_date=trade_date,
        quantity=quantity,
        execution_price=(
            Decimal(execution_price) if execution_price is not None else None
        ),
        reference_close=(
            Decimal(execution_price) if execution_price is not None else None
        ),
        execution_price_source=(
            "db_close_default" if execution_price is not None else None
        ),
        fee_usd=Decimal("0"),
        note="",
        command_id=f"command-{event_id}",
    )


class PortfolioMonitoringPositionEventPersistenceTests(unittest.TestCase):
    def test_domain_enums_define_append_only_event_vocabulary(self) -> None:
        from app.services.portfolio_monitoring import schemas

        self.assertEqual(
            {member.value for member in schemas.PositionEventAction},
            {"create", "replace", "void"},
        )
        self.assertEqual(
            {member.value for member in schemas.PositionEffect},
            {"initial_quantity_correction", "buy", "sell"},
        )
        self.assertEqual(
            {member.value for member in schemas.ExecutionPriceSource},
            {"db_close_default", "manual_override"},
        )

    def test_repository_protocol_exposes_position_event_operations(self) -> None:
        from app.services.portfolio_monitoring.persistence import MonitoringRepository

        required = {
            "list_position_events",
            "get_position_event",
            "next_position_event_order",
            "insert_position_event",
        }

        self.assertTrue(required.issubset(MonitoringRepository.__dict__))

    def test_position_event_row_parser_preserves_decimal_and_provenance_fields(self) -> None:
        from app.services.portfolio_monitoring.persistence import _position_event_from_row

        created_at = datetime(2026, 7, 20, 12, 30)
        record = _position_event_from_row(
            {
                "position_event_id": "event-v1",
                "root_event_id": "event-root",
                "supersedes_event_id": None,
                "monitoring_item_id": "item-amd",
                "event_order": 3,
                "event_action": "create",
                "position_effect": "buy",
                "trade_date": date(2026, 7, 17),
                "requested_start_date": date(2026, 7, 16),
                "effective_start_date": date(2026, 7, 17),
                "quantity": 5,
                "execution_price": "145.25",
                "reference_close": Decimal("144.80"),
                "execution_price_source": "manual_override",
                "fee_usd": "1.10",
                "note": "추가 매수",
                "command_id": "command-1",
                "created_at": created_at,
            }
        )

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.execution_price, Decimal("145.25"))
        self.assertEqual(record.reference_close, Decimal("144.80"))
        self.assertEqual(record.fee_usd, Decimal("1.10"))
        self.assertEqual(record.requested_start_date, date(2026, 7, 16))
        self.assertEqual(record.effective_start_date, date(2026, 7, 17))
        self.assertEqual(record.created_at, created_at)


class PortfolioMonitoringPositionEventProjectionTests(unittest.TestCase):
    def test_projection_uses_terminal_revision_without_reordering_the_root(self) -> None:
        from app.services.portfolio_monitoring.position_events import (
            project_position_events,
        )

        records = [
            _event(
                "buy-v1", "buy-root", None, 1, "create", "buy",
                date(2026, 7, 10), 5, "100",
            ),
            _event(
                "sell-v1", "sell-root", None, 2, "create", "sell",
                date(2026, 7, 10), 3, "110",
            ),
            _event(
                "buy-v2", "buy-root", "buy-v1", 1, "replace", "buy",
                date(2026, 7, 10), 7, "99",
            ),
        ]

        projection = project_position_events(_stock_item(), records)

        self.assertEqual(projection.effective_initial_shares, 30)
        self.assertEqual(
            [row.root_event_id for row in projection.trades],
            ["buy-root", "sell-root"],
        )
        self.assertEqual([row.quantity for row in projection.trades], [7, 3])

    def test_void_removes_business_effect_but_retains_audit_row(self) -> None:
        from app.services.portfolio_monitoring.position_events import (
            project_position_events,
        )

        projection = project_position_events(
            _stock_item(),
            [
                _event(
                    "buy-v1", "buy-root", None, 1, "create", "buy",
                    date(2026, 7, 10), 5, "100",
                ),
                _event(
                    "buy-void", "buy-root", "buy-v1", 1, "void", "buy",
                    date(2026, 7, 10), None, None,
                ),
            ],
        )

        self.assertEqual(projection.trades, ())
        self.assertEqual(projection.audit_rows[-1].status, "voided")

    def test_projection_applies_single_initial_quantity_correction(self) -> None:
        from app.services.portfolio_monitoring.position_events import (
            project_position_events,
        )

        projection = project_position_events(
            _stock_item(),
            [
                _event(
                    "correction-v1", "correction-root", None, 1, "create",
                    "initial_quantity_correction", date(2026, 7, 1), 40, None,
                )
            ],
        )

        self.assertEqual(projection.effective_initial_shares, 40)
        self.assertEqual(projection.initial_correction.quantity, 40)

    def test_projection_uses_corrected_date_close_and_quantity(self) -> None:
        from app.services.portfolio_monitoring.position_events import (
            project_position_events,
        )

        item = _stock_item(input_shares=30)
        correction = replace(
            _event(
                "correct-v1",
                "correct-root",
                None,
                1,
                "create",
                "initial_quantity_correction",
                date(2026, 6, 29),
                40,
                None,
            ),
            requested_start_date=date(2026, 6, 28),
            effective_start_date=date(2026, 6, 29),
            reference_close=Decimal("95"),
        )

        projection = project_position_events(item, [correction])

        self.assertEqual(
            projection.initial_contract.requested_start_date,
            date(2026, 6, 28),
        )
        self.assertEqual(
            projection.initial_contract.effective_start_date,
            date(2026, 6, 29),
        )
        self.assertEqual(projection.initial_contract.entry_close, Decimal("95"))
        self.assertEqual(projection.initial_contract.initial_shares, 40)
        self.assertEqual(projection.initial_contract.initial_capital, Decimal("3800"))

    def test_legacy_quantity_correction_falls_back_to_item_start_contract(self) -> None:
        from app.services.portfolio_monitoring.position_events import (
            project_position_events,
        )

        item = _stock_item(input_shares=30)
        legacy = _event(
            "correct-v1",
            "correct-root",
            None,
            1,
            "create",
            "initial_quantity_correction",
            date(2026, 7, 1),
            20,
            None,
        )

        projection = project_position_events(item, [legacy])

        self.assertEqual(
            projection.initial_contract.requested_start_date,
            item.requested_start_date,
        )
        self.assertEqual(
            projection.initial_contract.effective_start_date,
            item.effective_start_date,
        )
        self.assertEqual(projection.initial_contract.entry_close, item.entry_close)
        self.assertEqual(projection.initial_contract.initial_shares, 20)
        self.assertEqual(projection.initial_contract.initial_capital, Decimal("2000"))

    def test_sequence_applies_each_split_before_same_day_sell(self) -> None:
        from app.services.portfolio_monitoring.position_events import (
            project_position_events,
            validate_position_sequence,
        )

        projection = project_position_events(
            _stock_item(),
            [
                _event(
                    "sell-v1", "sell-root", None, 1, "create", "sell",
                    date(2026, 7, 15), 50, "110",
                )
            ],
        )
        snapshots = validate_position_sequence(
            _stock_item(),
            projection,
            split_factors={date(2026, 7, 15): Decimal("2")},
        )

        self.assertEqual(snapshots[-1].shares_before, Decimal("60"))
        self.assertEqual(snapshots[-1].shares_after, Decimal("10"))

    def test_sequence_rejects_full_sell_and_non_stock_targets(self) -> None:
        from app.services.portfolio_monitoring.position_events import (
            PositionEventValidationError,
            assert_position_item_eligible,
            project_position_events,
            validate_position_sequence,
        )

        projection = project_position_events(
            _stock_item(),
            [
                _event(
                    "sell-v1", "sell-root", None, 1, "create", "sell",
                    date(2026, 7, 10), 30, "110",
                )
            ],
        )
        with self.assertRaisesRegex(PositionEventValidationError, "최소 1주"):
            validate_position_sequence(_stock_item(), projection, split_factors={})

        with self.assertRaisesRegex(PositionEventValidationError, "개별주식"):
            assert_position_item_eligible(_stock_item(instrument_kind="etf"))


if __name__ == "__main__":
    unittest.main()
