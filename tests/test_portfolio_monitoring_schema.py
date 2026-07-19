from __future__ import annotations

import importlib
import unittest
from datetime import date
from decimal import Decimal


def _load_schema_module():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.schemas")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio_monitoring domain schema module is required") from exc


def _load_database_schemas():
    module = importlib.import_module("finance.data.db.schema")
    if not hasattr(module, "PORTFOLIO_MONITORING_SCHEMAS"):
        raise AssertionError("PORTFOLIO_MONITORING_SCHEMAS is required")
    return module.PORTFOLIO_MONITORING_SCHEMAS


class PortfolioMonitoringDatabaseSchemaTests(unittest.TestCase):
    def test_schema_defines_group_item_and_command_tables(self) -> None:
        portfolio_monitoring_schemas = _load_database_schemas()

        self.assertEqual(
            set(portfolio_monitoring_schemas),
            {
                "monitoring_portfolio_group",
                "monitoring_portfolio_item",
                "monitoring_portfolio_command",
            },
        )

        group_sql = portfolio_monitoring_schemas["monitoring_portfolio_group"]
        self.assertIn("CREATE TABLE IF NOT EXISTS monitoring_portfolio_group", group_sql)
        self.assertIn("portfolio_group_id VARCHAR(64) PRIMARY KEY", group_sql)
        self.assertIn("is_default TINYINT(1) NOT NULL DEFAULT 0", group_sql)
        self.assertIn("version BIGINT NOT NULL DEFAULT 1", group_sql)
        self.assertIn("deleted_at TIMESTAMP NULL", group_sql)
        self.assertIn("ix_monitoring_group_status", group_sql)

        item_sql = portfolio_monitoring_schemas["monitoring_portfolio_item"]
        self.assertIn("CREATE TABLE IF NOT EXISTS monitoring_portfolio_item", item_sql)
        self.assertIn("monitoring_item_id VARCHAR(64) PRIMARY KEY", item_sql)
        self.assertIn("source_type ENUM('direct_security','selected_strategy')", item_sql)
        self.assertIn("instrument_kind ENUM('stock','etf','strategy')", item_sql)
        self.assertIn("funding_mode ENUM('fixed_notional','fixed_shares')", item_sql)
        self.assertIn("requested_start_date DATE NOT NULL", item_sql)
        self.assertIn("effective_start_date DATE NOT NULL", item_sql)
        self.assertIn("tracking_end_effective_date DATE NULL", item_sql)
        self.assertIn("exit_value DECIMAL(24,8) NULL", item_sql)
        self.assertIn("status ENUM('active','ended','data_review')", item_sql)
        self.assertIn("ix_monitoring_item_group_status", item_sql)
        self.assertIn("ix_monitoring_item_source", item_sql)

        command_sql = portfolio_monitoring_schemas["monitoring_portfolio_command"]
        self.assertIn("CREATE TABLE IF NOT EXISTS monitoring_portfolio_command", command_sql)
        self.assertIn("command_id VARCHAR(64) PRIMARY KEY", command_sql)
        self.assertIn("request_fingerprint CHAR(64) NOT NULL", command_sql)
        self.assertIn("status ENUM('pending','succeeded','failed')", command_sql)
        self.assertIn("result_ref VARCHAR(128) NULL", command_sql)
        self.assertIn("ix_monitoring_command_target", command_sql)


class PortfolioMonitoringDomainSchemaTests(unittest.TestCase):
    def _valid_direct_share_input(self):
        schemas = _load_schema_module()
        return schemas.AddMonitoringItemInput(
            portfolio_group_id="group-core",
            source_type=schemas.SourceType.DIRECT_SECURITY,
            source_ref="AAPL",
            instrument_kind=schemas.InstrumentKind.STOCK,
            requested_start_date=date(2026, 7, 1),
            funding_mode=schemas.FundingMode.FIXED_SHARES,
            input_shares=10,
        )

    def test_integer_shares_are_required_for_direct_security_share_mode(self) -> None:
        schemas = _load_schema_module()

        valid = schemas.validate_add_item_input(self._valid_direct_share_input())
        self.assertEqual(valid.input_shares, 10)

        for invalid_shares in (0, -1, 1.5, Decimal("2.5"), True):
            with self.subTest(invalid_shares=invalid_shares):
                invalid = schemas.AddMonitoringItemInput(
                    **{
                        **self._valid_direct_share_input().__dict__,
                        "input_shares": invalid_shares,
                    }
                )
                with self.assertRaisesRegex(ValueError, "integer shares"):
                    schemas.validate_add_item_input(invalid)

    def test_selected_strategy_accepts_fixed_notional_only(self) -> None:
        schemas = _load_schema_module()
        valid = schemas.AddMonitoringItemInput(
            portfolio_group_id="group-core",
            source_type=schemas.SourceType.SELECTED_STRATEGY,
            source_ref="decision-001",
            instrument_kind=schemas.InstrumentKind.STRATEGY,
            requested_start_date=date(2026, 7, 1),
            funding_mode=schemas.FundingMode.FIXED_NOTIONAL,
            input_notional=Decimal("10000"),
        )

        self.assertEqual(
            schemas.validate_add_item_input(valid).input_notional,
            Decimal("10000"),
        )

        invalid = schemas.AddMonitoringItemInput(
            **{
                **valid.__dict__,
                "funding_mode": schemas.FundingMode.FIXED_SHARES,
                "input_notional": None,
                "input_shares": 3,
            }
        )
        with self.assertRaisesRegex(ValueError, "selected strategy.*fixed notional"):
            schemas.validate_add_item_input(invalid)

    def test_fixed_notional_must_be_positive_and_exclusive(self) -> None:
        schemas = _load_schema_module()
        base = schemas.AddMonitoringItemInput(
            portfolio_group_id="group-core",
            source_type=schemas.SourceType.DIRECT_SECURITY,
            source_ref="SPY",
            instrument_kind=schemas.InstrumentKind.ETF,
            requested_start_date=date(2026, 7, 1),
            funding_mode=schemas.FundingMode.FIXED_NOTIONAL,
            input_notional=Decimal("10000"),
        )

        self.assertEqual(
            schemas.validate_add_item_input(base).input_notional,
            Decimal("10000"),
        )
        for invalid_notional in (Decimal("0"), Decimal("-1"), None):
            with self.subTest(invalid_notional=invalid_notional):
                invalid = schemas.AddMonitoringItemInput(
                    **{**base.__dict__, "input_notional": invalid_notional}
                )
                with self.assertRaisesRegex(ValueError, "positive notional"):
                    schemas.validate_add_item_input(invalid)

        both_modes = schemas.AddMonitoringItemInput(
            **{**base.__dict__, "input_shares": 2}
        )
        with self.assertRaisesRegex(ValueError, "input_shares must be empty"):
            schemas.validate_add_item_input(both_modes)

    def test_request_fingerprint_is_stable_across_mapping_key_order(self) -> None:
        schemas = _load_schema_module()
        first = {
            "source_ref": "AAPL",
            "requested_start_date": date(2026, 7, 1),
            "input_notional": Decimal("10000.00"),
            "tags": ["core", "growth"],
        }
        second = {
            "tags": ["core", "growth"],
            "input_notional": Decimal("10000.00"),
            "requested_start_date": date(2026, 7, 1),
            "source_ref": "AAPL",
        }

        fingerprint = schemas.build_request_fingerprint(first)
        self.assertEqual(fingerprint, schemas.build_request_fingerprint(second))
        self.assertEqual(len(fingerprint), 64)
        self.assertNotEqual(
            fingerprint,
            schemas.build_request_fingerprint({**first, "source_ref": "MSFT"}),
        )


if __name__ == "__main__":
    unittest.main()
