# Runs

## 2026-07-12

- linked worktree `codex/backtest-dev`를 확인했고 새 worktree를 만들지 않았다.
- 구현 전 Practical Validation / Provider Gap / Final Review / BacktestRuntime baseline 178개 테스트가 통과했다.
- 1차 RED 2개에서 shared completion helper 부재와 Final Review recovery 수집의 replay 미초기화를 확인했다.
- 두 수집 경로를 공통 completion helper로 통합한 뒤 focused 3개, py_compile, `git diff --check`를 통과했다.
- 2차 recovery progress / replay save guard RED 2개를 확인하고 4단계 progress read model과 저장 방어를 구현했다.
- Practical Validation / BacktestRuntime focused 115개, py_compile, `git diff --check`를 통과했다.
- 3차 latest-before-eligibility / new stable-key handoff RED 2개를 확인했다.
- source별 최신 validation 선택, blocked-latest fallback 방지, save-and-move 자동 선택·확정을 구현한 뒤 focused 184개, py_compile, `git diff --check`를 통과했다.
- Browser QA에서 legacy/stale 검토서의 `2단계 재검증 필요`, 최종 판단 비활성, REVIEW 근거 렌더링을 확인했다. 760x900 viewport에서 outer document와 React iframe 모두 horizontal overflow가 없었다.
- 실제 provider 수집과 registry append는 실행하지 않았다. in-app Browser에서는 React navigation intent가 Streamlit rerun으로 관측되지 않아 전체 클릭 체인은 contract test로 보완했다.
- 최종 focused service / contract tests 188개, React production build, target py_compile, `git diff --check`가 통과했다.
