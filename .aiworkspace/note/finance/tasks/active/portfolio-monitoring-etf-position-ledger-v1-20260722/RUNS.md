# Runs

## 2026-07-22 기준선

- Python focused: position events, valuation, read model, component `66 tests`, PASS.
- React: `36 tests`, PASS.
- worktree: linked worktree `/Users/taeho/Project/quant-data-pipeline-worktrees/main-dev`, branch `codex/main-dev`.

## 2026-07-22 TDD와 회귀

- RED: ETF eligibility validation error, ETF valuation error, selected projection `eligible=False`를 확인.
- GREEN: position events + valuation + read model `50 tests`, PASS.
- 최종 Python focused: commands, page, position events, valuation, read model, component `111 tests`, PASS.
- React: `36 tests`, PASS; `tsc --noEmit`, PASS; Vite production build, PASS.

## 2026-07-22 actual Browser QA

- route: `/selected-portfolio-dashboard`, read-only로 확인하고 저장 command는 실행하지 않음.
- QQQ: 최초/현재 4주, 누적 입금 `$2,970.96`, 현재 평가금액 `$2,839.13`, 두 position action 노출.
- SOXX: 최초/현재 6주, 누적 입금 `$3,598.20`, 현재 평가금액 `$3,316.14`, 두 position action 노출.
- browser console warning/error 0건.
- screenshot: repository root `portfolio-monitoring-etf-position-ledger-qa.png` generated artifact, stage 제외.
