from __future__ import annotations

from typing import Any

from finance.data.asset_profile import load_symbols_from_asset_profile
from finance.data.db.mysql import MySQLClient


SourceResult = dict[str, Any]


def _query_symbols(table: str) -> list[str]:
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_meta")
        rows = db.query(f"SELECT symbol FROM {table} ORDER BY symbol")
        return [row["symbol"] for row in rows if row.get("symbol")]
    finally:
        db.close()


def _merge_unique(*groups: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for sym in group:
            if sym in seen:
                continue
            seen.add(sym)
            out.append(sym)
    return out


def resolve_symbol_source(source_mode: str, manual_symbols: list[str]) -> SourceResult:
    try:
        if source_mode == "Manual":
            return {
                "status": "ok" if manual_symbols else "error",
                "message": "Manual symbols ready." if manual_symbols else "No manual symbols provided.",
                "symbols": manual_symbols,
                "count": len(manual_symbols),
                "source_mode": source_mode,
            }

        if source_mode == "NYSE Stocks":
            symbols = _query_symbols("nyse_stock")
        elif source_mode == "NYSE ETFs":
            symbols = _query_symbols("nyse_etf")
        elif source_mode == "NYSE Stocks + ETFs":
            symbols = _merge_unique(_query_symbols("nyse_stock"), _query_symbols("nyse_etf"))
        elif source_mode == "Profile Filtered Stocks":
            symbols = load_symbols_from_asset_profile("stock", on_filter=True)
        elif source_mode == "Profile Filtered ETFs":
            symbols = load_symbols_from_asset_profile("etf", on_filter=True)
        elif source_mode == "Profile Filtered Stocks + ETFs":
            symbols = _merge_unique(
                load_symbols_from_asset_profile("stock", on_filter=True),
                load_symbols_from_asset_profile("etf", on_filter=True),
            )
        else:
            return {
                "status": "error",
                "message": f"Unsupported symbol source: {source_mode}",
                "symbols": [],
                "count": 0,
                "source_mode": source_mode,
            }

        return {
            "status": "ok" if symbols else "error",
            "message": f"{source_mode} ready." if symbols else f"{source_mode} returned no symbols.",
            "symbols": symbols,
            "count": len(symbols),
            "source_mode": source_mode,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Failed to resolve symbol source: {exc}",
            "symbols": [],
            "count": 0,
            "source_mode": source_mode,
        }
