# Economic Cycle Manual Refresh Design

Status: Approved
Date: 2026-07-25
Owner: Overview / Market Context

## Context

`Workspace > Overview > Market Context > 경제 사이클`의 `월말 이후 경제사이클 흐름`은
현재 DB에 저장된 마지막 `intramonth_nowcast`를 읽는다. 2026-07-25 현재 표시 기준일은
2026-07-21이지만, 그 row의 `source_collected_at`은 2026-07-16이다. 이는 브라우저 진입
또는 데스크톱 재실행이 수집 job을 자동으로 실행하지 않기 때문이다.

기존 backend에는 17개 FRED series를 증분 수집하고 월말 rollover와 월중 nowcast
materialization을 수행하는 `run_economic_cycle_intramonth_refresh`가 있다. 그러나 현재
경제사이클 UI는 이 job을 호출하는 action을 제공하지 않고, `FRED_API_KEY`도 현재
worktree runtime에 주입되지 않았다.

사용자는 launchd, cron, heartbeat 같은 background scheduler를 이번 범위에 포함하지
않고, 브라우저에서 최신화 필요 여부를 확인한 뒤 버튼을 눌러 직접 수집·계산하고 싶다.

## Goals

- `main-dev`, `sub-dev`, `backtest-dev` 각각의 root `.env`에 동일한 로컬
  `FRED_API_KEY`를 저장한다.
- `.env`는 Git에 포함되지 않도록 shared exclude와 tracked `.gitignore`로 이중
  보호한다.
- Streamlit과 CLI job이 worktree root `.env`를 읽되 이미 주입된 process environment를
  덮어쓰지 않는다.
- 저장된 월중 계산일과 최신 계산 가능 평일을 비교해 최신화 필요 여부를 안내한다.
- stale, missing, read error 상태에서 `최신 데이터로 다시 계산` action을 제공한다.
- 버튼은 기존 증분 수집·월말 rollover·월중 materialization pipeline을 재사용한다.
- 성공 후 DB postcondition을 확인한 경우에만 cache를 비우고 새 결과를 표시한다.
- 실패하면 마지막 정상 월말 및 월중 결과를 그대로 유지한다.

## Non-goals

- macOS launchd, cron, 앱 내 timer, 브라우저 heartbeat를 추가하지 않는다.
- 브라우저 진입만으로 provider 수집을 시작하지 않는다.
- React 또는 Streamlit render 함수에서 FRED를 직접 호출하지 않는다.
- raw run, row count, provider response, stack trace 중심의 운영 진단 패널을 만들지 않는다.
- 기존 월말 history를 덮어쓰거나 월중 row를 월말 ribbon에 섞지 않는다.
- FRED API key 값을 tracked file, task 문서, log, screenshot에 기록하지 않는다.

## Considered Approaches

### 1. Background scheduler

사용자 개입 없이 최신 상태를 만들 수 있지만 데스크톱 종료, launchd 설치·운영,
재시도 정책까지 범위가 커진다. 이번 요청에서 명시적으로 제외한다.

### 2. Browser entry automatic refresh

진입 시 stale 상태를 즉시 해소할 수 있지만 page render가 provider 호출과 DB write를
암묵적으로 일으킨다. 긴 응답과 실패가 화면 진입을 막을 수 있어 제외한다.

### 3. Freshness notice plus explicit manual action

화면 진입은 DB read만 수행하고, 사용자가 stale 안내를 본 뒤 action을 명시적으로
실행한다. 현재 ingestion 경계를 보존하면서 실행 시점이 분명하므로 이 접근을 채택한다.

## Architecture

### A. Local environment loading

작은 runtime helper가 현재 worktree root의 `.env`를
`dotenv.load_dotenv(path, override=False)`로 읽는다. `override=False`를 사용해 shell,
CI, launch environment에서 이미 제공한 `FRED_API_KEY`를 우선한다. `.env`가 없으면
오류 없이 기존 동작을 유지한다.

Streamlit entrypoint와 Overview automation CLI entrypoint가 provider job 실행 전에
helper를 호출한다. 개별 collector나 UI component는 `.env` 파일 위치를 알지 않는다.

세 worktree에는 각각 물리적인 `.env`를 둔다.

- `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev/.env`
- `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/.env`
- `/Users/taeho/Project/quant-data-pipeline-worktrees/backtest-dev/.env`

shared Git directory의 `.git/info/exclude`에는 `.env`를 즉시 등록한다. tracked
`.gitignore`에도 root 및 nested local environment files를 보호하는 규칙을 추가한다.
값 자체는 diff, commit, task log에 남기지 않는다.

### B. Freshness contract

새 pure freshness adapter는 `intramonth.as_of_date`와 최신 계산 가능 평일을 비교한다.
주말에는 직전 금요일을 목표일로 사용한다. 예를 들어 2026-07-25 토요일의 목표일은
2026-07-24다. 공휴일 거래 캘린더를 추정하지 않고 평일 규칙만 사용하며, 이후 실제
provider release가 없더라도 해당 날짜 기준으로 PIT 계산을 재실행할 수 있다.

service read model은 다음 compact field를 선택적으로 제공한다.

```text
data_freshness
  status = READY | REFRESH_AVAILABLE | MISSING | ERROR
  persisted_as_of_date
  target_as_of_date
  refresh_required
  user_message
```

`READY`는 저장된 월중 계산일이 목표일 이상인 상태다. 과거이면
`REFRESH_AVAILABLE`, row가 없으면 `MISSING`, 날짜 해석 또는 read 실패는 `ERROR`다.
월말 결과는 freshness 오류와 무관하게 계속 렌더링한다.

### C. Manual action boundary

UI helper는 component가 반환한 nonce 기반 action event를 한 번만 소비하고,
Overview action wrapper를 호출한다. wrapper가 다음을 수행한다.

1. 현재 날짜로부터 target 평일을 결정한다.
2. 기존 `run_economic_cycle_intramonth_refresh(as_of_date=target)`를 실행한다.
3. DB에서 최신 월중 snapshot을 다시 읽는다.
4. 저장된 `as_of_date >= target`인지 postcondition을 확인한다.

기존 pipeline 순서는 바꾸지 않는다.

```text
17-series incremental FRED collection
  -> closed-month rollover when required
  -> intramonth nowcast materialization
  -> persisted snapshot verification
```

job이 `success` 또는 사용 가능한 `partial_success`를 반환하고 postcondition까지
충족할 때만 성공으로 취급한다. `LIMITED`는 숨기지 않되 계산 가능한 잠정 결과로
유지한다. provider failure, credential absence, materialization failure, postcondition
failure는 새 결과를 성공으로 표시하지 않는다.

### D. UI behavior

경제사이클 React shell의 월중 흐름 가까이에 compact freshness/action bar를 둔다.

- 최신 상태: 저장된 최신 계산 기준일을 보이고 action은 숨기거나 비활성화한다.
- 최신화 필요: 현재 계산일과 목표일을 짧게 설명하고
  `최신 데이터로 다시 계산` 버튼을 표시한다.
- 수집 중: 중복 클릭을 막고 `최신 자료를 수집하고 경제사이클을 다시 계산하는 중`으로
  표시한다.
- 성공: 새 기준일을 확인하는 짧은 one-shot message 후 rerun된 최신 화면을 보인다.
- 실패: 마지막 정상 결과가 유지됐음을 알리고 재시도 가능한 action을 남긴다.

React component는 event payload만 반환한다. Python helper가 job을 실행하므로
`Ingestion -> DB -> Loader -> UI` 경계를 유지한다. React component가 unavailable인
fallback Streamlit 화면에도 같은 manual action을 제공한다.

진단 세부정보는 run history에 남기되 첫 화면에는 사용자에게 필요한 기준일, 최신화
필요 여부, 다음 행동만 보여준다.

## State and Failure Handling

- API key 없음: action 실패, 기존 snapshot 유지, credential 설정 필요 안내
- FRED series 일부 실패: 새 nowcast 성공 처리 금지, last-good 유지
- 신규 release 없음: 증분 fetch 후 target 날짜 기준 materialization 허용
- exact model artifact 없음: 새 row 미기록, last-good 유지
- DB write 성공처럼 보이나 target row 없음: postcondition failure
- 같은 날짜 재실행: 기존 business key UPSERT로 idempotent
- UI rerun 또는 component duplicate event: nonce 소비 기록으로 한 번만 실행
- service read 실패: 월말 payload를 가능한 범위에서 유지하고 refresh action 제공

## Testing

### Local environment

- root `.env` load
- missing `.env` is harmless
- existing process environment has precedence
- `.env` rules are effective in all three worktrees
- secret value is absent from tracked diff and task logs

### Freshness

- weekday returns same date
- Saturday and Sunday return previous Friday
- persisted date before target is `REFRESH_AVAILABLE`
- persisted date equal to or after target is `READY`
- missing and malformed dates produce safe states

### Manual action

- target date is passed to the existing combined refresh
- success requires a persisted target snapshot
- `partial_success` with usable persisted target is accepted
- job failure or failed postcondition preserves cache and last-good result
- duplicate event nonce does not run twice

### UI and actual QA

- current 2026-07-21 row on 2026-07-25 shows target 2026-07-24 and action
- action loading, success, and failure copy
- no raw job/result diagnostic panel
- React typecheck/test/build and tracked component bundle rebuild
- desktop and 420px Browser QA with no horizontal overflow or console error
- QA screenshot is generated but not committed

## Data Integrity Verification

Before actual refresh, record count and stable checksum evidence for existing monthly
`current`/historical rows. After refresh:

- prior monthly history remains unchanged
- only required closed-month canonical row may be appended
- one target-date `intramonth_nowcast` business key exists
- `source_collected_at` advances when collection succeeds
- action run history is recorded once

## Implementation Roadmap

### 1차 — Local secret and runtime boundary

Add `.env` Git protection, populate the three local files without exposing their value, and add
the non-overriding environment loader. Completion means UI and CLI can see the credential while
Git cannot track the files.

### 2차 — Freshness and manual action

Add the pure freshness contract, action wrapper, postcondition, event consumption, and compact
React/fallback controls. Completion means stale state is actionable without provider access during
render.

### 3차 — Actual refresh, QA, and durable documentation

Run focused tests and the real manual flow, verify DB invariants, perform desktop/mobile Browser
QA, and synchronize runbook/project documentation. Completion means the 2026-07-24 target can be
materialized without altering prior monthly history.

## Completion Criteria

- all three worktrees have ignored local `.env` files and no secret appears in Git.
- the 2026-07-25 browser view recognizes 2026-07-24 as the target date.
- stale/missing/error states present a clear manual refresh action.
- page render remains DB-only until the user explicitly clicks.
- a successful click persists and displays a target-date nowcast only after DB verification.
- a failed click retains the last-good 2026-07-21 result.
- no background scheduler or diagnostic dashboard is added.
- focused Python/React tests, build, DB integrity checks, and Browser QA pass.
