from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from app.runtime.backtest_result_bundle import build_backtest_result_bundle
from app.workspace_paths import BACKTEST_ARTIFACT_DIR
from finance.data.asset_profile import load_top_symbols_from_asset_profile
from finance.data.market_intelligence import load_market_cap_universe_members
from finance.loaders import load_futures_ohlcv, load_price_history, load_statement_fundamentals_shadow
from finance.performance import portfolio_performance_summary
from finance.swing import (
    DEFAULT_SWING_FUTURES_SYMBOLS,
    RISK_ON_MOMENTUM_STRATEGY_KEY,
    RISK_ON_MOMENTUM_STRATEGY_NAME,
    RiskOnMomentumConfig,
    build_buy_and_hold_result,
    build_futures_macro_mean_z_scores,
    clone_config,
    prepare_swing_feature_frame,
    run_risk_on_momentum_backtest,
)
from finance.swing_analysis import (
    build_quality_warnings,
    build_swing_comparison_suite,
    build_swing_sensitivity_suite,
    build_swing_stability_tables,
    build_trade_cause_summary,
)


RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_MODE = "top1000"
RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_LIMIT = 1000
RISK_ON_MOMENTUM_BENCHMARK_TICKERS = ("SPY", "QQQ")


def _normalize_optional_symbols(tickers: Sequence[str] | None) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in tickers or []:
        symbol = str(raw).strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)
    return normalized


def _resolve_risk_on_momentum_universe(
    *,
    tickers: Sequence[str] | None,
    universe_mode: str,
    preset_name: str | None,
    universe_limit: int | None,
) -> tuple[list[str], str, str | None, int | None, str]:
    from app.runtime.backtest.common import BacktestDataError, BacktestInputError

    raw_mode = str(universe_mode or RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_MODE).strip().lower()
    if raw_mode in {"manual", "manual_tickers"}:
        manual = _normalize_optional_symbols(tickers)
        if not manual:
            raise BacktestInputError("Manual Risk-On Momentum universe requires at least one ticker.")
        return manual, "manual_tickers", None, len(manual), "manual_tickers"

    if raw_mode in {"sp500", "snp500", "s&p500", "s&p_500", "s_p_500", "s-and-p-500"}:
        normalized_limit = 500
        universe_code = "SP500"
        normalized_mode = "sp500"
        normalized_preset = preset_name or "S&P 500"
    elif raw_mode in {"top2000", "top_2000"}:
        normalized_limit = int(universe_limit or 2000)
        universe_code = "TOP2000"
        normalized_mode = "top2000"
        normalized_preset = preset_name or "Top2000"
    else:
        normalized_limit = int(universe_limit or RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_LIMIT)
        universe_code = "TOP1000"
        normalized_mode = "top1000"
        normalized_preset = preset_name or "Top1000"

    rows: list[dict[str, Any]] = []
    try:
        rows = load_market_cap_universe_members(universe_code, universe_limit=normalized_limit)
    except Exception:
        rows = []

    symbols = [
        str(row.get("symbol") or "").strip().upper()
        for row in rows
        if str(row.get("symbol") or "").strip()
    ]
    source = f"market_cap_universe_members:{universe_code}"
    if universe_code == "SP500" and not symbols:
        raise BacktestDataError(
            "No S&P 500 universe rows were found for Risk-On Momentum. "
            "Refresh the S&P 500 universe membership first."
        )
    if not symbols:
        symbols = [
            str(symbol).strip().upper()
            for symbol in load_top_symbols_from_asset_profile(
                "stock",
                country="United States",
                on_filter=True,
                limit=normalized_limit,
                order_by="market_cap_desc",
            )
            if str(symbol).strip()
        ]
        source = "nyse_asset_profile.market_cap_fallback"

    if not symbols:
        raise BacktestDataError(
            "No symbols were found for the requested Risk-On Momentum managed universe. "
            "Refresh asset_profile / market-cap universe data first."
        )
    return symbols, normalized_mode, normalized_preset, normalized_limit, source


def _date_minus_days(value: str | None, days: int) -> str | None:
    if value is None:
        return None
    return (pd.to_datetime(value).normalize() - pd.DateOffset(days=int(days))).strftime("%Y-%m-%d")


def _dataframe_records(df: pd.DataFrame | None) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    return json.loads(df.to_json(orient="records", date_format="iso"))


def _performance_summary_row(label: str, result_df: pd.DataFrame) -> dict[str, Any]:
    if result_df is None or result_df.empty:
        return {
            "label": label,
            "rows": 0,
            "end_balance": np.nan,
            "cagr": np.nan,
            "sharpe_ratio": np.nan,
            "maximum_drawdown": np.nan,
            "cumulative_return": np.nan,
        }
    summary = portfolio_performance_summary(result_df, name=label, freq="D").iloc[0]
    start_balance = float(summary.get("Start Balance") or np.nan)
    end_balance = float(summary.get("End Balance") or np.nan)
    return {
        "label": label,
        "rows": int(len(result_df)),
        "start_date": summary.get("Start Date"),
        "end_date": summary.get("End Date"),
        "start_balance": start_balance,
        "end_balance": end_balance,
        "cagr": float(summary.get("CAGR")),
        "sharpe_ratio": float(summary.get("Sharpe Ratio")),
        "maximum_drawdown": float(summary.get("Maximum Drawdown")),
        "cumulative_return": float(end_balance / start_balance - 1.0) if start_balance else np.nan,
    }


def _write_risk_on_momentum_artifact(
    *,
    primary_result: Any,
    macro_off_result: Any | None,
    random_summary_df: pd.DataFrame,
    benchmark_comparison_df: pd.DataFrame,
    v2_analysis: dict[str, Any] | None,
    config: RiskOnMomentumConfig,
    meta: dict[str, Any],
) -> dict[str, Any]:
    BACKTEST_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    base_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{RISK_ON_MOMENTUM_STRATEGY_KEY}_run"
    artifact_dir = BACKTEST_ARTIFACT_DIR / base_name
    counter = 2
    while artifact_dir.exists():
        artifact_dir = BACKTEST_ARTIFACT_DIR / f"{base_name}_{counter}"
        counter += 1
    artifact_dir.mkdir(parents=True, exist_ok=False)

    payload = {
        "strategy_key": RISK_ON_MOMENTUM_STRATEGY_KEY,
        "strategy_name": RISK_ON_MOMENTUM_STRATEGY_NAME,
        "meta": meta,
        "config": dict(config.__dict__),
        "metrics": primary_result.metrics,
        "trade_log": _dataframe_records(primary_result.trade_log_df),
        "scanner": _dataframe_records(primary_result.scanner_df),
        "monthly_returns": _dataframe_records(primary_result.monthly_returns_df),
        "yearly_returns": _dataframe_records(primary_result.yearly_returns_df),
        "ticker_contribution": _dataframe_records(primary_result.ticker_contribution_df),
        "benchmark_comparison": _dataframe_records(benchmark_comparison_df),
        "random_summary": _dataframe_records(random_summary_df),
        "macro_off_metrics": macro_off_result.metrics if macro_off_result is not None else {},
        "macro_off_result": _dataframe_records(macro_off_result.result_df if macro_off_result is not None else None),
        "v2_analysis": {
            key: _dataframe_records(value) if isinstance(value, pd.DataFrame) else value
            for key, value in dict(v2_analysis or {}).items()
        },
    }
    artifact_path = artifact_dir / "risk_on_momentum_5d_run.json"
    artifact_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    return {
        "artifact_dir": str(artifact_dir),
        "run_json": str(artifact_path),
        "trade_row_count": int(len(primary_result.trade_log_df)),
        "scanner_row_count": int(len(primary_result.scanner_df)),
        "random_iteration_count": int(len(random_summary_df)),
    }


def run_risk_on_momentum_5d_backtest_from_db(
    *,
    tickers: Sequence[str] | None = None,
    start: str | None = "2021-06-01",
    end: str | None = None,
    timeframe: str = "1d",
    option: str = "close_based",
    universe_mode: str = RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_MODE,
    preset_name: str | None = "Top1000",
    universe_limit: int | None = RISK_ON_MOMENTUM_DEFAULT_UNIVERSE_LIMIT,
    start_balance: float = 10_000.0,
    execution_mode: str = "close_based",
    exit_mode: str = "fixed_pct",
    max_holding_days: int = 5,
    stop_loss_pct: float = -2.5,
    take_profit_pct: float = 5.0,
    atr_period: int = 14,
    stop_atr_multiple: float = 1.0,
    take_profit_atr_multiple: float = 2.0,
    max_new_positions_per_day: int = 3,
    max_total_positions: int = 3,
    transaction_cost_bps: float = 0.0,
    slippage_bps: float = 0.0,
    macro_filter_enabled: bool = True,
    macro_filter_mode: str = "hard_filter",
    risk_on_min: float = 0.0,
    rate_pressure_max: float = 1.0,
    dollar_pressure_max: float = 1.0,
    safe_haven_max: float = 1.0,
    rate_pressure_penalty_weight: float = 10.0,
    dollar_pressure_penalty_weight: float = 10.0,
    safe_haven_penalty_weight: float = 10.0,
    min_price: float = 5.0,
    min_avg_dollar_volume_20d: float = 20_000_000.0,
    min_avg_volume_20d: float = 500_000.0,
    random_iterations: int = 50,
    random_seed: int = 42,
    scanner_top_n_per_day: int = 50,
    run_comparison_suite: bool = True,
    run_sensitivity_suite: bool = False,
) -> dict[str, Any]:
    from app.runtime.backtest import inspect_strict_annual_price_freshness
    from app.runtime.backtest.common import BacktestDataError
    from app.runtime.backtest.common import validate_backtest_date_range as _validate_backtest_date_range

    _validate_backtest_date_range(start, end)
    resolved_tickers, resolved_mode, resolved_preset, resolved_limit, universe_source = _resolve_risk_on_momentum_universe(
        tickers=tickers,
        universe_mode=universe_mode,
        preset_name=preset_name,
        universe_limit=universe_limit,
    )

    warnings: list[str] = []
    price_freshness = inspect_strict_annual_price_freshness(
        tickers=resolved_tickers,
        end=end,
        timeframe=timeframe,
        context_label=f"{RISK_ON_MOMENTUM_STRATEGY_NAME} universe",
    )
    if price_freshness["status"] == "warning":
        warnings.append(
            "가격 최신성 점검에서 주의가 필요합니다. "
            + price_freshness["message"]
            + " swing scanner가 최신 가격 공백이 있는 종목을 사실상 제외할 수 있습니다."
        )
    elif price_freshness["status"] == "error":
        raise BacktestDataError(price_freshness["message"])

    price_history = load_price_history(
        symbols=sorted(set(resolved_tickers).union(RISK_ON_MOMENTUM_BENCHMARK_TICKERS)),
        start=_date_minus_days(start, 180),
        end=end,
        timeframe=timeframe,
    )
    if price_history.empty:
        raise BacktestDataError(
            "No OHLCV rows were found for the Risk-On Momentum universe. "
            "Run price ingestion for the selected universe first."
        )

    price_history["symbol"] = price_history["symbol"].astype(str).str.upper()
    available_symbols = set(price_history["symbol"].unique().tolist())
    missing_price_symbols = [symbol for symbol in resolved_tickers if symbol not in available_symbols]
    if missing_price_symbols:
        warnings.append(
            "Some universe symbols had no DB price rows and were excluded from scanning: "
            + ", ".join(missing_price_symbols[:20])
            + (f" 외 {len(missing_price_symbols) - 20}개" if len(missing_price_symbols) > 20 else "")
        )

    candidate_price_history = price_history[price_history["symbol"].isin(resolved_tickers)].copy()
    if candidate_price_history.empty:
        raise BacktestDataError("No candidate universe symbols had usable DB OHLCV rows.")

    statement_history = load_statement_fundamentals_shadow(
        symbols=resolved_tickers,
        freq="annual",
        end=end,
    )
    if statement_history.empty:
        warnings.append(
            "No statement shadow fundamentals were available; financial risk filter will block candidate entries."
        )

    futures_history = load_futures_ohlcv(
        symbols=DEFAULT_SWING_FUTURES_SYMBOLS,
        start=_date_minus_days(start, 180),
        end=end,
        interval_code="1d",
    )
    macro_scores = build_futures_macro_mean_z_scores(futures_history)
    if macro_filter_enabled and macro_scores.empty:
        warnings.append(
            "Futures macro Mean-Z rows were unavailable; hard macro filter will block new entries."
        )

    config = RiskOnMomentumConfig(
        start=start,
        end=end,
        start_balance=float(start_balance),
        execution_mode=execution_mode,
        exit_mode=exit_mode,
        max_holding_days=int(max_holding_days),
        stop_loss_pct=float(stop_loss_pct),
        take_profit_pct=float(take_profit_pct),
        atr_period=int(atr_period),
        stop_atr_multiple=float(stop_atr_multiple),
        take_profit_atr_multiple=float(take_profit_atr_multiple),
        max_new_positions_per_day=int(max_new_positions_per_day),
        max_total_positions=int(max_total_positions),
        transaction_cost_bps=float(transaction_cost_bps),
        slippage_bps=float(slippage_bps),
        macro_filter_enabled=bool(macro_filter_enabled),
        macro_filter_mode=macro_filter_mode,
        risk_on_min=float(risk_on_min),
        rate_pressure_max=float(rate_pressure_max),
        dollar_pressure_max=float(dollar_pressure_max),
        safe_haven_max=float(safe_haven_max),
        rate_pressure_penalty_weight=float(rate_pressure_penalty_weight),
        dollar_pressure_penalty_weight=float(dollar_pressure_penalty_weight),
        safe_haven_penalty_weight=float(safe_haven_penalty_weight),
        min_price=float(min_price),
        min_avg_dollar_volume_20d=float(min_avg_dollar_volume_20d),
        min_avg_volume_20d=float(min_avg_volume_20d),
        scanner_top_n_per_day=int(scanner_top_n_per_day),
        random_seed=int(random_seed),
    )
    prepared_features = prepare_swing_feature_frame(
        candidate_price_history,
        statement_history=statement_history,
    )
    primary = run_risk_on_momentum_backtest(
        candidate_price_history,
        config=config,
        macro_scores=macro_scores,
        statement_history=statement_history,
        prepared_features=prepared_features,
    )

    macro_off_result = run_risk_on_momentum_backtest(
        candidate_price_history,
        config=clone_config(
            config,
            macro_filter_enabled=False,
            macro_filter_mode="off",
            collect_scanner_rows=False,
        ),
        macro_scores=macro_scores,
        statement_history=statement_history,
        prepared_features=prepared_features,
    )

    random_rows: list[dict[str, Any]] = []
    for iteration in range(max(0, int(random_iterations))):
        random_result = run_risk_on_momentum_backtest(
            candidate_price_history,
            config=clone_config(
                config,
                ranking_mode="random",
                random_seed=int(random_seed) + iteration + 1,
                collect_scanner_rows=False,
            ),
            macro_scores=macro_scores,
            statement_history=statement_history,
            prepared_features=prepared_features,
        )
        random_rows.append(
            {
                "iteration": iteration + 1,
                **random_result.metrics,
            }
        )
    random_summary_df = pd.DataFrame(random_rows)

    comparison_rows = [
        {
            "label": RISK_ON_MOMENTUM_STRATEGY_NAME,
            "rows": int(len(primary.result_df)),
            **primary.metrics,
        },
        {
            "label": f"{RISK_ON_MOMENTUM_STRATEGY_NAME} (Macro Off)",
            "rows": int(len(macro_off_result.result_df)),
            **macro_off_result.metrics,
        },
    ]
    for benchmark_ticker in RISK_ON_MOMENTUM_BENCHMARK_TICKERS:
        benchmark_df = build_buy_and_hold_result(
            price_history,
            symbol=benchmark_ticker,
            start=start,
            end=end,
            start_balance=float(start_balance),
        )
        comparison_rows.append(_performance_summary_row(f"{benchmark_ticker} Buy & Hold", benchmark_df))
    if not random_summary_df.empty:
        comparison_rows.append(
            {
                "label": "Random Ranking Median",
                "rows": int(len(random_summary_df)),
                "total_trades": float(random_summary_df["total_trades"].median()),
                "win_rate": float(random_summary_df["win_rate"].median()),
                "cagr": float(random_summary_df["cagr"].median()),
                "mdd": float(random_summary_df["mdd"].median()),
                "sharpe_ratio": float(random_summary_df["sharpe_ratio"].median()),
                "cumulative_return": float(random_summary_df["cumulative_return"].median()),
            }
        )
    benchmark_comparison_df = pd.DataFrame(comparison_rows)

    v2_analysis: dict[str, Any] = {}
    if bool(run_comparison_suite):
        v2_analysis.update(
            build_swing_comparison_suite(
                candidate_price_history,
                config=config,
                primary_result=primary,
                macro_scores=macro_scores,
                statement_history=statement_history,
                prepared_features=prepared_features,
            )
        )
    sensitivity_df = pd.DataFrame()
    if bool(run_sensitivity_suite):
        sensitivity_df = build_swing_sensitivity_suite(
            candidate_price_history,
            config=config,
            macro_scores=macro_scores,
            statement_history=statement_history,
            prepared_features=prepared_features,
        )
        v2_analysis["sensitivity_df"] = sensitivity_df
    v2_analysis.update(build_swing_stability_tables(primary))
    v2_analysis["trade_cause_summary_df"] = build_trade_cause_summary(primary.trade_log_df)
    v2_analysis["quality_warning_df"] = build_quality_warnings(
        result=primary,
        random_summary_df=random_summary_df,
        benchmark_comparison_df=benchmark_comparison_df,
        sensitivity_df=sensitivity_df,
        price_freshness=price_freshness,
        macro_scores=macro_scores,
        macro_filter_enabled=bool(macro_filter_enabled),
    )

    meta_input = {
        "tickers": resolved_tickers[:50],
        "start": start,
        "end": end,
        "timeframe": timeframe,
        "option": option,
        "universe_mode": resolved_mode,
        "preset_name": resolved_preset,
        "transaction_cost_bps": float(transaction_cost_bps),
        "min_price_filter": float(min_price),
        "requested_tickers": resolved_tickers[:50],
        "excluded_tickers": missing_price_symbols[:100],
    }
    all_warnings = warnings + primary.warnings
    bundle = build_backtest_result_bundle(
        primary.result_df,
        strategy_name=RISK_ON_MOMENTUM_STRATEGY_NAME,
        strategy_key=RISK_ON_MOMENTUM_STRATEGY_KEY,
        input_params=meta_input,
        summary_freq="D",
        warnings=all_warnings,
    )
    bundle["swing_trade_log_df"] = primary.trade_log_df
    bundle["swing_scanner_df"] = primary.scanner_df
    bundle["swing_metrics"] = primary.metrics
    bundle["swing_monthly_returns_df"] = primary.monthly_returns_df
    bundle["swing_yearly_returns_df"] = primary.yearly_returns_df
    bundle["swing_ticker_contribution_df"] = primary.ticker_contribution_df
    bundle["swing_random_summary_df"] = random_summary_df
    bundle["swing_benchmark_comparison_df"] = benchmark_comparison_df
    bundle["swing_macro_off_result_df"] = macro_off_result.result_df
    for key, value in v2_analysis.items():
        bundle[f"swing_{key}"] = value

    bundle["meta"].update(
        {
            "price_freshness": price_freshness,
            "strategy_execution_mode": config.execution_mode,
            "exit_mode": config.exit_mode,
            "position_sizing": "equal_slot",
            "start_balance": float(start_balance),
            "max_holding_days": int(max_holding_days),
            "stop_loss_pct": float(stop_loss_pct),
            "take_profit_pct": float(take_profit_pct),
            "atr_period": int(atr_period),
            "stop_atr_multiple": float(stop_atr_multiple),
            "take_profit_atr_multiple": float(take_profit_atr_multiple),
            "max_new_positions_per_day": int(max_new_positions_per_day),
            "max_total_positions": int(max_total_positions),
            "slippage_bps": float(slippage_bps),
            "macro_filter_enabled": bool(macro_filter_enabled),
            "macro_filter_mode": macro_filter_mode,
            "risk_on_min": float(risk_on_min),
            "rate_pressure_max": float(rate_pressure_max),
            "dollar_pressure_max": float(dollar_pressure_max),
            "safe_haven_max": float(safe_haven_max),
            "rate_pressure_penalty_weight": float(rate_pressure_penalty_weight),
            "dollar_pressure_penalty_weight": float(dollar_pressure_penalty_weight),
            "safe_haven_penalty_weight": float(safe_haven_penalty_weight),
            "min_avg_dollar_volume_20d": float(min_avg_dollar_volume_20d),
            "min_avg_volume_20d": float(min_avg_volume_20d),
            "random_iterations": int(random_iterations),
            "scanner_top_n_per_day": int(scanner_top_n_per_day),
            "run_comparison_suite": bool(run_comparison_suite),
            "run_sensitivity_suite": bool(run_sensitivity_suite),
            "v2_analysis_keys": sorted(v2_analysis),
            "universe_limit": resolved_limit,
            "universe_symbol_count": len(resolved_tickers),
            "universe_symbol_preview": resolved_tickers[:25],
            "universe_source": universe_source,
            "candidate_price_symbol_count": int(candidate_price_history["symbol"].nunique()),
            "statement_symbol_count": int(statement_history["symbol"].nunique()) if not statement_history.empty else 0,
            "futures_macro_symbol_count": int(futures_history["provider_symbol"].nunique()) if not futures_history.empty else 0,
            "macro_score_rows": int(len(macro_scores)),
            "benchmark_tickers": list(RISK_ON_MOMENTUM_BENCHMARK_TICKERS),
        }
    )
    artifact = _write_risk_on_momentum_artifact(
        primary_result=primary,
        macro_off_result=macro_off_result,
        random_summary_df=random_summary_df,
        benchmark_comparison_df=benchmark_comparison_df,
        v2_analysis=v2_analysis,
        config=config,
        meta=bundle["meta"],
    )
    bundle["swing_artifact"] = artifact
    bundle["meta"]["swing_artifact"] = artifact
    return bundle
