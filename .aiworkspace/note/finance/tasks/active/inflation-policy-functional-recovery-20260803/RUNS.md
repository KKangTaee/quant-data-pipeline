# Inflation Policy Functional Recovery Runs

## 2026-08-03 Baseline

- `.venv/bin/python -m pytest <inflation-policy 관련 17개 파일> -q`
  - 결과: `190 passed`, 기존 edgar deprecation warning 3건
- `npm test -- --run` in `economic_cycle_workbench`
  - 결과: React `11 passed`
- actual Browser reverse click
  - 결과: `datetime is not JSON serializable`로 component render crash 재현

