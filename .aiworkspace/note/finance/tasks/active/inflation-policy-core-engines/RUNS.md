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
- 2026-08-02: `tests/test_inflation_policy_validation.py`
  - RED: validation module 부재로 5 failed
  - GREEN: PIT chronological training cutoff, CRPS/MAE/coverage, Brier/log loss/ECE,
    baseline/calibration gate와 capped inverse-error weight 5 passed
- 2026-08-02: `tests/test_inflation_policy_model.py`
  - RED: hybrid model module 부재로 3 failed
  - GREEN: first-release target, 당시 공개 vintage feature, bridge·ridge·momentum과
    capped rolling weight, cycle dependency 부재 3 passed
- 2026-08-02: `tests/test_inflation_policy_pipeline.py`
  - RED: pipeline 부재, shifted zip 길이, Q4 status 과승격, 동일 개정 batch origin 오인,
    hybrid evidence/horizon, multi-rate driver/자동 zone, CLI dry-run 계약을 차례로 확인
  - GREEN: fail-closed snapshot, component별 status, active/overhead zone, no-write와
    explicit `--persist` 계약 8 passed
- 2026-08-02: focused engine/data suite
  - Initial result: model/pipeline/validation/loader/simulation/resistance/policy/PCE 45 passed
- 2026-08-02: actual 2026-07-29 18:00 UTC historical replay
  - Input: Core PCE latest 2026-05 observation released 2026-06-25; DGS10 latest
    2026-07-27 released before cutoff; 2026-07-30 PCE excluded
  - Monthly artifact: 97 release origins/99 targets, CRPS 0.06052, best comparable
    baseline 0.10757, calibration error 0.17374, publication `LIMITED`
  - Snapshot: overall/Q4/policy/rates `LIMITED`, reverse/recession `NOT_AVAILABLE`
  - DGS10: current 4.65%, active 4.58~4.65% `ATTEMPT`, next overhead 4.67%
- 2026-08-02: actual persistence check
  - `inflation_policy_model_artifact`: `inflation-policy-hybrid-v1`,
    `core_pce_hybrid`, horizon `one_month_core_pce_nowcast`, 97 origins/99 targets,
    publication `LIMITED`, `max_released_at <= as_of_at` 확인
  - `inflation_policy_snapshot`: same cutoff/model, `historical_replay`, publication `LIMITED`
- 2026-08-02: final regression verification
  - Inflation/policy focused suite after review corrections: 68 passed
  - Inflation/policy plus adjacent data and valuation suite: 184 passed
  - `py_compile`: 8 engine/loader modules passed
  - prohibited dependency/static constant search: economic-cycle result reuse 0, hard-coded
    4.7/4.70 source references 0
  - `git diff --check` and finance refinement hygiene: passed; protected user/generated
    artifacts remain unstaged
- 2026-08-02: independent review corrections
  - `FAILED` artifact의 snapshot 승격/저장 차단, explicit PIT artifact requirement,
    cutoff freshness assertion과 component별 latest observation/release 저장
  - artifact 실제 `trained_cutoff_at` provenance와 replay cutoff 검증; core 실패 시
    Treasury read payload만 독립 반환하고 실패 run write는 0건 유지
  - 실제 이력이 충족된 63/252/504 lookback만 인정하고 zone state를 known-at 이후
    재생해 `HOLD/FAILED`를 복원
  - near-target SEP에서도 항상 증가하는 5상태 경계와 3회 이상 policy tail range 보존
  - carry-forward·3개월·6개월 baseline 점수를 모두 저장하고 SEP/공식 benchmark가
    남은 동안 artifact를 `LIMITED`로 유지
