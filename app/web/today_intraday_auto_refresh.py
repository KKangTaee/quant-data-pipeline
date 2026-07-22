from __future__ import annotations

from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime
from threading import Lock
from typing import Any

import streamlit as st

from app.services.portfolio_monitoring.intraday_refresh import (
    EOD_MAX_ATTEMPTS,
    EOD_RETRY_SECONDS,
    IntradayRefreshScope,
    LatestPortfolioQuotes,
    RegularSessionState,
    build_eod_handoff_plan,
    load_latest_portfolio_quotes,
    run_due_intraday_collection,
)
from app.services.portfolio_monitoring.price_refresh import (
    run_portfolio_price_refresh,
)


@dataclass(frozen=True)
class CoordinatorSnapshot:
    collection_state: str
    last_result: Mapping[str, Any] | None
    eod_state: str
    eod_attempt_count: int
    eod_missing_symbols: tuple[str, ...]


class TodayIntradayCoordinator:
    """Own one non-blocking quote future per portfolio group."""

    def __init__(
        self,
        *,
        executor: Any | None = None,
        latest_loader: Callable[..., LatestPortfolioQuotes] = (
            load_latest_portfolio_quotes
        ),
        quote_runner: Callable[..., dict[str, Any]] = (
            run_due_intraday_collection
        ),
        eod_runner: Callable[..., Mapping[str, Any]] = (
            run_portfolio_price_refresh
        ),
    ) -> None:
        self._executor = executor or ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="today-intraday",
        )
        self._latest_loader = latest_loader
        self._quote_runner = quote_runner
        self._eod_runner = eod_runner
        self._futures: dict[str, Any] = {}
        self._future_kinds: dict[str, str] = {}
        self._last_results: dict[str, Mapping[str, Any]] = {}
        self._eod_states: dict[str, str] = {}
        self._eod_attempts: dict[str, int] = {}
        self._eod_last_submitted: dict[str, datetime] = {}
        self._eod_trade_dates: dict[str, date] = {}
        self._eod_missing_symbols: dict[str, tuple[str, ...]] = {}
        self._guard = Lock()

    def _snapshot_unlocked(self, group_id: str) -> CoordinatorSnapshot:
        return CoordinatorSnapshot(
            collection_state=(
                "running" if group_id in self._futures else "idle"
            ),
            last_result=self._last_results.get(group_id),
            eod_state=self._eod_states.get(group_id, "not_applicable"),
            eod_attempt_count=self._eod_attempts.get(group_id, 0),
            eod_missing_symbols=self._eod_missing_symbols.get(group_id, ()),
        )

    def snapshot(self, portfolio_group_id: str) -> CoordinatorSnapshot:
        with self._guard:
            return self._snapshot_unlocked(portfolio_group_id)

    def tick(
        self,
        *,
        scope: IntradayRefreshScope,
        session: RegularSessionState,
        now: datetime,
        latest_daily_dates: Mapping[str, date | str] | None = None,
    ) -> CoordinatorSnapshot:
        group_id = scope.portfolio_group_id
        with self._guard:
            future = self._futures.get(group_id)
            if future is not None and future.done():
                future_kind = self._future_kinds.pop(group_id, "quote")
                try:
                    completed = future.result()
                    self._last_results[group_id] = (
                        dict(completed)
                        if isinstance(completed, Mapping)
                        else {"status": "completed"}
                    )
                except Exception as exc:
                    self._last_results[group_id] = {
                        "status": "failed",
                        "message": str(exc),
                    }
                self._futures.pop(group_id, None)
                if future_kind == "eod":
                    self._eod_states[group_id] = "waiting"
                future = None

            if (
                session.trade_date is not None
                and self._eod_trade_dates.get(group_id) != session.trade_date
            ):
                self._eod_trade_dates[group_id] = session.trade_date
                self._eod_attempts[group_id] = 0
                self._eod_last_submitted.pop(group_id, None)

            eod_plan = build_eod_handoff_plan(
                scope=scope,
                session=session,
                latest_daily_dates=latest_daily_dates or {},
                now=now,
            )
            self._eod_missing_symbols[group_id] = eod_plan.missing_symbols
            if eod_plan.status == "confirmed":
                self._eod_states[group_id] = "confirmed"
                self._eod_attempts[group_id] = 0
                self._eod_last_submitted.pop(group_id, None)
                return self._snapshot_unlocked(group_id)
            if eod_plan.status == "waiting":
                attempts = self._eod_attempts.get(group_id, 0)
                running_eod = (
                    future is not None
                    and self._future_kinds.get(group_id) == "eod"
                )
                if running_eod:
                    self._eod_states[group_id] = "running"
                    return self._snapshot_unlocked(group_id)
                if attempts >= EOD_MAX_ATTEMPTS:
                    self._eod_states[group_id] = "exhausted"
                    return self._snapshot_unlocked(group_id)
                self._eod_states[group_id] = "waiting"
                last_submitted = self._eod_last_submitted.get(group_id)
                cadence_ready = (
                    last_submitted is None
                    or (now - last_submitted).total_seconds()
                    >= EOD_RETRY_SECONDS
                )
                if (
                    eod_plan.due
                    and future is None
                    and cadence_ready
                ):
                    self._futures[group_id] = self._executor.submit(
                        self._eod_runner,
                        list(scope.items),
                        now=now,
                    )
                    self._future_kinds[group_id] = "eod"
                    self._eod_attempts[group_id] = attempts + 1
                    self._eod_last_submitted[group_id] = now
                    self._eod_states[group_id] = "running"
                return self._snapshot_unlocked(group_id)

            self._eod_states[group_id] = "not_applicable"

            if (
                not session.collection_allowed
                or not scope.symbols
                or future is not None
            ):
                return self._snapshot_unlocked(group_id)

            try:
                latest = self._latest_loader(scope, now=now)
            except Exception as exc:
                self._last_results[group_id] = {
                    "status": "failed",
                    "message": str(exc),
                }
                return self._snapshot_unlocked(group_id)
            if not latest.due:
                return self._snapshot_unlocked(group_id)

            self._futures[group_id] = self._executor.submit(
                self._quote_runner,
                scope=scope,
                now=now,
            )
            self._future_kinds[group_id] = "quote"
            return self._snapshot_unlocked(group_id)


@st.cache_resource
def get_today_intraday_coordinator() -> TodayIntradayCoordinator:
    return TodayIntradayCoordinator()


__all__ = [
    "CoordinatorSnapshot",
    "TodayIntradayCoordinator",
    "get_today_intraday_coordinator",
]
