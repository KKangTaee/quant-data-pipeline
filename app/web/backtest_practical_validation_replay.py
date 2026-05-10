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
from finance.loaders import load_latest_market_date
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
RECHECK_MODE_EXTEND_TO_LATEST = "extend_to_latest"
RECHECK_MODE_STORED_PERIOD = "stored_period"
RECHECK_MODE_LABELS = {
    RECHECK_MODE_EXTEND_TO_LATEST: "최신 DB 데이터까지 확장 검증",
    RECHECK_MODE_STORED_PERIOD: "저장 기간 그대로 재현",
}


def _now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _day_gap(start: Any, end: Any) -> int | None:
    start_ts = pd.to_datetime(start, errors="coerce")
    end_ts = pd.to_datetime(end, errors="coerce")
    if pd.isna(start_ts) or pd.isna(end_ts):
        return None
    return int((end_ts.normalize() - start_ts.normalize()).days)


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


def build_practical_validation_recheck_plan(
    source: dict[str, Any],
    *,
    mode: str = RECHECK_MODE_EXTEND_TO_LATEST,
    end_override: Any | None = None,
) -> dict[str, Any]:
    """Plan the runtime period before executing the Practical Validation recheck."""
    source_row = dict(source or {})
    normalized_mode = mode if mode in RECHECK_MODE_LABELS else RECHECK_MODE_EXTEND_TO_LATEST
    source_period = _source_period(source_row)
    stored_start = _date_text(source_period.get("actual_start") or source_period.get("start"))
    stored_end = _date_text(source_period.get("actual_end") or source_period.get("end"))
    latest_market_date: str | None = None
    latest_error: str | None = None
    if normalized_mode == RECHECK_MODE_EXTEND_TO_LATEST:
        try:
            latest_market_date = _date_text(load_latest_market_date(timeframe="1d"))
        except Exception as exc:
            latest_error = str(exc)

    override_end = _date_text(end_override)
    requested_end = stored_end
    if override_end:
        requested_end = override_end
    elif normalized_mode == RECHECK_MODE_EXTEND_TO_LATEST and latest_market_date:
        stored_gap = _day_gap(stored_end, latest_market_date)
        requested_end = latest_market_date if stored_gap is None or stored_gap > 0 else stored_end

    requested_start = stored_start
    extension_gap = _day_gap(stored_end, requested_end)
    extension_days = max(extension_gap or 0, 0)
    if not requested_start or not requested_end:
        status = "BLOCKED"
        status_reason = "source period가 부족해 runtime 재검증 기간을 만들 수 없습니다."
    elif normalized_mode == RECHECK_MODE_STORED_PERIOD:
        status = "STORED_PERIOD"
        status_reason = "저장 당시 source 기간 그대로 기존 runtime을 재실행합니다."
    elif latest_error:
        status = "REVIEW"
        status_reason = "최신 DB 시장일 조회에 실패해 저장 종료일 기준으로만 재실행합니다."
    elif extension_days > 0:
        status = "EXTENDED"
        status_reason = "저장 당시 종료일 이후 DB에 있는 최신 시장일까지 확장해 재검증합니다."
    else:
        status = "NO_NEWER_DB_DATA"
        status_reason = "저장 당시 종료일보다 더 최신인 DB 시장일이 없어 같은 종료일로 재검증합니다."

    return {
        "mode": normalized_mode,
        "mode_label": RECHECK_MODE_LABELS[normalized_mode],
        "status": status,
        "status_reason": status_reason,
        "stored_period": {
            "start": stored_start,
            "end": stored_end,
        },
        "requested_period": {
            "start": requested_start,
            "end": requested_end,
        },
        "latest_market_date": latest_market_date,
        "latest_market_date_error": latest_error,
        "extension_days": extension_days,
        "uses_latest_db_date": normalized_mode == RECHECK_MODE_EXTEND_TO_LATEST,
        "curve_source": (
            "actual_runtime_latest_recheck"
            if normalized_mode == RECHECK_MODE_EXTEND_TO_LATEST
            else "actual_runtime_replay"
        ),
    }


def _component_payload(
    source: dict[str, Any],
    component: dict[str, Any],
    *,
    period_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    period = _source_period(source)
    override_period = dict(period_override or {})
    replay_contract = dict(component.get("replay_contract") or {})
    payload: dict[str, Any] = {
        "start": override_period.get("start") or period.get("start") or period.get("actual_start"),
        "end": override_period.get("end") or period.get("end") or period.get("actual_end"),
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
    if override_period:
        payload["start"] = override_period.get("start") or override_period.get("actual_start") or payload.get("start")
        payload["end"] = override_period.get("end") or override_period.get("actual_end") or payload.get("end")
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


def _period_coverage_rows(
    component_outputs: list[dict[str, Any]],
    *,
    requested_end: Any,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in component_outputs:
        actual_end = _date_text(row.get("actual_end"))
        requested = _date_text(row.get("requested_end") or requested_end)
        gap_days = max(_day_gap(actual_end, requested) or 0, 0)
        rows.append(
            {
                "Component": row.get("title") or row.get("component_id"),
                "Status": "PASS" if gap_days <= 7 else "REVIEW",
                "Requested End": requested or "-",
                "Actual End": actual_end or "-",
                "End Gap Days": gap_days,
                "Meaning": (
                    "요청한 최신 종료일과 거의 같은 기간까지 계산되었습니다."
                    if gap_days <= 7
                    else "요청한 최신 종료일보다 실제 결과가 짧습니다. cadence, signal interval, component date alignment를 확인해야 합니다."
                ),
            }
        )
    return rows


def _period_coverage(
    *,
    summary: dict[str, Any],
    requested_period: dict[str, Any],
    component_outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    requested_end = _date_text(requested_period.get("end"))
    actual_start = _date_text(summary.get("start_date"))
    actual_end = _date_text(summary.get("end_date"))
    end_gap_days = max(_day_gap(actual_end, requested_end) or 0, 0)
    rows = _period_coverage_rows(component_outputs, requested_end=requested_end)
    status = "PASS" if end_gap_days <= 7 else "REVIEW"
    return {
        "status": status,
        "summary": (
            "runtime curve가 요청 종료일과 거의 같은 기간까지 계산되었습니다."
            if status == "PASS"
            else "runtime 실행은 성공했지만 실제 portfolio curve 종료일이 요청 종료일보다 짧습니다."
        ),
        "requested_period": {
            "start": _date_text(requested_period.get("start")),
            "end": requested_end,
        },
        "actual_period": {
            "start": actual_start,
            "end": actual_end,
        },
        "end_gap_days": end_gap_days,
        "component_rows": rows,
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


def run_practical_validation_actual_replay(
    source: dict[str, Any],
    *,
    mode: str = RECHECK_MODE_EXTEND_TO_LATEST,
    end_override: Any | None = None,
) -> dict[str, Any]:
    """Recheck a Practical Validation source through existing strategy runtime without adding strategies."""
    source_row = dict(source or {})
    recheck_plan = build_practical_validation_recheck_plan(source_row, mode=mode, end_override=end_override)
    components = [
        dict(component or {})
        for component in list(source_row.get("components") or [])
        if (optional_float(dict(component or {}).get("target_weight")) or 0.0) > 0.0
    ]
    started = time.perf_counter()
    attempted_at = _now_text()
    replay_id = f"pv_recheck_{uuid4().hex[:12]}"
    component_outputs: list[dict[str, Any]] = []
    benchmark_curve_records: list[dict[str, Any]] = []
    benchmark_ticker = "-"
    requested_period = dict(recheck_plan.get("requested_period") or {})

    if recheck_plan.get("status") == "BLOCKED":
        return {
            "replay_id": replay_id,
            "attempted_at": attempted_at,
            "source_id": source_row.get("selection_source_id"),
            "source_kind": source_row.get("source_kind"),
            "status": "BLOCKED",
            "elapsed_ms": round((time.perf_counter() - started) * 1000.0, 3),
            "component_count": len(components),
            "successful_component_count": 0,
            "component_results": [],
            "portfolio_curve": [],
            "benchmark_curve": [],
            "benchmark_ticker": benchmark_ticker,
            "summary": {},
            "recheck_plan": recheck_plan,
            "recheck_mode": recheck_plan.get("mode"),
            "stored_period": recheck_plan.get("stored_period"),
            "requested_period": recheck_plan.get("requested_period"),
            "actual_period": {},
            "period_coverage": {
                "status": "BLOCKED",
                "summary": recheck_plan.get("status_reason"),
                "requested_period": recheck_plan.get("requested_period"),
                "actual_period": {},
                "end_gap_days": None,
                "component_rows": [],
            },
            "curve_source": recheck_plan.get("curve_source"),
            "notes": recheck_plan.get("status_reason"),
        }

    for index, component in enumerate(components):
        title = str(component.get("title") or component.get("strategy_name") or f"Component {index + 1}")
        payload = _component_payload(source_row, component, period_override=requested_period)
        component_id = str(component.get("component_id") or component.get("registry_id") or f"component_{index + 1}")
        if not payload.get("strategy_key"):
            component_outputs.append(
                {
                    "component_id": component_id,
                    "title": title,
                    "target_weight": optional_float(component.get("target_weight")) or 0.0,
                    "strategy_key": "-",
                    "status": "NOT_RUN",
                    "requested_start": payload.get("start"),
                    "requested_end": payload.get("end"),
                    "error": "strategy_key를 확인할 수 없어 runtime 재검증을 건너뜁니다.",
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
                    "requested_start": payload.get("start"),
                    "requested_end": payload.get("end"),
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
                    "requested_start": payload.get("start"),
                    "requested_end": payload.get("end"),
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
        period_coverage = {
            "status": "NOT_RUN",
            "summary": "portfolio curve가 없어 실제 기간 coverage를 확인하지 못했습니다.",
            "requested_period": requested_period,
            "actual_period": {},
            "end_gap_days": None,
            "component_rows": _period_coverage_rows(component_outputs, requested_end=requested_period.get("end")),
        }
    else:
        status = "PASS" if len(successful) == len(components) else "REVIEW"
        summary = _summary_from_df(
            portfolio_df,
            name=(
                "Latest Runtime Recheck Portfolio"
                if recheck_plan.get("mode") == RECHECK_MODE_EXTEND_TO_LATEST
                else "Stored Period Runtime Replay Portfolio"
            ),
        )
        portfolio_curve_records = curve_records_from_df(portfolio_df)
        period_coverage = _period_coverage(
            summary=summary,
            requested_period=requested_period,
            component_outputs=component_outputs,
        )
        if status == "PASS" and period_coverage.get("status") == "REVIEW":
            status = "REVIEW"
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
        "recheck_plan": recheck_plan,
        "recheck_mode": recheck_plan.get("mode"),
        "recheck_mode_label": recheck_plan.get("mode_label"),
        "stored_period": recheck_plan.get("stored_period"),
        "requested_period": recheck_plan.get("requested_period"),
        "actual_period": period_coverage.get("actual_period"),
        "period_coverage": period_coverage,
        "latest_market_date": recheck_plan.get("latest_market_date"),
        "extension_days": recheck_plan.get("extension_days"),
        "curve_source": recheck_plan.get("curve_source"),
        "notes": (
            "Runtime recheck uses existing strategy runtime only. "
            "It is validation evidence, not live approval."
        ),
    }
