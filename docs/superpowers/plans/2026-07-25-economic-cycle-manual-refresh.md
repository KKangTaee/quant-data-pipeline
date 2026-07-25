# Economic Cycle Manual Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 로컬 FRED credential을 안전하게 로드하고, 경제사이클 화면이 최신 계산 가능 평일과 저장된 월중 결과를 비교해 사용자가 버튼으로 증분 수집·재계산할 수 있게 한다.

**Architecture:** Worktree-local `.env`는 공용 runtime helper가 `override=False`로 읽고 UI/CLI entrypoint가 이를 호출한다. 경제사이클 service는 DB snapshot으로만 freshness를 계산하며, explicit React/Streamlit event가 Overview action façade를 통해 기존 combined refresh pipeline을 실행하고 persisted target snapshot postcondition을 확인한다. UI render 자체는 계속 provider를 호출하지 않고 실패 시 last-good snapshot을 유지한다.

**Tech Stack:** Python 3.12, Streamlit, python-dotenv 1.1.1+, MySQL, pytest, React 18, TypeScript 5.7, Vite 6

## Global Constraints

- 세 로컬 파일은 `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.env`, `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/.env`, `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/.env`다.
- 사용자가 제공한 FRED API key는 `.env` 외의 tracked file, diff, task log, screenshot, shell output에 남기지 않는다.
- `dotenv.load_dotenv(..., override=False)`를 사용해 이미 주입된 process environment를 덮어쓰지 않는다.
- 2026-07-25 토요일의 economic-cycle target은 직전 평일 2026-07-24다.
- 화면 진입은 DB read-only이며 provider 수집은 `refresh_economic_cycle_data` explicit click에서만 실행한다.
- 기존 `run_economic_cycle_intramonth_refresh`의 17-series incremental collection, closed-month rollover, intramonth materialization 순서를 재사용한다.
- 성공은 persisted `intramonth_nowcast.as_of_date >= target_as_of_date` postcondition까지 필요하다.
- 실패 시 기존 monthly history와 last-good intramonth result를 유지한다.
- launchd, cron, timer, heartbeat, raw job/row/provider diagnostic panel은 추가하지 않는다.
- monthly `current`/`historical_replay` row는 rewrite하지 않고 필요한 closed-month row만 append할 수 있다.
- `.env`, run history, QA screenshot, unrelated dirty files는 commit하지 않는다.

---

## File Structure

### New files

- `app/runtime_env.py`: active worktree root `.env`를 process env 우선으로 로드하는 단일 책임 helper
- `app/services/overview/economic_cycle_freshness.py`: weekday target과 persisted intramonth date를 비교하는 pure adapter
- `tests/test_runtime_env.py`: missing file, successful load, process env precedence 검증
- `tests/test_economic_cycle_freshness.py`: weekday/weekend와 READY/REFRESH_AVAILABLE/MISSING/ERROR 검증

### Modified application files

- `.gitignore`: local environment file의 tracked 보호
- `app/web/streamlit_app.py`: Streamlit import graph가 provider job을 사용하기 전에 root `.env` 로드
- `app/jobs/overview_automation.py`: CLI `main()`에서 같은 root `.env` 로드
- `app/services/overview/economic_cycle.py`: `data_freshness`를 DB-only read model에 연결
- `app/jobs/overview_actions.py`: existing combined refresh를 감싸고 DB postcondition을 판정하는 explicit action façade
- `app/web/overview/market_context_helpers.py`: nonce 소비, progress, one-shot reflection, cache/rerun, fallback button
- `app/web/overview/economic_cycle_react_component.py`: component action payload를 Python으로 반환
- `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx`: compact freshness/action bar와 explicit event emit
- `app/web/streamlit_components/economic_cycle_workbench/src/style.css`: desktop/mobile action bar layout
- `app/web/streamlit_components/economic_cycle_workbench/component_static/`: Vite production build output

### Modified tests and durable docs

- `tests/test_economic_cycle_service.py`: service freshness attachment와 empty/error fallback
- `tests/test_economic_cycle_refresh.py`: Overview action target/postcondition/last-good contract
- `tests/test_market_context_economic_cycle.py`: event bridge, duplicate nonce, cache gate, React source/build contract
- `.aiworkspace/note/finance/docs/PROJECT_MAP.md`: economic-cycle UI의 explicit manual action boundary
- `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`: local `.env`, button flow, failure recovery
- `.aiworkspace/note/finance/docs/ROADMAP.md`: manual freshness action 완료 기록
- `.aiworkspace/note/finance/docs/INDEX.md`: 갱신된 runbook/current-state 안내 확인
- `.aiworkspace/note/finance/WORK_PROGRESS.md`: 3~5줄 handoff
- `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`: 요청·진단·결론 handoff
- `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725/`: task 상태, 실행 근거, 위험 갱신

---

### Task 1: Local secret protection and runtime loader

**Files:**
- Create: `app/runtime_env.py`
- Create: `tests/test_runtime_env.py`
- Modify: `.gitignore`
- Modify: `app/web/streamlit_app.py:10-16`
- Modify: `app/jobs/overview_automation.py:13-28,623-644`
- Local only: common Git directory `.git/info/exclude`
- Local only: the three worktree root `.env` files listed in Global Constraints

**Interfaces:**
- Consumes: `app.workspace_paths.PROJECT_ROOT`
- Produces: `load_project_local_env(project_root: Path | None = None) -> bool`

- [ ] **Step 1: Add failing runtime environment tests**

Create `tests/test_runtime_env.py` with exact behavior:

```python
from __future__ import annotations

import os
from pathlib import Path


def test_load_project_local_env_reads_root_file(
    tmp_path: Path, monkeypatch
) -> None:
    from app.runtime_env import load_project_local_env

    monkeypatch.delenv("FRED_API_KEY", raising=False)
    (tmp_path / ".env").write_text("FRED_API_KEY=" + "from-local-file\n")

    assert load_project_local_env(tmp_path) is True
    assert os.environ["FRED_API_KEY"] == "from-local-file"


def test_load_project_local_env_preserves_process_value(
    tmp_path: Path, monkeypatch
) -> None:
    from app.runtime_env import load_project_local_env

    monkeypatch.setenv("FRED_API_KEY", "from-process")
    (tmp_path / ".env").write_text("FRED_API_KEY=" + "from-local-file\n")

    assert load_project_local_env(tmp_path) is True
    assert os.environ["FRED_API_KEY"] == "from-process"


def test_load_project_local_env_missing_file_is_harmless(
    tmp_path: Path, monkeypatch
) -> None:
    from app.runtime_env import load_project_local_env

    monkeypatch.delenv("FRED_API_KEY", raising=False)

    assert load_project_local_env(tmp_path) is False
    assert "FRED_API_KEY" not in os.environ
```

- [ ] **Step 2: Run the new tests and verify the module is missing**

Run:

```bash
.venv/bin/python -m pytest tests/test_runtime_env.py -q
```

Expected: collection fails with `ModuleNotFoundError: No module named 'app.runtime_env'`.

- [ ] **Step 3: Implement the minimal non-overriding loader**

Create `app/runtime_env.py`:

```python
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from app.workspace_paths import PROJECT_ROOT


def load_project_local_env(project_root: Path | None = None) -> bool:
    """Load the active worktree's local environment without overriding process values."""
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    env_path = root / ".env"
    if not env_path.is_file():
        return False
    return bool(load_dotenv(dotenv_path=env_path, override=False))
```

In `app/web/streamlit_app.py`, immediately after adding
`DIRECT_RUN_PROJECT_ROOT` to `sys.path`, load the environment before importing page modules:

```python
from app.runtime_env import load_project_local_env

load_project_local_env(DIRECT_RUN_PROJECT_ROOT)
```

In `app/jobs/overview_automation.py`, import the helper and call it at the start of `main()` before
`run_overview_automation(...)`:

```python
from app.runtime_env import load_project_local_env


def main(argv: Sequence[str] | None = None) -> int:
    load_project_local_env()
    parser = argparse.ArgumentParser(
        description="Run browser-independent Overview market intelligence automation."
    )
```

- [ ] **Step 4: Protect and populate the local secret files without printing their value**

Add these tracked rules to `.gitignore`:

```gitignore
.env
.env.*
!.env.example
```

Add the same three lines to the common Git directory `.git/info/exclude`. Use the user-supplied
credential from the active session to create each of the three root `.env` files with exactly one
logical setting whose key is `FRED_API_KEY` and whose value is that active-session secret. Perform
the write through a secret-aware local edit that does not place the value in tool-call output or a
tracked patch.

Verify only presence, permissions, and Git exclusion; do not print file contents:

```bash
for worktree in \
  /Users/taeho/Project/quant-data-pipeline-worktrees/main-dev \
  /Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev \
  /Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev
do
  test -s "$worktree/.env"
  git -C "$worktree" check-ignore -q .env
done
```

Expected: all commands exit 0 and `git status --short --ignored` shows each `.env` as ignored.

- [ ] **Step 5: Run focused tests and secret scans**

Run:

```bash
.venv/bin/python -m pytest tests/test_runtime_env.py -q
.venv/bin/python -m py_compile app/runtime_env.py app/web/streamlit_app.py app/jobs/overview_automation.py
git diff --check
git diff -- .gitignore app/runtime_env.py app/web/streamlit_app.py app/jobs/overview_automation.py tests/test_runtime_env.py
```

Expected: tests pass, compile succeeds, diff is clean, and no credential value appears in the diff.

- [ ] **Step 6: Commit the runtime boundary only**

```bash
git add .gitignore app/runtime_env.py app/web/streamlit_app.py app/jobs/overview_automation.py tests/test_runtime_env.py
git commit -m "기능: 로컬 FRED 환경변수 로드"
```

Do not stage `.env`, `.git/info/exclude`, run history, screenshots, or unrelated dirty files.

---

### Task 2: Economic-cycle freshness read model

**Files:**
- Create: `app/services/overview/economic_cycle_freshness.py`
- Create: `tests/test_economic_cycle_freshness.py`
- Modify: `app/services/overview/economic_cycle.py:75-125,380-442,509-536`
- Modify: `tests/test_economic_cycle_service.py`

**Interfaces:**
- Consumes: optional persisted intramonth projection with `as_of_date`
- Produces: `latest_economic_cycle_refresh_date(value: date | datetime | None = None) -> date`
- Produces: `build_economic_cycle_freshness(intramonth: Mapping[str, Any] | None, *, today: date | datetime | None = None, read_error: bool = False) -> dict[str, Any]`
- Produces: top-level `data_freshness` with `status`, `persisted_as_of_date`, `target_as_of_date`, `refresh_required`, `message`, optional `action`

- [ ] **Step 1: Add failing weekday and state tests**

Create `tests/test_economic_cycle_freshness.py`:

```python
from datetime import date, datetime


def test_latest_refresh_date_uses_previous_friday_on_weekend() -> None:
    from app.services.overview.economic_cycle_freshness import (
        latest_economic_cycle_refresh_date,
    )

    assert latest_economic_cycle_refresh_date(date(2026, 7, 24)) == date(2026, 7, 24)
    assert latest_economic_cycle_refresh_date(date(2026, 7, 25)) == date(2026, 7, 24)
    assert latest_economic_cycle_refresh_date(datetime(2026, 7, 26, 9, 0)) == date(2026, 7, 24)


def test_stale_intramonth_exposes_manual_action() -> None:
    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    result = build_economic_cycle_freshness(
        {"as_of_date": "2026-07-21"},
        today=date(2026, 7, 25),
    )

    assert result["status"] == "REFRESH_AVAILABLE"
    assert result["persisted_as_of_date"] == "2026-07-21"
    assert result["target_as_of_date"] == "2026-07-24"
    assert result["refresh_required"] is True
    assert result["action"] == {
        "id": "refresh_economic_cycle_data",
        "label": "최신 데이터로 다시 계산",
        "enabled": True,
    }


def test_current_intramonth_hides_manual_action() -> None:
    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    result = build_economic_cycle_freshness(
        {"as_of_date": "2026-07-24"},
        today=date(2026, 7, 25),
    )

    assert result["status"] == "READY"
    assert result["refresh_required"] is False
    assert "action" not in result


def test_missing_and_read_error_remain_actionable() -> None:
    from app.services.overview.economic_cycle_freshness import (
        build_economic_cycle_freshness,
    )

    missing = build_economic_cycle_freshness(None, today=date(2026, 7, 25))
    failed = build_economic_cycle_freshness(
        None, today=date(2026, 7, 25), read_error=True
    )

    assert missing["status"] == "MISSING"
    assert failed["status"] == "ERROR"
    assert missing["action"]["id"] == "refresh_economic_cycle_data"
    assert failed["action"]["id"] == "refresh_economic_cycle_data"
```

- [ ] **Step 2: Run the freshness tests and verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_freshness.py -q
```

Expected: module import fails because `economic_cycle_freshness.py` does not exist.

- [ ] **Step 3: Implement the pure freshness adapter**

Create `app/services/overview/economic_cycle_freshness.py` with:

```python
from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from typing import Any

ACTION = {
    "id": "refresh_economic_cycle_data",
    "label": "최신 데이터로 다시 계산",
    "enabled": True,
}


def _as_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def latest_economic_cycle_refresh_date(
    value: date | datetime | None = None,
) -> date:
    resolved = _as_date(value) or date.today()
    while resolved.weekday() >= 5:
        resolved -= timedelta(days=1)
    return resolved


def build_economic_cycle_freshness(
    intramonth: Mapping[str, Any] | None,
    *,
    today: date | datetime | None = None,
    read_error: bool = False,
) -> dict[str, Any]:
    target = latest_economic_cycle_refresh_date(today)
    persisted = _as_date(dict(intramonth or {}).get("as_of_date"))
    if read_error:
        status = "ERROR"
        message = "저장된 최신 계산일을 확인하지 못했습니다. 수동으로 다시 확인할 수 있습니다."
    elif persisted is None:
        status = "MISSING"
        message = f"월중 계산 결과가 없습니다. {target.isoformat()} 기준으로 다시 계산할 수 있습니다."
    elif persisted < target:
        status = "REFRESH_AVAILABLE"
        message = f"현재 계산일 {persisted.isoformat()} · 최신 계산 가능일 {target.isoformat()}"
    else:
        status = "READY"
        message = f"최신 계산 기준 {persisted.isoformat()}"
    result = {
        "status": status,
        "persisted_as_of_date": persisted.isoformat() if persisted else None,
        "target_as_of_date": target.isoformat(),
        "refresh_required": status != "READY",
        "message": message,
    }
    if status != "READY":
        result["action"] = dict(ACTION)
    return result
```

- [ ] **Step 4: Attach freshness to normal and empty service models**

Add optional `freshness_date: str | date | datetime | None = None` to
`build_economic_cycle_read_model`. Pass the projected `intramonth` and fixed date to the new
adapter:

```python
data_freshness = build_economic_cycle_freshness(
    intramonth,
    today=freshness_date,
)
```

Return `"data_freshness": data_freshness` beside `"intramonth": intramonth`.

Extend `_empty_model` with `freshness_date` and return:

```python
"data_freshness": build_economic_cycle_freshness(
    None,
    today=freshness_date,
    read_error=status == "ERROR",
),
```

Pass `freshness_date` through every `_empty_model(...)` branch so an empty/error model still
offers the same explicit action without fetching.

- [ ] **Step 5: Add service attachment tests**

In `tests/test_economic_cycle_service.py`, add:

```python
def test_service_attaches_intramonth_freshness() -> None:
    service = importlib.import_module("app.services.overview.economic_cycle")
    model = service.build_economic_cycle_read_model(
        snapshot_loader=lambda **_kwargs: _ready_snapshot(),
        intramonth_loader=lambda **_kwargs: _intramonth_snapshot(),
        history_loader=lambda **_kwargs: [],
        market_series_loader=lambda **_kwargs: [],
        asset_price_loader=lambda **_kwargs: [],
        sp500_earnings_loader=lambda **_kwargs: {},
        freshness_date=date(2026, 7, 25),
    )

    assert model["data_freshness"]["persisted_as_of_date"] == "2026-07-21"
    assert model["data_freshness"]["target_as_of_date"] == "2026-07-24"
    assert model["data_freshness"]["status"] == "REFRESH_AVAILABLE"
```

Use the existing fixture names in that file; if its monthly fixture has a different exact helper
name, call that existing helper without changing fixture contents.

- [ ] **Step 6: Run tests and commit the DB-only freshness contract**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_freshness.py tests/test_economic_cycle_service.py -q
.venv/bin/python -m py_compile app/services/overview/economic_cycle_freshness.py app/services/overview/economic_cycle.py
git diff --check
```

Expected: focused tests pass and service source contains no collector/materializer import.

Commit:

```bash
git add app/services/overview/economic_cycle_freshness.py app/services/overview/economic_cycle.py tests/test_economic_cycle_freshness.py tests/test_economic_cycle_service.py
git commit -m "기능: 경제사이클 최신화 필요 상태 계산"
```

---

### Task 3: Manual action façade and persisted postcondition

**Files:**
- Modify: `app/jobs/overview_actions.py:32-60,381-525`
- Modify: `tests/test_economic_cycle_refresh.py`

**Interfaces:**
- Consumes: `latest_economic_cycle_refresh_date`, `run_economic_cycle_intramonth_refresh`, `load_cycle_snapshot`
- Produces: `run_overview_economic_cycle_refresh(*, as_of_date: str | date | datetime | None = None, refresh_runner: Callable[..., JobResult] = run_economic_cycle_intramonth_refresh, snapshot_loader: Callable[..., Mapping[str, object] | None] = load_cycle_snapshot) -> JobResult`
- Accepted success statuses: `success`, `partial_success`
- Postcondition: returned persisted row has `as_of_date >= target_as_of_date`

- [ ] **Step 1: Add failing action façade tests**

Append to `tests/test_economic_cycle_refresh.py`:

```python
def test_overview_action_uses_previous_friday_and_requires_persisted_target() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    calls = []

    def runner(*, as_of_date):
        calls.append(as_of_date)
        return {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "partial_success",
            "rows_written": 1,
            "failed_symbols": [],
            "message": "provisional",
            "details": {},
        }

    rows = iter(
        [
            {"as_of_date": "2026-07-21", "run_kind": "intramonth_nowcast"},
            {"as_of_date": "2026-07-24", "run_kind": "intramonth_nowcast"},
        ]
    )
    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=runner,
        snapshot_loader=lambda **_kwargs: next(rows),
    )

    assert calls == [date(2026, 7, 24)]
    assert result["status"] == "partial_success"
    assert result["details"]["target_as_of_date"] == "2026-07-24"
    assert result["details"]["after_as_of_date"] == "2026-07-24"


def test_overview_action_rejects_success_without_persisted_target() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "success",
            "rows_written": 1,
            "failed_symbols": [],
            "message": "claimed success",
            "details": {},
        },
        snapshot_loader=lambda **_kwargs: {
            "as_of_date": "2026-07-21",
            "run_kind": "intramonth_nowcast",
        },
    )

    assert result["status"] == "incomplete"
    assert result["details"]["after_as_of_date"] == "2026-07-21"
    assert "기존 2026-07-21 결과를 유지" in result["message"]


def test_overview_action_preserves_failed_pipeline_result() -> None:
    from app.jobs.overview_actions import run_overview_economic_cycle_refresh

    rows = iter(
        [
            {"as_of_date": "2026-07-21"},
            {"as_of_date": "2026-07-21"},
        ]
    )
    result = run_overview_economic_cycle_refresh(
        as_of_date=date(2026, 7, 25),
        refresh_runner=lambda **_kwargs: {
            "job_name": "refresh_economic_cycle_intramonth",
            "status": "failed",
            "rows_written": 0,
            "failed_symbols": ["PAYEMS"],
            "message": "gap",
            "details": {},
        },
        snapshot_loader=lambda **_kwargs: next(rows),
    )

    assert result["status"] == "failed"
    assert result["rows_written"] == 0
    assert result["details"]["after_as_of_date"] == "2026-07-21"
```

- [ ] **Step 2: Run the new action tests and verify the façade is missing**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_refresh.py -q
```

Expected: new tests fail importing `run_overview_economic_cycle_refresh`.

- [ ] **Step 3: Implement the wrapper with before/after DB reads**

Import the freshness target helper, combined refresh runner, and DB loader in
`app/jobs/overview_actions.py`. Implement the exact signature from Interfaces.

The wrapper must:

```python
target = latest_economic_cycle_refresh_date(as_of_date)
before = snapshot_loader(
    as_of_date=target,
    run_kind="intramonth_nowcast",
)
pipeline = dict(refresh_runner(as_of_date=target))
after = snapshot_loader(
    as_of_date=target,
    run_kind="intramonth_nowcast",
)
```

Normalize before/after dates without raising on missing values. Return job name
`overview_economic_cycle_manual_refresh`. Preserve pipeline `rows_written` and
`failed_symbols`. Build details with:

```python
{
    "target_as_of_date": target.isoformat(),
    "before_as_of_date": before_date,
    "after_as_of_date": after_date,
    "pipeline_status": pipeline.get("status"),
    "pipeline_job_name": pipeline.get("job_name"),
}
```

Status rules:

- if `before_date >= target`, return `success` without running the pipeline;
- if pipeline status is `success` or `partial_success` and `after_date >= target`, preserve that
  pipeline status;
- if pipeline status is accepted but the postcondition fails, return `incomplete`;
- otherwise return `failed`;
- any loader/runner exception returns `failed` with the prior date in the user message when known.

Messages are compact and user-facing:

```text
최신 경제사이클 계산 기준 2026-07-24를 반영했습니다.
2026-07-24 기준 잠정 계산을 반영했습니다.
최신 계산일을 확인하지 못했습니다. 기존 2026-07-21 결과를 유지합니다.
경제사이클을 최신화하지 못했습니다. 기존 2026-07-21 결과를 유지합니다.
```

- [ ] **Step 4: Run action and existing pipeline tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_economic_cycle_refresh.py tests/test_economic_cycle_freshness.py -q
.venv/bin/python -m py_compile app/jobs/overview_actions.py
git diff --check
```

Expected: all focused tests pass; `app/jobs/economic_cycle_refresh.py` remains unchanged.

- [ ] **Step 5: Commit the action façade**

```bash
git add app/jobs/overview_actions.py tests/test_economic_cycle_refresh.py
git commit -m "기능: 경제사이클 수동 최신화 액션 추가"
```

---

### Task 4: Python UI event bridge, cache gate, and fallback

**Files:**
- Modify: `app/web/overview/market_context_helpers.py:12-50,99-133,189-217,257-278,409-426`
- Modify: `app/web/overview/economic_cycle_react_component.py:36-43`
- Modify: `tests/test_market_context_economic_cycle.py:154-169`

**Interfaces:**
- Consumes: `run_overview_economic_cycle_refresh() -> JobResult`
- Produces: component return `dict[str, Any] | None`
- Produces: event `{event: {id: "refresh_economic_cycle_data", nonce: string}}`
- Session keys: `overview_economic_cycle_refresh_result`, `overview_economic_cycle_refresh_last_event`

- [ ] **Step 1: Replace the obsolete no-event test with failing bridge tests**

Keep assertions that service/component never import provider collectors or materializers, but remove
the obsolete assertion that the component has no event. Add:

```python
def test_cycle_component_returns_explicit_action_event() -> None:
    module = importlib.import_module(
        "app.web.overview.economic_cycle_react_component"
    )
    component = Mock(
        return_value={
            "event": {
                "id": "refresh_economic_cycle_data",
                "nonce": "cycle-1",
            }
        }
    )

    with patch.object(module, "_declare_economic_cycle_component", return_value=component):
        result = module.render_economic_cycle_component({"schema_version": "economic_cycle_v2"})

    assert result["event"]["id"] == "refresh_economic_cycle_data"


def test_cycle_event_runs_once_and_clears_cache_only_on_usable_success() -> None:
    helpers = importlib.import_module("app.web.overview.market_context_helpers")
    state = {}
    run_action = Mock(
        return_value={"status": "partial_success", "message": "refreshed"}
    )
    store = Mock()
    clear = Mock()
    rerun = Mock()
    event = {
        "event": {
            "id": "refresh_economic_cycle_data",
            "nonce": "cycle-1",
        }
    }

    assert helpers._handle_economic_cycle_event(
        event,
        state=state,
        run_action=run_action,
        store_result=store,
        clear_cache=clear,
        rerun=rerun,
    ) is True
    assert helpers._handle_economic_cycle_event(
        event,
        state=state,
        run_action=run_action,
        store_result=store,
        clear_cache=clear,
        rerun=rerun,
    ) is False
    run_action.assert_called_once_with()
    store.assert_called_once()
    clear.assert_called_once_with()
    rerun.assert_called_once_with()


def test_cycle_event_keeps_cache_on_incomplete_result() -> None:
    helpers = importlib.import_module("app.web.overview.market_context_helpers")
    clear = Mock()
    helpers._handle_economic_cycle_event(
        {"event": {"id": "refresh_economic_cycle_data", "nonce": "cycle-2"}},
        state={},
        run_action=lambda: {"status": "incomplete", "message": "kept"},
        store_result=Mock(),
        clear_cache=clear,
        rerun=Mock(),
    )
    clear.assert_not_called()
```

- [ ] **Step 2: Run bridge tests and verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q
```

Expected: bridge return value and `_handle_economic_cycle_event` tests fail.

- [ ] **Step 3: Return the component value**

Change `render_economic_cycle_component` to:

```python
def render_economic_cycle_component(
    payload: dict[str, Any],
    *,
    key: str = "economic_cycle_workbench",
) -> dict[str, Any] | None:
    component = _declare_economic_cycle_component()
    if component is None:
        return None
    result = component(payload=payload, key=key, default=None)
    return dict(result) if isinstance(result, dict) else None
```

- [ ] **Step 4: Implement nonce consumption and UI execution**

In `market_context_helpers.py`, add:

```python
ECONOMIC_CYCLE_RESULT_KEY = "overview_economic_cycle_refresh_result"
ECONOMIC_CYCLE_EVENT_KEY = "overview_economic_cycle_refresh_last_event"
ECONOMIC_CYCLE_ACTION_ID = "refresh_economic_cycle_data"
```

Add focused helpers:

```python
def _economic_cycle_event_payload(event: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(event, dict):
        return {}
    nested = event.get("event")
    return dict(nested) if isinstance(nested, dict) else dict(event)


def _consume_economic_cycle_event(payload: dict[str, Any], *, state: Any) -> bool:
    if str(payload.get("id") or "") != ECONOMIC_CYCLE_ACTION_ID:
        return False
    token = f"{ECONOMIC_CYCLE_ACTION_ID}:{payload.get('nonce') or ECONOMIC_CYCLE_ACTION_ID}"
    if state.get(ECONOMIC_CYCLE_EVENT_KEY) == token:
        return False
    state[ECONOMIC_CYCLE_EVENT_KEY] = token
    return True
```

`_run_economic_cycle_refresh_for_ui()` uses one `st.status` block and calls only
`run_overview_economic_cycle_refresh()`. `_handle_economic_cycle_event(...)` stores the result once
through `_store_overview_job_result`, clears only `load_economic_cycle_model` when status is
`success` or `partial_success`, then reruns. `incomplete` and `failed` retain cache.

`render_economic_cycle()` must:

1. load the DB model;
2. pop `ECONOMIC_CYCLE_RESULT_KEY` once and attach only
   `{"status": str(result.get("status") or "failed"), "message": str(result.get("message") or "")}`
   as `refresh_result`;
3. pass payload to React and consume the returned event;
4. use fallback rendering when the component is unavailable.

The fallback renderer reads `payload["data_freshness"]["action"]`, shows the same message/button,
runs the same UI helper, records the result once, clears cache only on accepted success, and reruns.
It must offer the action before returning from an `ERROR` payload.

- [ ] **Step 5: Run Python bridge regression**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py tests/test_economic_cycle_refresh.py tests/test_economic_cycle_service.py -q
.venv/bin/python -m py_compile app/web/overview/market_context_helpers.py app/web/overview/economic_cycle_react_component.py
git diff --check
```

Expected: duplicate nonce runs once, incomplete/failed do not clear cache, and provider modules are
still absent from service/React source.

- [ ] **Step 6: Commit the Python UI bridge**

```bash
git add app/web/overview/market_context_helpers.py app/web/overview/economic_cycle_react_component.py tests/test_market_context_economic_cycle.py
git commit -m "기능: 경제사이클 수동 최신화 이벤트 연결"
```

---

### Task 5: React freshness action and production component

**Files:**
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx:1-3,198-232,1186-1214`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/src/style.css`
- Modify: `app/web/streamlit_components/economic_cycle_workbench/component_static/`
- Modify: `tests/test_market_context_economic_cycle.py:228-317,467-487,490-500`

**Interfaces:**
- Consumes: `payload.data_freshness` and optional `payload.refresh_result`
- Emits: `{event: {id: "refresh_economic_cycle_data", nonce: string}}`
- Does not emit: provider URL, collector name, row count, timer event

- [ ] **Step 1: Add failing React source contracts**

Add source assertions:

```python
def test_cycle_component_has_compact_manual_freshness_action() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    for token in (
        "data_freshness?: EconomicCycleFreshness",
        "refresh_result?: RefreshResult",
        "최신 데이터로 다시 계산",
        'id: "refresh_economic_cycle_data"',
        "Streamlit.setComponentValue",
        'className="cycle-freshness-bar"',
    ):
        assert token in source
    assert ".cycle-freshness-bar" in css
    assert "rows_written" not in source
    assert "failed_symbols" not in source
```

Update `test_cycle_component_has_no_fetch_job_trading_or_refresh_loop` so it continues to forbid:

```python
for forbidden in (
    "fetch(",
    "axios",
    "setinterval",
    "settimeout",
    "run_collect",
    "materialize",
    "매수",
    "매도",
    "주문",
):
    assert forbidden not in source
```

Remove only the obsolete `streamlit.setcomponentvalue` forbidden token.

- [ ] **Step 2: Run the source contract and verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q
```

Expected: freshness/action tokens are missing.

- [ ] **Step 3: Add typed payload and explicit event emit**

Import `useState` with the existing React hooks. Add:

```typescript
type EconomicCycleFreshness = {
  status: "READY" | "REFRESH_AVAILABLE" | "MISSING" | "ERROR";
  persisted_as_of_date?: string | null;
  target_as_of_date?: string | null;
  refresh_required: boolean;
  message: string;
  action?: {
    id: "refresh_economic_cycle_data";
    label: string;
    enabled: boolean;
  };
};

type RefreshResult = {
  status: "success" | "partial_success" | "incomplete" | "failed";
  message: string;
};
```

Extend `CyclePayload`:

```typescript
data_freshness?: EconomicCycleFreshness;
refresh_result?: RefreshResult;
```

Implement `EconomicCycleFreshnessBar`. When action is enabled, its button sets local collecting
state and emits:

```typescript
Streamlit.setComponentValue({
  event: {
    id: "refresh_economic_cycle_data",
    nonce: `${Date.now()}`,
  },
});
```

The visible states are:

- READY: `최신 계산 기준 {persisted_as_of_date}`, no enabled action;
- stale/missing/error: `message` plus `최신 데이터로 다시 계산`;
- collecting: disabled button with `최신 자료를 수집하고 다시 계산하는 중`;
- one-shot result: only result `message`, styled from its status.

Render the bar directly before the intramonth flow so it is visible even when
`payload.intramonth` is missing.

- [ ] **Step 4: Add responsive styles**

Add `.cycle-freshness-bar`, `.cycle-freshness-copy`, `.cycle-freshness-action`,
`.cycle-refresh-result` rules. Desktop uses copy/action columns; under the existing
`@media (max-width: 420px)` block:

```css
.cycle-freshness-bar {
  grid-template-columns: 1fr;
}

.cycle-freshness-action {
  width: 100%;
}
```

Keep the existing `overflow-x: hidden` contract and no fixed pixel width wider than the component.

- [ ] **Step 5: Build and test the production component**

Run:

```bash
.venv/bin/python -m pytest tests/test_market_context_economic_cycle.py -q
npm run build
```

Working directory for the second command:

```text
app/web/streamlit_components/economic_cycle_workbench
```

Then run:

```bash
git diff --check
git status --short app/web/streamlit_components/economic_cycle_workbench tests/test_market_context_economic_cycle.py
```

Expected: Vite build succeeds, tracked `component_static` matches source, source contract passes.

- [ ] **Step 6: Commit the React surface**

```bash
git add app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx app/web/streamlit_components/economic_cycle_workbench/src/style.css app/web/streamlit_components/economic_cycle_workbench/component_static tests/test_market_context_economic_cycle.py
git commit -m "기능: 경제사이클 최신화 버튼 표시"
```

---

### Task 6: Actual FRED refresh and data-integrity verification

**Files:**
- Runtime only: `.aiworkspace/note/finance/run_history/*.jsonl`
- Generated only: `economic-cycle-manual-refresh-v1-qa.png`
- Modify evidence: active task `RUNS.md`, `STATUS.md`, `RISKS.md`

**Interfaces:**
- Consumes: real `FRED_API_KEY`, local MySQL, `run_overview_economic_cycle_refresh`
- Produces: persisted target `intramonth_nowcast` and verified UI state

- [ ] **Step 1: Record pre-refresh monthly and intramonth evidence without exposing secrets**

Run a read-only Python audit from the main worktree:

```bash
.venv/bin/python - <<'PY'
import hashlib
import json
from finance.data.db.mysql import MySQLClient

db = MySQLClient("localhost", "root", "1234", 3306)
try:
    db.use_db("finance_meta")
    monthly = db.query(
        """
        SELECT *
        FROM economic_cycle_snapshot
        WHERE run_kind IN ('current', 'historical_replay')
        ORDER BY run_kind, as_of_date, model_version
        """
    )
    intramonth = db.query(
        """
        SELECT as_of_date, model_version, status, source_collected_at, updated_at
        FROM economic_cycle_snapshot
        WHERE run_kind = 'intramonth_nowcast'
        ORDER BY as_of_date, model_version
        """
    )
finally:
    db.close()
canonical = json.dumps(monthly, default=str, sort_keys=True, separators=(",", ":"))
print({
    "monthly_count": len(monthly),
    "monthly_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    "latest_intramonth": intramonth[-1] if intramonth else None,
})
PY
```

Copy only count/hash/date metadata into task `RUNS.md`; do not copy source payloads or credentials.

- [ ] **Step 2: Run the real manual action once**

Confirm local env loading without printing its value:

```bash
.venv/bin/python -c "from app.runtime_env import load_project_local_env; import os; loaded=load_project_local_env(); print({'env_file_loaded': loaded, 'fred_key_present': bool(os.environ.get('FRED_API_KEY'))})"
```

Then execute the same façade used by the button:

```bash
.venv/bin/python -c "from app.runtime_env import load_project_local_env; load_project_local_env(); from datetime import date; from app.jobs.overview_actions import run_overview_economic_cycle_refresh, record_overview_action_result; result=run_overview_economic_cycle_refresh(as_of_date=date(2026,7,25)); record_overview_action_result(result); print({'job_name': result.get('job_name'), 'status': result.get('status'), 'message': result.get('message'), 'details': {key: result.get('details', {}).get(key) for key in ('target_as_of_date','before_as_of_date','after_as_of_date','pipeline_status')}})"
```

Expected: target and after are `2026-07-24`; status is `success` or `partial_success`. The printed
result must not contain the API key or raw provider payload.

- [ ] **Step 3: Verify post-refresh invariants**

Repeat the Step 1 audit. Expected:

- prior monthly rows have the same count/hash unless a missing closed-month canonical row was
  legitimately appended;
- if one closed-month row was appended, all pre-existing monthly rows retain their original
  serialized hash and the new row is documented separately;
- latest `intramonth_nowcast.as_of_date` is `2026-07-24`;
- one business key exists for target/model version;
- `source_collected_at` is later than the prior 2026-07-16 evidence;
- the manual action result is appended once to run history.

Run the exact target uniqueness query:

```bash
.venv/bin/python - <<'PY'
from finance.data.db.mysql import MySQLClient

db = MySQLClient("localhost", "root", "1234", 3306)
try:
    db.use_db("finance_meta")
    rows = db.query(
        """
        SELECT as_of_date, model_version, run_kind, COUNT(*) AS business_rows,
               MAX(source_collected_at) AS source_collected_at
        FROM economic_cycle_snapshot
        WHERE run_kind = 'intramonth_nowcast'
          AND as_of_date = '2026-07-24'
        GROUP BY as_of_date, model_version, run_kind
        """
    )
finally:
    db.close()
print(rows)
PY
```

Expected: one row per model version and `business_rows=1`.

- [ ] **Step 4: Run full focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_runtime_env.py tests/test_economic_cycle_freshness.py tests/test_economic_cycle_refresh.py tests/test_economic_cycle_service.py tests/test_market_context_economic_cycle.py tests/test_service_contracts.py -q
.venv/bin/python -m py_compile app/runtime_env.py app/services/overview/economic_cycle_freshness.py app/services/overview/economic_cycle.py app/jobs/overview_actions.py app/web/overview/market_context_helpers.py app/web/overview/economic_cycle_react_component.py
npm run build
git diff --check
```

Run `npm run build` from `app/web/streamlit_components/economic_cycle_workbench`.

- [ ] **Step 5: Perform Browser QA**

Start an isolated app on an unused non-user port after loading the main worktree `.env`:

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8517 --server.headless true
```

Use the in-app Browser skill to open `http://localhost:8517`, navigate to
`Market Research > 시장 환경 > 경제 사이클`, and verify:

- before refresh, stale data shows current date and target date with one action;
- during refresh, the action is disabled and progress is understandable;
- after refresh, latest state shows `2026-07-24` and the action is hidden/disabled;
- monthly cards and ribbon still use canonical monthly data;
- no raw run/job/row panel appears;
- desktop and 420px have no horizontal overflow;
- browser console/page errors are zero.

Save one generated screenshot as `economic-cycle-manual-refresh-v1-qa.png` in the worktree root and
do not stage it.

- [ ] **Step 6: Record QA evidence without committing runtime artifacts**

Update active task `RUNS.md`, `STATUS.md`, and `RISKS.md` with:

- test command summaries and pass counts;
- actual before/after dates and monthly invariant evidence;
- Browser QA viewport and screenshot filename;
- any provider limitation or unresolved risk.

Do not stage run history JSONL, `.env`, screenshot, or unrelated dirty files.

---

### Task 7: Durable documentation and closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725/PLAN.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725/RISKS.md`

**Interfaces:**
- Consumes: verified implementation and actual QA evidence
- Produces: durable user/runbook boundary and compact root handoff

- [ ] **Step 1: Synchronize canonical documentation**

Use `finance-runbook-maintainer` for the operational procedure and `finance-doc-sync` for durable
alignment.

Update `PROJECT_MAP.md` so the economic-cycle row states:

- UI remains DB-only on entry;
- stale/missing/error freshness exposes one explicit manual action;
- action façade owns combined refresh and persisted target verification;
- background scheduler is not required for the manual flow.

Update `OVERVIEW_MARKET_INTELLIGENCE.md`:

- replace the claim that intramonth refresh depends on an unattended scheduler;
- document worktree-local `.env` with `override=False`;
- document the browser button and CLI fallback;
- document last-good and postcondition recovery;
- never include a credential value.

Add the completed roadmap item and keep root logs to 3~5 lines for this task. Update `INDEX.md` only
where current navigation/status text is affected.

- [ ] **Step 2: Mark the three-stage roadmap complete**

In active task docs:

```text
1차 complete — local secret and runtime boundary
2차 complete — freshness and manual action
3차 complete — actual refresh, QA, and closeout
```

Record exact commits, focused verification, actual DB dates, and generated screenshot name. Keep
the exposed-key rotation recommendation in `RISKS.md` until the user rotates it.

- [ ] **Step 3: Validate documentation and working tree scope**

Run:

```bash
rg -n "TO""DO|TB""D|PLACE""HOLDER|api_key=[A-Za-z0-9]" docs/superpowers/plans/2026-07-25-economic-cycle-manual-refresh.md .aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725 .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md
git diff --check
git status --short
```

Expected: no placeholder or secret match, no whitespace errors, and only intended docs/code are
selected for the final commit.

- [ ] **Step 4: Commit closeout documentation**

```bash
git add .aiworkspace/note/finance/docs/PROJECT_MAP.md .aiworkspace/note/finance/docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md .aiworkspace/note/finance/docs/ROADMAP.md .aiworkspace/note/finance/docs/INDEX.md .aiworkspace/note/finance/WORK_PROGRESS.md .aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md .aiworkspace/note/finance/tasks/active/market-research-economic-cycle-manual-refresh-v1-20260725
git commit -m "문서: 경제사이클 수동 최신화 운영 절차 정리"
```

- [ ] **Step 5: Final verification before completion claim**

Use `superpowers:verification-before-completion` and run:

```bash
git diff --check HEAD~1
git status --short
git log --oneline -8
```

Confirm `.env`, run history, screenshot, and pre-existing unrelated changes are not in any task
commit. Report overall roadmap `3/3차 complete`, the actual persisted target date, Browser QA
evidence, remaining key-rotation recommendation, and the next durable runbook location.
