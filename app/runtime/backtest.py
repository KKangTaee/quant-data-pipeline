from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from app.runtime.backtest_result_bundle import build_backtest_result_bundle
from app.runtime.backtest_risk_on_momentum import (
    RISK_ON_MOMENTUM_BENCHMARK_TICKERS,
    RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_LIMIT,
    RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_MODE,
    run_risk_on_momentum_5d_backtest_from_db,
)
from app.runtime.backtest_real_money import (
    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    ETF_OPERABILITY_STRATEGY_KEYS,
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    REAL_MONEY_CASH_LABEL,
    STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
    STRICT_BENCHMARK_CONTRACT_TICKER,
    STRICT_DEFAULT_BENCHMARK_CONTRACT,
    STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    _apply_real_money_hardening,
    _apply_transaction_cost_postprocess,
    _build_benchmark_policy_surface,
    _build_benchmark_result_df,
    _build_deployment_readiness_contract,
    _build_etf_operability_policy_surface,
    _build_guardrail_policy_surface,
    _build_liquidity_policy_surface,
    _build_promotion_decision,
    _build_probation_and_monitoring_contract,
    _build_real_money_validation_surface,
    _build_rolling_and_out_of_sample_review_surface,
    _build_shortlist_contract,
    _build_validation_policy_surface,
    _build_weight_map,
    _coerce_float,
    _coerce_list_cell,
    _compute_drawdown_stats,
    _compute_total_return,
    _estimate_turnover_series,
    _missing_turnover_input_columns,
    _normalize_tickers,
    _policy_status_to_check_status,
    _resolve_guardrail_reference_ticker,
    _rolling_validation_window,
    _turnover_diagnostics_from_result,
)
from finance.loaders import (
    load_asset_profile_status_summary,
    load_factor_snapshot,
    load_latest_market_date,
    load_price_freshness_summary,
    load_price_history,
    load_statement_factor_snapshot_shadow,
    load_statement_snapshot_strict,
)
from finance.sample import (
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_SIGNAL_INTERVAL,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    GTAA_DEFAULT_SCORE_WEIGHTS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    HISTORICAL_DYNAMIC_PIT_UNIVERSE,
    STATIC_MANAGED_RESEARCH_UNIVERSE,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_INVESTABILITY_DEFAULT_MIN_AVG_DOLLAR_VOLUME_20D_M,
    STRICT_INVESTABILITY_DEFAULT_MIN_HISTORY_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_DEFAULT_DEFENSIVE_TICKERS,
    STRICT_DEFAULT_REJECTION_HANDLING_MODE,
    STRICT_DEFAULT_RISK_OFF_MODE,
    STRICT_DEFAULT_WEIGHTING_MODE,
    STRICT_REJECTION_HANDLING_MODE_FILL_RETAIN_CASH,
    STRICT_REJECTION_HANDLING_MODE_FILL_REWEIGHT,
    STRICT_REJECTION_HANDLING_MODE_RETAIN_CASH,
    STRICT_REJECTED_SLOT_FILL_DEFAULT_ENABLED,
    STRICT_PARTIAL_CASH_RETENTION_DEFAULT_ENABLED,
    STRICT_RISK_OFF_MODE_DEFENSIVE,
    STRICT_WEIGHTING_MODE_EQUAL,
    STRICT_WEIGHTING_MODE_RANK_TAPERED,
    QUALITY_STRICT_DEFAULT_FACTORS,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    VALUE_STRICT_DEFAULT_FACTORS,
    get_dual_momentum_from_db,
    get_equal_weight_from_db,
    get_global_relative_strength_from_db,
    get_gtaa3_from_db,
    get_quality_snapshot_from_db,
    get_risk_parity_trend_from_db,
    get_statement_quality_snapshot_from_db,
    get_statement_quality_value_snapshot_shadow_from_db,
    get_statement_quality_snapshot_shadow_from_db,
    get_statement_value_snapshot_shadow_from_db,
    resolve_strict_rejection_handling_mode,
    strict_rejection_handling_mode_to_flags,
)


class BacktestInputError(ValueError):
    """Raised when user-facing backtest input is structurally invalid."""


class BacktestDataError(ValueError):
    """Raised when the requested DB-backed backtest cannot find required market data."""


def _resolve_dynamic_etf_promotion_policy_defaults(
    *,
    promotion_min_benchmark_coverage: float | None,
    promotion_min_net_cagr_spread: float | None,
    promotion_min_liquidity_clean_coverage: float | None,
    promotion_max_underperformance_share: float | None,
    promotion_min_worst_rolling_excess_return: float | None,
    promotion_max_strategy_drawdown: float | None,
    promotion_max_drawdown_gap_vs_benchmark: float | None,
) -> dict[str, float]:
    """Attach strict-compatible promotion thresholds to ETF dynamic strategy contracts."""

    return {
        "promotion_min_benchmark_coverage": float(
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE
            if promotion_min_benchmark_coverage is None
            else promotion_min_benchmark_coverage
        ),
        "promotion_min_net_cagr_spread": float(
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD
            if promotion_min_net_cagr_spread is None
            else promotion_min_net_cagr_spread
        ),
        "promotion_min_liquidity_clean_coverage": float(
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE
            if promotion_min_liquidity_clean_coverage is None
            else promotion_min_liquidity_clean_coverage
        ),
        "promotion_max_underperformance_share": float(
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE
            if promotion_max_underperformance_share is None
            else promotion_max_underperformance_share
        ),
        "promotion_min_worst_rolling_excess_return": float(
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN
            if promotion_min_worst_rolling_excess_return is None
            else promotion_min_worst_rolling_excess_return
        ),
        "promotion_max_strategy_drawdown": float(
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN
            if promotion_max_strategy_drawdown is None
            else promotion_max_strategy_drawdown
        ),
        "promotion_max_drawdown_gap_vs_benchmark": float(
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK
            if promotion_max_drawdown_gap_vs_benchmark is None
            else promotion_max_drawdown_gap_vs_benchmark
        ),
    }




def _summary_frequency(option: str, timeframe: str) -> str:
    if option == "month_end":
        return "M"
    if timeframe == "1d":
        return "D"
    return "M"


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
        raise BacktestDataError(
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


def run_equal_weight_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    rebalance_interval: int = 12,
    min_price_filter: float | None = None,
    transaction_cost_bps: float | None = None,
    benchmark_ticker: str | None = None,
    guardrail_reference_ticker: str | None = None,
    promotion_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    promotion_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    promotion_min_benchmark_coverage: float | None = None,
    promotion_min_net_cagr_spread: float | None = None,
    promotion_min_liquidity_clean_coverage: float | None = None,
    promotion_max_underperformance_share: float | None = None,
    promotion_min_worst_rolling_excess_return: float | None = None,
    promotion_max_strategy_drawdown: float | None = None,
    promotion_max_drawdown_gap_vs_benchmark: float | None = None,
    universe_mode: str = "manual_tickers",
    preset_name: str | None = None,
) -> dict[str, Any]:
    """
    Public UI-facing runtime wrapper for static equal-weight ETF baskets with Real-Money diagnostics.
    """
    normalized_tickers = _normalize_tickers(tickers)
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)
    price_freshness = inspect_strict_annual_price_freshness(
        tickers=normalized_tickers,
        end=end,
        timeframe=timeframe,
        context_label="Equal Weight universe",
    )
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if benchmark_ticker and benchmark_ticker not in normalized_tickers:
        _preflight_price_strategy_data(
            tickers=[benchmark_ticker],
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

    warnings: list[str] = []
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 점검에서 주의가 필요합니다. "
            + price_freshness["message"]
            + " 결과 기간이 요청 종료일보다 짧아질 수 있으므로 `Data Trust Summary`와 원본 가격 데이터를 함께 확인하세요."
        )

    bundle = build_backtest_result_bundle(
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
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "guardrail_reference_ticker": guardrail_reference_ticker,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            "promotion_min_benchmark_coverage": promotion_min_benchmark_coverage,
            "promotion_min_net_cagr_spread": promotion_min_net_cagr_spread,
            "promotion_min_liquidity_clean_coverage": promotion_min_liquidity_clean_coverage,
            "promotion_max_underperformance_share": promotion_max_underperformance_share,
            "promotion_min_worst_rolling_excess_return": promotion_min_worst_rolling_excess_return,
            "promotion_max_strategy_drawdown": promotion_max_strategy_drawdown,
            "promotion_max_drawdown_gap_vs_benchmark": promotion_max_drawdown_gap_vs_benchmark,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        guardrail_reference_ticker=guardrail_reference_ticker,
        benchmark_universe_tickers=normalized_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )


def run_gtaa_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = 3,
    interval: int = GTAA_DEFAULT_SIGNAL_INTERVAL,
    min_price_filter: float | None = None,
    transaction_cost_bps: float | None = None,
    benchmark_ticker: str | None = None,
    score_lookback_months: Sequence[int] | None = None,
    score_return_columns: Sequence[str] | None = None,
    score_weights: dict[str, float] | None = None,
    trend_filter_window: int = GTAA_DEFAULT_TREND_FILTER_WINDOW,
    risk_off_mode: str = GTAA_DEFAULT_RISK_OFF_MODE,
    defensive_tickers: Sequence[str] | None = None,
    market_regime_enabled: bool = False,
    market_regime_window: int = STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    market_regime_benchmark: str = STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    crash_guardrail_enabled: bool = GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    crash_guardrail_drawdown_threshold: float = GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    crash_guardrail_lookback_months: int = GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    promotion_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    promotion_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    promotion_min_benchmark_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float | None = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float | None = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float | None = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float | None = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float | None = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    """
    Public UI-facing runtime wrapper for the second DB-backed backtest screen.
    """
    normalized_tickers = _normalize_tickers(tickers)
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if (market_regime_enabled or crash_guardrail_enabled) and market_regime_benchmark:
        benchmark_symbol = str(market_regime_benchmark).strip().upper()
        if benchmark_symbol and benchmark_symbol not in normalized_tickers:
            _preflight_price_strategy_data(
                tickers=[benchmark_symbol],
                start=start,
                end=end,
                timeframe=timeframe,
            )
    if (underperformance_guardrail_enabled or drawdown_guardrail_enabled) and benchmark_ticker:
        guardrail_symbol = str(benchmark_ticker).strip().upper()
        if guardrail_symbol and guardrail_symbol not in normalized_tickers:
            _preflight_price_strategy_data(
                tickers=[guardrail_symbol],
                start=start,
                end=end,
                timeframe=timeframe,
            )

    normalized_score_lookback_months = [
        int(value)
        for value in (
            list(score_lookback_months)
            if score_lookback_months is not None
            else list(GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS)
        )
    ]
    normalized_score_return_columns = [f"{months}MReturn" for months in normalized_score_lookback_months]
    normalized_score_weights = (
        {f"{months}MReturn": 1.0 for months in normalized_score_lookback_months}
        if score_weights is None
        else dict(score_weights)
    )
    promotion_policy = _resolve_dynamic_etf_promotion_policy_defaults(
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )

    result_df = get_gtaa3_from_db(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        interval=interval,
        min_price=min_price_filter,
        score_lookback_months=normalized_score_lookback_months,
        score_return_columns=normalized_score_return_columns,
        score_weights=normalized_score_weights,
        trend_filter_window=trend_filter_window,
        risk_off_mode=risk_off_mode,
        defensive_tickers=list(defensive_tickers or GTAA_DEFAULT_DEFENSIVE_TICKERS),
        market_regime_enabled=market_regime_enabled,
        market_regime_window=market_regime_window,
        market_regime_benchmark=market_regime_benchmark,
        crash_guardrail_enabled=crash_guardrail_enabled,
        crash_guardrail_drawdown_threshold=crash_guardrail_drawdown_threshold,
        crash_guardrail_lookback_months=crash_guardrail_lookback_months,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
    )

    bundle = build_backtest_result_bundle(
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
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            **promotion_policy,
            "score_lookback_months": normalized_score_lookback_months,
            "score_return_columns": normalized_score_return_columns,
            "score_weights": normalized_score_weights,
            "trend_filter_window": trend_filter_window,
            "risk_off_mode": risk_off_mode,
            "defensive_tickers": list(defensive_tickers or GTAA_DEFAULT_DEFENSIVE_TICKERS),
            "market_regime_enabled": market_regime_enabled,
            "market_regime_window": market_regime_window,
            "market_regime_benchmark": market_regime_benchmark,
            "crash_guardrail_enabled": crash_guardrail_enabled,
            "crash_guardrail_drawdown_threshold": crash_guardrail_drawdown_threshold,
            "crash_guardrail_lookback_months": crash_guardrail_lookback_months,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "drawdown_guardrail_enabled": drawdown_guardrail_enabled,
            "drawdown_guardrail_window_months": drawdown_guardrail_window_months,
            "drawdown_guardrail_strategy_threshold": drawdown_guardrail_strategy_threshold,
            "drawdown_guardrail_gap_threshold": drawdown_guardrail_gap_threshold,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )
    bundle = _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=normalized_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        **promotion_policy,
    )
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Underperformance Guardrail enabled: rebalance candidates move to cash when trailing strategy excess return "
            f"vs `{benchmark_ticker}` over `{underperformance_guardrail_window_months}M` falls below "
            f"`{underperformance_guardrail_threshold:.0%}`."
        ]
    if drawdown_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Drawdown Guardrail enabled: rebalance candidates move to cash when trailing strategy drawdown over "
            f"`{drawdown_guardrail_window_months}M` falls below `{drawdown_guardrail_strategy_threshold:.0%}` "
            f"or drawdown gap vs `{benchmark_ticker}` rises above `{drawdown_guardrail_gap_threshold:.0%}`."
        ]
    return bundle


def run_global_relative_strength_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    cash_ticker: str | None = GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    interval: int = GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    min_price_filter: float | None = None,
    transaction_cost_bps: float | None = None,
    benchmark_ticker: str | None = None,
    score_lookback_months: Sequence[int] | None = None,
    score_return_columns: Sequence[str] | None = None,
    score_weights: dict[str, float] | None = None,
    trend_filter_window: int = GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    promotion_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    promotion_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    promotion_min_benchmark_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float | None = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float | None = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float | None = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float | None = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float | None = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers or GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS)
    normalized_cash_ticker = str(cash_ticker or "").strip().upper() or None
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)

    preflight_tickers = list(normalized_tickers)
    if normalized_cash_ticker and normalized_cash_ticker not in preflight_tickers:
        preflight_tickers.append(normalized_cash_ticker)
    price_freshness = inspect_strict_annual_price_freshness(
        tickers=preflight_tickers,
        end=end,
        timeframe=timeframe,
        context_label="Global Relative Strength universe",
    )
    _preflight_price_strategy_data(
        tickers=preflight_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if benchmark_ticker and benchmark_ticker not in preflight_tickers:
        _preflight_price_strategy_data(
            tickers=[benchmark_ticker],
            start=start,
            end=end,
            timeframe=timeframe,
        )

    normalized_score_lookback_months = [
        int(value)
        for value in (
            list(score_lookback_months)
            if score_lookback_months is not None
            else list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_SCORE_LOOKBACK_MONTHS)
        )
    ]
    normalized_score_return_columns = [f"{months}MReturn" for months in normalized_score_lookback_months]
    normalized_score_weights = (
        {f"{months}MReturn": 1.0 for months in normalized_score_lookback_months}
        if score_weights is None
        else dict(score_weights)
    )
    promotion_policy = _resolve_dynamic_etf_promotion_policy_defaults(
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )

    result_df = get_global_relative_strength_from_db(
        tickers=normalized_tickers,
        cash_ticker=normalized_cash_ticker,
        start=start,
        end=end,
        timeframe=timeframe,
        option=option,
        top=top,
        interval=interval,
        min_price=min_price_filter,
        score_lookback_months=normalized_score_lookback_months,
        score_return_columns=normalized_score_return_columns,
        score_weights=normalized_score_weights,
        trend_filter_window=trend_filter_window,
    )
    effective_tickers = _normalize_tickers(result_df.attrs.get("effective_tickers") or normalized_tickers)
    requested_tickers = _normalize_tickers(result_df.attrs.get("requested_tickers") or normalized_tickers)
    excluded_tickers_raw = result_df.attrs.get("excluded_tickers") or []
    excluded_tickers = _normalize_tickers(excluded_tickers_raw) if excluded_tickers_raw else []
    malformed_price_rows = list(result_df.attrs.get("malformed_price_rows") or [])
    warnings: list[str] = []
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 점검에서 주의가 필요합니다. "
            + price_freshness["message"]
            + " 결과 기간이 요청 종료일보다 짧아질 수 있으므로 `Data Trust Summary`와 원본 가격 데이터를 함께 확인하세요."
        )
    if excluded_tickers:
        warnings.append(
            "Global Relative Strength 실행에서 이동평균/상대강도 계산에 필요한 가격 이력이 부족한 티커를 제외했습니다: "
            + ", ".join(excluded_tickers)
            + ". 결과를 해석하기 전에 해당 티커의 DB 가격 데이터를 보강하거나 universe에서 제외하는 것이 좋습니다."
        )
    if malformed_price_rows:
        malformed_preview = []
        for row in malformed_price_rows[:5]:
            ticker = str(row.get("ticker") or "").strip().upper()
            count = int(row.get("count") or 0)
            sample_dates = row.get("sample_dates") or []
            sample_text = ", ".join(str(value) for value in sample_dates[:3])
            malformed_preview.append(f"{ticker} {count}건({sample_text})")
        more = ""
        if len(malformed_price_rows) > 5:
            more = f" 외 {len(malformed_price_rows) - 5}개 티커"
        warnings.append(
            "가격 데이터에 결측 행이 있어 공통 리밸런싱 날짜가 보수적으로 줄어들 수 있습니다: "
            + "; ".join(malformed_preview)
            + more
            + ". 값을 임의로 채우거나 보정하지 않았으므로, 원본 DB 가격 데이터를 점검하거나 재수집하는 것이 좋습니다."
        )

    bundle = build_backtest_result_bundle(
        result_df,
        strategy_name="Global Relative Strength",
        strategy_key="global_relative_strength",
        input_params={
            "tickers": effective_tickers,
            "requested_tickers": requested_tickers,
            "excluded_tickers": excluded_tickers,
            "malformed_price_rows": malformed_price_rows,
            "cash_ticker": normalized_cash_ticker,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "option": option,
            "top": top,
            "rebalance_interval": interval,
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            **promotion_policy,
            "score_lookback_months": normalized_score_lookback_months,
            "score_return_columns": normalized_score_return_columns,
            "score_weights": normalized_score_weights,
            "trend_filter_enabled": True,
            "trend_filter_window": trend_filter_window,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
            "research_source": "/Users/taeho/Project/quant-research/.note/research/strategies/2026-04-15-global-relative-strength-allocation-with-trend-safety-net.md",
        },
        summary_freq=_summary_frequency(option, timeframe),
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
    return _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=effective_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        **promotion_policy,
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
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    promotion_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    promotion_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    promotion_min_benchmark_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float | None = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float | None = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float | None = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float | None = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float | None = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)
    promotion_policy = _resolve_dynamic_etf_promotion_policy_defaults(
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if (underperformance_guardrail_enabled or drawdown_guardrail_enabled) and benchmark_ticker:
        guardrail_symbol = str(benchmark_ticker).strip().upper()
        if guardrail_symbol and guardrail_symbol not in normalized_tickers:
            _preflight_price_strategy_data(
                tickers=[guardrail_symbol],
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
        min_price=min_price_filter,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
    )

    bundle = build_backtest_result_bundle(
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
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "drawdown_guardrail_enabled": drawdown_guardrail_enabled,
            "drawdown_guardrail_window_months": drawdown_guardrail_window_months,
            "drawdown_guardrail_strategy_threshold": drawdown_guardrail_strategy_threshold,
            "drawdown_guardrail_gap_threshold": drawdown_guardrail_gap_threshold,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            **promotion_policy,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )
    bundle = _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=normalized_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        **promotion_policy,
    )
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Underperformance Guardrail enabled: rebalance candidates move to cash when trailing strategy excess return "
            f"vs `{benchmark_ticker}` over `{underperformance_guardrail_window_months}M` falls below "
            f"`{underperformance_guardrail_threshold:.0%}`."
        ]
    if drawdown_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Drawdown Guardrail enabled: rebalance candidates move to cash when trailing strategy drawdown over "
            f"`{drawdown_guardrail_window_months}M` falls below `{drawdown_guardrail_strategy_threshold:.0%}` "
            f"or drawdown gap vs `{benchmark_ticker}` rises above `{drawdown_guardrail_gap_threshold:.0%}`."
        ]
    return bundle


def run_dual_momentum_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "month_end",
    top: int = 1,
    rebalance_interval: int = 1,
    min_price_filter: float = ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    transaction_cost_bps: float = ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    benchmark_ticker: str = ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    underperformance_guardrail_enabled: bool = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    underperformance_guardrail_window_months: int = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    underperformance_guardrail_threshold: float = STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    drawdown_guardrail_enabled: bool = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    drawdown_guardrail_window_months: int = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    drawdown_guardrail_strategy_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    drawdown_guardrail_gap_threshold: float = STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    promotion_min_etf_aum_b: float = ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    promotion_max_bid_ask_spread_pct: float = ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    promotion_min_benchmark_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
    promotion_min_net_cagr_spread: float | None = STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
    promotion_min_liquidity_clean_coverage: float | None = STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
    promotion_max_underperformance_share: float | None = STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
    promotion_min_worst_rolling_excess_return: float | None = STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
    promotion_max_strategy_drawdown: float | None = STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
    promotion_max_drawdown_gap_vs_benchmark: float | None = STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
    universe_mode: str = "preset",
    preset_name: str | None = None,
) -> dict[str, Any]:
    normalized_tickers = _normalize_tickers(tickers)
    benchmark_ticker = str(benchmark_ticker or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper()
    _validate_backtest_date_range(start, end)
    promotion_policy = _resolve_dynamic_etf_promotion_policy_defaults(
        promotion_min_benchmark_coverage=promotion_min_benchmark_coverage,
        promotion_min_net_cagr_spread=promotion_min_net_cagr_spread,
        promotion_min_liquidity_clean_coverage=promotion_min_liquidity_clean_coverage,
        promotion_max_underperformance_share=promotion_max_underperformance_share,
        promotion_min_worst_rolling_excess_return=promotion_min_worst_rolling_excess_return,
        promotion_max_strategy_drawdown=promotion_max_strategy_drawdown,
        promotion_max_drawdown_gap_vs_benchmark=promotion_max_drawdown_gap_vs_benchmark,
    )
    _preflight_price_strategy_data(
        tickers=normalized_tickers,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if (underperformance_guardrail_enabled or drawdown_guardrail_enabled) and benchmark_ticker:
        guardrail_symbol = str(benchmark_ticker).strip().upper()
        if guardrail_symbol and guardrail_symbol not in normalized_tickers:
            _preflight_price_strategy_data(
                tickers=[guardrail_symbol],
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
        min_price=min_price_filter,
        benchmark_ticker=benchmark_ticker,
        underperformance_guardrail_enabled=underperformance_guardrail_enabled,
        underperformance_guardrail_window_months=underperformance_guardrail_window_months,
        underperformance_guardrail_threshold=underperformance_guardrail_threshold,
        drawdown_guardrail_enabled=drawdown_guardrail_enabled,
        drawdown_guardrail_window_months=drawdown_guardrail_window_months,
        drawdown_guardrail_strategy_threshold=drawdown_guardrail_strategy_threshold,
        drawdown_guardrail_gap_threshold=drawdown_guardrail_gap_threshold,
    )

    bundle = build_backtest_result_bundle(
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
            "min_price_filter": min_price_filter,
            "transaction_cost_bps": transaction_cost_bps,
            "benchmark_ticker": benchmark_ticker,
            "underperformance_guardrail_enabled": underperformance_guardrail_enabled,
            "underperformance_guardrail_window_months": underperformance_guardrail_window_months,
            "underperformance_guardrail_threshold": underperformance_guardrail_threshold,
            "drawdown_guardrail_enabled": drawdown_guardrail_enabled,
            "drawdown_guardrail_window_months": drawdown_guardrail_window_months,
            "drawdown_guardrail_strategy_threshold": drawdown_guardrail_strategy_threshold,
            "drawdown_guardrail_gap_threshold": drawdown_guardrail_gap_threshold,
            "promotion_min_etf_aum_b": promotion_min_etf_aum_b,
            "promotion_max_bid_ask_spread_pct": promotion_max_bid_ask_spread_pct,
            **promotion_policy,
            "universe_mode": universe_mode,
            "preset_name": preset_name,
        },
        summary_freq=_summary_frequency(option, timeframe),
    )
    bundle = _apply_real_money_hardening(
        bundle,
        summary_freq=_summary_frequency(option, timeframe),
        min_price_filter=min_price_filter,
        transaction_cost_bps=transaction_cost_bps,
        benchmark_contract=STRICT_DEFAULT_BENCHMARK_CONTRACT,
        benchmark_ticker=benchmark_ticker,
        benchmark_universe_tickers=normalized_tickers,
        promotion_min_etf_aum_b=promotion_min_etf_aum_b,
        promotion_max_bid_ask_spread_pct=promotion_max_bid_ask_spread_pct,
        **promotion_policy,
    )
    if underperformance_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Underperformance Guardrail enabled: rebalance candidates move to cash when trailing strategy excess return "
            f"vs `{benchmark_ticker}` over `{underperformance_guardrail_window_months}M` falls below "
            f"`{underperformance_guardrail_threshold:.0%}`."
        ]
    if drawdown_guardrail_enabled:
        bundle["meta"]["warnings"] = list(bundle["meta"].get("warnings") or []) + [
            "ETF Drawdown Guardrail enabled: rebalance candidates move to cash when trailing strategy drawdown over "
            f"`{drawdown_guardrail_window_months}M` falls below `{drawdown_guardrail_strategy_threshold:.0%}` "
            f"or drawdown gap vs `{benchmark_ticker}` rises above `{drawdown_guardrail_gap_threshold:.0%}`."
        ]
    return bundle


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
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_factors = [
        str(name).strip()
        for name in (quality_factors or QUALITY_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one quality factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
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
        "universe_builder_scope": (
            f"{statement_freq}_first_pass"
            if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE
            else None
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
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
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
            "universe_builder_scope": ("annual_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
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
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

    normalized_factors = [
        str(name).strip()
        for name in (value_factors or VALUE_STRICT_DEFAULT_FACTORS)
        if str(name).strip()
    ]
    if not normalized_factors:
        raise BacktestInputError("At least one quarterly value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
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
            "universe_builder_scope": ("quarterly_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
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
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

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
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
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
            "universe_builder_scope": ("annual_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
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
    universe_input_tickers = normalized_tickers
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
        universe_input_tickers = _normalize_tickers(dynamic_candidate_tickers or normalized_tickers)

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
        raise BacktestInputError("At least one quarterly quality/value factor must be provided.")

    price_freshness = inspect_strict_annual_price_freshness(
        tickers=universe_input_tickers,
        end=end,
        timeframe=timeframe,
    )

    dynamic_price_pool = None
    if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE:
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
            "universe_builder_scope": ("quarterly_first_pass" if universe_contract == HISTORICAL_DYNAMIC_PIT_UNIVERSE else None),
            "universe_debug": universe_debug,
        },
        summary_freq=_summary_frequency(option, timeframe),
        data_mode="db_backed_strict_statement_shadow_factors",
        warnings=warnings,
    )
    bundle["meta"]["price_freshness"] = price_freshness
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
