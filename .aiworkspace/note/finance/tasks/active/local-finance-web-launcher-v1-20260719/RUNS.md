# Local Finance Web Launcher V1 Runs

Date: 2026-07-19

## Baseline

```bash
.venv/bin/python -m pytest tests/test_backtest_refactor_boundaries.py -q -k 'workflow_shell'
```

Result: could not run because the worktree venv has no `pytest` module.

```bash
uv run --with pytest python -m pytest tests/test_backtest_refactor_boundaries.py -q -k 'workflow_shell'
```

Result: `2 passed, 48 deselected`.

## TDD RED

- CLI validation RED: test loader failed with `FileNotFoundError: /Users/taeho/.local/bin/qweb`.
- Frontend RED: 5 tests failed because `Config` and build helpers were absent.
- Lifecycle RED: 8 tests failed because state/start/stop/log helpers were absent.
- Mixed listener ownership RED exposed that a set containing both owned and foreign PID must not be treated as
  `RUNNING`.

## TDD GREEN

```bash
python3 /Users/taeho/.local/share/qweb/test_qweb.py -v
```

Result: `23 tests`, `OK`.

Coverage includes:

- worktree/port validation and help parsing
- buildable package discovery
- generated directory fingerprint exclusion
- initial/current/changed/deleted-output build decision
- Overview `component_static/` output recognition
- npm failure propagation
- manual port conflict refusal before build/start
- owned instance idempotency
- PID/meta recording
- cwd and mixed-listener ownership rejection
- exact-ownership `SIGTERM`
- dead PID + free port stale-state cleanup without signal
- non-positive PID metadata rejection
- missing log handling

## Syntax And Shell Discovery

```bash
python3 -m py_compile /Users/taeho/.local/bin/qweb /Users/taeho/.local/share/qweb/test_qweb.py
zsh -n /Users/taeho/.zshrc
zsh -lic 'command -v qweb && qweb help'
```

Result: Python and zsh syntax exit 0; qweb resolves to `/Users/taeho/.local/bin/qweb` and prints usage.

## Read-Only Existing Port Check

```bash
qweb status main-dev 8521 || true
qweb status sub-dev 8502 || true
qweb status backtest-dev 8506 || true
```

Result:

```text
PORT_CONFLICT: port 8521 is used by PID(s) [37122]
PORT_CONFLICT: port 8502 is used by PID(s) [49406]
PORT_CONFLICT: port 8506 is used by PID(s) [49317]
```

No signal or build was issued. `/Users/taeho/.local/state/qweb` remained empty.

## Real Frontend Discovery

Read-only discovery against `main-dev` found 19 buildable `app/web` packages:

- 12 component packages with `build/`
- 7 Overview / workspace packages with `component_static/`

The latter includes `economic_cycle_workbench` and `market_context_valuation`. This confirmed that Overview Market
Context does not depend on the three Backtest build commands and that qweb must recognize both output conventions.

## Live Start/Stop Scope

Actual start/stop smoke was intentionally skipped because all requested ports already have manually started user
processes and the approved safety contract forbids mutating them. The unittest fixture verifies start/stop behavior;
the first user adoption step is to stop one manual process and run `qweb start <worktree> <port>`.
