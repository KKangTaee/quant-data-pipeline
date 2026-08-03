# Inflation Policy Functional Recovery Notes

## 2026-08-03 재감사 결론

- actual snapshot의 overall/model/inflation/policy status는 `LIMITED`다.
- actual reverse/equity status는 `NOT_AVAILABLE`이다.
- Core one-month artifact는 내부 baseline보다 우수하지만
  `benchmark_suite_incomplete` 하나로 강제 `LIMITED`다.
- Q4 path, policy path와 reverse는 production pipeline에서 각각 상태가 하드코딩돼 있다.
- actual `sp500_index_earnings`는 0건이며 `joint_macro_paths` artifact도 없다.
- current S&P official workbook parser는 release date 이전 period를 모두 actual로 저장하므로
  historical forward EPS consensus vintage source를 대신할 수 없다.

## 보존 경계

- 사용자 수정 registry와 untracked research/run history/QA artifact는 stage하지 않는다.
- 기존 app server는 사용자 실행으로 간주해 종료하지 않는다.

