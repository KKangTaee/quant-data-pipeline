from __future__ import annotations

from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Any

import streamlit as st

from app.services.portfolio_monitoring.intraday_refresh import (
    IntradayRefreshScope,
    LatestPortfolioQuotes,
    RegularSessionState,
    load_latest_portfolio_quotes,
    run_due_intraday_collection,
)


@dataclass(frozen=True)
class CoordinatorSnapshot:
    collection_state: str
    last_result: Mapping[str, Any] | None
    eod_state: str
    eod_attempt_count: int


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
    ) -> None:
        self._executor = executor or ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="today-intraday",
        )
        self._latest_loader = latest_loader
        self._quote_runner = quote_runner
        self._futures: dict[str, Any] = {}
        self._last_results: dict[str, Mapping[str, Any]] = {}
        self._guard = Lock()

    def _snapshot_unlocked(self, group_id: str) -> CoordinatorSnapshot:
        return CoordinatorSnapshot(
            collection_state=(
                "running" if group_id in self._futures else "idle"
            ),
            last_result=self._last_results.get(group_id),
            eod_state="not_applicable",
            eod_attempt_count=0,
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
    ) -> CoordinatorSnapshot:
        group_id = scope.portfolio_group_id
        with self._guard:
            future = self._futures.get(group_id)
            if future is not None and future.done():
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
                future = None

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
            return self._snapshot_unlocked(group_id)


@st.cache_resource
def get_today_intraday_coordinator() -> TodayIntradayCoordinator:
    return TodayIntradayCoordinator()


__all__ = [
    "CoordinatorSnapshot",
    "TodayIntradayCoordinator",
    "get_today_intraday_coordinator",
]
