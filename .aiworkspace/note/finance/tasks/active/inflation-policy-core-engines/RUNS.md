# Inflation Policy Core Engines Runs

- 2026-08-02: linked worktree와 branch 확인
  - Result: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`, `codex/sub-dev`
- 2026-08-02: data foundation baseline regression
  - Result: 133 passed, third-party `edgar` deprecation warning 3개, `git diff --check` passed
- 2026-08-02: `tests/test_inflation_path.py`
  - RED: 신규 module/function 부재로 4 failed, simulation API 부재로 2 failed
  - GREEN: Q4/Q4, compounded root solve, SEP-versioned 5상태, threshold/simplex,
    component mixture와 empirical-residual requirement 6 passed
- 2026-08-02: `tests/test_policy_path.py`
  - RED: 신규 module 부재로 5 failed, compact target bin contract 불일치로 1 failed
  - GREEN: SEP marginal, vote direction, reaction matrix, optional prior 재정규화,
    component weight cap, net-move/target-bin consistency 5 passed; Core 포함 11 passed
- 2026-08-02: `tests/test_yield_resistance.py`
  - RED: 신규 module 부재로 5 failed, multi-lookback 동일 pivot touch 중복으로 1 failed
  - GREEN: pivot known-at, dynamic clustering/confluence, 상태 전이, 두 driver lens,
    joint inflation confirmation 6 passed; Core/Policy 포함 17 passed
- 2026-08-02: `tests/test_inflation_policy_simulation.py`
  - RED: 신규 module 부재로 5 failed, conditional float exact assertion 1 failed
  - GREEN: two-lens rate path, weighted target probability, reverse conditional distribution,
    sparse support fail-closed, next-PCE likelihood reweight 5 passed; 전체 domain 22 passed
