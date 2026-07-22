from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from types import SimpleNamespace

import pandas as pd


NOW = datetime(2026, 7, 22, 14, 0, tzinfo=timezone.utc)


def _item(
    symbol: str,
    *,
    source_type: str = "direct_security",
    kind: str = "stock",
    status: str = "active",
):
    return SimpleNamespace(
        source_ref=symbol,
        source_type=source_type,
        instrument_kind=kind,
        status=status,
    )


def _group(group_id: str = "group-a"):
    return SimpleNamespace(portfolio_group_id=group_id)


def _session(quality: str = "CONFIRMED") -> dict[str, object]:
    return {
        "calendar_quality": quality,
        "timezones": {
            "market": "America/New_York",
            "viewer": "Asia/Seoul",
        },
        "schedule": [
            {
                "trade_date": "2026-07-22",
                "day_kind": "TRADING_DAY",
                "holiday_label": None,
                "open_at_utc": "2026-07-22T13:30:00+00:00",
                "close_at_utc": "2026-07-22T20:00:00+00:00",
                "is_early_close": False,
            }
        ],
    }


class FakeDb:
    def __init__(self, *, rows=None, lock_acquired: int = 1) -> None:
        self.rows = list(rows or [])
        self.lock_acquired = lock_acquired
        self.used_dbs: list[str] = []
        self.queries: list[tuple[str, list[object]]] = []
        self.closed = False

    def use_db(self, db_name: str) -> None:
        self.used_dbs.append(db_name)

    def query(self, sql: str, params=None):
        normalized = " ".join(sql.split())
        values = list(params or [])
        self.queries.append((normalized, values))
        if "GET_LOCK" in normalized:
            return [{"acquired": self.lock_acquired}]
        if "RELEASE_LOCK" in normalized:
            return [{"released": 1}]
        return list(self.rows)

    def close(self) -> None:
        self.closed = True


class TodayPortfolioIntradayScopeTests(unittest.TestCase):
    def test_scope_hash_and_eligibility_are_stable(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_intraday_refresh_scope,
        )

        scope = build_intraday_refresh_scope(
            _group(),
            [
                _item("amd"),
                _item("QQQ", kind="etf", status="data_review"),
                _item(
                    "strategy-1",
                    source_type="selected_strategy",
                    kind="strategy",
                ),
                _item("OLD", status="ended"),
            ],
        )

        self.assertEqual(scope.symbols, ("AMD", "QQQ"))
        self.assertEqual(
            scope.universe_code,
            "TODAY_" + sha256(b"group-a").hexdigest()[:16].upper(),
        )
        self.assertEqual(len(scope.items), 2)

    def test_only_confirmed_open_session_is_collectible(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            resolve_regular_session_state,
        )

        opened = resolve_regular_session_state(_session(), NOW)
        limited = resolve_regular_session_state(_session("LIMITED"), NOW)

        self.assertEqual(opened.phase, "OPEN")
        self.assertEqual(opened.trade_date, date(2026, 7, 22))
        self.assertTrue(opened.collection_allowed)
        self.assertEqual(limited.phase, "STALE")
        self.assertFalse(limited.collection_allowed)

    def test_preopen_and_close_boundaries_do_not_collect(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            resolve_regular_session_state,
        )

        preopen = resolve_regular_session_state(
            _session(),
            datetime(2026, 7, 22, 13, 29, 59, tzinfo=timezone.utc),
        )
        closed = resolve_regular_session_state(
            _session(),
            datetime(2026, 7, 22, 20, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(preopen.phase, "PRE_OPEN")
        self.assertFalse(preopen.collection_allowed)
        self.assertEqual(closed.phase, "CLOSED")
        self.assertFalse(closed.collection_allowed)


class TodayPortfolioIntradaySnapshotTests(unittest.TestCase):
    def _scope(self):
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_intraday_refresh_scope,
        )

        return build_intraday_refresh_scope(
            _group(),
            [_item("AMD"), _item("QQQ", kind="etf")],
        )

    def test_latest_attempt_becomes_due_at_exactly_300_seconds(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            load_latest_portfolio_quotes,
        )

        rows = [
            {
                "symbol": "AMD",
                "snapshot_time_utc": NOW.replace(tzinfo=None),
                "quote_time_utc": NOW.replace(tzinfo=None),
                "latest_price": 101.0,
                "previous_close": 100.0,
                "provider_status": "ok",
                "error_msg": None,
            }
        ]
        at_299 = load_latest_portfolio_quotes(
            self._scope(),
            now=NOW + timedelta(seconds=299),
            db_factory=lambda: FakeDb(rows=rows),
        )
        at_300 = load_latest_portfolio_quotes(
            self._scope(),
            now=NOW + timedelta(seconds=300),
            db_factory=lambda: FakeDb(rows=rows),
        )

        self.assertFalse(at_299.due)
        self.assertTrue(at_300.due)

    def test_quote_older_than_600_seconds_is_stale(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            load_latest_portfolio_quotes,
        )

        rows = [
            {
                "symbol": "AMD",
                "snapshot_time_utc": NOW.replace(tzinfo=None),
                "quote_time_utc": (NOW - timedelta(seconds=601)).replace(
                    tzinfo=None
                ),
                "latest_price": 101.0,
                "previous_close": 100.0,
                "provider_status": "ok",
                "error_msg": None,
            }
        ]
        latest = load_latest_portfolio_quotes(
            self._scope(),
            now=NOW,
            db_factory=lambda: FakeDb(rows=rows),
        )

        self.assertEqual(latest.status, "STALE")
        self.assertEqual(latest.fresh_symbols, ())
        self.assertEqual(latest.fallback_symbols, ("AMD", "QQQ"))

    def test_partial_snapshot_reports_exact_coverage(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            load_latest_portfolio_quotes,
        )

        rows = [
            {
                "symbol": "AMD",
                "snapshot_time_utc": NOW.replace(tzinfo=None),
                "quote_time_utc": NOW.replace(tzinfo=None),
                "latest_price": 101.0,
                "previous_close": 100.0,
                "provider_status": "ok",
                "error_msg": None,
            },
            {
                "symbol": "QQQ",
                "snapshot_time_utc": NOW.replace(tzinfo=None),
                "quote_time_utc": None,
                "latest_price": None,
                "previous_close": 500.0,
                "provider_status": "error",
                "error_msg": "provider down",
            },
        ]
        latest = load_latest_portfolio_quotes(
            self._scope(),
            now=NOW,
            db_factory=lambda: FakeDb(rows=rows),
        )

        self.assertEqual(latest.status, "LIVE_PARTIAL")
        self.assertEqual(latest.fresh_symbols, ("AMD",))
        self.assertEqual(latest.fallback_symbols, ("QQQ",))
        self.assertEqual(latest.quotes["AMD"]["latest_price"], 101.0)


class TodayPortfolioIntradayLockTests(unittest.TestCase):
    def _scope(self):
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_intraday_refresh_scope,
        )

        return build_intraday_refresh_scope(_group(), [_item("AMD")])

    def test_lock_contention_skips_provider_collection(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            LatestPortfolioQuotes,
            run_due_intraday_collection,
        )

        calls: list[dict[str, object]] = []
        due = LatestPortfolioQuotes.empty(self._scope(), due=True)
        result = run_due_intraday_collection(
            self._scope(),
            now=NOW,
            db_factory=lambda: FakeDb(lock_acquired=0),
            latest_loader=lambda scope, **kwargs: due,
            collector=lambda **kwargs: calls.append(kwargs),
        )

        self.assertEqual(result["status"], "lock_contended")
        self.assertEqual(calls, [])

    def test_recent_db_attempt_survives_new_runner_instance(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            LatestPortfolioQuotes,
            run_due_intraday_collection,
        )

        calls: list[dict[str, object]] = []
        recent = LatestPortfolioQuotes.empty(self._scope(), due=False)
        for _ in range(2):
            result = run_due_intraday_collection(
                self._scope(),
                now=NOW,
                db_factory=lambda: FakeDb(),
                latest_loader=lambda scope, **kwargs: recent,
                collector=lambda **kwargs: calls.append(kwargs),
            )
            self.assertEqual(result["status"], "not_due")

        self.assertEqual(calls, [])

    def test_acquired_lock_rechecks_due_and_releases_after_collection(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            LatestPortfolioQuotes,
            run_due_intraday_collection,
        )

        fake_db = FakeDb(lock_acquired=1)
        calls: list[dict[str, object]] = []
        due = LatestPortfolioQuotes.empty(self._scope(), due=True)
        result = run_due_intraday_collection(
            self._scope(),
            now=NOW,
            db_factory=lambda: fake_db,
            latest_loader=lambda scope, **kwargs: due,
            collector=lambda **kwargs: calls.append(kwargs)
            or {"rows_written": 1},
        )

        self.assertEqual(result["status"], "submitted_result")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["symbols"], ("AMD",))
        self.assertEqual(
            calls[0]["source_ref"],
            "portfolio_group_id=group-a",
        )
        self.assertTrue(
            any("RELEASE_LOCK" in sql for sql, _ in fake_db.queries)
        )
        self.assertTrue(fake_db.closed)


class TodayPortfolioLiveValuationTests(unittest.TestCase):
    def _scope(self):
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_intraday_refresh_scope,
        )

        amd = SimpleNamespace(
            monitoring_item_id="amd-item",
            source_ref="AMD",
            source_type="direct_security",
            instrument_kind="stock",
            status="active",
            funding_mode="fixed_notional",
            input_notional=Decimal("1000"),
            input_shares=None,
            entry_close=Decimal("100"),
        )
        qqq = SimpleNamespace(
            monitoring_item_id="qqq-item",
            source_ref="QQQ",
            source_type="direct_security",
            instrument_kind="etf",
            status="active",
            funding_mode="fixed_shares",
            input_notional=None,
            input_shares=Decimal("5"),
            entry_close=Decimal("200"),
        )
        return build_intraday_refresh_scope(_group(), [amd, qqq])

    def _workspace(self, *, external_flow: Decimal = Decimal("0")):
        return {
            "active_group": {
                "basis_date": date(2026, 7, 21),
                "metrics": {
                    "current_value": Decimal("2520"),
                    "gross_contributions": Decimal("2200"),
                    "gross_withdrawals": Decimal("0"),
                    "total_return": Decimal("0.10"),
                    "contribution_by_item": {
                        "amd-item": Decimal("100"),
                        "qqq-item": Decimal("120"),
                        "strategy-item": Decimal("100"),
                    },
                },
                "curve": pd.DataFrame(
                    [
                        {
                            "date": pd.Timestamp("2026-07-21"),
                            "total_value": 2520.0,
                            "unit_value": 1.10,
                        }
                    ]
                ),
                "item_rows": (
                    {
                        "monitoring_item_id": "amd-item",
                        "source_ref": "AMD",
                        "current_value": Decimal("1000"),
                        "total_return": Decimal("0.10"),
                    },
                    {
                        "monitoring_item_id": "qqq-item",
                        "source_ref": "QQQ",
                        "current_value": Decimal("1020"),
                        "total_return": Decimal("0.12"),
                    },
                    {
                        "monitoring_item_id": "strategy-item",
                        "source_ref": "strategy-a",
                        "current_value": Decimal("500"),
                        "total_return": Decimal("0.25"),
                    },
                ),
            },
            "item_details": {
                "amd-item": {
                    "position": {
                        "current_shares": Decimal("10"),
                        "gross_contributions": Decimal("0"),
                        "gross_withdrawals": Decimal("0"),
                    }
                },
                "qqq-item": {
                    "position": {
                        "current_shares": Decimal("5"),
                        "gross_contributions": Decimal("900"),
                        "gross_withdrawals": Decimal("0"),
                    }
                },
            },
            "intraday_external_flow": external_flow,
        }

    def _quotes(self, *, include_qqq: bool = True):
        from app.services.portfolio_monitoring.intraday_refresh import (
            LatestPortfolioQuotes,
        )

        values = {
            "AMD": {"symbol": "AMD", "latest_price": 105.0},
        }
        if include_qqq:
            values["QQQ"] = {"symbol": "QQQ", "latest_price": 204.0}
        fresh = tuple(values)
        return LatestPortfolioQuotes(
            status="LIVE_READY" if include_qqq else "LIVE_PARTIAL",
            attempt_time_utc=NOW,
            quote_time_utc=NOW,
            quotes=values,
            fresh_symbols=fresh,
            fallback_symbols=() if include_qqq else ("QQQ",),
            due=False,
        )

    def test_fixed_notional_and_share_items_preserve_retained_cash(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_live_portfolio_overlay,
        )

        overlay = build_live_portfolio_overlay(
            workspace=self._workspace(),
            scope=self._scope(),
            quotes=self._quotes(),
            eod_closes={"AMD": Decimal("100"), "QQQ": Decimal("200")},
            now=NOW,
        )

        self.assertIsNotNone(overlay)
        assert overlay is not None
        self.assertEqual(overlay["status"], "LIVE_READY")
        self.assertEqual(overlay["coverage"], {"fresh": 2, "expected": 2})
        self.assertEqual(overlay["metrics"]["current_value"], 2590.0)
        values = {row["symbol"]: row["current_value"] for row in overlay["items"]}
        self.assertEqual(values["AMD"], 1050.0)
        self.assertEqual(values["QQQ"], 1040.0)
        contributors = {
            row["symbol"]: row["contribution_value"]
            for row in overlay["contributors"]
        }
        self.assertEqual(contributors["AMD"], 150.0)

    def test_partial_quote_falls_back_to_eod_and_excludes_strategy_from_coverage(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_live_portfolio_overlay,
        )

        overlay = build_live_portfolio_overlay(
            workspace=self._workspace(),
            scope=self._scope(),
            quotes=self._quotes(include_qqq=False),
            eod_closes={"AMD": Decimal("100"), "QQQ": Decimal("200")},
            now=NOW,
        )

        self.assertIsNotNone(overlay)
        assert overlay is not None
        self.assertEqual(overlay["status"], "LIVE_PARTIAL")
        self.assertEqual(overlay["coverage"], {"fresh": 1, "expected": 2})
        self.assertEqual(overlay["fallback_symbols"], ["QQQ"])
        self.assertEqual(overlay["metrics"]["current_value"], 2570.0)

    def test_all_quotes_missing_returns_no_live_point(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            LatestPortfolioQuotes,
            build_live_portfolio_overlay,
        )

        empty = LatestPortfolioQuotes.empty(self._scope(), due=False)
        overlay = build_live_portfolio_overlay(
            workspace=self._workspace(),
            scope=self._scope(),
            quotes=empty,
            eod_closes={"AMD": Decimal("100"), "QQQ": Decimal("200")},
            now=NOW,
        )

        self.assertIsNone(overlay)

    def test_live_returns_chain_from_eod_unit_value_with_modified_dietz(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_live_portfolio_overlay,
        )

        workspace = self._workspace(external_flow=Decimal("100"))
        workspace["active_group"]["metrics"]["current_value"] = Decimal("1500")
        workspace["active_group"]["curve"].loc[0, "total_value"] = 1500.0
        workspace["active_group"]["item_rows"] = (
            {
                "monitoring_item_id": "amd-item",
                "source_ref": "AMD",
                "current_value": Decimal("1000"),
                "total_return": Decimal("0.10"),
            },
            {
                "monitoring_item_id": "qqq-item",
                "source_ref": "QQQ",
                "current_value": Decimal("0"),
                "total_return": Decimal("0"),
            },
            {
                "monitoring_item_id": "strategy-item",
                "source_ref": "strategy-a",
                "current_value": Decimal("500"),
                "total_return": Decimal("0.25"),
            },
        )
        overlay = build_live_portfolio_overlay(
            workspace=workspace,
            scope=self._scope(),
            quotes=self._quotes(include_qqq=False),
            eod_closes={"AMD": Decimal("100"), "QQQ": Decimal("200")},
            now=NOW,
        )

        self.assertIsNotNone(overlay)
        assert overlay is not None
        # (1,550 - 1,500 - 100) / (1,500 + 0.5 * 100)
        expected_daily = Decimal("-50") / Decimal("1550")
        self.assertAlmostEqual(
            overlay["metrics"]["latest_observation_return"],
            float(expected_daily),
        )
        self.assertAlmostEqual(
            overlay["metrics"]["total_return"],
            float((Decimal("1.10") * (Decimal("1") + expected_daily)) - Decimal("1")),
        )

    def test_load_workspace_eod_closes_reads_only_group_basis_date(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            load_workspace_eod_closes,
        )

        calls = []
        closes = load_workspace_eod_closes(
            workspace=self._workspace(),
            scope=self._scope(),
            price_loader=lambda **kwargs: calls.append(kwargs) or pd.DataFrame(
                [
                    {"symbol": "AMD", "date": "2026-07-21", "close": 100.0},
                    {"symbol": "QQQ", "date": "2026-07-21", "close": 200.0},
                ]
            ),
        )

        self.assertEqual(closes, {"AMD": Decimal("100.0"), "QQQ": Decimal("200.0")})
        self.assertEqual(calls[0]["start"], "2026-07-21")
        self.assertEqual(calls[0]["end"], "2026-07-21")


class TodayPortfolioEodHandoffTests(unittest.TestCase):
    def _scope(self):
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_intraday_refresh_scope,
        )

        item = SimpleNamespace(
            monitoring_item_id="amd-item",
            source_ref="AMD",
            source_type="direct_security",
            instrument_kind="stock",
            status="active",
        )
        return build_intraday_refresh_scope(_group(), [item])

    def _closed_session(self, *, close_hour: int = 20):
        from app.services.portfolio_monitoring.intraday_refresh import (
            RegularSessionState,
        )

        return RegularSessionState(
            phase="CLOSED",
            trade_date=date(2026, 7, 22),
            open_at_utc=datetime(2026, 7, 22, 13, 30, tzinfo=timezone.utc),
            close_at_utc=datetime(2026, 7, 22, close_hour, 0, tzinfo=timezone.utc),
            collection_allowed=False,
        )

    def test_eod_handoff_starts_at_close_plus_five_minutes(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_eod_handoff_plan,
        )

        close = datetime(2026, 7, 22, 20, 0, tzinfo=timezone.utc)
        inputs = {
            "scope": self._scope(),
            "session": self._closed_session(),
            "latest_daily_dates": {"AMD": date(2026, 7, 21)},
        }
        before = build_eod_handoff_plan(
            **inputs,
            now=close + timedelta(seconds=299),
        )
        due = build_eod_handoff_plan(
            **inputs,
            now=close + timedelta(seconds=300),
        )

        self.assertFalse(before.due)
        self.assertTrue(due.due)
        self.assertEqual(due.missing_symbols, ("AMD",))

    def test_early_close_uses_scheduled_close_boundary(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_eod_handoff_plan,
        )

        early_close = datetime(2026, 7, 22, 17, 0, tzinfo=timezone.utc)
        plan = build_eod_handoff_plan(
            scope=self._scope(),
            session=self._closed_session(close_hour=17),
            latest_daily_dates={"AMD": date(2026, 7, 21)},
            now=early_close + timedelta(minutes=5),
        )

        self.assertTrue(plan.due)

    def test_confirmed_daily_date_disables_handoff(self) -> None:
        from app.services.portfolio_monitoring.intraday_refresh import (
            build_eod_handoff_plan,
        )

        plan = build_eod_handoff_plan(
            scope=self._scope(),
            session=self._closed_session(),
            latest_daily_dates={"AMD": date(2026, 7, 22)},
            now=datetime(2026, 7, 22, 20, 5, tzinfo=timezone.utc),
        )

        self.assertEqual(plan.status, "confirmed")
        self.assertFalse(plan.due)

if __name__ == "__main__":
    unittest.main()
