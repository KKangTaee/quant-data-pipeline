# Local Finance Web Launcher

Status: Active
Last Verified: 2026-07-19

## Purpose

`qweb`는 worktree 이름과 port만 받아 finance Streamlit app의 frontend 준비, background 시작,
상태 확인, 안전한 종료와 log 확인을 한 명령으로 수행하는 개인 local launcher다.

새 worktree나 frontend 변경 병합 후 `build/` 또는 `component_static/`이 없어 React 화면이 Python fallback으로 내려가는 문제를
방지한다.

## When To Use

- 새 finance worktree에서 처음 app을 시작할 때
- React/Vite frontend 변경을 merge한 뒤 app을 다시 시작할 때
- main-dev, sub-dev, backtest-dev처럼 여러 worktree를 서로 다른 port로 동시에 운영할 때
- 어떤 PID와 log가 특정 worktree/port instance를 소유하는지 확인할 때

Git branch, merge, worktree 생성·삭제 또는 production deployment에는 사용하지 않는다.

## Prerequisites

- worktree path:
  `/Users/taeho/Project/quant-data-pipeline-worktrees/<worktree>`
- worktree-local Python:
  `<worktree>/.venv/bin/python`
- app entry:
  `<worktree>/app/web/streamlit_app.py`
- local commands: `python3`, `node`, `npm`, `lsof`, `ps`, `tail`
- executable:
  `/Users/taeho/.local/bin/qweb`
- shell PATH block in `/Users/taeho/.zshrc`

현재 shell에 PATH를 반영하려면 한 번 실행한다.

```bash
source /Users/taeho/.zshrc
```

## Commands

Start:

```bash
qweb start main-dev 8521
qweb start sub-dev 8502
qweb start backtest-dev 8506
```

Status:

```bash
qweb status main-dev 8521
```

Logs:

```bash
qweb logs main-dev 8521
```

`logs`는 `tail -f`를 사용한다. `Ctrl+C`는 log follow만 종료하며 Streamlit은 계속 실행된다.

Stop:

```bash
qweb stop main-dev 8521
```

Help:

```bash
qweb help
```

## Start Behavior

1. worktree name과 port 형식을 검증한다.
2. port listener가 이미 있는지 확인한다.
3. qweb-owned 동일 instance면 중복 process를 만들지 않고 현재 URL을 반환한다.
4. 다른 process가 port를 사용하면 `PORT_CONFLICT`로 중단하며 종료 signal을 보내지 않는다.
5. `app/web/**/package.json` 중 `scripts.build`가 있는 frontend를 찾는다.
6. 저장 fingerprint가 없거나 source가 바뀌었거나 `build/`·`component_static/`·`dist/`가 없으면 해당 package만
   `npm ci` 또는 `npm install` 후 `npm run build`한다.
7. frontend 하나라도 실패하면 Streamlit을 시작하지 않는다.
8. build가 모두 준비되면 worktree cwd에서 Streamlit을 background로 시작하고 PID/meta/log를 기록한다.

설치 후 첫 start는 fingerprint가 없으므로 기존 build가 있더라도 전체 frontend를 한 번 다시 검증·빌드할
수 있다. 이후 start는 변경되거나 output이 사라진 package만 rebuild한다.

## Expected Result

성공한 start는 아래 형태로 출력한다.

```text
RUNNING: http://localhost:8521 (PID 12345)
```

Status state:

- `RUNNING`: PID, command, cwd, port listener가 모두 qweb metadata와 일치
- `STOPPED`: qweb state와 port listener가 모두 없음
- `STALE_STATE`: qweb state는 있지만 실제 process ownership이 불일치
- `PORT_CONFLICT`: 같은 port를 수동 실행 또는 다른 process가 사용

## Existing Manual Process Adoption

기존에 아래처럼 직접 시작한 서버는 qweb metadata가 없으므로 `PORT_CONFLICT`로 보이는 것이
정상이다.

```bash
.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8521
```

qweb로 전환하려면 기존 서버를 시작한 terminal에서 `Ctrl+C`로 한 번 종료한 뒤 실행한다.

```bash
qweb start main-dev 8521
```

기존 PID를 qweb가 자동 종료하거나 임의로 인수하지 않는다.

## Failure Handling

### PORT_CONFLICT

```bash
lsof -nP -iTCP:8521 -sTCP:LISTEN
```

요청한 worktree에서 사용자가 직접 시작한 서버인지 확인한다. 맞으면 해당 terminal에서 종료한 뒤
`qweb start`를 다시 실행한다. 다른 process면 port를 바꾼다.

### Frontend build failed

출력된 frontend 경로에서 직접 확인한다.

```bash
cd <reported-frontend-directory>
npm ci
npm run build
```

실패를 해결한 뒤 `qweb start`를 다시 실행한다. 실패 상태에서는 Streamlit이 시작되지 않는다.

### Startup not confirmed

```bash
qweb status <worktree> <port>
qweb logs <worktree> <port>
```

qweb는 startup 확인 실패 시 자동 kill하지 않는다. log와 ownership을 확인한 뒤 정확한 qweb-owned
instance일 때만 `qweb stop`을 사용한다.

### STALE_STATE

PID reuse나 cwd/command mismatch 가능성이 있으므로 PID 파일만 보고 직접 `kill`하지 않는다.
`qweb status`, `lsof`, `ps` 결과를 함께 확인한다. 기록 PID가 이미 죽었고 port도 비어 있으면 아래 명령이
signal 없이 stale PID/meta만 정리한다.

```bash
qweb stop <worktree> <port>
```

기록 PID가 살아 있거나 port listener가 있으면 ownership 불일치로 계속 거부한다.

## Generated Local Artifacts

```text
/Users/taeho/.local/state/qweb/
  <worktree>-<port>.pid
  <worktree>-<port>.meta
  <worktree>-<port>.log
  fingerprints/<worktree>/*.sha256
```

이 파일과 frontend `node_modules/`, `build/`, `component_static/`, `dist/`는 local/generated artifact다. Git에 stage하거나
commit하지 않는다. 정상 stop은 PID/meta를 제거하고 log는 보존한다.

## Related Docs

- [Runbook Index](./README.md)
- [Backtest UI Flow](../flows/BACKTEST_UI_FLOW.md)
- [Script Structure Map](../architecture/SCRIPT_STRUCTURE_MAP.md)
- [Local Finance Web Launcher Design](../../tasks/active/local-finance-web-launcher-v1-20260719/DESIGN.md)
