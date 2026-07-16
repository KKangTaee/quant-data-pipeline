# Runs

## 2026-07-16 Diagnosis Baseline

- `git status --short --branch`, recent commit log 확인.
- finance INDEX / ROADMAP / PROJECT_MAP / SCRIPT_STRUCTURE_MAP / BACKTEST_UI_FLOW / PORTFOLIO_SELECTION_FLOW 확인.
- 2026-07 Practical Validation validation audit와 Final Review evidence closure task 문서 확인.
- current Practical Validation page / workspace / closure / stage role / React component / boundary test source 확인.
- focused baseline:
  - `.venv/bin/python -m unittest tests.test_backtest_evidence_closure tests.test_backtest_refactor_boundaries tests.test_service_contracts.PracticalValidationServiceContractTests tests.test_service_contracts.PracticalValidationReplayServiceContractTests`
  - result: 66 tests, `OK`.

## 2026-07-16 Design

- B안 Hybrid One-Shell Decision Workspace를 채택했다.
- protected `PRACTICAL_VALIDATION_RESULTS.jsonl`, run history, saved JSONL, generated QA artifact는 수정하거나 stage하지 않았다.

## 2026-07-16 Plan

- `superpowers:writing-plans` 기준으로 1차 truth contract, 2차 read model, 3차 one-shell UI, 4차 QA / docs의 RED -> GREEN -> commit 단위를 작성했다.
- 구현 세션은 새 worktree를 만들지 않고 현재 `codex/backtest-dev`에서 `superpowers:executing-plans`를 사용한다.
- plan self-review에서 exact file, interface, test command, expected failure/pass, Korean commit, protected artifact exclusion을 확인했다.
- self-review에서 provider CTA와 실제 callable handler의 커밋 순서를 맞추고, `validation_result_id`를 read model 최상위 계약으로 고정했다.
- `source_required`, explicit measurement 기반 `measured_caution`, method audit의 actual PASS / remaining REVIEW 분리, 동일 root 중복 방지, React fallback / ResizeObserver / stale intent guard를 계획에 보강했다.
- current saved GRS-shaped row의 Validation Efficacy audit는 walk-forward REVIEW 1개와 OOS / regime PASS 2개를 실제로 보유하므로 generic module 문구만 first-read에 쓰지 않도록 projection 기준을 명시했다.
