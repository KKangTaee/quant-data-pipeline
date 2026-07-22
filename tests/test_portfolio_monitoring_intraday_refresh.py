from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from types import SimpleNamespace


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


if __name__ == "__main__":
    unittest.main()
