from __future__ import annotations

import unittest
from datetime import date, datetime
from decimal import Decimal


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
        self.assertEqual(record.created_at, created_at)


if __name__ == "__main__":
    unittest.main()
