"""Read Futures Macro daily rows across current and pre-migration schemas."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any


QueryFn = Callable[
    [str, str, Sequence[Any] | None],
    list[dict[str, Any]],
]

FINAL_COLUMNS = (
    "final_open",
    "final_high",
    "final_low",
    "final_close",
    "final_adj_close",
    "final_volume",
    "finalization_basis",
    "final_source_ref",
    "finalized_at",
)


def load_futures_macro_daily_rows(
    query_fn: QueryFn,
    *,
    symbols: Sequence[str],
    lookback_days: int,
) -> list[dict[str, Any]]:
    """Load daily rows with one narrow fallback for an unmigrated schema."""

    selected = [
        str(symbol).strip().upper()
        for symbol in symbols
        if str(symbol).strip()
    ]
    if not selected:
        return []
    placeholders = ", ".join(["%s"] * len(selected))
    params: list[Any] = [
        "1d",
        *selected,
        max(1, int(lookback_days)),
    ]
    raw_projection = """
        provider_symbol, interval_code, candle_time_utc,
        open, high, low, close, adj_close, volume,
        source, provider_status, collected_at
    """
    final_projection = ", ".join(FINAL_COLUMNS)
    legacy_projection = ", ".join(
        f"NULL AS {column}" for column in FINAL_COLUMNS
    )

    def run(final_fields: str) -> list[dict[str, Any]]:
        return query_fn(
            "finance_price",
            f"""
            SELECT {raw_projection}, {final_fields}
            FROM futures_ohlcv
            WHERE interval_code = %s
              AND provider_symbol IN ({placeholders})
              AND candle_time_utc >= DATE_SUB(
                    UTC_TIMESTAMP(), INTERVAL %s DAY
                  )
            ORDER BY provider_symbol, candle_time_utc
            """,
            params,
        )

    try:
        return run(final_projection)
    except Exception as exc:
        message = str(exc).lower()
        if "unknown column" not in message or not any(
            column in message for column in FINAL_COLUMNS
        ):
            raise
        return run(legacy_projection)
