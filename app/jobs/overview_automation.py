from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Iterable, Sequence
from zoneinfo import ZoneInfo

from app.jobs.ingestion_jobs import (
    JobResult,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_macro_calendar,
    run_collect_market_intraday_snapshot,
    run_collect_sp500_valuation_context,
    run_collect_sp500_universe,
    run_collect_symbol_directory_snapshots,
)
from app.jobs.run_history import append_run_history, load_run_history
from app.workspace_paths import RUN_ARTIFACT_DIR

US_MARKET_TZ = ZoneInfo("America/New_York")
LOCK_FILE = RUN_ARTIFACT_DIR / "locks" / "overview_automation.lock"
LOCK_STALE_AFTER_MINUTES = 90
ACCEPTED_CADENCE_STATUSES = {"success", "partial_success"}


@dataclass(frozen=True)
class ScheduledJobSpec:
    job_id: str
    job_name: str
    label: str
    cadence_minutes: int
    profiles: tuple[str, ...]
    market_hours_only: bool
    runner: Callable[[datetime], JobResult]
    description: str


def _now_str(value: datetime | None = None) -> str:
    return (value or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")


def _parse_history_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:19], fmt)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.replace(tzinfo=None)


def _as_local_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone().replace(tzinfo=None)


def _as_market_time(value: datetime) -> datetime:
    if value.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        value = value.replace(tzinfo=local_tz)
    return value.astimezone(US_MARKET_TZ)


def is_us_market_hours(value: datetime | None = None) -> bool:
    market_time = _as_market_time(value or datetime.now())
    if market_time.weekday() >= 5:
        return False
    return time(9, 30) <= market_time.time() <= time(16, 5)


def _run_sp500_universe(_: datetime) -> JobResult:
    return run_collect_sp500_universe()


def _run_nasdaq_symbol_directory(_: datetime) -> JobResult:
    return run_collect_symbol_directory_snapshots(sources=("nasdaqlisted",))


def _run_intraday_snapshot(
    universe_code: str,
    universe_limit: int,
    *,
    fallback_to_yfinance: bool,
) -> Callable[[datetime], JobResult]:
    def runner(_: datetime) -> JobResult:
        return run_collect_market_intraday_snapshot(
            universe_code=universe_code,
            universe_limit=universe_limit,
            interval="5m",
            chunk_size=100,
            quote_batch_size=200,
            method="quote_fast",
            fallback_to_yfinance=fallback_to_yfinance,
        )

    return runner


def _run_fomc_calendar(value: datetime) -> JobResult:
    current_year = value.year
    return run_collect_fomc_calendar(years=(current_year, current_year + 1))


def _run_macro_calendar(value: datetime) -> JobResult:
    current_year = value.year
    return run_collect_macro_calendar(years=(current_year, current_year + 1))


def _run_earnings_calendar(_: datetime) -> JobResult:
    return run_collect_earnings_calendar(
        symbol_source="latest_movers",
        universe_code="SP500",
        top_movers_limit=20,
        lookahead_days=120,
        max_symbols=50,
        validate_with_nasdaq=True,
    )


def _run_sp500_valuation(_: datetime) -> JobResult:
    return run_collect_sp500_valuation_context(
        index_earnings_path=os.getenv("SP500_INDEX_EARNINGS_PATH") or None,
        source_release_date=os.getenv("SP500_INDEX_EARNINGS_RELEASE_DATE") or None,
    )


OVERVIEW_AUTOMATION_JOB_SPECS: tuple[ScheduledJobSpec, ...] = (
    ScheduledJobSpec(
        job_id="sp500_universe",
        job_name="collect_sp500_universe",
        label="S&P 500 Universe",
        cadence_minutes=24 * 60,
        profiles=("safe", "standard", "broad"),
        market_hours_only=False,
        runner=_run_sp500_universe,
        description="Refresh current S&P 500 membership for Overview market intelligence.",
    ),
    ScheduledJobSpec(
        job_id="nasdaq_symbol_directory",
        job_name="collect_symbol_directory_snapshots",
        label="Nasdaq Symbol Directory",
        cadence_minutes=24 * 60,
        profiles=("safe", "standard", "broad"),
        market_hours_only=False,
        runner=_run_nasdaq_symbol_directory,
        description="Refresh Nasdaq-listed current Symbol Directory snapshot for Overview coverage.",
    ),
    ScheduledJobSpec(
        job_id="sp500_intraday",
        job_name="collect_sp500_intraday_snapshot",
        label="S&P 500 Daily Snapshot",
        cadence_minutes=5,
        profiles=("safe", "standard", "broad", "intraday", "browser_safe"),
        market_hours_only=True,
        runner=_run_intraday_snapshot("SP500", 500, fallback_to_yfinance=True),
        description="Collect S&P 500 quote-fast daily movers snapshot during US market hours.",
    ),
    ScheduledJobSpec(
        job_id="top1000_intraday",
        job_name="collect_top1000_intraday_snapshot",
        label="Top1000 Daily Snapshot",
        cadence_minutes=15,
        profiles=("standard", "broad", "intraday"),
        market_hours_only=True,
        runner=_run_intraday_snapshot("TOP1000", 1000, fallback_to_yfinance=False),
        description="Collect Top1000 quote-fast daily movers snapshot during US market hours.",
    ),
    ScheduledJobSpec(
        job_id="top2000_intraday",
        job_name="collect_top2000_intraday_snapshot",
        label="Top2000 Daily Snapshot",
        cadence_minutes=30,
        profiles=("standard", "broad", "intraday"),
        market_hours_only=True,
        runner=_run_intraday_snapshot("TOP2000", 2000, fallback_to_yfinance=False),
        description="Collect Top2000 quote-fast daily movers snapshot during US market hours.",
    ),
    ScheduledJobSpec(
        job_id="nasdaq_intraday",
        job_name="collect_nasdaq_intraday_snapshot",
        label="Nasdaq-listed Daily Snapshot",
        cadence_minutes=30,
        profiles=("standard", "broad", "intraday"),
        market_hours_only=True,
        runner=_run_intraday_snapshot("NASDAQ", 5000, fallback_to_yfinance=False),
        description="Collect Nasdaq-listed quote-fast daily movers snapshot during US market hours.",
    ),
    ScheduledJobSpec(
        job_id="sp500_valuation",
        job_name="collect_sp500_valuation_context",
        label="S&P 500 Valuation Context",
        cadence_minutes=24 * 60,
        profiles=("safe", "standard", "broad"),
        market_hours_only=False,
        runner=_run_sp500_valuation,
        description="Discover the newest SEP vintage and refresh Shiller plus SPX/SPY valuation inputs.",
    ),
    ScheduledJobSpec(
        job_id="fomc_calendar",
        job_name="collect_fomc_calendar",
        label="FOMC Calendar",
        cadence_minutes=24 * 60,
        profiles=("safe", "standard", "broad", "events"),
        market_hours_only=False,
        runner=_run_fomc_calendar,
        description="Refresh FOMC event rows from the official Federal Reserve calendar.",
    ),
    ScheduledJobSpec(
        job_id="macro_calendar",
        job_name="collect_macro_calendar",
        label="Macro Calendar",
        cadence_minutes=24 * 60,
        profiles=("safe", "standard", "broad", "events"),
        market_hours_only=False,
        runner=_run_macro_calendar,
        description="Refresh official BLS / BEA macro release calendar rows.",
    ),
    ScheduledJobSpec(
        job_id="earnings_calendar",
        job_name="collect_earnings_calendar",
        label="Earnings Calendar",
        cadence_minutes=24 * 60,
        profiles=("safe", "standard", "broad", "events"),
        market_hours_only=False,
        runner=_run_earnings_calendar,
        description="Refresh bounded upcoming earnings for latest S&P 500 movers.",
    ),
)

VALID_PROFILES = tuple(sorted({profile for spec in OVERVIEW_AUTOMATION_JOB_SPECS for profile in spec.profiles}))


def _select_specs(
    *,
    profile: str,
    job_ids: Iterable[str] | None = None,
    specs: Sequence[ScheduledJobSpec] = OVERVIEW_AUTOMATION_JOB_SPECS,
) -> list[ScheduledJobSpec]:
    normalized_profile = str(profile or "standard").strip().lower()
    requested = {str(item).strip().lower() for item in (job_ids or []) if str(item).strip()}
    selected = [
        spec
        for spec in specs
        if normalized_profile in spec.profiles
        and (not requested or spec.job_id.lower() in requested or spec.job_name.lower() in requested)
    ]
    return selected


def _latest_accepted_history(
    job_name: str,
    history_rows: Sequence[dict[str, Any]],
    accepted_statuses: set[str] = ACCEPTED_CADENCE_STATUSES,
) -> dict[str, Any] | None:
    for row in history_rows:
        if row.get("job_name") != job_name:
            continue
        if str(row.get("status") or "").lower() not in accepted_statuses:
            continue
        return row
    return None


def build_overview_automation_plan(
    *,
    profile: str = "standard",
    job_ids: Iterable[str] | None = None,
    history_rows: Sequence[dict[str, Any]] | None = None,
    now: datetime | None = None,
    force: bool = False,
    allow_outside_market_hours: bool = False,
    specs: Sequence[ScheduledJobSpec] = OVERVIEW_AUTOMATION_JOB_SPECS,
) -> list[dict[str, Any]]:
    now_value = now or datetime.now()
    now_local = _as_local_naive(now_value)
    history = list(history_rows or [])
    selected_specs = _select_specs(profile=profile, job_ids=job_ids, specs=specs)
    market_is_open = is_us_market_hours(now_value)

    rows: list[dict[str, Any]] = []
    for spec in selected_specs:
        latest = _latest_accepted_history(spec.job_name, history)
        latest_finished = _parse_history_datetime((latest or {}).get("finished_at"))
        next_due_at = (
            latest_finished + timedelta(minutes=max(1, spec.cadence_minutes))
            if latest_finished is not None
            else None
        )
        due_by_cadence = latest_finished is None or now_local >= (next_due_at or now_local)
        market_blocked = spec.market_hours_only and not market_is_open and not allow_outside_market_hours
        should_run = bool(force or (due_by_cadence and not market_blocked))
        if force:
            reason = "forced"
        elif market_blocked:
            reason = "outside US market hours"
        elif due_by_cadence:
            reason = "due"
        else:
            reason = "cadence not due"

        rows.append(
            {
                "job_id": spec.job_id,
                "job_name": spec.job_name,
                "label": spec.label,
                "cadence_minutes": spec.cadence_minutes,
                "market_hours_only": spec.market_hours_only,
                "last_finished_at": (latest or {}).get("finished_at"),
                "next_due_at": _now_str(next_due_at) if next_due_at else None,
                "should_run": should_run,
                "reason": reason,
                "description": spec.description,
            }
        )
    return rows


class OverviewAutomationLock:
    def __init__(
        self,
        path: Path = LOCK_FILE,
        *,
        stale_after_minutes: int = LOCK_STALE_AFTER_MINUTES,
        now: datetime | None = None,
    ) -> None:
        self.path = path
        self.stale_after_minutes = stale_after_minutes
        self.now = now or datetime.now()
        self._fd: int | None = None

    def __enter__(self) -> "OverviewAutomationLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and self._is_stale():
            self.path.unlink(missing_ok=True)
        try:
            self._fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RuntimeError(f"Overview automation lock is already held: {self.path}") from exc
        payload = json.dumps(
            {
                "pid": os.getpid(),
                "created_at": _now_str(self.now),
                "stale_after_minutes": self.stale_after_minutes,
            },
            ensure_ascii=False,
        )
        os.write(self._fd, payload.encode("utf-8"))
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self.path.unlink(missing_ok=True)

    def _is_stale(self) -> bool:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            created_at = _parse_history_datetime(payload.get("created_at"))
        except Exception:
            created_at = None
        if created_at is None:
            return True
        return _as_local_naive(self.now) - created_at > timedelta(minutes=max(1, self.stale_after_minutes))


def _automation_context_prefix(execution_mode: str) -> str:
    normalized = str(execution_mode or "").strip().lower()
    if normalized == "browser_auto":
        return "Browser-session Overview automation"
    return "Scheduled Overview automation"


def _with_automation_metadata(
    result: JobResult,
    *,
    profile: str,
    spec: ScheduledJobSpec,
    plan_row: dict[str, Any],
    execution_mode: str,
) -> JobResult:
    out = dict(result)
    normalized_execution_mode = str(execution_mode or "scheduled").strip().lower() or "scheduled"
    metadata = dict(out.get("run_metadata") or {})
    input_params = dict(metadata.get("input_params") or {})
    input_params.update(
        {
            "automation_profile": profile,
            "automation_job_id": spec.job_id,
            "cadence_minutes": spec.cadence_minutes,
            "market_hours_only": spec.market_hours_only,
        }
    )
    metadata.update(
        {
            "execution_mode": normalized_execution_mode,
            "automation_profile": profile,
            "automation_job_id": spec.job_id,
            "input_params": input_params,
            "execution_context": f"{_automation_context_prefix(normalized_execution_mode)}: {spec.description}",
        }
    )
    out["run_metadata"] = metadata
    details = dict(out.get("details") or {})
    details["automation"] = {
        "profile": profile,
        "job_id": spec.job_id,
        "execution_mode": normalized_execution_mode,
        "cadence_minutes": spec.cadence_minutes,
        "planned_reason": plan_row.get("reason"),
    }
    out["details"] = details
    return out


def _overall_status(results: Sequence[JobResult], *, skipped: bool = False) -> str:
    if skipped:
        return "skipped"
    if not results:
        return "skipped"
    statuses = {str(result.get("status") or "").lower() for result in results}
    if statuses <= {"success"}:
        return "success"
    if "success" in statuses or "partial_success" in statuses:
        return "partial_success"
    return "failed"


def run_overview_automation(
    *,
    profile: str = "standard",
    job_ids: Iterable[str] | None = None,
    dry_run: bool = False,
    force: bool = False,
    allow_outside_market_hours: bool = False,
    lock_path: Path = LOCK_FILE,
    now: datetime | None = None,
    history_rows: Sequence[dict[str, Any]] | None = None,
    history_loader: Callable[..., list[dict[str, Any]]] = load_run_history,
    history_appender: Callable[[dict[str, Any]], None] = append_run_history,
    specs: Sequence[ScheduledJobSpec] = OVERVIEW_AUTOMATION_JOB_SPECS,
    execution_mode: str = "scheduled",
) -> dict[str, Any]:
    started_at = _now_str(now)
    t0 = perf_counter()
    now_value = now or datetime.now()
    normalized_profile = str(profile or "standard").strip().lower()
    normalized_execution_mode = str(execution_mode or "scheduled").strip().lower() or "scheduled"
    if history_rows is None:
        history = history_loader(limit=500)
    else:
        history = list(history_rows)
    plan = build_overview_automation_plan(
        profile=normalized_profile,
        job_ids=job_ids,
        history_rows=history,
        now=now_value,
        force=force,
        allow_outside_market_hours=allow_outside_market_hours,
        specs=specs,
    )
    spec_by_id = {spec.job_id: spec for spec in _select_specs(profile=normalized_profile, job_ids=job_ids, specs=specs)}
    due_rows = [row for row in plan if row.get("should_run")]

    if dry_run or not due_rows:
        status = "dry_run" if dry_run else "skipped"
        return {
            "job_name": "overview_automation",
            "status": status,
            "profile": normalized_profile,
            "execution_mode": normalized_execution_mode,
            "started_at": started_at,
            "finished_at": _now_str(),
            "duration_sec": round(perf_counter() - t0, 3),
            "market_hours_open": is_us_market_hours(now_value),
            "jobs_due": len(due_rows),
            "jobs_run": 0,
            "plan": plan,
            "results": [],
        }

    results: list[JobResult] = []
    with OverviewAutomationLock(lock_path, now=now_value):
        for row in due_rows:
            spec = spec_by_id.get(str(row["job_id"]))
            if spec is None:
                continue
            try:
                result = spec.runner(now_value)
            except Exception as exc:
                finished_at = _now_str()
                result = {
                    "job_name": spec.job_name,
                    "status": "failed",
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "duration_sec": 0,
                    "rows_written": 0,
                    "symbols_requested": None,
                    "symbols_processed": None,
                    "failed_symbols": [],
                    "message": f"Overview automation job failed: {exc}",
                    "details": {"automation_job_id": spec.job_id},
                }
            annotated = _with_automation_metadata(
                result,
                profile=normalized_profile,
                spec=spec,
                plan_row=row,
                execution_mode=normalized_execution_mode,
            )
            history_appender(annotated)
            results.append(annotated)

    status = _overall_status(results)
    return {
        "job_name": "overview_automation",
        "status": status,
        "profile": normalized_profile,
        "execution_mode": normalized_execution_mode,
        "started_at": started_at,
        "finished_at": _now_str(),
        "duration_sec": round(perf_counter() - t0, 3),
        "market_hours_open": is_us_market_hours(now_value),
        "jobs_due": len(due_rows),
        "jobs_run": len(results),
        "plan": plan,
        "results": results,
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return _now_str(value)
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _print_text_summary(summary: dict[str, Any]) -> None:
    print(f"Overview automation: {summary.get('status')} profile={summary.get('profile')}")
    print(f"Market hours open: {summary.get('market_hours_open')}")
    print(f"Jobs due/run: {summary.get('jobs_due')} / {summary.get('jobs_run')}")
    for row in summary.get("plan") or []:
        marker = "RUN" if row.get("should_run") else "SKIP"
        print(f"- {marker} {row.get('job_id')}: {row.get('reason')}")
    for result in summary.get("results") or []:
        print(f"  result {result.get('job_name')}: {result.get('status')} - {result.get('message')}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run browser-independent Overview market intelligence automation.")
    parser.add_argument("--profile", default="standard", choices=VALID_PROFILES, help="Automation profile to evaluate.")
    parser.add_argument("--job", action="append", dest="job_ids", help="Limit run to one job_id or job_name. Repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Only print the due/skip plan; do not collect data.")
    parser.add_argument("--force", action="store_true", help="Run selected jobs regardless of cadence and market-hours guard.")
    parser.add_argument(
        "--allow-outside-market-hours",
        action="store_true",
        help="Allow intraday snapshot jobs outside US market hours while keeping cadence checks.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary.")
    args = parser.parse_args(argv)

    try:
        summary = run_overview_automation(
            profile=args.profile,
            job_ids=args.job_ids,
            dry_run=args.dry_run,
            force=args.force,
            allow_outside_market_hours=args.allow_outside_market_hours,
        )
    except RuntimeError as exc:
        error_summary = {
            "job_name": "overview_automation",
            "status": "locked",
            "message": str(exc),
        }
        if args.json:
            print(json.dumps(error_summary, ensure_ascii=False, indent=2, default=_json_safe))
        else:
            print(f"Overview automation locked: {exc}")
        return 75

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, default=_json_safe))
    else:
        _print_text_summary(summary)
    if summary.get("status") == "failed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
