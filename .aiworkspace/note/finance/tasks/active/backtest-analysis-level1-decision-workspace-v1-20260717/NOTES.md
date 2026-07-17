# Notes

## 2026-07-17 Current Audit

- Level1의 올바른 역할은 단일 전략 또는 weighted Mix candidate source를 만들고
  Level1 data / execution readiness를 확인한 뒤 명시적으로 Level2에 넘기는 것이다.
- 현재 primary 전략 실행, 결과 KPI / chart, Data Trust, factor readiness, policy
  signal, handoff 기능은 존재한다.
- 핵심 문제는 기능 부재보다 혼합된 information architecture와 duplicated state /
  explanation ownership이다.
- `app/web/backtest_result_display.py`와 `app/web/backtest_compare/page.py`는 큰 기존
  surface이므로 한 번에 runtime까지 재작성하지 않고 read model / adapter 경계부터
  도입한다.
- `Risk-On Momentum 5D`는 연구용이 아니라 개발 도중 미완성된 전략이다.
- 실행 성공, saved Mix, Level2 candidate는 서로 다른 persistence contract다.

## Approved Visual Decisions

- 목적 분기형 entry
- 마지막 workspace 복원
- single S1 / Mix M1 four-step shell
- R1 decision-first result
- G1 contextual advanced settings
- C1 purpose-grouped catalog
- P1 saved Mix inside Mix Step 1
- T2 read model + one-shell

시각 companion 산출물은 `.superpowers/brainstorm/57312-1784291161/`에 있으며
generated artifact이므로 commit하지 않는다.
