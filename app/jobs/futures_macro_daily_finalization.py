"""Finalize a same-date futures daily session on explicit refresh."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime, time, timezone
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


def run_pending_futures_daily_finalization(
    *,
    symbols: Sequence[str],
    evaluation_time: datetime,
    collect_runner: Callable[..., dict[str, Any]],
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
    evaluation = evaluation_time
    if evaluation.tzinfo is None:
        evaluation = evaluation.replace(tzinfo=timezone.utc)
    else:
        evaluation = evaluation.astimezone(timezone.utc)
    evaluation_et = evaluation.astimezone(NEW_YORK)
    try:
        latest_rows = list(daily_rows_loader(required))
    except Exception:
        return _result(
            status="error",
            session_date=None,
            required_symbols=required,
            missing_symbols=required,
            reason="daily_state_load_failed",
        )
    rows_by_symbol = {
        str(row.get("provider_symbol") or "").strip().upper(): dict(row)
        for row in latest_rows
        if str(row.get("provider_symbol") or "").strip()
    }
    missing_daily = [
        symbol for symbol in required if symbol not in rows_by_symbol
    ]
    if missing_daily:
        return _result(
            status="incomplete",
            session_date=None,
            required_symbols=required,
            missing_symbols=missing_daily,
            reason="incomplete_daily_coverage",
        )

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
        return _result(
            status="incomplete",
            session_date=max(session_dates) if session_dates else None,
            required_symbols=required,
            missing_symbols=[
                symbol
                for symbol, resolved in resolved_by_symbol.items()
                if resolved.session_date is None
            ],
            reason="inconsistent_daily_sessions",
        )
    session_date = next(iter(session_dates))
    explicitly_final = [
        symbol
        for symbol, resolved in resolved_by_symbol.items()
        if resolved.reason == "explicit_session_aggregate"
    ]
    if len(explicitly_final) == len(required):
        return _result(
            status="reused",
            session_date=session_date,
            required_symbols=required,
            symbols_finalized=len(required),
            reason="explicit_session_aggregate_reused",
        )
    if session_date < evaluation_et.date().isoformat():
        return _result(
            status="not_required",
            session_date=session_date,
            required_symbols=required,
            reason="session_precedes_evaluation_date",
        )
    if session_date > evaluation_et.date().isoformat():
        return _result(
            status="incomplete",
            session_date=session_date,
            required_symbols=required,
            missing_symbols=required,
            reason="future_session_not_eligible",
        )
    if evaluation_et.time() < FUTURES_DAILY_SETTLEMENT_STABLE_ET:
        return _result(
            status="not_due",
            session_date=session_date,
            required_symbols=required,
            reason="settlement_cutoff_not_reached",
        )
    if all(
        resolved.status == "FINAL"
        for resolved in resolved_by_symbol.values()
    ):
        return _result(
            status="not_required",
            session_date=session_date,
            required_symbols=required,
            reason="provider_daily_already_final",
        )
    if any(
        resolved.status != "IN_PROGRESS"
        for resolved in resolved_by_symbol.values()
    ):
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
                symbol: rows_by_symbol[symbol].get("candle_time_utc")
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
