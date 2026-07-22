from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
from typing import Any, Iterator
from zoneinfo import ZoneInfo

from finance.data.db.mysql import MySQLClient
from finance.data.market_intelligence import (
    collect_and_store_symbol_intraday_snapshot,
)

from .persistence import MonitoringItemRecord, PortfolioGroupRecord


DB_PRICE = "finance_price"
INTRADAY_INTERVAL = "5m"
INTRADAY_CADENCE_SECONDS = 300
QUOTE_STALE_SECONDS = 600
TODAY_INTRADAY_MAX_SYMBOLS = 10
ACTIVE_ITEM_STATUSES = {"active", "data_review"}
DIRECT_INSTRUMENT_KINDS = {"stock", "etf"}


@dataclass(frozen=True)
class IntradayRefreshScope:
    portfolio_group_id: str
    universe_code: str
    symbols: tuple[str, ...]
    items: tuple[MonitoringItemRecord, ...]


@dataclass(frozen=True)
class RegularSessionState:
    phase: str
    trade_date: date | None
    open_at_utc: datetime | None
    close_at_utc: datetime | None
    collection_allowed: bool


@dataclass(frozen=True)
class LatestPortfolioQuotes:
    status: str
    attempt_time_utc: datetime | None
    quote_time_utc: datetime | None
    quotes: Mapping[str, Mapping[str, Any]]
    fresh_symbols: tuple[str, ...]
    fallback_symbols: tuple[str, ...]
    due: bool

    @classmethod
    def empty(
        cls,
        scope: IntradayRefreshScope,
        *,
        due: bool,
    ) -> "LatestPortfolioQuotes":
        return cls(
            status="NO_ATTEMPT",
            attempt_time_utc=None,
            quote_time_utc=None,
            quotes={},
            fresh_symbols=(),
            fallback_symbols=scope.symbols,
            due=due,
        )


def _price_db_factory() -> MySQLClient:
    return MySQLClient("localhost", "root", "1234", 3306)


def _normalized_symbol(value: Any) -> str:
    return str(value or "").strip().upper().replace(".", "-")


def _as_utc(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value or "").strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _positive_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def portfolio_intraday_universe_code(portfolio_group_id: str) -> str:
    group_id = str(portfolio_group_id or "").strip()
    if not group_id:
        raise ValueError("portfolio_group_id is required.")
    digest = sha256(group_id.encode("utf-8")).hexdigest()[:16].upper()
    return f"TODAY_{digest}"


def build_intraday_refresh_scope(
    group: PortfolioGroupRecord | Any,
    items: Sequence[MonitoringItemRecord | Any],
) -> IntradayRefreshScope:
    """Select the default group's active direct stocks and ETFs."""

    group_id = str(getattr(group, "portfolio_group_id", "") or "").strip()
    if not group_id:
        raise ValueError("A persisted portfolio group is required.")
    eligible = tuple(
        item
        for item in items
        if str(getattr(item, "status", "") or "").strip().lower()
        in ACTIVE_ITEM_STATUSES
        and str(getattr(item, "source_type", "") or "").strip().lower()
        == "direct_security"
        and str(getattr(item, "instrument_kind", "") or "").strip().lower()
        in DIRECT_INSTRUMENT_KINDS
        and _normalized_symbol(getattr(item, "source_ref", None))
    )
    symbols = tuple(
        sorted(
            {
                _normalized_symbol(getattr(item, "source_ref", None))
                for item in eligible
            }
        )
    )
    if len(symbols) > TODAY_INTRADAY_MAX_SYMBOLS:
        raise ValueError("Today intraday refresh supports at most 10 symbols.")
    return IntradayRefreshScope(
        portfolio_group_id=group_id,
        universe_code=portfolio_intraday_universe_code(group_id),
        symbols=symbols,
        items=eligible,
    )


def resolve_regular_session_state(
    market_session: Mapping[str, Any] | Any,
    now: datetime,
) -> RegularSessionState:
    """Resolve the server-side regular-session gate from the Today schedule."""

    current = _as_utc(now)
    if current is None:
        raise ValueError("An aware or UTC-compatible current time is required.")
    payload = dict(market_session) if isinstance(market_session, Mapping) else {}
    if str(payload.get("calendar_quality") or "").upper() != "CONFIRMED":
        return RegularSessionState("STALE", None, None, None, False)
    timezones = dict(payload.get("timezones") or {})
    market_timezone = ZoneInfo(
        str(timezones.get("market") or "America/New_York")
    )
    local_date = current.astimezone(market_timezone).date()
    schedule = [
        dict(row)
        for row in payload.get("schedule") or []
        if isinstance(row, Mapping)
    ]
    row = next(
        (
            item
            for item in schedule
            if str(item.get("trade_date") or "") == local_date.isoformat()
        ),
        None,
    )
    if row is None:
        return RegularSessionState("STALE", None, None, None, False)
    trade_date = date.fromisoformat(str(row["trade_date"]))
    day_kind = str(row.get("day_kind") or "").upper()
    if day_kind in {"HOLIDAY", "WEEKEND"}:
        return RegularSessionState(day_kind, trade_date, None, None, False)
    if day_kind != "TRADING_DAY":
        return RegularSessionState("STALE", trade_date, None, None, False)
    open_at = _as_utc(row.get("open_at_utc"))
    close_at = _as_utc(row.get("close_at_utc"))
    if open_at is None or close_at is None or close_at <= open_at:
        return RegularSessionState("STALE", trade_date, None, None, False)
    if current < open_at:
        phase = "PRE_OPEN"
    elif current < close_at:
        phase = "OPEN"
    else:
        phase = "CLOSED"
    return RegularSessionState(
        phase=phase,
        trade_date=trade_date,
        open_at_utc=open_at,
        close_at_utc=close_at,
        collection_allowed=phase == "OPEN",
    )


def _load_latest_portfolio_quote_rows(
    scope: IntradayRefreshScope,
    *,
    db: MySQLClient | Any,
) -> list[dict[str, Any]]:
    if not scope.symbols:
        return []
    placeholders = ",".join(["%s"] * len(scope.symbols))
    return db.query(
        f"""
        SELECT
          s.symbol, s.snapshot_time_utc, s.quote_time_utc,
          s.latest_price, s.previous_close, s.return_pct, s.volume,
          s.provider_status, s.error_msg, s.source, s.source_ref
        FROM market_intraday_snapshot s
        JOIN (
          SELECT MAX(snapshot_time_utc) AS snapshot_time_utc
          FROM market_intraday_snapshot
          WHERE universe_code = %s AND interval_code = %s
        ) latest
          ON latest.snapshot_time_utc = s.snapshot_time_utc
        WHERE s.universe_code = %s
          AND s.interval_code = %s
          AND s.symbol IN ({placeholders})
        ORDER BY s.symbol ASC
        """,
        [
            scope.universe_code,
            INTRADAY_INTERVAL,
            scope.universe_code,
            INTRADAY_INTERVAL,
            *scope.symbols,
        ],
    )


def load_latest_portfolio_quotes(
    scope: IntradayRefreshScope,
    *,
    now: datetime | None = None,
    db_factory: Callable[[], MySQLClient | Any] = _price_db_factory,
) -> LatestPortfolioQuotes:
    """Read one group's durable latest attempt and classify fresh coverage."""

    current = _as_utc(now or datetime.now(timezone.utc))
    if current is None:
        raise ValueError("now is required.")
    if not scope.symbols:
        return LatestPortfolioQuotes.empty(scope, due=False)
    db = db_factory()
    try:
        db.use_db(DB_PRICE)
        rows = _load_latest_portfolio_quote_rows(scope, db=db)
    finally:
        db.close()
    if not rows:
        return LatestPortfolioQuotes.empty(scope, due=True)

    attempt_times = [
        parsed
        for row in rows
        if (parsed := _as_utc(row.get("snapshot_time_utc"))) is not None
    ]
    attempt_time = max(attempt_times) if attempt_times else None
    due = (
        attempt_time is None
        or (current - attempt_time).total_seconds()
        >= INTRADAY_CADENCE_SECONDS
    )
    fresh_quotes: dict[str, dict[str, Any]] = {}
    quote_times: list[datetime] = []
    has_stale_ok = False
    for raw_row in rows:
        row = dict(raw_row)
        symbol = _normalized_symbol(row.get("symbol"))
        quote_time = _as_utc(row.get("quote_time_utc"))
        quote_price = _positive_float(row.get("latest_price"))
        provider_ok = str(row.get("provider_status") or "").lower() == "ok"
        age_seconds = (
            (current - quote_time).total_seconds()
            if quote_time is not None
            else None
        )
        fresh = (
            symbol in scope.symbols
            and provider_ok
            and quote_price is not None
            and age_seconds is not None
            and age_seconds <= QUOTE_STALE_SECONDS
        )
        if fresh:
            row["symbol"] = symbol
            row["latest_price"] = quote_price
            fresh_quotes[symbol] = row
            quote_times.append(quote_time)
        elif provider_ok:
            has_stale_ok = True

    fresh_symbols = tuple(
        symbol for symbol in scope.symbols if symbol in fresh_quotes
    )
    fallback_symbols = tuple(
        symbol for symbol in scope.symbols if symbol not in fresh_quotes
    )
    if len(fresh_symbols) == len(scope.symbols):
        status = "LIVE_READY"
    elif fresh_symbols:
        status = "LIVE_PARTIAL"
    elif has_stale_ok:
        status = "STALE"
    else:
        status = "FAILED"
    return LatestPortfolioQuotes(
        status=status,
        attempt_time_utc=attempt_time,
        quote_time_utc=max(quote_times) if quote_times else None,
        quotes=fresh_quotes,
        fresh_symbols=fresh_symbols,
        fallback_symbols=fallback_symbols,
        due=due,
    )


@contextmanager
def portfolio_refresh_lock(
    db: MySQLClient | Any,
    universe_code: str,
) -> Iterator[bool]:
    lock_name = f"today_intraday:{universe_code}"
    acquired_rows = db.query(
        "SELECT GET_LOCK(%s, 0) AS acquired",
        [lock_name],
    )
    acquired = bool(
        acquired_rows
        and int(acquired_rows[0].get("acquired") or 0) == 1
    )
    try:
        yield acquired
    finally:
        if acquired:
            db.query(
                "SELECT RELEASE_LOCK(%s) AS released",
                [lock_name],
            )


def run_due_intraday_collection(
    scope: IntradayRefreshScope,
    *,
    now: datetime | None = None,
    db_factory: Callable[[], MySQLClient | Any] = _price_db_factory,
    latest_loader: Callable[..., LatestPortfolioQuotes] = load_latest_portfolio_quotes,
    collector: Callable[..., dict[str, Any]] = collect_and_store_symbol_intraday_snapshot,
) -> dict[str, Any]:
    """Collect once when the durable group attempt is due and lock is owned."""

    if not scope.symbols:
        return {"status": "no_symbols", "rows_written": 0}
    current = _as_utc(now or datetime.now(timezone.utc))
    if current is None:
        raise ValueError("now is required.")
    latest = latest_loader(scope, now=current, db_factory=db_factory)
    if not latest.due:
        return {"status": "not_due", "rows_written": 0}

    db = db_factory()
    try:
        db.use_db(DB_PRICE)
        with portfolio_refresh_lock(db, scope.universe_code) as acquired:
            if not acquired:
                return {"status": "lock_contended", "rows_written": 0}
            latest = latest_loader(scope, now=current, db_factory=db_factory)
            if not latest.due:
                return {"status": "not_due", "rows_written": 0}
            result = collector(
                symbols=scope.symbols,
                universe_code=scope.universe_code,
                source_ref=(
                    f"portfolio_group_id={scope.portfolio_group_id}"
                ),
                interval=INTRADAY_INTERVAL,
                snapshot_time_utc=current,
            )
            return {
                "status": "submitted_result",
                "rows_written": int(result.get("rows_written") or 0),
                "details": dict(result),
            }
    except Exception as exc:
        return {
            "status": "failed",
            "rows_written": 0,
            "message": str(exc),
        }
    finally:
        db.close()


__all__ = [
    "INTRADAY_CADENCE_SECONDS",
    "QUOTE_STALE_SECONDS",
    "IntradayRefreshScope",
    "LatestPortfolioQuotes",
    "RegularSessionState",
    "build_intraday_refresh_scope",
    "load_latest_portfolio_quotes",
    "portfolio_intraday_universe_code",
    "resolve_regular_session_state",
    "run_due_intraday_collection",
]
