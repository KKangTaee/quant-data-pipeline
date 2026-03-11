from __future__ import annotations

from typing import Any, Iterable

from finance.data.db.mysql import MySQLClient

from .ingestion_jobs import parse_symbols, split_valid_invalid_symbols


CheckResult = dict[str, Any]


def _ok(message: str, **details) -> CheckResult:
    return {"status": "ok", "message": message, "details": details}


def _warn(message: str, **details) -> CheckResult:
    return {"status": "warning", "message": message, "details": details}


def _error(message: str, **details) -> CheckResult:
    return {"status": "error", "message": message, "details": details}


def check_symbol_input(symbols: str | Iterable[str] | None) -> CheckResult:
    parsed, invalid = split_valid_invalid_symbols(symbols)
    if not parsed:
        return _error("No valid symbols provided.", count=0, invalid_symbols=invalid)
    if invalid:
        return _warn("Some symbols are invalid and may be ignored.", count=len(parsed), symbols=parsed, invalid_symbols=invalid)
    return _ok("Symbols are ready.", count=len(parsed), symbols=parsed)


def check_factor_prerequisites(
    symbols: str | Iterable[str] | None,
    *,
    freq: str = "annual",
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> CheckResult:
    parsed, invalid = split_valid_invalid_symbols(symbols)
    if not parsed:
        return _error("No valid symbols provided for factor validation.", symbols=[], invalid_symbols=invalid)

    price_db = MySQLClient(host, user, password, port)
    fund_db = MySQLClient(host, user, password, port)
    try:
        price_db.use_db("finance_price")
        fund_db.use_db("finance_fundamental")

        placeholders = ",".join(["%s"] * len(parsed))

        price_rows = price_db.query(
            f"""
            SELECT symbol, COUNT(*) AS cnt
            FROM nyse_price_history
            WHERE symbol IN ({placeholders}) AND timeframe = %s
            GROUP BY symbol
            """,
            parsed + ["1d"],
        )
        fund_rows = fund_db.query(
            f"""
            SELECT symbol, COUNT(*) AS cnt
            FROM nyse_fundamentals
            WHERE symbol IN ({placeholders}) AND freq = %s
            GROUP BY symbol
            """,
            parsed + [freq],
        )

        price_symbols = {row["symbol"] for row in price_rows if row.get("cnt", 0) > 0}
        fund_symbols = {row["symbol"] for row in fund_rows if row.get("cnt", 0) > 0}

        missing_price = [sym for sym in parsed if sym not in price_symbols]
        missing_fund = [sym for sym in parsed if sym not in fund_symbols]

        if not missing_price and not missing_fund:
            if invalid:
                return _warn(
                    "Factor prerequisites look ready for valid symbols, but some symbols are invalid.",
                    symbols=parsed,
                    invalid_symbols=invalid,
                    freq=freq,
                )
            return _ok(
                "Factor prerequisites look ready.",
                symbols=parsed,
                freq=freq,
            )

        return _warn(
            "Some factor prerequisites are missing.",
            symbols=parsed,
            invalid_symbols=invalid,
            freq=freq,
            missing_price=missing_price,
            missing_fundamentals=missing_fund,
        )
    except Exception as exc:
        return _error(
            f"Preflight check failed: {exc}",
            symbols=parsed,
            freq=freq,
        )
    finally:
        price_db.close()
        fund_db.close()


def check_asset_profile_prerequisites(
    kinds: Iterable[str],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> CheckResult:
    kinds = tuple(kinds)
    if not kinds:
        return _error("No asset profile kinds selected.", kinds=[])

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db("finance_meta")
        counts: dict[str, int] = {}
        for kind in kinds:
            rows = db.query(f"SELECT COUNT(*) AS cnt FROM nyse_{kind}")
            counts[kind] = int(rows[0]["cnt"])

        empty_kinds = [kind for kind, cnt in counts.items() if cnt == 0]
        if empty_kinds:
            return _warn(
                "Some NYSE universe tables are empty.",
                counts=counts,
                empty_kinds=empty_kinds,
            )

        return _ok("Asset profile prerequisites look ready.", counts=counts)
    except Exception as exc:
        return _error(f"Preflight check failed: {exc}", kinds=list(kinds))
    finally:
        db.close()
