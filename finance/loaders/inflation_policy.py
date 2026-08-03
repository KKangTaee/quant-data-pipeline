"""Strict DB-only point-in-time readers for inflation, policy, and yield paths."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from finance.data.db.mysql import MySQLClient
from finance.inflation_policy_catalog import get_inflation_policy_catalog


DB_META = "finance_meta"
DB_PRICE = "finance_price"
QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]


@dataclass(frozen=True)
class InflationPolicyDataBundle:
    as_of_at: str
    macro_rows: tuple[dict[str, object], ...]
    sep_rows: tuple[dict[str, object], ...]
    decision_rows: tuple[dict[str, object], ...]
    term_premium_rows: tuple[dict[str, object], ...]
    coverage: dict[str, object]
    spf_rows: tuple[dict[str, object], ...] = ()


@dataclass(frozen=True)
class InflationPolicyEquityBundle:
    """PIT-safe raw inputs for the independently gated equity component."""

    as_of_at: str
    price_rows: tuple[dict[str, object], ...]
    eps_rows: tuple[dict[str, object], ...]
    yield_rows: tuple[dict[str, object], ...]
    coverage: dict[str, object]


def _datetime_value(value: object, *, field: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, time.min)
    else:
        try:
            parsed = datetime.fromisoformat(
                str(value).strip().replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(f"Invalid {field}: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _date_value(value: object, *, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc


def _sql_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(tzinfo=None).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )


def _price_cutoff_date(value: object, *, as_of: datetime) -> date:
    """Return the latest US close logically known at an exact replay instant."""

    date_only = (
        isinstance(value, date)
        and not isinstance(value, datetime)
        or isinstance(value, str)
        and len(value.strip()) == 10
    )
    if date_only:
        return as_of.date()
    eastern = as_of.astimezone(ZoneInfo("America/New_York"))
    cutoff = eastern.date()
    # There is no collection timestamp on legacy daily rows. Before the regular
    # close, exclude the current US calendar day rather than leaking its close.
    if eastern.time() < time(16, 0):
        cutoff -= timedelta(days=1)
    return cutoff


def _query(
    database: str,
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(database, sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(database)
        return db.query(sql, params)
    except Exception as exc:
        message = str(exc).casefold()
        if ("doesn't exist" in message or "unknown table" in message) and any(
            table in message
            for table in (
                "macro_series_vintage_observation",
                "fomc_sep_distribution",
                "fomc_policy_decision",
                "spf_core_pce_probability",
                "inflation_policy_snapshot",
                "inflation_policy_model_artifact",
                "yield_resistance_definition",
            )
        ):
            return []
        raise
    finally:
        db.close()


def _release_eligible(row: Mapping[str, object], *, as_of: datetime) -> bool:
    released_at = row.get("released_at")
    if released_at in (None, ""):
        return False
    try:
        return _datetime_value(released_at, field="released_at") <= as_of
    except ValueError:
        return False


def _sort_timestamp(value: object) -> datetime:
    if value in (None, ""):
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        return _datetime_value(value, field="timestamp")
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def _latest_vintages(
    rows: Iterable[Mapping[str, object]],
    *,
    as_of: datetime,
    history_start: date,
    allowed_series: set[str] | None = None,
    allow_component_group: bool = False,
) -> tuple[dict[str, object], ...]:
    latest: dict[tuple[str, date], dict[str, object]] = {}
    for raw in rows:
        row = dict(raw)
        series_id = str(row.get("series_id") or "").strip().upper()
        is_component = (
            allow_component_group
            and str(row.get("factor_group") or "") == "inflation_pce_component"
        )
        if not series_id or (
            allowed_series is not None
            and series_id not in allowed_series
            and not is_component
        ):
            continue
        try:
            observation = _date_value(
                row.get("observation_date"), field="observation_date"
            )
        except ValueError:
            continue
        if not history_start <= observation <= as_of.date():
            continue
        if not _release_eligible(row, as_of=as_of):
            continue
        key = (series_id, observation)
        candidate_key = (
            _sort_timestamp(row.get("released_at")),
            _sort_timestamp(row.get("realtime_start")),
            _sort_timestamp(row.get("collected_at")),
            _sort_timestamp(row.get("updated_at")),
        )
        current = latest.get(key)
        if current is None:
            latest[key] = row
            continue
        current_key = (
            _sort_timestamp(current.get("released_at")),
            _sort_timestamp(current.get("realtime_start")),
            _sort_timestamp(current.get("collected_at")),
            _sort_timestamp(current.get("updated_at")),
        )
        if candidate_key > current_key:
            latest[key] = row
    return tuple(
        latest[key]
        for key in sorted(latest, key=lambda item: (item[0], item[1]))
    )


def _released_rows(
    rows: Iterable[Mapping[str, object]],
    *,
    as_of: datetime,
    date_field: str,
) -> tuple[dict[str, object], ...]:
    eligible: list[dict[str, object]] = []
    for raw in rows:
        row = dict(raw)
        if not _release_eligible(row, as_of=as_of):
            continue
        eligible.append(row)
    return tuple(
        sorted(
            eligible,
            key=lambda row: (
                str(row.get(date_field) or ""),
                _sort_timestamp(row.get("released_at")),
                str(row.get("variable_name") or ""),
                str(row.get("bin_label") or ""),
            ),
        )
    )


def load_inflation_policy_data_bundle(
    *,
    as_of_at: str | datetime,
    history_start: str | date,
    query_fn: QueryFn | None = None,
) -> InflationPolicyDataBundle:
    """Load only versions actually released by one forecast origin."""

    as_of = _datetime_value(as_of_at, field="as_of_at")
    start = _date_value(history_start, field="history_start")
    if start > as_of.date():
        raise ValueError("history_start cannot be after as_of_at")
    catalog_ids = tuple(spec.series_id for spec in get_inflation_policy_catalog())
    placeholders = ",".join(["%s"] * len(catalog_ids))
    as_of_sql = _sql_datetime(as_of)

    macro_sql = f"""
    WITH eligible_versions AS (
      SELECT source_rows.*,
             ROW_NUMBER() OVER (
               PARTITION BY series_id, observation_date
               ORDER BY released_at DESC, realtime_start DESC,
                        collected_at DESC, updated_at DESC
             ) AS version_rank
      FROM macro_series_vintage_observation source_rows
      WHERE (series_id IN ({placeholders})
             OR factor_group = 'inflation_pce_component')
        AND observation_date >= %s
        AND observation_date <= %s
        AND released_at IS NOT NULL
        AND released_at <= %s
    )
    SELECT * FROM eligible_versions
    WHERE version_rank = 1
    ORDER BY series_id, observation_date
    """
    macro_raw = _query(
        DB_META,
        macro_sql,
        (*catalog_ids, start.isoformat(), as_of.date().isoformat(), as_of_sql),
        query_fn=query_fn,
    )
    macro_rows = _latest_vintages(
        macro_raw,
        as_of=as_of,
        history_start=start,
        allowed_series=set(catalog_ids),
        allow_component_group=True,
    )

    sep_sql = """
    SELECT * FROM fomc_sep_distribution
    WHERE released_at IS NOT NULL
      AND released_at <= %s
    ORDER BY released_at, target_period, variable_name, distribution_kind, bin_label
    """
    sep_rows = _released_rows(
        _query(DB_META, sep_sql, (as_of_sql,), query_fn=query_fn),
        as_of=as_of,
        date_field="released_at",
    )

    decision_sql = """
    SELECT * FROM fomc_policy_decision
    WHERE released_at IS NOT NULL
      AND released_at <= %s
    ORDER BY meeting_date, released_at
    """
    decision_rows = _released_rows(
        _query(DB_META, decision_sql, (as_of_sql,), query_fn=query_fn),
        as_of=as_of,
        date_field="meeting_date",
    )

    spf_sql = """
    SELECT * FROM spf_core_pce_probability
    WHERE released_at IS NOT NULL
      AND released_at <= %s
    ORDER BY released_at, target_year, bin_number
    """
    spf_rows = _released_rows(
        _query(DB_META, spf_sql, (as_of_sql,), query_fn=query_fn),
        as_of=as_of,
        date_field="released_at",
    )

    term_sql = """
    WITH eligible_versions AS (
      SELECT source_rows.*,
             ROW_NUMBER() OVER (
               PARTITION BY series_id, observation_date
               ORDER BY released_at DESC, realtime_start DESC,
                        collected_at DESC, updated_at DESC
             ) AS version_rank
      FROM macro_series_vintage_observation source_rows
      WHERE series_id = 'ACMTP10'
        AND observation_date >= %s
        AND observation_date <= %s
        AND released_at IS NOT NULL
        AND released_at <= %s
    )
    SELECT * FROM eligible_versions
    WHERE version_rank = 1
    ORDER BY observation_date
    """
    term_rows = _latest_vintages(
        _query(
            DB_META,
            term_sql,
            (start.isoformat(), as_of.date().isoformat(), as_of_sql),
            query_fn=query_fn,
        ),
        as_of=as_of,
        history_start=start,
        allowed_series={"ACMTP10"},
    )

    present_series = sorted(
        {
            str(row.get("series_id") or "").strip().upper()
            for row in macro_rows
            if row.get("series_id")
        }
    )
    coverage: dict[str, object] = {
        "catalog_series_requested": len(catalog_ids),
        "catalog_series_present": present_series,
        "catalog_series_missing": sorted(set(catalog_ids) - set(present_series)),
        "sep_status": "READY" if sep_rows else "NOT_AVAILABLE",
        "decision_status": "READY" if decision_rows else "NOT_AVAILABLE",
        "spf_core_pce_status": "READY" if spf_rows else "NOT_AVAILABLE",
        # Current ACM workbooks revise history, so availability does not remove
        # the historical-replay limitation recorded by the collector.
        "term_premium_status": "LIMITED" if term_rows else "NOT_AVAILABLE",
    }
    return InflationPolicyDataBundle(
        as_of_at=as_of.isoformat(),
        macro_rows=macro_rows,
        sep_rows=sep_rows,
        decision_rows=decision_rows,
        term_premium_rows=term_rows,
        coverage=coverage,
        spf_rows=spf_rows,
    )


def load_inflation_policy_equity_bundle(
    *,
    as_of_at: str | datetime,
    history_start: str | date,
    query_fn: QueryFn | None = None,
) -> InflationPolicyEquityBundle:
    """Load official EPS vintages, S&P 500 prices, and yield vintages known then."""

    as_of = _datetime_value(as_of_at, field="as_of_at")
    start = _date_value(history_start, field="history_start")
    if start > as_of.date():
        raise ValueError("history_start cannot be after as_of_at")
    as_of_sql = _sql_datetime(as_of)
    price_cutoff = _price_cutoff_date(as_of_at, as_of=as_of)

    eps_raw = _query(
        DB_META,
        """
        SELECT period_end, period_type, earnings_basis, value_status, eps,
               source, source_ref, source_release_date, collected_at
        FROM sp500_index_earnings
        WHERE period_type = 'quarterly'
          AND eps > 0
          AND source_release_date <= %s
          AND period_end >= %s
        ORDER BY source_release_date, period_end, earnings_basis, value_status
        """,
        (as_of.date().isoformat(), start.isoformat()),
        query_fn=query_fn,
    )
    eps_rows: list[dict[str, object]] = []
    for raw in eps_raw:
        row = dict(raw)
        try:
            release_date = _date_value(
                row.get("source_release_date"), field="source_release_date"
            )
            period_end = _date_value(row.get("period_end"), field="period_end")
            value = float(row.get("eps"))
        except (TypeError, ValueError):
            continue
        if release_date > as_of.date() or period_end < start or value <= 0.0:
            continue
        if str(row.get("period_type") or "quarterly").lower() != "quarterly":
            continue
        row["source_release_date"] = release_date.isoformat()
        row["period_end"] = period_end.isoformat()
        eps_rows.append(row)

    price_raw = _query(
        DB_PRICE,
        """
        SELECT symbol, Date, Close
        FROM nyse_price_history
        WHERE symbol = '^GSPC'
          AND Date >= %s
          AND Date <= %s
          AND Close > 0
        ORDER BY Date
        """,
        (start.isoformat(), price_cutoff.isoformat()),
        query_fn=query_fn,
    )
    price_rows: list[dict[str, object]] = []
    for raw in price_raw:
        row = dict(raw)
        try:
            observed = _date_value(row.get("Date"), field="Date")
            close = float(row.get("Close"))
        except (TypeError, ValueError):
            continue
        if not start <= observed <= price_cutoff or close <= 0.0:
            continue
        row["Date"] = observed.isoformat()
        row["Close"] = close
        price_rows.append(row)

    yield_raw = _query(
        DB_META,
        """
        SELECT series_id, observation_date, released_at, realtime_start,
               realtime_end, value, collected_at, updated_at
        FROM macro_series_vintage_observation
        WHERE series_id IN ('DGS2', 'DGS10', 'DFII10', 'T10YIE', 'PCEPILFE')
          AND observation_date >= %s
          AND observation_date <= %s
          AND released_at IS NOT NULL
          AND released_at <= %s
        ORDER BY series_id, observation_date, released_at
        """,
        (start.isoformat(), as_of.date().isoformat(), as_of_sql),
        query_fn=query_fn,
    )
    yield_rows = _released_rows(
        yield_raw,
        as_of=as_of,
        date_field="observation_date",
    )
    return InflationPolicyEquityBundle(
        as_of_at=as_of.isoformat(),
        price_rows=tuple(sorted(price_rows, key=lambda row: str(row["Date"]))),
        eps_rows=tuple(
            sorted(
                eps_rows,
                key=lambda row: (
                    str(row["source_release_date"]),
                    str(row["period_end"]),
                    str(row.get("earnings_basis") or ""),
                ),
            )
        ),
        yield_rows=yield_rows,
        coverage={
            "official_eps_vintage_status": "READY" if eps_rows else "NOT_AVAILABLE",
            "official_eps_vintage_rows": len(eps_rows),
            "sp500_price_status": "READY" if price_rows else "NOT_AVAILABLE",
            "sp500_price_rows": len(price_rows),
            "yield_status": "READY" if yield_rows else "NOT_AVAILABLE",
            "yield_rows": len(yield_rows),
        },
    )


def load_inflation_policy_training_vintages(
    *,
    as_of_at: str | datetime,
    history_start: str | date,
    series_ids: Iterable[str],
    query_fn: QueryFn | None = None,
) -> tuple[dict[str, object], ...]:
    """Load every eligible vintage needed to reconstruct historical origins."""

    as_of = _datetime_value(as_of_at, field="as_of_at")
    start = _date_value(history_start, field="history_start")
    if start > as_of.date():
        raise ValueError("history_start cannot be after as_of_at")
    approved = tuple(
        dict.fromkeys(str(value).strip().upper() for value in series_ids if str(value).strip())
    )
    if not approved:
        raise ValueError("series_ids cannot be empty")
    placeholders = ",".join(["%s"] * len(approved))
    sql = f"""
    SELECT * FROM macro_series_vintage_observation
    WHERE series_id IN ({placeholders})
      AND observation_date >= %s
      AND observation_date <= %s
      AND released_at IS NOT NULL
      AND released_at <= %s
    ORDER BY series_id, observation_date, released_at, realtime_start
    """
    raw_rows = _query(
        DB_META,
        sql,
        (
            *approved,
            start.isoformat(),
            as_of.date().isoformat(),
            _sql_datetime(as_of),
        ),
        query_fn=query_fn,
    )
    eligible: list[dict[str, object]] = []
    for raw in raw_rows:
        row = dict(raw)
        series_id = str(row.get("series_id") or "").strip().upper()
        if series_id not in approved:
            continue
        try:
            observation = _date_value(
                row.get("observation_date"), field="observation_date"
            )
        except ValueError:
            continue
        if not start <= observation <= as_of.date() or not _release_eligible(
            row, as_of=as_of
        ):
            continue
        row["series_id"] = series_id
        eligible.append(row)
    return tuple(
        sorted(
            eligible,
            key=lambda row: (
                str(row.get("series_id") or ""),
                str(row.get("observation_date") or ""),
                _sort_timestamp(row.get("released_at")),
                str(row.get("realtime_start") or ""),
            ),
        )
    )


def load_latest_inflation_policy_snapshot(
    *,
    as_of_at: str | datetime | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, object] | None:
    """Return the latest persisted snapshot no later than the requested time."""

    as_of = _datetime_value(
        as_of_at or datetime.now(timezone.utc), field="as_of_at"
    )
    sql = """
    SELECT * FROM inflation_policy_snapshot
    WHERE as_of_at <= %s
    ORDER BY as_of_at DESC, updated_at DESC
    """
    rows = _query(DB_META, sql, (_sql_datetime(as_of),), query_fn=query_fn)
    eligible: list[dict[str, object]] = []
    for raw in rows:
        row = dict(raw)
        try:
            row_as_of = _datetime_value(row.get("as_of_at"), field="as_of_at")
        except ValueError:
            continue
        if row_as_of <= as_of:
            eligible.append(row)
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda row: (
            _sort_timestamp(row.get("as_of_at")),
            _sort_timestamp(row.get("updated_at")),
        ),
    )


def load_yield_resistance_definitions(
    *,
    as_of_at: str | datetime | None = None,
    include_inactive: bool = False,
    query_fn: QueryFn | None = None,
) -> tuple[dict[str, object], ...]:
    """Return definitions that were known and saved by one point in time."""

    as_of = _datetime_value(
        as_of_at or datetime.now(timezone.utc), field="as_of_at"
    )
    active_clause = "" if include_inactive else "AND is_active = 1"
    sql = f"""
    SELECT * FROM yield_resistance_definition
    WHERE known_at <= %s
      AND saved_at <= %s
      {active_clause}
    ORDER BY owner, instrument, zone_lower_pct, saved_at
    """
    rows = _query(
        DB_META,
        sql,
        (_sql_datetime(as_of), _sql_datetime(as_of)),
        query_fn=query_fn,
    )
    eligible: list[dict[str, object]] = []
    for raw in rows:
        row = dict(raw)
        try:
            known_at = _datetime_value(row.get("known_at"), field="known_at")
            saved_at = _datetime_value(row.get("saved_at"), field="saved_at")
        except ValueError:
            continue
        if known_at > as_of or saved_at > as_of:
            continue
        if not include_inactive and not bool(row.get("is_active", 0)):
            continue
        eligible.append(row)
    return tuple(
        sorted(
            eligible,
            key=lambda row: (
                str(row.get("owner") or ""),
                str(row.get("instrument") or ""),
                float(row.get("zone_lower_pct") or 0.0),
                _sort_timestamp(row.get("saved_at")),
            ),
        )
    )


def load_inflation_policy_model_artifact(
    *,
    model_version: str,
    trained_cutoff_at: str | datetime,
    component: str,
    query_fn: QueryFn | None = None,
) -> dict[str, object] | None:
    """Load one artifact only when its complete training identity matches."""

    version = str(model_version).strip()
    component_name = str(component).strip()
    if not version or not component_name:
        raise ValueError("model_version and component cannot be empty")
    trained_cutoff = _datetime_value(
        trained_cutoff_at, field="trained_cutoff_at"
    )
    sql = """
    SELECT * FROM inflation_policy_model_artifact
    WHERE model_version = %s
      AND trained_cutoff_at = %s
      AND component = %s
    ORDER BY updated_at DESC
    """
    rows = _query(
        DB_META,
        sql,
        (version, _sql_datetime(trained_cutoff), component_name),
        query_fn=query_fn,
    )
    for raw in rows:
        row = dict(raw)
        try:
            row_cutoff = _datetime_value(
                row.get("trained_cutoff_at"), field="trained_cutoff_at"
            )
        except ValueError:
            continue
        if (
            str(row.get("model_version") or "") == version
            and row_cutoff == trained_cutoff
            and str(row.get("component") or "") == component_name
        ):
            return row
    return None
