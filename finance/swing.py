from __future__ import annotations

from dataclasses import dataclass, replace
from math import sqrt
from typing import Any

import numpy as np
import pandas as pd

from .transform import add_daily_swing_features


RISK_ON_MOMENTUM_STRATEGY_KEY = "risk_on_momentum_5d"
RISK_ON_MOMENTUM_STRATEGY_NAME = "Risk-On Momentum 5D"

DEFAULT_SWING_FUTURES_SYMBOLS = (
    "ES=F",
    "NQ=F",
    "YM=F",
    "RTY=F",
    "ZN=F",
    "ZB=F",
    "GC=F",
    "6E=F",
    "6J=F",
    "6B=F",
    "6A=F",
    "6C=F",
)

MACRO_SCORE_MEMBERS: dict[str, dict[str, float]] = {
    "risk_on": {"ES=F": 1.0, "NQ=F": 1.0, "YM=F": 1.0, "RTY=F": 1.0},
    "rate_pressure": {"ZN=F": -1.0, "ZB=F": -1.0},
    "dollar_pressure": {"6E=F": -1.0, "6J=F": -1.0, "6B=F": -1.0, "6A=F": -1.0, "6C=F": -1.0},
    "safe_haven": {"GC=F": 1.0, "ZN=F": 1.0, "ZB=F": 1.0, "6J=F": 1.0},
}


@dataclass(frozen=True)
class RiskOnMomentumConfig:
    start: str | None = None
    end: str | None = None
    start_balance: float = 10_000.0
    execution_mode: str = "close_based"
    exit_mode: str = "fixed_pct"
    max_holding_days: int = 5
    stop_loss_pct: float = -2.5
    take_profit_pct: float = 5.0
    atr_period: int = 14
    stop_atr_multiple: float = 1.0
    take_profit_atr_multiple: float = 2.0
    max_new_positions_per_day: int = 3
    max_total_positions: int = 3
    allow_duplicate_positions: bool = False
    allow_pyramiding: bool = False
    transaction_cost_bps: float = 0.0
    slippage_bps: float = 0.0
    macro_filter_enabled: bool = True
    macro_filter_mode: str = "hard_filter"
    risk_on_min: float = 0.0
    rate_pressure_max: float = 1.0
    dollar_pressure_max: float = 1.0
    safe_haven_max: float = 1.0
    macro_max_staleness_days: int = 5
    min_price: float = 5.0
    min_avg_dollar_volume_20d: float = 20_000_000.0
    min_avg_volume_20d: float = 500_000.0
    min_history_days: int = 60
    require_positive_5d_return: bool = True
    return_20d_percentile_min: float = 0.80
    max_ma20_extension: float = 1.15
    max_5d_return_before_penalty: float = 0.12
    max_volatility_20d_before_penalty: float = 0.06
    scanner_top_n_per_day: int = 50
    ranking_mode: str = "score"
    random_seed: int = 42
    collect_scanner_rows: bool = True


@dataclass(frozen=True)
class Position:
    symbol: str
    signal_date: pd.Timestamp
    entry_date: pd.Timestamp
    entry_price: float
    quantity: float
    entry_notional: float
    entry_fee: float
    ranking_score: float
    stop_price: float
    take_profit_price: float
    atr_at_entry: float | None
    macro_snapshot: dict[str, Any]


@dataclass(frozen=True)
class SwingBacktestResult:
    result_df: pd.DataFrame
    trade_log_df: pd.DataFrame
    scanner_df: pd.DataFrame
    metrics: dict[str, Any]
    monthly_returns_df: pd.DataFrame
    yearly_returns_df: pd.DataFrame
    ticker_contribution_df: pd.DataFrame
    warnings: list[str]


def _normalize_percent(value: float) -> float:
    value = float(value or 0.0)
    return value / 100.0 if abs(value) > 1.0 else value


def _date_key(value: Any) -> pd.Timestamp:
    return pd.Timestamp(value).normalize()


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _validate_config(config: RiskOnMomentumConfig) -> None:
    if config.execution_mode != "close_based":
        raise ValueError("Risk-On Momentum 5D V1 only supports execution_mode='close_based'.")
    if config.exit_mode != "fixed_pct":
        raise ValueError("Risk-On Momentum 5D V1 only supports exit_mode='fixed_pct'.")
    if config.macro_filter_mode not in {"hard_filter", "off"}:
        raise ValueError("Risk-On Momentum 5D V1 only supports macro_filter_mode='hard_filter' or 'off'.")
    if config.allow_duplicate_positions:
        raise ValueError("Risk-On Momentum 5D V1 does not support duplicate simultaneous positions.")
    if config.allow_pyramiding:
        raise ValueError("Risk-On Momentum 5D V1 does not support pyramiding.")
    if int(config.max_total_positions) <= 0:
        raise ValueError("max_total_positions must be positive.")
    if int(config.max_new_positions_per_day) <= 0:
        raise ValueError("max_new_positions_per_day must be positive.")
    if int(config.max_holding_days) <= 0:
        raise ValueError("max_holding_days must be positive.")
    if float(config.start_balance) <= 0:
        raise ValueError("start_balance must be positive.")
    if config.ranking_mode not in {"score", "random"}:
        raise ValueError("ranking_mode must be 'score' or 'random'.")


def build_futures_macro_mean_z_scores(futures_history: pd.DataFrame) -> pd.DataFrame:
    """
    Build point-in-time futures macro mean-z score rows for swing filtering.

    The score definitions match the existing futures macro thermometer, but the
    output keeps the continuous Mean Z values used by this strategy's hard
    filter thresholds.
    """

    if futures_history is None or futures_history.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "risk_on_mean_z",
                "rate_pressure_mean_z",
                "dollar_pressure_mean_z",
                "safe_haven_mean_z",
                "standardized_symbol_count",
            ]
        )

    required = {"provider_symbol", "candle_time_utc", "close"}
    missing = required.difference(futures_history.columns)
    if missing:
        raise KeyError(f"futures_history is missing required columns: {sorted(missing)}")

    d = futures_history.copy()
    d["provider_symbol"] = d["provider_symbol"].astype(str).str.upper()
    d["date"] = pd.to_datetime(d["candle_time_utc"], errors="coerce").dt.normalize()
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d = d.dropna(subset=["provider_symbol", "date", "close"]).sort_values(["date", "provider_symbol"])
    if d.empty:
        return pd.DataFrame()

    close_matrix = d.pivot_table(index="date", columns="provider_symbol", values="close", aggfunc="last").sort_index()
    returns = close_matrix.pct_change(fill_method=None)
    rolling_vol = returns.rolling(60, min_periods=60).std(ddof=0)
    standardized = returns / rolling_vol.replace(0.0, np.nan)

    out = pd.DataFrame(index=standardized.index)
    for score_name, members in MACRO_SCORE_MEMBERS.items():
        weighted = []
        weights = []
        for symbol, signed_weight in members.items():
            if symbol not in standardized.columns:
                continue
            weight = abs(float(signed_weight))
            weighted.append(standardized[symbol] * (1.0 if signed_weight >= 0 else -1.0) * weight)
            weights.append(standardized[symbol].notna().astype(float) * weight)
        if not weighted:
            out[f"{score_name}_mean_z"] = np.nan
            out[f"{score_name}_coverage"] = 0
            continue
        weighted_sum = pd.concat(weighted, axis=1).sum(axis=1, min_count=1)
        weight_sum = pd.concat(weights, axis=1).sum(axis=1)
        out[f"{score_name}_mean_z"] = weighted_sum / weight_sum.replace(0.0, np.nan)
        out[f"{score_name}_coverage"] = pd.concat(weights, axis=1).gt(0).sum(axis=1)

    out["standardized_symbol_count"] = standardized.notna().sum(axis=1)
    out = out.reset_index().rename(columns={"index": "date"})
    return out.dropna(subset=["date"]).reset_index(drop=True)


def _build_financial_risk_snapshot(statement_history: pd.DataFrame) -> pd.DataFrame:
    if statement_history is None or statement_history.empty:
        return pd.DataFrame()

    required = {"symbol", "latest_available_at", "period_end"}
    missing = required.difference(statement_history.columns)
    if missing:
        raise KeyError(f"statement_history is missing required columns: {sorted(missing)}")

    d = statement_history.copy()
    d["symbol"] = d["symbol"].astype(str).str.upper()
    d["period_end"] = pd.to_datetime(d["period_end"], errors="coerce").astype("datetime64[ns]")
    d["latest_available_at"] = pd.to_datetime(d["latest_available_at"], errors="coerce").astype("datetime64[ns]")
    d = d.dropna(subset=["symbol", "latest_available_at"]).sort_values(["symbol", "period_end"])
    if d.empty:
        return d

    d["operating_income"] = pd.to_numeric(d.get("operating_income"), errors="coerce")
    d["total_debt"] = pd.to_numeric(d.get("total_debt"), errors="coerce")
    d["shareholders_equity"] = pd.to_numeric(d.get("shareholders_equity"), errors="coerce")
    d["total_assets"] = pd.to_numeric(d.get("total_assets"), errors="coerce")

    operating_loss = d["operating_income"] < 0
    d["operating_loss_streak_3"] = operating_loss.groupby(d["symbol"], sort=False).transform(
        lambda s: s.rolling(3, min_periods=3).sum()
    )
    d["debt_to_equity"] = d["total_debt"] / d["shareholders_equity"].replace(0.0, np.nan)
    d["financial_filter_pass"] = (
        d["total_assets"].notna()
        & (d["total_assets"] > 0)
        & d["shareholders_equity"].notna()
        & (d["shareholders_equity"] > 0)
        & (d["operating_loss_streak_3"].fillna(0) < 3)
        & (d["debt_to_equity"].fillna(0) <= 3.0)
    )
    d["financial_filter_reason"] = np.select(
        [
            d["total_assets"].isna() | (d["total_assets"] <= 0),
            d["shareholders_equity"].isna() | (d["shareholders_equity"] <= 0),
            d["operating_loss_streak_3"].fillna(0) >= 3,
            d["debt_to_equity"].fillna(0) > 3.0,
        ],
        [
            "missing_or_invalid_assets",
            "missing_or_invalid_equity",
            "three_year_operating_loss_streak",
            "debt_to_equity_above_3",
        ],
        default="pass",
    )
    return d.sort_values(["symbol", "latest_available_at", "period_end"]).reset_index(drop=True)


def attach_financial_risk_flags(features: pd.DataFrame, statement_history: pd.DataFrame | None) -> pd.DataFrame:
    d = features.copy()
    d["date"] = pd.to_datetime(d["date"], errors="coerce").astype("datetime64[ns]")
    d["financial_filter_pass"] = False
    d["financial_filter_reason"] = "missing_statement"
    d["financial_available_at"] = pd.NaT
    d["financial_debt_to_equity"] = np.nan
    d["financial_operating_loss_streak_3"] = np.nan

    snapshot = _build_financial_risk_snapshot(statement_history if statement_history is not None else pd.DataFrame())
    if snapshot.empty or d.empty:
        return d

    snapshot_cols = [
        "symbol",
        "latest_available_at",
        "financial_filter_pass",
        "financial_filter_reason",
        "debt_to_equity",
        "operating_loss_streak_3",
    ]
    pieces: list[pd.DataFrame] = []
    for symbol, price_group in d.sort_values(["symbol", "date"]).groupby("symbol", sort=False):
        statement_group = snapshot[snapshot["symbol"] == symbol][snapshot_cols].sort_values("latest_available_at")
        if statement_group.empty:
            pieces.append(price_group)
            continue
        merged = pd.merge_asof(
            price_group.sort_values("date"),
            statement_group,
            left_on="date",
            right_on="latest_available_at",
            by="symbol",
            direction="backward",
        )
        merged["financial_filter_pass"] = merged["financial_filter_pass_y"].fillna(False).astype(bool)
        merged["financial_filter_reason"] = merged["financial_filter_reason_y"].fillna("missing_statement")
        merged["financial_available_at"] = merged["latest_available_at"]
        merged["financial_debt_to_equity"] = pd.to_numeric(merged["debt_to_equity"], errors="coerce")
        merged["financial_operating_loss_streak_3"] = pd.to_numeric(
            merged["operating_loss_streak_3"],
            errors="coerce",
        )
        drop_cols = [
            col
            for col in [
                "financial_filter_pass_y",
                "financial_filter_reason_y",
                "latest_available_at",
                "debt_to_equity",
                "operating_loss_streak_3",
            ]
            if col in merged.columns
        ]
        merged = merged.drop(columns=drop_cols)
        if "financial_filter_pass_x" in merged.columns:
            merged = merged.drop(columns=["financial_filter_pass_x"])
        if "financial_filter_reason_x" in merged.columns:
            merged = merged.drop(columns=["financial_filter_reason_x"])
        pieces.append(merged)

    return pd.concat(pieces, ignore_index=True).sort_values(["date", "symbol"]).reset_index(drop=True)


def prepare_swing_feature_frame(
    price_history: pd.DataFrame,
    *,
    statement_history: pd.DataFrame | None = None,
) -> pd.DataFrame:
    features = add_daily_swing_features(price_history)
    if features.empty:
        return features
    features = features.rename(columns={"symbol": "symbol", "date": "date"})
    features = attach_financial_risk_flags(features, statement_history)
    return features.sort_values(["date", "symbol"]).reset_index(drop=True)


def _macro_lookup_builder(macro_scores: pd.DataFrame | None):
    if macro_scores is None or macro_scores.empty:
        dates = pd.DatetimeIndex([])
        frame = pd.DataFrame()
    else:
        frame = macro_scores.copy()
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
        frame = frame.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"], keep="last")
        dates = pd.DatetimeIndex(frame["date"])

    def lookup(signal_date: pd.Timestamp, config: RiskOnMomentumConfig) -> tuple[bool, str, dict[str, Any]]:
        if not config.macro_filter_enabled or config.macro_filter_mode == "off":
            return True, "disabled", {}
        if frame.empty or dates.empty:
            return False, "missing_macro_scores", {}
        index = dates.searchsorted(_date_key(signal_date), side="right") - 1
        if index < 0:
            return False, "missing_macro_scores", {}
        row = frame.iloc[int(index)]
        score_date = _date_key(row["date"])
        staleness = (_date_key(signal_date) - score_date).days
        snapshot = {
            "macro_score_date": score_date.strftime("%Y-%m-%d"),
            "macro_staleness_days": int(staleness),
            "risk_on_mean_z": _safe_float(row.get("risk_on_mean_z")),
            "rate_pressure_mean_z": _safe_float(row.get("rate_pressure_mean_z")),
            "dollar_pressure_mean_z": _safe_float(row.get("dollar_pressure_mean_z")),
            "safe_haven_mean_z": _safe_float(row.get("safe_haven_mean_z")),
            "standardized_symbol_count": int(row.get("standardized_symbol_count") or 0),
        }
        if staleness > int(config.macro_max_staleness_days):
            return False, "stale_macro_scores", snapshot
        checks = [
            snapshot["risk_on_mean_z"] is not None and snapshot["risk_on_mean_z"] > float(config.risk_on_min),
            snapshot["rate_pressure_mean_z"] is not None
            and snapshot["rate_pressure_mean_z"] <= float(config.rate_pressure_max),
            snapshot["dollar_pressure_mean_z"] is not None
            and snapshot["dollar_pressure_mean_z"] <= float(config.dollar_pressure_max),
            snapshot["safe_haven_mean_z"] is not None
            and snapshot["safe_haven_mean_z"] <= float(config.safe_haven_max),
        ]
        if all(checks):
            return True, "pass", snapshot
        return False, "hard_filter_failed", snapshot

    return lookup


def _rank_candidates(day_rows: pd.DataFrame, config: RiskOnMomentumConfig, rng: np.random.Generator) -> pd.DataFrame:
    eligible = day_rows[
        (day_rows["close"] >= float(config.min_price))
        & (day_rows["avg_dollar_volume_20d"] >= float(config.min_avg_dollar_volume_20d))
        & (day_rows["avg_volume_20d"] >= float(config.min_avg_volume_20d))
        & (day_rows["history_days"] >= int(config.min_history_days))
        & (day_rows["financial_filter_pass"].fillna(False).astype(bool))
    ].copy()
    if eligible.empty:
        return eligible

    eligible["return_20d_percentile"] = eligible["return_20d"].rank(pct=True)
    eligible["candidate_condition"] = (
        (eligible["close"] > eligible["ma20"])
        & (eligible["close"] > eligible["ma50"])
        & (eligible["return_20d_percentile"] >= float(config.return_20d_percentile_min))
        & (eligible["volume"] > eligible["avg_volume_20d"])
    )
    if config.require_positive_5d_return:
        eligible["candidate_condition"] = eligible["candidate_condition"] & (eligible["return_5d"] > 0)

    eligible["entry_condition"] = eligible["candidate_condition"] & (
        (eligible["close"] >= eligible["close_5d_high"])
        | ((eligible["daily_return"] > 0) & (eligible["volume"] > eligible["avg_volume_20d"]))
    )
    candidates = eligible[eligible["candidate_condition"]].copy()
    if candidates.empty:
        return candidates

    candidates["overheat_penalty"] = np.maximum(
        (candidates["close"] / candidates["ma20"].replace(0.0, np.nan)) - float(config.max_ma20_extension),
        0.0,
    ) * 100.0
    candidates["return_5d_penalty"] = np.maximum(
        candidates["return_5d"].fillna(0.0) - float(config.max_5d_return_before_penalty),
        0.0,
    ) * 100.0
    candidates["volatility_penalty"] = np.maximum(
        candidates["volatility_20d"].fillna(0.0) - float(config.max_volatility_20d_before_penalty),
        0.0,
    ) * 100.0
    candidates["ranking_score"] = (
        candidates["return_20d_percentile"].fillna(0.0) * 40.0
        + candidates["return_5d"].fillna(0.0) * 100.0
        + np.log1p(candidates["volume_ratio"].clip(lower=0).fillna(0.0)) * 10.0
        + candidates["ma20_distance"].fillna(0.0) * 50.0
        + candidates["ma50_distance"].fillna(0.0) * 30.0
        - candidates["overheat_penalty"]
        - candidates["return_5d_penalty"]
        - candidates["volatility_penalty"]
    )
    if config.ranking_mode == "random":
        candidates["ranking_score"] = rng.random(len(candidates))
    return candidates.sort_values(["ranking_score", "symbol"], ascending=[False, True]).reset_index(drop=True)


def _portfolio_value(
    *,
    cash: float,
    positions: dict[str, Position],
    day_rows_by_symbol: dict[str, dict[str, Any]],
    price_col: str,
) -> float:
    total = float(cash)
    for symbol, position in positions.items():
        row = day_rows_by_symbol.get(symbol)
        price = _safe_float(row.get(price_col)) if row else None
        if price is None:
            price = position.entry_price
        total += position.quantity * float(price)
    return float(total)


def _consecutive_loss_count(trades: pd.DataFrame) -> int:
    if trades.empty or "net_return_pct" not in trades.columns:
        return 0
    longest = 0
    current = 0
    for value in pd.to_numeric(trades["net_return_pct"], errors="coerce").fillna(0.0):
        if value < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return int(longest)


def _performance_metrics(result_df: pd.DataFrame, trades: pd.DataFrame, *, start_balance: float) -> dict[str, Any]:
    if result_df.empty:
        return {}
    result = result_df.sort_values("Date").reset_index(drop=True)
    returns = pd.to_numeric(result["Total Return"], errors="coerce").dropna()
    balance = pd.to_numeric(result["Total Balance"], errors="coerce")
    drawdown = balance / balance.cummax() - 1.0
    start_date = pd.Timestamp(result["Date"].iloc[0])
    end_date = pd.Timestamp(result["Date"].iloc[-1])
    years = max((end_date - start_date).days / 365.25, 1 / 365.25)
    end_balance = float(balance.iloc[-1])
    closed = trades[trades["exit_reason"] != "END_OF_BACKTEST"].copy() if not trades.empty else trades
    net_returns = pd.to_numeric(closed.get("net_return_pct", pd.Series(dtype=float)), errors="coerce").dropna()
    wins = net_returns[net_returns > 0]
    losses = net_returns[net_returns < 0]
    mean_daily = returns.mean() if not returns.empty else np.nan
    std_daily = returns.std(ddof=0) if len(returns) > 1 else np.nan
    return {
        "total_trades": int(len(closed)),
        "win_rate": float((net_returns > 0).mean()) if len(net_returns) else np.nan,
        "avg_return": float(net_returns.mean()) if len(net_returns) else np.nan,
        "avg_win": float(wins.mean()) if len(wins) else np.nan,
        "avg_loss": float(losses.mean()) if len(losses) else np.nan,
        "expectancy": float(net_returns.mean()) if len(net_returns) else np.nan,
        "cumulative_return": float(end_balance / float(start_balance) - 1.0),
        "cagr": float((end_balance / float(start_balance)) ** (1 / years) - 1.0),
        "mdd": float(drawdown.min()) if not drawdown.empty else np.nan,
        "sharpe_ratio": float(mean_daily / std_daily * sqrt(252)) if std_daily and not pd.isna(std_daily) else np.nan,
        "max_consecutive_losses": _consecutive_loss_count(closed),
        "avg_holding_days": float(pd.to_numeric(closed.get("holding_days", pd.Series(dtype=float)), errors="coerce").mean())
        if len(closed)
        else np.nan,
        "gross_profit": float(pd.to_numeric(closed.get("gross_pnl", pd.Series(dtype=float)), errors="coerce").clip(lower=0).sum())
        if len(closed)
        else 0.0,
        "gross_loss": float(pd.to_numeric(closed.get("gross_pnl", pd.Series(dtype=float)), errors="coerce").clip(upper=0).sum())
        if len(closed)
        else 0.0,
        "total_fees": float(pd.to_numeric(trades.get("total_fee", pd.Series(dtype=float)), errors="coerce").sum())
        if not trades.empty
        else 0.0,
    }


def _period_return_table(result_df: pd.DataFrame, freq: str, label: str) -> pd.DataFrame:
    if result_df.empty:
        return pd.DataFrame(columns=[label, "return"])
    d = result_df[["Date", "Total Balance"]].copy()
    d["Date"] = pd.to_datetime(d["Date"])
    d = d.sort_values("Date").set_index("Date")
    period_end_balance = d["Total Balance"].resample(freq).last().dropna()
    if period_end_balance.empty:
        return pd.DataFrame(columns=[label, "return"])
    previous = pd.concat([pd.Series([float(d["Total Balance"].iloc[0])], index=[period_end_balance.index[0]]), period_end_balance.iloc[:-1]])
    values = period_end_balance.to_numpy() / previous.to_numpy() - 1.0
    return pd.DataFrame({label: period_end_balance.index.strftime("%Y-%m"), "return": values})


def _ticker_contribution(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["symbol", "trades", "net_pnl", "avg_net_return_pct", "win_rate"])
    closed = trades[trades["exit_reason"] != "END_OF_BACKTEST"].copy()
    if closed.empty:
        return pd.DataFrame(columns=["symbol", "trades", "net_pnl", "avg_net_return_pct", "win_rate"])
    grouped = closed.groupby("symbol", as_index=False).agg(
        trades=("symbol", "size"),
        net_pnl=("net_pnl", "sum"),
        avg_net_return_pct=("net_return_pct", "mean"),
        win_rate=("net_return_pct", lambda s: float((s > 0).mean())),
    )
    return grouped.sort_values("net_pnl", ascending=False).reset_index(drop=True)


def run_risk_on_momentum_backtest(
    price_history: pd.DataFrame,
    *,
    config: RiskOnMomentumConfig,
    macro_scores: pd.DataFrame | None = None,
    statement_history: pd.DataFrame | None = None,
    prepared_features: pd.DataFrame | None = None,
) -> SwingBacktestResult:
    _validate_config(config)
    warnings: list[str] = []

    features = prepared_features.copy() if prepared_features is not None else prepare_swing_feature_frame(
        price_history,
        statement_history=statement_history,
    )
    if features.empty:
        raise ValueError("No usable price rows were available for Risk-On Momentum 5D.")

    features["date"] = pd.to_datetime(features["date"], errors="coerce").dt.normalize()
    start_ts = pd.to_datetime(config.start).normalize() if config.start else features["date"].min()
    end_ts = pd.to_datetime(config.end).normalize() if config.end else features["date"].max()
    features = features[(features["date"] <= end_ts)].sort_values(["date", "symbol"]).reset_index(drop=True)
    dates = [pd.Timestamp(value).normalize() for value in sorted(features["date"].dropna().unique())]
    dates = [value for value in dates if value >= start_ts and value <= end_ts]
    if len(dates) < 2:
        raise ValueError("At least two trading dates are required for D+1 execution.")

    by_date = {pd.Timestamp(date_value).normalize(): frame for date_value, frame in features.groupby("date", sort=True)}
    macro_lookup = _macro_lookup_builder(macro_scores)
    rng = np.random.default_rng(int(config.random_seed))

    cash = float(config.start_balance)
    positions: dict[str, Position] = {}
    pending_sells: list[dict[str, Any]] = []
    pending_buys: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []
    trade_rows: list[dict[str, Any]] = []
    scanner_rows: list[dict[str, Any]] = []
    previous_total: float | None = None
    cost_frac = max(float(config.transaction_cost_bps), 0.0) / 10_000.0
    slippage_frac = max(float(config.slippage_bps), 0.0) / 10_000.0
    stop_loss = _normalize_percent(config.stop_loss_pct)
    take_profit = _normalize_percent(config.take_profit_pct)

    for idx, signal_date in enumerate(dates):
        day_rows = by_date.get(signal_date, pd.DataFrame())
        day_rows_by_symbol = {
            str(row["symbol"]): dict(row)
            for _, row in day_rows.iterrows()
        }

        if pending_sells:
            remaining_sells: list[dict[str, Any]] = []
            for order in pending_sells:
                symbol = str(order["symbol"])
                position = positions.get(symbol)
                row = day_rows_by_symbol.get(symbol)
                open_price = _safe_float(row.get("open")) if row else None
                if position is None:
                    continue
                if open_price is None:
                    remaining_sells.append(order)
                    continue
                exit_price = float(open_price) * (1.0 - slippage_frac)
                gross_proceeds = position.quantity * exit_price
                exit_fee = gross_proceeds * cost_frac
                net_proceeds = gross_proceeds - exit_fee
                cash += net_proceeds
                exit_signal_date = pd.Timestamp(order["exit_signal_date"]).normalize()
                holding_days = sum(1 for date_value in dates if position.entry_date <= date_value <= exit_signal_date)
                gross_pnl = gross_proceeds - position.entry_notional
                net_pnl = net_proceeds - position.entry_notional - position.entry_fee
                trade_rows.append(
                    {
                        "entry_signal_date": position.signal_date.strftime("%Y-%m-%d"),
                        "entry_date": position.entry_date.strftime("%Y-%m-%d"),
                        "exit_signal_date": pd.Timestamp(order["exit_signal_date"]).strftime("%Y-%m-%d"),
                        "exit_date": signal_date.strftime("%Y-%m-%d"),
                        "symbol": symbol,
                        "entry_price": position.entry_price,
                        "exit_price": exit_price,
                        "quantity": position.quantity,
                        "entry_notional": position.entry_notional,
                        "gross_proceeds": gross_proceeds,
                        "gross_pnl": gross_pnl,
                        "net_pnl": net_pnl,
                        "gross_return_pct": exit_price / position.entry_price - 1.0,
                        "net_return_pct": net_proceeds / (position.entry_notional + position.entry_fee) - 1.0,
                        "exit_reason": order["reason"],
                        "holding_days": holding_days,
                        "ranking_score": position.ranking_score,
                        "entry_macro_risk_on_mean_z": position.macro_snapshot.get("risk_on_mean_z"),
                        "entry_macro_rate_pressure_mean_z": position.macro_snapshot.get("rate_pressure_mean_z"),
                        "entry_macro_dollar_pressure_mean_z": position.macro_snapshot.get("dollar_pressure_mean_z"),
                        "entry_macro_safe_haven_mean_z": position.macro_snapshot.get("safe_haven_mean_z"),
                        "execution_mode": config.execution_mode,
                        "exit_mode": config.exit_mode,
                        "stop_price": position.stop_price,
                        "take_profit_price": position.take_profit_price,
                        "atr_at_entry": position.atr_at_entry,
                        "entry_fee": position.entry_fee,
                        "exit_fee": exit_fee,
                        "total_fee": position.entry_fee + exit_fee,
                    }
                )
                positions.pop(symbol, None)
            pending_sells = remaining_sells

        if pending_buys:
            portfolio_open_value = _portfolio_value(
                cash=cash,
                positions=positions,
                day_rows_by_symbol=day_rows_by_symbol,
                price_col="open",
            )
            slot_value = portfolio_open_value / float(config.max_total_positions)
            remaining_buys: list[dict[str, Any]] = []
            for order in pending_buys:
                if len(positions) >= int(config.max_total_positions):
                    break
                symbol = str(order["symbol"])
                if symbol in positions and not config.allow_duplicate_positions:
                    continue
                row = day_rows_by_symbol.get(symbol)
                open_price = _safe_float(row.get("open")) if row else None
                if open_price is None:
                    remaining_buys.append(order)
                    continue
                entry_price = float(open_price) * (1.0 + slippage_frac)
                spend = min(float(slot_value), cash)
                if spend <= 0 or entry_price <= 0:
                    continue
                entry_notional = spend / (1.0 + cost_frac)
                entry_fee = entry_notional * cost_frac
                quantity = entry_notional / entry_price
                cash -= entry_notional + entry_fee
                atr_at_entry = _safe_float(row.get("atr14"))
                positions[symbol] = Position(
                    symbol=symbol,
                    signal_date=pd.Timestamp(order["signal_date"]),
                    entry_date=signal_date,
                    entry_price=entry_price,
                    quantity=quantity,
                    entry_notional=entry_notional,
                    entry_fee=entry_fee,
                    ranking_score=float(order.get("ranking_score") or 0.0),
                    stop_price=entry_price * (1.0 + stop_loss),
                    take_profit_price=entry_price * (1.0 + take_profit),
                    atr_at_entry=atr_at_entry,
                    macro_snapshot=dict(order.get("macro_snapshot") or {}),
                )
            pending_buys = remaining_buys

        total_balance = _portfolio_value(
            cash=cash,
            positions=positions,
            day_rows_by_symbol=day_rows_by_symbol,
            price_col="close",
        )
        total_return = np.nan if previous_total is None else total_balance / previous_total - 1.0
        previous_total = total_balance

        macro_pass, macro_reason, macro_snapshot = macro_lookup(signal_date, config)
        result_rows.append(
            {
                "Date": signal_date,
                "Total Balance": total_balance,
                "Total Return": total_return,
                "Cash": cash,
                "Position Count": len(positions),
                "Held Symbols": sorted(positions),
                "Macro Filter Pass": macro_pass,
                "Macro Filter Reason": macro_reason,
                "Pending Buy Count": 0,
                "Pending Sell Count": 0,
            }
        )

        next_date_exists = idx < len(dates) - 1
        exit_orders: list[dict[str, Any]] = []
        for symbol, position in list(positions.items()):
            row = day_rows_by_symbol.get(symbol)
            close_price = _safe_float(row.get("close")) if row else None
            if close_price is None:
                continue
            trading_holding_days = sum(1 for date_value in dates if position.entry_date <= date_value <= signal_date)
            reason = None
            if close_price <= position.stop_price:
                reason = "STOP_LOSS"
            elif close_price >= position.take_profit_price:
                reason = "TAKE_PROFIT"
            elif trading_holding_days >= int(config.max_holding_days):
                reason = "MAX_HOLDING_DAYS"
            if reason and next_date_exists:
                exit_orders.append(
                    {
                        "symbol": symbol,
                        "reason": reason,
                        "exit_signal_date": signal_date,
                    }
                )

        held_symbols = set(positions)
        exit_symbols = {str(order["symbol"]) for order in exit_orders}
        projected_positions = max(0, len(positions) - len(exit_symbols))
        available_slots = max(0, int(config.max_total_positions) - projected_positions)
        available_new = min(int(config.max_new_positions_per_day), available_slots)

        buy_orders: list[dict[str, Any]] = []
        ranked = pd.DataFrame()
        if macro_pass and next_date_exists and available_new > 0:
            ranked = _rank_candidates(day_rows, config, rng)
            if not ranked.empty:
                entry_ranked = ranked[ranked["entry_condition"].fillna(False)].copy()
                if not config.allow_duplicate_positions:
                    entry_ranked = entry_ranked[~entry_ranked["symbol"].isin(held_symbols)]
                selected = entry_ranked.head(available_new)
                for _, row in selected.iterrows():
                    buy_orders.append(
                        {
                            "symbol": str(row["symbol"]),
                            "signal_date": signal_date,
                            "ranking_score": float(row.get("ranking_score") or 0.0),
                            "macro_snapshot": macro_snapshot,
                        }
                    )

        if config.collect_scanner_rows and not ranked.empty:
            selected_symbols = {str(order["symbol"]) for order in buy_orders}
            scanner_source = ranked.head(max(int(config.scanner_top_n_per_day), len(selected_symbols))).copy()
            for rank_idx, (_, row) in enumerate(scanner_source.iterrows(), start=1):
                symbol = str(row["symbol"])
                if symbol in selected_symbols:
                    status = "QUEUED_BUY"
                elif symbol in held_symbols:
                    status = "HELD_EXCLUDED"
                elif bool(row.get("entry_condition")):
                    status = "RANK_BELOW_SLOT"
                else:
                    status = "WATCHLIST"
                scanner_rows.append(
                    {
                        "date": signal_date.strftime("%Y-%m-%d"),
                        "rank": rank_idx,
                        "symbol": symbol,
                        "status": status,
                        "ranking_score": float(row.get("ranking_score") or 0.0),
                        "return_20d": _safe_float(row.get("return_20d")),
                        "return_20d_percentile": _safe_float(row.get("return_20d_percentile")),
                        "return_5d": _safe_float(row.get("return_5d")),
                        "volume_ratio": _safe_float(row.get("volume_ratio")),
                        "ma20_distance": _safe_float(row.get("ma20_distance")),
                        "ma50_distance": _safe_float(row.get("ma50_distance")),
                        "financial_filter_pass": bool(row.get("financial_filter_pass")),
                        "financial_filter_reason": row.get("financial_filter_reason"),
                        "atr14": _safe_float(row.get("atr14")),
                        "volatility_20d": _safe_float(row.get("volatility_20d")),
                        "macro_filter_pass": macro_pass,
                        "macro_filter_reason": macro_reason,
                    }
                )

        pending_sells = exit_orders
        pending_buys = buy_orders
        result_rows[-1]["Pending Buy Count"] = len(pending_buys)
        result_rows[-1]["Pending Sell Count"] = len(pending_sells)

    final_date = dates[-1]
    final_rows = by_date.get(final_date, pd.DataFrame())
    final_by_symbol = {str(row["symbol"]): dict(row) for _, row in final_rows.iterrows()}
    for symbol, position in positions.items():
        row = final_by_symbol.get(symbol)
        close_price = _safe_float(row.get("close")) if row else position.entry_price
        gross_proceeds = position.quantity * float(close_price)
        gross_pnl = gross_proceeds - position.entry_notional
        net_pnl = gross_proceeds - position.entry_notional - position.entry_fee
        trade_rows.append(
            {
                "entry_signal_date": position.signal_date.strftime("%Y-%m-%d"),
                "entry_date": position.entry_date.strftime("%Y-%m-%d"),
                "exit_signal_date": final_date.strftime("%Y-%m-%d"),
                "exit_date": final_date.strftime("%Y-%m-%d"),
                "symbol": symbol,
                "entry_price": position.entry_price,
                "exit_price": close_price,
                "quantity": position.quantity,
                "entry_notional": position.entry_notional,
                "gross_proceeds": gross_proceeds,
                "gross_pnl": gross_pnl,
                "net_pnl": net_pnl,
                "gross_return_pct": float(close_price) / position.entry_price - 1.0,
                "net_return_pct": gross_proceeds / (position.entry_notional + position.entry_fee) - 1.0,
                "exit_reason": "END_OF_BACKTEST",
                "holding_days": sum(1 for date_value in dates if position.entry_date <= date_value <= final_date),
                "ranking_score": position.ranking_score,
                "entry_macro_risk_on_mean_z": position.macro_snapshot.get("risk_on_mean_z"),
                "entry_macro_rate_pressure_mean_z": position.macro_snapshot.get("rate_pressure_mean_z"),
                "entry_macro_dollar_pressure_mean_z": position.macro_snapshot.get("dollar_pressure_mean_z"),
                "entry_macro_safe_haven_mean_z": position.macro_snapshot.get("safe_haven_mean_z"),
                "execution_mode": config.execution_mode,
                "exit_mode": config.exit_mode,
                "stop_price": position.stop_price,
                "take_profit_price": position.take_profit_price,
                "atr_at_entry": position.atr_at_entry,
                "entry_fee": position.entry_fee,
                "exit_fee": 0.0,
                "total_fee": position.entry_fee,
            }
        )

    result_df = pd.DataFrame(result_rows)
    trade_log_df = pd.DataFrame(trade_rows)
    scanner_df = pd.DataFrame(scanner_rows)
    metrics = _performance_metrics(result_df, trade_log_df, start_balance=float(config.start_balance))
    monthly = _period_return_table(result_df, "ME", "month")
    yearly = _period_return_table(result_df, "YE", "year")
    if not yearly.empty:
        yearly["year"] = pd.to_datetime(yearly["year"], errors="coerce").dt.strftime("%Y")

    if config.macro_filter_enabled and (macro_scores is None or macro_scores.empty):
        warnings.append("Macro filter was enabled, but futures macro score rows were unavailable.")
    if trade_log_df.empty:
        warnings.append("No closed trades were generated for this Risk-On Momentum 5D run.")

    return SwingBacktestResult(
        result_df=result_df,
        trade_log_df=trade_log_df,
        scanner_df=scanner_df,
        metrics=metrics,
        monthly_returns_df=monthly,
        yearly_returns_df=yearly,
        ticker_contribution_df=_ticker_contribution(trade_log_df),
        warnings=warnings,
    )


def build_buy_and_hold_result(
    price_history: pd.DataFrame,
    *,
    symbol: str,
    start: str | None,
    end: str | None,
    start_balance: float,
) -> pd.DataFrame:
    if price_history is None or price_history.empty:
        return pd.DataFrame(columns=["Date", "Total Balance", "Total Return"])
    normalized = str(symbol or "").strip().upper()
    d = price_history.copy()
    d["symbol"] = d["symbol"].astype(str).str.upper()
    d["date"] = pd.to_datetime(d["date"], errors="coerce").dt.normalize()
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    if start is not None:
        d = d[d["date"] >= pd.to_datetime(start).normalize()]
    if end is not None:
        d = d[d["date"] <= pd.to_datetime(end).normalize()]
    d = d[(d["symbol"] == normalized) & d["close"].notna()].sort_values("date")
    if d.empty:
        return pd.DataFrame(columns=["Date", "Total Balance", "Total Return"])
    first_close = float(d["close"].iloc[0])
    out = pd.DataFrame(
        {
            "Date": d["date"],
            "Total Balance": float(start_balance) * d["close"].astype(float) / first_close,
        }
    )
    out["Total Return"] = out["Total Balance"].pct_change()
    return out.reset_index(drop=True)


def clone_config(config: RiskOnMomentumConfig, **changes: Any) -> RiskOnMomentumConfig:
    return replace(config, **changes)
