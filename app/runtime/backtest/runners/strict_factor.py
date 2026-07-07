from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from app.runtime.backtest.result_bundle import build_backtest_result_bundle
from app.runtime.backtest.real_money import (
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    STRICT_DEFAULT_BENCHMARK_CONTRACT,
    STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    _apply_real_money_hardening,
    _normalize_tickers,
    _resolve_guardrail_reference_ticker,
)
from finance.loaders import (
    load_asset_profile_status_summary,
    load_factor_snapshot,
    load_latest_market_date,
    load_pit_universe_membership_snapshots,
    load_price_freshness_summary,
    load_price_history,
    load_statement_factor_snapshot_shadow,
    load_statement_snapshot_strict,
)
from finance.data.pit_universe import normalize_pit_universe_code
from finance.sample import (
    HISTORICAL_DYNAMIC_PIT_UNIVERSE,
    PIT_MONTHLY_SNAPSHOT_UNIVERSE,
    QUALITY_STRICT_DEFAULT_FACTORS,
    STATIC_MANAGED_RESEARCH_UNIVERSE,
    STRICT_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_REJECTION_HANDLING_MODE,
    STRICT_DEFAULT_RISK_OFF_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH,
    STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT,
    STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH,
    STRICT_RISK_OFF_MODE_DEFENSIVE,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_WEIGHTING_MODE_RANK_TAPERED,
    VALUE_STRICT_DEFAULT_FACTORS,
    get_quality_snapshot_from_db,
    get_statement_quality_snapshot_from_db,
    get_statement_quality_snapshot_shadow_from_db,
    get_statement_quality_value_snapshot_shadow_from_db,
    get_statement_value_snapshot_shadow_from_db,
    resolve_strict_rejection_handling_mode,
    strict_rejection_handling_mode_to_flags,
)


def _input_error(message: str) -> Exception:
    from app.runtime.backtest.common import BacktestInputError

    return BacktestInputError(message)


def _data_error(message: str) -> Exception:
    from app.runtime.backtest.common import BacktestDataError

    return BacktestDataError(message)


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
        raise _input_error("Start date must be earlier than or equal to end date.")

    return start_ts, end_ts


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
        raise _data_error(
            "No OHLCV rows were found in MySQL for the requested tickers and date range. "
            "Run the ingestion pipeline first."
        )

    available_symbols = set(history["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if missing:
        raise _data_error(
            "Some requested tickers do not have DB price history for the selected range: "
            + ", ".join(missing)
        )


def _build_strict_rejected_slot_handling_warning(
    *,
    trend_filter_window: int,
    rejected_slot_handling_mode: str | None,
) -> str:
    resolved_mode = resolve_strict_rejection_handling_mode(rejected_slot_handling_mode)
    if resolved_mode == STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH:
        return (
            f"Trend Filter Overlay가 켜져 있습니다: 월말 선택 종목 중 `Close < MA{trend_filter_window}`인 종목은 "
            "먼저 다음 순위의 적격 종목으로 채우고, 그래도 남는 슬롯은 현금으로 보유합니다."
        )
    if resolved_mode == STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT:
        return (
            f"Trend Filter Overlay가 켜져 있습니다: 월말 선택 종목 중 `Close < MA{trend_filter_window}`인 종목은 "
            "먼저 다음 순위의 적격 종목으로 채우고, 최종 생존 종목을 다시 비중 조정합니다."
        )
    if resolved_mode == STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH:
        return (
            f"Trend Filter Overlay가 켜져 있습니다: 월말 선택 종목 중 `Close < MA{trend_filter_window}`인 종목은 "
            "다음 리밸런싱 전까지 해당 슬롯을 현금으로 남깁니다."
        )
    return (
        f"Trend Filter Overlay가 켜져 있습니다: 월말 선택 종목 중 `Close < MA{trend_filter_window}`인 종목은 "
        "제외하고, 다음 리밸런싱 전까지 생존 종목의 비중을 다시 조정합니다."
    )


def _inspect_dynamic_universe_price_pool(
    *,
    tickers: list[str],
    end: str | None,
    timeframe: str,
) -> dict[str, Any]:
    history = load_price_history(
        symbols=tickers,
        start=None,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        raise _data_error(
            "No OHLCV rows were found in MySQL for the requested dynamic candidate pool. "
            "Run the ingestion pipeline first."
        )

    available_symbols = sorted(
        history["symbol"].astype(str).str.upper().dropna().unique().tolist()
    )
    available_set = set(available_symbols)
    missing = [ticker for ticker in tickers if ticker not in available_set]
    return {
        "requested_count": len(tickers),
        "available_count": len(available_symbols),
        "missing_count": len(missing),
        "missing_symbols": missing,
    }


def _dynamic_universe_warning(statement_freq: str) -> str:
    normalized_freq = str(statement_freq or "annual").strip().lower()
    return (
        "Phase 10 1차 dynamic universe 방식입니다: 리밸런싱 날짜 기준 후보군을 "
        "관리 대상 후보 pool에서 재구성하며, 리밸런싱일 종가와 당시까지 확인된 "
        f"`{normalized_freq}` shares_outstanding을 사용해 근사 PIT membership을 만듭니다."
    )


def _pit_monthly_universe_warning(universe_code: str | None) -> str:
    return (
        "PIT Monthly Snapshot Universe 방식입니다: 백테스트는 현재 Top-N을 과거에 고정하지 않고, "
        f"사전에 저장된 `{universe_code or 'PIT monthly'}` 월말 universe snapshot을 리밸런싱 날짜별로 읽습니다. "
        "이 V1 snapshot은 DB 가격과 latest-known statement shares 기반의 근사 PIT이며 공식 지수 membership은 아닙니다."
    )


def _resolve_pit_monthly_universe_inputs(
    *,
    start: str | None,
    end: str | None,
    target_size: int,
    universe_code: str | None = None,
) -> tuple[list[str], dict[str, list[str]], str]:
    resolved_code = universe_code or normalize_pit_universe_code(target_size)
    snapshots = load_pit_universe_membership_snapshots(
        resolved_code,
        start=start,
        end=end,
        target_size=target_size,
    )
    if not snapshots:
        raise _data_error(
            f"No PIT monthly universe snapshots were found for `{resolved_code}` in the requested date range. "
            "Build the monthly PIT universe snapshots before running this contract."
        )

    symbols: list[str] = []
    seen: set[str] = set()
    for members in snapshots.values():
        for symbol in members:
            normalized = str(symbol or "").strip().upper()
            if normalized and normalized not in seen:
                symbols.append(normalized)
                seen.add(normalized)
    if not symbols:
        raise _data_error(
            f"PIT monthly universe snapshots for `{resolved_code}` do not contain any included members."
        )
    return symbols, snapshots, resolved_code


def _resolve_strict_universe_contract_inputs(
    *,
    normalized_tickers: list[str],
    universe_contract: str,
    dynamic_candidate_tickers: Sequence[str] | None,
    dynamic_target_size: int | None,
    start: str | None,
    end: str | None,
) -> tuple[list[str], int | None, dict[str, list[str]] | None, str | None]:
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)
        return universe_input_tickers, dynamic_target_size, None, None
    if universe_contract == PIT_MONTHLY_SNAPSHOT_UNIVERSE:
        target_size = int(dynamic_target_size or len(normalized_tickers))
        symbols, snapshots, universe_code = _resolve_pit_monthly_universe_inputs(
            start=start,
            end=end,
            target_size=target_size,
        )
        return symbols, target_size, snapshots, universe_code
    return normalized_tickers, dynamic_target_size, None, None


def _strict_universe_builder_scope(
    *,
    universe_contract: str,
    statement_freq: str,
) -> str | None:
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        return f"{statement_freq}_first_pass"
    if universe_contract == PIT_MONTHLY_SNAPSHOT_UNIVERSE:
        return f"{statement_freq}_pit_monthly_snapshot"
    return None


def _preflight_quality_snapshot_data(
    *,
    tickers: list[str],
    end: str | None,
    factor_freq: str,
    quality_factors: list[str],
) -> None:
    if end is None:
        raise _input_error("Quality snapshot strategy requires an end date.")

    snapshot = load_factor_snapshot(
        quality_factors,
        symbols=tickers,
        as_of_date=end,
        freq=factor_freq,
    )
    if snapshot.empty:
        raise _data_error(
            "No factor snapshot rows were found for the requested tickers and end date. "
            "Run the fundamentals/factors pipeline first."
        )

    available_symbols = set(snapshot["symbol"].astype(str).str.upper().unique().tolist())
    missing = [ticker for ticker in tickers if ticker not in available_symbols]
    if len(missing) == len(tickers):
        raise _data_error(
            "None of the requested tickers have factor snapshot rows for the selected end date."
        )


def _preflight_statement_quality_data(
    *,
    tickers: list[str],
    end: str | None,
    statement_freq: str,
) -> None:
    if end is None:
        raise _input_error("Statement-driven quality prototype requires an end date.")

    snapshot = load_statement_snapshot_strict(
        symbols=tickers,
        as_of_date=end,
        freq=statement_freq,
    )
    if snapshot.empty:
        raise _data_error(
            "No strict statement snapshot rows were found for the requested tickers and end date. "
            "Run Extended Statement Refresh first."
        )

    available_symbols = set(snapshot["symbol"].astype(str).str.upper().unique().tolist())
    if not available_symbols:
        raise _data_error(
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
        raise _input_error("Statement-driven shadow quality path requires an end date.")

    snapshot = load_statement_factor_snapshot_shadow(
        factor_names,
        symbols=tickers,
        as_of_date=end,
        freq=statement_freq,
    )
    if snapshot.empty:
        raise _data_error(
            "No statement-driven shadow factor snapshot rows were found for the requested tickers and end date. "
            "Run Extended Statement Refresh and rebuild statement shadow factors first."
        )


def inspect_strict_annual_price_freshness(
    *,
    tickers: Sequence[str] | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    context_label: str = "selected universe",
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    label = str(context_label or "selected universe").strip() or "selected universe"
    end_ts = pd.to_datetime(end).normalize() if end is not None else None
    effective_end_ts = end_ts

    if end_ts is not None:
        market_latest = load_latest_market_date(end=end, timeframe=timeframe)
        if market_latest is not None and pd.notna(market_latest):
            effective_end_ts = market_latest.normalize()

    summary = load_price_freshness_summary(
        symbols=normalized_tickers,
        end=end,
        timeframe=timeframe,
    )
    if summary.empty:
        return {
            "status": "error",
            "message": f"No DB price rows were found for the {label}.",
            "details": {
                "requested_count": len(normalized_tickers),
                "covered_count": 0,
                "missing_count": len(normalized_tickers),
                "missing_symbols": normalized_tickers[:20],
                "selected_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
                "effective_end_date": effective_end_ts.strftime("%Y-%m-%d") if effective_end_ts is not None else None,
                "effective_end_shift_days": (
                    int((end_ts - effective_end_ts).days)
                    if end_ts is not None and effective_end_ts is not None
                    else 0
                ),
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
            "message": f"No usable DB price dates were found for the {label}.",
            "details": {
                "requested_count": len(normalized_tickers),
                "covered_count": 0,
                "missing_count": len(normalized_tickers),
                "missing_symbols": normalized_tickers[:20],
                "selected_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
                "effective_end_date": effective_end_ts.strftime("%Y-%m-%d") if effective_end_ts is not None else None,
                "effective_end_shift_days": (
                    int((end_ts - effective_end_ts).days)
                    if end_ts is not None and effective_end_ts is not None
                    else 0
                ),
            },
        }

    common_latest = working["latest_date"].min().normalize()
    newest_latest = working["latest_date"].max().normalize()
    spread_days = int((newest_latest - common_latest).days)
    target_end = effective_end_ts if effective_end_ts is not None else newest_latest
    effective_shift_days = (
        int((end_ts - target_end).days) if end_ts is not None and target_end is not None else 0
    )

    stale_df = working[working["latest_date"].dt.normalize() < target_end].sort_values(["latest_date", "symbol"])
    lagging_df = working[working["latest_date"].dt.normalize() < newest_latest].sort_values(["latest_date", "symbol"])
    stale_symbols_all = stale_df["symbol"].tolist()
    lagging_symbols_all = lagging_df["symbol"].tolist()

    classification_symbols = sorted(set(stale_symbols_all + missing_symbols))
    classification_rows: list[dict[str, Any]] = []
    reason_counts: dict[str, int] = {}
    if classification_symbols:
        profile_df = load_asset_profile_status_summary(classification_symbols)
        profile_map = {
            str(row["symbol"]).upper(): row
            for _, row in profile_df.iterrows()
            if row.get("symbol") is not None
        }

        def _classify_reason(symbol: str, latest_date: pd.Timestamp | None) -> dict[str, Any]:
            profile = profile_map.get(symbol, {})
            profile_status = str(profile.get("status") or "").strip().lower()
            profile_error = str(profile.get("error_msg") or "").strip() or None
            delisted_at = profile.get("delisted_at")
            lag_days = None
            if latest_date is not None and pd.notna(latest_date) and target_end is not None:
                lag_days = int((target_end - latest_date.normalize()).days)

            if profile_status in {"delisted", "not_found"} or pd.notna(delisted_at):
                reason = "likely_delisted_or_symbol_changed"
                note = "Asset profile already marks this symbol as unavailable or delisted."
            elif profile_status == "error":
                reason = "asset_profile_error"
                note = "Asset profile collection is in an error state for this symbol."
            elif latest_date is None or pd.isna(latest_date):
                reason = "missing_price_rows"
                note = "No DB daily price rows exist for the selected timeframe."
            elif lag_days is not None and lag_days <= 7:
                reason = "minor_source_lag"
                note = "The symbol lags the selected end date by less than or equal to 7 days."
            elif lag_days is not None and lag_days <= 30:
                reason = "source_gap_or_symbol_issue"
                note = "The symbol has a material lag versus the selected end date while still looking active in asset profile."
            else:
                reason = "persistent_source_gap_or_symbol_issue"
                note = "The symbol is far behind the selected end date and may need provider or symbol-status investigation."

            if profile_error and reason != "asset_profile_error":
                note = f"{note} asset_profile_error={profile_error}"

            return {
                "symbol": symbol,
                "latest_date": (
                    latest_date.normalize().strftime("%Y-%m-%d")
                    if latest_date is not None and pd.notna(latest_date)
                    else None
                ),
                "lag_days": lag_days,
                "profile_status": profile_status or None,
                "reason": reason,
                "note": note,
            }

        for symbol in classification_symbols:
            latest_match = working.loc[working["symbol"] == symbol, "latest_date"]
            latest_date = latest_match.iloc[0] if not latest_match.empty else None
            row = _classify_reason(symbol, latest_date)
            classification_rows.append(row)
            reason_counts[row["reason"]] = reason_counts.get(row["reason"], 0) + 1

    details = {
        "requested_count": len(normalized_tickers),
        "covered_count": int(len(working)),
        "missing_count": len(missing_symbols),
        "missing_symbols": missing_symbols[:20],
        "missing_symbols_all": missing_symbols,
        "selected_end_date": end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
        "target_end_date": target_end.strftime("%Y-%m-%d") if target_end is not None else None,
        "effective_end_date": target_end.strftime("%Y-%m-%d") if target_end is not None else None,
        "effective_end_shift_days": effective_shift_days,
        "effective_end_basis": (
            "latest_market_date_on_or_before_selected_end"
            if effective_shift_days > 0
            else "selected_end_date"
        ),
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
        "reason_counts": reason_counts,
        "classification_rows": classification_rows[:50],
        "classification_scope": "heuristic",
    }

    if not missing_symbols and len(stale_df) == 0 and spread_days == 0:
        if effective_shift_days > 0 and end_ts is not None:
            message = (
                f"All {len(normalized_tickers)} {label} symbols have price data through effective trading end "
                f"`{target_end.strftime('%Y-%m-%d')}`. Selected end `{end_ts.strftime('%Y-%m-%d')}` does not have "
                "a later DB market session."
            )
        else:
            message = (
                f"All {len(normalized_tickers)} {label} symbols have price data through "
                f"`{common_latest.strftime('%Y-%m-%d')}`."
            )
        return {
            "status": "ok",
            "message": message,
            "details": details,
        }

    message_parts: list[str] = []
    if effective_shift_days > 0 and end_ts is not None:
        message_parts.append(
            f"Selected end `{end_ts.strftime('%Y-%m-%d')}` maps to effective trading end "
            f"`{target_end.strftime('%Y-%m-%d')}` for DB freshness checks."
        )
    if missing_symbols:
        message_parts.append(f"{len(missing_symbols)} {label} symbols have no DB price rows.")
    if len(stale_df) > 0:
        message_parts.append(
            f"{len(stale_df)} symbols stop before the effective trading end `{target_end.strftime('%Y-%m-%d')}`."
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


def _latest_result_date_string(result_df: pd.DataFrame) -> str | None:
    if result_df is None or result_df.empty or "Date" not in result_df.columns:
        return None
    result_dates = pd.to_datetime(result_df["Date"], errors="coerce").dropna()
    if result_dates.empty:
        return None
    return pd.Timestamp(result_dates.max()).normalize().strftime("%Y-%m-%d")


def _apply_dynamic_runnable_coverage_price_status(
    bundle: dict[str, Any],
    *,
    price_freshness: dict[str, Any],
    universe_debug: dict[str, Any] | None,
    result_df: pd.DataFrame,
) -> None:
    """Mark Dynamic PIT backfilled coverage as the effective data-trust basis."""
    debug = dict(universe_debug or {})
    if debug.get("contract") != HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        return

    target_size = int(debug.get("target_size") or 0)
    latest_membership_count = int(debug.get("last_membership_count") or 0)
    candidate_pool_count = int(debug.get("candidate_pool_count") or 0)
    if target_size <= 0:
        return

    status = "ok" if latest_membership_count >= target_size else "warning"
    actual_end = _latest_result_date_string(result_df)
    original_details = dict(price_freshness.get("details") or {})
    runnable_coverage = {
        "status": status,
        "contract": HISTORICAL_DYNAMIC_PIT_UNIVERSE,
        "target_size": target_size,
        "latest_membership_count": latest_membership_count,
        "min_membership_count": int(debug.get("min_membership_count") or 0),
        "max_membership_count": int(debug.get("max_membership_count") or 0),
        "candidate_pool_count": candidate_pool_count,
        "candidate_pool_price_status": str(price_freshness.get("status") or "").strip().lower() or None,
        "candidate_pool_missing_count": int(original_details.get("missing_count") or 0),
        "candidate_pool_stale_count": int(original_details.get("stale_count") or 0),
    }

    bundle.setdefault("meta", {})["runnable_coverage"] = runnable_coverage
    if status != "ok":
        return

    effective_end = (
        actual_end
        or original_details.get("effective_end_date")
        or original_details.get("target_end_date")
        or original_details.get("common_latest_date")
        or original_details.get("selected_end_date")
    )
    selected_end = original_details.get("selected_end_date") or effective_end
    warning_prefixes = ("가격 최신성 사전 점검:", "Price freshness preflight:")
    existing_warnings = [
        str(warning)
        for warning in bundle["meta"].get("warnings") or []
        if not str(warning).startswith(warning_prefixes)
    ]
    existing_warnings.append(
        "Dynamic PIT runnable coverage backfill: "
        f"target {target_size} was filled from {candidate_pool_count} candidate symbols. "
        "Candidate-pool stale/missing symbols are non-blocking unless runnable membership drops below target."
    )
    bundle["meta"]["warnings"] = existing_warnings
    bundle["meta"]["candidate_pool_price_freshness"] = price_freshness
    bundle["meta"]["price_freshness"] = {
        "status": "ok",
        "message": (
            f"Dynamic PIT backfill filled the runnable coverage target "
            f"({latest_membership_count}/{target_size}) through `{effective_end}`. "
            "Candidate-pool stale or missing symbols are retained as non-blocking context."
        ),
        "details": {
            "requested_count": target_size,
            "covered_count": latest_membership_count,
            "missing_count": 0,
            "missing_symbols": [],
            "missing_symbols_all": [],
            "selected_end_date": selected_end,
            "target_end_date": effective_end,
            "effective_end_date": effective_end,
            "effective_end_shift_days": original_details.get("effective_end_shift_days", 0),
            "effective_end_basis": original_details.get("effective_end_basis"),
            "common_latest_date": effective_end,
            "newest_latest_date": effective_end,
            "spread_days": 0,
            "stale_count": 0,
            "stale_symbols": [],
            "stale_symbols_all": [],
            "lagging_count": 0,
            "lagging_symbols": [],
            "lagging_symbols_all": [],
            "refresh_symbols_all": [],
            "runnable_coverage_status": status,
            "runnable_coverage_target_size": target_size,
            "runnable_coverage_latest_membership_count": latest_membership_count,
            "candidate_pool_count": candidate_pool_count,
            "candidate_pool_price_status": runnable_coverage["candidate_pool_price_status"],
            "candidate_pool_missing_count": runnable_coverage["candidate_pool_missing_count"],
            "candidate_pool_stale_count": runnable_coverage["candidate_pool_stale_count"],
        },
    }


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
        raise _input_error("The first public quality snapshot runtime supports only 'broad_research' mode.")
    if rebalance_freq != "monthly":
        raise _input_error("The first public quality snapshot runtime currently supports only monthly rebalance.")

    normalized_factors = [str(name).strip() for name in (quality_factors or ["roe", "gross_margin", "operating_margin", "debt_ratio"]) if str(name).strip()]
    if not normalized_factors:
        raise _input_error("At least one quality factor must be provided.")

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
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    guardrail_reference_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
    static_warnings: Sequence[str] | None = None,
    snapshot_source: str = "rebuild_statement",
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )
    effective_guardrail_reference_ticker = _resolve_guardrail_reference_ticker(
        benchmark_ticker,
        guardrail_reference_ticker,
    )
    strict_label = f"strict {statement_freq}"
    (
        universe_input_tickers,
        dynamic_target_size,
        pit_membership_snapshots,
        pit_universe_code,
    ) = _resolve_strict_universe_contract_inputs(
        normalized_tickers=normalized_tickers,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        start=start,
        end=end,
    )

    normalized_factors = [
        str(name).strip()
        for name in (quality_factors or QUALITY_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise _input_error("At least one quality factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract in {HISTORICAL_DYNAMIC_PIT_UNIVERSE, PIT_MONTHLY_SNAPSHOT_UNIVERSE}:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    effective_defensive_tickers = (
        _normalize_tickers(defensive_tickers or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE
        else []
    )
    if effective_defensive_tickers:
        defensive_only = [ticker for ticker in effective_defensive_tickers if ticker not in universe_input_tickers]
        if defensive_only:
            _preflight_price_strategy_data(
                tickers=defensive_only,
                start=start,
                end=end,
                timeframe=timeframe,
            )
    if underperformance_guardrail_enabled and effective_guardrail_reference_ticker:
        _preflight_price_strategy_data(
            tickers=[effective_guardrail_reference_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if drawdown_guardrail_enabled and effective_guardrail_reference_ticker:
        _preflight_price_strategy_data(
            tickers=[effective_guardrail_reference_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if snapshot_source == "shadow_factors":
        _preflight_statement_quality_shadow_data(
            tickers=universe_input_tickers,
            end=end,
            statement_freq=statement_freq,
            factor_names=normalized_factors,
        )
        result_payload = get_statement_quality_snapshot_shadow_from_db(
            tickers=normalized_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
            option=option,
            statement_freq=statement_freq,
            quality_factors=normalized_factors,
            top_n=top_n,
            rebalance_interval=rebalance_interval,
            min_price=float(min_price_filter or 0.0),
            min_history_months=int(min_history_months_filter or 0),
            min_avg_dollar_volume_20d_m=float(min_avg_dollar_volume_20d_m_filter or 0.0),
            trend_filter_enabled=trend_filter_enabled,
            trend_filter_window=trend_filter_window,
            weighting_mode=weighting_mode,
            rejected_slot_fill_enabled=rejected_slot_fill_enabled,
            partial_cash_retention_enabled=partial_cash_retention_enabled,
            risk_off_mode=risk_off_mode,
            defensive_tickers=effective_defensive_tickers,
            market_regime_enabled=market_regime_enabled,
            market_regime_window=market_regime_window,
            market_regime_benchmark=market_regime_benchmark,
            benchmark_ticker=benchmark_ticker,
            guardrail_reference_ticker=effective_guardrail_reference_ticker,
            underperformance_guardrail_enabled=underperformance_guardrail_enabled,
            underperformance_guardrail_window_months=underperformance_guardrail_window_months,
            underperformance_guardrail_threshold=underperformance_guardrail_threshold,
            drawdown_guardrail_enabled=drawdown_guardrail_enabled,
            drawdown_guardrail_window_months=drawdown_guardrail_window_months,
            drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
            drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
            universe_contract=universe_contract,
            dynamic_candidate_tickers=universe_input_tickers,
            dynamic_target_size=dynamic_target_size,
            pit_membership_snapshots=pit_membership_snapshots,
            pit_universe_code=pit_universe_code,
            return_details=True,
        )
        result_df = result_payload["result_df"]
        universe_debug = result_payload.get("universe_debug")
        dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
        dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []
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
        universe_debug = None
        dynamic_universe_snapshot_rows = []
        dynamic_candidate_status_rows = []

    warnings: list[str] = list(static_warnings or [])
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning(statement_freq))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool 참고: "
                f"{dynamic_price_pool['missing_count']}개 후보 symbol은 선택한 종료일까지 DB 가격 이력이 없어 "
                f"근사 PIT membership 구성에서 자연스럽게 제외되었습니다: {preview}{more}"
            )
    elif universe_contract == PIT_MONTHLY_SNAPSHOT_UNIVERSE:
        warnings.append(_pit_monthly_universe_warning(pit_universe_code))
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 사전 점검: "
            + price_freshness["message"]
            + f" 대형 universe `{strict_label}` 실행에서는 지연 symbol이 갱신되기 전까지 마지막 월 데이터가 중복되거나 밀려 보일 수 있습니다."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "요청한 시작일에는 사용할 수 있는 strict statement snapshot row가 없었습니다. "
                    f"전략은 `{first_active_date}`까지 현금 상태로 대기했습니다."
                )
    if min_history_months_filter:
        warnings.append(
            "최소 가격 이력 필터가 켜져 있습니다: 각 리밸런싱 전에 후보 종목은 최소 "
            f"`{int(min_history_months_filter)}개월`의 DB 가격 이력이 필요합니다."
        )
    if min_avg_dollar_volume_20d_m_filter:
        warnings.append(
            "유동성 필터가 켜져 있습니다: 각 리밸런싱 전에 후보 종목은 최근 20거래일 평균 거래대금이 최소 "
            f"`{float(min_avg_dollar_volume_20d_m_filter):.1f}M 달러` 이상이어야 합니다."
        )

    input_params = {
        "tickers": normalized_tickers,
        "start": start,
        "end": end,
        "timeframe": timeframe,
        "option": option,
        "top": top_n,
        "rebalance_interval": rebalance_interval,
        "factor_freq": statement_freq,
        "quality_factors": normalized_factors,
        "trend_filter_enabled": trend_filter_enabled,
        "trend_filter_window": trend_filter_window,
        "weighting_mode": weighting_mode,
        "rejected_slot_handling_mode": rejected_slot_handling_mode,
        "rejected_slot_fill_enabled": rejected_slot_fill_enabled,
        "partial_cash_retention_enabled": partial_cash_retention_enabled,
        "risk_off_mode": risk_off_mode,
        "defensive_tickers": effective_defensive_tickers,
        "market_regime_enabled": market_regime_enabled,
        "market_regime_window": market_regime_window,
        "market_regime_benchmark": market_regime_benchmark,
        "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
        "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
        "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
        "snapshot_mode": f"strict_statement_{statement_freq}",
        "universe_mode": universe_mode,
        "preset_name": preset_name,
        "snapshot_source": snapshot_source,
        "universe_contract": universe_contract,
        "dynamic_target_size": dynamic_target_size,
        "dynamic_candidate_count": len(universe_input_tickers),
        "dynamic_candidate_preview": universe_input_tickers[:20],
        "pit_universe_code": pit_universe_code,
        "universe_builder_scope": _strict_universe_builder_scope(
            universe_contract=universe_contract,
            statement_freq=statement_freq,
        ),
        "universe_debug": universe_debug,
    }
    if min_price_filter is not None:
        input_params["min_price_filter"] = min_price_filter
    if min_history_months_filter is not None:
        input_params["min_history_months_filter"] = int(min_history_months_filter or 0)
    if min_avg_dollar_volume_20d_m_filter is not None:
        input_params["min_avg_dollar_volume_20d_m_filter"] = float(min_avg_dollar_volume_20d_m_filter or 0.0)
    if transaction_cost_bps is not None:
        input_params["transaction_cost_bps"] = transaction_cost_bps
    if benchmark_contract is not None:
        input_params["benchmark_contract"] = str(benchmark_contract or STRICT_DEFAULT_BENCHMARK_CONTRACT).strip().lower()
    if benchmark_ticker is not None:
        input_params["benchmark_ticker"] = benchmark_ticker
    if effective_guardrail_reference_ticker:
        input_params["guardrail_reference_ticker"] = effective_guardrail_reference_ticker
    if promotion_min_benchmark_coverage is not None:
        input_params["promotion_min_benchmark_coverage"] = float(promotion_min_benchmark_coverage)
    if promotion_min_net_cagr_spread is not None:
        input_params["promotion_min_net_cagr_spread"] = float(promotion_min_net_cagr_spread)
    if promotion_min_liquidity_clean_coverage is not None:
        input_params["promotion_min_liquidity_clean_coverage"] = float(promotion_min_liquidity_clean_coverage)
    if promotion_max_underperformance_share is not None:
        input_params["promotion_max_underperformance_share"] = float(promotion_max_underperformance_share)
    if promotion_min_worst_rolling_excess_return is not None:
        input_params["promotion_min_worst_rolling_excess_return"] = float(promotion_min_worst_rolling_excess_return)
    if promotion_max_strategy_drawdown is not None:
        input_params["promotion_max_strategy_drawdown"] = float(promotion_max_strategy_drawdown)
    if promotion_max_drawdown_gap_vs_benchmark is not None:
        input_params["promotion_max_drawdown_gap_vs_benchmark"] = float(promotion_max_drawdown_gap_vs_benchmark)
    if drawdown_guardrail_enabled is not None:
        input_params["drawdown_guardrail_enabled"] = bool(drawdown_guardrail_enabled)
    if drawdown_guardrail_window_months is not None:
        input_params["drawdown_guardrail_window_months"] = int(drawdown_guardrail_window_months)
    if drawdown_guardrail_strategy_threshold is not None:
        input_params["drawdown_guardrail_strategy_threshold"] = float(drawdown_guardrail_strategy_threshold)
    if drawdown_guardrail_gap_threshold is not None:
        input_params["drawdown_guardrail_gap_threshold"] = float(drawdown_guardrail_gap_threshold)

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name=strategy_name,
        strategy_key=strategy_key,
        input_params=input_params,
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors" if snapshot_source == "shadow_factors" else "db_backed_strict_statement_snapshot",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    _apply_dynamic_runnable_coverage_price_status(
        bundle,
        price_freshness=price_freshness,
        universe_debug=universe_debug,
        result_df=result_df,
    )
    if "Defensive Sleeve Count" in result_df.columns:
        defensive_sleeve_active = result_df["Defensive Sleeve Count"].fillna(0).astype(float) > 0
        bundle["meta"]["defensive_sleeve_active_count"] = int(defensive_sleeve_active.sum())
        bundle["meta"]["defensive_sleeve_active_share"] = (
            float(defensive_sleeve_active.mean()) if not defensive_sleeve_active.empty else 0.0
        )
    if trend_filter_enabled:
        trend_warning = _build_strict_rejected_slot_handling_warning(
            trend_filter_window=trend_filter_window,
            rejected_slot_handling_mode=rejected_slot_handling_mode,
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [trend_warning]
    if weighting_mode == STRICT_WEIGHTING_MODE_RANK_TAPERED:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "집중도 완화 비중 방식이 켜져 있습니다: 선택 종목을 단순 동일비중으로 두지 않고 순위에 따라 완만하게 차등 배분합니다."
        ]
    if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Strict annual 방어자산 sleeve 계약이 켜져 있습니다: 완전 risk-off 상태에서는 전액 현금 대신 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
        ]
    if market_regime_enabled:
        regime_warning = (
            f"Market Regime Overlay가 켜져 있습니다: `{market_regime_benchmark}`가 `MA{market_regime_window}` 아래에서 마감하면 "
            f"월말 선택 종목을 `{', '.join(effective_defensive_tickers)}`로 회전합니다."
            if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers
            else f"Market Regime Overlay가 켜져 있습니다: `{market_regime_benchmark}`가 `MA{market_regime_window}` 아래에서 마감하면 월말 선택 종목을 전액 현금으로 이동합니다."
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [regime_warning]
    if underperformance_guardrail_enabled:
        under_warning = (
            "상대 성과 Guardrail이 켜져 있습니다: 최근 "
            f"`{underperformance_guardrail_window_months}개월` 전략 초과수익률이 `{effective_guardrail_reference_ticker}` 대비 "
            f"`{underperformance_guardrail_threshold:.0%}` 아래로 내려가면 리밸런싱 후보를 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
            if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers
            else "상대 성과 Guardrail이 켜져 있습니다: 최근 "
            f"`{underperformance_guardrail_window_months}개월` 전략 초과수익률이 `{effective_guardrail_reference_ticker}` 대비 "
            f"`{underperformance_guardrail_threshold:.0%}` 아래로 내려가면 리밸런싱 후보를 현금으로 이동합니다."
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [under_warning]
    if drawdown_guardrail_enabled:
        drawdown_warning = (
            "Drawdown Guardrail이 켜져 있습니다: 최근 "
            f"`{drawdown_guardrail_window_months}개월` 전략 drawdown이 `{drawdown_guardrail_strategy_threshold:.0%}` 아래로 내려가거나 "
            f"`{effective_guardrail_reference_ticker}` 대비 drawdown gap이 `{drawdown_guardrail_gap_threshold:.0%}`를 넘으면 "
            f"리밸런싱 후보를 `{', '.join(effective_defensive_tickers)}`로 회전합니다."
            if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers
            else "Drawdown Guardrail이 켜져 있습니다: 최근 "
            f"`{drawdown_guardrail_window_months}개월` 전략 drawdown이 `{drawdown_guardrail_strategy_threshold:.0%}` 아래로 내려가거나 "
            f"`{effective_guardrail_reference_ticker}` 대비 drawdown gap이 `{drawdown_guardrail_gap_threshold:.0%}`를 넘으면 리밸런싱 후보를 현금으로 이동합니다."
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [drawdown_warning]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
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
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    guardrail_reference_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    bundle = _run_statement_quality_bundle(
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
        min_price_filter=min_price_filter,
        min_history_months_filter=min_history_months_filter,
        min_avg_dollar_volume_20d_m_filter=min_avg_dollar_volume_20d_m_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=guardrail_reference_ticker,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_handling_mode=rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        universe_mode=universe_mode,
        preset_name=preset_name,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        snapshot_source="shadow_factors",
        static_warnings=[
            "Strict annual statement 경로입니다: 빠른 실행을 위해 사전 계산된 statement shadow factor로 annual statement 기반 quality snapshot을 순위화합니다.",
        ],
    )
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=_resolve_guardrail_reference_ticker(
            benchmark_ticker,
            guardrail_reference_ticker,
        ),
        benchmark_universe_tickers=_normalize_tickers(dynamic_candidate_tickers or tickers),
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
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
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
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
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
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
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    guardrail_reference_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )
    effective_guardrail_reference_ticker = _resolve_guardrail_reference_ticker(
        benchmark_ticker,
        guardrail_reference_ticker,
    )
    (
        universe_input_tickers,
        dynamic_target_size,
        pit_membership_snapshots,
        pit_universe_code,
    ) = _resolve_strict_universe_contract_inputs(
        normalized_tickers=normalized_tickers,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        start=start,
        end=end,
    )

    normalized_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise _input_error("At least one value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract in {HISTORICAL_DYNAMIC_PIT_UNIVERSE, PIT_MONTHLY_SNAPSHOT_UNIVERSE}:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    effective_defensive_tickers = (
        _normalize_tickers(defensive_tickers or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE
        else []
    )
    if effective_defensive_tickers:
        defensive_only = [ticker for ticker in effective_defensive_tickers if ticker not in universe_input_tickers]
        if defensive_only:
            _preflight_price_strategy_data(
                tickers=defensive_only,
                start=start,
                end=end,
                timeframe=timeframe,
            )
    if underperformance_guardrail_enabled and effective_guardrail_reference_ticker:
        _preflight_price_strategy_data(
            tickers=[effective_guardrail_reference_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if drawdown_guardrail_enabled and effective_guardrail_reference_ticker:
        _preflight_price_strategy_data(
            tickers=[effective_guardrail_reference_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="annual",
        factor_names=normalized_factors,
    )

    result_payload = get_statement_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="annual",
        value_factors=normalized_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        min_price=min_price_filter,
        min_history_months=min_history_months_filter,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m_filter,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_handling_mode=rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=effective_guardrail_reference_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        pit_membership_snapshots=pit_membership_snapshots,
        pit_universe_code=pit_universe_code,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Strict annual value 경로입니다: 사전 계산된 statement shadow factor를 사용해 annual statement 기반 value snapshot을 순위화합니다.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("annual"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool 참고: "
                f"{dynamic_price_pool['missing_count']}개 후보 symbol은 선택한 종료일까지 DB 가격 이력이 없어 "
                f"근사 PIT membership 구성에서 자연스럽게 제외되었습니다: {preview}{more}"
            )
    elif universe_contract == PIT_MONTHLY_SNAPSHOT_UNIVERSE:
        warnings.append(_pit_monthly_universe_warning(pit_universe_code))
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 사전 점검: "
            + price_freshness["message"]
            + " 대형 universe strict annual 실행에서는 지연 symbol이 갱신되기 전까지 마지막 월 데이터가 중복되거나 밀려 보일 수 있습니다."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "요청한 시작일에는 사용할 수 있는 strict statement shadow row가 없었습니다. "
                    f"전략은 `{first_active_date}`까지 현금 상태로 대기했습니다."
                )
    if min_history_months_filter:
        warnings.append(
            "최소 가격 이력 필터가 켜져 있습니다: 각 리밸런싱 전에 후보 종목은 최소 "
            f"`{int(min_history_months_filter)}개월`의 DB 가격 이력이 필요합니다."
        )
    if min_avg_dollar_volume_20d_m_filter:
        warnings.append(
            "유동성 필터가 켜져 있습니다: 각 리밸런싱 전에 후보 종목은 최근 20거래일 평균 거래대금이 최소 "
            f"`{float(min_avg_dollar_volume_20d_m_filter):.1f}M 달러` 이상이어야 합니다."
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
            "min_price_filter": min_price_filter,
            "min_history_months_filter": int(min_history_months_filter or 0),
            "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter or 0.0),
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_contract": benchmark_contract,
            "benchmark_ticker": benchmark_ticker,
            "guardrail_reference_ticker": effective_guardrail_reference_ticker,
            "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
            "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
            "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
            "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
            "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
            "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
            "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
            "factor_freq": "annual",
            "value_factors": normalized_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "weighting_mode": weighting_mode,
            "rejected_slot_handling_mode": rejected_slot_handling_mode,
            "rejected_slot_fill_enabled": rejected_slot_fill_enabled,
            "partial_cash_retention_enabled": partial_cash_retention_enabled,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
            "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
            "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
            "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
            "snapshot_mode": "strict_statement_annual",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "pit_universe_code": pit_universe_code,
            "universe_builder_scope": _strict_universe_builder_scope(
                universe_contract=universe_contract,
                statement_freq="annual",
            ),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    _apply_dynamic_runnable_coverage_price_status(
        bundle,
        price_freshness=price_freshness,
        universe_debug=universe_debug,
        result_df=result_df,
    )
    if "Defensive Sleeve Count" in result_df.columns:
        defensive_sleeve_active = result_df["Defensive Sleeve Count"].fillna(0).astype(float) > 0
        bundle["meta"]["defensive_sleeve_active_count"] = int(defensive_sleeve_active.sum())
        bundle["meta"]["defensive_sleeve_active_share"] = (
            float(defensive_sleeve_active.mean()) if not defensive_sleeve_active.empty else 0.0
        )
    if trend_filter_enabled:
        trend_warning = _build_strict_rejected_slot_handling_warning(
            trend_filter_window=trend_filter_window,
            rejected_slot_handling_mode=rejected_slot_handling_mode,
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [trend_warning]
    if weighting_mode == STRICT_WEIGHTING_MODE_RANK_TAPERED:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "집중도 완화 비중 방식이 켜져 있습니다: 선택 종목을 단순 동일비중으로 두지 않고 순위에 따라 완만하게 차등 배분합니다."
        ]
    if market_regime_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Market Regime Overlay가 켜져 있습니다: `{market_regime_benchmark}`가 `MA{market_regime_window}` 아래에서 마감하면 월말 선택 종목을 전액 현금으로 이동합니다."
        ]
    if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Strict annual 방어자산 sleeve 계약이 켜져 있습니다: 완전 risk-off 상태에서는 전액 현금 대신 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
        ]
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "상대 성과 Guardrail이 켜져 있습니다: 최근 "
            f"`{underperformance_guardrail_window_months}개월` 전략 초과수익률이 `{effective_guardrail_reference_ticker}` 대비 "
            f"`{underperformance_guardrail_threshold:.0%}` 아래로 내려가면 리밸런싱 후보를 현금으로 이동합니다."
            if risk_off_mode != STRICT_RISK_OFF_MODE_DEFENSIVE or not effective_defensive_tickers
            else "상대 성과 Guardrail이 켜져 있습니다: 최근 "
            f"`{underperformance_guardrail_window_months}개월` 전략 초과수익률이 `{effective_guardrail_reference_ticker}` 대비 "
            f"`{underperformance_guardrail_threshold:.0%}` 아래로 내려가면 리밸런싱 후보를 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
        ]
    if drawdown_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Drawdown Guardrail이 켜져 있습니다: 최근 "
            f"`{drawdown_guardrail_window_months}개월` 전략 drawdown이 `{drawdown_guardrail_strategy_threshold:.0%}` 아래로 내려가거나 "
            f"`{effective_guardrail_reference_ticker}` 대비 drawdown gap이 `{drawdown_guardrail_gap_threshold:.0%}`를 넘으면 리밸런싱 후보를 현금으로 이동합니다."
            if risk_off_mode != STRICT_RISK_OFF_MODE_DEFENSIVE or not effective_defensive_tickers
            else "Drawdown Guardrail이 켜져 있습니다: 최근 "
            f"`{drawdown_guardrail_window_months}개월` 전략 drawdown이 `{drawdown_guardrail_strategy_threshold:.0%}` 아래로 내려가거나 "
            f"`{effective_guardrail_reference_ticker}` 대비 drawdown gap이 `{drawdown_guardrail_gap_threshold:.0%}`를 넘으면 리밸런싱 후보를 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
        ]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=effective_guardrail_reference_ticker,
        benchmark_universe_tickers=universe_input_tickers,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )


def run_value_snapshot_strict_quarterly_prototype_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    value_factors: Sequence[str] | None = None,
    top_n: int = 10,
    rebalance_interval: int = 1,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )
    (
        universe_input_tickers,
        dynamic_target_size,
        pit_membership_snapshots,
        pit_universe_code,
    ) = _resolve_strict_universe_contract_inputs(
        normalized_tickers=normalized_tickers,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        start=start,
        end=end,
    )

    normalized_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise _input_error("At least one quarterly value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract in {HISTORICAL_DYNAMIC_PIT_UNIVERSE, PIT_MONTHLY_SNAPSHOT_UNIVERSE}:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    effective_defensive_tickers = (
        _normalize_tickers(defensive_tickers or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE
        else []
    )
    if effective_defensive_tickers:
        defensive_only = [ticker for ticker in effective_defensive_tickers if ticker not in universe_input_tickers]
        if defensive_only:
            _preflight_price_strategy_data(
                tickers=defensive_only,
                start=start,
                end=end,
                timeframe=timeframe,
            )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="quarterly",
        factor_names=normalized_factors,
    )

    result_payload = get_statement_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="quarterly",
        value_factors=normalized_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        weighting_mode=weighting_mode,
        rejected_slot_handling_mode=rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=effective_defensive_tickers,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        pit_membership_snapshots=pit_membership_snapshots,
        pit_universe_code=pit_universe_code,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Research-only quarterly value prototype: ranks quarterly statement shadow value factors and is intended for quarterly family validation rather than public default use.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("quarterly"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool note: "
                f"{dynamic_price_pool['missing_count']} candidate symbols do not have any DB price history up to the selected end date "
                f"and were naturally excluded from the approximate PIT membership build: {preview}{more}"
            )
    elif universe_contract == PIT_MONTHLY_SNAPSHOT_UNIVERSE:
        warnings.append(_pit_monthly_universe_warning(pit_universe_code))
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Wider quarterly prototype runs can degrade in the final month until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable quarterly statement shadow rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Value Snapshot (Strict Quarterly Prototype)",
        strategy_key="value_snapshot_strict_quarterly_prototype",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": "quarterly",
            "value_factors": normalized_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "weighting_mode": weighting_mode,
            "rejected_slot_handling_mode": rejected_slot_handling_mode,
            "rejected_slot_fill_enabled": rejected_slot_fill_enabled,
            "partial_cash_retention_enabled": partial_cash_retention_enabled,
            "risk_off_mode": risk_off_mode,
            "defensive_tickers": effective_defensive_tickers,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "snapshot_mode": "strict_statement_quarterly",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "pit_universe_code": pit_universe_code,
            "universe_builder_scope": _strict_universe_builder_scope(
                universe_contract=universe_contract,
                statement_freq="quarterly",
            ),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    _apply_dynamic_runnable_coverage_price_status(
        bundle,
        price_freshness=price_freshness,
        universe_debug=universe_debug,
        result_df=result_df,
    )
    if trend_filter_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            _build_strict_rejected_slot_handling_warning(
                trend_filter_window=trend_filter_window,
                rejected_slot_handling_mode=rejected_slot_handling_mode,
            )
        ]
    if weighting_mode == STRICT_WEIGHTING_MODE_RANK_TAPERED:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Concentration-Aware Weighting enabled: selected holdings use a mild rank taper instead of pure equal weight."
        ]
    if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Strict quarterly defensive sleeve contract enabled: full risk-off states "
            f"rotate into `{', '.join(effective_defensive_tickers)}` instead of staying fully in cash."
        ]
    if market_regime_enabled:
        regime_warning = (
            f"Market Regime Overlay enabled: month-end selections rotate into `{', '.join(effective_defensive_tickers)}` "
            f"when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
            if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers
            else f"Market Regime Overlay enabled: month-end selections move fully to cash when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [regime_warning]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
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
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    min_history_months_filter: int = STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    min_avg_dollar_volume_20d_m_filter: float = STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_contract: str = STRICT_DEFAULT_BENCHMARK_CONTRACT,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    guardrail_reference_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    promotion_min_benchmark_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )
    effective_guardrail_reference_ticker = _resolve_guardrail_reference_ticker(
        benchmark_ticker,
        guardrail_reference_ticker,
    )
    (
        universe_input_tickers,
        dynamic_target_size,
        pit_membership_snapshots,
        pit_universe_code,
    ) = _resolve_strict_universe_contract_inputs(
        normalized_tickers=normalized_tickers,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        start=start,
        end=end,
    )

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
        raise _input_error("At least one strict annual quality/value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract in {HISTORICAL_DYNAMIC_PIT_UNIVERSE, PIT_MONTHLY_SNAPSHOT_UNIVERSE}:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    effective_defensive_tickers = (
        _normalize_tickers(defensive_tickers or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE
        else []
    )
    if effective_defensive_tickers:
        defensive_only = [ticker for ticker in effective_defensive_tickers if ticker not in universe_input_tickers]
        if defensive_only:
            _preflight_price_strategy_data(
                tickers=defensive_only,
                start=start,
                end=end,
                timeframe=timeframe,
            )
    if underperformance_guardrail_enabled and effective_guardrail_reference_ticker:
        _preflight_price_strategy_data(
            tickers=[effective_guardrail_reference_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if drawdown_guardrail_enabled and effective_guardrail_reference_ticker:
        _preflight_price_strategy_data(
            tickers=[effective_guardrail_reference_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="annual",
        factor_names=normalized_factor_names,
    )

    result_payload = get_statement_quality_value_snapshot_shadow_from_db(
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
        min_price=min_price_filter,
        min_history_months=min_history_months_filter,
        min_avg_dollar_volume_20d_m=min_avg_dollar_volume_20d_m_filter,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_handling_mode=rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=effective_guardrail_reference_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        pit_membership_snapshots=pit_membership_snapshots,
        pit_universe_code=pit_universe_code,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Strict annual multi-factor 경로입니다: coverage 우선 quality factor와 annual statement 기반 value factor를 함께 사용합니다.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("annual"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool 참고: "
                f"{dynamic_price_pool['missing_count']}개 후보 symbol은 선택한 종료일까지 DB 가격 이력이 없어 "
                f"근사 PIT membership 구성에서 자연스럽게 제외되었습니다: {preview}{more}"
            )
    elif universe_contract == PIT_MONTHLY_SNAPSHOT_UNIVERSE:
        warnings.append(_pit_monthly_universe_warning(pit_universe_code))
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 사전 점검: "
            + price_freshness["message"]
            + " 대형 universe strict annual 실행에서는 지연 symbol이 갱신되기 전까지 마지막 월 데이터가 중복되거나 밀려 보일 수 있습니다."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "요청한 시작일에는 사용할 수 있는 strict annual multi-factor snapshot row가 없었습니다. "
                    f"전략은 `{first_active_date}`까지 현금 상태로 대기했습니다."
                )
    if min_history_months_filter:
        warnings.append(
            "최소 가격 이력 필터가 켜져 있습니다: 각 리밸런싱 전에 후보 종목은 최소 "
            f"`{int(min_history_months_filter)}개월`의 DB 가격 이력이 필요합니다."
        )
    if min_avg_dollar_volume_20d_m_filter:
        warnings.append(
            "유동성 필터가 켜져 있습니다: 각 리밸런싱 전에 후보 종목은 최근 20거래일 평균 거래대금이 최소 "
            f"`{float(min_avg_dollar_volume_20d_m_filter):.1f}M 달러` 이상이어야 합니다."
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
            "min_price_filter": min_price_filter,
            "min_history_months_filter": int(min_history_months_filter or 0),
            "min_avg_dollar_volume_20d_m_filter": float(min_avg_dollar_volume_20d_m_filter or 0.0),
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_contract": benchmark_contract,
            "benchmark_ticker": benchmark_ticker,
            "guardrail_reference_ticker": effective_guardrail_reference_ticker,
            "promotion_min_benchmark_coverage": float(promotion_min_benchmark_coverage),
            "promotion_min_net_cagr_spread": float(promotion_min_net_cagr_spread),
            "promotion_min_liquidity_clean_coverage": float(promotion_min_liquidity_clean_coverage),
            "promotion_max_underperformance_share": float(promotion_max_underperformance_share),
            "promotion_min_worst_rolling_excess_return": float(promotion_min_worst_rolling_excess_return),
            "promotion_max_strategy_drawdown": float(promotion_max_strategy_drawdown),
            "promotion_max_drawdown_gap_vs_benchmark": float(promotion_max_drawdown_gap_vs_benchmark),
            "factor_freq": "annual",
            "quality_factors": normalized_quality_factors,
            "value_factors": normalized_value_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "weighting_mode": weighting_mode,
            "rejected_slot_handling_mode": rejected_slot_handling_mode,
            "rejected_slot_fill_enabled": rejected_slot_fill_enabled,
            "partial_cash_retention_enabled": partial_cash_retention_enabled,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "drawdown_guardrail_enabled": bool(drawdown_guardrail_enabled),
            "drawdown_guardrail_window_months": int(drawdown_guardrail_window_months),
            "drawdown_guardrail_strategy_threshold": float(drawdown_guardrail_strategy_threshold),
            "drawdown_guardrail_gap_threshold": float(drawdown_guardrail_gap_threshold),
            "snapshot_mode": "strict_statement_annual",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "pit_universe_code": pit_universe_code,
            "universe_builder_scope": _strict_universe_builder_scope(
                universe_contract=universe_contract,
                statement_freq="annual",
            ),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    _apply_dynamic_runnable_coverage_price_status(
        bundle,
        price_freshness=price_freshness,
        universe_debug=universe_debug,
        result_df=result_df,
    )
    if "Defensive Sleeve Count" in result_df.columns:
        defensive_sleeve_active = result_df["Defensive Sleeve Count"].fillna(0).astype(float) > 0
        bundle["meta"]["defensive_sleeve_active_count"] = int(defensive_sleeve_active.sum())
        bundle["meta"]["defensive_sleeve_active_share"] = (
            float(defensive_sleeve_active.mean()) if not defensive_sleeve_active.empty else 0.0
        )
    if trend_filter_enabled:
        trend_warning = _build_strict_rejected_slot_handling_warning(
            trend_filter_window=trend_filter_window,
            rejected_slot_handling_mode=rejected_slot_handling_mode,
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [trend_warning]
    if weighting_mode == STRICT_WEIGHTING_MODE_RANK_TAPERED:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "집중도 완화 비중 방식이 켜져 있습니다: 선택 종목을 단순 동일비중으로 두지 않고 순위에 따라 완만하게 차등 배분합니다."
        ]
    if market_regime_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            f"Market Regime Overlay가 켜져 있습니다: `{market_regime_benchmark}`가 `MA{market_regime_window}` 아래에서 마감하면 월말 선택 종목을 전액 현금으로 이동합니다."
        ]
    if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Strict annual 방어자산 sleeve 계약이 켜져 있습니다: 완전 risk-off 상태에서는 전액 현금 대신 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
        ]
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "상대 성과 Guardrail이 켜져 있습니다: 최근 "
            f"`{underperformance_guardrail_window_months}개월` 전략 초과수익률이 `{effective_guardrail_reference_ticker}` 대비 "
            f"`{underperformance_guardrail_threshold:.0%}` 아래로 내려가면 리밸런싱 후보를 현금으로 이동합니다."
            if risk_off_mode != STRICT_RISK_OFF_MODE_DEFENSIVE or not effective_defensive_tickers
            else "상대 성과 Guardrail이 켜져 있습니다: 최근 "
            f"`{underperformance_guardrail_window_months}개월` 전략 초과수익률이 `{effective_guardrail_reference_ticker}` 대비 "
            f"`{underperformance_guardrail_threshold:.0%}` 아래로 내려가면 리밸런싱 후보를 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
        ]
    if drawdown_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Drawdown Guardrail이 켜져 있습니다: 최근 "
            f"`{drawdown_guardrail_window_months}개월` 전략 drawdown이 `{drawdown_guardrail_strategy_threshold:.0%}` 아래로 내려가거나 "
            f"`{effective_guardrail_reference_ticker}` 대비 drawdown gap이 `{drawdown_guardrail_gap_threshold:.0%}`를 넘으면 리밸런싱 후보를 현금으로 이동합니다."
            if risk_off_mode != STRICT_RISK_OFF_MODE_DEFENSIVE or not effective_defensive_tickers
            else "Drawdown Guardrail이 켜져 있습니다: 최근 "
            f"`{drawdown_guardrail_window_months}개월` 전략 drawdown이 `{drawdown_guardrail_strategy_threshold:.0%}` 아래로 내려가거나 "
            f"`{effective_guardrail_reference_ticker}` 대비 drawdown gap이 `{drawdown_guardrail_gap_threshold:.0%}`를 넘으면 리밸런싱 후보를 "
            f"`{', '.join(effective_defensive_tickers)}`로 회전합니다."
        ]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=benchmark_contract,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=effective_guardrail_reference_ticker,
        benchmark_universe_tickers=universe_input_tickers,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )


def run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db(
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
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    _validate_backtest_date_range(start, end)
    rejected_slot_handling_mode = resolve_strict_rejection_handling_mode(
        rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
    )
    rejected_slot_fill_enabled, partial_cash_retention_enabled = strict_rejection_handling_mode_to_flags(
        rejected_slot_handling_mode
    )
    (
        universe_input_tickers,
        dynamic_target_size,
        pit_membership_snapshots,
        pit_universe_code,
    ) = _resolve_strict_universe_contract_inputs(
        normalized_tickers=normalized_tickers,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        start=start,
        end=end,
    )

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
        raise _input_error("At least one quarterly quality/value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract in {HISTORICAL_DYNAMIC_PIT_UNIVERSE, PIT_MONTHLY_SNAPSHOT_UNIVERSE}:
        dynamic_price_pool = _inspect_dynamic_universe_price_pool(
            tickers=universe_input_tickers,
            end=end,
            timeframe=timeframe,
        )
    else:
        _preflight_price_strategy_data(
            tickers=universe_input_tickers,
            start=start,
            end=end,
            timeframe=timeframe,
        )
    if market_regime_enabled:
        _preflight_price_strategy_data(
            tickers=[market_regime_benchmark],
            start=start,
            end=end,
            timeframe=timeframe,
        )
    effective_defensive_tickers = (
        _normalize_tickers(defensive_tickers or STRICT_DEFAULT_DEFENSIVE_TICKERS)
        if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE
        else []
    )
    if effective_defensive_tickers:
        defensive_only = [ticker for ticker in effective_defensive_tickers if ticker not in universe_input_tickers]
        if defensive_only:
            _preflight_price_strategy_data(
                tickers=defensive_only,
                start=start,
                end=end,
                timeframe=timeframe,
            )
    _preflight_statement_quality_shadow_data(
        tickers=universe_input_tickers,
        end=end,
        statement_freq="quarterly",
        factor_names=normalized_factor_names,
    )

    result_payload = get_statement_quality_value_snapshot_shadow_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="quarterly",
        quality_factors=normalized_quality_factors,
        value_factors=normalized_value_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        weighting_mode=weighting_mode,
        rejected_slot_handling_mode=rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=effective_defensive_tickers,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=universe_input_tickers,
        dynamic_target_size=dynamic_target_size,
        pit_membership_snapshots=pit_membership_snapshots,
        pit_universe_code=pit_universe_code,
        return_details=True,
    )
    result_df = result_payload["result_df"]
    universe_debug = result_payload.get("universe_debug")
    dynamic_universe_snapshot_rows = result_payload.get("universe_snapshot_rows") or []
    dynamic_candidate_status_rows = result_payload.get("candidate_status_rows") or []

    warnings = [
        "Research-only quarterly multi-factor prototype: combines quarterly quality and value shadow factors for family-level validation, not public default use.",
    ]
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        warnings.append(_dynamic_universe_warning("quarterly"))
        if dynamic_price_pool and dynamic_price_pool["missing_count"] > 0:
            preview = ", ".join(dynamic_price_pool["missing_symbols"][:15])
            more = ""
            if dynamic_price_pool["missing_count"] > 15:
                more = f" ... (+{dynamic_price_pool['missing_count'] - 15} more)"
            warnings.append(
                "Dynamic candidate pool note: "
                f"{dynamic_price_pool['missing_count']} candidate symbols do not have any DB price history up to the selected end date "
                f"and were naturally excluded from the approximate PIT membership build: {preview}{more}"
            )
    elif universe_contract == PIT_MONTHLY_SNAPSHOT_UNIVERSE:
        warnings.append(_pit_monthly_universe_warning(pit_universe_code))
    if price_freshness["status"] == "warning":
        warnings.append(
            "Price freshness preflight: "
            + price_freshness["message"]
            + " Wider quarterly prototype runs can degrade in the final month until lagging symbols are refreshed."
        )
    if start:
        active_rows = result_df[result_df["Selected Count"].fillna(0) > 0]
        if not active_rows.empty:
            first_active_date = pd.to_datetime(active_rows.iloc[0]["Date"]).strftime("%Y-%m-%d")
            if first_active_date > start:
                warnings.append(
                    "No usable quarterly multi-factor snapshot rows were available at the requested start date. "
                    f"The strategy stayed in cash until `{first_active_date}`."
                )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Quality + Value Snapshot (Strict Quarterly Prototype)",
        strategy_key="quality_value_snapshot_strict_quarterly_prototype",
        input_params={
            "tickers": normalized_tickers,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top_n,
            "rebalance_interval": rebalance_interval,
            "factor_freq": "quarterly",
            "quality_factors": normalized_quality_factors,
            "value_factors": normalized_value_factors,
            "trend_filter_enabled": trend_filter_enabled,
            "trend_filter_window": trend_filter_window,
            "weighting_mode": weighting_mode,
            "rejected_slot_handling_mode": rejected_slot_handling_mode,
            "rejected_slot_fill_enabled": rejected_slot_fill_enabled,
            "partial_cash_retention_enabled": partial_cash_retention_enabled,
            "risk_off_mode": risk_off_mode,
            "defensive_tickers": effective_defensive_tickers,
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "snapshot_mode": "strict_statement_quarterly",
            "snapshot_source": "shadow_factors",
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "universe_contract": universe_contract,
            "dynamic_target_size": dynamic_target_size,
            "dynamic_candidate_count": len(universe_input_tickers),
            "dynamic_candidate_preview": universe_input_tickers[:20],
            "pit_universe_code": pit_universe_code,
            "universe_builder_scope": _strict_universe_builder_scope(
                universe_contract=universe_contract,
                statement_freq="quarterly",
            ),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    _apply_dynamic_runnable_coverage_price_status(
        bundle,
        price_freshness=price_freshness,
        universe_debug=universe_debug,
        result_df=result_df,
    )
    if trend_filter_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            _build_strict_rejected_slot_handling_warning(
                trend_filter_window=trend_filter_window,
                rejected_slot_handling_mode=rejected_slot_handling_mode,
            )
        ]
    if weighting_mode == STRICT_WEIGHTING_MODE_RANK_TAPERED:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Concentration-Aware Weighting enabled: selected holdings use a mild rank taper instead of pure equal weight."
        ]
    if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "Strict quarterly defensive sleeve contract enabled: full risk-off states "
            f"rotate into `{', '.join(effective_defensive_tickers)}` instead of staying fully in cash."
        ]
    if market_regime_enabled:
        regime_warning = (
            f"Market Regime Overlay enabled: month-end selections rotate into `{', '.join(effective_defensive_tickers)}` "
            f"when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
            if risk_off_mode == STRICT_RISK_OFF_MODE_DEFENSIVE and effective_defensive_tickers
            else f"Market Regime Overlay enabled: month-end selections move fully to cash when `{market_regime_benchmark}` closes below `MA{market_regime_window}`."
        )
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [regime_warning]
    if dynamic_universe_snapshot_rows:
        bundle["dynamic_universe_snapshot_rows"] = dynamic_universe_snapshot_rows
    if dynamic_candidate_status_rows:
        bundle["dynamic_candidate_status_rows"] = dynamic_candidate_status_rows
    return bundle


def run_quality_snapshot_strict_quarterly_prototype_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    quality_factors: Sequence[str] | None = None,
    top_n: int = 2,
    rebalance_interval: int = 1,
    trend_filter_enabled: bool = False,
    trend_filter_window: int = 200,
    weighting_mode: str = STRICT_DEFAULT_WEIGHTING_MODE,
    rejected_slot_handling_mode: str | None = None,
    rejected_slot_fill_enabled: bool = STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    partial_cash_retention_enabled: bool = STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    risk_off_mode: str = STRICT_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
    universe_contract: str = STATIC_MANAGED_RESEARCH_UNIVERSE,
    dynamic_candidate_tickers: Sequence[str] | None = None,
    dynamic_target_size: int | None = None,
) -> dict[str, Any]:
    return _run_statement_quality_bundle(
        strategy_name="Quality Snapshot (Strict Quarterly Prototype)",
        strategy_key="quality_snapshot_strict_quarterly_prototype",
        tickers=tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        statement_freq="quarterly",
        quality_factors=quality_factors,
        top_n=top_n,
        rebalance_interval=rebalance_interval,
        trend_filter_enabled=trend_filter_enabled,
        trend_filter_window=trend_filter_window,
        weighting_mode=weighting_mode,
        rejected_slot_handling_mode=rejected_slot_handling_mode,
        rejected_slot_fill_enabled=rejected_slot_fill_enabled,
        partial_cash_retention_enabled=partial_cash_retention_enabled,
        risk_off_mode=risk_off_mode,
        defensive_tickers=defensive_tickers,
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        universe_mode=universe_mode,
        preset_name=preset_name,
        universe_contract=universe_contract,
        dynamic_candidate_tickers=dynamic_candidate_tickers,
        dynamic_target_size=dynamic_target_size,
        snapshot_source="shadow_factors",
        static_warnings=[
            "Research-only quarterly strict prototype: ranks quarterly statement shadow factors and is intended for Phase 6 entry/validation rather than public default use.",
        ],
    )
