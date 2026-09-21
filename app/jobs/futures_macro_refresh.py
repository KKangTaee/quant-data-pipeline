"""Bounded current-data refresh for the Futures Macro tab; no forecast research."""

from datetime import datetime, timezone
from time import perf_counter

from app.jobs.ingestion_jobs import run_collect_futures_ohlcv
from app.jobs.futures_macro_daily_finalization import (
    run_pending_futures_daily_finalization,
)
from app.services.futures_macro_inputs import load_futures_macro_windows
from app.services.futures_macro_observation_snapshot import (
    materialize_futures_macro_observation_snapshot,
)
from app.services.futures_macro_intraday import active_futures_session_date
from app.services.futures_macro_windows import utc
from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS
from finance.loaders.futures import load_futures_daily_coverage


def _daily_refresh_needed(*, symbols, evaluation_time, snapshot):
    """Use stored daily coverage; this button never bootstraps ten years of research."""
    anchor = snapshot.get("windows", {}).get("since_close", {}).get("start_utc")
    if not anchor:
        return False
    coverage = {r["provider_symbol"]: r for r in load_futures_daily_coverage(symbols)}
    target = utc(anchor).date()
    return any(
        not coverage.get(s, {}).get("latest_daily_candle")
        or utc(coverage[s]["latest_daily_candle"]).date() < target
        for s in symbols
    )


def run_futures_macro_observation_refresh(
    *,
    evaluation_time=None,
    window_loader=None,
    collect_runner=None,
    daily_refresh_needed=None,
    finalization_runner=None,
    materialize_fn=None,
):
    """Fetch recent bars once, then at most two bounded missing-anchor backfills."""
    clock = perf_counter()
    now = utc(evaluation_time or datetime.now(timezone.utc))
    load = window_loader or load_futures_macro_windows
    collect = collect_runner or run_collect_futures_ohlcv
    symbols = list(DEFAULT_CORE_FUTURES_SYMBOLS)
    attempts, errors = [], []
    snapshot = load(evaluation_time=now)

    def attempt(selected, period, interval):
        try:
            result = collect(
                symbols=selected,
                period=period,
                interval=interval,
                materialize_snapshot=False,
            )
        except Exception as exc:
            result = {"status": "failed", "rows_written": 0, "message": str(exc)}
        attempts.append(result)
        if result.get("status") != "success":
            errors.append(result.get("message") or "일부 선물 자료를 받지 못했습니다.")
        return result

    latest_intraday = {"status": "success", "rows_written": 0}
    if active_futures_session_date(now) is not None:
        latest_intraday = attempt(symbols, "2d", "5m")
        snapshot = load(evaluation_time=now)
    for period in ("5d", "1mo"):
        missing = sorted(
            {
                s
                for w in snapshot["windows"].values()
                for s in w.get("missing_symbols", [])
            }
        )
        if not missing:
            break
        attempt(missing, period, "5m")
        snapshot = load(evaluation_time=now)
    daily, finalized, materialized = None, {}, {}
    try:
        if (daily_refresh_needed or _daily_refresh_needed)(
            symbols=symbols, evaluation_time=now, snapshot=snapshot
        ):
            daily = attempt(symbols, "1mo", "1d")
        # Reuse the initial full-universe collection; finalization must not launch another fetch.
        finalized = (finalization_runner or run_pending_futures_daily_finalization)(
            symbols=symbols,
            evaluation_time=now,
            collect_runner=collect,
            intraday_collection_result=latest_intraday,
        )
        materialized = (
            materialize_fn or materialize_futures_macro_observation_snapshot
        )(evaluation_time=now)
        if materialized.get("status") not in {"materialized", "reused", "kept_newer"}:
            errors.append("공유 일별 관측을 저장하지 못했습니다.")
        if (
            finalized.get("status") in {"incomplete", "error"}
            and finalized.get("reason") != "future_session_not_eligible"
        ):
            errors.append("완료 일봉 확정에 필요한 자료가 부족합니다.")
    except Exception as exc:
        errors.append(str(exc))
    usable = any(
        w.get("status") in {"AVAILABLE", "MARKET_CLOSED"}
        for w in snapshot["windows"].values()
    )
    complete = all(
        w.get("status") in {"AVAILABLE", "MARKET_CLOSED"}
        for w in snapshot["windows"].values()
    )
    status = (
        "success"
        if complete and not errors
        else "partial_success"
        if usable
        else "failed"
    )
    return {
        "job_name": "futures_macro_observation_refresh",
        "status": status,
        "duration_sec": round(perf_counter() - clock, 3),
        "rows_written": sum(int(r.get("rows_written") or 0) for r in attempts),
        "message": "저장 자료를 다시 확인했습니다."
        if status == "success"
        else "일부 비교 자료가 부족합니다. 관측 시각과 누락 항목을 확인해 주세요.",
        "details": {
            "windows": snapshot["windows"],
            "attempts": attempts,
            "errors": errors,
            "daily_finalization": finalized,
            "observation": materialized,
        },
    }
