"""Finalize a same-date futures daily session on explicit refresh."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from typing import Any

from app.services.futures_macro_sessions import (
    FUTURES_DAILY_SETTLEMENT_STABLE_ET,
    NEW_YORK,
    resolve_futures_daily_session,
)
from finance.data.futures_session_finalization import (
    build_session_finalization_batch,
    futures_session_window_utc,
    load_latest_futures_daily_rows,
    load_stored_futures_intraday_rows,
    write_futures_daily_finalization,
)


FinalizationResult = dict[str, Any]


def _normalized_symbols(symbols: Sequence[str]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            str(symbol).strip().upper()
            for symbol in symbols
            if str(symbol).strip()
        )
    )


def _result(
    *,
    status: str,
    session_date: str | None,
    required_symbols: Sequence[str],
    symbols_finalized: int = 0,
    missing_symbols: Sequence[str] = (),
    reason: str,
) -> FinalizationResult:
    return {
        "status": status,
        "session_date": session_date,
        "symbols_required": len(required_symbols),
        "symbols_finalized": int(symbols_finalized),
        "missing_symbols": list(missing_symbols),
        "reason": reason,
    }


def _evaluation_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _latest_session_state(
    *,
    required: Sequence[str],
    evaluation: datetime,
    daily_rows_loader: Callable[[Sequence[str]], list[dict[str, Any]]],
) -> dict[str, Any]:
    """Resolve one latest session state for both refresh probing and finalization."""

    try:
        latest_rows = list(daily_rows_loader(required))
    except Exception:
        return {
            "status": "error",
            "session_date": None,
            "missing_symbols": list(required),
            "reason": "daily_state_load_failed",
        }
    rows_by_symbol = {
        str(row.get("provider_symbol") or "").strip().upper(): dict(row)
        for row in latest_rows
        if str(row.get("provider_symbol") or "").strip()
    }
    missing_daily = [
        symbol for symbol in required if symbol not in rows_by_symbol
    ]
    if missing_daily:
        return {
            "status": "incomplete",
            "session_date": None,
            "missing_symbols": missing_daily,
            "reason": "incomplete_daily_coverage",
        }
    resolved_by_symbol = {
        symbol: resolve_futures_daily_session(
            symbol,
            rows_by_symbol[symbol].get("candle_time_utc"),
            rows_by_symbol[symbol].get("collected_at"),
            evaluation,
            finalization_basis=rows_by_symbol[symbol].get(
                "finalization_basis"
            ),
            final_close=rows_by_symbol[symbol].get("final_close"),
        )
        for symbol in required
    }
    session_dates = {
        resolved.session_date
        for resolved in resolved_by_symbol.values()
        if resolved.session_date is not None
    }
    if len(session_dates) != 1 or any(
        resolved.session_date is None
        for resolved in resolved_by_symbol.values()
    ):
        return {
            "status": "incomplete",
            "session_date": max(session_dates) if session_dates else None,
            "missing_symbols": [
                symbol
                for symbol, resolved in resolved_by_symbol.items()
                if resolved.session_date is None
            ],
            "reason": "inconsistent_daily_sessions",
        }

    session_date = next(iter(session_dates))
    evaluation_date = evaluation.astimezone(NEW_YORK).date().isoformat()
    reasons = {resolved.reason for resolved in resolved_by_symbol.values()}
    statuses = {resolved.status for resolved in resolved_by_symbol.values()}
    shared = {
        "session_date": session_date,
        "missing_symbols": [],
        "rows_by_symbol": rows_by_symbol,
        "resolved_by_symbol": resolved_by_symbol,
    }
    if reasons == {"explicit_session_aggregate"}:
        return {
            **shared,
            "status": "completed",
            "reason": "explicit_session_aggregate_reused",
            "completion_kind": "explicit",
        }
    if session_date < evaluation_date:
        return {
            **shared,
            "status": "completed",
            "reason": "session_precedes_evaluation_date",
            "completion_kind": "prior_session",
        }
    if session_date > evaluation_date:
        return {
            **shared,
            "status": "incomplete",
            "missing_symbols": list(required),
            "reason": "future_session_not_eligible",
        }
    if statuses == {"FINAL"}:
        return {
            **shared,
            "status": "completed",
            "reason": "provider_daily_already_final",
            "completion_kind": "provider_daily",
        }
    return {
        **shared,
        "status": "pending",
        "reason": "same_date_session_in_progress",
        "daily_finality": (
            "all_in_progress" if statuses == {"IN_PROGRESS"} else "mixed"
        ),
    }


def probe_pending_futures_daily_session(
    *,
    symbols: Sequence[str],
    evaluation_time: datetime,
    daily_rows_loader: Callable[[Sequence[str]], list[dict[str, Any]]] = (
        load_latest_futures_daily_rows
    ),
) -> dict[str, Any]:
    """Return the latest normalized session state for refresh orchestration."""

    required = _normalized_symbols(symbols)
    state = _latest_session_state(
        required=required,
        evaluation=_evaluation_utc(evaluation_time),
        daily_rows_loader=daily_rows_loader,
    )
    return {
        "status": state["status"],
        "session_date": state.get("session_date"),
        "symbols_required": len(required),
        "missing_symbols": list(state.get("missing_symbols") or []),
        "reason": state["reason"],
    }


def run_pending_futures_daily_finalization(
    *,
    symbols: Sequence[str],
    evaluation_time: datetime,
    collect_runner: Callable[..., dict[str, Any]],
    intraday_collection_result: dict[str, Any] | None = None,
    daily_rows_loader: Callable[[Sequence[str]], list[dict[str, Any]]] = (
        load_latest_futures_daily_rows
    ),
    intraday_rows_loader: Callable[..., list[dict[str, Any]]] = (
        load_stored_futures_intraday_rows
    ),
    writer: Callable[..., int] = write_futures_daily_finalization,
) -> FinalizationResult:
    """Rebuild one completed session only when all core rows can advance."""

    required = _normalized_symbols(symbols)
    evaluation = _evaluation_utc(evaluation_time)
    evaluation_et = evaluation.astimezone(NEW_YORK)
    state = _latest_session_state(
        required=required,
        evaluation=evaluation,
        daily_rows_loader=daily_rows_loader,
    )
    if state["status"] == "error":
        return _result(
            status="error",
            session_date=state.get("session_date"),
            required_symbols=required,
            missing_symbols=state.get("missing_symbols") or required,
            reason=state["reason"],
        )
    if state["status"] == "incomplete":
        return _result(
            status="incomplete",
            session_date=state.get("session_date"),
            required_symbols=required,
            missing_symbols=state.get("missing_symbols") or [],
            reason=state["reason"],
        )
    session_date = str(state["session_date"])
    if state["status"] == "completed" and state.get("completion_kind") == "explicit":
        return _result(
            status="reused",
            session_date=session_date,
            required_symbols=required,
            symbols_finalized=len(required),
            reason="explicit_session_aggregate_reused",
        )
    if state["status"] == "completed":
        return _result(
            status="not_required",
            session_date=session_date,
            required_symbols=required,
            reason=state["reason"],
        )
    if evaluation_et.time() < FUTURES_DAILY_SETTLEMENT_STABLE_ET:
        return _result(
            status="not_due",
            session_date=session_date,
            required_symbols=required,
            reason="settlement_cutoff_not_reached",
        )
    if state.get("daily_finality") == "mixed":
        resolved_by_symbol = dict(state["resolved_by_symbol"])
        return _result(
            status="incomplete",
            session_date=session_date,
            required_symbols=required,
            missing_symbols=[
                symbol
                for symbol, resolved in resolved_by_symbol.items()
                if resolved.status != "IN_PROGRESS"
            ],
            reason="mixed_daily_finality",
        )

    try:
        intraday_result = intraday_collection_result
        if intraday_result is None:
            intraday_result = collect_runner(
                symbols=list(required),
                period="2d",
                interval="5m",
                cadence_mode="manual_macro_daily_finalization",
                max_symbols=len(required),
                batch_size=len(required),
                sleep_sec=0.0,
                materialize_snapshot=False,
            )
        failed_symbols = sorted(
            {
                str(symbol).strip().upper()
                for symbol in list(
                    intraday_result.get("failed_symbols") or []
                )
                if str(symbol).strip()
            }
        )
        if (
            str(intraday_result.get("status") or "") != "success"
            or int(intraday_result.get("rows_written") or 0) <= 0
            or failed_symbols
        ):
            return _result(
                status="incomplete",
                session_date=session_date,
                required_symbols=required,
                missing_symbols=failed_symbols,
                reason="intraday_collection_incomplete",
            )
        window_start_utc, window_end_utc = futures_session_window_utc(
            session_date
        )
        stored_rows = intraday_rows_loader(
            symbols=required,
            start_utc=window_start_utc,
            end_utc=window_end_utc,
        )
        batch = build_session_finalization_batch(
            stored_rows,
            session_date=session_date,
            daily_targets={
                symbol: state["rows_by_symbol"][symbol].get("candle_time_utc")
                for symbol in required
            },
            required_symbols=required,
            finalized_at=evaluation,
        )
        if not batch.complete or len(batch.rows) != len(required):
            return _result(
                status="incomplete",
                session_date=session_date,
                required_symbols=required,
                missing_symbols=batch.missing_symbols,
                reason="stored_intraday_coverage_incomplete",
            )
        written = writer(batch, required_symbols=required)
        if int(written) != len(required):
            return _result(
                status="incomplete",
                session_date=session_date,
                required_symbols=required,
                missing_symbols=required,
                reason="finalization_write_incomplete",
            )
        return _result(
            status="finalized",
            session_date=session_date,
            required_symbols=required,
            symbols_finalized=written,
            reason="session_aggregate_written",
        )
    except Exception:
        return _result(
            status="error",
            session_date=session_date,
            required_symbols=required,
            missing_symbols=required,
            reason="finalization_write_failed",
        )
