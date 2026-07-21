from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from app.jobs.ingestion_jobs import JobResult, run_collect_ohlcv
from app.services.nyse_calendar import latest_completed_nyse_session
from finance.loaders import load_price_freshness_summary


ACTIVE_ITEM_STATUSES = {"active", "data_review"}
DIRECT_INSTRUMENT_KINDS = {"stock", "etf"}
PRICE_REFRESH_OVERLAP_DAYS = 7


def _normalized_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _date_value(value: Any) -> date | None:
    if value in (None, ""):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _eligible_items(items: Iterable[Any]) -> tuple[list[Any], int]:
    eligible: list[Any] = []
    excluded_strategy_count = 0
    for item in items:
        status = str(getattr(item, "status", "") or "").strip().lower()
        if status not in ACTIVE_ITEM_STATUSES:
            continue
        source_type = str(getattr(item, "source_type", "") or "").strip().lower()
        kind = str(getattr(item, "instrument_kind", "") or "").strip().lower()
        if source_type == "selected_strategy":
            excluded_strategy_count += 1
            continue
        if source_type != "direct_security" or kind not in DIRECT_INSTRUMENT_KINDS:
            continue
        if _normalized_symbol(getattr(item, "source_ref", None)):
            eligible.append(item)
    return eligible, excluded_strategy_count


def _symbol_items(items: Iterable[Any]) -> tuple[list[str], dict[str, list[Any]]]:
    symbols: list[str] = []
    by_symbol: dict[str, list[Any]] = {}
    for item in items:
        symbol = _normalized_symbol(getattr(item, "source_ref", None))
        if not symbol:
            continue
        if symbol not in by_symbol:
            symbols.append(symbol)
            by_symbol[symbol] = []
        by_symbol[symbol].append(item)
    return symbols, by_symbol


def _freshness_dates(frame: Any) -> dict[str, date]:
    if frame is None or not isinstance(frame, pd.DataFrame) or frame.empty:
        return {}
    if "symbol" not in frame or "latest_date" not in frame:
        return {}
    dates: dict[str, date] = {}
    for row in frame.to_dict("records"):
        symbol = _normalized_symbol(row.get("symbol"))
        latest_date = _date_value(row.get("latest_date"))
        if symbol and latest_date is not None:
            dates[symbol] = latest_date
    return dates


def _unavailable_plan(*, target_date: date, excluded_strategy_count: int) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "eligible": False,
        "target_date": target_date.isoformat(),
        "current_common_latest": None,
        "symbols": [],
        "stale_symbols": [],
        "missing_symbols": [],
        "excluded_strategy_count": excluded_strategy_count,
        "collection_start": None,
        "collection_end": target_date.isoformat(),
        "button_label": "보유 종목 가격 최신화",
        "rows": [],
        "message": "현재 그룹에 최신화할 활성 개별 주식·ETF가 없습니다.",
    }


def build_portfolio_price_refresh_plan(
    items: Iterable[Any],
    *,
    now: datetime | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    """Project one selected group's direct-security price refresh action."""

    target_date = latest_completed_nyse_session(now)
    eligible_items, excluded_strategy_count = _eligible_items(items)
    symbols, items_by_symbol = _symbol_items(eligible_items)
    if not symbols:
        return _unavailable_plan(
            target_date=target_date,
            excluded_strategy_count=excluded_strategy_count,
        )

    loader = freshness_loader or load_price_freshness_summary
    frame = loader(symbols, end=target_date.isoformat(), timeframe="1d")
    latest_by_symbol = _freshness_dates(frame)
    rows: list[dict[str, Any]] = []
    stale_symbols: list[str] = []
    missing_symbols: list[str] = []
    available_dates: list[date] = []
    for symbol in symbols:
        latest_date = latest_by_symbol.get(symbol)
        if latest_date is None:
            state = "missing"
            missing_symbols.append(symbol)
        elif latest_date < target_date:
            state = "stale"
            stale_symbols.append(symbol)
            available_dates.append(latest_date)
        else:
            state = "current"
            available_dates.append(latest_date)
        rows.append(
            {
                "symbol": symbol,
                "latest_date": latest_date.isoformat() if latest_date else None,
                "status": state,
            }
        )

    current_common_latest = min(available_dates).isoformat() if available_dates else None
    unresolved_symbols = stale_symbols + missing_symbols
    if not unresolved_symbols:
        return {
            "status": "up_to_date",
            "eligible": False,
            "target_date": target_date.isoformat(),
            "current_common_latest": current_common_latest,
            "symbols": symbols,
            "stale_symbols": [],
            "missing_symbols": [],
            "excluded_strategy_count": excluded_strategy_count,
            "collection_start": None,
            "collection_end": target_date.isoformat(),
            "button_label": "보유 종목 가격 최신화",
            "rows": rows,
            "message": f"활성 개별 종목 가격이 최근 완료 거래일 {target_date.isoformat()} 기준으로 최신입니다.",
        }

    start_candidates: list[date] = []
    for symbol in stale_symbols:
        start_candidates.append(latest_by_symbol[symbol] - timedelta(days=PRICE_REFRESH_OVERLAP_DAYS))
    for symbol in missing_symbols:
        effective_dates = [
            _date_value(getattr(item, "effective_start_date", None))
            for item in items_by_symbol[symbol]
        ]
        start_candidates.extend(value for value in effective_dates if value is not None)
    collection_start = min(start_candidates) if start_candidates else target_date - timedelta(days=PRICE_REFRESH_OVERLAP_DAYS)
    display_rows = [row for row in rows if row["status"] != "current"]
    return {
        "status": "refresh_available",
        "eligible": True,
        "target_date": target_date.isoformat(),
        "current_common_latest": current_common_latest,
        "symbols": symbols,
        "stale_symbols": stale_symbols,
        "missing_symbols": missing_symbols,
        "excluded_strategy_count": excluded_strategy_count,
        "collection_start": min(collection_start, target_date).isoformat(),
        "collection_end": target_date.isoformat(),
        "button_label": "보유 종목 가격 최신화",
        "rows": rows,
        "message": (
            f"{len(display_rows)}개 종목의 일봉을 최근 완료 거래일 "
            f"{target_date.isoformat()}까지 최신화할 수 있습니다."
        ),
    }


def run_portfolio_price_refresh(
    items: Iterable[Any],
    *,
    now: datetime | None = None,
    freshness_loader: Callable[..., pd.DataFrame] | None = None,
    runner: Callable[..., JobResult] | None = None,
) -> JobResult:
    """Refresh one group's direct-security daily rows and verify DB freshness."""

    item_rows = list(items)
    plan = build_portfolio_price_refresh_plan(
        item_rows,
        now=now,
        freshness_loader=freshness_loader,
    )
    run_metadata = {
        "pipeline_type": "portfolio_monitoring_price_refresh",
        "execution_mode": "user_action",
        "symbol_source": "selected_portfolio_group",
        "symbol_count": len(plan.get("symbols") or []),
        "input_params": {
            "start": plan.get("collection_start"),
            "end": plan.get("collection_end"),
            "interval": "1d",
        },
        "execution_context": (
            "Refresh active direct stock and ETF daily prices for the selected "
            "Portfolio Monitoring group."
        ),
    }
    if not plan.get("eligible"):
        now_text = datetime.now().isoformat(timespec="seconds")
        return {
            "job_name": "portfolio_monitoring_price_refresh",
            "status": "skipped",
            "started_at": now_text,
            "finished_at": now_text,
            "rows_written": 0,
            "symbols_requested": len(plan.get("symbols") or []),
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": str(plan.get("message") or "최신화할 가격이 없습니다."),
            "details": {
                "plan": plan,
                "target_tables": ["finance_price.nyse_price_history"],
            },
            "run_metadata": run_metadata,
        }

    selected_runner = runner or run_collect_ohlcv
    result = dict(
        selected_runner(
            list(plan["symbols"]),
            start=plan.get("collection_start"),
            end=plan.get("collection_end"),
            period="1mo",
            interval="1d",
            execution_profile="managed_safe",
        )
    )
    post_refresh = build_portfolio_price_refresh_plan(
        item_rows,
        now=now,
        freshness_loader=freshness_loader,
    )
    unresolved = list(post_refresh.get("stale_symbols") or []) + list(
        post_refresh.get("missing_symbols") or []
    )
    rows_written = int(result.get("rows_written") or 0)
    if unresolved:
        status = "partial_success" if rows_written > 0 else "failed"
        sample = ", ".join(unresolved[:8])
        if len(unresolved) > 8:
            sample = f"{sample} 외 {len(unresolved) - 8}개"
        message = (
            f"일부 가격을 최신화했지만 {sample} 종목은 "
            f"{plan['target_date']} 기준에 도달하지 못했습니다."
            if rows_written > 0
            else f"{sample} 종목의 가격을 최신화하지 못했습니다."
        )
    else:
        status = "success"
        message = (
            f"활성 개별 종목 가격을 {plan['target_date']}까지 최신화했습니다. "
            "공통 기준일과 가치곡선을 다시 계산합니다."
        )

    details = dict(result.get("details") or {})
    details.update(
        {
            "plan": plan,
            "post_refresh": post_refresh,
            "post_refresh_unresolved_symbols": unresolved,
            "post_refresh_unresolved_count": len(unresolved),
            "target_tables": ["finance_price.nyse_price_history"],
            "source": "yfinance OHLCV",
            "purpose": "Portfolio Monitoring selected-group price freshness repair",
        }
    )
    result.update(
        {
            "job_name": "portfolio_monitoring_price_refresh",
            "status": status,
            "rows_written": rows_written,
            "symbols_requested": len(plan["symbols"]),
            "symbols_processed": max(
                len(plan["symbols"]) - len(unresolved),
                0,
            ),
            "failed_symbols": unresolved,
            "message": message,
            "details": details,
            "run_metadata": run_metadata,
        }
    )
    return result
