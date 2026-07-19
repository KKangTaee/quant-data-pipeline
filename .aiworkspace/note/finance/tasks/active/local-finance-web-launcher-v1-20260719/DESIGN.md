# Local Finance Web Launcher V1 Design

Status: Implemented and verified
Date: 2026-07-19

## 이걸 하는 이유?

현재 Streamlit 실행 명령은 React/Vite frontend를 빌드하지 않는다. `build/`, `component_static/`와 `node_modules/`는
Git에 포함되지 않기 때문에 새 worktree 또는 frontend 변경을 병합한 worktree에서 바로 Streamlit만
실행하면 일부 화면이 Python fallback으로 내려갈 수 있다. 반대로 오래 사용한 worktree는 로컬 build가
남아 있어 같은 실행 명령으로도 정상처럼 보인다.

사용자가 worktree 이름과 port만 바꿔 동일한 방식으로 finance app을 시작·종료할 수 있도록 개인용
launcher를 제공한다. launcher는 빠른 실행보다 재현 가능한 frontend 준비와 안전한 process ownership을
우선한다.

## 목표

- `qweb start <worktree> <port>` 한 번으로 필요한 frontend build와 Streamlit 시작을 수행한다.
- `qweb stop <worktree> <port>`가 해당 launcher가 시작한 정확한 process만 종료한다.
- 여러 worktree와 port를 동시에 운영할 수 있다.
- 새 worktree, merge 이후 frontend 변경, build 삭제를 자동으로 감지한다.
- log와 PID 위치를 고정해 상태 확인과 문제 진단이 가능하다.

## 제외 범위

- Git branch 생성, merge, pull 또는 worktree 생성·삭제
- registry, saved portfolio, run history 변경
- production deployment, launchd 등록, 자동 browser open
- Streamlit 또는 React 화면 코드 변경
- `build/`, `component_static/`, `dist/`, `node_modules/`, runtime log의 Git commit

## 검토한 방식

### A. 개인 실행 파일 + PATH 등록 — 채택

`~/.local/bin/qweb` 하나를 모든 worktree에서 호출한다. `.zshrc`에는 `~/.local/bin` PATH 등록만 둔다.
worktree마다 script를 복제하지 않아 명령이 일관되고, 긴 shell function을 `.zshrc`에 직접 유지하지 않아도
된다.

### B. `.zshrc` 단일 function

설치는 간단하지만 process 검증, build fingerprint, 상태·로그 처리가 길어져 shell 설정이 운영 코드가
된다. 테스트와 유지보수가 어렵기 때문에 채택하지 않는다.

### C. worktree별 repo-local script

버전 관리에는 유리하지만 branch마다 script 버전이 달라질 수 있고 새 worktree마다 호출 경로를 바꿔야
한다. 여러 worktree를 하나의 명령으로 관리하려는 목적과 맞지 않아 채택하지 않는다.

## 사용자 인터페이스

```bash
qweb start main-dev 8521
qweb stop main-dev 8521
qweb status main-dev 8521
qweb logs main-dev 8521
qweb help
```

- worktree name은 `A-Z`, `a-z`, 숫자, `.`, `_`, `-`만 허용한다.
- port는 `1..65535` 정수만 허용한다.
- worktree root는
  `/Users/taeho/Project/quant-data-pipeline-worktrees/<worktree>`로 고정한다.
- `logs`는 현재 log를 follow하며 사용자가 `Ctrl+C`로 빠져나온다.

## 설치 위치와 상태 파일

- executable: `/Users/taeho/.local/bin/qweb`
- shell PATH: `/Users/taeho/.zshrc`의 `export PATH="/Users/taeho/.local/bin:$PATH"`
- state root: `/Users/taeho/.local/state/qweb/`
- instance key: `<worktree>-<port>`
- instance files:
  - `<instance>.pid`
  - `<instance>.log`
  - `<instance>.meta`
- frontend fingerprints:
  - `fingerprints/<worktree>/<package-key>.sha256`

state와 log는 local runtime artifact이며 Git에 포함하지 않는다.

## Start 흐름

1. argument, worktree name, port를 검증한다.
2. worktree directory, `.venv/bin/python`, `app/web/streamlit_app.py`, `npm`, `node`, `lsof` 존재를 확인한다.
3. port listener가 있으면 PID와 cwd를 확인한다.
   - 동일 instance가 이미 실행 중이면 성공 상태로 현재 URL을 출력한다.
   - 다른 process 또는 다른 worktree가 사용 중이면 아무것도 종료하지 않고 실패한다.
4. `app/web/**/package.json`을 `node_modules`, `build`, `dist` 제외 조건으로 찾는다.
5. `scripts.build`가 있는 package만 source fingerprint를 계산한다.
   - package metadata, lockfile, source, Vite/TypeScript config를 포함한다.
   - `node_modules`, `build`, `dist`, cache는 제외한다.
6. 아래 중 하나면 해당 package를 rebuild한다.
   - 저장된 fingerprint 없음
   - fingerprint 변경
   - `build/`, `component_static/`, `dist/`가 모두 없음
7. lockfile이 있으면 `npm ci`, 없으면 `npm install` 후 `npm run build`를 실행한다.
8. 하나라도 실패하면 Streamlit을 시작하지 않고 실패 package를 출력한다.
9. worktree cwd에서 `nohup .venv/bin/python -m streamlit run ...`을 실행한다.
10. PID/meta를 기록하고 제한 시간 동안 port listener를 확인한다.
11. 성공하면 URL, PID, log path를 출력한다. startup 확인 실패 시 process를 억지로 kill하지 않고 log 경로와
    복구 명령을 출력한다.

## Stop 흐름

1. instance PID/meta를 읽는다.
2. PID가 살아 있는지 확인한다.
3. process command가 Streamlit entry를 포함하고 cwd가 요청한 worktree와 일치하는지 확인한다.
4. port listener PID가 instance PID와 일치하는지 확인한다.
5. 모든 조건이 맞을 때만 `TERM`을 보낸다.
6. 제한 시간 동안 종료를 확인한다. 종료되지 않으면 자동 `KILL`하지 않고 사용자에게 PID와 수동 확인
   명령을 안내한다.
7. 정상 종료 후 PID/meta를 제거하고 log는 보존한다.

## Status와 Logs

`status`는 state file, process 생존, cwd, port listener를 함께 확인해 아래 중 하나를 출력한다.

- `RUNNING`: 네 조건이 모두 일치
- `STOPPED`: process 없음
- `STALE_STATE`: state는 있지만 PID/process가 불일치
- `PORT_CONFLICT`: port가 다른 process에 의해 사용됨

`logs`는 instance log가 없으면 실패하고, 있으면 `tail -f`로 연결한다.

## 오류 처리 원칙

- invalid worktree/port는 filesystem이나 process를 건드리기 전에 거부한다.
- build 실패는 app startup보다 먼저 종료한다.
- port conflict에서 기존 process를 자동 종료하지 않는다.
- stale PID는 재사용 가능성이 있으므로 command/cwd/port 일치 없이 `kill`하지 않는다.
- `.zshrc` PATH line은 marker를 사용해 중복 추가하지 않는다.
- 기존 사용자 `.zshrc` 내용은 보존한다.

## 검증 설계

구현은 shell fixture 기반 TDD로 진행한다.

1. RED: help/argument validation, invalid worktree, invalid port가 아직 없어 실패함을 확인한다.
2. GREEN: 최소 parser와 validation을 구현한다.
3. RED/GREEN: fake worktree와 fake `npm`으로 initial build, unchanged skip, changed rebuild, build failure
   startup 차단을 검증한다.
4. RED/GREEN: fake Streamlit/listener state로 start idempotency와 port conflict 거부를 검증한다.
5. RED/GREEN: PID/cwd/port 불일치에서 stop이 kill하지 않고, 정확히 일치할 때 TERM만 보내는지 검증한다.
6. `zsh -n`, test suite, 실제 `qweb help/status`를 실행한다.
7. 실제 app process를 임의 종료하지 않는다. 사용자 승인 없이 현재 8502/8505/8506/8521 process에
   start/stop smoke를 수행하지 않는다.

## 문서화

- Local App 반복 절차는 `docs/runbooks/`에 목적, 설치, 명령, 기대 결과, 실패 처리 순서로 기록한다.
- `docs/runbooks/README.md`에서 launcher runbook을 찾을 수 있게 한다.
- 개인 executable은 repo helper registry의 source-of-truth가 아니므로
  `AUTOMATION_SCRIPTS.md`에는 repo-local helper로 등록하지 않는다.

## 완료 조건

- 새 shell에서 `qweb help`가 동작한다.
- `qweb start <worktree> <port>`가 누락·변경된 전체 web frontend만 build한다.
- frontend build 실패 시 Streamlit이 시작되지 않는다.
- 동일 instance start는 중복 process를 만들지 않는다.
- 다른 process가 쓰는 port를 종료하거나 덮어쓰지 않는다.
- `qweb stop`은 command/cwd/port ownership이 일치할 때만 TERM을 보낸다.
- status/log 경로가 사용자에게 명확히 출력된다.
- `.zshrc` 기존 내용과 사용자 worktree 변경을 보존한다.
