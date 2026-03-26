from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from finance.loaders import (
    load_factor_snapshot,
    load_price_freshness_summary,
    load_price_history,
    load_statement_factor_snapshot_shadow,
    load_statement_snapshot_strict,
)
from finance.performance import portfolio_performance_summary
from finance.sample import (
    QUALITY_STRICT_DEFAULT_FACTORS,
    VALUE_STRICT_DEFAULT_FACTORS,
    get_dual_momentum_from_db,
    get_equal_weight_from_db,
    get_gtaa3_from_db,
    get_quality_snapshot_from_db,
    get_risk_parity_trend_from_db,
    get_statement_quality_value_snapshot_shadow_from_db,
    get_statement_quality_snapshot_from_db,
    get_statement_quality_snapshot_shadow_from_db,
    get_statement_value_snapshot_shadow_from_db,
)


class BacktestInputError(ValueError):
    """Raised when user-facing backtest input is structurally invalid."""


class BacktestDataError(ValueError):
    """Raised when the requested DB-backed backtest cannot find required market data."""


def _normalize_tickers(tickers: Sequence[str] | None) -> list[str]:
    if tickers is None:
        return ["VIG", "SCHD", "DGRO", "GLD"]

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in tickers:
        symbol = str(raw).strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)

    if not normalized:
        raise BacktestInputError("At least one ticker must be provided.")

    return normalized


def _summary_frequency(option: str, timeframe: str) -> str:
    if option == "month_end":
        return "M"
    if timeframe == "1d":
        return "D"
    return "M"


def _validate_backtest_date_range(start: str | None, end: str | None) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    start_ts = pd.to_datetime(start) if start is not None else None
    end_ts = pd.to_datetime(end) if end is not None else None

    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise BacktestInputError("Start date must be earlier than or equal to end date.")

    return start_ts, end_ts


def _preflight_equal_weight_data(
    *,
    tickers: list[str],
    start: str | None,
    end: str | None,
    timeframe: str,
) -> None:
    history = load_price_history(
        symbols=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found in MySQL for the requested tickers and date range. "
            "Run the ingestion pipeline first."
        )

    available_symbols = set(history["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if missing:
        raise BacktestDataError(
            "Some requested tickers do not have DB price history for the selected range: "
            + ", ".join(missing)
        )


def _preflight_price_strategy_data(
    *,
    tickers: list[str],
    start: str | None,
    end: str | None,
    timeframe: str,
) -> None:
    history = load_price_history(
        symbols=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found in MySQL for the requested tickers and date range. "
            "Run the ingestion pipeline first."
        )

    available_symbols = set(history["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if missing:
        raise BacktestDataError(
            "Some requested tickers do not have DB price history for the selected range: "
            + ", ".join(missing)
        )


def _preflight_quality_snapshot_data(
    *,
    tickers: list[str],
    end: str | None,
    factor_freq: str,
    quality_factors: list[str],
) -> None:
    if end is None:
        raise BacktestInputError("Quality snapshot strategy requires an end date.")

    snapshot = load_factor_snapshot(
        quality_factors,
        symbols=tickers,
        as_of_date=end,
        freq=factor_freq,
    )
    if snapshot.empty:
        raise BacktestDataError(
            "No factor snapshot rows were found for the requested tickers and end date. "
            "Run the fundamentals/factors pipeline first."
        )

    available_symbols = set(snapshot["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if len(missing) == len(tickers):
        raise BacktestDataError(
            "None of the requested tickers have factor snapshot rows for the selected end date."
        )


def _preflight_statement_quality_data(
    *,
    tickers: list[str],
    end: str | None,
    statement_freq: str,
) -> None:
    if end is None:
        raise BacktestInputError("Statement-driven quality prototype requires an end date.")

    snapshot = load_statement_snapshot_strict(
        symbols=tickers,
        as_of_date=end,
        freq=statement_freq,
    )
    if snapshot.empty:
        raise BacktestDataError(
            "No strict statement snapshot rows were found for the requested tickers and end date. "
            "Run Extended Statement Refresh first."
        )

    available_symbols = set(snapshot["symbol"].astype(str).str.upper().unique().tolist())
    if not available_symbols:
        raise BacktestDataError(
            "No symbols in the requested universe have strict statement snapshot coverage at the selected end date."
        )


def _preflight_statement_quality_shadow_data(
    *,
    tickers: list[str],
    end: str | None,
    statement_freq: str,
    factor_names: list[str],
) -> None:
    if end is None:
        raise BacktestInputError("Statement-driven shadow quality path requires an end date.")

    snapshot = load_statement_factor_snapshot_shadow(
        factor_names,
        symbols=tickers,
        as_of_date=end,
        freq=statement_freq,
    )
    if snapshot.empty:
        raise BacktestDataError(
            "No statement-driven shadow factor snapshot rows were found for the requested tickers and end date. "
            "Run Extended Statement Refresh and rebuild statement shadow factors first."
        )


def inspect_strict_annual_price_freshness(
    *,
    tickers: Sequence[str] | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    end_ts = pd.to_datetime(end).normalize() if end is not None else None

    summary = load_price_freshness_summary(
        symbols=normalized_tickers,
        end=end,
        timeframe=timeframe,
    )
    if summary.empty:
        return {
            "status": "error",
            "message": "No DB price rows were found for the selected strict annual universe.",
            "details": {
                "requested_count": len(normalized_tickers),
                "covered_count": 0,
                "missing_count": len(normalized_tickers),
                "missing_symbols": normalized_tickers[:20],
                "target_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
            },
        }

    working = summary.copy()
    working["symbol"] = working["symbol"].astype(str).str.upper()
    working["latest_date"] = pd.to_datetime(working["latest_date"], errors="coerce")
    working = working[working["symbol"].notna() & working["latest_date"].notna()].reset_index(drop=True)

    covered_symbols = set(working["symbol"].tolist())
    missing_symbols = [ticker for ticker in normalized_tickers if ticker not in covered_symbols]

    if working.empty:
        return {
            "status": "error",
            "message": "No usable DB price dates were found for the selected strict annual universe.",
            "details": {
                "requested_count": len(normalized_tickers),
                "covered_count": 0,
                "missing_count": len(normalized_tickers),
                "missing_symbols": normalized_tickers[:20],
                "target_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
            },
        }

    common_latest = working["latest_date"].min().normalize()
    newest_latest = working["latest_date"].max().normalize()
    spread_days = int((newest_latest - common_latest).days)
    target_end = end_ts if end_ts is not None else newest_latest

    stale_df = working[working["latest_date"].dt.normalize() < target_end].sort_values(["latest_date", "symbol"])
    lagging_df = working[working["latest_date"].dt.normalize() < newest_latest].sort_values(["latest_date", "symbol"])
    stale_symbols_all = stale_df["symbol"].tolist()
    lagging_symbols_all = lagging_df["symbol"].tolist()

    details = {
        "requested_count": len(normalized_tickers),
        "covered_count": int(len(working)),
        "missing_count": len(missing_symbols),
        "missing_symbols": missing_symbols[:20],
        "missing_symbols_all": missing_symbols,
        "target_end_date": target_end.strftime("%Y-%m-%d") if target_end is not None else None,
        "common_latest_date": common_latest.strftime("%Y-%m-%d"),
        "newest_latest_date": newest_latest.strftime("%Y-%m-%d"),
        "spread_days": spread_days,
        "stale_count": int(len(stale_df)),
        "stale_symbols": stale_symbols_all[:20],
        "stale_symbols_all": stale_symbols_all,
        "lagging_count": int(len(lagging_df)),
        "lagging_symbols": lagging_symbols_all[:20],
        "lagging_symbols_all": lagging_symbols_all,
        "refresh_symbols_all": sorted(set(stale_symbols_all + missing_symbols)),
    }

    if not missing_symbols and len(stale_df) == 0 and spread_days == 0:
        return {
            "status": "ok",
            "message": (
                f"All {len(normalized_tickers)} selected symbols have price data through "
                f"`{common_latest.strftime('%Y-%m-%d')}`."
            ),
            "details": details,
        }

    message_parts: list[str] = []
    if missing_symbols:
        message_parts.append(f"{len(missing_symbols)} symbols have no DB price rows.")
    if len(stale_df) > 0:
        message_parts.append(
            f"{len(stale_df)} symbols stop before the selected end `{target_end.strftime('%Y-%m-%d')}`."
        )
    if spread_days > 0:
        message_parts.append(
            f"Latest-date spread inside the universe is {spread_days} day(s) "
            f"(`{common_latest.strftime('%Y-%m-%d')}` -> `{newest_latest.strftime('%Y-%m-%d')}`)."
        )

    return {
        "status": "warning",
        "message": " ".join(message_parts),
        "details": details,
    }


def build_backtest_result_bundle(
    result_df: pd.DataFrame,
    *,
    strategy_name: str,
    strategy_key: str,
    input_params: dict[str, Any],
    execution_mode: str = "db",
    data_mode: str = "db_backed",
    summary_freq: str = "M",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build the minimal UI-facing bundle for a single backtest run.
    """
    if result_df is None or result_df.empty:
        raise ValueError("Backtest result is empty.")

    required_columns = {"Date", "Total Balance", "Total Return"}
    missing = required_columns.difference(result_df.columns)
    if missing:
        raise ValueError(f"Backtest result is missing required columns: {sorted(missing)}")

    result_df = result_df.copy()
    result_df["Date"] = pd.to_datetime(result_df["Date"])
    result_df = result_df.sort_values("Date").reset_index(drop=True)

    summary_df = portfolio_performance_summary(
        result_df,
        name=strategy_name,
        freq=summary_freq,
    )
    chart_df = result_df[["Date", "Total Balance", "Total Return"]].copy()

    meta = {
        "execution_mode": execution_mode,
        "data_mode": data_mode,
        "strategy_key": strategy_key,
        "tickers": input_params.get("tickers", []),
        "start": input_params.get("start"),
        "end": input_params.get("end"),
        "timeframe": input_params.get("timeframe"),
        "option": input_params.get("option"),
        "rebalance_interval": input_params.get("rebalance_interval"),
        "universe_mode": input_params.get("universe_mode"),
        "preset_name": input_params.get("preset_name"),
        "warnings": warnings or [],
    }
    if input_params.get("top") is not None:
        meta["top"] = input_params.get("top")
    if input_params.get("vol_window") is not None:
        meta["vol_window"] = input_params.get("vol_window")
    if input_params.get("factor_freq") is not None:
        meta["factor_freq"] = input_params.get("factor_freq")
    if input_params.get("rebalance_freq") is not None:
        meta["rebalance_freq"] = input_params.get("rebalance_freq")
    if input_params.get("snapshot_mode") is not None:
        meta["snapshot_mode"] = input_params.get("snapshot_mode")
    if input_params.get("quality_factors") is not None:
        meta["quality_factors"] = input_params.get("quality_factors")
    if input_params.get("value_factors") is not None:
        meta["value_factors"] = input_params.get("value_factors")
    if input_params.get("snapshot_source") is not None:
        meta["snapshot_source"] = input_params.get("snapshot_source")

    return {
        "strategy_name": strategy_name,
        "result_df": result_df,
        "summary_df": summary_df,
        "chart_df": chart_df,
        "meta": meta,
    }


def run_equal_weight_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 12,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    """
    Public UI-facing runtime wrapper for the first DB-backed backtest screen.
    """
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )

    result_df = get_equal_weight_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        interval=rebalance_interval,
    )

    return build_backtest_result_bundle(
        result_df,
        strategy_name="Equal Weight",
        strategy_key="equal_weight",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "rebalance_interval": rebalance_interval,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )


def run_gtaa_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = 3,
    interval: int = 2,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    """
    Public UI-facing runtime wrapper for the second DB-backed backtest screen.
    """
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )

    result_df = get_gtaa3_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        interval=interval,
    )

    return build_backtest_result_bundle(
        result_df,
        strategy_name="GTAA",
        strategy_key="gtaa",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top,
            "rebalance_interval": interval,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )


def run_risk_parity_trend_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 1,
    vol_window: int = 6,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )

    result_df = get_risk_parity_trend_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        rebalance_interval=rebalance_interval,
        vol_window=vol_window,
    )

    return build_backtest_result_bundle(
        result_df,
        strategy_name="Risk Parity Trend",
        strategy_key="risk_parity_trend",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "rebalance_interval": rebalance_interval,
            "vol_window": vol_window,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )


def run_dual_momentum_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = 1,
    rebalance_interval: int = 1,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )

    result_df = get_dual_momentum_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        rebalance_interval=rebalance_interval,
    )

    return build_backtest_result_bundle(
        result_df,
        strategy_name="Dual Momentum",
        strategy_key="dual_momentum",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top,
            "rebalance_interval": rebalance_interval,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )


def run_quality_snapshot_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    factor_freq: str = "annual",
    rebalance_freq: str = "monthly",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    snapshot_mode: str = "broad_research",
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)

    if snapshot_mode != "broad_research":
        raise BacktestInputError("The first public quality snapshot runtime supports only 'broad_research' mode.")
    if rebalance_freq != "monthly":
        raise BacktestInputError("The first public quality snapshot runtime currently supports only monthly rebalance.")

    normalized_factors = [str(name).strip() for name in (quality_factors or ["roe", "gross_margin", "operating_margin", "debt_ratio"]) if str(name).strip()]
    if not normalized_factors:
        raise BacktestInputError("At least one quality factor must be provided.")

    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    _preflight_quality_snapshot_data(
        tickers=normalized_tickers,
        end=end,
        factor_freq=factor_freq,
        quality_factors=normalized_factors,
    )

    result_df = get_quality_snapshot_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        factor_freq=factor_freq,
        quality_factors=normalized_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        snapshot_mode=snapshot_mode,
    )

    warnings: list[str] = []
    if start:
        selected_mask = result_df.get("Selected Count")
        if selected_mask is not None:
            active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
            if not active_rows.empty:
                first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
                if first_active_date > start:
                    warnings.append(
                        "No usable quality snapshot rows were available at the requested start date. "
                        f"The strategy stayed in cash until `{first_active_date}`."
                    )

    return build_backtest_result_bundle(
        result_df,
        strategy_name="Quality Snapshot",
        strategy_key="quality_snapshot",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": factor_freq,
            "rebalance_freq": rebalance_freq,
            "snapshot_mode": snapshot_mode,
            "quality_factors": normalized_factors,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_factor_snapshot",
        warnings=warnings,
    )


def _run_statement_quality_bundle(
    *,
    strategy_name: str,
    strategy_key: str,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    statement_freq: str = "annual",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    static_warnings: Sequence[str] | None = None,
    snapshot_source: str = "rebuild_statement",
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)

    normalized_factors = [
        str(name).strip()
        for name in (quality_factors or QUALITY_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one quality factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=normalized_tickers,
        end=end,
        timeframe=timeframe,
    )

    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if snapshot_source == "shadow_factors":
        _preflight_statement_quality_shadow_data(
            tickers=normalized_tickers,
            end=end,
            statement_freq=statement_freq,
            factor_names=normalized_factors,
        )
        result_df = get_statement_quality_snapshot_shadow_from_db(
            tickers=normalized_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
            option=option,
            statement_freq=statement_freq,
            quality_factors=normalized_factors,
            top_n=top_n,
            rebalance_interval=rebalance_interval,
        )
    else:
        _preflight_statement_quality_data(
            tickers=normalized_tickers,
            end=end,
            statement_freq=statement_freq,
        )
        result_df = get_statement_quality_snapshot_from_db(
            tickers=normalized_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
            option=option,
            statement_freq=statement_freq,
            quality_factors=normalized_factors,
            top_n=top_n,
            rebalance_interval=rebalance_interval,
        )

    warnings: list[str] = list(static_warnings or [])
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Large-universe strict annual runs can show duplicate or shifted final-month rows until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable strict statement snapshot rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name=strategy_name,
        strategy_key=strategy_key,
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": statement_freq,
            "quality_factors": normalized_factors,
            "snapshot_mode": "strict_statement_annual",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "snapshot_source": snapshot_source,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors" if snapshot_source == "shadow_factors" else "db_backed_strict_statement_snapshot",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    return bundle


def run_quality_snapshot_strict_annual_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    return _run_statement_quality_bundle(
        strategy_name="Quality Snapshot (Strict Annual)",
        strategy_key="quality_snapshot_strict_annual",
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="annual",
        quality_factors=quality_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        universe_mode=universe_mode,
        preset_name=preset_name,
        snapshot_source="shadow_factors",
        static_warnings=[
            "Strict annual statement path: ranks annual statement-driven quality snapshots using precomputed statement shadow factors for faster public execution.",
        ],
    )


def run_statement_quality_prototype_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    statement_freq: str = "annual",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    return _run_statement_quality_bundle(
        strategy_name="Statement Quality Prototype",
        strategy_key="statement_quality_prototype",
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq=statement_freq,
        quality_factors=quality_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        universe_mode=universe_mode,
        preset_name=preset_name,
        snapshot_source="rebuild_statement",
        static_warnings=[
            "Prototype path: strict statement snapshots are used for sample-universe architecture validation.",
        ],
    )


def run_value_snapshot_strict_annual_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    value_factors: Sequence[str] | None = None,
    top_n: int = 10,
    rebalance_interval: int = 1,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)

    normalized_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=normalized_tickers,
        end=end,
        timeframe=timeframe,
    )

    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    _preflight_statement_quality_shadow_data(
        tickers=normalized_tickers,
        end=end,
        statement_freq="annual",
        factor_names=normalized_factors,
    )

    result_df = get_statement_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="annual",
        value_factors=normalized_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
    )

    warnings = [
        "Strict annual value path: ranks annual statement-driven value snapshots using precomputed statement shadow factors.",
    ]
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Large-universe strict annual runs can show duplicate or shifted final-month rows until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable strict statement shadow rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Value Snapshot (Strict Annual)",
        strategy_key="value_snapshot_strict_annual",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": "annual",
            "value_factors": normalized_factors,
            "snapshot_mode": "strict_statement_annual",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    return bundle


def run_quality_value_snapshot_strict_annual_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    quality_factors: Sequence[str] | None = None,
    value_factors: Sequence[str] | None = None,
    top_n: int = 10,
    rebalance_interval: int = 1,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)

    normalized_quality_factors = [
        str(name).strip()
        for name in (quality_factors or QUALITY_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    normalized_value_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    normalized_factor_names: list[str] = []
    for factor_name in [*normalized_quality_factors, *normalized_value_factors]:
        if factor_name and factor_name not in normalized_factor_names:
            normalized_factor_names.append(factor_name)

    if not normalized_factor_names:
        raise BacktestInputError("At least one strict annual quality/value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=normalized_tickers,
        end=end,
        timeframe=timeframe,
    )

    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    _preflight_statement_quality_shadow_data(
        tickers=normalized_tickers,
        end=end,
        statement_freq="annual",
        factor_names=normalized_factor_names,
    )

    result_df = get_statement_quality_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="annual",
        quality_factors=normalized_quality_factors,
        value_factors=normalized_value_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
    )

    warnings = [
        "Strict annual multi-factor path: combines coverage-first quality factors with annual statement-driven valuation factors.",
    ]
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Large-universe strict annual runs can show duplicate or shifted final-month rows until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable strict annual multi-factor snapshot rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Quality + Value Snapshot (Strict Annual)",
        strategy_key="quality_value_snapshot_strict_annual",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": "annual",
            "quality_factors": normalized_quality_factors,
            "value_factors": normalized_value_factors,
            "snapshot_mode": "strict_statement_annual",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    return bundle
