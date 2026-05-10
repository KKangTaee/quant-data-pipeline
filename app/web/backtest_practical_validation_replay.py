from __future__ import annotations

import time
from datetime import datetime
from typing import Any
from uuid import uuid4

import pandas as pd

from app.web.backtest_practical_validation_curve import curve_records_from_df, optional_float
from app.web.runtime.backtest import (
    ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
    ETF_OPERABILITY_DEFAULT_MIN_AUM_B,
    ETF_REAL_MONEY_DEFAULT_BENCHMARK,
    ETF_REAL_MONEY_DEFAULT_MIN_PRICE,
    ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP,
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
    GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
    GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED,
    GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
    GTAA_DEFAULT_DEFENSIVE_TICKERS,
    GTAA_DEFAULT_RISK_OFF_MODE,
    GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS,
    GTAA_DEFAULT_SIGNAL_INTERVAL,
    GTAA_DEFAULT_TREND_FILTER_WINDOW,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
    STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
    STRICT_MARKET_REGIME_DEFAULT_WINDOW,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
    STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
    run_dual_momentum_backtest_from_db,
    run_equal_weight_backtest_from_db,
    run_global_relative_strength_backtest_from_db,
    run_gtaa_backtest_from_db,
    run_risk_parity_trend_backtest_from_db,
)
from finance.performance import make_monthly_weighted_portfolio, portfolio_performance_summary
from finance.sample import (
    GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS,
    GTAA_DEFAULT_TICKERS,
)


RISK_PARITY_DEFAULT_TICKERS = ["SPY", "TLT", "GLD", "IEF", "LQD"]
DUAL_MOMENTUM_DEFAULT_TICKERS = ["QQQ", "SPY", "IWM", "SOXX", "BIL"]

DISPLAY_NAME_TO_STRATEGY_KEY = {
    "equal weight": "equal_weight",
    "equal_weight": "equal_weight",
    "gtaa": "gtaa",
    "global relative strength": "global_relative_strength",
    "global_relative_strength": "global_relative_strength",
    "risk parity trend": "risk_parity_trend",
    "risk_parity_trend": "risk_parity_trend",
    "dual momentum": "dual_momentum",
    "dual_momentum": "dual_momentum",
}


def _now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _clean_strategy_key(component: dict[str, Any], payload: dict[str, Any]) -> str:
    for value in (
        payload.get("strategy_key"),
        component.get("strategy_key"),
        component.get("strategy_family"),
        component.get("strategy_name"),
        component.get("title"),
    ):
        raw = str(value or "").strip()
        if not raw:
            continue
        normalized = raw.lower().replace("-", " ").replace("_", " ")
        key = DISPLAY_NAME_TO_STRATEGY_KEY.get(normalized) or DISPLAY_NAME_TO_STRATEGY_KEY.get(raw.lower())
        if key:
            return key
        slug = "_".join(part for part in normalized.split() if part)
        if slug in set(DISPLAY_NAME_TO_STRATEGY_KEY.values()):
            return slug
    return ""


def _list_from_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        items = value
    else:
        text = str(value or "")
        for delimiter in [";", "|", "\n", "\t"]:
            text = text.replace(delimiter, ",")
        items = text.split(",")
    output: list[str] = []
    seen: set[str] = set()
    for item in items:
        symbol = str(item or "").strip().upper()
        if not symbol or symbol in {"-", "NONE", "NAN"} or symbol in seen:
            continue
        seen.add(symbol)
        output.append(symbol)
    return output


def _int_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _float_value(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _bool_value(value: Any, default: bool) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def _source_period(source: dict[str, Any]) -> dict[str, Any]:
    period = dict(source.get("period") or {})
    return {
        "start": period.get("start") or period.get("actual_start"),
        "end": period.get("end") or period.get("actual_end"),
        "actual_start": period.get("actual_start") or period.get("start"),
        "actual_end": period.get("actual_end") or period.get("end"),
    }


def _component_payload(source: dict[str, Any], component: dict[str, Any]) -> dict[str, Any]:
    period = _source_period(source)
    replay_contract = dict(component.get("replay_contract") or {})
    payload: dict[str, Any] = {
        "start": period.get("start") or period.get("actual_start"),
        "end": period.get("end") or period.get("actual_end"),
        "timeframe": "1d",
        "option": "month_end",
        "universe_mode": "manual_tickers",
        "preset_name": component.get("title") or component.get("strategy_name"),
        "benchmark_ticker": component.get("benchmark") if component.get("benchmark") not in {"", "-"} else None,
    }
    source_snapshot = dict(source.get("source_snapshot") or {})
    payload.update(dict(source_snapshot.get("settings_snapshot") or {}))
    payload.update(dict(replay_contract.get("settings_snapshot") or {}))
    payload.update(dict(replay_contract.get("contract") or {}))
    payload.update(dict(component.get("contract") or {}))
    payload.setdefault("start", period.get("actual_start"))
    payload.setdefault("end", period.get("actual_end"))
    payload["start"] = payload.get("start") or period.get("actual_start")
    payload["end"] = payload.get("end") or period.get("actual_end")
    if payload.get("top") is None and payload.get("top_n") is not None:
        payload["top"] = payload.get("top_n")
    strategy_key = _clean_strategy_key(component, payload)
    payload["strategy_key"] = strategy_key
    tickers = _list_from_value(payload.get("tickers"))
    if not tickers:
        tickers = _list_from_value(component.get("universe"))
    if not tickers:
        if strategy_key == "gtaa":
            tickers = list(GTAA_DEFAULT_TICKERS)
        elif strategy_key == "global_relative_strength":
            tickers = list(GLOBAL_RELATIVE_STRENGTH_DEFAULT_TICKERS)
        elif strategy_key == "risk_parity_trend":
            tickers = list(RISK_PARITY_DEFAULT_TICKERS)
        elif strategy_key == "dual_momentum":
            tickers = list(DUAL_MOMENTUM_DEFAULT_TICKERS)
    payload["tickers"] = tickers
    return payload


def _summary_from_df(result_df: pd.DataFrame, *, name: str) -> dict[str, Any]:
    if result_df is None or result_df.empty:
        return {}
    try:
        summary_df = portfolio_performance_summary(result_df, name=name, freq="M")
    except Exception:
        return {}
    if summary_df.empty:
        return {}
    row = summary_df.iloc[0]
    return {
        "start_date": str(row.get("Start Date")),
        "end_date": str(row.get("End Date")),
        "end_balance": optional_float(row.get("End Balance")),
        "cagr": optional_float(row.get("CAGR")),
        "sharpe": optional_float(row.get("Sharpe Ratio")),
        "mdd": optional_float(row.get("Maximum Drawdown")),
    }


def _run_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key = str(payload.get("strategy_key") or "").strip()
    common = {
        "tickers": list(payload.get("tickers") or []),
        "start": payload.get("start"),
        "end": payload.get("end"),
        "timeframe": payload.get("timeframe") or "1d",
        "option": payload.get("option") or "month_end",
        "min_price_filter": _float_value(payload.get("min_price_filter"), ETF_REAL_MONEY_DEFAULT_MIN_PRICE),
        "transaction_cost_bps": _float_value(
            payload.get("transaction_cost_bps"),
            ETF_REAL_MONEY_DEFAULT_TRANSACTION_COST_BPS,
        ),
        "benchmark_ticker": str(payload.get("benchmark_ticker") or ETF_REAL_MONEY_DEFAULT_BENCHMARK).strip().upper(),
        "promotion_min_etf_aum_b": _float_value(payload.get("promotion_min_etf_aum_b"), ETF_OPERABILITY_DEFAULT_MIN_AUM_B),
        "promotion_max_bid_ask_spread_pct": _float_value(
            payload.get("promotion_max_bid_ask_spread_pct"),
            ETF_OPERABILITY_DEFAULT_MAX_BID_ASK_SPREAD_PCT,
        ),
        "universe_mode": payload.get("universe_mode") or "manual_tickers",
        "preset_name": payload.get("preset_name"),
    }
    if key == "equal_weight":
        return run_equal_weight_backtest_from_db(
            **common,
            rebalance_interval=_int_value(payload.get("rebalance_interval"), 12),
        )
    if key == "gtaa":
        return run_gtaa_backtest_from_db(
            **common,
            top=_int_value(payload.get("top"), 3),
            interval=_int_value(payload.get("interval"), GTAA_DEFAULT_SIGNAL_INTERVAL),
            score_lookback_months=list(payload.get("score_lookback_months") or GTAA_DEFAULT_SCORE_LOOKBACK_MONTHS),
            score_return_columns=payload.get("score_return_columns"),
            score_weights=dict(payload.get("score_weights")) if payload.get("score_weights") else None,
            trend_filter_window=_int_value(payload.get("trend_filter_window"), GTAA_DEFAULT_TREND_FILTER_WINDOW),
            risk_off_mode=payload.get("risk_off_mode") or GTAA_DEFAULT_RISK_OFF_MODE,
            defensive_tickers=list(payload.get("defensive_tickers") or GTAA_DEFAULT_DEFENSIVE_TICKERS),
            market_regime_enabled=_bool_value(payload.get("market_regime_enabled"), False),
            market_regime_window=_int_value(payload.get("market_regime_window"), STRICT_MARKET_REGIME_DEFAULT_WINDOW),
            market_regime_benchmark=payload.get("market_regime_benchmark") or STRICT_MARKET_REGIME_DEFAULT_BENCHMARK,
            crash_guardrail_enabled=_bool_value(payload.get("crash_guardrail_enabled"), GTAA_DEFAULT_CRASH_GUARDRAIL_ENABLED),
            crash_guardrail_drawdown_threshold=_float_value(
                payload.get("crash_guardrail_drawdown_threshold"),
                GTAA_DEFAULT_CRASH_GUARDRAIL_DRAWDOWN_THRESHOLD,
            ),
            crash_guardrail_lookback_months=_int_value(
                payload.get("crash_guardrail_lookback_months"),
                GTAA_DEFAULT_CRASH_GUARDRAIL_LOOKBACK_MONTHS,
            ),
            underperformance_guardrail_enabled=_bool_value(
                payload.get("underperformance_guardrail_enabled"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=_int_value(
                payload.get("underperformance_guardrail_window_months"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=_float_value(
                payload.get("underperformance_guardrail_threshold"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=_bool_value(
                payload.get("drawdown_guardrail_enabled"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=_int_value(
                payload.get("drawdown_guardrail_window_months"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=_float_value(
                payload.get("drawdown_guardrail_strategy_threshold"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=_float_value(
                payload.get("drawdown_guardrail_gap_threshold"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
        )
    if key == "global_relative_strength":
        return run_global_relative_strength_backtest_from_db(
            **common,
            cash_ticker=payload.get("cash_ticker") or GLOBAL_RELATIVE_STRENGTH_DEFAULT_CASH_TICKER,
            top=_int_value(payload.get("top"), GLOBAL_RELATIVE_STRENGTH_DEFAULT_TOP),
            interval=_int_value(payload.get("interval"), GLOBAL_RELATIVE_STRENGTH_DEFAULT_SIGNAL_INTERVAL),
            score_lookback_months=payload.get("score_lookback_months"),
            score_return_columns=payload.get("score_return_columns"),
            score_weights=dict(payload.get("score_weights")) if payload.get("score_weights") else None,
            trend_filter_window=_int_value(
                payload.get("trend_filter_window"),
                GLOBAL_RELATIVE_STRENGTH_DEFAULT_TREND_FILTER_WINDOW,
            ),
        )
    if key == "risk_parity_trend":
        return run_risk_parity_trend_backtest_from_db(
            **common,
            rebalance_interval=_int_value(payload.get("rebalance_interval"), 1),
            vol_window=_int_value(payload.get("vol_window"), 6),
            underperformance_guardrail_enabled=_bool_value(
                payload.get("underperformance_guardrail_enabled"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=_int_value(
                payload.get("underperformance_guardrail_window_months"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=_float_value(
                payload.get("underperformance_guardrail_threshold"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=_bool_value(
                payload.get("drawdown_guardrail_enabled"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=_int_value(
                payload.get("drawdown_guardrail_window_months"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=_float_value(
                payload.get("drawdown_guardrail_strategy_threshold"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=_float_value(
                payload.get("drawdown_guardrail_gap_threshold"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
        )
    if key == "dual_momentum":
        return run_dual_momentum_backtest_from_db(
            **common,
            top=_int_value(payload.get("top"), 1),
            rebalance_interval=_int_value(payload.get("rebalance_interval"), 1),
            underperformance_guardrail_enabled=_bool_value(
                payload.get("underperformance_guardrail_enabled"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_ENABLED,
            ),
            underperformance_guardrail_window_months=_int_value(
                payload.get("underperformance_guardrail_window_months"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            underperformance_guardrail_threshold=_float_value(
                payload.get("underperformance_guardrail_threshold"),
                STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD,
            ),
            drawdown_guardrail_enabled=_bool_value(
                payload.get("drawdown_guardrail_enabled"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_ENABLED,
            ),
            drawdown_guardrail_window_months=_int_value(
                payload.get("drawdown_guardrail_window_months"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS,
            ),
            drawdown_guardrail_strategy_threshold=_float_value(
                payload.get("drawdown_guardrail_strategy_threshold"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD,
            ),
            drawdown_guardrail_gap_threshold=_float_value(
                payload.get("drawdown_guardrail_gap_threshold"),
                STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD,
            ),
        )
    raise ValueError(f"지원하지 않는 Practical Validation replay strategy입니다: {key or '-'}")


def _combine_replayed_components(
    component_outputs: list[dict[str, Any]],
    *,
    initial_capital: float = 10000.0,
    date_policy: str = "intersection",
) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []
    weights: list[float] = []
    names: list[str] = []
    for index, row in enumerate(component_outputs):
        result_df = row.get("_result_df")
        if not isinstance(result_df, pd.DataFrame) or result_df.empty:
            continue
        dfs.append(result_df)
        weights.append(optional_float(row.get("target_weight")) or 0.0)
        names.append(str(row.get("title") or f"component_{index + 1}"))
    if not dfs:
        return pd.DataFrame()
    if len(dfs) == 1:
        output = dfs[0][["Date", "Total Balance", "Total Return"]].copy()
    else:
        output = make_monthly_weighted_portfolio(
            dfs,
            ratios=weights,
            names=names,
            date_policy=date_policy if date_policy in {"union", "intersection"} else "intersection",
        )
    output = output.copy()
    start_balance = optional_float(output["Total Balance"].iloc[0]) if not output.empty else None
    if start_balance and start_balance > 0:
        output["Total Balance"] = output["Total Balance"] / start_balance * float(initial_capital)
        output["Total Return"] = output["Total Balance"].pct_change().fillna(0.0)
    return output


def run_practical_validation_actual_replay(source: dict[str, Any]) -> dict[str, Any]:
    """Replay a Practical Validation source through existing strategy runtime without adding strategies."""
    source_row = dict(source or {})
    components = [
        dict(component or {})
        for component in list(source_row.get("components") or [])
        if (optional_float(dict(component or {}).get("target_weight")) or 0.0) > 0.0
    ]
    started = time.perf_counter()
    attempted_at = _now_text()
    replay_id = f"pv_replay_{uuid4().hex[:12]}"
    component_outputs: list[dict[str, Any]] = []
    benchmark_curve_records: list[dict[str, Any]] = []
    benchmark_ticker = "-"

    for index, component in enumerate(components):
        title = str(component.get("title") or component.get("strategy_name") or f"Component {index + 1}")
        payload = _component_payload(source_row, component)
        component_id = str(component.get("component_id") or component.get("registry_id") or f"component_{index + 1}")
        if not payload.get("strategy_key"):
            component_outputs.append(
                {
                    "component_id": component_id,
                    "title": title,
                    "target_weight": optional_float(component.get("target_weight")) or 0.0,
                    "strategy_key": "-",
                    "status": "NOT_RUN",
                    "error": "strategy_key를 확인할 수 없어 actual runtime replay를 건너뜁니다.",
                    "payload_preview": payload,
                }
            )
            continue
        try:
            bundle = _run_payload(payload)
            result_df = bundle.get("result_df")
            if not isinstance(result_df, pd.DataFrame) or result_df.empty:
                raise ValueError("runtime result_df가 비어 있습니다.")
            meta = dict(bundle.get("meta") or {})
            summary = _summary_from_df(result_df, name=title)
            benchmark_df = bundle.get("benchmark_chart_df")
            if not benchmark_curve_records and isinstance(benchmark_df, pd.DataFrame) and not benchmark_df.empty:
                benchmark_curve_records = curve_records_from_df(
                    benchmark_df.rename(
                        columns={
                            "Benchmark Total Balance": "Total Balance",
                            "Benchmark Total Return": "Total Return",
                        }
                    )
                )
                benchmark_ticker = str(payload.get("benchmark_ticker") or component.get("benchmark") or "Benchmark")
            component_outputs.append(
                {
                    "component_id": component_id,
                    "title": title,
                    "target_weight": optional_float(component.get("target_weight")) or 0.0,
                    "strategy_key": payload.get("strategy_key"),
                    "status": "PASS",
                    "result_rows": len(result_df),
                    "actual_start": meta.get("actual_result_start") or summary.get("start_date"),
                    "actual_end": meta.get("actual_result_end") or summary.get("end_date"),
                    "summary": summary,
                    "payload_preview": {
                        key: value
                        for key, value in payload.items()
                        if key
                        in {
                            "strategy_key",
                            "tickers",
                            "start",
                            "end",
                            "timeframe",
                            "option",
                            "top",
                            "interval",
                            "rebalance_interval",
                            "benchmark_ticker",
                            "preset_name",
                            "universe_mode",
                        }
                    },
                    "result_curve": curve_records_from_df(result_df),
                    "_result_df": result_df,
                }
            )
        except Exception as exc:
            component_outputs.append(
                {
                    "component_id": component_id,
                    "title": title,
                    "target_weight": optional_float(component.get("target_weight")) or 0.0,
                    "strategy_key": payload.get("strategy_key") or "-",
                    "status": "REVIEW",
                    "error": str(exc),
                    "payload_preview": {
                        key: value
                        for key, value in payload.items()
                        if key in {"strategy_key", "tickers", "start", "end", "timeframe", "option", "benchmark_ticker"}
                    },
                }
            )

    successful = [row for row in component_outputs if row.get("status") == "PASS"]
    construction = dict(source_row.get("construction") or {})
    portfolio_df = _combine_replayed_components(
        component_outputs,
        date_policy=str(construction.get("date_policy") or "intersection"),
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
    if portfolio_df.empty:
        status = "BLOCKED" if not successful else "REVIEW"
        summary = {}
        portfolio_curve_records: list[dict[str, Any]] = []
    else:
        status = "PASS" if len(successful) == len(components) else "REVIEW"
        summary = _summary_from_df(portfolio_df, name="Actual Runtime Replay Portfolio")
        portfolio_curve_records = curve_records_from_df(portfolio_df)
    serializable_components = [
        {key: value for key, value in row.items() if key != "_result_df"}
        for row in component_outputs
    ]
    return {
        "replay_id": replay_id,
        "attempted_at": attempted_at,
        "source_id": source_row.get("selection_source_id"),
        "source_kind": source_row.get("source_kind"),
        "status": status,
        "elapsed_ms": elapsed_ms,
        "component_count": len(components),
        "successful_component_count": len(successful),
        "component_results": serializable_components,
        "portfolio_curve": portfolio_curve_records,
        "benchmark_curve": benchmark_curve_records,
        "benchmark_ticker": benchmark_ticker,
        "summary": summary,
        "notes": "Actual replay uses existing strategy runtime only. It is validation evidence, not live approval.",
    }
