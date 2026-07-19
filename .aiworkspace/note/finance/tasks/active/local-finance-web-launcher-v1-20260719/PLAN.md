# Local Finance Web Launcher V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install one `qweb` command that builds changed or missing web frontends and safely starts, stops, inspects, and tails logs for a named finance worktree and port.

**Architecture:** A dependency-free Python executable at `/Users/taeho/.local/bin/qweb` owns validation, frontend fingerprints, npm builds, process metadata, and ownership checks. Its unittest suite lives at `/Users/taeho/.local/share/qweb/test_qweb.py`; `.zshrc` only exposes the executable through PATH. Durable instructions live in finance runbooks while PID, log, metadata, and fingerprints remain personal local state.

**Tech Stack:** Python 3 standard library, unittest/mock, npm/Vite, macOS `lsof`/`ps`, zsh, Streamlit CLI.

## Global Constraints

- Worktree names allow only `A-Z`, `a-z`, digits, `.`, `_`, and `-`.
- Ports must be integers in `1..65535`.
- Default worktree root is `/Users/taeho/Project/quant-data-pipeline-worktrees`.
- Default state root is `/Users/taeho/.local/state/qweb`.
- Discover only `app/web/**/package.json` packages with `scripts.build`.
- Never commit `node_modules`, `build`, `dist`, cache, PID, log, metadata, or fingerprint files.
- Any frontend build failure blocks Streamlit startup.
- Port conflicts never trigger automatic termination.
- Stop sends `TERM` only when PID, command, cwd, and listener ownership match; it never escalates to `KILL`.
- Existing 8502, 8505, 8506, and 8521 processes are not mutated during verification.
- Existing `.zshrc` content and unrelated dirty worktree files are preserved.

---

### Task 1: CLI Validation And Local Test Harness

**Files:**
- Create: `/Users/taeho/.local/share/qweb/test_qweb.py`
- Create: `/Users/taeho/.local/bin/qweb`

**Interfaces:**
- Consumes: `help` or `<command> <worktree> <port>`, plus optional `QWEB_WORKTREES_ROOT` and `QWEB_STATE_DIR` overrides.
- Produces: `ParsedCli`, `validate_worktree_name(name)`, `validate_port(raw)`, `parse_cli(argv)`, and `main(argv)`.

- [ ] **Step 1: Create local directories**

Run:

```bash
mkdir -p /Users/taeho/.local/bin /Users/taeho/.local/share/qweb /Users/taeho/.local/state/qweb
```

Expected: all three directories exist and repository files are unchanged.

- [ ] **Step 2: Write failing validation tests**

The unittest loader sets `QWEB_SOURCE_ONLY=1`, loads the extensionless executable with `runpy.run_path()`, and asserts:

```python
self.assertEqual(qweb["validate_worktree_name"]("main-dev"), "main-dev")
with self.assertRaisesRegex(ValueError, "worktree"):
    qweb["validate_worktree_name"]("../main-dev")
self.assertEqual(qweb["validate_port"]("8521"), 8521)
with self.assertRaisesRegex(ValueError, "port"):
    qweb["validate_port"]("70000")
self.assertEqual(qweb["parse_cli"](["help"]).command, "help")
```

- [ ] **Step 3: Run RED**

Run:

```bash
python3 /Users/taeho/.local/share/qweb/test_qweb.py -v
```

Expected: FAIL or ERROR because `/Users/taeho/.local/bin/qweb` and its functions do not exist.

- [ ] **Step 4: Implement the minimal CLI skeleton**

Implement a Python shebang script with:

```python
WORKTREE_RE = re.compile(r"^[A-Za-z0-9._-]+$")

@dataclass(frozen=True)
class ParsedCli:
    command: str
    worktree: str | None = None
    port: int | None = None

def validate_worktree_name(name: str) -> str:
    if not name or not WORKTREE_RE.fullmatch(name):
        raise ValueError("invalid worktree name")
    return name

def validate_port(raw: str) -> int:
    if not raw.isdigit() or not 1 <= int(raw) <= 65535:
        raise ValueError("invalid port")
    return int(raw)
```

`parse_cli()` accepts only `start|stop|status|logs` with three arguments or `help|-h|--help`. Guard execution with `QWEB_SOURCE_ONLY`.

- [ ] **Step 5: Run GREEN**

Run:

```bash
chmod 755 /Users/taeho/.local/bin/qweb
python3 /Users/taeho/.local/share/qweb/test_qweb.py -v
python3 -m py_compile /Users/taeho/.local/bin/qweb
```

Expected: validation tests PASS and compilation exits 0.

### Task 2: Frontend Discovery, Fingerprints, And Conditional Builds

**Files:**
- Modify: `/Users/taeho/.local/share/qweb/test_qweb.py`
- Modify: `/Users/taeho/.local/bin/qweb`

**Interfaces:**
- Consumes: `worktree/app/web`, package JSON, saved fingerprints, and `subprocess.run`.
- Produces: `discover_frontends(root) -> list[Path]`, `source_fingerprint(dir) -> str`, `needs_build(dir, fingerprint_file) -> bool`, and `build_frontends(instance) -> list[Path]`.

- [ ] **Step 1: Write failing discovery and rebuild-policy tests**

Temporary fixtures contain one package with `scripts.build`, one without it, and excluded generated files. Assert initial build required, matching fingerprint plus `build/` skips, source edit rebuilds, deleted output rebuilds, and mocked npm failure raises `QwebError`.

- [ ] **Step 2: Run RED**

Run the unittest file and confirm failures are missing discovery/fingerprint/build functions.

- [ ] **Step 3: Implement deterministic discovery and hashing**

Use:

```python
EXCLUDED_DIRS = {"node_modules", "build", "dist", ".git", "__pycache__", ".vite"}

def discover_frontends(worktree_root: Path) -> list[Path]:
    packages = []
    for package_json in (worktree_root / "app" / "web").rglob("package.json"):
        if any(part in EXCLUDED_DIRS for part in package_json.parts):
            continue
        payload = json.loads(package_json.read_text())
        if isinstance(payload.get("scripts"), dict) and payload["scripts"].get("build"):
            packages.append(package_json.parent)
    return sorted(packages)
```

`source_fingerprint()` hashes each non-generated relative filename and file bytes in sorted order with SHA-256. Fingerprints live under `state/fingerprints/<worktree>/<sha256-relative-package-key>.sha256`.

- [ ] **Step 4: Implement conditional builds**

For each stale package:

```python
install = ["npm", "ci"] if (frontend / "package-lock.json").exists() else ["npm", "install"]
subprocess.run(install, cwd=frontend, check=True)
subprocess.run(["npm", "run", "build"], cwd=frontend, check=True)
fingerprint_file.write_text(source_fingerprint(frontend) + "\n")
```

A package is current only if its fingerprint matches and `build/` or `dist/` exists. Wrap JSON/hash/subprocess errors in `QwebError` naming the package. Do not start Streamlit after a failure.

- [ ] **Step 5: Run GREEN**

Run the unittest file. Expected: discovery, skip, rebuild, deleted-output, and failure-blocking tests PASS.

### Task 3: Safe Start, Status, Stop, And Logs

**Files:**
- Modify: `/Users/taeho/.local/share/qweb/test_qweb.py`
- Modify: `/Users/taeho/.local/bin/qweb`

**Interfaces:**
- Consumes: validated instance, metadata JSON, `lsof`, `ps`, `Popen`, and Task 2 build functions.
- Produces: `listener_pids(port)`, `process_cwd(pid)`, `process_command(pid)`, `inspect_instance(instance)`, `start(instance)`, `stop(instance)`, `status(instance)`, and `logs(instance)`.

- [ ] **Step 1: Write failing ownership and lifecycle tests**

Mock process boundaries and assert:

```python
listener_pids.return_value = {999}
process_cwd.return_value = Path("/tmp/other")
with self.assertRaisesRegex(QwebError, "PORT_CONFLICT"):
    start(instance)
popen.assert_not_called()
```

Also assert an owned running instance is idempotent, cwd mismatch never calls `os.kill`, exact ownership calls `os.kill(pid, signal.SIGTERM)` once, and state classification covers `RUNNING`, `STOPPED`, `STALE_STATE`, and `PORT_CONFLICT`.

- [ ] **Step 2: Run RED**

Run the unittest file. Expected: lifecycle tests fail because lifecycle helpers are missing.

- [ ] **Step 3: Implement state inspection**

Metadata uses exact keys:

```json
{"pid":123,"worktree":"main-dev","worktree_root":"/absolute/path","port":8521,"command":[".venv/bin/python","-m","streamlit","run","app/web/streamlit_app.py"]}
```

Use `lsof -tiTCP:<port> -sTCP:LISTEN` for listeners, `lsof -a -p <pid> -d cwd -Fn` for cwd, and `ps -p <pid> -o command=` for command. Return only the four documented states with details.

- [ ] **Step 4: Implement safe start**

Validate prerequisites, refuse foreign listeners, build frontends, open the log, then call:

```python
subprocess.Popen(
    [str(worktree / ".venv/bin/python"), "-m", "streamlit", "run", "app/web/streamlit_app.py",
     "--server.port", str(port), "--server.headless", "true", "--server.runOnSave", "false",
     "--server.fileWatcherType", "none"],
    cwd=worktree, stdout=log_handle, stderr=subprocess.STDOUT, start_new_session=True,
)
```

Write PID/meta atomically and poll up to 15 seconds. On timeout retain state/log, return a nonzero recovery message, and send no signal.

- [ ] **Step 5: Implement safe stop, status, and logs**

`stop()` verifies PID, Streamlit command fragment, exact cwd, and listener PID before `SIGTERM`; it polls 10 seconds, removes PID/meta on success, preserves logs, and never sends `SIGKILL`. `status()` is read-only. `logs()` requires the log and runs `tail -f`.

- [ ] **Step 6: Run GREEN and compile**

Run:

```bash
python3 /Users/taeho/.local/share/qweb/test_qweb.py -v
python3 -m py_compile /Users/taeho/.local/bin/qweb /Users/taeho/.local/share/qweb/test_qweb.py
/Users/taeho/.local/bin/qweb help
```

Expected: all tests PASS, compilation exits 0, and help lists the four commands.

### Task 4: Shell Exposure And Durable Runbook

**Files:**
- Modify: `/Users/taeho/.zshrc`
- Create: `.aiworkspace/note/finance/docs/runbooks/LOCAL_FINANCE_WEB_LAUNCHER.md`
- Modify: `.aiworkspace/note/finance/docs/runbooks/README.md`
- Modify: `.aiworkspace/note/finance/tasks/active/local-finance-web-launcher-v1-20260719/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/local-finance-web-launcher-v1-20260719/RUNS.md`

**Interfaces:**
- Consumes: the installed and tested qweb executable.
- Produces: qweb discovery in new zsh sessions and a durable operating guide.

- [ ] **Step 1: Add idempotent PATH configuration**

Append only when its marker is absent:

```zsh
# qweb local finance launcher
export PATH="/Users/taeho/.local/bin:$PATH"
```

Preserve all existing `.zshrc` content.

- [ ] **Step 2: Verify fresh-shell discovery**

Run:

```bash
zsh -n /Users/taeho/.zshrc
zsh -lic 'command -v qweb && qweb help'
```

Expected: syntax exits 0, qweb resolves to `/Users/taeho/.local/bin/qweb`, and usage prints.

- [ ] **Step 3: Read-only status checks**

Run:

```bash
qweb status main-dev 8521 || true
qweb status sub-dev 8502 || true
qweb status backtest-dev 8506 || true
```

Expected: manually started listeners report `PORT_CONFLICT` or `STALE_STATE`; no signals or builds occur.

- [ ] **Step 4: Write runbook and index entry**

The runbook contains Purpose, When To Use, Prerequisites, Installation, Commands, Expected Result, Failure Handling, Generated Artifacts, and Related Docs. It explains first-start full build, later conditional rebuilds, read-only status, qweb-owned stop, and manual-process port adoption.

- [ ] **Step 5: Record exact evidence**

Update STATUS and RUNS with RED/GREEN commands, test counts, shell discovery, status results, and why actual live start/stop smoke was skipped.

- [ ] **Step 6: Run final verification**

Run:

```bash
python3 /Users/taeho/.local/share/qweb/test_qweb.py -v
python3 -m py_compile /Users/taeho/.local/bin/qweb /Users/taeho/.local/share/qweb/test_qweb.py
zsh -n /Users/taeho/.zshrc
zsh -lic 'command -v qweb && qweb help'
git diff --check
git status --short
```

Expected: tests PASS, Python and zsh syntax pass, qweb is discoverable, documentation diff is clean, and unrelated user files remain unstaged.

- [ ] **Step 7: Commit documentation closeout**

Stage only the task and runbook files and commit with `로컬 Finance 웹 실행기 설치와 운영 절차`. Personal executable/tests/state/logs/builds and unrelated artifacts remain outside Git.
