# Master Merge Resolution 2026-07-25 Runs

## 2026-07-25

- `git status --short --branch`, `git diff --name-only --diff-filter=U`,
  `git ls-files -u`: 문서 5개, Python 1개, Economic Cycle source/static bundle 충돌 확인.
- `git show :1/:2/:3`, `git diff --cc`: current branch의 Economic Cycle/data 완료 기록과
  incoming master의 Header/Sentiment/Institutional/Futures 완료 기록이 독립적임을 확인.
- 충돌 체크리스트 기준으로 run history, registry 수정, QA 이미지와 `.superpowers/`를
  무관 로컬 상태로 분류했다.
- `.venv`에 누락된 `pytest`를 `uv pip`로 설치하고 Header package는 lockfile 기준
  `npm ci`를 수행했다. 설치 파일은 Git 추적 대상이 아니다.
- Economic Cycle/data focused: `144 passed`.
- Futures Macro/finalization focused: `106 passed`, subtest `15 passed`.
- Institutional/Sentiment focused: `84 passed`, subtest `8 passed`.
- Events/earnings/coverage service contracts: `122 passed`, `783 deselected`.
- Market Research Header: React `11 passed`, TypeScript `--noEmit` pass.
- Economic Cycle Vite production build와 affected Python `py_compile` pass.
- Browser QA:
  - 최초 8501은 `sub-dev` cwd 프로세스임을 `lsof`로 식별했다.
  - main-dev 전용 8511에서 desktop title `34px`, 420px title `28px`,
    header/body overflow 0, 새 recovery summary, freshness bar, 금·달러 공통 배경
    각 1회, console warning/error 0을 확인했다.
  - generated screenshot은 repository root
    `master-merge-resolution-20260725-qa.png`에 두고 commit에서 제외한다.
