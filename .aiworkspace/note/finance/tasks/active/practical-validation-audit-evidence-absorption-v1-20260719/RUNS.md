# Runs

## 2026-07-19 Baseline

- Worktree: linked worktree, branch `codex/backtest-dev`.
- Focused suite: `91 passed`, 3 existing edgar deprecation warnings.
- Protected dirty state: Practical Validation registry, run history, saved portfolio JSONL, `.superpowers/`, generated QA artifacts.

## 2026-07-19 TDD / Build

- Compact provenance service RED: 3 expected failures (`candidate.provenance`, `replay.provenance`, `record` missing).
- Service GREEN: `31 passed`, 3 existing edgar deprecation warnings.
- UI ownership / raw boundary RED: 3 expected failures.
- Focused GREEN: `96 passed`, 3 existing edgar deprecation warnings.
- React build: passed, 175 modules transformed.

## 2026-07-19 Actual Browser QA

- Before replay: Step 1 candidate summary visible; replay/validation records hidden; bottom raw disclosure absent.
- Actual latest replay: status PASS, requested/actual period and latest common price date visible, limiting symbols visible.
- Step 4 record text contains profile, mode, attempted time, Replay ID, Validation ID.
- 760px: outer/context/decision horizontal overflow all false; candidate/replay provenance grids one column.
- Browser console errors: 0.
- QA artifact: `practical-validation-audit-evidence-absorption-v1-desktop-qa.png` (local generated artifact, not committed).

## 2026-07-19 Final Verification

- Focused suite: `96 passed`, 3 existing edgar deprecation warnings.
- Python compile: decision workspace service, page, and fallback panel passed.
- React production build: passed, 175 modules transformed; `index-BBAKHxPS.css`, `index-Bn0sRqz8.js`.
- Latest Browser QA: Data Trust internal status translated to `확인 완료`; raw audit labels absent.
- 760px: provenance grid one column (`645px`), document overflow false; console errors 0.
